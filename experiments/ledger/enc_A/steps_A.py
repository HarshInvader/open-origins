"""Step tables for six published RNA-precursor routes (R6-R11), board task #29, blind encoder enc-A.

Same conventions as experiments/pathway_map/steps.py (read-only import):
NaN = not reported or not read (checks become UNASSESSED); INF = scenario feedstock with no stated
concentration; `unread` steps are given to the scorer as `missing`. RT ('room temperature') is recorded
as 23 C, our stated assumption (same as steps_dsm.py). `purified=True` marks any input the source
bought, isolated or crystallised rather than carried over, except scenario feedstocks bought as
commercial reagents (steps.py convention). Concentrations marked 'our arithmetic' were computed from
the reagent amounts and volumes stated in the cited procedure. Nothing here is scored.

Sources opened (all legal open copies):
- R6 Becker 2018: PMC5765019 full text + Nat Commun SI (static-content.springer.com).
- R7 Becker 2019: accepted manuscript + SI, Open Access LMU (epub.ub.uni-muenchen.de/71503).
- R8 Xu 2020: PMC7116818 author manuscript + Nature SI (static-content.springer.com).
- R9 Yi 2020: PMC7306801 full text (SI not opened: PMC download challenge).
- R10 Ritson 2022: PMC9619408 full text (SI not opened: PMC download challenge, ACS 403).
- R11 Gibard 2018: PMC6295206 author manuscript + Nat Chem SI (static-content.springer.com).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "pathway_map"))
import steps as ST  # noqa: E402

NAN, INF, inp, step = ST.NAN, ST.INF, ST.inp, ST.step

D = dict(
    becker2018="10.1038/s41467-017-02639-1",  # R6
    becker2019="10.1126/science.aax2747",     # R7
    xu2020="10.1038/s41586-020-2330-9",       # R8
    yi2020="10.1073/pnas.1922139117",         # R9
    ritson2022="10.1021/jacs.2c07774",        # R10
    gibard2018="10.1038/nchem.2878",          # R11
)

RT = 23.0  # 'room temperature' / 'r.t.' in the sources; 23 C is our assumption
RT_NOTE = "RT recorded as 23 C (our assumption; source says room temperature)"
RAIN = dict(ph=7.0, t=23.0, solvent="water", redox="neutral", species={})  # pH 7 / 23 C: our assumption, as in steps.py

# =====================================================================================
# SCENARIOS (one per route; feedstocks as the authors claim them)
# =====================================================================================
SCENARIOS = {
    "R6_geothermal_wetdry": dict(
        name="R6_geothermal_wetdry", t_range=[0, 160], uv=True, redox="neutral",
        settings=["surface_pool", "hot_soil"],
        feedstocks={s: INF for s in ["malononitrile", "amidinium_2b", "NaNO2", "AcOH", "HCOOH", "Ni0", "Fe0",
                                     "H2", "carbonate", "ribose", "methylamine", "dimethylamine"]},
        volatile=["HCOOH", "AcOH", "H2", "CO2", "MeSH"],
        streams={
            "rain": dict(RAIN),
            "basic_water": dict(ph=9.5, t=NAN, solvent="water", redox="neutral", species={"carbonate": NAN}),
            "dilute_formic": dict(ph=NAN, t=NAN, solvent="water", redox="neutral", species={"HCOOH": NAN}),
        },
        minerals={},
        basis=("Becker 2018 (10.1038/s41467-017-02639-1) Fig. 1, Results and Discussion: a geothermal field with wet-dry "
               "cycles; starting materials made in the atmosphere and washed in by rain; several environments linked by "
               "rivers; hot soil (volcanic activity or sunlight on dark surfaces) reaching 110-160 C for the salt melts; "
               "dilute formic acid with elemental Ni/Fe from the crust; slightly basic water (pH ~9-10, carbonates) "
               "to precipitate metal ions; ribose formed elsewhere and washed in by rain or flooding. Feedstocks named "
               "in the Discussion: formic acid, acetic acid, NaNO2, malononitrile, amidinium compounds, Ni or Fe; "
               "amines for the G-branch aminolysis. No concentrations stated (INF). T range 0-160 C: up to the "
               "highest salt melt. UV: surface setting, not used by any step. Redox 'neutral' is our classification "
               "(not stated). Stream basic_water pH 9.5 = midpoint of the authors' 'pH ~9-10' (our choice); rain pH and "
               "T are our assumption."),
    ),
    "R7_surface_basins": dict(
        name="R7_surface_basins", t_range=[0, 100], uv=True, redox="neutral",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["cyanoacetylene", "NH3", "hydroxylamine", "HCN", "urea", "HCOOH", "cyanate",
                                     "nitrite", "bisulfite", "carbonate", "borate", "Zn2+", "Co2+", "Fe2+", "FeS2",
                                     "luneburgite", "struvite", "ribose"]},
        volatile=["NH3", "HCN"],
        streams={
            "acid_rain": dict(ph=3.0, t=NAN, solvent="water", redox="neutral", species={}),
            "carbonate_water": dict(ph=10.0, t=NAN, solvent="water", redox="neutral", species={"carbonate": NAN}),
            "rain": dict(RAIN),
        },
        minerals={},
        basis=("Becker 2019 (10.1126/science.aax2747, accepted manuscript, Discussion and Fig. 5B): several surface "
               "basins in a geothermal field or at surface hydrothermal vents, linked by one or two streams; wet-dry "
               "cycles; pH fluctuating between ~3 (acid rain from SO2/NOx) and ~10 (carbonates); elevated "
               "temperatures; NO2-, HSO3- and urea delivered by rain; cyanoacetylene from surface hydrothermal vents; "
               "Zn/Fe and their ions, iron-sulfur surfaces, borates and phosphate minerals (luneburgite, struvite). "
               "Key starting molecules listed: cyanoacetylene, NH3, NH2OH (or its disulfonate), HCN, urea, formic acid, "
               "isocyanate, nitrite, carbonate, borate. Ribose: the authors 'need to assume' it arrives by flooding or "
               "mixing (they say its selective formation is unclear); listed as feedstock as claimed. Hydroxylurea "
               "and thiols are NOT in the authors' feedstock list. No concentrations stated (INF). T range 0-100 C: "
               "our bound (steps run up to 100 C). UV not invoked. Redox 'neutral' is our classification (N2/CO2 "
               "atmosphere per the Introduction). Stream temperatures not stated (NaN)."),
    ),
    "R8_cyanosulfidic_xu": dict(
        name="R8_cyanosulfidic_xu", t_range=[0, 150], uv=True, redox="reducing",
        settings=["surface_pool", "evaporite"],
        feedstocks={s: INF for s in ["HCN", "H2S", "adenine", "NH4SCN", "thiourea", "nitrite", "bisulfite",
                                     "Mg2+", "phosphate", "ferrocyanide"]},
        volatile=["HCN", "H2S"],
        streams={"rain": dict(RAIN)},
        minerals={},
        basis=("Xu 2020 (10.1038/s41586-020-2330-9) main text: guided by the cyanosulfidic scenario (their ref. 23); "
               "adenine as an HCN pentamer; NH4SCN from HCN/H2S photochemistry or thiourea; nitrous acid from N2 and CO2; "
               "bisulfite from atmospheric SO2 in water; magnesium ions; glycosyl donors 12/15 and thiocytidines 13/3 "
               "are intermediates of the earlier pyrimidine synthesis (not feedstocks, not made in this paper); "
               "'converging streams that then undergo evaporation' bring 12/15 and 16 together; TAP enriched by moving "
               "down a thermal gradient. Ferrocyanide used in photoreduction (cyanosulfidic reagent). No "
               "concentrations stated (INF). T range 0-150 C: up to the dry-state glycosylation. Redox 'reducing' "
               "follows the cyanosulfidic scenario the authors cite (our classification)."),
    ),
    "R9_radiolytic_drydown": dict(
        name="R9_radiolytic_drydown", t_range=[0, 100], uv=True, redox="neutral",
        settings=["surface_pool"],
        feedstocks={"HCN": 0.025, "NaCl": 5.0, "NH4Cl": 0.1, "phosphate": 0.01},
        volatile=["HCN", "NH3"],
        streams={},
        minerals={},
        basis=("Yi 2020 (10.1073/pnas.1922139117): the authors state the aim is NOT a specific geological scenario. "
               "Model: an aqueous mixture of NaCl, NH4Cl, phosphate and HCN as the only carbon source (concentrations "
               "of their initial mixture, Fig. 2A legend, used as feedstock concentrations), driven by ionizing "
               "radiation (radioactive crustal minerals, solar particles, cosmic rays; solar UV also listed) and "
               "dry-down in transiently evaporating water bodies (riverbanks, puddles, salt pans, coastlines). "
               "T range 0-100 C and redox 'neutral' are our choices (not stated). No streams claimed."),
    ),
    "R10_cyanosulfidic_ritson": dict(
        name="R10_cyanosulfidic_ritson", t_range=[0, 100], uv=True, redox="reducing",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["HCN", "HS-", "cyanoacetylene", "DCI", "formamide", "cyanamide",
                                     "glycolaldehyde", "glyceraldehyde"]},
        volatile=["HCN", "cyanoacetylene"],
        streams={"formamide": dict(ph=NAN, t=NAN, solvent="formamide", redox="unknown", species={})},
        minerals={},
        basis=("Ritson 2022 (10.1021/jacs.2c07774), Introduction and Conclusions (Scheme 6): the cyanosulfidic scenario; "
               "cyanoacetylene made in a transiently reduced atmosphere (late-accretion impacts) and needing capture; "
               "4,5-dicyanoimidazole (DCI) as the byproduct of adenine synthesis from cyanide and formamide; "
               "glycolaldehyde and glyceraldehyde from photochemical Kiliani-Fischer homologation with HS-; "
               "cyanamide (via thiourea) from HCN/HS- chemistry; some reactions in water and some in formamide "
               "(Scheme 6 magenta arrows); crystallisation at five junctures; stream confluences for sequential "
               "addition. ribo-aminooxazoline (ribo-4) is an intermediate from earlier chemistry, not a feedstock. "
               "No concentrations (INF). T range 0-100 C our choice; redox 'reducing' our classification of the "
               "cyanosulfidic scenario. The formamide stream's pH/T are not stated."),
    ),
    "R11_dap_aqueous": dict(
        name="R11_dap_aqueous", t_range=[0, 100], uv=False, redox="neutral",
        settings=["surface_pool"],
        feedstocks={s: INF for s in ["DAP", "Zn2+", "Mg2+"]},
        volatile=["NH3"],
        streams={"rain": dict(RAIN)},
        minerals={},
        basis=("Gibard 2018 (10.1038/nchem.2878, author manuscript PMC6295206): a single-pot aqueous environment "
               "(solution or paste, i.e. low water activity); DAP as the plausible phosphorylating agent, made from "
               "trimetaphosphate + ammonia at high pH (cited) or possibly schreibersite corrosion (suggested). "
               "Nucleosides, imidazole and their sources are not addressed (not feedstocks). No geological setting, "
               "T range, UV or redox stated: 0-100 C, uv False and 'neutral' are our placeholders."),
    ),
}

# =====================================================================================
# R6  Becker 2018, Nat Commun 9:163 (purine nucleosides; adenosine branch encoded)
# =====================================================================================
R6 = [
    step("B1", "malononitrile + S-methylisothiourea + NaNO2/AcOH (pH ~4) -> (hydroxyimino)malononitrile; slow "
         "evaporation and cooling crystallise the amidinium salt 2b.3", "S1", "surface_pool",
         [inp("malononitrile", 0.39, note="200 mmol in ~512 ml total (our arithmetic); text: amidinium 400 mM"),
          inp("amidinium_2b", 0.39, note="S-methylisothiourea hemisulfate 200 mmol (our arithmetic)"),
          inp("NaNO2", 0.39, note="202 mmol (our arithmetic)"),
          inp("AcOH", NAN, note="12 ml AcOH in 460 ml water; molarity not stated")],
         (4.0, 45.0, "water", "unknown"),
         {"salt_2b_3": NAN},
         out_cond=(NAN, 9.0, "water", "unknown"),
         yield_status="demonstrated",
         yield_text="45% crystalline 2b salt of 3 (90 mmol); 40-60% for salts 2a-d",
         source=D["becker2018"],
         where="Results 'Selective crystallization of an organic salt' (pH ~4, 400 mM, crystallises from ~1 M); "
               "Methods 'Methylthioamidine (2b) salt of (hydroxyimino)malononitrile (3)'",
         notes=("RT 2 h, then 45 C open to air 3-4 d until ~500 -> 200 ml, then 8-10 C overnight; crystals filtered. "
                "Conditions record the 45 C evaporation stage; output temperature 9 C = midpoint of 8-10 C (our choice). "
                "Output is a solid (concentration NaN)."),
         assumptions=["output T 9 C is the midpoint of the stated 8-10 C"]),
    step("B2", "dry-state melt of salt 2b.3 at its melting point (126 C) overnight -> nitrosopyrimidine 4b",
         "S1", "hot_soil",
         [inp("salt_2b_3", NAN, True, "crystallised salt (5.00 g), solid")],
         (NAN, 126.0, "dry", "unknown"),
         {"nitrosopyrimidine_4b": NAN},
         yield_status="demonstrated_purified",
         yield_text="'quantitative reaction mixture' used without purification; 64% after water wash (100 mg scale); 60-85% for 4a-d",
         source=D["becker2018"],
         where="Methods '2-(methylthio)-5-nitrosopyrimidine-4,6-diamine (4b)'; Results 'Nitroso-pyrimidine formation'",
         notes="Mixed salts also converted together on a 100-160 C gradient (1 C/5 min). Caution in Methods: overheating releases MeSH."),
    step("B3", "4b + Ni0 in dilute formic acid, 70 C, 2 h -> FaPy-ms2A (5b)", "S1", "surface_pool",
         [inp("nitrosopyrimidine_4b", 0.045, True, "250 mg (1.35 mmol) in 30 ml (our arithmetic); water-washed solid"),
          inp("HCOOH", NAN, note="'dilute HCOOH (20%)'; units not stated"),
          inp("Ni0", NAN, note="1.00 g Ni powder per 30 ml")],
         (NAN, 70.0, "water", "unknown"),
         {"FaPy_ms2A": NAN},
         yield_status="demonstrated_purified",
         yield_text="5b 56% isolated (500 mg 4b, 2 h, only product)",
         source=D["becker2018"],
         where="SI 'General procedure for the formation and isolation of FaPy compounds' and 'FaPyA (5c)'; Results "
               "'Formamidopyrimidine formation'",
         notes="Sealed pressure tube. pH not stated. Fe powder works for all FaPys except 5b."),
    step("B4", "isolated 5b, H2 bubbled, Ni0/dilute formic acid 70 C, 7 d -> FaPyA (5c) by desulfurisation",
         "S1", "surface_pool",
         [inp("FaPy_ms2A", 0.045, True, "isolated 5b, 250 mg (1.35 mmol) in 30 ml (our arithmetic)"),
          inp("HCOOH", NAN, note="20% formic acid"), inp("Ni0", NAN), inp("H2", NAN, note="bubbled before reaction")],
         (NAN, 70.0, "water", "unknown"),
         {"FaPyA": NAN},
         yield_status="demonstrated_purified",
         yield_text="5c 51% isolated after 7 d, only product",
         source=D["becker2018"],
         where="SI 'FaPyA (5c)'; Results para 'The 2-(methylthio)-5-nitrosopyrimidine-4,6-diamine (4b) gives...'",
         notes="Main text: 5c always forms via 5b; desulfurisation controlled by time, promoted by H2 bubbling."),
    step("B5", "FaPyA ground with ribose (15 eq), dry 100 C, 8 h -> FaPy-ribosides", "S2", "hot_soil",
         [inp("FaPyA", NAN, True, "crystallised FaPy, 0.025 mmol, solid"),
          inp("ribose", NAN, note="0.375 mmol (15 eq), solid; feedstock as claimed")],
         (NAN, 100.0, "dry", "unknown"),
         {"FaPyA_riboside": NAN},
         yield_status="demonstrated_purified",
         yield_text="intermediate not quantified; overall nucleoside yield reported after B6",
         source=D["becker2018"],
         where="SI 'Nucleoside formation using ribose and FaPy (5a-h)'; Results 'Formation of canonical and non-canonical nucleosides'"),
    step("B6", "FaPy-riboside residue in 0.5 M Et3N, 100 C sealed, 21 d -> adenosine (alpha/beta furanosides and pyranosides)",
         "S2", "surface_pool",
         [inp("FaPyA_riboside", NAN, note="dry residue from B5, carried"),
          inp("Et3N", 0.5, True, "3 ml 0.5 M Et3N; laboratory base for 'basic conditions'")],
         (NAN, 100.0, "water", "unknown"),
         {"adenosine": NAN, "adenosine_isomers": NAN},
         yield_status="demonstrated_purified",
         yield_text=("N9-nucleosides 15-60% across 6a-h ('up to 60%'); per-compound adenosine yield not stated in the "
                     "main text; beta-furanoside and beta-pyranoside major; extra regioisomers (likely N3) for A, m2A, DA "
                     "only when FaPys came from the continuous route"),
         source=D["becker2018"],
         where="SI 'Nucleoside formation using ribose and FaPy (5a-h)' (5c: 21 d); Results; Fig. 4",
         notes="pH of 0.5 M Et3N not reported."),
]
R6_H = [
    dict(procs=[dict(process="selective_separation", species="salt_2b_3", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="drying"), dict(process="transport", to_setting="hot_soil", dilution=1.0),
                dict(process="heating", t_after=126.0)],
         why="Crystals filtered from the cooled mother liquor (authors' enrichment I), then heated dry to the melt."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5),
                dict(process="selective_separation", species="nitrosopyrimidine_4b", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="transport", to_setting="surface_pool", dilution=1.0),
                dict(process="rehydration", stream="dilute_formic", f=0.5),
                dict(process="heating", t_after=70.0)],
         why=("Water dissolves unreacted salt and leaves insoluble 4b (enrichment II, 'rain shower or flooding'); 4b then "
              "meets dilute formic acid with Ni. f=0.5 for both rehydrations is our placeholder; the authors used 30 ml "
              "20% HCOOH per 250 mg 4b.")),
    dict(procs=[dict(process="drying"),
                dict(process="rehydration", stream="basic_water", f=0.5),
                dict(process="selective_separation", species="Ni2+", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="selective_separation", species="FaPy_ms2A", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="rehydration", stream="dilute_formic", f=0.5),
                dict(process="gas_exchange", gas="H2"),
                dict(process="heating", t_after=70.0)],
         why=("Authors evaporated to dryness, took up in water with K2CO3 to pH 9-10, filtered off Ni salts, concentrated "
              "(<1/10 volume, not encoded as a factor) and crystallised 5b (enrichment III), then reran it with fresh "
              "Ni/formic acid after bubbling H2. f values are placeholders.")),
    dict(procs=[dict(process="drying"),
                dict(process="rehydration", stream="basic_water", f=0.5),
                dict(process="selective_separation", species="Ni2+", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="selective_separation", species="FaPyA", property="crystallisation",
                     demonstrated_by=D["becker2018"]),
                dict(process="rehydration", stream="rain", f=0.5),
                dict(process="drying"), dict(process="transport", to_setting="hot_soil", dilution=1.0),
                dict(process="heating", t_after=100.0)],
         why=("Same FaPy workup and crystallisation; then 'washed into the same environment by rain' with ribose (a "
              "feedstock) and dried. In the lab, solid FaPy and ribose were ground together and oven-heated.")),
    dict(procs=[dict(process="transport", to_setting="surface_pool", dilution=1.0),
                dict(process="rehydration", stream="basic_water", f=0.5),
                dict(process="heating", t_after=100.0)],
         why="Residue taken up in basic solution and heated (lab: 3 ml 0.5 M Et3N, sealed tube). f is a placeholder."),
]

# =====================================================================================
# R7  Becker 2019, Science 366:76 (pyrimidine nucleosides and 5'-nucleotides)
# =====================================================================================
R7 = [
    step("P1", "cyanoacetylene + hydroxylurea (Zn2+, urea, Na2CO3) -> 3-aminoisoxazole 4", "S1", "surface_pool",
         [inp("cyanoacetylene", 0.1, note="100 umol in 1 ml"),
          inp("hydroxylurea", 0.105, True, "commercial; not an authors' feedstock (cited from NH2OH + cyanate)"),
          inp("urea", 0.4), inp("Zn2+", 0.1, note="ZnCl2"), inp("carbonate", 0.4, note="Na2CO3")],
         (10.0, RT, "water", "unknown"),
         {"isoxazole_4": 0.088},
         yield_status="demonstrated_purified",
         yield_text="4: 88% (Zn2+), 83% (Co2+) in 2 h by LC-MS; main text 80-90%; with NH2OH 17%; via disulfonate 6 from NO2-/SO2 63%",
         source=D["becker2019"],
         where="Results 'Abiotic synthesis of pyrimidine nucleosides' para 1; SI 'General procedure for the formation of 3-aminoisoxazole (4)... From hydroxyurea'",
         notes="SI: 25 C, 850 rpm, 2 h; pH 10 from main text ('slightly basic (pH 10)'). Output = 88% x 0.1 M (our arithmetic).",
         assumptions=[RT_NOTE + "; SI states 25 C, recorded as 23"]),
    step("P2", "one pot: neutralise to pH 6-7, dry down at 95 C, 2 d -> N-isoxazolyl-urea 8 (Zn2+-catalysed)",
         "S1", "surface_pool",
         [inp("isoxazole_4", 0.088, note="carried in the same pot"), inp("urea", 0.4), inp("Zn2+", 0.1)],
         (6.5, 95.0, "water", "unknown"),
         {"isoxazolylurea_8": 0.056},
         out_cond=(NAN, 95.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text="8: 56% (Zn2+), 40% (Co2+) from cyanoacetylene in one pot; from commercial 4: 88% (Zn), 68% (Co), 25% (no metal)",
         source=D["becker2019"],
         where="Results para 3 ('one-pot experiment'); SI 'N-isoxazolyl-urea (8)... One-pot prebiotic synthesis from 1'",
         tested_with=["carbonate", "hydroxylurea"],
         notes="pH 6.5 = midpoint of the stated 6-7. Neutralised with 70.4 ul conc. HCl; authors attribute this to acid rain.",
         assumptions=["pH 6.5 is the midpoint of the stated 6-7"]),
    step("P3", "ribosylation: 8 + ribose (5 eq) + boric acid, dry-down 95 C, 20 h -> N-isoxazolyl-N'-ribosyl-ureas 10a-d",
         "S2", "surface_pool",
         [inp("isoxazolylurea_8", 0.082, True, "isolated solid 8; 500 ul of 100 mM in 608 ul total (our arithmetic)"),
          inp("ribose", 0.41, note="83 ul of 3 M (our arithmetic); feedstock as claimed"),
          inp("borate", 0.021, note="25 ul of 500 mM boric acid (our arithmetic)")],
         (NAN, 95.0, "water", "unknown"),
         {"ribosylurea_10": 0.078},
         out_cond=(NAN, 95.0, "dry", "unknown"),
         yield_status="demonstrated_purified",
         yield_text="10a-d 95% (pyranosides 10c/d dominate initially); borax or synthetic luneburgite >70%",
         source=D["becker2019"],
         where="Results para 4; SI 'N-isoxazolyl-N'-ribosyl-urea (10a-d) Prebiotic synthesis'; Fig. S4a, Fig. S5",
         notes="pH not stated (Fig. S5: 'slightly basic' vs 'more acidic' give different glycosylation). A dry grinding variant (oven 95 C overnight) also given."),
    step("P4", "furanoside enrichment: heat 10a-d in 125 mM borax, 95 C, 2.5-5 h -> furanosides 10a/b", "S2", "surface_pool",
         [inp("ribosylurea_10", NAN, note="'the mixture obtained in a)' (Fig. S4)"), inp("borate", 0.125, note="borax")],
         (NAN, 95.0, "water", "unknown"),
         {"ribosylurea_10ab": NAN, "isoxazolylurea_8": NAN, "ribose": NAN},
         yield_status="demonstrated",
         yield_text="furanosides 10a/b 54% (Fig. 2B); only traces of pyranosides after 5 h; partial hydrolysis back to 8 + ribose",
         source=D["becker2019"],
         where="Results para 4; Fig. 2B; Fig. S4b legend (125 mM borax, 95 C, 2.5 h)",
         notes="'Slightly basic conditions'; pH not given as a number."),
    step("P5", "reductive N-O cleavage: 10a/b + Fe2+ (FeS2) + DTT + luneburgite in 75 mM Na2CO3, Ar, 100 C, 4 h -> cytidines 11 (+ uridines 12)",
         "S2", "surface_pool",
         [inp("ribosylurea_10ab", 0.2, True, "0.1 mmol 3:1 alpha/beta-furanoside mixture in 0.5 ml (our arithmetic)"),
          inp("luneburgite", 0.2, True, "synthetic mineral, 1 eq (solid)"),
          inp("DTT", 0.3, True, "1.5 eq; commercial thiol, not an authors' feedstock"),
          inp("FeS2", 0.1, note="0.5 eq solid; or 0.0001-0.001 eq ammonium iron(II) sulfate"),
          inp("carbonate", 0.075, note="75 mM Na2CO3")],
         (NAN, 100.0, "water", "reducing"),
         {"cytidine": 0.17, "uridine": NAN},
         yield_status="demonstrated_purified",
         yield_text="cytidines 11 combined 85% with luneburgite (alpha ~ beta furanosides; little pyranoside); uridines 12a/b small",
         source=D["becker2019"],
         where="Results 'Selective one-pot formation...' para 1; Fig. 2C; SI 'General procedure nucleoside formation' and 'one-pot nucleotide formation'",
         notes=("Argon-degassed solutions (hence 'reducing'). Output 'cytidine' = all four isomers combined, 85% x 0.2 M "
                "(our arithmetic). The 3:1 alpha/beta input ratio matches the SI's synthetic-reference preparation, so the "
                "input was likely synthetic, not P4 product (our inference). Without minerals: 100 mM Na2CO3/50 mM boric acid pH 9.7."),
         assumptions=["input 10a/b taken as the synthetic 3:1 mixture (inferred from the stated ratio)"]),
    step("P6", "one pot: add solid urea (40 eq), dry down at 85 C, 20 h with luneburgite -> 5'-CMP/CDP (+ UMP/UDP)", "S2", "surface_pool",
         [inp("cytidine", 0.17, note="carried in the same pot"),
          inp("urea", 8.0, note="4 mmol into 0.5 ml (our arithmetic)"),
          inp("luneburgite", 0.2, True, "carried; phosphate source")],
         (NAN, 85.0, "water", "unknown"),
         {"pyrimidine_5prime_phosphates": 0.032},
         out_cond=(NAN, 85.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text="phosphorylated nucleosides 19% relative to cytidine; furanoside:pyranoside 4:1 -> 17:1; 5'-mono and 5'-di(pyro)phosphates",
         source=D["becker2019"],
         where="Results 'Selective one-pot formation...' para 1; Fig. 3; SI 'General procedure for one-pot nucleotide formation'",
         tested_with=["DTT", "FeS2", "carbonate", "uridine"],
         notes="Urea dissolved at 65 C, then a 25 ul aliquot kept at 85 C, 20 h open to air. Output 19% x 0.17 M (our arithmetic). Struvite variant needs oxalic acid."),
]
R7_H = [
    dict(procs=[dict(process="same_pot"),
                dict(process="mixing", stream="acid_rain", f=0.066, ph_after=6.5),
                dict(process="heating", t_after=95.0)],
         why=("Same vessel. Lab: 70.4 ul conc. HCl into ~1 ml (volume fraction 0.066 used as f); the authors attribute the "
              "neutralisation to acid rain (pH 3), so the named stream is acid_rain.")),
    dict(procs=[dict(process="rehydration", stream="carbonate_water", f=0.5),
                dict(process="selective_separation", species="Zn2+", property="crystallisation",
                     demonstrated_by=D["becker2019"]),
                dict(process="selective_separation", species="isoxazolylurea_8", property="crystallisation",
                     demonstrated_by=D["becker2019"]),
                dict(process="rehydration", stream="rain", f=0.5),
                dict(process="heating", t_after=95.0), dict(process="drying")],
         why=("Authors' enrichment: carbonated water dissolves 4, urea and 8, leaving Zn as hydroxide/carbonate; the "
              "supernatant concentrates and 8 crystallises (55%; shown on the batch made from commercial 4, with K2CO3, "
              "5 d at RT). Then 'flooding or mixing of environments' brings ribose (feedstock); dry-down at 95 C. "
              "The concentration factor is not stated, so no evaporation process is encoded. f values are placeholders.")),
    dict(procs=[dict(process="rehydration", stream="carbonate_water", f=0.5)],
         why="Dry ribosylation mixture heated in 125 mM borax ('slightly basic'); borate is a feedstock. f is a placeholder."),
    dict(procs=[dict(process="rehydration", stream="carbonate_water", f=0.5),
                dict(process="heating", t_after=100.0)],
         why=("Reduction run in 75 mM Na2CO3 under argon at 100 C. The source started from a 3:1 alpha/beta-furanoside "
              "mixture, apparently synthetic, not the P4 product; no separation of furanosides from P4 is shown. "
              "Argon degassing has no process on the list.")),
    dict(procs=[dict(process="same_pot"), dict(process="cooling", t_after=85.0)],
         why="Same pot: solid urea added (feedstock), dissolved at 65 C, aliquot dried at 85 C."),
]

# =====================================================================================
# R8  Xu 2020, Nature 582:60 (dA, dI with C and U; Fig. 4 Route A, bisulfite)
# =====================================================================================
R8 = [
    step("X1", "1:1 alpha/beta-2-thiocytidine (13 + 3) + nitrous acid, pH 4 -> alpha-anhydrocytidine 12 + cytidine",
         "S2", "surface_pool",
         [inp("alpha_thiocytidine", 0.0078, True, "1.0 mg (0.004 mmol) in 0.5 ml (our arithmetic); from earlier synthesis"),
          inp("beta_thiocytidine", 0.0078, True, "1.0 mg in 0.5 ml (our arithmetic)"),
          inp("nitrite", 0.08, note="NaNO2 0.04 mmol"), inp("phosphate", 0.1, note="Na2HPO4 0.05 mmol")],
         (4.0, RT, "water", "unknown"),
         {"anhydrocytidine_12": 0.0078, "cytidine": 0.0042, "thiouridine": 0.0013, "uridine": 0.0008},
         yield_status="demonstrated_purified",
         yield_text="12: 100% from 13 (8 h); from 3: cytidine 54%, 2-thiouridine 17%, uridine 10%; 12 stable under these conditions",
         source=D["xu2020"],
         where="Main text 'Systems-level Prebiotic Plausibility' (route A); SI 'Reactions of a mixture of 2-thiocytidine 3 and alpha-2-thiocytidine 13 with nitrous acid'",
         notes="pH set to 4.0 with 1 M HCl; 10% D2O. Output concentrations = yields x 7.8 mM (our arithmetic).",
         assumptions=[RT_NOTE]),
    step("X2", "dry-state tethered glycosylation: 12 + 8-mercaptoadenine 16 + MgCl2 (pH 8, dried), 150 C, 1.5 d -> thioanhydroadenosines 18 (N9) + 19 (N7)",
         "S2", "evaporite",
         [inp("anhydrocytidine_12", 0.001, True, "3.0 mg weighed in 10 ml before drying; not the X1 mixture"),
          inp("mercaptoadenine_16", 0.002, True, "3.0 mg weighed"),
          inp("Mg2+", 0.002, note="MgCl2 2.0 mg in 10 ml")],
         (NAN, 150.0, "dry", "unknown"),
         {"thioanhydroA_18": NAN, "thioanhydroA_19": NAN, "cytidine": NAN, "cytosine": NAN},
         yield_status="demonstrated_purified",
         yield_text="18 26%, 19 34% from 12 with cytidine present (95% of cytidine survives); without cytidine 26%/42%; from 15 with MgCl2 39%/48%",
         source=D["xu2020"],
         where="SI 'Dry state reaction of a mixture of alpha-anhydrocytidine 12, cytidine 1 and 8-mercaptoadenine 16 ... bisulfite'; main text Fig. 2 paragraph",
         tested_with=["cytidine"],
         notes="Solution adjusted to pH 8.0, concentrated, redissolved and concentrated 3x, then 150 C dry. Cytidine (3.0 mg, weighed) was added alongside."),
    step("X3", "UV 254 nm photoreduction with bisulfite + ferrocyanide, pH 7, 6 h -> deoxyadenosine 7 (+ 8-mercapto-dA 26), N7 isomers destroyed",
         "S2", "surface_pool",
         [inp("thioanhydroA_18", NAN, note="crude X2 residue, carried"),
          inp("bisulfite", 0.0625, note="0.05 mmol in 0.8 ml (our arithmetic); SI writes 'Na2SO4' (likely sulfite; main text: bisulfite)"),
          inp("ferrocyanide", 0.00625, note="K4Fe(CN)6 0.005 mmol in 0.8 ml (our arithmetic)")],
         (7.0, NAN, "water", "reducing"),
         {"dA": NAN, "mercapto_dA_26": NAN, "cytidine": NAN},
         yield_status="demonstrated",
         yield_text="step yield not reported separately in route A; on synthetic 18 alone: dA 51% + 26 23%; on 18/19 mixture: 44% + 18%, N7 products destroyed",
         source=D["xu2020"],
         where="SI route A procedure (photoreduction paragraph); main text photoreduction paragraphs; Table S3",
         tested_with=["cytidine"],
         notes="Degassed water (recorded as reducing). Temperature not stated. Cytidine alone is 80% destroyed by this irradiation; 18 protects it (Extended Data Fig. 7)."),
    step("X4", "nitrous acid, pH 4, ~2 d -> dA + dI (N7-dA hydrolysed) alongside C and U", "S2", "surface_pool",
         [inp("dA", NAN, note="carried"), inp("nitrite", 0.1125, note="NaNO2 0.09 mmol in 0.8 ml (our arithmetic)"),
          inp("phosphate", 0.125, note="NaH2PO4 0.10 mmol in 0.8 ml (our arithmetic)")],
         (4.0, RT, "water", "unknown"),
         {"dA": NAN, "dI": NAN, "cytidine": NAN, "uridine": NAN},
         yield_status="demonstrated",
         yield_text="dA 10%, dI 9% from 12 over three steps (X2-X4); final dA:dI:C:U 10:9:67:14; 84% of C+U persisted",
         source=D["xu2020"],
         where="SI route A procedure (nitrous acid paragraph); main text 'Systems-level Prebiotic Plausibility'; Fig. 4",
         tested_with=["cytidine", "mercapto_dA_26"],
         notes="pH adjusted to 4 with 1 M HCl.",
         assumptions=[RT_NOTE + " (source gives no temperature for this step; nitrous acid steps elsewhere at RT)"]),
]
R8_H = [
    dict(procs=[dict(process="drying"), dict(process="transport", to_setting="evaporite", dilution=1.0),
                dict(process="heating", t_after=150.0)],
         why=("NOT carried in the source: route A's glycosylation started from weighed 12 and cytidine, not from the X1 "
              "mixture, and 16 was supplied (its synthesis is branch R8b). Physical operations encoded: pH adjusted to 8 "
              "(not on the list), repeated evaporation to dryness, 150 C dry state. Authors: 12 and 16 'brought together, "
              "perhaps by converging streams that then undergo evaporation'.")),
    dict(procs=[dict(process="transport", to_setting="surface_pool", dilution=1.0),
                dict(process="rehydration", stream="rain", f=0.5),
                dict(process="uv_irradiation")],
         why=("Crude residue used directly: dissolved in 0.8 ml degassed water with sulfite and ferrocyanide (feedstocks), "
              "pH set to 7 with HCl, irradiated 254 nm. f is a placeholder.")),
    dict(procs=[dict(process="drying"), dict(process="rehydration", stream="rain", f=0.5)],
         why=("Lyophilised, redissolved in 0.8 ml water with NaNO2 and NaH2PO4 (feedstocks); pH brought to 4 with 1 M HCl, "
              "which no listed process represents. f is a placeholder.")),
]

R8B = [
    step("X5", "adenine hydrolysis in phosphate buffer pH 8, 138 C, 10-12 d -> 4,5,6-triaminopyrimidine (TAP)", "S2", "surface_pool",
         [inp("adenine", NAN, note="500 mg (or 1 g); buffer volume not stated"), inp("phosphate", 1.0, note="1 M sodium phosphate buffer")],
         (8.0, 138.0, "water", "unknown"),
         {"TAP": NAN, "AICA": NAN, "adenine": NAN, "formate": NAN},
         out_cond=(NAN, 4.0, "water", "unknown"),
         yield_status="demonstrated",
         yield_text="TAP 2-3% (8-9% based on recovered adenine); cooled supernatant AICA:TAP:adenine ~4:2:1",
         source=D["xu2020"],
         where="Main text (TAP paragraph); SI 'Adenine Hydrolysis'; Table S1",
         notes="Sealed tube. Supernatant stored at 4 C 24 h (recorded as output T). Main text: environment would 'continuously generate TAP' enriched down a thermal gradient."),
    step("X6", "adenine hydrolysate + NH4SCN, evaporated, dry 150 C, 16 h -> 8-mercaptoadenine 16", "S2", "evaporite",
         [inp("TAP", NAN, note="100 ul crude hydrolysate + 1 ml water, carried"),
          inp("NH4SCN", 0.33, note="28 mg (0.37 mmol) in 1.1 ml (our arithmetic)")],
         (NAN, 150.0, "dry", "unknown"),
         {"mercaptoadenine_16": NAN},
         yield_status="demonstrated",
         yield_text="from hydrolysate: 16 confirmed by spiking, not quantified; from commercial TAP: TAP:16 0:100 with thiourea 150 C 16 h (Table S2)",
         source=D["xu2020"],
         where="SI 'Synthesis of 8-mercaptoadenine 16' ('From adenine hydrolysate'); Table S2",
         notes="Solution pH 7.5 measured before evaporation. 16 crystallises from water over weeks (SI)."),
]
R8B_H = [
    dict(procs=[dict(process="selective_separation", species="adenine", property="crystallisation",
                     demonstrated_by=D["xu2020"]),
                dict(process="rehydration", stream="rain", f=0.91),
                dict(process="drying"), dict(process="transport", to_setting="evaporite", dilution=1.0),
                dict(process="heating", t_after=150.0)],
         why=("Cooling precipitates adenine and enriches TAP in the supernatant (Table S1). 100 ul supernatant + 1 ml water "
              "(f = 1/1.1) with NH4SCN (feedstock), evaporated and heated dry.")),
]

# =====================================================================================
# R9  Yi 2020, PNAS 117:13267 (2-aminooxazole and 2-aminoimidazole from HCN)
# =====================================================================================
R9 = [
    step("Y1", "gamma radiolysis of NaCN in brine (NaCl, NH4Cl, Pi), pH 7, ~1 d -> cyanamide + glyceronitrile (+ others)",
         "S1", "surface_pool",
         [inp("HCN", 0.025, note="as NaCN"), inp("NaCl", 5.0), inp("NH4Cl", 0.1), inp("phosphate", 0.01)],
         (7.0, 24.0, "water", "reducing"),
         {"cyanamide": 6.5e-4, "glyceronitrile": 1.0e-4},
         yield_status="demonstrated",
         yield_text="cyanamide 0.65 mM (2.6% from CN-), glyceronitrile 0.10 mM (1.2%); no free glycolaldehyde",
         source=D["yi2020"],
         where="Fig. 2A legend (50 ml, 25 mM NaCN, 0.1 M NH4Cl, 5 M NaCl, 10 mM Pi, pH 7, N2, ~2.2 kGy/h, ~48 kGy, ~24 C); Table 1 (dagger rows)",
         notes="Prepared under N2 (recorded as reducing). Without NaCl no cyanamide forms; Pi > ~0.1 M suppresses it."),
    step("Y2", "dry-down: concentrate ~10x under reduced pressure at 35 C; HCN loss frees glycolaldehyde from glyceronitrile",
         "S1", "surface_pool",
         [inp("glyceronitrile", 1.0e-4, note="carried"), inp("cyanamide", 6.5e-4, note="carried")],
         (7.0, 35.0, "water", "unknown"),
         {"cyanamide": 2.8e-3, "glyceronitrile": 5.7e-4, "glycolaldehyde": 1.6e-4},
         yield_status="demonstrated",
         yield_text="after ~10x volume reduction: cyanamide 2.8 mM, glyceronitrile 0.57 mM, glycolaldehyde 0.16 mM (0.13% from CN-)",
         source=D["yi2020"],
         where="Fig. 2A legend (50 -> ~5 ml at 35 C); Results 'gamma Radiolysis Combined with Dry-Down...'; Table 1 (double-dagger rows)",
         notes="Large amount of NaCl precipitated; cyanamide reached ~half the theoretical 6.5 mM. Fig. 1 control (pure reagents) shows the same release over three dry-wet cycles."),
    step("Y3", "heat the concentrated mixture at 50 C, 3 h, pH 8 -> 2-aminooxazole + 2-aminoimidazole", "S1", "surface_pool",
         [inp("glycolaldehyde", 1.6e-4, note="carried"), inp("cyanamide", 2.8e-3, note="carried"),
          inp("phosphate", NAN, note="carried; ~10x the initial 10 mM if none lost (not measured)"),
          inp("NH4Cl", NAN, note="carried; not measured after dry-down")],
         (8.0, 50.0, "water", "unknown"),
         {"2-aminooxazole": 9.0e-5, "2-aminoimidazole": 5.5e-5, "imidazolone_3": NAN, "aminoacetonitrile": NAN, "serinenitrile": NAN},
         yield_status="demonstrated",
         yield_text="2-aminooxazole 0.09 mM (0.11% from CN-; ~69% from free glycolaldehyde), 2-aminoimidazole 0.055 mM (0.066%; ~34%)",
         source=D["yi2020"],
         where="Fig. 2A legend; Fig. 2B; Table 1 (section-sign rows)",
         tested_with=["glyceronitrile", "NaCl", "aminoacetonitrile", "serinenitrile"],
         notes="At pH 7 2-aminooxazole still forms in lower yield, favouring 2-aminoimidazole (SI Fig. S20, not opened). pH later set to 6 only for NMR resolution."),
]
R9_H = [
    dict(procs=[dict(process="same_pot")], why="Same solution concentrated under reduced pressure (the dry-down is step Y2)."),
    dict(procs=[dict(process="selective_separation", species="NaCl", property="crystallisation",
                     demonstrated_by=D["yi2020"]),
                dict(process="heating", t_after=50.0)],
         why=("A sample of the homogeneous solution was taken off the precipitated NaCl, mixed 450 ul + 50 ul D2O "
              "(not encoded), pH adjusted to 8 (reagent not stated; not on the list), heated to 50 C.")),
]

# =====================================================================================
# R10  Ritson 2022, JACS (CV-DCI as cyanoacetylene surrogate -> ribo-anhydrocytidine)
# =====================================================================================
R10 = [
    step("T1", "4,5-dicyanoimidazole (DCI) suspended in water at pH 5.2 + cyanoacetylene -> N-cyanovinyl-DCI (CV-DCI), crystallises overnight",
         "S1", "surface_pool",
         [inp("DCI", NAN, note="concentration in SI (not opened)"), inp("cyanoacetylene", NAN, note="concentration in SI (not opened)")],
         (5.2, NAN, "water", "unknown"),
         {"CV_DCI": NAN},
         yield_status="demonstrated",
         yield_text="clean addition over hours (1H NMR); crystals of CV-DCI by next morning; yield not given in main text",
         source=D["ritson2022"],
         where="Results and Discussion para 1; Scheme 2 (SI Figs. S1-S3 not opened)",
         notes="H2O/D2O. Solid CV-DCI unchanged after 6 months on the bench; little reaction with cyanide, phosphate, adenosine, ammonia in water."),
    step("T2", "CV-DCI (200 mM) + ribo-aminooxazoline (100 mM) in formamide, 50 C, 2 d -> ribo-anhydrocytidine 6",
         "S2", "surface_pool",
         [inp("CV_DCI", 0.2, True, "crystalline CV-DCI dissolved in formamide"),
          inp("ribo_aminooxazoline", 0.1, True, "crystalline ribo-4 from earlier chemistry; not made in this paper")],
         (NAN, 50.0, "formamide", "unknown"),
         {"ribo_anhydrocytidine": 0.05, "trans_cyanovinyl_21": 0.014},
         yield_status="demonstrated_purified",
         yield_text="6 ~50% after 2 d (+ ~14% trans-cyanovinyl 21); UV of the crude raises 6 from ~48% to ~55% (neat formamide) or ~58% (diluted in water)",
         source=D["ritson2022"],
         where="Results and Discussion para 2; Scheme 2 (SI Figs. S8-S11 not opened)",
         notes="In water the same reaction gave low conversion (poor solubility). Outputs = yield x 100 mM (our arithmetic). Wavelength of the UV step not in main text."),
]
R10_H = [
    dict(procs=[dict(process="selective_separation", species="CV_DCI", property="crystallisation",
                     demonstrated_by=D["ritson2022"]),
                dict(process="drying"),
                dict(process="rehydration", stream="formamide", f=0.5),
                dict(process="heating", t_after=50.0)],
         why=("CV-DCI crystallises and was recovered and dried; then dissolved in formamide (the authors' formamide "
              "environment, Scheme 6) with ribo-4 at 50 C. ribo-4 is supplied crystalline; its crystallisation is "
              "cited, not shown here, so no separation is encoded for it. f is a placeholder.")),
]

# =====================================================================================
# R11  Gibard 2018, Nat Chem 10:212 (DAP phosphorylation; uridine paste reaction)
# =====================================================================================
R11 = [
    step("G1", "uridine + DAP (5 eq, replenished) + imidazole (5 eq) as a paste with drops of water, RT, 36 d -> uridine-2',3'-cyclophosphate + oligouridylates",
         "S2", "surface_pool",
         [inp("uridine", NAN, True, "commercial nucleoside, 4.1 mmol; source not addressed by authors"),
          inp("DAP", NAN, note="5 equiv., re-added when consumed (10-15 d); lab-synthesised from phenyl phosphorodiamidate"),
          inp("imidazole", NAN, True, "5 equiv.; commercial, not claimed as a feedstock")],
         (NAN, RT, "paste", "unknown"),
         {"cUMP": NAN, "oligoU_cyclic": NAN, "cUMP_5prime_amidophosphate": NAN},
         yield_status="demonstrated_purified",
         yield_text="c-UMP 83% conversion (65% isolated, 1 g scale, 36 d); 89% at 0.1 mmol with 50 eq DAP (18 d); oligouridylates to tetramer detected, not quantified",
         source=D["gibard2018"],
         where="Results para 2 ('paste-reaction'); Fig. 1b; SI Method C and Supplementary Table 1 entries 14-16",
         notes=("Paste concentrations not definable (NaN). On dissolution for NMR the paste read pH 8.5-9.5 (not recorded "
                "as the reaction pH). Solution alternative (Method B, pH 7, 0.1 M uridine, 5 eq DAP, Mg/Zn, 1 eq imidazole): "
                "20-29% c-UMP in 28 d, no oligomers reported. A/C/G nucleosides: c-AMP 31%, c-CMP 27%, c-GMP 27% in solution."),
         assumptions=[RT_NOTE]),
]
R11_H = []

# =====================================================================================
PATHWAYS = [
    dict(id="R6", label="Becker 2018 purine nucleosides via nitroso-pyrimidines (adenosine branch)",
         scenario="R6_geothermal_wetdry", steps=R6, handoffs=R6_H,
         note=("Adenosine branch 4b -> 5b -> 5c -> A. The G, m2G, m22G, m1G, DA and m2A branches (hydrolysis/aminolysis "
               "of 4a-d) are not encoded. Every intermediate is crystallised or washed; B2-B6 used isolated material.")),
    dict(id="R7", label="Becker 2019 pyrimidine nucleosides and 5'-nucleotides via isoxazolyl-urea",
         scenario="R7_surface_basins", steps=R7, handoffs=R7_H,
         note=("Pyrimidine route of Fig. 1A/2/3. The purine-coupled one-pot (Fig. 5A) is not encoded. Legal copy: accepted "
               "manuscript on Open Access LMU.")),
    dict(id="R8", label="Xu 2020 dA/dI with C and U (Fig. 4 route A)",
         scenario="R8_cyanosulfidic_xu", steps=R8, handoffs=R8_H,
         note="Route A of the systems-level experiment. 8-mercaptoadenine synthesis is branch R8b; route B (15, H2S) not encoded."),
    dict(id="R8b", label="Xu 2020 branch: adenine -> TAP -> 8-mercaptoadenine",
         scenario="R8_cyanosulfidic_xu", steps=R8B, handoffs=R8B_H,
         note="Feeds 16 into R8 step X2 in the authors' scheme; not run in sequence with R8 in the source."),
    dict(id="R9", label="Yi 2020 radiolysis + dry-down: HCN -> 2-aminooxazole / 2-aminoimidazole",
         scenario="R9_radiolytic_drydown", steps=R9, handoffs=R9_H,
         note="Fig. 2A experiment; the only route here run start to finish without reagent additions (pH adjustment excepted)."),
    dict(id="R10", label="Ritson 2022 CV-DCI capture of cyanoacetylene -> ribo-anhydrocytidine",
         scenario="R10_cyanosulfidic_ritson", steps=R10, handoffs=R10_H,
         note="The 2-aminothiazole synthesis and the cited aminal sugar separation are described in NOTES.md, not encoded."),
    dict(id="R11", label="Gibard 2018 DAP paste phosphorylation of uridine -> c-UMP and oligo-U",
         scenario="R11_dap_aqueous", steps=R11, handoffs=R11_H,
         note="Single step, no hand-offs. Legal copy: NIH author manuscript PMC6295206."),
]
