"""One-off: add the papers read for T14 (autocatalytic tiers vs rewired networks) to the library (2026-11-25)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
TODAY = "2026-11-25"
T14 = "T14 (sealed, 2026-11-25, experiments/t14_autocatalytic_tiers/T14_RESULTS.md)"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "date": TODAY, "topic": "Vents and first cells", "touches": []}
    base.update(k); return base

new = [
 entry(id="peng-2022-hierarchical-autocatalytic-networks", relevance="core",
  title="The hierarchical organization of autocatalytic reaction networks and its relevance to the origin of life",
  authors="Peng Z, Linderoth J, Baum DA", year=2022, venue="PLoS Comput. Biol. 18:e1010498",
  doi="10.1371/journal.pcbi.1010498", url="https://doi.org/10.1371/journal.pcbi.1010498", read_depth="full",
  question="Do abiotic and biochemical reaction networks contain seed-dependent autocatalytic systems (SDASs), and are they organised in tiers?",
  tried="Expand an abiotic network (277 species, 717 reactions) and a KEGG-derived biochemical network (4,216 species, 8,402 reactions) from fixed food sets, find singleton seeds that induce self-maintaining sets, and compare the sets.",
  method_data="Network expansion plus a feasibility LP for self-maintenance; reaction tables and Python scripts in the supplement (CC BY).",
  key_results="Biochemical: 304 supported seeds in three cliques inducing nested SDASs of 301, 357 and 1,414 species. Abiotic: one SDAS of 91 species. 'the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs'.",
  limits="No randomised or rewired comparison; the abiotic network has a single SDAS, so it shows no nesting.",
  ideas_for_us=T14 + ": against 200+200 degree-preserving rewires (tier 0 fixed), the biochemical network's 3 nested sets are never matched (rewired: 1 set, nested share 0). Sealed verdict support. But rewired networks have 3-4x more seeds and a set twice as big: real biochemistry is tiered because its autocatalysis is constrained. A null that keeps element balance is the next test.",
  source_opened="full text (Europe PMC, PMC9491600) and supplementary tables S1-S4, S8-S14, scripts S1-S3"),
 entry(id="huson-2024-self-generating-autocatalytic-networks", relevance="background",
  title="Self-generating autocatalytic networks: structural results, algorithms and their relevance to early biochemistry",
  authors="Huson D, Xavier JC, Steel M", year=2024, venue="J. R. Soc. Interface 21:20230732",
  doi="10.1098/rsif.2023.0732", url="https://doi.org/10.1098/rsif.2023.0732", read_depth="full",
  question="What are the structural properties of self-generating autocatalytic (RAF) networks, and how can they be computed?",
  tried="Structural results and algorithms for self-generating autocatalytic networks, with applications to early biochemistry.",
  method_data="Theory and algorithms.",
  key_results="Structural and algorithmic results for RAF-type networks; cites Peng 2022 once among 'other recent structural approaches'.",
  limits="No rewiring or null-model test.",
  ideas_for_us=T14 + ": checked as prior art; it does not test whether SDAS tiers exceed a degree null.",
  source_opened="full text (PMC11286130)"),
 entry(id="matthaus-2008-biosynthetic-potentials-hierarchy", relevance="useful",
  title="Biosynthetic Potentials of Metabolites and Their Hierarchical Organization",
  authors="Matthäus F, Salazar C, Ebenhöh O", year=2008, venue="PLoS Comput. Biol. 4:e1000049",
  doi="10.1371/journal.pcbi.1000049", url="https://doi.org/10.1371/journal.pcbi.1000049", read_depth="full",
  question="Are the biosynthetic potentials (scopes) of metabolites in KEGG organised hierarchically?",
  tried="Compute network-expansion scopes from many random seed sets in KEGG and compare them.",
  method_data="Network expansion on KEGG; 1,000 random seed sets per seed size 2-20.",
  key_results="'most of the resulting consensus scopes overlap or are fully contained in others, revealing a hierarchical ordering of metabolites'; concluded to be 'an intrinsic characteristic of the metabolic network itself'.",
  limits="Randomises seed sets, never the network; scopes need no autocatalysis.",
  ideas_for_us=T14 + ": the closest earlier work. T14 adds the network null it lacked: for SDAS tiers (which also need self-maintenance) the nesting does not survive degree-preserving rewiring, which supports its 'intrinsic' reading for KEGG.",
  source_opened="full text (PMC2289774)"),
]
added = [e["id"] for e in new if e["id"] not in by]
d["papers"].extend(e for e in new if e["id"] not in by)
g = by.get("golnik-2026-raf-stoichiometric-autocatalysis")
if g:
    g["ideas_for_us"] = (g.get("ideas_for_us", "").rstrip() + " Checked as prior art for " + T14 +
        ": formal theory naming the SDAS concept of Peng 2022; it analyses no randomised network.").strip()
    g["date"] = TODAY
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", added, "total", len(d["papers"]))
