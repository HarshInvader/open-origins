"""Extract prereg v2/v4 real-data feature tables, B1/B2 baselines, and root-PP
decompositions for Moody et al. 2024 (E_M = 1,290.6) and Huang et al. 2026 (E_H = 1,331.0).

Pure Python stdlib (no external dependencies). Leaves pipeline/ untouched.
Outputs:
  - real_features_moody.tsv
  - real_features_huang.tsv
  - real_baselines_summary.json
"""
import collections
import glob
import gzip
import json
import math
import os
import statistics

ROOT = os.path.dirname(os.path.abspath(__file__))
MDIR = os.path.join(ROOT, "raw/moody/Supp_data")
KDIR = os.path.join(ROOT, "raw/moody/COG_OR_reconciliation")
HDIR = os.path.join(ROOT, "raw/huang/4_Ancestral_reconstruction/Euryarchaeota_root")


def logit(p):
    p = min(max(p, 1e-6), 1.0 - 1e-6)
    return math.log(p / (1.0 - p))


def parse_newick(s):
    s = s.rstrip(";").strip()

    def helper(i):
        node = {"name": "", "children": []}
        if s[i] == "(":
            i += 1
            while True:
                ch, i = helper(i)
                node["children"].append(ch)
                if s[i] == ",":
                    i += 1
                elif s[i] == ")":
                    i += 1
                    break
        j = i
        while j < len(s) and s[j] not in ",):":
            j += 1
        node["name"] = s[i:j].strip()
        i = j
        if i < len(s) and s[i] == ":":
            i += 1
            while i < len(s) and s[i] not in ",)":
                i += 1
        return node, i

    root, _ = helper(0)
    return root


def get_leaves(node):
    if not node["children"]:
        return [node["name"]]
    out = []
    for c in node["children"]:
        out.extend(get_leaves(c))
    return out


def find_node(node, name):
    if node["name"] == name:
        return node
    for c in node["children"]:
        r = find_node(c, name)
        if r:
            return r
    return None


def main():
    # ===================== 1. MOODY ET AL. 2024 =====================
    tax_dom, tax_phy = {}, {}
    with open(os.path.join(MDIR, "Taxonomy/ArcBacEuk_names.csv")) as f:
        for line in f.read().splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            k, t = parts[0], parts[1]
            dom = t.split("_")[0]
            tax_dom[k] = dom
            if dom == "Bacteria":
                phy = t[len("Bacteria_"):].split("-", 1)[0]
            elif dom == "Archaea":
                sp = t.split("_")
                phy = sp[2] if len(sp) > 2 else "none"
            else:
                phy = "other"
            tax_phy[k] = phy

    copies = collections.defaultdict(dict)
    for fp in sorted(glob.glob(os.path.join(MDIR, "Gene_Fastas/Pure_sequences/K*.fasta"))):
        k = os.path.basename(fp).split(".")[0]
        with open(fp) as f:
            for line in f:
                if line.startswith(">"):
                    g = line[1:].split("-", 1)[0].strip()
                    copies[k][g] = copies[k].get(g, 0) + 1

    genomes = sorted({g for c in copies.values() for g in c})
    A = [g for g in genomes if tax_dom.get(g) == "Archaea"]
    B = [g for g in genomes if tax_dom.get(g) == "Bacteria"]
    setA, setB = set(A), set(B)

    phyA = collections.defaultdict(list)
    for g in A:
        if tax_phy.get(g, "none") != "none":
            phyA[tax_phy[g]].append(g)
    phyB = collections.defaultdict(list)
    for g in B:
        if tax_phy.get(g, "none") != "none":
            phyB[tax_phy[g]].append(g)
    phyA_ge3 = {k: v for k, v in phyA.items() if len(v) >= 3}
    phyB_ge3 = {k: v for k, v in phyB.items() if len(v) >= 3}

    runs = []
    for i in range(1, 6):
        d = {}
        with open(os.path.join(KDIR, f"kegg{i}_cons.txt")) as f:
            for line in f:
                p = line.split()
                if len(p) >= 2:
                    d[p[0]] = float(p[1])
        runs.append(d)

    common = sorted(set.intersection(*(set(r.keys()) for r in runs)))
    pp_m = {k: statistics.median(r[k] for r in runs) for k in common}
    E_M = sum(pp_m.values())

    moody_out = os.path.join(ROOT, "real_features_moody.tsv")
    m_strata = collections.defaultdict(
        lambda: {"n": 0, "sum_pp": 0.0, "pp_ge_50": 0, "pp_ge_75": 0}
    )
    m_bins = collections.defaultdict(
        lambda: {"n": 0, "sum_pp": 0.0, "n_single_dom": 0, "n_b2": 0, "n_b1": 0}
    )
    b1_all_set, b1_ge3_set, b2_set, t75d_set, t50d_set = set(), set(), set(), set(), set()

    with open(moody_out, "w") as out:
        out.write(
            "family\tpp\tlogit_pp\toccA\toccB\tmin_occ\tlog_mean_copy\t"
            "n_genomes_A\tn_genomes_B\tb1\tb1_ge3\tb2\n"
        )
        for k in common:
            c = copies.get(k, {})
            nA = sum(1 for g in c if g in setA)
            nB = sum(1 for g in c if g in setB)
            oA = nA / len(A)
            oB = nB / len(B)
            mo = min(oA, oB)
            mc = sum(c.values()) / len(c) if c else 1.0
            lmc = math.log(mc)
            p = pp_m[k]
            b1 = int(
                sum(1 for t in phyA.values() if sum(g in c for g in t) >= 0.5 * len(t)) >= 4
                and sum(1 for t in phyB.values() if sum(g in c for g in t) >= 0.5 * len(t)) >= 4
            )
            b1_ge3 = int(
                sum(1 for t in phyA_ge3.values() if sum(g in c for g in t) >= 0.5 * len(t)) >= 4
                and sum(1 for t in phyB_ge3.values() if sum(g in c for g in t) >= 0.5 * len(t)) >= 4
            )
            b2 = int(oA > 0.01 and oB > 0.01)
            out.write(
                f"{k}\t{p:.8f}\t{logit(p):.6f}\t{oA:.6f}\t{oB:.6f}\t{mo:.6f}\t"
                f"{lmc:.6f}\t{nA}\t{nB}\t{b1}\t{b1_ge3}\t{b2}\n"
            )
            if b1:
                b1_all_set.add(k)
            if b1_ge3:
                b1_ge3_set.add(k)
            if b2:
                b2_set.add(k)
            if p >= 0.75 and b2:
                t75d_set.add(k)
            if p >= 0.50 and nA > 0 and nB > 0:
                t50d_set.add(k)
            if nA == 0 and nB == 0:
                st = "no_fasta"
            elif nA == 0:
                st = "bacteria_only"
            elif nB == 0:
                st = "archaea_only"
            elif not b2:
                st = "both_rare_le_1pct"
            else:
                st = "both_gt_1pct_B2"
            d = m_strata[st]
            d["n"] += 1
            d["sum_pp"] += p
            if p >= 0.5:
                d["pp_ge_50"] += 1
            if p >= 0.75:
                d["pp_ge_75"] += 1
            bidx = min(4, int(p * 5))
            bname = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"][bidx]
            bd = m_bins[bname]
            bd["n"] += 1
            bd["sum_pp"] += p
            if nA == 0 or nB == 0:
                bd["n_single_dom"] += 1
            if b2:
                bd["n_b2"] += 1
            if b1:
                bd["n_b1"] += 1

    print(f"=== MOODY E_M = {E_M:.2f} DECOMPOSITION (7,456 families) ===")
    for st in ["archaea_only", "bacteria_only", "both_rare_le_1pct", "both_gt_1pct_B2", "no_fasta"]:
        d = m_strata[st]
        pct = 100.0 * d["sum_pp"] / E_M
        print(
            f"  {st:20s}: n={d['n']:4d}, sum_PP={d['sum_pp']:7.1f} ({pct:5.1f}%), "
            f"PP>=0.5={d['pp_ge_50']:4d}, PP>=0.75={d['pp_ge_75']:3d}"
        )
    print("  PP bins:")
    for bname in ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]:
        bd = m_bins[bname]
        print(
            f"    {bname}: n={bd['n']:4d}, sum_PP={bd['sum_pp']:6.1f}, "
            f"single_dom={bd['n_single_dom']:4d}, B2={bd['n_b2']:4d}, B1={bd['n_b1']:3d}"
        )
    print(
        f"  Baselines: B1(all named phyla {len(phyA)}A/{len(phyB)}B)={len(b1_all_set)}, "
        f"B1(phyla>=3g {len(phyA_ge3)}A/{len(phyB_ge3)}B)={len(b1_ge3_set)}, "
        f"B2={len(b2_set)}, T75d(>1%)={len(t75d_set)}, T50d(>=1g)={len(t50d_set)}"
    )
    print(
        f"  Overlaps: B1∩T75d={len(b1_all_set & t75d_set)}, "
        f"B1(>=3g)∩T75d={len(b1_ge3_set & t75d_set)}, "
        f"B1∩T50d={len(b1_all_set & t50d_set)}"
    )

    # ===================== 2. HUANG ET AL. 2026 =====================
    nwk = open(os.path.join(HDIR, "species_trees/inferred_species_tree.newick")).read().strip()
    tree = parse_newick(nwk)
    root_name = tree["name"]
    childA, childB = tree["children"][0], tree["children"][1]
    leavesA = set(get_leaves(childA))
    leavesB = set(get_leaves(childB))
    dpann_node = find_node(tree, "DPANN")
    leaves_dpann = set(get_leaves(dpann_node))
    all_leaves = leavesA | leavesB
    leaves_nondpann = all_leaves - leaves_dpann
    print(
        f"\n=== HUANG TREE: root={root_name}, childA={childA['name']} ({len(leavesA)}), "
        f"childB={childB['name']} ({len(leavesB)}), total={len(all_leaves)}, DPANN={len(leaves_dpann)} ==="
    )

    h_root_pp = {}
    h_leaf_copies = collections.defaultdict(dict)
    all_h_fams = set()
    with gzip.open(
        os.path.join(HDIR, "reconciliations/perspecies_eventcount_per_family_summary.tsv.gz"), "rt"
    ) as f:
        hdr = f.readline().rstrip("\n").split("\t")
        idx_sp = hdr.index("species_label")
        idx_pr = hdr.index("presence")
        idx_cp = hdr.index("copies")
        idx_fm = hdr.index("Family")
        for line in f:
            p = line.rstrip("\n").split("\t")
            sp = p[idx_sp]
            fm = p[idx_fm]
            all_h_fams.add(fm)
            if sp == root_name:
                h_root_pp[fm] = float(p[idx_pr])
            elif sp in all_leaves:
                cp = float(p[idx_cp])
                if cp > 0:
                    h_leaf_copies[fm][sp] = cp

    huang_out = os.path.join(ROOT, "real_features_huang.tsv")
    h_fams = sorted(h_root_pp.keys())
    E_H = sum(h_root_pp.values())
    h_strata = collections.defaultdict(
        lambda: {"n": 0, "sum_pp": 0.0, "pp_ge_50": 0, "pp_ge_75": 0}
    )
    h_bins = collections.defaultdict(
        lambda: {"n": 0, "sum_pp": 0.0, "n_single_child": 0, "occ_dpann": [], "occ_nondpann": []}
    )

    with open(huang_out, "w") as out:
        out.write(
            "family\tpp\tlogit_pp\toccA\toccB\tmin_occ\tlog_mean_copy\t"
            "n_genomes_A\tn_genomes_B\tocc_dpann\tocc_nondpann\n"
        )
        for fm in h_fams:
            c = h_leaf_copies.get(fm, {})
            nA = sum(1 for g in c if g in leavesA)
            nB = sum(1 for g in c if g in leavesB)
            oA = nA / len(leavesA)
            oB = nB / len(leavesB)
            mo = min(oA, oB)
            mc = sum(c.values()) / len(c) if c else 1.0
            lmc = math.log(mc)
            od = sum(1 for g in c if g in leaves_dpann) / len(leaves_dpann)
            ond = sum(1 for g in c if g in leaves_nondpann) / len(leaves_nondpann)
            p = h_root_pp[fm]
            out.write(
                f"{fm}\t{p:.8f}\t{logit(p):.6f}\t{oA:.6f}\t{oB:.6f}\t{mo:.6f}\t"
                f"{lmc:.6f}\t{nA}\t{nB}\t{od:.6f}\t{ond:.6f}\n"
            )
            if nA == 0 and nB == 0:
                st = "no_leaves"
            elif nA == 0:
                st = "childB_only"
            elif nB == 0:
                st = "childA_only"
            elif not (oA > 0.01 and oB > 0.01):
                st = "both_rare_le_1pct"
            else:
                st = "both_gt_1pct"
            d = h_strata[st]
            d["n"] += 1
            d["sum_pp"] += p
            if p >= 0.5:
                d["pp_ge_50"] += 1
            if p >= 0.75:
                d["pp_ge_75"] += 1
            bidx = min(4, int(p * 5))
            bname = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"][bidx]
            bd = h_bins[bname]
            bd["n"] += 1
            bd["sum_pp"] += p
            if nA == 0 or nB == 0:
                bd["n_single_child"] += 1
            bd["occ_dpann"].append(od)
            bd["occ_nondpann"].append(ond)

    print(f"Huang families: total_in_tsv={len(all_h_fams)}, with_root_row={len(h_fams)}, E_H={E_H:.2f}")
    for st in ["childA_only", "childB_only", "both_rare_le_1pct", "both_gt_1pct", "no_leaves"]:
        d = h_strata[st]
        pct = 100.0 * d["sum_pp"] / E_H
        print(
            f"  {st:20s}: n={d['n']:4d}, sum_PP={d['sum_pp']:7.1f} ({pct:5.1f}%), "
            f"PP>=0.5={d['pp_ge_50']:4d}, PP>=0.75={d['pp_ge_75']:3d}"
        )
    print("  PP bins:")
    for bname in ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]:
        bd = h_bins[bname]
        md = sum(bd["occ_dpann"]) / max(1, len(bd["occ_dpann"]))
        mnd = sum(bd["occ_nondpann"]) / max(1, len(bd["occ_nondpann"]))
        print(
            f"    {bname}: n={bd['n']:4d}, sum_PP={bd['sum_pp']:6.1f}, "
            f"single_child={bd['n_single_child']:4d}, mean_occ_DPANN={md:.3f}, mean_occ_nonDPANN={mnd:.3f}"
        )

    summary = {
        "moody": {
            "n_genomes": len(genomes),
            "n_archaea": len(A),
            "n_bacteria": len(B),
            "n_archaea_phyla_named": len(phyA),
            "n_bacteria_phyla_named": len(phyB),
            "n_archaea_phyla_ge3": len(phyA_ge3),
            "n_bacteria_phyla_ge3": len(phyB_ge3),
            "n_common_families": len(common),
            "E_M": round(E_M, 2),
            "baselines_on_7456": {
                "B1_all_named_phyla": len(b1_all_set),
                "B1_phyla_ge3": len(b1_ge3_set),
                "B2_gt_1pct_both": len(b2_set),
                "T75d_gt_1pct_both": len(t75d_set),
                "T50d_ge_1g_both": len(t50d_set),
                "overlap_B1_T75d": len(b1_all_set & t75d_set),
                "overlap_B1ge3_T75d": len(b1_ge3_set & t75d_set),
                "overlap_B1_T50d": len(b1_all_set & t50d_set),
            },
            "E_M_strata": {
                k: {
                    "n": v["n"],
                    "sum_pp": round(v["sum_pp"], 2),
                    "share_of_E_M": round(v["sum_pp"] / E_M, 4),
                    "pp_ge_50": v["pp_ge_50"],
                    "pp_ge_75": v["pp_ge_75"],
                }
                for k, v in m_strata.items()
            },
            "pp_bins": {
                k: {
                    "n": v["n"],
                    "sum_pp": round(v["sum_pp"], 2),
                    "n_single_dom": v["n_single_dom"],
                    "n_b2": v["n_b2"],
                    "n_b1": v["n_b1"],
                }
                for k, v in m_bins.items()
            },
        },
        "huang": {
            "root_node": root_name,
            "childA": childA["name"],
            "n_childA": len(leavesA),
            "childB": childB["name"],
            "n_childB": len(leavesB),
            "n_dpann": len(leaves_dpann),
            "n_total_families_in_tsv": len(all_h_fams),
            "n_root_row_families": len(h_fams),
            "E_H": round(E_H, 2),
            "E_H_strata": {
                k: {
                    "n": v["n"],
                    "sum_pp": round(v["sum_pp"], 2),
                    "share_of_E_H": round(v["sum_pp"] / E_H, 4),
                    "pp_ge_50": v["pp_ge_50"],
                    "pp_ge_75": v["pp_ge_75"],
                }
                for k, v in h_strata.items()
            },
            "pp_bins": {
                k: {
                    "n": v["n"],
                    "sum_pp": round(v["sum_pp"], 2),
                    "n_single_child": v["n_single_child"],
                    "mean_occ_dpann": round(
                        sum(v["occ_dpann"]) / max(1, len(v["occ_dpann"])), 4
                    ),
                    "mean_occ_nondpann": round(
                        sum(v["occ_nondpann"]) / max(1, len(v["occ_nondpann"])), 4
                    ),
                }
                for k, v in h_bins.items()
            },
        },
    }
    with open(os.path.join(ROOT, "real_baselines_summary.json"), "w") as out:
        json.dump(summary, out, indent=2)
    print("\nWrote real_features_moody.tsv, real_features_huang.tsv, real_baselines_summary.json")


if __name__ == "__main__":
    main()
