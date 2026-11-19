# enc-A encoding notes (task #29, R6–R11)

Nothing here is scored. All six routes were encoded from legal open copies; none is marked unread.

## General
- Every `f=0.5` in a rehydration hand-off is a placeholder; no source gives a natural mixing fraction. Rain at pH 7 and 23 °C is assumed, following steps.py.
- "Room temperature" is recorded as 23 °C. This is stated as an assumption on each step that uses it.
- Concentrations marked "our arithmetic" were computed from the stated amounts and volumes.
- Several lab reagents stand in for natural processes the authors claim. They are encoded as the authors used them:
  - conc. HCl (R7 P2, R8 pH adjustments)
  - Et3N (R6 B6)
  - K2CO3 (R6 and R7 workups)
  - DTT (R7 P5)
- pH adjustments with unnamed acid or base (R8 X2–X4, R9 Y3) have no matching process in the closed list. They are described only in `why`.
- Supplements that were not opened:
  - R9: PMC SI download behind a bot challenge.
  - R10: PMC challenge and ACS 403.
  - R10 T1 therefore has NaN concentrations, temperature and yield.
- Some selective_separation entries are precipitation of metal hydroxides or carbonates (Ni2+ in R6, Zn2+ in R7). They are encoded with property "crystallisation", the nearest item on the closed list.

## R6 Becker 2018
- Only the adenosine branch (4b → 5b → 5c → A) is encoded. The G-family branches are not.
- Each intermediate after B1 was isolated by crystallisation or washing, so those inputs are `purified=True`.
- The authors present the following as natural enrichment steps (I–III):
  - the salt crystallisation
  - the water wash of 4b
  - the FaPy crystallisation after K2CO3 treatment
- The "<1/10 volume" concentration in the FaPy workup is not encoded as an evaporation factor.
- 20% HCOOH: units (v/v or w/w) not stated. pH not stated.
- Adenosine yield is given only as the 15–60% range across all N9 nucleosides.
- Proposed N3 regioisomers appear only with continuous-route FaPys.

## R7 Becker 2019
- Legal copy: the LMU accepted manuscript plus SI.
- Hydroxylurea (P1) was bought commercially. The authors list NH2OH or its disulfonate as the feedstock and do not list hydroxylurea.
- Two alternatives are noted but not encoded:
  - NH2OH gave a 17% yield.
  - NO2−/SO2 → disulfonate gave 63% over two steps.
- The 55% crystallisation of 8 was shown on a batch made from commercial 4 at 5× scale. It was not shown on the one-pot P2 product.
- P5 started from a 3:1 α/β furanoside mixture. This matches the synthetic reference, so P4 output was not carried into P5 (our inference). No furanoside separation was shown.
- Argon degassing in P5 has no process in the list.
- Ribose is a feedstock because the authors "need to assume" it is supplied.
- The purine one-pot (Fig. 5A) is not encoded.

## R8 Xu 2020
- X2 started from weighed 12 and cytidine, not from the X1 mixture. Hand-off 1 states this.
- 8-Mercaptoadenine 16 was supplied. Its synthesis is the separate branch R8b, which was not run in sequence.
- The SI writes "Na2SO4" in the photoreduction step. The main text says bisulfite, so it is encoded as bisulfite.
- X3 temperature and step yield are not reported. Yields on isolated 18 are given in `yield_text`.
- X4 temperature is not stated and is recorded as RT (assumption).
- Route B (via 15 and H2S) is not encoded.
- R8b: buffer volume not stated. The yield from the hydrolysate is qualitative (confirmed by spiking).

## R9 Yi 2020
- The authors say this is not a specific geological scenario. Feedstocks are their initial mixture.
- N2 atmosphere is recorded as "reducing" under the anoxic convention.
- 24 °C is taken from the "~24 °C" in the Fig. 2A legend.
- The pH adjustment to 8 before Y3 has no named reagent.
- The 450 µL + 50 µL D2O dilution is not encoded.

## R10 Ritson 2022
- Main text only. The T1 numbers are in the SI, which was not opened.
- Ribo-aminooxazoline is an input from earlier work. Its crystallisation is cited, not shown, so no separation is encoded for it.
- Not encoded, recorded here only:
  - The 2-aminothiazole synthesis: glycolaldehyde 25 mM + NaSH 100 mM + NH2CN 75 mM in 200 mM bicarbonate, pH 9.2, 60 °C. Yield 26% at 3 d, 30% at 7 d, 32–40% at 10–25 d.
  - The cited aminal sugar separations (Islam et al., not opened).
- The UV wavelength for the post-irradiation yield boost is not in the main text.

## R11 Gibard 2018
- Legal copy: the NIH author manuscript (PMC6295206) plus the Springer SI.
- The route is one step with no hand-offs.
- Paste concentrations cannot be defined.
- The pH 8.5–9.5 reading was taken on dissolution for NMR and is not the reaction pH.
- DAP was made in the lab but is a scenario feedstock as the authors claim.
- Uridine and imidazole were bought (`purified=True`). The authors do not address where they come from.
- The solution variant (Method B) and the A/C/G results are given in the notes field only.
