# Planted autocatalytic core: always found, but maxRAF size only flags large cores, and two of four nulls are invalid

**Verdict: the method passes, with limits.** The maxRAF code is correct: it matched brute-force enumeration on 400 of 400 small random networks, and it contained the planted core in 180 of 180 networks (cores of 20 to 1000 reactions). The real question is whether a maxRAF size test can tell a planted core from no core, and the answer depends on the null:

- **N1, degree-preserving rewiring, is valid.** Its false-positive rate with nothing planted is 1/20 and 0/20 on the two background models. Its power is weak. It flags a 1000-reaction core 20/20 and 12/20 times, a 300-reaction core 8/20 and 5/20 times, and a 100-reaction core 2/20 and 0/20 times, against background maxRAFs of about 1000 to 2000 reactions.
- **N2, catalyst-only shuffle, is valid.** False-positive rate 1/20 and 0/20. It has the best power: a 1000-reaction core is flagged 20/20 and 19/20 times, a 300-reaction core 14/20 and 8/20.
- **N3, uniform random food of equal size, is invalid.** It flags 18/20 and 20/20 networks that have nothing planted. Real food sets are hubs, so a random draw of the same size almost always gives a smaller maxRAF. Do not use it.
- **N3m, degree-matched random food, passes the gate as pre-registered (above-rate 0/40), but it has no power and is skewed.** It never flags a planted core, at any size (0/80 for k ≥ 100). With nothing planted, it puts the real maxRAF *below* its 95% range in 14/20 and 18/20 networks.

So a "maxRAF larger than null" result under N1 or N2 means something; a result under N3 means nothing; and N3m cannot produce one. This gate is applied in task #6 exactly as `docs/prereg/raf_null_xavier2020.md` set it out (N1 and N3m decisive if they pass; the gate is the one-sided above-rate ≤ 10%). N3m's low-side skew is disclosed there as a known defect, not used to change the rule.

## Set-up

- **Algorithm.** Hordijk & Steel 2004, "Detecting autocatalytic, self-sustaining sets in chemical reaction systems", J Theor Biol 227:451-461, doi:10.1016/j.jtbi.2003.11.020 (verified: Crossref record opened). The maxRAF is found by repeatedly removing reactions that lack a reactant or a catalyst in the food closure. Code: `raf.py`.
- **Background networks** (`gen.py`): 6000 reactions over 5700 metabolites plus 10 catalyst-only "metals", a 40-molecule food set (20 hubs, 10 metals, 10 random), 1-3 reactants and products per reaction, and 2/3 of reactions catalysed by 1-2 of 40 catalysts (the metals plus 30 cofactor metabolites). There are two models. R draws substrates independently with Zipf weights. S grows reactions outward from the food set, so nearly every metabolite is reachable, as in a curated metabolic network. Both have about the size of the Xavier et al. 2020 network (5994 reactions and 5723 metabolites as reported in that paper, doi:10.1098/rspb.2019.2377, verified via Crossref and Europe PMC PMC7126077). The parameters are our own choices, not fitted to it.
- **Planted core:** k new molecules and k reactions. Each reaction makes one core molecule from food hubs and earlier core molecules, and is catalysed by a random core molecule. Sizes k = 20, 100, 300 and 1000; k = 0 is the nothing-planted control. 20 networks per cell, 99 null replicates per network per null, fixed seeds.
- **Decision per network:** "above" = observed maxRAF size above the 97.5th percentile of the null.

## Numbers

Counts of networks (out of 20) flagged above / below the null 95% range:

| Background | Planted k | Mean maxRAF | Core recovered | N1 | N2 | N3 | N3m |
|---|---|---|---|---|---|---|---|
| R | 0 | 960 | n/a | 1 / 0 | 1 / 0 | 18 / 0 | 0 / 14 |
| R | 20 | 854 | 20/20 | 2 / 0 | 0 / 1 | 19 / 0 | 0 / 13 |
| R | 100 | 1031 | 20/20 | 2 / 0 | 6 / 0 | 20 / 0 | 0 / 12 |
| R | 300 | 1054 | 20/20 | 8 / 0 | 14 / 0 | 20 / 0 | 0 / 15 |
| R | 1000 | 2027 | 20/20 | 20 / 0 | 20 / 0 | 19 / 0 | 0 / 13 |
| S | 0 | 1803 | n/a | 0 / 0 | 0 / 0 | 20 / 0 | 0 / 18 |
| S | 20 | 1980 | 20/20 | 2 / 0 | 0 / 1 | 20 / 0 | 0 / 15 |
| S | 100 | 1737 | 20/20 | 0 / 0 | 4 / 0 | 19 / 0 | 0 / 15 |
| S | 300 | 2217 | 20/20 | 5 / 0 | 8 / 0 | 19 / 0 | 0 / 14 |
| S | 1000 | 2824 | 20/20 | 12 / 0 | 19 / 0 | 20 / 0 | 0 / 13 |

Wilson 95% intervals for each rate are in `results.json`. With 20 networks per cell, a false-positive rate of 0/20 is compatible with up to about 16%, and 1/20 with up to about 24%.

## What this means for task #6

- "The maxRAF contains the core" is not a test. Every background already has a maxRAF of about 1000 or more reactions, so containment happens with or without a planted core. Only the size-versus-null comparison has any specificity.
- Under N1, the detectable effect is roughly a core of 30% or more of the background maxRAF. A null result on real data therefore cannot exclude a smaller genuine autocatalytic core.
- Food-set nulls are hard. The real food set is chosen (hubs, metals, cofactors), so size-matched random food is not a fair comparison (N3). Degree matching (N3m) over-corrects in these models. A better food null would match molecule roles (catalyst degree and substrate degree separately), and that is a follow-up.

## Not checked

- Background models with modular, pathway-like structure. Real metabolism may differ, so these rates are about the method, not about KEGG.
- Cores whose catalysts are food molecules (cofactor-catalysed cores). Planted catalysts here are always core molecules.
- Null replicates per network were 99, so p-values resolve only to 0.01.

## Files

`raf.py` (algorithm and nulls), `gen.py` (generators), `planted_run.py` (run; resumable), `planted_runs.jsonl` (200 rows), `part_a.json`, `summarize.py`, `results.json`, `ledger_rows.csv`. The run went through `board/run.sh` with `Pool(2)`.

## Hypotheses

| Hypothesis | Result |
|---|---|
| maxRAF code is exact | yes, 400/400 against brute force |
| Planted core is inside the maxRAF | yes, 180/180 |
| N1 is calibrated (FPR ≤ 10%) | yes: 1/20, 0/20 |
| N1 detects a planted core better than its FPR | only for k ≥ 300 (R 8/20, S 5/20) and k = 1000 (20/20, 12/20) |
| N3 is a valid null | no: 18/20, 20/20 FPR |
| N3m is a valid null | above-side yes (0/40), low side skewed (14/20, 18/20), no power |
