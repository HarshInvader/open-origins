# T3 prior art: RNA persistence per origin setting

Written 2026-11-24 by the T3 prep agent. No outcome statistic was computed on field data.

"Opened" means I fetched the full text in this session and read the passage quoted. "Named" means the paper is cited by an opened source, or was found by search, and I did not read it. Named papers must be opened before sealing.

All fetches used the User-Agent `open-research-site/1.0`. Full texts came from the Europe PMC REST service (`https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML`).

## Short answer

1. **The qualitative result is established.** Hot water and alkaline water destroy RNA fast, and RNA is most stable near pH 4–5 and 0 °C. This is in the literature from 1988 to 2020 (Miller & Bada; Kua & Bada; Bernhardt & Tate; Le Vay & Mutschler). T3 would only repeat it for hot vents.
2. **The exact T3 design was not found.** I found no paper that runs a cleavage rate law over a database of measured field waters (vents, hot springs, lakes) and reports a copyable length per setting. Searches: Europe PMC, web search over arXiv and bioRxiv, six query forms. A search that finds nothing is weak evidence.
3. **The closest work is narrower.**
   - Kua & Bada 2011 compare stability across proposed settings from pH and temperature only, with no Mg and no field database (opened in round 2; confirmed).
   - Schwintek et al. 2025 do the copy-versus-cleave comparison, but for one lab condition.
   - Cohen et al. 2024 measured RNA survival and copying in real soda-lake water, for two lakes.
   - Mojarro et al. 2021 measured cleavage against metal and pH in Mars-analogue solutions.
4. **What is left to test.** The temperature part is done. The open part is the chemistry: at a fixed temperature, does a setting's own pH, Mg and salt make RNA last longer or shorter than plain control water? See the prereg, arm K3.

## The rate law (task 2)

Li & Breaker 1999 (J. Am. Chem. Soc. 121:5364–5372, doi:10.1021/ja990592p) is paywalled. **I did not open it.** Two open-access papers reproduce its rate law with the same parameters.

**Source 1 (opened).** Wayment-Steele HK, Kim DS, Choe CA, et al. 2021. Theoretical basis for stabilizing messenger RNA through secondary structure design. Nucleic Acids Res. 49:10604–10617. doi:10.1093/nar/gkab764. PMC8499941. CC BY 4.0. Methods, "Quantitative model for RNA hydrolysis":

```
k_projected = k_background × 10^(0.983 (pH − 6)) × 10^(−0.24 (3.16 − [K+]/1 M))
              × 10^(0.07 (T − 23 °C)) × 69.3 ([Mg2+]/1 M)^0.80 × 3.57 ([K+]/1 M)^(−0.419)
```

- k_background = 1.30 × 10⁻⁹ min⁻¹, "which represents the model's selected reference point: pH 6, 23°C, [K+] = 3.17 M".
- Verbatim: "The above equation was parametrized from measurements with [Mg2+] concentrations between 0.005 and 0.01 M; for conditions with 0 M Mg2+, we omit the last two terms."
- It is a rate per phosphodiester bond. They multiply by length and by the unpaired fraction (0.4) to get a rate per molecule.
- The equation text writes 3.16 and the sentence after it writes 3.17 M. The paper does not explain the difference.

**Source 2 (opened).** Schwintek P, et al. (Braun and Mast groups) 2025. Prebiotic gas flow environment enables isothermal nucleic acid replication. eLife. doi:10.7554/eLife.100152. PMC12240584. CC BY 4.0. Appendix 8, equation 19:

```
k_hyd [1/min] = L · k_bg · 10^(0.983 (pH − 6)) · 10^(−0.24 (3.16 − [K+])) · 10^(0.07 (T − 23))
                · 3.57 [K+]^(−0.419) · 69.3 [Mg2+]^0.8
```

- k_bg = 1.3 × 10⁻⁹ min⁻¹; L is the oligomer length; concentrations are in molar.
- Verbatim: "We used Na+ instead of K+ in the experiment, but assumed here, that the K+ correction would be similar for this calculation."

**Units.** k in min⁻¹ per linkage. T in °C. Concentrations in mol/L.

**Valid ranges. Only partly confirmed.**

| Variable | What an opened source says | Status |
|---|---|---|
| Mg²⁺ | Fitted between 5 and 10 mM (Wayment-Steele) | Confirmed second-hand |
| K⁺ | Reference point 3.17 M. Used at 0.14 M (Wayment-Steele) and 1 M (Cohen, quoting Li & Breaker) | Fitted range not confirmed |
| Temperature | Reference 23 °C. Used at 5–37 °C (Wayment-Steele) and 45 °C (Schwintek) | Fitted range not confirmed |
| pH | Reference pH 6. Used at 7–9.5 | Fitted range not confirmed |

Someone with legal access to the JACS paper must read the fitted ranges before sealing.

**Checks I ran (`scripts/rate_law_gate.py`, published lab numbers only, no field data).**

- Wayment-Steele Table 1: my code matches 5 of 6 printed rates within 1%. The sixth (in vitro transcription, 37 °C, pH 7.6, 14 mM Mg) comes out 2.2× lower than printed. I could not find the cause from the printed inputs.
- Schwintek Appendix 8 prints 8.917 × 10⁻⁶ min⁻¹ (200 µM Mg) and 3.231 × 10⁻⁵ min⁻¹ (1 mM Mg) for a 24-mer at 45 °C, pH 7. The paper does not print the K⁺ value it used. K⁺ = 1 mM reproduces both numbers exactly. This is my back-calculation, not a statement in the paper.

**Three ways the formula misbehaves outside its fitted range** (arithmetic on the formula, not results):

1. **Low Mg.** The Mg × K term is below 1 when Mg is small. At 0.14 M K⁺ the formula says Mg *slows* cleavage below 0.36 mM Mg; at 10 mM K⁺, below 0.09 mM.
2. **Low salt.** With Mg present, K⁺^(−0.419) grows without limit as K⁺ goes to zero. Field waters are dilute and Na-dominated.
3. **Temperature.** The rate rises tenfold per 14.3 °C with no upper limit. Vent fluids reach several hundred °C. Any verdict on hot water is made by this one term.

It also has no acid-catalysed term, so it will call acid springs safe. Bernhardt & Tate put the stability optimum at pH 4–5.

## Extension rates (task 2)

| System | k_ext or yield | Conditions | Source | Status |
|---|---|---|---|---|
| Nonenzymatic primer extension, 2-aminoimidazole-activated G | 3.7 h⁻¹ plateau (monomer AI-G); 27 h⁻¹ plateau with an activated downstream helper (bridged dinucleotide or OAt-G) | 100 mM MgCl₂, 250 mM NaCl, 100 mM Tris pH 8; one-nucleotide extension; detection limit 10⁻² h⁻¹ | Walton T, Pazienza L, Szostak JW. 2019. Biochemistry 58:755–762. doi:10.1021/acs.biochem.8b01156. PMC7547881 | Opened |
| Nonenzymatic extension in natural soda-lake water | "comparable" one-nucleotide rate to the lab standard (50 mM MgCl₂, pH 8). Values are in Fig. 2C only. No primer hydrolysis seen at 72 h; partial hydrolysis at 6 days | Lake water: about 1 M Na⁺, about 1 mM Mg²⁺, pH 10 | Cohen ZR, et al. 2024. PNAS Nexus 3:pgae084. doi:10.1093/pnasnexus/pgae084. PMC10949909 | Opened. Numbers not in text |
| Nonenzymatic, generic | "1 hr⁻¹", attributed to Walton et al. 2019 | not given | Schwintek 2025, Appendix 8 | Opened (as a quote) |
| Polymerase ribozyme (class I lineage, 24-3) | "72 hr⁻¹" per base, attributed to Tupper & Higgs 2021 and Horning & Joyce 2016 | not given | Schwintek 2025, Appendix 8 | Quote opened. **Horning & Joyce 2016 (doi:10.1073/pnas.1610103113) opened in round 2** at https://pmc.ncbi.nlm.nih.gov/articles/PMC5024611/: "average rate of primer extension" of 1.2 nt/min for the 24-3 polymerase (72 h⁻¹), at 200 mM MgCl₂, 50 mM Tris pH 8.3, 17 °C; wild type 0.012 and tC19Z 0.005 nt/min. Tupper & Higgs 2021 not opened |
| QT51 (parent of QT45), one ligation step | k_obs = 0.06 min⁻¹ | −7 °C frozen, pH 9, 50 mM MgCl₂ | Gianni E, et al. 2026. Science 391:1022–1028. doi:10.1126/science.adt2760. PMC7618777 | Opened |
| QT45, full length | about 0.2% yield in 72 days for each strand; per-nucleotide fidelity 94.1% | −7 °C frozen, pH 9, 0.4 mM MgCl₂ | Gianni 2026; also `experiments/qt45_numbers/RESULTS.md` | Opened |
| QT45, measured decay | half-life about 117 days; R18 about 16 days | −7 °C frozen, pH 9, 50 mM MgCl₂ | Gianni 2026 (text, fig. S8) | Opened |
| Triplet polymerase ribozyme (TPR; 5TU/t5+1 lineage) | 1.2–1.38-fold per pH/freeze-thaw cycle | synthesis at −7 °C, pH 9, 1 mM MgCl₂; strand separation at pH 3.6, 80 °C | Attwater J, et al. 2025. Nat. Chem. 17:1129. doi:10.1038/s41557-025-01830-y. PMC12226338 | Opened. No per-nucleotide rate found |
| 52-2 polymerase | — | — | — | Not found in an opened source |

Two warnings.

- Every k_ext was measured in a lab buffer (pH 8–9, 50–100 mM Mg, or eutectic ice). None was measured as a function of field T, pH and Mg. Using a lab k_ext for a field sample gives an upper bound on copying.
- A one-step rate is not a full-length rate. QT51's 0.06 min⁻¹ step does not match QT45's 0.2% full-length yield in 72 days.

## Papers

### Papers that already state the result

**Bernhardt HS, Tate WP. 2012.** Primordial soup or vinaigrette: did the RNA world evolve at acidic pH? Biol. Direct 7:4. doi:10.1186/1745-6150-7-4. PMC3372908. **Opened.**
- Found: "RNA is most stable at pH 4-5 and is unstable at alkaline pH". They argue against an RNA world in alkaline vents such as Lost City.
- Bears on T3: the "alkaline vents are bad for RNA" claim is theirs. They use pH and temperature only. No Mg, no field database, no copying rate.

**Kua J, Bada JL. 2011.** Primordial ocean chemistry and its compatibility with the RNA world. Orig. Life Evol. Biosph. 41:553–558. doi:10.1007/s11084-011-9250-5. **Opened in round 2** (the article page at https://link.springer.com/article/10.1007/s11084-011-9250-5 is readable without a login; Unpaywall lists it as closed).
- Method: pH and temperature only. Five representative pH values: 3.5 (acidic vent), 5.4, 6.7, 8 and 10 ("alkaline hydrothermal vent (e.g., Lost City)"). Phosphodiester data from Linjalahti & Mikkola 2007 (a 13-mer oligo-U, pH 2–12, 35 and 90 °C; not opened).
- Found: phosphodiester half-lives at 25 °C of 2, 29, 51, 32 and 2 years at pH 3.5, 5.4, 6.7, 8 and 10. "Even the lower temperature alkaline hydrothermal vents would show half-lives of less than a day at 75°C."
- On Mg, one sentence only: "Minerals and dissolved ions may alter the decomposition rates. Li and Breaker (1999) have measured the accelerated kinetics of phosphodiester bond cleavage in the presence of Mg2+."
- Bears on T3: the nearest prior study. It has no Mg term, no salt term and no field database. So the temperature and pH part of T3 is done, and the field-chemistry part (K3) is not pre-empted.

**Le Vay K, Mutschler H. 2020.** Nucleic acid catalysis under potential prebiotic conditions. Chem. Asian J. 15:214–230. doi:10.1002/asia.201901205. PMC7003795. **Opened.**
- Found: "environments with a high concentration of Mg2+ and high temperatures, such as hydrothermal vents, are unsuitable settings for RNA-based scenarios of molecular evolution." Cites Li & Breaker for half-lives of minutes.
- Bears on T3: states the vent verdict outright. But it assumes vents are Mg-rich. Field data can check that premise.

**Miller SL, Bada JL. 1988.** Submarine hot springs and the origin of life. Nature 334:609–611. **Named** (search snippet only).
- Reported to extrapolate a phosphodiester half-life of minutes at 250 °C and seconds at 350 °C.
- Bears on T3: the hot-vent kill is 38 years old.

### Papers that do part of the T3 calculation

**Schwintek et al. 2025** (details above). **Opened.**
- Found: for a 24-mer at 45 °C, pH 7, 50–200 µM Mg, they compute a hydrolysis half-time near 2,000 hours with the Li & Breaker law, and state: "The timescale of replication using prebiotically plausible machinery therefore out-competes the hydrolysis in the experimental settings used here."
- Bears on T3: this is the T3 comparison (copy time against cleavage time) for one lab condition. It claims RNA persists long enough in a heated gas-flow pore.

**Wayment-Steele et al. 2021** (details above). **Opened.**
- Found: the rate law, with worked rates for mRNA storage conditions.
- Bears on T3: source of the rate law, and a published table to test the code against.

**Cohen ZR, Ding D, Zhou L, DasGupta S, Haas S, Sinclair KP, Todd ZR, Black RA, Szostak JW, Catling DC. 2024** (details above). **Opened.**
- Found: in water from Last Chance Lake and Goodenough Lake, nonenzymatic extension ran at lab-like rates. "We did not observe hydrolysis of RNA primers after 72 hours in natural or artificial lake water", "roughly consistent with previous estimates of ∼1% RNA degradation after 72 hours in 1 M K+ and 5 mM Mg2+ at pH 9.5" (citing Li & Breaker). "The relatively low concentration of divalent cations may compensate for the high pH".
- Bears on T3: a direct measurement in field water for the soda-lake setting. It is the claim "RNA persists long enough in setting X" for lakes. It is also the best known-answer check for the rate law.

**Mojarro A, Jin L, Szostak JW, Head JW, Zuber MT. 2021.** In search of the RNA world on Mars. Geobiology 19:307–321. doi:10.1111/gbi.12433. PMC8248371. CC BY 4.0. **Opened.**
- Found: measured cleavage of a single RNA linkage against pH (3.2–9) and metal (Mg²⁺, Fe²⁺, Mn²⁺ up to 50 mM). Metals speed cleavage at nearly all pH. Slowest cleavage with Mg at pH 5.4. At pH 3.2 more metal means slower cleavage.
- Bears on T3: an independent measured data set to test the rate law's pH and Mg terms. It also shows Fe²⁺ and Mn²⁺ cleave RNA faster than Mg²⁺ at pH 5.4–8. The Li & Breaker law has no Fe or Mn term, and vent fluids are rich in both.

**Guth-Metzler R, et al. 2023.** Goldilocks and RNA: where Mg²⁺ concentration is just right. Nucleic Acids Res. 51:3529–3539. doi:10.1093/nar/gkad124. PMC10164553. **Opened** (abstract and methods).
- Found: Mg both cleaves RNA and protects it by folding it. Folded RNAs show a lifetime peak at intermediate Mg. Measured at 65 °C, pH 7.1, 180 mM NaCl.
- Bears on T3: the rate law is for unstructured RNA. A folded ribozyme or a duplex lasts longer. T3 gives a lower bound on lifetime for structured RNA.

**Gianni et al. 2026** and **Attwater et al. 2025** (details above). **Opened.**
- Bear on T3: they claim the ice setting works. Gianni say the syntheses need "further improvements in synthetic efficiency and fidelity likely required to overcome chemical degradation". The repo's own analysis (`experiments/qt45_numbers/RESULTS.md`) found decay about 210 times faster than synthesis for QT45.

**Walton et al. 2019** (details above). **Opened.** Source of the nonenzymatic k_ext.

### Named, not opened

- **Li & Breaker 1999** (the rate law). Paywalled. **Not opened; to be requested.** Round 2 search: Unpaywall lists no open copy; no PMC or repository copy found.
- **Oivanen M, Kuusela S, Lönnberg H. 1998.** Chem. Rev. 98:961–990. doi:10.1021/cr960425x. Named in Wayment-Steele and Mojarro. Likely source for acid catalysis and activation energies.
- **Tupper & Higgs 2021.** Ribozyme polymerase rate (Horning & Joyce 2016 is now opened; see the extension-rate table).
- **Deamer D, Damer B, Kompanichenko V. 2019.** Hydrothermal chemistry and the origin of cellular life. Astrobiology. doi:10.1089/ast.2018.1979. Not open access. A search snippet says it tabulates Lost City, Kamchatka and Yellowstone water chemistry and argues from it. Must be read: it may already do a field-chemistry comparison for hot springs. **Not opened; to be requested.** Unpaywall lists it as closed; a ResearchGate copy answered 403 and was left alone.
- **Levy & Miller 1998**; **Larralde et al. 1995.** Nucleobase and ribose stability. These are in the plan's data column. They concern other bonds, not the phosphodiester bond.
- **Martin & Russell 2003** (doi:10.1098/rstb.2002.1183), cited by Le Vay & Mutschler as the vent scenario.
- **Haas S, Sinclair KP, Catling DC. 2024.** Commun. Earth Environ. 5:28. doi:10.1038/s43247-023-01192-8. Soda-lake water chemistry.
- **Diehl & Bach 2020.** Geochem. Geophys. Geosyst. 21:e2020GC009385. doi:10.1029/2020GC009385. The MARHYS description paper. **Not opened; to be requested.** Unpaywall lists it as hybrid open access (CC BY) at Wiley, but the Wiley server answered 403 to the script and this was not worked around. A person can open it in a browser. In its place I read the documentation rows inside the database file (quoted in the prereg).

### Opened in round 2 (rate-law cross-checks)

- **Breaker et al. 2003.** "A common speed limit for RNA-cleaving ribozymes and deoxyribozymes" (journal RNA). PMC1370461. Opened. Quote: the "uncatalyzed rate constant" is "~10⁻⁸ min⁻¹ (Li and Breaker 1999) under near physiological conditions (pH 7.0, 250 mM K+, 5 mM Mg2+, 23°C)". Our coded law gives 1.60e-8 min⁻¹ there. Used as gate G3.
- **Emilsson et al. 2003.** "Ribozyme speed limits" (journal RNA). PMC1370456. Opened. 2′-OH pKa 13.7 at 23 °C and 250 mM K⁺; maximum rate about 0.02 min⁻¹; log-rate slope of one under basic pH. Used for the pH ceiling of tier B.
- **Cohen 2024, second reading.** Reactions "performed at room temperature". Primer length not found in the text. It quotes Li & Breaker as "∼1% RNA degradation after 72 hours in 1 M K+ and 5 mM Mg2+ at pH 9.5"; our law gives 1.66% per linkage. Used as gate G4.

## To be requested (draft note; not sent)

Three papers are still unread: Li & Breaker 1999 (doi:10.1021/ja990592p), Deamer, Damer & Kompanichenko 2019 (doi:10.1089/ast.2018.1979) and Diehl & Bach 2020 (doi:10.1029/2020GC009385). The third is open access and only needs a person with a browser. For the first two, a library login or a note to an author is the legal route. Draft, for the owner to edit and send if they wish:

> Hi Ron,
>
> Thank you for your 1999 paper with Dr Li on how fast RNA breaks at the 2′-hydroxyl. More than twenty-five years on, people still use its rate equation, and we would like to use it too.
>
> We are a small open project. We want to ask how long RNA would last in real waters, such as vents, hot springs and soda lakes. We only know your equation second-hand, from Wayment-Steele et al. 2021 and Schwintek et al. 2025, and we cannot reach the paper itself (doi:10.1021/ja990592p).
>
> Could you send us a copy? Two things matter most to us: the ranges of temperature, pH, K⁺ and Mg²⁺ that the fit covers, and the uncertainty on each fitted number. We want to stay inside those ranges and say so plainly.
>
> Thank you for your time, whatever you decide.
>
> [name]

The same note works for David Deamer with the middle changed: we need the paper's own wording of the hot-spring claim and its table of water chemistry, so that we quote it exactly.

## Field data (task 3)

All files are in `raw/`. I looked only at column names, units, category labels and counts of non-empty cells (`scripts/probe_columns.py`, `scripts/probe_marhys_labels.py`). I printed no value of T, pH, Mg or any ion.

| Setting | Dataset | URL opened | Licence | Login | In repo |
|---|---|---|---|---|---|
| Marine vents | MARHYS 4.0. Diehl A, Bach W. 2024. PANGAEA. 6,788 merged sample entries (abstract) | https://doi.org/10.1594/PANGAEA.972999 | CC BY 4.0 (stated on the record) | Single files: no. The all-files ZIP needs a PANGAEA account | `raw/marhys4/MARHYS_DB_4_0.xlsx` (5.3 MB) |
| Hot springs | USGS Yellowstone water chemistry, ver. 2.0 (March 2025). McCleskey RB, et al. 845 samples, 147 columns | https://doi.org/10.5066/P92XKJU7 (ScienceBase item 618be315d34ec04fc9c7fb1f) | US public domain for the most part (metadata use constraint) | No | `raw/usgs_ynp_p92xkju7/YNP_WQ.csv` (0.46 MB) |
| Hot springs, long record | USGS historic Yellowstone water chemistry 1883–2021. Price MB, et al. 2024. 4,918 samples, 117 columns | https://doi.org/10.5066/P9KSEVI1 (ScienceBase item 64e4d56bd34e736b81e18584) | Same | No | `raw/usgs_ynp_historic_p9ksevi1/` (2.1 MB) |
| Lakes, ponds (control) | The same two USGS files. Their water-type field has "lake", "river, stream, or creek", "seep", "snow" | as above | as above | No | as above |
| Soda lakes | Cohen 2024 SI Tables S1–S3 (two lakes); Haas 2024 | not downloaded | — | — | Not in repo |
| Ice | No field chemistry data set found | — | — | — | — |

Columns found:
- MARHYS: one sheet, 6,804 rows by 205 columns. Sample type (HF, EM, SW, STD), geologic setting, rock type, Tsample, Tmax, Tcalc, T (°C), pHmeas, pHmin, pHcalc, pH, Mg, K, Na, Ca, Fe, Mn (mmol/kg or µmol/kg), and more.
- USGS ver. 2.0: field pH in 802 rows, water temperature in 722, dissolved Mg, K, Na, Ca in 808 each.
- USGS historic: field pH in 3,334 rows, temperature in 3,760, Mg in 3,284, K in 3,698, Na in 3,722.

Known traps, to check in the MARHYS paper before sealing:
- "EM" rows are calculated end members. The header text says Tcalc and pHcalc are calculated. End-member Mg is conventionally set to zero. Using EM rows would put Mg = 0 in by assumption.
- Vent pH is usually measured on deck at about 25 °C, not at vent temperature.
- The USGS files overlap. Samples from 2009 on may be in both.

## Searches run

- Web search, 14 queries, on: RNA half-life across prebiotic settings; the Li & Breaker equation; replication against degradation; field measurements of RNA in natural water; a database-driven habitability map for RNA; QT45; MARHYS; USGS Yellowstone; Kua & Bada; Mojarro; soda lakes.
- Europe PMC search and full-text fetch, 12 records. Several requests timed out or returned 503. I did not retry more than once.
- Not searched: Google Scholar citation trails for Li & Breaker 1999 and Kua & Bada 2011. A person should check "cited by" for both.
