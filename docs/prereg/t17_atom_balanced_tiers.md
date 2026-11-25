# Pre-registration (T17): do the nested autocatalytic tiers of KEGG biochemistry survive an atom-conserving null?

Status: written 2026-11-25. This is study U1 in `docs/NEW_STUDIES_2026-11-25.md`. `gate` and `planted` have been run; the dry run and `real` have not. The script refuses `real` until `docs/prereg/HASHES.txt` names `experiments/t17_atom_balanced_tiers/scripts/t17_analysis.py` with its current sha256. The sealed hash is in `HASHES.txt`.

## What has been seen (blinding disclosure)

The unknown is where the real biochemical network's two hierarchy statistics (number of sets, nested share) fall among atom-balanced rewired copies of it.

- **The observed statistics are published and were recomputed by T14 and again here:** 304 seeds, 3 sets, nested share 1.0, largest set 1,414 species. These are the claim, not a peek.
- **T14's sealed result is known.** Degree-preserving rewires (which do not keep atoms) give 1 set and nested share 0 in essentially every copy, and 3 to 4 times more seeds. That is why this study exists.
- **No atom-balanced rewired copy of the real network has been scanned.** The gate built 13 rewired copies (2 per null for A, C and Bconv, 5 for B) and measured only how much they differ from the real network (which reactions changed, Jaccard overlap, invariants). No seed scan, LP, set count or any autocatalysis statistic was computed on them.
- **The planted check uses synthetic networks only** (T14's mass-balanced generator, the same seeds and networks as T14's sparse world).
- **Script versions.** (1) The gate first ran under `b956aa1e...`. (2) The planted mode was then restricted to Nulls A to C and cut to 50 draws per null, and the KEGG hash check was added to `load_real`. The gate was re-run under `934915d4...` with identical numbers; that run is what `scripts_out/t17_gate.json` holds. A first planted attempt at 100 draws was stopped before it finished any replicate, and nothing from it was kept. (3) The planted check ran under `934915d4...`. After its first 5 + 5 replicates showed that the design's support rule cannot flag planted cores (change C1), the rule code (`verdict`, `classify`, `planted_merge`) was changed, giving `94bc1a27...`. Nothing that computes the stored observed values or null arrays changed, so parts written later record `94bc1a27...` for arrays computed by the same code. `planted_merge` re-applies the rules to the stored arrays. (4) The coordinating agent then reverted C1 from deciding to reported only. The design's rules decide; see C1. That changed only `verdict` and the summary keys in `planted_merge`, giving `3f5fb554...`. The later planted parts were computed under that hash, and the final `planted_merge` applied the rules under it. No code that computes observed values or null arrays changed at any of these steps. The gate is re-run under the sealed hash before the seal.

## Claim under test

Peng Z, Linderoth J, Baum DA. 2022. "The hierarchical organization of autocatalytic reaction networks and its relevance to the origin of life." PLoS Comput Biol 18:e1010498. doi:10.1371/journal.pcbi.1010498 (PMC9491600). Full text: `experiments/t14_autocatalytic_tiers/raw/europepmc/` (quotes as in the T14 prereg).

- Results, verbatim: "These SDASs are nested, with SDAS-bio-1c including the entirety of SDAS-bio-1b, which includes the entirety of SDAS-bio-1a."
- Discussion, verbatim: "We found that the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs converting simple materials and energy to more complex species."

**Where T14 left it.** T14's sealed verdict was support: degree-preserving rewires destroy the tiers. T14's results file names the gap: rewired reactions do not conserve atoms. So "the tiers are specific" could mean "biochemistry is organised" or only "real chemistry balances its atoms and random chemistry does not".

**H1.** The nested tiers are a feature of which balanced reactions biology uses: atom-balanced rewired copies do not show them.

**H0.** Atom-balanced rewired copies that keep the tier-0 system show as many nested sets.

## Inputs (exact)

| Input | sha256 | Use |
|---|---|---|
| T14 `raw/plos/S2_Table.xlsx` (read-only, gitignored) | 8ace73e1e69d29d35d7c8471c5633812a1e4b3a27ba195b77c4b92d14b321fe9 | network: 8,402 reactions (4,201 reversible pairs), 4,216 species |
| T14 `data/food_sets.tsv` (in repo) | 466965aa53b1d4fbce0f5f238804f2976d4813cc25fdeec99dfc9c18787bce3d | ultimate food |
| T14 `scripts/t14_analysis.py` (sealed; imported) | 48ecdd36d68b3a7a281a56b85755e85c6ee67a0d212b99a0940bb5197cb57f62 | loader, expansion, scan, LP, synthetic generator |
| `raw/kegg/batch_000.txt` ... `batch_421.txt` (gitignored) | c6f6dbf06324e91014a01219127388bf4e08b14948dd8cfe2ef572de8bab4791 (hash over the sorted file names and file hashes; `kegg_hash()` in the script) | KEGG COMPOUND entries, FORMULA line |
| `raw/kegg/ids.txt` | c6e5a9a4b474ba902be5176a6a8e47dac6a9675f8c8535e387c4541dfb18f35e | the 4,216 ids fetched |

The KEGG entries were fetched on 2026-11-25 by `scripts/t17_fetch_kegg.py` from `https://rest.kegg.jp/get/<10 ids>` (422 calls, at least 0.5 s apart, generic User-Agent). They are untrusted text; only the `ENTRY` and `FORMULA` lines are read, by strict regexes, under `python -I`. The T14 inputs are re-hashed by T14's own check at every run, and the T14 script's hash is checked before import. `load_real` (used by the gate, the dry run and `real`) checks `kegg_hash()` against the value above and stops on a mismatch.

## Formulas and balance (gate; structure only)

- 4,214 of 4,216 ids have a KEGG entry; 4,210 have a plain formula (no R group, no "n", no brackets). Without one: C01358, C04905, C04908, C05359, C20797, C20798.
- 21 elements occur.
- **8,154 of 8,402 reactions balance every element exactly**, 224 do not, and 24 touch a species without a plain formula. The U1 design note counted 8,152, 224 and 26 from an earlier formula pass; the difference is 2 species whose formulas this parser accepts. The rule thresholds refer to "the balanced reactions", which are now 8,154.
- Movable units (reversible pairs or one-way reactions that balance, are outside tier 0 and have no species on both sides): 4,053 of 4,201 pairs. The other 148 pairs never change.

## Fixed decisions

- **D1. Expansion, tier 0, seeds, support and statistics** exactly as T14 (D1, D2): imported from the sealed T14 script. Statistics: n_seeds, n_sets, nested_share, largest, and chain_depth (chain_depth is reported only; see C1).
- **D2. Units and halves.** A unit is a reversible pair (forward reaction, reverse rebuilt as its exact reverse) or a one-way reaction (KEGG has none here). A unit's stubs are its species with coefficients and sides. A *half* is any nonempty proper subset of a unit's stubs, each keeping its side; its formula difference d = (products in the half) minus (reactants in the half), summed over elements with coefficients. If two halves have the same d, exchanging them leaves both reactions balanced in every element. For reversible units a half with difference -d may also be exchanged after flipping its sides (the reverse reaction exists anyway).
- **D3. One move.** Pick a movable unit uniformly, one of its eligible halves uniformly, and a partner half uniformly among all current eligible halves with the same d (or -d, flipped) in other units. Reject the move if either new reaction has an empty side, a species twice on one side or on both sides, or all reactants in tier 0 (forward, and for pairs the reverse as well), which keeps the tier-0 system exactly. The rewired network's tier 0 is asserted equal to the real one (30 species, 44 reactions). The partner index is updated lazily: a sampled stale entry is dropped and the move rejected.
- **D4. Chain length.** 20 attempted moves per movable unit (81,060 per draw), each draw started from the real network with its own seed. Fixed by the gate (below) before any null statistic existed.
- **D5. Null A, "isomer".** Halves are single stubs: a species is exchanged only with a species of identical formula and the same coefficient and side. Reported only.
- **D6. Null B, "half-reaction swap" (decides kill and support).** All halves eligible.
- **D7. Null C, "strict" (decides support).** Null B, but no half may contain a frozen species: tier-0 species and the top 1% of species by degree (T14's `frozen_species`). Frozen species therefore never move.
- **D8. Null Bconv (reported only).** Null B with both the exchanged half and the kept half required to have at least one reactant and one product (a "main conversion" plus a "cofactor conversion", the design's example). This is the literal reading of the design's "two coupled halves"; Null B is the general form and is the one the design's gate and rules name.
- **Invariants checked in the gate for every null:** every species keeps its counts as reactant and as product; all 8,154 balanced reactions stay balanced; every reverse is exact; tier 0 unchanged.
- **D9. Counts and seeds.** 200 draws each of Nulls A, B, C and 100 of Bconv; draw i of null k uses seed `[20261217, 6, k, i]` (dry run: stream 5). All 4,186 candidates are scanned.
- **D10b. chain_depth** (longest chain of strictly nested sets, T14's definition) is placed against every null alongside the four statistics; it enters only the reported-only C1 rule.
- **D10.** Quantiles: numpy `quantile` (linear); "inside the central 95%" = within [q0.025, q0.975] inclusive; "above the central 99%" = above q0.995.

## Gate (`t17_analysis.py gate`; run; passed)

Output: `scripts_out/t17_gate.json`.

**1. T14 reproduced.** 4,216 species, 8,402 reactions; tier 0 of 30 species and 44 reactions; 4,186 candidates; 304 seeds; 3 sets of 1,414, 357 and 301 species (4,114, 916 and 736 reactions; cliques of 3, 34 and 267); nested share 1.0; chain depth 3. Pass.

**2. Mixing (the decidability gate; structure only, no scan).** Share of the 8,154 balanced directed reactions whose exact reaction no longer exists in the copy, and Jaccard overlap of the copy's directed reaction set with the real one:

| Null | Draws | Mean share changed | Mean Jaccard | Share changed after 1 / 2 / 5 / 10 / 20 moves per unit (draw 0) | Same, with hubs and tier-0 species deleted from every reaction |
|---|---|---|---|---|---|
| A (isomer) | 2 | 0.520 | 0.334 | 0.22 / 0.33 / 0.43 / 0.50 / 0.51 | 0.486 changed, Jaccard 0.334 |
| **B (half swap)** | **5** | **0.737** | **0.176** | 0.26 / 0.38 / 0.55 / 0.66 / 0.73 | 0.665, 0.203 |
| C (strict) | 2 | 0.662 | 0.223 | 0.34 / 0.45 / 0.58 / 0.63 / 0.66 | 0.565, 0.271 |
| Bconv | 2 | 0.529 | 0.338 | 0.22 / 0.30 / 0.43 / 0.48 / 0.53 | 0.415, 0.420 |

The design's thresholds for Null B (at least 30% changed, mean Jaccard below 0.8) are met by a wide margin in every draw (0.729 to 0.747 changed; Jaccard 0.168 to 0.181). **The study is decidable.** Freedom: 27,547 formula-difference classes of halves (17,924 of size 1); every movable unit has at least one half with a partner; the largest classes hold 1,716, 1,339 and 980 halves. Rewiring takes about 20 to 28 CPU s per Null-B draw and 8 to 10 s for the others.

Mixing is still rising slowly at 20 moves per unit (Null B: 0.66 at 10, 0.73 at 20). An under-mixed null sits closer to the real network, which makes kill easier and support harder. 20 is kept (D4); the share changed in every real draw is recorded and the gate thresholds are re-checked on the real Null-B draws (R4).

## Decision rules (as in U1)

Only the biochemical network is tested (the abiotic network, 717 reactions with species named by formula, is too small for hierarchy and is not run).

- **Kill (of the "biological organisation" reading).** n_sets (real 3) and nested_share (real 1.0) both lie inside the central 95% of Null B. Atom bookkeeping alone then gives nested tiers, and T14's support is downgraded to "real chemistry is tiered".
- **Support (as designed, unchanged).** n_sets (real 3) and nested_share (real 1.0) both lie above the central 99% of Null B and of Null C. The planted check showed this rule cannot fire when the real nested_share is 1.0 and more than about 0.5% of null draws have any nested pair (see C1), so **in practice the sealed outcomes are kill or not killed**. Support is not reachable in this design. That is stated here before any real-network null exists.
- **Not killed.** Anything other than kill. Report where the real values fall under each null. This does not upgrade T14's support. It says only that atom balance alone did not reproduce the tiers in the central 95% of Null B.
- **Reported only:** Null A and Bconv flags; n_seeds, largest and chain_depth positions and quantiles under every null (T14's second finding, that rewired networks are 3 to 4 times more autocatalytic, is re-asked under atom balance); share changed and Jaccard of every draw.
- **R4. Mixing in the real draws.** If the mean share changed over the 200 real Null-B draws is below 0.30 or their mean Jaccard is 0.8 or more, the verdict is "not decidable" whatever the statistics say (`real_verdict` applies this).

**C1. A proposed support rule, reported only.** The planted check showed the design's support rule is unworkable. nested_share is capped at 1.0, and the real value is 1.0. "Above the central 99%" needs the null's q0.995 below 1.0, so the rule fails whenever more than about 0.5% of null draws contain any nested pair. Atom-balanced nulls keep such pairs in 10 to 12% of draws on the planted networks, because they keep parts of the planted cores. The design's support rule therefore flagged 0 of 5 planted networks. Replacing nested_share with chain_depth (n_sets and chain_depth above the central 99% of B and C) flags 5 of 5 planted networks and 0 of 5 controls. But this replacement was proposed **after** the planted calibration ran, and it is not one of the fallbacks stated in advance (F1 to F5). Under the project rule, a deciding rule changed after calibration would make the study invalid. C1 is therefore computed and reported as `support_c1_reported_only` and never decides the verdict. The kill rule is the design's, unchanged; the cap does not affect it, because it asks whether the real values lie *inside* the null. Nothing about the real network's nulls had been computed when C1 was proposed.

The gate showed every other rule workable.

## Fallback rules (stated before calibration)

- **F1. Time.** The dry run measures the median CPU seconds of a Null-B or Null-C draw (rewire plus scan) and saves `fallback` in `scripts_out/t17_dryrun.json`. If that median exceeds 60 s, `real` uses 100 draws per deciding null and a fixed random sample of 1,000 candidate seeds (the observed network too), as in T14's D8. Otherwise the full counts (D9) are used. `real` reads the flag; it does not re-time.
- **F2. A part that dies or times out** (crash, machine sleep, app restart) is re-run with the same arguments. Draws are seeded by index, so a re-run gives the same draws. Parts are merged by draw index; `real_verdict` refuses to run with any draw missing.
- **F3. A draw that raises** (a rewire that changes tier 0, which the move rule should make impossible, or an LP error) stops the part. It is reported, and the draw is re-run once from the same seed. If it fails again, the run stops and the study is reported as not completed, with the error; no draw is skipped or replaced.
- **F4. Compute ceiling.** If the full `real` run cannot finish within 7 days of the seal at 1 to 2 cores, the remaining draws are dropped and the verdict is computed on the first N complete draws per null, provided N is at least 100 for Nulls B and C. Below 100, the study is reported as not completed.
- **F5. KEGG input changed.** If `kegg_hash()` does not match the sealed value (for example the raw folder was lost), the entries are re-fetched with the same script. If the formulas parsed from the new fetch give a different set of balanced reactions, the study stops and needs a new seal.

## Planted check (`planted`, `planted_merge`; run; synthetic only)

**Worlds.** T14's sparse big world (1,500 species, 600 reversible pairs, mass-balanced), the same seeds and networks as T14's planted check. The integer "mass" is the only element, so every background reaction balances. `sparse_planted`: three nested, mass-balanced autocatalytic cores planted on top (T14's planting). `sparse_samedeg`: the planted network rewired once by Null B, so it keeps degrees and atom balance but loses the cores. `sparse_background`: no cores. 10 replicates each of `sparse_planted` and `sparse_samedeg`, 5 of `sparse_background`, with 50 draws per null (A, B, C; Bconv not run, to save time; T14 used 100 draws, cut here because under the required background priority each process got about 20% of a core and a replicate took 20 to 40 minutes). With 50 draws, the 99.5th percentile is computed with numpy's linear interpolation and falls between the two largest draws, so a flagged statistic sits at or near the top of the null. Output `scripts_out/t17_planted.json`.

**Criteria (U1 gate 3).** The design's criterion: planted cores flagged (n_sets and nested_share above the central 99%) against each of Nulls A, B and C in at least 8 of 10 replicates, and controls flagged in at most 1 of 10. **Under the design's rule this criterion fails** (0 of 10 planted networks flagged; see C1). Its consequence is the one stated under the decision rules: support is not reachable, and the study can only kill or not kill. The kill rule's own planted behaviour is reported in the table. It should kill the same-degree controls and should not kill the planted networks. The C1 columns are reported only.

**Results** (`scripts_out/t17_planted.json`, final merge: 10 replicates of `sparse_planted` and of `sparse_samedeg`, 5 of `sparse_background`, 50 draws per null).

| Scenario | Reps | Design's rules: kill / not killed / support | Design's support flag by A, B, C (each) | C1 (reported only): flagged by all of A, B, C | Null draws with any nested pair (A, B, C) | Mean null q0.995 of n_sets (A, B, C) |
|---|---|---|---|---|---|---|
| sparse_planted (observed 4 sets, depth 4) | 10 | 0 / **10** / 0 | 2, 0, 0 | 10 of 10 | 10%, 13%, 10% | 2.90, 2.98, 2.98 |
| sparse_samedeg (observed mean 1.1 sets) | 10 | **10** / 0 / 0 | 0, 0, 0 | 0 of 10 | 9%, 11%, 10% | 2.05, 2.83, 2.70 |
| sparse_background (no cores, 1 set) | 5 | **5** / 0 / 0 | 0, 0, 0 | 0 of 5 | 0.4%, 0.4%, 0.4% | 1.15, 1.15, 1.15 |

- **Kill rule (deciding) behaves as required.** It kills 10 of 10 same-degree controls and 5 of 5 background networks. It kills 0 of 10 planted networks.
- **The design's support rule cannot fire,** as stated under the decision rules. It flagged 0 of 10 planted networks against all of A to C. **C1** (reported only) flags 10 of 10 planted networks and 0 of 15 controls.
- About 89 to 90% of reactions change under every null in the synthetic world. Null A is this free only because the synthetic world has one element.
- Median null scan: about 0.47 CPU s per synthetic draw.
- **Atom-balanced nulls keep a planted core in some draws,** up to 3 nested sets against the planted 4. T14's degree nulls never did this. For the real network (3 sets, depth 3), this means even the reported-only C1 rule would be blocked if about 0.5% of null draws kept the real tiers. The deciding kill rule asks the opposite question: do the real values lie inside the central 95% of Null B?

## Ways it could be fooled, and limits

- **The synthetic world has one element.** With mass as the only element, many species share a "formula", so Null A is far freer in the synthetic world than in KEGG (it changed about 90% of synthetic reactions, 52% of real ones). The planted check tests the pipeline and the rules, not how constrained real chemistry is.
- **Atoms are not all of chemistry.** Null B keeps elements but not charge, bond chemistry, thermodynamics or enzyme logic. A rewired reaction such as "glucose + NAD+ -> X + NADH" may balance and still be chemically absurd. "Not killed" says the tiers are more than degree plus atom bookkeeping, not that they are more than "real chemistry".
- **Unbalanced reactions stay fixed.** 248 directed reactions (224 unbalanced, 24 with formula-less species) and the 44 tier-0 reactions never move; 148 of 4,201 pairs are frozen in every null. If they carry the tiers, every null keeps them. The planted check cannot test this. (The real network's frozen pairs are listed in the gate output by count only.)
- **Mixing not at a plateau** (see gate). Reported per draw.
- **Discreteness.** As in T14, the hierarchy statistics are small integers and shares; quantiles are published.
- **Formulas are one snapshot of KEGG** (fetched 2026-11-25) and may differ from those the authors used in 2022. Protonation states in KEGG are not always consistent (H is an element here), which is one reason 224 reactions do not balance.
- **One database decides,** as in T14. KEGG is evolved metabolism, not prebiotic chemistry.

## How to run after the seal

From `experiments/`, single-threaded, `taskpolicy -b nice -n 20`, OMP/OPENBLAS threads = 1, one or two processes:

1. `dryrun B 0 200`, `dryrun C 0 200`, `dryrun A 0 200`, `dryrun Bconv 0 100` in parts of about 25 draws, then `dryrun_verdict` (blind: flags and times only; fixes F1).
2. `real B A B`, `real C ...`, `real A ...`, `real Bconv ...` in parts of about 25 draws (about 30 to 40 CPU s per Null-B draw, so about 2 h of one core per 200 Null-B draws), then `real_verdict`.

Estimated total about 8 to 10 core hours for dry run plus real.

## Decisions to confirm at the seal

0. **The design's rules decide; C1 is reported only.** Outcomes in practice are kill or not killed (see C1).
1. **Null B as the deciding null, Null C for support, A and Bconv reported only** (the U1 design; Bconv added as the literal "coupled halves" reading).
2. **20 moves per unit** (D4) with the real-draw mixing re-check (R4).
3. **KEGG hash check** (F5): already in `load_real`, so it applies to the gate, the dry run and `real`.
4. **Dry run before real** (as T14), at about half the real cost; or skip it and fix F1 from the gate timing (rewire 20 to 28 s plus a scan of about 7 s, well under 60 s).
5. **Files to hash at the seal:** `scripts/t17_analysis.py`, `scripts/t17_fetch_kegg.py`, `scripts_out/t17_gate.json`, `scripts_out/t17_planted.json`, this file, and `raw/kegg/ids.txt`.

## Decisions confirmed at the seal

1. **The design's rules decide; C1 is reported only.** Kill: n_sets and nested_share both inside the central 95% of Null B. Support uses the design's rule, which the planted check showed cannot fire here, so the outcomes in practice are kill or not killed. C1 (n_sets and chain_depth above the central 99% of B and C) is computed and reported and never decides. The coordinating agent confirmed this; a chain_depth support rule belongs in a new prereg on a network not used for calibration.
2. **Nulls.** Null B decides kill. Nulls B and C are named in the (unreachable) design support rule. Nulls A and Bconv are reported only. 20 moves per unit, with the real-draw mixing re-check R4.
3. **KEGG hash check (F5)** is applied in `load_real`. The formula snapshot is the one hashed below (`raw/kegg/ids.txt` plus the batch hash in `t17_gate.json`).
4. **Dry run before real.** It is blind, using one Null-B rewire of the real network as a stand-in, and it fixes the F1 time fallback. Then `real`, in parts of about 25 draws, single-threaded under nice 20, from a detached runner with a pid file. A part that dies is re-run with the same arguments (F2).
5. **The gate was re-run under the sealed script hash.** Its numbers match the earlier gate exactly; only the hash and timing fields differ.
6. No other change. Any change after this seal makes the verdict invalid.
