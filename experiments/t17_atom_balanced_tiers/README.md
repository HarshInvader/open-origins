# T17: do KEGG biochemistry's nested autocatalytic tiers survive an atom-conserving null?

Status: **sealed 2026-11-25T11:26:40Z** (prereg, scripts, gate, planted and the KEGG id list in `docs/prereg/HASHES.txt`). Blind dry run 21 of 28 parts done (Null A draws 25-200 missing); `dryrun_verdict` and `real` have not run, so no null of the real network has been scanned. The old laptop's runner stopped on 2026-11-25; the run resumes on the new laptop with the same arguments (prereg F2). Prereg: `docs/prereg/t17_atom_balanced_tiers.md`. Design: section "U1" of `docs/NEW_STUDIES_2026-11-25.md`.

## Question

T14 (sealed, support) found that degree-preserving rewires of the KEGG-derived network of Peng, Linderoth & Baum 2022 give one autocatalytic set and no nesting, where the real network has three nested sets. But T14's rewired reactions do not conserve atoms. T17 repeats the test with nulls in which every rewired reaction balances every element, using KEGG molecular formulas. If the tiers survive, they are a feature of which balanced reactions biology uses. If not, atom bookkeeping alone gives tiers.

## Layout

- `scripts/t17_fetch_kegg.py`: downloads the KEGG COMPOUND entries for the 4,216 species (422 calls of 10 ids, at least 0.5 s apart, generic User-Agent). Output in `raw/kegg/` (gitignored; KEGG data are not ours to republish).
- `scripts/t17_analysis.py`: modes `gate`, `planted`, `planted_merge`, `sealcheck`, `dryrun`, `dryrun_verdict`, `real`, `real_verdict`. It imports the sealed T14 script (`experiments/t14_autocatalytic_tiers/scripts/t14_analysis.py`, sha256 checked) for loading, expansion, scan, LP and the synthetic generator. `real` refuses unless `docs/prereg/HASHES.txt` names the script with its current sha256.
- `scripts_out/`: `t17_gate.json`, `t17_planted.json` and the planted parts.
- `work/` (gitignored): logs and, later, the blind dry-run draws.

## Run

From `experiments/`, single-threaded under `nice -n 20`, with the project venv:

```
python -I t17_atom_balanced_tiers/scripts/t17_fetch_kegg.py t17_atom_balanced_tiers
python -I t17_atom_balanced_tiers/scripts/t17_analysis.py t17_atom_balanced_tiers gate
python -I t17_atom_balanced_tiers/scripts/t17_analysis.py t17_atom_balanced_tiers planted sparse_planted 0 10
```

See the prereg for the gate and planted results and for how `real` will be run after the seal.
