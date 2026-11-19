"""Score root presence probabilities against the planted LUCA.

Usage:
    python score.py <simdir> [--run alerax_true_PER-FAMILY_ROOT] [--bins 0,0.2,0.4,0.6,0.8,1.0]

Without --run, every <simdir>/alerax_*/root_pp.tsv is scored. Writes score.json next to each
root_pp.tsv and prints a table.

Universe: every family in sample/truth.tsv (present in >= 1 sampled genome, or at the MRCA).
Families with no PP (1 sampled gene, or absent from the sample) count as PP = 0.
  T75 / T50   : PP >= 0.75 / 0.5
  T75d / T50d : as above and present in >= 1 sampled genome of each domain
  recall      = true LUCA called / true LUCA size (all true LUCA families, sampled or not)
  precision   = true LUCA called / called (None when nothing is called)
  E = sum of PP over the universe; R = E / true LUCA size
  calibration : per PP bin, n families and the share that are true LUCA; plus the 0.4-0.6 bin (P5)
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_tsv, write_json


def score(sim, run_dir, bins):
    truth = read_tsv(os.path.join(sim, "sample", "truth.tsv"))
    pp = {r["family"]: float(r["pp"]) for r in read_tsv(os.path.join(run_dir, "root_pp.tsv"))}
    fam = []
    for r in truth:
        fam.append({"f": r["family"], "luca": int(r["luca"]), "both": int(r["n_genomes_A"]) > 0 and int(r["n_genomes_B"]) > 0,
                    "pp": pp.get(r["family"], 0.0), "n": int(r["n_genes"])})
    n_true = sum(x["luca"] for x in fam)
    res = {"true_luca_size": n_true, "n_families": len(fam),
           "true_luca_reconcilable": sum(1 for x in fam if x["luca"] and x["n"] >= 2),
           "true_luca_in_both_domains": sum(1 for x in fam if x["luca"] and x["both"]),
           "tiers": {}}
    for tier, thr, dom in [("T75", 0.75, False), ("T50", 0.5, False), ("T75d", 0.75, True), ("T50d", 0.5, True)]:
        called = [x for x in fam if x["pp"] >= thr and (x["both"] or not dom)]
        tp = sum(x["luca"] for x in called)
        res["tiers"][tier] = {"called": len(called), "tp": tp,
                              "recall": tp / n_true if n_true else None,
                              "precision": tp / len(called) if called else None,
                              "false_share": 1 - tp / len(called) if called else None}
    E = sum(x["pp"] for x in fam)
    res["E"] = E
    res["R"] = E / n_true if n_true else None
    cal = []
    for lo, hi in list(zip(bins[:-1], bins[1:])) + [(0.4, 0.6)]:
        last = hi >= bins[-1]
        inb = [x for x in fam if lo <= x["pp"] < hi or (last and x["pp"] == hi)]
        cal.append({"bin": "%.2f-%.2f" % (lo, hi), "n": len(inb), "n_luca": sum(x["luca"] for x in inb),
                    "share_luca": sum(x["luca"] for x in inb) / len(inb) if inb else None,
                    "mean_pp": sum(x["pp"] for x in inb) / len(inb) if inb else None})
    res["calibration"] = cal
    return res


def fmt(v):
    return "  -  " if v is None else "%.3f" % v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--run", action="append")
    ap.add_argument("--bins", default="0,0.2,0.4,0.6,0.8,1.0")
    a = ap.parse_args()
    sim = os.path.abspath(a.simdir)
    bins = [float(x) for x in a.bins.split(",")]
    runs = [os.path.join(sim, r) for r in a.run] if a.run else sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(sim, "alerax_*", "root_pp.tsv")))
    for rd in runs:
        res = score(sim, rd, bins)
        write_json(os.path.join(rd, "score.json"), res)
        print("== %s  true LUCA %d (reconcilable %d)  E %.2f  R %s"
              % (os.path.basename(rd), res["true_luca_size"], res["true_luca_reconcilable"], res["E"], fmt(res["R"])))
        for t, v in res["tiers"].items():
            print("   %-5s called %3d  recall %s  precision %s" % (t, v["called"], fmt(v["recall"]), fmt(v["precision"])))
        print("   calibration: " + "; ".join("%s n=%d luca=%s" % (c["bin"], c["n"], fmt(c["share_luca"])) for c in res["calibration"]))


if __name__ == "__main__":
    main()
