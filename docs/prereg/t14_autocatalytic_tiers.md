# Pre-registration (T14): is the tiered autocatalytic structure of biochemistry more than its degree sequence gives?

Status: DRAFT, written 2026-11-25 by the T14 prep agent. This is study N3 in `docs/plans/next_studies_2026-11-25.md`. `gate`, `timing`, `planted` and the dry run have been run. `real` has not been run. The script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t14_autocatalytic_tiers/scripts/t14_analysis.py` with its current sha256 (`48ecdd36d68b3a7a281a56b85755e85c6ee67a0d212b99a0940bb5197cb57f62`). Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is where the real networks' four statistics fall in the distribution of the same statistics over rewired copies of those networks. No rewired copy of either real network has been scanned outside the dry run, and the dry run printed and saved no statistic.

- **The observed statistics are published, and the gate recomputed them.** Biochemical network: 304 seeds, 3 sets, nested share 1.0, largest set 1,414 species (chain depth 3). Abiotic network: 12 seeds, 1 set, nested share 0, largest 91. These are the claim being tested, not a peek at the answer.
- **No real null value has been computed or seen.** `real` has never run.
- **Dry run (the real code, on a rewired stand-in).** The stand-in is one swap rewire of each real network (seeded). Its nulls were drawn and scanned, so null draws from essentially the same ensemble as the real nulls now exist in `work/dryrun_blind/` (gitignored). They were never opened, printed or summarized, apart from scan times and LP counts per draw. `dryrun_verdict` prints only per-statistic flags (inside 95% / outside 99%), the verdict and scan times about the stand-in. Combined with the published observed values these flags still leak little: they say where a degree-matched random network sits in its own null, not where the real one does.
- **The planted check uses synthetic networks only.** Their backgrounds come from a generator whose parameters (species counts, hub counts, side-size shares) were set from descriptive shares of the real networks, not from their degree sequences or any null.
- **Earlier drafts.** The gate ran under hashes `f5b0d0d5...` and `caa41adb...` before the current one, with identical numbers each time. `timing` (synthetic only) ran under earlier generators and then under `caa41adb...`. The whole planted check ran once under `caa41adb...`; two sparse replicates before that ran before the revised rule (C3) existed and were discarded. Under `caa41adb...` a rewired biochemical scan took about 30 to 40 s, so the expansion and LP code were made faster without changing what they compute (lists instead of numpy scalars in the expansion; the LP matrix built sparse instead of dense, which is what scipy hands HiGHS anyway), and the fallback timing was switched to CPU seconds (D8). Everything was then re-run under the current hash: gate (same numbers), timing (identical outputs), and the whole planted check, whose observed values and null arrays are identical to the `caa41adb...` run in all 76 synthetic networks. A first dry run under `caa41adb...` was stopped part way and its null files deleted unopened. Everything in `scripts_out/` now comes from `48ecdd36...`.
- **What this does to my expectation.** In every synthetic background, rewired copies hold one supported set, never a nested hierarchy. If the real biochemical rewires behave the same way, the real network's three nested sets will fall outside. But the real network is much larger and more hub-dominated than the synthetic ones, and its rewires take about 3 times longer to scan than the real network does (about 7 CPU seconds against 2.4; most of their expansions are distinct, as in the real one), so I hold no firm expectation.

## Claim under test

Peng Z, Linderoth J, Baum DA. 2022. "The hierarchical organization of autocatalytic reaction networks and its relevance to the origin of life." PLoS Comput Biol 18:e1010498. doi:10.1371/journal.pcbi.1010498 (PMC9491600). Read in full from `experiments/t14_autocatalytic_tiers/raw/europepmc/PMC9491600.txt`.

- Discussion, verbatim: "We found that the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs converting simple materials and energy to more complex species."
- Results, verbatim: "Network expansion from the ultimate food generates a 30-species, 44-reaction tier-0 system (S10 Table). Treating this tier-0 system as external food, 304 of the 4186 non-tier-0 species are singleton supported seeds able to induce a tier-1 SDAS (S11 Table). These seeds belong to three cliques: the 267-species clique bio-1a induces SDAS-bio-1a (301 species; 736 reactions; S12 Table); the 34-species clique bio-1b induces SDAS-bio-1b (357 species; 916 reaction; S13 Table); the 3-species clique bio-1c induces SDAS-bio-1c (1414 species; 4114 reaction; S14 Table). These SDASs are nested, with SDAS-bio-1c including the entirety of SDAS-bio-1b, which includes the entirety of SDAS-bio-1a."
- Abiotic network, verbatim: "Twelve of the 272 non-tier-0 species constitute the clique abio-1 inducing a tier-1 SDAS, SDAS-abio-1 (S3 Table) of 91 species and 220 reactions (S4 Table)."
- Food, verbatim: "we chose {H2, CH4, NO, FeS2, visible light} and {H2O,CO2,NH3,H2S,H2SO4,H2SO3,HSO3−,H3PO4,H4P2O7} as the ultimate food, respectively."

**Why it might be an artefact.** Network expansion from a fixed food set, plus a feasibility LP, may give seeds, several induced sets and nesting in any large network with a few hub species (water, H+, ATP, NAD). The paper has no randomized comparison (no match for "rewir", "null model", "shuffl", "random network" or "degree-preserving" in its text). Prior art (`experiments/t14_autocatalytic_tiers/PRIOR_ART.md`) finds no citing work that runs one.

**H1 (the authors' reading).** The nested tier-1 structure is a property of the specific chemistry: rewired networks with the same degrees do not show it.

**H0.** Rewired networks that keep every species' reactant and product counts, every reaction's size and the tier-0 system show as many nested sets.

## Inputs (exact)

All from the paper's PLoS supplement, `https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1010498.sNNN`, saved in `raw/plos/` (gitignored: `.gitignore:41:experiments/*/raw/`, confirmed with `git check-ignore`). The xlsx files are read with a stdlib zip/XML reader (no macros, nothing evaluated) under `python3 -I`. The three decision inputs are re-hashed at the start of every run and the run stops on a mismatch.

| File | Source id | sha256 | Use |
|---|---|---|---|
| S1_Table.xlsx | s006 | ffa6f52f9326754a0025c826a80e59e449bd23d95e86135b73b0f0149b785ac3 | abiotic network, 717 one-way reactions, 277 species |
| S2_Table.xlsx | s007 | 8ace73e1e69d29d35d7c8471c5633812a1e4b3a27ba195b77c4b92d14b321fe9 | biochemical network, 8,402 reactions (4,201 reversible pairs), 4,216 species |
| data/food_sets.tsv (in repo) | authors' code | 466965aa53b1d4fbce0f5f238804f2976d4813cc25fdeec99dfc9c18787bce3d | ultimate food: 15 KEGG ids (bio), 5 (abio) |
| S3_Table.xlsx | s008 | cc8e3ebbe6ec63c04f55042015843fcbfd56aae07535cf866c51237c8b626124 | gate only: abio supported seeds |
| S10_Table.xlsx | s016 | c4b8bef5ddc5e9798371d4b73719d471ee5b63a196006c5e98283712c50307cb | gate only: bio tier 0 |
| S11_Table.xlsx | s017 | 7424e3ce56c3b57c3be8aeccb18506135e62f0fea84ead88db26c2738d97bbe9 | gate only: bio supported seeds |
| PMC9491600.xml | Europe PMC fullTextXML | a2d2756c77ded95e68cb5a43bb49e283a529a5507ba03296a167abc0348290fe | claim text |

The biochemical food list is the `input_food_list` in the authors' `FromSelectedFoodSet_to_LinProg_KEGG.py` (S2 Python Script, s028): the paper's nine species plus six ion and hydrate forms. The nine-species file `Biochem_ufs.txt` (S3 Python Script, s029) gives the same tier 0, and the gate checks both. The authors' scripts were read as text and never run. The LP rule (`b_positive = 0.001`, HiGHS) comes from the same script.

## Gate (`t14_analysis.py gate`; run; passed)

Run under the current hash; output in `scripts_out/t14_gate.json`.

| Check | Published | Rebuilt | Pass |
|---|---|---|---|
| bio species / reactions | 4,216 / 8,402 | 4,216 / 8,402 | yes |
| bio tier 0 (species, reactions) | 30, 44 (S10 Table) | 30, 44; same species as S10 | yes |
| bio non-tier-0 candidates | 4,186 | 4,186 | yes |
| bio singleton supported seeds | 304 | 304; same list as S11 | yes (within 5%: exact) |
| bio set sizes, species | 1,414, 357, 301 | 1,414, 357, 301 | yes (exact) |
| bio set sizes, reactions | 4,114, 916, 736 | 4,114, 916, 736 | yes |
| bio clique sizes | 3, 34, 267 | 3, 34, 267 | yes |
| bio nesting | 1c contains 1b contains 1a | chain depth 3, nested share 1.0 | yes |
| bio nine-species food | (same tier 0) | 30, 44 | yes |
| abio species / reactions | 277 / 717 | 277 / 717 | yes |
| abio tier 0 | 5 species, 0 reactions | 5, 0 | yes |
| abio candidates | 272 | 272 | yes |
| abio seeds / set | 12 seeds; 91 species, 220 reactions (S3, S4) | 12, same list as S3; 91, 220 | yes |

A full scan of the real biochemical network takes 2.4 CPU seconds (1.6 to 3.4 s wall, depending on machine load); the abiotic one takes 0.03 s.

## Fixed decisions

- **D1. Expansion, tier 0, seeds and support** exactly as in the gate (module docstring): expansion to closure; candidates are every species used by a reaction and not in tier 0; one seed at a time; induced set = expansion of tier 0 plus the seed, minus tier 0; supported if the LP `A x >= 0.001, x >= 0` is feasible (HiGHS status 0). A species that no reaction in the induced set produces makes the LP infeasible, and the code checks for this before calling the LP (same answer, faster). LP results are cached by induced species set.
- **D2. Statistics.** n_seeds (supported singleton seeds), n_sets (distinct induced sets among them), nested_share (share of pairs of distinct sets in which one contains the other; 0 with fewer than two sets), largest (species in the largest set). chain_depth (longest chain of strictly nested sets) is reported only.
- **D3. Units.** A unit is a reversible pair (a reaction and its exact reverse) or a one-way reaction. Every null moves only right-side stubs (a species with its coefficient) between units and then rebuilds each reverse reaction as the exact reverse. So every species keeps its count as reactant and as product, every reaction keeps its sizes and coefficients, reversibility is kept, and the food set is unchanged. A stub may not land in a unit whose left side already holds that species, or duplicate a species on a right side. Conflicts after the permutation are repaired by random swaps within the same group (up to 400 rounds), and the run stops if any remain.
- **D4. Null 1, "swap" (decides kill and support).** All right-side stubs move within two groups (paired units, one-way units), except that the tier-0 system is kept exactly: units in R0 do not move, and no moved reversible unit may end with a right side made only of tier-0 species (its reverse would then fire from food and enlarge tier 0). The rewired network's tier 0 is asserted equal to the real one.
- **D5. Null 2, "strict" (decides support).** As swap, and in addition the stubs of frozen species never move (tier-0 species and the top 1% of species by total degree), and the other stubs move only within groups of (paired or not, degree class floor(log2 degree)). So every reaction also keeps the degree-class profile of its products. This replaces the plan's element-balance null (change C2).
- **D6. Reported-only null, "swap_plan".** The plan's swap exactly as written, with no tier-0 protection; 50 draws per network.
- **D7. Counts.** 200 swap and 200 strict rewires per database, seeded `[20261126, 6, db, null, i]`. All candidates are scanned in each.
- **D8. Time fallback (the plan's rule, stated here before calibration).** The plan says: "Time one network first; if it takes more than 60 s, cut to 100 rewires and sample 1,000 seeds." Time is measured in CPU seconds of the scanning process, so a loaded machine cannot trigger it. A real network scan takes 2.4 CPU s, so the fallback does not apply to the real networks. Because a rewired network scans slower, the same 60 s threshold is also applied to the median CPU time of the dry run's rewired-stand-in null scans (both nulls, each database), measured once and saved in `scripts_out/t14_dryrun.json` as `fallback`. If true, `real` uses 100 rewires per null and a fixed random sample of 1,000 candidate seeds per network (the observed network too); n_seeds is then scaled to the full candidate count. The dry run measured a median of about 7 to 8 CPU s (see below), so the fallback is **not** triggered, and `real` reads that flag rather than re-timing.
- **D9. Quantiles.** numpy `quantile` (linear) on the null values; "inside the central 95%" means within [q0.025, q0.975] inclusive; "outside the central 99%" means above q0.995 or below q0.005.

## Decision rules

The primary rule is the hierarchy rule (`PRIMARY_RULE = "hier"` in the script). The plan's rule is computed and reported next to it.

**Primary (hierarchy rule, C3).** In the biochemical network:
- **Kill:** n_sets and nested_share both lie inside the central 95% of the swap null.
- **Support:** n_sets and nested_share both lie above the central 99% of both the swap and the strict null.
- **Partly:** anything else.
- The abiotic network is reported only: its flags and an `abio_contradicts` flag (either hierarchy statistic below the central 99% of both its nulls). n_seeds and largest are reported with their positions.

**Plan rule (reported).** Kill: in the biochemical network at least 3 of 4 statistics inside the central 95% of the swap null. Support: at least 3 of 4 statistics outside the central 99% of both nulls, in the same direction in both databases. Also reported: whether at least 3 of 4 are outside both nulls in the biochemical network alone, and the plan rule's kill against the plan's literal null (swap_plan).

## Changes from the plan, made before the seal

- **C1. Both deciding nulls keep the tier-0 system.** The plan's swap, applied as written, moves stubs into and out of the food-driven tier-0 reactions. In the synthetic `timing` networks one such rewire swelled tier 0 from 8 species to 424 to 1,030 in every big network (and from 5 to 163 to 248 in three of four small ones), leaving almost nothing to seed: the plan null gave a median of 0 seeds and 0 sets in every big synthetic network of the planted check. Any real network with seeds would then sit "outside" such a null on every statistic, a guaranteed false support. Tier 0 is not what the claim is about (the paper treats it as given food), so both nulls keep it fixed (D4). The plan's literal swap is still run and reported (D6).
- **C2. The stricter null keeps degree classes and hubs, not element balance.** The plan asks for a null that "also keeps element balance by swapping only between reactions with the same product formula count". S1 and S2 carry no molecular formulas, so element balance cannot be checked from the deposited data. The strict null (D5) instead freezes hubs and tier-0 species and swaps only between species of the same degree class. It is stricter than swap (fewer moves; each reaction keeps its product profile), but it does not keep atoms. A true element-balance null would need KEGG compound formulas, which the user can decide to fetch (see the decisions below).
- **C3. The deciding statistics are the two hierarchy statistics.** The planted check showed the plan's 3-of-4 support rule cannot detect planted nested cores: planting three nested cores changes n_sets and nested_share but leaves n_seeds and largest inside the null. So the plan rule gave support in 0 of 14 planted networks, against 14 of 14 for the hierarchy rule, with no false support from either rule in 24 random controls. The plan's "same direction in both databases" clause has a second problem: the real abiotic network has a single tier-1 set (the paper says so, and the gate confirms it), so its nested_share is 0. A null that also gives one set can never place it outside, so the clause could not be met by the abiotic data whatever the biochemical network shows. The abiotic network is therefore reported, not ruled on. The form of the rule changed; its thresholds (95% inside for kill, 99% outside both nulls for support) are the plan's.
- **C4. Planted check counts.** 100 rewires per null per synthetic network (not 200), and 20 plan-null draws, to keep each run under 20 minutes. 10 replicates per sparse scenario and 4 per dense scenario.

## Planted check (`t14_analysis.py planted`, `planted_merge`; run; synthetic networks only)

**Synthetic worlds.** Each replicate pairs a "big" network (standing in for biochemistry; reversible pairs) and a "small" one (standing in for the abiotic network; mostly one-way reactions). Backgrounds are random and mass-balanced: every reaction conserves an integer "mass", hub-only reactions join hub species only, and specific species join with hubs, following side-size shares like the real networks'. Two worlds: sparse (600 pairs over 1,500 species in big) and dense (1,550 pairs). **Planted cores** are made of new species. Core k has members X1..Xm (m = 8 big, 6 small) with steps Xi + in_i -> X(i+1) and a branching step Xm + in_m -> X1 + X2, all mass-balanced. Core 1 feeds on food of mass 1; core k feeds on core k-1's members. A link step Xm -> X1 + Y (+ waste) produces a seed of the layer below, so seeding core k also brings up every lower core, and the planted chain sits on top of the background's own set. Three nested cores are planted in the big network and one in the small one.

**Scenarios.** `planted`: as above. `samedeg`: the planted network rewired once by swap, so the degrees are the same but the cores are destroyed (the user's "pure random networks with the same degrees"). `background`: no cores at all. Output: `scripts_out/t14_planted.json` (all parts computed by `48ecdd36...`).

| Scenario | n | Hier rule: kill / partly / support | Plan rule: kill / partly / support | Mean observed n_sets, nested_share (big) | Null medians n_sets, nested_share (swap, strict) |
|---|---|---|---|---|---|
| sparse_planted | 10 | 0 / 0 / **10** | 0 / 10 / 0 | 4.0, 1.0 | 1, 0 ; 1, 0 |
| dense_planted | 4 | 0 / 0 / **4** | 0 / 4 / 0 | 4.0, 1.0 | 1, 0 ; 1, 0 |
| sparse_samedeg | 10 | **10** / 0 / 0 | 10 / 0 / 0 | 1.0, 0.0 | 1, 0 ; 1, 0 |
| dense_samedeg | 4 | **4** / 0 / 0 | 4 / 0 / 0 | 1.0, 0.0 | 1, 0 ; 1, 0 |
| sparse_background | 10 | **10** / 0 / 0 | 9 / 1 / 0 | 1.0, 0.0 | 1, 0 ; 1, 0 |

Rates. Hierarchy rule: support in 14 of 14 planted networks (no false kill, 0/14); false support 0 of 24 random controls; kill in 24 of 24 controls. Plan rule: support in 0 of 14 planted networks (the miscalibration behind C3); false kill 0 of 14; false support 0 of 24; kill in 23 of 24 controls.

Other things the planted check showed:
- n_seeds and largest barely move when cores are planted (sparse: mean observed 312 seeds against a null median of 330; largest 437 against 446). They measure scale, not tiering.
- The plan's literal null (swap_plan) gave 0 seeds and 0 sets in every big synthetic network, because its tier 0 swelled to cover almost the whole network.
- In the small sparse world the background sometimes has no supported set while its rewires have one, so the small network can fall below its null on n_seeds and n_sets (`abio_contradicts` 5 of 10 in sparse_background, 0 in the planted scenarios). That is one reason the abiotic network is reported only.
- Median rewired scan time: 0.2 CPU s (sparse big) and 0.8 CPU s (dense big).

## Dry run (`dryrun`, `dryrun_verdict`; run; blind)

The real code path (`null_part` and `final`) with each real network replaced by one swap rewire of itself (stream `[20261126, 99, db]`), 200 swap and 200 strict null draws per database (stream 5, separate from the real stream 6), and 50 plan-null draws. Null draws are in `work/dryrun_blind/` (gitignored), never opened. Output `scripts_out/t14_dryrun.json`:

| Network | n_seeds | n_sets | nested_share | largest | Inside 95% of swap | Outside 99% of both |
|---|---|---|---|---|---|---|
| bio stand-in | inside | inside | inside | inside | 4 of 4 | 0 of 4 |
| abio stand-in | inside | inside | inside | inside | 4 of 4 | 0 of 4 |

- Hierarchy rule (primary): **kill** (both hierarchy statistics inside the central 95% of the swap null); `abio_contradicts` false.
- Plan rule: **kill** (4 of 4 inside); biochemical-only 3-of-4 outside: false.
- Median null scan time: 7.57 CPU s (bio), 0.04 CPU s (abio), so `fallback` = false (D8).
- As intended, a degree-matched random network reads as inside its null on every statistic. The pipeline (parts, merge, completeness check, both rules) runs end to end.

## Reported only (no rule attached)

- chain_depth for both networks and its null quantiles.
- The plan rule's verdict, the biochemical-only 3-of-4 flag, and the plan rule against the plan's literal null.
- n_seeds and largest positions relative to both nulls.
- All abiotic flags and `abio_contradicts`.
- Null quantiles (0.5%, 2.5%, 50%, 97.5%, 99.5%) of every statistic under each null, and the observed set sizes.
- Median scan seconds and LP counts.

## Ways it could be fooled, and limits

- **The nulls break chemistry.** Rewiring does not keep atoms, so rewired reactions are not real chemistry. That is the point of a degree null, but a rewired network may be easier or harder to make autocatalytic than any real chemistry. The strict null narrows this but does not close it (C2).
- **Discreteness.** n_sets and nested_share are small integers and shares. If the null almost always gives one set, any real network with two nested sets is "outside". The rule is only as strong as the claim "rewired copies rarely give nested sets"; the null quantiles will be published so a reader can see this.
- **Tier 0 fixed by construction.** The nulls keep tier 0, so the test says nothing about whether the tier-0 system itself is special.
- **One database decides.** With the abiotic network reported only, a support verdict rests on the biochemical network alone. The paper's "share" claim covers both networks, so a support here supports the biochemical half only.
- **KEGG is curated metabolism, not prebiotic chemistry.** Hub species and enzyme-driven pathways shape it. A support verdict says the nesting is more than degrees give in this database, not that it arose prebiotically.
- **Planted cores are clean.** Synthetic cores are tidy, new-species cycles linked straight to the layer below. The real tiers share motifs and many species, which may be harder to tell from a random network than the planted ones.
- **Timing.** The fallback flag (D8) is fixed once by the dry run in CPU seconds and not re-measured.

## How to run `real` after the seal

Single-threaded, `nice -n 20`, OMP and OPENBLAS threads = 1, each command under 20 minutes:

- `real abio swap 0 200`, `real abio strict 0 200`, `real abio swap_plan 0 50`, `real bio swap_plan 0 50` (a minute or less each).
- `real bio swap A B` and `real bio strict A B` in parts of about 45 draws. A rewired biochemical scan takes about 7 to 8 CPU s, so about 50 minutes of single-core time per null (10 to 12 minutes wall per part on the loaded machine).
- `real_verdict` merges the parts in `scripts_out/real_parts/` (it stops if any null is incomplete) and writes `scripts_out/t14_real.json`.

## Sources actually opened

- Peng, Linderoth & Baum 2022, PMC9491600 full text; supplementary S1-S4, S8-S14 Tables and S1-S3 Python Scripts (s006-s009, s013-s019, s027-s029).
- Prior art as listed in `experiments/t14_autocatalytic_tiers/PRIOR_ART.md`: Huson, Xavier & Steel 2024 (PMC11286130); Golnik et al. 2026 (arXiv 2605.25523); Matthäus, Salazar & Ebenhöh 2008 (PMC2289774); Gagrani et al. 2024 (arXiv 2303.14238); Baum et al. 2023 (PMC10618062); Peng et al. 2023 JACS (PMC10591316); Kosc et al. 2025 (PMC12067211); Plum et al. 2025 (PMC12226336); Nandan et al. 2026 (PMC12924792); Peng, Spencer & Baum 2026 (PMC13682562).
- Repo code read (not modified): `experiments/raf_null/` (the stub-permutation and repair idea in D3 follows it), `experiments/raf/raf.py`, `docs/prereg/t13_ligase_global_epistasis.md` and its script (seal pattern).

## Decisions to confirm at the seal

1. **C3, the hierarchy rule as primary.** Accept that only n_sets and nested_share decide, and that the abiotic network is reported only. The alternative is to keep the plan's rule, which the planted check shows cannot give support even for planted nested cores.
2. **C2, the strict null.** Accept the degree-class null in place of element balance, or ask for KEGG formulas to be fetched for a true element-balance null. That would change the script and need a new planted check and dry run.
3. **C1, tier-0-preserving nulls.** Accept that both deciding nulls keep tier 0, with the plan's literal null reported only.
4. **Compute.** About 1.7 hours of single-core time for `real` (D8 fallback not triggered).
5. **Files to hash at the seal:** `scripts/t14_analysis.py`, `data/food_sets.tsv`, `scripts_out/t14_gate.json`, `scripts_out/t14_planted.json`, `scripts_out/t14_dryrun.json`.

## Decisions confirmed at the seal

1. **C3** is accepted. The hierarchy rule (n_sets and nested_share in the biochemical network) is primary. The abiotic network and the plan's 3-of-4 rule are reported only. The planted check showed the plan's rule cannot detect planted nested cores (0 of 14). The abiotic network's single published set makes the plan's "both databases" clause impossible to meet.
2. **C2** is accepted. The degree-class null stands in for element balance, because the deposited tables have no formulas. A true element-balance null built from KEGG formulas is a possible follow-up study. It is not part of this seal.
3. **C1** is accepted. Both deciding nulls keep tier 0 fixed. The plan's literal null (`swap_plan`) is reported only.
4. **Compute.** `real` runs as in "How to run `real` after the seal", in parts, single-threaded under nice 20, from a detached runner with a pid file so that an app restart cannot kill it. A part that dies is re-run with the same arguments. Each part's draws are seeded by draw index, so a re-run gives the same draws.
5. No other change. Any change after this seal makes the verdict invalid.
