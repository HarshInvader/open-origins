# QT45 tertiary contacts and fitter multi-mutants from the open double-mutant landscape (board task #30)

Agent: qt45. Run 2026-11-19. Pre-registration: `docs/prereg/qt45_epistasis.md`, sha256
`c3097e59134e5d7251948fea3c1df2c5d4b02e7c48763946dbf82c376ef18f15`, logged in `docs/prereg/HASHES.txt`
at 2026-11-19T06:05:54Z, before any epistasis value was computed.

## Verdict: negative

Two of the three pre-registered kill criteria were hit:

1. **The planted check fell short of its pre-set power.** Required: at least 5 of 10 planted contacts in
   the top 20 ranked pairs in at least 8 of 10 replicates. Observed: hits per replicate
   `[6, 4, 5, 7, 4, 4, 6, 5, 4, 3]`, i.e. **5 of 10 replicates passing** (mean 4.8 planted contacts
   recovered, against a chance expectation of 0.202). The pipeline is far better than chance but below
   the power I committed to, so by the sealed rule the ranking is not trusted.
2. **The primary sealed output could not be filled.** The pre-registered definition of a
   "non-Watson-Crick candidate" (wild-type identities cannot form a WC/wobble pair **and** no measured
   double restores one) leaves only **one** eligible pair with 3 or more informative doubles in the whole
   landscape, and it is not significant (G10-A38, n=3, mean epistasis 0.26, q=0.53). With up to 9 measured
   doubles per position pair, almost every pair contains some double whose two mutant identities are
   WC-complementary, so the filter excludes nearly everything. This is a flaw in the sealed design, not a
   property of QT45, and I am recording it rather than rewriting the criterion.

The third kill criterion was **not** hit: there are 4,914 informative doubles (threshold 200), and the
global nonlinearity clearly beats pure additivity out of sample.

## Data used

Zenodo record 13891380 (doi:10.5281/zenodo.13891380), MIT licence, file
`optimized_fitness_landscape_zenodo.zip`, directory `QT45/single_double_mutant_csvs/`. I did not download
the 2.3 GB or 0.86 GB archives in full: the zip central directory was read with an HTTP range request and
only the seven small processed CSVs plus the authors' analysis notebook were extracted by range
(about 1.8 MB total), into `experiments/qt45_epistasis/raw/` (not committed).

- 132 single mutants, 8,346 doubles (`double_mutant_fitness_all.csv`), fitness = log2 enrichment vs
  wild type (wild type = 0, floor near -14).
- Robustness copy: 7,212 doubles from `complete10_double_mutant_fitness_all.csv`.
- Wild-type variable region, from the authors' notebook:
  `GCAGGGCAGCGCAGTCGGACATTGATAACGGAATCGAGCCCGCC` = positions 2-45 (T = U). This reproduces all eight
  published pairs at the expected identities, which is the sanity check on the numbering.

Code: `experiments/qt45_epistasis/epistasis.py`. Outputs: `experiments/qt45_epistasis/results.json`.
Runtime about 24 s on 1 core under `taskpolicy -b nice -n 20`; the shared compute lock was not needed
(well under 10 CPU-minutes).

## Held-out numbers

20% of doubles held out (seed 20261119, stratified on informative/non-informative), models fitted on the 80%.
Out-of-sample R²:

| model | all held-out doubles (n=1669) | informative only (n=983) |
|---|---|---|
| M1 additive (`f1+f2`) | 0.655 | 0.807 |
| M2 additive + global nonlinearity `g` | **0.910** | **0.854** |
| M3 M2 + pair epistasis terms (18 pairs at FDR 5%) | 0.910 | 0.857 |

So the global nonlinearity (the floor) explains most of what looks like epistasis in this landscape;
**pair-specific epistasis adds essentially nothing out of sample** (+0.0005 overall, +0.002 on informative
doubles). Residual sd on informative doubles: 1.25 log2 units.

Processing robustness: the top 10 ranked pairs are identical between the two processings
(`double_mutant_fitness_all` vs `complete10`, overlap 10/10). A true cross-library hold-out was not
possible: the deposited QT45 processed data is one optimized library with three technical replicates, as
declared in the prereg.

## Positive controls recovered

Of the eight published pairs, five have 3 or more informative doubles; G10-C36, C17-G31 and G18-C30 are
lost to the floor. Ranks out of 718 scored pairs: **C11-U35 rank 1** (mean epistasis 5.12, q=0.020) —
the paper's only non-canonical pair comes out first — **C8-G39 rank 3** (3.14), **G7-C40 rank 5** (2.91),
**G6-C41 rank 22** (1.63), **U16-A34 rank 24** (1.55, q=0.16). Median mean-epistasis of the published
pairs: 2.91.

## Sealed predictions, verbatim

### A. Top 10 predicted non-Watson-Crick contacts

Only one pair met the sealed definition. Reported verbatim, unchanged:

```
1. G10-A38   n=3   mean epistasis 0.26   t=3.57   p=0.190   q=0.533   (not significant)
2.-10.  no further pair met the pre-registered non-Watson-Crick criterion
```

This prediction is **not** offered to a lab: by the sealed rule it is a null output.

### B. 10 triple mutants predicted to beat wild type

Model M3 extended to triples, `g(f1+f2+f3) + sum of the three FDR-5% pair terms`, all three constituent
doubles measured and informative; 1,450 triples considered. Verbatim, in rank order
(predicted fitness, log2 vs wild type = 0):

```
 1. G6U  C41U C42A   +4.53   doubles:  0.565, -0.142,  0.664
 2. G7U  C21U C40U   +4.03   doubles:  0.218, -1.371,  1.186
 3. C41U C42A G43U   +3.99   doubles:  0.664,  1.591,  0.026
 4. G6U  C41U G43U   +3.89   doubles:  0.565,  0.841,  1.591
 5. C41U C42A C44U   +3.73   doubles:  0.664,  1.714,  1.075
 6. G6U  C41U C44U   +3.69   doubles:  0.565,  0.503,  1.714
 7. G7U  C40U C44U   +3.59   doubles: -1.371, -1.520, -0.473
 8. G7U  C40U G43U   +3.59   doubles: -1.371, -0.498,  1.819
 9. C13A U23G C44U   +3.56   doubles:  0.519,  1.621,  0.814
10. G7U  C13A C40U   +3.37   doubles: -3.286, -1.371,  0.108
```

The same list is frozen machine-readably in `results.json` (`sealed_triples`). Nucleotide numbering is the
paper's; U is written for the T of the DNA-alphabet CSVs.

**Honest reading of B.** These are weak predictions. The isotonic `g` saturates at about +2.2 and the
informative additive range stops at +2.93, so every triple with three positive singles is extrapolation:
the ranking is driven by the pair terms on top of a saturated `g`, not by evidence about triples. Eight of
the ten involve the 3'-terminal positions 40-44, which the paper itself finds permissive in the basal stem
region. Entries 7, 8 and 10 are predicted to beat wild type although all three constituent doubles are
*below* wild type, which is a straightforward warning that the model is over-reaching.

## Post-hoc, not sealed: pairs whose wild-type identities cannot pair

Because criterion A emptied itself, I also ranked the pairs that merely fail the wild-type WC/wobble test
(the sealed criterion without the "no rescuing double" clause). This is exploratory and carries no
pre-registered error control:

```
C11-U35  n=3  mean 5.12  q=0.020   (the published non-canonical pair - positive control)
C30-A33  n=3  mean 3.20  q=0.033
C21-A22  n=6  mean 3.03  q=0.020
A20-C21  n=6  mean 2.72  q=0.048
A28-C30  n=3  mean 2.44  q=0.041
G39-G43  n=9  mean 2.32  q=0.020
C11-C30  n=3  mean 2.03  q=0.020
```

Five of the seven involve C30 or C21 and their immediate neighbours. C30's published partner G18 is itself
lost to the floor, and adjacent-position pairs (20-21, 21-22) cannot be tertiary contacts in any ordinary
sense, so most of this list is more plausibly local structure or a single-mutant artefact than a new
tertiary contact. It is written down so a later test can be sealed against it, not as a claim.

## Limits

- **The floor dominates.** With doubles reaching -14, a monotone `g` absorbs most of the signal; the
  paper's additive definition of epistasis (`f_double - f1 - f2`) therefore reports as "negative epistasis"
  what is largely saturation. That is the one genuinely useful methodological finding here, and it cuts
  against, not for, reading contacts off this landscape.
- **Coverage, not statistics, is the binding constraint.** 718 of 946 position pairs have 3 or more
  informative doubles, but three of the eight published pairs do not, so the data cannot see the
  interactions that are already known to exist in the core.
- **No independent library.** One optimized library, three technical replicates. The replicate agreement
  is high but says nothing about selection-level reproducibility.
- **Tertiary contacts in the paper are intermolecular.** Gianni et al. map QT45 tertiary contacts to the
  *primer-template-substrate* by 2'-deoxy substitution, not intramolecular contacts; the landscape used
  here can only speak to intramolecular pairs, so there is no overlap to check against.
- **No experimental structure.** An RCSB full-text search for "QT45 ribozyme" on 2026-11-19 returned
  HTTP 204 (no hits). The nearest experimental structure is the cryo-EM structure of the unrelated
  5TU/Harness polymerase ribozyme (McRae et al. 2024, PNAS 121, doi:10.1073/pnas.2313332121, found via
  Europe PMC). No AlphaFold or published 3D model of QT45 was located, so the weak external check in the
  prereg was not run; had one been available it would have been a model, not experimental data.

## Novelty position (Phase 0)

The idea was only partly novel and the paper is closer to it than the task assumed. Gianni et al. 2026
(doi:10.1126/science.adt2760) already derive secondary structure from the same epistasis data with their
own algorithm. From their Supplementary Text, verbatim:

> "To identify base-paired nucleotides, we developed an algorithm that analyzes mutation effects on
> epistasis and fitness. The algorithm first identifies all position pairs capable of forming Watson-Crick
> or wobble base pairs, then classifies double mutants involving candidate positions as either base pair-
> breaking or base pair-retaining."

> "The algorithm identified the following base pairs based on fitness and epistasis analysis: G10-C36,
> U16-A34, G18-C30, C8-G39, G7-C40, and G6-C41."

> "This analysis revealed strong evidence for canonical base pairs U16-A34, G7-C40, and C8-G39, as well as
> the non-canonical base pair C11-U35."

What they do **not** do is infer *tertiary* (non-WC, long-range) contacts from epistasis — their tertiary
contact mapping is experimental, by 2'-OH substitution against the primer-template-substrate, from the main
text:

> "In order to assess the QT45 ribozyme tertiary interactions with the primer-template-substrate, we mapped
> the location of the 2'-OH groups needed for efficient catalysis ... by 2'-deoxynucleotide substitution"

and they propose no fitter multi-mutants. So the gap was real; this run shows the open data cannot close it.

## References opened

- doi:10.1126/science.adt2760 (author manuscript text and SI, cached under `experiments/qt45_numbers/raw/`).
- https://zenodo.org/records/13891380 (API record and file list), doi:10.5281/zenodo.13891380.
- https://www.ebi.ac.uk/europepmc/webservices/rest/search (queries "QT45 ribozyme";
  "triplet polymerase ribozyme" AND epistasis) - 9 and 4 hits, no prior epistasis-to-contacts work on QT45.
- https://search.rcsb.org/rcsbsearch/v2/query (full text "QT45 ribozyme") - HTTP 204, no PDB entry.
