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
