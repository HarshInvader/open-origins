# Planted LUCA recovery on simulated trees (task #9): results

Verdict: **negative for gene-tree-free LUCA rules.** Not one rule met the sealed pass mark in any of the 10 grid cells, including the cells with no gene transfer at all. The decisive output, the largest τ/μ at which R4 (the Moody-like rule) stays validated, is **none**.

- Pre-registration: `docs/prereg/luca_planted_recovery.md`. Its hash matched `HASHES.txt` at judging (4b4aff10…, sealed 2026-11-18T07:12Z).
- Run: `sim.py`, 100 runs (2 loss rates × 5 transfer ratios × 10 seeds), through `board/run.sh`. Output is in `out/runs.jsonl`; the summary is from `summarize.py`.
- Judged by the lead against the sealed marks. No analysis choices were made after seeing the data.

## Pass marks (fixed in advance)
- **Rule validated:** mean precision ≥ 0.8 and mean recall ≥ 0.5.
- **Size estimate validated:** mean |relative error| ≤ 20%.

## Precision / recall (mean over 10 replicates)

| loss μ | τ/μ | R1 both domains | R2 Weiss breadth | R3 ML≥0.75 | R4 = R3+R1 | R5 ML≥0.5 | R6 oracle |
|---|---|---|---|---|---|---|---|
| 1 | 0 | 1.00 / 0.28 | 1.00 / 0.24 | 1.00 / 0.28 | 1.00 / 0.28 | 0.63 / 0.98 | 1.00 / 0.24 |
| 1 | 0.1 | 0.80 / 0.40 | 0.97 / 0.27 | 0.97 / 0.30 | 0.97 / 0.30 | 0.64 / 0.98 | 1.00 / 0.25 |
| 1 | 0.3 | 0.68 / 0.55 | 0.89 / 0.31 | 0.92 / 0.32 | 0.92 / 0.32 | 0.70 / 0.77 | 1.00 / 0.23 |
| 1 | 1 | 0.58 / 0.84 | 0.74 / 0.48 | 0.83 / 0.39 | 0.83 / 0.39 | 0.80 / 0.43 | 1.00 / 0.19 |
| 1 | 3 | 0.50 / 0.99 | 0.66 / 0.77 | 0.73 / 0.58 | 0.73 / 0.58 | 0.70 / 0.65 | 1.00 / 0.12 |
| 2 | 0 | 1.00 / 0.12 | 1.00 / 0.10 | 1.00 / 0.12 | 1.00 / 0.12 | 0.65 / 0.78 | 1.00 / 0.10 |
| 2 | 0.1 | 0.57 / 0.33 | 0.85 / 0.11 | 0.86 / 0.13 | 0.86 / 0.13 | 0.60 / 0.80 | 1.00 / 0.07 |
| 2 | 0.3 | 0.49 / 0.56 | 0.71 / 0.20 | 0.76 / 0.17 | 0.76 / 0.17 | 0.60 / 0.72 | 1.00 / 0.05 |
| 2 | 1 | 0.44 / 0.92 | 0.62 / 0.55 | 0.69 / 0.35 | 0.69 / 0.35 | 0.57 / 0.96 | 1.00 / 0.03 |
| 2 | 3 | 0.37 / 1.00 | 0.56 / 0.85 | 0.60 / 0.87 | 0.60 / 0.87 | 0.41 / 1.00 | 0.90 / 0.01 |

**Validated cells: 0 of 60 rule × cell combinations.** The rules fail in one of two ways:
- **Strict rules miss most of the truth.** R2, R3, R4 and R6 keep precision high but recall at most 0.39 wherever precision is ≥ 0.8.
- **Loose rules let false positives in.** R1 and R5 reach high recall only where transfer drives precision below 0.8.

## Size estimate (Σ posterior vs true count)

| loss μ | τ/μ = 0 | 0.1 | 0.3 | 1 | 3 |
|---|---|---|---|---|---|
| 1 | +0.6% | +2.9% | +9.4% | +15% | +39% |
| 2 | +0.2% | +28% | +52% | +123% | +254% |

- The error is always an **over**estimate, and it grows with transfer.
- The estimate is validated only at μ = 1 with τ/μ ≤ 1, and at μ = 2 with no transfer.

## The sealed prediction, checked
- **"R1/R2 precision falls below 0.8 once τ/μ ≥ 0.3": partly right.**
  - R1 falls as predicted: 0.68 and 0.49 at τ/μ = 0.3.
  - R2 holds at μ = 1 until τ/μ = 1, where it reaches 0.74.
- **"R3/R4 do better on precision": right.** At μ = 1, τ/μ = 0.3, R4 scores 0.92 against R1's 0.68.
- **"Size estimate biased upward under transfer": right.** At high loss the bias is large: +28% even at τ/μ = 0.1.

## What this does and does not mean
- **It does not test or refute Moody et al. 2024.** They used ALE, which reconciles gene trees with the species tree. These rules use only presence and absence, apart from the R6 oracle. The result bounds the simpler shortcuts, not the published method.
- **For task #10 (robustness scan on Moody's data):** a presence-based reanalysis of their data would be uninformative. The scan needs gene-tree reconciliation, or it should be reframed as "how sensitive is the LUCA size to the transfer rate".
- **Recall is low even with no transfer, partly by design.** With loss μ = 1, only about 28% of observable LUCA families survive in both domains. Families surviving in one domain only count in the truth set but no two-domain rule can find them. The sealed recall denominator includes them, and we keep it as sealed.
- **Exploratory, not part of the verdict:** with the denominator restricted to families present in both domains, the strict rules would look much better. This is noted for the red team and is not used to change the verdict.
- **Limits:** there is no duplication, and the loss and transfer grid is set in advance rather than taken from published rates, because Moody gives none. The species trees are Yule trees with 64 tips.
