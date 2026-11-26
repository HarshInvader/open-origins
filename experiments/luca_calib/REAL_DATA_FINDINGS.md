# Real-Data Anatomy & Baseline Findings (Task #32)

> Archived working note from 2026-11-19, committed 2026-11-26 as written. Later work supersedes parts of it: section 4's pilot blocker was resolved, and the calibration results are in K1-K5_RESULTS.md and docs/RESEARCH_STATE.md. Read those for current conclusions.

Generated 2026-11-19 by `extract_real_features.py` (pure stdlib; sealed `pipeline/` untouched).
Outputs:
- `real_features_moody.tsv` (7,456 common KEGG families, 700 genomes)
- `real_features_huang.tsv` (5,322 root-row arCOG families, 257 archaeal genomes)
- `real_baselines_summary.json`
- `calibrate_and_verdict.py` (self-tested on `results/ale_smoke/sim`: PASS)

## 1. Key Discovery: The 10× Single-Domain / Single-Child PP Split (Moody vs. Huang)

Decomposing Moody et al. 2024 (`E_M = 1,290.65`) and Huang et al. 2026 (`E_H = 1,331.00`) by extant domain/root-child presence reveals a stark structural difference in where their ancestral genome sizes come from:

| Stratum | Moody 2024 (`n` / 7,456) | Moody sum PP (`% E_M`) | Moody `PP >= 0.75` | Huang 2026 (`n` / 5,322) | Huang sum PP (`% E_H`) | Huang `PP >= 0.75` |
|---|---:|---:|---:|---:|---:|---:|
| Child A only (Archaea / Eury) | 490 | 171.1 (**13.3%**) | 113 | 753 | 16.0 (**1.2%**) | 1 |
| Child B only (Bacteria / TackA+DPANN) | 2,972 | 195.6 (**15.2%**) | 81 | 584 | 19.5 (**1.5%**) | 0 |
| **Total single-domain / single-child** | **3,462** | **366.7 (28.4%)** | **194** | **1,337** | **35.5 (2.7%)** | **1** |
| Both domains/children, `<= 1%` in rarer | 1,277 | 185.1 (14.3%) | 90 | 291 | 14.9 (1.1%) | 4 |
| Both domains/children, `> 1%` in both (`B2`) | 2,717 | 738.9 (57.2%) | 400 | 3,694 | 1,280.7 (96.2%) | 810 |

- In **Moody 2024**, **28.4% of `E_M`** (`366.7` expected families) and **29.0% of the highest-confidence bin (`PP 0.8–1.0`: `166/573`)** come from **single-domain families** completely absent from either Archaea or Bacteria. Combined with rare cross-domain families (`<= 1%`), **42.8% of `E_M` (`551.8`) sits outside `B2`**.
- In **Huang 2026**, **only 2.7% of `E_H`** (`35.5`) and **0.14% of the `0.8–1.0` bin (`1/710`)** come from single-child families; **96.2% (`1,280.7`)** sits in families present in `> 1%` of both `Eury` (96 genomes) and `TackA+DPANN` (161 genomes).
- **DPANN loss signature in Huang 2026:** Across high-confidence LACA families (`PP 0.8–1.0`, `n = 710`), mean occupancy is **0.366** in DPANN (77 genomes) vs. **0.597** in non-DPANN archaea (180 genomes) — a `0.61×` retention ratio directly reflecting elevated DPANN loss.

## 2. Mechanistic Link to `ale_smoke` (`O_R = 3.555` vs. Flat `O_R = 1`)

In the completed `ale_smoke` control (`true_LUCA = 34`, of which `12` are genuine single-domain LUCA families lost in one domain):
- **Fitted `O_R` (`pp`, `O_R = 3.555`):** `E = 26.71` (`R = 0.786`), single-domain share = **27.3%** (`7.29 / 26.71`), matching Moody's real-data **28.4%**.
- **Flat `O_R = 1` (`pp_flat`):** `E = 16.31` (`R = 0.480`), single-domain share = **5.5%** (`0.90 / 16.31`), close to Huang's **2.7%**.

This gives the main grid a sharp mechanistic test: under zero HGT (`ale_smoke`), Moody's `O_R` reweighting rescues real stem-loss LUCA families; under realistic HGT (`T*`, `2·T*`), stratifying calibration by single-domain vs. `B2` families will show directly whether Moody's `366.7` single-domain expected families are rescued stem-loss LUCA genes or `O_R`-inflated false positives.

## 3. Moody Real-Data Baselines (Prereg v4 §D — Unblocked Locally)

Contrary to `DEVIATIONS.md` #3, B1 and B2 on Moody's real data do not require the Bristol `.uml_rec` download (`Pure_sequences/`, `ArcBacEuk_names.csv`, and `kegg1-5_cons.txt` are all local):
- **B1 (Mrnjavac phylum rule, `>= 50%` in `>= 4` named phyla per domain; 27A / 91B):** **871** families on the 7,456 common set (**922** on all 9,371 FASTA families).
  - Sensitivity excluding tiny phyla (`< 3` genomes; 19A / 19B): **519** families.
- **B2 (`> 1%` in both domains):** **2,717** families on the 7,456 common set (**2,843** on all 9,371).
- **T75d (`PP >= 0.75`, `> 1%` both):** **400** families (Moody published 399 because their script consumed row 1 as a header).
- **T50d (`PP >= 0.50`, `>= 1` genome both):** **819** families.
- **Overlaps:** `B1 ∩ T75d = 208 / 400` (Jaccard `0.196`; `105 / 400` for `B1_ge3`), `B1 ∩ T50d = 363 / 819` (Jaccard `0.274`).

## 4. Operational Blocker Found: `run_pilot.sh` (`fit`) Stopped at 15:24:31

- `results/run_pilot.log` ends at `15:24:24` with `resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown`.
- `results/fit/points/{00,01,02}/gm_00/logs/zombi_Gm.log` are all 0 bytes and `gm_00/zombi/G` only wrote `GenomeParameters.tsv` at `15:24:31` (no writes for 40+ minutes; zero `point.json` checkpoints).
- **Action needed from user's terminal (mamba `phylo` env is outside this chat's connected folder):** restart `experiments/luca_calib/pipeline/local/run_pilot.sh` so `fit` -> `seqscale` -> `pilot` actually run.
