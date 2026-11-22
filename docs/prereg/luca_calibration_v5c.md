# Amendment v5c: K3 (gene-tree error) and K2 replicates, on one AWS spot machine (task #32)

Agent: orig-paper. Written 2026-11-22, after K2 was read (K2_RESULTS.md, commit f2d9a06) and before any K3 run. No inferred gene tree, K3 score, or seed-2/3 simulation exists yet. v5, v5a and v5b stay in force except as changed here. AWS approved by the owner on 2026-11-22. Machine: one c7a.8xlarge spot instance (32 vCPU) via `.local/aws/spot.py`, at most 24 h, within the $50/month cap.

## Why
K2 showed that with true gene trees, Moody et al.'s fitted root weight recovers the planted root set (R 0.91-1.08) once families that ALE crashes on are set aside. The remaining question is whether **gene-tree error** inflates or deflates the estimate. That is K3.

## Software
Same pinned code: ALE b59dfaf (Bio++ 2.4.1 fetched by ALE's CMake, Linux build with g++ and Ubuntu's Boost), Zombi as in `ext/zombi`, IQ-TREE 3 from bioconda (same major version as the laptop's 3.1.4), pipeline unchanged (manifest c555e9a4…). Build differences from the laptop are recorded in the run log.

## Runs (priority order; anything not finished at 22 h is reported as not run)
1. **K3, seed 1:** K2's existing simulation n80_t0.4 (80 genomes per domain, transfer 0.4, origination 40). `infer_trees.py` (IQ-TREE LG+G4, 1,000 UFBoot, families with ≥ 4 genes; 2-3 genes get their single topology), then `run_ale.py --trees inferred`, then `score.py`.
2. **Replicates:** seeds 2 and 3 of the same cell, simulated with the K2 runner settings, each scored with true trees (K2 arm) and inferred trees (K3 arm).
3. **K3 at 40 genomes per domain** (K2's n40_t0.4, seed 1), inferred arm.

## Measures
- **R_true, R_inf:** Σ PP (Moody reweighting, one global O_R in [1, 20]) / true root families in the sample, as in K2 (failed families PP 0).
- **Primary, R_inf\*:** the same ratio computed only over families that ALE completed in **both** arms of that seed (true and inferred). Introduced here, after K2 showed that ALE crashes on large families, which are all true root families. Stated before any K3 run.
- **Q = R_inf\* / R_true\*** on the same family set: the effect of gene-tree error alone.
- Also: flat-prior sums, fitted O_R per arm, recall and false share at PP ≥ 0.5 and ≥ 0.75, families by ALE status, PP of non-root families (the false-positive mass).

## Decision (seed 1 alone if replicates do not finish; otherwise mean over seeds)
- **R_inf\* > 1.25:** "gene-tree error inflates the reconstructed root genome". This would be evidence that Moody-style LUCA sizes are overestimates.
- **R_inf\* < 0.8:** "gene-tree error deflates it".
- **0.8 ≤ R_inf\* ≤ 1.25:** "the estimator survives gene-tree error at these settings".
- The direction is also reported with the seed-to-seed range; one-seed results are labelled preliminary.

## Limits carried forward
Origination 40, not 512 (fewer rare families than real data); 200 root families; 160 sampled genomes, not 700; T\* not fitted to real data; 157 sites with substitution scaling not fitted to Moody's p-distance.
