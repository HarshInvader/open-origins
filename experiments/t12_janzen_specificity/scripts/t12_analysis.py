"""T12 (prereg docs/prereg/t12_janzen_specificity.md): does ribozyme specificity really rise with activity in
Janzen et al. 2022 (Nat Commun, doi:10.1038/s41467-022-31387-0), or is it the background floor?

Usage (single process, single thread; run under nice):
  python -I t12_analysis.py <experiments/t12_janzen_specificity dir> gate       # checks + the paper's own Table 1
  python -I t12_analysis.py <dir> planted [NREP]                               # synthetic profiles only
  python -I t12_analysis.py <dir> sealcheck                                    # says whether `real` would run
  python -I t12_analysis.py <dir> dryrun                                       # `real` code, activity permuted
  python -I t12_analysis.py <dir> real                                         # sealed test; refuses without seal

Inputs: TSVs written by scripts/xlsx_to_tsv.py from Source Data (MOESM3) into cache/sd/ (gitignored).

Definitions (paper, Results; authors' BackgroundNormalizer.py / PromIndexPlot.py):
  r_s,i      catalytic enhancement = bootstrap-median k*A / background k0A0 (sheet "Figure 2", r_<sub>)
  all_sum_s  sum over the six substrates of r_s,i (the paper's "total activity")
  I_s        promiscuity index = normalised Shannon entropy of r_s,i / all_sum_s (log base cancels)
  Table 1    Pearson and Spearman of (all_sum, I) over all 1,954 sequences of each family

This study (D-numbers refer to the prereg):
  subset     sequences with all_sum > 30 (the paper's "substantial overall activity", Fig. 6; D2).  It selects
             on activity alone.  The plan's subset (r > 5 on at least two substrates) is reported only.
  I_adj      the index computed on a_s,i = max(r_s,i - 1, 0) (background subtracted, floored at 0; D3)
  R_adj      Pearson(log10 all_sum, I_adj) on the subset (D4)
  R_full     the paper's Pearson(all_sum, I) on all 1,954 sequences
  R_simex    primary (D6): R_adj corrected for shared measurement noise by SIMEX.  Extra log-normal noise
             at lambda = 0.5, 1, 1.5, 2 times each cell's deposited bootstrap variance is added, the subset is
             re-selected and R_adj recomputed; a quadratic in lambda is read at lambda = -1.  Interval: 95%
             percentile bootstrap over sequences with SIMEX redone inside each resample.
  swap null  the plan's profile-swap null (variants plain / donor / eb).  Reported only: none is calibrated
             (prereg, "Fixed decisions").

Blinding: `gate` pairs activity with specificity only through the paper's Table 1 test on all 1,954 sequences
per family.  `planted` never reads a real rate profile: it uses the real all_sum distribution, the real noise
(log-sd by substrate and level) and synthetic profiles.  `dryrun` permutes activity over sequences within
family before anything is paired.
"""
import sys, os, json, hashlib
import numpy as np
from scipy import stats

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t12_janzen_specificity/scripts/t12_analysis.py"
SEED = 20261125
SUBS = ["BWO", "BFO", "BLO", "BIO", "BVO", "BMO"]
FAMS = ["Fam1A.1", "Fam1B.1", "Fam2.1", "Fam2.2", "Fam3.1"]
RT = 5.0                    # the paper's activity threshold r_t
MIN_ACTIVE = 2              # plan's subset: active on at least two substrates (reported only)
SUM_MIN = 30.0              # D2: subset = all_sum > 30 (the paper's "substantial overall activity", Fig. 6)
SUBSET = "sum30"            # D2 primary subset rule; "ge2" = the plan's rule
MIN_SUBSET = 200            # gate: a family is eligible if its subset has at least this many sequences
RESCALE = True              # D5: null rates are rescaled to each sequence's observed all_sum
DONOR_Q = 0.90              # D5: donors are the top 10% of the family by all_sum
FLOOR_MAX = 3.0             # D5: floor sequences have max r <= 3
N_NULL_REAL, N_NULL_PL = 2000, 200
NREP = int(sys.argv[3]) if MODE == "planted" and len(sys.argv) > 3 else 100
SUP_R = -0.30               # plan: support needs R_adj <= -0.3 (kept for the plan-literal rule)
SUP_EST = -0.15             # D7: support needs R_simex <= -0.15 (and the interval below 0)
KILL_EST = -0.05            # D7: kill if R_simex > -0.05 or the interval reaches 0
BG = {"BWO": 1.57, "BFO": 1.37, "BLO": 1.46, "BIO": 0.87, "BVO": 1.21, "BMO": 2.14}   # Supp Table 2, 10^mu1
TABLE1 = {"Fam1A.1": (-0.696, -0.647, 0.554, 0.711), "Fam1B.1": (-0.839, -0.502, 0.738, 0.477),
          "Fam2.1": (-0.535, -0.888, 0.452, 0.911), "Fam2.2": (-0.538, -0.866, 0.445, 0.865),
          "Fam3.1": (-0.814, -0.462, 0.749, 0.513)}   # (R_I, rho_I, R_arom, rho_arom), published
FIG5_TEXT = {"Fam1A.1": 254, "Fam1B.1": 278, "Fam2.1": 1029, "Fam2.2": 853, "Fam3.1": 43}

F = {"xlsx": "raw/esm/41467_2022_31387_MOESM3_ESM.xlsx", "s2": "cache/sd/sheet2.tsv",
     "s4": "cache/sd/sheet4.tsv", "s5": "cache/sd/sheet5.tsv"}
SHA = {"xlsx": "78471fb417347bdc84129b48d27904ae942eab2fd022d84e0d311b3112ba329c",
       "s2": "412299ffb2838201fef3e107c5feb368e41d71f250d65de182ed486b4137bf45",
       "s4": "e1acbc71ced4886cbdfbc698321d0cbadcc48210119fdaea60568e01eb448069",
       "s5": "721d9b6a7abc2c23ceaa05787d9f330b13c6fb2c85fa3b1acb5dd6de471f2f22"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def path(k):
    return os.path.join(D, F[k])


def check_inputs():
    for k in F:
        got = sha256(path(k))
        if got != SHA[k]:
            sys.exit("input hash mismatch for %s: %s" % (F[k], got))


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
    print("wrote scripts_out/" + name)


# ---------------------------------------------------------------- data
def read_tsv(p):
    lines = [l for l in open(p, encoding="utf-8").read().split("\n") if l.strip()]
    hdr = lines[0].split("\t")
    return hdr, [l.split("\t") for l in lines[1:]]


class Data:
    def __init__(self):
        h, rows = read_tsv(path("s2"))
        c = {k: i for i, k in enumerate(h)}
        col = lambda k: np.array([float(r[c[k]]) for r in rows])
        self.seq = np.array([r[c["seq"]] for r in rows])
        self.fam = np.array([r[c["Family"]] for r in rows])
        self.r = np.stack([col("r_" + s) for s in SUBS], 1)
        self.lo = np.stack([col("r_2.5%_" + s) for s in SUBS], 1)
        self.hi = np.stack([col("r_97.5%_" + s) for s in SUBS], 1)
        self.kA50 = np.stack([col("bs_kA_50%_" + s) for s in SUBS], 1)
        self.sig = (np.log(self.hi) - np.log(self.lo)) / 3.92      # bootstrap log-sd per cell
        h4, rows4 = read_tsv(path("s4"))
        c4 = {k: i for i, k in enumerate(h4)}
        idx = {s: i for i, s in enumerate(self.seq)}
        self.map4 = np.array([idx[r[c4["seq"]]] for r in rows4])
        self.r4 = np.stack([np.array([float(r[c4["r_" + s]]) for r in rows4]) for s in SUBS], 1)
        self.fam4 = np.array([r[c4["Family"]] for r in rows4])
        self.allsum4 = np.array([float(r[c4["all_sum"]]) for r in rows4])
        self.I4 = np.array([float(r[c4["I"]]) for r in rows4])
        h5, rows5 = read_tsv(path("s5"))
        self.fig5 = {f: {int(r[0]): int(r[1 + j]) for r in rows5} for j, f in enumerate(FAMS)}

    def family(self, f):
        return np.where(self.fam == f)[0]


def prom_index(R):
    """Normalised Shannon entropy along the last axis; rows with zero total give nan."""
    R = np.asarray(R, float)
    tot = R.sum(-1, keepdims=True)
    q = np.where(tot > 0, R / np.where(tot > 0, tot, 1), np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(q > 0, q * np.log(q), 0.0)
    out = -t.sum(-1) / np.log(R.shape[-1])
    return np.where(tot[..., 0] > 0, out, np.nan)


def n_active(R):
    return (R > RT).sum(-1)


def masked_pearson(x, y, m):
    """Pearson of x and y over m (all of shape (..., n)); returns shape (...)."""
    m = m.astype(float)
    n = m.sum(-1)
    x = np.where(m > 0, x, 0.0); y = np.where(m > 0, y, 0.0)
    mx = (x * m).sum(-1) / n; my = (y * m).sum(-1) / n
    dx = (x - mx[..., None]) * m; dy = (y - my[..., None]) * m
    return (dx * dy).sum(-1) / np.sqrt((dx * dx).sum(-1) * (dy * dy).sum(-1))


def stats_of(R, subset=None):
    """The three per-family statistics for rates R (..., n, 6)."""
    subset = subset or SUBSET
    allsum = R.sum(-1)
    I = prom_index(R)
    a = np.maximum(R - 1.0, 0.0)
    Iadj = prom_index(a)
    sub = (n_active(R) >= MIN_ACTIVE) if subset == "ge2" else (allsum > SUM_MIN)
    r_full = masked_pearson(allsum, I, np.ones_like(sub))
    r_adj = masked_pearson(np.log10(allsum), np.nan_to_num(Iadj), sub)
    return r_full, r_adj, sub.sum(-1), allsum, Iadj, sub


# ---------------------------------------------------------------- noise bank
class NoiseBank:
    """Real bootstrap log-sd, binned by substrate and log10 r (0.25 wide).  No specificity is read.
    Built once from the real deposit and used both by the planted generator and by the null."""
    def __init__(self, r, sig):
        self.edges = np.arange(-1.0, 3.01, 0.25)
        lr = np.log10(r)
        self.pools = []
        for i in range(6):
            b = np.clip(np.digitize(lr[:, i], self.edges), 0, len(self.edges))
            pools = {}
            for k in range(len(self.edges) + 1):
                if (b == k).sum() >= 30:
                    pools[k] = np.sort(sig[b == k, i])
            keys = np.array(sorted(pools))
            # every bin index maps to the nearest populated bin
            full = [pools[keys[np.argmin(np.abs(keys - k))]] for k in range(len(self.edges) + 1)]
            self.pools.append(full)
        self.floor_sd = np.median(sig[r.max(1) <= FLOOR_MAX], 0)

    def draw(self, Rlevel, rng):
        out = np.empty(Rlevel.shape)
        lr = np.log10(np.maximum(Rlevel, 1e-3))
        u = rng.random(Rlevel.shape)
        for i in range(6):
            b = np.clip(np.digitize(lr[..., i], self.edges), 0, len(self.edges))
            oi = out[..., i]
            for k in np.unique(b):
                m = b == k
                pool = self.pools[i][k]
                oi[m] = pool[(u[..., i][m] * len(pool)).astype(int)]
        return out


# ---------------------------------------------------------------- null
class EBDonors:
    """D5 primary null ("eb"): donor profiles with their own measurement noise removed.
    Donors = top 10% of the family by all_sum.  Each donor's active set S (r > 5) defines a pattern group.
    For groups with >= EB_MIN members and |S| >= 2, log a_S is modelled as Gaussian; its covariance is the
    observed covariance minus the mean noise variance (deposited log-sd, scaled to log a by r/a), clipped
    to be positive semi-definite.  A null profile from such a donor is a fresh draw from that Gaussian;
    other donors give their raw profile.  Components outside S keep the donor's raw small share."""
    EB_MIN = 8

    def __init__(self, R, sig):
        allsum = R.sum(1)
        self.donors = np.where(allsum >= np.quantile(allsum, DONOR_Q))[0]
        a = np.maximum(R - 1.0, 0.0)
        self.raw = a / np.where(a.sum(1, keepdims=True) > 0, a.sum(1, keepdims=True), 1)
        act = R > RT
        self.groups = {}
        key = np.array([int("".join("1" if x else "0" for x in act[t]), 2) for t in range(len(R))])
        self.key = key
        for k in np.unique(key[self.donors]):
            mem = self.donors[key[self.donors] == k]
            S = act[mem[0]]
            if len(mem) < self.EB_MIN or S.sum() < 2:
                continue
            x = np.log(np.maximum(a[np.ix_(mem, np.where(S)[0])], 1e-6))
            sa = sig[np.ix_(mem, np.where(S)[0])] * (R[np.ix_(mem, np.where(S)[0])] / np.maximum(a[np.ix_(mem, np.where(S)[0])], 1e-6))
            C = np.cov(x.T) - np.diag((sa ** 2).mean(0))
            w, V = np.linalg.eigh(C)
            C = (V * np.maximum(w, 0)) @ V.T
            L = np.linalg.cholesky(C + 1e-10 * np.eye(len(C)))
            self.groups[k] = (np.where(S)[0], x.mean(0), L)

    def profiles(self, dn, rng):
        """dn: donor indices (any shape).  Returns profiles (dn.shape + (6,))."""
        P = self.raw[dn].copy()
        kk = self.key[dn]
        for k, (S, mu, L) in self.groups.items():
            m = kk == k
            if not m.any():
                continue
            z = rng.standard_normal((m.sum(), len(S)))
            x = mu[None] + z @ L.T
            e = np.exp(x - x.max(1, keepdims=True))
            rest = P[m][:, [j for j in range(6) if j not in S]].sum(1)
            sub = P[m]
            sub[:, S] = e / e.sum(1, keepdims=True) * (1.0 - rest)[:, None]
            P[m] = sub
        return P


def null_rates(R, sig, rng, n_draw, variant, nb, eb=None):
    """Profile-swap null for one family.  R: (n, 6) rates.  Returns (n_draw, n, 6)."""
    n = len(R)
    allsum = R.sum(1)
    A = np.maximum(allsum - 6.0, 0.0)
    a = np.maximum(R - 1.0, 0.0)
    prof = a / np.where(a.sum(1, keepdims=True) > 0, a.sum(1, keepdims=True), 1)
    donors = np.where(allsum >= np.quantile(allsum, DONOR_Q))[0]
    floor = np.where(R.max(1) <= FLOOR_MAX)[0]
    if len(floor) < 20:     # too few floor sequences in the family: pool is the 20 lowest by max r
        floor = np.argsort(R.max(1))[:20]
    dn = donors[rng.integers(0, len(donors), (n_draw, n))]
    fl = floor[rng.integers(0, len(floor), (n_draw, n))]
    if variant == "eb":
        sigx = A[None, :, None] * eb.profiles(dn, rng)
        s = nb.draw(1.0 + sigx, rng)
        sigx = sigx * np.exp(s * rng.standard_normal(sigx.shape))
    else:
        sigx = A[None, :, None] * prof[dn]
        if variant == "plain":
            sigx = sigx * np.exp(sig[None] * rng.standard_normal((n_draw, n, 6)))
    Rn = R[fl] + sigx
    if RESCALE:   # D5: each sequence keeps its observed total activity exactly
        tot = Rn.sum(-1, keepdims=True)
        Rn = Rn * (allsum[None, :, None] / tot)
    return Rn


# ---------------------------------------------------------------- SIMEX (D6, primary)
LAM = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
K_REAL, K_PL = 100, 10          # noise draws per lambda: point estimate (real) / per bootstrap sample
B_REAL, B_PL = 400, 60          # bootstrap samples for the SIMEX interval
PRE_MIN = 12.0                  # only sequences with observed all_sum > 12 can enter the subset under added noise


def radj_batch(R):
    """R_adj (Pearson log10 all_sum vs I_adj on all_sum > 30) for a batch R (..., n, 6)."""
    allsum = R.sum(-1)
    Iadj = prom_index(np.maximum(R - 1.0, 0.0))
    return masked_pearson(np.log10(allsum), np.nan_to_num(Iadj), allsum > SUM_MIN)


def simex(R, sig, rng, K, B):
    """SIMEX-quadratic estimate of the noise-free R_adj, and its bootstrap distribution.
    Extra noise at lambda times the deposited log-variance multiplies every cell; the subset is re-selected
    in every simulated data set; the mean R_adj per lambda is fitted by a quadratic and read at lambda = -1."""
    pre = np.where(R.sum(1) > PRE_MIN)[0]
    Rp, sp = R[pre], sig[pre]
    vals = [float(radj_batch(Rp))]
    for lam in LAM[1:]:
        acc = []
        for k in range(0, K, 20):
            kk = min(20, K - k)
            Rl = Rp[None] * np.exp(np.sqrt(lam) * sp[None] * rng.standard_normal((kk,) + Rp.shape))
            acc.append(radj_batch(Rl))
        vals.append(float(np.nanmean(np.concatenate(acc))))
    point = float(np.polyval(np.polyfit(LAM, vals, 2), -1.0))
    lin = float(np.polyval(np.polyfit(LAM, vals, 1), -1.0))
    boot = np.full(B, np.nan)
    if len(pre) >= 10 and B > 0:
        bi = rng.integers(0, len(pre), (B, len(pre)))
        Rb, sb = Rp[bi], sp[bi]
        curve = [radj_batch(Rb)]
        kb = K_PL if B <= B_PL else 10
        for lam in LAM[1:]:
            acc = np.zeros(B)
            for k in range(kb):
                acc += radj_batch(Rb * np.exp(np.sqrt(lam) * sb * rng.standard_normal(Rb.shape)))
            curve.append(acc / kb)
        curve = np.array(curve)                       # (len(LAM), B)
        X = np.vander(LAM, 3)                         # quadratic fit for every bootstrap sample at once
        coef = np.linalg.lstsq(X, curve, rcond=None)[0]
        boot = np.vander(np.array([-1.0]), 3) @ coef
        boot = boot[0]
    q = np.polyfit(LAM, vals, 2)   # reported only: the same curve read as if the true noise variance were c x deposited
    return {"curve": vals, "R_simex": point, "R_simex_linear": lin,
            "reported_only_if_true_noise_var_x0.5": float(np.polyval(q, -0.5)),
            "reported_only_if_true_noise_var_x2": float(np.polyval(q, -2.0)),
            "ci": [float(np.nanquantile(boot, 0.025)), float(np.nanquantile(boot, 0.975))] if np.isfinite(boot).any() else [float("nan")] * 2}


def family_test(R, sig, rng, nb, K, B, n_null, null_variants=("plain",)):
    r_full, r_adj, nsub, allsum, Iadj, sub = stats_of(R)
    out = {"n": int(len(R)), "n_subset": int(nsub), "R_full": float(r_full),
           "rho_full": float(stats.spearmanr(allsum, prom_index(R))[0]), "R_adj_raw": float(r_adj)}
    out["simex"] = simex(R, sig, rng, K, B)
    # the plan's subset and statistic, reported only
    _, r_adj2, nsub2, allsum2, Iadj2, sub2 = stats_of(R, "ge2")
    out["plan_subset"] = {"n": int(nsub2), "R_adj": float(r_adj2)}
    idx = np.where(sub2)[0]
    if len(idx) >= 10:
        bb = idx[rng.integers(0, len(idx), (2000 if B > B_PL else 400, len(idx)))]
        rb = masked_pearson(np.log10(allsum2[bb]), Iadj2[bb], np.ones(bb.shape))
        out["plan_subset"]["ci"] = [float(np.nanquantile(rb, 0.025)), float(np.nanquantile(rb, 0.975))]
    else:
        out["plan_subset"]["ci"] = [float("nan")] * 2
    # the plan's profile-swap null, reported only
    eb = EBDonors(R, sig) if "eb" in null_variants else None
    for v in null_variants:
        nf, na = [], []
        for k in range(0, n_null, 100):
            Rn = null_rates(R, sig, rng, min(100, n_null - k), v, nb, eb)
            nf.append(stats_of(Rn)[0]); na.append(stats_of(Rn, "ge2")[1])
        nf, na = np.concatenate(nf), np.concatenate(na)
        out["null_" + v] = {"R_full_q": [float(x) for x in np.nanquantile(nf, [0.025, 0.5, 0.975])],
                            "R_adj_plan_subset_q": [float(x) for x in np.nanquantile(na, [0.025, 0.5, 0.975])]}
    return out


def family_verdicts(o):
    """Per-family verdicts: 'kill', 'partly' or 'support'."""
    v = {}
    S = o["simex"]; est = S["R_simex"]; lo, hi = S["ci"]
    # D7, primary
    if not np.isfinite(hi) or hi >= 0 or est > KILL_EST:
        v["primary"] = "kill"
    elif est <= SUP_EST:
        v["primary"] = "support"
    else:
        v["primary"] = "partly"
    # the plan as written (plan subset, raw R_adj, profile-swap null with doubled noise), reported only
    if "null_plain" in o:
        nl = o["null_plain"]; ps = o["plan_subset"]
        ci_excl0 = np.isfinite(ps["ci"][1]) and ps["ci"][1] < 0
        full_inside = nl["R_full_q"][0] <= o["R_full"] <= nl["R_full_q"][2]
        if full_inside or not ci_excl0:
            v["plan"] = "kill"
        elif ps["R_adj"] <= SUP_R and o["R_full"] < nl["R_full_q"][0]:
            v["plan"] = "support"
        else:
            v["plan"] = "partly"
    # raw R_adj on the primary subset without the SIMEX correction, reported only
    rb = o["R_adj_raw"]
    v["raw_no_simex"] = "support" if (rb <= SUP_EST and hi < 0) else ("kill" if rb > KILL_EST else "partly")
    return v


RULES = ("primary", "plan", "raw_no_simex")
ELIGIBLE = [f for f in FAMS if FIG5_TEXT[f] >= MIN_SUBSET]     # D8: fixed from the published Fig. 5 counts


def overall(per):
    """per: {family: verdict dict}.  D8: verdict over the eligible families (3 of 4)."""
    res = {}
    for rule in RULES:
        vs = [per[f][rule] for f in ELIGIBLE if rule in per[f]]
        if not vs:
            continue
        ns, nk = vs.count("support"), vs.count("kill")
        res[rule] = "support" if ns >= 3 else ("kill" if nk >= 3 else "mixed")
        vs5 = [per[f][rule] for f in FAMS if rule in per[f]]
        res[rule + "_4of5"] = ("support" if vs5.count("support") >= 4 else
                               "kill" if vs5.count("kill") >= 4 else "mixed")
    return res


# ---------------------------------------------------------------- gate
def gate():
    check_inputs()
    d = Data()
    g = {"mode": "gate", "rows_sheet2": int(len(d.seq)), "rows_sheet4": int(len(d.map4)),
         "family_sizes": {f: int((d.fam == f).sum()) for f in FAMS},
         "sheet4_seqs_all_in_sheet2": bool(len(set(d.map4)) == len(d.map4) == len(d.seq))}
    g["max_abs_diff_r_sheet4_vs_sheet2"] = float(np.abs(d.r4 - d.r[d.map4]).max())
    g["family_labels_agree"] = bool((d.fam4 == d.fam[d.map4]).all())
    bgv = np.array([BG[s] for s in SUBS])
    g["max_rel_diff_r_vs_kA50_over_bg"] = float(np.abs(d.r / (d.kA50 / bgv) - 1).max())
    R = d.r[d.map4]
    g["max_abs_diff_allsum"] = float(np.abs(R.sum(1) - d.allsum4).max())
    Ime = prom_index(d.r4)
    g["max_abs_diff_I_recomputed_vs_sheet"] = float(np.abs(Ime - d.I4).max())
    g["share_I_within_1e-6"] = float((np.abs(Ime - d.I4) < 1e-6).mean())
    tab, ok = {}, True
    for f in FAMS:
        k = d.fam4 == f
        x = d.allsum4[k]; arom = (d.r4[k, 0] + d.r4[k, 1]) / x
        row = {"n": int(k.sum()),
               "R_I_sheet": float(stats.pearsonr(x, d.I4[k])[0]), "rho_I_sheet": float(stats.spearmanr(x, d.I4[k])[0]),
               "R_I_recomputed": float(stats.pearsonr(x, Ime[k])[0]),
               "R_arom": float(stats.pearsonr(x, arom)[0]), "rho_arom": float(stats.spearmanr(x, arom)[0]),
               "published": TABLE1[f]}
        diffs = [row["R_I_sheet"] - TABLE1[f][0], row["rho_I_sheet"] - TABLE1[f][1],
                 row["R_arom"] - TABLE1[f][2], row["rho_arom"] - TABLE1[f][3]]
        row["max_abs_diff_vs_published"] = float(np.max(np.abs(diffs)))
        ok &= abs(row["R_I_recomputed"] - TABLE1[f][0]) <= 0.02 and row["n"] == 1954
        tab[f] = row
    g["table1"] = tab
    g["table1_R_match_within_0.02_all_families"] = bool(ok)
    # published structure count (Fig. 5; also in the Results text), recomputed from rates
    cnt = {}
    for f in FAMS:
        na = n_active(d.r[d.family(f)])
        cnt[f] = {"recomputed_ge2": int((na >= MIN_ACTIVE).sum()), "published_text_ge2": FIG5_TEXT[f],
                  "recomputed_hist": [int((na == j).sum()) for j in range(7)],
                  "sheet_fig5_hist": [d.fig5[f].get(j, 0) for j in range(7)]}
    g["fig5_counts"] = cnt
    g["fig5_match"] = bool(all(cnt[f]["recomputed_hist"] == cnt[f]["sheet_fig5_hist"] for f in FAMS))
    elig = [f for f in FAMS if cnt[f]["recomputed_ge2"] >= MIN_SUBSET]
    g["eligible_families"] = elig
    g["gate_subset_rule_pass"] = len(elig) >= 3
    # structure / noise marginals (no specificity)
    g["noise_logsd_quantiles_10_50_90"] = [float(x) for x in np.quantile(d.sig, [0.1, 0.5, 0.9])]
    g["n_floor_sequences_max_r_le_3"] = {f: int((d.r[d.family(f)].max(1) <= FLOOR_MAX).sum()) for f in FAMS}
    # activity-only marginal: size of the primary subset (all_sum > 30); no specificity involved
    g["n_subset_allsum_gt30"] = {f: int((d.r[d.family(f)].sum(1) > SUM_MIN).sum()) for f in FAMS}
    g["gate_pass"] = bool(ok and g["gate_subset_rule_pass"] and g["fig5_match"])
    print(json.dumps(g, indent=1))
    dump("t12_gate.json", g)


# ---------------------------------------------------------------- planted
THETA = {"Fam1A.1": [2.0, 2.5, 0.0, -0.3, -0.3, 0.2], "Fam1B.1": [2.0, 2.5, 0.0, -0.3, -0.3, 0.2],
         "Fam2.1": [0.3, 1.0, 0.3, -0.5, -0.5, 0.4], "Fam2.2": [0.3, 1.0, 0.3, -0.5, -0.5, 0.4],
         "Fam3.1": [1.5, 2.3, 0.0, 0.0, 0.0, 0.0]}   # synthetic log-preferences, shaped on the paper's text
SIG1_LN = np.array([0.247, 0.205, 0.185, 0.141, 0.140, 0.180]) * np.log(10)    # Supp Table 2 sigma1


def synth_family(f, allsum_real, sig_real, nb, rng, gamma, tau, floor_var=True, noise="level", mix=False):
    n = len(allsum_real)
    A = np.maximum(allsum_real - 6.0, 0.0)
    z = np.log10(A + 1.0); z = (z - z.mean()) / z.std()
    g = np.exp(gamma * z)
    base = np.array(THETA[f])[None] + tau * rng.standard_normal((n, 6))
    if mix:   # non-Gaussian profiles: 40% specialists with one random substrate boosted by +3
        sp = rng.random(n) < 0.4
        base[sp, rng.integers(0, 6, sp.sum())] += 3.0
    lp = g[:, None] * base
    p = np.exp(lp - lp.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
    if floor_var:
        sf = np.sqrt(np.maximum(SIG1_LN ** 2 - nb.floor_sd ** 2, 0.0))
        fl = np.exp(sf[None] * rng.standard_normal((n, 6)) - 0.5 * sf[None] ** 2)
    else:
        fl = np.ones((n, 6))
    Rt = fl + A[:, None] * p
    s = sig_real if noise == "cell" else nb.draw(Rt, rng)
    eps = rng.standard_normal((n, 6))
    if noise == "corr":   # inputs A-C (BFO, BLO, BMO) and D-F (BWO, BVO, BIO) share a factor, rho = 0.5
        gA, gD = rng.standard_normal(n), rng.standard_normal(n)
        shared = np.stack([gD, gA, gA, gD, gD, gA], 1)
        eps = np.sqrt(0.5) * eps + np.sqrt(0.5) * shared
    Rm = Rt * np.exp(s * eps)
    _, r_true, _, _, _, _ = stats_of(Rt)
    return Rm, s, float(r_true)


SCEN = [  # name, gamma, tau, floor variation, noise model, mixture profiles
    ("null, tau 0.7", 0.0, 0.7, True, "level", False),
    ("null, tau 1.2", 0.0, 1.2, True, "level", False),
    ("null, tau 0.4", 0.0, 0.4, True, "level", False),
    ("null, no floor variation", 0.0, 0.7, False, "level", False),
    ("null, real per-cell noise", 0.0, 0.7, True, "cell", False),
    ("null, mixture of specialists", 0.0, 0.7, True, "level", True),
    ("null, correlated noise within input groups", 0.0, 0.7, True, "corr", False),
    ("link gamma 0.1", 0.1, 0.7, True, "level", False),
    ("link gamma 0.2", 0.2, 0.7, True, "level", False),
    ("link gamma 0.4", 0.4, 0.7, True, "level", False),
    ("link gamma 0.2, real per-cell noise", 0.2, 0.7, True, "cell", False),
    ("link gamma 0.2, mixture of specialists", 0.2, 0.7, True, "level", True),
]


def planted():
    check_inputs()
    d = Data()
    nb = NoiseBank(d.r, d.sig)
    which = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(len(SCEN)))
    rows = []
    for si in which:
        name, gamma, tau, flv, nz, mix = SCEN[si]
        rng = np.random.default_rng([SEED, 2, si])
        tally = {}
        acc = {f: {"R_full": [], "R_adj_raw": [], "R_simex": [], "R_true": [], "ci_hi": [], "plan_R_adj": [],
                   "n_subset": []} for f in FAMS}
        for rep in range(NREP):
            per = {}
            for f in FAMS:
                ix = d.family(f)
                Rm, s, rtrue = synth_family(f, d.r[ix].sum(1), d.sig[ix], nb, rng, gamma, tau, flv, nz, mix)
                o = family_test(Rm, s, rng, nb, K_PL * 2, B_PL, N_NULL_PL)
                per[f] = family_verdicts(o)
                a = acc[f]
                a["R_full"].append(o["R_full"]); a["R_adj_raw"].append(o["R_adj_raw"])
                a["R_simex"].append(o["simex"]["R_simex"]); a["R_true"].append(rtrue)
                a["ci_hi"].append(o["simex"]["ci"][1]); a["plan_R_adj"].append(o["plan_subset"]["R_adj"])
                a["n_subset"].append(o["n_subset"])
                for rule in RULES:
                    tally.setdefault("fam_" + rule, {}).setdefault(f, []).append(per[f][rule])
            for k, v in overall(per).items():
                tally.setdefault(k, []).append(v)
        row = {"scenario": name, "index": si, "gamma": gamma, "tau": tau, "floor_var": flv, "noise": nz,
               "mixture": mix, "nrep": NREP}
        for k, v in tally.items():
            if k.startswith("fam_"):
                row[k] = {f: {x: vv.count(x) / len(vv) for x in ("kill", "partly", "support")} for f, vv in v.items()}
            else:
                row[k] = {x: v.count(x) / len(v) for x in ("kill", "mixed", "support")}
        row["means"] = {f: {k: float(np.nanmean(v)) for k, v in acc[f].items()} for f in FAMS}
        row["sd_R_simex"] = {f: float(np.nanstd(acc[f]["R_simex"])) for f in FAMS}
        rows.append(row)
        print(json.dumps({"scenario": name, "primary": row.get("primary"), "plan_4of5": row.get("plan_4of5"),
                          "raw_no_simex": row.get("raw_no_simex"),
                          "fam_primary": row.get("fam_primary"),
                          "means": {f: {k: round(v, 3) for k, v in row["means"][f].items()} for f in FAMS}}),
              flush=True)
    res = {"mode": "planted", "seed": [SEED, 2], "nrep": NREP, "n_null": N_NULL_PL, "B": B_PL, "K": K_PL * 2,
           "script_sha256": sha256(os.path.abspath(__file__)), "eligible": ELIGIBLE, "rows": rows}
    tag = "" if len(sys.argv) <= 4 else "_part_" + sys.argv[4].replace(",", "-")
    dump("t12_planted%s.json" % tag, res)


def planted_merge():
    out = os.path.join(D, "scripts_out")
    parts = sorted(f for f in os.listdir(out) if f.startswith("t12_planted_part_"))
    rows, meta = [], None
    for p in parts:
        j = json.load(open(os.path.join(out, p)))
        meta = meta or j
        if j["script_sha256"] != meta["script_sha256"] or j["nrep"] != meta["nrep"]:
            sys.exit("parts come from different script versions or NREP: %s" % p)
        rows += j["rows"]
    rows.sort(key=lambda r: r["index"])
    meta = dict(meta); meta["rows"] = rows; meta["parts"] = parts
    dump("t12_planted.json", meta)


# ---------------------------------------------------------------- real (sealed)
PRIMARY = "primary"


def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs()
    d = Data()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    nb = NoiseBank(d.r, d.sig)
    per, fams = {}, {}
    for f in FAMS:
        ix = d.family(f)
        R, s = d.r[ix].copy(), d.sig[ix].copy()
        if dry:   # permute activity: each sequence keeps its profile above floor, takes another's total
            A = np.maximum(R - 1.0, 0.0).sum(1)
            pi = rng.permutation(len(R))
            scale = np.where(A > 0, A[pi] / np.where(A > 0, A, 1), 1.0)
            R = np.where(R > 1.0, 1.0 + (R - 1.0) * scale[:, None], R)
        o = family_test(R, s, rng, nb, K_REAL, B_REAL, N_NULL_REAL, ("eb", "donor", "plain"))
        v = family_verdicts(o)
        o["verdicts"] = v
        fams[f] = o; per[f] = v
    ov = overall(per)
    res = {"mode": "dryrun_activity_permuted" if dry else "real", "seed": [SEED, 4 if dry else 3],
           "script_sha256": st["script_sha256"], "primary_rule": PRIMARY, "eligible": ELIGIBLE,
           "verdict": ov.get(PRIMARY), "all_rules": ov, "families": fams}
    print(json.dumps(res, indent=1, default=float))
    dump("t12_dryrun_permuted_activity.json" if dry else "t12_real.json", res)


if __name__ == "__main__":
    np.seterr(invalid="ignore", divide="ignore")
    if MODE == "gate":
        gate()
    elif MODE == "planted":
        planted()
    elif MODE == "planted_merge":
        planted_merge()
    elif MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "dryrun":
        real(dry=True)
    elif MODE == "real":
        real(dry=False)
    else:
        sys.exit("unknown mode")
