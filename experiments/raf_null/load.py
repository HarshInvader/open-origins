"""Parse the Xavier et al. 2020 dataset S4 (CatlyNet-style text) into a directed network for raf.py.

Format (as found in rspb20192377supp5.txt): sections <molecules>, <food set>, <reactions>.
Reaction line: id TAB "a + 2 b <=> c" (or =>) TAB catalyst expression TAB weight.
Catalyst expression: space = OR, & = AND (binds tighter), parentheses group. Converted to DNF clauses.
Reversible (<=>) reactions become two directed reactions with the same id and catalysts.
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "raf"))

PSEUDO = {"Pooling", "Spontaneous"}


def _tok(expr):
    return re.findall(r"\(|\)|&|[^\s()&]+", expr)


def parse_cat(expr):
    """Return DNF: list of frozensets."""
    toks = _tok(expr.strip())
    pos = 0

    def expression():
        nonlocal pos
        terms = [term()]
        while pos < len(toks) and toks[pos] not in (")",):
            terms.append(term())
        out = []
        for t in terms:
            out.extend(t)
        return out

    def term():
        nonlocal pos
        dnf = factor()
        while pos < len(toks) and toks[pos] == "&":
            pos += 1
            other = factor()
            dnf = [a | b for a in dnf for b in other]
        return dnf

    def factor():
        nonlocal pos
        t = toks[pos]
        if t == "(":
            pos += 1
            d = expression()
            assert toks[pos] == ")", expr
            pos += 1
            return d
        pos += 1
        return [frozenset([t])]

    if not toks:
        return []
    d = expression()
    assert pos == len(toks), expr
    uniq = []
    for c in d:  # drop clauses that are supersets of others
        if not any(o < c for o in d) and c not in uniq:
            uniq.append(c)
    return uniq


def _side(s):
    out = []
    for term in s.split(" + "):
        parts = term.strip().split()
        if parts:
            out.append(parts[-1])
    return out


def read(path):
    sec = None
    food, rxns = [], []
    for line in Path(path).read_text().splitlines():
        if line.startswith("<") and line.endswith(">") and "\t" not in line:
            sec = line.strip("<>")
            continue
        if not line.strip():
            continue
        if sec == "food set":
            food.append(line.split("\t")[-1].strip())
        elif sec == "reactions":
            rid, eq, cat, *_ = line.split("\t")
            rev = "<=>" in eq
            lhs, rhs = re.split(r"\s*<=>\s*|\s*=>\s*", eq)
            rxns.append(dict(id=rid, lhs=_side(lhs), rhs=_side(rhs), rev=rev, cat=parse_cat(cat)))
    return food, rxns
