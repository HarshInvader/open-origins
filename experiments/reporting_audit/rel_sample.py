"""Seed-1 reliability sample: 7 prebiotic + 3 comparison included papers; write blind hand-off list."""
import csv, numpy as np
ext = list(csv.DictReader(open("extraction.csv")))
rng = np.random.default_rng(1)
sel = []
for s, k in [("prebiotic", 7), ("comparison", 3)]:
    ps = sorted({r["paper_id"] for r in ext if r["set"] == s}, key=lambda p: int(p[3:]))
    sel += [ps[i] for i in sorted(rng.choice(len(ps), k, replace=False))]
with open("batches/rel_handoffs.txt", "w") as f:
    for r in ext:
        if r["paper_id"] in sel:
            f.write(f'{r["set"]} {r["paper_id"]} doi:{r["doi"]} year:{r["year"]} handoff:{r["handoff"]} | step n product: {r["step_n"]} | step n+1 product: {r["step_n1"]}\n')
print(sel)
