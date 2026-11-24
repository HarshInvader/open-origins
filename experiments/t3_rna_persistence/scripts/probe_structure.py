"""Blind structure probe. Writes data/structure_counts.json.
Reads category labels and whether cells are empty. Never reads, prints or stores a measured value."""
import zipfile, re, sys, csv, json, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

def vent_class(geol, rock1):
    if rock1 == 'Peridotite': return 'V2_ultramafic'
    if rock1 == 'Sediment': return 'V4_sediment'
    if geol == 'Mid-oceanic spreading center' and rock1 == 'Basalt': return 'V1_basalt_ridge'
    if geol in ('Back-arc spreading center', 'Volcanic arc'): return 'V3_arc_backarc'
    return 'V5_other'

def marhys():
    z = zipfile.ZipFile(os.path.join(ROOT, 'raw/marhys4/MARHYS_DB_4_0.xlsx'))
    ss = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
    S = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', ss, flags=re.S)]
    xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
    LAB = {'Z': 'type', 'K': 'geol', 'G': 'rock1', 'E': 'area'}
    NEED = {'AG': 'T', 'AK': 'pH', 'BM': 'Mg', 'BK': 'K', 'BR': 'Na'}
    sizes = collections.defaultdict(collections.Counter); perid = collections.Counter(); total = collections.Counter()
    for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', xml, flags=re.S):
        if int(rn) < 15: continue
        lab = {}; have = set()
        for c, a, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(?:<f[^>]*>.*?</f>|<f[^>]*/>)?(?:<v>(.*?)</v>)?</c>)', body, flags=re.S):
            if c in LAB and 't="s"' in a and v: lab[LAB[c]] = S[int(v)].strip()
            elif c in NEED and v not in (None, ''): have.add(NEED[c])
        t = lab.get('type')
        if t not in ('HF', 'EM', 'SW'): continue
        cls = vent_class(lab.get('geol', ''), lab.get('rock1', '')) if t != 'SW' else 'SW'
        total[f'{t}|{cls}'] += 1
        if lab.get('rock1') == 'Peridotite' and t == 'HF': perid[lab.get('area', '')] += 1
        if have >= {'T', 'pH', 'Mg', 'K', 'Na'}: sizes[f'{t}|{cls}'][lab.get('area', '')] += 1
        if t == 'SW' and have >= {'pH', 'Mg', 'K', 'Na'}: sizes['SW_noT|SW'][lab.get('area', '')] += 1
    return {'rows_total': dict(total), 'complete_cluster_sizes': {k: sorted(v.values(), reverse=True) for k, v in sizes.items()},
            'peridotite_HF_areas': dict(perid.most_common())}

def usgs():
    p = os.path.join(ROOT, 'raw/usgs_ynp_p92xkju7/YNP_WQ.csv')
    sizes = collections.defaultdict(collections.Counter); total = collections.Counter()
    with open(p, newline='', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            wt = r['WaterType'].strip(); total[wt] += 1
            ok = lambda k: r.get(k, '').strip() not in ('', '--', 'NA')
            if (ok('pH_Field_StandardUnits') or ok('pH_Lab_StandardUnits')) and ok('WaterTemperature_DegreesCelsius') and all(
                    ok(k) for k in ('Magnesium_Dissolved_MilligramsPerLiter_Mg', 'Sodium_Dissolved_MilligramsPerLiter_Na', 'Potassium_Dissolved_MilligramsPerLiter_K')):
                sizes[wt][r['Area'].strip()] += 1
    return {'rows_total': dict(total), 'complete_cluster_sizes': {k: sorted(v.values(), reverse=True) for k, v in sizes.items()}}

out = {'marhys4': marhys(), 'usgs_ynp_v2': usgs()}
json.dump(out, open(os.path.join(ROOT, 'data/structure_counts.json'), 'w'), indent=1)
for src, d in out.items():
    print(src, 'rows', d['rows_total'])
    for k, v in d['complete_cluster_sizes'].items(): print(f'   {k:22s} complete rows {sum(v):5d} clusters {len(v):3d}  largest {v[:5]}')
print('peridotite HF areas:', out['marhys4']['peridotite_HF_areas'])
