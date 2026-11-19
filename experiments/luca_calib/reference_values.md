# Reference values recorded before any calibration (task #32)

| Target | Source | Value | Reproduction check |
|---|---|---|---|
| E_M (Moody 2024) | median per-family root PP over `kegg1-5_cons.txt`, 7,456 families common to all 5 runs (figshare 10.6084/m9.figshare.24428659) | **1,290.6** | sum of `LUCA_PPs.csv` = 1,297.2 vs their reported mean 1,298.25 |
| E_H (Huang 2026) | sum of `presence` at the root node `Node_GCA-000006805.1_AP024487.1_0` in `Euryarchaeota_root/reconciliations/perspecies_eventcount_per_family_summary.tsv.gz` (Zenodo 18701544), 5,322 families with a root row out of 7,059 | **1,331.0** | PP ≥ 0.5: 1,239, and PP ≥ 0.75: 815, against their reported 1,219 and 800 (+1.6% and +1.9%) |

Decision bands for Huang (v4 §B), as multiples of E_H:
- below 0.67× = below 892;
- 0.8-1.25× = 1,065-1,664;
- above 1.5× = above 1,997.

Recorded 2026-11-19, before any simulation, fitting or calibration.

**Note on Huang's scripts.** Their deposited `0_scripts.zip` has no AleRax command line. Their AleRax options are therefore taken from their methods text and from `model_parameters.txt`, which holds per-species D, L, T and O values.
