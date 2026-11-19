# Red team of the DSM route score (task #27, agent rt-27)

**Bottom line.** The original score (task #26, `experiments/dsm_route`) survives. My blind re-encoding agrees on 4 of 5 main-route hand-off verdicts. The one disagreement (D1→D2) moves between two "not continuous" classes, and on review I side with the original. So the considered flip fraction is **0/6 (0%)**. The raw blind disagreement is **1/5 (20%)**, which sits exactly on the kill threshold. Cohen's kappa on the 4-class verdicts is **0.58** for the 5 hand-offs, or **0.70** with the entry row included.

Three of the original's claims are weaker than `RESULTS.md` makes them sound:

- **H1 is close to vacuous.** It cannot show that rule v1 is not too strict.
- **H5 is too generous.** The break is real, but under the source actually read it is F4 (ribose is never made), not F6.
- **The headline "none is a pH or temperature mismatch" is uninformative for this route.** pH could not be assessed on any of the five DSM hand-offs.

## Order of work

1. I read only the allowed files: `pathway_map/steps.py`, `score_map.py`, `compatibility_rule.md` and `compat/scorer.py`.
2. I read the sources.
   - Full text of Hirakawa 2025, from the PMC12745811 XML, plus its SI Appendix PDF from the Europe PMC supplementaryFiles zip.
   - Full text of Kawai 2019 (PMC6459274, doi:10.1089/ast.2017.1800).
   - Full text of Jerome 2022 (PMC9233534, doi:10.1089/ast.2022.0027, via NCBI efetch; Europe PMC returned HTTP 500).
   - Abstracts only of Kim 2011 (doi:10.1021/ja201769f) and Kim & Benner 2021 (doi:10.1089/ast.2020.2264). Europe PMC lists both as "Subscription required", and I found no legal open full text.
3. I wrote `steps_rt.py` and wrote its sha256 to `ENCODING_SHA.txt` (`e2182a1f…`). Only then did I open `experiments/dsm_route/*` and `docs/prereg/dsm_route_score.md`.
4. I scored with `score_rt.py`.
   - It uses the scorer and wrapper unchanged, called as `score_dsm.py` calls them.
   - The planted controls passed 28/28, run in memory, because `planted.py` rewrites files in `experiments/compat`.
   - Each encoding was scored twice: A is the sealed scorer, B adds score_dsm's NaN patch.
   - Outputs: `results.json` and `handoffs_rt.csv`.

## Hand-off diff (main route; run B, i.e. with the NaN patch)

| Hand-off | Original | Red team (blind) | Same class? | Comment |
|---|---|---|---|---|
| entry→D1 | unverified | unverified | yes | |
| D1→D2 | blocked (D2 unread, Kim 2011) | broken (F4: DHA) | **no** | I encoded D2 from Kawai 2019, the only full text: HMS + dihydroxyacetone (DHA) at pH 10.5 and 65 °C gives "mainly erythro- and threo-branched pentoses". Hirakawa's Step 1 supplies only HCHO and glycolaldehyde, so DHA is F4. On review this F4 is a technicality: Hirakawa's real step 2 (Kim 2011) starts from HCHO + glycolaldehyde, and the abstract allows "1 to 3 carbons". I accept the original's verdict. |
| D2→D3 | broken (F6 ribose) | broken (**F4** ribose) | yes | The original lists ribose as a D2 output on the authors' claim. No source read reports ribose: Kawai reports branched pentoses, and Hirakawa's Discussion needs a Bilik or retro-aldol step (refs 82-84, not opened) to get linear pentoses. Read strictly, ribose is never made (F4). F6 arises only once ribose is granted. |
| D3→D4 | unverified (W1 phosphate) | unverified (W1 phosphate) | yes | Same verdict, but see Q4. |
| D4→D5 | broken (F4 adenosine) | broken (F4 adenosine) | yes | |
| D5→D6 | broken (F6 NTPs) | broken (F6 ATP) | yes | The original's D5 outputs all four NTPs although its only nucleoside input is adenosine. That is generous, but it changes no verdict. |
| dsm_b D4→P2 | broken (F4 cG/cU/cC, F6 cAMP) | not encoded | n/a | I reviewed it: it stands. |

Agreement statistics:

| Measure | Value |
|---|---|
| 4-class verdicts, 5 hand-offs | p_o 0.80, p_e 0.52, κ = 0.58 |
| Same, with the entry row | p_o 0.83, κ = 0.70 |
| Binary "hard fail?" | κ = 0.55 |
| Exact hard-fail code sets | 3/5 agree |
| After my review concession on D1→D2 | 5/5, κ = 1.0 |

With n = 5, these kappas are very imprecise.

## The four questions

**1. Is free adenosine reported after the 90 °C dry-down?** No.

- The main text (Results 1.5) assigns only adenosine 2',3'-cyclic phosphate and adenosine 2'-phosphate.
- The Fig. 4 legend says the ~17 min peak "includes adenosine monophosphates".
- SI Figs S7-S10 show only the LC-MS/MS transitions m/z 330>136 (cyclic) and 348>85 (2'-AMP).
- SI Figs S12-S13 start from adenosine 2'-phosphate, not from the one-pot mixture.
- No adenosine transition is shown. Adenosine [M+H]+ would be m/z 268; that is my arithmetic, not a number from the paper.

So free adenosine was not reported, and as far as the paper shows it was not looked for. That is absence of evidence, not evidence of absence. The D4→D5 F4 (H3) stands.

**2. Do Kim 2011 or Kim & Benner 2021 show ribose separation, or a nucleotide input?** Only the abstracts are legally open.

- **Kim 2011:** pent(ul)oses "including the ribose found in RNA" from HCHO + glycolaldehyde, with borate, molybdate and calcium minerals. It mentions no separation or isolation of ribose. Over time, material passes to a branched heptulose.
- **Kim & Benner 2021:** "nucleoside 5'-triphosphates upon evaporative heating", at 2-3% NTP and ~30% total 5'-phosphorylation. The text says "paths are already available to make nucleosides", so the input is the nucleoside, not a nucleotide.

Neither abstract removes a fail. Hirakawa's Discussion says urea + borate move phosphate to the 5' position, with no data and no citation. That would give 5'-AMP, which is still not a nucleoside.

**3. Were the two post-run fixes fair?**

- **NaN range check: fair as applied, but not safe in general.**
  - I confirmed it changes none of the 22 task #5 hand-offs.
  - On the original encoding, the predicted F4/F6 codes appear with or without the patch. The patch removes only F7 "pH nan not between nan and 7.0" and the knock-on F3.
  - The flaw: if a hand-off sets an explicit `ph_after` (or `t_after`) while the old value is NaN, the patch lets an unknown pH become a known one, and F1 then counts as *assessed and passing*. My own D5→D6 shows this: F1 disappears from the unassessed list under the patch.
  - The original never sets `ph_after` after a NaN, so its numbers are unaffected. A future use should force the result to NaN whenever a range bound is NaN.
- **cAMP rename: fair.** In this repo, `cAMP` is the 2',3'-cyclic isomer (Caimi; `pathway_map` P1 note), and Hirakawa's D4 product is adenosine 2',3'-cyclic phosphate. The rename only turned a false F4 into the correct F6. D4→P2 stays broken through F4 on cGMP, cUMP and cCMP either way.

**4. Is D3→D4 a fair specificity check?** It is not a meaningful one.

- **The checks that could fail it are not really applied:**
  - F1 and F8 are unassessed, because D4's pH and redox are not reported.
  - In the original, F5 is circular: D4's RCP input is set to D3's 52.9 mM, so the ratio is 1 by construction. In mine it is unassessed, because RCP in the one-pot was never measured.
- **The checks that remain are settled by the encoder's own choices:** F2, F3, F4, F6 and F9 depend on the hand-off and on the purified flag.
- **The two runs are different experiments.** D3 ran in 800 mM phosphate buffer. The one-pot had no buffer and only 100 mM borax, and its RCP was not quantified (SI Fig. S11).

A hand-off the source ran in one pot can hardly fail. It therefore says almost nothing about whether rule v1 is too strict on real chemistry. The original's "supports reading 0/22 as real gaps" overstates what it shows; its own caveat ("weak check") is the right reading.

## Verdicts on H1-H6

| # | Claim | Verdict |
|---|---|---|
| H1 | D3→D4 has no hard fail; so the rule is not too strict | **Weakened.** The fact reproduces. The inference does not follow (Q4). |
| H2 | Main route not continuous | **Stands.** Same in my encoding: D5 is unread and 4 hand-offs are broken. |
| H3 | F4 adenosine at D4→D5 | **Stands.** Free adenosine is not reported (Q1). |
| H4 | F6 on NTPs at D5→D6 | **Stands.** |
| H5 | F6 ribose at D2→D3 | **Stands as a break, weakened as stated.** Under the read source it is F4: no ribose is produced, only branched pentoses. F6 depends on granting the authors' unread claim. |
| H6 | F4 cG/cU/cC at D4→P2 | **Stands** (reviewed, not re-encoded). |

## Other problems found

- **pH was never tested.** F1 is unassessed on all 5 original DSM hand-offs. The map-level line "none is a pH or temperature mismatch" therefore carries no information for this route.
- **A pH gap is hidden behind "unread".** In Kawai's model of step 2, the pot is pH 10.5 in 1.1 M carbonate, while D3 needs pH 7. Gas exchange (±2 units) gives F1. The rule's mixing process lets rain set pH 7.0 anywhere between the two values, which a 1.1 M carbonate buffer would not allow chemically. The original hides this gap by treating D2 as unread.
- **DAP-as-feedstock hides a gap.** Hirakawa's Discussion says adenylates were obtained "directly from ribose–borate, adenosine, ammonia, and cyclic triphosphate". However:
  - the one-pot used lab-synthesised DAP;
  - the CTMP + NH3 run reached only "small peaks" of RCP (not quantified);
  - that run was never carried on to adenine.

  Both encodings grant DAP. If it were not granted, D2→D3 would also carry F4 for DAP, which is already a broken hand-off.
- **D4 is labelled "demonstrated" on unquantified products.** Both encodings do this. The ~17% figure is from pure RCP (refs 21-22, not opened).

## Sources opened

- doi:10.1073/pnas.2516418122 (Europe PMC PMC12745811 full-text XML; SI `pnas.2516418122.sapp.pdf` via Europe PMC supplementaryFiles)
- doi:10.1089/ast.2017.1800 (PMC6459274 full-text XML)
- doi:10.1089/ast.2022.0027 (PMC9233534, NCBI efetch XML)
- doi:10.1021/ja201769f and doi:10.1089/ast.2020.2264 (Europe PMC abstracts only)

Cited through Hirakawa and not opened (unverified): Kim & Benner 2017, Kim & Kim 2019, refs 82-84, Verlander 1973.

Rerun: `.venv/bin/python -I experiments/redteam_dsm/score_rt.py`
