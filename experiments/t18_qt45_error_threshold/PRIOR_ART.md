# T18 prior art: has anyone computed QT45's error threshold from its own landscape?

Searched 2026-11-25 on Europe PMC (REST search, generic User-Agent) and Crossref (titles and authors). Only papers whose text or abstract was opened are cited. Queries: `"error threshold" AND "polymerase ribozyme"` (31 hits), `"error catastrophe" AND "polymerase ribozyme"` (15), `"relaxed error threshold"` (12), `"error threshold" AND "fitness landscape" AND RNA` (118), `"error threshold" AND (ribozyme OR "RNA world") AND (landscape OR mutational)` (77), `QT45 AND (fidelity OR "error threshold" OR quasispecies)` (6), `"error threshold" AND "deep mutational"` (9).

## Verdict

**Partly done, by the QT45 authors themselves.** Not fully done, so the study goes ahead, but as a re-analysis of their model's decisive assumptions, not as a first calculation.

## The QT45 paper

Gianni E, Kwok SLY, Wan CJK, Goeij K, Clifton BE, Colizzi ES, Attwater J, Holliger P. 2026. "A small polymerase ribozyme that can synthesize itself and its complementary strand." Science 391:1022-1028. doi:10.1126/science.adt2760. Opened: author manuscript and SI via Europe PMC (PMC7618777), cached in `experiments/qt45_numbers/raw/`.

**Fidelity, verbatim (main text):** "Deep sequencing confirmed the identity of the full-length (-) strand synthesized using the NNN pool, with 10.9% perfect full-length (-) strand sequences, and an average per nucleotide fidelity of 94.1% ( Fig. 4D ), slightly higher than the fidelity of seq0-HH synthesis."

- Conditions (Fig. 4 legend): 8 nM primer, 8 nM template, 80 nM ribozyme, 50 nM each substrate (all 64 triplets, "NNN"), 0.01% Tween 20, 0.4 mM MgCl₂, 1.2 mM KCl, 1 mM CHES-KOH pH 9, 72 days at −7 °C frozen.
- No confidence interval is given. From the perfect-read share, 0.109^(1/42) = 0.9486 per nucleotide, so the two summaries differ by about 0.008.
- Other figures, other conditions: 92.6% for the 33-nt hammerhead (NNN pool, 50 mM MgCl₂, 50 mM CHES pH 9, 65 days); 43.4% perfect reads for the (+) strand made from defined triplets plus one hexamer (no per-nucleotide figure given).
- Errors: "G:U wobble mispairing, particularly at the first triplet position, is the main source of errors".

**Their error-threshold work (main text):** "we modelled the specific behavior of a population of QT45 wild-type and its mutants using the empirical relative fitness values measured in this study ( Fig. 2D ) as proxies for replication rates ... This analysis suggests that at the fidelities observed for QT45 products (92.6% and 94.1%) the population of active variants (quasispecies) would be minimal (<0.5%), but an increase in fidelity to levels observed in other polymerase ribozymes (e.g. 97.4% ( 13 )), would enable maintenance of a sizeable population of active variants of QT45 length in the current mutational landscape (~12% of the total population, fig. S32B )."

**Their model (Supplementary Text, "Error threshold computational numerical model"), verbatim excerpts:**
- "The model represents the genotype space as the master sequence (Hamming distance, HD = 0), all single mutants (HD = 1), all double mutants (HD = 2), and a lumped class containing all genotypes with HD ≥ 3."
- "Rare values for fitness for HD=2 mutants that are missing from the dataset, as well as HD=3 lumped class are given an arbitrary growth rate value of 0.01."
- "Q was normalized such that all residual probability in each column were assigned to the HD ≥ 3 class, which was modeled as absorbing".
- S32A (single-peak Eigen): "QT45 only requires a selective superiority higher than 166 to overcome the error threshold" (84-nt genome, q = 0.941); "the selective superiority in a self-replication context is unknown."

**Their code** (Zenodo 10.5281/zenodo.13891380, `QTribozyme_quasispecies-main-2.zip`, read not run; copy in `raw/authors_quasispecies/`, gitignored): rate = 2^(log2 enrichment); the inputs are value-identical to the CSVs used by #30; the S32B observable is the summed concentration of HD ≤ 2 genotypes with rate > 0.8. One quirk: mutant-to-mutant transitions use the single-strand table (`dmut_mean`) while master transitions use the composite two-strand table.

**What they did not do:** give a threshold error rate or its uncertainty; model HD ≥ 3 genotypes (they set all of them to 0.01, yet at 94.1% about 89% of the master's offspring per (+) → (−) → (+) generation are HD ≥ 3); vary the 0.01; or check the method on landscapes with a known threshold.

## Error thresholds from real ribozyme data

- Kun Á, Santos M, Szathmáry E. 2005. "Real ribozymes suggest a relaxed error threshold." Nat Genet 37:1008-1011. doi:10.1038/ng1621. Opened: abstract (Europe PMC; full text paywalled, not obtained). "on the basis of comparative analysis of two extensively mutagenized ribozymes, that with a copying fidelity of 0.999 per digit per replication the phenotypic error threshold rises well above 7,000 nucleotides". The two ribozymes are named in Szilágyi 2014 as the Neurospora VS and hairpin ribozymes, not polymerases.
- Szilágyi A, Kun Á, Szathmáry E. 2014. "Local neutral networks help maintain inaccurately replicating ribozymes." PLoS One 9:e109987. doi:10.1371/journal.pone.0109987. Opened: full text (PMC4192543). Genotypic vs phenotypic thresholds "0.033 versus 0.053 and 0.042 versus 0.144" for the VS and hairpin ribozymes; the phenotypic threshold is predicted from the one-step degree of neutrality (their Eq. 2, from Takeuchi et al.; the equation is an image in the XML and was not transcribed). Their landscapes are computed secondary structures (full numerical solution up to length 16), not measured fitness.
- Chen IA. 2024. "RNA life on the edge of catastrophe." PNAS 121:e2402649121. doi:10.1073/pnas.2402649121. Opened: full text (PMC10990123). Commentary on Papastavrou et al.; states the single-peak condition u < (ln f₀)/L and that 52-2 "lacked sufficient fidelity to beat the error threshold"; no calculation on a measured landscape.
- Papastavrou N, Horning DP, Joyce GF. 2024. "RNA-catalyzed evolution of catalytic RNA." PNAS 121:e2321592121. doi:10.1073/pnas.2321592121 (in library, full read earlier). Experimental: 71-89 (89.1%) propagates a hammerhead, 52-2 (81.4%) does not. No threshold computed from a landscape, and the polymerase copies a hammerhead, not itself.

## Checked, not relevant to this question

- Higgs PG. 2026. "How Strong Is the Case for the RNA World?" Life 16:1633. doi:10.3390/life16101633 (full text, PMC13706048). Mentions QT45's length against the virtual-circular-genome limit; its error-threshold discussion is spatial clustering and compartments, not QT45's landscape.
- Flores-García AA et al. 2026. Front Genet. doi:10.3389/fgene.2026.1813517 (full text, PMC13126052). Review; restates 94.1% and that it "naturally connects to error threshold constraints"; no calculation.
- Paczkó M, Szathmáry E, Szilágyi A. 2024. eLife 13:RP93208. doi:10.7554/elife.93208 (title and abstract via search only). Theory of parabolic growth; no measured landscape. Not used.

## What this means for T18

1. The headline question ("is QT45 below threshold at 94.1%?") has an answer on record from the authors. T18 can only add value by testing what drives it: the 0.01 for HD ≥ 3, and the unknown selective superiority.
2. The relaxed-threshold idea (neutral and compensatory mutants raise the threshold; Kun 2005, Szilágyi 2014) has not been applied to a polymerase's own measured landscape. This is the original part.
3. The strongest test is therefore: replace the 0.01 with a model of HD ≥ 3 fitted to singles and doubles, check on planted landscapes that this recovers a known threshold, and report e* and λ_A(e_meas) with an interval.
