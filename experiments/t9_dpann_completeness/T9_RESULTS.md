# T9 result: DPANN's excess gene loss is seen on deep branches too, but the sealed rule falls just short of support

Prereg: `docs/prereg/t9_dpann_completeness.md`, sealed in 8325e9e (`HASHES.txt`). Script: `scripts/t9_analysis.py` (sha256 e7b00f68…). Output: `results/t9_real.json`.

## Claim

Huang et al. 2026 (Nat Commun, doi:10.1038/s41467-026-76386-7) write that "the DPANN loss rate was inferred to be higher than that for the other clades (DPANN: 0.40-0.45, other clades: 0.26-0.27)". Many DPANN genomes are incomplete metagenome assemblies, with a CheckM 2 median of 91% against 98% for other archaea. AleRax counts a gene missing from an incomplete genome as a loss on that genome's own branch. The question is whether the excess loss is only that artefact.

The test looks at internal branches with at least 3 descendant genomes. One incomplete genome cannot create a loss on such a branch. The measure is the loss fraction, losses ÷ (losses + copies), for DPANN over other archaea. The interval comes from resampling whole clades.

## Sealed verdict: inconclusive, at the edge of support

| | |
|---|---|
| DPANN branches / other branches | 49 / 125 (12 / 7 clade blocks) |
| Mean loss fraction, DPANN / other | 0.267 / 0.195 |
| Ratio r, Euryarchaeota root (primary) | **1.37** (95% interval 1.146 to 1.63) |

Support needed r ≥ 1.3 and a lower bound above 1.15. The ratio passes, but the lower bound is 1.146, which misses by 0.004. Kill needed r < 1.15 and a lower bound ≤ 1.0, which is far from what was seen. The sealed verdict is **inconclusive**.

Most of the interval's width comes from the few-clade t quantile (2.45 with 7 non-DPANN blocks). The plain bootstrap percentile interval is 1.20 to 1.59. That interval was not the sealed rule.

## Reported only (no rule)

| Variant | Ratio (95% interval) |
|---|---|
| MHH root | 1.40 (1.17, 1.66), which would meet support |
| All internal branches (the plan's set) | 1.35 (1.16, 1.58) |
| Adjusted for the spurious-loss floor from incompleteness | 1.35 (1.15, 1.57) |
| ≥ 5 descendant genomes | 1.45 (1.13, 1.86) |
| ≥ 9 descendant genomes | 1.38 (0.84, 2.27) |
| Per unit of substitution length | 1.30 (0.86, 1.98) |
| Pooled sums | 1.39 |
| Tips only, raw | 1.27 |

- **Arm A is a positive control, and it behaved as expected.** Among non-DPANN tips, loss rises with incompleteness: slope 0.81 (0.40 to 1.09), and 0.73 with CheckM 1. Incompleteness does inflate tip losses in this pipeline.
- **The tip excess is explained by completeness.** On DPANN tips, observed losses over those predicted from completeness alone come to 1.09 (0.95 to 1.29), or 0.87 with CheckM 1.
- So the DPANN excess **on tips** looks like incompleteness, but the excess on **deep branches**, about 1.35–1.45 times, remains under every variant. Only the two variants with few clades or noisy branch lengths have intervals that reach 1.

## Reading

- The incompleteness artefact does not explain DPANN's high loss. The excess is as large on branches with 3, 5 or more descendant genomes as it is overall, where a missing gene in one genome cannot create a loss. This is evidence for the paper's biological reading, short of the bar fixed in advance.
- The sealed rule could not quite separate 1.15 from 1.37, because only 7 non-DPANN clade blocks exist. The planted check had shown this: at a true ×1.6, support came only 26% of the time.
- **Limit, stated before the seal.** Each rate class shares one loss rate between its tips and its internal branches, so incomplete tips can raise the internal losses of their class. The tip check (arm C ≈ 1.0) suggests this effect is small, but it is not ruled out.

## What it means for us

- K6 and the preprint use the same family of reconciliation models. Incompleteness clearly inflates tip losses (arm A), so per-tip loss counts from MAG-rich trees should not be read at face value. Deep-branch contrasts are more robust.
- This result does not challenge Huang 2026. It is a small, well-documented support-leaning check, and the authors might find it useful. The owner decides about any note.
