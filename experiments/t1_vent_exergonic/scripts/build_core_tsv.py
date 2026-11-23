"""Build data/wimmer2021_core_reactions.tsv from Wimmer SI Table 1 (inputs only: IDs,
KEGG equations, module, EC, KO, synthesis target) plus matching covariates
(EC class, n substrates, n products, ATP/NTP involvement). Computes NO thermodynamics.
Also records, per reaction, whether Table 3 sheet A has a value (NA vs numeric)
-- a presence flag only, never the value.

Usage: python3 -I build_core_tsv.py <expdir>
"""
import sys, os, re, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlsx_dump import read  # noqa: E402

EXP = sys.argv[1]
RAW = os.path.join(EXP, 'raw', 'wimmer_supp', 'x')
T1 = os.path.join(RAW, 'Table_1.xlsx')
T3 = os.path.join(RAW, 'Table_3.XLSX')

# cofactor / currency compounds (KEGG IDs) excluded when counting "main" substrates
NTP = {'C00002', 'C00044', 'C00063', 'C00075', 'C00131', 'C00081'}  # ATP GTP CTP UTP dATP ITP
CURRENCY = {'C00001', 'C00080', 'C00009', 'C00013', 'C00002', 'C00008', 'C00020',
            'C00044', 'C00035', 'C00063', 'C00112', 'C00075', 'C00015', 'C00105',
            'C00003', 'C00004', 'C00005', 'C00006', 'C00138', 'C00139', 'C00016',
            'C01352', 'C00011', 'C00014', 'C00288', 'C00283', 'C00282', 'C00010'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def parse_side(s):
    out = []
    for tok in s.split(' + '):
        tok = tok.strip()
        m = re.match(r'^(\d+(?:\.\d+)?|n|\(?[nm][+-]?\d*\)?)?\s*([A-Z]\d{5}|[A-Za-z0-9_]+)$', tok)
        if not m:
            out.append(('?', tok))
            continue
        coef, cid = m.group(1) or '1', m.group(2)
        out.append((coef, cid))
    return out


def main():
    rows = read(T1)[0][1]
    hdr_i = next(i for i, r in enumerate(rows) if r and r[0] == 'Reaction ID')
    hdr = rows[hdr_i]
    recs = [r + [''] * (len(hdr) - len(r)) for r in rows[hdr_i + 1:] if r and r[0].strip()]
    # Table 3 sheet A presence flags (value present or 'NA'), keyed by row order + ID
    t3 = dict(read(T3))['A']
    present = {}
    for r in t3[2:]:
        if r and r[0]:
            vals = r[3:]
            present.setdefault(r[0].strip(), []).append(0 if all(v == 'NA' for v in vals) else 1)
    out = os.path.join(EXP, 'data', 'wimmer2021_core_reactions.tsv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cols = ['idx', 'reaction_id', 'kegg_equation', 'synthesis_target', 'kegg_module', 'ec',
            'ko', 'ec_class', 'n_left', 'n_right', 'n_left_main', 'n_right_main',
            'ntp_hydrolysis_left', 'parse_ok', 'kegg_rid', 'table3_has_value']
    seen = collections.Counter()
    with open(out, 'w') as f:
        f.write('# Wimmer et al. 2021 Front Microbiol doi:10.3389/fmicb.2021.793664, SI Table 1 (polarised, synthesis direction).\n')
        f.write(f'# sha256 raw/wimmer_supp/x/Table_1.xlsx = {sha(T1)}\n')
        f.write(f'# sha256 raw/wimmer_supp/x/Table_3.XLSX = {sha(T3)} (used only for the per-reaction NA/value presence flag)\n')
        f.write('# ec_class = first digit of the first EC number; main = excluding currency compounds listed in build_core_tsv.py\n')
        f.write('\t'.join(cols) + '\n')
        for i, r in enumerate(recs):
            rid, eq = r[0].strip(), r[1].strip()
            target, module, ec, ko = r[4].strip(), r[5].strip(), r[6].strip(), r[7].strip()
            if '<=>' in eq:
                L, R = eq.split('<=>')
                left, right = parse_side(L.strip()), parse_side(R.strip())
            else:
                left, right = [('?', eq)], []
            ok = int(all(c != '?' for c, _ in left + right) and bool(right))
            lid = {c for _, c in left}
            rid_set = {c for _, c in right}
            ntp = int(bool(lid & NTP) and bool(rid_set & {'C00008', 'C00020', 'C00035', 'C00112', 'C00015', 'C00105', 'C00013', 'C00009', 'C00206'}))
            ecm = re.match(r'(\d)\.', ec)
            k = seen[rid]
            seen[rid] += 1
            pres = present.get(rid, [])
            flag = pres[k] if k < len(pres) else ''
            f.write('\t'.join(map(str, [
                i + 1, rid, eq, target, module, ec, ko, ecm.group(1) if ecm else 'NA',
                len(left), len(right),
                len([c for _, c in left if c not in CURRENCY]),
                len([c for _, c in right if c not in CURRENCY]),
                ntp, ok, int(bool(re.match(r'^R\d{5}$', rid))), flag])) + '\n')
    print('wrote', out, len(recs), 'reactions')


if __name__ == '__main__':
    main()
