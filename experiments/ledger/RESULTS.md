# Intervention ledger (task #29): killed by its own sealed criterion. Two blind encoders do not agree on how to score published routes.

**Verdict: negative, and the kill rule fired.**
- The prereg (`docs/prereg/intervention_ledger.md`, sha `528b9d13`) stops the study if blind encoders agree with kappa below 0.6. On the hand-offs that could be aligned, kappa is **0.22** (agreement 4 of 7). With the NaN-tolerant scorer it is −0.31.
- The encoders did not even split routes the same way. Steps per route differed in 4 of 6 routes: Becker 2019 has 5 vs 4 hand-offs, Xu 2020 3+1 vs 4, Ritson 2022 1 vs 4, Gibard 2018 0 vs 1.
- Only Becker 2018 and Yi 2020 lined up, giving 7 hand-offs.
- The sealed predictions P1-P6 are therefore not interpreted as findings. Their values are below for the record.

## The insight, which is the real result
1. **The literature does not report enough to check pH continuity.** pH can be checked at only **2 of 20** hand-offs (encoder B) and **4 of 17** (encoder A). Temperature is checkable more often (11/20, 15/17).
   - So the claim from the earlier map, that breaks are never pH or temperature, is mostly a statement about what papers leave out. Red team #21 found the same.
   - This extends Richert's 2018 call (doi:10.1038/s41467-018-07219-5): the number of interventions cannot even be counted reliably from published methods, because the conditions at each hand-off are not reported.
2. **Most of the disagreement comes from how a route is cut into steps, not from the chemistry.**
   - On the old routes, the red team was given the step list and agreed with kappa 0.82 (#21).
   - Here each encoder chose the steps from the paper, and agreement fell apart.
   - A ledger like this needs a fixed, shared step list per route, set by the authors or by a third party, before anyone scores it.
3. **The rule's "process error" flag (F7) is the commonest hard fail** (13 of A's flags, 7 of B's). Most of these come from unreported pH entering a range check, the NaN artefact found in red teams #21 and #27. They measure missing data, not chemistry.

## Sealed predictions, as scored (not interpreted)
| | Encoder A (primary) | Encoder B (primary) | Prediction | Status |
|---|---|---|---|---|
| P1: at most 3 hand-offs with no hard fail | 1 of 17 | 9 of 20 | ≤ 3 | encoders disagree |
| P2: every pass is a same-pot, no-workup hand-off | 0 of 1 pass | 0 of 7 passes | all | fails in both |
| P3: at least 90% of broken hand-offs fail only on F3/F4/F6 | 12% | 27% | ≥ 90% | fails in both (F7 dominates) |
| P3b: no F1/F2-only fail | 0 | 0 | 0 | holds, but pH is checkable at only 2-4 hand-offs |
| P4: Yi 2020 radiolysis → dry-down → azoles has no hard fail | F2 and F7 | passes | pass | encoders disagree; A encoded `same_pot` with no heating |
| P5: Becker 2018 fails at ribose entry (not blind) | F4 at B5→B6 | F4 at B2→B3 | F4/F6 | holds in both, at different steps |

With the NaN-tolerant scorer (sensitivity), P3 is 33% for A and 67% for B, still under 90%.

The order-shuffle null was not run on these routes: the study was stopped first, and red team #21 already showed the rule cannot see step order.

## Process
- Planted controls passed 28/28 before scoring. The rule, scorer and wrapper are unchanged.
- Encoder A (Opus) and encoder B (Sonnet) worked blind to each other and to the prereg. Their file hashes were recorded before scoring:
  - A: `b77959e6…`
  - B: `deb58166…`
- R7 (Becker 2019) was encoded from a university accepted-manuscript copy, and R11 from the NIH author manuscript, both legal open copies.
- Some supplementary files were blocked (bot checks, 403); those values are NaN.

## What would rescue the idea
A fixed step list per route, agreed before encoding, ideally by the authors themselves. Plus a reporting checklist for prebiotic papers: pH, temperature, concentration and solvent at the end of every step, and an explicit "carried over vs freshly added" flag for each input. The checklist could be a short contribution in its own right, but it is a proposal, not a result.

Files:
- `score_ledger.py`;
- `results.json`;
- `enc_A/`, `enc_B/` (steps, NOTES.md, SHA.txt).
