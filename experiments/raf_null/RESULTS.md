# The 1,335-reaction RAF in anaerobic metabolism is no larger than its nulls give: negative

**Verdict: within null (pre-registered rule), and the claim fails the test.** We reproduced the published maxRAF exactly from the authors' own file. It is not larger than what the network's degree structure and food-set choice produce:

- **Degree-preserving rewiring (N1, decisive):** rewired copies of the network, with the same food set, have maxRAFs of 3,394 to 3,583 reactions (95% range; median 3,495). The real network's maxRAF is 1,357, far *below* that range (lower p = 0.001). Real metabolism wired this way is less autocatalytic than random wiring with the same degrees, not more.
  - **Caveat added 2026-11-26 (from T17).** The last sentence of this bullet is now doubtful. This rewiring preserves degrees but not atom balance, so most rewired reactions are chemically impossible, and that was known to inflate structural statistics long before we used it (Basler et al. 2011, doi:10.1093/bioinformatics/btr145, which reports 99.8% of reactions unbalanced after switch randomisation; Samal & Martin 2011, doi:10.1371/journal.pone.0022295). T17 (`experiments/t17_atom_balanced_tiers/T17_RESULTS.md`) found that a comparable degree null made a KEGG hierarchy look special when an atom-balanced null did not. Chemically impossible reactions are unconstrained in what they may produce, which plausibly inflates a maxRAF, so **"real metabolism is less autocatalytic than random wiring with the same degrees" is withdrawn as a reading** pending an atom-balanced re-run. The N1 numbers stand as computed. The verdict of this study does not rest on N1: it rests on N3m, the degree-matched random food set, where the real value sits inside the range, and that null does not rewire reactions at all.
- **Degree-matched random food of equal size (N3m, decisive):** 95% range 705 to 1,403, median 1,073. The real 1,357 is inside the range (upper p = 0.064).
- **Catalyst assignments shuffled on the real substrate network (N2, descriptive):** 95% range 1,308 to 1,748, median 1,521. The real value is inside (upper p = 0.92).

Under the rule sealed before the run (`docs/prereg/raf_null_xavier2020.md`, sha256 `22e3ab3f...9762053`), the verdict is **"within null"**: the observed value lies inside the 95% range of at least one decisive null. There is no evidence here that the RAF is more than an artefact of network size, degree structure and food choice. That is the riskiest prediction for the autocatalytic-set theory in `docs/fable_plan.md` §3.

What this does *not* say: it does not say the network has no RAF, or that RAFs played no role. A RAF of this size exists in the real network, as it would in most networks with these degrees and this food set.

## Claim and data

- Xavier, Hordijk, Kauffman, Steel & Martin 2020, "Autocatalytic chemical networks at the origin of metabolism", Proc R Soc B 287:20192377, doi:10.1098/rspb.2019.2377. Verified: I opened the Crossref record and the Europe PMC full text (PMC7126077). They report a maxRAF of 1,335 reactions, 25% of the anaerobic network, when all organic cofactors are in the food set.
- Data: their supplementary dataset S4 (`raw/rspb20192377supp5.txt`, CC BY 4.0, from the Europe PMC supplementary-files endpoint). The paper describes it as the prokaryotic O2-independent network with the food set of small molecules, abiotic carbon and organic cofactors. It has 6,039 reactions (3,192 reversible), 5,740 molecules and a 68-molecule food set, with catalysts given as AND/OR expressions. It is KEGG-derived and was redistributed by the authors; we downloaded nothing from KEGG. Total download: 4 MB.
- Rhea and ModelSEED were not used. The task allowed them, but the authors' own deposited network is the claim as published. A Rhea-built network is a follow-up (see below).

## Reproduction

Our maxRAF is 1,357 reactions. That is inside the pre-registered 2% tolerance (1,308 to 1,362). 22 of those reactions are "Pooling" bookkeeping reactions (they map, for example, each flavin to a "Flavins" token). Without them the count is exactly **1,335**, the published number. The algorithm is the Hordijk & Steel 2004 reduction (doi:10.1016/j.jtbi.2003.11.020, verified via Crossref), extended to AND/OR catalysis and reversible reactions. On small random networks it agrees with brute-force enumeration in 300 of 300 cases (`cnet.py`).

## Numbers (999 replicates per null)

| Null | Role | Null median | 95% range | Observed | p upper | p lower | Outcome |
|---|---|---|---|---|---|---|---|
| N1 degree-preserving rewiring | decisive | 3,495 | 3,394-3,583 | 1,357 | 1.000 | 0.001 | below |
| N3m degree-matched random food | decisive | 1,073 | 705-1,403 | 1,357 | 0.064 | 0.938 | inside |
| N2 catalyst shuffle | descriptive | 1,521 | 1,308-1,748 | 1,357 | 0.917 | 0.086 | inside |
| N3 uniform random food | descriptive, invalid | 3 | 0-34 | 1,357 | 0.001 | 1.000 | above (meaningless) |

- **Gate (task #8, `experiments/raf/RESULTS.md`).** N1 and N3m passed the pre-registered gate, so both are decisive. N3 failed it: on synthetic networks with nothing planted, its false-positive rate was 18/20 and 20/20. Its "above" result here is the same artefact. A real food set of hubs and cofactors always beats a random draw, so it is no evidence of anything.
- **Power.** The N3m result is not a power failure. A maxRAF of 1,404 or more (3.4% above observed) would have been flagged. Nor is the N1 result: the observed value is 2,037 reactions below the null's lower bound. Effect sizes are (obs − median)/IQR = −33.7 for N1 and +1.1 for N3m.
- **Caveat on N3m, disclosed in task #8.** On synthetic networks, N3m never flagged a planted core and tended to put the real value low. Here the real value sits in its upper tail (p = 0.064). N3m is biased against an "above" result, so a borderline "inside" under N3m is weak evidence on its own. The decisive and robust part of the verdict is N1. N2 agrees: random catalyst assignment on the real substrate network gives maxRAFs as large as or larger than the real ones.
- Nulls held the 45 Pooling reactions and every clause containing "Pooling" or "Spontaneous" fixed, as pre-registered.

## Reading

The 1,335-reaction RAF is a property of a network with these degrees and this food set: hubs plus a cofactor-rich food set. Real wiring makes it smaller than random wiring, plausibly because modern metabolism has long linear and branched pathways that a degree-preserving shuffle turns into shortcuts. Real catalyst assignments do no better than random ones. The paper's qualitative conclusion, that small-molecule catalysts and cofactors in the food set produce large RAFs, is consistent with our numbers. But the size of the RAF is not evidence that metabolism carries a special autocatalytic signature. Topology is not kinetics either way.

## Not checked

- A Rhea-derived anaerobic network built independently of KEGG. This would test whether the result depends on the database (follow-up task).
- The other food sets in the paper (metals and CO2 only, the LUCA-cofactor set) and the acetogen and methanogen networks (datasets S1 and S2 are in `raw/` but were not used).
- Food-set nulls that match molecule roles (catalyst degree and substrate degree separately). N3m is the best we had, and it has known bias.
- Whether the maxRAF contains a smaller core that is itself non-random. The size test cannot see cores under about 30% of the background (task #8).

## Files

`load.py` (parser), `cnet.py` (maxRAF with AND/OR catalysis, nulls), `run_null.py` (refuses to run unless the pre-registration hash is listed), `null_sizes.jsonl` (3,996 rows), `observed.json`, `summarize.py`, `results.json`, `ledger_rows.csv`, `raw/` (Xavier et al. supplementary files, 3.4 MB). Run: `board/run.sh .venv/bin/python -I experiments/raf_null/run_null.py`, with Pool(2).

## Hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| Our code reproduces the published maxRAF | dataset S4 | yes: 1,335 excluding Pooling (1,357 with them) |
| maxRAF is above degree-preserving rewired networks | N1 | no: far below (1,357 vs 3,394-3,583) |
| maxRAF is above degree-matched random food sets | N3m | no: inside (upper p = 0.064) |
| Real catalyst assignment gives a larger RAF than random | N2 | no: inside (upper p = 0.92) |
