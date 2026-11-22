"""K3 (prereg v5c) summary: R_true, R_inf, and R* over families ALE completed in both arms. python -I k3_score.py <out.json> <tag=simdir>..."""
import sys, csv, json
def rows(p): return {r["family"]: r for r in csv.DictReader(open(p), delimiter="\t")}
out = {}
for arg in sys.argv[2:]:
    tag, sim = arg.split("=", 1)
    truth = rows(f"{sim}/sample/truth.tsv"); luca = {f for f, r in truth.items() if r["luca"] == "1"}
    arms = {}
    for arm in ("ale_true", "ale_inferred"):
        try: arms[arm] = rows(f"{sim}/{arm}/root_pp.tsv")
        except FileNotFoundError: pass
    res = {"true_luca": len(luca)}
    both = None
    for arm, rr in arms.items():
        ok = {f for f, r in rr.items() if r["status"] == "ok"}
        both = ok if both is None else both & ok
        for col in ("pp", "pp_flat"):
            res[f"{arm}_R_{col}"] = sum(float(r[col]) for r in rr.values() if r["status"] == "ok") / len(luca)
        res[f"{arm}_n_failed"] = sum(r["status"].startswith("ALE") for r in rr.values())
        res[f"{arm}_failed_luca"] = sum(r["status"].startswith("ALE") and f in luca for f, r in rr.items())
        o = json.load(open(f"{sim}/{arm}/or_fit.json")); res[f"{arm}_O_R"] = o["O_R"]
        res[f"{arm}_false_pp_mass"] = sum(float(r["pp"]) for f, r in rr.items() if r["status"] == "ok" and f not in luca)
    if both is not None:
        nl = len(both & luca); res["n_both_ok"] = len(both); res["luca_both_ok"] = nl
        for arm, rr in arms.items():
            res[f"{arm}_Rstar"] = sum(float(rr[f]["pp"]) for f in both) / nl if nl else None
        if len(arms) == 2 and res["ale_true_Rstar"]:
            res["Q"] = res["ale_inferred_Rstar"] / res["ale_true_Rstar"]
    out[tag] = res
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out, indent=1))
