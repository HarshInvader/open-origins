# Pre-registration K7: is K5's stem-transfer adversary realistic? (draft, not sealed)

**Status.** Draft written 2026-11-25, before any K7 measure was computed on any world, simulated or real. Not sealed and not hashed: sealing is the coordinator's call. Nothing in this file may change after the first calibration number exists, except by a dated deviation that says so; any other change after calibration makes K7 INVALID.

**Computed before writing.** Only structure checks, no measure:
- the measure parser was run on two simulated `.uml_rec` files and on one of Moody et al.'s deposited files (K15358, run 1), to check that the root and the two stems are found and that transfer tokens parse;
- Moody et al.'s focal (constrained) species tree: the root splits 350 Archaea from 350 Bacteria (taxonomy file `ArcBacEuk_names.csv`), so their two root-child branches are the LACA and LBCA stems;
- the laptop ALE crash threshold, from the existing seed-1 run: families with up to 152 sampled genes run; every family with 153 or more fails in ALEobserve (DEVIATIONS 11-12 of `experiments/luca_calib`).

## Question
K5 (`experiments/luca_calib/K5_RESULTS.md`) found that the pipeline (Zombi world, ALE, Moody et al.'s fitted root weight) cannot tell a big LUCA from a small LUCA plus about 250 stem-born families that crossed between the domains early. The crossing rate there was 115-600 times the background transfer rate. Is crossing on that scale consistent with what Moody et al.'s own reconciliations show about transfer on the two domain stems?

## Prior art (opened)
- **Moody et al. 2024, Supplementary Data 5** (Nature site, `41559_2024_2461_MOESM8_ESM.csv`) gives transfers received per copy at the LACA and LBCA nodes: 0.164 and 0.24, against 0.229 for the mean over all nodes and 0.413 for the 95th percentile. At face value the stems receive transfers at about the background rate (0.72× and 1.05× the mean). That number has not been calibrated against known truth: K5 shows that ALE can absorb stem traffic into root presence, which would leave this ratio low even if the traffic were heavy. K7 asks whether the ratio (and a donor-based version) would rise if the traffic were there.
- **Moody et al. 2024, Supplementary Information** ("Reconciliation caveats") states the identifiability limit in words: a gene born on one stem and transferred to the other before the radiations "will appear to map to LUCA in any phylogenetic analysis". It gives no rate.
- Davín et al. 2018, Williams et al. 2017 and Williams et al. 2023 (library entries, read earlier) use ALE transfers for dating, rooting and parameter estimation. None estimates a stem or inter-domain transfer rate, and none calibrates one against simulation.
- Moody et al. 2022 (eLife, abstract read) and Martinez-Gutierrez & Aylward 2021 (MBE, abstract read) show inter-domain transfer in marker genes; neither gives a stem rate from reconciliations.

## Measures
Computed by `experiments/k7_realism_bound/k7_measure.py` from `.uml_rec` files only, never from simulation truth. The two stems are the two branches below the root of the species tree in the `S:` line. A transfer token `T@d->g` in the 100 sampled reconciled gene trees is *inter-domain* when d and g lie in different stem clades. Every count is divided by the number of samples (a posterior expectation). Sums run over all reconciled families of a world (or of one Moody run).

- **M1 (primary, donor-based).** I_stem = Σ inter-domain transfers with a stem as donor / Σ presence on the two stems. I_int = Σ inter-domain transfers with an internal, non-stem, non-root donor / Σ presence on those branches. **M1 = I_stem / I_int.**
- **M2 (secondary, received, Supplementary Data 5 style).** R_stem = Σ Transfers (ALE's received count) on the two stems / Σ copies on the two stems. R_all = the same over all non-root branches. **M2 = R_stem / R_all.**
- Uncertainty: 1,000 bootstrap resamples of families (numpy seed 7), 95% percentile interval.

Both are ratios to the same tree's background, so they do not need branch durations, which undated ALE ignores.

## Planted test (the kill test, run first)

### Worlds
- **Sources:** the K3 Linux true-tree simulations of seeds 1 and 3, the two seeds K5 read (80 genomes per domain, transfer 0.4). Kept families: K5's rule, 20 root families (`stemsim.kept_rows`, rng [seed, 999]) plus every non-root family. Their existing Linux `ale_true` reconciliations are reused.
- **Stem-born families:** N = 250 in every world (between K5's matched 225 and 275). Simulated with `experiments/luca_calib/k5/stemsim.py` (imported, not modified): birth point uniform by length on the stems, Zombi Gm rates, and extra stem traffic at rate x per copy on a stem to a lineage of the other domain's clade.
- **Ladder:** x = m × 0.4 (the background mean transfer rate), m ∈ {1, 10, 50, 150, 600}. K5's adversary was m = 605 (seed 1) and 116 (seed 3).
- **Pairing:** family i draws its birth point and rates from rng [seed, i], as in K5, so families are paired across rungs and with K5. Its events use rng [seed, 7000 + m, i].
- **References (no new ALE):** the control world (K5's N = 0 world) and the big world (K3 as is).
- **Reconciliation:** `experiments/luca_calib/pipeline/run_ale.run_family`, imported unchanged: ALEobserve on the true tree, then ALEml_undated with 100 samples, seed 1, `separators=_`, flat origination. Linux build for the full test.

### Pass bar (per measure; must hold on both seeds)
- **P1, order:** M(50) < M(150) < M(600), and M(1) < M(150).
- **P2, separation at K5's boundary:** the upper 95% bound of M at m = 50 is below the lower 95% bound at m = 150.
- **P3, cross-seed recovery:** invert this seed's M at m = 50, 150 and 600 on the other seed's curve (linear interpolation of log M against log m). Each recovered m̂ is within a factor of 2 of the planted m. This implies that 50× reads as at most 100× and 150× as at least 75×.

A measure that meets P1-P3 has *passed*. Also reported, not part of the bar: M at m = 1 against the control world, the share of stem-born families with ≥ 0.5 expected stem-donor inter-domain transfers, ALE failures per world, and K5's realized cross-domain transfers per family.

### Portability (needed for the real-data rule, from existing outputs only)
- **Size:** M in the big world at 20, 40 and 80 genomes per domain (K2 cells n20/n40/n80 at transfer 0.4; laptop ALE, families over 152 genes missing, disclosed).
- **Gene-tree error:** M with inferred against true gene trees, K3 seeds 2 and 3 (Linux).
- **F** = the largest ratio between any two of these values, taken ≥ 1. Moody et al. used 1,000 UFBoot trees per family on a 700-genome tree, so their M is widened by F before it is read.

## Decision rule on Moody et al.'s data (only after a measure has passed)
- **Data:** the 5 constrained (focal topology) runs in `Constrained_recs_archive.zip`, data.bris doi:10.5523/bris.405xnm7ei36d2cj65nrirg3ip, the run-level `.uml_rec` files (the COG-category subfolders are copies of them). Read by HTTP range request, one member at a time; only per-family summaries are kept.
- **Reproduction check first:** our per-stem T/copies must come within 15% of Supplementary Data 5 (LACA 0.164, LBCA 0.24). A miss is reported, and the measures are still computed our way on both sides.
- **Observed band:** M_obs is the median of the 5 runs. The band is [lowest 2.5% bound over runs / F, highest 97.5% bound × F].
- **Mapping:** the band is mapped to m on the curve pooled over the seeds (mean log M at each m, linear interpolation in log-log). Below the m = 1 rung it reads "≤ 1"; above m = 600 it reads "> 600".
- **Verdict:**
  - **Below K5's adversary range:** upper m̂ < 115. Add "and below 50×" if upper m̂ < 50.
  - **Inside or above:** lower m̂ ≥ 115.
  - **Undecidable:** the band straddles 115, or F > 3.
- **Scope:** m̂ is a multiplier-equivalent at K5's stem-born share (N = 250 against the world's other families) in an 80-per-domain world. It is not a time rate on Moody et al.'s stems, whose durations are unknown.

## Fallbacks, stated before calibration
1. If M1 passes, M1 is used. If only M2 passes, M2 is used. If neither passes, K7 stops with "reconciliation-based stem measures cannot recover the planted multiplier, so the realism bound is undecidable with this pipeline". No verdict is computed on Moody et al.'s data; only the Supplementary Data 5 face values are reported, with that caveat.
2. ALE failures: if more than 5% of a world's stem-born families fail on Linux, the measure is computed without them and the share is reported. If more than 10% fail, that world is invalid. The bar is then judged on the remaining rungs only if m = 50 and m = 150 are both valid; otherwise K7 is incomplete.
3. If seed 1 or 3 cannot be built or run, seed 2 replaces it; with fewer than 2 seeds K7 is incomplete.
4. No other change after calibration. A rung, N, measure or threshold changed after any calibration number exists makes K7 INVALID.

## Pilot (laptop; not part of the bar)
Seed 1 only, rungs m ∈ {1, 50, 150, 600}, N = 250 built; ALE is run only on stem-born families with index i < 125 (the same indices at every rung, so they stay paired). That cut was made on 2026-11-25 after the first m = 1 chunk, from its run times alone and before any measure was aggregated or read: all 250 would take about 2.5 thread-hours at the laptop's current load (about 25 on 10 cores). Laptop ALE (`ext/ale_build`), `taskpolicy -b nice -n 20`, OMP_NUM_THREADS=1, short foreground chunks. Background families come from the laptop seed-1 `ale_true` (57 families over 152 genes are missing there). Stem-born families with more than 152 sampled genes at a rung are skipped at that rung and counted. The pilot is descriptive: it checks that the code runs end to end, gives a compute estimate, and can flag a showstopper such as a flat M. Because the skipped large families are the ones most likely to carry stem traffic, a flat pilot is a warning, not a kill. Outputs go to a scratch directory outside the repo; only a compact JSON summary is kept.

## Compute (full test, Linux)
- Stem-born ALE per world: about 0.9 core-hours at m = 600 and 0.5 at m = 150, from K5's s1 λ4 and λ1 timings; less at lower rungs. About 2 core-hours per seed, 4-5 for two seeds.
- The seed-1 Linux big-world `ale_true` must be present (K5 re-ran it on AWS) or re-run (about 0.7 core-hours).
- Moody et al.: about 6.6 GB streamed, a few core-minutes of parsing.

## Run plan for the full planted test (2026-11-26, before any full-test reconciliation)
- **Where.** On free GitHub-hosted Linux runners, approved by the coordinator at no spend (`experiments/k7_realism_bound/runner/README.md`). Nothing in the method changes. The settings are the prereg's: N = 250, m ∈ {1, 10, 50, 150, 600}, no size cap, `run_family` unchanged, 100 samples, seed 1.
- **Seed 3's source world.** Its Zombi species-tree files never came back from AWS. They were rebuilt by re-running the seeded species-tree step with K3's settings. The resulting sampled species tree and domains are byte-identical to the stored ones.
- **Seed 1's background.** Its Linux reconciliations stayed on AWS, so the background is re-run on Linux (the prereg allows this, about 0.7 core-hours).
- **Gates.**
  - The runner's ALE must first reproduce 12 stored AWS Linux reconciliations byte for byte.
  - Every world must match the laptop build exactly.
  - If either gate fails, the run stops and is reported.
- **Nothing read.** No full-test measure has been computed or read. The pilot result (seed 1, laptop) is as reported above.
