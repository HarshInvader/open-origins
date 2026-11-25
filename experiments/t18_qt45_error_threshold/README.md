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
