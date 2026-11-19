"""Stage F: fit loss L and transfer/loss to the real gene-family statistics (prereg v2 change 1, as
amended by v3 change 3). Genome-only Zombi runs (T, Ti, Gm without gene trees); no sequences, no
inference.

Usage:
    python fit.py <outdir> --config configs/v3_base.json [--workers 4]
                  [--L 0.5,1,2,4] [--TL 0.1,0.2,0.4,0.6] [--seed-base 100] [--set key=value ...]

Grid point i (L-major order, i = 0..15) uses seed seed_base + i for both the species tree and Gm.
Duplication = 0.2 * L, transfer = TL * L (additive transfers, replacement 0), family rates lognormal
with the config's sigma (0.5), root genome and sampling from the config (600 families, 40 per domain).

Origination at each point is found by bisection on log(origination) so that
    ratio = median over sampled genomes of (families in genome) / (families present across sampled genomes)
is within target +/- tol (0.106 +/- 0.02). The bracket starts at --o-start and expands by x4.
Statistics at the accepted origination (families present in >= 1 sampled genome):
    occupancy = share of the sampled genomes holding the family (equal domain sizes, so pooled as in
    real_stats.py); its 10-bin histogram on [0, 1] as shares; share present in both domains;
    median occupancy; median genome size (families).
Distance = sum over bins (sim share - real share)^2 + (both-domain share - 0.455)^2, real shares from
real_stats.json. The fitted point (L*, T*) is the smallest distance among points whose bisection met
the tolerance. fit.json also carries the v2 3b fit-check values for the genome statistics (the
p-distance check is made by seqscale.py) and fit_config.json is the config at (L*, T*).

Every point is checkpointed in <outdir>/points/<i>/point.json and skipped when present.
"""
import argparse
import copy
import json
import math
import os
import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EXP, log, write_json
import simulate as S

REAL_STATS = os.path.join(EXP, "real_stats.json")
BOTH_TARGET = 0.455          # prereg v2
OCC_TARGET = 0.03            # v2 3b
RATIO_TARGET = 994 / 9371    # 0.106, v2 change 1


def genome_stats(zdir, sampled_by_dom):
    gdir = os.path.join(zdir, "G", "Genomes")
    A, B = sampled_by_dom
    gen = {s: set(S.read_genome(os.path.join(gdir, s + "_GENOME.tsv"))) for s in A + B}
    fams = sorted(set().union(*gen.values()), key=int)
    n = len(A) + len(B)
    occA = np.array([sum(f in gen[s] for s in A) / len(A) for f in fams])
    occB = np.array([sum(f in gen[s] for s in B) / len(B) for f in fams])
    occ = (occA * len(A) + occB * len(B)) / n
    sizes = [len(gen[s]) for s in A + B]
    hist = np.histogram(occ, bins=10, range=(0, 1))[0]
    return {"n_families_present": len(fams),
            "median_genome_families": float(np.median(sizes)),
            "ratio": float(np.median(sizes) / len(fams)) if fams else float("nan"),
            "occupancy_hist": hist.tolist(),
            "occupancy_share": (hist / max(1, hist.sum())).tolist(),
            "median_occupancy": float(np.median(occ)) if fams else float("nan"),
            "frac_both_domains": float(np.mean((occA > 0) & (occB > 0))) if fams else float("nan")}


def run_gm(cfg, pdir, k, sampled_by_dom):
    """One Gm run at cfg's origination in pdir/gm_<k>/ (a fresh copy of T); returns stats."""
    wd = os.path.join(pdir, "gm_%02d" % k)
    if os.path.isdir(wd):
        shutil.rmtree(wd)
    for d in ["params", "logs", "zombi"]:
        os.makedirs(os.path.join(wd, d))
    shutil.copytree(os.path.join(pdir, "zombi", "T"), os.path.join(wd, "zombi", "T"))
    t = time.time()
    S.step_genomes(cfg, wd, os.path.join(wd, "logs"), gene_trees=False)
    secs = time.time() - t
    st = genome_stats(os.path.join(wd, "zombi"), sampled_by_dom)
    st["origination"] = cfg["genome"]["origination"]
    st["gm_seconds"] = round(secs, 1)
    shutil.rmtree(os.path.join(wd, "zombi"))       # Gm output can be large; keep params and logs
    return st


def fit_point(i, L, TL, base, outdir, seed, real_share, target, tol, o_start, max_evals):
    pdir = os.path.join(outdir, "points", "%02d" % i)
    done = os.path.join(pdir, "point.json")
    if os.path.exists(done):
        return json.load(open(done))
    if os.path.isdir(pdir):
        shutil.rmtree(pdir)
    for d in ["params", "logs"]:
        os.makedirs(os.path.join(pdir, d))
    cfg = copy.deepcopy(base)
    cfg["seed"] = seed
    g = cfg["genome"]
    g["loss"], g["duplication"], g["transfer"] = L, 0.2 * L, TL * L
    g["replacement_transfer"] = 0.0
    T0 = time.time()
    tree = S.step_species_tree(cfg, pdir, os.path.join(pdir, "logs"))
    t_tree = time.time() - T0
    ext = S.read_tree(os.path.join(pdir, "zombi", "T", "ExtantTree.nwk"))
    mrca, doms, dom_roots, sampled_by_dom = S.sample_species(cfg, ext)

    evals = []

    def f(o):
        c = copy.deepcopy(cfg)
        c["genome"]["origination"] = o
        st = run_gm(c, pdir, len(evals), sampled_by_dom)
        evals.append(st)
        return st["ratio"]

    def ok(r):
        return abs(r - target) <= tol

    # ratio falls as origination rises. Bracket in log space, then bisect (geometric midpoint).
    accepted = None
    lo, hi = None, None                      # lo: ratio above target, hi: ratio below target
    o = o_start
    r = f(o)
    if ok(r):
        accepted = len(evals) - 1
    elif r > target:
        lo = o
        while hi is None and len(evals) < max_evals:
            o *= 4
            r = f(o)
            if ok(r):
                accepted = len(evals) - 1
                break
            if r > target:
                lo = o
            else:
                hi = o
    else:
        hi = o
        while lo is None and len(evals) < max_evals:
            o /= 4
            r = f(o)
            if ok(r):
                accepted = len(evals) - 1
                break
            if r < target:
                hi = o
            else:
                lo = o
        if accepted is None and lo is None and len(evals) < max_evals:
            r = f(0.0)                       # no origination at all
            if ok(r):
                accepted = len(evals) - 1
            elif r < target:
                lo = None                    # cannot reach the target: too few root families shared
            else:
                lo = 0.0
    while accepted is None and lo is not None and hi is not None and len(evals) < max_evals:
        o = math.sqrt(lo * hi) if lo > 0 else hi / 4
        r = f(o)
        if ok(r):
            accepted = len(evals) - 1
        elif r > target:
            lo = o
        else:
            hi = o
    best = accepted if accepted is not None else int(np.argmin([abs(e["ratio"] - target) for e in evals]))
    st = evals[best]
    sim_share = np.array(st["occupancy_share"])
    dist = float(np.sum((sim_share - real_share) ** 2) + (st["frac_both_domains"] - BOTH_TARGET) ** 2)
    res = {"i": i, "L": L, "TL": TL, "seed": seed, "duplication": 0.2 * L, "transfer": TL * L,
           "bisection_ok": accepted is not None, "origination": st["origination"], "stats": st,
           "distance": dist, "evaluations": evals, "species_tree": tree,
           "sampling": {"mrca": mrca, "domain_sizes": [len(d) for d in doms]},
           "seconds": {"tree": round(t_tree, 1), "total": round(time.time() - T0, 1)}}
    shutil.rmtree(os.path.join(pdir, "zombi_T_raw"), ignore_errors=True)
    write_json(done + ".tmp", res)
    os.replace(done + ".tmp", done)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outdir")
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--L", default="0.5,1,2,4")
    ap.add_argument("--TL", default="0.1,0.2,0.4,0.6")
    ap.add_argument("--seed-base", type=int, default=100)
    ap.add_argument("--target", type=float, default=RATIO_TARGET)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--o-start", type=float, default=100.0, help="first origination tried")
    ap.add_argument("--max-evals", type=int, default=12, help="Gm runs per point at most")
    a = ap.parse_args()
    out = os.path.abspath(a.outdir)
    os.makedirs(os.path.join(out, "points"), exist_ok=True)
    base = S.load_config(a.config, a.set)
    real = json.load(open(REAL_STATS))
    real_hist = np.array(real["occupancy_hist"], dtype=float)
    real_share = real_hist / real_hist.sum()
    grid = [(L, TL) for L in map(float, a.L.split(",")) for TL in map(float, a.TL.split(","))]
    log("stage F: %d points, %d workers -> %s" % (len(grid), a.workers, out))
    T0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fit_point, i, L, TL, base, out, a.seed_base + i, real_share, a.target, a.tol,
                          a.o_start, a.max_evals): i for i, (L, TL) in enumerate(grid)}
        for fu in as_completed(futs):
            r = fu.result()
            results.append(r)
            log("point %d L=%g TL=%g: origination %.4g ratio %.3f (%s) both %.3f dist %.4f, %d Gm runs, %.0fs"
                % (r["i"], r["L"], r["TL"], r["origination"], r["stats"]["ratio"],
                   "ok" if r["bisection_ok"] else "NOT within tol", r["stats"]["frac_both_domains"],
                   r["distance"], len(r["evaluations"]), r["seconds"]["total"]))
    results.sort(key=lambda r: r["i"])
    pool = [r for r in results if r["bisection_ok"]] or results
    best = min(pool, key=lambda r: r["distance"])
    st = best["stats"]
    check = {
        "median_occupancy": {"value": st["median_occupancy"], "target": OCC_TARGET,
                             "pass": OCC_TARGET / 1.5 <= st["median_occupancy"] <= OCC_TARGET * 1.5},
        "frac_both_domains": {"value": st["frac_both_domains"], "target": BOTH_TARGET,
                              "pass": abs(st["frac_both_domains"] - BOTH_TARGET) <= 0.07},
        "median_pdistance": {"value": None, "target": 0.61, "pass": None,
                             "note": "made by seqscale.py (seqscale.json)"},
    }
    fit_cfg = copy.deepcopy(base)
    g = fit_cfg["genome"]
    g["loss"], g["duplication"], g["transfer"] = best["L"], best["duplication"], best["transfer"]
    g["origination"] = best["origination"]
    g["replacement_transfer"] = 0.0
    fit = {"L_star": best["L"], "TL_star": best["TL"], "T_star": best["transfer"],
           "origination_star": best["origination"], "best_point": best["i"],
           "selected_from": "points meeting the ratio tolerance" if pool is not results else "all points (none met tolerance)",
           "real": {"occupancy_share": real_share.tolist(), "frac_both_domains": BOTH_TARGET,
                    "ratio_target": a.target, "ratio_tol": a.tol},
           "fit_check_v2_3b": check,
           "points": [{k: r[k] for k in ("i", "L", "TL", "seed", "duplication", "transfer", "bisection_ok",
                                          "origination", "distance", "stats", "seconds")} for r in results],
           "config": base, "settings": vars(a), "seconds": round(time.time() - T0, 1)}
    write_json(os.path.join(out, "fit.json"), fit)
    write_json(os.path.join(out, "fit_config.json"), fit_cfg)
    log("fit: L*=%g T/L*=%g (T*=%g) origination %.4g distance %.4f; occupancy check %s, both-domain check %s"
        % (best["L"], best["TL"], best["transfer"], best["origination"], best["distance"],
           check["median_occupancy"]["pass"], check["frac_both_domains"]["pass"]))


if __name__ == "__main__":
    main()
