"""One-off: add the papers read for T13 (ligase neutral network vs one global curve) to the library (2026-11-24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); ids = {e["id"] for e in d["papers"]}
TODAY = "2026-11-24"
T13 = "T13 (sealed, 2026-11-24, experiments/t13_ligase_global_epistasis/T13_RESULTS.md)"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "date": TODAY, "topic": "RNA world", "touches": []}
    base.update(k); return base

new = [
 entry(id="rotrattanadumrong-2022-ligase-neutral-network", relevance="core",
  title="Experimental exploration of a ribozyme neutral network using evolutionary algorithm and deep learning",
  authors="Rotrattanadumrong R, Yokobayashi Y", year=2022, venue="Nat. Commun. 13:4847",
  doi="10.1038/s41467-022-32538-z", url="https://doi.org/10.1038/s41467-022-32538-z", read_depth="full",
  question="How far does the neutral network of a ligase ribozyme reach, and can a neural network find distant neutral variants?",
  tried="Explore a ligase ribozyme's sequence space for eight generations with a genetic algorithm and an MLP trained on measured activities, plus a complete 2^16 library between two genotypes.",
  method_data="High-throughput ligation assay, two replicates; MLP trained on 20,920 variants from generations 1-6; Walsh-Hadamard analysis of the 2^16 library. Data on Zenodo (doi:10.5281/zenodo.6945203, Apache-2.0).",
  key_results="Neutral variants found at Hamming distances up to 19. 'In generation 8, almost all neutral mutants identified were expected to be deleterious under the epistasis-free model', read as the network having learned 'higher-order, nonlinear mutational effects'. Generation 8 neutral fraction 0.28.",
  limits="The 'epistasis-free' baseline is multiplicative in activity, which drives far variants to zero; no global-nonlinearity baseline. The authors note that 'Further statistical tests could be performed to remove global nonlinearities'.",
  ideas_for_us=T13 + ": one additive score through one global curve, fitted on generations 1-6, recalls 80% of neutral variants nearby (held-out, generation 7) but 0.1% in generation 8. A rebuilt network beats it there by only 0.049 AP (support needed 0.10). Verdict 'partly': the additive failure is real, the case for learned higher-order effects is weak. Compare QT45 (#30).",
  source_opened="full text (Europe PMC, PMC9385714) and Zenodo deposit (selected members)"),
 entry(id="charest-2023-ribozyme-landscape-information-epistasis", relevance="useful",
  title="Discovering pathways through ribozyme fitness landscapes using information theoretic quantification of epistasis",
  authors="Charest N, Shen Y, Lai YC, Chen IA, Shea JE", year=2023, venue="RNA 29:1644-1657",
  doi="10.1261/rna.079541.122", url="https://doi.org/10.1261/rna.079541.122", read_depth="full",
  question="Can an information-theoretic measure of epistasis find evolutionary pathways through ribozyme fitness landscapes?",
  tried="Quantify epistasis in ribozyme landscape data with an information-theoretic method and use it to trace pathways.",
  method_data="Re-analysis of published ribozyme fitness landscapes.",
  key_results="Argues that simple nonlinear (global-curve) models work 'for relatively simple systems in which there is a largely additive landscape subject to random variation, but not for more complex landscapes', and calls the Rotrattanadumrong MLP a 'black box'.",
  limits="Sets global-curve models aside as a class without fitting one to the ligase data.",
  ideas_for_us=T13 + ": prior art. T13 fitted the global curve it set aside: on the ligase it works near the training data and fails far from it, so its claim about global curves holds for distant variants and not for nearby ones.",
  source_opened="full text (PMC10578471)"),
 entry(id="marti-gomez-2026-gpmap-tools", relevance="background",
  title="Inference and Visualization of Complex Genotype-Phenotype Maps",
  authors="Martí-Gómez C, Zhou J, Chen WC, Stoltzfus A, Kinney JB, McCandlish DM", year=2026, venue="Mol. Biol. Evol. 43:msag023",
  doi="10.1093/molbev/msag023", url="https://doi.org/10.1093/molbev/msag023", read_depth="full",
  question="How can complex genotype-phenotype maps be inferred from data and visualised?",
  tried="Present gpmap-tools, with minimum epistasis interpolation (MEI) and variance-component (VC) regression, and visualisation of landscapes.",
  method_data="Worked examples on short sequence elements such as the Shine-Dalgarno sequence.",
  key_results="Tools for inference and visualisation of complete or near-complete genotype-phenotype maps.",
  limits="Its own limitation: MEI and VC regression 'do not explicitly model global or nonspecific epistasis'. It cites the ligase dataset only in an introductory list.",
  ideas_for_us=T13 + ": checked as prior art; it does not fit a global curve to the ligase data, so it does not settle T13.",
  source_opened="full text (PMC12911936)"),
 entry(id="faure-2024-walsh-hadamard-extension", relevance="background",
  title="An extension of the Walsh-Hadamard transform to calculate and model epistasis in genetic landscapes of arbitrary shape and complexity",
  authors="Faure AJ, Lehner B, Miró Pina V, Serrano Colome C, Weghorn D", year=2024, venue="PLoS Comput. Biol. 20:e1012132",
  doi="10.1371/journal.pcbi.1012132", url="https://doi.org/10.1371/journal.pcbi.1012132", read_depth="full",
  question="How can epistasis be calculated for landscapes with more than two states per site?",
  tried="Extend the Walsh-Hadamard transform to landscapes of arbitrary shape and apply it to deep mutational scans.",
  method_data="Empirical work on tRNA and protein domain landscapes.",
  key_results="A general background-averaged epistasis framework for multi-allelic landscapes.",
  limits="Cites the ligase study only in an introductory list; not applied to it.",
  ideas_for_us=T13 + ": checked as prior art; it does not test the ligase generation 8 claim.",
  source_opened="full text (PMC11161127)"),
]
added = [e["id"] for e in new if e["id"] not in ids]
d["papers"].extend(e for e in new if e["id"] not in ids)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", added, "total", len(d["papers"]))
