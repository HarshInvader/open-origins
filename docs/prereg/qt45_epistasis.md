# Pre-registration: QT45 tertiary contacts and fitter multi-mutants from the double-mutant fitness landscape (board task #30)

Agent: qt45. Written 2026-11-19, before any epistasis value was computed or inspected.

## Disclosure of what I had already read
- Gianni et al. 2026, Science 391:1022, doi:10.1126/science.adt2760 (author manuscript text and SI, cached in `experiments/qt45_numbers/raw/`). I read its fitness-landscape and epistasis Methods and Supplementary Text in full, including:
  - their base-pair-calling algorithm (Watson-Crick/wobble-capable pairs only, pair-retaining vs pair-breaking doubles, ranked by average epistasis of pair-retaining doubles);
  - the pairs it reported: G10-C36, U16-A34, G18-C30, C8-G39, G7-C40, G6-C41, plus non-canonical C11-U35, and C17-G31 from their large-positive-epistasis table (Table S4);
  - that their epistasis definition is `e = f_double - f_single1 - f_single2` with no global nonlinearity;
  - that the double-mutant fitness range runs to about -14 (a floor), far more negative than 5TU.
- The processed single- and double-mutant fitness CSVs from Zenodo 10.5281/zenodo.13891380 (MIT). Before writing this I inspected only: file names, column layout, row counts, and the **single**-mutant fitness distribution. I have not computed or looked at any double-mutant epistasis value.
- Wild-type QT45 variable region, recovered from the authors' notebook in the same record:
  `GCAGGGCAGCGCAGTCGGACATTGATAACGGAATCGAGCCCGCC` = positions 2..45 (DNA alphabet; T = U).

## Question
From the published QT45 double-mutant fitness landscape alone, can position pairs be ranked so that (a) pairs that are *not* Watson-Crick/wobble-capable and not in the published secondary structure come out as candidate tertiary/non-canonical contacts, and (b) a model of singles + pair epistasis nominates triple mutants predicted to exceed wild-type fitness?

Both outputs are sealed here and in `experiments/qt45_epistasis/RESULTS.md` so a lab can confirm or refute them.

## Data
- `double_mutant_fitness_all.csv` (8346 doubles, three technical replicates merged), `combined_single_mutant_fitness.csv` (132 singles), `complete10_double_mutant_fitness_all.csv` (7212 doubles, stricter read threshold), `complete10_single_mutant_fitness_all.csv`, from Zenodo record 13891380, `optimized_fitness_landscape_zenodo.zip`, directory `QT45/single_double_mutant_csvs/`. Fitness is log2 enrichment relative to wild type, so wild type = 0.
- Substitutions only. Deletion variants (`deletion_mutation_analysis.csv`) are excluded.

## Epistasis model
1. Additive score for a double mutant at positions i,j with mutations a,b: `x = f(i,a) + f(j,b)` from the single-mutant table.
2. Global nonlinearity: fit a monotone increasing function `g` of `x` to the observed double fitness `y`, by isotonic regression (PAVA, pool-adjacent-violators) on all doubles in the training set, then linearly interpolated.
3. Epistasis is the residual `e = y - g(x)`. This is the only epistasis measure used for ranking.
4. **Informative doubles.** Because of the floor near -14, a double carries information only where `g` has usable slope. A double is informative if:
   - both constituent single fitnesses are > -8, and
   - the additive score `x` is > -10, and
   - the observed fitness is > -13.5.
   Fewer than 200 informative doubles is a kill criterion.

## How position pairs are ranked
- For each unordered position pair (i,j) with at least 3 informative doubles, the statistic is the mean residual `mean(e)` over its informative doubles, and its t-like score `mean(e) / (sd(e)/sqrt(n))` is reported alongside.
- Pairs are ranked by `mean(e)`, descending (positive epistasis = mutual rescue = evidence of contact).
- Each pair is labelled:
  - **WC-capable** if any of its informative doubles produces a Watson-Crick or wobble pair (AU, UA, GC, CG, GU, UG) at (i,j);
  - **published** if it is one of G6-C41, G7-C40, C8-G39, G10-C36, C11-U35, U16-A34, G18-C30, C17-G31;
  - **non-Watson-Crick candidate** otherwise, i.e. the wild-type identities cannot form a WC/wobble pair and no rescuing double restores one. The sealed top-10 is drawn from this class only.

## Fair null
1. **Matched permutation null.** Pairs are binned by sequence separation `|i-j|` (bins 1-3, 4-7, 8-15, 16-30, >30) and by the mean of their constituent single-mutant fitnesses (quartiles of the pair-level mean, computed over all pairs). For each observed pair, the null distribution of `mean(e)` is built from 2000 draws in which residuals are permuted among informative doubles belonging to pairs in the same (separation, single-fitness) cell. Empirical one-sided p, then Benjamini-Hochberg FDR at 5%.
2. **Secondary-structure-only baseline.** The published 8 pairs are scored by the same statistic. A candidate contact counts as new information only if its `mean(e)` exceeds the median of the published pairs' `mean(e)`. If every pair above the significance threshold is a published WC pair, the verdict is negative: the landscape carries secondary structure and nothing more.

## Held-out design
- 20% of doubles held out at random (seed 20261119), stratified by informative/non-informative.
- Three models fitted on the 80%: (M1) pure additive `y = x`; (M2) additive + global nonlinearity `y = g(x)`; (M3) `y = g(x) + pair term`, where the pair term is the training mean residual for pairs passing FDR 5% and 0 otherwise.
- Reported: out-of-sample R² of M1, M2, M3 on the held-out doubles, on all held-out doubles and on informative ones only.
- Library hold-out: the record's QT45 processed data is one library (one optimized library, three technical replicates), so a true cross-library hold-out is not possible from these files. The substitute, declared in advance, is to repeat the whole ranking on `complete10_double_mutant_fitness_all.csv` (a stricter read-count processing of the same reads) and report the rank overlap of the top 10. This is a processing-robustness check, not an independent library.

## Planted check
- Simulate a landscape on the same 44 positions: single fitnesses taken as the real measured singles; 10 planted contacts drawn at random among pairs with separation > 3; for each planted pair, doubles that "restore" a complementary identity get +E epistasis (E drawn 2-8), others get 0; the sum is pushed through the empirical monotone `g` fitted to the real data, hard-floored at -14, and Gaussian noise matched to the real residual sd is added. Only the double genotypes actually measured in the real data are simulated, so coverage and the floor match.
- **Pre-set power:** the pipeline must place at least 5 of the 10 planted contacts in its top 20 ranked pairs, in at least 8 of 10 simulation replicates. Chance expectation is 10 x 20/990 ≈ 0.2 planted pairs in a top 20. Failing this is a kill criterion.

## Sealed outputs (committed before any comparison with outside structure)
- The top 10 predicted non-Watson-Crick contacts (ranked list of position pairs with the statistic).
- 10 triple mutants predicted to beat wild type (fitness > 0), from M3 extended to triples as `g(f1+f2+f3) + sum of the three pair terms`, requiring all three constituent doubles to be measured and informative; ranked by predicted fitness, reported with predicted values.

## Kill criteria
- The planted check fails the pre-set power above.
- Held-out R² of M2/M3 is no better than M1 (additive).
- Fewer than 200 informative doubles.

## External check (weak, and only after sealing)
No experimental QT45 structure exists: an RCSB full-text search for "QT45 ribozyme" on 2026-11-19 returned HTTP 204 (no hits). The nearest structure is the cryo-EM structure of the unrelated 5TU/"Harness" polymerase ribozyme (McRae et al. 2024, PNAS 121, Europe PMC hit). If an AlphaFold or other published 3D *model* of QT45 appears, scoring contacts against it is a weak check only: a model is not experimental data.
