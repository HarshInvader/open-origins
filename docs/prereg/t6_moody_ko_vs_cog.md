# Pre-registration (T6): does merging split KEGG families into COGs rescue LUCA families, beyond re-run noise?

Status: DRAFT, written 2026-11-24 by the T6 prep agent. This is study S2 in `docs/plans/next_studies_2026-11-24.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t6_moody_ko_cog/scripts/t6_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is the pairing of each COG's PP (Supplementary Data 2) with the PP of its own member KOs (Supplementary Data 1). Every deciding number comes from that pairing: the rescue rate in the merge group, the flip rate in the retest group, and their ratio.

- **Not computed.** The rescue rate, the flip rate, the ratio, or any change in PP between a COG and its KOs. No script has printed a paired value.
- **One paired answer, taken on purpose.** `gate` asks whether the COG PP is a plain copy of the KO PP in the retest group, and prints one of three levels: under 5% of families equal, between, or over 95%. The answer is "under 5%". If the table were a copy, the retest group would hold no re-run and the study would be empty. Nothing else about the pairing was printed.
- **KO side only (allowed; the KO table is the published one).**
  - How many COGs in each group are eligible, split by the largest member-KO PP and by family size. These are the blind counts below.
  - The count of KOs with PP ≥ 0.75 (682) and the paper's flag count (399).
  - 1,898 KOs have no PP. Their median size is 2 sequences, and Moody's own `Probable` flag is 0 for all of them.
- **Structure only.** Sequence ids and trimmed alignments of every COG and KO, from the deposit. No PP.
- **COG side, marginal only.** `dryrun` permutes the COG PP over COGs, so it shows the marginal: about 15% of COGs have PP ≥ 0.75 and about 23% have PP ≥ 0.5. For KOs with a PP the share at or above 0.75 is 9.1%. The gate also checked that the PP column of Supplementary Data 2 equals the repo's `COG_LUCA_PP.csv` (it does).
- **Three loose values by accident.** A `head -1` on headerless files printed 0.2116 (first line of `COG_test/LUCA_PP.csv`, which is COG0001 and was already disclosed in T5), 0.9975 (first line of `LUCA_PPs.csv`, a KO value) and 785 (first line of `simulations_COG_LUCA.csv`, one simulated COG count).
- **What this does to my expectation.** The COG marginal is higher than the KO marginal. That fits rescue, and it fits a general upward shift in single-run values just as well. I have no view on which. The thresholds 2, 5 and 5% come from the plan and I have not moved them. The form of the rule did change, for reasons that the planted check shows (see "Changes from the plan").

## Claim under test

Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1 (PMC11383801, read from `experiments/t6_moody_ko_cog/raw/europepmc/PMC11383801_fulltext.xml`).

- Results, verbatim: "…it has the drawback that some widespread gene families that were likely present in LUCA are divided into multiple KO families that individually appear to be restricted to particular taxonomic groups and inferred to have arisen later. To account for this limitation, we also performed an analysis of COG (Clusters of Orthologous Genes) gene families, which correspond to more coarse-grained functional annotations (Supplementary Data 2)."
- Methods, verbatim: "We also performed a COG-based clustering analysis in which COGs were assigned based on the modal COG identifier annotated for each KEGG gene family based on the results from EGGNOGMAPPER v.2 (ref. 89). These gene families were aligned, trimmed and one set of gene trees (with 1,000 ultrafast bootstrap replicates) was inferred using the same parameters as described above for the KEGG gene families."
- Supplementary Data 2 caption, verbatim: "This table contains the results for the reconciliations of COG-based gene family clustering against the constrained focal species-tree topology."

The paper gives no count of families that the COG analysis rescues.

**H1.** Merging rescues families. A COG built from several KOs that are each below 0.5 reaches 0.75 far more often than a re-run alone would take it there.

**H0.** Merging adds nothing beyond a re-run. Such a COG reaches 0.75 about as often as a single-KO COG with the same starting PP and size, where nothing was merged.

## The natural experiment

- **Retest group, 1,887 COGs.** One member KO. The COG holds exactly the KO's sequences, and its trimmed alignment is identical to the KO's (checked for all 1,887). Only the gene trees and the reconciliation were run again. The KO value is the median of five runs and the COG value is one run.
- **Merge group, 1,201 COGs.** Two or more member KOs (477 have two, 249 three, 148 four, 327 five or more; the largest has 40). The COG's sequences are the union of its KOs' sequences in 1,200 cases; COG3321 has one extra sequence (Jaccard 0.958).

## Inputs (exact)

Paths are under `experiments/` unless noted. Downloads used User-Agent `open-research-site/1.0`. Python reads them with `-I`.

| File | Source | sha256 |
|---|---|---|
| `t5_wehbi_moody/raw/moody_springer_esm/41559_2024_2461_MOESM4_ESM.tsv` | Moody 2024, Supplementary Data 1 (9,365 KEGG families); already in the repo | 1a769b73b2945f1ff62c175a581b61ee27049b74fa8177fdcf917cd36233c3c0 |
| `t5_wehbi_moody/raw/moody_springer_esm/41559_2024_2461_MOESM5_ESM.tsv` | same paper, Supplementary Data 2 (3,088 COGs); already in the repo | 7e1f361a0b88706cb29d2eb3eb1ae19297f26eeea00e0375eb30d2eebfa7cf5a |
| `luca_calib/raw/moody/Supp_data/Genome_Size_Number_estimates/COG_test/COG_LUCA_PP.csv` | deposit copy of the COG PP column; read only | bd7388d9f553330a27448fac6ccc7ef6ed1c6d4d6c9b9e90abaf8a0bf32221ff |
| `luca_calib/raw/moody/Supp_data.zip` | Moody 2024 deposit, doi:10.6084/m9.figshare.24428659; already in the repo; read only, never unpacked | 4e3bbbf5ff0ed14cca3e774e9929f1d031d7e0f2b869fed79f4ff004fa0cefe4 |
| `t6_moody_ko_cog/raw/europepmc/PMC11383801_fulltext.xml` | Europe PMC full text of the paper | 06f36feba0d96f19864a5582b06a03350875457aa29fd84c4bdfa7010dbc7736 |
| `t6_moody_ko_cog/data/cog_ko_sets.tsv` | built by `scripts/build_sets.py` from the zip | 5234bb37261c5c2e0e7bdb4815281289ccefa6d5befea3f6a2e009ad8aea93b6 |
| `t6_moody_ko_cog/scripts/build_sets.py` | this study | 02ed67a600cacc9299457d9a5242552fb5d43392802daba678a96a49f3400e0f |
| `t6_moody_ko_cog/scripts/t6_analysis.py` | this study | a07524fae79b445455fbac3fccac3112a87213de9708eb48c6f62b8e3181d89b |
| `t6_moody_ko_cog/scripts_out/t6_gate.json` | `gate` output | b3754e58d0ddfcc0c4595384b81051992efab7b9d0586dce0906e6b6902865b0 |
| `t6_moody_ko_cog/scripts_out/t6_planted.json` | `planted` output | e8b57a3c7d9ff2f5eb6b0709b7fe250811331340c3f1943ae20d6dc5ddc34644 |
| `t6_moody_ko_cog/scripts_out/t6_dryrun_permuted_pp.json` | `dryrun` output | c6cad12b23c1da60d36723d4515d815f17bd333af0e4f07f7cf8ced56dd908a9 |

Notes on the inputs.

- Nothing new was downloaded except the Europe PMC full text and the prior-art search responses (`raw/prior_art/`). The plan expected range requests into the figshare zip; the zip was already in the repo, so none were made.
- Free disk was 10 GB at the start and 5.9 GB at the end. This study wrote under 2 MB; another job on the machine used the rest.
- Nothing under `experiments/luca_calib` was modified.
- `t6_analysis.py` checks the sha256 of every file it reads and stops on a mismatch.

## Gate (`t6_analysis.py gate`; run; passed)

| Check | Result |
|---|---|
| Rows in Supplementary Data 1 | 9,365 |
| KOs flagged `Probable_and_sampling_threshold_met` | 399, the paper's "conservative subset of 399 KOs" |
| Rows in Supplementary Data 2 | 3,088 |
| COG PP column equals the deposit's `COG_LUCA_PP.csv` | yes |
| Every COG is the modal COG of at least one KO, and its `Modal_KEGG_ko` is one of them | 3,088 of 3,088 |
| Retest COGs whose sequence set equals the KO's | 1,887 of 1,887 |
| Retest COGs whose trimmed alignment is identical to the KO's | 1,887 of 1,887 |
| Merge COGs whose sequence set equals the union of their KOs | 1,200 of 1,201; smallest Jaccard 0.958 |

The plan asked for 30 random single-KO COGs. The files were local, so the gate covers all 3,088 COGs.

**What the plan had wrong.**

- The plan's blind check said the 1,887 single-KO COGs "have the same archaeal and bacterial domain proportions in both tables". That check carries no information. Supplementary Data 2 copies those columns from the modal KO (`sequences_in_modal_KEGG`, `arc_domain_prop`, `bac_domain_prop`). The sequence files are the real check, and they pass.
- The plan gave the merge sizes as 542, 279 and 167, "up to 78". Counting member KOs through the `COG` column of Supplementary Data 1 gives 477, 249 and 148, up to 40. The totals agree (1,887 and 1,201).
- The plan did not say which KO column to use. The caption of Supplementary Data 2 settles it: the constrained topology, so `constrained_median`.
- In 982 merge COGs the member KOs share sequences with each other. The deposit names the COG files `_duprem`, and the COG keeps each sequence once.

## Blind counts (KO side only; taken before the design was fixed)

A COG is eligible when every member KO has a PP and every one is below 0.5.

| | Retest group | Merge group |
|---|---|---|
| COGs | 1,887 | 1,201 |
| A member KO has no PP | 0 | 492 |
| Eligible | 1,505 | 433 (36% of the group) |
| Median sequences per eligible COG | 82 | 233 |

Eligible COGs by the largest member-KO PP (x):

| x | 0 to 0.1 | 0.1 to 0.2 | 0.2 to 0.3 | 0.3 to 0.4 | 0.4 to 0.5 |
|---|---|---|---|---|---|
| Retest | 1,171 | 144 | 75 | 72 | 43 |
| Merge | 241 | 65 | 47 | 50 | 30 |

Eligible COGs by x and by size third (cut points 127 and 348 sequences, the thirds of the eligible merge group):

| x | Retest: small, middle, large | Merge: small, middle, large |
|---|---|---|
| 0 to 0.1 | 804, 267, 100 | 109, 83, 49 |
| 0.1 to 0.2 | 59, 61, 24 | 16, 19, 30 |
| 0.2 to 0.3 | 30, 35, 10 | 8, 16, 23 |
| 0.3 to 0.4 | 17, 37, 18 | 7, 17, 26 |
| 0.4 to 0.5 | 16, 21, 6 | 5, 9, 16 |

**The decision is non-empty.**

- Support needs at least 61 rescued COGs (5% of 1,201). 433 are eligible, so up to 433 can be rescued.
- Every one of the 15 cells that holds merge COGs also holds retest COGs. The smallest such retest cell has 6.
- The retest group is a re-run and not a copy (the three-level answer above).
- A kill is reachable at any noise level (planted rows below).

## Fixed decisions

- **D1, units and groups.** The 3,088 COGs of Supplementary Data 2. A COG's member KOs are the rows of Supplementary Data 1 whose `COG` column names it. Retest group: one member. Merge group: two or more.
- **D2, PP values.** KO: `constrained_median`. COG: `PP` in Supplementary Data 2. x is the largest member-KO PP. y is the COG PP.
- **D3, thresholds.** Eligible: every member KO has a PP and each is below 0.5. Rescued (merge group) or flipped (retest group): eligible and y ≥ 0.75. These are the plan's thresholds.
- **D4, KOs without a PP.** A COG with such a member is not eligible. These KOs are mostly one to three sequences, so merging one into a larger KO is close to a re-run and would blur the merge group. Counting them as "below 0.5" is reported only.
- **D5, strata.** Five bins of x (edges 0, 0.1, 0.2, 0.3, 0.4, 0.5) by three bins of COG size in sequences (up to 127, 128 to 348, over 348). 15 strata.
- **D6, statistic.** Rescue rate R = rescued ÷ eligible merge COGs. Matched flip rate F = the retest group's flip rate in each stratum, weighted by the eligible merge group's share in that stratum. Ratio = R ÷ F. Matching gives both groups the same spread of starting PP and of family size.
- **D7, interval.** R has a Beta posterior with half a count of prior on each side (Jeffreys). Each stratum's flip rate has a Beta posterior whose prior is half a count on each side divided by 15, so the whole retest side carries the same half count. 4,000 joint draws. The estimate is the median of the ratio and the interval is its 2.5th to 97.5th percentile. No resampling of families is involved.
- **D8, void.** If more than 95% of retest COGs have y equal to x (to 1e-9), the retest group is a copy and the verdict is "void".
- **D9, seed.** 20261126. Generators: `[seed, 2]` planted, `[seed, 3]` real, `[seed, 4]` dryrun. `gate` uses no random numbers.
- **D10, order of runs.** `gate`, `planted`, `dryrun`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with the script's current sha256.

## Decision rules

- **Kill.** The lower bound of the ratio is at or below 2. Merging then adds nothing that a re-run does not.
- **Support.** The lower bound is above 2, the ratio is at least 5, and at least 5% of the merge group is rescued (61 of 1,201).
- **Otherwise.** "Partly": rescue beats re-run noise, but it is small or the ratio is under 5.

## Changes from the plan, made before the seal

The plan's rule was: rates as shares of each whole group, kill if the interval for their ratio includes 2, support at ratio ≥ 5 with ≥ 5% of merged COGs rescued. The thresholds are unchanged. Three things in the form of the rule changed, and the planted check is the reason for each.

1. **Rates are taken among eligible COGs.** Only 36% of the merge group is eligible against 80% of the retest group, because "every member below 0.5" is harder to meet with more members. With no rescue at all, the plan's ratio comes out near 0.5 where it should be 1, and a true ratio of 12 reads as 5 (planted rows, column "plan rule").
2. **The retest rate is matched on starting PP and on size.** Eligible merge COGs start closer to 0.5 and are about three times larger. If noise grows with family size and nothing is rescued, matching on PP alone reads 1.3 to 1.4, and matching on both reads 1.0 to 1.1.
3. **The interval is a posterior, and the prior count is shared across strata.** Flips may number a handful, and a bootstrap cannot move a zero. A first version gave each of the 15 strata its own half count. That inflated the flip rate and cut the ratio by about half under planted rescue (5.2 where the truth was about 12). Sharing one half count across the strata removed the bias. This was found and fixed in the planted run, before any real pairing.

The "5% of merged COGs" condition still uses the whole merge group as its base, as the plan wrote it.

## Planted check (`t6_analysis.py planted`; run; synthetic COG PP only)

Every replicate keeps the real KO PPs, groups, member lists and sizes. It never reads the COG PP column. 300 replicates per row. Script sha256 a07524fa….

**How a synthetic re-run is made.** A COG starts from x. With probability q it gets an unrelated PP, drawn from the pool of all KO PP values (9.1% of the pool is at or above 0.75). Otherwise it keeps x with a jitter of 0.03. The value of q is unknown, so the rows cover 0 to 0.4.

- **Null.** Merge COGs are re-run like any other.
- **Rescue.** As the null, and a share p of the eligible merge COGs is set to a PP between 0.75 and 1.
- **Noise by size.** No rescue. q rises with family size, the same way in both groups.
- **Noisier merge.** No rescue. The merge group's q is 2 or 4 times the retest group's, at any size.

| Planted | Rescued, flipped (mean) | Ratio, plan rule | Ratio, x only | Ratio, primary (mean 95% interval) | P(kill) | P(partly) | P(support) |
|---|---|---|---|---|---|---|---|
| Null, q = 0 | 0, 0 | 1.6 | 2.0 | 1.7 (0.0 to 1,224) | 1.00 | 0.00 | 0.00 |
| Null, q = 0.02 | 0.7, 2.8 | 0.4 | 0.8 | 0.8 (0.1 to 237) | 1.00 | 0.00 | 0.00 |
| Null, q = 0.05 | 2.1, 6.8 | 0.5 | 1.0 | 1.0 (0.2 to 7.2) | 1.00 | 0.00 | 0.00 |
| Null, q = 0.1 | 3.9, 13.8 | 0.5 | 1.0 | 1.0 (0.3 to 3.3) | 1.00 | 0.00 | 0.00 |
| Null, q = 0.2 | 7.9, 27.9 | 0.5 | 1.0 | 1.0 (0.4 to 2.4) | 1.00 | 0.00 | 0.00 |
| Null, q = 0.4 | 16.0, 54.4 | 0.5 | 1.0 | 1.0 (0.6 to 1.9) | 1.00 | 0.00 | 0.00 |
| Rescue, q = 0.1, p = 0.02 | 12.6, 14.1 | 1.4 | 3.1 | 3.1 (1.4 to 8.3) | 0.84 | 0.16 | 0.00 |
| Rescue, q = 0.1, p = 0.05 | 25.7, 13.3 | 3.1 | 6.6 | 7.0 (3.3 to 17.0) | 0.11 | 0.89 | 0.00 |
| Rescue, q = 0.1, p = 0.1 | 46.6, 13.8 | 5.4 | 11.7 | 11.8 (6.0 to 27.3) | 0.00 | 0.97 | 0.03 |
| Rescue, q = 0.1, p = 0.15 | 68.9, 13.9 | 7.8 | 16.9 | 17.8 (9.3 to 41.3) | 0.00 | 0.13 | 0.87 |
| Rescue, q = 0.1, p = 0.2 | 89.9, 13.8 | 10.3 | 22.4 | 23.4 (12.4 to 54.7) | 0.00 | 0.00 | 1.00 |
| Rescue, q = 0.1, p = 0.3 | 133.0, 13.5 | 15.8 | 33.7 | 35.0 (18.9 to 84.3) | 0.00 | 0.00 | 1.00 |
| Rescue, q = 0.1, p = 0.5 | 219.0, 13.8 | 24.4 | 53.3 | 56.0 (29.6 to 124) | 0.00 | 0.00 | 1.00 |
| Rescue, q = 0.02, p = 0.1 | 44.2, 2.7 | 24.8 | 51.2 | 55.4 (13.2 to 12,102) | 0.00 | 0.99 | 0.01 |
| Rescue, q = 0.02, p = 0.3 | 130.4, 2.8 | 70.4 | 156 | 169 (40.2 to 35,553) | 0.00 | 0.00 | 1.00 |
| Rescue, q = 0.4, p = 0.3 | 140.7, 55.0 | 4.0 | 8.9 | 8.9 (6.3 to 13.4) | 0.00 | 0.00 | 1.00 |
| Rescue, q = 0.4, p = 0.5 | 225.3, 54.9 | 6.5 | 14.3 | 14.3 (10.1 to 20.9) | 0.00 | 0.00 | 1.00 |
| Noise by size, q = 0.1 | 4.7, 10.7 | 0.7 | 1.3 | 1.0 (0.4 to 4.1) | 1.00 | 0.00 | 0.00 |
| Noise by size, q = 0.2 | 9.4, 20.8 | 0.7 | 1.4 | 1.1 (0.5 to 2.7) | 1.00 | 0.00 | 0.00 |
| Noise by size, q = 0.4 | 18.2, 42.1 | 0.7 | 1.3 | 1.1 (0.6 to 1.9) | 1.00 | 0.00 | 0.00 |
| Noisier merge, 2 times | 8.1, 13.5 | 1.0 | 2.1 | 2.2 (0.8 to 6.0) | 0.98 | 0.02 | 0.00 |
| Noisier merge, 4 times | 15.9, 13.7 | 1.8 | 3.9 | 4.0 (1.9 to 10.8) | 0.63 | 0.37 | 0.00 |

The verdict columns are for the primary rule.

What the table shows.

- **The null works.** With no rescue the primary ratio is 1.0 and every replicate is a kill, at every noise level.
- **Both verdicts are reachable.** Kill has probability 1.00 under the null. Support has probability 1.00 once about 90 eligible merge COGs are rescued (p = 0.2).
- **The 5% condition is what separates partly from support.** At p = 0.1 the ratio is near 12 and 47 COGs are rescued, short of 61, so the verdict is "partly" 97% of the time.
- **No null row ever gives support.** The worst null, a merge group four times noisier, gives "partly" 37% of the time.
- **The plan's rule was miscalibrated.** Its null ratio is 0.5, and at high noise it would have called a true ratio of 9 "partly" (q = 0.4, p = 0.3).
- **With zero flips the interval is very wide** (null, q = 0). The verdict is still a kill, because no COG is rescued.

**Dry run.** `t6_analysis.py dryrun` runs the full `real` code, including every reported-only extra, on COG PP permuted over all COGs. It ran without error and gave a ratio of 0.98 (0.75 to 1.28), a kill, as it should. Its other numbers are synthetic.

## Reported only (no rule attached)

`real` also prints these. None can change the verdict.

- **Test-retest reliability, retest group.** The share of single-KO COGs whose call at 0.5 changes, in each direction. The share that moves by more than 0.25 and by more than 0.5. The median absolute change, the mean change and the correlation. The same call-change share for KOs with `COG_perc` ≥ 0.9. This adds to the "810 families differ by more than 0.5 between runs" finding.
- The plan's rule (shares of the whole groups) and the rule matched on x alone, each with the verdict it would have given.
- Thresholds 0.5 to 0.5 and 0.25 to 0.75.
- The retest group limited to KOs with `COG_perc` ≥ 0.9.
- KO side taken from `ML_median` and from `MEAN_OF_MEDIANS`.
- A member KO without a PP counted as below 0.5 (785 eligible merge COGs).
- The merge group split into two KOs and three or more.
- **Downward mirror.** COGs whose best member KO is at or above 0.75 and whose COG PP is below 0.5, in each group. If merged families are simply noisier, this rises along with the rescues.
- The mean change between the best member KO and the COG in the merge group.
- **Second null from the plan, KO side only.** The eligible share of the real merge group against 1,000 random regroupings of the same KOs into groups of the same sizes.
- The lists of rescued and flipped COG ids.

## Ways it could be fooled, and limits

1. **A noisier merge group looks like rescue.** A merged family has a new alignment and a larger tree. If that alone makes its PP jump more often, in both directions, the ratio rises with nothing rescued. Four times the noise gives "partly" in 37% of planted runs. It never gives support. The downward mirror is the check.
2. **Size is matched in thirds.** Inside a third, merge COGs can still be larger. Planted noise by size leaves a ratio of 1.0 to 1.1.
3. **The retest is not a full re-run.** The alignments are identical, so alignment noise is absent from the null. Merged families were aligned afresh. This makes the null a little too quiet, which favours H1.
4. **One run against a median of five.** A single run is noisier than a median, in both groups alike. The flip rate is therefore not the noise between two single runs.
5. **x is the best member.** A merged COG is compared with a re-run of its highest-PP KO. Another reference (the modal KO, or a weighted mean) would give more rescues. The choice is the conservative one.
6. **Moody's PP is not ground truth.** A rescued COG is one whose PP rose. Whether the family was in LUCA is a separate question.
7. **Origination rates.** Moody fitted root origination rates by COG category. If the COG run used different fitted values from the KO run, every COG shifts, in both groups. Matching absorbs a common shift only in part. The mean change in each group is reported.
8. **KOs with no PP are left out.** 492 merge COGs have one. The lenient version is reported and may disagree.
9. **COGs are not independent.** Sequences can sit in KOs that belong to different COGs. The interval treats COGs as independent, so it is somewhat too narrow.
10. **The synthetic re-run is a guess.** Real noise may depend on x, on size and on breadth in ways the planted model lacks. The planted check shows that the rule is calibrated for this model, not for the truth.
11. **One threshold pair decides.** Two other pairs are reported.

## Sources actually opened

- Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1: full text from Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11383801/fullTextXML`), Supplementary Data 1 and 2, and the deposit doi:10.6084/m9.figshare.24428659 (`README.txt`, the member list, the COG and KO sequence files, the trimmed alignments, `COG_LUCA_PP.csv`, `merge2.py`).
- Prior art: `experiments/t6_moody_ko_cog/PRIOR_ART.md` lists every search, with the five abstracts read.
