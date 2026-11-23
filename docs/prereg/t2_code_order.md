# Pre-registration (T2): do asteroid amino-acid abundances predict the Wehbi 2024 code order beyond molecular weight?

Status: drafted 2026-11-23 by the T2 prep agent. The coordinator fixed decisions D1–D11 (section "Fixed decisions", which overrides anything above it) and sealed it by hash, together with `experiments/t2_code_order/scripts/t2_analysis.py` and the four data TSVs, before any statistic relating abundance to code order was computed.

## What has been seen (blinding disclosure)

- I transcribed every input value by hand: Wehbi Table 1, Glavin Extended Data Tables 2 and 3 (protein amino acid rows), and Higgs & Pudritz Table 2. So I have read both the abundance columns and the order column in full.
- I have not computed any correlation, rank comparison, partial τ or regression that relates abundance to code order, on any sample, and I have not sorted one list by the other.
- The only numbers I computed:
  - the Wehbi ratios recomputed from their Dataset S2 (code-order side only);
  - sums of the transcribed Extended Data Table 2 cells, checked against the printed column sums (abundance side only; all five matched).
- Wehbi's GitHub file `AminoAcid_properties.csv` also has meteorite abundance columns (`AA_abundance_Murchison`, `CM2`, `CR2`, …). I extracted only `Letter` and `MolecularWeightsDa` and did not read those columns. Wehbi's analysis script never refers to them (grep for Murchison/CM2/CR2/meteor found nothing).

## Hypothesis

H1 is the "prebiotic availability" route to code order: amino acids that were more abundant abiotically entered the genetic code earlier. Higgs & Pudritz 2009 state it this way (verbatim, arXiv:0904.0402): "Our hypothesis is that the early amino acids were frequent in the environment at the time of the origin of the genetic code and the first proteins, but that the late amino acids were rare or …".

Testable form:
- Wehbi's LUCA usage is a measure of order that does not use abiotic data.
- Across amino acids, log abundance in a pristine returned asteroid sample should be positively associated with LUCA usage after controlling for molecular weight. Higher LUCA usage means earlier.
- Molecular weight is the control because Wehbi report that "Smaller amino acids are enriched in LUCA (Fig. 4A; weighted R2 = 0.48, P = 0.0005)". Meteoritic abundance also falls with carbon number, so molecular weight alone could produce an association.

## Inputs (exact)

All files are in `experiments/t2_code_order/`. Raw downloads are in `raw/<source>/`, and the clean TSVs are in `data/`, each carrying the sha256 of its source file in the header.

1. **Code order.** `data/wehbi2024_luca_usage.tsv`.
   - Source: Wehbi S, Wheeler A, Morel B, Manepalli N, Minh BQ, Lauretta DS, Masel J. 2024. PNAS 121:e2410311121, doi:10.1073/pnas.2410311121, Table 1 (from the PMC11670089 HTML).
   - Definition (verbatim Table 1 title): "LUCA and pre-LUCA clans' ancestral amino acid frequencies are divided by post-LUCA clan's ancestral amino acid frequencies to produce measures of relative usage".
   - The paper recommends this quantity (verbatim): "we recommend using the LUCA amino acid enrichment values plotted on the y-axis of Fig. 4A, which can be found together with their SE in Table 1."
   - Table 1 prints 3 significant figures, with ties A = T = 1.07 and C = P = 1.01.
   - `luca_usage_recomputed` comes from Dataset S2 (weighted by `Clan_Conlength`; 309 LUCA and 1,232 post-LUCA clans). It rounds to Table 1 for all 20 amino acids and breaks those ties.
2. **Molecular weight.** `data/aa_molecular_weight.tsv`.
   - Primary: Wehbi's own covariate, `MolecularWeightsDa` from `AminoAcid_properties.csv` (GitHub sawsanwehbi/Pfam-age-classification, tree 01219d85…). These are integer Da with ties I = L = 131 and K = Q = 146.
   - Higgs & Pudritz MW (one decimal) is kept for a sensitivity run.
3. **Abundances.** Glavin DP et al. 2025, Nat. Astron. 9:199–210, doi:10.1038/s41550-024-02472-9 (CC BY; PMC11842271).
   - `data/glavin2025_edt2_free_protein_aa.tsv`, from Extended Data Table 2.
     - All 20 protein amino acids, D+L combined, **free** (not hydrolysed), measured by AccQ·Tag LC-FD/MS, n = 3.
     - Samples: Bennu OREX-803001-0, Murchison (CM2), Tarda, Orgueil, and Ryugu A0106. Ryugu values are from Parker et al. 2023, GCA 347:42–57, and 11 of the 20 Ryugu cells are "n.r.".
   - `data/glavin2025_edt3_free_total_protein_aa.tsv`, from Extended Data Table 3.
     - OPA/NAC LC-FD/ToF-MS + HRMS, D and L listed separately.
     - **Free** and **total** values for Bennu and Murchison: "total (free + bound) amino acid abundances" after "6 M HCl vapour at 150 °C for 3 h".
     - Total only for Tarda, Orgueil and Ryugu A0106.
     - Only 9 protein amino acids (G, A, S, D, T, E, V, L, I). OPA/NAC does not label secondary amines, so there is no Pro.
   - Status codes in both files, defined by Glavin's verbatim legends:
     - `quantified`;
     - `below_detection_limit` ("<x"; x is stored as `detection_limit`);
     - `trace_below_quantitation` ("tr.": "tentatively identified at trace levels but was below the limit of quantitation");
     - `upper_limit_not_blank_corrected` ("≤x", footnote d);
     - `not_reported`;
     - `not_determined`.
4. **Comparator (not part of the decision).** `data/higgs_pudritz2009_table2.tsv`: Robs, Rcode, Crel, ΔG, ATP and MW. Robs is H&P's abundance-based order.

## Statistic

- Kendall partial τ: τ(x,y·z) = (τxy − τxz·τyz) / sqrt((1 − τxz²)(1 − τyz²)), using τ-b for each pairwise term.
  - x = log10 abundance.
  - y = Wehbi LUCA usage.
  - z = molecular weight.
- Prediction: τ(x,y·z) > 0.
- Non-detects: "<DL" cells enter as ties at the detection limit (but see decision D4, which this rule does not settle).
- p-value: one-sided, (1 + #{τ_perm ≥ τ_obs}) / (1 + 10⁵), from 10⁵ permutations with a fixed seed. The permutation scheme is decision D7.
- Upper 95% bound on τ: method to be fixed (D8).

## Design

- **Fit set: Murchison.** Partial τ has no free parameters, so "fit" can only mean choosing the analysis options (D1–D8) by looking at Murchison. My recommendation is to fix all options now, blind, and report Murchison as an exploratory third sample, so that nothing is tuned on any sample (see D9).
- **Scored sets: Bennu (OREX-803001-0) and Ryugu (A0106).**
- **Decision rule** (from the plan, unchanged):
  - **Support:** τ ≥ 0.4 and p < 0.01, in both Bennu and Ryugu.
  - **Kill:** τ ≤ 0.1 in both, with the upper 95% bound < 0.4 in both.
  - **Otherwise:** inconclusive.
- **Planted-signal power check**, run before any real statistic and with the same code:
  - Use the real MW, the real Wehbi y, the real detection limits and the real non-detect pattern for each scored sample.
  - Generate x = a·rank(y) + b·rank(z) + noise, at target partial τ ∈ {0, 0.2, 0.4, 0.6}.
  - Apply each sample's censoring by setting every planted value below that sample's DL to the DL tie.
  - Report P(support), P(kill) and P(inconclusive) at each τ, for n = 9 (Extended Data Table 3 subset) and n = 20 (Extended Data Table 2).
  - If P(support | τ = 0.6) < 0.5 or P(kill | τ = 0) < 0.5 for the chosen inputs, say so before unblinding, and downgrade the test to "cannot decide" for that input set rather than run it.
  - Expectation, not yet measured: at n ≤ 9 with heavy ties, "upper bound < 0.4" is close to unreachable, so the kill arm may be impossible by design.

## Ways it could be fooled

1. **Size confound beyond MW.**
   - Strecker yields, the ΔG of formation (H&P) and abundance all scale with carbon number and side-chain type.
   - Integer MW ties (I/L, K/Q) and MW's coarseness may leave size signal in the residual.
   - Sensitivity runs: H&P MW, and carbon number.
2. **Analytical coverage, not abundance.**
   - Hot-water extraction destroys or does not recover some amino acids. Glavin SI Table 12 footnote c: Asn, Gln and Cys are "Unstable in hot water and may have decomposed during extraction".
   - Acid hydrolysis (total fraction) converts Asn → Asp and Gln → Glu, and destroys Trp.
   - The large amino acids that Wehbi calls "late" (W, Y, F, R, H, K, Q, N) are exactly the non-detects. So any detection-biased measure lines up with the size and lateness axis by construction. MW control helps only in part.
3. **Censoring geometry.**
   - DLs differ by analyte and sample. For example, Ryugu L-Ala "<0.44" sits beside D-Ala 0.025, and Bennu Glu 0.01 is quantified while His is "<0.1".
   - "Ties at the DL" can put a quantified amino acid below a non-detect.
4. **Terrestrial contamination**, mainly in Murchison (a meteorite curated since 1969).
   - The L-enantiomer exceeds D in total L-Glu (10.6 vs 3.5), L-Ser (3.6 vs 0.54) and L-Thr (13 vs 1.2).
   - Glavin and Naraoka report Ryugu A0106 L-Ser and L-Val excesses, and Naraoka write that "contamination is likely the non-racemic valine in the A0106 extract". Using L or D+L would reward biology-like patterns.
5. **Method dependence for one sample.**
   - Ryugu A0106 glycine is "~0.6 nmol g-1" by LC-FD/HRMS but "5.6 nmol g-1" by 3D-HPLC/FD (Naraoka et al. 2023, Science, doi:10.1126/science.abn9033, HAL copy).
   - Bennu free glycine is 10.1 in Extended Data Table 2 (AccQ·Tag) but 33 in Extended Data Table 3 (OPA/NAC). The choice of table changes x.
6. **Small n and non-independence.**
   - Amino acids share biosynthetic families and chemistry, and n ≤ 20 (9 for Extended Data Table 3). A single amino acid can swing τ.
   - Run a leave-one-out sensitivity and report it, but do not use it for the decision.
7. **Circularity and shared authorship.**
   - Lauretta (OSIRIS-REx PI) is a Wehbi co-author, and Wehbi's property file holds meteorite columns, so they may have looked at this informally. Their published text does not test abundance against LUCA usage.
   - The order itself is derived only from protein sequences.
   - Wehbi already report that Trifonov's consensus order (which includes abiotic-abundance metrics) adds nothing beyond MW. This prior result makes a null the expected outcome.
8. **Ryugu and Bennu are not independent tests of different chemistry.** Both are CI-like aqueously altered bodies analysed partly by the same Goddard lab. Agreement between them is weaker evidence than two independent bodies would give.

## Open decisions (must be fixed before sealing)

- **D1, amino-acid set.** Choose one:
  - (a) all 20, from Extended Data Table 2 (free);
  - (b) the 9 in Extended Data Table 3;
  - (c) the amino acids detected in at least one scored sample;
  - (d) Gly excluded (achiral; dominates).
  - Ryugu has 9 non-"n.r." cells in Extended Data Table 2 and 9 in Extended Data Table 3, so its n ≤ 9 whatever is chosen. Decide whether "n.r." is dropped (recommended) or treated as a non-detect (not defensible: "not reported" is not "not detected").
- **D2, fraction.** Free (Extended Data Table 2 or 3) or total (Extended Data Table 3, Bennu and Murchison only; Ryugu is total-only in Extended Data Table 3).
  - Total for Ryugu vs free for Bennu would mix measures.
  - Options: free for both, using Extended Data Table 2 (Ryugu free values exist for S, G, D, E, A, and "<" for T, V, L, I); or total for both, using Extended Data Table 3.
- **D3, enantiomer.** D+L as printed (Extended Data Table 2), D only, or 2×D as a contamination-robust total (Extended Data Table 3 only). How to sum when one enantiomer is censored, for example Ryugu D-Ala 0.025 with L-Ala "<0.44".
- **D4, non-detect and trace handling.**
  - "<DL" → tie at DL (plan default).
  - "tr." has no printed number. Options: tie at the 0.1 nmol g⁻¹ level the text calls "the 0.1 nmol g-1 detection limit", or rank all "tr." above all "<DL" and below all quantified.
  - "≤x" (not blank-corrected) → value x, or censored at x.
  - Whether to censor every value below the sample's largest DL to one tie (Helsel-style). This avoids problem 3 in "Ways it could be fooled" but loses information.
- **D5, Ryugu sample and source.**
  - A0106 as printed in Glavin (Parker 2023 and Naraoka 2023 data).
  - The alternative Ryugu sample C0107 is in Parker et al. 2023. I could not open it (ScienceDirect returned 403 to automated access), so C0107 is unavailable for now.
  - Also decide the footnote-f values (3D-HPLC single measurement for Val/Iva/Nva): use them, or keep the "<" limits.
- **D6, the y variable.**
  - Table 1 rounded values (tied) or the Dataset S2 recomputed values (untied).
  - Whether to use Wehbi's SE at all, for example a sensitivity run that drops amino acids whose usage CI includes 1.
- **D7, permutation scheme.**
  - (i) Permute x over amino acids, holding (y, z) pairs. This is the plan default; its null is x ⊥ (y, z), which also breaks the x–z link.
  - (ii) Permute y within MW strata, for example tertiles, which keeps the x–z structure.
  - Fix the seed.
- **D8, the upper 95% bound.** Options: bootstrap over amino acids (unstable at n ≤ 9), inverting the permutation test over planted shifts, or a jackknife. The kill rule cannot be applied until this is fixed.
- **D9, the role of Murchison.** Recommendation: no tuning; report it as a third, exploratory sample under the fixed pipeline. Also decide the Murchison source:
  - Glavin Extended Data Tables 2/3 (the UIC sample, 26.3 mg, same lab and method as Bennu); or
  - the literature compilations behind H&P M1 (Engel & Nagy 1982, H₂O extract), which are not downloaded and are likely paywalled.
- **D10, log base and zeros.** log10. Zeros cannot occur (all cells are positive or censored).
- **D11, MW source.** Wehbi integer MW (primary) or H&P MW (sensitivity). Whether carbon number is an extra covariate.

## Sources actually opened

- Wehbi et al. 2024 PNAS, doi:10.1073/pnas.2410311121:
  - main text, from https://pmc.ncbi.nlm.nih.gov/articles/PMC11670089/;
  - SI PDF and Datasets S1–S2, via the Europe PMC supplementaryFiles API for PMC11670089;
  - GitHub sawsanwehbi/Pfam-age-classification (README, AminoAcid_properties.csv, AncientAminoAcidUsageAnalysis.R).
- Glavin et al. 2025 Nat. Astron., doi:10.1038/s41550-024-02472-9:
  - main text, from https://pmc.ncbi.nlm.nih.gov/articles/PMC11842271/;
  - SI PDF and source-data xlsx, via the Europe PMC supplementaryFiles API;
  - full-resolution Extended Data Table 2/3/4 images, from static-content.springer.com.
- Higgs & Pudritz 2009 Astrobiology, doi:10.1089/ast.2008.0280: arXiv:0904.0402 (submitted version).
- Naraoka et al. 2023 Science, doi:10.1126/science.abn9033: HAL hal-04208565 (submitted manuscript; Table S3 is not in that copy).

## Fixed decisions (coordinator, at sealing; these override the draft text above)

- **D1, amino-acid set.** All 20 protein amino acids from Extended Data Table 2. Amino acids marked "n.r." or "n.d." in a sample are dropped from that sample, not treated as non-detects. Gly is kept.
- **D2, fraction.** Free (hot-water extract) for every sample, from Extended Data Table 2. Extended Data Table 3 (free and total) is not used.
- **D3, enantiomer.** D+L as printed in Extended Data Table 2.
- **D4, cell rules.**
  - Quantified: the value.
  - "<DL": the DL, so non-detects tie at their DL.
  - "tr.": 0.1 nmol g⁻¹.
  - "≤x": x.
  - No Helsel re-censoring.
- **D5, Ryugu.** A0106 as printed in Glavin Extended Data Table 2. Footnote-f single-measurement values are not substituted for "<" limits.
- **D6, y.** `luca_usage_recomputed` from Dataset S2 (untied).
- **D7, permutation.** y is permuted within molecular-weight tertiles of that sample's amino acids (stable sort; `numpy.array_split` into 3). There are 10⁵ draws and the p-value is one-sided.
- **D8, upper bound.** The 95th percentile of 10⁴ bootstrap resamples of amino acids.
- **D9, Murchison.** Glavin Extended Data Table 2 Murchison, reported as exploratory and not used in the verdict. Nothing is tuned on any sample.
- **D10, log scale.** log10.
- **D11, molecular weight.** Wehbi's integer molecular weight. No other covariate in the primary analysis.
- **Seed.** 20261123, one NumPy generator for the whole run.
- **Order of runs.**
  1. `t2_analysis.py power` first. It uses each scored sample's amino-acid set and censoring count, never its values, and reports the verdict rates at planted strengths 0 to 0.8 (400 draws each).
  2. If P(kill) < 0.5 at planted strength 0, or P(support) < 0.5 at the strongest planted strength, for either scored sample: the corresponding verdict is declared unreachable before `real` is run, and the run is reported as unable to reach that verdict.
  3. Then `t2_analysis.py real`.
- **Verdict.**
  - Support: both Bennu and Ryugu give partial τ ≥ 0.4 and p < 0.01.
  - Kill: both give partial τ ≤ 0.1 and an upper 95% bound < 0.4.
  - Otherwise: inconclusive.
- **Reported without a rule.**
  - Leave-one-out partial τ.
  - The pairwise τ-b terms.
  - Murchison.
