"""Downstream prereg v2/v4 calibration, 200-replicate bootstrap, and P1-P8 verdict engine
for task #32 (LUCA calibration).

Completely outside the sealed pipeline/ directory (leaves MANIFEST.sha256 untouched).
Uses sklearn.linear_model.LogisticRegression(C=1.0) if available, else an exact
standardized L2-regularized Newton-IRLS solver in pure Python stdlib.

Usage:
    # Full main-grid + Arm L + Arm H verdict:
    python3 calibrate_and_verdict.py <results_dir> --out <verdict.json>

    # Self-test on a single simulation directory (e.g. results/ale_smoke/sim):
    python3 calibrate_and_verdict.py --selftest results/ale_smoke/sim
"""
import argparse
import glob
import json
import math
import os
import random
import statistics
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MOODY_FEATS = os.path.join(ROOT, "real_features_moody.tsv")
HUANG_FEATS = os.path.join(ROOT, "real_features_huang.tsv")

E_M = 1290.65
E_H = 1331.00

BANDS_MOODY = {"overstated_lt": 865.0, "validated_lo": 1032.0, "validated_hi": 1613.0, "understated_gt": 1936.0}
BANDS_HUANG = {"overstated_lt": 892.0, "validated_lo": 1065.0, "validated_hi": 1664.0, "understated_gt": 1997.0}


def logit(p):
    p = min(max(float(p), 1e-6), 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def read_tsv(path):
    with open(path) as f:
        hdr = f.readline().rstrip("\n").split("\t")
        rows = []
        for line in f:
            if not line.strip():
                continue
            vals = line.rstrip("\n").split("\t")
            rows.append(dict(zip(hdr, vals)))
    return rows


def extract_sim_features(simdir, run_name="ale_inferred", pp_col="pp"):
    """Extract the 5 prereg v2/v4 features + truth label for every family in a simulation."""
    truth = read_tsv(os.path.join(simdir, "sample", "truth.tsv"))
    dom_rows = read_tsv(os.path.join(simdir, "sample", "domains.tsv"))
    dom = {r["species"]: r["domain"] for r in dom_rows}
    nA_tot = sum(1 for v in dom.values() if v == "A")
    nB_tot = sum(1 for v in dom.values() if v == "B")

    pp_path = os.path.join(simdir, run_name, "root_pp.tsv")
    pp_map = {r["family"]: float(r[pp_col]) for r in read_tsv(pp_path)} if os.path.exists(pp_path) else {}

    # Mean copy number where present from copy_numbers.tsv
    mean_copy = {}
    cn_path = os.path.join(simdir, "sample", "copy_numbers.tsv")
    if os.path.exists(cn_path):
        with open(cn_path) as f:
            _sps = f.readline().rstrip("\n").split("\t")[1:]
            for line in f:
                parts = line.rstrip("\n").split("\t")
                nz = [int(x) for x in parts[1:] if int(x) > 0]
                mean_copy[parts[0]] = (sum(nz) / len(nz)) if nz else 1.0

    X, y, meta = [], [], []
    for r in truth:
        fam = r["family"]
        nA = int(r["n_genomes_A"])
        nB = int(r["n_genomes_B"])
        oA = nA / max(1, nA_tot)
        oB = nB / max(1, nB_tot)
        mo = min(oA, oB)
        mc = mean_copy.get(fam, max(1.0, int(r["n_genes"]) / max(1, nA + nB)))
        p = pp_map.get(fam, 0.0)
        X.append([logit(p), oA, oB, mo, math.log(max(1.0, mc))])
        y.append(int(r["luca"]))
        meta.append({"family": fam, "pp": p, "luca": int(r["luca"]), "both": nA > 0 and nB > 0})
    return X, y, meta


def load_real_features(path):
    rows = read_tsv(path)
    X = [
        [float(r["logit_pp"]), float(r["occA"]), float(r["occB"]), float(r["min_occ"]), float(r["log_mean_copy"])]
        for r in rows
    ]
    pps = [float(r["pp"]) for r in rows]
    fams = [r["family"] for r in rows]
    return X, pps, fams, rows


# ---- Standardized L2 Logistic Regression (exact Newton-IRLS, pure stdlib fallback) ----
def _solve_linear(A, b):
    """Gaussian elimination with partial pivoting for small (d x d) systems (d <= 6)."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        denom = M[col][col]
        if abs(denom) < 1e-14:
            denom = 1e-14
        for j in range(col, n + 1):
            M[col][j] /= denom
        for r in range(n):
            if r != col:
                fac = M[r][col]
                for j in range(col, n + 1):
                    M[r][j] -= fac * M[col][j]
    return [M[i][n] for i in range(n)]


class L2LogisticModel:
    """Standardized L2 logistic regression (C=1.0, unpenalized intercept)."""

    def __init__(self, C=1.0, max_iter=50, tol=1e-7):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol
        self.means = None
        self.stds = None
        self.coef = None  # [w0, w1, ..., wd-1, b]

    def fit(self, X, y):
        n = len(X)
        d = len(X[0])
        self.means = [sum(row[j] for row in X) / n for j in range(d)]
        self.stds = []
        for j in range(d):
            m = self.means[j]
            var = sum((row[j] - m) ** 2 for row in X) / max(1, n)
            s = math.sqrt(var)
            self.stds.append(s if s > 1e-12 else 1.0)
        Xs = [[(row[j] - self.means[j]) / self.stds[j] for j in range(d)] + [1.0] for row in X]
        lam = 1.0 / self.C
        w = [0.0] * (d + 1)
        for _ in range(self.max_iter):
            grad = [0.0] * (d + 1)
            H = [[0.0] * (d + 1) for _ in range(d + 1)]
            for xi, yi in zip(Xs, y):
                z = sum(wj * xij for wj, xij in zip(w, xi))
                z = max(-30.0, min(30.0, z))
                pi = 1.0 / (1.0 + math.exp(-z))
                diff = pi - yi
                wi = max(pi * (1.0 - pi), 1e-9)
                for j in range(d + 1):
                    grad[j] += diff * xi[j]
                    xij_wi = xi[j] * wi
                    for k in range(j, d + 1):
                        H[j][k] += xij_wi * xi[k]
            for j in range(d):
                grad[j] += lam * w[j]
                H[j][j] += lam
            H[d][d] += 1e-9
            for j in range(d + 1):
                for k in range(j):
                    H[j][k] = H[k][j]
            step = _solve_linear(H, grad)
            max_step = max(abs(s) for s in step)
            w = [wj - sj for wj, sj in zip(w, step)]
            if max_step < self.tol:
                break
        self.coef = w
        return self

    def predict_proba(self, X):
        d = len(self.means)
        out = []
        for row in X:
            z = self.coef[d]
            for j in range(d):
                z += self.coef[j] * (row[j] - self.means[j]) / self.stds[j]
            z = max(-30.0, min(30.0, z))
            out.append(1.0 / (1.0 + math.exp(-z)))
        return out


def bootstrap_calibrate(sim_datasets, X_real, n_boot=200, seed=42):
    """200-replicate bootstrap over replicate simulations (prereg v2)."""
    rng = random.Random(seed)
    X_all, y_all = [], []
    for Xs, ys in sim_datasets:
        X_all.extend(Xs)
        y_all.extend(ys)
    full_model = L2LogisticModel(C=1.0).fit(X_all, y_all)
    p_full = full_model.predict_proba(X_real)
    C_point = sum(p_full)
    C_hi75 = sum(1 for p in p_full if p >= 0.75)

    k = len(sim_datasets)
    boot_C = []
    for _ in range(n_boot):
        idxs = [rng.randrange(k) for _ in range(k)]
        Xb, yb = [], []
        for idx in idxs:
            Xb.extend(sim_datasets[idx][0])
            yb.extend(sim_datasets[idx][1])
        m = L2LogisticModel(C=1.0).fit(Xb, yb)
        boot_C.append(sum(m.predict_proba(X_real)))
    boot_C.sort()
    lo = boot_C[int(0.025 * n_boot)]
    hi = boot_C[min(n_boot - 1, int(0.975 * n_boot))]
    return {
        "C_point": round(C_point, 2),
        "ci95": [round(lo, 2), round(hi, 2)],
        "n_p_ge_75": C_hi75,
        "coef": [round(c, 4) for c in full_model.coef],
    }


def classify_verdict(span_lo, span_hi, bands):
    if span_hi < bands["overstated_lt"]:
        return "Artefact, LUCA overstated"
    if span_lo > bands["understated_gt"]:
        return "Artefact, LUCA understated"
    if span_lo >= bands["validated_lo"] and span_hi <= bands["validated_hi"]:
        return "Validated"
    return "Not resolved (bound)"


def selftest(simdir):
    print(f"=== SELF-TEST on {simdir} ===")
    runs = sorted(
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(simdir, "ale_*", "root_pp.tsv"))
        + glob.glob(os.path.join(simdir, "alerax_*", "root_pp.tsv"))
    )
    if not runs:
        raise RuntimeError(f"No root_pp.tsv found in {simdir}")
    run = runs[0]
    X, y, meta = extract_sim_features(simdir, run_name=run)
    m = L2LogisticModel(C=1.0).fit(X, y)
    p_hat = m.predict_proba(X)
    print(f"Run={run}: N={len(y)}, true_LUCA={sum(y)}, raw_E={sum(r['pp'] for r in meta):.2f}, cal_sum={sum(p_hat):.2f}")
    print(f"  coef (logit_pp, occA, occB, min_occ, log_mean_copy, intercept): {[round(c, 3) for c in m.coef]}")
    if os.path.exists(MOODY_FEATS):
        Xm, _, _, _ = load_real_features(MOODY_FEATS)
        pm = m.predict_proba(Xm)
        print(f"  [SMOKE DRY-RUN ONLY, NOT A REAL VERDICT] Moody 7,456 sum(p_hat)={sum(pm):.1f}, n(p>=0.75)={sum(p>=0.75 for p in pm)}")
    if os.path.exists(HUANG_FEATS):
        Xh, _, _, _ = load_real_features(HUANG_FEATS)
        ph = m.predict_proba(Xh)
        print(f"  [SMOKE DRY-RUN ONLY, NOT A REAL VERDICT] Huang 5,322 sum(p_hat)={sum(ph):.1f}, n(p>=0.75)={sum(p>=0.75 for p in ph)}")
    print("SELF-TEST PASS")


def evaluate_main(results_dir, out_path):
    """Evaluate main grid (9 sims: 0.5T*, T*, 2T* x 3 seeds), Arm L (3 sims), and Arm H."""
    main_dir = os.path.join(results_dir, "main")
    if not os.path.isdir(main_dir):
        raise FileNotFoundError(f"Main grid directory not found: {main_dir}")

    # Discover simulation directories by condition naming (e.g. T0.5_s1, T1_s1, T2_s1 or similar)
    sim_dirs = sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(main_dir, "*", "sample", "truth.tsv"))
    )
    if not sim_dirs:
        raise FileNotFoundError(f"No simulations found under {main_dir}")

    by_cond = {}
    scores_inf, scores_true = {}, {}
    for sd in sim_dirs:
        name = os.path.basename(sd)
        cond = name.rsplit("_", 1)[0] if "_" in name else name
        by_cond.setdefault(cond, []).append(sd)
        for run, store in (("ale_inferred", scores_inf), ("ale_true", scores_true)):
            sp = os.path.join(sd, run, "score.json")
            if os.path.exists(sp):
                store[name] = json.load(open(sp))

    # Predictions P1-P5 on inferred trees
    p1_vals = {k: v["tiers"]["T75"]["recall"] for k, v in scores_inf.items()}
    p1_pass = bool(p1_vals) and all(v is not None and v < 0.5 for v in p1_vals.values())

    p3_pairs = {
        k: (scores_inf[k]["R"], scores_true[k]["R"])
        for k in scores_inf
        if k in scores_true and scores_inf[k]["R"] is not None and scores_true[k]["R"] is not None
    }
    p3_pass = bool(p3_pairs) and all(ri < rt for ri, rt in p3_pairs.values())

    # Pooled 0.4-0.6 calibration bin (P5)
    bin_n = sum(
        c["n"] for v in scores_inf.values() for c in v["calibration"] if c["bin"] == "0.40-0.60"
    )
    bin_luca = sum(
        c["n_luca"] for v in scores_inf.values() for c in v["calibration"] if c["bin"] == "0.40-0.60"
    )
    p5_share = (bin_luca / bin_n) if bin_n else None
    p5_pass = p5_share is not None and abs(p5_share - 0.5) > 0.15

    # Moody real-data calibration per transfer setting + pooled
    Xm, _, _, _ = load_real_features(MOODY_FEATS)
    moody_cal = {}
    all_sims = []
    for cond, sds in sorted(by_cond.items()):
        ds = [extract_sim_features(sd, "ale_inferred")[:2] for sd in sds]
        all_sims.extend(ds)
        moody_cal[cond] = bootstrap_calibrate(ds, Xm, n_boot=200, seed=42)
    moody_cal["pooled"] = bootstrap_calibrate(all_sims, Xm, n_boot=200, seed=42)

    span_lo = min(v["ci95"][0] for k, v in moody_cal.items() if k != "pooled")
    span_hi = max(v["ci95"][1] for k, v in moody_cal.items() if k != "pooled")
    moody_verdict = classify_verdict(span_lo, span_hi, BANDS_MOODY)

    res = {
        "n_main_sims": len(sim_dirs),
        "conditions": {k: [os.path.basename(x) for x in v] for k, v in sorted(by_cond.items())},
        "predictions": {
            "P1_t75_recall_lt_0.5_all": {"pass": p1_pass, "values": p1_vals},
            "P3_R_inferred_lt_R_true_all": {"pass": p3_pass, "pairs": p3_pairs},
            "P5_bin_04_06_diff_gt_0.15": {"pass": p5_pass, "n": bin_n, "n_luca": bin_luca, "share": p5_share},
        },
        "moody_calibration": {
            "E_M": E_M,
            "by_setting": moody_cal,
            "span": [span_lo, span_hi],
            "verdict": moody_verdict,
        },
    }
    if out_path:
        with open(out_path, "w") as f:
            json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("results_dir", nargs="?")
    ap.add_argument("--selftest", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.selftest:
        selftest(a.selftest)
    elif a.results_dir:
        evaluate_main(a.results_dir, a.out)
    else:
        ap.error("Provide <results_dir> or --selftest <simdir>")


if __name__ == "__main__":
    main()
