# Pre-registration (T7): does evaporating real hot-spring water open the vesicle and RNA-copying window?

Status: DRAFT, written 2026-11-24 by the T7 prep agent. This is Route 6 (lipid, compartment first). `count`, `gate`, `planted` and `dryrun` have been run. `real` has not been run. The script refuses to run it until `docs/prereg/HASHES.txt` has two lines: one naming `experiments/t7_evaporation_window/scripts/t7_analysis.py` with its current sha256, and one naming this file with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is the joint state along each spring's evaporation path. That means Mg, Ca, Na + K and pH at the same concentration factor (CF). No script has computed an evaporation path for an unpermuted field water.

- **Seen before T7, from T4.** In the raw USGS thermal-water rows, 9 of 660 reach Mg ≥ 1 mM, in 3 of 40 areas (`experiments/t4_vesicle_rna_window/T4_STATUS.md`). These are raw waters with no evaporation. They tell me that Mg starts low.
- **Margins only (`count`).** Rows with each input filled, rows with a complete input set, and rows passing the charge-balance filter. The counts are given in "Blind counts" below. No path was computed and no window was evaluated.
- **Synthetic and published waters only (`gate`, `planted`).** Seawater, the Lake Magadi brine and the synthetic template waters. No field value enters them.
- **Permuted field rows (`dryrun`).** Every solute column, pH and T are shuffled independently across rows before the `real` code runs. This breaks the joint, which is the unknown. It keeps the marginals, so it does leak them. Under permutation, 6.6% of USGS rows pass window M along the primary path, and 4.5% of the first 200 historic rows do. That is what Yellowstone's marginals allow when they are mixed at random. It is not an estimate of the real share. It does tell me that the real answer is not forced to zero by the marginals alone.
- **One stray line.** PHREEQC wrote `error.inp` (the raw state of one failing permuted water) into the experiment folder. I opened its first five lines (temperature 78.8 °C) and deleted it. It is a permuted water.
- **What this does to my expectation.** I expect that many waters never reach 1 mM Mg, and that the acid ones never enter the pH window. I have no view on the sign of the result.

## Claim under test

**H.** Evaporating real hot-spring waters brings Mg into the range for nonenzymatic RNA copying (≥ 1 mM; T4's R1) while the water is still inside the fatty-acid or mixed-amphiphile vesicle window. The window limits are Ca, Na + K and pH, as T4 used them.

Where the claim comes from (all opened; quotes and files in `experiments/t7_evaporation_window/PRIOR_ART.md`):

- Damer & Deamer 2020, doi:10.1089/ast.2019.2045, quoted verbatim: "As evaporation occurs during a wet-dry cycle, the initial modest concentrations of the various ionic solutes of hydrothermal fields increase a 100-fold or more as most of the water is lost to the atmosphere."
- Milshteyn et al. 2018, doi:10.3390/life8020011, quoted verbatim: "if the Mammoth Hot Spring water undergoes drying, the 27 mM ionic solutes pass through a concentration equivalent to ~2 molar when 99% of the water has evaporated."
- Cary et al. 2024, doi:10.3390/life14030415, quoted verbatim: "A potential outcome is that cation concentrations increase in pools during evaporation."
- Cohen et al. 2024, doi:10.1093/pnasnexus/pgae084, quoted verbatim: "...while maintaining ∼1 mM divalent cations because of the poor solubility of Mg-containing carbonates". The quote is about soda lakes.

These sources treat evaporation as linear concentration with no minerals. The soda-lake papers show the mechanism that could open the window: carbonate removes Ca while Mg stays in solution. None of them runs a database of spring waters along a mineral-saturation path against the joint window. Prior-art verdict: not settled.

## Inputs (exact)

| File | Source | sha256 |
|---|---|---|
| `experiments/t3_rna_persistence/raw/usgs_ynp_p92xkju7/YNP_WQ.csv` | McCleskey et al. 2022, ver. 2.0 (2025), doi:10.5066/P92XKJU7; already in the repo (as cited by T3) | 084cb39954ae8cf5740302ded09faaef4a81d90dbeeb399718f848187d7e7911 |
| `experiments/t3_rna_persistence/raw/usgs_ynp_historic_p9ksevi1/Yellowstone_Water_Chemistry_1883-2021.csv` | Price et al. 2024, doi:10.5066/P9KSEVI1; already in the repo (as cited by T3) | cee22209d5a350ed10af3bb54ee84a1525202f05b50537708eaf7677296b7e90 |
| `pitzer.dat` bundled in phreeqpython 1.6.2 (inside the gitignored `.venv`) | PHREEQC Pitzer database | eb5051704fad461c4e5325721afc7b9025fad7c2906f72ed48ae182aa2c1a5c9 |
| `phreeqpython-1.6.2.tar.gz` (PyPI sdist; installed into the venv, not kept in the repo) | IPhreeqc 3 with a universal macOS library | b7bb93fa5a87f6c7778916e56f2abecc3b13bd3b64ae74cd46328335227297e2 |

The sha256 of each output, and of the script and this file, is listed in `HASHES.txt` at sealing. `real` checks the two CSVs and `pitzer.dat` against the hashes above and stops on a mismatch. Nothing new was downloaded except the papers in `raw/lit/` and the PyPI sdist.

## Model

- **Engine.** PHREEQC 3 (IPhreeqc, through phreeqpython 1.6.2). One database: `pitzer.dat`, with Pitzer activities valid at high ionic strength and to about 200 °C. It has Si, SiO2(a), Sepiolite, Sepiolite(d), Brucite and the soda-lake and seawater salts.
- **Fluoride.** `pitzer.dat` has no F. The F⁻, HF and MgF⁺ species and Fluorite were copied from the `phreeqc.dat` bundled in the same package. They are loaded once per engine. Fluorite is a real Ca sink in Yellowstone alkaline-chloride water.
- **The path.** Water is removed as a REACTION on a log-spaced CF grid from 1 to `cf_max`, in 61 steps. The removal in each step is 55.5084 × (1 − 1/CF) mol. Minerals may only precipitate (initial amount 0, at a target saturation index). The raw water, with no minerals, is state 0 of the same path.
- **Path end.** `cf_max` is the smaller of 1000 and the CF at which Na + K would pass 1500 mM by simple scaling (but at least 1.5). Past that, every window's salt limit is closed many times over. This is D5.
- **Temperature.** The pool sits at the spring's temperature, capped at 95 °C. A 25 °C variant uses REACTION_TEMPERATURE 25.
- **Gas.** Closed (no gas exchange), or open to modern air at log pCO2 −3.4.
- **Failures.** If PHREEQC fails, the first retry doubles the number of steps to the same end point. The second and third retries shorten the path to `cf_max`^0.85 each time. The prefix of a shortened path is valid and is used; that path is marked truncated. After four failures the path counts as failed.

### Mineral sets (D6)

LATE is 24 late salts that can only form near dryness: Halite, Sylvite, Mirabilite, Thenardite, Glauberite, Gaylussite, Pirssonite, Trona, Natron, Nahcolite, Burkeite, Epsomite, Hexahydrite, Kieserite, Bloedite, Polyhalite, Syngenite, Glaserite, Arcanite, Kainite, Carnallite, Bischofite, Leonite and Schoenite. All are at saturation index 0.

| Set | Minerals (target saturation index) |
|---|---|
| base | Calcite 0, Gypsum 0, Anhydrite 0, Fluorite 0, SiO2(a) 0, Sepiolite(d) 0, Brucite 0, LATE |
| generous | base without Sepiolite(d) and Brucite (no early Mg sink), LATE |
| strict | Calcite 0.5 (calcite needs supersaturation), Gypsum 0, Anhydrite 0, no Fluorite, SiO2(a) 0, ordered Sepiolite 0, Brucite 0, LATE |

Dolomite and magnesite are left out of every set. They do not form at Earth-surface conditions on the time scale of a drying pool. Including them would remove Mg as a modelling artefact.

### Nine path combinations

| Name | Minerals | Temperature | Gas | Used for |
|---|---|---|---|---|
| base_Ts_closed | base | spring | closed | **primary** |
| base_Ts_open | base | spring | open | kill guard |
| base_25_closed | base | 25 °C | closed | kill guard |
| base_25_open | base | 25 °C | open | kill guard |
| gen_Ts_closed, gen_Ts_open, gen_25_closed, gen_25_open | generous | as named | as named | kill guard |
| strict_Ts_closed | strict | spring | closed | support guard |

## Windows (T4, mM; M = Na + K)

A state is inside a window when 1 ≤ Mg ≤ Mg max, Ca ≤ Ca max, M ≤ M max, and pH is inside the range. The Mg floor of 1 mM is T4's R1.

| Window | Mg max | Ca max | M max | pH | Role |
|---|---|---|---|---|---|
| M | 4 | 1.9 | 600 | 6.5–12 | mixed arm, base |
| M_strict | 4 | 0.5 | 600 | 7.0–11.5 | mixed arm, support guard |
| M_lenient_pH3 | 10 | 1.9 | 1000 | ≥ 3.0 | mixed arm, kill guard |
| P_lenient | 2 | 2 | 200 | 7.0–9.5 | pure arm, base and support guard |
| P_lenient_pH3 | 2 | 2 | 200 | ≥ 3.0 | pure arm, kill guard |
| R10_open | no ceiling, Mg ≥ 10 | 1.9 | 600 | 6.5–12 | reported only |

There are two differences from T4.

- T4's M-strict limited Ca + Fe(II) to 0.5 mM. The model has no Fe, so M_strict limits Ca alone.
- T4's lenient windows had no pH limit. Here they have a floor of pH 3.0. Milshteyn 2018 saw lauric-acid vesicles at pH 3.3 in Yellowstone water, quoted verbatim: "Dodecanoic acid (12-carbon lauric acid) formed membranous vesicles at pH 3.3 and pH 7.9". Nothing I opened shows vesicles below that. This floor was added after planted round 1 (see "Changes made before the seal").

P_strict (Mg ≤ 0.5) is empty with R1 by definition and is not tested.

## Unit and outcome

- **Unit.** One water sample (a row), clustered by its `Area`. Areas are resampled in the bootstrap.
- **Outcome.** A row passes a window if any state on its path, including the raw state, is inside the window. S is the share of rows that pass.
- **Interval.** An area bootstrap with 10,000 draws. Each draw takes the areas with replacement and computes the pooled row share. The bounds lo and hi are the 0.5th and 99.5th percentiles.
- **Decision set.** USGS `thermal water` rows from `YNP_WQ.csv` that pass D1–D3: 528 rows in 37 areas.
- **Replication set.** Historic `thermal water source` rows dated before 2009 that pass D1–D3: 749 rows in 34 areas. The same rules give a separate verdict on these.

## Fixed decisions

- **D1, inputs.** A row needs pH, T, Ca, Mg, Na, K, Cl, SO4 and SiO2. It also needs alkalinity, except when pH < 4.5. In that case alkalinity is set to 0 and no alkalinity term is passed to PHREEQC. F, Li, B and Br are used when present and set to 0 when missing.
  - pH is the field value, or the lab value when the field value is missing (T3 D3).
  - mg/L is divided by the atomic or formula mass and entered as mmol/kgw (T3 D8).
  - A value written "<x" enters as x/2 (T3 D9).
- **D2, replication set.** The historic file, restricted to rows dated before 2009 (T3 D11), so that it does not repeat the USGS rows. It gives a separate verdict and does not change the USGS verdict.
- **D3, charge balance.** A row is kept if its raw-state charge-balance error from PHREEQC is at most 10% in absolute value. This uses only the raw speciation.
- **D4, conditions.** The pool temperature is the spring temperature, capped at 95 °C. A 25 °C variant is also run. The gas is closed, or open at log pCO2 −3.4.
- **D5, path end.** As given in "Model": CF up to 1000, stopping where Na + K would pass 1500 mM.
- **D6, minerals.** The three sets above. Dolomite and magnesite are excluded.
- **D7, bar and tails.** The bar is S = 5%. The tails are 0.5% each. The support area rule is at least 5 areas with a passing row. At least 30 rows and 5 areas are needed to decide. "Rare" (S ≤ 1%) is a label only.
- **D8, guards.**
  - Support guard: the strict combination with window M_strict for the mixed arm, or P_lenient for the pure arm.
  - Kill guard: a row passes if it is inside M_lenient_pH3 (or P_lenient_pH3 for the pure arm) on any of the eight non-strict combinations.
- **D9, failures.** For each combination, the failed share is the share of rows whose path failed. If the worst of the nine is above 5%, the arm is "not reported: model failures". Truncated paths are used, and their count is reported.
- **D10, seed and order.** The seed is 20261127. `planted` uses the seed, `real` uses seed + 3 and `dryrun` uses seed + 4. The runs go in this order: `count`, `gate`, `planted`, `dryrun`, then the seal, then `real`.

## Decision rules (each arm, each set)

The rules are checked in this order.

1. **Not reported: model failures.** The worst failed share over the nine combinations is above 5%.
2. **Cannot decide by design.** Fewer than 30 rows or fewer than 5 areas.
3. **H supported.** On the primary path with the base window, lo ≥ 5% and passing rows sit in at least 5 areas. The support guard must meet the same rule. If it does not, the result is "not reported as support: fragile (strict minerals and window)".
4. **H killed.** On the primary path with the base window, hi < 5%. The kill guard must also have hi < 5%. If it does not, the result is "not reported as a kill: model-dependent (generous minerals or other path conditions open it)". A kill with S ≤ 1% carries the label "rare".
5. **Inconclusive.** Anything else.

**Headline.** The headline verdict is the USGS set, mixed arm. The pure arm and the historic set are reported beside it with their own verdicts. The headline says "replicated" only if the historic mixed arm gives the same verdict.

**What a kill means.** Under modern-air and spring-temperature pool chemistry, and even with generous minerals, fewer than 5% of Yellowstone thermal waters ever pass through the joint window as they dry. It does not mean that no pool anywhere could. It means the route needs something the spring water does not supply, such as mixing, a chelator or a different source rock.

**What a support means.** At least 5% of waters, spread over at least 5 areas, pass through the window as they dry. This must also hold with strict minerals and a strict Ca limit.

**Reported only, never deciding.**
- S for every combination and window (M, M_strict, M_lenient_pH3, P_lenient, R10_open).
- The failed and truncated counts per combination.
- The primary-path S for each arm among rows with raw pH ≥ 4.5 (added at the seal; see below).
- An attribution on the primary path. At the first state with Mg ≥ 1 mM, the row is either inside window M, or the attribution says which limit is out (Ca, salt, pH, Mg > 4). It can also say Mg never reaches 1 mM.

## Gate (`t7_analysis.py gate`; run; PASS)

The rules were written into the script (`GATE_RULES`) before the gate was first run. They were not changed afterwards.

**Seawater.** Milshteyn 2018 Table 3 water (Na 469, Ca 10, Mg 53, K 10, HCO3 2, SO4 28 mM), with Cl set by charge balance. The path runs at 25 °C, closed, with Calcite, Gypsum, Anhydrite and Halite, to CF 20 in 301 steps. The G3 bounds bracket Gharsalli 2026, doi:10.3389/fmicb.2026.1843317, quoted verbatim: "halite formation starts around FC ≈ 11". The G2 bounds are my own reading of the equilibrium sequence, with no opened source behind them.

| Check | Rule | Result |
|---|---|---|
| G1 | calcite saturation index > 0 in the raw water | 0.64, pass |
| G2 | gypsum onset CF in [3.0, 4.5] | 3.63, pass |
| G3 | halite onset CF in [9.5, 13.0] | 11.10, pass |
| G4 | Cl = CF × Cl₀ within 1% before halite | largest error 0.37%, pass |
| G5 | calcite saturation index at 90 °C > at 25 °C | 1.22 > 0.64, pass |

**Lake Magadi.** This is the published PHREEQC + Pitzer path of Getenet 2022, doi:10.1021/acs.cgd.1c01391, starting from its Table 1 brine. F and PO4 are omitted. The path runs at 25 °C, closed, to CF 100 in 401 steps. Each check must fall within a factor of 1.3 of the published value.

| Check | Published | T7 | Bounds | Result |
|---|---|---|---|---|
| M1 nahcolite onset CF | 6.2 | 6.25 | 4.77–8.06 | pass |
| M2 trona onset CF | 9.7 | 9.70 | 7.46–12.61 | pass |
| M3 halite onset CF | 32 | 28.0 | 24.6–41.6 | pass |
| M4 SiO2(a) saturation CF | 3.0 | 3.08 | 2.31–3.90 | pass |
| M5 pH at CF 6 below raw pH | 9.8 → 9.4 | 9.80 → 9.45 | | pass |

The following are not checks. Gaylussite begins at CF 8.67 (published 8.6). Pirssonite begins at 11.4 (published 11.5). The raw charge-balance error is 0.29%. The path failed at CF 100 and was shortened by the retry rule to CF 50.1, which still covers every check.

**Pass rule.** All of G1–G5, and at least 4 of M1–M5. The result is 5 of 5 and 5 of 5. **GATE PASS.**

Two code bugs were fixed before the gate passed. Neither changed a rule.

1. The raw-water row was missing from the output, which shifted every CF by one step. G1 and G4 failed in round 1. The fix was to put the solution, reaction and selected output in one simulation.
2. A failed path was shortened to the square root of its CF, which cut off Magadi halite. The fix is that the first retry now uses finer steps.

## Blind counts (margins only; taken before the design was fixed)

| Set | Rows | Complete (D1) | Complete areas | \|CBE\| ≤ 10% (kept) | Kept areas | \|CBE\| ≤ 20% | Kept rows with pH < 4.5 |
|---|---|---|---|---|---|---|---|
| USGS thermal water | 681 | 597 | 39 | **528** | **37** | 581 | 261 |
| Historic thermal water source, before 2009 | 2,731 | 884 | 38 | **749** | **34** | 785 | 318 |

For the historic set, 848 further rows were dropped because they are dated 2009 or later, or are undated.

- **The largest area** holds 180 of the 528 USGS rows (34%), and 413 of the 749 historic rows (55%). The area bootstrap carries this.
- **The decision is non-empty.**
  - Support needs lo ≥ 5% with passing rows in at least 5 areas. With 528 rows in 37 areas, that is reachable (planted P1 and P5).
  - A kill needs hi < 5%. That is reachable (planted P0 and P3).
- **Other USGS water types are not tested.**
  - overflow: 45 rows in 6 areas, 1 area holding 33
  - streams: 35 rows in 14 areas
  - lake: 14 rows in 5 areas
  - drill hole: 5 rows in 1 area
  - seep: 3 rows in 1 area

## Planted check (`t7_analysis.py planted`; run; synthetic waters only)

**Template waters.** There are six classes of 12 waters each. Each water is randomly varied around a recipe (each solute by a factor of e^±0.25; T from 40 to 92 °C). Every water is run through PHREEQC on all nine combinations, so each row's outcome is a real model result. The classes are:

- pass: dilute Na-HCO3 water with Ca well below Mg
- fail_ca: Ca-SO4 water
- fail_acid: pH about 2.5
- fail_salt: Na-Cl water with Mg/Na about 1e-4
- sep: alkaline, silica-rich and Mg-poor, so sepiolite decides
- strict: Ca between 0.5 and 1.9 mM when Mg reaches 1 mM

| Class | primary / M | strict / M_strict | any generous / M_lenient_pH3 | Failed paths |
|---|---|---|---|---|
| pass | 1.00 | 1.00 | 1.00 | 0 |
| fail_ca | 0.00 | 0.00 | 0.00 | 0 |
| fail_acid | 0.00 | 0.00 | 0.00 | 0 |
| fail_salt | 0.00 | 0.00 | 0.00 | 0 |
| sep | 0.00 | 0.00 | 1.00 | 0 |
| strict | 1.00 | 0.00 | 1.00 | 0 |

Every class behaves as designed.

**Worlds.** The real area sizes of each set are used. Each area gets a logit effect with sd 1. The logit shift is calibrated so that the expected share of the first class equals the planted value. The rest of each area is fail_ca, fail_acid and fail_salt in the ratio 0.4 : 0.4 : 0.2. There are 200 worlds per cell, with 400 bootstrap draws each, scored by the same `verdict()` code as `real` (mixed arm).

USGS structure (528 rows, 37 areas):

| World | Expected | Kill | Support | Inconclusive | Not reported |
|---|---|---|---|---|---|
| P0 nothing passes | kill | **1.000** | 0.000 | 0.000 | 0.000 |
| P1 30% pass | support | 0.000 | **1.000** | 0.000 | 0.000 |
| P2 5% pass (on the bar) | false calls rare | **0.020** | **0.000** | 0.975 | 0.005 |
| P3 1% pass | mostly kill | 0.965 | 0.000 | 0.035 | 0.000 |
| P4 2.5% pass | kill power | 0.415 | 0.000 | 0.570 | 0.015 |
| P5 12% pass | support power | 0.000 | 0.480 | 0.445 | 0.075 |
| P6 25% sep (sepiolite decides) | not reported as a kill | 0.000 | 0.000 | 0.000 | 1.000 |
| P7 30% strict (strict closes it) | not reported as support | 0.000 | 0.000 | 0.000 | 1.000 |
| P8 60% pass in 2 areas only | no support | 0.000 | 0.000 | 1.000 | 0.000 |

Historic structure (749 rows, 34 areas):

| World | Kill | Support | Inconclusive | Not reported |
|---|---|---|---|---|
| P0 | **1.000** | 0.000 | 0.000 | 0.000 |
| P1 | 0.000 | **0.995** | 0.005 | 0.000 |
| P2 on the bar | **0.035** | **0.005** | 0.945 | 0.015 |
| P3 | 0.925 | 0.000 | 0.065 | 0.010 |
| P4 | 0.480 | 0.000 | 0.505 | 0.015 |
| P5 | 0.000 | 0.505 | 0.475 | 0.020 |
| P6 | 0.000 | 0.000 | 0.000 | 1.000 |
| P7 | 0.000 | 0.000 | 0.000 | 1.000 |
| P8 | 0.000 | 0.000 | 1.000 | 0.000 |

**What the planted check shows.**
- Both verdicts can be reached.
- The false-kill rate at the bar is 2.0% (USGS) and 3.5% (historic), both at most 5%.
- The false-support rate at the bar is 0.0% and 0.5%.
- Both guards fire when they should (P6, P7).
- Two areas alone cannot give support (P8).
- Power is modest near the bar, at 0.4–0.5 for a true 2.5% or a true 12%. A result near the bar will most likely be "inconclusive".

## Changes made before the seal

All of these were made before any unpermuted field path was computed.

1. **Planted round 1** (kept in `scripts_out/t7_planted_round1.*`) said "TEMPLATES NOT AS DESIGNED". The fail_acid waters passed T4's lenient window, which has no pH limit, so a kill could never happen. Kill power was also zero, because the kill rule had an area cap copied from T4's support side. Two changes followed:
   - The lenient guards got a pH ≥ 3.0 floor (Milshteyn 2018, quoted above).
   - The area cap on kills was removed.
   The bar, the tails and the window limits did not change.
2. **Two gate code bugs**, described in the gate section. They were fixes, not rule changes.
3. **No alkalinity term below pH 4.5** in the PHREEQC input. Before this, permuted acid rows with nonzero alkalinity made the raw speciation fail. Real rows below pH 4.5 already had alkalinity set to 0 (D1). The change affects only the dryrun.
4. **The D9 failed share is the worst of all nine combinations.** Earlier, `real` took the worst of the primary, strict and generous combinations, while `planted` already used all nine. The script now matches the planted code. `gate` and `planted` were rerun on the final script. Their outputs are byte-identical to the earlier runs.

## Dry run (`t7_analysis.py dryrun all 200`; run on the final script; permuted inputs)

These are the `real` code paths on USGS rows (all 528) and the first 200 historic rows. Every solute column, pH and T are shuffled independently across rows, and areas stay in place. There are 2,000 bootstrap draws. **This is a code check. Nothing in it estimates the real answer.**

| Set | Arm | Verdict | S [lo, hi] | Passing rows | Areas with a pass |
|---|---|---|---|---|---|
| USGS | mixed | inconclusive | 0.0663 [0.0389, 0.0832] | 35 / 528 | 15 / 37 |
| USGS | pure | not reported as a kill (model-dependent) | 0.0284 [0.0085, 0.0472] | 15 / 528 | 7 / 37 |
| historic (200) | mixed | inconclusive | 0.0450 [0.0000, 0.1500] | 9 / 200 | 4 / 16 |
| historic (200) | pure | inconclusive | 0.0150 [0.0000, 0.0968] | 3 / 200 | 2 / 16 |

- Failed paths: 2.5% (USGS) and 4.0% (historic) in every combination. Truncated paths: 13–15 (USGS) and 8–9 (historic) per combination.
- Permuted rows break charge balance, because the CBE filter ran before the shuffle. Real rows passed the filter, so failures should be fewer.
- The attribution code runs. On permuted USGS rows, for example, 305 never reach 1 mM Mg, 35 are inside M, and 60 are out on pH only.
- The pure-arm USGS row shows the kill guard working: the base hi is 0.047, the guard hi is 0.105, so the kill is not reported.

## Ways this could be fooled

- **Acid water fills the denominator.** 261 of the 528 USGS rows, and 318 of the 749 historic rows, are below pH 4.5. They can enter only the pH ≥ 3 lenient guard, never window M. So a kill partly measures how common acid-sulfate water is. The attribution table shows how much of the result it accounts for.
- **Equilibrium is not kinetics.** Calcite and sepiolite may lag in a real pool. The generous set and the strict calcite (SI 0.5) cover one side each. Amorphous silica and silicates that are not in the sets are not modelled.
- **No Fe or Al.** Fe(II) counts against vesicles in T4's M-strict. It is absent here, so M_strict is less strict than T4's.
- **Modern air only.** Prebiotic pCO2 was much higher. Higher CO2 would lower the pH and keep more Ca in solution. The open variant is the modern-air case. There is no high-CO2 variant.
- **Pools are not closed boxes.** Mixing, rain refilling and dust are not modelled. Each path is one water drying alone.
- **One park.** All rows are from Yellowstone. The result says nothing about other hot-spring provinces.
- **Sampling is not even.** One area holds 34% (USGS) or 55% (historic) of the rows. The area bootstrap widens the interval but does not reweight.
- **The window edges are lab numbers.** They come from Cary 2024 and Jordan 2019 (via T4) and Milshteyn 2018. Different amphiphile mixtures could move them.

## Decisions at the seal

These choices were made by the project coordinator, not the owner, before `real` ran. None was chosen from an outcome. The one input that leaned on data, the permuted dry run, was not used to pick the primary path.

1. **Primary combination:** spring temperature, closed, as written. Open to air stays in the kill guard and the reported-only table.
2. **Bar:** 5%, as written. A kill means such waters are rare in Yellowstone's sampled thermal waters, not that no pond anywhere could do it.
3. **Historic set:** reported only, as written.
4. **CBE threshold:** 10%, as written.
5. **pH ≥ 3 lenient floor:** kept. It is a judgement based on one observation (Milshteyn 2018, pH 3.3) and is disclosed as such.
6. **Fluorite in the base set:** kept. It helps H, so it makes a kill harder.
7. **Dolomite and magnesite:** excluded, as written. This also makes a kill harder.
8. **Acid rows:** a reported-only share among rows with raw pH ≥ 4.5 was added to `cmd_real`. It uses its own random generator (seed + 7), so no other draw changes. Gate, planted and dryrun outputs were produced by the script before this addition. The addition was smoke-tested on 60 permuted rows (`dryrun 40 20`), and the original dry-run output was restored. It decides nothing.
9. **Not modelled:** Fe, Al and high-CO2 early-Earth air. These are limits of the study.
10. **Runtime:** about 30 minutes on one core under `nice -n 20`, alongside the K6 job that holds the compute lock. It is single-threaded and light.
