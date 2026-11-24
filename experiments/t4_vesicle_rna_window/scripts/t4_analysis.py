#!/usr/bin/env python3
"""T4: do vesicle-compatible and RNA-compatible windows overlap in real natural waters?
Prereg (DRAFT): docs/prereg/t4_vesicle_rna_window.md

Modes
  count      declared blind count. Prints rows and clusters per class in each candidate window:
             the Mg band (A) and the co-condition window (B), separately. It never prints, stores
             or computes the joint count A-and-B, and never prints a measured value.
  loadcheck  rows and clusters loaded per class, and a cross-check against the T3 loaders.
  planted    synthetic worlds on the real cluster sizes (data/structure_counts.json). No field value.
  real       the sealed analysis. Refuses unless docs/prereg/HASHES.txt holds a line for the T4
             prereg and a line for this script, both matching the files on disk.

Row classes, units, non-detects and clusters follow T3 decisions D1, D3, D4, D8, D9, D10
(docs/prereg/t3_rna_persistence.md). vent_class, _num, sha256 are imported from t3_analysis.py.
The T3 loaders do not read Ca and they require T, so T4 has its own loaders; `loadcheck` confirms
that they return the T3 row counts when T is required.

Standard library only. Single process. Run with: nice python3 -I t4_analysis.py <mode>
"""
import csv, json, math, os, random, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(EXP))
T3 = os.path.join(REPO, 'experiments', 't3_rna_persistence')
sys.path.insert(0, os.path.join(T3, 'scripts'))
import t3_analysis as t3   # noqa: E402  (vent_class, _num, sha256, load_marhys, load_usgs)

PREREG_REL = 'docs/prereg/t4_vesicle_rna_window.md'
SCRIPT_REL = 'experiments/t4_vesicle_rna_window/scripts/t4_analysis.py'

INF = float('inf')
# All concentrations in mM. M = Na + K (T3 D4). Sources: PRIOR_ART.md, section "Thresholds".
WINDOWS = {
    # pure fatty acid
    'P_strict':  dict(Mg_max=0.5, Ca_max=0.5, M_max=200.0, pH=(7.0, 9.5)),
    'P_lenient': dict(Mg_max=2.0, Ca_max=2.0, M_max=200.0, pH=(7.0, 9.5)),
    # mixed amphiphile (fatty acid + monoglyceride or alcohol)
    'M':         dict(Mg_max=4.0, Ca_max=1.9, M_max=600.0, pH=(6.5, 12.0)),
    # guards on the mixed arm
    'M_strict':  dict(Mg_max=4.0, Ca_max=0.5, M_max=600.0, pH=(7.0, 11.5), fe=True),
    'M_lenient': dict(Mg_max=10.0, Ca_max=1.9, M_max=1000.0, pH=(-INF, INF)),
    # guard on the pure arm
    'P_lenient_nopH': dict(Mg_max=2.0, Ca_max=2.0, M_max=200.0, pH=(-INF, INF)),
    # alkaline-vent mixture (Jordan 2019), reported only
    'J_alk':     dict(Mg_max=50.0, Ca_max=10.0, M_max=600.0, pH=(11.5, INF)),
}
RNA = {'R1': 1.0, 'R50': 50.0}            # minimum Mg, mM
CFG = dict(seed=20261126, n_boot_real=10000, min_rows=30, min_clusters=5,
           kill_J_lo=0.05, kill_clusters=5, support_J=0.01, support_clusters=1,
           vent_kill_cond_lo=0.25, vent_support_cond=0.02,
           label_Mg_poor=0.01, label_cov_rho_hi=0.5, label_cov_expected=0.05,
           kill_tail=0.005)   # kill bound = 0.5th percentile of the cluster bootstrap (lower end of a 99% interval); tightened after planted round 1
ARMS = {   # arm name -> (base window, strict guard or None, lenient guard)
    'mixed': ('M', 'M_strict', 'M_lenient'),
    'pure':  ('P_lenient', None, 'P_lenient_nopH'),
}
VENT_CLASSES = ('V1_basalt_ridge', 'V2a_alkaline_serpentinite', 'V2b_ultramafic_other', 'V3_arc_backarc', 'V4_sediment', 'V5_other')


# ----------------------------------------------------------------------------- windows

def in_A(r, w, m):
    """Mg band: enough Mg for the RNA side and not too much for the vesicle side."""
    return m <= r['Mg'] <= WINDOWS[w]['Mg_max']


def in_B(r, w):
    """Co-conditions of the vesicle window: Ca (plus Fe(II) where the window says so), salt and pH."""
    W = WINDOWS[w]
    ca = r['Ca'] + (r.get('Fe') or 0.0 if W.get('fe') else 0.0)
    return ca <= W['Ca_max'] and r['M'] <= W['M_max'] and W['pH'][0] <= r['pH'] <= W['pH'][1]


def empty_by_definition(w, m):
    return m > WINDOWS[w]['Mg_max']


# ----------------------------------------------------------------------------- loaders (T3 D1, D3, D4, D8, D9, D10)

def load_marhys(require_T=False):
    z = zipfile.ZipFile(os.path.join(T3, 'raw', 'marhys4', 'MARHYS_DB_4_0.xlsx'))
    S = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8', 'replace'), flags=re.S)]
    xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
    LAB = {'Z': 'type', 'K': 'geol', 'G': 'rock1', 'E': 'area', 'C': 'vent'}
    NUM = {'AG': 'T', 'AK': 'pH', 'BM': 'Mg', 'BK': 'K', 'BR': 'Na', 'AZ': 'Ca', 'BF': 'Fe'}   # Ca mmol/kg, Fe umol/kg
    out = {}; dropped = {}
    for rn, body in re.findall(r'<row [^>]*r="(\d+)"[^>]*>(.*?)</row>', xml, flags=re.S):
        if int(rn) < 15: continue
        lab = {}; num = {}
        for col, a, v in re.findall(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(?:<v>(.*?)</v>)?</c>)', body, flags=re.S):
            if col in LAB and 't="s"' in a and v: lab[LAB[col]] = S[int(v)].strip()
            elif col in NUM and v and 't="s"' not in a:
                try: num[NUM[col]] = float(v)
                except ValueError: pass
        t = lab.get('type')
        if t not in ('HF', 'EM', 'SW'): continue
        cls = 'SW' if t == 'SW' else t3.vent_class(lab.get('geol', ''), lab.get('rock1', ''), lab.get('area', ''))
        need = ['pH', 'Mg', 'Ca', 'K', 'Na'] + (['T'] if require_T and t != 'SW' else [])
        key = f'{t}|{cls}'
        if not all(k in num for k in need):
            dropped[key] = dropped.get(key, 0) + 1; continue
        cluster = lab.get('vent', '') if cls == 'V2a_alkaline_serpentinite' else lab.get('area', '')   # D10
        out.setdefault(key, []).append({'pH': num['pH'], 'Mg': num['Mg'], 'Ca': num['Ca'], 'M': num['Na'] + num['K'],   # D8: mmol/kg read as mM
                                        'Fe': num['Fe'] / 1000.0 if 'Fe' in num else None, 'cluster': cluster})
    return out, dropped


def load_usgs(require_T=False):
    out = {}; dropped = {}
    with open(os.path.join(T3, 'raw', 'usgs_ynp_p92xkju7', 'YNP_WQ.csv'), newline='', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            wt = r['WaterType'].strip(); n = t3._num
            pH = n(r['pH_Field_StandardUnits']); pH = n(r['pH_Lab_StandardUnits']) if pH is None else pH      # D3
            Mg = n(r['Magnesium_Dissolved_MilligramsPerLiter_Mg']); Ca = n(r['Calcium_Dissolved_MilligramsPerLiter_Ca'])
            Na = n(r['Sodium_Dissolved_MilligramsPerLiter_Na']); K = n(r['Potassium_Dissolved_MilligramsPerLiter_K'])
            Fe = n(r['FerrousIron_Dissolved_MilligramsPerLiter_Fe(II)'])
            need = [pH, Mg, Ca, Na, K] + ([n(r['WaterTemperature_DegreesCelsius'])] if require_T else [])
            if None in need:
                dropped[wt] = dropped.get(wt, 0) + 1; continue
            out.setdefault(wt, []).append({'pH': pH, 'Mg': Mg / 24.305, 'Ca': Ca / 40.078, 'M': Na / 22.990 + K / 39.098,      # D8, mM
                                           'Fe': Fe / 55.845 if Fe is not None else None, 'cluster': r['Area'].strip()})
    return out, dropped


def all_classes():
    m, md = load_marhys(); u, ud = load_usgs()
    cls = {}
    for k, v in m.items(): cls['marhys:' + k] = v
    for k, v in u.items(): cls['usgs:' + k] = v
    return cls, {'marhys4': md, 'usgs': ud}


def nclu(rows):
    return len(set(r['cluster'] for r in rows))


# ----------------------------------------------------------------------------- count (blind; margins only)

def cmd_count():
    cls, dropped = all_classes()
    res = {'note': 'Margins only. The joint count A-and-B is never computed in this mode.', 'dropped': dropped, 'classes': {}}
    struct = {}
    print('Blind count. A = Mg band (RNA minimum <= Mg <= vesicle maximum). B = Ca, salt and pH inside the vesicle window.')
    print('Printed: rows/clusters. The joint A-and-B is NOT computed.\n')
    pairs = [(w, m) for w in ('P_strict', 'P_lenient', 'P_lenient_nopH', 'M', 'M_strict', 'M_lenient', 'J_alk') for m in ('R1', 'R50')]
    for w, m in pairs:
        if empty_by_definition(w, RNA[m]):
            print(f'  {w} x {m}: EMPTY BY DEFINITION (RNA minimum {RNA[m]} mM > vesicle Mg maximum {WINDOWS[w]["Mg_max"]} mM). No data needed.')
    print()
    for name in sorted(cls):
        rows = cls[name]; n = len(rows)
        sizes = {}
        for r in rows: sizes[r['cluster']] = sizes.get(r['cluster'], 0) + 1
        struct[name] = sorted(sizes.values(), reverse=True)
        c = {'rows': n, 'clusters': len(sizes), 'rows_with_Fe': sum(1 for r in rows if r['Fe'] is not None), 'windows': {}}
        for mname, mval in RNA.items():
            sub = [r for r in rows if r['Mg'] >= mval]
            c[f'Mg_ge_{mname}'] = [len(sub), nclu(sub)]
        print(f'{name}: complete rows {n}, clusters {len(sizes)}; Mg>=1 mM {c["Mg_ge_R1"][0]}/{c["Mg_ge_R1"][1]}; Mg>=50 mM {c["Mg_ge_R50"][0]}/{c["Mg_ge_R50"][1]}')
        for w in ('P_strict', 'P_lenient', 'P_lenient_nopH', 'M', 'M_strict', 'M_lenient', 'J_alk'):
            B = [r for r in rows if in_B(r, w)]
            entry = {'B': [len(B), nclu(B)]}
            line = f'    {w:14s} B {len(B):4d}/{nclu(B):2d}'
            for mname, mval in RNA.items():
                if empty_by_definition(w, mval):
                    entry[f'A_{mname}'] = 'empty by definition'; line += f' | A({mname}) empty-by-def'
                else:
                    A = [r for r in rows if in_A(r, w, mval)]
                    entry[f'A_{mname}'] = [len(A), nclu(A)]; line += f' | A({mname}) {len(A):4d}/{nclu(A):2d}'
            c['windows'][w] = entry; print(line)
        res['classes'][name] = c
    os.makedirs(os.path.join(EXP, 'scripts_out'), exist_ok=True); os.makedirs(os.path.join(EXP, 'data'), exist_ok=True)
    json.dump(res, open(os.path.join(EXP, 'scripts_out', 't4_blind_count.json'), 'w'), indent=1)
    json.dump({'note': 'complete-row cluster sizes per class; counts only', 'cluster_sizes': struct}, open(os.path.join(EXP, 'data', 'structure_counts.json'), 'w'), indent=1)
    return 0


def cmd_loadcheck():
    cls, dropped = all_classes()
    for name in sorted(cls):
        print(f'{name:40s} loaded {len(cls[name]):5d} clusters {nclu(cls[name]):3d}')
    print('dropped:', json.dumps(dropped))
    # cross-check against the T3 loaders: with T required, T4 rows must be a subset count <= T3 count (T4 also needs Ca)
    m3, _ = t3.load_marhys(); u3, _ = t3.load_usgs(); m4, _ = load_marhys(require_T=True); u4, _ = load_usgs(require_T=True)
    ok = True
    for k in sorted(set(m3) | set(m4)):
        a, b = len(m3.get(k, [])), len(m4.get(k, [])); ok &= b <= a
        print(f'  T3 {k:34s} {a:5d}   T4 with T required (also needs Ca) {b:5d}   lost to missing Ca {a - b}')
    for k in sorted(set(u3) | set(u4)):
        a, b = len(u3.get(k, [])), len(u4.get(k, [])); ok &= b <= a
        print(f'  T3 {k:34s} {a:5d}   T4 with T required (also needs Ca) {b:5d}   lost to missing Ca {a - b}')
    print('LOADCHECK', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


# ----------------------------------------------------------------------------- statistics

def cluster_table(rows, w, m):
    """Per cluster: [n, nA, nB, nJ]."""
    t = {}
    for r in rows:
        c = t.setdefault(r['cluster'], [0, 0, 0, 0])
        a = in_A(r, w, m); b = in_B(r, w)
        c[0] += 1; c[1] += a; c[2] += b; c[3] += (a and b)
    return t


def stats(tab, keys):
    n = nA = nB = nJ = 0
    for k in keys:
        c = tab[k]; n += c[0]; nA += c[1]; nB += c[2]; nJ += c[3]
    J = nJ / n if n else float('nan')
    exp = (nA / n) * (nB / n) if n else float('nan')               # expected joint share when Mg is drawn at random within the class
    return dict(n=n, nA=nA, nB=nB, nJ=nJ, J=J, pA=nA / n if n else float('nan'), pB=nB / n if n else float('nan'),
                cond=nJ / nA if nA else float('nan'), expected=exp, rho=J / exp if exp > 0 else float('nan'))


def ci(vals):
    v = sorted(x for x in vals if not math.isnan(x))
    if not v: return [float('nan'), float('nan')]
    return [v[int(0.025 * (len(v) - 1))], v[int(math.ceil(0.975 * (len(v) - 1)))]]


def window_result(rows, w, m, n_boot, rng):
    tab = cluster_table(rows, w, m); keys = sorted(tab)
    s = stats(tab, keys)
    s['clusters'] = len(keys); s['clusters_A'] = sum(1 for k in keys if tab[k][1]); s['clusters_J'] = sum(1 for k in keys if tab[k][3])
    # null within cluster: expected joint share when Mg is shuffled inside each area only
    s['expected_within_cluster'] = sum(tab[k][1] * tab[k][2] / tab[k][0] for k in keys) / s['n'] if s['n'] else float('nan')
    draws = {'J': [], 'cond': [], 'rho': [], 'pA': [], 'expected': []}
    for _ in range(n_boot):
        d = stats(tab, [keys[rng.randrange(len(keys))] for _ in keys])
        for q in draws: draws[q].append(d[q])
    for q in draws: s[q + '_ci'] = ci(draws[q])
    for q in ('J', 'cond'):
        v = sorted(x for x in draws[q] if not math.isnan(x))
        s[q + '_killlo'] = v[int(CFG['kill_tail'] * (len(v) - 1))] if v else float('nan')
    return s


def verdict_share(base, strict, lenient, c=CFG):
    """Springs and lakes. Claim U: the setting does not offer the joint window. Decision on the row share J."""
    if base['n'] < c['min_rows'] or base['clusters'] < c['min_clusters']:
        return 'cannot decide by design', ''
    kill = base['J_killlo'] >= c['kill_J_lo'] and base['clusters_J'] >= c['kill_clusters']
    supp = base['J'] <= c['support_J'] and base['clusters_J'] <= c['support_clusters']
    if kill:
        if strict is not None and not (strict['J_killlo'] >= c['kill_J_lo'] and strict['clusters_J'] >= c['kill_clusters']):
            return 'not reported as a kill', 'fragile: strict window'
        return 'U killed', label(base)
    if supp:
        if not (lenient['J'] <= c['support_J'] and lenient['clusters_J'] <= c['support_clusters']):
            return 'not reported as support', 'window-dependent'
        return 'U supported', label(lenient)
    return 'inconclusive', ''


def verdict_cond(base, strict, lenient, c=CFG):
    """Vents. Mg in a sampled vent fluid is a seawater fraction, so the decision is on P(B | A)."""
    if base['nA'] < c['min_rows'] or base['clusters_A'] < c['min_clusters']:
        return 'cannot decide by design', ''
    kill = base['cond_killlo'] >= c['vent_kill_cond_lo']
    supp = base['cond'] <= c['vent_support_cond']
    if kill:
        if strict is not None and not (strict['nA'] >= c['min_rows'] and strict['cond_killlo'] >= c['vent_kill_cond_lo']):
            return 'not reported as a kill', 'fragile: strict window'
        return 'U killed', ''
    if supp:
        if not (lenient['nA'] >= c['min_rows'] and lenient['cond'] <= c['vent_support_cond']):
            return 'not reported as support', 'window-dependent'
        return 'U supported', ''
    return 'inconclusive', ''


def label(s, c=CFG):
    """Why the window is closed or open. Attribution only; never changes a verdict."""
    if s['pA_ci'][1] <= c['label_Mg_poor']: return 'Mg-poor: the Mg band alone decides'
    if s['expected_ci'][0] >= c['label_cov_expected'] and s['rho_ci'][1] < c['label_cov_rho_hi']: return 'covariation closes the window'
    if s['rho_ci'][0] > 1.0: return 'covariation opens the window'
    return 'no covariation shown'


def analyse(rows, arm, m, n_boot, rng, kind):
    bw, sw, lw = ARMS[arm]
    out = {'arm': arm, 'rna': m, 'base_window': bw}
    if empty_by_definition(bw, RNA[m]):
        out['verdict'] = 'empty by definition'; out['label'] = 'thresholds alone; no field data used'; return out
    base = window_result(rows, bw, RNA[m], n_boot, rng)
    strict = window_result(rows, sw, RNA[m], n_boot, rng) if sw else None
    lenient = window_result(rows, lw, RNA[m], n_boot, rng)
    v, lab = (verdict_share if kind == 'share' else verdict_cond)(base, strict, lenient)
    out.update(verdict=v, label=lab, base=base, strict=strict, lenient=lenient)
    return out


def mixing_guard(em_rows, sw, w, m):
    """Vents only, cations only. For each end-member row, does the straight mixing line with seawater pass through
    the Mg band with Ca and salt inside the window at some seawater fraction? pH does not mix linearly; it is left out."""
    W = WINDOWS[w]; hit = 0; n = 0
    for e in em_rows:
        d = sw['Mg'] - e['Mg']
        if d <= 0: continue
        n += 1
        f0 = max(0.0, (m - e['Mg']) / d); f1 = min(1.0, (W['Mg_max'] - e['Mg']) / d)
        if f1 < f0: continue
        ok = False
        for f in (f0, f1):          # Ca and salt are linear in f, so the endpoints of the band are enough
            ca = f * sw['Ca'] + (1 - f) * e['Ca']; M = f * sw['M'] + (1 - f) * e['M']
            ok |= ca <= W['Ca_max'] and M <= W['M_max']
        hit += ok
    return {'em_rows': n, 'lines_through_window': hit, 'share': hit / n if n else float('nan')}


# ----------------------------------------------------------------------------- planted (synthetic only)

GOOD = dict(pH=7.8, Ca=0.3, M=20.0)


def synth(sizes, world, rng):
    """Synthetic rows on the real cluster sizes. Values are invented; only the sizes are real."""
    rows = []
    a, b = world.get('a', 0.0), world.get('b', 0.6)
    for ci_, n in enumerate(sizes):
        ea, eb = rng.gauss(0, 1.0), rng.gauss(0, 1.0)                 # area effects on the logit scale
        pa = 1 / (1 + math.exp(-(math.log(a / (1 - a)) + ea))) if 0 < a < 1 else a
        pb = 1 / (1 + math.exp(-(math.log(b / (1 - b)) + eb))) if 0 < b < 1 else b
        if world.get('only_clusters') is not None and ci_ >= world['only_clusters']: pa = 0.0
        for _ in range(n):
            inband = rng.random() < pa
            lo, hi = world.get('band', (1.2, 3.5))
            Mg = rng.uniform(lo, hi) if inband else math.exp(rng.uniform(math.log(0.005), math.log(0.5)))
            good = rng.random() < pb
            if world.get('couple') and inband: good = False
            r = dict(GOOD, Mg=Mg, Fe=None, cluster=f'c{ci_}')
            if not good:
                mode = world.get('bad', 'acid')
                if mode == 'acid': r['pH'] = rng.uniform(2.0, 4.0)
                elif mode == 'calcium': r['Ca'] = rng.uniform(4.0, 9.0)
                elif mode == 'ph_edge': r['pH'] = rng.uniform(5.6, 6.3)
            r['pH'] += rng.gauss(0, 0.1) if good else 0.0
            rows.append(r)
    return rows


WORLDS = [
    ('W0 Mg-poor',              dict(a=0.0),                                  'U supported; label Mg-poor'),
    ('W1 window common',        dict(a=0.3, b=0.6),                           'U killed'),
    ('W2 acid pH closes',       dict(a=0.3, b=0.6, couple=True),              'not reported as support (window-dependent)'),
    ('W3 rare, on the vent bar', dict(a=0.1, b=0.25),                         'no kill, no support'),
    ('W3b on both bars',        dict(a=0.2, b=0.25),                          'no support; kills near nominal'),
    ('W3c below both bars',     dict(a=0.2, b=0.15),                          'no kill, no support'),
    ('W4 two areas only',       dict(a=0.6, b=0.9, only_clusters=2),          'no kill'),
    ('W5 pH edge',              dict(a=0.3, b=0.0, bad='ph_edge'),            'not reported as support (window-dependent)'),
    ('W6 Mg 5-9 mM',            dict(a=0.3, b=0.6, band=(5.0, 9.0)),          'not reported as support (window-dependent)'),
    ('W7 calcium closes',       dict(a=0.3, b=0.6, couple=True, bad='calcium'), 'U supported; label covariation'),
]


def cmd_planted():
    sc = json.load(open(os.path.join(EXP, 'data', 'structure_counts.json')))['cluster_sizes']
    rng = random.Random(CFG['seed']); runs, nb = 200, 400
    structures = [('usgs:thermal water', 'share'), ('marhys:HF|V1_basalt_ridge', 'cond'), ('marhys:HF|V2b_ultramafic_other', 'cond')]
    res = {'runs': runs, 'n_boot': nb, 'cells': []}
    for sname, kind in structures:
        sizes = sc[sname]
        print(f'\n{sname}: {sum(sizes)} rows, {len(sizes)} clusters; rule: {kind}')
        print(f'  {"world":26s} {"expected":44s} killed supp  incon notrep cannot | labels')
        for wname, world, expect in WORLDS:
            tally = {}; labels = {}
            for _ in range(runs):
                rows = synth(sizes, world, rng)
                o = analyse(rows, 'mixed', 'R1', nb, rng, kind)
                tally[o['verdict']] = tally.get(o['verdict'], 0) + 1
                if o['label']: labels[o['label']] = labels.get(o['label'], 0) + 1
            g = lambda k: tally.get(k, 0) / runs
            cell = dict(structure=sname, rule=kind, world=wname, expected=expect, killed=g('U killed'), supported=g('U supported'), inconclusive=g('inconclusive'),
                        not_reported=g('not reported as a kill') + g('not reported as support'), cannot=g('cannot decide by design'),
                        labels={k: v / runs for k, v in labels.items()})
            res['cells'].append(cell)
            print(f'  {wname:26s} {expect:44s} {cell["killed"]:.2f}   {cell["supported"]:.2f}  {cell["inconclusive"]:.2f}  {cell["not_reported"]:.2f}   {cell["cannot"]:.2f}  | ' +
                  '; '.join(f'{k} {v:.2f}' for k, v in sorted(cell['labels'].items())))
    os.makedirs(os.path.join(EXP, 'scripts_out'), exist_ok=True)
    json.dump(res, open(os.path.join(EXP, 'scripts_out', 't4_planted.json'), 'w'), indent=1)
    return 0


# ----------------------------------------------------------------------------- real (sealed)

def seal_ok():
    hp = os.path.join(REPO, 'docs', 'prereg', 'HASHES.txt')
    if not os.path.exists(hp): return False, 'docs/prereg/HASHES.txt not found'
    sealed = {}
    for ln in open(hp, encoding='utf-8'):
        parts = ln.split()
        if len(parts) >= 2: sealed[parts[1]] = parts[0]          # the last line for a path wins
    for rel in (PREREG_REL, SCRIPT_REL):
        if rel not in sealed: return False, f'no HASHES.txt line for {rel}'
        if sealed[rel] != t3.sha256(os.path.join(REPO, rel)): return False, f'{rel} differs from its sealed hash'
    return True, 'sealed'


def median(v):
    v = sorted(v); n = len(v)
    return v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])


def cmd_real():
    ok, why = seal_ok()
    if not ok:
        print('REFUSED: T4 is not sealed (%s). Seal the prereg and this script in docs/prereg/HASHES.txt first.' % why)
        return 2
    cls, dropped = all_classes(); rng = random.Random(CFG['seed']); nb = CFG['n_boot_real']
    res = {'dropped': dropped, 'definition_arms': {}, 'settings': {}}
    for w in ('P_strict', 'P_lenient', 'M', 'M_lenient', 'J_alk'):
        for m in RNA: res['definition_arms'][f'{w} x {m}'] = 'empty by definition' if empty_by_definition(w, RNA[m]) else 'open in threshold space'
    swr = cls.get('marhys:SW|SW', [])
    sw = {k: median([r[k] for r in swr]) for k in ('Mg', 'Ca', 'M')} if swr else None
    plan = [('usgs:thermal water', 'share'), ('usgs:lake', 'share'), ('usgs:river, stream, or creek', 'share')] + [('marhys:HF|' + c, 'cond') for c in VENT_CLASSES]
    for name, kind in plan:
        rows = cls.get(name, [])
        if not rows: continue
        for arm in ('mixed', 'pure'):
            o = analyse(rows, arm, 'R1', nb, rng, kind)
            if kind == 'cond' and sw and 'base' in o:
                em = cls.get(name.replace('HF|', 'EM|'), [])
                o['mixing_guard'] = mixing_guard(em, sw, o['base_window'], RNA['R1'])
                g = o['mixing_guard']
                if g['em_rows'] >= CFG['min_rows']:
                    if o['verdict'] == 'U killed' and g['share'] <= CFG['vent_support_cond']: o['verdict'], o['label'] = 'not reported as a kill', 'sampling-driven'
                    if o['verdict'] == 'U supported' and g['share'] >= CFG['vent_kill_cond_lo']: o['verdict'], o['label'] = 'not reported as support', 'sampling-driven'
            res['settings'][f'{name} | {arm} x R1'] = o
            print(f'{name:36s} {arm:5s} x R1  {o["verdict"]}  {o["label"]}')
        res['settings'][f'{name} | J_alk x R1 (reported only)'] = window_result(rows, 'J_alk', RNA['R1'], nb, rng)
    json.dump(res, open(os.path.join(EXP, 'scripts_out', 't4_real.json'), 'w'), indent=1)
    return 0


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'count': sys.exit(cmd_count())
    if mode == 'loadcheck': sys.exit(cmd_loadcheck())
    if mode == 'planted': sys.exit(cmd_planted())
    if mode == 'real': sys.exit(cmd_real())
    print(__doc__); sys.exit(1)
