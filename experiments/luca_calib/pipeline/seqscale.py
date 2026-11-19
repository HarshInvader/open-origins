"""Sequence-scale pilot (prereg v2 change 2, v3 change 3): find Zombi's tree scaling so that the
median mean pairwise p-distance of sampled alignments is 0.61 +/- 0.05.

Usage:
    python seqscale.py <outdir> --config fit_config.json [--set key=value ...]
                       [--n-aln 300] [--n-seqs 30] [--rtt-start 2.0] [--max-evals 8]

One genome simulation (T, Ti, Gm with gene trees) at the config's rates and seed. Families with
>= 4 sampled genes are candidates; --n-aln of them are drawn (seed 0). For each trial value of
sequence.target_root_to_tip (Zombi SCALING = rtt / tree_height), Zombi Su (WAG, 157 sites, the
v1 lognormal lineage and family multipliers, sigma 0.5) runs on just those families: their complete
and pruned gene trees are copied into a fresh experiment folder with a copy of T, so Su simulates only
them. Statistic, as real_stats.py: per alignment, up to --n-seqs sampled sequences drawn at random
(seed 0), mean p-distance over pairs with >= 30 gap-free sites; then the median over alignments.
The search brackets in log(rtt) (x2 steps) and bisects until |median - 0.61| <= --stop-tol (0.01),
or --max-evals Su runs; the evaluation closest to 0.61 is chosen.

Writes <outdir>/seqscale.json (all evaluations, chosen rtt, the v2 3b p-distance check) and
<outdir>/pilot_config.json (the input config with sequence.target_root_to_tip set).
Checkpointed: each evaluation is cached in <outdir>/evals/<rtt>.json.
"""
import argparse
import copy
import json
import math
import os
import random
import shutil
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, read_fasta, write_json
import simulate as S

TARGET, CHECK_TOL = 0.61, 0.05


def mean_pdistance(seqs, n_seqs, rnd):
    s = rnd.sample(seqs, min(n_seqs, len(seqs)))
    d = []
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            m = [(a, b) for a, b in zip(s[i], s[j]) if a != "-" and b != "-"]
            if len(m) >= 30:
                d.append(sum(a != b for a, b in m) / len(m))
    return float(np.mean(d)) if d else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outdir")
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--n-aln", type=int, default=300)
    ap.add_argument("--n-seqs", type=int, default=30)
    ap.add_argument("--rtt-start", type=float, default=2.0)
    ap.add_argument("--stop-tol", type=float, default=0.01)
    ap.add_argument("--max-evals", type=int, default=8)
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    cfg = S.load_config(a.config, a.set)
    for d in ["params", "logs", "evals"]:
        os.makedirs(os.path.join(out, d), exist_ok=True)
    logs = os.path.join(out, "logs")
    T0 = time.time()
    secs = {}

    # ---- one genome simulation with gene trees (checkpointed)
    gdone = os.path.join(out, "genome.done")
    if not os.path.exists(gdone):
        shutil.rmtree(os.path.join(out, "zombi"), ignore_errors=True)
        t = time.time()
        S.step_species_tree(cfg, out, logs)
        S.step_genomes(cfg, out, logs, gene_trees=True)
        shutil.rmtree(os.path.join(out, "zombi_T_raw"), ignore_errors=True)
        secs["genomes"] = round(time.time() - t, 1)
        open(gdone, "w").write(json.dumps(secs) + "\n")
    else:
        secs.update(json.loads(open(gdone).read()))
    zdir = os.path.join(out, "zombi")
    ext = S.read_tree(os.path.join(zdir, "T", "ExtantTree.nwk"))
    mrca, doms, dom_roots, sampled_by_dom = S.sample_species(cfg, ext)
    sampled = set(sampled_by_dom[0] + sampled_by_dom[1])
    gdir = os.path.join(zdir, "G", "Genomes")
    counts = {}
    for s in sampled:
        for fam, c in S.read_genome(os.path.join(gdir, s + "_GENOME.tsv")).items():
            counts[fam] = counts.get(fam, 0) + c
    cand = sorted((f for f, c in counts.items() if c >= 4), key=int)
    chosen = sorted(random.Random(0).sample(cand, min(a.n_aln, len(cand))), key=int)
    log("%d families with >= 4 sampled genes; %d used" % (len(cand), len(chosen)))
    gtdir = os.path.join(zdir, "G", "Gene_trees")

    def evaluate(rtt):
        cache = os.path.join(out, "evals", "%.6g.json" % rtt)
        if os.path.exists(cache):
            return json.load(open(cache))
        wd = os.path.join(out, "su_%.6g" % rtt)
        shutil.rmtree(wd, ignore_errors=True)
        for d in ["params", "logs", "zombi/G/Gene_trees"]:
            os.makedirs(os.path.join(wd, d))
        shutil.copytree(os.path.join(zdir, "T"), os.path.join(wd, "zombi", "T"))
        for f in chosen:
            for kind in ("completetree", "prunedtree"):
                shutil.copy(os.path.join(gtdir, "%s_%s.nwk" % (f, kind)), os.path.join(wd, "zombi/G/Gene_trees"))
        c = copy.deepcopy(cfg)
        c["sequence"]["target_root_to_tip"] = rtt
        t = time.time()
        info = S.step_sequences(c, wd, os.path.join(wd, "logs"), mrca, sorted(sampled))
        su_s = time.time() - t
        rnd = random.Random(0)
        pds = []
        for f in chosen:
            pf = os.path.join(wd, "zombi", "S", f + "_pruned.fasta")
            seqs = [sq for name, sq in read_fasta(pf) if name.rsplit("_", 1)[0] in sampled]
            if len(seqs) < 4:
                continue
            v = mean_pdistance(seqs, a.n_seqs, rnd)
            if v is not None:
                pds.append(v)
        res = {"rtt": rtt, "scaling": info["scaling"], "median_pdistance": float(np.median(pds)),
               "quantiles": [float(x) for x in np.quantile(pds, [0.1, 0.25, 0.5, 0.75, 0.9])],
               "n_aln": len(pds), "mean_mrca_to_tip_subs": info["mean_mrca_to_tip_subs"],
               "su_seconds": round(su_s, 1)}
        shutil.rmtree(wd)
        write_json(cache, res)
        log("rtt %.4g: median p-distance %.4f over %d alignments (Su %.0fs)" % (rtt, res["median_pdistance"], len(pds), su_s))
        return res

    evals = []
    lo = hi = None            # lo: p below target, hi: p above target
    rtt = a.rtt_start
    while len(evals) < a.max_evals:
        e = evaluate(rtt)
        evals.append(e)
        p = e["median_pdistance"]
        if abs(p - TARGET) <= a.stop_tol:
            break
        if p < TARGET:
            lo = rtt
        else:
            hi = rtt
        if lo is None:
            rtt = hi / 2
        elif hi is None:
            rtt = lo * 2
        else:
            rtt = math.sqrt(lo * hi)
    best = min(evals, key=lambda e: abs(e["median_pdistance"] - TARGET))
    pcfg = copy.deepcopy(cfg)
    pcfg["sequence"]["target_root_to_tip"] = best["rtt"]
    res = {"rtt_star": best["rtt"], "scaling_star": best["scaling"], "median_pdistance": best["median_pdistance"],
           "fit_check_v2_3b": {"median_pdistance": {"value": best["median_pdistance"], "target": TARGET,
                                                    "pass": abs(best["median_pdistance"] - TARGET) <= CHECK_TOL}},
           "n_candidate_families": len(cand), "evaluations": evals, "settings": vars(a),
           "seconds": dict(secs, total=round(time.time() - T0, 1))}
    write_json(os.path.join(out, "seqscale.json"), res)
    write_json(os.path.join(out, "pilot_config.json"), pcfg)
    log("rtt* %.4g (SCALING %.4g): median p-distance %.4f, check %s"
        % (best["rtt"], best["scaling"], best["median_pdistance"], res["fit_check_v2_3b"]["median_pdistance"]["pass"]))


if __name__ == "__main__":
    main()
