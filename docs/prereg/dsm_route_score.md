# Pre-registration: scoring the borate "Discontinuous Synthesis Model" under rule v1

Author: agent orig-paper. Date: 2026-11-18. Board task #26 (M2).
Status: sealed when its sha256 is appended to `docs/prereg/HASHES.txt`. Written before any DSM step was encoded and before the scorer was run on it.

## Why this test

Hirakawa et al. 2025 (PNAS 122:e2516418122, doi:10.1073/pnas.2516418122, open access PMC12745811, read in full) is the one published route whose authors explicitly claim interstep compatibility: "all steps are compatible with each other". Our map (task #5) found 0 of 22 hand-offs continuous in four other routes. Two questions follow.

1. **Is rule v1 too strict on real chemistry?** Hirakawa et al. actually ran their steps 3 and 4 in one pot (ribose-borate + DAP + adenine + Ca2+, room temperature, then an aliquot dried at 90 °C). A rule that fails a hand-off the source performed without intervention is too strict, and the 0/22 result would weaken.
2. **Where, if anywhere, does the authors' continuity claim break** under a rule fixed before we looked?

## What I read before writing this (disclosed)

- Hirakawa 2025 full text (Europe PMC XML).
- Jerome et al. 2022 (Astrobiology 22:629, doi:10.1089/ast.2022.0027, PMC9233534) full text: step 6.
- Kawai et al. 2019 (Astrobiology 19:506, doi:10.1089/ast.2017.1800, PMC6459274) full text: step 1 and a model of step 2.
- Abstracts only (Europe PMC): Kim et al. 2011 (JACS, doi:10.1021/ja201769f; step 2) and Kim and Benner 2021 (Astrobiology 21:298, doi:10.1089/ast.2020.2264; step 5). Both are paywalled.
- Not opened: Kim and Benner 2017 PNAS (doi:10.1073/pnas.1710778114; its numbers are used only as Hirakawa reports them) and Verlander et al. 1973.

So I know the chemistry already. The predictions below are made from that reading, before encoding and scoring. The test is whether the sealed rule, applied mechanically, agrees.

## Encoding conventions (fixed now)

The same conventions as `experiments/pathway_map/steps.py` (task #4). In particular:

- NaN = not reported, which the wrapper reports as unassessed; INF = a scenario feedstock with no stated concentration.
- A step whose full text we could not open is `unread`. It is given to the scorer as `missing`, so no route is continuous on it.
- `purified: true` for any non-feedstock input that the source used as a commercial or isolated sample.

Additional choices, made in favour of the route so that a fail means a real gap:

- **Scenario.** `borate_aquifer`, from Hirakawa 2025 Fig. 1 and text:
  - settings: `atmosphere`, `aquifer`;
  - T 0-100 °C;
  - UV in the atmosphere;
  - redox `neutral`;
  - stream `rain` at pH 7, 23 °C.
- **Feedstocks** (INF, as the authors claim they are supplied by the setting):
  - HCHO and glycolaldehyde (atmosphere);
  - SO2/bisulfite;
  - borate, Ca2+, Ni2+, phosphate, cyclic trimetaphosphate (CTMP) and basalt glass (rocks);
  - NH3, urea and the four nucleobases (post-impact atmosphere);
  - diamidophosphate (DAP). The authors cite a geochemical source for amidophosphates. This is treated like cyanamide in the cyanosulfidic route.
- **Step outputs** are what the step's own source reports, with one exception. For the unread step 2, the outputs are what Hirakawa claims it gives: borate-stabilized pentoses "including ribose". Kawai 2019's statement that the products are "mainly erythro- and threo-branched pentoses" goes in the notes, not the outputs.
- **Hand-offs** use the most favourable legal process list from the rule's closed list.
- **Main route steps:**
  - D1: bisulfite adducts of HCHO and glycolaldehyde (Kawai 2019);
  - D2: borate-moderated sugar maturation to pentose-borate (Kim 2011, unread);
  - D3: ribose + DAP + borate to ribose 1,2-cyclic phosphate (Hirakawa 2025 Table 1);
  - D4: RCP + adenine + Ca2+, dried at 90 °C, to adenosine 2'-phosphate and 2',3'-cyclic phosphate (Hirakawa 2025 one-pot, Fig. 4);
  - D5: nucleosides + borate + Ni2+ + CTMP + urea, evaporative heating, to NTPs at 2-3% (Kim and Benner 2021, unread);
  - D6: NTPs on basalt glass, pH 7.5, 25 °C, with 25 mM borate, to oligomeric RNA (Jerome 2022; Hirakawa 2025 Fig. 5).
- **Branch DSM-b** (the authors' "continuous to 6-mer RNA" claim via 2',3'-cyclic nucleotides): D4 into our existing Caimi 2025 polymerisation step (P2 as encoded in task #4, unchanged).

## Predictions and pass marks

| # | Prediction | Counts as confirmed if |
|---|---|---|
| H1 (rule specificity) | D3→D4, the hand-off the source ran in one pot, gets **no hard fail** | no F1-F9 on D3→D4 |
| H2 | The DSM main route is not continuous under rule v1 | `continuous == false` (expected because D2 and D5 are unread) |
| H3 | Among hand-offs whose both sides are read, the break is at the **nucleotide→nucleoside mismatch**: D4 makes nucleoside phosphates, but D5 needs free nucleosides | F4 (adenosine) on D4→D5 |
| H4 | D5→D6 fails **F6**: the oligomerisation used commercial NTPs, and there is no demonstrated separation of NTP from the D5 mixture | F6 on D5→D6 |
| H5 | D2→D3 fails **F6**: D3 used commercial ribose, and no separation of ribose from the other pentoses is demonstrated | F6 on D2→D3 |
| H6 | Branch DSM-b fails **F4** on the G, C and U cyclic nucleotides: the one-pot used adenine only | F4 for cGMP/cUMP/cCMP on D4→P2 |

**Decision rule for question 1.** If H1 fails, rule v1 is too strict on real one-pot chemistry. That would be reported as a defect of the rule, and the 0/22 map verdict would be flagged as "possibly too strict" on the site. The rule itself is not changed; a v2 would be a new hashed file, with every route rescored under both versions.

**Decision rule for question 2.** Each hard fail is reported with the source sentence behind it. If H3-H6 fail (no hard fail where predicted), that is a point in favour of the authors' claim, and it is reported as such.

**Not a test of.** Yields, kinetics, chirality or the geology of borate supply. Rule v1 does not score those.

## Planted check

The scorer's 28 planted controls (task #3) must still pass 28/28 immediately before scoring. A run that fails them does not count.

## Outputs

`experiments/dsm_route/`:
- `steps_dsm.py`: the encoding. Its sha256 is written into `RESULTS.md` and posted as a board note before the scorer is run on it.
- `score_dsm.py`;
- `RESULTS.md`, `results.json`, `ledger_rows.csv`.
