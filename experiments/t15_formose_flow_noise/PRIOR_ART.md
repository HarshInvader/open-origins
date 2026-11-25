# Prior art for T15: has anyone checked van Duppen et al.'s dynamic-vs-steady-state shifts against repeat-run noise?

Written before any dynamic-run mean was computed. Everything cited below was opened in this repo. Quotes are
verbatim from the files in `raw/europepmc/`, `raw/si/`, `raw/github/src/` and `raw/prior_art/` (all
gitignored). Titles and author lists come from Europe PMC or Crossref metadata saved in `raw/prior_art/meta/`
and `raw/prior_art/crossref/`.

**Verdict: no. Proceed with the study.** No citing work re-tests the size of the dynamic-vs-steady-state
shifts against run-to-run noise or serial correlation. The paper's p-values come from Student's
two-sample t-test (`scipy.stats.ttest_ind`, equal variances by default) applied to the serial samples of
one run against those of another, so every sample counts as an independent draw. The SI does not name or
describe the test. It was found in the authors' deposited code, which was read as text and not run.

## The paper under test

van Duppen P, Daines E, Robinson WE, Huck WTS. 2023. "Dynamic Environmental Conditions Affect the
Composition of a Model Prebiotic Reaction Network." J Am Chem Soc 145:7559-7568. doi:10.1021/jacs.3c00908,
PMC10080678, PMID 36961990 (Europe PMC metadata). Full text read from `raw/europepmc/PMC10080678.xml`.

Claims (verbatim):

> "Surprisingly, the product compositions of the formose reaction under dynamic conditions deviate
> significantly from those under steady state conditions." (Abstract)

> "Surprisingly, despite the system having the same average concentrations of Ca(OH)2 compared to an
> unperturbed reaction, the measured concentration distributions vary significantly (at least p ≤ 1 × 10–4
> in each series for compounds 3, 5, 7, and 11) in response to fluctuations in [Ca(OH)2]in." (amplitude series)

> "Again, we observed average concentrations of compounds which deviate from steady-state averages (3, 5,
> 7, and 11; p ≤ 1 × 10–4, in all compound series; see Figures S12 and S13)." (rate series)

The four compounds are named in the Figure 2 caption: "(a) DHA (3), (b) threose (5), (c) erythrulose (7),
and (d) xylulose (11)". They match rows 3, 5, 7 and 11 of the deposited `info_files/compound_information.csv`.

What the paper says about the samples and the noise (verbatim):

> "For each experimental condition, the CSTR was left to equilibrate to the applied dynamics for 30 min
> before 50 samples were collected with time intervals of 40.8 s (or 30.6 s for EXP013)."

> "Groups of experiments were performed on the same day with equilibration periods between them
> (EXP001-EXP003, EXP004-EXP006, EXP007-EXP009, and EXP010-EXP012)."

> "This variation is due to experimental noise introduced by factors such as the time taken for sample
> freeze-quenching and variations in mixing inside the reactor which we were unable to eliminate. This
> variance is constant across the data set."

> "p-Values were calculated as indicators for the significance of the difference between means" (Figure 2
> and Figure 3 captions)

Table 1 (from the XML) lists two pairs of runs at identical settings: EXP001 and EXP010 (σ = 0, steady
state, 50 mM formaldehyde), and EXP003 and EXP012 (σ = 5.75 mM, 45 s steps, 50 mM). The paper does not
compare either pair, and it does not mention them as replicates.

## Which test, and does it treat samples as independent?

The SI (`raw/si/ja3c00908_si_001.pdf`, 13 pages, sha256
`0864636d08b0f2d9ef7446ad78ddeb62d0e1debd724ad4a9f61f60ff5c6b575e`, from the Europe PMC supplementary-files
endpoint) has no statistical methods section. A search of its text for "t-test", "test", "p-value",
"statistic", "independent", "Welch" and "Mann" finds nothing. Figures S6-S13 are violin plots.

The deposited code (`github.com/huckgroup/Formose_2022`, commit 94c10347154fac67371c5b9101ce79ffaf70ffdc,
read as text) answers the question. In `processing_scripts_formose/data_analysis_functions.py`, function
`data_p_values` (verbatim):

```
        result = stats.ttest_ind(dist_1, dist_2, nan_policy="omit")
```

`dist_1` and `dist_2` are the whole concentration series of two runs (about 43 to 50 samples each). So:

- **Test:** Student's two-sample t-test with pooled variance (scipy's default `equal_var=True`).
- **Independence:** every sample in a run counts as an independent draw. The samples are taken in
  sequence from one reactor, 30.6 to 40.8 s apart, with a 120 s residence time, so neighbouring samples share
  liquid. Nothing corrects for serial correlation, and nothing models variation between runs or days.
- **Missing values:** `data_report.py` reads `"nan"` cells as 0 (`0 if x == "nan" else float(x)`), so a
  missing value enters the test as a zero. In the 12 runs used here, no row has a missing value for the four
  compounds.
- **Multiple testing:** `plotting_functions.py` passes the raw p-values to `statannotations`
  (`annotator.set_pvalues(p)`) with no correction, over about 20 compounds × 3 pairs × 4 series.
- `01_composition_analysis.py` sets the comparison sets `[EXP004, EXP005, EXP006]`, `[EXP001, EXP002, EXP003]`,
  `[EXP007, EXP008, EXP009]` and `[EXP010, EXP012, EXP011]`. The first run of each set is the steady state.

## The group's follow-ups (named in the plan)

**Baltussen MG, de Jong TJ, Duez Q, Robinson WE, Huck WTS. 2024.** "Chemical reservoir computation in a
self-organizing reaction network." Nature. doi:10.1038/s41586-024-07567-x, PMC11254755. Full text opened.
It cites the paper as reference 23 (verbatim):

> "Our recent work on dynamic self-organization of chemical reaction pathways in the formose reaction4,23
> inspired us to consider its propensity for information processing."

It builds on the result. It does not re-test it. It reports its own steady-state outputs as reproducible
(verbatim): "These data establish a large dataset that is deterministic (Supplementary Information section
3.2 and Supplementary Fig. 7) and robust against outliers and overfitting." Its averaging is over "the final
10-minute sample period of the steady-state output" from a mass-spectrometry stream. That is a different
setup from the GC-MS run means tested here, and no between-run comparison of the 2023 runs is made.

**de Jong TJ, Demertzi AD, Robinson WE, Huck WTS. 2025.** "Environmental History is Transferred via Minerals
Altering Formose Reaction Pathways." Angew Chem Int Ed 64:e202504659. doi:10.1002/anie.202504659,
PMC12124346. Full text opened. It cites the paper (with Robinson et al. 2022) as references 11 and 12 (verbatim):

> "Our previous work on the formose reaction, a model prebiotic CRN, has shown that its outcomes are
> significantly shaped by modulating the concentration of the catalyst Ca(OH)2.[ 11 , 12 ]"

The study is a batch study with minerals. It takes the 2023 result as given and does not reanalyse it.

## Other citing works (screened by abstract or title)

Europe PMC lists 25 citing records (`meta/citations_epmc.json`) and OpenCitations lists 37 citing DOIs, 30
distinct (`meta/citations_oc.json`, Crossref metadata for each in `crossref/`). Abstracts were read from
Europe PMC (`citing_abstracts.txt`) or Crossref where available. None reanalyses the 2023 data, discusses
its replicate runs, or raises serial correlation. They fall into these groups:

- **Computational formose chemistry.** Kua and coworkers (Life 2024, 2025, 2026), Kan et al. (J Chem Phys 2025;
  JACS Au 2026), Venturini & González (ChemPlusChem 2024).
- **Other experimental formose work.**
  - Nishijima et al. 2026 (Angew Chem, PMC12910140; full text opened). It cites the paper in an introductory
    list only. Its own reproducibility note concerns its own samples: "the trends observed in both the VK
    diagrams and KMD plots for NaOH‐ and Ca(OH)2‐catalyzed reactions were reproduced when independently
    prepared samples were analyzed using different instruments".
  - Chikatani et al. 2025; Tabata et al. 2023, 2024; Xu et al. 2025; Briš et al. 2024 (same group, analytics);
    Sutton et al. 2025 (Chem).
- **Reviews and perspectives.**
  - Hashidzume 2025, BBA Adv, PMC11835704 (full text opened). It summarises the claim without assessing it:
    "Huck et al. [75] investigated the product distribution of formose reaction under similar flow conditions
    at varying the magnitudes and rates of temporal fluctuation of the concentrations of Ca2+ and OH–".
  - Menor-Salván & Ruiz-Bermejo 2025; Edri et al. 2025; Csizi & Lörtscher 2024; Gentili & Stano 2024;
    Sangchai et al. 2023; de Jong, Trigka & Lerch 2024.
- **Unrelated systems.** Kurpik et al. 2024 (Pd/Pt network); Huang et al. 2026 (nucleopeptides); Matange et al.
  2025 (Nat Chem, chemical evolution of mixtures); Kurrle et al. 2025 (Wöhler RNA); Roszak et al. 2024; Ito
  et al. (SSRN); Tran, Yi & Fahrenbach 2023.

## Searches that found nothing relevant

- **Europe PMC.** `"formose" AND ("autocorrelation" OR "reproducibility" OR "replicate runs") AND ("flow" OR
  "CSTR")` gave 21 hits (`meta/search_epmc.json`). By title, none reanalyses the 2023 runs.
- **arXiv.** `all:formose` returned no entries.
- **GitHub.** The one fork of Formose_2022 (`anirban-a/Formose_2022`) is 0 commits ahead of the original.
  Repository search for "formose" lists the Huck group's later repositories. One,
  `huckgroup/formose_collective_dynamics` (created 2026-09), has a README naming a manuscript "Emergence of
  Collective Dynamics in a Driven Prebiotic Chemical Network" (de Jong, Baltussen, Robinson, Huck). Europe
  PMC and Crossref title searches found no published record of it (`meta/search_collective.json`,
  `meta/crossref_collective.json`). Only its README was read. It is not cited as evidence here.

## What this means for the study

The question is open. The paper's comparisons are all within one day. The only repeat runs at identical
settings were done on different days (EXP001 with EXP002 and EXP003; EXP010 with EXP011 and EXP012). So the
test can ask whether the dynamic-vs-steady shifts exceed the shift between repeat runs on different days. It
cannot measure run-to-run noise within a day, because the deposit has no such repeats.
