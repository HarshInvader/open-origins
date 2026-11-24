# T3 status: not sealed; cannot be decided with open field data (2026-11-24)

Draft prereg: `docs/prereg/t3_rna_persistence.md` (committed unsealed in a077c83). The real run was never executed: `t3_analysis.py real` refuses to run without a seal, and no cleavage rate, contrast or L* was computed on any field row.

## Why it stops here

1. **Gate 2 (sealed in e7cc89e before scoring; `GATE2_RESULT.md`).** The reproduced Li & Breaker magnesium term was tested blind against Mojarro et al. 2021's measured cleavage at 75 °C.
   - **Above 10 mM: PASS.** The law predicts the rise from 10 to 25 and 50 mM within a factor of 1.3 at the median and 1.8 at worst. It is slightly too steep in every row.
   - **Below 5 mM: FAIL** under the free-Mg convention (median error a factor of 1.8, worst a factor of 2.1).
   - So the law is usable for decisions only at Mg 5–55 mM (5–50 strict), with T 5–45 °C and pH 6–9.5.
2. **Declared blind count (counts only; `scripts/range_count.py`, `scripts_out/t3_range_count.json`).** This is option 3 of "Open before sealing" A.
   - **Yellowstone (USGS):** 0 of 710 rows in range across thermal water, lakes, streams, overflow, drill holes and seeps. Every row has Mg below 5 mM. The stream control is out of range.
   - **Vents (MARHYS measured rows):** only 44 of 640 (basalt ridges), 44 of 423 (arcs and back-arcs), 2 of 81 (sediment), 3 of 137 (ultramafic), 6 of 21 (other) and 0 of 10 (Lost City) are in range. They are in range because they are cool and Mg-rich, which in a vent sample means they are mostly entrained seawater. A contrast against seawater would largely compare seawater with itself.
   - **Seawater control:** in range under the 55 mM reading only.

So the study would return "cannot decide" for springs and lakes by construction, and a near-tautological answer for vents. Sealing it and running it would add nothing.

## What was learned (reportable)

- **The magnesium term of the standard RNA-cleavage law (Li & Breaker 1999, as reproduced in Wayment-Steele 2021 and Schwintek 2025) holds from 10 to 50 mM.** In one independent data set (Mojarro 2021), it runs slightly steep there, overstating cleavage at 50 mM by about 15–80%.
- **Below 5 mM it was not confirmed.** That is where every Yellowstone spring, lake and stream sample sits. Published claims about RNA stability in Mg-poor natural waters therefore rest on an untested part of the law. An example is Cohen et al. 2024 for soda lakes: "the relatively low concentration of divalent cations may compensate for the high pH".
- **Mojarro's pH dependence is not monotonic** between pH 6.7 and 9, while the law predicts a steady ~10× per pH unit. Their buffer changes (MES to Tris) between those columns, so this may be a buffer effect. The pH term needs its own blind test before any setting comparison.

## What would make T3 decidable

- Measured RNA cleavage rates at Mg 0.01–5 mM, pH 6–10 and T 25–90 °C in natural or matched-composition water, to calibrate the low-Mg regime. This is a cheap bench experiment and a good request to a lab.
- Li & Breaker 1999's own fitted ranges and uncertainties (paywalled; to be requested).
