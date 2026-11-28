"""One-off: paper watch 2026-11-28. Adds the papers kept from .local/paperwatch/2026-11-28/origins.md (hub repo).
Only papers actually opened are added. Numbers are quoted from what was opened."""
import json, pathlib
P = pathlib.Path(__file__).with_name("library.json")
d = json.loads(P.read_text()); by = {e["id"]: e for e in d["papers"]}
TODAY = "2026-11-28"

def entry(**k):
    base = {"kind": "Paper", "in_news": False, "verified": True, "changes_plan": "", "imported": False,
            "added": TODAY, "touches": [], "url": "https://doi.org/" + k["doi"]}
    base.update(k); return base

new = [
 entry(id="yang-2026-vent-copper-hcn-from-glycine", relevance="useful", topic="Vents and first cells", in_news=True,
  title="Copper derived from deep-sea hydrothermal vent minerals facilitates hydrogen cyanide formation from glycine in alkaline aqueous environment",
  authors="Yang Z, Li Y, Lu Y, Yamaguchi A, Adachi K, Yamamoto M, Kitadai N, Tagawa S, Hashizume D, Nakamura R",
  year=2026, venue="Communications Chemistry", doi="10.1038/s42004-026-02263-5", date="2026-11-25",
  read_depth="full",
  question="Can hydrogen cyanide (HCN) be made in place near deep-sea hydrothermal vents, instead of being supplied from the atmosphere?",
  tried="A copper-rich natural vent chimney mineral oxidises glycine to HCN in alkaline, oxygen-free water, with copper(II) leached from the mineral as the oxidant.",
  method_data="Chimney sample KK805#R02 from the Iheya North Field, Mid-Okinawa Trough (1009.4 m depth), interior only, ground and cleaned in a glovebox. 50 mM glycine with 50 mg chimney powder at pH 12; 13C-labelled glycine to confirm the carbon source; control reactions with CuCl2 and synthetic Cu(Gly)2; two further chimney samples (KK804#R03, KK809#R02) for comparison; ICP-OES and UV-Vis for leached copper.",
  key_results="HCN reached 451.42 nM at 25 °C in 24 h; the yield rose threefold at 10 °C. 13C labelling showed the cyanide came from the added glycine. The two other chimney samples, dominated by ZnS, FeS2 and PbS with only minor chalcopyrite, gave no quantifiable cyanide (Welch's ANOVA across the three samples F(2, 3.55) = 389.69, p = 6.94 × 10^-5). The authors conclude the mineral supplies copper(II) as an oxidant rather than acting as a catalyst.",
  limits="One copper-rich chimney worked; two copper-poor ones did not, so the route depends on local copper. pH 12 and 50 mM glycine are high; the authors call yields modest and say they did not simulate high-temperature, high-pressure vent fluid. Free cyanide only (conservative). The sampled vent fluid itself is acidic (pH about 5.0), so the alkaline setting is an analogue, not the sample's own environment. Glycine supply at 50 mM is assumed, not shown.",
  ideas_for_us="Add a vent-local HCN source row to the step tables of the pathway map (#4/#5), conditional on a copper-bearing sulfide and a glycine supply, with 451 nM per 24 h at pH 12 as the measured ceiling. It sits beside IDEAS #7 (drop comets as a cyanide source): if comets go, this is one of the few non-atmospheric HCN routes left, and its nM output must be compared with the mM levels HCN chemistry usually needs. See IDEAS #13.",
  touches=["#4", "#5", "#17"],
  source_opened="full text (Europe PMC, PMC13809238, CC BY-NC-ND)"),
 entry(id="pesciotta-2026-hydrolyzed-exoplanet-hazes", relevance="useful", topic="From space",
  title="Hydrolyzed Hazes on Water-rich Exoplanets: Composition and Prebiotic Chemistry",
  authors="Pesciotta C, Hörst S, Radke M, Moran S, Blakley B, He C, Vuitton V, Flandinet L",
  year=2026, venue="The Planetary Science Journal 7(11)", doi="10.3847/psj/aebf8b", date="2026-11-01",
  read_depth="full",
  question="What happens to the chemistry of photochemical haze on temperate, water-rich sub-Neptunes when it meets liquid water?",
  tried="Expose lab haze analogs to water and look for new oxygenated, prebiotically relevant molecules.",
  method_data="Haze analogs made in the PHAZER chamber (Johns Hopkins) from gas mixtures for 1000x solar metallicity atmospheres at 300 K and 400 K, about 3 mbar; hydrolysed into soluble and insoluble fractions; ESI Orbitrap high-resolution mass spectrometry in positive and negative mode; elemental analysis and van Krevelen diagrams.",
  key_results="Thousands of CHNO molecular formulas after hydrolysis. Oxygen weight percent rose significantly in the soluble fraction and moderately in the insoluble one (errors ±2.0-7.2%). Formulas consistent with monosaccharides and derivatives appeared, and few candidate molecules were destroyed. The two planet analogs became more alike after hydrolysis.",
  limits="Formulas only: a mass match is not an identification, and the authors say amino acids, nucleobases and sugars still need confirming with other methods. Two simulated atmospheres, one lab chamber.",
  ideas_for_us="Context for the delivery side of the pathway map (#5/#20): a haze-plus-water source of oxygenated organics. It enters our tables only once specific molecules are confirmed, not as formula matches.",
  touches=["#5", "#20"],
  source_opened="full text (IOP publisher page, CC BY 4.0)"),
 entry(id="lin-2026-eukaryote-root-gene-duplications", relevance="context", topic="LUCA and the tree of life", kind="Preprint",
  title="Rooting the tree of eukaryotes using ancient gene duplications",
  authors="Lin C, Kay C, Schick O, Spang A, Szöllősi GJ, Pisani D, Donoghue PCJ, Williams TA",
  year=2026, venue="bioRxiv", doi="10.64898/2026.11.20.768066", date="2026-11-23",
  read_depth="abstract",
  question="Where is the root of the eukaryote tree, using a signal that does not depend on distant prokaryote outgroups?",
  tried="Use pre-LECA gene duplications: each paralogue roots its sibling, and the evidence is pooled across families by phylogenetic reconciliation.",
  method_data="219 pre-LECA duplicate gene families; reconciliation analyses over candidate root positions.",
  key_results="Reconciliation rejected most candidate roots. Most analyses favoured a root on or within Metamonada; Discoba, or a deep Opimoda-Diphoda split, were not rejected under some conditions. Metamonada sat basal within each paralogue in about 23-25% of duplicate gene trees, more than other groups.",
  limits="(abstract only) bioRxiv full text returned 429 and was not retried. About LECA, not LUCA. The abstract itself notes possible biases in reconciliation.",
  ideas_for_us="Same family of methods as #32 (pooling root signal across gene families by reconciliation), from the Williams/Szöllősi groups. Useful as a real-data example of a credible set of roots rather than one root, which is how #32 should report root uncertainty.",
  touches=["#32"],
  source_opened="abstract (Europe PMC preprint record PPR1375483)"),
 entry(id="nesterov-mueller-2026-protocode-mats", relevance="context", topic="RNA world",
  title="Physico-chemical aspects of protocode mats: a code-first reconstruction",
  authors="Nesterov-Mueller A, Schmidt D",
  year=2026, venue="BioSystems", doi="10.1016/j.biosystems.2026.106032", date="2026-11-26",
  read_depth="abstract",
  question="Can the origin of the genetic code be tied to a physical, mineral-supported organisation of prebiotic chemistry?",
  tried="The authors' combinatorial fusion cascade splits four protocodes into two mineral-bound 'protomats', anchored by arginine (on smectite) and lysine.",
  method_data="Theoretical reconstruction: a structural model of the arginine protomat and electrostatic and Born-energy estimates.",
  key_results="Cellular biosynthesis routes follow the two-way split for 17 of 18 amino acids, with aspartate the only shared node. At 140 mM monovalent salt and half surface coverage, film ordering needs a lateral attraction of at least 5.5 kJ/mol per contact. Born barriers for charged HCO3-, HS-, CN- and NH4+ across the apolar core are 44.9-62.8 kBT at core permittivity 3 (27.7-45.6 kBT with a finite-slab correction).",
  limits="(abstract only; paywalled) A model built on the authors' own framework, with no experiment. The 17-of-18 match is a post hoc fit to a scheme with free choices.",
  ideas_for_us="None for now. Any genetic-code claim like this would need a null for how often a random two-way split of amino acids matches biosynthesis routes this well (relevant to #19).",
  touches=["#19"],
  source_opened="abstract (Europe PMC, MED 43098412)"),
]
added = [e["id"] for e in new if e["id"] not in by]
d["papers"].extend(e for e in new if e["id"] not in by)
d["updated"] = TODAY
P.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n"); print("added", len(added), added)
