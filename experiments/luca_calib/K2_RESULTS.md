# K2: does Moody's fitted root weight recover a planted root genome? (prereg v5, v5a, v5b; task #32)

Run 2026-11-21. ALE on true gene trees; Moody's reweighting with one global O_R in [1, 20]; origination 40, 200 root families, seed 1. Scores in `results/k2/<cell>/score/`.

| Genomes / domain | Transfer | True root families | Σ PP fitted | R | Σ PP flat | R flat | Fitted O_R | Families ALE crashed on (all true root) | R without crashed families |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 0.2 | 171 | 155.9 | 0.912 | 99.0 | 0.579 | 3.94 | 0 | 0.912 |
| 20 | 0.4 | 179 | 176.6 | 0.986 | 93.5 | 0.522 | 4.20 | 2 | 0.998 |
| 40 | 0.2 | 179 | 171.3 | 0.957 | 106.4 | 0.595 | 4.32 | 4 | 0.979 |
| 40 | 0.4 | 180 | 168.7 | 0.937 | 108.6 | 0.603 | 4.31 | 15 | 1.023 |
| 80 | 0.2 | 179 | 146.0 | 0.816 | 105.6 | 0.590 | 4.26 | 34 | 1.007 |
| **80** | **0.4** | **189** | **141.9** | **0.751** | 87.4 | 0.463 | 4.21 | 57 | 1.075 |

At the decision cell (80, 0.4): PP ≥ 0.5 calls 135 families, 120 true (recall 0.63, false share 0.11); PP ≥ 0.75 calls 121, 113 true (recall 0.60, false share 0.07). Families with PP 0.8-1.0: 119, of which 95% are true root families.

## Sealed decision
R = 0.751 at 80 genomes per domain and transfer 0.4 is outside 0.8-1.25, so under v5b the result is **"dead before the grid"**.

## Red team (after reading the scores; not part of the sealed rule)
1. **The failure comes from ALE crashing, not from the reweighting.** ALEobserve overflows (Boost `tgamma` / `double_factorial`) on very large families, and these are always true root families: 57 of 57 at the decision cell. They are scored PP 0 (DEVIATIONS 11), so R drops as tip count grows, because more root families get large enough to crash. With those families left out, R is 0.91-1.08 in every cell.
2. **So with true gene trees, the fitted root weight is roughly calibrated at these settings.** It neither inflates nor deflates the root set much. It is also needed: the flat prior recovers only 46-60% of the true count.
3. **Practical point:** anyone applying ALE at scale must check for silent ALEobserve failures. Moody et al.'s handling of very large families should be checked; we have not checked it.
4. **The 35-fold flat-vs-fitted gap in Moody's data is not reproduced here** (about 1.6-fold). The flat prior spreads over 2N−1 branches: 1,399 in Moody, 79-319 here. So the gap is expected to grow with tree size and cannot be compared directly.
5. **Not tested:** gene-tree error (K3), realistic family richness, replicates.
