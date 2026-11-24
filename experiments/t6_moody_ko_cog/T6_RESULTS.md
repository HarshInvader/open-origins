# T6 result: merging KEGG families into COGs does not rescue LUCA families beyond re-run noise

Prereg: `docs/prereg/t6_moody_ko_vs_cog.md`, sealed in 95e2a3e (`HASHES.txt`). Script: `scripts/t6_analysis.py` (sha256 a07524fa…). Output: `results/t6_real.json`.

## Claim

Moody et al. 2024 (Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1) ran a COG-level analysis because "some widespread gene families that were likely present in LUCA are divided into multiple KO families that individually appear to be restricted to particular taxonomic groups and inferred to have arisen later". The paper gives no count of families the COG analysis rescues.

We used a natural experiment in their own deposited tables:
- **Retest group, 1,887 COGs.** Each COG has a single member KO, so its alignment is identical to that KO's. Only the trees and the reconciliation were re-run, so these COGs measure pure re-run noise.
- **Merge group, 1,201 COGs.** Each COG has two or more member KOs.

A merge COG is **eligible** if every member KO has PP < 0.5. It is **rescued** if the COG reaches 0.75.

## Sealed verdict: kill

| | |
|---|---|
| Eligible merge COGs | 433 of 1,201 |
| Rescued | **23** (5.3% of eligible; 1.9% of the merge group, against the 5% that support needs) |
| Re-run flip rate, matched on starting PP and size | 8.1% (60 flips among 1,505 eligible single-KO COGs) |
| Ratio, rescue over re-run | **0.66** (95% interval 0.40 to 1.08) |

The kill rule is a lower bound at or below 2. The whole interval sits at or below 1. A merged family reaches 0.75 no more often than a family that was just re-run, and the point estimate is lower.

## Reported only (no rule)

| Variant | Ratio (95% interval) |
|---|---|
| Plan's rule (whole groups) | 0.60 (0.37, 0.95) |
| Matched on starting PP only | 0.74 (0.46, 1.18) |
| Threshold 0.5 → 0.5 | 0.71 (0.53, 0.96) |
| Threshold 0.25 → 0.75 | 0.98 (0.47, 1.90) |
| KO side from `ML_median` | 0.86 (0.52, 1.35) |
| KO side from `MEAN_OF_MEDIANS` | 0.83 (0.51, 1.37) |
| A member KO with no PP counts as low (785 eligible) | 0.64 (0.42, 1.00) |
| Retest limited to `COG_perc` ≥ 0.9 | 0.57 (0.34, 0.97) |
| Merge COGs with exactly 2 KOs | 1.01 (0.58, 1.64) |
| Merge COGs with 3 or more KOs | 0.30 (0.11, 0.69) |

No variant reaches 2. The more KOs a COG merges, the *less* often it is rescued.

### Merging loses more LUCA families than it gains

- **Downward mirror.** Look at COGs whose best member KO is at or above 0.75. The COG falls below 0.5 in **128 of 277** merge COGs (46%), against **37 of 244** retest COGs (15%).
- **Mean change.** In the merge group, the COG's PP is on average 0.096 below its best member KO's (n = 1,196).

So merging split families does not pull LUCA families back in. It more often pushes out a family that one of its KOs had placed in LUCA. A likely cause is that a larger merged tree carries more transfers and losses for the reconciliation to explain. That cause is a reading, not a test.

### Re-run noise in Moody's pipeline (retest group, n = 1,887)

- Re-running alone changes the call at 0.5 for **11.2%** of single-KO families: 7.0% go up across 0.5 and 4.1% go down.
- 5.1% move by more than 0.5 and 14.9% by more than 0.25. The median absolute change is 0.026, and r = 0.80.
- The share with `COG_perc` ≥ 0.9 is the same, 11.9%.
- This puts a size on the paper's own note that 810 families differ by more than 0.5 between runs.

### Eligibility null (KO side only)

36.1% of real merge COGs are eligible, against 31.0% (95% range 29.1 to 33.1) when the same KOs are regrouped at random. Real COGs group low-PP KOs together slightly more than chance does.

## Gate and disclosures

- The gate, the planted check (null ratio 1.0, so both verdicts can be reached) and the permuted dry run (0.98, a kill) all passed before the seal. See the prereg.
- The form of the rule changed from the plan before the seal: rates are taken among eligible COGs, matched on PP and size, with a shared Jeffreys prior. The thresholds did not change. The planted check showed the plan's rule was miscalibrated. Under the plan's rule the verdict would also be kill (0.60).
- The KO value is a median of five runs and the COG value is one run, so the retest group slightly overstates single-run noise for the KO side. This makes the noise baseline, if anything, generous to rescue.

## What it means for us

- For K6 and the LUCA preprint, the KO-level calls are the better unit. Moody's COG table is no more inclusive. It is noisier and loses families more often than it gains them. The ~11% re-run call-flip rate is a floor for how far any single family's LUCA call can be trusted. This supports reporting LUCA content as a weighted sum rather than as a family list.
- This is a clean, fully deposited result and could be worth a short note to the authors. The owner decides.
