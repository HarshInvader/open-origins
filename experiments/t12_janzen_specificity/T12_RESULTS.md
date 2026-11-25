# T12 result: "activity rises with specificity" holds clearly in one ribozyme family out of four once the floor and shared noise are removed; sealed verdict kill

Prereg: `docs/prereg/t12_janzen_specificity.md`, sealed in 65e1b15 (`HASHES.txt`). Script: `scripts/t12_analysis.py` (sha256 3203b475…). Output: `scripts_out/t12_real.json`.

## Claim

Janzen et al. 2022 (Nat. Commun. 13:3631, doi:10.1038/s41467-022-31387-0) measured aminoacylation rates on six substrates for 1,954 sequences in each of five ribozyme families. They write: "ribozyme activity was positively correlated with specificity, indicating that selection for increased activity would also lead to increased specificity". The evidence is Table 1: Pearson R from −0.54 to −0.84 between activity and the promiscuity index over all 1,954 sequences of each family, with p < 10⁻⁹⁵.

Two things make that correlation partly automatic:
1. **The floor.** Rates are given relative to background, so an inactive sequence reads about 1 on every substrate. That looks perfectly even (index near 1), whatever its true preference.
2. **Shared noise.** Total activity and the index come from the same six noisy cells. An overestimated top cell makes a sequence look both more active and more specific.

The test removes both:
- It keeps sequences with summed activity above 30, the paper's own cut.
- It subtracts the background (r − 1) before computing evenness.
- It corrects the correlation for measurement noise by SIMEX. Extra noise is added at known multiples of each cell's deposited bootstrap variance, and the result is extrapolated back to zero noise.

The rule:
- **Per family, kill** if the 95% interval of the corrected correlation R_S reaches 0, or R_S > −0.05.
- **Per family, support** if R_S ≤ −0.15 and the family is not killed.
- **Overall:** at least 3 of the 4 large families decide.

## Gate (before the seal)

- Table 1 reproduces to within 0.0005; for example, 1A.1 gives R = −0.6955 against the published −0.696.
- The index recomputes to within 3.3 × 10⁻⁷.

## Sealed verdict: kill (3 of 4 families)

| Family | Sequences above the cut | Paper's R (all 1,954) | Raw R after removing the floor | **Noise-corrected R_S** (95% interval) | Verdict |
|---|---|---|---|---|---|
| 1A.1 | 159 | −0.70 | −0.27 | **−0.25** (−0.53, +0.02) | kill (interval touches 0) |
| 1B.1 | 206 | −0.84 | −0.23 | **−0.05** (−0.30, +0.22) | kill |
| 2.1 | 1,064 | −0.53 | −0.50 | **−0.41** (−0.52, −0.31) | **support** |
| 2.2 | 1,136 | −0.54 | −0.23 | **+0.10** (−0.04, +0.26) | kill |
| 3.1 (reported only) | 37 | −0.81 | −0.34 | −0.25 (−0.82, +0.42) | too few to decide |

- **Most of the paper's correlation comes from the floor.** Removing inactive sequences and subtracting the background cuts R from −0.54 to −0.84 down to −0.23 to −0.50.
- **Correcting for shared noise** removes most of what is left in 1B.1 and all of it in 2.2.
- **Family 2.1 keeps a strong, well-measured link.** Its interval is far from 0.
- **Family 1A.1 is not a clean negative.** Its estimate (−0.25) is as large as 2.1's support line. It is killed only because, with 159 sequences, its interval just reaches 0 (+0.015). The planted check had shown this family has about 50% power at a true −0.22.

## Reported only (no rule)

- **Other rules.** The plan's rule and the uncorrected rule both give "mixed", not kill:

  | Family | Plan's rule | Uncorrected |
  |---|---|---|
  | 2.1 | support | support |
  | 2.2 | support | partly |
  | 1A.1 | partly | partly |
  | 1B.1 | partly | partly |

  The planted check showed that both of those rules give false support when no link exists, up to 17% of runs for the plan's rule.
- **If the real noise differs from the deposited bootstrap noise.** These are the same fitted curves, read at other noise levels:

  | Family | Half the deposited variance | Twice the deposited variance |
  |---|---|---|
  | 1A.1 | −0.26 | −0.23 |
  | 1B.1 | −0.15 | +0.19 |
  | 2.1 | −0.45 | −0.34 |
  | 2.2 | −0.08 | +0.54* |

  \*The twice-variance values come from extrapolating far along a quadratic and can leave [−1, 1]. They show direction only.
- **The kill depends partly on the noise assumption.** If the deposited bootstrap overstates the noise twofold, three families would have point estimates at −0.15 or stronger. 2.2 would still not support, and 1A.1 and 1B.1 would still need narrower intervals.
- The plan's subset (active above r = 5 on two or more substrates) gives raw R_adj of −0.19, −0.17, −0.59, −0.36 and −0.34, for 1A.1, 1B.1, 2.1, 2.2 and 3.1.

## Reading

- **What it shows.** The headline correlation in Table 1 (R up to −0.84, p < 10⁻⁹⁵) is mostly a consequence of how the index treats inactive sequences, and partly of noise that the total and the index share. As a general statement, "activity was positively correlated with specificity", for all families, does not survive. Only one of four large families (2.1) keeps a clear link beyond the floor and noise.
- **What it does not show.** It does not show that specificity never rises with activity. 2.1 shows it does, and 1A.1 points the same way without enough sequences to say. The kill rules out a link of about −0.2 or stronger as a general property of these families. It also leans on the deposited bootstrap being a fair measure of the noise; see the table above. Aromatic preference, the paper's second specificity measure, was not tested.
- **The "by-product" story.** The paper's title idea is that specificity emerges as a by-product of selection for activity. These data support it for one family. They do not support it as a general rule of ribozyme evolution.

## What it means for us

- **For the RNA-world route,** the claim that early ribozymes would gain substrate specificity for free under selection for activity has weaker evidence than its Table 1 suggests. It may hold in some sequence families and not others.
- **Method lesson,** the same as T8: any index computed from the same noisy measurements as the quantity it is correlated with needs a shared-noise correction and a floor check. The SIMEX correction here can be reused.
- This is a clean reanalysis of fully deposited data, and it reproduces the paper's own numbers first. It could be worth a friendly note to the authors. The owner decides.
