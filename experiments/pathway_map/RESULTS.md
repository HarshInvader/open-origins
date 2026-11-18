# Pathway map: no route is continuous, and no hand-off between two published steps passes cleanly

**Verdict.** I encoded four routes from the papers themselves: cyanosulfidic, alkaline vent, warm pond and ice-RNA. I then scored them under the sealed compatibility rule (sha256 `bfa572ed…`, scorer unchanged).

- **No route is continuous.** Of the 22 hand-offs between steps, none is continuous: 9 have a hard fail, 12 are blocked because one side has no published step, and 1 passes but cannot be fully checked.
- **The furthest route is cyanosulfidic.** It reaches oligomers (S3) with published yields at every stage on the way, but 8 of its 9 hand-offs are unexplained. Only C3→C4 (thione to aminooxazoline) passes, and only on the most favourable reading.
- **Fewest breaks.** Ranked by the rule (hard fails first), the alkaline vent comes first with 0 hard fails. That ranking is an artefact: 5 of the vent's 6 steps have no published chemistry, so there is nothing to break. Counting unexplained hand-offs instead, the routes tie at "all of them", except cyanosulfidic, which has 8 of 9.
- **Where each route first breaks:**
  - cyanosulfidic: at C1→C2. Ritson 2012 gives the sugars only as cyanate-trapped oxazolidinones, and the next step needs free glycolaldehyde (F4).
  - alkaline vent: right after formate and acetate (V1→V2). No vent step to sugars or nucleotides exists.
  - warm pond: at entry. The pond has no nucleotide source, and both pond papers start from laboratory nucleotides (F4).
  - ice-RNA: at entry. Nothing makes triplet substrates, and every RNA input is supplied purified (F4, F6).
- **The gap every route shares.** No route has any published step for sustained replication of the replicator (S5). The only template copying with a yield (S4) uses a purified, selected ribozyme plus purified triplets, primers and a hexamer.

**Task #18, net replication per cycle.**
- **QT45 is below 1.** Under its paper's own conditions the net factor is about **0.65 per 72-day incubation**. Synthesis (0.24% and 0.17% per 72 days) is about **210 times slower** than decay (half-life ~117 days). Counting only perfect copies, it is about **970 times slower**.
- **Attwater 2025 is above 1, but only for what gets copied.** Short templates grow 1.11-1.46-fold per cycle, and a 29-nt ribozyme fragment up to 1.26-fold. The whole replicase is never copied: fresh ribozyme is added at each dilution. So no paper shows a replicator with net growth above 1.

These results are negative. There is no positive continuity claim to red-team. I did add an M6 task to audit the encoding (below), because a misread step could flip a verdict.

## Hand-offs per route

| Route | Steps (yield / purified / missing / unread) | Hand-offs | Continuous | Unverified | Broken (hard fail) | Blocked by missing step | Hard-fail codes | Warnings |
|---|---|---|---|---|---|---|---|---|
| Cyanosulfidic | 10 (1 / 5 / 2 / 2) | 9 | 0 | 1 | 5 | 3 | F3, F4, F6 | 4 |
| Alkaline vent | 6 (1 / 0 / 5 / 0) | 5 | 0 | 0 | 0 | 5 | none | 0 |
| Warm pond | 5 (0 / 1 / 3 / 1) | 4 | 0 | 0 | 2 (+ entry F4) | 2 | F4, F6 | 0 |
| Ice-RNA | 5 (0 / 2 / 3 / 0) | 4 | 0 | 0 | 2 (+ entry F4) | 2 | F4, F6 | 1 |

Rule ranking (hard fails, then missing, then purified, then warnings): vent, ice-RNA, pond, cyanosulfidic. Read it with the caveat above.

"Unexplained" means a hard fail or a missing or unread step on either side. "Unverified" means no hard fail, but some check lacks a number in the source (see Method).

## Where each route breaks (every hard fail)

**Cyanosulfidic** (Ritson 2012 → Stairs 2017 → Powner 2009 → Caimi 2025):
- **C1→C2, F4.** Free glycolaldehyde is not made. Ritson's photoredox gives it trapped as an oxazolidinone (~15%). Stairs starts from commercial glycolaldehyde.
- **C2→C3, F4.** The same problem for glyceraldehyde (its oxazolidinone forms at 1-5%). The pH step from below 1 to 7 was cleared by crystallising 2-thiooxazole (which Stairs reports) and redissolving it in rain.
- **C3→C4: passes, unverified.** It passes only if (a) Stairs' lab crystallisation of the thione counts as a demonstrated separation, and (b) the step runs at pH 9, inside the 8.5-10.5 range where Stairs reports 15-23% per pass. Gas exchange raises pH by the rule's 2-unit cap. The two-cycle 45%+33% yield is at pH 10.5, which the rule cannot reach from pH 7.
- **C5→C6, F3 and F6.** The phosphorylation with a reported yield (44%) runs in formamide at 100 °C, and no listed process supplies formamide. Its input, anhydrocytidine, was commercial (ancitabine).
- **C6→C7, F3.** Formamide back to water for the UV step: no listed process removes formamide.
- **C7→C8, F4 and F6.**
  - The route makes no canonical purines: cAMP and cGMP have no source (Stairs makes 8-oxo-purines).
  - Caimi's polymerisation used commercial BioLog cyclic nucleotides.
- **Unread steps.** C5 (anhydrocytidine) and C7 (UV C→U) are Powner 2009, which is paywalled, so they count as missing.

**Alkaline vent** (Altair 2025):
- **Only step 1 exists.** Formate (736 µM) and acetate (11 µM) form after 18 h under a 6/75 °C, pH 5.7/11 gradient across Ni-FeS. The set-up uses a Nafion membrane and wired electrodes.
- **Steps 2-6 are missing:** sugars, nucleotides, oligomers, copying and replication.
- **The one hand-off out of step 1 has no hard fail.** It uses transport plus 1000× thermophoresis (Matreux 2024), but it leads into a missing step.

**Warm pond** (Simonis 2026 abstract → Caimi 2025):
- **Entry, F4.** No nucleotide feedstock.
- **P0→P1, F6.** Simonis starts from laboratory 5′-AMP and 5′-UMP.
- **P1→P2, F4 and F6.**
  - cGMP and cCMP have no source (Simonis tested A and U only).
  - Caimi used commercial cyclic nucleotides.
  - The abstract does not say which isomer Simonis's cyclic products are, so passing cAMP and cUMP through F4 is provisional.
- **Not scored by the rule:** Seltún spring water destroyed about 90% of A10/U10 in 4 cycles (Simonis abstract).

**Ice-RNA** (Gianni 2026 QT45, Attwater 2025):
- **Entry, F4.** Nothing makes triplet substrates.
- **I2→I3, F4 and F6.** QT45 is a selected, transcribed 45-mer (the step that would make it abiotically is missing). Primer and hexamer have no source. Triplets were supplied purified.
- **I3→I4, F4 and F6.** Attwater's replicator is a different ribozyme (the triplet polymerase ribozyme, TPR), with primers and template supplied.

## Ranked gap list (27 gaps; full list with details in `map.json` → `gaps`)

Rank order:
1. Gaps no route has bridged even with purified inputs.
2. Then gaps bridged only with purified inputs.
3. Then by the number of routes blocked at that stage.
4. Then the earlier stage first.

| Rank | Gap | Routes blocked | Routes with any yield at this stage |
|---|---|---|---|
| 1-4 | **S5: sustained replication of a whole replicator** (missing in all four: C10, V6, P4, I5) | 4 | 0 |
| 5-15 | **S2: nucleotides from the scenario's own feedstocks.** Missing in vent, pond and ice; unread Powner steps; formamide hand-offs (C5→C6, C6→C7 F3); laboratory nucleotides (P0→P1 F6); no nucleotide or triplet feedstock (pond and ice entry F4) | 4 | 1 (cyanosulfidic, purified only) |
| 16-20 | **S4: template copying.** Missing in cyanosulfidic, vent and pond. Ice-RNA has a yield, but its ribozyme, primers and triplets are all supplied (I2→I3, I3→I4: F4, F6) | 4 | 1 (purified only) |
| 21-24 | **S3: oligomers without commercial nucleotides and with purines.** Missing in vent and ice; C7→C8 and P1→P2 (F4 purines, F6) | 4 | 2 (purified only) |
| 25-27 | **S1: free C2/C3 sugars from C1 chemistry.** Vent V2 missing; cyanosulfidic C1→C2 and C2→C3 (F4: sugars come out trapped) | 2 | 2 |

The ranking puts **purine nucleotides** and **a source of activated substrates (triplets or cyclic nucleotides) inside the scenario** near the top. Every route that reaches polymers or copying fails there (F4 or F6) before it ever meets S5.

## Task #18: net replication per cycle

| | QT45 (Gianni 2026) | Attwater 2025 (TPR) |
|---|---|---|
| Conditions | eutectic ice −7 °C, pH 9, 0.4 mM MgCl₂, 8 nM template, 80 nM ribozyme, 50 nM each triplet; (+) and (−) in separate tubes; 72 days | pH-freeze-thaw cycles about once a day (HCl, 80 °C for 2 min, KOH, −7 °C for ~24 h), 0.4 mM MgCl₂, 20 nM ribozyme, 100 nM each triplet; twofold dilution into fresh ribozyme every 4th cycle |
| Copying | (−) 0.24%, (+) 0.17% in 72 days; 10.9% / 43.4% perfect full-length | short templates ×1.20-1.46 per cycle; A_D duplex 9× and 31× over 21 cycles (×1.11 and ×1.18 per cycle); 29-nt ribozyme fragment up to ×1.26 |
| Decay | half-life ~117 days (paper, fig. S8) | not used (the ribozyme is resupplied) |
| **Net per cycle** | **0.65 per 72 days (below 1)**; rate must rise ~210× (~970× for perfect copies only); with no decay, the doubling time would be ~68 years | **above 1 for templates; not measured for the replicase**, which is supplied rather than copied |

How the QT45 figure was computed:
- **Model.** Two strands copy each other with first-order rates k = yield / 72 days and decay at ln2 / 117 per day. Net growth rate r = √(k₊k₋) − k_deg.
- **Correcting for ribozyme decay during the incubation** changes the gap by only about 1.2×.
- **Caveat.** The half-life was measured in "standard reaction conditions" (fig. S8, which I did not read). Those may not be the low-Mg buffer used for self-synthesis.

Code: `net_replication.py`.

## Method

**Step tables.** These live in `steps.py`. One row per step:
- inputs with concentration and a purified flag;
- conditions: pH, T, solvent, redox;
- outputs with concentration and end conditions;
- yield status and text;
- source DOI, plus the place in the paper where each number was read;
- notes, and any assumptions I made.

Scenarios (feedstocks, streams, settings, T range, UV) come with a `basis` that cites their source. Hand-offs list processes from the rule's closed list, each with a reason.

**Sources opened.**
- Full text via Europe PMC or PMC:
  - Ritson 2012;
  - Patel 2015;
  - Stairs 2017;
  - Hudson 2020;
  - Matreux 2024;
  - Altair 2025;
  - Caimi 2025;
  - Attwater 2025;
  - Gianni 2026.
- Abstract only:
  - Simonis 2026 (paywalled);
  - Powner 2009 (paywalled; its steps are marked `unread`).
- Two DOIs were added to `docs/PAPERS.csv` after a Crossref check: Ritson 2012 (10.1038/nchem.1467) and Stairs 2017 (10.1038/ncomms15270).

**Scoring.** `score_map.py` calls `experiments/compat/scorer.py` unchanged. The planted controls were rerun first and still pass 28 of 28.

The scorer assumes complete numbers. Where a source does not report one:
- with NaN, it silently passes F1, F5, W1 and W2;
- with a NaN required temperature, it raises F2;
- with an "unknown" solvent or redox, it raises F3 or F8.

So the wrapper replays the state with the scorer's own functions and reports those checks as **unassessed**. It never adds a fail, and it removes only F2, F3 and F8 flags whose inputs were missing.

**Steps marked `unread`.** These are given to the scorer as `missing`, so no route can be called continuous on a step I could not read.

**Choices that favour the routes.** These are deliberate, so that a fail means a real gap. A red team should attack them:
- C2→C3: crystals redissolved in rain at a stated pH 6;
- C3→C4: a lab crystallisation counts as a demonstrated separation, and the step is encoded at pH 9 inside the source's range;
- C4→C5: CO₂ gas exchange lowers pH by 2;
- vent: 1000× thermophoresis;
- urea is counted as a cyanosulfidic feedstock, because Patel 2015 calls it a by-product of the cyanamide step.

**Choices against the routes:**
- Ritson's sugars count as unavailable, because they are trapped as oxazolidinones.
- Formamide counts as unobtainable.

## Not checked

- **Paywalled full texts.** Powner 2009 (C5 and C7) and Simonis 2026 are abstract only. Reading Powner could turn C5 and C7 into scored steps. It cannot fix C1→C2 or the formamide F3.
- **Supplementary information.** I read no SI files. Concentrations and temperatures for Ritson C1, the QT45 half-life conditions, and Attwater's per-nucleotide fidelity are all in SIs.
- **Other branches.** Not encoded:
  - the Powner 2-aminooxazole branch with its own yields (paywalled);
  - Patel's H₂S-driven homologation (no yields in the main text);
  - Hudson 2020 as an alternative vent step 1 (1.5 µM formate; in the notes);
  - an impact or formamide scenario.

  Each would be a new route under the same rule.
- **Kinetics, side products and decomposition during hand-offs.** These are outside the rule. Simonis's degradation result is recorded but not scored.
- **Unassessed checks.** There are many: most sources give no redox class or feedstock concentration. They are listed per hand-off in `map.json` (`unassessed`) and `handoffs.csv`.

## map.json format (for the site's pathway-map page)

Top level:
- `format`, `rule_file`, `rule_sha256`, `scorer`, `built_by`;
- `stages`: S1-S5 with labels;
- `check_names`: F1-F9 and W1-W3, each with a plain name;
- `legend`: the meaning of every `yield_status` and hand-off `verdict`;
- `ranking`: route ids in the rule's order;
- `routes[]`;
- `gaps[]`.

Each entry in `routes[]` has:
- `id`, `label`, `note`;
- `summary`: the counts in the table above, plus `continuous`, `hard_fail_codes` and `stages_missing`;
- `scenario`: name, T range, UV, redox, settings, feedstocks (`"unstated"` means no stated concentration), streams and `basis` text;
- `steps[]`;
- `handoffs[]`.

Each step in `steps[]` has:
- `id`, `name`, `stage`, `setting`;
- `inputs[]` (species, conc in M or null, purified, note);
- `conditions` (ph, t, solvent, redox; null when not reported);
- `outputs`;
- `purified_inputs`;
- `yield_status`: `demonstrated`, `demonstrated_purified`, `missing` or `unread`;
- `yield_text`;
- `source_doi` and `source_url`;
- `where`, `notes`, `assumptions[]`.

Each hand-off in `handoffs[]` has:
- `id` (for example `C1->C2`; the first is `entry->C1`), `from_step`, `to_step`;
- `processes[]`;
- `verdict`: `continuous`, `unverified`, `blocked_by_missing_step` or `broken`;
- `unexplained`;
- `flags` and the scorer's `notes`;
- `unassessed[]` (code, species, reason);
- `why`: a plain-language justification.

Each entry in `gaps[]` has:
- `rank`, `route`, `where`, `stage`;
- `kind`: `missing_step`, `unread_step` or `hard_fail`;
- `codes`, `detail`;
- `routes_blocked_at_stage`, `routes_with_any_yield_at_stage`, `routes_with_unpurified_yield_at_stage`.

A site page can draw one row per route with a coloured cell per step (`yield_status`), a connector per hand-off (`verdict`), and the `notes` and `why` text on hover.

## Files

- `steps.py`: step tables and scenarios (tasks #4 and #17).
- `score_map.py`: the scoring wrapper (task #5); writes `map.json`, `results.json` and `handoffs.csv`.
- `net_replication.py`: task #18; adds `net_replication` to `results.json`.
- `ledger_rows.csv`: 6 rows (4 routes, 2 replication).
- `tools/xml2txt.py`: tag stripper for the downloaded full texts.
- Rerun with:

  ```
  .venv/bin/python -I experiments/pathway_map/score_map.py && .venv/bin/python -I experiments/pathway_map/net_replication.py
  ```

  This takes under a second.
- **Raw files deleted.** The downloaded full texts (2.9 MB of XML and HTML) were deleted after extraction, as the disk rule requires.

## Hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| At least one of the four routes is continuous under rule v1 | score all hand-offs | no: 0 of 22 hand-offs continuous |
| The cyanosulfidic route's breaks are only about purification | hard-fail codes | no: F3 (formamide) and F4 (trapped sugars, no purines) as well as F6 |
| The vent route's low hard-fail count means it is the most complete | count missing steps | no: 5 of 6 steps have no published chemistry |
| QT45 nets more than 1 per cycle under its paper's conditions | yields vs half-life | no: 0.65 per 72 days; needs ~210× faster synthesis |
| Attwater's system nets more than 1 per cycle | per-cycle fits in the paper | yes for short templates and a 29-nt fragment (1.11-1.46); not shown for the replicase itself |
