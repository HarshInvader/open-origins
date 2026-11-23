# T2 result: asteroid amino-acid abundance vs the Wehbi 2024 code order, beyond molecular weight

Prereg: `docs/prereg/t2_code_order.md`, sealed in f963a82. The power declaration was committed in 7cc5256, before the real run. Output: `results/t2_real.json`.

## Sealed verdict: cannot decide by design

The planted-signal check (`POWER_DECLARATION.md`) showed that Ryugu A0106 (n = 9) gives a kill under no signal only 26% of the time, and a support under the strongest planted signal only 47% of the time. Both are below the 50% bar, so both verdicts were declared unreachable before the real test ran. That label stands.

## What the data show

| Sample | Role | n | Partial τ | One-sided p | Upper 95% | τ(x,y) | τ(x,MW) | τ(y,MW) | Leave-one-out range |
|---|---|---|---|---|---|---|---|---|---|
| Bennu OREX-803001-0 | scored | 20 | −0.02 | 0.67 | 0.27 | 0.11 | −0.28 | −0.44 | −0.09 to 0.11 |
| Ryugu A0106 | scored | 9 | −0.16 | 0.75 | 0.26 | 0.00 | −0.44 | −0.31 | −0.29 to −0.07 |
| Murchison CM2 | exploratory | 20 | 0.25 | 0.17 | 0.51 | 0.46 | −0.65 | −0.44 | 0.13 to 0.34 |

- **Both scored samples meet the sealed kill thresholds** (partial τ ≤ 0.1 and upper bound < 0.4). The script's mechanical verdict is "kill". It is reported as "cannot decide by design" because the declaration came first.
- **How much the kill means.** The power check does say how often the kill thresholds are met by chance when a real effect is present (`results/t2_power.json`):
  - At a planted strength of 0.4 or more: 1.5% of the time for Ryugu and 4.8% for Bennu.
  - At 0.6 or more: 0.3% and 1.5%.
  - So the data argue against a moderate or strong availability effect beyond size in these returned samples. They cannot rule out a weak one (planted 0.2: 7% for Ryugu, 22% for Bennu).
- **Murchison** shows a raw abundance–usage association (τ = 0.46), which is the kind of pattern Higgs & Pudritz built on. Once molecular weight is controlled it falls to 0.25 and is not significant (p = 0.17).
  - Murchison has been curated since 1969, and its L-excesses in Glu, Ser and Thr point to terrestrial contamination (see the prereg).
  - Wehbi et al. already reported that size explains the older consensus order.
- **Reading.** In the two pristine returned samples, amino-acid abundance carries no information about the order of entry into the genetic code beyond molecular size. The test as sealed was too small to call this formally. It would become decidable with more reported Ryugu amino acids (sample C0107 in Parker et al. 2023), or a Bennu protein-amino-acid analysis with lower detection limits.

## Caveats (from the prereg)

- Non-detects dominate Bennu (14 of 20). Under the "ties at the DL" rule, the late, large amino acids (W, Y, F, R, H, K, Q, N) are exactly the non-detects.
- Hot-water extraction loses Asn, Gln and Cys.
- Bennu and Ryugu are both CI-like bodies analysed partly by the same lab, so they are not fully independent tests.
