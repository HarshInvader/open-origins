"""Score the red-team encoding with the unchanged wrapper/scorer and diff against the original (task #21).

Run from repo root: .venv/bin/python -I experiments/redteam_pathway/score_rt.py
Writes diff.json and shuffle_null.json next to this file.
"""
import copy
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "pathway_map"))
sys.path.insert(0, str(HERE.parents[0] / "compat"))
sys.path.insert(0, str(HERE))
import score_map as SM  # noqa: E402
import steps as ST  # noqa: E402
import steps_rt as RT  # noqa: E402

HARD = SM.HARD


def rows_by_id(pathways):
    out = {}
    for pw in pathways:
        rows, summ = SM.score_pathway(pw)
        out[pw["id"]] = (rows, summ)
    return out


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    orig = rows_by_id(ST.PATHWAYS)
    mine = rows_by_id(RT.PATHWAYS)
    diff = []
    for pid in orig:
        ro, rm = orig[pid][0][1:], mine[pid][0][1:]
        assert [r["handoff"] for r in ro] == [r["handoff"] for r in rm], pid
        for a, b in zip(ro, rm):
            diff.append(dict(route=pid, handoff=a["handoff"], orig=a["verdict"], rt=b["verdict"],
                             orig_hard=sorted(HARD & set(a["flags"])), rt_hard=sorted(HARD & set(b["flags"])),
                             orig_warn=sorted(set(a["flags"]) - HARD), rt_warn=sorted(set(b["flags"]) - HARD),
                             orig_notes=a["notes"], rt_notes=b["notes"],
                             orig_procs=[p["process"] for p in a["processes"]],
                             rt_procs=[p["process"] for p in b["processes"]]))
    va, vb = [d["orig"] for d in diff], [d["rt"] for d in diff]
    flips = sum(x != y for x, y in zip(va, vb))
    code_diff = sum(d["orig_hard"] != d["rt_hard"] for d in diff)
    res = dict(n_handoffs=len(diff), verdict_flips=flips, flip_fraction=flips / len(diff),
               hard_code_set_differs=code_diff, kappa=kappa(va, vb),
               rt_summary={k: v[1] for k, v in mine.items()}, orig_summary={k: v[1] for k, v in orig.items()},
               rows=diff)
    (HERE / "diff.json").write_text(json.dumps(SM.jsonable(res), indent=1))
    print(f"flips {flips}/{len(diff)} = {flips/len(diff):.3f}; kappa {res['kappa']:.3f}; hard-code sets differ {code_diff}")
    for d in diff:
        mark = "*" if d["orig"] != d["rt"] else (" ~" if d["orig_hard"] != d["rt_hard"] else "  ")
        print(f"{mark} {d['route']:<14}{d['handoff']:<9} {d['orig']:<24}{str(d['orig_hard']):<22} | {d['rt']:<24}{d['rt_hard']}")
    for pid, (_, s) in mine.items():
        print(pid, "continuous" if s["continuous"] else "not continuous", s["hard_fail_codes"])


if __name__ == "__main__":
    main()
