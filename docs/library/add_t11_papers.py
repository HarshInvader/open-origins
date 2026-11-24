"""One-off: add the papers read for T11 (ribozyme epistasis vs tertiary contacts) to the library (2026-11-24)."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); ids = {e["id"] for e in d["papers"]}
TODAY = "2026-11-24"
T11 = "T11 (sealed, 2026-11-24, experiments/t11_ribozyme_epistasis/T11_RESULTS.md)"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "date": TODAY, "topic": "RNA world", "touches": []}
    base.update(k); return base

new = [
 entry(id="roberts-2023-ribozyme-double-mutant-scans", relevance="core",
  title="RNA sequence to structure analysis from comprehensive pairwise mutagenesis of multiple self-cleaving ribozymes",
  authors="Roberts JM, Beck JD, Pollock TB, Bendixsen DP, Hayden EJ", year=2023, venue="eLife 12:e80360",
  doi="10.7554/elife.80360", url="https://doi.org/10.7554/elife.80360", read_depth="full",
  question="Do complete single- and double-mutant activity maps of self-cleaving ribozymes carry their structure, including tertiary contacts?",
  tried="Measure the cleavage of every single and double mutant of five ribozymes (CPEB3, HDV, hammerhead, hairpin, twister) by sequencing, and read structure from epistasis heat maps.",
  method_data="Co-transcriptional self-cleavage, fraction cleaved from read counts, three replicates; epistasis as log(RA_ij / (RA_i RA_j)). Data and code at GitLab, archived at swh:1:rev:7be31e58784ab6ffe5f15790ebbda98279af84d2 (also holds a hatchet ribozyme not in the paper).",
  key_results="Base-paired regions show anti-diagonal lines of strong positive epistasis, and disrupting fewer base pairs gives higher epistasis. Hairpin loops A and B show positive epistasis; the hammerhead loop-loop contact does not ('double mutants do not show positive epistasis').",
  limits="Tertiary contacts are shown by heat maps and by region, with no score of contacts against non-contact pairs matched on separation and single-mutant effects. The paper says CPEB3 has no crystal structure; one exists (PDB 7QR3, 2022).",
  ideas_for_us=T11 + ": we scored contacts against matched non-contacts with a noise-scaled epistasis z. Base pairs: pooled Δ 0.44 (0.33-0.50), so the method works. Tertiary contacts: Δ 0.11 (-0.02 to 0.23), inconclusive. The faint, consistent signal (about AUC 0.6 in every ribozyme with harmful singles) is real-looking but not established. This gives our QT45 study (#30) its missing positive control.",
  source_opened="full text (Europe PMC, PMC9901934)"),
 entry(id="zhang-2020-coda-base-pairs-from-mutants", relevance="useful",
  title="Accurate inference of the full base-pairing structure of RNA by deep mutational scanning and covariation-induced deviation of activity",
  authors="Zhang Z, Xiong P, Zhang T, Wang J, Zhan J, Zhou Y", year=2020, venue="Nucleic Acids Res. 48:1451-1465",
  doi="10.1093/nar/gkz1192", url="https://doi.org/10.1093/nar/gkz1192", read_depth="partial",
  question="Can base pairs, including pseudoknots and lone pairs, be inferred from single-to-triple mutant fitness data?",
  tried="Fit a support-vector model of double-mutant activity from the two singles, and call base pairs from the deviations.",
  method_data="Deep mutational scans of an RNA and of a 48-nt twister fragment (PDB 4OJI).",
  key_results="'a library of <5 x 10^4 single-to-triple mutants is sufficient to infer 25 of 26 base pairs'; the twister ribozyme at 100% precision 'with only noncanonical base pairs as false negatives'.",
  limits="Target is base pairs, scored by precision against the native list, with no null matched on separation or single effects. Non-canonical contacts are the misses. Read: abstract, CODA methods and the twister section.",
  ideas_for_us=T11 + ": prior art. Base pairs from mutant scans are established, so T11 uses them only as a positive control and tests non-base-pair contacts. Their global fit of doubles from singles is the same idea as our isotonic fit.",
  source_opened="full text, parts read (PMC7026644)"),
 entry(id="andreasson-2020-glms-double-mutant-rescue", relevance="background",
  title="Comprehensive sequence-to-function mapping of cofactor-dependent RNA catalysis in the glmS ribozyme",
  authors="Andreasson JOL, Savinov A, Block SM, Greenleaf WJ", year=2020, venue="Nat. Commun. 11:1663",
  doi="10.1038/s41467-020-15540-1", url="https://doi.org/10.1038/s41467-020-15540-1", read_depth="partial",
  question="Which double mutants of the glmS ribozyme rescue the activity of a harmful single mutant, and what does that say about its structure?",
  tried="Measure cleavage rates of many glmS variants on a sequencing chip and look for rescue interactions.",
  method_data="High-throughput kinetics of glmS variants; a rescue is kobs(double)/kobs(single) > 1.",
  key_results="G26 mutations rescue both members of the G7-C52 pair, a tertiary interaction; no rescues were seen within the 27*28-45 base triple at the active site.",
  limits="Contacts are discussed case by case, with no systematic score. Read: the double-mutant rescue section only.",
  ideas_for_us=T11 + ": prior art and a warning. Contacts at catalytic positions may never be rescued because their identity matters for chemistry, one reason a tertiary signal in epistasis would be small, as T11 found (Δ 0.11).",
  source_opened="full text, rescue section read (PMC7125110)"),
 entry(id="zheng-2019-hatchet-ribozyme-structure", relevance="background",
  title="Hatchet ribozyme structure and implications for cleavage mechanism",
  authors="Zheng L, Falschlunger C, Huang K, Mairhofer E, Yuan S, Wang J, Patel DJ, Micura R, et al.", year=2019, venue="PNAS 116:10783-10791",
  doi="10.1073/pnas.1902413116", url="https://doi.org/10.1073/pnas.1902413116", read_depth="partial",
  question="What is the crystal structure of the hatchet self-cleaving ribozyme?",
  tried="Solve the crystal structure of the hatchet ribozyme product.",
  method_data="X-ray crystallography (PDB 6JQ5).",
  key_results="'Two hatchet ribozyme product molecules form a dimer through swapping of the 3' ends of the pairing strand', probably helped by the palindromic A67-U70.",
  limits="The dimer swap means a monomer's contacts have to be stitched from two chains.",
  ideas_for_us=T11 + ": source of the hatchet contact map (monomer stitched from chains A and B, palindrome dropped). Hatchet's single mutants were near-neutral in the Roberts deposit, so it failed T11's base-pair check and did not count.",
  source_opened="full text (PMC6561176)"),
]
added = [e["id"] for e in new if e["id"] not in ids]
d["papers"].extend(e for e in new if e["id"] not in ids)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", added, "total", len(d["papers"]))
