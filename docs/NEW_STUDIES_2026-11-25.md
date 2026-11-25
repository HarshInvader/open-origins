# New studies on open data, ranked (2026-11-25, second list)

Written by a planning agent. Read-only work: nothing was committed, sealed or run. This file is the only thing written to the repo.

- **What "opened" means here.** I fetched the full text from Europe PMC or the publisher page, or the data file or its listing, and read the lines quoted. Anything I did not open is marked "not opened".
- **What "blind count" means.** I counted rows, columns, groups, file members or structural properties. I did not read any outcome value, except where a line says so. Each study below can still be sealed blind.
- **Score.** (Chance the result changes how a route is viewed, 1 to 5) × (feasibility, 1 to 5).
- **Lessons applied from T1 to T16.**
  - Serial samples are not replicates (T15). Where a paper has one lineage or one run per arm, the study says so and treats rounds or samples as repeated measures, not as independent units.
  - An index that shares noise with the thing it is compared to needs a noise correction or a split-replicate design (T8, T12).
  - Network nulls keep degrees, and now also atoms (T14).
  - Every study has a power gate before the seal (T16).
- **One access finding that matters for the whole queue.** Dryad's file API returns 401 and its download link 403 for scripts. The same datasets are served openly by Zenodo, which now hosts Dryad's files: query `https://zenodo.org/api/records?q=doi:"<dryad doi>"` and use the `files/.../content` links. I fetched one file this way (a 52 KB README) and listed a 48 MB zip by range request. This reopens Lai et al. 2021, which the last plan dropped for this reason.

## Ranking

| Rank | Study | Route | Score |
|---|---|---|---|
| 1 | U1. T14 follow-up: do the nested autocatalytic tiers survive an atom-conserving null? (Peng, Linderoth & Baum 2022) | autocatalytic sets, metabolism first | 4 × 5 = 20 |
| 2 | U2. Do active ribozymes really gain more from encapsulation, and is the encapsulated landscape really more rugged, or is one condition just noisier? (Lai, Liu & Chen 2021) | protocells, RNA world | 4 × 5 = 20 |
| 3 | U3. Are "over half" of the HDV-to-ligase genotypes really dual-function, or is that a read floor? (Bendixsen et al. 2019) | RNA world, evolvability | 3 × 5 = 15 |
| 4 | U4. Did the low-fidelity lineage lose the hammerhead because of fidelity, or because selection was weaker? (Papastavrou, Horning & Joyce 2024) | RNA world, error threshold | 5 × 3 = 15 |
| 5 | U5. Are early expansion steps enriched in metal enzymes within pathways, at reaction level? (Goldford et al. 2024) | metabolism first | 3 × 4 = 12 |
| 6 | U6. Which arrows of the five-member replicator network survive replicate noise? (Mizuuchi, Furubayashi & Ichihashi 2022) | RNA world, replicator networks | 3 × 4 = 12 |
| 7 | U7. Do formose compositions differ between environments by more than repeat runs differ? (Robinson et al. 2022) | prebiotic chemistry, formose | 3 × 3 = 9 |
| 8 | U8. Does a nested, sample-family-held-out test keep the 90% biosignature accuracy? (Cleaves et al. 2023; peripheral) | biosignatures | 2 × 4 = 8 |
| 9 | U9. Is the "frustrated" aminoacylation landscape a property of the landscape or of what the selection let us see? (Pressman et al. 2019; gate first) | RNA world, evolvability | 3 × 2 = 6 |

U1 and U2 tie. U1 goes first because its inputs are already in the repo and its blind count is done. N5 from the earlier list (Wehbi 2026, tryptophan) is still unrun and would sit below U7.

---

## U1 (top pick). Do the nested autocatalytic tiers survive an atom-conserving null?

**Claim.** Peng, Linderoth & Baum 2022, PLoS Comput Biol 18:e1010498, doi:10.1371/journal.pcbi.1010498 (PMC9491600; full text saved in the repo under `experiments/t14_autocatalytic_tiers/raw/europepmc/`, quotes as in the T14 prereg):

> "These SDASs are nested, with SDAS-bio-1c including the entirety of SDAS-bio-1b, which includes the entirety of SDAS-bio-1a."

> "We found that the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs converting simple materials and energy to more complex species."

**Where T14 left it.** Degree-preserving rewires give one set and no nesting in essentially every copy, so T14's sealed verdict was support. The T14 result file names the gap itself: rewired reactions do not conserve atoms, so "tiers are specific" could mean "biochemistry is organised" or only "real chemistry balances its atoms and random chemistry does not".

**Data (all open; the first two are already in the repo).**
- Network: S2 Table (8,402 reactions, 4,216 species) and the food set, as hashed in `docs/prereg/t14_autocatalytic_tiers.md`.
- Formulas: KEGG REST, `https://rest.kegg.jp/get/<up to 10 compound ids>`, FORMULA line (opened; 422 calls, about 6 minutes at a polite rate). KEGG REST is free for academic use; keep the formulas in the gitignored `raw/` folder, not in the repo.

**Decidability check (blind; structure only, no null was drawn).**
- 4,208 of 4,216 species have a plain formula (no R group, no "n").
- 8,152 of 8,402 reactions balance every element exactly with those formulas. 224 do not balance and 26 touch a species without a formula. So 97% of the network can be rewired under exact atom conservation; the other 250 reactions stay fixed.
- Not yet counted: how much freedom the atom rule leaves. That is the gate below.

**The null (three levels, from weakest to strongest constraint).**
- **Null A, isomer swap.** A product stub may only be exchanged with a stub of a species with the same formula. Atom balance is kept exactly. Mixing is limited to isomer classes.
- **Null B, half-reaction swap.** Write each balanced reaction as two coupled halves with opposite formula differences (for example a main conversion and a cofactor conversion such as ATP to ADP). Halves are exchanged between reactions that share the same formula difference. Every rewired reaction is atom-balanced; every species keeps its reactant and product counts within its class.
- **Null C, strict.** Null B, with tier-0 species and the top 1% of species by degree frozen, as in T14's strict null.
- All three keep the tier-0 system exactly, as T14's C1 correction requires, and rebuild each reverse reaction as the exact reverse.

**Gate (before the seal).**
1. Reproduce the T14 gate numbers (304 seeds; sets of 301, 357 and 1,414 species).
2. Mixing: under Null B, at least 30% of the 8,152 balanced reactions must differ from the original after rewiring, and the mean Jaccard overlap between a rewired copy's reaction set and the real one must be below 0.8. If Null B cannot reach this, the atom rule leaves too little freedom and the study is "not decidable"; report the count and stop.
3. Planted check on synthetic atom-balanced networks (T14's generator already balances mass): three planted nested cores must be flagged against Nulls A to C in at least 8 of 10 replicates, and a same-degree network without cores must be flagged in at most 1 of 10.

**Kill rule (of the "biological organisation" reading).** The real network's number of sets (3) and nested share (1.0) both lie inside the central 95% of Null B. Atom bookkeeping alone then gives nested tiers, and T14's support is downgraded to "real chemistry is tiered".

**Support rule.** Both statistics lie above the central 99% of Nulls B and C. The tiers are then a feature of which balanced reactions biology uses, not of balance itself.

**Between.** Report "partly", with where the real values fall. Null A is reported only.

**Also report.** Seed count and largest set against each null. T14 found rewired networks are more autocatalytic (3 to 4 times more seeds). Whether that also holds under atom balance is the second finding.

**Power concern.** The main risk is low mixing, not sample size: if most formula-difference classes hold one or two reactions, Null B is nearly the real network and can never kill. Gate 2 measures this before any real null is scanned. The abiotic network (717 reactions, species named by formula) is too small for hierarchy and stays reported-only.

**Cost.** T14 took about 1.7 h for 400 rewires. Three nulls at 200 draws each: 3 to 4 laptop hours, detached and resumable.

**Prior art checked.** `experiments/t14_autocatalytic_tiers/PRIOR_ART.md` found no randomised test of any kind. New search today: Europe PMC, papers citing PMID 36084149 that mention "mass balance", "element balance", "atom-balanced", "stoichiometric consistency" or "mass-balanced": 0 hits. No one has run this.

---

## U2. Do active ribozymes gain more from encapsulation, and is the encapsulated landscape more rugged, beyond a difference in measurement noise?

**Claim.** Lai, Liu & Chen 2021, PNAS, doi:10.1073/pnas.2025054118 (opened, PMC8166191). Abstract:

> "In addition, highly active ribozymes benefit disproportionately more from encapsulation. The asymmetry in fitness gain broadens the distribution of fitness in the system. Consistent with Fisher's fundamental theorem of natural selection, encapsulation therefore leads to faster adaptation when the RNAs are encapsulated inside a protocell during in vitro selection."

Results:

> "The predominance of |εInV| > |εOutV| indicates greater epistasis when encapsulated."

> "For all ribozyme families, the γd values are smaller in the encapsulated condition than the nonencapsulated condition, indicating a less-correlated, more-rugged landscape for the ribozyme fitness peak when encapsulated"

**Why it might fail.**
- "Benefit" is the encapsulated activity over the non-encapsulated one, compared against activity. The two share a term, so noise alone makes a trend (the T12 problem).
- Larger mutational effects, larger epistasis and lower γd are all what extra measurement noise produces. The two conditions were sequenced separately: the paper gives "1,399,829 and 1,073,520 sequence reads" and "81,065 … and 59,665 … unique sequences" as analysable, with a filter of more than 10 reads on average. That is a thin read budget per sequence, and it differs between conditions.
- The read filter is applied per condition, so the analysed set is selected on a noisy quantity.

**Data (open, CC0).** Dryad doi:10.5068/D1PX0K, served by Zenodo record 4706159 (listing opened).
- `InV-kSeq-counts.zip` (47.6 MB) and `OutV-kSeq-counts.zip` (54.1 MB). I listed the first by range request: 44 members, per-sample count files `BYO-<conc>-<rep>_counts.txt`, three replicates at each substrate concentration. No count was read.
- `InV-kSeq-matlab.zip` and `OutV-kSeq-matlab.zip` (43 and 35 MB): the authors' fitting code. The fastq zips (15 GB each) are not needed.

**Gate.**
1. Refit k_s·A_s from the counts and reproduce the per-family r² of encapsulated against non-encapsulated activity (0.9546, 0.9401, 0.7558, 0.5705, 0.8593) within 0.05, and the analysable counts within 5%.
2. Power: plant a slope of 1.15 (log-log) on simulated sequences with the real read depths and the real triplicate scatter; the support rule must fire in at least 80% of runs, and a planted slope of 1.00 must fire in at most 5%.

**Kill test 1 (disproportionate benefit).**
- Fit activity three times, once per replicate set. Take the non-encapsulated activity from replicate 1 as x, and the benefit from replicates 2 and 3, so x and the ratio share no noise. Rotate the roles.
- Estimate the errors-in-variables slope of log encapsulated on log non-encapsulated activity per family, with SIMEX on the bootstrap noise as a cross-check.
- **Kill:** the 95% interval for the slope includes 1 in at least 3 of the 5 families, and the pooled slope is below 1.05.
- **Support:** lower bound above 1.05 in at least 4 of 5 families.

**Kill test 2 (ruggedness and epistasis).**
- Null: an additive landscape per family (the paper's own multilinear model), with noise drawn at each sequence's measured replicate scatter in each condition. This gives the share of double mutants with |εInV| > |εOutV|, and the γd gap, expected from noise alone.
- Second arm: thin the less noisy condition's reads until the two conditions have equal median replicate scatter, then recompute.
- **Kill:** the observed share and the γd gap both lie inside the central 95% of the noise-only null, or vanish (interval includes 0.5 and 0) after noise matching.
- **Support:** both lie outside the central 99% and survive noise matching.

**Power concern.** Low-activity sequences cannot have k and A separated (the paper says so) and sit near a floor. The decision should use sequences with at least 100 mean reads (6,711 in the paper) and report the rest. If triplicate scatter is dominated by a per-sample offset, as in T16, the split-replicate design loses its independence; gate 2 will show this.

**Cost.** About 100 MB of downloads. Refitting 80,000 curves three times with numpy: under an hour. No MATLAB needed.

**Prior art checked.** Europe PMC, papers citing PMID 34001592 with encapsulation, protocell, landscape, noise or reanalysis in the title: 20 hits, all reviews or new experiments (for example Saha, Choi & Chen 2024, doi:10.1021/acs.accounts.4c00174; Charest et al. 2023, doi:10.1261/rna.079541.122). Titles only. No reanalysis found.

---

## U3. Are "over half" of the genotypes between the HDV ribozyme and a ligase really dual-function?

**Claim.** Bendixsen, Collet, Østman & Hayden 2019, PLoS Biol, doi:10.1371/journal.pbio.3000300 (opened, PMC6555535):

> "Based on this cutoff, we find that over half the genotypes (9,032) can perform both functions (Fig 2B). Specifically, we detected HDV activity for 9,032 of the genotypes and Ligase activity for 16,384 genotypes."

> "The high frequency of dual-function intersection sequences in our data supports the idea that ancient genes that duplicated and enabled radiation events [55] may be characterized by both significant functional overlaps and a robust genotype network."

**Why it might fail.**
- Ligase activity is reported for every one of the 16,384 genotypes. A value that is never zero looks like a floor.
- The cutoff is "detected as active at least 3 times in our data, once in each replicate". The authors argue that a sequencing error from a neighbour would have to recur three times. But error and PCR recombination are rates, not rare events: a genotype with highly active one-mutation neighbours receives spill-over reads in every replicate.
- The authors' own leak check is a frequency-against-fitness correlation, which does not test neighbour spill-over.

**Data (open).** S1 Data, 3.05 MB xlsx, `https://journals.plos.org/plosbiology/article/file?type=supplementary&id=10.1371/journal.pbio.3000300.s028` (opened; header rows only).
- Sheet "Replicate Details": 16,384 genotypes × (HDV: fitness, cleaved, uncleaved for replicates 1 to 3; Ligase: ligated, unligated for replicates 1 to 3). So raw counts per replicate are there.
- Code: gitlab.com/devinbendixsen/innovation_ribozyme_fls (listing opened). Raw reads: ENA PRJEB30802 (not needed, not opened).

**Gate.** Recompute both fitness columns of the "Fitness Table" sheet from the replicate counts (correlation ≥ 0.99), and reproduce 9,032 within 2%.

**Kill rule.**
- For each genotype and replicate, predict the ligated (and cleaved) count expected from spill-over: a rate ε times the summed product counts of its 14 one-mutation neighbours. Fit ε on the genotypes in the bottom tenth of ligase fitness, in replicate 1 only, and apply it to replicates 2 and 3.
- A genotype is "active above the floor" if its product count exceeds the spill-over expectation in replicates 2 and 3 at a 1% Poisson tail each.
- Reliability arm: among genotypes below the median ligase fitness, the rank correlation of ligase fitness between replicates 2 and 3.
- **Kill:** fewer than 25% of the 9,032 remain dual-function above the floor, and the low-half replicate correlation is below 0.2.
- **Support:** at least 75% remain, and the low-half correlation is at least 0.5.

**Null that rules out a result by definition.** Planted check on the real count structure: (i) assign true ligase activity to a random 10% of genotypes and fill the rest by spill-over only; the test must return about 10%. (ii) Give all genotypes weak true activity with no spill-over; the test must keep them.

**Power concern.** The spill-over rate is fitted on the same data, so it can absorb real weak activity and over-kill. The planted check (ii) measures this. Read depth is fixed (the paper gives a mean of 369 reads per genotype in the HDV library), so the weakest activities cannot be separated from zero by any method; the result should be stated as a range ("between X and Y genotypes are dual-function").

**Cost.** One 3 MB file. Minutes.

**Prior art checked.** Europe PMC, papers citing PMID 31136568 that mention reanalysis, background, false positive, detection limit, noise, cross-contamination or promiscuity: 22 hits; titles are new landscapes and reviews (for example Wagner 2023, doi:10.1038/s41467-023-39321-8; Schmutzer, Dasmeh & Wagner 2024, doi:10.1007/s00239-024-10161-4). Titles only; none reads as a re-test of the 9,032.

---

## U4. Did the low-fidelity lineage lose the hammerhead because of fidelity, or because selection was weaker?

**Claim.** Papastavrou, Horning & Joyce 2024, PNAS, doi:10.1073/pnas.2321592121 (opened, PMC10945747):

> "This size was found to place the hammerhead above the error threshold for the low-fidelity polymerase, but within the error threshold for the high-fidelity polymerase."

> "The low-fidelity polymerase was unable to maintain the essential features of the hammerhead motif, with heritable information becoming lost to entropic decay after only a few generations of evolution."

**Why it might fail.** This is the first laboratory demonstration of an error threshold with an RNA polymerase ribozyme, and the two arms differ in more than fidelity.
- One lineage per polymerase. Eight rounds in a row are not eight replicates.
- "Two parallel lineages of RNA-catalyzed evolution were carried out, using either the 52-2 or 71-89 polymerase in the presence of either 200 or 50 mM Mg2+, respectively".
- The authors say selection differed: the 52-2 lineage's persistence "is also due to imperfect stringency of selection. Catalytically inactive RNAs can still be released from the streptavidin-coated beads due to uncatalyzed cleavage". If background release is a fixed leak, the low-yield arm has weaker effective selection, and weaker selection alone moves a population over the threshold.

**Data (open, CC0).** Dryad doi:10.5061/dryad.rxwdbrvgs, served by Zenodo record 10714366 (README opened in full; file list opened).
- `raw_data.zip` (7.1 GB): for every round and both lineages, three pools were sequenced: the copied minus strand, the plus strand before cleavage, and the plus strand after cleavage. This is what makes the test possible.
- `processed_data.zip` (135 MB): sequence-frequency tables for the cleaved pools of every round, base-call tables for round 1, and a mock round with no polymerase or cleavage step.
- `figure_data.zip` (262 KB).

**The test.** Per round r and lineage, from motif-consistent fractions (the authors' own hammerhead-motif matcher is in the deposit):
- Q_r = retention through copying: odds of a functional motif in the pre-cleavage pool of round r, over the odds in the cleaved pool of round r−1.
- E_r = selection: odds in the cleaved pool of round r, over the odds in the pre-cleavage pool of round r.
- Then replay the recursion with swapped parts: (Q of 52-2, E of 71-89) and (Q of 71-89, E of 52-2), and ask which swap moves the round-8 outcome.

**Gate.**
1. Reproduce the round-1 fidelities (85.6% and 90.9% single-pass; 81.4% and 89.1% reciprocal) from the base-call tables within 0.5 points, and the motif-consistent fractions in the figure data.
2. Power: simulate the recursion with read sampling noise and the observed round-to-round spread of Q and E; a planted world in which only Q differs must give "support" in at least 80% of runs, and one in which only E differs must give "kill" in at least 80%. If the round-to-round spread is too large for either, stop.

**Kill rule (of the fidelity attribution).** Swapping Q alone explains less than 50% of the round-8 gap in log-odds of functional sequences, and swapping E alone explains at least 50%.

**Support rule.** Swapping Q alone explains at least 80%, and the median E does not differ between lineages by more than twofold.

**Reported either way.** Whether Q_r matches what the measured per-nucleotide fidelity predicts for the conserved positions; and E_r against the functional fraction, which shows whether selection weakens as function is lost (a feedback the paper's reading leaves out).

**Power concern.** This cannot separate the polymerase from its Mg2+ concentration; "fidelity" here means the copying condition as run. With one lineage per arm the conclusion is about this experiment, not about error thresholds in general. Reads are plentiful, so the uncertainty is between rounds (8 values of Q and E per lineage), and the bootstrap must resample rounds, not reads.

**Cost.** The honest version needs the pre-cleavage fastqs: pull members from the 7.1 GB zip by range request, one at a time, count sequences and delete. A few hours of download and one to two CPU hours. Disk: under 1 GB at any time. A cheaper first pass uses only `processed_data.zip` (cleaved pools) and treats Q·E as one number per round; it can show whether the 52-2 decline is steady or front-loaded, but it cannot decide the question.

**Prior art checked.** Europe PMC, papers citing PMID 38437533 that mention error threshold, reanalysis, selection stringency, confound or magnesium: 20 hits; titles are new ribozyme work and reviews (for example Gianni et al. 2026, doi:10.1126/science.adt2760, already in our library). Titles only. No reanalysis of the two lineages found.

---

## U5. Are early expansion steps enriched in metal-dependent enzymes within pathways, at reaction level?

**Claim.** Goldford, Smith, Longo, Wing & McGlynn 2024, Nat Ecol Evol, doi:10.1038/s41559-024-02361-4 (abstract opened on the publisher page; the main text is behind a paywall and the bioRxiv full text returned 429, so I quote the abstract only):

> "Early phases of the expansion are enriched with enzymes that are metal dependent and structurally symmetric, supporting models of early biochemical evolution."

**Why it might fail.**
- The authors' notebooks (opened: `main.ipynb` logic as repeated in `revisions.v1/main-partial-correlations.ipynb` and `main-reanalyzeFoldSym.ipynb`) compute, for each expansion iteration, the share of reactions that use a metal and the mean fold-symmetry score, then correlate these per-iteration means with iteration number. Iterations are a series, they hold very different numbers of reactions, and neighbouring iterations share pathways.
- Our own metabolic-strata study (NEGATIVE_ATLAS, Mrnjavac et al. 2026) found that "metal reactions come early" held across the network and vanished within pathways. That entry says a fresh sealed test on a second stratified network is what would settle it. This is that network.

**Data (open).** github.com/jgoldford/metabolic-continuity (tree listed; README and two notebooks opened).
- `assets/models/metabolism.v8.01May2023.pkl` (7.1 MB), `assets/seed_set.csv`, `assets/fold2rxn.ec.30Aug2022.p20.csv`, `assets/xgroup_symmetry.txt`, `assets/KEGG_ModuleVsCompound.csv`, `revisions.v1/SI_tables/S1.csv` (18,940 reaction rows), `S7.csv` (compound emergence per model), `S11.csv` (module emergence).
- Blinding disclosure: I printed the header and first data row of S1, S7, S10 and S11 (one module's correlation and one module's emergence iteration). No metal or symmetry statistic was seen.
- The expansion engine is the authors' `networkExpansionPy` (open). Running it is running their code; do that in an isolated environment. If the reaction-to-iteration table can be rebuilt from S1 and S7 alone, prefer that.

**Gate.** Rebuild reaction emergence iterations and reproduce the authors' per-iteration metal curve (their Fig. 3C code path) to a correlation of 0.95 with their plotted values, and the module emergence iterations in S11 exactly for at least 95% of modules.

**Kill rule.**
- Unit: reaction. Outcome: emergence iteration (rank). Label: metal-using (the authors' definition) and, separately, fold symmetry score.
- Statistic: difference in mean rank between metal and non-metal reactions, computed within KEGG modules and summed (stratified Wilcoxon), with labels permuted within modules, 10,000 times.
- **Kill:** the within-module p is above 0.05 for metal use, and the within-module effect is under one third of the unstratified effect.
- **Support:** within-module p below 0.01 with an effect of at least half the unstratified one.
- Second null (reported): 200 random seed sets matched on size and element content, to see how often an expansion from arbitrary seeds also puts metal reactions early. The repo already holds random-seed runs for other statistics.

**Power concern.** Reactions outside any module drop out of the stratified test; count them at the gate and require at least 500 reactions in modules that contain both labels. Metal use is defined through cofactor species in the model, so a reaction that makes or consumes a metal cofactor is early almost by construction; exclude reactions on the path to the cofactors themselves in a stated variant.

**Cost.** Minutes for the tests; the expansion itself is seconds to minutes.

**Prior art checked.** Europe PMC, papers citing PMID 38519634: 5 in all; the relevant one is Corlett, Smith, Smith & Goldford 2026 (doi:10.1073/pnas.2609531123; abstract opened), by the same group, which builds fold-emergence orderings on the same expansion and reports them "broadly concordant with enzyme phyletic distribution". It does not run a within-pathway permutation. The authors' own revision notebooks run partial correlations on per-iteration means (iteration against symmetry given complexity), which is not a reaction-level or within-module test.

---

## U6. Which arrows of the five-member replicator network survive replicate noise?

**Claim.** Mizuuchi, Furubayashi & Ichihashi 2022, Nat Commun, doi:10.1038/s41467-022-29113-x (opened, PMC8933500):

> "The final population, comprising five RNA lineages, forms a replicator network with diverse interactions, including cooperation to help the replication of all other members."

How the network was drawn (Fig. 4 caption):

> "Error bars indicate mean ± SEM (n = 3 or 4 as shown as individual data points). Measurements were taken from distinct samples. Average fold replications (>1.5-fold) were used to draw the directed graphs (Fig. 3d)."

**Why it might fail.** Each arrow is a mean of 3 or 4 fold-replication values compared with a fixed cutoff of 1.5. There is no test against the no-partner baseline and no correction for the number of pairs. An arrow just over 1.5 with wide scatter is not an interaction, and the "replicates all other members" reading needs every one of its arrows.

**Data (open).** Source Data, `41467_2022_29113_MOESM6_ESM.xlsx` (15.7 MB; opened, labels only). Sheet "Fig. 4": raw fold-replication values for single RNAs and pairs at rounds 0, 120, 155 to 158 and 228, three rows per condition; 181 numeric cells in all. No value was read.

**Gate.** Recompute the means and redraw the published graphs of Fig. 3d from the >1.5 rule; every published arrow must be reproduced.

**Kill rule.**
- For each arrow at round 228, test log fold replication of the target with the partner against 0 (one-sided t on logs, and an exact sign-flip test), Holm-corrected over all tested pairs at that round.
- Also bootstrap the replicates and redraw the graph 10,000 times.
- **Kill:** fewer than half of the round-228 arrows survive Holm at 0.05, or the cooperative lineage replicates all four others in fewer than 50% of bootstrap graphs.
- **Support:** at least 80% of arrows survive, and the "replicates all others" pattern appears in at least 90% of bootstrap graphs.

**Power concern.** With n = 3, an exact test cannot reach p < 0.05 after correction over a dozen pairs, so the t-test on logs carries the decision and leans on normality. State this in the seal. The power gate: simulate true 2-fold and true 1-fold arrows with the pooled within-condition log SD (computed blind to which condition is which); support must fire for true 2-fold in at least 80% of runs. If not, report bootstrap arrow frequencies only, with no verdict.

**Cost.** Minutes.

**Prior art checked.** Europe PMC, papers citing PMID 35304447 that mention reanalysis, replicate, statistical, threshold or noise: 23 hits; titles are follow-ups from the same group and reviews (for example Kanai & Ichihashi 2026, doi:10.1093/molbev/msag184). Titles only. No re-test of the network arrows found.

---

## U7. Do formose compositions differ between environments by more than repeat runs differ?

**Claim.** Robinson, Daines, van Duppen, de Jong & Huck 2022, Nat Chem, doi:10.1038/s41557-022-00956-7 (abstract opened on the publisher page; main text is behind a paywall):

> "Here we demonstrate how complex systems of chemical reactions exhibit well-defined self-organization in response to varying environmental conditions. This self-organization allows the compositional complexity of the reaction products to be controlled as a function of factors such as feedstock and catalyst availability."

**Why it might fail.** T15 found, in the same laboratory's flow set-up, that repeat runs at identical settings differ by 2.7 to 6 within-run SD. If the same holds here, part of the structure across conditions is run-to-run variation.

**Data (open).** github.com/huckgroup/formose-2021 (tree listed, 504 files), plus the publisher's two source-data CSVs (opened; small).
- `EXPERIMENT_INFO/Experiment_parameters.csv` (opened): 112 experiments, 33 condition columns.
- `DATA/DERIVED_PARAMETERS/AverageData.csv` (86 KB; not opened): average composition per experiment.

**Decidability check (blind; conditions only).** Ignoring the experiment code, 104 condition sets are distinct. Four sets were run more than once, 12 runs in all: one set six times (FRN061A, FRN063A to E), three sets twice. That gives 15 + 3 = 18 within-set pairs, but only 4 independent sets.

**Gate.** The repeat runs must be true repeats: check dates and notes in the repo, and that none is a designed variation recorded elsewhere (for example a different mineral batch). If the six-run set is a time series of one run, the study has 3 repeat pairs and stops as underpowered.

**Kill rule.**
- Distance: Aitchison distance between average compositions (log-ratio, with a stated zero replacement).
- R = median distance between repeat runs of the same set. B = median distance between runs from different condition sets, matched to the repeat pairs on residence time and temperature.
- **Kill:** B/R below 2, with a bootstrap over condition sets whose upper bound is below 3.
- **Support:** B/R at least 4 with a lower bound above 2.
- Second arm: redo the paper's clustering after adding repeat-level noise to each experiment 1,000 times; report how often each experiment keeps its cluster.

**Power concern.** Four repeat sets. A bootstrap over four units has almost no resolution, so the honest outcomes are likely "kill" or "inconclusive", not "support". The quoted claim is from the abstract only; the paper's specific clustering claim must be read from a legal copy before sealing.

**Cost.** Minutes.

**Prior art checked.** Europe PMC, papers citing PMID 35668214 with reproducibility, formose, replicate or variability in the title: 12 hits (for example de Jong et al. 2025, doi:10.1002/anie.202504659; Briš et al. 2024, doi:10.1002/anie.202316621). Titles only. T15 (van Duppen 2023) is ours. No repeat-run test of the 2022 dataset found.

---

## U8 (peripheral). Does the 90% biosignature accuracy survive holding out whole sample families?

**Claim.** Cleaves et al. 2023, PNAS, doi:10.1073/pnas.2307149120 (opened, PMC10576141):

> "After evaluating Pyr-GC-EI-MS features in all 134 samples, the random forest model correctly predicted the biogenicity of samples with ~90% accuracy. Thus, the generalized testing error using nested cross-validation (CV) was 10.4% with an area under the receiver operating characteristic curve of 91.2%."

**Why it might fail.** The 134 samples (59 biotic, 75 abiotic) come in families: several meteorites, several coals, several synthesis products of one kind. Random splits put members of one family on both sides, so the model can score well by recognising the family. The claim that matters, an "agnostic" test for unfamiliar material, needs whole families held out.

**Data (open).** OSF doi:10.17605/OSF.IO/EMBH8 (node public; file list opened): `Cleavesetal.pyrGCMSData.zip` (221 MB). Code: github.com/ghystad/Machine_learning_and_preprocessing_pyr_GSMS_data (not opened). Sample attributes are in SI Appendix Table S1 (not opened).

**Gate.** Reproduce the nested-CV error within 4 points of 10.4% with a Python random forest on features built by the authors' stated steps. Fix the family labels from Table S1 before any model is fit, and seal them.

**Kill rule.** Leave-one-family-out balanced accuracy below 70%, or more than 15 points under the random-split accuracy computed with the same code. **Support:** at least 85% and within 5 points.

**Null.** Permute biotic/abiotic labels across whole families (not samples) 1,000 times, to get the accuracy a family-recognising model reaches when the label carries no information.

**Power concern.** Perhaps 10 to 20 families, so accuracy moves in steps of several points; give a family-bootstrap interval. Family assignment is a judgement call, which is why it is sealed first.

**Cost.** One 221 MB download; preprocessing and forests in one to two hours.

**Prior art checked.** Europe PMC, papers citing PMID 37748080 with biosignature, machine, agnostic or pyrolysis in the title: 8 hits, including the same group's follow-up (Wong et al. 2025, doi:10.1073/pnas.2514534122; title only). No independent grouped-validation test found. Ranked low because it is about biosignatures, not about an origin route.

---

## U9 (gate first). Is the "frustrated" aminoacylation landscape a property of the landscape, or of what the selection let us see?

**Claim.** Pressman et al. 2019, J Am Chem Soc, doi:10.1021/jacs.8b13298 (opened, PMC6548421):

> "An analysis of evolutionary pathways shows that, while local optimization within a ribozyme family would be possible, optimization of activity over the entire landscape would be frustrated by large valleys of low activity."

> "The only pathways that could be constructed between different motifs contain fitness losses down to baseline activity, with multiple mutational steps occurring at near baseline activity. The closest apposition of motifs was a pathway between Family 3.1 and Family 1A.1, which involves 5 consecutive intermediates expected to have baseline activity"

**Why it might fail.** Activities were measured only for sequences that survived six rounds of selection and reached the read floor. Intermediates that were not seen were "expected to have baseline activity". Missing is not the same as inactive: a moderately active sequence far from a family centre may simply not be in the pool.

**Data (open, CC0).** Dryad doi:10.5061/dryad.nm1189t, served by Zenodo record 4970564 (file list opened): `kseq-counts.zip` (91 MB), `ActivityObservedData.xlsx` (328 KB), `peak_pather_v01.py` with its README, and selection count zips (200 and 142 MB).

**Gate (decides whether the study exists).** Within families, where paths are known to exist, measure the detection rate: of the one-mutation neighbours of measured sequences with activity 10 to 100 times background, what share has a measurement at all, as a function of distance from the family centre? If the share at distance 4 or more is under 50%, an unseen inter-motif intermediate tells us nothing, and the paper's "frustrated" reading is unsupported by its own coverage. That is the finding; no path search is then needed.

**Kill rule.** Thin the within-family data to the coverage seen between motifs and rerun the authors' path search. Kill if known within-family paths are lost in at least 50% of thinned copies. Support if at least 90% are kept, meaning the method would have found inter-motif paths had they existed.

**Power concern.** A kill here says "not shown", not "paths exist". Only new measurements can show that. The same group later extended the neighbourhoods (Janzen 2022, our T12) and reported a new within-motif bridge (Charest et al. 2023, doi:10.1261/rna.079541.122; abstract opened: "a previously unknown evolutionary 'bridge' between two ribozyme families that share a common motif"). That is partial prior art in the direction of the kill.

**Cost.** About 100 MB to 430 MB of downloads; a few CPU hours for the thinned path searches.

---

## Looked at and not proposed

- **Kudella et al. 2021 (doi:10.1073/pnas.2018830118; opened, PMC7923349).** "Structured sequences emerge from random pool" is a good target for a ligase-bias null, but: "NGS data files are available upon request." Not deposited. Dropped.
- **Xavier & Kauffman 2022 (doi:10.1098/rsta.2021.0244; Crossref abstract opened).** RAFs "in all of 6683 prokaryotic metabolic networks". The publisher page returned 403 and I could not confirm a data deposit. Dropped. It would also repeat `experiments/raf_null`.
- **Bokov & Steinberg 2009 (doi:10.1038/nature07749; abstract and the supplementary PDF opened).** I wanted a random-orientation null for the A-minor dependency hierarchy of 23S rRNA. The authors already ran it: Supplementary Notes 2B gives the probability of no cycles under random orientation as "P = P1 × P2 = 207 × 2-38 ≈ 7.53 × 10-10". Nothing cheap is left.
- **Pinna et al. 2022 (doi:10.1371/journal.pbio.3001437; opened, PMC9531788).** S1 Data holds the numbers behind every figure, with N = 3. The claims are all-or-nothing chemistry (ATP forms with Fe3+ and acetyl phosphate, not with other ions or other diphosphates); a reanalysis cannot overturn a 20% yield against zero.
- **Vincent et al. 2019 (doi:10.3390/life9040080; opened, PMC6911371) and Asche et al. 2021 (doi:10.1038/s41467-021-23828-z; opened, PMC8192940).** Both papers hedge their own claims ("hints", "more research is needed"; Asche reports that repeat runs "differ"). No sharp claim to test.
- **Goldford et al. 2019 (doi:10.1038/s41559-019-1018-8).** Europe PMC full text returned 500. Not opened; the last plan found no claim there whose null is not set by a definition.
- **Goldford et al. 2017 (doi:10.1016/j.cell.2017.02.001), Harrison et al. 2022 (doi:10.1016/j.bbabio.2022.148597), Coleman et al. 2021 (doi:10.1126/science.abe0511).** Looked up only; not open access on Europe PMC and no deposit checked. Not proposed.
- **Matreux et al. 2024 (doi:10.1038/s41586-024-07193-7).** Looked up only (PMC10990939 exists). Not read; no proposal.

## Housekeeping

- Sources used: Europe PMC REST (search and full-text XML), Crossref, publisher pages for abstracts and supplementary links, PLoS supplementary files, Springer static supplementary files, GitHub and GitLab APIs, Zenodo API, Dryad API (metadata only), OSF API, KEGG REST.
- User-Agent was `open-research-site/1.0` on every request. No personal detail was sent.
- Blocked and not worked around: Dryad file API (401) and Dryad download link (403); bioRxiv full text (429, one attempt); royalsocietypublishing.org (403); Europe PMC full text for PMC6881557 (500). The Zenodo route to Dryad-deposited files is the repository's own public mirror, not a workaround.
- Largest downloads: one 15.7 MB source-data xlsx (Mizuuchi), one 3.4 MB supplementary PDF (Bokov), one 3 MB xlsx (Bendixsen). Zips were listed by range request without fetching members. KEGG formulas for 4,216 compounds were fetched for the U1 blind count.
- Everything fetched sits in a scratch directory outside the repo and can be deleted. The addresses above are enough to fetch it again.
- Not done here: adding the papers read today (Lai 2021, Bendixsen 2019, Papastavrou 2024, Mizuuchi 2022, Cleaves 2023, Pressman 2019, Pinna 2022, Kudella 2021, Bokov & Steinberg 2009) to `library.json` and the site. The task allowed one file only; the coordinator should queue that.
