# Assembly index beats size on small molecules, but in the wrong direction (task #7)

**Verdict.**
- **Molecules (T7a): MA adds separation beyond size and beats compression.**
  - The setup is 889 Rhea metabolites, each mass-matched (±1 Da) to an enumerated GDB-13/17 molecule.
  - Adding assembly index (MA) to molecular weight (MW) and heavy-atom count (HA) raises the cross-validated AUC from 0.585 to 0.646. The gain is ΔAUC = 0.061 (95% CI 0.037 to 0.089).
  - MA also beats a compression measure (LZ, the compressed length of the canonical SMILES): ΔAUC = 0.054 (0.020 to 0.085).
  - Both pass the pre-registered marks.
- **But the direction contradicts assembly theory.** At matched heavy-atom count, biotic molecules have *lower* MA than abiotic ones: −0.52 (−0.60 to −0.44). On its own, MA ranks biotic below abiotic (AUC 0.436 on M_HA, the set balanced within each heavy-atom count).
  - So the pre-registered "supports the AT direction" mark fails.
  - The separation MA adds here follows the ring-rich scaffolds of enumerated chemistry, not biological selection. This is shown in the exploratory section below.
- **Mixtures (T7b): negative and underpowered.** These are Marshall et al. 2021's 25 labelled samples.
  - The MS2 peak count (Marshall's MA proxy) does not beat ion m/z: ΔAUC = 0.115 (−0.19 to 0.42).
  - The test can detect only a shift of about 2 between-sample SD.
- **Minerals (T7c, descriptive): MA per atom is low.** Hazen et al. 2024's mineral subunits have 0.09 to 0.5 MA per heavy atom; organics have a median of 0.63.
  - The two most complex minerals (ewingite and ilmajokite, EMA 18) clear the MA ≥ 15 "life threshold" without biology, as published.
  - None of our ≤17-heavy-atom molecules, biotic or abiotic, reaches MA 15. Only 2 abiotic ones do.

**Note on order of the planted check.** The pre-registered planted check P1a was first run with a fast out-of-fold (OOF) bootstrap, and it failed (details below). The lead ruled that the refit-bootstrap version, the method the primary uses, be run on the same planted labels. It passed. It ran **after the primary had run but before the primary was read**. The pass was recorded in the ledger (`asm_P1a_refit`) and in `out/planted_refit.json` (sha256 bfd7be85…) before I opened `molecules.json`.

## Planted-answer checks

| Check | Method | Result | Pass mark | Status |
|---|---|---|---|---|
| P1a: size-only planted labels on M_MW, 50 reps | OOF bootstrap (not the primary method) | CI covers 0 in 76%; 16% false positives | ≥ 90% | **Fail**: the OOF bootstrap understates CV variance |
| P1a-refit: same labels, seeds and nboot = 300 | Refit bootstrap (the primary method) | CI covers 0 in **100%**; 0% false positives; mean CI width 0.010 | ≥ 90% | **Pass** |
| P1b: MA-residual planted labels | OOF bootstrap | Detected 88% of the time at a gain of 0.053 AUC (γ = 0.2); 30% at 0.021 | power ≥ 0.8 | The detectable gain is about 0.05 AUC (optimistic, because the refit CI is wider) |
| P2a: no-effect simulated mixtures, 40 reps | Sample bootstrap | Covers 0 in 95% | ≥ 90% | Pass |
| P2b: planted peak shift | Sample bootstrap | Power 0 at 0.5 to 1 SD; 0.2 at 1.5 SD; 0.5 at 2 SD | power ≥ 0.8 | No δ ≤ 2 SD is detectable |

The OOF-bootstrap failure is a trap worth knowing: resampling a fixed set of out-of-fold predictions ignores refit variance, and its CI was too narrow by about 2×.

## T7a, molecules (Rhea biotic vs GDB-13/17 abiotic)

- **Window.** 2,039 biotic and 1,349 abiotic molecules, HA ∈ {4..10, 14..17}, no timeouts. The matched sets are M_MW (1,778 molecules, 889 pairs within 1 Da) and M_HA (2,164).

| Model or feature (M_MW, 10-fold CV × 5) | AUC |
|---|---|
| MW + HA | 0.585 |
| MW + HA + LZ | 0.591 |
| MW + HA + MA | 0.646 |
| MW + HA + MA + LZ | 0.662 |

| Single feature (biotic = positive) | M_HA (size-balanced) | Unmatched window |
|---|---|---|
| MA | 0.436 (0.411 to 0.460) | 0.642 |
| LZ | 0.561 | 0.721 |
| MW | 0.549 | 0.743 |
| HA | 0.500 | 0.713 |

- **Unmatched, MA is the weakest of the four features.** It does worse than MW, HA and LZ. Its unmatched AUC of 0.64 comes from size.
- **Kekulé sensitivity (S5).** Swapping in the reference MA for GDB molecules computed from their original mol files changes 4 molecules. ΔAUC stays at 0.061.
- **Exploratory, not pre-registered, computed after reading the primary.** On M_MW the GDB molecules average 1.35 rings, and 37% have two or more. Rhea molecules average 0.60 rings, and 8% have two or more.
  - Fused and bridged ring systems give fewer reusable fragments, so their MA is higher.
  - Metabolites are mostly acyclic chains with repeated units (CH₂, CHOH, phosphate), so their MA is lower.
  - The likely source of MA's added separation is therefore that GDB enumerates every graph-theoretically allowed scaffold. Real abiotic chemistry is not like that.

## T7b, Marshall et al. 2021 mixtures

- **Samples.** 13 biological vs 12 non-living samples. Features are per-sample maxima, averaged over 500 subsamples of 15 ions.
  - Peaks give AUC 0.827. m/z gives 0.712.
  - ΔAUC = 0.115 (−0.19 to 0.42): **not significant**.
- **Within 50-Da m/z bins (ion level).** Peaks give AUC 0.565; m/z gives 0.484.
- **Leave-one-sample-out logistic regression.** m/z alone gives 0.455; m/z + peaks gives 0.75.
- **Estimated MA ≥ 15.** This holds in 77% of biological and 8% of non-living samples (standard curve MA = 5.888 + 0.526·peaks, r = 0.885, n = 114).
- **Sensitivities.**
  - Formose Recursive Cycle relabelled as non-living: Δ 0.006 (−0.29 to 0.31).
  - Abiotic-only negatives: Δ 0.169 (−0.18 to 0.52).
  - No subsampling: Δ 0.077 (−0.19 to 0.36).
- **Caveat.** The deposited ions span only m/z 300 to 500, so m/z is a weak size proxy here. Whisky and beer samples are labelled biological. The peak-count signal is real but small-sample. This test cannot separate it from size or sample type.

## T7c, Hazen et al. 2024 minerals (descriptive)

| Mineral | Subunit heavy atoms | EMA | EMA per heavy atom | Organic trend MA at that HA |
|---|---|---|---|---|
| calcite | 4 | 2 | 0.50 | 3.0 |
| beryl | 24 | 5 | 0.21 | 13.8 |
| vanarsite | 70 | 11 | 0.16 | 38.7 |
| ilmajokite | 98 | 18 | 0.18 | 53.9 |
| ewingite | 196 | 18 | 0.09 | 107.0 |

- **All 12 subunits lie below the organic MA–HA trend, as predicted.** (Eudialyte has two subunit readings, so 11 minerals give 12 rows.) The trend is MA = 0.54·HA + 0.81, fitted on HA 4 to 17; above that range it is an extrapolation. A size-only rule would flag these large heteropolyanions far more readily than MA does.

## Validation of the MA implementation
- `assembly-theory` 0.7.0 matches the reference MA on 1,471 of 1,471 original mol files (checks, coconut_55, gdb13_1201, gdb17_200).
- Through our SMILES → mol pipeline, the alternative Kekulé form shifts MA by ±1 in a few molecules. Agreement is 87% for checks, 93% for coconut_55, 99.9% for gdb13 and 98.5% for gdb17. The strict 100% gate therefore fails on the pipeline but not on the implementation. S5 above shows this has no effect on the result.
- Marshall's older code gives higher values on Reaxys molecules: agreement 3%, mean difference −1.37 (ours lower). We use ours, as pre-registered.

## What would change this
- **An abiotic reference set that is not enumerated.** Examples: meteoritic organics (Glavin et al. 2025 lists Bennu soluble organics), Miller–Urey and formose products, or a GDB subset filtered to match the ring distribution of the biotic set. If MA's added AUC disappears after ring matching, T7a's positive is a scaffold artefact.
- **Larger molecules.** MA is meant to matter above about 15 steps. Every molecule here is ≤ 17 heavy atoms, so this tests the low end only.

## Files
- Pre-registration: `docs/prereg/assembly_index_size_null.md` (sha256 b60f5f12…, in HASHES.txt).
- Code: `compute_ma.py`, `molecules.py`, `mixtures.py`, `planted_refit.py`.
- Outputs: `out/molecules.json`, `out/mixtures.json`, `out/planted_refit.json`, `out/validation_original_molfiles.json`, `results.json`, `ledger_rows.csv`.

## Citations
- Marshall et al. 2021, Nat Commun 12:3033. doi:10.1038/s41467-021-23258-x (verified, opened).
- Hazen et al. 2024, J R Soc Interface 21:20230632. doi:10.1098/rsif.2023.0632 (verified, opened).
- Glavin et al. 2025, Nat Astron. doi:10.1038/s41550-024-02472-9 (verified, opened).
- Vimal et al., assembly-theory software, arXiv:2507.08852 (unverified DOI).
- Rhea (rhea-db.org) and the GDB-13/17 subsets from the DaymudeLab/assembly-theory repo `data/` (data sources, no DOI cited).
