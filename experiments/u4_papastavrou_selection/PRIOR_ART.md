# Prior art for U4: was the hammerhead lost to fidelity, or to weaker selection?

Written before any number was computed from the deposit. Everything quoted below was opened in this
repo and saved under `raw/` (gitignored). Titles, DOIs and author lists come from Europe PMC, bioRxiv
or Zenodo metadata saved there. All requests used User-Agent `open-research-site/1.0` and carried no
personal details. No paywall or bot block was worked around.

**Verdict: the fidelity-versus-selection question is named in the literature but has never been
measured.** The authors name imperfect selection stringency themselves; the accompanying PNAS
commentary names the selection-strength escape route explicitly. Neither, nor any of the 58 citing
records screened, splits the per-round change into a copying part and a selection part.

## Papers read

### 1. The paper under test

Papastavrou N, Horning DP, Joyce GF. 2024. "RNA-catalyzed evolution of catalytic RNA." PNAS 121,
e2321592121. doi:10.1073/pnas.2321592121, PMC10945747, PMID 38437533. Full text read from
`raw/europepmc/PMC10945747.xml`. The SI Appendix (`pnas.2321592121.sapp.pdf`) could **not** be
opened: Europe PMC's article page returned 403 for the file, the PMC open-access package service
returned 404 (the article is CC BY-NC-ND, not in the OA subset), and the Europe PMC
`supplementaryFiles` zip bundles Movie S1, which would exceed this task's 5 MB download limit. So
SI Tables S1-S3 and the SI Methods are **not verified here**; the figure-data deposit does contain
`figure_data/Papastavrou_23_fidelity_Table_S2_and_S3.xlsx` (224,933 bytes uncompressed), which is the
spreadsheet that builds those tables from the base-call files.

The fidelity claim (verbatim):

> "Beginning with the Seq0 hammerhead ribozyme as a template, the 52-2 polymerase synthesizes HHR–
> (in 200 mM Mg 2+ ) with a single-pass fidelity of 85.6% per nucleotide. The resulting HHR– RNAs in
> turn direct the synthesis of new copies of HHR+ with 81.4% overall fidelity for the reciprocal
> synthesis of HHR– and HHR+. In contrast, the 71-89 polymerase (in 50 mM Mg 2+ ) synthesizes HHR–
> with 90.9% single-pass fidelity, and carries out reciprocal synthesis of HHR– and HHR+ with 89.1%
> overall fidelity (SI Appendix, Tables S2 and S3)."

What bears on the fidelity-versus-selection question:

- **The authors say selection was imperfect, in the arm that lost function** (verbatim): "Even though
  the 52-2 lineage lost hammerhead functionality, it could still be propagated (Fig. 2A). This
  behavior partly reflects the small but dwindling portion of the population that retain catalytic
  activity, but is also due to imperfect stringency of selection. Catalytically inactive RNAs can
  still be released from the streptavidin-coated beads due to uncatalyzed cleavage of the RNA
  substrate during the 30-min incubation in the presence of 20 mM MgCl 2 . In addition, there likely
  is imperfect exclusion of a small amount of uncleaved materials. These mechanisms can be
  significant relative to the small amount of functional hammerheads produced by the low-fidelity
  52-2 polymerase but have little consequence compared to the strong signal of hammerhead-catalyzed
  cleavage that is maintained throughout the 71-89 lineage (Fig. 2B)." The leak is named and argued
  to matter more in the 52-2 arm. It is not quantified, and nothing is replayed with it removed.
- **They know the threshold depends on selection strength** (verbatim): "This observation derives in
  part from a high-stringency selection process that enables superior sequences to prevail against
  their competitors, thereby easing the error threshold by a factor of the natural log of the
  superiority of the most advantageous variants (8)." Reference 30 for the relaxed threshold is Kun,
  Santos & Szathmáry 2005, Nat Genet 37, 1008-1011, doi:10.1038/ng1621 (reference metadata only; not
  opened).
- **Fidelity and Mg2+ are confounded, and the authors say so** (verbatim): "Much of the improved
  fidelity can be attributed to the ability of the 71-89 polymerase to operate in the presence of
  50 mM Mg 2+ , whereas the 52-2 polymerase requires 200 mM Mg 2+ to replicate RNAs as complex as the
  hammerhead (17)."
- **A partial decomposition already exists, but only inside the 71-89 arm.** For Fig. 4B the authors
  took Seq0 and five peak variants through one round, separately and mixed, and compared fitness from
  "the relative yields of plus- and minus-strand synthesis and RNA-cleavage activity" against
  "relative enrichment of progeny RNAs in a competition experiment". They also estimated each
  variant's specific activity by "multiplying its observed activity by the fraction of functional
  progeny", where the functional fraction came from "the fraction of pre-cleaved HHR+ RNA sequences
  from each individually propagated population that are consistent with the hammerhead motif". So
  replicability and catalysis are separated **per variant, for one round, with the 71-89 polymerase
  only**. Nothing of this kind is done per round, and nothing is done for the 52-2 lineage.
- The sequencing design that U4 needs is stated: "with corresponding HHR– RNAs and HHR+ RNAs that had
  not undergone hammerhead cleavage" were also sequenced, and round-1 fidelity was computed from
  "Sequences of HHR– and pre-cleaved HHR+ RNAs from the first round of evolution".
- The mock round is described: "A mock round 8 of evolution was performed using the HHR+ RNA from
  round 7 as input and carrying out reverse transcription and PCR amplification, but omitting the
  steps of RNA-catalyzed amplification and hammerhead cleavage."

### 2. The commentary that names the confound

Chen IA. 2024. "RNA life on the edge of catastrophe." PNAS 121, e2402649121.
doi:10.1073/pnas.2402649121, PMC10990123, PMID 38478681. Full text read from
`raw/europepmc/PMC10990123.xml`. Verbatim:

> "After observing the success of 71-89, one might reflect on whether 52-2 might have been able to
> overcome the error catastrophe. Since the error threshold is proportional to ln f 0 , in theory,
> strong selection conditions could amplify fitness differences to the point that replication would
> tolerate the high error rate of 52-2. In practice, however, various realities may thwart this
> approach, as stringent conditions would also lower absolute activity, possibly to the point that
> degradation might outpace synthesis (22), such that solving one problem might cause new ones."

This is the U4 question stated as theory, about a hypothetical different experiment. It asks whether
52-2 could have been rescued by stronger selection. It does not ask, or test, whether the selection
actually applied differed between the two arms as run, and it computes nothing from the data.

### 3. The citing paper on population dynamics during selection

Brooks EM, Kotlin NR, Weiss Z, DasGupta S. 2025. "Population dynamics of ribozymes during in vitro
selection." bioRxiv, doi:10.1101/2025.08.31.673163 (PPR1079590). Full text read from
`raw/europepmc/brooks_full.html`.

It analyses all eight rounds of a 2-aminoimidazole-ligase selection from a random pool, tracking how
sequence families rise and fall: "Selection pressure was increased by decreasing reaction times (from
2 h to 10 min) and Mg 2+ concentrations (from 20 mM to 5 mM) over eight rounds", and "Sequence
diversity decreased from >98% in rounds 1-5 to 54.61% in round 6 and eventually to 12.20% in round
8, indicating significant sequence enrichment". It reports per-round abundance and enrichment of
families and per-position conservation, and it finds that "abundance did not always predict activity"
(abstract).

Bearing on U4: it is a per-round enrichment analysis, that is, the E half alone. Copying there is by
protein RT-PCR, no copying fidelity is measured, and no retention-versus-selection split is made. It
cites Papastavrou et al. only in its reference list (ref 19); it reanalyses nothing from that
experiment.

### 4. Related work read at abstract level only

These four are not open access in Europe PMC, so only the Europe PMC abstract was read
(`raw/europepmc/MED*.json`, `raw/europepmc/PPR1346425.json`). None is a reanalysis of the two
lineages.

- Horning DP. 2025. "Emergent and convergent features in the laboratory evolution of polymerase
  ribozymes." Biochemistry. doi:10.1021/acs.biochem.5c00160. A review by the paper's second author of
  how laboratory evolution shaped these polymerases; the abstract reports no decomposition.
  Full text not opened, so its content beyond the abstract is unverified.
- Horning DP, Nasser S, Joyce GF. 2026. "Enhanced fidelity and sequence generality of an RNA
  polymerase ribozyme." Preprint, doi:10.64898/2026.10.18.759947 (PPR1346425). The follow-on: "By
  applying stringent selection pressure over the course of 33 successive rounds of evolution, both
  the fidelity and sequence generality of the polymerase were greatly improved. When synthesizing
  large functional RNAs such as the class I ligase ribozyme, the fidelity improved from 86% to 94%
  per nucleotide". It raises fidelity further; it does not revisit the 52-2 versus 71-89 hammerhead
  lineages.
- Kent AD, Yang LL, Cole KH, Lee IA, Lupták A. 2026. "A polymerase ribozyme increases copying fidelity
  through pyrophosphate-mediated RNA repair." PNAS. doi:10.1073/pnas.2606892123. A mechanism for
  raising fidelity, with a commentary by Murugan A, "Going in reverse to get it right in RNA
  replication", doi:10.1073/pnas.2619019123 (no abstract in Europe PMC; title only). Neither
  concerns selection stringency in the hammerhead experiment.
- Ravasio R, Husain K, Evans CG, Phillips R, Ribezzi-Crivellari M, Szostak JW, Murugan A. 2026.
  "Evolution of error correction through a need for speed." Science. doi:10.1126/science.adt1275.
  Argues proofreading can evolve under selection for speed alone. It is about how fidelity itself
  evolves, not about attributing one experiment's outcome to fidelity or to selection.

## Searches and screen

- Europe PMC citations of MED/38437533: **58 records** (`raw/europepmc/citations.json`). Titles and
  journals were read for all 58; abstracts were read for the six named above. The rest are new
  ribozyme and prebiotic-chemistry work, reviews, and RNA-world overviews. None has a title
  suggesting a reanalysis of these two lineages, an error-threshold decomposition, or a treatment of
  selection stringency in this experiment.
- Europe PMC topic searches (`raw/searches/s1.json`, `s2.json`, `s3.json`; counts on 2026-11-26):
  - `"error threshold" AND ribozyme AND ("selection stringency" OR "selection strength" OR superiority)`:
    8 hits. The paper itself, Paczkó et al. 2024 eLife on a relaxed error threshold under parabolic
    growth, earlier Joyce-group polymerase work, and general RNA-world reviews. Titles and metadata
    only.
  - `"error threshold" AND ("in vitro evolution" OR "directed evolution") AND fidelity AND selection`:
    38 hits, almost all protein-polymerase or viral-quasispecies work. Nothing that separates
    fidelity from selection strength in a ribozyme replication experiment.
  - `Papastavrou AND (reanalysis OR "error threshold")`: 7 hits, 3 of them relevant and already listed
    here; the others are unrelated clinical papers and conference-abstract collections.
- No reanalysis of the 52-2 and 71-89 lineages was found in any of these.

## What U4 would add

U4 would be the first measurement, per round and per lineage, of how much of the round-to-round change
in motif-consistent fraction comes from copying (pre-cleavage pool against the previous cleaved pool)
and how much from selection (cleaved pool against the same round's pre-cleavage pool), and so the
first test of whether the 52-2 arm's loss of the hammerhead survives giving it the 71-89 arm's
selection. The idea is in print twice (the authors' own stringency caveat, Chen's ln f0 remark); the
quantity has not been computed by anyone.

## Data check (Zenodo record 10714366)

Metadata and README fetched from the Zenodo API; the three zips' central directories were read with
HTTP range requests on the last 64 KB of each file. **Neither `processed_data.zip` nor `raw_data.zip`
was downloaded.** Record license: CC0; derived from Dryad doi:10.5061/dryad.rxwdbrvgs.

Files in the record (byte sizes from the API):

| File | Size |
|---|---|
| `README.md` | 52,005 |
| `figure_data.zip` | 262,392 |
| `processed_data.zip` | 134,835,539 |
| `raw_data.zip` | 7,103,242,168 |

**`processed_data.zip` holds 8 members, 2,421,422,796 bytes uncompressed** (name, uncompressed size):

- `dist_refs.fasta`, 311
- `HH_p52_n0_abd_clst_more_M_dist_refs_dists.txt`, 802,403,749
- `HH_p71_n0_abd_clst_more_M_dist_refs_dists.txt`, 640,247,616
- `HH_p52and71_n0_abd_M_dist_refs_dists.txt`, 978,692,563
- `HH_p52and71_m_n0_abd_aln_R1_52_2_muts.txt`, 30,590
- `HH_p52and71_m_n0_abd_aln_R1_89_muts.txt`, 29,120
- `HH_p52and71_E1_n0_abd_aln_R1_52_2_E1_muts.txt`, 9,619
- `HH_p52and71_E1_n0_abd_aln_R1_89_E1_muts.txt`, 9,228

Findings against the four questions asked:

1. **Which pools are in `processed_data.zip`.** Only cleaved plus-strand pools, per the README: "The
   p52 table contained frequency data for HHR+ cleaved populations and the round 8 mock selection
   population from evolution with 52-2. The p71 table contained frequency data for HHR+ cleaved
   populations and the round 8 mock selection population from evolution with 71-89 and all sequenced
   populations (HHR+ pre-cleaved and cleaved) from the 71-89 reselection. The p52and71 table contains
   frequency data for HHR+ cleaved populations from both branches of evolution." So the only
   pre-cleavage **frequency** data in the processed deposit is the single-round 71-89 reselection, not
   rounds 1-8 of either lineage.
2. **Pre-cleavage plus-strand pools per round and lineage.** They exist, as raw reads only.
   `raw_data.zip`'s central directory lists **130 members** (deflate, zip64, local-header offsets
   present), totalling 7,124,656,964 bytes uncompressed. For each round 1-8 and each lineage (`52_2`,
   `89`) there are exactly two read files for each of the three pools: minus strand (`R{r}_{lin}_S*`),
   pre-cleaved plus strand (`R{r}_{lin}_E1_S*`), cleaved plus strand (`R{r}_{lin}_E2_S*`). That is
   96 files; the rest are the reselection branch (7 pre-cleaved and 7 cleaved pairs), the two mock
   rounds, and the `CT_S27` starting mixture. Individual members run 34-110 MB compressed, so
   member-by-member extraction by range request is possible.
3. **Mock round and round-1 base-call tables.** Both exist. Mock round 8 raw reads are present for
   both lineages (`Raw files/R8_89_m_S25_R1/R2_001.fastq.gz`, `Raw files/R8_52_m_S26_R1/R2_001.fastq.gz`)
   and the mock appears as a population column in the p52 and p71 tables. The round-1 base-call tables
   are the four `muts.txt` files above: HHR– and pre-cleaved HHR+, for each lineage.
4. **The motif matcher.** It is **not** inside record 10714366. The scripts live in the companion
   Zenodo record **10306022** ("Deep sequencing datasets from: RNA-catalyzed evolution of catalytic
   RNA", type software, MIT licence, 13 files), which the data record declares itself derived from.
   `HHmotif_Matchor.py` (3,461 bytes) was downloaded and read (`raw/zenodo_code/HHmotif_Matchor.py`).
   It applies the regex `GTCGCGA.*(.)CTGA.GA(.).*(.)GAAATGCGG`, requires the pre-CUGANGA base to be
   `A`, and requires the stem II closing pair to be one of `AT, AC, GC, GT, CT, TT`. The same record
   holds `Sequence_Tabulator.py`, `Base_Count_Tabulator.py`, `LevDist_Measuror.py`,
   `Peak_Clusteror.py` and the R notebooks.

## Problems for the planned test

1. **The Q/E split cannot be done from `processed_data.zip`.** The per-round pre-cleavage pools are
   present only as fastqs in the 7.1 GB `raw_data.zip`. The honest test needs the 32 `E1` files
   (8 rounds × 2 lineages × 2 reads, roughly 1.4 GB compressed) plus the already-available cleaved
   pools. The central directory and per-member offsets read cleanly from the zip tail, so pulling one
   member at a time by range request looks feasible, but that is beyond the light-work budget and has
   not been attempted here.
2. **Q as defined is not pure copying.** The pre-cleavage HHR+ pool sits downstream of two polymerase
   passes plus reverse transcription, PCR and transcription. Any Q computed from it is the retention
   of motif-consistent sequences through the whole copy-and-amplify step, not the polymerase's
   fidelity alone. The two arms share the RT-PCR steps, so a between-arm comparison is still
   meaningful, but the quantity must not be reported as fidelity.
3. **The authors have already done a decomposition, in one place.** Fig. 4B separates replicability
   from specific activity for six variants, one round, 71-89 only. U4 must not redo that; the project
   rule forbids re-deriving an established result. The open part is the per-round, per-lineage split,
   including the 52-2 arm.
4. **Polymerase and Mg2+ cannot be separated.** 52-2 ran at 200 mM Mg2+, 71-89 at 50 mM, and the
   authors attribute much of the fidelity difference to the Mg2+ difference. Whatever U4 finds is
   about the copying condition as run, not about the polymerase alone.
5. **The selection leak is bounded only weakly.** The mock round omits both the polymerase step and
   the cleavage step, and exists for round 8 only, so it bounds the amplification-only change at one
   round rather than giving a per-round estimate of uncatalyzed release.
6. **Eight rounds, one lineage per arm.** The uncertainty lies between rounds, not between reads, so
   the test has at most eight values of Q and E per arm, as the plan's power gate already notes.
7. **SI Tables S2 and S3 were not opened here** (403 and 404 as described above), so the gate's
   reproduction of the published round-1 fidelities will have to be checked against the figure-data
   spreadsheet rather than against the SI tables.
