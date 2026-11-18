"""maxRAF detection (Hordijk & Steel 2004 reduction algorithm) and the nulls used by tasks #8 and #6.

A network: n_mol molecules (ids 0..n_mol-1) and a list of reactions, each with
reactants, products and catalysts (lists of molecule ids). A food set is a set of ids.

maxRAF algorithm (Hordijk & Steel 2004, J Theor Biol 227:451, doi:10.1016/j.jtbi.2003.11.020):
  R' <- reactions with at least one catalyst
  repeat: C <- closure of food under R' (a reaction fires when all its reactants are in C)
          R'' <- {r in R': all reactants in C and at least one catalyst in C}
          stop when R'' == R'
The result is the union of all RAFs (empty if there is none).
"""
import itertools

import numpy as np
import scipy.sparse as sp


class Net:
    def __init__(self, n_mol, reactants, products, catalysts):
        self.n_mol = int(n_mol)
        self.reactants = [np.asarray(x, dtype=np.int64) for x in reactants]
        self.products = [np.asarray(x, dtype=np.int64) for x in products]
        self.catalysts = [np.asarray(x, dtype=np.int64) for x in catalysts]
        self.n_rxn = len(self.reactants)
        self._build()

    @staticmethod
    def _inc(lists, n_rxn, n_mol):
        rows = np.repeat(np.arange(n_rxn), [len(x) for x in lists])
        cols = np.concatenate(lists) if len(lists) and sum(len(x) for x in lists) else np.zeros(0, np.int64)
        m = sp.csr_matrix((np.ones(len(cols), dtype=np.int32), (rows, cols)), shape=(n_rxn, n_mol))
        m.data[:] = 1  # collapse duplicates
        return m

    def _build(self):
        self.R = self._inc(self.reactants, self.n_rxn, self.n_mol)
        self.P = self._inc(self.products, self.n_rxn, self.n_mol)
        self.C = self._inc(self.catalysts, self.n_rxn, self.n_mol)
        self.PT = self.P.T.tocsr()

    def copy_with(self, reactants=None, products=None, catalysts=None):
        return Net(self.n_mol, reactants if reactants is not None else self.reactants,
                   products if products is not None else self.products,
                   catalysts if catalysts is not None else self.catalysts)


def food_mask(net, food):
    f = np.zeros(net.n_mol, dtype=bool)
    f[np.asarray(list(food), dtype=np.int64)] = True
    return f


def closure(net, avail0, active):
    """Molecules reachable from avail0 using reactions in `active` (bool mask). Returns (avail, enabled)."""
    avail = avail0.copy()
    act = active.astype(np.int32)
    while True:
        missing = net.R @ (~avail).astype(np.int32)
        enabled = (missing == 0) & active
        new = avail | ((net.PT @ (enabled.astype(np.int32) * act)) > 0)
        if (new == avail).all():
            return avail, enabled
        avail = new


def max_raf(net, food):
    """Return bool mask of reactions in the maxRAF."""
    f = food_mask(net, food) if not isinstance(food, np.ndarray) or food.dtype != bool else food
    active = np.asarray(net.C.sum(axis=1)).ravel() > 0
    while True:
        avail, enabled = closure(net, f, active)
        has_cat = (net.C @ avail.astype(np.int32)) > 0
        keep = active & enabled & has_cat
        if (keep == active).all():
            return keep
        active = keep


# ---------------------------------------------------------------- brute force (correctness check)
def is_raf(net, food_m, subset):
    if not subset:
        return False
    active = np.zeros(net.n_rxn, dtype=bool)
    active[list(subset)] = True
    avail, enabled = closure(net, food_m, active)
    for r in subset:
        if not enabled[r]:
            return False
        if not avail[net.catalysts[r]].any():
            return False
    return True


def brute_max_raf(net, food):
    fm = food_mask(net, food)
    union = set()
    for k in range(1, net.n_rxn + 1):
        for sub in itertools.combinations(range(net.n_rxn), k):
            if set(sub) <= union:
                continue
            if is_raf(net, fm, sub):
                union |= set(sub)
    m = np.zeros(net.n_rxn, dtype=bool)
    m[list(union)] = True
    return m


# ---------------------------------------------------------------- nulls
def _permute_stubs(lists, rng, max_rounds=200):
    """Permute molecule stubs across all slots, keeping each reaction's slot count and each
    molecule's stub count; then repair within-reaction duplicates by random stub swaps."""
    lens = np.array([len(x) for x in lists])
    if lens.sum() == 0:
        return [x.copy() for x in lists]
    stubs = np.concatenate(lists).copy()
    rng.shuffle(stubs)
    owner = np.repeat(np.arange(len(lists)), lens)
    for _ in range(max_rounds):
        # find duplicate (owner, molecule) pairs
        key = owner * (stubs.max() + 1) + stubs
        order = np.argsort(key, kind="stable")
        dup = np.zeros(len(stubs), dtype=bool)
        dup[order[1:]] = key[order[1:]] == key[order[:-1]]
        idx = np.flatnonzero(dup)
        if len(idx) == 0:
            break
        other = rng.integers(0, len(stubs), size=len(idx))
        stubs[idx], stubs[other] = stubs[other], stubs[idx].copy()
    bounds = np.cumsum(lens)[:-1]
    return [np.unique(x) if len(np.unique(x)) < len(x) else x for x in np.split(stubs, bounds)]


def null_rewire(net, rng):
    """N1: degree-preserving rewiring of reactant, product and catalyst edges (each role separately)."""
    return net.copy_with(_permute_stubs(net.reactants, rng), _permute_stubs(net.products, rng),
                         _permute_stubs(net.catalysts, rng))


def null_catalysts(net, rng):
    """N2: keep the substrate network; reassign catalysis edges, degree-preserving."""
    return net.copy_with(catalysts=_permute_stubs(net.catalysts, rng))


def null_food(net, food, rng, pool=None):
    """N3: random food set of equal size drawn uniformly from `pool` (default: every molecule used)."""
    if pool is None:
        used = np.zeros(net.n_mol, dtype=bool)
        for m in (net.R, net.P, net.C):
            used |= np.asarray(m.sum(axis=0)).ravel() > 0
        pool = np.flatnonzero(used)
    return set(rng.choice(pool, size=len(food), replace=False).tolist())


def degree_strata(net):
    """Stratum per molecule: (catalyst-only?, log2 bin of total degree). Unused molecules get -1."""
    dr = np.asarray(net.R.sum(axis=0)).ravel() + np.asarray(net.P.sum(axis=0)).ravel()
    dc = np.asarray(net.C.sum(axis=0)).ravel()
    tot = dr + dc
    strat = np.where(tot > 0, (dr == 0).astype(int) * 100 + np.floor(np.log2(np.maximum(tot, 1))).astype(int), -1)
    return strat


def null_food_matched(net, food, rng, strat=None):
    """N3m: random food set, each food molecule replaced by a random molecule of the same stratum
    (same catalyst-only status, same log2 degree bin), without replacement."""
    if strat is None:
        strat = degree_strata(net)
    out = set()
    for f in sorted(food):
        cand = np.flatnonzero(strat == strat[f])
        cand = np.setdiff1d(cand, np.fromiter(out, dtype=np.int64, count=len(out)))
        out.add(int(rng.choice(cand)) if len(cand) else int(f))
    return out


def null_test(net, food, kind, n_rep, rng, food_pool=None):
    """Observed maxRAF size and the null sizes. kind in {'N1','N2','N3','N3m'}."""
    strat = degree_strata(net) if kind == "N3m" else None
    obs = int(max_raf(net, food).sum())
    sizes = []
    for _ in range(n_rep):
        if kind == "N1":
            sizes.append(int(max_raf(null_rewire(net, rng), food).sum()))
        elif kind == "N2":
            sizes.append(int(max_raf(null_catalysts(net, rng), food).sum()))
        elif kind == "N3":
            sizes.append(int(max_raf(net, null_food(net, food, rng, food_pool)).sum()))
        elif kind == "N3m":
            sizes.append(int(max_raf(net, null_food_matched(net, food, rng, strat)).sum()))
        else:
            raise ValueError(kind)
    sizes = np.array(sizes)
    p_hi = (1 + (sizes >= obs).sum()) / (n_rep + 1)
    p_lo = (1 + (sizes <= obs).sum()) / (n_rep + 1)
    lo, hi = np.percentile(sizes, [2.5, 97.5])
    return dict(obs=obs, null_mean=float(sizes.mean()), null_lo=float(lo), null_hi=float(hi),
                p_hi=float(p_hi), p_lo=float(p_lo), above=bool(p_hi < 0.025), below=bool(p_lo < 0.025))
