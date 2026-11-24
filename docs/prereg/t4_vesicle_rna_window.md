# Pre-registration (T4): do vesicle-compatible and RNA-compatible windows overlap in real natural waters?

Status: **DRAFT, not sealed.** Round 1, 2026-11-24, by the T4 prep agent. Nothing is hashed. No joint-window count or share has been computed on field data. **Recommendation: do not seal this as a kill test.** The blind count shows that no arm can return a kill. See "What the blind count means".

Prior art and sources: `experiments/t4_vesicle_rna_window/PRIOR_ART.md`.
Analysis script: `experiments/t4_vesicle_rna_window/scripts/t4_analysis.py` (modes `count`, `loadcheck`, `planted`, `real`). `real` refuses to run until this file and the script each have a line in `docs/prereg/HASHES.txt`. That refusal was tested.

## What has been seen (blinding disclosure)

- **Field files.** The same two files as T3: MARHYS 4.0 and the USGS Yellowstone file. No new field file was fetched.
- **Counts seen.** Rows and clusters per setting with Mg, Ca, Na, K and pH filled. Then two margins per setting and window, as rows and clusters:
  - **A**, the Mg band: rows with RNA minimum ≤ Mg ≤ vesicle maximum.
  - **B**, the co-conditions: rows with Ca, salt and pH inside the vesicle window.
- **Not computed.** The joint count (A and B in the same row) for any setting. No share, ratio or interval. No measured value was printed, sorted, summarised or plotted.
- **A margin is a count of values.** It is weaker blinding than T3 kept. The task asked for it, to avoid T3's empty decision range. It is what shows the test is not a real test.
- **The windows were fixed first.** They are in `PRIOR_ART.md`, written before the count ran. One guard window (pure acid with no pH limit) was added to the count afterwards. It has the same Mg band, so only its B margin is new.
- **The kill bound was tightened once**, after the first planted run and before any seal. See "Planted power check".
- **Published summaries I did read.** Cary 2024 (a list of named springs said to hold divalent cations "<0.7 mM"). Cohen 2024 (two soda lakes at about 1 M Na⁺, 1 mM Mg²⁺, pH 10). Milshteyn 2018 (two Yellowstone pools and seawater).
- **Computed.** Synthetic worlds (`planted`). The loader check against T3's loaders (pass).

## The claim under test, and who makes it

**U (the window is missing outside soda lakes).** "Fatty acid vesicles have been shown to form in other putative early Earth environments, such as subaerial hot springs ( 52 , 53 ) and deep-sea hydrothermal vents ( 54 ); however, it is unclear whether any of these environments can also support the assembly of RNA, suggesting a possible unique role for soda lakes during the origin of life." (Cohen et al. 2024, doi:10.1093/pnasnexus/pgae084, opened.)

Read as a testable statement per setting: **water of this setting does not offer, in one sample, enough Mg for RNA chemistry and little enough Mg, Ca and salt for fatty-acid vesicles.**

The opposite view is in Milshteyn 2018 and Damer & Deamer 2020 (hot-spring water suits membranes) and Jordan 2019 (alkaline vent mixtures suit membranes). None of them adds an RNA condition.

## Inputs

| File | Source | sha256 (first 12) |
|---|---|---|
| `experiments/t3_rna_persistence/raw/marhys4/MARHYS_DB_4_0.xlsx` | Diehl & Bach 2024, doi:10.1594/PANGAEA.972999 | 1855355a392e |
| `experiments/t3_rna_persistence/raw/usgs_ynp_p92xkju7/YNP_WQ.csv` | McCleskey et al. 2022, ver. 2.0, doi:10.5066/P92XKJU7 | 084cb39954ae |

T4 reads Ca and Fe as well. It does not need temperature. Rows lost for a missing field are in `scripts_out/t4_blind_count.json`.

## Thresholds, with sources

All numbers are from opened papers. The full table is in `PRIOR_ART.md`. Concentrations in mM. M is Na⁺ + K⁺.

Vesicle side:

- Pure myristoleic acid leaks at 0.5 mM Mg and turns turbid at 1 mM (Chen 2005, doi:10.1021/ja051784p, Table 1).
- With its monoglyceride at 2:1 the limits are 4 and 6 mM (Chen 2005; Mansy & Szostak 2008, doi:10.1073/pnas.0805086105).
- Pure myristoleic acid stayed stable at about 2 mM Mg (Anella & Danelon 2014, doi:10.3390/life4040929).
- Oleic acid leaks at 10 mM Mg. With 15 mol% glycerol monooleate it holds (Adamala 2016, doi:10.1038/ncomms11041).
- Lauric acid with monolaurin flocculates beyond about 1.9 mM of Ca, Fe or Mg. Ca is the strongest. Without a wet-dry cycle vesicles are seen only at 0–0.5 mM Ca (Cary 2024, doi:10.3390/life14030415).
- Decanoic acid aggregates near 0.2 M NaCl (Chen 2005; Maurer 2017, doi:10.3390/life7040044).
- Acids with alkanols form vesicles from pH about 6.5 to above 12. At pH 12 they hold in 600 mM NaCl, 50 mM Mg and 10 mM Ca. At pH 7 or 9 they do not form in 20 mM MgCl₂ or 5 mM CaCl₂ (Jordan 2019, doi:10.1038/s41559-019-1015-y).

RNA side:

- **R50, Mg ≥ 50 mM.** "Both ribozyme catalyzed and non-enzymatic RNA copying reactions require high (50–200 mM) concentrations of Mg 2+" (Adamala & Szostak 2013, doi:10.1126/science.1241888).
- **R1, Mg ≥ 1 mM.** The lowest level at which an opened source shows activity. A hammerhead ribozyme at 1 mM (Chen 2005, Table 2). Copying and a ligase ribozyme at about 1 mM in lake water (Cohen 2024).

Windows, fixed before the count:

| Window | Mg | Ca | M | pH | Role |
|---|---|---|---|---|---|
| P-strict | ≤ 0.5 | ≤ 0.5 | ≤ 200 | 7.0–9.5 | pure acid, strict |
| P-lenient | ≤ 2 | ≤ 2 | ≤ 200 | 7.0–9.5 | pure arm, base |
| P-lenient-nopH | ≤ 2 | ≤ 2 | ≤ 200 | none | pure arm, lenient guard |
| M | ≤ 4 | ≤ 1.9 | ≤ 600 | 6.5–12 | mixed arm, base |
| M-strict | ≤ 4 | Ca + Fe(II) ≤ 0.5 | ≤ 600 | 7.0–11.5 | mixed arm, strict guard |
| M-lenient | ≤ 10 | ≤ 1.9 | ≤ 1000 | none | mixed arm, lenient guard |
| J-alk | ≤ 50 | ≤ 10 | ≤ 600 | ≥ 11.5 | reported only |

## Empty by definition (an established lab fact, not a result)

A pair is empty when the RNA minimum is above the vesicle Mg maximum. No water can be in such a window. No field data is used.

| Pair | Why empty |
|---|---|
| P-strict × R1 | 1 mM > 0.5 mM |
| P-strict, P-lenient, M, M-strict, M-lenient × R50 | 50 mM > 0.5 to 10 mM |

This is the Mg conflict that Adamala & Szostak 2013 and Chen 2005 already state. T4 reports it as their finding. It is not counted as a T4 kill or support for any setting.

Only J-alk × R50 is not empty by its numbers. Its B margin is zero rows in every setting, so it has no data.

## Blind count (rows / clusters)

Mixed arm, R1. A = Mg between 1 and 4 mM. B = Ca, salt and pH inside window M.

| Setting | Complete rows | Mg ≥ 1 mM | A (M) | B (M) | B (M-lenient) |
|---|---|---|---|---|---|
| USGS thermal water | 660 / 40 | 9 / 3 | 8 / 3 | 218 / 26 | 649 / 37 |
| USGS streams | 50 / 19 | 0 / 0 | 0 / 0 | 39 / 17 | 50 / 19 |
| USGS overflow | 67 / 7 | 3 / 1 | 3 / 1 | 63 / 5 | 64 / 6 |
| USGS lake | 15 / 5 | 0 / 0 | 0 / 0 | 13 / 5 | 15 / 5 |
| Vent HF, basalt ridge | 717 / 29 | 700 / 29 | 136 / 17 | 0 / 0 | 1 / 1 |
| Vent HF, arc and back-arc | 544 / 39 | 515 / 39 | 99 / 21 | 2 / 1 | 11 / 1 |
| Vent HF, ultramafic other | 163 / 4 | 160 / 4 | 43 / 3 | 0 / 0 | 0 / 0 |
| Vent HF, sediment | 111 / 3 | 108 / 3 | 32 / 2 | 0 / 0 | 0 / 0 |
| Vent HF, Lost City type | 10 / 2 | 9 / 2 | 7 / 2 | 0 / 0 | 0 / 0 |
| Vent HF, other | 27 / 5 | 26 / 4 | 2 / 1 | 0 / 0 | 0 / 0 |

Pure arm, R1 (A = Mg between 1 and 2 mM): thermal water A 5 / 2; basalt ridge A 32 / 8, B 0; arc A 40 / 14, B 0. Full table: `scripts_out/t4_blind_count.log`.

## What the blind count means

The joint window needs A and B in one row. So the joint count can never exceed the smaller margin.

- **Springs, streams and lakes are Mg-poor.** 9 of 660 thermal-water rows reach 1 mM Mg, in 3 of 40 areas. The joint share can be at most 8 rows, or 1.2%. A kill needs 5%. A kill is impossible.
- **Vents fail on salt and calcium.** B is 0 to 2 rows in every vent class. So the share of in-band rows that also pass B is at most 2 in 99. A kill needs 25%. A kill is impossible.
- **So every decidable arm can only return "supported" or "inconclusive".** That is known before the joint count is run. The outcome comes from one margin per setting, not from how Mg varies with Ca, salt or pH.
- **The covariation null adds nothing.** With A or B near zero, observed and expected joint shares are both near zero.

This is the T3 pattern in a new form. T3's decision range was empty. T4's decision range is full on one side only. A sealed run would look like a passed test and carry no risk of failure. **I recommend not sealing it as a kill test.** What it honestly is: a descriptive count, "Yellowstone waters are Mg-poor; sampled vent fluids are too salty and Ca-rich". Both are near-restatements of Cary 2024 and Milshteyn 2018 on a larger table.

The rules below are kept so the design is on record, and so a new dataset with real spread in Mg (closed-basin and soda lakes) could be run under them.

## Settings that cannot decide (declared up front)

Bars: at least 30 rows and 5 clusters. For vents the bars apply to in-band rows (A).

| Setting | Why it cannot decide |
|---|---|
| Vent HF, ultramafic other | 4 clusters; A in 3 |
| Vent HF, sediment | 3 clusters; A in 2 |
| Vent HF, Lost City type | 10 rows, 2 clusters |
| Vent HF, other | A is 2 rows in 1 cluster |
| USGS lake | 15 rows |
| USGS drillhole, seep | 7 and 3 rows, 1 cluster each |
| All EM rows | Mg is zero by definition; never decision rows |
| Seawater rows | reference only |

The planted run confirms it for the ultramafic class: "cannot decide" in every world. So T4 says nothing about Lost City or other serpentinite vents. That is the setting Jordan 2019 argues for.

## Decidable arms, statistics and rules

Decidable by size: USGS thermal water, streams and overflow (share rule). Vent HF basalt ridge and arc/back-arc (conditional rule). Arms: mixed (M) and pure (P-lenient), each with R1.

Statistics, per setting and window:

- J = share of rows in A and B. pA, pB = the margins as shares.
- cond = share of in-band rows that pass B.
- **Null.** Expected joint share = pA × pB. That is what J would be if Mg were drawn at random from the same class. A second version shuffles Mg only inside each area. rho = J / expected.
- Intervals: cluster bootstrap over areas, 10,000 draws, seed 20261126.

**Share rule (springs, streams, lakes).**

- **U killed** if the 0.5th percentile of the bootstrap for J is ≥ 5%, and joint rows sit in ≥ 5 areas. The strict window must agree. If not: "not reported as a kill: fragile".
- **U supported** if J ≤ 1% and joint rows sit in ≤ 1 area. The lenient window must agree. If not: "not reported as support: window-dependent".
- Otherwise inconclusive.

**Conditional rule (vents).** Mg in a sampled vent fluid is mostly a seawater fraction. So the Mg band is set by how the sample was taken. The decision is on cond.

- Needs ≥ 30 in-band rows in ≥ 5 areas.
- **U killed** if the 0.5th percentile of cond is ≥ 0.25. The strict window must agree.
- **U supported** if cond ≤ 0.02. The lenient window must agree.

**Guards.** They can remove a verdict. They cannot create one.

- Mixing guard (vents): for each EM row, does the straight mixing line with median seawater pass through the window? If that disagrees with the HF verdict, the label is "sampling-driven, not reported".
- Labels, which never change a verdict: "Mg-poor: the Mg band alone decides" (upper bound of pA ≤ 1%); "covariation closes the window" (expected ≥ 5% and rho < 0.5); "covariation opens the window"; "no covariation shown".

What the margins already allow:

| Setting, mixed arm | Kill possible? | Possible outcomes |
|---|---|---|
| Thermal water | no (J ≤ 1.2%) | supported, inconclusive, not reported |
| Streams | no (A = 0) | supported, label Mg-poor, for certain |
| Overflow | no (J ≤ 4.5%) | supported only if no joint row; else inconclusive |
| Basalt ridge vents | no (B = 0) | supported for certain, unless the mixing guard removes it |
| Arc vents | no (cond ≤ 2 in 99) | supported or inconclusive |

## Planted power check

Synthetic values on the real cluster sizes. 200 runs per world, 400 bootstrap draws. Mixed arm, R1. Log: `scripts_out/t4_planted.log`.

**Round 1 found too many kills on the bar.** The kill bound was then the 2.5th percentile. Worlds built with the true value on the kill bar gave kills in 12% of runs (thermal-water structure) and 8% and 3% (vent structure). The nominal rate is 2.5%. The cluster bootstrap is too narrow with unequal area sizes. That is not acceptable for a rule that reports a kill. **Fix, made before any seal:** the kill bound is now the 0.5th percentile. Round 1 is kept in `scripts_out/t4_planted_round1.log`.

Round 2, share of runs:

| World | What it shows | Thermal water (share rule) | Basalt vents (cond rule) |
|---|---|---|---|
| W0 Mg-poor | support is found and labelled Mg-poor | supported 1.00 | cannot decide 1.00 |
| W1 window common | a real window is seen | killed 0.97 | killed 0.95 |
| W2 acid pH closes it | support that hangs on the pH limit is not reported | not reported 1.00 | not reported 1.00 |
| W3 rare; on the vent bar | no kill at the bar | inconclusive 1.00 | killed 0.02 |
| W3b on both bars | kill rate at the bar | killed 0.01 | killed 0.02 |
| W3c below both bars | no kill below the bar | killed 0.00 | killed 0.00 |
| W4 two areas only | two areas cannot make a kill | inconclusive 1.00 | cannot decide 1.00 |
| W5 pH just outside | not reported as support | not reported 1.00 | not reported 1.00 |
| W6 Mg 5–9 mM | not reported as support | not reported 1.00 | cannot decide 1.00 |
| W7 calcium closes it | support, labelled covariation | supported 1.00 (label 0.98) | supported 1.00 |

- False support: none in any world.
- False kills: at most 2% with the truth on the bar, and none below it. The area effects in the synthetic worlds push the true mean slightly above the bar, so 2% is an upper reading. I accept this rate.
- Power for a real window (W1) fell from 0.99 to 0.97 and from 0.97 to 0.95.
- Ultramafic structure (4 areas): cannot decide in every world, as declared.

The planted check shows the rules work. It does not rescue the test. On the real margins no kill can occur.

## Fixed decisions

- D1. Classes, pH column, M = Na + K, units, non-detects and clusters as in T3 (its D1, D3, D4, D8, D9, D10). Decision rows for vents are HF rows only.
- D2. A row needs Mg, Ca, Na, K and pH. Fe(II) is used where present, in M-strict only.
- D3. Windows and RNA minima as in the tables above. No temperature condition (Mansy 2008: vesicles stable to 90–100 °C).
- D4. Two arms, pure and mixed. They are reported separately and never pooled.
- D5. Pairs that are empty by definition are reported as such and take no part in any verdict.
- D6. Kill bound: 0.5th percentile of the cluster bootstrap. Bars: 5% and 5 areas (share), 0.25 (cond). Support bars: 1% and 1 area (share), 0.02 (cond).
- D7. Size bars: 30 rows and 5 areas.

## Ways it could be fooled

- **A window count is an upper bound.** In Joshi 2017 the pure acids, and acid plus alcohol, "did not form vesicles in the hot spring waters". The same mixtures do in buffer. Only mixtures with a monoglyceride formed vesicles there. Passing the window does not show vesicles form.
- **Evaporation.** Damer & Deamer 2020 say solutes "increase a 100-fold or more" as a pool dries. A Mg-poor spring could pass through the Mg band on the way. T4 does not model that.
- **pH limits are weak.** Milshteyn 2018 saw membranes at pH 3.3 in real spring water. Every support verdict is checked with no pH limit.
- **R1 is generous to RNA.** Activity at 1 mM is slow, and Cohen's copying used activated nucleotides in 1 M Na⁺ at pH 10.
- **Modern water.** Modern seawater has about 50 mM Mg. Early seawater may have differed. Vent HF rows carry modern seawater.
- **One park.** All spring rows are from Yellowstone.
- **Citrate and other chelators** change both windows (Adamala & Szostak 2013). No field file has them.

## Limits

- No kill can occur on these data. A "supported" verdict would be a count of two margins.
- Nothing can be said about serpentinite vents, lakes, or soda lakes. Soda lakes are not in either file.
- The pure-acid Ca limit is my choice, set equal to the Mg limit. No opened source gives it.

## Open before sealing

- **A. Decide whether to seal at all.** My advice: no. Publish the margin table as a descriptive note, or drop T4.
- **B. If the test is kept, it needs waters with spread in Mg.** A closed-basin or soda-lake chemistry table, with many lakes, would let U's "unique role for soda lakes" fail or pass. No such file is on disk. It must be found and blind-counted first.
- **C. Unread sources.** Monnard 2002 (doi:10.1089/15311070260192237) is the primary source for the decanoic acid limits. Deamer, Damer & Kompanichenko 2019 (doi:10.1089/ast.2018.1979) holds the spring list behind Cary's "<0.7 mM". Neither was opened.
- **D. The mixing guard leaves out pH**, because pH does not mix linearly.
- **E. Hashes.** Seal this file and the script together. The script changed after the planted run only in the count mode (one more margin window).

## Sources opened

Chen 2005, doi:10.1021/ja051784p. Adamala & Szostak 2013, doi:10.1126/science.1241888. Mansy & Szostak 2008, doi:10.1073/pnas.0805086105. Anella & Danelon 2014, doi:10.3390/life4040929. Adamala 2016, doi:10.1038/ncomms11041. Maurer 2017, doi:10.3390/life7040044. Joshi 2017, doi:10.3390/life7040051. Milshteyn 2018, doi:10.3390/life8020011. Jordan 2019, doi:10.1038/s41559-019-1015-y. Damer & Deamer 2020, doi:10.1089/ast.2019.2045. Joshi 2021, doi:10.3390/life11121413. Cohen 2024, doi:10.1093/pnasnexus/pgae084. Cary 2024, doi:10.3390/life14030415. Where each was opened is in `PRIOR_ART.md`.
