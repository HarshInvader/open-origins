# T17 result: the nested autocatalytic tiers are reproduced by atom-balanced nulls; sealed verdict kill

This overturns T14's support. Study U1. Prereg: `docs/prereg/t17_atom_balanced_tiers.md`, sealed
2026-11-25T11:26:40Z in `docs/prereg/HASHES.txt`. Script `scripts/t17_analysis.py`, sha256
`3f5fb5544fc9c1c3d3b575c27f432967f0b305d7640fb46012f41457964bc533`, the sealed hash. Output
`scripts_out/t17_real.json`, from 28 parts in `scripts_out/real_parts/` (700 draws, 700 distinct draw
indices). No fallback was triggered: the dry run's median null scan was 5.77 CPU s, far under F1's 60 s,
so the full preregistered counts ran (200 draws each of Nulls A, B and C, 100 of Bconv, all 4,186
candidate seeds).

## What was tested

T14 (sealed 2026-11-25) found that the KEGG-derived biochemical network of Peng, Linderoth and Baum 2022
(doi:10.1371/journal.pcbi.1010498) has 3 nested self-sustaining sets, where degree-preserving rewires
give 1 set and no nesting at every central quantile. T14 read that as "nested tiers are a property of
the specific chemistry, not of degrees."

T14's rewires swap products between reactions. They preserve every species' reactant and product counts
and every reaction's size, but they do **not** preserve atom balance: the rewired reactions are mostly
not chemically legal. T17 asks whether the hierarchy survives a null that keeps the chemistry legal.
Nulls swap whole half-reactions between reactions within a formula-difference class, so every reaction
stays atom balanced, and the tier-0 food system is untouched.

- **Null A:** loosest, any eligible half.
- **Null B:** the deciding null for the kill rule; all halves eligible.
- **Null Bconv:** Null B restricted as in D5.
- **Null C:** strict, no half containing a tier-0 species or a top-1%-degree hub may move.

## Result

| Statistic | Real | Null A 2.5-97.5% (median) | Null B | Null Bconv | Null C |
|---|---|---|---|---|---|
| Distinct seed-induced sets | **3** | 1-5 (3) | 1-3 (2) | 1-3 (1.5) | 0-4 (2) |
| Share of nested set pairs | **1.0** | 0-1 (1) | 0-1 (1) | 0-1 (0.5) | 0-1 (1) |
| Depth of nested chain | **3** | 1-5 (3) | 1-3 (2) | 1-3 (1.5) | 0-4 (2) |
| Supported seeds | 304 | 79-482 (411) | 182-579 (456) | 148-614 (453) | 0-557 (357) |
| Largest set (species) | 1,414 | 500-1,830 (1,638) | 577-1,779 (1,569) | 1,278-1,756 (1,517) | 0-1,865 (1,626) |

Real set sizes: 1,414, 357 and 301 species, nested, as T14's gate reproduced.

**Every real statistic lies inside the central 95% of every one of the four nulls, and outside the
central 99% of none of them.** The real value of 3 sets is exactly Null A's median, and its nested share
of 1.0 is the median of A, B and C. By the sealed kill rule (real n_sets and nested_share both inside
the central 95% of Null B), the verdict is **kill**.

Mixing (R4) passes with room to spare: over the 200 real Null-B draws, a mean 73.8% of the 8,154 balanced
directed reactions no longer exist in the copy, and the mean Jaccard overlap with the real reaction set is
0.175, against thresholds of 30% and 0.8. So the study is decidable and the kill stands.

Support was unreachable before the run, for a reason recorded in the prereg (C1): nested_share is capped
at 1.0 and the real value is 1.0, so "above the central 99%" cannot fire once more than about 0.5% of
null draws contain any nested pair. The reported-only C1 rule, which replaces nested_share with
chain_depth, also does not fire here (0 of 4 nulls), so nothing changes if it is read.

## Reading

**The hierarchy is not evidence about the chemistry of early metabolism.** Once the null is required to
conserve atoms, networks that are random in every other respect produce the same number of nested sets,
the same perfect nestedness and the same chain depth as KEGG. Atom balance plus the degree sequence plus
the fixed tier-0 food set are enough. T14's support came from nulls that break atom balance, which is a
constraint real biochemistry cannot violate; the comparison was against networks that could not exist.

Two other apparent peculiarities dissolve the same way. Against degree nulls the real network looked
unusual for having *few* supported seeds (304 against a median 1,349) and a *small* largest set (1,414
against 3,214). Against atom-balanced nulls both sit comfortably inside: 304 seeds against a Null-B
median of 456, and 1,414 species against 1,569.

**Which rival explanation fits.** The four rivals were written into `README.md` after all 28 parts were
on disk and before `real_verdict` ran or any real statistic was read.

- **Rival 1 (kill is the true answer) fits.** The real values sit near the middle of the nulls, and Null
  A, the loosest, is the closest match of all.
- **Rival 3 (a kill for the dull reason that the null cannot break the relevant constraint) is argued
  against, though not excluded.** The nulls are not stuck at the real values: they span 0 to 5 sets and
  0 to 4 chain depth, often exceeding the real network, and they move 74% of reactions. A null that
  simply preserved the tiers by construction would cluster at the real value, not straddle it. The
  stronger argument is the planted calibration: the same kill rule kills 10 of 10 same-degree controls
  and 5 of 5 background networks, yet kills **0 of 10 networks with a planted core**. The rule has
  demonstrated power to withhold a kill when real hierarchical structure is present, so a kill here is
  informative. The residual worry recorded in the prereg stands: atom-balanced nulls kept part of a
  planted core in 10 to 12% of draws, so these nulls are gentler on hierarchy than degree nulls are.
  That is a reason this result cannot show the tiers are *absent*; it is not a reason to doubt that
  KEGG's tiers are unremarkable against legal chemistry.
- **Rival 2 (real structure) does not fit:** there is no separation to explain.
- **Rival 4 (leak or artefact):** the real and null statistics come from the same imported T14 routine,
  the KEGG input hash is checked at every load, and the 700 draws carry 700 distinct indices.

## Scope

- This concerns the **hierarchical organisation** claim: how many self-sustaining sets there are, whether
  they nest, and how deep the chain is. It says nothing about whether autocatalytic sets exist in
  biochemistry; they do, in the nulls too.
- **Biochemical network only.** T17 does not re-run the abiotic network, where T14 found one set.
- It does not show the tiers are *not* chemically meaningful, only that this statistic cannot tell. A
  test that could: a null that conserves atoms *and* thermodynamic feasibility, or one built on a
  measured flux-carrying subnetwork rather than on KEGG's full reaction list.
- Smallest effect this could have caught: the kill rule fires only when the real values fall inside the
  central 95% of Null B. Its planted calibration (kills 0 of 10 planted, 10 of 10 same-degree controls)
  shows it separates a planted hierarchy from none; it was not calibrated against a hierarchy weaker
  than the planted one, so a small excess over legal-chemistry nulls would not have been detected.

## Consequence for T14

T14's sealed verdict is not withdrawn as a statement about its own nulls, which it reports correctly. Its
**reading** is retracted: nested tiers are not shown to be a property of the specific chemistry. T14's
`T14_RESULTS.md` carries a pointer to this file. The project's first support therefore did not survive the
first harder null we built for it, and it was our own follow-up that overturned it.
