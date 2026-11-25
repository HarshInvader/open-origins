"""One-off: add the papers read for T15 (formose dynamic flow vs repeat-run noise) to the library (2026-11-25)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); ids = {e["id"] for e in d["papers"]}
TODAY = "2026-11-25"
T15 = "T15 (sealed, 2026-11-25, experiments/t15_formose_flow_noise/T15_RESULTS.md)"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "date": TODAY, "topic": "Building blocks", "touches": []}
    base.update(k); return base

new = [
 entry(id="van-duppen-2023-formose-dynamic-conditions", relevance="core",
  title="Dynamic Environmental Conditions Affect the Composition of a Model Prebiotic Reaction Network",
  authors="van Duppen P, Daines E, Robinson WE, Huck WTS", year=2023, venue="J. Am. Chem. Soc. 145:7559-7568",
  doi="10.1021/jacs.3c00908", url="https://doi.org/10.1021/jacs.3c00908", read_depth="full",
  question="Does a fluctuating environment change the products of the formose reaction compared with steady state?",
  tried="Run the formose reaction in a flow reactor at steady state and with oscillating Ca(OH)2 input or flow rate, and compare product concentrations by GC-MS.",
  method_data="13 flow runs, about 44-51 samples each, ~20 sugars quantified; data and code at github.com/huckgroup/Formose_2022 (BSD-3).",
  key_results="'the product compositions of the formose reaction under dynamic conditions deviate significantly from those under steady state conditions'; p <= 1e-4 for DHA, threose, erythrulose and xylulose in every series.",
  limits="The p-values come from scipy ttest_ind on the serial samples of one run against another (found in the authors' code; the SI does not name the test): samples treated as independent, no run-to-run variance. Two repeat-run pairs in the deposit are never compared.",
  ideas_for_us=T15 + ": the median dynamic-vs-steady shift (1-2.4 within-run SD) is smaller than the gap between repeat runs at identical settings (2.7-6 SD for DHA, threose, xylulose; about 14 for erythrulose). Sealed verdict kill: the effect is not shown beyond run-to-run reproducibility. The repeats span days, the comparisons do not, so this is not proof of no effect.",
  source_opened="full text (Europe PMC, PMC10080678) and the GitHub deposit at commit 94c10347"),
 entry(id="baltussen-2024-formose-reservoir-computing", relevance="useful",
  title="Chemical reservoir computation in a self-organizing reaction network",
  authors="Baltussen MG, de Jong TJ, Duez Q, Robinson WE, Huck WTS", year=2024, venue="Nature 631:549-555",
  doi="10.1038/s41586-024-07567-x", url="https://doi.org/10.1038/s41586-024-07567-x", read_depth="full",
  question="Can the formose reaction network, driven by input changes, compute like a reservoir computer?",
  tried="Drive the formose reaction in flow with varying inputs and read its outputs by mass spectrometry to perform classification and prediction tasks.",
  method_data="Flow reactor, online mass spectrometry, steady-state output averaged over the final 10-minute sample period.",
  key_results="The network performs nonlinear classification and prediction tasks; the outputs are described as 'deterministic' and 'robust against outliers and overfitting'.",
  limits="Builds on van Duppen 2023 without re-testing it; a different measurement setup.",
  ideas_for_us=T15 + ": follow-up that takes the 2023 dynamic-conditions result as given. T15 shows that result is not separated from run-to-run noise in its own deposit; this paper's own reproducibility data are separate and were not tested.",
  source_opened="full text (PMC11254755)"),
 entry(id="de-jong-2025-formose-minerals-history", relevance="background",
  title="Environmental History is Transferred via Minerals Altering Formose Reaction Pathways",
  authors="de Jong TJ, Demertzi AD, Robinson WE, Huck WTS", year=2025, venue="Angew. Chem. Int. Ed. 64:e202504659",
  doi="10.1002/anie.202504659", url="https://doi.org/10.1002/anie.202504659", read_depth="full",
  question="Can minerals carry the history of past conditions into later formose reaction outcomes?",
  tried="Batch formose reactions with minerals exposed to different earlier conditions.",
  method_data="Batch experiments with minerals.",
  key_results="Reports that earlier environmental history, transferred through minerals, alters formose pathways; cites the 2023 work as showing outcomes are 'significantly shaped by modulating the concentration of the catalyst Ca(OH)2'.",
  limits="Takes the 2023 result as given; not a reanalysis.",
  ideas_for_us=T15 + ": follow-up checked as prior art; does not re-test the 2023 claim.",
  source_opened="full text (PMC12124346)"),
]
added = [e["id"] for e in new if e["id"] not in ids]
d["papers"].extend(e for e in new if e["id"] not in ids)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", added, "total", len(d["papers"]))
