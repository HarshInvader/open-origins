# Reporting audit (task #31): within a paper, prebiotic syntheses report step-end conditions about as well as Beilstein J Org Chem. The sealed "reporting gap" predictions fail.

**Verdict: negative.** P1, P2 and P3 fail. P4 holds. Reliability was high (mean kappa 0.95), so the kill rule does not fire and the failures are findings, not noise.

Prereg: `docs/prereg/reporting_audit.md`, sha `fd412e97…`, sealed 2026-11-19T06:14Z before any paper was drawn.

**Sample.**
- Prebiotic set: 40 papers, 96 hand-offs, 57 of them aqueous. The query returned 264 hits.
  - Up to the 40th inclusion, 142 were taken in seed-0 order.
  - 61 were excluded at title/abstract, mostly nutrition or microbiome "prebiotics".
  - 81 were screened in full text, and 41 of those were excluded, mostly single-step (E2).
- Comparison set: 20 Beilstein J Org Chem papers, 83 hand-offs. The query returned 215 hits; 22 were screened and 2 excluded.
- Every screened paper, its DOI and the reason for any exclusion are in `screening.csv`.

## Sealed predictions
| | Prediction | Result | Verdict |
|---|---|---|---|
| P1 | Median per-paper fraction of prebiotic hand-offs with end pH reported is < 0.30 | **1.00** (bootstrap 95% CI 0.33-1.00; 29 papers with an aqueous hand-off). pH is reported at 68% of aqueous hand-offs (39/57), and in 15 of 29 papers at every one. | **fails** |
| P2 | < 20% of prebiotic papers state carried-over / isolated / fresh for every input | **90%** (36/40; Wilson 95% CI 77-96%) | **fails** |
| P3 | Prebiotic share of hand-offs with all four numeric items (pH or non-aqueous, T, concentration, solvent) is below the comparison set's, CI excluding 0 | 28.1% vs 28.9%, diff **−0.008**, 95% CI −0.17 to +0.16 | **fails** (no difference) |
| P4 | No year trend: Spearman \|rho\| < 0.2 | rho = 0.19 (p = 0.25, n = 40) | holds (descriptive) |

**What P3 could have detected.** The bootstrap SE of the difference is 0.084, so a gap of about 0.23 (23 percentage points) would have been detected with 80% power. Smaller gaps cannot be excluded.

**Sensitivity analyses (sealed, not used for verdicts).**
- Counting `S` as reported does not change P1 or P3.
- Counting bare "rt" as a temperature: diff −0.21, CI −0.37 to −0.06.
  - The comparison set then pulls ahead. Its end_T is mostly missing only because BJOC writes bare "rt" (36 of 83 hand-offs).
- Counting non-aqueous hand-offs as pH not reported (NA strict): prebiotic is *ahead*, +0.16 (CI 0.06 to 0.27). Organic steps in BJOC never report pH.
- Per-paper means instead of pooled hand-offs: diff −0.009 (CI −0.18 to 0.17).
- **Conclusion.** The sign of P3 depends on two coding conventions (bare rt, and NA for pH). The sealed primary is a null.

## Item by item (share of hand-offs reported)
| Item | Prebiotic (96) | BJOC (83) | Diff (95% CI, paper bootstrap) |
|---|---|---|---|
| End pH (of aqueous hand-offs) | 68% (39/57) | 7% (1/14) | — |
| End temperature, numeric | 40% | 42% | −0.03 (−0.22, 0.17) |
| End concentration/amount of carried product | **59%** (54% of aqueous) | **89%** | **−0.30 (−0.47, −0.12)** |
| Solvent / medium named | 95% | 100% | −0.05 (−0.12, 0.00) |
| Carried / isolated / fresh stated for every input | 95% | 96% | −0.02 (−0.08, 0.05) |
| Workup or "used directly" described | 90% | 94% | −0.04 (−0.15, 0.06) |
| Step n+1 demonstrated with an authentic or commercial sample of step n's product | 7% (7/96; 6 unclear) | 1% | — |

The only clear exploratory gap is **concentration or amount of the carried product at the end of a step**. Prebiotic aqueous steps often give a yield by NMR or HPLC, but not the volume, scale or final concentration of the mixture handed on.

## Reliability
A fresh, blind subagent re-scored 10 papers drawn with seed 1 (7 prebiotic, 3 comparison; 32 hand-offs). It was given the primary hand-off list.

| Item | kappa | Agreement |
|---|---|---|
| end pH | 1.00 | 8/8 non-NA pairs; NA calls agree 30/32 |
| end T | 0.76 | 29/32 |
| end concentration | 0.93 | 31/32 |
| solvent | 1.00 | 32/32 |
| carry | 1.00 | 32/32 |
| workup | 1.00 | 32/32 |

- **Mean kappa 0.95**, above the 0.6 kill threshold.
- Caveat: solvent, carry and workup were Y in almost every row for both coders. Their kappa of 1.0 reflects near-constant data, under the sealed convention.
- Caveat: the pH kappa rests on 8 pairs.
- This tests item scoring only, not segmentation. #29 showed segmentation is where coders split.

## How this squares with #29
#29 could check pH at only 2-4 of 17-20 hand-offs. Those were hand-offs **between papers and between labs**: a route stitched from several publications, where step n's end state and step n+1's start state are never written in the same place.

Within a single paper, the hand-offs are mostly reported. pH, solvent, carry status and workup are each above two-thirds. So the gap #29 hit is a **gap between papers, not within them**. A within-paper reporting checklist will not close it on its own. What would close it is stating the end state of a step in a form the next lab can test against.

Also, 16 of the 40 prebiotic papers have only one hand-off in their main sequence. Most "multi-step" prebiotic papers are short.

## Limits
- **Coding.** One primary coder per paper (Sonnet subagents, given only the codebook) and a blind second coder on 10 papers. Eligibility (E2, at least one hand-off) was judged by the primary coders.
  - Some calls were generous. PMC9884078 counts washing and HF treatment between CVD cycles as steps, and PMC8979813 and PMC8115318 are marked borderline.
- **Lenient pH definition, as sealed.** `E` includes "held at a stated buffer pH". A buffered step's pH after hours at 70-100 °C, or after a dry-down, is assumed rather than measured. A stricter "measured end pH" item would score lower. That item was not sealed, so it is not tested here.
- **The comparison set is one journal.** BJOC was chosen for open access, and only 14 of its 83 hand-offs are aqueous, so pH barely enters its all-four share. Organic synthesis and aqueous prebiotic chemistry differ in which items matter.
- **Sources.** The main text and the open SI came from the Europe PMC `supplementaryFiles` endpoint. 2 of the 60 included papers had SI zips with no text files, and items found only in figure images were missed.
- **Sampling frame.** It is defined by keywords. The prebiotic query is dominated by nutrition papers (stage-1 exclusions). Prebiotic papers outside PMC open access are not represented, including most of the Sutherland and Powner Nature/Science papers used in #21 and #29.
- **Power.** It is modest, with n = 40 + 20. P3 could miss a true gap below about 0.23.

## Draft reporting checklist (8 items, derived from the data)
The checklist is ordered by where the data show a gap, or where #29 showed a cross-paper break.
1. **Concentration of the carried product at the end of each step.** Give it in mM (or the amount and volume), not only the yield. This is the main measured gap: 54% vs 89%.
2. **End temperature as a number.** Do not write "rt"; this is missing in about 60% of hand-offs in both sets.
3. **Measured pH at the end of each aqueous step,** after heating, dry-down or additions, not only the buffer's nominal pH.
4. **Source of each next-step input.** State whether it was carried in the crude mixture, isolated (how, and with what loss), or a commercial or authentic sample.
   - Flag "authentic" explicitly. It occurred at 7 of 96 prebiotic hand-offs and was unclear at 6 more.
5. **Medium at the end of the step:** solvent, buffer and salts with concentrations, and whether a dry film or a residue was rehydrated (with what, and what volume).
6. **Workup between steps,** or an explicit "same pot, no workup".
7. **Co-products and leftover reagents carried forward,** with approximate amounts. This is what turns a same-pot claim into a checkable one; it was not scored here.
8. **A step-state table in the SI.** One row per step, with columns for items 1-7. This lets a route that spans papers be checked across papers.
   - That is where #29 failed.

## Files
- `sample.py`: frame and seed-0 order.
- `frame_*.csv`, `stage1.py` and `stage1_prebiotic.csv`: title/abstract screen.
- `fetch_ft.py`: full text and SI.
- `codebook.txt`: the only instructions coders received.
- `batches/`: raw coder output.
- `merge.py`: the first 40/20 eligible papers by rank.
- `screening.csv`, `extraction.csv`.
- `rel_sample.py`, `reliability.csv`.
- `audit.py`: stats, with a planted check that recovered a planted −0.3 difference as −0.26 with CI excluding 0, and a planted 0 with CI including 0.
- `results.json`, `ledger_rows.csv`.

Richert 2018 (doi:10.1038/s41467-018-07219-5) is cited as in #29, which opened its abstract. The 60 papers below were opened as full text by the coders (Europe PMC).

## Sampled papers (included)

**prebiotic**

| rank | PMCID | DOI | year | journal | title | hand-offs |
|---|---|---|---|---|---|---|
| 1 | PMC6486662 | 10.1089/ast.2018.1935 | 2019 | Astrobiology | A Prebiotic Synthesis of Canonical Pyrimidine and Purine Ribonucleotides. | 1 |
| 6 | PMC12258671 | 10.1002/anie.202507248 | 2025 | Angew Chem Int Ed Engl | From Amino Acids to α-Keto Acids via β-Elimination and Transamination Initiates a Pathway to Prebiotic Reaction Networks. | 2 |
| 7 | PMC6506141 | 10.1021/jacs.8b12331 | 2019 | J Am Chem Soc | Length-Selective Synthesis of Acylglycerol-Phosphates through Energy-Dissipative Cycling. | 3 |
| 8 | PMC6616635 | 10.3390/life9020040 | 2019 | Life (Basel) | Chemistry of Homocysteine Thiolactone in A Prebiotic Perspective. | 5 |
| 11 | PMC11897787 | 10.1039/d5ra00205b | 2025 | RSC Adv | Role of metal(ii) hexacyanocobaltate(iii) surface chemistry for prebiotic peptides synthesis. | 1 |
| 14 | PMC9753540 | 10.1021/acsomega.2c05754 | 2022 | ACS Omega | Multicomponent Synthesis of Diaminopurine and Guanine PNA's Analogues Active against Influenza A Virus from Prebiotic Compounds. | 2 |
| 15 | PMC8851484 | 10.1073/pnas.2116840119 | 2022 | Proc Natl Acad Sci U S A | Nonenzymatic assembly of active chimeric ribozymes from aminoacylated RNA oligonucleotides. | 4 |
| 19 | PMC2984373 | 10.1021/ja108197s | 2010 | J Am Chem Soc | Chemoselective multicomponent one-pot assembly of purine precursors in water. | 1 |
| 20 | PMC5454461 | 10.1038/ncomms15270 | 2017 | Nat Commun | Divergent prebiotic synthesis of pyrimidine and 8-oxo-purine ribonucleotides. | 5 |
| 23 | PMC7616004 | 10.1016/j.chempr.2024.02.001 | 2024 | Chem | A prebiotic Krebs cycle analog generates amino acids with H2 and NH3 over nickel. | 3 |
| 29 | PMC9033569 | 10.1039/d1ra02379a | 2021 | RSC Adv | Meteorite-catalyzed intermolecular trans-glycosylation produces nucleosides under proton beam irradiation. | 1 |
| 32 | PMC9776562 | 10.1021/acs.langmuir.2c02106 | 2022 | Langmuir | Emergence of Order in Origin-of-Life Scenarios on Mineral Surfaces: Polyglycine Chains on Silica. | 2 |
| 37 | PMC9296462 | 10.1038/s41598-022-15753-y | 2022 | Sci Rep | Borate-guided ribose phosphorylation for prebiotic nucleotide synthesis. | 1 |
| 40 | PMC5585222 | 10.1038/s41467-017-00463-1 | 2017 | Nat Commun | Emergence of native peptide sequences in prebiotic replication networks. | 2 |
| 41 | PMC10817532 | 10.3390/life14010108 | 2024 | Life (Basel) | From the RNA-Peptide World: Prebiotic Reaction Conditions Compatible with Lipid Membranes for the Formation of Lipophilic Random Peptides in the Presence of Short Oligonucleotides, and More. | 3 |
| 43 | PMC9634692 | 10.1021/acs.biochem.0c00943 | 2021 | Biochemistry | A Potential Role for Aminoacylation in Primordial RNA Copying Chemistry. | 3 |
| 45 | PMC5510716 | 10.1039/c7cc00693d | 2017 | Chem Commun (Camb) | A new and potentially prebiotic α-cytidine derivative. | 4 |
| 46 | PMC6617062 | 10.3390/life9020052 | 2019 | Life (Basel) | Prebiotic Sugar Formation Under Nonaqueous Conditions and Mechanochemical Acceleration. | 1 |
| 47 | PMC9884078 | 10.1021/acs.jpcb.2c07382 | 2023 | J Phys Chem B | Polypeptide Chain Growth Mechanisms and Secondary Structure Formation in Glycine Gas-Phase Deposition on Silica Surfaces. | 5 |
| 49 | PMC4037592 | 10.1007/s00239-014-9617-0 | 2014 | J Mol Evol | Conversion of biosynthetic precursors of RNA to those of DNA by photoredox chemistry. | 1 |
| 55 | PMC9169909 | 10.1073/pnas.2116429119 | 2022 | Proc Natl Acad Sci U S A | Freeze-thaw cycles enable a prebiotically plausible and continuous pathway from nucleotide activation to nonenzymatic RNA copying. | 1 |
| 56 | PMC11575587 | 10.1039/d4sc05362a | 2024 | Chem Sci | Mg2+-driven selection of natural phosphatidic acids in primitive membranes. | 2 |
| 58 | PMC7826252 | 10.1093/nar/gkaa1215 | 2021 | Nucleic Acids Res | Structural interpretation of the effects of threo-nucleotides on nonenzymatic template-directed polymerization. | 1 |
| 59 | PMC5940729 | 10.1038/s41467-018-04147-2 | 2018 | Nat Commun | Mimicking the surface and prebiotic chemistry of early Earth using flow chemistry. | 2 |
| 60 | PMC3548433 | 10.1021/ja311164j | 2013 | J Am Chem Soc | Synthesis of N3'-P5'-linked phosphoramidate DNA by nonenzymatic template-directed primer extension. | 3 |
| 64 | PMC7005209 | 10.3389/fchem.2020.00041 | 2020 | Front Chem | Deep Eutectic Solvents as Media for the Prebiotic DNA-Templated Synthesis of Peptides. | 5 |
| 65 | PMC12519194 | 10.1073/pnas.2500503122 | 2025 | Proc Natl Acad Sci U S A | Protopeptide backbone affects assembly in aqueous solutions. | 1 |
| 68 | PMC8139960 | 10.1038/s41467-021-23300-y | 2021 | Nat Commun | 2,6-diaminopurine promotes repair of DNA lesions under prebiotic conditions. | 1 |
| 70 | PMC8630799 | 10.1021/jacs.1c09253 | 2021 | J Am Chem Soc | Quantitative Difference in Solubility of Diastereomeric (2H/1H)-Isotopomers. | 4 |
| 79 | PMC6172253 | 10.1038/s41467-018-06374-z | 2018 | Nat Commun | Selective prebiotic conversion of pyrimidine and purine anhydronucleosides into Watson-Crick base-pairing arabino-furanosyl nucleosides in water. | 1 |
| 94 | PMC5770463 | 10.1038/s41467-017-02742-3 | 2018 | Nat Commun | A prebiotic template-directed peptide synthesis based on amyloids. | 1 |
| 96 | PMC9586328 | 10.1073/pnas.2212642119 | 2022 | Proc Natl Acad Sci U S A | Aqueous microdroplets enable abiotic synthesis and chain extension of unique peptide isomers from free amino acids. | 1 |
| 100 | PMC11044211 | 10.1021/acsomega.3c09949 | 2024 | ACS Omega | A Prebiotic Genetic Nucleotide as an Early Darwinian Ancestor for Pre-RNA Evolution. | 3 |
| 117 | PMC9241005 | 10.1021/jacsau.2c00087 | 2022 | JACS Au | Water-Based Dynamic Depsipeptide Chemistry: Building Block Recycling and Oligomer Distribution Control Using Hydration-Dehydration Cycles. | 5 |
| 123 | PMC12745811 | 10.1073/pnas.2516418122 | 2025 | Proc Natl Acad Sci U S A | Interstep compatibility of a model for the prebiotic synthesis of RNA consistent with Hadean natural history. | 2 |
| 132 | PMC9040849 | 10.1039/d1ra05240c | 2021 | RSC Adv | Aminomalononitrile inspired prebiotic chemistry as a novel multicomponent tool for the synthesis of imidazole and purine derivatives with anti-influenza A virus activity. | 3 |
| 134 | PMC8115318 | 10.1039/d1sc01250a | 2021 | Chem Sci | Prebiotic access to enantioenriched glyceraldehyde mediated by peptides. | 1 |
| 138 | PMC8433156 | 10.1038/s41467-021-25668-3 | 2021 | Nat Commun | The chemistry of branched condensed phosphates. | 3 |
| 139 | PMC4959843 | 10.7554/elife.17756 | 2016 | Elife | Nonenzymatic copying of RNA templates containing all four letters is catalyzed by activated oligonucleotides. | 5 |
| 141 | PMC8979813 | 10.1038/s41557-022-00890-8 | 2022 | Nat Chem | Charge-density reduction promotes ribozyme activity in RNA-peptide coacervates via RNA fluidization and magnesium partitioning. | 1 |

**comparison**

| rank | PMCID | DOI | year | journal | title | hand-offs |
|---|---|---|---|---|---|---|
| 0 | PMC6604749 | 10.3762/bjoc.15.138 | 2019 | Beilstein J Org Chem | Selenophene-containing heterotriacenes by a C-Se coupling/cyclization reaction. | 3 |
| 2 | PMC6244240 | 10.3762/bjoc.14.260 | 2018 | Beilstein J Org Chem | Synthesis of pyrrolidine-based hamamelitannin analogues as quorum sensing inhibitors in Staphylococcus aureus. | 5 |
| 3 | PMC8450977 | 10.3762/bjoc.17.142 | 2021 | Beilstein J Org Chem | Transition-metal-free intramolecular Friedel-Crafts reaction by alkene activation: A method for the synthesis of some novel xanthene derivatives. | 4 |
| 4 | PMC12667733 | 10.3762/bjoc.21.202 | 2025 | Beilstein J Org Chem | Efficient solid-phase synthesis and structural characterization of segetalins A-H, J and K. | 3 |
| 5 | PMC2956404 | 10.3762/bjoc.6.81 | 2010 | Beilstein J Org Chem | Preparation of aminoethyl glycosides for glycoconjugation. | 4 |
| 6 | PMC4901869 | 10.3762/bjoc.12.89 | 2016 | Beilstein J Org Chem | A robust synthesis of 7,8-didemethyl-8-hydroxy-5-deazariboflavin. | 5 |
| 7 | PMC5082451 | 10.3762/bjoc.12.210 | 2016 | Beilstein J Org Chem | Regiocontroled Pd-catalysed C5-arylation of 3-substituted thiophene derivatives using a bromo-substituent as blocking group. | 1 |
| 8 | PMC11693970 | 10.3762/bjoc.20.273 | 2024 | Beilstein J Org Chem | Synthesis of acenaphthylene-fused heteroarenes and polyoxygenated benzo[j]fluoranthenes via a Pd-catalyzed Suzuki-Miyaura/C-H arylation cascade. | 5 |
| 9 | PMC6774081 | 10.3762/bjoc.15.219 | 2019 | Beilstein J Org Chem | Synthesis of acremines A, B and F and studies on the bisacremines. | 5 |
| 10 | PMC6122332 | 10.3762/bjoc.14.196 | 2018 | Beilstein J Org Chem | A general and atom-efficient continuous-flow approach to prepare amines, amides and imines via reactive N-chloramines. | 2 |
| 11 | PMC4142848 | 10.3762/bjoc.10.176 | 2014 | Beilstein J Org Chem | Concise total synthesis of two marine natural nucleosides: trachycladines A and B. | 5 |
| 12 | PMC4778503 | 10.3762/bjoc.12.39 | 2016 | Beilstein J Org Chem | Diastereoselective synthesis of new O-alkylated and C-branched inositols and their corresponding fluoro analogues. | 5 |
| 13 | PMC8722398 | 10.3762/bjoc.17.207 | 2021 | Beilstein J Org Chem | Stepwise PEG synthesis featuring deprotection and coupling in one pot. | 5 |
| 14 | PMC3458728 | 10.3762/bjoc.8.123 | 2012 | Beilstein J Org Chem | Asymmetric total synthesis of smyrindiol employing an organocatalytic aldol key step. | 5 |
| 15 | PMC5942382 | 10.3762/bjoc.14.74 | 2018 | Beilstein J Org Chem | Methyl isocyanide as a convertible functional group for the synthesis of spirocyclic oxindole γ-lactams via post-Ugi-4CR/transamidation/cyclization in a one-pot, three-step sequence. | 2 |
| 16 | PMC4222376 | 10.3762/bjoc.10.247 | 2014 | Beilstein J Org Chem | Synthesis and immunological evaluation of protein conjugates of Neisseria meningitidis X capsular polysaccharide fragments. | 5 |
| 18 | PMC5727846 | 10.3762/bjoc.13.257 | 2017 | Beilstein J Org Chem | A semisynthesis of 3'-O-ethyl-5,6-dihydrospinosyn J based on the spinosyn A aglycone. | 5 |
| 19 | PMC8450941 | 10.3762/bjoc.17.152 | 2021 | Beilstein J Org Chem | Synthesis of phenanthridines via a novel photochemically-mediated cyclization and application to the synthesis of triphaeridine. | 4 |
| 20 | PMC6369998 | 10.3762/bjoc.15.33 | 2019 | Beilstein J Org Chem | Synthesis of C 3-symmetric star-shaped molecules containing α-amino acids and dipeptides via Negishi coupling as a key step. | 5 |
| 21 | PMC3678503 | 10.3762/bjoc.9.95 | 2013 | Beilstein J Org Chem | A versatile and efficient approach for the synthesis of chiral 1,3-nitroamines and 1,3-diamines via conjugate addition to new (S,E)-γ-aminated nitroalkenes derived from L-α-amino acids. | 5 |
