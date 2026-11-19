"""Blind red-team encoding of the six-step Discontinuous Synthesis Model (DSM), board task #27 (agent rt-27).

Written BEFORE opening anything in experiments/dsm_route/ or docs/prereg/dsm_route_score.md. Sources opened
(full text via Europe PMC / NCBI PMC, SI via Europe PMC supplementaryFiles):
  Hirakawa 2025 PNAS 10.1073/pnas.2516418122 (PMC12745811) + SI Appendix (pnas.2516418122.sapp.pdf)
  Kawai 2019 Astrobiology 10.1089/ast.2017.1800 (PMC6459274; DOI from the PMC XML; full text read)
  Jerome 2022 Astrobiology (PMC9233534, DOI 10.1089/ast.2022.0027 per the PMC XML, which carries "Correction to: Astrobiology 2022; 22(6): 629-636"; full text read)
  Kim 2011 JACS 10.1021/ja201769f and Kim & Benner 2021 Astrobiology 10.1089/ast.2020.2264: ABSTRACT ONLY
  (Europe PMC lists both as subscription-only; no legal open full text found).

Same data structure and conventions as experiments/pathway_map/steps.py (NaN = not reported, INF = scenario
feedstock with no stated concentration, "unknown" = solvent/redox not stated; redox "reducing" only if run anoxic).

Encoding choices a reviewer should attack (all deliberate, listed so they can be diffed):
  * D1 is the SO2 trapping of HCHO as hydroxymethanesulfonate (HMS), the only lab-tested part of Hirakawa's Step 1
    (atmospheric HCHO photochemistry, Pinto 1980 / Harman 2013, was not opened).
  * D2 follows Kawai 2019, the full text read: HMS + dihydroxyacetone (DHA) in borate-carbonate pH 10.5 -> mainly
    erythro/threo BRANCHED pentoses. Ribose is not reported by Kawai. Kim 2011 (abstract) says ribose is among the
    pentoses from HCHO + glycolaldehyde, with no amount. So D2's output is branched_pentoses, and D3's ribose is F4.
  * DHA is not supplied by the scenario: Hirakawa's Step 1 gives HCHO with ppm glycolaldehyde (HOCH2CHO).
    (Fig. 1 legend writes the formula HOCH2CH(OH)-CHO, i.e. glyceraldehyde; the abstract says "1 to 3 carbons".)
  * DAP is treated as a scenario feedstock (generous): Hirakawa calls amidophosphates the product of condensed
    phosphate + NH3 and shows small DAP/RCP peaks from CTMP + NH3 + ribose-borate (Results 1.4, no numbers).
  * D4 is Hirakawa's own one-pot run (Methods 3.4): RCP formed in situ, never purified, then 90 C dry-down with
    adenine and Ca2+. Products (2',3'-cAMP, 2'-AMP) were assigned by LC-MS/MS but NOT quantified. The ~17% yield
    Hirakawa quotes is from refs 21-22 with pure RCP (not opened). Labelled "demonstrated" with that caveat.
  * D5 (Kim & Benner 2021) starts from free nucleosides (abstract). No free adenosine is reported after the 90 C
    dry-down in Hirakawa main text, Fig. 4 or SI Figs S7-S13 (only m/z 330>136 and 348>85 were monitored).
  * D6 uses Jerome 2022 with ATP alone (Jerome: each NTP incubated separately at 3 uM also gives type (b)
    products, Suppl. Fig. S6, not opened by us). Borate tolerance comes from Hirakawa Fig. 5 (UTP only).
"""
NAN = float("nan")
INF = float("inf")

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pathway_map"))
from steps import inp, step  # noqa: E402  (same helpers as the four-route map)

D = dict(
    hirakawa2025="10.1073/pnas.2516418122",
    kawai2019="10.1089/ast.2017.1800",
    jerome2022="10.1089/ast.2022.0027",
    kim2011="10.1021/ja201769f",
    kimbenner2021="10.1089/ast.2020.2264",
)

STAGES = {
    "S1": "C-C chemistry from feedstocks (sugars, C1-C2 acids)",
    "S2": "nucleotides (activated or cyclic)",
    "S3": "oligomers (non-templated polymerisation)",
}

RAIN = dict(ph=7.0, t=25.0, solvent="water", redox="neutral", species={})

SCENARIO = dict(
    name="dsm_aquifer", t_range=[0, 100], uv=True, redox="neutral",
    settings=["atmosphere", "aquifer"],
    feedstocks={"HCHO": INF, "glycolaldehyde": INF, "bisulfite": INF, "borate": INF, "carbonate": INF,
                "phosphate": INF, "CTMP": INF, "NH3": INF, "DAP": INF, "adenine": INF, "Ca2+": INF,
                "Ni2+": INF, "urea": INF, "basalt_glass": INF},
    volatile=["HCHO", "NH3"],
    streams={"rain": RAIN},
    minerals={},
    basis=("Hirakawa 2025 (Fig. 1 legend; Discussion): HCHO + ppm glycolaldehyde from a redox-neutral CO2/N2/H2O "
           "atmosphere, trapped by mantle SO2; rain delivers them to an intermittently irrigated, basalt-constrained, "
           "borate-leaching sub-aerial aquifer; nucleobases, NH3 and urea from an atmosphere transiently reduced by a "
           "Vesta-sized impactor (which also delivers Ni, Kim & Benner 2021 abstract); condensed phosphate (CTMP) -> "
           "amidophosphates (DAP) with NH3. Aquifer pH: 'a balanced pH of 6.5 to 7.0 might be expected' (Hirakawa "
           "Discussion) -> rain stream pH 7.0, T 25 C (T is our assumption). Range 0-100 C: liquid water, covers the 90 C "
           "dry-down. Redox 'neutral' per Hirakawa's mantle/atmosphere (transiently reduced after impact). "
           "No feedstock concentrations are stated (INF). DAP as feedstock is a generous reading (see module doc)."),
)

DSM = [
    step("D1", "HCHO + bisulfite (from SO2) -> hydroxymethanesulfonate (HMS)", "S1", "atmosphere",
         [inp("HCHO", 1.0, note="13C-paraformaldehyde 1 mmol in 1 ml"), inp("bisulfite", 1.0, note="NaHSO3 1 mmol")],
         (NAN, 65.0, "water", "unknown"),
         {"HMS": NAN},
         yield_status="demonstrated",
         yield_text=("no numeric yield; HMS isolated by lyophilisation, single 13C signal 74.5 ppm, no methanol/formate. "
                     "Glycolaldehyde and glyceraldehyde 1:1 with bisulfite: >99% adduct (Figs 4-5)"),
         source=D["kawai2019"], where="Methods 2.2.1; Results 3.4",
         notes=("pH not stated: 1 M NaOH added dropwise 'until the solution became clear'. Hirakawa places this in "
                "aerosols/rain (Fig. 1 legend), Kawai says it 'certainly would have occurred in the hydrosphere'."),
         assumptions=["'demonstrated' although Kawai gives no numeric HMS yield"]),
    step("D2", "HMS + DHA in borate-carbonate -> borate-complexed branched pentoses", "S1", "aquifer",
         [inp("HMS", 1.0, note="13C-HMS 1.0 mmol in 1 ml D2O"),
          inp("DHA", 0.5, purified=True, note="dihydroxyacetone 0.5 mmol; same enediolate as glyceraldehyde"),
          inp("carbonate", 1.1, note="Na2CO3 1.1 M"), inp("borate", 0.278, note="H3BO3 0.278 M")],
         (10.5, 65.0, "water", "unknown"),
         {"branched_pentoses": NAN},
         yield_status="demonstrated_purified",
         yield_text=("13C product manifold 'quantitatively identical' to free H13CHO; products 'mainly erythro- and "
                     "threo-branched pentoses' (Kim 2011); no numeric yield in the text"),
         source=D["kawai2019"], where="Methods 2.2.2; Results 3.1; Fig. 3 legend (pH 10.4, 65 C); Discussion",
         notes=("Large-scale run (2.2.3) was degassed under N2 (65 C 2 d + RT 10 d); the 13C comparison run was not "
                "stated anoxic, so redox 'unknown'. Ribose is not reported. Kim 2011 abstract: pentoses 'including the "
                "ribose found in RNA' from HCHO + glycolaldehyde, and a molybdate-catalysed rearrangement of a branched "
                "pentose (no conditions or amounts in the abstract). Hirakawa Discussion: branched -> linear pentoses "
                "via Bilik or retro-aldol/aldol (refs 82-84, not opened)."),
         assumptions=["DHA counted as a non-scenario input (Hirakawa Step 1 names HCHO and glycolaldehyde only)"]),
    step("D3", "ribose + DAP (+ borate, phosphate buffer) -> ribose 1,2-cyclic phosphate (RCP)", "S2", "aquifer",
         [inp("ribose", 0.2, purified=True, note="D-ribose, Wako, 200 mM"),
          inp("DAP", 0.2, note="lab-synthesised from phenyl phosphorodiamidate; scenario feedstock by assumption"),
          inp("borate", 0.4, note="boric acid 400 mM"), inp("phosphate", 0.8, note="phosphate buffer 800 mM")],
         (7.0, 25.0, "water", "unknown"),
         {"RCP": 0.05293, "DAP": 0.01939, "ACP": 0.00253, "phosphate": 0.8},
         out_cond=(8.5, 25.0, "water", "unknown"),
         yield_status="demonstrated_purified",
         yield_text="RCP 47.90 mM at 24 h, 52.93 mM at 48 h (max), 39.23 mM at 288 h with borate; 26% of ribose at 48 h (our arithmetic)",
         source=D["hirakawa2025"], where="Table 1 (with borate); Methods 3.3; Fig. 3B (start pH ~6.8-7, end ~8.5, r.t.)",
         tested_with=["PCP", "pyrophosphate"],
         notes=("Outputs at 48 h (most favourable). Without phosphate buffer (ribose, borax 100 mM, DAP, CaCl2 5 mM, "
                "adenine 5 mM) RCP forms (SI Fig. S11) but is not quantified. CTMP + 5% NH3 + ribose-borate at pH ~10.4 "
                "gave 'small peaks' of RCP and DAP after 4 d (Results 1.4; SI Figs S3-S6), not quantified."),
         assumptions=["48 h point chosen (maximum RCP)"]),
    step("D4", "in-situ RCP + adenine + Ca2+, 90 C dry-down -> adenosine 2',3'-cyclic phosphate and 2'-phosphate",
         "S2", "aquifer",
         [inp("RCP", NAN, note="formed in situ from 200 mM ribose + 200 mM DAP + 100 mM borax, r.t. 24-168 h; not quantified"),
          inp("adenine", 0.005, note="5 mM"), inp("Ca2+", 0.005, note="CaCl2 5 mM")],
         (NAN, 90.0, "water", "unknown"),
         {"cAMP_23": NAN, "AMP_2": NAN},
         out_cond=(NAN, 90.0, "dry", "unknown"),
         yield_status="demonstrated",
         yield_text=("products assigned by LC-MS/MS with co-injection (Fig. 4; SI Figs S7-S10); NO yield reported. "
                     "Hirakawa quotes ~17% N9 adenosine 2'-phosphate from pure RCP (refs 21-22, not opened)"),
         source=D["hirakawa2025"], where="Results 1.5; Methods 3.4; Fig. 4; SI Figs S7-S10",
         tested_with=["ribose", "DAP", "borate", "ACP", "PCP", "pyrophosphate"],
         notes=("20 ul aliquot heated to dryness 24 h at 90 C, lids open; residue dissolved in 200 ul water. No phosphate "
                "buffer in this run. Free adenosine is not reported anywhere (main text, Fig. 4, SI): only m/z 330>136 "
                "(cyclic) and 348>85 (2'-AMP) chromatograms are shown; Fig. 4 says the ~17 min peak 'includes adenosine "
                "monophosphates'."),
         assumptions=["'demonstrated' although the one-pot products are not quantified"]),
    step("D5", "adenosine + Ni2+/borate + urea + CTMP, evaporative heating -> adenosine 5'-tri/di/monophosphate",
         "S2", "aquifer",
         [inp("adenosine", NAN, purified=True, note="nucleoside input per abstract"),
          inp("Ni2+", NAN), inp("borate", NAN), inp("urea", NAN), inp("CTMP", NAN)],
         (NAN, NAN, "water", "unknown"),
         {"ATP": NAN, "ADP": NAN, "AMP_5": NAN},
         out_cond=(NAN, NAN, "dry", "unknown"),
         yield_status="unread",
         yield_text="abstract: 2-3% nucleoside 5'-triphosphates; total 5'-phosphorylation typically 30%; full text not open",
         source=D["kimbenner2021"], where="abstract (Europe PMC); full text subscription-only",
         notes=("Abstract names nucleosides as the substrate ('Experimentally supported paths are already available to "
                "make nucleosides'), not nucleoside 2'/3'-phosphates. Hirakawa Discussion claims urea + borate move "
                "phosphate to the 5'-site, with no data or citation in the paper.")),
    step("D6", "ATP on basalt/diabase glass -> polyribonucleic acid", "S3", "aquifer",
         [inp("ATP", 3e-6, purified=True, note="3 uM; commercial alpha-32P-labelled NTPs"),
          inp("basalt_glass", NAN, note="22 mg glass per reaction; volume not in main text")],
         (7.5, 25.0, "water", "unknown"),
         {"RNA_polymer": NAN},
         yield_status="demonstrated_purified",
         yield_text=("type (b) products from each NTP alone; with 4 NTPs on MRM glass 2e-3 pmol triphosphate/h per g glass; "
                     "90-300 nt; RNase-sensitive. Hirakawa: borate 25 mM pH 6.5/7.5 does not inhibit (UTP, Iceland glass)"),
         source=D["jerome2022"], where="Jerome Results (Fig. 1-2; rate paragraph); Hirakawa Results 1.6, Fig. 5, Methods 3.6",
         tested_with=["borate"],
         notes="Hirakawa's borate test used UTP only; ATP-with-borate is not shown."),
]

HANDOFFS = [
    dict(procs=[dict(process="transport", to_setting="aquifer", dilution=1.0)],
         why="Rain carries HMS into the aquifer (dilution 1.0: most favourable; real dilution unknown). Same 65 C assumed."),
    dict(procs=[dict(process="mixing", stream="rain", f=0.5, ph_after=7.0), dict(process="cooling", t_after=25.0)],
         why=("Rain dilutes the pH 10.5 borate-carbonate pot and lowers pH to 7.0 (the rule's bound: between 10.5 and 7); "
              "a 1.1 M carbonate buffer would not in fact drop to pH 7 on 1:1 dilution. Branched pentoses are not ribose.")),
    dict(procs=[dict(process="heating", t_after=90.0), dict(process="same_pot")],
         why=("Same pot heated to 90 C; Hirakawa ran this one-pot (without the 800 mM phosphate buffer). RCP concentration "
              "in the one-pot run was not measured.")),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5), dict(process="same_pot")],
         why="Rain redissolves the dry residue. The step needs free adenosine; D4 makes nucleotides, not the nucleoside."),
    dict(procs=[dict(process="rehydration", stream="rain", f=0.5, ph_after=7.5), dict(process="cooling", t_after=25.0)],
         why="Rain redissolves the dry residue onto glass; ATP would have to be separated from ADP/AMP/urea/CTMP/Ni."),
]

PATHWAY = dict(id="dsm_rt", label="Discontinuous Synthesis Model (red-team blind encoding)", scenario="dsm_aquifer",
               steps=DSM, handoffs=HANDOFFS)
