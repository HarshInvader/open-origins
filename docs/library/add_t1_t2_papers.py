"""One-off: add or upgrade the library entries for the papers read for T1 and T2 (2026-11-23/24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text())
L = d["papers"]
by = {e["id"]: e for e in L}
TODAY = "2026-11-24"

def base(**k):
    e = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
         "added": TODAY, "date": TODAY, "relevance": "useful"}
    e.update(k)
    return e

new = [
    base(id="wimmer-2021-luca-exergonic-vents",
         title="Energy at Origins: Favorable Thermodynamics of Biosynthetic Reactions in the Last Universal Common Ancestor (LUCA)",
         authors="Wimmer JLE, Xavier JC, Vieira AdN, Pereira DPH, Leidner J, Sousa FL, Kleinermanns K, Preiner M, Martin WF",
         year=2021, venue="Frontiers in Microbiology 12:793664", doi="10.3389/fmicb.2021.793664",
         url="https://doi.org/10.3389/fmicb.2021.793664", topic="Vents and first cells", read_depth="full",
         question="Are the reactions of LUCA's core biosynthesis downhill (exergonic) under alkaline hydrothermal vent conditions?",
         tried="Take 402 core biosynthetic reactions hand-polarised toward synthesis, compute their free energy with eQuilibrator over a grid of pH and temperature, and count the share that is exergonic.",
         method_data="eQuilibrator component contribution; reactant and product concentrations 1 mM, or products 100-fold below reactants; pH and temperature grid; supplementary tables of reactions and free energies.",
         key_results="About 77% of the scored reactions are exergonic at 1 mM, and 95-98% with a 100-fold product gradient. The share is highest around pH 9 and 80 C, which the authors read as matching Lost City-type vents.",
         limits="Our T1 test (sealed, 2026-11-24) found the result is not specific: with the same gradient, 62% of the core run backwards is still exergonic; at equal concentrations the core is 8-11 points less exergonic than matched non-core reactions; vent and pond do not differ beyond the null. Their 77% also counts 37 reactions whose free energy could not be estimated (entered as 0) as exergonic; on the 314 computable reactions the share is 74.8%.",
         ideas_for_us="Done as T1 (experiments/t1_vent_exergonic/T1_RESULTS.md). The general lesson: a share of exergonic reactions needs a reversed and a matched-null control before it says anything about a setting.",
         touches=["#4"], source_opened="full text (PMC8710812, CC BY) and SI Tables 1 and 3 via Europe PMC"),
    base(id="wehbi-2024-genetic-code-order",
         title="Order of amino acid recruitment into the genetic code resolved by last universal common ancestor's protein domains",
         authors="Wehbi S, Wheeler A, Morel B, Manepalli N, Minh BQ, Lauretta DS, Masel J",
         year=2024, venue="PNAS 121:e2410311121", doi="10.1073/pnas.2410311121",
         url="https://doi.org/10.1073/pnas.2410311121", topic="LUCA and the tree of life", read_depth="full",
         question="In what order did amino acids enter the genetic code, judged from protein domains that already existed in LUCA?",
         tried="Compare ancestral amino-acid frequencies of LUCA and pre-LUCA protein-domain clans with those of post-LUCA clans; enrichment in LUCA means earlier recruitment.",
         method_data="Pfam clans dated by phylogeny; ancestral sequence reconstruction; per-amino-acid relative usage with SE (Table 1); code and amino-acid properties on GitHub (sawsanwehbi/Pfam-age-classification).",
         key_results="Early (enriched in LUCA): V G I M T A H E P C. Late (depleted): K S D L N R F Y Q W. Molecular size explains much of the older consensus order.",
         limits="Usage ratios are printed to 3 significant figures, so some amino acids tie. The order is inferred from protein sequences, not from chemistry.",
         ideas_for_us="Used as the outcome in T2 (does asteroid abundance predict this order beyond molecular weight?). Answer: no detectable effect in Bennu or Ryugu, though the sealed test could not decide formally (experiments/t2_code_order/T2_RESULTS.md).",
         touches=["#19"], source_opened="full text (PMC11670089) and GitHub data at commit 01219d8"),
    base(id="higgs-pudritz-2009-code-thermodynamics",
         title="A thermodynamic basis for prebiotic amino acid synthesis and the nature of the first genetic code",
         authors="Higgs PG, Pudritz RE",
         year=2009, venue="Astrobiology 9:483-490", doi="10.1089/ast.2008.0280",
         url="https://doi.org/10.1089/ast.2008.0280", topic="Building blocks", read_depth="full",
         question="Do the amino acids that are easiest to make abiotically match the ones that entered the genetic code first?",
         tried="Combine amino-acid frequencies from discharge experiments, hydrothermal-vent simulations and meteorites into one ranking, then compare it with free energies of formation and with a consensus code order.",
         method_data="Table 1 of 12 abiotic sources (meteorites, spark discharge and others); Table 2 with observed rank, code rank (Trifonov 2004), relative concentration, free energy of formation (Amend and Shock 1998), ATP cost and molecular weight.",
         key_results="Ten of the 20 protein amino acids form in Miller-type discharge experiments. Across discharge, vent and meteorite sources these ten early amino acids fall in one consistent order of decreasing abundance, which thermodynamics predicts. The authors argue the first proteins reflected these abundances and the other ten were added later, stepwise.",
         limits="The consensus order they compare with has since been revised (Wehbi 2024). Amino acids never observed share one bottom rank. Abundance and molecular weight are strongly linked, which our T2 controls for.",
         ideas_for_us="Prior art behind T2. Our partial correlation, controlling for molecular weight, finds no abundance effect in the returned asteroid samples; Murchison's raw association falls from 0.46 to 0.25 once weight is controlled.",
         touches=["#19"], source_opened="arXiv:0904.0402 (submitted version), Table 2 via pdftotext"),
]
for e in new:
    if e["id"] in by:
        by[e["id"]].update(e)
    else:
        L.append(e)

g = by["glavin-2025-l0-samples"]
g.update(read_depth="full", date=TODAY,
         question="What soluble organic matter, including amino acids, is in the first Bennu samples?",
         method_data="Hot-water extracts analysed by LC-FD/ToF-MS and LC-FD/HRMS; Extended Data Tables 2 and 3 compare Bennu OREX-803001-0 with Murchison, Tarda, Orgueil and Ryugu A0106.",
         limits=g["limits"].replace("(abstract only) ", "") + " Of the 20 protein amino acids, 14 are below detection in Bennu's Extended Data Table 2, and Asn, Gln and Cys are lost to hot-water extraction.",
         ideas_for_us="Source of the abundances for T2 (transcribed in experiments/t2_code_order/data). In T2, abundance did not predict genetic-code order beyond molecular weight.",
         source_opened="full text (PMC11842271) and Extended Data Tables 2-3 (CC BY)")
n = by["naraoka-2023-l0-samples"]
n.update(read_depth="full", date=TODAY,
         key_results="Ryugu sample A0106 contains amino acids, amines and other soluble organics. The authors note L-excesses (for example in valine) and write that contamination is the likely source of non-racemic valine in the A0106 extract.",
         limits="Read the HAL copy (hal-04208565, submitted manuscript); Table S3 is not in that copy. Glycine in A0106 differs about tenfold between methods (~0.6 nmol/g by LC-FD/HRMS vs 5.6 nmol/g by 3D-HPLC/FD).",
         ideas_for_us="Used in T2 to choose D+L abundance (not L alone) because of contamination. The alternative Ryugu sample C0107 (Parker 2023) would make T2 decidable but could not be opened.",
         source_opened="HAL hal-04208565 (submitted manuscript)")
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print(len(L))
