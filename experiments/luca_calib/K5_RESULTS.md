# K5 results: can the pipeline tell a big LUCA from a small one? (prereg v6)

**Sealed verdict: "cannot discriminate in a loosely matched world."**

The small world has a true root of 19-20 families, plus 225-275 families born on the domain stems that crossed between the domains 4-7 times each. ALE with Moody et al.'s root reweighting scored it at 209-229, as large as or larger than a true root of 184-189 (183-206).

The match was loose, so the claim is limited. And with no extra early exchange, a small world could not be made to resemble the big one at all.

Numbers from `k5/k5_report.py` (output `results/k5/k5_report.json`). Tuning: `results/k5/tune/`. Deviations: DEVIATIONS 16. Advice from Fable: `docs/RESEARCH_STATE.md`.

## What ran
- **Seeds:** 1 and 3. Seed 2 was stopped by its sealed planted check: occupancy KS D 0.120 against a critical value of 0.111.
- **Ladder λ ∈ {0, 1, 4}:**
  - λ = 0: unmatched on both seeds. Matching the number of broad families needed 1,700-2,600 stem-born families, and one domain's genomes grew to about 5 times their size.
  - λ = 1: matched on seed 1 only (N = 350), so it is not read.
  - λ = 4: matched on both seeds (s1 N = 225, s3 N = 275). Neither seed is tightly matched:
    - row 5: one domain's mean families per genome is 26% too high (s1 A 171 against 136; s3 B 164 against 130.5);
    - s1 also misses row 6, with 72% more copies per occupied genome;
    - s3 also misses row 3, with 7% more families entering ALE.
- **Realized cross-domain stem transfers per stem-born family:** 6.9 (s1) and 3.97 (s3). The stem transfer rate x is 242 (s1) and 46 (s3), against an ordinary transfer rate of 0.4 per gene. The origination burst on the stems is about 80× (s1) and 28× (s3) the background rate.
- **Positive control:** 200 stemsim root-born families replaced Zombi's in seed 1. R is 1.075, inside 0.95-1.15, so it passes. ALE reconciles stemsim's trees as it does Zombi's.
- **Reproducibility:** re-running seed 1's big-world ALE on this machine reproduced R = 1.0875 exactly.
- **Completion:** 4 of 899 ALE runs failed in s1 λ4, all on stem-born families and none on root families (99.6% complete). Every other world completed fully.

## Results (true gene trees, Linux ALE, O_R refit per world)

| World | True root | ΣPP | R | H (vs big) | Fitted O_R | Prior multiplier | ΣPP: root / stem-born / other | ECE |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| Big s1 (K3) | 189 | 205.5 | 1.09 | 1 | 4.59 | 1.52 | 176.4 / - / 29.2 | 0.021 |
| Big s3 (K3) | 184 | 183.0 | 0.99 | 1 | 4.40 | 1.52 | 162.5 / - / 20.5 | 0.012 |
| Control s1 (N = 0) | 20 | 25.8 | 1.29 | 0.126 | 2.50 | 1.77 | 17.2 / - / 8.6 | 0.010 |
| Control s3 (N = 0) | 20 | 24.3 | 1.22 | 0.133 | 2.39 | 1.58 | 17.5 / - / 6.8 | 0.008 |
| **Small s1, λ = 4** | 20 | **208.9** | 10.45 | **1.016** | 4.57 | 2.64 | 19.0 / 161.1 / 28.9 | 0.211 |
| **Small s3, λ = 4** | 20 | **228.8** | 11.44 | **1.250** | 4.60 | 2.39 | 19.0 / 187.2 / 22.6 | 0.218 |
| Small s1, λ = 1 (not read) | 20 | 248.8 | 12.44 | 1.211 | 4.73 | 2.30 | 19.0 / 198.5 / 31.2 | 0.241 |

**Decision (v6).** λ = 4 is read on both seeds:
- mean H = 1.13 ≥ 0.5, with both seeds on the same side;
- mean R_small − R_ctrl = 9.7;
- neither seed is tightly matched.

So the sealed rule gives "cannot discriminate in a loosely matched world".

## What the numbers say
- **Without stem traffic, the pipeline separates the worlds.** The 20-family control scores 24-26 (H 0.13), and its fitted O_R falls to about 2.4-2.5 from about 4.5.
- **With stem traffic, it does not.** The stem-born families raise O_R back to the big world's value, and ALE assigns them root PPs like real root families. 170 (s1) and 195 (s3) of them reach PP ≥ 0.5.
- **Calibration breaks.** ECE rises from 0.01-0.02 to 0.21-0.22. The posteriors stop meaning what they say in this world.
- **Most of the effect is in the reconciliation, not the weight.** With the flat prior (O_R = 1), the small world still scores 79.0 (s1) and 95.9 (s3), against 135.4 and 120.3 for the big world. That is a flat-prior H of 0.58 and 0.80, against 0.11-0.13 for the controls. The fitted weight then adds the rest.

## Diagnostics read after the verdict (not sealed)
- **Topology split (Fable's "free" follow-up).** Families were grouped by whether the true gene tree's root split separates the domains cleanly. It does not discriminate: even among true root families only 1-2 of 20 have a clean root split, because duplication, loss and transfer blur it. Stem-born and root families look alike: mostly present in both domains without a clean split, mean PP 0.84-0.85 against 0.95-0.98.
- **One-domain families.** Stem-born families whose sampled genes are all in one domain (18-20 per world) still get a mean PP of 0.64-0.75 under the fitted weight. Their summed flat-prior PP is 0.9-1.5 across 18-20 families, under 0.1 each on average. So it is the fitted weight that puts them at the root.

## Limits and objections
- **Strong adversary.** The adversary is strong on purpose. The stem transfer rate is 115-600× background, and the origination burst on the stems is 28-80× background. The result bounds what the method can identify *if* early inter-domain exchange was that intense. It does not show that it was.
- **Part of this is identifiability, built in.** A gene that crossed early to the other domain's stem has the same gene tree as one inherited from the root. No topology-only method can separate the two. What is new here is the size of the effect, at matched phyletic summaries.
- **λ = 0 favours Moody et al.** With ordinary transfer, a small world could not be made to look like the big one. That has equal weight in this report.
- **The match is loose.** N is the only tuning knob, and one domain's genomes come out about 26% too large. This does not by itself give a test on real data, which has no big-world reference, but it weakens the match.
- **Thin evidence.** Two seeds (seed 2 was stopped), true gene trees only, one species-tree shape per seed. Stem-born families come from stemsim, not Zombi; the planted checks and the positive control support that.

## What would make this a headline result (not run)
1. **A realism bound:** how intense the stem exchange would have to be compared with the inter-domain transfer rate Moody et al.'s own reconciliations imply.
2. **A tight match:** a second tuning knob, such as stem-born family size or the domain balance of the stem traffic, under a new prereg, on three or more seeds.
3. **The same test with inferred gene trees.**
