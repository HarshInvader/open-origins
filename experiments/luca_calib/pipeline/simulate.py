"""Simulate one planted-LUCA dataset with Zombi (T -> Ti -> Gm -> Su), then sample, prune and write the truth.

Usage:
    python simulate.py <outdir> <config.json> [--set section.key=value ...]

Every rate, size and count comes from the config (defaults below) or a --set override.
Zombi is called unmodified from ext/zombi; this script only writes its parameter and CustomRates files.

Steps
 1. Zombi T (birth-death). If either subtree under the extant root has fewer than
    sampling.n_per_domain tips, the T seed is incremented (prereg: "the next seed is used").
 2. The complete tree (stem and extinct lineages included) is rescaled so the extant-tree root,
    which is the MRCA of any sample with both domains, is species_tree.tree_height before the present,
    and fed back to Zombi Ti, which rebuilds Events.tsv.
    Zombi's own SCALE_TREE only writes side files that G mode does not read, hence Ti.
 3. Zombi Gm: per-family D/T/L rates drawn by Zombi from the distributions we write
    (f:x when genome.family_rate_sigma == 0, else l:mu;sigma with mean equal to the rate).
 4. Zombi Su with CustomRates/{ST,GT}_Substitution_rates.tsv written here (lognormal, seeded).
 5. Sample n_per_domain extant tips per domain; write species tree, pruned true gene trees,
    FASTA, AleRax mapping files, copy-number matrix and truth (MRCA genome, cross-checked
    against the per-family event files).
"""
import argparse
import copy
import json
import math
import os
import shutil
import sys
import time

import numpy as np
from ete3 import Tree

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ZOMBI_DIR, PHYLO_PY, log, run, read_fasta, write_fasta, gene_species,
                    write_json, update_timings)

DEFAULTS = {
    "seed": 1,
    "species_tree": {
        "speciation": 1.0,
        "extinction": 0.5,
        "total_lineages": 600,      # Zombi STOPPING_RULE 1: stop when this many lineages are alive
        "max_lineages": 100000,
        "tree_height": 1.0,         # extant-tree root (the sampled MRCA, "LUCA") to present, after rescaling
        "max_seed_tries": 50,
    },
    "sampling": {"n_per_domain": 60},
    "genome": {
        "initial_genome_size": 1000,
        "duplication": 0.2,
        "transfer": 0.3,
        "loss": 1.0,
        "origination": 0.0,          # per lineage per unit time (genome-wide in Zombi)
        "family_rate_sigma": 0.0,    # lognormal sigma of per-family D/T/L (0 = all families share the rate)
        "replacement_transfer": 0.0,
        "min_genome_size": 10,       # Zombi ignores losses in genomes below this size
        "inversion": 0.0,
        "transposition": 0.0,
        "duplication_extension": "g:1",
        "transfer_extension": "g:1",
        "loss_extension": "g:1",
    },
    "sequence": {
        "aa_model": "WAG",           # Zombi's default AA_MODEL; one of JTT WAG LG DAYHOFF MTMAM MTREV24
        "sequence_size": 300,
        "target_root_to_tip": 2.0,   # expected subs/site from the sampled MRCA to a tip (mean multipliers)
        "lineage_sigma": 0.5,
        "family_sigma": 0.5,
        "multiplier_mean_one": True,  # lognormal mu = -sigma^2/2 so E[multiplier] = 1
    },
}


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d


def parse_value(s):
    try:
        return json.loads(s)
    except ValueError:
        return s


def load_config(path, sets):
    cfg = copy.deepcopy(DEFAULTS)
    if path:
        deep_update(cfg, json.load(open(path)))
    for s in sets or []:
        key, val = s.split("=", 1)
        parts = key.split(".")
        d = cfg
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = parse_value(val)
    return cfg


def write_params(path, items):
    with open(path, "w") as f:
        for k, v in items:
            f.write("%s\t%s\n" % (k, v))


def zombi(mode, params, expdir, logfile):
    return run([PHYLO_PY, os.path.join(ZOMBI_DIR, "Zombi.py"), mode, params, expdir],
               cwd=ZOMBI_DIR, logfile=logfile)


def rate_spec(rate, sigma):
    if rate <= 0:
        return "f:0"
    if sigma <= 0:
        return "f:%r" % float(rate)
    return "l:%r;%r" % (math.log(rate) - sigma ** 2 / 2.0, float(sigma))


def read_tree(path):
    return Tree(open(path).readline().strip(), format=1)


def domains_of(extant_tree):
    root = extant_tree.get_tree_root()
    c = root.get_children()
    if len(c) != 2:
        raise RuntimeError("extant root is not binary")
    return root.name, [sorted(x.get_leaf_names()) for x in c], [x.name for x in c]


# ----------------------------------------------------------------------------------------------
def step_species_tree(cfg, out, logs):
    st = cfg["species_tree"]
    n_dom = cfg["sampling"]["n_per_domain"]
    pdir = os.path.join(out, "params")
    raw = os.path.join(out, "zombi_T_raw")
    seed = cfg["seed"]
    for attempt in range(st["max_seed_tries"]):
        tseed = seed + attempt
        params = os.path.join(pdir, "SpeciesTreeParameters.tsv")
        write_params(params, [
            ("SPECIATION", "f:%r" % float(st["speciation"])),
            ("EXTINCTION", "f:%r" % float(st["extinction"])),
            ("STOPPING_RULE", 1), ("TOTAL_TIME", 1), ("TOTAL_LINEAGES", st["total_lineages"]),
            ("MIN_LINEAGES", 1), ("MAX_LINEAGES", st["max_lineages"]), ("VERBOSE", 0),
            ("SCALE_TREE", 0), ("SEED", tseed)])
        if os.path.isdir(raw):
            shutil.rmtree(raw)
        zombi("T", params, raw, os.path.join(logs, "zombi_T.log"))
        ext = read_tree(os.path.join(raw, "T", "ExtantTree.nwk"))
        _, doms, _ = domains_of(ext)
        sizes = [len(d) for d in doms]
        log("T seed %d: extant %d, domain sizes %s" % (tseed, len(ext), sizes))
        if min(sizes) >= n_dom:
            break
    else:
        raise RuntimeError("no T seed gave >= %d tips per domain" % n_dom)

    # Rescale the complete tree (stem and dead lineages included) by one factor.
    comp = read_tree(os.path.join(raw, "T", "CompleteTree.nwk"))
    comp_root_dist = float(open(os.path.join(raw, "T", "CompleteTree.nwk")).read().strip().rstrip(";").split(":")[-1])
    # height = crown of the extant tree (extant root = MRCA of any two-domain sample -> present)
    height = max(ext.get_distance(l) for l in ext.get_leaves())
    f = st["tree_height"] / height
    for n in comp.traverse():
        n.dist = n.dist * f
    comp.name = "Root"
    comp.dist = comp_root_dist * f
    nwk = comp.write(format=1, format_root_node=True)  # ends with ")Root:<stem>;" (Ti reads the stem from it)
    scaled = os.path.join(pdir, "CompleteTree_scaled.nwk")
    with open(scaled, "w") as fh:
        fh.write(nwk + "\n")
    zdir = os.path.join(out, "zombi")
    zombi("Ti", scaled, zdir, os.path.join(logs, "zombi_Ti.log"))
    ext2 = read_tree(os.path.join(zdir, "T", "ExtantTree.nwk"))
    if sorted(ext2.get_leaf_names()) != sorted(ext.get_leaf_names()) or \
            ext2.robinson_foulds(ext, unrooted_trees=False)[0] != 0:
        raise RuntimeError("Ti rebuild changed the extant tree")
    return {"t_seed": tseed, "raw_height": height, "scale_factor": f, "stem_length": comp_root_dist * f,
            "n_extant": len(ext), "n_complete_leaves": len(comp)}


def step_genomes(cfg, out, logs):
    g = cfg["genome"]
    s = g["family_rate_sigma"]
    params = os.path.join(out, "params", "GenomeParameters.tsv")
    write_params(params, [
        ("DUPLICATION", rate_spec(g["duplication"], s)),
        ("TRANSFER", rate_spec(g["transfer"], s)),
        ("LOSS", rate_spec(g["loss"], s)),
        ("INVERSION", "f:%r" % float(g["inversion"])),
        ("TRANSPOSITION", "f:%r" % float(g["transposition"])),
        ("ORIGINATION", "f:%r" % float(g["origination"])),
        ("DUPLICATION_EXTENSION", g["duplication_extension"]),
        ("TRANSFER_EXTENSION", g["transfer_extension"]),
        ("LOSS_EXTENSION", g["loss_extension"]),
        ("INVERSION_EXTENSION", "g:1"), ("TRANSPOSITION_EXTENSION", "g:1"),
        ("REPLACEMENT_TRANSFER", g["replacement_transfer"]),
        ("ASSORTATIVE_TRANSFER", "False"), ("ALPHA", 100),
        ("INITIAL_GENOME_SIZE", g["initial_genome_size"]),
        ("MIN_GENOME_SIZE", g["min_genome_size"]),
        ("EVENTS_PER_BRANCH", 0), ("PROFILES", 1), ("GENE_TREES", 1), ("RECONCILED_TREES", 0),
        ("VERBOSE", 0), ("SCALE_TREE", 0),
        ("GENE_LENGTH", "f:100"), ("INTERGENE_LENGTH", 100), ("PSEUDOGENIZATION", 0.5),
        ("RATE_FILE", "False"), ("SCALE_RATES", "False"),
        ("SEED", cfg["seed"])])
    zombi("Gm", params, os.path.join(out, "zombi"), os.path.join(logs, "zombi_Gm.log"))


def step_sequences(cfg, out, logs, mrca, sampled):
    sq = cfg["sequence"]
    zdir = os.path.join(out, "zombi")
    rng = np.random.default_rng(cfg["seed"] + 7919)
    crdir = os.path.join(zdir, "CustomRates")
    os.makedirs(crdir, exist_ok=True)

    def draw(sigma):
        if sigma <= 0:
            return 1.0
        mu = -sigma ** 2 / 2.0 if sq["multiplier_mean_one"] else 0.0
        return float(rng.lognormal(mu, sigma))

    comp = read_tree(os.path.join(zdir, "T", "CompleteTree.nwk"))
    comp.get_tree_root().name = "Root"
    st_mult = {}
    for n in comp.traverse("preorder"):
        st_mult[n.name] = draw(sq["lineage_sigma"])
    with open(os.path.join(crdir, "ST_Substitution_rates.tsv"), "w") as f:
        f.write("lineage\tSUBSTITUTION_RATE_MULTIPLIER\n")
        for k, v in st_mult.items():
            f.write("%s\t%r\n" % (k, v))
    gtdir = os.path.join(zdir, "G", "Gene_trees")
    fams = sorted((x.split("_")[0] for x in os.listdir(gtdir) if "complete" in x), key=int)
    with open(os.path.join(crdir, "GT_Substitution_rates.tsv"), "w") as f:
        f.write("gene_family\tSUBSTITUTION_RATE_MULTIPLIER\n")
        for fam in fams:
            f.write("%s\t%r\n" % (fam, draw(sq["family_sigma"])))

    scaling = sq["target_root_to_tip"] / cfg["species_tree"]["tree_height"]
    params = os.path.join(out, "params", "SequenceParameters.tsv")
    write_params(params, [
        ("SCALING", repr(scaling)), ("SEQUENCE_SIZE", sq["sequence_size"]),
        ("SEQUENCE", "amino-acid"), ("AA_MODEL", sq["aa_model"]),
        ("CODON_MODEL", "MG"), ("ALPHA", 1.0), ("BETA", 0.5), ("KAPPA", 1.0),
        ("VERBOSE", 0), ("SEED", cfg["seed"])])
    zombi("Su", params, zdir, os.path.join(logs, "zombi_Su.log"))

    # realised mean MRCA->tip distance (lineage multipliers only; family multipliers have mean 1)
    m = comp & mrca
    rtt = []
    for leaf in sampled:
        node, d = comp & leaf, 0.0
        while node is not m:
            d += node.dist * st_mult[node.name]
            node = node.up
        rtt.append(d * scaling)
    return {"scaling": scaling, "mean_mrca_to_tip_subs": float(np.mean(rtt)),
            "mean_mrca_to_tip_time": float(np.mean([m.get_distance(comp & l) for l in sampled]))}


def read_genome(path):
    counts = {}
    with open(path) as f:
        f.readline()
        for line in f:
            h = line.rstrip("\n").split("\t")
            if len(h) >= 2:
                counts[h[1]] = counts.get(h[1], 0) + 1
    return counts


def mrca_copies_from_events(events_path, mrca):
    """Copies of the family at the MRCA's speciation = number of S events whose parent lineage is the MRCA."""
    n = 0
    with open(events_path) as f:
        f.readline()
        for line in f:
            h = line.rstrip("\n").split("\t")
            if len(h) == 3 and h[1] == "S" and h[2].split(";")[0] == mrca:
                n += 1
    return n


# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("outdir")
    ap.add_argument("config")
    ap.add_argument("--set", action="append", default=[], help="override, e.g. genome.transfer=1.0")
    ap.add_argument("--force", action="store_true", help="delete outdir first")
    a = ap.parse_args()

    cfg = load_config(a.config, a.set)
    out = os.path.abspath(a.outdir)
    if os.path.exists(out):
        if not a.force:
            sys.exit("%s exists (use --force)" % out)
        shutil.rmtree(out)
    for d in ["params", "logs", "sample", "sample/fasta", "sample/true_trees", "sample/mappings"]:
        os.makedirs(os.path.join(out, d), exist_ok=True)
    logs = os.path.join(out, "logs")
    write_json(os.path.join(out, "config.json"), cfg)
    summary = {}
    T0 = time.time()

    t = time.time()
    summary["species_tree"] = step_species_tree(cfg, out, logs)
    update_timings(out, "zombi_T_and_Ti", time.time() - t)

    zdir = os.path.join(out, "zombi")
    ext = read_tree(os.path.join(zdir, "T", "ExtantTree.nwk"))
    mrca, doms, dom_roots = domains_of(ext)
    rng = np.random.default_rng(cfg["seed"])
    n_dom = cfg["sampling"]["n_per_domain"]
    sampled_by_dom = [sorted(rng.choice(d, size=n_dom, replace=False).tolist(), key=lambda x: int(x[1:]))
                      for d in doms]
    sampled = sampled_by_dom[0] + sampled_by_dom[1]
    dom_of = {s: "A" for s in sampled_by_dom[0]}
    dom_of.update({s: "B" for s in sampled_by_dom[1]})
    sp = ext.copy()
    sp.prune(sampled, preserve_branch_length=True)
    if sp.get_tree_root().name != mrca:
        raise RuntimeError("sampled-tree root %s != extant root %s" % (sp.get_tree_root().name, mrca))
    with open(os.path.join(out, "sample", "species_tree.nwk"), "w") as f:
        f.write(sp.write(format=1, format_root_node=True) + "\n")
    with open(os.path.join(out, "sample", "domains.tsv"), "w") as f:
        f.write("species\tdomain\n")
        for s in sampled:
            f.write("%s\t%s\n" % (s, dom_of[s]))
    summary["sampling"] = {"mrca": mrca, "domain_roots": dom_roots, "domain_sizes": [len(d) for d in doms],
                           "n_sampled": len(sampled)}
    log("MRCA %s, domain roots %s, sampled %d" % (mrca, dom_roots, len(sampled)))

    t = time.time()
    step_genomes(cfg, out, logs)
    update_timings(out, "zombi_Gm", time.time() - t)
    log("Gm done in %.1fs" % (time.time() - t))

    t = time.time()
    summary["sequence"] = step_sequences(cfg, out, logs, mrca, sampled)
    update_timings(out, "zombi_Su", time.time() - t)
    log("Su done in %.1fs" % (time.time() - t))

    # ---- genomes of sampled species and the MRCA
    t = time.time()
    gdir = os.path.join(zdir, "G", "Genomes")
    genomes = {s: read_genome(os.path.join(gdir, s + "_GENOME.tsv")) for s in sampled}
    mrca_genome = read_genome(os.path.join(gdir, mrca + "_GENOME.tsv"))
    famdir = os.path.join(zdir, "G", "Gene_families")
    all_fams = sorted((x.split("_")[0] for x in os.listdir(famdir) if x.endswith("_events.tsv")), key=int)

    sset = set(sampled)
    rows, mismatches = [], []
    gtdir = os.path.join(zdir, "G", "Gene_trees")
    sdir = os.path.join(zdir, "S")
    n_written = 0
    for fam in all_fams:
        ev = mrca_copies_from_events(os.path.join(famdir, fam + "_events.tsv"), mrca)
        gn = mrca_genome.get(fam, 0)
        if ev != gn:
            mismatches.append((fam, gn, ev))
        cn = {s: genomes[s].get(fam, 0) for s in sampled}
        n_genes = sum(cn.values())
        if n_genes == 0 and gn == 0:
            continue
        nA = sum(1 for s in sampled_by_dom[0] if cn[s] > 0)
        nB = sum(1 for s in sampled_by_dom[1] if cn[s] > 0)
        rows.append((fam, gn, ev, int(gn > 0), n_genes, nA, nB))
        if n_genes == 0:
            continue
        # true gene tree pruned to sampled genes
        line = open(os.path.join(gtdir, fam + "_prunedtree.nwk")).readline().strip()
        if "(" in line:
            gt = Tree(line, format=1)
            keep = [l for l in gt.get_leaf_names() if gene_species(l) in sset]
        else:
            gt, keep = None, [line.rstrip(";")] if gene_species(line.rstrip(";")) in sset else []
        if len(keep) != n_genes:
            raise RuntimeError("family %s: %d sampled leaves in tree vs %d in genomes" % (fam, len(keep), n_genes))
        if n_genes >= 2:
            gt.prune(keep, preserve_branch_length=True)
            with open(os.path.join(out, "sample", "true_trees", fam + ".nwk"), "w") as f:
                f.write(gt.write(format=5) + "\n")
        with open(os.path.join(out, "sample", "mappings", fam + ".map"), "w") as f:
            for gname in sorted(keep):
                f.write("%s %s\n" % (gname, gene_species(gname)))
        seqs = {}
        pf = os.path.join(sdir, fam + "_pruned.fasta")
        if os.path.exists(pf):
            seqs = dict(read_fasta(pf))
        elif n_genes == 1:
            # Zombi Su does not simulate single-leaf complete trees; such families are never reconciled.
            seqs = {}
        missing = [k for k in keep if k not in seqs]
        if missing and n_genes >= 2:
            raise RuntimeError("family %s: %d sampled genes lack sequences" % (fam, len(missing)))
        if not missing:
            write_fasta(os.path.join(out, "sample", "fasta", fam + ".fasta"), [(k, seqs[k]) for k in sorted(keep)])
        n_written += 1

    if mismatches:
        raise RuntimeError("Zombi check failed: MRCA genome vs events differ for %d families, e.g. %s"
                           % (len(mismatches), mismatches[:5]))

    with open(os.path.join(out, "sample", "truth.tsv"), "w") as f:
        f.write("family\tmrca_copies_genome\tmrca_copies_events\tluca\tn_genes\tn_genomes_A\tn_genomes_B\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    present = [r[0] for r in rows if r[4] > 0]
    with open(os.path.join(out, "sample", "copy_numbers.tsv"), "w") as f:
        f.write("family\t" + "\t".join(sampled) + "\n")
        for fam in present:
            f.write(fam + "\t" + "\t".join(str(genomes[s].get(fam, 0)) for s in sampled) + "\n")
    update_timings(out, "sample_and_prune", time.time() - t)

    sizes = [len(genomes[s]) for s in sampled]
    luca = [r for r in rows if r[3]]
    summary["families"] = {
        "zombi_total": len(all_fams),
        "present_in_sample": len(present),
        "ge2_genes": sum(1 for r in rows if r[4] >= 2),
        "ge4_genes": sum(1 for r in rows if r[4] >= 4),
        "true_luca_size": len(luca),
        "true_luca_with_ge2_genes": sum(1 for r in luca if r[4] >= 2),
        "true_luca_absent_from_sample": sum(1 for r in luca if r[4] == 0),
        "mean_sampled_genome_families": float(np.mean(sizes)),
        "mean_sampled_genome_genes": float(np.mean([sum(genomes[s].values()) for s in sampled])),
        "zombi_event_check": "pass (%d families)" % len(all_fams),
    }
    summary["total_seconds"] = round(time.time() - T0, 2)
    write_json(os.path.join(out, "sim_summary.json"), summary)
    log(json.dumps(summary["families"]))


if __name__ == "__main__":
    main()
