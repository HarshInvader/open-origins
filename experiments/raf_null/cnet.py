"""Reaction network with reversible reactions and AND/OR catalysis, maxRAF and nulls (task #6).

Same Hordijk-Steel reduction as experiments/raf/raf.py, generalised to catalyst clauses
(a reaction is catalysed if every molecule of at least one clause is in the closure) and to
reversible reactions (split into two directed reactions sharing one id).
"""
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "raf"))
from raf import _permute_stubs  # noqa: E402


class CNet:
    """lhs, rhs: list of int arrays; rev: bool array; cats: list (per reaction) of list of int arrays (clauses)."""

    def __init__(self, n_mol, lhs, rhs, rev, cats):
        self.n_mol, self.lhs, self.rhs, self.rev, self.cats = n_mol, lhs, rhs, np.asarray(rev, bool), cats
        self.n = len(lhs)
        src, dst, owner = [], [], []
        for i in range(self.n):
            src.append(lhs[i]); dst.append(rhs[i]); owner.append(i)
            if self.rev[i]:
                src.append(rhs[i]); dst.append(lhs[i]); owner.append(i)
        self.owner = np.array(owner)
        nd = len(owner)
        self.nd = nd
        self.R = self._inc(src, nd)
        self.PT = self._inc(dst, nd).T.tocsr()
        cl, cl_dir = [], []
        for d, i in enumerate(owner):
            for c in cats[i]:
                cl.append(c); cl_dir.append(d)
        self.K = self._inc(cl, len(cl))
        self.cl_dir = np.array(cl_dir, dtype=np.int64)

    def _inc(self, lists, nrow):
        rows = np.repeat(np.arange(nrow), [len(x) for x in lists])
        cols = np.concatenate([np.asarray(x, np.int64) for x in lists]) if lists else np.zeros(0, np.int64)
        m = sp.csr_matrix((np.ones(len(cols), np.int32), (rows, cols)), shape=(nrow, self.n_mol))
        m.data[:] = 1
        return m


def max_raf(net, food_mask):
    """Bool mask over undirected reactions: in the maxRAF (either direction)."""
    has_any = np.bincount(net.cl_dir, minlength=net.nd) > 0
    active = has_any.copy()
    while True:
        avail = food_mask.copy()
        while True:
            enabled = ((net.R @ (~avail).astype(np.int32)) == 0) & active
            new = avail | ((net.PT @ enabled.astype(np.int32)) > 0)
            if (new == avail).all():
                break
            avail = new
        ok = (net.K @ (~avail).astype(np.int32)) == 0
        has_cat = np.bincount(net.cl_dir[ok], minlength=net.nd) > 0
        keep = active & enabled & has_cat
        if (keep == active).all():
            out = np.zeros(net.n, bool)
            out[net.owner[keep]] = True
            return out
        active = keep


def rewire(net, rng, fixed_rxn, fixed_mol, mode):
    """mode 'N1': rewire lhs, rhs and catalyst stubs; 'N2': catalyst stubs only.
    Reactions in fixed_rxn and clauses containing a molecule in fixed_mol are not touched."""
    free = [i for i in range(net.n) if i not in fixed_rxn]
    lhs, rhs = list(net.lhs), list(net.rhs)
    if mode == "N1":
        nl = _permute_stubs([net.lhs[i] for i in free], rng)
        nr = _permute_stubs([net.rhs[i] for i in free], rng)
        for j, i in enumerate(free):
            lhs[i], rhs[i] = nl[j], nr[j]
    slots = [(i, k) for i in free for k, c in enumerate(net.cats[i]) if not (set(c.tolist()) & fixed_mol)]
    newc = _permute_stubs([net.cats[i][k] for i, k in slots], rng)
    cats = [list(c) for c in net.cats]
    for (i, k), c in zip(slots, newc):
        cats[i][k] = c
    return CNet(net.n_mol, lhs, rhs, net.rev, cats)
