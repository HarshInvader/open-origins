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
