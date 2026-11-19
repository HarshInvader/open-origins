"""QT45 epistasis -> candidate non-WC contacts and fitter triple mutants.

Pre-registered in docs/prereg/qt45_epistasis.md (sha256 in docs/prereg/HASHES.txt).
Data: Zenodo 10.5281/zenodo.13891380 (MIT), processed CSVs only, in ./raw/.
Run: .venv/bin/python -I experiments/qt45_epistasis/epistasis.py
"""
import json
import os
import re
from itertools import combinations

import numpy as np
from scipy.stats import false_discovery_control

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
SEED = 20261119

# WT variable region, positions 2..45 (DNA alphabet, T == U); from the authors' notebook.
WT_SEQ = "GCAGGGCAGCGCAGTCGGACATTGATAACGGAATCGAGCCCGCC"
WT = {i + 2: c for i, c in enumerate(WT_SEQ)}
POSITIONS = sorted(WT)

PUBLISHED = {(6, 41), (7, 40), (8, 39), (10, 36), (11, 35), (16, 34), (18, 30), (17, 31)}
WCSET = {("A", "T"), ("T", "A"), ("G", "C"), ("C", "G"), ("G", "T"), ("T", "G")}

MUT = re.compile(r"^([ACGT])(\d+)([ACGT])$")


def read_tsv(name):
    out = []
    with open(os.path.join(RAW, name)) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            try:
                out.append((parts[0], float(parts[1])))
            except ValueError:
                continue
    return out


def parse_mut(tok):
    m = MUT.match(tok)
    if not m:
        return None
    wt, pos, mt = m.group(1), int(m.group(2)), m.group(3)
    if WT.get(pos) != wt:
        return None
    return pos, mt


def load():
    singles = {}
    for tok, f in read_tsv("combined_single_mutant_fitness.csv"):
        p = parse_mut(tok)
        if p:
            singles[p] = f
    doubles = []
    for tok, f in read_tsv("double_mutant_fitness_all.csv"):
        bits = tok.split()
        if len(bits) != 2:
            continue
        a, b = parse_mut(bits[0]), parse_mut(bits[1])
        if not a or not b or a[0] == b[0]:
            continue
        if a not in singles or b not in singles:
            continue
        if a[0] > b[0]:
            a, b = b, a
        doubles.append((a, b, f))
    return singles, doubles


def isotonic(x, y):
    """PAVA isotonic regression; returns (xs, ys) for interpolation."""
    o = np.argsort(x, kind="mergesort")
    xs, ys = np.asarray(x)[o].astype(float), np.asarray(y)[o].astype(float)
    vals = list(ys)
    wts = [1.0] * len(ys)
    lvl = [[i] for i in range(len(ys))]
    i = 0
    while i < len(vals) - 1:
        if vals[i] <= vals[i + 1] + 1e-12:
            i += 1
            continue
        w = wts[i] + wts[i + 1]
        v = (vals[i] * wts[i] + vals[i + 1] * wts[i + 1]) / w
        vals[i:i + 2] = [v]
        wts[i:i + 2] = [w]
        lvl[i:i + 2] = [lvl[i] + lvl[i + 1]]
        if i > 0:
            i -= 1
    fit = np.empty(len(ys))
    for v, idxs in zip(vals, lvl):
        fit[idxs] = v
    return xs, fit


def make_g(x, y):
    xs, fit = isotonic(x, y)
    # collapse duplicate x
    ux, inv = np.unique(xs, return_inverse=True)
    uy = np.zeros(len(ux))
    cnt = np.zeros(len(ux))
    np.add.at(uy, inv, fit)
    np.add.at(cnt, inv, 1)
    uy /= cnt
    return lambda q: np.interp(np.asarray(q, float), ux, uy)


def informative(f1, f2, x, y):
    return (f1 > -8) and (f2 > -8) and (x > -10) and (y > -13.5)


def build(singles, doubles):
    rows = []
    for a, b, y in doubles:
        f1, f2 = singles[a], singles[b]
        x = f1 + f2
        rows.append(dict(pos=(a[0], b[0]), mut=(a, b), f1=f1, f2=f2, x=x, y=y,
                         info=informative(f1, f2, x, y)))
    return rows


def pair_stats(rows, resid_key="e", min_n=3):
    byp = {}
    for r, e in rows:
        if not r["info"]:
            continue
        byp.setdefault(r["pos"], []).append((e, r))
    out = {}
    for p, lst in byp.items():
        es = np.array([e for e, _ in lst])
        if len(es) < min_n:
            continue
        sd = es.std(ddof=1) if len(es) > 1 else np.nan
        t = es.mean() / (sd / np.sqrt(len(es))) if sd and sd > 0 else np.nan
        out[p] = dict(n=len(es), mean=float(es.mean()), sd=float(sd), t=float(t),
                      members=[r for _, r in lst])
    return out


def wc_capable(pair, members):
    i, j = pair
    if (WT[i], WT[j]) in WCSET:
        return True
    for r in members:
        (pi, mi), (pj, mj) = r["mut"]
        a = mi if pi == i else mj
        b = mj if pj == j else mi
        if (a, b) in WCSET:
            return True
    # also singles-level: a double could restore a pair with one mutated side
    for r in members:
        (pi, mi), (pj, mj) = r["mut"]
        if (mi, mj) in WCSET or (mj, mi) in WCSET:
            return True
    return False


def sep_bin(p):
    d = abs(p[1] - p[0])
    for k, hi in enumerate([3, 7, 15, 30]):
        if d <= hi:
            return k
    return 4


def matched_null(stats, rng, nperm=2000):
    """Permute residuals within (separation bin, single-fitness quartile) cells."""
    keys = list(stats)
    meanf = {p: np.mean([ (r["f1"] + r["f2"]) / 2 for r in stats[p]["members"]]) for p in keys}
    qs = np.quantile(list(meanf.values()), [0.25, 0.5, 0.75])
    cell = {p: (sep_bin(p), int(np.searchsorted(qs, meanf[p]))) for p in keys}
    pools = {}
    for p in keys:
        pools.setdefault(cell[p], []).extend(stats[p]["resid"])
    pvals = {}
    for p in keys:
        pool = np.array(pools[cell[p]])
        n = stats[p]["n"]
        draws = rng.choice(pool, size=(nperm, n), replace=True).mean(axis=1)
        pvals[p] = float((1 + np.sum(draws >= stats[p]["mean"])) / (nperm + 1))
    return pvals, cell


def rank_pipeline(rows, rng, nperm=2000, fit_rows=None):
    fit = fit_rows if fit_rows is not None else rows
    g = make_g([r["x"] for r in fit], [r["y"] for r in fit])
    res = [(r, r["y"] - float(g([r["x"]])[0])) for r in rows]
    stats = pair_stats(res)
    for p, s in stats.items():
        s["resid"] = [e for e, r in [(rr["y"] - float(g([rr["x"]])[0]), rr) for rr in s["members"]]]
    # recompute resid cleanly
    for p, s in stats.items():
        s["resid"] = [float(rr["y"] - g([rr["x"]])[0]) for rr in s["members"]]
    pv, _ = matched_null(stats, rng, nperm)
    ps = list(stats)
    q = false_discovery_control([pv[p] for p in ps], method="bh") if ps else []
    for p, qq in zip(ps, q):
        stats[p]["p"] = pv[p]
        stats[p]["q"] = float(qq)
    return g, stats


# ---------------------------------------------------------------- planted check
def plant_once(singles, doubles, rng, g_real, resid_sd, n_plant=10):
    pairs = [p for p in combinations(POSITIONS, 2) if p[1] - p[0] > 3]
    planted = [tuple(pairs[i]) for i in rng.choice(len(pairs), n_plant, replace=False)]
    E = {p: rng.uniform(2, 8) for p in planted}
    sim = []
    for a, b, _ in doubles:
        x = singles[a] + singles[b]
        p = (a[0], b[0])
        bonus = 0.0
        if p in planted:
            # "restoring" doubles: those whose mutant identities form a WC/wobble pair
            if (a[1], b[1]) in WCSET:
                bonus = E[p]
        y = float(g_real([x])[0]) + bonus + rng.normal(0, resid_sd)
        y = max(y, -14.0)
        sim.append((a, b, y))
    rows = build(singles, sim)
    _, stats = rank_pipeline(rows, rng, nperm=400)
    order = sorted(stats, key=lambda p: -stats[p]["mean"])[:20]
    hits = sum(1 for p in planted if p in order)
    return hits, planted


def main():
    rng = np.random.default_rng(SEED)
    singles, doubles = load()
    rows = build(singles, doubles)
    n_info = sum(r["info"] for r in rows)
    out = dict(n_singles=len(singles), n_doubles=len(rows), n_informative=n_info,
               seed=SEED, kill=[])
    if n_info < 200:
        out["kill"].append("fewer than 200 informative doubles")

    g_full, stats = rank_pipeline(rows, rng, nperm=2000)
    resid_all = np.array([r["y"] - float(g_full([r["x"]])[0]) for r in rows if r["info"]])
    resid_sd = float(resid_all.std(ddof=1))
    out["residual_sd_informative"] = resid_sd

    # ---- planted check
    hits = []
    for _ in range(10):
        h, _p = plant_once(singles, doubles, rng, g_full, resid_sd)
        hits.append(h)
    out["plant"] = dict(hits_per_rep=hits, reps_passing=int(sum(h >= 5 for h in hits)),
                        chance_expectation=round(10 * 20 / 990, 3),
                        passes=bool(sum(h >= 5 for h in hits) >= 8))
    if not out["plant"]["passes"]:
        out["kill"].append("planted check below pre-set power")

    # ---- held-out R2
    idx = np.arange(len(rows))
    info_mask = np.array([r["info"] for r in rows])
    test = np.zeros(len(rows), bool)
    for m in (info_mask, ~info_mask):
        sub = idx[m]
        pick = rng.choice(sub, size=int(round(0.2 * len(sub))), replace=False)
        test[pick] = True
    train_rows = [r for r, t in zip(rows, test) if not t]
    test_rows = [r for r, t in zip(rows, test) if t]
    g_tr = make_g([r["x"] for r in train_rows], [r["y"] for r in train_rows])
    _, stats_tr = rank_pipeline(train_rows, rng, nperm=800)
    pair_term = {p: s["mean"] for p, s in stats_tr.items() if s["q"] < 0.05}

    def r2(pred, obs):
        obs = np.asarray(obs)
        pred = np.asarray(pred)
        return float(1 - np.sum((obs - pred) ** 2) / np.sum((obs - obs.mean()) ** 2))

    def evaluate(subset):
        y = [r["y"] for r in subset]
        m1 = [r["x"] for r in subset]
        m2 = list(g_tr([r["x"] for r in subset]))
        m3 = [a + pair_term.get(r["pos"], 0.0) for a, r in zip(m2, subset)]
        return dict(n=len(subset), additive=r2(m1, y), nonlinear=r2(m2, y), pairs=r2(m3, y))

    out["heldout"] = dict(all=evaluate(test_rows),
                          informative=evaluate([r for r in test_rows if r["info"]]),
                          n_pair_terms=len(pair_term))
    if out["heldout"]["all"]["nonlinear"] <= out["heldout"]["all"]["additive"]:
        out["kill"].append("held-out R2 no better than additive")

    # ---- ranked pairs
    ranked = sorted(stats, key=lambda p: -stats[p]["mean"])
    def label(p):
        if p in PUBLISHED:
            return "published"
        return "WC-capable" if wc_capable(p, stats[p]["members"]) else "non-WC"
    tbl = [dict(pair=f"{WT[p[0]]}{p[0]}-{WT[p[1]]}{p[1]}", i=p[0], j=p[1], n=stats[p]["n"],
                mean_epistasis=round(stats[p]["mean"], 3), t=round(stats[p]["t"], 2),
                p=stats[p]["p"], q=round(stats[p]["q"], 4), label=label(p))
           for p in ranked]
    out["all_pairs_top40"] = tbl[:40]
    pub_means = [stats[p]["mean"] for p in PUBLISHED if p in stats]
    out["published_pairs"] = {f"{WT[p[0]]}{p[0]}-{WT[p[1]]}{p[1]}":
                              dict(rank=ranked.index(p) + 1, mean=round(stats[p]["mean"], 3),
                                   n=stats[p]["n"], q=round(stats[p]["q"], 4))
                              for p in PUBLISHED if p in stats}
    out["published_median_mean_epistasis"] = float(np.median(pub_means)) if pub_means else None
    out["sealed_top10_nonWC"] = [t for t in tbl if t["label"] == "non-WC"][:10]

    # ---- triples predicted to beat WT
    pair_full = {p: s["mean"] for p, s in stats.items() if s["q"] < 0.05}
    measured = {}
    for r in rows:
        if r["info"]:
            measured[(r["mut"][0], r["mut"][1])] = r["y"]
    best_single = {}
    for (pos, mt), f in singles.items():
        if f > best_single.get(pos, (-99, None))[0]:
            best_single[pos] = (f, mt)
    cand_pos = [p for p, (f, _) in best_single.items() if f > -1.0]
    triples = []
    for trio in combinations(sorted(cand_pos), 3):
        muts = [(p, best_single[p][1]) for p in trio]
        ds = [tuple(sorted([muts[a], muts[b]])) for a, b in [(0, 1), (0, 2), (1, 2)]]
        if not all(d in measured for d in ds):
            continue
        x = sum(singles[m] for m in muts)
        pred = float(g_full([x])[0]) + sum(pair_full.get((d[0][0], d[1][0]), 0.0) for d in ds)
        triples.append((pred, muts, [measured[d] for d in ds]))
    triples.sort(reverse=True)
    out["n_triples_considered"] = len(triples)
    out["sealed_triples"] = [
        dict(triple=" ".join(f"{WT[p]}{p}{m}" for p, m in muts),
             predicted_fitness=round(pred, 3),
             constituent_double_fitness=[round(v, 3) for v in dv])
        for pred, muts, dv in triples[:10]]

    # ---- robustness: complete10 processing
    try:
        s2 = {}
        for tok, f in read_tsv("complete10_single_mutant_fitness_all.csv"):
            p = parse_mut(tok)
            if p:
                s2[p] = f
        d2 = []
        for tok, f in read_tsv("complete10_double_mutant_fitness_all.csv"):
            bits = tok.split()
            if len(bits) != 2:
                continue
            a, b = parse_mut(bits[0]), parse_mut(bits[1])
            if not a or not b or a[0] == b[0] or a not in s2 or b not in s2:
                continue
            if a[0] > b[0]:
                a, b = b, a
            d2.append((a, b, f))
        rows2 = build(s2, d2)
        _, stats2 = rank_pipeline(rows2, np.random.default_rng(SEED + 1), nperm=800)
        rank2 = sorted(stats2, key=lambda p: -stats2[p]["mean"])
        top10_main = [(t["i"], t["j"]) for t in tbl[:10]]
        out["complete10"] = dict(n_doubles=len(rows2),
                                 top10_overlap=len(set(top10_main) & set(rank2[:10])),
                                 nonWC_top10_overlap=len(
                                     set((t["i"], t["j"]) for t in out["sealed_top10_nonWC"]) &
                                     set(rank2[:20])))
    except Exception as exc:  # pragma: no cover
        out["complete10"] = dict(error=str(exc))

    with open(os.path.join(HERE, "results.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("all_pairs_top40",)}, indent=1)[:4000])


if __name__ == "__main__":
    main()
