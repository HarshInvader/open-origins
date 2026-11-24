# T3 Gate 2: does the rate law hold outside Mg 5–10 mM?

Status: **RULE ONLY. Written 2026-11-24, before any scoring.** The coordinator commits this file first. Scoring (step B) starts only after the message "committed".

## Question

The Li & Breaker law, as reproduced in Wayment-Steele 2021 and Schwintek 2025, has a Mg term that was fitted between 5 and 10 mM. T3 needs it at lower and higher Mg. Does it predict measured cleavage there?

## What I have and have not seen

- **Seen: conditions and layout only.** Two probe scripts read the paper's XML. `scripts/probe_mojarro_layout.py` prints table headers and prints every digit in table bodies and captions as `#`. `scripts/probe_mojarro_methods.py` prints four Methods subsections and the first column of Table 1.
- **One leak, disclosed.** The second probe printed the Figure 3 caption, which sits inside a Methods subsection. It states three measured slopes at pH 6.7 and 50 mM metal, including Mg²⁺: "ln(p/po) = −0.038h". So I have seen one measured rate: 50 mM Mg, pH 6.7. That row is removed from scoring below. I did not compute its prediction.
- **Qualitative statements seen** (masked captions): Mg rows are "generally more stable" than Fe or Mn rows; the authors fit a saturation ("one-site binding") model; precipitates were seen with Fe²⁺ and Mn²⁺.
- **Not seen.** Any cell of Table 1 or Table 2. The Results and Discussion text.
- **Round 1.** The paper was opened in round 1 for prior art. I hold no rate value from that reading beyond what is written in `PRIOR_ART.md`.

## Source

Mojarro A, et al. 2021. "In search of the RNA world on Mars". PMC8248371. CC BY 4.0. File: `raw/mojarro2021/PMC8248371.xml` (sha256 starts d59f90e8a56f), from the Europe PMC full-text service.

**Table 1**, "Pseudofirst-order reaction kinetics k obs (h⁻¹) of RNA cleavage". Layout:

- Columns: five pH blocks (3.2, 5.4, 6.7, 8, 9). Each block has `k obs (h⁻¹) (10⁻²)`, `SEM (10⁻³)` and `t 1/2 (h)`.
- Rows: Fe²⁺, Mg²⁺ and Mn²⁺ at 50, 25, 10, 5 and 2.5 mM; three Mg:Fe mixtures; one "0 mM" negative control.

Conditions (Methods):

- 75 °C. 250 mM buffer: glycine-HCl (pH 3.2), MES (pH 5.4 and 6.7), Tris (pH 8 and 9). 1 mM EDTA in every reaction. MgCl₂. n = 2.
- No Na⁺ or K⁺ concentration is stated. The temperature at which buffer pH was set is not stated.
- Substrate: a 15-mer of DNA with one ribonucleotide, 5′-Cy3-TTT-TTT-rCTT-TTT-TTT-3′. It has **one** cleavable linkage.
- k obs is the slope of ln(fraction intact) against time.

## Rows

Only the Mg²⁺ block and the 0 mM row are used. Only the pH 6.7, 8 and 9 columns are scored: the law has no acid term (prereg D7).

| Set | Rows (nominal Mg × pH) | Count |
|---|---|---|
| Reference | 10 mM at pH 6.7, 8, 9 | 3 |
| In-range check | 5 mM at pH 6.7, 8, 9 | 3 |
| **Low range (Mg < 5 mM)** | 2.5 mM at pH 6.7, 8, 9 | 3 |
| **High range (Mg > 10 mM)** | 25 mM at pH 6.7, 8, 9; 50 mM at pH 8, 9 | 5 |
| Removed (seen) | 50 mM at pH 6.7 | 1 |
| Reported only | pH 3.2 and 5.4 columns; the 0 mM row; Fe, Mn and mixture rows | — |

Rows the law was fitted on: none of these. They come from a different lab, substrate and temperature.

## Why the test is a ratio

An absolute comparison would fail for reasons that have nothing to do with Mg:

- 75 °C is far above the 5–45 °C where opened sources use the law.
- Tris pH falls on heating, and the paper does not say at what temperature pH was set.
- The monovalent cation level is not stated, and the law needs it.
- One rC linkage between thymidines is not an average RNA linkage.

All four cancel in a ratio of two rows in the same pH column. Only the Mg dependence remains. That is the part T3 needs.

## Conversion

- k per linkage [min⁻¹] = (table value × 10⁻²) / 60. One linkage, so no division by length.
- The half-life column is not used. It is ln 2 / k and adds nothing.
- Measured ratio for a row: R_meas = k(Mg, pH) / k(10 mM, same pH).

## Prediction (fixed)

```
R_pred = F_Mg(Mg) / F_Mg(Mg_ref) = (Mg / Mg_ref)^0.80
```

- Exponent 0.80, fixed. The prefactors 69.3 and 3.57 and the [M+]^(−0.419) term cancel because the buffer is the same in both rows.
- The literal law is used, without the D5 floor. The floor needs [M+], which is not stated.
- **Mg convention.** EDTA at 1 mM binds about 1 mM of metal. Two conventions, both sealed:
  - nominal: Mg = 2.5, 5, 10, 25, 50 mM;
  - free: Mg = nominal − 1 mM = 1.5, 4, 9, 24, 49 mM.

| Row | R_pred nominal | R_pred free |
|---|---|---|
| 2.5 mM | 0.330 | 0.239 |
| 5 mM | 0.574 | 0.523 |
| 25 mM | 2.08 | 2.19 |
| 50 mM | 3.62 | 3.88 |

These are arithmetic on the formula. No measured value enters.

## Metric

For each row: e = log10(R_pred / R_meas). Positive e means the law gives too steep a rise with Mg.

Per range, and per Mg convention, report:

- the median of e (signed);
- the median of |e|;
- the largest |e|;
- the share of rows with |e| ≤ log10(1.5) = 0.176.

The tolerance comes from T3 itself. Its smallest decision bar is 0.3 in log10 (a factor of 2). An error in the Mg term must stay well under that.

## Pass rule

**Step 0, can the data test anything?** The in-range check (5 mM against 10 mM, three rows) must have median |e| ≤ 0.176 under at least one Mg convention. If not, the data cannot confirm the law even where it was fitted. Then the gate is **UNTESTABLE** and both ranges are treated as FAIL.

**Low range and high range, judged separately.** A range gets **PASS** only if, under **both** Mg conventions:

- median |e| ≤ 0.176 (a factor of 1.5), and
- no row has |e| > 0.301 (a factor of 2).

Otherwise it gets **FAIL**. There is no third outcome and no re-scoring with other choices.

Noise is not used as an excuse. If a row's SEM is large, the row still counts.

## What each outcome does to T3's D6

| Outcome | D6 Mg range for tier A (decision) |
|---|---|
| Low FAIL, high FAIL (or UNTESTABLE) | 5–10 mM. No change |
| Low PASS only | 2.5–10 mM |
| High PASS only | 5–55 mM |
| Both PASS | 2.5–55 mM |

- A PASS extends the range only as far as the rows that were tested. It never licenses "any Mg".
- **The 55 mM bound is a declared choice.** The highest tested row is 50 mM. I add 10% because seawater is expected near 53 mM. That expectation is general knowledge; I have not read it from the MARHYS file. The coordinator may strike the margin and keep 50 mM. If so, a seawater control above 50 mM stays outside tier A.
- **Stream water stays out under every outcome.** Fresh water is expected to hold well under 2.5 mM Mg. This gate cannot bring the stream control into tier A.
- Under FAIL, the range stays "extrapolated, reported only". The signed median error is then quoted next to every tier B number in that range, as the known direction of bias.
- D6's temperature and pH limits do not change under any outcome.

## Reported only (no effect on the rule)

- The 0 mM row against the 10 mM row. The law says to drop the Mg term at 0 mM, so this ratio needs [M+]. It is shown for [M+] = 0.25 M as an assumption.
- The absolute comparison at 75 °C, with the same assumption.
- The pH 3.2 and 5.4 columns.
- The removed row (50 mM, pH 6.7).
- Fe²⁺ and Mn²⁺ rows against Mg²⁺ rows, for the "wrong metals" caveat in the prereg.

## Limits of this gate

1. **One paper, 8 scored rows, n = 2 each.** A PASS is thin support. A FAIL is thin evidence too, but it costs nothing: the range simply stays extrapolated.
2. **75 °C only.** A PASS assumes the Mg exponent is the same at field temperatures.
3. **One linkage, DNA neighbours.** Not a typical RNA strand.
4. **No monovalent salt added.** The law's Mg term was fitted in K⁺ solutions. A ratio hides this, but saturation behaviour may differ.
5. **Narrow span.** The test reaches 4× below and 5× above the fitted range, and no further.
6. **Other sources looked at and not usable.** Wayment-Steele Table 1 holds model outputs, not measurements. Cohen 2024 gives gel images, no rate in the text. Gianni 2026 gives one half-life at 50 mM Mg, but in ice of unknown solute concentration, and I have already compared it with the law (gate G6), so it is not blind. I did not run a new literature search for further tables: search results can show rate values.

## Step B (after "committed")

1. Add mode `gate2` to `scripts/t3_analysis.py`. It reads the Mg block and the 0 mM row of Table 1 from the XML, applies this rule, and prints the table of e values and the verdict.
2. Write `GATE2_RESULT.md` with the extracted values, the scores and the D6 that follows.
3. Any departure from this file is listed there as a deviation.

**Coordinator note at commit.** The upper bound of 55 mM (50 mM tested + 10%) was chosen knowing that the seawater control sits near 53 mM. That is a control input value, not an outcome, and it is kept and disclosed here. Under the strict reading (cap at 50 mM), the seawater control is a small extrapolation. Both readings are reported.
