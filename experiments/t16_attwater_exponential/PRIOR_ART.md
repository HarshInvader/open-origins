# Prior art for T16: has anyone questioned whether Attwater et al. 2025's ribozyme replication is exponential?

Written before any growth law was fitted to the deposited data. Everything cited below was opened in this
repo. Quotes are verbatim from the files in `raw/europepmc/` and `raw/prior_art/` (all gitignored).
Titles and author lists come from Europe PMC or Crossref metadata saved there.

**Verdict: no one has. But the question cannot be decided with the deposited data** (see `README.md`,
power gate). None of the 17 citing records screened questions the exponential claim, tests parabolic
growth or product inhibition against it, or reanalyses Fig. 3e.

## The paper under test

Attwater J, Augustin TL, Curran JF, Kwok SLY, Ohlendorf L, Gianni E, Holliger P. 2025. "Trinucleotide
substrates under pH-freeze-thaw cycles enable open-ended exponential RNA replication by a polymerase
ribozyme." Nature Chemistry. doi:10.1038/s41557-025-01830-y, PMC12226338, PMID 40437192 (Europe PMC
metadata). Full text read from `raw/europepmc/PMC12226338.xml`. An earlier preprint has the same claim:
Attwater J, Augustin T, Curran JF, Kwok S, Gianni E, Holliger P. 2023. "Trinucleotide building blocks
enable exponential ribozyme-catalysed RNA replication and open-ended growth of diverse RNA sequence
pools". bioRxiv, doi:10.1101/2023.03.17.533225 (abstract only).

**The claim** (verbatim):

> "When combined with coupled pH and freeze–thaw cycles, this enabled exponential replication of both (+)
> and (−) strands of double-stranded RNAs, including a fragment of the ribozyme itself." (Abstract)

> "The (+) and (−) strands of the +14-nt sequence exhibited a four-cycle exponential growth phase (1.2- and
> 1.38-fold per cycle) before plateauing at 3.5- and 7-fold amplification from the starting duplex (Fig.
> 3e). This confirms that pH/freeze–thaw cycling lets the TPR exponentially replicate RNA sequences, with
> open-ended cycling driving the evolution of replicable RNAs from libraries." (Results)

**How Fig. 3e was made** (caption, verbatim):

> "e, Cycling as in a of 0.8 nM of both strands of one clone (shown here beneath its substrates) without
> dilution. Average strand copy numbers (filled orange circles, FITC strand; open blue circles, Cy5 strand;
> comprising full-length and starting template) are shown for three independent reactions per cycle
> (transparent circles). Dotted lines are exponential curves fitted up to four cycles (x): FITC strand =
> e0.38x, R2 = 0.997; Cy5 strand = e0.20x, R2 = 0.984."

So:
- There are **3 independent reactions**, read at each of cycles 0 to 8 (9 points in the source data).
- The fit is to the **average** copy number, **cycles 0 to 4 only**.
- The fitted form is **e^(kx), with no free intercept**: the curve is forced through 1 at cycle 0.
- R² is computed on those 5 average points.
- No alternative growth law is fitted or compared.

**How yield is quantified** (Methods, verbatim):

> "Gels were scanned on a Typhoon FLA-9000 imager (GE) at different wavelengths for each
> fluorophore-labelled primer. ... Gel bands were quantified using ImageQuant analysis software; backgrounds
> were drawn between peak troughs or using adjacent negative controls. For primer extensions, band
> intensities of unextended primers and extension products of all lengths were used to calculate the product
> distribution, and hence extension yields of, for example, 'full-length' (full-length band only), 'reaching
> full-length' (including longer bands) or 'primer extension' (at least 1–3 triplet addition) products, as
> indicated in the figure legends, with product pmol or µM calculated from the known total pmol or µM of
> primer in each reaction."

Cycling (Methods, verbatim): "Another cycle was initiated by thawing the reactions at room temperature
before HCl addition, and so on." The methods do not say how each reaction was sampled at each cycle.
Fig. 3e is "without dilution".

**Two inconsistencies, from the text alone** (no data needed):
1. **The per-cycle folds disagree.** The caption's fits give e^0.38 = 1.46-fold and e^0.20 = 1.22-fold
   per cycle. The text gives "1.2- and 1.38-fold per cycle". The 1.38 looks like the exponent 0.38
   written as a fold. Also, the text lists "(+) and (−)" while the caption lists FITC and Cy5, so which
   fold belongs to which strand is not stated.
2. **The deposited "Mean" row does not match the three datasets.** It differs from their arithmetic
   mean by up to 16% (FITC) and 31% (Cy5) at some cycle. It also differs from the geometric mean (27%,
   21%) and the median (66%, 21%).
   - This is a difference-only check, recorded in `scripts_out/t16_scatter.json`. No mean value was
     printed.
   - The caption's fits are to the plotted averages. So it is not clear which numbers the published
     R² comes from.

**Other observations from the paper, for context:**
- **Fig. 3c (rates).** Fig. 3c's rates ("apparent exponents of 1.37-, 1.3- and 1.27-fold per cycle")
  come from one series, with no replicates. That series is multiplied by the cumulative dilution. As
  the plan says, keeping pace with serial dilution is exponential by construction, so it cannot decide
  the growth law.
- **Fig. 2 / Extended Data Fig. 3 (a different measure).** These report "Amplification after x cycles =
  1 + 2^((x-1)/4)*([ ≥ FL(x)] ÷ starting [AD])". That is a different quantity, and not the claim under
  test.
- **Product inhibition is named.** The paper's own framing names the classic cause of parabolic growth:
  "RNA replication is considered a key process in the origins of life. However, both enzymatic and
  non-enzymatic RNA replication cycles are impeded by the 'strand separation problem', a form of
  product inhibition arising from the extraordinary stability of RNA duplexes and their rapid reannealing
  kinetics." (Abstract)

## Why the alternative matters (background, opened)

Paczkó M, Szathmáry E, Szilágyi A. 2024. "Stochastic parabolic growth promotes coexistence and a relaxed
error threshold in RNA-like replicator populations." eLife. doi:10.7554/elife.93208 (abstract only):

> "Autonomous, non-enzymatic, and sustained replication of such information carriers presents a problem,
> because product formation and hybridization between template and copy strands reduces replication speed.
> Kinetics of growth is then parabolic with the benefit of entailing competitive coexistence, thereby
> maintaining diversity."

Parabolic and exponential growth differ in their evolutionary consequences: parabolic growth allows
coexistence, while exponential growth leads to selection. That is why the claim is worth testing.

## Searches and screen

All requests used User-Agent `open-research-site/1.0`. No paywall or bot block was worked around.
The OSF view-only link was not opened.

**Citing records.** Europe PMC `MED/40437192/citations` returned 16. OpenCitations index v2 returned 9:
- 8 of the 9 are among the Europe PMC 16;
- one extra, doi:10.64898/2025.12.18.695146 (Maiklem, Attwater, "5′ RNA Aminoacylation via Interstrand
  Acyl-Transfer", Crossref metadata), is about aminoacyl transfer.

That gives **17 unique records**. Abstracts were read for 15 of them. Two have no abstract in Europe PMC
or Crossref and were screened by title only:
- Müller, "The power of triplets", Nat Rev Chem 2025 (a highlight);
- "How a freezing pond could kick-start life's self-replication", Nature 2025 (news).

No abstract mentions exponential, parabolic or square-root growth, sub-exponential growth, or product
inhibition in connection with this paper. Keyword screen in `raw/prior_art/citing_core.json`. The
records:

| Europe PMC id | Year | Title (Europe PMC metadata) | Relevant to the growth law? |
|---|---|---|---|
| 42652975 | 2026 | Exonuclease Ribozyme Encoded in a Circular Genome: On the Initiation of the RNA World. | no |
| PPR1253421 | 2026 | Emergent primordial heritability in short random RNA pools | no (nonenzymatic ligation pools) |
| 41990560 | 2026 | From random pools to precision tools: The expanding repertoire of synthetic nucleic acid catalysts. | no (review) |
| 42011785 | 2026 | Sequence patterns in RNA replication via the virtual circular genome mechanism. | no (simulation; VCG) |
| 41915419 | 2026 | Assembly of Replicating Protocells with Primitive Metabolism. | no |
| 41861754 | 2026 | Nucleic acid catalysts: From the origin of life to modern applications. | no (review) |
| 41819849 | 2026 | Molecular insights into dynamic RNA quaternary assemblies. | no |
| 41819008 | 2026 | The evolving logic of biocatalyzed nucleic acid synthesis. | no (review) |
| 41748576 | 2026 | Analysis and control of untemplated DNA polymerase activity for guided synthesis of kilobase-scale DNA sequences. | no |
| 41678588 | 2026 | A small polymerase ribozyme that can synthesize itself and its complementary strand. | no (same group; QT45; yields "~0.2% in 72 days", no growth-law claim) |
| 41651995 | 2026 | G-quadruplexes self-assembled from nucleotide monomers as stable prepolymer scaffolds in aqueous environments. | no |
| 41428828 | 2026 | Ice Confinement Enabled Click Conjugation of DNA Oligonucleotides and Macromolecules. | no |
| 41355437 | 2025 | Ice-Confinement Overcomes the Diffusion-Reaction Limitation in Surface Assays. | no |
| 41659704 | 2025 | Selection-diversification interplay in oligonucleotide chemical evolution. | no (review) |
| 40691300 | 2025 | The power of triplets. | title only |
| 40442437 | 2025 | How a freezing pond could kick-start life's self-replication. | title only |

**Topic searches** (Europe PMC; counts on 2026-11-25, saved in `raw/prior_art/epmc_searches.json`):
- `"polymerase ribozyme" AND exponential AND (parabolic OR "sub-exponential" OR "product inhibition") AND replication`:
  14 hits. These are the paper, its preprint, a GTP synthase ribozyme paper (2026), Paczkó et al. 2024
  and older replicator-model papers. None is a reanalysis.
- `(Attwater OR "triplet polymerase ribozyme") AND (exponential OR parabolic OR "growth law" OR reanalysis)`:
  24 hits, most of them off-topic. None is a reanalysis.
- `"parabolic growth" AND (ribozyme OR "RNA replication") AND (2025 OR 2026)`: 3 hits, all off-topic.

**arXiv** (export API):
- `all:ribozyme AND all:exponential`: 3 hits. The only one from 2023 on is "MoRSAIK: Sequence Motif
  Reactor Simulation, Analysis and Inference Kit in Python" (2025, title only, a software kit).
- `all:ribozyme AND all:replication AND all:parabolic`: 0 hits.
- `all:"strand separation" AND all:RNA AND all:replication`: 0 hits.

## What this means for T16

The question is open: nobody has tested exponential against parabolic or linear growth on Fig. 3e. But
the deposited data (3 reactions × 9 cycles, with large between-reaction scatter) cannot tell the laws
apart at the published amplitudes. The power gate in `README.md` shows this. The two reporting
inconsistencies above can be stated without any growth-law test.
