# T1 results: is LUCA's core metabolism specifically exergonic under alkaline-vent conditions?

Prereg: `docs/prereg/t1_vent_exergonic.md` (sealed ff2efbe). One deviation was logged before the real run: T1-1, a D4 σ filter in the gate (`DEVIATIONS.md`).
Script: `scripts/t1_analysis.py` (sha256 6c4888ba…). Output: `scripts_out/t1_real.json`. Seed 20261124. Software: eQuilibrator 0.8.1, component-contribution 0.8.0.

## Answer

Wimmer et al. (2021) report that most of LUCA's core reactions are exergonic at vent conditions. We reproduce that number: 96.5% of the core is exergonic at pH 9 and 80 °C with a 100-fold product gradient. The number does not show anything specific to LUCA or to vents.

- **Direction (kill).** Reverse every core reaction and apply the same gradient, and 62.1% are still exergonic (Monte Carlo 95% interval 61.1–64.3). The kill line was 50%. The high share comes mostly from the assumed concentration gradient, not from which way the reactions run.
- **Specificity (kill, both pools).** At equal concentrations at the vent cell, the core is *less* exergonic than matched non-core reactions:
  - N1 (Rhea): 71.7% vs 80.0%. Gap −8.4 points, 95% CI −15.4 to −2.0.
  - N2 (Xavier S4): 71.7% vs 82.7%. Gap −11.0 points, 95% CI −18.1 to −4.7.
- **Setting (kill, both pools).** The vent-minus-pond advantage of the core over the null is:
  - N1: +2.2 points, 95% CI 0.0 to 5.1. The CI touches 0, so it is a kill at the boundary.
  - N2: −0.3 points, 95% CI −2.5 to 2.2.
  - Low power: planted runs found a real one-proton pH 9 peak only 32% of the time. Read this kill as "no vent-specific preference detected", not as a refutation (prereg, planted section).
- **Overall rule: two or more kills means "uninformative".** On these data, the Wimmer exergonicity result says nothing about whether LUCA's metabolism was tuned to vents. As the prereg requires, the three arms above are the headline.

## Numbers

| Arm | Statistic | N1 (Rhea) | N2 (Xavier S4) | Rule | Verdict |
|---|---|---|---|---|---|
| Direction | reversed core exergonic share, vent, gradient | 62.1% | 62.1% (core only) | kill ≥ 50, support ≤ 30 | kill |
| Specificity | core − matched null, vent, equal 1 mM | −8.4 [−15.4, −2.0] | −11.0 [−18.1, −4.7] | kill: gap < 5 and upper < 10 | kill |
| Setting | (vent − pond) core − null, gradient | +2.2 [0.0, 5.1] | −0.3 [−2.5, 2.2] | kill: CI includes 0 or wholly < 0 | kill |

Counts: 402 core rows, of which 314 were used (D4 σ < 100 kJ/mol, with balanced and parsed reactions only). Null rows used: N1 1,315 of 1,910; N2 1,560 of 2,488. Most matches are exact at the finest stratum (EC class, substrate and product counts, ATP use): N1 301 of 314, N2 296 of 314.

## Reported without a rule

- **Specificity under the gradient:** gap +2.5 [−2.0, 5.4] (N1) and +2.8 [−1.7, 5.7] (N2). Under the 100-fold gradient, 94–96% of every set is exergonic. The gradient caps the shares near 100%, so the core cannot stand out. This is why the sealed arm measures at equal concentrations.
- **Direction by change in molecule count (Δn):** reactions that increase the number of molecules (Δn > 0, n = 80) are all exergonic forward and 35% exergonic reversed. Reactions with Δn ≤ 0 stay 71–81% exergonic when reversed. Because the gradient favours products, it favours any reaction that makes more molecules. This explains part of the direction result.
- **Setting at equal concentrations:** −2.5 [−7.0, 2.5] (N1) and −8.9 [−13.7, −4.1] (N2). Without the gradient, the vent cell favours the null over the core.
- **Other pond cells:** at pH 6, 25 °C and at pH 3, 70 °C, every contrast either includes 0 or lies wholly below it.
- **Window fraction:** 7–9% of draws have the core's exergonic share peaking inside pH 8–10 and T ≥ 70 °C. The planted runs had already shown this statistic does not discriminate.

## What happened along the way

1. **Planted runs (before the real run).** These found two design flaws, both fixed before the real run:
   - Specificity hit a ceiling under the gradient, so it moved to equal concentrations.
   - The setting window statistic did not discriminate, so the verdict now uses the contrast only.
2. **Gate failure and deviation T1-1.** The first gate gave r = 0.117 against Wimmer Table 3.
   - The cause: 37 reactions with σ ≥ 100 kJ/mol are entered as exactly 0 in their table.
   - We added the sealed D4 σ filter to the gate. This was logged and committed before the rerun.
   - The gate then passed: r = 0.99999, and our share and theirs are both 74.84% on the 314 computable reactions.
3. **Post-hoc finding (not part of any arm).** Wimmer's 77% headline counts those 37 placeholder zeros as exergonic, because ΔG ≤ 0 counts as exergonic. That turns 74.8% (235 of 314) into 77.5% (272 of 351). Their published 77% therefore includes about 3 points from reactions whose ΔG could not be estimated.

## Limits

- The test covers the organic-reductant core (Table 1/3), not the H₂-substituted set behind the 95–97% headline (D1). The null cannot be H₂-substituted in the same way, so the H₂ headline is addressed only indirectly.
- Component contribution has no temperature term for ΔG′°. Temperature enters only through RT ln Q, as in Wimmer.
- The null pools are modern enzymes with annotated directions. "Matched non-core metabolism is at least as exergonic" is a statement about metabolism in general. It does not exclude the possibility that early metabolism differed in some other way.
