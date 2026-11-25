"""T18b: QT45 error threshold with measured pair epistasis kept (empirical Bayes) for HD >= 3 genotypes.

Modes (run from experiments/, single-threaded, low priority):
  gate                          noise model from the replicate counts, count-to-CSV reproduction, layouts (no
                                fitness model of the real landscape beyond T18's gate fit)
  planted <family> <start> <n>  planted kill test, families A B C D E F (and stress S)
  planted_merge                 apply the planted criterion (prereg P3) to all parts
  real                          refuses unless docs/prereg/HASHES.txt names this file and t18b_core.py (not written:
                                T18b's real run is specified in the prereg and is added only after a planted pass)

Prereg: docs/prereg/t18b_qt45_pair_epistasis.md.
"""
import glob
import hashlib
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t18_core as C  # noqa: E402
import t18b_core as B  # noqa: E402

OUT = os.path.join(C.STUDY, "scripts_out")
W_DEAD = 0.01
PLANT = dict(N=5000, k=5, T0=60, burn0=30, T=40, burn=15, refine=False)
M_DRAWS = 2                 # posterior draws per planted replicate (prereg D5)
FAMILIES = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "S": 6}
SEQ_ERR = 1e-3              # per-nucleotide read error used to contaminate planted triple counts (prereg P2)
TRIPLE_MIN_IN = 10
TRIPLE_FLAG = 1.0           # |log2(Phi_obs / Phi_model)| above this flags the model (prereg D9)


def jdump(obj, name):
    with open(os.path.join(OUT, name), "w") as fh:
        json.dump(obj, fh, separators=(",", ":"), default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def hashes():
    return dict(analysis=sha256(os.path.abspath(__file__)), core=sha256(os.path.join(C.HERE, "t18b_core.py")),
                t18_core=sha256(os.path.join(C.HERE, "t18_core.py")))


# ------------------------------------------------------------------ gate
def gate():
    t0 = time.process_time()
    cnt, tot = B.load_counts_hd012()
    S, D, ns, nd = C.load_real()
    # G1b: our pooled fitness from the streamed counts reproduces the deposited CSV values
    diffs, n_cmp = [], 0
    for (i, b) in C.mutation_list():
        f = B.pooled_fitness(cnt, tot, ((i, b),))
        if f is not None:
            diffs.append(abs(f - S[i, b]))
            n_cmp += 1
    muts = C.mutation_list()
    for (i, bi) in muts:
        for (j, bj) in muts:
            if j <= i or not np.isfinite(D[i, bi, j, bj]):
                continue
            f = B.pooled_fitness(cnt, tot, ((i, bi), (j, bj)))
            if f is not None:
                diffs.append(abs(f - D[i, bi, j, bj]))
                n_cmp += 1
    nm = B.noise_model(cnt, tot)
    I1, I2 = B.input_layout(cnt)
    # noise on the real measured values (from the model at the observed F)
    sd_s = B.sigma_pooled(S[S != 0], I1[S != 0], nm)
    md = np.isfinite(D)
    sd_d = B.sigma_pooled(D[md], I2[md], nm)
    Dm = D[md]
    info = Dm > -8
    # unmeasured doubles: why are they missing?
    unm_in, unm_zero_out = 0, 0
    for (i, bi) in muts:
        for (j, bj) in muts:
            if j <= i or np.isfinite(D[i, bi, j, bj]):
                continue
            c = cnt.get(((i, bi), (j, bj)), {})
            if c.get("in_nodel", 0) >= 10:
                unm_in += 1
                if sum(c.get(L, 0) for L in B.LIBS_OUT) == 0:
                    unm_zero_out += 1
    Gt, It = B.load_triple_layout(TRIPLE_MIN_IN)
    Gt3, It3 = B.load_triple_layout(3)
    out = dict(hashes=hashes(),
               G1b_count_reproduction=dict(n_compared=n_cmp, max_abs_diff=float(max(diffs)),
                                           passes=bool(n_cmp == ns + nd and max(diffs) < 1e-6)),
               noise_model=nm,
               noise_sd_singles=dict(median=float(np.median(sd_s)), mean_var=float(np.mean(sd_s ** 2))),
               noise_sd_doubles=dict(median=float(np.median(sd_d)), q10=float(np.quantile(sd_d, .1)),
                                     q90=float(np.quantile(sd_d, .9)),
                                     mean_var_informative=float(np.mean(sd_d[info] ** 2)) / 1.0),
               input_counts=dict(singles_median=float(np.median(I1[S != 0])), doubles_median=float(np.median(I2[md])),
                                 doubles_q10=float(np.quantile(I2[md], .1))),
               unmeasured_doubles=dict(n=int(8514 - nd), with_input_ge10=unm_in, of_which_zero_output=unm_zero_out),
               triple_layout=dict(n_input_ge10=int(len(It)), n_input_ge3=int(len(It3)),
                                  input_sum_ge10=float(It.sum()), input_median_ge10=float(np.median(It)) if len(It) else None),
               cpu_s=time.process_time() - t0)
    jdump(out, "t18b_gate.json")
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------ planted
def calib():
    with open(os.path.join(OUT, "t18_gate.json")) as fh:
        g = json.load(fh)["G1_ge_fit"]
    with open(os.path.join(OUT, "t18b_gate.json")) as fh:
        gb = json.load(fh)
    return g, gb


def family_spec(family, cal):
    """Prereg P1. Epistasis magnitudes in latent units; s0 = T18 family B's pair/higher-order sd."""
    s0 = (cal["resid_sd_double_informative"] / np.sqrt(3)) / cal["mean_slope_informative"]
    spec = dict(noise_mult=1.0, sd_pair=0.0, p_neg=0.5, sd_h=0.0, cliff=None)
    if family == "A":
        pass
    elif family == "B":
        spec.update(sd_pair=s0, sd_h=s0)
    elif family == "C":
        spec.update(sd_pair=s0, sd_h=s0, p_neg=0.85)
    elif family == "D":
        spec.update(sd_pair=s0, sd_h=s0, p_neg=0.15)
    elif family == "E":
        spec.update(sd_h=np.sqrt(2) * s0)
    elif family == "F":
        spec.update(sd_pair=s0, sd_h=s0, cliff=(np.log2(0.01), 0.5))
    elif family == "S":     # stress (reported only): noise 1.5x larger than the method's noise model says
        spec.update(sd_pair=s0, sd_h=s0, noise_mult=1.5)
    else:
        raise ValueError(family)
    spec["s0"] = float(s0)
    return spec


def make_truth(family, rep, cal, gb, mask_pairs, I1, I2):
    rng = np.random.default_rng([20261125, 181, 10 + FAMILIES[family], rep])
    spec = family_spec(family, cal)
    muts = C.mutation_list()
    a = np.array(cal["latent_effects"])
    kappa = rng.uniform(0.5, 1.6)
    a_new = kappa * rng.permutation(a) + rng.normal(0, 0.2 * a.std(), len(a))
    A = np.zeros((C.NS, 4))
    for k, (i, b) in enumerate(muts):
        A[i, b] = a_new[k]
    E = np.zeros((C.NS * 4, C.NS * 4))
    if spec["sd_pair"] > 0:
        idx = np.array([i * 4 + b for i, b in muts])
        mag = np.abs(rng.normal(0, spec["sd_pair"], (len(idx), len(idx))))
        sign = np.where(rng.random((len(idx), len(idx))) < spec["p_neg"], -1.0, 1.0)
        vals = np.triu(mag * sign, 1)
        vals = vals + vals.T
        site = np.array([i for i, _ in muts])
        vals[site[:, None] == site[None, :]] = 0
        E[np.ix_(idx, idx)] = vals
    nu = float(np.exp(rng.uniform(np.log(0.5), np.log(2.0))))
    truth = B.Truth(A, E, spec["sd_h"], cal["lo"], cal["hi"], nu, seed=int(rng.integers(1 << 30)), cliff=spec["cliff"])
    nm = gb["noise_model"]
    floor = cal["floor_obs"]
    # observations on the real layout: all singles, doubles on the real mask, heteroscedastic replicate noise
    G1 = np.tile(C.WT, (len(muts), 1))
    for k, (i, b) in enumerate(muts):
        G1[k, i] = b
    F1t = truth.logfit(G1)
    i1 = np.array([I1[i, b] for i, b in muts])
    F1 = np.maximum(F1t + spec["noise_mult"] * B.sigma_pooled(F1t, i1, nm) * rng.standard_normal(len(muts)), floor)
    S_obs = np.zeros((C.NS, 4))
    for k, (i, b) in enumerate(muts):
        S_obs[i, b] = F1[k]
    G2 = np.tile(C.WT, (len(mask_pairs), 1))
    i2 = np.zeros(len(mask_pairs))
    for k, ((i, bi), (j, bj)) in enumerate(mask_pairs):
        G2[k, i], G2[k, j] = bi, bj
        i2[k] = I2[i, bi, j, bj]
    F2t = truth.logfit(G2)
    F2 = np.maximum(F2t + spec["noise_mult"] * B.sigma_pooled(F2t, i2, nm) * rng.standard_normal(len(mask_pairs)), floor)
    D_obs = np.full((C.NS, 4, C.NS, 4), np.nan)
    for k, ((i, bi), (j, bj)) in enumerate(mask_pairs):
        D_obs[i, bi, j, bj] = D_obs[j, bj, i, bi] = F2[k]
    params = dict(kappa=kappa, nu=nu, **{k: v for k, v in spec.items() if k != "cliff"},
                  cliff=None if spec["cliff"] is None else list(spec["cliff"]))
    return truth, S_obs, D_obs, params, rng, (F2t, F2, i2)


def planted_triples(truth, Gt, It, I2, nm, rng):
    """Simulated pooled triple counts on the real triple input layout, with read-error contamination from the
    three parent doubles (prereg P2). Returns observed aggregate Phi_obs."""
    c = nm["c_wt"]
    a = nm["a"]
    Ft = truth.logfit(Gt)
    iota = It * np.exp(np.sqrt(a / It) * rng.standard_normal(len(It)))   # true input abundance
    mu = iota * c * np.exp2(Ft)
    # contamination: each parent double contributes (its expected output) * SEQ_ERR/3 reads
    diff = Gt != C.WT
    sites = np.argsort(~diff, axis=1, kind="stable")[:, :3]
    cont = np.zeros(len(Gt))
    for drop in range(3):
        keep = [x for x in range(3) if x != drop]
        Gp = Gt.copy()
        Gp[np.arange(len(Gt)), sites[:, drop]] = C.WT[sites[:, drop]]
        s1, s2 = sites[:, keep[0]], sites[:, keep[1]]
        ip = I2[s1, Gt[np.arange(len(Gt)), s1], s2, Gt[np.arange(len(Gt)), s2]]
        cont += ip * c * np.exp2(truth.logfit(Gp)) * SEQ_ERR / 3
    lam = mu + cont
    kshape = np.maximum(lam / max(a - 1, 1e-9), 1e-6)
    o = rng.poisson(lam * rng.gamma(kshape, 1 / kshape)) if a > 1 else rng.poisson(lam)
    return float(o.sum() / (c * It.sum()))


def triple_stat(land, Gt, It, phi_obs):
    Fm = land.logfit(Gt)
    phi_mod = float(np.sum(It * np.exp2(Fm)) / It.sum())
    return float(np.log2(phi_obs / phi_mod)) if phi_obs > 0 else -np.inf, phi_mod


def planted(family, start, n):
    cal, gb = calib()
    nm = gb["noise_model"]
    S, D, _, _ = C.load_real()
    cnt, _ = B.load_counts_hd012()
    I1, I2 = B.input_layout(cnt)
    Gt, It = B.load_triple_layout(TRIPLE_MIN_IN)
    muts = C.mutation_list()
    mask_pairs = [((i, bi), (j, bj)) for (i, bi) in muts for (j, bj) in muts
                  if j > i and np.isfinite(D[i, bi, j, bj])]
    kw = {k: PLANT[k] for k in ("N", "k", "T0", "burn0", "T", "burn", "refine")}
    rows = []
    for rep in range(start, start + n):
        # runtime-only checkpointing: one json per replicate, skipped if already written (seeds are per index)
        rep_path = os.path.join(OUT, f"t18b_planted_rep_{family}_{rep:02d}.json")
        if os.path.exists(rep_path):
            print(f"skip {family} {rep}: {os.path.basename(rep_path)} exists", flush=True)
            continue
        print(f"start {family} {rep}", flush=True)
        t0 = time.process_time()
        truth, S_obs, D_obs, params, rng, (F2t, F2, i2) = make_truth(family, rep, cal, gb, mask_pairs, I1, I2)
        tr = C.threshold(truth, rng, w_dead=W_DEAD, **kw)
        row = dict(family=family, rep=rep, params=params, e_true=tr["e_star"], censored_true=tr["censored"])
        if tr["e_star"] is not None:
            ge = C.fit_ge(S_obs, D_obs)
            sigD = np.full_like(D_obs, np.nan)
            md = np.isfinite(D_obs)
            sigD[md] = B.sigma_pooled(D_obs[md], I2[md], nm)
            pf = B.fit_pairs(ge, S_obs, D_obs, sigD)
            draws = []
            for m in range(M_DRAWS):
                land = B.PairLandscape(S_obs, D_obs, ge, B.pair_matrix(pf, draw_rng=rng))
                th = C.threshold(land, rng, w_dead=W_DEAD, **kw)
                draws.append(th["e_star"] if th["e_star"] is not None else th["censored"])
            num = [x for x in draws if isinstance(x, float)]
            e_fit = float(np.mean(num)) if len(num) == M_DRAWS else None
            land_mode = B.PairLandscape(S_obs, D_obs, ge, B.pair_matrix(pf))
            th_mode = C.threshold(land_mode, rng, w_dead=W_DEAD, **kw)
            phi_obs = planted_triples(truth, Gt, It, I2, nm, rng)
            T, phi_mod = triple_stat(land_mode, Gt, It, phi_obs)
            rd = ge["resid_double"]
            info = ge["fitted_double"] > -8
            row.update(e_fit=e_fit, e_fit_draws=draws, rel_err=None if e_fit is None else e_fit / tr["e_star"] - 1,
                       e_fit_mode=th_mode["e_star"],
                       rel_err_mode=None if th_mode["e_star"] is None else th_mode["e_star"] / tr["e_star"] - 1,
                       tau=pf["tau"], tau_true_pair=params["sd_pair"], mean_shrink_inf=pf["mean_shrink_informative"],
                       resid_sd_double_inf=float(rd[info].std(ddof=1)),
                       triple_T=T, triple_phi_obs=phi_obs, triple_phi_mod=phi_mod,
                       triple_flag=bool(abs(T) > TRIPLE_FLAG))
        row["cpu_s"] = time.process_time() - t0
        rows.append(row)
        print(json.dumps(row, default=str), flush=True)
        tmp = rep_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(dict(hashes=hashes(), plant_settings=PLANT, m_draws=M_DRAWS, rows=[row]), fh,
                      separators=(",", ":"), default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
        os.replace(tmp, rep_path)


def success(r):
    """Prereg P3: one replicate's outcome."""
    if r["e_true"] is None:
        return None
    within = r.get("rel_err") is not None and abs(r["rel_err"]) <= 0.20
    if r["family"] == "F":
        return bool(within or r["triple_flag"])
    return bool(within and not r["triple_flag"])


def planted_merge():
    rows = []
    for fn in sorted(glob.glob(os.path.join(OUT, "t18b_planted_rep_*_*.json"))):
        with open(fn) as fh:
            rows += json.load(fh)["rows"]
    summ = {}
    for fam in FAMILIES:
        rr = sorted([r for r in rows if r["family"] == fam], key=lambda r: r["rep"])
        valid = [r for r in rr if r["e_true"] is not None]
        errs = [r["rel_err"] for r in valid if r.get("rel_err") is not None]
        em = [r["rel_err_mode"] for r in valid if r.get("rel_err_mode") is not None]
        first = valid[:20]
        ok = [success(r) for r in first]
        s = dict(n_rows=len(rr), n_censored_true=len(rr) - len(valid), n_scored=len(valid),
                 n_within_20pct=int(sum(abs(x) <= 0.2 for x in errs)),
                 n_fit_censored=sum(r.get("e_fit") is None for r in valid),
                 median_abs_rel_err=float(np.median(np.abs(errs))) if errs else None,
                 median_rel_err=float(np.median(errs)) if errs else None,
                 mean_rel_err=float(np.mean(errs)) if errs else None,
                 mode_median_rel_err=float(np.median(em)) if em else None,
                 mode_n_within_20pct=int(sum(abs(x) <= 0.2 for x in em)),
                 n_triple_flag=int(sum(r["triple_flag"] for r in valid)),
                 median_triple_T=float(np.median([r["triple_T"] for r in valid])) if valid else None,
                 median_tau=float(np.median([r["tau"] for r in valid])) if valid else None,
                 e_true_range=[min(r["e_true"] for r in valid), max(r["e_true"] for r in valid)] if valid else None,
                 first20_success=int(sum(ok)), first20_n=len(first),
                 misses_so_far=int(sum(1 for x in ok if not x)))
        if fam != "S":
            s["passes"] = bool(len(first) == 20 and sum(ok) >= 16)
            s["already_failed"] = bool(s["misses_so_far"] > 4)
        summ[fam] = s
    req = [f for f in FAMILIES if f != "S"]
    out = dict(summary=summ, gate_passes=all(summ[f].get("passes") for f in req),
               gate_failed=any(summ[f].get("already_failed") for f in req))
    jdump(out, "t18b_planted.json")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "gate":
        gate()
    elif mode == "planted":
        planted(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif mode == "planted_merge":
        planted_merge()
    elif mode == "real":
        sys.exit("refusing: T18b real mode is not written until the planted kill test passes (prereg R)")
    else:
        sys.exit(f"unknown mode {mode}")
