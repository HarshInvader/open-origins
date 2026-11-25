"""T18b core: replicate noise model, empirical-Bayes pair terms on the latent scale, planted truths, triple check.

Imports t18_core (unchanged). Nothing here computes a threshold on the real landscape.
Prereg: docs/prereg/t18b_qt45_pair_epistasis.md.
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import expit, ndtri

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t18_core as C  # noqa: E402

NS, WT, AR = C.NS, C.WT, C.AR
BASES = C.BASES
COUNTS = os.path.join(C.STUDY, "raw", "t18b_counts")
LN2 = np.log(2.0)
LIBS_OUT = ("out_nodel_A", "out_nodel_B", "out_nodel_C")


# ------------------------------------------------------------------ counts (HD <= 2 only; HD = 3 files are blind)
def parse_label(lab):
    if lab == "WT":
        return ()
    out = []
    for tok in lab.split(","):
        p, b = tok.split(":")
        out.append((int(p) - 2, BASES.index(b)))
    return tuple(out)


def load_counts_hd012():
    """dict genotype -> {lib: count}; genotype = tuple of (site, base) sorted by site."""
    cnt = {}
    for lib in LIBS_OUT + ("in_nodel",):
        with open(os.path.join(COUNTS, f"counts_hd012_{lib}.tsv")) as fh:
            for line in fh:
                _, lab, c = line.rstrip("\n").split("\t")
                g = parse_label(lab)
                cnt.setdefault(g, {})[lib] = cnt.get(g, {}).get(lib, 0) + int(c)
    with open(os.path.join(COUNTS, "totals.json")) as fh:
        tot = {k: v["total_len44_reads"] for k, v in json.load(fh).items()}
    return cnt, tot


def pooled_fitness(cnt, tot, g):
    """The authors' pooled log2 enrichment vs WT (combined outputs A+B+C)."""
    c, w = cnt.get(g, {}), cnt[()]
    o = sum(c.get(L, 0) for L in LIBS_OUT)
    i = c.get("in_nodel", 0)
    if o == 0 or i == 0:
        return None
    ow = sum(w[L] for L in LIBS_OUT)
    return float(np.log2((o / i) / (ow / w["in_nodel"])))


def noise_model(cnt, tot, min_count=5):
    """Replicate noise. For each HD 1-2 variant with all three output counts >= min_count:
    F_r = log2((o_r/O_r)/(i/I)) - same for WT; the input cancels in the spread over r.
    Fit E[s^2] = a * mean_r(1/o_r) / ln2^2 + b by least squares (s^2 = sample variance over the 3 replicates).
    Returns a, b, and per-variant data for reporting."""
    w = cnt[()]
    rows = []
    for g, c in cnt.items():
        if len(g) == 0 or len(g) > 2:
            continue
        o = np.array([c.get(L, 0) for L in LIBS_OUT], float)
        i = c.get("in_nodel", 0)
        if (o < min_count).any() or i < 10:
            continue
        ow = np.array([w[L] for L in LIBS_OUT], float)
        Fr = np.log2(o / ow)  # input and totals are common offsets; spread is what matters
        rows.append((Fr.var(ddof=1), np.mean(1 / o) / LN2 ** 2, o.sum(), i))
    s2, x, osum, ii = map(np.array, zip(*rows))
    X = np.column_stack([x, np.ones_like(x)])
    a, b = np.linalg.lstsq(X, s2, rcond=None)[0]
    a, b = max(a, 1.0), max(b, 0.0)  # at least Poisson
    # check of fit: binned observed vs predicted
    q = np.quantile(x, np.linspace(0, 1, 9))
    bins = []
    for lo, hi in zip(q[:-1], q[1:]):
        m = (x >= lo) & (x <= hi)
        bins.append(dict(mean_inv_count=float(x[m].mean() * LN2 ** 2), obs_s2=float(s2[m].mean()),
                         pred_s2=float(a * x[m].mean() + b), n=int(m.sum())))
    c_wt = sum(w[L] for L in LIBS_OUT) / w["in_nodel"]
    return dict(a=float(a), b=float(b), n_variants=int(len(s2)), min_count=min_count, bins=bins,
                c_wt=float(c_wt), wt_counts={k: int(v) for k, v in w.items()})


def sigma_pooled(F, i_in, nm):
    """Noise sd (log2) of a pooled fitness value at fitness F with input count i_in, from the replicate model.
    Expected pooled output count mu = i_in * c_wt * 2^F (floored at 1 read).
    Var = a/ln2^2 * (1/mu + 1/i_in) + b/3  (input overdispersion assumed equal to the outputs' per-read factor a)."""
    mu = np.maximum(np.asarray(i_in, float) * nm["c_wt"] * np.exp2(F), 1.0)
    return np.sqrt(nm["a"] / LN2 ** 2 * (1 / mu + 1 / np.asarray(i_in, float)) + nm["b"] / 3)


def input_layout(cnt):
    """Input counts for the 132 singles (44,4) and all doubles (44,4,44,4) (0 if absent)."""
    I1 = np.zeros((NS, 4))
    I2 = np.zeros((NS, 4, NS, 4))
    for g, c in cnt.items():
        i = c.get("in_nodel", 0)
        if len(g) == 1:
            I1[g[0][0], g[0][1]] = i
        elif len(g) == 2:
            (s1, b1), (s2, b2) = g
            I2[s1, b1, s2, b2] = I2[s2, b2, s1, b1] = i
    return I1, I2


def load_triple_layout(min_in=10):
    """Triple genotypes and their INPUT counts only (layout; output counts are not read here)."""
    G, I = [], []
    with open(os.path.join(COUNTS, "counts_hd3_in_nodel.tsv")) as fh:
        for line in fh:
            _, lab, c = line.rstrip("\n").split("\t")
            c = int(c)
            if c >= min_in:
                g = np.array(WT)
                for s, b in parse_label(lab):
                    g[s] = b
                G.append(g)
                I.append(c)
    return np.array(G, dtype=np.int8), np.array(I, float)


# ------------------------------------------------------------------ fast pair sum
def pair_sum(G, P):
    """sum_{i<j} P[slot_i, slot_j] over the mutated sites of each genotype. P: (176,176) symmetric, 0 diagonal."""
    diff = G != WT
    hd = diff.sum(1)
    m = int(hd.max()) if len(G) else 0
    if m < 2:
        return np.zeros(len(G))
    order = np.argsort(~diff, axis=1, kind="stable")[:, :m]  # mutated sites first
    slots = order * 4 + np.take_along_axis(G, order, 1).astype(np.int64)
    valid = np.arange(m)[None, :] < hd[:, None]
    out = np.zeros(len(G))
    for a in range(m - 1):
        for b in range(a + 1, m):
            v = valid[:, b]
            if not v.any():
                break
            out[v] += P[slots[v, a], slots[v, b]]
    return out


# ------------------------------------------------------------------ the T18b model
def fit_pairs(ge, S, D, sigD, mode="ml"):
    """Empirical-Bayes pair terms on the latent scale for every measured double.

    Observation model per measured double mn: F_obs = g(zhat_mn + E_mn) + eps, eps ~ N(0, sigD_mn^2) (replicate
    noise model), prior E_mn ~ N(0, tau^2). tau^2 by maximum marginal likelihood under the linearisation
    r ~ N(0, k^2 tau^2 + sigma^2) over doubles not at the censoring floor. E_mn: posterior mode (Gauss-Newton on the
    nonlinear g, 30 steps), posterior sd from the curvature at the mode. Unmeasured pairs: 0.
    Returns dict with tau, Ehat (n_d,), Esd (n_d,), index arrays."""
    muts, s_idx, s_y, d1, d2, dy = C.observations(S, D)
    a = ge["x"][:len(muts)]
    zh = ge["z0"] + a[d1] + a[d2]
    lo, hi = ge["lo"], ge["hi"]
    g = lambda z: lo + (hi - lo) * expit(z)  # noqa: E731
    gp = lambda z: (hi - lo) * expit(z) * (1 - expit(z))  # noqa: E731
    sig = np.array([sigD[muts[i][0], muts[i][1], muts[j][0], muts[j][1]] for i, j in zip(d1, d2)])
    r = dy - g(zh)
    k = gp(zh)
    floor = min(S.min(), np.nanmin(D))
    use = dy > floor + 1e-9

    def nll(t):
        v = k[use] ** 2 * t ** 2 + sig[use] ** 2
        return 0.5 * np.sum(np.log(v) + r[use] ** 2 / v)

    tau = float(minimize_scalar(nll, bounds=(0.0, 3.0), method="bounded").x)
    E = np.zeros_like(dy)
    if tau > 1e-6:
        for _ in range(30):
            kz = gp(zh + E)
            rz = dy - g(zh + E)
            # Gauss-Newton step for min (rz^2/sig^2 + E^2/tau^2)
            num = kz * rz / sig ** 2 - E / tau ** 2
            den = kz ** 2 / sig ** 2 + 1 / tau ** 2
            E = E + num / den
        kz = gp(zh + E)
        Esd = 1 / np.sqrt(kz ** 2 / sig ** 2 + 1 / tau ** 2)
    else:
        Esd = np.zeros_like(dy)
    shrink = (k ** 2 * tau ** 2) / (k ** 2 * tau ** 2 + sig ** 2)
    return dict(tau=tau, E=E, Esd=Esd, d1=d1, d2=d2, muts=muts, r=r, k=k, sig=sig,
                mean_shrink_informative=float(shrink[dy > -8].mean()) if np.any(dy > -8) else None)


def pair_matrix(pf, draw_rng=None):
    """176x176 symmetric pair matrix from the EB fit: posterior mode, or one posterior draw if draw_rng is given."""
    vals = pf["E"].copy()
    if draw_rng is not None:
        vals = vals + pf["Esd"] * draw_rng.standard_normal(len(vals))
    P = np.zeros((NS * 4, NS * 4))
    muts = pf["muts"]
    sl = np.array([i * 4 + b for i, b in muts])
    P[sl[pf["d1"]], sl[pf["d2"]]] = vals
    P[sl[pf["d2"]], sl[pf["d1"]]] = vals
    return P


class PairLandscape(C.MeasuredLandscape):
    """T18 primary (measured HD<=2, global curve elsewhere) plus pair terms on the latent scale for HD >= 3."""

    def __init__(self, S, D, ge, P):
        super().__init__(S, D, "ge", ge=ge)
        self.P = P

    def logfit(self, G):
        F = super().logfit(G)
        hd = (G != WT).sum(1)
        big = hd >= 3
        if big.any():
            Gb = G[big]
            z = self.ge["z0"] + self.ge["A"][AR, Gb].sum(1) + pair_sum(Gb, self.P)
            F[big] = C.ge_predict(self.ge, z)
        return F


# ------------------------------------------------------------------ planted truth (fast pair sum; same maths as T18)
class Truth(C.TruthLandscape):
    """T18 truth with sparse pair sums, optional HD>=3 cliff (family F)."""

    def __init__(self, A, E176, sd_h, lo, hi, nu, seed, cliff=None):
        super().__init__(A, np.zeros((NS * 4, NS * 4)), sd_h, lo, hi, nu, seed)
        self.P = np.asarray(E176, float)
        self.cliff = cliff  # None or (log2 level, sd)
        if cliff is not None:
            rng = np.random.default_rng(seed + 1)
            self.R2 = rng.integers(0, 2**63 - 1, size=(NS, 4), dtype=np.int64).astype(np.uint64)

    def latent(self, G):
        z = self.z0 + self.A[AR, G].sum(1) + self._h(G) - self.hwt
        if np.any(self.P):
            z = z + pair_sum(G, self.P)
        return z

    def logfit(self, G):
        F = super().logfit(G)
        if self.cliff is not None:
            big = (G != WT).sum(1) >= 3
            if big.any():
                with np.errstate(over="ignore"):
                    key = self.R2[AR, G[big]].sum(1, dtype=np.uint64)
                    u = (C.splitmix64(key) >> np.uint64(11)).astype(np.float64) / float(2**53)
                u = np.clip(u, 1e-12, 1 - 1e-12)
                F[big] = np.minimum(F[big], self.cliff[0] + self.cliff[1] * ndtri(u))
        return F
