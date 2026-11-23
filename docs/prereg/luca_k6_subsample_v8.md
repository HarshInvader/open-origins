# Pre-registration v8 (K6): is the LUCA count invariant to taxon sampling on Moody et al.'s own data?

Sealed 2026-11-23 before any gene tree or reconciliation was run.

## Disclosure
- Moody et al.'s data download includes `Subsample_test/`: a 65-genome subsample with its rooted tree, pruned and trimmed alignments, and the root PPs from their own runs (`subsample_results.csv`).
- Their paper's Methods mention the test, but neither the main text nor Supplementary Information 1 reports its result. We searched both on 2026-11-23.
- A planning agent compared their deposited subsample PPs with their 700-genome PPs before this seal and reported:
  - a ratio of ΣPP of about 2.0–2.2 on common families;
  - a per-family Pearson correlation of 0.27.
- That comparison used their numbers, not ours. Nothing below has been run.

## Question
On Moody et al.'s own families, does the expected LUCA count change when the same method runs on 65 genomes instead of 700? Both runs estimate presence at the same node (the root between Archaea and Bacteria). If the count is not invariant, at most one of the two can be calibrated.

## Inputs (sha256 recorded in HASHES.txt at sealing)
- `Supp_data/Subsample_test/subsampled_tree.tre.rooted`: the 65-tip rooted species tree.
- `Supp_data/Subsample_test/gene_family_trimmed_for_sampling/*`: the trimmed alignments. A manifest hash covers all of them.
- `Supp_data/Subsample_test/subsample_results.csv`: their PPs. Duplicate KO rows are averaged per column, and the count of duplicates is reported.
- The 700-genome PPs: `kegg{1-5}_cons.txt` (as in K1).

## Family sample (fixed before any tree is built)
- A full run needs about 140 CPU-hours (2–2.5 days on the laptop's 3 Origins workers), and the laptop disk cannot hold all the bootstrap trees. So K6 runs on a seeded random sample instead.
- **Sample:** 800 of the 5,122 families with at least 2 sequences, drawn with `random.Random(20261123).sample`. The list is in `experiments/luca_calib/k6/family_sample_800.txt` (median 9 sequences; 6 families have ≥ 100).
- **Fit:** ŵ_65 is fitted on the sample alone. ΣPP_700 is summed over the same families.
- **Uncertainty:** a 95% interval for S comes from a 2,000-resample bootstrap over families, holding ŵ_65 fixed. If the interval spans two verdict regions, the verdict is "inconclusive", whatever the point estimate.
- **Disclosure:** before the seal we looked at alignment lengths in Moody et al.'s trimmed alignments (median 175 columns; median 47 for families with ≥ 100 sequences). We report them without a rule.

## Pipeline (code sealed by hash)
- **Adapter:** `experiments/luca_calib/k6/make_simdir.py` converts the inputs to our pipeline layout:
  - numeric family IDs, with a KO map;
  - species names stripped of "_";
  - gene names `<species>_<n>`.
- **Gene trees:** `pipeline/infer_trees.py` runs IQ-TREE 3 with `-m LG+F+G4 -B 1000 --wbtl`, seed 1, one thread per family.
  - Families with 2–3 sequences use their single topology.
  - Families with 1 sequence are skipped.
  - LG+F+G with 1,000 UFBoot is Moody et al.'s stated gene-tree model.
- **Driver:** `experiments/luca_calib/k6/run_k6.sh` runs the two pipeline scripts unchanged, 30 families per batch.
  - After each batch it deletes the batch's tree and ALE work files and keeps only the `uml_rec` files.
  - At the end it runs one reweighting over all of them.
- **Reconciliation:** `pipeline/run_ale.py --trees inferred` runs ALEobserve and ALEml_undated with flat origination, then Moody's reweighting code with one global O_R in [1, 20].
  - This uses the Mac arm64 ALE build. Its overflow on very large families is handled by the completion rule below.

## Gates
- **G1, fidelity:** on families scored by both, the Spearman correlation between our PP and the mean of Moody's `test1` and `test2` must be ≥ 0.80, and our ΣPP must be within ±15% of theirs.
  - **If G1 fails:** the verdict is "cannot reproduce their subsample". The primary readout is still reported, but labelled non-confirmatory.
- **G2, completion:** ALE failures must be ≤ 1% of reconcilable families, and failed families must not be more than 1.5× enriched among families with ≥ 100 sequences.
  - **Otherwise:** report S with failed families counted as PP 0 and as PP 1, and call the result inconclusive unless both give the same verdict.

## Primary readout
- **Definition:** S = ΣPP_65(ŵ_65) / ΣPP_700, summed over common families. Common means scored in all five 700-genome runs and reconciled by us at 65 genomes. ΣPP_700 is the median over the five runs of the per-run sum.
- **Verdict:**
  - 0.80 ≤ S ≤ 1.25: **invariant**.
  - S > 1.5 or S < 0.67: **not invariant**, so at most one estimate is calibrated.
  - Otherwise: inconclusive.

## Secondary readout (jackknife)
- **Draws:** three random draws (seeds 11, 12, 13) of half the archaeal and half the bacterial tips of the 65-genome tree.
- **Method:** use the same 800 families, matched by KO because the adapter renumbers families. Prune the alignments and the tree to the drawn tips, drop families left with fewer than 2 sequences, and run the same pipeline.
- **Definition:** J = mean over draws of ΣPP_half / ΣPP_65, on families common to all.
- **Verdict:**
  - J > 1.25 with all three draws > 1: **the count rises as taxa are removed**.
  - J < 0.8 with all three < 1: **the count falls as taxa are removed**.
  - 0.8 ≤ J ≤ 1.25: **no trend**.
  - Otherwise: inconclusive.

## Reported without a rule
- ŵ_65 and the prior root share.
- The default-prior ΣPP and the multiplier.
- The share of families with Bayes factor r(N−1) in [0.01, 10].
- The per-family Spearman correlation of 65 against 700.
- The means for the known-ancient and known-young control sets defined in v7.
- S under a flat prior.

## Reading, fixed in advance
- "Not invariant" does not say which estimate is wrong. A regime-matched simulation at the 65-genome scale (K7) is needed to decide that, and it will be pre-registered separately.
- "Invariant" removes one objection, but it does not show calibration.
