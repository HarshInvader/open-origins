"""Estimate how many step-6 Rhea candidates the FULL eQuilibrator DB (zenodo.4128543)
would cover, using the bloom-filter accession index bundled with equilibrator-cache-data
(no false negatives; small false-positive rate). Membership only, no thermodynamics.
Also maps each missing Rhea microspecies ChEBI to its parents (chebi_pH7_3_mapping).
Usage: .venv/bin/python -I scripts/full_db_coverage.py <expdir>"""
import sys, os, collections
from equilibrator_cache.accession_index import AccessionIndex
import equilibrator_cache_data as d

EXP = sys.argv[1]
ix = AccessionIndex.load(d.ACCESSION_INDEX_PATH)
rev = collections.defaultdict(list)
with open(os.path.join(EXP, 'raw', 'rhea_tsv', 'x', 'tsv', 'chebi_pH7_3_mapping.tsv')) as f:
    next(f)
    for l in f:
        p, ms, _ = l.rstrip('\n').split('\t')
        rev[ms.replace('CHEBI:', '')].append(p.replace('CHEBI:', ''))


def in_full(a):
    cands = [a] + rev.get(a, [])
    return any(k in ix or f'CHEBI:{k}' in ix for k in cands)


n = mini_ok = full_ok = 0
for line in open(os.path.join(EXP, 'scripts_out', 'step6_chebi.tsv')):
    m, accs = line.rstrip('\n').split('\t')
    accs = accs.split()
    n += 1
    if all(a.startswith('mini:') for a in accs):
        mini_ok += 1
        full_ok += 1
    elif all(a.startswith('mini:') or in_full(a) for a in accs):
        full_ok += 1
print(f'step-6 candidates {n}; covered by mini {mini_ok}; covered by full (bloom estimate) {full_ok}')
