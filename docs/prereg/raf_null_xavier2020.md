# Pre-registration: is the maxRAF of the Xavier et al. 2020 anaerobic network larger than its nulls?

Author: agent orig-1. Date: 2026-11-18. Board task #6 (M3), gated on task #8 (M4).
Written before the maxRAF of the real network was computed by us and before any null was run on it. At this point I have only parsed the file (counts: 6039 reactions of which 3192 reversible, 5740 molecules, 68 food molecules, 45 reactions whose catalyst is the bookkeeping token "Pooling").

## Claim under test

Xavier, Hordijk, Kauffman, Steel & Martin 2020, "Autocatalytic chemical networks at the origin of metabolism", Proc R Soc B 287:20192377, doi:10.1098/rspb.2019.2377 (verified: Crossref record and Europe PMC full text PMC7126077 opened). They report a maxRAF of 1335 reactions in the O2-independent prokaryotic network when all organic cofactors are added to the food set, and read RAFs as "attributes of biochemical origins conserved in metabolic networks". The riskiest form (docs/fable_plan.md §3): the RAF is more than an artefact of network size and food-set choice.

## Data

Their electronic supplementary dataset S4 (file `rspb20192377supp5.txt`, CC BY 4.0, from Europe PMC), which the paper describes as the prokaryotic O2-independent network with the food set of small molecules, abiotic carbon and organic cofactors. KEGG-derived, redistributed by the authors; we do not download KEGG. Rhea/ModelSEED are not used in this run (a Rhea-built network is a separate follow-up task).

## Method

maxRAF by the Hordijk-Steel reduction (doi:10.1016/j.jtbi.2003.11.020, verified via Crossref), generalised to AND/OR catalyst expressions and reversible reactions (`experiments/raf_null/cnet.py`; agrees with brute-force enumeration on 300/300 small random networks). Size = number of reactions (by id) with at least one direction in the maxRAF.

**Reproduction check.** If our observed size differs from 1335 by more than 2% (outside 1308-1362), I report the discrepancy, keep our own number as the observed value, and say the test is of the file as deposited.

## Nulls (999 replicates each, seeds fixed in code)

- **N1 degree-preserving rewiring.** Permute reactant stubs among reactant slots, product stubs among product slots, and catalyst-clause stubs among catalyst-clause slots, separately; every molecule keeps its reactant, product and catalyst degree; every reaction keeps its slot counts and reversibility. The 45 Pooling reactions and clauses containing the tokens Pooling or Spontaneous are held fixed.
- **N2 catalyst shuffle.** As N1 but only catalyst clauses are permuted; the substrate network is real.
- **N3 random food, uniform.** The 66 real food molecules are replaced by 66 molecules drawn uniformly from all molecules used in the network (the 2 pseudo-tokens kept).
- **N3m random food, degree-matched.** Each real food molecule is replaced by a molecule in the same stratum (catalyst-only or not, times log2 of total degree), without replacement.

## Decision rule

- For each null: 95% range = 2.5th to 97.5th percentile of null sizes; two one-sided empirical p = (1 + #null ≥ obs)/(1000) and (1 + #null ≤ obs)/(1000).
- **Validity gate from task #8.** A null counts as decisive only if, on the synthetic networks of task #8 with nothing planted, its "above the 95% range" rate was ≤ 10% for both background models, and the RAF code recovered every planted core. A null that fails the gate is reported as descriptive only.
- **Decisive nulls:** N1 and N3m (the two the board task names: degree-preserving networks and equal-size food sets), subject to the gate.
- **Verdict:**
  - "Above null" (RAF not explained by size/degree/food choice): obs above the 97.5th percentile of every decisive null.
  - "Within null" (consistent with an artefact): obs inside the 95% range of at least one decisive null.
  - "Below null": obs below the 2.5th percentile of every decisive null.
  - Mixed patterns are reported as mixed, null by null, with no overall pass.
- N2 and N3 are reported, not decisive. One ledger row per null (4 tests, family "M3:raf-xavier").

## Power

With 999 replicates, the 95% range is estimated to about ±1 percentile. The detectable effect is reported as (obs − null median)/null IQR and as the distance from obs to the nearer 95% bound, in reactions.

## What this cannot show

Topology is not kinetics; a RAF in a modern KEGG network does not show it ran prebiotically. The nulls hold the database's modern composition fixed (degree sequences, molecule identities), so "above null" means "above what degree structure and food size give", not "prebiotic".
