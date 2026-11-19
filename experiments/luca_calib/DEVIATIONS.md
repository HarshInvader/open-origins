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
