"""Pre-registration v7 (docs/prereg/luca_realdata_v7.md): real-data checks on the LUCA root weight.

Items 1 (dose response), 2 (Bayes-factor count), 3 (ribosome/tRNA vs photosystem controls),
4 (LOESS propagation to proteins, validated against Moody's ~2,657), 6 (families dropped before scoring).

Usage: python -I r_analyses.py <luca_calib dir> <out dir>
"""
import sys, os, json, math, glob, statistics, collections
import numpy as np

L, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
D = f"{L}/raw/moody/COG_OR_reconciliation"
SUPP = f"{L}/raw/moody/Supp_data"
N = 2 * 700 - 1
SAT = 1 - 1e-12
RUNS = [1, 2, 3, 4, 5]
res = {}

# ---------- recover flat-prior root odds r, exactly as k1_prior.py ----------
cat_of = {}
for line in open(f"{D}/Map2.tsv"):
    f = line.rstrip("\n").split("\t")
    if len(f) >= 2:
        cat_of[f[0]] = f[1].strip()

def pp_of(w, r):
    x = w * r
    return x / (x + 1.0)

def invert(pp, ws):
    pp = min(pp, SAT)
    if pp <= 0:
        return 0.0
    if len(ws) == 1:
        return (pp / (1 - pp)) / ws[0]
    lo, hi = -800.0, 800.0
    for _ in range(200):
        mid = (lo + hi) / 2
        v = sum(pp_of(w, math.exp(mid)) for w in ws) / len(ws)
        lo, hi = (mid, hi) if v < pp else (lo, mid)
    return math.exp((lo + hi) / 2)

runs = {}
for i in RUNS:
    w = {c: float(v) for c, v in (l.split(",") for l in open(f"{D}/KEGG{i}_OR.csv").read().splitlines()[1:])}
    fam = {k: float(p) for k, p in (l.split() for l in open(f"{D}/kegg{i}_cons.txt"))}
    runs[i] = (w, fam)
common = sorted(set.intersection(*(set(runs[i][1]) for i in RUNS)))
fams = [k for k in common if len(cat_of.get(k, "")) in (1, 2)
        and all(c in runs[i][0] for i in RUNS for c in cat_of[k])]
R = np.array([[invert(runs[i][1][k], [runs[i][0][c] for c in cat_of[k]]) for k in fams] for i in RUNS])
F = len(fams)
res["n_scored"] = F

def fit_logw(r):
    def ll(o):
        return np.sum(np.log1p(math.exp(o) * r)) - len(r) * math.log(N - 1 + math.exp(o))
    grid = np.arange(-5, 40, 0.01)
    return float(grid[np.argmax([ll(o) for o in grid])])

logw_hat = [fit_logw(R[j]) for j in range(5)]
w_hat = math.exp(statistics.median(logw_hat))
res["logw_hat_per_run"] = logw_hat
res["w_hat_median"] = w_hat

def med_pp(w):
    return np.median(R * w / (R * w + 1), axis=0)  # per family, median over runs

# ---------- 1. dose response ----------
grid = np.logspace(0, 5, 101)
dose = []
for w in grid:
    per_run = R * w / (R * w + 1)
    dose.append({"w": float(w), "sum_pp_median_run": float(np.median(per_run.sum(axis=1))),
                 "sum_pp_min_run": float(per_run.sum(axis=1).min()),
                 "sum_pp_max_run": float(per_run.sum(axis=1).max()),
                 "n_pp_ge_0.5_median_run": float(np.median((per_run >= 0.5).sum(axis=1))),
                 "prior_root_share": float(w / (w + N - 1))})
res["dose"] = dose
for wq in (1, 10, 100, w_hat, 1000, 1e4):
    pr = R * wq / (R * wq + 1)
    res.setdefault("dose_points", []).append({"w": wq, "sum_pp": float(np.median(pr.sum(axis=1))),
                                              "n_ge_0.5": float(np.median((pr >= 0.5).sum(axis=1)))})

# ---------- 2. Bayes factors ----------
BF_real = np.median(R, axis=0) * (N - 1)

def leaves(nwk):
    s = open(nwk).read()
    return s.count(",") + 1

sims = []
for tp in glob.glob(f"{L}/results/**/sample/truth.tsv", recursive=True):
    base = os.path.dirname(os.path.dirname(tp))
    rp = f"{base}/ale_true/root_pp.tsv"
    sp = f"{base}/sample/species_tree.nwk"
    if not (os.path.exists(rp) and os.path.exists(sp)):
        continue
    truth = {}
    for l in open(tp).read().splitlines()[1:]:
        f = l.split("\t"); truth[f[0]] = int(f[3])
    Ns = 2 * leaves(sp) - 1
    rows = []
    for l in open(rp).read().splitlines()[1:]:
        f = l.split("\t")
        if f[5] != "ok" or f[0] not in truth:
            continue
        p = min(float(f[2]), SAT)
        rows.append((p / (1 - p) * (Ns - 1), truth[f[0]]))
    if rows:
        sims.append({"name": os.path.relpath(base, L), "N": Ns, "rows": rows})

def best_threshold(rows):
    bf = np.array([x for x, _ in rows]); y = np.array([t for _, t in rows])
    cands = np.unique(np.log10(np.clip(bf, 1e-300, None)))
    best = (-1, None, None, None)
    P, Nn = (y == 1).sum(), (y == 0).sum()
    for c in cands:
        pred = np.log10(np.clip(bf, 1e-300, None)) >= c
        sens = (pred & (y == 1)).sum() / P if P else float("nan")
        spec = (~pred & (y == 0)).sum() / Nn if Nn else float("nan")
        ba = (sens + spec) / 2
        if ba > best[0]:
            best = (ba, float(c), float(sens), float(spec))
    return best

pooled = [r for s in sims for r in s["rows"]]
ba, t_star, sens, spec = best_threshold(pooled)
per_sim = []
for s in sims:
    b = best_threshold(s["rows"])
    nl = sum(t for _, t in s["rows"])
    per_sim.append({"name": s["name"], "N": s["N"], "n_fam": len(s["rows"]), "n_luca": nl,
                    "log10_bf_star": b[1], "bal_acc": b[0]})
ts = [p["log10_bf_star"] for p in per_sim if p["log10_bf_star"] is not None and 0 < p["n_luca"] < p["n_fam"]]
lbr = np.log10(np.clip(BF_real, 1e-300, None))
res["bf"] = {"n_sims": len(sims), "pooled_log10_bf_star": t_star, "pooled_bal_acc": ba,
             "pooled_sens": sens, "pooled_spec": spec,
             "real_count_at_star": int((lbr >= t_star).sum()),
             "p10_log10_star": float(np.percentile(ts, 10)), "p90_log10_star": float(np.percentile(ts, 90)),
             "real_count_at_p10": int((lbr >= np.percentile(ts, 10)).sum()),
             "real_count_at_p90": int((lbr >= np.percentile(ts, 90)).sum()),
             "per_sim": per_sim,
             "real_log10_bf_quantiles": {q: float(np.percentile(lbr, q)) for q in (10, 25, 50, 75, 90, 99)}}
np.save(f"{OUT}/real_log10_bf.npy", lbr)
json.dump({s["name"]: [[math.log10(max(x, 1e-300)), t] for x, t in s["rows"]] for s in sims},
          open(f"{OUT}/sim_log10_bf.json", "w"))

# ---------- 3. controls ----------
def kos(fn):
    return {l.split("\t")[1].strip().replace("ko:", "") for l in open(f"{L}/raw/kegg_lists/{fn}") if "\t" in l}
feat = {}
for l in open(f"{L}/real_features_moody.tsv").read().splitlines()[1:]:
    f = l.split("\t"); feat[f[0]] = (float(f[3]), float(f[4]))
idx = {k: j for j, k in enumerate(fams)}
pos = sorted(k for k in (kos("link_ko_map03010.txt") | kos("link_ko_map00970.txt"))
             if k in idx and feat.get(k, (0, 0))[0] >= 0.5 and feat[k][1] >= 0.5)
neg = sorted(k for k in (kos("link_ko_M00161.txt") | kos("link_ko_M00163.txt")) if k in idx)
ctrl = {"n_pos": len(pos), "n_neg": len(neg), "neg_families": neg}
cg = np.logspace(-3, 8, 1101)
window = []
curve = []
for w in cg:
    m = med_pp(w)
    mp, mn = float(np.mean([m[idx[k]] for k in pos])), float(np.mean([m[idx[k]] for k in neg])) if neg else float("nan")
    curve.append((float(w), mp, mn))
    if mp >= 0.9 and mn <= 0.1:
        window.append(float(w))
ctrl["curve"] = curve[::10]
m_hat = med_pp(w_hat)
ctrl["mean_pp_pos_at_what"] = float(np.mean([m_hat[idx[k]] for k in pos]))
ctrl["mean_pp_neg_at_what"] = float(np.mean([m_hat[idx[k]] for k in neg])) if neg else None
ctrl["neg_pp_at_what"] = {k: float(m_hat[idx[k]]) for k in neg}
ctrl["neg_feat"] = {k: feat.get(k) for k in neg}
if len(pos) < 5 or len(neg) < 5:
    ctrl["verdict"] = "underpowered"
elif not window:
    ctrl["verdict"] = "c: no window"
else:
    ctrl["window_w"] = [min(window), max(window)]
    ctrl["window_sum_pp"] = [float(np.median((R * x / (R * x + 1)).sum(axis=1))) for x in ctrl["window_w"]]
    ctrl["verdict"] = "a: w_hat inside window" if min(window) <= w_hat <= max(window) else "b: window excludes w_hat"
# where does each condition hold separately
ctrl["w_min_pos_ge_0.9"] = next((w for w, mp, _ in curve if mp >= 0.9), None)
ctrl["w_max_neg_le_0.1"] = max((w for w, _, mn in curve if mn <= 0.1), default=None)
res["controls"] = ctrl

# ---------- 4. LOESS (R defaults: span .75, degree 2, tricube, direct) ----------
gx, gy = [], []
for l in open(f"{SUPP}/Genome_Size_Number_estimates/merged_data_genomes_kos_bp.csv").read().splitlines()[1:]:
    f = l.split(",")
    gx.append(float(f[4])); gy.append(float(f[3]))
gx, gy = np.array(gx), np.array(gy)

def loess(x0, x=gx, y=gy, span=0.75):
    n = len(x); q = int(math.floor(n * span))
    d = np.abs(x - x0)
    h = np.sort(d)[q - 1]
    u = np.clip(d / h, 0, 1)
    wt = (1 - u ** 3) ** 3
    X = np.vstack([np.ones(n), x - x0, (x - x0) ** 2]).T
    W = np.sqrt(wt)
    beta = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)[0]
    return float(beta[0])

lo = {"x_min": float(gx.min()), "x_max": float(gx.max()), "n": len(gx),
      "pred_at_1298.25": loess(1298.25), "pred_at_1255": loess(1255), "pred_at_1340": loess(1340)}
lo["gate_pass"] = abs(lo["pred_at_1298.25"] - 2657) / 2657 <= 0.01
if lo["gate_pass"]:
    lo["dose"] = [{"w": d["w"], "kos": d["sum_pp_median_run"],
                   "proteins": loess(d["sum_pp_median_run"]) if d["sum_pp_median_run"] >= gx.min() else None}
                  for d in dose[::5]]
    lo["at_w_hat"] = loess(float(np.median((R * w_hat / (R * w_hat + 1)).sum(axis=1))))
    if "window_sum_pp" in ctrl:
        lo["window"] = [loess(s) if s >= gx.min() else None for s in ctrl["window_sum_pp"]]
res["loess"] = lo

# ---------- 6. dropped families ----------
tax = {}
for l in open(f"{SUPP}/Taxonomy/ArcBacEuk_names.csv").read().splitlines()[1:]:
    p = l.split("\t")
    if len(p) >= 2:
        tax[p[0]] = p[1].split("_")[0]
info = {}
for fp in sorted(glob.glob(f"{SUPP}/Gene_Fastas/Pure_sequences/K*.fasta")):
    k = os.path.basename(fp).split(".")[0]
    gs = collections.Counter(l[1:].split("-", 1)[0].strip() for l in open(fp) if l.startswith(">"))
    info[k] = gs
allg = {g for c in info.values() for g in c}
nA = sum(tax.get(g) == "Archaea" for g in allg); nB = sum(tax.get(g) == "Bacteria" for g in allg)

def desc(keys):
    seqs = [sum(info[k].values()) for k in keys]
    gen = [len(info[k]) for k in keys]
    uni = [sum(tax.get(g) == "Archaea" for g in info[k]) / nA >= 0.5 and
           sum(tax.get(g) == "Bacteria" for g in info[k]) / nB >= 0.5 for k in keys]
    return {"n": len(keys), "median_seqs": statistics.median(seqs), "median_genomes": statistics.median(gen),
            "universal_frac": sum(uni) / len(keys), "n_universal": sum(uni),
            "universal": [k for k, u in zip(keys, uni) if u]}
scored = set(fams)
missing = sorted(k for k in info if k not in scored)
in_any_run = set().union(*(set(runs[i][1]) for i in RUNS))
ds, dm = desc(sorted(k for k in info if k in scored)), desc(missing)
drop = {"nA": nA, "nB": nB, "n_fasta": len(info), "scored": {k: v for k, v in ds.items() if k != "universal"},
        "missing": dm, "missing_in_some_run_only": len([k for k in missing if k in in_any_run]),
        "scored_without_fasta": len(scored - set(info))}
drop["ratio_universal"] = dm["universal_frac"] / ds["universal_frac"] if ds["universal_frac"] else None
drop["ratio_median_seqs"] = dm["median_seqs"] / ds["median_seqs"]
drop["flag_undercount"] = (drop["ratio_universal"] or 0) >= 2 or drop["ratio_median_seqs"] >= 2
res["dropped"] = drop

json.dump(res, open(f"{OUT}/realdata_v7.json", "w"), indent=1)
show = {k: v for k, v in res.items() if k not in ("dose",)}
show["bf"] = {k: v for k, v in res["bf"].items() if k != "per_sim"}
show["controls"] = {k: v for k, v in ctrl.items() if k != "curve"}
show["dropped"]["missing"] = {k: v for k, v in dm.items() if k != "universal"}
print(json.dumps(show, indent=1, default=str))
