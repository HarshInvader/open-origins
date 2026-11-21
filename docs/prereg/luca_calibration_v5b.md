# Amendment v5b: K2 at lower gene-family richness, 20-80 tips (task #32)

Agent: orig-paper. Written 2026-11-21, before any K2 cell was simulated to completion. Seen so far: timing only, plus the origination fit's own output (origination 512, genome ratio 0.089, both-domain share 0.076), which v5a already made a descriptive check. No ALE output, PP, score or root count has been seen. v5 and v5a stay in force except as changed here. Approved by the owner on 2026-11-21 (option A).

## Timing that forces this
- At the fitted origination of 512 families per genome per unit time, the smallest K2 cell (20 tips per domain, 100 lineages) ran its genome simulation for about 40 min and did not finish before the 2 h step limit ended the job.
- Gm cost grows with lineages and families alive, so cells with 160 tips per domain would take days each. One step longer than 2 h cannot finish in this environment.

## Changes
1. **Origination is fixed, not fitted: 40 per genome per unit time.** Fallback on timing only: if the 20-tip, transfer 0.2 genome simulation takes more than 60 min, it is stopped and origination is halved (20, then 10). That value is then used in every cell. The fitted 512 and the genome ratio it would match (0.106) are reported. The miss on that ratio at 40 is stated as a limit.
2. **Tip counts: 20, 40 and 80 per domain**, at T\* (transfer 0.2) and 2·T\* (0.4), seed 1. 160 is run only if the 80-tip cells each take under 2 h per step.
3. **Decision rule (replaces the 320-tip rule):** R = Σ PP (Moody's reweighting, one global O_R in [1, 20]) / true root-family count, with true gene trees. R at 80 tips per domain and 2·T\* outside 0.8-1.25 means **"dead before the grid"**: Moody's estimator is biased under known truth even without gene-tree error. Inside the range means "survives K2".
4. **Reported alongside, descriptive:** R at every cell, the flat w = 1 sum, the fitted root weight against the weight that recovers the true count, recall and false share at PP ≥ 0.5 and ≥ 0.75, genome ratio, both-domain share, p-distance.
5. K3 as in v5a, on the 2·T\* simulation at the largest tip count run here.

## Added limits
- Gene-family richness is lower than in Moody's data, so rare families are under-represented. Rare, scattered families are the ones most likely to be misplaced at the root, so this may understate bias.
- The 320-tip test in v5 is not run.
