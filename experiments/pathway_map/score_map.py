"""Score the four step tables under the sealed compatibility rule (task #5).

Uses experiments/compat/scorer.py unchanged (it refuses to run unless the rule hash is in HASHES.txt).
The scorer was written for complete numbers. Our tables contain NaN (not reported) and "unknown"
(solvent/redox not stated), and the scorer then (a) silently passes NaN comparisons (F1, F5, W1, W2)
and (b) raises F2 when the required T is NaN, and F3/F8 when one side is "unknown". This wrapper
replays the same state with the scorer's own functions and reports each such check as UNASSESSED
instead: it never adds a fail the scorer did not raise, and it removes only F2/F3/F8 flags whose
inputs were NaN/"unknown". Writes map.json, results.json, ledger_rows.csv, handoffs.csv.
"""
import copy
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "compat"))
sys.path.insert(0, str(HERE))
import scorer  # noqa: E402
import steps as ST  # noqa: E402

HARD = set(scorer.P["hard_fails"])
CHECK_NAMES = dict(F1="pH", F2="temperature", F3="solvent", F4="input source", F5="concentration",
                   F6="purified hand-off", F7="process validity", F8="redox", F9="setting",
                   W1="untested interference", W2="thin concentration", W3="claimed separation")


def nan(x):
    return isinstance(x, float) and math.isnan(x)


def scorer_label(step):
    return {"demonstrated": "demonstrated", "demonstrated_purified": "demonstrated_purified"}.get(
        step["yield_status"], "missing")


def unassessed_inputs(state, step, scen, produced):
    """Per-input concentration checks the scorer cannot make (NaN or unstated feedstock conc)."""
    out = []
    feed = scen.get("feedstocks", {})
    stream_sp = {k for st in scen["streams"].values() for k in st["species"]}
    for i in step["inputs"]:
        a, used = i["species"], i["conc"]
        if a not in produced and a not in feed and a not in stream_sp:
            continue  # F4 already raised
        have = state["species"].get(a) if state else None
        f = feed.get(a)
        if nan(used):
            out.append(("F5", a, "source concentration not reported"))
        elif f is not None and math.isinf(f) and (have is None or nan(have) or have < used):
            out.append(("F5", a, "scenario feedstock with no stated concentration"))
        elif have is not None and nan(have) and f is None:
            out.append(("F5", a, "carried concentration unknown (earlier step did not report it)"))
    if state is not None and step["inputs"]:
        if any(nan(c) for c in state["species"].values()) or nan(step["inputs"][0]["conc"]):
            out.append(("W1", "*", "some carried or main-input concentrations unknown"))
    return out


def score_pathway(pw):
    scen = ST.SCENARIOS[pw["scenario"]]
    steps = pw["steps"]
    sc_steps = []
    for s in steps:
        d = copy.deepcopy(s)
        d["yield_label"] = scorer_label(s)
        d["inputs"] = [dict(species=i["species"], conc=i["conc"], purified=i["purified"]) for i in s["inputs"]]
        sc_steps.append(d)
    res = scorer.score(dict(scenario=scen, steps=sc_steps, handoffs=[h["procs"] for h in pw["handoffs"]]))

    # replay state to find unassessed checks
    rows = []
    produced = set()
    entry = res["handoffs"][0]
    ua0 = unassessed_inputs(None, steps[0], scen, produced)
    rows.append(dict(handoff="entry->" + steps[0]["id"], frm=None, to=steps[0]["id"], processes=[],
                     flags=entry["flags"], notes=entry["notes"], unassessed=ua0, why="Feedstocks of the scenario."))
    produced = set(steps[0]["outputs"]["species"])
    state = scorer._state_from_step(sc_steps[0], {})
    for k in range(1, len(steps)):
        nxt, h = steps[k], pw["handoffs"][k - 1]
        s = copy.deepcopy(state)
        for p in h["procs"]:
            try:
                scorer.apply_process(s, p, scen)
            except scorer.ProcErr:
                pass
        c = nxt["conditions"]
        ua = []
        if nan(s["ph"]) or nan(c["ph"]):
            ua.append(("F1", "", f"pH {'after hand-off' if nan(s['ph']) else 'needed'} not reported"))
        if nan(s["t"]) or nan(c["t"]):
            ua.append(("F2", "", f"T {'after hand-off' if nan(s['t']) else 'needed'} not reported"))
        if "unknown" in (s["solvent"], c["solvent"]):
            ua.append(("F3", "", "solvent not stated"))
        if "unknown" in (s["redox"], c["redox"]):
            ua.append(("F8", "", "redox class not stated by the source"))
        ua += unassessed_inputs(s, nxt, scen, produced)
        ua += list(h.get("unassess", []))
        r = res["handoffs"][k]
        ua_codes = {u[0] for u in ua if u[0] in ("F2", "F3", "F8")}
        flags = [f for f in r["flags"] if f not in ua_codes]
        notes = [n for n in r["notes"] if n.split()[0] not in ua_codes]
        # manual unassess entries for F4 (provisional outputs) suppress that F4 only if raised for that species
        rows.append(dict(handoff=f"{steps[k-1]['id']}->{nxt['id']}", frm=steps[k - 1]["id"], to=nxt["id"],
                         processes=h["procs"], flags=flags, notes=notes, unassessed=ua, why=h["why"]))
        produced |= set(nxt["outputs"]["species"])
        state = scorer._state_from_step(sc_steps[k], s["species"])

    status = {s["id"]: s["yield_status"] for s in steps}
    for r in rows[1:]:
        hard = HARD & set(r["flags"])
        touches_missing = status[r["frm"]] in ("missing", "unread") or status[r["to"]] in ("missing", "unread")
        if hard:
            r["verdict"] = "broken"
        elif touches_missing:
            r["verdict"] = "blocked_by_missing_step"
        elif r["unassessed"]:
            r["verdict"] = "unverified"
        else:
            r["verdict"] = "continuous"
        r["unexplained"] = r["verdict"] in ("broken", "blocked_by_missing_step")
    rows[0]["verdict"] = "broken" if HARD & set(rows[0]["flags"]) else ("unverified" if rows[0]["unassessed"] else "continuous")
    rows[0]["unexplained"] = rows[0]["verdict"] == "broken"

    ys = [s["yield_status"] for s in steps]
    hos = rows[1:]
    summ = dict(
        n_steps=len(steps), n_handoffs=len(hos),
        n_unexplained=sum(r["unexplained"] for r in hos),
        n_hard_fail_handoffs=sum(r["verdict"] == "broken" for r in hos),
        n_blocked_by_missing=sum(r["verdict"] == "blocked_by_missing_step" for r in hos),
        n_unverified=sum(r["verdict"] == "unverified" for r in hos),
        n_continuous=sum(r["verdict"] == "continuous" for r in hos),
        n_warnings=sum(len(set(r["flags"]) - HARD) for r in hos),
        n_unassessed_checks=sum(len(r["unassessed"]) for r in rows),
        n_demonstrated=ys.count("demonstrated"), n_demonstrated_purified=ys.count("demonstrated_purified"),
        n_missing=ys.count("missing"), n_unread=ys.count("unread"),
        hard_fail_codes=sorted({f for r in hos for f in r["flags"] if f in HARD}),
        entry_flags=rows[0]["flags"],
        continuous=res["continuous"],
        scorer_raw=dict(n_hard_fail_handoffs=res["n_hard_fail_handoffs"], n_warnings=res["n_warnings"],
                        n_missing_steps=res["n_missing_steps"], n_purified_steps=res["n_purified_steps"]),
        stages_with_yield=sorted({s["stage"] for s in steps if s["yield_status"].startswith("demonstrated")}),
        stages_missing=sorted({s["stage"] for s in steps if s["yield_status"] in ("missing", "unread")}
                              - {s["stage"] for s in steps if s["yield_status"].startswith("demonstrated")}),
    )
    return rows, summ


def jsonable(x):
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None if math.isnan(x) else "unstated"
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return x


def gap_list(all_rows, summaries):
    """One row per gap. Rank: missing step > hard fail; within those, by how many routes share the stage."""
    gaps = []
    for pw in ST.PATHWAYS:
        for s in pw["steps"]:
            if s["yield_status"] in ("missing", "unread"):
                gaps.append(dict(route=pw["id"], where=s["id"], stage=s["stage"], kind=s["yield_status"] + "_step",
                                 codes=[], detail=s["name"] + ". " + s["notes"]))
        for r in all_rows[pw["id"]]:
            hard = sorted(HARD & set(r["flags"]))
            if hard:
                to = next(s for s in pw["steps"] if s["id"] == r["to"])
                gaps.append(dict(route=pw["id"], where=r["handoff"], stage=to["stage"], kind="hard_fail",
                                 codes=hard, detail=" | ".join(r["notes"]) + ". Hand-off: " + r["why"]))
    stage_routes, stage_demo = {}, {}
    for g in gaps:
        stage_routes.setdefault(g["stage"], set()).add(g["route"])
    for pw in ST.PATHWAYS:
        for s in pw["steps"]:
            if s["yield_status"] == "demonstrated":
                stage_demo.setdefault(s["stage"], set()).add(pw["id"])
            if s["yield_status"] == "demonstrated_purified":
                stage_demo.setdefault(s["stage"] + "p", set()).add(pw["id"])
    kind_rank = {"missing_step": 0, "unread_step": 1, "hard_fail": 2}
    for g in gaps:
        g["routes_blocked_at_stage"] = len(stage_routes[g["stage"]])
        g["routes_with_unpurified_yield_at_stage"] = len(stage_demo.get(g["stage"], ()))
        g["routes_with_any_yield_at_stage"] = len(stage_demo.get(g["stage"], set()) | stage_demo.get(g["stage"] + "p", set()))
    # rank: gaps no route has bridged even with purified inputs come first; then the ones only
    # bridged with purified inputs; then by how many routes are blocked there; earlier stage first
    gaps.sort(key=lambda g: (g["routes_with_any_yield_at_stage"], g["routes_with_unpurified_yield_at_stage"],
                             -g["routes_blocked_at_stage"], int(g["stage"][1]), kind_rank[g["kind"]],
                             -len(g["codes"]), g["route"]))
    for i, g in enumerate(gaps, 1):
        g["rank"] = i
    return gaps


def main():
    all_rows, summaries = {}, {}
    for pw in ST.PATHWAYS:
        rows, summ = score_pathway(pw)
        all_rows[pw["id"]], summaries[pw["id"]] = rows, summ
    order = sorted(summaries, key=lambda k: (summaries[k]["n_hard_fail_handoffs"], summaries[k]["n_missing"] + summaries[k]["n_unread"],
                                             summaries[k]["n_demonstrated_purified"], summaries[k]["n_warnings"]))
    gaps = gap_list(all_rows, summaries)

    # ---- map.json (site format)
    m = dict(
        format="open-origins pathway map v1", rule_file="docs/prereg/compatibility_rule.md",
        rule_sha256=scorer.P["sha256"], scorer="experiments/compat/scorer.py", built_by="experiments/pathway_map/score_map.py",
        stages=ST.STAGES, check_names=CHECK_NAMES,
        legend=dict(
            yield_status=dict(demonstrated="yield published by another lab from unpurified inputs",
                              demonstrated_purified="yield published, but from purified or commercial inputs",
                              missing="no published step known to us", unread="published, but we could not open the full text"),
            handoff_verdict=dict(continuous="no hard fail, every check assessable", unverified="no hard fail, but some checks lack numbers",
                                 blocked_by_missing_step="one side is a missing/unread step", broken="at least one hard fail (F1-F9)")),
        ranking=order,
        routes=[],
        gaps=gaps,
    )
    for pw in ST.PATHWAYS:
        scen = ST.SCENARIOS[pw["scenario"]]
        m["routes"].append(dict(
            id=pw["id"], label=pw["label"], note=pw["note"], summary=summaries[pw["id"]],
            scenario=dict(name=scen["name"], t_range=scen["t_range"], uv=scen["uv"], redox=scen["redox"],
                          settings=scen["settings"], feedstocks=scen["feedstocks"], streams=scen["streams"],
                          basis=scen["basis"]),
            steps=[dict(id=s["id"], name=s["name"], stage=s["stage"], setting=s["setting"],
                        inputs=s["inputs"], conditions=s["conditions"], outputs=s["outputs"],
                        purified_inputs=any(i["purified"] for i in s["inputs"]),
                        yield_status=s["yield_status"], yield_text=s["yield_text"],
                        source_doi=s["source_doi"], source_url=("https://doi.org/" + s["source_doi"]) if s["source_doi"] else None,
                        where=s["where"], notes=s["notes"], assumptions=s["assumptions"]) for s in pw["steps"]],
            handoffs=[dict(id=r["handoff"], from_step=r["frm"], to_step=r["to"], processes=r["processes"],
                           verdict=r["verdict"], unexplained=r["unexplained"], flags=r["flags"], notes=r["notes"],
                           unassessed=[dict(code=u[0], species=u[1], reason=u[2]) for u in r["unassessed"]],
                           why=r["why"]) for r in all_rows[pw["id"]]],
        ))
    (HERE / "map.json").write_text(json.dumps(jsonable(m), indent=1))

    # ---- handoffs.csv
    with open(HERE / "handoffs.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["route", "handoff", "verdict", "hard_fails", "warnings", "n_unassessed", "processes", "notes"])
        for pw in ST.PATHWAYS:
            for r in all_rows[pw["id"]]:
                w.writerow([pw["id"], r["handoff"], r["verdict"], " ".join(f for f in r["flags"] if f in HARD),
                            " ".join(f for f in r["flags"] if f not in HARD), len(r["unassessed"]),
                            "; ".join(p["process"] for p in r["processes"]), " | ".join(r["notes"])])

    out = dict(task=[4, 5, 17], rule_sha256=scorer.P["sha256"], ranking=order,
               routes={k: summaries[k] for k in order},
               n_gaps=len(gaps), top_gaps=[dict(rank=g["rank"], route=g["route"], where=g["where"], stage=g["stage"],
                                                 kind=g["kind"], codes=g["codes"],
                                                 routes_with_any_yield_at_stage=g["routes_with_any_yield_at_stage"]) for g in gaps[:15]],
               any_route_continuous=any(s["continuous"] for s in summaries.values()))
    (HERE / "results.json").write_text(json.dumps(jsonable(out), indent=2))
    print(json.dumps(jsonable(out), indent=2))
    for pw in ST.PATHWAYS:
        print("\n==", pw["id"])
        for r in all_rows[pw["id"]]:
            print(f"  {r['handoff']:<10} {r['verdict']:<24} {r['flags']}  UA={[u[0]+':'+u[1] for u in r['unassessed']]}")
            for n in r["notes"]:
                print("       ", n)


if __name__ == "__main__":
    main()
