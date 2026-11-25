"""T18 core: landscapes, global-epistasis fit and the population Monte Carlo error-threshold estimator.

Nothing in this file reads the decision quantity; it is imported by t18_analysis.py.

Genotype: 44 sites (QT45 positions 2-45, the sites in the deposited landscape), base index 0..3 = A,C,G,T.
Fitness F is log2 relative replication rate (WT = 0), as in the authors' quasispecies model
(rate = 2**F, Zenodo QTribozyme_quasispecies, QT_quasispecies_dynamics.py).

Threshold definition (D3 in the prereg): genotypes with F <= log2(w_dead) form an absorbing "dead" class that
replicates at w_dead (the authors' lump, rate 0.01). The active quasispecies persists iff the Perron root
lambda_A of the active block of W = Q A exceeds w_dead. e* is the per-nucleotide, per-strand error rate at
which lambda_A(e*) = w_dead.
"""
import os
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.special import expit, ndtri

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
EXPS = os.path.dirname(STUDY)
sys.path.insert(0, os.path.join(EXPS, "qt45_epistasis"))
import epistasis as E30  # noqa: E402  (#30 loaders: load(), make_g(), WT_SEQ)

BASES = "ACGT"
WT_SEQ = E30.WT_SEQ
NS = len(WT_SEQ)  # 44
WT = np.array([BASES.index(c) for c in WT_SEQ], dtype=np.int8)
AR = np.arange(NS)
FLOOR = -14.0
TRANS = np.array([2, 3, 0, 1], dtype=np.int8)  # A<->G, C<->T


# ------------------------------------------------------------------ data
def load_real():
    """Singles S (44,4; 0 at WT base) and doubles D (44,4,44,4; nan if unmeasured, symmetric)."""
    singles, doubles = E30.load()
    S = np.zeros((NS, 4))
    for (pos, mt), f in singles.items():
        S[pos - 2, BASES.index(mt)] = f
    D = np.full((NS, 4, NS, 4), np.nan)
    for a, b, f in doubles:
        i, bi = a[0] - 2, BASES.index(a[1])
        j, bj = b[0] - 2, BASES.index(b[1])
        D[i, bi, j, bj] = f
        D[j, bj, i, bi] = f
    return S, D, len(singles), len(doubles)


def mutation_list():
    """The 132 single mutations as (site, base)."""
    return [(i, b) for i in range(NS) for b in range(4) if b != WT[i]]


def observations(S, D):
    """Flatten singles + measured doubles into index arrays for fitting."""
    muts = mutation_list()
    mid = {m: k for k, m in enumerate(muts)}
    s_idx = np.array([mid[m] for m in muts])
    s_y = np.array([S[i, b] for i, b in muts])
    d1, d2, dy = [], [], []
    for (i, bi) in muts:
        for (j, bj) in muts:
            if j <= i:
                continue
            v = D[i, bi, j, bj]
            if np.isfinite(v):
                d1.append(mid[(i, bi)])
                d2.append(mid[(j, bj)])
                dy.append(v)
    return muts, s_idx, s_y, np.array(d1), np.array(d2), np.array(dy)


# ------------------------------------------------------------------ global-epistasis fit (method)
def fit_ge(S, D, x0=None):
    """Latent additive model through one 4-parameter logistic: F = lo + (hi-lo)*expit(z0 + sum a).

    Fitted by least squares to singles, measured doubles and WT (=0, weight 10). Returns dict.
    """
    muts, s_idx, s_y, d1, d2, dy = observations(S, D)
    M = len(muts)
    ns, nd = len(s_y), len(dy)

    def unpack(p):
        return p[:M], p[M], p[M + 1], p[M + 2]

    def resid(p):
        a, z0, lo, hi = unpack(p)
        zs = z0 + a[s_idx]
        zd = z0 + a[d1] + a[d2]
        g = lambda z: lo + (hi - lo) * expit(z)  # noqa: E731
        return np.concatenate([g(zs) - s_y, g(zd) - dy, [10.0 * g(z0)]])

    def jac(p):
        a, z0, lo, hi = unpack(p)
        J = np.zeros((ns + nd + 1, M + 3))
        zs = z0 + a[s_idx]
        zd = z0 + a[d1] + a[d2]
        for rows, z, cols in ((np.arange(ns), zs, [s_idx]), (ns + np.arange(nd), zd, [d1, d2])):
            sg = expit(z)
            dz = (hi - lo) * sg * (1 - sg)
            for c in cols:
                np.add.at(J, (rows, c), dz)
            J[rows, M] = dz
            J[rows, M + 1] = 1 - sg
            J[rows, M + 2] = sg
        sg0 = expit(z0)
        J[-1, M] = 10 * (hi - lo) * sg0 * (1 - sg0)
        J[-1, M + 1] = 10 * (1 - sg0)
        J[-1, M + 2] = 10 * sg0
        return J

    if x0 is None:
        lo0, hi0 = FLOOR, 2.5
        z00 = np.log(-lo0 / hi0)  # expit(z0)= -lo/(hi-lo)
        a0 = np.clip(s_y / 3.0, -6, 2)
        x0 = np.concatenate([a0, [z00, lo0, hi0]])
    r = least_squares(resid, x0, jac=jac, method="trf", max_nfev=400, x_scale="jac")
    a, z0, lo, hi = unpack(r.x)
    A = np.zeros((NS, 4))
    for k, (i, b) in enumerate(muts):
        A[i, b] = a[k]
    res = r.fun[:-1]
    return dict(A=A, z0=float(z0), lo=float(lo), hi=float(hi), x=r.x,
                resid_single=res[:ns], resid_double=res[ns:], fitted_double=(res[ns:] + dy),
                d_obs=dy, s_obs=s_y, cost=float(r.cost), success=bool(r.success))


def ge_predict(ge, z):
    return ge["lo"] + (ge["hi"] - ge["lo"]) * expit(z)


# ------------------------------------------------------------------ landscapes
class MeasuredLandscape:
    """Measured values for HD<=2 where available; a model for everything else (the method).

    model: 'ge' (latent global epistasis, primary), 'iso30' (#30 isotonic curve on the sum of observed
    singles), 'additive' (sum of observed singles, floored), 'authors' (HD>=3 and unmeasured doubles
    = log2(0.01), as in the authors' model).
    """

    def __init__(self, S, D, model, ge=None, iso=None, use_measured=True):
        self.S, self.D, self.model, self.ge, self.iso = S, D, model, ge, iso
        self.use_measured = use_measured
        self.Dflat = D.reshape(NS * 4, NS * 4)

    def logfit(self, G):
        diff = G != WT
        hd = diff.sum(1)
        phi = self.S[AR, G].sum(1)
        if self.model == "ge":
            F = ge_predict(self.ge, self.ge["z0"] + self.ge["A"][AR, G].sum(1))
        elif self.model == "iso30":
            F = self.iso(phi)
        elif self.model == "additive":
            F = np.maximum(phi, FLOOR)
        elif self.model == "authors":
            F = np.full(len(G), np.log2(0.01))
        else:
            raise ValueError(self.model)
        F = np.asarray(F, float)
        if self.use_measured:
            F[hd == 0] = 0.0
            one = hd == 1
            F[one] = phi[one]
            two = np.nonzero(hd == 2)[0]
            if len(two):
                r, c = np.nonzero(diff[two])
                c = c.reshape(-1, 2)
                bb = G[two[:, None], c]
                v = self.Dflat[c[:, 0] * 4 + bb[:, 0], c[:, 1] * 4 + bb[:, 1]]
                ok = np.isfinite(v)
                F[two[ok]] = v[ok]
        return F


def splitmix64(x):
    x = (x + np.uint64(0x9E3779B97F4A7C15))
    x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
    x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
    return x ^ (x >> np.uint64(31))


class TruthLandscape:
    """Synthetic full-sequence-space landscape (planted check).

    z = z0 + sum a + sum_{pairs} E + h(genotype) - h(WT);  F = Richards curve of z (lo..hi), WT exactly 0.
    h is a hash-based random field (uncorrelated higher-order epistasis, 'rough Mount Fuji' term).
    """

    def __init__(self, A, E176, sd_h, lo, hi, nu, seed):
        self.A, self.E, self.sd_h, self.lo, self.hi, self.nu = A, E176.astype(np.float32), sd_h, lo, hi, nu
        rng = np.random.default_rng(seed)
        self.R = rng.integers(0, 2**63 - 1, size=(NS, 4), dtype=np.int64).astype(np.uint64)
        # choose z0 so that F(WT)=0 with h(WT) removed below
        frac = (0 - lo) / (hi - lo)
        # Richards: F = lo + (hi-lo) * expit(z)**(1/nu)  ->  expit(z0) = frac**nu
        p = frac ** nu
        self.z0 = float(np.log(p / (1 - p)))
        self.hwt = 0.0
        self.hwt = float(self._h(WT[None, :])[0])

    def _h(self, G):
        if self.sd_h == 0:
            return np.zeros(len(G))
        with np.errstate(over="ignore"):
            key = self.R[AR, G].sum(1, dtype=np.uint64)
            u = (splitmix64(key) >> np.uint64(11)).astype(np.float64) / float(2**53)
        u = np.clip(u, 1e-12, 1 - 1e-12)
        return self.sd_h * ndtri(u)

    def latent(self, G):
        z = self.z0 + self.A[AR, G].sum(1)
        if np.any(self.E):
            idx = AR * 4 + G  # (n,44)
            H = np.zeros((len(G), NS * 4), dtype=np.float32)
            np.put_along_axis(H, idx.astype(np.int64), 1.0, axis=1)
            z = z + 0.5 * np.einsum("ij,ij->i", H @ self.E, H)
        z = z + self._h(G) - self.hwt
        return z

    def logfit(self, G):
        z = self.latent(G)
        return self.lo + (self.hi - self.lo) * expit(z) ** (1.0 / self.nu)


class SinglePeak:
    """Analytic check: WT rate 1, every mutant dead (or neutral on `neutral` sites)."""

    def __init__(self, neutral=()):
        self.neutral = np.zeros(NS, bool)
        self.neutral[list(neutral)] = True

    def logfit(self, G):
        bad = ((G != WT) & ~self.neutral).any(1)
        return np.where(bad, -np.inf, 0.0)


class SiteIndependent:
    """Analytic check without killing: log2 fitness additive over sites (multiplicative rates)."""

    def __init__(self, Ssite):
        self.Ssite = Ssite

    def logfit(self, G):
        return self.Ssite[AR, G].sum(1)


def site_independent_lambda(Ssite, e, spectrum="uniform"):
    """Exact Perron root of the product of per-site 4x4 matrices Q_site @ diag(2**S_site)."""
    lam = 1.0
    P = site_transition(e, spectrum)
    for i in range(NS):
        W = P @ np.diag(2.0 ** Ssite[i])  # column j: parent base j
        lam *= np.max(np.real(np.linalg.eigvals(W)))
    return lam


# ------------------------------------------------------------------ mutation model
def site_transition(e, spectrum="uniform"):
    """Composite (+)->(-)->(+) per-site transition matrix P[child, parent] for per-strand error e."""
    if spectrum == "uniform":
        step = np.full((4, 4), e / 3.0)
        np.fill_diagonal(step, 1 - e)
        # complement then copy back: with a symmetric uniform table the composite is step @ step
        return step @ step
    if spectrum == "transition":
        step = np.zeros((4, 4))
        for b in range(4):
            step[b, b] = 1 - e
            step[TRANS[b], b] = e
        return step @ step
    raise ValueError(spectrum)


def change_prob(e, spectrum="uniform"):
    return 1.0 - site_transition(e, spectrum)[0, 0]


def mutate(G, u, spectrum, rng):
    K = G.copy()
    m = rng.random(K.shape) < u
    if spectrum == "uniform":
        K[m] = (K[m] + rng.integers(1, 4, size=int(m.sum()), dtype=np.int8)) % 4
    else:
        K[m] = TRANS[K[m]]
    return K


# ------------------------------------------------------------------ estimator
def lambda_at(land, e, pop, rng, w_dead, k=5, T=60, burn=20, tau=1.0, spectrum="uniform",
              Fpop=None, min_alive=50):
    """Population Monte Carlo estimate of the Perron root of the active block at error rate e.

    Returns (lam, pop, Fpop, info). Dead = F <= log2(w_dead) (absorbing). w_dead=0 -> no killing.
    """
    N = len(pop)
    u = change_prob(e, spectrum)
    cut = np.log2(w_dead) if w_dead > 0 else -np.inf
    if Fpop is None:
        Fpop = land.logfit(pop)
    logs, alive_fr = [], []
    for t in range(T):
        w = np.exp2(Fpop / tau)
        wm = w.mean()
        par = rng.choice(N, size=N * k, p=w / w.sum())
        kids = mutate(pop[par], u, spectrum, rng)
        Fk = land.logfit(kids)
        alive = Fk > cut
        na = int(alive.sum())
        if na < min_alive:
            return 0.0 if na == 0 else float(wm * na / (N * k)), pop, Fpop, dict(extinct=True, t=t, n_alive=na)
        lam_t = wm * na / (N * k)
        sel = np.nonzero(alive)[0][rng.integers(0, na, N)]
        pop, Fpop = kids[sel], Fk[sel]
        if t >= burn:
            logs.append(np.log(lam_t))
            alive_fr.append(na / (N * k))
    lam = float(np.exp(np.mean(logs)))
    hd = (pop != WT).sum(1)
    info = dict(extinct=False, lam_sd_log=float(np.std(logs)), alive_frac=float(np.mean(alive_fr)),
                mean_hd=float(hd.mean()), frac_w_ge_08=float(np.mean(np.exp2(Fpop / tau) >= 0.8)),
                mean_w=float(np.exp2(Fpop / tau).mean()))
    return lam, pop, Fpop, info


E_GRID = [0.01, 0.02, 0.03, 0.045, 0.06, 0.08, 0.10, 0.125, 0.15, 0.20, 0.25]


def threshold(land, rng, w_dead=0.01, N=10000, k=5, tau=1.0, spectrum="uniform", grid=E_GRID,
              T0=100, burn0=50, T=60, burn=20, refine=True):
    """e* where lambda_A(e) = w_dead. Ascending warm-started grid, stop after the first crossing,
    one refinement point, log-linear interpolation. Returns dict (e_star may be '<min' or '>max')."""
    pop = np.tile(WT, (N, 1))
    Fpop = None
    pts = []
    target = np.log(w_dead)
    first = True
    for e in grid:
        lam, pop, Fpop, info = lambda_at(land, e, pop, rng, w_dead, k=k, T=T0 if first else T,
                                         burn=burn0 if first else burn, tau=tau, spectrum=spectrum, Fpop=Fpop)
        first = False
        pts.append((e, lam, info))
        if lam <= w_dead or info.get("extinct"):
            break
    out = dict(points=[(e, lam, {k2: v for k2, v in inf.items()}) for e, lam, inf in pts])
    lams = [p[1] for p in pts]
    if lams[0] <= w_dead:
        out["e_star"] = None
        out["censored"] = "below_min"
        return out
    if lams[-1] > w_dead:
        out["e_star"] = None
        out["censored"] = "above_max"
        return out

    def interp(p_lo, p_hi):
        # log lambda is close to linear in x = log(1-u(e)) (exactly so for a single peak); interpolate there
        (e1, l1), (e2, l2) = p_lo, p_hi
        if l2 <= 0:
            return 0.5 * (e1 + e2)
        x1, x2 = np.log(1 - change_prob(e1, spectrum)), np.log(1 - change_prob(e2, spectrum))
        y1, y2 = np.log(l1) - target, np.log(l2) - target
        xs = x1 + (x2 - x1) * y1 / (y1 - y2)
        ee = np.linspace(e1, e2, 2001)
        xx = np.log(1 - np.array([change_prob(v, spectrum) for v in ee]))
        return float(ee[np.argmin(np.abs(xx - xs))])

    lo_pt, hi_pt = (pts[-2][0], pts[-2][1]), (pts[-1][0], pts[-1][1])
    e_est = interp(lo_pt, hi_pt)
    if refine:
        # one extra point at the interpolated e*, equilibrated from WT
        pop2 = np.tile(WT, (N, 1))
        lam_r, _, _, info_r = lambda_at(land, e_est, pop2, rng, w_dead, k=k, T=T0, burn=burn0, tau=tau,
                                        spectrum=spectrum)
        out["refine"] = (e_est, lam_r, info_r)
        if lam_r > w_dead and not info_r.get("extinct"):
            e_est = interp((e_est, lam_r), hi_pt)
        elif lam_r > 0:
            e_est = interp(lo_pt, (e_est, lam_r))
        else:
            e_est = 0.5 * (lo_pt[0] + e_est)
    out["e_star"] = e_est
    out["censored"] = None
    return out


def lambda_profile(land, rng, es, w_dead=0.01, N=10000, k=5, tau=1.0, spectrum="uniform", T=100, burn=50):
    """lambda_A at a fixed list of e (each from WT). Used for lambda_A(e_measured) reporting."""
    res = []
    for e in es:
        pop = np.tile(WT, (N, 1))
        lam, _, _, info = lambda_at(land, e, pop, rng, w_dead, k=k, T=T, burn=burn, tau=tau, spectrum=spectrum)
        res.append(dict(e=e, lam=lam, **info))
    return res
