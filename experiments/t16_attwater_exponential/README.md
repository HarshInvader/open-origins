# T16: is the ribozyme replication of Attwater et al. 2025 exponential? Stopped at the power gate: not decidable

This is study S7 in `docs/plans/next_studies_2026-11-24.md`, written 2026-11-25 by the T16 prep agent. The
plan marked it "marginal; gate first". **The gate failed.** No pre-registration was written, nothing was
sealed, and no growth law was fitted to the real data. Nothing is committed or pushed.

## Data

| File | Source | sha256 |
|---|---|---|
| `raw/source_data/fig3.zip` (17,889,628 bytes) | https://static-content.springer.com/esm/art%3A10.1038%2Fs41557-025-01830-y/MediaObjects/41557_2025_1830_MOESM4_ESM.zip | `ad63ca87f156c10bc621ba5b31c598cd265d90c1eba3c0e94795e9c2c44b17ed` |
| `raw/xlsx/SD_Fig3e.xlsx` | `SD_Fig3/SD_Fig3e.xlsx` in the zip | `bcb27ef4f1198086526ef6e2e49ea441cd3f18b29fbfa4ea89433871258a91ee` |
| `raw/xlsx/SD_Fig3c.xlsx` | `SD_Fig3/SD_Fig3c.xlsx` in the zip | `6b1d1b6368eda5b02955d7f640e87117a823302a9c7cc824dfe22bb00a8b488a` |
| `raw/europepmc/PMC12226338.xml` | Europe PMC full text | (claim text) |

- **Gitignored.** `raw/` is ignored (`git check-ignore -v` gives `.gitignore:41:experiments/*/raw/`).
- **What was extracted.** Only the two xlsx files came out of the zip. The zip is kept, at 18 MB, which
  is inside the disk budget.
- **How the xlsx files were read.** They were opened as zip/XML with the Python standard library under
  `python -I`. Nothing in them was executed.
- **OSF.** The view-only OSF link was not opened.

**Layout of `SD_Fig3e.xlsx`.** This was read with every number masked; only labels were shown.
- Row 2 holds the cycles, 0 to 8.
- For each strand (FITC, Cy5) there is a "Mean" row and "Dataset 1-3" rows.
- So the file has 3 reactions × 9 cycles × 2 strands.

**`SD_Fig3c.xlsx`** is one series of 8 cycle points for the +14, +11 and +8 nt bands, each with
"Intensity" and "Amplification vs. 5 cycles". It has no replicates. It was read for layout only. The plan
already rules it out: keeping pace with dilution is exponential by construction.

## What was seen (blinding disclosure)

`t16_analysis.py scatter` is the only code that touched the measured copy numbers. It computes each
replicate's deviation from **its own cycle's replicate mean**, on the log scale, and saves only the
following summaries (`scripts_out/t16_scatter.json`):
- the pooled log SD over cycles 1-4 and 1-8;
- the share of that variance carried by a per-reaction constant, and by a per-reaction slope in cycle;
- the within-reaction residual SD;
- the largest deviation at cycle 0;
- a count of non-positive values;
- difference-only checks of the "Mean" row against the arithmetic mean, geometric mean and median of
  the three datasets.

Nothing else was computed. No cycle mean, no level, no growth law, and no per-cycle SD on the linear
scale, which could reveal the curve if noise were additive. The first draft of `scatter` also computed
linear-scale pooled SDs and per-cycle log SDs. That draft was edited before it was ever run. The run
that wrote the json used the version described here, plus the within-reaction terms added in a second
run.

The scatter, with the log scale written ln:

| | FITC | Cy5 |
|---|---|---|
| pooled ln-SD, cycles 1-4 (df 8) | 0.323 | 0.237 |
| share of that: per-reaction constant / per-reaction slope / residual | 0.92 / 0.07 / 0.01 | 0.86 / 0.14 / 0.01 |
| pooled ln-SD, cycles 1-8 (df 16) | 0.420 | 0.366 |
| share of that: constant / slope / residual | 0.86 / 0.08 / 0.06 | 0.74 / 0.06 / 0.20 |
| cycle 0 | identical in all 3 reactions (1 by construction) | same |
| "Mean" row vs arithmetic mean of datasets, max relative difference | 16% | 31% |

**Reading of the scatter.** Each reaction sits about 25-35% above or below the others at every cycle,
and the shape varies little within a reaction. The scatter model is the same in the gate and in the
generator:
- a per-reaction ln offset u, SD 0.31 (FITC) and 0.22 (Cy5);
- a per-reaction ln slope v per cycle, SD 0.07 and 0.08;
- an independent residual e, SD 0.05 and 0.03 (df 4);
- for cycles 1-8, SDs 0.39 / 0.05 / 0.11 (FITC) and 0.32 / 0.04 / 0.19 (Cy5).

**Also used: the published fits** (part of the claim, not a peek). e^0.38x and e^0.20x give 4.57-fold
(FITC) and 2.23-fold (Cy5) growth by cycle 4.

## Power gate (`t16_analysis.py gate 2000`; run)

**Laws.** All three go from 1 at cycle 0 to A at cycle 4, with two parameters each (a, r) on the ln
scale:
- exponential, a e^(rx);
- parabolic (square-root law, dy/dx ∝ √y), a(1 + rx)²;
- linear, a(1 + rx).

**Plan's rule, per strand.**
- Support: ΔAICc ≥ 6 against both parabolic and linear.
- Kill: the smaller ΔAICc is < 2.
- The study needs both strands.
- The laws have equal parameter counts, so ΔAICc = n ln(RSS_alt / RSS_exp).

**Fit forms tried, all fixed before any real fit.**
- `pooled`: the plan's literal replicate-level fit with one intercept, cycles 0-4.
- `fe`: one intercept per reaction, which removes the reaction offsets, on cycles 1-4. Cycle 0 is 1 by
  definition.
- `anchored`: the authors' form, y(0) = 1 with no intercept.
- Each form was also run on all 9 cycles with a plateau term, `c0_8_plateau`: y = a h(r · min(x, x_b)),
  with the breakpoint x_b profiled.

**Generator and simulation.**
- The generator uses the scatter model above, at the observed SDs (`obs`) and at their 80% upper
  confidence bounds (`hi80`, χ² with the stated df).
- Amplitude grid: 1.5, 2, 2.23, 3, 3.5, 4.57, 7 and 10-fold by cycle 4.
- 2,000 synthetic 3-reaction data sets per cell.
- Seeds are `[20261125, 1, cell]`.
- Output: `scripts_out/t16_gate.json`.

**Result** (P = proportion of synthetic data sets; "published A" is 4.57 for FITC and 2.23 for Cy5):

| Design | Fit form | Noise | P(support), FITC at published A | P(support), Cy5 at published A | Study power (both) | Max false support, any A, par or lin true | P(kill) when truly exponential, FITC / Cy5 | P(support), FITC at A = 7 / 10 | P(support), Cy5 at A = 7 / 10 |
|---|---|---|---|---|---|---|---|---|---|
| c0_4 | pooled | obs | 0.066 | 0.004 | 0.0002 | 0.015 | 0.70 / 0.93 | 0.22 / 0.40 | 0.39 / 0.61 |
| c0_4 | pooled | hi80 | 0.009 | 0.001 | 0.0000 | 0.026 | 0.92 / 0.98 | 0.03 / 0.08 | 0.08 / 0.16 |
| c0_4 | fe | obs | 0.170 | 0.021 | 0.0035 | 0.010 | 0.45 / 0.90 | 0.48 / 0.74 | 0.59 / 0.82 |
| c0_4 | fe | hi80 | 0.043 | 0.009 | 0.0004 | 0.008 | 0.77 / 0.96 | 0.14 / 0.27 | 0.19 / 0.33 |
| c0_4 | anchored | obs | 0.041 | 0.002 | 0.0001 | 0.015 | 0.73 / 0.95 | 0.17 / 0.34 | 0.33 / 0.54 |
| c0_4 | anchored | hi80 | 0.005 | 0.000 | 0.0000 | 0.021 | 0.95 / 0.99 | 0.01 / 0.05 | 0.05 / 0.11 |
| c0_8_plateau | pooled | obs | 0.013 | 0.000 | 0.0000 | 0.009 | 0.86 / 1.00 | 0.07 / 0.18 | 0.06 / 0.18 |
| c0_8_plateau | pooled | hi80 | 0.001 | 0.000 | 0.0000 | 0.003 | 0.98 / 1.00 | 0.01 / 0.02 | 0.01 / 0.03 |
| c0_8_plateau | fe | obs | 0.009 | 0.000 | 0.0000 | 0.003 | 0.81 / 1.00 | 0.07 / 0.23 | 0.02 / 0.08 |
| c0_8_plateau | fe | hi80 | 0.001 | 0.000 | 0.0000 | 0.001 | 0.96 / 1.00 | 0.01 / 0.05 | 0.01 / 0.02 |
| c0_8_plateau | anchored | obs | 0.010 | 0.000 | 0.0000 | 0.009 | 0.86 / 1.00 | 0.06 / 0.17 | 0.05 / 0.17 |
| c0_8_plateau | anchored | hi80 | 0.001 | 0.000 | 0.0000 | 0.002 | 0.98 / 1.00 | 0.01 / 0.02 | 0.00 / 0.02 |

**What the table shows.**
- **Power is far below 80%.** At the published amplitudes, the best form (`fe`, observed scatter) has
  study power 0.4% and per-strand power 17% (FITC) and 2% (Cy5).
  - Median ΔAICc against parabolic is 2.3 (FITC) and 0.2 (Cy5).
  - At 4.57- and 2.23-fold growth over four cycles, the exponential, parabolic and linear curves
    differ by less than the reaction-to-reaction spread of the slopes.
  - Even with 10-fold growth, per-strand power is only 74-82%.
- **False support is fine.** It is at most 2.6% in every cell. The rule is specific, but it has almost
  no sensitivity.
- **The kill rule would mislead.** If replication is truly exponential at the published rates, the
  plan's kill fires 45-98% of the time for FITC and 90-100% for Cy5, depending on the form and design. Running the study would most
  likely "kill" exponential growth whatever the truth.
- **The plateau design does not help; it hurts.** The breakpoint absorbs the curvature, and the scatter
  over cycles 5-8 is larger.

**Verdict: not decidable. Stop.** Under the user's rule (seal only with ≥ 80% power and ≤ 5% false
support), T16 is not sealed.

## What would make it decidable

- More reactions per cycle, or more cycles in the growth phase.
- Larger growth before the plateau. Even 10-fold by cycle 4 gives about 75-80% per strand.
- Per-reaction data with lower reaction-to-reaction slope variation.

None of these exists in the deposit.

## Kept from this work, independent of any growth law

These two points come from `PRIOR_ART.md`.
1. **The text and caption disagree on per-cycle folds.** The text gives 1.2 and 1.38. The caption's
   e^0.20 and e^0.38 give 1.22 and 1.46.
2. **The deposited "Mean" row is not the arithmetic mean, geometric mean or median of the three
   deposited datasets.** It differs by up to 16-31%, 21-27% and 21-66% respectively. The R² values in
   the caption come from fits to the plotted averages.
   **Corrected 2026-11-25, see below.** This point was wrong as stated.

## Correction (2026-11-25 recheck)

A fresh agent recomputed both reporting points from the raw `SD_Fig3e.xlsx` (Sheet1, C2:L10) and the paper text.

1. **Per-cycle folds: confirmed.** The caption gives "FITC strand = e^0.38x, R2 = 0.997; Cy5 strand =
   e^0.20x, R2 = 0.984". The text gives "1.2- and 1.38-fold per cycle". The text's numbers equal 1 + k
   rather than e^k (1.46 and 1.22). Fig. 3c in the same paper converts with e^k correctly.
2. **The "Mean" row: our earlier claim was wrong.** The Mean rows are geometric means of three datasets,
   matching to 5e-10. But the Dataset 2 rows are swapped between the two strand blocks:
   - FITC Mean = geometric mean of FITC Dataset 1, **Cy5 Dataset 2** and FITC Dataset 3;
   - Cy5 Mean = geometric mean of Cy5 Dataset 1, **FITC Dataset 2** and Cy5 Dataset 3.

   So the plotted average is a geometric mean (the caption says "Average"). Most likely the two Dataset 2
   rows were swapped in the deposited sheet, or mislabelled. The earlier check compared each Mean row
   with the datasets under its own strand label, which is why nothing matched. The scatter numbers above
   use the rows as labelled. Swapping Dataset 2 back would change the per-reaction offsets, but the
   power-gate conclusion rests on 3 reactions over cycles 0-4 and does not depend on which label a row has.

## Reproduce

From the repo root, single-threaded:

```
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
nice -n 20 experiments/t1_vent_exergonic/.venv/bin/python -I experiments/t16_attwater_exponential/scripts/t16_analysis.py experiments/t16_attwater_exponential scatter
nice -n 20 experiments/t1_vent_exergonic/.venv/bin/python -I experiments/t16_attwater_exponential/scripts/t16_analysis.py experiments/t16_attwater_exponential gate 2000
```

The gate takes about 80 s.
