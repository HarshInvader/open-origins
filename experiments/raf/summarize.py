"""Summarise planted_runs.jsonl into results.json (task #8)."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NULLS = ["N1", "N2", "N3", "N3m"]


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return [round(c - h, 3), round(c + h, 3)]


rows = [json.loads(l) for l in (HERE / "planted_runs.jsonl").read_text().splitlines()]
g = collections.defaultdict(list)
for r in rows:
    g[(r["kind"], r["k"])].append(r)
table = []
for (kind, k), v in sorted(g.items()):
    n = len(v)
    e = dict(background=kind, planted_k=k, n_networks=n, mean_maxraf=round(sum(r["maxraf"] for r in v) / n, 1),
             core_recovered=None if k == 0 else sum(r["recovered"] for r in v))
    for nl in NULLS:
        a = sum(r[nl]["above"] for r in v); b = sum(r[nl]["below"] for r in v)
        e[nl] = dict(above=a, below=b, above_rate=round(a / n, 3), above_ci=wilson(a, n), below_rate=round(b / n, 3))
    table.append(e)
gate = {}
for nl in NULLS:
    fpr = {e["background"]: e[nl]["above_rate"] for e in table if e["planted_k"] == 0}
    gate[nl] = dict(fpr_above_by_background=fpr, passes_gate=all(x <= 0.10 for x in fpr.values()),
                    two_sided_fpr_by_background={e["background"]: round((e[nl]["above"] + e[nl]["below"]) / e["n_networks"], 3)
                                                 for e in table if e["planted_k"] == 0})
part_a = json.loads((HERE / "part_a.json").read_text())
rec = [r["recovered"] for r in rows if r["k"]]
out = dict(task=8, part_a_bruteforce=part_a, recovery=dict(n=len(rec), recovered=sum(rec)),
           n_rep_per_null=99, table=table, gate=gate)
(HERE / "results.json").write_text(json.dumps(out, indent=2))
for e in table:
    print(e["background"], e["planted_k"], e["mean_maxraf"], e["core_recovered"],
          {nl: (e[nl]["above"], e[nl]["below"]) for nl in NULLS})
print(json.dumps(gate, indent=1))
