# Ideas from the library

Written 2026-11-19 from the papers in [library.json](library.json) (rendered in [LIBRARY.md](LIBRARY.md)). These are ideas only. None of them has been started, sealed or run. Each would need its own pre-registration before any data is looked at.

Ranked by how much each one would tell us per unit of work, and by whether it bears on a study we are running now.

## 1. Clade-varying loss rates in the LUCA calibration truth model, and a second target (bears on #32)

- **Sources.** Huang et al. 2026, Nat Commun, doi:10.1038/s41467-026-76386-7 (full text). Csűrös 2026, PNAS, doi:10.1073/pnas.2537812123. Szöllősi et al. 2026 gene-content grammar preprint (library entry `szollosi-2026-gene-content-grammar`).
- **The idea.** Huang et al. found that letting loss rates differ by lineage changed where the archaeal root sits and what the ancestor contained. DPANN loss was 0.40-0.45, against 0.26-0.27 in other clades. Sealed v3 of #32 draws a rate for each family (lognormal, sigma 0.5), but every lineage shares the same rates. So we do not know how the calibration behaves when one domain, or one clade inside it, loses genes faster than the rest.
- **What's untested.** No one has simulated genomes with a known LUCA under lineage-varying loss and then measured the root PP bias of ALE or AleRax. Huang et al. report no such simulation in the main text or methods. Their supplement was not opened.
- **Open data.** Huang et al.'s per-family LACA posteriors and reconciliations are on Zenodo, record 18701544. The calibration learned in #32 can be applied to them as a second target, with the prediction written down first. Their family counts for LACA are 800-1,219 (Euryarchaeota root) and 1,190-1,709 (MHH root), at PP thresholds 0.5 and 0.75.
- **Current study.** Yes, #32. Adding this would need a new sealed amendment (a sensitivity arm). It must not be an edit to v1, v2 or v3.

## 2. Two transfer patterns the #32 truth model may miss (bears on #32)

- **Sources.** Wehbi et al. 2026, bioRxiv, doi:10.64898/2026.05.28.728509 (full text). Selcuk et al. 2026, bioRxiv, doi:10.64898/2026.06.11.731707 (full text, v1). Mrnjavac et al. 2026, Sci Adv, doi:10.1126/sciadv.aef3128 (full text).
- **The idea.**
  - **Stem-to-stem transfer.** A gene transferred between the bacterial and archaeal stems just after LUCA gives a gene tree that looks like a LUCA split. Wehbi et al. show this for tryptophanyl-tRNA synthetase.
  - **Fused domains.** A family can inherit a LUCA call from one of its domains. Wehbi et al. suggest this happened with trpE in Moody et al. 2024.
  - **Missed homologs.** Selcuk et al. raise the ancestral flagellar set from 24 to about 50 groups, so false absences at depth are common.
- **What's untested.** How often each pattern turns into a wrong LUCA call under Moody's pipeline.
- **Open data.**
  - Wehbi code and data: github.com/sawsanwehbi/Ancient-Tryptophan-Tyrosine-usage.
  - Mrnjavac et al.'s LUCA rule (present in at least 50% of genomes in at least 4 higher taxa in each domain) can run on our simulated genomes as a baseline classifier. Their repository: doi:10.25838/d5p-91.
- **Current study.** #32. Stem-to-stem transfers are probably already within Zombi's transfer settings, so a check of what the grid covers may be enough. The occupancy baseline is cheap to add to the reporting without changing the sealed endpoint.

## 3. Size-matched assembly index on Rutter et al.'s data (bears on #7 and #22)

- **Sources.** Rutter et al. 2026, PNAS, doi:10.1073/pnas.2619198123 (full text). Pagel et al. 2026, J Chem Inf Model, doi:10.1021/acs.jcim.6c00939 (full text).
- **The idea.** Rutter et al. trained a model that predicts assembly index (MA) from flight-style mass spectra. Its error is 0.04 relative MSE, against 0.12 for the best size-only baseline. The paper compares no living and non-living samples. Their own database comparison shows PubChem molecules with higher MA than COCONUT 2.0 natural products at the same bond count. That points the opposite way from "high MA means life", and matches our #7 finding.
- **What's untested.**
  - Whether MA separates biotic from abiotic samples at matched size on their data.
  - Whether "does AI beat size" holds as a classification question, not only a regression one.
- **Open data.** Zenodo doi:10.5281/zenodo.20586263. Code: github.com/croningp/assemblycpp-v5.
- **Current study.** It feeds #22, the red team of the AI positive. A sealed prediction is easy to write: COCONUT mean MA is below PubChem mean MA at every bond count from 10 to 40.

## 4. A positive control for QT45 epistasis-to-contacts (bears on #30)

- **Sources.**
  - Szokoli et al. 2026, bioRxiv, doi:10.64898/2026.08.14.744467 (abstract). Cryo-EM of tC19Z at 3.1 Å.
  - Strutzenberg et al. 2026, bioRxiv, doi:10.64898/2026.08.30.748161 (abstract). Substrate-bound polymerase ribozyme.
- **The idea.** #30 came out negative, but it had no positive control. A polymerase ribozyme with a solved structure gives a known contact map. If our epistasis-to-contacts method cannot recover those contacts from mutational data, the #30 negative says more about the method than about QT45.
- **What's untested.** Whether double-mutant or deep mutational scanning data exist for tC19Z or a close relative. Szokoli et al. used designed compensatory mutations, which is a small, targeted set.
- **Open data.** PDB 37SO and EMDB-78467 (named in the reading notes; not yet opened by us). A mutational dataset is still needed.
- **Current study.** #30 is finished, so this would be a follow-up. It is worth doing only if a mutational dataset turns up.

## 5. Is the "exploration ratio" a sample-size effect? (bears on #22)

- **Sources.** Jirasek et al. 2026, ACS Cent Sci, doi:10.1021/acscentsci.6c00618 (full text). Pagel et al. 2026, J Chem Inf Model, doi:10.1021/acs.jcim.6c00939 (full text).
- **The idea.**
  - Jirasek et al. report ER 0.77-0.96 for non-specific activation and 0.51-0.75 for proteases. But the protease ensembles are tiny: 8 to 36 unique sequences, against up to 1,846 for CDI.
  - Pagel et al. report a per-depth decay exponent beta = 0.499 for natural products against PubChem, without a random-subset null.
- **What's untested.** Whether subsampling the large control ensembles to protease size drops ER to 0.5-0.75. And whether random PubChem subsets of COCONUT size give beta near 0.499.
- **Open data.** Jirasek data on Zenodo and github.com/croningp/peptide_selection (MIT). PubChem and COCONUT are public.
- **Current study.** #22. It is cheap, and either outcome is informative.

## 6. Score the vent route under Tutolo's critique (bears on #4/#5)

- **Sources.**
  - Tutolo 2026, PNAS, doi:10.1073/pnas.2613108123 (abstract only, closed).
  - Baidya et al. 2026, Nat Commun, doi:10.1038/s41467-026-75933-6 (full text).
  - Hoffmann et al. 2026, BBA Bioenergetics, doi:10.1016/j.bbabio.2026.149610 (full text).
  - Lowe et al. 2026, ChemRxiv, doi:10.26434/chemrxiv.15006057/v1 (abstract; full text behind a bot check).
- **The idea.**
  - Add a scored vent-route variant where the steps fail that need a hot pH gradient, FeS walls or vent-made fatty acids.
  - Add a crustal phosphite supply row with Baidya's numbers: about 1 nM in the open ocean, up to 67 µM in a UV-shielded lake, below 0.1 µM in an exposed lake.
  - Lowe et al. suggest Mn2+/Fe3+ or low pH can protect fatty acid vesicles from Mg2+. That would be a conditional exception in the compatibility rule.
- **What's untested.** How much each change moves route success under the hashed rule.
- **Open data.** The paper tables. No new deposit is needed.
- **Current study.** The pathway map (#4/#5/#20/#21). Any rule change must be a new hashed rule version. The Tutolo and Lowe parts should wait for full-text reads.

## 7. Drop comets as a cyanide source in the step tables (bears on #5/#17/#20)

- **Source.** Anslow et al. 2026, Sci Rep, doi:10.1038/s41598-026-74214-y (full text).
- **The idea.** Across 10^5 Monte Carlo runs, all set to favour delivery, the median number of comet impacts that left at least 10 mM HCN on land was 0. 54% of runs had none.
- **What's untested.** How many of our pond and cyanosulfidic step tables credit comets. Whether the routes still close with only atmospheric or crustal HCN sources.
- **Open data.** None needed.
- **Current study.** A step-table check, not a new study.

## 8. Mirror-image nucleotides as a scored input to copying (bears on #4/#5)

- **Sources.**
  - Essex et al. 2026, JACS, doi:10.1021/jacs.6c14723 (abstract). An L-nucleotide at the primer end is a chain terminator.
  - Davisson et al. 2026, ACS Omega, doi:10.1021/acsomega.5c11196 (abstract). Nonenzymatic aminoacylation couples RNA and amino-acid chirality.
- **The idea.** Make "near-homochiral activated nucleotides" an explicit input to the nonenzymatic copying step. The chirality hand-off then becomes a scored gap instead of an assumption.
- **What's untested.** How much enantiomeric excess the copying step can tolerate. The abstracts give no numbers, so the full texts are needed first.
- **Open data.** None yet.
- **Current study.** Pathway map. Low cost.

## Added 2026-11-21 (paper watch)

### 9. Charge balance as its own step in the vent route (bears on #4)

- **Source.** Altair, Hudson et al. 2026, Chem Commun, doi:10.1039/d6cc04072a (full text).
- **The idea.** Electrons cross synthetic vent minerals about 10^4 to 10^6 times more easily than ions (e.g. FeS 1.5e-2 vs 4.97e-7 S/cm). Score "ions keep up with electrons across the wall" as a separate hand-off in the vent step table.
- **What's untested.** Whether any published vent CO2-reduction experiment ran long enough, with a real gradient, for ionic transport to limit it.
- **Open data.** The paper's conductivities; published vent-reactor yields for comparison.
- **Current study.** Step table B3 / #4. Low cost.

### 10. Nucleotide condensates as a compartment and a hydrolysis escape (bears on B3, #4/#5)

- **Source.** Hauf, Dindo et al. 2026, bioRxiv, doi:10.64898/2026.11.18.767475 (abstract only; preprint).
- **The idea.** Polymer-free nucleotide condensates reportedly keep RNA intact for days in acid and push a hammerhead ribozyme toward religation. Add them as a scored option for the compartment step and for the RNA-hydrolysis hand-off in the pond route.
- **What's untested.** Whether the nucleotide, divalent-cation and diol concentrations they need fit our supply rows. The full text is needed first (bioRxiv blocked our client).
- **Open data.** None yet.
- **Current study.** Pathway map. Score as "preprint, one lab" until replicated.

## Added 2026-11-23 (paper watch)

### 11. A size-matched null for "minerals expand prebiotic chemistry" (bears on #6/#23, #4)

- **Source.** Li, Guo et al. 2026, PNAS Nexus, doi:10.1093/pnasnexus/pgag405 (abstract only). Adding mineral-promoted reactions to a 114,476-molecule network more than doubled the pathways to 12 targets and reached 14 targets that were otherwise unreachable.
- **The idea.** Adding reactions always adds routes. Add the same number of random, degree-matched reactions instead of the mineral set, and ask whether the mineral set reaches more targets than that null. This is the same null our #6 RAF test applied to Xavier 2020.
- **What's untested.** Whether the mineral effect beats a size-matched random addition.
- **Open data.** Needs their network and the list of mineral reactions; check the full text and supplement for a deposit first.
- **Current study.** No change to K5. A cheap follow-on to #6/#23 if the data are deposited.

## Added 2026-11-25 (paper watch)

### 12. Two-solver agreement before any assembly-index test on large molecules (bears on #7/#22)

- **Source.** Tang 2026, ChemRxiv, doi:10.26434/chemrxiv.15012760/v1 (abstract only; preprint). On 626,161 COCONUT natural products, the Rust assembly-theory 0.6.1 and the legacy C++ solver correlate at r = 0.9674 but give the same integer MA for only 57.20%.
- **The idea.** Before reopening the "MA ≥ 15" region that our atlas leaves open, compute MA for a random COCONUT subset with assembly-theory 0.7.0 and a second exact solver, keep only molecules where both agree, and check whether the biotic-vs-abiotic result changes when the disagreeing molecules are dropped.
- **What's untested.** Whether solver disagreement is concentrated at high MA, where a biosignature threshold would sit.
- **Open data.** COCONUT 2.0 (open); both solvers are open source.
- **Current study.** None running. A data-quality gate for any future #7/#22 work on large molecules.
