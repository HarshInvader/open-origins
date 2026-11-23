# Amendment v5e: K4 reporting and inconclusive zones (task #32)

Agent: orig-paper. Written 2026-11-23 after an independent Fable review (owner's "Use Fable to plan" rule), **before any K4 step had finished** (no K4 `.done` file, no score). v5d's lanes and decision thresholds are unchanged.

## Added rules
1. **Completion clause.** If, in a cell, fewer than 90% of reconcilable families complete in ALE, or the families that fail are more than 1.5× enriched for true root families relative to their share of all families, the cell is **inconclusive**, not a pass or fail. R is also reported with failed families counted as PP 0 and as PP 1.
2. **Near-boundary clause.** One seed per cell, and K3's seed-to-seed spread is about 0.08. Any R within 0.05 of 0.8 or 1.25 is **inconclusive pending a second seed**.
3. **Interpretation stated in advance.** A pass means "the reweighting is not biased within Zombi's model class at these settings". It does not validate Moody et al.'s 2,600 proteins, because ALE's model and Zombi's simulator are closely matched and the simulated regime is easy.
4. **The w80 lane (transfer 0.8)** is relabelled a **robustness check, not a worst case**. ALE models transfer and re-fits its rate, so a higher rate of a modelled process is not misspecification.

## Added measures, reported for every cell (and for K3)
- **Prior multiplier:** fitted Σ PP / flat Σ PP. Real data: 1,270 / 33.9 ≈ 37×. K3 so far: about 1.5×. A pass is only informative to the extent that the multiplier approaches the real one.
- **Reliability curve:** for each PP bin (0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1), the number of families, mean PP and the fraction truly root; plus the expected calibration error (count-weighted mean |mean PP − fraction root|). Shown for true and inferred trees.
- Fitted O_R and the root-family fraction (true root families / families in the sample) per cell.
