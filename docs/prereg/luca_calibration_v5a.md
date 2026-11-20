# Amendment v5a: making K2 and K3 runnable on the laptop (task #32)

Agent: orig-paper. Written 2026-11-20, before any K2 or K3 simulation. Only timing information has been seen: no fit point, score or genome statistic. v5 (`95682ad2…`) stays in force except as changed here.

## Timing that forces this
- One Zombi Gm run at the v3 scale (600 extant lineages, 600 root families, per-family rates) did not finish in 2 h at background priority with origination 5. It reached simulated time 1.03 of 1.17 and was slowing.
- A run at origination 100 (stage F's first bracket) did not finish in 1 h.
- So a single Gm run takes about 5 h or more. Stage F as sealed (16 points × up to 12 Gm runs) would take more than a week of laptop time.
- v5's fallback is therefore invoked now, on timing alone, rather than after 24 h. **T\* = loss 1, transfer/loss 0.2, duplication 0.2 × loss.** Stage F is not run.

## K2 design (replaces v5's K2 inputs; decision rule unchanged)
- **Scale.**
  - Sampled tips: 20, 40, 80 and 160 per domain.
  - The species tree is grown to 5 × n_per_domain extant lineages. Seeds are retried until both root subtrees hold at least n_per_domain tips, as in v3.
- **Root genome: 200 families** instead of 600.
  - Zombi evolves families independently, so per-family recovery, R and the false share are unchanged in expectation; only the noise grows.
  - Per-family rate heterogeneity stays: lognormal, σ = 0.5.
- **Transfer:** 0.2 (T\*) and 0.4 (2·T\*), with loss 1 and duplication 0.2. Seed 1.
- **Origination, fitted once (genome sizes only, no inference).**
  - `fit.py` runs a single point: L = 1, transfer/loss = 0.2, 20 tips per domain, 100 lineages, 200 root families, `--o-start 2`.
  - The target is the v2 statistic: median sampled genome / families in the sample = 0.106 ± 0.02.
  - The fitted origination rate (per genome per unit time) is used unchanged in every K2 cell and in K3.
  - The observed ratio, occupancy histogram and both-domain share in each cell are reported as descriptive fit checks, not gates.
- **Sequences.**
  - 157 sites, WAG, with v3_base's substitution scaling (root-to-tip target 2.0). The seqscale step that would fit p-distance to 0.61 is skipped for time.
  - The median p-distance of each cell is reported. K3's limits note any miss of 0.61 ± 0.05.
- **Reconciliation:** ALE on true gene trees, then Moody's reweighting with one global O_R in [1, 20]. The flat w = 1 version is reported alongside, as is the fitted root weight, compared with the weight that would make Σ PP equal the true count (from K1's "next" note).

## K3 design
- It reuses K2's 2·T\* simulation at the largest tip count whose projected IQ-TREE plus ALE time is ≤ 36 h with 3 workers, judged from K2's timings only.
- IQ-TREE LG+G4 with 1,000 UFBoot, then ALE on the inferred trees and the same reweighting.
- Pairing true and inferred trees on one simulation isolates the effect of gene-tree error.

## Unchanged
- v5's K2 decision: R at 320 tips and 2·T\* outside 0.8-1.25 with true trees means "dead before the grid".
- Measures, the order K1 → K2 → K3, and no main grid before K1-K3 are reported.

## Added limits
- T\* is not fitted to real data.
- Genomes are smaller than real ones (200 against about 1,000 root families).
- Sequence divergence is not fitted.
- K2 and K3 test the pipeline's bias at stated settings. They are not a calibration of Moody's real numbers.
