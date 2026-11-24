# T11 result: epistasis finds base pairs almost perfectly, and tertiary contacts only weakly; the sealed test is inconclusive

Prereg: `docs/prereg/t11_ribozyme_epistasis.md`, sealed in 288b952 (`HASHES.txt`). Script: `scripts/t11_analysis.py` (sha256 85b93369…). Output: `results/t11_real.json`.

## Claim

Roberts et al. 2023 (eLife 12:e80360, doi:10.7554/elife.80360) measured every single and double mutant of five self-cleaving ribozymes. They write that the data reveal "paired regions, unpaired loops, non-canonical structures, and tertiary structural contacts", but they show this with heat maps only. They give no score against a null.

The question is whether pairs of nucleotides in tertiary contact in the crystal structure have higher positive epistasis than non-contact pairs. The comparison holds sequence separation and how harmful the single mutants are fixed.

- **Score.** Each double gets a z: how far it beats the prediction from its two singles, after fitting the global curve and allowing for counting and replicate noise. A pair's score is its largest z.
- **Effect size.** Δ is the matched AUC minus 0.5.
- **Positive control.** Base pairs must reach Δ ≥ 0.15.

## Sealed verdict: inconclusive

| | Δ | 90% interval (5th to 95th percentile) |
|---|---|---|
| Base pairs, pooled (positive control) | **0.44** | 0.33 to 0.50 |
| Tertiary contacts, pooled (decision) | **0.11** | −0.02 to 0.23 |

- **Base-pair check.** HDV, hammerhead, hairpin and twister pass, with base-pair Δ of 0.30 to 0.49. Hatchet fails (0.06), as the planted check predicted from its near-neutral singles. Four of the five deciding ribozymes count, so the verdict is not void.
- **Support** needed a pooled Δ ≥ 0.10 (met, 0.113), a 5th percentile above 0 (missed, −0.017), and at least 2 ribozymes at 0.10 or more (met: HDV 0.14 and twister 0.15).
- **Kill** needed the 95th percentile below 0.15. It is 0.23, so an effect of the size the plan called support is not ruled out.
- **Hatchet included anyway (reported only):** pooled tertiary Δ 0.08 (−0.02 to 0.16), also inconclusive.

| Ribozyme | Base pairs Δ | Tertiary Δ | Contacts scored |
|---|---|---|---|
| HDV | 0.49 | 0.14 | 15 |
| Hammerhead | 0.30 | 0.09 | 18 |
| Hairpin | 0.47 | 0.08 | 27 |
| Twister | 0.47 | 0.15 | 21 |
| Hatchet (failed the check) | 0.06 | 0.00 | 36 |
| CPEB3 (reported only) | 0.43 | 0.15 | 14 |

## Reported only (no rule)

- **The plan's own per-ribozyme rule gives "kill", with both z and raw ε.** This is not a finding. That rule counts ribozymes whose interval includes 0, and each ribozyme's interval is about ±0.3 wide. The planted check showed it rarely reaches support even when a strong signal is planted (see the prereg).
- **Every sensitive ribozyme leans the same way.** Tertiary Δ is between 0.07 and 0.16 under every variant: unmatched, separation-only, tercile strata, 10 or 50 reads, non-contacts beyond 8 Å, mean z and isotonic ε. CPEB3, which did not decide, also gives 0.10 to 0.15. Hatchet sits at about 0 throughout.
- **Proximity in general does not explain it.** Non-contact pairs at 4–6, 6–8 or 8–12 Å score about the same as pairs beyond 12 Å (bands −0.09 to 0.05, except HDV 4–6 Å at 0.23). The faint signal belongs to actual contacts, not just nearby nucleotides.
- **The plan's raw ε** gives higher tertiary Δ (0.11 to 0.22). The planted check showed it is biased by up to 0.17 with nothing planted, which is why it is reported only.

## Reading

- **What it shows.** On full double-mutant scans of four ribozymes, epistasis recovers Watson–Crick base pairs almost perfectly (matched AUC about 0.94). Tertiary contacts are recovered only weakly, at a matched AUC of about 0.61. The point estimate is consistent and positive in every ribozyme with harmful single mutants. With 81 contacts, the test cannot tell 0 from about 0.2.
- **What it does not show.** It does not confirm the paper's claim that the data reveal tertiary contacts in a way that holds up against a matched null: the lower bound touches 0. It does not refute it either. The crystal structures are single states, often of the product. The contact definition (4 Å) mixes backbone contacts, which no base change can rescue, with base contacts.
- **The comparison that matters.** The structural signal in these scans is base pairing. Tertiary contacts add, at best, a small signal that would need several times more contacts to establish.

## What it means for us

- **Our QT45 study (#30)** found no tertiary-contact signal in epistasis and had no positive control. These scans now give it one. The method sees base pairs easily and tertiary contacts only faintly, even in good data. So #30's negative is what this method should be expected to give, and is not evidence against structure in QT45.
- **For the replicator-first route,** epistasis maps are a reliable way to read secondary structure from fitness data, but not yet a way to read 3D structure. Any claim that "the fitness landscape encodes the fold" should be limited to base pairing unless it is tested against a matched null.
- **A side finding:** CPEB3 does have a crystal structure (7QR3, 2022), though Roberts et al. say it does not. Its contacts give the same faint signal as the others.
- This is a fully deposited reanalysis that uses the authors' own counts, and could be worth a friendly note. The owner decides.
