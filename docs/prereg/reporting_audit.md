# Pre-registration: are step-end conditions reported in prebiotic multi-step syntheses? (board task #31)

Agent: audit. Written 2026-11-19, before any paper in either sample was drawn, opened or scored.

## Disclosure of what I had already seen
- `experiments/ledger/RESULTS.md` (#29): pH was checkable at 2-4 of 17-20 hand-offs in six RNA routes. Those six papers can appear in the sample by chance; they are not excluded or forced in.
- `experiments/redteam_pathway/RESULTS.md` (#21).
- Before sealing I ran both queries below once to check their syntax and hit counts (264 and 215 hits on 2026-11-19), which printed the first five titles of each. No paper was opened.

## Question
In open-access prebiotic multi-step syntheses, how often do papers report the conditions at the end of each step, so that the hand-off to the next step can be checked? How does that compare with multi-step synthesis papers from a field with reporting norms?

## Sampling frame (fixed)
Europe PMC REST search (`/webservices/rest/search`, `resultType=lite`, cursorMark paging, all hits), run once after sealing.

**Prebiotic query (exact string):**
```
(TITLE_ABS:"prebiotic") AND (TITLE_ABS:"synthesis" OR TITLE_ABS:"formation") AND (TITLE_ABS:nucleotide* OR TITLE_ABS:nucleoside* OR TITLE_ABS:sugar* OR TITLE_ABS:ribose OR TITLE_ABS:"amino acid*" OR TITLE_ABS:peptide* OR TITLE_ABS:lipid* OR TITLE_ABS:"fatty acid*" OR TITLE_ABS:phospholipid*) AND OPEN_ACCESS:y AND HAS_FT:y AND PUB_YEAR:[2010 TO 2025] AND PUB_TYPE:"research-article" AND SRC:MED
```

**Comparison query (exact string), Beilstein J Org Chem (fully open access):**
```
(JOURNAL:"Beilstein J Org Chem") AND (TITLE_ABS:"total synthesis" OR TITLE_ABS:"multistep synthesis" OR TITLE_ABS:"multi-step synthesis" OR TITLE_ABS:"steps") AND OPEN_ACCESS:y AND HAS_FT:y AND PUB_YEAR:[2010 TO 2025] AND PUB_TYPE:"research-article" AND SRC:MED
```

**Random order.** Hits with a PMCID are de-duplicated and sorted by PMCID (numeric). The order is `numpy.random.default_rng(0).permutation(n)` for each list separately. Papers are screened in that order until 40 prebiotic and 20 comparison papers are eligible. This is equivalent to a seed-0 random sample from the eligible list. Every screened paper and its exclusion reason is logged in `experiments/reporting_audit/screening.csv`.

**Eligibility (both sets, same rules).**
- E1. Original experimental wet-lab chemistry. Excluded: reviews, perspectives, purely computational or theoretical papers, and analytical papers that only detect or quantify compounds (e.g. meteorite or ice analysis) without a synthesis.
- E2. At least one hand-off: the product of one reported reaction step is an input of a further reported reaction step in the same paper, whether used in situ, as a crude mixture or after isolation.
- E3 (prebiotic set only). The chemistry is framed by the authors as prebiotic, and the products are nucleobases, nucleosides, nucleotides, sugars, amino acids, peptides, lipids or amphiphiles, or precursors the authors present as leading to these.
- E4. Full text open in PMC / Europe PMC. Retractions are excluded.
- E5. Published 2010-2025 (the query enforces this).

## Unit and segmentation
- **Step.** A reaction the paper presents as a distinct operation producing a named product (a numbered step, a scheme arrow, or a separately described procedure). Workup alone is not a step.
- **Main sequence.** The longest chain of steps leading to the paper's headline product, as drawn in the main-text scheme. If there are several, take the first one the text describes.
- **Hand-off.** Step n → step n+1 on the main sequence, where a product of step n is an input of step n+1. At most the first 5 hand-offs per paper are scored, in order, so that long total syntheses do not dominate.

## Items per hand-off (scored from main text and open SI only)
"Reported" means stated numerically (or named, for solvent) for the end of step n, or derivable from numbers the paper states. "Standard conditions", "rt" or "ambient" without a number in the paper do not count.
1. **end_pH.** Codes: `E` = pH at the end of step n is stated, or the step was held at a stated pH (buffer of stated pH, pH-stat); `S` = only the starting pH of an unbuffered step is stated; `N` = none; `NA` = the medium at the end of step n has no bulk water (organic solvent, neat organic reagent, gas phase). For dry-down or solid-state steps made from an aqueous solution, the pH of that solution counts, so the code is not NA. Primary: reported = `E`.
2. **end_T.** `Y` = numeric temperature for the final stage of step n (e.g. "25 °C", "rt (20-25 °C)" if defined numerically somewhere in the paper); `N` otherwise. Bare "rt" is coded `N`, with a flag `rt_only=1` for a sensitivity analysis.
3. **end_conc.** `Y` = the concentration or amount of the carried product at the end of step n is stated, or computable from stated numbers: a yield plus the scale and volume, or an isolated mass or yield if the product was isolated. `N` otherwise.
4. **solvent.** `Y` = the medium at the end of step n is named (solvent, buffer composition, "neat", "dry film"); `N` otherwise.
5. **carry.** `Y` = for every input of step n+1 the paper makes clear whether it was carried over from step n's mixture, isolated or purified from step n, or freshly added (commercial or separately prepared, including an authentic sample of the intermediate). `N` = at least one input's source is unclear. Also recorded: `uses_authentic` = `Y` if step n+1, as demonstrated, used a commercial or separately prepared sample of step n's product rather than step n's own output; `N`; `U` unclear.
6. **workup.** `Y` = the transition is described: a workup or purification procedure, or an explicit "used directly" or "same pot". `N` otherwise.

**"All four numeric items"** = end_pH (`E`, or `NA`), end_T `Y`, end_conc `Y` and solvent `Y`.

## Coding procedure
- **Primary coding.** Subagents, each given only this codebook section (Unit, Items, Coding procedure), not the predictions. Each batch mixes prebiotic and comparison papers. Full text comes from Europe PMC `fullTextXML`; SI comes from the Europe PMC `supplementaryFiles` endpoint (PDFs converted with pdftotext). SI that cannot be legally opened is recorded as `si_status=blocked`, and items found only there count as not reported.
- **Reliability.** A fresh subagent re-codes 10 papers drawn at random (seed 1: 7 prebiotic, 3 comparison) and is blind to the primary scores. It receives the primary hand-off list (step n product → step n+1), so the test is of item scoring, not of segmentation. #29 showed segmentation is the larger problem, and that limit will be stated.
- **Kappa.** Cohen's kappa per item at hand-off level on the binary reported / not reported. For end_pH: `E` vs not; rows where either coder says `NA` are dropped, and NA agreement is reported separately. If both coders give one constant value with full agreement, kappa = 1.
- **Kill criterion.** Mean kappa over the 6 items < 0.6. The predictions are then reported as scored but not interpreted, and the entry goes to NEGATIVE_ATLAS.

## Sealed predictions
- **P1.** Prebiotic set: the median across papers of the per-paper fraction of hand-offs with end_pH = `E` is below 0.30. NA hand-offs are excluded from the fraction, and papers with only NA hand-offs are excluded.
- **P2.** Fewer than 20% of prebiotic papers have carry = `Y` at every scored hand-off.
- **P3.** The share of hand-offs with all four numeric items (pooled over hand-offs) is lower in the prebiotic set than in the comparison set. Test: 10,000 bootstrap resamples (seed 0), resampling papers with replacement within each set. P3 holds if the 95% percentile CI of (prebiotic − comparison) lies entirely below 0.
- **P4 (descriptive).** Prebiotic set: Spearman rho between publication year and the per-paper fraction of hand-offs with all four items has |rho| < 0.2.

**Sensitivity analyses (reported, not used for verdicts):**
- P1 and P3 with `S` counted as reported;
- P3 with NA counted as not reported (strict);
- P3 with bare "rt" counted as reported;
- P3 with per-paper means instead of pooled hand-offs.

**Planted check, run before real data.** `audit.py` must recover the known proportions, and a known difference of −0.3 between sets, from a synthetic extraction table (60 papers, seed 0) to within ±0.05, and must give a CI containing 0 for a planted zero difference.

## What would count as a strong result
P1-P3 hold and kappa ≥ 0.6. That would make a checklist backed by data, not just a proposal: the specific items prebiotic papers omit, measured against a field with norms. P3 failing would also be informative, since it would mean the gap is not specific to prebiotic chemistry.

## Outputs
In `experiments/reporting_audit/`:
- `sample.py` (frame and sampling);
- `screening.csv`;
- `extraction.csv` (one row per hand-off);
- `reliability.csv`;
- `audit.py`;
- `results.json`;
- `RESULTS.md`;
- `ledger_rows.csv`.
