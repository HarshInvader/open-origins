"""Summarise null_sizes.jsonl against observed.json under the pre-registered decision rule (task #6)."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NULLS = ["N1", "N2", "N3", "N3m"]
gate = json.loads((HERE.parent / "raf/results.json").read_text())["gate"]
obs_info = json.loads((HERE / "observed.json").read_text())
obs = obs_info["observed_maxraf"]
sizes = {n: [] for n in NULLS}
for l in (HERE / "null_sizes.jsonl").read_text().splitlines():
    r = json.loads(l); sizes[r["null"]].append(r["size"])
res = {}
for n in NULLS:
    s = np.array(sizes[n]); m = len(s)
    lo, med, hi = np.percentile(s, [2.5, 50, 97.5]); q1, q3 = np.percentile(s, [25, 75])
    p_hi = (1 + (s >= obs).sum()) / (m + 1); p_lo = (1 + (s <= obs).sum()) / (m + 1)
    res[n] = dict(n=m, null_min=int(s.min()), null_lo=float(lo), null_median=float(med), null_hi=float(hi),
                  null_max=int(s.max()), p_upper=float(p_hi), p_lower=float(p_lo),
                  above=bool(obs > hi), below=bool(obs < lo),
                  effect_iqr=float((obs - med) / (q3 - q1)) if q3 > q1 else None,
                  dist_to_nearer_bound=float(min(abs(obs - lo), abs(obs - hi))),
                  frac_zero=float((s == 0).mean()),
                  decisive=n in ("N1", "N3m") and gate[n]["passes_gate"])
dec = [n for n in NULLS if res[n]["decisive"]]
if not dec:
    verdict = "no decisive null passed the task #8 gate"
elif all(res[n]["above"] for n in dec):
    verdict = "above null"
elif all(res[n]["below"] for n in dec):
    verdict = "below null"
elif any(not res[n]["above"] and not res[n]["below"] for n in dec):
    verdict = "within null"
else:
    verdict = "mixed"
out = dict(task=6, observed=obs_info, nulls=res, decisive_nulls=dec, verdict=verdict)
(HERE / "results.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
