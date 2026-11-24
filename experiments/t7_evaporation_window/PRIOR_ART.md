# T7 prior art: has anyone evaporated real spring water against the vesicle and RNA windows?

Written 2026-11-24, before any field evaporation path was computed. Searches: Europe PMC REST (full-text search and `fullTextXML`), Crossref and the arXiv API, User-Agent `open-research-site/1.0`, no personal data in any request. Downloads are in `raw/lit/` and are untrusted. They were read with `python3 -I` helpers (`scripts/xml2txt.py`, and a keyword-in-context reader). Papers already opened for T4 are cited from `../t4_vesicle_rna_window/raw/lit/`.

## Verdict

**Not settled. The test is worth building.**

- Several groups model or measure evaporation for prebiotic chemistry. All of them are about phosphate, cyanide or salt, or about soda lakes as a class.
- None takes a database of real spring waters along a mineral-saturation evaporation path and asks whether Mg reaches about 1 mM while Ca, salt and pH are still inside a fatty-acid vesicle window.
- The hot-spring papers (Damer & Deamer 2020, Milshteyn 2018, Cary 2024) treat evaporation as linear concentration, in words or one-line arithmetic, with no mineral precipitation.
- The soda-lake papers (Toner & Catling 2020, Cohen 2024, Tutolo 2024, Haas 2024) show that carbonate precipitation strips Ca. That is the mechanism that could open the window. But they apply it to closed-basin lakes, not hot springs, and never test the joint window along a path.

## Sources opened, with the claim each supports

**Toner & Catling 2020**, PNAS, doi:10.1073/pnas.1916109117 (`raw/lit/PMC6969521.txt`). Evaporation removes Ca and Mg from carbonate waters, and a PHREEQC model is used.
- "Upon evaporation of these fluids, Ca 2+ and Mg 2+ ions precipitate as carbonates and silicates, and the residual carbonate alkalinity concentrates as Na–HCO 3 –CO 3 -rich brine"
- "we use the phreeqc.dat database in the geochemical program PHREEQC"
- They name the membrane problem without testing it: "A difficulty for an origin of life in saline lakes is that high salt concentrations tend to destabilize lipid vesicles ( 56 ) and inhibit RNA oligimerization ( 57 ), but these issues are potentially resolvable."

**Cohen et al. 2024**, PNAS Nexus, doi:10.1093/pnasnexus/pgae084 (`../t4_vesicle_rna_window/raw/lit/PMC10949909.txt`). Two evaporated soda lakes, measured. No path model and no hot springs.
- "Because we sampled after seasonal evaporation, the lake water contained ∼1 M Na + and ∼1 mM Mg 2+ near pH 10."
- "High concentrations of activated nucleotides could have been achieved through the evaporation of shallow soda lakes on the early Earth, while maintaining ∼1 mM divalent cations because of the poor solubility of Mg-containing carbonates"
- "Continued evaporation yields sodium concentrations above ∼1 M where vesicles flocculate despite the presence of additional compounds."

**Cary et al. 2024**, Life, doi:10.3390/life14030415 (`../t4_vesicle_rna_window/raw/lit/PMC10971489.txt`). Evaporation raises cations in hot-spring pools. This is stated, not modelled.
- "Hot springs are affected by precipitation and evaporation cycles, which contribute to natural variability in the concentration of cations in the same pool over time as water volumes change. A potential outcome is that cation concentrations increase in pools during evaporation."
- "Mass flocculation of lipid vesicles occurs beyond ~1.9 mM of Ca, Fe, and Mg cations in this study, while natural settings on Earth are observed to be <0.7 mM"

**Damer & Deamer 2020**, Astrobiology, doi:10.1089/ast.2019.2045 (`../t4_vesicle_rna_window/raw/lit/PMC7133448.txt`). A linear statement, with no minerals.
- "As evaporation occurs during a wet-dry cycle, the initial modest concentrations of the various ionic solutes of hydrothermal fields increase a 100-fold or more as most of the water is lost to the atmosphere."

**Milshteyn et al. 2018**, Life, doi:10.3390/life8020011 (`../t4_vesicle_rna_window/raw/lit/PMC6027054.txt`). Linear arithmetic for one spring. Also the low-pH vesicle observation used for T7's lenient pH floor.
- "if the Mammoth Hot Spring water undergoes drying, the 27 mM ionic solutes pass through a concentration equivalent to ~2 molar when 99% of the water has evaporated."
- "Dodecanoic acid (12-carbon lauric acid) formed membranous vesicles at pH 3.3 and pH 7.9"
- Table 3 seawater (used in the gate): "Na 469 mM Ca 10 mM Mg 53 mM K 10 mM HCO 3 2 mM SO 4 28 mM SiO 2 0".

**Tutolo et al. 2024**, Life, doi:10.3390/life14121624 (`raw/lit/PMC11678467.txt`). Field data, geophysics and hydrology for two soda lakes. The window is raised but not tested.
- "the evaporation processes that yield elevated phosphate concentrations also increase the concentration of many other solutes. While this elevated salinity can drive condensation and polymerization reactions through its effect on water activity [ 11 ], it may inhibit the formation of some lipid membranes"
- "Recent work suggests that alkaline lake waters are permissive of RNA and cell membrane functionality, although only after adjustments to pH and/or freshening events [ 26 ]."

**Walton et al. 2025**, Science Advances, doi:10.1126/sciadv.adq0027 (`raw/lit/PMC11837993.txt`). A steady-state phosphate budget for closed basins, with no ion-window modelling. Its sink rule depends on divalent cations:
- "the onset of abiotic sinks, which is largely determined by how concentrated in carbonate and depleted in divalent cations the lake is"

**Haas et al. 2024**, Communications Earth & Environment, doi:10.1038/s43247-023-01192-8 (`raw/lit/haas2024.txt`, publisher OA page). Calcite removes Ca early on evaporation of basalt-derived water:
- "Plagioclase weathering produces Na–HCO 3 –CO 3 dominated water chemistry from which calcite precipitates early and completely upon evaporation"

**Getenet et al. 2022**, Crystal Growth & Design, doi:10.1021/acs.cgd.1c01391 (`raw/lit/PMC8991015.txt`). A published PHREEQC + Pitzer evaporation path with a measured start composition (Lake Magadi). **Used as the T7 gate.**
- "The PHREEQC version 3.4 code with the Pitzer database was used for thermodynamic hydrochemical speciation, evaporation, and precipitation calculations."
- "trona was predicted to precipitate first at a CF of 9.7"; "Nahcolite is predicted to precipitate for a short period between CFs of 6.2 and 16.4"; "halite which starts forming at a CF of 32"; "Amorphous silica supersaturates at a CF of 3"; "At a CF of 8.6, calcite starts dissolving and gaylussite begins to form until a CF of 11.5. Pirssonite came to equilibrium with the solution after a CF of 11.5"; "Initially, pH decreases slightly from 9.8 to 9.4 until a CF of 6.4"

**Gharsalli et al. 2026**, Frontiers in Microbiology, doi:10.3389/fmicb.2026.1843317 (`raw/lit/PMC13712413.txt`). Field seawater evaporation sequence in a saltern. **Used for the gate bounds.**
- "calcium concentrations maintain a linear relationship with the potassium-based concentration factor (FC) until reaching approximately five times the initial seawater concentration. Subsequently, as gypsum precipitation intensifies (FC = 5–8), calcium levels decline sharply"
- "halite formation starts around FC ≈ 11"

**Opened and not relevant to the question:**
- Mulkidjanian et al. 2025, doi:10.3390/life15030399 (`raw/lit/PMC11943819.txt`): vapour-condensate pools and Zn/K. No evaporation path against a vesicle window.
- Ross & Deamer 2023, doi:10.3390/life13081749 (`raw/lit/PMC10456050.txt`): wet-dry replication chemistry.
- Subbotin et al. 2026, doi:10.3390/life16040542 (`raw/lit/PMC13117335.txt`): liposomes in craters. Evaporation is mentioned only in a list of settings.

**Found but not opened (paywalled or no OA copy found):**
- Deamer, Damer & Kompanichenko 2019, doi:10.1089/ast.2018.1979 (the spring list behind Cary's "<0.7 mM").
- Toner & Catling 2019, GCA, doi:10.1016/j.gca.2019.06.031 (cyanide in alkaline lakes, evaporation-modelled).
- Gangidine et al. 2020, doi:10.3390/life10010003 (silica precipitation in a wet-dry hot-spring chamber; the publisher returned 403 and Europe PMC returned 500).
- Walton, White & Rimmer 2026, doi:10.1177/15311074261435780 (chemical fluxes; not OA).

None of these is cited for a claim.

## What T7 adds

The first stepwise, mineral-saturation evaporation of a full database of real hot-spring waters, scored against T4's vesicle windows and the R1 RNA minimum, with the kill and support rules fixed before any field path is computed. The mechanism Toner & Catling and Cohen describe for soda lakes is that carbonate removes Ca while Mg stays in solution. T7 asks whether Yellowstone spring water follows that route.
