# T13 result: one global curve does not find the distant neutral ligases, and neither does a network by much; sealed verdict "partly"

Prereg: `docs/prereg/t13_ligase_global_epistasis.md`, sealed in 0321f9b (`HASHES.txt`). Script: `scripts/t13_analysis.py` (sha256 f8d20c02…). Output: `scripts_out/t13_real.json`.

## Claim

Rotrattanadumrong and Yokobayashi 2022 (Nat. Commun. 13:4847, doi:10.1038/s41467-022-32538-z) evolved a ligase ribozyme with a genetic algorithm and a neural network (MLP), over generations 1 to 8. They write:

> "In generation 8, almost all neutral mutants identified were expected to be deleterious under the epistasis-free model. This indicated that the neural network was able to learn higher-order, nonlinear mutational effects".

Their "epistasis-free" model multiplies the single-mutant activities. Far from the wild type (Hamming distance 6 to 19), that drives every prediction toward zero. A model with no specific interactions at all can predict quite differently there. That model is one additive score per mutation passed through one saturating curve, called model G. The question is whether model G, trained on generations 1 to 6 only, finds the generation 8 neutral variants about as well as models with interactions:
- **GP:** G plus pair terms.
- **A rebuilt MLP.**

The rules:
- **Kill:** G recalls at least 80% of the measured generation 8 neutral variants, *and* the better interaction model beats it by at most 0.05 average precision (AP).
- **Support:** the lift is at least 0.10.

## Gate (passed before the seal)

The authors' split was reproduced exactly: 20,920 training variants and 8,967 test variants. The generation 8 neutral fraction is 0.279; the paper gives 0.28. The multiplicative model calls 0.3% of the generation 8 neutral variants neutral, which reproduces "almost all … expected to be deleterious". The replicate ceiling is AP 0.997 and recall 0.845.

## Sealed verdict: partly (neither kill nor support)

| Generation 8 (n = 11,960, 27.9% neutral) | AP | Recall of neutral variants |
|---|---|---|
| Null (labels shuffled within Hamming-distance bins) | 0.378 | – |
| Authors' multiplicative model | 0.403 | 0.003 |
| **G: one global curve** | **0.467** | **0.001** |
| GP: curve plus pair terms | 0.423 | 0.017 |
| Rebuilt MLP | 0.516 | – |
| **Lift** (best interaction model − G) | **+0.049** | |

- **Kill fails on recall.** The global curve, fitted on generations 1 to 6, calls almost none of the generation 8 neutral variants neutral (0.1%). It fails as completely as the authors' multiplicative model. So the paper's specific point stands: an additive model, even with a global nonlinearity, would not have found these variants.
- **Support fails on lift.** The network does better than G, but only by 0.049 AP, which is below the 0.10 support line. Every model trained on generations 1 to 6 ranks generation 8 only a little better than the distance-matched null: the best is 0.52 against 0.38.

## Reported only (no rule)

| Set | AP of G / GP / MLP | Null | Recall of G | Lift |
|---|---|---|---|---|
| Held-out generations 1–6 (n = 8,967) | 0.853 / 0.739 / 0.933 | 0.203 | 0.80 | 0.080 |
| Generation 7 (n = 11,976) | 0.939 / 0.929 / 0.974 | 0.786 | 0.80 | 0.035 |

- Near the training data, the global curve works well. It recalls 80% of neutral variants, near the replicate ceiling of 0.845, and the network adds less than 0.10 AP.
- Pair terms (GP) do *worse* than G everywhere. With 467 pair terms they overfit, so this study gives no sign that pairwise epistasis helps prediction.
- The plan's rule as written also gives "partly".

## Reading

- **What it shows.** The authors' generation 8 inference has two parts.
  - "The additive model would have called these dead" holds, even when the additive model gets a global curve. Generation 8 sits far outside what generations 1 to 6 can inform through any additive score.
  - "So the network must have learned higher-order effects" is only weakly supported. Our network, trained on the same data, ranks generation 8 slightly better than the curve (+0.05 AP). Neither predicts these variants well.
- **The selection effect.** The generation 8 variants were chosen by the authors' own network, so a network is favoured on exactly these rows (prereg limit 4). Even so, the lift is small.
- **What it does not show.** The test cannot see third-order structure: in planted runs it gave "partly" every time. "Partly" is therefore compatible with the authors' own Walsh-Hadamard finding that third-order terms are needed. It is also compatible with a curve that simply extrapolates badly.

## What it means for us

- **Comparison with QT45 (#30).** There, one global curve explained almost everything and pair terms added nothing. Here the curve explains the near neighbourhood just as well (generations 1 to 7), but fails far from the training data. So "one global curve suffices" is a local statement for both ribozymes. Whether anything simple works at Hamming distance 10 or more remains open.
- **For the replicator-first route,** neutral networks of a ribozyme reach far, but how they reach that far is not yet predictable from local data by any model tested here, including a network.

## Correction to the sealed PRIOR_ART.md

`PRIOR_ART.md` gives the Faure & Lehner 2024 paper the title "The genetic architecture of biomolecular phenotypes". Its actual title, per Europe PMC metadata for PMC11161127, is "An extension of the Walsh-Hadamard transform to calculate and model epistasis in genetic landscapes of arbitrary shape and complexity". The authors are Faure, Lehner, Miró Pina, Serrano Colome and Weghorn (PLoS Comput. Biol. 20:e1012132, doi:10.1371/journal.pcbi.1012132). The sealed file is left unchanged so that its hash still matches. The library entry uses the correct title. The error does not affect the test.
