# K4 results: does the LUCA estimate hold as trees grow? (prereg v5d, v5e)

**Status, 2026-11-23: n160 scored; n320 and w80 not run.**

**Verdict at 160 genomes per domain: inconclusive under the v5e completion clause, with R = 1.10.**
- ALE failed on 1 of 1,411 families. That family is a true root family, so the failure is enriched for root families far beyond the clause's 1.5× limit.
- R is inside the 0.8-1.25 range however the failed family is counted: 1.100 with it counted as PP 0, 1.105 as PP 1.

Numbers come from `k3/k3_report.py` (output `results/k4/k4_report.json`). Deviations: 15 and 17.

## What ran
- **n160:** 160 genomes per domain (800 lineages), transfer 0.4, origination 40, 200 root families, seed 1. True gene trees, Linux ALE, Moody et al.'s global O_R refit.
- **n320:** simulation was still running when AWS reclaimed the spot machine (08:50 UTC). Nothing was scored. Under v5d, the scaling rule is applied at 160 and labelled as such.
- **w80 (transfer 0.8):** dropped to stay within budget (DEVIATIONS 15).

## n160, true gene trees

| Measure | Value |
|---|---:|
| True root families (all with ≥ 2 genes) | 182 |
| Families entering ALE / completed | 1,411 / 1,410 |
| ΣPP, fitted O_R | 200.1 |
| **R** | **1.100** (1.105 with the failed family as PP 1) |
| R, flat prior | 0.763 |
| Prior multiplier | 1.44 |
| Fitted O_R | 4.66 |
| False mass / true count | 0.153 |
| Missed mass / true count | 0.054 |
| Calls at PP ≥ 0.5: n, false share, recall | 193, 0.093, 0.962 |
| Calls at PP ≥ 0.75: n, false share, recall | 180, 0.044, 0.945 |
| ECE (5 bins) | 0.014 |

**Reliability:**

| PP bin | Families | Mean PP | Share truly root |
|---|---:|---:|---:|
| 0-0.2 | 1,193 | 0.006 | 0.004 |
| 0.2-0.4 | 20 | 0.29 | 0.00 |
| 0.4-0.6 | 7 | 0.50 | 0.14 |
| 0.6-0.8 | 13 | 0.69 | 0.38 |
| 0.8-1.0 | 177 | 0.985 | 0.96 |

## Reading
- **Scale doesn't change the estimate.** R is 1.10 at 160 per domain, 1.00-1.09 at 40-80 (K3, true trees), and the fitted O_R stays at about 4.4-4.7. The flat prior still undercounts (0.76), and the fitted weight still corrects it.
- **The pattern holds:** calibrated overall (ECE 0.014), with the middle bins (0.2-0.8) over-confident, as in K3.
- **Why the cell is inconclusive.** The failed family is the largest in the sample: 1,853 genes, present in all 320 genomes. Root families are the largest families: all 50 largest families in the sample, and 159 of the largest 182, are root families. So ALE failures driven by size will fall mainly on root families. This one failure moves R by only 0.005, but at 320 per domain or in real data more large families could fail, and all of them would hide root genes. The cause was not checked: ALEobserve's log was on the reclaimed machine.
- **The caveat from K3 applies.** The prior multiplier is 1.44 here against about 38 in Moody et al.'s real data. A pass would mean "not biased under correct specification in this regime", not that 2,600 has been validated.

## Not run, and why
- **n320:** lost to a spot reclaim. Re-running it would need about 3 h of simulation plus a long ALE step, and the month's AWS cap ($50; $45.42 booked) does not cover that.
- **A second n160 seed** would test whether the boundary case matters; it is not run either.
