# Pre-registration (T8): is the growth-versus-variation trade-off in RNA networks more than droplet noise?

Status: DRAFT, written 2026-11-25 by the T8 prep agent. This is study S3 in `docs/plans/next_studies_2026-11-24.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run, and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t8_ameta_noise/scripts/t8_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is the pairing of each network's yield with the perturbations that start from it, after noise is taken out. Every deciding number comes from that pairing.

- **Not computed.** No real correlation between yield and perturbation, raw or adjusted, on any set of pairs. No real correlation between yield and either noise measure.
- **One joint look, taken on purpose: the paper's own test.** `gate` reproduces the Fisher test of Fig. 2d on the paper's 162 pairs. It printed one 2×2 table: 1 pair high-yield and strongly perturbed, 52 low-yield and strongly perturbed, 20 high-yield and not strongly perturbed, 89 neither. Of those 162 pairs, 41 are in the 1,093 pairs this study tests. So a two-by-two summary of 41 of the 1,093 pairs has been seen. Nothing finer was printed.
- **Real perturbations and real noise, without yield.** `dryrun` uses the real fractions with yield permuted over networks. It shows marginals that involve no real yield:
  - median perturbation 0.135;
  - median noise floor 0.087;
  - in 27% of pairs the perturbation is below the noise floor;
  - the size-stratified Spearman correlation between perturbation and noise is 0.54 with the floor and 0.41 with the split-half noise.
  Every number in the dry-run output that involves yield is synthetic.
- **Structure and the yield–UMI link.** I saw counts of networks, droplets, pairs and replicates; the droplet UMI totals; and that network fractions equal the mean of droplet fractions. The planted check uses the real yields and the real UMI totals together, so it carries the real link between them. That link is built into the method: a droplet's yield is computed from its UMI counts.
- **Pilot planted runs.** Before the size strata were added, a 1-replicate and a 3-replicate planted run were made. They are synthetic. They showed that noise and yield both rise with network size. That is why the strata were added (D4).
- **The paper's Fig. 2d image was not viewed.** In the authors' notebooks I read the code cells only, not the saved outputs.
- **What this does to my expectation.** I have none on the sign. The planted check shows that noise alone, given the real UMI totals, makes a size-stratified Spearman correlation of about −0.11 to −0.22 between yield and perturbation. So a raw trade-off of that size would carry no information. The thresholds −0.20 and −0.05 come from the plan and have not moved. The form of the rule changed in two ways (see "Changes from the plan").

## Claim under test

Ameta et al. 2021, Nat. Commun. 12:842, doi:10.1038/s41467-021-21000-1 (PMC7870898, read from `experiments/t8_ameta_noise/raw/europepmc/PMC7870898_fulltext.xml`; excerpts in `raw/europepmc/PMC7870898_definitions_excerpt.txt`).

- Results, verbatim: "Furthermore, we observed that high-yield networks tend to display small perturbation values, implying a trade-off between growth and variation (Fig. 2d, Supplementary Fig. 6e)."
- Definition of perturbation, verbatim (Results; the absolute-value bars are lost in the XML text): "Denoting V the set of species common to G and G′, we define the network perturbation as pG→G′ = ∑v∈V |y′v − yv| where yv and y′v are the respective fractions of species v in G and G′, both normalized within V (Fig. 2b). By definition, the maximum is pG→G′ = 2 and is reached for a full switch in species composition".
- Fig. 2d caption, verbatim: "Perturbation pG→G′ for networks with 3, 4, and 5 species plotted against network yield in µM for perturbations involving the addition of a novel catalysts (with G/C as IGS) with at least one target. The number of strongly perturbable (pG→G′ > 0.8, above the green dotted line) and high-yield networks (>0.08 µM, right hand side of red dotted line) is very low compared to the null hypothesis of independence between the two properties (one-sided Fisher exact test, N = 162, odds ratio <0.1, 95% confidence interval 0.01–0.66, p-value = 1.6 × 10−3)."
- Yield, Methods, verbatim: "To determine network yield per droplet, first we computed a droplet-specific UMI to concentration conversion rate by considering total hairpin reporter UMIs as well as number of different hairpin reporters identified. This was then used to convert total number of ribozyme UMIs into a yield value."
- Droplet filter, Methods, verbatim: "only the droplet barcodes with more than 10 UMIs associated with hairpin RNA reporters and 20 with ribozymes were retained and the fraction of each species in the network was computed."

The Methods section has no further definition of perturbation. The definition above is from Results, and the authors' code (`utils/az_tools.py`, `compute_pscore` and `collapse_postprocess`) matches it: each network's fractions are averaged over its droplets, then renormalised within V.

**Why it might be an artefact.** A droplet's yield is its ribozyme UMI count scaled by its reporter UMIs. A low-yield droplet has fewer ribozyme UMIs, so its fractions are noisier, and noise alone raises the L1 distance between two networks' mean fractions.

**H1.** High-yield networks change their composition less when a species is added, beyond what measurement noise explains.

**H0.** Once noise is accounted for, the change in composition does not depend on yield.

## Inputs (exact)

Paths are under `experiments/t8_ameta_noise/`. Downloads used User-Agent `open-research-site/1.0` and carried no personal details. Python reads every downloaded file with `-I`, and scripts live in `scripts/`. `raw/` and `cache/` are gitignored, because the data are third-party.

| File | Source | sha256 |
|---|---|---|
| `raw/esm/41467_2021_21000_MOESM4_ESM.xlsx` | Supplementary Data 2, 1,789,073 bytes | 343f1c7014d70bc3dbb41d749aa2988ba43968829bc203d9118a8f41d1067278 |
| `cache/sd2/sheet1.tsv` | sheet "Networks (experimental data)", written by `scripts/xlsx_to_tsv.py` | edad2c8763ebdfb13fb21df9140b17128c5eb1477e82cbe6bb59df57c935ceb9 |
| `cache/sd2/sheet3.tsv` | sheet "Droplets (node fractions)" | f0704a9eebf3616d59458ef85de1dbf5aa58fce3e70f7998bf9d8e3fc76d26a8 |
| `cache/sd2/sheet4.tsv` | sheet "Droplets (number of UMIs)" | fd11539a592dd6c3660218d60df2df9bb5305020f6ad2fa06dc00dafd11676ea |
| `raw/esm/41467_2021_21000_MOESM1_ESM.pdf` | Supplementary Information | 4f6557e1b2a935941b975bbf7b7e462f73cbeee5322db7dd656dd214a60d71a2 |
| `raw/europepmc/PMC7870898_fulltext.xml` | Europe PMC full text | 6e58890e8fc07daf60195e7d18edbfc619170e37464a27698599186f4f107f6b |
| `raw/europepmc/PMC7870898_definitions_excerpt.txt` | verbatim excerpts of the definitions, from the XML | 18b0c85ab03e27344678f19beb915aba6cd88d5a9dec38f11ab5d7855c66d7d4 |
| `raw/github/` | authors' code, `smnars/azoarcus_networks` at 76cd71e (the code behind doi:10.5281/zenodo.4016905): `analysis/figures.ipynb`, `analysis/supplementary_figures.ipynb`, `utils/az_tools.py`, `utils/az_model.py`; read, never run | figures.ipynb 9ca8fd33…, az_tools.py 8f3f5f54…, az_model.py 739ba38f…, supplementary_figures.ipynb f0ded173… |
| `scripts/xlsx_to_tsv.py` | this study; stdlib only, reads the xlsx through `zipfile` | 150ac0748723c999c2585b24578eea8347151623fbafe55f32847f9f22f8d551 |
| `scripts/t8_analysis.py` | this study | 18ffe6a283b2da6af11e62eac39b5595aedd82fbecfde85bfd1ef924f7d84d0e |
| `scripts_out/t8_gate.json` | `gate` output | fca877dd9fbc74e09ddfe3c182804cb354d720a3d72212b3fa1201a82753ead0 |
| `scripts_out/t8_planted.json` | `planted` output | 38a6606fda7a45308a589d7f92983a4b8234f02684620d1ccf495a7cdf6301d5 |
| `scripts_out/t8_dryrun_permuted_yield.json` | `dryrun` output | 545e67df2b346bc28776edd2a73c401cccf0b73b6fb3993d299f1347d7ceb21e |

- `t8_analysis.py` checks the sha256 of the xlsx and the three TSVs, and stops on a mismatch.
- The figshare raw data (doi:10.6084/m9.figshare.c.5103962) and the 69 MB Zenodo zip were not downloaded. Supplementary Data 2 holds every droplet's fractions and UMI counts, which is all the test needs.
- Python: `experiments/t1_vent_exergonic/.venv` (numpy 2.5.5, scipy 1.18.1), run under `nice -n 20` with one thread.

## Gate (`t8_analysis.py gate`; run; passed)

| Check | Result |
|---|---|
| Networks; droplets | 1,837; 20,039 |
| Droplets whose filled cells match exactly one network | 20,039 of 20,039 |
| Fraction and UMI sheets have the same filled cells | yes |
| Networks whose droplet count equals the sheet's "Number of replicates" | 1,836 of 1,837. The exception (AC AG CA CC CU UU UG GU) has 3 droplets and is listed with 2 |
| Droplets appear in network blocks | 1,838 runs for 1,837 networks; one network is split in two runs |
| Network fraction = mean of its droplets' fractions | 99.94% of cells within 1e-4 (the sheet rounds to 4 decimals); worst 0.042, in the network above |
| Droplet fraction = UMI share | worst difference 5e-5 (rounding) |
| Ribozyme UMIs per droplet | min 20, 10th percentile 30, median 110, 90th 542, max 16,931 |
| Fig. 2d subset rebuilt from the authors' code | **162 pairs** (82 distinct G) |
| 2×2 table [[high p and high yield, high p and low yield], [low p and high yield, low p and low yield]] | [[1, 52], [20, 89]] |
| Odds ratio | 0.086 (sample); 0.086 (conditional MLE) |
| 95% interval | Woolf 0.011–0.656, the paper's "0.01–0.66"; the exact conditional interval is 0.002–0.57 |
| One-sided Fisher p | 1.62 × 10⁻³ |

The same table comes out from the sheet's rounded network fractions and from the droplet means.

**How a droplet's network is read.** A droplet's network is the set of species whose cells are filled. A blank cell means the species was not supplied. A 0 means it was supplied and no UMI was seen (11,993 such cells). This matches the Methods: a network is identified from its hairpin reporters, not from the ribozymes detected.

**How the Fig. 2d subset is defined** (authors' `figures.ipynb` cell 36, `az_tools.is_catalytic_innovation`):
- G has 3, 4 or 5 species;
- the added species a has G or C as its IGS (first letter of the species name);
- no species of G shares a's IGS (m = 0);
- exactly one species of G has the tag that base-pairs with a's IGS (n = 1);
- the yield is that of G, and networks with one droplet are kept.

The caption's "at least one target" is "exactly one" in the code. With "at least one", N is 181.

**What the plan had wrong.**
- The plan counted 1,834 distinct networks and 4,549 pairs. The data have 1,837 networks and 4,589 pairs (4,534 with G of two or more species).
- The plan's 1,115 pairs with at least 5 replicates included G of one species, where p is 0 by definition. Without those there are 1,093 pairs; with them, 1,118. The plan's floor of 111 pairs per size matches size 6 here.
- The paper's 162 pairs are mostly networks with one or two droplets. Only 41 of them have 5 or more droplets on both sides. No noise can be estimated from a single droplet, so this study cannot test the 162 pairs themselves. It tests every single-species addition with enough droplets (D2). The Fig. 2d subset is reported only.

## Blind decidability counts (structure only)

Pairs with at least 5 droplets on both sides and G of at least two species, by the size of G: 131 (2 species), 232 (3), 161 (4), 166 (5), 111 (6), 44 (7), 19 (8), 37 (9), 33 (10), 43 (11), 50 (12), 37 (13), 23 (14), 6 (15). That is 1,093 pairs from 386 distinct G.

## Fixed decisions

- **D1, perturbation.** p(G→G′) = Σv∈V |m′v − mv|, where m and m′ are the mean droplet fractions of G and G′, each renormalised within V = the species of G. If a mean is all zero on V it becomes uniform (the authors' `norm_array`). Yield is the network yield of G in µM from Supplementary Data 2.
- **D2, pairs.** All (G, G′) with G′ = G plus one species, both networks present, G of 2 or more species, and 5 or more droplets in each network: 1,093 pairs.
- **D3, noise (primary): split-half, as in the plan.** For each G, split its droplets at random into two halves (sizes ⌊n/2⌋ and the rest), take the L1 distance between the two half means, and average over 200 random splits. No species is added. Every pair from the same G gets the same value.
- **D4, size strata.** All correlations are Spearman correlations within strata of the size of G: 2, 3, 4, 5, 6, 7–8, 9–11 and 12–15 species. Each value is turned into a rank score within its stratum, (rank − 0.5)/n − 0.5, and the Pearson correlation of those scores is the size-stratified Spearman.
- **D5, second noise measure (reported, and used in the robustness rules only).** The noise floor of a pair is the bootstrap expectation, with 200 draws of each network's droplets, of Σv∈V |(m*′ − m′) − (m* − m)|, all renormalised within V. It uses the droplets of both G and G′ at their real counts.
- **D6, adjusted correlation (K-b).** The partial size-stratified Spearman correlation between yield and p given the noise: (r_yp − r_yz·r_pz) / √((1 − r_yz²)(1 − r_pz²)).
- **D7, interval.** Resample the 386 G networks with replacement, 4,000 times. A pair is weighted by the number of times its G is drawn. Correlations are recomputed on the fixed rank scores with those weights. The interval is the 2.5th to 97.5th percentile.
- **D8, seed.** 20261125. Generators: `[seed, 2]` planted, `[seed, 3]` real, `[seed, 4]` dryrun. `gate` uses no random numbers.
- **D9, primary rule.** `noabs_split` in the script.
- **D10, order of runs.** `gate`, `planted`, `dryrun`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with the script's current sha256.

## Decision rules (primary, `noabs_split`)

Let r_yp be the size-stratified Spearman correlation between yield and p (K-a), r_yz the same between yield and the split-half noise, and r_B the partial correlation (K-b) with its interval [lo, hi].

- **Kill.** hi ≥ 0 (the interval includes 0 or lies above it), or r_yz ≤ r_yp (yield relates to noise at least as negatively as it relates to perturbation).
- **Support.** Not a kill, r_B ≤ −0.20 and hi < −0.05.
- **Otherwise: "partly".** Something beyond noise, but weaker than −0.20 or with an upper bound between −0.05 and 0.

## Changes from the plan, made before the seal

The plan's rule was: K-a and K-b as above but pooled over all sizes. Kill if the K-b interval includes 0 or if the yield–noise correlation is as strong as the yield–perturbation correlation. Support at an adjusted correlation of −0.2 or stronger, with the interval excluding −0.05, and the same holding when perturbation is computed on absolute concentrations (fraction × yield). The thresholds, the noise measure and both kill clauses are unchanged. Two things changed.

1. **The absolute-concentration condition is now reported only.** Absolute perturbation, Σ|Y′·m′ − Y·m|, grows with yield by construction, because every concentration is a fraction times yield. In the planted check it rises with yield even under the strongest planted trade-off: its mean adjusted correlation is −0.03 to −0.10 for true trade-offs of −0.42 to −0.44, and +0.18 to +0.32 under the nulls. With that condition, support was reached in 0 of 1,500 planted runs, including runs whose true correlation was −0.44 (column "plan as written"). The rule could only kill or say "partly". It is still computed and reported.
2. **Correlations are taken within network-size strata.** The paper says yield "varied 10-fold across networks comprising between 2 and 15 catalytic species (see Supplementary Table 2)". Both p and the noise are sums over the species of G, so they change with size too. In the 1-replicate pilot planted run with pooled sizes, the noise correlated positively with yield in every row I printed (+0.38 to +0.44). Within size strata the same quantity was negative under the nulls. The size effect would dominate a pooled correlation. The pooled version is reported only.

The plan's split-half noise was kept as the primary. The two-sided noise floor (D5) was calibrated as well. It performs about the same (table), but it calls "partly" in up to 9% of no-change nulls, where the split-half calls "kill" in all of them. A third form, Spearman(yield, p − noise), was tried and dropped: subtracting the split-half noise over-corrects, because a half sample is noisier than the full sample.

## Choices confirmed at the seal

- Both changes above are accepted. The absolute-concentration condition could never reach support because absolute perturbation grows with yield by construction. Size strata remove a confound that the pooled pilot showed.
- The noise measure is the plan's split-half (`noabs_split`). The two-sided noise floor is reported only, because it says "partly" in up to 9% of no-change nulls.
- Scope: every single-species addition with at least 5 droplets on both sides (1,093 pairs). The paper's own 162 pairs are mostly one-droplet networks, so they cannot carry a noise adjustment. The 41 that can are reported only.
- Power limit, accepted: a weak true trade-off (planted −0.08) is killed 42% of the time. A kill here means "no trade-off of about −0.15 or stronger beyond noise", not "no trade-off at all".

## Planted check (`t8_analysis.py planted`; run; synthetic fractions only)

Every replicate keeps the real 1,837 networks, the real 20,039 droplets with their real ribozyme UMI totals, the real network yields, and the 1,093 real pairs. It never reads a real fraction. 100 replicates per row; noise from 40 splits and 40 bootstrap draws; intervals from 1,000 cluster draws. Script sha256 18ffe6a2….

**How synthetic droplets are made.**
- Each species v gets a random effect θv ~ N(0, 1). Each ordered pair (u, v) gets a random interaction βuv ~ N(0, σβ²). Neither depends on the real chemistry or on yield.
- The true composition of network N is πN,v ∝ exp(θv + gN Σu∈N βuv).
- Under the null gN = 1, so the true composition does not depend on yield. With σβ = 0 every true perturbation is exactly 0, and only noise remains.
- A planted trade-off sets gN = exp(−γ zN), where zN is the log yield of N standardised within networks of its size. Interactions are then weaker in high-yield networks, so adding a species changes them less.
- Each droplet's counts are Dirichlet-multinomial around πN, with its real UMI total. The concentration κ is unlimited (multinomial only), 50 or 20. In "extra noise at low yield", κ = 50 × (Y/median Y), so low-yield networks get extra droplet-to-droplet noise beyond counting.
- "True r" is the size-stratified Spearman correlation between yield and the true perturbation.

| Planted | True p (mean) | True r | Raw r (K-a) | Adjusted r (K-b) | Primary: kill, partly, support | Plan as written: kill, partly, support | Floor noise: kill, partly, support |
|---|---|---|---|---|---|---|---|
| Null, no true change, multinomial only | 0.00 | 0.00 | -0.19 | -0.04 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Null, no true change, κ = 50 | 0.00 | 0.00 | -0.11 | -0.02 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 0.91, 0.09, 0.00 |
| Null, no true change, extra noise at low yield | 0.00 | 0.01 | -0.22 | -0.06 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Null, σβ = 0.5, κ = 50 | 0.26 | 0.00 | -0.01 | 0.02 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Null, σβ = 1, multinomial only | 0.40 | 0.01 | 0.00 | 0.09 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Null, σβ = 1, κ = 50 | 0.40 | 0.00 | -0.00 | 0.06 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Null, σβ = 1, κ = 20 | 0.40 | -0.01 | -0.01 | 0.04 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 0.99, 0.01, 0.00 |
| Null, σβ = 1, extra noise at low yield | 0.39 | -0.01 | -0.02 | 0.08 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 | 1.00, 0.00, 0.00 |
| Trade-off γ = 0.5, σβ = 1, κ = 50 | 0.40 | -0.08 | -0.08 | -0.09 | 0.42, 0.55, 0.03 | 0.42, 0.58, 0.00 | 0.35, 0.61, 0.04 |
| Trade-off γ = 1, σβ = 1, κ = 50 | 0.43 | -0.16 | -0.15 | -0.19 | 0.01, 0.57, 0.42 | 0.01, 0.99, 0.00 | 0.01, 0.55, 0.44 |
| Trade-off γ = 2, σβ = 1, κ = 50 | 0.50 | -0.25 | -0.23 | -0.29 | 0.00, 0.08, 0.92 | 0.00, 1.00, 0.00 | 0.00, 0.11, 0.89 |
| Trade-off γ = 2, σβ = 0.5, κ = 50 | 0.40 | -0.44 | -0.38 | -0.40 | 0.00, 0.00, 1.00 | 0.00, 1.00, 0.00 | 0.00, 0.00, 1.00 |
| Trade-off γ = 3, σβ = 0.5, κ = 50 | 0.44 | -0.44 | -0.38 | -0.41 | 0.00, 0.00, 1.00 | 0.00, 1.00, 0.00 | 0.00, 0.00, 1.00 |
| Trade-off γ = 2, σβ = 0.5, κ = 20 | 0.40 | -0.42 | -0.34 | -0.36 | 0.00, 0.00, 1.00 | 0.00, 1.00, 0.00 | 0.00, 0.00, 1.00 |
| Trade-off γ = 2, σβ = 0.5, extra noise at low yield | 0.40 | -0.44 | -0.39 | -0.39 | 0.00, 0.00, 1.00 | 0.00, 1.00, 0.00 | 0.00, 0.00, 1.00 |

"Raw r" and "Adjusted r" are means over replicates. The verdict columns are shares of the 100 replicates.

What the table shows.

- **Noise alone makes a trade-off.** With no true change at all, the raw size-stratified correlation is −0.11 to −0.22. That is the artefact the plan suspected, at the real UMI counts. A raw trade-off of that size is not evidence.
- **The adjustment removes it.** The adjusted correlation is −0.06 to +0.09 under every null, and every null replicate is a kill. False support is 0 in 800 null runs, well under the 5% limit.
- **Both verdicts are reachable.** Kill has probability 1.00 under every null. Support has probability 0.92 at a true correlation of −0.25 and 1.00 at −0.42 to −0.44, including with extra noise at low yield.
- **A weak true trade-off can be killed.** At a true correlation of −0.08, the primary kills 42% of the time. At −0.16 it kills 1%, says "partly" 57% and supports 42%.
- **The plan's rule as written could not support.** See "Changes from the plan".
- **The adjusted correlation overshoots upward when the true perturbation is large and unrelated to yield** (+0.06 to +0.09 with σβ = 1). That pushes toward kill, not support.

**Dry run.** `t8_analysis.py dryrun` runs the full `real` code, including every reported-only extra, on yield permuted over the 1,837 networks. It ran without error.
- Primary: r_yp 0.030 (−0.045 to 0.107), r_yz 0.091, r_B −0.008 (−0.074 to 0.056). Verdict "kill", as it should be.
- Every other rule also said "kill".
- Its other numbers are synthetic, apart from the marginals disclosed above.

## Reported only (no rule attached)

`real` also prints these. None can change the verdict.

- K-a with its interval (the plan's unadjusted test).
- The adjusted correlation with the two-sided noise floor (D5), and the rule that needs both noise measures (`noabs_both`).
- **Absolute concentrations** (the plan's condition, and the paper's Supplementary Fig. 6e): the raw and adjusted correlations between yield and Σ|Y′m′ − Ym|, with the noise scaled by the pair's mean yield, and the verdict of the plan's rule as written.
- Spearman(yield, p − noise) for both noise measures.
- The pooled correlation without size strata.
- Each size of G separately, for sizes with at least 30 pairs.
- Pairs with at least 3 droplets (1,621 pairs) and at least 10 droplets (547 pairs).
- The Fig. 2d subset limited to pairs with at least 5 droplets (41 pairs): Spearman between yield and p, and between yield and p minus the noise floor.
- The median of p and of the noise floor, and the share of pairs with p below the floor.

## Ways it could be fooled, and limits

1. **The noise model is a guess.** The planted check covers multinomial counting with or without extra Dirichlet noise, and extra noise at low yield. Real droplets may also suffer fusion errors, barcode cross-talk and PCR jackpots that depend on yield in other ways. The adjustment is calibrated for the modelled noise, not the true noise.
2. **The noise of G′ is not in the primary.** The split-half noise uses G only. G′ has its own noise. The two-sided floor (D5) includes both and is reported, along with the rule that needs both.
3. **Partial correlation is linear in ranks.** If noise and true change combine non-linearly (they add roughly in quadrature), a rank-linear adjustment can leave some artefact behind. In the planted nulls the leftover is −0.06 at most, well short of −0.20.
4. **Yield itself is noisy, and network yield is a mean.** Supplementary Data 2 gives only the network mean yield, not each droplet's, so yield noise cannot be modelled per droplet. Noise in yield weakens any true correlation toward 0, which favours a kill.
5. **The tested question is broader than Fig. 2d.** The paper's claim rests on 162 catalytic-innovation pairs, mostly from one- or two-droplet networks. This study tests every single-species addition with 5 or more droplets on both sides, across sizes 2 to 15. A trade-off confined to catalytic innovations in small networks could be diluted here. The Fig. 2d subset at 5 or more droplets (41 pairs) is reported, but it is too small to decide.
6. **Topology is a real cause, not an artefact.** The paper explains part of the trade-off through background strength σG, which tracks yield. Support here means "more than noise". It does not mean "independent of topology".
7. **Pairs share networks.** One G starts several pairs, and one G′ can end several. The interval resamples G only, so it is somewhat too narrow.
8. **Fixed rank scores in the bootstrap.** The bootstrap reweights fixed rank scores rather than re-ranking each draw. This is close, but not exact.
9. **The one network with a count mismatch** (3 droplets, listed as 2) is used with its 3 droplets.
10. **The planted trade-off is one mechanism.** It weakens interactions in high-yield networks. A real trade-off might take another form, with other power.

## Sources actually opened

- Ameta et al. 2021: full text from Europe PMC (`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7870898/fullTextXML`); Supplementary Information PDF and Supplementary Data 2 xlsx from `static-content.springer.com`; the authors' code from GitHub `smnars/azoarcus_networks` at commit 76cd71ecdb4a867f3a034a05f671cc64661d104c (`analysis/figures.ipynb`, `analysis/supplementary_figures.ipynb`, `utils/az_tools.py`, `utils/az_model.py`, `README.md`), read as source and never run.
- Prior art: `experiments/t8_ameta_noise/PRIOR_ART.md` lists every search and every abstract read. No reanalysis of the trade-off was found.
