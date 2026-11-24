# Next studies on open data, ranked (2026-11-24)

Written by a planning agent. Read-only work: nothing was committed, sealed or run.

- **What "opened" means here.** I fetched the full text from Europe PMC, or the file itself, and read the lines quoted. Anything I did not open is marked "not opened".
- **What "blind count" means.** I counted rows, sample sizes or the spread of a covariate. I did not read any outcome value. Each study below can still be sealed blind.
- **Score.** Decisiveness × cheapness × novelty, each from 1 to 5.
- **Lessons applied from T1 to T4.**
  - Each kill test has an empirical null drawn from the same data and pipeline, so a definition or an assumed input cannot produce the result.
  - Each decision range was checked for being non-empty before design. Where I could not check it, the study says so and starts with a gate.
  - No field-chemistry databases are used.

## Ranking

| Rank | Study | Score |
|---|---|---|
| 1 | S1. Is Wehbi's "88.6% agreement with Moody" more than a breadth effect? | 5 × 5 × 4 = 100 |
| 2 | S2. Does merging split KEGG families into COGs rescue LUCA families, beyond re-run noise? | 4 × 5 × 4 = 80 |
| 3 | S3. Is the growth-versus-variation trade-off in RNA networks more than droplet noise? | 4 × 5 × 4 = 80 |
| 4 | S4. Is LUCA's 4.2 Ga age set by the sequences, or by the hard maximum and the rate prior? | 4 × 3 × 4 = 48 |
| 5 | S5. Does DPANN's high loss rate survive a check against genome completeness? | 3 × 5 × 3 = 45 |
| 6 | S6. Does pairwise epistasis find tertiary contacts in five ribozymes with known structures? | 4 × 4 × 2 = 32 |
| 7 | S7. Is the ribozyme replication of Attwater 2025 exponential? (marginal; gate first) | 2 × 5 × 3 = 30 |

S2 and S3 tie. S2 goes first because it uses files already in the repo and extends the K-series.

---

## S1 (top pick). Is Wehbi's "88.6% agreement with Moody" more than a breadth effect?

**Claim.** Wehbi et al. 2024, PNAS, doi:10.1073/pnas.2410311121 (opened, PMC11670089):

> "Encouragingly, 88.6% of Pfams that we annotate as pre-LUCA or LUCA are contained within genes annotated by Moody et al. (21) as present in LUCA with more than 50% confidence, when present in their dataset (Fig. 3C). This level of agreement far exceeds earlier works (22)."

The Fig. 3 caption says the Pfams "are well validated by the whole gene annotations of Moody et al."

**Why it might fail.** A Pfam maps to many COGs. If "contained within genes annotated as LUCA" means "at least one mapped COG has PP > 0.5", a Pfam that maps to more COGs passes more easily. The paper reports no rate for its post-LUCA Pfams, so the 88.6% has no baseline. T2 used Wehbi's values, so this matters to us.

**Data (all open, no login).**
- Pfam age classes: `ClassifiedPFAMs.csv`, 172 KB, https://raw.githubusercontent.com/sawsanwehbi/Pfam-age-classification/main/ClassifiedPFAMs.csv (opened).
- Their own flags for the 969 LUCA and pre-LUCA Pfams: `MoodyPfams_probabilities.csv`, 14 KB, same repository (opened; columns `greater_than_75`, `50_to_75`, `less_than_50`). It has no rows for post-LUCA Pfams.
- COG to protein to Pfam map: `cog2uniprot2pfam.csv.zip`, 74.9 MB, https://ndownloader.figshare.com/files/49682610 (doi:10.6084/m9.figshare.27191274.v1). I fetched the first 19 MB by range request and read it: columns `cog_id, uniprot_acc, pfamA_acc`; 300 MB unpacked; about 11.5 million rows by extrapolation.
- Moody COG probabilities: Supplementary Data 2, 390 KB, 3,088 COGs, https://static-content.springer.com/esm/art%3A10.1038%2Fs41559-024-02461-1/MediaObjects/41559_2024_2461_MOESM5_ESM.tsv (opened; column names only). A copy is in the repo at `experiments/luca_calib/raw/moody/Supp_data/Genome_Size_Number_estimates/COG_test/COG_LUCA_PP.csv`.

**Decidability check (blind; no PP value was read).**
- Class sizes: 871 LUCA and 102 pre-LUCA Pfams; 2,782 LBCA and 285 LACA Pfams.
- In the 27% prefix of the map (3.12 million rows), 932 LUCA or pre-LUCA Pfams and 2,380 LBCA or LACA Pfams map to at least one Moody COG.
- The confound is real. LUCA and pre-LUCA Pfams map to a median of 4 Moody COGs (quartiles 2, 4, 10). Post-LUCA Pfams map to a median of 2 (quartiles 1, 2, 4).
- Every breadth bin has both groups, so matching is possible:

| Mapped Moody COGs | LUCA or pre-LUCA | LBCA or LACA |
|---|---|---|
| 1 | 170 | 864 |
| 2 | 122 | 505 |
| 3 to 4 | 179 | 484 |
| 5 to 8 | 196 | 293 |
| 9 to 16 | 145 | 152 |
| 17 or more | 120 | 82 |

- These counts come from a prefix sorted by UniProt accession. Recount on the full file before sealing.

**Gate.** From the full map, reproduce 88.6% within 2 points, and reproduce the flags in `MoodyPfams_probabilities.csv` for at least 95% of the 969 Pfams. If the gate fails, the "contained within" rule is not what I assumed; stop and read their R code.

**Kill rule.**
- A = share of LUCA or pre-LUCA Pfams with at least one mapped Moody COG at PP > 0.5.
- B = the same share for LBCA or LACA Pfams matched one-to-one on the number of mapped Moody COGs (exact for 1 to 4, bins above).
- G = A − B, with a 95% interval from a bootstrap over Pfam clans.
- **Kill:** G < 10 points and the upper bound is below 20. The agreement is then mostly breadth, and "validated by Moody" does not hold.

**Null that rules out a result by definition.**
- Both arms use the same rule and the same map, and they are matched on breadth. The "any COG" rule therefore cannot create a gap.
- A shuffle gives the floor: permute PP among Moody COGs within deciles of COG size, 2,000 times, and recompute A. This is the agreement the rule yields with no age signal.
- Planted checks: random Pfam labels with the real breadth distribution must give G near 0. Labels copied from Moody's PP must give G near 1 − B.

**Support rule.** G ≥ 30 points and the lower bound is above 20. Between kill and support, report G as "partly informative".

**Also report (not a decision).** The mean share of a Pfam's mapped COGs with PP > 0.5, in place of the "any" rule. And the result at PP > 0.75.

**Cost.** Laptop, under 10 minutes. Read the zip as a stream; do not unpack it (10 GB of disk is free).

**Prior art checked.**
- Europe PMC, full text, preprints included:
  - `"Wehbi" AND "amino acid recruitment" AND Moody AND (validation OR agreement OR "base rate")`: 1 hit, the paper itself.
  - `"Pfam" AND LUCA AND "Moody" AND (breadth OR "number of COGs" OR null) AND "genetic code"`: 1 hit, Nikfarjam et al. 2026 (a LUCApedia database paper, doi:10.1093/bioadv/vbaf309). Title only; it is not a test of this agreement.
  - Papers citing Wehbi 2024 (PMID 39665745) that mention Moody with validation, base rate or breadth: Moody et al. 2025 (doi:10.1098/rstb.2024.0097) and Nonacs & Nonacs 2026 (doi:10.1007/s00239-025-10294-0). Titles only; neither looks like a reanalysis.
- arXiv: the API returned HTTP 429 on every query. Not checked.
- bioRxiv: covered only through Europe PMC's preprint index.

---

## S2. Does merging split KEGG families into COGs rescue LUCA families, beyond re-run noise?

**Claim.** Moody et al. 2024, Nat Ecol Evol, doi:10.1038/s41559-024-02461-1 (opened, PMC11383801):

> "…it has the drawback that some widespread gene families that were likely present in LUCA are divided into multiple KO families that individually appear to be restricted to particular taxonomic groups and inferred to have arisen later. To account for this limitation, we also performed an analysis of COG (Clusters of Orthologous Genes) gene families, which correspond to more coarse-grained functional annotations (Supplementary Data 2)."

Methods: "COGs were assigned based on the modal COG identifier annotated for each KEGG gene family".

**The idea.** The deposit holds a natural experiment.
- Some COGs are built from exactly one KO. These are the same genes, aligned, treed and reconciled a second time. The difference between the KO's PP and the COG's PP is pipeline noise.
- Other COGs merge two or more KOs. If splitting hides LUCA families, merging should raise PP by more than that noise.

**Data.**
- Supplementary Data 1 (KO table, 3.4 MB, 9,365 rows): https://static-content.springer.com/esm/art%3A10.1038%2Fs41559-024-02461-1/MediaObjects/41559_2024_2461_MOESM4_ESM.tsv (opened; structure columns only).
- Supplementary Data 2 (COG table, 390 KB, 3,088 rows): the `MOESM5_ESM.tsv` file at the same address (opened; structure columns only).

**Decidability check (blind; the PP columns were not read).**
- 1,887 COGs in Supplementary Data 2 come from exactly one KO. All 1,887 have the same archaeal and bacterial domain proportions in both tables. 1,705 also have the same sequence count; the other 182 differ by a few sequences.
- 1,201 COGs merge two or more KOs (542 merge two, 279 three, 167 four, up to 78).
- Among single-KO COGs with at least 90% of sequences in the modal COG (1,465), the four domain-breadth cells hold 256 to 489 families each.

**Gate.** For 30 random single-KO COGs, confirm from the deposited COG sequence files that the gene set matches the KO's. The files are inside `Supp_data.zip` (3.6 GB, doi:10.6084/m9.figshare.24428659); pull single members by range request. If the sets differ, define the retest group by Jaccard ≥ 0.95.

**Kill rule.**
- Flip rate in the retest group: share of single-KO COGs where the KO has PP < 0.5 and the COG has PP ≥ 0.75.
- Rescue rate in the merge group: share of multi-KO COGs where every member KO has PP < 0.5 and the COG has PP ≥ 0.75.
- **Kill:** the rescue rate is at most twice the flip rate (the interval for the ratio includes 2). Merging then adds nothing beyond a re-run.

**Null.** The retest group is the null. It comes from the same pipeline on the same genes, so no model or assumed parameter enters. A second null: break merged COGs into random KO groups of the same sizes and domain breadth, and compare the KO-level maximum only.

**Support rule.** The rescue rate is at least five times the flip rate, and at least 5% of merged COGs are rescued.

**Reported either way.** The share of single-KO families whose LUCA call (PP ≥ 0.5) changes between the two analyses. This is the test-retest reliability of a per-family call, and it adds to our "810 families differ by more than 0.5 between runs" finding.

**Cost.** Laptop, minutes.

**Prior art checked.**
- Europe PMC: `LUCA AND Moody AND (KEGG AND COG) AND (clustering OR "orthologous group") AND (sensitivity OR robustness) AND reconciliation` returned the Moody paper and unrelated conference abstracts.
- Our own library notes for Szöllősi 2026, Csűrös 2026 and Williams 2023 say none checks per-family call stability across clusterings.
- arXiv: API returned 429. Not checked.

---

## S3. Is the growth-versus-variation trade-off in RNA networks more than droplet noise?

**Claim.** Ameta et al. 2021, Nat Commun, doi:10.1038/s41467-021-21000-1 (opened, PMC7870898):

> "Furthermore, we observed that high-yield networks tend to display small perturbation values, implying a trade-off between growth and variation (Fig. 2d, Supplementary Fig. 6e)."

Fig. 2d caption: "The number of strongly perturbable (pG→G′ > 0.8…) and high-yield networks (>0.08 µM…) is very low compared to the null hypothesis of independence between the two properties (one-sided Fisher exact test, N = 162, odds ratio <0.1, 95% confidence interval 0.01–0.66, p-value = 1.6 × 10−3)."

**Why it might fail.**
- The test uses 162 pairs and two fixed cut-offs.
- Perturbation is measured on species fractions. A low-yield droplet has few molecule counts, so its fractions are noisy, and noise alone looks like perturbation. A relative measure also shrinks when the baseline grows.

**Data.** Supplementary Data 2, 1.79 MB xlsx, https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-021-21000-1/MediaObjects/41467_2021_21000_MOESM4_ESM.xlsx (opened).
- Sheet "Networks (experimental data)": 1,837 rows; 16 node fractions, number of replicates, yield in µM.
- Sheets "Droplets (node fractions)" and "Droplets (number of UMIs)": 20,039 droplets each.
- Raw data (doi:10.6084/m9.figshare.c.5103962) and code (doi:10.5281/zenodo.4016905): not opened.

**Decidability check (blind; only which species are present and replicate counts).**
- 1,834 distinct networks, all with a yield value.
- 4,549 pairs (G, G′) where G′ is G plus one species.
- 1,115 of those have at least 5 replicates on both sides, with at least 111 pairs at each size from 2 to 6 species. The paper's test used 162.

**Gate.** Reproduce the paper's Fisher test (N = 162, odds ratio < 0.1) from the Methods definition of perturbation. I did not read that definition; read it before sealing. Also confirm that a droplet's network can be read from which cells are filled.

**Kill rule.**
- K-a: Spearman correlation between the yield of G and the perturbation G→G′ over all pairs with at least 5 replicates, bootstrapped by network.
- K-b: the same after adjusting for a noise perturbation: for each G, the perturbation between two random halves of its own replicate droplets, with no species added.
- **Kill:** the K-b interval includes 0, or the yield-to-noise correlation is as strong as the yield-to-perturbation correlation.

**Null.** The split-half noise perturbation is measured from the same droplets. Nothing about the chemistry is assumed. Planted check: simulate droplets with compositions independent of yield and the real UMI counts; the pipeline must return no trade-off after adjustment.

**Support rule.** After adjustment, the correlation is −0.2 or stronger and the interval excludes −0.05. It must also hold when perturbation is computed on absolute concentrations (fraction × yield).

**Cost.** Laptop, minutes.

**Prior art checked.**
- Europe PMC: `"Azoarcus" AND autocatalytic AND network AND ("trade-off" OR tradeoff) AND (null OR compositional OR reanalysis)`: 4 hits (Lambert 2025, Ameta 2021 review, the paper, Szathmáry 2006). None is a reanalysis by title.
- Papers citing it (PMID 33558542) with reanalysis, null, artefact or compositional: 10 hits; the six I saw listed are follow-ups and reviews (e.g. Ameta 2023, Jirasek 2026), not reanalyses. Titles only.
- arXiv: 429. Not checked.

---

## S4. Is LUCA's 4.2 Ga age set by the sequences, or by the hard maximum and the rate prior?

**Claim.** Moody et al. 2024, doi:10.1038/s41559-024-02461-1 (opened):

> "Here we infer that LUCA lived ~4.2 Ga (4.09–4.33 Ga) through divergence time analysis of pre-LUCA gene duplicates, calibrated using microbial fossils and isotope records under a new cross-bracing implementation."

**Why it might fail (inputs I read, not outcomes).**
- The LUCA node has hard bounds. `Calibnodes.csv` in the authors' repository gives `LUCA; B{3.3470,4.5200,1e-300,1e-300}` and `ROOT; U(4.520,1e-300)`.
- The rate prior was built from the root age. Methods: the mean rate was "calculated by dividing the tree height of our best-scoring ML tree … into the estimated mean root age of our phylogeny (that is, 4.520 Ga…)".
- The paper says of its prior check: "we are not attempting to test the hypothesis that the fossil record is an accurate temporal archive".

**Data.** https://github.com/sabifo4/LUCA-divtimes (GPL-3.0; file tree listed through the GitHub API).
- `01_PAML/00_CODEML/out_CODEML/Hessian/1/in.BV`, 2.65 MB (branch lengths, gradient, Hessian).
- `00_data_formatting/01_inp_data/LUCAdup_246sp_allcb_calib_MCMCtree.tree`, 8 KB.
- `01_PAML/02_MCMCtree/dummy_ctl_files/mcmctree_dummy.ctl` (opened: burn-in 100,000; sample every 1,000; 20,000 samples; rate prior Γ(2, 2.5)).
- `01_PAML/02_MCMCtree/calib_files/Calibnodes.csv` (opened).
- Software: PAML 4.10.7 MCMCtree, which the paper used. Not installed on the laptop; it builds from source.

**Decidability check (blind).**
- All inputs exist and are small. I opened no posterior or prior summary file.
- Either outcome can happen: the posterior median under each change lands inside or outside the stated regions.
- Moody's own sensitivity runs were per gene, leave-one-gene-out, a richer substitution model, and with or without cross-bracing. None moved the maximum or the rate prior.

**Runs (both clock models, concatenated data, cross-bracing A).**
- R0: the published settings. Gate: the LUCA 95% interval matches the published one within 0.05 Ga at both ends.
- P1: raise the LUCA and root maximum from 4.52 to 6.0 Ga. This is unphysical on purpose; it asks what the sequences say.
- P2: halve and double the rate prior mean, with the bounds unchanged.
- Each run has a twin without sequence data (`usedata = 0`).

**Kill rule.** The claim fails as a data-driven date if either holds under both clock models:
- under P1 the posterior median is above 4.52 Ga;
- under P2 the posterior median leaves 4.09–4.33 Ga in the direction of the rate change.

**Null.** For each run, the twin without data gives the prior on the LUCA node from the same sampler and calibrations. Any gap between the pair comes from the sequences. Report information gain as 1 − (posterior width / prior width).

**Support rule.** Under P1 the median stays at or below 4.52 Ga and the interval overlaps 4.09–4.33; under P2 both medians stay inside 4.09–4.33.

**Cost.** Unknown until timed. Run 1% of a chain first. If a chain takes more than 8 hours on the laptop, use one AWS spot machine; the budget cap is $1.

**Prior art checked.**
- Europe PMC:
  - `LUCA AND "4.2 Ga" AND (prior OR calibration OR "maximum bound") AND (sensitivity OR critique OR reanalysis)`: 5 hits (Abramov 2026, Moody 2024, Moody 2022, Zellner 2017, a 2016 primer). None reanalyses the date, by title.
  - `"cross-bracing" AND LUCA AND (prior OR "maximum age") AND sensitivity`: Moody 2024 and Kay et al. 2026 (eukaryote duplications).
  - Papers that cite Moody 2024 with clock and prior terms: 7 hits (e.g. Endres 2026, Klos 2026). They use the date; none tests it, by title.
- Mahendrarajah et al. 2023 (doi:10.1038/s41467-023-42924-w) dated a similar tree. I opened only its data statement, so I cannot say what it reports about the maximum bound. Read it before sealing.
- arXiv: 429. Not checked.

---

## S5. Does DPANN's high loss rate survive a check against genome completeness?

**Claim.** Huang et al. 2026, Nat Commun, doi:10.1038/s41467-026-76386-7 (opened, PMC13473441):

> "Adding a DPANN-specific loss rate substantially improved reconciliation model fit (BIC: 3284636.6, Supplementary Data 10), and, as predicted, the DPANN loss rate was inferred to be higher than that for the other clades (DPANN: 0.40-0.45, other clades: 0.26-0.27)."

**What the authors already did.** "To account for the incomplete nature of some MAGs, genome completeness estimates from CheckM v2 were used in reconciliation". So this study asks whether that correction was enough. It is a residual-confounding check, which is why it ranks fifth.

**Data.**
- Supplementary Data 1–33, 6.2 MB xlsx, https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-026-76386-7/MediaObjects/41467_2026_76386_MOESM3_ESM.xlsx (opened; Supplementary Data 1 has CheckM 1 and CheckM 2 completeness for each genome).
- Zenodo doi:10.5281/zenodo.18701544, `4_Ancestral_reconstruction.zip`, 438 MB. Already in the repo at `experiments/luca_calib/raw/huang/`. `perspecies_eventcount_transfer_corrected.txt` has 513 branches with speciations, duplications, losses, transfers and copies (header read only).

**Decidability check (blind; completeness only, no loss count read).**
- Focal set: 257 archaea. By GTDB phylum name I count 72 DPANN and 185 others. This labelling is rough; use the paper's clade labels.
- CheckM 2 completeness: DPANN median 91.1 (32 of 72 below 90); others median 98.3 (30 of 185 below 90, 12 below 80).
- CheckM 1: DPANN median 82.0; others 98.1.
- So the two groups differ in completeness, and the non-DPANN group has about 30 low-completeness genomes for a within-group test.

**Kill rule.**
- Arm A (negative control): among non-DPANN tips only, does the loss fraction on the tip branch rise with (100 − completeness)? If the correction worked, the slope is 0.
- Arm B: DPANN versus other clades on internal branches only, per unit branch length. A gap in one genome cannot create a loss on a branch with two or more descendants unless all of them miss the gene.
- **Kill:** arm A shows a positive slope (interval excludes 0) and the arm B ratio is below 1.15 with an interval that includes 1. The DPANN excess is then confined to tips and tracks incompleteness.

**Null.** An incompleteness-only model predicts a spurious tip loss fraction of (1 − c) for completeness c, and a spurious internal loss of the product of (1 − c) over descendants, which is near 0. Compare observed values with these. Also shuffle clade labels in blocks of matched depth.

**Support rule.** Arm B ratio ≥ 1.3 with a clade-block bootstrap interval that excludes 1.15, and arm A slope not different from 0.

**Cost.** Laptop, minutes. The data are local.

**Prior art checked.**
- Europe PMC:
  - `DPANN AND "gene loss" AND (completeness OR incomplete) AND reconciliation AND (artefact OR artifact OR bias)`: 13 hits; the six listed were Huang 2026 and its preprint, Rao 2026, Csűrös 2026, Zhang 2025, Huang 2025. None tests this by title.
  - `"genome completeness" AND (reconciliation OR "ancestral reconstruction") AND "gene loss" AND (MAG OR "metagenome-assembled") AND bias`: 8 hits. Csűrös 2026 (doi:10.1073/pnas.2537812123) builds a sampling-bias correction for gene-count models; that is method-level prior art and should be read first.
- arXiv: 429. Not checked.

---

## S6. Does pairwise epistasis find tertiary contacts in five ribozymes with known structures?

**Claim.** Roberts et al. 2023, eLife, doi:10.7554/elife.80360 (opened, PMC9901934):

> "The results demonstrate that the data sets provide structural information similar to chemical or enzymatic probing experiments, but with additional quantitative functional information."

The paper shows this with heat maps and gives no score against a null. It also reports that the hammerhead loop-loop contact shows no positive epistasis.

**Why we care.** Our QT45 epistasis study (#30) was negative and had no positive control (IDEAS.md, idea 4). This dataset is that control: every single and double mutant of ribozymes with solved structures.

**Data.** https://gitlab.com/bsu/biocompute-public/mut_12 (public; file tree listed through the GitLab API).
- `Data/Counts_JB/*_Mut12_seqData_JB.p` for CPEB3, HDV, hammerhead, hairpin, hatchet and twister: 1.3 to 6.0 MB each (sizes read from headers).
- `Data/Structures/ribo_structures.p`, 825 bytes.
- The files are Python pickles. Do not load them with plain `pickle.load`; use a restricted unpickler.
- Structures: the paper names PDB 1M5K for the hairpin. The other structures are in papers it cites, which I did not open.

**Decidability check (partial).**
- The abstract states coverage of "every possible single and double mutant of five self-cleaving ribozymes".
- Not checked: how many non-helical contacts each structure has. Gate: count them from the PDB files before reading any activity value. Need at least 15 per ribozyme (heavy atoms within 4 Å, sequence separation of 4 or more, not a Watson-Crick or GU pair). Drop ribozymes below that.

**Kill rule.** Score each position pair by its largest positive epistasis. Compute the AUC for tertiary contacts against non-contacts.
- **Kill:** AUC minus the matched-null AUC is below 0.05 (interval includes 0) in at least 4 of 5 ribozymes.

**Null.** Non-contact pairs matched on sequence separation and on the single-mutant effects of both positions. Positive epistasis can only show where the single mutants are harmful, so an unmatched comparison would reward any pair of important positions. Base pairs are scored separately as a planted positive: the method must find them.

**Support rule.** The difference is at least 0.15 in at least 3 of 5 ribozymes.

**Cost.** Laptop, under an hour.

**Prior art checked.** Europe PMC, `ribozyme AND epistasis AND ("tertiary contact" OR "tertiary contacts") AND ("double mutant" OR pairwise) AND (prediction OR inference OR recover)`: 5 hits.
- Zhang et al. 2020 (doi:10.1093/nar/gkz1192) infer base pairing from deep mutational scans.
- Andreasson et al. 2020 (doi:10.1038/s41467-020-15540-1) use rescue analysis on glmS.
- Rollins et al. 2019 (doi:10.1038/s41588-019-0432-9), Soo et al. 2021 and Weinreb et al. 2016 cover contact inference more broadly.
- So the method is established. What is new is small: tertiary contacts only, a matched null, these five ribozymes, and its use as our control. Titles and abstracts only.

---

## S7. Is the ribozyme replication of Attwater 2025 exponential? (marginal; gate first)

**Claim.** Attwater et al. 2025, Nat Chem, doi:10.1038/s41557-025-01830-y (opened, PMC12226338):

> "When combined with coupled pH and freeze–thaw cycles, this enabled exponential replication of both (+) and (−) strands of double-stranded RNAs, including a fragment of the ribozyme itself."

Fig. 3 caption: "Dotted lines are exponential curves fitted up to four cycles (x): FITC strand = e^0.38x, R² = 0.997; Cy5 strand = e^0.20x, R² = 0.984."

**Data.** Source Data Fig. 3, 17.9 MB zip, https://static-content.springer.com/esm/art%3A10.1038%2Fs41557-025-01830-y/MediaObjects/41557_2025_1830_MOESM4_ESM.zip (opened; numbers masked).
- `SD_Fig3e.xlsx`: 9 cycle points, 3 datasets, 2 strands.
- `SD_Fig3c.xlsx`: 8 cycle points, one series, 3 bands.
- Sequencing data are on OSF through a view-only link. Not opened.

**Decidability check: marginal.**
- The published fit uses only the first four cycles, with three replicates.
- This is the T2 trap (n = 9). Gate: using only the replicate scatter, simulate exponential, parabolic and linear growth over those cycles. Seal only if the test separates them at 80% power.
- The serial-dilution series in Fig. 3c cannot decide the question. Keeping pace with dilution is exponential by construction.

**Kill rule.** Exponential growth is not preferred over parabolic or linear growth (ΔAICc below 2) for both strands, on replicate-level fits over cycles 0 to 4.

**Null.** Simulated series from each growth law with the observed replicate scatter. The scatter is a property of the measurement, not of the outcome.

**Support rule.** Exponential is preferred by ΔAICc of 6 or more over both alternatives, for both strands.

**Cost.** Laptop, minutes.

**Prior art checked.** Europe PMC, `"polymerase ribozyme" AND exponential AND (parabolic OR "sub-exponential" OR "product inhibition") AND replication AND 2025`: 2 hits, the paper and Han et al. 2026 (a GTP synthase ribozyme). No reanalysis found. arXiv: 429, not checked.

---

## Looked at and not proposed

- **Meteorite and sample-return tables.** I found no claim with enough rows that I could verify as downloadable. Isovaline excess against aqueous alteration needs tables from several paywalled papers, and the samples number 10 to 20.
- **Nonenzymatic copying (Duzdevich et al. 2020, doi:10.1093/nar/gkaa400; opened).** The data sit behind a view-only OSF link, and the paper is a methods paper with no sharp claim to test.
- **McRae et al. 2024 (doi:10.1073/pnas.2313332121; opened).** The fitness landscape is only in the supplement: "All other data are included in the manuscript and/or supporting information."
- **Coleman et al. 2021 (doi:10.1126/science.abe0511).** Not open access on Europe PMC; not opened.
- **Wehbi's pre-LUCA aromatic enrichment.** 136 pre-LUCA and 309 LUCA clans are in `Clan_data_ancestralAAC.csv` (opened; class counts only). The right null is post-LUCA families that had also duplicated before their ancestor, and I could not confirm that label is deposited.
- **Root-weight dependence in other datasets.** The count follows from the reweighting identity, so the result would come from a definition.
- **Caimi et al. 2025 (doi:10.1021/acscentsci.5c00488).** Opened for links only; the length distributions are in a supplement PDF.

## Housekeeping

- Two downloads broke the 20 MB limit by mistake: Attwater source-data zips of 34 MB and 22 MB, deleted at once and unused.
- Everything under `/tmp/oo_plan/` is deleted at the end of this run. The addresses above are enough to fetch it again.
- User-Agent was `open-research-site/1.0` on every request. No paywall or bot block was worked around.
