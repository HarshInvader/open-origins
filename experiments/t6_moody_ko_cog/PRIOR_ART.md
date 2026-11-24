# T6 prior art: has anyone tested KO-to-COG rescue against re-run noise in Moody 2024?

Written 2026-11-24 by the T6 prep agent. No real rescue rate or flip rate was computed.

"Opened" means I fetched the text in this session and read the passage quoted. "Abstract only" means I read the Europe PMC abstract and nothing else. "Title only" means I saw the title in a search result. Title-only papers carry no claim here.

All requests used the User-Agent `open-research-site/1.0`. Saved responses are in `raw/prior_art/` and `raw/europepmc/`. A search that finds nothing is weak evidence.

## Short answer

1. **The claim is one sentence in Moody 2024, with no test attached.** The paper says KO splitting hides LUCA families and that the COG analysis was run "to account for this limitation". It reports no count of rescued families and no comparison with a re-run.
2. **The exact T6 design was not found.** I found no paper that compares Moody's KO and COG probabilities family by family, and none that uses the single-KO COGs as a test-retest group.
3. **The search was thin.** Europe PMC returned 502 or 503 on about half of the requests and needed retries. arXiv returned no entries. Of the 182 papers that cite Moody 2024, I screened titles only.

## What Moody 2024 says (opened)

Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11383801/fullTextXML`, saved as `raw/europepmc/PMC11383801_fulltext.xml`.

- Results: "…it has the drawback that some widespread gene families that were likely present in LUCA are divided into multiple KO families that individually appear to be restricted to particular taxonomic groups and inferred to have arisen later. To account for this limitation, we also performed an analysis of COG (Clusters of Orthologous Genes) gene families, which correspond to more coarse-grained functional annotations (Supplementary Data 2)."
- Methods, KO families: "Five independent sets of ML trees were then inferred using IQ-TREE 2 (ref. 86), using LG + F + G, with 1,000 ultrafast bootstrap replicates."
- Methods, COG families: "We also performed a COG-based clustering analysis in which COGs were assigned based on the modal COG identifier annotated for each KEGG gene family based on the results from EGGNOGMAPPER v.2 (ref. 89). These gene families were aligned, trimmed and one set of gene trees (with 1,000 ultrafast bootstrap replicates) was inferred using the same parameters as described above for the KEGG gene families."
- Supplementary Data 2 caption: "This table contains the results for the reconciliations of COG-based gene family clustering against the constrained focal species-tree topology."
- Results: "we identified a conservative subset of 399 KOs that were likely to be present in LUCA, with PPs ≥0.75, and found in both Archaea and Bacteria (Supplementary Data 1)". The gate reproduces 399.
- The only COG count in the main text is an overlap with an earlier study: "we find 81 overlapping COG gene families with the consensus dataset of ref. 7".

Two things follow for the design.

- The COG value is one run. The KO value is the median of five runs. The retest group therefore measures "one new run against the median of five", which is the comparison the merged families also get.
- The COG analysis used the constrained topology, so the matching KO column is `constrained_median`.

## Searches

| Where | Query | Result |
|---|---|---|
| Europe PMC | `DOI:10.1038/s41559-024-02461-1` | 1 hit, PMID 38997462 |
| Europe PMC | `"last universal common ancestor" AND reconciliation AND KEGG AND COG AND (merging OR splitting OR clustering)` | 6 hits: Moody 2024 and five unrelated to this test (ATP synthase dating, eggNOG 4.5, oxidative adaptations, lipid micelles) |
| Europe PMC | `(LUCA OR "last universal common ancestor") AND reconciliation AND (orthogroup OR "family definition" OR "over-split" OR "clustering granularity")` | 7 hits, none on LUCA family calls. Closest by title: a review of hierarchical orthologous groups (below) |
| Europe PMC | `(LUCA OR "last universal common ancestor") AND (reproducibility OR "run-to-run" OR "test-retest") AND (ALE OR reconciliation)` | 171 hits, all noise in the first 25 (clinical questionnaires; "ALE" and "LUCA" match other things) |
| Europe PMC | `Moody AND LUCA AND (reanalysis OR critique OR comment OR "matters arising")` | 58 hits, none a reanalysis of the gene-content tables in the first 25 |
| Europe PMC | citations of PMID 38997462, all 182, titles screened for COG, KEGG, ortholog, cluster, reconciliation, robust, gene content, gene family, LUCA, reanalysis | about 30 titles matched; none is a KO-against-COG comparison. Five were read as abstracts (below) |
| arXiv API | `all:"last universal common ancestor" AND all:reconciliation` | 0 entries |

The plan's own search, and the project library notes it cites for Szöllősi 2026, Csűrös 2026 and Williams 2023, stand as written in `docs/plans/next_studies_2026-11-24.md`. I did not reopen those papers.

## Closest papers (abstract only)

- **Szöllősi, Spang, Boussau, Williams 2026, preprint, doi:10.64898/2026.09.03.749268.** The abstract says reconciliation methods "tend to underestimate ancestral contents due to phylogenetic noise". It proposes a gene-content model to denoise reconstructions. It supports the idea that per-family calls are noisy. The abstract does not mention KO or COG clustering.
- **Huang et al. 2026, Nat. Commun., doi:10.1038/s41467-026-76386-7.** Archaeal root and the last archaeal ancestor by reconciliation. Not about family definition.
- **Sarton-Lohéac et al. 2025, J. Mol. Evol., doi:10.1007/s00239-025-10277-1.** A review of hierarchical orthologous groups. General background on family definition; no LUCA test.
- **Goldman, Fournier, Kaçar 2026, Cell Genomics, doi:10.1016/j.xgen.2026.101140.** A review of universal paralogs. Not this test.
- **Gagnon and Csűrös 2026, PNAS, doi:10.1073/pnas.2619901123.** A reply about transient genes in profile-based reconstruction. Europe PMC holds no abstract for it; title only.

Title only, from the citing list: "Reconstructing ancient genomes from gene counts: A robust likelihood framework with sampling bias correction" (PMID 42101992) and "A new LUCApedia database for data-driven research on early evolutionary history" (PMID 41510024).

## What is established and what T6 adds

- **Established inside this project:** the five KO runs disagree a great deal per family (`docs/RESEARCH_STATE.md`: 810 families differ by more than 0.5 between runs).
- **Not found anywhere:** a count of families that merging rescues, set against the same pipeline's re-run noise.
- **T6 adds** that count, and the test-retest reliability of a single-run call on identical alignments.

## Limits of this check

- Citing papers were screened by title. A paper that does this comparison in a supplement would be missed.
- bioRxiv and Google Scholar were not searched.
- The Europe PMC errors mean some queries ran once only.
