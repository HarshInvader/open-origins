"""Blind encoding (agent enc-B, board task #29) of six published prebiotic RNA-precursor routes
as step tables for the sealed compatibility rule (docs/prereg/compatibility_rule.md, rule v1).

Format and conventions: experiments/pathway_map/steps.py (read-only import).
NaN = not reported (or only in an SI we could not open); INF = scenario feedstock with no stated concentration.
Routes: R6 Becker 2018, R7 Becker 2019, R8 Xu 2020, R9 Yi 2020, R10 Ritson 2022, R11 Gibard 2018.
Nothing here has been scored. Ambiguities are listed per route in NOTES.md.

`purified` convention (see NOTES.md): True for any input that was isolated, crystallised or synthesised
and then used as a clean sample, and for commercial non-feedstock reagents. A commercial reagent that the
authors themselves claim as a scenario feedstock follows the steps.py convention (counts as supplied by the
scenario, purified=False).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pathway_map"))
import steps as ST  # noqa: E402

NAN, INF, inp, step = ST.NAN, ST.INF, ST.inp, ST.step

D = dict(
    becker2018="10.1038/s41467-017-02639-1",   # PMC5765019, full text read (SI not obtainable)
    becker2019="10.1126/science.aax2747",      # LMU repository submitted manuscript + SI, read in full
    xu2020="10.1038/s41586-020-2330-9",        # PMC7116818, full text read (SI not obtainable)
    yi2020="10.1073/pnas.1922139117",          # PMC7306801, full text read (SI not read)
    ritson2022="10.1021/jacs.2c07774",         # PMC9619408, full text read (SI not read)
    gibard2018="10.1038/nchem.2878",           # PMC6295206 accepted manuscript, read (SI not obtainable)
    islam2017="10.1038/nchem.2703",            # cited inside Ritson 2022 only; NOT opened
)

RT = 23.0  # 'room temperature' in the sources; 23 C is our stated assumption (same convention as steps_dsm.py)


def _rain(note):
    return dict(ph=7.0, t=RT, solvent="water", redox="neutral", species={}, basis=note)


RAIN_NOTE = "ASSUMED: pure water at pH 7, 23 C. The source gives no rain composition."

# ------------------------------------------------------------------ scenarios
SCENARIOS = {
    "becker2018_geothermal": dict(
        name="becker2018_geothermal", t_range=[0, 160], uv=False, redox="neutral",
        settings=["geothermal_field"],
        feedstocks={s: INF for s in ["malononitrile", "amidinium", "nitrite", "acetic_acid", "formic_acid", "Ni0",
                                     "Fe0", "ribose", "methylamine", "dimethylamine"]},
        volatile=[],
        streams={
            "rain": {k: v for k, v in _rain(RAIN_NOTE).items() if k != "basis"},
            "carbonate_water": dict(ph=10.0, t=RT, solvent="water", redox="neutral", species={}),
        },
        minerals={},
        basis=("Becker 2018 (10.1038/s41467-017-02639-1) Fig. 1 legend, Discussion: geothermal fields with wet-dry "
               "cycles; starting materials produced from a prebiotic atmosphere and washed in by rain; formic acid, "
               "acetic acid, sodium nitrite, malononitrile, amidinium compounds, elemental Ni or Fe (Discussion); "
               "ribose formed elsewhere and washed in by rain or flooding (Results, last section); amines optional "
               "(Results 'Diversification'). Soil heating to 110-160 C by volcanic activity or sunlight on dark "
               "surfaces (Results 'Nitroso-pyrimidine formation'): range 0-160 C. No UV claimed. No concentrations "
               "stated for any feedstock (INF). Redox 'neutral' is our label (N2/CO2-type setting; not stated). "
               "Rain pH 7 is ASSUMED. 'carbonate_water' pH 10 is from 'slightly basic conditions (pH ~9-10)' "
               "(Results 'Formamidopyrimidine formation'); its T is ASSUMED. The authors draw several rivers/environments; "
               "we use one setting (see NOTES.md)."),
    ),
    "becker2019_geothermal": dict(
        name="becker2019_geothermal", t_range=[0, 100], uv=False, redox="neutral",
        settings=["geothermal_basin"],
        feedstocks={s: INF for s in ["cyanoacetylene", "hydroxyurea", "urea", "Zn2+", "Co2+", "carbonate",
                                     "boric_acid", "ribose", "Fe2+", "FeS2", "DTT", "luneburgite", "NH3",
                                     "nitrite", "bisulfite", "malononitrile", "amidinium", "formic_acid", "Zn0"]},
        volatile=[],
        streams={
            "acid_rain": dict(ph=3.0, t=25.0, solvent="water", redox="neutral", species={}),
            "carbonate_water": dict(ph=10.0, t=25.0, solvent="water", redox="neutral", species={}),
            "rain": {k: v for k, v in _rain(RAIN_NOTE).items() if k != "basis"},
        },
        minerals={},
        basis=("Becker 2019 (10.1126/science.aax2747; LMU submitted manuscript) Discussion and Fig. 5B: surface or "
               "geothermal basins with one or two streams, wet-dry cycles, elevated temperature (95-100 C used), "
               "pH fluctuating between ~3 (acid rain from SO2/NOx) and ~10 (carbonates); cyanoacetylene from surface "
               "hydrothermal vents (their ref 13); hydroxyurea from hydroxylamine + cyanate; hydroxylamine from "
               "nitrite + bisulfite; Zn2+/Co2+, Fe2+, FeS/pyrite, borate and phosphate minerals (lueneburgite, struvite, "
               "colemanite, hydroxyapatite); urea by rain. Early atmosphere N2/CO2 (Intro) -> redox 'neutral' is our label. "
               "'acid_rain' pH 3 and 'carbonate_water' pH 10 are the authors' stated pH extremes; stream T 25 C is ASSUMED. "
               "'rain' pH 7 is ASSUMED. DTT is not claimed as prebiotic by the authors (they state any thiol works); it is "
               "listed as a feedstock only because the authors run the headline one-pot with it (see NOTES.md). No "
               "feedstock concentrations stated (INF). UV not claimed."),
    ),
    "xu2020_cyanosulfidic": dict(
        name="xu2020_cyanosulfidic", t_range=[0, 150], uv=True, redox="reducing",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["adenine", "ammonium_thiocyanate", "thiourea", "bisulfite", "hydrosulfide",
                                     "phosphate", "Mg2+"]},
        volatile=[],
        streams={
            "rain": {k: v for k, v in _rain(RAIN_NOTE).items() if k != "basis"},
            "atmospheric_nitrous_acid": dict(ph=4.0, t=RT, solvent="water", redox="neutral", species={"HNO2": NAN}),
        },
        minerals={},
        basis=("Xu 2020 (10.1038/s41586-020-2330-9) Results: 'guidance from a geochemical scenario' = the cyanosulfidic "
               "network (their ref 23, Patel 2015, not opened by us): adenine as an HCN pentamer; NH4SCN an inevitable "
               "by-product of HCN/H2S photochemistry; thiourea cited; TAP enriched by moving down a thermal gradient; "
               "converging streams then evaporation (150 C dry state); bisulfite from atmospheric SO2; hydrosulfide; "
               "nitrous acid from N2 and CO2; MgCl2 ('magnesium ions', their ref 28). UV 254 nm photoreduction -> uv True. "
               "Redox 'reducing' copies the cyanosulfidic scenario in steps.py. Phosphate listed because step X1 uses a "
               "phosphate buffer. 'atmospheric_nitrous_acid' pH 4 is the reaction pH the authors used; its HNO2 "
               "concentration is not reported (NaN). Rain pH 7 ASSUMED. Pyrimidine-arm intermediates (alpha-anhydro-"
               "uridine/cytidine) are NOT claimed as feedstocks here."),
    ),
    "yi2020_radiolytic_brine": dict(
        name="yi2020_radiolytic_brine", t_range=[0, 100], uv=False, redox="neutral",
        settings=["brine_pool"],
        feedstocks={s: INF for s in ["HCN", "NaCl", "NH4Cl", "phosphate"]},
        volatile=["HCN"],
        streams={},
        minerals={},
        basis=("Yi 2020 (10.1073/pnas.1922139117) Introduction and Discussion: HCN as the only organic feedstock "
               "(from UV photochemistry, lightning, particle impact or impact ablation) plus NaCl, NH4Cl and phosphate; "
               "ionising radiation (radioactive minerals, cosmic rays, flares) with dose rates 'the upper limit' of natural "
               "sources; transiently evaporating water bodies (riverbanks, puddles, salt pans, coastlines) rewetted "
               "semi-periodically. The authors say the aim is not a specific geological scenario. Radiolysis is not on the "
               "closed process list and is recorded only as a step condition. HCN volatility is the authors' own argument "
               "(removal of excess HCN by evaporation). No UV claimed for the scenario. Redox 'neutral' is our label."),
    ),
    "ritson2022_cyanosulfidic": dict(
        name="ritson2022_cyanosulfidic", t_range=[0, 100], uv=True, redox="reducing",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["glycolaldehyde", "glyceraldehyde", "cyanamide", "hydrosulfide",
                                     "cyanoacetylene", "DCI"]},
        volatile=["cyanoacetylene"],
        streams={},
        minerals={},
        basis=("Ritson 2022 (10.1021/jacs.2c07774) Introduction, Conclusions: 'cyanosulfidic scenario we have previously "
               "described': cyanoacetylene made in a (transiently reduced) atmosphere (negligible concentration, bp 45 C); "
               "glycolaldehyde and glyceraldehyde by photochemical Kiliani-Fischer chemistry (UV on sulfur anions); NH2CN and "
               "thiourea from HCN/HS-; 4,5-dicyanoimidazole (DCI) as the major by-product of prebiotic adenine synthesis "
               "(their refs 9, 10, not opened); streams that converge; crystallisation at five junctures. Groundwater is "
               "mentioned for concentration. No concentrations stated (INF). Bicarbonate is NOT claimed as a feedstock. "
               "Redox 'reducing' copies the cyanosulfidic scenario in steps.py. Range 0-100 C is our convention."),
    ),
    "gibard2018_paste": dict(
        name="gibard2018_paste", t_range=[0, 50], uv=False, redox="neutral",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["DAP"]},
        volatile=[],
        streams={},
        minerals={},
        basis=("Gibard 2018 (10.1038/nchem.2878; PMC accepted manuscript) Abstract, Discussion: diamidophosphate (DAP) is "
               "a 'plausible prebiotic agent produced from trimetaphosphate' (by reaction with ammonia at high pH; their "
               "refs 36-38, not opened); aqueous (solution or paste) conditions, r.t. to 50 C, pH 5.5-8, single-pot "
               "aqueous environment. The paper gives no geological setting. Nucleosides, imidazole and the optional Mg2+/"
               "Zn2+ are reagents the authors add; they are NOT claimed as scenario feedstocks. Redox 'neutral' is our label."),
    ),
}

# ------------------------------------------------------------------ R6 Becker 2018
R6 = [
    step("B1", "malononitrile + amidinium + nitrite (pH ~4): (hydroxyimino)malononitrile amidinium salt crystallises on slow evaporation then cooling",
         "S1", "geothermal_field",
         [inp("malononitrile", 0.4, note="1 eq; 100 mmol in ~256 mL total (Methods)"),
          inp("amidinium", 0.4, note="400 mM, HCl or H2SO4 salts of 2a-d (Results first section)"),
          inp("nitrite", 0.4, note="NaNO2, 1.01 eq (Methods)"),
          inp("acetic_acid", 0.4, note="6 mL AcOH in ~256 mL (Methods); gives pH ~4")],
         (4.0, 45.0, "water", "unknown"),
         {"amidinium_oxime_salt": NAN},
         out_cond=(NAN, 9.0, "water", "unknown"),
         yield_status="demonstrated",
         yield_text="isolated crystals: 2a salt 40%, 2b 45%, 2c 53%, 2d 60%",
         source=D["becker2018"], where="Results 'Selective crystallization of an organic salt'; Methods (four salt procedures); Fig. 2a-b",
         notes=("Methods: 2 h at r.t., then 3-4 days at 45 C open to air until concentrated to ~100 mL (from ~256 mL), then fridge overnight 8-10 C. "
                "Solution concentration reaches ~1 M amidinium before crystallisation (Results). Concentration of the salt in the pot not reported."),
         assumptions=["acetic acid and nitrite concentrations computed from the Methods masses and volumes (assumes volumes add)",
                      "cooling temperature 9 C = midpoint of the stated 8-10 C"]),
    step("B2", "dry-state heating of the salt to its melting point -> 5-nitrosopyrimidines (nitrosoPy 4a-d)",
         "S1", "geothermal_field",
         [inp("amidinium_oxime_salt", NAN, True, "crystals filtered off (B1); neat solid, 5 g scale")],
         (NAN, 160.0, "dry", "unknown"),
         {"nitrosoPy": NAN},
         yield_status="demonstrated_purified",
         yield_text="'quantitative' crude; after water suspension and filtration isolated 4a 59%, 4b 64%, 4c 85%, 4d 71% (100 mg scale); main text '60 and 85%'",
         source=D["becker2018"], where="Results 'Nitroso-pyrimidine formation'; Methods (four nitrosopyrimidine procedures)",
         notes=("Salts melt at 108 (2a), 126 (2b), 159 (2c), 142 (2d) C and were kept overnight at their own melting point; "
                "a mixture of all four was heated in a gradient 1 C per 5 min from 100 to 160 C. 160 C is the top of that gradient "
                "and is used as the single step T. Heating too fast above the melting point releases MeSH (2b)."),
         assumptions=["step T = 160 C (top of the stated gradient; individual salts need 108-159 C)"]),
    step("B3", "hydrolysis (0.5 M HCl, r.t., overnight) and aminolysis diversify nitrosoPy into oxo- and N-alkyl nitrosoPys (4e-i)",
         "S2", "geothermal_field",
         [inp("nitrosoPy", NAN, True, "water-insoluble solid left after water wash (B2)"),
          inp("HCl", 0.5, note="0.5 M HCl used 'to accelerate'; authors say reactions are very slow at neutral pH")],
         (0.3, RT, "water", "unknown"),
         {"nitrosoPy": NAN},
         yield_status="demonstrated_purified",
         yield_text="4a->4f and 4c->4i near quantitative overnight; 4b->4e slower, mixture of 4b and 4e; 4e + amines -> 4g,4h in 3-4 d at r.t. (not quantified in main text)",
         source=D["becker2018"], where="Results 'Diversification by hydrolysis and aminolysis'; Fig. 3a-b",
         notes=("Optional branch: needed for the G-type nucleosides (G, m2G, m22G, m1G), not for A, ms2A, m2A. Aminolysis: methylamine 300 mM and "
                "dimethylamine 100 mM, pH ~10 with Na2CO3, 3-4 days r.t.; 4b precipitates and is protected. Output species label 'nitrosoPy' = the mixture 4b-d,f-i."),
         assumptions=["pH 0.3 computed for 0.5 M strong acid (not reported)", "r.t. = 23 C"]),
    step("B4", "nitrosoPy + dilute formic acid + elemental Ni or Fe -> formamidopyrimidines (FaPy 5a-h)",
         "S2", "geothermal_field",
         [inp("nitrosoPy", NAN, True, "precipitated by neutralising (B3 hand-off)"),
          inp("formic_acid", NAN, note="'dilute formic acid'; value in SI, not obtained"),
          inp("Ni0", NAN, note="elementary Ni (or Fe)")],
         (NAN, NAN, "water", "unknown"),
         {"FaPy": NAN, "Ni2+": NAN},
         yield_status="demonstrated_purified",
         yield_text="'converts quantitatively all nitroso-compounds into the corresponding FaPy compounds'; 4b -> 5b after 2 h, -> 5c (desulfurised) after 7 d (H2 sparge speeds it)",
         source=D["becker2018"], where="Results 'Formamidopyrimidine formation as nucleobase precursor'; Fig. 3a,c",
         notes="Ni0/Fe0 become Ni2+/Fe2+; formic acid decomposes to CO2 + H2. T, formic acid concentration and pH not in the main text (SI could not be downloaded).",
         tested_with=["Fe2+"]),
    step("B5", "FaPy + ribose in the dry state -> FaPy ribosides",
         "S2", "geothermal_field",
         [inp("FaPy", NAN, True, "crystallised from basic solution after metal removal (B4 hand-off)"),
          inp("ribose", NAN, note="ribose assumed made elsewhere and washed in; amount in SI")],
         (NAN, NAN, "dry", "unknown"),
         {"FaPy_riboside": NAN},
         yield_status="demonstrated_purified",
         yield_text="'rapid reaction'; no separate yield for this sub-step in the main text",
         source=D["becker2018"], where="Results 'Formation of canonical and non-canonical nucleosides'; Fig. 4a",
         notes="T and conditions not in the main text."),
    step("B6", "dissolve in water, heat under basic conditions -> purine nucleosides (A, G, ms2A, m2A, m2G, m22G, m1G, DA; furanosides and pyranosides)",
         "S2", "geothermal_field",
         [inp("FaPy_riboside", NAN, note="carried from the dry-state condensation; same last wet-dry cycle")],
         (NAN, NAN, "water", "unknown"),
         {"purine_nucleosides": NAN},
         yield_status="demonstrated",
         yield_text="N9 nucleosides 'up to 60%'; ribosylation 'between 15 and 60%'; N3-type regioisomers for A, m2A, DA when FaPy comes from the continuous route",
         source=D["becker2018"], where="Results 'Formation of canonical and non-canonical nucleosides'; Fig. 4b",
         notes="No pH, T or concentration given in the main text ('basic conditions').",
         tested_with=["Ni2+", "Fe2+"]),
]
R6_H = [
    dict(procs=[dict(process="selective_separation", species="amidinium_oxime_salt", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="drying"), dict(process="heating", t_after=160.0)],
         why="Crystals were filtered off, then heated neat to the melting point (Methods)."),
    dict(procs=[dict(process="cooling", t_after=RT), dict(process="rehydration", stream="rain", f=0.9),
                dict(process="selective_separation", species="nitrosoPy", property="crystallisation",
                     demonstrated_by=D["becker2018"])],
         why="Water added to the melt residue dissolves unreacted salt; insoluble nitrosoPy kept (precipitation counted as crystallisation; f=0.9 is our reading of 100 mg in 2-3 mL)."),
    dict(procs=[dict(process="mixing", stream="carbonate_water", f=0.5, ph_after=7.0),
                dict(process="selective_separation", species="nitrosoPy", property="crystallisation",
                     demonstrated_by=D["becker2018"])],
         why="'Neutralizing the solutions leads to efficient precipitation' of nitrosoPys (Fig. 3b); the neutralising base is not named."),
    dict(procs=[dict(process="mixing", stream="carbonate_water", f=0.5, ph_after=9.5),
                dict(process="selective_separation", species="FaPy", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="rehydration", stream="rain", f=0.5), dict(process="drying")],
         why="FaPys washed free of Ni/Fe carbonates/hydroxides at pH 9-10, crystallised by evaporation (Fig. 3c); ribose arrives by rain or flooding, then the last evaporation."),
    dict(procs=[dict(process="rehydration", stream="carbonate_water", f=0.5)],
         why="'Upon dissolution in water and subsequent heating under basic conditions' (Results)."),
]

# ------------------------------------------------------------------ R7 Becker 2019
Y_NOTE = "Becker 2019 submitted manuscript (LMU repository) incl. Supplementary Materials"
R7 = [
    step("Y1", "cyanoacetylene + hydroxyurea -> 3-aminoisoxazole (carbonate, pH 10, Zn2+, urea present)",
         "S1", "geothermal_basin",
         [inp("cyanoacetylene", 0.1, note="100 umol in 1 mL (SI)"), inp("hydroxyurea", 0.105, note="1.1 eq"),
          inp("urea", 0.4, note="4 eq"), inp("Zn2+", 0.1, note="1 eq ZnCl2; Co2+ also"),
          inp("carbonate", 0.4, note="Na2CO3 4 eq")],
         (10.0, 25.0, "water", "unknown"),
         {"aminoisoxazole": 0.088, "urea": 0.4, "Zn2+": 0.1, "carbonate": 0.4},
         yield_status="demonstrated",
         yield_text="3-aminoisoxazole 88% (Zn2+), 83% (Co2+); main text 80-90%; 63% via hydroxylamine disulfonate; 17% with plain NH2OH",
         source=D["becker2019"], where="Main text 'Abstract synthesis of pyrimidine nucleosides'; SI 'General procedure for the formation of 3-aminoisoxazole (4)' (hydroxyurea); Fig. 1",
         notes=("SI: 25 C, 2 h, 850 rpm. Main text says the one-pot gives 4 'at 95 C (80-90%)': conflict between main text and SI; SI value used. "
                "Robust over 10-95 C, 10-100 mM, with urea and metal ions (main text). Output concentration = 88% x 0.1 M."),
         assumptions=["product concentration computed from the stated yield and 100 umol/mL"],
         tested_with=["urea", "Zn2+", "Co2+", "carbonate"]),
    step("Y2", "neutralise to pH 6-7, dry down at 95 C with urea and Zn2+ -> N-isoxazolylurea (8)",
         "S2", "geothermal_basin",
         [inp("aminoisoxazole", 0.088, note="formed in the same pot (Y1)"), inp("urea", 0.4), inp("Zn2+", 0.1)],
         (6.5, 95.0, "water", "unknown"),
         {"isoxazolylurea": 0.056},
         out_cond=(NAN, 95.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text="one-pot 56% (Zn2+), 40% (Co2+) at 95 C, 2 d; from pure 4: 88% (Zn2+), 68% (Co2+), 25% (no metal)",
         source=D["becker2019"], where="Main text 'Abstract synthesis of pyrimidine nucleosides'; SI 'One-pot prebiotic synthesis from 1'; Fig. 2A",
         notes=("SI: neutralised with conc. HCl (70.4 uL into ~1 mL), equilibrated at 95 C to pH 6-7, then 2 d at 95 C open to air to evaporate; residue dissolved to 1 mL. "
                "The authors' natural analogue is acid rain (pH ~3, Discussion). Standalone version used 4 at ~1 M (500 umol in 500 uL)."),
         assumptions=["pH 6.5 = midpoint of the stated 6-7", "isoxazolylurea concentration = 56% x 0.1 M (residue made up to 1 mL)"],
         tested_with=["carbonate", "hydroxyurea"]),
    step("Y3", "isoxazolylurea + ribose + boric acid, dry-down at 95 C -> N-isoxazolyl-N'-ribosylureas (10a-d)",
         "S2", "geothermal_basin",
         [inp("isoxazolylurea", 0.082, True, "crystallised/ground solid or synthetic standard; 0.05 mmol in ~608 uL"),
          inp("ribose", 0.41, note="0.25 mmol in ~608 uL (3 M stock)"),
          inp("boric_acid", 0.021, note="0.0125 mmol in ~608 uL (500 mM stock)")],
         (NAN, 95.0, "water", "unknown"),
         {"isoxazolyl_riboside": NAN},
         out_cond=(NAN, 95.0, "dry", "unknown"),
         yield_status="demonstrated_purified",
         yield_text="10a-d 95% (pyranosides dominate first); heating in 125 mM borax 95 C 2.5-5 h converts to furanosides 10a,b (54%); lueneburgite or borax >70%",
         source=D["becker2019"], where="Main text 'Abstract synthesis of pyrimidine nucleosides'; SI 'N-isoxazolyl-N'-ribosyl-urea'; Figs. S4, S5",
         notes="SI also describes a ground-solid version (5 eq ribose, 0.25 eq boric acid, oven 95 C overnight). Pyranoside-to-furanoside equilibration needs a further basic/borate heating (not a separate numbered step).",
         assumptions=["concentrations computed from SI amounts and volumes (volumes add)"]),
    step("Y4", "reductive N-O cleavage with Fe2+ / dithiol + mineral (lueneburgite), 100 C, anoxic -> cytidine and uridine nucleosides (11a-d, 12a,b)",
         "S2", "geothermal_basin",
         [inp("isoxazolyl_riboside", 0.2, True, "10a/b 3:1 mixture, 0.1 mmol in 0.5 mL; isolated/synthetic"),
          inp("carbonate", 0.075, note="75 mM Na2CO3"), inp("Fe2+", 1e-4, note="0.0005 eq (NH4)2Fe(SO4)2 x 0.2 M"),
          inp("DTT", 0.3, note="1.5 eq"), inp("luneburgite", 0.2, note="1 eq mineral")],
         (NAN, 100.0, "water", "reducing"),
         {"pyrimidine_nucleosides": NAN},
         yield_status="demonstrated_purified",
         yield_text="combined 85% (cytidine isomers + uridine) with synthetic lueneburgite; alpha- and beta-furanosyl C about equal; only 0.0001 eq Fe2+ needed; none without Fe2+",
         source=D["becker2019"], where="Main text 'Abstract synthesis...' and 'Selective one-pot formation of 5'-nucleoside mono- and di-phosphates'; SI 'General procedure nucleoside formation'; Fig. 2C, Fig. S6",
         notes=("Argon-degassed, sealed, 4 h. SI general procedure lists Fe source 0.5 eq; main text and Fig. 2C legend give 0.0005 eq soluble Fe2+; the nucleotide one-pot SI uses FeS2 0.5 eq. "
                "Thiol alternatives (Fig. S6, 0.001 eq Fe2+, carbonate/borate pH 9.7): cysteine 11a 37.2% + 11b 22.9%, mercaptoethanol 30.8/18.2, DTT 54.7/19.8, propanedithiol 26.0/12.2."),
         assumptions=["Fe2+ 0.0005 eq taken from the Fig. 2C legend (not the SI general-procedure 0.5 eq)"]),
    step("Y5", "add urea, dry down at 85 C with lueneburgite -> cytidine and uridine 5'-mono- and 5'-diphosphates",
         "S2", "geothermal_basin",
         [inp("pyrimidine_nucleosides", NAN, note="same pot (Y4); concentration not reported"),
          inp("urea", NAN, note="40 eq solid urea (4 mmol on 0.1 mmol nucleoside), dissolved at 65 C"),
          inp("luneburgite", 0.2, note="1 eq, still present from Y4")],
         (NAN, 85.0, "water", "unknown"),
         {"nucleotides_5prime": NAN},
         out_cond=(NAN, 85.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text="19% relative to cytidine isomers (5'-mono- and 5'-di-phosphates); furanoside:pyranoside enriched from 4:1 to 17:1; pyrophosphates dominate the diphosphates",
         source=D["becker2019"], where="Main text 'Selective one-pot formation of 5'-nucleoside mono- and di-phosphates'; SI 'General procedure for one-pot nucleotide formation'; Figs. 3, S7",
         notes="Open to air 20 h, 85 C. Struvite also works (with 3 eq oxalic acid, Fig. S11 not read).",
         tested_with=["carbonate", "DTT", "Fe2+", "FeS2"]),
]
R7_H = [
    dict(procs=[dict(process="mixing", stream="acid_rain", f=0.5, ph_after=6.5), dict(process="heating", t_after=95.0)],
         why="Authors neutralise pH 10 to 6-7 (SI: conc. HCl, ~7% by volume); their natural analogue is acid rain at pH ~3. f=0.5 is the value that lands at pH 6.5 from pH 10 with a pH 3 stream."),
    dict(procs=[dict(process="selective_separation", species="isoxazolylurea", property="crystallisation",
                     demonstrated_by=D["becker2019"]),
                dict(process="rehydration", stream="rain", f=0.5), dict(process="heating", t_after=95.0)],
         why="8 was enriched by crystallisation from carbonated supernatant (55%, X-ray) and then met ribose by 'flooding or mixing of environments' (main text); the one-pot purine/pyrimidine run skips the crystallisation."),
    dict(procs=[dict(process="rehydration", stream="carbonate_water", f=0.5), dict(process="heating", t_after=100.0)],
         why="Dried riboside residue 'taken up with a slightly basic solution' (100 mM Na2CO3, 50 mM borate), argon-degassed, with Fe2+ and DTT, heated to 100 C."),
    dict(procs=[dict(process="same_pot"), dict(process="cooling", t_after=85.0)],
         why="Solid urea added directly to the nucleoside reaction mixture, then dried at 85 C ('one-pot')."),
]

# ------------------------------------------------------------------ R8 Xu 2020
R8 = [
    step("X1", "adenine hydrolysis (138 C, phosphate pH 8, 10-12 d) -> 4,5,6-triaminopyrimidine (TAP) enriched in the supernatant",
         "S2", "surface_pool",
         [inp("adenine", NAN, note="commercial; concentration in SI"), inp("phosphate", NAN, note="phosphate buffer; concentration in SI")],
         (8.0, 138.0, "water", "unknown"),
         {"TAP": NAN, "AICA": NAN, "formate": NAN, "adenine": NAN},
         yield_status="demonstrated",
         yield_text="TAP 2-3% (8-9% on recovered adenine) at partial conversion; supernatant AICA : TAP : adenine = 4 : 2 : 1, formate the only other major component",
         source=D["xu2020"], where="Results 'Prebiotic Route to Purine Deoxyribonucleosides' (adenine paragraph); Fig. 2, Fig. S1-S5 (SI not obtained)",
         notes="Adenine does not react with elemental sulfur up to 300 C. Miller et al. reported t1/2 of adenine ~1 year at 100 C. Authors propose moving down a thermal gradient to enrich TAP."),
    step("X2", "TAP + ammonium thiocyanate (or thiourea), dry-state heating -> 8-mercaptoadenine (16)",
         "S2", "surface_pool",
         [inp("TAP", NAN, note="commercial or crude adenine hydrolysate (both work)"),
          inp("ammonium_thiocyanate", NAN, note="or thiourea 25")],
         (NAN, NAN, "dry", "unknown"),
         {"mercaptoadenine": NAN},
         yield_status="demonstrated",
         yield_text="conversion stated; no yield, T or time in the main text",
         source=D["xu2020"], where="Results (adenine paragraph, last two sentences); Fig. 2 (SI not obtained)",
         notes="Label 'demonstrated' rests on the main-text statement that TAP 'is converted to 8-mercaptoadenine'; the yield is in the SI, which could not be downloaded."),
    step("X3", "alpha-anhydrouridine (15) + 8-mercaptoadenine + MgCl2, dry state 150 C -> N9- and N7-8,2'-anhydrothioadenosines (18, 19)",
         "S2", "surface_pool",
         [inp("anhydrouridine_15", NAN, True, "alpha-anhydrouridine, made from alpha-2-thiouridine at 80 C (63% water, 89% formamide); alpha-anhydrocytidine 12 also works"),
          inp("mercaptoadenine", NAN, True, "16 from TAP + NH4SCN"),
          inp("Mg2+", NAN, note="MgCl2")],
         (NAN, 150.0, "dry", "unknown"),
         {"thioanhydroadenosine_N9": NAN, "thioanhydroadenosine_N7": NAN},
         yield_status="demonstrated_purified",
         yield_text="from 15: 39% N9 (18) + 48% N7 (19) = 87% with MgCl2; from 12: 26% + 42% = 68%; without MgCl2 14% and 16% (trace from 12)",
         source=D["xu2020"], where="Results 'Prebiotic Route to Purine Deoxyribonucleosides'; Fig. 2; Extended Data Fig. 8a (150 C, 1.5 d, mixture)",
         notes="Authors imagine 15 and 16 'brought together, perhaps by converging streams that then undergo evaporation'. 8-mercaptoguanine did not react."),
    step("X4", "254 nm photoreduction of 18/19 with bisulfite (pH 7) -> deoxyadenosine (7) + 8-mercapto-deoxyadenosine (26)",
         "S2", "surface_pool",
         [inp("thioanhydroadenosine_N9", NAN), inp("thioanhydroadenosine_N7", NAN), inp("bisulfite", NAN, note="HSO3-, pH 7")],
         (7.0, NAN, "water", "unknown"),
         {"deoxyadenosine": NAN, "mercapto_deoxyadenosine": NAN},
         yield_status="demonstrated_purified",
         yield_text="18+19 mixture with bisulfite: dA 44%, 26 18% (N9 only; 7 h); 18 alone: dA 51%, 26 23%; 19 alone: destroyed. With H2S instead: 18: dA 39%, 26 15%; mixture dA 31% + N7-dA 17%",
         source=D["xu2020"], where="Results 'Prebiotic Route...'; Fig. 2; Extended Data Fig. 3 (7 h irradiation)",
         notes="Hydrosulfide variant keeps the N7 product (20), which hydrolyses ~70x faster than dA. Route A in Fig. 4 adds ferrocyanide to the bisulfite step.",
         tested_with=["thioanhydroadenosine_N7"]),
    step("X5", "nitrous acid (pH 4, r.t., days) -> deoxyinosine (9) alongside dA; 26 is desulfurised",
         "S2", "surface_pool",
         [inp("deoxyadenosine", NAN, note="carried from photoreduction"), inp("mercapto_deoxyadenosine", NAN),
          inp("HNO2", NAN, note="nitrous acid at pH 4")],
         (4.0, RT, "water", "unknown"),
         {"deoxyinosine": NAN, "deoxyadenosine": NAN},
         yield_status="demonstrated",
         yield_text="4 d r.t.: ~40% of dA -> dI (60:40); 67:33 dA:26 -> 65:35 dA:dI; 47:53 dA:C -> dA:dI:C:U 30:17:42:11",
         source=D["xu2020"], where="Results 'Prebiotic Route to A Purine/Pyrimidine Genetic System'; Fig. 2; Extended Data Fig. 6",
         notes="Concentrations and nitrite source in SI. Without HNO2 only trace depurination (t1/2 1600 h at pH 4).",
         assumptions=["r.t. = 23 C"]),
]
R8_H = [
    dict(procs=[dict(process="cooling", t_after=RT),
                dict(process="selective_separation", species="adenine", property="crystallisation", mode="remove",
                     demonstrated_by=D["xu2020"]),
                dict(process="drying")],
         why="'Differential solubilities of adenine and TAP: supernatants are enriched in TAP after cooling'; NH4SCN 'can be mixed at any stage, eventual evaporation and dry-state reaction'."),
    dict(procs=[dict(process="heating", t_after=150.0)],
         why="'Converging streams that then undergo evaporation'; 15 (and in the lab, isolated 16) are dry-mixed and heated at 150 C. 15 comes from the pyrimidine arm, not produced earlier in this table."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5), dict(process="uv_irradiation")],
         why="Dry residue taken up in water with bisulfite and irradiated at 254 nm (Extended Data Fig. 3: crude mixture, then 7 h)."),
    dict(procs=[dict(process="mixing", stream="atmospheric_nitrous_acid", f=0.5, ph_after=4.0)],
         why="Photoreduction products 'treated with nitrous acid at pH 4' (Fig. 2 legend)."),
]

# ------------------------------------------------------------------ R9 Yi 2020
R9 = [
    step("N1", "gamma radiolysis (~48 kGy, ~1 d) of dilute HCN in brine: glyceronitrile and cyanamide",
         "S1", "brine_pool",
         [inp("HCN", 0.025, note="25 mM NaCN, pH 7"), inp("NaCl", 5.0, note="5 M"), inp("NH4Cl", 0.1),
          inp("phosphate", 0.01, note="10 mM Pi")],
         (7.0, 24.0, "water", "reducing"),
         {"cyanamide": 6.5e-4, "glyceronitrile": 1.0e-4, "HCN": NAN, "NaCl": 5.0, "NH4Cl": 0.1, "phosphate": 0.01},
         out_cond=(NAN, 24.0, "water", "reducing"),
         yield_status="demonstrated",
         yield_text="cyanamide ~0.65 mM (2.6% on CN-); glyceronitrile 0.10 mM (1.2%); no free glycolaldehyde detected; complex mixture also present",
         source=D["yi2020"], where="Results 'gamma Radiolysis Combined with Dry-Down...'; Fig. 2A legend; Table 1",
         notes=("50 mL, N2 atmosphere, 60Co ~2.2 kGy/h, ~24 C. NaCl omitted -> no cyanamide; Pi > ~0.1 M hinders cyanamide/glyceronitrile. "
                "Radiolysis is not a closed-list process, recorded only as a step condition. Step labelled 'reducing' because the source ran it under N2 (steps.py convention)."),
         assumptions=["redox class 'reducing' for an N2-atmosphere run"]),
    step("N2", "dry-down (~10x concentration, 35 C, reduced pressure) removes excess HCN and frees glycolaldehyde from glyceronitrile",
         "S1", "brine_pool",
         [inp("glyceronitrile", 1.0e-4), inp("cyanamide", 6.5e-4), inp("HCN", NAN, note="excess HCN, amount not reported")],
         (NAN, 35.0, "water", "unknown"),
         {"glycolaldehyde": 1.6e-4, "cyanamide": 2.8e-3, "glyceronitrile": 5.7e-4},
         out_cond=(NAN, 35.0, "water", "unknown"),
         yield_status="demonstrated",
         yield_text="glycolaldehyde ~0.16 mM (0.13% on NaCN); cyanamide 2.8 mM (1.1%); glyceronitrile 0.57 mM (0.68%); NaCl precipitates (may carry cyanamide)",
         source=D["yi2020"], where="Results 'gamma Radiolysis Combined with Dry-Down...'; Fig. 2A; Table 1 (dagger-double footnote); Fig. 1 (model dry-down)",
         notes="Solution concentrated from 50 to ~5 mL; a homogeneous aliquot without solid was used. Partial loss of cyanamide to the NaCl precipitate or degradation is suspected. Adding NaCN back to 0.1 M kills the next step (control).",
         tested_with=["NaCl", "NH4Cl", "phosphate"]),
    step("N3", "heating the concentrate at pH 8, 50 C, 3 h -> 2-aminooxazole and 2-aminoimidazole",
         "S2", "brine_pool",
         [inp("glycolaldehyde", 1.6e-4), inp("cyanamide", 2.8e-3), inp("phosphate", NAN, note="~10x the starting 10 mM after dry-down (not measured)"),
          inp("NH4Cl", NAN, note="concentrated ~10x (not measured)")],
         (8.0, 50.0, "water", "unknown"),
         {"aminooxazole": 9.0e-5, "aminoimidazole": 5.5e-5},
         yield_status="demonstrated",
         yield_text="2-aminooxazole 0.09 mM (Table 1; text says ~0.11 mM) = 0.11% on NaCN or 69% on glycolaldehyde; 2-aminoimidazole 0.055 mM = 0.066% on NaCN or 34% on glycolaldehyde; imidazolone 3 also formed",
         source=D["yi2020"], where="Results 'gamma Radiolysis Combined with Dry-Down...'; Table 1 (section footnote); Fig. 2A-B",
         notes=("pH adjusted by hand to 8 in the NMR tube (450 uL + 50 uL D2O); at pH 7 more aminoimidazole, less aminooxazole. Aminooxazole concentration is the mean of two experiments "
                "(Table 1) while the text gives ~0.11 mM. Aminoacetonitrile and serinenitrile form from the cyanohydrins during this heating."),
         tested_with=["glyceronitrile", "NaCl", "NH4Cl", "phosphate", "aminoacetonitrile", "serinenitrile", "cyanamide"]),
]
R9_H = [
    dict(procs=[dict(process="same_pot"), dict(process="heating", t_after=35.0)],
         why="Concentrated under reduced pressure at 35 C; the concentration itself is recorded inside N2 (outputs measured after dry-down)."),
    dict(procs=[dict(process="same_pot"), dict(process="heating", t_after=50.0)],
         why="Aliquot transferred to an NMR tube, pH adjusted to 8 by hand (7 -> 8 is within the 1.0 tolerance), heated to 50 C."),
]

# ------------------------------------------------------------------ R10 Ritson 2022
R10 = [
    step("C1", "glycolaldehyde + NaSH + cyanamide, bicarbonate pH 9.2, 60 C -> 2-aminothiazole",
         "S1", "surface_pool",
         [inp("glycolaldehyde", 0.025, note="25 mM, supplied as dimer; hydrolyses rapidly"), inp("hydrosulfide", 0.1, note="NaSH 100 mM"),
          inp("cyanamide", 0.075, note="75 mM"), inp("bicarbonate", 0.2, note="200 mM buffer")],
         (9.2, 60.0, "water", "unknown"),
         {"aminothiazole": 0.0065, "aminooxazole": 2.5e-4, "dithiane_46": NAN},
         yield_status="demonstrated",
         yield_text="26% after 3 d, 30% after 7 d, 32-40% after 10-25 d (bicarbonate pH 9.2); phosphate pH 7: ~10% (3 d), ~14% (7 d); 2-aminooxazole ~1%",
         source=D["ritson2022"], where="Results (paragraphs on 2-aminothiazole 23, Scheme 4-5, Figures S13-S17); Conclusions",
         notes=("Two pathways to 23 (fast minor via 2-aminooxazole chemistry; slow major via thiazoline 48). Main by-product dithiane 46 (crystalline). "
                "Evaporating 100 mM 23 at pH 6.5 to crystallisation lost <10%. Yield basis (glycolaldehyde) is not stated; output concentration assumes it."),
         assumptions=["aminothiazole = 26% x 25 mM assuming yield on glycolaldehyde", "aminooxazole ~1% x 25 mM"]),
    step("C2", "aminal formation: 2-aminothiazole crystallises glycolaldehyde (1-a) and glyceraldehyde (3-a) separately",
         "S1", "surface_pool",
         [inp("aminothiazole", NAN), inp("glycolaldehyde", NAN), inp("glyceraldehyde", NAN)],
         (NAN, NAN, "water", "unknown"),
         {"glycolaldehyde_aminal": NAN, "glyceraldehyde_aminal": NAN},
         yield_status="unread",
         yield_text="described in Ritson 2022 Scheme 3 and text; performed and quantified in Islam 2017 (10.1038/nchem.2703), which we did not open",
         source=D["islam2017"], where="Ritson 2022 Results (Islam et al. paragraph) and Scheme 3 caption",
         notes="Not experimentally re-done in Ritson 2022. Rapid crystallisation of 1-a, delayed crystallisation of 3-a allow separation; 3-k:3 ~9:1 at equilibrium."),
    step("C3", "1-a + cyanamide -> 2-aminooxazole; 2-aminooxazole + 3-a -> ribo-aminooxazoline (crystalline)",
         "S2", "surface_pool",
         [inp("glycolaldehyde_aminal", NAN, True, "crystalline 1-a"), inp("cyanamide", NAN),
          inp("glyceraldehyde_aminal", NAN, True, "crystalline 3-a")],
         (NAN, NAN, "water", "unknown"),
         {"aminooxazole": NAN, "ribo_aminooxazoline": NAN},
         yield_status="unread",
         yield_text="Scheme 1/3: reaction of crystallised 1-a with NH2CN to give 2, and of 2 with crystallised 3-a to give ribo-4 shown 'robust' in Islam 2017 (not opened); Powner 2009 Nature cited for ribo-4 crystallisation (not opened)",
         source=D["islam2017"], where="Ritson 2022 Introduction (Scheme 1) and Results (Islam paragraph)",
         notes="Not experimentally re-done in Ritson 2022."),
    step("C4", "cyanoacetylene + 4,5-dicyanoimidazole (DCI), pH 5.2 -> crystalline N-cyanovinyl-4,5-dicyanoimidazole (CV-DCI)",
         "S1", "surface_pool",
         [inp("cyanoacetylene", NAN, note="aqueous solution added to a DCI suspension"), inp("DCI", NAN, note="suspended in H2O/D2O; concentration in SI")],
         (5.2, NAN, "water", "unknown"),
         {"CV-DCI": NAN},
         yield_status="demonstrated",
         yield_text="'clean addition ... on a timescale of hours'; crystals formed overnight (X-ray); no yield given; solid stable 6 months in air; little reaction with CN-, phosphate, adenosine, NH3",
         source=D["ritson2022"], where="Results (first paragraph, Scheme 2, Figures S1-S7)",
         notes="T and concentrations in SI (not read). DCI is claimed as the major by-product of prebiotic adenine synthesis (refs not opened).",
         tested_with=["cyanide", "phosphate", "adenosine", "ammonia"]),
    step("C5", "CV-DCI + ribo-aminooxazoline in formamide, 50 C, 2 d, then UV -> ribo-anhydrocytidine",
         "S2", "surface_pool",
         [inp("CV-DCI", 0.2, True, "crystalline CV-DCI, 200 mM"),
          inp("ribo_aminooxazoline", 0.1, True, "crystalline ribo-4, 100 mM")],
         (NAN, 50.0, "formamide", "unknown"),
         {"ribo_anhydrocytidine": 0.05, "cyanovinyl_adduct_21": 0.014},
         yield_status="demonstrated_purified",
         yield_text="anhydrocytidine 6 ~50% after 2 d (~48% before irradiation); trans-cyanovinyl adduct 21 ~14%; irradiation -> ~55% (neat formamide) or ~58% (diluted in water); 21 not converted by heat (90 C)",
         source=D["ritson2022"], where="Results (CV-DCI + ribo-4 paragraph, Scheme 2, Figures S8-S11)",
         notes="In water the reaction of 20 with ribo-4 gives low conversion (poor solubility). Output concentrations = stated yield x 0.1 M (assumes yield on ribo-4).",
         assumptions=["output concentrations computed from stated yields on 100 mM ribo-aminooxazoline"]),
]
R10_H = [
    dict(procs=[dict(process="same_pot")], why="Into an unread step; conditions unknown."),
    dict(procs=[dict(process="same_pot")], why="Between unread steps."),
    dict(procs=[dict(process="same_pot")], why="From an unread step into the independent CV-DCI branch; the paper describes no hand-off between these (see NOTES.md)."),
    dict(procs=[dict(process="selective_separation", species="CV-DCI", property="crystallisation", demonstrated_by=D["ritson2022"]),
                dict(process="drying"), dict(process="heating", t_after=50.0)],
         why="CV-DCI crystals recovered and dissolved in formamide with ribo-4 (Results); ribo-4 arrives as a separately crystallised input, not carried through this hand-off."),
]

# ------------------------------------------------------------------ R11 Gibard 2018
R11 = [
    step("G1", "uridine + DAP + imidazole, paste with a few drops of water -> uridine 2',3'-cyclic phosphate (c-UMP)",
         "S2", "surface_pool",
         [inp("uridine", NAN, True, "commercial nucleoside; paste, amount in SI"), inp("DAP", NAN, note="equivalents in SI"),
          inp("imidazole", NAN, note="equivalents in SI")],
         (NAN, RT, "unknown", "unknown"),
         {"c-UMP": NAN},
         yield_status="demonstrated_purified",
         yield_text="c-UMP ~80% after 30 d; 65% isolated at 1 g scale; solution (method B, pH ~7, imidazole) similar conversion; cytidine 42% (10 d); adenosine <5%, guanosine 17% in paste; solution: c-CMP 27%, c-AMP 31%, c-GMP 27%",
         source=D["gibard2018"], where="Results 'Phosphorylation of nucleosides/tides and oligonucleotides by DAP'; Fig. 1a-b; Methods Summary",
         notes=("Method B: 0.1 M uridine, 1-25 eq DAP, pH 5.5-10, r.t.-50 C, with/without Zn2+, Mg2+ or imidazole, over days-weeks; Zn2+ lowers pH and hydrolyses DAP. "
                "Paste solvent 'unknown' because 'paste' is not in the allowed solvent set. 5'-NMPs react with DAP (pH 7) to amidodiphosphates (77-90% in 5 d), not encoded."),
         assumptions=["r.t. = 23 C"]),
    step("G2", "same paste: oligomerisation of the cyclophosphorylated uridine -> oligouridylates up to tetramer with terminal 2',3'-cyclophosphate",
         "S3", "surface_pool",
         [inp("c-UMP", NAN, note="formed in the same paste (G1); concentration not reported"), inp("DAP", NAN), inp("imidazole", NAN)],
         (NAN, RT, "unknown", "unknown"),
         {"oligouridylate": NAN},
         yield_status="demonstrated",
         yield_text="oligomers up to tetramer 'observed'; not quantified; phosphodiester linkage type (2',5' vs 3',5') not determined",
         source=D["gibard2018"], where="Results (paste-reaction paragraph); Fig. 1b",
         notes=("The paper shows oligomers forming in the same G1 paste, not from isolated c-UMP; encoded as a second step in the same pot to match the headline claim 'higher order structures under the same phosphorylation conditions'. "
                "Peptide and liposome results (glycine, glycerol/nonanoic acid) are separate substrates and are not encoded."),
         assumptions=["r.t. = 23 C", "G2 treated as a separate step for the oligomerisation claim although the source reports it from the same paste"]),
]
R11_H = [
    dict(procs=[dict(process="same_pot")], why="Oligomers appear in the same paste mixture without workup (Results)."),
]

# ------------------------------------------------------------------ pathways
PATHWAYS = [
    dict(id="r6", label="Becker 2018 wet-dry continuous synthesis of purine nucleosides (Nat Commun)",
         scenario="becker2018_geothermal", steps=R6, handoffs=R6_H,
         note="SI not obtainable (download challenge page); several T, pH and concentration values are NaN."),
    dict(id="r7", label="Becker 2019 unified pyrimidine route via isoxazolylurea to nucleosides and 5'-phosphates (Science)",
         scenario="becker2019_geothermal", steps=R7, handoffs=R7_H,
         note="Read from the LMU repository submitted manuscript with SI. Purine arm (Fig. 4-5) not encoded."),
    dict(id="r8", label="Xu 2020 purine deoxyribonucleosides dA and dI via 8-mercaptoadenine (Nature)",
         scenario="xu2020_cyanosulfidic", steps=R8, handoffs=R8_H,
         note="Starts at Fig. 2: alpha-anhydropyrimidine 15 is an input from the pyrimidine arm. SI not obtainable."),
    dict(id="r9", label="Yi 2020 continuous radiolysis plus dry-down network to 2-aminooxazole and 2-aminoimidazole (PNAS)",
         scenario="yi2020_radiolytic_brine", steps=R9, handoffs=R9_H,
         note="SI not read; Table 1 and main text used."),
    dict(id="r10", label="Ritson 2022 azole-assisted route: CV-DCI cyanoacetylene capture and 2-aminothiazole (JACS)",
         scenario="ritson2022_cyanosulfidic", steps=R10, handoffs=R10_H,
         note="C2 and C3 are Scheme 1/3 steps from Islam 2017 / Powner 2009 and are labelled unread."),
    dict(id="r11", label="Gibard 2018 DAP phosphorylation of uridine and oligomerisation in paste (Nat Chem)",
         scenario="gibard2018_paste", steps=R11, handoffs=R11_H,
         note="Not a feedstock-to-nucleoside route: starts from supplied nucleosides."),
]
