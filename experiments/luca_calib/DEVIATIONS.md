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
10. **Stage F not run; K2 and K3 scaled down (prereg v5a, 2026-11-20).**
    - One Gm run at the v3 scale takes about 5 h or more at background priority, so stage F would take more than a week.
    - v5's fallback T* (loss 1, transfer/loss 0.2) is used now, on timing alone.
    - K2 and K3 use 200 root families. Their origination rate is fitted once on a small tree.
    - The seqscale step is skipped. Details are in `docs/prereg/luca_calibration_v5a.md`.

## 11. ALE overflow on very large families (2026-11-21, before any K2 score was read)
In K2 cell n20_t0.4, ALEobserve crashed on 2 of 386 families (166 and 527 gene copies): Boost `double_factorial` / `tgamma` overflow, a known size limit of ALE. `run_ale.py` (sealed) already writes PP 0 for such families and exits 3. The K2 runner now accepts exit 3 for ALE steps. Those families keep PP 0 and stay in the true count, which can only lower R. The number of failed families per cell is reported. Decided from the error log only; no score, PP or root-family identity was looked at.

## 12. ALE large-family crashes are specific to the laptop build (2026-11-22, before any K3 score)
The Linux x86-64 build on AWS (g++ 13.3, Boost 1.83; BUILD_INFO_aws.txt) was checked against the laptop build on K2's n40_t0.4 true trees. Flat root PPs agree to 3e-18 on all 528 families both completed. The 15 families that crashed ALEobserve on the laptop (macOS arm64, where `long double` is 64-bit, so Boost `tgamma` overflows sooner) run fine on Linux, where `long double` is 80-bit. So DEVIATIONS 11's crashes come from the laptop platform, not from ALE as Moody et al. would have run it. K3 therefore re-runs the true-tree arm on Linux for every cell. The laptop K2 results are kept as `ale_true_laptop`. The K2 verdict (R = 0.751) is superseded by the Linux true-tree R for the same simulation, which will be reported alongside it.

## 13. K3 setup fixes (2026-11-22, before any K3 score)
- `setup_remote.sh` stopped at the IQ-TREE symlink step (pipefail on `ls`). It now continues, and it installs Zombi's `networkx` and `pyvolve` and the `biopython` versions the laptop uses.
- `run_k3.sh`: seed lanes failed at start (unbound variable), so lanes can now be started separately (`LANES`). Seeds 2 and 3 started about 3 minutes after seed 1 and n40.
- `verify.sh` cannot check prereg hashes on the machine (docs/ not copied). The pipeline manifest was checked there with `sha256sum -c`: all files OK.

## 14. First K3 machine lost; seeds 2-3 re-run (2026-11-23, before any K3 inferred score for seeds 2-3)
The first c7a.8xlarge spot machine was gone about 9.5 h into its 24 h booking (spot reclaim; disk deleted). Seed 1, n40 and the true-tree scores of seeds 2-3 had been pulled before. Seeds 2-3 are re-run from scratch on a second machine (same seeds, so the same simulations), with 16 workers per lane (`SEED_W`), and results are pulled every 4 minutes. `setup_remote.sh` now tolerates the IQ-TREE link already existing.

## 15. K4 machine lost; n160 and n320 moved to the K3 machine; w80 dropped (2026-11-23, before any K4 score)
- **What happened:** the origins-k4 spot instance (c7a.4xlarge) was reclaimed by AWS (`Server.SpotInstanceTermination`) during the first simulation step, so no K4 output existed.
- **Change:** the n160 and n320 lanes (true trees, v5d/v5e decision cells) were restarted unchanged on origins-k3b with `LANES="n160 n320" bash k4/run_k4.sh`.
- **Dropped:** w80, a robustness check only under v5e. A relaunch would need about $10 of the $9.70 left in the booked budget.
- **Timing:** v5d's fallback still applies; if n320 does not finish before the machine's auto-termination, n160 is scored.

## 16. K5: stemsim determinism fix after sealing; seed 2 stopped by its planted check (2026-11-23, before any tuning output or PP was read)
- **Bug:** stemsim drew ordinary-transfer recipients from an unsorted Python set. With hash randomization (`python -I`), set order changes between processes, so runs could not be repeated exactly.
  - **Fix:** the candidates are now sorted, matching how the stem-transfer candidates were already drawn. The model is unchanged; only reproducibility is.
  - The stemsim hash is resealed in HASHES.txt. A repeat run now gives identical output.
- **Planted checks with the fixed code:**

  | Seed | Births | KS D: genes / occupancy / domain A / domain B | Critical value |
  |---|---|---|---|
  | 1 | root | 0.048 / 0.055 / 0.048 / 0.070 | 0.111 |
  | 1 | mid | 0.018 / 0.023 / 0.055 / 0.034 | 0.097 |
  | 2 | root | 0.097 / **0.120** / 0.088 / 0.078 | 0.111 |
  | 2 | mid | 0.030 / 0.037 / 0.047 / 0.046 | 0.089 |
  | 3 | root | 0.067 / 0.053 / 0.035 / 0.057 | 0.111 |
  | 3 | mid | 0.077 / 0.073 / 0.019 / 0.066 | 0.095 |

- **Seed 2 stopped:** its root-birth occupancy check fails (0.120 against 0.111), so under v6 K5 stops for seed 2. K5 runs on seeds 1 and 3, and a λ level is read only if both match.
- **Red-team note, not a rule change:** these are 24 tests at α = 0.05, so about one failure is expected even from a perfect simulator. On seed 2, stemsim's root families are about 4% less widespread than Zombi's (mean occupancy 81.3 against 84.8). One possible cause is Zombi's genome-size floor, which stemsim lacks.
- **Process note:** tuning was first started as six detached processes. That broke the 3-worker cap and the no-detach rule. They were killed before finishing, their output was deleted unread, and tuning was rerun as a tracked job with 3 at a time.

## 17. Second K3 machine lost; seeds 2-3 inferred arms re-run; K4 n320 not run (2026-11-23, before any seed 2-3 inferred score was read)
- AWS reclaimed origins-k3b (spot, "no capacity") at 08:50 UTC, 3 h before its booked end.
  - The last pull (about 07:55) had the true-tree arms of seeds 2-3 and K4 n160 (scored). It did not have the seed 2-3 inferred-tree output, which was then in its last few IQ-TREE runs.
  - K4 n320 was still simulating and is lost.
- Seeds 2-3 are re-run from scratch on origins-k3c (c7a.8xlarge, 5 h, $5.12 booked; $45.42 of $50 for the month). The scripts are unchanged and the seeds are the same, so the simulations are the same. This time results are pulled every 10 minutes.
- K4: under v5d, the scaling rule is applied at n160, labelled as such; n320 is reported as not run.
- K4 n160: ALE failed on 1 of 1,411 families (family 46, a root family with 1,853 genes). Under the v5e completion clause the cell is inconclusive. R is reported with the failed family counted both ways (1.100 / 1.105).
