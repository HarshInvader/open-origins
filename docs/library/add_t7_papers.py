"""One-off: add the library entries for the papers read for T7 (2026-11-24), and T7 notes on papers already in the library."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text())
L = d["papers"]
by = {e["id"]: e for e in L}
TODAY = "2026-11-24"
T7 = "T7 (inconclusive, see experiments/t7_evaporation_window/T7_RESULTS.md)"

def base(**k):
    e = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
         "added": TODAY, "date": TODAY, "relevance": "useful"}
    e.update(k)
    return e

new = [
    base(id="getenet-2022-magadi-evaporation",
         title="A Comprehensive Methodology for Monitoring Evaporitic Mineral Precipitation and Hydrochemical Evolution of Saline Lakes: The Case of Lake Magadi Soda Brine (East African Rift Valley, Kenya)",
         authors="Getenet M, García-Ruiz JM, Otálora F, Emmerling F, Al-Sabbagh D, Verdugo-Escamilla C",
         year=2022, venue="Crystal Growth & Design 22:2307-2317", doi="10.1021/acs.cgd.1c01391",
         url="https://doi.org/10.1021/acs.cgd.1c01391", topic="Vents and first cells", read_depth="full",
         question="In what order do minerals precipitate as Lake Magadi soda brine evaporates, and how does the brine chemistry change along the way?",
         tried="Evaporate Lake Magadi brine in acoustically levitated droplets watched by video microscopy and synchrotron X-ray diffraction, characterise the minerals ex situ, and compare with a thermodynamic evaporation model.",
         method_data="In situ video microscopy and synchrotron XRD of levitated droplets; ex situ Raman, XRD and SEM; PHREEQC 3.4 with the Pitzer database for speciation, evaporation and precipitation, starting from a measured brine (Table 1).",
         key_results="Model path by concentration factor (CF): amorphous silica supersaturates at CF 3; nahcolite precipitates between CF 6.2 and 16.4; calcite starts dissolving and gaylussite forms at CF 8.6 until 11.5, then pirssonite; trona first at CF 9.7; halite from CF 32. pH falls slightly from 9.8 to 9.4 up to CF 6.4. Alkaline-earth carbonates and fluorite are predicted first, then siliceous sediments; halite/villiaumite, thermonatrite and sylvite follow trona. The experiments reproduce the mineral assemblages seen in the lake.",
         limits="One brine from one lake. The authors note that predicted and measured sulfate and phosphate disagree, which they read as biological cycling. Sylvite and glaserite are predicted near complete dryness but not reported in the basin.",
         ideas_for_us=T7 + ": the gate. T7 reran this published PHREEQC + Pitzer path from the Table 1 brine and had to match it within a factor of 1.3: nahcolite onset CF 6.25 (published 6.2), trona 9.70 (9.7), halite 28.0 (32), amorphous silica 3.08 (3.0), and the small pH drop; 5 of 5 checks passed.",
         touches=[], source_opened="full text (PMC8991015, CC BY)"),
    base(id="gharsalli-2026-sfax-saltern-halite",
         title="Halite crystallization at Sfax solar salterns, Tunisia, driven by brine geochemistry and biogeochemical interactions",
         authors="Gharsalli N, Mhiri N, Yaich C, Karray F",
         year=2026, venue="Frontiers in Microbiology 17:1843317", doi="10.3389/fmicb.2026.1843317",
         url="https://doi.org/10.3389/fmicb.2026.1843317", topic="Vents and first cells", read_depth="full",
         question="How do brine geochemistry and halophilic microbes shape halite crystallisation along the evaporation gradient of a seawater-fed saltern?",
         tried="Analyse 26 brines along the Sfax saltern gradient, isolate halophilic archaea from three basins, and run crystallisation experiments with increasing biomass inoculum against abiotic controls.",
         method_data="Major-ion geochemistry of 26 brine samples (mean salinity about 28-570 g/L); enrichment cultures from surface and bottom brines; controlled halite crystallisation with 25-75% inoculum.",
         key_results="The brines follow a marine evaporation sequence. Calcium rises linearly with the potassium-based concentration factor (FC) to about 5 times seawater, then falls sharply as gypsum precipitation intensifies (FC 5-8). Halite starts forming around FC 11. Three Halorubrum species were isolated from cultures tolerating up to 280 g/L; surface-brine cultures gave 5.550 +/- 0.127 g of halite-dominated precipitate after 10 days at 25% inoculum.",
         limits="One saltern, a field sequence rather than a controlled evaporation. The concentration factor is based on potassium. Most of the paper is about microbes and crystal form, not the ion path.",
         ideas_for_us=T7 + ": the halite bound in the seawater gate. T7's check G3 (halite onset CF between 9.5 and 13.0) brackets this field value; T7 got 11.10.",
         touches=[], source_opened="full text (PMC13712413, CC BY)"),
    base(id="toner-catling-2020-carbonate-lake-phosphate",
         title="A carbonate-rich lake solution to the phosphate problem of the origin of life",
         authors="Toner JD, Catling DC",
         year=2020, venue="PNAS 117:883-888", doi="10.1073/pnas.1916109117",
         url="https://doi.org/10.1073/pnas.1916109117", topic="Building blocks", read_depth="full",
         question="Can carbonate-rich lakes hold the high phosphate levels that prebiotic syntheses use, when most natural waters lose phosphate to apatite?",
         tried="Model evaporation and steady-state inflow of carbonate-rich waters with PHREEQC, tracking how calcium is taken up in carbonates instead of apatite.",
         method_data="PHREEQC with the phreeqc.dat database; evaporation and steady-state lake models; comparison with measured phosphate in carbonate-rich lakes (Fig. 1).",
         key_results="Modern carbonate-rich lakes could hold up to about 0.1 molal phosphate at steady state with evaporation and inflow, because calcium is locked in carbonates. Evaporation without inflow can reach more than 1 molal. On evaporation, Ca and Mg precipitate as carbonates and silicates and the brine becomes Na-HCO3-CO3 rich. Under early CO2-rich air the brines would be buffered to pH 6.5-9.",
         limits="About phosphate, not membranes or RNA. The authors name the problem that high salt destabilises lipid vesicles and inhibits RNA oligomerisation, and call it potentially resolvable without testing it.",
         ideas_for_us=T7 + ": the mechanism T7 asks about (carbonate strips Ca on evaporation). T7 applies it to Yellowstone spring waters and scores the path against the vesicle and RNA windows, which this paper does not do.",
         touches=[], source_opened="full text (PMC6969521, CC BY-NC-ND)"),
    base(id="haas-2024-last-chance-lake-phosphate",
         title="Biogeochemical explanations for the world's most phosphate-rich lake, an origin-of-life analog",
         authors="Haas S, Sinclair KP, Catling DC",
         year=2024, venue="Communications Earth & Environment 5:28", doi="10.1038/s43247-023-01192-8",
         url="https://doi.org/10.1038/s43247-023-01192-8", topic="Building blocks", read_depth="full",
         question="Why does Last Chance Lake hold so much dissolved phosphate?",
         tried="Test explanations by studying phosphorus and nitrogen cycling in Last Chance Lake and Goodenough Lake, Canada: sediment mineralogy, phosphorus sinks and N2-fixation rates.",
         method_data="Field sampling of water and sediment in two soda lakes; sediment calcium mineralogy; N2-fixation measurements.",
         key_results="No geochemical phosphorus precipitation was found; sedimentary calcium is in dolomite rather than apatite; N2 fixation, probably suppressed by high salinity, is too low to create much biological phosphate demand. Last Chance Lake reaches 37 mM phosphate, the highest known natural level. Plagioclase weathering gives Na-HCO3-CO3 water from which calcite precipitates early and completely on evaporation.",
         limits="Two modern lakes on basalt. About phosphate, not membranes or RNA copying.",
         ideas_for_us=T7 + ": prior art for calcite removing Ca early on evaporation of basalt-derived water. T7 tests whether the same route works for hot-spring water and still leaves the vesicle window open.",
         touches=[], source_opened="full text (publisher open-access page)"),
    base(id="tutolo-2024-groundwater-alkaline-lakes",
         title="Groundwater-Driven Evolution of Prebiotic Alkaline Lake Environments",
         authors="Tutolo BM, Perrin R, Lauer R, Bossaer S, Tosca NJ, Hutchings A, Sevgen S, Nightingale M, Ilg D, Mott EB, Wilson T",
         year=2024, venue="Life 14:1624", doi="10.3390/life14121624",
         url="https://doi.org/10.3390/life14121624", topic="Vents and first cells", read_depth="full",
         question="How do physical processes (evaporation, groundwater inflow, mixing) drive the chemistry of prebiotic alkaline lakes?",
         tried="Study the neighbouring Last Chance and Goodenough Lakes, British Columbia, with near-surface geophysics, aqueous geochemistry and hydrogeologic modelling.",
         method_data="Near-surface geophysics, water chemistry and hydrogeologic models of two small alkaline lakes with contrasting evaporation.",
         key_results="Extreme phosphate enrichment needs a lake that is geomorphologically prone to evaporation. The density contrast between evaporated brines and inflowing groundwater drives Rayleigh-Taylor instabilities and vigorous surface-subsurface mixing, which the authors offer as a way to reconcile conflicting needs of UV light, salinity, metals and pH.",
         limits="Two lakes. The authors note that the evaporation that raises phosphate also raises other solutes and may inhibit some lipid membranes, but they do not test a vesicle or RNA window.",
         ideas_for_us=T7 + ": prior art. It raises the salt-versus-membrane conflict for evaporating lakes; T7 tests that conflict along modelled paths for hot-spring water.",
         touches=[], source_opened="full text (PMC11678467, CC BY)"),
    base(id="walton-2025-closed-basin-phosphate",
         title="Large closed-basin lakes sustainably supplied phosphate during the origins of life",
         authors="Walton CR, Hao J, Schönbächler M, Shorttle O",
         year=2025, venue="Science Advances 11:eadq0027", doi="10.1126/sciadv.adq0027",
         url="https://doi.org/10.1126/sciadv.adq0027", topic="Building blocks", read_depth="full",
         question="Could closed-basin lakes keep high phosphate at steady state while phosphate is being used up?",
         tried="Build a steady-state phosphate budget for closed-basin lakes, with Mono Lake, California, as the case study, and compare lake classes by size and inflow.",
         method_data="Steady-state P budget with inflow, recycling and abiotic sinks; modern lake data.",
         key_results="Mono Lake keeps just below 1 mM dissolved phosphate through the year, well mixed, while supporting productivity of about 100 mM C per m2 per day. Smaller closed basins can swing from about 1 mM to orders of magnitude lower with the seasons. When abiotic sinks start depends largely on how carbonate-rich and divalent-cation-poor the lake is.",
         limits="A phosphate budget only; no ion-window or membrane modelling.",
         ideas_for_us=T7 + ": prior art. Its sink rule depends on divalent cations, the same ions T7 tracks, but it does not follow an evaporation path against a vesicle window.",
         touches=[], source_opened="full text (PMC11837993, CC BY)"),
    base(id="mulkidjanian-2025-zinc-potassium-geothermal",
         title="Origin of the RNA World in Cold Hadean Geothermal Fields Enriched in Zinc and Potassium: Abiogenesis as a Positive Fallout from the Moon-Forming Impact?",
         authors="Mulkidjanian AY, Dibrova DV, Bychkov AY",
         year=2025, venue="Life 15:399", doi="10.3390/life15030399",
         url="https://doi.org/10.3390/life15030399", topic="RNA world", read_depth="full", relevance="background",
         question="Could fallout of zinc and potassium after the Moon-forming impact have made Hadean geothermal fields where RNA-like molecules arose?",
         tried="Estimate the moderately volatile elements that fell onto the early protocrust after the impact and argue how geothermal fluids venting through that layer would make organics.",
         method_data="Calculations of moderately volatile element fallout and a reasoned scenario for vapour-condensate pools.",
         key_results="The authors calculate that the top layer of the protocrust could have held up to 10^19 kg of metallic zinc. They propose that pools of geothermal vapour condensate selected low-volatile, mineral-affine, radiation-resistant, nitrogen-rich, polymerisable molecules.",
         limits="A hypothesis paper. It does not model an evaporation path against a vesicle window.",
         ideas_for_us=T7 + ": opened during the prior-art search and found not relevant; not cited for any claim.",
         touches=[], source_opened="full text (PMC11943819, CC BY)"),
    base(id="subbotin-2026-liposome-craters",
         title="Experimental and Numerical Modeling of Liposome Congregation in Meteorite Craters of Early Earth",
         authors="Subbotin VM, Turner BA, Davies BA, Lopez AG, Fiksel G",
         year=2026, venue="Life 16:542", doi="10.3390/life16040542",
         url="https://doi.org/10.3390/life16040542", topic="Vents and first cells", read_depth="full", relevance="background",
         question="Could gravity and earthquakes gather liposomes on the floors of early-Earth meteorite craters?",
         tried="Build a model crater that undergoes sudden, repetitive displacements matched to earthquake ground motion, and simulate the same numerically, to see whether liposome-sized particles collect at the crater floor.",
         method_data="Bench crater with a spherical-cap shape (sphere radius 200 mm), displacements and velocities matched to earthquake data; numerical simulations with 350 um particles.",
         key_results="The experiments and simulations show particles gathering at the floor of a bowl-shaped crater, especially with periodic seismic disturbance.",
         limits="The simulations use 350 um particles; the authors note that realistic 350 nm liposomes would take about six orders of magnitude longer, and fluid motion is not included.",
         ideas_for_us=T7 + ": opened during the prior-art search and found not relevant (evaporation appears only in a list of settings); not cited for any claim.",
         touches=[], source_opened="full text (PMC13117335, CC BY)"),
]
for e in new:
    if e["id"] in by:
        by[e["id"]].update(e)
    else:
        L.append(e)

notes = {
    "damer-deamer-2020-hot-spring-hypothesis": " " + T7 + ": the linear 100-fold drying statement that T7 replaces with a mineral-saturation evaporation path. Followed that way, Yellowstone waters seldom reach both windows (2.8% of USGS rows on the primary path, 99% interval 0.3-9.4%).",
    "milshteyn-2018-vesicles-hot-spring-water": " " + T7 + ": source of the pH 3.0 floor on the lenient windows (vesicles at pH 3.3) and of the Table 3 seawater used in the gate.",
    "cary-2024-life-on-mars-protocells": " " + T7 + ": source of the 1.9 mM calcium limit in the vesicle window, and of the statement that evaporation raises cations in pools, which T7 models with mineral precipitation.",
    "cohen-2024-soda-lakes-rna-membranes": " " + T7 + ": the soda-lake route (carbonate removes Ca while about 1 mM Mg stays) that T7 tests on Yellowstone spring water. It works for only a few percent of waters, mostly near-neutral to alkaline and Mg-rich, Na-poor ones.",
}
for k, v in notes.items():
    e = by[k]
    if "T7 (" not in e["ideas_for_us"]:
        e["ideas_for_us"] = e["ideas_for_us"] + v
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
print(len(L))
