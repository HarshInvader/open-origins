# Paper Blueprint: Simulation-Calibrated LUCA & LACA Genome Reconstructions (Task #32)

> Archived planning note from 2026-11-19, committed 2026-11-26 as written. It is not a current plan: the project rule is results first, papers later, and the LUCA calibration results since then (K1-K6, docs/RESEARCH_STATE.md) change the pitch. Venue names are placeholders for the owner.

**Working title:** *Simulation calibration of probabilistic gene-tree–species-tree reconciliation at LUCA depth*
**Target venues:** *Nature Ecology & Evolution* (direct reply/companion to Moody et al. 2024) or *PNAS* (direct resolution of the 2026 Csűrös vs. Szöllősi/Williams debate).

---

## 1. Core pitch (why leading groups will care)

A live 2026 dispute splits the deep-evolution field on whether probabilistic reconciliation (ALE/AleRax) **overstates** or **understates** early cellular complexity:
- **Moody et al. 2024** (*Nat Ecol Evol* 8:1654, `10.1038/s41559-024-02461-1`) inferred a complex 2,657-protein LUCA from 700 genomes and 9,365 KEGG families (399 confident KOs at PP ≥ 0.75; 1,298 expected KOs from PP sums across 7,467 families), without simulation validation.
- **Csűrös 2026** (*PNAS*, `10.1073/pnas.2537812123`) and **Gagnon & Csűrös 2026** (*PNAS*, `10.1073/pnas.2619901123`) argue ALE at 700-genome scale hallucinates HGT and collapses LUCA to ~45 confident genes.
- **Szöllősi & Williams 2026** (*PNAS*, `10.1073/pnas.2618431123`; *bioRxiv*, `10.64898/2026.09.03.749268`) argue the opposite: reconciliation systematically *underestimates* deep ancestors (FNR 0.5–0.9), but tested only injected presence/absence noise rather than phylogenetic simulation.
- **Huang et al. 2026** (*Nat Commun* 17, `10.1038/s41467-026-76386-7`) showed that global loss rates create small-genome attraction in AleRax over 257 archaea (DPANN loss 0.40–0.45 vs. 0.26–0.27), shifting LACA size, again without simulation truth.

**The gap we close:** The first pre-registered, end-to-end phylogenetic simulation at LUCA depth (complete birth-death trees with extinct/unsampled ghost donors, fitted to Moody's real occupancy/divergence statistics, saturated sequence evolution with model misspecification WAG → LG+G4, IQ-TREE UFBoot distributions, Moody's exact `ALEml_undated` + `O_R_Optimization.py`, and Huang's clade-wise AleRax) calibrated directly onto both published real-data endpoints (`E_M = 1,290.6` and `E_H = 1,331.0`).

---

## 2. Figures & tables (mapped 1:1 to pipeline outputs)

1. **Figure 1 — Simulation realism & planted control (fit check + v3 gate).**
   - Panel A: Fitted Zombi Gm occupancy histogram, both-domain share, and pairwise p-distance vs. Moody's 700-genome real data (`real_stats.json` vs. `results/fit/fit.json`, `results/seqscale/seqscale.json`).
   - Panel B: Planted control (`control_s1`) showing identifiable-LUCA T50 recall ≥ 0.90 vs. unidentifiable one-domain LUCA loss.
2. **Figure 2 — Thresholded content vs. PP-summed genome size across transfer regimes (P1–P5).**
   - Panel A: Recall and precision of T75, T50, T75d, T50d, and baselines B1 (Mrnjavac) / B2 (>1% both domains) across `0.5·T*`, `T*`, `2·T*` (inferred vs. true trees; fitted `O_R` vs. flat `O_R = 1`).
   - Panel B: Size ratio `R = E / true LUCA` (showing whether diffuse low PPs inflate `E` even when T75d is conservative) + reliability curve across PP bins (0–0.2 … 0.8–1.0 and 0.4–0.6 for P5).
   - Panel C: Stem-to-stem transfer share of false T50d calls (v4 §C, Wehbi et al. 2026 diagnostic).
3. **Figure 3 — Lineage-varying loss stress test (Arm L, P7).**
   - Global-rate ALE (`armL_s11..13`, fast-clade loss ×1.6) vs. clade-wise AleRax (`alerax_H_inferred`): shows whether global-rate calibration holds or breaks under DPANN-like rate heterogeneity.
4. **Figure 4 — Calibrated real-data LUCA (Moody 2024) and LACA (Huang 2026) sizes (P6, P8).**
   - Forest plot of uncalibrated `E_M = 1,290.6` vs. calibrated `C` across `0.5·T*`, `T*`, `2·T*`, pooled, and union span against sealed decision bands (`<865` overstated, `1,032–1,613` validated, `>1,936` understated), alongside `B1`, `B2`, and high-confidence `p̂ ≥ 0.75` vs. 399.
   - Companion panel for Huang 2026 `E_H = 1,331.0` vs. `C_H` against `<892 / 1,065–1,664 / >1,997`.

---

## 3. Two reviewer-killer additions to run right after `run_main.sh`

1. **Taxon-scaling sensitivity curve (pre-empts the "80 vs. 700 genomes" objection):**
   - Run 1 replicate each at `n_per_domain ∈ {20, 40, 80}` (40, 80, 160 tips) at `(L*, T*)` and plot `R(n)` and `T75d recall(n)` to show whether bias is monotonic or already saturated by 80 tips.
2. **50-family Moody ALE parity check (`DEVIATIONS.md` #3):**
   - Retry Bristol `.uml_rec` download (or rerun `ALEml_undated` on 50 Moody UFBoot gene-tree files from `Supp_data` if present) to confirm mean |ΔPP| ≤ 0.05 against Moody's deposited consensus PPs.

---

## 4. Companion deliverables (secondary, only after #32 is submitted)

- **QT45 saturation note:** Short methods letter from `experiments/qt45_epistasis/RESULTS.md` showing that global floor saturation (−14 log2) lifts held-out R² from 0.655 to 0.910 while pairwise epistasis adds only +0.0005. Pair with human-lead outreach to the Holliger lab on QT45 structure / sealed variant testing.
- **Cross-paper prebiotic hand-off table:** Freeze blind-coding; reopen only if route authors verify fixed step tables (`F4`/`F6` cross-paper breaks + carried-product concentration gap 59% vs. 89%).
