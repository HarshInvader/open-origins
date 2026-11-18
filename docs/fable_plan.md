> **Corrections after the citation audit (2026-11-18, experiments/research_sweep/RESULTS.md).** The plan below is kept as written; these override it.
> - QT45 net yield is about 0.2% over 72 days (from the paper), not the second-hand 0.02%.
> - Exponential replication of short RNAs by a ribozyme was shown by Attwater et al. 2025 (Nature Chemistry), so "no exponential growth yet" is wrong. L3 is still not met, because no whole replicator has been made from a setting's own feedstocks.
> - Only the measurable chiral amino acids in Bennu were racemic.
> - The magnetite route reaches about 60% enantiomeric excess at best, about 35% on average.
> - The assembly-index-as-grammar paper is Abrahão et al. (PLOS Complex Systems); Uthamacumaran's is in npj Systems Biology and Applications.
> - Wołos et al. 2020 does not show that cyanosulfidic chemistry needs ordered reagent delivery.

**Bottom Line**

The origin of life will not be "cracked" by end of 2027 in the full sense; I put that under 1 in 100. A laptop team can still hit a narrower, checkable goal: an audited pathway map with every gap named, plus pre-registered predictions confirmed by data published after the hash. I put that at roughly 1 in 8.

Claims with citations were checked by search today. Anything marked "(memory)" is from my recall and needs verifying before it goes on the site.

**1. Root Goal**

Split it in two, because the field has two different questions: "can chemistry do it?" and "how did it happen on Earth?".

- **R-full ("cracked").** One stated geochemical scenario and one pathway from its feedstocks to a system showing heritable variation in replication rate, meeting four tests:
  - Every step has a yield published by a lab other than us (the outside anchor).
  - Steps are compatible under a rule we hash in advance: each step's inputs must be reachable from the previous step's outputs by a named physical process, with no purified hand-offs.
  - A kinetic model fitted on steps 1..k predicts at least 3 held-out measurements published after the hash, within pre-set tolerance.
  - An independent red team fails to break it.
- **R-open (what we can move).** By 2027-12-31:
  - The pathway map exists for at least 4 scenarios, with every step scored.
  - At least 10 published claims are benched against nulls.
  - At least 3 hashed predictions are confirmed by later data, at least one of them about returned-sample chemistry or a new ribozyme landscape.
- **Rule carried over.** Our bench can refute a claim or score a pathway; only wet-lab or sample data from others can confirm.

**2. Claim Ladder**

- **L0, building blocks from a stated setting.** Largely met. Bennu's returned sample holds 33 amino acids, 14 of them proteinogenic, plus all five canonical nucleobases (Glavin, Dworkin et al. 2025, Nature Astronomy). Furukawa's team measured ribose at 0.097 nmol/g and glucose at 0.35 nmol/g, and found no deoxyribose (Furukawa et al. 2025, Nature Geoscience).
- **L1, activation and polymerisation under compatible conditions.** Partly met. Individual steps work; chaining them without purification is the weak point. A notable recent step is Singh, Powner et al. 2025 (Nature 644:933): several prebiotic routes to aminoacyl-thiols, and thioester-driven aminoacylation of ribonucleosides near neutral pH.
- **L2, template copying of function-length sequences.** Demonstrated under engineered conditions. Gianni, Holliger et al. 2026 (Science 391:1022) is the landmark: a 45-nucleotide ribozyme, QT45, copies RNA from trinucleotide triphosphates in mildly alkaline eutectic ice, and it made both a copy of itself and of its complementary template.
- **L3, sustained exponential self-replication from scenario feedstocks.** Not met. A forum reading of the QT45 paper puts the net gain at about 0.02% over 72 days; that figure is second-hand and must be checked against the paper.
- **L4, open-ended Darwinian evolution in a compartment.** Not met. The nearest result is Papastavrou, Horning & Joyce 2024 (PNAS 121:e2321592121), "RNA-catalyzed evolution of catalytic RNA"; I verified the citation, not the details.
- **H-track, historical link to LUCA.** Separate from L0-L4. LUCA is already a complex cell, so it constrains the end point, not the start.

**3. Theory Map**

- **RNA world.**
  - Riskiest prediction: small polymerase ribozymes are common in sequence space and can run a closed cycle.
  - For: QT45. Its authors argue that finding polymerase activity in so small a motif means such ribozymes are more frequent in sequence space than assumed.
  - Against: substrates are pre-activated triplets supplied by the experimenter; no exponential growth yet.
  - Status: strengthened at L2, open at L3.
- **Alkaline vents / metabolism first.**
  - Riskiest prediction: natural pH gradients across Fe(Ni)S barriers drive CO2 reduction well past formate.
  - For: Hudson et al. 2020 (PNAS), where formate vanished once the pH gradient was removed or much reduced. Altair et al. 2025 (JACS) report micromolar formic and acetic acid on the ocean side with Fe-S or Fe-Ni-S present.
  - Against: micromolar C1-C2 products are far from a metabolic network; nucleotide chemistry in vents remains weak (memory).
  - Status: strained beyond C2.
- **Warm ponds / wet-dry cycling.**
  - Riskiest prediction: cycling yields long, copyable polymers without hydrolysis winning.
  - I did not verify 2023-2026 papers this session; put this first in the research sweep.
  - Status: unscored.
- **Cyanosulfidic chemistry (Sutherland).**
  - Riskiest prediction: one UV-lit surface setting supplies nucleotide, amino acid and lipid precursors without incompatible steps.
  - Against: the network needs ordered delivery of reagents; Wołos et al. 2020 (Science) mapped such networks computationally (memory, verify).
  - Status: strong step by step, strained on continuity.
- **Peptide-RNA co-evolution.**
  - Riskiest prediction: uncoded aminoacylation becomes sequence-specific without enzymes.
  - For: Singh et al. 2025, in which aminoacyl-thiols pick RNA diols over amine nucleophiles, so aminoacylation beats uncoded peptide bonding.
  - Status: rising, with coding still unexplained.
- **Autocatalytic sets (RAF).**
  - Riskiest prediction: RAF sets in real metabolism are more than an artefact of network size and food-set choice.
  - For: Xavier et al. 2020 (Proc R Soc B), where cofactors relevant to the anaerobic network give a maxRAF of 1,335 reactions, a quarter of that network.
  - Against: one review objects that these networks are not catalytically closed and lean on the environment for catalysts as well as building blocks.
  - Status: untested against proper nulls; this is a prime bench target.
- **Assembly theory.**
  - Riskiest prediction: assembly index above about 15 at high copy number occurs only with life.
  - Against: Hazen et al. 2024 (J R Soc Interface), where mineral heteropolyanions such as those in ewingite and ilmajokite score above the proposed cutoff of 15. Uthamacumaran, Abrahão & Zenil 2024 (PLOS Complex Systems) hold that assembly index equals the size of a minimal context-free grammar, bounded by Shannon entropy and LZ-type compression.
  - Defence: Walker et al. 2024 object that Hazen's values are theoretical, from crystal structures of charged units that cannot be isolated in solution. Kempes et al. 2025 (npj Complexity) maintain that assembly index is not identical to computational complexity or compression measures.
  - Status: the threshold claim is strained; the dispute is unresolved.
- **Homochirality.**
  - Meteoritic delivery is strained: Bennu's chiral amino acids are racemic, matching Ryugu.
  - The magnetite spin-selectivity route (Ozturk, Liu, Sutherland & Sasselov 2023, Science Advances) is live but fragile: direct crystallisation gave no consistent selectivity, and recrystallisation averaged around 35% ee.
- **Lipid world.** Not verified this session; I recall no decisive 2023-2026 result.
- **Biosignature side note.** K2-18b DMS is not supported: a joint JWST reanalysis finds no statistical significance for DMS or DMDS (Luque et al. 2025, A&A).

**4. Bench The Published Claims**

- **LUCA gene content.** Moody et al. 2024 (Nat Ecol Evol 8:1654) infer that LUCA lived about 4.2 billion years ago as a complex anaerobic acetogen inside an ecosystem.
  - Re-test: how much of the gene set survives changes to the presence-probability cutoff, taxon sampling and transfer model.
  - Compare with Weiss et al. 2016 and the consensus of Crapitto et al. 2022.
  - Null: gene families with shuffled phyletic patterns at matched breadth.
- **RAF in metabolism.** Rerun the maxRAF on degree-preserving randomised networks and on random food sets of equal size. Report where the real network falls.
- **Network expansion.** Goldford et al. 2017 (Cell) phosphate-free core (memory): same randomisation null, plus a thermodynamic filter.
- **Assembly index.** On the Marshall et al. 2021 (Nat Commun) mass-spec data (memory), test whether assembly index separates biotic from abiotic better than molecular weight, heavy-atom count or LZ complexity alone.
- **Ribozyme landscapes.** Test "functional RNAs are common" claims against the selection bias of the starting library, using each paper's own read counts.
- **Pathway completeness.** Score each cyanosulfidic and vent step for condition compatibility with the previous step, rather than counting products made.
- **Chirality.** Meta-analyse reported enantiomeric excess in meteorites against contamination indicators. Bennu and Ryugu are the clean controls.

**5. Datasets And Tools**

- **Reactions:** Rhea (open), ModelSEED, BiGG, eQuilibrator for free energies. KEGG and MetaCyc bulk downloads are licensed; check terms before use.
- **LUCA:** Moody et al. supplementary data, eggNOG/COG, GTDB trees, ALE and GeneRax for reconciliation (small subsets only on a laptop).
- **Ribozymes:** QT45 has a deposit titled "Data and code from: A small polymerase ribozyme that can synthesize itself and its complementary strand"; also Rfam and older deep-mutational scans (memory: Pressman et al. 2019 JACS; Kobori & Yokobayashi 2016).
- **Sample return:** Bennu compound tables in the Glavin 2025 and Furukawa 2025 supplements; Astromat and JAXA DARTS for raw data (memory, verify access).
- **Chemistry:** Open Reaction Database, PubChem, RDKit, RetroRules for reaction rules.
- **Exoplanets:** MAST for JWST spectra; low priority, as it tests biosignature claims, not origins.

**6. Planted-Answer Controls**

- **LUCA.** Simulate gene families on a known tree with transfer, loss and duplication at published rates. The method must recover the planted ancestral set at our sample size, with stated precision and recall.
- **RAF and expansion.** Plant a known autocatalytic core in a randomised network. Detection must exceed the false-positive rate on networks with no plant.
- **Assembly index.** Blind-label known biotic and abiotic compounds matched on mass. Assembly index must beat the size-only classifier.
- **Ribozyme landscape.** Simulate a landscape with a known fraction of functional sequences and the paper's sampling depth. The estimator must recover that fraction.
- **Pathway scorer.** Insert a deliberately incompatible step, such as a pH 2 product fed to a pH 10 reaction. The scorer must flag it.

**7. First Tasks**

All are laptop-feasible unless noted.

- **M1, Latest research sweep.**
  - T1. Build the 2023-2026 paper ledger for every theory, with author, year, venue and DOI. Decisive: each claim marked verified or unverified. Start with wet-dry cycling and lipid world.
  - T2. Extract QT45 yields, rates and fidelity from the paper and deposit. Decisive: is net replication above or below 1 per cycle?
- **M2, Pathway map.**
  - T3. Encode cyanosulfidic, vent, pond and ice-RNA pathways as step tables (inputs, conditions, yield, source). Decisive: the count of unexplained hand-offs per pathway.
  - T4. Hash the compatibility rule, then score all pathways. Decisive: a ranked gap list.
- **M3, Bench.**
  - T5. RAF null test on Rhea-derived anaerobic networks. Decisive: the real maxRAF falls inside or outside the null's 95% range.
  - T6. Assembly index versus size null. Decisive: the difference in classification accuracy, with interval.
  - T7. LUCA robustness scan on a subsample of families. Decisive: the fraction of the acetogen call that survives. Laptop-feasible on a subset only.
- **M4, Controls.**
  - T8. Planted-core recovery for T5.
  - T9. Simulated-tree recovery for T7.
- **M5, Predictions.**
  - T10. Hash a prediction of relative abundances for compounds not yet reported from Bennu, derived from formose and Strecker kinetics. Decisive: later papers match or miss.
  - T11. Hash predicted fitness for unmeasured QT45 double mutants from the single-mutant data. Decisive: later scans confirm or refute.
- **M6, Red team.**
  - T12. An independent agent reruns T5-T7 from raw data without seeing our code.
  - T13. Audit every citation on the site against its DOI.

**8. Honest Odds**

- **R-full by 2027:** under 1 in 100.
- **R-open by 2027:** about 1 in 8. The limiting factor is whether confirming data appears in time.
- **What would raise them most:**
  - New Bennu or Ryugu compound tables released after our hash.
  - A lab reporting sustained exponential replication by a small ribozyme, which we could model in advance.
  - A wet lab agreeing to run one pre-registered test. That requires a human-sent request, not an automatic one.

**9. Site Pages That Differ**

- **Pathway map.** One row per step. Colour shows demonstrated, demonstrated with purified inputs, or missing. Conditions and source are shown per step.
- **Scenario cards.** Vent, pond, ice and impact, each with what it explains and what it cannot.
- **Two ladders.** "Can chemistry do it" and "what happened on Earth", shown separately.
- **Prediction ledger.** Hash, date, claim, and status (open, confirmed, failed).
- **Claim bench.** Each published claim with its null result and effect size.

**10. Blind Spots And Traps**

- **No single answer exists.** Unlike a script, several pathways may all work. Showing possibility is not showing history.
- **"Prebiotically plausible" is a judgement.** Fix the rule in advance or it will bend to favoured results.
- **Yields hide hand-offs.** Most published steps start from purified reagents.
- **LUCA is late.** It tells us little about the first replicator.
- **Topology is not kinetics.** A network containing an autocatalytic set says nothing about whether it runs.
- **Database bias.** Metabolic databases record modern biochemistry; nulls must respect that.
- **Contamination.** Any chirality or sample claim needs the blank data.
- **Agent error.** AI agents invent citations; T13 exists for that reason.
- **Laptop limits.** Full reconciliation of thousands of gene families will not fit; subsample and say so.
- **Multiple testing.** Many theories multiplied by many tests gives chance hits. Keep the project-wide ledger from day one.