# enc-B encoding notes (board task #29)

Encoded blind from the sources listed below. Nothing was scored. Steps and hand-offs follow each paper's own schemes.

## Sources opened
- R6 Becker 2018: PMC5765019 full text. SI PDF not obtainable (the PMC download returned a JavaScript "Preparing to download" page; not bypassed).
- R7 Becker 2019: legal green open copy, submitted manuscript with SI, LMU repository (epub.ub.uni-muenchen.de/71503). Read in full.
- R8 Xu 2020: PMC7116818 full text. SI not obtainable (same reason as R6).
- R9 Yi 2020: PMC7306801 main text. SI not read.
- R10 Ritson 2022: PMC9619408 main text. SI not read.
- R11 Gibard 2018: PMC6295206 accepted manuscript. SI not obtainable.
- Islam 2017 (10.1038/nchem.2703) and Powner 2009 are cited only through Ritson 2022; not opened.

No route is wholly "unread". Unread steps: R10 C2 and C3.

## Global conventions and deviations
- `purified`: True for isolated, crystallised or synthesised intermediates used as clean samples. A commercial reagent that the authors claim as a scenario feedstock is purified=False, following steps.py, even though the brief says "bought -> True". Exceptions: commercial nucleosides in R11 (uridine) and adenine/TAP-type compounds are marked per step; R11 uridine is True because the scenario does not claim it as a feedstock.
- RT = 23 C is an assumption (as in steps_dsm.py). Explicit temperatures are used where stated (R7 Y1 uses the SI 25 C).
- Redox "reducing" only where the source ran anoxic (R7 Y4 argon, R9 N1 N2). Elsewhere "unknown". Scenario redox labels ("neutral", "reducing") are mine; sources mostly do not state them.
- Rain stream (pH 7, 23 C, pure water) is ASSUMED in every scenario that uses it. R7 acid_rain pH 3 and carbonate_water pH 10 are the authors' pH extremes; stream T is assumed.
- Precipitation is encoded as property="crystallisation".
- Hand-off lists always have len(steps)-1 entries.
- Linear chains cannot express convergence. Branches that join a second purified intermediate (R6 ribose, R8 alpha-anhydrouridine, R10 ribo-aminooxazoline and CV-DCI) enter as inputs; the second arm's origin is not encoded.
- Radiolysis (R9) is not on the closed process list; recorded only as a step condition.
- Paste (R11) has no matching solvent label; solvent set to "unknown".
- Concentrations computed from SI masses and volumes assume volumes add. Listed in `assumptions` per step.

## R6 Becker 2018 (6 steps, 5 hand-offs)
- Only the headline purine-nucleoside route is encoded; the pyrimidine and diversification branches are one optional step (B3).
- Several authors' environments (rivers, ponds) collapse into one geothermal-field scenario.
- B2 T: salts melt at 108-159 C; the top of the 100-160 C gradient (160) is used.
- B3 pH 0.3 computed from 0.5 M HCl; aminolysis at pH ~10 not encoded.
- B4 to B6: T, pH, concentrations not in the main text (NaN); SI not obtained.
- "Dry" solvent for B2 and B5 is the authors' neat/dry-state description.
- Hand-off 2 uses f=0.9 for water addition (my reading of 100 mg in 2-3 mL).
- Neutralising base in hand-off 3 is not named by the authors.

## R7 Becker 2019 (5 steps, 4 hand-offs)
- Main text and SI conflict on the one-pot aminoisoxazole T (main text 95 C; SI 25 C, 2 h). SI used.
- Y4 iron loading: SI general procedure 0.5 eq; Fig. 2C legend 0.0005 eq Fe2+. Legend value used.
- Y3 and Y4 inputs are synthetic or isolated (purified=True). The one-pot run (SI) skips isolation; not encoded as a separate route.
- Pyranoside to furanoside equilibration (borate heating) is not a numbered step; folded into notes.
- Purine arm not encoded.
- DTT is not claimed prebiotic by the authors; listed as scenario feedstock only because the headline run uses it.
- Hand-off 1 f=0.5 acid_rain at pH 6.5 is my arithmetic; the SI neutralised with concentrated HCl.

## R8 Xu 2020 (5 steps, 4 hand-offs)
- Starts at Fig. 2. alpha-anhydrouridine (15) comes from the pyrimidine arm and is an input, not produced in this table.
- Almost all concentrations, T and times are in the SI (not obtained): NaN.
- X2 "demonstrated" rests on a main-text sentence only.
- Hydrosulfide variant (N7 product persists) and ferrocyanide variant (Fig. 4 route A) not encoded.
- X5 deoxyinosine formation is concurrent with dA; encoded as one step.
- Hand-off 1 uses "remove" mode for adenine crystallisation (my reading of supernatant enrichment).

## R9 Yi 2020 (3 steps, 2 hand-offs)
- Table 1 and text differ for 2-aminooxazole (0.09 vs ~0.11 mM). Table value used.
- Dry-down step N2 is 35 C under reduced pressure. The ~10x concentration is encoded in outputs, not as a separate evaporation process.
- Hand-off pH change 7 to 8 is a manual adjustment in the NMR tube.
- N3 phosphate and NH4Cl inputs are NaN (not measured after dry-down).
- Hand-offs use same_pot although aliquots were withdrawn; no workup applied.

## R10 Ritson 2022 (5 steps, 4 hand-offs)
- C2 and C3 are labelled "unread": the aminal and ribo-aminooxazoline chemistry is from Islam 2017, which was not opened.
- C4/C5 are independent of C1 to C3 in the paper (CV-DCI captures cyanoacetylene; ribo-aminooxazoline enters as crystalline). The linear chain therefore has no real hand-off between C3 and C4; same_pot is a placeholder.
- C1 yield basis (glycolaldehyde) not stated; assumed.
- C5 solvent is formamide, which the scenario does not claim as a setting; the rule may flag it under F3 or F9.
- DCI origin rests on refs 9 and 10 (not opened).

## R11 Gibard 2018 (2 steps, 1 hand-off)
- The paper gives no geological setting; the scenario is minimal and only claims DAP as feedstock.
- G2 is the oligomerisation seen in the same paste; split from G1 to carry the headline claim.
- Nucleosides are purified=True inputs.
- Peptide, liposome and amidodiphosphate results not encoded.
- Most concentrations are in the SI (not obtained): NaN.
