# Pre-registration: the step-compatibility rule

Author: agent orig-1. Date: 2026-11-18. Board task #3 (M2).
Status: sealed. The sha256 of this file is in `docs/prereg/HASHES.txt`. It was hashed before any pathway was encoded or scored (task #4 had not started; no step table existed in the repo).

## What this rule decides

Whether step k+1 of a pathway can start from what step k leaves behind, in the same scenario, using only named physical processes. It does not decide whether a step works (that is the step's published yield) or whether the pathway is fast enough (that is kinetics, a separate test). It is fixed: no one may change it to rescue a route. A changed rule is a new file with a new hash, and every pathway must then be rescored under both.

## The records it needs

**Scenario.** Name; allowed temperature range; settings (for example `surface_pool`, `vent_chimney`, `ice`); whether UV is present; redox class of the environment (`reducing`, `neutral`, `oxidizing`); a list of feedstock species with concentration (M); a list of named fluid streams (pH, T, solvent, redox class, species and concentrations); a list of named minerals with their buffered pH range.

**Step.** Id; setting (must belong to the scenario); required inputs, each with the concentration the source used (M) and a flag `purified` (true if the source started from an isolated or commercial sample of that input); conditions (pH, T in °C, solvent, redox class); outputs with concentration (M) and the pH, T, solvent and redox class at the end of the step; `tested_with` (species the source showed the step tolerates); a yield label (`demonstrated`, `demonstrated_purified`, `missing`) and a source.

**Hand-off** from step k to step k+1: an ordered list of processes, each from the closed list below, with its parameters.

## Closed list of physical processes

Only these. Anything else is a hard fail (F7).

| Process | What it may change | Limits |
|---|---|---|
| `same_pot` | nothing | |
| `mixing` | pH, T, solvent, redox, concentrations | needs a named scenario stream and volume fraction f in (0,1); carried species × (1−f); stream species × f; the new pH must lie between the old pH and the stream pH (inclusive); same for T |
| `evaporation` | concentrations of non-volatile species | concentration factor ≤ 1000; species marked volatile are removed; pH may move by at most 1 unit more |
| `drying` | solvent becomes `dry` | non-volatile species kept as solid; the next step must be `dry` or be preceded by `rehydration` |
| `rehydration` | solvent, concentrations | as `mixing` with a named stream |
| `freezing_eutectic` | T, concentrations | T to a value in [−30, 0] °C and inside the scenario range; concentration factor ≤ 1000 |
| `heating` / `cooling` | T | any T inside the scenario range |
| `uv_irradiation` | nothing in conditions | only if the scenario has UV |
| `thermophoresis` | concentrations | factor ≤ 1000; only in settings with a stated thermal gradient (`vent_chimney`, `porous_rock`) |
| `gas_exchange` | pH, redox | pH may move by at most 2 units; redox may become the scenario's own class |
| `mineral_buffering` | pH | the new pH must lie in the named scenario mineral's buffered range |
| `selective_separation` | removes or isolates a named species | must name the species and the physical property (crystallisation, adsorption, volatility); counts as a pass only with a `demonstrated_by` source showing that separation, otherwise W3 |
| `transport` | setting | moves material between two settings of the same scenario; concentrations × a stated dilution factor ≤ 1 |

The concentration caps (1000-fold) and tolerances below are conventions set by this project in advance, not literature values. They are deliberately generous so that a fail means a real gap.

## Tests, applied after the processes have been applied in order

Hard fails (each stops the hand-off counting as continuous):

- **F1 pH.** |pH after hand-off − pH step k+1 needs| > 1.0.
- **F2 temperature.** |T after hand-off − T needed| > 10 °C, or T needed is outside the scenario range.
- **F3 solvent.** Solvent after hand-off differs from the solvent needed.
- **F4 missing input.** A required input is neither produced by an earlier step of this pathway (carried forward through every hand-off since) nor a scenario feedstock or stream species.
- **F5 concentration.** Available concentration < 0.01 × the concentration the source used.
- **F6 purified hand-off.** A required input has `purified: true` and the hand-off has no `selective_separation` for that species.
- **F7 process.** A process is not on the closed list, lacks its required parameters, breaks a limit in the table, or is not available in the scenario or setting (for example UV in a vent, thermophoresis in a pool).
- **F8 redox.** Redox class after hand-off differs from the class step k+1 needs.
- **F9 setting.** Step k+1's setting differs from step k's and there is no `transport`, or a setting is not part of the scenario.

Warnings (scored and reported, not fails):

- **W1 untested interference.** A carried species that is not a required input is present at more than 10% of the molar concentration of the main (first-listed) required input and is not in `tested_with`.
- **W2 thin concentration.** Available concentration is between 0.01× and 0.1× the concentration the source used.
- **W3 claimed separation.** A `selective_separation` without a `demonstrated_by` source. It clears F6 but is reported.

## Step-level labels (rule 6 of the agent brief)

Each step also gets its yield label: `demonstrated` (a lab other than us reported a yield under these conditions from unpurified inputs), `demonstrated_purified` (reported, but from purified inputs) or `missing`.

## Pathway score

For each pathway: number of hand-offs, number with any hard fail, number of warnings, number of `demonstrated_purified` steps, number of `missing` steps. A pathway is **continuous** under this rule if and only if it has zero hard fails and zero `missing` steps. The ranked gap list (task #5) sorts pathways by hard fails, then missing steps, then purified steps, then warnings.

## Planted controls the scorer must pass before it scores anything real

On a toy scenario with made-up species (so no real chemistry is implied):

1. A three-step baseline pathway with every hand-off compatible scores zero flags.
2. **The planted incompatible step:** a step whose output is at pH 2 feeds a step that needs pH 10 through `same_pot`. The scorer must flag F1 on that hand-off and nothing else.
3. Its control: the same hand-off through `mixing` with a scenario stream at pH 12 (f = 0.5, target pH 10 inside [2, 12]) must not flag F1.
4. One planted violation per other code (F2–F9, W1–W3), each with a compliant twin. Each violation must raise exactly its own code; each twin must raise none.

Pass mark: all planted cases give exactly the expected flags (sensitivity 1 and specificity 1 on the planted set). If any case fails, the scorer is fixed and rerun; the rule above does not change.

## Machine-readable parameters

The scorer reads this block and refuses to run if this file's sha256 is not in `HASHES.txt`.

```json
{
  "rule_version": 1,
  "ph_tolerance": 1.0,
  "t_tolerance_c": 10.0,
  "conc_fail_ratio": 0.01,
  "conc_warn_ratio": 0.1,
  "interference_ratio": 0.1,
  "max_concentration_factor": 1000.0,
  "evaporation_extra_ph_shift": 1.0,
  "gas_exchange_max_ph_shift": 2.0,
  "freezing_t_range_c": [-30.0, 0.0],
  "thermal_gradient_settings": ["vent_chimney", "porous_rock"],
  "processes": ["same_pot", "mixing", "evaporation", "drying", "rehydration", "freezing_eutectic", "heating", "cooling", "uv_irradiation", "thermophoresis", "gas_exchange", "mineral_buffering", "selective_separation", "transport"],
  "hard_fails": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"],
  "warnings": ["W1", "W2", "W3"]
}
```
