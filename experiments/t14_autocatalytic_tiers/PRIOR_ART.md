# Prior art for T14: has anyone tested Peng, Linderoth & Baum's tiered SDAS structure against rewired networks?

Written before any rewired version of the real networks was built or scanned. Everything cited below was
opened in this repo; quotes are verbatim from the files in `raw/europepmc/` and `raw/prior_art/` (both
gitignored). Titles and authors come from Europe PMC or Crossref metadata saved in `raw/prior_art/meta/`
and `raw/prior_art/crossref/`.

**Verdict: no. Proceed with the study.** None of the works that cite the paper runs a randomized,
rewired or degree-preserving null on seed-dependent autocatalytic systems (SDASs), their seeds or their
tiers. The paper itself contains no such test. The closest earlier work (Matthäus, Salazar & Ebenhöh 2008)
reports a nested hierarchy of metabolic "scopes" in KEGG and calls it intrinsic, but its randomization
draws random seed sets in the real network; it does not randomize the network.

## The paper under test

Peng Z, Linderoth J, Baum DA. 2022. "The hierarchical organization of autocatalytic reaction networks and
its relevance to the origin of life." PLoS Comput Biol 18:e1010498. doi:10.1371/journal.pcbi.1010498,
PMC9491600. Read in full from `raw/europepmc/PMC9491600.txt` (Europe PMC full-text XML, flattened).

The result this study tests (Results, biochemical network, verbatim):

> "Network expansion from the ultimate food generates a 30-species, 44-reaction tier-0 system (S10 Table).
> Treating this tier-0 system as external food, 304 of the 4186 non-tier-0 species are singleton supported
> seeds able to induce a tier-1 SDAS (S11 Table). These seeds belong to three cliques: the 267-species
> clique bio-1a induces SDAS-bio-1a (301 species; 736 reactions; S12 Table); the 34-species clique bio-1b
> induces SDAS-bio-1b (357 species; 916 reaction; S13 Table); the 3-species clique bio-1c induces
> SDAS-bio-1c (1414 species; 4114 reaction; S14 Table). These SDASs are nested, with SDAS-bio-1c including
> the entirety of SDAS-bio-1b, which includes the entirety of SDAS-bio-1a."

How the authors read it (Discussion, verbatim):

> "We found that the abiotic and biochemical networks share multiple properties, including hierarchically
> organized SDASs converting simple materials and energy to more complex species."

The abiotic network (verbatim):

> "The tier-0 system has 5 species and no reactions. Twelve of the 272 non-tier-0 species constitute the
> clique abio-1 inducing a tier-1 SDAS, SDAS-abio-1 (S3 Table) of 91 species and 220 reactions (S4 Table)."

A case-insensitive search of the full text for "rewir", "null model", "shuffl", "random network" and
"degree-preserving" finds nothing. The paper gives no comparison with randomized networks, so it does not
say whether three nested tier-1 systems are more than the network's degree sequence would give.

## The two works the plan named

**Huson D, Xavier JC, Steel M. 2024.** "Self-generating autocatalytic networks: structural results,
algorithms and their relevance to early biochemistry." J R Soc Interface. doi:10.1098/rsif.2023.0732,
PMC11286130. Full text opened (`raw/prior_art/fulltext/PMC11286130.txt`). It cites Peng et al. 2022
(reference 25) once, in a list (verbatim):

> "In addition, a number of other recent structural approaches to autocatalytic networks have been
> applied in origins of life research [24,25]."

It contains no rewiring, shuffling or null-model test (zero matches for the terms above).

**Golnik R, Gatter T, Hordijk W, Stadler PF, Vassena N. 2026.** "Bridging two theoretical frameworks of
autocatalysis: RAF sets and stoichiometric autocatalysis." J Theor Biol. doi:10.1016/j.jtbi.2026.112580
(metadata from Europe PMC). Read via the arXiv version 2605.25523 (`raw/prior_art/fulltext/`). It is
formal theory relating RAF sets to stoichiometric autocatalysis. It names the SDAS concept (the PDF's
two-column text extraction interleaves lines; the fragments read "the seed-dependent autocatalytic
system ... (SDAS) studied in (Peng, Linderoth and Baum, 2022)"). The only match for "random" is the title
of a cited reference (Mossel & Steel 2005, "Random biochemical networks: ..."). No randomized network is
analysed.

## Closest earlier work

**Matthäus F, Salazar C, Ebenhöh O. 2008.** "Biosynthetic potentials of metabolites and their
hierarchical organization." PLoS Comput Biol. doi:10.1371/journal.pcbi.1000049, PMC2289774. Full text
opened. It finds nested "scopes" in KEGG (verbatim):

> "We observe that most of the resulting consensus scopes overlap or are fully contained in others,
> revealing a hierarchical ordering of metabolites according to their biosynthetic potential."

Its randomization is over seed sets, not over the network (verbatim):

> "For each seed size between 2 and 20, we generate 1000 random seeds and calculate the corresponding
> scopes."

and it concludes (verbatim):

> "We thus assume that the hierarchy is indeed an intrinsic characteristic of the metabolic network
> itself."

So the nesting of expansion scopes in metabolism is known (since 2008) and is held to be a property of the
network. Neither this paper nor any later one asks whether that nesting, or the SDAS tiers, survives a
rewiring that keeps each species' number of reactions. That is the gap T14 fills. Note the difference in
object: scopes need no autocatalysis; SDASs must also pass the stoichiometric self-maintenance test.

Seen at abstract level only (Europe PMC metadata, not full text), none describes a rewired-network test of
expansion hierarchy: Handorf, Ebenhöh & Heinrich 2005 (doi:10.1007/s00239-005-0027-1; robustness of scopes
to reaction removal), Handorf, Ebenhöh, Kahn & Heinrich 2006 (doi:10.1049/ip-syb:20060021), Basler,
Nikoloski, Ebenhöh & Handorf 2008 (doi:10.1142/9781848163003_0012; random nutrient sets), and Stulajter &
Rappoport 2024 (doi:10.1021/acs.jctc.4c00810; compares reaction networks with random graph models on graph
measures, not on autocatalysis).

## Citing works screened

Citations were gathered from Europe PMC (`citations` endpoint, 24 records), OpenCitations COCI (38) and
OpenCitations v2 (38), merged by DOI into 35 unique works. Each was screened from its metadata and, where
open, its full text. Full texts opened and searched (zero matches for "rewir", "degree-preserving",
"null model", "shuffl" and "random network" in every one):

| Work | DOI | What it does with Peng et al. |
|---|---|---|
| Baum DA, Peng Z, Dolson E, Smith E, Plum AM, Gagrani P. 2023. The ecology-evolution continuum and the origin of life. J R Soc Interface | 10.1098/rsif.2023.0346 | conceptual review; no null |
| Peng Z, Adam ZR, Fahrenbach AC, Kaçar B. 2023. Assessment of Stoichiometric Autocatalysis across Element Groups. JACS | 10.1021/jacs.3c07041 | applies autocatalysis detection to other networks; no rewired null |
| Gagrani P, Blanco V, Smith E, Baum D. 2024. Polyhedral geometry and combinatorics of an autocatalytic ecosystem. J Math Chem (arXiv 2303.14238) | 10.1007/s10910-024-01576-x | theory; random networks only as future work |
| Kosc T, Kuperberg D, Rajon E, Charlat S. 2025. Thermodynamic consistency of autocatalytic cycles. PNAS | 10.1073/pnas.2421274122 | thermodynamics of cycles; no SDAS null |
| Plum AM, Kempes CP, Peng Z, Baum DA. 2025. Spatial structure supports diversity in prebiotic autocatalytic chemical ecosystems. npj Complexity | 10.1038/s44260-025-00045-z | spatial simulations; no null on tiers |
| Nandan P, Nghe P, Unterberger J. 2026. Autocatalytic cores in the diluted regime: classification and properties. J Math Biol | 10.1007/s00285-026-02357-7 | formal classification; no null |
| Peng Z, Spencer E, Baum D. 2026. The diverse effects of side reactions on the persistence of autocatalytic cycles. J R Soc Interface | 10.1098/rsif.2026.0308 | kinetics of side reactions; no null |
| Huson, Xavier & Steel 2024; Golnik et al. 2026 | above | above |

Gagrani et al. (verbatim, from the arXiv text): "In future work it would be interesting, similar to
[35, 36], to consider randomly generated CCRNs in an Erdos-Renyi framework".

The remaining citing works were screened by title and abstract metadata and are about other topics
(kinetics, prebiotic chemistry databases, niche construction, criticality, curvature inference,
philosophy of origins): Pascal 2024; Pross & Pascal 2023; Root-Bernstein & Brown 2022; Tran, Yi &
Fahrenbach 2023; Smith, Smith & Andersen 2023/2024; Pirovino et al. 2023; Peng L et al. 2023
(doi:10.1002/qub2.22); Chorowski, Kutner & Struzik 2024; Despons, De Decker & Lacoste 2024; Despons 2025;
Adams et al. 2024; Sokolskyi et al. 2022 and 2024; Cuevas-Zuviria et al. 2025 (preprint and journal);
Narayanan et al. 2025; Papale et al. 2025 and 2026; Wong et al. 2025; Avram et al. 2025; Juckett 2026;
Camprubi, Pearce & Preiner 2026; Lei, de Farias & Burton 2026; a 2023 paper in a Ukrainian chemistry
journal on chaos control in an autocatalytic dissipative system (doi:10.15421/jchemtech.v31i1.262503).

Keyword searches (Europe PMC and arXiv; saved in `raw/prior_art/search/`) for SDAS, seed-dependent
autocatalytic, network expansion with randomization, scope hierarchy, autocatalytic cores with a null,
and rewired autocatalytic networks found no further candidate.

## Gaps

- Three Europe PMC metadata requests returned HTTP 503 (PMIDs 36294944, 37712016, 38004311); their
  Crossref or OpenCitations records were used instead where present.
- Two Zenodo records (doi:10.5281/zenodo.8156386 and 10.5281/zenodo.15397883, one a Lacoste & Ledoux
  preprint) had no Crossref record and could not be opened. They could hold a null test; this is the main
  residual risk to the verdict.
- Paywalled full texts were not sought by any other route.
