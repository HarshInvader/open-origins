# Pre-registration (T5): is Wehbi 2024's "88.6% agreement with Moody" more than a breadth effect?

Status: DRAFT, written 2026-11-24 by the T5 prep agent. This is study S1 in `docs/plans/next_studies_2026-11-24.md`. `gate` and `planted` have been run. `real` has not been run and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t5_wehbi_moody/scripts/t5_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is B, the agreement rate for breadth-matched LBCA and LACA Pfams.

- **Not computed.** B, G, or any statistic that joins a real Moody PP to a post-LUCA Pfam. No script in this study has done that join.
- **Computed on the LUCA and pre-LUCA side** (allowed, because A is the published number):
  - A under several candidate rules while I searched for Wehbi's rule (listed under "Gate");
  - A at PP > 0.75 (80.5%) and the mean share of mapped COGs over 0.5 (30.7%);
  - the shuffle floor for A.
- **Breadth counts for both sides** (map and labels only, no PP).
- **Two COG-level PP values by accident.** A `head` of `COG_LUCA_PP.csv` printed COG0001 = 0.2116 and COG0002 = 0.3403. Wehbi did not use that file (see "Gate"), and two COGs say nothing about B.
- **Permuted PP.** `planted` and `dryrun` permute the PP vector over COGs before any join, so every post-side number they print is synthetic. They do show the marginal of the PP vector. About 23% of COGs have PP > 0.5, and with that marginal and the real breadths the "any COG" rule gives about 84% for either side.
- **What this does to my expectation.** The floor for A is 87.1% and A is 88.7%. I expect a kill. That expectation comes from the allowed side and from permuted data. The thresholds below were fixed in the plan before any of it was computed, and I have not moved them.

## Claim under test

Wehbi S, Wheeler A, Morel B, Manepalli N, Minh BQ, Lauretta DS, Masel J. 2024. PNAS 121:e2410311121, doi:10.1073/pnas.2410311121 (PMC11670089, read from `experiments/t2_code_order/raw/wehbi_pmc_html/article.html`).

- Results, verbatim: "Encouragingly, 88.6% of Pfams that we annotate as pre-LUCA or LUCA are contained within genes annotated by Moody et al. (21) as present in LUCA with more than 50% confidence, when present in their dataset (Fig. 3C). This level of agreement far exceeds earlier works (22)."
- Fig. 3 caption, verbatim: "Pfams (A) and clans (B) classified as ancient are well validated by the whole gene annotations of Moody et al. (21) (C)."
- Fig. 3 caption, the method, verbatim: "98% of our pre-LUCA Pfams and 87% of our LUCA Pfams are present in genes annotated by as present in LUCA with more than 50% confidence, when present in their dataset. We mapped all Clusters of Orthologous Genes (COGs) (30) in Moody et al. (Supplementary Table 1 in ref. 21 to UniProt IDs (31) using the EggNOG 5.0 database (32). We then identified their associated Pfams using the "Pfam-A.regions.uniprot.tsv" file downloaded from the Pfam FTP site [...] on May 28th, 2024. Our protein to Pfam ID mappings are available in "Protein2Domain_mappings" in ref. 33."

**H1.** The agreement reflects age. LUCA and pre-LUCA Pfams hit a Moody PP > 0.5 gene far more often than post-LUCA Pfams that map to the same number of COGs.

**H0.** The agreement reflects breadth. A Pfam that maps to many COGs passes an "any COG" rule whatever its age, so breadth-matched post-LUCA Pfams score about the same.

The paper gives no rate for its post-LUCA Pfams.

## Inputs (exact)

Everything is under `experiments/t5_wehbi_moody/` unless noted. Downloads used User-Agent `open-research-site/1.0`. Python reads them with `-I`.

| File | Source | sha256 |
|---|---|---|
| `raw/wehbi_github_01219d8/Pfam_data_ancestralAAC.csv` | GitHub sawsanwehbi/Pfam-age-classification, commit 01219d85bfcaec82df0b80c0c24d031416e6dd96 | c8ee6d1975bed699c1b6ae4934bed66680a4eae8d3a9cb8146661be64a54a894 |
| `raw/wehbi_github_01219d8/ClassifiedPFAMs.csv` | same commit | 0f186fdc3187593177a8f516f897b7ff7790abb3d0c54fca779364288f54871d |
| `raw/wehbi_github_01219d8/MoodyPfams_probabilities.csv` | same commit | c3b19db381c659677d5ea6672f4d7f5f7e59fa295d6f0ccba5a792a3d211d609 |
| `raw/wehbi_github_01219d8/AncientAminoAcidUsageAnalysis.R` | same commit | e5d6ecd8d24bc1121f58024b5e5712d33ece15d9bbeb8a52ece4ae6ec73b8d4c |
| `raw/wehbi_github_01219d8/ClassifyingTrees.R` | same commit | 373a812d357c1281b8eafdd08b928132ad30242455a3ce7ddf99faffcc171308 |
| `raw/wehbi_github_01219d8/New_LUCAvspreLUCA.R` | same commit | 89ae28382f287c0e63efd59b3ff43a8869e242a27d80a3cda0b0592c6fa18717 |
| `raw/wehbi_github_01219d8/ASR_AAC.R` | same commit | 7bb228f1cd1b510cd3b9591061534d7f2a7fe6ffbd30ca4d35258afad93f1867 |
| `raw/wehbi_github_01219d8/ConservedSites.R` | same commit | 18c6e692ce3c00b5846bef79f4493002b4ef77d5f41c87cbbdbc3729f7b7937a |
| `raw/wehbi_github_01219d8/LUCA_Moody_pathways.csv` | same commit (not used) | 7964f2fb415734a92e45836e5a981f97e7d60ca18784a5f0988166251c7fdba0 |
| `raw/wehbi_github_01219d8/README.md` | same commit | 8128e5e6a3d272def0e7d4b413113fe04647e040199d24d20981256cdc18c2b7 |
| `raw/wehbi_figshare_27191274/cog2uniprot2pfam.csv.zip` | figshare doi:10.6084/m9.figshare.27191274.v1, file 49682610, CC BY 4.0, 74,936,808 bytes; md5 8bc29b9e… matches figshare's | 102c9a5d5e20ea039f85221839ffd793074096cb6b0b0ec587352a22902f6add |
| `raw/figshare_meta/article_27191274.json` | figshare API record for that deposit | 1c586d3632e8a95820b58e7cb9d48920fcf8c46ef62ed6347443ff245f3b361a |
| `raw/moody_springer_esm/41559_2024_2461_MOESM4_ESM.tsv` | Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1, Supplementary Data 1 (9,365 KEGG families) | 1a769b73b2945f1ff62c175a581b61ee27049b74fa8177fdcf917cd36233c3c0 |
| `raw/moody_springer_esm/41559_2024_2461_MOESM5_ESM.tsv` | same paper, Supplementary Data 2 (3,088 COGs) | 7e1f361a0b88706cb29d2eb3eb1ae19297f26eeea00e0375eb30d2eebfa7cf5a |
| `../luca_calib/raw/moody/Supp_data/Genome_Size_Number_estimates/COG_test/COG_LUCA_PP.csv` | already in the repo; same 3,088 COGs and PP values as Supplementary Data 2 | bd7388d9f553330a27448fac6ccc7ef6ed1c6d4d6c9b9e90abaf8a0bf32221ff |
| `data/cog_pfam_edges.tsv` | built by `scripts/build_map.py` from the zip | 406bd1082b78e3a87ba39678a01d4c134dc649fbeb52b5866cb0410d95481ca3 |
| `data/cog_sizes.tsv` | built by `scripts/build_map.py` from the zip | d10553b1fd58c7a5bd0c920b1cb8bf4730cbc9248dc1a01c260eaf6a84239bd7 |
| `scripts/build_map.py` | this study | 6483d807da9189990b7bfeb346d13ac8d2a00d5b0298e6f93fac9a8054fe62ac |
| `scripts/t5_analysis.py` | this study | f80a19691c19d2cdc592bd17361ed06ad763514bd8bbf46076558651a11eb53f |
| `scripts_out/t5_gate.json` | `gate` output | 77ddeb5dee9a8289a43085547d4784c12547a20a7a143985934959a42c1810ad |
| `scripts_out/t5_planted.json` | `planted` output | 59fcdd026b3fa07ed76c4072638b699950214a8df53981eca89c870b53cb5b9b |
| `scripts_out/t5_dryrun_permuted_pp.json` | `dryrun` output | f894d6573ccc51c6b123fc7f9163ecc30e8f137f25c79b92d1d0b9c3d104ba8d |

Notes on the inputs.

- `experiments/t2_code_order/raw/wehbi_github_01219d8` held only three files, so I downloaded the rest at the same commit. `main` still points at that commit.
- `build_map.py` reads the zip as a stream and never unpacks it. The map has 12,813,262 rows, 3,356 COGs, 9,562 Pfams and 73,529 COG and Pfam pairs. Free disk was 9.9 GB before the download.
- `t5_analysis.py` checks the sha256 of every file it reads and stops on a mismatch.

## Gate (`t5_analysis.py gate`; run; passed)

**Result.** A = 845/953 = 88.67% against the published 88.6%. The script reproduces the flags in `MoodyPfams_probabilities.csv` for 969 of 969 Pfams. By class it gives 98/100 pre-LUCA and 747/853 LUCA, which are the caption's 98% and 87%.

**The "contained within" rule.** The code that built `MoodyPfams_probabilities.csv` is not in the repository. The only R lines that touch it read the finished file (`AncientAminoAcidUsageAnalysis.R`, lines 37 and 43 to 44). I found the rule from the caption and from the flags.

1. A Pfam maps to every COG that shares at least one UniProt accession with it in `cog2uniprot2pfam.csv`. One protein is enough.
2. A COG stands for every KEGG family in Moody Supplementary Data 1 whose `COG` column (the family's most frequent COG) names it.
3. The Pfam's PP is the largest `constrained_median` over those families.
4. `greater_than_75` means PP > 0.75, `50_to_75` means 0.5 < PP ≤ 0.75, and `less_than_50` means the rest.
5. "Present in their dataset" means the Pfam maps to at least one COG in the map. Such a Pfam counts in the denominator even when no family behind its COGs has a PP. PF03169 is the one LUCA-side case, and Wehbi flag it `less_than_50`. 16 LUCA-side Pfams map to no COG and carry no flag.

**What the plan had wrong, and what changed.**

- The plan assumed the PP came from Moody's COG table, Supplementary Data 2, which is the repo's `COG_LUCA_PP.csv`. With that file the first gate attempt failed: A = 80.3% and 706 of 969 flags. The map's 3,356 COGs are all in the `COG` column of Supplementary Data 1, and 389 of them are missing from Supplementary Data 2. So the PP source is Supplementary Data 1, as the caption says ("Supplementary Table 1 in ref. 21").
- Other columns of Supplementary Data 1 do not reproduce the flags: `ML_median` matches 810 and gives A = 94.9%, and `MEAN_OF_MEDIANS` matches 867 and gives A = 90.7%.
- The rule "any COG" in the plan was right. The unit behind each COG is a KEGG family, and a COG can stand for several families.
- Breadth on the full map is larger than the plan's prefix count. The LUCA side maps to a median of 11 COGs (quartiles 5, 11, 27). The post side maps to a median of 4 (quartiles 2, 4, 10).

**Breadth counts on the full map** (no PP used). 953 LUCA or pre-LUCA and 2,716 LBCA or LACA Pfams map to at least one COG. 16 and 339 map to none.

| Mapped COGs | LUCA or pre-LUCA | LBCA or LACA |
|---|---|---|
| 1 | 40 | 439 |
| 2 | 52 | 393 |
| 3 | 65 | 320 |
| 4 | 53 | 230 |
| 5 to 8 | 179 | 537 |
| 9 to 16 | 202 | 368 |
| 17 or more | 362 | 429 |

The 17-or-more bin splits into 17 to 32 (176 and 250), 33 to 64 (106 and 134) and 65 or more (80 and 45). The 3,669 Pfams fall in 1,463 clans, counting a Pfam with no clan as its own clan. 200 clans hold Pfams from both sides.

**Shuffle floor for A** (LUCA side only). Permute the COG PP values among COGs within deciles of COG size, 2,000 times, and recompute A.

- Mean 87.1%, central 95% of shuffles 85.1% to 89.1%, largest 91.0%.
- The published 88.67% is at or below 7.8% of shuffles (157 of 2,001 counting the observed value).
- With an unrestricted shuffle the floor is 84.5% (82.0% to 86.9%).
- So the rule returns about 87% for these Pfams when PP carries no information about them beyond COG size.

## Fixed decisions

- **D1, classes.** Labels are the `ancestor` column of `Pfam_data_ancestralAAC.csv`, the paper's final classes (868 LUCA, 101 pre-LUCA, 2,770 LBCA, 285 LACA). The old side is LUCA plus pre-LUCA. The post side is LBCA plus LACA. `ClassifiedPFAMs.csv` is the earlier list with 12 more ancient Pfams (871, 102, 2,782, 285). The 969 flagged Pfams are exactly the old side of D1.
- **D2, mapping and PP.** The five-step rule under "Gate", unchanged for both sides. Rows whose Pfam is `NA` are dropped.
- **D3, threshold.** hit = PP > 0.5, strict.
- **D4, breadth and bins.** Breadth is the number of mapped COGs under D2, including COGs with no PP. Bins are exact for 1, 2, 3 and 4, then 5 to 8, 9 to 16, and 17 or more.
- **D5, matching.** One-to-one with replacement, taken in expectation. For each old-side Pfam, the match is a post-side Pfam drawn uniformly from the same bin. B is the mean over all such draws, which is the post-side hit rate in each bin weighted by the old side's bin counts. This removes matching noise, so matching needs no seed and has no ties to break. Without replacement is impossible, since the old side outnumbers the post side at 65 or more COGs.
- **D6, statistic.** A is the hit rate over all old-side Pfams present in the map. G = A − B, in percentage points.
- **D7, interval.** Bootstrap over clans. Resample the 1,463 clans with replacement, both sides together, 2,000 draws. The interval is the 2.5th to 97.5th percentile of G. A Pfam with no clan is its own clan. If a resample leaves a bin with old-side Pfams and no post-side Pfams, that bin drops out of B for that draw, and the output counts such draws.
- **D8, Pfams in no Moody COG.** Dropped from both sides, as Wehbi do ("when present in their dataset"). That is 16 old-side and 339 post-side Pfams. Pfams whose COGs have no PP stay in and count as misses.
- **D9, seed.** 20261125. Each mode has its own NumPy generator: `[seed, 1]` gate, `[seed, 2]` planted, `[seed, 3]` real, `[seed, 4]` dryrun.
- **D10, order of runs.** `gate`, then `planted`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with the script's current sha256.

## Decision rules (from S1, unchanged)

- **Kill.** G < 10 points and the upper bound is below 20. The agreement is then mostly breadth, and "validated by Moody" does not hold.
- **Support.** G ≥ 30 points and the lower bound is above 20.
- **Otherwise.** Report G as "partly informative".

No rule changed. The planted run gives no reason to change one (next section).

## Planted check (`t5_analysis.py planted`; run; permuted PP only)

Every replicate keeps the real map, the real labels, the real breadths and the real clans. It first permutes the PP vector over COGs, so no COG keeps its own PP. 400 replicates per row, each with the full 2,000-draw clan bootstrap. The script sha256 is f80a1969….

**PP side.** PP values go to COGs by rank of w × rank(old share) + (1 − w) × noise. A COG's old share is the fraction of its ancient Pfam partners that are LUCA or pre-LUCA. w = 0 is the plan's "random labels with the real breadth distribution". w = 1 copies PP from the labels.

**Label side.** PP is fully permuted. Then, within each exact breadth value, a fraction f of the old labels goes to Pfams that hit and the rest go at random. Each breadth value keeps its real number of old labels. f = 1 is the plan's "labels copied from Moody's PP".

| Planted | A | B | G | Mean 95% interval | P(kill) | P(partly) | P(support) |
|---|---|---|---|---|---|---|---|
| PP side, w = 0 (null) | 84.6 | 84.2 | 0.4 | −1.8 to 2.5 | 1.00 | 0.00 | 0.00 |
| PP side, w = 0.1 | 85.8 | 83.8 | 2.0 | −0.2 to 4.1 | 1.00 | 0.00 | 0.00 |
| PP side, w = 0.2 | 87.1 | 83.0 | 4.1 | 2.0 to 6.2 | 1.00 | 0.00 | 0.00 |
| PP side, w = 0.3 | 88.7 | 81.7 | 6.9 | 4.8 to 9.2 | 0.98 | 0.02 | 0.00 |
| PP side, w = 0.4 | 89.9 | 78.6 | 11.3 | 8.8 to 13.8 | 0.24 | 0.76 | 0.00 |
| PP side, w = 0.5 | 90.2 | 71.2 | 19.1 | 15.7 to 22.5 | 0.00 | 1.00 | 0.00 |
| PP side, w = 0.75 | 87.9 | 47.8 | 40.1 | 35.4 to 44.7 | 0.00 | 0.00 | 1.00 |
| PP side, w = 1 | 86.0 | 35.9 | 50.1 | 45.7 to 54.5 | 0.00 | 0.00 | 1.00 |
| Label side, f = 0 (null) | 84.6 | 84.3 | 0.3 | −1.8 to 2.4 | 1.00 | 0.00 | 0.00 |
| Label side, f = 0.1 | 85.8 | 83.9 | 1.9 | −0.2 to 4.1 | 1.00 | 0.00 | 0.00 |
| Label side, f = 0.2 | 87.1 | 83.6 | 3.4 | 1.4 to 5.6 | 1.00 | 0.00 | 0.00 |
| Label side, f = 0.3 | 88.7 | 83.3 | 5.3 | 3.2 to 7.5 | 1.00 | 0.00 | 0.00 |
| Label side, f = 0.5 | 91.5 | 82.7 | 8.7 | 6.7 to 11.0 | 0.89 | 0.12 | 0.00 |
| Label side, f = 1 | 100.0 | 81.0 | 19.0 | 16.8 to 21.6 | 0.00 | 1.00 | 0.00 |

What the table shows.

- **The null works.** With no link between PP and age, G is 0.3 to 0.4 points and every replicate is a kill. The small positive value is what is left of the breadth difference inside the bins. Splitting 17-or-more into three bins gives the same null G (0.4), so the plan's bins stand.
- **Both verdicts are reachable.** Kill has probability 1.00 at the null. Support has probability 1.00 when PP tracks the labels at w ≥ 0.75.
- **The middle is ordered.** A planted G of 7 is a kill 98% of the time, 11 is "partly" 76% of the time, 19 is always "partly", and 40 is always support.
- **Labels alone cannot reach support.** With the real spread of PP values over COGs, breadth already gives 84% to both sides. Perfect labels raise A to 100 and leave B at 81, so G tops out near 19. This is the plan's "G near 1 − B". Support needs B below about 59 with A at 88.7, and that happens only if the COGs that post-LUCA Pfams map to have much lower PP than a shuffle gives them.
- **Reading a kill.** A kill says the 88.6% does not separate old Pfams from post-LUCA Pfams of the same breadth. It does not say the Pfam ages are wrong. The planted rows at w = 0.2 and 0.3 hold a real link and still give a kill, because the "any COG" rule saturates.

**Dry run.** `t5_analysis.py dryrun` runs the full `real` code, including every reported-only extra, on PP permuted over COGs. It ran without error and gave G = −0.8 (−2.9 to 1.5), a kill, as it should.

## Reported only (no rule attached)

`real` also prints these. None can change the verdict.

- The hit rate for each side in each breadth bin, with the 17-or-more bin split in three.
- The unmatched post-side rate.
- G with the finer bins (1, 2, 3, 4, 5 to 8, 9 to 16, 17 to 32, 33 to 64, 65 or more).
- G at PP > 0.75.
- G for the mean share of a Pfam's mapped COGs with PP > 0.5, in place of the "any" rule.
- G with breadth counted as the number of Moody families that have a PP, in place of the number of COGs.
- G with the old side as LUCA only and as pre-LUCA only, and with the post side as LBCA only and as LACA only.
- G when a Pfam needs two proteins to map to a COG.
- G with Moody's COG-level PP (Supplementary Data 2) in place of Supplementary Data 1.
- The within-size-decile shuffle floor for A and for G, 2,000 shuffles, with the share of shuffles whose G is at least the observed G.

## Ways it could be fooled, and limits

1. **Breadth is matched in bins.** Inside 5 to 8, 9 to 16 and 17 or more, the old side still maps to slightly more COGs. Under the null this adds 0.4 points. The finer bins and the family-count matching are reported.
2. **COG count is not the only breadth.** A COG can stand for several KEGG families, and a big COG has more chances of a high PP. Old-side Pfams may sit in bigger COGs. The family-count matching and the size-decile floor address this in part.
3. **The map is loose.** One protein links a Pfam to a COG, so a domain found once in a large COG inherits that COG's PP. This is Wehbi's rule and the test keeps it. The two-protein version is reported.
4. **Moody's PP is not ground truth.** A real age signal that Moody's PP misses looks like a kill here. The test is about the agreement claim, not about the Pfam ages.
5. **Post-LUCA Pfams can sit in LUCA genes.** A domain added after LUCA to a gene that LUCA had will hit. Wehbi make this point themselves about accessory domains. So a high B is partly real biology, and it still means the 88.6% cannot validate the ages.
6. **The classes share inputs.** Both papers reconcile gene trees with species trees on overlapping prokaryote genomes. Agreement between them is weaker evidence than agreement between independent methods.
7. **Clans overlap the two sides.** 200 clans hold Pfams from both. The bootstrap resamples clans for both sides at once, which keeps that dependence.
8. **One threshold and one statistic decide.** PP > 0.5 with the "any" rule is the published claim. The 0.75 and mean-share versions are reported and may disagree.
9. **The rule is inferred.** Wehbi's script for the flags is not deposited. The rule here reproduces every flag, but another rule could do the same on the old side and differ on the post side. I found none.
10. **I expect a kill** (see the disclosure). The script, thresholds and decisions are fixed before the post side is read.

## Sources actually opened

- Wehbi et al. 2024, PNAS, doi:10.1073/pnas.2410311121. Main text from the saved PMC11670089 HTML. GitHub sawsanwehbi/Pfam-age-classification at commit 01219d8: README, the five R scripts (searched for Moody, COG and UniProt), `ClassifiedPFAMs.csv`, `Pfam_data_ancestralAAC.csv`, `MoodyPfams_probabilities.csv`, and the header of `LUCA_Moody_pathways.csv`.
- Wehbi 2024, figshare, doi:10.6084/m9.figshare.27191274.v1: the API record and `cog2uniprot2pfam.csv.zip`.
- Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1: the article page (supplementary captions only), Supplementary Data 1 and Supplementary Data 2.
- Prior art: I ran no new searches. The plan's searches stand as written there.
