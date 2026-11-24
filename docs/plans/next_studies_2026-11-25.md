# Next studies on open data, ranked (2026-11-25)

Written by a planning agent. Read-only work: nothing was committed, sealed or run.

- **What "opened" means here.** I fetched the full text from Europe PMC, or the file itself, and read the lines quoted. Anything I did not open is marked "not opened".
- **What "blind count" means.** I counted rows, columns, groups and coverage. I did not read any outcome value. Each study below can still be sealed blind.
- **Score.** Impact × decidability × cheapness, each from 1 to 5.
- **Lessons applied from T1 to T10.**
  - No field-geochemistry database is used to judge a laboratory claim (T3, T4, T7).
  - Each study takes a published headline claim, the authors' own deposited data, and a matched null or natural experiment inside that data (T5, T6, T8, T9).
  - Group sizes were counted before design. Where n is small the study says so and starts with a power gate (T2).
  - Everything runs on one laptop core in minutes to a few hours. No dating, no large tree inference (T10).
  - Four of the five studies sit outside LUCA phylogenomics.

## Ranking

| Rank | Study | Score |
|---|---|---|
| 1 | N1. Does ribozyme specificity really rise with activity, or is it the background floor? | 4 × 5 × 5 = 100 |
| 2 | N2. Does the ligase neutral network need higher-order epistasis, or does one global curve do? | 4 × 4 × 4 = 64 |
| 3 | N3. Is the tiered autocatalytic structure of biochemistry more than its degree sequence gives? | 3 × 4 × 4 = 48 |
| 4 | N4. Do formose mixtures under changing flow differ from steady state by more than a repeat run does? | 3 × 3 × 5 = 45 |
| 5 | N5. Is the tryptophan gap between the archaeal and bacterial ancestors more than small-sample scatter? (marginal; gate first) | 3 × 2 × 5 = 30 |

S6 (Roberts 2023 epistasis against tertiary contacts) and S7 (Attwater 2025 growth law) from the 2026-11-24 plan are still unrun and still valid. They would sit between N4 and N5.

---

## N1 (top pick). Does ribozyme specificity really rise with activity, or is it the background floor?

**Claim.** Janzen et al. 2022, Nat Commun, doi:10.1038/s41467-022-31387-0 (opened, PMC9233669):

> "Furthermore, ribozyme activity was positively correlated with specificity, indicating that selection for increased activity would also lead to increased specificity."

> "Promiscuity was observed to decrease as overall activity increased for all families (Fig. 4 and Supplementary Fig. 7)."

Table 1 gives the correlations per family: "Correlations between overall catalytic activity and specificity for each ribozyme family (Pearson's R and Spearman's ρ; n = 1954, p-values < 10^−95 in each case (two-sided))". The promiscuity-index R runs from −0.535 to −0.839 (published values).

**Why it might fail.**
- The promiscuity index is the normalised entropy of a sequence's rates across six substrates. It equals 1 when the rates are equal.
- The paper reports a floor: "The background rate was 0.55 ± 0.18 M−1 min−1", and a peak that "represented a background of catalytically inactive, or nearly inactive, mutants".
- A sequence at the floor on all six substrates has near-equal rates, so its index is near 1 whatever its true preference. An active sequence rises above the floor on some substrates first. A negative correlation then follows from the floor and the noise alone.
- n = 1,954 per family means every sequence in the family is in the correlation, inactive ones included.
- The claim feeds the genetic-code story (specificity as a free by-product of selection for activity), so it matters beyond this paper.

**Data (open, no login).**
- Source Data, 17.6 MB: https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-022-31387-0/MediaObjects/41467_2022_31387_MOESM3_ESM.xlsx (opened; structure only).
- Code: https://github.com/ichen-lab-ucsb/WFLIVM_k-Seq (file list opened; includes `PromIndexPlot.py`).
- Raw reads are on Dryad, doi:10.25349/D92C9C, 85 GB. Not needed and not opened (the file API returned 401).

**Decidability check (blind; no rate, index or correlation in the file was read).**
- Sheet "Figure 4": 9,770 rows. Columns: `seq`, `Family`, six rate columns (`r_BWO`, `r_BFO`, `r_BLO`, `r_BIO`, `r_BVO`, `r_BMO`), `all_sum`, `I`.
- Five families, 1,954 sequences each.
- Sheet "Figure 2": 9,770 rows × 128 columns. For each substrate it holds the fitted `k`, `A` and `kA`, and bootstrap mean, standard deviation and 2.5 / 50 / 97.5 percentiles for each. The measurement noise per sequence and substrate is therefore in the deposit.
- Not yet counted, because it means reading rates: how many sequences per family are above the paper's activity threshold on two or more substrates. That count is the gate below.

**Gate.**
- Recompute `I` and the Table 1 correlations from the six rate columns. Match the published R within 0.02 for all five families.
- Count sequences with a rate above the paper's threshold (5) on at least two substrates. Need at least 200 per family in at least three families. If not, report "the claim rests on sequences at the floor" as the finding and stop.

**Kill rule.**
- R_adj = correlation of log activity with the index, per family, computed only on sequences above threshold on at least two substrates, with the background rate subtracted and rates floored at zero.
- R_null = the same statistic on simulated data: each sequence keeps its total activity, its above-background preference profile is swapped with that of a random sequence in the same family, the background is added back, and noise is drawn from the deposited bootstrap standard deviations. 2,000 draws.
- **Kill:** in at least four of five families, the observed full-sample R lies inside the central 95% of R_null, or the 95% bootstrap interval of R_adj includes 0.

**Null.** The profile swap removes any real link between activity and preference but keeps the floor, the noise and the activity distribution. Whatever correlation it yields is produced by the index's definition. Planted checks: a simulated family with a fixed preference profile at every activity level must return R_adj near 0; one where the preference sharpens with activity must return a clearly negative R_adj.

**Support rule.** In at least four of five families, R_adj ≤ −0.3 with an interval that excludes 0, and the observed R lies below the 2.5th percentile of R_null.

**Cost.** Laptop, minutes. One xlsx, no alignment or model fitting.

**Prior art checked.**
- Europe PMC, `ribozyme promiscuity specificity activity correlation background k-Seq aminoacylation`: 3 hits, only the paper itself is relevant.
- Europe PMC citation list for the paper: 19 citing records read by title. None is a reanalysis of the activity and specificity correlation. Charest et al. 2023 (RNA) uses the landscape for epistasis; Kenchel et al. 2024 is on chirality.
- arXiv, `ribozyme AND promiscuity`: query returned no entries.

---

## N2. Does the ligase neutral network need higher-order epistasis, or does one global curve do?

**Claim.** Rotrattanadumrong and Yokobayashi 2022, Nat Commun, doi:10.1038/s41467-022-32538-z (opened, PMC9385714):

> "In generation 8, almost all neutral mutants identified were expected to be deleterious under the epistasis-free model. This indicated that the neural network was able to learn higher-order, nonlinear mutational effects, and identify distant neutral mutants that would have been inaccessible through in silico selection, mutation, and recombination alone."

The abstract adds that the neutral paths "might be predicted using only information from lower-order interactions".

**Why it might fail.**
- "Epistasis-free" here means additive on the measured scale. An additive latent score passed through one saturating curve is also free of specific interactions, and it predicts that many mutants additive-on-the-measured-scale calls dead are in fact neutral.
- Our QT45 study (#30) found exactly this on another ribozyme: the global curve lifted R² from 0.655 to 0.910 and pair terms added 0.0005.
- If the global-curve model matches the network on the held-out generations, the data do not show higher-order epistasis.

**Data (open, Apache-2.0).**
- Zenodo doi:10.5281/zenodo.6945203, one zip of 136.7 MB: https://zenodo.org/api/records/6945203/files/Rotrattanadumrong_2022_ligase_ribz_evolution.zip/content
- The zip is over the 20 MB limit as a whole. I listed its directory by range request (138 entries) and pulled four members one at a time. The study should do the same.

**Decidability check (blind; no activity value was read).**
- `Filtered_reads_files/Filtered_LibWT_Mut_R1_R2_QS20_tolerance_1.csv`, 10.6 MB: 65,536 rows, the complete 2^16 set between the two genotypes. Columns include `Sequences`, `RA_1`, `RA_2`, `Mean_RA`, `HD_WT`, `HD_Mut`, `Generation`, `Algorithm`. Two replicates, so a noise ceiling can be computed.
- `Filtered_Lib1…`: 10,000 rows, Hamming distance 0 to 3.
- `Filtered_Lib8…`: 11,960 rows, Hamming distance 6 to 19.
- `Filtered_Lib7_MLP…`: 1,000 rows, Hamming distance 3 to 10.
- The paper states the network was "trained on 20,920 variants from generations 1–6" with 8,967 held out, and uses relative activity ≥ 0.2 as "neutral".
- Not opened: the Lib2 to Lib7 files (0.3 to 1.7 MB each; listed only). The `sampled_paths*.txt` files are Python pickles and must not be loaded.

**Gate.**
- Rebuild the generation 1 to 6 training set and match the stated 20,920 within 2%.
- Reproduce the paper's statement for the additive-on-measured-scale model on generation 8 (most neutral variants predicted below 0.2). If either fails, stop.

**Kill rule.**
- Model G = additive latent score from position-by-base terms plus one monotone curve (sigmoid), fitted on generations 1 to 6 only.
- Score on generation 7 and 8 variants: average precision for calling RA ≥ 0.2, and Spearman ρ with measured RA.
- Ceiling = the same scores for replicate 1 predicting replicate 2 in the 2^16 library.
- **Kill:** model G calls at least 80% of the measured generation 8 neutral variants neutral, and its average precision is within 0.05 of a small network trained on the same data (rebuilt here, since the authors' per-variant predictions were not located in the deposit).

**Null.** Labels shuffled within Hamming-distance bins give the floor for average precision; this stops distance from the wild type from passing as skill. Planted checks: data simulated from a pure global-curve model must give "kill"; data with planted pairwise terms of the size needed to flip 30% of calls must not.

**Support rule.** Model G calls under 50% of generation 8 neutral variants neutral, and adding pair terms or the network lifts average precision by 0.10 or more on held-out generations.

**Cost.** Laptop, under an hour. Fits are logistic-style regressions on about 21,000 rows and at most a few hundred parameters.

**Prior art checked.**
- Europe PMC, `ligase ribozyme neutral network global epistasis nonlinearity additive model`: 1 hit, the paper.
- Citation list (26 records read by title). Two could overlap and were not opened: Martí-Gómez et al. 2026 (Mol Biol Evol, "Inference and Visualization of Complex Genotype-Phenotype Maps") and Faure et al. 2024 (PLoS Comput Biol, Walsh-Hadamard extension). Open both before sealing.

---

## N3. Is the tiered autocatalytic structure of biochemistry more than its degree sequence gives?

**Claim.** Peng, Linderoth and Baum 2022, PLoS Comput Biol, doi:10.1371/journal.pcbi.1010498 (opened, PMC9491600):

> "We found that the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs converting simple materials and energy to more complex species."

The paper reports "304 of the 4186 non-tier-0 species are singleton supported seeds able to induce a tier-1 SDAS" and three nested groups in the biochemical network.

**Why it might fail.**
- Any large reaction network with a few hub species (water, ATP, NAD) may show seeds, tiers and nesting under this expansion rule.
- I searched the full text for "rewir", "null", "shuffl" and "random network" and found no randomised comparison.
- If rewired networks give the same seed counts and nesting, the shared properties say little about life or its origin.

**Data (open, CC BY).**
- S1 Table (abiotic), 44.8 KB: https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1010498.s006 (opened).
- S2 Table (biochemical), 407 KB: https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1010498.s007 (opened).

**Decidability check (blind; structure only, no expansion was run).**
- S1: 717 reaction rows. Columns `Serial`, `Reaction_Category`, `Reaction_ID`, `Reactant_name`, `Reactant_stoi`, `Product_name`, `Product_stoi`, `Note`.
- S2: 8,402 reaction rows. Columns `Serial`, `Reaction_entry`, `Reactants`, `Reactant_stoi`, `Products`, `Product_stoi`, `Note`.
- Both match the counts in the text ("277 species and 717 unidirectional reactions"; "4216 species and 8402 reactions").
- The repo already has rewiring and expansion code in `experiments/raf_null`.
- Not checked: the tier-0 food list as a machine-readable file. It may need to be typed from the text.

**Gate.** Reproduce the 304 singleton seeds within 5% and the three nested group sizes (301, 357, 1,414 species) within 5%. If the expansion rule cannot be rebuilt from the paper, stop.

**Kill rule.**
- Statistics: number of singleton seeds; number of distinct seed-induced sets; share of pairs of sets that are nested; size of the largest set.
- Null: 200 rewired networks per database. Swap products between reactions so each species keeps its count as reactant and as product, and each reaction keeps its number of reactants and products. Food set unchanged.
- **Kill:** in the biochemical network, at least three of the four statistics lie inside the central 95% of the rewired values.

**Null.** Rewiring keeps the hubs, the size and the food set, and breaks only the specific chemistry. A second, stricter null also keeps element balance by swapping only between reactions with the same product formula count; report both. Planted check: a network built by hand with three nested autocatalytic cores must fall outside the rewired range.

**Support rule.** At least three of four statistics lie outside the central 99% of both nulls, in the same direction in both databases.

**Cost.** Laptop. About 4,186 seed expansions per network × 200 networks. Time one network first; if it takes more than 60 s, cut to 100 rewires and sample 1,000 seeds.

**Prior art checked.**
- Europe PMC, `"self-propagating" autocatalytic biochemical network randomized null rewired "network expansion"`: 0 hits.
- Citation list (24 records read by title). Huson, Xavier and Steel 2024 (J R Soc Interface) and Golnik et al. 2026 (J Theor Biol) are on related RAF structure; neither title signals a rewiring test of this paper. Not opened.

---

## N4. Do formose mixtures under changing flow differ from steady state by more than a repeat run does?

**Claim.** van Duppen et al. 2023, J Am Chem Soc, doi:10.1021/jacs.3c00908 (opened, PMC10080678):

> "Surprisingly, the product compositions of the formose reaction under dynamic conditions deviate significantly from those under steady state conditions."

> "Again, we observed average concentrations of compounds which deviate from steady-state averages (3, 5, 7, and 11; p ≤ 1 × 10^–4, in all compound series; see Figures S12 and S13)."

**Why it might fail.**
- Samples within one flow run are taken in sequence and are likely autocorrelated. A test that treats 45 samples as 45 independent draws overstates significance.
- The honest yardstick is the gap between two runs at the same settings. The deposit holds two such pairs.

**Data (open, BSD-3-Clause).**
- https://github.com/huckgroup/Formose_2022 (file list opened).
- `info_files/list_exp.csv` and `info_files/compound_information.csv` (opened; 31 compounds).
- 13 runs at `Extended_data_GH/EXP0NN/Analysed_data/EXP0NN_Data.csv`, 0.6 to 2.9 MB each (opened; structure only; files are Latin-1).

**Decidability check (blind; no concentration was read).**
- Each run has about 44 to 51 samples × about 20 compound columns.
- Two repeat pairs at identical settings: EXP001 and EXP010 (both steady state); EXP003 and EXP012 (both at the same fluctuation setting).
- Other steady-state runs: EXP004 and EXP007, at other formaldehyde levels.
- The authors' own comparison sets are [4, 5, 6], [1, 2, 3], [7, 8, 9] and [10, 12, 11].
- Weak point: two repeat pairs is a small base for a noise estimate. The gate handles this.

**Gate.** For each compound, compute the difference in run means for the two repeat pairs with a moving-block bootstrap interval. If the two pairs disagree in size by more than a factor of 3 for most compounds, the repeat noise is not pinned down; stop and report "cannot decide".

**Kill rule.**
- D_dyn = absolute difference in mean concentration, dynamic run against its steady-state partner, per compound, in units of the pooled within-run standard deviation.
- D_rep = the same for the repeat pairs.
- **Kill:** for the four compounds named in the quote, the median D_dyn is less than 2 × the larger D_rep, and block-bootstrap intervals for D_dyn − D_rep include 0 in at least three of four.

**Null.** Repeat runs at identical settings give the size of a shift when nothing was changed. The block bootstrap (block length from the autocorrelation time, set before reading means) keeps serial correlation. Planted check: adding a known shift of 3 pooled standard deviations to one repeat run must be detected.

**Support rule.** For at least three of the four compounds, D_dyn exceeds 3 × the larger D_rep and the interval for D_dyn − D_rep excludes 0.

**Cost.** Laptop, minutes.

**Prior art checked.**
- Europe PMC, `formose dynamic environment replicate reproducibility oscillating flow`: 1 hit, unrelated.
- Citation list (25 records read by title). Follow-ups from the same group (Baltussen et al. 2024, Nature; de Jong et al. 2025, Angew Chem) build on the result. No independent reanalysis by title. Not opened.

---

## N5. Is the tryptophan gap between the archaeal and bacterial ancestors more than small-sample scatter? (marginal; gate first)

**Claim.** Wehbi et al. 2026, bioRxiv, doi:10.64898/2026.05.28.728509 (abstract opened through Europe PMC; full text **not opened**, the bioRxiv XML returned 429):

> "However, ancestral sequence reconstruction suggests that Archaea were depleted for W while Bacteria were not, and enzymes essential for W biosynthesis emerged in Bacteria."

**Why it might fail.**
- Tryptophan is the rarest amino acid, so its frequency in a small set of reconstructed domains is noisy.
- The archaeal side is small (counts below). A random draw of the same size from the bacterial side may often look as depleted.
- Our library notes record that a large share of the reconstructed archaeal tryptophans sit at low-confidence sites.

**Data (open; no licence file in the repository).**
- https://github.com/sawsanwehbi/Ancient-Tryptophan-Tyrosine-usage (56 files; list opened).
- Opened, structure only: `Clan_data_ancestralAAC_NQarc.csv`, `AncientPostLUCA.csv`, `Prokaryotic_phylostrata.csv`, `laca_lbca_df_arc.csv`, `W_freq_df_ArcBac.csv`, `Conserved_W.csv`.
- Not opened: `pfam_asr_aac_NQArc_0.4_0.35preLBCA` (3.5 MB) and `archaea_alignments.zip` (21.6 MB, over the limit).

**Decidability check (blind; no frequency or ratio was read).**
- `Clan_data_ancestralAAC_NQarc.csv`: 4,173 clans × 26 columns (20 amino acids, lengths, `Clan_ancestor`). Classes: LUCA 309, pre-LUCA 136, post-LUCA 1,232, modern 2,234, unclassifiable 262.
- `Prokaryotic_phylostrata.csv`: 1,988 clans. Pre-LACA 31, pre-LBCA 251, modern Archaea 161, modern Bacteria 1,545.
- `AncientPostLUCA.csv`: 3,055 Pfams. LACA 222, pre-LACA 63, LBCA 2,195, pre-LBCA 575.
- The archaeal ancestor side is 31 clans or 63 Pfams. That is above the T2 failure size (9) but thin for a rare amino acid.

**Gate.** Before reading any W value, simulate: draw 31 clans from the 251 pre-LBCA clans with tryptophan replaced by a permuted other rare amino acid column (C or H), and find the smallest true depletion that a size-matched test detects with 80% power. If that is larger than a 40% relative depletion, stop: the data cannot decide.

**Kill rule.**
- T = ratio of length-weighted W frequency, pre-LACA clans over pre-LBCA clans.
- Null: 10,000 draws of 31 clans from the pre-LBCA set, matched on concatenated length tercile; T recomputed against the remainder.
- **Kill:** observed T lies inside the central 95% of the null, or C, H or M show a ratio as far from 1 as W does.

**Null.** Size-matched draws from the bacterial side show how depleted a 31-clan sample looks by chance. The other rare amino acids show whether the gap is specific to W or shared by anything rare. Planted check: removing 40% of W from a random 31-clan draw must be detected.

**Support rule.** Observed T below the 1st percentile of the null, W the most extreme of the 20 amino acids, and the result holds when sites under 70% reconstruction confidence are dropped (needs the unopened 3.5 MB file to carry site confidence; unverified).

**Cost.** Laptop, minutes.

**Prior art checked.** Europe PMC, `tryptophan Archaea ancestral reconstruction depleted LUCA amino acid usage`: 21 hits; the preprint, Wehbi et al. 2024 (the parent study, tested in T5), and James et al. 2021 (eLife; amino-acid trends with protein age; not opened). No reanalysis of the preprint found.

---

## Looked at and not proposed

- **Jirasek et al. 2026 (doi:10.1021/acscentsci.6c00618; opened, PMC13720923), IDEAS #5.** The claim is sharp ("nonspecific activation conditions yield exploration ratios of 0.77–0.96, whereas sequence-selective proteases yield lower ratios of 0.51–0.75") and the paper says each row "represents a single experimental trajectory". The size-matched test needs per-sequence tables, which sit in `experimental/MolecularAssembly.parquet` at https://github.com/croningp/peptide_selection (41.3 MB, over the limit, not opened). `experimental/labbook.csv` was opened: 66 experiments, 8 columns. This becomes a proposal the moment a 41 MB download is allowed.
- **Lai, Liu and Chen 2021 (doi:10.1073/pnas.2025054118; opened, PMC8166191).** "Highly active ribozymes benefit disproportionately more from encapsulation" is a good T8-style target. The Dryad files (doi:10.5068/D1PX0K) are 43 MB and up, and the file API returned 401.
- **Wang et al. 2022 (doi:10.1186/s12864-022-08435-6).** The frameshift-tolerant genetic code claim was already answered by Xu and Zhang 2021 (doi:10.1093/molbev/msab164; abstract opened).
- **Crapitto et al. 2022 (doi:10.1002/ece3.8930; opened).** Eight studies; already uses random-cluster nulls; supplement not reachable.
- **Kenchel et al. 2024 (doi:10.1038/s41467-024-52362-x; source data opened).** About 15 ribozymes. Too few.
- **Protocells: Salibi et al. 2023 (doi:10.1038/s41467-023-36940-z) and Shinoda et al. 2025 (doi:10.1039/d5sc04710b).** Source tables opened. Three to six replicates per condition; demonstrations, not sharp claims.
- **Asche et al. 2021 (doi:10.1038/s41467-021-23828-z).** Supplement zip is 868 MB; about 10 experiments.
- **Impact delivery: Anslow et al. 2026 (doi:10.1038/s41598-026-74214-y; opened, PMC13716819).** Code and outputs are open (github.com/richard17a/comet_delivery_hcn; listed). Any kill would rest on assumed model inputs, which is the T1 mistake.
- **Nonenzymatic copying: Duzdevich et al. 2021 and 2024 (doi:10.1093/nar/gkab173, doi:10.1093/nar/gkae982).** Data on view-only OSF links. Kudella et al. 2021: sequencing data "available upon request". Calaça Serrão et al. 2024 (doi:10.1093/nar/gkad1190): figshare zips of 23.6 and 30.2 MB, over the limit, not opened.
- **Meteorites and returned samples.** Again no large formula or abundance table that I could verify as downloadable (Schmitt-Kopplin et al. 2023 deposits PDFs only).
- **Goldford et al. 2019 network expansion.** Networks are open (github.com/segrelab/BoundaryConditionsForAncientMetabolism; listed). I found no claim whose null is not set by a definition.

## Housekeeping

- No download broke the 20 MB limit. Large zips were handled by listing the directory with a range request and fetching single members.
- Blocked and not worked around: Dryad file API (401), bioRxiv full-text XML (429), Europe PMC supplementary-file endpoint (500).
- Everything under the scratch directory in `/tmp` is deleted at the end of this run. The addresses above are enough to fetch it again.
- User-Agent was `open-research-site/1.0` on every request. No personal detail was sent.
