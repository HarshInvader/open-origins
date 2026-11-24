"""T8 (prereg docs/prereg/t8_ameta_noise.md): is the growth-versus-variation trade-off in Ameta et al. 2021
(Nat Commun, doi:10.1038/s41467-021-21000-1) more than droplet noise?

Usage (single process, single thread; run under nice):
  python -I t8_analysis.py <experiments/t8_ameta_noise dir> gate       # structure + the paper's own Fisher test
  python -I t8_analysis.py <experiments/t8_ameta_noise dir> planted    # synthetic droplets only (real UMI totals)
  python -I t8_analysis.py <experiments/t8_ameta_noise dir> sealcheck  # says whether `real` would run
  python -I t8_analysis.py <experiments/t8_ameta_noise dir> dryrun     # the `real` code, yield permuted over networks
  python -I t8_analysis.py <experiments/t8_ameta_noise dir> real       # the sealed test; refuses without a seal

Inputs are the TSVs written by scripts/xlsx_to_tsv.py from Supplementary Data 2 into cache/sd2/ (gitignored).
A droplet's network is the set of species whose cells are filled (blank = species absent).

Definitions (paper, Results; authors' code az_tools.compute_pscore / collapse_postprocess):
  network mean fraction  m_N = mean over N's droplets of the droplet's species fractions
  perturbation           p(G->G') = sum over v in V=G of |m_G'(v)/sum_V m_G' - m_G(v)/sum_V m_G|
  yield                  Y_N = network yield in uM (Supplementary Data 2, mean over droplets)

Blinding: `gate` pairs yield with perturbation only on the paper's own 162-pair subset and prints only the
2x2 table and the Fisher test.  `planted` never reads real fractions (it uses real UMI totals, the real
network list and the real yields).  `dryrun` permutes yield over networks before anything is paired.
"""
import sys, os, json, hashlib
import numpy as np
from scipy import stats
from scipy.stats import contingency

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t8_ameta_noise/scripts/t8_analysis.py"
SEED = 20261125
MINREP = 5                 # D2: both networks of a pair need at least this many droplets
MINSIZE = 2                # D2: G has at least 2 species (with 1, p is 0 by definition)
B_NOISE_REAL, B_NOISE_PL = 200, 40     # bootstrap draws for the noise floor
S_SPLIT_REAL, S_SPLIT_PL = 200, 40     # random splits for the plan's split-half noise
B_CI_REAL, B_CI_PL = 4000, 1000        # cluster-bootstrap draws for intervals
NREP = int(sys.argv[3]) if MODE == "planted" and len(sys.argv) > 3 else 100   # planted replicates per scenario
SUP_R, SUP_EXCL = -0.20, -0.05          # support: estimate <= -0.20 and upper bound < -0.05
P_HI, Y_HI = 0.8, 0.08     # the paper's Fig. 2d cut-offs (gate only)

F = {"net": "cache/sd2/sheet1.tsv", "frac": "cache/sd2/sheet3.tsv", "umi": "cache/sd2/sheet4.tsv",
     "xlsx": "raw/esm/41467_2021_21000_MOESM4_ESM.xlsx"}
SHA = {"xlsx": "343f1c7014d70bc3dbb41d749aa2988ba43968829bc203d9118a8f41d1067278",
       "net": None, "frac": None, "umi": None}   # filled below from SHA_TSV
SHA_TSV = {"net": "edad2c8763ebdfb13fb21df9140b17128c5eb1477e82cbe6bb59df57c935ceb9", "frac": "f0704a9eebf3616d59458ef85de1dbf5aa58fce3e70f7998bf9d8e3fc76d26a8", "umi": "fd11539a592dd6c3660218d60df2df9bb5305020f6ad2fa06dc00dafd11676ea"}
WC = {"G": "C", "C": "G", "A": "U", "U": "A"}


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
        want = SHA[k] if SHA[k] else SHA_TSV[k]
        got = sha256(path(k))
        if got != want:
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
        json.dump(obj, f, indent=1)
    print("wrote scripts_out/" + name)


# ---------------------------------------------------------------- data
def read_tsv(p):
    lines = open(p, encoding="utf-8").read().split("\n")
    hdr = lines[1].split("\t")
    rows = [(l.split("\t") + [""] * 20)[:18] for l in lines[2:] if l.strip()]
    return hdr, rows


class Data:
    def __init__(self):
        hdr, nrows = read_tsv(path("net"))
        self.sp = hdr[:16]
        self.ig = np.array([s[0] for s in self.sp]); self.tg = np.array([s[1] for s in self.sp])
        self.mask = np.array([[r[i] != "" for i in range(16)] for r in nrows])          # networks x 16
        self.yield_ = np.array([float(r[17]) for r in nrows])
        self.reps_listed = np.array([int(r[16]) for r in nrows])
        self.net_frac_sheet = np.array([[float(r[i]) if r[i] != "" else 0.0 for i in range(16)] for r in nrows])
        key = {tuple(m): i for i, m in enumerate(self.mask)}
        _, frows = read_tsv(path("frac")); _, urows = read_tsv(path("umi"))
        fm = np.array([[r[i] != "" for i in range(16)] for r in frows])
        um = np.array([[r[i] != "" for i in range(16)] for r in urows])
        self.same_pattern = bool((fm == um).all())
        self.drop_net = np.array([key.get(tuple(m), -1) for m in fm])
        self.frac = np.array([[float(r[i]) if r[i] != "" else 0.0 for i in range(16)] for r in frows])
        self.umi = np.array([[float(r[i]) if r[i] != "" else 0.0 for i in range(16)] for r in urows])
        self.umi_tot = self.umi.sum(1)
        self.n = len(self.mask)
        self.drops = [np.where(self.drop_net == i)[0] for i in range(self.n)]
        self.ndrop = np.array([len(x) for x in self.drops])
        self.size = self.mask.sum(1)

    def pairs(self, minrep=MINREP, minsize=MINSIZE):
        """All (G, G', a) with G' = G plus species a, both networks in the data."""
        key = {tuple(m): i for i, m in enumerate(self.mask)}
        out = []
        for gp in range(self.n):
            for a in np.where(self.mask[gp])[0]:
                m = self.mask[gp].copy(); m[a] = False
                g = key.get(tuple(m))
                if g is None or self.size[g] < minsize:
                    continue
                if min(self.ndrop[g], self.ndrop[gp]) < minrep:
                    continue
                out.append((g, gp, a))
        return np.array(out, dtype=int).reshape(-1, 3)

    def fig2d_pairs(self):
        """The paper's Fig. 2d subset (figures.ipynb cell 36): |G| in 3..5, IGS of a is G or C, no species of G
        shares a's IGS (m = 0), exactly one species of G has the tag that pairs with a's IGS (n = 1)."""
        P = self.pairs(minrep=1, minsize=1)
        keep = []
        for g, gp, a in P:
            if self.size[g] not in (3, 4, 5) or self.ig[a] not in "GC":
                continue
            inG = self.mask[g]
            m = int((self.ig[inG] == self.ig[a]).sum())
            n = int((self.tg[inG] == WC[self.ig[a]]).sum())
            if m == 0 and n == 1:
                keep.append((g, gp, a))
        return np.array(keep, dtype=int)


def net_means(d, frac):
    M = np.zeros((d.n, 16))
    for i in range(d.n):
        if d.ndrop[i]:
            M[i] = frac[d.drops[i]].mean(0)
    return M


def renorm(X, V):
    """Restrict the last axis to V (bool, broadcastable) and renormalise; all-zero -> uniform on V."""
    Y = X * V
    s = Y.sum(-1, keepdims=True)
    k = V.sum(-1, keepdims=True) * np.ones_like(s)
    U = np.broadcast_to(V, Y.shape) / k
    return np.where(s > 0, Y / np.where(s > 0, s, 1), U)


def perturbation(M, P, mask):
    V = mask[P[:, 0]]
    return np.abs(renorm(M[P[:, 1]], V) - renorm(M[P[:, 0]], V)).sum(1)


# ---------------------------------------------------------------- noise measures
def boot_means(d, frac, nets, B, rng):
    out = {}
    for i in nets:
        idx = d.drops[i]
        draw = rng.integers(0, len(idx), (B, len(idx)))
        out[i] = frac[idx][draw].mean(1)
    return out


def noise_floor(d, frac, M, P, B, rng):
    """D5, second noise measure (the primary uses split_half): expected L1 size of the sampling error of
    p(G->G') when nothing changes.
    Bootstrap each network's droplets, take the deviation of each side's renormalised mean from its own
    point value, and average sum_v |dev_G' - dev_G| over draws.  Uses the droplets of both G and G'."""
    nets = np.unique(P[:, :2])
    bm = boot_means(d, frac, nets, B, rng)
    out = np.empty(len(P))
    for k, (g, gp, a) in enumerate(P):
        V = d.mask[g]
        x0 = renorm(M[g], V); y0 = renorm(M[gp], V)
        X = renorm(bm[g], V); Y = renorm(bm[gp], V)
        out[k] = np.abs((Y - y0) - (X - x0)).sum(1).mean()
    return out


def split_half(d, frac, P, S, rng):
    """The plan's noise: for each G, mean over S random splits of its droplets into two halves of the
    L1 distance between the two half means (no species added)."""
    val = {}
    for g in np.unique(P[:, 0]):
        idx = d.drops[g]; n = len(idx); h = n // 2
        perm = rng.permuted(np.tile(np.arange(n), (S, 1)), axis=1)
        A = frac[idx][perm[:, :h]].mean(1); Bm = frac[idx][perm[:, h:]].mean(1)
        val[g] = np.abs(A - Bm).sum(1).mean()
    return np.array([val[g] for g in P[:, 0]])


# ---------------------------------------------------------------- statistics
STRATA = [(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 8), (9, 11), (12, 15)]   # D4: strata of |G|
CUR_STRATUM = None   # set by analyse(): stratum id of each pair


def stratum_of(sizes):
    out = np.full(len(sizes), -1)
    for k, (lo, hi) in enumerate(STRATA):
        out[(sizes >= lo) & (sizes <= hi)] = k
    return out


def ranks(x):
    """D4: within-stratum rank scores, (rank - 0.5)/n - 0.5, so every stratum is centred on 0.  A Pearson
    correlation of these scores is a size-stratified Spearman correlation."""
    out = np.empty(len(x))
    for k in np.unique(CUR_STRATUM):
        m = CUR_STRATUM == k
        out[m] = (stats.rankdata(x[m]) - 0.5) / m.sum() - 0.5
    return out


def wcorr(W, a, b):
    """Weighted Pearson correlation for each row of weights W (B x P)."""
    sw = W.sum(1, keepdims=True)
    ma = (W @ a)[:, None] / sw; mb = (W @ b)[:, None] / sw
    A = a[None, :] - ma; Bv = b[None, :] - mb
    cov = (W * A * Bv).sum(1); va = (W * A * A).sum(1); vb = (W * Bv * Bv).sum(1)
    return cov / np.sqrt(va * vb)


def partial(rxy, rxz, ryz):
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))


def cluster_weights(P, B, rng):
    """D7: resample the before-networks G with replacement; a pair gets the count of its G."""
    G, inv = np.unique(P[:, 0], return_inverse=True)
    C = rng.multinomial(len(G), np.ones(len(G)) / len(G), size=B)      # B x nG
    return C[:, inv].astype(float)


def spear_block(y, p, z, W):
    """Spearman(y,p), Spearman(y,z), partial Spearman(y,p | z): point values and bootstrap draws."""
    ry, rp, rz = ranks(y), ranks(p), ranks(z)
    pt = {"yp": np.corrcoef(ry, rp)[0, 1], "yz": np.corrcoef(ry, rz)[0, 1], "pz": np.corrcoef(rp, rz)[0, 1]}
    pt["partial"] = partial(pt["yp"], pt["yz"], pt["pz"])
    bs = {"yp": wcorr(W, ry, rp), "yz": wcorr(W, ry, rz), "pz": wcorr(W, rp, rz)}
    bs["partial"] = partial(bs["yp"], bs["yz"], bs["pz"])
    return pt, bs


def ci(x):
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def analyse(d, frac, yld, P, rng, Bn, S, Bci, extras=False, stratify=True):
    global CUR_STRATUM
    CUR_STRATUM = stratum_of(d.size[P[:, 0]]) if stratify else np.zeros(len(P), dtype=int)
    M = net_means(d, frac)
    p = perturbation(M, P, d.mask)
    nf = noise_floor(d, frac, M, P, Bn, rng)
    sh = split_half(d, frac, P, S, rng)
    YG, YGp = yld[P[:, 0]], yld[P[:, 1]]
    V = d.mask[P[:, 0]]
    # D6: absolute concentrations, c = fraction x network yield, on V (no renormalisation)
    cG = M[P[:, 0]] * V * YG[:, None]; cGp = M[P[:, 1]] * V * YGp[:, None]
    p_abs = np.abs(cGp - cG).sum(1)
    W = cluster_weights(P, Bci, rng)
    out = {"n_pairs": int(len(P)), "n_G": int(len(np.unique(P[:, 0])))}
    for nm, z in (("floor", nf), ("split", sh)):
        pt, bs = spear_block(YG, p, z, W)
        out[nm] = {"r_yp": pt["yp"], "r_yp_ci": ci(bs["yp"]), "r_yz": pt["yz"], "r_yz_ci": ci(bs["yz"]),
                   "r_pz": pt["pz"], "partial": pt["partial"], "partial_ci": ci(bs["partial"])}
        # absolute version, noise scaled to concentration units by the mean yield of the pair
        za = z * (YG + YGp) / 2
        pa, ba = spear_block(YG, p_abs, za, W)
        out[nm]["abs_r_yp"] = pa["yp"]; out[nm]["abs_r_yp_ci"] = ci(ba["yp"])
        out[nm]["abs_partial"] = pa["partial"]; out[nm]["abs_partial_ci"] = ci(ba["partial"])
        # D8 candidate: excess perturbation p - noise floor (a difference, not a regression adjustment)
        ex = p - z
        pe, be = spear_block(YG, ex, z, W)
        out[nm]["excess_r"] = pe["yp"]; out[nm]["excess_r_ci"] = ci(be["yp"])
        exa = p_abs - za
        pea, bea = spear_block(YG, exa, za, W)
        out[nm]["abs_excess_r"] = pea["yp"]; out[nm]["abs_excess_r_ci"] = ci(bea["yp"])
    if extras:
        out["_arrays"] = {"p": p, "floor": nf, "split": sh, "p_abs": p_abs}
    return out


def verdicts(o):
    """Rules evaluated side by side.  PRIMARY is the one that decides (see prereg).
    kill (plan K-b): the upper bound of the partial correlation is >= 0, or yield-noise is at least as
         negative as yield-perturbation.
    support: partial <= -0.20 and its upper bound < -0.05 (plan); `plan_*` also needs the same on absolute
         concentrations (plan as written)."""
    v = {}
    k, sp = {}, {}
    for nm in ("floor", "split"):
        e = o[nm]
        k[nm] = e["partial_ci"][1] >= 0 or e["r_yz"] <= e["r_yp"]
        sp[nm] = e["partial"] <= SUP_R and e["partial_ci"][1] < SUP_EXCL
        sa = e["abs_partial"] <= SUP_R and e["abs_partial_ci"][1] < SUP_EXCL
        v["plan_" + nm] = "kill" if k[nm] else ("support" if sp[nm] and sa else "partly")
        v["noabs_" + nm] = "kill" if k[nm] else ("support" if sp[nm] else "partly")
        kx = e["excess_r_ci"][1] >= 0
        sx = e["excess_r"] <= SUP_R and e["excess_r_ci"][1] < SUP_EXCL
        v["excess_" + nm] = "kill" if kx else ("support" if sx else "partly")
    v["noabs_both"] = "kill" if (k["floor"] or k["split"]) else ("support" if sp["floor"] and sp["split"] else "partly")
    return v


# ---------------------------------------------------------------- gate
def gate():
    check_inputs()
    d = Data()
    res = {"mode": "gate", "script_sha256": sha256(os.path.abspath(__file__))}
    res["networks"] = int(d.n); res["droplets"] = int(len(d.drop_net))
    res["droplets_matched_to_a_network"] = int((d.drop_net >= 0).sum())
    res["frac_and_umi_sheets_same_filled_cells"] = d.same_pattern
    res["networks_whose_droplet_count_equals_listed_replicates"] = int((d.ndrop == d.reps_listed).sum())
    bad = np.where(d.ndrop != d.reps_listed)[0]
    res["networks_with_count_mismatch"] = [{"species": [d.sp[i] for i in np.where(d.mask[j])[0]],
                                            "droplets": int(d.ndrop[j]), "listed": int(d.reps_listed[j])} for j in bad]
    runs = 1 + int((np.diff(d.drop_net) != 0).sum())
    res["droplet_runs_in_file_order"] = runs
    M = net_means(d, d.frac)
    dev = np.abs(M - d.net_frac_sheet)[d.mask]
    res["max_abs_dev_network_fraction_vs_mean_of_droplets"] = float(dev.max())
    res["share_network_cells_within_1.01e-4"] = float((dev <= 1.01e-4).mean())
    frac_from_umi = d.umi / d.umi_tot[:, None]
    res["max_abs_dev_droplet_fraction_vs_umi_share"] = float(np.abs(frac_from_umi - d.frac).max())
    res["droplet_umi_total_quantiles_0_10_50_90_100"] = [float(x) for x in np.percentile(d.umi_tot, [0, 10, 50, 90, 100])]
    # blind decidability counts (structure only)
    Pall = d.pairs(minrep=1, minsize=1)
    res["pairs_all"] = int(len(Pall))
    res["pairs_G_size_ge2"] = int(len(d.pairs(minrep=1, minsize=2)))
    P = d.pairs()
    res["pairs_primary_minrep5_size_ge2"] = int(len(P))
    res["primary_distinct_G"] = int(len(np.unique(P[:, 0])))
    res["primary_pairs_by_G_size"] = {int(s): int((d.size[P[:, 0]] == s).sum()) for s in np.unique(d.size[P[:, 0]])}
    # the paper's Fisher test (the one joint look allowed)
    Q = d.fig2d_pairs()
    res["fig2d_pairs"] = int(len(Q)); res["fig2d_distinct_G"] = int(len(np.unique(Q[:, 0])))
    out = {}
    for src, MM in (("mean_of_droplets", M), ("network_sheet_rounded", d.net_frac_sheet)):
        p = perturbation(MM, Q, d.mask)
        y = d.yield_[Q[:, 0]]
        hp, hy = p > P_HI, y > Y_HI
        t = np.array([[int((hp & hy).sum()), int((hp & ~hy).sum())],
                      [int((~hp & hy).sum()), int((~hp & ~hy).sum())]])
        odds_s, p_less = stats.fisher_exact(t, alternative="less")
        cond = contingency.odds_ratio(t, kind="conditional")
        cci = cond.confidence_interval(0.95)
        se = float(np.sqrt((1.0 / t).sum())) if (t > 0).all() else float("nan")
        woolf = [float(np.exp(np.log(odds_s) - 1.959964 * se)), float(np.exp(np.log(odds_s) + 1.959964 * se))]
        out[src] = {"table [[hiP&hiY, hiP&loY],[loP&hiY, loP&loY]]": t.tolist(),
                    "sample_odds_ratio": float(odds_s), "conditional_mle_odds_ratio": float(cond.statistic),
                    "conditional_95ci_two_sided": [float(cci.low), float(cci.high)],
                    "woolf_95ci_on_sample_odds_ratio": woolf,
                    "one_sided_fisher_p_less": float(p_less),
                    "pass_N": len(Q) == 162, "pass_or_lt_0.1": float(cond.statistic) < 0.1,
                    "pass_p_1.6e-3_to_2_sig_fig": round(float(p_less), 4) == 0.0016}
    res["fisher"] = out
    res["gate_pass"] = all(v["pass_N"] and v["pass_or_lt_0.1"] for v in out.values())
    print(json.dumps(res, indent=1))
    dump("t8_gate.json", res)


# ---------------------------------------------------------------- planted
def true_comp(d, rng, sig_b, gamma, yld):
    """Log-linear compositions from random species effects theta and random pairwise effects beta (independent
    of the real chemistry and of yield).  gamma > 0 plants a trade-off: interaction strength of network N is
    scaled by exp(-gamma * z(log Y_N)), so high-yield networks respond less to an added species."""
    theta = rng.normal(0, 1, 16)
    beta = rng.normal(0, sig_b, (16, 16)); np.fill_diagonal(beta, 0)
    z = np.log(yld).copy()
    for sz in np.unique(d.size):                    # standardise log yield within each network size
        m = d.size == sz
        z[m] = (z[m] - z[m].mean()) / z[m].std() if m.sum() > 2 and z[m].std() > 0 else 0.0
    g = np.exp(-gamma * z)
    L = theta[None, :] + g[:, None] * (d.mask.astype(float) @ beta)     # sum over u in N of beta[u, v]
    L = np.where(d.mask, L, -np.inf)
    L = L - L.max(1, keepdims=True)
    Pi = np.exp(L); Pi = Pi / Pi.sum(1, keepdims=True)
    return Pi


def sim_droplets(d, Pi, kappa_net, rng):
    """Each real droplet keeps its network and its real UMI total; its counts are Dirichlet-multinomial
    around the network's true composition with concentration kappa (inf = multinomial only)."""
    pi = Pi[d.drop_net]
    k = kappa_net[d.drop_net]
    fin = np.isfinite(k)
    pd_ = pi.copy()
    if fin.any():
        gsh = rng.gamma(np.where(pi[fin] > 0, pi[fin] * k[fin, None], 1.0)) * (pi[fin] > 0)
        s = gsh.sum(1, keepdims=True)
        pd_[fin] = np.where(s > 0, gsh / np.where(s > 0, s, 1), pi[fin])
    cnt = rng.multinomial(d.umi_tot.astype(np.int64), pd_)
    return cnt / d.umi_tot[:, None]


SCEN = [
    # name, sigma_beta, gamma, kappa, kappa-depends-on-yield exponent
    ("null_zero_true_p_multinomial", 0.0, 0.0, np.inf, 0.0),
    ("null_zero_true_p_kappa50", 0.0, 0.0, 50.0, 0.0),
    ("null_zero_true_p_kappa_rises_with_yield", 0.0, 0.0, 50.0, 1.0),
    ("null_sb0.5_kappa50", 0.5, 0.0, 50.0, 0.0),
    ("null_sb1_multinomial", 1.0, 0.0, np.inf, 0.0),
    ("null_sb1_kappa50", 1.0, 0.0, 50.0, 0.0),
    ("null_sb1_kappa20", 1.0, 0.0, 20.0, 0.0),
    ("null_sb1_kappa_rises_with_yield", 1.0, 0.0, 50.0, 1.0),
    ("tradeoff_g0.5_sb1_kappa50", 1.0, 0.5, 50.0, 0.0),
    ("tradeoff_g1_sb1_kappa50", 1.0, 1.0, 50.0, 0.0),
    ("tradeoff_g2_sb1_kappa50", 1.0, 2.0, 50.0, 0.0),
    ("tradeoff_g2_sb0.5_kappa50", 0.5, 2.0, 50.0, 0.0),
    ("tradeoff_g3_sb0.5_kappa50", 0.5, 3.0, 50.0, 0.0),
    ("tradeoff_g2_sb0.5_kappa20", 0.5, 2.0, 20.0, 0.0),
    ("tradeoff_g2_sb0.5_kappa_rises_with_yield", 0.5, 2.0, 50.0, 1.0),
]


def planted():
    check_inputs()
    d = Data()
    P = d.pairs()
    yld = d.yield_.copy()                          # real yields; real fractions are never read
    rng = np.random.default_rng([SEED, 2])
    rows = []
    for name, sb, gam, kap, kexp in SCEN:
        acc = {}; tally = {}
        truth = []
        for rep in range(NREP):
            Pi = true_comp(d, rng, sb, gam, yld)
            kn = np.full(d.n, kap) if kexp == 0 else kap * (yld / np.median(yld)) ** kexp
            fr = sim_droplets(d, Pi, kn, rng)
            # true perturbation and its correlation with yield (what the test should recover)
            tp = perturbation(Pi, P, d.mask)
            global CUR_STRATUM
            CUR_STRATUM = stratum_of(d.size[P[:, 0]])
            truth.append([float(tp.mean()), float(np.corrcoef(ranks(yld[P[:, 0]]), ranks(tp))[0, 1]) if tp.std() > 0 else 0.0])
            o = analyse(d, fr, yld, P, rng, B_NOISE_PL, S_SPLIT_PL, B_CI_PL)
            for nm in ("floor", "split"):
                for k in ("r_yp", "r_yz", "partial", "abs_partial", "excess_r", "abs_excess_r"):
                    acc.setdefault(nm + "." + k, []).append(o[nm][k])
                acc.setdefault(nm + ".partial_hi", []).append(o[nm]["partial_ci"][1])
                acc.setdefault(nm + ".excess_hi", []).append(o[nm]["excess_r_ci"][1])
            for rule, vv in verdicts(o).items():
                tally.setdefault(rule, {"kill": 0, "partly": 0, "support": 0})[vv] += 1
        tr = np.array(truth)
        row = {"scenario": name, "sigma_beta": sb, "gamma": gam, "kappa": None if not np.isfinite(kap) else kap,
               "kappa_yield_exponent": kexp, "n_rep": NREP,
               "true_mean_p": round(float(tr[:, 0].mean()), 3), "true_spearman_yield_p": round(float(tr[:, 1].mean()), 3),
               "mean": {k: round(float(np.mean(v)), 3) for k, v in acc.items()},
               "rates": {r: {k: round(c / NREP, 3) for k, c in t.items()} for r, t in tally.items()}}
        rows.append(row)
        print(json.dumps(row), flush=True)
    dump("t8_planted.json", {"mode": "planted", "seed": [SEED, 2], "script_sha256": sha256(os.path.abspath(__file__)),
                             "n_pairs": int(len(P)), "rows": rows})


# ---------------------------------------------------------------- real (sealed)
PRIMARY = "noabs_split"   # D9: plan K-b with split-half noise, size-stratified, no absolute condition


def real(dry=False):
    st = seal_status()
    if not dry and not st["real_allowed"]:
        sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                 % (SELF, st["script_sha256"]))
    check_inputs()
    d = Data()
    P = d.pairs()
    rng = np.random.default_rng([SEED, 4 if dry else 3])
    yld = d.yield_.copy()
    if dry:
        yld = yld[rng.permutation(d.n)]
    o = analyse(d, d.frac, yld, P, rng, B_NOISE_REAL, S_SPLIT_REAL, B_CI_REAL, extras=True)
    arr = o.pop("_arrays")
    v = verdicts(o)
    res = {"mode": "dryrun_yield_permuted" if dry else "real", "seed": [SEED, 4 if dry else 3],
           "script_sha256": st["script_sha256"], "primary_rule": PRIMARY,
           "verdict": v.get(PRIMARY), "all_rules": v, "stats": o}
    # reported only
    YG = yld[P[:, 0]]
    rep = {}
    rep["median_p"] = float(np.median(arr["p"])); rep["median_noise_floor"] = float(np.median(arr["floor"]))
    rep["share_p_below_noise_floor"] = float((arr["p"] < arr["floor"]).mean())
    by = {}
    for s in np.unique(d.size[P[:, 0]]):
        k = d.size[P[:, 0]] == s
        if k.sum() >= 30:
            by[int(s)] = {"n": int(k.sum()), "spearman_yield_p": float(stats.spearmanr(YG[k], arr["p"][k])[0]),
                          "spearman_yield_excess": float(stats.spearmanr(YG[k], (arr["p"] - arr["floor"])[k])[0])}
    rep["by_G_size"] = by
    Q = d.fig2d_pairs()
    Qk = Q[np.minimum(d.ndrop[Q[:, 0]], d.ndrop[Q[:, 1]]) >= MINREP]
    rep["fig2d_subset_with_minrep5"] = int(len(Qk))
    if len(Qk) >= 10:
        Mq = net_means(d, d.frac)
        pq = perturbation(Mq, Qk, d.mask)
        nq = noise_floor(d, d.frac, Mq, Qk, B_NOISE_REAL, rng)
        rep["fig2d_subset_spearman_yield_p"] = float(stats.spearmanr(yld[Qk[:, 0]], pq)[0])
        rep["fig2d_subset_spearman_yield_excess"] = float(stats.spearmanr(yld[Qk[:, 0]], pq - nq)[0])
    for mr in (3, 10):
        Pm = d.pairs(minrep=mr)
        om = analyse(d, d.frac, yld, Pm, rng, B_NOISE_REAL // 2, S_SPLIT_REAL // 2, B_CI_REAL // 2)
        rep["minrep_%d" % mr] = {"n_pairs": om["n_pairs"], "rules": verdicts(om),
                                 "floor_excess_r": om["floor"]["excess_r"], "floor_excess_r_ci": om["floor"]["excess_r_ci"]}
    ou = analyse(d, d.frac, yld, P, rng, B_NOISE_REAL // 2, S_SPLIT_REAL // 2, B_CI_REAL // 2, stratify=False)
    rep["unstratified_by_size"] = {"rules": verdicts(ou), "split": {k: ou["split"][k] for k in
                                   ("r_yp", "r_yp_ci", "r_yz", "partial", "partial_ci")}}
    res["reported_only"] = rep
    print(json.dumps(res, indent=1, default=float))
    dump("t8_dryrun_permuted_yield.json" if dry else "t8_real.json", res)


if __name__ == "__main__":
    np.seterr(invalid="ignore", divide="ignore")
    if MODE == "gate":
        gate()
    elif MODE == "planted":
        planted()
    elif MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "dryrun":
        real(dry=True)
    elif MODE == "real":
        real(dry=False)
    else:
        sys.exit("unknown mode")
