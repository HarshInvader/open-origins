# T9 prior art: has anyone checked DPANN's high loss rate in Huang 2026 against genome completeness?

Written 2026-11-24 by the T9 prep agent. No loss count was joined to completeness or to a clade label while this was written.

"Opened" means I fetched the full text in this session and read the passage quoted. "Abstract only" means I read the Europe PMC abstract and nothing else. "Title only" means I saw the title in a search result; title-only papers carry no claim here.

All requests used the User-Agent `open-research-site/1.0` and no name or email. Saved responses are in `raw/prior_art/`, `raw/europepmc/` and `raw/alerax_src/` (all gitignored). A search that finds nothing is weak evidence.

## Short answer

1. **Prior art does not settle the question.** No paper I found tests whether the DPANN loss excess in Huang 2026 survives a completeness check. Csűrös 2026 is the closest. It names the confound for DPANN and says it cannot be separated from copy numbers, but it uses a different 269-genome dataset and a different model (copy-number GLD, not reconciliation). It does not touch Huang's data.
2. **Csűrös 2026 sharpens the design.** It says that in a copy-number model, incompleteness is "perfectly absorbed by increased loss". So a test must look where incompleteness cannot reach easily: internal branches with several descendants. That is arm B of the plan.
3. **The AleRax source settles one point the plan got wrong.** In AleRax, a gene missing from an incomplete genome is still written to the event counts as a loss on that tip's branch. CheckM completeness changes the likelihood, not the bookkeeping. So tip-branch losses rise with incompleteness even when the correction works. The plan's arm A ("if the correction worked, the slope is 0") cannot be a negative control. Details below.
4. **One paper cites Huang 2026 (Nat Commun) and five cite its preprint.** None is a reanalysis of the loss rates, by abstract.

## What Huang et al. 2026 say (opened)

Huang et al. 2026, Nat. Commun., doi:10.1038/s41467-026-76386-7. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13473441/fullTextXML`, saved as `raw/europepmc/PMC13473441_fulltext.xml`.

- The claim: "Adding a DPANN-specific loss rate substantially improved reconciliation model fit (BIC: 3284636.6, Supplementary Data 10), and, as predicted, the DPANN loss rate was inferred to be higher than that for the other clades (DPANN: 0.40-0.45, other clades: 0.26-0.27)."
- How completeness entered: "To account for the incomplete nature of some MAGs, genome completeness estimates from CheckM v2 were used in reconciliation139 (Supplementary Data 1)."
- The software: "...were reconciled with 15 different rooted archaeal species trees (Fig. 1A) using the distinct reconciliation models implemented in AleRax v1.1.156".
- The 4-parameter model: "First, we introduced DPANN-specific rate classes: a different loss rate (DPANN:L; 4 parameters)..."
- The model behind the deposited event counts: "For ancestral genome content reconstruction, we allowed heterogeneous origination by estimating independent rates for the root, its two immediate descendants, and the DPANN lineage using --origination OPTIMISE, based on the reconciliation model with 72 parameters".
- Clade labels of that model: "...and for DPANN lineages (i.e., for each Micrarchaeota; B1Sed10-29; Iainarchaeota; Altiarchaeota; Undinarchaeota; Aenigmarchaeota; PWEA01; EX4484_52; Nanohaloarchaeota; SpSt-1190; parvarchaeal-related lineages; UBA10117; Pacearchaeales; Woesearchaeales+SCGC-AAA011-G17; Nanoarchaeales; plus two internal nodes representing the last common ancestor of all DPANN and of DPANN Cluster 1 archaea, respectively), yielding 72 parameters in total (DTL_br2)."
- Per-branch losses: "the branch leading to the common ancestor of DPANN archaea (LDCA) experienced 639.82 /592.64 loss events, followed by another 490.19/588.91 events on the branch leading to Undinarchaeota and DPANN Cluster 2 archaea under the Euryarchaeota/MHH root (Supplementary Data 20...)".
- Genome quality: "we applied several rounds of manual curation to assemble a dataset of 257 phylogenetically representative, high-quality (low contamination, high completeness) genomes".

The paper does not report a check of the DPANN loss rate against completeness beyond feeding CheckM2 values to AleRax.

## How AleRax uses completeness (source opened)

AleRax, `https://github.com/BenoitMorel/AleRax` (main branch), `src/ale/UndatedDTLMultiModel.hpp`; and the GeneRaxCore submodule it pins (commit 9ad7263b), `src/util/Scenario.cpp`. Saved in `raw/alerax_src/`.

- The extinction probability of a terminal species branch includes the chance that the gene is there but not seen: `temp = REAL(_PS[ec] * this->_fm[e]); // S but not observed scenario`.
- An observed gene at a tip is weighted by the chance it is seen: `temp = REAL(_PS[ec] * (1.0 - this->_fm[e])); // S and observed scenario`.
- A gene that survives in one child and dies out in the other is an SL event, with the "dead" child recorded: `recCell->event.type = ReconciliationEventType::EVENT_SL; recCell->event.lostSpeciesNode = g;`. The probability of that child dying out, `_uE[gc]`, includes the not-observed term above.
- The per-species counts add one loss to that child for every SL event: `case ReconciliationEventType::EVENT_SL: speciesToEventCount.at(event.pllLostSpeciesNode->label)[2]++;`.

So in the deposited `losses` column, a gene missing because a MAG is incomplete is counted as a loss on the tip branch. The fraction-missing term makes such scenarios more likely and keeps them from distorting the rates. It does not take them out of the counts. This is why the plan's arm A is re-cast as a positive control (see the prereg).

## Csűrös 2026 (opened)

Csűrös 2026, PNAS, doi:10.1073/pnas.2537812123, "Reconstructing ancient genomes from gene counts: A robust likelihood framework with sampling bias correction". Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13167736/fullTextXML`, saved as `raw/europepmc/PMC13167736_fulltext.xml`.

- Data: "We compiled a collection of homolog families across 269 Archaeal genomes from ref. 24", where ref. 24 is Dombrowski et al. 2020 (Nat. Commun. 11, 3939). Methods: "We identified all genome assemblies from ref. 24 that had unique NCBI Taxonomy identifiers and complete annotations in NCBI GenBank." It is not Huang's 257-genome set.
- The confound, stated for DPANN: "The inferred losses represent a combination of genuine evolutionary events such as genome streamlining in symbiotic Nanobdellati and technological artifacts of missing gene annotations. Nanobdellati genomes, which are primarily metagenome-derived, show loss of 28 to 36% families, compared to a median of 12 to 13% among E114 terminal lineages, which are well represented in complete genome assemblies."
- Why copy numbers cannot separate the two: "Crucially, incomplete genome coverage makes no difference in the GLD model because it gets perfectly absorbed by increased loss and adjusted duplication rates (7). (Consequently, genome completeness is nonidentifiable from copy numbers.)"
- On reconciliation at this scale: "We suggest that reconciliation methods are pushed beyond their limits at such scales: gene trees for large families are mathematically underdetermined because of bounded gene length."
- Its "sampling bias correction" is a correction for the minimum family size used to build the dataset ("defined as the minimum number Ωmin of copies in observed gene families"). It is not a completeness correction.

What this means for T9. Csűrös raises exactly the T9 question for DPANN tip lineages and leaves it open; it says the answer cannot come from copy numbers alone. It does not test Huang's reconciliation counts. It also points to the one place a test can work: losses deep in the tree, where a single incomplete genome cannot create them.

## Searches

| Where | Query | Result |
|---|---|---|
| Europe PMC | `DOI:10.1038/s41467-026-76386-7` | 1 hit, PMID 42595756, PMC13473441, cited by 1 |
| Europe PMC | citations of PMID 42595756 | 1: Szöllősi et al. 2026 preprint (below) |
| Europe PMC | `"methanogenic ancestor of the Archaea"` | 4 hits, including the preprint PPR1117682 (doi:10.1101/2025.11.11.687807), cited by 4 |
| Europe PMC | citations of PPR1117682 | 5 (below) |
| Europe PMC | `DOI:10.1073/pnas.2537812123` | Csűrös 2026, PMID 42101992, PMC13167736, open access |
| Europe PMC | `("fraction missing" OR "fraction_missing" OR "missing genes" OR "genome completeness") AND (ALE OR AleRax OR GeneRax OR reconciliation) AND ("gene loss" OR "loss rate")` | 81 hits; first 30 by title: Csűrös 2026, Huang 2026 and preprint, Rao et al. 2026 (Micrarchaeota), Manzano-Morales and Gabaldón 2026 (Asgard), Panguiarchaeum 2025, plus plant, animal and bacterial genome papers. None tests a loss rate against completeness, by title |
| Europe PMC | `DPANN AND ("loss rate" OR "gene loss") AND (completeness OR "metagenome-assembled" OR MAG) AND (artefact OR artifact OR bias OR overestimat*)` | 21 hits. New by title: Pellegrinetti et al. 2026 "Rethinking metagenome-assembled genome completeness" (no abstract in Europe PMC), "Genomic diversity, lifestyles and evolutionary origins of DPANN archaea" (2019), "Comparative Genomics Provides Insights into the Genetic Diversity and Evolution of the DPANN Superphylum" (2021). None tests Huang's rates, by title |
| Europe PMC | `(reconciliation OR "ancestral gene content") AND (incomplete genomes OR "genome incompleteness" OR "incomplete MAGs") AND (simulation OR benchmark)` | 1,371 hits, almost all noise past the first five; nothing on point |
| Europe PMC | `AleRax` | 18 hits: the AleRax paper (Morel et al. 2024) and papers using it. None evaluates the fraction-missing option, by title |
| arXiv API | `all:DPANN` | 0 entries |
| arXiv API | `all:reconciliation AND all:completeness AND all:loss` | 7 entries, none on point (one on distance-bounded reconciliation, the rest unrelated) |
| arXiv API | `all:"gene loss" AND all:"metagenome-assembled"` | 1 entry, unrelated (repeat detection) |
| arXiv API | `all:"fraction missing" AND all:reconciliation` | 0 entries |

The plan's own Europe PMC searches stand as written in `docs/plans/next_studies_2026-11-24.md`.

## Papers citing Huang 2026 or its preprint (abstract only)

- **Szöllősi, Spang, Boussau, Williams 2026, preprint, doi:10.64898/2026.09.03.749268**, "Improved ancestral genome reconstruction using a learned gene-content grammar". The abstract says reconciliation methods "tend to underestimate ancestral contents due to phylogenetic noise" and that their denoiser can "reconstruct gene repertoires from highly fragmented and noisy input data". It does not test DPANN loss rates.
- **Molecular Biology and Evolution 2026, doi:10.1093/molbev/msag091**, on salt adaptation in DPANN (Nanohaloarchaeota, Terrarchaeota). Uses reconciliation; the abstract says nothing about completeness or loss rates.
- **Journal of Applied Microbiology 2026, doi:10.1093/jambio/lxag056**, "Tracing ancient life through the genomic record". A review of methods and their pitfalls. No test.
- **Preprint doi:10.64898/2026.07.02.735847**, histone chromatin in Asgard archaea. Not related.
- **Preprint doi:10.64898/2026.06.17.729505**, insertions placing Nanohaloarchaea in DPANN. Notes "several cases of MAGs misannotations". No loss-rate test.

## Other abstracts read

- **Rao et al. 2026, Natl. Sci. Rev., doi:10.1093/nsr/nwaf542** (PMC12892359). 163 Micrarchaeota genomes; "less-host-dependent organisms evolved from symbionts through the gradual acquisition of pFLAGs through horizontal gene transfer". No completeness test of loss rates in the abstract.
- **Manzano-Morales and Gabaldón 2026, Nat. Commun., doi:10.1038/s41467-026-71534-5.** Asgard gene duplication and transfer. Not about DPANN or completeness.
- **Morel et al. 2024, Bioinformatics, doi:10.1093/bioinformatics/btae162**, the AleRax paper. The abstract does not mention missing genes; the source code (above) is what I relied on.

## Verdict

Not settled. Csűrös 2026 states the confound for DPANN and argues that copy-number data cannot separate it; it does not use Huang's data. No paper tests Huang's DPANN loss excess on internal branches. The study goes ahead, with arm A re-cast because of how AleRax counts losses.
