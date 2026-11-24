# T8 result: across all additions, the growth-versus-variation trade-off in Ameta 2021 does not exceed droplet noise

Prereg: `docs/prereg/t8_ameta_noise.md`, sealed in d479750 (`HASHES.txt`). Script: `scripts/t8_analysis.py` (sha256 18ffe6a2…). Output: `scripts_out/t8_real.json`.

## Claim

Ameta et al. 2021, Nat Commun, doi:10.1038/s41467-021-21000-1, study autocatalytic networks of *Azoarcus* ribozyme fragments in droplets. They write: "high-yield networks tend to display small perturbation values, implying a trade-off between growth and variation". They base this on a Fisher test over 162 network pairs (odds ratio < 0.1, p = 1.6 × 10⁻³).

Perturbation is measured on species fractions. Yield is counted from the same droplets' molecules (UMIs). A low-yield droplet has fewer counts, so its fractions are noisier, and noise alone reads as perturbation. The test asks whether the trade-off survives an adjustment for each network's own split-half noise.

## Gate (passed before the seal)

Reproduced from the authors' notebook definition: table [[1, 52], [20, 89]], odds ratio 0.086, 95% CI 0.011–0.656, one-sided p = 1.62 × 10⁻³. This matches the paper exactly.

## Sealed verdict: kill

Correlations are Spearman, taken within strata of network size. The data are all single-species additions with at least 5 droplets on both sides: 1,093 pairs from 386 base networks. The interval comes from a bootstrap over base networks.

| | Correlation (95% interval) |
|---|---|
| Yield vs perturbation (raw) | −0.114 (−0.192, −0.037) |
| Yield vs split-half noise, no species added | **−0.154** (−0.273, −0.031) |
| Yield vs perturbation, given noise (K-b, primary) | **−0.057** (−0.121, 0.010) |

The kill rule had two arms, and both hold:
1. The K-b upper bound is ≥ 0.
2. The yield–noise correlation is at least as negative as the yield–perturbation correlation.

High-yield networks vary less when a species is added. They vary just as much less when **nothing** is added and their own droplets are split in two. The planted check showed that noise alone produces a raw correlation of −0.11 to −0.22, and the real raw value, −0.114, sits inside that range.

## Reported only (no rule)

- **The two-sided noise floor in place of split-half** gives "partly". The partial correlation is −0.071 (−0.136, −0.005), excluding 0 but far from the −0.20 support line. In planted no-change nulls this measure said "partly" up to 9% of the time, which is why it was not the primary.
- **At least 3 droplets per side (1,621 pairs):** kill under split-half, partly under the floor. **At least 10 per side (547 pairs):** mostly partly, with excess correlation −0.10 (−0.20, −0.01).
- **By size:** the raw trade-off is clearest in 2-species networks (−0.32, n = 131). It is near zero at 4–6 species. It is negative again in the small samples at 9–13 species.
- **The paper's own subset.** 41 of the 162 Fig. 2d pairs have at least 5 droplets on both sides. In these 41 the raw correlation is −0.69 and the excess over noise is −0.65. That is strong, but it rests on a small, hand-selected subset: G and C IGS additions with one target, 3–5 species. It has no interval and no stratification. It may hold a real, specific effect, or reflect how the subset was chosen. This study cannot tell which.
- Without size strata, every rule gives kill. The pooled correlation is positive (+0.32), because yield, perturbation and noise all change with size.
- 27% of real pairs have a perturbation below their own noise floor. The median perturbation is 0.135 against a median floor of 0.087.

## Reading

- As a general claim about these networks ("high-yield networks tend to display small perturbation values"), the trade-off is not shown. Across 1,093 additions it is no larger than the yield-dependence of plain droplet noise.
- At best a weak residual remains, about −0.06 to −0.10. The sealed test has limited power there: a planted −0.08 is killed 42% of the time. A kill means no trade-off of about −0.15 or stronger beyond noise.
- The strong effect the paper reports may be specific to the subset it chose. Testing that needs more droplets per network in that subset (raw data on figshare, doi:10.6084/m9.figshare.c.5103962, not opened).

## What it means for us

- For the "networks before replicators" route, this removes one empirical leg: evidence that autocatalytic RNA networks already trade growth against variability. The effect may still be real in specific architectures, but the deposited data cannot show it in general.
- It is a small, clean, fully deposited reanalysis, and the authors' own code matches our definitions. It is a candidate for a friendly note to the authors. The owner decides.
