# One fitted parameter sets the size of LUCA's reconstructed genome

**Draft preprint, 2026-11-21; corrected and extended with K3-K5, 2026-11-23. Not submitted.** Open Origins project. All code, data, pre-registrations and their SHA-256 hashes are in this repository (`docs/prereg/`, `experiments/luca_calib/`).

## Abstract
Moody et al. (2024) estimated that the last universal common ancestor (LUCA) carried about 2,600 proteins. They got there by summing, over KEGG families, the posterior probability that each family was present at the root of a 700-genome tree. Those probabilities come from ALE reconciliations reweighted by a root-origination weight fitted by maximum likelihood (Coleman et al. 2021). We inverted Moody et al.'s deposited per-family probabilities to recover each family's flat-prior root odds, then recomputed the sum under alternative root weights. With their fitted weights, the sum is 1,290.6 expected families across the 7,456 families scored, reproducing their deposited total. Under ALE's default uniform root prior (w = 1), the same reconciliations give 33.9. One global weight (w ≈ 290) gives 1,270. Relaxing the per-category bounds gives 1,286. So about 97% of the summed LUCA size depends on one estimated quantity. The data support that weight strongly (ΔlogL = 1,169 against w = 1), so this is not a prior artefact. It does, however, move the open question to whether the maximum-likelihood root weight is calibrated. In pre-registered known-truth simulations (Zombi; ALE with the fitted weight), the sum recovered the planted root set to within 0.91-1.10 of the true count with true gene trees. With gene trees inferred from simulated sequences, the mean over three seeds was 1.01 (0.96-1.04). The flat prior recovered only 46-72%. The root posteriors are well calibrated in these worlds (expected calibration error 0.01-0.03): the total is right although 10-18% of the PP mass sits on non-root families. At 160 genomes per domain R was 1.10. A second pre-registered test (K5) asked whether the method can tell a big root genome from a small one plus intense early inter-domain transfer. It could not: a world with a 20-family root, padded with stem-born families that crossed between domains 4-7 times each, scored as large as a 190-family root (2 seeds, loosely matched). This requires stem transfer far above background (more than 100×), and with ordinary transfer the small world could not be made to resemble the big one. These simulations lean on the fitted weight far less than the real data do (prior multiplier 1.5-1.9× against 38×), so they do not validate the 2,600-protein estimate. An apparent failure at our largest pre-registered cell (0.75) was a numerical overflow specific to the macOS arm64 build of ALE. The same reconciliations on a Linux x86-64 build give 1.087.

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

### 2.3 Inferred gene trees (K3)
Same simulator settings at 80 genomes per domain, transfer 0.4, seeds 1-3, plus a 40-genome cell. Gene trees were inferred with IQ-TREE 3 (LG+G4, 1,000 UFBoot) from sequences simulated along each true gene tree, then reconciled with ALE (Linux x86-64 build) and reweighted as above. Decision (amendment v5c): mean over seeds of R* (Σ PP over families completed in both arms / root families among them) with inferred trees; above 1.25 "inflates", below 0.8 "deflates". Calibration measures (reliability bins, ECE, call-level false share and recall) were added in v5e before any of them was read.

### 2.4 More genomes (K4)
Seed 1 at 160 genomes per domain, true gene trees (amendments v5d, v5e). A cell is inconclusive if fewer than 90% of families complete, or if failed families are more than 1.5× enriched for root families.

### 2.5 Big root or early stem transfer? (K5)
Pre-registration v6 (sha256 d8a0a7b3…). For each K3 seed we built a small world on the same species tree: 20 of the true root families, all non-root families, and N families born on the two domain stems (between the root and each domain's crown) by our own per-family simulator using Zombi's rules (`k5/stemsim.py`). On the stems, each stem-born family also transfers into the other domain's clade at λ times a rate set from the stem length. N was tuned blind to PP so that phyletic summaries (rows 1-2: broad families and families entering ALE) match the big world. Readouts: H = Σ PP(small) / Σ PP(big), and the excess over a control world with N = 0. Decision: mean H ≥ 0.5 at the top matched λ means "cannot discriminate" (qualified as "loosely matched" unless every row matches). An ALE positive control (stemsim root-born families replacing Zombi's) had to give R in 0.95-1.15.

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


### 3.3 Inferred gene trees (K3): survives

| Seed | R*_true | R*_inf | Q = R*_inf / R*_true | Flat-prior R (inferred) | Prior multiplier (inferred) | False share at PP ≥ 0.5 (inferred) | Recall at PP ≥ 0.5 (inferred) | ECE (inferred) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.099 | 1.044 | 0.95 | 0.617 | 1.67 | 0.085 | 0.910 | 0.011 |
| 2 | 1.042 | 0.956 | 0.92 | 0.509 | 1.86 | 0.045 | 0.876 | 0.009 |
| 3 | 1.113 | 1.027 | 0.92 | 0.526 | 1.87 | 0.150 | 0.823 | 0.031 |
| 1, 40 genomes/domain | 1.047 | 1.036 | 0.99 | 0.569 | 1.79 | 0.094 | 0.906 | 0.030 |

Mean R*_inf over seeds 1-3 is 1.009, so the pre-registered verdict is "survives". Inferred trees lower the estimate by 5-8% at 80 genomes per domain, mostly through missed root mass. ALE completed every family. In probability mass, 10-18% of the true root count sits on non-root families and 7-19% is missed. The posteriors are calibrated (ECE 0.01-0.03), so the right total is not luck: it is what a calibrated posterior gives.

### 3.4 More genomes (K4): R = 1.10, formally inconclusive
At 160 genomes per domain R = 1.100 (flat prior 0.763; fitted O_R 4.66; ECE 0.014). ALE failed on 1 of 1,411 families, the largest in the sample (1,853 genes, a true root family), so by the sealed completion clause the cell is inconclusive; counting that family as PP 1 gives 1.105. The 50 largest families in the sample are all root families, so failures that track family size fall on the root. The 320-genome cell was lost to a cloud-machine reclaim and is not reported.

### 3.5 Big root or early stem transfer? (K5): cannot discriminate, loosely matched

| World (true root) | Σ PP | H vs big world | Fitted O_R | ECE |
|---|---:|---:|---:|---:|
| Big, seeds 1 / 3 (189 / 184) | 205.5 / 183.0 | 1 | 4.59 / 4.40 | 0.021 / 0.012 |
| Control, N = 0 (20) | 25.8 / 24.3 | 0.13 / 0.13 | 2.50 / 2.39 | 0.010 / 0.008 |
| Small, λ = 4 (20) | 208.9 / 228.8 | 1.02 / 1.25 | 4.57 / 4.60 | 0.21 / 0.22 |

The positive control passed (R = 1.075). Without stem traffic the pipeline separates the worlds (H 0.13). With it, stem-born families get root PPs like true root families, the fitted root weight returns to the big-world value, and calibration fails. Even under the flat prior, H is 0.58 and 0.80 (controls 0.11-0.13), so most of the effect comes from the reconciliations and the fitted weight adds the rest. The match was loose: one domain's genomes were about 26% too large on both seeds. At λ = 0 (ordinary transfer) the small world could not be matched at all. The stem transfer needed is 115-600× background.

## 4. Discussion
- **Pre-registered verdict, as scored on the laptop:** R = 0.751 at the decision cell, outside 0.8-1.25, so "dead before the grid".
- **Why that verdict is superseded:** the shortfall came entirely from ALE crashing on large families (57 of 57 were true root families). We traced the crash to the macOS arm64 build (DEVIATIONS 12). On Linux the same cell gives R = 1.087, inside the band. The laptop verdict reflects a platform-specific numerical limit, not a bias in the reweighting.
- **What this means for LUCA:** in these simulations Moody et al.'s reweighting is calibrated and needed, with true gene trees, with inferred gene trees (K3) and at twice the tree size (K4). Critiques of their LUCA size (e.g. Csűrös 2026) would have to rest on model misfit or on a history these simulations do not contain, not on the root-weight step as such.
- **Where it can be fooled (K5):** gene trees cannot separate "present at the root" from "born just after the root and moved early between the domains". If early inter-domain exchange was extremely intense, the method would report a large LUCA either way. Whether it was that intense is not shown here; a realism bound against the transfer rates implied by Moody et al.'s own reconciliations is the next test.
- **Practical warning (narrowed):** builds of ALE on platforms where `long double` is 64-bit (e.g. macOS arm64) overflow on very large families, and those families are disproportionately ancient. A pipeline that silently drops or zeroes them undercounts the root genome. Moody et al. ran on Linux clusters, where this does not occur.

## 5. Limits
- Simulated genomes are smaller (200 root families) and have fewer rare families than real ones (origination 40 instead of the 512 needed to match Moody et al.'s genome-to-pan-genome ratio, on laptop time limits).
- Prior multiplier: 1.5-1.9× in our simulations against about 38× in the real data. The real analysis leans much harder on the fitted weight than any world we simulated.
- One model class: ALE's model and Zombi's simulator are closely matched. K5 used our own stem simulator, checked by planted tests and a positive control.
- Few replicates: K3 three seeds, K4 and K5 one and two. Simulations are not bit-reproducible across machines (DEVIATIONS 17); the verdicts use paired arms from the same world.
- Full results: `K3_RESULTS.md`, `K4_RESULTS.md`, `K5_RESULTS.md` in `experiments/luca_calib/`.
- The decomposition assumes the deposited consensus files hold the root posterior under the category weights, as the scripts imply. We could not access the `.uml_rec` files.

## Data and code
`experiments/luca_calib/` (pipeline manifest sha256 c555e9a4…), `docs/prereg/HASHES.txt`, `experiments/luca_calib/DEVIATIONS.md`.
