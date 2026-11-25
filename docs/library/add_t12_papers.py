"""One-off: add the papers read for T12 (Janzen 2022 specificity vs activity) to the library (2026-11-24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); ids = {e["id"] for e in d["papers"]}
TODAY = "2026-11-24"
T12 = "T12 (sealed, 2026-11-24, experiments/t12_janzen_specificity/T12_RESULTS.md)"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "date": TODAY, "topic": "RNA world", "touches": []}
    base.update(k); return base

new = [
 entry(id="janzen-2022-aminoacylation-ribozyme-specificity", relevance="core",
  title="Emergent properties as by-products of prebiotic evolution of aminoacylation ribozymes",
  authors="Janzen E, Shen Y, Vázquez-Salazar A, Liu Z, Blanco C, Kenchel J, Chen IA", year=2022, venue="Nat. Commun. 13:3631",
  doi="10.1038/s41467-022-31387-0", url="https://doi.org/10.1038/s41467-022-31387-0", read_depth="full",
  question="When aminoacylation ribozymes are selected for activity, do other properties, such as substrate specificity, come along as by-products?",
  tried="Measure rates of 1,954 sequences in each of five ribozyme families on six aminoacyl substrates by k-Seq, and correlate total activity with a promiscuity index.",
  method_data="k-Seq kinetics relative to background, per-sequence bootstrap intervals; promiscuity index (normalized entropy of the six rates); data in the supplementary workbook (MOESM3).",
  key_results="'ribozyme activity was positively correlated with specificity'; Table 1 gives Pearson R of -0.54 to -0.84 between activity and promiscuity over all 1,954 sequences per family (p < 1e-95).",
  limits="Rates are relative to background, so inactive sequences read about 1 on every substrate and look perfectly even; total activity and the index share the same noisy cells. Neither is corrected for in Table 1.",
  ideas_for_us=T12 + ": with the floor removed (all_sum > 30, r - 1) and shared noise corrected by SIMEX, the link holds clearly in family 2.1 only (R_S -0.41, -0.52 to -0.31). 1B.1 (-0.05) and 2.2 (+0.10) lose it; 1A.1 (-0.25) is too small to say. Sealed verdict: kill of the general claim. Gate reproduced Table 1 to 0.0005 first.",
  source_opened="full text (Europe PMC, PMC9233669) and supplementary information"),
 entry(id="shen-2021-kseq-ribozyme-kinetics", relevance="useful",
  title="Kinetic sequencing (k-Seq) as a massively parallel assay for ribozyme kinetics: utility and critical parameters",
  authors="Shen Y, Pressman A, Janzen E, Chen IA", year=2021, venue="Nucleic Acids Res. 49:e67",
  doi="10.1093/nar/gkab199", url="https://doi.org/10.1093/nar/gkab199", read_depth="abstract",
  question="How reliable are kinetic parameters measured for many ribozyme sequences at once by sequencing?",
  tried="Characterise k-Seq and its sources of error, and add bootstrapping to quantify uncertainty per sequence.",
  method_data="k-Seq on aminoacylation ribozyme pools.",
  key_results="'Relative abundance, kinetic coefficients, and measurement noise were found to affect the measurement of each sequence. We introduced bootstrapping to robustly quantify the uncertainty in estimating model parameters'.",
  limits="Abstract only. It does not discuss the promiscuity index.",
  ideas_for_us=T12 + ": source of the per-sequence bootstrap noise that T12's SIMEX correction relies on. If that bootstrap understates the real noise, T12's correction is too weak, which would push toward support, not kill.",
  source_opened="abstract (Europe PMC)"),
 entry(id="nath-2008-promiscuity-index", relevance="background",
  title="A Quantitative Index of Substrate Promiscuity",
  authors="Nath A, Atkins WM", year=2008, venue="Biochemistry 47:157-166",
  doi="10.1021/bi701448p", url="https://doi.org/10.1021/bi701448p", read_depth="abstract",
  question="Can enzyme promiscuity be put on one quantitative scale?",
  tried="Define a promiscuity index from catalytic efficiencies toward a set of substrates.",
  method_data="Normalized entropy of catalytic efficiencies.",
  key_results="'Here we define a quantitative index of promiscuity (I) that can be calculated from the catalytic efficiencies of an enzyme toward a defined set of substrates.'",
  limits="Abstract only. Defined on catalytic efficiencies, which have no floor at 1; applied to rates relative to background it inherits a floor.",
  ideas_for_us=T12 + ": the index Janzen 2022 uses. Its original form has no background floor, which is why T12 subtracts the background (r - 1) before computing it.",
  source_opened="abstract (Europe PMC)"),
 entry(id="janzen-2020-promiscuous-ribozymes-review", relevance="background",
  title="Promiscuous Ribozymes and Their Proposed Role in Prebiotic Evolution",
  authors="Janzen E, Blanco C, Peng H, Kenchel J, Chen IA", year=2020, venue="Chem. Rev. 120:4879-4897",
  doi="10.1021/acs.chemrev.9b00620", url="https://doi.org/10.1021/acs.chemrev.9b00620", read_depth="abstract",
  question="Were early ribozymes more promiscuous than evolved ones, and did that matter for prebiotic evolution?",
  tried="Review promiscuity in natural and in vitro selected ribozymes.",
  method_data="Literature review.",
  key_results="'We suggest that while de novo ribozymes appear to be promiscuous in general, they are not obviously more promiscuous than more highly evolved or active sequences.'",
  limits="Abstract only; a review.",
  ideas_for_us=T12 + ": the same group's earlier view, that activity and promiscuity are not obviously linked, fits T12 better than the 2022 headline does: after floor and noise correction, only one of four families shows the link.",
  source_opened="abstract (Europe PMC)"),
]
added = [e["id"] for e in new if e["id"] not in ids]
d["papers"].extend(e for e in new if e["id"] not in ids)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", added, "total", len(d["papers"]))
