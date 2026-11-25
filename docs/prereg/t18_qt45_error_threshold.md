# Pre-registration (T18): can QT45 sustain its own information at its measured fidelity? The error threshold from its own landscape

Status: **draft, not sealed.** Written 2026-11-25. The sections "Design", "Decision rules" and "Calibration fallbacks" were written before the gate's landscape fit and before any planted replicate ran. The gate and the planted kill test were then run (results below). `real` has not been run. The script refuses `real` until `docs/prereg/HASHES.txt` names both `experiments/t18_qt45_error_threshold/scripts/t18_analysis.py` and `scripts/t18_core.py` with their current sha256.

## What has been seen (blinding disclosure)

- **Published by the authors and read before design.** Gianni et al. 2026 (doi:10.1126/science.adt2760), main text and Supplementary Text, "Error threshold computational numerical model", and fig. S32. Their quasispecies model on the same landscape gives "minimal (<0.5%)" active variants at 92.6% and 94.1% fidelity and "~12% of the total population" at 97.4%. Their code (Zenodo 10.5281/zenodo.13891380, `QTribozyme_quasispecies-main-2.zip`) was read, not run.
- **Seen in #30** (`experiments/qt45_epistasis/RESULTS.md`): one isotonic global curve explains the doubles out of sample (held-out R² 0.910 against 0.655 additive); pair terms add nothing; residual sd 1.25 log2 on informative doubles.
- **Seen in the gate (landscape only).** The 4-parameter global-epistasis fit to the real singles and doubles: its floor, top, residual sd and the 132 latent effects. These calibrate the planted landscapes. No threshold, Perron root or population quantity of the real landscape has been computed under any model.
- **The planted landscapes reuse the real latent effects, shuffled across mutation slots and rescaled** (factor 0.5 to 1.6 per replicate). Their planted thresholds are therefore loosely informative about what a QT45-like landscape gives. That is disclosed here; the planted summary reports recovery error, and the planted e* values are in the JSON.
- **The authors' S32B observable is reproduced only inside `real` (step R0)**, because it implies which side of the threshold their model sits on.

## Question and prior art

Full notes: `experiments/t18_qt45_error_threshold/PRIOR_ART.md`.

The core question has already been asked **by the QT45 authors themselves**, on the same data: a deterministic replicator-mutator model over master, all singles, all doubles and a lumped HD ≥ 3 class (fig. S32B). Their verdict: at the measured fidelities the active quasispecies is "minimal (<0.5%)". Three choices in that model are arbitrary and decide the answer:

1. Every HD ≥ 3 genotype and every unmeasured double replicates at 0.01 of WT, and HD ≥ 3 is absorbing. At 94.1% per strand about 5 mutations hit each 44-nt copy per (+) → (−) → (+) generation, so HD ≥ 3 is where most offspring land. The 0.01 sets the answer.
2. The output is the share of genotypes with rate ≥ 0.8 at a grid of fidelities, not a threshold error rate with uncertainty.
3. The background rate (0.01) is the selective superiority the quasispecies has to beat, and the paper says it is "unknown" in self-replication.

Kun, Santos & Szathmáry 2005 (doi:10.1038/ng1621) and Szilágyi, Kun & Szathmáry 2014 (doi:10.1371/journal.pone.0109987) computed phenotypic error thresholds from measured mutational data, but for the Neurospora VS and hairpin ribozymes, not for a polymerase copying itself. No other paper found computes a threshold for a polymerase ribozyme from its own measured landscape.

**What is new here:** (a) a threshold error rate e* with an interval, (b) higher-order mutants modelled from singles and doubles (a fitted global-epistasis model) instead of set to 0.01, with sensitivity variants, (c) a σ-free number, λ_A at the measured error rate, which is the largest background rate QT45's quasispecies can outgrow, and (d) a planted check that the method recovers a known threshold from singles and doubles alone.

**H1 (support).** With higher-order mutants modelled, QT45's measured landscape keeps an active quasispecies at 94.1% per-nucleotide fidelity: e_meas / e* < 1.

**H0 (kill).** QT45 is below its own error threshold at 94.1% even with modelled higher-order mutants: e_meas / e* > 1. The authors' conclusion stands, and the 0.01 assumption was not what drove it.

## Inputs (exact)

| Input | sha256 | Use |
|---|---|---|
| `experiments/qt45_epistasis/raw/combined_single_mutant_fitness.csv` (Zenodo 13891380, MIT; gitignored) | 497564255f02ba18fe2a47d8897856ee3af1821a3ad4f124ba1874fa8ca33e7d | 132 singles, log2 enrichment vs WT |
| `experiments/qt45_epistasis/raw/double_mutant_fitness_all.csv` (same) | 6b0ffea906ad53c21f2400607264a41182c4ef880ae7109d1eacc761a4f2fa18 | 8,346 doubles |
| `experiments/qt45_epistasis/epistasis.py` (#30; imported for `load`, `make_g`, `WT_SEQ`) | 9fda250c736651bccd02a87f66e915ac9ea2259697bde81b477d4d128c512384 | loaders |
| `experiments/qt45_numbers/raw/quasispecies.zip` (authors' model; read, not run) | e698472924706a37c9ebc50ce2ea2e08364357755823f38043dcb3d9108d4ae2 | definitions checked against |

The authors' quasispecies inputs (`data_QT45_v2_singlemut_fitnes.txt`, `..._doublemut_fitnes.txt`) were checked to be value-identical to the two CSVs (133 and 8,347 lines, max difference 0).

**Fidelity (confirmed from the source text).** Main text: "Deep sequencing confirmed the identity of the full-length (-) strand synthesized using the NNN pool, with 10.9% perfect full-length (-) strand sequences, and an average per nucleotide fidelity of 94.1% ( Fig. 4D )". Conditions (Fig. 4 legend): 8 nM primer, 8 nM template, 80 nM QT45, 50 nM each of the 64 triplets, 0.4 mM MgCl₂, 1.2 mM KCl, 1 mM CHES-KOH pH 9, 0.01% Tween 20, 72 days at −7 °C frozen. No confidence interval is given. The hammerhead figure (92.6%, NNN pool, 50 mM MgCl₂, 65 days) and the (+) strand with defined substrates (43.4% perfect reads) are other conditions.

## Design (written before the gate fit and the planted check)

- **D1. Genotype space.** The 44 landscape sites (QT45 positions 2–45; position 1 is the fixed 5′ G) with 4 bases each: the full space of 4⁴⁴ sequences, not a truncation.
- **D2. Replication and mutation.** Rate = 2^(F/τ), F = log2 enrichment vs WT, τ = 1 (the authors' mapping). One generation is (+) → (−) → (+). Each strand copy errs at e per nucleotide, uniformly over the 3 wrong bases, so a site changes with probability u(e) = 1 − (1 − e)² − e²/3 per generation (both strands, as the authors). e_meas = 1 − 0.941 = 0.059.
- **D3. Threshold.** Genotypes with F ≤ log2(w_dead) form an absorbing dead class that replicates at w_dead = 0.01 (the authors' value; no back mutation, as in their lump). The active quasispecies persists iff the Perron root λ_A of the active block of W = QA is above w_dead. **e\*** is the e with λ_A(e) = w_dead. Also reported: **λ_A(e_meas)**, the largest dead-class rate that QT45's quasispecies outgrows at 94.1%, and σ_req = 1/λ_A(e_meas); the single-peak Eigen value is 1/(1 − u)⁴⁴ ≈ 199 (the paper's 166 uses q⁸⁴).
- **D4. Estimator.** Population Monte Carlo of the Feynman–Kac type: N parents, 5 offspring per parent drawn ∝ rate and mutated, dead offspring removed, N survivors resampled. λ_t = mean rate × surviving share; λ_A = geometric mean of λ_t after burn-in. e grid 0.01, 0.02, 0.03, 0.045, 0.06, 0.08, 0.10, 0.125, 0.15, 0.20, 0.25, warm-started, stopped at the first crossing; e* by interpolation of log λ_A against log(1 − u). Real run: N = 20,000, 100 generations (50 burn-in) at the first point and 60 (20) after, plus one refinement point. Bootstrap and variants: N = 10,000. Planted: N = 5,000, 60 (30) and 40 (15), no refinement.
- **D5. Primary model for unmeasured genotypes (method).** Measured values for WT, singles and the 8,346 measured doubles. Everything else (166 unmeasured doubles and all HD ≥ 3) from a latent global-epistasis fit: F = lo + (hi − lo)·logistic(z₀ + Σ aₘ), fitted by least squares to singles, doubles and WT = 0 (three starts, lowest cost). This is the principled form of #30's "one global curve": #30 applied its curve to the sum of *observed* singles, which is not the latent additive scale and saturates at the floor.
- **D6. Uncertainty.** Residual bootstrap, B = 30: add resampled residuals (singles and doubles separately) to the fitted values, floor at the observed minimum, refit, recompute e* (fresh random stream each). 95% interval = 2.5 and 97.5 percentiles (with B = 30 these are close to the second-smallest and second-largest). Censored draws sit at the grid ends. Fidelity enters only through e_meas: R is also reported at 0.926 (hammerhead) and at 0.109^(1/42) = 0.9486 (from the perfect-read share); the decision uses 0.941.

## Decision rules (written before the gate fit and the planted check)

- **D7. Decision quantity** R = e_meas / e\*, primary model, with the bootstrap interval [R_lo, R_hi] = [e_meas / e\*_97.5, e_meas / e\*_2.5].
  - **Support (H1):** R_hi < 1.
  - **Kill (H0):** R_lo > 1.
  - **Inconclusive:** otherwise.
  - **Not decidable:** primary e\* censored (outside 0.01–0.25), or the planted gate failed (F2).
- **D8. Robustness label (reported with the verdict, does not change it).** "Robust" if R falls on the same side of 1 under every variant: V1 authors (HD ≥ 3 and unmeasured doubles = 0.01); V2 #30's isotonic curve on the sum of observed singles; V3 additive in log2; V4 global epistasis without measured overrides; V5 w_dead = 2⁻¹⁰ and 0.05; V6 transitions-only spectrum (G:U wobble errors are the main source in the paper); V7 τ = 0.5 and 2. Otherwise "model-dependent", with the variants named. V1 against primary is the direct test of whether the authors' 0.01 drives their conclusion.
- **D9. R0 (run inside `real`, before R1).** Reproduce the authors' S32B observable under V1: share of the whole population (dead class included) with rate ≥ 0.8. Pass: below 1% at 0.926 and 0.941, between 6% and 24% at 0.974 (published ~12%). The tolerance is wide because our Q differs from theirs in one documented way (see Limits).

## Planted kill test (the gate the coordinator requires)

Synthetic full-space landscapes with a known threshold. The method sees only singles (all 132) and doubles on the real measured mask (8,346), with noise at the real level and floor censoring, and must recover e\*_true.

- **Truth.** z = z₀ + Σ aₘ + Σ pairs Eₘₙ + h(genotype) − h(WT); F = lo + (hi − lo)·logistic(z)^(1/ν), a Richards curve (ν log-uniform in [0.5, 2], so the method's plain logistic is misspecified). aₘ = κ × (real latent effects shuffled across slots) + N(0, 0.2 sd), κ uniform in [0.5, 1.6]. Eₘₙ Gaussian pair epistasis; h a hash-based random field (uncorrelated higher-order epistasis). lo, hi from the gate fit. e\*_true by the same estimator on the truth.
- **Noise (r_d, r_s = gate-fit residual sd of informative doubles and of singles; k̄ = mean slope of the fitted curve over informative doubles).**
  - Family A: all residual as measurement noise (sd r_d, r_s), no epistasis beyond the curve.
  - Family B: residual split in thirds: noise r/√3, pair epistasis and higher-order field each (r_d/√3)/k̄ in latent units.
  - Family C (stress, reported only): as B with both epistasis terms doubled.
- **Criterion (gate).** In each of families A and B, at least 16 of the first 20 scored replicates have |e\*_fit / e\*_true − 1| ≤ 0.20. #30's isotonic variant is also scored on B (reported only).
- **Estimator checks (gate G0).** Single peak: MC e\* within 2% of (1 − u)⁴⁴ = 0.01. Mesa (10 neutral sites, the rest lethal): within 2% of (1 − u)³⁴ = 0.01. Site-independent landscape without killing at e = 0.02: λ within 5% of the exact product of per-site Perron roots.

## Calibration fallbacks (written before the gate fit and the planted check)

- **F1. Global-epistasis fit.** If the three starts do not all report success, or their costs differ by more than 1%, the lowest-cost fit is used and the spread is reported. If no start reports success, V2 (#30's isotonic curve) becomes the primary model, decided before any threshold is computed.
- **F2. Planted test fails** (fewer than 16 of 20 within 20% in A or in B): the failing family is re-run once with N = 20,000 and doubled generations (estimator precision is the only pre-allowed change). If it still fails, `real` is still run but the verdict is reported as "not decidable by this method" and R, e\* and the variants are reported only. No rule, threshold or model is changed after the planted check.
- **F3. Censored planted truth** (e\*_true outside 0.01–0.25): the replicate is not scored; it is replaced by the next replicate index. At most 5 replacements per family; beyond that the family counts as failed.
- **F4. Compute.** If a planted replicate exceeds 10 CPU minutes, planted N drops to 3,000 for all later replicates of all families (reported). Planted parts that die are re-run with the same arguments (replicates are seeded by index).
- **F5. G0 estimator checks fail.** That is a code fault: fix, re-run G0, and record the fix here before any planted replicate is scored. G0 is not tuned after the planted check.
- **F6. R0 fails** in the real run: the result is reported with R0 flagged; the primary analysis is not changed.
- **F7. Disk** (coordinator instruction): outputs are compact JSON; nothing is written that would bring the study above 500 MB.

## Gate results (`gate`; run; passed)

Output: `scripts_out/t18_gate.json`. About 14 CPU s.

| Check | Result | Pass |
|---|---|---|
| G0a single peak | MC e\* 0.05141 vs analytic 0.05145 (0.07%) | yes |
| G0b mesa (10 neutral sites) | 0.06623 vs 0.06626 (0.05%) | yes |
| G0c site-independent, no killing, e = 0.02 | λ 0.1788 vs exact 0.1776 (0.7%) | yes |
| G1 data | 132 singles, 8,346 doubles, WT region 44 nt as #30 | yes |

Global-epistasis fit (F1 not triggered): three starts, all report success, cost spread 2 × 10⁻⁶. lo = −12.11, hi = +5.14, z₀ = 0.896. Doubles: residual sd 0.98 (0.95 on the 4,425 informative doubles, fitted F > −8), R² 0.933; singles: residual sd 0.64. For comparison, #30's isotonic curve on the sum of observed singles gives residual sd 1.15 and R² 0.908 on the same doubles. Mean curve slope over informative doubles 3.83 log2 per latent unit.

An estimator check done before the gate, at N = 2,000 to 40,000 on a site-independent landscape at e = 0.06 (delocalised, mean HD ≈ 24), showed large finite-N bias (λ 0.33 to 0.59 against exact 0.68). That is why the gate checks G0c in the localised regime and why every threshold is defined with an absorbing dead class (D3), where the estimator is accurate (G0a, G0b).

## Planted results (`planted`, `planted_merge`; run; **gate failed in family B**)

Output: `scripts_out/t18_planted_A_*.json`, `t18_planted_B_*.json`, merged in `scripts_out/t18_planted.json`. Settings: N = 5,000, 5 offspring per parent, no refinement (D4). 25 to 80 CPU s per replicate under heavy machine load.

| Family | Replicates scored | Within 20% | Median abs. error | Mean signed error | e\*_true range | Criterion (≥ 16 of 20) |
|---|---|---|---|---|---|---|
| A (noise only) | 20 | **20** | 2.5% | −0.3% | 0.115–0.145 | **pass** |
| B (noise + pair + higher-order field) | 6 (rep 3 censored, F3) | **1** | 27% | **−27%** | 0.154–0.214 | **fail** (5 misses already exceed the 4 allowed) |
| B, #30 isotonic variant (reported only) | 6 | 0 | 32% | −32% | | |
| C (stress) | not run | | | | | |

The B run was stopped after 7 replicates because the criterion could no longer be met: 5 of the first 6 scored replicates miss by more than 20%. All six errors have the same sign: the method **underestimates** e\* in every replicate (−17%, −29%, −23%, −29%, −41%, −26%). C was not run, since it only adds more epistasis to B.

**F2 diagnostic (one replicate, `scripts/t18_diag_f2.py`, output `scripts_out/t18_diag_f2_B1.json`).** Replicate B1 at the F2 precision (N = 20,000, generations 120/60 and 80/30): e\*_true 0.1764, e\*_fit 0.1361, error **−22.8%** (−28.7% at N = 5,000). More precision does not remove the bias. The same truth with the higher-order field removed (pair epistasis kept) gives e\*_true 0.1739. Almost all of the rise therefore comes from **pair epistasis**, not from the higher-order field.

**Reading.** When the landscape is the global curve plus noise (A), singles and doubles pin the threshold to a few percent. When a third of the double-mutant residual is real pair epistasis (B), the true threshold rises (about 0.15 to 0.21, against about 0.13 in A). The global-curve model misses the rise.
- **Why the model misses it.** Pair terms that are small in any one double (sd 0.14 latent units; #30 found they add almost nothing to out-of-sample R² on doubles) add up in genotypes with many mutations. A genotype with m mutations carries m(m−1)/2 pairs, and at the threshold the quasispecies sits around 4 to 6 mutations from WT. The extra latent variance among those genotypes lets some survive, which raises e\*.
- **What this does not mean.** It is not an identifiability limit of HD ≤ 2 data. The pair terms are measured, one per double, but the primary model throws them away as noise.
- **Direction.** In every B replicate the method underestimates e\*, so it errs conservatively (toward kill).

**Consequence under the rules stated in advance (F2).** F2 allows one re-run of the failing family with N = 20,000 and doubled generations. The full re-run (20 replicates, about 15 to 20 CPU min each under current load, about 5 to 7 core hours) has **not** been run, by coordinator instruction (no long runs). The B1 diagnostic says it would fail. If the coordinator runs it and it fails, `real` may run, but its verdict is "not decidable by this method" and R is reported only. No rule is changed here.

**Proposed, not adopted.** Each would be a change after calibration, so none can decide this study. Each needs a new prereg (T18b) with its own planted test.
1. **Model change.** Keep the measured pair terms (each double's residual from the curve, shrunk toward 0 by its replicate noise) and add them to the latent sum for HD ≥ 3 genotypes. The doubles measure exactly the pair terms that drive B's rise.
2. **One-sided rule.** "Support" if R_hi < 1, since the method underestimates e\*; "kill" is not reachable. This must first be shown to hold in planted families whose epistasis is mostly negative, which B's symmetric terms do not test.

## Limits

- **Cis-replication assumption.** Rate = own activity assumes each polymerase copies itself (compartments, tethering). In a well-mixed pool dead sequences are copied by active ones as templates (the parasite problem; Higgs 2026). The quasispecies threshold is then not the binding constraint.
- **Activity is a proxy.** The landscape measures one round of a ligation/extension selection, not self-replication (the authors make the same caveat).
- **Dead-class rate.** w_dead is not measured. λ_A(e_meas) is reported so a reader can apply any value.
- **Uniform per-site fidelity.** Positional fidelity (Fig. 4D) and the per-read error distribution are not used; the transitions-only variant brackets spectrum effects.
- **Authors' Q.** In the authors' code, transitions out of a mutant use the single-strand table (`dmut_mean`) where those out of the master use the composite two-strand table, so mutants copy more accurately than the master (factor 0.941/0.885 per mutated site at 94.1%). Our Q uses the composite rate everywhere. This is why R0's tolerance is wide.
- **Far-away genotypes.** T13 found that one global curve misses neutral variants far from WT (generation 8 recall 0.1%), which makes the primary model, if anything, pessimistic for distant genotypes.
- **Finite-population estimator.** A Monte Carlo estimate with O(1/N) bias; G0 and the planted test measure it.
