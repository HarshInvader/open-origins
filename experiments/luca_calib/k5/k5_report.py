"""K5 report under prereg v6. python -I k5_report.py <out.json> <k5_results_dir> big1=<sim> big3=<sim>

For each world dir (s<seed>_ctrl, s<seed>_lam<L>, s1_rootctrl) reads sample/truth.tsv,
sample/stem_families.tsv (if any), ale_true/root_pp.tsv and ale_true/or_fit.json.
Big worlds: the K3 true-tree arm of the same seed (Linux ALE).
"""
import csv
import json
import os
import sys


def rows(p):
    return {r["family"]: r for r in csv.DictReader(open(p), delimiter="\t")}


def world(d):
    truth = rows(os.path.join(d, "sample", "truth.tsv"))
    root = {f for f, r in truth.items() if r["luca"] == "1"}
    rp = rows(os.path.join(d, "ale_true", "root_pp.tsv"))
    ok = {f: float(r["pp"]) for f, r in rp.items() if r["status"] == "ok"}
    flat = {f: float(r["pp_flat"]) for f, r in rp.items() if r["status"] == "ok"}
    failed = [f for f, r in rp.items() if r["status"].startswith("ALE")]
    sf = os.path.join(d, "sample", "stem_families.tsv")
    stem = rows(sf) if os.path.exists(sf) else {}
    s = sum(ok.values())
    n = len(root)
    out = {"true_root": n, "sum_pp": s, "R": s / n, "sum_pp_flat": sum(flat.values()),
           "prior_multiplier": s / sum(flat.values()), "O_R": json.load(open(os.path.join(d, "ale_true", "or_fit.json")))["O_R"],
           "split": {"root": sum(p for f, p in ok.items() if f in root),
                     "stem_born": sum(p for f, p in ok.items() if f in stem),
                     "other": sum(p for f, p in ok.items() if f not in root and f not in stem)},
           "n_ale": len(ok) + len(failed), "n_failed": len(failed), "failed_root": sum(f in root for f in failed),
           "completion": len(ok) / max(1, len(ok) + len(failed))}
    out["R_failed_as_1"] = (s + len(failed)) / n
    if stem:
        out["n_stem_born"] = len(stem)
        out["stem_present"] = sum(int(r["n_genes"]) > 0 for r in stem.values())
        out["Tstem_per_family"] = sum(int(r["Tstem"]) for r in stem.values()) / len(stem)
        out["stem_pp_ge_0.5"] = sum(1 for f in stem if ok.get(f, 0) >= 0.5)
    N, ece = len(ok), 0.0
    for i in range(5):
        fs = [f for f, p in ok.items() if (i / 5 <= p < (i + 1) / 5) or (i == 4 and p == 1.0)]
        if fs:
            ece += len(fs) / N * abs(sum(ok[f] for f in fs) / len(fs) - sum(f in root for f in fs) / len(fs))
    out["ECE"] = ece
    wj = os.path.join(d, "k5_world.json")
    if os.path.exists(wj):
        w = json.load(open(wj))
        out["world"] = {k: w[k] for k in ("lambda", "x_stem", "n_stem_born", "stem_born_present", "stem_born_ge2", "events",
                                          "true_luca_new", "rootctrl") if k in w}
    return out


def main():
    outp, base = sys.argv[1], sys.argv[2]
    big = dict(a.split("=", 1) for a in sys.argv[3:])
    res = {"big": {}, "worlds": {}}
    for k, sim in big.items():
        res["big"][k.replace("big", "s")] = world(sim)
    for w in sorted(os.listdir(base)):
        d = os.path.join(base, w)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "ale_true", "root_pp.tsv")):
            res["worlds"][w] = world(d)
    for w, r in res["worlds"].items():
        seed = w.split("_")[0]
        if seed in res["big"] and "rootctrl" not in w:
            r["H"] = r["sum_pp"] / res["big"][seed]["sum_pp"]
            c = res["worlds"].get(seed + "_ctrl")
            if c:
                r["R_minus_Rctrl"] = r["R"] - c["R"]
    # decision (v6): lambda read only if both remaining seeds (1, 3) are matched; here lambda 4 only
    rc = res["worlds"].get("s1_rootctrl")
    dec = {"positive_control_R": rc["R"] if rc else None,
           "positive_control_pass": bool(rc and 0.95 <= rc["R"] <= 1.15)}
    lam4 = [res["worlds"][k] for k in ("s1_lam4", "s3_lam4") if k in res["worlds"]]
    if len(lam4) == 2:
        H = [x["H"] for x in lam4]
        E = [x["R_minus_Rctrl"] for x in lam4]
        mH, mE = sum(H) / 2, sum(E) / 2
        same_H = all(h >= 0.5 for h in H) or all(h < 0.5 for h in H)
        same_E = all(e > 0.5 for e in E) or all(e <= 0.5 for e in E)
        incl_H = abs(mH - 0.5) <= 0.05 or not same_H
        incl_E = abs(mE - 0.5) <= 0.1 or not same_E
        if not dec["positive_control_pass"]:
            v = "not applied: positive control failed"
        elif incl_H:
            v = "inconclusive on H"
        elif mH >= 0.5:
            v = "cannot discriminate in a loosely matched world (no read seed is tightly matched)"
        elif incl_E:
            v = "inconclusive on R_small - R_ctrl"
        elif mE <= 0.5:
            v = "discriminates"
        else:
            v = "partial: inflates a small root genome by R_small - R_ctrl = %.2f over background at lambda 4" % mE
        dec.update({"lambda": 4, "H": H, "mean_H": mH, "R_minus_Rctrl": E, "mean_R_minus_Rctrl": mE, "verdict": v})
    res["decision_v6"] = dec
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps(dec, indent=1))


if __name__ == "__main__":
    main()
