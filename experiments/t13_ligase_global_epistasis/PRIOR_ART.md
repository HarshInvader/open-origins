# Prior art for T13: has anyone fitted a global-epistasis model to the Rotrattanadumrong & Yokobayashi ligase landscape?

Written before any model was fitted. Everything cited below was opened and read in this repo; quotes
are verbatim from the files in `raw/europepmc/` and `raw/prior_art/` (both gitignored).

**Verdict: no. Proceed with the study.** Of the 41 works that cite the paper, none fits a latent-additive
score through a monotone curve (a global / nonspecific epistasis model) to this ligase dataset, and none
re-analyses the generation-8 "higher-order epistasis" claim at all. Two of the works the plan flagged as
possible prior art (Martí-Gómez et al. 2026; Faure & Lehner 2024) cite the dataset only in passing lists
and demonstrate their methods on other landscapes. One (Beck/Charest et al. 2023) re-analyses ribozyme
landscapes with an information-theoretic method and explicitly sets global-curve methods aside as
unsuited to complex landscapes — which is a motivation for this study, not an answer to it.

## The paper under test

Rotrattanadumrong & Yokobayashi 2022, "Experimental exploration of a ribozyme neutral network using
evolutionary algorithm and deep learning", Nat. Commun. 13:4847, doi:10.1038/s41467-022-32538-z,
PMC9385714. Read in full from `raw/europepmc/PMC9385714.txt`.

The claim this study tests (line 33, verbatim):

> "In generation 8, almost all neutral mutants identified were expected to be deleterious under the
> epistasis-free model. This indicated that the neural network was able to learn higher-order, nonlinear
> mutational effects, and identify distant neutral mutants that would have been inaccessible through in
> silico selection, mutation, and recombination alone."

The authors themselves flag the gap this study fills (line 54, verbatim):

> "Finally, some of the nonlinearities identified in this library could be attributed to global noise from
> experimental errors. We used the RA values calculated from the mean of the two replicates to reduce
> experimental errors. Furthermore, any global nonlinearities would also have affected the MLP
> predictions, because the same dataset was used to train it. Therefore, our conclusion remains robust in
> terms of the predictability of this dataset using the current model. Further statistical tests could be
> performed to remove global nonlinearities, which could improve model performance."

That is a statement that the test was *not* done. "Epistasis-free" in the claim means their own
log-additive model on the measured scale: the product of the single mutants' relative activities. An
additive latent score passed through one saturating curve carries no specific interaction either, yet it
predicts exactly the pattern they read as higher-order epistasis — which is why the test is worth running.

Other load-bearing lines from the same file: line 22 (the log-additive model and its 75.5% accuracy on
generation 1), line 24 (the RA >= 0.2 neutrality threshold), line 32 ("the fraction of neutral mutants in
generation 8 was only 0.28"), line 53 (Walsh-Hadamard: R2 0.54 for 1st+2nd order, "only the 3rd order
terms were required to achieve an accuracy similar to that of the current MLP model (R2 ~ 0.72)"),
line 71 (RA definition and read filtering), line 86 (MLP architecture), and the Fig. 3a caption
("trained on 20,920 variants from generations 1-6 ... held-out testing set of 8967 variants").

## How the citing literature was screened

Public APIs only, User-Agent `open-research-site/1.0`, no personal details in any request, no paywall or
bot-block evasion. Raw responses are kept in `raw/prior_art/`.

| Source | Query | Result |
|---|---|---|
| Europe PMC citations | PMID 35977956 | 27 citing records; every abstract pulled (`ab_*.json`) and read |
| OpenCitations COCI | doi:10.1038/s41467-022-32538-z | 30 citing DOIs; the 7 not in Europe PMC checked via Crossref (`cr_*.json`) |
| Crossref | same DOI | `is-referenced-by-count` = 41 |
| Europe PMC search | `"global epistasis" AND "ligase ribozyme"` | 0 hits |
| Europe PMC search | `"neutral network" AND ribozyme AND ("global epistasis" OR "nonspecific epistasis")` | 0 hits |
| Europe PMC search | `zenodo AND "6945203"` | 1 hit (the paper itself) |
| Europe PMC search | `"ligase ribozyme" AND (reanalysis OR re-analysis) AND epistasis` | 1 hit (an artificial-life review, no refit) |
| Europe PMC search | `"global epistasis" AND (ribozyme OR RNA) AND "latent"` | 20 hits, all general method or other systems |
| Europe PMC search | `Rotrattanadumrong` | 10 hits, all by the same group, none a refit of this landscape |
| arXiv | 4 queries on global epistasis + ribozyme / neutral network | 0 relevant |
| Zenodo | `ligase ribozyme` | 3 records, none a re-analysis |

Three citing full texts were opened in full because their abstracts put them closest to this study.

## The three closest papers

### Martí-Gómez, Zhou, Chen, Kinney, McCandlish 2026, gpmap-tools (MBE), PMC12911936

Cites this dataset only once, in an introductory list of combinatorially complete landscapes (line 10).
Its worked examples are the Shine-Dalgarno sequence and other short elements, not the ligase. Its own
stated limitation (line 105, verbatim) is the opposite of prior art here:

> "First, MEI and VC regression are phenomenological models. As such, they do not explicitly model global
> or nonspecific epistasis that often arises from nonlinear dependencies between the underlying quantities
> affected by mutations and our measurements"

So the method the plan worried might already have been applied to this dataset does not model global
epistasis at all, and was not applied to this dataset.

### Faure & Lehner 2024, "The genetic architecture of biomolecular phenotypes" (PLoS Comput Biol), PMC11161127

Cites this paper as one of refs 5-13 in an introductory DMS list (line 12, verbatim):

> "In particular, DMS enables the systematic measurement of mutational effects across entire
> combinatorially complete genetic landscapes [5-13]."

Its empirical work is on tRNA and protein-domain landscapes. Global epistasis appears only as a reason to
prefer regression over direct Walsh-Hadamard computation (line 128, verbatim):

> "However, estimating epistatic coefficients by regression-as in Eq (12)-is a more natural choice in the
> presence of missing data, when data for multiple related phenotypes is available [23] and/or in the
> presence of global epistasis [24, 25]."

No fit to this dataset.

### Charest, Shea et al. 2023, "Discovering pathways through ribozyme fitness landscapes using information theoretic quantification of epistasis" (RNA), PMC10578471

The only citing paper that engages with this study's substance. It describes the authors' MLP as a black
box and dismisses global-curve methods as a class (line 13, verbatim):

> "Attempts to model epistasis include using simple nonlinear functions to capture latent, nonepistatic
> traits (Kondrashov and Kondrashov 2015; Starr and Thornton 2016; Sailer and Harms 2017; Otwinowski et al.
> 2018), and machine learning models (Sarkisyan et al. 2016; Yang et al. 2019). The former technique
> performs well for relatively simple systems in which there is a largely additive landscape subject to
> random variation, but not for more complex landscapes. ... While the approach effectively identified
> neutral mutants of the ribozyme, the perceptron itself constituted a 'black box' (Rotrattanadumrong and
> Yokobayashi 2022)."

That is an assertion that a global curve would not do here, made without fitting one to this dataset.
It is the hypothesis T13 tests, stated as a premise.

## Everything else

The remaining citing records are, by abstract: ribozyme and aptamer engineering, directed-evolution
method papers, deep-learning sequence-design papers, origin-of-life reviews, and unrelated applications.
The closest by phrasing is a preprint on AAV capsids (PPR1349324) that models "sitewise effects
transformed by global epistasis" — the right model, a different system, no contact with this dataset.

## In-repo precedent

Study QT45 (`experiments/qt45_epistasis/`) fitted the same shape of model (additive latent score plus an
isotonic monotone curve) to a different landscape: held-out R2 went 0.655 -> 0.910 with the curve, and
adding pairwise terms gained 0.0005. T13 reuses that approach, with the curve in parametric form so it can
be fitted jointly and simulated from.
