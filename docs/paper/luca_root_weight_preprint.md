# The LUCA gene count of Moody et al. (2024) depends almost entirely on one fitted weight

**Draft preprint, 2026-11-23. Not submitted.** Markdown copy; the source of truth is the LaTeX in `luca_root_weight/` (`main.tex`, `main.pdf`). Open Origins, an independent open-science project. All code, data, pre-registrations and their SHA-256 hashes are public (see Data and code). **This copy predates the real-data checks added on 2026-11-23 (Sections 2.3–2.4 and Figures 1–3 of the PDF); read `main.pdf`.**

## Abstract
Moody et al. (2024) estimated that the last universal common ancestor (LUCA) had about 2,600 genes. Their estimate adds up, over 7,467 gene families, the probability that each family was present in LUCA. These probabilities come from gene-tree reconciliations, scaled by a root weight fitted to the data.

We show that this weight sets almost the whole count. From Moody et al.'s deposited results we recovered each family's probability without the weight.
- With the fitted weight, the expected count is 1,291 families.
- Without it, the same reconciliations give 34.
- That is a factor of 38.

The data favour the fitted weight strongly, by about 1,100 log-likelihood units, and its 95% interval moves the count only between 1,238 and 1,347. So the estimate is precise. Whether it is accurate depends on whether the fitted weight is right, and the likelihood cannot tell us that.

We therefore tested the method on simulated genomes where the ancestor is known, under rules fixed in advance.
- The first test failed. We traced the failure to a numerical bug in one build of the reconciliation software.
- With a correct build, the method recovered the planted ancestor within the pre-registered band, using both true and inferred gene trees (0.96 to 1.11 of the true count).
- But in these simulations the weight multiplied the count by only 1.4 to 1.9, far from the 38 it applies to the real data.
- In a simulated world with a small ancestor and intense early gene exchange between the two domains of life, the method reported an ancestor as large as a big one.

These tests neither validate nor refute the 2,600-gene estimate. The deciding test is a simulation in the regime of the real data, where the weight has to do most of the work.

## 1. Introduction
**The question.** How many genes did LUCA have? Moody et al. (2024) estimated about 2,600 protein-coding genes. That is comparable to many modern prokaryotes, and it implies a complex ancestor.

**How the estimate is built.** It takes three steps:
1. For each of 7,467 KEGG gene families, reconcile the family's gene trees with a 700-genome species tree using ALE (Szöllősi et al. 2013). This gives the posterior probability (PP) that the family was present at the root.
2. Add up the PPs. The sum, about 1,300, is the expected number of families in LUCA.
3. Convert this family count into a protein count by regression on modern genomes, giving about 2,600.

**The weight.** ALE's default prior treats the root like any other branch when a family first appears. Coleman et al. (2021) introduced a weight, w, that makes a family more or less likely to have originated at the root. Moody et al. fitted w by maximum likelihood, separately for each functional category of genes. A larger w raises every family's PP of being in LUCA.

**Why this could matter.** Maximum likelihood finds the weight that fits the data best under ALE's model. If the model fits real gene families poorly, the best-fitting weight can still be wrong. A wrong weight would carry straight into the count. Others have pointed at this sensitivity:
- Csűrös (2026) states that Moody et al.'s reconciliations result in "a last universal common ancestor (LUCA) with only 45 genes" (his SI Fig. S41). His main text does not give the derivation, and we have not read his SI.
- Szöllősi et al. (2026) report that, for an archaeal root, not optimising the root weight "greatly reduced" the number of root families.

Neither paper measures how much of Moody et al.'s count the weight carries. Neither tests whether the fitted weight recovers a known ancestor.

**What we did.** We made two contributions:
1. An exact decomposition of Moody et al.'s count into the evidence from the reconciliations and the contribution of the fitted weight (Section 2.1).
2. Pre-registered tests on simulated genomes with a known ancestor, asking whether the fitted weight recovers it (Sections 2.3-2.5).

We did not recompute the final 2,600-protein figure. It follows from the family count by Moody et al.'s regression.

## 2. Results
### 2.1 The fitted weight multiplies the count 38-fold
For a family whose reconciliation gives root odds r under the default prior, the weight changes the probability to PP(w) = w·r / (w·r + 1). We inverted this formula on Moody et al.'s deposited PPs to recover r for each family. We then recomputed the count under other weights (Table 1).

**Table 1.** Expected number of LUCA families under different root weights (median over Moody et al.'s five runs).

| Root weight | Expected count (Σ PP) | Families with PP ≥ 0.75 | Families with PP ≥ 0.5 |
|---|---:|---:|---:|
| Moody et al.'s fitted weights (recomputed) | 1,290.6 | 684 | 1,118 |
| The same, with the fitting bounds relaxed | 1,286.2 | 682 | 1,116 |
| One weight for all families (w ≈ 290) | 1,270.0 | 612 | 1,050 |
| Default prior (w = 1) | 33.9 | 1 | 2 |

- Our recomputation reproduces Moody et al.'s total.
- Without the weight, the count falls from 1,291 to 34, and only one family reaches PP ≥ 0.75.
- A single shared weight gives nearly the same count as the per-category weights. The result does not depend on how the categories were split.

### 2.2 The data pin the weight down tightly
The count is not an artefact of an arbitrary choice.
- The data reject the default prior. In run 1, the log-likelihood rises by 1,169 units from w = 1 to the best-fitting weight (7,028 one-category families). Across the five runs the gain is 1,089-1,166 units.
- The 95% likelihood interval for the shared weight is narrow (log w of 5.58-5.77 in every run). Across that interval the count stays between 1,238 and 1,347.

So the estimate is precise. Precision is not accuracy. The likelihood shows which weight fits best under ALE's model. It cannot show whether that weight recovers the true ancestor. Only a test with a known answer can.

### 2.3 In simulations, the method recovers a known ancestor
We simulated genome evolution with Zombi (Davín et al. 2020), starting from an ancestor of 200 gene families. We then ran Moody et al.'s pipeline: ALE reconciliation, then a fitted root weight. We score each run by R, the expected count divided by the true number of ancestral families still present in the sampled genomes. R = 1 is perfect. The pre-registered pass band was 0.8 to 1.25.

**The first test failed.** At the pre-registered decision setting (80 genomes per domain, transfer rate 0.4), R was 0.751 (Table 2).
- ALE had crashed on 57 families, and every one of them was a true ancestral family.
- The cause was the ALE build for Apple-silicon Macs. Its 64-bit long double makes a gamma function overflow on very large families.
- The Linux build completed every family, and agreed with the Mac build to within 3 × 10⁻¹⁸ wherever both finished.
- Re-run on Linux, the same setting gave R = 1.087.

We report the failure as the pre-registered verdict and the Linux result as a correction made afterwards.

**Table 2.** Recovery of a planted ancestor with true gene trees. Rows 1-6 are the pre-registered Mac runs. The last row is the decision setting re-run on Linux.

| Genomes per domain | Transfer rate | True ancestral families | R | R without crashed families | Families ALE crashed on |
|---|---|---:|---:|---:|---:|
| 20 | 0.2 | 171 | 0.912 | 0.912 | 0 |
| 20 | 0.4 | 179 | 0.986 | 0.998 | 2 |
| 40 | 0.2 | 179 | 0.957 | 0.979 | 4 |
| 40 | 0.4 | 180 | 0.937 | 1.023 | 15 |
| 80 | 0.2 | 179 | 0.816 | 1.007 | 34 |
| **80** | **0.4** | **189** | **0.751** | 1.075 | 57 |
| 80, Linux | 0.4 | 189 | 1.087 | 1.087 | 0 |

**The method also passed with inferred gene trees.** Real gene trees are inferred from sequences and contain errors. We simulated protein alignments of 157 sites along each true gene tree, inferred the trees with IQ-TREE 3, and ran the same pipeline (Table 3). The mean R over three random seeds was 1.01 (range 0.96-1.04), so the pre-registered verdict was that the estimate "survives" gene-tree error.

**Table 3.** Recovery with true and with inferred gene trees, 80 genomes per domain unless stated.

| Seed | R, true trees | R, inferred trees | Multiplier from the weight (inferred) |
|---|---:|---:|---:|
| 1 | 1.099 | 1.044 | 1.67 |
| 2 | 1.042 | 0.956 | 1.86 |
| 3 | 1.113 | 1.027 | 1.87 |
| 1, 40 genomes per domain | 1.047 | 1.036 | 1.79 |

The right total partly comes from errors that cancel.
- Probability placed on families that were not ancestral was 10-17% of the true count.
- Probability missing from families that were ancestral was 11-19%.
- Individual probabilities are only roughly calibrated. Among families given PP above 0.8, between 88% and 97% were truly ancestral. Mid-range probabilities missed in both directions, depending on the seed.

**More genomes gave a similar answer.** With 160 genomes per domain and true gene trees (one seed), R was 1.100. ALE failed on one family, the largest in the sample and a true ancestral one, so under our rules this run is formally inconclusive. A run with 320 genomes per domain was lost to a cloud-machine shutdown.

### 2.4 The simulations are an easier case than the real data
In every simulation, the evidence from the reconciliations alone already did most of the work.
- **In the simulations:** without the weight, the count was 46-76% of the true ancestor. The weight then multiplied it by only 1.4 to 1.9.
- **In the real data:** without the weight, the count is 2.6% of Moody et al.'s fitted count. The weight multiplies it by 38.

So our tests show the fitted weight working when it makes a small correction, in simulations closely matched to ALE's model. They say nothing about a 38-fold correction. The real gene families behave differently under ALE's model from our simulated ones. That is consistent with the model misfit Csűrös (2026) argues for, but our tests do not examine it.

### 2.5 A small ancestor plus intense early gene exchange looks like a large one
A family that crossed between the two domains just after LUCA has the same gene-tree shape as one inherited from LUCA. We asked how large this confusion could be. For seeds 1 and 3 we built a "small" world:
- an ancestor of only 20 families;
- plus 225 (seed 1) or 275 (seed 3) families born on the two stem lineages just after the root, which then crossed between the domains 4.0-6.9 times each;
- tuned so that the sampled genomes looked like those of the big world.

The method could not tell the two worlds apart (Table 4). The small world scored 1.02 and 1.25 times the big world's count. Without the stem families, the 20-family control scored only 0.13. The pipeline also recovered a planted ancestor generated by our own stem simulator (R = 1.075), so this simulator does not explain the result.

**Table 4.** Expected count in big and small worlds (seeds 1 / 3).

| World (true ancestral families) | Expected count | Ratio to the big world |
|---|---:|---:|
| Big (189 / 184) | 205.5 / 183.0 | 1 |
| Control: small ancestor, no stem families (20) | 25.8 / 24.3 | 0.13 / 0.13 |
| Small ancestor plus stem families (20) | 208.9 / 228.8 | 1.02 / 1.25 |

Most of the confusion comes from the reconciliations, not the weight. Even without the weight, the small world scored 0.58 and 0.80 of the big world, against 0.11-0.13 for the controls.

This result has three limits:
- **An extreme adversary.** Stem transfer was 115-600 times the background rate, with a burst of new families on the stems 28-80 times background.
- **A loose match.** One domain's genomes came out about 26% too large.
- **A point for Moody et al.** With ordinary transfer rates, no small world could be made to look like the big one at all.

The result shows what the method cannot distinguish if early exchange was that intense. It does not show that early exchange was that intense.

## 3. Discussion
**The count is a fitted weight times weak evidence.** Moody et al.'s family count is, to a close approximation, the product of the reconciliation evidence (34 families) and a fitted weight (×38). The data support the weight strongly. The open question is whether it is accurate.

**Our tests check self-consistency, not the real estimate.** In simulations, the fitted weight recovers a known ancestor with true and with inferred gene trees. But there it makes a correction of under 2-fold, not 38-fold. Our tests therefore neither validate nor refute the 2,600-gene estimate.

**The method has a blind spot.** Gene trees cannot separate "present in LUCA" from "born just after LUCA and exchanged early between the domains". If early exchange was intense, the method would report a large LUCA either way.

**A practical warning for ALE users.** ALE builds with a 64-bit long double, such as those for Apple-silicon Macs, fail on very large gene families. Those families are disproportionately ancient. A pipeline that drops them silently will undercount the ancestor. We saw no failures on Linux x86-64, which Moody et al. used.

**Two tests would settle more.**
1. A simulation in the regime of the real data, where the evidence alone gives only a few percent of the fitted count. This needs more genomes, many more rare families and realistic alignment lengths. If the fitted weight still recovers the ancestor there, that supports Moody et al.; if it does not, it undermines the estimate.
2. A bound on how intense early exchange would need to be, compared with the inter-domain transfer that Moody et al.'s own reconciliations imply.

## 4. Limits
- **Smaller genomes.** Our simulated genomes have 200 ancestral families and fewer rare families than real ones, because of compute limits.
- **One model class.** ALE's model and Zombi's simulator are closely matched. Real gene families may fit ALE's model less well.
- **Few replicates.** Three seeds for inferred trees, one for 160 genomes, two for the small-ancestor test. Simulations are not bit-reproducible across machines, so each comparison uses paired runs from the same simulated world.
- **Untested input.** The decomposition assumes the deposited summary files hold the root probabilities under the fitted weights, as Moody et al.'s scripts imply. We could not access the raw reconciliation files.

## 5. Methods
### 5.1 Decomposition
Moody et al.'s reweighting changes only the root prior, by w = exp(O_R). For families assigned to one functional category, r = PP / ((1 − PP)·w). For families in two categories, where the deposited PP is the mean over both weights, we solved for r by bisection. Families in three or more categories were skipped. We used the five deposited runs (`kegg{1-5}_cons.txt`, `KEGG{1-5}_OR.csv`, figshare 24428659), took the median over runs for each family, and summed. A planted check on synthetic files recovered both sums to 12 significant figures. The likelihood interval was computed with the same likelihood as Moody et al.'s fitting script. Code: `experiments/luca_calib/k1_prior.py`. Pre-registration: `docs/prereg/luca_calibration_v5.md` (sha256 95682ad2…), sealed before the analysis.

### 5.2 Simulations with true gene trees
Zombi simulated a species tree, then genome evolution along the complete tree, including extinct lineages. Settings:
- an ancestor of 200 families;
- duplication 0.2, transfer 0.2 or 0.4, loss 1.0, origination 40, with lognormal rates per family (σ = 0.5);
- 20, 40 or 80 sampled genomes per domain.

Each family's true gene tree was reconciled with ALE against the sampled species tree. Moody et al.'s root reweighting then followed, with one global O_R in [1, 20]. Pre-registered decision (amendment v5b, sha256 b37a26d7…): R outside 0.8-1.25 at 80 genomes per domain and transfer 0.4 means the estimator is biased even without gene-tree error. All amendments before the decision were made on timing or crash logs, before any score was read.

### 5.3 Simulations with inferred gene trees
The settings were the same, at 80 genomes per domain and transfer 0.4, for seeds 1-3, plus one run at 40 genomes per domain.
- **Sequences:** protein alignments of 157 sites simulated under WAG, with root-to-tip length 2.0 (not fitted to Moody et al.'s alignments).
- **Tree inference:** IQ-TREE 3 under LG+G4, with 1,000 ultrafast bootstraps.
- **Reconciliation:** ALE (Linux x86-64 build), reweighted as above.

Decision (amendment v5c): take the mean R over seeds with inferred trees, counting only families completed with both true and inferred trees. Above 1.25 means "inflates" and below 0.8 means "deflates". The calibration measures were added (amendment v5e) before any of them was read.

### 5.4 More genomes
Seed 1 at 160 genomes per domain, true gene trees (amendments v5d, v5e). A run is inconclusive if fewer than 90% of families complete, or if failed families are more than 1.5 times enriched for ancestral families.

### 5.5 Small ancestor with early exchange
Pre-registration v6 (sha256 d8a0a7b3…). For each seed we built a small world on the same species tree from three parts:
- 20 of the true ancestral families;
- all the non-ancestral families;
- N families born on the two stems between the root and each domain's crown.

Stem families came from our own simulator using Zombi's rules (`k5/stemsim.py`). On the stems, each also transferred into the other domain at λ times a rate set from the stem length. N was tuned, blind to PP, so that summaries of the sampled genomes matched the big world. The readout is H, the small world's expected count divided by the big world's. Decision: mean H ≥ 0.5 at the highest matched λ means "cannot discriminate", qualified as "loosely matched" unless every summary matched. A positive control, in which the stem simulator generated the ancestral families, had to give R between 0.95 and 1.15.

## Data and code
Repository: https://github.com/HarshInvader/open-origins
- Pipeline: `experiments/luca_calib/` (manifest sha256 c555e9a4…)
- Full results: `K3_RESULTS.md`, `K4_RESULTS.md`, `K5_RESULTS.md` in `experiments/luca_calib/`
- Pre-registrations and hashes: `docs/prereg/`, `docs/prereg/HASHES.txt`
- Deviations from the pre-registrations: `experiments/luca_calib/DEVIATIONS.md`

## References
- Coleman GA, Davín AA, Mahendrarajah TA, et al. (2021). A rooted phylogeny resolves early bacterial evolution. *Science* 372:eabe0511. doi:10.1126/science.abe0511
- Csűrös M (2026). Reconstructing ancient genomes from gene counts: a robust likelihood framework with sampling bias correction. *PNAS* 123(19):e2537812123. doi:10.1073/pnas.2537812123
- Davín AA, Tricou T, Tannier E, de Vienne DM, Szöllősi GJ (2020). Zombi: a phylogenetic simulator of trees, genomes and sequences that accounts for dead linages. *Bioinformatics* 36:1286. doi:10.1093/bioinformatics/btz710
- Moody ERR, Álvarez-Carretero S, Mahendrarajah TA, et al. (2024). The nature of the last universal common ancestor and its impact on the early Earth system. *Nature Ecology & Evolution* 8:1654-1666. doi:10.1038/s41559-024-02461-1
- Szöllősi GJ, Rosikiewicz W, Boussau B, Tannier E, Daubin V (2013). Efficient exploration of the space of reconciled gene trees. *Systematic Biology* 62:901-912. doi:10.1093/sysbio/syt054
- Szöllősi GJ, Spang A, Boussau B, Williams TA (2026). Improved ancestral genome reconstruction using a learned gene-content grammar. bioRxiv. doi:10.64898/2026.09.03.749268
