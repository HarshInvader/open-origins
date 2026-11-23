"""Build the candidate pool for the T1 matched null from Rhea release 143 (CC BY 4.0).
Computes NO thermodynamics. Outputs:
  data/rhea_null_pool.tsv     one row per eligible Rhea master reaction, written in its
                              UniProt physiological direction, with matching covariates
  scripts_out/null_pool_summary.txt   counts per exclusion step and per matching stratum

Direction rules (both independent of any Gibbs-energy computation by us):
  dir_uniprot : UniProtKB/Swiss-Prot "physiological direction" links (rhea2uniprot_sprot,
                DIRECTION LR or RL). A master is kept only if all its directional links
                point one way (LR-only or RL-only).
  dir_metacyc : MetaCyc reaction direction as cross-referenced by Rhea (rhea2metacyc,
                DIRECTION LR or RL); NA if absent, BI or UN.
Usage: python3 -I build_null_pool.py <expdir>
"""
import sys, os, gzip, re, hashlib, collections, sqlite3
import xml.etree.ElementTree as ET

EXP = sys.argv[1]
RDF = os.path.join(EXP, 'raw', 'rhea_rdf', 'rhea.rdf.gz')
TSV = os.path.join(EXP, 'raw', 'rhea_tsv', 'x', 'tsv')
CORE = os.path.join(EXP, 'data', 'wimmer2021_core_reactions.tsv')
MINI = os.path.join(EXP, '.venv', 'lib', 'python3.15', 'site-packages',
                    'equilibrator_cache_data', 'mini_compounds.sqlite')
RDFNS = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
RH = '{http://rdf.rhea-db.org/}'
RDFS = '{http://www.w3.org/2000/01/rdf-schema#}'
BASE = 'http://rdf.rhea-db.org/'

# ChEBI (pH 7.3 major microspecies, as used by Rhea)
NTP = {'30616', '37565', '37563', '46398', '61404'}             # ATP GTP CTP UTP dATP
NTP_PROD = {'456216', '456215', '58189', '58115', '58069', '60377', '58223', '57865',
            '43474', '33019'}                                    # NDP/NMP, Pi, PPi
CURRENCY = {'15377', '15378', '43474', '33019', '30616', '456216', '456215', '37565',
            '58189', '58115', '37563', '58069', '60377', '46398', '58223', '57865',
            '57540', '57945', '58349', '57783', '16526', '28938', '17544', '57287',
            '57692', '58307', '15379', '18276', '29919'}
O2 = '15379'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def loc(tag):
    return tag.split('}', 1)[1] if '}' in tag else tag


def parse_rdf():
    rx = collections.defaultdict(dict)        # reaction id -> fields
    side_parts = collections.defaultdict(list)  # side id -> [(coef, participant id)]
    part_comp = {}                            # participant -> compound
    comp_acc = {}                             # compound -> accession
    with gzip.open(RDF, 'rb') as fh:
        for ev, el in ET.iterparse(fh, events=('end',)):
            if loc(el.tag) != 'Description':
                continue
            about = el.get(RDFNS + 'about', '')
            if not about.startswith(BASE):
                el.clear(); continue
            key = about[len(BASE):]
            for ch in el:
                t, res = loc(ch.tag), ch.get(RDFNS + 'resource')
                rkey = res[len(BASE):] if res and res.startswith(BASE) else res
                if re.match(r'^\d+$', key):
                    d = rx[key]
                    if t == 'subClassOf' and rkey in ('Reaction', 'DirectionalReaction', 'BidirectionalReaction'):
                        d['kind'] = rkey
                    elif t == 'ec':
                        d.setdefault('ec', []).append(res.rsplit('/', 1)[1])
                    elif t == 'isChemicallyBalanced':
                        d['balanced'] = ch.text == 'true'
                    elif t == 'isTransport':
                        d['transport'] = ch.text == 'true'
                    elif t == 'side':
                        d.setdefault('sides', []).append(rkey)
                    elif t == 'seeAlso' and res and 'kegg.reaction' in res:
                        d.setdefault('kegg', []).append(res.rsplit('/', 1)[1])
                    elif t == 'status':
                        d['status'] = rkey
                elif re.match(r'^\d+_[LR]$', key) and t.startswith('contains') and t != 'contains':
                    side_parts[key].append((t[len('contains'):], rkey))
                elif key.startswith('Participant_') and t == 'compound':
                    part_comp[key] = rkey
                elif key.startswith('Compound_') and t == 'accession':
                    comp_acc[key] = ch.text
            el.clear()
    return rx, side_parts, part_comp, comp_acc


def read_tsv(name):
    with open(os.path.join(TSV, name)) as f:
        next(f)
        return [l.rstrip('\n').split('\t') for l in f if l.strip()]


def main():
    rx, side_parts, part_comp, comp_acc = parse_rdf()
    log = []
    masters = {k: v for k, v in rx.items() if v.get('kind') == 'Reaction'}
    log.append(f'Rhea master (UN) reactions in RDF: {len(masters)}')

    # direction rule 1: UniProt physiological direction
    up = collections.defaultdict(set)
    for rid, d, m, acc in read_tsv('rhea2uniprot_sprot.tsv'):
        if d in ('LR', 'RL'):
            up[m].add(d)
    # direction rule 2: MetaCyc
    mc = collections.defaultdict(set)
    for rid, d, m, acc in read_tsv('rhea2metacyc.tsv'):
        if d in ('LR', 'RL'):
            mc[m].add(d)
    # KEGG xrefs of masters (via BI rows)
    kegg = collections.defaultdict(set)
    for rid, d, m, acc in read_tsv('rhea2kegg_reaction.tsv'):
        kegg[m].add(acc)

    # core KEGG reaction IDs and core stoichiometries (as eQ compound-id multisets)
    core_rids, core_eqs = set(), []
    with open(CORE) as f:
        lines = [l.rstrip('\n').split('\t') for l in f if not l.startswith('#')]
    hdr = lines[0]
    core = [dict(zip(hdr, r)) for r in lines[1:]]
    for c in core:
        core_rids.add(re.sub(r'_\d+$', '', c['reaction_id']))
    con = sqlite3.connect(f'file:{MINI}?mode=ro', uri=True)
    reg = dict(con.execute('select namespace, id from registries'))
    kegg2c = dict(con.execute('select accession, compound_id from compound_identifiers where registry_id=?', (reg['kegg'],)))
    chebi2c, chebi_res = {}, {}   # Rhea ChEBI number -> eQ compound id / eQ accession string
    for acc, cid in con.execute('select accession, compound_id from compound_identifiers where registry_id=?', (reg['chebi'],)):
        chebi2c[acc.replace('CHEBI:', '')] = cid
        chebi_res[acc.replace('CHEBI:', '')] = acc
    # Rhea writes pH 7.3 major microspecies; eQuilibrator may list only the parent ChEBI.
    # Fall back to any parent ChEBI whose pH 7.3 major microspecies is the Rhea ID.
    rev = collections.defaultdict(list)
    for parent, ms, origin in read_tsv('chebi_pH7_3_mapping.tsv'):
        rev[ms.replace('CHEBI:', '')].append(parent.replace('CHEBI:', ''))
    for ms, parents in rev.items():
        if ms in chebi2c:
            continue
        hits = {chebi2c[p]: p for p in parents if p in chebi2c}
        if len(hits) == 1:
            cid, p = hits.popitem()
            chebi2c[ms], chebi_res[ms] = cid, chebi_res[p]
    H = {kegg2c.get('C00080')}
    for c in core:
        L, R = c['kegg_equation'].split('<=>')
        ls = frozenset(kegg2c.get(x) for x in re.findall(r'C\d{5}', L)) - H
        rs = frozenset(kegg2c.get(x) for x in re.findall(r'C\d{5}', R)) - H
        core_eqs.append(frozenset([ls, rs]))
    core_eqset = set(core_eqs)

    rows, steps, step6 = [], collections.Counter(), []
    for m, d in masters.items():
        steps['0 master'] += 1
        if d.get('status') != 'Approved':
            continue
        steps['1 approved'] += 1
        dirs = up.get(m, set())
        if len(dirs) != 1:
            continue
        steps['2 uniprot one-way direction'] += 1
        if d.get('transport'):
            continue
        steps['3 not transport'] += 1
        if not d.get('balanced'):
            continue
        steps['4 balanced'] += 1
        sides = {}
        generic = False
        for s in d.get('sides', []):
            parts = []
            for coef, p in side_parts.get(s, []):
                acc = comp_acc.get(part_comp.get(p, ''), '')
                if not acc.startswith('CHEBI:'):
                    generic = True
                parts.append((coef, acc.replace('CHEBI:', '')))
            sides[s[-1]] = parts
        if generic or set(sides) != {'L', 'R'}:
            continue
        steps['5 small molecules only (no generic/polymer)'] += 1
        if any(not re.match(r'^\d+$', co) for co, _ in sides['L'] + sides['R']):
            continue
        steps['6 integer stoichiometry'] += 1
        step6.append((m, [a for _, a in sides['L'] + sides['R']]))
        if any(a not in chebi2c for _, a in sides['L'] + sides['R']):
            continue
        steps['7 all compounds in eQuilibrator mini DB (by ChEBI)'] += 1
        if kegg.get(m, set()) & core_rids:
            steps['x excluded: KEGG xref in core'] += 1
            continue
        lc = frozenset(chebi2c[a] for _, a in sides['L']) - H
        rc = frozenset(chebi2c[a] for _, a in sides['R']) - H
        if frozenset([lc, rc]) in core_eqset:
            steps['x excluded: same compounds as a core reaction'] += 1
            continue
        steps['8 not core'] += 1
        dir_up = dirs.pop()
        sub, prod = (sides['L'], sides['R']) if dir_up == 'LR' else (sides['R'], sides['L'])
        mcd = mc.get(m, set())
        dir_mc = next(iter(mcd)) if len(mcd) == 1 else 'NA'
        sids = {a for _, a in sub}
        pids = {a for _, a in prod}
        ec = sorted(d.get('ec', []))
        rows.append({
            'rhea_master': m, 'dir_uniprot': dir_up, 'dir_metacyc': dir_mc,
            'directions_agree': 'NA' if dir_mc == 'NA' else int(dir_mc == dir_up),
            'substrates': ' + '.join(f'{c} CHEBI:{a}' for c, a in sub),
            'products': ' + '.join(f'{c} CHEBI:{a}' for c, a in prod),
            'ec': ','.join(ec) or 'NA', 'ec_class': ec[0][0] if ec else 'NA',
            'n_left': len(sub), 'n_right': len(prod),
            'n_left_main': len(sids - CURRENCY), 'n_right_main': len(pids - CURRENCY),
            'ntp_hydrolysis_left': int(bool(sids & NTP) and bool(pids & NTP_PROD)),
            'has_o2': int(O2 in sids | pids),
            'kegg_xref': ','.join(sorted(kegg.get(m, []))) or 'NA',
            'eq_formula': ' + '.join(f'{c} chebi:{chebi_res[a]}' for c, a in sub) + ' = '
                          + ' + '.join(f'{c} chebi:{chebi_res[a]}' for c, a in prod)})

    out = os.path.join(EXP, 'data', 'rhea_null_pool.tsv')
    cols = list(rows[0].keys())
    with open(out, 'w') as f:
        f.write('# Rhea release 143 (2026-11-04), CC BY 4.0, ftp.expasy.org/databases/rhea\n')
        for p in [RDF, os.path.join(TSV, 'chebi_pH7_3_mapping.tsv'), os.path.join(TSV, 'rhea2uniprot_sprot.tsv'), os.path.join(TSV, 'rhea2metacyc.tsv'),
                  os.path.join(TSV, 'rhea2kegg_reaction.tsv'), CORE, MINI]:
            f.write(f'# sha256 {os.path.relpath(p, EXP)} = {sha(p)}\n')
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')

    # summary
    def stratum(r):
        return (r['ec_class'], min(int(r['n_left_main']), 3), min(int(r['n_right_main']), 3),
                int(r['ntp_hydrolysis_left']))
    nul = collections.Counter(stratum(r) for r in rows)
    nul_noo2 = collections.Counter(stratum(r) for r in rows if r['has_o2'] == 0)
    nul_agree = collections.Counter(stratum(r) for r in rows if r['has_o2'] == 0 and r['directions_agree'] == 1)
    cs = collections.Counter(stratum(c) for c in core if c['table3_has_value'] == '1')
    summ = [*log, *(f'{k}: {v}' for k, v in sorted(steps.items()))]
    summ.append(f'pool rows: {len(rows)}; without O2: {sum(nul_noo2.values())}; '
                f'without O2 and MetaCyc agrees: {sum(nul_agree.values())}; '
                f'MetaCyc disagrees: {sum(1 for r in rows if r["directions_agree"] == 0)}; '
                f'MetaCyc NA: {sum(1 for r in rows if r["directions_agree"] == "NA")}')
    summ.append('stratum = (EC class, min(main substrates,3), min(main products,3), NTP hydrolysis)')
    summ.append('core = the 351 reactions with a value in Wimmer Table 3 (presence flag only)')
    summ.append('stratum\tcore351\tpool\tpool_noO2\tpool_noO2_agree')
    short = {'all': 0, 'noo2': 0, 'agree': 0}
    for s in sorted(cs, key=str):
        summ.append(f'{s}\t{cs[s]}\t{nul[s]}\t{nul_noo2[s]}\t{nul_agree[s]}')
        for k, n in (('all', nul[s]), ('noo2', nul_noo2[s]), ('agree', nul_agree[s])):
            if n < cs[s]:
                short[k] += cs[s] - n
    summ.append(f'core reactions lacking a 1:1 match without replacement: all={short["all"]} '
                f'noO2={short["noo2"]} noO2+agree={short["agree"]}')
    os.makedirs(os.path.join(EXP, 'scripts_out'), exist_ok=True)
    with open(os.path.join(EXP, 'scripts_out', 'step6_chebi.tsv'), 'w') as f:
        for m, accs in step6:
            f.write(m + '\t' + ' '.join(('mini:' if a in chebi2c else '') + a for a in accs) + '\n')
    open(os.path.join(EXP, 'scripts_out', 'null_pool_summary.txt'), 'w').write('\n'.join(summ) + '\n')
    print('\n'.join(summ))


if __name__ == '__main__':
    main()
