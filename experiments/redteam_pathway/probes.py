"""Targeted probes of the original encoding (task #21). Each probe edits a deep copy of the ORIGINAL cyanosulfidic
route and rescored with the unchanged wrapper. Run: .venv/bin/python -I experiments/redteam_pathway/probes.py
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "pathway_map"))
sys.path.insert(0, str(HERE.parents[0] / "compat"))
import score_map as SM  # noqa: E402
import steps as ST  # noqa: E402

CY = next(p for p in ST.PATHWAYS if p["id"] == "cyanosulfidic")
S = "10.1038/ncomms15270"


def idx(pw, sid):
    return next(i for i, s in enumerate(pw["steps"]) if s["id"] == sid)


def show(tag, pw, only=None):
    rows, summ = SM.score_pathway(pw)
    out = []
    for r in rows[1:]:
        if only and r["handoff"] not in only:
            continue
        out.append(dict(handoff=r["handoff"], verdict=r["verdict"], flags=r["flags"], notes=r["notes"]))
        print(f"  [{tag}] {r['handoff']:<8} {r['verdict']:<24} {r['flags']}  {'; '.join(r['notes'])[:160]}")
    return out


def main():
    res = {}
    print("P0 baseline (original)")
    res["baseline"] = show("orig", CY, {"C1->C2", "C2->C3", "C3->C4", "C5->C6", "C6->C7", "C7->C8"})

    # P1: C3->C4 with C4 needing pH 10.5 (the condition of the 45%/33% yield the original uses for outputs)
    pw = copy.deepcopy(CY); pw["steps"][idx(pw, "C4")]["conditions"]["ph"] = 10.5
    print("P1a C4 at pH 10.5, original hand-off (gas_exchange to 9)")
    res["P1a"] = show("P1a", pw, {"C3->C4"})
    pw["handoffs"][2]["procs"] = [pw["handoffs"][2]["procs"][0], dict(process="cooling", t_after=25.0),
                                  dict(process="evaporation", factor=1.0, ph_after=8.0), dict(process="gas_exchange", ph_after=10.0)]
    print("P1b C4 at pH 10.5, evaporation(+1 pH, factor 1) then gas_exchange(+2): rule-legal")
    res["P1b"] = show("P1b", pw, {"C3->C4"})
    pw = copy.deepcopy(CY); pw["handoffs"][2]["procs"][0].pop("demonstrated_by")
    print("P1c original pH 9, separation of thione_1a without demonstrated_by (Stairs crystallised pure diastereomers for X-ray)")
    res["P1c"] = show("P1c", pw, {"C3->C4"})

    # P2: C5->C6 via Stairs Method I (dry urea/phosphate melt, 140 C) instead of formamide Method V
    pw = copy.deepcopy(CY); c6 = pw["steps"][idx(pw, "C6")]
    c6["conditions"].update(t=140.0, solvent="dry"); c6["outputs"].update(t=140.0, solvent="dry")
    pw["handoffs"][4]["procs"] = [dict(process="drying"), dict(process="transport", to_setting="evaporite", dilution=1.0),
                                  dict(process="heating", t_after=140.0)]
    pw["handoffs"][5]["procs"] = [dict(process="rehydration", stream="rain", f=0.5, ph_after=7.0),
                                  dict(process="cooling", t_after=23.0),
                                  dict(process="transport", to_setting="surface_pool", dilution=1.0)]
    print("P2a C6 as dry urea melt (Method I; its yield for 11 is in the SI, not read)")
    res["P2a"] = show("P2a", pw, {"C5->C6", "C6->C7"})
    pw["handoffs"][4]["procs"].insert(0, dict(process="selective_separation", species="anhydrocytidine", property="crystallisation"))
    print("P2b + claimed crystallisation of anhydrocytidine (no demonstrated_by -> W3)")
    res["P2b"] = show("P2b", pw, {"C5->C6", "C6->C7"})

    # P3: C7->C8 claimed separation of cCMP
    pw = copy.deepcopy(CY)
    pw["handoffs"][6]["procs"] = [dict(process="selective_separation", species="cCMP", property="crystallisation")]
    print("P3 C7->C8 isolate cCMP by claimed crystallisation")
    res["P3"] = show("P3", pw, {"C7->C8"})

    # P4: C1 output pH known (7, as at start) -> pH 0 at C2 is unreachable under the scenario's streams
    pw = copy.deepcopy(CY); pw["steps"][0]["outputs"]["ph"] = 7.0
    print("P4 C1 output pH set to its starting 7")
    res["P4"] = show("P4", pw, {"C1->C2"})

    # P5: C1 produces free sugars (the H2S variant Patel 2015 mentions, not opened)
    pw = copy.deepcopy(CY); pw["steps"][0]["outputs"]["species"].update(glycolaldehyde=float("nan"), glyceraldehyde=float("nan"))
    pw["steps"][idx(pw, "C2")]["inputs"][0]["purified"] = False
    pw["steps"][idx(pw, "C3")]["inputs"][1]["purified"] = False
    print("P5 hypothetical: C1 releases free glycolaldehyde and glyceraldehyde, unpurified")
    res["P5"] = show("P5", pw, {"C1->C2", "C2->C3"})

    # P6: thermophoresis factor in the vent
    for fct in (2.5, 1000.0):
        v = copy.deepcopy(next(p for p in ST.PATHWAYS if p["id"] == "alkaline_vent")); v["handoffs"][0]["procs"][1]["factor"] = fct
        print(f"P6 vent thermophoresis factor {fct}")
        res[f"P6_{fct}"] = show("P6", v, {"V1->V2"})
    (HERE / "probes.json").write_text(json.dumps(SM.jsonable(res), indent=1))


if __name__ == "__main__":
    main()
