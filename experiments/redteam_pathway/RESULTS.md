# Red team of the pathway map (board task #21, agent rt-21)

Target: `experiments/pathway_map` (orig-3), scored under the sealed rule v1 (`docs/prereg/compatibility_rule.md`) with `experiments/compat/scorer.py` and the wrapper `score_map.py`. The scorer, rule and wrapper were not changed.

## Verdict in one paragraph

The map survives the kill test. My blind re-encoding flips 2 of 22 hand-off verdicts (9.1%, threshold 20%), with Cohen's kappa 0.82. The probes move a further 2 hand-offs (C5→C6, C6→C7) from broken to blocked. Counting every disagreement from either source, 4/22 (18%) differ, still under the threshold. Those two moves change no route's status.

**"0/22 continuous" holds, but it is structural rather than a finding of the compatibility rule.**
- Every route contains a missing step, and 12 of the 22 hand-offs touch a missing or unread step.
- The wrapper cannot return "continuous" for any hand-off whose step has redox "unknown", and that covers all steps except C1 and V1.

**"Every hard fail is F3, F4 or F6, never pH or temperature" holds as scored, but it is weaker than stated.**
- Both F3 fails can be removed under the rule: one by choosing the dry phosphorylation method, the other because it is an artefact of a NaN pH.
- The real pH gap at C1→C2 is hidden as "unassessed". C2 needs pH ≈ 0, and nothing in the scenario can reach that.
- C3→C4 passes on pH only because of an encoding choice (pH 9) or a loophole (evaporation's free 1-unit pH shift).
- The breaks that survive every reading are all F4 (missing input), some with F6 alongside.

**Shuffle null.** For hard fails, the rule cannot tell the real cyanosulfidic order from random orders (p ≈ 0.73). It sees order only through F4, which chains species names.

## Method

1. **Blind encoding.** `steps_rt.py` was written before I read the encoded values in `steps.py`. I read only the `D` dict, the step ids and names, the helpers, `SCENARIOS` and `RAIN`; scenario choices were reused, not re-encoded.
   - sha256 `7d5c9169…1c69` is in `ENCODING_SHA.txt`, written before scoring.
   - Known errors in my own blind file are listed below and were not edited after hashing.
2. **Scoring.** `score_rt.py` runs `score_map.score_pathway` on both encodings and writes `diff.json`.
3. **Probes.** `probes.py` edits copies of the original route and writes `probes.json`.
4. **Shuffle null.** `shuffle_null.py` writes `shuffle_null.json`. It runs 200 shuffles per route (seed 21), plus all 720 orders of the six demonstrated cyanosulfidic steps.

All of it runs in under 1 CPU-second.

**Sources I opened (full text, PMC HTML):**
- Ritson 2012, 10.1038/nchem.1467: https://pmc.ncbi.nlm.nih.gov/articles/PMC3589744/
- Stairs 2017, 10.1038/ncomms15270: https://pmc.ncbi.nlm.nih.gov/articles/PMC5454461/
- Caimi 2025, 10.1021/acscentsci.5c00488: https://pmc.ncbi.nlm.nih.gov/articles/PMC12464751/
- Altair 2025, 10.1021/jacs.5c01948: https://pmc.ncbi.nlm.nih.gov/articles/PMC12356197/
- Matreux 2024, 10.1038/s41586-024-07193-7: https://pmc.ncbi.nlm.nih.gov/articles/PMC10990939/
- Gianni 2026, 10.1126/science.adt2760 (author manuscript): https://pmc.ncbi.nlm.nih.gov/articles/PMC7618777/
- Attwater 2025, 10.1038/s41557-025-01830-y: https://pmc.ncbi.nlm.nih.gov/articles/PMC12226338/
- Patel 2015, 10.1038/nchem.2202: https://pmc.ncbi.nlm.nih.gov/articles/PMC4568310/

**Powner 2009 and Simonis 2026: abstract only.** I read them through PubMed efetch (PMIDs 19444213 and 41793254).
- OpenAlex lists both as closed, with no repository full text.
- UCL Discovery shows a Cloudflare challenge, so I did not use it.
- C5, C7 and P1 therefore stay "unread". Hudson 2020 was not needed and I did not read it.

## Per hand-off

Columns:
- **Orig.** The original verdict.
- **RT blind.** The verdict from my hashed blind encoding.
- **RT rule-legal.** The most favourable verdict the rule allows, from the probes.

Verdict abbreviations: B = broken, BL = blocked_by_missing_step, U = unverified.

| Hand-off | Orig (hard) | RT blind (hard) | RT rule-legal | Reason for any difference |
|---|---|---|---|---|
| C1→C2 | B (F4) | B (F1, F4) | B (F4) | I left C1's output pH at its start value of 7, so F1 appeared (orig used NaN, so unassessed). That is my artefact, but it exposes a real gap: C2 needs pH ≈ 0 (0.5 M HSCN). The scenario's only stream is rain at pH 7, and no process can acidify. P4 shows that F1 fires as soon as C1's pH is known. F4 is robust: Ritson's products are the cyanate-trapped oxazolidinones 13/14, not free glycolaldehyde. |
| C2→C3 | B (F4) | B (F4) | B (F4) | Agree. "Rain at pH 6" is not what decides this. The rule lets the pH after rehydration be anywhere in [0, 7], and C3 works at pH 4–9. F4 (no free glyceraldehyde) decides it. The orig's `demonstrated_by` for crystallising 2-thiooxazole is generous: Stairs extracted 4b with EtOAc and crystallised it from CH2Cl2, and the "crystallises directly from water" claim cites refs 27/28 (unverified). This would only add W3. If C1 did release free sugars (P5, hypothetical), the isolate-mode separation would also strip glyceraldehyde (F5). |
| C3→C4 | U | **B (F1)** | U | **Flip.** I encoded C4 at pH 10.5, the condition behind the 45%/33% yield. The orig uses the same yield for C4's output concentrations but encodes the step at pH 9, which is internally inconsistent; orig notes this. With gas_exchange capped at +2, the pH after hand-off is 9 against 10.5 needed, so F1. A rule-legal route back to pass exists: evaporation with factor 1 shifts pH by +1 for free, then gas_exchange adds +2 (P1b). The pass therefore rests on a loophole or on picking the low end of 8.5–10.5. Also too generous: the thione crystallisation is counted as demonstrated, but Stairs crystallised diastereomers made from pure pentoses (Methods: "67% from ribose") for X-ray, not 1a out of the C3 crude. W3 is fairer (P1c). It does not change the verdict. |
| C4→C5 | BL | BL | BL | Agree (C5 unread). |
| C5→C6 | B (F3, F6) | B (F3, F6) | **BL** | Same blind. Rule-legal: Stairs Method I is a dry urea/NH4H2PO4 melt at 140 °C, inside the scenario's 0–150 °C, with no formamide. It removes F3. A claimed crystallisation of anhydrocytidine (no `demonstrated_by`, so W3) removes F6, which leaves only the unread C5 (P2a/P2b). Caveat: the Method I yield for 11 is in the SI, which I did not read. The main text says 11 suffers "significant hydrolysis" under urea-mediated phosphorylation. |
| C6→C7 | B (F3) | B (F3, F7) | **BL** | The orig's F3 comes from a NaN artefact, not a missing process. Rehydration with rain at f ≥ 0.5 legally makes the solvent water (scorer, lines 84–85), contrary to the orig's "why". It fails only because C6's output pH is NaN: the scorer then raises F7 ("pH nan not between"), and the aborted process leaves the solvent as formamide. With any known pH, the hand-off is only blocked by the unread C7 (P7b). The wrapper's stated policy is that NaN-dependent checks are never fails; here it does not apply that policy to F7. My blind F7 is the same artefact. |
| C7→C8 | B (F4, F6) | B (F4) | B (F4) | Agree on the verdict. My F6 is missing because of a naming error in my file (`cytidine_cyclic_phosphate` vs `cCMP`), which turned F6 into F4. Purines are robust: the route never makes canonical cAMP or cGMP. Stairs makes the 8-oxo-A and 8-oxo-I cyclic phosphates. Isolating cCMP by a claimed separation removes cUMP and adds F5 (P3). |
| C8→C9, C9→C10 | BL | BL | BL | Agree. |
| V1→V2 … V5→V6 | BL ×5 | BL ×5 | BL ×5 | Agree. The 1000x thermophoresis is too generous: Matreux measured at most about 2.5-fold c0 in a single chamber (18 K). The 10³–10⁴ figures come from network simulations and from ratios between species. It is moot, because V2 is missing and the verdict is identical at 2.5x and at 1000x (P6). |
| P0→P1 | B (F6) | **BL** | B (F6) | **Flip, my omission.** The Simonis abstract says the nucleotide solutions were "prepared in the laboratory", and I did not flag AMP/UMP as purified. The orig's F6 is fair. With two purified inputs the rule cannot clear F6, because isolate-mode separation keeps only one species. I accept the orig verdict. |
| P1→P2 | B (F4, F6) | B (F4, F6) | B | Agree (cGMP and cCMP are never made; cAMP and cUMP are purchased). |
| P2→P3, P3→P4 | BL | BL | BL | Agree. |
| I1→I2 | BL | BL | BL | Agree. |
| I2→I3 | B (F4, F6) | B (F4, F6) | B | Agree. The orig omits Gianni's 8 nM template t4psP10QT45 as an input; I omitted the hexamer. Either omission would add another F4. |
| I3→I4 | B (F4, F6) | B (F4, F6) | B | Agree. The TPR ribozyme, primers and template are not produced by I3. |
| I4→I5 | BL | BL | BL | Agree. |

**Agreement statistics:**
- Blind vs orig: 2/22 flips (C3→C4, P0→P1), flip fraction 0.091, kappa 0.822. The set of hard-fail codes differs on 5 hand-offs.
- Rule-legal vs orig: 2/22 flips (C5→C6, C6→C7), kappa 0.825.
- Either source vs orig: 4/22 = 0.18. **Below the 20% kill threshold.**

On adjudication, both blind flips are weak:
- P0→P1 was my error.
- C3→C4 turns on which pH within the source's 8.5–10.5 range one encodes.

The rule-legal flips are the substantive findings. They are harsh calls that the rule as written does not require.

## Checks of the encoded numbers against the sources

These orig values match what I read:
- **Stairs (C2–C6):** 0.1 M glycolaldehyde and 0.5 M HSCN (85%); 0.25 M 4b, 0.5–1 M glyceraldehyde, 60 °C, pD 7 (74%); 0.24 M 1a, 0.25 M cyanoacetylene, 1 M NH4Cl (15–23%, or 45%/33% over two cycles at pH 10.5); Method V at 0.05 M, phosphate 0.1 M, urea 1 M, 100 °C, 72 h (44%, measured with 17A present).
- **Caimi (C8/P2):** BioLog sodium salts, 50 mM, KOH, 23 °C, Y = 36% AUGC at pH 11.
- **Altair (V1):** Table 2 entry 3, 735.9 µM formate and 11.15 µM acetate.
- **Gianni (I3):** 8 nM primer and template, 80 nM QT45, 50 nM each triplet, 0.4 mM MgCl2, CHES pH 9, −7 °C, 72 days, 0.24% and 0.17%.
- **Attwater (I4):** 20 nM TPR, 100 nM triplets and primers, HCl to pH ~3.6, 80 °C 2 min, KOH, flash-freeze, −7 °C.

**Discrepancies I found:**
- C4's pH is encoded at 9 while its outputs use the pH-10.5 yields; orig discloses this.
- Two `demonstrated_by` citations are generous (2-thiooxazole and thione_1a crystallisation; see above).
- I3 omits the template input.
- In I4's yield text, "1.46-fold" and "1.26-fold" are numbers I did not locate in the text I extracted (unverified by me, not shown wrong). I found 1.2 and 1.38 for the +14-nt duplex.

## The wrapper (score_map.py) and the NaN/"unknown" handling

1. **F7 from NaN is not treated as unassessed.** Mixing and rehydration compute the new pH from a NaN state pH, and `_between` then fails, so the scorer raises F7. The failed process also leaves the state unchanged, which cascades into F3. Consequence: no fluid can be added after any step whose output pH is unreported. That is too harsh, and it contradicts the wrapper docstring ("never adds a fail…"). It is what makes C6→C7 broken. The reverse also happens: NaN pH shifts inside evaporation and gas_exchange pass silently (`abs(nan) > x` is False) and are not listed as unassessed.
2. **F8 is effectively switched off.** Every step except C1 and V1 has redox "unknown". As a result, every hand-off that is neither broken nor blocked can only be "unverified", and "continuous" is unreachable for the pond, ice and almost all cyanosulfidic hand-offs. The 0/22 headline is therefore guaranteed by construction (plus missing steps), not tested.
3. **The `unassess` entries on P1→P2 are only appended.** The comment says they suppress F4, but no code does so. It is harmless today (no F4 is raised for cAMP/cUMP there), but misleading.
4. **"broken" overrides "blocked".** F6 flags taken from an abstract-only step (P1) make P0→P1 "broken". Defensible, but it counts a gap that the missing step P0 already explains.
5. **Not wrapper bugs, but they shape the verdicts:**
   - In the scorer, F4 masks F5 and F6 for the same input (`continue`).
   - A bare claimed `selective_separation` clears F6 with only W3, but isolate mode keeps a single species. So F6 can be cleared for one purified input and never for two or more. Whether F6 survives depends on the number of purified inputs, not on the chemistry.
   - Evaporation with factor 1 allows a free 1-unit pH shift.

## Shuffle null (Fable's test)

The test permutes step order within each route of the **original** encoding. Results:

| Route | Hand-off policy | Hard-fail hand-offs: real | Null mean [min, max] | p(null ≤ real) | F4 hand-offs: real / null mean / p |
|---|---|---|---|---|---|
| cyanosulfidic | A: all same_pot | 7 | 6.89 [4, 9] | 0.72 | 3 / 5.07 / 0.04 |
| cyanosulfidic | B: orig lists by position | 5 | 7.30 [5, 9] | 0.04 | 3 / 5.07 / 0.04 |
| cyanosulfidic | C: transport/dry/heat menu | 7 | 6.78 [4, 9] | 0.75 | 3 / 5.07 / 0.04 |
| alkaline_vent | A / B / C | 1 / 0 / 0 | 3.02 / 2.98 / 1.61 | 0.01 / 0.00 / 0.05 | 0 / 1.61 / 0.05 |
| warm_pond | A = B = C | 2 | 3.06 [2, 4] | 0.135 | 1 / 2.53 / 0.05 |
| ice_rna | A = B = C | 2 | 3.21 [2, 4] | 0.165 | 2 / 3.21 / 0.165 |
| cyanosulfidic, 6 demonstrated steps, all 719 other orders | C | 5 of 5 | 4.83 [4, 5] | 1.00 | 4 / 3.67 / 0.92 |

**What the rule cannot see.** On total hard fails, it does not score shuffled routes worse than the real one where it matters:
- For cyanosulfidic under neutral process lists, the real order is at the null mean.
- Among the six steps that have yields, every order, including the real one, breaks 4–5 of 5 hand-offs. The rule is saturated.

**Where order does show up:**
- The real order looks better only under B, with process lists that orig-3 wrote for that order. That measures how well the lists were fitted, not what the rule can detect.
- The rule sees order only through F4, because inputs must be produced upstream. That works for the vent and pond routes mostly because invented placeholder names for missing steps (`C2_C3_sugars` …) chain together.
- Its pH, temperature and solvent checks carry no ordering signal on these data.

## Headline verdict

- **0/22 continuous:** holds in the orig encoding, my blind encoding and every probe. It is structural: every route has missing steps, and the wrapper cannot return "continuous" when redox is unknown. Report it as "no route is complete", not as a result of the compatibility test.
- **Hard fails are only F3, F4 and F6, never pH or temperature:**
  - **As scored, true.**
  - **Robustly, only F4 (with F6) survives.** C1→C2, C2→C3, C7→C8, P1→P2, I2→I3 and I3→I4 break on a missing input under every reading.
  - **Both F3s are removable.** C5→C6 via Method I. C6→C7's F3 is a NaN artefact; its rule-legal verdict is blocked.
  - **"Never pH" needs a caveat.** C1→C2 has a real, unfixable pH gap (pH 7 → ≈0) that NaN hides. C3→C4 passes pH only at the low end of the source's range or through the evaporation loophole.
  - **Temperature never fails in any encoding.** That is expected, because heating and cooling to any in-range temperature is free under the rule.
- **Kill threshold not met (18% at most < 20%).** The map stands, with the C5→C6 and C6→C7 verdicts and the F3 and pH wording corrected.

## Files

- `steps_rt.py`: blind encoding, hashed in `ENCODING_SHA.txt`. Known self-errors (not edited after hashing):
  - the `cytidine_cyclic_phosphate`/`cCMP` name mismatch;
  - no purified flag on P1;
  - C1's output pH left at 7;
  - a dead `gas_exchange` placeholder on C7→C8, replaced in code by `same_pot`.
- `score_rt.py` → `diff.json`; `probes.py` → `probes.json`; `shuffle_null.py` → `shuffle_null.json`.
