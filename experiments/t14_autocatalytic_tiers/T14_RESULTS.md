# T14 result: KEGG biochemistry's nested autocatalytic tiers are not reproduced by rewired networks; sealed verdict support (biochemical network only)

Prereg: `docs/prereg/t14_autocatalytic_tiers.md`, sealed in 78bd277 (`HASHES.txt`). Script: `scripts/t14_analysis.py` (sha256 48ecdd36…). Output: `scripts_out/t14_real.json`. Run detached in parts, 200 + 200 rewires per database; the time fallback was not triggered.

## Claim

Peng, Linderoth and Baum 2022 (PLoS Comput. Biol. 18:e1010498, doi:10.1371/journal.pcbi.1010498) expanded a KEGG-derived biochemical network (4,216 species, 8,402 reactions) and an abiotic network (277 species, 717 reactions) from fixed food sets.

In the biochemical network, 304 species are "singleton supported seeds". These fall into three cliques whose self-sustaining sets (SDASs) have 301, 357 and 1,414 species and "are nested". The authors write that "the abiotic and biochemical networks share multiple properties, including hierarchically organized SDASs". They ran no randomised comparison.

The test rewires each network. Products are swapped between reactions, so every species keeps its counts as reactant and as product, every reaction keeps its size, and the tier-0 food system is unchanged. It then asks whether rewired networks also give several nested sets. There are two nulls:
- **swap:** a plain degree-preserving product swap.
- **strict:** hubs and tier-0 species are frozen, and swaps stay within degree classes.

## Gate (before the seal)

All published numbers were reproduced exactly:
- **Biochemical network:** tier 0 of 30 species and 44 reactions; 304 seeds; nested sets of 301, 357 and 1,414 species.
- **Abiotic network:** 12 seeds and one set of 91 species.

## Sealed verdict: support (hierarchy rule, biochemical network)

| Biochemical network | Real | Swap null (2.5–97.5%, median) | Strict null (2.5–97.5%, median) |
|---|---|---|---|
| Distinct seed-induced sets | **3** | 1–1 (1) | 1–1 (1) |
| Share of nested set pairs | **1.0** | 0–0 (0) | 0–0 (0) |
| Depth of nested chain | **3** | 1–1 (1) | 1–1 (1) |
| Supported seeds | 304 | 1,294–1,397 (1,349) | 938–1,049 (1,003) |
| Largest set (species) | 1,414 | 3,137–3,291 (3,214) | 2,490–2,609 (2,550) |

- **The rule's two statistics.** The number of sets and the nested share both lie above the central 99% of both nulls, which is the sealed support condition. In 200 + 200 rewired copies, a second set appears in at most about 1 in 200.
- **The other two statistics go the other way.** Rewired networks have about 3–4 times *more* seeds and a largest set about twice as big. One giant self-sustaining set swallows everything.
- **The plan's 3-of-4 rule (reported only) gives "partly".** Its four statistics all lie outside both nulls, but in mixed directions: seed count and largest set fall *below* the null, while the two hierarchy statistics fall above it. The planted check had shown that this rule cannot detect planted nested cores.

## Abiotic network (reported only)

The real abiotic network has one set (12 seeds, 91 species), so nothing is nested in it. Its rewired copies also give one set in the large majority of draws, with up to 2 at the 97.5th percentile. The hierarchy statistics are inside the null, so the abiotic data are consistent with the null and do not contradict the biochemical result. As in the biochemical network, rewired abiotic networks have more seeds (median 65 against 12) and a larger set (224 against 91).

## Reading

- **What it shows.** In KEGG biochemistry, the three nested autocatalytic tiers are a property of the specific chemistry, not of how many reactions each species takes part in. Shuffling which products each reaction makes, while keeping every degree, destroys the tiers in essentially every copy.
- **What it also shows, and this matters as much.** Shuffled networks are *more* autocatalytic, not less. More species can seed a self-sustaining set, and the set they seed is much larger. Real biochemistry is organised into a nested ladder because its autocatalysis is *constrained*. A small core enables a larger one, which enables a larger one again, instead of everything percolating at once.
- **What it does not show.**
  - The rewired reactions do not conserve atoms (prereg limit 1). Part of the "constraint" may simply be mass balance and real chemical feasibility, which a degree null throws away. A null that keeps element balance, built from KEGG formulas, would separate "chemistry is constrained" from "biochemistry is organised in tiers". That is the obvious follow-up.
  - The result covers the biochemical network only. The abiotic network has no hierarchy to test (one set), so the paper's "share" claim is supported only for its biochemical half.
  - KEGG is evolved metabolism, not prebiotic chemistry.

## What it means for us

- **For the metabolism-first and autocatalytic-set routes,** this is the first result in this series that *supports* a published structural claim against a proper null. Nested tiers that build on each other are a real, non-trivial feature of biochemistry's network. The reason is not hub degrees: degree-matched random chemistry gives one big undifferentiated set.
- **Next study.** The element-balance null above would show whether the tiers come from atom bookkeeping or from biology's particular choices.
- It is a strong, positive and cheap result, and could be worth a friendly note to the authors. The owner decides.
