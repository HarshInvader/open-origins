# T8 prior art: has anyone tested the Ameta 2021 growth-versus-variation trade-off against droplet noise?

Written 2026-11-25 by the T8 prep agent. No real test statistic was computed.

"Opened" means I fetched the text in this session and read the passage quoted. "Abstract only" means I read the abstract and nothing else. "Title only" means I saw the title in a list. Title-only papers carry no claim here.

All requests used the User-Agent `open-research-site/1.0` and carried no personal name or email. Saved responses are in `raw/prior_art/`, `raw/europepmc/`, `raw/esm/` and `raw/github/` (all gitignored). A search that finds nothing is weak evidence.

## Short answer

1. **No reanalysis found.** None of the 27 papers that cite Ameta et al. 2021 reanalyses the trade-off, tests it against measurement noise, or questions it. I read the abstract of each of the 22 citing papers that have one. The other five I saw by title only.
2. **The paper did not test it against noise.** It reports a measurement precision (about 6% per species fraction), a repeat experiment (r = 0.84) and an absolute-concentration version of the plot (Supplementary Fig. 6e). None of these asks whether the trade-off survives noise that depends on yield.
3. **arXiv has no reanalysis.** Eight queries found one related paper, a theory paper from the same group (below). It does not reanalyse the data.
4. **The study is not settled by prior art.** It goes ahead.

## What Ameta 2021 says (opened)

Ameta, Arsène, Foulon, Saudemont, Clifton, Griffiths, Nghe 2021, "Darwinian properties and their trade-offs in autocatalytic RNA reaction networks", Nat. Commun. 12:842, doi:10.1038/s41467-021-21000-1, PMID 33558542, PMC7870898. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7870898/fullTextXML`, saved as `raw/europepmc/PMC7870898_fulltext.xml`. The passages below are also in `raw/europepmc/PMC7870898_definitions_excerpt.txt`.

- The claim: "Furthermore, we observed that high-yield networks tend to display small perturbation values, implying a trade-off between growth and variation (Fig. 2d, Supplementary Fig. 6e)."
- The test (Fig. 2d caption): "The number of strongly perturbable (pG→G′ > 0.8, above the green dotted line) and high-yield networks (>0.08 µM, right hand side of red dotted line) is very low compared to the null hypothesis of independence between the two properties (one-sided Fisher exact test, N = 162, odds ratio <0.1, 95% confidence interval 0.01–0.66, p-value = 1.6 × 10−3)."
- The authors' own partial explanation: "Consistently, the attenuation of perturbations with large σG/e combined with the weak but significant correlation between growth and σG (r = 0.5, p < 10−5, Fig. 3d) explains part of the trade-off between yield and perturbation reported in Fig. 2d."
- Noise, as the paper reports it: "…with on average 11 replicates each (Fig. 1d and Supplementary Fig. 5a), indicating a mean precision of ~6% in species fractions (Supplementary Fig. 5b). Repeatability was tested with a full experimental replicate (r = 0.84, p < 10−3 between species fractions; Supplementary Fig. 5c)."
- Droplet filter (Methods): "Then, only the droplet barcodes with more than 10 UMIs associated with hairpin RNA reporters and 20 with ribozymes were retained and the fraction of each species in the network was computed."
- Yield (Methods): "To determine network yield per droplet, first we computed a droplet-specific UMI to concentration conversion rate by considering total hairpin reporter UMIs as well as number of different hairpin reporters identified. This was then used to convert total number of ribozyme UMIs into a yield value."

The yield of a droplet is its ribozyme UMI count scaled by its reporter UMIs. A low-yield droplet therefore has few ribozyme UMIs, and its fractions are noisier. That is the artefact this study tests.

Supplementary Information (`raw/esm/41467_2021_21000_MOESM1_ESM.pdf`, opened):

- Supplementary Fig. 5b: "Distribution of species fraction standard deviation where standard deviation is measured from the networks with at least 5 replicates. … The result indicates a mean precision of ~6% in species fractions." This is one average over all networks. It is not split by yield.
- Supplementary Fig. 6e: "Perturbation, computed with absolute concentrations in µM rather than species fraction as in Fig. 2d, for networks with 3, 4 and 5 species is plotted against network yield in µM for perturbations involving the addition of a novel catalysts (with G/C as the middle nucleotide of the IGS) with at least one target." The caption reports no test.

The authors' code (doi:10.5281/zenodo.4016905; the same repository on GitHub, `smnars/azoarcus_networks`, commit 76cd71e) was opened as source only, never run. `analysis/figures.ipynb` cell 36 builds the Fig. 2d subset, and `utils/az_tools.py` defines the perturbation (`compute_pscore`, `collapse_postprocess`) and "catalytic innovation" (`is_catalytic_innovation`: "no other node has the same IGS and … it has at least a target different from itself"). No cell in either notebook contains the Fisher test. I read the code cells only, not the saved outputs.

## Searches

| Where | Query | Result |
|---|---|---|
| Europe PMC | citations of PMID 33558542 (`/MED/33558542/citations`) | 27 papers; the same 27 as `CITES:33558542_MED` |
| OpenCitations (COCI v2) | citations of doi:10.1038/s41467-021-21000-1 | 26 DOIs, which are the Europe PMC set plus or minus preprint and book duplicates. Crossref says 38 citations; the 12 missing are not in either open index |
| Europe PMC | `CITES:33558542_MED AND ("trade-off" OR tradeoff OR "trade-offs")` | 4 hits: design principles and growth laws of minimal autocatalysts (Commun. Chem. 2024), a backstory piece (iScience 2023), two reviews (Life 2021, IJMS 2021). None tests the trade-off |
| Europe PMC | `CITES:33558542_MED AND (noise OR "sampling error" OR artefact OR artifact OR reanalysis OR "re-analysis")` | 4 hits: assembly theory (2026), autocatalyst design (2024), "what is the question" (2022), a review (Life 2021). None is a reanalysis |
| Europe PMC | `CITES:33558542_MED AND (perturbation AND yield)` | 0 hits |
| Europe PMC | `"Azoarcus" AND ("trade-off" OR tradeoff) AND (perturbation OR perturbability) AND (droplet OR droplets)` | 5 hits: the paper, a 2021 review, three unrelated |
| Europe PMC | `(Ameta OR "41467-021-21000-1") AND ("growth" AND "variation") AND ("trade-off" OR tradeoff) AND (noise OR "sampling" OR compositional OR artefact OR artifact)` | 18 hits: the paper, the 2021 review, the rest unrelated (plant water transport, PFAS, conference books) |
| Europe PMC | `("autocatalytic network" OR "autocatalytic networks" OR "autocatalytic sets") AND ("compositional data" OR "sampling noise" OR "Poisson noise") AND (droplet OR UMI)` | 0 hits |
| arXiv | `all:Azoarcus AND all:autocatalytic`; `all:autocatalytic AND all:RNA AND all:networks AND all:droplets AND all:Darwinian`; `abs:"Darwinian properties" AND abs:autocatalytic`; `all:autocatalytic AND all:trade-off AND all:variation`; `all:autocatalytic AND all:compartments AND all:heritable AND all:variation` | 0 hits each |
| arXiv | `all:Ameta AND all:autocatalytic` | 1 hit, arXiv:2211.03155 (below) |
| arXiv | `all:Azoarcus` | 6 hits, all on ribozyme folding or plants |
| arXiv | `all:autocatalytic AND all:ribozyme` | 1 hit, "Autocatalytic Sets and RNA Secondary Structure" (title only, 2016, predates the paper) |

## Citing papers read as abstracts (none is a reanalysis)

- Ameta et al. 2023, Commun. Chem., doi:10.1038/s42004-023-00887-5, "Multispecies autocatalytic RNA reaction networks in coacervates" (and its bioRxiv preprint). A follow-up experiment: "these phase-separated compartments endow robustness to the composition of the collectively autocatalytic networks against external perturbations." New data. It does not revisit Fig. 2d.
- Toward Evolution in Chemical Reaction Networks, RSC book chapter 2022, doi:10.1039/9781839164798-00379. A review: "we review experimental efforts and corresponding theories toward building and discovering evolutionary properties in chemical reaction networks."
- Abiogenesis through gradual evolution of autocatalysis into template-based replication, FEBS Lett. 2022/2023, PMID 36203246. A review: "we examine how experimentally feasible RNA reactions catalysed by ribozymes could implement the evolutionary properties of variation, heredity and reproduction".
- A stepwise emergence of evolution in the RNA world, FEBS Lett. 2025, PMID 40353364. A scenario paper ("I propose a 3-stage scenario").
- Temperature-driven catalytic switching… in coacervates, Small 2025, PMID 41255031. New experiments on Azoarcus in coacervates.
- On the Evolutionary Development of Biological Organization from Complex Prebiotic Chemistry, book chapter 2023, doi:10.1007/978-3-031-38968-9_9. Philosophy of organisation ("we offer a critical analysis of organizational models").
- The other abstracts I read were theory or reviews with no reanalysis of this dataset: assembly-theory directedness (2026), proto-biosignatures (2026), living versus non-living (2026), the RNA-first fallacy (2026), autocatalytic cores in the diluted regime (2026), thermodynamics of Darwinian selection (2025), cross-chiral amplification (2024), design principles of minimal autocatalysts (2024), is life binary or gradual (2024), ribonucleotide recognition motifs (2024), a self-stacking DNA circuit (2023), autocatalysis in diluted networks (2022), the origin of life question (2022), microfluidics in prebiotic chemistry (2022), protogenome evolution (2021), RNA diversification by a recombinase (2021), self-reproduction in autocatalytic systems (2021), speciation before the origin of life (2021). One citing paper is about neonatal microglia.
- Title only (no abstract in Europe PMC or Crossref): "Going in reverse to get it right in RNA replication" (2026), "What Are Ribozymes for? Arguing for Function Pluralism" (2023), "Droplet-based microfluidics" (Nat. Rev. Methods Primers 2023), "An interdisciplinary effort…" (iScience 2023), "Social Networking of Quasi-Species Consortia…" (2021).

## arXiv:2211.03155 (abstract only)

Matsubara, Ameta, Thutupalli, Nghe, Krishna, "Conditions for Darwinian evolution in compartmentalized autocatalytic reaction networks". A theory paper from the same group: "we show that multistable autocatalytic reaction networks can maintain heritable compositional states across a broad class of growth-division regimes". It does not reanalyse the 2021 droplet data.

## What this does not cover

- Citing papers outside the open indexes (Crossref counts 38; Europe PMC and OpenCitations list 27 and 26).
- Reviews that discuss the trade-off in their full text but not in their abstract. Only the abstracts were screened.
- Google Scholar, which was not used.
