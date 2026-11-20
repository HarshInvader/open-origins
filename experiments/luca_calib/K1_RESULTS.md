# K1: how much of Moody et al.'s LUCA size does the root prior create? (prereg v5, task #32)

Run 2026-11-20, after v5 was sealed (`95682ad2…`).
- **Code:** `k1_prior.py`.
- **Inputs:** Moody's deposited `COG_OR_reconciliation/` (figshare 24428659) and `real_features_moody.tsv`.
- **Output:** `results/k1/k1.json`. No simulation was used.

## Planted check (before real data)
On synthetic files (2,000 families, 5 category weights, 20% of families in two categories), the inversion recovered:
- the flat-prior sum: 12.141565834572 against the true 12.141565834572;
- the reweighted sum: 285.157824752312 against the true 285.157824752312.

## Result (7,456 families common to Moody's 5 runs; per-family median over runs, then summed)

| Root weight | Σ PP | PP ≥ 0.75 | PP ≥ 0.5 | Single-domain share |
|---|---:|---:|---:|---:|
| Moody's per-category weights (recomputed; equals E_M) | 1,290.6 | 684 | 1,118 | 28.4% |
| Per-category weights, bounds relaxed to O_R ∈ [−5, 40] | 1,286.2 | 682 | 1,116 | 28.4% |
| One global weight, fitted (O_R = 5.67-5.69, w ≈ 290 in all runs) | 1,270.0 | 612 | 1,050 | 28.1% |
| **Flat, w = 1 (ALE default: uniform over the 1,399 branches)** | **33.9** | **1** | **2** | 27.5% |

- No family's PP was saturated (all below 1 − 1e-12), so the bounds-interval columns in `k1.json` collapse to single values.
- **The exp(20) bound is immaterial.** Moody's categories B and W hit it, but they hold only 3 families and 1 family. Refitted without bounds, B goes to the lower bound and W to the upper one. The total moves by 4 families.

## Sealed decision and predictions
- **Decision:** S_flat = 33.9 < 0.5·E_M = 645, so the sum is **"largely prior-driven"** as defined in v5. About 97% of Moody's summed size depends on fitting a root weight greater than 1.
- **Prior-sensitivity range:** 33.9 to 1,290.6.
- **P9** (S_flat < 865): **confirmed.**
- **P10** (single-domain share of S_flat below 28.4%): **confirmed only marginally** (27.5%). The single-domain share hardly depends on the root weight.

## Red team: what this does and does not show
1. **The data strongly prefer the fitted weight.** In run 1 (7,028 one-category families), the log-likelihood rises by 1,169 from w = 1 to the fitted O_R = 5.75 (2ΔLL = 2,339). So the root weight is not an arbitrary prior. It is an empirical-Bayes estimate with overwhelming likelihood support. "LUCA's size is a prior artefact" would be a **wrong** headline.
2. **What it does show:** Moody's LUCA size depends almost entirely on one estimated quantity, the root weight, while the bounds and the per-category choice don't matter (1,270-1,291). Under ALE's default prior the same reconciliations give about 34 expected root families. That is the same order as Csűrös's "45 genes" (Fig. S41), which comes from a different calculation, so this is no confirmation of it.
3. **The open question this sharpens:** is the maximum-likelihood root weight calibrated? Gene-tree error and transfers from ghost lineages can make scattered families look like root originations. That would inflate the fitted weight, and with it every family's root PP. Only a known-truth simulation can test this, which is K2 (true trees) and K3 (inferred trees).
4. **Limits:**
   - The inversion assumes `kegg*_cons.txt` holds the `rell` root posterior under the category weights, as their scripts imply. The check confirms the arithmetic, not that assumption.
   - We did not use their `.uml_rec` files (data.bris refused connections on 2026-11-19 and 2026-11-20).
   - N = 1,399 affects only the fitted-weight rows, not S_flat.

## Next
K2 and K3 run as sealed in v5. A sharper measure follows from K1 and is reported alongside K2 and K3 as descriptive:
- the fitted global root weight in simulation, against the weight that would recover the true root count;
- whether simulated data show the same roughly 35-fold gap between flat-prior and fitted-weight sums.
