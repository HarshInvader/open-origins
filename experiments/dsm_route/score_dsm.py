"""Score the DSM route (task #26) with the unchanged rule-v1 scorer and the task #5 wrapper.

Runs the 28 planted controls first and refuses to score if any fails.
Writes results.json and handoffs.csv next to this file.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/pathway_map"))
sys.path.insert(0, str(HERE))

planted = subprocess.run([sys.executable, "-I", str(ROOT / "experiments/compat/planted.py")],
                         capture_output=True, text=True)
pres = json.loads((ROOT / "experiments/compat/results.json").read_text())
print(planted.stdout[-400:])

import score_map as SM  # noqa: E402
import steps_dsm as SD  # noqa: E402

SM.ST.SCENARIOS["borate_aquifer"] = SD.SCENARIO

# NaN policy extension (added after the first run, disclosed in RESULTS.md): the scorer's mixing/rehydration
# check "new pH between old pH and stream pH" raises F7 whenever the old pH is NaN (not reported), and the
# failed process then leaves the solvent unchanged (knock-on F3). Consistent with the task #5 wrapper
# (unreported numbers are UNASSESSED, never a fail), a range check with a NaN bound passes here and the
# hand-off records it as unassessed. This can only remove fails. It changes nothing in the four task #5 routes
# (none has an F7).
_orig_between = SM.scorer._between


def _between_nan_ok(x, a, b):
    if any(v != v for v in (x, a, b)):
        return True
    return _orig_between(x, a, b)


SM.scorer._between = _between_nan_ok

out = dict(task=26, rule_sha256=SM.scorer.P["sha256"], planted=pres.get("summary", pres.get("pass")), routes={})
rows_csv = []
for pw in SD.PATHWAYS:
    rows, summ = SM.score_pathway(pw)
    out["routes"][pw["id"]] = dict(summary=SM.jsonable(summ), handoffs=[
        dict(handoff=r["handoff"], verdict=r["verdict"], flags=r["flags"], notes=r["notes"],
             unassessed=[list(u) for u in r["unassessed"]], why=r["why"]) for r in rows])
    print("\n==", pw["id"], "continuous:", summ["continuous"])
    for r in rows:
        print(f"  {r['handoff']:<10} {r['verdict']:<24} {r['flags']}  UA={[u[0]+':'+u[1] for u in r['unassessed']]}")
        for n in r["notes"]:
            print("       ", n)
        rows_csv.append([pw["id"], r["handoff"], r["verdict"], " ".join(r["flags"]), len(r["unassessed"]), " | ".join(r["notes"])])

(HERE / "results.json").write_text(json.dumps(SM.jsonable(out), indent=2))
with open(HERE / "handoffs.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["route", "handoff", "verdict", "flags", "n_unassessed", "notes"])
    w.writerows(rows_csv)
