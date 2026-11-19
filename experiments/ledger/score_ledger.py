"""Task #29: score enc_A and enc_B (blind encodings of R6-R11) under unchanged rule v1 + task #5 wrapper.
Prereg docs/prereg/intervention_ledger.md (sha 528b9d13). Planted controls first. No NaN patch (primary);
the DSM-style NaN-pass patch is reported as a sensitivity only (red team #27 showed it is unsafe in general).
"""
import json, subprocess, sys, importlib
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "experiments/pathway_map")]
pl = subprocess.run([sys.executable, "-I", str(ROOT / "experiments/compat/planted.py")], capture_output=True, text=True)
pres = json.loads((ROOT / "experiments/compat/results.json").read_text())
print("planted:", pres.get("summary", pres.get("pass")))
import score_map as SM
HARD = {"F1","F2","F3","F4","F5","F6","F7","F8","F9"}

def run(enc, patch):
    sys.path.insert(0, str(HERE / f"enc_{enc}"))
    mod = importlib.import_module(f"steps_{enc}")
    SM.ST.SCENARIOS.update(mod.SCENARIOS)
    orig = SM.scorer._between
    if patch:
        SM.scorer._between = lambda x, a, b: True if any(v != v for v in (x, a, b)) else orig(x, a, b)
    out = []
    try:
        for pw in mod.PATHWAYS:
            rows, summ = SM.score_pathway(pw)
            for i, r in enumerate(rows):
                if r["handoff"].startswith("entry"):
                    continue
                codes = sorted({f.split()[0].rstrip(":") for f in r["flags"] if f.split()[0].rstrip(":") in HARD})
                procs = [p["process"] for p in pw["handoffs"][i - 1]["procs"]] if i - 1 < len(pw["handoffs"]) else []
                ua = sorted({u[0] for u in r["unassessed"]})
                out.append(dict(route=pw["id"], handoff=r["handoff"], verdict=r["verdict"], hard=codes,
                                same_pot_only=procs == ["same_pot"], procs=procs, unassessed=ua))
    finally:
        SM.scorer._between = orig
    return out

res = {e: {p: run(e, p) for p in (False, True)} for e in ("A", "B")}

def summarise(rows):
    broken = [r for r in rows if r["hard"]]
    passes = [r for r in rows if not r["hard"] and r["verdict"] != "blocked_by_missing_step"]
    only346 = [r for r in broken if set(r["hard"]) <= {"F3","F4","F6"}]
    ph_t_only = [r for r in broken if set(r["hard"]) <= {"F1","F2"}]
    return dict(n=len(rows), broken=len(broken), no_hard_fail=len([r for r in rows if not r["hard"]]),
                passes_not_blocked=len(passes), passes_same_pot=sum(r["same_pot_only"] for r in passes),
                passes=[f'{r["route"]}:{r["handoff"]}:{"/".join(r["procs"])}' for r in passes],
                frac_only_F346=(len(only346) / len(broken)) if broken else None, ph_t_only=len(ph_t_only),
                any_F1=sum("F1" in r["hard"] for r in rows), any_F2=sum("F2" in r["hard"] for r in rows),
                pH_assessed=sum("F1" not in r["unassessed"] for r in rows),
                T_assessed=sum("F2" not in r["unassessed"] for r in rows),
                code_counts={c: sum(c in r["hard"] for r in rows) for c in sorted(HARD)},
                verdicts={v: sum(r["verdict"] == v for r in rows) for v in sorted({r["verdict"] for r in rows})})

out = dict(task=29, prereg="528b9d13", planted=pres.get("summary"), summary={}, rows=res)
for e in "AB":
    for p in (False, True):
        s = summarise(res[e][p]); out["summary"][f"{e}_{'patch' if p else 'primary'}"] = s
        print(f"\n== enc {e} {'NaN-patch' if p else 'PRIMARY'}:", json.dumps(s, indent=0))
for e in "AB":
    print(f"\n-- enc {e} primary rows")
    for r in res[e][False]:
        print(f'  {r["route"]:<6}{r["handoff"]:<10}{r["verdict"]:<24}{r["hard"]} procs={r["procs"]} UA={r["unassessed"]}')
(HERE / "results.json").write_text(json.dumps(SM.jsonable(out), indent=1, default=str))
