# Pre-registration (T12): does ribozyme specificity really rise with activity, or is it the background floor and shared noise?

Status: DRAFT, written 2026-11-25 by the T12 prep agent. This is study N1 in `docs/plans/next_studies_2026-11-25.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run, and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t12_janzen_specificity/scripts/t12_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is the pairing of each sequence's total activity with the shape of its substrate profile, once the background floor and measurement noise are taken out. Every deciding number comes from that pairing.

- **Not computed.** No real R_adj on any subset, raw or corrected. No real SIMEX estimate. No real profile-swap null. No real correlation between activity and the index other than the paper's own test below.
- **One joint look, taken on purpose: the paper's own test.** `gate` reproduces Table 1: Pearson and Spearman of total activity against the promiscuity index (and against aromatic preference) over all 1,954 sequences of each family. The values match the paper to 0.0005 (table under "Gate"). This test includes the floor, which is the artefact under study, so it says little about the answer.
- **The co-option count is published, so it is not a peek.** The number of sequences with r > 5 on at least two substrates is in the Results text (254, 278, 1,029, 853, 43) and in the Source Data sheet "Figure 5". `gate` recomputes the Fig. 5 histograms from the rates and they match the sheet exactly. The count uses the profile, but only the number per family was seen, and it is the paper's own figure. It is used only to set which families are eligible (D8).
- **Activity-only and noise-only marginals.** I saw:
  - the size of the primary subset, all_sum > 30: 159, 206, 1,064, 1,136 and 37 sequences for 1A.1, 1B.1, 2.1, 2.2, 3.1;
  - floor counts (max r ≤ 3): 1,454, 1,468, 569, 320, 1,490;
  - the deposited bootstrap noise as log-sd per cell: 10th, 50th and 90th percentiles 0.136, 0.262 and 0.534; and how it rises with the cell's own level (median about 0.24 at the floor, 0.27 to 0.30 at log10 r of 0.5 to 1, 0.38 to 0.54 above log10 r of 1).
  The noise-by-level table pairs a cell's rate with its own noise. It does not pair a sequence's total with its profile shape.
- **The planted check uses real activity and real noise.** Synthetic families take the real all_sum of each sequence and either noise drawn by level from the real noise bank or, in the "real per-cell noise" rows, each real sequence's own six noise values. Those six values carry some trace of the real profile, because noise rises with level. Only synthetic verdicts and means were printed.
- **Dry run.** `dryrun` runs the full `real` code with activity permuted within family (each sequence keeps its above-floor profile shape and takes another sequence's total). Its numbers are disclosed below. They involve real profile shapes but no real pairing of shape with activity.
- **Pilot and diagnostic runs, all synthetic.** Three calibration scripts (`scripts/diag_planted.py`, `scripts/diag2.py`, `scripts/diag3.py`) and a 3-replicate pilot of an earlier `planted` were run on synthetic profiles only. They showed that every form of the plan's profile-swap null is miscalibrated (see "Changes from the plan") and that SIMEX is not.
- **What this does to my expectation.** I have none on the sign. The planted check shows that with no link at all, the raw R_adj on the primary subset is −0.03 to −0.32 (synthetic family means), and the full-sample R of the paper's Table 1 test is −0.32 to −0.74 in the same synthetic nulls. The published values (−0.54 to −0.84) sit at or just beyond that range. So both the paper's R and a raw R_adj of that size carry no information by themselves.

## Claim under test

Janzen, Shen, Vázquez-Salazar, Liu, Blanco, Kenchel, Chen 2022, "Emergent properties as by-products of prebiotic evolution of aminoacylation ribozymes", Nat. Commun. 13:3631, doi:10.1038/s41467-022-31387-0 (PMC9233669, read from `experiments/t12_janzen_specificity/raw/europepmc/PMC9233669_fulltext.xml`).

- Abstract, verbatim: "Furthermore, ribozyme activity was positively correlated with specificity, indicating that selection for increased activity would also lead to increased specificity."
- Results, verbatim: "The promiscuity index … is a normalized entropy which describes the evenness of the distribution of rates across different substrates. … Promiscuity was observed to decrease as overall activity increased for all families (Fig. 4 and Supplementary Fig. 7)."
- Table 1 caption, verbatim: "Correlations between overall catalytic activity and specificity for each ribozyme family (Pearson's R and Spearman's ρ; n = 1954, p-values < 10−95 in each case (two-sided))."
- Rate, verbatim: "we determined catalytic enhancement, i.e., the ratio of catalyzed to background reaction rates."
- Threshold, verbatim: "An activity threshold of rt = 5 was chosen for two reasons. First, this threshold is two-fold more than the estimated 95% range for background activity (Supplementary Fig. 4, Supplementary Table 2)".
- Discussion, verbatim: "Substrate preferences were amplified with increasing activity, resulting in a positive correlation between activity and substrate specificity."

**Why it might be an artefact.** Two reasons.

1. *The floor.* r is the rate divided by the background, so an inactive sequence has r near 1 on all six substrates and an index near 1, whatever its preferences. If r = 1 + A·p with a fixed preference profile p, the index rises toward 1 as the activity A falls. A negative R over all 1,954 sequences follows from the definition.
2. *Shared noise.* Total activity and the index are computed from the same six noisy cells. If the peak cell is overestimated, the total goes up and the profile looks more peaked, both at once. In the planted nulls this alone gives R_adj of about −0.2 on sequences well above the floor.

**H1.** Among active sequences, those with higher total activity have more uneven above-background profiles, beyond what the floor and shared noise produce.

**H0.** Once the floor is subtracted and the shared noise is corrected, profile evenness does not depend on total activity.

## Inputs (exact)

Paths are under `experiments/t12_janzen_specificity/`. Downloads used User-Agent `open-research-site/1.0` and carried no personal details. Python reads every downloaded file with `-I`, and scripts live in `scripts/`. `raw/` and `cache/` are gitignored (checked with `git check-ignore`), because the data are third-party.

| File | Source | sha256 |
|---|---|---|
| `raw/esm/41467_2022_31387_MOESM3_ESM.xlsx` | Source Data, 17,604,475 bytes, `https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-022-31387-0/MediaObjects/41467_2022_31387_MOESM3_ESM.xlsx` | 78471fb417347bdc84129b48d27904ae942eab2fd022d84e0d311b3112ba329c |
| `cache/sd/sheet2.tsv` | sheet "Figure 2" (9,770 sequences × 128 columns: fits, bootstrap summaries, r and its 2.5/97.5% bounds per substrate), written by `scripts/xlsx_to_tsv.py` | 412299ffb2838201fef3e107c5feb368e41d71f250d65de182ed486b4137bf45 |
| `cache/sd/sheet4.tsv` | sheet "Figure 4" (sequence, family, six r, all_sum, I) | e1acbc71ced4886cbdfbc698321d0cbadcc48210119fdaea60568e01eb448069 |
| `cache/sd/sheet5.tsv` | sheet "Figure 5" (co-option histograms) | 721d9b6a7abc2c23ceaa05787d9f330b13c6fb2c85fa3b1acb5dd6de471f2f22 |
| `cache/sd/sheet1.tsv`, `sheet3.tsv`, `sheet6.tsv` | other sheets, not used | d789660f…, a5e95a74…, ca82c9f8… |
| `raw/esm/41467_2022_31387_MOESM1_ESM.pdf` | Supplementary Information | f983e587fde692b19ebab8e7b8252770a659489a4241f66fa3949cb0d4d5f7b4 |
| `raw/europepmc/PMC9233669_fulltext.xml` | Europe PMC full text | 9eb3620710c011e9ff94045e65cb73f7aa68dc005de2518b12ad6c7179698df7 |
| `raw/github/` | authors' scripts, `ichen-lab-ucsb/WFLIVM_k-Seq` at 68990737c2257cef2815d7df74e2f7686bc5a597; read, never run | BackgroundNormalizer.py c1693f5c…, PromIndexPlot.py 2aaafb57…, PromIndex_TableMaker.py b4e07149…, PromIndexResultsMerger.py 5d51ae88…, CoOptionCounterBarPlot.py 17ee9697… |
| `scripts/xlsx_to_tsv.py` | this study; stdlib only, reads the xlsx through `zipfile` | db025c15ce8b5b5d3f4a61a39a2d365e152ef15cc13fad0f2f0c1ff122f7dfa0 |
| `scripts/t12_analysis.py` | this study | 84183003314faac72afb2c0f79cc55c89866b94845deb4ba0a1d585269c3ea85 |
| `scripts/diag_planted.py`, `diag2.py`, `diag3.py` | calibration diagnostics, synthetic only | 3bc4f02a…, 68ce0073…, 60ba2a8f… |
| `scripts_out/t12_gate.json` | `gate` output | a1bfee69b962e14e3185a8858d35255f7bf859407a1e63e3f8d711e792da98c6 |
| `scripts_out/t12_planted.json` | `planted` output (merged from four parts) | 5f6fc43184b8197e21149b4fb4b1de0a435c351181245e106bd1fcdf1ef93dd3 |
| `scripts_out/t12_dryrun_permuted_activity.json` | `dryrun` output | e9c8236a0e8de02a873e0c70b60e4e8e0155aef9ffc9d416e99ccbf7a789a557 |

- `t12_analysis.py` checks the sha256 of the xlsx and the three TSVs it reads, and stops on a mismatch.
- The workbook's internal metadata contains a file path from the authors' machine. It is not copied anywhere.
- Python: `experiments/t1_vent_exergonic/.venv` (numpy 2.5.5, scipy 1.18.1), run under `nice -n 20` with one thread.

## Gate (`t12_analysis.py gate`; run; passed)

| Check | Result |
|---|---|
| Sequences in sheet "Figure 2"; in sheet "Figure 4" | 9,770; 9,770 (1,954 per family), the same sequences |
| r in "Figure 4" vs "Figure 2" | identical |
| r = bootstrap-median k·A / background (Supp. Table 2: BWO 1.57, BFO 1.37, BLO 1.46, BIO 0.87, BVO 1.21, BMO 2.14) | worst relative difference 1e-14 |
| all_sum = Σ r | exact |
| Index recomputed as normalised Shannon entropy of r / all_sum | worst difference 3.3e-7 from the sheet |
| Table 1, Pearson R(all_sum, I), recomputed vs published | 1A.1 −0.6955 (−0.696), 1B.1 −0.839 (−0.839), 2.1 −0.535 (−0.535), 2.2 −0.538 (−0.538), 3.1 −0.814 (−0.814); all ρ and both aromatic columns within 0.0005 |
| Fig. 5 histograms recomputed from r > 5 vs sheet "Figure 5" | identical in all five families |
| Sequences active on ≥ 2 substrates | 254, 278, 1,029, 853, 43 (as in the text) |
| Plan's gate: at least 3 families with ≥ 200 such sequences | 4 (1A.1, 1B.1, 2.1, 2.2); passed |

The authors' `PromIndexPlot.py` shows that Table 1 uses raw all_sum (not log) against the index from the online calculator. The index sheet holds the calculator's output; my recomputation matches it.

## Fixed decisions

- **D1, rates.** r_s,i from sheet "Figure 2" (`r_<sub>`, the paper's catalytic enhancement). Noise σ_s,i = (ln r97.5% − ln r2.5%) / 3.92, from the deposited bootstrap bounds of the same cell.
- **D2, subset (primary).** Sequences with all_sum > 30. This is the paper's own cut (Fig. 6 caption, verbatim: "having substantial overall activity (∑XrsBXO>30)"; Results: "in analogy to rt = 5 for 6 substrates"). It selects on activity alone. The plan's subset (r > 5 on at least two substrates) is reported only (see "Changes").
- **D3, floor removal.** a_s,i = max(r_s,i − 1, 0). I_adj is the normalised Shannon entropy of a_s / Σa_s (0 log 0 = 0).
- **D4, statistic.** R_adj = Pearson(log10 all_sum, I_adj) on the subset, per family.
- **D5, noise correction (primary): SIMEX, quadratic.** For λ in {0.5, 1, 1.5, 2}, multiply every cell by exp(√λ · σ_s,i · ε) with ε ~ N(0, 1), re-select the subset (all_sum > 30 on the noised data), recompute R_adj, and average over K draws. Fit a quadratic in λ to the five points (λ = 0 is the observed R_adj) and read it at λ = −1. That is R_S. Only sequences with observed all_sum > 12 are carried, since a sequence below that has a negligible chance of crossing 30 under the added noise. K = 100 for `real`.
- **D6, interval.** 400 bootstrap resamples of the carried sequences; SIMEX redone inside each one with 10 draws per λ; quadratic fitted per resample; 2.5th to 97.5th percentile.
- **D7, per-family verdict.**
  - **Kill:** the interval's upper end ≥ 0, or R_S > −0.05.
  - **Support:** not a kill, and R_S ≤ −0.15.
  - **Otherwise "partly".**
- **D8, eligible families and overall verdict.** Eligible: families whose published count of sequences active on ≥ 2 substrates is at least 200 (the plan's gate number): 1A.1, 1B.1, 2.1, 2.2. Fam3.1 (43) is reported only. **Support** if at least 3 of the 4 eligible families say support. **Kill** if at least 3 of 4 say kill. Otherwise **mixed**.
- **D9, seed.** 20261125. Generators: `[seed, 2, scenario]` planted, `[seed, 3]` real, `[seed, 4]` dryrun. `gate` uses no random numbers.
- **D10, primary rule.** `primary` in the script.
- **D11, order of runs.** `gate`, `planted`, `dryrun`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with its current sha256.

## Decision rules

Stated in D7 and D8. In words: the paper's claim survives only if, in at least three of the four large families, the noise-corrected correlation between log activity and the evenness of the above-background profile is −0.15 or stronger, with a 95% interval below 0. It dies if in at least three of them the interval reaches 0 or the estimate is weaker than −0.05.

## Changes from the plan, made before the seal

The plan's rules were:
- R_adj on sequences with r > 5 on at least two substrates, background subtracted and floored at zero;
- a null that keeps each sequence's total activity, swaps its above-background profile with a random same-family sequence, adds the background back and draws noise from the bootstrap SDs, 2,000 draws;
- kill if in at least 4 of 5 families the observed R is inside the central 95% of the null, or the R_adj interval includes 0;
- support if in at least 4 of 5 families R_adj ≤ −0.3 with an interval excluding 0, and the observed R is below the null's 2.5th percentile.

The floor subtraction (D3), the statistic (D4), the interval-excludes-zero clause and the idea of a calibrated null are kept. Four things changed. All are documented with synthetic numbers.

1. **The profile-swap null is replaced by SIMEX.** No version of the swap null was calibrated in synthetic families with no link:
   - *As written* ("plain": the donor profile is already noisy, then fresh noise is added): the null gets double noise, so it is too noisy and hides real links. With rescaling to the observed totals it still overshot.
   - *Donor noise only* ("donor"): keeps the donor's own noise. Because high-activity donors carry their own shared-noise artefact, it is biased toward false support.
   - *Empirical-Bayes-smoothed donors* ("eb"): conservative without rescaling, and over-shooting with it.
   - The underlying reason is that the artefact sits in the pairing of each sequence's own noise with its own total. A swap null breaks that pairing, so it removes the artefact from the null but not from the observed value, or adds it twice.
   SIMEX corrects the observed statistic directly. In the planted nulls the corrected value centres on 0 (table below). The swap nulls are still computed and reported.
2. **The primary subset is all_sum > 30, not "r > 5 on ≥ 2 substrates".** The plan's subset selects on the profile. A sequence passes it more easily if its profile is even. That builds a link between activity and evenness into the subset. The paper's own all_sum > 30 cut selects on activity only. The plan's subset is reported (raw R_adj and the plan's rule).
3. **The support threshold is −0.15, not −0.3, and it is on the corrected value.** The plan set −0.3 on the raw R_adj, presumably to clear the artefact. After SIMEX the artefact is gone, so −0.3 would demand a large effect. With the real activity spread, a planted link of γ = 0.2 gives a true R_adj of about −0.2. Kill below −0.05, support at −0.15 or stronger, "partly" between.
4. **Overall rule: 3 of the 4 eligible families, not 4 of 5.** Fam3.1 has 43 sequences active on two substrates and 37 with all_sum > 30, too few for any interval to exclude 0 (planted interval width about ±0.4). Requiring it would make support nearly unreachable for reasons of sample size. The plan's own gate number (200) sets eligibility. The 4-of-5 version is reported.

How the plan's rule performs on the same synthetic families is in the column "plan as written" below. Its false-support rate reaches 17% (τ = 0.4) under the nulls.

## Planted check (`t12_analysis.py planted`; run; synthetic profiles only)

Every replicate keeps each family's 1,954 real all_sum values and the real noise, and never reads a real profile. 100 replicates per row. In each replicate SIMEX uses 20 draws per λ for the point estimate and 60 bootstrap resamples with 10 draws per λ for the interval (fewer than `real`, for time). The swap nulls use 200 draws. Script sha256 84183003….

**How synthetic families are made.**
- A = max(all_sum − 6, 0), the real activity above floor.
- Each sequence gets log-preferences θ_f + τ·ε (θ_f is a fixed per-family shape, ε ~ N(0, 1) per substrate), multiplied by g = exp(γ z), where z is the standardised log(A + 1). Preference p = softmax of that.
- γ = 0 is the null: the profile shape does not depend on activity. γ > 0 plants a link: more active sequences have more peaked profiles.
- The true rate is floor + A·p. The floor varies by substrate around 1 with the spread of Supp. Table 2 (or is exactly 1 in "no floor variation").
- Measured rates multiply each cell by exp(σ ε). σ is drawn from the real noise bank by substrate and level ("level"), or is the real sequence's own six σ ("real per-cell noise"). In "correlated noise", the substrates measured together share half the noise variance.
- "Mixture of specialists": 40% of sequences get one random substrate boosted by +3 in log-preference.
- "True R_adj" is R_adj computed on the noise-free rates.

| Planted | True R_adj (1A.1 / 1B.1 / 2.1 / 2.2) | Raw R_adj | SIMEX R_S | Primary: kill, mixed, support | Plan as written: kill, mixed, support |
|---|---|---|---|---|---|
| Null, tau 0.7 | 0.00 / 0.01 / 0.01 / 0.00 | -0.08 / -0.19 / -0.21 / -0.23 | 0.04 / -0.04 / -0.03 / -0.03 | 0.99, 0.01, 0.00 | 0.00, 0.98, 0.02 |
| Null, tau 1.2 | -0.01 / 0.01 / 0.01 / 0.00 | -0.08 / -0.14 / -0.15 / -0.17 | 0.01 / -0.00 / -0.00 / -0.01 | 1.00, 0.00, 0.00 | 0.00, 0.98, 0.02 |
| Null, tau 0.4 | 0.03 / 0.02 / 0.01 / 0.01 | -0.10 / -0.22 / -0.25 / -0.27 | 0.01 / -0.06 / -0.07 / -0.07 | 0.97, 0.03, 0.00 | 0.00, 0.83, 0.17 |
| Null, no floor variation | 0.01 / 0.00 / -0.00 / 0.00 | -0.09 / -0.19 / -0.22 / -0.23 | 0.01 / -0.05 / -0.03 / -0.02 | 0.99, 0.01, 0.00 | 0.00, 0.93, 0.07 |
| Null, real per-cell noise | 0.01 / -0.00 / 0.01 / 0.01 | -0.03 / -0.06 / -0.19 / -0.18 | -0.02 / 0.03 / -0.03 / 0.01 | 1.00, 0.00, 0.00 | 0.00, 1.00, 0.00 |
| Null, mixture of specialists | -0.00 / 0.01 / 0.00 / 0.00 | -0.07 / -0.14 / -0.11 / -0.11 | 0.03 / -0.01 / 0.02 / 0.03 | 1.00, 0.00, 0.00 | 0.02, 0.95, 0.03 |
| Null, correlated noise within input groups | 0.00 / 0.01 / 0.00 / 0.00 | -0.10 / -0.19 / -0.22 / -0.24 | 0.01 / -0.03 / -0.04 / -0.04 | 0.99, 0.01, 0.00 | 0.00, 0.94, 0.06 |
| Link gamma 0.1 | -0.17 / -0.12 / -0.11 / -0.11 | -0.20 / -0.26 / -0.28 / -0.29 | -0.12 / -0.13 / -0.12 / -0.11 | 0.45, 0.52, 0.03 | 0.00, 0.05, 0.95 |
| Link gamma 0.2 | -0.28 / -0.22 / -0.21 / -0.23 | -0.31 / -0.33 / -0.35 / -0.37 | -0.24 / -0.22 / -0.22 / -0.24 | 0.01, 0.37, 0.62 | 0.00, 0.00, 1.00 |
| Link gamma 0.4 | -0.35 / -0.29 / -0.38 / -0.41 | -0.37 / -0.36 / -0.47 / -0.50 | -0.33 / -0.29 / -0.39 / -0.41 | 0.00, 0.07, 0.93 | 0.00, 0.00, 1.00 |
| Link gamma 0.2, real per-cell noise | -0.28 / -0.22 / -0.20 / -0.23 | -0.29 / -0.27 / -0.33 / -0.33 | -0.30 / -0.23 / -0.22 / -0.20 | 0.01, 0.20, 0.79 | 0.00, 0.00, 1.00 |
| Link gamma 0.2, mixture of specialists | -0.23 / -0.17 / -0.12 / -0.13 | -0.27 / -0.26 / -0.21 / -0.23 | -0.22 / -0.16 / -0.12 / -0.13 | 0.16, 0.75, 0.09 | 0.00, 0.00, 1.00 |

Per family (all five, including the reported-only Fam3.1):

| Planted | Support share per family, primary (1A.1 / 1B.1 / 2.1 / 2.2 / 3.1) | Kill share per family | SIMEX sd across replicates |
|---|---|---|---|
| Null, tau 0.7 | 0.01 / 0.08 / 0.00 / 0.01 / 0.08 | 0.99 / 0.92 / 0.96 / 0.90 / 0.92 | 0.14 / 0.15 / 0.06 / 0.06 / 0.30 |
| Null, tau 1.2 | 0.04 / 0.05 / 0.00 / 0.00 / 0.11 | 0.96 / 0.95 / 0.99 / 0.96 / 0.89 | 0.13 / 0.14 / 0.05 / 0.05 / 0.27 |
| Null, tau 0.4 | 0.02 / 0.10 / 0.08 / 0.08 / 0.08 | 0.98 / 0.90 / 0.83 / 0.79 / 0.92 | 0.15 / 0.14 / 0.06 / 0.06 / 0.29 |
| Null, no floor variation | 0.01 / 0.10 / 0.05 / 0.01 / 0.06 | 0.99 / 0.90 / 0.87 / 0.92 / 0.94 | 0.15 / 0.15 / 0.06 / 0.06 / 0.26 |
| Null, real per-cell noise | 0.03 / 0.01 / 0.02 / 0.00 / 0.07 | 0.97 / 0.99 / 0.91 / 1.00 / 0.93 | 0.13 / 0.13 / 0.05 / 0.05 / 0.37 |
| Null, mixture of specialists | 0.01 / 0.04 / 0.00 / 0.00 / 0.03 | 0.99 / 0.96 / 0.99 / 1.00 / 0.97 | 0.14 / 0.14 / 0.05 / 0.05 / 0.28 |
| Null, correlated noise within input groups | 0.02 / 0.07 / 0.03 / 0.04 / 0.04 | 0.98 / 0.93 / 0.94 / 0.88 / 0.96 | 0.13 / 0.14 / 0.06 / 0.06 / 0.24 |
| Link gamma 0.1 | 0.22 / 0.18 / 0.30 / 0.28 / 0.14 | 0.78 / 0.82 / 0.32 / 0.47 / 0.86 | 0.15 / 0.14 / 0.05 / 0.06 / 0.24 |
| Link gamma 0.2 | 0.49 / 0.51 / 0.91 / 0.95 / 0.23 | 0.51 / 0.49 / 0.03 / 0.00 / 0.77 | 0.12 / 0.12 / 0.05 / 0.05 / 0.24 |
| Link gamma 0.4 | 0.77 / 0.73 / 1.00 / 1.00 / 0.24 | 0.23 / 0.27 / 0.00 / 0.00 / 0.76 | 0.11 / 0.10 / 0.04 / 0.05 / 0.23 |
| Link gamma 0.2, real per-cell noise | 0.78 / 0.61 / 0.91 / 0.78 / 0.13 | 0.22 / 0.39 / 0.02 / 0.08 / 0.87 | 0.10 / 0.11 / 0.05 / 0.06 / 0.27 |
| Link gamma 0.2, mixture of specialists | 0.47 / 0.31 / 0.19 / 0.31 / 0.13 | 0.53 / 0.69 / 0.28 / 0.19 / 0.87 | 0.11 / 0.11 / 0.04 / 0.04 / 0.24 |

"Raw R_adj", "SIMEX R_S" and "True R_adj" are means over replicates. Verdict columns are shares of the 100 replicates. "Plan as written" is the plan's rule on the same synthetic data (plain swap null, plan subset, 4 of 5 families).

What the table shows.

- **Shared noise alone makes a link.** With no true link, the raw R_adj on the primary subset is −0.03 to −0.27, strongest in the families with many active sequences. A raw R_adj of that size is not evidence.
- **SIMEX removes it.** Under all seven nulls the corrected R_S is −0.07 to +0.04 per family. The overall verdict is kill in 97 to 100% of null replicates and support in 0 of 700. Per family, false support is at most 10% (1B.1), which is why the overall rule needs three of four families.
- **Both verdicts are reachable.** Kill is reached in 97 to 100% of nulls. Support is reached in 62% of replicates at γ = 0.2 (true R_adj about −0.22), 79% with real per-cell noise at the same γ, and 93% at γ = 0.4 (true about −0.29 to −0.41).
- **A weak link is usually not supported.** At γ = 0.1 (true about −0.11 to −0.17) the overall verdict is kill 45%, mixed 52%, support 3%. With the mixture of specialists at γ = 0.2 (true about −0.12 to −0.23) it is mostly mixed. So a kill means "no link of about −0.2 or stronger beyond noise".
- **The plan's rule as written gives false support.** It supports in up to 17% of null replicates (τ = 0.4) and 2 to 7% in most others, because its raw R_adj carries the shared-noise artefact and the swap null does not reproduce it.
- **Fam3.1 cannot decide.** Its R_S has an sd of 0.23 to 0.37 across replicates and it supports in only 13 to 24% of replicates even at γ = 0.2 to 0.4. That is why it is reported only.

## Dry run

`t12_analysis.py dryrun` runs the full `real` code, including every reported-only extra, with activity permuted within family. Each sequence keeps its above-floor profile shape and takes another sequence's total (cells above 1 become 1 + (r − 1) × A_other / A_own; the bootstrap σ of each cell is kept). It ran without error in about 13 minutes. Every rule said **kill**, overall and in every family (the plan's rule said "partly" in 2.2).

| Family | Subset n | R_full | Raw R_adj | R_S (interval) | Plan subset n, R_adj |
|---|---|---|---|---|---|
| 1A.1 | 100 | −0.48 | +0.17 | +0.18 (−0.11 to +0.45) | 115, +0.25 |
| 1B.1 | 173 | −0.53 | +0.02 | −0.01 (−0.23 to +0.15) | 195, +0.19 |
| 2.1 | 997 | −0.31 | −0.01 | +0.29 (+0.17 to +0.42) | 884, −0.08 |
| 2.2 | 1,089 | −0.37 | +0.01 | +0.60 (+0.47 to +0.71) | 863, −0.19 |
| 3.1 | 35 | −0.50 | −0.03 | −0.09 (−0.69 to +0.69) | 57, +0.22 |

**The dry run is a code check, not a calibration.** Permuting activity breaks the pairing between a sequence's own noise and its own total, which is the artefact SIMEX corrects. So in the dry run the raw R_adj has no shared-noise artefact in it (about 0), while SIMEX still assumes one and removes it. That is why R_S is strongly positive in 2.1 and 2.2. On real data, where each cell's noise really is in its total, the planted rows apply. The overcorrection here pushes toward kill. Even so, the real run's R_S in 2.1 and 2.2 should be read next to its SIMEX curve, which `real` prints.

The R_full values (−0.31 to −0.53) show how much of the paper's Table 1 survives when activity is assigned at random: a large share.

`sealcheck` prints `"real_allowed": false`.

## Reported only (no rule attached)

`real` also prints these. None can change the verdict.

- The paper's full-sample R and ρ (Table 1) for comparison.
- Raw R_adj on the primary subset, and its verdict without SIMEX (`raw_no_simex`).
- The SIMEX curve (R_adj at each λ) and the linear extrapolation.
- The plan's subset (r > 5 on ≥ 2 substrates): its size, R_adj and bootstrap interval.
- The plan's rule as written (plain swap null, plan subset, 4 of 5 families).
- The swap nulls (plain, donor, eb): the 2.5, 50 and 97.5 percentiles of R_full and of R_adj on the plan subset.
- Fam3.1's full SIMEX result and verdict.
- The 4-of-5 version of every rule.

## Ways it could be fooled, and limits

1. **SIMEX assumes the deposited bootstrap bounds describe the noise.** If the real k-Seq noise is larger than its bootstrap says (for example from library-prep or sequencing batch effects), SIMEX under-corrects and leaves some negative artefact, which pushes toward support. If it is smaller, SIMEX over-corrects toward positive values, which pushes toward kill; the dry run shows how strong that can be when the noise is not in the total at all. The planted check covers level-dependent, per-cell and correlated noise, but each at the deposited size.
2. **SIMEX treats noise as log-normal and independent across draws.** The "correlated noise" row tests one departure. Strong skew in the real noise is not tested.
3. **Quadratic extrapolation can overcorrect.** In the small families (1A.1, 1B.1) the SIMEX estimate has an sd of about 0.13 to 0.15 across replicates and sometimes lands above the truth. This pushes toward kill, not support.
4. **Power is limited in 1A.1 and 1B.1.** With about 160 to 230 sequences above all_sum 30, a true R_adj of −0.2 is supported only part of the time (table). A kill there means "no link of about −0.2 or stronger beyond noise", not "no link at all".
5. **The index is one measure of specificity.** Aromatic preference (the paper's second measure) is not tested. A link in aromatic preference alone would be missed.
6. **The subtraction of exactly 1 assumes the background is exact.** The background varies by substrate and is itself estimated (Supp. Table 2). The planted check includes floor variation of that size.
7. **Sequences are related.** Families are clusters of related sequences. The bootstrap treats sequences as independent, so the interval may be somewhat too narrow.
8. **Selection on all_sum > 30 truncates activity.** The correlation is measured over a narrower activity range than the full family. That weakens it toward 0, which favours a kill.
9. **The synthetic preference shapes are guesses.** θ_f is shaped on the paper's description (aromatic preference in 1A, 1B, 3.1; broader profiles in 2.1, 2.2). Other shapes could give other power.

## Sources actually opened

- Janzen et al. 2022: full text from Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9233669/fullTextXML`); Supplementary Information PDF and Source Data xlsx from `static-content.springer.com`; the authors' scripts from GitHub `ichen-lab-ucsb/WFLIVM_k-Seq` at commit 68990737c2257cef2815d7df74e2f7686bc5a597, read as source and never run.
- Nath and Atkins 2008 (doi:10.1021/bi701448p), abstract only, for the index's origin.
- Prior art: `experiments/t12_janzen_specificity/PRIOR_ART.md` lists every search and every abstract read. No reanalysis of the activity-specificity link was found.

## Decisions confirmed at the seal

1. **The four rule changes** (SIMEX-corrected R_S as primary, the all_sum > 30 subset, support at −0.15, and 3 of 4 eligible families) are accepted. Each was forced by the planted check before any real R_adj or R_S was computed. The plan's rule as written is computed and reported only.
2. **Power.** About 62% support at a true R_adj of −0.22, with 1A.1 and 1B.1 near 50% each, is accepted. A kill is read as "no link of about −0.2 or stronger beyond noise", never as "no link".
3. **The noise assumption** (limit 1) is accepted as the main risk. It is now shown, not just stated. One reported-only addition was made to `simex()` after the planted and dry runs: the same fitted quadratic is also read at λ = −0.5 and λ = −2. These are the corrected values if the true noise variance were half or twice the deposited one. The readout adds no random draws and does not touch the verdict. The dry run was re-run with the final script: its output is identical apart from the two new keys. The planted output is from the previous script hash (84183003…), and the only difference between the two scripts is these two keys. The ×2 readout extrapolates far along a quadratic and can leave [−1, 1]; it shows direction only.
4. **The `diag*.py` scripts** stay in the repo, because this prereg cites them. They read no real profiles.
5. No other change. Any change after this seal makes the verdict invalid.
