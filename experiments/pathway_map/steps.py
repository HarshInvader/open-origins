"""Step tables for four origin-of-life routes (board tasks #4 and #17), in the format the
sealed scorer (experiments/compat/scorer.py, rule v1) reads, plus provenance fields.

Conventions (stated in RESULTS.md; a red team should attack them):
- NaN = a number the source does not give, or that we could not read. INF = a scenario
  feedstock with no stated concentration. "unknown" = a solvent or redox class not stated.
  Checks that depend on any of these are reported as UNASSESSED, never as pass or fail.
- `purified` is applied to non-feedstock inputs (intermediates, ribozymes, primers). A
  scenario feedstock bought as a commercial reagent counts as supplied by the scenario.
- A step's redox class is "reducing" only where the source ran it anoxic (argon sparge, glovebox);
  otherwise "unknown" (bench chemistry in air does not tell us what the step needs), so F8 is unassessed.
- yield_status: demonstrated | demonstrated_purified | missing (no step in the field that we
  know of) | unread (published, but we could not open the source). The scorer is given
  "missing" for unread steps, so no route can be called continuous on an unread step.
- Every number below was read in the source named in the row (section given in `where`).
"""
NAN = float("nan")
INF = float("inf")

STAGES = {
    "S1": "C-C chemistry from feedstocks (sugars, C1-C2 acids)",
    "S2": "nucleotides (activated or cyclic)",
    "S3": "oligomers (non-templated polymerisation)",
    "S4": "template copying / ribozyme polymerase",
    "S5": "sustained replication of the replicator (net > 1 per cycle)",
}

D = dict(
    patel2015="10.1038/nchem.2202",
    ritson2012="10.1038/nchem.1467",
    stairs2017="10.1038/ncomms15270",
    powner2009="10.1038/nature08013",
    caimi2025="10.1021/acscentsci.5c00488",
    simonis2026="10.1177/15311074261427257",
    altair2025="10.1021/jacs.5c01948",
    hudson2020="10.1073/pnas.2002659117",
    matreux2024="10.1038/s41586-024-07193-7",
    gianni2026="10.1126/science.adt2760",
    attwater2025="10.1038/s41557-025-01830-y",
)


def inp(species, conc, purified=False, note=""):
    return dict(species=species, conc=conc, purified=purified, note=note)


def step(id, name, stage, setting, inputs, cond, outs, out_cond=None, yield_status="missing",
         yield_text="none", source=None, where="", tested_with=(), notes="", assumptions=()):
    ph, t, solvent, redox = cond
    oc = out_cond or cond
    return dict(
        id=id, name=name, stage=stage, setting=setting, inputs=inputs, tested_with=list(tested_with),
        conditions=dict(ph=ph, t=t, solvent=solvent, redox=redox),
        outputs=dict(species=outs, ph=oc[0], t=oc[1], solvent=oc[2], redox=oc[3]),
        yield_status=yield_status, yield_text=yield_text, source_doi=source, where=where,
        notes=notes, assumptions=list(assumptions))


def missing(id, name, stage, setting, inputs, outs, notes):
    return step(id, name, stage, setting, [inp(s, NAN) for s in inputs], (NAN, NAN, "unknown", "unknown"),
                {o: NAN for o in outs}, yield_status="missing", yield_text="no published step known to us",
                source=None, notes=notes)


RAIN = dict(ph=7.0, t=23.0, solvent="water", redox="neutral", species={},
            basis="ASSUMED: pure water (Caimi 2025 adds Milli-Q water each cycle as a stand-in for rain); natural rain pH not sourced")

# ---------------------------------------------------------------- scenarios
SCENARIOS = {
    "cyanosulfidic": dict(
        name="cyanosulfidic", t_range=[0, 150], uv=True, redox="reducing",
        settings=["surface_pool", "evaporite"],
        feedstocks={"HCN": INF, "Cu(I)": INF, "HSCN": INF, "cyanoacetylene": INF, "NH3": INF,
                    "phosphate": INF, "H2S": INF, "cyanamide": INF, "urea": INF},
        volatile=["HCN", "NH3", "H2S"],
        streams={"rain": {k: v for k, v in RAIN.items() if k != "basis"}},
        minerals={},
        basis=("Patel 2015 (10.1038/nchem.2202, 'Towards a geochemical scenario', Fig. 2): post-impact surface "
               "streams and pools leaching a thermally metamorphosed evaporite: HCN and NaCN/KCN, CaNCN -> cyanamide, "
               "CaC2 -> acetylene -> cyanoacetylene (Cu-catalysed, >25%), Mg3N2 -> NH3, phosphate from schreibersite/"
               "vivianite, hydrosulfide from metal sulfides, Cu(I) cyanocuprates; solar UV; sequential delivery by flow. "
               "Urea: Patel 2015 calls it a by-product of the cyanamide step. HSCN from HCN + sulfur per Stairs 2017 (10.1038/ncomms15270). Upper T 150 C: the scenario invokes "
               "geothermal/impact heating of dry evaporite; no step here runs above 100 C. Feedstock concentrations "
               "are not stated by the sources (INF). Rain stream pH is our assumption."),
    ),
    "alkaline_vent": dict(
        name="alkaline_vent", t_range=[0, 100], uv=False, redox="reducing",
        settings=["vent_chimney", "porous_rock"],
        feedstocks={"CO2": INF, "H2": INF},
        volatile=["CO2", "H2"],
        streams={
            "vent_fluid": dict(ph=11.0, t=75.0, solvent="water", redox="reducing",
                               species={"Na2S": 0.1, "K2HPO4": 0.01, "Na2Si3O7": 0.01}),
            "ocean": dict(ph=5.7, t=6.0, solvent="water", redox="neutral", species={"Na2Si3O7": 0.01}),
        },
        minerals={},
        basis=("Altair 2025 (10.1021/jacs.5c01948, Tables 1-2): vent-simulant fluid Na2S 100 mM, K2HPO4 10 mM, "
               "Na2Si3O7 10 mM, H2-purged, pH 11, 75 C; ocean simulant Na2Si3O7 10 mM, CO2-purged, pH 5.7, 6 C. "
               "Hudson 2020 (10.1073/pnas.2002659117) uses the same vent fluid (pH 12.3) vs ocean pH 3.9. "
               "Thermophoresis allowed in vent_chimney/porous_rock (rule), cap 1000x (Matreux 2024, "
               "10.1038/s41586-024-07193-7). The ocean stream's redox class (neutral) is our classification."),
    ),
    "warm_pond": dict(
        name="warm_pond", t_range=[0, 100], uv=True, redox="neutral",
        settings=["surface_pool"],
        feedstocks={},
        volatile=[],
        streams={"rain": {k: v for k, v in RAIN.items() if k != "basis"}},
        minerals={},
        basis=("Caimi 2025 (10.1021/acscentsci.5c00488): pond with day-night wet-dry cycles, only water added each "
               "cycle, room temperature, pH set with KOH. Simonis 2026 (10.1177/15311074261427257, abstract only): "
               "Icelandic hot-spring waters (Seltun destructive, Hveradalir benign). Range 0-100 C = liquid water at "
               "the surface (our convention). No nucleotide feedstock is supplied by the pond sources."),
    ),
    "ice_freeze_thaw": dict(
        name="ice_freeze_thaw", t_range=[-10, 80], uv=True, redox="neutral",
        settings=["ice"],
        feedstocks={"Mg2+": INF},
        volatile=[],
        streams={},
        minerals={},
        basis=("Gianni 2026 (10.1126/science.adt2760) and Attwater 2025 (10.1038/s41557-025-01830-y): eutectic ice at "
               "-7 C, pH 9 (CHES-KOH), 0.4 mM MgCl2; Attwater cycles add HCl (to ~pH 3.6), heat to 80 C for 2 min, add "
               "KOH and refreeze. The range -10..80 C is set to the experiments' span; no geological source for this "
               "combination was read by us (Attwater cite a geothermal-ice setting; not checked). Mg2+ concentration "
               "in a natural setting is not stated (INF)."),
    ),
}

# ---------------------------------------------------------------- pathways
CYANO = [
    step("C1", "HCN -> glycolaldehyde and glyceraldehyde (trapped as cyanate oxazolidinones), Cu(I) photoredox",
         "S1", "surface_pool",
         [inp("HCN", NAN, note="13C-KCN; concentration in SI, not read"), inp("Cu(I)", NAN, note="catalytic CuCN")],
         (7.0, NAN, "water", "reducing"),
         {"glycolaldehyde_oxazolidinone": NAN, "glyceraldehyde_oxazolidinone": NAN},
         out_cond=(NAN, NAN, "water", "reducing"),
         yield_status="demonstrated",
         yield_text="oxazolidinone 13 (from glycolaldehyde) ~15% on average per 4 HCN; 14 (from glyceraldehyde) 1-5%; ~30% of HCN lost to a black polymer",
         source=D["ritson2012"], where="main text, 'neutralized by the addition of hydrochloric acid', 254 nm, 7 h; yields paragraph",
         notes=("The sugars are sequestered by cyanate as oxazolidinones; free glycolaldehyde is not the accumulated product. "
                "Temperature and concentrations are in the SI (not read). pH: 'neutralized' (recorded as 7). "
                "Patel 2015 reports an H2S-driven variant that gives the free sugars, but its main text gives no yields for it."),
    ),
    step("C2", "glycolaldehyde + thiocyanic acid -> 2-thiooxazole", "S1", "surface_pool",
         [inp("glycolaldehyde", 0.1, purified=True, note="commercial glycolaldehyde (methods: 1 g, 16.7 mmol)"),
          inp("HSCN", 0.5, note="KSCN + HCl")],
         (0.0, 80.0, "water", "unknown"),
         {"2-thiooxazole": 0.085},
         yield_status="demonstrated_purified", yield_text="85% (isolated)",
         source=D["stairs2017"], where="Results 'Oxazole 4a...'; Methods (glycolaldehyde 1 g, KSCN 3.24 g, water 3 ml, 37% HCl 2.10 ml, RT 2 h then 80 C, 24 h)",
         notes=("pH not reported. From the stated amounts (about 25 mmol HCl in about 5 ml) we calculate pH below 1; recorded as 0 "
                "(a bound, our calculation). Product extracted into ethyl acetate and crystallised; the paper notes 2-thiooxazole "
                "can also crystallise directly from water and sublime."),
         assumptions=["pH 0 is our calculation from reagent amounts, not a measurement"],
    ),
    step("C3", "2-thiooxazole + glyceraldehyde -> pentose oxazolidinone thiones (1a)", "S1", "surface_pool",
         [inp("2-thiooxazole", 0.25, purified=True, note="crystallised 4b"),
          inp("glyceraldehyde", 0.5, purified=True, note="0.5-1 M; commercial")],
         (7.0, 60.0, "water", "unknown"),
         {"thione_1a": 0.185},
         yield_status="demonstrated_purified", yield_text="up to 74% thione 1a in 24 h (70% ribo+arabino 1:1, 30% lyxo/xylo)",
         source=D["stairs2017"], where="Results: 'near neutral pH (pH 4-9)... 60 C... up to 74% thione 1a in 24 h'",
         notes="Works at pH 4-9; sluggish below 6, faster above 7. Recorded at pH 7."),
    step("C4", "thione 1a + cyanoacetylene + ammonia -> arabino- and ribo-aminooxazoline (10a)", "S2", "surface_pool",
         [inp("thione_1a", 0.24, purified=True, note="isolated thione"),
          inp("cyanoacetylene", 0.25), inp("NH3", 1.0, note="as NH4Cl 1 M")],
         (9.0, 25.0, "water", "unknown"),
         {"arabino_aminooxazoline": 0.108, "ribo_aminooxazoline": 0.0792},
         yield_status="demonstrated_purified",
         yield_text=("15-23% 10a per pass from cyanovinyl thione 1b with NH4Cl 1 M at pH 8.5-10.5; 45% arabino + 33% ribo "
                     "over two cyanovinylation/ammonolysis cycles at pH 10.5"),
         source=D["stairs2017"], where="Results 'Aminooxazoline synthesis' (0.24 M 1a, 0.25 M cyanoacetylene, pH 7-10.5; repeated cycles at pH 10.5)",
         notes=("Room temperature (recorded as 25 C). ribo-10a crystallises spontaneously after two cycles. Encoded at pH 9 "
                "(inside the 8.5-10.5 range where a yield is reported) to give the route its most favourable reading; output "
                "concentrations use the two-cycle pH 10.5 yields, which is generous."),
         assumptions=["pH 9 chosen inside the source's 8.5-10.5 range; the 45/33% yield was at pH 10.5"]),
    step("C5", "arabino-aminooxazoline + cyanoacetylene -> 2,2'-anhydrocytidine", "S2", "surface_pool",
         [inp("arabino_aminooxazoline", NAN), inp("cyanoacetylene", NAN), inp("phosphate", NAN)],
         (7.0, NAN, "water", "unknown"),
         {"anhydrocytidine": NAN}, out_cond=(NAN, NAN, "water", "unknown"),
         yield_status="unread", yield_text="published (Powner 2009) but full text paywalled; not read",
         source=D["powner2009"], where="abstract only; conditions from Stairs 2017's description",
         notes=("Stairs 2017 (10.1038/ncomms15270) states this step needs stoichiometric phosphate to keep pH < 7 and stop "
                "hydrolysis of the anhydronucleoside (which hydrolyses readily above pH 6.5). pH recorded as the bound 7."),
         assumptions=["pH 7 is the upper bound '< 7' from Stairs 2017"],
    ),
    step("C6", "anhydrocytidine + phosphate + urea in formamide -> cytidine-2',3'-cyclic phosphate", "S2", "evaporite",
         [inp("anhydrocytidine", 0.05, purified=True, note="ancitabine, commercial; 0.03 mmol in 0.6 ml"),
          inp("phosphate", 0.1, note="NH4H2PO4 0.06 mmol"), inp("urea", 1.0, note="0.6 mmol")],
         (NAN, 100.0, "formamide", "unknown"),
         {"cCMP": 0.022}, out_cond=(NAN, 100.0, "formamide", "unknown"),
         yield_status="demonstrated_purified",
         yield_text="44% (co-phosphorylated with 8,2'-anhydro-adenosine, 34%); formamide, 100 C, 72 h",
         source=D["stairs2017"], where="Results last paragraph ('44% and 34%'); Methods, phosphorylation Method V",
         notes=("pH not stated. Stairs 2017 also notes significant hydrolysis of 11 under urea-mediated phosphorylation. "
                "Powner 2009 phosphorylated by drying an aqueous solution with urea and phosphate (not read)."),
    ),
    step("C7", "UV: cytidine-2',3'-cyclic phosphate -> uridine-2',3'-cyclic phosphate (partial)", "S2", "surface_pool",
         [inp("cCMP", NAN)], (NAN, NAN, "water", "unknown"), {"cUMP": NAN, "cCMP": NAN},
         out_cond=(NAN, NAN, "water", "unknown"),
         yield_status="unread", yield_text="published (Powner 2009, Fig. 5) but full text paywalled; not read",
         source=D["powner2009"], where="abstract and figure titles only; Patel 2015 main text says UV 'partially converts'",
         notes="Patel 2015 (10.1038/nchem.2202) intro: UV partially converts C>p to U>p and destroys stereoisomeric impurities."),
    step("C8", "wet-dry polymerisation of 2',3'-cyclic nucleotides (A, U, G, C) -> RNA oligomers", "S3", "surface_pool",
         [inp("cAMP", 0.0125, True, "BioLog, sodium salt"), inp("cUMP", 0.0125, True, "BioLog"),
          inp("cGMP", 0.0125, True, "BioLog"), inp("cCMP", 0.0125, True, "BioLog")],
         (11.0, 23.0, "water", "unknown"),
         {"RNA_oligomers": 0.018, "RNA_10mer": 0.00005},
         yield_status="demonstrated_purified",
         yield_text="AUGC at pH 11: Y = 36% into oligomers; 6% 4-mer, 0.1% 10-mer (10 cycles)",
         source=D["caimi2025"], where="Abstract; Methods (50 mM total, KOH, 23 C, slow evaporation 8-10 h, water only per cycle)",
         notes="Concentrations are per nucleotide (50 mM equimolar AUGC). RNA_oligomers is in nucleotide equivalents (36% of 50 mM)."),
    missing("C9", "template-directed copying of oligomers under the same conditions", "S4", "surface_pool",
            ["RNA_oligomers"], ["RNA_copies"],
            "Caimi 2025 proposes templated ligation 'under the same pH' as a next step; not shown."),
    missing("C10", "sustained replication of a replicator made from these oligomers", "S5", "surface_pool",
            ["RNA_copies"], ["replicator"], "No source."),
]
CYANO_H = [
    dict(procs=[dict(process="heating", t_after=80.0)],
         why="Glycolaldehyde would have to be released from its oxazolidinone and the pot acidified; no named process does either."),
    dict(procs=[dict(process="selective_separation", species="2-thiooxazole", property="crystallisation",
                     demonstrated_by=D["stairs2017"]), dict(process="drying"),
                dict(process="rehydration", stream="rain", f=0.5, ph_after=6.0),
                dict(process="evaporation", factor=6.0), dict(process="heating", t_after=60.0)],
         why=("Most favourable reading: 2-thiooxazole crystallises from water (Stairs 2017), the crystals are redissolved by "
              "rain (acid left in the mother liquor; pH 6 stated by us, inside the rule's [0, 7] bound), concentrated 6x and "
              "warmed. Glyceraldehyde is still not available as a free sugar.")),
    dict(procs=[dict(process="selective_separation", species="thione_1a", property="crystallisation",
                     demonstrated_by=D["stairs2017"]),
                dict(process="cooling", t_after=25.0), dict(process="gas_exchange", ph_after=9.0)],
         why=("Stairs 2017 crystallised all thione diastereomers (a lab crystallisation, counted as demonstrated; red-team "
              "target). NH3 uptake (gas exchange) raises pH by 2 units to 9 (the rule's cap).")),
    dict(procs=[dict(process="gas_exchange", ph_after=7.0)],
         why="Phosphate-buffered pH < 7 is needed; CO2 uptake (gas exchange) lowers pH by 2 units to 7."),
    dict(procs=[dict(process="drying"), dict(process="transport", to_setting="evaporite", dilution=1.0),
                dict(process="heating", t_after=100.0)],
         why="Drying onto evaporite and heating; the source step runs in formamide, which no listed process supplies."),
    dict(procs=[dict(process="transport", to_setting="surface_pool", dilution=1.0)],
         why="Back to the pool for UV; formamide has to be removed, which no listed process does."),
    dict(procs=[dict(process="same_pot")],
         why="Same pool; purines (cAMP, cGMP) are not made by this route."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
]

VENT = [
    step("V1", "CO2 + H2 -> formate + acetate across Ni-FeS under pH and thermal gradients", "S1", "vent_chimney",
         [inp("CO2", NAN, note="ocean side CO2-purged"), inp("H2", NAN, note="vent side H2-purged")],
         (5.7, 6.0, "water", "reducing"),
         {"formate": 7.359e-4, "acetate": 1.115e-5},
         yield_status="demonstrated",
         yield_text="formic acid 735.9 uM, acetic acid 11.15 uM after 18 h (ocean 6 C pH 5.7 / vent 75 C pH 11, Ni-FeS)",
         source=D["altair2025"], where="Table 2 entry 3 (temperature-gradient 'fuel cell' arrangement)",
         notes=("Engineered set-up: Nafion membrane between compartments, mineral-painted Fe electrodes joined by a wire. "
                "At 25 C (Table 1) FeS2 gave 4.2 uM formic + 2.5 uM acetic acid. Hudson 2020 (10.1073/pnas.2002659117) "
                "microfluidic, pH 12.3/3.9, room temperature: 1.5 uM formate, none without the pH gradient. Conditions recorded "
                "are the ocean side, where product forms."),
    ),
    missing("V2", "formate/acetate -> C2-C3 sugars or aldehydes under vent conditions", "S1", "porous_rock",
            ["formate", "acetate"], ["C2_C3_sugars"], "No vent source in PAPERS.csv or found by us."),
    missing("V3", "-> nucleobases and ribonucleotides under vent conditions", "S2", "porous_rock",
            ["C2_C3_sugars"], ["activated_nucleotides"], "No source."),
    missing("V4", "nucleotide polymerisation in vent pores", "S3", "porous_rock",
            ["activated_nucleotides"], ["RNA_oligomers"],
            "Thermophoresis enriches nucleotides (Matreux 2024) but polymerisation in vent pores is not shown in sources read."),
    missing("V5", "template copying", "S4", "porous_rock", ["RNA_oligomers"], ["RNA_copies"], "No source."),
    missing("V6", "sustained replication", "S5", "porous_rock", ["RNA_copies"], ["replicator"], "No source."),
]
VENT_H = [
    dict(procs=[dict(process="transport", to_setting="porous_rock", dilution=1.0),
                dict(process="thermophoresis", factor=1000.0)],
         why="Thermophoretic enrichment in rock cracks, at the rule's 1000x cap (Matreux 2024)."),
    dict(procs=[dict(process="same_pot")], why="Between missing steps."),
    dict(procs=[dict(process="same_pot")], why="Between missing steps."),
    dict(procs=[dict(process="same_pot")], why="Between missing steps."),
    dict(procs=[dict(process="same_pot")], why="Between missing steps."),
]

POND = [
    missing("P0", "nucleotide synthesis in the pond", "S2", "surface_pool",
            ["nucleotide_precursors"], ["AMP_5", "UMP_5"],
            "The pond sources start from laboratory nucleotides."),
    step("P1", "wet-dry cycling of 5'-AMP / 5'-UMP in hot-spring water -> cyclic mononucleotides, U dimers",
         "S2", "surface_pool",
         [inp("AMP_5", NAN, True, "laboratory nucleotides"), inp("UMP_5", NAN, True, "laboratory nucleotides")],
         (NAN, NAN, "water", "unknown"),
         {"cAMP": NAN, "cUMP": NAN, "UpU": NAN}, out_cond=(NAN, NAN, "water", "unknown"),
         yield_status="unread", yield_text="abstract reports synthesis of cyclic mononucleotides and U dimers; no yield in abstract; full text not opened",
         source=D["simonis2026"], where="abstract (Europe PMC)",
         notes=("Abstract: Seltun (SE) water degraded AMP 95% and UMP 63% over 16 cycles and destroyed ~90% of A10/U10 in 4 "
                "cycles; Hveradalir (HV) water was as benign as nuclease-free water; cyclic mononucleotides formed. Isomer "
                "(2',3' vs 3',5') not stated in the abstract: the cAMP/cUMP outputs here are provisional."),
         assumptions=["cyclic products assumed to be the 2',3' isomers Caimi uses (F4 on cAMP/cUMP marked unassessed)"],
    ),
    step("P2", "wet-dry polymerisation of 2',3'-cyclic nucleotides (A, U, G, C) -> RNA oligomers", "S3", "surface_pool",
         [inp("cAMP", 0.0125, True, "BioLog"), inp("cUMP", 0.0125, True, "BioLog"),
          inp("cGMP", 0.0125, True, "BioLog"), inp("cCMP", 0.0125, True, "BioLog")],
         (11.0, 23.0, "water", "unknown"),
         {"RNA_oligomers": 0.018, "RNA_10mer": 0.00005},
         yield_status="demonstrated_purified",
         yield_text="AUGC at pH 11: Y = 36%; 6% 4-mer, 0.1% 10-mer; G alone up to ~70% at pH 10",
         source=D["caimi2025"], where="Abstract; Table 1; Methods",
         notes="Only water added per cycle. Natural Seltun spring water destroys ~90% of 10-mers in 4 cycles (Simonis 2026 abstract): not scored by the rule."),
    missing("P3", "template-directed copying / ligation at pond pH", "S4", "surface_pool",
            ["RNA_oligomers"], ["RNA_copies"], "Proposed by Caimi 2025; not shown."),
    missing("P4", "sustained replication", "S5", "surface_pool", ["RNA_copies"], ["replicator"], "No source."),
]
POND_H = [
    dict(procs=[dict(process="same_pot")], why="From a missing step."),
    dict(procs=[dict(process="same_pot")],
         why="Same pond. G and C cyclic nucleotides are not made by P1 (only A and U tested); P1's conditions are unread.",
         unassess=[("F4", "cAMP", "isomer not stated in the Simonis abstract"),
                   ("F4", "cUMP", "isomer not stated in the Simonis abstract")]),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
]

ICE = [
    missing("I1", "prebiotic synthesis of trinucleotide triphosphates (pppNNN)", "S2", "ice",
            ["activated_nucleotides"], ["pppNNN"],
            "Both ice papers use triplets prepared in the laboratory; no prebiotic route was in the sources read."),
    missing("I2", "abiotic emergence of a 45-nt polymerase ribozyme (QT45)", "S3", "ice",
            ["pppNNN"], ["QT45_plus"],
            "QT45 was selected from transcribed random pools; abiotic oligomers reach ~10 nt at 0.1% (Caimi 2025)."),
    step("I3", "QT45 copies its complementary strand and itself from triplets in eutectic ice", "S4", "ice",
         [inp("QT45_plus", 8e-8, True, "in vitro transcribed ribozyme, 80 nM"),
          inp("pppNNN", 5e-8, True, "50 nM each triplet; 15 defined or all 64"),
          inp("primer", 8e-9, True, "8 nM primer BCy3P10 (template carries a primer-binding site)"),
          inp("hexamer_pppAUUGAU", 5e-8, True, "needed for full-length (+) synthesis"),
          inp("Mg2+", 4e-4, note="0.4 mM MgCl2")],
         (9.0, -7.0, "water", "unknown"),
         {"QT45_minus": 1.9e-11, "QT45_plus_copy": 1.4e-11},
         yield_status="demonstrated_purified",
         yield_text="(-) strand 0.24% and (+) strand 0.17% of template in 72 days; fidelity 94.1%/nt (64-triplet pool); 10.9% perfect full-length (-), 43.4% perfect (+) with defined triplets",
         source=D["gianni2026"], where="Abstract; Results 'self-synthesis'; Fig. 4 legend (8 nM primer and template, 80 nM ribozyme, 50 nM each substrate, 0.4 mM MgCl2, 1.2 mM KCl, 1 mM CHES-KOH pH 9, 72 days at -7 C)",
         notes=("(-) and (+) syntheses ran in separate tubes; (+) synthesis needed one pre-formed hexamer and one pH-heat-freeze "
                "cycle. Output concentrations = yield x 8 nM template (our arithmetic)."),
    ),
    step("I4", "pH-freeze-thaw cycling: triplet-based exponential replication of short dsRNA by the TPR ribozyme", "S4", "ice",
         [inp("TPR_ribozyme", 2e-8, True, "20 nM triplet polymerase ribozyme (5TU + t1 heterodimer); resupplied at each dilution"),
          inp("pppNNN", 1e-7, True, "100 nM each"), inp("primer", 1e-7, True, "100 nM each primer"),
          inp("short_dsRNA_template", 8e-9, True, "up to 1 pmol per 125 ul"),
          inp("Mg2+", 4e-4, note="0.4 mM MgCl2")],
         (9.0, -7.0, "water", "unknown"),
         {"short_dsRNA_copies": NAN},
         yield_status="demonstrated_purified",
         yield_text="1.2-1.46-fold per cycle for short (+8 to +14 nt) products; 29-nt ribozyme fragment up to 1.26-fold per cycle; A_D duplex 9x (+) and 31x (-) over 21 cycles",
         source=D["attwater2025"], where="Results 'Open-ended RNA amplification', Fig. 3 legend, 'Fragmentary self-replication'; Methods 'Replication cycling'",
         notes=("Each cycle: +0.6 mM HCl, 80 C 2 min, +KOH, flash-freeze in liquid N2, -7 C ~24 h. Freezing concentrates "
                "solutes ~440x. A different ribozyme (TPR) from QT45; the whole replicase is not replicated."),
    ),
    missing("I5", "exponential replication of a whole polymerase ribozyme by itself", "S5", "ice",
            ["QT45_plus", "pppNNN"], ["replicator"],
            "QT45 makes each strand at ~0.2% per 72 days (task #18 in RESULTS.md); the TPR replicates fragments only."),
]
ICE_H = [
    dict(procs=[dict(process="same_pot")], why="Between missing steps."),
    dict(procs=[dict(process="same_pot")], why="From a missing step."),
    dict(procs=[dict(process="same_pot")],
         why="Same ice; Attwater's replicator is a different ribozyme with primers and a template supplied."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
]

PATHWAYS = [
    dict(id="cyanosulfidic", label="Cyanosulfidic (Sutherland/Powner)", scenario="cyanosulfidic", steps=CYANO, handoffs=CYANO_H,
         note=("Encoded via the readable 2-thiooxazole branch (Stairs 2017) because the canonical 2-aminooxazole route "
               "(Powner 2009) is paywalled; Powner steps C5 and C7 are 'unread'. Continues into Caimi 2025 polymerisation, "
               "which is pond chemistry inside the same surface-pool scenario.")),
    dict(id="alkaline_vent", label="Alkaline hydrothermal vent", scenario="alkaline_vent", steps=VENT, handoffs=VENT_H,
         note="Only the first step (CO2 -> formate/acetate) has a published yield."),
    dict(id="warm_pond", label="Warm pond / wet-dry", scenario="warm_pond", steps=POND, handoffs=POND_H,
         note="Absorbs task #17 (Caimi 2025 + Simonis 2026)."),
    dict(id="ice_rna", label="Ice / RNA (QT45, Attwater)", scenario="ice_freeze_thaw", steps=ICE, handoffs=ICE_H,
         note="Only route with demonstrated template copying; every RNA input is supplied purified."),
]
