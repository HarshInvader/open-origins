"""Synthetic metabolism-like networks and planted autocatalytic cores (task #8).

Parameters are our own rough choices at the scale of the Xavier et al. 2020 anaerobic network
(5994 reactions, 5723 metabolites, as reported in that paper); they are not fitted to it.
"""
import numpy as np

from raf import Net


def _zipf_weights(n, s=1.0):
    w = 1.0 / np.arange(1, n + 1) ** s
    return w / w.sum()


def _sizes(rng, n):
    return rng.choice([1, 2, 3], size=n, p=[0.35, 0.45, 0.20])


def background(kind, rng, n_rxn=6000, n_met=5700, n_food=40, n_metal=10, n_cof=30, frac_cat=2 / 3):
    """kind 'R': reactants/products drawn independently (heavy-tailed weights).
    kind 'S': reactions grown outward from the food set, so almost every metabolite is reachable.
    Molecules 0..n_met-1 are metabolites (0 = biggest hub); n_met..n_met+n_metal-1 are 'metals' that
    only catalyse and are in the food set. Catalysis: a random frac_cat of reactions get 1-2 catalysts
    from the metals plus n_cof 'cofactor' metabolites (no planted structure).
    Returns (net, food set)."""
    w = _zipf_weights(n_met)
    hubs = list(range(20))
    food_met = hubs + list(rng.choice(np.arange(20, n_met), size=n_food - 20 - n_metal, replace=False))
    metals = list(range(n_met, n_met + n_metal))
    food = set(int(x) for x in food_met) | set(metals)
    nr, npd = _sizes(rng, n_rxn), _sizes(rng, n_rxn)
    reactants, products = [], []
    if kind == "R":
        for a, b in zip(nr, npd):
            m = rng.choice(n_met, size=a + b, replace=False, p=w)
            reactants.append(m[:a]); products.append(m[a:])
    elif kind == "S":
        avail = list(food_met)
        made = set(avail)
        order = [i for i in range(n_met) if i not in made]
        rng.shuffle(order)
        nxt = 0
        for a, b in zip(nr, npd):
            av = np.array(avail)
            pw = w[av] / w[av].sum()
            r = rng.choice(av, size=min(a, len(av)), replace=False, p=pw)
            prods = []
            for _ in range(b):
                if nxt < len(order) and rng.random() < 0.6:
                    prods.append(order[nxt]); nxt += 1
                else:
                    prods.append(int(rng.choice(av, p=pw)))
            prods = np.unique([p for p in prods if p not in set(r.tolist())])
            if len(prods) == 0:
                prods = np.array([order[nxt] if nxt < len(order) else int(rng.choice(n_met))]); nxt += 1
            for p in prods:
                if p not in made:
                    made.add(int(p)); avail.append(int(p))
            reactants.append(r); products.append(prods.astype(np.int64))
    else:
        raise ValueError(kind)
    cof = list(rng.choice(np.setdiff1d(np.arange(20, n_met), food_met), size=n_cof, replace=False))
    pool = np.array(metals + cof)
    cw = _zipf_weights(len(pool), 0.8)
    rng.shuffle(cw)
    catalysts = []
    for _ in range(n_rxn):
        if rng.random() < frac_cat:
            k = 1 if rng.random() < 0.7 else 2
            catalysts.append(rng.choice(pool, size=k, replace=False, p=cw))
        else:
            catalysts.append(np.zeros(0, np.int64))
    return Net(n_met + n_metal, reactants, products, catalysts), food


def plant_core(net, food, k, rng):
    """Add a k-reaction RAF on k new molecules: reaction j consumes 1-2 molecules from the food
    hubs and earlier core products, makes core molecule j, and is catalysed by a random core molecule.
    Returns (new net, food, indices of planted reactions)."""
    base = net.n_mol
    food_l = sorted(food)
    reactants = list(net.reactants); products = list(net.products); catalysts = list(net.catalysts)
    idx = []
    for j in range(k):
        pool = food_l[:20] + [base + i for i in range(j)]
        a = 1 if j == 0 or rng.random() < 0.5 else 2
        r = [int(rng.choice(food_l[:20]))] if j == 0 else list(rng.choice(pool, size=a, replace=False))
        if j > 0 and not any(x >= base for x in r):
            r[-1] = base + int(rng.integers(0, j))  # keep the core connected
        reactants.append(np.unique(np.array(r, dtype=np.int64)))
        products.append(np.array([base + j], dtype=np.int64))
        catalysts.append(np.array([base + int(rng.integers(0, k))], dtype=np.int64))
        idx.append(len(reactants) - 1)
    return Net(base + k, reactants, products, catalysts), food, np.array(idx)
