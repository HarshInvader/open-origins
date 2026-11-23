"""K1 (prereg v5): how much of Moody et al.'s summed LUCA size does the root prior create?

Moody's O_R_Optimization.py reweights only the root branch prior by w = exp(O_R):
    PP(w) = w r / (w r + 1),   loglik(w) = log b + log(w r + 1) - log(N - 1 + w)
with r = flat-prior root odds of the family and N = 1,399 branches. So r is recoverable from
their per-run PPs and category weights, and the sum can be recomputed under any root weight.

Usage: python -I k1_prior.py <COG_OR_reconciliation dir> <real_features_moody.tsv> <out.json>
"""
import sys, json, math, statistics

D, FEAT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
N = 2 * 700 - 1
SAT = 1 - 1e-12
RUNS = [1, 2, 3, 4, 5]

cat_of = {}
for line in open(f"{D}/Map2.tsv"):
    f = line.rstrip("\n").split("\t")
    if len(f) >= 2:
        cat_of[f[0]] = f[1].strip()

def pp_of(w, r):
    if math.isinf(r):
        return 1.0
    x = w * r
    return x / (x + 1.0)

def invert(pp, ws):
    """Return (r, saturated). ws = list of 1 or 2 category weights; PP is the mean over them."""
    if pp >= SAT:
        pp = SAT
        sat = True
    else:
        sat = False
    if pp <= 0:
        return 0.0, False
    if len(ws) == 1:
        return (pp / (1 - pp)) / ws[0], sat
    lo, hi = -800.0, 800.0  # bisection on ln r
    for _ in range(200):
        mid = (lo + hi) / 2
        r = math.exp(mid)
        v = sum(pp_of(w, r) for w in ws) / len(ws)
        if v < pp:
            lo = mid
        else:
            hi = mid
    return math.exp((lo + hi) / 2), sat

runs = {}
for i in RUNS:
    w = {}
    for line in open(f"{D}/KEGG{i}_OR.csv").read().splitlines()[1:]:
        c, v = line.split(",")
        w[c] = float(v)
    fam = {}
    for line in open(f"{D}/kegg{i}_cons.txt"):
        k, p = line.split()
        fam[k] = float(p)
    runs[i] = (w, fam)

common = sorted(set.intersection(*(set(runs[i][1]) for i in RUNS)))
strat = {}
for line in open(FEAT).read().splitlines()[1:]:
    f = line.split("\t")
    occA, occB = float(f[3]), float(f[4])
    if occA == 0 or occB == 0:
        strat[f[0]] = "single_domain"
    elif min(occA, occB) <= 0.01:
        strat[f[0]] = "both_le1pct"
    else:
        strat[f[0]] = "B2"

# recover r per run
R = {i: {} for i in RUNS}
cats = {}
nsat = {i: 0 for i in RUNS}
skipped = set()
for k in common:
    c = cat_of.get(k, "")
    if len(c) not in (1, 2):
        skipped.add(k)
        continue
    cats[k] = list(c)
for i in RUNS:
    w, fam = runs[i]
    for k in common:
        if k in skipped:
            continue
        ws = [w[c] for c in cats[k] if c in w]
        if len(ws) != len(cats[k]):
            skipped.add(k)
            continue
        r, sat = invert(fam[k], ws)
        R[i][k] = (r, sat)
        nsat[i] += sat
fams = [k for k in common if k not in skipped]

def fit_w(rs, lo=-5.0, hi=40.0):
    """ML root weight over O_R in [lo, hi]: maximise sum log(w r + 1) - F log(N - 1 + w)."""
    F = len(rs)
    def ll(o):
        w = math.exp(o)
        return sum(math.log1p(w * r) for r in rs) - F * math.log(N - 1 + w)
    best = max((ll(lo + j * 0.05), lo + j * 0.05) for j in range(int((hi - lo) / 0.05) + 1))
    o = best[1]
    step = 0.05
    while step > 1e-4:
        cand = [(ll(x), x) for x in (o - step, o, o + step) if lo <= x <= hi]
        o = max(cand)[1]
        step /= 2
    return o

def summarise(pp_by_run, label):
    med = {k: statistics.median(pp_by_run[i][k] for i in RUNS) for k in fams}
    out = {"label": label, "sum": sum(med.values()),
           "n_pp_ge_0.75": sum(v >= 0.75 for v in med.values()),
           "n_pp_ge_0.5": sum(v >= 0.5 for v in med.values())}
    for s in ("single_domain", "both_le1pct", "B2"):
        out["sum_" + s] = sum(v for k, v in med.items() if strat.get(k) == s)
    out["single_domain_share"] = out["sum_single_domain"] / out["sum"] if out["sum"] else float("nan")
    return out


import json as _j
out={}
for i in RUNS:
    rs=[R[i][k][0] for k in fams]
    F=len(rs)
    def ll(o):
        w=math.exp(o); return sum(math.log1p(w*r) for r in rs)-F*math.log(N-1+w)
    o_hat=fit_w(rs); L=ll(o_hat)
    def edge(sign):
        a=o_hat; step=0.5
        while ll(a+sign*step)>=L-1.92: a+=sign*step
        lo,hi=sorted((a,a+sign*step))
        for _ in range(60):
            m=(lo+hi)/2
            if (ll(m)>=L-1.92)==(sign>0): lo=m
            else: hi=m
        return (lo+hi)/2
    lo,hi=edge(-1),edge(1)
    S=lambda o: sum(pp_of(math.exp(o),r) for r in rs)
    out[i]={"O_hat":o_hat,"S_hat":S(o_hat),"O_lo":lo,"O_hi":hi,"S_lo":S(lo),"S_hi":S(hi),"F":F,"dLL_flat":L-ll(0.0)}
    print(i,out[i])
_j.dump(out,open(OUT,"w"),indent=1)
