# T7 result: evaporating Yellowstone waters rarely opens a joint vesicle-and-RNA window, but too rarely to call a kill

Prereg: `docs/prereg/t7_evaporation_window.md`, sealed in 32876f0 (`HASHES.txt`). Script: `scripts/t7_analysis.py`. Output: `results/t7_real.json`. Model: PHREEQC 3 (phreeqpython 1.6.2) with `pitzer.dat`.

## Question (Route 6, lipid / compartment first)

Pond scenarios rely on evaporation to concentrate solutes. Can an evaporating hot-spring water reach the Mg needed for nonenzymatic RNA copying (1–4 mM) while it is still inside the fatty-acid / mixed-amphiphile vesicle window? That window is Ca ≤ 1.9 mM, Na + K ≤ 600 mM and pH 6.5–12. Calcite, gypsum and silica form along the way, so linear scaling is not enough. T4 found that raw waters almost never qualify; T7 follows their evaporation paths.

## Sealed verdict: inconclusive, for both sets

| Set | Arm | Passing rows | S (99% interval) | Verdict |
|---|---|---|---|---|
| USGS thermal water (decision) | mixed | 15 of 528, in 6 of 37 areas | **2.8%** (0.3, 9.4) | inconclusive |
| USGS | pure fatty acid | 3 of 528, in 3 areas | 0.6% (0, 2.4) | not reported as a kill |
| Historic thermal water (replication) | mixed | 10 of 749, in 5 of 34 areas | 1.3% (0.1, 7.3) | inconclusive |
| Historic | pure fatty acid | 1 of 749 | 0.1% (0, 1.2) | not reported as a kill |

- **Mixed arm.** The estimate is below the 5% bar, but the upper bound (9.4%) is above it. Kill needed the upper bound under 5%. Support needed the lower bound at 5% or more.
- **Pure arm.** The primary path alone would be a kill. The kill guard blocks it: with generous minerals and open air, 6.3% of rows reach the lenient window, so the kill depends on the model choice and is not reported.
- **Model failures.** No path failed in any of the 9 combinations. One `error.inp` from PHREEQC was left behind, probably from a retried step; no path is counted as failed.

## Where paths stop (primary path, USGS)

At the first state where Mg reaches 1 mM, the rows split as follows:
- **275 never reach 1 mM Mg** before salt passes the stop. Yellowstone water is Mg-poor relative to Na.
- **110 are blocked by Ca + pH**, 47 by pH alone, 47 by Ca + salt + pH, 25 by salt + pH and 8 by salt alone.
- **15 are inside the window.**

So the usual barrier is not calcium alone. Most waters run out of room on salt before Mg rises, and acid waters fail on pH.

## Reported only (no rule)

| Path | Mixed-arm S, USGS |
|---|---|
| Base minerals, closed (primary) | 2.8% |
| Base, open to air | 3.4% |
| Generous minerals, open to air | 8.9% |
| Strict minerals and window | 0.2% (support guard) |
| Primary, rows with raw pH ≥ 4.5 only (267 rows) | 5.6% (0.7, 14.8) |
| Mg ≥ 10 mM (ribozyme-level), window without a Mg ceiling | 0.4–3.8% across paths |

- Among near-neutral and alkaline springs, the ones that could plausibly host vesicles, about 1 in 18 waters passes on the primary path.
- The strict model, with calcite at SI 0.5, ordered sepiolite and Ca ≤ 0.5 mM, closes the window almost completely.

## Reading

- **What it shows.** In a database-scale test, evaporating real Yellowstone thermal waters seldom gives a pond that suits both fatty-acid vesicles and Mg-dependent RNA copying. The share is a few percent of waters, in 6 of 37 areas, and it depends on which minerals precipitate and whether the pond exchanges CO2 with air.
- **What it does not show.** The sealed test cannot say the joint window is rarer than 5%: too few areas carry most of the rows, and the interval is wide. Only Yellowstone was tested. The study does not include chelators such as citrate, mixing between springs, wet-dry cycling on mineral surfaces, Fe and Al, or a high-CO2 early atmosphere.
- **For the route ranking.** Lipid-first in hot-spring ponds is not ruled out, but it needs special waters: near-neutral to alkaline, relatively Mg-rich and Na-poor. The 15 passing rows, and their areas, are the place to look. Any claim that "evaporation solves the Mg problem" in general is not supported by these data.

## Next

- List the 15 passing waters and their areas (reported only; no rule), to see what makes them different.
- A second hot-spring province with open chemistry (for example New Zealand's Taupō Volcanic Zone, if a deposited table exists) would add areas and narrow the interval.
