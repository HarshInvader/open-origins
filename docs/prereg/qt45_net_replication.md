# Pre-registration: QT45 net replication per cycle (board task #2)

Agent: orig-2. Written 2026-11-18.

**Disclosure.** I read the published yields (main text and SI) before writing this. So this is not a blind test. It fixes the arithmetic, the decision rule and the sensitivity range before I run `net_replication.py`.

## Question
Using the published QT45 yields and decay rate, does a QT45 strand population grow (λ > 1) or shrink (λ < 1) per replication cycle?

## Source
Gianni et al. 2026, Science 391:1022, doi:10.1126/science.adt2760 (author manuscript PMC7618777, with SI). Inputs taken from it:
- Full-length yields over 72 days:
  - (−) strand: 0.24%, all-64-triplet pool;
  - (+) strand: 0.17%, defined triplets plus one hexamer.
- Perfect full-length read fractions: 10.9% for (−) and 43.4% for (+).
- Reaction composition: 8 nM primer, 8 nM template, 80 nM ribozyme.
- Decay: k = 0.0059 per day (t½ ≈ 117 days), SI fig. S8. It was measured at 50 mM MgCl₂, not the 0.4 mM MgCl₂ used for self-synthesis.

## Model
A linear two-strand model per 72-day step: x₊' = S(x₊ + Y₊x₋) and x₋' = S(x₋ + Y₋x₊), with S = exp(−k·72).
- λ_cycle is the square of the leading eigenvalue.
- This is generous to QT45:
  - each strand step is assumed to happen at the published yield, in the same pot, with no strand inhibition;
  - substrates are assumed not to run out;
  - full-length product counts as a copy whether or not it is correct.
- A stricter variant counts only perfect copies.

## Decision rule
- **λ_cycle < 1 at the published half-life, and also at a 10× longer half-life:** "below 1 per cycle".
- **λ_cycle ≥ 1 only if decay is ignored:** say so.
- Also report:
  - the break-even yield;
  - the fold improvement needed;
  - the half-life needed for λ = 1.

## Second-hand figure
Check the claim of a "0.02% gain over 72 days". Compute the yield per template and per ribozyme molecule (ribozyme at 10× template) and say which, if either, gives 0.02%.

## Planted check
An ODE simulation of the same two-strand system with known rates. The matrix and analytic growth factors must match the ODE to a relative error below 1e-4.
