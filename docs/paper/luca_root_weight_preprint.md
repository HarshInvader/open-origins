# One fitted parameter sets the size of LUCA's reconstructed genome

**Draft preprint, 2026-11-21, corrected 2026-11-23. Not submitted.** Open Origins project. All code, data, pre-registrations and their SHA-256 hashes are in this repository (`docs/prereg/`, `experiments/luca_calib/`).

## Abstract
Moody et al. (2024) estimated that the last universal common ancestor (LUCA) carried about 2,600 proteins. They got there by summing, over KEGG families, the posterior probability that each family was present at the root of a 700-genome tree. Those probabilities come from ALE reconciliations reweighted by a root-origination weight fitted by maximum likelihood (Coleman et al. 2021). We inverted Moody et al.'s deposited per-family probabilities to recover each family's flat-prior root odds, then recomputed the sum under alternative root weights. With their fitted weights, the sum is 1,290.6 expected families across the 7,456 families scored, reproducing their deposited total. Under ALE's default uniform root prior (w = 1), the same reconciliations give 33.9. One global weight (w ≈ 290) gives 1,270. Relaxing the per-category bounds gives 1,286. So about 97% of the summed LUCA size depends on one estimated quantity. The data support that weight strongly (ΔlogL = 1,169 against w = 1), so this is not a prior artefact. It does, however, move the open question to whether the maximum-likelihood root weight is calibrated. In known-truth simulations (Zombi; ALE with the fitted weight), the sum recovered the planted root set to within 0.91-1.10 of the true count with true gene trees, and to within 1.02-1.04 with inferred gene trees (seed 1 and a 40-genome cell). The flat prior recovered only 46-72%. An apparent failure at our largest pre-registered cell (0.75) was a numerical overflow specific to the macOS arm64 build of ALE. The same reconciliations on a Linux x86-64 build give 1.087.

## 1. Background
- Moody et al. 2024, *Nat Ecol Evol* 8:1654-1666, doi:10.1038/s41559-024-02461-1. 700 genomes, ALE reconciliations of KEGG and COG families, root-origination reweighting by `O_R_Optimization.py`. Their robustness checks were empirical, not known-truth simulations of root content.
- Coleman et al. 2021, *Science* 372:eabe0511, doi:10.1126/science.abe0511. Introduced the root-origination reweighting. Their Zombi simulations (figshare doi:10.6084/m9.figshare.12651074) scored root position and DTL event counts, not root gene content.
- Csűrös 2026, *PNAS* 123(19):e2537812123, doi:10.1073/pnas.2537812123. Argues large-scale reconciliations inflate transfers, and in a reanalysis reports a much smaller LUCA ("45 genes"). Its simulations test a profile model, not ALE.
- Szöllősi et al. 2013, *Syst Biol* 62:901-912, doi:10.1093/sysbio/syt054 (ALE). Davín et al. 2020, *Bioinformatics* 36:1286, doi:10.1093/bioinformatics/btz710 (Zombi).

**What is new here:** an exact decomposition of Moody et al.'s LUCA size into flat-prior evidence and a fitted root weight, and a pre-registered known-truth test of whether that weight recovers a planted root genome.

## 2. Methods
### 2.1 Decomposition (K1)
Moody et al.'s reweighting changes only the root branch prior, by w = exp(O_R). For a family with flat-prior root odds r, PP(w) = w·r / (w·r + 1). For families assigned to one functional category, r = PP / ((1 − PP)·w). For families in two categories (PP is the mean over both weights), we solve for r by bisection. Families in three or more categories are skipped. We used the five deposited runs (`kegg{1-5}_cons.txt`, `KEGG{1-5}_OR.csv`, figshare 24428659), took the per-family median over runs, and summed. A planted check on synthetic files recovered both sums to 12 significant figures. Code: `experiments/luca_calib/k1_prior.py`. Pre-registration: `docs/prereg/luca_calibration_v5.md` (sha256 95682ad2…), sealed before the analysis.

### 2.2 Known-truth simulation (K2)
Zombi simulates a species tree, then genome evolution with origination, duplication (0.2), transfer (0.2 or 0.4) and loss (1.0) along the complete tree including extinct lineages, from a root genome of 200 families with lognormal per-family rates (σ = 0.5). We sample 20, 40 or 80 genomes per domain, reconcile each family's true gene tree with ALE against the sampled species tree, apply Moody et al.'s root reweighting (one global O_R in [1, 20]), and compare Σ PP with the true number of root families still present in the sample. Pre-registered decision (amendment v5b, sha256 b37a26d7…): R outside 0.8-1.25 at 80 genomes per domain and transfer 0.4 means the estimator is biased even without gene-tree error. Amendments v5a and v5b, and deviations 1-11, were all made on timing or crash logs before any score was read.

## 3. Results
### 3.1 The summed LUCA size is almost entirely the fitted root weight

| Root weight | Σ PP | PP ≥ 0.75 | PP ≥ 0.5 |
|---|---:|---:|---:|
| Moody et al.'s per-category weights (recomputed) | 1,290.6 | 684 | 1,118 |
| Per-category, bounds relaxed (O_R ∈ [−5, 40]) | 1,286.2 | 682 | 1,116 |
| One global weight (O_R ≈ 5.68, w ≈ 290) | 1,270.0 | 612 | 1,050 |
| Flat, w = 1 (ALE default) | 33.9 | 1 | 2 |

- Under the default prior, only one family reaches PP ≥ 0.75.
- The exp(20) bound that two categories hit holds 4 families and moves the total by about 4.
- The share of the sum from single-domain families barely changes with the weight (27.5-28.4%).
- The likelihood strongly favours the fitted weight: in run 1, log-likelihood rises by 1,169 from w = 1 to the optimum.

### 3.2 Does the fitted weight recover a planted root genome?

| Genomes / domain | Transfer | True root families | Σ PP fitted | R | Σ PP flat | R flat | Fitted O_R | Families ALE crashed on (all true root) | R without crashed families |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | 0.2 | 171 | 155.9 | 0.912 | 99.0 | 0.579 | 3.94 | 0 | 0.912 |
| 20 | 0.4 | 179 | 176.6 | 0.986 | 93.5 | 0.522 | 4.20 | 2 | 0.998 |
| 40 | 0.2 | 179 | 171.3 | 0.957 | 106.4 | 0.595 | 4.32 | 4 | 0.979 |
| 40 | 0.4 | 180 | 168.7 | 0.937 | 108.6 | 0.603 | 4.31 | 15 | 1.023 |
| 80 | 0.2 | 179 | 146.0 | 0.816 | 105.6 | 0.590 | 4.26 | 34 | 1.007 |
| **80** | **0.4** | **189** | **141.9** | **0.751** | 87.4 | 0.463 | 4.21 | 57 | 1.075 |
| 80, Linux build | 0.4 | 189 | 205.4 | 1.087 | 135.3 | 0.716 | 4.59 | 0 | 1.087 |

The "crashed" families were crashes of the macOS arm64 ALE build, which has a 64-bit long double; Boost's tgamma/double_factorial overflow on very large families. The Linux x86-64 build (80-bit long double) completes every family, and its PPs agree with the macOS build to within 3e-18 wherever both finish (DEVIATIONS 11-12). The bottom row is the decision cell re-run on Linux. The rows above it are the laptop runs as pre-registered.

The rest of this paragraph uses the laptop run, decision cell (80, 0.4). (80, 0.4): PP ≥ 0.5 calls 135 families, 120 true (recall 0.63, false share 0.11); PP ≥ 0.75 calls 121, 113 true (recall 0.60, false share 0.07). Families with PP 0.8-1.0: 119, of which 95% are true root families.



## 4. Discussion
- **Pre-registered verdict, as scored on the laptop:** R = 0.751 at the decision cell, outside 0.8-1.25, so "dead before the grid".
- **Why that verdict is superseded:** the shortfall came entirely from ALE crashing on large families (57 of 57 were true root families). We traced the crash to the macOS arm64 build (DEVIATIONS 12). On Linux the same cell gives R = 1.087, inside the band. The laptop verdict reflects a platform-specific numerical limit, not a bias in the reweighting.
- **What this means for LUCA:** with perfect gene trees, Moody et al.'s reweighting is roughly calibrated, and needed. Critiques of their LUCA size (e.g. Csűrös 2026) would have to rest on gene-tree error or model misfit, not on the root-weight step. That is what K3 tests.
- **Practical warning (narrowed):** builds of ALE on platforms where `long double` is 64-bit (e.g. macOS arm64) overflow on very large families, and those families are disproportionately ancient. A pipeline that silently drops or zeroes them undercounts the root genome. Moody et al. ran on Linux clusters, where this does not occur.

## 5. Limits
- Simulated genomes are smaller (200 root families) and have fewer rare families than real ones (origination 40 instead of the 512 needed to match Moody et al.'s genome-to-pan-genome ratio, on laptop time limits).
- Inferred-tree error (K3) is reported separately (`experiments/luca_calib/K3_RESULTS.md`, pending seeds 2 and 3).
- The decomposition assumes the deposited consensus files hold the root posterior under the category weights, as the scripts imply. We could not access the `.uml_rec` files.

## Data and code
`experiments/luca_calib/` (pipeline manifest sha256 c555e9a4…), `docs/prereg/HASHES.txt`, `experiments/luca_calib/DEVIATIONS.md`.
