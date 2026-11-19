"""Score root presence probabilities against the planted LUCA.

Usage:
    python score.py <simdir> [--run ale_inferred] [--pp-column pp] [--bins 0,0.2,0.4,0.6,0.8,1.0]
                    [--out-dir DIR] [--quiet]

Without --run, every <simdir>/alerax_*/ and <simdir>/ale_*/ root_pp.tsv is scored. Writes
score[_<column>].json next to each root_pp.tsv (or into --out-dir as <run>_score[_<column>].json)
and prints a table unless --quiet. For ale_* runs, --pp-column pp is the fitted-O_R PP and
pp_flat the O_R = 1 sensitivity; both are scored when --pp-column is not given.

Universe: every family in sample/truth.tsv (present in >= 1 sampled genome, or at the MRCA).
Families with no PP (1 sampled gene, or absent from the sample) count as PP = 0.
  T75 / T50   : PP >= 0.75 / 0.5
  T75d / T50d : as above and present in >= 1 sampled genome of each domain
  recall      = true LUCA called / true LUCA size (all true LUCA families, sampled or not)
  precision   = true LUCA called / called (None when nothing is called)
  E = sum of PP over the universe; R = E / true LUCA size
  calibration : per PP bin, n families and the share that are true LUCA; plus the 0.4-0.6 bin (P5)
  gate_v3     : planted-control gate (prereg v3 change 2). Identifiable LUCA families = true LUCA,
                present in >= 1 sampled genome of each domain, >= 3 sampled genes.
                pass = T50 recall over identifiable LUCA >= 0.9 and non-LUCA share of all T50 calls
                <= 0.05. R over all LUCA families is reported with it but does not gate.
  baselines   : prereg v4 D, from sample/copy_numbers.tsv (presence = copies >= 1), scored like a tier.
                B1 (Mrnjavac): present in >= 50% of the genomes of >= 4 higher taxa in each domain;
                higher taxa = clades.higher_taxa (cut each domain's sampled tree at the depth giving 6
                clades, else the nearest count >= 4). B2: present in > 1% of genomes in both domains.
  stem        : prereg v4 C, if sample/stem_transfers.tsv exists (stem_transfers.py): share of false
                T50d calls whose family was transferred stem to stem.
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_tsv, write_json
import clades


def baselines(sim):
    """Return {family: (b1, b2)} for families in copy_numbers.tsv, plus the taxa used."""
    from ete3 import Tree
    sp = Tree(open(os.path.join(sim, "sample", "species_tree.nwk")).readline().strip(), format=1)
    dom = {r["species"]: r["domain"] for r in read_tsv(os.path.join(sim, "sample", "domains.tsv"))}
    taxa = {d: clades.higher_taxa(sp, [k for k, v in dom.items() if v == d]) for d in ("A", "B")}
    out = {}
    with open(os.path.join(sim, "sample", "copy_numbers.tsv")) as f:
        sps = f.readline().rstrip("\n").split("\t")[1:]
        for line in f:
            h = line.rstrip("\n").split("\t")
            pres = {s_: int(c) > 0 for s_, c in zip(sps, h[1:])}
            b1 = all(sum(1 for t in taxa[d] if sum(pres[x] for x in t) >= 0.5 * len(t)) >= 4 for d in ("A", "B"))
            b2 = all(sum(pres[x] for x in dom if dom[x] == d) / sum(1 for x in dom if dom[x] == d) > 0.01
                     for d in ("A", "B"))
            out[h[0]] = (b1, b2)
    return out, {d: [len(t) for t in v] for d, v in taxa.items()}


def gate_v3(fam, R):
    ident = [x for x in fam if x["luca"] and x["both"] and x["n"] >= 3]
    called = [x for x in fam if x["pp"] >= 0.5]
    tp = sum(1 for x in ident if x["pp"] >= 0.5)
    recall = tp / len(ident) if ident else None
    false_share = sum(1 for x in called if not x["luca"]) / len(called) if called else None
    return {"n_identifiable_luca": len(ident), "t50_tp_identifiable": tp, "t50_recall_identifiable": recall,
            "t50_called": len(called), "t50_false_share": false_share,
            "pass": bool(recall is not None and recall >= 0.9 and (false_share is None or false_share <= 0.05)),
            "R_all_luca_not_gating": R}


def score(sim, run_dir, bins, column="pp"):
    truth = read_tsv(os.path.join(sim, "sample", "truth.tsv"))
    pp = {r["family"]: float(r[column]) for r in read_tsv(os.path.join(run_dir, "root_pp.tsv"))}
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
    res["gate_v3"] = gate_v3(fam, res["R"])
    has_cn = os.path.exists(os.path.join(sim, "sample", "copy_numbers.tsv"))
    bl, taxa = baselines(sim) if has_cn else ({}, None)
    res["baselines"] = {"higher_taxa_sizes": taxa}
    for i, name in (enumerate(("B1", "B2")) if has_cn else []):
        called = [x for x in fam if bl.get(x["f"], (False, False))[i]]
        tp = sum(x["luca"] for x in called)
        res["baselines"][name] = {"called": len(called), "tp": tp, "recall": tp / n_true if n_true else None,
                                  "precision": tp / len(called) if called else None,
                                  "false_share": 1 - tp / len(called) if called else None}
    stp = os.path.join(sim, "sample", "stem_transfers.tsv")
    if os.path.exists(stp):
        flag = {r["family"]: int(r["stem_to_stem"]) for r in read_tsv(stp)}
        false50d = [x for x in fam if x["pp"] >= 0.5 and x["both"] and not x["luca"]]
        k = sum(flag.get(x["f"], 0) for x in false50d)
        res["stem_transfer"] = {"false_t50d": len(false50d), "stem_to_stem": k,
                                "share": k / len(false50d) if false50d else None,
                                "families_flagged": sum(flag.values())}
    res["pp_column"] = column
    return res


def fmt(v):
    return "  -  " if v is None else "%.3f" % v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--run", action="append")
    ap.add_argument("--bins", default="0,0.2,0.4,0.6,0.8,1.0")
    ap.add_argument("--pp-column", default=None)
    ap.add_argument("--out-dir", default=None, help="write score files here instead of next to root_pp.tsv")
    ap.add_argument("--quiet", action="store_true", help="print nothing (sealed pilot scoring)")
    a = ap.parse_args()
    sim = os.path.abspath(a.simdir)
    bins = [float(x) for x in a.bins.split(",")]
    runs = [os.path.join(sim, r) for r in a.run] if a.run else sorted(
        os.path.dirname(p) for p in glob.glob(os.path.join(sim, "alerax_*", "root_pp.tsv"))
        + glob.glob(os.path.join(sim, "ale_*", "root_pp.tsv")))
    jobs = []
    for rd in runs:
        header = open(os.path.join(rd, "root_pp.tsv")).readline().rstrip("\n").split("\t")
        cols = [a.pp_column] if a.pp_column else [c for c in ("pp", "pp_flat") if c in header]
        jobs += [(rd, c) for c in cols]
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)
    for rd, col in jobs:
        res = score(sim, rd, bins, col)
        name = "score.json" if col == "pp" else "score_%s.json" % col
        dest = os.path.join(a.out_dir, os.path.basename(rd) + "_" + name) if a.out_dir else os.path.join(rd, name)
        write_json(dest, res)
        if a.quiet:
            continue
        g = res["gate_v3"]
        print("== %s  true LUCA %d (reconcilable %d)  E %.2f  R %s"
              % (os.path.basename(rd), res["true_luca_size"], res["true_luca_reconcilable"], res["E"], fmt(res["R"])))
        for t, v in res["tiers"].items():
            print("   %-5s called %3d  recall %s  precision %s" % (t, v["called"], fmt(v["recall"]), fmt(v["precision"])))
        print("   v3 gate: %s  (identifiable LUCA %d, T50 recall %s, T50 false share %s; R %s, not gating)  [%s]"
              % ("PASS" if g["pass"] else "FAIL", g["n_identifiable_luca"], fmt(g["t50_recall_identifiable"]),
                 fmt(g["t50_false_share"]), fmt(g["R_all_luca_not_gating"]), col))
        b = res["baselines"]
        if "B1" in b:
            print("   B1 called %d recall %s precision %s | B2 called %d recall %s precision %s"
                  % (b["B1"]["called"], fmt(b["B1"]["recall"]), fmt(b["B1"]["precision"]),
                     b["B2"]["called"], fmt(b["B2"]["recall"]), fmt(b["B2"]["precision"])))
        if "stem_transfer" in res:
            st = res["stem_transfer"]
            print("   stem-to-stem: %d of %d false T50d calls" % (st["stem_to_stem"], st["false_t50d"]))
        print("   calibration: " + "; ".join("%s n=%d luca=%s" % (c["bin"], c["n"], fmt(c["share_luca"])) for c in res["calibration"]))


if __name__ == "__main__":
    main()
