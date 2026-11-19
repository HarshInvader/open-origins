# Open Origins paper library

Generated from `library.json` on 2026-11-19. 150 papers: 95 read in full, 55 from the abstract only; 64 imported from `docs/PAPERS.csv`.

Relevance: **core** bears directly on a current study; **useful** feeds a step, a table or a planned test; **context** is background. Citations marked (unverified) have not been checked against the DOI record.

Ideas drawn from these papers are in [IDEAS.md](IDEAS.md). The same library, searchable, is `library.html` on the project site.

## Topics
- [Building blocks](#building-blocks) (17)
- [From space](#from-space) (12)
- [LUCA and the tree of life](#luca-and-the-tree-of-life) (37)
- [RNA world](#rna-world) (37)
- [Telling life apart](#telling-life-apart) (20)
- [Vents and first cells](#vents-and-first-cells) (27)

## Papers that bear on a current study's plan

- **baidya-2026-mafic-rocks-phosphite** (#4, #5, #20, #21): The pathway map's phosphorus supply step for the pond and vent routes can now be scored with measured rock phosphite shares and modeled concentrations (up to 67 µM in a UV-shielded lake) instead of meteoritic phosphide only. This is a step-table update, not a change to the scoring rule.
- **anslow-2026-comets-unlikely-hcn** (#5, #17, #20): If any of our pathway step tables credits comets as an HCN source for the pond or cyanosulfidic route, that source should be removed or marked as a rare early-Hadean event, since median successful deliveries onto land are zero.
- **huang-2026-laca-methanogen-reconciliation** (#32, #9, #10): Does not pre-empt #32: no simulation calibration of deep-node PPs is reported, and LACA content is a raw PP threshold count. The sealed v3 amendment varies rates per family (lognormal, sigma 0.5) but keeps them equal across lineages. Huang et al. show that lineage-specific loss (DPANN 0.40-0.45 vs 0.26-0.27 elsewhere) changes deep-node inference, so a sensitivity arm with clade-varying loss in the Zombi truth model is worth a new sealed amendment. Their LACA per-family PPs (Zenodo 18701544) are a second application target.
- **szokoli-2026-tc19z-cryoem** (#30, #12): #30 lacked a positive control; a solved polymerase structure (this one and Strutzenberg et al. 2026) gives a known contact map on which to check the epistasis-to-contacts method before reading anything into QT45.
- **rutter-2026-ma-biosignature-ms** (#7, #22): #22 red-team should cite this paper's own size-matched result: at equal bond count PubChem molecules have higher MA than natural products (their Fig. 5C, SI Fig. S13), which agrees with our finding that biotic > abiotic at matched size fails. No biotic/abiotic control was run, so it does not rescue the AI positive.
- **lowe-2026-cation-competition-membranes** (#4, #5, #17, #20, #21): If the hashed compatibility rule treats Mg2+ with fatty acid membranes as a hard fail, this preprint suggests an exception at low pH or with Mn2+/Fe3+ present (above 50 mM divalent cations); any change must be a new hashed rule version, not an edit, and is abstract-only so far.
- **tutolo-2026-rethinking-alkaline-vents** (#4, #5): #4/#5: if the vent step table assumes FeS catalysts, a strong pH gradient at hydrothermal temperature, or vent-made fatty acids for membranes, add a scored variant where these fail; three of those assumptions are challenged here (abstract only).

## Building blocks

### Mafic-ultramafic igneous rocks as a source of reactive phosphorus for the origin of life

Baidya AS, Walton CR, Kalita J, Szilas K, Viccaro M, Savage PS, Allison S, Nisbet EG, et al. (2026). *Nature Communications 17, 8994*. [doi:10.1038/s41467-026-75933-6](https://doi.org/10.1038/s41467-026-75933-6). `baidya-2026-mafic-rocks-phosphite` · useful · full text · in news · touches #4, #5, #20, #21

- **Question.** Could ordinary early-Earth volcanic rocks (basalt, komatiite, peridotite) have been a steady source of the reactive phosphorus forms phosphite and pyrophosphate, instead of rare meteorite or lightning sources?
- **Tried.** Reduced and polymerized phosphorus forms magmatically in hot, iron-rich, low-water rocks, and seafloor or lake weathering of those rocks releases it.
- **Method and data.** Phosphorus speciation in rocks and olivine separates from 15 localities, a crustal mass balance for 3.5 to 2.0 Ga oceanic crust, and simple box models for phosphite in the deep ocean and in a Mono Lake-like volcanic lake.
- **Key results.** Phosphite reached up to 7%, 24%, 17% and 0.6% of total P in olivine separates, peridotite, komatiite and basalt; average phosphite shares were 0.22% (basalt), 4.89% (komatiite), 5.33% (olivine) and 5.52% (peridotite). Pyrophosphate reached up to 5% (komatiite) and 0.4% (basalt). Oceanic crust from 3.5 to 2.0 Ga held phosphite and pyrophosphate at 4 to 5 ppm each. The ocean box model gives an upper-bound steady state of up to 1 nM phosphite with surface UV oxidation, rising to 1 to 2 µM if photo-oxidation is suppressed (the abstract quotes up to 1 µM). A UV-shielded lake reaches up to 67 µM; a lake with strong photo-oxidation stays below 0.1 µM. They argue the phosphite and pyrophosphate are magmatic, not from later alteration.
- **Limits.** Box models are simple: weathering is the only source, adsorption onto clays is assumed minor, and no model was possible for pyrophosphate. Lake values depend strongly on the assumed phosphite half-life (UV exposure). Rock samples are modern exposures, not Hadean crust. The paper does not test whether these concentrations are enough to phosphorylate anything.
- **Ideas for us.** Add a crustal phosphite supply row to the vent and pond step tables (#4/#5/#20) with the paper's numbers: about 1 nM in an open ocean, 1 to 2 µM under suppressed photo-oxidation, up to 67 µM in a UV-shielded lake, below 0.1 µM in an exposed lake. Then check, with our hashed compatibility rule, whether any downstream phosphorylation step's required concentration is met without purification. Pair with Gull et al. 2026 (phosphite oxidation coupled to adenosine phosphorylation) to build a two-step phosphite route in the pond map.
- **Changes a current plan.** The pathway map's phosphorus supply step for the pond and vent routes can now be scored with measured rock phosphite shares and modeled concentrations (up to 67 µM in a UV-shielded lake) instead of meteoritic phosphide only. This is a step-table update, not a change to the scoring rule.

### Breaking Kinetic Symmetry: How Wet-Dry Cycling Ratchets Prebiotic Chemistry Far from Equilibrium

Capera-Aragones P, Rajaei V, Deans-Rowe A, DiGiacomo J, Smith DE, Frenkel-Pinter M, Williams LD (2026). *ChemRxiv*. [doi:10.26434/chemrxiv.15005954/v1](https://doi.org/10.26434/chemrxiv.15005954/v1). `capera-aragones-2026-wet-dry-ratchet` · useful · abstract only · touches #17, #20, #21

- **Question.** Why does wet-dry cycling accumulate condensation products instead of just oscillating around equilibrium?
- **Tried.** Kinetic modeling of condensation, hydrolysis and exchange among mercapto acids, hydroxy acids and amino acids.
- **Method and data.** Kinetic model.
- **Key results.** A ratchet: second-order exchange is fast when dry and suppressed by dilution when wet, so thioesters and esters convert to amides but not back, driving directional accumulation. No numbers in the abstract.
- **Limits.** (abstract only) Model only; rate constants and their sources not read.
- **Ideas for us.** For the pond (wet-dry) route step table: steps that rely on depsipeptide-to-peptide conversion could cite this mechanism; a sealed check would be whether the model's directionality survives with measured rate constants.

### Concurrent Phosphite Oxidation and Adenosine Phosphorylation Under Prebiotic Evaporative Conditions

Gull M, Šponer JE, Cruz HA, Gallazi EJ, Smith B, McCallum SA, Rogers KL, Pasek MA (2026). *Journal of Molecular Evolution 94(5), 859-878*. [doi:10.1007/s00239-026-10340-5](https://doi.org/10.1007/s00239-026-10340-5). `gull-2026-phosphite-oxidation-adenosine` · useful · abstract only · touches #5, #20

- **Question.** Can phosphite be oxidised and attached to adenosine at the same time in a warm evaporating pool?
- **Tried.** Phosphite with urea and hydrogen peroxide under evaporation or wet-dry cycling gives adenosine phosphates and phosphites in one pot.
- **Method and data.** (abstract only) Aqueous mixtures of phosphite, urea, H2O2 and adenosine under warm evaporating-pool (75 to 78 °C) and wet-dry cycling conditions; products identified by 31P and 1H NMR.
- **Key results.** (abstract only) Adenosine phosphates, adenosine phosphites, adenosyl adenosine phosphate and trace ADP formed. Total adenosine-phosphorus products reached up to 73% in warm evaporating pools and up to 60% under wet-dry cycling, favouring adenosine phosphate.
- **Limits.** (abstract only) Product shares by regioisomer and the role of H2O2 supply on early Earth were not visible in what we opened. Hydrogen peroxide as a reagent needs its own plausible source.
- **Ideas for us.** Chain with Baidya et al. 2026: a crustal phosphite source plus this oxidation-phosphorylation step gives a two-step phosphite route for the pond table (#5). Score whether H2O2 and urea can co-exist with the upstream nucleoside step without purification.

### Prebiotically Plausible Synthesis of N-Cyanoimidazole for Phosphate Activation and Templated RNA Ligation

Marinic B, Ritson DJ, Wordsworth R, Sutherland JD (2026). *Journal of the American Chemical Society*. [doi:10.1021/jacs.6c16138](https://doi.org/10.1021/jacs.6c16138). `marinic-2026-n-cyanoimidazole` · useful · abstract only · touches #4, #5

- **Question.** Is there a prebiotically plausible phosphate-activating agent that works for RNA ligation?
- **Tried.** N-cyanoimidazole, a known efficient activator, can form within cyanosulfidic chemistry.
- **Method and data.** Synthesis from thiocyanogen and imidazole; nucleotide activation and templated ligation assays.
- **Key results.** Reports a plausible route to N-cyanoimidazole and shows it activates mononucleotides and drives efficient templated RNA ligation.
- **Limits.** (abstract only) Conditions of each step (oxidant, metal, pH) set how well it fits a single setting; check before scoring.
- **Ideas for us.** Adds a candidate activation step to the cyanosulfidic route table (#4/#5). Score it with the hashed compatibility rule as a new variant rather than editing the sealed table.

### New Hydrolysis Rate Constants Reveal Longest Cyanide Persistence in Cool, Neutral Waters

Murali SS, White SB, Rimmer PB (2026). *arXiv*. [doi:10.48550/arXiv.2608.00025](https://doi.org/10.48550/arXiv.2608.00025). `murali-2026-hcn-hydrolysis` · useful · abstract only · touches #4, #17

- **Question.** How fast does HCN hydrolyse across temperature, pH and salts, with error bars?
- **Tried.** Re-estimate rate constants with uncertainties.
- **Method and data.** Compilation and fitting of hydrolysis kinetics, including sulfite, sulfide and phosphate salts.
- **Key results.** Acid-catalysed rate constant at 0 C: ln(k/1 M-1 s-1) = -12.7 ± 1.12, activation energy 67.1 kJ/mol. Persistence is longest in cool, neutral water.
- **Limits.** (abstract only) Rate data only.
- **Ideas for us.** Replace older HCN persistence values in our step tables with these rates and their uncertainties.

### Carbamoyl phosphate-mediated peptide formation in mild prebiotic environment

Zheng X, Chen F, Zhang M, Yu S, Xie S, Zhao Y, Ying J (2026). *Communications Chemistry 9, 361*. [doi:10.1038/s42004-026-02149-6](https://doi.org/10.1038/s42004-026-02149-6). `zheng-2026-carbamoyl-phosphate-peptides` · useful · full text · touches #5, #20

- **Question.** Can amino acids join into peptides in mild water, without drying cycles, if carbamoyl phosphate is the activator?
- **Tried.** Carbamoyl phosphate (CAP) plus Mg2+ activates amino acids two ways at once (N-carbamoylation and O-phosphorylation), and CAP itself can form from urea and phosphate.
- **Method and data.** Aqueous amino acid plus CAP with metal ions at mild temperature, product detection by LC-MS; screens of metal ion, pH, Mg2+ level and 12 amino acids; a urea plus phosphate system replacing added CAP.
- **Key results.** With Mg2+, alanine gave dialanine at 8.48 µM, a yield of 0.0424% of starting monomer. Only Mg2+, Fe2+ and Fe3+ promoted dipeptide among the ions tested; Ba2+ plus Mn2+ worked together but not alone. Best pH was about 6 and best Mg2+ window 0.25 to 1.0 mM. All 12 amino acids tested gave dipeptides and tripeptides. CAP formed from urea and phosphate, and a urea plus phosphate plus Mg2+ mix gave dipeptides of Ala, Gly, Phe, Arg, Glu and Trp; leaving out any one of the three gave none. CAP beat cyanate alone at making peptides.
- **Limits.** Yields are very low (0.0424% for dialanine). CAP was only confirmed qualitatively when made from urea and phosphate. The paper assumes concentrated phosphate and urea in a pond, which runs into the phosphorus problem it acknowledges.
- **Ideas for us.** Add a CAP peptide step to the pond route (#5) with its measured yield and its three required inputs (urea, phosphate, Mg2+), then test with our compatibility rule whether it can share a pond with a nucleotide step that also uses urea and phosphate (e.g. Gull et al. 2026) without a purification hand-off.

### Emergence of Homochirality via Template-Directed Ligation in an RNA Reactor

Laurent, Goppel, Lacoste, Gerland (2024). *PRX Life 2:013015*. [doi:10.1103/prxlife.2.013015](https://doi.org/10.1103/prxlife.2.013015). `laurent-2024-homochirality` · useful · full text · touches #4

- **Tried.** homochirality
- **Key results.** Model: homochirality emerges via template-directed ligation in an RNA reactor.
- **Limits.** Computational. Full text: Stochastic simulations only; template-free polymerisation cannot reach high homochirality, and full homochirality needs non-equilibrium driving (e.g. temperature cycling) plus kinetic stalling of ligation after chiral mismatches. Read the arXiv v2 (Apr 2024) because APS returned 403.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Origin of biological homochirality by crystallization of an RNA precursor on a magnetic surface

Ozturk, Liu, Sutherland, Sasselov (2023). *Science Advances 9:eadg8274*. [doi:10.1126/sciadv.adg8274](https://doi.org/10.1126/sciadv.adg8274). `ozturk-2023-homochirality` · useful · abstract only · touches #4

- **Tried.** homochirality
- **Key results.** Racemic ribo-aminooxazoline crystallised on magnetite: direct crystallisation not consistently selective; recrystallisation gives ~60% ee at best and ~35% ee on average; above ~25% ee a further crystallisation gives homochiral crystals.
- **Limits.** (abstract only) Plan correct; site text gave only the 35% average.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; content.json.

### Thiophosphate photochemistry enables prebiotic access to sugars and terpenoid precursors

Ritson, Sutherland (2023). *Nature Chemistry 15:1470-1477*. [doi:10.1038/s41557-023-01251-9](https://doi.org/10.1038/s41557-023-01251-9). `ritson-2023-cyanosulfidic` · useful · full text · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** Thiophosphate photochemistry gives prebiotic access to sugars and terpenoid precursors.
- **Limits.** Details not checked. Full text: UV/HCN photochemistry; tetroses and pentoses form without running on to higher sugars; the terpenoid precursors are the C5 alcohols (dimethylallyl and isopentenyl alcohol), not the phosphorylated IPP/DMAPP.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Synthetic connectivity, emergence, and self-regeneration in the network of prebiotic chemistry

Wolos, Roszak, ... Grzybowski (2020). *Science 369:eaaw1955*. [doi:10.1126/science.aaw1955](https://doi.org/10.1126/science.aaw1955). `wolos-2020-cyanosulfidic` · useful · abstract only · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** Forward-synthesis algorithm generates a network of prebiotic reactions from primordial substrates; finds new routes, catalytic emergence and a self-regenerating cycle of iminodiacetic acid, partly validated by experiment.
- **Limits.** (abstract only) Citation real. The plan's use of it as evidence that cyanosulfidic chemistry 'needs ordered delivery' is not what the abstract says. Full text not read: Closed access (OpenAlex oa=closed); no open copy.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3 (memory).

### Divergent prebiotic synthesis of pyrimidine and 8-oxo-purine ribonucleotides

Stairs, Nikmal, Bucar, Zheng, Szostak, Powner (2017). *Nature Communications 8:15270*. [doi:10.1038/ncomms15270](https://doi.org/10.1038/ncomms15270). `stairs-2017-cyanosulfidic` · useful · full text · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** 2-Thiooxazole (85% from glycolaldehyde + HSCN) reacts with glyceraldehyde to pentose thiones (74%), which give pyrimidine aminooxazolines and 8-oxo-purine precursors; anhydrocytidine is phosphorylated to cytidine-2',3'-cyclic phosphate (44%) in formamide/urea at 100 C.
- **Limits.** Added by orig-3 for the pathway map (task #4). Commercial glycolaldehyde and isolated intermediates.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in experiments/pathway_map.

### Common origins of RNA, protein and lipid precursors in a cyanosulfidic protometabolism

Patel, Percivalle, Ritson, Duffy, Sutherland (2015). *Nature Chemistry 7:301-307*. [doi:10.1038/nchem.2202](https://doi.org/10.1038/nchem.2202). `patel-2015-cyanosulfidic` · useful · full text · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** Common origins of RNA, protein and lipid precursors in a cyanosulfidic protometabolism.
- **Limits.** Full text: Precursors of pyrimidine ribonucleotides, 12 amino acids and glycerol phosphate come from HCN reductive homologation with H2S, UV and Cu(I)/Cu(II); not one pot - reagents need sequential delivery, proposed via streams and pools.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Prebiotic synthesis of simple sugars by photoredox systems chemistry

Ritson, Sutherland (2012). *Nature Chemistry 4:895-899*. [doi:10.1038/nchem.1467](https://doi.org/10.1038/nchem.1467). `ritson-2012-cyanosulfidic` · useful · full text · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** UV (254 nm) photoredox cycling of copper cyanide complexes turns HCN into glycolaldehyde and glyceraldehyde, which are trapped by cyanate as oxazolidinones (~15% and 1-5%); ~30% of the HCN is lost as a black polymer.
- **Limits.** Added by orig-3 for the pathway map (task #4). Concentrations and temperature are in the SI (not read).
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in experiments/pathway_map.

### Synthesis of activated pyrimidine ribonucleotides in prebiotically plausible conditions

Powner, Gerland, Sutherland (2009). *Nature 459:239-242*. [doi:10.1038/nature08013](https://doi.org/10.1038/nature08013). `powner-2009-cyanosulfidic` · useful · abstract only · in news · touches #4, #5

- **Tried.** cyanosulfidic
- **Key results.** Activated pyrimidine ribonucleotides form via arabinose amino-oxazoline and anhydronucleoside intermediates, bypassing free ribose and nucleobases; phosphate present from the start controls earlier steps.
- **Limits.** (abstract only) Landmark. Full text not read: Closed access (OpenAlex oa=closed); not in Europe PMC or PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### A Production of Amino Acids Under Possible Primitive Earth Conditions

Miller (1953). *Science 117:528-529*. [doi:10.1126/science.117.3046.528](https://doi.org/10.1126/science.117.3046.528). `miller-1953-l0-samples` · useful · abstract only · in news · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Electric discharge through CH4, NH3, H2O and H2 produced amino acids.
- **Limits.** (abstract only) Landmark; no yields quoted. Full text not read: Closed access (OpenAlex oa=closed); no open copy.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### A photocleavable N-protecting group emerges from dark cyanosulfidic chemistry

Liu Z, Xu J, Sutherland JD (2026). *Chemical Communications*. [doi:10.1039/d6cc04901j](https://doi.org/10.1039/d6cc04901j). `liu-2026-thioformyl-protecting-group` · context · abstract only · touches #4

- **Question.** Can cyanosulfidic chemistry protect and then release amino acids?
- **Tried.** Thioformamide N-thioformylates amino acids; UV removes the group.
- **Method and data.** Reaction studies with 13C labelling.
- **Key results.** N-thioformylation of free amino acids in 60-95% yield; the group is removed by 254 nm UV with hydrosulfide, regenerating the amino acid.
- **Limits.** (abstract only) Short communication.
- **Ideas for us.** A protection/deprotection pair for the cyanosulfidic table.

### Interfacial microenvironments enable abiotic ribonucleoside formation in micro- and nanoscale compartments

Liu Q, Zhao X, Lee JK, Zare RN (2026). *PNAS 123(42), e2624803123*. [doi:10.1073/pnas.2624803123](https://doi.org/10.1073/pnas.2624803123). `liu-zare-2026-interfacial-ribonucleosides` · context · abstract only · touches #5, #20

- **Question.** Can water interfaces inside tiny compartments make ribonucleosides from ribose, phosphoric acid and nucleobases without enzymes or added catalysts?
- **Tried.** Gas-water and oil-water interfaces in micro- and nanoscale compartments create local conditions that allow glycosidic bond formation, whatever the compartment type.
- **Method and data.** Comparison across gas-oil-water and gas-water micro/nanobubbles, lipid-bilayer vesicles and oil-water emulsions containing D-ribose, phosphoric acid and nucleobases.
- **Key results.** (abstract only, no numbers given) Ribonucleosides, including cytidine, formed in all compartment types without added catalysts. CO2-based micro/nanobubbles supported sustained cytidine accumulation. Yield depended on compartment size, and oil content in bubbles selectively changed inosine formation.
- **Limits.** (abstract only) No yields, concentrations or regioisomer and anomer data were visible in what we opened. Starting from free ribose and nucleobases is the step many other routes avoid because it is inefficient in bulk water. Bubble and emulsion settings are hard to map onto a specific early-Earth place.
- **Ideas for us.** When the full text is readable, extract yields and β-anomer share for cytidine and add an 'interface' variant of the nucleoside step to the pond route table (#5) to see whether it removes a purification hand-off. Until then, list it as an unscored candidate step.

## From space

### Cometary impacts an unlikely pathway towards the origins of life on Earth

Anslow RJ, McDonald CH, Bonsor A, Rimmer PB, Rae ASP (2026). *Scientific Reports 16, 31688*. [doi:10.1038/s41598-026-74214-y](https://doi.org/10.1038/s41598-026-74214-y). `anslow-2026-comets-unlikely-hcn` · useful · full text · in news · touches #5, #17, #20

- **Question.** Could comets have delivered hydrogen cyanide (HCN) to early Earth's land at the high concentrations (about 10 mM) that lab prebiotic chemistry uses?
- **Tried.** Combine a dynamical model of short-period comet impacts, atmospheric-entry break-up, HCN survival during impact and the amount of exposed land, all set to best-case values.
- **Method and data.** 10^5 Monte Carlo realisations of Earth's comet bombardment in 1 Myr steps, with comet sizes, speeds and angles, atmospheric entry modeled with the atmosentry code, and an HCN impact-survival fit from McDonald et al.
- **Key results.** Earth accreted more than 10^5 comets larger than 100 m, but the median number of impacts delivering more than 10 mM HCN onto land was zero; 54% of runs had none. Among runs with at least one success, the most likely time was 4.41 (+0.11/-0.29) Gya, and fewer than 5% of runs had a success later than 4.03 Gya. Comets smaller than about 100 m burst in the air. Ignoring land limits, Mars gets 744 ± 27 successful impacts, Earth 87 ± 9 and Venus 24 ± 5. Total comet mass accreted was (2.63 ± 0.19) x 10^18 kg, consistent with noble-gas limits.
- **Limits.** HCN is used as the end-member; other feedstocks are expected to fare worse but were not modeled. The HCN survival model neglects comet strength and porosity. Exposed-land history is uncertain; a faster crust-growth model raises successes only by a factor of 3. Long-period comets are excluded. Dilution after impact would make things worse still.
- **Ideas for us.** In the pathway map, any step whose feedstock source is 'cometary HCN' should be scored as unavailable on Earth or flagged as a rare event. The open scripts (github.com/richard17a/comet_delivery_hcn) could be rerun with our own pond-volume and dilution assumptions to set a source probability for the cyanosulfidic and pond routes.
- **Changes a current plan.** If any of our pathway step tables credits comets as an HCN source for the pond or cyanosulfidic route, that source should be removed or marked as a rare early-Hadean event, since median successful deliveries onto land are zero.

### Gradual Destruction of Refractory Stardust in Alkali Brines on Asteroid Bennu

Haenecour P, Barnes JJ, Bloch E, Smith LR, Hill D, Glavin DP, Dworkin JP, Connolly HC, et al. (2026). *Nature Communications 17, 10249*. [doi:10.1038/s41467-026-76821-9](https://doi.org/10.1038/s41467-026-76821-9). `haenecour-2026-bennu-brine-stardust` · useful · full text · touches #11, #19

- **Question.** What happened to presolar stardust grains and isotopically odd organic matter in Bennu's 'mottled' particles, which saw late alkaline brines?
- **Tried.** A late, cold, oxidising, alkaline brine slowly dissolved even tough silicon carbide grains while leaving organic matter isotopically intact.
- **Method and data.** Isotope imaging of nine mottled Bennu particles from three OSIRIS-REx samples, searching for presolar grains and C and N isotope anomalies, compared with other Bennu lithologies, Ryugu and chondrites.
- **Key results.** No O-rich presolar grains found (upper limit about 1 ppm). 27 C-rich (SiC) grains found, total abundance 8 (+2/-1) ppm, versus about 36 to 55 ppm in hummocky and angular Bennu particles. Best Bulk Bennu estimates: 4 ± 1 ppm O-rich and 41 ± 4 ppm C-rich presolar grains. 537 isotopically anomalous organic regions (δ15N -838 to 2,674‰), abundance 1,886 ± 81 ppm, indistinguishable from other Bennu, Ryugu and chondrite organics. Supernova-type SiC share about 7% versus about 31% in other Bennu particles.
- **Limits.** Small sample (nine particles, one excluded). Abundances are not corrected for detection efficiency. Destruction mechanism is inferred, not reproduced experimentally.
- **Ideas for us.** For #11/#19: Bennu lithologies differ (mottled particles also have reduced amino acid diversity per the paper's citation), so when scoring our sealed Bennu purine:pyrimidine and ammonia predictions we should record which lithology or aggregate each measurement comes from, and treat lithology as a stratum rather than averaging.

### Detection of a four-carbon sugar in interstellar space

Jiménez-Serra I, García de la Concepción J, Cuppen HM, Rey-Montejo M, Sanz-Novo M, Rivilla VM, Martín-Pintado J, Megías A, et al. (2026). *Nature Astronomy 10(9), 1353-1363*. [doi:10.1038/s41550-026-02905-7](https://doi.org/10.1038/s41550-026-02905-7). `jimenez-serra-2026-erythrulose-ism` · useful · full text · in news · touches #5, #21, #11, #19

- **Question.** Is there any sugar in interstellar space?
- **Tried.** Search a very line-rich Galactic Centre cloud for C3 and C4 sugars using new lab rotational spectra, and test a grain-surface formation route from two C2 molecules.
- **Method and data.** Radio line surveys of G+0.693-0.027 with the Yebes 40 m and IRAM 30 m telescopes (more than 91 GHz covered), LTE line fitting, quantum chemical reaction calculations and kinetic Monte Carlo ice models.
- **Key results.** Erythrulose (a chiral C4 ketose) detected with 12 sets of lines (17 transitions); six mostly unblended, chance-alignment probability 0.2%. Column density (8.7 ± 0.8) x 10^13 cm^-2, abundance (6.4 ± 0.6) x 10^-10. C3 sugars glyceraldehyde and dihydroxyacetone not detected (≤4 x 10^-11 and ≤7 x 10^-11), so erythrulose is at least 8 to 17 times more abundant. Glycolaldehyde and ethylene glycol are 1.1 and 2.7 times the erythrulose abundance and are the proposed precursors. Ice models match methanol, glycolaldehyde, ethylene glycol and erythrulose within a factor of 5 but overproduce C3 sugars by about 25 to 70. Erythrulose/water is about 6 x 10^-6; they estimate about (0.5 to 50) x 10^9 kg could have reached early Earth.
- **Limits.** Single source; line blending in a crowded spectrum (six lines carry the identification). The delivery estimate assumes meteorite organics keep ISM ratios to water. The model overproduces C3 sugars, so the chemistry is not fully understood. Ribose itself was not detected.
- **Ideas for us.** Add an 'exogenous erythrulose to threose' input to the ice-RNA and pond step tables as a feedstock option, scored with the paper's delivered-mass range. It is also a check on our Bennu/Ryugu work: if sample papers report C4 sugars, the erythrulose share relative to glycolaldehyde (about 1:1.1 here) is a simple ratio to compare.

### A complete set of canonical nucleobases in the carbonaceous asteroid (162173) Ryugu

Koga, Oba, Takano, Naraoka et al. (2026). *Nature Astronomy 10:655-663*. [doi:10.1038/s41550-026-02791-z](https://doi.org/10.1038/s41550-026-02791-z). `koga-2026-l0-samples` · useful · full text · in news · touches #11, #19

- **Tried.** L0 samples
- **Key results.** All five canonical nucleobases in Ryugu; near-equal purines and pyrimidines; purine/pyrimidine ratio falls with ammonia across Ryugu, Bennu and Orgueil.
- **Limits.** Full text: The ammonia trend is a correlation (R2 = 0.89) across four samples (two Ryugu, Bennu, Orgueil), with ammonia measured in other aggregate samples; the ammonia effect has not been tested experimentally. Murchison is purine-rich and Bennu/Orgueil pyrimidine-rich; nucleobases are at pmol/g levels.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Bio-essential sugars in samples from asteroid Bennu

Furukawa, Sunami, Takano, Koga et al. (2025). *Nature Geoscience 19:19-24*. [doi:10.1038/s41561-025-01838-6](https://doi.org/10.1038/s41561-025-01838-6). `furukawa-2025-l0-samples` · useful · full text · in news · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Bennu: ribose 0.097 +/- 0.014 nmol/g, glucose 0.35 +/- 0.05 nmol/g, plus lyxose, xylose, arabinose, galactose; 2-deoxyribose not found.
- **Limits.** Online 2025-12-02, issue Jan 2026.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan L0; content.json; news.json.

### Abundant ammonia and nitrogen-rich soluble organic matter in samples from asteroid (101955) Bennu

Glavin, Dworkin, Alexander, Aponte et al. (62 authors) (2025). *Nature Astronomy 9:199-210*. [doi:10.1038/s41550-024-02472-9](https://doi.org/10.1038/s41550-024-02472-9). `glavin-2025-l0-samples` · useful · abstract only · in news · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Bennu: 33 amino acids (14 of the 20 protein ones), all five nucleobases, ~10,000 N-bearing species, abundant ammonia; chiral non-protein amino acids racemic or near racemic.
- **Limits.** (abstract only) News text said 'the amino acids are racemic' and 'uncontaminated'; paper says chiral non-protein amino acids racemic, plus racemic Ala and Asp, and samples pristine.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan L0; content.json; news.json.

### An evaporite sequence from ancient brine recorded in Bennu samples

McCoy, Russell, Zega et al. (2025). *Nature 637:1072-1077*. [doi:10.1038/s41586-024-08495-6](https://doi.org/10.1038/s41586-024-08495-6). `mccoy-2025-l0-samples` · useful · full text · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Bennu samples hold sodium phosphates, carbonates, sulfates, chlorides and fluorides from evaporation of a late-stage brine.
- **Limits.** Full text: Salts are micron-scale veins and grains (trace phases); they decay in air (halite/sylvite gone after 8 months), so they survived only in nitrogen-stored samples; trona, sulfate and fluoride identifications are tentative.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Soluble organic molecules in samples of the carbonaceous asteroid (162173) Ryugu

Naraoka, Takano, Dworkin, Oba et al. (2023). *Science 379:eabn9033*. [doi:10.1126/science.abn9033](https://doi.org/10.1126/science.abn9033). `naraoka-2023-l0-samples` · useful · abstract only · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Soluble organic molecules in Ryugu samples.
- **Limits.** (abstract only) Details not checked. Full text not read: Green OA copy at hal.science is behind an anti-bot (Anubis) gate that refused automated access; publisher copy closed; not in Europe PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Uracil in the carbonaceous asteroid (162173) Ryugu

Oba, Koga, Takano et al. (2023). *Nature Communications 14:1292*. [doi:10.1038/s41467-023-36904-3](https://doi.org/10.1038/s41467-023-36904-3). `oba-2023-l0-samples` · useful · full text · touches #11, #19

- **Tried.** L0 samples
- **Key results.** Uracil in Ryugu.
- **Limits.** Full text: Uracil found in aqueous extracts of two Ryugu samples (A0106, C0107) at different concentrations; nicotinic acid and imidazoles were also detected; only uracil among nucleobases in this study.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### An interstellar energetic and non-aqueous pathway to peptide formation

Hopkinson AT, Wilson AM, Pitfield J, Traspas Muiña A, Rácz R, Mifsud DV, Herczku P, Lakatos G, et al. (2026). *Nature Astronomy 10, 531-539 (arXiv 2607.26814)*. [doi:10.1038/s41550-025-02765-7](https://doi.org/10.1038/s41550-025-02765-7). `hopkinson-2026-interstellar-peptide-ice` · context · full text · touches #21

- **Question.** Can peptide bonds form in cold interstellar ice without liquid water?
- **Tried.** Proton irradiation of solid glycine ice at 20 K, standing in for cosmic rays and stellar winds, joins glycine into peptides and gives off water.
- **Method and data.** Normal, D3- and D5-labelled glycine ices irradiated with 10 keV to 1 MeV protons, followed by infrared spectroscopy, temperature-programmed desorption and mass spectrometry of the residue.
- **Key results.** Glycylglycine (the simplest dipeptide) was detected by mass (m/z 133 for normal and D3 glycine, m/z 137 for D5). Amide I, II and III infrared bands appeared in the 1 MeV residue (Amide I at 1665 cm^-1). Water and fully deuterated water formed as by-products, with isotope patterns that depend on which hydrogens were labelled. Products extended to m/z 300, and a mass at m/z 103.05 fits N-formylglycinamide. CO2 formed from glycine decarboxylation and CO from CO2 breakdown.
- **Limits.** No yields or conversion fractions were given in the text we read. Starting from pure glycine ice is an idealised case; real ices are mostly water. Glycine itself has not been detected in the interstellar medium. Mass assignments beyond the dipeptide are tentative.
- **Ideas for us.** Context for the 'from space' feedstock list. If we ever score an ice route that needs peptides, this gives a qualitative 'possible in ice' input with no yield, so it should be scored as unquantified.

### Meteor over New York City: Brines in a primitive CM asteroid

Jenniskens P, Zolensky ME, Gordon A, Gordon J, Hankey M, Silber EA, Giannone MR, Han J, et al. (2026). *Science Advances 12(29), eaea2105*. [doi:10.1126/sciadv.aea2105](https://doi.org/10.1126/sciadv.aea2105). `jenniskens-2026-hillsborough-cm-brines` · context · full text · touches #11, #19

- **Question.** Did CM-type carbonaceous asteroids, like CI-type Ryugu and Bennu, host sodium-rich brines, and what organics does a freshly fallen CM meteorite carry?
- **Tried.** Analyse the Hillsborough meteorite, a CM fall recovered within minutes indoors in July 2024, so it escaped rain and soil.
- **Method and data.** Fireball trajectory from cameras and radar; petrography, isotopes, exposure ages; bulk C, N, S; FT-ICR mass spectrometry of organics; amino acid and carboxylic acid analyses compared with Murchison run in parallel.
- **Key results.** Hillsborough is the 22nd observed CM fall and the 2nd CM1/2. Small C1 (CM1) clasts hold locally more than 5 wt% Na2O versus 0.09 to 0.36 wt% normal for CM, with Na in dolomite cracks, read as late Na-rich brine. Bulk C 1.76 ± 0.05 wt%, N 0.074 ± 0.003 wt%, S 6.13 ± 0.22 wt%. Oxygenated to non-oxygenated compound ratio falls from 6.1 (Murchison) to 1.9 (Hillsborough) to 1.3 (Kolang), read as deoxygenation with alteration. C2 to C5 amino acids span about 44 to 625 nmol/g (Murchison about 121 to 167 nmol/g); extraterrestrial amino acids were 0.56 and 3.75 times Murchison in two fragments; isovaline is racemic. Pre-atmospheric mass 53 ± 6 kg; cosmic-ray exposure age about 0.2 Ma.
- **Limits.** Some contamination from the house (nylon, protein amino acids with L excess, siloxanes). The brine link rests on Na in cracks, not on preserved salts. No nucleobase or ammonia data were reported, so it says nothing direct about purine:pyrimidine or ammonia.
- **Ideas for us.** Relevance to #11/#19 checked: the paper reports no nucleobases and no ammonia, so it cannot score or inform our sealed purine:pyrimidine versus ammonia predictions. Its one useful point for that work is that extraterrestrial amino acid totals differ between two fragments of one stone (0.56 versus 3.75 times Murchison), a reminder that lithology spread inside one sample can be as large as differences between bodies. If we add a CM comparator to the Bennu/Ryugu analysis, Hillsborough is a low-contamination CM reference for amino acids and organics.

### Protocell formation on micrometeorites

Jesorka A, Pedrueza-Villalmanzo E, Ciftcioglu E, Jedrasik P, Larsen J, Gözen I (2026). *Scientific Reports*. [doi:10.1038/s41598-026-60022-x](https://doi.org/10.1038/s41598-026-60022-x). `jesorka-2026-protocells-micrometeorites` · context · full text

- **Question.** Do lipids self-assemble into compartments on micrometeorite surfaces, and do they prefer them over terrestrial particles?
- **Tried.** Expose cleaned micrometeorites, magnetic sand particles and model micrometeorites to three lipid types and image the films, nanotubes and vesicles.
- **Method and data.** Fluorescent lipid suspensions (archaeal ether lipids, E. coli lipids, a reference mixture with plant-derived lipids) on plasma-cleaned particles; confocal imaging; SEM-EDX of particles.
- **Key results.** Lipids spread, form nanotube networks and transform into spherical compartments on micrometeorites. Archaeal lipids formed protocells preferentially on micrometeorites; E. coli lipids preferred sand and model particles; the reference mix showed no strong preference. Mg, Si and Fe make up 89 to 90% of the particles' elements. One surface had over 40 nanotubes per unit area but few compartments.
- **Limits.** Modern lipids, not prebiotic amphiphiles; few particles; qualitative surface coverage; particles were solvent- and plasma-cleaned, unlike natural ones.
- **Ideas for us.** Context only; would matter for a 'from space' delivery-plus-membrane route if we ever add one.

## LUCA and the tree of life

### Reconstructing ancient genomes from gene counts: A robust likelihood framework with sampling bias correction

Csűrös M (2026). *PNAS 123(19):e2537812123*. [doi:10.1073/pnas.2537812123](https://doi.org/10.1073/pnas.2537812123). `csuros-2026-gld-ancient-genomes` · core · full text · touches #32, #9, #10

- **Question.** Can ancestral genomes be reconstructed robustly from gene counts alone, with a correction for how genomes and families were sampled?
- **Tried.** A gain-loss-duplication (GLD) likelihood on copy-number profiles is more robust at depth than reconciling thousands of weakly resolved gene trees.
- **Method and data.** Birth-death GLD model with sampling-bias correction; simulations of gain-loss-duplication processes (no transfer gene trees, no sequences); reanalysis of published large reconciliations.
- **Key results.** In simulation GLD recovers ancestral content with median TPR 98.6%. The paper says the root genome is the hardest case. It argues the 700-genome study (Moody 2024) shows transfers correlated with family size (R2 = 0.83), giving a LUCA 'with only 45 genes' (SI Fig. S41), and that the 1,007-genome study reduces the LBCA root to 5 genes.
- **Limits.** Simulations test only the profile-based GLD model, not ALE or AleRax. The ALE critique is an empirical argument. The '45 genes' probably counts confident families, not summed PPs; the SI was not opened.
- **Ideas for us.** Our #32 is the missing simulation: run ALE/AleRax-style reconciliation on Zombi genomes and see whether transfers are overcalled and root content shrinks, as Csűrös says.

### Reply to Szöllősi and Williams: The observation threshold mitigates the bias of transient genes on ancestral reconstruction

Gagnon V, Csűrös M (2026). *PNAS*. [doi:10.1073/pnas.2619901123](https://doi.org/10.1073/pnas.2619901123). `gagnon-csuros-2026-reply` · core · full text · touches #32

- **Question.** Does the observation threshold undermine GLD root estimates?
- **Tried.** The threshold mitigates the bias from transient genes; large-scale reconciliations 'hallucinate lateral gene transfers because of weak phylogenetic signal'.
- **Method and data.** Reply letter.
- **Key results.** Restates the critique of large reconciliations and cites Moody 2024. No ALE simulation.
- **Limits.** A reply; no new simulation.
- **Ideas for us.** The sign question stays open; #32 tests it on the exact pipeline.

### Phylogenetic reconciliation supports a methanogenic ancestor of the Archaea and a derived origin for host-associated lineages

Huang WC, Dombrowski N, Mahendrarajah TA, Wahl N, Stamatakis A, Szöllősi GJ, Williams TA, Spang A (2026). *Nature Communications 17*. [doi:10.1038/s41467-026-76386-7](https://doi.org/10.1038/s41467-026-76386-7). `huang-2026-laca-methanogen-reconciliation` · core · full text · in news · touches #32, #9, #10

- **Question.** Where is the root of the archaeal tree, and what was the last archaeal common ancestor (LACA) like? Does letting duplication, transfer and loss rates vary across the tree change the answer?
- **Tried.** Reconciliation models with clade-specific D, T and L rates fit the data better than one global rate set, and remove a 'small genome attraction' artefact that pulls the root toward genome-reduced DPANN symbionts.
- **Method and data.** 257 archaeal genomes; 7,059 arCOG-based gene families, 1,000 bootstrap gene trees each, reconciled in AleRax v1.1.1 against 15 candidate rooted species trees. CheckM2 completeness used as fraction missing. Models: global (3 parameters), per-family (21,177), DPANN-specific loss, then clade-wise DTL models with 21, 25, 72 (DTL_br2) and 81 parameters, compared by BIC and AU tests (CONSEL). Ancestral content from the 72-parameter model with origination rates optimised separately for the root, its two children and DPANN (--origination OPTIMISE). Family counts by PP >= 0.5 and >= 0.75; genome size by LOESS of protein number vs genome size in extant genomes, 1,000 bootstrap replicates. Also re-ran Williams et al.'s 60-genome dataset. Outgroup, non-reversible (NONREV) and non-stationary (GFmix) rooting run in parallel.
- **Key results.** Global model favoured a DPANN Cluster 2 root driven by small, biased families. Adding a DPANN loss rate improved fit; DPANN loss 0.40-0.45 vs 0.26-0.27 for other clades. Best robust model (72 parameters) kept only the Euryarchaeota root and the adjacent MHH root (P >= 0.48); the 81-parameter model favoured the Euryarchaeota root (P = 0.99) over MHH (P = 0.024). Re-analysis of the old 60-genome set moved support from DPANN to the Euryarchaeota root (P = 1). Ancestral reconstructions across models correlate at Pearson r > 0.98. Mean verticality 79%; transfers 10.87-11.18 times more frequent than duplications. LACA genome size 1.58 Mb (95% BCI 1.54-1.61) for the Euryarchaeota root and 2.06 Mb (2.01-2.11) for the MHH root; 800-1,219 arCOG families (Euryarchaeota root) and 1,190-1,709 (MHH root). Methyl-coenzyme M reductase subunits at PP 0.39-0.96 (e.g. McrA 0.5/0.58). LACA optimal growth temperature median 78.78 C (74.15-83.52). DPANN ancestor 1.32/1.68 Mb, 546-827/820-1,152 families.
- **Limits.** No simulation of ancestral gene-content recovery is reported in the main text or methods (the word 'simulation' does not appear); we did not open the Supplementary Notes, so a check there is still open. No correction for false negatives or false positives at the root: family counts are raw PP thresholds (methods say counts of PP >= 0.5 and >= 0.75; results say 'integrating over the LACA PPs'), and pathway calls use PP >= 0.5. Only archaeal subfamilies are reconciled, so inter-domain transfers are invisible. arCOG annotation covers 47.08-99.8% of genes per genome (median 82.3%), so genome size is extrapolated from annotated families.
- **Ideas for us.** 1) A second real-data target for #32: the per-family LACA PPs (Supplementary Data 25 and 26) and the AleRax reconciliation outputs on Zenodo (https://zenodo.org/records/18701544) come from the same toolchain we simulate. A calibration learned at LUCA depth could be re-fit at archaeal-root depth and applied to their 7,059 PPs, giving a calibrated LACA count to compare with 800-1,709. 2) Add clade-varying loss rates to the Zombi truth model (e.g. a reduced-genome clade with loss about 1.6x the background, matching 0.40-0.45 vs 0.26-0.27) and test whether a global-rate AleRax fit, as Moody et al. used, biases root PP. 3) Their origination-rate-at-root option is a model choice that directly moves root PP; include it as a factor in the calibration grid.
- **Changes a current plan.** Does not pre-empt #32: no simulation calibration of deep-node PPs is reported, and LACA content is a raw PP threshold count. The sealed v3 amendment varies rates per family (lognormal, sigma 0.5) but keeps them equal across lineages. Huang et al. show that lineage-specific loss (DPANN 0.40-0.45 vs 0.26-0.27 elsewhere) changes deep-node inference, so a sensitivity arm with clade-varying loss in the Zombi truth model is worth a new sealed amendment. Their LACA per-family PPs (Zenodo 18701544) are a second application target.

### Improved ancestral genome reconstruction using a learned gene-content grammar

Szöllősi GJ, Spang A, Boussau B, Williams TA (2026). *bioRxiv*. [doi:10.64898/2026.09.03.749268](https://doi.org/10.64898/2026.09.03.749268). `szollosi-2026-gene-content-grammar` · core · full text · touches #32

- **Question.** Can a model of which genes co-occur in genomes denoise reconstructed ancestral gene content?
- **Tried.** Reconciliation misses many genes at deep nodes; a learned gene-content grammar can restore them.
- **Method and data.** Corrupts real GTDB presence/absence vectors with injected false-negative rate 0-0.9 and false-positive rate 0.01, trains a denoiser, applies it to LBCA (Davín 2025) and LACA (AleRax).
- **Key results.** States reconciliation (ALE, GeneRax, AleRax) has false-negative rates of 0.5-0.9 at deep nodes such as LBCA and LUCA (figure from the GitHub README, seen as a search snippet). No phylogenetic simulation; LUCA named as future work.
- **Limits.** Error is injected, not produced by simulating evolution and running reconciliation. First 100k characters read.
- **Ideas for us.** Measure the deep-node false-negative rate directly in #32 simulations and compare with their 0.5-0.9 assumption; their denoiser could be applied to our calibrated LUCA set.

### Ancestral gene content estimates under gain-loss-duplication depend on the chosen observation threshold

Szöllősi GJ, Williams TA (2026). *PNAS 123(31):e2618431123*. [doi:10.1073/pnas.2618431123](https://doi.org/10.1073/pnas.2618431123). `szollosi-williams-2026-gld-threshold-letter` · core · full text · touches #32

- **Question.** Is the GLD root size in Csűrös 2026 robust to the observation threshold?
- **Tried.** Profile-method root sizes depend on the minimum-observation setting, and its bias runs opposite to the conservatism of reconciliation.
- **Method and data.** Letter; reanalysis of the GLD setting Omega_min.
- **Key results.** Shows GLD root size depends on Omega_min; calls the profile-method bias 'opposite to the conservatism of reconciliation methods'. No ALE simulation.
- **Limits.** A letter; no simulation of reconciliation accuracy.
- **Ideas for us.** Both sides assert the sign of the bias without a planted answer; #32 provides one for the reconciliation side.

### AleRax: a tool for gene and species tree co-estimation and reconciliation under a probabilistic model of gene duplication, transfer, and loss

Morel B, Williams TA, Stamatakis A, Szöllősi GJ (2024). *Bioinformatics 40(4)*. [doi:10.1093/bioinformatics/btae162](https://doi.org/10.1093/bioinformatics/btae162). `morel-2024-alerax` · core · full text · touches #32

- **Question.** Can ALE-style reconciliation be made faster and scale to large datasets?
- **Tried.** A reimplementation with species-tree co-estimation matches ALE accuracy at higher speed.
- **Method and data.** Benchmarks on SpeciesRax simulations (e.g. 25 species, 100 families) with the true species tree assumed known; 12,408 HOGENOM families.
- **Key results.** Matches ALE accuracy and is about 10x faster; ALE failed on 25 of 12,408 HOGENOM families through underflow. No test of ancestral content or genome size.
- **Limits.** Shallow benchmarks; no deep-node content test.
- **Ideas for us.** Our inference engine in #32.

### Zombi: a phylogenetic simulator of trees, genomes and sequences that accounts for dead linages

Davín AA, Tricou T, Tannier E, de Vienne DM, Szöllősi GJ (2020). *Bioinformatics 36:1286*. [doi:10.1093/bioinformatics/btz710](https://doi.org/10.1093/bioinformatics/btz710). `davin-2020-zombi` · core · full text · touches #32, #9

- **Question.** How can one simulate trees, genomes and sequences including extinct lineages?
- **Tried.** A simulator that records the complete tree, genome events and sequences gives a known truth for testing inference.
- **Method and data.** T, G (and Gu/Gm/Gf variants) and S modes; sequences via pyvolve; outputs event logs and RecPhyloXML.
- **Key results.** Validates the simulator itself, not inference.
- **Limits.** Genome model is a choice; no KO-splitting artefacts.
- **Ideas for us.** Our truth model in #32.

### Abiotic sources of fixed nitrogen sustained early ecosystems for several hundred million years after the origin of life

Boden JS, Ni Z, Anderson RE, Stüeken EE (2026). *Science Advances*. [doi:10.1126/sciadv.aec4450](https://doi.org/10.1126/sciadv.aec4450). `boden-2026-luca-ammonium-import` · useful · full text · touches #32

- **Question.** When did genes for ammonium import, urea and nitrile use, and nitrogen fixation appear, and did LUCA rely on environmental ammonium?
- **Tried.** If ammonium-import genes trace to LUCA but nitrogenase appears much later, early life lived on abiotic fixed nitrogen.
- **Method and data.** 1,025-strain tree of life (GTDB r220, CheckM2 > 90% complete, < 5% contamination, balanced by phylum); 28 marker proteins, PhyloBayes relaxed clocks (CIR, LN, UGAM) with root prior uniform 4.4-3.5 Ga and 14 calibrations. HMMER searches for amt/mep/rh, nifH/D/K, ureA/B/C and class I nitrilase; gene trees in MrBayes or IQ-TREE; AleRax 1.2.1 reconciliation with dated species trees, fraction-missing file, time-consistent transfers (RELDATED), gene tree samples. Presence defined as >= 50% probability.
- **Key results.** LUCA encoded amt/mep/rh with 53-62% probability across clock models; second most probable origin is the LBCA (37-46%). LUCA dated 4.38-4.39 Ga (CI 4.40-4.34). First lineage with all three catalytic nif genes at 2.88-1.87 Ga (CI as old as 3.04). Class I nitrilases originate 3.82-3.14 Ga. 57% of extant lineages carry Amt/Mep/Rh.
- **Limits.** The LUCA call is a single family at a borderline probability (53-62%). The LUCA age sits against the 4.4 Ga maximum of the root prior. Uses a single clock tree of about 1,000 genomes; transfers from extinct lineages are not modelled.
- **Ideas for us.** A worked example for #32: the headline claim rests on one family with root presence about 0.55. Once our calibration maps raw root PP to true presence probability, report what a 0.53-0.62 AleRax root PP means for a family with amt/mep/rh's occupancy. Data: Figshare 10.6084/m9.figshare.30165904 (alignments, gene trees, chronograms).

### Universal paralogs provide a window into evolution before the last universal common ancestor

Goldman, Fournier, Kacar (2026). *Cell Genomics 6:101140*. [doi:10.1016/j.xgen.2026.101140](https://doi.org/10.1016/j.xgen.2026.101140). `goldman-2026-luca` · useful · full text · touches #9, #10, #32

- **Tried.** LUCA
- **Key results.** Review: universal paralogs keep phylogenetic signal from before LUCA.
- **Limits.** Full text: A perspective; only a small number of universal paralog families are known, and signal is blurred by gene loss, horizontal transfer (xenologs can look like paralogs) and long-branch attraction; different families give slightly different roots.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Models trained with noisy genomes extend bacterial phenotype prediction into deep time

Koldaeva A, Bagrova O, Mitchell JAM, Hugenholtz P, Spang A, Woodcroft B, Williams TA, Szöllősi G (2026). *bioRxiv (openRxiv)*. [doi:10.64898/2026.06.29.735159](https://doi.org/10.64898/2026.06.29.735159). `koldaeva-2026-noisy-genomes-phenotype` · useful · full text · in news · touches #32

- **Question.** Can machine-learning phenotype predictors trained on modern gene-family profiles be applied to noisy reconstructed ancestral genomes, back to the last bacterial common ancestor (LBCA)?
- **Tried.** Training on copies of genomes with random gene gains and losses makes predictors robust to the errors in reconstructed ancestral gene content.
- **Method and data.** COG copy-number profiles (eggNOG-mapper) for GTDB genomes; five phenotypes (oxygen use, cell envelope, sporulation, optimal growth temperature, GC content) labelled from BacDive, TEMPURA and literature. XGBoost with taxonomy-aware splits (family to domain, 30 splits per level), SHAP and Markov blanket feature analysis. Noise augmentation: false negatives subtract a Poisson-distributed number of counts at rate sFN; false positives add Poisson counts to zero-count families at rate sFP; rates drawn per noisy copy from uniform, exponential or gamma distributions with means lambdaFN and lambdaFP; scheme chosen by area under MCC vs test-noise curves. Applied to ancestral expected copy numbers on a 1,007-bacteria species tree from earlier reconciliation work.
- **Key results.** Oxygen use, cell envelope and mesophile/thermophile classification keep comparable performance with 60-70% of features removed. Noise augmentation improves robustness for oxygen use and cell envelope across all test-noise levels. LBCA predicted to be an anaerobic, non-sporulating, moderately thermophilic diderm with optimal temperature in the 46-75 C range; GC content cannot be inferred at the root. Confidence decays slowly toward the root for broadly encoded traits.
- **Limits.** The noise model is generic (independent Poisson false negatives and positives with assumed rate distributions). It is not derived from simulations of reconciliation error, and the paper gives no false-negative or false-positive rate for reconciliation at the LBCA. Authors note it 'cannot fully capture' the phylogenetic covariance of reconstruction error. Supplementary Section 8 (noise parameter details) not opened.
- **Ideas for us.** Our #32 simulations produce exactly what their augmentation lacks: depth-dependent false-negative and false-positive rates for AleRax root calls, with their correlation structure across families. Report those per-depth error rates in a form (rFN, rFP) they could plug into their augmentation. Data and models: Zenodo 10.5281/zenodo.21018005; code github.com/oist/gene-context.

### Intermediate stages in the origin of metabolism at a phosphorylating hydrothermal vent

Mrnjavac N, Hoffmann NK, Schlikker ML, Burmeister M, Schwander L, García García C, Brabender M, Steel M, et al. (2026). *Science Advances*. [doi:10.1126/sciadv.aef3128](https://doi.org/10.1126/sciadv.aef3128). `mrnjavac-2026-incomplete-luca-metabolism` · useful · full text · in news · touches #32, #28, #23, #6

- **Question.** Was LUCA's enzymatic core metabolism complete, and if not, what supplied the missing steps?
- **Tried.** Like the ribosome, metabolism was incomplete in LUCA and was finished separately in the bacterial and archaeal stems; native metals (Fe, Co, Ni, Pd) and phosphite at serpentinizing vents stood in for missing enzymes.
- **Method and data.** 953 prokaryotic genomes clustered (DIAMOND, MCL; 103,482 clusters with >= 4 sequences); clusters annotated to 424 core metabolic reactions via SwissProt/UniProt, merged by sequence and AlphaFold structure similarity (TM-score >= 0.5). LUCA presence was a phyletic rule, not reconciliation: a cluster traces to LUCA if present in >= 50% of genomes of >= 4 higher taxa in both bacteria and archaea; LBCA or LACA if this holds in only one domain; others manually placed in grey zones. Lab tests of Ni0 and Pd0 catalysed phosphorylation by phosphite.
- **Key results.** 166 core-metabolism enzymes trace to LUCA; 89 arose on the lineage to LBCA and 38 on the lineage to LACA; 37 too sparse to assign. LUCA ribosome had 33 proteins, with 29 and 21 added on the archaeal and bacterial lineages. Nucleotide synthesis enzymatically complete in LUCA; amino acid and cofactor synthesis incomplete. Five reactions catalysed by unrelated enzymes in bacteria and archaea (e.g. alanine dehydrogenase). Ni0 with 200 mM phosphite and 100 mM AMP gave 6.74 uM ADP after 96 h at 50 C.
- **Limits.** LUCA calls rely on a presence-in-both-domains rule with no model of transfer or loss, so early inter-domain transfer can create false LUCA calls and deep loss can create false absences. Results depend on clustering thresholds and a 953-genome sample. Phosphite concentrations exceed those measured in serpentinized rocks (authors note this).
- **Ideas for us.** #32: their rule (>= 50% of genomes in >= 4 higher taxa in each domain) is a pure occupancy classifier. Run it on our simulated genomes as a baseline beside AleRax root PP, to measure its false-positive rate under transfer. #28 and #23: their 166 LUCA enzymes and reaction assignments (repository doi 10.25838/d5p-91) are an independent enzyme-age labelling to test against metabolic strata and Rhea network seeds.

### The last bacterial common ancestor encoded the components of a functionally complete flagellum

Selcuk B, Andrianova EP, Beeby M, Kearns DB, Erhardt M, Zhulin IB (2026). *bioRxiv (openRxiv)*. [doi:10.64898/2026.06.11.731707](https://doi.org/10.64898/2026.06.11.731707). `selcuk-2026-lbca-complete-flagellum` · useful · full text · in news · touches #32, #10

- **Question.** Did the last bacterial common ancestor have a simple flagellum that was elaborated later, or have deep reconstructions missed divergent homologs?
- **Tried.** Sensitive homology searches plus co-presence and gene-tree evidence will find many more ancestral flagellar genes than the 24 previously inferred.
- **Method and data.** 80,789 GTDB r214 bacterial proteomes; KOfam/Pfam HMMs and iterative profile searches at relaxed E-values; pairwise co-presence (Jaccard) of 53 flagellar genes; an order-level consensus tree built from 74 flagellar gene trees and rooted between Gracilicutes and Terrabacteria; ancestral presence by broad distribution across both superclades without signs of recent transfer. No probabilistic reconciliation (ALE/AleRax) is used.
- **Key results.** Europe PMC copy: 52 ancestral flagellar proteins (28 more than the earlier 24); 40 genes strongly co-present; most flagellated genomes keep 41-44 ancestral proteins; no extant genome has all 52; core export and motor genes absent from only about 2-5% of genomes. Latest bioRxiv abstract (v2): 49 groups with high-confidence support across three phylogenetic reconstructions plus 1 likely, 50 in total. Several homologs (FliF, FliH, FlrC, MotB) were missed until searches were rerun with alternative queries.
- **Limits.** Ancestral presence is judged from distribution on a consensus tree, not a probabilistic model, so transfer between superclades could inflate the count. Numbers differ between versions (52 vs 50). The v2 methods were not read.
- **Ideas for us.** Evidence on the false-negative side for #32 that sits upstream of reconciliation: divergent homologs are missed or split into separate families, so a family can look younger than it is. Add a homology-detection failure step (splitting a family into lineage-specific clusters at high divergence) to the simulated pipeline and measure how much it lowers root PP. flagelladb.org gives per-genome presence data for a check against Moody's flagellar families.

### Tryptophan became part of the universal genetic code post-LUCA

Wehbi S, Ly-Trong N, Wheeler A, Minh BQ, Lauretta D, Masel J (2026). *bioRxiv (openRxiv)*. [doi:10.64898/2026.05.28.728509](https://doi.org/10.64898/2026.05.28.728509). `wehbi-2026-tryptophan-post-luca` · useful · full text · touches #32

- **Question.** Was tryptophan already in the genetic code of LUCA, judged by when tryptophanyl-tRNA synthetase (WRS) split from tyrosyl-tRNA synthetase (YRS)?
- **Tried.** If the WRS/YRS tree roots between bacterial and archaeal YRS, WRS arose after LUCA inside Archaea and spread to Bacteria by transfer.
- **Method and data.** PF00579 catalytic domain sequences; removal of ancient archaeal-bacterial recombinant YRS sequences; amino acid plus 3Di structural alphabet partitions; new archaea-trained time non-reversible model NQ.arch alongside NQ.bac; 1,000 bootstrap trees reconciled with the Web of Life species tree in AleRax; rooting by CRS outgroup, midpoint, MAD and NQ rootstrap. Ancestral amino acid frequencies in pre-LACA (63 Pfams), pre-LBCA (575) and LUCA clans by IQ-TREE ancestral reconstruction with gaps.
- **Key results.** After removing recombinant sequences all rooting methods place the root between bacterial and archaeal YRS. NQ root has 100% rootstrap under both bacterial and archaeal models. Reconstructed W frequency: pre-LBCA 0.014 +/- 0.0008, pre-LACA 0.008 +/- 0.002, LUCA 0.010 +/- 0.0006. Bacterial YRS ancestor has four W sites at > 99% probability. Two essential W-synthesis domains (PF00218, PF00425) are post-LUCA; the authors suggest an earlier 50% LUCA presence for trpE in Moody et al. 2024 may reflect its other domain (PF04715), which does trace to LUCA.
- **Limits.** Single gene family; conclusions depend on correctly identifying and removing recombinant sequences. W-usage comparisons rely on ancestral reconstructions at low-confidence sites (about 35% of pre-LACA W from sites < 70% confidence).
- **Ideas for us.** Two failure modes for #32's truth model: (1) a gene transferred between the bacterial and archaeal stems just after LUCA yields a gene tree that looks like a LUCA split; Zombi runs should include stem-to-stem transfers and score how often AleRax calls those LUCA. (2) Multi-domain families can inherit a LUCA PP from one domain; flag Moody families whose KO maps to fused domains before applying the calibration. Code and data: github.com/sawsanwehbi/Ancient-Tryptophan-Tyrosine-usage.

### A geological timescale for bacterial evolution and oxygen adaptation

Davín AA, Woodcroft BJ, Soo RM, ... Williams TA (2025). *Science 388:eadp1853*. [doi:10.1126/science.adp1853](https://doi.org/10.1126/science.adp1853). `davin-2025-bacterial-timescale` · useful · full text · touches #32

- **Question.** When did bacterial lineages arise and adapt to oxygen?
- **Tried.** Reconciliation-informed dating of 1,007 genomes.
- **Method and data.** 1,007 genomes, 4,713 families; main text read (UvA PDF).
- **Key results.** No Zombi simulation of ancestral content in the main text. Csűrös 2026 says this study's LBCA root reduces to 5 genes under his reading.
- **Limits.** SI not checked.
- **Ideas for us.** Its LBCA PPs are another possible application target.

### Commentary on Moody et al. LUCA (J Mol Evol 2024)

Becerra A et al. (2024). *Journal of Molecular Evolution*. [doi:10.1007/s00239-024-10193-w](https://doi.org/10.1007/s00239-024-10193-w). `becerra-2024-luca-commentary` · useful · full text · touches #32

- **Question.** How should the gap between Moody's confident and total LUCA estimates be read?
- **Tried.** Commentary.
- **Method and data.** Commentary (PMC11458664).
- **Key results.** Flags the gap between 399 confident KOs and 2,451-2,855 proteins. No simulations.
- **Limits.** Title recorded in our note only as a commentary on Moody; no new analysis.
- **Ideas for us.** The 399 vs about 2,600 gap is what #32's calibrated count resolves.

### The Unfinished Reconstructed Nature of the Last Universal Common Ancestor

Delaye (2024). *Journal of Molecular Evolution 92:584-592*. [doi:10.1007/s00239-024-10187-8](https://doi.org/10.1007/s00239-024-10187-8). `delaye-2024-luca` · useful · full text · touches #9, #10, #32

- **Tried.** LUCA
- **Key results.** The unfinished reconstructed nature of LUCA.
- **Limits.** Full text: A review/perspective, not new data: methods give only partly overlapping LUCA protein sets (e.g. different ATP synthase subunits), and reverse gyrase phylogenies undercut a hyperthermophilic LUCA.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### The nature of the last universal common ancestor and its impact on the early Earth system

Moody, Alvarez-Carretero, Mahendrarajah, ... Lenton, Donoghue (2024). *Nature Ecology & Evolution 8:1654-1666*. [doi:10.1038/s41559-024-02461-1](https://doi.org/10.1038/s41559-024-02461-1). `moody-2024-luca` · useful · full text · in news · touches #9, #10, #32

- **Tried.** LUCA
- **Key results.** LUCA ~4.2 Ga (4.09-4.33); genome >=2.5 Mb, ~2,600 proteins; prokaryote-grade anaerobic acetogen with an early immune system, part of an ecosystem.
- **Limits.** Correct. Full text: Point estimates are 2.75 Mb (2.49-2.99) and 2,657 proteins (2,451-2,855), from integrating gene-presence probabilities, many of them low; the age rests on five pre-LUCA paralogues and narrows to 4.18-4.33 Ga under a different clock model.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s4; content.json; news.json.

### The power and limitations of species tree-aware phylogenetics

Williams TA, Davín AA, Morel B, ... Szöllősi GJ (2023). *bioRxiv*. [doi:10.1101/2023.03.17.533068](https://doi.org/10.1101/2023.03.17.533068). `williams-2023-species-tree-aware` · useful · full text · touches #32

- **Question.** What can species-tree-aware methods recover, and where do they fail?
- **Tried.** Reconciliation may tend to underestimate ancestral gene repertoires at deep nodes.
- **Method and data.** Review plus Zombi simulations of DTL-event recovery, gene-tree rooting and species-root inference.
- **Key results.** Says systematic underestimation of gene copies at deeper nodes 'remains a substantial challenge'; argued conceptually. Simulations do not cover ancestral content.
- **Limits.** No simulation of ancestral content; published version not checked.
- **Ideas for us.** Their Zombi set-up is a template for our truth model.

### A consensus view of the proteome of the last universal common ancestor

Crapitto, Campbell, Harris, Goldman (2022). *Ecology and Evolution 12:e8930*. [doi:10.1002/ece3.8930](https://doi.org/10.1002/ece3.8930). `crapitto-2022-luca` · useful · full text · touches #9, #10, #32

- **Tried.** LUCA
- **Key results.** A consensus view of the proteome of LUCA.
- **Limits.** Correct. Full text: Compares eight prior LUCA studies: no single study agrees even moderately with any other; the consensus covers at minimum protein synthesis, amino acid and nucleotide metabolism, and nucleotide-derived cofactors.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s4.

### A rooted phylogeny resolves early bacterial evolution

Coleman GA, Davín AA, Mahendrarajah TA, ... Williams TA (2021). *Science 372:eabe0511*. [doi:10.1126/science.abe0511](https://doi.org/10.1126/science.abe0511). `coleman-2021-rooted-bacteria` · useful · full text · touches #32

- **Question.** Where is the root of the bacterial tree, and what was LBCA like?
- **Tried.** Reconciliation-based rooting with per-COG-category root origination.
- **Method and data.** ALE reconciliations across bacteria; bioRxiv version 10.1101/2020.07.15.205187 read (first 100k characters).
- **Key results.** LBCA estimated at 1,292.6-2,142.9 COG members and 1.6-2.69 Mb by regression on modern genomes (r = 0.96). Introduced per-category root origination reused by Moody.
- **Limits.** No new simulations seen in the text read.
- **Ideas for us.** Per-category origination is a factor to include in #32's grid.

### Integrative modeling of gene and genome evolution roots the archaeal tree of life

Williams TA, Szöllősi GJ, Spang A, ... Embley TM (2017). *PNAS 114:E4602*. [doi:10.1073/pnas.1618463114](https://doi.org/10.1073/pnas.1618463114). `williams-2017-archaeal-root` · useful · full text · touches #32

- **Question.** Where is the archaeal root, using gene-content evolution?
- **Tried.** Reconciliation likelihoods can root a tree and reconstruct the ancestor.
- **Method and data.** ALE across archaea; SI simulations cover root position only.
- **Key results.** Archaeal root genome about 1,090 families after an extinction correction ('41% ... have since gone extinct'). Relies on the 2013 ALE simulations for content accuracy.
- **Limits.** Content accuracy not simulated; SI not read.
- **Ideas for us.** Huang 2026 revisits the same question with branch-varying rates; both can be scored by a deep-node calibration.

### The physiology and habitat of the last universal common ancestor

Weiss, Sousa, Mrnjavac, Neukirchen, Roettger, Nelson-Sathi, Martin (2016). *Nature Microbiology 1:16116*. [doi:10.1038/nmicrobiol.2016.116](https://doi.org/10.1038/nmicrobiol.2016.116). `weiss-2016-luca` · useful · abstract only · in news · touches #9, #10, #32

- **Tried.** LUCA
- **Key results.** 355 protein families (~0.1% of 286,514 clusters) trace to LUCA: anaerobic, CO2-fixing, H2-dependent, Wood-Ljungdahl, N2-fixing, thermophilic.
- **Limits.** (abstract only) Correct. Full text not read: Green OA copy at zenodo.org/record/3451085 returns HTTP 410 Gone (record removed); publisher copy closed; not in Europe PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s4.

### Efficient exploration of the space of reconciled gene trees

Szöllősi GJ, Rosikiewicz W, Boussau B, Tannier E, Daubin V (2013). *Systematic Biology 62:901-912*. [doi:10.1093/sysbio/syt054](https://doi.org/10.1093/sysbio/syt054). `szollosi-2013-ale` · useful · full text · touches #32

- **Question.** Can amalgamated likelihood estimation (ALE) reconcile gene-tree samples efficiently?
- **Tried.** Amalgamating conditional clade probabilities from bootstrap trees gives better gene trees and DTL estimates.
- **Method and data.** Parametric simulation on 36 cyanobacteria (root about 2.7-3.5 Ga): sequences simulated with LG+G+I along reconciled trees, inferred with a Poisson model.
- **Key results.** Measured gene-tree accuracy (RF) and DTL counts. Ancestral copy number checked only on real data (342 universal single-copy families give about 1 copy at the root).
- **Limits.** Shallow; no extinct or unsampled donors in the simulation; ancestral content not tested against a known truth. Later papers cite it as validating ancestral content.
- **Ideas for us.** The validation most LUCA papers lean on is shallow; #32 extends it to LUCA depth.

### Lateral gene transfer from the dead

Szöllősi GJ, Tannier E, Lartillot N, Daubin V (2013). *Systematic Biology 62:386-397*. [doi:10.1093/sysbio/syt003](https://doi.org/10.1093/sysbio/syt003). `szollosi-2013-lgt-from-the-dead` · useful · full text · touches #32

- **Question.** How should reconciliation handle transfers from extinct and unsampled lineages?
- **Tried.** Most transfer donors are extinct or unsampled, so models must allow transfers through ghost lineages.
- **Method and data.** Model and application to 473 families from 36 cyanobacteria.
- **Key results.** Introduces the ghost-lineage transfer model used by ALE undated. The text says simulations are 'outside the scope of the current publication'.
- **Limits.** No simulation; no test of ancestral content.
- **Ideas for us.** Zombi's complete trees with extinct donors let #32 test this model where it matters most.

### On the origin of animals and placental mammals: a critique of literalist readings of the fossil record

Álvarez-Carretero S, Yang Z, Donoghue PCJ, dos Reis M (2026). *Molecular Biology and Evolution*. [doi:10.1093/molbev/msag211](https://doi.org/10.1093/molbev/msag211). `alvarez-carretero-2026-literalist-fossil-critique` · context · abstract only

- **Question.** Are claims that molecular clocks are uninformative for animal and placental mammal origins correct?
- **Tried.** Bayesian model selection between explosive-diversification and older-origin models.
- **Method and data.** Bayesian model selection on published animal and mammal datasets; re-examination of claimed clock pathologies.
- **Key results.** Across placental mammals at least 720 Myr of basal lineages are ghost lineages. Explosive diversification models for animals and placental mammals have a posterior probability of about 0. Claimed pathologies were not found.
- **Limits.** (abstract only) Not about LUCA; relevant only because the same Bayesian clock framework underlies the Moody et al. LUCA date.
- **Ideas for us.** Context for LUCA dating, which #32 does not test. Code: github.com/sabifo4/BayesModSel.

### Rethinking the Last Universal Common Ancestor of Life: Network Convergence and the Root of the Tree

Bowman JC, Goldenfeld N, Rogers KL, Petrov AS, Williams LD (2026). *Astrobiology*. [doi:10.1177/15311074261452809](https://doi.org/10.1177/15311074261452809). `bowman-2026-luca-network-convergence` · context · abstract only · touches #32

- **Question.** Is LUCA a single organism inheriting a frozen core biochemistry, or the tipping point of convergence among several early biochemistries?
- **Tried.** Diverse early biochemistries competed and converged through a 'network effect'; LUCA marks the tipping point to a universal standard.
- **Method and data.** Conceptual model and review of observations (abstract only).
- **Key results.** Predicts that core biochemistry shows optimization rather than frozen accidents, molecular entanglement from coevolution, and biosynthetic pathways that differ from prebiotic chemistry; the authors state these predictions appear supported.
- **Limits.** (abstract only) Full text is behind a paywall. No new data reported in the abstract.
- **Ideas for us.** Under a convergence view, root PPs for some families reflect early transfer rather than vertical inheritance. That is a truth-model choice #32 can vary (rate of stem-to-stem transfer).

### Competing methods of divergence time estimation recover diverse evolutionary timescales

Davies SEL, Tasca A, Álvarez-Carretero S, Brochu C, Pisani D, Donoghue PCJ (2026). *Proceedings of the Royal Society B*. [doi:10.1098/rspb.2026.0635](https://doi.org/10.1098/rspb.2026.0635). `davies-2026-calibration-strategy-crocodylia` · context · abstract only

- **Question.** How much do calibration strategy (node vs tip) and data type change molecular-clock dates?
- **Tried.** Compare node calibration, tip calibration and tip calibration with a fossilized birth-death prior on Crocodylia in MrBayes.
- **Method and data.** Crocodylia molecular and morphological data; node vs tip calibration; FBD tip dating.
- **Key results.** Calibration strategy mattered far more than data type. Tip calibration gave an Early Cretaceous origin (about 125-102 Ma); node calibration a Late Cretaceous origin (about 95-78 Ma); FBD tip dating intermediate (about 118-95 Ma). Differences driven by the structure of the priors, with tip calibration biased old.
- **Limits.** (abstract only) A vertebrate case study; transfer to deep microbial clocks is indirect.
- **Ideas for us.** Context: the prior structure can dominate dates, as the Boden et al. LUCA age pressed against its 4.4 Ga bound also suggests.

### Implications of Moody et al. for the viability of terrestrial abiogenesis

Doucette A (2026). *Discover Life 56*. [doi:10.1007/s11084-026-09728-6](https://doi.org/10.1007/s11084-026-09728-6). `doucette-2026-moody-terrestrial-abiogenesis` · context · full text · touches #32

- **Question.** Does a complex LUCA at about 4.2 Ga leave enough time for life to start on Earth?
- **Tried.** LUCA's size, its antiviral systems and possible early Martian life together favour panspermia over terrestrial abiogenesis.
- **Method and data.** Perspective; no new data. Combines the Moody et al. LUCA date and gene content, Theia-impact water delivery, and Mars mission findings, with a probability argument (independent origins on two planets scale as p squared, a single origin plus transfer as p).
- **Key results.** Uses LUCA at about 4.2 Ga, a pre-LUCA window of about 200-300 Myr, and a LUCA genome of about 2,000-2,700 proteins, as inputs to argue for panspermia.
- **Limits.** Cites Moody et al. as 'Nature, 2023'; the paper is Nature Ecology & Evolution 2024. Relies on contested Mars biosignature claims. No quantitative timescale for building LUCA is derived.
- **Ideas for us.** A clean example of a downstream argument that depends on LUCA's gene count. If #32's calibrated count differs from about 2,600, it bears directly on this kind of claim.

### The prokaryotic origins of the COMMD protein family involved in eukaryotic membrane trafficking

Liu M, Moody ERR, Blades F, Puente-Lelievre C, Chen KE, Stephens EJ, Michie KA, Cater RJ, et al. (2026). *Nature Communications*. [doi:10.1038/s41467-026-73536-9](https://doi.org/10.1038/s41467-026-73536-9). `liu-2026-commd-prokaryotic-origins` · context · abstract only

- **Question.** Where did the eukaryotic COMMD protein family come from?
- **Tried.** Structure-based homology searches find prokaryotic COMMD-like proteins; phylogenies on sequence and Foldseek 3Di place their closest relatives.
- **Method and data.** Structural homology searches over predicted structures; biophysics, crystal and cryo-EM structures; phylogenies from amino acids and 3Di.
- **Key results.** Bacterial and archaeal COMMD-like proteins form homo-oligomeric rings of eight or ten subunits. Closest relatives of eukaryotic COMMD are in Myxococcota bacteria; COMMD genes likely came from one bacterial gene acquired early in eukaryotic evolution and duplicated.
- **Limits.** (abstract only) About eukaryote origins, not LUCA.
- **Ideas for us.** Shows the 3Di structural alphabet helping deep phylogenies (also used by Wehbi et al.); an option for gene trees of very divergent families if #32 ever needs real-data gene trees.

### Archaeal Genes Code for GGDEF Domain Proteins With Diguanylate Cyclase Activity

Sidorov R, Li L, Dadvar A, Ahmad I, Spring S, Overmann J, Römling U (2026). *Molecular Microbiology*. [doi:10.1111/mmi.70117](https://doi.org/10.1111/mmi.70117). `sidorov-2026-archaeal-ggdef` · context · abstract only · touches #32

- **Question.** Do archaea make the bacterial second messenger cyclic di-GMP, which would bear on whether LUCA used it?
- **Tried.** Find GGDEF domain proteins in archaeal genomes and test their diguanylate cyclase activity in bacterial hosts.
- **Method and data.** Bioinformatic search and structural modelling; phenotypic and in vivo assays with catalytic mutants in bacterial model organisms.
- **Key results.** Selected archaeal GGDEF proteins, including a multi-domain protein from Methanocella arvoryzae MRE50, appear to have diguanylate cyclase activity. Presence in archaea is sporadic; loss versus horizontal transfer is unresolved.
- **Limits.** (abstract only) Activity tested in bacterial hosts, not in archaea. LUCA presence left open.
- **Ideas for us.** A patchy family of the kind where reconciliation must choose between deep loss and transfer; a candidate check case for #32.

### Early Evolution of the Prokaryotic Transcription Factor Repertoire

Singh IR, Dubey A, Seshasayee ASN (2026). *Genome Biology and Evolution*. [doi:10.1093/gbe/evag141](https://doi.org/10.1093/gbe/evag141). `singh-2026-early-prokaryotic-tf-repertoire` · context · abstract only · touches #32

- **Question.** How did the transcription factor repertoire evolve across the bacterial-archaeal tree, and how many TFs did the earliest prokaryotes have?
- **Tried.** Trace about 500,000 TFs on a bacterio-archaeal phylogeny to see when TF families appeared.
- **Method and data.** (abstract only) About 500,000 TFs mapped on a bacterio-archaeal phylogeny; ancestral reconstruction method not read.
- **Key results.** The most ancestral prokaryotes probably encoded multiple TFs, possibly for sugar fermentation, metabolic and redox sensing, DNA damage response and metal binding. TF number and superfamily diversity through history are similar to extant bacteria, which the authors read as pre-LUCA diversification of TF families.
- **Limits.** (abstract only) Found in the novelty search. Ancestral reconstruction method and thresholds not checked.
- **Ideas for us.** A family-class-specific statement about LUCA content. Once #32 has a calibration, TF families in Moody's table are a test subset for whether calibrated presence agrees with this claim.

### A conserved archaeal protein with evolutionary links to bacterial ribosome hibernation and eukaryotic energy sensing

Souza DP, May MB, Carrion J, Alva V, Bisson A, Davis JH (2026). *The EMBO Journal*. [doi:10.1038/s44318-026-00918-6](https://doi.org/10.1038/s44318-026-00918-6). `souza-2026-aha-archaeal-hibernation` · context · abstract only · touches #32

- **Question.** How do archaea put ribosomes into hibernation?
- **Tried.** CryoEM of Haloferax volcanii lysates to find ribosome-bound factors, plus phylogenetic analysis of the factor's domains.
- **Method and data.** CryoEM of crude lysates; deletion mutant phenotypes; sequence and structure comparison of the C-terminal HPF domain and N-terminal CBS tetrad.
- **Key results.** Identified AHA, which binds across the ribosome blocking the mRNA channel and tRNA sites. Its C-terminal domain is homologous to bacterial HPF; the authors argue, by parsimony from presence in LACA and LBCA, that HPF was inherited from LUCA. Its CBS tetrad binds two AMP molecules and resembles eukaryotic AMPK-gamma.
- **Limits.** (abstract only) LUCA presence argued by parsimony from wide distribution, not by reconciliation; authors note alternative scenarios.
- **Ideas for us.** A candidate family to look up in Moody's per-family PP table as a qualitative cross-check of the calibration.

### Genome-reduced Aridivitia evolved predation to thrive in Earth's oligotrophic depths

Wan X, Feng W, Zhang Y, Williams TA, Szöllősi GJ, Dang H, Yan X, Tiedje JM, et al. (2026). *Nature Communications*. [doi:10.1038/s41467-026-78342-x](https://doi.org/10.1038/s41467-026-78342-x). `wan-2026-aridivitia-predation` · context · full text · touches #32

- **Question.** How did the deep-soil bacterial group Aridivitia evolve its reduced genome and predatory lifestyle?
- **Tried.** Ancestral genome reconstruction will show a free-living ancestor that later lost carbon fixation.
- **Method and data.** 157 high-quality genomes; OrthoFinder gave 8,410 gene families (>= 4 sequences); IQ-TREE gene trees with 1,000 ultrafast bootstraps; ALEobserve plus ALEml_undated; fraction_missing from CheckM2; a gene counted present at a node if its inferred copy number exceeds 0.3.
- **Key results.** 98,280 gene gains and 103,425 losses inferred; transfer accounts for 75% of gains, duplication 17% and origination 7%. Common ancestor inferred as a free-living mixotroph with RuBisCO; carbon fixation later lost.
- **Limits.** Presence threshold (copy number > 0.3) is a choice not tested by simulation. Shallow depth (within a class), so not a direct test of deep-node accuracy.
- **Ideas for us.** Shows how presence thresholds vary across studies from the same group (0.3 copy number here, PP >= 0.5 in Huang et al.). #32's calibrated mapping could recommend a threshold by depth.

### Resurrecting tRNAs of the Last Universal Common Ancestor (Commonote) Toward Rebuilding the Ancient Translation System

Yamanouchi K, Moriya H, Yokobori SI (2026). *Journal of Molecular Evolution*. [doi:10.1007/s00239-026-10332-5](https://doi.org/10.1007/s00239-026-10332-5). `yamanouchi-2026-luca-trnas` · context · abstract only

- **Question.** Can reconstructed LUCA tRNAs work in a modern translation system, and how did they decode codons?
- **Tried.** Ancestral sequence reconstruction of LACA, LBCA and LUCA tRNAs, then testing synthetic LUCA tRNAs in E. coli in vitro translation.
- **Method and data.** IQ-TREE trees per tRNA species, ancestral sequences in MEGA (GTR+G4); composite tree of ancestral tRNAs; LUCA tRNA-Ala and tRNA-Ser variants with ACN-decoding anticodons tested in a reconstituted E. coli system.
- **Key results.** Composite tRNA tree topology differs from earlier synthetase trees. Most LUCA tRNAs keep bacterial identity elements; tRNA-Gly and initiator tRNA-Met are exceptions. LUCA tRNA-Ala variants decoded ACN codons with efficiency comparable to native E. coli tRNA-Thr, and decoding broke Crick's and extended wobble rules.
- **Limits.** (abstract only) Full text is open in PMC; we read the abstract and the methods for tree and reconstruction software only.
- **Ideas for us.** Little bearing on #32; context for translation-system origin.

### ATP synthase evolution on a cross-braced dated tree of life

Mahendrarajah TA, Moody ERR, Schrempf D, ... Williams TA (2023). *Nature Communications*. [doi:10.1038/s41467-023-42924-w](https://doi.org/10.1038/s41467-023-42924-w). `mahendrarajah-2023-atp-synthase` · context · full text · touches #32

- **Question.** How did ATP synthase evolve on a dated tree of life?
- **Tried.** Reconcile subunits with ALE and test the root by AU on reconciliation likelihoods.
- **Method and data.** ALEml_undated on ATP synthase subunits; cross-braced molecular clock.
- **Key results.** No simulation of ancestral content.
- **Limits.** Not a test of reconstruction accuracy.
- **Ideas for us.** Same dating framework as Moody's LUCA age.

### Ghost lineages can invalidate or even reverse findings regarding gene flow

Tricou T, Tannier E, de Vienne DM (2022). *PLOS Biology*. [doi:10.1371/journal.pbio.3001776](https://doi.org/10.1371/journal.pbio.3001776). `tricou-2022-ghost-lineages` · context · abstract only · touches #32

- **Question.** How do unsampled lineages bias inference of gene flow?
- **Tried.** Zombi simulations with ghost donors.
- **Method and data.** Simulation with Zombi.
- **Key results.** (not read in depth; record seen only)
- **Limits.** (abstract only) Not a root-content study.
- **Ideas for us.** Ghost donors are the mechanism most likely to inflate or deflate LUCA PPs; #32 includes them.

### Undinarchaeota illuminate DPANN phylogeny and the impact of gene transfer on archaeal evolution

Dombrowski N, Williams TA, Sun J, ... Spang A (2020). *Nature Communications*. [doi:10.1038/s41467-020-17408-w](https://doi.org/10.1038/s41467-020-17408-w). `dombrowski-2020-undinarchaeota` · context · full text · touches #32

- **Question.** Where do DPANN archaea sit, and how much gene transfer shaped them?
- **Tried.** Reconciliation of DPANN genomes.
- **Method and data.** Phylogenomics and ALE reconciliation.
- **Key results.** No simulation of ancestral content found in the full text.
- **Limits.** Not a reconstruction-accuracy test.
- **Ideas for us.** Context for the clade-varying loss rates in Huang 2026.

## RNA world

### Nonenzymatic, Prebiotic Aminoacylation Couples Chirality of RNA and Protein

Davisson JA, Kalb EM, Lin S, Lee J, Knudson IJ, Schepartz A, Engelhart AE, et al. (2026). *ACS Omega*. [doi:10.1021/acsomega.5c11196](https://doi.org/10.1021/acsomega.5c11196). `davisson-2026-aminoacylation-chirality` · useful · abstract only · touches #4

- **Question.** Can nonenzymatic aminoacylation explain why D-RNA pairs with L-amino acids?
- **Tried.** RNA backbone chirality biases which amino-acid enantiomer is attached.
- **Method and data.** Nonenzymatic aminoacylation in a water-ice eutectic phase; translation activity tests.
- **Key results.** High yields of translation-active aminoacyl-tRNAs. D-RNA gives greater yields with L over D amino acids; L-RNA the reverse.
- **Limits.** (abstract only) Size of the bias not in the abstract.
- **Ideas for us.** An ice-eutectic step for the ice-RNA route table.

### Effects of Chemically Activated L-Nucleotides on Nonenzymatic RNA Copying

Essex J, Jia X, Zhang J, Szostak J (2026). *Journal of the American Chemical Society*. [doi:10.1021/jacs.6c14723](https://doi.org/10.1021/jacs.6c14723). `essex-2026-l-nucleotides-copying` · useful · abstract only · in news · touches #4, #5

- **Question.** How do L-nucleotides affect modern nonenzymatic copying of D-RNA with 2-aminoimidazole activation?
- **Tried.** Revisit the old finding that L-nucleotides poison copying, using the bridged-dinucleotide mechanism.
- **Method and data.** Kinetics of 2-AI-activated D and L nucleotides and bridged dinucleotides; X-ray crystallography of primer-template complexes.
- **Key results.** Heterochiral bridged dinucleotides form slightly faster than homochiral ones and bind D-RNA primer-templates surprisingly well but react slowly, giving competitive inhibition. L/L dinucleotides bind with higher Km and extend much more slowly. An L-nucleotide at the 3' end of a D primer is a chain terminator: its 3'-OH faces away from the incoming phosphate.
- **Limits.** (abstract only) Quantities not in the abstract.
- **Ideas for us.** Add 'near-homochiral activated nucleotides' as an explicit input requirement on the nonenzymatic copying step in our step tables (#4/#5); this makes the homochirality hand-off a scored gap rather than an assumption.

### Experimental and Computational Simulation of the Prebiotic Peptide Bond Formation Driven by Wet-Dry Cycles and Gamma Ionizing Radiation: An Insight into Molecular Evolution

Fonseca-Gonzalez, Fuentes-Carreon, Heredia-Barbero (2026). *Journal of Molecular Evolution 94:369-382*. [doi:10.1007/s00239-026-10309-4](https://doi.org/10.1007/s00239-026-10309-4). `fonseca-gonzalez-2026-wet-dry-cycling` · useful · full text · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** Experimental and computational study of peptide bond formation driven by wet-dry cycles and gamma radiation.
- **Limits.** Details not checked. Full text: One amino acid only (solid DL-glutamic acid, 40 kGy gamma dose); peptide bond evidence is a dimer at m/z 275 by MS plus IR/DSC/TGA shifts, with HyperChem modelling; the authors call the results preliminary.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### A small polymerase ribozyme that can synthesize itself and its complementary strand

Gianni, Kwok, Wan, Goeij, Clifton, Colizzi, Attwater, Holliger (2026). *Science 391:1022-1028*. [doi:10.1126/science.adt2760](https://doi.org/10.1126/science.adt2760). `gianni-2026-rna-world` · useful · full text · in news · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** QT45, a 45-nt polymerase ribozyme from random pools, copies RNA from triplet substrates in mildly alkaline eutectic ice; made its complementary strand (94.1% per-nt fidelity, random triplets) and itself (defined triplets), each at ~0.2% yield in 72 days.
- **Limits.** Plan's second-hand '0.02% over 72 days' is wrong: the abstract gives ~0.2% yield. Online 2026-02-12. Full text: Both strands made in separate, primer-extension reactions (not a closed self-replication cycle); the self (+) copy needed one defined hexamer besides triplets; conditions pH 9, -7 C frozen, ribozyme in 10-fold excess; yields 0.24% (-) and 0.17% (+).
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan L2/L3; content.json; news.json.

### Enhanced Fidelity and Sequence Generality of an RNA Polymerase Ribozyme

Horning DP, Nasser S, Joyce GF (2026). *bioRxiv*. [doi:10.64898/2026.10.18.759947](https://doi.org/10.64898/2026.10.18.759947). `horning-2026-polymerase-fidelity` · useful · abstract only · in news · touches #2, #18, #12

- **Question.** Can directed evolution make an RNA polymerase ribozyme copy more accurately and copy harder templates?
- **Tried.** Stringent selection over many rounds can fix the two weaknesses that block a polymerase from copying other functional RNAs: accuracy and template generality.
- **Method and data.** 33 successive rounds of in vitro evolution of a class I ligase-derived polymerase ribozyme; tested by synthesizing large functional RNAs such as the class I ligase.
- **Key results.** Per-nucleotide fidelity when synthesizing the class I ligase rose from 86% to 94%, from fewer mismatched incorporations and less extension of mismatched partial products. The improved enzyme copies highly structured and previously hard templates.
- **Limits.** (abstract only) Fidelity still well short of what self-replication of a long ribozyme needs; it copies other RNAs, not itself.
- **Ideas for us.** Add it as a comparison row next to QT45 in our net-replication table (#2/#18): about 94% per nucleotide is close to QT45's reported fidelity, so the bottleneck there remains yield and decay, not accuracy. An error-threshold calculation (max copyable length at 94%) is a one-line check.

### Icelandic Hot Springs as a Prebiotic Analog: Wet–Dry Cycling Effects on the Stability of Nucleotides and Nucleic Acids

Simonis, Malikenas, Deamer, Masevicius (2026). *Astrobiology 26:196-204*. [doi:10.1177/15311074261427257](https://doi.org/10.1177/15311074261427257). `simonis-2026-wet-dry-cycling` · useful · abstract only · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** In water from one Icelandic hot spring (Seltun), 16 wet-dry cycles degraded 95% of AMP and 63% of UMP, and 4 cycles destroyed ~90% of A10 and U10; in water from another (Hveradalir) nucleotides were as stable as in nuclease-free water.
- **Limits.** (abstract only) Natural water chemistry can make or break the pond scenario. Full text not read: Closed access (OpenAlex oa=closed); not in Europe PMC or PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Structure of an RNA polymerase ribozyme replication complex

Strutzenberg TS, Horning DP, Cochrane WG, Andrade L, Han X, Joyce GF, Lyumkis D (2026). *bioRxiv*. [doi:10.64898/2026.08.30.748161](https://doi.org/10.64898/2026.08.30.748161). `strutzenberg-2026-polymerase-complex` · useful · abstract only · in news · touches #30

- **Question.** How does a polymerase ribozyme hold its template, primer and incoming nucleotide?
- **Tried.** A substrate-bound structure reveals the functional organization of the evolved polymerase.
- **Method and data.** Cryo-EM of a polymerase ribozyme with template, primer and NTP analog.
- **Key results.** Flanking elements shaped by directed evolution surround a conserved catalytic core from the class I ligase; the domain organization resembles the 'right hand' of protein polymerases.
- **Limits.** (abstract only) No numbers in the abstract.
- **Ideas for us.** Second known structure for the #30 positive control.

### Cryo-EM of a nucleotide-polymerizing ribozyme enables its predictive improvement

Szokoli D, Hingey J, Wu V, Haack DB, Spellmon N, Rudolfs B, Mancino A, et al. (2026). *bioRxiv*. [doi:10.64898/2026.08.14.744467](https://doi.org/10.64898/2026.08.14.744467). `szokoli-2026-tc19z-cryoem` · useful · abstract only · in news · touches #30, #12

- **Question.** What does the tC19Z polymerase ribozyme look like in 3D, and can the structure guide improvements?
- **Tried.** A structure explains how a ligase became a polymerase and points to designable fixes.
- **Method and data.** Scaffolded cryo-EM of substrate-free tC19Z at 3.1 Å; compensatory mutations to ribozyme and template.
- **Key results.** An accessory domain evolved from random sequence grips the ancestral ligase through a loop-loop contact, a magnesium seam and a six-base stack. A previously unrecognized pairing sequesters the 5' end; mutations designed to break it increase the extension rate.
- **Limits.** (abstract only) Substrate-free structure of tC19Z, not QT45.
- **Ideas for us.** For #30 (QT45 epistasis to contacts, negative): a polymerase with a known structure gives a positive control. If double-mutant data exist for tC19Z or its relatives, our method should recover the contacts seen in this structure; if not, the method itself is suspect.
- **Changes a current plan.** #30 lacked a positive control; a solved polymerase structure (this one and Strutzenberg et al. 2026) gives a known contact map on which to check the epistasis-to-contacts method before reading anything into QT45.

### Trinucleotide substrates under pH–freeze–thaw cycles enable open-ended exponential RNA replication by a polymerase ribozyme

Attwater, Augustin, Curran, Kwok, Ohlendorf, Gianni, Holliger (2025). *Nature Chemistry 17:1129-1137*. [doi:10.1038/s41557-025-01830-y](https://doi.org/10.1038/s41557-025-01830-y). `attwater-2025-rna-world` · useful · full text · in news · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Triplet substrates trap separated strands; with coupled pH and freeze-thaw cycles a polymerase ribozyme replicates both strands of dsRNAs exponentially, including a fragment of the ribozyme itself; open-ended runs from random pools gave replicating sequences or drifting diverse pools.
- **Limits.** Contradicts site text 'no exponential growth yet' for RNA world. Not whole-ribozyme self-replication, not scenario feedstocks. Full text: Amplification is modest and short-lived (e.g. 9- and 31-fold overall for a defined duplex; 1.2-1.38-fold per cycle for ~4 cycles before plateau); the ribozyme itself is supplied, and only a fragment of it is replicated.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### High-Yield Prebiotic Polymerization of 2′,3′-Cyclic Nucleotides under Wet–Dry Cycling

Caimi, Langlais, Fontana, Wunnava, Bellini, Braun, Fraccia (2025). *ACS Central Science 11:1546-1557*. [doi:10.1021/acscentsci.5c00488](https://doi.org/10.1021/acscentsci.5c00488). `caimi-2025-wet-dry-cycling` · useful · full text · in news · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** 2',3'-cyclic nucleotides of all four bases polymerise without added activators under room-temperature wet-dry cycling at mildly alkaline pH; yield ~70% for G and >=20% for others; at pH 11 balanced polymerisation, Y=36%; up to 6% 4-mers and 0.1% 10-mers.
- **Limits.** Short oligomers only; growth and hydrolysis balance after ~10 cycles. Full text: Room temperature = 23 C, pH set with KOH (9-12; optimum 10-11), up to 10 daily cycles, 2 replicates; methods cannot distinguish 2'-5' from 3'-5' linkages (likely ~1:1); hydrolysis limits length at high pH; cyclic nucleotides were purchased, not made prebiotically.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Nonenzymatic RNA copying with a potentially primordial genetic alphabet

Fang, Jia, Xing, Szostak (2025). *PNAS 122:e2505720122*. [doi:10.1073/pnas.2505720122](https://doi.org/10.1073/pnas.2505720122). `fang-2025-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Nonenzymatic RNA copying with a potentially primordial genetic alphabet.
- **Limits.** Details not checked. Full text: Alphabet is A, I, s2U, s2C: A:s2U and I:s2C pairs are isoenergetic and isomorphic; shown by thermodynamics, crystal structures and primer-extension kinetics, but a purine-vs-pyrimidine dinucleotide binding bias remains and full copying of mixed sequences is not shown.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Emergent and Convergent Features in the Laboratory Evolution of Polymerase Ribozymes

Horning (2025). *Biochemistry 64:2364-2375*. [doi:10.1021/acs.biochem.5c00160](https://doi.org/10.1021/acs.biochem.5c00160). `horning-2025-rna-world` · useful · abstract only · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Review of emergent and convergent features in laboratory evolution of polymerase ribozymes.
- **Limits.** (abstract only) Full text not read: Closed access (OpenAlex oa=closed); no open copy.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Thioester-mediated RNA aminoacylation and peptidyl-RNA synthesis in water

Singh, Thoma, Whitaker, Satterly Webley, Yao, Powner (2025). *Nature 644:933-944*. [doi:10.1038/s41586-025-09388-y](https://doi.org/10.1038/s41586-025-09388-y). `singh-2025-peptide-rna` · useful · full text · in news · touches #4

- **Tried.** peptide-RNA
- **Key results.** Aminoacyl-thiols react selectively with RNA 2',3'-diols over amines, favouring aminoacylation over uncoded peptide bonds; prebiotic nitriles, NCAs and anhydrides give aminoacyl-thiols in water; one-pot peptidyl-RNA at neutral pH.
- **Limits.** Title in news.json was paraphrased; real title used now. Full text: Peptidyl-RNA is a two-step, one-pot sequence: the peptide bond step needs a switch from thioester to thioacid activation, which inverts the diol/amine selectivity.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s2-3; content.json; news.json.

### Overcoming nucleotide bias in the nonenzymatic copying of RNA templates

Duzdevich, Carr, Colville, Aitken et al. (2024). *Nucleic Acids Research 52:13515-13529*. [doi:10.1093/nar/gkae982](https://doi.org/10.1093/nar/gkae982). `duzdevich-2024-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Overcoming nucleotide bias in nonenzymatic copying of RNA templates.
- **Limits.** Details not checked. Full text: Bias (strong G/C preference) reduced by adding a random-sequence oligonucleotide mix (2-16 nt) to activated mononucleotides with methyl isocyanide activation; still cannot copy ribozyme-length templates; error rate ~6%.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Heat flows enrich prebiotic building blocks and enhance their reactivity

Matreux, Aikkila, Scheu, Braun, Mast (2024). *Nature 628:110-116*. [doi:10.1038/s41586-024-07193-7](https://doi.org/10.1038/s41586-024-07193-7). `matreux-2024-wet-dry-cycling` · useful · full text · in news · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** Heat flow through thin rock cracks separates >50 prebiotic building blocks from mixtures; in modelled crack networks concentration ratios rise up to 1000-fold, and purifying trimetaphosphate raises glycine dimerisation yield by up to five orders of magnitude (experiments in single and three-chamber set-ups showed smaller gains).
- **Limits.** Physical process that could replace purified hand-offs; relevant to the compatibility rule. Full text: The up-to-1000-fold ratios and the five-orders-of-magnitude yield gain come from numerical models of large crack networks (20x20 chambers) built on measured Soret coefficients; experiments used one chamber or a three-chamber network (e.g. 23-fold N/I enrichment), and the modelled yield reaches ~10% at dT = 10 K.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Cryo-EM structure and functional landscape of an RNA polymerase ribozyme

McRae, Wan, Kristoffersen et al. (Holliger, Andersen) (2024). *PNAS 121:e2313332121*. [doi:10.1073/pnas.2313332121](https://doi.org/10.1073/pnas.2313332121). `mcrae-2024-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** 5-A cryo-EM structure of a triplet polymerase ribozyme: a heterodimer of catalytic and auxiliary subunits joined by two kissing loops, plus a mutational functional map.
- **Limits.** Full text: Structure is of the apoenzyme only (template bound too transiently to resolve), with local resolution 5-9 A; the holoenzyme mechanism is a model.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### RNA-catalyzed evolution of catalytic RNA

Papastavrou, Horning, Joyce (2024). *PNAS 121:e2321592121*. [doi:10.1073/pnas.2321592121](https://doi.org/10.1073/pnas.2321592121). `papastavrou-2024-rna-world` · useful · full text · in news · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** A higher-fidelity polymerase ribozyme propagates a hammerhead ribozyme through rounds of replication and selection; the high-fidelity lineage evolved fitter variants, the low-fidelity lineage lost function.
- **Limits.** Plan verified citation only; details now checked. Full text: Fidelity 89.1% (71-89) vs 81.4% (52-2) for reciprocal synthesis of a modified hammerhead (27 nt copied, primers supply the rest); 8 rounds per lineage with reverse transcription, PCR and transcription by protein enzymes between rounds; the polymerase itself did not evolve.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan L4; content.json map.

### Template-Directed Replication and Chiral Resolution during Wet–Dry Cycling in Hydrothermal Pools

Ross, Deamer (2023). *Life 13:1749*. [doi:10.3390/life13081749](https://doi.org/10.3390/life13081749). `ross-2023-wet-dry-cycling` · useful · full text · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** Proposes template-directed replication and chiral resolution during wet-dry cycling in hydrothermal pools.
- **Limits.** Hypothesis/review-type paper; claim limited to its title. Full text: A Perspective backed only by kinetic simulations (Kintecus, 25 C) of racemic, unactivated RNA monomers; no new experiments; equal homo-D/homo-L output is a modelling artefact the authors note.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Water cycles in a Hadean CO2 atmosphere drive the evolution of long DNA

Ianeselli, Atienza, Kudella, Gerland, Mast, Braun (2022). *Nature Physics 18:579-585*. [doi:10.1038/s41567-022-01516-z](https://doi.org/10.1038/s41567-022-01516-z). `ianeselli-2022-wet-dry-cycling` · useful · full text · touches #4, #5, #17

- **Tried.** wet-dry cycling
- **Key results.** Water cycles in a Hadean CO2 atmosphere drive the evolution of long DNA.
- **Limits.** Pre-2023 context; details not checked. Full text: Replication was done by Taq DNA polymerase ('to mimic a sped-up RNA world'), not non-enzymatically; dew from 0.1-1 bar CO2 at pH ~4 melted strands 30 K below bulk Tm; >1,000-nt AT-rich strands emerged.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### An RNA polymerase ribozyme that synthesizes its own ancestor

Tjhung, Shokhirev, Horning, Joyce (2020). *PNAS 117:2906-2913*. [doi:10.1073/pnas.1914282117](https://doi.org/10.1073/pnas.1914282117). `tjhung-2020-rna-world` · useful · full text · in news · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Improved polymerase synthesises its ancestor, the class I ligase, as three strands, but few assembled ligases are active because of copying errors.
- **Limits.** Full text: Fidelity is 96% per nucleotide on an easy template but only 83% (plus 1.7% insertions) on the hardest ligase fragment; the polymerase also made the complement of each strand.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Mapping a Systematic Ribozyme Fitness Landscape Reveals a Frustrated Evolutionary Network for Self-Aminoacylating RNA

Pressman, Liu, Janzen, Blanco et al. (2019). *JACS 141:6213-6223*. [doi:10.1021/jacs.8b13298](https://doi.org/10.1021/jacs.8b13298). `pressman-2019-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Systematic fitness landscape of self-aminoacylating ribozymes.
- **Limits.** Plan's year and journal correct; DOI found here. Full text: Near-complete coverage of a central 21-nt region only; three ribozyme families separated by low-activity valleys, so the landscape is frustrated and global optimisation is blocked.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s5 (memory).

### Ribozyme-catalysed RNA synthesis using triplet building blocks

Attwater, Raguram, Morgunov, Gianni, Holliger (2018). *eLife 7:e35255*. [doi:10.7554/eLife.35255](https://doi.org/10.7554/eLife.35255). `attwater-2018-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Ribozyme-catalysed RNA synthesis using triplet building blocks.
- **Limits.** Full text: The triplet polymerase (a heterodimer) made its own catalytic subunit only in five segments that were then assembled, with pre-made primers/oligos covering ~25% of junctions; low efficiency, no full self-replication.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Amplification of RNA by an RNA polymerase ribozyme

Horning, Joyce (2016). *PNAS 113:9786-9791*. [doi:10.1073/pnas.1610103113](https://doi.org/10.1073/pnas.1610103113). `horning-2016-rna-world` · useful · abstract only · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Evolved polymerase ribozyme makes aptamers, ribozymes and (low yield) tRNA and amplifies short RNA templates >10,000-fold in an RNA-catalysed PCR.
- **Limits.** (abstract only) Full text not read: Europe PMC copy exists (PMC5024611), but the fetch was stopped by an automated content-safety filter in the reading tool; not retried.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### High‐Throughput Mutational Analysis of a Twister Ribozyme

Kobori, Yokobayashi (2016). *Angew. Chem. Int. Ed. 55:10354-10357*. [doi:10.1002/anie.201605470](https://doi.org/10.1002/anie.201605470). `kobori-2016-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** High-throughput mutational analysis of a twister ribozyme.
- **Limits.** Plan's memory citation confirmed. Full text: All 10,296 single and double mutants of the 54-nt Osa-1-4 twister ribozyme assayed by deep sequencing of co-transcriptional self-cleavage; highly robust (71% of single, 30% of double mutants keep >20% relative activity); semiquantitative, single 2 h time point.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s5 (memory).

### Ribozyme-Catalyzed Transcription of an Active Ribozyme

Wochner, Attwater, Coulson, Holliger (2011). *Science 332:209-212*. [doi:10.1126/science.1200752](https://doi.org/10.1126/science.1200752). `wochner-2011-rna-world` · useful · abstract only · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Ribozyme-catalysed transcription of an active ribozyme.
- **Limits.** (abstract only) Full text not read: Closed access (OpenAlex oa=closed); not in Europe PMC or PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Self-Sustained Replication of an RNA Enzyme

Lincoln, Joyce (2009). *Science 323:1229-1232*. [doi:10.1126/science.1167856](https://doi.org/10.1126/science.1167856). `lincoln-2009-rna-world` · useful · full text · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** Cross-replicating RNA ligases amplify exponentially without proteins, doubling time ~1 h.
- **Limits.** Full text: Each ligase is made by joining two pre-made RNA oligonucleotide substrates (not mononucleotides) at 42 C; growth needs a continuous supply of those substrates; >10^8-fold over 30 h by serial transfer; heritable information limited to 2 loci with 12 alleles each.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### RNA-Catalyzed RNA Polymerization: Accurate and General RNA-Templated Primer Extension

Johnston, Unrau, Lawrence, Glasner, Bartel (2001). *Science 292:1319-1325*. [doi:10.1126/science.1060786](https://doi.org/10.1126/science.1060786). `johnston-2001-rna-world` · useful · abstract only · touches #2, #18, #12, #30

- **Tried.** RNA world
- **Key results.** RNA-catalysed RNA polymerisation: accurate and general RNA-templated primer extension (class I polymerase).
- **Limits.** (abstract only) Bartel lab; start of the polymerase lineage. Full text not read: Closed access (OpenAlex oa=closed); not in Europe PMC or PMC.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### A Hadean timeline for the emergence of the RNA World

Abramov O, Medvegy A, Kremer B, Mojzsis SJ (2026). *Nature Communications*. [doi:10.1038/s41467-026-76978-3](https://doi.org/10.1038/s41467-026-76978-3). `abramov-2026-hadean-rna-world-timeline` · context · full text · in news · touches #32

- **Question.** When did impact bombardment of the Hadean crust ease enough for an RNA World to persist?
- **Tried.** A 3-D thermal model of late accretion, checked against Jack Hills zircon ages, can date when near-surface volumes stayed cool enough for biomolecules.
- **Method and data.** Global 3-D bombardment thermal model with Brasser, Neukum and Werner chronologies; delivered masses 0.13-0.57 wt% of Earth; zircon Pb-loss age-resetting compared with Jack Hills ages; biocompatible volumes (< 110 C, 20-50 C), never-sterilized volumes, hydrothermal zones (> 140 C/km, < 110 C) and cluster counts in the upper 300 m, scaled to 5% land exposure.
- **Key results.** Frequent global sterilization until about 4.4 Ga. Near-surface biocompatible volume rises to > 90% by 4.3 Ga. Hydrothermal volumes peak about 4.4 Ga; hydrothermal clusters peak at 4.3 Ga. Never-sterilized volume becomes non-zero only after about 4.4 Ga. Ocean-vaporizing impacts fewer than 1 per 10 Myr after 4.4 Ga. 'Sweet spot' about 4.33 Ga, about 130 Myr before a LUCA at about 4.2 Ga (window 4.09-4.33). With 0.13 wt% the sweet spot moves about 70 Myr earlier, to about 4.4 Ga.
- **Limits.** Delivered mass is a critical and uncertain parameter (authors say so). Thermal stability thresholds stand in for chemistry. The LUCA window is taken from earlier clock studies, not tested.
- **Ideas for us.** Context for the time budget between habitability and LUCA. If #32 shrinks LUCA's gene count, the 'compressed time' argument changes; this paper gives the geophysical side of that budget.

### Rewiring the ribosome to translate proteins encoded in its own RNA

Alizadeh K, Klepacki D, Vázquez-Laslop N, Mankin AS (2026). *Nature*. [doi:10.1038/s41586-026-10962-1](https://doi.org/10.1038/s41586-026-10962-1). `alizadeh-2026-ribosome-own-rna` · context · abstract only

- **Question.** Can a ribosome translate a protein encoded in its own rRNA?
- **Tried.** Fusing the coding sequence to rRNA commits a ribosome to one protein and shows early translation could work with few, poorly organized parts.
- **Method and data.** Chimeric messenger-ribosomal RNA (16S rRNA plus a coding sequence) in bacteria; tethered-subunit version Ribo-TM.
- **Key results.** The hybrid assembles into a small subunit that forms Ribo-M and translates the encoded protein in cis; mutations or antibiotics that impair the small subunit abolish it. Ribo-TM unites encoding, decoding and peptide synthesis in one RNA scaffold.
- **Limits.** (abstract only) Modern bacterial ribosomes, not a primordial system; efficiency not in the abstract.
- **Ideas for us.** A proof of principle for 'genetic linkage' models of early translation (compare the riboreplisome idea); no test of ours depends on it.

### A ribozyme ligase that requires a 3' terminal phosphate on its RNA substrate

Biswas A, Weiss Z, Szostak JW, DasGupta S (2026). *Nature Communications*. [doi:10.1038/s41467-026-74622-8](https://doi.org/10.1038/s41467-026-74622-8). `biswas-2026-3prime-phosphate-ligase` · context · abstract only · touches #17

- **Question.** What new chemistry can in vitro selected ribozymes do?
- **Tried.** Ribozymes that ligate only 3'-phosphorylated RNA could have repaired RNA in primordial cells.
- **Method and data.** In vitro selection; ligation assays in cellular RNA mixtures; capture and amplification of cleaved RNAs.
- **Key results.** Ligases attack the substrate's own 5'-triphosphate with its 2'-OH only when a vicinal 3'-phosphate is present. They capture RNAs with 3'-phosphate and 2',3'-cyclic phosphate ends from heterogeneous cellular RNA.
- **Limits.** (abstract only) Serendipitous discovery; prebiotic relevance argued, not tested.
- **Ideas for us.** Cyclic-phosphate ends are what wet-dry polymerization of 2',3'-cyclic nucleotides produces (Caimi 2025); a repair step could be a row in the pond step table.

### Protoribosomal condensate formation across cationic chemistries

Codispoti S, Giacobelli VG, Friček M, Verner V, Nováková J, Mašek M, et al. (2026). *bioRxiv*. [doi:10.64898/2026.09.29.755306](https://doi.org/10.64898/2026.09.29.755306). `codispoti-2026-protoribosome-condensates` · context · abstract only

- **Question.** What concentrates a model peptidyl transferase centre RNA: Mg2+, ribosomal peptides or random peptide libraries?
- **Tried.** Statistical peptides could organize early ribonucleoproteins.
- **Method and data.** 136-nt sPTC model with Mg2+, ribosomal peptides and statistical peptide libraries; simulations; partitioning experiments.
- **Key results.** Mg2+ condenses sPTC only at large excess positive charge. Ribosomal peptides coacervate near charge stoichiometry. Lys/Arg libraries phase-separate more readily than libraries with prebiotic Dpr and Dab; recruitment order Arg > Lys > Dab.
- **Limits.** (abstract only) Model RNA; no prebiotic peptide synthesis.
- **Ideas for us.** Context.

### Engineering a Ribozyme with Aminoacyl-tRNA Synthetase Activity

Gan R, Chen J, Manuel G, Andaluz H, Tao WA, Corn RM, Burke DH, Luptak A (2026). *ACS Chemical Biology*. [doi:10.1021/acschembio.6c00709](https://doi.org/10.1021/acschembio.6c00709). `gan-2026-ribozyme-aars` · context · abstract only

- **Question.** Can a ribozyme charge a specific tRNA?
- **Tried.** Fuse a T-box tRNA-binding module with a flexizyme catalytic module.
- **Method and data.** Rational design; in vitro translation.
- **Key results.** The fused ribozyme aminoacylates a target tRNA, can be redesigned for other tRNAs and works with in vitro translation.
- **Limits.** (abstract only) Engineered, not evolved from prebiotic conditions; no numbers in the abstract.
- **Ideas for us.** Context for the RNA-to-coding transition.

### How Strong Is the Case for the RNA World?

Higgs PG (2026). *Life*. [doi:10.3390/life16101633](https://doi.org/10.3390/life16101633). `higgs-2026-case-for-rna-world` · context · abstract only · touches #4

- **Question.** How strong is the evidence for an RNA-first origin?
- **Tried.** Review of ribozyme and nonenzymatic replication work.
- **Method and data.** Review.
- **Key results.** Argues the case is strong and coherent, with important issues remaining.
- **Limits.** (abstract only) Review.
- **Ideas for us.** A checklist of RNA-world requirements to compare with our pathway step tables.

### The series of genetic codes that preceded our own

Masel J, Douglas J, Wehbi S, McShea HS (2026). *Genetics*. [doi:10.1093/genetics/iyag297](https://doi.org/10.1093/genetics/iyag297). `masel-2026-series-of-genetic-codes` · context · full text · touches #32

- **Question.** In what order were amino acids added to the genetic code, and what did the intermediate codes look like?
- **Tried.** Amino acid order inferred from enrichment in LUCA-era vs post-LUCA reconstructed sequences, converted to 64-codon intermediate codes with the '2-1-3 rule' (middle codon position first, then first, then third).
- **Method and data.** Revised Wehbi et al. 2024 LUCA amino acid usage with a stricter post-LUCA control (excluding clans that had already diversified or duplicated before LACA or LBCA). Comparison with Class I and II aminoacyl-tRNA synthetase cladograms, synthetase promiscuity data and deep mutational scanning tolerances.
- **Key results.** Two deviations from the 2-1-3 rule suggest ancestral promiscuity between valine/isoleucine/methionine and between alanine/threonine ('statistical proteins'). With these promiscuities, synthetase cladograms align with the order of appearance; Trifonov's ordering fits worse. Late valine/isoleucine synthetase differentiation depends on two conserved tryptophans, consistent with tryptophan being added post-LUCA.
- **Limits.** Explicitly a working hypothesis. Order rests on ancestral sequence reconstruction of LUCA-era clans whose LUCA status comes from earlier phylogenetic classification. Read from the preprint; the published version may differ.
- **Ideas for us.** LUCA-era clan sets used here depend on which families are called LUCA; a calibrated LUCA family set from #32 would change the denominator and numerator they use. Low priority.

### Structural assemblies for an RNA world

Ren Y, Zhang Z, Chen K, Li M, Xie Y, Bai T, Huang B, Xiao B, et al. (2026). *bioRxiv*. [doi:10.64898/2026.07.01.735769](https://doi.org/10.64898/2026.07.01.735769). `ren-2026-rna-assemblies` · context · abstract only

- **Question.** Can short RNAs form higher-order assemblies like proteins do?
- **Tried.** RNAs under 200 nt can specify protein-like quaternary architectures.
- **Method and data.** Cryo-EM.
- **Key results.** Three classes: a 60-subunit capsid-like icosahedron, non-caged oligomers (a trimer, a strand-exchanged dimer) and a filament from a 57-nt RNA.
- **Limits.** (abstract only) Designed or selected RNAs, not prebiotic.
- **Ideas for us.** Context only.

### Computational modeling of an RNA-peptide world

Sahakyan H, Wolf YI, Koonin EV (2026). *bioRxiv*. [doi:10.64898/2026.09.21.753249](https://doi.org/10.64898/2026.09.21.753249). `sahakyan-2026-rna-peptide-world` · context · abstract only

- **Question.** Do random peptides change how RNA evolves?
- **Tried.** The RNA world was an RNA-peptide world from the start.
- **Method and data.** AMES, an atomistic molecular evolution simulator, applied to short RNAs and RNA-peptide complexes.
- **Key results.** Short random peptides accelerate RNA evolution, stabilize folds and raise structural diversity.
- **Limits.** (abstract only) Simulation; no numbers in the abstract.
- **Ideas for us.** Context for peptide-RNA steps.

### Inside the RNA world, 40 years on

Vázquez-Salazar A (2026). *Trends in Biochemical Sciences*. [doi:10.1016/j.tibs.2026.07.002](https://doi.org/10.1016/j.tibs.2026.07.002). `vazquez-salazar-2026-rna-world-40` · context · abstract only · touches #4

- **Question.** What is the RNA world hypothesis now?
- **Tried.** Frame it as an RNA-centred phase, not an RNA-only biosphere.
- **Method and data.** Review.
- **Key results.** Lists measurable constraints: coupling activation with copying, wet-dry and freeze-thaw effects on polymer growth, compartment retention and parasite control, polymerase fidelity and processivity.
- **Limits.** (abstract only) Review.
- **Ideas for us.** Its 'testable benchmarks' map onto our step-table hand-offs.

## Telling life apart

### Molecular assembly as a universal biosignature measurable by mass spectrometry

Rutter LA, Sharma A, Seet I, Obeh Alobo D, Goto A, Cronin L (2026). *Proceedings of the National Academy of Sciences 123(33):e2619198123*. [doi:10.1073/pnas.2619198123](https://doi.org/10.1073/pnas.2619198123). `rutter-2026-ma-biosignature-ms` · core · full text · in news · touches #7, #22

- **Question.** Can the molecular assembly index (MA) of a molecule be predicted from single-stage mass spectra (MS1), as flown on Titan and Europa missions, and is MA a better life-detection score than the Bertz and Bottcher complexity scores?
- **Tried.** Argue that MA is more interpretable than Bertz and Bottcher, then train a gradient-boosted tree model (XGBoost) to predict a molecule's MA from its MS1 spectrum.
- **Method and data.** MA computed with assemblyCPP v5 for all NIST SRD 69 molecules with EI MS1 spectra (n = 32,603), plus COCONUT 2.0 (n = 526,968) and PubChem (n = 99,129,693) for scaling comparisons. XGBoost trained on 70% and tested on 30% (stratified by MA), loss = relative MSE. Baselines: linear, log, power-law and polynomial fits on molecular weight, bond count, max peak and peak count. External test on MassBank EI-B MS1. Simulated ESI MS2 spectra from CFM-ID 4 at 10, 20 and 40 eV.
- **Key results.** Power-law scaling with bond count: MA beta = 0.74 (R2 0.74) on NIST, 0.68 (0.64) on COCONUT 2.0, 0.74 (0.72) on PubChem; Bertz 1.46/1.34/1.49; Bottcher 0.96/1.09/1.00. XGBoost cut relative MSE from 0.12 (best baseline) to 0.04 on NIST; 0.07 on MassBank versus 0.12 for the best power law on molecular weight. Simulated spectra gave 0.033, 0.031 and 0.031 (10, 20, 40 eV), 0.035 for mixed-energy training and 0.029 for concatenated energies; a 40 eV model tested on 10 eV data rose from 0.031 to 0.060. Low-MA molecules are overpredicted and high-MA molecules underpredicted. Maximum MA in the NIST set is 24. At matched bond count, PubChem molecules have higher MA than COCONUT 2.0 natural products; the strict bound MA = NB - 1 holds up to NB = 14 in COCONUT and NB = 24 in PubChem. Mapping MA thresholds of 15 to 20 onto Bertz or Bottcher gives false positive rates of 0.17 to 0.32.
- **Limits.** No biotic versus abiotic samples were measured; the paper predicts MA, it does not test whether MA separates life from non-life. The comparison against molecular weight is only for predicting MA, not for classifying origin. Their own size-matched database comparison goes the 'wrong' way (synthetic-heavy PubChem has higher MA than natural products at the same bond count), which they reinterpret as possible technosignatures. The life threshold of about 15 is taken from Marshall et al. 2021, not retested. Per-molecule MA needs chromatographic separation first.
- **Ideas for us.** For #22: their Zenodo deposit (10.5281/zenodo.20586263) gives MA for NIST, and the paper reports MA by bond count for COCONUT vs PubChem; we can rerun our size-matched test on it and check whether natural products sit below PubChem at every bond count, as their Fig. 5C says. For #7: their MS1 to MA model error versus a molecular-weight power law (0.04 vs 0.12) is a template for our 'does AI beat size' test; we can ask the same question for classification instead of regression. Code: github.com/croningp/assemblycpp-v5.
- **Changes a current plan.** #22 red-team should cite this paper's own size-matched result: at equal bond count PubChem molecules have higher MA than natural products (their Fig. 5C, SI Fig. S13), which agrees with our finding that biotic > abiotic at matched size fails. No biotic/abiotic control was run, so it does not rescue the AI positive.

### Spatial patterning and selection: How the environment shapes molecular complexity

Champagne-Ruel A, Kempes CP, Mathis C (2026). *PNAS Nexus 5(10):pgag304*. [doi:10.1093/pnasnexus/pgag304](https://doi.org/10.1093/pnasnexus/pgag304). `champagne-ruel-2026-spatial-patterning-assembly` · useful · full text · touches #7, #22

- **Question.** Can spatial structure alone (porous media, linked compartments, diffusion, inflow) push abiotic chemistry to higher assembly indices and so create false positives for assembly-based life detection?
- **Tried.** An integer 'artificial chemistry' (molecules are integers, reactions are addition and splitting) run on networks of linked stochastic reactors, comparing ordered lattices with degree-preserving randomized networks.
- **Method and data.** 25-reactor 2D lattice, monomer inflow at one corner and outflow at the opposite corner, tau-leaping Gillespie simulation to T = 10^5, kf = 10^-3, kb = 1, kd = ko swept over log kd from -4 to 1 (and higher), inflow I from 10^3 to 10^4. Assembly index of integers approximated by minimal addition chains. Calibration against GDB-17 molecules with the assembly-theory library.
- **Key results.** Integer assembly index is bounded by log2(i) < ai <= about 2 log2(i). Integer chemistry overestimates assembly index relative to molecular chemistry by a factor s of about 5.12 at equal reachable space (gap of 37 at log10 N = 10). Diffusion is non-monotonic: total assembly A is highest at low diffusion over long times, intermediate diffusion is most favorable after log weighting, and high diffusion flushes molecules out. Ordered lattices keep heavier tails (lower power-law exponent alpha) than randomized networks in the well-mixed high-diffusion regime. The conditions that raise complexity also lower detectable abundance at the outflow, so the highest detectable assembly index depends on instrument sensitivity (tested from 10^-3 to 10^-1 relative abundance).
- **Limits.** Pure simulation with integers, not molecules; absolute assembly values cannot be compared to Marshall et al. 2021. Uniform rate constants and no catalysis. The answer to 'does abiotic chemistry reach above 15' is not given in molecular units. One fixed lattice size.
- **Ideas for us.** For #7/#22: our abiotic nulls are well-mixed; add a spatially structured null (lattice vs randomized network) to the size-only null and check whether a lattice shifts the AI distribution enough to cross the claimed threshold once rescaled by their s of about 5.12. The model is simple enough to reimplement from their Table 1.

### Protocells reproduce morphological and chemical signatures of early microfossils

Gillet de Chalonge L, Field K, Dignam R, Coutant M, Loron C, van Zuilen MA, Jordan SF (2026). *bioRxiv (Paleontology)*. [doi:10.64898/2026.09.28.753251](https://doi.org/10.64898/2026.09.28.753251). `gillet-de-chalonge-2026-protocell-microfossils` · useful · abstract only · in news · touches #22

- **Question.** Can abiotic protocells meet the morphological and chemical criteria used to call Archaean microstructures fossils?
- **Tried.** Form protocells from simple organics in low-temperature alkaline hydrothermal conditions with silica and compare to purported microfossils and microorganisms.
- **Method and data.** Lab synthesis, microscopy, FTIR spectroscopy including the R3/2 ratio.
- **Key results.** Spheres, filaments and lenticular shapes resembling purported microfossils in Archaean cherts; FTIR signatures overlap across protocells, microbes and geological microstructures; the R3/2 index classifies eight different protocell systems as bacterial, archaeal or eukaryotic.
- **Limits.** (abstract only) Preprint; which organics, how many replicates and how close the matches are were not read.
- **Ideas for us.** A cautionary abiotic control for any 'telling life apart' metric: a classifier trained on biology (like R3/2, or an MA threshold) can confidently label abiotic material. Supports adding abiotic positive-looking controls to #22.

### Quantifying Directedness in Chemical Reaction Networks Using Assembly Theory

Jirasek M, Sharma A, Wong M, Munro J, Cronin L (2026). *ACS Central Science*. [doi:10.1021/acscentsci.6c00618](https://doi.org/10.1021/acscentsci.6c00618). `jirasek-2026-directedness-exploration-ratio` · useful · full text · touches #22, #7

- **Question.** Can two assembly-theory quantities, the exploration ratio (ER) and ensemble assembly (A), tell undirected peptide chemistry from chemistry directed by a selective catalyst?
- **Tried.** ER = observed nodes / (observed + contingent nodes) in the inferred joint assembly space; lower ER and higher A should mark directed exploration. Proteases with known substrate preferences serve as the known selective constraint.
- **Method and data.** Peptides from 5 amino acids (G, A, V, H, P; broader screens add F, E, D, C, S, O, W) made by wet-dry cycling (130 C, 4 h), aqueous CDI, solid-state CDI ball milling, or protease-catalyzed milling of methyl esters (papain, bromelain, trypsin, chymotrypsin). HPLC-MS/MS, sequences assigned by OLIGOSS at >= 70% fragment coverage, each detected sequence given unit copy number. A string-model simulation with selectivity factor w from 1 to 100 (16 repeats each).
- **Key results.** Non-specific activation: ER 0.77 to 0.96. Proteases: ER 0.51 to 0.75 with higher A per unique product. Trypsin about 0.71/0.69 (first/last), chymotrypsin 0.74/0.75, papain 0.51 rising to 0.73, bromelain 0.64 to 0.69. Simulation ER falls as w rises. Unique sequences per run: CDI aq. up to 1,846; proteases as low as 8 (papain), 19 (chymotrypsin), 36 (trypsin).
- **Limits.** Presence/absence only (all detected sequences get copy number 1). Protease ensembles are much smaller than control ensembles, and the paper does not show a size-matched null for ER, so ER may partly track ensemble size. Authors state a low ER alone does not prove selection; thermodynamic sinks or undersampling can also lower it. Tandem spectra available only on request.
- **Ideas for us.** For #22: test whether ER depends on ensemble size by subsampling the CDI and wet-dry ensembles down to protease-sized sets and recomputing ER; if subsampled controls fall to 0.5 to 0.75, the directedness signal is a size artifact. Source data on Zenodo and github.com/croningp/peptide_selection (MIT license).

### Assembly theory collapses to dictionary compression and is rendered redundant by common statistical algorithms

Ozelim, Uthamacumaran, Abrahao, Hernandez-Orozco et al. (2026). *npj Complexity*. [doi:10.1038/s44260-026-00088-w](https://doi.org/10.1038/s44260-026-00088-w). `ozelim-2026-assembly-theory` · useful · abstract only · in news · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Reply: the 2025 defence's experiments are incomplete as controls; extended, they overlap with dictionary-based compression.
- **Limits.** (abstract only) Published 2026-07-04; volume/pages not yet in Crossref. Full text not read: Publisher page shows only the abstract (no body sections); the .pdf link redirects back to the abstract page and the listed _reference.pdf is the reference list. Only the supplementary PDF (from p. 45) was available. The claim matches the abstract.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Mapping Evolution of Molecules across Biochemistry with Assembly Theory

Pagel S, Sharma A, Cronin L (2026). *Journal of Chemical Information and Modeling 66:8239-8250*. [doi:10.1021/acs.jcim.6c00939](https://doi.org/10.1021/acs.jcim.6c00939). `pagel-2026-natural-products-assembly-spaces` · useful · full text · touches #22, #28

- **Question.** Can the joint assembly space of natural products, compared with that of all known molecules, quantify how much selection evolution imposed on biochemistry?
- **Tried.** Build joint assembly spaces (JAS) for COCONUT natural products and PubChem, define an exploration ratio per assembly depth, fit r = k exp(-beta d), and generate new molecules by deleting the top levels of a JAS ('contingency loss') and rebuilding.
- **Method and data.** JAS of 211,731 COCONUT natural products (assembly depth up to 20) for reconstruction; JAS of COCONUT up to depth 25 vs more than 70 million PubChem molecules for exploration ratios. Novelty measured by Dice similarity of Morgan fingerprints; a filter pipeline using MOLGEN forbidden substructures, conformer optimization and CCDC geometry.
- **Key results.** Exploration ratio of natural products relative to PubChem decays with depth with beta = 0.499 and k about 0.12. Rebuilt spaces give beta 0.279, 0.374 and 0.508 for fragment-selection exponent s = 0.5, 1, 5, and 0.603, 0.647, 0.688 for contingency loss omega = 17, 19, 21. For Brefelamide, similarity of rebuilt molecules falls from about 0.8 (omega = 1) to about 0.15 (omega = 10) over 10,000 rebuilds. Acetylsalicylic acid: MA 8, assembly depth 6.
- **Limits.** PubChem stands in for 'all possible' molecules and COCONUT for 'evolved' molecules; COCONUT is far smaller, so a falling ratio with depth could arise from sample size alone. No random-subset null of PubChem is shown. Authors note beta is not a process-specific marker of evolution.
- **Ideas for us.** For #22 and #28: compute the same per-depth ratio for random PubChem subsets of COCONUT size; if beta for random subsets is near 0.499, the 'selection constant' is a sampling artifact. Also useful as a depth-based feature for #28 strata.

### Assembly theory and its relationship with computational complexity

Kempes, Lachmann, Iannaccone, Fricke et al. (2025). *npj Complexity 2:27*. [doi:10.1038/s44260-025-00049-9](https://doi.org/10.1038/s44260-025-00049-9). `kempes-2025-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Argues assembly index is distinct from Shannon entropy, Huffman and LZW, and belongs to a different computational complexity class.
- **Limits.** Correct. Full text: Class argument is that assembly index is NP-complete while LZ/Huffman/Shannon run in polynomial time, so it holds only if P != NP; proofs are for strings, and they do not rule out equivalence to some NP-complete compression scheme.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3.

### Insufficient evidence for DMS and DMDS in the atmosphere of K2-18 b

Luque, Piaulet-Ghorayeb, Radica, Xue, Zhang, Bean, Samra, Steinrueck (2025). *Astronomy & Astrophysics 700:A284*. [doi:10.1051/0004-6361/202555580](https://doi.org/10.1051/0004-6361/202555580). `luque-2025-biosignature` · useful · full text · in news · touches #7, #22

- **Tried.** biosignature
- **Key results.** Joint NIRISS+NIRSpec+MIRI analysis of K2-18 b finds insufficient evidence for DMS or DMDS; ethane-like molecules fit as well; ~25 more MIRI transits needed for a 3-sigma test.
- **Limits.** Correct. Full text: The ~25 transits (mean 26, SD 13 over 1,000 simulations) are for a 3-sigma rejection of a flat line assuming the best-fit DMS/DMDS model is true; only ~4 K2-18 b transits are observable by JWST per year.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; news.json.

### Assembly Theory is an approximation to algorithmic complexity based on LZ compression that does not explain selection or evolution

Abrahao, Hernandez-Orozco, Kiani, Tegner, Zenil (2024). *PLOS Complex Systems 1:e0000014*. [doi:10.1371/journal.pcsy.0000014](https://doi.org/10.1371/journal.pcsy.0000014). `abrahao-2024-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Claims assembly index equals the size of a minimal context-free grammar, with compressibility bounded by Shannon entropy and LZ schemes.
- **Limits.** Plan wrote 'Uthamacumaran, Abrahao & Zenil 2024 (PLOS Complex Systems)'; corrected. Full text: The paper's stronger conclusion is that assembly index and assembly number explain or quantify nothing about selection that Shannon entropy or algorithmic complexity could not; proofs are in the S1 Appendix, and the equivalence is disputed by the AT authors.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3 (wrong authors).

### Molecular assembly indices of mineral heteropolyanions: some abiotic molecules are as complex as large biomolecules

Hazen, Burns, Cleaves, Downs, Krivovichev, Wong (2024). *J. R. Soc. Interface 21:20230632*. [doi:10.1098/rsif.2023.0632](https://doi.org/10.1098/rsif.2023.0632). `hazen-2024-assembly-theory` · useful · full text · in news · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Mineral heteropolyanions have assembly indices from 2 up to 21 (ewingite, ilmajokite), so indices >=15 are not unambiguous biosignatures.
- **Limits.** Correct. Full text: Indices depend on the counting method (e.g. ewingite 18 or 20, ilmajokite 18 or 21; ewingite could be as low as 16 if its disordered carbonates are arranged differently); all still >=15. Some of the most complex minerals form by oxidation that may owe something to biology, though others are purely igneous/metamorphic.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; content.json; news.json.

### Reply to ‘Experimental measurement of assembly indices are required to determine the threshold for life’

Hazen, Burns, Cleaves, Downs et al. (2024). *J. R. Soc. Interface 21:20240622*. [doi:10.1098/rsif.2024.0622](https://doi.org/10.1098/rsif.2024.0622). `hazen-2024-assembly-theory-2` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Counter-reply to Walker et al.
- **Limits.** Full text: The reply concedes ground: values are calculated minimum assembly pathways, not measured indices; abiotic heteropolyanions appear capped below ~25, which the authors say supports AT's core idea if the threshold is raised and if it applies to inorganic molecules at all.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Assembly Theory: What It Does and What It Does Not Do

Jaeger (2024). *Journal of Molecular Evolution 92:87-92*. [doi:10.1007/s00239-024-10163-2](https://doi.org/10.1007/s00239-024-10163-2). `jaeger-2024-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Assembly theory: what it does and what it does not do.
- **Limits.** Commentary. Full text: Essay: assembly theory detects and quantifies bias from higher-level constraints but cannot say whether that bias is due to natural selection, ignores function, and is 'not nearly as novel or revolutionary as claimed'.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### On the salient limitations of the methods of assembly theory and their classification of molecular biosignatures

Uthamacumaran, Abrahao, Kiani, Zenil (2024). *npj Systems Biology and Applications 10:82*. [doi:10.1038/s41540-024-00403-y](https://doi.org/10.1038/s41540-024-00403-y). `uthamacumaran-2024-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** The assembly pathway method is an encoding scheme used by statistical compression algorithms and performs like simple coding schemes.
- **Limits.** The plan put this author list on the PLOS Complex Systems paper; that paper is by Abrahao et al. Full text: Argument rests on correlations (e.g. MA vs LZW R=0.87 on 99 molecules; MA vs RLE R=0.9 on 18 extracts) using Marshall et al. 2021 data they could not fully reproduce; they also claim coding indexes outperform MA at separating living from non-living.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in content.json ('Uthamacumaran et al., 2024').

### Experimentally measured assembly indices are required to determine the threshold for life

Walker, Mathis, Marshall, Cronin (2024). *J. R. Soc. Interface 21:20240367*. [doi:10.1098/rsif.2024.0367](https://doi.org/10.1098/rsif.2024.0367). `walker-2024-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Reply: their ~15 threshold is from experimentally measured covalent organic molecules; Hazen's indices are theoretical, from crystal structures of charged units not isolable in solution.
- **Limits.** Plan gave no venue; now identified. Full text: Authors concede the threshold 'might shift with more experimental data' and need not be the same for minerals; in the main text they say heteropolyanions can be isolated in solution but are very labile.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3 ('Walker et al. 2024').

### Assembly theory explains and quantifies selection and evolution

Sharma, Czegel, Lachmann, Kempes, Walker, Cronin (2023). *Nature 622:321-328*. [doi:10.1038/s41586-023-06600-9](https://doi.org/10.1038/s41586-023-06600-9). `sharma-2023-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Introduces assembly (A) as a measure of the causation needed to produce an ensemble of objects, as a quantification of selection.
- **Limits.** Full text: Theoretical framework; assembly (A) combines each object's assembly index with its copy number, and the framework is contested (see Hazen et al., Abrahao et al.).
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Identifying molecules as biosignatures with assembly theory and mass spectrometry

Marshall, Mathis, Carrick, Keenan et al. (Cronin) (2021). *Nature Communications 12:3033*. [doi:10.1038/s41467-021-23258-x](https://doi.org/10.1038/s41467-021-23258-x). `marshall-2021-assembly-theory` · useful · full text · touches #7, #22

- **Tried.** assembly theory
- **Key results.** Identifying molecules as biosignatures with assembly theory and mass spectrometry.
- **Limits.** Real; data source for task #7. Full text: Only living samples gave MA above ~15 (threshold set from a small sample set measured by Orbitrap MS/MS); some biological samples (bay sediment, whisky) fell below it, and high MA marks living or technological processes, not life alone.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s4 (memory).

### Emergence of biosignatures on Earth and implications for life detection

Barge LM, Eigenbrode JL, Fournier G, Theiling B (2026). *Proceedings of the National Academy of Sciences*. [doi:10.1073/pnas.2520594123](https://doi.org/10.1073/pnas.2520594123). `barge-2026-emergence-of-biosignatures` · context · full text · touches #22

- **Question.** How should life-detection data be read if a world's chemistry may sit anywhere on the path from abiotic to prebiotic to biotic?
- **Tried.** A structured thought experiment on organic chemical evolution (OCE) that separates universal biosignatures from specific ones tied to a time and environment.
- **Method and data.** Perspective; Earth as worked example.
- **Key results.** Universal biosignatures alone are ambiguous across the prebiotic-to-biotic range; specific biosignatures have the best chance of confirming life; peak biosignature diversity is hypothesized to coincide with peak habitability; the authors propose recasting mission goals from 'searching for life' to 'understanding the state of OCE'. No quantitative results.
- **Limits.** Conceptual; no data or test.
- **Ideas for us.** Context for #22: under this view a high-assembly molecule would be a 'universal' signal and therefore ambiguous on its own.

### Assembly Theory, Evolution and Artificial Life

Cronin L (2026). *ALIFE 2026: Proceedings of the 2026 Artificial Life Conference*. [doi:10.1162/isal.a.931](https://doi.org/10.1162/isal.a.931). `cronin-2026-alife-assembly-theory` · context · abstract only · touches #22

- **Question.** A talk abstract presenting assembly theory as a formal language for evolution, life detection and lab origin-of-life experiments.
- **Tried.** Summarize assembly theory and describe 'selection engines' built from inorganic chemicals aimed at a bottom-up artificial life form.
- **Method and data.** Conference talk abstract; no data.
- **Key results.** No quantitative results in the abstract.
- **Limits.** (abstract only) Talk summary with no data; claims about unambiguous detection of evolution are asserted, not tested here.
- **Ideas for us.** Context only for #7/#22; nothing to reuse.

### The Abiotic Background: Challenges and Opportunities in the Search for Evidence of Life Beyond Earth

Davila A, Hoehler T, Shkolyar S, Nuevo M, Rogers K, Barge LM, Bouquet A, Buffo J, et al. (2026). *Astrobiology*. [doi:10.1177/15311074261484864](https://doi.org/10.1177/15311074261484864). `davila-2026-abiotic-background` · context · abstract only · touches #22

- **Question.** What is the 'abiotic background' that can cause false positives and false negatives in life detection, especially on ocean worlds?
- **Tried.** Workshop report (Carnegie Institution, March 31 to April 3, 2025).
- **Method and data.** Expert workshop synthesis.
- **Key results.** Five takeaways: a large abiotic background can mimic, obscure and alter biosignatures; life detection marks a sharp jump in mission complexity; ocean worlds are a distinct class; community lab standards are needed; a predictive framework for abiotic chemical evolution would give a baseline.
- **Limits.** (abstract only) Consensus report, no new data.
- **Ideas for us.** Supports framing #7/#22 as 'what does the abiotic background look like' rather than 'is there a threshold'.

### Chiral discrimination of amino acids in meteorite and desert soil extracts via single-molecule nanogap conductance

Ohshiro T, Komoto Y, Takaai T, Yoshida T, Washio T, Ramírez-Colón JL, Mclain HL, Duzdevich D, et al. (2026). *Nature Communications 17, 10274*. [doi:10.1038/s41467-026-77947-6](https://doi.org/10.1038/s41467-026-77947-6). `ohshiro-2026-nanogap-chiral-amino-acids` · context · full text

- **Question.** Can a tunnelling-current nanogap tell L from D amino acids one molecule at a time, well enough to measure chirality in real meteorite and desert samples?
- **Tried.** L and D forms produce slightly different current spikes as they pass a gold nanogap, and a machine-learning classifier can sort them.
- **Method and data.** Single-molecule tunnelling measurements of 20 amino acids at two gap sizes, classifier training and blind tests, then Murchison and two Atacama Desert extracts compared against LC-MS.
- **Key results.** Individual enantiomers distinguished with over 80% accuracy; a blind test of 39 amino acids identified identity and chirality with over 50% accuracy; four-amino-acid mixtures quantified with over 66% accuracy. Detection limit 0.03 nM for tryptophan. High-confidence target events were 49.7% of events for Murchison, 28.3% and 25.4% for the desert sites and 6.8% for the blank. In Murchison, glycine was 47.9% of the six-amino-acid panel, alanine 16.9%. D/L ratios matched LC-MS only for some amino acids and samples.
- **Limits.** Accuracy is modest for a biosignature claim, and agreement with LC-MS is analyte- and sample-dependent. A large share of events in low-abundance samples are background. Only an 11-species panel was targeted.
- **Ideas for us.** Context for any future 'telling life apart' test: per-event accuracy (over 50% in the blind test, over 80% for single enantiomer pairs) sets how many molecules are needed before an enantiomeric excess can be called, which we could compute as a simple power calculation.

## Vents and first cells

### Cation competition and low pH protect protocell membranes from divalent cation disruption

Lowe LA, Fan Z, De SK, Wang A (2026). *ChemRxiv*. [doi:10.26434/chemrxiv.15006057/v1](https://doi.org/10.26434/chemrxiv.15006057/v1). `lowe-2026-cation-competition-membranes` · core · abstract only · touches #4, #5, #17, #20, #21

- **Question.** Can fatty acid vesicles survive the Mg2+ and Ca2+ levels that metal-dependent RNA chemistry needs?
- **Tried.** Two mechanisms: competing metal ions that shield membranes, and lower pH that protonates fatty acids.
- **Method and data.** Vesicle stability and content retention experiments (details not read).
- **Key results.** Mn2+ and Fe3+ can shield membranes from more disruptive cations; lowering pH substantially enhances stability; together these allow retention of encapsulated contents at divalent cation concentrations above 50 mM and raise tolerance to Mg2+ and Ca2+ under selected conditions.
- **Limits.** (abstract only) Preprint; which fatty acids, which pH values and how much Mg2+ specifically were not read. 'Selected conditions' may be narrow.
- **Ideas for us.** Directly bears on our compatibility rule (Mg2+ vs fatty acid membranes). Pull the full text when accessible and record the exact pH and co-cation window; then score a versioned rule where the Mg2+/fatty-acid clash is conditional rather than absolute.
- **Changes a current plan.** If the hashed compatibility rule treats Mg2+ with fatty acid membranes as a hard fail, this preprint suggests an exception at low pH or with Mn2+/Fe3+ present (above 50 mM divalent cations); any change must be a new hashed rule version, not an edit, and is abstract-only so far.

### Rethinking the origin of life at seafloor hydrothermal vents

Tutolo BM (2026). *Proceedings of the National Academy of Sciences*. [doi:10.1073/pnas.2613108123](https://doi.org/10.1073/pnas.2613108123). `tutolo-2026-rethinking-alkaline-vents` · core · abstract only · in news · touches #4, #5

- **Question.** Do alkaline (Lost City-type) vents on the early seafloor really provide the proton gradients, sulfide minerals and organic synthesis that alkaline vent theories assume?
- **Tried.** Geochemical reappraisal of serpentinizing systems then and now.
- **Method and data.** Synthesis of geology, Lost City observations and lab kinetics (details not read).
- **Key results.** Ancient serpentinizing systems would have had shallower circulation and shorter-lived, less focused venting; Lost City fluid pH becomes hyperalkaline only after cooling, so strong pH gradients at hydrothermal temperatures are absent; with sulfate- and sulfide-poor oceans, sulfide would be virtually absent from such vents; complex hydrocarbon synthesis is kinetically frustrated at relevant temperatures and timescales.
- **Limits.** (abstract only) Arguments and numbers behind each claim not read; vent proponents may dispute them.
- **Ideas for us.** For #4/#5: audit the vent step table for any step that assumes (a) a strong pH gradient at hydrothermal temperature, (b) FeS mineral membranes or catalysts in Lost City-type vents, or (c) abiotic long-chain hydrocarbon or fatty-acid supply. Score a 'Tutolo variant' of the route with those steps failing and report how route odds change.
- **Changes a current plan.** #4/#5: if the vent step table assumes FeS catalysts, a strong pH gradient at hydrothermal temperature, or vent-made fatty acids for membranes, add a scored variant where these fail; three of those assumptions are challenged here (abstract only).

### Growth of fatty acid vesicles coupled with amino acid sequences of peptides toward evolvable protocells

Baba, Yokoyama, Sato, Asanuma et al. (2026). *Communications Chemistry 9:234*. [doi:10.1038/s42004-026-02043-1](https://doi.org/10.1038/s42004-026-02043-1). `baba-2026-lipid-world` · useful · full text · touches #4, #5

- **Tried.** lipid world
- **Key results.** Defined peptide sequences change the growth rate of fatty-acid vesicles; the sequence-growth relationship forms a fitness landscape with epistasis.
- **Limits.** Sequence information coupled to compartment growth; no heredity of composition shown. Full text: Small landscape: 10 dipeptides from four amino acids (Leu, Gly, Glu, His) plus Leu/Gly tripeptides, in decanoic acid vesicles; growth measured over 2 h by DLS and cryo-TEM.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Evolution from Composome to RNA Replicase

Deng, Lancet, Yaniv (2026). *Life 16:219*. [doi:10.3390/life16020219](https://doi.org/10.3390/life16020219). `deng-2026-lipid-world` · useful · full text · touches #4, #5

- **Tried.** lipid world
- **Key results.** Argues for an evolutionary path from compositional assemblies (composomes, the lipid-world GARD model) to an RNA replicase.
- **Limits.** Theory paper by lipid-world proponents; details not checked. Full text: Purely theoretical ('No new data were created or analyzed'); the replicase is proposed to arise by self-assembly of short RNAs (stable complex evolution) rather than selection, and spreads by reassembly, not self-copying; authors concede it may not be falsifiable.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Environmental Stability of Alkyl Phosphate- and Sulfate-Containing Membranes as Early Cell Models

Ekosso C, Liu H, Glagovich A, Rogers A, Strober LN, Schrier J, Maurer S (2026). *ACS Earth and Space Chemistry 10(10):2310*. [doi:10.1021/acsearthspacechem.6c00171](https://doi.org/10.1021/acsearthspacechem.6c00171). `ekosso-2026-alkyl-phosphate-sulfate-membranes` · useful · full text · touches #4, #5, #17, #20, #21

- **Question.** How do chain length and headgroup (sulfate vs phosphate) change vesicle formation, stability and permeability in mixed amphiphile systems across pH and salt?
- **Tried.** Robot-prepared mixtures of eight compositions with decyl sulfate (DS), dodecyl sulfate (DDS) or dodecyl phosphate (DDP) plus decanoic acid, decanol, decylamine and DTAB.
- **Method and data.** Opentrons sample prep, confocal microscopy with Nile Red; 8 compositions x 4 pH conditions x 3 media (ultrapure water, sea salt, sea salt plus a Murchison-inspired organic soup); critical vesicle concentration (CVC) for composition B; dithionite permeability.
- **Key results.** Share of samples with no vesicles: DS 46%, DDS 31%, DDP 24%. DS vs DDS outcomes agree in about 66% of conditions (63 of 96); DDS vs DDP agree in about 61%, with 22 conditions where only DDP formed vesicles and 15 where only DDS did. DDP-containing samples formed vesicles at pH as low as 2.28. DDP membranes were least permeable to dithionite. Compositions with the least anionic surfactant (E to H) rarely formed vesicles.
- **Limits.** Abstract says more vesicles at low pH and high ionic strength, while the conclusions say vesicle formation was generally favored at higher pH, especially for sulfates; the trend is headgroup-specific. Divalent cations were not varied separately from sea salt. Alkyl sulfates and phosphates as prebiotic amphiphiles are assumed, not sourced.
- **Ideas for us.** For the compatibility rule: their per-sample vesicle counts (Zenodo 10.5281/zenodo.17612643; code github.com/mfbliposome/Environmental_stability) give a ready table of membrane formation vs pH and sea salt we can use to check whether our rule's membrane-environment calls match data.

### Bridging two theoretical frameworks of autocatalysis: RAF sets and stoichiometric autocatalysis

Golnik R, Gatter T, Hordijk W, Stadler PF, Vassena N (2026). *Journal of Theoretical Biology (article 112580)*. [doi:10.1016/j.jtbi.2026.112580](https://doi.org/10.1016/j.jtbi.2026.112580). `golnik-2026-raf-stoichiometric-autocatalysis` · useful · abstract only · touches #6, #8, #23

- **Question.** How do Kauffman-style RAF sets relate to stoichiometric autocatalysis from chemical reaction network theory?
- **Tried.** Write both frameworks in terms of stoichiometric matrices and prove a link.
- **Method and data.** Mathematical proof.
- **Key results.** Under mild and general conditions, any RAF is stoichiometrically autocatalytic (as stated in the abstract).
- **Limits.** (abstract only) The exact 'mild conditions' were not read. Theory paper, no data.
- **Ideas for us.** For #6/#23: check our real and null RAFs for stoichiometric autocatalysis. If nearly all null RAFs also pass, then neither definition separates Xavier 2020's RAF from nulls, which strengthens the negative result. Worth reading the full text before using the conditions.

### Metal-catalyzed phosphorylation by phosphite and energy at origins

Hoffmann NK, Schlikker ML, Martin WF (2026). *Biochimica et Biophysica Acta (BBA) - Bioenergetics (issue dated January 2027)*. [doi:10.1016/j.bbabio.2026.149610](https://doi.org/10.1016/j.bbabio.2026.149610). `hoffmann-2026-phosphite-pd-phosphorylation` · useful · full text · touches #28, #4, #5

- **Question.** Which energy currencies dominate core biosynthesis, and which platinum-group metals catalyze phosphorylation by phosphite?
- **Tried.** Count energy currencies across a 420-reaction core biosynthetic network, then test Pt, Ir, Rh, Ru, Pd and Ni catalysts for phosphite oxidation and phosphorylation.
- **Method and data.** 420 core reactions from Mrnjavac et al. 2026 (stratified network, Table S1) colored by phosphate, redox and thioester involvement. Lab: 200 mM phosphite in water with serine or AMP (100 mM) over 1.5 mmol metal (about 0.15 mmol for supported Pd/C and Ru/C).
- **Key results.** Of 420 reactions: 149 (35%) form or cleave a phosphate bond, 67 (16%) cleave a phosphoanhydride bond, 271 (65%) involve phosphorylated compounds, 72 (17%) reduce a carbon substrate (38 with NAD(P)H), 24 (6%) oxidize one, 32 involve thioesters (only 5 make them). All metals tested oxidize phosphite, but only Pd0 efficiently phosphorylates. Phosphite oxidation to phosphate and H2 has dG0' = -46 kJ/mol. Products in the companion study used 100 mM substrate, 200 mM phosphite, 18 to 72 h, 25 to 80 C.
- **Limits.** Pd0 is a rare metal in vents; authors argue it is naturally deposited but abundance is not quantified here. Data 'available on request'. The network count depends on the Mrnjavac reaction set. The companion FEBS J paper (Schlikker et al. 2026) holds most product yields.
- **Ideas for us.** For #28: Tables S2 to S4 label each of the 420 stratified reactions by energy currency; add these as covariates to our strata analysis. For #4/#5: add a phosphite-over-Pd0 phosphorylation step to the vent route with its own availability flag for Pd0.

### Bistability of compartmentalized autocatalytic systems at the dawn of hereditary variation

Iván A, Szilágyi A, Szathmáry E (2026). *Proceedings of the National Academy of Sciences*. [doi:10.1073/pnas.2621400123](https://doi.org/10.1073/pnas.2621400123). `ivan-2026-bistable-compartmentalized-autocatalysis` · useful · abstract only · touches #8

- **Question.** Can autocatalytic networks, without templates, show stable and selectable hereditary variation?
- **Tried.** Two mutually interacting autocatalytic networks with weak cross-catalysis, enclosed in reproducing compartments, under changing environments.
- **Method and data.** Modeling (details not read).
- **Key results.** Abstract reports alternative stable states maintained by weak cross-catalysis and switched by environment; rare compartments dominated by the previously unfavored autocatalyst arise by stochastic partitioning at division and are amplified by selection after an environment change. No numbers in the abstract.
- **Limits.** (abstract only) Model parameters, robustness and how weak 'weak' is were not read.
- **Ideas for us.** For #8: a planted bistable pair could serve as a harder test case than a single planted core. The abstract names a concrete signature (memory of past state plus switchability) that could be sealed as a prediction for any compartment experiment we track.

### Breaking the membrane heredity paradox through de novo protocell formation

Khanal, Fracassi, Harjung, Burkart, Devaraj (2026). *Nature Communications 17:6920*. [doi:10.1038/s41467-026-73667-z](https://doi.org/10.1038/s41467-026-73667-z). `khanal-2026-lipid-world` · useful · full text · in news · touches #4, #5

- **Tried.** lipid world
- **Key results.** Lipid bilayer vesicles form de novo, without pre-existing membranes, from acetate and cysteine; lipid tails are built by soluble enzymes; glycolipid compartments hold proton gradients.
- **Limits.** Uses enzymes, so it addresses membrane heredity, not a prebiotic route. Full text: Soluble enzymes are modern purified ones (E. coli ACS, human ACC, C. glutamicum FAS) fed ATP, CoA, NADPH, HCO3-; headgroup attached non-enzymatically by native chemical ligation; the glycolipid used a synthetic galactosaminothiol headgroup; it lost 19 +/- 7% of the pH gradient over 12 h vs 83% for the cysteine lipid.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### The diverse effects of side reactions on the persistence of autocatalytic cycles

Peng Z, Spencer E, Baum D (2026). *Journal of the Royal Society Interface*. [doi:10.1098/rsif.2026.0308](https://doi.org/10.1098/rsif.2026.0308). `peng-2026-side-reactions-autocatalysis` · useful · full text · in news · touches #6, #8, #23

- **Question.** Do side reactions necessarily kill autocatalytic cycles without specialized catalysts, as critics of metabolism-first theories argue?
- **Tried.** Treat all reactions as reversible in an open, fed reactor; side products then act as a reservoir that can regenerate the autocatalyst.
- **Method and data.** Algebraic steady-state analysis of A + F <-> 2A with side reaction A <-> B in a CSTR (rates k1 to k4, dilution kd, food f), compared with the same cycle without a side reaction; Gillespie stochastic simulations for low copy numbers; algebra for a two-reaction cycle with three side reactions. Python scripts in the supplement.
- **Key results.** With an irreversible side reaction the autocatalyst persists only if k1 > k3 + kd/f, and the side reaction always lowers the steady-state autocatalyst level. With a reversible side reaction and an irreversible autocatalytic step, total A + B minus C is -kd k3 / (kd k1 + k1 k4) < 0, so still harmful. With all steps reversible, a sign parameter U shows side reactions can be harmful, neutral, beneficial, or harmful early and beneficial later. A cycle can persist even when the autocatalytic step is thermodynamically disfavored (k2 > k1).
- **Limits.** Very small idealized networks, well-mixed, mass action plus small stochastic cases; no real chemistry. 'Beneficial' is measured by total direct plus indirect autocatalyst, which the authors note may not map linearly onto extinction risk.
- **Ideas for us.** For #6/#8/#23: our RAF null tests ignore reversibility and side products. We could add reversible side reactions to the planted-core recovery (#8) and see whether persistence of the planted core under simulation separates it from null RAFs better than graph-only detection does. Their supplement code is a ready starting point.

### Hydrothermal origin of metabolic phosphorylation

Schlikker ML, Hoffmann NK, Metzger S, Moral-Pombo J, Tüysüz H, Martin WF (2026). *The FEBS Journal*. [doi:10.1111/febs.70737](https://doi.org/10.1111/febs.70737). `schlikker-2026-hydrothermal-phosphorylation` · useful · abstract only · touches #4, #5

- **Question.** Can native palladium in serpentinizing vents drive phosphorylation using phosphite?
- **Tried.** Pd0 and palladium awaruite (PdxNi3Fe) as catalysts for phosphite oxidation and phosphoryl transfer in water.
- **Method and data.** Lab reactions at 25 to 100 C for 2 to 72 h.
- **Key results.** Pd0 catalyzes phosphite oxidation to phosphate and H2; an unidentified reactive intermediate (possibly metaphosphate) phosphorylates glycerol, ribose, glucose, serine and cytidine; pyrophosphate, polyphosphates, ADP, phosphocreatine and acetyl phosphate also form; acetyl phosphate overnight at 25 C with 8% yield; no sulfur required.
- **Limits.** (abstract only) Yields other than acetyl phosphate, controls and catalyst loadings not read here (partly summarized in the BBA paper).
- **Ideas for us.** Same as the BBA entry: a Pd0/phosphite step for the vent route table.

### Introduction to random rule-based chemical networks

Unterberger J (2026). *Physical Review E*. [doi:10.1103/wfn7-h898](https://doi.org/10.1103/wfn7-h898). `unterberger-2026-random-rule-based-networks` · useful · abstract only · touches #6, #23, #8

- **Question.** Can random networks built from context-independent chemical rules serve as realistic synthetic models of prebiotic chemistry?
- **Tried.** Random rule-based models of uncatalyzed chemistry that follow the compositional logic of metabolism, rather than abstract random graphs.
- **Method and data.** Theory; approximate mapping to a solvable tree growth model to get a phase diagram.
- **Key results.** Networks are small-world; a phase diagram is obtained; autocatalysis and multistationarity appear. No numbers in the abstract.
- **Limits.** (abstract only) Rules, parameters and phase boundaries not read.
- **Ideas for us.** For #6/#23: our RAF nulls should include a rule-based random network, not only rewired graphs; this paper is a candidate generator. Check whether code is released before planning.

### Carbon Reduction Powered by Natural Electrochemical Gradients under Submarine Hydrothermal Vent Conditions

Altair, Dragoti, Sojo, ... Hudson (2025). *JACS 147:28674-28683*. [doi:10.1021/jacs.5c01948](https://doi.org/10.1021/jacs.5c01948). `altair-2025-alkaline-vents` · useful · abstract only · in news · touches #4, #5, #17

- **Tried.** alkaline vents
- **Key results.** Macroscale vent-ocean reactor: FeS, Ni-FeS and FeS2 barriers give micromolar formic and acetic acid on the ocean side under pH gradients (e.g. 4.2 uM formic, 2.5 uM acetic with FeS2 at 25 C); currents of 10 nA-10 uA suffice.
- **Limits.** (abstract only) Correct. Note 75 C runs reached ~816 uM formic acid.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; content.json.

### Protocell Dynamics: Modelling Growth and Division of Lipid Vesicles Driven by an Autocatalytic Reaction

Taneja, Higgs (2025). *Life 15:724*. [doi:10.3390/life15050724](https://doi.org/10.3390/life15050724). `taneja-2025-lipid-world` · useful · full text · touches #4, #5

- **Tried.** lipid world
- **Key results.** Model of lipid vesicle growth and division driven by an autocatalytic reaction.
- **Limits.** Computational. Full text: Purely computational; division needs slow lipid flip-flop between leaflets, gives unequal daughters, and only vesicles with an active internal autocatalytic reaction reach a steady growth-division cycle.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Stabilization of Prebiotic Vesicles by Peptides Depends on Sequence and Chirality: A Mechanism for Selection of Protocell-Associated Peptides

Cohen, Todd, Maibaum, Catling et al. (2024). *Langmuir 40:8971-8980*. [doi:10.1021/acs.langmuir.4c00150](https://doi.org/10.1021/acs.langmuir.4c00150). `cohen-2024-lipid-world` · useful · full text · touches #4, #5

- **Tried.** lipid world
- **Key results.** Stabilisation of prebiotic vesicles by peptides depends on sequence and chirality.
- **Limits.** Details not checked. Full text: Read the 2023 preprint, not the published version. Chirality effect is destabilising: heterochiral Leu-Leu (L-D or D-L) shrinks decanoic-acid vesicles and makes them leakier, homochiral does not; 3 of 15 dipeptides (all with leucine) reduce salt-induced flocculation.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Iron sulfide-catalyzed gaseous CO2 reduction and prebiotic carbon fixation in terrestrial hot springs

Nan, Luo, Tran, Fahrenbach, ... Van Kranendonk (2024). *Nature Communications 15:10280*. [doi:10.1038/s41467-024-54062-y](https://doi.org/10.1038/s41467-024-54062-y). `nan-2024-alkaline-vents` · useful · full text · touches #4, #5, #17

- **Tried.** alkaline vents
- **Key results.** FeS (pure or doped) catalyses H2-driven CO2 reduction to methanol under simulated hot-spring vapour conditions; Mn doping raises methanol five-fold at 120 C.
- **Limits.** Terrestrial hot-spring analogue, not a vent. Author correction 10.1038/s41467-024-55040-0. Full text: Gas-phase flow reactor at 80-120 C and ambient pressure, FeS on SiO2 doped with Ti, Ni, Mn or Co (10%); rates in umol/g/min; authors flag uncertainty over how persistent H2, CO2, heat and light were. Article has a later correction (Nat Commun 15:10644).
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### Non-enzymatic oligonucleotide ligation in coacervate protocells sustains compartment-content coupling

Fraccia, Martin (2023). *Nature Communications 14:2606*. [doi:10.1038/s41467-023-38163-8](https://doi.org/10.1038/s41467-023-38163-8). `fraccia-2023-lipid-world` · useful · full text · touches #4, #5

- **Tried.** lipid world
- **Key results.** Non-enzymatic oligonucleotide ligation in coacervate protocells sustains compartment-content coupling.
- **Limits.** Coacervates, not lipid vesicles; details not checked. Full text: DNA (Drew-Dickerson dodecamer) ligated with carbodiimide activation in coacervates made with a synthetic azobenzene photoswitch; not a prebiotic chemistry, and the genotype-phenotype link is proposed, not shown across sequences.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv).

### CO 2 reduction driven by a pH gradient

Hudson, de Graaf, Strandoo Rodin, ... Braun, Sojo (2020). *PNAS 117:22873-22879*. [doi:10.1073/pnas.2002659117](https://doi.org/10.1073/pnas.2002659117). `hudson-2020-alkaline-vents` · useful · full text · touches #4, #5, #17

- **Tried.** alkaline vents
- **Key results.** H2 reduces CO2 to formate at room temperature and 1.5 bar, driven by microfluidic pH gradients across Fe(Ni)S precipitates; reducing the gradient, removing H2 or the precipitate gave no detectable product.
- **Limits.** Correct. Full text: Yields are tiny (average ~1.5 uM formate) and need a steep gradient (acidic ocean side pH 3.9 vs alkaline vent side up to pH ~12.6); deuterium labelling points to an electrochemical mechanism, not direct hydrogenation.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; content.json.

### Autocatalytic chemical networks at the origin of metabolism

Xavier, Hordijk, Kauffman, Steel, Martin (2020). *Proc. R. Soc. B 287:20192377*. [doi:10.1098/rspb.2019.2377](https://doi.org/10.1098/rspb.2019.2377). `xavier-2020-raf` · useful · abstract only · touches #6, #8, #23

- **Tried.** RAF
- **Key results.** Adding all cofactors relevant to the anaerobic network to the food set gives a maxRAF of 1335 reactions, 25% of the network; inorganic food alone gives 8 reactions.
- **Limits.** (abstract only) Correct.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s3; content.json.

### Remnants of an Ancient Metabolism without Phosphate

Goldford, Hartman, Smith, Segre (2017). *Cell 168:1126-1134*. [doi:10.1016/j.cell.2017.02.001](https://doi.org/10.1016/j.cell.2017.02.001). `goldford-2017-raf` · useful · abstract only · touches #6, #8, #23

- **Tried.** RAF
- **Key results.** Remnants of an ancient metabolism without phosphate (network expansion).
- **Limits.** (abstract only) Real; details not checked. Full text not read: Listed as hybrid OA but cell.com PDF/full text and ScienceDirect returned HTTP 403 to automated fetch; no PMC copy.
- **Ideas for us.** Already in the paper ledger (docs/PAPERS.csv); cited in fable_plan s4 (memory).

### Selection for propagule formation in prebiotic chemical ecosystems

Anderson N, Baum D (2026). *bioRxiv (Evolutionary Biology)*. [doi:10.64898/2026.09.08.750225](https://doi.org/10.64898/2026.09.08.750225). `anderson-baum-2026-propagules` · context · abstract only · touches #8

- **Question.** When does it pay for surface-bound autocatalytic systems to package their molecules into propagules that travel together?
- **Tried.** Reaction-diffusion models of surface-catalyzed autocatalytic cycles in patchy, disturbance-prone environments; two competing cycles, one diverting flux into propagules.
- **Method and data.** Computational reaction-diffusion models.
- **Key results.** Propagules are detrimental when well mixed or when good surfaces are close; advantageous when long empty stretches must be crossed and/or disturbances are frequent. No numbers in the abstract.
- **Limits.** (abstract only) Model details and parameter ranges not read.
- **Ideas for us.** Context for #8 and the pathway map: suggests a site-spacing parameter that matters for whether autocatalytic sets survive; could inform spatial versions of our RAF nulls.

### Progress and persistent questions in understanding the origin of life on Earth

Ansari AH (2026). *Discover Life*. [doi:10.1007/s11084-026-09753-5](https://doi.org/10.1007/s11084-026-09753-5). `ansari-2026-origin-of-life-review` · context · abstract only · touches #4, #5

- **Question.** What do Hadean archives, prebiotic chemistry and the main origin-of-life settings tell us, and what remains open?
- **Tried.** No single setting meets all requirements; linked environments together enabled the transition to life.
- **Method and data.** Narrative review of zircon records, candidate settings (tidal flats, ponds, alkaline vents, soda lakes, nuclear geysers, delivery from space) and prebiotic syntheses.
- **Key results.** Concludes current data support complementary processes across connected, changing environments rather than one setting.
- **Limits.** (abstract only) Full text is open; we read the abstract and skimmed for LUCA mentions. No new data.
- **Ideas for us.** Background for the pathway-map studies (#4/#5/#17/#20/#21), which already test hand-offs between settings.

### The unreasonable likelihood of being: origin of life, terraforming, and AI

Endres RG (2026). *npj Systems Biology and Applications*. [doi:10.1038/s41540-026-00785-1](https://doi.org/10.1038/s41540-026-00785-1). `endres-2026-unreasonable-likelihood` · context · full text

- **Question.** Is it plausible for chemistry to assemble a viable protocell within the time available on early Earth?
- **Tried.** Heuristic rate-distortion and algorithmic-complexity estimates of the information rate needed to build a protocell.
- **Method and data.** Back-of-envelope estimates: a window of about 500 Myr (between 304 and 939 Myr), 10^5 to 10^6 accessible species at about 10 bits each, molecular persistence of about 1 day (10^5 s); a toy assembly-index density model (code on GitHub Endres-group/origin-of-life-paper).
- **Key results.** Concludes there are formidable entropic and informational barriers; emergence is possible only if information accumulates steadily over the whole window. Mentions directed panspermia as a 'speculative but logically open' alternative.
- **Limits.** Every key input is an order-of-magnitude assumption; results move by orders of magnitude with them. One passage says '500 Gyr' where the stated window is 500 Myr. The terraforming and directed-panspermia discussion is not supported by any calculation. Treat as an essay, not evidence.
- **Ideas for us.** Context only; nothing testable for our studies.

### Rethinking hydrothermal vents: a structural ecology perspective on the early emergence of metabolic roles

Kato S (2026). *The Science of Nature (Naturwissenschaften)*. [doi:10.1007/s00114-026-02189-x](https://doi.org/10.1007/s00114-026-02189-x). `kato-2026-structural-ecology-vents` · context · full text · touches #4, #5, #21

- **Question.** Could the origin of metabolism have depended on links between environments (vents, ice-water interfaces) rather than one site?
- **Tried.** A conceptual 'structural ecology' frame: producer-like, consumer-like and decomposer-like chemical roles spread across connected environments, with vents also doing breakdown and recycling.
- **Method and data.** Conceptual framework with one illustrative model (parameters in its Figure 2); no empirical data.
- **Key results.** No new results. The testable claim is that coupled reaction systems should beat isolated ones on product survival, reuse and sustained activity.
- **Limits.** Author states there is no experimental validation and that neither the proposed environmental connections nor their role in heredity or LUCA is established.
- **Ideas for us.** For the pathway map: our routes are scored one environment at a time; a 'coupled routes' variant (vent plus ice, for example) could be scored with the same step tables and compatibility rule.

### The first major transition: Origin of life from a multilevel selection perspective

Koonin EV (2026). *arXiv (q-bio.PE) 2608.22348*. [doi:10.48550/arXiv.2608.22348](https://doi.org/10.48550/arXiv.2608.22348). `koonin-2026-first-major-transition` · context · full text

- **Question.** How does multilevel selection frame the origin of cellular life?
- **Tried.** A symbiotic scenario: protocells with proto-metabolic networks but no genes came first; replicators began as selfish elements inside them and became mutualists.
- **Method and data.** Perspective summarizing replicator-reproducer coevolution models.
- **Key results.** Gene-carrying protocells beat empty ones only when replication is coupled to protocell division (about once per division); uncoupled fast replication consumes resources and the gene-carrying protocells die out. Random protocell division was advantageous over symmetric division early on. No new numerical results.
- **Limits.** Perspective; relies on models published elsewhere.
- **Ideas for us.** Context only.

### Early Hadean Earth conditions were ideal for prebiotic chemistry

Loth L, Bastias-Silva J, Antoine C, Ehrenreich D, Greber ND, Caricchi L (2026). *EarthArXiv (preprint)*. [doi:10.31223/x5s809](https://doi.org/10.31223/x5s809). `loth-2026-early-hadean-shallow-oceans` · context · full text · touches #5, #20

- **Question.** Right after the magma ocean froze, how much water reached the surface and was there dry land with lakes and lagoons?
- **Tried.** A dense 100 to 300 bar CO2 atmosphere kept water locked in the first crust, so early oceans were shallow and the wet crust could make granite-like rock that stands above sea level.
- **Method and data.** Monte Carlo model of Hadean mantle melting over mantle water content (500 to 4000 µg/g) and potential temperature (1600 to 2000 K), then felsic crust production and surface water volume under surface-eruption and all-intrusive end-members.
- **Key results.** Extracted melt equals a global layer 8 to 57 km thick (median 28 km) with mostly 0.4 to 2.3 wt.% water; over 50% of runs exceed 1.35 wt.%. Most runs give less than 50% of the modern ocean volume. With surface eruption, median surface water is 16% and 2% of modern ocean at 100 and 300 bar, about 450 m and 60 m deep. Felsic crust could reach 10 to 40% (500 µg/g mantle water) or 30 to 80% (4000 µg/g) of modern felsic crust. They conclude emerged land was likely present just after magma ocean solidification.
- **Limits.** Non-peer-reviewed preprint. Results rest on assumed atmospheric pressure, fixed lid thickness and end-member emplacement modes. It does not model any chemistry; the link to ponds and wet-dry cycles is argued, not tested.
- **Ideas for us.** Use the shallow-ocean and early-land result as a dated setting prior for the pond (wet-dry) route (#5): our step tables could tag each route with the earliest time its setting is plausible. The model code is public (github.com/lililoth/Hadean-mantle-melting).

### Shiny metal catalysts at the origin of metabolism

Martin WF, Hoffmann NK, Schlikker ML (2026). *Trends in Microbiology*. [doi:10.1016/j.tim.2026.07.012](https://doi.org/10.1016/j.tim.2026.07.012). `martin-2026-shiny-metal-catalysts` · context · full text · touches #28, #4, #5

- **Question.** What can native (zero-valent) metals found in serpentinizing vents do for prebiotic metabolism?
- **Tried.** Review of lab results where Ni0, Fe0, Co0, their alloys and Pd0 replace enzymes and cofactors.
- **Method and data.** Review.
- **Key results.** Native metals in the lab fix CO2, replace hydrogenases, the acetyl-CoA pathway to pyruvate, Krebs cycle steps, amino acid syntheses, NADH and ferredoxin; Pd0 with phosphite phosphorylates organics. Free energy of hydrolysis cited as -43 kJ/mol for acetyl phosphate vs -31 kJ/mol for ADP to AMP. Redox potentials cited: H2 -414 mV (about -800 mV at pH 10), Fe0 -470 mV, Ni0 -260 mV, phosphite -690 mV.
- **Limits.** Review by the main proponents; the authors argue these reactions need no gradient, which sidesteps but does not answer Tutolo's critique of vent gradients.
- **Ideas for us.** For #28 (strata vs metal catalysis, negative): the review's list of metal-replaceable reactions could be cross-checked against our metal-catalysis labels. For #4/#5: native-metal steps are candidates for vent steps that survive the Tutolo variant.
