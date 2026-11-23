"""K5 small-LUCA world: simulate gene families born on the two domain stems, on an existing
simulation's complete species tree, and merge them with a subset of that simulation's families.

Usage:
  python -I stemsim.py validate <simdir> <out.json> [--n 600] [--seed 1]
  python -I stemsim.py tune <simdir> <out.json> --lam L [--seed 1]
  python -I stemsim.py build <simdir> <outdir> --n-stem N --lam L [--seed 1]
  python -I stemsim.py summary <simdir_or_world> <out.json>

Gene-family process (matches the Zombi Gm settings used in K2-K4, prereg v5b/v5c):
  per-family rates d, t, l drawn lognormal with mean dup/transfer/loss and sigma (rate_spec in
  simulate.py); each gene copy duplicates (rate d), is lost (l) or is copied by transfer (t) into a
  lineage drawn uniformly from the other lineages alive at that time (additive, no replacement); at
  a speciation every copy passes to both children; at an extinction its copies die. No genome-size
  floor (Zombi's MIN_GENOME_SIZE floor only blocks losses in genomes under 10 genes).
Stem extra (K5, prereg v6): a copy on a stem lineage also transfers at rate X to a lineage drawn
  uniformly from the lineages of the OTHER domain's whole clade alive at that time (its stem, dead
  side lineages, or early crown lineages). The two stems overlap in time only briefly (seed 1:
  0.006 of 1.0), so a stem-to-stem-only target would almost never be available.
Stems: the complete-tree lineages from the sampled MRCA (exclusive) to each domain's sampled crown
  (inclusive), as in pipeline/stem_transfers.py, plus every side subtree branching off them in which
  no lineage survives to the present.
Origination: N_STEM families, each born at a point drawn uniformly by length over all stem
  branches. All are kept whatever their fate (no selection on outcome).
validate: N families born at time 0 on the root lineage, no stem extra; compared with the
  simulation's own initial-genome families (ids <= initial_genome_size) on sampled-genome summaries.
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np
from ete3 import Tree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pipeline"))
from common import read_tsv, write_json  # noqa: E402


# ------------------------------------------------------------------ species tree
class Species:
    def __init__(self, sim):
        self.sim = sim
        rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(sim, "zombi", "T", "Events.tsv")).readlines()[1:]]
        self.events = []                         # (time, kind, nodes)
        self.parent, self.children, self.birth, self.end = {}, {}, {"Root": 0.0}, {}
        self.present = max(float(t) for t, e, n in rows)
        for t, e, n in rows:
            t = float(t)
            h = n.split(";")
            if e == "S":
                p, c1, c2 = h[0], h[1], h[2]
                self.parent[c1] = self.parent[c2] = p
                self.children[p] = (c1, c2)
                self.birth[c1] = self.birth[c2] = t
                self.end[p] = t
                self.events.append((t, "S", (p, c1, c2)))
            elif e == "E":
                self.end[h[0]] = t
                self.events.append((t, "E", (h[0],)))
            elif e == "F":
                self.end[h[0]] = self.present
        self.events.sort(key=lambda x: x[0])
        sp = Tree(open(os.path.join(sim, "sample", "species_tree.nwk")).readline().strip(), format=1)
        self.mrca = sp.get_tree_root().name
        self.crowns = [c.name for c in sp.get_tree_root().get_children()]
        self.sampled = set(sp.get_leaf_names())
        dom = {r["species"]: r["domain"] for r in read_tsv(os.path.join(sim, "sample", "domains.tsv"))}
        self.dom = dom
        self.extant = {n for n, t in self.end.items() if t == self.present and n not in self.children}
        self.stems = [self._stem(c) for c in self.crowns]
        # each domain's whole complete-tree clade: descendants of the MRCA's child toward that crown
        self.clades = []
        for c in self.crowns:
            x = c
            while self.parent[x] != self.mrca:
                x = self.parent[x]
            self.clades.append(set(self._desc(x)))

    def _desc(self, n):
        out, st = [], [n]
        while st:
            x = st.pop()
            out.append(x)
            st.extend(self.children.get(x, ()))
        return out

    def _stem(self, crown):
        path, x = [], crown
        while x != self.mrca:
            path.append(x)
            x = self.parent[x]
        s = set(path)
        for x in path:
            if x == crown:
                continue
            for c in self.children.get(x, ()):
                if c in s:
                    continue
                sub = self._desc(c)
                if not any(y in self.extant for y in sub):
                    s.update(sub)
        return s

    def length(self, n):
        return self.end[n] - self.birth[n]


# ------------------------------------------------------------------ one family
def draw_rate(rng, mean, sigma):
    if mean <= 0:
        return 0.0
    if sigma <= 0:
        return mean
    return float(rng.lognormal(math.log(mean) - sigma ** 2 / 2.0, sigma))


class Node:
    __slots__ = ("lin", "t0", "t1", "kids", "name")

    def __init__(self, lin, t0):
        self.lin, self.t0, self.t1, self.kids, self.name = lin, t0, None, [], None


def simulate_family(S, rng, rates, lin0, t0, x_stem=0.0):
    """Returns (root Node, list of extant leaf Nodes, counters)."""
    d, tr, l = rates
    alive = {n for n in S.birth if S.birth[n] <= t0 < S.end[n]}
    if lin0 not in alive:
        raise RuntimeError("origin lineage %s not alive at %f" % (lin0, t0))
    root = Node(lin0, t0)
    copies = [root]                              # live gene copies
    stem_of = {}
    for i, st in enumerate(S.stems):
        for n in st:
            stem_of[n] = i
    ctr = {"D": 0, "T": 0, "L": 0, "Tstem": 0, "Xnone": 0, "mrca": 0}
    ev_i = 0
    while ev_i < len(S.events) and S.events[ev_i][0] <= t0:
        ev_i += 1
    t = t0
    while copies:
        t_next = S.events[ev_i][0] if ev_i < len(S.events) else S.present
        n_stem = sum(1 for c in copies if c.lin in stem_of) if x_stem > 0 else 0
        base = len(copies) * (d + tr + l)
        total = base + n_stem * x_stem
        dt = rng.exponential(1.0 / total) if total > 0 else math.inf
        if t + dt < t_next:
            t += dt
            u = rng.random() * total
            if u < base:
                c = copies[min(int(u // (d + tr + l)), len(copies) - 1)]
                k = (u % (d + tr + l))
                kind = "D" if k < d else ("T" if k < d + tr else "L")
            else:
                stems = [c for c in copies if c.lin in stem_of]
                c = stems[min(int((u - base) // x_stem), len(stems) - 1)]
                kind = "X"
            if kind == "L":
                c.t1 = t
                copies.remove(c)
                ctr["L"] += 1
                continue
            if kind == "D":
                rec = c.lin
            elif kind == "T":
                cand = sorted(n for n in alive if n != c.lin)  # sorted: set order varies per process
                if not cand:
                    continue
                rec = cand[int(rng.integers(len(cand)))]
            else:
                other = S.clades[1 - stem_of[c.lin]]
                cand = sorted(n for n in alive if n in other)
                if not cand:
                    ctr["Xnone"] += 1
                    continue
                rec = cand[int(rng.integers(len(cand)))]
            a, b = Node(c.lin, t), Node(rec, t)
            c.t1, c.kids = t, [a, b]
            copies.remove(c)
            copies += [a, b]
            ctr["D" if kind == "D" else "T"] += 1
            if kind == "X":
                ctr["Tstem"] += 1
            continue
        # species event (or the present)
        t = t_next
        if ev_i >= len(S.events):
            break
        _, kind, nodes = S.events[ev_i]
        ev_i += 1
        if kind == "S":
            p, c1, c2 = nodes
            if p == S.mrca:
                ctr["mrca"] = sum(1 for c in copies if c.lin == p)
            alive.discard(p)
            alive.update((c1, c2))
            new = []
            for c in copies:
                if c.lin == p:
                    a, b = Node(c1, t), Node(c2, t)
                    c.t1, c.kids = t, [a, b]
                    new += [a, b]
                else:
                    new.append(c)
            copies = new
        else:
            (n,) = nodes
            alive.discard(n)
            for c in [c for c in copies if c.lin == n]:
                c.t1 = t
                copies.remove(c)
    for c in copies:
        c.t1 = S.present
    leaves = [c for c in copies if c.lin in S.extant]
    return root, leaves, ctr


def to_newick(root, keep):
    """Gene tree pruned to the leaf Nodes in keep, unary nodes suppressed (branch lengths summed)."""
    keep = set(map(id, keep))

    def rec(n):
        if not n.kids:
            return (n.name, n.t1 - n.t0) if id(n) in keep else None
        subs = [s for s in (rec(k) for k in n.kids) if s is not None]
        if not subs:
            return None
        if len(subs) == 1:
            s, bl = subs[0]
            return s, bl + (n.t1 - n.t0)
        return "(%s)" % ",".join("%s:%.8g" % s for s in subs), n.t1 - n.t0

    r = rec(root)
    return None if r is None else r[0] + ";"


def family_record(S, rng, rates, lin0, t0, x_stem, fam, gid0):
    """rng drives the family's events only (birth point and rates are drawn by the caller)."""
    root, leaves, ctr = simulate_family(S, rng, rates, lin0, t0, x_stem)
    sampled = [c for c in leaves if c.lin in S.sampled]
    for i, c in enumerate(sorted(sampled, key=lambda c: (int(c.lin[1:]), c.t0))):
        c.name = "%s_%d" % (c.lin, gid0 + i)
    nA = len({c.lin for c in sampled if S.dom[c.lin] == "A"})
    nB = len({c.lin for c in sampled if S.dom[c.lin] == "B"})
    nwk = to_newick(root, sampled) if len(sampled) >= 2 else None
    return {"family": fam, "n_genes": len(sampled), "nA": nA, "nB": nB, "nwk": nwk,
            "genes": [(c.name, c.lin) for c in sampled], "ctr": ctr, "origin": lin0, "t0": t0}


def stem_segments(S):
    segs = [(nm, S.birth[nm], S.end[nm]) for st in S.stems for nm in sorted(st, key=lambda x: int(x[1:]))]
    L = np.array([e - b for _, b, e in segs])
    return segs, L


def stem_point(S, rng):
    segs, L = stem_segments(S)
    i = int(rng.choice(len(segs), p=L / L.sum()))
    nm, b, e = segs[i]
    return nm, b + rng.random() * (e - b)


def stem_tau(S):
    """Mean time a copy born at a uniform stem point spends on the stems before leaving them by
    descent (its stem path reaches the crown's end, or its side lineage dies). Used to set
    x = lambda / tau, so lambda = expected stem-to-other-stem transfers per founding copy (no D/L)."""
    segs, L = stem_segments(S)
    stem_of = {n: i for i, st in enumerate(S.stems) for n in st}

    def exit_time(nm):
        # follow the stem path downward: on the path to the crown, the remaining stem ends at the
        # crown lineage's end; on a dead side subtree, at the latest death below nm
        best, st = S.end[nm], [nm]
        while st:
            y = st.pop()
            best = max(best, S.end[y])
            st.extend(c for c in S.children.get(y, ()) if c in S.stems[stem_of[nm]])
        return best

    tot = 0.0
    for (nm, b, e), l in zip(segs, L):
        ex = exit_time(nm)
        # integral over t0 in [b,e] of (ex - t0) dt / l = ex - (b+e)/2
        tot += l * (ex - (b + e) / 2.0)
    return tot / L.sum(), float(L.sum())


def stem_family(S, g, seed, lam_code, i, x, base_id, gid0):
    """Stem-born family i: its own rng, so a world with N families is a prefix of one with N' > N."""
    rng_a = np.random.default_rng([seed, i])            # birth point and rates: paired across lambda
    lin, t0 = stem_point(S, rng_a)
    rates = tuple(draw_rate(rng_a, g[k], g["family_rate_sigma"]) for k in ("duplication", "transfer", "loss"))
    return family_record(S, np.random.default_rng([seed, lam_code, i]), rates, lin, t0, x,
                         str(base_id + i), gid0 + i * 10000)


# ------------------------------------------------------------------ summaries
def summarize(rows, nA_tot, nB_tot):
    """Phyletic summaries over families present in >= 1 sampled genome (K5 matching rows 1-6)."""
    pres = [r for r in rows if r["n_genes"] > 0]
    both = [r for r in pres if r["nA"] > 0 and r["nB"] > 0]
    broad = [r for r in pres if r["nA"] >= 0.25 * nA_tot and r["nB"] >= 0.25 * nB_tot]
    occ = [r["nA"] + r["nB"] for r in pres]
    occupied = sum(occ)
    return {"n_present": len(pres), "frac_both_domains": len(both) / max(1, len(pres)),
            "n_broad_both": len(broad), "n_ge2_genes": sum(1 for r in pres if r["n_genes"] >= 2),
            "genome_families_A": sum(r["nA"] for r in pres) / nA_tot,
            "genome_families_B": sum(r["nB"] for r in pres) / nB_tot,
            "single_species_frac": sum(1 for o in occ if o == 1) / max(1, len(pres)),
            "mean_copies_per_occupied": sum(r["n_genes"] for r in pres) / max(1, occupied),
            "occupancy": occ}


def compare(small, big):
    """K5 matching table (prereg v6): True = within tolerance."""
    def rel(k):
        return abs(small[k] - big[k]) / big[k]
    return {
        "row1_frac_both_domains": abs(small["frac_both_domains"] - big["frac_both_domains"]) <= 0.03,
        "row2_n_broad_both": rel("n_broad_both") <= 0.10,
        "row3_n_ge2_genes": rel("n_ge2_genes") <= 0.05,
        "row4_occupancy_ks": ks(small["occupancy"], big["occupancy"]) < 0.10,
        "row5_genome_size": rel("genome_families_A") <= 0.10 and rel("genome_families_B") <= 0.10,
        "row6_copies_single": rel("mean_copies_per_occupied") <= 0.10 and rel("single_species_frac") <= 0.10,
        "occupancy_ks_D": ks(small["occupancy"], big["occupancy"]),
    }


def sim_rows(sim):
    return [{"family": r["family"], "n_genes": int(r["n_genes"]), "nA": int(r["n_genomes_A"]),
             "nB": int(r["n_genomes_B"]), "luca": int(r["luca"])}
            for r in read_tsv(os.path.join(sim, "sample", "truth.tsv"))]


def ks(a, b):
    a, b = np.sort(a), np.sort(b)
    xs = np.union1d(a, b)
    return float(np.max(np.abs(np.searchsorted(a, xs, "right") / len(a) - np.searchsorted(b, xs, "right") / len(b))))


# ------------------------------------------------------------------ commands
def cfg_of(sim):
    return json.load(open(os.path.join(sim, "config.json")))


def cmd_validate(a):
    S = Species(a.simdir)
    g = cfg_of(a.simdir)["genome"]
    rng = np.random.default_rng(a.seed)
    nA_tot = sum(1 for v in S.dom.values() if v == "A")
    nB_tot = len(S.dom) - nA_tot
    mine = []
    segs = [(n, S.birth[n], S.end[n]) for n in sorted(S.end, key=lambda x: (x != "Root", x))]
    L = np.array([e - b for _, b, e in segs])
    for i in range(a.n):
        if a.mode == "root":
            lin, t0 = "Root", 0.0
        else:                                    # uniform by length over the whole complete tree
            j = int(rng.choice(len(segs), p=L / L.sum()))
            lin, t0 = segs[j][0], segs[j][1] + rng.random() * (segs[j][2] - segs[j][1])
        rates = tuple(draw_rate(rng, g[k], g["family_rate_sigma"]) for k in ("duplication", "transfer", "loss"))
        r = family_record(S, rng, rates, lin, t0, 0.0, "v%d" % i, 0)
        mine.append(r)
    ini = g["initial_genome_size"]
    allz = sim_rows(a.simdir)
    if a.mode == "root":
        z, zn = [r for r in allz if int(r["family"]) <= ini], ini
    else:
        total = json.load(open(os.path.join(a.simdir, "sim_summary.json")))["families"]["zombi_total"]
        z, zn = [r for r in allz if int(r["family"]) > ini], total - ini
    # Zombi truth.tsv omits families absent from both the sample and the MRCA; pad with zeros
    z += [{"n_genes": 0, "nA": 0, "nB": 0}] * (zn - len(z))
    if a.mode == "mid":                          # compare families present in the sample only
        mine = [r for r in mine if r["n_genes"] > 0]
        z = [r for r in z if r["n_genes"] > 0]
    out = {}
    for name, f in [("n_genes", lambda r: r["n_genes"]), ("occupancy", lambda r: r["nA"] + r["nB"]),
                    ("nA", lambda r: r["nA"]), ("nB", lambda r: r["nB"])]:
        x, y = [f(r) for r in mine], [f(r) for r in z]
        out[name] = {"ks_D": ks(x, y), "mean_stemsim": float(np.mean(x)), "mean_zombi": float(np.mean(y)),
                     "frac0_stemsim": float(np.mean(np.array(x) == 0)), "frac0_zombi": float(np.mean(np.array(y) == 0))}
    out["n_stemsim"], out["n_zombi"] = len(mine), len(z)
    out["ks_crit_0.05"] = 1.36 * math.sqrt((len(mine) + len(z)) / (len(mine) * len(z)))
    write_json(a.out, out)
    print(json.dumps(out, indent=1))


GRID = list(range(25, 500, 25)) + list(range(500, 2000, 50)) + list(range(2000, 4001, 100))


def kept_rows(src, seed, n_root):
    truth = read_tsv(os.path.join(src, "sample", "truth.tsv"))
    luca = sorted((r["family"] for r in truth if r["luca"] == "1"), key=int)
    keep_luca = set(np.random.default_rng([seed, 999]).choice(luca, size=n_root, replace=False).tolist())
    return truth, keep_luca, [r for r in truth if r["luca"] == "0" or r["family"] in keep_luca]


def as_row(r):
    return {"n_genes": int(r["n_genes"]), "nA": int(r["n_genomes_A"]) if "n_genomes_A" in r else r["nA"],
            "nB": int(r["n_genomes_B"]) if "n_genomes_B" in r else r["nB"]}


def world_setup(src, seed, lam):
    S = Species(src)
    g = cfg_of(src)["genome"]
    tau, stem_len = stem_tau(S)
    x = lam / tau
    truth, keep_luca, kept = kept_rows(src, seed, 20)
    base_id = 10 ** (len(str(max(int(r["family"]) for r in truth))) + 1)
    return S, g, tau, stem_len, x, truth, keep_luca, kept, base_id


def cmd_tune(a):
    """Prereg v6 tuning: per (source sim, lambda), the smallest grid N whose small world matches the big
    world on rows 1 and 2; rows 3-6 are recorded. Phyletic summaries only (no PP is read)."""
    src = os.path.abspath(a.simdir)
    S, g, tau, stem_len, x, truth, keep_luca, kept, base_id = world_setup(src, a.seed, a.lam)
    dom = S.dom
    nA = sum(1 for v in dom.values() if v == "A")
    nB = len(dom) - nA
    big = summarize([as_row(r) for r in truth], nA, nB)
    base = [as_row(r) for r in kept]
    lam_code = int(round(a.lam * 1000))
    new, trace, chosen = [], [], None
    for N in GRID:
        while len(new) < N:
            new.append(stem_family(S, g, a.seed, lam_code, len(new), x, base_id, 10 ** 7))
        sm = summarize(base + [r for r in new if r["n_genes"] > 0], nA, nB)
        c = compare(sm, big)
        trace.append({"N": N, **{k: v for k, v in sm.items() if k != "occupancy"}, **c})
        trace[-1]["Tstem_per_family"] = sum(r["ctr"]["Tstem"] for r in new) / N
        trace[-1]["Xnone"] = sum(r["ctr"]["Xnone"] for r in new)
        if sm["n_broad_both"] > 1.2 * big["n_broad_both"]:
            break
    passing = [t for t in trace if t["row1_frac_both_domains"] and t["row2_n_broad_both"]]
    if passing:   # prereg v6: closest on row 2 among passers, ties to the smallest N
        best = min(passing, key=lambda t: (abs(t["n_broad_both"] - big["n_broad_both"]), t["N"]))
        status, N_use = "matched", best["N"]
    else:
        best = min(trace, key=lambda t: (abs(t["n_broad_both"] - big["n_broad_both"]), t["N"]))
        status, N_use = "unmatched", best["N"]
    rows_4_5 = best["row4_occupancy_ks"] and best["row5_genome_size"]
    out = {"source": src, "seed": a.seed, "lambda": a.lam, "tau": tau, "x": x, "stem_length": stem_len,
           "stems_n_lineages": [len(s) for s in S.stems], "status": status, "N": N_use,
           "tight_match_rows_4_5": bool(rows_4_5),
           "big": {k: v for k, v in big.items() if k != "occupancy"},
           "at_N": [t for t in trace if t["N"] == N_use][0], "trace": trace}
    write_json(a.out, out)
    print(json.dumps({k: v for k, v in out.items() if k != "trace"}, indent=1))


def cmd_build(a):
    src = os.path.abspath(a.simdir)
    S, g, tau, stem_len, x, truth, keep_luca, kept, base_id = world_setup(src, a.seed, a.lam)
    if a.rootctrl:
        # prereg v6 ALE positive control: Zombi's initial-genome families are replaced by stemsim
        # families born at the root (time 0); truth = copies at the MRCA's speciation.
        ini = g["initial_genome_size"]
        kept = [r for r in truth if int(r["family"]) > ini]
        keep_luca = set()
        new = []
        for i in range(ini):
            rng_a = np.random.default_rng([a.seed, 7777, i])
            rates = tuple(draw_rate(rng_a, g[k], g["family_rate_sigma"]) for k in ("duplication", "transfer", "loss"))
            new.append(family_record(S, np.random.default_rng([a.seed, 7778, i]), rates, "Root", 0.0, 0.0,
                                     str(base_id + i), 10 ** 7 + i * 10000))
        x, a.n_stem = 0.0, 0
    out = os.path.abspath(a.outdir)
    if os.path.exists(out):
        sys.exit("%s exists" % out)
    for d in ["sample/true_trees", "sample/mappings", "ale_true/uml_rec"]:
        os.makedirs(os.path.join(out, d))
    for f in ["species_tree.nwk", "domains.tsv"]:
        shutil.copy(os.path.join(src, "sample", f), os.path.join(out, "sample", f))
    shutil.copy(os.path.join(src, "config.json"), os.path.join(out, "config.json"))
    os.makedirs(os.path.join(out, "zombi"))
    shutil.copytree(os.path.join(src, "zombi", "T"), os.path.join(out, "zombi", "T"))
    kept_ids = {r["family"] for r in kept}
    for f in kept_ids:
        for sub in ["true_trees/%s.nwk" % f, "mappings/%s.map" % f]:
            p = os.path.join(src, "sample", sub)
            if os.path.exists(p):
                shutil.copy(p, os.path.join(out, "sample", sub))
    ale_src = os.path.join(src, a.ale_dir, "uml_rec")
    n_rec = 0
    for fn in sorted(os.listdir(ale_src)) if os.path.isdir(ale_src) else []:
        if fn.endswith(".ale.uml_rec") and fn.split(".ale.uml_rec")[0].rsplit("_", 1)[-1] in kept_ids:
            shutil.copy(os.path.join(ale_src, fn), os.path.join(out, "ale_true", "uml_rec", fn))
            n_rec += 1
    lam_code = int(round(a.lam * 1000))
    if not a.rootctrl:
        new = [stem_family(S, g, a.seed, lam_code, i, x, base_id, 10 ** 7) for i in range(a.n_stem)]
    ctr_tot = {k: sum(r["ctr"][k] for r in new) for k in ("D", "T", "L", "Tstem", "Xnone")}
    for r in new:
        if r["n_genes"] >= 2:
            with open(os.path.join(out, "sample", "true_trees", r["family"] + ".nwk"), "w") as f:
                f.write(r["nwk"] + "\n")
        if r["n_genes"] >= 1:
            with open(os.path.join(out, "sample", "mappings", r["family"] + ".map"), "w") as f:
                for gname, lin_ in sorted(r["genes"]):
                    f.write("%s %s\n" % (gname, lin_))
    with open(os.path.join(out, "sample", "truth.tsv"), "w") as f:
        f.write("family\tmrca_copies_genome\tmrca_copies_events\tluca\tn_genes\tn_genomes_A\tn_genomes_B\n")
        for r in kept:
            f.write("\t".join(r[k] for k in ["family", "mrca_copies_genome", "mrca_copies_events", "luca",
                                              "n_genes", "n_genomes_A", "n_genomes_B"]) + "\n")
        for r in new:
            m = r["ctr"]["mrca"]
            if r["n_genes"] > 0 or m > 0:
                f.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\n" % (r["family"], m, m, int(m > 0), r["n_genes"], r["nA"], r["nB"]))
    with open(os.path.join(out, "sample", "stem_families.tsv"), "w") as f:
        f.write("family\torigin_lineage\tt0\tn_genes\tnA\tnB\tD\tT\tL\tTstem\n")
        for r in new:
            c = r["ctr"]
            f.write("%s\t%s\t%.6f\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (r["family"], r["origin"], r["t0"], r["n_genes"],
                                                               r["nA"], r["nB"], c["D"], c["T"], c["L"], c["Tstem"]))
    info = {"source": src, "seed": a.seed, "lambda": a.lam, "rootctrl": bool(a.rootctrl),
            "true_luca_new": sum(1 for r in new if r["ctr"]["mrca"] > 0), "tau": tau, "x_stem": x, "n_root_kept": 20,
            "n_stem_born": a.n_stem, "stem_length_total": stem_len, "stems_n_lineages": [len(s) for s in S.stems],
            "crowns": S.crowns, "mrca": S.mrca, "kept_families": len(kept), "uml_rec_copied": n_rec,
            "stem_born_present": sum(1 for r in new if r["n_genes"] > 0),
            "stem_born_ge2": sum(1 for r in new if r["n_genes"] >= 2), "events": ctr_tot,
            "root_families_kept": sorted(keep_luca, key=int)}
    write_json(os.path.join(out, "k5_world.json"), info)
    print(json.dumps({k: v for k, v in info.items() if k != "root_families_kept"}, indent=1))


def cmd_summary(a):
    rows = sim_rows(a.simdir)
    dom = {r["species"]: r["domain"] for r in read_tsv(os.path.join(a.simdir, "sample", "domains.tsv"))}
    nA = sum(1 for v in dom.values() if v == "A")
    s = summarize(rows, nA, len(dom) - nA)
    s["true_luca"] = sum(r["luca"] for r in rows)
    write_json(a.out, s)
    print(json.dumps({k: v for k, v in s.items() if k != "occupancy"}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("simdir"), v.add_argument("out")
    v.add_argument("--n", type=int, default=600)
    v.add_argument("--seed", type=int, default=1)
    v.add_argument("--mode", choices=["root", "mid"], default="root")
    b = sub.add_parser("build")
    b.add_argument("simdir"), b.add_argument("outdir")
    b.add_argument("--n-stem", type=int, required=True)
    b.add_argument("--lam", type=float, required=True, help="stem transfers per founding copy (x = lam / tau)")
    b.add_argument("--seed", type=int, default=1)
    b.add_argument("--ale-dir", default="ale_true")
    b.add_argument("--rootctrl", action="store_true", help="ALE positive control (ignores --n-stem/--lam)")
    t = sub.add_parser("tune")
    t.add_argument("simdir"), t.add_argument("out")
    t.add_argument("--lam", type=float, required=True)
    t.add_argument("--seed", type=int, default=1)
    s = sub.add_parser("summary")
    s.add_argument("simdir"), s.add_argument("out")
    a = ap.parse_args()
    {"validate": cmd_validate, "build": cmd_build, "summary": cmd_summary, "tune": cmd_tune}[a.cmd](a)


if __name__ == "__main__":
    main()
