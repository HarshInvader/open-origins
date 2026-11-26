# Open Origins: research state

Decision log for the main study. Each entry gives the advice we got (Fable, per the owner's "Use Fable to plan" rule), what we decided, and why.

## Main study: LUCA calibration (task #32)

**Question.** Does Moody et al. 2024's LUCA size (Σ root PP ≈ 1,291 KEGG families, which they convert to about 2,600 proteins) survive known-truth simulation?

**Closed so far (details in `experiments/luca_calib/`):**
- **K1, real data:** 97% of the summed size depends on one fitted root weight. The sum is 1,290.6 with the fitted weight and 33.9 under a flat prior. The data support the weight strongly (ΔlogL = 1,169).
- **Of Moody's 1,290.6 (computed 2026-11-23 from their deposited PPs):**
  - 47% comes from the 684 families with PP ≥ 0.75;
  - 21% from 434 families with PP between 0.5 and 0.75;
  - 32% from 6,338 families each below 0.5, of which 15% is from 5,677 families below 0.2.
  - So about a third of the size rests on families no one would call LUCA one by one.
- **K2 (laptop):** the sealed rule said "fail" (R 0.751). That was a crash in the macOS arm64 ALE build on very large families (DEVIATIONS 11-12). Linux ALE gives R 1.087 on the same simulation.
- **K3 (AWS, Linux ALE), seed 1 at 80 genomes per domain:**
  - R* is 1.099 with true gene trees and 1.044 with inferred ones (Q 0.95).
  - n40 gives 1.03 / 1.02.
  - Seeds 2 and 3, true trees: 1.057 / 1.013. Their inferred arms are re-running after the spot machine was lost (DEVIATIONS 14).
- **K4 (v5d + v5e):** running on AWS. 160 and 320 genomes per domain with true trees, and transfer 0.8 with inferred trees.

### 2026-11-23: Fable review (K3 reading, per-call finding, K4 design, next study)

**On reading K3:**
- **Advice:**
  - Report every seed in both arms, with its range, and the paired inferred-minus-true difference.
  - Report the decomposition into false and missed probability mass.
  - Report the **prior multiplier** (fitted Σ / flat Σ): about 1.5× in our simulations against 37× in the real data.
  - Trap 1: a pass is only "unbiased under correct specification in an easy regime", not "2,600 validated". Zombi and ALE are close model cousins, and fitting one root weight is close to moment-matching the root count, so R ≈ 1 is the expected outcome.
- **Decision:** adopted. All of these items are now sealed as K4/K3 measures in v5e. The verdict wording will follow trap 1.

**On the "~15% wrong assignments" finding:**
- **Advice:** as framed, this is not a finding. A calibrated posterior must put some mass on wrong families, and "right total by cancellation" is simply what calibration means.
  - Reframe it as a calibration test: a reliability curve plus expected calibration error, for true and inferred trees.
  - Apply it to the real PPs: how much of 1,291 rests on PP < 0.5 families?
  - Prior work to check (from Fable's memory, unverified): Morel et al. GeneRax 2020 / AleRax 2024 benchmarks; Kordi & Bansal (RANGER-DTL); Davín et al. 2018; Tricou et al. 2022 (ghost lineages); Berkemer & McGlynn 2020; Menet et al. 2022; Williams et al. 2017; Szöllősi et al. 2013.
- **Decision:**
  - Adopted the reframing. The reliability curve and calibration error are sealed in v5e.
  - The real-data split is done (above: 32% below PP 0.5). That is the reportable point.
  - Still to do: check the listed papers before calling anything new. So far we have checked Moody 2024, Coleman 2021, Csűrös 2026, Szöllősi & Williams 2026 and Gagnon & Csűrös 2026; none quantifies per-family root-call error.

**On the K4 design:**
- **Advice:**
  - Add a completion clause, an "inconclusive" band within 0.05 of the thresholds, pre-stated interpretation, and the extra measures.
  - Transfer 0.8 is not a worst case, because ALE models transfer.
  - The damaging factors, in order: (1) stem origination plus early inter-domain transfer; (2) a prior-dominated regime; (3) family mis-delineation (KEGG lumping); (4) ghost donors; (5) a wrong root or species tree.
- **Decision:**
  - Sealed as v5e before any K4 score existed. w80 is relabelled a robustness check.
  - Did not stop or replace the K4 lanes: they were already running, and the money is spent.

**On what to do next:**
- **Advice:** more seeds, scales or transfer rates will not give an important result; on its own the size critique reads as a competent validation. The one study worth doing is a **two-worlds discrimination test**:
  - **Big-LUCA world:** 200 root families.
  - **Small-LUCA world:** 20 root families, plus about 180 families born on the two domain stems with elevated inter-domain transfer, tuned blind so the phyletic summaries match.
  - **Pipeline:** identical in both worlds, with the root weight fitted per world.
  - **Kill rule:** small-world R > 2 means "the pipeline hallucinates a large LUCA from stem transfer". R in 0.8-1.25, with a clearly lower fitted weight than the big world, means "it discriminates".
  - **Caveat:** stem-born, stem-transferred genes are partly a matter of definition. Report a bound per unit of stem transfer.
  - If the method passes, pivot away from this angle.
- **Decision:** adopted as the next study (K5).
  - It is feasible: `simulate.py` already supports Zombi Gu mode with per-lineage event and transfer rates (arm L), so stem-specific origination and transfer can be set without editing Zombi.
  - Run with true trees first, on the laptop under the Origins lock.
  - Plan: build and test the stem-rate writer, tune the small world to match on phyletic summaries only (no PP), seal the prereg, then run.
  - Stop rule: if K5 passes, close the LUCA-size angle and pivot.

### 2026-11-23: K5 design (Fable, two rounds)

**Round 1: how to simulate the small world.**
- **Advice:**
  - Use Zombi Gm superposition (option B): the K3 world, a few root families, plus stem-born families.
  - Reuse K3 seeds 1-3 as the big world, so the two worlds are paired.
  - Match on phyletic summaries with fixed tolerances.
  - Report absolute ΣPP, not only R.
  - Flagged threat: a transfer boost applied over the whole tree is a weaker adversary than one applied only on the stems.
- **Decision:** adopted, with one change. Stem-born families are simulated by our own per-family simulator (`k5/stemsim.py`, Zombi Gm rules), not by a second Zombi run.
  - The stems hold only 0.071 of 87.8 units of tree length. Stem-only origination in Zombi would need about 220,000 families.
  - stemsim can also apply the extra transfer on the stems only, which removes the flagged threat.
  - Removing root families from the K3 world is valid because Gm families are independent.

**Round 2: review of the prereg draft.**
- **Advice:** do not seal yet.
  - The two stems coexist only during [0.1013, 0.1073] on seed 1, so a stem-to-stem-only target almost never exists. The planned λ ladder would really have been {0, 0.03, 0.12}.
  - Add a control world (N = 0) and judge the excess over it, because background false mass alone gives R_small of about 2.
  - Pick N closest on row 2, not the smallest matching N.
  - Require tight matching before claiming "cannot discriminate".
  - Require all seeds on the same side, and require the top rung for "discriminates".
  - Pair families across λ.
  - Add a planted check for mid-tree births and an ALE positive control.
- **Decision:** all adopted.
  - The target is now any lineage in the other domain's clade.
  - Both planted checks pass.
  - Sealed as v6 (sha d8a0a7b3…, with stemsim.py dbc99e94…).

### 2026-11-23: K4 machine lost
- The origins-k4 spot machine was reclaimed about 5 minutes into simulating; nothing had been scored.
- The n160 and n320 true-tree lanes were restarted on the K3 machine (origins-k3b), which had spare cores.
- w80, which v5e relabelled a robustness check, was dropped to stay inside the budget. That is $40.30 booked of $50, against estimates; actual spend is lower. See DEVIATIONS 15.

### 2026-11-23: prior art for the calibration finding
Checked by a subagent; every source was opened. Davín 2018, Berkemer & McGlynn 2020, Menet 2022, Williams 2017, Williams 2023, Morel 2024 (AleRax), Tricou 2022, Szöllősi 2013, Moody 2024, Coleman 2021 and Gàlvez-Morante 2024 (Dollo) were checked. None measures per-family root-presence accuracy, or the calibration of root posteriors, on known-truth reconciliation simulations.
- **Closest work:** Szöllősi, Spang, Boussau and Williams 2026 (bioRxiv 10.64898/2026.09.03.749268). It reports reliability and ECE for a denoiser on artificially corrupted extant genomes, and it *assumes* deep-node reconciliation errors are mostly false negatives.
  - A search-engine summary credits it with an ECE of about 0.24 for raw reconciliation output. **This is not verified.** bioRxiv returned 429, and the full text has not been read.
  - Our K3 ECE is 0.01-0.03 on known-truth simulations, with about 9% false calls at PP ≥ 0.5.
- **Decision:** do not claim novelty until that preprint's full text is read. Adding the new papers to the library.

### 2026-11-23: K5 result and how to read it (Fable)
- **Sealed verdict (v6):** "cannot discriminate in a loosely matched world".
  - λ = 4 was read on seeds 1 and 3. Mean H is 1.13; mean R_small − R_ctrl is 9.7.
  - The positive control passes (R 1.075).
  - Full write-up: `experiments/luca_calib/K5_RESULTS.md`.
- **Advice:** the rule was applied correctly.
  - Publish it as a sealed result, not as the headline. The match is loose: s1 also misses row 6 (+72%) and s3 misses row 3 (+7%).
  - The adversary is strong, with stem transfer 115-600× background.
  - λ = 0 being unmatched favours Moody et al. and must be reported with equal weight.
  - Two free follow-ups: a topology split, and H under the flat prior.
- **Decision:** adopted. Both follow-ups were run and are labelled post hoc.
  - Flat-prior H is 0.58 and 0.80 (controls 0.11-0.13).
  - The topology split does not separate stem-born families from root families.
  - The site entry uses Fable's cautious wording.
  - Not run yet: a realism bound (stem exchange against the inter-domain transfer implied by Moody's reconciliations), and a tight match under a new prereg.

### 2026-11-23: prior-art check resolved (Szöllősi et al. 2026)
- **Sources:** bioRxiv still returns 429 on the full text, so I did not retry. The abstract was re-read through the bioRxiv API (v1 and v2), alongside our existing library entry `szollosi-2026-gene-content-grammar`, which covers the first 100k characters read on 2026-11-19.
- **What it does:** the preprint tests its denoiser on real GTDB genomes with errors injected on purpose (false negatives 0-0.9, false positives 0.01). It holds out whole phyla for testing. It does not simulate evolution and run reconciliation against a known ancestor.
- **The unverified ECE claim:** the "ECE ≈ 0.24 for raw reconciliation" figure from the earlier search summary does not appear in anything we have read. It is treated as unsupported.
- **Our contrast:** the preprint *assumes* deep-node reconciliation false-negative rates of 0.5-0.9. In K3's known-truth simulations, missed root mass is 0.07-0.13 of the true count, on both true and inferred trees.
  - Our setting is idealized (correct model, 40-80 genomes per domain), so this is a contrast in one regime, not a refutation.
- **Decision:** we may say that no known-truth calibration test of root-presence posteriors was found among the papers checked. No broader novelty claim.

### 2026-11-23: K3 after three spot reclaims (Fable)
- **Situation:** AWS reclaimed the c7a.8xlarge spot machine three times (at 9.5 h, at 3 h, and at 30 min), each time before the seed 2-3 inferred arms finished. $4.58 of booked headroom was left under the $50 cap.
- **Advice:** do not spend the last of the cap on a fourth spot attempt today. Report "verdict not reached", then finish on on-demand when the cap resets on 1 Dec. One more attempt is defensible only under a deadline, in a different pool.
  - **Wording if it fails:** "K3 verdict not reached. The sealed rule requires the mean R*_inf over seeds 1-3; only seed 1 completed (1.044). Seeds 2-3 inferred arms were lost to spot reclaims, unrelated to results. Seed 1 and n40 (1.036) are descriptive only."
  - Never put three-seed true-tree numbers beside a one-seed inferred number. Seeds 2-3 averaging above 1.353 or below 0.678 would still flip the verdict.
- **Decision:** one last attempt, on a different instance family (c6a.8xlarge, us-east-1d, 5 h, $3.55 booked; month $48.97 of $50).
  - Reason: the owner asked for a paper today and the coordinator asked for K3 to be closed tonight, which is the deadline case.
  - If this attempt is also reclaimed: stop, use Fable's wording, and finish in December.

### 2026-11-23: independent read of the preprint draft (Fable)
Owner asked for the draft `docs/paper/luca_root_weight_preprint.md` to be made ready for a possible bioRxiv post. A fresh Fable agent saw only the draft and the papers, and opened the full texts itself.
- **(a) Already published?** Partly anticipated, qualitatively.
  - Csűrös 2026 (PNAS) states that Moody et al.'s reconciliations imply "a LUCA with only 45 genes" (SI Fig. S41). The main text gives no derivation and no mechanism.
  - Szöllősi et al. 2026 (bioRxiv) note that non-ML root origination greatly reduces root families, in an archaeal-root context.
  - Not found anywhere: the exact decomposition (ΣPP 1,290.6 against 33.9 under a flat prior, a 38× multiplier), or a known-truth test of root gene-content recovery.
- **(b) Strongest objection:** the simulations are in a different regime from the real data. The flat prior recovers 46-76% of the true root there, against about 3% in Moody's data; the prior multiplier is 1.4-1.9 there, against 38. A referee would say the simulations do not test the regime the real estimate lives in.
- **(c) Overreaches found:**
  - the title;
  - the "97%" framing;
  - the post-hoc 0.91-1.10 band;
  - K3 called "calibrated" (the mid PP bins are over-confident);
  - K4 "twice the size";
  - K5 "It could not";
  - a sentence on what Csűrös's view "would have to rest" on;
  - a range given as 46-72 that should be 46-76.
- **(d) Verdict: revise.**
- **Decision:** the core result is not already published, so proceed. Every overreach was fixed:
  - new title, "an exact decomposition and pre-registered simulation tests";
  - the 95% profile interval for O_R (5.58-5.77, ΣPP 1,238-1,347) is added;
  - the pre-registered K2 failure is stated first;
  - K3 is described as within the pre-registered band, with the offsetting errors and mid-bin over-confidence stated;
  - K4 is reported as inconclusive;
  - K5 is described as loosely matched, with transfer over 100× background and the built-in identifiability limit;
  - Csűrös and Szöllősi are credited, and the novelty claim is narrowed to the exact decomposition and the known-truth tests;
  - the regime mismatch is added to the abstract and the limits.
- **Left open:** a regime-matched simulation, in which the flat prior recovers about 3% of the true root. Until that exists, K2-K4 are self-consistency checks in an easier regime and do not validate 2,600.
- **Next:** one outside expert read by email (owner's step 2). Posting stays with the owner.
- **Expert read requested (2026-11-23).** One email went to Gergely Szöllősi (OIST), using the address on an official OIST page. It asked whether the decomposition is correct, and whether there is a reason to trust the maximum-likelihood root weight that we missed. The draft is kept privately. No follow-up before 3 Dec.

### 2026-11-23: checking the Fable review against our own files
The owner asked whether Fable's review was right. Each of its numeric claims was checked against `K2`-`K5` results and `results/k3/k3_report.json`.
- **Correct:**
  - the multiplier contrast (1.4-1.9 in the simulations, from 1.38-1.89 across K2-K4, against 38.1 = 1,290.6 / 33.9);
  - the flat-prior share of the planted root (46-76%: 0.463 to 0.763);
  - that K2's pre-registered verdict failed (R 0.751);
  - K4 inconclusive;
  - K5's adversary strength;
  - the core novelty finding.
- **Two errors, fixed in the draft:**
  1. *Apples against oranges in the regime objection.* The "~3% in the real data" figure is the flat count as a share of the *fitted* count (33.9 / 1,290.6). It is not a share of the true root, which is unknown. The like-for-like simulation figure is 53-72% of the fitted count. The objection stands, but it is now stated this way.
  2. *Calibration.* Fable said PPs near 0 and 1 are well calibrated and intermediate PPs are over-confident, generalising from one bin (s1 inferred, PP 0.6-0.8, n = 18). Across the four inferred cells, the mid-bin errors go both ways: s1 and n40 are over-confident, s2 and s3 under-confident (75 root families against 88 expected, pooled). The top bin is also off in s3 (0.88 truly root against a mean PP of 0.97).
- **Also changed:**
  - a limits line said 1.5-1.9×, now 1.4-1.9×;
  - the "calibrated posterior" reading in K3_RESULTS is corrected the same way.
- **Unchanged:** the verdict "revise", and the email already sent. The email does not mention calibration or the 3% figure.

### 2026-11-23: second independent audit of the LaTeX preprint (Fable)
- **Verdict:** not publishable in a journal as is.
  - Odds as is: bioRxiv about 90% once a named human author is listed; PCI Evol Biol about 15%; a GBE/MBE short paper about 10%; NEE Matters Arising under 5%.
  - The arithmetic is right. But the framing "34 against 1,291" is a straw man, because the default prior is itself a strong prior: 1/1,399 of originations at the root. The simulations also test an easier regime.
- **Checked against our own files before acting:**
  - Confirmed: the identity ΣPP = F·ŵ/(ŵ+N−1) at the ML weight, exact in all five runs (`results/k1/k1_ci.json`). The count is F times the fitted root-origination share, about 17%.
  - Confirmed: "no failures on Linux" was wrong. K4 had 1 of 1,411 and K5 had 4 of 899.
  - Confirmed: K5 seed 2 was stopped by its planted check and was not reported. Table 4's seed-3 big world is an earlier simulation (184 families).
  - Confirmed: K2_RESULTS already noted the tree-size confound (79-639 branches against 1,399), but the paper did not.
  - Confirmed: the "three or more categories skipped" sentence applied to no family (all 7,456 were scored).
  - Partly wrong: "1,290.6 against the published 1,298.25". 1,290.6 is the sum of Moody's deposited PPs. 1,298.25 is the mean KO count of their sampled genomes, a different quantity. The wording was clarified.
  - Not verified by us: Fable's quick dose-response numbers (206 / 768 / 1,218 / 1,942 at w = 10 / 100 / 290 / 1,000) and its ~3-family flat-prior sum for translation families. Not used in the paper.
  - New prior art, opened by us: Szöllősi & Williams 2026 PNAS letter (doi:10.1073/pnas.2618431123) and the reply by Gagnon & Csűrös (doi:10.1073/pnas.2619901123). Both concern the archaeal ancestor and the observation threshold; neither discusses the root weight or Moody's LUCA. Novelty holds; both are cited as context.
- **Done:**
  - New title, the identity added as Eq. 2, and the default prior explained as non-neutral.
  - All factual fixes above.
  - Two references added; 8 of 8 resolve on Crossref.
- **Ranked additions (Fable; not yet run):**
  1. Dose-response figure of the count against w.
  2. Histogram of root odds, real against simulated.
  3. Real-data controls: does any w separate universal families (ribosomal proteins, aminoacyl-tRNA synthetases) from late, oxygen-dependent ones?
  4. Propagate to proteins by rerunning Moody's LOESS.
  5. Read Csűrös's SI (it returned 403 to the reviewer).
  6. Families dropped between the FASTA set (9,371) and the scored set (7,456).
  7. Regime-matched simulation (weeks).
  8. A realism bound for K5.
  - Not worth doing: more easy-regime seeds, the 320-genome rerun, tighter K5 matching, Count or Wagner comparisons.
- **Decision:** fix every confirmed error now. Propose additions 1-6 (about 2-3 days, laptop only) to the owner before any posting. Item 7 decides whether this becomes a result.

### 2026-11-23: real-data checks, additions 1–6 (prereg v7, sealed in 9a090d7)
- **Owner approval:** the owner approved additions 1–6 ("go ahead ... use aws if u need"). Everything ran on the laptop in under 4 minutes; no AWS was used.
- **Pre-registered verdicts:**
  - **Controls (3):** verdict (c), no window. There are 50 near-universal ribosome/tRNA-charging families and 12 photosystem families.
    - With one shared weight, the ancient set reaches a mean PP of 0.9 only at w ≥ 43,000; the young set stays ≤ 0.1 only up to w ≈ 3,200. At the fitted w, the ancient set's mean is 0.31.
    - Post hoc, with Moody's own per-category PPs: the ancient set's mean is 0.52. L22, L18 and S4 have PP 0.04, while PsaB (in no archaeon) has 0.89.
  - **Bayes factor (2):** 75% of real families have BF < 1 (median 0.18). 82% sit in [0.01, 10], against 11% and 20% of simulated root and non-root families. The weight-free count is 1,439, with a bracket of 954–1,916. It transfers poorly from the simulations, so it is reported only as a bracket.
  - **LOESS (4):** the gate passed (2,659 against 2,657). Proteins are 1,546 at w = 100, 2,638 at ŵ and 4,249 at w = 1,000.
  - **Unscored families (6):** no undercount flag. Post hoc: 18 of the 20 largest families are unscored, including 20 universal ones. That is at most +20 families, under 2%.
  - **Csűrös SI (5):** the SI is hosted only on pnas.org, which returns 403, so we stopped there.
- **Paper:** two new Results subsections, Figures 1–3, a new Methods subsection, an updated abstract and discussion, and NUMBERS.md. One error was caught before commit: a family name written from memory (ATP synthase β) was not in the dropped list. It was replaced with names fetched from KEGG.
- **Reading:** the real-data checks strengthen the paper's core claim. Per-family evidence is weak, and the weight decides most families. They do not show the total is wrong. Item 7, a regime-matched simulation, is still the deciding test.

### 2026-11-23: owner direction and the working queue
- **Owner direction:** never stop and never wait on data. The Szöllősi email is a side bet; the inbox shows no reply yet. When data or compute is missing, reason from first principles. Borrow methods from Bayesian model checking, calibration in ML and weather forecasting, and astrobiology. Recombine data we already have, and run the strongest test on the laptop. AWS has about $1 left until 1 December.
- **Queue (ranked; updated as results come in):**
  1. **Cold audit of the LUCA preprint.** A Fable agent is running; every finding will be fixed.
  2. **Calibration of the root weight in the real-data regime (item 7).** A Fable agent is designing laptop options. Run it only if it is cheap and decisive. Seal the pre-registration, then run the kill test first under the Origins lock.
  3. **Origin-of-life routes (the project's real goal).** A Fable agent is mapping the routes: RNA world, metabolism first, vents, surface ponds, lipid world, the cyanosulfidic network and others. For each it will name the riskiest claim that open data can check, then rank the tests. The top test gets sealed and run, kill test first.
  4. **Backup Origins studies** from the item-7 design agent, to be merged with item 3's ranking.

### 2026-11-23: cold audit of the preprint (Fable) and fixes
- **Verdict:** revise, then post. Every numerical claim was checked against our files (`results/realdata/audit_checks.json`), and all held.
- **Fixed:**
  - **One counting convention.** Per-run sums, reported as the median and range over runs. The default-prior count is about 40, not 34, and the multiplier is about 32, not 38.
  - **Title.** "Is set by" became "is a fitted root-origination share applied to weakly informative gene families".
  - **Labels.** The real-data checks are now called "pre-specified", with the seal-to-run timing stated. The 0.01–10 band is labelled post hoc.
  - **Run-to-run instability added.** 810 families differ by more than 0.5 between runs, and L22 ranges from 0.001 to 0.89.
  - **Control section reframed.** The ranking works (AUC 0.93), but the calls are too low. The young-set limit was driven by PsaB alone.
  - **Direction of error.** A new paragraph says it is unknown: the controls suggest an undercount, while the early-exchange simulation suggests inflation.
  - **Bayes-factor count.** The "brackets Moody" claim is removed. The threshold rises with tree size.
  - **Smaller fixes.** The circular "reproduces 1,290.6" claim is removed. The identity is scoped to the shared-weight refit. The Table 3 R* definition is explained. The likelihood interval is stated per run.
  - **Citations.** Williams et al. 2023 added (deep-node underestimation; already in the library). The Csűrös SI wording changed to "could not retrieve".
- **Not done:**
  - Bremer 2022 and Williams 2023 GBE are not added, because neither was read.
  - The Csűrös SI (Fig. S41) needs a person to open it in a browser. The automated fetch was blocked, and we don't work around blocks.

### 2026-11-23: K6 sealed and running; origin-of-life routes ranked
- **K6 (prereg v8, sealed in 208991c).** Does the LUCA count stay the same when Moody et al.'s own method runs on their 65-genome subsample instead of 700 genomes?
  - We run our pipeline (IQ-TREE LG+F+G4 with 1,000 UFBoot, then ALE and Moody's reweighting) on a seeded random sample of 800 of the 5,122 families with at least 2 sequences.
  - A full run would take about 140 CPU-hours and more disk than the laptop has.
  - **Disclosed before sealing.** Moody's deposited subsample PPs give about 2× the 700-genome ΣPP. Their trimmed alignments are short: median 175 columns, and 47 for families with 100 or more sequences.
  - **Smoke test, 10 families.** The pipeline works end to end. Two IQ-TREE runs failed when the disk briefly filled, so the driver now retries failed families twice. Families with 50–60 sequences take 12–16 minutes each.
  - **Running.** Seven chunks of 120 families under the Origins lock, each resumable. The driver deletes tree files after each batch.
- **Origin-of-life routes** are mapped and ranked in `docs/plans/origin_routes_2026-11-23.md`. Each route has its riskiest claim that open data can check.
- **Queue (ranked):**
  1. **K6** primary readout, then the half-taxa jackknife (3 draws). Update the LUCA preprint if the result is decisive.
  2. **T1: is the vent exergonicity of LUCA's metabolism specific?** (Wimmer 2021.) This is the top origin-of-life test. Blocker: the 1.3 GB eQuilibrator cache won't fit on the disk now (about 3 GB free). Next step: check whether `equilibrator-api` can run on a smaller compound set; otherwise run it on AWS after 1 December. Seal before computing any ΔG.
  3. **T2: do asteroid amino-acid abundances predict the order in which amino acids entered the genetic code?** (Wehbi 2024 vs Bennu/Ryugu.) Takes minutes. Needs the Wehbi per-amino-acid values and Glavin's tables; Higgs & Pudritz 2009 must be read first.
  4. **T3: RNA persistence budget** per setting (MARHYS, USGS). The rate laws must be confirmed from legal copies first.
  5. **Backups:**
     - the acetogen call against w and 65 vs 700 genomes;
     - Huang 2026 root-weight dependence;
     - the K5 realism bound;
     - a red-team of the RAF and assembly-index results;
     - the purine:pyrimidine vs ammonia prediction.

### 2026-11-23: T2 result (asteroid amino acids vs genetic-code order)
- **Status.** Prereg sealed in f963a82. The power declaration (7cc5256) came before the real run, and the result is in 60486b9. Details: `experiments/t2_code_order/T2_RESULTS.md`.
- **Sealed verdict: cannot decide by design.** Ryugu A0106 reports only 9 of the 20 protein amino acids, so neither verdict reaches the 50% planted-power bar there.
- **The data.** Both returned samples meet the kill thresholds: partial τ (abundance vs Wehbi LUCA usage, controlling for molecular weight) is −0.02 for Bennu and −0.16 for Ryugu, with upper bounds 0.27 and 0.26.
  - A kill happens by chance in ≤ 5% of runs at a planted strength of 0.4 or more. So a moderate or strong availability effect beyond size is disfavoured. A weak one is not excluded.
  - Murchison (exploratory, and contamination-prone) gives raw τ = 0.46, which falls to a partial τ of 0.25 (p = 0.17) once molecular weight is controlled.
- **What would decide it:** more reported Ryugu amino acids (C0107, Parker 2023; the publisher blocks automated access), or Bennu analyses with lower detection limits.
- **Library.** Wehbi 2024, Glavin 2025, Higgs & Pudritz 2009 (arXiv) and Naraoka 2023 (HAL) were read and still need adding to library.json and the site.

### 2026-11-23: T1 design fixes from the planted control
- **Specificity ceiling.** At the vent cell with the gradient, the null is about 87% exergonic, so the core–null gap saturates at about 12 points even at a −60 kJ/mol shift. It could never reach the plan's 15. The decision moves to equal concentrations.
- **Setting window.** The window criterion is non-discriminating: the peak falls in the vent window in 86% of draws under the null, because with Q < 1, hotter is always more exergonic. The decision now uses the contrast only.
- **Direction arm.** It works as intended: kill when the gradient alone makes the share, support at −60.
- **Next.** An agent is applying these changes and fixing decisions D1–D15. I seal once its planted rerun is in.
- **K6.** 90 of 800 families are done. Laptop load is about 15, so a 30-family batch takes about an hour, and chunks run one batch at a time.

### 2026-11-24: T1 result (is LUCA's vent exergonicity specific?)
- **Status.** Prereg sealed in ff2efbe. Deviation T1-1 (D4 σ filter in the gate) was logged in e5c2d94 before the gate rerun. The gate passed in 259e88b. Details: `experiments/t1_vent_exergonic/T1_RESULTS.md`.
- **Sealed verdict: uninformative.** All three arms kill, and both null pools agree.
  - **Direction.** Under the 100-fold gradient at pH 9, 80 °C, the core *reversed* is still 62.1% exergonic (kill ≥ 50). The forward share is 96.5%, which replicates Wimmer.
  - **Specificity.** At equal concentrations, the core is *less* exergonic than matched non-core reactions: −8.4 points [−15.4, −2.0] against Rhea and −11.0 [−18.1, −4.7] against Xavier S4.
  - **Setting.** Vent − pond, core − null: +2.2 [0.0, 5.1] for Rhea and −0.3 [−2.5, 2.2] for S4. Planted power was low here, so read it as "no vent preference detected".
- **Plain reading.** The "LUCA's metabolism runs downhill at vents" number comes from the assumed product gradient. It is not a property of the core or of vents. Matched modern metabolism is at least as downhill.
- **Post hoc.** Wimmer's 77% counts 37 reactions they could not estimate (entered as ΔG = 0) as exergonic. On the 314 reactions that can be computed, the share is 74.8%.
- **Next.** Library entry for Wimmer 2021. Consider writing T1 up as a short note together with the K-series, once K6 is in. T3 (RNA persistence) is next in the queue.
- **K6.** Chunk q_aa finished (120 of 800 families; O_R 5.09 on that subset). q_ab is running under the Origins lock.

### 2026-11-24: T3 stopped before sealing; K6 operations change
- **T3 (RNA persistence per setting): cannot be decided with open field data.** Details: `experiments/t3_rna_persistence/T3_STATUS.md`. No field statistic was computed.
  - **Redesign.** The plan's "share of samples with L* < 45 nt" would have measured temperature only. The draft moved to a chemistry contrast in which temperature cancels, plus a guard for MARHYS endmember rows, which are by definition Mg = 0.
  - **Gate 2 (sealed in e7cc89e, then scored).** The Li & Breaker Mg term holds from 10 to 50 mM against Mojarro 2021 (within 1.3× at the median, slightly steep). It fails below 5 mM.
  - **Declared blind count.** All 710 Yellowstone rows have Mg < 5 mM. The in-range vent rows are seawater-dominated mixtures. The study would be empty or tautological, so it was not sealed.
  - **Reportable.** Claims that RNA is stable in Mg-poor natural water (e.g. Cohen 2024, soda lakes) rest on an untested part of the rate law. A low-Mg cleavage calibration would unlock T3; it is a good lab request.
- **K6 operations (OPS-1, OPS-2 in `experiments/luca_calib/k6/OPERATIONS.md`; method unchanged).**
  - Chunks are now 10 families.
  - The 5 families with ≥ 100 sequences run in a resumable IQ-TREE queue.
  - Finished trees from killed chunks are salvaged through the same `run_ale.py`.
- **Next.** Route 6 (lipid / compartment-first): do vesicle-compatible and RNA-compatible Mg windows overlap in real fluids? It uses the same MARHYS and USGS data and needs no rate law.

### 2026-11-24: T4 (vesicle and RNA windows in real waters): descriptive only
- **Not sealed.** The declared blind count's margins already fix every arm, so it is reported as description and labelled not blind (`experiments/t4_vesicle_rna_window/T4_STATUS.md`).
- **Finding.** In Yellowstone, at most 1.2% of 660 thermal-water rows (3 of 40 areas) could be in both the mixed-amphiphile vesicle window and the RNA Mg minimum. In MARHYS vent rows, almost none pass the vesicle Ca, salt and pH limits.
- **Pure fatty acid against ribozyme Mg** is empty by definition. That is a known lab fact.
- **Pattern across T3 and T4.** Open field-chemistry databases are too Mg-poor (springs) or too hot, salty or seawater-mixed (vents) to decide claims made at lab conditions. Next: a fresh Fable plan for studies whose decidability is checked by a blind count *before* design.

### 2026-11-24: new study list (Fable) and T5 started
- **Plan.** `docs/plans/next_studies_2026-11-24.md` (e87847a) ranks seven studies. Each was checked to be decidable on deposited data before any outcome was read. They move away from field geochemistry and toward deposited phylogenomic and lab datasets.
- **T5 = S1.** Is Wehbi 2024's "88.6% of LUCA Pfams agree with Moody" more than a breadth effect?
  - Old Pfams map to a median of 4 Moody COGs, young ones to 2.
  - Test: A (LUCA/pre-LUCA) against B (breadth-matched LBCA/LACA), bootstrapped over clans.
  - Kill: G < 10 points with the upper bound < 20. Support: G ≥ 30 with the lower bound > 20.
- **Status.** An agent is setting up the gate (reproduce 88.6% and their flags) and the planted check. B is not computed before the seal.
- **Library.** 23 papers from T3/T4 added (1950ff6, 185 total, live).

### 2026-11-24: T5 result (Wehbi 88.6% agreement with Moody): kill
- **Sealed in 2038f94, real run done.** Details: `experiments/t5_wehbi_moody/T5_RESULTS.md`.
- **Numbers.** A = 88.7% (LUCA/pre-LUCA Pfams, reproducing 88.6%). B = 80.6% (post-LUCA Pfams matched on breadth). G = 8.1 [5.6, 10.5], which meets the kill rule (G < 10 and upper bound < 20).
- **Reading.** The published validation is mostly a base rate. A Pfam "agrees" if any of its COGs has PP > 0.5, and old Pfams map to twice as many COGs. Shuffling PP within COG size gives A = 87.2%.
- **Caveat.** A small real age signal remains (G about 8, 7–13 across variants; p ≈ 0.0005 against the shuffle). Pre-LUCA Pfams have the smallest gap (3.7), and LACA Pfams match LUCA's rate.
- **Next.** S2 (Moody KO vs COG merging, against a re-run-noise null). A note to the Wehbi/Masel authors is for the owner to decide.

### 2026-11-24: T6 result (Moody KO vs COG merging): kill, and merging loses more than it gains
- **Sealed in 95e2a3e, real run done.** Details: `experiments/t6_moody_ko_cog/T6_RESULTS.md`.
- **Numbers.**
  - 23 of 433 eligible merge COGs are rescued (every member KO < 0.5, COG ≥ 0.75). That is 1.9% of the merge group; support needed 5%.
  - The matched re-run flip rate is 8.1%.
  - The ratio is 0.66 [0.40, 1.08]. Kill needed a lower bound ≤ 2. No variant reaches 2, and COGs with 3+ KOs give 0.30.
- **Stronger reading.** Look at COGs whose best KO is ≥ 0.75. The COG falls below 0.5 in 46% of merge COGs, against 15% of single-KO COGs. The mean COG PP is 0.096 below the best member. Moody's COG analysis does not recover LUCA families that KO splitting hid; it drops them more often.
- **Re-run noise.** Re-running alone changes the call at 0.5 for 11.2% of single-KO families (r = 0.80).
- **For K6 and the preprint.** Keep the KO-level unit. Treat the ~11% re-run call flip as a floor on per-family trust; this supports reporting LUCA content as a weighted sum rather than as a list.
- **Next.** Route 6 kill test (evaporation path, T4 follow-up 1). Then S3 (Ameta 2021 noise null).

### 2026-11-24: T8 result (Ameta 2021 growth-variation trade-off vs droplet noise): kill
- **Sealed in d479750, real run done.** Details: `experiments/t8_ameta_noise/T8_RESULTS.md`.
- **Gate.** The paper's Fisher test reproduces exactly (OR 0.086, p 1.62e-3).
- **Numbers.** 1,093 additions with at least 5 droplets on both sides, correlations within size strata:
  - yield vs perturbation −0.114;
  - yield vs split-half noise (nothing added) −0.154;
  - partial correlation given noise −0.057 [−0.121, 0.010].
- **Verdict.** Both kill arms hold. High-yield networks look stable because their droplets are less noisy.
- **Caveats.** The floor-based noise measure gives "partly" (−0.07). The paper's own subset, the 41 of its 162 pairs with enough droplets, still shows −0.65 after adjustment. That subset is small and selected, reported only.
- **Next.** T7 (Route 6 evaporation) is being set up; then S4 (Moody age prior) or S5 (DPANN completeness).

### 2026-11-24: T7 sealed; T9 result (DPANN loss vs genome completeness): inconclusive, at the edge of support
- **T7 (Route 6 evaporation path, PHREEQC Pitzer)** was sealed in 32876f0. Its real run (about 30 min) was killed three times by server restarts and is running again. The seal-time decisions are in the prereg.
- **T9 was sealed in 8325e9e and run.** Details: `experiments/t9_dpann_completeness/T9_RESULTS.md`.
  - Internal branches with ≥ 3 genomes: DPANN/other loss-fraction ratio 1.37 [1.146, 1.63]. Support needed a lower bound above 1.15, so the verdict is inconclusive by 0.004.
  - With the MHH root (reported only) the ratio is 1.40 [1.17, 1.66].
  - Every variant gives 1.30–1.45.
- **Reading.** Incompleteness inflates *tip* losses: arm A slope 0.81, and the DPANN tip excess is fully predicted by completeness. The deep-branch excess remains, so it is not an incompleteness artefact. This leans toward Huang's biological reading.
- **For K6.** Read tip losses from MAG-rich trees with care; deep-branch contrasts are sturdier.
- **Next.** T7 result; then S4 (Moody age prior; needs MCMCtree; timing first) or S6.

### 2026-11-24: T7 result (Route 6: evaporating Yellowstone waters into a joint vesicle and RNA window): inconclusive
- **Sealed in 32876f0, run detached (restarts had killed it three times).** Details: `experiments/t7_evaporation_window/T7_RESULTS.md`.
- **Numbers.**
  - USGS mixed arm: 15 of 528 waters (6 of 37 areas) pass, S = 2.8% (0.3–9.4%). This is below the 5% bar, but the interval crosses it, so the verdict is inconclusive.
  - Historic set: 1.3% (0.1–7.3%).
  - Pure fatty acid: 0.6%. That would be a kill on the primary path, but the open-air path with generous minerals opens it (6.3%).
- **Mechanism.** Half the waters never reach 1 mM Mg before salt stops the path (Yellowstone water has little Mg relative to Na). Most others fail on Ca + pH.
- **Reported only.** Near-neutral waters (pH ≥ 4.5): 5.6%. Strict minerals: 0.2%.
- **Reading.** Evaporation does not generally solve the Mg problem for lipid-first ponds. A few special waters (near-neutral, Mg-richer, Na-poor) could. Route 6 is not killed; it is narrowed to those waters.
- **Next.** S4 (Moody age prior) is in setup: prior art, PAML build and timing. A second hot-spring province would narrow T7.

### 2026-11-24: T10 (S4, is Moody's 4.2 Ga LUCA set by the prior?) parked until 1 December
- **Setup done, not sealed.** See `experiments/t10_luca_age_prior/T10_STATUS.md`.
- **Prior art.** It does not settle the question. No one has moved the 4.52 Ga maximum or the rate prior on Moody's data.
- **Why parked.** One full MCMCtree chain is 28–42 laptop CPU-days. The cheapest decisive kill test (P1 under both clocks, 4 chains at 2M iterations) is about 95 core-hours, roughly $1–2 on spot, which is over this month's remaining cap.
- **Next for S4.** Run it after 1 December, or on the laptop if a normal-priority timing run shows it fits.
- **Study list.** S6 (ribozyme epistasis vs tertiary contacts) and S7 (Attwater exponential, gate first) remain. Next: S6.

### 2026-11-24: new study list (Fable, 2026-11-25 plan)
- `docs/plans/next_studies_2026-11-25.md` ranks five more studies, each checked to be decidable on deposited data. They move away from LUCA phylogenomics:
  - **N1 (top).** Janzen 2022: is ribozyme specificity rising with activity a background-floor artefact of an entropy index?
  - **N2.** Rotrattanadumrong & Yokobayashi 2022: does a ligase neutral network need higher-order epistasis?
  - **N3.** Peng, Linderoth & Baum 2022: are nested autocatalytic tiers more than rewired networks give?
  - **N4.** van Duppen 2023: do formose mixtures under flow differ beyond replicate noise?
  - **N5 (marginal).** Wehbi 2026: is the tryptophan depletion more than scatter?
- S6 (T11) is in setup. N1 becomes T12.

### 2026-11-24: T11 result (S6, epistasis vs tertiary contacts in five ribozymes): inconclusive
- **Sealed in 288b952 and run.** Details: `experiments/t11_ribozyme_epistasis/T11_RESULTS.md`. Data: Roberts et al. 2023 full double-mutant scans.
- **Numbers.**
  - Base pairs, the positive control: pooled matched Δ = 0.44 (0.33–0.50). Four of five ribozymes pass; hatchet fails, as predicted from its near-neutral singles.
  - Tertiary contacts: Δ = 0.11 (90% interval −0.02 to 0.23). Support missed on the lower bound. Kill missed because 0.15 is not excluded.
- **Reported only.** Every sensitive ribozyme leans positive (0.07–0.16 under every variant; CPEB3 0.15). Non-contact distance bands show no proximity gradient.
- **Reading.** Epistasis maps read base pairing almost perfectly and 3D contacts only faintly (matched AUC about 0.6). Our QT45 negative (#30) is what this method should give. It is not evidence against structure.
- **Next.** N1 (T12, Janzen specificity floor) is in setup. Then N2–N5 and S7.

### 2026-11-24: T12 result (N1, Janzen 2022: does ribozyme specificity rise with activity?): kill of the general claim
- **Sealed in 65e1b15 and run.** Details: `experiments/t12_janzen_specificity/T12_RESULTS.md`. Before sealing I added one reported-only noise-sensitivity readout (it adds no random draws).
- **Numbers.** Table 1 was reproduced first. Then the floor was removed (all_sum > 30, r − 1) and shared noise corrected by SIMEX. Per family:
  - 2.1: R_S −0.41 (−0.52, −0.31), **support**.
  - 1A.1: −0.25 (−0.53, +0.02), killed because the interval touches 0; underpowered.
  - 1B.1: −0.05, kill.
  - 2.2: +0.10, kill.
  - Overall: kill, 3 of 4 families.
- **Reported only.** The plan's rule and the uncorrected rule both give "mixed", but both give false support in no-link planted runs. If the real noise were half the deposited bootstrap noise, 1B.1 would reach −0.15. The kill leans partly on the noise assumption.
- **Reading.** The paper's R of −0.54 to −0.84 is mostly the background floor. "Specificity for free under selection for activity" holds in one family, not as a rule.
- **Next.** N2 (Rotrattanadumrong & Yokobayashi ligase epistasis) setup. K6 continues.

### 2026-11-24: T13 result (N2, does the ligase neutral network need higher-order epistasis?): partly
- **Sealed in 0321f9b and run.** Details: `experiments/t13_ligase_global_epistasis/T13_RESULTS.md`. The gate reproduced the authors' split (20,920 / 8,967) and the generation 8 neutral fraction (0.279).
- **Numbers, generation 8.** One global curve fitted on generations 1–6 recalls 0.1% of the neutral variants, so the kill fails on recall. AP: curve 0.467, network 0.516, null 0.378. The lift is 0.049, below the 0.10 needed for support.
- **Reported only.** Nearby (held-out generations 1–6 and generation 7), the curve recalls 80% of neutral variants, near the replicate ceiling, and the network adds under 0.10 AP. Pair terms do worse than the curve everywhere.
- **Reading.** The paper's "an additive model would have called them dead" holds, even with a global curve. "So the network learned higher-order effects" is only weakly supported. Far-away neutral variants are not predictable by any model tested here. With QT45 (#30): "one curve suffices" is a local statement.
- **Next.** N3 (Peng/Linderoth/Baum autocatalytic tiers) setup. K6 continues.

### 2026-11-25: T14 sealed and running; T15 result (N4, van Duppen 2023 formose under dynamic flow): kill
- **T14** (N3, autocatalytic tiers against rewired networks) was sealed in 78bd277. The gate reproduced the paper exactly. `real` is running detached, about 1.7 h.
- **T15 sealed in 5304720 and run.** Details: `experiments/t15_formose_flow_noise/T15_RESULTS.md`.
  - **The authors' test.** The published p ≤ 10⁻⁴ come from a pooled t-test on the serial samples of one run against another, with no run-to-run variance (found in their code).
  - **Numbers.** The median dynamic-vs-steady shift is 0.9–2.4 within-run SD. Repeat runs at identical settings differ by 2.7–6 SD (DHA, threose, xylulose) and about 14 SD (erythrulose). Kill holds in 4 of 4 compounds, and in 3 of 3 without erythrulose.
  - **Reading.** The flow effect is not shown beyond run-to-run reproducibility. The repeats span days and the comparisons do not, and power is limited, so this is not proof of no effect.
- **Next.** N5 (marginal, gate first) or S7 (Attwater, gate first). K6 continues.

### 2026-11-25: T14 result (N3, Peng/Linderoth/Baum 2022 autocatalytic tiers against rewired networks): support
- **Sealed in 78bd277 and run** detached, with 200 + 200 rewires and no fallback. Details: `experiments/t14_autocatalytic_tiers/T14_RESULTS.md`.
- **Numbers.**
  - The biochemical network has 3 nested sets (nested share 1.0, chain depth 3).
  - Under both degree-preserving nulls, the rewired copies give 1 set and nested share 0 at every central quantile.
  - Rewired networks have 3–4× more seeds (median 1,349 swap, 1,003 strict, against 304) and a largest set about 2× bigger.
- **Reading.**
  - This is the first support in the series. Nested tiers are a property of the specific chemistry, not of degrees.
  - Rewiring makes networks *more* autocatalytic. Real biochemistry is tiered because its autocatalysis is constrained.
  - The abiotic network has a single set, consistent with its null, so the result covers the biochemical half only.
- **Next.** An element-balance null built from KEGG formulas would separate atom bookkeeping from biochemical organisation. It is a candidate follow-up.

### 2026-11-25: T16 (S7, is Attwater 2025's ribozyme replication exponential?): not decidable, stopped at the power gate
- **Record.** `experiments/t16_attwater_exponential/README.md`. No growth law was ever fitted to the real data. Only the replicate scatter was read.
- **Why it stopped.**
  - The data are 3 reactions over growth cycles 0–4.
  - 86–92% of the scatter is a constant offset per reaction.
  - At the published rates, the plan's AICc rule supports "exponential" under 1% of the time even when growth truly is exponential.
  - Its kill would fire 45–100% of the time on a truly exponential curve.
  - Using all 9 cycles with a plateau term makes it worse.
- **Noted, no test needed.**
  - The caption's e^0.38x and e^0.20x mean 1.46- and 1.22-fold per cycle, but the text says "1.2- and 1.38-fold".
  - The deposited "Mean" row is not the mean or median of the three datasets. **Corrected 2026-11-25 by a fresh recheck:** the Mean rows are geometric means, but the two Dataset 2 rows are swapped between the FITC and Cy5 blocks of SD_Fig3e.xlsx. The fold point (text gives 1 + k, not e^k) was confirmed.
  - Whether to tell the authors is the owner's call.
- **The study list.** Only N5 (marginal) is left. A new Fable list has been asked for, with the T14 follow-up (an element-balance null for the autocatalytic tiers) as a candidate.

### 2026-11-25: T18 (QT45's error threshold from its own landscape): the method failed its planted kill test; not sealed, no real threshold computed
- **Record.** `experiments/t18_qt45_error_threshold/README.md`, `PRIOR_ART.md`, prereg draft `docs/prereg/t18_qt45_error_threshold.md` (unsealed).
- **Prior art.** The QT45 authors (Gianni 2026, fig. S32B) already modelled a quasispecies on this landscape: "<0.5%" active at 94.1% fidelity. They set every unmeasured double and every genotype with 3+ mutations to a growth rate of 0.01. At 94.1% about 89% of offspring per round trip carry 3+ mutations, so that value decides their answer. No threshold, no interval, no planted check. Relaxed-threshold theory (Kun 2005, Szilágyi 2014) has not been applied to a polymerase's own measured landscape.
- **Fidelity confirmed.** 94.1% per nucleotide (main text, Fig. 4D); the 10.9% perfect-read share implies 94.9%.
- **Gate passed.** The population estimator lands within 0.07% (single peak), 0.05% (mesa) and 0.7% (site-independent) of exact thresholds.
- **Kill test failed.** A global-epistasis curve fitted to singles and doubles recovers a planted threshold within 20% on 20/20 noise-only landscapes (median error 2.5%), but on 1/6 landscapes with planted pair and higher-order epistasis (median −27%, always low). The cause is pair epistasis: terms too small to see in one double add up over the 4–6 mutations genotypes carry near the threshold.
- **Ruling.** Kill test failed; F2 re-run not run (failure is systematic bias per the attached diagnostic; precision re-run cannot fix it); no real-data threshold computed.
- **Status.** Under fallback F2 the real-data verdict would be "not decidable by this method". The next step is a T18b design that keeps the measured pair terms, with its own planted test (including mostly-negative epistasis). Nothing changed in T18's rules.

### 2026-11-25: K7 (K5 realism bound) pilot: reconciliation barely sees stem-to-stem transfer
- **Record.** `experiments/k7_realism_bound/`, draft prereg `docs/prereg/k7_realism_bound.md` (not sealed). Moody's per-family reconciliations are public (data.bris, doi:10.5523/bris.405xnm7ei36d2cj65nrirg3ip; 77,286 `.uml_rec` files on the focal tree).
- **Question.** Is K5's adversary (stem transfer 115–600× background) realistic, judged by the stem transfer Moody 2024's own reconciliations imply? At face value their Supplementary Data 5 puts the stems at about background (0.72× and 1.05× the all-node mean).
- **Pilot (seed 1, planted m = 1–600×).** Neither preregistered measure responds to the planted multiplier. At 600× the families truly crossed between stems 187 times, and ALE inferred about 0.6 stem-donor transfers; the crossings became root presence instead (stem-born families' root presence 0.07 → about 0.2). Planted values sit inside the null spread across tree sizes.
- **Caveat.** The laptop ALE build crashes on families over 152 genes, which held 77% of the true crossings at 600×, so this is a warning, not a kill. The full planted test (about 4–5 core-hours on Linux) is for the coordinator.
- **What it means if it holds.** A low stem-transfer ratio in real reconciliations is not evidence against heavy stem exchange, because the method maps that exchange onto LUCA. This is the mechanism behind K5's failure, measured rather than argued.

### 2026-11-25: new study list U1–U9 (docs/NEW_STUDIES_2026-11-25.md)
Ranked by how much the result could change a route, times how feasible it is. Each entry gives the quoted claim, a checked data link, the kill and support rules, the null, the power risk and a prior-art scan.
1. **U1.** Do T14's nested tiers survive an atom-conserving null? (Peng 2022) This is next. The mixing gate comes first.
2. **U2.** Encapsulation gains in ribozymes against the difference in noise between conditions. (Lai 2021, data on Zenodo)
3. **U3.** Bendixsen 2019: is "over half dual-function" a read floor?
4. **U4.** Papastavrou 2024: fidelity against selection strength. One lineage per arm is the weak point.
5. **U5.** Goldford 2024: are metal enzymes enriched early at reaction level, tested with a within-pathway permutation?
6. **U6.** Mizuuchi 2022: which arrows of the replicator network survive replicate noise?
7. **U7.** Robinson 2022: formose differences between environments against repeat runs.
8. **U8.** Cleaves 2023: does the accuracy hold when whole sample families are held out? (peripheral)
9. **U9.** Pressman 2019: is the frustrated landscape real? (gate first)

U5 and U7 were quoted from abstracts only. Before either is sealed, a legal full text has to be read.

### 2026-11-26: moved to a new laptop; T18b pilot relaunched; queue re-ranked (Fable)
- **Environment.** Repo venv `.venv`: Python 3.15.2, numpy 2.5.5, scipy 1.18.1 (the same numpy/scipy as the old `t1_vent_exergonic/.venv`). Every sealed file matches its latest line in `docs/prereg/HASHES.txt`; the older mismatching lines are superseded by logged deviations. IQ-TREE 3.1.4 and the unchanged ALE binaries were restored, and ALE reproduces a stored family's likelihoods exactly (`experiments/luca_calib/k6/OPERATIONS.md`, OPS-3).
- **T18b.** The old laptop left no finished pilot replicate. The pilot (prereg F4: B and E 0–4; A, C, D and F 0–1) was relaunched at 17:39Z with 3 single-thread workers at nice 20. Before any replicate finished, the rival explanations of a pass or fail were written into `experiments/t18_qt45_error_threshold/README.md`. Open issue: prereg F4 says planted N drops to 3,000 once a replicate takes more than 10 CPU min, but the committed code keeps N = 5,000. The pilot runs as committed; the coordinator decides.
- **T17 (U1).** It never reached `real`. The blind dry run has 21 of 28 parts; Null A draws 25–200 are missing, and the sealed `dryrun_verdict` refuses until every null is complete. The README now says "sealed". It resumes after the T18b pilot (one heavy job per project).
- **K6.** 505 of 800 families done. It runs after T17.
- **Attwater email (T16).** The coordinator approved it on 2026-11-26. The address is from the official UCL profile. The draft is in the hub's `.local`. **Not sent:** AgentMail is not connected in this laptop's executor, so it needs the owner to reconnect the AgentMail integration.
- **Fable re-rank (2026-11-26).**
  1. U4 (Papastavrou 2024, CC0 Zenodo 10714366; selection strength vs fidelity in the only lab RNA error-threshold demonstration).
  2. K7 full planted test (Linux ALE).
  3. U5 (Goldford 2024; needs a legal full text).
  4. U2 (Lai 2021).
  5. U3 (Bendixsen 2019).
  6. U9, gate only.
  7. U6, power gate only.
  - Drop U7 (T15 already makes the point; four repeat sets cannot support) and U8 (peripheral).
  - Queue advice: T18b pilot verdict, then T17 real (outcomes are kill, partly or not decidable, since support is unreachable by its own prereg), then K7 when Linux is available, then the rest of K6. If the T18b pilot survives, do not automatically spend the 20–30 core-hours of the full test ahead of U4 and K7.
- **Decision.**
  - Adopted, with one change: K7 needs Linux ALE. AWS has about $1 left until 1 December, so K6 keeps the laptop slot after T17, and K7 goes first on AWS from 1 December (coordinator approved spot within the cap).
  - U4 prior art and a data check are prepared now as the light job: low CPU, done alongside.
  - Fable's idea of a free GitHub-hosted Linux runner for K7 is the owner's call. It is not used.

### 2026-11-26: T18b failed its planted kill test; the QT45 threshold line is closed
- **Result.** The F4 pilot (18 replicates, N = 5,000 under D-F4, merged 2026-11-26) failed in family E (higher-order epistasis only): 0 of 5 replicates were within 20%. Every E threshold came out high; the posterior-mode estimate was +42%, and most draws were above the 0.25 grid. A (no epistasis) was recovered within 1%. B passed 1 of 3 scored, C 0 of 2 (+61%, +90%). D's truths were above the grid, so D was unscored. F passed 2 of 2 through correct triple flags. There were no false triple flags. Full table: prereg "Planted results".
- **Reading.** This matches rival 1, written before the results: τ̂ absorbs higher-order epistasis (E's τ̂ was 0.13–0.22 with no true pair terms), which inflates the extrapolation. T18 (pairs dropped) erred −27%; T18b (pairs kept) errs high. Both fit the same singles and doubles. So the threshold is not identifiable to within 20% from HD ≤ 2 data on these landscapes.
- **Decision (coordinator's standing rule).** Closed. There is no T18c and `real` is not written. No real-data threshold was computed. Negative atlas and site updated.
- **Queue now.** T17 dry run (Null A 25–200, 3 workers), then `dryrun_verdict`, then T17 real, then K6. K7's GitHub-runner workflow is written and tested locally. Pushing it waits on the `workflow` token scope (owner). U4 prior art is done (data check: "partly").
- **Updated ranking (unblocked).** 1. T17 real (running). 2. K7 on GitHub runner (needs the token scope) or AWS from 1 Dec. 3. K6 remainder (laptop, after T17). 4. U4 with a member-wise raw-data pull. 5. U5. 6. U2. 7. U3. U9 and U6 are gate only. The QT45 line (T18/T18b) is closed.
