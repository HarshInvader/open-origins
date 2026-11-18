"""Task #8: planted autocatalytic core recovery and null calibration.

Part A: the maxRAF code agrees with brute-force enumeration on small random networks.
Part B: planted cores are always inside the detected maxRAF (recovery).
Part C: false-positive rate (nothing planted) and power (core planted) of each null test used in #6:
        N1 degree-preserving rewiring, N2 catalyst-only shuffle, N3 uniform random food, N3m degree-matched food.
Resumable: appends one JSON line per network to planted_runs.jsonl.
Run: board/run.sh .venv/bin/python -I experiments/raf/planted_run.py
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from raf import Net, brute_max_raf, max_raf, null_test  # noqa: E402
from gen import background, plant_core  # noqa: E402

OUT = HERE / "planted_runs.jsonl"
KINDS = ["R", "S"]
KS = [0, 20, 100, 300, 1000]
N_NET = 20
N_REP = 99
NULLS = ["N1", "N2", "N3", "N3m"]


def part_a(n=400, seed=7):
    rng = np.random.default_rng(seed)
    agree = 0; nonempty = 0
    for _ in range(n):
        n_mol = int(rng.integers(5, 9)); n_rxn = int(rng.integers(3, 10))
        rs, ps, cs = [], [], []
        for _ in range(n_rxn):
            m = rng.choice(n_mol, size=int(rng.integers(2, 4)), replace=False)
            a = int(rng.integers(1, len(m)))
            rs.append(m[:a]); ps.append(m[a:])
            cs.append(rng.choice(n_mol, size=int(rng.integers(0, 3)), replace=False))
        net = Net(n_mol, rs, ps, cs)
        food = set(rng.choice(n_mol, size=int(rng.integers(1, 4)), replace=False).tolist())
        a1 = max_raf(net, food); a2 = brute_max_raf(net, food)
        agree += bool((a1 == a2).all()); nonempty += bool(a2.any())
    return dict(n=n, agree=agree, n_with_raf=nonempty)


def job(args):
    kind, k, i = args
    rng = np.random.default_rng([ord(kind), k, i, 2026])
    net, food = background(kind, rng)
    idx = np.array([], dtype=int)
    if k:
        net, food, idx = plant_core(net, food, k, rng)
    m = max_raf(net, food)
    row = dict(kind=kind, k=k, i=i, n_rxn=net.n_rxn, maxraf=int(m.sum()),
               recovered=bool(m[idx].all()) if k else None)
    for nk in NULLS:
        row[nk] = null_test(net, food, nk, N_REP, rng)
    return row


def main():
    done = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            r = json.loads(line)
            done.add((r["kind"], r["k"], r["i"]))
    a = part_a()
    (HERE / "part_a.json").write_text(json.dumps(a))
    print("part A", a, flush=True)
    todo = [(kd, k, i) for kd in KINDS for k in KS for i in range(N_NET) if (kd, k, i) not in done]
    with Pool(2) as pool, open(OUT, "a") as fh:
        for row in pool.imap_unordered(job, todo):
            fh.write(json.dumps(row) + "\n"); fh.flush()
            print(row["kind"], row["k"], row["i"], row["maxraf"], {n: row[n]["above"] for n in NULLS}, flush=True)


if __name__ == "__main__":
    main()
