# Research sweep and citation audit (tasks #1 and #14)

**Verdict: every citation in the founding plan and on the site resolves to a real DOI, but the site and plan contained five wrong claims and two wrong attributions, now fixed. The biggest correction: exponential RNA replication by a ribozyme was shown in 2025 (Attwater et al., Nature Chemistry), so "no exponential growth yet" was wrong. And QT45's yield is about 0.2% in 72 days, not the plan's second-hand 0.02%.**

Agent: orig-sweep. Date: 2026-11-18.

## What was produced

- `docs/PAPERS.csv`: 62 papers, all resolved on Crossref by DOI (verified = yes for all 62). Columns: theory, authors, year, venue, doi, claim, verified, checked_against, cited_in, note.
  - 32 rows had their claim checked against the abstract, and 7 of those also against the full text (Glavin, Furukawa, Altair, Xavier, Ozturk via Europe PMC/nature.com).
  - 30 rows are checked on metadata only (title, authors, venue, year). Their claim column paraphrases only the title. `checked_against` says which.
- `site/news.json`: 19 items, all `verified: true`, all URLs now `https://doi.org/...` links. 7 existing items corrected, 12 added (15 latest, 4 landmark).
- `site/content.json`: theory rows, ladder and pathway map corrected, and a Lipid world row added (below). A copy of the pre-edit file is in `content.before.json`.
- The site was rebuilt with `python3 -I site/build.py`.

## Wrong claims found and fixed

| Where | Was | Source says | Fix |
|---|---|---|---|
| fable_plan L3 | QT45 "net gain about 0.02% over 72 days" (second-hand) | ~0.2% yield in 72 days, both self-copy and complement (abstract, doi:10.1126/science.adt2760) | site says ~0.2% yield; plan left as written, corrected here |
| content.json RNA world | "there is no exponential growth yet" | Attwater et al. 2025 (doi:10.1038/s41557-025-01830-y): exponential replication of both strands of short dsRNAs, including a ribozyme fragment, with supplied triplets and pH/freeze-thaw cycles | rewritten; L3 stays "Not met" because the whole replicator was not copied from scenario feedstocks |
| news.json Bennu | "the amino acids are racemic"; "uncontaminated" | the chiral non-protein amino acids that could be resolved were racemic or near racemic; racemic Ala and Asp mean negligible contamination; samples "pristine" (full text) | rewritten |
| content.json homochirality | "about 35% excess after recrystallisation" | ~60% ee at best and ~35% on average; above ~25% ee, a further crystallisation gives 100% ee (full text, PMC10246896) | rewritten with both numbers |
| fable_plan cyanosulfidic | Wołos et al. 2020 cited as showing that the network "needs ordered delivery" | the paper is a computational forward-synthesis network with a self-regenerating cycle; it does not make that claim | noted; the site never cited Wołos |
| fable_plan assembly | "Uthamacumaran, Abrahão & Zenil 2024 (PLOS Complex Systems)" | the PLOS Complex Systems paper is Abrahão, Hernández-Orozco, Kiani, Tegnér & Zenil (doi:10.1371/journal.pcsy.0000014); the Uthamacumaran paper is npj Syst Biol Appl 10:82 (doi:10.1038/s41540-024-00403-y) | both cited correctly on the site |
| fable_plan assembly | "Walker et al. 2024" with no venue | J R Soc Interface 21:20240367 (doi:10.1098/rsif.2024.0367); the claim matches its abstract | venue added |

Smaller fixes:
- **Dates.** Furukawa is Nature Geoscience 19:19-24, online 2025-12-02, issue January 2026. QT45 was online 2026-02-12, issue dated March 2026.
- **Goldford.** Goldford 2017 is Cell 168:1126, DOI 10.1016/j.cell.2017.02.001.
- **Plan citations marked "(memory)" are real.** Pressman 2019 is JACS (DOI 10.1021/jacs.8b13298), Kobori & Yokobayashi 2016 is Angew Chem (10.1002/anie.201605470), and Marshall 2021 is Nat Commun (10.1038/s41467-021-23258-x).
- **Old news URLs.** All seven old news URLs pointed at journal homepages. Each now points to its DOI.
- **Singh 2025 headline.** The news headline was a paraphrase. It now uses the paper's real title.

Confirmed as stated in the plan:
- **Glavin.** 33 amino acids, 14 of them proteinogenic, and all five nucleobases.
- **Furukawa.** Ribose 0.097 and glucose 0.35 nmol/g, with no deoxyribose.
- **Singh.** Nature 644:933.
- **QT45.** Science 391:1022.
- **Papastavrou.** PNAS 121:e2321592121.
- **Hudson 2020.** No product without the pH gradient.
- **Altair 2025.** Micromolar formic and acetic acid on the ocean side.
- **Xavier 2020.** A maxRAF of 1,335 reactions, 25% of the network.
- **Hazen 2024.** Assembly indices up to 21 (ewingite, ilmajokite).
- **Kempes 2025.** npj Complexity 2:27.
- **Moody 2024.** About 4.2 Ga, an anaerobic acetogen, Nat Ecol Evol 8:1654.
- **Luque 2025.** A&A 700:A284.
- **Weiss 2016 and Crapitto 2022.**

## Content changes

- **Theory scoreboard.**
  - Warm ponds moved from "Untested" to "Partial". For: Caimi 2025, where wet-dry cycling polymerises cyclic nucleotides without activators. Against: the chains stay short (0.1% reach 10-mers), and in Šimonis 2026, water from one Icelandic spring destroyed about 90% of A10/U10 in 4 cycles.
  - Lipid world row added, status Untested. Evidence: Baba 2026 (peptide sequence tunes vesicle growth) and Khanal 2026 (de novo bilayers, but made with enzymes).
  - The assembly row now cites both sides with venues: Hazen, Uthamacumaran, Abrahão, Ozelim vs Walker, Kempes.
- **Pathway map.**
  - The building-blocks step adds Ryugu's five nucleobases (Koga 2026).
  - The polymers step adds Caimi 2025.
  - The exponential replication step adds Attwater 2025. It stays "Not met".
  - The compartments step moved from "Untested" to "Partial".
  - The pond scenario's "explains" and "gap" text was rewritten.
- **Ladder.** L2 now gives QT45's yield. L3 notes that short-RNA exponential replication has been shown.

## Not checked

- **Metadata-only rows.** For the 30 `Crossref metadata` rows in PAPERS.csv, only the title, authors, venue and year were checked, not the claims inside. None of them is used for a number on the site.
- **Miller 1953.** The full text is paywalled. The news item quotes no yields. The gases and the one-week run come from the bibliographic record and an encyclopaedia summary.
- **QT45 body text and supplement.** These were not opened (Science returns 403). Task #2 needs the deposit.
- **Not edited.** `docs/fable_plan.md` and `README.md` were not edited, because they belong to the lead. The README's L2/L3 wording is still correct under its own definition. The plan's 0.02% figure and its Wołos and Uthamacumaran attributions should be corrected by the lead.
- **Search scope.** Crossref keyword search plus web search. This is not a systematic review, and wet-dry and lipid papers in other venues may be missing.
- **Downloads.** The raw full texts used (1.0 MB in `raw/`) were deleted after checking. No statistical tests were run, so there are no ledger rows.

## Hypotheses this suggests (added as board tasks)

| Idea | Why | Task |
|---|---|---|
| Decide whether thermophoretic crack purification counts as a "named physical process" in the compatibility rule | Matreux 2024 raised a downstream yield by 10^5 by purifying in cracks | #20, closed: the hashed rule already allows thermophoresis up to 1000x, matching Matreux |
| Purine:pyrimidine ratio vs NH3 across returned samples | Koga 2026 reports a negative correlation across Ryugu, Bennu and Orgueil; it can be sealed as a prediction for the next sample table | M5 |
| Attwater 2025 net growth per cycle | gives the number L3 needs: does a full-length replicator's net copy rate exceed 1 per cycle at reported fidelity? | M2 |
| Pond step table from Caimi 2025 + Šimonis 2026 | first quantitative wet-dry steps | M2 |
| Red-team this audit | rule: never red-team your own result | M6 |
