# Pre-registration (T13): does the ligase neutral network need higher-order epistasis, or does one global curve do?

Status: DRAFT, written 2026-11-25 by the T13 prep agent. This is study N2 in `docs/plans/next_studies_2026-11-25.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run, and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t13_ligase_global_epistasis/scripts/t13_analysis.py` with its current sha256 (`f8d20c02c14a8aab32cb2c493bd00289eecc732a05b749e6d2aa344db874d9a7`). Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is whether an additive latent score through one saturating curve, fitted only to generations 1-6, recovers the generation-8 neutral variants that the authors' log-additive model calls deleterious. Every deciding number comes from scoring that model against generation-8 per-variant outcomes, and that has not been done.

- **Not computed.** Model G, model GP and the network have never been fitted to, or scored against, a real generation 7 or 8 outcome. No real recall, AP, lift or null on generation 8 exists in this repo.
- **Fitting is confined to generations 1-6.** All three models are fitted on the authors' own 20,920-row training split of generations 1-6 only, in every mode. Generation 7 and 8 rows are read for their genotypes and for the gate's published-marginal checks, never for fitting.
- **The gate's looks at generations 7 and 8 are the authors' own published numbers.** `gate` recomputes exactly the quantities the paper prints: the generation-8 observed neutral fraction (0.2791 against the published 0.28), the share of those neutral variants the authors' log-additive model also expects to be neutral (0.0033, their "almost all ... expected to be deleterious"), and the generation-7 fractions by algorithm (0.736 / 0.888 / 0.897 against the published 0.74 / 0.89 / --). These are published marginals; they are the claim being tested, not a peek at the answer, and no model of ours is involved in any of them.
- **Generation 1 and WT/Mut marginals.** Generation-1 neutral fraction 0.109 (published 0.11), the authors' Fig. 2c log-additive R2 on generation 1 at Hamming distance > 1 of 0.75497 (published 75.5%), WT/Mut library neutral fraction 0.6020 (published 0.60), and the replicate ceiling in that library (AP 0.9973, rho 0.9833, recall 0.8452). All published or replicate-only.
- **The planted check uses real genotypes, real generation 1-6 outcomes and real replicate noise.** The H0 world starts from model G fitted to the real generation 1-6 training split, keeps the real generation-7 and generation-8 *genotypes*, and draws measurement noise from a bank of real replicate deviations (RA_rep - Mean_RA) binned by level, built from generations 1-6. One published marginal enters the calibration: the 0.28 of Fig. 3b. No generation-7 or generation-8 per-variant outcome enters. Only synthetic verdicts and means were printed (table below).
- **Dry run.** `dryrun` runs the whole `real` path with the generation-7 and generation-8 labels permuted within Hamming-distance bins before anything is scored. Its numbers are disclosed below. The generation 1-6 held-out split inside it is *not* permuted, which is why its numbers there are real; that is a check that the pipeline works, and it is reported, not ruled on.
- **An earlier draft of the script ran `gate` once.** Same numbers; the script hash then was `0a03bef0...`, and the gate was rerun with the final hash.
- **What this does to my expectation.** The planted check shows the test has power: a pure global-curve world gives kill in 7/10 (generation-1-6-pinned) and 10/10 (generation-8-pinned) replicates, and planted pairwise interactions that flip 30% of generation-8 calls give support in 10/10 with no false kills. It also shows one real limit: planted *third-order* interactions of the same severity give "partly" in 10/10, never support. So a support verdict is informative and a kill verdict is informative, but a "partly" cannot distinguish a weak global-curve failure from genuine third-order structure. I hold no expectation on which way the real data falls.

## Claim under test

Rotrattanadumrong and Yokobayashi 2022, "Experimental exploration of a ribozyme neutral network using evolutionary algorithm and deep learning", Nat. Commun. 13:4847, doi:10.1038/s41467-022-32538-z (PMC9385714), read from `experiments/t13_ligase_global_epistasis/raw/europepmc/PMC9385714_fulltext.xml`.

- Results, verbatim: "In generation 8, almost all neutral mutants identified were expected to be deleterious under the epistasis-free model. This indicated that the neural network was able to learn higher-order, nonlinear mutational effects, and identify distant neutral mutants that would have been inaccessible through in silico selection, mutation, and recombination alone."
- Results, verbatim: "In generation 7c, less than half of the neutral mutants could be identified using the log-additive model (Fig. 3b, hatched bars). This suggests an increasing contribution from epistasis at higher Hamming distances."
- Results, verbatim: "the fraction of neutral mutants in generation 8 was only 0.28".
- Walsh-Hadamard analysis, verbatim: "only the 3rd order terms were required to achieve an accuracy similar to that of the current MLP model (R2 ~ 0.72)".
- The authors' own caveat, verbatim: "Finally, some of the nonlinearities identified in this library could be attributed to global noise from experimental errors. ... Further statistical tests could be performed to remove global nonlinearities, which could improve model performance."
- Fig. 3a caption, verbatim: "trained on 20,920 variants from generations 1-6 ... held-out testing set of 8967 variants".

**Why it might be an artefact.** "Epistasis-free" in the claim means the authors' log-additive model *on the measured scale*: expRA = exp(sum of ln RA of the constituent single mutants). That model is multiplicative in RA, so at Hamming distance 12-13 it drives the prediction to near zero no matter how mild each mutation is. A model with no specific interaction of any order — an additive latent score through one monotone saturating curve — makes a different prediction there, because the curve's floor and ceiling absorb the accumulation. So "the log-additive model expected them to be deleterious" does not imply "higher-order epistasis". Whether it does here is an empirical question, and it is the one this study asks.

**H1 (the authors' reading).** Recovering generation-8 neutral variants needs specific interactions: a model with pairwise or network-learned interactions beats the single-curve model on the same data.

**H0 (this study's alternative).** One additive latent score through one monotone curve, fitted to generations 1-6 only, recovers the generation-8 neutral variants about as well as any interaction-carrying model trained on the same rows.

## Inputs (exact)

Source: the authors' Zenodo deposit, doi:10.5281/zenodo.6945203, `Rotrattanadumrong_2022_ligase_ribz_evolution.zip`, 136,702,776 bytes, 138 entries. The zip was **not** downloaded. Its central directory was listed by HTTP range request and each member below was range-fetched, inflated, CRC- and size-checked, and written on its own (`scripts/zip_fetch.py`; listing in `raw/zenodo/zip_listing.tsv`). The `sampled_paths*.txt` members are Python pickles and were never fetched or read. `raw/` is gitignored (`.gitignore:41:experiments/*/raw/`). Total on disk 21 MB. Every hash below is re-checked at the start of every run and the run stops on a mismatch.

| File (basename) | sha256 | bytes | rows |
|---|---|---|---|
| README.txt | a66ef96f582a81008e3a4ad3181f259a40e7d696adc803ddeb3b74eac263cfec | 1946 | - |
| Filtered_Lib1_R1_R2_QS20.csv | a29b42c04261e65f38c0aa03eb26e507d44bc3fdc35e0d11003dc2ea683b78fd | 1707377 | 10000 |
| Filtered_Lib2_R1_R2_QS20.csv | 8902261dab6e351585046fabc6379910e8ce26c3ee054b2a932af3400fa372b2 | 340359 | 1985 |
| Filtered_Lib3_R1_R2_QS20.csv | cf2c6864ff2344ffee296d89f31e1d309bb4ac7a9286c2b998a79d3f358f881b | 338343 | 1985 |
| Filtered_Lib4_R1_R2_QS20.csv | becdcb169e4f1a0271772427a3406d5b7f8fbc71822914bf80a12642d1fcf8e2 | 332792 | 1985 |
| Filtered_Lib4B_R1_R2_QS20.csv | cededa1da23a69f781fbefac3e44cb28ace0b59981b41c26a3bef7865d0b06ff | 372788 | 1984 |
| Filtered_Lib5_R1_R2_QS20.csv | 3ef6fe0fa17140df32baa272cd47129cadc1b616756be62d0f8dc37bb9d2aa6e | 845260 | 5981 |
| Filtered_Lib6_R1_R2_QS20.csv | dcc7d3f20ab2232637eeb11096bc15529e09ace35196ea57943672dc0ec8aeee | 1005692 | 5967 |
| Filtered_Lib7_R1_R2_QS20.csv | abd1604c01108b0fb6c64338d66308ec38aaa07f88642a3d9b2410c292b3ae0d | 1742397 | 9977 |
| Filtered_Lib7_MLP_R1_R2_QS20.csv | 15c7b43d324a1d96e5196483893638a4c551682f2c5ed3853c55b24272308206 | 178995 | 1000 |
| Filtered_Lib7_MLP_xtra_R1_R2_QS20.csv | 9011f86759474291860f0ed485ebc4cea55001b6c01ebefbcc3eac41812b7b4e | 169515 | 999 |
| Filtered_Lib8_R1_R2_QS20.csv | 924925f8ec55120cb27fb0fb296b4bd5340275e95553916a31aaff7da3c8001a | 1852535 | 11960 |
| Filtered_LibWT_Mut_R1_R2_QS20_tolerance_1.csv | 09de9febd525d57b06d2122426fe3fc5099a2d4dfae043d24f589ce2003a8ba0 | 10624365 | 65536 |
| Models_scores.csv | 4180a76550502390b39bb0d3c97b6e3dd9e8f7cee786647b83946fc629b6fb8e | 671 | - |
| ML_Recall_by_HD.csv | 6d7f3dcf408b2d2a522a04f1da2d4cae5c537277f330f6128708e5ac155555a0 | 772 | - |
| ML_Precisions_by_HD.csv | 8605dbdc4f729b8f32df068b1ded53e4e3172f869629cc73c29e75d33a7a05ae | 679 | - |
| kfold_metrics.csv | a7de77a89d5a13968c38a24a7dd976f116d18ecda58aa5f2f4dfa02bb5bc7036 | 423 | - |
| Machine_Learning_Models.ipynb | 0669f134d8cc99d5e9be450f0de5ae85f13c9d48def3728932d993c76357424b | 32482 | - |
| Generate_Figure_2.ipynb | f50075db2f56e886717a6a4fa646b892a608078bb890af8f65f410f4dfa405ce | 432293 | - |
| Generate_Figure_3.ipynb | f16878ec61d8b84b759e9f090ca4506b497ccd0793a0644042d847f66a4ebc45 | 338150 | - |

Full text of the paper: `raw/europepmc/PMC9385714_fulltext.xml`, sha256 f27898facbcb796d8fc7e48cfd1f4a1ff521ce4759a297d1389e8dfb4ca36a84.

Code: `scripts/t13_analysis.py` f8d20c02c14a8aab32cb2c493bd00289eecc732a05b749e6d2aa344db874d9a7; `scripts/zip_fetch.py` 6e86afdf040c3b2e5904a5c07e95794590529e97b1b8ebd786ec7abafb8ec5e4; `scripts/xml2txt.py` 6ddc146e399b4db6295fc1382774f16a6381fb8223e60e253bbdf51274316698; `scripts/nb_code.py` ab39d92e2dde863346c73ae5fb519fde5421991d88e2ef9c8be5defb789b72bf. Everything is parsed with `python3 -I` under the repo's `t1_vent_exergonic` venv (numpy 2.5.5, scipy 1.18.1); the archive is treated as untrusted data throughout.

## Gate (`t13_analysis.py gate`; run; passed)

The gate must reproduce the authors' own construction and the claim's premise before anything else runs. `gate_pass: true`; full output in `scripts_out/t13_gate.json`.

| Check | Ours | Published | Status |
|---|---|---|---|
| Generations 1-6, unique rows | 29,887 | - | - |
| Authors' train / test split | 20,920 / 8,967 | 20,920 / 8,967 | exact |
| Generation-8 observed neutral fraction | 0.27910 | 0.28 (Fig. 3b) | match |
| Generation-8 neutral variants the log-additive model also calls neutral | 0.00330 | "almost all ... expected to be deleterious" | reproduced |
| Generation 7a observed neutral fraction | 0.73589 | 0.74 | match |
| Generation 7b | 0.88800 | 0.89 | match |
| Generation 7c | 0.89690 | (<0.5 also-expected: ours 0.419) | match |
| Generation-1 neutral fraction | 0.10900 | 0.11 (Fig. 5a) | match |
| Generation-1 log-additive R2, HD > 1 (Fig. 2c) | 0.754971 | 0.755 | match |
| WT/Mut library neutral fraction | 0.60204 | 0.60 (Fig. 5a) | match |
| Single mutants missing from the data | 0 | - | - |

Replicate ceiling, from the 65,536-row WT/Mut library (replicate 1 predicting replicate 2): AP 0.99730, Spearman 0.98329, recall at RA >= 0.2 of 0.84525.

The split is reproduced as `np.random.RandomState(0).permutation(n)` with the test set the first `ceil(0.3n)` rows, which matches sklearn's `train_test_split(test_size=0.30, random_state=0)` on the authors' own file order (Lib1, Lib6, Lib4, Lib3, Lib2, Lib5, Lib4B, from `Machine_Learning_Models.ipynb`).

## Fixed decisions

- **D1. Neutrality.** A variant is neutral iff `Mean_RA >= 0.2`, the paper's own threshold, on its own measured value. Never on a model's.
- **D2. Rows and split.** Training is the authors' own 20,920-row split of generations 1-6; the 8,967-row held-out split is reported, never ruled on. Generations 7 and 8 contribute genotypes only.
- **D3. Model G.** `phi = b0 + X beta` with one term per (position, base) mutation away from wild type (105 terms, 35 positions); `g(phi) = lo + (hi - lo) * sigmoid(phi)`. Fitted by `scipy.optimize.least_squares` with an analytic Jacobian against measured `Mean_RA` on the training split. `lo` is bounded to [-0.2, 0.3] and `hi - lo` to [0.5, 3.0] times the largest measured activity, because unbounded fits ran the asymptote to ~1e12 and made every generation-8 prediction non-neutral. No interaction term of any order.
- **D4. The authors' model (LA).** Their own definition, `expRA = exp(sum of ln RA of the single mutants)`, with the singles pooled over all generations. Reported, used in the gate, never fitted.
- **D5. Model GP.** G's fitted curve, plus one ridge term (penalty 1.0) per mutation pair that co-occurs at least 100 times in the training split, fitted on the latent scale. 467 pairs qualify.
- **D6. The network.** A numpy MLP on the one-hot sequence (140 inputs), hidden layers 128-64-32 (the authors' own sizes), BCE loss on the same neutral/deleterious labels and the same rows as the authors' MLP; Adam, 100 epochs, batch 1024, lr 0.005. Its reported AP is the **best of 3 seeds**, so one bad initialisation cannot hide a learnable interaction. (The authors likewise picked the best of five model families.)
- **D7. Decision rules.** Below.
- **D8. Null.** The scored model's predictions are shuffled within Hamming-distance-to-wild-type bins (each distance its own bin; bins with fewer than 30 rows merged into one), 20 shuffles, median AP reported. A bin-preserving null, so distance alone cannot carry the result.
- **D9. Ceiling.** The replicate ceiling from the WT/Mut library (above) is reported beside every AP. A model cannot be asked to beat it.
- **D10. Seed.** 20261125, with every stochastic step drawing from a named sub-stream.
- **D11. Seal.** `real` refuses to run unless `docs/prereg/HASHES.txt` contains a line naming `experiments/t13_ligase_global_epistasis/scripts/t13_analysis.py` that begins with the script's current sha256. `sealcheck` prints that state. Currently `real_allowed: false`.

## Decision rules

Applied to generation 8, the generation the claim is about. `lift` = (the better of GP and the network) minus G, in average precision, on the same rows.

- **Kill** (the authors' reading of generation 8 does not survive): `recall_G >= 0.80` **and** `lift <= 0.05`. That is, the single-curve model recovers at least 80% of the measured generation-8 neutral variants, and no interaction-carrying model trained on the same rows beats it by more than 0.05 AP.
- **Support** (specific interactions are needed): not kill, **and** `lift >= 0.10`.
- **Partly**: anything else.

The plan's rule as written is computed and reported alongside every verdict, in every mode, as `plan_as_written`.

## Changes from the plan, made before the seal

The plan's rules were run in the planted check first; two of them are miscalibrated. Both changes are to the *form* of the rule, documented here, decided before any real generation-8 outcome was scored.

1. **The plan's support clause is unreachable.** The plan required `recall_G < 0.50` for support. In the planted worlds with real pairwise interactions severe enough to flip 30% or 45% of generation-8 calls, `recall_G` stays at 0.77 and 0.84 — the global curve keeps recovering most neutral variants even while a pair model beats it clearly on ranking. Under the plan as written, *support is never reached in any scenario*, including the one built to demand it (0/10). The recall clause was therefore dropped from the support rule, which now rests on lift alone. With that change the planted pair scenarios reach support 10/10 and the nulls still never do.
2. **Lift is measured against the better of GP and the network, not the network alone.** The plan's kill clause compared AP(G) to AP(net). Pair terms are the specific-interaction model the question is actually about, and in the flip-45 scenario GP and the net disagree about which detects the planting. Taking the maximum makes the kill rule strictly harder to satisfy and the support rule strictly easier, i.e. it is conservative against this study's own hypothesis.
3. **The H0 world needed calibrating, and the fallback was fixed before calibration.** Model G fitted to generations 1-6 alone sends the latent score so low at Hamming distance 13 that a simulated generation 8 holds no neutral variant at all and no metric exists. Rescaling all per-mutation terms cannot fix it. The H0 world therefore shrinks the terms of the mutations generation 8 actually uses by one factor k weighted by their generation-8 frequency, and shifts the intercept by a: `beta*_m = beta_m (1 - (1-k) min(1, f_m/f95))`. Two pins were declared in advance and **both are reported**: `pin16` sets a so the noise-free generation 1-6 neutral fraction equals the real one (which reaches a generation-8 fraction of only 0.051), and `pin8` sets k so the noise-free generation-8 fraction equals the published 0.28 (reaching 0.272, with generation 1-6 at 0.256). Only genotypes, one training marginal and one published marginal enter. The truth stays additive-latent through one curve with no interaction of any order.
4. **The network takes the best of 3 seeds** (D6) rather than a single fit, after a 3-replicate pilot showed the median-over-seeds AP was unstable enough to flip a verdict.

## Planted check (`t13_analysis.py planted`; run; simulated activities only)

10 replicates per scenario, run as three foreground parts and merged (`scripts_out/t13_planted.json`). Each replicate simulates generation 1-6, 7 and 8 activities from the real genotypes under the stated truth, adds measurement noise drawn by level from the real replicate-deviation bank, then runs the whole scoring path. Planted sizes were set by bisection against the pin8 world so the stated share of generation-8 calls flips (base scale 0.3449 for pairs, 1.7279 for triples). Pair effects are drawn N(0,1) on co-occurring pairs; triples add a third mutation at a fixed offset.

| Scenario | truth | false-kill | support rate | mean lift (min, max) | mean recall_G | mean AP_G | mean AP_net | mean AP_null | gen-8 neutral frac | verdicts | plan as written |
|---|---|---|---|---|---|---|---|---|---|---|---|
| null_global_curve_pin16 | pure curve | **0.70 (correct kill)** | 0.00 | -0.238 (-0.293, -0.167) | 0.820 | 0.909 | 0.671 | 0.092 | 0.050 | 7 kill / 3 partly / 0 support | 7 / 3 / 0 |
| null_global_curve_pin8 | pure curve | **1.00 (correct kill)** | 0.00 | -0.106 (-0.151, -0.076) | 0.918 | 0.976 | 0.870 | 0.341 | 0.265 | 10 / 0 / 0 | 10 / 0 / 0 |
| pairs_flip30 | + pairwise | 0.00 | **1.00** | 0.162 (0.108, 0.190) | 0.772 | 0.634 | 0.796 | 0.357 | 0.329 | 0 / 0 / 10 | 0 / 10 / 0 |
| third_order_flip30 | + 3rd order | 0.00 | 0.00 | 0.043 (0.011, 0.068) | 0.645 | 0.454 | 0.496 | 0.305 | 0.288 | 0 / 10 / 0 | 0 / 10 / 0 |
| pairs_flip15 | + pairwise, half size | 0.00 | 0.00 | 0.037 (-0.014, 0.075) | 0.770 | 0.756 | 0.792 | 0.330 | 0.274 | 0 / 10 / 0 | 0 / 10 / 0 |
| pairs_flip45 | + pairwise, 1.5x size | 0.00 | **1.00** | 0.230 (0.210, 0.265) | 0.836 | 0.598 | 0.829 | 0.380 | 0.366 | 0 / 0 / 10 | 0 / 10 / 0 |

What this establishes, and what it does not.

- **False-kill rate on a true interaction is 0/40.** No scenario with any planted interaction ever gave kill. A kill verdict on the real data would therefore be meaningful.
- **False-support rate on a pure global curve is 0/20.** Neither null ever gave support. A support verdict would therefore be meaningful.
- **Correct kill on a pure curve is 7/10 and 10/10.** The 3 misses in pin16 are "partly", never "support": there the simulated generation 8 has only a 5% neutral fraction, so AP is noisy. Under the pin that matches the published 0.28, kill is 10/10.
- **Pairwise interactions of the severity the plan asked for are detected (10/10).** Half that severity is not (0/10, lift 0.037): the test's floor sits between flipping 15% and 30% of calls.
- **Third-order interactions of the same severity are NOT detected.** 0/10 support, mean lift 0.043, even with the best of several network seeds. Neither the pair model nor the network learns them from 20,920 rows. This is a real and declared limit: a "partly" verdict on the real data cannot distinguish a mild global-curve failure from genuine third-order structure, which is precisely the structure the paper's own Walsh-Hadamard analysis points at ("only the 3rd order terms were required to achieve an accuracy similar to that of the current MLP model"). A kill or a support verdict is informative; a "partly" is not, and must be reported as such rather than argued either way.

Note on the merged output: the `scales` map records a bisected scale under the key `null_global_curve_pin16`. That entry is spurious (the null scenarios plant nothing; their `scale` is 0.0 in the rows, which is what is used). It is left as-is rather than changing the script hash and redoing every planted run.

## Dry run (`t13_analysis.py dryrun`; run)

The full `real` code path with the generation-7 and generation-8 labels permuted within Hamming-distance bins before anything is scored (`scripts_out/t13_dryrun_permuted_labels.json`).

- Verdict: **partly** (kill false, support false); `plan_as_written`: partly.
- Generation 8: recall_G 0.00060, AP_G 0.37848, AP_GP 0.34969, AP_net 0.30441, AP_null 0.37977, lift -0.02879, Spearman_G 0.20341. AP_G sits *at* the shuffled null, as it must when the labels carry no signal, and recall collapses to essentially zero.
- Generation 7: recall_G 0.70250, AP_G 0.78259, AP_null 0.78930, lift -0.01408 — again at the null, with the apparent recall explained entirely by the 0.762 permuted neutral fraction.
- Generation 1-6 held-out split (not permuted, so this is the pipeline check): AP_G 0.85315, AP_net 0.93158, AP_null 0.20073, recall_G 0.80218, Spearman_G 0.72928. The models do fit; the generation-7/8 numbers above are flat because the labels were destroyed, not because the code is broken.
- Fitted curve on the permuted run: lo 0.0146, hi 4.2625, b0 -1.0474, 467 pair terms.

So the pipeline neither invents a kill nor invents support from permuted labels.

## Reported only (no rule attached)

- The plan's rules as written, beside every verdict (`plan_as_written`).
- The shuffled-within-Hamming-bins null AP for every model on every generation.
- The replicate ceiling (AP 0.99730, rho 0.98329, recall 0.84525).
- Generation 7 (all three algorithms) and the generation 1-6 held-out split: same metrics, no rule.
- Spearman rho for G and GP everywhere.
- The authors' log-additive model's own recall and AP on generation 8.
- The fitted curve's lo, hi, b0 and the spread of the per-mutation terms.
- The number of qualifying pair terms.

## Ways it could be fooled, and limits

1. **Third-order structure is invisible to this test.** Shown above, 0/10 detection. If the real answer is "third-order interactions matter", this study returns "partly", not "support". It cannot be read as evidence against third-order epistasis.
2. **The detection floor sits above 15% of calls.** Pairwise interactions milder than that give "partly" too.
3. **The H0 world is calibrated, not observed.** It needs a shrink factor and an intercept shift to put any neutral variant in generation 8 at all. That the pure-curve world has to be bent this far to reach the published 0.28 is itself informative about how far generation 8 sits below generations 1-6, and it means the planted false-kill rates are rates *for that constructed world*, not for the real one. Both pins are reported for this reason.
4. **Generation 8 is not a random sample.** It is what the authors' own MLP selected, so it is enriched for whatever that MLP learned. A model that happens to resemble the MLP has an advantage on these rows that is about the selection, not about the landscape. This is why the rule leans on recall of *measured* neutral variants and on a bin-preserving null, and why generation 7 (selected differently) is reported beside it.
5. **Our network is not the authors' network.** Same architecture and labels, different framework, no sklearn or torch available. If our net underperforms theirs, lift is understated and the test tilts toward kill. The best-of-3-seeds rule is the partial guard; the generation 1-6 held-out AP of 0.93 is the sanity check.
6. **Model G's bounds are a choice.** Without them the fit diverges. Different bounds would give a different curve, though the asymptote bound only ever makes G's predictions *less* extreme.
7. **Shared measurement noise.** RA and its neutrality call come from the same two replicates. The ceiling (recall 0.845) is the honest upper bound on any model's recall; a model at 0.80 is near it.
8. **Reading a kill too broadly.** A kill says the authors' generation-8 inference does not require specific interactions, not that the landscape has none. Their own Walsh-Hadamard result stands independently.

## Sources actually opened

- Rotrattanadumrong & Yokobayashi 2022, Nat. Commun. 13:4847, PMC9385714 (full text, read line by line).
- The Zenodo deposit doi:10.5281/zenodo.6945203, members listed in "Inputs" (notebooks read as code cells only, via `scripts/nb_code.py`; no notebook outputs were read).
- Martí-Gómez et al. 2026 (MBE), PMC12911936; Faure & Lehner 2024 (PLoS Comput Biol), PMC11161127; Charest et al. 2023 (RNA), PMC10578471 — all full text.
- Europe PMC citations (27 records, every abstract), OpenCitations COCI (30 DOIs), Crossref (41 citing), plus 9 keyword searches, 4 arXiv queries and 2 Zenodo queries. All screened; see `experiments/t13_ligase_global_epistasis/PRIOR_ART.md`.
- In-repo precedent: `experiments/qt45_epistasis/RESULTS.md`.

Prior-art verdict: no one has fitted a global-epistasis model to this dataset, and no one has re-examined the generation-8 claim. The study is not redundant.

## Decisions to confirm at the seal

1. **Accept the two rule changes** (support on lift alone; lift from the better of GP and the net), or reinstate the plan's rules knowing they give support 0/10 in the scenario built to demand it.
2. **Accept the declared third-order blind spot**, or add a third-order term to GP before the seal (which would change the script hash and require redoing the planted check).
3. **Accept both H0 pins as reported**, or name one as primary.
4. **Confirm that the null floor and the replicate ceiling stay reported-only** rather than entering the rule, as the plan asked.
5. Add the line for `experiments/t13_ligase_global_epistasis/scripts/t13_analysis.py` with sha256 `f8d20c02c14a8aab32cb2c493bd00289eecc732a05b749e6d2aa344db874d9a7` to `docs/prereg/HASHES.txt`, then run `real`.

## Decisions confirmed at the seal

1. **The two rule changes** are accepted.
   - Support rests on lift alone. The plan's `recall_G < 0.50` arm reached support in 0 of 10 runs, even in the scenario built to demand it.
   - Lift is taken from the better of the pairwise model (GP) and the network.
   The plan's rules as written are computed and reported only.
2. **The third-order blind spot** is accepted and declared. Planted third-order structure that flips 30% of calls gave "partly" in every run, never "kill". A "partly" verdict cannot tell a mild failure of the curve from real third-order structure. A kill means no pairwise-sized structure that GP or the network can learn on these data. It does not mean there are no higher-order effects at all.
3. **Both null pins** (gen 1–6 and gen 8) shape only the planted null scenarios, not the real analysis. Both are kept as calibration evidence; neither is primary. The real analysis uses only the gen 1–6 fit.
4. **The null floor and the replicate ceiling** are reported only, not part of the rule.
5. **The spurious `scale` key** recorded under `null_global_curve_pin16` in the merged planted JSON is left as it is and noted. Nothing was planted in that scenario.
6. No other change. Any change after this seal makes the verdict invalid.
