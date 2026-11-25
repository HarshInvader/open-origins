"""T17 (prereg docs/prereg/t17_atom_balanced_tiers.md): do the nested autocatalytic tiers of KEGG biochemistry
(T14) survive an atom-conserving null?

Claim under test: Peng, Linderoth & Baum 2022, PLoS Comput Biol 18:e1010498 (PMC9491600): "These SDASs are
nested, with SDAS-bio-1c including the entirety of SDAS-bio-1b, which includes the entirety of SDAS-bio-1a."
T14 (sealed, support) showed degree-preserving rewires give one set and no nesting.  Its rewired reactions do
not conserve atoms.  T17 asks the same question under nulls in which every rewired reaction is atom-balanced.

Usage (single process, single thread; run under nice -n 20 with OMP/OPENBLAS threads = 1):
  python -I t17_analysis.py <experiments/t17_atom_balanced_tiers dir> gate
  python -I t17_analysis.py <dir> planted <SCEN> <REP_FROM> <REP_TO>   # synthetic networks only
  python -I t17_analysis.py <dir> planted_merge
  python -I t17_analysis.py <dir> sealcheck
  python -I t17_analysis.py <dir> dryrun <NULL> <FROM> <TO>   # real code path; one Null-B rewire of the real
  python -I t17_analysis.py <dir> dryrun_verdict              #   network stands in for it; prints flags only
  python -I t17_analysis.py <dir> real <NULL> <FROM> <TO>     # sealed; refuses without the seal
  python -I t17_analysis.py <dir> real_verdict                # sealed; merges real parts, applies rules

Reuse: expansion, tier 0, the singleton-seed scan, the LP, the statistics, the T14 loaders and the T14
synthetic generator are imported from the sealed T14 script (its sha256 is checked against the T14 seal).
Inputs: T14's S2 Table and food set (read-only, hashed by T14's own check), and the KEGG COMPOUND entries in
raw/kegg/ (gitignored, untrusted text; only the FORMULA line is parsed, by a strict regex).

Nulls (all start from the real network and keep the tier-0 system exactly; see prereg D3-D6):
  A  "isomer"  exchange single stubs (species with coefficient) whose formulas are identical.
  B  "half"    split a reaction into two halves k + g (g a nonempty proper part of its stubs; each stub keeps
               its side); exchange g with a half g' of another reaction that has the same formula difference
               (products minus reactants).  Both new reactions balance every element.
  C  "strict"  B, but the exchanged halves may not contain a frozen species (tier-0 species and the top 1% of
               species by degree), so frozen species never move.
  Bconv        reported only: B with each half a "conversion" (>= 1 reactant and >= 1 product in g and in k).
"""
import glob
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

D = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
ARGS = sys.argv[3:]
REPO = os.path.dirname(os.path.dirname(D))
SELF = "experiments/t17_atom_balanced_tiers/scripts/t17_analysis.py"
T14_DIR = os.path.join(os.path.dirname(D), "t14_autocatalytic_tiers")
T14_SCRIPT = os.path.join(T14_DIR, "scripts", "t14_analysis.py")
T14_SHA = "48ecdd36d68b3a7a281a56b85755e85c6ee67a0d212b99a0940bb5197cb57f62"   # sealed in HASHES.txt
SEED = 20261217


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


if sha256(T14_SCRIPT) != T14_SHA:
    sys.exit("T14 script hash mismatch: it must be the sealed version")
_argv = sys.argv
sys.argv = [T14_SCRIPT, T14_DIR, "lib"]
_spec = importlib.util.spec_from_file_location("t14", T14_SCRIPT)
t14 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t14)
sys.argv = _argv

STATS = t14.STATS                     # n_seeds, n_sets, nested_share, largest
HIER = ["n_sets", "nested_share"]          # kill rule (as designed)
SUPPORT = ["n_sets", "chain_depth"]         # C1 support rule, reported only (post-calibration proposal)
RSTATS = STATS + ["chain_depth"]            # statistics placed against every null
NULLS = ["A", "B", "C", "Bconv"]
DECIDING = ["B", "C"]
STEP_MULT = 20                        # attempted moves per draw = STEP_MULT x movable units (fixed by the gate)
TOP_FROZEN = 0.01


def dump(name, obj):
    os.makedirs(os.path.join(D, "scripts_out"), exist_ok=True)
    with open(os.path.join(D, "scripts_out", name), "w") as f:
        json.dump(obj, f, indent=1, default=float)
    print("wrote scripts_out/" + name, flush=True)


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


# ---------------------------------------------------------------- formulas (untrusted KEGG text)
KEGG_DIR = "raw/kegg"
ID_RE = re.compile(r"^ENTRY\s+(C\d{5})\s")
FORM_RE = re.compile(r"^FORMULA\s+(\S+)\s*$")
PLAIN_RE = re.compile(r"^(?:[A-Z][a-z]?\d*)+$")
TOK_RE = re.compile(r"([A-Z][a-z]?)(\d*)")


def kegg_hash():
    """One sha256 over the sorted batch files (name and bytes), so the formula input is fixed at the seal."""
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(D, KEGG_DIR, "batch_*.txt"))):
        h.update(os.path.basename(p).encode())
        h.update(sha256(p).encode())
    return h.hexdigest()


def read_formulas():
    """{KEGG id: formula string or None}, from the FORMULA line of each entry.  Nothing is evaluated."""
    out = {}
    for p in sorted(glob.glob(os.path.join(D, KEGG_DIR, "batch_*.txt"))):
        if os.path.getsize(p) > 20_000_000:
            sys.exit("kegg file too large: " + p)
        cur = None
        for line in open(p, encoding="utf-8", errors="replace"):
            m = ID_RE.match(line)
            if m:
                cur = m.group(1)
                out.setdefault(cur, None)
                continue
            m = FORM_RE.match(line)
            if m and cur is not None and out.get(cur) is None:
                out[cur] = m.group(1)
            if line.startswith("///"):
                cur = None
    return out


def parse_plain(f):
    """Element counts of a plain formula (no R group, no n, no brackets, no dots), else None."""
    if f is None or not PLAIN_RE.match(f):
        return None
    c = {}
    for el, n in TOK_RE.findall(f):
        c[el] = c.get(el, 0) + (int(n) if n else 1)
    if "R" in c:
        return None
    return c


def formula_vectors(names, raw):
    """Integer vectors over a fixed element list; None for a species without a plain formula."""
    parsed = {n: parse_plain(raw.get(n)) for n in names}
    els = sorted({e for c in parsed.values() if c for e in c})
    vec = [tuple(c.get(e, 0) for e in els) if c else None for c in (parsed[n] for n in names)]
    return vec, els


def balanced(net, vec, r):
    sp = list(net.lhs[r]) + list(net.rhs[r])
    if any(vec[s] is None for s in sp):
        return None
    E = len(vec[sp[0]])
    d = [0] * E
    for s, c in zip(net.lhs[r], net.lco[r]):
        for i in range(E):
            d[i] -= c * vec[s][i]
    for s, c in zip(net.rhs[r], net.rco[r]):
        for i in range(E):
            d[i] += c * vec[s][i]
    return not any(d)


# ---------------------------------------------------------------- the atom-conserving rewiring
def frozen_species(net, food):
    return t14.frozen_species(net, food)          # tier-0 species | top 1% by degree (T14's definition)


class Rewirer:
    """State of a rewiring chain over the movable units of `net`.

    unit u (forward reaction index; its partner, if any, is rebuilt as the exact reverse) has stubs
    [(species, coef, side)], side 0 = reactant, 1 = product.  A half is a bitmask over the unit's stubs.
    Movable units: atom-balanced (every species with a plain formula), not in tier 0 (neither direction fired
    from food), no species on both sides.  All other units never change."""

    def __init__(self, net, food, vec, kind):
        self.net, self.food, self.vec, self.kind = net, food, vec, kind
        avail0, fired0, _ = t14.tier0(net, food)
        self.avail0, self.fired0 = avail0, fired0
        self.E = len(next(v for v in vec if v is not None))
        self.frz = frozen_species(net, food) if kind == "C" else None
        units = t14.units_of(net)
        self.paired = {u: bool(net.partner[u] >= 0) for u in units}
        mov = []
        for u in units:
            p = net.partner[u]
            if fired0[u] or (p >= 0 and fired0[p]):
                continue
            if set(net.lhs[u]) & set(net.rhs[u]):
                continue
            if not balanced(net, vec, u):
                continue
            mov.append(u)
        self.mov = mov
        self.st = {u: [(s, c, 0) for s, c in zip(net.lhs[u], net.lco[u])] +
                      [(s, c, 1) for s, c in zip(net.rhs[u], net.rco[u])] for u in mov}
        # lazy index: (paired, delta) -> list of (u, mask) entries.  Entries are added when a unit changes and
        # never removed eagerly; a sampled entry is checked against the unit's current halves and dropped if
        # stale (the move is then rejected, like any other failed proposal).
        self.index = {}
        self.inidx = set()       # (key, u, mask) present in self.index
        self.halves = {}         # u -> list of (mask, delta), current
        self.hmap = {}           # u -> {mask: delta}, current
        self._hcache = {}
        for u in mov:
            self._add(u)

    # -- halves
    def _halves_of(self, stubs):
        """[(mask, delta)] of the eligible halves of a unit with these stubs (cached by content).
        delta = formula of the half's products minus its reactants; built bit by bit."""
        key = tuple(stubs)
        hit = self._hcache.get(key)
        if hit is not None:
            return hit
        n, E, full = len(stubs), self.E, (1 << len(stubs)) - 1
        sv = []
        for s, c, side in stubs:
            sg = c if side else -c
            sv.append(tuple(sg * x for x in self.vec[s]))
        fm = sum(1 << i for i, (s, c, side) in enumerate(stubs) if self.frz is not None and self.frz[s])
        lm = sum(1 << i for i, (s, c, side) in enumerate(stubs) if side == 0)
        rm = full ^ lm
        dl = [None] * (full + 1)
        dl[0] = (0,) * E
        out = []
        for mask in range(1, full):
            low = mask & -mask
            prev = dl[mask ^ low]
            v = sv[low.bit_length() - 1]
            d = tuple(a + b for a, b in zip(prev, v))
            dl[mask] = d
            if self.kind == "A" and mask != low:
                continue
            if self.kind == "C" and mask & fm:
                continue
            if self.kind == "Bconv":
                k = full ^ mask
                if not (mask & lm and mask & rm and k & lm and k & rm):
                    continue
            out.append((mask, d))
        out = (out, dict(out))
        self._hcache[key] = out
        return out

    def _add(self, u):
        hs, hm = self._halves_of(self.st[u])
        P = self.paired[u]
        for mask, d in hs:
            key = (P, d)
            t = (key, u, mask)
            if t not in self.inidx:
                self.inidx.add(t)
                self.index.setdefault(key, []).append((u, mask))
        self.halves[u], self.hmap[u] = hs, hm

    # -- validity
    def _ok(self, stubs):
        L = [s for s, c, side in stubs if side == 0]
        R = [s for s, c, side in stubs if side == 1]
        if not L or not R or len(set(L)) != len(L) or len(set(R)) != len(R) or set(L) & set(R):
            return False
        a = self.avail0
        if all(a[s] for s in L):                 # would fire from tier 0
            return False
        return True

    def _ok_unit(self, u, stubs):
        if not self._ok(stubs):
            return False
        if self.paired[u]:                       # the reverse must not fire from tier 0 either
            if all(self.avail0[s] for s, c, side in stubs if side == 1):
                return False
        return True

    # -- one attempted move
    def step(self, rng):
        u = self.mov[int(rng.integers(len(self.mov)))]
        hs = self.halves[u]
        if not hs:
            return False
        mask, d = hs[int(rng.integers(len(hs)))]
        P = self.paired[u]
        fwd = self.index.get((P, d), [])
        neg = tuple(-x for x in d)
        rev = self.index.get((P, neg), []) if P else []
        n = len(fwd) + len(rev)
        if n <= 1:
            return False
        j = int(rng.integers(n))
        flip = j >= len(fwd)
        lst, jj = (rev, j - len(fwd)) if flip else (fwd, j)
        v, mv = lst[jj]
        if self.hmap[v].get(mv) != (neg if flip else d):        # stale entry: drop it, reject the move
            self.inidx.discard(((P, neg if flip else d), v, mv))
            lst[jj] = lst[-1]
            lst.pop()
            return False
        if v == u:
            return False
        Su, Sv = self.st[u], self.st[v]
        g = [Su[i] for i in range(len(Su)) if mask >> i & 1]
        ku = [Su[i] for i in range(len(Su)) if not mask >> i & 1]
        g2 = [Sv[i] for i in range(len(Sv)) if mv >> i & 1]
        kv = [Sv[i] for i in range(len(Sv)) if not mv >> i & 1]
        if flip:
            g = [(s, c, 1 - side) for s, c, side in g]
            g2 = [(s, c, 1 - side) for s, c, side in g2]
        nu, nv = ku + g2, kv + g
        if not (self._ok_unit(u, nu) and self._ok_unit(v, nv)):
            return False
        self.st[u], self.st[v] = nu, nv
        self._add(u); self._add(v)
        return True

    def network(self):
        net = self.net
        lhs, lco, rhs, rco = list(net.lhs), list(net.lco), list(net.rhs), list(net.rco)
        for u in self.mov:
            S = self.st[u]
            lhs[u] = tuple(s for s, c, side in S if side == 0); lco[u] = tuple(c for s, c, side in S if side == 0)
            rhs[u] = tuple(s for s, c, side in S if side == 1); rco[u] = tuple(c for s, c, side in S if side == 1)
            b = net.partner[u]
            if b >= 0:
                lhs[b], lco[b], rhs[b], rco[b] = rhs[u], rco[u], lhs[u], lco[u]
        out = t14.Net(net.names, lhs, lco, rhs, rco, net.partner)
        a1, f1, _ = t14.tier0(out, self.food)
        if not ((a1 == self.avail0).all() and (f1 == self.fired0).all()):
            raise RuntimeError("rewire changed tier 0")
        return out


def rewire(net, food, vec, kind, rng, mult=STEP_MULT, checkpoints=None):
    rw = Rewirer(net, food, vec, kind)
    n_steps = mult * len(rw.mov)
    acc = 0
    snaps = {}
    cps = sorted(checkpoints or [])
    for t in range(1, n_steps + 1):
        acc += rw.step(rng)
        if cps and t == int(cps[0] * len(rw.mov)):
            snaps[cps.pop(0)] = rw.network()
    return rw.network(), {"n_movable_units": len(rw.mov), "n_steps": n_steps, "accepted": acc,
                          "accept_rate": acc / max(n_steps, 1)}, snaps


# ---------------------------------------------------------------- invariants and mixing (structure only)
def sig(net, r):
    return (tuple(sorted(zip(net.lhs[r], net.lco[r]))), tuple(sorted(zip(net.rhs[r], net.rco[r]))))


def invariants(net, new, vec):
    def role(n):
        a = np.zeros(n.n_sp, np.int64); b = np.zeros(n.n_sp, np.int64)
        for L, R in zip(n.lhs, n.rhs):
            a[list(L)] += 1; b[list(R)] += 1
        return a, b
    a0, b0 = role(net); a1, b1 = role(new)
    bal_before = sum(1 for r in range(net.n_rx) if balanced(net, vec, r))
    bal_after = sum(1 for r in range(new.n_rx) if balanced(new, vec, r))
    pair_ok = all(sig(new, r)[0] == sig(new, new.partner[r])[1] and sig(new, r)[1] == sig(new, new.partner[r])[0]
                  for r in range(new.n_rx) if new.partner[r] >= 0)
    return {"role_counts_kept": bool((a0 == a1).all() and (b0 == b1).all()),
            "balanced_before": bal_before, "balanced_after": bal_after, "reverse_pairs_exact": bool(pair_ok)}


def mixing(net, new, idx):
    """Share of the reactions in `idx` (directed) whose exact reaction (sides, coefficients) no longer exists in
    the copy, and the Jaccard overlap of the two networks' reaction sets (all directed reactions)."""
    real_all = {sig(net, r) for r in range(net.n_rx)}
    new_all = {sig(new, r) for r in range(new.n_rx)}
    changed = sum(1 for r in idx if sig(net, r) not in new_all)
    return {"share_changed": changed / len(idx), "n_changed": changed, "n_ref": len(idx),
            "jaccard": len(real_all & new_all) / len(real_all | new_all)}


def skeleton_mixing(net, new, idx, frz):
    """Same, with frozen species (hubs, tier-0 species) deleted from every reaction (reported only)."""
    def sk(n, r):
        return (tuple(sorted(s for s in n.lhs[r] if not frz[s])), tuple(sorted(s for s in n.rhs[r] if not frz[s])))
    new_all = {sk(new, r) for r in range(new.n_rx)}
    real_all = {sk(net, r) for r in range(net.n_rx)}
    changed = sum(1 for r in idx if sk(net, r) not in new_all)
    return {"share_changed": changed / len(idx), "jaccard": len(real_all & new_all) / len(real_all | new_all)}


# ---------------------------------------------------------------- decision rules
Q_IN, Q_OUT = (0.025, 0.975), (0.005, 0.995)


def position(obs, vals, q):
    lo, hi = np.quantile(np.asarray(vals, float), q)
    return 0 if lo <= obs <= hi else (1 if obs > hi else -1)


def classify(obs, nulls):
    out = {}
    for k, rows in nulls.items():
        out[k] = {s: {"inside95": position(obs[s], [r[s] for r in rows], Q_IN) == 0,
                      "out99": position(obs[s], [r[s] for r in rows], Q_OUT)} for s in RSTATS}
    return out


def verdict(cls):
    """Deciding rules are the design's (prereg, decision rules), unchanged after calibration:
    Kill: n_sets and nested_share both inside the central 95% of Null B.
    Support: n_sets and nested_share both above the central 99% of Null B and of Null C.
    Otherwise "not killed".  The planted check showed the design's support rule cannot fire when
    nested_share is 1.0 in real and in >0.5% of null draws, so in practice the sealed outcomes are kill or not killed.
    support_c1_reported_only: n_sets and chain_depth above the central 99% of B and C. Proposed after the
    planted check (prereg C1); a post-calibration change, so it is reported only and never decides."""
    kill = all(cls["B"][s]["inside95"] for s in HIER)
    design = (not kill) and all(cls[k][s]["out99"] > 0 for k in DECIDING for s in HIER)
    c1 = (not kill) and all(cls[k][s]["out99"] > 0 for k in DECIDING for s in SUPPORT)
    rep = {k: all(cls[k][s]["out99"] > 0 for s in HIER) for k in cls}
    rep_c1 = {k: all(cls[k][s]["out99"] > 0 for s in SUPPORT) for k in cls}
    return {"verdict": "kill" if kill else ("support" if design else "not killed"), "kill": kill, "support": design,
            "flagged_by_null": rep, "support_c1_reported_only": c1, "flagged_by_null_c1_reported_only": rep_c1}


# ---------------------------------------------------------------- real network
KEGG_SHA = "c6f6dbf06324e91014a01219127388bf4e08b14948dd8cfe2ef572de8bab4791"   # kegg_hash() of the 2026-11-25 fetch


def load_real():
    t14.check_inputs()
    if kegg_hash() != KEGG_SHA:
        sys.exit("KEGG input hash mismatch (prereg F5)")
    net, food, miss = t14.load_db("bio")
    raw = read_formulas()
    vec, els = formula_vectors(net.names, raw)
    return net, food, vec, els, raw


def gate():
    res = {"mode": "gate", "script_sha256": sha256(os.path.abspath(__file__)), "t14_script_sha256": T14_SHA,
           "kegg_batches_sha256": kegg_hash(),
           "kegg_n_batch_files": len(glob.glob(os.path.join(D, KEGG_DIR, "batch_*.txt")))}
    net, food, vec, els, raw = load_real()
    # 1. T14 gate numbers (the observed network; published values)
    o = t14.scan(net, food)
    res["t14_reproduced"] = {"species": net.n_sp, "reactions": net.n_rx, "tier0": [o["tier0_species"], o["tier0_reactions"]],
                             "n_candidates": o["n_candidates"], "stats": {k: o[k] for k in STATS},
                             "chain_depth": o["chain_depth"], "set_sizes": o["set_sizes"],
                             "cpu_seconds_full_scan": o["cpu_seconds"]}
    ok1 = (net.n_sp == 4216 and net.n_rx == 8402 and o["n_seeds"] == 304 and o["n_sets"] == 3
           and o["nested_share"] == 1.0 and [x[0] for x in o["set_sizes"]] == [1414, 357, 301]
           and [o["tier0_species"], o["tier0_reactions"]] == [30, 44])
    res["gate1_t14_pass"] = bool(ok1)
    # formulas and balance (structure only)
    n_entry = sum(1 for n in net.names if n in raw)
    n_form = sum(1 for n in net.names if raw.get(n) is not None)
    n_plain = sum(1 for v in vec if v is not None)
    bal = [balanced(net, vec, r) for r in range(net.n_rx)]
    res["formulas"] = {"species": net.n_sp, "kegg_entries_found": n_entry, "with_formula_line": n_form,
                       "plain_formula": n_plain, "elements": els,
                       "no_plain_formula": sorted(n for n, v in zip(net.names, vec) if v is None)}
    res["balance"] = {"balanced": sum(1 for b in bal if b is True), "unbalanced": sum(1 for b in bal if b is False),
                      "touch_species_without_formula": sum(1 for b in bal if b is None)}
    bal_idx = [r for r in range(net.n_rx) if bal[r] is True]
    frz = frozen_species(net, food)
    # 2. mixing gate: a few draws per null, rewiring only (no network scan of any null copy)
    mix = {}
    for ki, kind in enumerate(NULLS):
        rows = []
        n_draw = 5 if kind == "B" else 2
        for i in range(n_draw):
            rng = np.random.default_rng([SEED, 1, ki, i])
            t = time.process_time()
            new, info, snaps = rewire(net, food, vec, kind, rng, checkpoints=[1, 2, 5, 10] if i == 0 else None)
            info["cpu_seconds_rewire"] = round(time.process_time() - t, 2)
            row = info | mixing(net, new, bal_idx) | {"skeleton": skeleton_mixing(net, new, bal_idx, frz)}
            if i == 0:
                row["invariants"] = invariants(net, new, vec)
                row["share_changed_by_mult"] = {str(m): round(mixing(net, sn, bal_idx)["share_changed"], 4)
                                                for m, sn in snaps.items()} | {str(STEP_MULT): round(row["share_changed"], 4)}
            rows.append(row)
            print(kind, i, json.dumps({k: v for k, v in row.items() if k != "skeleton"}), flush=True)
        mix[kind] = {"draws": rows,
                     "mean_share_changed": float(np.mean([r["share_changed"] for r in rows])),
                     "mean_jaccard": float(np.mean([r["jaccard"] for r in rows])),
                     "mean_skeleton_share_changed": float(np.mean([r["skeleton"]["share_changed"] for r in rows])),
                     "mean_skeleton_jaccard": float(np.mean([r["skeleton"]["jaccard"] for r in rows]))}
    res["mixing"] = mix
    mb = mix["B"]
    res["gate2_mixing_pass"] = bool(mb["mean_share_changed"] >= 0.30 and mb["mean_jaccard"] < 0.80)
    # structure of the formula-difference classes (how much freedom the atom rule leaves)
    rw = Rewirer(net, food, vec, "B")
    sizes = sorted((len(v) for v in rw.index.values()), reverse=True)
    units_with_partner = sum(1 for u in rw.mov if any(
        len(rw.index.get((True, d), [])) + len(rw.index.get((True, tuple(-x for x in d)), [])) > 1
        for m, d in rw.halves[u]))
    res["freedom_B"] = {"movable_units": len(rw.mov), "units_total": len(t14.units_of(net)),
                        "movable_units_with_any_partner_half": units_with_partner,
                        "n_delta_classes": len(sizes), "largest_classes": sizes[:10],
                        "classes_of_size_1": sum(1 for s in sizes if s == 1)}
    print(json.dumps({k: res[k] for k in ["gate1_t14_pass", "formulas", "balance", "gate2_mixing_pass", "freedom_B"]},
                     default=float, indent=1)[:4000])
    dump("t17_gate.json", res)


# ---------------------------------------------------------------- synthetic networks (planted check)
# T14's generator (sparse world): every background and planted reaction conserves an integer "mass".  Here the
# mass is the only "element", so each species' formula is a one-element vector.  The small (abiotic) network is
# not used: T17 rules on the biochemical network only.
N_NULL_PLANTED = 50           # per null per network (the real run uses N_NULL_REAL); cut from 100 for time
NULLS_PLANTED = ["A", "B", "C"]      # Bconv is reported only and is not run in the planted check (time)
SCEN = {"sparse_planted": (3, False), "sparse_samedeg": (3, True), "sparse_background": (0, False)}
SCEN_CODE = {k: i for i, k in enumerate(SCEN)}


def planted():
    name, r0, r1 = ARGS[0], int(ARGS[1]), int(ARGS[2])
    n_cores, samedeg = SCEN[name]
    rows = []
    for rep in range(r0, r1):
        t = time.time()
        rng = np.random.default_rng([t14.SEED, 1, 0, rep, len("big")])
        parts = t14.gen_background(rng, t14.WORLDS["sparse"]["big"])
        if n_cores:
            t14.plant_cores(rng, parts, n_cores, t14.CORE_M["big"], reversible=True)
        names, lhs, lco, rhs, rco, partner, food, mass = parts
        net = t14.Net(names, lhs, lco, rhs, rco, partner)
        vec = [(int(m),) for m in mass]
        if samedeg:   # same degrees, atom-balanced, cores broken by one Null-B rewire
            net, _, _ = rewire(net, food, vec, "B", np.random.default_rng([SEED, 2, rep]))
        o = t14.scan(net, food)
        obs = {k: o[k] for k in RSTATS}
        nulls, mixs, secs = {}, {}, []
        bal_idx = [r for r in range(net.n_rx) if balanced(net, vec, r)]
        for ki, kind in enumerate(NULLS_PLANTED):
            rr, mm = [], []
            for i in range(N_NULL_PLANTED):
                g = np.random.default_rng([SEED, 3, SCEN_CODE[name], rep, ki, i])
                nn, info, _ = rewire(net, food, vec, kind, g)
                s = t14.scan(nn, food)
                rr.append({k: s[k] for k in STATS + ["chain_depth"]})
                secs.append(s["cpu_seconds"])
                if i < 5:
                    mm.append(mixing(net, nn, bal_idx)["share_changed"])
            nulls[kind] = rr
            mixs[kind] = float(np.mean(mm))
        cls = classify(obs, nulls)
        v = verdict(cls)
        res = {"scenario": name, "rep": rep, "obs": obs | {"chain_depth": o["chain_depth"]},
               "set_sizes_top6": o["set_sizes"][:6],
               "nulls": {k: {s: [r[s] for r in rr] for s in STATS + ["chain_depth"]} for k, rr in nulls.items()},
               "mixing_share_changed_mean5": mixs, "verdict": v,
               "null_scan_cpu_median": float(np.median(secs)), "seconds": round(time.time() - t, 1)}
        print(json.dumps({"scenario": name, "rep": rep, "obs": res["obs"], "verdict": v["verdict"],
                          "flagged": v["flagged_by_null"], "mix": mixs,
                          "null_median_nsets": {k: float(np.median(res["nulls"][k]["n_sets"])) for k in NULLS_PLANTED},
                          "sec": res["seconds"]}), flush=True)
        rows.append(res)
    dump("t17_planted_part_%s_%d-%d.json" % (name, r0, r1),
         {"script_sha256": sha256(os.path.abspath(__file__)), "n_null": N_NULL_PLANTED, "rows": rows})


def planted_merge():
    parts = sorted(glob.glob(os.path.join(D, "scripts_out", "t17_planted_part_*.json")))
    by, hashes = {}, set()
    for p in parts:
        j = json.load(open(p))
        hashes.add(j["script_sha256"])
        for r in j["rows"]:
            nulls = {k: [dict(zip(RSTATS, x)) for x in zip(*[r["nulls"][k][s] for s in RSTATS])] for k in r["nulls"]}
            v = verdict(classify(r["obs"], nulls))
            by.setdefault(r["scenario"], {})[r["rep"]] = {"v": v, "r": r}
    table = {}
    for name, reps in by.items():
        vs = [x["v"] for x in reps.values()]
        rs = [x["r"] for x in reps.values()]
        table[name] = {
            "n_rep": len(vs),
            "rule": {"kill": sum(x["kill"] for x in vs), "support": sum(x["support"] for x in vs),
                     "not_killed": sum(x["verdict"] == "not killed" for x in vs)},
            "flagged_by_null": {k: sum(x["flagged_by_null"][k] for x in vs) for k in NULLS_PLANTED},
            "flagged_by_A_B_C": sum(all(x["flagged_by_null"][k] for k in ["A", "B", "C"]) for x in vs),
            "c1_reported_only": {"support": sum(x["support_c1_reported_only"] for x in vs),
                                 "flagged_by_null": {k: sum(x["flagged_by_null_c1_reported_only"][k] for x in vs)
                                                     for k in NULLS_PLANTED},
                                 "flagged_by_A_B_C": sum(all(x["flagged_by_null_c1_reported_only"][k] for k in ["A", "B", "C"])
                                                         for x in vs)},
            "null_draws_with_any_nested_pair": {k: float(np.mean([np.mean(np.asarray(r["nulls"][k]["nested_share"]) > 0)
                                                                  for r in rs])) for k in NULLS_PLANTED},
            "mean_obs": {s: float(np.mean([r["obs"][s] for r in rs])) for s in STATS + ["chain_depth"]},
            "mean_null_median": {k: {s: float(np.mean([np.median(r["nulls"][k][s]) for r in rs])) for s in STATS}
                                 for k in NULLS_PLANTED},
            "mean_null_q995": {k: {s: float(np.mean([np.quantile(r["nulls"][k][s], 0.995) for r in rs]))
                                   for s in HIER + ["chain_depth"]}
                               for k in NULLS_PLANTED},
            "mean_mixing_share_changed": {k: float(np.mean([r["mixing_share_changed_mean5"][k] for r in rs]))
                                          for k in NULLS_PLANTED},
            "median_null_scan_cpu": float(np.median([r["null_scan_cpu_median"] for r in rs])),
        }
    out = {"rules_applied_by_script_sha256": sha256(os.path.abspath(__file__)),
           "parts_computed_by_script_sha256": sorted(hashes), "n_null_per_network": N_NULL_PLANTED,
           "table": table, "parts": [os.path.basename(p) for p in parts]}
    print(json.dumps(table, indent=1))
    dump("t17_planted.json", out)


# ---------------------------------------------------------------- real and dry run
N_NULL_REAL = {"A": 200, "B": 200, "C": 200, "Bconv": 100}
FALLBACK_SECONDS = 60.0
FALLBACK_N, FALLBACK_SEEDS = 100, 1000


def standin():
    net, food, vec, els, raw = load_real()
    nn, _, _ = rewire(net, food, vec, "B", np.random.default_rng([SEED, 99]))
    return nn, food, vec


def fallback_state():
    p = os.path.join(D, "scripts_out", "t17_dryrun.json")
    if not os.path.exists(p):
        sys.exit("REFUSED: run the dry run first; it fixes whether the time fallback applies.")
    return json.load(open(p))["fallback"]


def null_part(dry):
    kind, i0, i1 = ARGS[0], int(ARGS[1]), int(ARGS[2])
    if kind not in NULLS:
        sys.exit("unknown null")
    if not dry:
        st = seal_status()
        if not st["real_allowed"]:
            sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                     % (SELF, st["script_sha256"]))
        fb = fallback_state()
        net, food, vec, _, _ = load_real()
    else:
        fb = False
        net, food, vec = standin()
    nmax = FALLBACK_N if (fb and kind != "Bconv") else N_NULL_REAL[kind]
    i1 = min(i1, nmax)
    sample = FALLBACK_SEEDS if fb else None
    bal_idx = [r for r in range(net.n_rx) if balanced(net, vec, r)]
    rows = []
    for i in range(i0, i1):
        rng = np.random.default_rng([SEED, 5 if dry else 6, NULLS.index(kind), i])
        nn, info, _ = rewire(net, food, vec, kind, rng)
        o = t14.scan(nn, food, seeds_sample=sample, rng=rng)
        rows.append({k: o[k] for k in STATS + ["chain_depth", "cpu_seconds", "n_lp"]} |
                    {"i": i, "accept_rate": info["accept_rate"]} | mixing(net, nn, bal_idx))
    sub = "work/dryrun_blind" if dry else "scripts_out/real_parts"
    os.makedirs(os.path.join(D, sub), exist_ok=True)
    fn = os.path.join(D, sub, "bio_%s_%d-%d.json" % (kind, i0, i1))
    json.dump({"script_sha256": sha256(os.path.abspath(__file__)), "null": kind, "fallback": fb, "rows": rows},
              open(fn, "w"))
    secs = [r["cpu_seconds"] for r in rows]
    print(json.dumps({"wrote": os.path.relpath(fn, D), "n": len(rows),
                      "scan_cpu_seconds_median": float(np.median(secs)) if secs else None}), flush=True)


def final(dry):
    if not dry:
        st = seal_status()
        if not st["real_allowed"]:
            sys.exit("REFUSED: docs/prereg/HASHES.txt has no line naming %s with its current sha256 (%s)."
                     % (SELF, st["script_sha256"]))
        fb = fallback_state()
        net, food, vec, _, _ = load_real()
    else:
        fb = False
        net, food, vec = standin()
    sub = "work/dryrun_blind" if dry else "scripts_out/real_parts"
    rows = {}
    for p in sorted(glob.glob(os.path.join(D, sub, "bio_*.json"))):
        j = json.load(open(p))
        for r in j["rows"]:
            rows.setdefault(j["null"], {})[r["i"]] = r
    nulls = {k: [v[i] for i in sorted(v)] for k, v in rows.items()}
    for k in NULLS:
        need = FALLBACK_N if (fb and k != "Bconv") else N_NULL_REAL[k]
        if len(nulls.get(k, [])) != need:
            sys.exit("incomplete: %s has %d of %d draws" % (k, len(nulls.get(k, [])), need))
    o = t14.scan(net, food, seeds_sample=FALLBACK_SEEDS if fb else None, rng=np.random.default_rng([SEED, 7]))
    obs = {k: o[k] for k in RSTATS}
    cls = classify(obs, nulls)
    v = verdict(cls)
    secs = float(np.median([r["cpu_seconds"] for k in DECIDING for r in nulls[k]]))
    mixB = {"mean_share_changed": float(np.mean([r["share_changed"] for r in nulls["B"]])),
            "mean_jaccard": float(np.mean([r["jaccard"] for r in nulls["B"]]))}
    mixB["pass"] = mixB["mean_share_changed"] >= 0.30 and mixB["mean_jaccard"] < 0.80
    if dry:
        res = {"mode": "dryrun_standin_one_B_rewire_blind", "script_sha256": sha256(os.path.abspath(__file__)),
               "verdict": v["verdict"],
               "flags": {k: {s: {"inside95": cls[k][s]["inside95"], "out99": cls[k][s]["out99"]} for s in RSTATS}
                         for k in cls},
               "null_scan_cpu_seconds_median": secs, "fallback": bool(secs > FALLBACK_SECONDS),
               "note": "No statistic of the stand-in or its nulls is printed or saved; draws in work/dryrun_blind/."}
        print(json.dumps(res, indent=1, default=float))
        dump("t17_dryrun.json", res)
        return
    if not mixB["pass"]:
        v = v | {"verdict": "not decidable", "reason": "Null B mixing in the real draws below the gate thresholds"}
    res = {"mode": "real", "script_sha256": sha256(os.path.abspath(__file__)), "fallback": fb, "verdict": v,
           "class": cls, "observed": obs | {"chain_depth": o["chain_depth"], "set_sizes": o["set_sizes"]},
           "null_quantiles": {k: {s: np.quantile([r[s] for r in nulls[k]], [0.005, 0.025, 0.5, 0.975, 0.995]).tolist()
                                  for s in STATS + ["chain_depth"]} for k in nulls},
           "mixing_B_real_draws": mixB, "null_scan_cpu_seconds_median": secs}
    print(json.dumps(res, indent=1, default=float))
    dump("t17_real.json", res)


if __name__ == "__main__":
    np.seterr(all="ignore")
    if MODE == "gate":
        gate()
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
