"""Score the red-team DSM encoding (task #27) with the unchanged rule-v1 scorer and the task #5 wrapper,
called the same way experiments/dsm_route/score_dsm.py calls them, and compare with the original.

Differences from score_dsm.py (deliberate):
- The 28 planted controls are run IN MEMORY (planted.py's main() rewrites experiments/compat/*.csv/json,
  which this task may not touch).
- Every route is scored twice: A = scorer exactly as sealed (no NaN patch), B = with score_dsm.py's
  post-run NaN range-check patch. The original's encoding is also scored both ways, so the effect of the
  patch is visible on both encodings.
- Writes only experiments/redteam_dsm/results.json and handoffs_rt.csv.
"""
import copy
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/pathway_map"))
sys.path.insert(0, str(ROOT / "experiments/compat"))
sys.path.insert(0, str(HERE))

import planted as PL  # noqa: E402
import score_map as SM  # noqa: E402
import steps_rt as RT  # noqa: E402

sys.path.insert(0, str(ROOT / "experiments/dsm_route"))
import steps_dsm as SD  # noqa: E402

# ---- planted controls, in memory
n_ok = 0
for name, fn, exp in PL.CASES:
    res = PL.scorer.score(PL.m(fn)())
    got = {r["handoff"]: set(r["flags"]) for r in res["handoffs"] if r["flags"]}
    n_ok += got == {k: set(v) for k, v in exp.items()}
assert n_ok == len(PL.CASES), f"planted controls {n_ok}/{len(PL.CASES)}; refusing to score"
print(f"planted controls {n_ok}/{len(PL.CASES)} OK")

SM.ST.SCENARIOS["dsm_aquifer"] = RT.SCENARIO
SM.ST.SCENARIOS["borate_aquifer"] = SD.SCENARIO

_orig_between = SM.scorer._between


def _between_nan_ok(x, a, b):  # copied from score_dsm.py
    if any(v != v for v in (x, a, b)):
        return True
    return _orig_between(x, a, b)


def run(pw, patched):
    SM.scorer._between = _between_nan_ok if patched else _orig_between
    try:
        rows, summ = SM.score_pathway(copy.deepcopy(pw))
    finally:
        SM.scorer._between = _orig_between
    return rows, summ


out = dict(task=27, rule_sha256=SM.scorer.P["sha256"], planted=f"{n_ok}/{len(PL.CASES)}", runs={})
csv_rows = []
for label, pw in [("rt", RT.PATHWAY), ("orig_dsm", SD.PATHWAYS[0]), ("orig_dsm_b", SD.PATHWAYS[1])]:
    for patched in (False, True):
        key = f"{label}_{'B_nanpatch' if patched else 'A_sealed'}"
        rows, summ = run(pw, patched)
        out["runs"][key] = dict(summary=SM.jsonable(summ), handoffs=[
            dict(handoff=r["handoff"], verdict=r["verdict"], flags=r["flags"], notes=r["notes"],
                 unassessed=[list(u) for u in r["unassessed"]]) for r in rows])
        print(f"\n== {key}  continuous={summ['continuous']}")
        for r in rows:
            print(f"  {r['handoff']:<10} {r['verdict']:<24} {r['flags']}  UA={[u[0] + ':' + u[1] for u in r['unassessed']]}")
            for n in r["notes"]:
                print("       ", n)
            csv_rows.append([key, r["handoff"], r["verdict"], " ".join(r["flags"]), len(r["unassessed"]), " | ".join(r["notes"])])

(HERE / "results.json").write_text(json.dumps(SM.jsonable(out), indent=2))
with open(HERE / "handoffs_rt.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["run", "handoff", "verdict", "flags", "n_unassessed", "notes"])
    w.writerows(csv_rows)
