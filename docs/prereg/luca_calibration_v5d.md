# Amendment v5d: K4, true-tree tip scaling and one worst-case cell (task #32)

Agent: orig-paper. Written 2026-11-23, before any K4 simulation. Seen so far: K2 (laptop), K3 seed 1 and n40 (AWS, Linux ALE), and the Linux true-tree scores of seeds 2 and 3 (R 1.057, 1.013). K3's seed 2-3 inferred arms were still running when this was sealed. Approved by the coordinator for the owner, 2026-11-23. Machine: one c7a.4xlarge spot instance via `.local/aws/spot.py`, at most 22 h, within the $50/month cap. Code: the sealed pipeline (manifest c555e9a4…) and Linux ALE build as in v5c (DEVIATIONS 12).

## Why
v5's original K2 rule asked about **320 genomes per domain**, which the laptop could not reach and the arm64 ALE build could not score (DEVIATIONS 11-12). K3 found the estimator calibrated at 80 per domain with transfer 0.4. Two open ways it could still fail are **scale** (more tips and branches, so the flat prior is spread thinner and the fitted weight must do more work) and **heavier transfer**.

## Lanes (in parallel; each step resumable; anything unfinished at 21 h is reported as not run)
1. **n160:** 160 genomes per domain (800 lineages), transfer 0.4, origination 40, 200 root families, seed 1. Simulate, ALE on true trees, score.
2. **n320:** 320 per domain (1,600 lineages), otherwise the same. Simulate, ALE on true trees, score.
3. **Worst case, w80:** 80 per domain, **transfer 0.8 (4·T\*)**, otherwise as K3. Simulate, ALE on true trees, IQ-TREE (LG+G4, 1,000 UFBoot) and ALE on inferred trees, score both.

## Measures
As in v5c: R (Σ PP with Moody's reweighting, one global O_R in [1, 20], divided by true root families in the sample), R\* over families completed in every arm, flat-prior R, fitted O_R, recall and false share at PP ≥ 0.5 and ≥ 0.75, and the false PP mass (Σ PP over non-root families).

## Decisions
- **Scaling (v5's rule, restored):** R_true at 320 per domain outside 0.8-1.25 means "the reweighting is biased at scale". If n320 does not finish, the rule is applied at 160 and labelled as such.
- **Worst case:** R\*_inf at w80 outside 0.8-1.25 means "fails under heavy transfer". Inside means "survives 4·T\* with gene-tree error".
- **Per-call error (descriptive, reported for every cell):** the false share at PP ≥ 0.5 and the share of the true root set missed at PP ≥ 0.5.

## Limits
One seed per cell. Origination 40 rather than 512. 200 root families. Not fitted to Moody's data.
