# T17: do KEGG biochemistry's nested autocatalytic tiers survive an atom-conserving null?

Status: **complete; sealed verdict kill (2026-11-26).** The blind dry run (28 of 28 parts) fixed F1 to the full counts, and `real` ran all 28 parts (700 draws). Every real statistic lies inside the central 95% of all four atom-balanced nulls, so the kill rule fires and **T14's support is overturned**. Results: `T17_RESULTS.md`. Prereg: `docs/prereg/t17_atom_balanced_tiers.md`. Design: section "U1" of `docs/NEW_STUDIES_2026-11-25.md`.

## Question

T14 (sealed, support) found that degree-preserving rewires of the KEGG-derived network of Peng, Linderoth & Baum 2022 give one autocatalytic set and no nesting, where the real network has three nested sets. But T14's rewired reactions do not conserve atoms. T17 repeats the test with nulls in which every rewired reaction balances every element, using KEGG molecular formulas. If the tiers survive, they are a feature of which balanced reactions biology uses. If not, atom bookkeeping alone gives tiers.

## Layout

- `scripts/t17_fetch_kegg.py`: downloads the KEGG COMPOUND entries for the 4,216 species (422 calls of 10 ids, at least 0.5 s apart, generic User-Agent). Output in `raw/kegg/` (gitignored; KEGG data are not ours to republish).
- `scripts/t17_analysis.py`: modes `gate`, `planted`, `planted_merge`, `sealcheck`, `dryrun`, `dryrun_verdict`, `real`, `real_verdict`. It imports the sealed T14 script (`experiments/t14_autocatalytic_tiers/scripts/t14_analysis.py`, sha256 checked) for loading, expansion, scan, LP and the synthetic generator. `real` refuses unless `docs/prereg/HASHES.txt` names the script with its current sha256.
- `scripts_out/`: `t17_gate.json`, `t17_planted.json` and the planted parts.
- `work/` (gitignored): logs and, later, the blind dry-run draws.

## Run

From `experiments/`, single-threaded under `nice -n 20`, with the project venv:

```
python -I t17_atom_balanced_tiers/scripts/t17_fetch_kegg.py t17_atom_balanced_tiers
python -I t17_atom_balanced_tiers/scripts/t17_analysis.py t17_atom_balanced_tiers gate
python -I t17_atom_balanced_tiers/scripts/t17_analysis.py t17_atom_balanced_tiers planted sparse_planted 0 10
```

See the prereg for the gate and planted results and for how `real` will be run after the seal.

## Rival explanations for the real outcome

Written 2026-11-26 after all 28 `real` parts were on disk and before `real_verdict` was run or any real
statistic was read. The sealed rules allow three outcomes: **kill** (the real n_sets and nested_share
both lie inside the central 95% of Null B), **not killed** (they do not, and the design's support rule
is unreachable per C1), or **not decidable** (R4: the Null-B draws failed to mix).

1. **Kill is the true answer.** The KEGG network's nested autocatalytic tiers are a by-product of its
   degree sequence and its atom-balance constraints. T14's degree-preserving nulls destroyed the tiers
   because they also destroyed atom balance; once the nulls are made chemically legal, the tiers come
   back on their own. Prediction: the real values sit near the middle of Null B, and Null A (the loosest
   null) looks much like Null B.
2. **Not killed, and the tiers are real structure.** Prediction: the real values sit above essentially
   every Null-B draw, with Null C (frozen hubs) closer to the real values than Null B, because freezing
   hubs preserves part of the real architecture. A clean separation would be meaningful even though
   "support" cannot be declared.
3. **Not killed for a dull reason: a residual constraint the null cannot break.** The atom-balance
   rewire may be unable to move the particular reactions that make the tiers, so the nulls keep them by
   construction, not because the tiers are special. This looks like rival 2 but is distinguished by the
   mixing numbers (R4, share changed and Jaccard) and by Null A, which is loosest: if even Null A cannot
   push the real values inside, the nulls are too constrained rather than the structure being strong.
   The planted check already found that atom-balanced nulls keep a planted core in 10 to 12% of draws,
   so this is a live worry, not a hypothetical.
4. **A leak or artefact.** The real values are computed by the same imported T14 code as the nulls, and
   the KEGG input hash is checked at every load, so a mismatch between the real and null code paths is
   ruled out by construction. What is not ruled out by construction is a seed collision between parts;
   the independent check is that the 28 parts carry 700 distinct seeds by the D9 formula.

**Independent check on the measure.** n_sets and nested_share are structural counts from the same
expansion routine T14 sealed and whose analytic behaviour T14's gate tested; they are not fitted. The
stated reason they track the target is that a nested autocatalytic hierarchy is, by definition, a set of
self-sustaining subnetworks ordered by inclusion, which is what these two count. Their weakness is
nested_share's cap at 1.0, which is why it cannot support, only kill (C1).
