# Pre-registration (T15): do formose mixtures under changing flow differ from steady state by more than a repeat run does?

Status: DRAFT, written 2026-11-25 by the T15 prep agent. This is study N4 in `docs/plans/next_studies_2026-11-25.md`.

- **Run so far:** `gate`, `planted` (7 variants), `planted_merge`, `dryrun` and `sealcheck`.
- **Not run:** `real`. The script refuses it until `docs/prereg/HASHES.txt` names `experiments/t15_formose_flow_noise/scripts/t15_analysis.py` with its current sha256 (`047456a0e6e23099783a61338bfa5b37731f3fa627b6d345fa7b02fd955dbc08`).
- Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is how far each dynamic run's mean sits from its steady-state partner's mean, for compounds 3, 5, 7 and 11. No dynamic-run mean has been computed, printed or saved, and no dynamic run has been compared with steady state.

- **The repeat pairs were read in full (the gate needs them).** In pooled within-run SD units, the shift between repeat runs at identical settings, run on different days, is:

  | Compound | EXP001 vs EXP010 (steady) | EXP003 vs EXP012 (dynamic) |
  |---|---|---|
  | 3, DHA | 3.79 | 5.91 |
  | 5, threose | 2.74 | 0.10 |
  | 7, erythrulose | 14.67 | 12.96 |
  | 11, xylulose | 3.17 | 1.82 |

  These are the D_rep half of the rule, so the yardstick is known. The values for the other 16 compounds common to the four repeat runs are in `scripts_out/t15_gate.json`.
- **The four repeat runs therefore also fed the planted-check generator.** Their within-run SD, lag-1 autocorrelation and between-run offset SD (σ_u = 3.43, 1.39, 9.83 and 1.48 within-run SD for compounds 3, 5, 7 and 11) came from them.
- **The dynamic runs were read only as demeaned series.** Three things were computed from them:
  - integrated autocorrelation times, to set the block length;
  - within-run SD ratios, dynamic over steady (printed; `block.within_run_sd_ratio_dyn_over_steady` in the gate file);
  - row and missing-value counts.

  An SD ratio says how much the dynamic runs fluctuate. It says nothing about where their means sit. For the record, the ratios range from 0.82 to 7.86. The largest are DHA and threose at 100 mM formaldehyde.
- **The authors' published summaries are part of the claim, not a peek.**
  - The paper reports erythrulose at the 50 mM rate series as "[7] = 4.8 ± 0.5 mM" (45 s), "6.0 ± 0.5 mM" (steady state) and "4.2 ± 0.7 mM" (120 s).
  - In within-run SD units, that is a shift of roughly 2 to 3 SD. The repeat-pair yardstick for erythrulose is about 13 to 15 SD.
- **Expectation.** Given the repeat-pair values above and the paper's own erythrulose numbers, I expect the dynamic shifts for at least erythrulose to fall inside the day-to-day spread. That points toward kill. Threose has a small yardstick in one pair (0.10) but 2.74 in the other, and the rule uses the larger. I hold no firm expectation for DHA or xylulose.
- **Script versions.** The gate and the base, no_offset and real_resid planted variants first ran under two earlier drafts of the script. Those drafts differed only in the planted grid and generator, plus a guard tying `real` to a gate file written by the same hash. Their outputs were deleted. Everything in `scripts_out/` now comes from `047456a0...`. The gate and the three re-run variants gave numbers identical to the earlier runs.

## Claim under test

van Duppen P, Daines E, Robinson WE, Huck WTS. 2023. "Dynamic Environmental Conditions Affect the Composition of a Model Prebiotic Reaction Network." J Am Chem Soc 145:7559-7568. doi:10.1021/jacs.3c00908 (PMC10080678). Read in full from `experiments/t15_formose_flow_noise/raw/europepmc/PMC10080678.xml`.

- Abstract, verbatim: "Surprisingly, the product compositions of the formose reaction under dynamic conditions deviate significantly from those under steady state conditions."
- Amplitude series, verbatim: "the measured concentration distributions vary significantly (at least p ≤ 1 × 10–4 in each series for compounds 3, 5, 7, and 11) in response to fluctuations in [Ca(OH)2]in."
- Rate series, verbatim: "Again, we observed average concentrations of compounds which deviate from steady-state averages (3, 5, 7, and 11; p ≤ 1 × 10–4, in all compound series; see Figures S12 and S13)."
- The four compounds (Figure 2 caption, verbatim): "(a) DHA (3), (b) threose (5), (c) erythrulose (7), and (d) xylulose (11)". They are rows 3, 5, 7 and 11 of `info_files/compound_information.csv`. The SMILES columns are `O=C(CO)CO`, `O=C[C@@H](O)[C@H](O)CO`, `O=C(CO)[C@H](O)CO` and `O=C(CO)[C@@H](O)[C@H](O)CO`, and all 12 runs have all four.

**The authors' test.** `scipy.stats.ttest_ind(dist_1, dist_2, nan_policy="omit")` (in `processing_scripts_formose/data_analysis_functions.py`, read as text). This is Student's pooled-variance t-test on the 43 to 50 serial samples of one run against another, with every sample treated as independent. The SI does not describe it. See `experiments/t15_formose_flow_noise/PRIOR_ART.md`.

**Why it might be an artefact.**
- Serial samples from one reactor are correlated, so the t-test overstates n.
- More importantly, every comparison in the paper is between two runs. Two runs at identical settings may differ by more than the t-test's within-run noise allows. The deposit has two such repeat pairs, run on different days, and the paper never compares them.

**H1 (the authors' reading).** The dynamic-vs-steady shifts for compounds 3, 5, 7 and 11 are well beyond the shift between repeat runs at identical settings.

**H0.** They are no larger than a repeat run's shift.

## Inputs (exact)

All files come from `https://raw.githubusercontent.com/huckgroup/Formose_2022/94c10347154fac67371c5b9101ce79ffaf70ffdc/<path>` (BSD-3-Clause; commit of 2023-03-27, the repository's latest). They are saved in `experiments/t15_formose_flow_noise/raw/github/src/`, which is gitignored (`.gitignore:41:experiments/*/raw/`, confirmed with `git check-ignore`).

The files are Latin-1 text. They are parsed by splitting on commas and calling `float()` under `python -I`. Nothing in them is executed, and none of the authors' code was run. The script re-hashes every decision input at the start of each run and stops on a mismatch. The full list with URLs is in `raw/github/manifest.tsv`.

| File (under `Extended_data_GH/` unless noted) | sha256 | Role |
|---|---|---|
| EXP001/Analysed_data/EXP001_Data.csv | adbf96e5f3ea472f085f97e03eb4f644c8bec76a648cba12a3e9cd940fd0c117 | steady, 50 mM; repeat pair 1 |
| EXP002/Analysed_data/EXP002_Data.csv | 1070cdf34c844caaab285833e5f5bb84b6a8edce64e5be4b80fe9269860cfa45 | dynamic |
| EXP003/Analysed_data/EXP003_Data.csv | 88a997ba04b486861b462c08822aad66a608b5f41beafb2d907281281847f01f | dynamic; repeat pair 2 |
| EXP004/Analysed_data/EXP004_Data.csv | 753a355133f3bb2b333b2fd2a2645279c47d38b05b0f8a5adcebdce69f933322 | steady, 20 mM |
| EXP005/Analysed_data/EXP005_Data.csv | 055096744dbe320e2e1b7850c464617826092d17499d792ca9e05f8ef56e981b | dynamic |
| EXP006/Analysed_data/EXP006_Data.csv | 5ecc4074e2d92cf91bdbb56c19536b57e93e8c3c64200c18c94a2ef4415aca15 | dynamic |
| EXP007/Analysed_data/EXP007_Data.csv | 6bd44020a0339012b01ed36da18698e8af4c478a47fac0ab7fcedbbecda54f05 | steady, 100 mM |
| EXP008/Analysed_data/EXP008_Data.csv | 4e209a9574ac31bd973ab42f1c75b05b748d09c838697f22cc81973a846762be | dynamic |
| EXP009/Analysed_data/EXP009_Data.csv | bbe7ea06b9c71427f67cff41b48252224d3f16482eeac426b402bc468dc099be | dynamic |
| EXP010/Analysed_data/EXP010_Data.csv | 4ca57dc428717406bb128422c624f17949c43f37b7430cb943c52e45d3a7c8a9 | steady, 50 mM; repeat pair 1 |
| EXP011/Analysed_data/EXP011_Data.csv | dd6ec0841bd14229796246baf23b5f0de3fca0f86fe64105b5e52f50fea171c7 | dynamic (120 s) |
| EXP012/Analysed_data/EXP012_Data.csv | c847678cc7d1031d74ca18f7fa04b16c66d1aaacb5049bc6d6ddb5be8d411220 | dynamic; repeat pair 2 |
| info_files/compound_information.csv | 9fa500e42125c2d0576ee682af89f8c0831eaf424f93fa05ac69c10b9b2f1c1a | compound numbering |
| info_files/list_exp.csv | 3458b6edfd0ac2558fc65ba2f5c7258f9d15fa8ffb3cd2a034ef6ce667500eb4 | run settings |
| PMC10080678.xml (Europe PMC) | (claim text; Table 1) | |
| ja3c00908_si_001.pdf (Europe PMC supplementary files) | 0864636d08b0f2d9ef7446ad78ddeb62d0e1debd724ad4a9f61f60ff5c6b575e | SI; no test described |

Run settings (paper Table 1 and `list_exp.csv` agree):

| Run | Setting |
|---|---|
| EXP001, EXP004, EXP007, EXP010 | σ = 0 |
| EXP002, 005, 008 | σ = 2.89 mM, 45 s steps |
| EXP003, 006, 009, 012 | σ = 5.75 mM, 45 s steps |
| EXP011 | σ = 5.75 mM, 120 s steps |

Formaldehyde levels: 50 mM in EXP001-003 and EXP010-012, 20 mM in EXP004-006, 100 mM in EXP007-009. Same-day groups: EXP001-003, EXP004-006, EXP007-009 and EXP010-012. The rows are in sampling order. EXP002, 003, 005, 006, 008 and 009 index rows by seconds, with gaps where samples were dropped, and the others by sample number. After dropping, the runs have 43 to 50 rows. None of the 12 runs has a missing value for the four compounds.

## Comparisons (exact)

These are the authors' sets from `01_composition_analysis.py`. The first run in each set is the steady state (σ = 0).

| Set | Steady state | Dynamic runs compared with it |
|---|---|---|
| [4, 5, 6], 20 mM, amplitude | EXP004 | EXP005 (2.89 mM, 45 s), EXP006 (5.75 mM, 45 s) |
| [1, 2, 3], 50 mM, amplitude | EXP001 | EXP002 (2.89 mM, 45 s), EXP003 (5.75 mM, 45 s) |
| [7, 8, 9], 100 mM, amplitude | EXP007 | EXP008 (2.89 mM, 45 s), EXP009 (5.75 mM, 45 s) |
| [10, 12, 11], 50 mM, rate | EXP010 | EXP012 (5.75 mM, 45 s), EXP011 (5.75 mM, 120 s) |

These give 8 dynamic-vs-steady comparisons, all within one day. There are two repeat pairs, both spanning two days: (EXP001, EXP010), both steady, and (EXP003, EXP012), both at 5.75 mM with 45 s steps.

## Gate (`t15_analysis.py gate`; run; passed)

The plan's rule is: "If the two pairs disagree in size by more than a factor of 3 for most compounds, the repeat noise is not pinned down; stop and report 'cannot decide'."

Implemented as follows:
- For every compound present in all four repeat runs (20), D is computed for each pair.
- The gate fails if max/min of the two exceeds 3 for more than half of those compounds.
- The plan asks for a moving-block bootstrap interval, so 95% intervals of each repeat-pair D are computed for the four compounds and reported.

**Result.**
- 4 of 20 compounds disagree by more than 3×: threose (5; 27×), compound 14 (32×), compound 8 (4.9×) and compound 30 (3.3×).
- Among the four claim compounds, only threose disagrees (2.74 against 0.10).
- **Gate passed.** Output: `scripts_out/t15_gate.json`.

Repeat-pair D bootstrap 95% intervals:

| Compound | EXP001 vs EXP010 | EXP003 vs EXP012 |
|---|---|---|
| 3 | [3.28, 4.84] | [4.59, 8.53] |
| 5 | [2.12, 3.95] | [0.01, 0.76] |
| 7 | [11.5, 22.1] | [11.1, 16.6] |
| 11 | [1.99, 8.07] | [1.53, 2.41] |

**Block length.**
- **Rule (D3).** For each run and compound, the integrated autocorrelation time τ (1 + 2 × the initial positive run of the sample autocorrelation of the demeaned series, lags 1 to n/4) is computed for all 12 runs × 4 compounds. Then L = ceil(2 × 75th percentile of τ), with L at least 2 and at most floor(shortest run / 4).
- **Result.** The 75th percentile of τ is 2.31, so **L = 5 samples** (about 2.5 to 3.4 minutes, 1.3 to 1.7 residence times).
- The steady run EXP001 has the longest times (τ = 3.8 to 9.2), a sign of slow drift within the run.

## Fixed decisions

- **D1. Series.** One column per run and compound, in sampling order. "nan" cells are dropped (there are none here). The authors' nan-to-0 convention is used only for the reported reproduction of their t-test.
- **D2. Effect size.** D(a, b) = |mean_a − mean_b| / sqrt((sd_a² + sd_b²) / 2), with ddof = 1. This is the plan's "pooled within-run standard deviation".
- **D3. Block length** L = 5 (see the gate), fixed in `t15_gate.json` and read by every later mode.
- **D4. Per-compound statistics.**
  - D_rep(c) = max(D(EXP001, EXP010), D(EXP003, EXP012)), the plan's "larger D_rep".
  - D_dyn(c) = median of D over the 8 comparisons, the plan's "median D_dyn".
  - Δ(c) = D_dyn(c) − D_rep(c).
- **D5. Bootstrap.**
  - Circular moving-block bootstrap with block L, B = 4,000 replicates (seed `[20261125, 4]` for `real`).
  - Each of the 12 runs is resampled independently, once per replicate, with the same positions for all four compounds of a run. A steady run used in two comparisons is therefore resampled once.
  - D_dyn, D_rep and Δ are recomputed in each replicate, and the 2.5% and 97.5% quantiles of Δ form the interval.
- **D6. Compounds.** Only 3, 5, 7 and 11 decide. Nothing else in the deposit decides.

## Decision rules

Primary is the revised rule (`PRIMARY_RULE = "revised"`). The plan's literal rule is computed and reported next to it.

**Revised (primary).**
- **Kill:**
  - at least 3 of the 4 compounds have D_dyn < 2 × D_rep; and
  - at least 3 of the 4 have a Δ interval whose lower end is ≤ 0 (the interval does not lie wholly above 0).
- **Support:** at least 3 of the 4 compounds have D_dyn > 3 × D_rep and a Δ interval whose lower end is > 0.
- **Neither:** anything else. ("Conflict", both kill and support at once, cannot happen with these thresholds but is coded.)

**Plan rule (reported).**
- **Kill:** at least 3 of 4 compounds have D_dyn < 2 × D_rep, and at least 3 of 4 have a Δ interval that includes 0.
- **Support:** as in the revised rule.

**What the verdicts mean.**
- Kill: the shifts the paper reports are not larger than the shift between two runs at identical settings done on different days.
- Kill does *not* mean the dynamics have no effect within a day. The deposit cannot test that, because it has no within-day repeats.
- Support: the shifts clear the day-to-day spread by the plan's margin.

## Changes from the plan, made before the seal

- **C1. Reading of "median D_dyn" and "for the four compounds".**
  - The median is taken over the 8 dynamic-vs-steady comparisons, per compound.
  - The first kill clause is applied per compound and needs at least 3 of 4, mirroring the plan's "three of four" in the second clause and in the support rule.
  - The 8 comparisons are the authors' four sets, because the amplitude quote and the rate quote both name the four compounds. The rate set alone, [10, 12, 11], is reported only.
- **C2. The kill interval clause changed form: "includes 0" became "does not lie wholly above 0".**
  - With the plan's literal form, kill is close to unreachable when nothing is planted. A median of 8 run-pair shifts is usually smaller than the larger of two. When D_dyn is clearly below D_rep, the interval of Δ lies wholly *below* 0, and the plan's rule then returns "neither", although the data favour H0 even more strongly.
  - In the planted check, in every variant with day offsets, the plan rule gave kill at zero shift in only 1% to 14% of worlds (base: 24 of 500). The revised form gave 86% to 95%. Only the no-offset world, which the repeat pairs rule out, lets the plan rule kill (98%).
  - In the dry run the plan rule returned "neither" with all four intervals below 0. The revised form returned kill.
  - Thresholds (2×, 3×, 3 of 4, 95%) are the plan's. Only the direction of the interval test changed.
- **C3. The plan's planted-check expectation cannot be met, and no rule change can meet it honestly.**
  - The plan says "adding a known shift of 3 pooled standard deviations to one repeat run must be detected". The repeat pairs show that runs at identical settings on different days differ by 2 to 15 within-run SD for these compounds (σ_u = 1.4 to 9.8 SD). A 3 SD shift is therefore inside the day-to-day spread.
  - The rule's question is "more than a repeat run does?", so "not more" is the correct answer for a 3 SD shift. Under the revised rule it comes out as kill in about half the realistic worlds and as neither in the rest (table below).
  - Lowering the multipliers to make 3 SD detectable would change the question, so they were not changed. The resolution is stated instead: support needs a shift of roughly 10 to 40 within-run SD (or about 2 to 4 × σ_u of the noisiest decisive compound).
  - The user decides at the seal whether this resolution is acceptable (decision 2).
- **C4. Planted design.** The plan says to add the shift "to one repeat run". With two real repeat pairs that gives one realisation and no rates. The planted check therefore simulates whole 12-run worlds calibrated on the repeat runs (next section). The literal one-run version is the dry run's stand-in idea and is not separately rated.

## Planted check (`t15_analysis.py planted`, `planted_merge`; run; synthetic runs only)

**Generator.** For each of the four compounds, in units of its pooled within-run SD from the four repeat runs:
- Each of the 12 synthetic runs has the real run's length, plus its own offset u ~ N(0, σ_u²) and within-run noise.
- In the base variant the noise is AR(1) with φ equal to the mean lag-1 autocorrelation of the repeat runs: 0.23, 0.12, 0.32 and 0.23 for compounds 3, 5, 7 and 11.
- σ_u is estimated from the two repeat-pair shifts, after subtracting the AR(1) variance of a run mean: 3.43, 1.39, 9.83 and 1.48.
- Every one of the 8 dynamic runs gets +δ. The two dynamic repeat runs have identical settings, so they get the same shift.
- The real code (`analyse`, `verdicts`) is run with L = 5 and B = 400. There are 500 worlds per δ per variant, seeded `[20261125, 2, variant, δ index]`.

**Variants.**

| Variant | What it changes |
|---|---|
| base | as described |
| real_resid | noise is a block resample of a real demeaned repeat run, standardised (realistic shape and serial correlation) |
| no_offset | σ_u = 0 |
| half_offset | σ_u × 0.5 |
| double_offset | σ_u × 2 |
| dyn_sd_x1.5 | dynamic runs have 1.5× the within-run SD |
| phi_0.8 | φ = 0.8 |

**Results** (`scripts_out/t15_planted.json`). Counts are kill / neither / support out of 500, under the revised rule (primary) and the plan rule. The user-specified grid is 0, 1, 2, 3 and 5. The extended grid (10, 20, 40) shows where support becomes reachable.

| δ (SD) | base: revised | base: plan | real_resid: revised | no_offset: revised | half_offset: revised | double_offset: revised | dyn_sd_x1.5: revised | phi_0.8: revised |
|---|---|---|---|---|---|---|---|---|
| 0 | **431** / 69 / **0** | 24 / 476 / 0 | 454 / 45 / 1 | 492 / 8 / 0 | 475 / 25 / 0 | 444 / 56 / 0 | 463 / 37 / 0 | 469 / 31 / 0 |
| 1 | 439 / 61 / 0 | 23 / 477 / 0 | 440 / 60 / 0 | 3 / 237 / 260 | 411 / 89 / 0 | 433 / 67 / 0 | 442 / 58 / 0 | 453 / 47 / 0 |
| 2 | 364 / 136 / 0 | 30 / 470 / 0 | 382 / 117 / 1 | 0 / 1 / 499 | 167 / 324 / 9 | 401 / 99 / 0 | 381 / 119 / 0 | 407 / 92 / 1 |
| 3 | **243** / 256 / 1 | 21 / 478 / 1 | 285 / 215 / 0 | 0 / 0 / 500 | 46 / 439 / 15 | 364 / 136 / 0 | 286 / 212 / 2 | 302 / 197 / 1 |
| 5 | 49 / 441 / 10 | 3 / 487 / 10 | 61 / 426 / 13 | 0 / 0 / 500 | 0 / 407 / 93 | 276 / 223 / 1 | 86 / 409 / 5 | 98 / 392 / 10 |
| 10 | 0 / 393 / 107 | 0 / 393 / 107 | 2 / 398 / 100 | 0 / 0 / 500 | 0 / 151 / 349 | 39 / 457 / 4 | 0 / 415 / 85 | 1 / 391 / 108 |
| 20 | 0 / 138 / 362 | 0 / 138 / 362 | 0 / 162 / 338 | 0 / 0 / 500 | 0 / 5 / 495 | 0 / 383 / 117 | 0 / 155 / 345 | 0 / 146 / 354 |
| 40 | 0 / 3 / 497 | 0 / 3 / 497 | 0 / 5 / 495 | 0 / 0 / 500 | 0 / 0 / 500 | 0 / 141 / 359 | 0 / 11 / 489 | 0 / 7 / 493 |

The plan rule's support counts are identical to the revised rule's in every cell, and its kill counts are given for base only. The full table is in the json.

**Rates (base, revised rule).**
- False support at δ = 0: 0 of 500. Across all variants at δ = 0 it is at most 1 of 500 (real_resid).
- Kill at δ = 0: 86% (87% to 98% in the other variants).
- At δ = 3 SD: kill 49% ("false kill" if one insists a 3 SD effect is real; see C3), neither 51%, support 0.2%.
- Support reaches 21% at 10 SD, 72% at 20 SD and 99% at 40 SD.
- With no day offsets, a 1 SD shift already gives support 52%, and 2 SD gives 100%. The rule is sensitive; it is the day-to-day spread that limits it.

**Plan rule.** Kill at δ = 0 is only 5% (base) and at most 14% in any variant with day offsets (98% with none). This is the miscalibration behind C2.

**Can every verdict be reached?** Yes, under the revised rule:
- kill when nothing is planted;
- neither in between;
- support for shifts well beyond the day-to-day spread.

Under the plan rule, kill is reachable only in the unrealistic no-offset world.

## Dry run (`dryrun`; run)

This runs the real code path (`report`, `analyse`, `verdicts`) with each of the 8 dynamic-vs-steady comparisons replaced by a repeat pair. The pairs alternate (EXP001, EXP010), (EXP003, EXP012) and their reverses, with B = 4,000 and seed `[20261125, 3]`. It uses only data already seen. Output: `scripts_out/t15_dryrun.json`.

| Compound | D_dyn (stand-in) | D_rep | Δ | 95% interval |
|---|---|---|---|---|
| 3 DHA | 4.85 | 5.91 | −1.06 | [−2.30, −0.22] |
| 5 threose | 1.42 | 2.74 | −1.32 | [−1.87, −0.88] |
| 7 erythrulose | 13.82 | 14.67 | −0.85 | [−4.68, −0.04] |
| 11 xylulose | 2.50 | 3.17 | −0.68 | [−3.05, −0.05] |

- **Revised rule: kill** (k1 4 of 4, k2 4 of 4, support 0).
- **Plan rule: neither** (k1 4 of 4, but k2 0 of 4, because every interval lies below 0; see C2).

As intended, repeat pairs standing in for the comparisons read as "no more than a repeat". The pipeline runs end to end.

## Reported only (no rule attached)

- D for each of the 8 comparisons and each compound, and the signed shift in SD units.
- Verdicts per set under both rules, including the rate set [10, 12, 11] that the second quote is about.
- The authors' t-test reproduced (`ttest_ind`, nan to 0) for each comparison and compound.
- An autocorrelation-aware Welch test with n_eff = n / τ per run. Note that it still ignores day-to-day variation.
- The plan rule's verdict and the counts behind both rules.

## Ways it could be fooled, and limits

- **The yardstick spans days; the comparisons do not.** Every dynamic-vs-steady comparison is within one day. Both repeat pairs span two days, the only repeats in the deposit.
  - If day-to-day drift is much larger than within-day run-to-run noise, the test can kill a within-day effect that is real.
  - A kill should be reported as "not larger than the difference between repeat runs on different days", not as "no effect of dynamics".
- **Peak identity may shift between days.** Retention times move by about 0.7 min between the EXP001-003 and EXP010-012 groups, with the same GC method and calibration file in all runs. The elution order of erythrose, threose and erythrulose also differs between groups, as the column headers show:
  - EXP001: erythrose 7.999, threose 8.037, erythrulose 8.079;
  - EXP004: erythrose 7.965, erythrulose 8.012, threose 8.061;
  - EXP010: erythrose 8.676, erythrulose 8.819, threose 8.864.

  If peaks were assigned differently on different days, part of D_rep, notably erythrulose's 13 to 15 SD, could be misassignment rather than chemistry. That would inflate the yardstick and favour kill. The chromatograms are not in the deposit, so this cannot be checked here.
- **Within-run drift.** EXP001 has τ up to 9 samples. Slow drift within a run inflates both its SD (shrinking D) and the bootstrap interval. L = 5 may be short for that run.
- **Two pairs, max of two.** D_rep is the larger of two noisy numbers, and the 50 mM pairs are used as the yardstick for the 20 mM and 100 mM sets too.
- **Scale differences.** Dynamic runs at 100 mM fluctuate up to 7.9× more than their steady partner. D divides by the pooled SD, so a large dynamic SD shrinks D_dyn. The planted variant dyn_sd_x1.5 shows a modest effect on the rates.
- **The bootstrap captures within-run sampling noise only.** Variation between runs enters through D_rep as a point value, not through the interval.

## How to run `real` after the seal

Single-threaded, `nice -n 20`, OMP and OPENBLAS threads = 1, from the repo root:

```
experiments/t1_vent_exergonic/.venv/bin/python -I experiments/t15_formose_flow_noise/scripts/t15_analysis.py experiments/t15_formose_flow_noise real
```

It takes well under a minute. It refuses unless the seal line is present and `t15_gate.json` was written by the same script hash. It writes `scripts_out/t15_real.json`.

## Sources actually opened

- **The paper.** van Duppen et al. 2023, PMC10080678 full text (Europe PMC XML) and SI PDF (Europe PMC supplementary files).
- **The authors' code, read as text and never run** (Formose_2022 at 94c10347): `01_composition_analysis.py`, `04_compositional_shift.py`, `processing_scripts_formose/data_analysis_functions.py`, `data_report.py`, `plotting_functions.py`, `README.md`.
- **Prior art.** As listed in `experiments/t15_formose_flow_noise/PRIOR_ART.md`: Baltussen et al. 2024 (PMC11254755), de Jong et al. 2025 (PMC12124346), Nishijima et al. 2026 (PMC12910140), Hashidzume 2025 (PMC11835704). The other citing records were screened by abstract or title.
- **Repo files read, not modified.** `docs/prereg/t14_autocatalytic_tiers.md` and `experiments/t14_autocatalytic_tiers/scripts/t14_analysis.py` (seal pattern).

## Decisions to confirm at the seal

1. **C2, revised kill clause** ("interval does not lie wholly above 0") as primary, with the plan's literal clause reported. The alternative keeps the plan's form, which gives kill at zero shift in only 5% of realistic worlds.
2. **C3, the resolution.** Accept that the test cannot detect shifts of about 3 to 5 within-run SD against this day-to-day spread, so a kill means "within the spread of repeat runs on different days". The alternative is to declare the study undecidable now, because the deposit lacks within-day repeats.
3. **C1, the readings.** The median is over the 8 comparisons, the first kill clause is per compound with 3 of 4, and all four sets decide while the rate set is reported.
4. **The peak-identity caveat.** Whether to write to the authors about peak assignment across days before or after `real`. Any reply cannot change the sealed rule.
5. **Files to hash at the seal:**
   - `docs/prereg/t15_formose_flow_noise.md`
   - `experiments/t15_formose_flow_noise/PRIOR_ART.md`
   - `experiments/t15_formose_flow_noise/scripts/t15_analysis.py`
   - `experiments/t15_formose_flow_noise/scripts_out/t15_gate.json`
   - `experiments/t15_formose_flow_noise/scripts_out/t15_planted.json`
   - `experiments/t15_formose_flow_noise/scripts_out/t15_dryrun.json`

## Decisions confirmed at the seal

1. **C2** is accepted. The kill clause becomes "lower end ≤ 0", and that form is primary. The plan's literal form ("interval includes 0") is computed and reported alongside. On the planted check it gives kill in only 5% of zero-shift worlds, because a D_dyn clearly below D_rep gives an interval wholly below 0.
2. **Resolution is accepted. How a verdict must be read is fixed now.** Both repeat pairs span different days, and every one of the authors' comparisons is within one day.
   - A **kill** means: the dynamic-versus-steady shift is not larger than the gap between repeat runs at identical settings on different days. So the deposited data cannot separate the dynamic effect from run-to-run reproducibility. It does **not** mean that changing flow has no effect.
   - The planted check gives about 49% kill at a true 3 SD shift. So a kill is weak evidence against shifts of that size, and says little about smaller ones.
   - A **support** means the shift is clearly larger than between-day reproducibility.
3. **C1** is accepted as written: the median over all 8 comparisons, a per-compound kill clause needing 3 of 4 compounds, and the rate set reported only.
4. **Peak assignment** (retention-time shifts, and the elution order of erythrose, threose and erythrulose changing between days) is a stated limit. It may inflate the yardstick, especially for erythrulose. It is not checked here. Any contact with the authors is the owner's decision.
5. **Already established, and independent of the verdict:** from the authors' code, the published p-values come from a pooled t-test that treats 43–50 serial samples from one run as independent draws, with no run-level variance. That point stands whatever `real` returns.
6. No other change. Any change after this seal makes the verdict invalid.
