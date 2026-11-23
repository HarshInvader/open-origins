# Pre-registration v6: K5, can the pipeline tell a big LUCA from a small one?

**Sealed 2026-11-23, before any small world was tuned or scored.** Builds on v5 to v5e. Design advice from Fable (two rounds) is in `docs/RESEARCH_STATE.md`.

**Computed before sealing.** No PP or ALE output from any K5 world was read. Only these were run:
- stem lengths, τ and the stem-overlap window, from the seed-1 tree;
- the two planted checks below;
- one smoke build each of a small world (λ = 1, N = 50) and the positive control, to check that trees and mappings agree.

## Question
K3 showed that ALE plus Moody et al.'s root reweighting recovers a planted root genome of about 190 families (R* 1.01-1.10). Does it also report a small root genome when the root really is small, but many families were born on the two domain stems and crossed between the domains early? If it reports a large LUCA in that world, the size in Moody et al. 2024 cannot separate "big LUCA" from "small LUCA plus early stem traffic".

## Worlds

### Big world
The K3 simulations, seeds 1-3: 80 genomes per domain, transfer 0.4, origination 40, 200 initial families. The ALE output is the Linux true-tree run (`ale_true`, DEVIATIONS 12). These runs already exist and are reused unchanged.

### Small world
It is built on the same complete species tree as each big-world seed.
- **Root families:** 20 of the seed's true root families are kept, chosen at random (rng `[seed, 999]`). The other root families are removed.
- **Other families:** every non-root family is kept unchanged, including its ALE output. Zombi Gm families evolve independently, so the kept families are a valid draw from the same process. The one exception is the genome-size floor, which only blocks losses in genomes under 10 genes.
- **Stem-born families:** N families are added, each born at a point drawn uniformly by length over the stems.
  - They are simulated by `experiments/luca_calib/k5/stemsim.py` with Zombi Gm's per-gene rules:
    - per-family lognormal duplication 0.2, transfer 0.4 and loss 1.0 (σ 0.5);
    - additive transfer to a lineage drawn uniformly from those alive;
    - copies pass to both children at speciation and die at extinction;
    - no genome-size floor.
  - Families are born and evolve whatever their fate, and none is kept or dropped by outcome.
- **Stems:** the complete-tree lineages from the sampled MRCA (exclusive) to each domain's sampled crown (inclusive), as in `pipeline/stem_transfers.py`, plus every side subtree off them with no surviving lineage.
- **Stem traffic:** a copy on a stem lineage also transfers, at rate x, to a lineage drawn uniformly from the other domain's whole clade alive at that time: its stem, its dead side lineages or its early crown lineages.
  - The target is not the other stem alone, because the two stems coexist only briefly. On seed 1 they overlap in [0.1013, 0.1073] of a tree of height 1.1, and stem A is a single lineage 0.006 long.
  - x = λ / τ, where τ (0.0165 on seed 1) is the mean time a copy born at a uniform stem point stays on the stems. So λ is the expected number of cross-domain stem transfers per founding copy, ignoring duplication and loss.
  - The realized count per family (`Tstem`, which includes copies made by stem duplication) is reported for every cell.
- **Pairing across λ:** family i draws its birth point and rates from rng `[seed, i]`, the same at every λ, and its events from rng `[seed, round(1000·λ), i]`.

### Control world (N = 0)
The 20 kept root families plus all other families, with no stem-born families. It needs no new ALE run, only an O_R refit and scoring, and it sets the background floor (R_ctrl, H_ctrl).

### ALE positive control (seed 1)
- Zombi's 200 initial-genome families are replaced by 200 stemsim families born at the root, and ALE is run on them. Truth for these families is the number of copies at the MRCA's speciation.
- **Pass:** R = ΣPP / true root count within 0.95-1.15. K3 seed 1's true-tree R was 1.087.
- **Fail:** K5 is reported as "stemsim's trees are not reconciled like Zombi's", and the decision rule is not applied.

### Planted checks (already run, phyletic only, seed-1 tree, final code)

| stemsim births | Compared with | KS D: genes / occupancy / domain A / domain B | Critical value |
|---|---|---|---|
| 600 at the root | Zombi's 200 initial-genome families | 0.055 / 0.067 / 0.052 / 0.063 | 0.111 |
| 600 uniform over the whole tree | Zombi's 3,673 originated families, present ones only (224 vs 1,373) | 0.065 / 0.077 / 0.041 / 0.042 | 0.098 |

Both checks are rerun for seeds 2 and 3 at build time. Any KS D above its critical value stops K5 for that seed.

## The λ ladder (fixed, not tuned)
λ ∈ {0, 1, 4}. At λ = 0, stem-born families reach the other domain only by ordinary transfer.

## Tuning N (phyletic summaries only; no PP or ALE output is read)
For each seed and λ, N is chosen from the grid {25, 50, …, 475; 500, 550, …, 1950; 2000, 2100, …, 4000}. Grid values above the first one where the small world exceeds the big world's row 2 by more than 20% are not tried.

**Gating rows:**
1. Fraction of present families found in both domains (±0.03 absolute).
2. Number of families in ≥25% of the sampled genomes of each domain (±10%).

Among grid values that pass rows 1 and 2, N is the one closest to the big world on row 2, with ties going to the smaller N.

**Recorded rows (they do not gate):**
3. Families with ≥2 sampled genes, i.e. those entering ALE (±5%).
4. Occupancy histogram (KS D < 0.1).
5. Mean families per sampled genome in each domain (±10%).
6. Mean copies per occupied genome, and the single-species fraction (±10%).

**Cell labels:**
- **Tightly matched:** a matched cell that also passes rows 4 and 5.
- **Unmatched:** no grid value passes rows 1 and 2. The cell gets no ALE run and is reported as "the small world can be told apart from phyletic data alone".

Families are simulated in index order with per-family rngs, so a world with N families is a prefix of any larger one, and the tuning is deterministic.

## Pipeline (identical to K3's true-tree arm)
- ALE (Linux build, `setup_remote.sh`) runs on the true gene trees of the stem-born families with ≥2 sampled genes.
- Kept families reuse their K3 `uml_rec`.
- `run_ale.py` refits Moody et al.'s single global O_R over all of the small world's families.
- `score.py` scores against `sample/truth.tsv`, where the true root is the 20 kept root families still present.

## Measures
For each seed and λ, matched cells only:
- **ΣPP_small** (fitted O_R).
- **R_small** = ΣPP_small / true root count, and the same ratio for the control world (R_ctrl).
- **H** = ΣPP_small / ΣPP_big, where big is the same seed's K3 true-tree arm. H_ctrl is reported as H's floor.
- ΣPP split three ways: kept root families, stem-born families, and other families. A stem-born family that raises O_R and so inflates the "other" mass counts as a stem effect.
- Realized cross-domain stem transfers per stem-born family.
- Fitted O_R and the prior multiplier (fitted Σ / flat Σ), small against big.
- Reliability curve and ECE, as in v5e.

## Decision rule
Per λ, take the mean over matched seeds. A λ level is read only if at least 2 of the 3 seeds are matched.
- **Same-side condition:** a criterion holds at a λ only if every read seed falls on the same side of its threshold. Otherwise that criterion is inconclusive at that λ.
- **Cannot discriminate:** mean H ≥ 0.5 at any read λ. In a phyletically matched world whose root is about 10 times smaller, the pipeline then reports at least half the big world's size. That would be a limit on what this method class can identify, not a bug in our wrapper. The claim needs the read seeds at that λ to be tightly matched. Otherwise it is reported as "cannot discriminate in a loosely matched world".
- **Discriminates:** mean H < 0.5 and mean (R_small − R_ctrl) ≤ 0.5 at every read λ, and λ = 4 must be read. An excess of 0.5 is at most 10 PP-units over the background floor.
- **Partial:** anything else. Reported as "inflates a small root genome by R_small − R_ctrl over background at λ".
- **Inconclusive band:** a mean within 0.05 of 0.5 for H, or within 0.1 of 0.5 for R_small − R_ctrl, is inconclusive for that criterion.
- **Completion:** v5e's completion clause applies to the small world's ALE runs.
- **Positive control:** it must pass first (see above).
- **No λ read:** the result is "small worlds tuned this way are distinguishable on phyletic data", and nothing is claimed about the pipeline.

## Limits, stated in advance
- **True gene trees only.** Gene-tree error is not tested here.
- **A pass is narrow.** "Discriminates against this adversary" covers only:
  - stem-born families with extra cross-domain transfer from the stems;
  - families simulated by stemsim rather than Zombi;
  - one species-tree shape per seed.
- **The target is the whole clade.** Stem traffic lands on any lineage of the other domain's clade, mostly its early crown lineages. That is a narrower adversary than a true stem-to-stem transfer.
- **Same-topology families.** A family born on one stem, transferred to the other early and vertical afterwards has the same topology as a root family. Undated ALE cannot tell them apart, so part of any H is irreducible by construction.

## Compute
- The K3 AWS machine if it is still up; otherwise one spot machine under the $50/month cap.
- ALE runs only for the stem-born families and the positive control.
- Worlds are built on the AWS machine from its Linux `ale_true` outputs.
- The laptop is not used for ALE: its arm64 build fails on large families (DEVIATIONS 12).
