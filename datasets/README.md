# Origin-of-life data, in one place

**Most of the data this field needs is open, but the data that would confirm a route is not.** Reaction databases, returned-sample measurements, LUCA gene families and ribozyme fitness landscapes are public, mostly under CC0 or CC BY. What is missing is the yield and kinetics of each prebiotic step under realistic, unpurified conditions, and any measurement of a replicator that outgrows its own decay. No archive holds these, because nobody has measured them.

`catalog.csv` lists 92 datasets: 13 tables this project made (included here), 67 public sets you can fetch, 2 sample collections on request, and 10 that are reference-only (paywalled, unlicensed or web-only). We opened 86 of them on 2026-11-18 at their DOI, API or landing page; the other 6 are marked `verified=no` with the reason. 21 feed our results today.

## What is here

| Path | What |
|---|---|
| `catalog.csv` | Every relevant dataset, used or not. Columns: `id, title, kind, tier, origin, terms, size, n, labels, serves_tasks, used_by_us, verified, notes`. Tiers: `included`, `fetch`, `request`, `reference-only`. |
| `open/` | 13 tables made by this project (CC BY 4.0). `open/MANIFEST.csv` says where each came from. |
| `fetch.py` | Lists the catalogue and fetches the subsets our results use into `datasets/local/` (git ignores it). |
| `build.py` | Rebuilds `open/` from `experiments/` and `docs/`, and checks `catalog.csv`. |

## Get the data

```bash
python3 -I datasets/fetch.py list               # the catalogue, by tier; * marks sets our results use
python3 -I datasets/fetch.py fetch rhea         # one set we use, as the subset our results need
python3 -I datasets/fetch.py index qt45_dryad   # file list only (Zenodo, figshare, Dryad, remote zip): no data
python3 -I datasets/fetch.py meta ryugu_bennu_ao   # request-tier sets: what it is and how it is requested
```

`fetch` works for `rhea`, `xavier2020_s4`, `daymude_at` and `qt45_zenodo` (the 191 kB quasispecies model only). The whole project has a 1.5 GB download budget, and `fetch` refuses to exceed it. Large deposits are read by HTTP range request where the server allows it. `marshall2021` is the exception: its 9 MB of figure data sits inside a 1.27 GB nested zip, so `fetch` prints manual steps instead.

## The included tables

| File | Rows | What |
|---|---|---|
| `papers_ledger.csv` | 64 | Every cited paper, resolved by DOI, with the claim and what it was checked against. |
| `bench_ledger.csv` | 23 | One row per test from every experiment: statistic, CI, n, pre-registered or exploratory. |
| `pathway_map.json` | 4 routes | Cyanosulfidic, alkaline vent, warm pond and ice-RNA as step tables, with hand-offs, verdicts and ranked gaps. |
| `pathway_handoffs.csv` | 26 | Every hand-off with its verdict and flags under the sealed compatibility rule. |
| `compat_planted_cases.csv` | 28 | The planted cases the compatibility rule had to catch. |
| `qt45_growth_calc.json` | 1 | QT45 net replication per cycle: inputs and growth factors. |
| `raf_planted_results.json` | 1 | Planted autocatalytic cores: recovery, and false-positive rate of each null. |
| `raf_null_observed.json` | 1 | The Xavier 2020 network as we reproduced it, and its maxRAF. |
| `raf_null_sizes.jsonl` | 3,996 | maxRAF size of every null replicate. |
| `luca_planted_grid.csv` | 60 | Planted LUCA recovery: precision and recall per rule and grid cell. |
| `assembly_molecules.csv` | 4,486 | Assembly index, mass, heavy atoms and compression length for Rhea vs GDB molecules. |
| `assembly_mixtures.json` | 25 samples | Marshall 2021 mixtures as we read them. |
| `assembly_results.json` | 1 | AUCs, deltas and CIs for the assembly-index tests. |

`assembly_molecules.csv` has no SMILES column. Half its rows come from GDB, which states no licence. Re-join by id after `fetch.py fetch daymude_at`.

## On request, or reference only

- **Ryugu and Bennu samples** (JAXA Announcement of Opportunity). A proposal is reviewed and samples are lent. NASA's Bennu request pages returned 404 on the day we checked. Only the human lead applies; agents never do.
- **KEGG and MetaCyc** need a subscription for bulk use. Rhea (CC BY 4.0) covers the same ground for our network tests.
- **NOEL and the Wołos 2020 Allchemy network** can be browsed on the web but not downloaded.
- **Weiss 2016, Naraoka 2023, Schmitt-Kopplin 2010** are not open access, and their tables have no open deposit.
- **networkExpansionPy** (Goldford 2019) has no licence in its repository.

## Open, and not yet used

These would help open tasks now:
- **Molecular assembly by mass spectrometry, Zenodo 2026** (`cronin2026_ms`, 4.3 GB, CC BY 4.0). Probably a larger labelled set than Marshall's 25 samples, for #7 and #22. List its zip with `index` first.
- **Bennu and Ryugu instrument data on Astromat** (`bennu_*`, `ryugu_c0378_2026`, all CC0). The Ryugu C0378 set was published on 2026-09-15. Any sealed prediction for #11 or #19 must be hashed before it is read.
- **ChemOrigins** (`chemorigins`, MIT, 194 KB). Curated prebiotic reactions with conditions and sources, for the pathway map (#4, #5).
- **Ribozyme fitness landscapes** (`pressman2019`, `kseq2021`, both CC0). A test bed for the additive and epistatic models of #12 before the QT45 prediction is sealed.
- **Crapitto 2022 consensus LUCA proteome** (`crapitto2022`, CC0) and **Moody 2024 reconciliations** (`moody2024_figshare`, CC BY 4.0) for #10.
- **COCONUT** (CC0) as a second biotic set for #7, and **eQuilibrator** to flag uphill hand-offs in the map.

## Missing, and wanted

The data that would most raise the odds of the 2027 goal, and is not public anywhere:
- Yields and rates for each prebiotic step run on the previous step's crude output, not on purified inputs. This decides R-full conditions 1 to 3.
- Any per-cycle measurement of a replicator whose copies outgrow its decay (L3). QT45 shrinks by about half per cycle on its own numbers.
- QT45 double-mutant fitness. Our prediction (#12) is waiting for it.
- A non-enumerated abiotic reference set: formula lists from meteorite and spark-discharge mass spectrometry (Schmitt-Kopplin 2010 has no deposit).
- A downloadable copy of NOEL or the Wołos 2020 network.
- Harmonised compound-abundance tables for Bennu and Ryugu. The instrument data are open but raw, tens of GB per bundle; the tables sit in paper supplements.
- Any open dataset on vesicles or membranes under prebiotic conditions, and one open compilation of banded-iron and stromatolite records. We found neither.

The early-Earth geochemistry rows (zircons, TTGs, Macrostrat, GEOROC) are listed for the H track. None of them is used yet.
