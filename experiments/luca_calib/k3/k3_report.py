"""K3 report (prereg v5c decision rule + v5e/Fable measures) from root_pp.tsv and truth.tsv.

Usage: python -I k3_report.py <out.json> <tag=simdir> ...
Per tag and arm (ale_true, ale_inferred, whichever exist):
  R          = sum PP (fitted O_R, completed families) / true root count
  R_flat     = same with the flat prior (O_R = 1); prior multiplier = sum PP / sum PP_flat
  false_mass = sum PP over non-root families; missed_mass = sum (1 - PP) over root families
               (families without a PP count as PP 0); both also as a share of the true root count
  calls      = at PP >= 0.5 and >= 0.75: n called, false share, recall
  reliability: 5 equal PP bins over families with a PP: n, mean PP, share truly root; ECE = sum n_b/N |mean - share|
  R*         = sum PP over families completed in both arms / root families among them (v5c); Q = R*_inf / R*_true
Decision (v5c): mean of R*_inf over seeds (tags starting with "s"): > 1.25 inflates, < 0.8 deflates, else survives.
"""
import csv
import json
import sys


def rows(p):
    return {r["family"]: r for r in csv.DictReader(open(p), delimiter="\t")}


def arm_stats(rr, luca, o_r):
    ok = {f: float(r["pp"]) for f, r in rr.items() if r["status"] == "ok"}
    flat = {f: float(r["pp_flat"]) for f, r in rr.items() if r["status"] == "ok"}
    n = len(luca)
    s, sf = sum(ok.values()), sum(flat.values())
    res = {"R": s / n, "R_flat": sf / n, "sum_pp": s, "sum_pp_flat": sf, "prior_multiplier": s / sf if sf else None,
           "O_R": o_r, "n_failed": sum(r["status"].startswith("ALE") for r in rr.values()),
           "false_mass": sum(p for f, p in ok.items() if f not in luca),
           "missed_mass": sum(1 - ok.get(f, 0.0) for f in luca)}
    res["false_share_of_true"] = res["false_mass"] / n
    res["missed_share_of_true"] = res["missed_mass"] / n
    for t in (0.5, 0.75):
        called = [f for f, p in ok.items() if p >= t]
        tp = sum(f in luca for f in called)
        res["calls_%g" % t] = {"n": len(called), "false_share": (len(called) - tp) / len(called) if called else None,
                                "recall": tp / n}
    bins, ece, N = [], 0.0, len(ok)
    for i in range(5):
        lo, hi = i / 5, (i + 1) / 5
        fs = [f for f, p in ok.items() if (lo <= p < hi) or (i == 4 and p == 1.0)]
        if not fs:
            bins.append({"bin": [lo, hi], "n": 0})
            continue
        m = sum(ok[f] for f in fs) / len(fs)
        sh = sum(f in luca for f in fs) / len(fs)
        ece += len(fs) / N * abs(m - sh)
        bins.append({"bin": [lo, hi], "n": len(fs), "mean_pp": m, "share_root": sh})
    res["reliability"], res["ECE"] = bins, ece
    return res, ok


def main():
    out = {}
    for arg in sys.argv[2:]:
        tag, sim = arg.split("=", 1)
        truth = rows(f"{sim}/sample/truth.tsv")
        luca = {f for f, r in truth.items() if r["luca"] == "1"}
        res, oks = {"true_root": len(luca)}, {}
        for arm in ("ale_true", "ale_inferred"):
            try:
                rr = rows(f"{sim}/{arm}/root_pp.tsv")
            except FileNotFoundError:
                continue
            o_r = json.load(open(f"{sim}/{arm}/or_fit.json"))["O_R"]
            res[arm], oks[arm] = arm_stats(rr, luca, o_r)
        if len(oks) == 2:
            both = set(oks["ale_true"]) & set(oks["ale_inferred"])
            nl = len(both & luca)
            res["n_both_ok"], res["root_both_ok"] = len(both), nl
            for arm in oks:
                res[arm]["Rstar"] = sum(oks[arm][f] for f in both) / nl
            res["Q"] = res["ale_inferred"]["Rstar"] / res["ale_true"]["Rstar"]
            res["paired_diff_Rstar"] = res["ale_inferred"]["Rstar"] - res["ale_true"]["Rstar"]
        out[tag] = res
    seeds = [t for t in out if t.startswith("s") and "ale_inferred" in out[t] and "Rstar" in out[t]["ale_inferred"]]
    if seeds:
        vals = [out[t]["ale_inferred"]["Rstar"] for t in seeds]
        m = sum(vals) / len(vals)
        out["decision_v5c"] = {"seeds": seeds, "Rstar_inf": vals, "mean": m, "range": [min(vals), max(vals)],
                               "verdict": "inflates" if m > 1.25 else "deflates" if m < 0.8 else "survives"}
    json.dump(out, open(sys.argv[1], "w"), indent=1)
    print(json.dumps(out.get("decision_v5c", {}), indent=1))


if __name__ == "__main__":
    main()
