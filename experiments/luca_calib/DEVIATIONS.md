# Implementation notes and logged deviations (task #32)

Written before the pilot, as v3 and v4 require. None of these changes a prediction or a decision rule.

1. **Arm L (v4 §A): family rate heterogeneity is dropped in this arm.**
   - Zombi's Gu mode can apply loss ×1.6 to the clade's subtree without code edits, but it cannot also draw per-family rates.
   - Gu rates are per lineage and genome-wide, so the genome model differs from Gm. Rates are scaled to the fitted genome size, and loss is set so the expected genome size does not drift.
   - Recorded as `family_rate_heterogeneity: dropped`. v4 allows this case.
2. **Arm H (v4 §B) differs from Huang et al. 2026.** Their scripts have no AleRax command line, so H is built from their methods text.

   | Item | Ours | Huang |
   |---|---|---|
   | AleRax version | 1.4.0 | 1.1.1 |
   | Rate classes | 4 (root, two root children, fast clade) | 24 (72 parameters) |
   | Fraction missing | 0 | CheckM2 estimates |
   | Species-tree search | SKIP; AleRax will not combine a parametrisation file with HYBRID or REROOT | n/a |
   | Families with fewer than 3 genes | root PP set to 0 | stated as excluded |

   Details are in `h_meta.json` for each run.
3. **v3's check of ALE against Moody's own data (50 families) is not yet done.** It needs their `.uml_rec` files from the Bristol data repository, which did not connect on 2026-11-19. The B1/B2 baselines on Moody's real data are waiting on the same download. Both will be retried; if they cannot be done, they are reported as not done.
4. **Optimiser.**
   - bayesian-optimization 1.4.3 is used with `allow_duplicate_points=True` (needed when the optimum sits at a bound); 1.2.0 does not work with numpy 2.
   - Moody's bounds (1, 20) are kept verbatim, so O_R cannot fall below 1.
   - The flat sensitivity analysis uses O_R fixed at 1, as v3 states.
5. **ALE build.** ALE's own CMake builds Bio++ 2.4.1, because ALE does not work with Bio++ 3.0. ALE commit b59dfaf3.
6. **Moody's `read_file` and `rell` are used unchanged and hash-checked.** On synthetic input they match a numpy reference to 3.6e-15.
7. **Laptop rules of 2026-11-19 (code change before the pilot).**
   - The runners now default to the Origins lock, `compute.lock.origins`.
   - Workers are capped at 3.
   - A memory guard waits while free memory is under 20%. It runs before each stage, IQ-TREE family, ALE family, Su chunk and fit point.
   - The manifest was resealed after these changes. They affect scheduling only, not results.
8. **ALE link fix.**
   - ALE's CMake links `Boost::mpi` into its exODT library. conda-forge Boost 1.85 has no boost_mpi library, so the link failed.
   - `ale_boost_shim.cmake` now provides an empty `Boost::mpi` target. ALE's own files are still unedited.
   - ALEobserve and ALEml_undated linked without undefined symbols, so neither uses MPI.
   - The manifest was resealed.
9. **Zombi Ti's window for counting tips as alive.**
   - Zombi `Ti` treats every leaf within 0.1% of the farthest leaf as alive. At 600 extant lineages, extinct lineages that died inside that window came back as 1–5 extra extant tips, and the pipeline's own consistency check stopped stage F.
   - `step_species_tree` now ends such extinct leaves just before the window, moving each by ≤ 0.11% of tree height. A leaf born inside the window is removed instead.
   - Counts are recorded per simulation (`ti_guard_shortened`, `ti_guard_removed`). Zombi itself is unedited.
   - Test on seeds 100, 105, 107, 109 and 115: 3–6 leaves shortened, at most 1 removed, and the extant tree was rebuilt exactly.
   - The ale_smoke stage ran before this fix. It is plumbing only and is not rerun.
   - The manifest was resealed.
