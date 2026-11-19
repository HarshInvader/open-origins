"""Clade rules shared by arm L, arm H and baseline B1 (prereg v4 A, B, D).

fast_clade(sp_tree, domain_tips, seed): the deepest clade in one root subtree whose sampled tips are
    15-30% of that domain's sampled tips. "Deepest" = the clade's crown node is closest in time to
    the root (smallest root-to-node distance on the sampled, ultrametric tree). Nodes within 1e-9 of
    the deepest distance are ties, broken by numpy default_rng(seed). Returns the node name.
higher_taxa(sp_tree, domain_tips, target=6, minimum=4): cut the domain's sampled subtree at the
    depth giving `target` clades; if no depth gives exactly `target`, the count nearest to `target`
    among counts >= `minimum` is used (ties: the larger count). Returns a list of tip lists.
"""
import numpy as np


def domain_root(sp_tree, domain_tips):
    return sp_tree.get_common_ancestor(list(domain_tips)) if len(domain_tips) > 1 else sp_tree & list(domain_tips)[0]


def fast_clade(sp_tree, domain_tips, seed, lo=0.15, hi=0.30):
    dom = set(domain_tips)
    droot = domain_root(sp_tree, dom)
    n = len(dom)
    root = sp_tree.get_tree_root()
    cand = []
    for node in droot.traverse():
        if node is droot:
            continue
        k = len(set(node.get_leaf_names()) & dom)
        if lo <= k / n <= hi:
            cand.append((root.get_distance(node), node.name, k))
    if not cand:
        raise RuntimeError("no clade with %g-%g of the domain's %d sampled tips" % (lo, hi, n))
    dmin = min(c[0] for c in cand)
    ties = sorted(c for c in cand if c[0] - dmin <= 1e-9)
    pick = ties[int(np.random.default_rng(seed).integers(len(ties)))] if len(ties) > 1 else ties[0]
    return pick[1], {"depth": pick[0], "n_tips": pick[2], "share": pick[2] / n, "n_ties": len(ties),
                     "n_candidates": len(cand)}


def higher_taxa(sp_tree, domain_tips, target=6, minimum=4):
    dom = set(domain_tips)
    droot = domain_root(sp_tree, dom)
    root = sp_tree.get_tree_root()
    # cut just below each internal node's time: the clades are the children of nodes above the cut
    internal = sorted(((root.get_distance(x), x.name, x) for x in droot.traverse() if not x.is_leaf()), key=lambda v: (v[0], v[1]))
    best = None
    for i in range(len(internal)):
        cut = internal[i][0]
        clades = []
        for x in droot.traverse():
            up = root.get_distance(x.up) if x.up is not None else -1
            if root.get_distance(x) > cut + 1e-12 and up <= cut + 1e-12 and x is not droot:
                clades.append(x)
        c = len(clades)
        if c < minimum:
            continue
        key = (abs(c - target), -c)
        if best is None or key < best[0]:
            best = (key, [sorted(set(x.get_leaf_names()) & dom) for x in clades])
        if c == target:
            break
    if best is None:
        return [sorted(dom)]
    return best[1]
