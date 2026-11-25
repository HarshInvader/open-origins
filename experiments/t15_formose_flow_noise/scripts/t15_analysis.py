"""T15 (prereg docs/prereg/t15_formose_flow_noise.md): do formose mixtures under changing flow differ
from steady state by more than a repeat run does?

Claim under test: van Duppen, Daines, Robinson & Huck 2023, J Am Chem Soc 145:7559,
doi:10.1021/jacs.3c00908 (PMC10080678): "Again, we observed average concentrations of compounds which
deviate from steady-state averages (3, 5, 7, and 11; p <= 1 x 10^-4, in all compound series; see Figures
S12 and S13)."  The authors' p-values come from scipy.stats.ttest_ind on the ~45 serial samples of each
run, treated as independent draws (processing_scripts_formose/data_analysis_functions.py, read as text).

Usage (single process, single thread; run under nice -n 20 with OMP/OPENBLAS threads = 1):
  python -I t15_analysis.py <experiments/t15_formose_flow_noise dir> gate       # block length, repeat pairs
  python -I t15_analysis.py <dir> planted <VARIANT> <N_REP>                      # synthetic runs only
  python -I t15_analysis.py <dir> planted_merge
  python -I t15_analysis.py <dir> dryrun      # `real` code; repeat pairs stand in for every comparison
  python -I t15_analysis.py <dir> sealcheck
  python -I t15_analysis.py <dir> real        # sealed; refuses without the seal

Inputs: the authors' deposited run files (raw/github/src/..., gitignored; Latin-1 text), pinned to commit
94c10347154fac67371c5b9101ce79ffaf70ffdc of github.com/huckgroup/Formose_2022. They are parsed as plain
text (split on commas, float()); nothing in them is executed. Every input's sha256 is checked.

Definitions (fixed; see the prereg for the reasons):
  series      a run's concentration column for one compound, in sample order; "nan" cells are dropped
              (the authors turn them into 0; that convention is used only for the reported t-test).
  sd          within-run standard deviation, ddof = 1.
  D(a, b)     |mean_a - mean_b| / sqrt((sd_a^2 + sd_b^2) / 2).
  D_rep(c)    max(D(EXP001, EXP010), D(EXP003, EXP012)) for compound c (the two repeat pairs).
  D_dyn(c)    median over the 8 dynamic-vs-steady comparisons (COMPARISONS) of D(dynamic, steady).
  Delta(c)    D_dyn(c) - D_rep(c); 95% percentile interval from a circular moving-block bootstrap that
              resamples each run's sample positions (same positions for every compound of a run).
  block L     from integrated autocorrelation times of within-run demeaned series (no mean is compared).
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t15_formose_flow_noise/scripts/t15_analysis.py"
SEED = 20261125
SRC = "raw/github/src"

RUNS = ["EXP%03d" % i for i in range(1, 13)]
SHA = {
    "info_files/compound_information.csv": "9fa500e42125c2d0576ee682af89f8c0831eaf424f93fa05ac69c10b9b2f1c1a",
    "info_files/list_exp.csv": "3458b6edfd0ac2558fc65ba2f5c7258f9d15fa8ffb3cd2a034ef6ce667500eb4",
    "EXP001": "adbf96e5f3ea472f085f97e03eb4f644c8bec76a648cba12a3e9cd940fd0c117",
    "EXP002": "1070cdf34c844caaab285833e5f5bb84b6a8edce64e5be4b80fe9269860cfa45",
    "EXP003": "88a997ba04b486861b462c08822aad66a608b5f41beafb2d907281281847f01f",
    "EXP004": "753a355133f3bb2b333b2fd2a2645279c47d38b05b0f8a5adcebdce69f933322",
    "EXP005": "055096744dbe320e2e1b7850c464617826092d17499d792ca9e05f8ef56e981b",
    "EXP006": "5ecc4074e2d92cf91bdbb56c19536b57e93e8c3c64200c18c94a2ef4415aca15",
    "EXP007": "6bd44020a0339012b01ed36da18698e8af4c478a47fac0ab7fcedbbecda54f05",
    "EXP008": "4e209a9574ac31bd973ab42f1c75b05b748d09c838697f22cc81973a846762be",
    "EXP009": "bbe7ea06b9c71427f67cff41b48252224d3f16482eeac426b402bc468dc099be",
    "EXP010": "4ca57dc428717406bb128422c624f17949c43f37b7430cb943c52e45d3a7c8a9",
    "EXP011": "dd6ec0841bd14229796246baf23b5f0de3fca0f86fe64105b5e52f50fea171c7",
    "EXP012": "c847678cc7d1031d74ca18f7fa04b16c66d1aaacb5049bc6d6ddb5be8d411220",
}

# The four compounds named in the quote, by the authors' numbering (compound_information.csv).
C4 = {3: "O=C(CO)CO", 5: "O=C[C@@H](O)[C@H](O)CO", 7: "O=C(CO)[C@H](O)CO", 11: "O=C(CO)[C@@H](O)[C@H](O)CO"}
C4_NAMES = {3: "dihydroxyacetone", 5: "threose", 7: "erythrulose", 11: "xylulose"}

# The authors' sets (01_composition_analysis.py): first run of each set is steady state (sigma = 0).
SETS = [("EXP004", ["EXP005", "EXP006"], "20 mM HCHO, amplitude"),
        ("EXP001", ["EXP002", "EXP003"], "50 mM HCHO, amplitude"),
        ("EXP007", ["EXP008", "EXP009"], "100 mM HCHO, amplitude"),
        ("EXP010", ["EXP012", "EXP011"], "50 mM HCHO, rate")]
COMPARISONS = [(dyn, st) for st, dyns, _ in SETS for dyn in dyns]   # (dynamic, steady), 8 of them
REPEATS = [("EXP001", "EXP010"), ("EXP003", "EXP012")]               # identical settings, other day
REPEAT_RUNS = ["EXP001", "EXP010", "EXP003", "EXP012"]
STEADY = [s for s, _, _ in SETS]

B_REAL = 4000            # bootstrap replicates, real and dry run
B_PLANT = 400            # bootstrap replicates per synthetic world
ALPHA = 0.05
K_KILL, K_SUP = 2.0, 3.0  # the plan's multipliers
NEED = 3                 # "at least three of four"
SHIFTS = [0.0, 1.0, 2.0, 3.0, 5.0]            # the user-specified grid (pooled within-run SD)
SHIFTS_EXT = [10.0, 20.0, 40.0]              # reported: where support becomes reachable
PRIMARY_RULE = "revised"  # set after the planted check; see prereg C2


# ---------------------------------------------------------------- io
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def path_of(k):
    if k.startswith("EXP"):
        return os.path.join(D, SRC, "Extended_data_GH", k, "Analysed_data", k + "_Data.csv")
    return os.path.join(D, SRC, k)


def check_inputs():
    bad = {k: sha256(path_of(k)) for k in SHA if sha256(path_of(k)) != SHA[k]}
    if bad:
        sys.exit("input hash mismatch: %s" % json.dumps(bad))


def seal_status():
    me = sha256(os.path.abspath(__file__))
    hp = os.path.join(REPO, "docs", "prereg", "HASHES.txt")
    named = hashed = False
    if os.path.exists(hp):
        for line in open(hp, encoding="utf-8"):
            if SELF in line:
                named = True
                if line.split()[:1] == [me]:
                    hashed = True
    return {"script_sha256": me, "line_naming_script": named, "line_with_current_hash": hashed,
            "real_allowed": named and hashed}


def dump(name, obj):
    os.makedirs(os.path.join(D, "scripts_out"), exist_ok=True)
    with open(os.path.join(D, "scripts_out", name), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    print("wrote scripts_out/" + name, flush=True)


def load_run(run):
    """Return {smiles: float array in sample order, nan kept} for one run. Plain-text parse only."""
    p = path_of(run)
    if os.path.getsize(p) > 5_000_000:
        sys.exit("file too large: " + run)
    lines = open(p, encoding="latin-1").read().split("\n")
    i0 = [k for k, l in enumerate(lines) if l.startswith("start_data")]
    i1 = [k for k, l in enumerate(lines) if l.startswith("end_data")]
    if len(i0) != 1 or len(i1) != 1:
        sys.exit("bad data section: " + run)
    hdr = [e for e in lines[i0[0] + 1].split(",") if e != ""]
    rows = [[e for e in lines[k].split(",") if e != ""] for k in range(i0[0] + 2, i1[0])]
    if any(len(r) != len(hdr) for r in rows):
        sys.exit("ragged rows: " + run)
    order = np.array([float(r[0]) for r in rows])
    if np.any(np.diff(order) <= 0):
        sys.exit("sample order not increasing: " + run)
    out = {}
    for j, h in enumerate(hdr[1:], 1):
        smi = h.split("/")[0].strip()
        if smi in out:
            sys.exit("duplicate column %s in %s" % (smi, run))
        out[smi] = np.array([float("nan") if r[j].strip().lower() == "nan" else float(r[j]) for r in rows])
    return out


def load_all():
    check_inputs()
    data = {}
    for r in RUNS:
        cols = load_run(r)
        for c, smi in C4.items():
            if smi not in cols:
                sys.exit("compound %d missing in %s" % (c, r))
        data[r] = cols
    return data


def series4(data, runs):
    """{run: (n x 4) array, rows with any nan among the 4 compounds dropped}, plus nan counts."""
    out, nan_counts = {}, {}
    for r in runs:
        m = np.column_stack([data[r][C4[c]] for c in C4])
        keep = ~np.isnan(m).any(axis=1)
        nan_counts[r] = int((~keep).sum())
        out[r] = m[keep]
    return out, nan_counts


# ---------------------------------------------------------------- autocorrelation and block length
def tau_int(x):
    """Integrated autocorrelation time of a demeaned series: 1 + 2 * sum of the initial positive
    run of the sample autocorrelation, lags 1 .. floor(n/4)."""
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    v = np.dot(x, x)
    if v == 0:
        return 1.0
    t = 1.0
    for k in range(1, n // 4 + 1):
        rho = np.dot(x[:-k], x[k:]) / v
        if rho <= 0:
            break
        t += 2 * rho
    return float(t)


def lag1(x):
    x = np.asarray(x, float) - np.mean(x)
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x))


def block_length(ser):
    """L = ceil(2 * 75th percentile of tau over every run x the four compounds), at least 2, at most
    floor(shortest run / 4). Uses demeaned series only."""
    taus = {r: [tau_int(ser[r][:, j]) for j in range(4)] for r in ser}
    allt = np.array([t for r in taus for t in taus[r]])
    q75 = float(np.quantile(allt, 0.75))
    nmin = min(len(ser[r]) for r in ser)
    L = int(min(max(2, math.ceil(2 * q75)), nmin // 4))
    return L, taus, q75


# ---------------------------------------------------------------- statistics
def dstat(a, b):
    """a, b: (..., n) arrays -> D along last axis."""
    ma, mb = a.mean(-1), b.mean(-1)
    va, vb = a.var(-1, ddof=1), b.var(-1, ddof=1)
    return np.abs(ma - mb) / np.sqrt((va + vb) / 2)


def boot_idx(n, L, B, rng):
    """Circular moving-block bootstrap indices, shape (B, n)."""
    nb = -(-n // L)
    starts = rng.integers(0, n, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(L)[None, None, :]) % n
    return idx.reshape(B, nb * L)[:, :n]


def analyse(ser, comps, reps, L, B, rng):
    """Core of `real` (also used by dryrun and planted). ser: {run: (n x 4)}.
    Returns per-compound D_rep, D_dyn, Delta and its bootstrap interval, and per-comparison D."""
    runs = sorted({r for p in comps + reps for r in p})
    # point estimates, shape (4,)
    Dc = np.array([dstat(ser[a].T, ser[b].T) for a, b in comps])        # (ncomp, 4)
    Dr = np.array([dstat(ser[a].T, ser[b].T) for a, b in reps])         # (2, 4)
    d_dyn, d_rep = np.median(Dc, 0), Dr.max(0)
    # bootstrap: same positions for all compounds of a run; each run resampled once per replicate
    bs = {}
    for r in runs:
        idx = boot_idx(len(ser[r]), L, B, rng)
        bs[r] = np.transpose(ser[r][idx], (2, 0, 1))                    # (4, B, n)
    Dcb = np.array([dstat(bs[a], bs[b]) for a, b in comps])             # (ncomp, 4, B)
    Drb = np.array([dstat(bs[a], bs[b]) for a, b in reps])              # (2, 4, B)
    delta_b = np.median(Dcb, 0) - Drb.max(0)                            # (4, B)
    lo = np.quantile(delta_b, ALPHA / 2, axis=1)
    hi = np.quantile(delta_b, 1 - ALPHA / 2, axis=1)
    return {"D_comp": Dc, "D_rep_pairs": Dr, "D_dyn": d_dyn, "D_rep": d_rep,
            "delta": d_dyn - d_rep, "lo": lo, "hi": hi}


def verdicts(res):
    """Both rule forms. Plan literal and revised (prereg C2). Arrays over the four compounds."""
    dd, dr, lo, hi = res["D_dyn"], res["D_rep"], res["lo"], res["hi"]
    k1 = dd < K_KILL * dr
    k2_plan = (lo <= 0) & (hi >= 0)          # interval includes 0
    k2_rev = lo <= 0                          # interval does not lie wholly above 0
    sup = (dd > K_SUP * dr) & (lo > 0)
    out = {}
    for name, k2 in (("plan", k2_plan), ("revised", k2_rev)):
        kill = (int(k1.sum()) >= NEED) and (int(k2.sum()) >= NEED)
        support = int(sup.sum()) >= NEED
        v = "support" if support else ("kill" if kill else "neither")
        if support and kill:
            v = "conflict"
        out[name] = {"verdict": v, "n_k1": int(k1.sum()), "n_k2": int(k2.sum()), "n_support": int(sup.sum())}
    return out


# ---------------------------------------------------------------- gate
def gate():
    data = load_all()
    ser, nans = series4(data, RUNS)
    # 1. block length from demeaned series of every run (no mean compared or printed)
    L, taus, q75 = block_length(ser)
    sd_ratio = {}
    for dyn, st in COMPARISONS:
        sd_ratio[dyn + "/" + st] = [float(ser[dyn][:, j].std(ddof=1) / ser[st][:, j].std(ddof=1)) for j in range(4)]
    blk = {"L": L, "tau_q75": q75, "tau": taus, "n_after_nan_drop": {r: len(ser[r]) for r in RUNS},
           "nan_rows_dropped": nans, "within_run_sd_ratio_dyn_over_steady": sd_ratio}
    print(json.dumps({"block_length": L, "tau_q75": q75}), flush=True)
    # 2. repeat pairs only (disclosed): D for every compound present in all four repeat runs
    common = sorted(set.intersection(*[set(data[r]) for r in REPEAT_RUNS]))
    rows = []
    for smi in common:
        ds = []
        for a, b in REPEATS:
            x, y = data[a][smi], data[b][smi]
            x, y = x[~np.isnan(x)], y[~np.isnan(y)]
            ds.append(float(dstat(x, y)) if len(x) > 2 and len(y) > 2 else float("nan"))
        ratio = max(ds) / min(ds) if min(ds) > 0 else float("inf")
        num = [k for k, s in C4.items() if s == smi]
        rows.append({"smiles": smi, "compound": num[0] if num else None, "D_001_010": ds[0], "D_003_012": ds[1],
                     "ratio": ratio, "disagree_gt3": bool(ratio > 3)})
    n_dis = sum(r["disagree_gt3"] for r in rows)
    passed = n_dis <= len(rows) / 2
    # bootstrap intervals for the repeat-pair mean differences, the four compounds (SD units)
    rng = np.random.default_rng([SEED, 1])
    rep_ci = {}
    for a, b in REPEATS:
        ia, ib = boot_idx(len(ser[a]), L, B_REAL, rng), boot_idx(len(ser[b]), L, B_REAL, rng)
        xa, xb = np.transpose(ser[a][ia], (2, 0, 1)), np.transpose(ser[b][ib], (2, 0, 1))
        db = dstat(xa, xb)
        rep_ci[a + "/" + b] = {str(c): [float(np.quantile(db[j], .025)), float(np.quantile(db[j], .975))]
                               for j, c in enumerate(C4)}
    four = [r for r in rows if r["compound"] in C4]
    res = {"mode": "gate", "script_sha256": sha256(os.path.abspath(__file__)), "inputs": SHA,
           "block": blk, "repeat_pairs_all_common_compounds": rows, "n_common": len(rows),
           "n_disagree_gt3": n_dis, "gate_passed": bool(passed),
           "four_compounds_disagree_gt3": int(sum(r["disagree_gt3"] for r in four)),
           "repeat_D_bootstrap_95": rep_ci,
           "rule": "fail ('cannot decide') if max/min of the two repeat-pair D exceeds 3 for more than half "
                   "of the compounds present in all four repeat runs"}
    dump("t15_gate.json", res)
    print(json.dumps({"n_common": len(rows), "n_disagree_gt3": n_dis, "gate_passed": bool(passed),
                      "four_disagree": res["four_compounds_disagree_gt3"]}), flush=True)


def gate_state():
    p = os.path.join(D, "scripts_out", "t15_gate.json")
    if not os.path.exists(p):
        sys.exit("REFUSED: run the gate first.")
    g = json.load(open(p))
    if g["script_sha256"] != sha256(os.path.abspath(__file__)):
        sys.exit("REFUSED: scripts_out/t15_gate.json was written by another version of this script; re-run gate.")
    return g


# ---------------------------------------------------------------- planted check
def noise_params(ser):
    """Per compound, from the four repeat runs only: within-run sd (pooled), lag-1 autocorrelation (mean),
    and run-offset sd sigma_u from the two repeat-pair differences (SD units)."""
    pars = []
    for j in range(4):
        sd = math.sqrt(np.mean([ser[r][:, j].var(ddof=1) for r in REPEAT_RUNS]))
        phi = float(np.clip(np.mean([lag1(ser[r][:, j]) for r in REPEAT_RUNS]), 0.0, 0.95))
        nbar = np.mean([len(ser[r]) for r in REPEAT_RUNS])
        v = (1 + phi) / (1 - phi) / nbar                   # var of a run mean / sd^2, AR(1) approx.
        d2 = np.mean([((ser[a][:, j].mean() - ser[b][:, j].mean()) / sd) ** 2 for a, b in REPEATS])
        su = math.sqrt(max(0.0, d2 / 2 - v))
        pars.append({"sd": sd, "phi": phi, "sigma_u": su})
    return pars


def ar1(n, phi, rng):
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0]
    s = math.sqrt(1 - phi * phi)
    for t in range(1, n):
        x[t] = phi * x[t - 1] + s * e[t]
    return x


VARIANTS = {
    # name: (sigma_u multiplier, dynamic-run sd multiplier, phi override or None)
    "base": (1.0, 1.0, None),
    "no_offset": (0.0, 1.0, None),
    "half_offset": (0.5, 1.0, None),
    "double_offset": (2.0, 1.0, None),
    "dyn_sd_x1.5": (1.0, 1.5, None),
    "phi_0.8": (1.0, 1.0, 0.8),
    "real_resid": (1.0, 1.0, "resid"),   # noise = block resample of a real demeaned repeat run
}


def resid_noise(real, j, n, L, rng):
    """Unit-sd noise: circular block resample of a randomly chosen real repeat run's demeaned series."""
    x = real[REPEAT_RUNS[rng.integers(4)]][:, j]
    x = (x - x.mean()) / x.std(ddof=1)
    return x[boot_idx(len(x), L, 1, rng)[0]][:n] if n <= len(x) else np.resize(x[boot_idx(len(x), L, 1, rng)[0]], n)


def synth_world(ns, pars, shift, var, rng, real=None, L=5):
    """Synthetic 12-run world in units of each compound's pooled within-run sd (repeat runs).
    Every run gets an independent offset u ~ N(0, sigma_u^2); every dynamic run gets +shift."""
    su_m, dyn_m, phi_o = VARIANTS[var]
    dyn_runs = {d for d, _ in COMPARISONS}
    ser = {}
    for r in RUNS:
        cols = []
        for j in range(4):
            p = pars[j]
            sdm = dyn_m if r in dyn_runs else 1.0
            u = su_m * p["sigma_u"] * rng.standard_normal()
            if phi_o == "resid":
                e = resid_noise(real, j, ns[r], L, rng)
            else:
                e = ar1(ns[r], p["phi"] if phi_o is None else phi_o, rng)
            cols.append(10.0 + u + (shift if r in dyn_runs else 0.0) + sdm * e)
        ser[r] = np.column_stack(cols)
    return ser


def planted():
    var, nrep = sys.argv[3], int(sys.argv[4])
    g = gate_state()
    if not g["gate_passed"]:
        sys.exit("gate failed: cannot decide")
    data = load_all()
    ser, _ = series4(data, RUNS)
    L = g["block"]["L"]
    pars = noise_params(ser)
    ns = {r: len(ser[r]) for r in RUNS}
    rows = []
    t0 = time.process_time()
    for si, shift in enumerate(SHIFTS + SHIFTS_EXT):
        rng = np.random.default_rng([SEED, 2, list(VARIANTS).index(var), si])
        counts = {"plan": {}, "revised": {}}
        for _ in range(nrep):
            w = synth_world(ns, pars, shift, var, rng, real=ser, L=L)
            v = verdicts(analyse(w, COMPARISONS, REPEATS, L, B_PLANT, rng))
            for k in counts:
                counts[k][v[k]["verdict"]] = counts[k].get(v[k]["verdict"], 0) + 1
        rows.append({"shift_sd": shift, "n": nrep, "counts": counts})
        print(json.dumps(rows[-1]), flush=True)
    dump("t15_planted_%s.json" % var, {"script_sha256": sha256(os.path.abspath(__file__)), "variant": var,
                                       "variant_def": VARIANTS[var], "L": L, "B": B_PLANT,
                                       "noise_params": {str(c): pars[j] for j, c in enumerate(C4)},
                                       "rows": rows, "cpu_seconds": time.process_time() - t0})


def planted_merge():
    me = sha256(os.path.abspath(__file__))
    out = {"merged_by_script_sha256": me, "variants": {}}
    for var in VARIANTS:
        p = os.path.join(D, "scripts_out", "t15_planted_%s.json" % var)
        if os.path.exists(p):
            j = json.load(open(p))
            out["variants"][var] = {"computed_by": j["script_sha256"], "noise_params": j["noise_params"],
                                    "rows": j["rows"]}
    dump("t15_planted.json", out)


# ---------------------------------------------------------------- dry run and real
def report(ser, comps, L, B, rng, data, mode):
    res = analyse(ser, comps, REPEATS, L, B, rng)
    v = verdicts(res)
    per_c = {}
    for j, c in enumerate(C4):
        per_c[str(c)] = {"name": C4_NAMES[c], "D_dyn": res["D_dyn"][j], "D_rep": res["D_rep"][j],
                         "D_rep_pairs": list(res["D_rep_pairs"][:, j]), "delta": res["delta"][j],
                         "ci95": [res["lo"][j], res["hi"][j]],
                         "D_per_comparison": {a + "-" + b: res["D_comp"][k, j] for k, (a, b) in enumerate(comps)}}
    return {"mode": mode, "script_sha256": sha256(os.path.abspath(__file__)), "L": L, "B": B,
            "comparisons": comps, "repeats": REPEATS, "primary_rule": PRIMARY_RULE,
            "verdict": v[PRIMARY_RULE]["verdict"], "rules": v, "per_compound": per_c}


def reported_only(ser, data, L, rng):
    """Reported, no rule attached: per-set verdicts, authors' t-test reproduced, and an
    autocorrelation-aware t-test (n_eff = n / tau)."""
    from scipy import stats
    out = {"per_set": {}, "ttests": {}}
    for st, dyns, label in SETS:
        r = analyse(ser, [(d, st) for d in dyns], REPEATS, L, 2000, rng)
        out["per_set"][label] = verdicts(r)
    for dyn, st in COMPARISONS:
        for j, c in enumerate(C4):
            a0 = np.nan_to_num(data[dyn][C4[c]], nan=0.0)       # the authors' nan -> 0
            b0 = np.nan_to_num(data[st][C4[c]], nan=0.0)
            p_auth = float(stats.ttest_ind(b0, a0).pvalue)
            a, b = ser[dyn][:, j], ser[st][:, j]
            na, nb = len(a) / tau_int(a), len(b) / tau_int(b)
            se = math.sqrt(a.var(ddof=1) / na + b.var(ddof=1) / nb)
            t = (a.mean() - b.mean()) / se
            dfw = se ** 4 / ((a.var(ddof=1) / na) ** 2 / max(na - 1, 1) + (b.var(ddof=1) / nb) ** 2 / max(nb - 1, 1))
            out["ttests"]["%s-%s c%d" % (dyn, st, c)] = {
                "p_authors_ttest_ind": p_auth, "p_neff_welch": float(2 * stats.t.sf(abs(t), dfw)),
                "signed_diff_sd": float((a.mean() - b.mean()) / math.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2))}
    return out


def dryrun():
    g = gate_state()
    if not g["gate_passed"]:
        sys.exit("gate failed: cannot decide")
    data = load_all()
    ser, _ = series4(data, RUNS)
    # stand-in: each dynamic-vs-steady comparison is replaced by a repeat pair (alternating, both orders)
    stand = [REPEATS[k % 2] if (k // 2) % 2 == 0 else REPEATS[k % 2][::-1] for k in range(len(COMPARISONS))]
    res = report(ser, stand, g["block"]["L"], B_REAL, np.random.default_rng([SEED, 3]), data,
                 "dryrun_repeat_pairs_stand_in")
    dump("t15_dryrun.json", res)
    print(json.dumps({"verdict": res["verdict"], "rules": res["rules"]}), flush=True)


def real():
    st = seal_status()
    if not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    g = gate_state()
    if not g["gate_passed"]:
        sys.exit("gate failed: cannot decide")
    data = load_all()
    ser, _ = series4(data, RUNS)
    res = report(ser, COMPARISONS, g["block"]["L"], B_REAL, np.random.default_rng([SEED, 4]), data, "real")
    res["reported_only"] = reported_only(ser, data, g["block"]["L"], np.random.default_rng([SEED, 5]))
    dump("t15_real.json", res)
    print(json.dumps({"verdict": res["verdict"], "rules": res["rules"]}), flush=True)


if __name__ == "__main__":
    if MODE == "gate":
        gate()
    elif MODE == "planted":
        planted()
    elif MODE == "planted_merge":
        planted_merge()
    elif MODE == "dryrun":
        dryrun()
    elif MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "real":
        real()
    else:
        sys.exit("unknown mode")
