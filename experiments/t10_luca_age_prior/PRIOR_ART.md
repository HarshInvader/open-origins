# T10 prior art: has anyone moved the 4.52 Ga maximum or the rate prior behind Moody 2024's LUCA date?

Written 2026-11-24 by the T10 prep agent. This is study S4 in `docs/plans/next_studies_2026-11-24.md`. No posterior from any of our MCMCtree runs was read while this was written. I did not open the authors' published posterior or prior summaries (`sum_files_post/`, `sum_files_prior/`).

"Opened" means I fetched the full text in this session and read the passage quoted. "Title only" means I saw the title in a search result, and those papers carry no claim here. All requests used the User-Agent `open-research-site/1.0` and no name or email. Saved responses are in `raw/prior_art/` (gitignored). A search that finds nothing is weak evidence.

## Short answer

1. **Prior art does not settle the question.** No paper I found reruns Moody 2024's data with a different maximum on LUCA or the root, or with a different rate-prior mean. Moody's own sensitivity runs change the data (per gene, leave one gene out, a richer substitution model), the partitioning and the cross-bracing. They do not change the maximum or the rate-prior mean.
2. **The nearest evidence is from the same group and points one way.** Mahendrarajah et al. 2023 dated a different tree (ribosomal proteins and ATP synthase, McmcDate) with the same 4.52 Ga maximum. Their LUCA interval reaches the maximum (4.52–4.32 Ga). They write that "the credibility interval associated with the LUCA still clashes against the root hard-maximum", and that the age of LUCA "is sensitive to the root calibration used". They cite two studies with younger maxima (3.9 and 3.8–4.1 Ga) whose LUCA intervals also reach their own maxima. Their data are not Moody's, and Moody's interval (4.09–4.33 Ga) does not reach 4.52. So the question is still open for Moody's data. Prior art does make a P1 shift the expected outcome.
3. **Two papers use Moody's date and comment on prior sensitivity, but neither tests it.** Kay et al. 2026, with overlapping authors, left out universal-paralogue duplication nodes because such a node "is also the root and, therefore, sensitive to the root prior used in the molecular clock analysis". Schrago & Mello 2024 note that LUCA's age is "close to the maximum bound set by the Moon-forming impact".
4. **The plan's gate cites the wrong dataset.** The abstract's 4.09–4.33 Ga comes from the partitioned dataset. The plan's R0, and the `in.BV` it names, use the concatenated dataset. See "What this changes for the design".

## Mahendrarajah et al. 2023 (opened)

Mahendrarajah et al. 2023, Nat. Commun. 14, doi:10.1038/s41467-023-42924-w, "ATP synthase evolution on a cross-braced dated tree of life". Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10656485/fullTextXML`, saved as `raw/prior_art/PMC10656485.xml`. Supplementary Information was not opened.

What it reports about the maximum:

- "We estimate that LUCA lived 4.52–4.32 Ga and 4.52–4.42 Ga in the braced and non-braced analysis, respectively (Fig. 5A, Supplementary Fig. 16). Ages towards the younger end of the spectrum from our braced analysis seem more plausible considering the Moon-forming impact at 4.52 Ga, though both ages imply a rapid origin of LUCA following this putative sterilization event."
- "However, as observed in previous studies19,27, the credibility interval associated with the LUCA still clashes against the root hard-maximum represented by the moon-forming impact even when implementing cross-bracing. This indicates that bracing helps to ameliorate, though not completely resolve, the problem of an under-calibrated clock inferring rates that are too low to account for the amount of genetic change that has occurred since the root of the universal tree19,93."
- "Some recent studies have reported moderately younger age estimates for LUCA: 4.05–3.42 Ga94, or a range of values 4.48–3.93 Ga depending on conditions95. An important driver of these differences is the choice of root maximum, which was younger in both studies (3.8–4.1 Ga95 and 3.9 Ga94). In turn, also in those studies94,95, the credibility interval for the age of LUCA clashes against the maximum used to calibrate the root node. This is consistent with previous work suggesting that the age of LUCA is sensitive to the root calibration used19,21,27,95,96."
- "We used the age of the Earth as our root maximum (the moon-forming impact at 4.52 Ga) because we are unaware of any compelling evidence for a younger maximum on the age of extant life (Supplementary Material)."

The references, from the paper's list: 19 is Moody et al. 2022, eLife (doi:10.7554/eLife.66695); 21 is Coleman et al. 2021, Science; 27 is Betts et al. 2018, Nat. Ecol. Evol.; 93 is Zhu et al. 2019, Nat. Commun.; 94 is Fournier et al. 2021, Proc. Biol. Sci. (doi:10.1098/rspb.2021.0675); 95 is Mateos et al. 2023, Sci. Adv. (doi:10.1126/sciadv.ade4847); 96 is Parsons et al. 2021, Geobiology. I did not open 19, 21, 27, 93, 94, 95 or 96.

What it reports about the rate prior: nothing in the main text. The method is different: "We used McmcDate ... McmcDate approximates the phylogenetic likelihood using a multivariate normal distribution", with "an uncorrelated log normal relaxed molecular clock model" and calibrations as "uniform distributions with bisected normal distributions at the boundaries".

So the paper reports no run with a moved maximum. It argues from the comparison across studies that the maximum drives the LUCA age, and its own interval is pressed against 4.52.

## Moody et al. 2024: their prior and their sensitivity checks (opened)

Moody et al. 2024, Nat. Ecol. Evol. 8, doi:10.1038/s41559-024-02461-1. Full text from `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11383801/fullTextXML`, saved as `raw/prior_art/PMC11383801.xml`.

The maximum:

- "We used soft-uniform bounds, with the maximum-age bound based on the time of the Moon-forming impact (4,510 million years ago (Ma) ± 10 Myr), which would have effectively sterilized Earth's precursors, Tellus and Theia13."
- "Some previous studies have placed a younger maximum constraint on the age of LUCA based on the assumption that life could not have survived Late Heavy Bombardment (LHB) (~3.7–3.9 billion years ago (Ga))19. ... Thus, the LHB hypothesis should not be considered a credible maximum constraint on the age of LUCA."
- Note: the text says "soft-uniform", but the repository's `Calibnodes.csv` gives the LUCA bound as `B{3.3470,4.5200,1e-300,1e-300}` and the root as `U(4.520,1e-300)`. Both tails are 1e-300, so in practice both bounds are hard. The input tree has the same strings.

The rate prior:

- "We specified a vague rate prior with the shape parameter equal to 2 and the scale parameter equal to 2.5: Γ(2, 2.5). This gamma distribution is meant to account for the uncertainty on our estimate for the mean evolutionary rate, ~0.81 substitutions per site per time unit, which we calculated by dividing the tree height of our best-scoring ML tree (Supplementary Information) into the estimated mean root age of our phylogeny (that is, 4.520 Ga, time unit = 109 years ...)."

Which dataset gives the headline numbers:

- "The duplicated LUCA node age estimates we obtained under the autocorrelated rates (geometric Brownian motion (GBM))29,30 and independent-rates log-normal (ILN)31,32 relaxed-clock models with our partitioned dataset (GBM, 4.18–4.33 Ga; ILN, 4.09–4.32 Ga; Fig. 1) fall within our composite age estimate for LUCA ranging from 3.94 Ga to 4.52 Ga".
- "Our main analysis consisted of inferring the timetree for the partitioned dataset under both the GBM and the ILN relaxed-clock models in which nodes that correspond to the same divergences are cross-braced (that is, hereby referred to as cross-bracing A)."

Sensitivity checks (what they varied):

- "In addition, we ran 10 additional inference analyses to benchmark the effect that partitioning, cross-bracing and relaxed-clock models can have on species divergence time estimation: (1) GBM + concatenated alignment + cross-bracing A, ... (6) ILN + concatenated alignment + cross-bracing A, ..."
- "Lastly, we used (1) individual gene alignments, (2) a leave-one-out strategy (rate prior changed for alignments without ATP and Leu, Γ(2, 2.2), and without Tyr, Γ(2, 2.3), but was Γ(2, 2.5) for the rest; see 'Additional methods'), and (3) a more complex substitution model94 to assess their impact on timetree inference."
- "Dating analyses based on single genes, or concatenations that excluded each gene in turn, returned compatible timescales (Extended Data Figs. 1 and 2 ...)."
- The prior check: "Lastly, we assessed the impact that truncation may have on the estimated divergence times by running MCMCtree when sampling from the prior (that is, the same settings specified above but without using sequence data, which set the prior distribution to be the target distribution during the MCMC)."
- On what the prior check is for: "we are not attempting to test the hypothesis that the fossil record is an accurate temporal archive of evolutionary history because it is not28."
- Convergence protocol: "Note that if tail-ESS and bulk-ESS values are larger than 100, the chains are assumed to have been efficient and reliable parameter estimates ... If R-hat values are larger than 1.05, between- and within-chain estimates do not agree and thus mixing has been poor."

The rate-prior changes in the leave-one-out runs (scale 2.2 and 2.3 against 2.5) re-derive the same mean from a new tree height. They are not a test of the prior. No run moves the maximum.

## Citing papers (Europe PMC)

| Query | Hits | What I did |
|---|---|---|
| `CITES:38997462_MED AND (prior OR "maximum" OR "root age" OR "upper bound" OR sensitivity OR calibration) AND (LUCA OR "last universal common ancestor")` (papers citing Moody 2024; 195 cite it in total) | 70 | Read 50 titles (the first page); opened 5 full texts (below). 20 titles not seen. |
| `CITES:37978174_MED AND (prior OR "maximum" OR "root age" OR "upper bound" OR sensitivity)` (papers citing Mahendrarajah 2023) | 47 | Read all 47 titles; opened 2 full texts (below). |

Full texts opened (saved in `raw/prior_art/`) and searched for sentences on the maximum, the root prior, the rate prior or Moody's date:

- **Kay et al. 2026**, "Dated gene duplications elucidate the evolutionary assembly of eukaryotes" (PMC12872463). "These genes were not integrated into our analyses because, within the gene trees, the duplication node is also the root and, therefore, sensitive to the root prior used in the molecular clock analysis19." Ref. 19 is Moody 2024. They say this, but they run no test.
- **Schrago & Mello 2024**, "Challenges in Assembling the Dated Tree of Life" (PMC11523137). "One key result from recent timescales is that the age of the LUCA is approximately 4 billion years, which is close to the maximum bound set by the Moon-forming impact (Betts et al. 2018; Kumar et al. 2022; Craig et al. 2023)." A review, with no reanalysis.
- **Abramov et al. 2026**, "A Hadean timeline for the emergence of the RNA World" (PMC13597498). It uses the date: "4.2 Ga, the approximate mean of the 4.09-4.33 LUCA window31." No test.
- **Goldman, Fournier & Kaçar 2026**, "Universal paralogs provide a window into evolution before the last universal common ancestor" (PMC12985370). It describes the five-paralogue dating. I found no sentence on the maximum or the priors.
- **Moody et al. 2025**, "The emergence of metabolisms through Earth history ..." (PMC12329450). It uses the same timetree. No prior test.
- **Wang & Meade 2026**, "Molecular clock dating using complex mixture models: applied to ancient symbionts" (PMC12971015). Simulations with root ages of 1 to 4 Ga on the substitution model. It does not touch the maximum or the rate prior on LUCA data.
- **Wang et al. 2026**, "RNA-Iron complexes catalyse prebiotic oxygen generation" (PMC12996335). It only cites the date.

Title only, and possibly relevant but not opened: Davín et al. 2025, "A geological timescale for bacterial evolution and oxygen adaptation" (PMID 40179162, no PMC copy). Juckett 2026, "Can the Timing of the Origin of Life Be Inferred from Trends in the Growth of Organismal Complexity?" (PMC12843384).

## arXiv

Six queries through `export.arxiv.org/api/query`:

- `abs:"last universal common ancestor" AND abs:age`: 0 hits.
- `abs:LUCA AND abs:clock`: 2 hits, both off topic.
- `abs:"cross-bracing"`: 1 hit, off topic.
- `abs:MCMCtree AND abs:prior`: 0 hits.
- `all:"universal common ancestor"`: 8 hits, none on dating priors.
- `all:"divergence time" AND all:calibration AND all:prior`: 3 hits. These are general methods papers on calibrated tree priors (1103.5780, 1311.4921, 2512.02312) and none concerns LUCA.

Nothing relevant. arXiv is not where this field publishes.

## GitHub

The authors' repository `sabifo4/LUCA-divtimes` at commit `a2bf515fe3dddfc006b6d19e5444259857c62557` (2025-12-10) has prior runs (`sum_analyses/00_prior`, `sum_files_prior/`) under the published calibrations only. It has no folder for a moved maximum or a changed rate prior (file tree listed through the GitHub API, 8,544 entries, not truncated). I did not search GitHub more widely.

## What this changes for the design

- **The study still adds information.** No one has moved the maximum or the rate-prior mean on Moody's data.
- **The gate needs the concatenated published interval.** The plan's R0 is "concatenated data, cross-bracing A", and the `in.BV` the plan names (`00_CODEML/out_CODEML/Hessian/1/in.BV`) is the concatenated one. The partitioned analysis uses five Hessians (`01_CODEML/out_CODEML/Hessian_part/1..5`). The abstract's 4.09–4.33 Ga is partitioned. The gate must use the concatenated cross-bracing A interval, which is in Supplementary Data 6 or the repo's `sum_files_post/`. Neither is opened yet. This is a decision for the owner (see the prereg).
- **Mahendrarajah 2023 sets the expectation.** If Moody's LUCA behaves like theirs, P1 moves it upward. That is the kill outcome, so the kill is the expected result and a support would be the surprise.
