# The borate DSM route breaks at three hand-offs its authors call compatible; the rule passes the one hand-off they ran in one pot

**Verdict.** Hirakawa et al. 2025 (PNAS, doi:10.1073/pnas.2516418122) claim that every step of the six-step borate "Discontinuous Synthesis Model" (DSM) is compatible with the others. I scored their route under our sealed rule v1, which was written before any route was encoded. Every pre-registered prediction held.

- **The rule is not too strict on the one hand-off that was really run without intervention (H1, confirmed).**
  - D3→D4 is RCP formation, then glycosylation of adenine, dried at 90 °C in the same pot. It gets no hard fail.
  - It gets one warning: our D3 numbers come from a run in 800 mM phosphate buffer, and the one-pot run had no buffer.
  - This is the first check of rule v1 on a sequence a lab actually performed in one pot. It supports reading our 0/22 result for the other four routes as real gaps rather than an over-strict rule.
  - It is a weak check: one hand-off, and the RCP concentration in the one-pot is taken from the buffered run.
- **The route is not continuous (H2).** Two of its six steps (D2 sugars, D5 triphosphates) are paywalled. Under our convention, unread steps count as missing.
- **Three hand-offs break even with both sides read or given the authors' claims:**
  - **D2→D3, F6 (H5).** The ribose step used commercial D-ribose. The sugar step is reported, in the source we read (Kawai 2019), to give "mainly erythro- and threo-branched pentoses". No demonstrated process pulls ribose out of that mixture. For the score, we granted that ribose is made at all, which is the authors' claim.
  - **D4→D5, F4 (H3): the nucleotide/nucleoside mismatch.** The one-pot glycosylation makes adenosine 2'-phosphate and 2',3'-cyclic phosphate. The triphosphate step starts from free nucleosides. No step in the route makes free adenosine.
    - The authors' answer is that urea with borate moves phosphate to the 5' position. That gives 5'-AMP, still not a nucleoside, and they cite no experiment for it.
    - This break is not about borate, which was the only interference the paper tested.
  - **D5→D6, F6 (H4).** The basalt-glass polymerisation used commercial NTPs at 3 µM each. The triphosphate step yields 2-3% NTPs in a dried mixture with NDPs, NMPs, urea, Ni²⁺, CTMP and borate. No demonstrated separation connects the two.
- **The authors' shortcut branch also breaks (H6).** Their alternative goes through 2',3'-cyclic nucleotides "to 6-mer RNA". With Caimi 2025 as the polymerisation step, it fails at D4→P2:
  - F4: only adenine was run in the one-pot, so there are no cyclic G, C or U nucleotides;
  - F6: Caimi used commercial cyclic nucleotides.

**What this adds to the map.** With five routes, 0 of 27 hand-offs are continuous. Two pass without a hard fail, but some of their checks cannot be assessed:
- cyanosulfidic C3→C4, within Stairs 2017;
- DSM D3→D4, the one-pot.

Both are within a single paper. Across the five routes, every hard fail is one of three kinds:
- F4: an input nobody makes in the scenario;
- F6: an input used in purified form;
- F3: a solvent change (formamide in the cyanosulfidic route).

None is a pH or temperature mismatch. The field's compatibility tests check whether one reagent interferes with another step (here: does borate inhibit steps 3 and 6?). The breaks we find are a different kind of gap: **what one step outputs is not what the next step was tested with.**

## Pre-registration and order of work

- Prereg: `docs/prereg/dsm_route_score.md`, sha256 `30dcc280…`, appended to `HASHES.txt` at 2026-11-18T21:18Z. Every prediction was written before encoding.
- Encoding: `steps_dsm.py` was hashed (`b4cb7fff…`) and posted as a board note before the scorer was first run on it.
- Planted controls: 28/28 passed immediately before scoring (sensitivity 1, specificity 1).
- Scorer: `experiments/compat/scorer.py`, unchanged; rule sha256 `bfa572ed…`.

### Two changes after the first run (both disclosed; both can only remove fails)

1. **NaN range check.** When a residue's pH was never reported (NaN), the scorer's rehydration check "new pH lies between old pH and rain pH" raised **F7**. The failed process then left the solvent "dry", which caused a knock-on **F3**.
   - In the task #5 wrapper's terms, this is an unreported number and should be "unassessed". So `score_dsm.py` lets a range check with a NaN bound pass, and the hand-off stays "unassessed" for pH.
   - Checked: this leaves all 22 hand-offs of the four task #5 routes exactly unchanged.
   - First-run effect: spurious F7 on D4→D5, D5→D6 and D4→P2, plus F3 on D4→P2. All are removed.
2. **Name mismatch.** I named D4's product `cAMP_23`, while the Caimi step calls the same molecule (adenosine 2',3'-cyclic phosphate) `cAMP`. That raised a false F4. After renaming, F6 remains, because Caimi bought it.

The predicted fails (F6 at D2→D3, F4 at D4→D5, F6 at D5→D6, F4 for cGMP, cUMP and cCMP on D4→P2) were present in the first run as well, so neither change created them.

### Further deviation

The Caimi step (P2) was relabelled from `surface_pool` to `aquifer`, so that it sits inside the DSM scenario. This favours the route; otherwise F9 would fire.

## Hand-offs

| Route | Hand-off | Verdict | Hard fails | Why |
|---|---|---|---|---|
| dsm | entry→D1 | unverified | none | feedstock concentrations unstated |
| dsm | D1→D2 | blocked | none | D2 unread (Kim 2011 paywalled) |
| dsm | D2→D3 | **broken** | F6 ribose | commercial ribose; products "mainly branched pentoses" (Kawai 2019) |
| dsm | D3→D4 | unverified (passes) | none | one pot in the source; W1 phosphate buffer |
| dsm | D4→D5 | **broken** | F4 adenosine | D4 makes 2'-/2',3'-cyclic AMP, D5 needs nucleosides |
| dsm | D5→D6 | **broken** | F6 ATP/UTP/GTP/CTP | commercial NTPs at 3 µM; D5 gives 2-3% NTP in a salt mixture |
| dsm_b | D4→P2 | **broken** | F4 cUMP/cGMP/cCMP; F6 cAMP | adenine-only one-pot; Caimi used commercial cyclic nucleotides |

Full flags and unassessed checks: `results.json`, `handoffs.csv`.

## Sources (DOIs opened)

- Hirakawa et al. 2025, PNAS 122:e2516418122, doi:10.1073/pnas.2516418122. Full text read (Europe PMC PMC12745811).
- Kawai et al. 2019, Astrobiology 19:506, doi:10.1089/ast.2017.1800. Full text read (PMC6459274).
- Jerome et al. 2022, Astrobiology 22:629, doi:10.1089/ast.2022.0027. Full text read (PMC9233534).
- Kim et al. 2011, JACS, doi:10.1021/ja201769f. Abstract only.
- Kim and Benner 2021, Astrobiology 21:298, doi:10.1089/ast.2020.2264. Abstract only.
- Caimi 2025 (doi:10.1021/acscentsci.5c00488), via the task #4 encoding.
- Cited through Hirakawa, not opened: Kim and Benner 2017 (doi:10.1073/pnas.1710778114), Verlander et al. 1973, Gibard et al. 2019.

Raw full texts were kept in `/tmp` only, not in the repo.

## Not checked, and how this could be wrong

- **D2 and D5 are paywalled.** Their full texts could show a ribose separation, or a nucleotide input to the triphosphate step. Either would remove a fail. Reading them (legally, or by asking the authors) is the most direct test.
- **Free adenosine might form during the 90 °C dry-down.** It is not reported in Fig. 4. One faster peak "includes adenosine monophosphates". If it is present, the D4→D5 F4 falls. That is a concrete question for the authors.
- **The single real one-pot hand-off is a weak specificity check.** A stronger one needs more published multi-step one-pot sequences, for example Becker et al. 2018/2019 wet-dry nucleoside syntheses (not yet read).
- **Generous choices may hide gaps.**
  - DAP, nucleobases, NH3 and urea are counted as feedstocks because the authors claim them.
  - Ribose is counted as produced.
  - Rain is assumed to be pH 7.
- **Rule v1 does not score** yields, kinetics, chirality or borate supply.
- **Independence.** The person who encoded the route also wrote the predictions. An independent re-encode (M6) is needed before this goes on the site as a finding.

## Hypotheses

| # | Prediction | Result |
|---|---|---|
| H1 | D3→D4 (one pot in the source) has no hard fail | confirmed |
| H2 | DSM main route not continuous | confirmed (2 unread steps, 3 hard-fail hand-offs) |
| H3 | F4 adenosine at D4→D5 | confirmed |
| H4 | F6 on NTPs at D5→D6 | confirmed |
| H5 | F6 ribose at D2→D3 | confirmed |
| H6 | F4 cGMP/cUMP/cCMP on D4→P2 | confirmed (plus F6 cAMP) |

Rerun (under 1 s): `.venv/bin/python -I experiments/dsm_route/score_dsm.py`
