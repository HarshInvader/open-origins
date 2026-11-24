# T5 result: Wehbi 2024's "88.6% agreement with Moody" is mostly a base rate

Prereg: `docs/prereg/t5_wehbi_moody_base_rate.md`, sealed in 2038f94 (`HASHES.txt`). Script: `scripts/t5_analysis.py` (sha256 f80a1969…). Output: `results/t5_real.json`.

## Claim

Wehbi et al. 2024 (PNAS, doi:10.1073/pnas.2410311121) write: "88.6% of Pfams that we annotate as pre-LUCA or LUCA are contained within genes annotated by Moody et al. as present in LUCA with more than 50% confidence ... This level of agreement far exceeds earlier works". The Fig. 3 caption says their LUCA Pfams "are well validated by the whole gene annotations of Moody et al." No rate was given for younger Pfams.

## Sealed verdict: kill

| | Share agreeing with Moody (PP > 0.5) |
|---|---|
| A: LUCA and pre-LUCA Pfams (n = 953) | **88.7%** (reproduces the published 88.6%) |
| B: post-LUCA (LBCA/LACA) Pfams matched on the number of Moody COGs they map to | **80.6%** |
| G = A − B | **8.1 points**, 95% CI 5.6 to 10.5 (clan bootstrap) |

Kill rule: G < 10 and the upper bound < 20. Both hold. The agreement does not validate the LUCA annotations: Pfams that Wehbi date *after* LUCA agree with Moody's LUCA calls 80.6% of the time once breadth is matched.

## Why: breadth

A Pfam counts as agreeing if any of the COGs it maps to has PP > 0.5. Old Pfams map to more COGs, a median of 4 against 2. Within each breadth bin the two groups are close, and above 16 COGs both reach 99–100%:

| Mapped COGs | 1 | 2 | 3 | 4 | 5–8 | 9–16 | 17–32 | 33–64 | 65+ |
|---|---|---|---|---|---|---|---|---|---|
| LUCA/pre-LUCA, % (n) | 45 (40) | 46 (52) | 66 (65) | 77 (53) | 90 (179) | 97 (202) | 100 (176) | 100 (106) | 100 (80) |
| post-LUCA, % (n) | 27 (439) | 42 (393) | 50 (320) | 59 (230) | 74 (537) | 89 (368) | 99 (250) | 100 (134) | 100 (45) |

Shuffling Moody's PP among COGs of similar size, with no age information at all, gives A = 87.2% on average (97.5th percentile 89.2%). The published 88.6% sits inside that floor.

## But there is a small real signal

G is well above the shuffle floor (floor G 0.4, 95% range −1.8 to 2.7; p ≈ 0.0005). LUCA Pfams do agree with Moody somewhat more than matched younger Pfams: about 8 points, or 7–13 across the reported variants. The validation is real but weak, not "far exceeds".

## Reported only (no rule)

| Variant | G (95% CI) |
|---|---|
| Finer breadth bins | 8.0 (5.6, 10.5) |
| PP > 0.75 | 8.1 (5.3, 11.0) |
| Mean share of a Pfam's COGs over 0.5 (no "any" rule) | 8.7 (7.0, 10.5) |
| Map requires ≥ 2 shared proteins | 10.7 (8.0, 13.3) |
| Matched on PP-bearing COGs only | 12.7 (10.1, 15.6) |
| Moody's COG-level PP (Supp. Data 2) instead of Supp. Data 1 | 10.4 (6.9, 14.2) |
| Old = LUCA only | 8.6 (5.9, 11.2) |
| Old = pre-LUCA only | 3.7 (1.1, 6.9) |
| Post = LBCA only | 8.7 (6.3, 11.1) |
| Post = LACA only | −2.2 (−6.2, 2.1) |

- Three variants land just above the 10-point kill line, in the "partly informative" zone. None comes near the 30-point support line. So the reading "mostly base rate, small real signal" holds across variants. The kill is on the sealed primary.
- Wehbi's *pre-LUCA* Pfams, the oldest class, have the smallest gap: 3.7 points.
- Post-LUCA *archaeal* (LACA) Pfams agree with Moody's LUCA calls at least as often as LUCA Pfams do.

## Gate and disclosures

- **Gate.** A = 845/953 = 88.67%. All 969/969 of Wehbi's per-Pfam flags (`MoodyPfams_probabilities.csv`) reproduce.
- **PP source.** The PP column is `constrained_median` from Moody Supplementary Data 1, taken at each KEGG family's modal COG. The repo's COG-level table fails the gate (80.3%). Wehbi's flag-building script is not deposited, so the rule was inferred from the caption and the flags, then confirmed by the 969/969 match.
- **Accidental view.** Two COG-level PP values were printed by accident before the seal (COG0001 and COG0002, from a file not used in the primary). This is disclosed in the prereg.

## What it means for us

- T2 used Wehbi's per-amino-acid LUCA usage values. This result does not touch those values. It says only that the Moody cross-check, offered as validation of which Pfams are LUCA-era, is weak evidence.
- It is a small, self-contained correction with fully deposited data. It is a candidate for a short note to the authors (warm, first names, facts exact; the owner decides).
