# Pre-registration (T18b): QT45's error threshold with its measured pair epistasis kept

Status: **failed its planted kill test (pilot, family E 0 of 5); closed under F2, never sealed.** Written 2026-11-25. Everything above "Gate results" was written before the T18b gate ran and before any T18b planted replicate. T18b is the follow-up named in T18's prereg (`docs/prereg/t18_qt45_error_threshold.md`, "Proposed, not adopted", item 1). It is the last attempt: if its planted kill test fails, T18b is reported as failed and there is no T18c (coordinator).

## Why T18b exists

T18's primary model (a 4-parameter global-epistasis curve fitted to singles and doubles, used for every unmeasured genotype) passed its estimator checks but **failed its planted kill test**: within 20% on 20 of 20 noise-only landscapes, but on 1 of 6 landscapes with planted pair plus higher-order epistasis, always low (median −27%). A diagnostic (`scripts_out/t18_diag_f2_B1.json`) traced the miss to pair epistasis. Pair terms are small in any one double, but a genotype with m mutations carries m(m−1)/2 of them, and near the threshold the quasispecies sits 4 to 6 mutations from WT. T18's curve treats the double residuals as noise and throws them away. T18b keeps them.

## What has been seen (blinding disclosure)

- Everything disclosed in T18's prereg, including T18's gate fit to the real singles and doubles (floor, top, residual sd, latent effects) and T18's planted results.
- **Read counts.** Per-replicate read counts were streamed from the deposit (Zenodo 10.5281/zenodo.13891380, `optimized_fitness_landscape_zenodo.zip`, `QT45/collapsed_reads/{in_nodel, out_nodel_A, out_nodel_B, out_nodel_C}.fasta`; script `scripts/t18b_counts.py`, nothing large written to disk). Kept: counts of WT, singles and doubles (their pooled fitness is already public in the CSVs) and of triples (HD = 3).
- **Triples are blind.** The triple output counts (`raw/t18b_counts/counts_hd3_out_nodel_*.tsv`) are on disk and have not been read by any code or person. Before `real`, only the triple *input* counts (the layout: which triples were in the starting library, and how many reads) are used. The input library is the pre-selection pool, so its counts carry no fitness information.
- **Not computed on the real landscape:** any threshold, Perron root, growth rate, R, the EB pair-term variance τ², or any triple fitness.

## Question

Same as T18: is QT45's measured fidelity (94.1% per nucleotide, e_meas = 0.059) above or below the error threshold e\* set by its own measured landscape? H1 (support): R = e_meas / e\* < 1. H0 (kill): R > 1.

## Design

T18's D1 to D4 and D6 carry over unchanged: the 44-site genotype space; rate 2^(F/τ_T) with τ_T = 1; one (+) → (−) → (+) generation per step with per-strand error e, uniform over the 3 wrong bases; an absorbing dead class at w_dead = 0.01; e\* where λ_A(e\*) = w_dead; the same population Monte Carlo estimator, e grid and interpolation (`t18_core.threshold`, unchanged); planted N = 5,000, 60 (30) and 40 (15) generations, no refinement; real N = 20,000 with refinement.

- **D5′. Model (the change).** WT, the 132 singles and the 8,346 measured doubles use their measured values (as T18). Unmeasured doubles use T18's curve with no pair term. For every genotype with 3 or more mutations:
  F = g(z₀ + Σ aₘ + Σ_{measured pairs mn in the genotype} Êₘₙ),
  where g, z₀ and aₘ are T18's global-epistasis fit (`t18_core.fit_ge`, unchanged, three starts) and Êₘₙ is the pair term of double mn on the latent scale.
- **Shrinkage rule (empirical Bayes, fixed here).**
  - Observation model per measured double: F_obs = g(ẑₘₙ + Eₘₙ) + ε, with ε ~ N(0, σₘₙ²) and σₘₙ from the replicate noise model (D10). Prior: Eₘₙ ~ N(0, τ²), one τ for all pairs.
  - τ² by maximum marginal likelihood under the linearisation rₘₙ ~ N(0, kₘₙ²τ² + σₘₙ²), where r is the residual from the curve and k = g′(ẑ). Doubles at the censoring floor are excluded from this fit. τ is searched on [0, 3] latent units.
  - Êₘₙ is the posterior mode of the nonlinear model (30 Gauss–Newton steps). Its posterior sd sₘₙ comes from the curvature at the mode.
  - **Unmeasured pairs** (168 of the 8,514 possible doubles) are shrunk fully to 0. Site-level means are not used: they add 44 parameters for 2% of the pairs.
- **Plug-in: posterior draws, not the posterior mean.** e\* is a convex functional of the landscape: survivors far from WT come from the upper tail of Σ E. A posterior-mean plug-in keeps only the shrunk share of the pair variance, so it is biased toward T18's error. The primary landscape therefore uses one posterior draw, Eₘₙ = Êₘₙ + sₘₙ·N(0, 1) per pair (multiple imputation). The primary e\* is the mean over M draws: M = 2 in planted replicates, M = 4 in `real`. The posterior-mode landscape is reported as a diagnostic in both.
- **D10. Replicate noise model.** The outputs have three replicates (A, B, C) from one input library. For every single and double with all three output counts ≥ 5 (and input ≥ 10), the spread of F_r = log2(o_r / O_r) over the replicates estimates the output noise: the input is shared and cancels. Fit E[s²] = a · mean_r(1/o_r) / ln²2 + b by least squares. a is the per-read overdispersion and b the replicate-level variance. The noise sd of a pooled value at fitness F with input count i is
  σ(F, i) = sqrt( a/ln²2 · (1/μ + 1/i) + b/3 ),  μ = max(i · c_WT · 2^F, 1),
  where c_WT is WT's pooled output-to-input read ratio. Assumption: input reads have the same per-read overdispersion a as output reads. This cannot be checked from these data, which is why stress family S is run. The method evaluates σ at the observed F, in planted and real runs alike.
- **D6′. Uncertainty (real).** T18's residual bootstrap (B = 30), with the EB fit and one fresh posterior draw redone in each replicate. 95% interval from the 2.5 and 97.5 percentiles. Censored draws sit at the grid ends.
- **D9. Triple check (a safeguard against a cliff the doubles cannot see).** HD ≥ 3 fitness cannot be identified from HD ≤ 2 data alone. A landscape where every triple is dead would look the same in singles and doubles. The deposited reads contain triples, so T18b tests its HD ≥ 3 model against them, at the level that matters for a quasispecies: the input-weighted mean replication rate of triples.
  - Φ_obs = Σₜ oₜ / (c_WT Σₜ iₜ) over triples t with input iₜ ≥ 10, where oₜ is the pooled output count (zeros included, so there is no selection on survival).
  - Φ_model = Σₜ iₜ 2^{F̂ₜ} / Σₜ iₜ, with F̂ from the posterior-mode landscape.
  - T = log2(Φ_obs / Φ_model). **The model is flagged if |T| > 1**, meaning the mean triple rate is off by more than a factor of 2.
  - In `real`, T is computed once, after the EB fit and before any threshold. A flag makes the verdict "not decidable".

## Decision rules (real run, after a planted pass)

- **D7′.** R = e_meas / e\*, with e\* from the primary T18b model (mean of 4 posterior draws), and bootstrap interval [R_lo, R_hi] = [e_meas / e\*_97.5, e_meas / e\*_2.5].
  - **Support (H1):** R_hi < 1.
  - **Kill (H0):** R_lo > 1.
  - **Inconclusive:** otherwise.
  - **Not decidable:** the primary e\* is censored (outside 0.01–0.25), the triple check flags (|T_real| > 1), or the planted test did not pass.
- **No one-sided rule.** T18 proposed "support only, because the method errs low". T18b does not adopt it in any form, whatever families C and D show. The rule is two-sided, as above.
- **D8′. Robustness label** (reported, does not change the verdict). Same side of 1 under: V1 the authors' model (HD ≥ 3 at 0.01); V2 T18's primary (pairs set to 0); V3 the T18b posterior-mode landscape; V4 w_dead = 2⁻¹⁰ and 0.05; V5 transitions-only spectrum; V6 τ_T = 0.5 and 2. Otherwise "model-dependent", with the variants named.
- **R0** (reproduce the authors' S32B observable under V1) is run as in T18 D9.
- The `real` mode is not written yet. It will implement exactly D5′, D6′, D7′, D8′, D9 and R0, and is added and sealed only after a planted pass.

## Planted kill test

Each replicate is a synthetic full-space landscape with a known threshold. The method sees only what it would see in the real data, on the real layout, and must recover e\*_true.

- **P1. Truth** (as T18): z = z₀ + Σ aₘ + Σ pairs Eₘₙ + h(genotype) − h(WT), and F = lo + (hi − lo)·logistic(z)^(1/ν), a Richards curve with ν log-uniform in [0.5, 2], so the method's logistic is misspecified. aₘ = κ × (real latent effects shuffled across slots) + N(0, 0.2 sd), with κ uniform in [0.5, 1.6]. lo and hi come from T18's gate. h is a hash-based random field (uncorrelated higher-order epistasis). s₀ = T18 family B's latent sd = (0.95/√3)/3.83 ≈ 0.143.

| Family | Pair terms Eₘₙ | Higher-order field h | Other | Role |
|---|---|---|---|---|
| A | none | none | | noise only |
| B | Gaussian, sd s₀, symmetric | sd s₀ | | T18's failing family |
| C | \|N(0, s₀)\|, negative with probability 0.85 | sd s₀ | | mostly negative pairs |
| D | \|N(0, s₀)\|, positive with probability 0.85 | sd s₀ | | mostly positive pairs |
| E | none | sd √2·s₀ (B's total epistatic variance) | | higher-order only |
| F | as B | as B | every HD ≥ 3 genotype capped at F ≤ log2(0.01) + 0.5·N(0,1) (hash field) | cliff past 2 mutations, close to the authors' 0.01 |
| S (stress, reported only) | as B | as B | noise 1.5× what the method's noise model says | unmodelled shared noise |

- **P2. Observations (real layout).**
  - All 132 singles, and doubles only on the real measured mask (8,346).
  - Each value gets Gaussian noise with sd σ(F_true, i_real) from D10. i_real is the real input count of that slot, so noise is heteroscedastic and large for low-fitness and low-input variants, as in the data. Values are floor-censored at the real observed minimum.
  - Triples: the real triple input layout (input ≥ 10). Simulated pooled counts oₜ ~ Poisson(λₜ·Gamma) with overdispersion a. λₜ = ιₜ·c_WT·2^{F_true}, where ιₜ is the input count with input noise, plus read-error contamination from the three parent doubles at 10⁻³ per nucleotide, i.e. each parent's expected output × 10⁻³/3.
  - The method is identical to D5′ and D9.
- **P3. Criterion (pass bar).** For each of families A, B, C, D, E and F, at least 16 of the first 20 scored replicates must succeed:
  - A to E: success means |e\*_fit / e\*_true − 1| ≤ 0.20 **and** no triple flag. A false flag would make the real verdict "not decidable", so it counts as a miss.
  - F: success means within 20% **or** a triple flag. The method must not return a confident wrong threshold when HD ≥ 3 genotypes are really dead.
  - A fit that is censored (e\*_fit outside the grid) is a miss.
  - **T18b passes only if all six families pass.** S is reported only.
- **P4.** e\*_true comes from the same estimator on the truth. T18's G0 checks of that estimator passed and the estimator is unchanged.

## Calibration fallbacks (written before the gate and before any planted replicate)

- **F1. Global-epistasis fit.** As T18's F1.
- **F2. Planted test fails** (any of A to F with more than 4 misses in its first 20 scored): T18b has failed. It is reported as failed, with every family's results. Nothing is re-run at higher precision, and no rule, model, shrinkage or threshold is changed. There is no T18c, and `real` is not written.
- **F3. Censored planted truth** (e\*_true outside 0.01–0.25): not scored; replaced by the next replicate index; at most 5 per family, beyond which the family fails.
- **F4. Compute.**
  - If a planted replicate takes more than 10 CPU minutes, planted N drops to 3,000 for all later replicates (reported).
  - If the full test is estimated to need more than about 2 core hours, the first replicates of each family are run as a pilot with the same seeds and rules. A pilot can fail a family (more than 4 misses) but cannot pass one. The remaining replicates are left to the coordinator.
- **F5. Noise model.** a < 1 is set to 1 (Poisson) and b < 0 is set to 0. If fewer than 500 variants have all three output counts ≥ 5, the minimum drops to 2.
- **F6. Triple layout.** If fewer than 1,000 triples have input ≥ 10, the cut drops to input ≥ 3. If fewer than 200 remain, the triple check is dropped, and F's success becomes "within 20%" alone (and A–E's "no flag" condition falls away).
- **F7. EB variance.** τ̂ at 0 gives no pair terms (the model reduces to T18), and is used as is. τ̂ at the upper bound 3 is reported and used.
- **F8. Disk.** Outputs are compact JSON. Nothing is written that would bring the study above 500 MB.

## Limits (known before running)

- The triple check tests the mean rate of HD = 3 only, not HD 4 to 6, where the threshold quasispecies lives. A model can be right at HD 3 and wrong further out.
- Read-error contamination of triple counts (from fitter parent doubles) biases Φ_obs upward. Planted triples include it at 10⁻³ per nucleotide. The real rate after the authors' read processing is unknown.
- The input-noise overdispersion is assumed equal to the outputs' (D10). Family S measures what happens if total noise is 1.5× the model.
- All of T18's limits stand: cis-replication, activity as a proxy for replication, unmeasured w_dead, uniform per-site fidelity, and Monte Carlo bias.

## Gate results (`gate`; run after everything above was written)

Output: `scripts_out/t18b_gate.json`. About 2 CPU s.

- **Count reproduction.** Pooled fitness rebuilt from the streamed counts matches every deposited value: 8,478 of 8,478 (132 singles, 8,346 doubles), max difference 2 × 10⁻¹⁵. A first stream of the input library stopped early with no error (15.0 M of 35.6 M records). It was re-streamed with resumable range requests and checks on member length and deflate end-of-stream, and the record count now matches the authors' notebook (35,558,679).
- **Noise model (D10).** 5,348 variants, a fitted below 1, so set to 1 (F5, Poisson); b = 0.022. The binned check over-predicts the replicate variance at high counts (observed 0.007 vs predicted 0.022 in the top-count bin) and fits within about 30% elsewhere. With σ from this model, the median noise sd is 0.094 log2 for singles and 0.28 for doubles (10th–90th percentile 0.16–0.74). T18's residual sd on informative doubles is 0.95. Under this model, measurement noise explains about 6% of the double residual variance.
- **Input counts.** Median 1,969 for singles and 120 for doubles (10th percentile 53).
- **Unmeasured doubles.** 168. 94 of them were in the input with ≥ 10 reads and had zero output in all three replicates, so these are dropouts at low fitness, not random gaps. Shrinking them to a 0 pair term (D5′) gives them the curve's prediction.
- **Triple layout (inputs only).** 104,959 triples with input ≥ 10 (F6 not triggered), median input 13, summed input 1.44 M reads.

## Planted results

**Pilot result (F4), merged 2026-11-26 by `planted_merge` (`scripts_out/t18b_planted.json`): T18b FAILED its planted kill test.**

| Family | Replicates | Truth censored (F3) | Scored | Within 20% | Fit censored | Triple flags | Successes | Median relative error (draw mean / posterior mode) | Median τ̂ |
|---|---|---|---|---|---|---|---|---|---|
| A, noise only | 0–1 | 0 | 2 | 2 | 0 | 0 | 2 of 2 | +0.4% / +0.8% | 0.005 |
| B, T18's failing family | 0–4 | 2 | 3 | 1 | 1 | 0 | 1 of 3 | +23% / +9% | 0.232 |
| C, mostly negative pairs | 0–1 | 0 | 2 | 0 | 0 | 0 | 0 of 2 | +75% / +78% | 0.142 |
| D, mostly positive pairs | 0–1 | 2 | 0 | — | — | — | not scored | — | — |
| **E, higher-order only** | 0–4 | 0 | 5 | 0 | **5** | 0 | **0 of 5** | above grid / +42% | 0.159 |
| F, cliff past 2 mutations | 0–1 | 0 | 2 | 0 | 0 | 2 | 2 of 2 (flagged) | +184% / +171% | 0.225 |

- **Verdict.** Family E has 5 misses, more than the 4 a family may have in its first 20 (P3). By F2, T18b has failed. Nothing is re-run, no rule or model is changed, there is no T18c, and `real` is not written. No threshold was ever computed on the real landscape, and the triple output counts stay unread.
- **Every miss in A to E errs high.** E's truth is 0.125–0.134. Every one of its 10 posterior-draw thresholds but 2 lies above the grid's upper end (0.25), and the posterior-mode landscape gives 0.178–0.197. C errs +61% and +90%; B's scored replicates err +11%, +35% and above the grid. A, with no epistasis, is recovered within 1%. D's two truths are above the grid (F3), so D is unscored in the pilot.
- **Which rival explanation fits** (written before any replicate finished; `experiments/t18_qt45_error_threshold/README.md`).
  - **Rival 1, estimator bias from τ absorbing non-pair epistasis.** It predicted a high bias with a consistent sign, largest in E, with A unbiased. That is what happened: τ̂ in E (0.13–0.22, true pair sd 0) is as large as in B.
  - **Rival 2, a cliff the triple check cannot see.** It does not apply: F's cliff was flagged in both replicates (T ≈ −4).
  - **Rival 3, noise model.** It is not implicated: A passes, and S was not run in the pilot.
  - **Rival 4, false triple flags.** None fired in A to E.
  - **Bug check.** A rules out a plumbing bug. The posterior-mode landscape is also high in E, so the draw step is not the only cause.
- **What it means.** Singles and doubles cannot separate pair epistasis from higher-order epistasis or curve shape, and the threshold depends on how that variance is carried to genotypes 4 to 6 mutations out. T18 dropped the pair residuals and erred low (median −27% in B). T18b keeps them and errs high (+40% to beyond +95% in E). Both models fit the same singles and doubles. Under T18b's planted families, the QT45 error threshold is therefore not identifiable from HD ≤ 2 data to within 20%. **The QT45 threshold line is closed.**
- **Smallest effect the test could catch.** None was attempted on real data. The bracket is the result: on the same synthetic landscapes, the two defensible extrapolations straddle the true e\* by about −27% and +40% or more.
- **Compute.** 18 replicates at N = 5,000 (D-F4), 2.3–16.6 CPU min each, 3 workers at nice 20 on 2026-11-26.

One observation from profiling, before scoring. In planted B replicate 0 (computed on the planted data, not on real data), τ̂ = 0.246, while the true pair sd is 0.144. The doubles cannot tell pair epistasis apart from the higher-order field or from curve misspecification, so τ absorbs both. Summed over many pairs, this inflates latent variance at high HD, which may push e\* high, especially in family E. This is recorded here before any replicate was scored. It changes no rule.

### Disclosed deviation D-F4 (2026-11-26T18:38Z): planted N stays 5,000
- **The rule.** F4 says planted N drops to 3,000 for later replicates once a replicate takes more than 10 CPU min. The committed code (`t18b_analysis.py` 68a0e731, PLANT N = 5,000) never implemented this, and replicates cost about 10–15 CPU min.
- **Ruling** (coordinator, 2026-11-26). N stays 5,000 for the whole pilot and the full test. The code is not changed mid-pilot: mixing N across replicates would be worse than either choice. F4 was a fallback to save run time, and keeping N = 5,000 only raises precision.
- **What had been seen.** The ruling was made before any replicate result was read. When it was recorded, six replicate files existed (B 0, D 0–1, E 0–1, F 0). They were listed by name only. No replicate JSON or result line in the logs had been opened by any person or agent.
