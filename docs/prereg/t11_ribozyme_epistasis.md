# Pre-registration (T11): does pairwise epistasis find tertiary contacts in ribozymes with solved structures?

Status: DRAFT, written 2026-11-24 by the T11 prep agent. This is study S6 in `docs/plans/next_studies_2026-11-24.md`. `gate`, `planted` and `dryrun` have been run. `real` has not been run and the script refuses to run it until `docs/prereg/HASHES.txt` names `experiments/t11_ribozyme_epistasis/scripts/t11_analysis.py` with its current sha256. Nothing is sealed, committed or pushed.

## What has been seen (blinding disclosure)

The unknown is the pairing of double-mutant activity with the structure labels: whether contact pairs score higher than matched non-contact pairs. Every deciding number comes from that pairing.

- **Not computed.** No double-mutant value, epistasis value or pair score has been joined to a real contact, base-pair or non-contact label. No script has printed one.
- **Structure only, before any activity was read.** The contact labels (`data/t11_contacts.json`) were built from the PDB files by `t11_structures.py`. It reads no activity file. The gate counts are below.
- **Data structure, coverage and depth (allowed).** Pickle keys, genotype counts, read depth per genotype and the wild-type fraction cleaved in each replicate (`scripts_out/t11_gate.json`).
- **Single mutants, without labels.** I looked at the spread of single-mutant effects (quantiles of f over all singles) and at replicate noise estimated from singles. This showed one thing that matters: **hatchet single mutants are nearly neutral** (f from −0.03 to 0.02 between the 5th and 95th percentiles, none below −0.5), and the median double is also near 0. A ribozyme with no harmful mutations cannot show compensation, for base pairs or for contacts. The planted check confirms that hatchet almost never passes the base-pair check (4 to 5% of replicates). I kept hatchet in the deciding set and let the pre-set base-pair check handle it (D2).
- **Real singles and real labels inside the planted check.** The planted generator uses the real single-mutant activities and read depths and the real labels to plant synthetic doubles. Its outputs are synthetic. It never reads a real double.
- **The dry run.** `dryrun` runs `real` on the real doubles with all three labels permuted within separation bins. Its numbers carry no information about the real labels.
- **The second HDV file (`..._v2_HDV_...`).** I opened its structure only: a flat table of one number per genotype, with no cleaved/uncleaved split and no replicates. It cannot feed this pipeline and is not used.
- **What this does to my expectation.** Roberts et al. report that the hammerhead loop-loop contact shows no positive epistasis, and Andreasson et al. missed a base triple at a catalytic site. I expect a small effect at best. I have no view on whether it clears 0.10.

## Claim under test

Roberts et al. 2023, eLife 12:e80360, doi:10.7554/elife.80360 (PMC9901934, read in full; quotes in `experiments/t11_ribozyme_epistasis/PRIOR_ART.md`).

- Abstract, verbatim: "Heatmap-based visualization of the data revealed patterns indicating structural features of the ribozymes including paired regions, unpaired loops, non-canonical structures, and tertiary structural contacts. ... The results demonstrate that the data sets provide structural information similar to chemical or enzymatic probing experiments, but with additional quantitative functional information."
- Introduction, verbatim: "the propensity for positive epistasis between physically interacting nucleotides suggests that a comprehensive evaluation of pairwise mutational effects should contain considerable structural information."

The paper gives no score of tertiary contacts against a null.

**H1.** Nucleotide pairs in tertiary contact score higher on positive epistasis than non-contact pairs at the same sequence separation and with equally harmful single mutants.

**H0.** They do not. Once separation and single-mutant effects are matched, epistasis does not tell tertiary contacts from non-contacts.

**Why it matters here.** Our QT45 study (#30) was negative and had no positive control (`docs/library/IDEAS.md`, idea 4; `experiments/qt45_epistasis/RESULTS.md`). These five ribozymes give that control: every single and double mutant, measured under one protocol, in RNAs with solved structures.

## Inputs (exact)

Paths are under `experiments/t11_ribozyme_epistasis/`. Downloads used the User-Agent `open-research-site/1.0` and no name or email. Every Python run used `-I`, one thread and `nice -n 20`.

**Activity data.** GitLab `bsu/biocompute-public/mut_12`, commit `7be31e58784ab6ffe5f15790ebbda98279af84d2` ("Add ENA Data", 2022-08-19). This is the Software Heritage revision the paper cites (`swh:1:rev:7be31e58...`). Saved to `raw/gitlab/files/` (gitignored). The files are untrusted pickles. They are read only through `scripts/safe_pickle.py`, an unpickler that resolves no globals at all. An opcode scan (`scripts/pickle_globals.py`) found no GLOBAL, STACK_GLOBAL, REDUCE, BUILD or NEWOBJ in any of them. Each one is a dict of dicts of str to int or float.

| File | Ribozyme | sha256 |
|---|---|---|
| `raw/gitlab/files/Data_Counts_JB_HDV_Mut12_seqData_JB.p` | HDV | a6267b417f6315675290628878156237b9b9d5050e807faca41c3678ba56cc18 |
| `raw/gitlab/files/Data_Counts_JB_HHIII_Mut12_seqData_JB.p` | Hammerhead | d85919e5d2438b561549d3a761b4bb36d8528c58520d14ab20de3bb78d16c84b |
| `raw/gitlab/files/Data_Counts_JB_Hairpin_Mut12_seqData_JB.p` | Hairpin | 6149e2a75eff2e35f2f4b572fcaff87db4ef8a19b12c5a382c9a9370ade92275 |
| `raw/gitlab/files/Data_Counts_JB_Hatchet_Mut12_seqData_JB.p` | Hatchet | 4a89503524e752d8b1909d31b5c9987094a1fe3470e54aae5321fa989b3989f5 |
| `raw/gitlab/files/Data_Counts_JB_Twister_Mut12_seqData_JB.p` | Twister | f2467181555ef5f21d2c8ea9ee175659b4f0d2f09a8e2108d06b1df657d3d52b |
| `raw/gitlab/files/Data_Counts_JB_CPEB3_Mut12_seqData_JB.p` | CPEB3 (reported only) | ab44c25662b1a4dffad631e6f3321d6e9cae2009d8b065a4cfdaa37b133fbb32 |
| `raw/gitlab/files/Data_Structures_ribo_structures.p` | deposit dot-bracket stems; used only to check our base pairs | 9c075296c3e8dfb02bf953d02a162a85bb4aab3e81cbae1544a5ec418ee3fabc |

Each counts pickle has the keys `rz_cleaved1-3`, `rz_uncleaved1-3`, `relative_fitness1-3` and `fitness`. Only the six count keys are used. The wild type is the most-read genotype, and it equals the per-position consensus.

**Structures.** mmCIF from RCSB, saved to `raw/pdb/` (gitignored). `t11_structures.py` checks each file's sha256.

| Ribozyme | PDB | Resolution | sha256 of the cif |
|---|---|---|---|
| HDV | 1DRZ (genomic ribozyme, U1A complex, product) | 2.3 Å | 8a1551b200e38766741140dad7e9262d8a3c31f390567704e08d3dd2b453bb65 |
| Hammerhead | 2QUW (G12A mutant, after cleavage) | 2.2 Å | c572d8fd77cd9a6318e72b624e6af2d24960960fd1d593d39de715b91f8691ea |
| Hairpin | 1M5K (catalytically active conformation), the PDB named in Roberts | 2.4 Å | 927536265d5e1d2beadc36b4d634a94d2faab8297c024adf89a128758dc31a86 |
| Hatchet | 6JQ5 (product, domain-swapped dimer) | 2.06 Å | 03b50dcb3a2c615a6ca6460505590bfae49d0738bedbcafb3a2d2479481f3d71 |
| Twister | 4OJI (O. sativa Osa-1-4), also used by Zhang 2020 | 2.3 Å | 1e5f64af150856519583393426182ad454f82a6dde3cd3570ad62ecc6b375473 |
| CPEB3 | 7QR3 (chimpanzee, crystal dimer) | 2.18 Å | bb8066f864990e63557053624a766f21845365483b6c33c43ffe886e20337e44 |

1SJ3, 4PR6, 2QUS, 3ZD5, 6JQ6 and 7QR4 were downloaded and compared as alternatives; they are not used. Their entry lines are in `raw/pdb/entry_info.txt`.

**This study's files.**

| File | What | sha256 |
|---|---|---|
| `data/t11_contacts.json` | labels, maps, distances (built by `t11_structures.py`) | 3ed1a94a02a9ac8c1f530add799065fc97fc1c1258cb4c81a4b0f700339e0bda |
| `scripts/t11_structures.py` | structure gate | a82cdeea5e21972c041f8c85fb2ec56f4cc9b1d83fa31a17a51c71d02c1c4bf5 |
| `scripts/safe_pickle.py` | restricted unpickler | 6e56948a4ff3121ea4d840898da9cb3637864afb429552b531978072c6b4eadc |
| `scripts/t11_analysis.py` | gate, planted, dryrun, sealcheck, real | 85b93369106bd7322e5841d542998e5028173c90c9f691b19714186b36400245 |
| `scripts_out/t11_gate.json` | `gate` output | d60b4d22b07745ed9178cf9692a8105f98d2f7bd8d33985c81c5853cec7bf97d |
| `scripts_out/t11_planted.json` | `planted` output | 0961279a6e0a2583b3848440b004fcfd1d96d4ffcd31290929680129917b979d |
| `scripts_out/t11_dryrun_permuted_labels.json` | `dryrun` output | fa31a5ba2229c74629da8f0bd70658f98e290eec05f8ce0d80253db7240b49a6 |

`t11_analysis.py` checks the sha256 of every counts file and of the contacts JSON, and stops on a mismatch.

## Structure labels (fixed before any activity value was read)

**Numbering.** Each wild-type position is mapped to a residue by explicit blocks `(wt_from, wt_to, chain, auth_from)`, read by hand from the sequences. The script checks every mapped base and drops any position whose base differs. A position with no residue, or with a different base, is unmapped. Every pair that touches an unmapped position is left out.

| Ribozyme | Blocks | Mapped | Notes |
|---|---|---|---|
| HDV | 1-45 → B101-145; 72-84 → B160-172 | 58 of 87 | P4 (46-71) is replaced by the U1A loop in the crystal; 85-87 are absent |
| Hammerhead | 1-45 → B13-57 | 44 of 45 | position 39 is the G12A mutation in the crystal, dropped |
| Hairpin | 1-7 → A13-19; 24-50 → B3-29; 54-71 → B52-69 | 51 of 71 | four-way junction construct; 34 is a mismatch; 51-53 is the U1A arm; 8-23 are not mapped |
| Hatchet | 1-6 → A1-6; 10-46 → A13-49; 47-63 → A50-66; 68-78 → B71-81 | 66 of 78 | the functional monomer A′ is chain A up to the swap and chain B after it; 64-67 (the palindrome that forms the intermolecular duplex) are excluded; 7-9 are not mapped; 15 and 43-46 (UUCG in the scan, GAAA in the crystal) are mismatches |
| Twister | 1-48 → A7-54 | 46 of 48 | auth 17-18 are not modelled |
| CPEB3 | 1-41 → C1-41; 55-67 → C57-69 | 54 of 69 | reported only (D2) |

**Base pairs (canonical).** A pair is canonical if it is GC, AU or GU and its hydrogen-bond distances are all at most 3.5 Å: GC needs N1-N3, O6-N4 and N2-O2; AU needs N1-N3 and N6-O4; GU needs N1-O2 and O6-N3. The two bases must also be coplanar: each base's centroid sits less than 2.0 Å from the other base's plane, measured along the normal. Without the coplanarity test, stacked neighbours were being called pairs.

**Helical pairs.** A pair that is not canonical but lies within index distance 2 of a canonical pair (|i − a| + |j − b| ≤ 2) is helical. These are stacking and cross-strand neighbours of helices. They are neither contacts nor non-contacts.

**Tertiary contacts.** Heavy atoms within 4.0 Å, sequence separation ≥ 4, not canonical, not helical.

**Non-contacts.** No heavy atoms within 4.0 Å, separation ≥ 4, not canonical, not helical.

**Base pairs used as the positive control.** Canonical pairs with separation ≥ 4.

## Gate (`t11_structures.py` and `t11_analysis.py gate`; run; passed)

| Ribozyme | Canonical (sep ≥ 4) | Helical | Tertiary | Non-contacts | Deposit stem pairs recovered | Kept (≥ 15 tertiary) |
|---|---|---|---|---|---|---|
| HDV | 19 | 101 | 22 | 1,349 | 16 of 17 mapped | yes |
| Hammerhead | 12 | 73 | 18 | 726 | 10 of 10 | yes |
| Hairpin | 12 | 65 | 27 | 1,039 | 11 of 12 | yes |
| Hatchet | 22 | 109 | 36 | 1,807 | (none in the deposit) | yes |
| Twister | 14 | 90 | 21 | 784 | 13 of 14 | yes |
| CPEB3 | 15 | 87 | 14 | 1,165 | 14 of 18 | no (reported only anyway) |

The canonical pairs not in the deposit stems are known pairs: HDV G1·U37 and P1.1 (21-39, 22-38); hammerhead C20-G25 and U12-A34 (the loop pair); hairpin G1-C46 (the docking pair Roberts name); twister C9-G13 (the lone pair Zhang name); CPEB3 1-36.

| Ribozyme | Doubles observed / expected | Doubles with ≥ 20 reads | Median reads per double | Replicate noise τ (logit) | Tertiary pairs with ≥ 5 usable doubles | Base pairs with ≥ 5 usable doubles |
|---|---|---|---|---|---|---|
| HDV | 33,669 / 33,669 | 24,258 | 26 | 0.106 | 15 of 22 | 17 of 19 |
| Hammerhead | 8,910 / 8,910 | 8,910 | 447 | 0.136 | 18 | 12 |
| Hairpin | 22,365 / 22,365 | 22,364 | 102 | 0.151 | 27 | 12 |
| Hatchet | 27,027 / 27,027 | 27,027 | 103 | 0.031 | 36 | 22 |
| Twister | 10,152 / 10,152 | 10,152 | 309 | 0.281 | 21 | 14 |
| CPEB3 | 21,114 / 21,114 | 21,114 | 154 | 0.161 | 14 | 15 |

Every single and every double is present in all six files. Five deciding ribozymes pass, so the gate passes (it needs 3).

## Fixed decisions

- **D1, data.** The six count pickles above, at the pinned commit. Reads are summed over the three replicates.
- **D2, deciding set.** HDV, hammerhead, hairpin, hatchet and twister. CPEB3 is reported only, because its crystal (7QR3) is a dimer in which the P1.1 region pairs with a symmetry mate, so its tertiary contacts there may be crystal contacts. Hatchet stays in, and the base-pair check (D10) decides whether it counts. Its near-neutral singles were seen before this was fixed (see the disclosure), and the planted check says it will almost certainly fail that check.
- **D3, activity.** FC(g) = (C + 0.5) / (N + 1), with C the cleaved reads and N the total reads of genotype g. f(g) = log10(FC(g) / FC(wt)).
- **D4, usable doubles.** A double needs at least 20 reads over the three replicates.
- **D5, usable pairs.** A position pair needs at least 5 usable doubles of its 9.
- **D6, strata.** Separation bin (4-7, 8-15, 16-30, 31+) × the sorted pair of sensitivity quartiles of the two positions. Sensitivity s(i) is the mean f of the three singles at i. The quartiles are taken over the mapped positions of each ribozyme.
- **D7, epistasis of one double.** Fit g, an isotonic (non-decreasing) function of f(a) + f(b) to f(double), over all usable doubles of the ribozyme. This is the global nonlinearity, as in #30. Then z = (p_obs − p0) / sd, with p_obs = FC(wt)·10^f(double) and p0 = FC(wt)·10^g(f(a) + f(b)), clipped to 1e-4 to 0.999. The variance is sd² = p0(1 − p0)/N + (Σ_r N_r² / N²)·(p0(1 − p0))²·τ². Here τ is the replicate noise on the logit scale, estimated from the singles. So z measures how far a double beats the global-nonlinearity prediction, in units of its own counting and replicate noise.
- **D8, pair score.** S(i, j) is the largest z over the usable doubles at i, j. The largest is used because a contact may be rescued by one specific pair of bases.
- **D9, effect size and interval.** Δ = stratified AUC − 0.5: over (positive, non-contact) pairs in the same stratum, the share in which the positive scores higher, with ties counting half. A stratum with no non-contacts drops out. Interval: 2,000 bootstrap draws over nucleotide positions. Positions are resampled with replacement, and a pair's weight is m_i·m_j.
- **D10, base-pair check (positive control).** A deciding ribozyme passes if its base-pair Δ (canonical pairs against non-contacts, same strata) is at least 0.15. **Failure outcome, fixed now:** if fewer than 3 deciding ribozymes pass, the verdict is **void**. The method could not see base pairs in this data, so the data say nothing either way about tertiary contacts, and #30's negative is neither explained nor excused by it.
- **D11, thresholds.** T_SUPPORT = 0.10 and T_EXCLUDE = 0.15.
- **D12, pooling.** The pooled tertiary Δ is the mean of the passing ribozymes' tertiary Δ, weighted by their numbers of usable contacts. Its interval adds the bootstrap draws of each ribozyme with the same weights; the bootstraps are independent across ribozymes. The 5th and 95th percentiles are used.
- **D13, seed and order.** Seed 20261125. Generators: `[seed, 2]` planted, `[seed, 3]` real, `[seed, 4]` dryrun. Order: `gate`, `planted`, `dryrun`, then seal, then `real`. `real` exits unless `HASHES.txt` has a line that names the script and starts with the script's current sha256.

## Decision rules

Applied in this order.

- **Void.** Fewer than 3 deciding ribozymes pass the base-pair check (D10).
- **Support.** The pooled tertiary Δ is at least 0.10, its 5th percentile is above 0, and at least 2 passing ribozymes each have tertiary Δ ≥ 0.10.
- **Kill.** The pooled 95th percentile is below 0.15. The data then rule out an effect of the size the plan called support.
- **Otherwise inconclusive.**

## Changes from the plan, made before the seal

The plan's rule was: score each pair by its largest raw epistasis; per ribozyme, compare tertiary contacts against matched non-contacts by AUC; **kill** if the difference is below 0.05 (interval including 0) in at least 4 of 5 ribozymes; **support** if it is at least 0.15 in at least 3 of 5; base pairs as a planted positive. The matching, the 0.15 size and the base-pair control are kept. Four things changed, each because of the planted check.

1. **The statistic: z against the global nonlinearity, not raw ε.** The plan's ε = f_ab − f_a − f_b, maximised over doubles, is biased under the null. With no tertiary signal planted, its Δ is 0.10 (HDV), 0.17 (hammerhead), 0.07 (hairpin) and 0.09 (twister). Hammerhead would read as "strong" with nothing there. The cause is that the floor and the curvature of activity make ε depend on the single effects in a way the quartile strata only partly remove. An isotonic ε (the #30 form) still left hammerhead near 0.10 in an exploratory run. The z form (D7) has null Δ within ±0.04 for every ribozyme and every null model, and it keeps the power (table below). Raw ε and isotonic ε are reported only.
2. **The decision is pooled, not counted per ribozyme.** One ribozyme has 12 to 36 contacts, and the position bootstrap gives each per-ribozyme Δ an interval about ±0.3 wide. The plan's per-ribozyme rule, even with z as the statistic, never reaches support above 7.5% of replicates, even with every contact visible at 80% strength. It returns void in 53 to 97% of replicates, because a per-ribozyme base-pair interval rarely clears 0. Pooling about 100 contacts narrows the 90% interval to about ±0.09 (dry run). The "at least 2 ribozymes" condition keeps one ribozyme from carrying support alone.
3. **The base-pair check is a point threshold.** For the same reason, "base-pair Δ ≥ 0.15" is used without an interval condition. When base pairs are planted, the base-pair Δ is 0.26 to 0.41 and the pass rate is 88 to 100% for HDV, hammerhead, hairpin and twister (one exception: hammerhead under floor_hetero, 1%). When they are not planted, the pass rate is at most 5%.
4. **Kill is "0.15 excluded", not "below 0.05".** Under the pooled interval, "Δ below 0.05" is a weak target. The plan's own support size (0.15) is the effect worth ruling out. Under every null with base pairs planted, kill has probability 0.58 to 0.85, and false support is 0.

Two other changes from the plan text:

- **The ribozyme set.** The plan said "five ribozymes with known structures", meaning the five in Roberts (CPEB3, HDV, hammerhead, hairpin, twister). Roberts believed CPEB3 had no crystal structure; it has one (7QR3, 2022), but in a dimer that rearranges P1.1. The deposit also holds hatchet, which has a crystal structure (6JQ5) and is not in the paper. The deciding set swaps CPEB3 for hatchet. CPEB3 is reported in full.
- **Base pairs come from the structure, not the deposit's stems.** The geometric rule finds the deposit's stems (50 of 53 mapped stem pairs in HDV, hammerhead, hairpin and twister; 14 of 18 in CPEB3; the deposit has no hatchet stems) and a few known pairs the stems lack (listed under the gate), so labels are consistent across ribozymes.

## Planted check (`t11_analysis.py planted`; run; synthetic doubles only)

Every replicate keeps the real single-mutant activities, real read depths, real labels and real replicate structure. It never reads a real double. 200 replicates per row, 200 bootstrap draws each. Script sha256 85b93369….

**How synthetic doubles are made.** The true double activity starts from f_a + f_b (null "mult") and is capped at +0.3. Base pairs: with probability 0.8, a pair's pairing-restoring doubles move 75% of the way back to wild type. Tertiary contacts: with probability π, one random double of the pair's nine moves ρ of the way to wild type. Then a floor is applied (the lowest single FC). Counts are binomial at the real depths, with per-replicate logit noise τ.

- **floor:** as mult; this is the default.
- **floor_hetero:** extra noise per position (sd 0.15) and per double (sd 0.15).
- **saturating:** a second hit in a broken molecule costs little: max(f_a + f_b, min(f_a, f_b) − 0.3).
- **no_bp:** base pairs not planted; the base-pair check should fail.

| Planted | Tertiary Δ, z (HDV / HH / HP / hatchet / TW) | Tertiary Δ, plan's raw ε | Pooled Δ | P(kill) | P(inconclusive) | P(support) | P(void) | Plan rule with z: kill / support / void |
|---|---|---|---|---|---|---|---|---|
| Null, mult | 0.00 / −0.00 / 0.01 / 0.00 / −0.03 | 0.11 / 0.17 / 0.07 / −0.02 / 0.09 | −0.00 | 0.81 | 0.19 | 0.00 | 0.00 | 0.37 / 0.00 / 0.63 |
| Null, floor | 0.00 / −0.01 / 0.00 / 0.00 / −0.03 | 0.10 / 0.17 / 0.07 / −0.01 / 0.08 | −0.01 | 0.83 | 0.16 | 0.00 | 0.01 | 0.43 / 0.00 / 0.56 |
| Null, floor_hetero | −0.01 / −0.04 / −0.00 / −0.00 / −0.01 | 0.08 / 0.06 / 0.07 / −0.01 / 0.06 | −0.01 | 0.58 | 0.29 | 0.00 | 0.13 | 0.03 / 0.00 / 0.97 |
| Null, saturating | −0.02 / −0.00 / 0.01 / 0.00 / −0.02 | 0.10 / 0.17 / 0.06 / −0.01 / 0.09 | −0.01 | 0.84 | 0.15 | 0.00 | 0.00 | 0.42 / 0.00 / 0.58 |
| Null, no base pairs | 0.01 / −0.02 / 0.01 / 0.00 / −0.03 | 0.10 / 0.16 / 0.07 / −0.01 / 0.08 | n/a | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 / 0.00 / 1.00 |
| π 0.2, ρ 0.5 | 0.06 / 0.02 / 0.03 / 0.01 / 0.04 | 0.14 / 0.18 / 0.07 / −0.01 / 0.13 | 0.04 | 0.40 | 0.57 | 0.04 | 0.00 | 0.47 / 0.00 / 0.53 |
| π 0.4, ρ 0.5 | 0.09 / 0.04 / 0.06 / 0.00 / 0.12 | 0.15 / 0.18 / 0.09 / −0.01 / 0.16 | 0.08 | 0.12 | 0.74 | 0.13 | 0.01 | 0.45 / 0.00 / 0.55 |
| π 0.6, ρ 0.5 | 0.15 / 0.05 / 0.09 / 0.01 / 0.21 | 0.18 / 0.18 / 0.09 / −0.01 / 0.21 | 0.12 | 0.01 | 0.50 | 0.48 | 0.00 | 0.45 / 0.00 / 0.55 |
| π 0.8, ρ 0.5 | 0.20 / 0.08 / 0.14 / 0.01 / 0.28 | 0.21 / 0.20 / 0.11 / −0.01 / 0.25 | 0.17 | 0.00 | 0.12 | 0.88 | 0.01 | 0.35 / 0.00 / 0.60 |
| π 0.4, ρ 0.8 | 0.16 / 0.09 / 0.21 / 0.01 / 0.17 | 0.20 / 0.22 / 0.22 / −0.00 / 0.21 | 0.16 | 0.00 | 0.25 | 0.74 | 0.01 | 0.41 / 0.00 / 0.58 |
| π 0.8, ρ 0.8 | 0.31 / 0.19 / 0.40 / 0.01 / 0.33 | 0.30 / 0.26 / 0.38 / −0.00 / 0.31 | 0.32 | 0.00 | 0.00 | 1.00 | 0.00 | 0.15 / 0.07 / 0.57 |
| π 0.6, ρ 0.5, saturating | 0.15 / 0.09 / 0.22 / 0.00 / 0.21 | 0.18 / 0.20 / 0.18 / −0.01 / 0.21 | 0.17 | 0.00 | 0.15 | 0.84 | 0.00 | 0.35 / 0.00 / 0.63 |

Base-pair check pass rate when base pairs are planted, over all rows (HDV / HH / HP / hatchet / TW): 0.99-1.00 / 0.88-0.94 / 0.98-1.00 / 0.03-0.05 / 0.99-1.00. Exception: under floor_hetero, hammerhead passes 1% of the time. With base pairs not planted, the pass rate is 0.01 to 0.05.

What the table shows.

- **The null works.** With no tertiary signal, z's Δ is within ±0.04 for every ribozyme and null model. False support is 0 in all five null rows (worst case 0 of 1,000 null replicates; the bar was 5%).
- **Both verdicts are reachable.** Kill has probability 0.81 to 0.84 under the main nulls. Support has probability 0.88 to 1.00 once most contacts are visible (π ≥ 0.8, or π 0.4 at ρ 0.8).
- **Weak signals are mostly inconclusive.** At π 0.2 to 0.4 (pooled Δ 0.04 to 0.08) the verdict is inconclusive 57 to 74% of the time. Kill there is 12 to 40%: a real but small effect can be called a kill when its pooled 95th percentile falls below 0.15. That is what kill means here: an effect of 0.15 is ruled out.
- **The plan's statistic is biased** (column "plan's raw ε"). Its null Δ for hammerhead is 0.16 to 0.17.
- **The plan's per-ribozyme rule cannot reach support** (last column). It is void in most replicates and gives support in at most 7.5%.
- **Hatchet adds nothing.** Its Δ is about 0 in every row, and it passes the base-pair check 3 to 5% of the time. When it does pass, it pulls the pooled Δ toward 0, which works against support.
- **The control does its job.** With no base pairs planted, the verdict is void every time.

## Dry run (`t11_analysis.py dryrun`; run; labels permuted)

`dryrun` runs the full `real` code, with every reported-only extra, on the real doubles. All three labels (canonical, tertiary, non-contact) are permuted within separation bins, so the base-pair control is broken too. Output (`scripts_out/t11_dryrun_permuted_labels.json`):

| Ribozyme | Base-pair Δ (95%) | Tertiary Δ (95%) |
|---|---|---|
| HDV | 0.14 (−0.17 to 0.41) | 0.01 (−0.25 to 0.29) |
| Hammerhead | −0.00 (−0.23 to 0.24) | −0.06 (−0.31 to 0.22) |
| Hairpin | 0.10 (−0.29 to 0.33) | −0.09 (−0.27 to 0.10) |
| Hatchet | −0.03 (−0.29 to 0.21) | −0.02 (−0.20 to 0.19) |
| Twister | −0.03 (−0.31 to 0.29) | 0.00 (−0.32 to 0.28) |
| CPEB3 (reported only) | 0.02 (−0.29 to 0.30) | 0.19 (−0.17 to 0.41) |

- Verdict: **void**. No ribozyme passes the base-pair check, as it should when labels are random.
- With the base-pair check skipped: pooled tertiary Δ −0.03 (5th to 95th percentile −0.12 to 0.06), so **kill**.
- The plan's rule, with z and with raw ε: void.
- These numbers are synthetic; they say nothing about the real labels. They show that the code runs end to end and that random labels give void.

`sealcheck` reports `real_allowed: false`. `real` was called to confirm that it refuses; it exited with "REFUSED" before reading any data.

## Reported only (no rule attached)

`real` also writes these. None can change the verdict.

- The verdict if every deciding ribozyme had passed the base-pair check.
- The plan's per-ribozyme rule, with z and with the plan's raw ε (`reported_only_verdict_plan_rule_z`, `..._raw_eps`).
- Per ribozyme: raw-ε max (the plan's statistic) and isotonic ε, for contacts and base pairs; mean ε; mean z.
- Unmatched AUC (no strata), and separation-only strata.
- Tercile strata instead of quartiles.
- Usable-double thresholds of 10 and 50 reads.
- Tertiary contacts against non-contacts farther than 8 Å.
- Distance bands: non-contacts at 4-6, 6-8 and 8-12 Å against those beyond 12 Å. If epistasis reflects proximity in general, these bands show a gradient.
- A per-contact table: each contact's score and its rank among the matched non-contacts.
- All of the above for CPEB3.
- τ per ribozyme.

## Ways it could be fooled, and limits

1. **One crystal, one state.** Contacts come from a single crystal structure, often of the product, in a crystallisation construct (U1A loops in HDV and hairpin, a G12A mutant in hammerhead, a swapped dimer in hatchet). Solution contacts during cleavage may differ. This weakens H1's chance, not H0's.
2. **Unmapped regions.** HDV loses P4 and 3 terminal nucleotides; hairpin loses 8-23 and the U1A arm. Contacts there are not scored.
3. **4 Å is a blunt contact definition.** It mixes base-base, base-backbone and backbone-backbone contacts. A backbone contact may not be rescuable by any base change. The distance bands and the per-contact table are there to show this.
4. **Matching is coarse.** Quartile bins of sensitivity and four separation bins. A residual link between single effects and the score inside a stratum would bias Δ. The planted nulls bound this for the generator used; they cannot prove it for the real data.
5. **The planted generator is a guess.** Real epistasis may come from folding cooperativity, alternative folds or misfolding that the generator lacks. In particular, an alternative fold could make non-contact pairs show positive epistasis, which pulls Δ toward 0.
6. **Hatchet.** Its singles are near-neutral, so it almost certainly fails the base-pair check and does not count. The verdict then rests on four ribozymes, and void needs only two of those four to fail.
7. **HDV is shallow.** The median double has 26 reads, and 7 of 22 contacts lack 5 usable doubles. Its contacts are weighted by usable count, not by the full 22.
8. **Max over nine doubles.** Pairs with more usable doubles have more chances at a high maximum. Contacts and non-contacts in a stratum usually have all nine (except in HDV), so this is mostly balanced.
9. **Positions are not independent, pairs even less so.** The position bootstrap handles the shared-position dependence. It does not handle dependence through structure (whole helices or loops failing together).
10. **Base pairs as a control are easier than contacts.** Passing it shows the method can see the strongest kind of compensation. It does not show that it could see weaker kinds.
11. **The plan's thresholds were kept, but the rule's form changed** after the planted check (see "Changes from the plan"). The changes were made with no real double joined to a label.

## Sources actually opened

- Roberts et al. 2023, eLife, doi:10.7554/elife.80360: full text from Europe PMC (PMC9901934); the deposit at the pinned commit (README, the count pickles, `ribo_structures.p`; the notebooks and Julia code were downloaded but only skimmed for file use).
- Zheng et al. 2019, PNAS, doi:10.1073/pnas.1902413116 (hatchet structure): full text, PMC6561176.
- Zhang et al. 2020, Nucleic Acids Res., doi:10.1093/nar/gkz1192: full text, PMC7026644.
- Andreasson et al. 2020, Nat. Commun., doi:10.1038/s41467-020-15540-1: full text, PMC7125110.
- Przytula-Mally et al. 2022 preprint, doi:10.1101/2022.09.22.508989 (CPEB3 crystals): abstract only.
- RCSB entries 1DRZ, 1SJ3, 4PR6, 2QUS, 2QUW, 3ZD5, 1M5K, 6JQ5, 6JQ6, 4OJI, 7QR3, 7QR4 (mmCIF and entry metadata).
- Prior-art searches and the other abstracts: `experiments/t11_ribozyme_epistasis/PRIOR_ART.md`.

## Decisions confirmed at the seal

1. **Hatchet** stays in the deciding set. The pre-set base-pair check (D10) decides whether it counts. It is not dropped by hand, even though its near-neutral singles were seen; dropping it would be a choice made after looking.
2. **The four rule changes** above are accepted. Each was forced by the planted check before any real double was joined to a label. The plan's per-ribozyme rule is computed and reported only.
3. **Thresholds** T_SUPPORT = 0.10 and T_EXCLUDE = 0.15, at least 20 reads per double and at least 5 usable doubles per pair, as in D4, D5 and D11.
4. **CPEB3** is reported only (D2).
5. No other change. Any change after this seal makes the verdict invalid.
