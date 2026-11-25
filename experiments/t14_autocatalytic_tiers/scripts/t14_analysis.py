"""T14 (prereg docs/prereg/t14_autocatalytic_tiers.md): is the tiered autocatalytic structure of
biochemistry more than its degree sequence gives?

Claim under test: Peng, Linderoth & Baum 2022, PLoS Comput Biol 18(9):e1010498,
doi:10.1371/journal.pcbi.1010498 (PMC9491600): "We found that the abiotic and biochemical networks share
multiple properties, including hierarchically organized SDASs converting simple materials and energy to
more complex species."  In the biochemical network, "304 of the 4186 non-tier-0 species are singleton
supported seeds", in three cliques whose SDASs (301, 357, 1414 species) "are nested".

Usage (single process, single thread; run under nice -n 20 with OMP/OPENBLAS threads = 1):
  python -I t14_analysis.py <experiments/t14_autocatalytic_tiers dir> gate
  python -I t14_analysis.py <dir> timing                       # synthetic networks only
  python -I t14_analysis.py <dir> planted <SCEN> <REP_FROM> <REP_TO>   # synthetic networks only
  python -I t14_analysis.py <dir> planted_merge
  python -I t14_analysis.py <dir> sealcheck
  python -I t14_analysis.py <dir> dryrun <DB> <NULL> <FROM> <TO>  # `real` code; one rewire of each network
  python -I t14_analysis.py <dir> dryrun_verdict               #   stands in for it; prints flags only
  python -I t14_analysis.py <dir> real <DB> <NULL> <FROM> <TO> # sealed; refuses without the seal
  python -I t14_analysis.py <dir> real_verdict                 # sealed; merges real parts, applies rules

Inputs: S1 Table and S2 Table of the paper (raw/plos/, gitignored), read straight from the xlsx with a
stdlib zip/XML reader (no macros, nothing evaluated), and data/food_sets.tsv (from the authors' own code).
Every input's sha256 is checked and the run stops on a mismatch.

Definitions follow the paper and the authors' deposited scan script (FromSelectedFoodSet_to_LinProg_KEGG.py):
  expansion   fire every reaction whose reactants are all present, add its products, repeat to closure.
  tier 0      (S0, R0) = expansion of the ultimate food.
  candidate   every species of the network not in S0, one at a time.
  induced     (S1, R1) = expansion of S0 + {seed}, minus (S0, R0).
  supported   the LP  A x >= 0.001, x >= 0  is feasible, A = net stoichiometry of S1 (rows) in R1 (columns);
              the seed is in S1, so it must be net-produced (the authors' "supported seed").
  set         the induced S1 of a supported seed; seeds with the same S1 form one clique.
Statistics: n_seeds, n_sets (distinct sets), nested_share (share of pairs of distinct sets in which one
contains the other; 0 when fewer than two sets), largest (species in the largest set).
"""
import hashlib
import json
import math
import os
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from collections import deque

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

D, MODE = os.path.abspath(sys.argv[1]), sys.argv[2]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t14_autocatalytic_tiers/scripts/t14_analysis.py"
SEED = 20261126

SHA = {
    "raw/plos/S1_Table.xlsx": "ffa6f52f9326754a0025c826a80e59e449bd23d95e86135b73b0f0149b785ac3",
    "raw/plos/S2_Table.xlsx": "8ace73e1e69d29d35d7c8471c5633812a1e4b3a27ba195b77c4b92d14b321fe9",
    "data/food_sets.tsv": "466965aa53b1d4fbce0f5f238804f2976d4813cc25fdeec99dfc9c18787bce3d",
}

LP_B = 0.001             # the authors' b_positive
STATS = ["n_seeds", "n_sets", "nested_share", "largest"]


# ---------------------------------------------------------------- io helpers
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_inputs():
    bad = {n: sha256(os.path.join(D, n)) for n in SHA if sha256(os.path.join(D, n)) != SHA[n]}
    if bad:
        sys.exit("input hash mismatch: %s" % json.dumps(bad))


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
    print("wrote scripts_out/" + name, flush=True)


XM = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_xlsx_first_sheet(path):
    """Rows of the first worksheet as lists of strings. Stdlib only; reads sharedStrings and sheet1 XML."""
    z = zipfile.ZipFile(path)
    for info in z.infolist():
        if info.file_size > 50_000_000:
            sys.exit("xlsx part too large: " + info.filename)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(XM + "si"):
            shared.append("".join(t.text or "" for t in si.iter(XM + "t")))
    rows = []
    for row in ET.fromstring(z.read("xl/worksheets/sheet1.xml")).iter(XM + "row"):
        vals = {}
        for c in row.findall(XM + "c"):
            ref = re.match(r"[A-Z]+", c.get("r")).group(0)
            col = 0
            for ch in ref:
                col = col * 26 + ord(ch) - 64
            v = c.find(XM + "v")
            if c.get("t") == "s" and v is not None:
                val = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(XM + "t"))
            else:
                val = v.text if v is not None else ""
            vals[col - 1] = val
        rows.append([vals.get(i, "") for i in range(max(vals) + 1)] if vals else [])
    return rows


# ---------------------------------------------------------------- network
class Net:
    """Directed reactions over integer species. lhs/rhs: tuples of species; lco/rco: coefficients.
    partner[r] = index of the exact reverse reaction, or -1."""

    def __init__(self, names, lhs, lco, rhs, rco, partner):
        self.names, self.lhs, self.lco, self.rhs, self.rco = names, lhs, lco, rhs, rco
        self.partner = np.asarray(partner, np.int64)
        self.n_sp, self.n_rx = len(names), len(lhs)
        cons = [[] for _ in range(self.n_sp)]
        for r, L in enumerate(lhs):
            for s in L:
                cons[s].append(r)
        self.cons = cons
        self.nreact = np.array([len(L) for L in lhs], np.int64)

    def used(self):
        m = np.zeros(self.n_sp, bool)
        for L, R in zip(self.lhs, self.rhs):
            m[list(L)] = True
            m[list(R)] = True
        return m


def pair_up(lhs, lco, rhs, rco):
    key = {}
    for r in range(len(lhs)):
        key.setdefault((tuple(sorted(zip(lhs[r], lco[r]))), tuple(sorted(zip(rhs[r], rco[r])))), []).append(r)
    partner = [-1] * len(lhs)
    for r in range(len(lhs)):
        if partner[r] >= 0:
            continue
        cand = key.get((tuple(sorted(zip(rhs[r], rco[r]))), tuple(sorted(zip(lhs[r], lco[r])))), [])
        for q in cand:
            if q != r and partner[q] < 0:
                partner[r], partner[q] = q, r
                break
    return partner


def load_db(db):
    if db == "bio":
        rows = read_xlsx_first_sheet(os.path.join(D, "raw/plos/S2_Table.xlsx"))
        hdr, body, cols = rows[0], rows[1:], (1, 2, 3, 4, 5)
        assert hdr[:7] == ["Serial", "Reaction_entry", "Reactants", "Reactant_stoi", "Products",
                           "Product_stoi", "Note"], hdr
    else:
        rows = read_xlsx_first_sheet(os.path.join(D, "raw/plos/S1_Table.xlsx"))
        hdr, body, cols = rows[0], rows[1:], (2, 3, 4, 5, 6)
        assert hdr[:8] == ["Serial", "Reaction_Category", "Reaction_ID", "Reactant_name", "Reactant_stoi",
                           "Product_name", "Product_stoi", "Note"], hdr
    names, ix = [], {}

    def gid(x):
        if x not in ix:
            ix[x] = len(names)
            names.append(x)
        return ix[x]

    rid, lhs, lco, rhs, rco = [], [], [], [], []
    for r in body:
        r = r + [""] * 8
        a, b, c, d, e = (r[i].strip() for i in cols)
        L, Lc = [gid(x.strip()) for x in b.split(",")], [int(x) for x in c.split(",")]
        R, Rc = [gid(x.strip()) for x in d.split(",")], [int(x) for x in e.split(",")]
        assert len(L) == len(Lc) and len(R) == len(Rc) and len(set(L)) == len(L) and len(set(R)) == len(R)
        rid.append(a)
        lhs.append(tuple(L)); lco.append(tuple(Lc)); rhs.append(tuple(R)); rco.append(tuple(Rc))
    food = [l.split("\t")[1] for l in open(os.path.join(D, "data/food_sets.tsv"), encoding="utf-8")
            if l.strip() and not l.startswith("#") and l.split("\t")[0] == db]
    net = Net(names, lhs, lco, rhs, rco, pair_up(lhs, lco, rhs, rco))
    net.rid = rid
    return net, [ix[f] for f in food if f in ix], [f for f in food if f not in ix]


# ---------------------------------------------------------------- expansion and LP
def tier0(net, food):
    avail = np.zeros(net.n_sp, bool)
    avail[food] = True
    need = net.nreact.copy()
    fired = np.zeros(net.n_rx, bool)
    q = deque(food)
    while q:
        s = q.popleft()
        for r in net.cons[s]:
            need[r] -= 1
            if need[r] == 0:
                fired[r] = True
                for p in net.rhs[r]:
                    if not avail[p]:
                        avail[p] = True
                        q.append(p)
    # reactions with no reactants (none in these data) would fire too
    for r in np.flatnonzero(net.nreact == 0):
        fired[r] = True
    return avail, fired, need


def expand_seed(net, avail0, need0, seeds):
    """Species and reactions newly reached from tier 0 plus `seeds` (lists, in order reached).
    avail0 and need0 may be numpy arrays or plain lists (lists are much faster; scan passes lists)."""
    need = need0.tolist() if isinstance(need0, np.ndarray) else list(need0)
    new_sp, new_rx = [], []
    seen = set()
    q = deque()
    for s in seeds:
        if not avail0[s] and s not in seen:
            seen.add(s); new_sp.append(s); q.append(s)
    while q:
        s = q.popleft()
        for r in net.cons[s]:
            need[r] -= 1
            if need[r] == 0:
                new_rx.append(r)
                for p in net.rhs[r]:
                    if not avail0[p] and p not in seen:
                        seen.add(p); new_sp.append(p); q.append(p)
    return new_sp, new_rx


def sdas_feasible(net, sp, rx):
    """The authors' inequality (1): x >= 0 with sum_j x_j s_ij >= LP_B for every internal species i."""
    if not rx:
        return False
    row = {s: i for i, s in enumerate(sp)}
    ri, ci, va = [], [], []
    for j, r in enumerate(rx):
        for s, c in zip(net.lhs[r], net.lco[r]):
            if s in row:
                ri.append(row[s]); ci.append(j); va.append(-float(c))
        for s, c in zip(net.rhs[r], net.rco[r]):
            if s in row:
                ri.append(row[s]); ci.append(j); va.append(float(c))
    # sparse A with duplicates summed and explicit zeros dropped: the same nonzeros scipy builds from a
    # dense A before handing it to HiGHS, without the dense detour
    A = coo_matrix((va, (ri, ci)), shape=(len(sp), len(rx))).tocsr()
    A.sum_duplicates()
    A.eliminate_zeros()
    Ac = A.tocoo()
    pos = np.zeros(len(sp), bool)
    pos[Ac.row[Ac.data > 0]] = True
    if not pos.all():                        # a species no internal reaction makes: infeasible
        return False
    res = linprog(np.zeros(len(rx)), A_ub=-A, b_ub=-LP_B * np.ones(len(sp)), bounds=(0, None),
                  method="highs")
    return res.status == 0


def scan(net, food, seeds_sample=None, rng=None, keep_sets=False):
    """Singleton-seed scan. Returns the four statistics and descriptors."""
    t0, c0 = time.time(), time.process_time()
    avail0, fired0, need0 = tier0(net, food)
    av_l, need_l = avail0.tolist(), need0.tolist()
    used = net.used()
    cand = [s for s in range(net.n_sp) if used[s] and not avail0[s]]
    n_cand = len(cand)
    if seeds_sample is not None and seeds_sample < n_cand:
        cand = sorted(rng.choice(cand, size=seeds_sample, replace=False).tolist())
    cache = {}
    sets = {}
    n_lp = 0
    for s in cand:
        sp, rx = expand_seed(net, av_l, need_l, [s])
        key = frozenset(sp)
        if key not in cache:
            cache[key] = sdas_feasible(net, sp, rx)
            n_lp += 1
            if cache[key]:
                sets[key] = {"n_species": len(sp), "n_reactions": len(rx), "seeds": []}
        if cache[key]:
            sets[key]["seeds"].append(s)
    keys = list(sets)
    n_sets = len(keys)
    pairs = n_sets * (n_sets - 1) // 2
    nested = sum(1 for i in range(n_sets) for j in range(i + 1, n_sets)
                 if keys[i] <= keys[j] or keys[j] <= keys[i])
    # longest chain of nested sets (reported only)
    order = sorted(range(n_sets), key=lambda i: len(keys[i]))
    depth = [1] * n_sets
    for a in range(n_sets):
        for b in range(a):
            if keys[order[b]] < keys[order[a]]:
                depth[a] = max(depth[a], depth[b] + 1)
    n_seeds = sum(len(v["seeds"]) for v in sets.values())
    scale = n_cand / len(cand) if cand else 1.0
    out = {
        "n_seeds": n_seeds * scale, "n_sets": n_sets, "nested_share": nested / pairs if pairs else 0.0,
        "largest": max((len(k) for k in keys), default=0),
        "nested_pairs": nested, "chain_depth": max(depth, default=0),
        "tier0_species": int(avail0.sum()), "tier0_reactions": int(fired0.sum()),
        "n_candidates": n_cand, "n_scanned": len(cand), "n_distinct_expansions": len(cache), "n_lp": n_lp,
        "seconds": round(time.time() - t0, 2), "cpu_seconds": round(time.process_time() - c0, 2),
        "set_sizes": sorted(([len(k), sets[k]["n_reactions"], len(sets[k]["seeds"])] for k in keys),
                            reverse=True),
    }
    if keep_sets:
        out["_sets"] = sets
    return out


# ---------------------------------------------------------------- nulls
# A "unit" is a reversible pair (forward reaction a, its exact reverse b) or an unpaired one-way reaction.
# Each unit has a left side L (kept) and a right side R (= products of a; reactants of b).  Every null
# permutes R-side stubs (a species with its coefficient) between units of the same kind (paired with
# paired, one-way with one-way) and rebuilds b as the exact reverse of a.  So every species keeps its count
# as a reactant and as a product (and its total stoichiometry in each role), every reaction keeps its number
# of reactants and products and its coefficients, reversibility is kept, and the food set is unchanged.
# A moved stub may not land in a unit whose L or R side already holds that species.
#
# "swap"   (null 1, decides kill and support): all R-side stubs move, except that the tier-0 system is kept
#          exactly: units in R0 are not touched, and no rewired reversible unit may end with an R side made
#          only of tier-0 species (its reverse would then fire from food and enlarge tier 0).  The rewired
#          network's tier 0 is asserted equal to the real one.
# "strict" (null 2, decides support): as "swap", and in addition stubs of frozen species never move
#          (tier-0 species and the top 1% of species by degree: water, H+, ATP/ADP, NAD(P)(H), CoA,
#          phosphate ... in KEGG), and the other stubs move only between species of the same degree class
#          floor(log2(degree)).  This stands in for the plan's element-balance swap, which needs molecular
#          formulas that the deposited data do not carry.
# "swap_plan" (reported only): the plan's swap as written, with no tier-0 protection.
NULLS = ["swap", "strict"]
NULL_REPORTED = ["swap_plan"]
TOP_FROZEN = 0.01


def units_of(net):
    return [r for r in range(net.n_rx) if net.partner[r] < 0 or r < net.partner[r]]


def degree(net):
    d = np.zeros(net.n_sp, np.int64)
    for L, R in zip(net.lhs, net.rhs):
        d[list(L)] += 1
        d[list(R)] += 1
    return d


def frozen_species(net, food):
    avail0, _, _ = tier0(net, food)
    d = degree(net)
    used = np.flatnonzero(d > 0)
    k = int(math.ceil(TOP_FROZEN * len(used)))
    thr = np.sort(d[used])[::-1][k - 1]
    return avail0 | (d >= thr)


def rewire(net, food, kind, rng, max_rounds=400):
    avail0, fired0, _ = tier0(net, food)
    keep_t0 = kind in ("swap", "strict")
    U = units_of(net)
    if keep_t0:
        U = [u for u in U if not (fired0[u] or (net.partner[u] >= 0 and fired0[net.partner[u]]))]
    Lset = [set(net.lhs[u]) for u in U]
    Rsp = [list(net.rhs[u]) for u in U]
    Rco = [list(net.rco[u]) for u in U]
    guard = [keep_t0 and net.partner[u] >= 0 for u in U]     # R side must keep a non-tier-0 species
    if kind == "strict":
        frz = frozen_species(net, food)
        dcls = np.floor(np.log2(np.maximum(degree(net), 1))).astype(int)
    groups = {}
    for ui, u in enumerate(U):
        paired = net.partner[u] >= 0
        for k, s in enumerate(Rsp[ui]):
            if kind == "strict":
                if frz[s]:
                    continue
                g = (paired, int(dcls[s]))
            else:
                g = (paired,)
            groups.setdefault(g, []).append((ui, k))
    for g, pos in groups.items():
        stubs = [(Rsp[ui][k], Rco[ui][k]) for ui, k in pos]
        perm = rng.permutation(len(stubs))
        for (ui, k), p in zip(pos, perm):
            Rsp[ui][k], Rco[ui][k] = stubs[p]

    def bad(ui, k):
        s = Rsp[ui][k]
        if s in Lset[ui] or Rsp[ui].count(s) > 1:
            return True
        return guard[ui] and all(avail0[x] for x in Rsp[ui])

    unresolved = 0
    for g, pos in groups.items():
        for _ in range(max_rounds):
            conf = [i for i, (ui, k) in enumerate(pos) if bad(ui, k)]
            if not conf:
                break
            for i in conf:
                ui, k = pos[i]
                if not bad(ui, k):
                    continue
                for _try in range(50):
                    j = int(rng.integers(len(pos)))
                    uj, kj = pos[j]
                    if uj == ui:
                        continue
                    Rsp[ui][k], Rsp[uj][kj] = Rsp[uj][kj], Rsp[ui][k]
                    Rco[ui][k], Rco[uj][kj] = Rco[uj][kj], Rco[ui][k]
                    if not bad(ui, k) and not bad(uj, kj) and not any(bad(uj, q) for q in range(len(Rsp[uj]))):
                        break
                    Rsp[ui][k], Rsp[uj][kj] = Rsp[uj][kj], Rsp[ui][k]
                    Rco[ui][k], Rco[uj][kj] = Rco[uj][kj], Rco[ui][k]
        unresolved += sum(1 for ui, k in pos if bad(ui, k))
    if unresolved:
        raise RuntimeError("rewire: %d unresolved conflicts" % unresolved)
    lhs, lco, rhs, rco = list(net.lhs), list(net.lco), list(net.rhs), list(net.rco)
    for ui, u in enumerate(U):
        rhs[u], rco[u] = tuple(Rsp[ui]), tuple(Rco[ui])
        b = net.partner[u]
        if b >= 0:
            lhs[b], lco[b] = tuple(Rsp[ui]), tuple(Rco[ui])
    out = Net(net.names, lhs, lco, rhs, rco, net.partner)
    if keep_t0:
        a1, f1, _ = tier0(out, food)
        if not ((a1 == avail0).all() and (f1 == fired0).all()):
            raise RuntimeError("rewire changed tier 0")
    return out


def check_rewire_invariants(net, new):
    """Degrees by role, reaction sizes and coefficients, and pairing are unchanged."""
    def role_counts(n):
        a = np.zeros(n.n_sp, np.int64); b = np.zeros(n.n_sp, np.int64)
        for L, R in zip(n.lhs, n.rhs):
            a[list(L)] += 1; b[list(R)] += 1
        return a, b
    a0, b0 = role_counts(net); a1, b1 = role_counts(new)
    ok = (a0 == a1).all() and (b0 == b1).all()
    ok &= all(len(x) == len(y) for x, y in zip(net.lhs, new.lhs)) and all(len(x) == len(y) for x, y in zip(net.rhs, new.rhs))
    ok &= sorted(c for t in net.rco for c in t) == sorted(c for t in new.rco for c in t)
    for r in range(new.n_rx):
        p = new.partner[r]
        if p >= 0:
            ok &= set(new.lhs[r]) == set(new.rhs[p]) and set(new.rhs[r]) == set(new.lhs[p])
    both = sum(1 for r in range(new.n_rx) if set(new.lhs[r]) & set(new.rhs[r]))
    both0 = sum(1 for r in range(net.n_rx) if set(net.lhs[r]) & set(net.rhs[r]))
    return {"invariants_ok": bool(ok), "both_side_reactions_before": both0, "both_side_reactions_after": both}


# ---------------------------------------------------------------- decision rules
Q_IN, Q_OUT = (0.025, 0.975), (0.005, 0.995)


def position(obs, vals, q):
    lo, hi = np.quantile(np.asarray(vals, float), q)
    return 0 if lo <= obs <= hi else (1 if obs > hi else -1)


def classify(obs, nulls):
    """obs: dict of the four statistics.  nulls: {"swap": [dicts], "strict": [dicts]}."""
    out = {}
    for s in STATS:
        out[s] = {
            "inside95_swap": position(obs[s], [v[s] for v in nulls["swap"]], Q_IN) == 0,
            "out99_swap": position(obs[s], [v[s] for v in nulls["swap"]], Q_OUT),
            "out99_strict": position(obs[s], [v[s] for v in nulls["strict"]], Q_OUT),
        }
        a, b = out[s]["out99_swap"], out[s]["out99_strict"]
        out[s]["out99_both"] = a if (a == b and a != 0) else 0
    n_in = sum(out[s]["inside95_swap"] for s in STATS)
    return {"per_stat": out, "n_inside95_swap": n_in,
            "n_out99_both": sum(out[s]["out99_both"] != 0 for s in STATS)}


def verdict(cls_bio, cls_abio):
    """Kill: in the biochemical network >= 3 of 4 statistics inside the central 95% of the swap null.
    Support: >= 3 of 4 statistics outside the central 99% of both nulls, same side, in both databases,
    with the same direction in both.  Partly: anything else."""
    kill = cls_bio["n_inside95_swap"] >= 3
    agree = [s for s in STATS if cls_bio["per_stat"][s]["out99_both"] != 0
             and cls_bio["per_stat"][s]["out99_both"] == cls_abio["per_stat"][s]["out99_both"]]
    support = (not kill) and len(agree) >= 3
    bio_only = (not kill) and cls_bio["n_out99_both"] >= 3
    return {"verdict": "kill" if kill else ("support" if support else "partly"), "kill": kill,
            "support": support, "agreeing_stats": agree, "bio_alone_outside_both_ge3": bio_only}


HIER = ["n_sets", "nested_share"]     # the tiered structure itself
SCALE = ["n_seeds", "largest"]        # how much is supported, not how it is arranged
PRIMARY_RULE = "hier"                 # "plan" or "hier"; the prereg says which one decides (confirmed at seal)


def verdict_hier(cls_bio, cls_abio):
    """Revised form (see prereg, change C3).  Only the two hierarchy statistics decide.
    Kill: in the biochemical network both n_sets and nested_share inside the central 95% of the swap null.
    Support: both above the central 99% of BOTH nulls.  Partly: anything else.
    The abiotic network is reported only (its published tier-1 is one set, so its hierarchy statistics
    cannot leave a null that also gives one set); abio_contradicts flags it if either hierarchy statistic
    lies below the central 99% of both of its nulls."""
    pb = cls_bio["per_stat"]
    kill = all(pb[s]["inside95_swap"] for s in HIER)
    support = (not kill) and all(pb[s]["out99_both"] > 0 for s in HIER)
    contra = any(cls_abio["per_stat"][s]["out99_both"] < 0 for s in HIER)
    return {"verdict": "kill" if kill else ("support" if support else "partly"), "kill": kill,
            "support": support, "abio_contradicts": contra,
            "scale_positions_swap": {s: pb[s]["out99_swap"] for s in SCALE}}


# ---------------------------------------------------------------- synthetic networks (planted check)
# Backgrounds are mass-balanced random networks generated from a Zipf species-weight law and side-size
# shares, NOT from the real networks' degree sequences, so no planted run reveals anything about the real
# networks' nulls.  Every background reaction conserves an integer "mass" (a stand-in for atoms), as real
# chemistry does; the nulls, like rewiring of the real networks, do not keep it.
# Shares of hubs and specific species per side follow the real networks' descriptive shares.
WORLDS = {
    # dense: about one reaction pair per species, like the real biochemical network
    "dense": {
        "big": {"n_sp": 1500, "n_pairs": 1550, "n_oneway": 0, "n_hub": 30, "n_food": 8, "a_spec": 0.8,
                "hub_p": [0.26, 0.53, 0.19, 0.02], "spec_p": [0.05, 0.83, 0.12], "coef2": 0.05, "mmax": 30},
        "small": {"n_sp": 280, "n_pairs": 54, "n_oneway": 609, "n_hub": 8, "n_food": 5, "a_spec": 0.8,
                  "hub_p": [0.68, 0.30, 0.02], "spec_p": [0.01, 0.41, 0.50, 0.08], "coef2": 0.08, "mmax": 30}},
    # sparse: lower density, smaller random autocatalytic component
    "sparse": {
        "big": {"n_sp": 1500, "n_pairs": 600, "n_oneway": 0, "n_hub": 30, "n_food": 8, "a_spec": 1.0,
                "hub_p": [0.4, 0.45, 0.15], "spec_p": [0.05, 0.9, 0.1], "coef2": 0.03, "mmax": 30},
        "small": {"n_sp": 280, "n_pairs": 20, "n_oneway": 250, "n_hub": 8, "n_food": 5, "a_spec": 1.0,
                  "hub_p": [0.75, 0.25], "spec_p": [0.01, 0.6, 0.35, 0.04], "coef2": 0.03, "mmax": 30}},
}
CORE_M = {"big": 8, "small": 6}


def gen_background(rng, g):
    n, nh, nf = g["n_sp"], g["n_hub"], g["n_food"]
    mass = np.zeros(n, np.int64)
    mass[:nf] = rng.integers(1, 4, size=nf)
    mass[0] = 1
    mass[nf:nh] = rng.integers(8, 41, size=nh - nf)
    mass[nh:] = rng.integers(2, g["mmax"] + 1, size=n - nh)
    wh = 1.0 / np.arange(1, nh + 1)
    wh /= wh.sum()
    ws = 1.0 / np.arange(1, n - nh + 1) ** g["a_spec"]
    ws /= ws.sum()
    wfull = np.zeros(n)
    wfull[nh:] = ws
    bym = {}
    for s in range(nh, n):
        bym.setdefault(int(mass[s]), []).append(s)
    sp_p = np.array(g["spec_p"][1:]) / sum(g["spec_p"][1:])
    hub_p = g["hub_p"]

    def pick_mass(m, excl):
        c = [s for s in bym.get(int(m), []) if s not in excl]
        if not c:
            return None
        w = wfull[c]
        return int(rng.choice(c, p=w / w.sum()))

    def hubs(k, excl):
        out, t = [], 0
        while len(out) < k and t < 100:
            t += 1
            s = int(rng.choice(nh, p=wh))
            if s not in out and s not in excl:
                out.append(s)
        return out

    def coefs(side):
        return [2 if (s < nh and rng.random() < g["coef2"]) else 1 for s in side]

    def msum(side, co):
        return int(sum(mass[s] * c for s, c in zip(side, co)))

    def one():
        for _ in range(500):
            if rng.random() < g["spec_p"][0]:          # hub-only unit (inorganic-like), both sides hubs
                L = hubs(max(1, int(rng.choice(len(hub_p), p=hub_p))), [])
                Lc = coefs(L)
                R = hubs(max(1, int(rng.choice(len(hub_p), p=hub_p))), L)
                Rc = [1] * len(R)
                if R and msum(R, Rc) == msum(L, Lc):
                    return L, Lc, R, Rc
                continue
            nsl, nsr = 1 + int(rng.choice(len(sp_p), p=sp_p)), 1 + int(rng.choice(len(sp_p), p=sp_p))
            L = []
            while len(L) < nsl:
                s = nh + int(rng.choice(n - nh, p=ws))
                if s not in L:
                    L.append(s)
            L += hubs(int(rng.choice(len(hub_p), p=hub_p)), L)
            Lc = coefs(L)
            R = hubs(int(rng.choice(len(hub_p), p=hub_p)), L)
            Rc = coefs(R)
            T = msum(L, Lc) - msum(R, Rc)
            if nsr == 1:
                s = pick_mass(T, set(L) | set(R))
                if s is None:
                    continue
                R.append(s); Rc.append(1)
            else:
                if T < 4:
                    continue
                m1 = int(rng.integers(2, T - 1))
                s1 = pick_mass(m1, set(L) | set(R))
                s2 = None if s1 is None else pick_mass(T - m1, set(L) | set(R) | {s1})
                if s2 is None:
                    continue
                R += [s1, s2]; Rc += [1, 1]
            return L, Lc, R, Rc
        raise RuntimeError("generator: no balanced reaction found")

    lhs, lco, rhs, rco, partner = [], [], [], [], []
    for _ in range(g["n_pairs"]):
        L, Lc, R, Rc = (tuple(x) for x in one())
        i = len(lhs)
        lhs += [L, R]; lco += [Lc, Rc]; rhs += [R, L]; rco += [Rc, Lc]; partner += [i + 1, i]
    for _ in range(g["n_oneway"]):
        L, Lc, R, Rc = (tuple(x) for x in one())
        lhs.append(L); lco.append(Lc); rhs.append(R); rco.append(Rc); partner.append(-1)
    names = ["s%d" % i for i in range(n)]
    return [names, lhs, lco, rhs, rco, partner, list(range(nf)), mass]


def plant_cores(rng, parts, n_cores, m, reversible):
    """Plant n_cores nested, mass-balanced autocatalytic cycles made of NEW species.
    Core k has members X1..Xm and inputs in_1..in_m (food species of mass 1 for core 1; the members of
    core k-1 for core k >= 2):  Xi + in_i -> X(i+1);  Xm + in_m -> X1 + X2 (the branching step).
    Masses: X1 = sum(in) - in_1, X(i+1) = Xi + in_i, which balances every step.
    Link down: Xm -> X1 + Y (+ W), Y a member of core k-1 (for core 1: a supported seed of the background,
    if it has one), W a new waste species that balances mass when Y is lighter than Xm - X1.  So the seeds
    of core k produce core k-1 and its induced set contains core k-1's, and the planted chain sits on top
    of the background's own set, as SDAS-bio-1a, 1b and 1c sit on each other."""
    names, lhs, lco, rhs, rco, partner, food, mass = parts
    one_food = [f for f in food if mass[f] == 1]
    new = []
    members = []
    mass = list(mass)

    def add_species(mv):
        names.append("p%d" % len(names))
        mass.append(int(mv))
        return len(names) - 1

    bg = Net(names[:], lhs, lco, rhs, rco, partner)
    o = scan(bg, food, keep_sets=True)
    bg_seeds = sorted(s for v in o["_sets"].values() for s in v["seeds"])
    for k in range(n_cores):
        if k == 0:
            inp = [one_food[int(rng.integers(len(one_food)))] for _ in range(m)]
        else:
            inp = [members[k - 1][i % m] for i in range(m)]
        im = [mass[x] for x in inp]
        x1 = sum(im) - im[0]
        X = [add_species(x1)]
        for i in range(m - 1):
            X.append(add_species(mass[X[-1]] + im[i]))
        for i in range(m - 1):
            new.append(((X[i], inp[i]), (X[i + 1],)))
        new.append(((X[m - 1], inp[m - 1]), (X[0], X[1])))
        # link down: X_m -> X_1 + Y (+ W)
        need = mass[X[m - 1]] - mass[X[0]]
        pool = bg_seeds if k == 0 else members[k - 1]
        cand = [y for y in pool if mass[y] <= need]
        if cand:
            exact = [y for y in cand if mass[y] == need]
            Y = (exact or cand)[int(rng.integers(len(exact or cand)))]
            prod = (X[0], Y) if mass[Y] == need else (X[0], Y, add_species(need - mass[Y]))
            new.append(((X[m - 1],), prod))
        members.append(X)
    for L, R in new:
        i = len(lhs)
        if reversible:
            lhs += [L, R]; lco += [(1,) * len(L), (1,) * len(R)]; rhs += [R, L]
            rco += [(1,) * len(R), (1,) * len(L)]; partner += [i + 1, i]
        else:
            lhs.append(L); lco.append((1,) * len(L)); rhs.append(R); rco.append((1,) * len(R))
            partner.append(-1)
    parts[7] = np.array(mass)
    return members


def synth(rng, world, which, n_cores):
    g = WORLDS[world][which]
    parts = gen_background(rng, g)
    members = plant_cores(rng, parts, n_cores, CORE_M[which], reversible=(which == "big")) if n_cores else []
    names, lhs, lco, rhs, rco, partner, food, mass = parts
    return Net(names, lhs, lco, rhs, rco, partner), food, members


def null_draws(net, food, kind, idx, stream, seeds_sample=None):
    out = []
    for i in idx:
        rng = np.random.default_rng(stream + [i])
        nn = rewire(net, food, kind, rng)
        o = scan(nn, food, seeds_sample=seeds_sample, rng=rng)
        out.append({k: o[k] for k in STATS + ["chain_depth", "seconds", "cpu_seconds", "n_lp"]} | {"i": i})
    return out


def obs_stats(o):
    return {k: o[k] for k in STATS}


# ---------------------------------------------------------------- modes
def gate():
    check_inputs()
    GATE_SHA = {"raw/plos/S10_Table.xlsx": None, "raw/plos/S11_Table.xlsx": None, "raw/plos/S3_Table.xlsx": None}
    for k in GATE_SHA:
        GATE_SHA[k] = sha256(os.path.join(D, k))
    res = {"mode": "gate", "script_sha256": sha256(os.path.abspath(__file__)), "gate_inputs": GATE_SHA}
    pub = {"bio": {"species": 4216, "reactions": 8402, "tier0_species": 30, "tier0_reactions": 44,
                   "n_candidates": 4186, "n_seeds": 304, "set_species": [1414, 357, 301],
                   "set_reactions": [4114, 916, 736], "clique_sizes": [3, 34, 267], "nested": True},
           "abio": {"species": 277, "reactions": 717, "tier0_species": 5, "tier0_reactions": 0,
                    "n_candidates": 272, "n_seeds": 12, "set_species": [91], "set_reactions": [220],
                    "clique_sizes": [12]}}
    ok = True
    for db in ["bio", "abio"]:
        net, food, miss = load_db(db)
        o = scan(net, food, keep_sets=True)
        sets = o.pop("_sets")
        p = pub[db]
        ss = [x[0] for x in o["set_sizes"]]
        sr = [x[1] for x in o["set_sizes"]]
        cs = [x[2] for x in o["set_sizes"]]
        within5 = lambda a, b: abs(a - b) <= 0.05 * b
        chk = {
            "species": [net.n_sp, p["species"], net.n_sp == p["species"]],
            "reactions": [net.n_rx, p["reactions"], net.n_rx == p["reactions"]],
            "tier0": [[o["tier0_species"], o["tier0_reactions"]], [p["tier0_species"], p["tier0_reactions"]],
                      [o["tier0_species"], o["tier0_reactions"]] == [p["tier0_species"], p["tier0_reactions"]]],
            "n_candidates": [o["n_candidates"], p["n_candidates"], o["n_candidates"] == p["n_candidates"]],
            "n_seeds_within5pct": [o["n_seeds"], p["n_seeds"], within5(o["n_seeds"], p["n_seeds"])],
            "set_species_within5pct": [ss, p["set_species"], len(ss) == len(p["set_species"]) and
                                       all(within5(a, b) for a, b in zip(ss, p["set_species"]))],
            "set_reactions": [sr, p["set_reactions"], sr == p["set_reactions"]],
            "clique_sizes": [cs, p["clique_sizes"], cs == p["clique_sizes"]],
        }
        if db == "bio":
            chk["nested_chain"] = [o["chain_depth"], 3, o["chain_depth"] == 3 and o["nested_share"] == 1.0]
            # tier-0 species list against S10 Table, supported list against S11 Table (published)
            s10 = [r[0] for r in read_xlsx_first_sheet(os.path.join(D, "raw/plos/S10_Table.xlsx"))[1:] if r]
            avail0, _, _ = tier0(net, food)
            chk["tier0_matches_S10A"] = [sorted(s10) == sorted(net.names[i] for i in np.flatnonzero(avail0)), True,
                                         sorted(s10) == sorted(net.names[i] for i in np.flatnonzero(avail0))]
            s11 = read_xlsx_first_sheet(os.path.join(D, "raw/plos/S11_Table.xlsx"))
            h = s11[0]
            pubsup = {r[h.index("Seed_Choice")] for r in s11[1:] if len(r) > h.index("Supported")
                      and r[h.index("Supported")] == "Yes"}
            oursup = {net.names[s] for v in sets.values() for s in v["seeds"]}
            chk["supported_list_matches_S11"] = [len(oursup & pubsup), len(pubsup), oursup == pubsup]
            # the paper's nine-species food (S3 Python Script Biochem_ufs.txt) gives the same tier 0
            nine = ["C00001", "C00014", "C00011", "C00283", "C00059", "C00094", "C11481", "C00009", "C00013"]
            a9, f9, _ = tier0(net, [net.names.index(x) for x in nine])
            chk["nine_food_same_tier0"] = [int(a9.sum()), int(f9.sum()), bool((a9 == avail0).all())]
        else:
            s3 = read_xlsx_first_sheet(os.path.join(D, "raw/plos/S3_Table.xlsx"))
            h = s3[0]
            pubsup = {r[h.index("Seed_Choice")] for r in s3[1:] if len(r) > h.index("Supported")
                      and r[h.index("Supported")] == "Yes"}
            oursup = {net.names[s] for v in sets.values() for s in v["seeds"]}
            chk["supported_list_matches_S3"] = [len(oursup & pubsup), len(pubsup), oursup == pubsup]
        # rewiring invariants on a throwaway draw are NOT checked here: no rewired real network is built
        # before the seal except in `dryrun` (see prereg).
        for k, v in chk.items():
            ok &= bool(v[-1])
        res[db] = {"checks": chk, "stats": obs_stats(o), "chain_depth": o["chain_depth"],
                   "seconds_full_scan": o["seconds"], "cpu_seconds_full_scan": o["cpu_seconds"],
                   "n_distinct_expansions": o["n_distinct_expansions"],
                   "food_missing_from_network": miss}
    res["fallback_triggered_by_real_scan_time"] = max(res["bio"]["cpu_seconds_full_scan"],
                                                      res["abio"]["cpu_seconds_full_scan"]) > FALLBACK_SECONDS
    res["gate_pass"] = bool(ok)
    print(json.dumps(res, indent=1, default=float))
    dump("t14_gate.json", res)


def timing():
    """Synthetic networks only: scan time and one rewire of each kind, per world."""
    out = {}
    for world in WORLDS:
        for which, nc in [("big", 0), ("big", 3), ("small", 0), ("small", 1)]:
            rng = np.random.default_rng([SEED, 7, len(world), len(which), nc])
            net, food, mem = synth(rng, world, which, nc)
            o = scan(net, food)
            row = {"obs": {k: o[k] for k in STATS + ["chain_depth", "seconds", "tier0_species", "n_candidates"]},
                   "set_sizes_top5": o["set_sizes"][:5]}
            for kind in NULLS + NULL_REPORTED:
                t = time.time()
                nn = rewire(net, food, kind, np.random.default_rng([SEED, 8, len(world), len(which), nc]))
                inv = check_rewire_invariants(net, nn)
                o2 = scan(nn, food)
                row[kind] = {k: o2[k] for k in STATS + ["chain_depth", "tier0_species"]} | inv | \
                            {"rewire_plus_scan_s": round(time.time() - t, 2)}
            out["%s_%s_cores%d" % (world, which, nc)] = row
            print(world, which, nc, json.dumps(row), flush=True)
    dump("t14_timing_synthetic.json", out)


# ---------------------------------------------------------------- planted check
N_NULL_PLANTED = 100        # per null per network in the planted check (real: N_NULL_REAL)
N_PLAN_PLANTED = 20         # the plan's literal swap, reported only
SCEN = {
    # name: (world, cores in big, cores in small, observed = one swap rewire of the planted pair?)
    "sparse_planted": ("sparse", 3, 1, False),
    "sparse_samedeg": ("sparse", 3, 1, True),
    "sparse_background": ("sparse", 0, 0, False),
    "dense_planted": ("dense", 3, 1, False),
    "dense_samedeg": ("dense", 3, 1, True),
}
SCEN_CODE = {k: i for i, k in enumerate(SCEN)}


def summarize_nulls(rows):
    return {s: [r[s] for r in rows] for s in STATS + ["chain_depth"]}


def one_network(net, food, stream, n_null, n_plan):
    o = scan(net, food)
    nulls = {}
    for ki, kind in enumerate(NULLS + NULL_REPORTED):
        n = n_plan if kind in NULL_REPORTED else n_null
        nulls[kind] = null_draws(net, food, kind, range(n), stream + [ki])
    return o, nulls


def evaluate(obs_big, nb, obs_small, ns):
    cb = classify(obs_big, nb)
    cs = classify(obs_small, ns)
    v = verdict(cb, cs)
    v["hier"] = verdict_hier(cb, cs)
    # the plan's rule with the plan's literal swap as "the rewired values" (reported only)
    plan = {"kill_plan_null": sum(position(obs_big[s], [r[s] for r in nb["swap_plan"]], Q_IN) == 0
                                  for s in STATS) >= 3}
    return cb, cs, v, plan


def planted():
    name, r0, r1 = sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
    world, cb, cs, samedeg = SCEN[name]
    rows = []
    for rep in range(r0, r1):
        t = time.time()
        res = {"scenario": name, "rep": rep}
        for which, nc in [("big", cb), ("small", cs)]:
            rng = np.random.default_rng([SEED, 1, {"sparse": 0, "dense": 1}[world], rep, len(which)])
            net, food, members = synth(rng, world, which, nc)
            if samedeg:
                net = rewire(net, food, "swap", np.random.default_rng([SEED, 2, rep, len(which)]))
            stream = [SEED, 3, SCEN_CODE[name], rep, len(which)]
            o, nulls = one_network(net, food, stream, N_NULL_PLANTED, N_PLAN_PLANTED)
            res[which] = {"obs": {k: o[k] for k in STATS + ["chain_depth", "tier0_species", "n_candidates"]},
                          "set_sizes_top6": o["set_sizes"][:6],
                          "nulls": {k: summarize_nulls(v) for k, v in nulls.items()},
                          "null_scan_seconds_median": float(np.median([r["cpu_seconds"] for v in nulls.values()
                                                                       for r in v]))}
        nb = {k: [dict(zip(STATS, x)) for x in zip(*[res["big"]["nulls"][k][s] for s in STATS])]
              for k in res["big"]["nulls"]}
        ns = {k: [dict(zip(STATS, x)) for x in zip(*[res["small"]["nulls"][k][s] for s in STATS])]
              for k in res["small"]["nulls"]}
        cbig, csmall, v, plan = evaluate(res["big"]["obs"], nb, res["small"]["obs"], ns)
        res.update({"class_big": cbig, "class_small": csmall, "verdict": v, "plan_null_as_written": plan,
                    "seconds": round(time.time() - t, 1)})
        print(json.dumps({"scenario": name, "rep": rep, "verdict_plan": v["verdict"], "verdict_hier": v["hier"]["verdict"],
                          "agree": v["agreeing_stats"],
                          "bio_alone": v["bio_alone_outside_both_ge3"], "obs_big": res["big"]["obs"],
                          "obs_small": res["small"]["obs"], "n_in95_big": cbig["n_inside95_swap"],
                          "n_out99_big": cbig["n_out99_both"], "sec": res["seconds"]}), flush=True)
        rows.append(res)
    dump("t14_planted_part_%s_%d-%d.json" % (name, r0, r1),
         {"script_sha256": sha256(os.path.abspath(__file__)), "n_null": N_NULL_PLANTED, "rows": rows})


def planted_merge():
    import glob
    parts = sorted(glob.glob(os.path.join(D, "scripts_out", "t14_planted_part_*.json")))
    me = sha256(os.path.abspath(__file__))
    by = {}
    hashes = set()
    for p in parts:
        j = json.load(open(p))
        hashes.add(j["script_sha256"])
        for r in j["rows"]:
            # rules are re-applied by this script to the stored observed values and null arrays
            nb = {k: [dict(zip(STATS, x)) for x in zip(*[r["big"]["nulls"][k][s] for s in STATS])]
                  for k in r["big"]["nulls"]}
            ns = {k: [dict(zip(STATS, x)) for x in zip(*[r["small"]["nulls"][k][s] for s in STATS])]
                  for k in r["small"]["nulls"]}
            cbig, csmall, v, plan = evaluate(r["big"]["obs"], nb, r["small"]["obs"], ns)
            by.setdefault(r["scenario"], {})[r["rep"]] = {"v": v, "cb": cbig, "plan": plan, "r": r}
    table = {}
    for name, reps in by.items():
        vs = [x["v"] for x in reps.values()]
        n = len(vs)
        per_stat = {s: {"above": sum(x["cb"]["per_stat"][s]["out99_both"] > 0 for x in reps.values()),
                        "below": sum(x["cb"]["per_stat"][s]["out99_both"] < 0 for x in reps.values()),
                        "inside95_swap": sum(x["cb"]["per_stat"][s]["inside95_swap"] for x in reps.values())}
                    for s in STATS}
        mean = lambda f: float(np.mean([f(x["r"]) for x in reps.values()]))
        table[name] = {
            "n_rep": n,
            "plan_rule": {"kill": sum(x["kill"] for x in vs), "support": sum(x["support"] for x in vs),
                          "partly": sum(x["verdict"] == "partly" for x in vs)},
            "hier_rule": {"kill": sum(x["hier"]["kill"] for x in vs),
                          "support": sum(x["hier"]["support"] for x in vs),
                          "partly": sum(x["hier"]["verdict"] == "partly" for x in vs),
                          "abio_contradicts": sum(x["hier"]["abio_contradicts"] for x in vs)},
            "bio_alone_outside_both_ge3": sum(x["bio_alone_outside_both_ge3"] for x in vs),
            "plan_null_as_written_kill": sum(x["plan"]["kill_plan_null"] for x in reps.values()),
            "per_stat_big": per_stat,
            "mean_obs_big": {s: mean(lambda r: r["big"]["obs"][s]) for s in STATS + ["chain_depth"]},
            "mean_null_swap_median_big": {s: mean(lambda r: float(np.median(r["big"]["nulls"]["swap"][s])))
                                          for s in STATS},
            "mean_null_strict_median_big": {s: mean(lambda r: float(np.median(r["big"]["nulls"]["strict"][s])))
                                            for s in STATS},
            "mean_null_swapplan_median_big": {s: mean(lambda r: float(np.median(r["big"]["nulls"]["swap_plan"][s])))
                                              for s in STATS},
            "mean_obs_small": {s: mean(lambda r: r["small"]["obs"][s]) for s in STATS},
            "mean_null_swap_median_small": {s: mean(lambda r: float(np.median(r["small"]["nulls"]["swap"][s])))
                                            for s in STATS},
            "median_null_scan_seconds_big": mean(lambda r: r["big"]["null_scan_seconds_median"]),
        }
    out = {"rules_applied_by_script_sha256": me, "parts_computed_by_script_sha256": sorted(hashes),
           "n_null_per_network": N_NULL_PLANTED, "table": table,
           "parts": [os.path.basename(p) for p in parts]}
    print(json.dumps(table, indent=1))
    dump("t14_planted.json", out)


# ---------------------------------------------------------------- real and dry run
N_NULL_REAL = 200
N_PLAN_REAL = 50            # the plan's literal swap, reported only
FALLBACK_SECONDS = 60.0     # plan: if one network scan takes longer, 100 rewires and 1,000 sampled seeds
FALLBACK_N, FALLBACK_SEEDS = 100, 1000
DB_CODE = {"bio": 0, "abio": 1}


def standin(db):
    net, food, _ = load_db(db)
    return rewire(net, food, "swap", np.random.default_rng([SEED, 99, DB_CODE[db]])), food


def fallback_state():
    p = os.path.join(D, "scripts_out", "t14_dryrun.json")
    if not os.path.exists(p):
        sys.exit("REFUSED: run the dry run first; it fixes whether the plan's time fallback applies.")
    return json.load(open(p))["fallback"]


def null_part(dry):
    db, kind, i0, i1 = sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
    if not dry:
        st = seal_status()
        if not st["real_allowed"]:
            sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                     % (SELF, st["script_sha256"]))
        fb = fallback_state()
    else:
        fb = False
    check_inputs()
    if dry:
        net, food = standin(db)
    else:
        net, food, _ = load_db(db)
    nmax = (FALLBACK_N if fb else N_NULL_REAL) if kind in NULLS else N_PLAN_REAL
    i1 = min(i1, nmax)
    sample = FALLBACK_SEEDS if fb else None
    stream = [SEED, 5 if dry else 6, DB_CODE[db], (NULLS + NULL_REPORTED).index(kind)]
    rows = null_draws(net, food, kind, range(i0, i1), stream, seeds_sample=sample)
    sub = "work/dryrun_blind" if dry else "scripts_out/real_parts"
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    fn = os.path.join(D, sub, "%s_%s_%d-%d.json" % (db, kind, i0, i1))
    json.dump({"script_sha256": sha256(os.path.abspath(__file__)), "db": db, "null": kind,
               "fallback": fb, "rows": rows}, open(fn, "w"))
    secs = [r["cpu_seconds"] for r in rows]
    # dry run is blind: only counts and times are printed, never a statistic
    print(json.dumps({"wrote": os.path.relpath(fn, D), "n": len(rows),
                      "scan_cpu_seconds_median": float(np.median(secs)) if secs else None,
                      "scan_cpu_seconds_max": max(secs) if secs else None}), flush=True)


def load_parts(sub, db):
    import glob
    rows = {}
    for p in sorted(glob.glob(os.path.join(D, sub, "%s_*.json" % db))):
        j = json.load(open(p))
        for r in j["rows"]:
            rows.setdefault(j["null"], {})[r["i"]] = r
    return {k: [v[i] for i in sorted(v)] for k, v in rows.items()}


def final(dry):
    if not dry:
        st = seal_status()
        if not st["real_allowed"]:
            sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                     % (SELF, st["script_sha256"]))
        fb = fallback_state()
    else:
        fb = False
    check_inputs()
    sub = "work/dryrun_blind" if dry else "scripts_out/real_parts"
    obs, nulls, cls, secs = {}, {}, {}, {}
    for db in ["bio", "abio"]:
        if dry:
            net, food = standin(db)
        else:
            net, food, _ = load_db(db)
        sample = FALLBACK_SEEDS if fb else None
        o = scan(net, food, seeds_sample=sample, rng=np.random.default_rng([SEED, 7, DB_CODE[db]]))
        obs[db] = o
        nulls[db] = load_parts(sub, db)
        need = FALLBACK_N if fb else N_NULL_REAL
        for k in NULLS:
            if len(nulls[db].get(k, [])) != need:
                sys.exit("incomplete: %s %s has %d of %d draws" % (db, k, len(nulls[db].get(k, [])), need))
        cls[db] = classify(obs_stats(o), nulls[db])
        secs[db] = float(np.median([r["cpu_seconds"] for k in NULLS for r in nulls[db][k]]))
    v = verdict(cls["bio"], cls["abio"])
    v["hier"] = verdict_hier(cls["bio"], cls["abio"])
    v["primary_rule"] = PRIMARY_RULE
    v["primary_verdict"] = v["hier"]["verdict"] if PRIMARY_RULE == "hier" else v["verdict"]
    if dry:
        fallback = secs["bio"] > FALLBACK_SECONDS or secs["abio"] > FALLBACK_SECONDS
        blind = {db: {s: {"inside95_swap": cls[db]["per_stat"][s]["inside95_swap"],
                          "out99_both": cls[db]["per_stat"][s]["out99_both"]} for s in STATS} for db in cls}
        res = {"mode": "dryrun_standin_one_swap_rewire_blind", "script_sha256": sha256(os.path.abspath(__file__)),
               "verdict": v, "per_stat_flags": blind,
               "n_inside95_swap": {db: cls[db]["n_inside95_swap"] for db in cls},
               "n_out99_both": {db: cls[db]["n_out99_both"] for db in cls},
               "null_scan_cpu_seconds_median": secs, "fallback": bool(fallback),
               "note": "No statistic of the stand-in or of its nulls is printed or saved here; the null draws "
                       "sit in work/dryrun_blind/ (gitignored) and are the same ensemble as the real nulls."}
        print(json.dumps(res, indent=1, default=float))
        dump("t14_dryrun.json", res)
        return
    plan_kill = sum(position(obs["bio"][s], [r[s] for r in nulls["bio"].get("swap_plan", [])], Q_IN) == 0
                    for s in STATS) >= 3 if nulls["bio"].get("swap_plan") else None
    res = {"mode": "real", "script_sha256": sha256(os.path.abspath(__file__)), "fallback": fb,
           "verdict": v, "class": cls,
           "observed": {db: {k: obs[db][k] for k in STATS + ["chain_depth", "set_sizes"]} for db in obs},
           "null_quantiles": {db: {k: {s: np.quantile([r[s] for r in nulls[db][k]], [0.005, 0.025, 0.5, 0.975, 0.995]).tolist()
                                       for s in STATS + ["chain_depth"]} for k in nulls[db]} for db in nulls},
           "plan_rule_with_plan_null_kill": plan_kill, "null_scan_cpu_seconds_median": secs}
    print(json.dumps(res, indent=1, default=float))
    dump("t14_real.json", res)


if __name__ == "__main__":
    np.seterr(all="ignore")
    if MODE == "gate":
        gate()
    elif MODE == "timing":
        timing()
    elif MODE == "planted":
        planted()
    elif MODE == "planted_merge":
        planted_merge()
    elif MODE == "sealcheck":
        print(json.dumps(seal_status(), indent=1))
    elif MODE == "dryrun":
        null_part(dry=True)
    elif MODE == "dryrun_verdict":
        final(dry=True)
    elif MODE == "real":
        null_part(dry=False)
    elif MODE == "real_verdict":
        final(dry=False)
    else:
        sys.exit("unknown mode")
