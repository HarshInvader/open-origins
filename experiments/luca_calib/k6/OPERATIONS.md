# K6 operational notes (no change to method)

These notes change how the work is scheduled on the laptop, not what is computed. The model (LG+F+G4), UFBoot (1,000, `--wbtl`), seed 1, `-T 1`, ALE settings and Moody reweighting are all as sealed in prereg v8 (208991c). Each note was written before the change was used.

## OPS-1 (2026-11-24): 10-family chunks
Commands in this harness are killed after 2 hours. Chunk q_ac (30 families) was killed with 23 of 30 trees done; the driver clears `inferred/` at the start of every batch, so they were lost. The 650 remaining families were re-split into 65 chunks of 10 (`results/k6/chunks10/`), dealt in a snake order by size so large families spread out. A wrapper starts a new chunk only if less than 70 minutes have passed.

## OPS-2 (2026-11-24): large families resume from IQ-TREE checkpoints; finished trees are not thrown away
Chunk c000 was killed with 9 of 10 trees done. The 10th, family 1169 (177 sequences), had not finished after about 2 hours at a laptop load of about 15. No 2-hour unit can hold such a family.
- **Large-family queue.** The 5 remaining families with ≥ 100 sequences (`results/k6/big_families.txt`) leave the chunks. `k6/run_big.sh` runs each with the same IQ-TREE command that `pipeline/infer_trees.py` uses, minus `-redo`, in a persistent directory `results/k6/big/<family>/`. A run cut off by the time limit resumes from IQ-TREE's own checkpoint on the next call. Family 1169's partial checkpoint from c000 is reused.
  - Disclosed: a run resumed from a checkpoint may not give the bit-identical tree set that one uninterrupted run with the same seed would. The method and settings are the same.
- **Salvage.** `k6/ale_from_trees.sh` runs the sealed `pipeline/run_ale.py` on tree files that are already finished and checked, in a side work directory `results/k6/s65_side/`. It then copies the resulting `.uml_rec` files into `s65_run/ale_inferred/uml_rec/`, so the driver skips those families. It is used for c000's 9 finished trees and for the large families once their trees exist. Trees go through `infer_trees.check_trees` (the same leaf-set check) before use.
- The final reweighting still runs once, over every `.uml_rec` in `s65_run`, as the driver's last step.

## OPS-3 (2026-11-26): new laptop, tools restored without rebuilding
The old laptop was replaced. The ALE binaries came across unchanged (sha256 2c5a0c9e... ALEobserve, 261d6ef6... ALEml_undated, as in `ext/ale_build/BUILD_INFO.txt`); only their conda runtime libraries were missing.
- `~/mamba/envs/phylo`: IQ-TREE 3.1.4 (bioconda, MacOS ARM 64-bit), the same version as before.
- `~/mamba/envs/alebuild`: conda-forge libboost 1.85, llvm-openmp, libcxx, so the binaries' rpath resolves as before. micromamba 2.10.0.
- Check: ALEml_undated re-run on the stored smoke family 10 (`results/ale_smoke/sim/ale_true/fams/10/ale_fam_10.ale`) with the pipeline's own arguments (`sample=100 seed=1 separators=_`) gives a byte-identical `.uml_rec`. A first check run without `seed=1` matched the log-likelihood (−19.5308), the ML rates and the per-branch likelihood columns, but not the sampled-reconciliation counts, as expected for an unseeded sampler.
- `~/mamba/envs/phylo` also holds the pipeline's Python stack, pinned as in `k3/setup_remote.sh`: Python 3.11.18, numpy 2.4.6, scipy 1.17.1, ete3 3.1.3, bayesian-optimization 1.4.3, networkx 3.6.1, pyvolve 1.1.0, biopython 1.88.
- The large-family crash limit (DEVIATIONS 11–12) is a property of this arm64 build and still applies here.
