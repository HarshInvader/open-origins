# Open Origins: open tasks

Exported from the team board on 18 Nov 2026. 11 ready, 0 waiting on earlier tasks, 1 in progress, 13 done.

To take one, read [CONTRIBUTING.md](../CONTRIBUTING.md) first: open an issue named `Taking #<id>` so nobody duplicates it.

## Ready now

### #21 Red-team the pathway-map encoding

Milestone M6, priority 2.

Attack experiments/pathway_map (tasks #4/#5, orig-3). Check each step row in steps.py against its source (numbers, purified flags, pH/T), and try to find a hand-off that the rule allows but orig-3 failed (e.g. a fairer process list for C1->C2, C5->C6 formamide, C7->C8 purines), or one passed too generously (C2->C3 rain redissolution at pH 6, C3->C4 lab crystallisation + pH 9, vent 1000x thermophoresis). Also check the wrapper (score_map.py) that turns NaN/unknown checks into 'unassessed'. If Powner 2009 or the Simonis 2026 full text can be read legally, encode C5, C7 and P1. Never red-team your own result.

### #22 Red-team the assembly-index positive (T7a)

Milestone M6, priority 2.

T7a found MA adds dAUC 0.061 [0.037,0.089] beyond MW+HA on 889 mass-matched Rhea vs GDB-13/17 pairs, and beats LZ (0.054 [0.020,0.085]); but biotic MA is LOWER at matched HA (-0.52). Not orig-2. Try to break it: (1) re-match on ring count / scaffold class as well as mass; does the gain vanish? (2) swap GDB for a non-enumerated abiotic set (Bennu/Murchison soluble organics, Miller-Urey/formose products); (3) recompute MA from a second implementation or Kekule-invariant form; (4) check the refit bootstrap CI and the M_MW matching code in experiments/assembly_null/{molecules.py,planted_refit.py}. Inputs: experiments/assembly_null/out/molecules.csv + ma_cache.jsonl. Report whether the positive survives and in which direction.

### #24 Red-team the Xavier 2020 'within null' result (#6)

Milestone M6, priority 2.

Treat the negative like a positive and try to break it before it is shown as a finding. Check: (1) the reproduction of 1,335 vs our 1,357 reactions, and which food set and catalysis annotations were used; (2) whether degree-preserving rewiring keeps chemistry valid (mass balance, cofactor roles), or inflates maxRAF with impossible reactions; (3) whether the degree-matched food null is fair to the original claim, which was about the food set they chose; (4) whether the verdict changes under a chemistry-respecting null (e.g. swap only within reaction classes, or EC-level shuffles); (5) what Xavier et al. actually claimed (read the paper's own wording; do not strawman). Output experiments/raf_null/REDTEAM.md with survives / weakened / overturned and the reason. No new compute beyond 30 min; use board/run.sh.

### #11 Bennu abundance prediction

Milestone M5, priority 3.

From formose and Strecker kinetics, hash predicted relative abundances for compounds not yet reported from Bennu or Ryugu. Decisive: later papers match or miss.

### #12 QT45 double-mutant prediction

Milestone M5, priority 3.

From single-mutant data, hash predicted fitness of unmeasured QT45 double mutants (an additive model and an epistatic model). Later scans confirm or refute.

### #15 Our own hypotheses (H track)

Milestone M3, priority 3.

Propose up to 3 new, testable hypotheses about how life began, built from results landed so far: which pathway gap is really blocking, a chemical regularity in Bennu or Ryugu data, or a network property that separates real from random metabolism. For each: write the refuting result, hash it in docs/prereg, test it on data it was not formed on (another network, another sample, or later data), and run a planted-answer check. Failures go in the negative atlas.

### #16 Red-team the citation audit and news page

Milestone M6, priority 3.

Independently re-resolve a random 15 of the 62 DOIs in docs/PAPERS.csv and every number in site/news.json and the theories/map sections of site/content.json against the source. Report any mismatch. Do not use experiments/research_sweep/tools; build your own check.

### #19 Seal purine:pyrimidine vs ammonia prediction for returned samples

Milestone M5, priority 3.

Koga et al. 2026 Nat Astron (doi:10.1038/s41550-026-02791-z) report purine/pyrimidine ratio correlating negatively with NH3 across Ryugu, Bennu and Orgueil. Fit it from the published tables and hash a prediction for the next Bennu/Ryugu nucleobase table before it appears.

### #23 RAF null test on a Rhea-built anaerobic network

Milestone M3, priority 3.

Task #6 found the Xavier 2020 KEGG-derived maxRAF within/below its nulls. Build an anaerobic network from Rhea (open) with cofactor/metal catalysis annotations, rerun experiments/raf_null/cnet.py maxRAF with nulls N1 and N3m (and a role-matched food null: catalyst degree and substrate degree matched separately). Pre-register first. Decisive: does the database change the verdict?

### #10 LUCA robustness scan

Milestone M3, priority 4.

On a subsample of families, measure how much of the Moody et al. 2024 (Nat Ecol Evol 8:1654) gene set and acetogen call survives changes to the presence cutoff, taxon sampling and transfer model. Compare with Weiss 2016 and Crapitto 2022. Laptop: subset only.

### #13 Independent rerun of the bench

Milestone M6, priority 5.

An agent that has not seen our code reruns the RAF null test, the assembly-index test and the LUCA scan from raw data.

## Waiting on earlier tasks

## In progress (do not duplicate)

- #25 Dataset catalogue for origin-of-life research (Indus-style datasets/)

## Done

- #1 2023-2026 paper ledger, DOI-verified: **data**, `experiments/research_sweep/RESULTS.md`

- #3 Hash the step-compatibility rule: **tool**, `experiments/compat/RESULTS.md`

- #2 QT45 numbers from the paper and deposit: **negative**, `experiments/qt45_numbers/RESULTS.md`

- #4 Encode pathways as step tables: **data**, `experiments/pathway_map/RESULTS.md`

- #6 RAF null test: **negative**, `experiments/raf_null/RESULTS.md`

- #8 Planted autocatalytic core recovery: **mixed**, `experiments/raf/RESULTS.md`

- #14 Citation audit: **mixed**, `experiments/research_sweep/RESULTS.md`

- #17 Pond (wet-dry) step table: **data**, `experiments/pathway_map/RESULTS.md`

- #18 Net replication per cycle from Attwater 2025: **negative**, `experiments/pathway_map/RESULTS.md`

- #20 Rule on thermophoretic purification in the compatibility rule: **data**, `experiments/research_sweep/RESULTS.md`

- #5 Score all pathways: **negative**, `experiments/pathway_map/RESULTS.md`

- #7 Assembly index vs a size-only null: **mixed**, `experiments/assembly_null/RESULTS.md`

- #9 Simulated-tree LUCA recovery: **negative**, `experiments/luca_planted/RESULTS.md`
