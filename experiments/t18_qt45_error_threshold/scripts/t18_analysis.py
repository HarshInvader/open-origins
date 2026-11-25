"""T18: error threshold of the QT45 polymerase ribozyme from its own measured landscape.

Modes (run from experiments/, single-threaded, low priority):
  gate                          G0 estimator checks (analytic), G1 data + global-epistasis fit (landscape only)
  planted <family> <start> <n>  synthetic landscapes with a known threshold (families A, B, C)
  planted_merge                 apply the planted criterion to all parts
  real                          the sealed analysis; refuses unless docs/prereg/HASHES.txt names this file's sha256

Prereg: docs/prereg/t18_qt45_error_threshold.md. Nothing here before `real` computes a threshold on the real
landscape.
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t18_core as C  # noqa: E402

STUDY = C.STUDY
OUT = os.path.join(STUDY, "scripts_out")
REPO = os.path.dirname(C.EXPS)
os.makedirs(OUT, exist_ok=True)

E_MEAS = 1 - 0.941          # per-nucleotide error, (-) strand synthesis with the NNN pool (Gianni et al. 2026)
W_DEAD = 0.01               # the authors' rate for HD>=3 and unmeasured doubles
PLANT = dict(N=5000, k=5, T0=60, burn0=30, T=40, burn=15, refine=False)
FAMILIES = {"A": 0, "B": 1, "C": 2}


def jdump(obj, name):
    with open(os.path.join(OUT, name), "w") as fh:
        json.dump(obj, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


# ------------------------------------------------------------------ gate
def gate():
    t0 = time.process_time()
    rng = np.random.default_rng([20261125, 18, 0])
    out = dict(script_sha256=sha256(os.path.abspath(__file__)), core_sha256=sha256(os.path.join(C.HERE, "t18_core.py")))
    kw = {k: PLANT[k] for k in ("N", "k", "T0", "burn0", "T", "burn", "refine")}

    # G0a single peak: (1-u)^44 = w_dead
    an = brentq(lambda e: (1 - C.change_prob(e)) ** C.NS - W_DEAD, 1e-4, 0.4)
    mc = C.threshold(C.SinglePeak(), rng, w_dead=W_DEAD, **kw)["e_star"]
    out["G0a_single_peak"] = dict(analytic=an, mc=mc, rel_err=abs(mc / an - 1), passes=bool(abs(mc / an - 1) <= 0.02))
    # G0b mesa: 10 fully neutral sites, the rest lethal: (1-u)^34 = w_dead
    an = brentq(lambda e: (1 - C.change_prob(e)) ** (C.NS - 10) - W_DEAD, 1e-4, 0.4)
    mc = C.threshold(C.SinglePeak(neutral=range(10)), rng, w_dead=W_DEAD, **kw)["e_star"]
    out["G0b_mesa"] = dict(analytic=an, mc=mc, rel_err=abs(mc / an - 1), passes=bool(abs(mc / an - 1) <= 0.02))
    # G0c site-independent, no killing, localized regime (e=0.02): exact Perron root
    Ss = np.zeros((C.NS, 4))
    r2 = np.random.default_rng(7)
    for i in range(C.NS):
        for b in range(4):
            if b != C.WT[i]:
                Ss[i, b] = -abs(r2.normal(1.5, 1.0))
    ex = C.site_independent_lambda(Ss, 0.02)
    lam, _, _, _ = C.lambda_at(C.SiteIndependent(Ss), 0.02, np.tile(C.WT, (PLANT["N"], 1)), rng, 0.0, k=1,
                               T=150, burn=75)
    out["G0c_site_independent"] = dict(exact=ex, mc=lam, rel_err=abs(lam / ex - 1), passes=bool(abs(lam / ex - 1) <= 0.05))

    # G1 data and the global-epistasis fit (landscape only)
    S, D, ns, nd = C.load_real()
    out["G1_data"] = dict(n_singles=ns, n_doubles=nd, wt_seq=C.WT_SEQ,
                          passes=(ns == 132 and nd == 8346 and len(C.WT_SEQ) == 44))
    fits = []
    for r in range(3):
        x0 = None
        if r > 0:
            base = C.fit_ge(S, D)["x"] if r == 1 else fits[0]["x"]
            x0 = base + np.random.default_rng(r).normal(0, 0.3, len(base))
        fits.append(C.fit_ge(S, D, x0=x0))
    best = min(fits, key=lambda f: f["cost"])
    rd, rs = best["resid_double"], best["resid_single"]
    yd = best["d_obs"]
    zd_fit = None
    muts, s_idx, s_y, d1, d2, dy = C.observations(S, D)
    a = best["x"][:len(muts)]
    zd = best["z0"] + a[d1] + a[d2]
    slope = (best["hi"] - best["lo"]) * expit(zd) * (1 - expit(zd))
    Fd = C.ge_predict(best, zd)
    info = Fd > -8
    out["G1_ge_fit"] = dict(
        lo=best["lo"], hi=best["hi"], z0=best["z0"], costs=[f["cost"] for f in fits],
        restart_spread_cost=float(np.ptp([f["cost"] for f in fits])),
        resid_sd_double=float(rd.std(ddof=1)), resid_sd_single=float(rs.std(ddof=1)),
        r2_double=float(1 - np.sum(rd ** 2) / np.sum((yd - yd.mean()) ** 2)),
        resid_sd_double_informative=float(rd[info].std(ddof=1)), n_informative=int(info.sum()),
        mean_slope_informative=float(slope[info].mean()), floor_obs=float(min(S.min(), np.nanmin(D))),
        latent_effects=a.tolist(), success=all(f["success"] for f in fits))
    # #30 isotonic curve (comparison only)
    x = np.array([S[i, bi] + S[j, bj] for (i, bi), (j, bj) in zip([muts[k] for k in d1], [muts[k] for k in d2])])
    g = C.E30.make_g(x, dy)
    rr = dy - g(x)
    out["G1_iso30"] = dict(resid_sd_double=float(rr.std(ddof=1)),
                           r2_double=float(1 - np.sum(rr ** 2) / np.sum((dy - dy.mean()) ** 2)))
    out["cpu_s"] = time.process_time() - t0
    out["passes"] = all(out[k]["passes"] for k in ("G0a_single_peak", "G0b_mesa", "G0c_site_independent", "G1_data"))
    jdump(out, "t18_gate.json")
    print(json.dumps({k: v for k, v in out.items() if k != "G1_ge_fit"}, indent=1, default=str))
    print(json.dumps({k: v for k, v in out["G1_ge_fit"].items() if k != "latent_effects"}, indent=1))


# ------------------------------------------------------------------ planted
def calib():
    with open(os.path.join(OUT, "t18_gate.json")) as fh:
        g = json.load(fh)
    return g["G1_ge_fit"]


def make_truth(family, rep, cal, mask_pairs):
    rng = np.random.default_rng([20261125, 18, 10 + FAMILIES[family], rep])
    muts = C.mutation_list()
    a = np.array(cal["latent_effects"])
    kappa = rng.uniform(0.5, 1.6)
    a_new = kappa * rng.permutation(a) + rng.normal(0, 0.2 * a.std(), len(a))
    A = np.zeros((C.NS, 4))
    for k, (i, b) in enumerate(muts):
        A[i, b] = a_new[k]
    r_d, r_s, slope = cal["resid_sd_double_informative"], cal["resid_sd_single"], cal["mean_slope_informative"]
    if family == "A":      # all residual as measurement noise, no epistasis beyond the global curve
        sdm_d, sdm_s, sd_pair, sd_h = r_d, r_s, 0.0, 0.0
    elif family == "B":    # residual split equally: noise, pair epistasis, higher-order random field
        sdm_d, sdm_s = r_d / np.sqrt(3), r_s / np.sqrt(3)
        sd_pair = sd_h = (r_d / np.sqrt(3)) / slope
    elif family == "C":    # stress: epistasis doubled
        sdm_d, sdm_s = r_d / np.sqrt(3), r_s / np.sqrt(3)
        sd_pair = sd_h = 2 * (r_d / np.sqrt(3)) / slope
    else:
        raise ValueError(family)
    E = np.zeros((C.NS * 4, C.NS * 4))
    if sd_pair > 0:
        idx = np.array([i * 4 + b for i, b in muts])
        vals = rng.normal(0, sd_pair, (len(idx), len(idx)))
        vals = np.triu(vals, 1)
        vals = vals + vals.T
        site = np.array([i for i, _ in muts])
        vals[site[:, None] == site[None, :]] = 0
        E[np.ix_(idx, idx)] = vals
    nu = float(np.exp(rng.uniform(np.log(0.5), np.log(2.0))))
    truth = C.TruthLandscape(A, E, sd_h, cal["lo"], cal["hi"], nu, seed=int(rng.integers(1 << 30)))
    # observations: all singles, doubles on the real measured mask, noise, floor censoring
    S_obs = np.zeros((C.NS, 4))
    G1 = np.tile(C.WT, (len(muts), 1))
    for k, (i, b) in enumerate(muts):
        G1[k, i] = b
    F1 = truth.logfit(G1) + rng.normal(0, sdm_s, len(muts))
    for k, (i, b) in enumerate(muts):
        S_obs[i, b] = max(F1[k], cal["floor_obs"])
    D_obs = np.full((C.NS, 4, C.NS, 4), np.nan)
    G2 = np.tile(C.WT, (len(mask_pairs), 1))
    for k, ((i, bi), (j, bj)) in enumerate(mask_pairs):
        G2[k, i], G2[k, j] = bi, bj
    F2 = np.maximum(truth.logfit(G2) + rng.normal(0, sdm_d, len(mask_pairs)), cal["floor_obs"])
    for k, ((i, bi), (j, bj)) in enumerate(mask_pairs):
        D_obs[i, bi, j, bj] = D_obs[j, bj, i, bi] = F2[k]
    params = dict(kappa=kappa, nu=nu, sdm_d=sdm_d, sdm_s=sdm_s, sd_pair=sd_pair, sd_h=sd_h)
    return truth, S_obs, D_obs, params, rng


def planted(family, start, n):
    cal = calib()
    S, D, _, _ = C.load_real()
    muts = C.mutation_list()
    mask_pairs = [((i, bi), (j, bj)) for (i, bi) in muts for (j, bj) in muts
                  if j > i and np.isfinite(D[i, bi, j, bj])]
    kw = {k: PLANT[k] for k in ("N", "k", "T0", "burn0", "T", "burn", "refine")}
    rows = []
    for rep in range(start, start + n):
        t0 = time.process_time()
        truth, S_obs, D_obs, params, rng = make_truth(family, rep, cal, mask_pairs)
        tr = C.threshold(truth, rng, w_dead=W_DEAD, **kw)
        row = dict(family=family, rep=rep, params=params, e_true=tr["e_star"], censored_true=tr["censored"],
                   true_points=[(p[0], p[1]) for p in tr["points"]])
        if tr["e_star"] is not None:
            ge = C.fit_ge(S_obs, D_obs)
            ml = C.MeasuredLandscape(S_obs, D_obs, "ge", ge=ge)
            fi = C.threshold(ml, rng, w_dead=W_DEAD, **kw)
            row.update(e_fit=fi["e_star"], censored_fit=fi["censored"],
                       rel_err=None if fi["e_star"] is None else fi["e_star"] / tr["e_star"] - 1,
                       ge_resid_sd_double=float(ge["resid_double"].std(ddof=1)))
            if family == "B":
                x = []
                yy = []
                for (i, bi), (j, bj) in mask_pairs:
                    x.append(S_obs[i, bi] + S_obs[j, bj])
                    yy.append(D_obs[i, bi, j, bj])
                iso = C.E30.make_g(np.array(x), np.array(yy))
                fi2 = C.threshold(C.MeasuredLandscape(S_obs, D_obs, "iso30", iso=iso), rng, w_dead=W_DEAD, **kw)
                row.update(e_fit_iso30=fi2["e_star"],
                           rel_err_iso30=None if fi2["e_star"] is None else fi2["e_star"] / tr["e_star"] - 1)
        row["cpu_s"] = time.process_time() - t0
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k not in ("true_points",)}, default=str), flush=True)
    jdump(dict(script_sha256=sha256(os.path.abspath(__file__)), core_sha256=sha256(os.path.join(C.HERE, "t18_core.py")),
               plant_settings=PLANT, rows=rows), f"t18_planted_{family}_{start}_{start + n}.json")


def planted_merge():
    rows = []
    for fn in sorted(glob.glob(os.path.join(OUT, "t18_planted_*_*_*.json"))):
        with open(fn) as fh:
            rows += json.load(fh)["rows"]
    summ = {}
    for fam in FAMILIES:
        rr = [r for r in rows if r["family"] == fam]
        valid = [r for r in rr if r["e_true"] is not None]
        errs = [r["rel_err"] for r in valid if r.get("rel_err") is not None]
        within = sum(abs(x) <= 0.20 for x in errs)
        s = dict(n_rows=len(rr), n_censored_true=len(rr) - len(valid), n_scored=len(valid),
                 n_fit_censored=sum(r.get("e_fit") is None for r in valid),
                 n_within_20pct=within, median_abs_rel_err=float(np.median(np.abs(errs))) if errs else None,
                 mean_rel_err=float(np.mean(errs)) if errs else None,
                 e_true_range=[min(r["e_true"] for r in valid), max(r["e_true"] for r in valid)] if valid else None)
        if fam == "B":
            e2 = [r["rel_err_iso30"] for r in valid if r.get("rel_err_iso30") is not None]
            s["iso30_n_within_20pct"] = sum(abs(x) <= 0.20 for x in e2)
            s["iso30_median_abs_rel_err"] = float(np.median(np.abs(e2))) if e2 else None
            s["iso30_mean_rel_err"] = float(np.mean(e2)) if e2 else None
        need = 16 if fam in ("A", "B") else None
        if need is not None:
            s["criterion"] = "at least 16 of the first 20 scored replicates within 20%"
            first = valid[:20]
            k = sum(1 for r in first if r.get("rel_err") is not None and abs(r["rel_err"]) <= 0.20)
            s["first20_within"] = k
            s["passes"] = bool(len(first) == 20 and k >= 16)
        summ[fam] = s
    out = dict(summary=summ, gate_passes=bool(summ.get("A", {}).get("passes") and summ.get("B", {}).get("passes")))
    jdump(out, "t18_planted.json")
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ real (sealed)
def sealed():
    me = sha256(os.path.abspath(__file__))
    core = sha256(os.path.join(C.HERE, "t18_core.py"))
    path = os.path.join(REPO, "docs", "prereg", "HASHES.txt")
    txt = open(path).read() if os.path.exists(path) else ""
    return (me in txt) and (core in txt)


REAL = dict(N=20000, k=5, T0=100, burn0=50, T=60, burn=20, refine=True)
REAL_VAR = dict(N=10000, k=5, T0=100, burn0=50, T=60, burn=20, refine=True)
B_BOOT = 30


def authors_fraction(land, e, rng, N=20000, T=150, burn=75):
    """The authors' Fig. S32B observable: share of the whole population (lump included) with rate >= 0.8."""
    lam, pop, Fpop, info = C.lambda_at(land, e, np.tile(C.WT, (N, 1)), rng, W_DEAD, k=5, T=T, burn=burn)
    if info.get("extinct") or lam <= W_DEAD:
        return 0.0
    x_lump = (info["mean_w"] - lam) / (lam - W_DEAD)
    return float(info["frac_w_ge_08"] / (1 + x_lump))


def real():
    if not sealed():
        sys.exit("refusing: t18_analysis.py and t18_core.py are not sealed in docs/prereg/HASHES.txt")
    t0 = time.process_time()
    S, D, _, _ = C.load_real()
    out = dict(script_sha256=sha256(os.path.abspath(__file__)), core_sha256=sha256(os.path.join(C.HERE, "t18_core.py")),
               e_meas=E_MEAS, w_dead=W_DEAD)
    rng = np.random.default_rng([20261125, 18, 99])

    # R0 reproduce the authors' Fig. S32B (their model: HD>=3 and unmeasured doubles at 0.01)
    au = C.MeasuredLandscape(S, D, "authors")
    r0 = {str(q): authors_fraction(au, 1 - q, rng) for q in (0.926, 0.941, 0.974)}
    out["R0_authors_S32B"] = dict(fractions=r0, passes=bool(r0["0.926"] < 0.01 and r0["0.941"] < 0.01
                                                             and 0.06 <= r0["0.974"] <= 0.24))
    jdump(out, "t18_real.json")

    # R1 primary
    fits = [C.fit_ge(S, D)]
    for r in (1, 2):
        fits.append(C.fit_ge(S, D, x0=fits[0]["x"] + np.random.default_rng(r).normal(0, 0.3, len(fits[0]["x"]))))
    ge = min(fits, key=lambda f: f["cost"])
    prim = C.MeasuredLandscape(S, D, "ge", ge=ge)
    th = C.threshold(prim, rng, w_dead=W_DEAD, **REAL)
    out["R1_primary"] = dict(e_star=th["e_star"], censored=th["censored"],
                             points=[(p[0], p[1]) for p in th["points"]], refine=th.get("refine", [None])[:2])
    lam_meas = C.lambda_profile(prim, rng, [E_MEAS], w_dead=W_DEAD, N=REAL["N"])[0]
    out["R3_lambda_at_e_meas"] = dict(primary=lam_meas, sigma_required=1 / lam_meas["lam"] if lam_meas["lam"] > 0 else None,
                                      single_peak_sigma=1 / (1 - C.change_prob(E_MEAS)) ** C.NS)
    jdump(out, "t18_real.json")

    # R2 residual bootstrap
    muts, s_idx, s_y, d1, d2, dy = C.observations(S, D)
    a = ge["x"][:len(muts)]
    fit_s = C.ge_predict(ge, ge["z0"] + a[s_idx])
    fit_d = C.ge_predict(ge, ge["z0"] + a[d1] + a[d2])
    rs, rd = s_y - fit_s, dy - fit_d
    floor = min(S.min(), np.nanmin(D))
    boots = []
    for b in range(B_BOOT):
        rb = np.random.default_rng([20261125, 18, 200, b])
        Sb = np.zeros_like(S)
        Db = np.full_like(D, np.nan)
        ys = np.maximum(fit_s + rb.choice(rs, len(rs)), floor)
        yd = np.maximum(fit_d + rb.choice(rd, len(rd)), floor)
        for k, (i, bb) in enumerate(muts):
            Sb[i, bb] = ys[k]
        for k in range(len(dy)):
            (i, bi), (j, bj) = muts[d1[k]], muts[d2[k]]
            Db[i, bi, j, bj] = Db[j, bj, i, bi] = yd[k]
        geb = C.fit_ge(Sb, Db, x0=ge["x"])
        tb = C.threshold(C.MeasuredLandscape(Sb, Db, "ge", ge=geb), rb, w_dead=W_DEAD, **REAL_VAR)
        boots.append(tb["e_star"] if tb["e_star"] is not None else tb["censored"])
        out["R2_bootstrap"] = dict(e_star=boots)
        jdump(out, "t18_real.json")
    num = np.array([x for x in boots if isinstance(x, float)])
    n_above = sum(1 for x in boots if x == "above_max")
    n_below = sum(1 for x in boots if x == "below_min")
    # censored draws are placed at the grid ends for the percentiles
    arr = np.concatenate([num, np.full(n_above, C.E_GRID[-1]), np.full(n_below, C.E_GRID[0])])
    lo_e, hi_e = np.percentile(arr, [2.5, 97.5])
    e1 = th["e_star"]
    R = (E_MEAS / e1) if e1 else None
    out["R2_bootstrap"].update(e_star_2p5=float(lo_e), e_star_97p5=float(hi_e), n_above=n_above, n_below=n_below,
                               R_point=R, R_lo=float(E_MEAS / hi_e), R_hi=float(E_MEAS / lo_e))

    # R4 variants (each re-estimates e*; fidelity only enters R)
    iso = C.E30.make_g(np.array([S[muts[i][0], muts[i][1]] + S[muts[j][0], muts[j][1]] for i, j in zip(d1, d2)]), dy)
    var = {}
    specs = {
        "V1_authors": (C.MeasuredLandscape(S, D, "authors"), {}),
        "V2_iso30": (C.MeasuredLandscape(S, D, "iso30", iso=iso), {}),
        "V3_additive": (C.MeasuredLandscape(S, D, "additive"), {}),
        "V4_ge_no_override": (C.MeasuredLandscape(S, D, "ge", ge=ge, use_measured=False), {}),
        "V5a_wdead_2^-10": (prim, dict(w_dead=2.0 ** -10)),
        "V5b_wdead_0.05": (prim, dict(w_dead=0.05)),
        "V6_transition_spectrum": (prim, dict(spectrum="transition")),
        "V7a_tau_0.5": (prim, dict(tau=0.5)),
        "V7b_tau_2": (prim, dict(tau=2.0)),
    }
    for name, (land, extra) in specs.items():
        kw = dict(REAL_VAR)
        wd = extra.get("w_dead", W_DEAD)
        tv = C.threshold(land, rng, w_dead=wd, tau=extra.get("tau", 1.0), spectrum=extra.get("spectrum", "uniform"), **kw)
        lv = C.lambda_profile(land, rng, [E_MEAS], w_dead=wd, N=REAL_VAR["N"], tau=extra.get("tau", 1.0),
                              spectrum=extra.get("spectrum", "uniform"))[0]
        var[name] = dict(e_star=tv["e_star"], censored=tv["censored"],
                         R=(E_MEAS / tv["e_star"]) if tv["e_star"] else None, lambda_at_e_meas=lv["lam"])
        out["R4_variants"] = var
        jdump(out, "t18_real.json")
    out["R4_fidelity_bracket"] = {str(q): ((1 - q) / e1 if e1 else None) for q in (0.926, 0.941, 1 - 0.109 ** (1 / 42))}

    # R5 verdict (prereg D7)
    if R is None:
        verdict = "not decidable (primary e* censored: %s)" % th["censored"]
    elif out["R2_bootstrap"]["R_hi"] < 1:
        verdict = "support"
    elif out["R2_bootstrap"]["R_lo"] > 1:
        verdict = "kill"
    else:
        verdict = "inconclusive"
    side = None if R is None else (R < 1)
    flips = [k for k, v in var.items() if v["R"] is not None and side is not None and (v["R"] < 1) != side]
    flips += [k for k, v in var.items() if v["R"] is None and v["censored"] == ("above_max" if not side else "below_min")]
    out["R5"] = dict(verdict=verdict, robust=(len(flips) == 0), variants_on_other_side=flips,
                     r0_reproduction_passes=out["R0_authors_S32B"]["passes"])
    out["cpu_s"] = time.process_time() - t0
    jdump(out, "t18_real.json")
    print(json.dumps(out["R5"], indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "gate":
        gate()
    elif mode == "planted":
        planted(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif mode == "planted_merge":
        planted_merge()
    elif mode == "real":
        real()
    else:
        sys.exit(f"unknown mode {mode}")
