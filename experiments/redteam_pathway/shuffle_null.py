"""Shuffle null (task #21, suggested by Fable): does rule v1 score shuffled step orders worse than the real order?

For each route of the ORIGINAL encoding (experiments/pathway_map/steps.py) we permute step order 200 times (seed 21)
and score with the unchanged wrapper (score_map.score_pathway). Hand-off process lists cannot follow a shuffle, so
three hand-off policies are used:
  A same_pot everywhere (real order rescored with same_pot too, so the comparison is like for like);
  B the real route's process lists kept by position (what a careless encoder would do);
  C 'best of a small menu' per hand-off: same_pot, or transport to the next step's setting (+drying if the next step
    is dry, +heating/cooling to the next step's T when known) -- gives each order its fairest simple chance.
Also D: cyanosulfidic restricted to its six demonstrated steps (C1 C2 C3 C4 C6 C8), all 720 orders, policy C.
Statistic: number of hand-offs with any hard fail (F1-F9), and the number with F4. One-sided p = share of shuffles
scoring <= the real order (low p = real order is clearly better).
Run: .venv/bin/python -I experiments/redteam_pathway/shuffle_null.py
"""
import copy
import itertools
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "pathway_map"))
sys.path.insert(0, str(HERE.parents[0] / "compat"))
import score_map as SM  # noqa: E402
import steps as ST  # noqa: E402

HARD = SM.HARD


def nan(x):
    return isinstance(x, float) and math.isnan(x)


def menu_c(prev, nxt, scen):
    procs = []
    if nxt["setting"] != prev["setting"]:
        procs.append(dict(process="transport", to_setting=nxt["setting"], dilution=1.0))
    if nxt["conditions"]["solvent"] == "dry":
        procs.append(dict(process="drying"))
    t_prev, t_need = prev["outputs"]["t"], nxt["conditions"]["t"]
    lo, hi = scen["t_range"]
    if not nan(t_need) and lo <= t_need <= hi:
        if nan(t_prev) or t_need >= t_prev:
            procs.append(dict(process="heating", t_after=t_need))
        else:
            procs.append(dict(process="cooling", t_after=t_need))
    return procs or [dict(process="same_pot")]


def build(pw, order, policy):
    steps = [pw["steps"][i] for i in order]
    scen = ST.SCENARIOS[pw["scenario"]]
    if policy == "A":
        hos = [dict(procs=[dict(process="same_pot")], why="") for _ in steps[1:]]
    elif policy == "B":
        hos = [dict(procs=copy.deepcopy(h["procs"]), why="") for h in pw["handoffs"]][: len(steps) - 1]
    else:
        hos = [dict(procs=menu_c(a, b, scen), why="") for a, b in zip(steps, steps[1:])]
    return dict(id=pw["id"], scenario=pw["scenario"], steps=steps, handoffs=hos)


def stat(pw):
    rows, _ = SM.score_pathway(pw)
    hos = rows[1:]
    return (sum(bool(HARD & set(r["flags"])) for r in hos), sum("F4" in r["flags"] for r in hos))


def run(pw, policy, orders):
    real = stat(build(pw, list(range(len(pw["steps"]))), policy))
    sh = [stat(build(pw, o, policy)) for o in orders]
    out = {}
    for j, name in enumerate(("hard", "F4")):
        vals = [s[j] for s in sh]
        out[name] = dict(real=real[j], null_mean=sum(vals) / len(vals), null_min=min(vals), null_max=max(vals),
                         p_le=sum(v <= real[j] for v in vals) / len(vals))
    return out


def main():
    rng = random.Random(21)
    res = {}
    for pw in ST.PATHWAYS:
        n = len(pw["steps"])
        orders = []
        for _ in range(200):
            o = list(range(n))
            rng.shuffle(o)
            orders.append(o)
        res[pw["id"]] = {p: run(pw, p, orders) for p in "ABC"}
    cy = next(p for p in ST.PATHWAYS if p["id"] == "cyanosulfidic")
    keep = [i for i, s in enumerate(cy["steps"]) if s["yield_status"].startswith("demonstrated")]
    sub = dict(cy, steps=[cy["steps"][i] for i in keep], handoffs=[dict(procs=[dict(process="same_pot")], why="")] * (len(keep) - 1))
    perms = [list(p) for p in itertools.permutations(range(len(keep))) if list(p) != list(range(len(keep)))]
    res["cyanosulfidic_demonstrated_only_all_perms"] = dict(steps=[cy["steps"][i]["id"] for i in keep], C=run(sub, "C", perms))
    (HERE / "shuffle_null.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        for p, d in v.items():
            if p == "steps":
                continue
            print(f"{k:<45}{p}  hard real {d['hard']['real']} null mean {d['hard']['null_mean']:.2f} "
                  f"[{d['hard']['null_min']},{d['hard']['null_max']}] p<= {d['hard']['p_le']:.3f} | "
                  f"F4 real {d['F4']['real']} null {d['F4']['null_mean']:.2f} p<= {d['F4']['p_le']:.3f}")


if __name__ == "__main__":
    main()
