"""Planted controls for the step-compatibility scorer (rule v1, task #3).

Toy scenario with made-up species A, B, X, Y, Z, K, Q, so no real chemistry is implied.
Each case = (name, modifier, expected flags per hand-off). Writes results.json and planted_cases.csv.
"""
import copy
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scorer  # noqa: E402

OUT = Path(__file__).resolve().parent

SCEN = dict(
    name="toy_pond", t_range=[-30, 100], uv=True, redox="reducing",
    settings=["surface_pool", "porous_rock"],
    feedstocks={"A": 0.1, "B": 0.1}, volatile=["V"],
    streams={
        "alk_spring": dict(ph=12, t=25, solvent="water", redox="reducing", species={"K": 0.01}),
        "oxic_seep": dict(ph=7, t=25, solvent="water", redox="oxidizing", species={}),
    },
    minerals={"carbonate": [6.5, 8.5]},
)


def step(i, inputs, outs, ph=7, t=25, solvent="water", redox="reducing", setting="surface_pool", tested=()):
    return dict(id=f"s{i}", setting=setting, inputs=inputs, tested_with=list(tested),
                conditions=dict(ph=ph, t=t, solvent=solvent, redox=redox),
                outputs=dict(species=outs, ph=ph, t=t, solvent=solvent, redox=redox),
                yield_label="demonstrated", source="toy")


def baseline():
    return dict(
        scenario=copy.deepcopy(SCEN),
        steps=[
            step(1, [dict(species="A", conc=0.1)], {"X": 0.01}),
            step(2, [dict(species="X", conc=0.01)], {"Y": 0.001}),
            step(3, [dict(species="Y", conc=0.001)], {"Z": 0.0001}, tested=["X"]),
        ],
        handoffs=[[dict(process="same_pot")], [dict(process="same_pot")]],
    )


def m(fn):
    def build():
        p = baseline()
        fn(p)
        return p
    return build


def s(p, i):
    return p["steps"][i]


def set_ph(st, ph, out=None):
    st["conditions"]["ph"] = ph
    st["outputs"]["ph"] = ph if out is None else out


# ---- modifiers ----------------------------------------------------------
def f1(p):  # THE planted incompatible step: pH 2 product fed to a pH 10 reaction
    set_ph(s(p, 0), 2); set_ph(s(p, 1), 10); set_ph(s(p, 2), 10)


def f1_twin(p):
    f1(p)
    p["handoffs"][0] = [dict(process="mixing", stream="alk_spring", f=0.5, ph_after=10)]
    s(p, 1)["tested_with"] = ["K"]; s(p, 2)["tested_with"] = ["X", "K"]


def f1_bad_mix(p):  # mixing claims a pH outside [pot, stream]
    p["handoffs"][0] = [dict(process="mixing", stream="alk_spring", f=0.5, ph_after=13)]
    s(p, 1)["tested_with"] = ["K"]; s(p, 2)["tested_with"] = ["X", "K"]
    set_ph(s(p, 1), 13, out=7)


def f2(p):
    s(p, 1)["conditions"]["t"] = 90


def f2_twin(p):
    f2(p); p["handoffs"][0] = [dict(process="heating", t_after=90)]


def f3(p):
    s(p, 1)["conditions"]["solvent"] = "dry"


def f3_twin(p):
    f3(p); p["handoffs"][0] = [dict(process="drying")]


def f4(p):
    s(p, 1)["inputs"].append(dict(species="Q", conc=0.01))


def f4_twin(p):
    s(p, 1)["inputs"].append(dict(species="B", conc=0.01))


def f5(p):
    s(p, 1)["inputs"][0]["conc"] = 10.0


def f5_twin(p):
    f5(p); p["handoffs"][0] = [dict(process="evaporation", factor=1000)]


def w2(p):
    s(p, 1)["inputs"][0]["conc"] = 0.2


def w2_twin(p):
    w2(p); p["handoffs"][0] = [dict(process="evaporation", factor=100)]


def f6(p):
    s(p, 1)["inputs"][0]["purified"] = True


def f6_twin(p):
    f6(p); p["handoffs"][0] = [dict(process="selective_separation", species="X", property="crystallisation",
                                     demonstrated_by="toy-source")]


def w3(p):
    f6(p); p["handoffs"][0] = [dict(process="selective_separation", species="X", property="crystallisation")]


def f7_unknown(p):
    p["handoffs"][0] = [dict(process="magic_filter")]


def f7_cap(p):
    p["handoffs"][0] = [dict(process="evaporation", factor=1e5)]


def f7_cap_twin(p):
    p["handoffs"][0] = [dict(process="evaporation", factor=1000)]


def f7_setting(p):
    p["handoffs"][0] = [dict(process="thermophoresis", factor=10)]


def f7_setting_twin(p):
    s(p, 1)["setting"] = "porous_rock"
    p["handoffs"][0] = [dict(process="transport", to_setting="porous_rock", dilution=1.0),
                        dict(process="thermophoresis", factor=10)]
    p["handoffs"][1] = [dict(process="transport", to_setting="surface_pool", dilution=1.0)]


def f7_uv(p):
    p["scenario"]["uv"] = False
    p["handoffs"][0] = [dict(process="uv_irradiation")]


def f8(p):
    s(p, 1)["conditions"]["redox"] = "oxidizing"


def f8_twin(p):
    f8(p); p["handoffs"][0] = [dict(process="mixing", stream="oxic_seep", f=0.5)]


def f9(p):
    s(p, 1)["setting"] = "porous_rock"; s(p, 2)["setting"] = "porous_rock"


def f9_twin(p):
    f9(p); p["handoffs"][0] = [dict(process="transport", to_setting="porous_rock", dilution=0.5)]


def w1(p):
    s(p, 2)["tested_with"] = []


def none(p):
    pass


E = {}  # no flags anywhere
CASES = [
    ("baseline", none, E),
    ("PLANTED pH2->pH10 same_pot", f1, {"1->2": {"F1"}}),
    ("twin: mixing with pH12 stream", f1_twin, E),
    ("mixing claims pH outside range (invalid process not applied, so pH also fails)", f1_bad_mix, {"1->2": {"F7", "F1"}}),
    ("F2 T jump, no heating", f2, {"1->2": {"F2"}}),
    ("twin: heating", f2_twin, E),
    ("F3 solvent change, no process", f3, {"1->2": {"F3"}}),
    ("twin: drying", f3_twin, E),
    ("F4 input from nowhere", f4, {"1->2": {"F4"}}),
    ("twin: input is a feedstock", f4_twin, E),
    ("F5 1000x short", f5, {"1->2": {"F5"}}),
    ("twin: evaporation 1000x", f5_twin, E),
    ("W2 20x short", w2, {"1->2": {"W2"}}),
    ("twin: evaporation 100x", w2_twin, E),
    ("F6 purified input", f6, {"1->2": {"F6"}}),
    ("twin: demonstrated crystallisation", f6_twin, E),
    ("W3 separation not demonstrated", w3, {"1->2": {"W3"}}),
    ("F7 unknown process", f7_unknown, {"1->2": {"F7"}}),
    ("F7 evaporation over cap", f7_cap, {"1->2": {"F7"}}),
    ("twin: evaporation at cap", f7_cap_twin, E),
    ("F7 thermophoresis in a pool", f7_setting, {"1->2": {"F7"}}),
    ("twin: transport to porous rock first", f7_setting_twin, E),
    ("F7 UV where there is none", f7_uv, {"1->2": {"F7"}}),
    ("F8 redox mismatch", f8, {"1->2": {"F8"}}),
    ("twin: mixing with oxic seep", f8_twin, E),
    ("F9 setting change, no transport", f9, {"1->2": {"F9"}}),
    ("twin: transport", f9_twin, E),
    ("W1 untested carried species", w1, {"2->3": {"W1"}}),
]


def main():
    rows, n_ok = [], 0
    for name, fn, exp in CASES:
        res = scorer.score(m(fn)())
        got = {r["handoff"]: set(r["flags"]) for r in res["handoffs"] if r["flags"]}
        exp_n = {k: set(v) for k, v in exp.items()}
        ok = got == exp_n
        n_ok += ok
        rows.append(dict(case=name, expected=json.dumps({k: sorted(v) for k, v in exp_n.items()}),
                         got=json.dumps({k: sorted(v) for k, v in got.items()}), ok=ok,
                         notes=" | ".join(n for r in res["handoffs"] for n in r["notes"])))
        print(("OK  " if ok else "BAD ") + name, got)
    with open(OUT / "planted_cases.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    viol = [r for r, c in zip(rows, CASES) if c[2]]
    clean = [r for r, c in zip(rows, CASES) if not c[2]]
    planted = rows[1]
    out = dict(task=3, rule_file="docs/prereg/compatibility_rule.md", rule_sha256=scorer.P["sha256"],
               n_cases=len(rows), n_correct=n_ok,
               sensitivity=sum(r["ok"] for r in viol) / len(viol), n_violation_cases=len(viol),
               specificity=sum(r["ok"] for r in clean) / len(clean), n_compliant_cases=len(clean),
               planted_pH2_to_pH10=dict(flagged=planted["ok"], got=json.loads(planted["got"]), notes=planted["notes"]),
               passed=n_ok == len(rows))
    (OUT / "results.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
