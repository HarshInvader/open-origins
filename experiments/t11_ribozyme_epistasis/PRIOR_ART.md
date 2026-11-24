# T11 prior art: does pairwise epistasis find tertiary contacts in ribozymes with solved structures?

Written 2026-11-24 by the T11 prep agent. No double-mutant or epistasis value was joined to a contact label while this was written.

"Opened" means I fetched the full text in this session and read the passage quoted. "Abstract only" means I read the Europe PMC abstract and nothing else. "Title only" means I saw the title in a search result; title-only papers carry no claim here.

All requests used the User-Agent `open-research-site/1.0` and no name or email. Saved responses are in `raw/prior_art/` and `raw/europepmc/` (both gitignored). A search that finds nothing is weak evidence.

## Short answer

1. **Prior art does not settle the question.** No paper I found scores how well double-mutant epistasis recovers tertiary (non-helical) contacts against a null matched on sequence separation and single-mutant effects.
   - Roberts et al. 2023 make the claim with heat maps and violin plots and give no score against a null.
   - Zhang et al. 2020 score base-pair recovery (sensitivity and precision), not tertiary contacts in general, and use no matched null.
   - Andreasson et al. 2020 read rescue interactions case by case for one ribozyme (glmS).
2. **Roberts themselves report a negative case.** The hammerhead loop-loop contact shows no positive epistasis. So the paper's general claim and one of its own examples point different ways. That is a reason to test it, not a result.
3. **One structure the plan did not expect.** Roberts write that no CPEB3 crystal structure exists, but a 2022 preprint reports one (PDB 7QR3/7QR4), and in it the P1.1 region forms a crystal dimer. CPEB3 is therefore reported only.
4. **The hatchet crystal is a domain-swapped dimer.** The functional monomer has to be stitched from two chains. This changes how its contacts are built (see the prereg).

## Roberts et al. 2023 (opened)

Roberts, Beck, Pollock, Bendixsen, Hayden 2023, eLife 12:e80360, doi:10.7554/elife.80360. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9901934/fullTextXML`, saved as `raw/europepmc/PMC9901934_fulltext.xml` and read in full.

- The claim: "Heatmap-based visualization of the data revealed patterns indicating structural features of the ribozymes including paired regions, unpaired loops, non-canonical structures, and tertiary structural contacts. ... The results demonstrate that the data sets provide structural information similar to chemical or enzymatic probing experiments, but with additional quantitative functional information."
- Why tertiary contacts might show it: "In addition, some non-canonical base interactions within tertiary contacts may also show epistasis even when they do not involve Watson-Crick or GU wobble base-pairing interactions. Nevertheless, the propensity for positive epistasis between physically interacting nucleotides suggests that a comprehensive evaluation of pairwise mutational effects should contain considerable structural information."
- How base pairs show up: "In this heatmap layout, many paired regions showed an anti-diagonal line of high-activity double mutant variants with strong positive epistasis ... In addition, pairs of mutations off the anti-diagonal tended to show negative or non-positive epistasis."
- The quantitative check they do give is by base-pair disruption, not by contact: "On average, disrupting two base pairs resulted in negative epistasis (mean of distribution), disrupting one base pair shifted the distribution toward more positive epistasis values, and the highest epistasis values (mean and max) were found for double mutants that result in zero disrupted base pairs".
- Hairpin loops A and B (a tertiary docking interface): "the double mutants within and between loop A and loop B show several instances of strong positive epistasis ... and the distributions of epistasis within and between these loops are significantly different than the terminal loops that are not structurally important (Figure 4D)." Their example is "the double mutant G1C and C46G", which is a base pair; our structure gate also finds G1-C46 as a canonical pair.
- The negative case, hammerhead loops: "Surprisingly, however, we found that most individual and double mutations do not reduce activity (Figure 5), and double mutants do not show positive epistasis (Figure 5—figure supplement 1). This indicates that the multiple interactions between the loops compensate for mutations that break a single interaction."
- CPEB3: "While no crystal structure of the CPEB3 ribozyme has been solved, this U:U base pair has been confirmed and implicated as a magnesium binding site based on NMR and Tb3+ cleavage data".
- The measurement: "This provides confidence in the fraction cleaved (FC) for each genetic variant in a given experiment, and genetic variants are compared to determine relative activity (RA)." Epistasis is defined on log relative activity, log(RA_ij / (RA_i · RA_j)).
- Data: "Sequences, activity data, and computer code is available at GitLab (https://gitlab.com/bsu/biocompute-public/mut_12 copy archived at swh:1:rev:7be31e58784ab6ffe5f15790ebbda98279af84d2)." This is the commit we pinned.
- Structures named in the text: the hairpin figure uses "Crystal structure of a hairpin ribozyme (PDB 1M5K". No other PDB id is named; the other entries were found through RCSB (see the prereg).
- The hatchet ribozyme is in the deposit but not in the paper.

What this means for T11. The paper's evidence for tertiary contacts is visual and by region (loops A and B). It does not ask whether a contact pair scores higher than a non-contact pair at the same separation and with equally harmful single mutants. That is the T11 test.

## Zhang et al. 2020 (opened)

Zhang, Xiong, Zhang, Wang, Zhan and Zhou 2020, Nucleic Acids Res. 48:1451, doi:10.1093/nar/gkz1192. Full text PMC7026644, saved as `raw/europepmc/PMC7026644_fulltext.xml`. I read the abstract, the methods on CODA and the twister section.

- Abstract: "a library of <5 × 10^4 single-to-triple mutants is sufficient to infer 25 of 26 base pairs including non-nested, nonhelical, and noncanonical base pairs with both sensitivity and precision at 96%. Such accurate inference was further confirmed by a twister ribozyme at 100% precision with only noncanonical base pairs as false negatives."
- The model of non-epistatic doubles: "these data points are used to generate the SVR model to fit RAobs(bi, bj) as a function of RAobs (bi) and RAobs (bj)." This is a global nonlinearity fitted to singles, the same idea as our isotonic fit.
- Twister structure: "we will focus on this fragment whose base-pairing structure (57) is shown in Figure 3 (PDB ID: 4OJI). The base pair pattern contains three noncanonical pairs (A2G39, A22A40, and Hoogsteen base pair U18A23), one lone pair (C9G13) as well as two long-distance loop-loop pseudoknots".

What this means for T11. Zhang show that deep mutational data recover base pairs, including tertiary base pairs that are Watson-Crick (pseudoknots, lone pairs). Their non-canonical pairs are the false negatives. T11 asks about contacts that are not Watson-Crick or GU pairs. Their target is base pairs, they report precision against the native list and no null matched on separation or single effects. The twister data they used (Kobori and Yokobayashi, 48-nt fragment, PDB 4OJI) is a different experiment from Roberts'. The base-pair result is established; T11 uses base pairs only as the positive control.

## Andreasson et al. 2020 (opened)

Andreasson, Savinov, Block and Greenleaf 2020, Nat. Commun. 11:1663, doi:10.1038/s41467-020-15540-1. Full text PMC7125110, saved as `raw/europepmc/PMC7125110_fulltext.xml`. I read the double-mutant rescue section.

- Definition: "double mutants with kobs(double)/kobs(single) > 1 (for a given constituent single mutant) were considered to display a “rescue” interaction."
- A tertiary contact found: "with G26 mutations rescuing second-site mutations in both members of the G7•C52 basepair (e.g., G26A rescues G7C by ~60-fold) (Fig. 5a, d), underscoring the importance of this tertiary interaction for catalytic function."
- A tertiary contact missed: "Conversely, we did not observe rescue interactions within the 27*28•45 base triple. This is likely because C28 and G45 are components of the active site and the cofactor binding pocket respectively".

What this means for T11. Case-by-case, with both hits and misses, in glmS (not one of our five). No systematic score. It warns that contacts at catalytic positions may never be rescued, because their identity matters for chemistry; that is one reason the effect may be small.

## Structure papers used for the gate (opened or abstract only)

- **Hatchet, Zheng et al. 2019, PNAS, doi:10.1073/pnas.1902413116 (opened, PMC6561176).** "Two hatchet ribozyme product molecules form a dimer through swapping of the 3′ ends of the pairing strand." And: "The existence of the palindromic nucleotides from A67 to U70 ... most likely contributes to the swapping of the 3′-end segments between two molecules of the hatchet ribozyme." Our map stitches the monomer A′ from chain A up to the swap point and chain B after it, and drops the palindrome.
- **CPEB3, Przytula-Mally et al. 2022 preprint, doi:10.1101/2022.09.22.508989 (abstract only; the full-text endpoint returned an error).** "the residues involved in forming the P1.1 mini-helix, which is an integral part of the characteristic nested double pseudoknot involving P1, P2, and P3, instead participate in a seven nucleotides loop with a conformation similar to the one from the anticodon (AC) loop of tRNAs when interacting with the mRNA codon. The conformation of the loop supports the formation of a four-base pair helix by interacting with the AC-like loop from a symmetry-related ribozyme leading to ribozyme dimer formation." The crystal contacts near P1.1 may not be the solution contacts, so CPEB3 does not decide.

## Papers that cite Roberts 2023

Europe PMC lists 16 citing records (`raw/prior_art/epmc_citations_roberts2023.json`). By title, none is a reanalysis of tertiary contacts. Two were read further:

- **RNAGym, Arora et al. 2025 preprint, doi:10.1101/2025.06.16.660049 (abstract only).** "we introduce RNAGym, a large-scale benchmarking framework specifically designed for three core tasks–RNA fitness, secondary structure, and tertiary structure prediction." Fitness and structure are separate tasks; the abstract does not describe scoring contacts from epistasis.
- **Beck et al. 2022, Front. Mol. Biosci., doi:10.3389/fmolb.2022.893864 (abstract only).** Machine learning of higher-order effects in CPEB3; about prediction of activity, not structure.

## Other close work (abstract only)

- **RNA-MobiSeq, Zhou et al. 2026 preprint, doi:10.21203/rs.3.rs-8802544/v1.** "covariation analysis via an RNA-specific unsupervised method converts these data into effective folding restraints, enabling accurate prediction of base-pairing (F1-score ≥ 90%) and tertiary (3.6–11.2 Å RMSD) structures for nine diverse RNAs". Its tertiary result is an RMSD of a folded model built from base-pair restraints, not a test of non-base-pair contacts.
- **Soo et al. 2021, PLoS Genet., doi:10.1371/journal.pgen.1009353, "Fitness landscape of a dynamic RNA structure".** "We further show that patterns of epistasis can be used to infer the presence of intramolecular pleiotropy." Two 4-bp segments of a group I intron; helices, not tertiary contacts.
- Protein work (Rollins et al. 2019, doi:10.1038/s41588-019-0432-9; Schmiedel and Lehner 2019, doi:10.1038/s41588-019-0431-x): title only. They infer protein contacts from double-mutant scans; the matched-null question for RNA is not theirs.

## Searches

| Where | Query | Hits |
|---|---|---|
| Europe PMC | `(ribozyme OR RNA) AND epistasis AND ("tertiary contact" OR "tertiary contacts" OR "tertiary interaction" OR "tertiary interactions") AND ("double mutant" OR "double mutants" OR pairwise)` | 35 |
| Europe PMC | `("deep mutational scanning" OR "mutational scan" OR "double mutant") AND RNA AND ("contact prediction" OR "contact map" OR "3D structure" OR "tertiary structure") AND epistasis` | 144 |
| Europe PMC | `"self-cleaving ribozymes" AND epistasis AND (structure OR contacts) AND (null OR AUC OR precision OR "positive predictive")` | 4 |
| Europe PMC | `(Roberts AND Hayden AND ribozyme AND pairwise mutagenesis)` | 9 |
| Europe PMC | `RNA AND ("deep mutational scanning" OR "high-throughput mutagenesis") AND ("3D structure" OR "tertiary") AND (inference OR determination OR "structure determination") AND epistasis` | 28 |
| Europe PMC | `("M2-seq" OR "mutate-and-map" OR "mutational profiling") AND RNA AND tertiary` | 449 (first 25 titles checked) |
| Europe PMC | citations of PMID 36655987 (Roberts 2023) | 16 |
| arXiv | `all:ribozyme AND all:epistasis`; `all:ribozyme AND all:"double mutant"`; `abs:RNA AND abs:epistasis AND abs:tertiary`; `all:RNA AND all:epistasis AND all:contacts` | 0 each |
| arXiv | `all:ribozyme AND all:fitness` | 4, none relevant by title |

Titles of the first 25 hits of each Europe PMC query are in `raw/prior_art/search_log.txt`.

## What this means for the design

- Base pairs are known to be recoverable (Zhang 2020; Roberts' violin plots). They are the positive control, not the question.
- The new part is small and specific: non-helical, non-WC contacts, scored against non-contacts matched on separation and single-mutant effect, in five ribozymes from one experiment. A negative answer would also say something about our QT45 study (#30), which had no positive control (`docs/library/IDEAS.md`, idea 4; `experiments/qt45_epistasis/RESULTS.md`).
- Roberts' hammerhead result and Andreasson's catalytic-site miss both predict that many tertiary contacts are invisible to single compensating doubles. The planted check covers a range where only a share of contacts is visible.
