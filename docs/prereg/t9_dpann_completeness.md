# Pre-registration (T9): does DPANN's high gene-loss rate survive a check against genome completeness?

Status: DRAFT, written 2026-11-24 by the T9 prep agent. This is study S5 in `docs/plans/next_studies_2026-11-24.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run, and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t9_dpann_completeness/scripts/t9_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is how the deposited per-branch loss counts pair with the DPANN label and with completeness. Every deciding number comes from that pairing.

- **Not computed.** No loss fraction for DPANN or non-DPANN branches, no ratio, and no slope of loss on completeness on the real labels. No script has printed a loss value joined to a clade label or to completeness.
- **Four loose loss values by accident.** A `head` on the event file printed the loss column for four rows: AP024486.1 145.56, AP024487.1 141.78, Aenigmatarchaeota 214.0 and Altarchaeota 293.66. They were not joined to completeness. Two of them (Aenigmatarchaeota and Altarchaeota) are DPANN internal nodes by name.
- **Whole-tree branch counts.** A diagnostic printed how many of the 512 branches have more transfers than duplications, and more transfers than losses (the published Fig. 2 counts; see the gate). These counts mix DPANN and other branches.
- **Published values, as flags only.** The gate compared the LDCA and UnCl2 branch losses with the values in the text and printed only match flags. The paper already prints both values, so the flags add nothing.
- **Model parameters.** The rate values in `model_parameters.txt` were never printed. Only the number of distinct D, T, L triplets (24) and of origination values (4) was printed.
- **Completeness and structure (allowed).** CheckM1 and CheckM2 distributions by group, branch and tip counts, depth bins, rate-class membership and file headers.
- **Dry run.** `dryrun` shuffles the DPANN label within depth bins and permutes completeness over tips, then runs the full `real` code. It printed whole-tree marginals: mean internal loss fraction near 0.22 and tip loss fraction near 0.23. About 30% of a shuffled "DPANN" set is truly DPANN by chance, so the dry run carries a little information about the real pairing. Its ratios were 0.97 to 1.07.
- **What this does to my expectation.** Nothing here points either way. The thresholds 1.15 and 1.3 come from the plan and were not moved. The form of the rule did change, and the planted check is the reason (see "Changes from the plan").

## Claim under test

Huang et al. 2026, Nat. Commun., doi:10.1038/s41467-026-76386-7 (PMC13473441, read from `experiments/t9_dpann_completeness/raw/europepmc/PMC13473441_fulltext.xml`).

- Results, verbatim: "Adding a DPANN-specific loss rate substantially improved reconciliation model fit (BIC: 3284636.6, Supplementary Data 10), and, as predicted, the DPANN loss rate was inferred to be higher than that for the other clades (DPANN: 0.40-0.45, other clades: 0.26-0.27)."
- How completeness entered, verbatim: "To account for the incomplete nature of some MAGs, genome completeness estimates from CheckM v2 were used in reconciliation139 (Supplementary Data 1)." And: "Genome completeness was estimated using CheckM2 (v0.1.3)139."
- The loss-rate model, verbatim: "First, we introduced DPANN-specific rate classes: a different loss rate (DPANN:L; 4 parameters), different duplication+loss rates (DPANN:DL; 5 parameters), different transfer+loss rates (DPANN:TL; 5 parameters) and different duplication+transfer+loss rates (DPANN:DTL; 6 parameters)."
- The model behind the deposited event counts, verbatim: "For ancestral genome content reconstruction, we allowed heterogeneous origination by estimating independent rates for the root, its two immediate descendants, and the DPANN lineage using --origination OPTIMISE, based on the reconciliation model with 72 parameters, which is highly correlated with the best-fitting model, DTL_br3 (Pearson's r: 1) (Supplementary Note 4)."
- The clade labels of that model, verbatim: "...and for DPANN lineages (i.e., for each Micrarchaeota; B1Sed10-29; Iainarchaeota; Altiarchaeota; Undinarchaeota; Aenigmarchaeota; PWEA01; EX4484_52; Nanohaloarchaeota; SpSt-1190; parvarchaeal-related lineages; UBA10117; Pacearchaeales; Woesearchaeales+SCGC-AAA011-G17; Nanoarchaeales; plus two internal nodes representing the last common ancestor of all DPANN and of DPANN Cluster 1 archaea, respectively), yielding 72 parameters in total (DTL_br2)."

**What is tested.** The 0.40–0.45 rates belong to the 4-parameter model, and the deposit holds no output of that model. The deposit does hold per-branch event counts under the 72-parameter model. So this study tests the claim behind the rates: that DPANN lineages lose genes faster than other archaea. It does not re-derive the published numbers.

**H1.** The DPANN excess is real. On internal branches with at least three descendant genomes, where one incomplete genome cannot create a loss, the DPANN loss fraction is at least 1.3 times the non-DPANN one.

**H0.** The excess is an artefact of incomplete genomes. Off the tips it shrinks to less than 1.15 times, and the data cannot exclude a ratio of 1.

**Prior art.** `experiments/t9_dpann_completeness/PRIOR_ART.md`. Not settled. Csűrös 2026 (PNAS, doi:10.1073/pnas.2537812123) names this confound for DPANN and says it cannot be separated using copy numbers, but it uses the 269-genome Dombrowski 2020 set and a copy-number model, not Huang's data. No paper citing Huang 2026 or its preprint tests the loss rates (by abstract).

## How AleRax counts losses (from the source)

This is why arm A of the plan changed. In AleRax (`src/ale/UndatedDTLMultiModel.hpp`) the extinction probability of a tip includes the gene being present but not seen: `temp = REAL(_PS[ec] * this->_fm[e]); // S but not observed scenario`. An SL event records the child where the gene died out (`recCell->event.lostSpeciesNode = g;`). The per-species counts (GeneRaxCore `src/util/Scenario.cpp`) add one loss to that child: `speciesToEventCount.at(event.pllLostSpeciesNode->label)[2]++;`. So a gene missing from an incomplete genome is still written as a loss on that tip's branch, even when the correction works as intended. Tip-branch losses must rise with incompleteness.

## Inputs (exact)

Paths are under `experiments/t9_dpann_completeness/` unless noted. Downloads used User-Agent `open-research-site/1.0`. Python reads them with `-I`. `t9_analysis.py` checks the sha256 of every file it reads and stops on a mismatch.

| File | Source | sha256 |
|---|---|---|
| `raw/41467_2026_76386_MOESM3_ESM.xlsx` | Huang 2026, Supplementary Data 1–33 | 5b267e6542b95625dca90fd9f5e440d031b5a1fa39e63f8fd92b0552219e7276 |
| `cache/supp/sheet1.tsv` | Supplementary Data 1 (genomes, CheckM1, CheckM2), via `scripts/xlsx_to_tsv.py` | fd9767fe177f9a29309adc68e7fc35c89cd18389e3c7fecd1520e86940608524 |
| `cache/supp/sheet10.tsv` | Supplementary Data 10 (BIC) | c405af80c41526ca1e9348050b6ab15df67db0277f76b0b00986fb64255e0e98 |
| `cache/supp/sheet20.tsv` | Supplementary Data 20 (per-branch events) | da0bd267bbb977d15001eedf0708a34161b32df8bccb77279fabe1f2017c4ec0 |
| `cache/supp/sheet33.tsv` | Supplementary Data 33 (model parameter counts) | c565ab0b094c491fe1264db5bc1bdac32125914b848ddb18442a60db525bece8 |
| `luca_calib/raw/huang/4_Ancestral_reconstruction.zip` (under `experiments/`) | Zenodo doi:10.5281/zenodo.18701544; already in the repo; left in place | not re-hashed; members below |
| `cache/deposit/4_Ancestral_reconstruction/Euryarchaeota_root/reconciliations/perspecies_eventcount_transfer_corrected.txt` | from the zip | 5173c698353fc66ef746347fe1f49501a87a2de4a4a28f3cb58e0765359ffe56 |
| `…/Euryarchaeota_root/species_trees/inferred_species_tree.newick` | from the zip | 97009007b4a205a52f84b1d0eb0e7de85223302e5a9e2f774e69a170c370cf7e |
| `…/Euryarchaeota_root/species_trees/starting_species_tree.newick` | from the zip | 872e0ae2ff2153fb2c1ddd9ba41e6861f46f283d0afd76403e3133068f1b4e4d |
| `…/Euryarchaeota_root/model_parameters/model_parameters.txt` | from the zip | c8ca0b4bb20340b57be1b668cd993ada38ecbefd08379a60ac20fda3e0c3124f |
| `…/MHH_root/reconciliations/perspecies_eventcount_transfer_corrected.txt` | from the zip | a2d24df401868ffc5485f5d417378883488730f8bf0ec9f0a4d58d04e3a2ad2e |
| `…/MHH_root/species_trees/inferred_species_tree.newick` | from the zip | 1eba48f214bd025ba4179ce67f33d62ff64953b101ab909fa8444b60a7e158cd |
| `…/MHH_root/species_trees/starting_species_tree.newick` | from the zip | 9e2141b051ee85d6a4459efce9b4cd6e098e60c13586524daf1e57c20183c632 |
| `…/MHH_root/model_parameters/model_parameters.txt` | from the zip | 4078e23fc18844af9ecf8b07740b3321f3d969e57c7ff77c626d3f0af4642d13 |
| `raw/europepmc/PMC13473441_fulltext.xml` | Europe PMC full text, Huang 2026 | 242643d47bb138b580b6aac97c459282552ec79754327720daae2663466af732 |
| `raw/europepmc/PMC13167736_fulltext.xml` | Europe PMC full text, Csűrös 2026 | ea839f8557845508671f375f93e217c22b7155c43feac1ae59c5f3eeb0b18fc3 |
| `raw/alerax_src/UndatedDTLMultiModel.hpp` | AleRax source, main branch | 45a631a406cb245d852e4619c9b7188d5d969d3d48f3e1c09b47ecad38137ba4 |
| `raw/alerax_src/Scenario.cpp` | GeneRaxCore at commit 9ad7263b | fb078f6a156111662fb4d34aa2f21b8ad8f944225e40a5fd9af039590ababd3a |

The outputs and scripts are hashed in the report that goes with this draft. They will go into `HASHES.txt` at the seal.

Notes on the inputs.

- `raw/` and `cache/` are gitignored. The cache is 824 KB. Nothing under `experiments/luca_calib` was modified.
- `data/t9_structure.tsv` comes from `gate`. It holds structure only: label, parent, tip flag, descendant tips, DPANN flag, rate class, depth bin, substitution length, CheckM2 and CheckM1. It holds no event count.

## Gate (`t9_analysis.py gate`; run; passed)

| Check | Result |
|---|---|
| Nodes and tips in the Euryarchaeota-root tree | 513 and 257 |
| Tips found in the Supplementary Data 1 focal set with CheckM2 | 257 of 257 |
| Labels in the event file and the tree are the same | yes, for both roots |
| Starting tree has the same topology as the inferred tree | yes, for both roots |
| Distinct D, T, L triplets in the parameters | 24, so 72 parameters (the paper: 72) |
| Distinct origination values | 4 (root, its two children, DPANN) |
| BIC = −2 lnL + k ln(7059) recomputed for all 135 cells of Supplementary Data 10 | matches, largest difference 4e-9; the DPANN_L cell is 3284636.6 as in the text |
| Fig. 2 group node counts (MHH 41, Halobacteriota 81, Thermoplasmatota 67, Korarchaeota 5, TAC 121, Asgard 39, Cluster1 35, Undinarchaeota 3, Cluster2 113) | all 9 match |
| Supplementary Data 20 equals the deposited event file | yes, 513 rows, both roots |
| LDCA losses 639.82/592.64 and UnCl2 losses 490.19/588.91 | match (flags only) |
| Branches with transfers > duplications and transfers > losses, Euryarchaeota root (published 507 and 177) | 507 and 177 with `receiving_transfers` |
| The same, MHH root (published 501 and 154) | 508 and 154 with `receiving_transfers`; 501 with `transfers` |

**What cannot be reproduced.** The DPANN_L rates (0.40–0.45 against 0.26–0.27) are parameters of the 4-parameter model. The deposit holds parameters and counts only for the 72-parameter model. So the per-branch losses cannot be tied to the published rates. What is reproduced: the BIC table, the tree and its group sizes, the 72-parameter structure, Supplementary Data 20, two published branch losses, and three of the four published transfer counts. The fourth (MHH, 501) matches the `transfers` column instead of `receiving_transfers`. This looks like a small inconsistency in the paper and does not affect the loss column.

**The DPANN label.** A branch is DPANN if it is the node labelled `DPANN` in the deposited tree or lies below it: 77 tips and 76 internal non-root branches. The other side has 180 tips and 179 internal branches. Rate classes are the 24 distinct triplets; 17 are DPANN-only, 7 are other-only, and none is mixed. Woesearchaeota is the largest DPANN class (39 branches).

**Blind counts.**

| | DPANN | Other |
|---|---|---|
| Tips | 77 | 180 |
| CheckM2 median (%) | 90.84 | 98.51 |
| CheckM2 below 90 / 80 / 70 | 34 / 5 / 2 | 28 / 12 / 3 |
| CheckM2 minimum | 57.89 | 42.99 |
| CheckM1 median, below 90 | 82.4, 65 | 98.13, 28 |
| Internal branches by descendant tips 2, 3–4, 5–8, 9–16, 17–32, 33+ | 27, 16, 12, 11, 2, 8 | 54, 49, 32, 24, 9, 11 |
| Internal branches with ≥ 3 descendant tips | 49 | 125 |
| Spurious internal-loss floor ∏(1 − c) over descendants, mean (max) | 0.0036 (0.054) | 0.0010 (0.026) |

**The decision is non-empty.** Both groups have internal branches deep enough for arm B. The non-DPANN side has 28 tips below 90% CheckM2, which is enough for the arm A control. Planted rows below show that both kill and support are reachable.

## Fixed decisions

- **D1, units.** The 512 non-root branches of the deposited Euryarchaeota-root species tree, with the event counts in `perspecies_eventcount_transfer_corrected.txt` (72-parameter model, origination optimised).
- **D2, statistic per branch.** f = losses ÷ (losses + copies). It is unitless. The undated AleRax model has no branch length in time, so the plan's "per unit branch length" cannot be applied as written. Losses per unit of substitution length (from the starting tree) are reported only.
- **D3, DPANN label.** As in the gate: the `DPANN` node and everything below it.
- **D4, completeness.** CheckM2 from Supplementary Data 1, focal rows, as a fraction. CheckM1 versions are reported only.
- **D5, branches in arm B.** Internal branches with at least `MIN_TIPS` = 3 descendant tips, so cherries are left out. The rule was fixed before the planted run: the smallest cutoff in (3, 5) whose worst-null false-support rate is at most 5%. The planted run chose 3, and the script's constant equals it.
- **D6, interval.** Clade-block bootstrap. Blocks are (rate class, DPANN flag), and blocks are resampled with replacement inside each group, 2,000 draws. The interval is log r ± t × sd(log r*), where t is the 97.5% Student t quantile with df = (number of blocks in the smaller group) − 1. The percentile interval is reported too.
- **D7, thresholds.** 1.15 and 1.3, from the plan.
- **D8, depth bins.** Internal branches binned by descendant tips at 2, 3–4, 5–8, 9–16, 17–32 and 33+. Tips form their own bin.
- **D9, seed.** 20261127. Generators: `[seed, 2]` planted, `[seed, 3]` real, `[seed, 4]` dryrun. `gate` uses no random numbers.
- **D10, roots.** The Euryarchaeota root is primary. The MHH root gets the same analysis, reported only.
- **D11, dry run.** Shuffle the DPANN label within depth bins (tips among tips, internal branches within their bin), and permute completeness over tips, before any statistic is computed.
- **D12, order of runs.** `gate`, `planted`, `dryrun`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with its current sha256.

## Decision rules (arm B, Euryarchaeota root)

r is the mean f of DPANN internal branches with ≥ 3 tips over the mean f of other internal branches with ≥ 3 tips. lo is the lower end of the D6 interval.

- **Kill.** r < 1.15 and lo ≤ 1.0. The excess does not reach the deep branches, so it is consistent with an incompleteness artefact.
- **Support.** r ≥ 1.3 and lo > 1.15. DPANN loses more genes on branches where one incomplete genome cannot create a loss.
- **Otherwise inconclusive.**

**Arm A, positive control (no rule attached).** The OLS slope of tip f on (1 − CheckM2) among non-DPANN tips, with a block-bootstrap percentile interval. Because of how AleRax counts losses, it should be positive. If it is not, the event counts behave differently from the source, and the report must say so next to the verdict.

## Changes from the plan, made before the seal

The plan's rule was: kill if arm A's slope is positive and arm B's ratio is below 1.15 with 1 inside its interval; support if arm B's ratio is at least 1.3 with an interval excluding 1.15 **and** arm A's slope is 0. The thresholds are unchanged. Three things changed.

1. **Arm A no longer enters the verdict.** In AleRax a gene missing from an incomplete genome is counted as a tip loss (see above). Arm A's slope is positive by construction, even when the correction works. In every planted row the slope interval was above 0 (probability 1.00), so the plan's support clause could never be met (column "plan rule": support 0.00 in every row, including a true twofold excess). Arm A becomes a positive control.
2. **Cherries are left out of arm B.** On a branch with two descendant tips, two incomplete genomes can still remove a gene together, and DPANN has more of those. With every internal branch included, false support reached 9.3% under the null (CheckM2 10 points too high in DPANN). With ≥ 3 tips the worst null is 3.3%.
3. **The interval is a few-block t interval.** There are only about 7 non-DPANN blocks. A percentile bootstrap over so few blocks was too narrow (5.3% worst-null false support with ≥ 3 tips). The t interval brought it to 3.3%.

The plan's spurious-floor null (the product of (1 − c) over descendants) is used as a reported-only adjustment. The floor is tiny (mean 0.004 in DPANN), so it cannot explain a large internal excess either way.

## Planted check (`t9_analysis.py planted`; run; synthetic losses only)

Each replicate runs on the real tree, the real rate classes and the real CheckM2 values. It never reads the event counts.

**How synthetic losses are made.** 1,200 families start at the root, and new families arise on each branch (Poisson, scaled to the loss rate). On each branch a family is lost with probability p = p0 × (a log-normal factor per rate class, sd `sd_block`) × (a log-normal factor per branch, sd 0.4). The DPANN factors multiply p on DPANN internal branches and on DPANN tips. Each tip shows a family it carries with probability equal to its true completeness. Families with fewer than 4 observed copies are dropped. Losses and copies come from Dollo parsimony on the observed tips. 150 replicates per null, 80 per alternative, 1,000 bootstrap draws each. Script sha256 e7b00f68….

| Planted | Arm A slope | Plan rule P(kill)/P(support) | All internal: ratio, P(support) | Primary (≥ 3 tips): ratio (5–95%) | P(kill) | P(incon.) | P(support) | ≥ 5 tips: ratio, P(support) |
|---|---|---|---|---|---|---|---|---|
| Null, p0 = 0.03 | 0.92 | 0.48 / 0.00 | 1.17, 0.04 | 1.09 (0.73 to 1.53) | 0.67 | 0.33 | 0.01 | 1.09, 0.01 |
| Null, p0 = 0.06 | 0.87 | 0.63 / 0.00 | 1.12, 0.01 | 1.06 (0.78 to 1.38) | 0.70 | 0.29 | 0.01 | 1.07, 0.01 |
| Null, p0 = 0.12 | 0.78 | 0.60 / 0.00 | 1.08, 0.00 | 1.06 (0.74 to 1.37) | 0.70 | 0.30 | 0.00 | 1.07, 0.00 |
| Null, sd_block 0.6 | 0.87 | 0.53 / 0.00 | 1.19, 0.05 | 1.13 (0.58 to 1.86) | 0.63 | 0.34 | 0.03 | 1.13, 0.01 |
| Null, CheckM2 10 points too high in DPANN | 0.87 | 0.23 / 0.00 | 1.32, 0.09 | 1.13 (0.80 to 1.53) | 0.60 | 0.39 | 0.01 | 1.09, 0.00 |
| Null, true completeness = CheckM1 | 0.56 | 0.31 / 0.00 | 1.27, 0.07 | 1.11 (0.79 to 1.49) | 0.57 | 0.41 | 0.02 | 1.07, 0.03 |
| Null, CheckM2 noisy (true = est − abs N(0, 5) points) | 0.86 | 0.58 / 0.00 | 1.14, 0.02 | 1.07 (0.79 to 1.46) | 0.71 | 0.28 | 0.01 | 1.07, 0.01 |
| Null, DPANN tips truly ×2 (tips only) | 0.87 | 0.36 / 0.00 | 1.23, 0.03 | 1.10 (0.80 to 1.46) | 0.63 | 0.37 | 0.00 | 1.09, 0.00 |
| DPANN ×1.3 | 0.87 | 0.14 / 0.00 | 1.40, 0.15 | 1.34 (0.99 to 1.86) | 0.24 | 0.69 | 0.07 | 1.33, 0.07 |
| DPANN ×1.6 | 0.87 | 0.00 / 0.00 | 1.69, 0.47 | 1.64 (1.21 to 2.03) | 0.03 | 0.71 | 0.26 | 1.65, 0.24 |
| DPANN ×2.0 | 0.87 | 0.00 / 0.00 | 2.07, 0.81 | 2.01 (1.50 to 2.60) | 0.00 | 0.29 | 0.71 | 2.04, 0.59 |
| DPANN ×1.6, p0 = 0.03 | 0.92 | 0.01 / 0.00 | 1.73, 0.47 | 1.65 (1.20 to 2.15) | 0.04 | 0.62 | 0.34 | 1.69, 0.28 |
| DPANN ×1.6, p0 = 0.12 | 0.78 | 0.03 / 0.00 | 1.63, 0.39 | 1.62 (1.19 to 2.16) | 0.03 | 0.69 | 0.29 | 1.66, 0.26 |
| DPANN ×1.6, sd_block 0.6 | 0.87 | 0.12 / 0.00 | 1.82, 0.20 | 1.79 (0.95 to 3.27) | 0.19 | 0.64 | 0.17 | 1.82, 0.16 |
| DPANN ×1.6, internal only | 0.87 | 0.04 / 0.00 | 1.59, 0.36 | 1.60 (1.15 to 2.22) | 0.06 | 0.62 | 0.31 | 1.62, 0.21 |
| DPANN ×1.6, CheckM2 10 points too high in DPANN | 0.87 | 0.00 / 0.00 | 1.90, 0.76 | 1.71 (1.27 to 2.32) | 0.00 | 0.55 | 0.45 | 1.67, 0.28 |
| DPANN ×1.6, true completeness = CheckM1 | 0.55 | 0.00 / 0.00 | 1.84, 0.62 | 1.70 (1.27 to 2.25) | 0.03 | 0.55 | 0.42 | 1.67, 0.29 |

What the table shows.

- **The primary rule is calibrated.** False support is at most 3.3% over the eight nulls, including CheckM2 overestimating DPANN completeness by 10 points and true completeness at the lower CheckM1 values.
- **Both verdicts are reachable.** Kill has probability 0.57 to 0.71 under the nulls. Support has probability 0.71 at a true twofold excess.
- **The plan's rule cannot give support.** Arm A's slope is always positive, so its support clause is never met.
- **All internal branches give too much false support.** 9.3% when CheckM2 is too high in DPANN.
- **Power is low at a paper-sized effect.** The paper's rates differ by about 1.6 times (0.40–0.45 against 0.26–0.27). At ×1.6 the primary rule gives support only 26% of the time, inconclusive 71% and kill 3%. A kill at the paper's effect size is rare, so a kill is informative. An inconclusive result is the likely outcome even if the claim is true.
- **The estimate is not biased.** Under the nulls the mean primary ratio is 1.06 to 1.13. Under the alternatives it tracks the planted factor.

**Dry run.** `t9_analysis.py dryrun` runs the full `real` code, every reported-only extra included, on shuffled labels and permuted completeness. It ran without error. Euryarchaeota root: r = 0.995 (0.81 to 1.22), a kill, as it should be. Arm A slope 0.08 (−0.12 to 0.20), flat, as it should be with completeness permuted. Depth-matched permutation p = 0.55. MHH root: r = 0.966 (0.79 to 1.18), a kill. Its other numbers are synthetic.

## Reported only (no rule attached)

`real` also prints these. None can change the verdict.

- Arm A, the positive control, with CheckM2 and with CheckM1.
- **Arm C.** DPANN tip f observed over the value the non-DPANN tip fit predicts from completeness. A value above 1 says DPANN tips lose more than their completeness explains.
- Arm B on all internal branches (the plan's version), with the verdict the plan's rule would give.
- Arm B with each branch's spurious floor ∏(1 − c) subtracted.
- Arm B with ≥ 5 and with ≥ 9 descendant tips.
- Arm B per unit substitution length.
- Pooled ratio (sums of losses over sums of losses plus copies).
- The raw tip ratio, DPANN over other.
- **Depth-matched permutation.** The arm B ratio against 2,000 shuffles of the DPANN label within depth bins (≥ 3 tips).
- **Leakage check.** The Spearman correlation, across DPANN rate classes, between internal f and the mean incompleteness of the class's tips.
- Everything above for the MHH root.

## Ways it could be fooled, and limits

1. **Leakage through shared rates.** Each rate class has one loss rate for its tips and internal branches. If incomplete DPANN tips push the class's fitted loss rate up, the internal branches of that class inherit higher losses. Then arm B can show an excess that is partly from completeness. The leakage check looks for it, but with 17 DPANN classes it has little power.
2. **The fraction-missing term may over-correct or under-correct.** Arm B does not depend on how well the correction works at the tips, but the fitted class rates do (point 1).
3. **Few blocks.** There are about 7 non-DPANN blocks, so the interval is wide and power is low (26% support at ×1.6). An inconclusive result says little.
4. **The 72-parameter counts, not the 4-parameter rates.** The published 0.40–0.45 belong to a model whose output is not deposited. A kill here says the excess does not show in the reconstruction's deep branches. It does not refute the 4-parameter fit directly.
5. **Losses on a branch depend on what the parent had.** DPANN branches start from an ancestor that the reconciliation already reduced. f divides by losses plus copies to account for this, but it is not a rate per unit time.
6. **DPANN is a monophyletic clade.** Any clade-wide difference in tree shape, gene-tree quality or transfer handling looks like a clade effect. The depth bins match shape only roughly.
7. **CheckM2 itself is biased for DPANN.** Reduced genomes lack marker genes, so completeness may be misjudged. The planted rows cover a 10-point overestimate and CheckM1 as the truth. Larger errors are not covered.
8. **The simulator is Dollo parsimony, not AleRax.** It has no duplications, no transfers and no gene trees. The planted check shows that the rule is calibrated for this model, not for AleRax's counting.
9. **Root.** The Euryarchaeota root is primary. The MHH root is reported, and the two may disagree.
10. **One cutoff decides.** ≥ 3 tips is primary. ≥ 5 and ≥ 9 are reported.

## Sources actually opened

- Huang et al. 2026, Nat. Commun., doi:10.1038/s41467-026-76386-7: full text from Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13473441/fullTextXML`), Supplementary Data 1, 10, 20 and 33 (from the 6.2 MB xlsx), and the Zenodo deposit doi:10.5281/zenodo.18701544 (`4_Ancestral_reconstruction.zip`: event counts, inferred and starting species trees, and model parameters for both roots).
- Csűrös 2026, PNAS, doi:10.1073/pnas.2537812123: full text from Europe PMC (`PMC13167736`).
- AleRax source, `https://github.com/BenoitMorel/AleRax`, `src/ale/UndatedDTLMultiModel.hpp`, and GeneRaxCore at commit 9ad7263b, `src/util/Scenario.cpp`.
- Prior-art searches and the abstracts read: `experiments/t9_dpann_completeness/PRIOR_ART.md`.

## Decisions at the seal

These choices were made by the project coordinator before `real` ran. None was chosen from an outcome.

1. **Changes to the plan's rule: all three accepted.**
   - Arm A becomes a positive control and leaves the verdict. AleRax counts a gene missing from an incomplete genome as a loss on that tip, so the plan's negative-control reading of arm A could never hold.
   - Only internal branches with at least 3 descendant genomes are used.
   - The interval is the few-clade t interval.
2. **Arm A:** a non-positive arm A is flagged next to the verdict. It does not void the result.
3. **Units:** the loss measure, losses ÷ (losses + copies), has no units. Losses per unit of substitution length are reported only, because the undated model has no branch lengths.
4. **Root:** Euryarchaeota is primary. MHH is reported only.
5. **What a kill means.** It says no DPANN excess near the size the paper reports, which is a ratio of about 1.6 (false kill 3% in the planted check). It does not rule out a smaller excess: at a true ×1.3, the false-kill rate is 24%. Support at ×1.6 comes only 26% of the time.
6. **Leakage risk:** each rate class shares one loss rate between its tips and its internal branches. Incomplete tips could therefore raise the internal-branch losses of their class. Only a weak check is reported for this, and it is a stated limit.
