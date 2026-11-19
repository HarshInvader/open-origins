"""Infer gene trees for the sampled families of one simulation.

Usage:
    python infer_trees.py <simdir> [--workers 2] [--min-iqtree 4] [--model LG+G4] [--bootstraps 1000]

  >= min-iqtree genes : IQ-TREE  -m <model> -B <bootstraps> --wbtl -T 1 ; keeps <fam>.ufboot (all UFBoot trees)
  2 .. min-iqtree-1   : the single unrooted topology, written as one tree
  1 gene              : skipped, listed in inferred/skipped_single_gene.txt

Writes <simdir>/inferred/trees/<fam>.trees (the file AleRax reads), iqtree/<fam>.* and inferred/status.tsv.
Every tree is checked to contain exactly the family's sampled genes.
"""
import argparse
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from ete3 import Tree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import IQTREE, wait_for_memory, log, read_fasta, update_timings


def small_topology(names):
    names = sorted(names)
    if len(names) == 2:
        return "(%s,%s);" % tuple(names)
    if len(names) == 3:
        return "(%s,%s,%s);" % tuple(names)
    raise ValueError(names)


def check_trees(path, names):
    want = set(names)
    n = 0
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        got = set(Tree(line, format=1).get_leaf_names())
        if got != want:
            return n, "leaf set mismatch in tree %d (%d vs %d leaves)" % (n + 1, len(got), len(want))
        n += 1
    return n, ""


def run_iqtree(fam, fasta, workdir, args):
    wait_for_memory()
    prefix = os.path.join(workdir, fam)
    cmd = [IQTREE, "-s", fasta, "-m", args.model, "-B", str(args.bootstraps), "--wbtl", "-T", "1",
           "--prefix", prefix, "-seed", str(args.seed), "-quiet", "-redo"] + args.iqtree_extra.split()
    t0 = time.time()
    import subprocess
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    uf = prefix + ".ufboot"
    if p.returncode != 0 or not os.path.exists(uf):
        return fam, None, dt, "iqtree failed rc=%d %s" % (p.returncode, (p.stderr or p.stdout)[-300:].replace("\n", " "))
    return fam, uf, dt, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--min-iqtree", type=int, default=4)
    ap.add_argument("--model", default="LG+G4")
    ap.add_argument("--bootstraps", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-genes", type=int, default=0,
                    help="SMOKE TESTS ONLY: skip IQ-TREE for families above this size (status 'skipped_max_genes'); 0 = no cap")
    ap.add_argument("--iqtree-extra", default="", help="extra IQ-TREE arguments, space separated")
    a = ap.parse_args()

    sim = os.path.abspath(a.simdir)
    fdir = os.path.join(sim, "sample", "fasta")
    out = os.path.join(sim, "inferred")
    tdir, idir = os.path.join(out, "trees"), os.path.join(out, "iqtree")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(tdir)
    os.makedirs(idir)

    T0 = time.time()
    fams = sorted((f[:-6] for f in os.listdir(fdir) if f.endswith(".fasta")), key=int)
    names = {f: [n for n, _ in read_fasta(os.path.join(fdir, f + ".fasta"))] for f in fams}
    status, singles, jobs = {}, [], []
    for f in fams:
        k = len(names[f])
        if k == 1:
            singles.append(f)
            status[f] = ("skipped_1_gene", 1, 0, 0.0, "")
        elif k < a.min_iqtree:
            p = os.path.join(tdir, f + ".trees")
            with open(p, "w") as fh:
                fh.write(small_topology(names[f]) + "\n")
            status[f] = ("single_topology", k, 1, 0.0, "")
        elif a.max_genes and k > a.max_genes:
            status[f] = ("skipped_max_genes", k, 0, 0.0, "smoke-test cap")
        else:
            jobs.append(f)

    capped = [f for f in fams if status.get(f, ("",))[0] == "skipped_max_genes"]
    log("%d families: %d IQ-TREE, %d small, %d single-gene, %d over --max-genes"
        % (len(fams), len(jobs), len(fams) - len(jobs) - len(singles) - len(capped), len(singles), len(capped)))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_iqtree, f, os.path.join(fdir, f + ".fasta"), idir, a) for f in jobs]
        for fu in as_completed(futs):
            f, uf, dt, err = fu.result()
            if uf is None:
                status[f] = ("failed", len(names[f]), 0, dt, err)
                continue
            n, err = check_trees(uf, names[f])
            if err:
                status[f] = ("failed", len(names[f]), n, dt, err)
                continue
            shutil.copy(uf, os.path.join(tdir, f + ".trees"))
            status[f] = ("iqtree_ufboot", len(names[f]), n, dt, "")

    with open(os.path.join(out, "status.tsv"), "w") as fh:
        fh.write("family\tstatus\tn_genes\tn_trees\tseconds\tnote\n")
        for f in fams:
            fh.write("%s\t%s\t%d\t%d\t%.2f\t%s\n" % ((f,) + status[f]))
    with open(os.path.join(out, "skipped_single_gene.txt"), "w") as fh:
        fh.write("\n".join(singles) + ("\n" if singles else ""))
    failed = [f for f in fams if status[f][0] == "failed"]
    iq = [status[f][3] for f in jobs if status[f][0] == "iqtree_ufboot"]
    dt = time.time() - T0
    update_timings(sim, "infer_trees_wall", dt)
    update_timings(sim, "iqtree_cpu_sum", sum(iq))
    log("done in %.1fs; IQ-TREE ok %d (sum %.1fs, max %.1fs), failed %d %s"
        % (dt, len(iq), sum(iq), max(iq) if iq else 0, len(failed), failed[:10]))


if __name__ == "__main__":
    main()
