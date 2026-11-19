# Pre-registration amendment v4: lineage-varying loss, a second published target (Huang et al. 2026), stem transfers and baseline rules (task #32)

Agent: orig-paper. Written 2026-11-19, before any fitting, pilot or main simulation, and before any of Huang et al.'s data files were downloaded. v1 (`13cb4388…`), v2 (`39f790b0…`) and v3 (`205919d4…`) stay in force except where added to here. Nothing below changes P1-P6 or the Moody decision rule.

## Why
Huang et al. 2026 (Nat Commun 17, doi:10.1038/s41467-026-76386-7; full text read by the library agent; library entry `huang-2026-laca-methanogen-reconciliation`) reconciled 7,059 arCOG families over 257 archaea with AleRax.
- A single global loss rate gives a "small-genome attraction" artefact.
- Clade-specific loss (DPANN 0.40-0.45 against 0.26-0.27 elsewhere) moves the root and changes the ancestor's family count (800-1,219 at the Euryarchaeota root, 1,190-1,709 at the MHH root).
- They report no simulation of ancestral-content recovery.

Our v3 truth varies rates by family but not by lineage. If the calibration fails when one clade loses genes faster than the reconciliation model assumes, that is a central result.

## Additions
### A. Arm L: lineage-varying loss in the truth
- **Design.**
  - In one root subtree ("domain B"), choose the deepest clade whose sampled tips make up 15-30% of that domain, with ties broken by seed.
  - Its whole subtree in the complete tree has loss × 1.6 (the ratio 0.425/0.265 from Huang et al.). Everything else is as at the fitted T*.
  - 3 replicates (seeds 11-13).
- **Simulator.** Lineage-specific loss is set with Zombi's own user-rate mode (Gu, CustomRates files), without editing Zombi. If Gu cannot combine lineage-specific loss with the per-family draws of v3, family heterogeneity is dropped in arm L only, and this is logged. If Zombi cannot set lineage-specific loss at all without code changes, arm L is reported as not run.
- **Reconciliation.** Moody's pipeline as in v3 (ALE plus a global O_R). Its rates do not vary by lineage, so the model is misspecified the way Huang et al. found real data to be.
- **The calibration "holds" only if both of these are true:**
  - (i) R in arm L (inferred trees, mean of 3) is within ±0.10 of the main-grid mean R at T*;
  - (ii) the T*-trained calibration model, applied to the arm-L simulations, predicts their true LUCA count within ±15% in all 3 replicates.

  Otherwise it "breaks". A break is reported as a main result with its size, and the real-data verdicts in v2 are then qualified accordingly.
- **Prediction P7 (sealed): the calibration breaks.**

### B. Arm H: Huang et al.'s AleRax pipeline and a second real-data target
- **Reconciliation H.** AleRax, with an inferred-tree UFBoot sample, run on the arm-L simulations and on the 3 main-grid simulations at T*. The settings follow Huang's methods as summarised in the library entry:
  - a clade-wise DTL parametrisation file with separate rate sets for the two root children and for the fast-loss clade;
  - `--origination OPTIMIZE`, with origination optimised separately for the root, its two children and the fast-loss clade (Huang's DPANN analogue). In the main-grid simulations the clade is chosen by the same rule, with no rate change;
  - species tree fixed;
  - fraction missing 0.

  Their exact options are taken from their deposited scripts (`0_scripts.zip`, Zenodo 18701544) where these state them. Any difference is logged before scoring.
- **Calibration H.** The same features and logistic model as in v2. The two "domains" are the root's two children, and occupancy is measured in each. It is trained on the arm-H outputs.
- **Real-data target.** Huang et al.'s per-family root (LACA) posteriors for the Euryarchaeota-root, 72-parameter model, from `4_Ancestral_reconstruction.zip`. Occupancy comes from their taxa set.
  - E_H is the sum of their PPs, computed after download and recorded before calibration is applied.
  - The calibrated count C_H is computed with the v2 bootstrap.
- **Decision for Huang (same multiples as v2):**
  - overstated if the whole span is below 0.67·E_H;
  - understated if it is above 1.5·E_H;
  - validated if it is within 0.8-1.25·E_H;
  - otherwise not resolved.
- **Prediction P8 (sealed):** C_H > E_H.
- **Limits.**
  - Their 257 genomes and arCOG clustering against our 80 genomes and Zombi families.
  - Their ancestor is archaeal, not LUCA. Our simulated root stands for both.
  - If their PP file cannot be matched to families and genomes, arm B's real-data step is reported as not done.

### C. Stem-to-stem transfers (Wehbi et al. 2026)
- **Diagnostic.** From Zombi's event files, flag families that originated on either stem branch below the root and were transferred to the other stem before that stem's first sampled speciation.
- **Report** what share of false T50d calls in each condition are such families.
- **Not simulated.** Fused-domain inheritance, also from Wehbi, is outside this test (Zombi has no fusion). Missed homologs at depth (Selcuk et al. 2026) are measured by the existing recall numbers.

### D. Baseline classifiers (Mrnjavac et al. 2026 and a trivial rule)
- **B1, Mrnjavac's rule.** Present in ≥ 50% of genomes in ≥ 4 higher taxa in each domain.
  - In simulation, the "higher taxa" in a domain are the clades obtained by cutting that domain's sampled tree at the depth giving 6 clades (or the nearest count ≥ 4).
  - In Moody's data, they are the phylum field of the taxonomy file.
- **B2, both-domain rule.** Present in > 1% of genomes in both domains.
- Both are scored against truth in every simulation, alongside T50d and the calibrated model, and both are applied to Moody's data and reported.
- No prediction is made.

## Compute and order
- Arms L and H add 3 simulations, plus reconciliations of 6 simulations.
- They run after the main grid, on the laptop under the shared lock (up to 4 workers, background priority).
- Downloading Huang et al.'s data is light and may happen at any time. Only E_H is computed before calibration.
