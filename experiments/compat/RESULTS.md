# Step-compatibility rule: sealed, and the scorer catches the planted incompatible step

**Verdict: done, passes its planted control.** The rule is sealed in `docs/prereg/compatibility_rule.md` (sha256 `bfa572ed574fe6da17482750f4003d338718a856356ad594f2f02bdd8f61dd77`, in `docs/prereg/HASHES.txt`). It was hashed before any pathway was encoded or scored. The scorer flags the planted pH 2 product fed to a pH 10 reaction (F1, nothing else) and gets all 28 planted cases right: 16 of 16 violations raise exactly their expected codes, and 12 of 12 compliant twins raise none.

No real pathway has been scored. That is task #5, which needs the step tables from task #4.

## What the rule says, in one paragraph

Step k+1 may start from what step k leaves only through an ordered list of named physical processes from a closed list of 14 (same pot, mixing with a named scenario stream, evaporation, drying, rehydration, eutectic freezing, heating, cooling, UV, thermophoresis, gas exchange, mineral buffering, selective separation, transport). After the processes are applied, nine hard fails are checked: pH within 1 unit (F1), temperature within 10 °C and inside the scenario range (F2), same solvent (F3), every input produced earlier or supplied by the scenario (F4), concentration at least 1% of what the source used (F5), no purified hand-off without a named separation (F6), only valid processes within their limits (F7), same redox class (F8), same setting or an explicit transport (F9). There are three warnings: an untested carried species above 10% of the main input (W1), concentration between 1% and 10% of what the source used (W2), and a separation claimed without a source that demonstrates it (W3). A pathway counts as continuous only with zero hard fails and no step lacking a yield. The 1000-fold concentration cap and the tolerances are our own conventions, chosen to be generous, not literature values.

## Numbers

| Case set | n | Correct |
|---|---|---|
| Planted violations (F1-F9, W1-W3, plus extra F7 variants) | 16 | 16 |
| Compliant twins and baseline | 12 | 12 |
| **The planted pH 2 -> pH 10 hand-off (`same_pot`)** | 1 | flagged F1 only: "F1 pH 2 after hand-off, step needs 10" |
| Its twin: mixing with a pH 12 scenario stream, f = 0.5, pH 10 after | 1 | no flags |

Per-case detail: `planted_cases.csv`. Summary: `results.json`.

## One correction made during the run (to a test case, not to the rule or scorer)

The first run scored 27 of 28. The case "mixing claims a pH outside the [pot, stream] range" was expected to raise only F7, and it raised F7 and F1. The scorer behaved correctly: an invalid process is not applied, so the pot stays at pH 7 while the step needs pH 13, which is also an F1. I changed that case's expected flags to {F7, F1}. The rule file and scorer were not touched.

## Implementation choices the rule leaves open (stated so a red team can attack them)

- After `mixing` with f ≥ 0.5, the pot takes the stream's solvent and redox class. With f < 0.5 it keeps its own, unless the pot is dry.
- If `mixing` gives no `ph_after` or `t_after`, the scorer uses a linear volume-weighted value. This is a crude stand-in, not chemistry. Real tables should state the pH after mixing.
- Species carry forward through every hand-off, and consumption of inputs is ignored. This favours continuity (generous).
- Feedstocks count at their scenario concentration in every setting.
- Step 1 inputs are checked against the scenario feedstocks (F4, F5, F6) and its setting against the scenario (F9). This is reported as hand-off "entry->1".

## Not checked

- Kinetics, side reactions or decomposition during a hand-off. The rule is about conditions only; "topology is not kinetics".
- Whether a scenario's streams and minerals are geologically plausible. That belongs to whoever writes the scenario table in task #4, with sources.
- Real pathways. None exist in the repo yet.

## Files

- `docs/prereg/compatibility_rule.md`: the sealed rule, including a JSON parameter block that the scorer reads.
- `experiments/compat/scorer.py` (sha256 `fddb713f...452b999ffb`): refuses to run if the rule's hash is not in HASHES.txt.
- `experiments/compat/planted.py` (sha256 `25e3c74c...e8f4802c7`): the 28 planted cases. Run it with `.venv/bin/python -I experiments/compat/planted.py`; it takes under a second.
- `results.json`, `planted_cases.csv`, `ledger_rows.csv`.

## Hypotheses

| Hypothesis | Test | Result |
|---|---|---|
| The scorer flags a pH 2 -> pH 10 hand-off with no named process | planted case | yes (F1 only) |
| The scorer does not flag the same hand-off when a valid named process connects it | twin | yes (no flags) |
| Each rule clause is sensitive and specific on planted cases | 28 cases | 28/28 |

No citations are used in this task.
