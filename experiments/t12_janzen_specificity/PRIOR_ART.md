# T12 prior art: has anyone tested the Janzen 2022 activity-specificity link against the background floor or noise?

Written 2026-11-25 by the T12 prep agent. No real test statistic was computed. The only pairing of activity with specificity seen so far is the paper's own Table 1, reproduced in `gate`.

"Opened" means I fetched the text in this session and read the passage quoted. "Abstract only" means I read the abstract and nothing else. "Title only" means I saw the title in a list. Title-only papers carry no claim here.

All requests used the User-Agent `open-research-site/1.0` and carried no personal name or email. Saved responses are in `raw/prior_art/`, `raw/europepmc/`, `raw/esm/` and `raw/github/` (all gitignored). A search that finds nothing is weak evidence.

## Short answer

1. **No reanalysis found.** None of the citing papers re-tests the activity-specificity correlation, against a floor, against noise or in any other way. Europe PMC lists 19 citing records; OpenCitations and Crossref add 6 more. I read the abstract of every one that has an abstract. Two have none (a 2025 reference-module chapter and an Angewandte German-edition duplicate); I saw them by title only.
2. **The paper did not test it against the floor or against noise.** The promiscuity index is computed on catalytic enhancement r = rate / background, so a sequence at the background floor has r near 1 on every substrate and an index near 1 by construction. The paper's test is Pearson and Spearman of total activity against the index over all 1,954 sequences of each family (Table 1). It reports no null that keeps the floor, and no correction for the fact that total activity and the index come from the same noisy cells.
3. **arXiv has no reanalysis.** Eight queries found 4 hits, none related. One citing paper has an arXiv version (arXiv:2405.10911, on proofreading); it does not touch ribozyme specificity.
4. **The study is not settled by prior art.** It goes ahead.

## What Janzen 2022 says (opened)

Janzen, Shen, Vázquez-Salazar, Liu, Blanco, Kenchel, Chen 2022, "Emergent properties as by-products of prebiotic evolution of aminoacylation ribozymes", Nat. Commun. 13:3631, doi:10.1038/s41467-022-31387-0, PMID 35752631, PMC9233669. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9233669/fullTextXML`, saved as `raw/europepmc/PMC9233669_fulltext.xml` (sha256 `9eb3620710c011e9ff94045e65cb73f7aa68dc005de2518b12ad6c7179698df7`).

- The claim (abstract): "Furthermore, ribozyme activity was positively correlated with specificity, indicating that selection for increased activity would also lead to increased specificity."
- The index (Results): "The promiscuity index … is a normalized entropy which describes the evenness of the distribution of rates across different substrates. The promiscuity index Is ranges from 0 to 1, such that sequences that are completely promiscuous, having equal activity on all substrates, would have Is = 1, and sequences completely specific to one substrate would have Is = 0. Promiscuity was observed to decrease as overall activity increased for all families (Fig. 4 and Supplementary Fig. 7)."
- The rate used (Results): "In analogy with catalytic power used to characterize enzymes, we determined catalytic enhancement, i.e., the ratio of catalyzed to background reaction rates." And: "The background rate was 0.55 ± 0.18 M−1min−1 (μ ± σ) … the measured background rate was found to correspond to the center of a low-activity peak".
- The index's inputs (Methods): "Promiscuity indices were calculated using the calculator available at http://hetaira.herokuapp.com/. Due to the single-turnover nature of the aminoacylation ribozymes studied here, promiscuity indices are calculated using catalytic enhancement values instead of the catalytic efficiency as originally described by Nath and Atkins."
- The test (Table 1 caption): "Correlations between overall catalytic activity and specificity for each ribozyme family (Pearson's R and Spearman's ρ; n = 1954, p-values < 10−95 in each case (two-sided))."
- The threshold (Results): "An activity threshold of rt = 5 was chosen for two reasons. First, this threshold is two-fold more than the estimated 95% range for background activity (Supplementary Fig. 4, Supplementary Table 2), so values of rs > 5 are statistically significantly greater than the normalized background rate."
- The co-option counts, which this study uses only as a published structure count (Results): "(1029 sequences in Family 2.1; 853 sequences in Family 2.2) … Families 1A.1, 1B.1, and 3.1, which contain more inactive sequences and generally preferred aromatic amino acids, had most sequences accepting only one (or zero) substrate". The same paragraph gives 254, 278 and 43 for 1A.1, 1B.1 and 3.1.
- The reading (Discussion): "Substrate preferences were amplified with increasing activity, resulting in a positive correlation between activity and substrate specificity."

Supplementary Information (`raw/esm/41467_2022_31387_MOESM1_ESM.pdf`, opened): "Supplementary Figure 7. Relationship of activity to promiscuity index Is, separated by family. These plots show the same data as Figure 4, with families plotted separately." No test is reported beyond Table 1.

The authors' scripts (GitHub `ichen-lab-ucsb/WFLIVM_k-Seq`, commit 6899073) were read as source only, never run. `BackgroundNormalizer.py` divides each k·A by the background; `PromIndex_TableMaker.py` and `PromIndexResultsMerger.py` prepare inputs for and merge outputs from the online calculator; `CoOptionCounterBarPlot.py` counts substrates with r > 5. No script computes a null.

The floor issue in one line: if r = 1 + A·p with A the activity above background and p a fixed preference profile, the index goes to 1 as A goes to 0 whatever p is. So a negative correlation between total activity and the index is expected on all 1,954 sequences even with no change in preference. The paper does not discuss this.

## Context papers (abstract only)

- Nath and Atkins 2008, Biochemistry, doi:10.1021/bi701448p, PMID 18081310, "A quantitative index of substrate promiscuity". The index's source. "Here we define a quantitative index of promiscuity (I) that can be calculated from the catalytic efficiencies of an enzyme toward a defined set of substrates." Defined on catalytic efficiencies, which have no floor at 1.
- Janzen, Blanco, Peng, Kenchel, Chen 2020, Chem. Rev., doi:10.1021/acs.chemrev.9b00620, PMID 32011135, "Promiscuous Ribozymes and Their Proposed Role in Prebiotic Evolution". Same group, earlier: "We suggest that while de novo ribozymes appear to be promiscuous in general, they are not obviously more promiscuous than more highly evolved or active sequences."
- Shen, Pressman, Janzen, Chen 2021, Nucleic Acids Res., doi:10.1093/nar/gkab199, PMID 33772580, the k-Seq methods paper. "Relative abundance, kinetic coefficients, and measurement noise were found to affect the measurement of each sequence. We introduced bootstrapping to robustly quantify the uncertainty in estimating model parameters". This is where the per-sequence bootstrap intervals used here come from. It does not discuss the index.
- Pressman et al. 2019, JACS, doi:10.1021/jacs.8b13298, PMID 30912655. The fitness landscape the families come from. No specificity analysis.
- Schmutzer, Dasmeh, Wagner 2024, J. Mol. Evol., doi:10.1007/s00239-024-10161-4, PMID 38470504. Promiscuity across BRENDA enzymes ("the promiscuity distribution of empirical enzymes is bimodal"). Not about this data.
- Peracchi and Polverini 2022, Molecules, doi:10.3390/molecules27041398, PMID 35209187. Discrimination indices from kcat/KM in transaminases. Not about this data.

## Searches

| Where | Query | Result |
|---|---|---|
| Europe PMC | `CITES:35752631_MED` | 19 records (one is a bioRxiv duplicate of the RNA 2023 paper) |
| OpenCitations (index v2) | citations of doi:10.1038/s41467-022-31387-0 | 25 entries. Beyond Europe PMC: Frontiers Appl. Math. Stat. 2024, Genes Genet. Syst. 2023 (PMID 37032071), BioSystems 2023 (PMID 36657560), a 2025 RNA World reference module, the Angewandte German-edition duplicate |
| Crossref | `is-referenced-by-count` for the DOI | 26 |
| Europe PMC | `CITES:35752631_MED AND (promiscuity OR specificity)` | 5 hits: JACS Au 2025, Nat. Commun. 2024 (chirality), NAR 2024 (T-boxzyme), RNA 2023 (epistasis), PNAS 2023 (Euplotes). None tests the link |
| Europe PMC | `CITES:35752631_MED AND (background OR noise OR artefact OR artifact OR reanalysis OR "re-analysis" OR entropy)` | 6 hits, all reviews or unrelated experiments |
| Europe PMC | `"promiscuity index" AND (background OR noise OR floor OR "measurement error" OR bias OR artefact OR artifact)` | 37 hits; the paper itself and unrelated fields (HLA, GPCRs, NRPS) |
| Europe PMC | `"promiscuity index" AND (activity OR "catalytic efficiency") AND (correlation OR correlated)` | 34 hits; same kind |
| Europe PMC | `(ribozyme OR ribozymes) AND (promiscuity OR specificity) AND activity AND (correlation OR "trade-off" OR tradeoff) AND (k-Seq OR "kinetic sequencing" OR "high-throughput")` | 775 hits; first 25 read by title: the paper and unrelated ribozyme work |
| Europe PMC | `"Nath" AND "Atkins" AND "promiscuity"` | 26 hits; none on ribozymes except the paper and the 2020 review |
| Europe PMC | `(specificity AND activity AND correlation) AND ("normalized entropy" OR "Shannon entropy") AND (enzyme OR ribozyme) AND (noise OR background OR "detection limit")` | 353 hits; first 25 by title, none relevant |
| Europe PMC | `("k-Seq" OR "kinetic sequencing") AND (ribozyme OR ribozymes)` | 12 hits; none reanalyses the specificity link |
| Europe PMC | `("k-Seq" OR "kinetic sequencing") AND (precision OR uncertainty OR "critical parameters" OR bootstrap)` | 29 hits; the methods paper (2020 preprint, 2021 NAR) and unrelated |
| Europe PMC | `(promiscuity OR specificity) AND (activity) AND ("detection limit" OR "background activity" OR "noise floor" OR "measurement noise") AND (entropy OR "promiscuity index")` | 1,503 hits; first 15 by title, none relevant |
| arXiv | `all:ribozyme AND all:promiscuity`; `all:aminoacylation AND all:ribozyme`; `all:"promiscuity index"`; `all:"kinetic sequencing" AND all:ribozyme`; `all:specificity AND all:activity AND all:correlation AND all:entropy AND all:enzyme AND all:noise`; `all:Janzen AND all:ribozyme` | 0 hits each |
| arXiv | `all:ribozyme AND all:specificity AND all:activity` | 3 hits, all unrelated (ion condensation, folding) |
| arXiv | `all:"k-Seq"` | 1 hit, unrelated (commutative algebra) |

## Citing papers read as abstracts (none is a reanalysis)

- Di Giulio 2023, BioSystems, doi:10.1016/j.biosystems.2023.104838, PMID 36657560. The only critique. It is about error minimisation, not specificity: "Finally, I criticize the opinion of Janzen et al. (2022) according to which their self-aminoacylating ribozyme system would have been capable of generating an error minimization of the genetic code as its emergent property."
- Charest et al. 2023, RNA, doi:10.1261/rna.079541.122 (and bioRxiv 10.1101/2023.05.22.541765). Epistasis on the ribozyme fitness landscape. No specificity test.
- Kenchel et al. 2024, Nat. Commun., doi:10.1038/s41467-024-52362-x. Chiral selectivity of 15 ribozymes; "chiral preference is conserved within sequence families". New data, not the activity-specificity link.
- JACS Au 2025, doi:10.1021/jacsau.5c00146. Metal-ion effects on the structure of two of these ribozymes (S-1A.1-a, S-2.1-a).
- Annu. Rev. Biophys. 2024, doi:10.1146/annurev-biophys-030822-025038, "Fitness Landscapes and Evolution of Catalytic RNA". A review.
- Acc. Chem. Res. 2024, doi:10.1021/acs.accounts.4c00174 (protocells and RNA); PNAS 2024, doi:10.1073/pnas.2321592121 (RNA-catalysed evolution); NAR 2024, doi:10.1093/nar/gkae151 (T-boxzyme); Chem. Sci. 2024, doi:10.1039/d4sc05317f (2'-OH reagents review); Angew. 2024, doi:10.1002/anie.202317997 (replicator fidelity); Prog. Biophys. Mol. Biol. 2024, doi:10.1016/j.pbiomolbio.2024.07.002 (major transitions); Nat. Chem. 2025, doi:10.1038/s41557-024-01698-4 (frameworks review); Trends Genet. 2025, doi:10.1016/j.tig.2025.02.004 (translation factors); bioRxiv 2025, doi:10.1101/2025.06.16.660049 (RNAGym benchmarks); bioRxiv 2026, doi:10.64898/2026.01.27.701630 (peptide catalyst in yeast); Science 2026, doi:10.1126/science.adt1275 (proofreading, arXiv:2405.10911); PNAS 2023, doi:10.1073/pnas.2221683120 (Euplotes code); JACS 2023, doi:10.1021/jacs.2c12497 (lysine peptides); In Silico Biol. 2023, doi:10.3233/isb-220253 (speciation); Genes Genet. Syst. 2023, doi:10.1266/ggs.22-00085 (genetic-code hypothesis); Front. Appl. Math. Stat. 2024, doi:10.3389/fams.2024.1340640 (codon logic). Each cites the paper for background. None re-tests specificity.
- Title only: "The RNA World Hypothesis: Past Triumphs, Current Challenges and Future Questions" (Reference Module in Life Sciences, 2025, doi:10.1016/b978-0-443-15750-9.00105-1); the Angewandte German edition, doi:10.1002/ange.202317997.
