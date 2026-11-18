# Pre-registration: planted LUCA recovery on simulated trees (board task #9)

Agent: orig-2. Written 2026-11-18, before any simulation was run.

## Question
How well do LUCA-calling rules recover a planted ancestral gene set when genes are lost and horizontally transferred between and within domains? The rules are gene-tree-free analogues of the criteria in Moody et al. 2024 (Nat Ecol Evol 8:1654, doi:10.1038/s41559-024-02461-1, verified) and Weiss et al. 2016 (Nat Microbiol 1:16116, doi:10.1038/nmicrobiol.2016.116, verified via docs/PAPERS.csv).

This is a simulation; there are no real data. It is the planted-answer gate that task #10 (robustness scan on Moody's data) depends on.

## Rates
Moody et al. do not state numeric per-family duplication, transfer and loss rates in the main text (I checked the PMC11383801 full text). So rates are a pre-set grid, not "published rates":
- loss μ ∈ {1, 2} expected losses per lineage per root-to-tip depth;
- transfer ratio τ/μ ∈ {0, 0.1, 0.3, 1, 3}.

Duplication does not change presence or absence, so it does not affect presence-based rules. It is left out, and this is stated as a limitation.

## Simulation
- **Species tree:**
  - root with two domain stems (A and B);
  - each domain is a Yule crown tree with 32 tips, crown age 0.8 of root-to-tip depth 1;
  - one new tree per replicate.
- **Families:**
  - 500 planted LUCA families present at the root;
  - 1,500 later families, each originating at a uniform random point on the tree's total branch length.
- **Dynamics, in discrete time with dt = 0.002:**
  - per lineage that carries the family: loss with probability μ·dt;
  - transfer with probability τ·dt, to a uniformly random contemporaneous lineage in either domain, which then carries it.
- Families absent from all tips are unobservable and are dropped.
- The truth set is the observable planted LUCA families.
- 10 replicates per grid cell, seeds 0-9.

## Rules tested
- **R1 "both domains"** (Moody's sampling requirement at our tip count): present in ≥ 1 tip of each domain.
- **R2 "Weiss breadth"**: present in ≥ 2 tips of each domain, in ≥ 2 different subclades (children of the crown root) within each domain.
- **R3 "ML ≥ 0.75"**:
  - model: a two-state gain/loss continuous-time Markov chain on the true species tree, with shared gain rate, loss rate and root frequency fitted by maximum likelihood, conditioned on observability;
  - call: posterior P(present at root) ≥ 0.75.
- **R4**: R3 plus R1, mirroring Moody's most stringent category.
- **R5**: posterior ≥ 0.5.
- **R6 "Weiss oracle"**: R2 plus each domain's copies being monophyletic in the true gene history (no surviving inter-domain transfer). This is an upper bound for gene-tree methods.
- **Size estimate**: Σ posterior over all observable families, compared with the true count. This mirrors Moody's genome-size integration.

## Outputs per grid cell
- precision and recall of each rule (mean and SD over replicates);
- relative error of the size estimate.

## Pass marks, fixed in advance
- A rule is "validated" in a cell if mean precision ≥ 0.8 and mean recall ≥ 0.5.
- The size estimate is "validated" if mean |relative error| ≤ 20%.
- **Decisive output:** the largest τ/μ at which R4 (the Moody-like rule) stays validated.
- **Prediction:** precision of the presence rules R1/R2 falls below 0.8 once τ/μ ≥ 0.3. R3/R4 do better, but the size estimate is biased upward under transfer, because the gene-tree-free model reads transfers as presence.

## Caveats
- ALE uses gene trees; these rules do not, except R6. So this bounds the behaviour of simpler, gene-tree-free rules plus an oracle.
- It does not reproduce ALE.
