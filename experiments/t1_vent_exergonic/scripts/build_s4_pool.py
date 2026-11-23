"""Second null pool: Xavier et al. 2020 Proc R Soc B dataset S4 (rspb20192377supp5.txt,
CC BY 4.0, already in repo at experiments/raf_null/raw/). Keeps reactions written with a
one-way arrow ("=>", direction "parsed out of KGML files for KEGG pathways and
manually-curated", Xavier SI) that are not in the Wimmer core and whose KEGG compounds are
all in the eQuilibrator mini DB. Same covariates as the core. No thermodynamics.
Usage: python3 -I build_s4_pool.py <expdir>"""
import sys, os, re, sqlite3, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_core_tsv import parse_side, NTP, CURRENCY  # noqa: E402

EXP = sys.argv[1]
S4 = os.path.normpath(os.path.join(EXP, '..', 'raf_null', 'raw', 'rspb20192377supp5.txt'))
CORE = os.path.join(EXP, 'data', 'wimmer2021_core_reactions.tsv')
MINI = os.path.join(EXP, '.venv', 'lib', 'python3.15', 'site-packages',
                    'equilibrator_cache_data', 'mini_compounds.sqlite')
NTP_PROD = {'C00008', 'C00020', 'C00035', 'C00112', 'C00015', 'C00105', 'C00013', 'C00009', 'C00206'}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    con = sqlite3.connect(f'file:{MINI}?mode=ro', uri=True)
    reg = dict(con.execute('select namespace, id from registries'))
    mini = {a for (a,) in con.execute('select accession from compound_identifiers where registry_id=?', (reg['kegg'],))}
    core_ids, core_sets = set(), set()
    with open(CORE) as f:
        rows = [l.rstrip('\n').split('\t') for l in f if not l.startswith('#')]
    for r in rows[1:]:
        core_ids.add(re.sub(r'_\d+$', '', r[1]))
        L, R = r[2].split('<=>')
        core_sets.add(frozenset([frozenset(re.findall(r'C\d{5}', L)) - {'C00080'},
                                 frozenset(re.findall(r'C\d{5}', R)) - {'C00080'}]))
    # EC class via Rhea (CC BY): KEGG reaction -> Rhea master -> EC (rhea2kegg_reaction, rhea2ec)
    tsv = os.path.join(EXP, 'raw', 'rhea_tsv', 'x', 'tsv')
    m2ec = collections.defaultdict(set)
    for l in list(open(os.path.join(tsv, 'rhea2ec.tsv')))[1:]:
        _, _, m, ec = l.rstrip('\n').split('\t')
        m2ec[m].add(ec)
    r2ec = collections.defaultdict(set)
    for l in list(open(os.path.join(tsv, 'rhea2kegg_reaction.tsv')))[1:]:
        _, _, m, kr = l.rstrip('\n').split('\t')
        r2ec[kr] |= m2ec.get(m, set())
    txt = open(S4).read().split('<reactions>', 1)[1]
    out, steps = [], collections.Counter()
    for line in txt.splitlines():
        if not line.strip():
            continue
        f = line.split('\t')
        rid, eq = f[0].strip(), f[1].strip()
        steps['0 S4 reactions'] += 1
        if '<=>' in eq or '=>' not in eq:
            continue
        steps['1 one-way arrow'] += 1
        L, R = eq.split('=>')
        left, right = parse_side(L.strip()), parse_side(R.strip())
        if any(c == '?' for c, _ in left + right) or any(not re.match(r'^C\d{5}$', x) for _, x in left + right):
            continue
        steps['2 parsable, KEGG compounds only'] += 1
        if any(x not in mini for _, x in left + right):
            continue
        steps['3 all compounds in eQuilibrator mini DB'] += 1
        ls = frozenset(x for _, x in left) - {'C00080'}
        rs = frozenset(x for _, x in right) - {'C00080'}
        if rid in core_ids or frozenset([ls, rs]) in core_sets:
            steps['x in core'] += 1
            continue
        steps['4 not core'] += 1
        lid, rset = {x for _, x in left}, {x for _, x in right}
        ecs = sorted(r2ec.get(rid, set()))
        cls = sorted({e[0] for e in ecs})
        out.append([rid, eq.replace('=>', '<=>'), ','.join(ecs) or 'NA',
                    cls[0] if len(cls) == 1 else ('NA' if not cls else 'multi'), str(len(left)), str(len(right)),
                    str(len(lid - CURRENCY)), str(len(rset - CURRENCY)),
                    str(int(bool(lid & NTP) and bool(rset & NTP_PROD))),
                    str(int('C00007' in lid | rset))])
    p = os.path.join(EXP, 'data', 's4_null_pool.tsv')
    with open(p, 'w') as fh:
        fh.write('# Xavier et al. 2020 Proc R Soc B doi:10.1098/rspb.2019.2377, dataset S4, one-way (=>) reactions not in the Wimmer core\n')
        fh.write(f'# sha256 ../raf_null/raw/rspb20192377supp5.txt = {sha(S4)}\n')
        fh.write('# kegg_equation is written in the S4 arrow direction (substrates left). S4 has no EC; ec_class comes from Rhea (rhea2kegg_reaction + rhea2ec); NA if unmapped, multi if classes differ.\n')
        fh.write('reaction_id\tkegg_equation\tec_via_rhea\tec_class\tn_left\tn_right\tn_left_main\tn_right_main\tntp_hydrolysis_left\thas_o2\n')
        for r in out:
            fh.write('\t'.join(r) + '\n')
    for k, v in sorted(steps.items()):
        print(f'{k}: {v}')


if __name__ == '__main__':
    main()
