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
- **Caveat added 2026-11-26.** The degree-preserving rewiring does not conserve atom balance, so most of its reactions are chemically impossible, which was already known to distort such comparisons (Basler et al. 2011, doi:10.1093/bioinformatics/btr145). After T17, the side-reading that real metabolism is *less* autocatalytic than same-degree random wiring is withdrawn pending an atom-balanced re-run. The verdict here rests on the degree-matched random food set, which rewires nothing, so it is unaffected.
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

## "QT45 tertiary contacts can be read off the open double-mutant landscape" fails on its own power check (qt45, task #30)
- **Test.** Gianni et al. 2026 (doi:10.1126/science.adt2760) deposit 132 single and 8,346 double QT45 mutant fitnesses (Zenodo 13891380, MIT). I fitted additive fitness plus a monotone global nonlinearity, took the residual as epistasis, ranked position pairs against a null matched on sequence separation and single-mutant fitness, and sealed the top 10 non-Watson-Crick contacts plus 10 triple mutants predicted to beat wild type. Prereg sha `c3097e59`.
- **Result.** The planted check recovered on average 4.8 of 10 implanted contacts in its top 20 (chance 0.2) but passed the sealed bar of 5-of-10 in only 5 of 10 replicates, against the pre-set 8 of 10. The sealed non-Watson-Crick list came back with one pair, not ten (G10-A38, q=0.53), because the sealed filter excluded any pair with a WC-complementary double and almost every pair has one.
- **The informative part.** Out-of-sample R² on held-out doubles: additive 0.655, additive + global nonlinearity 0.910, plus pair epistasis 0.910. The floor at about -14 log2 explains nearly all the apparent epistasis, and pair-specific terms add +0.0005. Reported "negative epistasis" in landscapes of this depth is largely saturation.
- **Detectable.** Positive controls are recovered where coverage allows: C11-U35 ranks 1 of 718 pairs, C8-G39 rank 3, G7-C40 rank 5. But three of the eight published pairs (G10-C36, G18-C30, C17-G31) have fewer than 3 informative doubles, so the method cannot see known core interactions.
- **Not closed.** It reopens with a deeper or less saturating selection, more than one library, or a non-WC filter that is not self-emptying. A QT45 structure would also make it checkable: RCSB has no QT45 entry as of 2026-11-19.
- **Details.** experiments/qt45_epistasis/RESULTS.md.

## "Prebiotic multi-step papers under-report step-end conditions" fails within papers (audit, task #31)
- **Test.** A sealed audit (prereg sha `fd412e97`) of 40 open-access prebiotic papers and 20 Beilstein J Org Chem multi-step papers. Both sets were randomly sampled (seed 0) from fixed Europe PMC queries and scored per hand-off for end pH, T, concentration, solvent, carried-vs-fresh and workup. A blind second coder agreed with mean kappa 0.95.
- **Result.**
  - P1 fails: the median paper reports pH at 100% of its aqueous hand-offs; overall 68% of 57.
  - P2 fails: 90% of papers state carried/isolated/fresh for every input.
  - P3 fails: all four numeric items in 28.1% vs 28.9% of hand-offs, diff −0.008, CI −0.17 to 0.16.
- **Detectable.** A gap of about 0.23 between sets at 80% power.
- **What remains.** Exploratory, not sealed: the concentration of the carried product is reported less often in prebiotic papers (59% vs 89%, CI on diff −0.47 to −0.12). The pH gap #29 found sits *between* papers stitched into one route, not within single papers.
- **Not closed.** The sealed pH item counts a stated buffer pH. A "measured end pH" item, and a cross-paper route audit with fixed step lists, remain open.
- **Details.** experiments/reporting_audit/RESULTS.md.

## "QT45's error threshold can be read from its single and double mutant landscape" fails its planted test twice (qt45, T18 and T18b)
- **Test.** We fitted a Bayesian additive-plus-nonlinearity model to Gianni et al. 2026's open singles and doubles (doi:10.1126/science.adt2760; Zenodo 13891380). We then carried the fit to genotypes several mutations away and read off the error rate at which the wild-type class is lost. Before touching the real data, the method had to recover planted thresholds within 20% on synthetic landscapes. T18 dropped the pair residuals; T18b kept them as a learned pair-variance τ².
- **Result.** T18 erred low: median −27% in its pair-epistasis family. T18b erred high: 0 of 5 in the higher-order-only family, posterior mode +42%, and most draws above the grid. The noise-only family was recovered within 1%. Neither method was run on the real landscape.
- **What it could catch.** The planted test catches a systematic bias of 20% or more in any family (more than 4 of 20 misses). Both models fit HD ≤ 2 data and bracket the truth from opposite sides by roughly −27% and +40% or more.
- **Scope.** This closes threshold estimation from HD ≤ 2 data alone. It does not close a threshold estimate with measured triples or deeper mutants, or a direct measurement of the error threshold by serial replication at graded fidelity.
- **Details.** docs/prereg/t18_qt45_error_threshold.md, docs/prereg/t18b_qt45_pair_epistasis.md, experiments/t18_qt45_error_threshold/.

## "Biochemistry's nested autocatalytic tiers reflect its specific chemistry" fails against atom-balanced nulls (orig, U1/T17; overturns T14)
- **Test.** Peng, Linderoth and Baum 2022 (doi:10.1371/journal.pcbi.1010498) report that a KEGG-derived network of 4,216 species expands from a fixed food set into 3 nested self-sustaining sets (1,414, 357 and 301 species). T14 compared this with degree-preserving product swaps, which gave 1 set and no nesting, and read the hierarchy as chemically special. T17 rebuilt the null to swap whole half-reactions within formula-difference classes, so every rewired reaction stays atom balanced and the tier-0 food set is untouched. 700 draws over four nulls, all 4,186 candidate seeds, rules sealed before the run.
- **Result.** The atom-balanced nulls reproduce the hierarchy. Real 3 sets against Null A's median of 3 and Null B's 1-3; real nested share 1.0 against a median of 1.0 in three of the four nulls; real chain depth 3 against Null A's median of 3. Every real statistic is inside the central 95% of all four nulls. Sealed verdict: kill. The nulls mixed well (74% of reactions changed, Jaccard 0.175).
- **What it could catch.** The kill rule kills 10 of 10 same-degree controls and 5 of 5 background networks while killing 0 of 10 networks with a planted autocatalytic core, so it can withhold a kill when a strong hierarchy is present. It was not calibrated against hierarchies weaker than the planted one, so a small excess over legal-chemistry nulls would have been missed.
- **Scope.** It closes the hierarchy statistic (set count, nestedness, chain depth) as evidence about early metabolic chemistry, for the biochemical network. It does not show autocatalytic sets are absent; the nulls have them too. The abiotic network was not re-run. Atom-balanced nulls kept part of a planted core in 10 to 12% of draws, so they are gentler on hierarchy than degree nulls.
- **Not closed.** It reopens with a null that conserves atoms and thermodynamic feasibility, or one built on a measured flux-carrying subnetwork instead of KEGG's full reaction list.
- **Details.** experiments/t17_atom_balanced_tiers/T17_RESULTS.md.
