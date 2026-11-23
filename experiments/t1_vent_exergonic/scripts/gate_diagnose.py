"""T1 gate diagnosis (post-seal, logged in DEVIATIONS.md). Touches only the gate target: our dG vs Wimmer Table 3
sheet A, pH 7, 25 C, 1 mM. Computes no arm statistic and no null-pool quantity.
Usage: .venv/bin/python -I scripts/gate_diagnose.py
"""
import sys, json, collections, pathlib
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t1_analysis as T

core = T.load_core()
cc, Q_, ver = T.eq_setup()
rx, meta = T.eq_parse(cc, core)
ok = [i for i, m in enumerate(meta) if m[0]]
mu, U = T.eq_grid(cc, Q_, [rx[i] for i in ok], [(7, 25)])
sig = np.sqrt(np.sum(U ** 2, axis=1))
theirs = T.table3_column('A', 7, 25)
seen = collections.Counter()
rows = []
pos = {i: j for j, i in enumerate(ok)}
for i, r in enumerate(core):
    k = seen[r['reaction_id']]; seen[r['reaction_id']] += 1
    tv = theirs.get(r['reaction_id'], [None] * (k + 1))[k]
    if tv is None or i not in pos:
        continue
    j = pos[i]
    ours = T.dg(mu[0][j], meta[i][2], meta[i][3], 25, T.CFG['c_equal_M'], T.CFG['c_equal_M'])
    rows.append((r['reaction_id'], float(ours), float(tv), float(sig[j]), float(mu[0][j])))
a = np.array([[o, t, s] for _, o, t, s, _ in rows])
d = a[:, 0] - a[:, 1]
from_rank = lambda x: np.argsort(np.argsort(x))
out = {
    "n": len(rows),
    "pearson": float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]),
    "spearman": float(np.corrcoef(from_rank(a[:, 0]), from_rank(a[:, 1]))[0, 1]),
    "pearson_vs_minus_ours": float(np.corrcoef(-a[:, 0], a[:, 1])[0, 1]),
    "abs_diff_quantiles_kJ": {q: float(np.quantile(np.abs(d), q)) for q in (0.25, 0.5, 0.75, 0.9, 0.95, 0.99)},
    "n_abs_diff_gt_5": int((np.abs(d) > 5).sum()), "n_abs_diff_gt_50": int((np.abs(d) > 50).sum()),
    "pearson_sigma_lt_100": float(np.corrcoef(a[a[:, 2] < 100, 0], a[a[:, 2] < 100, 1])[0, 1]),
    "n_sigma_lt_100": int((a[:, 2] < 100).sum()),
    "pearson_abs_diff_lt_50": float(np.corrcoef(a[np.abs(d) < 50, 0], a[np.abs(d) < 50, 1])[0, 1]),
    "worst": sorted([{"id": i, "ours": round(o, 1), "theirs": round(t, 1), "sigma": round(s, 1)} for i, o, t, s, _ in rows],
                    key=lambda x: -abs(x["ours"] - x["theirs"]))[:15],
}
json.dump(out, open(HERE.parent / "scripts_out" / "t1_gate_diagnose.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "worst"}, indent=1)); print(json.dumps(out["worst"][:15]))

# shares on the D4-computable subset, and how Wimmer's zeros enter their share
m = a[:, 2] < 100
z = a[:, 1] == 0
extra = {"share_ours_sigma_lt_100": float(T.share(a[m, 0])), "share_theirs_sigma_lt_100": float(T.share(a[m, 1])),
         "n_theirs_exactly_zero": int(z.sum()), "n_theirs_zero_and_sigma_ge_100": int((z & ~m).sum()),
         "n_sigma_ge_100": int((~m).sum()), "share_theirs_all_351": float(T.share(a[:, 1])),
         "share_rule": "share() counts dG <= 0 as exergonic (T.share)"}
out.update(extra); json.dump(out, open(HERE.parent / "scripts_out" / "t1_gate_diagnose.json", "w"), indent=1)
print(json.dumps(extra, indent=1))
