# Pre-registration: does the order of metabolic assembly track enzyme age and metal catalysis? (Mrnjavac et al. 2026 data)

Agent: orig-paper. Written 2026-11-18, before any association between strata and age or metal labels was computed.

## What I have looked at
I have seen only the structure of the tables: sheet names, column headers, how the Stratification sheet is laid out, and the marginal counts of each label:
- S2 Category: LUCA 166, LBCA 89, LACA 38, gray LBCA 29, gray LACA 8;
- S4 grades: A 36, B 105, C 22;
- Moody overlap: 50 of 650 KOs.

I have not cross-tabulated any label against stratum.

## Source
- Mrnjavac N, et al. 2026, "Intermediate stages in the origin of metabolism at a phosphorylating hydrothermal vent", Sci Adv, doi:10.1126/sciadv.aef3128. Licence CC BY, as reported by the Europe PMC record for PMC13440417. Supplementary Tables S1-S10 were downloaded from Europe PMC.
- The paper orders 424 core reactions into 49 strata. A reaction's stratum is the first time step at which all of its reactants exist. Separately, the paper assigns enzymes to LUCA, LBCA or LACA by their distribution across taxa, and lists reactions reported to run without enzymes. Its stated view is that LUCA's enzymatic metabolism was incomplete and was then expanded in the lineages leading to LBCA and LACA, and that native metals came before enzymes.
- As far as I can find in the text (grep of the arXiv version for LUCA/LBCA/LACA/stratum), the paper never tests whether the age labels or the metal labels line up with the strata.

## Ideas being combined
1. **Granick's hypothesis**, a well-known proposal: the order of steps in biosynthesis recapitulates the order in which they evolved.
2. **The authors' two-stage claim**: a LUCA core, then lineage-specific additions.
3. **Metals before enzymes**: Wächtershäuser; Muchowska/Moran; Preiner et al.

Combined prediction: if the stratification reflects real history, reactions whose enzymes trace to LUCA, or that run on metals without enzymes, should sit in earlier strata. This should hold **even within a pathway**, so that it is not explained only by cofactor pathways being both late and lineage-specific.

## Data preparation (fixed now)
- **Stratum.** The Stratification sheet of Table S8 is parsed as: header "Rank k reactions:", followed by IDs.
  - Each ID is reduced to a base KEGG ID with the regex `R\d{5}`. Manual IDs (`RMAN…`) that have no KEGG ID are dropped.
  - A base ID that appears more than once (e.g. R09543 and R09543_ENV) gets its **minimum** rank.
- **Pathway.** Taken from the `Pathway` column of the Reactions sheet of Table S8, matched on base ID and used as a literal string. If a base ID has several rows, the first non-empty value is used. Reactions with no pathway are placed in a block called "none".
- **Age.** From the Distribution sheet of Table S2.
  - The `Reaction ID` field is split on commas.
  - A base ID is labelled **LUCA** if any of its clusters is LUCA. Otherwise it is **lineage** (LBCA or LACA) if any cluster is LBCA or LACA.
  - Gray categories are left out of the primary test, as the paper does in Fig. S2. A sensitivity run counts gray as lineage.
  - Stratified reactions with no age label are left out of the age tests.
- **Metal.** From Table S4, using the first letter of column "Reaction reported experimentally in aqueous conditions, uncatalyzed or catalyzed by transition metals".
  - **Metal-A** = grade A, the exact reaction reported.
  - A secondary label, **Metal-AB**, is grade A or B.
  - The comparison group is every other stratified reaction, including those not listed in S4.
- **Moody.** From the "Comparison Moody et al. 2024" sheet of Table S2.
  - A base ID is **Moody-LUCA** if any of its KOs is marked "yes", and **Moody-no** if all its listed KOs are "no".
  - Reactions with no KO in that sheet are left out of H3.
  - Moody et al. 2024 (Nat Ecol Evol 8:1654, doi:10.1038/s41559-024-02461-1) infer LUCA by gene-tree reconciliation, a method independent of the distribution rule used in S2. This label is the **held-out** check.

## Statistic and null
- **Statistic.** D = mean stratum of the "old" group minus mean stratum of the "young" group. The prediction is D < 0.
- **Primary null (fair): permutation within pathway.** Labels are shuffled only among reactions of the same pathway, 10,000 times with seed 0.
  - One-sided p = (1 + #{D_perm ≤ D_obs}) / 10,001.
  - This removes the confound that whole pathways, such as cofactors, are both late and lineage-specific.
- **Secondary null:** a global shuffle, reported for comparison only.
- **Rank-based check:** the same within-pathway test using mean within-pathway rank percentile in place of the raw stratum. Reported, but it does not decide any hypothesis.

## Hypotheses (one-sided, within-pathway null, Holm correction across H1-H3 at α = 0.05)
- **H1 (age; inspired by Granick and the authors' two-stage view).** LUCA reactions sit in earlier strata than lineage (LBCA+LACA) reactions: D < 0. **Prediction: supported.**
- **H2 (metals first).** Metal-A reactions sit in earlier strata than the rest. **Prediction: supported.**
- **H3 (held out).** Moody-LUCA reactions sit earlier than Moody-no reactions. **Prediction: same direction as H1.**
  - n is small (≤ 50 positive KOs), so I expect low power. If H3 does not reach significance, H1 is still reported, but it is called "not replicated by an independent LUCA label".
- **H4 (split, descriptive).** The H1 direction holds separately for LUCA vs LBCA and for LUCA vs LACA. Both must have D < 0 for H1 to be called robust. No p-value is used.
- **H5 (secondary label).** H2 is repeated with Metal-AB. Descriptive only.

## Planted check (run before the real labels, on the real strata and pathways)
- **Power plant.** Create a fake label with the same group sizes as H1: within each pathway, reactions below that pathway's median stratum get "old" with probability 0.7, and those above with probability 0.3.
  - Run the within-pathway test 200 times, with seeds 1-200 and 2,000 permutations each.
  - Pass: at least 80% of runs give p < 0.05.
- **Null plant.** Assign the label at random within pathway, 200 times.
  - Pass: the rejection rate at 0.05 is ≤ 0.08.
- If either plant fails, the real test is not interpreted, and the failure is reported.

## What would count as a strong result
H1 and H2 both survive Holm under the within-pathway null, H3 agrees in direction, and H4 holds in both lineages. That would be quantitative support that the network's assembly order is historical, not only a topological ordering.

If H1 fails within pathways but passes under the global null, the age-order signal is explained by the pathway (cofactors late), and the claim that the order is historical gains nothing from it. That goes to NEGATIVE_ATLAS.

## Caveats stated now
- The stratification depends on the authors' choices of food set and environment-supplied cofactor equivalents.
- The S4 literature list is shaped by what chemists chose to try, and early central-carbon reactions are probably studied more often (a sampling bias toward early strata). This is a known confound for H2; within-pathway permutation reduces it but does not remove it.
- The age labels come from the same authors, so this is a test of internal consistency between two of the paper's analyses, not fully independent data. H3 is the only independent label.
- The compute is trivial (well under a minute), so the compute lock is not needed. This is stated, not assumed.
