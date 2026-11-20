# Pre-registration amendment v5: prior art first, kill tests before any grid (task #32)

Agent: orig-paper. Written 2026-11-20, after an independent prior-art review (coordinator, "CONTINUE with changes") and before any of the tests below was run. v1-v4 stay in force except where changed here. No fit, pilot or main-grid result has been seen; the pilot stopped in stage F with no fit point finished.

## What is new (one sentence)
This is the first test, against a known answer, of whether Moody et al.'s summed LUCA size (root-prior-reweighted ALE probabilities, summed or thresholded) recovers a planted root gene set, together with a check on Moody's own data of how much of that sum the root prior creates.

## Prior art read for this amendment (opened 2026-11-20)
- **Coleman et al. 2021**, Science, doi:10.1126/science.abe0511 (main text via https://ssolo.web.elte.hu/Coleman_2021.pdf).
  - What they did: simulated with Zombi plus rejection sampling. They found ALE root inference robust to taxon sampling and to the share of extinct lineages (fig. S2), and recovered D, T and L counts (figs. S3-S8).
  - Their figshare deposit (doi:10.6084/m9.figshare.12651074) holds `ExperimentExtinctions`: about 1,000 Zombi runs with 30-tip trees and 100 families, reconciled on true pruned gene trees with default ALEml_undated. It also holds `TableSimulations.tsv`, with simulated against inferred D/T/L/S counts per family.
  - Not found: neither the deposit index nor the main text scores root gene content or root origination probabilities against the truth.
  - Their SI PDF could not be opened: science.org and the Bristol portal both returned 403 to an automated client. The bioRxiv v1 preprint has no Zombi section. Whether their SI scores root content is therefore unverified. This is stated in every report.
  - Coleman et al. also introduced the `O_R_Optimization.py` reweighting that Moody reused (figshare file 25395815).
- **Csűrös 2026**, PNAS, doi:10.1073/pnas.2537812123 (PMC13167736, main text read through PMC).
  - Its known-truth simulations cover only Count/GLD birth-death models, plus IQ-TREE gene-tree recovery.
  - It runs no reconciliation on a known history.
  - Fig. S41, described in the main text, is a reanalysis of Moody's data: transfers correlate with family size (R² = 0.83), giving a LUCA of about 45 genes.
  - The SI PDF itself sits behind a browser challenge and was not opened.
- **Moody et al. 2024**, Nat Ecol Evol, doi:10.1038/s41559-024-02461-1. Its deposit (figshare 24428659, `COG_OR_reconciliation/`) has no known-truth simulation.
- **Szöllősi et al. 2026 and Williams 2023:** no simulations, per the coordinator's review. Not re-opened here.

## Kill test K1, on real data with no simulation (run first)
- **What the reweighting does.** `O_R_Optimization.py` multiplies only the root branch's prior weight, by w = exp(O_R). So for one family with flat-prior root odds r = a/b (a = root origination likelihood, b = the sum over the other branches), the reweighted posterior is PP(w) = w·r / (w·r + 1), and the family's log-likelihood is log b + log(w·r + 1) − log(N − 1 + w).
  - N = max_id + 1 = 2·700 − 1 = 1,399 branches.
  - r can therefore be recovered from Moody's deposited per-run PPs (`kegg1-5_cons.txt`) and per-category weights (`KEGG1-5_OR.csv`), with no `.uml_rec` file:
    - one-category families: r = odds(PP) / w;
    - two-category families (their PP is the mean over both categories, as in `setup_OR_estimation.py`): solve (PP(w1, r) + PP(w2, r)) / 2 = PP by bisection on log r.
  - Families with PP ≥ 1 − 1e-12 give only a lower bound on r. Their count is reported, and every sum is given as an interval over r between that bound and infinity.
- **Quantities.** Each is computed per run, then the per-family median over the 5 runs is summed over the 7,456 families common to all runs (as for E_M = 1,290.6):
  - S_rep: forward recomputation with Moody's weights. This is a check: it must equal E_M within 0.5%, or K1 is reported as "inversion failed" and stops.
  - S_flat: w = 1, ALE's default flat prior.
  - S_global: one global weight, fitted by maximising the summed log-likelihood over O_R ∈ [−5, 40] (grid step 0.01, then refined).
  - S_relaxed: per-category weights refitted with O_R ∈ [−5, 40], where Moody used [1, 20]. Two-category families are scored in both categories, as Moody did.
  - Each S is split by single-domain, both-domain ≤ 1%, and B2 (> 1% in both domains).
- **Decision (sealed).**
  - Moody's summed size is **"largely prior-driven"** if S_flat < 0.5·E_M (645).
  - It is **"prior-sensitive"** if 0.5·E_M ≤ S_flat < 0.8·E_M.
  - It is **"robust to the prior"** if S_flat ≥ 0.8·E_M (1,032).
  - The range [min, max] of {S_flat, S_global, S_relaxed, E_M} is reported as the prior-sensitivity range.
- **Predictions (sealed).**
  - P9: S_flat < 0.67·E_M (865).
  - P10: the single-domain share of S_flat is below Moody's 28.4%.
- **Limits.**
  - w = 1 is itself a prior: uniform over branches, so 1/1,399 at the root. It is not "no prior".
  - The inversion assumes `kegg*_cons.txt` holds the `rell` root posterior under the category weights, as their scripts imply. S_rep checks only the sum, not each family.

## Kill test K2: scaling on true gene trees (minutes to hours)
- **Design.**
  - ALEobserve on each family's true pruned gene tree (no IQ-TREE), then ALEml_undated and Moody's reweighting with one global O_R in [1, 20], plus the flat w = 1 version.
  - Sampled tips: 20, 40, 80 and 160 per domain (40-320 in total), at T* and 2·T*, seed 1, with everything else as in v3.
  - T* comes from stage F. If stage F has not finished after 24 h of laptop time, T* is set to the fit-grid centre (L = 1, transfer/loss = 0.2), and this is logged before any K2 score is read.
- **Measures.** R = (Σ root PP) / (true LUCA family count); recall and false share at T50/T75; the single-domain share of the sum.
- **Decision (sealed).** If R at 320 tips and 2·T* lies outside 0.8-1.25 under Moody's reweighting with true gene trees, the summed-PP size is biased even with perfect gene trees, and transfer to 700 genomes is called "dead before the grid".
- The direction of the trend in R with tip count is reported, with no prediction.

## Kill test K3: one inferred-tree cell at the most damaging setting
- 2·T*, 157 sites, IQ-TREE LG+G4 with 1,000 UFBoot, seed 1, at the largest tip count from K2 whose projected wall time is ≤ 36 h with 3 workers.
- The tip count is chosen from K2's timings only, before any K2 score is read.
- It is scored as in K2. It runs before any replicate.

## Changes to the study
1. **The main axis is now tip count**, replacing transfer level × 3 replicates. Any later grid is designed after K1-K3 and sealed in a further amendment.
2. **Arm H and the Huang endpoint are dropped,** along with P8, because of the reasons below. E_H (1,331.0) stays on file as background only.
   - 4 rate classes against Huang's 24;
   - a different AleRax version;
   - their ancestor is archaeal, not LUCA.
3. **The real-data correction is reported only as a sensitivity range,** never as "the corrected LUCA size". v2's verdict labels become descriptions of that range.
4. **Replication checks, not findings:** DTL recovery, root robustness and gene-tree accuracy reproduce Coleman et al. 2021 and are reported as replication checks.
5. **The true-tree arm is reduced to a check** (K2). The inferred-tree results carry the study.
6. Arm L (P7) and the stem-transfer diagnostic stay, after K1-K3, if those don't kill the study.

## Compute
- K1 is a minutes-long CPU job on deposited files.
- K2 and K3 run on the laptop under `compute.lock.origins`, with at most 3 workers, background priority and the memory guard.
- No main-grid run starts before K1-K3 are reported.
