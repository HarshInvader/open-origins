"""One-off: T18 (QT45 error threshold) prior-art papers and note (2026-11-25)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
base = dict(kind="Paper", topic="RNA world", in_news=False, added="2026-11-25", verified=True,
            changes_plan="", touches=["T18"], date="2026-11-25", relevance="core")
new = [
 dict(base, id="szilagyi-2014-local-neutral-networks", read_depth="full",
      title="Local Neutral Networks Help Maintain Inaccurately Replicating Ribozymes",
      authors="Szilágyi A, Kun Á, Szathmáry E", year=2014, venue="PLoS ONE 9 (2014), e109987",
      doi="10.1371/journal.pone.0109987", url="https://doi.org/10.1371/journal.pone.0109987", source_opened="PMC full text (PMC4192543)",
      question="How much do neutral mutants raise the error threshold of real ribozymes above the single-peak value?",
      tried="Compare genotypic and phenotypic error thresholds for two ribozymes, using computed secondary-structure landscapes.",
      method_data="Neurospora VS and hairpin ribozymes; landscapes from computed secondary structures, solved numerically up to length 16; threshold predicted from the one-step degree of neutrality.",
      key_results="Genotypic vs phenotypic thresholds of 0.033 vs 0.053 (VS) and 0.042 vs 0.144 (hairpin): neutral neighbours relax the threshold.",
      limits="Landscapes are computed structures, not measured fitness, and the ribozymes are not polymerases copying themselves.",
      ideas_for_us="T18 asks the same question of a polymerase's own measured landscape (QT45, singles and doubles). Our planted test showed that pair epistasis, small in any one double, adds up near the threshold and biases a global-curve model low by about 27%."),
 dict(base, id="kun-2005-relaxed-error-threshold", read_depth="abstract",
      title="Real ribozymes suggest a relaxed error threshold",
      authors="Kun Á, Santos M, Szathmáry E", year=2005, venue="Nat Genet 37 (2005), 1008-1011",
      doi="10.1038/ng1621", url="https://doi.org/10.1038/ng1621", source_opened="Abstract only (Europe PMC); full text paywalled",
      question="Is the error threshold for real ribozymes as harsh as the single-peak Eigen model implies?",
      tried="Comparative analysis of two extensively mutagenized ribozymes.",
      method_data="Mutagenesis data on two ribozymes (named in Szilágyi 2014 as the Neurospora VS and hairpin ribozymes).",
      key_results="With copying fidelity 0.999 per digit the phenotypic error threshold 'rises well above 7,000 nucleotides'.",
      limits="Read from the abstract only. Not a polymerase ribozyme, and not a self-copying system.",
      ideas_for_us="The relaxed-threshold idea that T18 tests on QT45's own landscape."),
]
for e in new:
    assert e["id"] not in by; d["papers"].append(e)
g = by["gianni-2026-rna-world"]
g["ideas_for_us"] = (g.get("ideas_for_us", "").rstrip() + " T18 (2026-11-25, experiments/t18_qt45_error_threshold): the authors' "
    "replicator-mutator model (fig. S32B) sets every unmeasured double and every genotype with 3+ mutations to a growth rate of 0.01, and at 94.1% "
    "fidelity about 89% of offspring per round trip carry 3+ mutations, so that value decides the answer. Our replacement, a global-epistasis curve "
    "fitted to singles and doubles, recovered planted thresholds within 3% on noise-only landscapes but missed by about 27% (always low) once pair "
    "epistasis was planted, so it failed its kill test before any real-data threshold was computed.").strip()
d["updated"] = "2026-11-25"
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("ok", len(d["papers"]))
