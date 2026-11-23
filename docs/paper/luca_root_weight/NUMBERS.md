# Where each number comes from

All paths are relative to `experiments/luca_calib/`.

| Number in paper | Source |
|---|---|
| 1,290.6 / 1,286.2 / 1,270.0 / 33.9; PP thresholds (Table 1) | `K1_RESULTS.md` (output of `k1_prior.py`) |
| ΔLL 1,169 (run 1); 1,089-1,166 (5 runs); log w 5.58-5.77; count 1,238-1,347 | `k1_ci.py` → `results/k1/k1_ci.json` (O_lo/O_hi, S_lo/S_hi, dLL_flat per run) |
| Table 2 (R, crashed families, Linux 1.087) | `K2_RESULTS.md`; DEVIATIONS 11-12 |
| Table 3, mean 1.009, false/missed mass, PP > 0.8 shares | `K3_RESULTS.md`; `results/k3/k3_report.json` |
| R 1.100 at 160 genomes | `K4_RESULTS.md`; `results/k4/k4_report.json` |
| Table 4, H, flat-prior H, stem transfer 115-600×, burst 28-80×, crossings 4.0-6.9, +26% genome size | `K5_RESULTS.md`; `results/k5/k5_report.json` |
| Multipliers 1.4-1.9; flat share 46-76% of the true ancestor | ratios computed from the K2-K4 tables above (fitted Σ PP / flat Σ PP) |
| Identity ΣPP = F·w/(w+N−1); 17% root share | `results/k1/k1_ci.json` (F, O_hat, S_hat per run) |

## Real-data checks (prereg v7, `docs/prereg/luca_realdata_v7.md`; results `experiments/luca_calib/results/realdata/realdata_v7.json`)

Script: `experiments/luca_calib/realdata/r_analyses.py`. Figures: `figures/make_figures.py`.

| Number in text | Source field |
|---|---|
| fitted w ≈ 293, prior share 17% | `w_hat_median` (292.9); 293/(293+1398) |
| 830 families at w=100; 2,022 at w=1,000 | `dose` (median-run sum) at w=100, 1000 |
| 1,546 / 4,249 / 2,638 proteins | `loess.dose` at w=100, 1000; `loess.at_w_hat` |
| LOESS 2,659 vs Moody 2,657 | `loess.pred_at_1298.25`; gate_pass true |
| 50 ancient / 12 young families | `controls.n_pos`, `controls.n_neg` |
| verdict: no window | `controls.verdict` = "c: no window" |
| ancient reaches 0.9 above w≈43,000 (97% prior share) | `controls.w_min_pos_ge_0.9` 42,658 |
| young ≤0.1 up to w≈3,200 | `controls.w_max_neg_le_0.1` 3,236 |
| ancient mean 0.31 at fitted w | `controls.mean_pp_pos_at_what` 0.306 |
| post hoc, Moody's own PPs: mean 0.52, 28 ≥0.5, 8 ≥0.9; L22/L18/S4 0.04; PsaB 0.89; 11 photosystem < 0.01 | computed from kegg{1-5}_cons.txt medians (session log 2026-11-23); occupancies from real_features_moody.tsv; names from raw/kegg_lists/list_named_kos.txt |
| translation (J) weights among largest | KEGG{1-5}_OR.csv: J 1,191–1,293, behind W/B (bound) and Z |
| 75% BF<1, median 0.18 | `bf.real_frac_bf_lt1` 0.753; `bf.medians.real` −0.736 (log10) |
| 82% in [0.01, 10]; sims 11% / 20% | `bf.share_m2_1` |
| sim root median BF ≈ 1,800 | `bf.medians.sim_root` 3.256 (log10) |
| threshold 2.2, balanced accuracy 0.92 | `bf.pooled_log10_bf_star` 0.341; `bf.pooled_bal_acc` |
| 1,439 families; 954–1,916 | `bf.real_count_at_star`; `real_count_at_p90`, `real_count_at_p10` |
| 16 simulations | `bf.n_sims` |
| 1,915 unscored; 1,653 with ≤3 sequences; smallest scored has 4 | `dropped.missing.n`; `dropped_posthoc.n_missing_le3`, `scored_min_seqs` |
| 18 of top 20; 27 of 41 with ≥1,000 sequences (post hoc) | `dropped_posthoc.top_n_missing`, `n_ge1000_missing/all` |
| 20 universal unscored; names | `dropped.missing.n_universal`; raw/kegg_lists/list_dropped_universal_{a,b}.txt |
| pre-registered flag: no undercount | `dropped.flag_undercount` false (ratio universal 0.38, ratio median size 0.05) |
| Csűrös SI not reachable | PMC article links SI only to pnas.org; pnas.org returned 403 |

## After the cold audit (2026-11-23): one convention, run instability
Source: `experiments/luca_calib/results/realdata/audit_checks.json` (script `realdata/audit_checks.py`). Counts are per-run sums; the text gives the median (range) over 5 runs. These replace the per-family-median sums (33.9, 1,290.6, 1,270.0, 684, 1,118) used before.

| Number in text | Field |
|---|---|
| deposited 1,310 (1,293–1,319); ≥0.75 728 (699–740); ≥0.5 1,139 (1,127–1,147) | `moody_sums`, `moody_ge75`, `moody_ge50` |
| shared weight 1,290 (1,280–1,305); 659 (651–690); 1,082 (1,066–1,103) | `shared_sums`, `shared_ge75`, `shared_ge50` |
| default prior 40.8 (39.4–41.4); 1; 3 (2–5) | `flat_sums`, `flat_ge75`, `flat_ge50` |
| multiplier about 32; 3.1% | `multiplier_moody_over_flat` (31.7–32.8); 40.8/1,310 |
| reported mean 1,298 | Moody et al. (LUCA_PPs.csv sums to 1,297.2: `luca_pps_sum`) |
| 810 families differ by > 0.5; 332 of 684 are ≥ 0.75 in every run | `spread_gt05`; `all_runs_ge75_of_med_ge75`, `med_ge75` |
| 40 of 50 ancient differ by > 0.5 | `pos_spread_gt05` |
| L22 per run 0.04, 0.38, 0.006, 0.001, 0.89; PsaB 0.84–0.91; PsaA 0.002 | `per_run` |
| AUC 93% | `auc_moody` 0.932 |
| young-set limit without PsaB about 19,000 | `w_max_neg_without_psab` |
| BF > 1 / 10 / 100: 1,841 / 749 / 123 | `bf_gt1`, `bf_gt10`, `bf_gt100` |
| inferred-tree band shares 13–14% and 17–20% | `k3_inferred_band_share` |
| per-sim threshold about 2–3 at ≤319 branches, 10 at 639 | `realdata_v7.json` `bf.per_sim` (k4 n160 log10 1.009) |
| log w 5.61–5.77 in run 1 | `results/k1/k1_ci.json` run 1 O_lo/O_hi |
