# T19 result: not decidable. The atom-balanced product swap cannot move this network enough.

**Verdict: the study stops at its own feasibility gate, exactly as the prereg said it would.** No maxRAF was
computed under the new null, and no result was read. The withdrawal of our `raf_null` N1 reading therefore
stands *as a withdrawal*: we still cannot say whether the real network's maxRAF is low compared with
chemically legal rewirings.

Prereg: `docs/prereg/t19_raf_atom_balanced.md`, written and committed in 311f2a3 **before** this gate ran.
Gate script `scripts/t19_gate1.py`, output `scripts_out/t19_gate1.json`. Inputs: Xavier 2020 dataset S4
(sha256 `85fc8b6c…`) and the KEGG formula table (sha256 `c16698c2…`, 5,328 formulas, gitignored under the
same rule T17 used for KEGG entries; regenerate with `scripts/t19_fetch_formulas.py`).

## What the gate found

Gate G1 is structure only. It computes nothing about autocatalytic sets, so there was no way to tune the
null towards a wanted answer.

| Quantity | Value |
|---|---|
| Reactions in dataset S4 | 6,039 |
| Distinct molecules used in reactions | 5,721 |
| Molecules with a definite elemental formula | 4,441 |
| Molecules without one | 1,280 (878 generic R/X/n, 225 no KEGG id, 177 no FORMULA line) |
| Reactions balanced as deposited | **4,264 (70.6%)** |
| Reactions excluded | 1,632 contain a formula-less molecule; 143 do not balance as deposited |
| Movable reactions | 4,264 (70.6%), so F1 was not triggered |
| Total-formula classes | 2,833 |
| Movable reactions alone in their class | **2,176 of 4,264 (51%)** |
| Largest classes | 45, 27, 26, 21, 19, 18 |
| Mean share of directed reactions changed, 20 pilot draws | **0.169** (threshold ≥ 0.30) |
| Mean Jaccard overlap with the real network | 0.715 (threshold < 0.80, met) |
| **G1** | **fail** |

## Why it failed, and why the design is at fault rather than the data

The move the prereg chose is to exchange **product sides** between reactions. For both reactions to stay
balanced, they must have the **same total formula**, and that is forced by the move, not an arbitrary
tightening: if A→B and C→D are balanced, then A→D is balanced only when A and C have equal composition. The
consequence is the table above: half the movable reactions are the only member of their total-formula class
and can never move at all, and a uniform permutation within the small remaining classes leaves most of the
rest in place. Only 17% of directed reactions change, against the 30% the prereg required.

So this is a design that was too tight, found out by its own gate before it could produce a number. One
encouraging detail: 70.6% of the deposited reactions do balance on KEGG formulas alone, so the network is
chemically well enough specified for an atom-balanced null in principle. The move type is the problem.

**For contrast, T17's null is far freer on a comparable network** because it swaps *half-reactions* within
formula-**difference** classes rather than whole product sides: 27,547 classes with the largest holding 1,716
halves, and it changed 73% of reactions. Matching formula differences is a much weaker requirement than
matching total formulas.

## What this does and does not settle

- It does **not** restore the withdrawn sentence. "Real metabolism is less autocatalytic than random wiring
  with the same degrees" stays withdrawn, on the grounds given in `RESULTS.md`: the N1 rewiring leaves
  almost all reactions chemically impossible (Basler et al. 2011, doi:10.1093/bioinformatics/btr145).
- It does **not** show the opposite either. T19 produced no comparison.
- It leaves `raf_null`'s own verdict untouched. That verdict ("within null") rests on N3m, the degree-matched
  random food set, which rewires no reactions.
- The honest state of this question is therefore: open, with the earlier answer retracted and no replacement.

## The obvious next design, and why it is a new prereg

A half-reaction swap on formula-difference classes, as in T17, would very likely clear G1's mixing
threshold. That is a different move, so it belongs in its own prereg rather than as an amendment here;
amending a null after its gate failed is the kind of post-hoc rule change that invalidated the support arm of
T17 (see C1 there). Writing it is cheap and nothing about any RAF has been computed, so the usual danger of
designing towards a known answer does not apply yet. It is queued as a decision, not started.
