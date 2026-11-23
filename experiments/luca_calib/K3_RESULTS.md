# K3 results: does the LUCA estimate survive gene-tree error? (prereg v5c, measures from v5e)

**Sealed verdict (v5c): "survives".** With gene trees inferred from simulated sequences, mean R*_inf over seeds 1-3 is **1.009** (seeds: 1.044, 0.956, 1.027), inside 0.8-1.25.

Status: final, 2026-11-23 14:05 UTC. Numbers come from `k3/k3_report.py`; the merged output is in `results/k3/k3_report.json`. Deviations: 12-14 and 17.

## Setup
- **Simulation:** Zombi, 80 genomes per domain, transfer 0.4, origination 40, 200 initial families, seeds 1-3.
- **Arms:**
  - true gene trees;
  - gene trees inferred from simulated sequences (IQ-TREE 3, LG+G4, 1,000 UFBoot; see `infer_trees.py`).
- **Pipeline:** ALE undated (Linux x86-64 build; DEVIATIONS 12), then Moody et al.'s global O_R refit.
- **Extra cell:** n40 is seed 1 at 40 genomes per domain.
- **Sealed rule (v5c):** take the mean R*_inf over seeds. Above 1.25 means "inflates", below 0.8 means "deflates", otherwise "survives". R* is ΣPP over families that ALE completed in both arms, divided by the root families among them.
- **Runs:**
  - Seed 1 and n40 ran on the first AWS machine.
  - Three spot machines were reclaimed. Seeds 2-3 finished on the fourth (origins-k3d), with true and inferred arms from the same simulation.
  - The simulation is not bit-reproducible across machines (DEVIATIONS 17). Earlier true-tree runs of seeds 2-3 are therefore different worlds; they are listed as extra true-tree replicates and are not part of the decision.

## Results

| Cell | Arm | True root | R | R* | R flat prior | Prior multiplier | Fitted O_R | False mass / true | Missed mass / true | ECE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| s1 | true | 189 | 1.087 | 1.099 | 0.716 | 1.52 | 4.59 | 0.154 | 0.067 | 0.021 |
| s1 | inferred | | 1.033 | **1.044** | 0.617 | 1.67 | 4.54 | 0.145 | 0.112 | 0.011 |
| s2 | true | 193 | 1.031 | 1.042 | 0.687 | 1.50 | 4.39 | 0.108 | 0.077 | 0.009 |
| s2 | inferred | | 0.946 | **0.956** | 0.509 | 1.86 | 4.29 | 0.096 | 0.150 | 0.009 |
| s3 | true | 186 | 1.065 | 1.113 | 0.647 | 1.65 | 4.45 | 0.183 | 0.118 | 0.026 |
| s3 | inferred | | 0.983 | **1.027** | 0.526 | 1.87 | 4.35 | 0.170 | 0.187 | 0.031 |
| n40 | true | 180 | 1.029 | 1.047 | 0.660 | 1.56 | 4.40 | 0.128 | 0.099 | 0.033 |
| n40 | inferred | | 1.018 | 1.036 | 0.569 | 1.79 | 4.39 | 0.144 | 0.126 | 0.030 |
| s2, earlier world | true only | 193 | 1.058 | | 0.660 | 1.60 | 4.44 | 0.154 | 0.096 | 0.015 |
| s3, earlier world | true only | 184 | 0.995 | | 0.654 | 1.52 | 4.40 | 0.111 | 0.117 | 0.012 |

- **Q = R*_inf / R*_true:** 0.95 (s1), 0.92 (s2), 0.92 (s3), 0.99 (n40). Inferred gene trees lower the estimate by about 5-8% at 80 per domain, mostly by losing PP on true root families (missed mass rises).
- **Completion:** ALE completed every family in every arm, with no failures.
- **Seed 1 and n40:** these numbers carry over from the report committed at 06:35 UTC, computed by the same script. Their raw outputs are no longer on the laptop.

### Individual calls

| Cell | Arm | PP ≥ 0.5: n | False share | Recall | PP ≥ 0.75: n | False share | Recall |
|---|---|---:|---:|---:|---:|---:|---:|
| s1 | true | 197 | 0.091 | 0.947 | 181 | 0.050 | 0.910 |
| s1 | inferred | 188 | 0.085 | 0.910 | 169 | 0.047 | 0.852 |
| s2 | true | 192 | 0.047 | 0.948 | 188 | 0.043 | 0.933 |
| s2 | inferred | 177 | 0.045 | 0.876 | 165 | 0.030 | 0.829 |
| s3 | true | 197 | 0.157 | 0.892 | 185 | 0.130 | 0.866 |
| s3 | inferred | 180 | 0.150 | 0.823 | 169 | 0.130 | 0.790 |
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

Reliability bins for every cell are in `results/k3/k3_report.json`.

## Reading
- **The total survives inferred gene trees.** On all three seeds R*_inf is within 0.96-1.04, so the sealed rule's verdict is clear-cut (mean 1.009).
- **Calls are right in total, not one by one.**
  - In probability mass, 10-18% of the true root count sits on families that were not at the root, and 7-19% of the true root mass is missed. The two roughly cancel.
  - At PP ≥ 0.5, between 5% and 16% of the families called are not root families, varying by seed.
- **Calibration is rough, not exact** (corrected 2026-11-23; an earlier version called the posteriors calibrated).
  - ECE is 0.01-0.03 in every cell, but it is dominated by families with PP near 0.
  - Intermediate PPs (0.2-0.8) fall in bins of 5-26 families, and the errors go both ways. In the four inferred cells there are 75 root families where 88 were expected: over-confident in s1 and n40, under-confident in s2 and s3.
  - Above PP 0.8, 0.88-0.97 of families are truly root against a mean PP of 0.97-0.98 (worst in s3).
  - So the total is near 1 partly because errors offset, not only because each PP is right.
  - K5 shows calibration breaks badly when early inter-domain transfer is extreme (ECE about 0.21).
- **Prior art:** no checked paper tests root-presence posteriors against a known answer (RESEARCH_STATE, 2026-11-23). Szöllősi et al. 2026 assume false-negative rates of 0.5-0.9 at deep nodes. Here missed root mass is 0.07-0.19, though only in this idealized regime.

## Limits
- **The caveat on any pass.** The prior multiplier is 1.5-1.9× in these simulations, against 38× in Moody et al.'s real data (1,290.6 / 33.9, K1). The real analysis leans far harder on the fitted root weight than these simulations do. A pass means "not biased under correct specification, in this regime", not that 2,600 has been validated.
- **Correct specification.** ALE's model and Zombi's simulator are closely matched; origination is 40 rather than 512, and there are 200 initial families.
- **Not bit-reproducible.** Re-running a seed on another machine gives a different world (DEVIATIONS 17). The verdict rests on three paired worlds, and the two extra true-tree worlds agree (R 0.995-1.058).
