# Pre-registration: how far off is a LUCA reconstruction at LUCA depth? A planted-LUCA calibration of the Moody et al. 2024 pipeline

Agent: orig-paper. Written 2026-11-19. No simulation and no AleRax run on simulated data has been done. The only things run before sealing:
- the AleRax `--help` output;
- reading Zombi's source and parameter files.

The novelty note is `docs/luca_calibration_novelty.md`.

## Why
Moody et al. 2024 (Nat Ecol Evol 8:1654, doi:10.1038/s41559-024-02461-1, full text PMC11383801 opened) reconstruct LUCA by ALE reconciliation of 9,365 KEGG families over 700 genomes. They report:
- 399 families at the strictest presence tier;
- a genome of about 2,657 proteins, estimated from root presence probabilities summed by random draws (mean 1,298 families) and mapped to protein count by LOESS.

Two published arguments predict opposite errors, and neither tested the pipeline on a known answer at this depth:
- **Csűrös 2026** (PNAS, doi:10.1073/pnas.2537812123) argues that ALE at this scale infers spurious transfers.
- **Szöllősi et al. 2026** (bioRxiv, doi:10.64898/2026.09.03.749268) puts false-negative rates at deep nodes at 0.5-0.9, using error injection into real data, not simulated evolution.

The novelty search found no study that does all of the following:
- simulates genomes at LUCA depth with transfers from extinct and unsampled lineages;
- infers gene trees from saturated sequences;
- applies Moody's thresholds and size step;
- scores against the planted root.

## Design (fixed now)
**Simulator.** Zombi, unmodified, commit `8db13ee4ba007f46c17f38586d31e5aa617c1647`. It is run in its own modes; no Zombi code is edited.

**Species tree (Zombi T mode).**
- Birth-death with speciation 1.0 and extinction 0.5 (Zombi units). The tree is grown until at least 600 extant lineages exist.
- The two subtrees under the root play the two "domains".
- 60 extant tips are sampled uniformly at random from each domain (120 in all). If a domain has fewer than 60 tips, the next seed is used.
- Every unsampled extant lineage and every extinct lineage stays in the complete tree and can donate transfers. This is the "transfers from the dead and unsampled" condition.
- Tree height is rescaled to 1 unit, representing about 4 Gyr.

**Genomes (Zombi Gm mode: family-specific duplication, transfer and loss rate multipliers, Zombi defaults).**
- The root genome has 1,000 families.
- Rates per gene per unit time: duplication 0.2, loss 1.0, transfer τ ∈ {0.3, 1.0}.
- Transfers are additive (REPLACEMENT_TRANSFER 0).
- Origination is the only tuned rate. It is set in a genome-size-only pilot, before any reconciliation, so that the mean sampled genome size lies between 500 and 2,000 families. The pilot records only genome sizes.

**Sequences (Zombi Su mode).**
- Amino acids, 300 sites, Zombi's amino-acid model (the model name is recorded).
- Lineage and family substitution-rate multipliers are lognormal with σ = 0.5, set via Zombi's CustomRates files.
- Tree scaling is set so that the mean root-to-tip distance is 2.0 expected substitutions per site, to create saturation at depth.

**Gene trees (inferred, the primary condition).**
- Families with ≥ 4 sampled genes: IQ-TREE 3 with LG+G4 and 1,000 ultrafast bootstraps; the bootstrap trees are given to AleRax.
- Families with 2-3 genes: the single unrooted topology.
- Families with 1 gene: not reconciled; their root probability is set to 0.
- **Control condition:** the same simulated families with Zombi's true gene trees, pruned to the sampled tips.

**Reconciliation.** AleRax 1.4.0:
- `--rec-model UndatedDTL`, `--model-parametrization PER-FAMILY`, `--origination OPTIMIZE`, 100 sampled reconciliations, seed 1;
- the true sampled species tree is given, which favours the method. Moody inferred theirs.
- **Sensitivity:** `--origination ROOT`.
- **Root presence probability (PP)** = the fraction of the 100 sampled reconciliations in which the family has at least one copy at the root of the sampled species tree.

**Truth.** A family is a true LUCA family if Zombi's genome at the most recent common ancestor of the 120 sampled tips (in the complete tree) has at least one copy of it. The true LUCA size is the count of such families.

**Moody's scoring, applied unchanged:**
- **T75 and T50:** PP ≥ 0.75 and PP ≥ 0.5.
- **T75d and T50d:** as above, and also present in more than 1% of genomes in both domains, which here means at least 1 genome per domain.
- **E** = the sum of PP over all families. This is the expected root family count, the quantity Moody's random draws estimate (their mean was 1,298).
- Moody's LOESS step maps family counts to protein counts on real genomes. It is outside this test, and any bias in E carries into it.

**Grid.**
- Main: 2 transfer levels × 3 replicate simulations (seeds 1-3) = 6 simulations. Each is analysed with both inferred and true gene trees.
- Planted control: 1 simulation with τ = 0, no family or lineage rate heterogeneity, and true gene trees.
- Pilot: the τ = 1.0, seed 1 simulation is run first, for timing only. Its results are not opened until the whole grid has run.

## Outcome measures
For each simulation and gene-tree condition:
- recall and precision at T75, T50, T75d and T50d;
- the size ratio R = E / true LUCA size;
- calibration: the observed share of true LUCA families in each PP bin (0-0.2, 0.2-0.4, …).

## Predictions (sealed)
- **P1 (threshold content undercounts).** With inferred gene trees, recall at T75 is < 0.5 in all 6 main simulations.
- **P2 (direction of the size error).** With inferred gene trees and τ = 1.0, R < 0.9 in at least 2 of 3 replicates: the summed size underestimates LUCA.
- **P3 (gene-tree error lowers the root).** R with inferred trees is lower than R with true trees in at least 5 of 6 simulations.
- **P4 (false LUCA families from transfer).** At τ = 1.0, the share of non-LUCA families among T50d calls is above 10% in at least 2 of 3 replicates.
- **P5 (miscalibration).** In the 0.4-0.6 PP bin, pooled over the inferred-tree runs, the share of true LUCA families differs from 0.5 by more than 0.15.

## Rule for any corrected LUCA size
- **If the inferred-tree R values across all 6 main simulations span ≤ 0.20 (max − min):** report a corrected expected family count of 1,298 / mean(R), with the range 1,298 / max(R) to 1,298 / min(R). Label it "under this simulation model".
- **Otherwise:** report only the bound 1,298 / max(R) to 1,298 / min(R), and say the correction is not stable.
- In either case, the correction is a statement about the pipeline's behaviour under this model, not a new LUCA estimate. The paper's protein count (2,657) is not corrected directly, because the LOESS step is not simulated.

## Validity checks and kill rules
- **Planted control must pass before anything else is read:** recall at T50 ≥ 0.9 and |R − 1| ≤ 0.10. If it fails, the pipeline (our parsing of the reconciliations or the AleRax settings) is wrong, and the main grid is not interpreted until the cause is found and logged.
- **Zombi check:** the true LUCA set is recomputed from Zombi's event files and must match the genome file at the MRCA node.
- **Coverage:** if more than 5% of families fail in IQ-TREE or AleRax, the study is reported as incomplete.

## Limits stated now
- 120 sampled genomes against Moody's 700, and 1,000 root families. The scale is smaller to fit a laptop.
- The true species tree is given, so species-tree error is not tested.
- Zombi's model, not real biology, defines "realistic"; a different simulator could give a different bias.
- Moody's family clustering (eggNOG, grouped by KEGG ID) is not simulated; families are given as Zombi defines them. Clustering error is a further source of error that this test leaves out.
- The authors of Zombi and AleRax, who co-authored Moody et al. 2024, are working on this question. If they publish first, this becomes an independent replication.

## Compute
Heavy (IQ-TREE on several thousand families per simulation). It runs only under the shared compute lock, with `taskpolicy -b nice -n 20` and at most 2 workers, after the queue: Indus retrain → Open Mind DREAM → Indus planted checks.
