"""T19 gate G1: is the atom-balanced null free enough to decide anything? Structure only, no RAF.

Prereg: docs/prereg/t19_raf_atom_balanced.md, section "Gate G1". This script computes nothing
about autocatalytic sets, so it cannot peek at the result. It reports, for the Xavier 2020
dataset S4: how many reactions balance as deposited, how many are movable, the total-formula
class sizes, and the mixing of 20 pilot draws of null N1b.

G1 passes only if mean share changed >= 0.30 and mean Jaccard < 0.80.

Run from the repo root:  python3 -I experiments/raf_null/scripts/t19_gate1.py
Writes experiments/raf_null/scripts_out/t19_gate1.json
"""
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
SRC = EXP / "raw" / "rspb20192377supp5.txt"
FORMULAS = EXP / "formulas.tsv"
OUT = EXP / "scripts_out" / "t19_gate1.json"

PSEUDO = {"Pooling", "Spontaneous"}
CID = re.compile(r"^C\d{5}$")
ELEM = re.compile(r"([A-Z][a-z]?)(\d*)")
GENERIC = re.compile(r"[RXn]")
N_PILOT = 20
SEED = 20261126


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_formula(f):
    """'C10H16N5O13P3' -> Counter. Returns None if it is generic or does not parse cleanly."""
    if not f or GENERIC.search(f):
        return None
    # reject anything with brackets, dots or charges: those are not plain element strings
    if re.search(r"[^A-Za-z0-9]", f):
        return None
    c = Counter()
    pos = 0
    for m in ELEM.finditer(f):
        if m.start() != pos:
            return None
        pos = m.end()
        c[m.group(1)] += int(m.group(2)) if m.group(2) else 1
    if pos != len(f):
        return None
    return c


def parse_side(side):
    """'C00473 + 2 C00003' -> list of (coef, molecule). Molecule names may contain spaces."""
    out = []
    for term in side.split(" + "):
        t = term.strip()
        if not t:
            continue
        m = re.match(r"^(\d+)\s+(.+)$", t)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
        else:
            out.append((1, t))
    return out


def load():
    sec = None
    name_to_id, reactions = {}, []
    with open(SRC, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            t = line.strip()
            if t.startswith("<") and t.endswith(">"):
                sec = t
                continue
            if not t:
                continue
            parts = line.rstrip("\n").split("\t")
            if sec == "<molecules>":
                if len(parts) > 1 and CID.fullmatch(parts[1].strip()):
                    for nm in parts[0].split(";"):
                        name_to_id[nm.strip()] = parts[1].strip()
            elif sec == "<reactions>":
                if len(parts) < 2:
                    continue
                rid, eq = parts[0].strip(), parts[1].strip()
                rev = "<=>" in eq
                sep = "<=>" if rev else "=>"
                if sep not in eq:
                    continue
                lhs, rhs = eq.split(sep, 1)
                reactions.append({"id": rid, "rev": rev,
                                  "lhs": parse_side(lhs), "rhs": parse_side(rhs)})
    return name_to_id, reactions


def comp(side, formula_of):
    """Summed elemental composition of a side, or None if any molecule has no definite formula."""
    total = Counter()
    for coef, mol in side:
        f = formula_of.get(mol)
        if f is None:
            return None
        for el, n in f.items():
            total[el] += coef * n
    return total


def key(c):
    return tuple(sorted(c.items()))


def sig(side):
    return frozenset((coef, mol) for coef, mol in side)


def main():
    if not FORMULAS.exists():
        print("missing %s; run t19_fetch_formulas.py first" % FORMULAS, file=sys.stderr)
        return 2
    raw_formula = {}
    for line in FORMULAS.read_text().splitlines():
        p = line.split("\t")
        if len(p) == 2:
            raw_formula[p[0]] = p[1]

    name_to_id, reactions = load()
    # molecule name -> Counter, for every molecule we can resolve to a definite formula
    formula_of, bad_reason = {}, Counter()
    names = {mol for r in reactions for side in (r["lhs"], r["rhs"]) for _, mol in side}
    for mol in names:
        if mol in PSEUDO:
            bad_reason["pseudo_token"] += 1
            continue
        cid = mol if CID.fullmatch(mol) else name_to_id.get(mol)
        if cid is None:
            bad_reason["no_kegg_id"] += 1
            continue
        f = raw_formula.get(cid)
        if f is None:
            bad_reason["no_formula_line"] += 1
            continue
        c = parse_formula(f)
        if c is None:
            bad_reason["generic_or_unparsed"] += 1
            continue
        formula_of[mol] = c

    balanced, movable, excl = [], [], Counter()
    for r in reactions:
        cl, cr = comp(r["lhs"], formula_of), comp(r["rhs"], formula_of)
        if cl is None or cr is None:
            excl["formula_less_molecule"] += 1
            continue
        if key(cl) != key(cr):
            excl["unbalanced_as_deposited"] += 1
            continue
        balanced.append(r)
        r["tf"] = key(cl)
        movable.append(r)

    classes = defaultdict(list)
    for r in movable:
        classes[r["tf"]].append(r)
    sizes = Counter(len(v) for v in classes.values())
    singletons = sum(len(v) for v in classes.values() if len(v) == 1)

    # real directed reaction set, over the whole network (fixed reactions included)
    def directed(rs):
        s = set()
        for r in rs:
            s.add((sig(r["lhs"]), sig(r["rhs"])))
            if r["rev"]:
                s.add((sig(r["rhs"]), sig(r["lhs"])))
        return s

    real_all = directed(reactions)
    fixed = [r for r in reactions if "tf" not in r]

    rng = random.Random(SEED)
    shares, jaccards = [], []
    for _ in range(N_PILOT):
        new = []
        for tf, group in classes.items():
            rhs = [r["rhs"] for r in group]
            perm = rhs[:]
            rng.shuffle(perm)
            for r, newrhs in zip(group, perm):
                new.append({"id": r["id"], "rev": r["rev"], "lhs": r["lhs"], "rhs": newrhs})
        copy_all = directed(new + fixed)
        changed = sum(1 for d in real_all if d not in copy_all)
        shares.append(changed / len(real_all))
        jaccards.append(len(real_all & copy_all) / len(real_all | copy_all))

    mean_share = sum(shares) / len(shares)
    mean_jac = sum(jaccards) / len(jaccards)
    movable_share = len(movable) / len(reactions)
    res = {
        "mode": "t19_gate1_structure_only",
        "inputs": {"dataset_s4_sha256": sha256(SRC), "formulas_sha256": sha256(FORMULAS)},
        "n_reactions": len(reactions),
        "n_molecules_in_reactions": len(names),
        "n_molecules_with_formula": len(formula_of),
        "molecules_excluded": dict(bad_reason),
        "n_balanced_as_deposited": len(balanced),
        "share_balanced": len(balanced) / len(reactions),
        "reactions_excluded": dict(excl),
        "n_movable": len(movable),
        "share_movable": movable_share,
        "n_total_formula_classes": len(classes),
        "class_size_histogram_top": dict(sorted(sizes.items())[:12]),
        "largest_classes": sorted((len(v) for v in classes.values()), reverse=True)[:6],
        "n_movable_in_singleton_class": singletons,
        "n_real_directed": len(real_all),
        "pilot_draws": N_PILOT,
        "mean_share_changed": mean_share,
        "mean_jaccard": mean_jac,
        "g1_thresholds": {"min_share_changed": 0.30, "max_jaccard": 0.80},
        "g1_pass": bool(mean_share >= 0.30 and mean_jac < 0.80),
        "f1_note": ("fewer than 60% of reactions are movable; F1 applies and the share held "
                    "fixed goes in the headline") if movable_share < 0.60 else "F1 not triggered",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    print("wrote %s" % OUT.relative_to(EXP.parent.parent))
    return 0


if __name__ == "__main__":
    sys.exit(main())
