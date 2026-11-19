"""Reconciliation H: Huang et al. 2026's AleRax set-up, as far as their methods state it (prereg v4 B).

Usage:
    python run_alerax_h.py <simdir> [--trees inferred|true] [--np 4] [--samples 100] [--seed 1] [--max-fams N]

AleRax 1.4.0 with a clade-wise parametrisation file (AleRax "--model-parametrization <filepath>"; format
read from AleRax v1.4.0 src/ale/OptimizationClasses.cpp: one line per species-tree node label followed by
the parameter letters, e.g. "n12 DTLO"; the node and its whole subtree get their own class for those
parameters unless a deeper listed node overrides it; the root always has its own class):
    <root child A> DTLO
    <root child B> DTLO
    <fast clade>   DTLO
so D, T, L and origination O each have 4 classes: the root node, child A's subtree, child B's subtree
outside the clade, and the clade's subtree (16 free parameters). This is the v4 "separate rate sets for the
two root children and for the fast-loss clade" with "origination optimised separately for the root, its
two children and the clade". The fast clade is the one Zombi Gu used (sim_summary.json) in arm-L
simulations, else clades.fast_clade on domain B's sampled tips with the simulation's seed (no rate change).
Other options: --rec-model UndatedDTL, --origination OPTIMIZE, --species-tree-search SKIP (species tree
fixed), no --fraction-missing-file (fraction missing 0), --gene-tree-samples 100, --min-covered-species 1,
inferred UFBoot tree samples (1,000 trees per family).

Root PP: AleRax's per-species "presence" at the species-tree root, i.e. the mean over the sampled
reconciliations, as in Huang's perspecies_eventcount_per_family_summary (run_alerax.py computes it from the
samples and checks it against reconciliations/summaries/*_meanSpeciesEventCounts.txt "presence").

Known differences from Huang et al. (logged in <run>/h_meta.json):
  - AleRax 1.4.0 here, v1.1.1 there.
  - 4 rate classes here; their 72-parameter DTL_br2 model has 24 clade classes for DTL.
  - Fraction missing 0 here (complete simulated genomes); CheckM2 completeness there.
  - Families with < 3 genes get PP 0 here (AleRax 1.4.0 aborts on 2-leaf trees).
  - Number of sampled reconciliations, transfer constraint and other defaults: not stated in their
    methods or deposited scripts; AleRax 1.4.0 defaults are used.
Output: <simdir>/alerax_H_<trees>/root_pp.tsv (same columns as run_alerax.py), h_meta.json.
"""
import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, read_tsv, write_json
from ete3 import Tree
import clades

DIFFERENCES = [
    "AleRax 1.4.0 (Huang: v1.1.1)",
    "4 rate classes (root, child A, child B, fast clade) for D, T, L and O; Huang's 72-parameter model has 24 DTL classes",
    "fraction missing 0 (Huang: CheckM2 completeness)",
    "families with < 3 sampled genes not reconciled (AleRax 1.4.0 aborts on 2-leaf trees), PP 0",
    "gene-tree samples 100 and other AleRax defaults: not stated by Huang",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("simdir")
    ap.add_argument("--trees", choices=["inferred", "true"], default="inferred")
    ap.add_argument("--np", type=int, default=1)
    ap.add_argument("--samples", type=int, default=100)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-fams", type=int, default=0)
    a = ap.parse_args()
    sim = os.path.abspath(a.simdir)
    sp = Tree(open(os.path.join(sim, "sample", "species_tree.nwk")).readline().strip(), format=1)
    ca, cb = [c.name for c in sp.get_tree_root().get_children()]
    summ = json.load(open(os.path.join(sim, "sim_summary.json")))
    cfg = json.load(open(os.path.join(sim, "config.json")))
    clade = summ.get("genome_model", {}).get("fast_clade")
    source = "Zombi Gu arm L"
    if not clade:
        dom = {r["species"]: r["domain"] for r in read_tsv(os.path.join(sim, "sample", "domains.tsv"))}
        clade, info = clades.fast_clade(sp, [k for k, v in dom.items() if v == "B"], cfg["seed"])
        source = "clades.fast_clade (no rate change) %s" % json.dumps(info)
    name = "alerax_H_%s" % a.trees
    rdir = os.path.join(sim, name)
    pfile = os.path.join(sim, "alerax_H_parametrization_%s.txt" % a.trees)
    with open(pfile, "w") as f:
        for lab in (ca, cb, clade):
            f.write("%s DTLO\n" % lab)
    cmd = [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_alerax.py"), sim,
           "--trees", a.trees, "--origination", "OPTIMIZE", "--parametrization", pfile, "--name", name,
           "--samples", str(a.samples), "--seed", str(a.seed), "--np", str(a.np)]
    if a.max_fams:
        cmd += ["--max-fams", str(a.max_fams)]
    log("H: classes root | %s | %s | clade %s (%s)" % (ca, cb, clade, source))
    p = subprocess.run(cmd)
    if p.returncode != 0:
        sys.exit(p.returncode)
    meta = json.load(open(os.path.join(rdir, "run_meta.json")))
    if meta["summary_mismatches"]:
        sys.exit("per-sample root presence disagrees with AleRax's summary presence: %s" % meta["summary_mismatches"][:5])
    write_json(os.path.join(rdir, "h_meta.json"), {
        "classes": {"root_child_A": ca, "root_child_B": cb, "fast_clade": clade, "clade_source": source},
        "parametrization_file": open(pfile).read(), "differences_from_huang": DIFFERENCES,
        "pp_definition": "AleRax per-species presence at the species-tree root (mean over sampled reconciliations)"})
    os.replace(pfile, os.path.join(rdir, "parametrization.txt"))


if __name__ == "__main__":
    main()
