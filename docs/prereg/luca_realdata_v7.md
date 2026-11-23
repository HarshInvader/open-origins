# Pre-registration v7: real-data checks on the LUCA root weight (Fable additions 1–6)

Sealed 2026-11-23 before running any of the tests below. The KEGG lists were downloaded first (raw/kegg_lists/, KEGG REST, fetched_utc.txt); none of them has been matched to PPs yet.

Shared definitions:
- **Data:** Moody et al. per-run PPs (kegg{1-5}_cons.txt) and category weights (KEGG{1-5}_OR.csv).
- **Flat-prior root odds:** r is recovered exactly as in K1 (k1_prior.py, `invert`). There are N = 1,399 branches. The 7,456 families common to all five runs are scored, and every summary is the median over the five runs.
- **PP(w):** PP(w) = w r/(w r + 1).
- **Bayes factor:** BF = r (N − 1). This is the factor by which the data move the odds of origination at the root against one average non-root branch. Unlike r, it does not depend on tree size through the prior.

## 1. Dose response (descriptive)
On a log-spaced grid of global w from 1 to 1e5, report:
- Σ PP;
- the number of families with PP ≥ 0.5;
- the prior root share w/(w + N − 1).

No decision rule.

## 2. Bayes factors, real against simulated
- **Simulations:** use every simulation with a truth.tsv (K2, K3 s2/s3, K4 n160, K5). Take PP_flat from root_pp.tsv, odds = PP_flat/(1 − PP_flat), N_sim = 2 × leaves(species tree) − 1, and BF = odds × (N_sim − 1). Clip PP_flat to 1 − 1e-12.
- **Threshold BF\*:** from the pooled simulated families scored on true trees (ale_true), choose the BF that maximises balanced accuracy for the truth label `luca`.
- **Report:**
  - the number of real families with BF ≥ BF\*;
  - the same count at the 10th and 90th percentiles of BF\* across the individual simulations;
  - the sensitivity and specificity of BF\* in the simulations.
- **Reading:** this is a count that does not use the root weight at all. It is valid only to the extent that the simulations resemble the real data, which the paper already says is not established. It will be reported as a bracket, not as an estimate.

## 3. Real-data controls
- **Positive set:** KOs in KEGG map03010 (Ribosome) or map00970 (Aminoacyl-tRNA biosynthesis) that are among the scored families and have occA ≥ 0.5 and occB ≥ 0.5.
- **Negative set:** KOs in modules M00161 (Photosystem II) or M00163 (Photosystem I) that are among the scored families. Oxygenic photosynthesis is not a LUCA trait.
- **Window:** the range of global w where the mean PP of the positive set is ≥ 0.9 and the mean PP of the negative set is ≤ 0.1.
- **Decision:**
  - (a) Moody's fitted w (median global ŵ from K1) lies inside the window: the controls are consistent with Moody's weight.
  - (b) The window exists but excludes ŵ: report the range of counts (Σ PP) the window implies.
  - (c) There is no window: these PPs cannot separate a known-ancient set from a known-young set at any single weight.
- **Fewer than 5 families:** if either set has fewer than 5 scored families, report the test as underpowered and do not apply the rule.

## 4. Propagation to proteins (descriptive, validated first)
- **Method:** reimplement R `loess` (span 0.75, degree 2, tricube weights, direct fit, family gaussian) in numpy. Fit proteins ~ KOs_per_genome on merged_data_genomes_kos_bp.csv.
- **Validation gate:** the prediction at 1,298.25 KOs must be within 1% of Moody's reported ~2,657. If it is not, propagation is not reported.
- **Prediction:** predict proteins at Σ PP for the w values in item 1, and for any window from item 3. Below the smallest observed KO count (161) the prediction is reported as NA, not extrapolated.

## 5. Csűrös et al. supplementary
Try to obtain the supplementary files from PMC through ordinary access only. If the files are not reachable, record that and stop.

## 6. Families dropped before scoring
- **Sets:** compare families with a FASTA in Pure_sequences but not among the 7,456 scored ("missing") against the scored families. Compute, from the FASTA headers and the taxonomy file:
  - number of sequences;
  - genomes;
  - occA and occB;
  - universal = occA ≥ 0.5 and occB ≥ 0.5.
- **Decision:**
  - If the universal fraction among missing families is ≥ 2× that among scored families, or the median number of sequences of missing families is ≥ 2× the scored median: flag a possible undercount. Report the bound: the number of missing universal families, which is an upper bound on LUCA families lost before scoring.
  - Otherwise: report that the dropped families do not change the count materially.
