"""Task #6: RAF null test on the Xavier et al. 2020 anaerobic prokaryotic network (dataset S4).

Follows docs/prereg/raf_null_xavier2020.md. Refuses to run unless that file's sha256 is in HASHES.txt.
Run: board/run.sh .venv/bin/python -I experiments/raf_null/run_null.py
Resumable: null sizes appended to null_sizes.jsonl.
"""
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cnet  # noqa: E402
from load import PSEUDO, read  # noqa: E402

PREREG = ROOT / "docs/prereg/raf_null_xavier2020.md"
DATA = HERE / "raw/rspb20192377supp5.txt"
OUT = HERE / "null_sizes.jsonl"
N_REP = 999
NULLS = ["N1", "N2", "N3", "N3m"]
PUBLISHED_MAXRAF = 1335


def check_prereg():
    h = hashlib.sha256(PREREG.read_bytes()).hexdigest()
    if h not in (ROOT / "docs/prereg/HASHES.txt").read_text():
        raise SystemExit("pre-registration not hashed; refusing to run")
    return h


def build():
    food, rxns = read(DATA)
    names = {}

    def ix(x):
        if x not in names:
            names[x] = len(names)
        return names[x]

    lhs = [np.array(sorted({ix(m) for m in r["lhs"]}), np.int64) for r in rxns]
    rhs = [np.array(sorted({ix(m) for m in r["rhs"]}), np.int64) for r in rxns]
    cats = [[np.array(sorted(ix(m) for m in c), np.int64) for c in r["cat"]] for r in rxns]
    fidx = [ix(f) for f in food]
    net = cnet.CNet(len(names), lhs, rhs, [r["rev"] for r in rxns], cats)
    pooling = {i for i, r in enumerate(rxns) if any("Pooling" in c for c in r["cat"])}
    pseudo = {names[p] for p in PSEUDO if p in names}
    return net, np.array(fidx), names, rxns, pooling, pseudo


def degree_strata(net):
    d = np.zeros(net.n_mol, int); dc = np.zeros(net.n_mol, int)
    for x in net.lhs + net.rhs:
        np.add.at(d, x, 1)
    for cs in net.cats:
        for c in cs:
            np.add.at(dc, c, 1)
    tot = d + dc
    return np.where(tot > 0, (d == 0).astype(int) * 100 + np.floor(np.log2(np.maximum(tot, 1))).astype(int), -1), tot


G = {}


def init():
    G["net"], G["food"], G["names"], G["rxns"], G["pool"], G["pseudo"] = build()
    G["strat"], G["deg"] = degree_strata(G["net"])


def fm(idx):
    m = np.zeros(G["net"].n_mol, bool); m[list(idx)] = True
    return m


def one(args):
    kind, i = args
    rng = np.random.default_rng([ord(c) for c in kind] + [i, 6])
    net, food, pseudo = G["net"], G["food"], G["pseudo"]
    real_food = [f for f in food if f not in pseudo]
    if kind in ("N1", "N2"):
        n2 = cnet.rewire(net, rng, G["pool"], pseudo, kind)
        size = int(cnet.max_raf(n2, fm(food)).sum())
    elif kind == "N3":
        pool = np.setdiff1d(np.flatnonzero(G["deg"] > 0), np.array(sorted(pseudo)))
        f = rng.choice(pool, size=len(real_food), replace=False).tolist() + sorted(pseudo)
        size = int(cnet.max_raf(net, fm(f)).sum())
    elif kind == "N3m":
        out = set()
        for f in sorted(real_food):
            cand = np.setdiff1d(np.flatnonzero(G["strat"] == G["strat"][f]),
                                np.array(sorted(out | pseudo), dtype=np.int64))
            out.add(int(rng.choice(cand)) if len(cand) else int(f))
        size = int(cnet.max_raf(net, fm(list(out) + sorted(pseudo))).sum())
    return dict(null=kind, i=i, size=size)


def main():
    h = check_prereg()
    init()
    net = G["net"]
    obs_mask = cnet.max_raf(net, fm(G["food"]))
    obs = int(obs_mask.sum())
    info = dict(prereg_sha256=h, n_reactions=net.n, n_directed=net.nd, n_molecules=net.n_mol,
                n_food=len(G["food"]), n_pooling=len(G["pool"]), observed_maxraf=obs,
                published_maxraf=PUBLISHED_MAXRAF, reproduces=obs == PUBLISHED_MAXRAF)
    print(info, flush=True)
    (HERE / "observed.json").write_text(json.dumps(info, indent=2))
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            r = json.loads(line); done.add((r["null"], r["i"]))
    todo = [(k, i) for k in NULLS for i in range(N_REP) if (k, i) not in done]
    with Pool(2, initializer=init) as pool, open(OUT, "a") as fh:
        for n, r in enumerate(pool.imap_unordered(one, todo, chunksize=10)):
            fh.write(json.dumps(r) + "\n")
            if n % 200 == 0:
                fh.flush(); print(n, r, flush=True)


if __name__ == "__main__":
    main()
