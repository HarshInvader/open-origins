# Within a pathway, the order of metabolic assembly does not follow enzyme age or metal catalysis

**Verdict: negative.**

- **Data.** Mrnjavac et al. 2026 (Sci Adv, doi:10.1126/sciadv.aef3128, CC BY) order 408 core KEGG reactions into 49 assembly strata. The same paper labels each reaction's enzyme as LUCA, LBCA or LACA, and lists the reactions reported to run without enzymes.
- **What I tested.** Granick's idea (biosynthetic order recapitulates evolution) combined with the paper's own "LUCA core, then lineage additions, metals before enzymes" view. Prediction: reactions with old enzymes, and reactions that run on metals, sit in earlier strata.
- **Result.** Under the sealed test, which shuffles labels only within a pathway, all three primary predictions fail (Holm-adjusted p 0.39, 0.66, 0.40).
- **What the overall pattern comes from.** Metal-catalysed reactions and Moody-LUCA reactions are clearly earlier across the whole network (global shuffle: p = 0.003 and p = 0.0003). That signal comes entirely from *which pathways* they belong to (central carbon early, cofactors late), not from their position inside a pathway.
- **Age labels.** The LUCA vs lineage label shows no age order even across the whole network. LUCA reactions average stratum 22.7, lineage reactions 22.0.

## Pre-registration and order of work
- **Prereg.** `docs/prereg/metabolic_strata_age.md`, sha256 `406b3e37…`, appended to `HASHES.txt` at 2026-11-18T21:47Z.
  - Before sealing I had seen only the column structure and the marginal label counts.
- **Planted checks.** Both passed before the real labels were used:
  - a label tilted 0.7/0.3 toward the earlier half of each pathway was detected in 99.5% of 200 runs;
  - random within-pathway labels were rejected in 6.0% of runs (limit 8%).
- **Board and compute.** Board task #28 (parent #15). Run with `taskpolicy -b nice`, single process, 5 min. Light compute, so no lock was taken; the prereg stated this in advance.

## Results (one-sided, D = mean stratum of "old" minus "young"; prediction D < 0)

| Test | n old / young | D (strata) | p within-pathway (primary) | Holm | p global (secondary) | Within-pathway percentile: D, p (check) |
|---|---|---|---|---|---|---|
| H1 LUCA vs LBCA+LACA | 198 / 102 | +0.64 | 0.13 | 0.39 | 0.69 | −0.045, 0.009 |
| H2 metal grade A vs rest | 37 / 371 | −4.81 | 0.66 | 0.66 | **0.003** | +0.054, 0.84 |
| H3 Moody 2024 LUCA vs not (held out) | 54 / 293 | −5.21 | 0.20 | 0.40 | **0.0003** | −0.078, 0.012 |
| H4a LUCA vs LBCA | 198 / 77 | −0.62 | 0.007 | — | 0.33 | — |
| H4b LUCA vs LACA | 198 / 33 | **+1.40** | 0.90 | — | 0.76 | — |
| H5 metal grade A or B vs rest | 138 / 270 | −1.42 | 0.99 | — | 0.10 | — |
| Sensitivity: gray counted as lineage | 198 / 118 | +0.59 | 0.16 | — | — | — |

- **H1 fails** and **H4 fails**: the direction reverses for LACA, and the H4 rule required both lineages to show D < 0.
- **H2 fails within pathways.** The global signal is strong, but by percentile, metal-A reactions sit slightly *later* inside their pathways.
- **H3 fails within pathways.** It is strong globally.

## Two things worth following up (exploratory, not decided by the prereg)
1. **Within-pathway percentile.** The rank-percentile version gives D < 0 for both age labels: LUCA p = 0.009, Moody-LUCA p = 0.012.
   - The sealed raw-stratum statistic does not, because it is dominated by long pathways such as cobalamin (37 reactions) and glycolysis (32).
   - So there may be a weak "old steps come first within a pathway" signal that is spread across many short pathways.
   - The prereg named this check as reporting only. Treating it as a finding would be choosing a statistic after seeing the results. If pursued, it needs a fresh sealed prediction on a different stratified network.
2. **The earliest strata are not "old", even by the paper's own labels** (post hoc look).
   - Strata 1-7 (the acetyl-CoA pathway, where the paper starts its ordering) hold 7 LUCA, 10 lineage-specific and 6 unlabelled reactions.
   - Only 2 of these 23 reactions are reported as the exact reaction without enzymes (grade A); 14 are grade C.
   - This fits the known fact that the methyl branch of the acetyl-CoA pathway uses unrelated enzymes in bacteria and archaea.
   - It means the start of the assembly order is the part of the network with the *least* phylogenetic support for being in LUCA. This is the main reason H4b reverses.

## What this does and does not say
- **It does not refute** the paper's proposal that cofactors replaced metals. That proposal rests on cofactors being needed before they are made (209 vs 90 reactions), which I did not test.
- **What it does say.** The paper presents the strata as an ordering of when reactions arose. Two independent signals of age (distribution-based and gene-tree-based) do not line up with that order once you hold the pathway fixed. Neither does the experimental metal-catalysis list.
  - The broad pattern of central carbon early and cofactors late is real across the network, but it is already built into the definition of the strata: a reaction can only appear once its reactants exist.
- **What the test could catch.** With labels tilted 0.7/0.3 within pathways, power was 0.995. A real within-pathway age signal of that size would have been found. Weak signals below that are not excluded; see exploratory point 1.

## Caveats
- All labels except Moody's come from the same paper, so this is an internal-consistency test.
- The S4 literature list reflects what chemists chose to try.
- 108 stratified reactions have no age label, and 51 Moody-labelled reactions have no S2 age.
- Manual reactions (`RMAN…`) were dropped, as sealed.
- Pathway blocks use the authors' labels as literal strings, so "Purine" and "Purine,GTP" count as different blocks.

## Files
- `strata_test.py`: parsing, planted checks and tests.
- `results.json`: all numbers.
- `reactions_labelled.csv`: the joined table, derived from CC BY data.
- Raw tables are not committed. To fetch them: Europe PMC PMC13440417, supplementary files `sciadv.aef3128_tables_s1_to_s10.zip`, into `raw/tables/`.

Rerun (about 5 min, 1 core): `.venv/bin/python -I experiments/metabolic_strata/strata_test.py`

## Sources (opened)
- Mrnjavac et al. 2026, Sci Adv, doi:10.1126/sciadv.aef3128. Main text and supplementary Tables S2, S4 and S8 read; licence CC BY per Europe PMC.
- Moody et al. 2024, Nat Ecol Evol 8:1654, doi:10.1038/s41559-024-02461-1. Used here only through the authors' KO comparison sheet in Table S2.
- Granick's hypothesis is cited by name only (unverified: original paper not opened).
