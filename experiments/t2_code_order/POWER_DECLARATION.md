# T2 power declaration (written before `t2_analysis.py real` was run)

The prereg (`docs/prereg/t2_code_order.md`, Fixed decisions) sets two conditions. If either scored sample gives P(kill) < 0.5 at planted strength 0, the kill verdict is unreachable. If either gives P(support) < 0.5 at the strongest planted strength, the support verdict is unreachable. Each unreachable verdict must be declared before the real test runs.

Planted-signal check (`results/t2_power.json`, 400 draws per strength, seed 20261123):

| Sample | n (censored) | P(kill), no signal | P(support), strongest signal (planted 0.8; achieved mean partial τ) |
|---|---|---|---|
| Bennu | 20 (14) | 0.60 | 0.645 (0.45) |
| Ryugu A0106 | 9 (4) | **0.26** | **0.47** (0.65) |

**Declared:** with Ryugu A0106 as printed in Glavin Extended Data Table 2, neither verdict is reachable. T2 as sealed cannot decide. The real test is still run and reported, labelled "cannot decide by design".

**Why.** Only 9 of Ryugu's 20 protein amino acids are reported, and 4 of those 9 are non-detects. Bennu reaches both verdicts more than half the time at these settings, but most of its cells are non-detects too (14 of 20).

**What would make it decidable.**
- More Ryugu amino acids, for example sample C0107 in Parker et al. 2023 (we could not open it: the publisher blocks automated access).
- A dedicated report of the protein amino acids in Bennu with lower detection limits.
