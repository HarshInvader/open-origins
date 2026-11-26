# Pre-registration: does the Xavier 2020 maxRAF stay below its rewiring null when the null conserves atoms?

Status: **written 2026-11-26, not sealed.** This is a correction run on our own earlier result, prompted by
T17. It is sealed only after gates G1 and G2 below have both run and passed; the rules here are fixed first,
and the gates can only stop the study, never change its decision rule. Study slot: follow-up to the
`raf_null` task, run number T19.

## Why this exists

Our own `experiments/raf_null/RESULTS.md` reported, from null N1 (degree-preserving rewiring), that rewired
copies give maxRAFs of 3,394-3,583 reactions against the real network's 1,357, and read that as "real
metabolism wired this way is less autocatalytic than random wiring with the same degrees". T17
(`experiments/t17_atom_balanced_tiers/T17_RESULTS.md`) found that a comparable degree-preserving null made a
KEGG hierarchy look special where an atom-balanced null did not, and the literature has said since 2011 that
switch randomisation leaves almost all metabolic reactions mass-unbalanced (Basler et al. 2011,
doi:10.1093/bioinformatics/btr145, reporting 99.8%; Samal & Martin 2011, doi:10.1371/journal.pone.0022295).
A rewiring that invents chemically impossible reactions is unconstrained in what those reactions may produce,
which plausibly inflates a maxRAF, so our N1 reading is suspect in a specific, testable direction. That
reading has already been withdrawn in the repo pending this test.

**What is not in question.** The `raf_null` study's own verdict ("within null") rests on N3m, the
degree-matched random food set, which rewires no reactions. That verdict stands whatever T19 finds, and T19
must not be reported as overturning it.

## Claim under test

Narrow and ours, not the authors': **the real network's maxRAF is below what rewired networks with the same
degrees give.** T19 asks whether that comparison survives when every rewired reaction is required to conserve
atoms.

## Data

The same input as `raf_null`: Xavier, Hordijk, Kauffman, Steel & Martin 2020, Proc R Soc B 287:20192377,
doi:10.1098/rspb.2019.2377, electronic supplementary dataset S4 (`experiments/raf_null/raw/rspb20192377supp5.txt`,
CC BY 4.0), already in the repo and hashed by `raf_null`'s loader. 5,740 molecules, 6,039 reactions, 68 food
molecules. Its `<molecules>` section carries a KEGG compound id per molecule.

Elemental formulas come from KEGG REST (`https://rest.kegg.jp/get/<10 ids>`), fetched by a new
`scripts/t19_fetch_formulas.py` on the same terms T17 used: at least 0.5 s between calls, User-Agent
`open-research-site/1.0`, no personal details, the response treated as untrusted text and read under
`python3 -I` with a strict regex over `ENTRY` and `FORMULA` lines only. Formulas are cached to a file whose
sha256 is recorded, and every later run checks that hash, so the network is fetched once.

## Method

maxRAF by the same unchanged code (`experiments/raf_null/cnet.py`, which agrees with brute-force enumeration
on 300 of 300 small random networks). Statistic: the number of reaction ids with at least one direction in the
maxRAF. The real observed value is the one already computed and recorded, 1,357 (1,335 excluding the 22
Pooling bookkeeping rows); this run does not recompute the claim, only the null.

### Null N1b, atom-balanced rewiring

A reaction's **total formula** is the summed elemental composition of its reactant side, counting
stoichiometry. If a reaction is balanced, its product side has the same total formula. Two balanced reactions
with equal total formulas may therefore exchange **product sides** and both remain exactly balanced. So:

1. Compute each reaction's reactant-side and product-side formulas.
2. A reaction is **movable** only if it is balanced as deposited and every molecule on both sides has a
   definite formula. A molecule is formula-less if KEGG gives no `FORMULA`, if the formula contains a generic
   group (an `R`, `X` or `n` term), or if it is one of the abstract tokens (`Peptide`, `Protein`, `Pooling`,
   `Spontaneous`, and any other molecule whose name has no KEGG id).
3. Group movable reactions into classes by total formula. Within a class, permute product sides uniformly at
   random (a random permutation of the class's product sides, drawn afresh per replicate).
4. **Held fixed:** every non-movable reaction, reversibility, all catalyst expressions, the food set, and the
   45 Pooling reactions. Catalysts are not touched at all, so N1b is strictly a substrate-network null.
   Molecule degrees are *not* preserved by construction; N1b trades degree preservation for atom balance,
   which is the point, and the two nulls are therefore complementary rather than nested.

999 replicates, seeds fixed in code, as in `raf_null`.

### Gate G1: is the null free enough to decide anything? (structure only, no RAF)

Reported before any null maxRAF is computed:

- the number and share of the 6,039 reactions that are balanced as deposited;
- the number of movable reactions, and why each excluded reaction was excluded;
- the number of total-formula classes, the class-size distribution, and how many movable reactions sit in a
  class of size 1 (those can never move);
- over 20 pilot draws: the mean share of reactions whose exact reaction no longer exists in the copy, and the
  mean Jaccard overlap of the copy's reaction set with the real one.

**G1 thresholds, fixed now (same form as T17's R4):** the mean share changed must be at least 0.30 and the
mean Jaccard below 0.80. **If G1 fails, the study stops and reports "not decidable: an atom-balanced product
swap cannot move this network enough", and the withdrawal of the N1 reading stands as a withdrawal** — that
is, we would be left unable to say whether the real maxRAF is low or not, which is itself the honest outcome
and must be reported as such, not as support for either reading.

### Gate G2: planted check

On the synthetic networks already built for the earlier RAF task (`experiments/raf_null`, task #8 machinery),
with formulas assigned so that balance is well defined: N1b must flag a planted autocatalytic core (real above
the 97.5th percentile) in at least 8 of 10 replicates, and must flag a network with nothing planted in at most
1 of 10. **If G2 fails, N1b is reported as descriptive only and decides nothing.** G2 runs before the real
nulls and its result is recorded whatever it is.

## Decision rule (fixed before any null maxRAF is seen)

95% range = 2.5th to 97.5th percentile of the 999 N1b sizes; two one-sided empirical
p = (1 + #null ≥ obs)/1000 and (1 + #null ≤ obs)/1000. With obs = 1,357:

- **"Artefact confirmed"** — obs lies **inside** the N1b 95% range. Then the "less autocatalytic than random
  wiring" reading was an artefact of chemically impossible reactions, and the withdrawal becomes a finished
  correction.
- **"Reading restored"** — obs lies **below** the 2.5th percentile of N1b. Then real metabolism is less
  autocatalytic than *chemically legal* random wiring too, and the withdrawn sentence is restored, with the
  atom-balanced null as its support.
- **"Reversed"** — obs lies **above** the 97.5th percentile of N1b. Then the real network is *more*
  autocatalytic than legal rewirings, which would be a new and much stronger claim than anything in
  `raf_null`, and would need its own replication before being reported as more than a single result.

All three are publishable and are written here so that none can be chosen afterwards. The N1b median and the
distance from obs to the nearer bound, in reactions, are reported in every case.

## Fallbacks, stated in advance

- **F1. Formulas missing.** If fewer than 60% of the 6,039 reactions are movable, the study still runs if G1
  passes, and the share of the network held fixed is reported in the headline, since a null that can move only
  a minority of reactions is weak evidence either way.
- **F2. KEGG unreachable or rate-limiting.** The fetch resumes from its cache; nothing else changes. If KEGG
  cannot be reached at all, the study is postponed, not run on partial formulas.
- **F3. Time.** 999 replicates at the observed maxRAF cost (`raf_null`'s run.log) is a few core-hours. If a
  replicate's median cost exceeds 60 s, the count drops to 199 replicates and the quantile precision is
  reported accordingly. The drop is decided by the pilot timing in G1, never after seeing null sizes.
- **F4. A rewired copy is disconnected from the food set** so its maxRAF is 0. Those draws are kept, not
  discarded; a null that often collapses is informative and the share of zero draws is reported.

## What this cannot show

- Topology is not kinetics. Nothing here shows a RAF ran prebiotically.
- N1b conserves atoms but not thermodynamic feasibility, and it keeps the database's modern molecule
  inventory, so "inside the null" means "inside what legal rewirings of modern KEGG chemistry give".
- N1b does not preserve molecule degrees, so a difference between N1 and N1b cannot be attributed to atom
  balance alone; it is the joint effect of adding balance and dropping degree preservation. This is a real
  limitation of the comparison and must be stated in the result, not buried.
- The study tests our own reading, not the authors' conclusion, which concerned cofactors in the food set and
  is untouched by it.
