# Pre-registration amendment v3: making the LUCA calibration runnable (task #32)

Agent: orig-paper. Written 2026-11-19, after smoke tests and before any fitting, pilot or main simulation. v1 (`13cb4388…`) and v2 (`39f790b0…`) stay in force except where changed here. The predictions P1-P6, the decision rule on the real-data endpoint, and the 865/1,032/1,613/1,936 thresholds are unchanged.

## What the smoke tests showed (seen before writing this)
These were plumbing tests on tiny runs: 30 tips and about 40 root families. Their scores are not part of the study.

1. **AleRax 1.4.0 refuses the v1 setting.** `--origination OPTIMIZE` with `--model-parametrization PER-FAMILY` is rejected; OPTIMIZE only runs with per-species settings, which were about 40× slower. AleRax also crashes on 2-gene families, and it exits with status 0 when it aborts. `--origination ROOT` gives PP ≈ 1 to almost every reconciled family.
2. **Moody's actual pipeline is not AleRax.** Their deposited `COG_OR_reconciliation/O_R_Optimization.py` (read 2026-11-19) works in two steps:
   - it takes ALEml_undated `.uml_rec` files, run with flat origination;
   - it then reweights each family's per-branch origination likelihoods by a root prior exp(O_R), with O_R optimised per COG category over the bounds (1, 20).
   Their fitted root weights range from about 33 to about 3,600. Categories B and W sit at the bound, exp(20) ≈ 4.85 × 10⁸.

   So the faithful test is to run ALEml_undated and their reweighting, not AleRax.
3. **In the no-transfer, true-tree smoke test, the misses were LUCA families present in only one domain among the sampled genomes.** Any method that places origination by the sampled taxa cannot identify these, so v1's planted-control gate (T50 recall ≥ 0.9 over all LUCA families) tests the definition of the truth, not whether our pipeline is correct.
4. **Cost.** Extrapolated from smoke runs, the v1/v2 scale costs 2-5 days of 2-core time per simulation, which is weeks for the grid. Zombi with additive transfers at transfer/loss ≥ 1 makes genomes grow without limit.

## Changes
1. **Reconciliation, now primary: Moody's two-step method.**
   - ALEml_undated runs per family on the 1,000 UFBoot trees (ALEobserve) with the sampled species tree, using ALE's default undated model with flat origination. Each genome's fraction missing is 0, because simulated genomes are complete.
   - Their `O_R_Optimization.py` logic is then applied unchanged, except for one adaptation: our families have no COG categories, so one global O_R is fitted. This is done by importing their functions on our `.uml_rec` files. Bounds (1, 20), Bayesian optimisation with 10 initial points and 50 iterations, random_state 1, as in their script.
   - **Root PP** is defined exactly as in their script: `p[max_id]`, the reweighted posterior probability that the family originated at the root. Under the undated model, a family is present at the root only if it originated there.
   - Their `merge.py` averages O_R over a family's COG categories. With one global O_R, that step does not apply.
   - **ALE build.** ALE is built from its public source (github.com/ssolo/ALE, recorded commit) against bioconda Bio++. If it cannot be built and verified within one working day, the fallback is AleRax `--model-parametrization ORIGINATION-PER-SPECIES --origination OPTIMIZE`. The fallback is labelled "not Moody's pipeline" and the real-data endpoint is then reported as indicative only.
   - **Verification of the ALE build.** On Moody's own deposited data, our ALE plus reweighting must reproduce their per-family consensus PP for 50 randomly chosen families (seed 0) to within 0.05 mean absolute difference. Their `.uml_rec` files, from the Bristol data repository, are used if they can be downloaded. Otherwise we rerun ALE on their gene-tree files for those 50 families.
2. **Planted-control gate, restated.**
   - The gate is scored on identifiable LUCA families: present in both domains among the sampled genomes, with ≥ 3 sampled genes.
   - Pass: recall at T50 ≥ 0.9, and the share of non-LUCA families among T50 calls ≤ 0.05.
   - R over all LUCA families is reported, but it does not gate.
   - The unidentifiable share (one-domain LUCA families) is a genuine part of the main bias and stays in every main measure.
3. **Scale and model.**
   - 40 sampled genomes per domain (80 in all) and 600 root families.
   - Sequence length 157 (v2).
   - The fit grid in v2 becomes loss L ∈ {0.5, 1, 2, 4} and transfer/loss ∈ {0.1, 0.2, 0.4, 0.6}. Transfers are additive, and these ratios keep genome size bounded.
   - Family rate heterogeneity: Zombi Gm draws each family's rates from a lognormal with mean equal to the set rate and σ = 0.5.
   - Zombi's amino-acid model is WAG; inference uses LG+G4, so the model is misspecified on purpose, as with real data.
   - **v2's 240/120 rule is replaced:** 40 per domain if the timing pilot's full per-simulation time is ≤ 12 h with 2 workers, otherwise 30 per domain.
4. **Main grid.** Unchanged in form (3 transfer settings × 3 replicates, plus the planted control). The sensitivity analysis is the reweighting with O_R fixed at 1, flat origination, replacing v1's AleRax ROOT.
5. **2-gene families.** Under ALE they are reconciled normally. Under the AleRax fallback, they get PP = 0 and are counted as missed.

## Limits added
- The global O_R replaces per-category values.
- The model is smaller again (80 genomes against Moody's 700), which may change transfer detectability. The fit check in v2 remains the guard for transfer to real data.
- If the ALE build fails, this study does not test Moody's exact pipeline, and it will say so in its title.
