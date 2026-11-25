# T15 result: dynamic-flow formose shifts are no larger than the gap between repeat runs; sealed verdict kill

Prereg: `docs/prereg/t15_formose_flow_noise.md`, sealed in 5304720 (`HASHES.txt`). Script: `scripts/t15_analysis.py` (sha256 047456a0…). Output: `scripts_out/t15_real.json`. Data: github.com/huckgroup/Formose_2022 at commit 94c10347.

## Claim

van Duppen, Daines, Robinson and Huck 2023 (J. Am. Chem. Soc. 145:7559, doi:10.1021/jacs.3c00908) ran the formose reaction in a flow reactor, both at steady state and with the calcium hydroxide input or the flow rate changing over time. Their abstract says: "Surprisingly, the product compositions of the formose reaction under dynamic conditions deviate significantly from those under steady state conditions". They report p ≤ 1 × 10⁻⁴ for DHA (3), threose (5), erythrulose (7) and xylulose (11) in every series.

**Their test.** The authors' code, read as text, uses `scipy.stats.ttest_ind`. That is a pooled t-test on the 43–50 serial samples of one run against another. It treats every sample as an independent draw and has no term for run-to-run variation. The deposit contains two pairs of repeat runs at identical settings, which the paper never compares:
- EXP001 and EXP010, both at steady state;
- EXP003 and EXP012, both at the same fluctuating setting.

**This test.**
- **Effect size.** D = |difference in run means| / pooled within-run SD.
- **D_dyn** is the median D over the paper's 8 dynamic-versus-steady comparisons.
- **D_rep** is the larger D of the two repeat pairs.
- **Interval.** A 95% moving-block bootstrap interval for D_dyn − D_rep, with block length 5 samples.

## Sealed verdict: kill (4 of 4 compounds)

| Compound | D_dyn (median of 8) | D_rep (two repeat pairs) | D_dyn − D_rep (95% interval) |
|---|---|---|---|
| DHA (3) | 1.83 | 5.91 (3.79, 5.91) | −4.07 (−6.25, −2.68) |
| Threose (5) | 1.78 | 2.74 (2.74, 0.10) | −0.96 (−2.13, −0.39) |
| Erythrulose (7) | 2.43 | 14.67 (14.67, 12.96) | −12.23 (−19.88, −10.07) |
| Xylulose (11) | 0.92 | 3.17 (3.17, 1.82) | −2.25 (−7.89, −0.99) |

- **Kill rule.** For each compound, D_dyn is below 2 × D_rep, and the lower end of the interval is ≤ 0. Both clauses hold for all four compounds. The rule needed 3 of 4. Support needed D_dyn > 3 × D_rep, which no compound reaches.
- **Erythrulose may not be a fair yardstick.** Its repeat gap (13–15 SD) is suspiciously large, and peak assignment for it may shift between days (prereg decision 4). The kill does not depend on it: DHA, threose and xylulose meet both clauses on their own.
- **The same verdict holds in each series.** The amplitude series at 20, 50 and 100 mM formaldehyde and the rate series each give kill under the sealed rule (reported only).
- **The plan's literal kill clause gives "neither".** That clause requires the interval to include 0. Here every interval lies wholly *below* 0: the dynamic shifts are smaller than the repeat gap. The planted check showed that clause almost never kills (prereg change C2).

## Reported only (no rule)

- **The authors' t-test is far too liberal.** Over the 32 tests (8 comparisons × 4 compounds), it gives p < 10⁻⁴ in 25. A Welch test with the sample size corrected for serial correlation gives p < 10⁻⁴ in 19. Neither test accounts for run-to-run variation, and that variation is the larger problem.
- **Some single comparisons are large.** EXP006 against EXP004 gives 12.1 SD for DHA and 8.8 SD for erythrulose. That is larger than any repeat gap for DHA. The *typical* dynamic shift, the median used by the rule, is 1–2.4 SD.

## Reading

- **What it shows.** Across the paper's 8 comparisons, the typical change between dynamic and steady-state conditions in the four highlighted sugars is about 1–2.4 within-run SD. Two runs at identical settings differ by 2.7–6 SD for three of these compounds, and by about 14 SD for erythrulose. As deposited, the data cannot separate the effect of changing flow from run-to-run reproducibility. The p-values in the paper come from a test that leaves out run-to-run variation entirely.
- **What it does not show**, as fixed at the seal:
  - It does not show that changing flow has no effect on the formose reaction.
  - Both repeat pairs were run on different days, while each of the authors' comparisons is within one day. Within-day repeat noise may be smaller, but the deposit has no within-day repeats.
  - The test has limited power: the planted check gives about 49% kill even at a true 3 SD shift.
  - Peak assignment may differ between days, which could inflate the yardstick, especially for erythrulose. This cannot be checked without the chromatograms.
- **The fair summary.** "Dynamic conditions change the product mixture" may be true. It is not demonstrated beyond the between-run variability that this deposit itself contains. A within-day repeat design would settle it.

## What it means for us

- **For the metabolism-first and "messy chemistry" routes,** one piece of evidence that environmental fluctuation steers prebiotic reaction networks is weaker than its p-values suggest. Follow-up work that builds on it (Baltussen et al. 2024, de Jong et al. 2025) should be read with run-to-run noise in mind.
- **Method lesson, the same as T8 and T12.** Serial samples within one run are not replicates. The yardstick for "conditions changed the outcome" is a repeat run at the same conditions.
- This is a clean reanalysis of deposited data, and the authors' own code identified their test. Asking the authors about within-day repeats and peak assignment could be worthwhile. The owner decides.
