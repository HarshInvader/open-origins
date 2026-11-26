# K7 full planted test on free GitHub-hosted Linux runners

Approved by the coordinator on 2026-11-26, at no spend. The workflow is `.github/workflows/k7_planted.yml`. It is triggered manually only and uses no secrets. Each job checks the code hashes in `code.sha256` before it does anything else.

## Why a runner
The prereg asks for the Linux ALE build. The laptop's arm64 build overflows on large families (luca_calib DEVIATIONS 11–12). AWS has about $1 left until 1 December.

## Inputs (`inputs/`, about 0.6 MB, our own simulated data)
- **Seed 1** (K2 n80_t0.4, the source K5 read): `config.json`, Zombi `T/Events.tsv`, and the sampled species tree, domains and truth table. It also holds the true trees of the 700 kept background families with at least 2 genes (`kept_true_trees.tgz`). The Linux reconciliations of these families were made on AWS and never copied back, so the runner re-runs them (prereg: "present or re-run").
- **Seed 3** (K3, made on AWS): only `sample/` and the Linux `ale_true` came back. The species-tree step (Zombi T, seeded) was re-run on the laptop with K3's exact settings. The sampled species tree and domains it gave are byte-identical to the stored ones, and the same re-run for seed 1 reproduces its stored `Events.tsv` and `config.json` byte for byte. `background.jsonl` was parsed on the laptop from the stored Linux reconciliations (769 families, none missing).
- **`alecheck/`**: 12 seed-3 source families, chosen with a fixed seed, plus the sha256 of their stored AWS Linux `.uml_rec` files.

## Checks, in order
1. `code.sha256`: the K7 scripts and the imported `stemsim.py`, `run_ale.py`, `common.py` and the CMake shim, as committed.
2. `alecheck`: the runner's ALE (commit b59dfaf3, Ubuntu 24.04 apt Boost, the same platform as the K3 AWS build) must reproduce the 12 stored reconciliations byte for byte (`seed=1`). Otherwise the whole run stops before any rung.
3. Every rung job rebuilds its world from `inputs/` and must match the laptop build: `families.json`, `S.nwk` and a digest of every tree file (`expected_build.sha256`).

## Jobs
`build-ale`, then `alecheck`, then `bg1` together with the 10 rung jobs (seed × m ∈ {1, 10, 50, 150, 600}, N = 250, no size cap), then `report` per seed.
- Each job is far inside the 6-hour limit. The largest is about 1 core-hour on 4 vCPU.
- A job that fails is re-run whole; seeds are fixed, so it gives the same records.
- The artefacts are compact JSONL records and `report_s{1,3}.json`. No ALE files are kept.
