# Brief for every agent on this project

Repo: `.`. Python: `.venv/bin/python` (create with `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`). Chemistry uses RDKit; networks use networkx; phylogenetics only on subsets that fit the laptop.

Goal: see `README.md`. We test origin-of-life theories by what they predict, score each proposed pathway step by step, and seal predictions that future data can confirm. Possible is not historical: never present a working route as what happened.

## Data
`docs/DATASETS.md` lists each source with its access route and licence: Rhea, ModelSEED, BiGG, eQuilibrator, the Moody 2024 LUCA supplement, the QT45 deposit, the Bennu supplements, PubChem and the Open Reaction Database. KEGG and MetaCyc bulk data are licensed, so check terms first and do not use them otherwise.

## Rules of evidence (non-negotiable)
1. **Citations are verified or marked.** Every paper you cite has a DOI you opened. Otherwise write "(unverified)". Agents invent references, and an invented one on the site is the worst failure this project can have.
2. **Pre-register.** Write the prediction, test and pass mark in `docs/prereg/<name>.md`, and append its sha256 to `docs/prereg/HASHES.txt` before looking.
3. **The compatibility rule is fixed.** Score pathway steps only under the hashed rule in `docs/prereg/compatibility_rule.md`. Do not adjust it to rescue a favoured route.
4. **Nulls that respect the data:**
   - degree-preserving randomised networks and random food sets of equal size for RAF and network expansion;
   - mass- and size-matched controls for assembly index;
   - phyletic patterns shuffled at matched breadth for LUCA.
5. **Planted answer first.** A method must recover a planted autocatalytic core, a planted ancestral gene set or a planted landscape fraction at our sample size before its real output counts.
6. **Yields come with conditions.** Record pH, temperature, concentration, purification and the source for every step. A step that starts from purified reagents is marked as such.
7. **Power and multiple tests.** Give the detectable effect size for each negative, and add one ledger row per test.
8. Write plainly. Lead with the conclusion.

## Output
Work in `experiments/<area>/` and give each area a `RESULTS.md`:
- the verdict first;
- numbers, nulls, CIs;
- what was not checked;
- a hypotheses table.

Also write `results.json` and `ledger_rows.csv` in the same folder. Do not edit other agents' folders. Do not git commit.
