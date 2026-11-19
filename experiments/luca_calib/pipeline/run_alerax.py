"""Run AleRax on one simulation and extract root presence probabilities.

Usage:
    python run_alerax.py <simdir> --trees inferred|true --origination OPTIMIZE|ROOT|UNIFORM|LCA
                         [--parametrization PER-FAMILY] [--samples 100] [--seed 1] [--extra "..."]

AleRax call:
    alerax -f families.txt -s sample/species_tree.nwk -p <run>/out --rec-model UndatedDTL
           --model-parametrization <P> --origination <O> --gene-tree-samples <N> --seed <S>
           --species-tree-search SKIP --min-covered-species 1
--species-tree-search SKIP is required: AleRax 1.4.0 defaults to HYBRID, which would search
(and change) the species tree that the prereg says is given.

NOTE: AleRax 1.4.0 refuses "--origination OPTIMIZE" with PER-FAMILY (or GLOBAL)
parametrization ("--origination OPTIMIZE cannot be used with --model-parametrization GLOBAL or
--model-parametrization PER-FAMILY"). OPTIMIZE needs a parametrization with per-species
origination (ORIGINATION-PER-SPECIES or PER-SPECIES). This script reports that error instead of
silently choosing one; pass --parametrization explicitly.

Root presence (PP), the extraction used:
    For each sample i in 0..N-1, read <out>/reconciliations/all/<fam>_speciesEventCounts_<i>.txt
    (CSV, header "species_label, speciations, duplications, losses, transfers, presence,
    origination, copies, singletons, transfers_to"). Take the row whose species_label is the
    species-tree root (absent row = 0). In GeneRaxCore Scenario::savePerSpeciesEventsCounts,
    "copies" counts the gene nodes mapped to that species with event S, SL or leaf, i.e. the gene
    copies present at the species node itself (the root speciation = the MRCA, the same moment as
    Zombi's genome of the MRCA). PP = (# samples with copies >= 1) / N.
    "presence" is set to 1 exactly when copies is incremented, so the mean of the presence column
    in reconciliations/summaries/<fam>_meanSpeciesEventCounts.txt must equal PP; this is checked.
Families with fewer than --min-genes (default 3) sampled genes are not reconciled and get PP = 0
(reconciled = 0): AleRax 1.4.0 aborts ("There was a problem with filling the nodes array") on any
2-leaf gene tree, and it exits with status 0 when it aborts, so this script checks its output.
--min-covered-species 1 is passed because AleRax's default (4) silently drops families covering
fewer than 4 species, which the prereg does not do.
Output: <run>/root_pp.tsv with columns family, pp, n_root_samples, mean_root_copies, reconciled.
"""
import argparse
import re
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ALERAX, log, run, read_tsv, update_timings, write_json
from ete3 import Tree


def read_counts(path, label):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        header = [h.strip() for h in f.readline().split(",")]
        for line in f:
            h = [x.strip() for x in line.split(",")]
            if h[0] == label:
                return dict(zip(header[1:], map(float, h[1:])))
    return {}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--trees", choices=["inferred", "true"], required=True)
    ap.add_argument("--origination", choices=["OPTIMIZE", "ROOT", "UNIFORM", "LCA"], required=True)
    ap.add_argument("--parametrization", default="PER-FAMILY")
    ap.add_argument("--samples", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--rec-model", default="UndatedDTL")
    ap.add_argument("--min-genes", type=int, default=3,
                    help="families with fewer sampled genes are not reconciled (AleRax 1.4.0 aborts on 2-leaf trees)")
    ap.add_argument("--min-covered-species", type=int, default=1,
                    help="passed to AleRax; its default (4) would silently drop small families")
    ap.add_argument("--extra", default="", help="extra AleRax arguments, space separated")
    ap.add_argument("--tag", default="", help="suffix for the run directory")
    ap.add_argument("--max-fams", type=int, default=0, help="smoke only: first N reconcilable families")
    ap.add_argument("--name", default="", help="run directory name (overrides the default)")
    ap.add_argument("--np", type=int, default=1, help="MPI ranks (mpiexec -np); 1 = plain call")
    a = ap.parse_args()

    sim = os.path.abspath(a.simdir)
    name = a.name or "alerax_%s_%s_%s%s" % (a.trees, a.parametrization, a.origination, ("_" + a.tag) if a.tag else "")
    rdir = os.path.join(sim, name)
    if os.path.isdir(rdir):
        shutil.rmtree(rdir)
    os.makedirs(rdir)

    sp_path = os.path.join(sim, "sample", "species_tree.nwk")
    root = Tree(open(sp_path).readline().strip(), format=1).get_tree_root().name
    truth = read_tsv(os.path.join(sim, "sample", "truth.tsv"))
    present = [r["family"] for r in truth if int(r["n_genes"]) > 0]

    fams, unrec = [], []
    with open(os.path.join(rdir, "families.txt"), "w") as f:
        f.write("[FAMILIES]\n")
        for fam in present:
            if a.trees == "true":
                tp = os.path.join(sim, "sample", "true_trees", fam + ".nwk")
            else:
                tp = os.path.join(sim, "inferred", "trees", fam + ".trees")
            ngenes = sum(1 for _ in open(os.path.join(sim, "sample", "mappings", fam + ".map")))
            if ngenes < a.min_genes or not os.path.exists(tp):
                unrec.append(fam)
                continue
            if a.max_fams and len(fams) >= a.max_fams:
                unrec.append(fam)
                continue
            fams.append(fam)
            f.write("- f%s\ngene_tree = %s\nmapping = %s\n" % (fam, tp, os.path.join(sim, "sample", "mappings", fam + ".map")))

    out = os.path.join(rdir, "out")
    mpi = [os.path.join(os.path.dirname(ALERAX), "mpiexec"), "-np", str(a.np)] if a.np > 1 else []
    cmd = mpi + [ALERAX, "-f", os.path.join(rdir, "families.txt"), "-s", sp_path, "-p", out,
           "--rec-model", a.rec_model, "--model-parametrization", a.parametrization,
           "--origination", a.origination, "--gene-tree-samples", str(a.samples), "--seed", str(a.seed),
           "--species-tree-search", "SKIP", "--min-covered-species", str(a.min_covered_species)] + a.extra.split()
    log("AleRax: %d families (%d not reconciled), root %s" % (len(fams), len(unrec), root))
    dt = run(cmd, logfile=os.path.join(rdir, "alerax.stdout"))
    txt = open(os.path.join(rdir, "alerax.stdout")).read()
    if "Error" in txt or "terminating" in txt or not os.path.isdir(os.path.join(out, "reconciliations", "all")):
        # AleRax 1.4.0 exits 0 even when it aborts, so check its output
        sys.exit("AleRax failed (exit status was 0):\n" + "\n".join(l for l in txt.splitlines() if not re.match(r"^\[[^]]+:[0-9]+\]", l))[-1500:])
    update_timings(sim, name, dt)
    log("AleRax done in %.1fs" % dt)

    rows, failed, mism = [], [], []
    for fam in fams:
        n_root, copies, ok = 0, 0.0, True
        for i in range(a.samples):
            c = read_counts(os.path.join(out, "reconciliations", "all", "f%s_speciesEventCounts_%d.txt" % (fam, i)), root)
            if c is None:
                ok = False
                break
            k = c.get("copies", 0.0)
            copies += k
            n_root += k >= 1
        if not ok:
            failed.append(fam)
            continue
        pp = n_root / float(a.samples)
        m = read_counts(os.path.join(out, "reconciliations", "summaries", "f%s_meanSpeciesEventCounts.txt" % fam), root)
        if m is not None and abs(m.get("presence", 0.0) - pp) > 1e-6:
            mism.append((fam, pp, m.get("presence", 0.0)))
        rows.append((fam, pp, n_root, copies / a.samples, 1))
    rows += [(fam, 0.0, 0, 0.0, 0) for fam in unrec]
    rows.sort(key=lambda r: int(r[0]))
    with open(os.path.join(rdir, "root_pp.tsv"), "w") as f:
        f.write("family\tpp\tn_root_samples\tmean_root_copies\treconciled\n")
        for r in rows:
            f.write("%s\t%.4f\t%d\t%.4f\t%d\n" % r)
    meta = {"cmd": cmd, "root": root, "n_reconciled": len(fams) - len(failed), "n_unreconciled_1gene": len(unrec),
            "n_failed": len(failed), "failed": failed, "summary_mismatches": mism, "seconds": round(dt, 2)}
    write_json(os.path.join(rdir, "run_meta.json"), meta)
    if failed:
        log("WARNING: %d families have no reconciliation output: %s" % (len(failed), failed[:10]))
    if mism:
        log("WARNING: per-sample PP disagrees with summary presence for %d families" % len(mism))
    log("wrote %s" % os.path.join(rdir, "root_pp.tsv"))


if __name__ == "__main__":
    main()
