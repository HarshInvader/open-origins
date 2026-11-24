# Pre-registration (T10): is LUCA's 4.2 Ga age set by the sequences, or by the 4.52 Ga maximum and the rate prior?

Status: DRAFT, written 2026-11-24 by the T10 prep agent. This is study S4 in `docs/plans/next_studies_2026-11-24.md`. Prior art is in `experiments/t10_luca_age_prior/PRIOR_ART.md`. MCMCtree has been built and timed. `planted`, `twins` (on 1% twin chains) and `dryrun` have been run. No full chain has been run. `real` refuses to run until `docs/prereg/HASHES.txt` names `experiments/t10_luca_age_prior/scripts/t10_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

**Feasibility first.** One posterior chain at the published length (20.1 million iterations) takes 28 to 42 CPU-days on this laptop under `taskpolicy -b`, and about 9 to 11 days on the authors' cluster. The full design as planned is 16 such chains. It does not fit the laptop or the $1 AWS cap. The compute plan below gives a reduced design and the decisions it needs.

## What has been seen (blinding disclosure)

The unknown is where the LUCA node (`t_n248`) goes in the posterior under P1, P2h and P2d. Nobody has run these.

- **Not seen.** No node age from any run with sequence data (`usedata = 2`). The three timing runs (R0 GBM for 14 minutes and 7 minutes, R0 ILN for 5 minutes) wrote `mcmc.txt` in `cache/runs/`. Their sample lines were counted, never parsed or printed. Their stdout is in `run.log` and was never printed. MCMCtree's progress lines carry running means of node ages.
- **One start value, by accident.** One `awk` over the first speed-test log printed `Initial 247): 4.455263`. This is a random start value drawn before any sampling, not a posterior.
- **The published logs.** For two published posterior logs and one prior log, I printed only the first and last token of the 1%, 50% and 100% progress lines, plus `Time used`. The 1% line's last token in each posterior log was a log-likelihood (−268.91 and −233.36). No node age was printed.
- **The prior, on purpose.** I ran four 1% prior-only twin chains (`usedata = 0`, strict clock, 201 samples each) to test the analysis code. Their LUCA summaries:
  - R0 twin: median 4.44 Ga, 95% interval 4.25 to 4.51.
  - P1 twin: median 5.88 Ga, 95% interval 5.65 to 5.98.
  - Both chain pairs show R-hat about 1.00 and ESS over 300. These are short chains, so the numbers are rough.
  - The prior is not the unknown. It is the null. But it shapes expectations (see "Ways it could be fooled", item 1).
- **The published results.** I know the partitioned intervals from the paper's text (GBM 4.18–4.33, ILN 4.09–4.32). I did not open the concatenated results (Supplementary Data 6, the repo's `sum_files_post/`) or the published prior summaries (`sum_files_prior/`).
- **What this does to my expectation.** Mahendrarajah 2023 found LUCA pressed against 4.52 on similar data. The prior here also sits near the maximum. I expect P1 to move LUCA up, which is the kill. I have not moved any threshold because of this.

## Claim under test

Moody et al. 2024, Nat. Ecol. Evol., doi:10.1038/s41559-024-02461-1 (PMC11383801), abstract, verbatim: "Here we infer that LUCA lived ~4.2 Ga (4.09–4.33 Ga) through divergence time analysis of pre-LUCA gene duplicates, calibrated using microbial fossils and isotope records under a new cross-bracing implementation."

The two inputs in question, verbatim:

- The maximum: "We used soft-uniform bounds, with the maximum-age bound based on the time of the Moon-forming impact (4,510 million years ago (Ma) ± 10 Myr)". The files use hard bounds: `Calibnodes.csv` gives `LUCA; B{3.3470,4.5200,1e-300,1e-300}` and `ROOT; U(4.520,1e-300)`.
- The rate prior: "Γ(2, 2.5) ... meant to account for the uncertainty on our estimate for the mean evolutionary rate, ~0.81 substitutions per site per time unit, which we calculated by dividing the tree height of our best-scoring ML tree ... into the estimated mean root age of our phylogeny (that is, 4.520 Ga ...)".

**H1 (data-driven).** The sequences place LUCA near 4.2 Ga. Moving the maximum or the rate-prior mean leaves the date close to where it was.

**H0 (prior-driven).** The date follows the maximum or the rate prior.

## Inputs (exact)

From `https://github.com/sabifo4/LUCA-divtimes` (GPL-3.0) at commit `a2bf515fe3dddfc006b6d19e5444259857c62557`. Paths were taken from the GitHub API tree (8,544 entries, not truncated). Each file is saved in `experiments/t10_luca_age_prior/raw/`, with `/` in the repo path replaced by `__`. All of `raw/` and `cache/` is gitignored and treated as untrusted. Every download used User-Agent `open-research-site/1.0`.

| Repo path | Use | sha256 |
|---|---|---|
| `01_PAML/00_CODEML/out_CODEML/Hessian/1/in.BV` | branch lengths, gradient, Hessian (concatenated dataset) | 551789b8986c5ea4f909e0d9d56585a77cdd2289b714fdbd159ca2757a8cf672 |
| `00_data_formatting/01_inp_data/LUCAdup_246sp_allcb_calib_MCMCtree.tree` | calibrated tree, cross-bracing A | 825e294e14bb31a35bfad914f6bc945275e0d9747b64b88fe25f79717a108009 |
| `01_PAML/02_MCMCtree/calib_files/Calibnodes.csv` | calibration list, checked against the tree | 9c42775d23c37db2fe8a2842f5c1bc7a14f1660e25faeccb4c252247b2a92e25 |
| `01_PAML/02_MCMCtree/dummy_aln/dummy_aln.aln` | `seqfile` (taxon names only; the likelihood comes from `in.BV`) | 281865574bb3d1cc45b94f14509c32cad577c843b5f571fb75b8acc2e083b3ed |
| `01_PAML/02_MCMCtree/dummy_ctl_files/mcmctree_dummy.ctl` | the authors' control template | 9f29cfcfb260304761cf5fbe83ad2cd146d79d35761d10d13ad6e7d0e73f7c42 |
| `01_PAML/02_MCMCtree/sum_analyses/01_posterior/GBM/1/mcmctree_1_r1.ctl` | the control file actually run, GBM | a6368df4b6ee373da317c2c9065d4c7eba55393363b9cba4a4ce814715c80db4 |
| `01_PAML/02_MCMCtree/sum_analyses/01_posterior/ILN/1/mcmctree_1_r1.ctl` | the same, ILN (differs only in `clock`) | b94eccfe1646d4517e8f9741b9b789bfda8e4220a4c4db98ab2914516eb191e3 |
| `01_PAML/02_MCMCtree/sum_analyses/pipelines_MCMCtree/GBM/pipeline_GBM.sh` | how they ran it (16 chains, 240 h limit) | 27dceed817116eee4efe4d34bc7b7752af782770b427633cfb3cdabeec420e6a |
| `01_PAML/02_MCMCtree/scripts/pipeline_MCMCtree_template.sh` | template of the above | fea36ae8d1273a393faf6fb15fa0e21e093954301e989d293cb4680a4b603c08 |
| `01_PAML/02_MCMCtree/scripts/generate_job_MCMCtree.sh` | job generator | 918804bbf465ce33c3d030dce7ebbb030b5acda6e53b3e6812d7e76797eb4214 |
| `01_PAML/00_CODEML/out_CODEML/Hessian/1/tmp0001.ctl` | CODEML settings behind `in.BV` | daa021295bab3248e0c6695557dc4b1ff2bf0400da85e4067497d740983aff7a |
| `00_data_formatting/scripts/Calib_converter_allcb.txt` | calibration-to-node map | 323da538d6d786c9cf98861516575053d517aad9c22725f6130b1452a83b0f97 |
| `00_data_formatting/scripts/Include_calibrations_allcb.R` | how the tree was calibrated (read only) | 4c9097a91562ebb75b9c95f184a83013cc46b50a70a84c879cb9ed43e96be81c |
| `LICENSE` | GPL-3.0 text | 2e8578f16b6ea265412166e8b4b1da045fcc11f28db03d664908410124a2f01e |

The published control file, as run: `usedata = 2`, `clock = 3` (GBM) or `2` (ILN), `model = 3`, `alpha = 0.5`, `ncatG = 4`, `BDparas = 1 1 0.1`, `rgene_gamma = 2 2.5`, `sigma2_gamma = 1 10`, `print = 1`, `burnin = 100000`, `sampfreq = 1000`, `nsample = 20000`, `duplication = 1`, `seed = -1`. The authors ran 16 chains per clock model.

The tree has four 4.520 maxima: the root `U(4.520,1e-300)`, LUCA `[#1 B{3.347,4.520,1e-300,1e-300}]`, TG-OXYPHOTOBACTERIA `[#10 B{2.945,4.520,...}]` and TG-EUKARYA-MITO `[#8 B{1.08557,4.520,0.025,1e-300}]`.

## Software

- PAML 4.10.7 source from `https://codeload.github.com/abacus-gene/paml/tar.gz/refs/tags/4.10.7` (tag object 59cb8ef8…). Tarball sha256 `0f29e768b3797b69eadc6332c3d046d8727702052d56c3b729883626c0a5a4e3`. Unpacked in `experiments/t10_luca_age_prior/cache/paml/`.
- Built with Apple clang 21.0.0 through the source Makefile: `make mcmctree CFLAGS="-O3 -Wall -Wno-unused-result -Wmemset-elt-size -D_FORTIFY_SOURCE=0"`. This is the Makefile's own CFLAGS plus `-D_FORTIFY_SOURCE=0`. No sudo and no Homebrew.
- **Why fortify is off.** The plain `make` binary aborts with SIGTRAP in `__chk_fail_overlap` while reading the tree. A debug build traced it to `treesub.c` `copy_to_Sptree`, `strcpy(stree->nodes[j].name, com.spname[j])`, where source and destination are the same buffer. That is a self-copy and changes nothing, so turning the check off is safe. The R0 gate is the check that our build matches the authors' Linux build.
- `mcmctree` binary sha256 `15244a2a3e40a804a36c8b85d430e0f1c9de0253632b955434351bdcc07f2ae6`.

## Runs

All runs use the concatenated dataset with cross-bracing A, `usedata = 2` with `in.BV`, and otherwise the published control file. `experiments/t10_luca_age_prior/scripts/make_run.py` writes each run directory.

| Run | Change from the published settings |
|---|---|
| R0 | none |
| P1 | root `U(4.520)` to `U(6.0)` and LUCA `B{3.347,4.520,...}` to `B{3.347,6.0,...}`. Unphysical on purpose: it asks what the sequences say. The other two 4.520 maxima stay (decision D3). |
| P2h | rate-prior mean halved: `rgene_gamma = 2 5` (mean 0.4 against 0.8) |
| P2d | rate-prior mean doubled: `rgene_gamma = 2 1.25` (mean 1.6) |

Each runs under GBM (`clock = 3`) and ILN (`clock = 2`), with 2 chains each. The seeds are fixed at `1000 + 97 × chain`. The authors used `seed = -1`.

**Twins (no sequence data).** `usedata = 0`, `clock = 1`, as the authors did for their own prior check. Without data, MCMCtree's prior on times does not involve the rates or the clock model. So two twins cover all eight posterior runs: the R0 twin serves R0, P2h and P2d under both clocks, and the P1 twin serves P1. The plan asked for one twin per run. This gives the same prior for far less compute. Each twin has 2 chains at full length, about 40 to 100 minutes each on the laptop.

## Fixed decisions (draft; owner to confirm D1 to D5)

- **D1, gate reference.** The published 95% interval for LUCA from the concatenated dataset with cross-bracing A, under each clock, to be read from Supplementary Data 6 or `sum_files_post/LUCAdup_{GBM,ILN}_all_mean_est.tsv` before the seal. It is not the abstract's 4.09–4.33, which is partitioned. `PUB_CONCAT` in the script is empty, and `real` returns "void" until it is filled.
- **D2, window.** The window used in the kill and support rules is the claim's 4.09–4.33 Ga, under both clocks.
- **D3, P1 scope.** P1 raises only the root and LUCA maxima, as the plan says. The variant that raises all four 4.520 maxima (`make_run.py --p1-scope all`) is reported only, if it is run at all.
- **D4, P2 kill.** For a given clock, P2 counts against the claim if either arm leaves the window in its own direction: P2h median above 4.33 or P2d median below 4.09.
- **D5, chain length.** To be set from the compute plan. The published length is 20.1 million iterations. The reduced design uses `burnin = 100000`, `sampfreq = 100`, `nsample = 19000` (2.0 million iterations). Whatever the length, the convergence rule below decides whether a run counts.
- **D6, the statistic.** The LUCA node is `t_n248` (driver; `t_n368` is the mirror). Pool both chains. Report the median and the 2.5% and 97.5% quantiles.
- **D7, convergence.** A run counts only if, for `t_n248`, the rank-normalised split R-hat is at most 1.05, the pooled bulk-ESS is at least 200, the tail-ESS (2.5% and 97.5% quantiles) is at least 100, and the two chain medians agree within 0.02 Ga. The R-hat and ESS thresholds are Moody's. The bulk-ESS of 200 and the 0.02 Ga agreement are added here. A run that fails is extended (more samples, same settings), not changed. A run still failing after extension gives "undecided".
- **D8, order.** Twins, then P1 under both clocks (the kill test), then R0 (the gate), then P2 if needed. Then seal, then `real`. All of these runs must exist before `real`, because `real` checks the gate before it gives any verdict.

## Gate

R0's 2.5% and 97.5% quantiles for LUCA must each lie within 0.05 Ga of the published concatenated cross-bracing A values (D1), under both clocks. If either clock fails, the verdict is "void": our build or inputs do not reproduce the paper, and P1 and P2 mean nothing.

## Decision rules (from the plan; D2 and D4 make them exact)

- **Kill.** The claim fails as a data-driven date if either holds under both clock models:
  - under P1, the posterior median is above 4.52 Ga;
  - under P2, P2h's median is above 4.33 Ga or P2d's median is below 4.09 Ga.
- **Support.** Under both clocks:
  - P1's median is at or below 4.52 Ga, and its 95% interval overlaps 4.09–4.33;
  - P2h's and P2d's medians are both inside 4.09–4.33.
- **Otherwise.** "Partly", for example a kill under one clock only.
- **Void.** The gate fails or `PUB_CONCAT` is empty. **Undecided.** Some run fails convergence after extension.

## Null and information gain

The twins give the prior on LUCA from the same sampler and calibrations. Any gap between a run and its twin comes from the sequences. Reported for every run: information gain 1 − (posterior width ÷ prior width), with width the 95% interval.

Also reported, with no rule attached:

- **Prior-following ratio for P1:** (P1 posterior median − R0 posterior median) ÷ (P1 prior median − R0 prior median). A value near 1 means the date moves with the maximum as the prior does. A value near 0 means the sequences hold it in place.
- The share of LUCA samples above 4.52 under P1.
- The root node (`t_n247`) under each run.

## Planted check and dry run (run)

- **`planted`** (`scripts_out/t10_planted.json`). Synthetic AR(1) chain pairs (φ = 0.9, 4,000 draws each) with set medians, through the real convergence and verdict code. Each case gave the expected verdict:
  - support: support;
  - P1 above 4.52 under both clocks: kill;
  - P2h above 4.33 under both clocks: kill;
  - P1 above 4.52 under one clock only: partly;
  - one P1 chain shifted by 0.15 Ga: undecided, because convergence fails.
- **`dryrun`** (`scripts_out/t10_dryrun_twins_as_posterior.json`). The full `real` code with every posterior run replaced by its prior twin (1% twin chains). This is the "sequences carry no information" case. It ran without error. Information gain was 0 everywhere and the verdict was **kill**, as it should be: with no data, LUCA follows the maximum (P1 twin median 5.88) and sits above the window (R0 twin median 4.44).
- **`real`** refused, as it should without a seal.

## Ways it could be fooled, and limits

1. **The prior already sits near the maximum.** The R0 twin puts LUCA at 4.25–4.51, and the P1 twin at 5.65–5.98. So under P1, the sequences must pull LUCA down about 1.4 Ga for support. A P1 kill says the 4.2 date needs the 4.52 bound. It does not say the sequences carry no information. The information gain and the prior-following ratio separate the two cases.
2. **The published posterior is already younger than the prior.** The paper's partitioned 4.09–4.33 lies below the R0 twin's 4.25–4.51, so the sequences already pull LUCA younger under R0. This is a reason the test is not settled in advance.
3. **The approximate likelihood.** `in.BV` is a normal approximation around the ML branch lengths. Moving the maximum changes times and rates, not branch lengths. The approximation is used the same way in every run.
4. **Chains too short.** The reduced chains are a tenth of the published length. D7 decides whether they count. Tail-ESS matters most, because the P1 question is about the upper tail.
5. **Our build is not the authors' build.** Clang against gcc, fortify off, macOS against Linux. The R0 gate catches a difference that matters.
6. **Only the concatenated dataset.** The headline numbers are partitioned. A kill on concatenated data carries over only if the partitioned analysis behaves alike. Moody reports the two as similar (Extended Data Fig. 1), but this study does not test that.
7. **Two maxima stay at 4.52 under P1.** TG-OXYPHOTOBACTERIA and TG-EUKARYA-MITO keep their maxima. They are descendants of LUCA, so they do not cap it, but they constrain rates. The `--p1-scope all` variant is the check, if it is run.
8. **6.0 Ga is arbitrary.** A different value moves the P1 prior. The rule asks only whether the median passes 4.52, and that question does not depend on the exact value once it is well above 4.52.
9. **The rate prior acts only through the data.** P2 can only change LUCA through the likelihood. If P2 moves LUCA, the sequences do not pin the rate. That is the point of P2.
10. **Soft or hard bounds.** The text says soft, the files say hard. We follow the files, as the authors' runs did.
11. **One node.** The rules use LUCA alone. LECA and the other calibrated nodes are not tested.

## Compute plan

Measured on this laptop under `taskpolicy -b nice -n 20`, single-threaded, while other jobs loaded the machine (load average 8 to 97). The posterior rates come from short runs of 760 to 790 iterations. A 1% chain (201,000 iterations) would have taken 21 to 29 hours, so it was not run. Details are in `experiments/t10_luca_age_prior/scripts_out/t10_timing_summary.json`.

| Run type | CPU s per 1,000 iterations | Wall s per 1,000 | One chain at the published length (20.1 million iterations) |
|---|---|---|---|
| R0 GBM, `usedata = 2` | 182 | 521 | 42 CPU-days, about 121 wall-days |
| R0 ILN, `usedata = 2` | 120 | 383 | 28 CPU-days, about 89 wall-days |
| Twin, `usedata = 0`, `clock = 1` | 0.11 | 0.13 to 0.30 | 37 CPU-minutes, 45 to 100 wall-minutes |
| Authors' cluster, ILN (their log) | 39 | 39 | 217.7 hours |
| Authors' cluster, GBM (their log) | about 46 | about 46 | 50% at 129.5 hours; the log shows no finish within the 240 h limit |

Under background priority the laptop is 3 to 4 times slower per CPU-second than the authors' cluster, and gets about a third of a core.

**The full set as planned** is R0, P1, P2h and P2d, each under 2 clocks with 2 chains: 16 posterior chains, plus twins.

- Laptop, one chain at a time under the lock: about 1,700 wall-days.
- At cluster speed: about 3,800 core-hours.
- On AWS spot, at roughly $0.01–0.02 per vCPU-hour (not checked today): $40–75.

It does not fit.

**Can the laptop do it overnight?** Only the twins: 4 chains of 1 to 2 hours each. One reduced posterior chain (2.0 million iterations) takes about 9 days (ILN) or 12 days (GBM) of wall time under `taskpolicy -b`.

**Cutting runs.**

- The twins are the cheap part. Two instead of eight, as explained under "Runs".
- Kill test first: P1 under GBM and ILN, 2 chains each (4 chains). If P1 kills under both clocks, P2 is not needed for the kill. R0 is still needed for the gate.
- Reduced chain length (D5): 2.0 million iterations instead of 20.1 million, with D7 deciding whether the chains have converged.
- The minimum for a kill verdict is P1 and R0 under 2 clocks with 2 chains: 8 chains. At reduced length that is about 190 core-hours at cluster speed. A support verdict needs all 16 chains, about 380 core-hours.
- A cheaper gate would cut R0. One option: run our binary and the official 4.10.7 macOS binary from the same seed for 1,000 iterations and check that `mcmc.txt` is byte-identical, which compares without reading. That validates the build but not convergence. The other: compare our full twin with the published prior summary. With both, the kill test is 4 chains, about 95 core-hours.

**AWS at a $1 cap.** About 95 core-hours at $0.01–0.02 is $1–2, so even the 4-chain kill test does not fit. One P1 pair under ILN alone, about 43 core-hours or $0.45–0.90, would fit, but it decides nothing, because the kill needs both clocks.

**A route not measured.** The laptop at normal priority, outside `taskpolicy -b`, on a performance core. If that runs near cluster speed (unmeasured; a 5-minute timing run would tell), the 4-chain kill test takes about two days with 2 chains at a time. That means holding 2 cores while another job holds the compute lock.

**Verdict.** As planned, the study is not feasible this month. The cheapest decisive set is the two twins (laptop, one night), then P1 under GBM and ILN with 2 chains each at 2.0 million iterations, then the R0 gate. It needs either normal-priority laptop cores for several days or roughly $2–4 of AWS spot.

## Decisions for the owner

1. **D1.** Gate against the concatenated published interval, which means opening Supplementary Data 6 or `sum_files_post`. The alternative is to switch R0 to the partitioned dataset (five `in.BV` blocks), which is slower and needs files the plan did not list.
2. **D3.** P1 raises only the root and LUCA maxima (the plan), or all four 4.520 maxima.
3. **D4.** A P2 kill needs one arm (draft) or both.
4. **D5 and the route.** Reduced chains plus one of three routes: normal-priority laptop cores, an AWS cap of about $2–4, or parking S4 until compute allows.
5. **The gate.** Full R0 chains, or the cheap byte-identical check plus the prior comparison.

## Scripts and outputs (sha256 at the time of writing)

| File | sha256 |
|---|---|
| `experiments/t10_luca_age_prior/scripts/make_run.py` | 7b53bc5244e35d38a010e9a04bb3170392a93de1186cf2cfc29f6955ddd94f8c |
| `experiments/t10_luca_age_prior/scripts/time_run.py` | 830d64bce0504ab3126352c6e703214144662a8551f0c37364e526a2160d5538 |
| `experiments/t10_luca_age_prior/scripts/t10_analysis.py` | f166002f4e27c15056bd7367caf0700aad568000e2df734a23d64839494d1817 |
| `experiments/t10_luca_age_prior/scripts/xml2txt.py` | 9ee910dc15d0a69c0b5a8fb915d5d72f790afc082f233d54f7c96941e8625982 |
| `experiments/t10_luca_age_prior/scripts_out/t10_planted.json` | ea0a9885597e9c2b34f7c058ccab11a38569f781e4bd3d42ec7a662e5a082e7e |
| `experiments/t10_luca_age_prior/scripts_out/t10_dryrun_twins_as_posterior.json` | 3c501708ef9830d1333607f9a42d4e9eff83cab51560ab2b6cb0308d8dc98dbc |
| `experiments/t10_luca_age_prior/scripts_out/t10_timing_summary.json` | 1dfbca9ff767fa21e50af978bae81cab4397181bbabd3797e3c0b1517ae683a1 |
