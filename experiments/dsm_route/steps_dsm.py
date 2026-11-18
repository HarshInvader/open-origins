"""Step table for the borate Discontinuous Synthesis Model (DSM), board task #26.

Pre-registration: docs/prereg/dsm_route_score.md (sealed; sha256 in HASHES.txt).
Same conventions as experiments/pathway_map/steps.py (read-only import; that folder is not edited):
NaN = not reported (checks become UNASSESSED), INF = scenario feedstock with no stated concentration,
`unread` steps are given to the scorer as `missing`.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pathway_map"))
import steps as ST  # noqa: E402

NAN, INF, inp, step = ST.NAN, ST.INF, ST.inp, ST.step

D = dict(
    hirakawa2025="10.1073/pnas.2516418122",   # PMC12745811, full text read
    kawai2019="10.1089/ast.2017.1800",        # PMC6459274, full text read
    kim2011="10.1021/ja201769f",              # abstract only (paywalled)
    kim2021="10.1089/ast.2020.2264",          # abstract only (paywalled)
    jerome2022="10.1089/ast.2022.0027",       # PMC9233534, full text read
)

SCENARIO = dict(
    name="borate_aquifer", t_range=[0, 100], uv=True, redox="neutral",
    settings=["atmosphere", "aquifer"],
    feedstocks={s: INF for s in ["HCHO", "glycolaldehyde", "bisulfite", "borate", "Ca2+", "Ni2+", "phosphate",
                                 "CTMP", "basalt_glass", "NH3", "urea", "adenine", "guanine", "cytosine",
                                 "uracil", "DAP"]},
    volatile=["NH3"],
    streams={"rain": dict(ph=7.0, t=23.0, solvent="water", redox="neutral", species={})},
    minerals={},
    basis=("Hirakawa 2025 (10.1073/pnas.2516418122) Fig. 1 and text: HCHO and ppm glycolaldehyde from a CO2/N2/H2O "
           "atmosphere, trapped by mantle SO2 as sulfonate adducts; rain delivers them to intermittently irrigated, "
           "basalt-constrained aquifers holding borate; nucleobases, NH3 and urea from an atmosphere transiently "
           "reduced by an impactor; condensed phosphate (CTMP) from glasses/volcanism; amidophosphates (DAP) cited "
           "to Gibard 2019 (not opened). All feedstock concentrations unstated (INF). Redox class 'neutral' per the "
           "authors' redox-neutral mantle. Rain pH 7 is our assumption (authors expect pH 6.5-7.0 in aquifers)."),
)

RT = 23.0  # 'room temperature' in the sources; 23 C is our stated assumption (same as the pond route)

DSM = [
    step("D1", "HCHO and glycolaldehyde trapped as bisulfite adducts (HMS etc.)", "S1", "atmosphere",
         [inp("HCHO", NAN), inp("glycolaldehyde", NAN), inp("bisulfite", NAN)],
         (NAN, 25.0, "water", "unknown"),
         {"HMS": NAN, "glycolaldehyde_bisulfite": NAN},
         yield_status="demonstrated",
         yield_text=">99% of glycolaldehyde consumed into the adduct (1:1 with NaHSO3, 25 C); HMS stable as a solid at 90 C",
         source=D["kawai2019"], where="Results 'Reaction of sulfite with glycolaldehyde...'; Methods (HMS synthesis)",
         notes="pH of adduct formation not given as a number. Reagents commercial, but all are scenario feedstocks."),
    step("D2", "borate-moderated carbohydrate maturation -> pentose-borate complexes", "S1", "aquifer",
         [inp("HMS", NAN), inp("glycolaldehyde_bisulfite", NAN), inp("borate", NAN)],
         (NAN, NAN, "water", "unknown"),
         {"pentose_borate": NAN, "ribose": NAN},
         yield_status="unread",
         yield_text="Kim 2011 abstract: borate, molybdate and Ca minerals guide formation of tetroses, heptoses and pent(ul)oses incl. ribose, 'hands off'; no yield in abstract",
         source=D["kim2011"], where="abstract (Europe PMC); outputs as claimed by Hirakawa 2025 Fig. 1",
         notes=("Kawai 2019 (read in full) runs a model of this step (HMS + dihydroxyacetone, borate-carbonate, pH 10.5, "
                "65 C) and states the products are 'mainly erythro- and threo-branched pentoses (Kim et al., 2011)'. "
                "Hirakawa 2025 says chirality/linear pentoses need a Bilik or retro-aldol step not demonstrated here. "
                "Ribose is listed as an output only because the authors claim it (pre-registered choice in favour of the route)."),
         assumptions=["ribose counted as produced (authors' claim), not shown in a source we read"]),
    step("D3", "ribose + diamidophosphate (+borate) -> ribose 1,2-cyclic phosphate (RCP)", "S2", "aquifer",
         [inp("ribose", 0.2, True, "commercial D-ribose (Wako)"), inp("DAP", 0.2, note="lab-synthesised; scenario feedstock by pre-registered choice"),
          inp("borate", 0.4), inp("phosphate", 0.8, note="800 mM phosphate buffer")],
         (7.0, RT, "water", "unknown"),
         {"RCP": 0.0529, "DAP": 0.0194, "borate": 0.4, "phosphate": 0.8},
         out_cond=(8.5, RT, "water", "unknown"),
         yield_status="demonstrated_purified",
         yield_text="RCP 52.9 +/- 0.5 mM from 200 mM ribose at 48 h with borate (~26%); 13.3 mM without borate",
         source=D["hirakawa2025"], where="Table 1; Fig. 3 legend (start pH ~6.8-7, end ~8.5, r.t.); Methods 3.3",
         notes="Variant with CTMP + 5% NH3 instead of DAP (pH ~10.4) gave only 'small peaks' of RCP after 4 days (not quantified)."),
    step("D4", "RCP + adenine + Ca2+ in the same pot, aliquot dried at 90 C -> adenosine 2'-phosphate and 2',3'-cyclic phosphate",
         "S2", "aquifer",
         [inp("RCP", 0.0529, note="formed in the same pot; concentration not reported for this variant, D3 value used"),
          inp("adenine", 0.005), inp("Ca2+", 0.005)],
         (NAN, 90.0, "dry", "unknown"),
         {"cAMP": NAN, "AMP_2": NAN},  # cAMP = adenosine 2',3'-cyclic phosphate (same name as Caimi's input); renamed from cAMP_23 after first run, disclosed
         out_cond=(NAN, 90.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text=("one-pot: adenosine 2',3'-cyclic phosphate and 2'-phosphate assigned by LC-MS/MS, not quantified; "
                     "from pure RCP (Kim & Benner 2017 as reported by Hirakawa): ~17% A 2'-P, C 7%, G 0.3%, U 0.8%"),
         source=D["hirakawa2025"], where="Section 1.5; Fig. 4; Methods 3.4",
         tested_with=["ribose", "DAP", "borate", "ACP"],
         notes=("The one-pot contained ribose 200 mM, DAP 200 mM, borax 100 mM (400 mM B), adenine 5 mM, CaCl2 5 mM, no "
                "phosphate buffer; r.t. 24-72 h; 20 ul aliquot heated to dryness 24 h at 90 C. Free adenosine is not "
                "reported as a product; a faster peak 'includes adenosine monophosphates'. Label 'demonstrated' is "
                "generous: yield is qualitative for these inputs."),
         assumptions=["RCP concentration in the one-pot taken as the D3 (Table 1) value"]),
    step("D5", "borate-guided 5'-phosphorylation of nucleosides with Ni2+, CTMP, urea, evaporative heating -> NTPs",
         "S2", "aquifer",
         [inp("adenosine", NAN, note="nucleoside input per abstract; purity not stated in abstract"),
          inp("borate", NAN), inp("Ni2+", NAN), inp("CTMP", NAN), inp("urea", NAN)],
         (NAN, NAN, "unknown", "unknown"),
         {"ATP": NAN, "UTP": NAN, "GTP": NAN, "CTP": NAN, "NDP": NAN, "NMP_5": NAN},
         yield_status="unread",
         yield_text="Kim & Benner 2021 abstract: 2-3% nucleoside 5'-triphosphates; total 5'-phosphorylation ~30%",
         source=D["kim2021"], where="abstract (Europe PMC)",
         notes="Hirakawa 2025 Step (5): 'regiochemical 5'-phosphorylation ... of 2',3'-borate complexed nucleosides'.",
         assumptions=["outputs listed for all four NTPs (abstract says 'nucleoside 5'-triphosphates' generically)"]),
    step("D6", "NTPs oligomerise on basalt glass (with borate) -> long RNA", "S3", "aquifer",
         [inp("ATP", 3e-6, True, "commercial NTP, 3 uM each"), inp("UTP", 3e-6, True, "commercial"),
          inp("GTP", 3e-6, True, "commercial, alpha-32P label"), inp("CTP", 3e-6, True, "commercial"),
          inp("basalt_glass", NAN)],
         (7.5, 25.0, "water", "unknown"),
         {"RNA_oligomers": NAN},
         yield_status="demonstrated_purified",
         yield_text="2e-3 pmol triphosphate polymerised per hour per g glass (25 C, pH 7.5); products >100 nt by gel; stable for months",
         source=D["jerome2022"], where="Jerome 2022 Abstract, Results; Hirakawa 2025 Section 1.6 and Fig. 5 (25 mM borate, pH 6.5-9, 3 weeks)",
         tested_with=["borate"],
         notes="Hirakawa: no inhibition by 25 mM borate at pH 6.5 and 7.5; yields higher than in unbuffered water."),
]

DSM_H = [
    dict(procs=[dict(process="transport", to_setting="aquifer", dilution=1.0)],
         why="Rain carries the adducts from the atmosphere into the aquifer (authors' scenario); no dilution, favourable."),
    dict(procs=[dict(process="same_pot")], why="From an unread step; conditions unknown."),
    dict(procs=[dict(process="same_pot"), dict(process="heating", t_after=90.0), dict(process="drying")],
         why="The source ran this in one pot: aliquot of the RCP mixture with adenine and Ca2+, heated to dryness at 90 C."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5)],
         why="Rewet the dried residue; D5 conditions are unread."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5)],
         why="Rewet the evaporated phosphorylation residue onto basalt glass; D5 end conditions are unread."),
]

# Branch DSM-b: D1-D4, then the Caimi 2025 cyclic-nucleotide polymerisation (P2 from task #4).
_P2 = copy.deepcopy(next(s for s in ST.POND if s["id"] == "P2"))
_P2["setting"] = "aquifer"   # DEVIATION from 'unchanged' (disclosed in RESULTS.md): pond -> aquifer, in favour of the route
DSM_B = DSM[:4] + [_P2]
DSM_B_H = DSM_H[:3] + [
    dict(procs=[dict(process="cooling", t_after=23.0), dict(process="rehydration", stream="rain", f=0.5)],
         why="Cool and rewet the dried D4 residue for wet-dry polymerisation of 2',3'-cyclic nucleotides."),
]

PATHWAYS = [
    dict(id="dsm", label="Borate DSM (Benner group)", scenario="borate_aquifer", steps=DSM, handoffs=DSM_H,
         note="Hirakawa 2025's six steps; steps 2 and 5 unread (paywalled)."),
    dict(id="dsm_b", label="Borate DSM, cyclic-nucleotide branch", scenario="borate_aquifer", steps=DSM_B, handoffs=DSM_B_H,
         note="Authors' 'continuous to 6-mer RNA' claim via 2',3'-cyclic phosphates, scored with Caimi 2025 as the polymerisation."),
]
