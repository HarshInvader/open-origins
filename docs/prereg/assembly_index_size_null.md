# Pre-registration: assembly index vs a size-only null (board task #7)

Agent: orig-2. Written 2026-11-18, before any outcome below was computed.
At writing time I had looked only at file schemas, sample labels and group sizes, never at MA, peak or m/z values by label.

## Question
Does molecular assembly index (MA) separate biotic from abiotic material better than size alone (molecular weight, heavy-atom count) or a compression measure, once size is matched?

## Data (all public)
- **D1, Marshall et al. 2021 source-data deposit** (Nat Commun 12:3033, doi:10.1038/s41467-021-23258-x, file 41467_2021_23258_MOESM2_ESM.zip).
  - `EnviromentalSamplesUpdated_Oct2020_outsidedata_seawater.csv`: one row per MS2 parent ion, with m/z, number of MS2 peaks, sample and source label.
  - `MS_data_Standard_Curve.csv`: 114 single compounds with MA and mean MS2 peak count, used to map peaks to estimated MA.
  - `ma_mw_subsampled_by_mw.csv`: 2,200 Reaxys molecules with InChI and Marshall's MA. Used only to validate our MA implementation.
- **D2, molecules with structures.**
  - Biotic: Rhea `rhea-chebi-smiles.tsv` (ChEBI compounds that take part in enzyme-catalysed reactions).
  - Abiotic (enumerated chemistry, no selection): GDB-13 (1,201) and GDB-17 (200) subsets with reference MA, from the DaymudeLab/assembly-theory repo `data/`.
  - Validation only: the `coconut_55` and `checks` sets.
- **D3, Hazen et al. 2024** (J R Soc Interface 21:20230632, doi:10.1098/rsif.2023.0632), Table 1: published SBMA and EMA for 11 mineral subunits. Descriptive only. The values are already published, so this is not a blind test.

## MA implementation
- `assembly-theory` 0.7.0 (Python bindings of the Rust crate): exact index, hydrogens stripped, 60 s timeout per molecule. Timed-out molecules are excluded and counted.
- Validation gate, which must pass before T7a counts: our MA equals the reference MA on 100% of `checks`, `coconut_55`, `gdb13_1201` and `gdb17_200`. It must also agree with Marshall's Reaxys MA (computed with a different, older code) on at least 90% of a random 300-molecule subsample with ≤ 25 heavy atoms. If Marshall's code disagrees, report the rate and use ours.

## Features
- **MW**: RDKit exact mass of the neutral parent.
- **HA**: heavy-atom count.
- **LZ** (compression): zlib level-9 compressed length, in bytes, of the RDKit canonical SMILES with stereo removed.
- **MA**: as above.
- **D1 only**: ion **m/z** (size proxy) and **MS2 peak count** (Marshall's MA proxy; estimated MA is a linear function of it).

## T7a, molecules (D2)
- **Filter (biotic and abiotic alike):**
  - parses in RDKit;
  - a single fragment (multi-fragment entries are dropped);
  - only C, N, O, S, P, F, Cl, Br, I, with at least one C;
  - no wildcard (`*`) atoms;
  - isotopes removed;
  - stereo removed;
  - deduplicated by canonical SMILES.
- **Size window:** only heavy-atom counts that both groups cover, HA ∈ {4..10} ∪ {14..17}.
- **Matched set M_HA:** within each HA value, randomly subsample the larger group to the size of the smaller (seed 0).
- **Matched set M_MW:** for each abiotic molecule in random order, take the nearest-MW unused biotic molecule within ±1.0 Da. Drop it if there is none.
- **Primary statistic:** ΔAUC_primary = AUC(MW + HA + MA) − AUC(MW + HA) on M_MW.
  - Both AUCs come from logistic regression with standardised features, 10-fold stratified CV, 5 repeats.
  - 95% CI from 2,000 bootstrap resamples of molecules, refitting the CV each time (repeats reduced to 1 inside the bootstrap).
- **Secondary statistics:**
  - S1: ΔAUC = AUC(MW + HA + MA) − AUC(MW + HA + LZ) on M_MW (does MA beat compression?).
  - S2: single-feature AUCs (biotic as positive) of MA, LZ, MW and HA on M_HA, each with a bootstrap CI.
  - S3: on the unmatched window set, AUC(MA) vs AUC(MW) vs AUC(HA), single feature.
  - S4: direction. Assembly theory predicts biotic MA > abiotic MA at matched size. Report the mean MA difference on M_HA with its CI.
- **Pass marks:**
  - "MA adds separation beyond size": the lower 95% bound of ΔAUC_primary is > 0.
  - "MA beats compression": the lower 95% bound of S1 is > 0.
  - "Supports the AT direction": S4 > 0 with CI excluding 0.
  - A CI spanning 0 is a negative. Report the smallest ΔAUC the test could detect (planted-control power).

## T7b, Marshall mixtures (D1)
- **Labels:**
  - Positive: Source = "Biological".
  - Negative: Source ∈ {"Abiotic", "Dead"}.
- **Exclusions:**
  - "??" (blinded; described separately);
  - "MeOH Control" (solvent blank);
  - "Aeromonas veronii TOP15" and "Seawater TOP15" (duplicates of the full samples).
- **Primary statistic, sample level:** ΔAUC_mix = AUC(max MS2 peaks per sample) − AUC(max m/z per sample).
  - Single-feature AUCs, no fitting.
  - To remove ion-count effects, each sample is subsampled to min(n, 15) ions; features are averaged over 500 draws.
  - 95% CI from 2,000 bootstrap resamples of samples, stratified by label.
- **Secondary statistics:**
  - M1: ion-level, m/z-matched. Stratify ions into 50-Da m/z bins. Within each bin, compute the AUC of MS2 peaks (biological vs non-living); combine as the ion-pair-weighted average. Report the same for m/z within bins. CI by cluster bootstrap over samples.
  - M2: leave-one-sample-out logistic regression, sample level: max m/z vs max m/z + max peaks.
  - M3: the fraction of samples per group whose top ion's estimated MA is ≥ 15. Estimated MA comes from our OLS fit MA ~ mean.MS2 on the standard curve.
- **Sensitivity checks:**
  - (i) "Formose Recursive Cycle" relabelled as negative. It is a chemical reaction mixture that the authors labelled biological.
  - (ii) negatives = Abiotic only.
  - (iii) no subsampling.
- **Pass mark:** "the MS2-based MA proxy beats size": the lower 95% bound of ΔAUC_mix is > 0. Note that n is about 26 samples, so power is low; the planted control gives the detectable effect.

## T7c, Hazen minerals (D3, descriptive)
- Count the heavy atoms of each published subunit from its formula.
- Place the 11 subunits on the MA-vs-HA relation fitted on D2 organics.
- Prediction (made before computing the fit): mineral subunits lie below the organic MA–HA trend. Their MA per atom is lower, because the units repeat.
- So a size-only rule would flag the large heteropolyanions at least as readily as MA does. MA ≥ 15 does occur abiotically (EMA 18 for ewingite and ilmajokite, as published).

## Planted-answer controls (run first, at our sample sizes)
- **P1 (T7a):** on the real M_MW set, replace labels with planted labels.
  - (a) Size-only planted: P(label = 1) = logistic(β·z(HA)). The method must report ΔAUC_primary CI covering 0 in ≥ 90% of 50 replicates.
  - (b) MA-planted: P(label = 1) = logistic(γ·z(MA residual on HA)). Find the smallest γ (AUC gain) detected in ≥ 80% of 50 replicates. That figure is the detectable effect size.
- **P2 (T7b):** simulate samples with the real group sizes and ion counts. Peaks are drawn from the real pooled peaks~m/z relation plus noise.
  - (a) No label effect: the CI covers 0 in ≥ 90% of runs.
  - (b) Planted peak shift of δ standard deviations for biological samples: report the δ detected in ≥ 80%.
- If P1(a) or P2(a) fails, the method is broken and its real output does not count.

## Multiple tests
- Ledger rows:
  - T7a primary;
  - T7a S1;
  - T7b primary.
- Everything else is secondary/descriptive.

## What would change my mind
- If MA adds AUC beyond MW + HA and beats LZ on mass-matched sets, the biosignature claim survives this null for these sets.
- If not, MA's separation in these data is carried by size or by string compressibility.
