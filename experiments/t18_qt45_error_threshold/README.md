# T18: can QT45 sustain its own information at its measured fidelity?

Status: **prepared, not sealed; planted kill test FAILED in family B** (A: 20 of 20 within 20%; B: 1 of 6, every miss low by 17-41%). See the prereg for the F2 consequence and the proposed T18b. The gate and the planted kill test have been run. `real` has not been run, and no threshold or Perron root of the real landscape has been computed. Prereg draft: `docs/prereg/t18_qt45_error_threshold.md` (not yet in `docs/prereg/HASHES.txt`). Prior art: `PRIOR_ART.md`.

## Question

QT45 (Gianni et al. 2026, doi:10.1126/science.adt2760) copies its complementary strand at 94.1% per-nucleotide fidelity. Is that above or below the error threshold set by its own measured fitness landscape (all 132 single and 8,346 double mutants)? The authors' own quasispecies model says it is below: active variants are "minimal (<0.5%)". But that model sets every genotype with 3 or more mutations to 0.01 of wild type, and at 94.1% most offspring carry 3 or more mutations. T18 models those genotypes from the measured singles and doubles (one global-epistasis curve, the #30 finding), estimates the threshold error rate e* with an interval, and reports R = e_meas / e*.

## Layout

- `scripts/t18_core.py`: landscapes (measured plus model, synthetic truth, analytic checks), the global-epistasis fit, the two-strand mutation model and the population Monte Carlo estimator of the Perron root and e*. It imports the #30 loaders from `experiments/qt45_epistasis/epistasis.py`.
- `scripts/t18_diag_f2.py`: one-replicate F2 precision diagnostic (output `scripts_out/t18_diag_f2_B1.json`).
- `scripts/t18_analysis.py`: modes `gate`, `planted <A|B|C> <start> <n>`, `planted_merge`, `real` (refuses until sealed).
- `scripts_out/`: `t18_gate.json`, `t18_planted_*.json` (parts), `t18_planted.json` (merged). All compact JSON.
- `raw/` (gitignored): Europe PMC full texts opened for the prior art and a copy of the authors' quasispecies code.
- `work/` (gitignored): logs.

Data: the deposited QT45 CSVs in `experiments/qt45_epistasis/raw/` (Zenodo 13891380, MIT, gitignored, about 0.25 MB). Nothing new is downloaded.

## Run

From `experiments/`, single-threaded, background priority:

```
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
taskpolicy -b nice -n 20 t1_vent_exergonic/.venv/bin/python -I t18_qt45_error_threshold/scripts/t18_analysis.py gate
taskpolicy -b nice -n 20 t1_vent_exergonic/.venv/bin/python -I t18_qt45_error_threshold/scripts/t18_analysis.py planted A 0 20
taskpolicy -b nice -n 20 t1_vent_exergonic/.venv/bin/python -I t18_qt45_error_threshold/scripts/t18_analysis.py planted_merge
```

Costs: gate about 15 CPU s; one planted replicate 30 to 80 CPU s; `real` (after the seal) is estimated at 2 to 4 core hours (primary at N = 20,000, 30 bootstrap refits, 9 variants), one process, under 100 MB of memory and under 1 MB of output.

## Ruling on fallback F2 (2026-11-25)

Kill test failed; F2 re-run not run (failure is systematic bias per the attached diagnostic, `scripts_out/t18_diag_f2_B1.json`; a precision re-run cannot fix it); no real-data threshold computed. In family B the estimate was always low (median −27%, 1/6 within 20%), and a 4× larger population still missed by −23%. More replicates sharpen a biased estimate without removing the bias. The follow-up is T18b, which keeps the measured pair terms. If T18b also fails its planted test, the QT45 threshold line closes.


## T18b: pair epistasis kept (prereg `docs/prereg/t18b_qt45_pair_epistasis.md`)

Status: **prereg written, gate run (passed), planted kill test running as a pilot. Not sealed. No real-data threshold, R, growth rate, EB variance τ² or triple fitness has been computed.** This is the last attempt: if T18b fails its planted test, it is reported as failed and there is no T18c.

- **Model.** WT, singles and measured doubles use their measured values. Genotypes with 3 or more mutations are F = g(z₀ + Σ a + Σ Ê_pair), with T18's global curve plus the measured pair terms on the latent scale. The pair terms are shrunk by empirical Bayes: one prior variance τ² by marginal likelihood, and per-double noise from a replicate noise model fitted to the three output replicates' read counts. The 168 unmeasured pairs are set to 0. The threshold uses posterior draws (mean of e\* over 2 planted or 4 real draws), not the posterior mean, because shrinkage removes exactly the variance that raises e\*.
- **Triple check.** The deposit's reads contain about 105,000 triples with input ≥ 10. The mean triple replication rate predicted by the model is compared with the observed rate, and a gap of more than a factor of 2 flags the model. The triple output counts stay unread until `real`.
- **Planted families.** A (noise only), B (T18's pair plus higher-order), C (mostly negative pairs), D (mostly positive), E (higher-order only), F (HD ≥ 3 cliff near the authors' 0.01), and S (noise 1.5× the model; stress, reported only). The pass bar is at least 16 of 20 successes in each of A to F. There is no one-sided rule.
- **Scripts.**
  - `scripts/t18b_counts.py` streams per-replicate counts from Zenodo with HTTP range requests into gitignored `raw/t18b_counts/` (about 21 MB).
  - `scripts/t18b_zipdir.py` lists a remote zip's members from its tail.
  - `scripts/t18b_core.py` holds the noise model, EB pair fit, pair landscape and planted truth.
  - `scripts/t18b_analysis.py` has the modes `gate`, `planted <fam> <start> <n>`, `planted_merge`, and `real` (which refuses).
  - All import the unchanged `t18_core.py`.
- **Outputs.** `scripts_out/t18b_gate.json`, `scripts_out/t18b_planted_rep_<fam>_<rep>.json` (one per replicate), and `scripts_out/t18b_planted.json` (merged by `planted_merge`).
- **Runtime-only change (2026-11-25, after a server restart killed the first pilot before any replicate finished).** `planted` now writes each replicate to its own JSON as soon as it finishes (atomic rename) and skips replicates whose JSON exists. `planted_merge` reads the per-replicate files. No computation, seed or rule changed: replicates are seeded by family and index.
- **Cost.** About 10 to 15 CPU min per planted replicate (4 thresholds: truth, 2 posterior draws, posterior mode). The full test (120 replicates) is about 20 to 30 core hours, so a pilot is run (prereg F4): B and E with 5 replicates each, and A, C, D and F with 2 each.

Run (from `experiments/`; on the new laptop (2026-11-26) the venv is the repo's `.venv`, Python 3.15.2 with numpy 2.5.5 and scipy 1.18.1, the same numpy/scipy as the old `t1_vent_exergonic/.venv`, and workers are harness background commands via `work/t18b_worker.sh`, not tmux):

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 taskpolicy -b nice -n 20 t1_vent_exergonic/.venv/bin/python -I t18_qt45_error_threshold/scripts/t18b_analysis.py planted B 0 5 >> t18_qt45_error_threshold/work/t18b_pl_B.log 2>&1
t1_vent_exergonic/.venv/bin/python -I t18_qt45_error_threshold/scripts/t18b_analysis.py planted_merge
```

### Rival explanations for the pilot outcome (written 2026-11-26, before any pilot replicate finished)

No `t18b_planted_rep_*.json` existed when this was written. Each rival predicts a different pattern across families, so the pilot can tell them apart.

1. **Estimator bias from τ absorbing non-pair epistasis.** τ̂ (0.246 in B replicate 0, true pair sd 0.144) soaks up the higher-order field and the curve misspecification. Prediction: e\*_fit is high, with a consistent sign, in E (no true pairs) and to a lesser degree in B, C and D, while A is unbiased. The posterior-mode diagnostic sits closer to the truth than the draw mean.
2. **Model misspecification at HD ≥ 3 that the triple check cannot see.** Prediction: F misses high *without* a triple flag, while A–E are fine. If F misses but flags, the safeguard works as designed and counts as a success.
3. **Noise-model problems.** The planted noise is drawn from the method's own noise model, so a wrong noise model cannot fail A–F. It can only show up in S. Prediction if noise matters: S fails while A–F pass. A failure in A, which has no epistasis, would point instead to Monte Carlo noise in the threshold estimator: errors of both signs, shared by the truth run.
4. **False triple flags.** Planted contamination (10⁻³) or overdispersion makes |T| > 1 on landscapes whose HD ≥ 3 model is right. Prediction: misses in A–E with an accurate e\* but flag = true.

Independent check on the measure. `rel_err` is computed against e\*_true from the same estimator run on the truth. A separate check, T18's G0 analytic tests, has already shown that estimator unbiased. A pass therefore means that the T18b model recovers the planted landscape's threshold, not that the estimator is right. Per the rules, any surprise, for example a family doing better than A, is treated as a bug, leak or artefact until it is ruled out.
