# T4 status: not sealed; the blind count fixes the answer, so it is reported as description (2026-11-24)

Draft prereg: `docs/prereg/t4_vesicle_rna_window.md`. Prior art: `PRIOR_ART.md`. Counts: `scripts_out/t4_blind_count.log`. Planted check: `scripts_out/t4_planted.log`. The real mode was never run.

**Question.** Fatty-acid vesicles tolerate little Mg²⁺. RNA copying needs Mg²⁺. In real natural waters, how often do the two windows overlap?

**Why it is not a test.** The declared blind count printed only the margins (rows inside each window separately). They already decide every arm:
- **Empty by definition (lab fact; Chen 2005, Adamala & Szostak 2013).** Every vesicle window against the ribozyme-level need (≥ 50 mM Mg). Also pure fatty acid (≤ 0.5 mM) against nonenzymatic copying (≥ 1 mM).
- **Yellowstone (USGS, 660 thermal-water rows).** Only 9 rows in 3 of 40 areas reach 1 mM Mg. The joint share is therefore at most 1.2%, and only "supported" or "inconclusive" could come out.
- **Vents (MARHYS measured rows).** 0–2 rows per class pass the vesicle limits on Ca (~1.9 mM, Cary 2024), salt and pH (Jordan 2019).
- Ultramafic, sediment, Lost City, lakes, drill holes and seeps have too few clusters to decide.

**Descriptive finding, not blind.** Open spring and vent chemistry almost never meets both the vesicle window and the minimum Mg for RNA copying.
- In Yellowstone, at most 1.2% of thermal-water rows could; in vents, almost none.
- This extends the two-lake joint test of Cohen 2024 and the roughly eight-spring vesicle test of Cary 2024 to a database scale. It does not test whether evaporation or local chelators (e.g. citrate, Chen 2005 / Adamala & Szostak 2013) open the window.

**Planted check (kept for reuse).** The kill bound was tightened from the 2.5th to the 0.5th percentile after round 1 gave 3–12% false kills at the threshold. Kills at the threshold are now ≤ 2%; power is 0.95–0.97; there is no false support.

**Open follow-ups**
1. Evaporation path: do spring waters reach Mg 1–4 mM before Ca or salt closes the vesicle window? Needs a mineral-saturation model.
2. A many-lake soda/closed-basin table to test Cohen 2024's "unique role" claim.
