# K3 results: does the LUCA estimate survive gene-tree error? (prereg v5c, measures from v5e)

**Status, 2026-11-23 06:50 UTC: partial.** Seed 1 is complete in both arms. Seeds 2 and 3 have finished the true-tree arm; their inferred-tree arms are running on AWS. The sealed verdict is the mean R*_inf over the three seeds and will be filled in when they finish. Numbers come from `k3/k3_report.py` (output: `results/k3/k3_report.json`).

## Setup
- **Simulation:** Zombi, 80 genomes per domain, transfer 0.4, origination 40, 200 initial families, seeds 1-3.
- **Arms:**
  - true gene trees;
  - gene trees inferred from simulated sequences (IQ-TREE 3.1.4 for Linux x86-64; see `infer_trees.py`).
- **Pipeline:** ALE undated (Linux x86-64 build; see DEVIATIONS 12), then Moody et al.'s global O_R refit.
- **Extra cell:** n40 is seed 1 at 40 genomes per domain.
- **Sealed rule (v5c):** take the mean R*_inf over seeds. Above 1.25 means "inflates", below 0.8 means "deflates", otherwise "survives". R* is ΣPP over families that ALE completed in both arms, divided by the root families among them.

## Results so far

| Cell | Arm | R | R* | R flat prior | Prior multiplier | Fitted O_R | False mass / true | Missed mass / true | ECE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| s1 | true | 1.087 | 1.099 | 0.716 | 1.52 | 4.59 | 0.154 | 0.067 | 0.021 |
| s1 | inferred | 1.033 | **1.044** | 0.617 | 1.67 | 4.54 | 0.145 | 0.112 | 0.011 |
| s2 | true | 1.058 | (pending) | 0.660 | 1.60 | 4.44 | 0.154 | 0.096 | 0.015 |
| s3 | true | 0.995 | (pending) | 0.654 | 1.52 | 4.40 | 0.111 | 0.117 | 0.012 |
| n40 | true | 1.029 | 1.047 | 0.660 | 1.56 | 4.40 | 0.128 | 0.099 | 0.033 |
| n40 | inferred | 1.018 | 1.036 | 0.569 | 1.79 | 4.39 | 0.144 | 0.126 | 0.030 |

- **Q:** R*_inf / R*_true is 0.95 for s1 and 0.99 for n40.
- **Completion:** ALE completed every family in every arm, with no failures.

### Individual calls

| Cell | Arm | PP ≥ 0.5: n | False share | Recall | PP ≥ 0.75: n | False share | Recall |
|---|---|---:|---:|---:|---:|---:|---:|
| s1 | true | 197 | 0.091 | 0.947 | 181 | 0.050 | 0.910 |
| s1 | inferred | 188 | 0.085 | 0.910 | 169 | 0.047 | 0.852 |
| s2 | true | 198 | 0.111 | 0.912 | 182 | 0.066 | 0.881 |
| s3 | true | 177 | 0.073 | 0.891 | 168 | 0.060 | 0.859 |
| n40 | true | 181 | 0.077 | 0.928 | 165 | 0.024 | 0.894 |
| n40 | inferred | 180 | 0.094 | 0.906 | 158 | 0.032 | 0.850 |

**Reliability, s1 inferred.** Families in 5 PP bins, with mean PP against the share that are truly root:

| PP bin | Families | Mean PP | Share truly root |
|---|---:|---:|---:|
| 0-0.2 | 647 | 0.01 | 0.01 |
| 0.2-0.4 | 26 | 0.29 | 0.23 |
| 0.4-0.6 | 11 | 0.50 | 0.45 |
| 0.6-0.8 | 18 | 0.71 | 0.50 |
| 0.8-1.0 | 165 | 0.98 | 0.96 |

## Reading so far (not the verdict)
- **The total:** with inferred trees, seed 1 gives R*_inf = 1.044, inside 0.8-1.25.
- **Wrong families:** about 11-15% of the true root count, in probability mass, sits on families that were not at the root. Missed root families offset it (7-13%). So the total comes out right while some individual families are wrong.
- **Calibration:** the posteriors are well calibrated, with ECE 0.01-0.03. "Some PP mass on wrong families" is what a calibrated posterior should do: the 0.6-0.8 bin is the visible exception, though it holds only 18 families. Following Fable's advice (RESEARCH_STATE), this is reported as a calibration result, not as an error rate.
- **The caveat on any pass:** the prior multiplier is 1.5-1.8× in these simulations against 38× in Moody et al.'s real data (1,290.6 / 33.9, K1). The real analysis leans far harder on the fitted root weight than these simulations do. A pass means "not biased under correct specification, in this regime", not "2,600 validated".
