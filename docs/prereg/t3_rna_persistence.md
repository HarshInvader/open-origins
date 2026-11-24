# Pre-registration (T3): does a setting's water chemistry let RNA last long enough to be copied?

Status: **DRAFT, not sealed.** Round 2, 2026-11-24, by the T3 prep agent. Nothing is hashed. No outcome statistic has been computed on field data. The section "Open before sealing" lists what still blocks the seal.

Prior art and sources: `experiments/t3_rna_persistence/PRIOR_ART.md`.
Analysis script: `experiments/t3_rna_persistence/scripts/t3_analysis.py` (modes `gate`, `planted`, `real`).

## What has been seen (blinding disclosure)

- **Field files.** MARHYS 4.0 and two USGS Yellowstone files are on disk. Probe scripts printed column names, units, category labels, the database's own documentation rows, and counts of non-empty cells. No value of temperature, pH, Mg, K, Na or any other measurement was printed, sorted, summarised or plotted.
- **Counts seen.** Rows and cluster sizes per setting for rows that have T, pH, Mg, K and Na filled (`data/structure_counts.json`). Counts of non-empty cells in each MARHYS pH and T column. Which fields are empty in Lost City rows.
- **Loader check.** `t3_analysis.py loadcheck` printed rows loaded, clusters and rows dropped per setting. It prints no value.
- **Not counted.** How many rows fall inside the confirmed range of D6. That needs the values, so it was left alone. This matters; see "Open before sealing", item A.
- **Published summaries I did read.** The USGS abstract (pH "from about 1 to 10", temperatures to "95°C"). The MARHYS abstract (site names). Cohen et al. 2024 (two soda lakes at about 1 M Na⁺, 1 mM Mg²⁺, pH 10). Prior-art papers that say hot and alkaline water destroys RNA.
- **Computed.** The rate law at lab conditions printed in opened papers (`gate`). Synthetic worlds (`planted`). L* for lab buffers.
- **Not computed.** No cleavage rate, half-life, contrast or L* for any field row.

## Why the plan's T3 is changed

The plan's rule was: a setting fails if at least 95% of samples give L* < 45 nt for every copying system. Three problems appeared before any data was touched.

1. **Hot water is already settled.** Miller & Bada 1988, Kua & Bada 2011, Bernhardt & Tate 2012 and Le Vay & Mutschler 2020 all say hot or alkaline vents destroy RNA. Kua & Bada (now opened) give half-lives "of less than a day at 75°C" for alkaline vents. Repeating that is not a new result.
2. **One term would make the headline.** The law multiplies the rate by 10 for every 14.3 °C. On a lab buffer (S1: pH 8, 100 mM Mg, 0.25 M Na⁺, 27 h⁻¹) L* is about 300 nt at 23 °C, 77 at 40 °C and 15 at 60 °C. It crosses 45 nt at 47 °C with no change in chemistry. "Share of samples that fail" would mostly be "share of samples hotter than about 50 °C". That is the T1 mistake: an assumption produces the number.
3. **"Every system" means "the fastest system".** A slow system fails everywhere, so it says nothing about the setting.

So the decision moves to a quantity in which temperature cancels.

## The end-member trap (found by the coordinator; fixed here)

MARHYS has two kinds of vent rows.

- **HF** rows are fluids as sampled. They are mixtures of vent fluid and seawater.
- **EM** rows are end members. They are extrapolated to zero Mg. Their Mg is zero by definition, not by measurement.

The law's Mg term is the largest chemistry term. So if EM rows fed it, "vent chemistry protects RNA" would be written by the end-member convention. This is the same failure as T1's gradient.

What the file itself says (its documentation rows, read with `scripts/probe_marhys_docs.py`):

- "pHcalc: pH calculated by regression trough zero Mg".
- "pH: pH measured or calculated by any mean Order of priority: HF:(pHmeas, pHcalc, pHmin) EM:(pHcalc, pHmin, pHmeas,)".
- "T: Temperature provided by any mean Order of priority: HF:(Tsample, Tcalc,Tmax) EM:(Tcalc, Tmax,Tsample)".
- "Tcalc: Temperature calculated for the end-member composition".

What the counts say:

- The sub-columns are nearly empty. `pHmeas` has 27 filled rows in the whole file, `pHcalc` 15, `pHmin` 214. The merged `pH` column has 3,658.
- So most pH values sit only in the merged column. The file does not let me separate measured from calculated pH.
- The file does not state the temperature at which pH was measured. Shipboard pH at about 25 °C is the usual practice (the coordinator's statement; I could not confirm it, because the MARHYS paper was blocked, see item C).

The fix, in four parts:

1. **Decision rows are HF rows only** (D1). EM rows never decide.
2. **pH is treated as a 25 °C bench value of unknown provenance** (D3). The law is applied to it as printed. A sealed sensitivity arm shifts pH by −0.5 and +0.5 on every decision row. A verdict must survive both.
3. **Definition guard.** The same statistic is computed on EM rows, and on a mixing line between each EM row and median seawater at sealed seawater fractions 0.1, 0.5 and 0.9. Each is reported. If the HF verdict and any of these disagree, the result is labelled **"definition-driven, not reported as a kill"**.
4. **Mg guard.** HF Mg is itself mostly a seawater mixing fraction. So every verdict is recomputed with the Mg term removed. If it changes, the label is **"Mg-driven, not reported as a kill"**.

## Claims under test, and who makes them

- **C-vent (hostile chemistry).** "environments with a high concentration of Mg2+ and high temperatures, such as hydrothermal vents, are unsuitable settings for RNA-based scenarios of molecular evolution" (Le Vay & Mutschler 2020, doi:10.1002/asia.201901205, opened). "RNA is most stable at pH 4-5 and is unstable at alkaline pH", against Lost City-type vents (Bernhardt & Tate 2012, doi:10.1186/1745-6150-7-4, opened).
- **C-lake (benign chemistry).** In soda lakes "The relatively low concentration of divalent cations may compensate for the high pH in lake water to keep the hydrolysis rate low" (Cohen et al. 2024, doi:10.1093/pnasnexus/pgae084, opened).
- **C-pore (copying wins).** "The timescale of replication using prebiotically plausible machinery therefore out-competes the hydrolysis" (Schwintek et al. 2025, doi:10.7554/eLife.100152, opened), for one lab condition.
- **C-spring.** Hot-spring pools as the site of RNA polymerisation (Deamer, Damer & Kompanichenko 2019, doi:10.1089/ast.2018.1979). **Not opened; to be requested.** Hot springs are analysed with the "hostile" bars, but no claim is quoted until the paper is read.
- **C-ice.** Copying in eutectic ice (Gianni et al. 2026; Attwater et al. 2025; both opened). No field chemistry exists for ice. Ice enters only as a lab check.

Testable form: at the temperature of each sample, compare the cleavage rate in the setting's own chemistry with the rate in control water. C-vent predicts vent chemistry is worse than control. C-lake predicts lake chemistry is no worse.

## Inputs (exact)

All in `experiments/t3_rna_persistence/`.

| File | Source | sha256 (first 12) |
|---|---|---|
| `raw/marhys4/MARHYS_DB_4_0.xlsx` | Diehl & Bach 2024, doi:10.1594/PANGAEA.972999, CC BY 4.0 | 1855355a392e |
| `raw/usgs_ynp_p92xkju7/YNP_WQ.csv` | McCleskey et al. 2022, ver. 2.0 (2025), doi:10.5066/P92XKJU7 | 084cb39954ae |
| `raw/usgs_ynp_historic_p9ksevi1/Yellowstone_Water_Chemistry_1883-2021.csv` | Price et al. 2024, doi:10.5066/P9KSEVI1 | cee22209d5a3 |
| `data/structure_counts.json` | counts and labels only, from `scripts/probe_structure.py` | hash at sealing |

Rate law, as reproduced in Wayment-Steele et al. 2021 (doi:10.1093/nar/gkab764) and Schwintek et al. 2025, from Li & Breaker 1999 (**not opened; to be requested**):

```
k_cl [min⁻¹ per linkage] = 1.30e-9 × 10^(0.983 (pH − 6)) × 10^(−0.24 (3.16 − [M+]))
                           × 10^(0.07 (T − 23)) × F_Mg
F_Mg = 69.3 [Mg]^0.80 × 3.57 [M+]^(−0.419)      (concentrations in mol/L, T in °C)
```

Copying systems:

| System | k_ext | Conditions | Source |
|---|---|---|---|
| S1 nonenzymatic, best case | 27 h⁻¹ | pH 8, 100 mM Mg, 250 mM Na⁺, 23 °C | Walton et al. 2019, doi:10.1021/acs.biochem.8b01156, opened |
| S2 nonenzymatic, monomer only | 3.7 h⁻¹ | same | same |
| S3 ribozyme polymerase 24-3 | 72 h⁻¹ ("1.2 nt/min") | 200 mM MgCl₂, 50 mM Tris pH 8.3, 17 °C | Horning & Joyce 2016, doi:10.1073/pnas.1610103113, opened (PMC5024611) |
| S4 QT45 | from 0.2% full-length yield in 72 days | −7 °C, pH 9, 50 mM MgCl₂ | Gianni et al. 2026; reported, not used |

## Statistics

For field row i with temperature T_i, pH_i, Mg_i and monovalent salt M_i:

1. **Cleavage rate** k_i = k_cl(T_i, pH_i, Mg_i, M_i).
2. **Copyable length** L*_i = sqrt(ln 2 · k_ext / (2 · k_i)). This uses a lab k_ext in field water, so L* is an upper bound.
3. **Chemistry contrast** (the decision quantity). c_i = log10 [ k_cl(T_i, row chemistry) / k_cl(T_i, control chemistry) ].
   - Temperature, k_ext and the prefactor cancel exactly.
   - c_i = c_pH + c_salt + c_Mg, with c_pH = 0.983 ΔpH, c_salt = 0.24 Δ[M+], c_Mg = Δ log10 F_Mg.
   - c_i > 0 means the setting's chemistry cuts RNA faster than control water at the same temperature.
4. **Controls.** Seawater: median pH, Mg and salt of MARHYS rows of type SW. Stream water: median of USGS rows with WaterType "river, stream, or creek". Every setting is reported against both.
5. **Setting statistic.** C_S = median of c_i. 95% interval by cluster bootstrap (D10), 10,000 draws, seed 20261125.

## Two tiers

- **Tier A, decision.** Only rows inside the confirmed range (D6), and only if the control is inside it too. Verdicts come from tier A alone.
- **Tier B, reported only.** All rows with 5 ≤ pH ≤ 11. Numbers carry the label "extrapolated". Tier B never gives a verdict.

## Decision rules

### K3, chemistry (primary arm; the strongest kill)

On tier A rows:

- **Kill of a "hostile chemistry" claim:** the 95% interval of C_S lies wholly below 0.
- **Support of a "hostile chemistry" claim:** the interval lies wholly above +1 (a factor of 10).
- **Kill of a "benign chemistry" claim:** the interval lies wholly above +1.
- **Support of a "benign chemistry" claim:** the interval lies wholly below +0.3 (a factor of 2).
- **Otherwise:** inconclusive.

### Guards on K3 (each can stop a verdict; none can create one)

A kill or support is reported only if all of these leave it unchanged. Otherwise the output reads "not reported as a kill (reason)".

| Guard | Recompute with | Label if the verdict changes |
|---|---|---|
| Salt rule | monovalent salt floored at 0.14 M (D4b) | fragile: salt rule |
| Law exponents | pH slope × 0.85 and × 1.15; Mg exponent × 0.85 and × 1.15 | fragile: rate law |
| pH convention | interval shifted by 0.983 × (−0.5) and × (+0.5) | pH-convention-dependent |
| Mg | contrast without c_Mg | Mg-driven |
| Definition | EM rows; mixing line at seawater fractions 0.1, 0.5, 0.9 | definition-driven |

The definition guard also fires when HF rows are inconclusive and an EM or mixing-line version gives a verdict. Then the flag is printed and the verdict stays inconclusive.

The pH-convention guard has a plain consequence. A kill needs the upper end of the interval below about −0.5. A support needs the lower end above about +1.5.

### K1, persistence budget (reported with a label; decides nothing alone)

- A setting **fails the budget** if at least 95% of its tier A rows have L* < 45 nt for the deciding system (D13).
- A setting **passes** if at least 25% of tier A rows have L* ≥ 90 nt with Mg floored at 1 mM, the lowest Mg at which an opened source shows copying (Cohen 2024; Attwater 2025).

### K2, attribution label on every K1 fail

- **T-neutral:** each row's own chemistry at 23 °C.
- **Chem-neutral:** control chemistry at each row's own temperature.
- Fails chem-neutral and passes T-neutral: **"temperature only"**. Headline: "any water this hot fails; nothing specific to this setting; already stated by Miller & Bada 1988 and Kua & Bada 2011." Not a new kill.
- Fails T-neutral: **"chemistry"**. Counts only if K3 agrees.
- The same labels are printed for tier B rows, marked "extrapolated".

### Verdict per setting

- **Killed / Supported:** K3 says so on tier A and no guard fires.
- **Not reported as a kill (reason):** K3 says so and a guard fires.
- **Cannot decide by design:** the control is outside the confirmed range, or tier A has fewer than 30 rows or fewer than 5 clusters.
- **Otherwise:** inconclusive.

## Gates

Gates 1–5 use lab numbers from opened papers only. Run 2026-11-24 with `nice python3 -I scripts/t3_analysis.py gate`. Result: **GATE PASS**, with one declared exception.

| Gate | Check | Result |
|---|---|---|
| G1 | Wayment-Steele 2021 Table 1, six rows, within 2% | 5 rows within 1%. Row 5 is the declared exception below |
| G2 | Schwintek 2025 Appendix 8, two rows, within 1% | both match at K⁺ = 1 mM. The paper does not print K⁺; 1 mM is back-calculated |
| G3 | Breaker et al. 2003: "~10⁻⁸ min⁻¹" at pH 7.0, 250 mM K⁺, 5 mM Mg²⁺, 23 °C; within a factor of 3 | ours 1.60e-8 |
| G4 | Cohen 2024 quoting Li & Breaker: "∼1% RNA degradation after 72 hours in 1 M K+ and 5 mM Mg2+ at pH 9.5"; within a factor of 3 | ours 1.66% per linkage. Temperature is not given; 23 °C assumed |
| G5 | Soda lake known answer (pH 10, 1 mM Mg, 1 M Na⁺, room temperature; no primer hydrolysis seen at 72 h): loss per linkage below 10% at 72 h | 1.45% at 72 h, 2.87% at 6 days. Primer length was not found in the text, so this is per linkage |
| G6 | Ice (Gianni 2026: QT45 half-life about 117 days at −7 °C, pH 9, 50 mM Mg). No pass bar | predicted 84 days at 0.05 M salt, 123 days at 0.14 M. Ratio 1.4 and 0.9 |
| G7 | Positive controls: buffers where copying was shown must give L* ≥ 45 nt | S1 buffer 304 nt; S3 buffer 397 nt; lake chemistry with S1 215 nt |
| G8 | Negative control: stream rows must not fail K1 at their own temperature | runs inside `real` only, because it reads field rows |

**Declared gate exception (G1 row 5).** The "in vitro transcription" row (37 °C, pH 7.6, 14 mM Mg, 4,000 nt) is printed as 57,000 × 10⁻⁷ min⁻¹. The law gives 25,950, which is 2.2× low. I checked the table's conditions. No single change explains it:

- Its other Mg row (1 mM, "physiological") matches to 0.1%. So the Mg term and units are coded as the paper uses them.
- pH 7.9 instead of 7.6 gives 51,173 (10% low). An exact match needs pH 7.948.
- An exact match by Mg alone needs 37.4 mM. By K⁺ alone it needs about 18–20 mM.
- Dropping the 0.4 unpaired factor gives 64,875 (14% high).

So the row stays **unexplained**. It is a disclosed gate failure. The gate rule is: G1 passes if the other five rows are within 2% and row 5 is within 1% of the disclosed −54.5%. This tolerance holds only because it is declared here, before sealing. Note the row lies at 14 mM, outside the confirmed range of D6, so it does not touch tier A.

## Gate 2: validity of the rate law outside Mg 5–10 mM

Full rule: `experiments/t3_rna_persistence/GATE2_RULE.md`. It was written before any measured rate was scored. The result goes in `GATE2_RESULT.md`.

- **Data.** Mojarro et al. 2021, Table 1 (PMC8248371, CC BY): measured cleavage of one RNA linkage at 75 °C, Mg 0–50 mM, pH 3.2–9.
- **Seen so far.** Conditions and table layout only, with one disclosed leak: the Figure 3 caption gives the rate at 50 mM Mg, pH 6.7. That row is removed.
- **Test.** A ratio within each pH column: R = k(Mg) / k(10 mM). Temperature, pH drift, buffer and substrate cancel. Prediction: R = (Mg / 10 mM)^0.80. Scored at pH 6.7, 8 and 9.
- **Mg conventions.** Nominal, and nominal minus 1 mM for the EDTA in the buffer. Both are sealed.
- **Metric.** e = log10(R_pred / R_meas) per row. Median signed e, median |e|, largest |e|.
- **Step 0.** The 5 mM rows must agree (median |e| ≤ 0.176). If not, the gate is UNTESTABLE and counts as FAIL.
- **Pass rule, separately for Mg < 5 mM (3 rows) and Mg > 10 mM (5 rows).** PASS needs median |e| ≤ 0.176 and no row above 0.301, under both Mg conventions. Otherwise FAIL.
- **Effect on D6.**

  | Outcome | Tier A Mg range |
  |---|---|
  | both FAIL, or UNTESTABLE | 5–10 mM (no change) |
  | low PASS only | 2.5–10 mM |
  | high PASS only | 5–55 mM |
  | both PASS | 2.5–55 mM |

- The 55 mM bound is 50 mM (the highest tested row) plus 10%, chosen because seawater is expected near 53 mM. The coordinator may strike the margin.
- The stream-water control stays outside tier A under every outcome.
- Under FAIL the range stays "extrapolated, reported only", with the signed error quoted as the direction of bias.
- Limits: one paper, 8 scored rows, 75 °C, one linkage with DNA neighbours, no added monovalent salt.

## Planted power check (synthetic only)

Run 2026-11-24: `nice -n 15 python3 -I scripts/t3_analysis.py planted`. Single process, 4.5 minutes.

- **Structure.** Real row counts and cluster sizes (`data/structure_counts.json`). Every value is synthetic.
- **Control.** Synthetic: pH 7.5, Mg 7.5 mM, salt 0.5 M. Inside the confirmed range. It is not seawater.
- **Noise.** pH: cluster sd 0.15 plus row sd 0.15. Mg: log sd 0.05 + 0.05. Salt: log sd 0.2.
- **Size.** 200 runs per cell, 200 bootstrap draws (reduced to keep the CPU free; the real run uses 10,000 draws). Claim tested: "hostile".

Worlds:

| World | Planted truth | Correct output |
|---|---|---|
| P0 null | chemistry equals control | no verdict |
| P1 hot only | T 85–125 °C, chemistry equals control | "cannot decide" in tier A; tier B label "temperature only" |
| P1b warm | T 35–45 °C, chemistry equals control | no verdict |
| P2 hostile | pH +1.6 | support |
| P3 mild | pH +0.5 | inconclusive (between the bars) |
| P4 protective | pH −1.1 in HF and EM rows | kill, no flag |
| P5 Mg dilution | HF Mg × 0.75, pH equal; EM rows pH −1.1, Mg 0 | no kill; "Mg-driven" or "definition-driven" |
| P6 EM-only effect | HF equals control; EM rows pH −1.1, Mg 0 | no kill; "definition-driven" flag |

Results (share of runs). "Not reported" means K3 made a call and a guard stopped it.

| Structure | World | Kill | Support | Inconclusive | Not reported | Cannot decide | Definition flag |
|---|---|---|---|---|---|---|---|
| Basalt ridge, 640 rows, 29 clusters | P0 | 0.00 | 0.00 | 0.96 | 0.04 | 0.00 | 0.00 |
| | P1 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| | P1b | 0.00 | 0.00 | 0.94 | 0.06 | 0.00 | 0.00 |
| | P2 | 0.00 | 0.46 | 0.00 | 0.55 | 0.00 | 0.00 |
| | P3 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| | P4 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| | P5 | 0.00 | 0.00 | 0.46 | 0.55 | 0.00 | 0.46 |
| | P6 | 0.00 | 0.00 | 0.97 | 0.03 | 0.00 | 0.97 |
| Ultramafic, 147 rows, 5 clusters | P0 | 0.00 | 0.00 | 0.91 | 0.10 | 0.00 | 0.00 |
| | P1 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| | P1b | 0.00 | 0.00 | 0.92 | 0.09 | 0.00 | 0.00 |
| | P2 | 0.00 | 0.35 | 0.00 | 0.61 | 0.04 | 0.00 |
| | P3 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| | P4 | 0.95 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 |
| | P5 | 0.00 | 0.00 | 0.63 | 0.33 | 0.04 | 0.00 |
| | P6 | 0.00 | 0.00 | 0.92 | 0.09 | 0.00 | 0.00 |
| Hot springs, 605 rows, 39 clusters | P0 | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 |
| | P1 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| | P1b | 0.00 | 0.00 | 0.95 | 0.04 | 0.00 | 0.00 |
| | P2 | 0.00 | 0.51 | 0.00 | 0.49 | 0.00 | 0.00 |
| | P3 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| | P4 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| | P5 | 0.00 | 0.00 | 0.38 | 0.62 | 0.00 | 0.00 |
| | P6 | 0.00 | 0.00 | 0.96 | 0.04 | 0.00 | 0.00 |
| Basalt ridge thinned to 10% (70 rows, 18 clusters) | P0 | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 |
| | P1 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| | P1b | 0.00 | 0.00 | 0.96 | 0.04 | 0.00 | 0.00 |
| | P2 | 0.00 | 0.39 | 0.00 | 0.61 | 0.00 | 0.00 |
| | P3 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 |
| | P4 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| | P5 | 0.00 | 0.00 | 0.55 | 0.45 | 0.00 | 0.55 |
| | P6 | 0.00 | 0.00 | 0.94 | 0.06 | 0.00 | 0.94 |

Rows may not sum to 1.00 because of rounding.

What the table says:

- **No false verdict.** In the six worlds where no verdict is correct (P0, P1, P1b, P3, P5, P6), kills and supports are 0 in all 4,800 runs.
- **The traps are caught.** P1 gives "cannot decide" in tier A and "temperature only" in tier B, every run. P5 never gives a kill. P6 never gives a kill and raises the definition flag in 94–97% of runs where EM rows exist.
- **Kill power is good.** P4 is killed in 95–100% of runs.
- **Support power is poor.** P2 (pH +1.6, contrast about +1.57) is supported in only 35–51% of runs. The pH-convention guard stops the rest. A support needs a contrast of about +1.6 or more. This is declared, not fixed: T3 can kill a "hostile" claim well and support one only when the effect is large.
- **The raw interval is a little too narrow.** At the null, K3 alone makes a call in 2–10% of runs (the bar would be 2.5%). It is worst with 5 clusters. The guards stop every one. So no verdict is reported on the interval alone.
- **Where the definition flag cannot work.** Ultramafic EM rows (21 complete) and hot springs (no EM rows) have no EM version. There the Mg guard is the only protection in P5, and P6 cannot arise.
- **Not planted.** Law-exponent error as a random draw. It is handled by the "fragile: rate law" guard instead.

## Fixed decisions

- **D1, settings and rows.** Decision rows are MARHYS sample type HF. EM rows feed the definition guard only. SW rows are the seawater control. Sub-settings, fixed from the label list before any value was read, first match wins:

  | Class | Rule on MARHYS labels | Complete HF rows | Clusters |
  |---|---|---|---|
  | V2a alkaline serpentinite | Vent area is "Lost City Hydrothermal Field" or "Old City Hydrothermal Field" | 10 | 2 |
  | V2b ultramafic, other | Rock type 1 is "Peridotite" | 137 | 4 |
  | V4 sediment | Rock type 1 is "Sediment" | 81 | 3 |
  | V1 basalt ridge | Geol. setting "Mid-oceanic spreading center" and rock type 1 "Basalt" | 640 | 29 |
  | V3 arc and back-arc | Geol. setting "Back-arc spreading center" or "Volcanic arc" | 423 | 38 |
  | V5 other | everything else | 21 | 6 |

  - "Complete" means T, pH, Mg, K and Na are all filled.
  - **V2a, V2b and V4 are "cannot decide by design" before any value is read:** fewer than 5 clusters. V2a also has fewer than 30 rows. Lost City is the vent the alkaline-vent claim is about, so this is a real gap. 113 of its HF rows lack K and 112 lack Na.
  - Hot springs: USGS ver. 2.0 rows with WaterType "thermal water" (605 complete rows, 39 areas). Lakes: WaterType "lake" (15 rows, 5 areas: cannot decide by design). Streams (37 rows, 15 areas) are the control.
- **D2, temperature.** MARHYS merged column `T`. The sub-columns `Tsample` (489 rows) and `Tcalc` (17 rows) are too sparse to choose between. For HF rows `T` is mostly the vent's maximum measured temperature, not the bottle's. Temperature cancels in K3, so this affects only K1 and the tier A filter. USGS `WaterTemperature_DegreesCelsius`.
- **D3, pH.** MARHYS merged column `pH`, applied as printed, treated as a 25 °C bench value. No in-situ correction. Sensitivity arm ± 0.5, sealed. USGS field pH; lab pH only if field pH is empty.
- **D4, monovalent salt.** [M+] = [Na⁺] + [K⁺], following Schwintek et al. MARHYS `Na` is the merged column (priority Nacalc, then Nameas, per the file). Two rules that must agree: (a) as measured; (b) floored at 0.14 M.
- **D5, Mg.** F_Mg = max(1, 69.3 [Mg]^0.80 × 3.57 [M+]^(−0.419)). At Mg = 0 the term is 1.
- **D6, confirmed range (tier A).** 5 ≤ T ≤ 45 °C, 6 ≤ pH ≤ 9.5, **5 ≤ Mg ≤ 10 mM**. The Mg range is the only fitted range confirmed from an opened source: "The above equation was parametrized from measurements with [Mg2+] concentrations between 0.005 and 0.01 M" (Wayment-Steele 2021). The T and pH ranges are where opened sources have used the law, not fitted ranges. The control must also have Mg in 5–10 mM and pH in 6–9.5. Rows outside are reported in tier B only.
- **D7, tier B limits.** 5 ≤ pH ≤ 11. The law has no acid term, and it bends near the 2′-OH pKa of 13.7 (Emilsson et al. 2003, opened).
- **D8, units.** MARHYS mmol/kg is taken as mmol/L. USGS mg/L is divided by atomic mass (Mg 24.305, K 39.098, Na 22.990).
- **D9, non-detects and gaps.** "<x" enters as x/2. Rows missing T, pH, Mg, K or Na are dropped and counted. Seawater control rows need pH, Mg, K and Na but not T (88 rows, 40 areas).
- **D10, clusters.** MARHYS "Vent area (large scale)"; for V2a the Vent-ID. USGS "Area".
- **D11, replication set.** The historic USGS file, after dropping samples dated 2009 or later. Not yet coded.
- **D12, thresholds.** L* 45 nt and 90 nt. K3 bars 0, +0.3 and +1. Minimum 30 rows and 5 clusters.
- **D13, deciding system.** S3, 72 h⁻¹, the fastest k_ext with an opened primary source. It was measured at 200 mM Mg, far from any field water. This affects K1 only.
- **D14, seed and draws.** Seed 20261125. 10,000 bootstrap draws in `real`.
- **D15, headline order.** K3 first with its guard labels. Then K1 with its K2 label. No tier B number without the word "extrapolated".
- **D16, seal check.** `real` refuses to run unless `docs/prereg/HASHES.txt` has a line for this file and a line for `t3_analysis.py`, and both hashes match the files on disk. Tested unsealed: it refuses.

## Ways it could be fooled

1. **Extrapolation.** Most rows are expected to lie outside D6. Outside it every number is the formula, not a measurement. Tier B is labelled for this reason.
2. **End-member convention.** See the trap section. Guarded, not removed.
3. **HF Mg is a mixing fraction.** A bottle with more seawater has more Mg. A Mg-driven contrast measures sampling, not the vent. Guarded by the Mg guard.
4. **Wrong metals.** Vent fluids carry Fe²⁺ and Mn²⁺. Mojarro et al. 2021 found both cleave RNA faster than Mg²⁺ at pH 5.4–8. The law has no term for them. A "protective" result for vents must carry this caveat.
5. **pH provenance.** Bench pH, in-situ pH and regression pH are mixed in one column. The ± 0.5 arm is a guess at the size of that error, not a measurement of it.
6. **Folded RNA.** The law is for unstructured RNA. Duplexes and folded ribozymes last longer (Guth-Metzler et al. 2023).
7. **Modern water is not Hadean water.** The controls are modern.
8. **Bulk water is not the micro-site.** Pores, films, ice veins and mineral surfaces change local ion levels.
9. **Tier A selects odd rows.** Vent rows at 5–45 °C with 5–10 mM Mg are diluted or diffuse fluids. They may not stand for the vent.

## Limits

- Phosphodiester cleavage only. No depurination, deamination or ribose decay.
- No field data for ice. Lakes: 15 rows.
- The rate law comes second-hand.

## Open before sealing

Closed in round 2: old items 3 (gate row: declared exception), 4 (Horning & Joyce opened), 6 (D1 fixed), 7 (script written; gate and planted run), and half of 2 (Kua & Bada opened: pH and temperature only, no Mg, no field data, so T3 is not pre-empted).

Still open:

- **A. Tier A may be empty. This is the main blocker.** Round 3: Gate 2 above now decides the Mg range. The text below is the problem it answers. Seawater is expected to hold far more than 10 mM Mg, and fresh stream water far less than 5 mM. I did not read the values, so this is expectation, not a count. If it holds, both controls are outside the confirmed range and every setting returns "cannot decide by design". The study would then be honest and empty. Ways out, for the coordinator to choose before sealing:
  1. Get Li & Breaker 1999 and replace D6 with the true fitted ranges and uncertainties. Best option.
  2. Seal as is and accept that the likely outcome is "cannot decide", with tier B reported as extrapolation.
  3. Allow one blind count: rows per setting inside D6, and whether each control is inside. Counts only, declared here first.
- **B. Li & Breaker 1999** (doi:10.1021/ja990592p). Not opened; to be requested. Unpaywall lists it as closed. No repository copy found.
- **C. Diehl & Bach 2020** (doi:10.1029/2020GC009385). Not opened; to be requested. It is open access (CC BY) but the Wiley server answered 403 to the script, and I did not work around it. A person can open it in a browser. Needed to confirm at what temperature pH was measured and how EM rows are built. Until then the trap section rests on the file's own documentation rows.
- **D. Deamer, Damer & Kompanichenko 2019.** Not opened; to be requested. Needed to quote C-spring.
- **E. Cohen 2024 primer length and temperature** for gate G5. Not found in the text read. G5 is per linkage until then.
- **F. Lost City.** Cannot be decided with these data (10 complete rows, 2 clusters). Either accept that, or seal a rule for rows that lack Na and K.
- **G. D11** (historic USGS replication) is not coded.
- **H. Seal.** Hash this file, `t3_analysis.py`, `data/structure_counts.json` and the raw files into `docs/prereg/HASHES.txt`.

A draft request note for items B–D is in `PRIOR_ART.md`, section "To be requested".

## Sources actually opened

Listed with DOI and URL in `PRIOR_ART.md`. Round 1: Wayment-Steele 2021; Schwintek 2025; Bernhardt & Tate 2012; Le Vay & Mutschler 2020; Cohen 2024; Mojarro 2021; Guth-Metzler 2023; Walton 2019; Gianni 2026; Attwater 2025; the PANGAEA record for MARHYS 4.0; two ScienceBase records. Round 2: Kua & Bada 2011; Horning & Joyce 2016; Breaker et al. 2003; Emilsson et al. 2003; the documentation rows inside the MARHYS file.
