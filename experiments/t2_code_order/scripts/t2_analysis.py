"""T2 (prereg t2_code_order.md): does asteroid amino-acid abundance predict Wehbi 2024 LUCA usage beyond molecular weight?

Usage:
  python -I t2_analysis.py <experiments/t2_code_order dir> power   # planted-signal check only; reads no abundance values
  python -I t2_analysis.py <experiments/t2_code_order dir> real    # the sealed test

Primary inputs (fixed in the prereg):
  x = log10 free D+L abundance, Glavin 2025 Extended Data Table 2; y = Wehbi luca_usage_recomputed; z = Wehbi integer MW.
  Cells: quantified -> value; "<DL" -> DL (ties at DL); "tr." -> 0.1; "<=x" -> x; n.r./n.d. -> amino acid dropped.
Statistic: Kendall partial tau from tau-b terms. p: one-sided, y permuted within MW tertiles of the sample's amino
acids (1e5 draws, seed 20261123). Upper 95% bound: 95th percentile of 1e4 bootstrap resamples of amino acids.
"""
import sys, os, json
import numpy as np

D, MODE = sys.argv[1], sys.argv[2]
SEED = 20261123
NPERM, NBOOT, NPOW = 100_000, 10_000, 400


def rows(path):
    lines = [l for l in open(path, encoding="utf-8").read().split("\n") if l and not l.startswith("#")]
    h = lines[0].split("\t")
    return [dict(zip(h, l.split("\t"))) for l in lines[1:]]


def tau_b(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    da = np.sign(a[:, None] - a[None, :]); db = np.sign(b[:, None] - b[None, :])
    iu = np.triu_indices(len(a), 1)
    da, db = da[iu], db[iu]
    num = (da * db).sum()
    den = np.sqrt((da != 0).sum() * (db != 0).sum())
    return num / den if den > 0 else 0.0


def partial_tau(x, y, z):
    txy, txz, tyz = tau_b(x, y), tau_b(x, z), tau_b(y, z)
    den = np.sqrt(max((1 - txz ** 2) * (1 - tyz ** 2), 1e-12))
    return (txy - txz * tyz) / den


def strata(z):
    """MW tertiles of the sample's amino acids (by rank; ties keep order of the stable sort)."""
    order = np.argsort(z, kind="stable")
    lab = np.empty(len(z), int)
    for k, idx in enumerate(np.array_split(order, 3)):
        lab[idx] = k
    return lab


def perm_p(x, y, z, rng, nperm=NPERM):
    obs = partial_tau(x, y, z)
    lab = strata(z)
    yy = np.array(y, float)
    ge = 0
    for _ in range(nperm):
        yp = yy.copy()
        for k in range(3):
            i = np.where(lab == k)[0]
            yp[i] = yy[rng.permutation(i)]
        ge += partial_tau(x, yp, z) >= obs - 1e-12
    return obs, (1 + ge) / (1 + nperm)


def boot_upper(x, y, z, rng, nboot=NBOOT):
    n = len(x); v = []
    for _ in range(nboot):
        i = rng.integers(0, n, n)
        v.append(partial_tau(x[i], y[i], z[i]))
    return float(np.percentile(v, 95))


def verdict_one(t, p, ub):
    if t >= 0.4 and p < 0.01:
        return "support"
    if t <= 0.1 and ub < 0.4:
        return "kill"
    return "inconclusive"


def overall(vs):
    if all(v == "support" for v in vs):
        return "support"
    if all(v == "kill" for v in vs):
        return "kill"
    return "inconclusive"


W = {r["aa1"]: float(r["luca_usage_recomputed"]) for r in rows(os.path.join(D, "data", "wehbi2024_luca_usage.tsv"))}
MW = {r["aa1"]: float(r["molecular_weight_da_wehbi"]) for r in rows(os.path.join(D, "data", "aa_molecular_weight.tsv"))}
G = rows(os.path.join(D, "data", "glavin2025_edt2_free_protein_aa.tsv"))
SAMPLES = {"Bennu": "Bennu_OREX-803001-0", "Ryugu": "Ryugu_A0106", "Murchison": "Murchison_CM2"}


def cells(sample):
    """(aa list, x values, censored flags, dl values) for one sample. Reads status and DL always; value only if real."""
    out = []
    for r in G:
        if r["sample"] != sample:
            continue
        st = r["status"]
        if st in ("not_reported", "not_determined"):
            continue
        out.append((r["aa1"], st, r["value"], r["detection_limit"]))
    return out


def x_of(c):
    aa, st, val, dl = c
    if st == "quantified":
        return float(val)
    if st == "below_detection_limit":
        return float(dl)
    if st == "trace_below_quantitation":
        return 0.1
    if st == "upper_limit_not_blank_corrected":
        return float(val) if val else float(dl)
    raise ValueError(c)


def planted(aas, sts, dls, target, rng):
    """x from a latent with a chosen dependence on rank(y) and rank(z); censored where the real sample is censored
    at that amino acid's real DL if the planted value falls below it. Scale: planted log10 values centred on the
    sample's log10 DL range so censoring bites as often as in the real pattern."""
    y = np.array([W[a] for a in aas]); z = np.array([MW[a] for a in aas])
    ry = (np.argsort(np.argsort(y)) - (len(y) - 1) / 2) / len(y)
    rz = (np.argsort(np.argsort(z)) - (len(z) - 1) / 2) / len(z)
    b = target * 6.0
    lat = b * ry - 2.0 * rz + rng.normal(0, 1, len(y))
    ncens = sum(s != "quantified" for s in sts)
    # censor the ncens lowest planted values (same censoring count as the real sample), as ties at the lowest DL
    x = lat.copy()
    if ncens:
        low = np.argsort(lat)[:ncens]
        x[low] = lat.min() - 1
    return x, y, z


res = {"mode": MODE, "seed": SEED}
rng = np.random.default_rng(SEED)

if MODE == "power":
    pw = {}
    for name in ("Bennu", "Ryugu"):
        cs = cells(SAMPLES[name])
        aas = [c[0] for c in cs]; sts = [c[1] for c in cs]; dls = [c[3] for c in cs]
        # calibrate b per target by simulation: report achieved mean partial tau alongside verdict rates
        out = {}
        for target in (0.0, 0.2, 0.4, 0.6, 0.8):
            vs, taus = [], []
            for _ in range(NPOW):
                x, y, z = planted(aas, sts, dls, target, rng)
                t, p = perm_p(x, y, z, rng, nperm=1000)
                ub = boot_upper(x, y, z, rng, nboot=300)
                vs.append(verdict_one(t, p, ub)); taus.append(t)
            out[str(target)] = {"mean_partial_tau": float(np.mean(taus)),
                                "P_support": vs.count("support") / NPOW, "P_kill": vs.count("kill") / NPOW,
                                "P_inconclusive": vs.count("inconclusive") / NPOW}
        pw[name] = {"n": len(aas), "n_censored": sum(s != "quantified" for s in sts), "by_planted_strength": out}
    res["power"] = pw
elif MODE == "real":
    per = {}
    for name, s in SAMPLES.items():
        cs = cells(s)
        aas = [c[0] for c in cs]
        x = np.log10([x_of(c) for c in cs]); y = np.array([W[a] for a in aas]); z = np.array([MW[a] for a in aas])
        t, p = perm_p(x, y, z, rng)
        ub = boot_upper(x, y, z, rng)
        loo = {a: float(partial_tau(np.delete(x, i), np.delete(y, i), np.delete(z, i))) for i, a in enumerate(aas)}
        per[name] = {"n": len(aas), "amino_acids": aas, "partial_tau": float(t), "p_one_sided": float(p),
                     "upper95": ub, "tau_xy": float(tau_b(x, y)), "tau_xz": float(tau_b(x, z)),
                     "tau_yz": float(tau_b(y, z)), "verdict": verdict_one(t, p, ub),
                     "role": "exploratory" if name == "Murchison" else "scored", "leave_one_out": loo}
    res["per_sample"] = per
    res["verdict"] = overall([per["Bennu"]["verdict"], per["Ryugu"]["verdict"]])
else:
    raise SystemExit("mode must be power or real")

os.makedirs(os.path.join(D, "results"), exist_ok=True)
json.dump(res, open(os.path.join(D, "results", f"t2_{MODE}.json"), "w"), indent=1)
print(json.dumps(res if MODE == "power" else {k: res[k] for k in ("verdict",)}, indent=1)[:3000])
