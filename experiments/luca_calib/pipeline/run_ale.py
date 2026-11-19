"""Moody et al.'s two-step root-origination method (prereg v3 change 1).

Usage:
    python run_ale.py <simdir> --trees inferred|true [--workers 4] [--samples 100] [--seed 1]
                      [--max-fams N] [--reweight-only]

Step 1 (per family, in parallel): ALEobserve on the family's trees (the 1,000 UFBoot trees for
  --trees inferred; the single true tree for --trees true), then ALEml_undated with the sampled
  species tree and ALE's defaults: flat origination (O_R=1), DTL rates optimised, fraction missing 0
  (ALE's default when no fraction_missing file is given). Gene names are <species>_<id>, so
  separators=_ . Files are named so that Moody's family parse, fname.split("_")[3].split(".")[0],
  returns our family id: the output is  S.nwk_ale_fam_<FAM>.ale.uml_rec .
Step 2: Moody's reweighting. Their functions read_file() and rell() are taken verbatim from
  raw/moody/COG_OR_reconciliation/O_R_Optimization.py (sha256 checked), by AST extraction with only
  the @ray.remote decorator removed, and executed under `from numpy import *` as in their module.
  Their module-level steps are reproduced line for line without ray: max_id from the last branch
  line of a .uml_rec, ll0 under a flat prior, fx(O_R), BayesianOptimization(pbounds (1, 20),
  random_state=1).maximize(init_points=10, n_iter=50). One global O_R over all families.
  Root PP = p[max_id] at the fitted O_R. Sensitivity: p[max_id] with a flat prior (x = 1 everywhere,
  i.e. ALE's own O_R = 1), which is v3's "O_R fixed at 1, flat origination".
  max_id is checked to be the root of S using the S: line of every .uml_rec.

Families with 1 sampled gene cannot be reconciled: pp = pp_flat = 0 (counted as missed).

Outputs in <simdir>/ale_<trees>/:
  S.nwk, fams/<FAM>/ (ALE work dirs), uml_rec/*.uml_rec, root_pp.tsv
  (family, pp, pp_flat, ml_e, n_genes, status), or_fit.json, run_meta.json
Exit status 3 if any family failed in ALE (outputs are still written; failed families get pp 0).
"""
import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EXP, wait_for_memory, log, read_tsv, update_timings, write_json
from ete3 import Tree

ALE_BIN = os.environ.get("LUCA_ALE_BIN", os.path.join(EXP, "ext", "ale_build", "bin"))
MOODY_SCRIPT = os.path.join(EXP, "raw", "moody", "COG_OR_reconciliation", "O_R_Optimization.py")
MOODY_SHA256 = "9de8bb9f0d460a2c8fedd217ea43cb7c88b512dbfee313fad5d6353451cf282b"
S_NAME = "S.nwk"
PREFIX = "ale_fam_"


# ---------------------------------------------------------------- Moody's functions, verbatim
def load_moody(script=MOODY_SCRIPT, check_hash=True):
    """Return a namespace holding Moody's read_file and rell, exactly as written in their script."""
    src = open(script).read()
    if check_hash:
        h = hashlib.sha256(src.encode()).hexdigest()
        if h != MOODY_SHA256:
            raise RuntimeError("O_R_Optimization.py sha256 %s != expected %s" % (h, MOODY_SHA256))
    mod = ast.parse(src)
    funcs = []
    for node in mod.body:
        if isinstance(node, ast.FunctionDef) and node.name in ("read_file", "rell"):
            node.decorator_list = []          # drop @ray.remote: the only change
            funcs.append(node)
    if sorted(f.name for f in funcs) != ["read_file", "rell"]:
        raise RuntimeError("read_file/rell not found in Moody's script")
    ns = {}
    exec("from numpy import *", ns)          # their module does `from numpy import *`
    exec(compile(ast.Module(body=funcs, type_ignores=[]), script, "exec"), ns)
    return ns


def moody_max_id(lookin, fname):
    """Their 'work around to get root_id, which is the largest id', line for line."""
    for line in open(lookin + "/" + fname).readlines():
        if "branch" in line:
            tmp, e, Ds, Ts, Ls, Os, cs, ss, ep, prp, ll = line.split()
            if "(" in e: e = e.split("(")[1].replace(")", "")
            e = int(e)
    return e


def check_root_is_max_id(path, max_id):
    """ALE numbers leaves 0..n-1, then internal nodes bottom-up; the S: line carries those ids as
    internal labels. Check that the root carries max_id (or, if the root label is not written, that
    max_id is the only internal id missing from the non-root nodes)."""
    s_line = next(l for l in open(path) if l.startswith("S:"))
    nwk = s_line.split("\t", 1)[1].strip()
    t = Tree(nwk, format=1)
    n = len(t)
    if max_id != 2 * n - 2:
        return False, "max_id %d but %d leaves" % (max_id, n)
    if t.name not in ("", None):
        return int(t.name) == max_id, "root label %s" % t.name
    internal = sorted(int(x.name) for x in t.traverse() if not x.is_leaf() and not x.is_root())
    ok = internal == list(range(n, 2 * n - 2))
    return ok, "root label absent; non-root internal ids %s n..2n-3" % ("are" if ok else "are not")


def bayes_opt_version():
    try:
        from importlib.metadata import version
        return version("bayesian-optimization")
    except Exception:
        return "?"


def fit_global_or(lookin, ns, init_points=10, n_iter=50, random_state=1):
    """Moody's module-level procedure without ray. Returns (fams, fit dict, results at ML O_R,
    results under the flat prior)."""
    from numpy import ones, exp
    from bayes_opt import BayesianOptimization
    import bayes_opt
    names = sorted(f for f in os.listdir(lookin) if ".uml_rec" in f)
    max_id = moody_max_id(lookin, names[0])
    ns["lookin"], ns["max_id"] = lookin, max_id
    raw = [ns["read_file"](f) for f in names]
    fams = [r for r in raw if isinstance(r, dict)]
    errors = [n for n, r in zip(names, raw) if not isinstance(r, dict)]
    rell = ns["rell"]
    ll0 = sum([result["rll"] for result in [rell(fam, ones(max_id + 1)) for fam in fams]])

    def fx(O_R):
        x = ones(max_id + 1)
        x[max_id] = exp(O_R)
        results = [rell(fam, x) for fam in fams]
        return sum([result["rll"] for result in results]) - ll0

    # allow_duplicate_points=True: bayes_opt >= 1.4 raises NotUniqueError when the GP proposes a point
    # already probed (e.g. an optimum at a bound); bayes_opt <= 1.2 returned the cached value instead.
    # 1.2 does not run with numpy 2, so we use 1.4.3 with duplicates allowed. The maximum is unaffected.
    optimizer = BayesianOptimization(f=fx, pbounds={'O_R': (1, 20)}, random_state=random_state, verbose=0,
                                     allow_duplicate_points=True)
    optimizer.maximize(init_points=init_points, n_iter=n_iter)
    O_R = optimizer.max["params"]["O_R"]
    x = ones(max_id + 1)
    x[max_id] = exp(O_R)
    results = [rell(fam, x) for fam in fams]
    flat = [rell(fam, ones(max_id + 1)) for fam in fams]
    fit = {"O_R": float(O_R), "x_root": float(x[max_id]), "max_id": int(max_id),
           "sum_rll": float(sum(r["rll"] for r in results)), "ll0": float(ll0),
           "delta_ll": float(optimizer.max["target"]),
           "n_families": len(fams), "n_read_errors": len(errors), "read_errors": errors,
           "n_p_gt_0.95": int(sum(r["p"][max_id] > 0.95 for r in results)),
           "bayes_opt_version": bayes_opt_version(),
           "evaluations": [[float(r["params"]["O_R"]), float(r["target"])] for r in optimizer.res],
           "settings": {"pbounds": [1, 20], "init_points": init_points, "n_iter": n_iter,
                        "random_state": random_state}}
    return fams, fit, results, flat


# ---------------------------------------------------------------- ALE runs
def write_species_tree(sim, out):
    """ALE parses internal labels of S as bootstrap values, so write leaf names and lengths only."""
    t = Tree(os.path.join(sim, "sample", "species_tree.nwk"), format=1)
    with open(os.path.join(out, S_NAME), "w") as f:
        f.write(t.write(format=5) + "\n")


def run_family(fam, tree_src, out, samples, seed, nice):
    """ALEobserve + ALEml_undated for one family in out/fams/<fam>/. Returns (fam, status, secs)."""
    wait_for_memory()
    t0 = time.time()
    final = os.path.join(out, "uml_rec", "%s_%s%s.ale.uml_rec" % (S_NAME, PREFIX, fam))
    if os.path.exists(final):
        return fam, "done", 0.0
    wd = os.path.join(out, "fams", fam)
    os.makedirs(wd, exist_ok=True)
    base = PREFIX + fam
    shutil.copyfile(tree_src, os.path.join(wd, base))
    logf = os.path.join(wd, "ale.log")
    with open(logf, "w") as lf:
        p = subprocess.run(nice + [os.path.join(ALE_BIN, "ALEobserve"), base], cwd=wd, stdout=lf, stderr=subprocess.STDOUT)
        if p.returncode != 0 or not os.path.exists(os.path.join(wd, base + ".ale")):
            return fam, "ALEobserve_failed", time.time() - t0
        cmd = nice + [os.path.join(ALE_BIN, "ALEml_undated"), os.path.join("..", "..", S_NAME), base + ".ale",
                      "sample=%d" % samples, "seed=%d" % seed, "separators=_"]
        lf.write("\n# " + " ".join(cmd) + "\n")
        lf.flush()
        p = subprocess.run(cmd, cwd=wd, stdout=lf, stderr=subprocess.STDOUT)
    rec = os.path.join(wd, "%s_%s.ale.uml_rec" % (S_NAME, base))
    if p.returncode != 0 or not os.path.exists(rec):
        return fam, "ALEml_undated_failed", time.time() - t0
    if any("Error" in l for l in open(rec)):
        return fam, "uml_rec_has_Error", time.time() - t0
    os.remove(os.path.join(wd, base))              # the copied tree sample; .ale is kept
    shutil.copyfile(rec, final + ".tmp")
    os.replace(final + ".tmp", final)
    return fam, "ok", time.time() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--trees", choices=["inferred", "true"], required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--samples", type=int, default=100, help="ALEml_undated sample= (default 100, ALE's default)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-fams", type=int, default=0, help="smoke only: first N reconcilable families")
    ap.add_argument("--reweight-only", action="store_true", help="skip ALE; reweight existing uml_rec files")
    ap.add_argument("--no-nice", action="store_true")
    a = ap.parse_args()
    sim = os.path.abspath(a.simdir)
    out = os.path.join(sim, "ale_" + a.trees)
    os.makedirs(os.path.join(out, "uml_rec"), exist_ok=True)
    nice = [] if a.no_nice else (["taskpolicy", "-b", "nice", "-n", "20"] if shutil.which("taskpolicy") else ["nice", "-n", "20"])
    t_start = time.time()

    truth = read_tsv(os.path.join(sim, "sample", "truth.tsv"))
    ngenes = {r["family"]: int(r["n_genes"]) for r in truth}
    todo = []
    for r in truth:
        f = r["family"]
        if ngenes[f] < 2:
            continue
        src = (os.path.join(sim, "inferred", "trees", f + ".trees") if a.trees == "inferred"
               else os.path.join(sim, "sample", "true_trees", f + ".nwk"))
        if not os.path.exists(src):
            raise SystemExit("missing tree file for family %s: %s" % (f, src))
        todo.append((f, src))
    if a.max_fams:
        todo = todo[:a.max_fams]

    status = {}
    if not a.reweight_only:
        write_species_tree(sim, out)
        log("ALE on %d families, %d workers, trees=%s" % (len(todo), a.workers, a.trees))
        secs = {}
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(run_family, f, src, out, a.samples, a.seed, nice) for f, src in todo]
            for i, fu in enumerate(as_completed(futs), 1):
                f, st, s = fu.result()
                status[f], secs[f] = st, s
                if st not in ("ok", "done"):
                    log("family %s: %s (see %s)" % (f, st, os.path.join(out, "fams", f, "ale.log")))
                if i % 50 == 0:
                    log("  %d/%d" % (i, len(todo)))
        t_ale = time.time() - t_start
        update_timings(sim, "ale_%s" % a.trees, t_ale)
    else:
        t_ale = 0.0
        secs = {}

    # Step 2: Moody's reweighting over every uml_rec present
    t1 = time.time()
    lookin = os.path.join(out, "uml_rec")
    ns = load_moody()
    fams, fit, results, flat = fit_global_or(lookin, ns)
    max_id = fit["max_id"]
    root_checks = [check_root_is_max_id(os.path.join(lookin, f), max_id)
                   for f in sorted(os.listdir(lookin)) if ".uml_rec" in f]
    bad = [msg for ok, msg in root_checks if not ok]
    if bad:
        raise SystemExit("max_id is not the root of S: %s" % bad[0])
    fit["root_check"] = "max_id %d is the root of S in all %d uml_rec files (%s)" % (max_id, len(root_checks), root_checks[0][1])
    by_fam = {}
    for fam, r, r0 in zip(fams, results, flat):
        assert r["fam"] == fam["fam"] == r0["fam"]
        by_fam[fam["fam"]] = (float(r["p"][max_id]), float(r0["p"][max_id]), int(fam["ML_e"]))
    with open(os.path.join(out, "root_pp.tsv"), "w") as fh:
        fh.write("family\tpp\tpp_flat\tml_e\tn_genes\tstatus\n")
        for r in truth:
            f = r["family"]
            if f in by_fam:
                pp, pp0, mle = by_fam[f]
                st = "ok"
            else:
                pp, pp0, mle = 0.0, 0.0, -1
                st = "single_gene" if ngenes[f] < 2 else status.get(f, "not_run")
            fh.write("%s\t%.6g\t%.6g\t%d\t%d\t%s\n" % (f, pp, pp0, mle, ngenes[f], st))
    t_rw = time.time() - t1
    write_json(os.path.join(out, "or_fit.json"), fit)
    failed = sorted(f for f, st in status.items() if st not in ("ok", "done"))
    write_json(os.path.join(out, "run_meta.json"), {
        "trees": a.trees, "workers": a.workers, "samples": a.samples, "seed": a.seed,
        "ale_bin": ALE_BIN, "moody_script_sha256": MOODY_SHA256, "n_reconcilable": len(todo),
        "n_single_gene": sum(1 for v in ngenes.values() if v < 2), "failed": failed,
        "seconds_ale": round(t_ale, 1), "seconds_reweight": round(t_rw, 1),
        "family_seconds": {k: round(v, 2) for k, v in secs.items()}})
    log("O_R %.4f (x_root %.4g), %d families, %d with p>0.95; reweight %.1fs" %
        (fit["O_R"], fit["x_root"], fit["n_families"], fit["n_p_gt_0.95"], t_rw))
    if failed:
        log("%d families failed in ALE: %s" % (len(failed), ",".join(failed[:20])))
        sys.exit(3)


if __name__ == "__main__":
    main()
