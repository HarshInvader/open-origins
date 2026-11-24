# T3 Gate 2 result: the rate law outside Mg 5–10 mM

Date: 2026-11-24. Rule: `GATE2_RULE.md`, sealed in commit e7cc89e before scoring. Run: `nice python3 -I scripts/t3_analysis.py gate2`. No deviation from the rule.

## Verdict

| Range | Verdict |
|---|---|
| Step 0 (5 mM rows) | testable: median \|e\| 0.112 under the nominal convention |
| **Low, Mg < 5 mM** | **FAIL** |
| **High, Mg > 10 mM** | **PASS** |

**Resulting D6: tier A Mg range is 5–55 mM.** Strict reading: 5–50 mM. Both are reported in the real run. Below 5 mM stays "extrapolated, reported only".

## Extracted values

Mojarro et al. 2021, Table 1, Mg²⁺ block and the 0 mM row. k per linkage in 10⁻⁴ min⁻¹ (table value × 10⁻² / 60). SEM in brackets.

| Mg (nominal) | pH 6.7 | pH 8 | pH 9 |
|---|---|---|---|
| 0 mM | 0.333 (0.025) | 3.03 (0.22) | 1.35 (0.18) |
| 2.5 mM | 2.40 (0.53) | 1.77 (0.68) | 8.87 (0.10) |
| 5 mM | 4.10 (0.24) | 3.08 (1.0) | 22.3 (2.3) |
| 10 mM (reference) | 5.52 (0.22) | 3.60 (0.12) | 48.3 (5.2) |
| 25 mM | 9.35 (0.24) | 7.35 (0.50) | 74.8 (4.2) |
| 50 mM | 12.4 (0.63), removed | 11.3 (0.05) | 104 (1.9) |

## Scores

R = k(Mg) / k(10 mM, same pH). e = log10(R_pred / R_meas). Positive e: the law rises too steeply with Mg.

| Set | Mg | pH | R_meas | R_pred nominal | e nominal | R_pred free | e free |
|---|---|---|---|---|---|---|---|
| In-range check | 5 | 6.7 | 0.743 | 0.574 | −0.112 | 0.523 | −0.153 |
| | 5 | 8 | 0.856 | 0.574 | −0.174 | 0.523 | −0.214 |
| | 5 | 9 | 0.462 | 0.574 | +0.094 | 0.523 | +0.054 |
| Low | 2.5 | 6.7 | 0.435 | 0.330 | −0.120 | 0.238 | −0.261 |
| | 2.5 | 8 | 0.491 | 0.330 | −0.173 | 0.238 | −0.313 |
| | 2.5 | 9 | 0.183 | 0.330 | +0.255 | 0.238 | +0.114 |
| High | 25 | 6.7 | 1.695 | 2.081 | +0.089 | 2.192 | +0.112 |
| | 25 | 8 | 2.042 | 2.081 | +0.008 | 2.192 | +0.031 |
| | 25 | 9 | 1.548 | 2.081 | +0.129 | 2.192 | +0.151 |
| | 50 | 8 | 3.130 | 3.624 | +0.064 | 3.879 | +0.093 |
| | 50 | 9 | 2.148 | 3.624 | +0.227 | 3.879 | +0.257 |

(The rule file prints R_pred free for 2.5 mM as 0.239. The script gives 0.238. Rounding only.)

| Set | Convention | Median e | Median \|e\| | Largest \|e\| | Share within 0.176 | Meets rule |
|---|---|---|---|---|---|---|
| In-range check | nominal | −0.112 | 0.112 | 0.174 | 3 of 3 | yes |
| In-range check | free | −0.153 | 0.153 | 0.214 | 2 of 3 | yes |
| Low | nominal | −0.120 | 0.173 | 0.255 | 2 of 3 | yes, barely |
| Low | free | −0.261 | 0.261 | 0.313 | 1 of 3 | **no** |
| High | nominal | +0.089 | 0.089 | 0.227 | 4 of 5 | yes |
| High | free | +0.112 | 0.112 | 0.257 | 4 of 5 | yes |

A range passes only if both conventions meet the rule (median |e| ≤ 0.176, none above 0.301).

## What it means

- **High range.** The law predicts the rise from 10 to 25 and 50 mM within a factor of 1.8 in every row, and within 1.3 at the median. Every error has the same sign: the law is a little too steep. So at 50 mM the law overstates cleavage by about 15–80%. This bias is quoted beside tier A numbers that use Mg above 10 mM.
- **The pass is not wide.** The worst row (50 mM, pH 9: 0.227 and 0.257) is close to the 0.301 limit.
- **Low range.** It fails on the free-Mg convention. Under the nominal convention it would pass by 0.003. The pH 9 row and the other two rows err in opposite directions, so there is no clear direction of bias. The signed median (−0.12 nominal, −0.26 free) is quoted beside tier B numbers below 5 mM, with that warning.
- **The in-range rows are not much better than the low rows.** The 5 mM rows miss by up to 0.21. So this data set is noisy at low Mg (SEM up to 38% of k at 2.5 mM, pH 8). The low FAIL may be noise. The rule does not allow that excuse, and it is not used.

## Reported only (no effect on the verdict)

- **Removed row** (50 mM, pH 6.7; seen before the rule was written): R_meas 2.242 against 3.624 (nominal) and 3.879 (free). e = +0.209 and +0.238. Had it been scored, the high range would still pass.
- **0 mM against 10 mM.** Measured 0.060, 0.843 and 0.028 at pH 6.7, 8 and 9. The law gives 0.090 if [M+] = 0.25 M is assumed. The pH 8 value is odd: the Mg-free rate there is almost as high as with 10 mM Mg.
- **Absolute rates at 10 mM, 75 °C, [M+] = 0.25 M assumed.** Law against measured: 0.62 against 5.5 (pH 6.7); 11.7 against 3.6 (pH 8); 112 against 48 (all × 10⁻⁴ min⁻¹). Off by factors of 9 low to 3 high. This was expected and is why the test is a ratio. It says the law's absolute value at 75 °C in these buffers is good to about one order of magnitude, no better.
- **Measured pH dependence is not monotonic.** At 10 mM the rate falls from pH 6.7 to pH 8 (5.5 to 3.6) and then rises 13-fold to pH 9. The law predicts a steady 9.6-fold rise per pH unit. The buffer changes from MES to Tris between those columns, and Tris pH falls on heating. This is outside Gate 2, but it bears on T3's pH term and on the ± 0.5 pH arm.
- **Acid columns** (ratios to 10 mM at 2.5, 5, 25, 50 mM). pH 3.2: 1.40, 1.14, 0.81, 0.53; more Mg means less cleavage, the opposite of the law. pH 5.4: 0.27, 0.86, 1.26, 1.03; flat above 5 mM. This supports D7: the law is not used below pH 5, and tier A starts at pH 6.
- **Fe²⁺ and Mn²⁺ rows** were not extracted. The script reads only the Mg block and the 0 mM row.

## Limits (from the rule, unchanged)

One paper. Eight scored rows, n = 2 each. 75 °C only. One linkage with DNA neighbours. No added monovalent salt. The test reaches 5× above the fitted range and no further.
