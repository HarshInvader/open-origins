"""K7 planted test (prereg docs/prereg/k7_realism_bound.md): K5-style worlds with a known stem-transfer
multiplier m, reconciled with the unchanged K5 pipeline, scored with k7_measure.

Imports experiments/luca_calib/k5/stemsim.py and pipeline/run_ale.py; modifies nothing there.
All outputs go to a scratch directory given on the command line (keep it outside the repo).

Usage (python3 must have numpy and ete3, e.g. the phylo env; run with -I):
  k7_planted.py build      <src_sim> <scratch> --seed 1 --m 1 50 150 600 [--n 250] [--cap 0]
  k7_planted.py background <src_sim> <scratch> --seed 1 [--ale-dir ale_true]
  k7_planted.py ale        <scratch> --m 600 [--workers 2] [--budget 480]
  k7_planted.py report     <scratch> <out.json>

build: per rung m, the N stem-born families (stemsim.stem_family; birth point and rates from rng
  [seed, i], events from rng [seed, 7000 + m, i]; stem extra rate x = m * genome transfer mean).
  Trees of families with >= 2 sampled genes are written, except those over --cap genes
  (cap 0 = no cap; the laptop pilot uses 152, the last size the macOS ALE build can run).
background: parses the source world's existing reconciliations of the kept families (K5 rule: 20
  root families + all non-root families) into records.
ale: reconciles a rung's trees with pipeline/run_ale.run_family (identical ALE commands), parses each
  .uml_rec at once into a record and deletes the ALE files. Stops starting families after --budget s.
report: M1, M2 (k7_measure.world_measures) per rung over background + stem-born records, with a
  1,000-sample family bootstrap (numpy seed 7), plus the control (background only).
"""
import argparse
import json
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LC = os.path.join(HERE, "..", "luca_calib")
sys.path.insert(0, os.path.join(LC, "k5"))
sys.path.insert(0, os.path.join(LC, "pipeline"))
sys.path.insert(0, HERE)
import k7_measure  # noqa: E402

NICE = ["taskpolicy", "-b", "nice", "-n", "20"] if shutil.which("taskpolicy") else ["nice", "-n", "20"]
KEEP = ("x_stem_out", "x_int_out", "x_term_out", "x_stem_in", "x_root_tok", "t_tokens", "pres_stem", "pres_int",
        "pres_term", "t_in_stem", "cop_stem", "t_in_all", "cop_all", "pres_root")


def compact(rec):
    return {k: round(rec[k], 6) for k in KEEP}


def append_jsonl(path, obj):
    with open(path, "a") as f:
        f.write(json.dumps(obj) + "\n")


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path) if l.strip()]


def cmd_build(a):
    import stemsim
    src = os.path.abspath(a.src)
    S = stemsim.Species(src)
    g = stemsim.cfg_of(src)["genome"]
    truth, keep_luca, kept = stemsim.kept_rows(src, a.seed, 20)
    base_id = 10 ** (len(str(max(int(r["family"]) for r in truth))) + 1)
    tau, stem_len = stemsim.stem_tau(S)
    os.makedirs(a.scratch, exist_ok=True)
    meta = {"source": src, "seed": a.seed, "n": a.n, "cap": a.cap, "t_background": g["transfer"],
            "tau": tau, "stem_length": stem_len, "base_id": base_id, "rungs": {}}
    for m in a.m:
        x = m * g["transfer"]
        d = os.path.join(a.scratch, "m%g" % m)
        os.makedirs(os.path.join(d, "trees"), exist_ok=True)
        fams, t0 = [], time.time()
        for i in range(a.n):
            r = stemsim.stem_family(S, g, a.seed, 7000 + int(m), i, x, base_id, 10 ** 7)
            row = {"family": r["family"], "n_genes": r["n_genes"], "nA": r["nA"], "nB": r["nB"],
                   "Tstem": r["ctr"]["Tstem"], "mrca": r["ctr"]["mrca"]}
            if r["n_genes"] >= 2 and (a.cap == 0 or r["n_genes"] <= a.cap):
                with open(os.path.join(d, "trees", r["family"] + ".nwk"), "w") as f:
                    f.write(r["nwk"] + "\n")
                row["run"] = True
            else:
                row["run"] = False
            fams.append(row)
        with open(os.path.join(d, "families.json"), "w") as f:
            json.dump(fams, f)
        ge2 = [r for r in fams if r["n_genes"] >= 2]
        meta["rungs"]["%g" % m] = {
            "x_stem": x, "lambda_equiv": x * tau, "n_present": sum(1 for r in fams if r["n_genes"] > 0),
            "n_ge2": len(ge2), "n_run": sum(r["run"] for r in fams),
            "n_skipped_over_cap": sum(1 for r in ge2 if not r["run"]),
            "Tstem_per_family": sum(r["Tstem"] for r in fams) / a.n,
            "true_luca_new": sum(1 for r in fams if r["mrca"] > 0),
            "both_domains": sum(1 for r in fams if r["nA"] > 0 and r["nB"] > 0),
            "genes_run_total": sum(r["n_genes"] for r in fams if r["run"]), "build_s": round(time.time() - t0, 1)}
        print("m=%g" % m, json.dumps(meta["rungs"]["%g" % m]), flush=True)
    # species tree for ALE, exactly as run_ale.write_species_tree writes it
    from run_ale import write_species_tree
    write_species_tree(src, a.scratch)
    with open(os.path.join(a.scratch, "build_meta.json"), "w") as f:
        json.dump(meta, f, indent=1)


def cmd_background(a):
    import stemsim
    src = os.path.abspath(a.src)
    truth, keep_luca, kept = stemsim.kept_rows(src, a.seed, 20)
    rec_dir = os.path.join(src, a.ale_dir, "uml_rec")
    out = os.path.join(a.scratch, "background.jsonl")
    if os.path.exists(out):
        os.remove(out)
    n_ok = n_missing = n_single = 0
    for r in kept:
        if int(r["n_genes"]) < 2:
            n_single += 1
            continue
        p = os.path.join(rec_dir, "S.nwk_ale_fam_%s.ale.uml_rec" % r["family"])
        if not os.path.exists(p):
            n_missing += 1
            continue
        rec = compact(k7_measure.family_record(p))
        rec["family"], rec["root_family"] = r["family"], r["family"] in keep_luca
        append_jsonl(out, rec)
        n_ok += 1
    info = {"kept": len(kept), "parsed": n_ok, "missing_uml_rec": n_missing, "single_gene": n_single,
            "ale_dir": a.ale_dir}
    with open(os.path.join(a.scratch, "background_meta.json"), "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info))


def cmd_ale(a):
    from run_ale import run_family
    d = os.path.join(a.scratch, "m%g" % a.m)
    out = os.path.join(d, "ale")
    os.makedirs(os.path.join(out, "uml_rec"), exist_ok=True)
    if not os.path.exists(os.path.join(out, "S.nwk")):
        shutil.copy(os.path.join(a.scratch, "S.nwk"), os.path.join(out, "S.nwk"))
    recs_path = os.path.join(d, "records.jsonl")
    done = {r["family"] for r in read_jsonl(recs_path)}
    base_id = json.load(open(os.path.join(a.scratch, "build_meta.json")))["base_id"]
    sel = lambda r: r["run"] and (a.max_index == 0 or int(r["family"]) - base_id < a.max_index)
    fams = [r for r in json.load(open(os.path.join(d, "families.json"))) if sel(r) and r["family"] not in done]
    fams.sort(key=lambda r: r["n_genes"])          # small first, so a chunk finishes many families
    t0 = time.time()
    n_new = n_fail = 0

    def one(r):
        fam = r["family"]
        if time.time() - t0 > a.budget:
            return fam, "not_started", 0.0
        return run_family(fam, os.path.join(d, "trees", fam + ".nwk"), out, 100, 1, NICE)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, r) for r in fams]
        for fu in as_completed(futs):
            fam, st, secs = fu.result()
            if st == "not_started":
                continue
            rec_file = os.path.join(out, "uml_rec", "S.nwk_ale_fam_%s.ale.uml_rec" % fam)
            if st in ("ok", "done") and os.path.exists(rec_file):
                rec = compact(k7_measure.family_record(rec_file))
                rec.update({"family": fam, "status": "ok", "secs": round(secs, 2)})
                os.remove(rec_file)
                n_new += 1
            else:
                rec = {"family": fam, "status": st, "secs": round(secs, 2)}
                n_fail += 1
            append_jsonl(recs_path, rec)
            shutil.rmtree(os.path.join(out, "fams", fam), ignore_errors=True)
    done = {r["family"] for r in read_jsonl(recs_path)}
    left = len([r for r in json.load(open(os.path.join(d, "families.json"))) if sel(r) and r["family"] not in done])
    print(json.dumps({"m": a.m, "new_ok": n_new, "new_failed": n_fail, "left": left,
                      "wall_s": round(time.time() - t0, 1)}))


def boot(recs, B=1000, seed=7):
    rng = np.random.default_rng(seed)
    keys = ("x_stem_out", "pres_stem", "x_int_out", "pres_int", "t_in_stem", "cop_stem", "t_in_all", "cop_all")
    X = np.array([[r[k] for k in keys] for r in recs])
    n = len(X)
    idx = rng.integers(0, n, size=(B, n))
    sums = X[idx].sum(axis=1)                       # B x 8
    with np.errstate(divide="ignore", invalid="ignore"):
        m1 = (sums[:, 0] / sums[:, 1]) / (sums[:, 2] / sums[:, 3])
        m2 = (sums[:, 4] / sums[:, 5]) / (sums[:, 6] / sums[:, 7])
    q = lambda v: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
    return {"M1_ci": q(m1), "M2_ci": q(m2)}


def cmd_report(a):
    bg = read_jsonl(os.path.join(a.scratch, "background.jsonl"))
    meta = json.load(open(os.path.join(a.scratch, "build_meta.json")))
    meta = dict(meta, source=os.path.relpath(meta["source"], os.path.join(HERE, "..")))   # no absolute paths
    out = {"build": meta, "background": json.load(open(os.path.join(a.scratch, "background_meta.json"))),
           "control": {**k7_measure.world_measures(bg), **boot(bg)}, "rungs": {}}
    for m in sorted(meta["rungs"], key=float):
        inside = lambda f: a.max_index == 0 or int(f) - meta["base_id"] < a.max_index
        recs = [r for r in read_jsonl(os.path.join(a.scratch, "m%s" % m, "records.jsonl")) if inside(r["family"])]
        ok = [r for r in recs if r.get("status") == "ok"]
        fams = [r for r in json.load(open(os.path.join(a.scratch, "m%s" % m, "families.json"))) if inside(r["family"])]
        n_run = sum(r["run"] for r in fams)
        n_skip = sum(1 for r in fams if r["n_genes"] >= 2 and not r["run"])
        stem_only = k7_measure.world_measures(ok) if ok else {}
        row = {**k7_measure.world_measures(bg + ok), **boot(bg + ok), "stem_born_ok": len(ok),
               "stem_born_failed": len(recs) - len(ok), "stem_born_not_done": n_run - len(recs),
               "subset_n_run": n_run, "subset_skipped_over_cap": n_skip,
               "stem_born_only": stem_only, "ale_core_s": round(sum(r.get("secs", 0) for r in recs), 1),
               "share_stem_donor_ge_0.5": (sum(1 for r in ok if r["x_stem_out"] >= 0.5) / len(ok)) if ok else None,
               "mean_pres_root_stem_born": (sum(r["pres_root"] for r in ok) / len(ok)) if ok else None}
        out["rungs"][m] = {**meta["rungs"][m], **row}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"control": {k: out["control"][k] for k in ("M1", "M1_ci", "M2", "M2_ci")},
                      "rungs": {m: {k: r[k] for k in ("M1", "M1_ci", "M2", "M2_ci", "stem_born_ok",
                                                      "stem_born_failed", "stem_born_not_done",
                                                      "subset_skipped_over_cap", "share_stem_donor_ge_0.5",
                                                      "mean_pres_root_stem_born", "ale_core_s")}
                                for m, r in out["rungs"].items()}}, indent=1))


def cmd_world(a):
    """Portability: M1, M2 over every .uml_rec in existing reconciliation directories (big worlds)."""
    out = {}
    for d in a.dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith(".uml_rec"))
        recs = [compact(k7_measure.family_record(os.path.join(d, f))) for f in files]
        key = os.path.relpath(os.path.abspath(d), os.path.join(HERE, ".."))
        out[key] = {**k7_measure.world_measures(recs), **boot(recs)}
        print(key, json.dumps({k: out[key][k] for k in ("M1", "M1_ci", "M2", "M2_ci", "n_families")}), flush=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("world")
    w.add_argument("out"), w.add_argument("dirs", nargs="+")
    b = sub.add_parser("build")
    b.add_argument("src"), b.add_argument("scratch")
    b.add_argument("--seed", type=int, required=True)
    b.add_argument("--m", type=float, nargs="+", required=True)
    b.add_argument("--n", type=int, default=250)
    b.add_argument("--cap", type=int, default=0)
    g = sub.add_parser("background")
    g.add_argument("src"), g.add_argument("scratch")
    g.add_argument("--seed", type=int, required=True)
    g.add_argument("--ale-dir", default="ale_true")
    e = sub.add_parser("ale")
    e.add_argument("scratch")
    e.add_argument("--m", type=float, required=True)
    e.add_argument("--workers", type=int, default=2)
    e.add_argument("--budget", type=float, default=480)
    e.add_argument("--max-index", type=int, default=0, help="pilot: only stem-born families with index < this")
    r = sub.add_parser("report")
    r.add_argument("scratch"), r.add_argument("out")
    r.add_argument("--max-index", type=int, default=0)
    a = ap.parse_args()
    {"build": cmd_build, "background": cmd_background, "ale": cmd_ale, "report": cmd_report,
     "world": cmd_world}[a.cmd](a)


if __name__ == "__main__":
    main()
