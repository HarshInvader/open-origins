# Negative atlas

Closed routes, each with the effect size the test could have caught. Empty until the first tests land.

## Assembly index on Marshall 2021 mixtures does not beat ion size (orig-2, task #7)
- **Test.** Max MS2 peak count vs max m/z per sample, 13 biological vs 12 non-living samples.
- **Result.** ΔAUC 0.115, 95% CI −0.19 to 0.42.
- **What it could catch.** The planted check detects only a shift of about 2 between-sample SD (power 0.5); 1.5 SD gives power 0.2.
- **Why the route is not closed.** The data are too small and their m/z range is narrow (300–500). Reopen with more samples or wider-m/z data.
- **Details.** experiments/assembly_null/RESULTS.md.

## "Biotic molecules have higher assembly index at matched size" fails on small molecules (orig-2, task #7)
- **Result.** Rhea vs GDB-13/17, heavy atoms ≤ 17, matched on HA: biotic minus abiotic MA = −0.52 (−0.60 to −0.44), the opposite sign to the prediction.
- **Caveat.** MA does add separation beyond size (ΔAUC 0.061), but by flagging ring-rich enumerated scaffolds as *more* complex.
- **Scope.** This covers small molecules only. It says nothing about MA ≥ 15.
- **Details.** experiments/assembly_null/RESULTS.md.

## "The 1,335-reaction RAF in anaerobic metabolism is more than an artefact of size and food choice" fails (orig-1, task #6)
- **Result.** The Xavier et al. 2020 maxRAF reproduces exactly from their dataset S4 (1,335, plus 22 Pooling rows). Degree-preserving rewired networks give 3,394-3,583, with the real value far below (p_lower = 0.001). Degree-matched random food sets give 705-1,403, with the real value inside (p_upper = 0.064).
- **Detectable.** A maxRAF of 1,404 or more would have been flagged under N3m. Under N1, cores smaller than about 30% of the background maxRAF are not detectable by size (task #8).
- **Scope.** KEGG-derived network as deposited, one food set. A Rhea-built network is open as task #23.
- **Details.** experiments/raf_null/RESULTS.md.

## "Metabolic assembly strata follow enzyme age and metal catalysis" fails within pathways (orig-paper, task #28)
- **Test.** Mrnjavac et al. 2026 (doi:10.1126/sciadv.aef3128) give 408 reactions in 49 strata. I asked whether, within the same pathway, reactions with LUCA enzymes, Moody 2024 LUCA KOs, or reactions shown to run on metals without enzymes sit in earlier strata. Labels were permuted within pathways; prereg sha `406b3e37`.
- **Result.** None of the three holds within pathways (Holm p 0.39, 0.66, 0.40). Across the whole network, metal-catalysed and Moody-LUCA reactions are earlier (p 0.003, 0.0003), but that comes from which pathway they are in. The paper's own LUCA label shows no ordering even across the whole network: mean stratum 22.7 LUCA vs 22.0 lineage. Strata 1-7 hold more lineage-specific enzymes than LUCA ones.
- **Detectable.** With labels tilted 0.7/0.3 within pathways, power is 0.995.
- **Not closed.** An exploratory within-pathway rank-percentile signal for age (p ≈ 0.01) would need a fresh sealed test on another stratified network.
- **Details.** experiments/metabolic_strata/RESULTS.md.

## "An intervention ledger of prebiotic RNA routes can be scored reproducibly from published methods" fails (orig-paper, task #29)
- **Test.** Two blind encoders scored six new routes (Becker 2018/2019, Xu 2020, Yi 2020, Ritson 2022, Gibard 2018) under sealed rule v1. Prereg sha `528b9d13`; the sealed kill rule was kappa < 0.6.
- **Result.** Kappa 0.22 on the 7 hand-offs that could be aligned. The encoders cut 4 of the 6 routes into different numbers of steps. The sealed prediction P3 (at least 90% of breaks are F3/F4/F6) failed in both encodings (12%, 27%), because process errors driven by unreported pH dominate.
- **What remains.** pH continuity can be checked at only 2-4 of 17-20 hand-offs, so "breaks are never pH" mostly reflects what papers do not report.
- **Not closed.** It reopens with author-fixed step lists and a reporting checklist.
- **Details.** experiments/ledger/RESULTS.md.
