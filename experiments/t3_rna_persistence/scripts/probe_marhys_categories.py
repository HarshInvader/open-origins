"""Blind probe of MARHYS: category labels and counts of non-empty cells only.
Never prints a measured value (T, pH, concentrations)."""
import zipfile, re, sys, collections
z = zipfile.ZipFile(sys.argv[1])
ss = z.read('xl/sharedStrings.xml').decode('utf-8', 'replace')
S = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', ss, flags=re.S)]
xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
LAB = {'Z': 'type', 'K': 'geol', 'G': 'rock1', 'H': 'rock2', 'E': 'area', 'P': 'sampler'}
NUM = {'AD': 'Tsample', 'AE': 'Tmax', 'AF': 'Tcalc', 'AG': 'T', 'AH': 'pHmeas', 'AI': 'pHmin', 'AJ': 'pHcalc', 'AK': 'pH',
       'BM': 'Mg', 'BK': 'K', 'BP': 'Nameas', 'BR': 'Na', 'BF': 'Fe', 'BN': 'Mn'}
cnt = {k: collections.Counter() for k in LAB.values()}
cross = collections.Counter(); nonempty = collections.Counter(); areas = collections.defaultdict(set)
joint = collections.Counter(); strnum = collections.Counter()
n = 0
for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', xml, flags=re.S):
    if int(rn) < 15: continue
    row = {}; 
    for c, a, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(?:<f>.*?</f>)?(?:<v>(.*?)</v>)?</c>)', body, flags=re.S):
        if c in LAB and 't="s"' in a and v: row[LAB[c]] = S[int(v)].strip()
        elif c in NUM and v not in (None, ''):
            if 't="s"' in a:
                if S[int(v)].strip(): row[NUM[c]] = 'str'
            else: row[NUM[c]] = 'num'
    t = row.get('type', '')
    if not t: continue
    n += 1
    for k in LAB.values(): cnt[k][row.get(k, '')] += 1
    cross[(t, row.get('geol', ''))] += 1
    areas[t].add(row.get('area', ''))
    for k in NUM.values():
        if k in row: nonempty[(t, k)] += 1; strnum[(k, row[k])] += 1
    if all(k in row for k in ('pHmeas', 'Mg')) and ('Tsample' in row or 'Tmax' in row): joint[(t, 'T(sample|max)+pHmeas+Mg')] += 1
    if all(k in row for k in ('pHmeas', 'Mg', 'Na', 'K')) and ('Tsample' in row or 'Tmax' in row): joint[(t, '+Na+K')] += 1
    if all(k in row for k in ('pHmeas', 'Mg', 'Na', 'K', 'Tsample')): joint[(t, 'Tsample+pHmeas+Mg+Na+K')] += 1
print('rows', n)
for k in ('type', 'geol', 'rock1', 'rock2', 'sampler'):
    print('##', k, len(cnt[k])); 
    for lab, c in cnt[k].most_common(40): print(f'   {c:6d}  {lab!r}')
print('## distinct areas per type', {t: len(a) for t, a in areas.items()})
print('## type x geol'); 
for (t, g), c in sorted(cross.items()): print(f'   {t:4s} {g!r:40s} {c}')
print('## non-empty counts type x column')
for (t, k), c in sorted(nonempty.items()): print(f'   {t:4s} {k:8s} {c}')
print('## joint complete'); 
for k, c in sorted(joint.items()): print('  ', k, c)
print('## cell kind', sorted(strnum.items()))
