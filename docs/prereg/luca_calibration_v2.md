# Pre-registration amendment v2: a calibrated LUCA size from Moody et al.'s own data (task #32)

Agent: orig-paper. Written 2026-11-19, after v1 (`docs/prereg/luca_calibration.md`, sha256 `13cb4388…`) and before any simulation or reconciliation.
- **What this amendment does.** It replaces v1's hand-picked rates with rates fitted to real data, and adds a real-data endpoint.
- **What v1 still governs.** Simulator, inference, reconciliation, truth definition, scoring tiers, the planted control and the kill rules, except where changed below.
- **v1's predictions P1-P5 are kept unchanged** and scored on the v2 main grid.

## What result would change the field's mind
The Moody/Williams/Szöllősi/Martin circle currently argues from two kinds of evidence:
- untested intuitions about which way reconciliation errs at LUCA depth: Csűrös 2026 says transfers are overcalled and LUCA shrinks to tens of genes; Szöllősi et al. 2026 say deep false negatives are 0.5-0.9;
- a published LUCA size that has never been checked against a known answer.

The result that would move them is a simulation-based calibration of the exact pipeline. It must meet three conditions:
- **Realistic simulations.** The simulated genomes match the real 700-genome data on gene-family statistics the inference never sees.
- **Moody's own data at the end.** It is applied to their own 7,456 per-family root probabilities.
- **A clear output.** It yields a calibrated expected LUCA family count with error bars that include model uncertainty.

The outcome then means one of three things:
- **Artefact.** If the calibrated count's whole range lies well outside Moody's 1,291 (below 0.67× or above 1.5×), LUCA's inferred complexity is substantially a reconstruction artefact, in a stated direction, with a corrected size.
- **Validated.** If the range sits inside 0.8-1.25×, the complex-LUCA picture rests on ground validated by simulation, and the critique is answered with a planted answer.
- **Unresolved.** If it is neither, the honest result is a bound: how far current data and methods can pin LUCA's size, and which parameter (transfer level) the answer depends on.

Each outcome settles part of a live dispute with something neither side has: a known answer at LUCA depth, and calibration on the real data.

## Already seen before sealing (disclosed)
- **Real summary statistics** (`experiments/luca_calib/real_stats.json`, from `real_stats.py`). These use no root probabilities. Over 700 genomes (350 Archaea, 350 Bacteria) and 9,371 families:
  - median family occupancy 0.03;
  - 45.5% of families present in both domains (30.3% above 1% in both);
  - median genome 994 families;
  - median trimmed alignment 156.5 sites;
  - median mean pairwise p-distance 0.61 (238 alignments sampled).
- **Reproduction of Moody's size input:**
  - the sum of `LUCA_PPs.csv` is 1,297.2, against their reported mean of 1,298.25;
  - their script reads the file with the first value as a header, so it drops one family;
  - the sum of the per-family median PP over the 5 runs in `kegg1-5_cons.txt` (7,456 families common to all runs) is **E_M = 1,290.6**. E_M is the reference value below.
- No calibration was computed, and no simulation was run.

## Changes to v1's design
1. **Rates fitted to real data (stage F; genome-only Zombi runs).**
   - Root genome: 1,000 families. Duplication = 0.2 × loss.
   - Grid: loss L ∈ {0.5, 1, 2, 4} and transfer/loss ∈ {0.1, 0.3, 1, 3}, which gives 16 points.
   - At each point, origination is set by bisection (genome sizes only) so that the median sampled genome holds 10.6% of all families present across sampled genomes (the real ratio, 994/9,371), within ±2 points.
   - Distance = Σ over the 10 occupancy-histogram bins of (sim share − real share)², plus (sim both-domain share − 0.455)².
   - The best point (L*, T*) is the fit.
   - Fitting uses one simulation per point (seed 100+i) and never runs inference.
2. **Substitution scale fitted the same way.** Sequence length is 157 sites, the real median. Zombi's tree scaling is set by a sequence-only pilot so that the median mean pairwise p-distance of sampled alignments is 0.61 ± 0.05. The lognormal multipliers (σ = 0.5) stay as in v1.
3. **Main grid.**
   - Transfer ∈ {0.5·T*, T*, 2·T*} at L*, with 3 replicate simulations each (seeds 1-3), so 9 simulations.
   - Each is analysed with inferred trees (primary) and true trees (control).
   - The planted control (no transfer, homogeneous rates, true trees) stays.
   - "τ = 1.0" in v1's P2 and P4 now means the T* and 2·T* settings; "all 6 main simulations" in P1, P3 and the stability rule now means all 9.
3b. **Fit check.** The fitted simulations must reproduce three things before the real-data endpoint is used:
   - median occupancy within a factor of 1.5 of 0.03;
   - both-domain share within ±0.07 of 0.455;
   - median p-distance within ±0.05 of 0.61.

   If any fails, the real-data endpoint is reported as "not transferable" and only the simulation results are reported.
4. **Scale.** 120 sampled genomes per domain (240 in all) if the pilot's full per-simulation time is ≤ 10 hours with 2 workers; otherwise 60 per domain as in v1. The pilot is only timed; its results stay unopened.

## Real-data endpoint (new)
- **Features per family**, computed identically in simulation (from the sampled copy matrix) and in Moody's data (from `Pure_sequences` headers and the taxonomy file):
  - logit(PP), with PP clipped to [1e-6, 1 − 1e-6];
  - occupancy in domain A;
  - occupancy in domain B;
  - min(occA, occB);
  - log mean copy number.
- **Calibration model.** Logistic regression (standardised features, L2 with C = 1), trained on the families of the inferred-tree simulations. It is fitted separately for each transfer setting and once pooled over the settings. The target is true presence at the sampled MRCA.
- **Calibrated count** C = Σ p̂ over Moody's 7,456 families. Here PP is the median over their 5 runs, and occupancy is computed with their 350/350 domain split.
- **Uncertainty.**
  - Within a setting: 200 bootstrap resamples of the 3 replicate simulations, refitting each time, give a 95% interval.
  - The span is the union of the three settings' intervals.
- **Decision (sealed).**
  - **"Artefact, LUCA overstated":** the whole span is below 0.67·E_M (865).
  - **"Artefact, LUCA understated":** the whole span is above 1.5·E_M (1,936).
  - **"Validated":** the whole span is within 0.8-1.25·E_M (1,032-1,613).
  - **Otherwise "not resolved":** report the span as the bound and name the setting it hinges on.
- **Secondary.** The calibrated count of high-confidence families (Σ over families with calibrated p̂ ≥ 0.75), compared with Moody's 399 at the T75d tier.
- **Prediction P6 (sealed).** C > E_M under the T* setting, which follows from v1's P2 (summed PP underestimates). The verdict is not predicted.

## Differences from Moody that remain (stated now)
- They used ALEml_undated with root origination optimised per COG category; we use AleRax OPTIMIZE (ROOT as sensitivity).
- Their families are KEGG-clustered eggNOG hits; ours are Zombi families.
- They inferred their species tree; we give the true one.
- Their scale is larger (700 genomes against 240 or 120).

Each of these is a reason the calibration might not transfer. The fit check guards only the gene-family statistics.

## Compute
- Stage F (16 genome-only runs plus bisection), the sequence pilot, the timing pilot, 9 main simulations plus 1 control.
- All of it runs under the shared lock, with `taskpolicy -b nice -n 20` and at most 2 workers.
- Light steps (code, smoke tests under 1 minute, the feature extraction from real data) proceed now.
