# LUCA reconstruction calibration: literature check and novelty search

Date: 2026-11-19. Sources were opened through Crossref, PMC (efetch full-text XML), bioRxiv full-text pages, GitHub and publisher PDFs. Europe PMC search was intermittently returning 503 errors, so some searches were rerun through web search. "(unverified)" marks anything not opened.

## Verdict

**Partly tested, but the specific test is still open.** No paper we found simulates genomes at LUCA depth (with extinct or unsampled donors), infers gene trees from simulated sequences, runs ALE or AleRax with Moody's root-origination, PP 0.5/0.75 and LOESS-size pipeline, and measures bias in root content or in the 2,657-protein estimate. Moody et al. ran no such simulation. The closest work points in conflicting directions on the sign of the bias:
- The Szöllősi/Williams group argues reconciliation *underestimates* deep ancestors. This is argued conceptually, and in a 2026 denoiser preprint the error is injected, not simulated phylogenetically.
- Csűrös 2026 (PNAS) argues ALE at the 700-genome scale produces spurious transfers and a tiny LUCA ("only 45 genes"). Its simulations test only the profile-based GLD model, not ALE.

That disagreement is the strongest motivation for this study, and also its main competitive risk.

**Update 2026-11-20 (prior-art review; prereg v5).** The claim that this "simulates genomes at LUCA depth" needs narrowing, because Coleman et al. 2021 already ran Zombi simulations with ALE for root position and DTL counts (see their entry below). What is new is narrower: the first known-truth test of whether Moody's root-weighted posterior probabilities, summed or thresholded, recover a planted root gene set when gene trees come from saturated sequences with ghost donors. At 80-320 tips this cannot settle the Csűrös-Szöllősi dispute. A "corrected LUCA size" is not a headline.

## What exists

### Verified prior-work references

| Ref | DOI / venue / year (opened) | What it tested in simulation |
|---|---|---|
| Szöllősi et al., "Lateral gene transfer from the dead" | 10.1093/sysbio/syt003, Syst Biol 62:386-397, 2013 (PMC3622898) | Theory and model for transfers through extinct and unsampled lineages, applied to 473 families from 36 cyanobacteria. **No simulation.** The text says: "Such simulations are, however, outside the scope of the current publication." No test of ancestral content. |
| Szöllősi et al., "Efficient exploration of the space of reconciled gene trees" (ALE) | 10.1093/sysbio/syt054, Syst Biol 62:901-912, 2013 (PMC3797637) | Parametric simulation on 36 cyanobacteria (root about 2.7-3.5 Ga): sequences simulated with LG+G+I along reconstructed reconciled trees, then inferred with a Poisson model. It measured gene-tree accuracy (RF) and DTL event counts. Ancestral copy number was compared for 342 universal single-copy families on **real** data (joint trees give about 1 copy at the root), not as a simulation truth test. There were no extinct or unsampled donors in the simulation, and it is not at LUCA depth. |
| Davín et al., Zombi | 10.1093/bioinformatics/btz710, Bioinformatics 36:1286, 2020 (online 2019; PMC7031779) | A simulator paper. It validates the simulator itself, not inference. It simulates the complete tree including extinct lineages (T mode), genomes (G mode, plus Gu/Gm/Gf variants with branch- or family-specific rates) and sequences (S mode, via pyvolve). The output includes the full event log and RecPhyloXML reconciliations. |
| Morel et al., AleRax | 10.1093/bioinformatics/btae162, Bioinformatics 40(4), 2024 (PMC10990685) | Benchmarks reuse the SpeciesRax simulations: for example 25 species and 100 families with varying site counts, with the "true species tree ... assumed to be known." Metrics are gene-tree RF and species-tree accuracy. AleRax matches ALE in accuracy and is about 10x faster. ALE failed on 25 of 12,408 HOGENOM families through underflow. **No test of ancestral content or genome size**, and the depth is shallow. |
| Moody et al. | 10.1038/s41559-024-02461-1, Nat Ecol Evol 8:1654-1666, 2024 (PMC11383801) | **No simulation of root-content recovery.** The robustness checks were empirical only (see the pipeline section below). The only "simulation" was Bernoulli sampling of KEGG genomes from PPs to propagate uncertainty into the size estimate. |

**Zombi install.** The repository is https://github.com/AADavin/ZOMBI (redirects to AADavin/Zombi; version 1.0.1; last push 2025-04-03; not archived). Install steps:
```
git clone https://github.com/AADavin/ZOMBI
pip3 install ete3 numpy networkx pyvolve   # README targets python 3.6
python3 Zombi.py T ./Parameters/SpeciesTreeParameters.tsv ./out   # then G, then S
```
Zombi includes a `SpeciesSampler.py` for taxon subsampling.

**AleRax install.** The repository is https://github.com/BenoitMorel/AleRax (pushed 2026-11-11). Install with `git clone --recursive ... && ./install.sh` (needs CMake 3.6 or later).

### Novelty-search findings (DOIs opened)

- **Szöllősi, Spang, Boussau & Williams, "Improved ancestral genome reconstruction using a learned gene-content grammar"**, bioRxiv 2026, doi:10.64898/2026.09.03.749268. This is the closest in spirit.
  - It states that reconciliation (ALE, GeneRax, AleRax) has false-negative rates of 0.5-0.9 at deep nodes such as LBCA and LUCA. That figure comes from the matching GitHub README (github.com/ssolo/gene-content-grammar; seen only as a search snippet).
  - It does **no phylogenetic simulation**. It corrupts real GTDB presence/absence vectors with injected false-negative rate f_N of 0 to 0.9 and false-positive rate f_P of 0.01, then trains a denoiser.
  - It is applied to LBCA (from Davín 2025) and LACA (from AleRax). LUCA is only named as future work.
  - Moody is cited only in passing. In the text read (the first 100k characters), it does not measure what bias reconciliation itself produces.
- **Williams, Davín, Morel, ... Szöllősi, "The power and limitations of species tree-aware phylogenetics"**, bioRxiv 2023, doi:10.1101/2023.03.17.533068.
  - It argues that reconciliation "may tend to under-estimate ancestral gene repertoires" and that "the systematic underestimation of gene copies at deeper nodes ... remains a substantial challenge".
  - The argument is conceptual (adapted from Kellner et al. 2018, unverified).
  - Its Zombi simulations cover DTL-event recovery, gene-tree rooting and species-root inference, **not** ancestral content.
- **Csűrös, "Reconstructing ancient genomes from gene counts: A robust likelihood framework with sampling bias correction"**, PNAS 123(19):e2537812123, 2026, doi:10.1073/pnas.2537812123 (PMC13167736).
  - It simulates gain-loss-duplication birth-death processes (no HGT gene trees, no sequences) to show that GLD recovers ancestral content (median TPR 98.6%). It notes that "the root genome represents the most difficult challenge".
  - It **critiques ALE at scale**. It says the 700-genome study (ref. 21 = Moody 2024) shows transfers correlated with family size (R² = 0.83), "resulting in a ... (LUCA) with only 45 genes (SI Appendix, Fig. S41)". It makes the same point about the 1,007-genome study (Davín 2025), saying "The LBCA root is reduced to 5 genes".
  - Its argument is that gene trees are underdetermined by sequence length, which is an empirical argument, not a simulation of ALE.
  - The "45" presumably counts confident families rather than summing PPs. We did not open the SI.
- **Szöllősi & Williams, "Ancestral gene content estimates under gain-loss-duplication depend on the chosen observation threshold"**, PNAS 123(31):e2618431123, 2026 (PMC13438450). This is a letter. It shows that GLD root size depends on Ω_min and calls the profile-method bias "opposite to the conservatism of reconciliation methods". There is no ALE simulation.
- **Gagnon & Csűrös, reply**, PNAS 2026, doi:10.1073/pnas.2619901123 (PMC13438522). It restates that "large-scale reconciliations ... hallucinate lateral gene transfers because of weak phylogenetic signal" and cites Moody. There is no ALE simulation.
- **Coleman et al. 2021, "A rooted phylogeny resolves early bacterial evolution"**, Science 372:eabe0511, doi:10.1126/science.abe0511.
  - **Correction (2026-11-20).** The 2026-11-19 entry said "no new simulations". That was wrong: it read only the bioRxiv v1 preprint, which has no Zombi section. The published version (main text: https://ssolo.web.elte.hu/Coleman_2021.pdf) did simulate:
    - "we simulated gene family evolution using Zombi (78) combined with rejection sampling to obtain sets of simulated gene families similar to the real data in terms of inferred DTL events";
    - root inference was robust to taxon sampling and to the share of extinct lineages (fig. S2);
    - D, T and L counts were accurately recovered (figs. S3-S8).
  - **Their figshare deposit** (doi:10.6084/m9.figshare.12651074, opened 2026-11-20):
    - `ExperimentExtinctions`: about 1,000 Zombi runs (30-tip trees with extinction, 100 families each), reconciled with default ALEml_undated on **true** pruned gene trees;
    - `TableSimulations.tsv`: simulated against inferred D/T/L/S per family.
    - Neither the deposit index nor the main text scores root gene content or root origination probabilities against the truth.
  - **SI not opened:** science.org and the Bristol portal returned 403 to an automated client. Whether the SI scores root content is **unverified**.
  - It introduced the root-weight reweighting (`O_R_Optimization.py`, per COG category) that Moody reuses.
  - It estimated LBCA at 1,292.6-2,142.9 COG members and 1.6-2.69 Mb by regression on modern genomes (r = 0.96).
  - **Consequence for novelty:** replicating DTL recovery or root robustness adds nothing new; they are replication checks at most (prereg v5). What remains new is narrower: a known-truth test of the root-weighted, summed or thresholded root probabilities, on inferred gene trees with ghost donors.
- **Williams et al. 2017, "Integrative modeling of gene and genome evolution roots the archaeal tree of life"**, PNAS 114:E4602, doi:10.1073/pnas.1618463114 (PMC5468678).
  - Its simulations (in the SI, unread) cover **root position** only.
  - Its ancestral genome size (archaeal root about 1,090) was corrected using extinction probabilities ("41% ... have since gone extinct").
  - For ancestral content accuracy it relies on the earlier ALE simulations: "Previous simulation studies (67) ... have suggested that ancestral gene content inferences under this model are realistic". Ref. 67 is the 2013 ALE paper above, which was shallow, had no ghost donors, and checked content only on real data.
- **Mahendrarajah et al. 2023, "ATP synthase evolution on a cross-braced dated tree of life"**, Nat Commun, doi:10.1038/s41467-023-42924-w (PMC10656485). It reconciles ATP synthase subunits with ALEml_undated and tests the root by AU on reconciliation likelihoods. There is no simulation.
- **Dombrowski et al. 2020, "Undinarchaeota illuminate DPANN phylogeny and the impact of gene transfer on archaeal evolution"**, Nat Commun, doi:10.1038/s41467-020-17408-w (PMC7414124). We found no simulation of ancestral content in the full text.
- **Crapitto et al. 2022, "A consensus view of the proteome of the last universal common ancestor"**, Ecol Evol 12:e8930, doi:10.1002/ece3.8930 (PMC9165204). The task brief's citation was wrong: this is Ecol Evol, not BMC Genomics. The paper is a meta-comparison of existing LUCA reconstructions and contains no simulation.
- **Davín et al. 2025, "A geological timescale for bacterial evolution and oxygen adaptation"**, Science 388:eadp1853, doi:10.1126/science.adp1853. We opened the UvA PDF (main text). It uses 1,007 genomes and 4,713 families. The main text mentions no Zombi simulation of ancestral content. We did not check the SI.
- **Tricou et al. on ghost lineages.** We saw the records but did not do a deep read:
  - PLoS Biol 2022, doi:10.1371/journal.pbio.3001776;
  - Syst Biol 2022, doi:10.1093/sysbio/syac011;
  - MBE 2025, doi:10.1093/molbev/msaf128 ("HGTs are not SPRs");
  - GBE 2025, doi:10.1093/gbe/evaf190;
  - "Gene flow can reveal ghost lineages", bioRxiv doi:10.1101/2024.12.11.627931.

  These use Zombi to study how ghost donors bias transfer or introgression detection and timing. None addresses root gene content or genome size.
- **Commentary on Moody.** Becerra et al., J Mol Evol 2024, doi:10.1007/s00239-024-10193-w (PMC11458664), flags the gap between 399 confident KOs and 2,451-2,855 proteins. "The Unfinished Reconstructed Nature of LUCA", J Mol Evol 2024, doi:10.1007/s00239-024-10187-8 (PMC11458799), discusses false positives from inter-domain HGT. Neither has simulations. **We found no Matters Arising or formal reply** to Moody in Nat Ecol Evol through web search and Europe PMC.
- **Kundu.** We found no Kundu paper on ancestral content. The only hit was Kundu & Bansal, "On the impact of uncertain gene tree rooting on DTL reconciliation", BMC Bioinformatics 2018, doi:10.1186/s12859-018-2269-0. We opened the Crossref title only; it concerns DTL events (unverified beyond the title).

## The exact gap

Nobody has measured **bias in (a) PP-thresholded root content (PP ≥ 0.5 and ≥ 0.75, with or without the 1%-both-domains sampling rule) and (b) PP-integrated, regression-mapped genome size** with all of the following:
1. truth known from a simulator with complete (extinct and unsampled) trees and transfers from ghost lineages at about 4 Gyr;
2. Moody-like sparse sampling of extant tips (about 700 tips, two domains);
3. gene trees **inferred** from saturated simulated sequences, as bootstrap or CCP distributions;
4. ALE or AleRax with per-category root origination and five-run medians;
5. the same KO-count to protein LOESS step.

The open sign question (Williams/Szöllősi say underestimation; Csűrös says spurious HGT and a tiny root) is what the experiment would settle for this exact pipeline. A second, distinct quantity is how the PP *sum* behaves compared with the *thresholded* count. Moody's 2,657 comes from the sum (about 1,298 expected KOs), not from the 399 thresholded KOs. Diffuse low PPs over thousands of families could inflate the sum even if thresholded content is conservative. Nobody has tested this.

## Moody pipeline facts (PMC11383801 full text)

- **Genomes.** "we first inferred an updated microbial phylogeny from 57 phylogenetic marker genes ... on 700 genomes, comprising 350 Archaea and 350 Bacteria". Note: the task brief said about 350; the actual count is **700**.
- **Families.**
  - "gene family clustering was performed using EGGNOGMAPPER v.2 ... DIAMOND search, a query cover of 50% and an e-value threshold of 0.0000001. Gene families were collated using their KEGG identifier, resulting in 9,365 gene families."
  - There was also a COG-based clustering, using the modal COG per KO, with one set of gene trees.
- **Gene trees.** "aligned using MAFFT v.7.5 ... trimmed using BMGE ... Five independent sets of ML trees were then inferred using IQ-TREE 2, using LG + F + G, with 1,000 ultrafast bootstrap replicates."
- **ALE settings.**
  - "converted into ALE files, using ALEobserve, and reconciled against topology 1 and topology 2 using ALEml_undated with the fraction missing for each genome included (where available)."
  - "Gene family root origination rates were optimized for each COG functional category as previously described [Coleman 2021]."
  - "We used the median probability at the root from across the five runs."
  - Topology 2 (the focal analysis) has DPANN sister to other Archaea and CPR sister to Chloroflexi (Extended Data Fig. 4). The root is between Archaea and Bacteria.
- **Cut-offs.** Both 0.75 and 0.5 are confirmed: "The most-stringent category was that with sampling above 1% in both domains and a PP ≥ 0.75, another category was with PP ≥ 0.75 with no sampling requirement, another with PP ≥ 0.5 with the sampling requirement; the least stringent was PP ≥ 0.5 with no sampling requirement." The result was "a conservative subset of 399 KOs ... with PPs ≥0.75, and found in both Archaea and Bacteria".
- **Genome size.** About 2,600 is confirmed: "2.75 Mb (2.49-2.99 Mb) encoding 2,657 (2,451-2,855) proteins".
  - Method: "We simulated 100 samples of 'KEGG genomes' based on the probabilities of each of the (7,467) gene families being present in LUCA using the random.rand function in numpy. The mean number of KEGG gene families was 1,298.25, the 95% HPD minimum was 1,255 and the maximum was 1,340."
  - "we used LOESS ... regression to estimate the relationship between the number of KOs and (1) the number of protein-coding genes and (2) the genome size for the 700 prokaryotic genomes used in the LUCA reconstruction."
  - "we used the presence of probability for each of these KEGG KO gene families rather than the estimated copy number." The prediction used R `predict` with 95% CIs.
  - The size therefore uses **all PPs** (Bernoulli draws), **not** the thresholds.
  - The 9,365 clustered families vs the 7,467 used for size is unexplained in the text, probably families that passed reconciliation (unverified).
- **Their robustness checks (empirical, no simulation).** "We tested for the effects of model complexity on reconciliation by using posterior mean site frequency LG + C20 + F + G across three independent runs in comparison with 3 LG + F + G independent runs. We also performed a 10% subsampling of the species trees and gene family alignments across two independent runs ... one with and one without ... Asgard archaea. We also tested the likelihood of the gene families under a bacterial root". They also ran a COG-level reanalysis and AU topology tests. **They did not validate root-content recovery by simulation.**
- **Data.** Reconciliation data and scripts are on figshare, doi:10.6084/m9.figshare.24428659 (not opened). This is useful for copying exact configs and per-category origination rates.

## Risks to novelty

1. **The Szöllősi/Williams/Boussau/Spang/Davín group is closest and active.** In 2026 they have the denoiser preprint and the PNAS exchange with Csűrös, they wrote Zombi and AleRax, and they are Moody co-authors. A Zombi-to-AleRax LUCA calibration is an obvious next step for them, and their SI or unpublished work may already contain one. Check the 2023 "power and limitations" final published version (unverified whether it has been published), the denoiser SI, and the Davín 2025 SI.
2. **Csűrös 2026 SI (Fig. S41)** reanalyses Moody's reconciliations. It is empirical, not simulated, but it pre-empts the "Moody is biased" framing. Our contribution must be the simulation-calibrated magnitude and sign, not the critique.
3. **SI and figshare material we did not read** for Moody, Coleman 2021, Williams 2017 and Davín 2025 could contain small simulation checks. Williams 2017's SI simulations concern the root position, according to the main text.
4. **Zombi as the truth model.** The result will depend on how well Zombi's genome model matches reality: its family-origination process, the lack of KO-splitting artifacts, and its transfer model. Moody notes KO splitting itself as a bias ("widespread gene families ... divided into multiple KO families"), and a pure simulation will not capture it. Reviewers will ask for this as a separate factor.
5. **Scale or compute.** About 700 tips, about 7-9k families, and five bootstrap sets is heavy. A reduced-scale study may be judged unrepresentative.

Searches run (Europe PMC, Crossref, web/bioRxiv): reconciliation together with simulation and "ancestral gene content" or "ancestral genome size"; LUCA together with ALE/AleRax and simulation; Moody critiques and Matters Arising; Crapitto; Tricou ghost; Kundu; Csűrös 2026.
