"""Build the T2 input TSVs (extraction only; no statistic relating abundance to code order).

Usage: python -I build_tsvs.py <experiment_dir>
Reads raw/ files only to hash them and to copy two numeric columns (Wehbi MW, Wehbi recomputed
ratio). Glavin and Higgs-Pudritz values are transcribed by hand from the table images / PDF text
and are typed in below; each row names its source table.
"""
import sys, os, csv, hashlib

EXP = sys.argv[1]
RAW = os.path.join(EXP, 'raw')
OUT = os.path.join(EXP, 'data')
os.makedirs(OUT, exist_ok=True)


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(RAW, rel), 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def write(name, header_lines, cols, rows):
    p = os.path.join(OUT, name)
    with open(p, 'w') as f:
        for l in header_lines:
            f.write('# ' + l + '\n')
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join('' if v is None else str(v) for v in r) + '\n')
    print('wrote', p, len(rows), 'rows')


AA3 = dict(G='Gly', A='Ala', S='Ser', D='Asp', T='Thr', E='Glu', V='Val', L='Leu', I='Ile', P='Pro',
           K='Lys', F='Phe', R='Arg', H='His', N='Asn', Q='Gln', C='Cys', Y='Tyr', M='Met', W='Trp')

# ---------------------------------------------------------------- Wehbi 2024 Table 1
# Transcribed from the PMC HTML of Table 1 (raw/wehbi_pmc_html/article.html).
wehbi_t1 = [  # aa, LUCA usage, LUCA SE, pre-LUCA usage, pre-LUCA SE  (row order as printed)
    ('V', '1.12', '0.0241', '1.04', '0.0205'), ('G', '1.11', '0.0283', '1.09', '0.0241'),
    ('I', '1.1', '0.0325', '1.07', '0.0351'), ('M', '1.08', '0.0386', '1.1', '0.0383'),
    ('A', '1.07', '0.0317', '1.03', '0.0297'), ('T', '1.07', '0.0369', '1.05', '0.0362'),
    ('H', '1.04', '0.0416', '1.17', '0.0486'), ('E', '1.03', '0.0357', '0.911', '0.0357'),
    ('C', '1.01', '0.0722', '1.03', '0.0844'), ('P', '1.01', '0.0282', '1.04', '0.0255'),
    ('K', '0.974', '0.038', '0.901', '0.0334'), ('S', '0.972', '0.0265', '1.02', '0.0239'),
    ('D', '0.968', '0.027', '0.988', '0.0363'), ('L', '0.942', '0.0256', '0.962', '0.032'),
    ('N', '0.934', '0.0374', '0.996', '0.0432'), ('R', '0.916', '0.0265', '0.915', '0.0271'),
    ('F', '0.895', '0.032', '1.02', '0.0394'), ('Y', '0.858', '0.0341', '0.982', '0.0309'),
    ('Q', '0.827', '0.031', '0.847', '0.0304'), ('W', '0.649', '0.0476', '0.865', '0.0526'),
]
recomp = {}
with open(os.path.join(EXP, 'scripts_out', 'wehbi_recomputed.tsv')) as f:
    for r in csv.DictReader(f, delimiter='\t'):
        recomp[r['aa']] = (r['LUCA_over_postLUCA_recomputed'], r['preLUCA_over_postLUCA_recomputed'])
early = set('VGIMTAHEPC')
rows = []
for aa, lu, luse, pre, prese in wehbi_t1:
    assert abs(float(recomp[aa][0]) - float(lu)) < 0.0051 * max(1, float(lu)), (aa, lu, recomp[aa])
    rows.append((aa, AA3[aa], lu, luse, pre, prese, recomp[aa][0], recomp[aa][1],
                 'early' if aa in early else 'late', 'Wehbi 2024 Table 1; recomputed from Dataset S2'))
write('wehbi2024_luca_usage.tsv', [
    'Source: Wehbi et al. 2024 PNAS 121:e2410311121, doi:10.1073/pnas.2410311121, Table 1 (PMC11670089 HTML).',
    'Table 1 title (verbatim): "LUCA and pre-LUCA clans\' ancestral amino acid frequencies are divided by post-LUCA',
    '  clan\'s ancestral amino acid frequencies to produce measures of relative usage"',
    'Paper (verbatim): "we recommend using the LUCA amino acid enrichment values plotted on the y-axis of Fig. 4A,',
    '  which can be found together with their SE in Table 1." Higher = earlier recruitment.',
    'Paper (verbatim): "We use enrichment in LUCA to reclassify VGIMTAHEPC as early and depletion to classify',
    '  KSDLNRFYQW as late."',
    'Units: dimensionless ratio. Table 1 prints 3 significant figures (ties A=T=1.07, C=P=1.01).',
    '*_recomputed columns: weighted means of Dataset S2 (Clan_data_ancestralAAC.csv) by Clan_Conlength, LUCA (n=309',
    '  clans) or preLUCA (n=136) over postLUCA (n=1232), mirroring AncientAminoAcidUsageAnalysis.R lines 96-101;',
    '  they round to Table 1 for all 20 amino acids (checked in build script). Script: scripts/wehbi_recompute.py.',
    'sha256 raw/wehbi_pmc_html/article.html = ' + sha('wehbi_pmc_html/article.html'),
    'sha256 raw/wehbi_europepmc_supp/x/pnas.2410311121.sd02.csv = ' + sha('wehbi_europepmc_supp/x/pnas.2410311121.sd02.csv'),
    'Detection limit / non-detects: not applicable.',
], ['aa1', 'aa3', 'luca_usage', 'luca_usage_se', 'preluca_usage', 'preluca_usage_se',
    'luca_usage_recomputed', 'preluca_usage_recomputed', 'wehbi_class', 'source'], rows)

# ---------------------------------------------------------------- molecular weight
mw = {}
with open(os.path.join(RAW, 'wehbi_github_01219d8', 'AminoAcid_properties.csv')) as f:
    r = list(csv.reader(f))
    i, j = r[0].index('Letter'), r[0].index('MolecularWeightsDa')
    for row in r[1:]:
        mw[row[i]] = row[j]
hp_mw = dict(G='75.1', A='89.1', D='133.1', E='147.1', V='117.1', S='105.1', I='131.2', L='131.2',
             P='115.1', T='119.1', K='146.2', F='165.2', R='174.2', H='155.2', N='132.1', Q='146.1',
             C='121.2', Y='181.2', M='149.2', W='204.2')
write('aa_molecular_weight.tsv', [
    'molecular_weight_da_wehbi: column MolecularWeightsDa of AminoAcid_properties.csv in',
    '  github.com/sawsanwehbi/Pfam-age-classification at commit tree 01219d85bfcaec82df0b80c0c24d031416e6dd96;',
    '  this is the covariate Wehbi regress on (script line 155: lm(ancient_clanConusage ~ MolecularWeightsDa)).',
    '  Integer Da; ties I=L=131, K=Q=146.',
    'molecular_weight_da_hp2009: Higgs & Pudritz 2009 Table 2 column MW ("molecular weight in Da"), arXiv:0904.0402.',
    'sha256 raw/wehbi_github_01219d8/AminoAcid_properties.csv = ' + sha('wehbi_github_01219d8/AminoAcid_properties.csv'),
    'sha256 raw/higgs_pudritz_arxiv_0904.0402/0904.0402.pdf = ' + sha('higgs_pudritz_arxiv_0904.0402/0904.0402.pdf'),
    'Units: Da (g/mol), free amino acid (not residue) mass.',
], ['aa1', 'aa3', 'molecular_weight_da_wehbi', 'molecular_weight_da_hp2009'],
    [(a, AA3[a], mw[a], hp_mw[a]) for a in 'GASDTEVLIPKFRHNQCYMW'])

# ---------------------------------------------------------------- Glavin 2025 EDT2 (free, AccQ-Tag, D+L)
# value strings exactly as printed. Columns: Bennu OREX-803001-0, Murchison, Tarda, Orgueil, Ryugu A0106
edt2 = [
    ('H', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('N', 'tr.', 'tr.', '<0.1', 'n.r.', 'n.r.'),
    ('Q', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('S', 'tr.', '0.14 ± 0.05', '1.70 ± 0.06', '0.10 ± 0.03', '0.52 ± 0.03'),
    ('R', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('G', '10.1 ± 0.5', '11.1 ± 1.2', '7.2 ± 0.8', '4.0 ± 1.3', '1.62 ± 0.04'),
    ('D', 'tr.', 'tr.', '0.9 ± 0.2', '0.89 ± 0.48', '0.25 ± 0.02'),
    ('E', '0.01 ± 0.01', '0.23 ± 0.02', '0.29 ± 0.02', '0.12 ± 0.07', '0.033 ± 0.001'),
    ('T', 'tr.', '0.28 ± 0.02', '0.32 ± 0.01', 'n.r.', '<0.1'),
    ('A', '1.60 ± 0.03', '4.1 ± 0.4', '0.15 ± 0.04', '1.13 ± 0.25', '0.17 ± 0.01'),
    ('P', '0.11 ± 0.01', '0.89 ± 0.07', '0.25 ± 0.03', 'n.r.', 'n.r.'),
    ('C', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('Y', 'tr.', 'tr.', '0.14 ± 0.12', 'n.r.', 'n.r.'),
    ('K', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('M', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
    ('V', '0.081 ± 0.004', '0.81 ± 0.06', '0.26 ± 0.01', '0.04 ± 0.01', '<0.2'),
    ('L', '0.036 ± 0.003', '0.13 ± 0.02', '0.17 ± 0.01', 'n.r.', '<0.2'),
    ('I', 'tr.', '0.10 ± 0.01', '0.14 ± 0.01', 'n.r.', '<0.1'),
    ('F', 'tr.', 'tr.', '<0.1', 'n.r.', 'n.r.'),
    ('W', '<0.1', '<0.1', '<0.1', 'n.r.', 'n.r.'),
]
samples2 = ['Bennu_OREX-803001-0', 'Murchison_CM2', 'Tarda_C2ung', 'Orgueil_CI1', 'Ryugu_A0106']


def parse(cell):
    """-> value, error, detection_limit, status"""
    c = cell.strip()
    if c.startswith('<'):
        return None, None, c[1:].split()[0], 'below_detection_limit'
    if c.startswith('≤'):
        return c[1:], None, None, 'upper_limit_not_blank_corrected'
    if c == 'tr.':
        return None, None, None, 'trace_below_quantitation'
    if c == 'n.r.':
        return None, None, None, 'not_reported'
    if c == 'n.d.':
        return None, None, None, 'not_determined'
    v, e = [x.strip() for x in c.split('±')]
    return v, e, None, 'quantified'


rows = []
for aa, *cells in edt2:
    for s, c in zip(samples2, cells):
        v, e, dl, st = parse(c)
        note = ''
        if st == 'trace_below_quantitation':
            note = 'tr. = tentatively identified at trace levels, below limit of quantitation; main text: "near the 0.1 nmol g-1 detection limit" (Met/Tyr/Asn sentence)'
        if s == 'Ryugu_A0106':
            note = (note + '; ' if note else '') + 'Ryugu column from Parker et al. 2023 GCA 347:42-57 (Glavin ref. 27)'
        if s == 'Orgueil_CI1':
            note = (note + '; ' if note else '') + 'Orgueil free protein AA from Glavin ref. 62'
        rows.append((aa, AA3[aa], 'D+L', s, 'free', c, v, e, 'nmol g-1', dl, st, '3' if s in samples2[:3] else '',
                     note, 'Glavin 2025 Extended Data Table 2'))
write('glavin2025_edt2_free_protein_aa.tsv', [
    'Source: Glavin et al. 2025 Nat. Astron. 9:199-210, doi:10.1038/s41550-024-02472-9, Extended Data Table 2,',
    '  transcribed by hand from the full-resolution image (static-content.springer.com, CC BY article).',
    'Title (verbatim): "Blank-subtracted free abundances of ammonia, amines, and amino acids, as measured by',
    '  LC-FD/ToF-MS, in the hot-water extract of Bennu (OREX-803001-0), compared with selected CCs and Ryugu (A0106)"',
    'Footnote a (verbatim, abridged only by ellipsis): "Hot-water extracts (100oC for 24 h) of the Bennu aggregate',
    '  subsample (OREX-803001-0; 25.6 mg), the CM2 Murchison meteorite (University of Chicago at Illinois; 26.3 mg), the',
    '  C2 ungrouped Tarda meteorite (Roberto Vargas, RV; 723 mg), and Ryugu (A0106; 13.08 mg extracted in water at',
    '  105oC for 20 h) were analyzed directly after AccQ·Tag derivatization ... Values are the average of three',
    '  measurements (n = 3) with a standard error, δx = σx·(n)^-1/2."',
    'Abbreviations (verbatim): "n.r. = not reported; n.d. = not determined; tr. = amino acid was tentatively',
    '  identified at trace levels but was below the limit of quantitation."',
    'All protein amino acids are D+L combined ("D,L-") except glycine (achiral). Free = not acid-hydrolysed.',
    'error = standard error as printed. detection_limit = the number after "<" where printed; no explicit LOD',
    '  is printed for "tr." cells.',
    'Printed sums: Bennu 11.9 ± 0.5; Murchison 17.8 ± 1.3; Tarda 11.5 ± 0.8; Orgueil 6.3 ± 1.4; Ryugu 2.59 ± 0.05.',
    'Cross-check: SI Table 12 (AccQ·TAG column) marks Phe detected, Asn and Tyr "tentative", Met/Gln/Trp/Lys/Arg/His/Cys',
    '  not detected; EDT2 prints Phe as "tr.".',
    'sha256 raw/glavin_springer_tables/41550_2024_2472_Tab2_ESM.jpg = ' + sha('glavin_springer_tables/41550_2024_2472_Tab2_ESM.jpg'),
    'sha256 raw/glavin_europepmc_supp/x/41550_2024_2472_MOESM1_ESM.pdf (SI) = ' + sha('glavin_europepmc_supp/x/41550_2024_2472_MOESM1_ESM.pdf'),
], ['aa1', 'aa3', 'enantiomer', 'sample', 'fraction', 'cell_as_printed', 'value', 'error_se', 'units',
    'detection_limit', 'status', 'n', 'note', 'source_table'], rows)

# ---------------------------------------------------------------- Glavin 2025 EDT3 (OPA/NAC, free and total)
# protein amino acid rows only. Columns: Bennu free, Bennu total, Murchison free, Murchison total,
# Tarda total, Orgueil total, Ryugu total. n is printed per Bennu/Murchison cell.
edt3 = [
    ('G', 'Gly', '', '6', ['33 ± 1', '44 ± 1', '28 ± 1', '80 ± 2', '11.2 ± 0.5', '11.5 ± 6.0', '0.46 ± 0.05']),
    ('A', 'Ala', 'D', '6', ['2.8 ± 0.4', '4.0 ± 0.6', '4.5 ± 0.6', '8.5 ± 1.2', '0.93 ± 0.04', '0.90 ± 0.19', '0.025 ± 0.006']),
    ('A', 'Ala', 'L', '6', ['2.6 ± 0.4', '3.9 ± 0.6', '4.2 ± 0.6', '11.5 ± 1.5', '1.62 ± 0.06', '1.1 ± 0.3', '<0.44']),
    ('S', 'Ser', 'D', '6', ['0.21 ± 0.09', '0.18 ± 0.03', '0.38 ± 0.07', '0.54 ± 0.08', '0.21 ± 0.01', '<0.01', '0.06 ± 0.01']),
    ('S', 'Ser', 'L', '6', ['0.24 ± 0.01', '≤0.7', '0.4 ± 0.1', '3.6 ± 0.6', '0.78 ± 0.03', '<0.01', '0.18 ± 0.03']),
    ('D', 'Asp', 'D', '6', ['0.94 ± 0.12', '1.35 ± 0.14', '0.69 ± 0.11', '2.4 ± 0.3', '0.42 ± 0.01', '0.41 ± 0.23', '<0.06']),
    ('D', 'Asp', 'L', '6', ['0.79 ± 0.16', '1.22 ± 0.12', '0.73 ± 0.15', '5.1 ± 0.6', '0.95 ± 0.03', '0.41 ± 0.21', '0.02 ± 0.01']),
    ('T', 'Thr', 'D', '6', ['<1', '<0.2', '<0.2', '1.2 ± 0.4', 'n.d.', 'n.r.', '<0.02']),
    ('T', 'Thr', 'L', '6', ['<1', '<0.2', '<1', '13 ± 4', 'n.d.', 'n.r.', '<0.04']),
    ('E', 'Glu', 'D', '6', ['0.08 ± 0.02', '0.79 ± 0.06', '0.64 ± 0.07', '3.5 ± 0.3', '0.79 ± 0.04', '0.32 ± 0.11', '<0.03']),
    ('E', 'Glu', 'L', '6', ['0.07 ± 0.01', '≤0.8', '0.85 ± 0.11', '10.6 ± 1.1', '7.04 ± 0.14', '0.56 ± 0.15', '<0.03']),
    ('V', 'Val', 'D', '6', ['0.08 ± 0.01', '0.16 ± 0.01', '0.93 ± 0.09', '1.64 ± 0.04', '0.05 ± 0.01', '0.19 ± 0.05', '<0.07 (0.026)f']),
    ('V', 'Val', 'L', '6', ['0.09 ± 0.01', '0.32 ± 0.06', '1.0 ± 0.1', '4.3 ± 0.2', '0.81 ± 0.01', '0.48 ± 0.02', '<0.06 (0.056)f']),
    ('L', 'Leu', 'D', '3', ['tr.', '0.09 ± 0.01', '<0.1', '0.9 ± 0.2', 'n.d.', 'n.r.', '<0.05']),
    ('L', 'Leu', 'L', '3', ['<0.3', '<0.3', '<0.1', '1.3 ± 0.5', 'n.d.', 'n.r.', '<0.06']),
    ('I', 'Ile', 'D', '6', ['tr.', '0.069 ± 0.005', '0.25 ± 0.05', '0.4 ± 0.1', 'n.d.', 'n.r.', '<0.04']),
    ('I', 'Ile', 'L', '6', ['<0.1', '≤0.4', '0.24 ± 0.02', '2.3 ± 0.2', 'n.d.', 'n.r.', '<0.04']),
]
cols3 = [('Bennu_OREX-803001-0', 'free'), ('Bennu_OREX-803001-0', 'total'), ('Murchison_CM2', 'free'),
         ('Murchison_CM2', 'total'), ('Tarda_C2ung', 'total'), ('Orgueil_CI1', 'total'), ('Ryugu_A0106', 'total')]
rows = []
for aa, a3, en, n, cells in edt3:
    for (s, fr), c in zip(cols3, cells):
        note = ''
        cc = c
        if c.endswith('f'):
            # "<0.07 (0.026)f": upper limit from ref 27, plus single 3D-HPLC value from ref 20
            cc = c.split(' (')[0]
            note = 'parenthetical ' + c.split('(')[1].split(')')[0] + ' nmol g-1 = footnote f: "Single measurement made by 3D HPLC with UV fluorescence detection from ref. 20" (Naraoka et al. 2023)'
        v, e, dl, st = parse(cc)
        if st == 'upper_limit_not_blank_corrected':
            note = 'footnote d: "Non-blank corrected value given as an upper limit for the concentration in the sample extract due to peak areas near background levels and ambiguity associated with the procedural blank contribution to the sample peak. Values included in the sum."'
        if st == 'trace_below_quantitation':
            note = 'tr. = "trace, amino acid tentatively identified above background but was below the limit of quantitation"'
        if s == 'Ryugu_A0106':
            note = (note + '; ' if note else '') + 'footnote c: "Data from ref. 27, unless otherwise noted." (Parker et al. 2023)'
        if s == 'Orgueil_CI1':
            note = (note + '; ' if note else '') + 'footnote b: "Data from ref. 59."'
        rows.append((aa, a3, en or 'achiral', s, fr, c, v, e, 'nmol g-1', dl, st,
                     n if s.startswith(('Bennu', 'Murchison')) else '', note, 'Glavin 2025 Extended Data Table 3'))
write('glavin2025_edt3_free_total_protein_aa.tsv', [
    'Source: Glavin et al. 2025 Nat. Astron. 9:199-210, doi:10.1038/s41550-024-02472-9, Extended Data Table 3,',
    '  transcribed by hand from the full-resolution image (static-content.springer.com, CC BY article).',
    '  Only the protein amino acid rows are kept (Gly, Ala, Ser, Asp, Thr, Glu, Val, Leu, Ile; OPA/NAC cannot',
    '  label secondary amines so Pro is absent; the other protein amino acids are not in this table).',
    'Title (verbatim): "Free and total amino acid abundances, as measured by LC-FD/ToF-MS and LC-FD/HRMS, in the',
    '  hot-water extract of Bennu (OREX-803001-0), compared with selected CCs and Ryugu (A0106)"',
    'Methods (verbatim): "40% of the water extract desalted by cation exchange chromatography followed by',
    '  o-phthaldialdehyde/N-acetyl-l-cysteine (OPA/NAC) derivatization and analysis using both LC-FD/ToF-MS and',
    '  [LC-FD/HRMS] to determine the free amino acid abundances in the extract. The other 40% was dried, acid-hydrolysed',
    '  under 6 M HCl vapour at 150 °C for 3 h and then desalted to determine the average total (free + bound) amino',
    '  acid abundances using both LC-FD/ToF-MS and LC-FD/HRMS."',
    'Footnote a (verbatim, abridged): "The reported uncertainties in the individual amino acid concentrations in',
    '  OREX-803001-0 and Murchison are based on the averages of three or six individual measurements (n) from both',
    '  instruments with a standard error, δx = σx·(n)^-1/2." Ryugu A0106 was extracted at 105 °C for 20 h.',
    'Abbreviations (verbatim): "tr. = trace, amino acid tentatively identified above background but was below the',
    '  limit of quantitation; n.r. = not reported; n.d. = not determined".',
    'Printed sums of C2-C6 amino acids (all, incl. non-protein): Bennu free 45 ± 1, total 70 ± 2; Murchison free',
    '  101 ± 2, total 253 ± 7; Tarda 37 ± 1; Orgueil 71 ± 10; Ryugu 15 ± 3.',
    'Each enantiomer is a separate row; D+L sums are not formed here (a prereg decision).',
    'sha256 raw/glavin_springer_tables/41550_2024_2472_Tab3_ESM.jpg = ' + sha('glavin_springer_tables/41550_2024_2472_Tab3_ESM.jpg'),
    'sha256 raw/glavin_pmc_html/article.html = ' + sha('glavin_pmc_html/article.html'),
], ['aa1', 'aa3', 'enantiomer', 'sample', 'fraction', 'cell_as_printed', 'value', 'error_se', 'units',
    'detection_limit', 'status', 'n', 'note', 'source_table'], rows)

# ---------------------------------------------------------------- Higgs & Pudritz 2009 Table 2
hp = [
    ('G', '1.1', '3.5', '1.0000', '80.49', '14.89', '11.7', '75.1'),
    ('A', '2.8', '4.0', '0.4970', '113.66', '-12.12', '11.7', '89.1'),
    ('D', '4.3', '6.0', '0.1633', '146.74', '32.78', '12.7', '133.1'),
    ('E', '6.8', '8.1', '0.1153', '172.13', '-1.43', '15.3', '147.1'),
    ('V', '8.5', '6.3', '0.0724', '178.00', '-70.12', '23.3', '117.1'),
    ('S', '8.6', '7.6', '0.0286', '173.73', '69.47', '11.7', '105.1'),
    ('I', '9.1', '11.4', '0.0226', '213.93', '-96.4', '32.3', '131.2'),
    ('L', '9.4', '9.9', '0.0116', '205.03', '-105.53', '27.3', '131.2'),
    ('P', '10.0', '7.3', '0.0437', '192.83', '-38.75', '20.3', '115.1'),
    ('T', '11.7', '9.4', '0.0008', '216.50', '53.51', '18.7', '119.1'),
    ('K', '12.6', '13.3', '0', '258.56', '-28.33', '30.3', '146.2'),
    ('F', '13.2', '14.4', '0', '303.64', '-114.54', '52.0', '165.2'),
    ('R', '13.3', '11.0', '0', '409.46', '197.52', '27.3', '174.2'),
    ('H', '13.3', '13.0', '0', '350.52', '154.48', '38.3', '155.2'),
    ('N', '14.2', '11.3', '0', '201.56', '83.53', '14.7', '132.1'),
    ('Q', '14.2', '11.4', '0', '223.36', '44.04', '16.3', '146.1'),
    ('C', '14.2', '13.8', '0', '224.67', '60.24', '24.7', '121.2'),
    ('Y', '14.2', '15.2', '0', '334.20', '-59.53', '50.0', '181.2'),
    ('M', '14.2', '15.4', '0', '113.22', '-174.71', '34.3', '149.2'),
    ('W', '14.2', '16.5', '0', '431.17', '-38.99', '74.3', '204.2'),
]
write('higgs_pudritz2009_table2.tsv', [
    'Source: Higgs & Pudritz 2009 Astrobiology 9:483-490, doi:10.1089/ast.2008.0280; legal copy arXiv:0904.0402',
    '  (submitted version), Table 2, transcribed via pdftotext.',
    'Caption (verbatim): "Thermodynamic and evolutionary properties of amino acids. Robs = ranking derived from Table',
    '  1; Rcode = ranking from Trifonov (2004); Crel = mean relative concentration from Table 1; ΔGsurf and ΔGhydro =',
    '  free energies of formation in kJ/mol (Amend and Shock, 1998); ATP cost of synthesis (Akashi and Gojobori,',
    '  2002); MW = molecular weight in Da."',
    'Robs method (verbatim): "amino acids were ranked according to each criterion in Table 1 ... All the remaining',
    '  amino acids are not observed, and are given an equal bottom rank ... The mean of these ranks from the 12',
    '  observations is termed Robs." Table 1 meteorite columns: M1 Murchison (H2O extract, Engel & Nagy 1982),',
    '  M2 Murray (Cronin & Moore 1971), M3 Yamato (hydrolysed, Shimoyama 1979); Gly = 1.0 normalisation.',
    'Lower Robs = more abundant prebiotically = proposed earlier. Not the Wehbi order; kept as prior art/comparator.',
    'sha256 raw/higgs_pudritz_arxiv_0904.0402/0904.0402.pdf = ' + sha('higgs_pudritz_arxiv_0904.0402/0904.0402.pdf'),
], ['aa1', 'aa3', 'Robs', 'Rcode_trifonov2004', 'Crel', 'dG_surf_kJmol', 'dG_hydro_kJmol', 'ATP_cost', 'MW_da'],
    [(a, AA3[a], *v) for a, *v in hp])
