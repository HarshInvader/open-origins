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
