# Pre-registration (T1): is LUCA's exergonic core specific to synthesis, to the core, and to vents?

Status: DRAFT, written 2026-11-23 by the T1 prep agent; decisions fixed and two design flaws corrected after the planted run on 2026-11-23 (section "Changes after the planted run"). The decisions D1–D15 are fixed (section "Fixed decisions") and written into `CFG` in `experiments/t1_vent_exergonic/scripts/t1_analysis.py`. The coordinator filled in the planted results and sealed this file, the script and the data TSVs by hash (docs/prereg/HASHES.txt) on 2026-11-23, before `gate` or `real` was run.

## What has been seen (blinding disclosure)

- **Read in full:** the Wimmer et al. 2021 main text (PMC HTML), including the main-text Table 1 counts of exergonic and endergonic reactions per compound, and the published headline numbers (77–78%, 95–98%, "around pH 9, 80°C").
- **Wimmer SI Tables 3, 4, 5, 8, 9 and 10 (result tables):** I opened only the sheet names, legends and header rows. A probe script (`scripts/xlsx_layout.py`) replaced every numeric cell with `<num>` before printing.
  - From Table 3 I extracted one thing: per reaction, whether sheet A holds numbers or "NA". This is the `table3_has_value` column, 351 values and 51 NA, matching the paper. No value was printed, stored or summarised.
  - Table 8 is sorted by vent ΔG. I saw only its first two rows (legend lines), not the order.
- **Not computed:** no ΔG, ΔG′°, exergonic share or uncertainty for any Wimmer core reaction or any null-pool reaction, except one reaction. The install check and `selftest` used R00086, ATP + H₂O → ADP + Pi. R00086 turned out to be in the S4 null pool. I saw ΔG′° = −27.37 (pH 7, 25 °C), −37.92 (pH 9, 25 °C), −35.37 (pH 7, 80 °C) and −49.12 (pH 9, 80 °C) kJ/mol, all at I = 0.25 M and pMg 3. `CFG['null_exclude_ids']` drops R00086 from every null.
- **Planted run:** `planted` was run twice, once on the draft script and once on the corrected script. It uses synthetic ΔG′° only, with the real core and null covariates (participant counts, EC class, NTP flag, KEGG module clusters). `gate` and `real` have not been run.
- **Non-thermodynamic comparisons I did make:**
  - Core compounds against the eQuilibrator mini DB and the full-DB accession index (membership only).
  - Rhea and S4 candidate counts per matching stratum.
  - Whether S4's arrow direction agrees with Wimmer's polarisation for the 233 shared reactions: 207 the same and 26 opposite. This compares equations only.

## Hypothesis and claim under test

Wimmer W.L.E., Xavier J.C., Vieira A.d.N., Pereira D.P.H., Leidner J., Sousa F.L., Kleinermanns K., Preiner M., Martin W.F. 2021. Front. Microbiol. 12:793664, doi:10.3389/fmicb.2021.793664 (PMC8710812, CC BY).

Claims, verbatim:
- Abstract: "we find that 95–97% of these reactions are exergonic (ΔG ≤ 0 kJ⋅mol−1) at pH 7-10 and 80-100°C under nonequilibrium conditions with H2 replacing biochemical reductants."
- Results: "We observed a tendency for the largest proportion of reactions to be exergonic around pH 9, 80°C and at low H2 concentrations, very much in line with, but not constrained by, modern conditions at Lost City".
- Results: "At 100-fold less product than reactant, 98% of core reactions become exergonic (Figure 2C), with marginal increase at higher ratios and no marked effect of temperature except at very high pH."

The paper names its own limits:
- "the component contribution method does not obtain values for ΔG as a function of temperature, and that temperature effects are considered by the reaction quotient";
- "the reactions of metabolism as they operate in modern cells are generally exergonic, otherwise metabolism would not run."

**H1 (what would make the result informative about vents).** The high exergonic share depends on three things, so it is specific:
- (a) the hand-set synthesis direction, not just the imposed product-poor gradient;
- (b) the LUCA core, not any similarly built set of directional metabolic reactions;
- (c) vent conditions, beyond what the same contrast gives a matched null.

**H0 (generic).** The share comes from the gradient rule and the general exergonicity of physiologically directed reactions. Then reversing the core gives a similar share, a matched null gives a similar share, and the vent-versus-pond contrast is no larger for the core than for the null.

## Wimmer's method, verbatim (what the reproduction must copy)

- **Tool.** "Gibbs energies were calculated using eQuilibrator API (Flamholz et al., 2012; Beber et al., 2021) version 0.4.1 under Python v. 3.6.7 which bases its estimates on the component contribution method (Noor et al., 2013)."
- **Grid and conditions.** "Unless otherwise specified, environmental conditions were simulated by varying the pH from 1 to 14 in increments of 1 and temperature from 25 to 100°C in increments of 5°C at constant ionic strength of 250 mM, Mg2+ concentration fixed to 3 mM, and reactant concentrations set to 1 mM."
  - Mg²⁺ 3 mM is read as pMg 3 (−log10 0.003 = 2.52 would be the literal reading; see D12).
- **Gradient.** "Nonequilibrium conditions were simulated by altering the reactant to product ratio from 1:1 to 1:0.1 mM, 1:0.01 mM, 1:0.001 mM, 1:0.0001 mM and 1:10 mM".
  - Table 3 legend, sheet C: "the reactant concentration is 1 mM and the product concentration is 0.01 mM".
  - The rule is by side: "all reactants (compounds on the left side of reactions) and products (right side)". Every left-side species is at 1 mM and every right-side species at 0.01 mM.
- **H₂O and H⁺.** "If H+ is involved in the reaction, its activity is 1 in eq. (1) at pH 7. If water is involved in the reaction, its activity in eq. (1) is also 1".
  - Also: "water concentration is fixed at 55 M and cannot be changed in these calculations".
- **CO₂.** "We allowed the concentration of CO2 to vary freely across analyses, having a substrate concentration of 1 mM under nonequilibrium conditions."
  - The Figure 4 text instead says "gasses at 1 atm" and "other gasses at 1 atm" (see D3).
- **H₂ (H₂-substituted set only).** "The compound concentration ratio was set to nonequilibrium 1:0.01 mM with fixed H2 reactant and product concentrations 1 μM, 10 μM, 100 μM, 1 mM, 10 mM, and 100 mM".
  - Also: "As an environmental parameter, H2 reactant and product concentrations must be equal."
- **Exergonic.** "For all calculations, reactions are classified as exergonic if ΔG ≤ 0."
- **Coverage.** "Atomic balancing was checked prior to calculation, such that ΔG was only calculated for balanced reactions, excluding partial reactions. For 351 reactions Gibbs energy was calculable, for the remaining 51 reactions ΔG calculation failed due to involvement of KEGG compounds undefined in the eQuilibrator database, compounds having ambiguous structures, or unbalanced reactions."
- **Direction.** "The 402 metabolic reactions comprising the core were manually polarized in the direction of cell synthesis".
  - Also: "we manually polarized the reactions toward synthesis by writing the KEGG reactions from left to right such that the flux of carbon and nitrogen starts from CO2 and NH3 and proceeds within the KEGG pathways in the direction of amino acid, nucleotide and cofactor synthesis."
- **Vent cell.** Supplementary Table 8 title: "Biosynthetic core reactions ranked by associated Gibbs energy in extreme hydrothermal vent conditions."
  - Legend: "Hydrogen concentration is fixed to 1 µM with the remaining compounds at nonequilibrium 1:0.01 mM. Ionic strength is 250 mM." The column is headed "ΔG Vent [kJ·mol–1]" and "pH 9; 80 °C".

**Correction to the plan's premise.** In eQuilibrator (checked in 0.8.1 source and on R00086), the untransformed ΔrG° has no temperature term. The Legendre transform to ΔG′° does take `temperature`, though. For R00086 at pH 7, going from 25 to 80 °C changes ΔG′° by −8.0 kJ/mol. So whether Wimmer's T dependence is "only RT ln Q" depends on whether they set `cc.temperature` (D2).

## Inputs (exact)

Every file is under `experiments/t1_vent_exergonic/` unless noted. sha256 values are listed in "Hashes" below.

1. **Core.**
   - Wimmer SI Table 1 (`raw/wimmer_supp/x/Table_1.xlsx`, from the Europe PMC supplementaryFiles API for PMC8710812): 402 polarised reactions in KEGG format, with synthesis target, KEGG module, EC and KO.
   - Clean table: `data/wimmer2021_core_reactions.tsv`, built by `scripts/build_core_tsv.py`. It adds:
     - EC class (first digit; 20 reactions have none);
     - participant counts;
     - main-substrate and main-product counts (excluding the currency compounds listed in the script);
     - an NTP-hydrolysis flag (84 reactions; the paper counts 80 NTP-hydrolysing among the 351);
     - `table3_has_value`.
   - Six IDs are not plain KEGG IDs. RMAN1–4 are manual. R01214_1 and R01214_2 are the same valine–leucine transaminase written in both directions. That matters for the direction arm (D13).
2. **Reproduction target.** Wimmer SI Table 3 (`raw/wimmer_supp/x/Table_3.XLSX`).
   - Sheets A–F hold 402 rows × (ID, equation, "Uncertainty", 16 temperatures × 14 pH). Missing values are "NA" (51 rows).
   - Sheet A has equal 1 mM concentrations; sheet C has 1 : 0.01 mM.
3. **Null pool N1, UniProt direction.** Rhea release 143 (2026-11-04, CC BY 4.0, ftp.expasy.org/databases/rhea): `raw/rhea_rdf/rhea.rdf.gz`, plus `raw/rhea_tsv/rhea-tsv.tar.gz` (rhea2uniprot_sprot, rhea2metacyc, rhea2kegg_reaction, rhea2ec, chebi_pH7_3_mapping).
   - Clean table: `data/rhea_null_pool.tsv` (`scripts/build_null_pool.py`), one row per Rhea master reaction, written in its UniProt physiological direction.
   - Filters, with counts:

     | Filter | Reactions left |
     |---|---|
     | Approved masters | 18,612 |
     | Swiss-Prot "physiological direction" one way only (LR-only 7,999 or RL-only 616; 362 with both are dropped) | 8,391 |
     | Not transport | 7,930 |
     | Chemically balanced | 7,930 |
     | Small molecules only (no generic or polymer participants) | 6,139 |
     | All ChEBI IDs resolvable in the eQuilibrator bundled mini DB (directly, or through a parent whose pH 7.3 major microspecies is that ID) | 2,319 |
     | Not core (KEGG xref in core: 133 dropped; same compound sets as a core reaction: 2 dropped) | **2,184** |
     | Without O₂ | **1,910** |

   - Second direction label: MetaCyc via Rhea. Of the 2,184, 1,047 have no O₂ and an agreeing MetaCyc direction, 20 disagree, and 928 have no MetaCyc direction.
4. **Null pool N2, Xavier S4 KGML direction.** `experiments/raf_null/raw/rspb20192377supp5.txt`: Xavier et al. 2020 Proc. R. Soc. B, doi:10.1098/rspb.2019.2377, dataset S4, CC BY 4.0, already in the repo.
   - Direction, verbatim from their SI: "The reversibility of reactions was parsed out of KGML files for KEGG pathways and manually–curated."
   - Clean table: `data/s4_null_pool.tsv` (`scripts/build_s4_pool.py`). The 2,847 one-way (`=>`) reactions reduce to 2,751 parsable, 2,718 eQuilibrator-covered and **2,489 not core**. 248 of these have an NTP flag; none has O₂ (S4 is O₂-free by construction).
   - EC class is mapped through Rhea (rhea2kegg_reaction + rhea2ec). 929 are NA and 4 have more than one class.
   - S4 and Wimmer share curators and agree in direction on 207 of 233 shared reactions. So N2 tests "other reactions polarised the same way", and N1 tests "other reactions polarised by physiology".
5. **eQuilibrator.**
   - Versions: equilibrator-api 0.8.1, equilibrator-cache 0.8.1, equilibrator-cache-data 0.1.0, component-contribution 0.8.0, Python 3.15.0. The venv is `.venv`.
   - Compound DB: the bundled mini DB (`equilibrator_cache_data/mini_compounds.sqlite`, 65 MB). It covers 373 of the 378 core KEGG compounds.
   - The 5 uncovered compounds (C21510, C21511, C21512, C21615, C21971) are absent from the full-DB accession index too. The bloom index has no false negatives, so the 1.3 GB full DB (doi:10.5281/zenodo.4128543) adds no core coverage.
   - The full DB would raise null coverage. A bloom-filter estimate gives about 4,150 of the 6,139 step-6 Rhea candidates covered, against 2,319 with mini (D10).
   - Any Zenodo download is redirected to `raw/equilibrator_cache/` (`scripts/eq_env.py`). Nothing has been downloaded.
   - Install check, ATP + H₂O = ADP + Pi (C00002 + C00001 = C00008 + C00009) at pH 7, I = 0.25 M, pMg 3, 25 °C:
     - ΔG′° = −27.37 ± 0.30 kJ/mol;
     - ΔG′ (1 mM each) = −44.49 kJ/mol.

## Reproduction gate (`t1_analysis.py gate`; stop if it fails)

- **Our computation.** ΔG for every parsable, balanced core reaction at pH 7, 25 °C, I = 0.25 M, pMg 3, with every solute at 1 mM. H₂O and H⁺ are left out of Q.
- **Comparison.** Against Table 3 sheet A, column "25°C" / "pH 7", reaction by reaction (matched by ID and occurrence).
- **Pass** requires both:
  - Pearson r ≥ 0.98 over the reactions with values on both sides;
  - the exergonic share (ΔG ≤ 0) on that intersection within 2 percentage points of theirs on the same intersection.
- **Also reported, not gating:**
  - their share on their 351;
  - our share on all our computable reactions;
  - coverage counts;
  - the maximum absolute difference.
- **If the gate fails, stop.** Report the failure, then try the pre-listed fallbacks in this order, each a separate, declared rerun:
  1. `equilibrator-api==0.4.1` with the compound cache it pins;
  2. D12 (pMg 2.52).
  The arms are never run on a failed gate.

## Planted control (`t1_analysis.py planted`; run, synthetic only)

- **Model.** Synthetic ΔG′°(pH, T) = b − h·RT·ln10·(pH − 9).
  - b ~ N(shift, sd = 25 kJ/mol), independently per reaction.
  - h is the net number of protons released: drawn from {−1, 0, 1} ("flat"), set to 0, or drawn from {−1, +1} ("peak9").
  - Scenarios: S0 symmetric (core and null both b ~ N(0, 25), flat h); core shifted by −15 (S1; S1b with sd 15), −25 (S1c), −40 (S2), −60 (S2b), all flat h with a flat-h null; S3 core peak9 with a zero-h null; S4 core shifted −15 plus peak9, with a zero-h null.
  - Only null pool N1 is used, so the two-null agreement rule is not exercised here.
  - The transform temperature is 'T' (the 'by_gate' default falls back to 'T' when no gate file exists).
  - Independent ΔG′° noise σ = 5 kJ/mol per Monte Carlo draw.
  - The real participant counts set ln Q. The real strata, clusters and null pool N1 set the matching.
  - 100 replicates per scenario, with 200 draws and 200 bootstrap resamples (the real run uses 1,000 of each).
- **Sanity check.** Symmetric b at equal concentrations with no ln Q gives an exergonic share of 50.2%. This is the plan's "about 50%".
- **Results** (rates over 100 replicates):

| Scenario | Direction S / K | Specificity S / K | Setting S / K | Reversed share | Equal-conc gap (lower bound) | Gradient gap (no rule) | Contrast (lower bound) | Window (no rule) |
|---|---|---|---|---|---|---|---|---|
| Symmetric null | 0.00 / 1.00 | 0.00 / 1.00 | 0.00 / 1.00 | 77.8% | -6.5 (-13.8) | -3.7 | 0.5 (-2.8) | 0.86 |
| Core −15, spread 25 | 0.00 / 1.00 | 0.27 / 0.00 | 0.00 / 1.00 | 63.0% | 13.1 (5.9) | 5.0 | -1.1 (-4.2) | 0.89 |
| Core −15, spread 15 | 0.00 / 1.00 | 0.74 / 0.00 | 0.00 / 1.00 | 66.3% | 16.4 (9.3) | 5.0 | -1.1 (-4.0) | 0.63 |
| Core −25 | 0.00 / 0.74 | 1.00 / 0.00 | 0.00 / 1.00 | 51.5% | 23.0 (16.1) | 8.4 | -1.8 (-4.8) | 0.78 |
| Core −40 | 0.02 / 0.00 | 1.00 / 0.00 | 0.00 / 1.00 | 33.9% | 33.2 (27.1) | 10.7 | -2.6 (-5.5) | 0.51 |
| Core −60 | 1.00 / 0.00 | 1.00 / 0.00 | 0.00 / 1.00 | 15.5% | 39.1 (33.7) | 11.6 | -3.2 (-6.0) | 0.24 |
| Core one-proton pH 9 peak | 0.00 / 1.00 | 0.00 / 1.00 | 0.32 / 0.68 | 77.8% | -6.9 (-14.1) | -3.1 | 2.2 (-0.6) | 0.93 |
| Core −15 plus pH 9 peak | 0.00 / 1.00 | 0.25 / 0.00 | 0.02 / 0.98 | 62.9% | 13.0 (5.6) | 5.1 | 0.5 (-1.9) | 0.93 |

S = P(support), K = P(kill), over 100 replicates. Script sha256 07ea92d2… (`scripts_out/t1_planted.json`).

- **What this means:** Each arm is read on its own. The overall rule (two or more kills means uninformative) is kept, but the per-arm verdicts are the result.

- **K-specificity (equal concentrations) works.**
  - With no shift it gives kill in every replicate.
  - With the core shifted −25 kJ/mol or more, support in every replicate (P ≥ 0.8).
  - At −15 it is borderline: P(support) is 0.27 at a ΔG′° spread of 25 kJ/mol and 0.74 at 15.
  - Even under the symmetric null the equal-concentration gap is about −6 points, not 0. That baseline comes from the stoichiometry of the matched pairs, and the planted runs include it.
- **K-direction works as a test of its own question: does the gradient alone make the share?**
  - It gives kill whenever the planted core shift is −25 kJ/mol or less, because a 1:0.01 gradient makes most reversed reactions exergonic too.
  - It reaches support only at about −60.
  - So a kill here means the gradient, not the direction of synthesis, carries most of the exergonic share. It does not mean the core has no thermodynamic bias.
- **K-setting has low power.**
  - A core preference of one proton for pH 9 gives support in only 32% of replicates, and kill in 68%.
  - A K-setting kill is therefore weak evidence against a vent-specific preference. Report it as "no vent-specific preference detected", not as a refutation.
  - The window statistic falls in the vent window in about 90% of draws under the symmetric null, so it is uninformative. It is reported only.
- **The overall rule overstates kills.** In the −25 scenario, "uninformative" is returned 74% of the time, from the direction and setting kills, even though specificity supports in every replicate. The headline must give the three arms separately.

## The three arms (`t1_analysis.py real`; thresholds unchanged from the plan)

All shares are % of computable reactions with ΔG ≤ 0. The vent cell is pH 9, 80 °C (D6). "Gradient" means the 1 : 0.01 mM rule (every left-side solute at 1 mM, every right-side solute at 0.01 mM). "Equal concentrations" means every participant at 1 mM, as in Table 3 sheet A. Computable means: parsed, balanced, and σ(ΔG′°) < 100 kJ/mol (D4).

**K-direction.** Reverse every core reaction and apply the same gradient at the vent cell: the reversed reaction's reactants (the original products) are at 1 mM and its products at 0.01 mM.
- Statistic: the exergonic share of the reversed core at mean ΔG′° (D5). A Monte Carlo 95% interval is reported without a rule.
- Kill: ≥ 50%.
- Support: ≤ 30%.
- Otherwise: inconclusive.

**K-specificity.** The core share minus the share of a matched null at the vent cell **at equal concentrations** (changed after the planted run; see below).
- Matching: for each core reaction, one null reaction is drawn uniformly, with replacement, from the same stratum. The strata are tried in order until one is non-empty (D8):
  1. (EC class, main substrates capped at 3, main products capped at 3, NTP hydrolysis);
  2. (EC class, NTP);
  3. (NTP).
- Point gap: the core share minus the mean matched-null share over 1,000 matchings.
- CI: 1,000 cluster-bootstrap resamples of the core. A cluster is the first KEGG module; "added manually" reactions are clustered by synthesis target (D9). Each resample gets a fresh matching and a fresh joint ΔG′° draw.
- Kill: gap < 5 points and upper 95% bound < 10.
- Support: gap ≥ 15 points and lower bound > 5.
- Otherwise: inconclusive.
- Run on both N1 and N2. The arm's verdict stands only if both give the same verdict; otherwise it is inconclusive ("null rules disagree").
- Reported without a rule: the same gap at the vent cell under the gradient, with its point estimate and bootstrap interval (same matchings and draws).

**K-setting.** For each of 1,000 joint ΔG′° draws (multivariate normal from the component-contribution covariance, computed jointly for the core and the null), with a fresh matching:
- contrast = (core share at vent − core share at pond) − (null share at vent − null share at pond), under the gradient. Pond = pH 7, 25 °C (D6).
- Kill: the contrast's 95% interval includes 0, or lies wholly below 0 (D15).
- Support: the lower bound of the interval is > 0.
- (With these two rules every outcome is either a kill or a support.)
- Both null pools must agree, as for K-specificity.
- Reported without a rule (changed after the planted run; see below):
  - the grid cell(s) where the core share peaks over pH 1–14 × T 25–100 °C, as the fraction of draws in which the peak lies in pH 8–10 and T ≥ 70 °C (tied maxima get fractional credit);
  - the same contrast at equal concentrations (every participant at 1 mM), median and 95% interval;
  - the contrast with pond = (pH 6, 25 °C) and (pH 3, 70 °C).

**Changes after the planted run.** The first planted run (draft script, sha256 `1321bf5b…`) exposed two design flaws. Only these two were changed; no threshold was moved.
1. *K-specificity had a ceiling.* Under the gradient at the vent cell, the matched null is already about 85–88% exergonic, so the core can gain at most about 12–15 points. With the core shifted −60 kJ/mol the mean gap was still only 11.6 points, and support (gap ≥ 15, lower bound > 5) was reached in 0% of replicates at every shift. The gradient pushes both sets toward 100%, which hides the difference. The decision statistic is now the gap at the same cell with equal 1 mM concentrations, where the null sits near the middle of the scale. The gradient gap is still reported.
2. *K-setting's window criterion did not discriminate.* Under the symmetric null (S0) the core's peak fell in the pH 8–10, T ≥ 70 °C window in 86% of draws (mean fraction 0.865), because with Q < 1 a hotter cell is always more exergonic, and the window catches the hot end. With a real planted pH 9 peak (S3) the fraction was 0.93, barely above the null's. The verdict now uses the vent-minus-pond contrast only; the window fraction is reported. The equal-concentration contrast is added as a reported secondary, because the gradient's RT ln Q term grows with T and acts on core and null alike.

**Overall verdict.**
- Two or more kills: the Wimmer result is uninformative about vents.
- All three supported: supported.
- Otherwise: reported per arm.

**Seed.** 20261124, with one NumPy generator for the whole run.

## Ways it could be fooled

1. **The gradient is symmetric in name only.**
   - Q uses summed stoichiometry. A reaction with more product species than reactant species (for example a cleavage) gains more from a "products at 0.01 mM" rule than a condensation does.
   - Reversing swaps that advantage. So the direction arm partly measures the core's mix of cleavages and condensations, not only its ΔG′°.
   - We report the forward and reversed shares split by Δn = (products − reactants) as a descriptive table.
2. **The null is directed by physiology, which partly follows thermodynamics.**
   - Curators set physiological direction from observed flux, and flux follows ΔG. So both N1 and N2 are biased toward exergonic, like the core. This is the point of the test, but it means "the core is not special" is the expected result under H0.
   - N2 shares curators with the core (207 of 233 directions agree).
3. **Coverage bias.**
   - eQuilibrator covers only about 38% of small-molecule Rhea candidates with the mini DB. Covered compounds skew toward well-studied central metabolites, the same space as the core.
   - The full DB (D10) changes the pool. The pool also includes eukaryotic and secondary-metabolism reactions, because Swiss-Prot directions are not filtered by taxon (D14).
4. **Temperature in the transform.**
   - If Wimmer did not set `cc.temperature`, and we do (or the reverse), the vent cell differs systematically. The gate at 25 °C cannot detect this (D2, D11).
   - The plan's statement that ΔG′° has no T term is not exactly true for eQuilibrator.
5. **The peak criterion is nearly built in for T.**
   - With Q < 1, ln Q < 0, so a higher T always lowers ΔG. The core share should therefore peak at the top of the grid (95–100 °C), which lies inside "T ≥ 70 °C".
   - The window criterion effectively tests pH only. A share that rises monotonically with pH peaks at pH 14 and fails the window, even if vents are favoured over ponds.
   - The planted run confirmed this (null peak in the window in 86% of draws), so the window is now reported only and has no rule. The same RT ln Q term also enters the vent-minus-pond contrast, for core and null alike; the equal-concentration contrast is reported to show how much of the contrast it carries.
6. **Uncertainty structure.**
   - Component-contribution errors are correlated through shared groups. Drawing the core and the null jointly keeps this, but reactions outside the CC span have huge σ (D4).
   - σ also comes from eQuilibrator 0.8.1 parameters, not 0.4.1.
7. **Version drift.**
   - We cannot run eQuilibrator 0.4.1 / Python 3.6.7 without a separate environment. Training data and group definitions have changed since 2021, so r ≥ 0.98 may fail for reasons unrelated to the claim. That is a stop, not a kill.
8. **Pond definition.** "Pond" is a choice, not data (D6). The contrast depends on which pH and T stand for "not vent".
9. **The H₂-substituted set is not tested.**
   - The 95–97% headline uses H₂ in place of NAD(P)H, ferredoxin and flavodoxin (73 reactions; equations in SI Table 4 as names, not KEGG IDs).
   - The null cannot be H₂-substituted in the same way, so the primary arms use the organic-reductant core (Table 1 / Table 3, 351 reactions). A result here speaks to the "98% at 100-fold gradient" claim, and only indirectly to the H₂ headline (D1).

## Fixed decisions

Each takes the draft's recommendation; the values are in `CFG`.

- **D1, core equation set:** the Table 1 organic-reductant equations (the 351 Table 3 scores) for all arms (`core_set = 'table1'`); the H₂-substituted set is not run in the primary analysis.
- **D2, temperature in the Legendre transform:** `by_gate`: the gate computes both variants (`cc.temperature = T`, and 298.15 K) on the D11 diagnostic cell, `real` uses the one with the higher r, and the other is reported as a sensitivity run; this looks only at the reproduction target, never at an arm statistic.
- **D3, gases in Q:** CO₂ and H₂ aqueous, at the side concentration (`gas_rule = 'aqueous'`); gas at 1 bar is a gate fallback only.
- **D4, computability:** parsed, balanced and σ(ΔG′°) < 100 kJ/mol, for core and null alike; the number of the 351 lost to the σ rule is reported.
- **D5, direction verdict value:** the point estimate at mean ΔG′°; the Monte Carlo interval is reported without a rule.
- **D6, settings:** vent = (pH 9, 80 °C), pond = (pH 7, 25 °C); ponds (pH 6, 25 °C) and (pH 3, 70 °C) are reported without a rule.
- **D7, null pools:** N1 (Rhea, Swiss-Prot physiological direction, no O₂) primary and N2 (Xavier S4, KGML direction) second; K-specificity and K-setting verdicts count only if both agree.
- **D8, matching:** (EC class, main substrates ≤ 3, main products ≤ 3, NTP), coarsening to (EC class, NTP) and then (NTP), with replacement, no NAD(P)H/ferredoxin stratum; match levels are reported.
- **D9, bootstrap unit:** the first-listed KEGG module, with "added manually" reactions clustered by synthesis target.
- **D10, compound DB:** the bundled mini DB (`compound_tier = 'bundled'`); N1 on the full DB is a possible later declared sensitivity run, not the primary.
- **D11, second gate cell:** `('A', 7, 80)` enabled as a non-gating diagnostic for D2 only; pass/fail stays the single pH 7, 25 °C cell (`gate_second_cell = None`).
- **D12, pMg:** pMg 3 primary; pMg 2.52 is the second gate fallback.
- **D13, R01214_1 / R01214_2:** both kept, as Wimmer did, for the gate and all shares.
- **D14, taxon filter on N1:** none in the primary run.
- **D15, K-setting contrast interval wholly below 0:** counts as a kill.

## Hashes

```
# sha256, paths relative to experiments/t1_vent_exergonic/ (computed 2026-11-24, before sealing)
6cf0985393e1939447d1bedd974ae6bc2144dc4b76458b5964bda40fe75bd637  raw/wimmer_supp/PMC8710812_supplementaryFiles.zip
3e6f3edcd30e81370b542b2fda34bea75b60940bd464a6a52c508da86ef71a83  raw/wimmer_supp/x/Table_1.xlsx
314cb915bd149ae24decf58eb7e25e34471d719453f1c7c7b053ee42792377fe  raw/wimmer_supp/x/Table_3.XLSX
55a077750ea84f3fe537a99a2357727239f199afde273f2dc3e52239f733fc2a  raw/wimmer_supp/x/Table_8.XLSX
446c72559984cd913e1c2c34e5ca8ce6990f8f87d6aff7c363343d2ae9f312d2  raw/wimmer_pmc_html/PMC8710812.html
3d6bb7634859b05b83049bc097bba122533df399fd1525b2b942672a988a178c  raw/wimmer_pmc_html/PMC8710812_fulltext.xml
8f858aff8d984d8e882b90fac0d81d6980589fb819b460da388ccb796195fa25  raw/rhea_rdf/rhea.rdf.gz
fc41700bc6b6def07ef2dc4c8e18c0cb81af04e1b64955734f13356401df3ef1  raw/rhea_tsv/rhea-tsv.tar.gz
85fc8b6ce32932cf346a2d30a3a6ddc0e6e43b469abdb289a7471098f99b65ff  ../raf_null/raw/rspb20192377supp5.txt
624d2d6a9c82733d8991fdab0f95624dce43b9d86e7b3a43560065ba5b6c4660  data/wimmer2021_core_reactions.tsv
28d1b891b75cb499909fbc1fe9f8f50d328c20c736914d40d1fc7a58e7a688e8  data/rhea_null_pool.tsv
f3370bc34fc65754f2680b183e31e934a07f7a3384538c1819ab3220f7c7a7a4  data/s4_null_pool.tsv
d9c2bbab2fec9cb57e95da19135b9d4869548adf4dd669af8041acd5fd9211ae  scripts/build_core_tsv.py
7a7b7eb59abadf05411ba030acf3413d35208de8e8817728437bc71168c1efa3  scripts/build_null_pool.py
a3ebf33d810f292786c0da78b52fc03e10714114d41c45d53e74c867c6ec91d7  scripts/build_s4_pool.py
8ea07d65ef7966822ff03329ed6764071b485e77ca59ab51d3df415ae1bb0264  scripts/eq_env.py
f26a16b037384a593163a86c49dbf7c284fae393113fee1a7c9189cf19edf337  scripts/full_db_coverage.py
bf18facf82c9a6a939bf140cd2ddc4e6e5848b78c04dfb6b14c7c26e028335a4  scripts/html2text.py
0932ca333d991dde823beebeb25c4288174974c140faf15eb60b1a69ba76973b  scripts/mechanics_test.py
1321bf5ba37d29adf02b300a14c46845e8437c9a420e913b1380d383c373709b  scripts/t1_analysis.py
8a1617812f9a4973854b24d0bee2d404b8afa441969762d845814eb1247c8a84  scripts/verify_install.py
6912259968ecf0329097c33f2f97d433d6022b51474b1fddeb6f54ed94fae851  scripts/xlsx_dump.py
310498a3374d2b62a011dc2191a0a64cd0093ec92287465a9f8064faa2940a6d  scripts/xlsx_layout.py
4770f5d0787e7d12183974404ab3af8ac98b964fecac0b4526453d91a50c561f  .venv/.../equilibrator_cache_data/mini_compounds.sqlite
7be6cc5eb6b0b19f28385d25b3583b06d16908f3c7550c890ea639d727cd82ac  .venv/.../equilibrator_cache_data/accessions.idx
```

Rerun `shasum -a 256` at sealing. Any change to t1_analysis.py after this point invalidates the planted run, which must then be redone.

## Sources actually opened

- Wimmer et al. 2021, doi:10.3389/fmicb.2021.793664:
  - main text, from https://pmc.ncbi.nlm.nih.gov/articles/PMC8710812/ and https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8710812/fullTextXML (saved, not read separately);
  - SI zip, from https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8710812/supplementaryFiles. The first attempt returned HTTP 500; the retry succeeded.
- Rhea release 143, https://ftp.expasy.org/databases/rhea/: tsv/rhea-tsv.tar.gz, rdf/rhea.rdf.gz, rdf/README.txt, LICENSE.txt, rhea-release.properties.
  - The rhea-db.org REST API returned a Cloudflare JavaScript challenge. I treated it as a block and did not work around it.
- Xavier et al. 2020, doi:10.1098/rspb.2019.2377: SI text (rspb20192377supp1.pdf) and dataset S4, both already in the repo under experiments/raf_null/raw/.
- eQuilibrator: PyPI packages equilibrator-api 0.8.1 and its dependencies. Their source was read for phase defaults, the Legendre transform and the cache tiers.
