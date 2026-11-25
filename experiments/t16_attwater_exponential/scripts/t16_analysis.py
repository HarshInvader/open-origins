"""T16 (plan S7, docs/plans/next_studies_2026-11-24.md): is the ribozyme replication in Attwater et al.
2025 (Nat Chem, doi:10.1038/s41557-025-01830-y, PMC12226338) exponential?

Claim under test, Fig. 3e caption: "Dotted lines are exponential curves fitted up to four cycles (x):
FITC strand = e^0.38x, R2 = 0.997; Cy5 strand = e^0.20x, R2 = 0.984."

Usage (single process, single thread; run under nice -n 20 with OMP/OPENBLAS threads = 1), from the
repo root:
  python -I t16_analysis.py <experiments/t16_attwater_exponential dir> scatter   # replicate scatter only
  python -I t16_analysis.py <dir> gate                                           # power gate (synthetic)

Blinding: before a seal, only `scatter` touches the measured copy numbers, and it returns only
replicate deviations from each cycle's own replicate mean (and summaries of them). No cycle mean, no
growth law and no curve shape is computed, printed or saved. The `gate` mode uses only the scatter
summary and the published fitted rates (part of the claim).

Inputs: SD_Fig3e.xlsx from the Source Data Fig. 3 zip (raw/, gitignored). The xlsx is read as a zip of
XML with the standard library; nothing in it is executed.
"""
import hashlib
import json
import math
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t16_attwater_exponential/scripts/t16_analysis.py"
SEED = 20261125
XLSX = {"SD_Fig3e.xlsx": "bcb27ef4f1198086526ef6e2e49ea441cd3f18b29fbfa4ea89433871258a91ee"}
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
STRANDS = {"FITC": (3, [4, 5, 6]), "Cy5": (7, [8, 9, 10])}   # (mean row, dataset rows) in Sheet1
COLS = "DEFGHIJKL"                                          # 9 cycle columns; row 2 holds the cycle number
PUB_RATE = {"FITC": 0.38, "Cy5": 0.20}                      # published e^(kx) fits, cycles 0-4
LAWS = ["exp", "par", "lin"]
DAICC_SUP, DAICC_KILL = 6.0, 2.0


# ---------------------------------------------------------------- io
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def dump(name, obj):
    os.makedirs(os.path.join(D, "scripts_out"), exist_ok=True)
    with open(os.path.join(D, "scripts_out", name), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    print("wrote scripts_out/" + name, flush=True)


def read_sheet(fname):
    p = os.path.join(D, "raw", "xlsx", fname)
    if sha256(p) != XLSX[fname]:
        sys.exit("input hash mismatch: " + fname)
    z = zipfile.ZipFile(p)
    if sum(i.file_size for i in z.infolist()) > 2_000_000:
        sys.exit("xlsx too large when unpacked")
    ss = ["".join(si.itertext()) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
    sh = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    cells = {}
    for row in sh.find("m:sheetData", NS):
        for c in row:
            v = c.find("m:v", NS)
            if v is None:
                continue
            cells[c.get("r")] = ss[int(v.text)] if c.get("t") == "s" else float(v.text)
    return cells


def load_fig3e():
    """Return cycles (9,) and {strand: (mean_row (9,), reps (3, 9))}. Callers decide what they may see."""
    c = read_sheet("SD_Fig3e.xlsx")
    assert c["C3"] == "Mean" and c["C7"] == "Mean" and c["B3"] == "FITC Strand" and c["B7"] == "Cy5 Strand"
    for mr, rr in STRANDS.values():
        assert [c["C%d" % r] for r in rr] == ["Dataset 1", "Dataset 2", "Dataset 3"]
    cyc = np.array([c[k + "2"] for k in COLS])
    out = {}
    for s, (mr, rr) in STRANDS.items():
        out[s] = (np.array([c["%s%d" % (k, mr)] for k in COLS]),
                  np.array([[c["%s%d" % (k, r)] for k in COLS] for r in rr]))
    return cyc, out


# ---------------------------------------------------------------- scatter (the only pre-seal data read)
def scatter():
    cyc, data = load_fig3e()
    res = {"cycles": cyc.tolist(), "strands": {}}
    for s, (mean_row, reps) in data.items():
        nonpos = int((reps <= 0).sum())
        # consistency of the deposited Mean row with the replicate average (difference only)
        mean_check = float(np.max(np.abs(mean_row - reps.mean(0)) / np.maximum(np.abs(reps.mean(0)), 1e-12)))
        lr = np.log(np.where(reps > 0, reps, np.nan))
        dev_log = lr - np.nanmean(lr, 0)          # deviation from each cycle's own replicate mean (log)
        r = {"nonpositive_values": nonpos, "mean_row_vs_rep_avg_max_rel_diff": mean_check}
        # Only pooled log-scale SDs are read. Linear-scale SDs and per-cycle SDs are NOT computed: under
        # additive noise their pattern across cycles would reveal the growth curve.
        for name, cols in (("c1_4", [1, 2, 3, 4]), ("c1_8", list(range(1, 9)))):
            dl = dev_log[:, cols]
            df = 2 * len(cols)
            r["pooled_log_sd_" + name] = float(math.sqrt(np.nansum(dl ** 2) / df))
            r["df_" + name] = df
            # dataset (reaction) effect: share of deviation variance carried by a per-dataset constant
            ds = dl.mean(1)
            r["dataset_effect_share_" + name] = float(len(cols) * np.sum(ds ** 2) / np.nansum(dl ** 2))
            # two-way residual (deviation minus its dataset constant): within-reaction scatter
            tw = dl - ds[:, None]
            dfw = 2 * (len(cols) - 1)
            r["within_log_sd_" + name] = float(math.sqrt(np.sum(tw ** 2) / dfw))
            r["df_within_" + name] = dfw
            r["dataset_offset_sd_" + name] = float(math.sqrt(np.sum(ds ** 2) / 2))
            # does the dataset deviation grow with cycle (rate-like) or stay constant (offset-like)?
            xc = np.array(cols, float) - np.mean(cols)
            sl = tw @ xc / (xc @ xc)
            tot = np.sum(dl ** 2)
            r["ss_share_" + name] = {"dataset_constant": float(len(cols) * np.sum(ds ** 2) / tot),
                                     "dataset_slope": float(np.sum(sl ** 2) * (xc @ xc) / tot),
                                     "residual": float(np.sum((tw - sl[:, None] * xc[None, :]) ** 2) / tot)}
        r["cycle0_max_abs_log_dev"] = float(np.nanmax(np.abs(dev_log[:, 0])))
        # what is the deposited Mean row? (differences only)
        gm = np.exp(lr.mean(0))
        r["mean_row_vs_geomean_max_rel_diff"] = float(np.max(np.abs(mean_row - gm) / gm))
        r["mean_row_vs_median_max_rel_diff"] = float(np.max(np.abs(mean_row - np.median(reps, 0))
                                                            / np.median(reps, 0)))
        res["strands"][s] = r
    dump("t16_scatter.json", res)
    print(json.dumps(res, indent=1))


# ---------------------------------------------------------------- growth laws
# every law is y = a * h(r x), with a > 0, r >= 0:
#   exp: h = e^u          (dy/dx = r y)
#   par: h = (1 + u)^2    (dy/dx = 2 r sqrt(a) sqrt(y); von Kiedrowski square-root law)
#   lin: h = 1 + u        (dy/dx = r a)
def hfun(law, u):
    if law == "exp":
        return np.exp(u)
    if law == "par":
        return (1.0 + u) ** 2
    return 1.0 + u


def rate_for(law, A, xe):
    """rate r such that h(r xe) = A (curve from 1 at x=0 to A at x=xe)."""
    if law == "exp":
        return math.log(A) / xe
    if law == "par":
        return (math.sqrt(A) - 1.0) / xe
    return (A - 1.0) / xe


R_GRID = {law: np.concatenate([[0.0], np.geomspace(1e-3, 50.0, 700)]) for law in LAWS}


FORMS = ["pooled", "fe", "anchored"]
#   pooled    replicate-level fit, one free intercept, every cycle in the design (cycle 0 included);
#             the plan's literal "replicate-level fits over cycles 0 to 4".
#   fe        one free intercept per reaction (Dataset 1-3), cycles >= 1 (cycle 0 is 1 by definition
#             in every reaction and carries no measurement); shape comes from within-reaction change.
#   anchored  no intercept: y(0) = 1 fixed (the authors' e^(kx) form), cycles >= 1, pooled.


def design_obs(x_cyc, nrep, form):
    keep = x_cyc >= (1 if form in ("fe", "anchored") else 0)
    return x_cyc[keep], keep


def fit_rss(law, x_cyc, Zr, form, cap=False):
    """Least squares on log y. Zr: (nsim, nrep, ncyc_kept) log copy numbers at cycles x_cyc (kept).
    Model: log y = c(+c_d) + log h(r x') with x' = min(x, xb) if cap (plateau after breakpoint xb,
    profiled on a 0.25-cycle grid). anchored: c = -log h(0) = 0. Returns RSS per sim (profiled over r)."""
    rg = R_GRID[law]
    nsim, nrep, nc = Zr.shape
    xbs = np.arange(1.0, x_cyc.max() + 1e-9, 0.25) if cap else [None]
    if form == "pooled":
        Z = Zr.reshape(nsim, -1)
        Zc = Z - Z.mean(1, keepdims=True)
    elif form == "fe":
        Zc = (Zr - Zr.mean(2, keepdims=True)).reshape(nsim, -1)
    else:
        Zc = Zr.reshape(nsim, -1)
    zz = (Zc ** 2).sum(1)
    best = np.full(nsim, np.inf)
    for xb in xbs:
        xx = x_cyc if xb is None else np.minimum(x_cyc, xb)
        G = np.log(hfun(law, rg[:, None] * xx[None, :]))             # (nr, nc); log h(0) = 0
        if form == "pooled":
            Gt = np.tile(G, nrep)
            Gc = Gt - Gt.mean(1, keepdims=True)
        elif form == "fe":
            Gc = np.tile(G - G.mean(1, keepdims=True), nrep)
        else:
            Gc = np.tile(G, nrep)
        rss = zz[:, None] - 2 * Zc @ Gc.T + (Gc ** 2).sum(1)[None, :]
        best = np.minimum(best, rss.min(1))
    return np.maximum(best, 1e-300)


def daicc(x_cyc, Y, form, cap=False):
    """Delta AICc of par and lin against exp (positive favours exp). Y: (nsim, nrep, ncyc) copy numbers.
    Within a form every law has the same parameter count, so Delta AICc = n ln(RSS_alt / RSS_exp)."""
    xk, keep = design_obs(x_cyc, Y.shape[1], form)
    Zr = np.log(Y[:, :, keep])
    n = Zr.shape[1] * Zr.shape[2]
    rss = {law: fit_rss(law, xk, Zr, form, cap) for law in LAWS}
    return {alt: n * np.log(rss[alt] / rss["exp"]) for alt in ("par", "lin")}, rss, n


def simulate(law, A, x_cyc, nrep, nsim, rng, su, sv, se, plateau_after=None):
    """Copy numbers (nsim, nrep, ncyc). True curve h(r x) from 1 at x=0 to A at x=4 (flat after
    plateau_after). Cycle 0 is exactly 1 (as deposited). For x >= 1, log-scale noise has the observed
    structure: per-reaction offset u_d ~ N(0, su^2), per-reaction slope v_d ~ N(0, sv^2) on centred
    cycle, independent e ~ N(0, se^2)."""
    r = rate_for(law, A, 4.0)
    xx = x_cyc if plateau_after is None else np.minimum(x_cyc, plateau_after)
    logf = np.log(hfun(law, r * xx))
    pos = x_cyc >= 1
    xc = x_cyc - x_cyc[pos].mean()
    u = rng.standard_normal((nsim, nrep, 1)) * su
    v = rng.standard_normal((nsim, nrep, 1)) * sv
    e = rng.standard_normal((nsim, nrep, x_cyc.size)) * se
    noise = (u + v * xc[None, None, :] + e) * pos[None, None, :]
    return np.exp(logf[None, None, :] + noise)


def verdict_strand(d):
    m = np.minimum(d["par"], d["lin"])
    return {"support": m >= DAICC_SUP, "kill": m < DAICC_KILL}


def noise_params(st, key):
    """(su, sv, se) and their 80% upper bounds from the scatter summary (deviations only)."""
    from scipy.stats import chi2
    cols = [1, 2, 3, 4] if key == "c1_4" else list(range(1, 9))
    xc = np.array(cols, float) - np.mean(cols)
    sxx = float(xc @ xc)
    tot = st["pooled_log_sd_" + key] ** 2 * st["df_" + key]
    sh = st["ss_share_" + key]
    df_e = 3 * len(cols) - len(cols) - 2 - 2
    su = st["dataset_offset_sd_" + key]
    sv = math.sqrt(sh["dataset_slope"] * tot / sxx / 2)
    se = math.sqrt(sh["residual"] * tot / df_e)
    up = lambda s, df: s * math.sqrt(df / chi2.ppf(0.20, df))
    return {"obs": (su, sv, se), "hi80": (up(su, 2), up(sv, 2), up(se, df_e)),
            "df": {"u": 2, "v": 2, "e": df_e}, "sxx": sxx}


AMPS = [1.5, 2.0, 2.23, 3.0, 3.5, 4.57, 7.0, 10.0]
DESIGNS = [("c0_4", np.arange(5.0), False, None, "c1_4"),
           ("c0_8_plateau", np.arange(9.0), True, 4.0, "c1_8")]


def gate():
    sc = json.load(open(os.path.join(D, "scripts_out", "t16_scatter.json")))
    nsim = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
    out = {"nsim": nsim, "seed": [SEED, 1],
           "rules": {"support": "min(dAICc_par, dAICc_lin) >= 6 (per strand; study needs both strands)",
                     "kill": "min(dAICc_par, dAICc_lin) < 2 (per strand; study needs both strands)"},
           "noise": {}, "cells": []}
    for s in ("FITC", "Cy5"):
        st = sc["strands"][s]
        for dname, xc, cap, pa, key in DESIGNS:
            npar = noise_params(st, key)
            out["noise"]["%s/%s" % (s, dname)] = npar
            for gname in ("obs", "hi80"):
                su, sv, se = npar[gname]
                for A in AMPS:
                    for law in LAWS:
                        rng = np.random.default_rng([SEED, 1, len(out["cells"])])
                        Y = simulate(law, A, xc, 3, nsim, rng, su, sv, se, pa)
                        for form in FORMS:
                            d, _, n = daicc(xc, Y, form, cap)
                            v = verdict_strand(d)
                            out["cells"].append({"strand": s, "design": dname, "noise": gname, "A": A,
                                                 "true": law, "form": form, "n_obs": n,
                                                 "p_support": float(v["support"].mean()),
                                                 "p_kill": float(v["kill"].mean()),
                                                 "median_dpar": float(np.median(d["par"])),
                                                 "median_dlin": float(np.median(d["lin"]))})
                print(s, dname, gname, flush=True)
    dump("t16_gate.json", out)


if __name__ == "__main__":
    if MODE == "scatter":
        scatter()
    elif MODE == "gate":
        gate()
    else:
        sys.exit("unknown mode " + MODE)
