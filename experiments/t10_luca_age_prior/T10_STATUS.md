# T10 (S4) status: parked until the AWS budget resets on 1 December; not sealed (2026-11-24)

Draft prereg: `docs/prereg/t10_luca_age_prior.md`. Prior art: `PRIOR_ART.md`. Timing: `scripts_out/t10_timing_summary.json`. No LUCA posterior was read.

**Why it is parked.**
- One MCMCtree chain at the published length (20.1M iterations) takes 28–42 CPU-days on the laptop under background priority. The timing runs were taken at a load average of 8–97, so this is pessimistic.
- The cheapest decisive kill test is 4 chains: P1, the raised 4.52 Ga maximum, under GBM and ILN, 2 chains each at 2.0M iterations. That is about 95 core-hours, or about $1–2 on spot, and only about $1 of this month's cap is left.
- The prior-only twins are quick (45–100 min) and fit on the laptop.

**What was learned.**
- Prior art: no one has moved the maximum or the rate prior on Moody's data. Mahendrarajah 2023 found LUCA "clashes against the root hard-maximum" in their own analysis.
- The plan's gate interval (4.09–4.33 Ga) is the partitioned-data result; the concatenated `in.BV` run needs the concatenated published interval.
- Bounds are hard in the files (`1e-300` tails), although the text calls them soft.
- PAML 4.10.7 needs `-D_FORTIFY_SOURCE=0` on macOS clang. An overlapping strcpy in `copy_to_Sptree` aborts the default build.
- The prior alone puts LUCA at 4.25–4.51 Ga under R0 and 5.65–5.98 Ga under P1 (short twins, looked at on purpose and disclosed). So under P1 the sequences would have to pull LUCA down by about 1.4 Ga for support. The test is not decided in advance.

**Open decisions (for the seal).**
1. Gate against the concatenated published interval.
2. Should P1 raise only the root and LUCA maxima, or all four 4.52 maxima?
3. Should a P2 kill need one arm or both?
4. Choose between a full R0 gate and the cheap binary-identity gate.

**Before 1 December.** A 5-minute timing run at normal priority would show whether the laptop alone can carry the 4-chain kill test.
