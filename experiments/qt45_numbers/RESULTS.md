# QT45: net replication is far below 1 per cycle (task #2)

**Verdict.** On its published numbers, a QT45 strand population shrinks.
- **Per cycle:** each full cycle ((+) → (−) → (+), 2 × 72 days) has a growth factor λ ≈ 0.43. Hydrolysis loses about 35% of the RNA every 72 days, while synthesis adds only about 0.2%.
- **To break even:** the geometric-mean full-length yield would need to reach about 53% per 72 days. That is about 260 times the published yields.
- **Ignoring decay:** synthesis alone gives λ = 1.004 per 144 days. That is 4.1 × 10⁻⁶ new (+) strands per (+) strand per cycle.
- **The 0.02% figure:** "0.02% gain over 72 days" is the yield per ribozyme molecule (0.24% × 8 nM template / 80 nM ribozyme = 0.024%). Per template it is 0.24%. The paper reports ~0.2%, per template.

QT45 is still the first ribozyme shown to make both its own strands (L2 on our ladder). It is nowhere near L3, sustained self-replication. The authors say as much ("slow and low-yielding"); this puts a number on the gap.

## Inputs
Source: Gianni et al. 2026, Science 391:1022-1028, doi:10.1126/science.adt2760. I verified the DOI and read the author manuscript and SI on PMC7618777 via Europe PMC.

| Quantity | Value | Where |
|---|---|---|
| (−) strand full-length yield | 0.24% in 72 days (all-64 triplet pool) | main text, Fig. 4C |
| (+) strand full-length yield | 0.17% in 72 days (defined triplets plus one hexamer, pppAUUGAU) | main text, Fig. 4C |
| Perfect full-length reads | 10.9% for (−) with the NNN pool; 43.4% for (+) with defined substrates | main text |
| Per-nucleotide fidelity | 94.1% for (−) synthesis; 92.6% for hammerhead synthesis | main text |
| Reaction | 8 nM primer, 8 nM template, 80 nM ribozyme; 50 nM each substrate; 0.4 mM MgCl₂, 1.2 mM KCl, 1 mM CHES-KOH pH 9; −7 °C frozen; 72 days | Fig. 4 legend |
| QT45 decay | k = 0.0059 per day (t½ ≈ 117 days), measured at 50 mM MgCl₂, pH 9, −7 °C | SI fig. S8 |
| Hammerhead (33 nt) synthesis | 1.88% (defined triplets) and 0.39% (NNN) in 65 days | main text |
| Abundance of QT folds in random RNA | 9.5 × 10⁻¹⁷ | main text, SI |

## Calculation (`net_replication.py`, output in `results_calc.json`)
The model has two strands per 72-day step: x₊' = S(x₊ + Y₊x₋) and x₋' = S(x₋ + Y₋x₊), with S = e^(−72k).

| | Value |
|---|---|
| Survival per 72 days, S | 0.654 |
| λ per cycle (144 days), counting all full-length product | **0.429** |
| λ per cycle, perfect copies only | 0.428 |
| λ per cycle with no decay | 1.004 |
| Break-even geometric-mean yield per 72 days | 0.53 |
| Fold improvement in yield needed | 262× |
| Decay rate ÷ synthesis rate | 210 |
| Half-life needed for λ = 1 at today's yields | about 24,700 days (68 years) |

Sensitivity to the decay rate:
- The half-life was measured at 50 mM Mg²⁺. The self-synthesis buffer has 0.4 mM, so real decay may well be slower.
- λ_cycle is 0.66 at t½ = 234 days, 0.82 at 500 days, 0.91 at 1,000 days and 0.98 at 5,000 days.
- It stays below 1 for any half-life under about 68 years.
- The verdict holds across a 10× and even a 40× longer half-life.

Recomputed from SI fig. S32: the Eigen error threshold for an 84-nt genome (both strands) at q = 0.941 needs a selective superiority s > q^(−84) = 165, matching the paper's 166. Only 0.6% of copies of the 84-nt genome would be error-free.

**This is generous to QT45.** Real self-replication would add three things the model leaves out:
- the (+) and (−) reactions run in one pot;
- strand inhibition, which the paper shows is the key obstacle and which needed a pre-made hexamer to overcome;
- triplet consumption.

## Planted check
An ODE of the same linear two-strand system with known synthesis and decay rates recovers the analytic growth factor to a relative error of ≤ 3 × 10⁻⁵ (pass, under 1e-4).

The discrete matrix formula used above agrees with the ODE when yields are small, as here. It diverges at yields of 30-90% (1.29 vs 1.37), so it should not be reused for high-yield systems.

## Context (not a QT45 result)
Attwater et al. 2025, Nat Chem 17:1129, doi:10.1038/s41557-025-01830-y (verified; read via PMC12226338):
- A larger triplet polymerase ribozyme (TPR) under pH/freeze-thaw cycling replicates short double-stranded RNAs exponentially, at about 1.2-1.38-fold per cycle.
- It amplifies a fragment of itself by up to 1.26-fold per cycle.
- So exponential replication exists for short templates copied by a separate, larger catalyst.

What is missing is a ribozyme that copies itself at λ > 1. QT45 is the closest candidate, and it is about 260× short in yield.

## What was not checked
- I did not re-quantify gels. The Dryad sequencing data and the Zenodo deposit (doi:10.5281/zenodo.13891380: 2.3 GB fitness landscape, 0.86 GB optimised landscape, 57 MB fidelity, 330 MB hammerhead fidelity, 191 kB quasispecies model) were not downloaded, except the 191 kB model (code not run; it is in raw/).
- Yields are single end-point values; the paper gives no time courses for self-synthesis, so the per-day rate assumes linear accumulation.
- The decay constant comes from a different buffer.
- "Cycle" here means two 72-day reactions. Attwater-style 20-day freeze-thaw cycles were not modelled for QT45 itself; the paper shows only a short duplex for that (SI fig. S31).

## Hypotheses table
| Hypothesis | Status |
|---|---|
| QT45 net replication ≥ 1 per cycle at published yields and decay | **Rejected** (λ = 0.43) |
| …even if decay is 10× slower than measured | Rejected (λ ≈ 0.91) |
| "0.02% gain over 72 days" is the per-template yield | Rejected: it is the per-ribozyme yield (0.024%); per template it is 0.24% |
| QT45 is above the Eigen threshold at 94.1% fidelity | Only if s > 165; untested |

## Files
- `net_replication.py`
- `results_calc.json`
- `results.json`
- `ledger_rows.csv`
- `raw/`: paper XML/text, SI PDF/text, Attwater 2025 XML, quasispecies zip
- Pre-registration: `docs/prereg/qt45_net_replication.md`. It was written after reading the inputs (disclosed there) but before running the calculation.
