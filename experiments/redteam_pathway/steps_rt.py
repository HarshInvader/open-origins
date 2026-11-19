"""Red-team (rt-21, board task #21) BLIND re-encoding of the four routes in experiments/pathway_map.

Written from the open full texts without reading the encoded values in experiments/pathway_map/steps.py.
Only the D dict, step ids/names/stages, the helper functions, SCENARIOS and RAIN were read (they are reused
unchanged, so scenario-level choices are NOT re-encoded here). Step names are kept so the diff is per hand-off.

Sources opened (full text, PMC HTML): Ritson 2012 PMC3589744; Stairs 2017 PMC5454461; Caimi 2025 PMC12464751;
Altair 2025 PMC12356197; Matreux 2024 PMC10990939; Gianni 2026 PMC7618777 (author manuscript);
Attwater 2025 PMC12226338; Patel 2015 PMC4568310. Abstract only (PubMed 19444213, 41793254): Powner 2009 and
Simonis 2026 (OpenAlex: closed, no legal open copy found; UCL repository copy is behind a bot challenge, not used).

Conventions (mine; where they differ from the original header they are marked):
- NaN = not given in the main text/methods I read. "RT" (room temperature) is encoded as 22 C and listed in
  `assumptions` (the rule's 10 C tolerance makes 20-25 C equivalent).
- Redox "reducing" only where the source sparged with argon/H2/CO2 (anoxic); otherwise "unknown" (same as orig).
- purified=True for any non-feedstock input taken from a bottle or isolated (same as orig convention).
- A selective_separation is added only where the source names a physical separation for that species;
  `demonstrated_by` only where the source states it happens from the crude mixture. Otherwise none (F6 stands).
- Unread steps: conditions NaN (not imported from secondary descriptions); Stairs' description noted.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pathway_map"))
import steps as ST  # noqa: E402  (only helpers, D, SCENARIOS are used)

NAN, INF, D = ST.NAN, ST.INF, ST.D
inp, step, missing = ST.inp, ST.step, ST.missing
RT = 22.0
SEP_4B = "10.1038/ncomms15270 main text: '4b can purified by crystallization directly from water' (citing refs 27,28; unverified)"

# ---------------------------------------------------------------- cyanosulfidic
CYANO = [
    step("C1", "HCN -> glycolaldehyde and glyceraldehyde (trapped as cyanate oxazolidinones), Cu(I) photoredox",
         "S1", "surface_pool",
         [inp("HCN", NAN, note="13C-KCN; amount only in SI"), inp("Cu(I)", NAN, note="'catalytic copper(I) cyanide'")],
         (7.0, NAN, "water", "reducing"),
         {"glycolaldehyde_oxazolidinone": NAN, "glyceraldehyde_oxazolidinone": NAN, "glycine_nitrile": NAN,
          "HCN_polymer": NAN},
         yield_status="demonstrated", yield_text="13 ~15% (4 HCN per 13); 14 1-5%; ~30% of HCN to black polymer",
         source=D["ritson2012"], where="main text paragraph '13C-labelled potassium cyanide...' and yields paragraph",
         notes="Products are the cyanate-trapped oxazolidinones 13/14, not free sugars. Free-sugar variants (H2S "
               "photoreduction, Ritson & Sutherland 2013) cited by Patel 2015 were not opened (unverified).",
         assumptions=["'neutralized by the addition of hydrochloric acid' encoded as pH 7", "T not stated (NaN)"]),
    step("C2", "glycolaldehyde + thiocyanic acid -> 2-thiooxazole", "S1", "surface_pool",
         [inp("glycolaldehyde", 0.1, purified=True, note="commercial"), inp("HSCN", 0.5)],
         (0.3, 80.0, "water", "unknown"), {"2-thiooxazole": 0.085},
         out_cond=(0.3, RT, "water", "unknown"),
         yield_status="demonstrated_purified", yield_text="85%",
         source=D["stairs2017"], where="Results para 1 (0.1 M glycolaldehyde, 0.5 M HSCN, 85%); Methods (2 h RT then 80 C, 24 h)",
         assumptions=["pH 0.3 DERIVED: -log10(0.5 M HSCN), full dissociation assumed; source says only 'aqueous thiocyanic acid'",
                      "output cooled to RT per Methods"]),
    step("C3", "2-thiooxazole + glyceraldehyde -> pentose oxazolidinone thiones (1a)", "S1", "surface_pool",
         [inp("2-thiooxazole", 0.25, purified=True, note="crystalline 4b dissolved in D2O"),
          inp("glyceraldehyde", 0.5, purified=True, note="0.5-1 M; commercial")],
         (7.0, 60.0, "water", "unknown"), {"thione_1a": 0.185},
         yield_status="demonstrated_purified", yield_text="up to 74% in 24 h (ribo/arabino 70%, 1:1)",
         source=D["stairs2017"], where="Results para 1; Methods (pD 7, 60 C, 24 h, re-adjusted every 6 h)",
         notes="pH 4-9 works; sluggish below 6."),
    step("C4", "thione 1a + cyanoacetylene + ammonia -> arabino- and ribo-aminooxazoline (10a)", "S2", "surface_pool",
         [inp("thione_1a", 0.25, purified=True, note="made from arabinose/ribose (Methods), not from C3"),
          inp("cyanoacetylene", 0.25), inp("NH3", 1.0, note="as NH4Cl 1 M")],
         (10.5, RT, "water", "unknown"),
         {"arabino_aminooxazoline": 0.1125, "ribo_aminooxazoline": 0.0825, "dicyanovinyl_sulfide": NAN},
         yield_status="demonstrated_purified", yield_text="45% arabino + 33% ribo over two cycles at pH 10.5",
         source=D["stairs2017"], where="Results 'We next investigated thione displacement with ammonia' paragraph",
         notes="Single pass pH 8.5-10.5 gives 15-23%; 60% only with 10a co-added (pH 7-10.5).",
         assumptions=["T: cyanovinylation stated at RT; ammonolysis T not stated"]),
    step("C5", "arabino-aminooxazoline + cyanoacetylene -> 2,2'-anhydrocytidine", "S2", "surface_pool",
         [inp("arabino_aminooxazoline", NAN), inp("cyanoacetylene", NAN), inp("phosphate", NAN)],
         (NAN, NAN, "water", "unknown"), {"anhydrocytidine": NAN},
         yield_status="unread", yield_text="Powner 2009 paywalled",
         source=D["powner2009"], where="abstract only (PubMed 19444213)",
         notes="Stairs 2017 describes this step as needing stoichiometric phosphate to hold pH <7, 'pH 3 and 6' range."),
    step("C6", "anhydrocytidine + phosphate + urea in formamide -> cytidine-2',3'-cyclic phosphate", "S2", "evaporite",
         [inp("anhydrocytidine", 0.05, purified=True, note="ancitabine, commercial"),
          inp("phosphate", 0.1, note="NH4H2PO4"), inp("urea", 1.0)],
         (NAN, 100.0, "formamide", "unknown"), {"cytidine_cyclic_phosphate": 0.022},
         yield_status="demonstrated_purified", yield_text="44% (co-phosphorylated with 17A, 34%)",
         source=D["stairs2017"], where="Results last paragraph; Methods phosphorylation Method V (0.03 mmol each in 0.6 ml formamide, 100 C, 72 h)",
         tested_with=["anhydroadenosine_17A"],
         notes="Main text: 11 alone suffers 'significant hydrolysis' under urea-mediated phosphorylation; the 44% was "
               "measured with 17A present. Method I (dry urea melt, 140 C, 20 min) exists but its yield for 11 is in SI only."),
    step("C7", "UV: cytidine-2',3'-cyclic phosphate -> uridine-2',3'-cyclic phosphate (partial)", "S2", "surface_pool",
         [inp("cytidine_cyclic_phosphate", NAN)], (NAN, NAN, "water", "unknown"),
         {"uridine_cyclic_phosphate": NAN, "cytidine_cyclic_phosphate": NAN},
         yield_status="unread", yield_text="Powner 2009 paywalled", source=D["powner2009"],
         where="abstract only"),
    step("C8", "wet-dry polymerisation of 2',3'-cyclic nucleotides (A, U, G, C) -> RNA oligomers", "S3", "surface_pool",
         [inp("cCMP", 0.0125, purified=True), inp("cUMP", 0.0125, purified=True),
          inp("cAMP", 0.0125, purified=True), inp("cGMP", 0.0125, purified=True)],
         (11.0, 23.0, "water", "unknown"), {"RNA_oligomers": 0.018},
         out_cond=(9.0, 23.0, "water", "unknown"),
         yield_status="demonstrated_purified", yield_text="Y = 36% AUGC at pH 11 (cycling)",
         source=D["caimi2025"], where="Results 'Enhanced Polymerization Yield by Wet-Dry Cycles'; Methods (BioLog sodium salts, 50 mM, KOH, open air, 23 C)",
         notes="Single-species runs exist: cCMP 32%, cUMP 25% at pH 11 (n=5).",
         assumptions=["output pH = 11 - ~2 (stated average drop over cycles)", "oligomer conc as nucleotide equivalents 0.36 x 50 mM"]),
    missing("C9", "template-directed copying of oligomers under the same conditions", "S4", "surface_pool",
            ["RNA_oligomers"], ["RNA_copies"], "No source."),
    missing("C10", "sustained replication of a replicator made from these oligomers", "S5", "surface_pool",
            ["RNA_copies"], ["replicator"], "No source."),
]
CYANO_H = [
    dict(procs=[dict(process="uv_irradiation"), dict(process="heating", t_after=80.0)],
         why="C1 pool continues; HSCN is a feedstock. C1 gives oxazolidinone-trapped sugars, not free glycolaldehyde."),
    dict(procs=[dict(process="selective_separation", species="2-thiooxazole", property="crystallisation",
                     demonstrated_by=SEP_4B),
                dict(process="rehydration", stream="rain", f=0.5, ph_after=7.0),
                dict(process="heating", t_after=60.0)],
         why="Crystallise 4b out of the acid (Stairs' stated mechanism), redissolve in rain, heat. Glyceraldehyde has no source."),
    dict(procs=[dict(process="selective_separation", species="thione_1a", property="crystallisation"),
                dict(process="rehydration", stream="rain", f=0.5),
                dict(process="cooling", t_after=RT),
                dict(process="gas_exchange", ph_after=9.0)],
         why="Claimed crystallisation of 1a (Stairs crystallised the diastereomers for X-ray only: W3), redissolve, "
             "NH3 uptake raises pH by the 2-unit gas_exchange limit."),
    dict(procs=[dict(process="same_pot")], why="Into an unread step."),
    dict(procs=[dict(process="transport", to_setting="evaporite", dilution=1.0), dict(process="drying"),
                dict(process="heating", t_after=100.0)],
         why="Dry down with phosphate/urea and heat; no formamide stream exists in the scenario."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5), dict(process="cooling", t_after=RT),
                dict(process="transport", to_setting="surface_pool", dilution=1.0), dict(process="uv_irradiation")],
         why="Into an unread step."),
    dict(procs=[dict(process="evaporation", factor=1.0), dict(process="gas_exchange", ph_after=NAN)],
         why="From an unread step. Purine cyclic nucleotides are never made in this route."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
]
# the gas_exchange with NaN above is a no-op placeholder; replace by same_pot to keep the state honest
CYANO_H[6] = dict(procs=[dict(process="same_pot")], why=CYANO_H[6]["why"])

# ---------------------------------------------------------------- alkaline vent
VENT = [
    step("V1", "CO2 + H2 -> formate + acetate across Ni-FeS under pH and thermal gradients", "S1", "vent_chimney",
         [inp("CO2", NAN, note="CO2-purged ocean simulant, 1 atm"), inp("H2", NAN, note="H2-purged vent simulant")],
         (5.7, 6.0, "water", "reducing"), {"formate": 7.359e-4, "acetate": 1.115e-5},
         yield_status="demonstrated", yield_text="735.9 uM formate, 11.15 uM acetate after 18 h (ocean side)",
         source=D["altair2025"], where="Table 2 entry 3 (ocean CO2 pH 5.7 6 C / vent H2 pH 11 75 C, Ni-FeS)",
         notes="Encoded on the ocean (product) side; vent side is pH 11, 75 C. Final pH not stated.",
         assumptions=["Ni-FeS mineral synthesised in the lab is treated as scenario mineral, not an input"]),
    missing("V2", "formate/acetate -> C2-C3 sugars or aldehydes under vent conditions", "S1", "porous_rock",
            ["formate", "acetate"], ["C2C3_carbonyls"], "No source."),
    missing("V3", "-> nucleobases and ribonucleotides under vent conditions", "S2", "porous_rock",
            ["C2C3_carbonyls"], ["ribonucleotides"], "No source."),
    missing("V4", "nucleotide polymerisation in vent pores", "S3", "porous_rock",
            ["ribonucleotides"], ["RNA_oligomers"], "No source."),
    missing("V5", "template copying", "S4", "porous_rock", ["RNA_oligomers"], ["RNA_copies"], "No source."),
    missing("V6", "sustained replication", "S5", "porous_rock", ["RNA_copies"], ["replicator"], "No source."),
]
VENT_H = [
    dict(procs=[dict(process="transport", to_setting="porous_rock", dilution=1.0),
                dict(process="thermophoresis", factor=2.5)],
         why="Thermophoresis at the factor Matreux 2024 measured in a single chamber (up to 2.5-fold c0); the 1e3-1e4 "
             "figures there are network simulations."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
]

# ---------------------------------------------------------------- warm pond
POND = [
    missing("P0", "nucleotide synthesis in the pond", "S2", "surface_pool", [], ["AMP", "UMP", "GMP", "CMP"],
            "No pond source makes nucleotides."),
    step("P1", "wet-dry cycling of 5'-AMP / 5'-UMP in hot-spring water -> cyclic mononucleotides, U dimers",
         "S2", "surface_pool", [inp("AMP", NAN), inp("UMP", NAN)], (NAN, NAN, "water", "unknown"),
         {"cAMP": NAN, "cUMP": NAN, "U_dimers": NAN},
         yield_status="unread", yield_text="abstract only: cyclic mononucleotides observed, no yield",
         source=D["simonis2026"], where="abstract (PubMed 41793254)",
         notes="2',3' vs 3',5' cyclic not stated in abstract; encoded as the 2',3' species Caimi needs (generous)."),
    step("P2", "wet-dry polymerisation of 2',3'-cyclic nucleotides (A, U, G, C) -> RNA oligomers", "S3", "surface_pool",
         [inp("cAMP", 0.0125, purified=True), inp("cUMP", 0.0125, purified=True),
          inp("cGMP", 0.0125, purified=True), inp("cCMP", 0.0125, purified=True)],
         (11.0, 23.0, "water", "unknown"), {"RNA_oligomers": 0.018}, out_cond=(9.0, 23.0, "water", "unknown"),
         yield_status="demonstrated_purified", yield_text="Y = 36% AUGC at pH 11",
         source=D["caimi2025"], where="as C8"),
    missing("P3", "template-directed copying / ligation at pond pH", "S4", "surface_pool",
            ["RNA_oligomers"], ["RNA_copies"], "No source."),
    missing("P4", "sustained replication", "S5", "surface_pool", ["RNA_copies"], ["replicator"], "No source."),
]
POND_H = [
    dict(procs=[dict(process="same_pot")], why="From a missing step."),
    dict(procs=[dict(process="same_pot")], why="From an unread step; only A and U were cycled."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
]

# ---------------------------------------------------------------- ice
ICE = [
    missing("I1", "prebiotic synthesis of trinucleotide triphosphates (pppNNN)", "S2", "ice", [], ["pppNNN"], "No source."),
    missing("I2", "abiotic emergence of a 45-nt polymerase ribozyme (QT45)", "S3", "ice", ["pppNNN"], ["QT45"], "No source."),
    step("I3", "QT45 copies its complementary strand and itself from triplets in eutectic ice", "S4", "ice",
         [inp("QT45", 8e-8, purified=True), inp("pppNNN", 5e-8, purified=True), inp("primer_BCy3P10", 8e-9, purified=True),
          inp("QT45_template", 8e-9, purified=True), inp("Mg2+", 4e-4)],
         (9.0, -7.0, "water", "unknown"), {"QT45_copies": 1.92e-11},
         yield_status="demonstrated_purified", yield_text="(-) strand 0.24%, (+) strand 0.17% in 72 days",
         source=D["gianni2026"], where="Fig. 4 legend; Results self-synthesis paragraphs",
         notes="(+) strand also needed a pre-formed hexamer pppAUUGAU and one pH-heat-freeze cycle.",
         assumptions=["output conc = 0.24% x 8 nM template"]),
    step("I4", "pH-freeze-thaw cycling: triplet-based exponential replication of short dsRNA by the TPR ribozyme", "S4", "ice",
         [inp("TPR_5TU_t1", 2e-8, purified=True), inp("pppNNN", 1e-7, purified=True), inp("primers", 1e-7, purified=True),
          inp("dsRNA_template", 8e-9, purified=True), inp("Mg2+", 4e-4)],
         (9.0, -7.0, "water", "unknown"), {"dsRNA_copies": NAN},
         yield_status="demonstrated_purified", yield_text="+14-nt duplex: 1.2-1.38x per cycle, plateau 3.5-7x; AD 9x/31x over 21 cycles",
         source=D["attwater2025"], where="Methods 'Replication cycling'; Fig. 3 legend; Results",
         notes="Each cycle adds HCl (pH 3.6, 80 C 2 min), KOH, flash-freeze, -7 C 24 h; serial dilution into fresh "
               "ribozyme+triplets every 4-5 cycles. The ice scenario has no stream to supply these."),
    missing("I5", "exponential replication of a whole polymerase ribozyme by itself", "S5", "ice",
            ["dsRNA_copies"], ["replicator"], "No source."),
]
ICE_H = [
    dict(procs=[dict(process="same_pot")], why="Missing to missing."),
    dict(procs=[dict(process="freezing_eutectic", t_after=-7.0, factor=1.0)], why="From a missing step into ice."),
    dict(procs=[dict(process="heating", t_after=80.0), dict(process="freezing_eutectic", t_after=-7.0, factor=1.0)],
         why="Same ice; Attwater's TPR is a different ribozyme; pH cycling needs HCl/KOH the scenario lacks."),
    dict(procs=[dict(process="same_pot")], why="Into a missing step."),
]

PATHWAYS = [
    dict(id="cyanosulfidic", scenario="cyanosulfidic", steps=CYANO, handoffs=CYANO_H),
    dict(id="alkaline_vent", scenario="alkaline_vent", steps=VENT, handoffs=VENT_H),
    dict(id="warm_pond", scenario="warm_pond", steps=POND, handoffs=POND_H),
    dict(id="ice_rna", scenario="ice_freeze_thaw", steps=ICE, handoffs=ICE_H),
]
