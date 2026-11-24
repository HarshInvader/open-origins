#!/usr/bin/env python3
"""T7: does evaporating real hot-spring water open the vesicle + RNA-copying window?
Prereg (DRAFT until sealed): docs/prereg/t7_evaporation_window.md

Hypothesis H (the claim under test): evaporating real hot-spring waters brings Mg into the range
for nonenzymatic RNA copying (>= 1 mM) while the water is still inside the fatty-acid / mixed-amphiphile
vesicle window (Ca, Na + K and pH limits as in T4).

Modes (run from the repo root, single process, under nice):
  .venv/bin/python -I scripts/t7_analysis.py count      declared blind count: rows with each input filled, margins only
  .venv/bin/python -I scripts/t7_analysis.py gate       model gate: seawater sequence (Milshteyn 2018 Table 3 water) and
                                                         the published Lake Magadi PHREEQC-Pitzer path (Getenet 2022)
  .venv/bin/python -I scripts/t7_analysis.py planted    synthetic template waters through PHREEQC, then synthetic worlds
                                                         on the real cluster sizes; no field value is read
  .venv/bin/python -I scripts/t7_analysis.py dryrun     the `real` code on field rows whose solute columns are permuted
                                                         independently across rows (a code check; nothing real is estimated)
  .venv/bin/python -I scripts/t7_analysis.py sealcheck  says whether `real` would run
  .venv/bin/python -I scripts/t7_analysis.py real       the sealed test; refuses unless docs/prereg/HASHES.txt has a line naming
                                                         this script with its current sha256 AND a line naming the prereg with its
                                                         current sha256
(.venv lives in experiments/t7_evaporation_window/; paths above are relative to that folder.)

Engine: PHREEQC (IPhreeqc 3.x, via the phreeqpython 1.6.2 wheel) with its bundled pitzer.dat, plus three fluoride
records (F-, HF, MgF+ and Fluorite) copied from the bundled phreeqc.dat, because pitzer.dat has no F and fluorite is a
real Ca sink in Yellowstone alkaline-chloride water.
"""
import csv, hashlib, json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(EXP))
SELF = 'experiments/t7_evaporation_window/scripts/t7_analysis.py'
PREREG_REL = 'docs/prereg/t7_evaporation_window.md'
OUT = os.path.join(EXP, 'scripts_out')

F = {
    'usgs': 'experiments/t3_rna_persistence/raw/usgs_ynp_p92xkju7/YNP_WQ.csv',
    'hist': 'experiments/t3_rna_persistence/raw/usgs_ynp_historic_p9ksevi1/Yellowstone_Water_Chemistry_1883-2021.csv',
}
SHA = {
    'usgs': '084cb39954ae8cf5740302ded09faaef4a81d90dbeeb399718f848187d7e7911',
    'hist': 'cee22209d5a350ed10af3bb54ee84a1525202f05b50537708eaf7677296b7e90',
}

SEED = 20261127
PITZER_SHA = 'eb5051704fad461c4e5325721afc7b9025fad7c2906f72ed48ae182aa2c1a5c9'   # bundled pitzer.dat in phreeqpython 1.6.2
CFG = dict(
    n_boot_real=10000,
    min_rows=30, min_areas=5,
    bar=0.05,                 # D7: the share that counts as "evaporation opens the window"
    support_areas=5,          # support needs passing rows in >= 5 areas
    tail=0.005,               # D7: 0.5th / 99.5th percentile of the area bootstrap
    rare=0.01,                # label only
    max_fail_share=0.05,      # D9: more failed paths than this and the combo is not reported
    cbe_max=10.0,             # D3: |charge-balance error| <= 10 % at the raw state
    T_cap=95.0,               # D4: pool temperature = min(spring T, 95 C)
    cf_max=1000.0, n_steps=61,
    M_stop=1500.0,            # D5: stop the path once Na + K would pass 1500 mM by conservative scaling
    pco2_open=-3.4,           # D4: log pCO2 of the open variant (modern air)
)

INF = float('inf')
# T4 windows (docs/prereg/t4_vesicle_rna_window.md), mM. M = Na + K. M_strict has no Fe term here (no Fe in the model).
WINDOWS = {
    'M':              dict(Mg_max=4.0,  Ca_max=1.9, M_max=600.0,  pH=(6.5, 12.0)),
    'M_strict':       dict(Mg_max=4.0,  Ca_max=0.5, M_max=600.0,  pH=(7.0, 11.5)),
    # lenient guards: T4's lenient windows with a pH floor of 3.0 (Milshteyn 2018 saw lauric-acid vesicles at pH 3.3 in
    # Yellowstone water; nothing opened shows vesicles below that). Changed after planted round 1, before any field path.
    'M_lenient_pH3':  dict(Mg_max=10.0, Ca_max=1.9, M_max=1000.0, pH=(3.0, INF)),
    'P_lenient':      dict(Mg_max=2.0,  Ca_max=2.0, M_max=200.0,  pH=(7.0, 9.5)),
    'P_lenient_pH3':  dict(Mg_max=2.0,  Ca_max=2.0, M_max=200.0,  pH=(3.0, INF)),
    'P_strict':       dict(Mg_max=0.5,  Ca_max=0.5, M_max=200.0,  pH=(7.0, 9.5)),    # empty with R1 by definition
    # reported only: Mg >= 10 mM with the mixed-arm Ca, salt and pH limits and no Mg ceiling
    'R10_open':       dict(Mg_max=INF,  Ca_max=1.9, M_max=600.0,  pH=(6.5, 12.0), Mg_min=10.0),
}
R1 = 1.0
ARMS = {   # arm -> base window, window of the support guard, window of the kill guard
    'mixed': ('M', 'M_strict', 'M_lenient_pH3'),
    'pure':  ('P_lenient', 'P_lenient', 'P_lenient_pH3'),
}

LATE = ['Halite', 'Sylvite', 'Mirabilite', 'Thenardite', 'Glauberite', 'Gaylussite', 'Pirssonite', 'Trona', 'Natron',
        'Nahcolite', 'Burkeite', 'Epsomite', 'Hexahydrite', 'Kieserite', 'Bloedite', 'Polyhalite', 'Syngenite', 'Glaserite',
        'Arcanite', 'Kainite', 'Carnallite', 'Bischofite', 'Leonite', 'Schoenite']
MINSETS = {   # D6. (phase, target SI)
    'base':     [('Calcite', 0.0), ('Gypsum', 0.0), ('Anhydrite', 0.0), ('Fluorite', 0.0), ('SiO2(a)', 0.0),
                 ('Sepiolite(d)', 0.0), ('Brucite', 0.0)] + [(p, 0.0) for p in LATE],
    'generous': [('Calcite', 0.0), ('Gypsum', 0.0), ('Anhydrite', 0.0), ('Fluorite', 0.0), ('SiO2(a)', 0.0)] + [(p, 0.0) for p in LATE],
    'strict':   [('Calcite', 0.5), ('Gypsum', 0.0), ('Anhydrite', 0.0), ('SiO2(a)', 0.0),
                 ('Sepiolite', 0.0), ('Brucite', 0.0)] + [(p, 0.0) for p in LATE],
}
COMBOS = {   # name -> (mineral set, temperature rule, gas)
    'base_Ts_closed':  ('base', 'spring', 'closed'),
    'base_Ts_open':    ('base', 'spring', 'open'),
    'base_25_closed':  ('base', '25', 'closed'),
    'base_25_open':    ('base', '25', 'open'),
    'gen_Ts_closed':   ('generous', 'spring', 'closed'),
    'gen_Ts_open':     ('generous', 'spring', 'open'),
    'gen_25_closed':   ('generous', '25', 'closed'),
    'gen_25_open':     ('generous', '25', 'open'),
    'strict_Ts_closed': ('strict', 'spring', 'closed'),
}
PRIMARY = 'base_Ts_closed'
GEN = ['gen_Ts_closed', 'gen_Ts_open', 'gen_25_closed', 'gen_25_open']

FLUORIDE = """
SOLUTION_MASTER_SPECIES
F F- 0 F 18.9984
SOLUTION_SPECIES
F- = F-
 -gamma 3.5 0
H+ + F- = HF
 -log_k 3.18
 -delta_h 3.18 kcal
 -analytic -2.033 0.012645 429.01
Mg+2 + F- = MgF+
 -log_k 1.82
 -delta_h 3.20 kcal
 -gamma 4.5 0
PHASES
Fluorite
 CaF2 = Ca+2 + 2 F-
 -log_k -10.6
 -delta_h 4.69 kcal
 -analytic 66.348 0.0 -4298.2 -25.271
END
"""

MW = dict(Ca=40.078, Mg=24.305, Na=22.990, K=39.098, Cl=35.453, SO4=96.06, HCO3=61.017, SiO2=60.084, F=18.998,
          Li=6.941, B=10.81, Br=79.904)


# ----------------------------------------------------------------------------- utilities

def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def dump(name, obj):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), 'w') as f:
        json.dump(obj, f, indent=1, default=lambda x: None if isinstance(x, float) and math.isnan(x) else str(x))


def num(s):
    """T3 D9: '<x' enters as x/2; blanks and codes are missing."""
    s = (s or '').strip()
    if s in ('', '--', 'NA', 'na', 'nd', 'ND'):
        return None
    try:
        return float(s[1:]) / 2 if s.startswith('<') else float(s)
    except ValueError:
        return None


# ----------------------------------------------------------------------------- PHREEQC engine

class Engine:
    def __init__(self):
        import phreeqpython
        from phreeqpython.viphreeqc import VIPhreeqc
        self.db = os.path.join(os.path.dirname(phreeqpython.__file__), 'database', 'pitzer.dat')
        self.version = getattr(phreeqpython, '__version__', '1.6.2')
        self.db_sha = sha256(self.db)
        self._V = VIPhreeqc
        self.fresh()

    def fresh(self):
        self.ip = self._V()
        self.ip.load_database(self.db)
        self.ip.run_string(FLUORIDE)

    def run(self, s):
        self.ip.run_string(s)
        a = self.ip.get_selected_output_array()
        hdr = a[0]
        return [dict(zip(hdr, r)) for r in a[1:]]


def cf_grid(cf_max, n):
    return [cf_max ** (i / (n - 1)) for i in range(n)]


def solution_block(w, T):
    """w: solutes in mmol/kgw (keys Ca Mg Na K Cl SO4 Alk Si F Li B Br), pH, T in C."""
    L = ['SOLUTION 1', f' temp {T:.3f}', f' pH {w["pH"]:.3f}', ' units mmol/kgw']
    for k, el in (('Ca', 'Ca'), ('Mg', 'Mg'), ('Na', 'Na'), ('K', 'K'), ('Cl', 'Cl'), ('SO4', 'S(6)'), ('Si', 'Si'),
                  ('F', 'F'), ('Li', 'Li'), ('B', 'B'), ('Br', 'Br')):
        v = w.get(k)
        if v is not None and v > 0:
            L.append(f' {el} {v:.6g}')
    if w.get('Alk') is not None and w['Alk'] > 0 and w['pH'] >= 4.5:     # D1: no alkalinity term in acid water
        L.append(f' Alkalinity {w["Alk"]:.6g}')
    if w.get('C') is not None and w['C'] > 0:
        L.append(f' C(4) {w["C"]:.6g}')
    return L


def evaporate(eng, w, minset, temp_rule, gas, cf_max=None, n=None, extra_si=(), extra_tot=()):
    """One stepwise evaporation path. Returns (steps, info). steps[0] is the raw water (no minerals, measured T and pH);
    steps[1:] are equilibrium states at CF on a log grid from 1 to cf_max, with the chosen minerals allowed to precipitate
    only (initial amount 0), at the pool temperature."""
    T0 = min(w['T'], CFG['T_cap'])
    M0 = w.get('Na', 0) + w.get('K', 0)
    if cf_max is None:
        cf_max = min(CFG['cf_max'], max(1.5, CFG['M_stop'] / max(M0, 1e-9)))
    n = n or CFG['n_steps']
    tries = []
    for attempt in range(4):
        cfs = cf_grid(cf_max, n)
        rem = [55.5084 * (1 - 1 / c) for c in cfs]
        sis = sorted(set(['Calcite', 'Gypsum', 'Fluorite', 'SiO2(a)', 'Sepiolite(d)', 'Brucite', 'Halite'] + list(extra_si)))
        # one simulation: the initial-solution row (state i_soln) is the raw water; the reaction rows (state react) are the path
        L = ['SELECTED_OUTPUT 1', ' -reset false', ' -state true', ' -pH true', ' -water true', ' -ionic_strength true',
             ' -percent_error true', ' -totals Ca Mg Na K Cl ' + ' '.join(extra_tot), ' -si ' + ' '.join(sis),
             ' -equilibrium_phases ' + ' '.join(p for p, _ in minset)]
        S = solution_block(w, T0)
        if w.get('Cl_charge'):
            S = [l if not l.startswith(' Cl ') else l + ' charge' for l in S]
        L += S + ['REACTION 1', ' H2O -1', ' ' + ' '.join('%.8f' % r for r in rem)]
        if temp_rule == '25':
            L += ['REACTION_TEMPERATURE 1', ' 25']
        L += ['EQUILIBRIUM_PHASES 1'] + [f' {p} {si} 0' for p, si in minset]
        if gas == 'open':
            L += [f' CO2(g) {CFG["pco2_open"]} 10']
        L += ['END']
        try:
            rows = eng.run('\n'.join(L))
        except Exception as e:   # numerical failure near dryness: shorten the path and retry; the prefix is still valid
            tries.append(str(e).splitlines()[-1][:160])
            eng.fresh()
            if attempt == 0:
                n = 2 * n                                  # retry 1: same end point, finer steps
            else:
                cf_max = max(1.2, cf_max ** 0.85)          # retries 2-3: shorter path
            continue
        raw = [r for r in rows if r['state'] == 'i_soln']
        rx = [r for r in rows if r['state'] == 'react']
        steps = []
        for i, r in enumerate(raw[:1] + rx):
            cf = 1.0 if i == 0 else cfs[i - 1]
            st = dict(cf=cf, raw=(i == 0), pH=r['pH'], mu=r['mu'], cbe=r.get('pct_err'),
                      Ca=1000 * r['Ca(mol/kgw)'], Mg=1000 * r['Mg(mol/kgw)'], M=1000 * (r['Na(mol/kgw)'] + r['K(mol/kgw)']),
                      Cl=1000 * r['Cl(mol/kgw)'])
            for p in sis:
                st['si_' + p] = r.get('si_' + p)
            for p, _ in minset:
                st['eq_' + p] = r.get(p)
            for t in extra_tot:
                st['tot_' + t] = 1000 * r.get(t + '(mol/kgw)', 0.0)
            steps.append(st)
        return steps, dict(cf_max=cf_max, attempts=attempt + 1, errors=tries, truncated=attempt > 0, failed=False)
    return [], dict(cf_max=cf_max, attempts=4, errors=tries, truncated=True, failed=True)


def in_window(st, wname, rmin=R1):
    W = WINDOWS[wname]
    lo = W.get('Mg_min', rmin)
    return (lo <= st['Mg'] <= W['Mg_max'] and st['Ca'] <= W['Ca_max'] and st['M'] <= W['M_max']
            and W['pH'][0] <= st['pH'] <= W['pH'][1])


def path_flags(steps):
    return {wn: any(in_window(s, wn) for s in steps) for wn in WINDOWS}


def path_diag(steps):
    """Attribution for the primary path (reported only). Which limit is out at the first state with Mg >= 1 mM."""
    d = dict(Mg_max_reached=max((s['Mg'] for s in steps), default=float('nan')), cf_reached=max((s['cf'] for s in steps), default=float('nan')))
    first = next((s for s in steps if s['Mg'] >= R1), None)
    if first is None:
        d['at_Mg1'] = 'Mg never reaches 1 mM'
    else:
        W = WINDOWS['M']; bad = []
        if first['Mg'] > W['Mg_max']: bad.append('Mg>4')
        if first['Ca'] > W['Ca_max']: bad.append('Ca')
        if first['M'] > W['M_max']: bad.append('salt')
        if not (W['pH'][0] <= first['pH'] <= W['pH'][1]): bad.append('pH')
        d['at_Mg1'] = 'inside window M' if not bad else 'out: ' + '+'.join(bad)
        d['cf_Mg1'] = first['cf']
    for key, cond in (('cf_Ca_over', lambda s: s['Ca'] > 1.9), ('cf_M_over', lambda s: s['M'] > 600.0)):
        s = next((s for s in steps if cond(s)), None)
        d[key] = s['cf'] if s else None
    return d


def run_water(eng, w, combos=COMBOS):
    res = {}
    for cname, (ms, tr, gas) in combos.items():
        steps, info = evaporate(eng, w, MINSETS[ms], tr, gas)
        res[cname] = dict(flags=path_flags(steps) if steps else None, failed=info['failed'], truncated=info['truncated'])
        if cname == PRIMARY:
            res[cname]['diag'] = path_diag(steps) if steps else None
            res[cname]['cbe'] = steps[0]['cbe'] if steps else None
    return res


# ----------------------------------------------------------------------------- field rows

def load_usgs(path_rel, kind):
    """Rows with the full input set, in mmol/kgw (mg/L divided by atomic or formula mass; T3 D8). Returns rows, margins."""
    rows, marg = [], {}
    p = os.path.join(REPO, path_rel)
    if kind == 'usgs':
        col = dict(type='WaterType', area='Area', date='CollectionDate', pHf='pH_Field_StandardUnits', pHl='pH_Lab_StandardUnits',
                   T='WaterTemperature_DegreesCelsius', Ca='Calcium_Dissolved_MilligramsPerLiter_Ca', Mg='Magnesium_Dissolved_MilligramsPerLiter_Mg',
                   Na='Sodium_Dissolved_MilligramsPerLiter_Na', K='Potassium_Dissolved_MilligramsPerLiter_K',
                   Alk='Alkalinity_Dissolved_MilligramsPerLiter_HCO3', Cl='Chloride_Dissolved_MilligramsPerLiter_Cl',
                   SO4='Sulfate_Dissolved_MilligramsPerLiter_SO4', SiO2='Silica_Dissolved_MilligramsPerLiter_SiO2',
                   F='Fluoride_Dissolved_MilligramsPerLiter_F', Li='Lithium_Dissolved_MilligramsPerLiter_Li',
                   B='Boron_Dissolved_MilligramsPerLiter_B', Br='Bromide_Dissolved_MilligramsPerLiter_Br', id='SampleID')
        enc = 'utf-8'
    else:
        col = {'type': 'Sample Type', 'area': 'Area', 'date': 'Sample Collection Year [YYYY]', 'pHf': 'pH (field) [standard units]',
               'pHl': 'pH (lab) [standard units]', 'T': 'Water Temperature [Celsius]', 'Ca': 'Calcium (Ca) [mg/L]',
               'Mg': 'Magnesium (Mg) [mg/L]', 'Na': 'Sodium (Na) [mg/L]', 'K': 'Potassium (K) [mg/L]', 'Alk': 'Alkalinity (HCO3) [mg/L]',
               'Cl': 'Chloride (Cl) [mg/L]', 'SO4': 'Sulfate (SO4) [mg/L]', 'SiO2': 'Silica (SiO2) [mg/L]', 'F': 'Fluoride (F) [mg/L]',
               'Li': 'Lithium (Li) [mg/L]', 'B': 'Boron (B) [mg/L]', 'Br': 'Bromide (Br) [mg/L]', 'id': 'Database ID'}
        enc = 'utf-8-sig'
    with open(p, newline='', encoding=enc, errors='replace') as f:
        for r in csv.DictReader(f):
            wt = r[col['type']].strip()
            if kind == 'hist':
                yr = num(r[col['date']])
                if yr is None or yr >= 2009:          # D2: replication set = historic rows dated before 2009 (T3 D11)
                    marg.setdefault(wt, {}).setdefault('dropped_2009_or_later_or_undated', 0)
                    marg[wt]['dropped_2009_or_later_or_undated'] += 1
                    continue
            m = marg.setdefault(wt, {})
            m['rows'] = m.get('rows', 0) + 1
            v = {k: num(r[col[k]]) for k in ('T', 'Ca', 'Mg', 'Na', 'K', 'Alk', 'Cl', 'SO4', 'SiO2', 'F', 'Li', 'B', 'Br')}
            pH = num(r[col['pHf']]);  pH = num(r[col['pHl']]) if pH is None else pH       # T3 D3
            v['pH'] = pH
            for k in ('pH', 'T', 'Ca', 'Mg', 'Na', 'K', 'Alk', 'Cl', 'SO4', 'SiO2', 'F'):
                if v[k] is not None:
                    m['has_' + k] = m.get('has_' + k, 0) + 1
            # D1: alkalinity may be missing only in acid water (pH < 4.5), where it is set to zero
            alk_ok = v['Alk'] is not None or (pH is not None and pH < 4.5)
            need = all(v[k] is not None for k in ('pH', 'T', 'Ca', 'Mg', 'Na', 'K', 'Cl', 'SO4', 'SiO2')) and alk_ok
            if not need:
                m['incomplete'] = m.get('incomplete', 0) + 1
                continue
            m['complete'] = m.get('complete', 0) + 1
            acid = pH < 4.5
            w = dict(type=wt, area=r[col['area']].strip(), id=r[col['id']].strip(), pH=pH, T=v['T'],
                     Ca=v['Ca'] / MW['Ca'], Mg=v['Mg'] / MW['Mg'], Na=v['Na'] / MW['Na'], K=v['K'] / MW['K'],
                     Cl=v['Cl'] / MW['Cl'], SO4=v['SO4'] / MW['SO4'], Si=v['SiO2'] / MW['SiO2'],
                     Alk=0.0 if acid else v['Alk'] / MW['HCO3'],
                     F=(v['F'] or 0.0) / MW['F'], Li=(v['Li'] or 0.0) / MW['Li'], B=(v['B'] or 0.0) / MW['B'], Br=(v['Br'] or 0.0) / MW['Br'])
            rows.append(w)
    return rows, marg


SOLUTES = ('Ca', 'Mg', 'Na', 'K', 'Cl', 'SO4', 'Si', 'Alk', 'F', 'Li', 'B', 'Br', 'pH', 'T')


def cbe_filter(eng, rows):
    """D3: |charge-balance error| at the raw state <= cbe_max. Uses only the raw speciation (no path, no window)."""
    keep, out = [], 0
    for w in rows:
        L = solution_block(w, min(w['T'], CFG['T_cap'])) + ['SELECTED_OUTPUT 1', ' -reset false', ' -percent_error true', 'END']
        try:
            e = eng.run('\n'.join(L))[0]['pct_err']
        except Exception:
            eng.fresh(); e = None
        w['cbe'] = e
        if e is not None and abs(e) <= CFG['cbe_max']:
            keep.append(w)
        else:
            out += 1
    return keep, out


# ----------------------------------------------------------------------------- statistics and rules

def share_stats(flags, areas, n_boot, rng):
    """flags: list of 0/1 per row; areas: area per row. Row share with an area (cluster) bootstrap."""
    tab = {}
    for f, a in zip(flags, areas):
        t = tab.setdefault(a, [0, 0]); t[0] += 1; t[1] += f
    keys = sorted(tab)
    n = sum(tab[k][0] for k in keys); k_ = sum(tab[k][1] for k in keys)
    S = k_ / n if n else float('nan')
    draws = []
    for _ in range(n_boot):
        nn = kk = 0
        for _ in keys:
            t = tab[keys[rng.randrange(len(keys))]]; nn += t[0]; kk += t[1]
        draws.append(kk / nn)
    draws.sort()
    lo = draws[int(CFG['tail'] * (len(draws) - 1))]
    hi = draws[int(math.ceil((1 - CFG['tail']) * (len(draws) - 1)))]
    return dict(n=n, k=k_, S=S, lo=lo, hi=hi, areas=len(keys), areas_pass=sum(1 for a in keys if tab[a][1] > 0))


def verdict(base, sup_guard, kill_guard, fail_share):
    """D7, D8, D9."""
    c = CFG
    if fail_share > c['max_fail_share']:
        return 'not reported: model failures', ''
    if base['n'] < c['min_rows'] or base['areas'] < c['min_areas']:
        return 'cannot decide by design', ''
    sup = base['lo'] >= c['bar'] and base['areas_pass'] >= c['support_areas']
    kill = base['hi'] < c['bar']                     # no area cap on a kill (removed after planted round 1)
    if sup:
        if not (sup_guard['lo'] >= c['bar'] and sup_guard['areas_pass'] >= c['support_areas']):
            return 'not reported as support', 'fragile: strict minerals and window'
        return 'H supported', ''
    if kill:
        if not kill_guard['hi'] < c['bar']:
            return 'not reported as a kill', 'model-dependent: generous minerals or other path conditions open it'
        return 'H killed', 'rare (<= 1%)' if base['S'] <= c['rare'] else ''
    return 'inconclusive', ''


def analyse(results, areas, n_boot, rng):
    """results: list of run_water outputs, aligned with areas."""
    out = {}
    fails = {c: sum(1 for r in results if r[c]['failed']) / max(1, len(results)) for c in COMBOS}
    trunc = {c: sum(1 for r in results if r[c]['truncated']) for c in COMBOS}
    def fl(c, wn):
        return [int(bool(r[c]['flags'] and r[c]['flags'][wn])) for r in results]
    for arm, (bw, sw, kw) in ARMS.items():
        base = share_stats(fl(PRIMARY, bw), areas, n_boot, rng)
        sg = share_stats(fl('strict_Ts_closed', sw), areas, n_boot, rng)
        kflags = [int(any(r[c]['flags'] and r[c]['flags'][kw] for c in GEN + [PRIMARY, 'base_Ts_open', 'base_25_closed', 'base_25_open'])) for r in results]
        kg = share_stats(kflags, areas, n_boot, rng)
        fs = max(fails.values())          # D9: worst of all nine combos (every combo feeds a rule or a guard)
        v, lab = verdict(base, sg, kg, fs)
        out[arm] = dict(verdict=v, label=lab, base=base, support_guard=sg, kill_guard=kg, fail_share=fs)
    rep = {}
    for c in COMBOS:
        rep[c] = {wn: share_stats(fl(c, wn), areas, min(n_boot, 2000), rng) for wn in ('M', 'M_strict', 'M_lenient_pH3', 'P_lenient', 'R10_open')}
    out['reported_by_combo'] = rep
    out['failed_share_by_combo'] = fails
    out['truncated_by_combo'] = trunc
    att = {}
    for r in results:
        d = r[PRIMARY].get('diag')
        if d:
            att[d['at_Mg1']] = att.get(d['at_Mg1'], 0) + 1
    out['attribution_primary'] = att
    return out


# ----------------------------------------------------------------------------- count (blind, margins only)

def cmd_count():
    res = {'note': 'Margins only. No evaporation path is computed and no window is evaluated in this mode.', 'inputs': {}}
    for key in ('usgs', 'hist'):
        p = os.path.join(REPO, F[key]); res['inputs'][key] = dict(path=F[key], sha256=sha256(p))
    eng = Engine()
    res['engine'] = dict(phreeqpython=eng.version, pitzer_dat_sha256=eng.db_sha)
    struct = {}
    for key in ('usgs', 'hist'):
        rows, marg = load_usgs(F[key], key)
        print(f'\n== {key}  ({F[key]})')
        for wt in sorted(marg):
            m = marg[wt]
            print(f'  {wt:28s} ' + ', '.join(f'{k} {v}' for k, v in sorted(m.items())))
        bytype = {}
        for w in rows: bytype.setdefault(w['type'], []).append(w)
        res[key] = {'margins': marg, 'complete_then_cbe': {}}
        for wt, rr in sorted(bytype.items()):
            keep, out = cbe_filter(eng, rr)
            k20 = sum(1 for w in rr if w['cbe'] is not None and abs(w['cbe']) <= 20.0)
            nacid = sum(1 for w in keep if w['pH'] < 4.5)
            sizes = {}
            for w in keep: sizes[w['area']] = sizes.get(w['area'], 0) + 1
            res[key]['complete_then_cbe'][wt] = dict(complete=len(rr), complete_areas=len(set(w['area'] for w in rr)),
                                                    cbe_le_10=len(keep), cbe_le_10_areas=len(sizes), cbe_le_20=k20,
                                                    acid_rows_alk_set_0=nacid, F_missing_set_0=sum(1 for w in keep if w['F'] == 0))
            struct[f'{key}:{wt}'] = sorted(sizes.values(), reverse=True)
            print(f'  -> {wt:26s} complete {len(rr):4d} rows / {len(set(w["area"] for w in rr)):2d} areas; '
                  f'|CBE|<=10%: {len(keep):4d} / {len(sizes):2d} areas; |CBE|<=20%: {k20}; acid (alk=0): {nacid}')
    dump('t7_blind_count.json', res)
    os.makedirs(os.path.join(EXP, 'data'), exist_ok=True)
    with open(os.path.join(EXP, 'data', 'structure_counts.json'), 'w') as f:
        json.dump({'note': 'area sizes of decision-ready rows (complete inputs, |CBE| <= 10%); counts only', 'cluster_sizes': struct}, f, indent=1)
    return 0


# ----------------------------------------------------------------------------- gate

GATE_RULES = {
    # seawater (Milshteyn 2018 Table 3: Na 469, Ca 10, Mg 53, K 10, HCO3 2, SO4 28 mM, pH 8.1; Cl set by charge), 25 C, closed
    'G1_calcite_supersaturated_raw': 'SI(calcite) > 0 in the raw water',
    'G2_gypsum_saturation_cf': (3.0, 4.5),
    'G3_halite_saturation_cf': (9.5, 13.0),
    'G4_cl_conservative_to_1pct': 'Cl = CF x Cl0 within 1% at every state before halite',
    'G5_calcite_retrograde': 'SI(calcite) of raw seawater at 90 C > at 25 C',
    # Lake Magadi (Getenet 2022 Table 1, F and PO4 left out as in their second simulation), 25 C, closed. Factor 1.3 each way.
    'M1_nahcolite_onset_cf': (6.2 / 1.3, 6.2 * 1.3),
    'M2_trona_onset_cf': (9.7 / 1.3, 9.7 * 1.3),
    'M3_halite_onset_cf': (32 / 1.3, 32 * 1.3),
    'M4_amorphous_silica_saturation_cf': (3.0 / 1.3, 3.0 * 1.3),
    'M5_pH_falls_to_cf_6': 'pH at CF 6 < raw pH',
    'pass_rule': 'all of G1-G5 and at least 4 of M1-M5',
}


def onset(steps, key, si=False):
    for s in steps:
        if s['raw']:
            continue
        v = s.get(('si_' if si else 'eq_') + key)
        if v is not None and ((si and v >= -1e-3) or (not si and v > 1e-12)):
            return s['cf']
    return None


def cmd_gate():
    eng = Engine()
    out = {'rules': GATE_RULES, 'engine': dict(phreeqpython=eng.version, pitzer_dat_sha256=eng.db_sha)}
    sw = dict(pH=8.1, T=25.0, Na=469, Ca=10, Mg=53, K=10, Alk=2.0, SO4=28, Cl=546.0, Cl_charge=True)
    ms = [('Calcite', 0.0), ('Gypsum', 0.0), ('Anhydrite', 0.0), ('Halite', 0.0)]
    st, info = evaporate(eng, sw, ms, 'spring', 'closed', cf_max=20.0, n=301, extra_si=('Anhydrite',))
    g = {}
    g['G1'] = st[0]['si_Calcite'] > 0
    cg = onset(st, 'Gypsum'); ch = onset(st, 'Halite')
    g['G2'] = cg is not None and GATE_RULES['G2_gypsum_saturation_cf'][0] <= cg <= GATE_RULES['G2_gypsum_saturation_cf'][1]
    g['G3'] = ch is not None and GATE_RULES['G3_halite_saturation_cf'][0] <= ch <= GATE_RULES['G3_halite_saturation_cf'][1]
    cl0 = st[0]['Cl']
    pre = [s for s in st if not s['raw'] and (ch is None or s['cf'] < ch)]
    err = max(abs(s['Cl'] / (cl0 * s['cf']) - 1) for s in pre)
    g['G4'] = err < 0.01
    hot = dict(sw, T=90.0)
    st90, _ = evaporate(eng, hot, ms, 'spring', 'closed', cf_max=1.01, n=2)
    g['G5'] = st90[0]['si_Calcite'] > st[0]['si_Calcite']
    out['seawater'] = dict(gypsum_onset_cf=cg, halite_onset_cf=ch, cl_max_rel_err=err, si_calcite_25=st[0]['si_Calcite'],
                           si_calcite_90=st90[0]['si_Calcite'], raw_cbe=st[0]['cbe'],
                           path=[{k: s[k] for k in ('cf', 'pH', 'Ca', 'Mg', 'M')} for s in st[::30]])
    # Lake Magadi brine, Getenet 2022 Table 1 (ppm). ppm read as mg per kg solution; kg water per kg solution from the TDS.
    ppm = dict(Na=12850, K=228.5, Cl=5250, CO3=9600, HCO3=6100, SO4=100.5, SiO2=91.4, Mg=12, Ca=4.5, B=5.2, Br=23.3)
    kgw = 1 - sum(ppm.values()) / 1e6
    mm = lambda x, mw: ppm[x] / mw / kgw
    mg = dict(pH=9.8, T=25.0, Na=mm('Na', MW['Na']), K=mm('K', MW['K']), Cl=mm('Cl', MW['Cl']), SO4=mm('SO4', MW['SO4']),
              Si=mm('SiO2', MW['SiO2']), Mg=mm('Mg', MW['Mg']), Ca=mm('Ca', MW['Ca']), B=mm('B', MW['B']), Br=mm('Br', MW['Br']),
              C=(ppm['CO3'] / 60.009 + ppm['HCO3'] / 61.017) / kgw)
    mms = [(p, 0.0) for p in ('Calcite', 'Magnesite', 'Gaylussite', 'Pirssonite', 'Nahcolite', 'Trona', 'Natron', 'Thenardite',
                              'Mirabilite', 'Burkeite', 'Halite', 'Sylvite', 'Glaserite', 'SiO2(a)')]
    stm, infom = evaporate(eng, mg, mms, 'spring', 'closed', cf_max=100.0, n=401, extra_si=('Nahcolite', 'Trona'))
    on = {p: onset(stm, p) for p in ('Nahcolite', 'Trona', 'Halite', 'SiO2(a)', 'Gaylussite', 'Pirssonite', 'Calcite', 'Magnesite')}
    si_sat = onset(stm, 'SiO2(a)', si=True)
    ph6 = next((s['pH'] for s in stm if not s['raw'] and s['cf'] >= 6.0), None)
    m = {}
    inr = lambda v, k: v is not None and GATE_RULES[k][0] <= v <= GATE_RULES[k][1]
    m['M1'] = inr(on['Nahcolite'], 'M1_nahcolite_onset_cf')
    m['M2'] = inr(on['Trona'], 'M2_trona_onset_cf')
    m['M3'] = inr(on['Halite'], 'M3_halite_onset_cf')
    m['M4'] = inr(si_sat, 'M4_amorphous_silica_saturation_cf')
    m['M5'] = ph6 is not None and ph6 < stm[0]['pH']
    out['magadi'] = dict(onsets=on, silica_saturation_cf=si_sat, raw_pH=stm[0]['pH'], pH_at_cf6=ph6, raw_cbe=stm[0]['cbe'],
                         failed=infom['failed'], cf_reached=infom['cf_max'],
                         published=dict(nahcolite=6.2, trona=9.7, halite=32, silica_supersaturates=3.0, pH='9.8 falls to 9.4 by CF 6.4'))
    passed = all(g.values()) and sum(m.values()) >= 4
    out['checks'] = dict(seawater=g, magadi=m, GATE='PASS' if passed else 'FAIL')
    dump('t7_gate.json', out)
    print('Seawater: gypsum onset CF %s, halite onset CF %s, Cl max rel err %.2e, SI calcite 25 C %.2f, 90 C %.2f'
          % (cg, ch, err, st[0]['si_Calcite'], st90[0]['si_Calcite']))
    print('  checks', g)
    print('Magadi: onsets', {k: (round(v, 2) if v else v) for k, v in on.items()}, 'SiO2(a) SI=0 at CF', si_sat,
          'raw pH %.2f, pH at CF 6 %s' % (stm[0]['pH'], ph6))
    print('  checks', m)
    print('GATE', out['checks']['GATE'])
    return 0 if passed else 1


# ----------------------------------------------------------------------------- planted

def template_waters(rng):
    """Synthetic waters whose fate is set by construction (mmol/kgw). Each class is varied at random around its recipe."""
    def jit(x, f=0.25): return x * math.exp(rng.uniform(-f, f))
    T = lambda: rng.uniform(40, 92)
    cls = {}
    # pass: dilute Na-HCO3 water, Ca far below Mg, little silica. Calcite keeps Ca low; Mg reaches 1 mM by CF ~3-10 while Na+K is tens of mM.
    cls['pass'] = [dict(pH=jit(8.3, 0.03), T=T(), Na=jit(4.0), K=jit(0.3), Mg=jit(0.25), Ca=jit(0.03), Cl=jit(1.0), SO4=jit(0.3),
                        Alk=jit(3.6), Si=jit(0.05), F=0.0) for _ in range(12)]
    # fail, calcium: Ca-SO4 water, Mg/Ca ~ 0.05. Ca passes 1.9 mM long before Mg reaches 1 mM.
    cls['fail_ca'] = [dict(pH=jit(7.2, 0.03), T=T(), Na=jit(1.0), K=jit(0.1), Mg=jit(0.05), Ca=jit(1.2), Cl=jit(0.5), SO4=jit(1.3),
                           Alk=jit(0.4), Si=jit(0.5), F=0.0) for _ in range(12)]
    # fail, acid: acid-sulfate water, pH ~2.5. Outside every pH limit; Mg is tiny.
    cls['fail_acid'] = [dict(pH=jit(2.5, 0.08), T=T(), Na=jit(0.5), K=jit(0.3), Mg=jit(0.05), Ca=jit(0.1), Cl=jit(0.2), SO4=jit(2.5),
                             Alk=0.0, Si=jit(4.0), F=0.0) for _ in range(12)]
    # fail, salt: Na-Cl water with Mg/Na ~ 1e-4. Na+K passes 600 mM while Mg is still well under 1 mM.
    cls['fail_salt'] = [dict(pH=jit(8.0, 0.03), T=T(), Na=jit(40.0), K=jit(2.0), Mg=jit(0.004), Ca=jit(0.02), Cl=jit(38.0), SO4=jit(1.0),
                             Alk=jit(3.0), Si=jit(0.2), F=0.0) for _ in range(12)]
    # sepiolite-sensitive: alkaline, silica-rich, Mg-poor. Sepiolite(d) strips Mg under the base minerals; without a Mg sink Mg reaches 1 mM.
    cls['sep'] = [dict(pH=jit(9.0, 0.02), T=T(), Na=jit(6.0), K=jit(0.3), Mg=jit(0.15), Ca=jit(0.02), Cl=jit(1.5), SO4=jit(0.3),
                       Alk=jit(5.0), Si=jit(4.0), F=0.0) for _ in range(12)]
    # strict-sensitive: passes window M with Ca between 0.5 and 1.9 mM at the Mg-1 mM point, so it fails M_strict.
    cls['strict'] = [dict(pH=jit(7.6, 0.02), T=T(), Na=jit(1.5), K=jit(0.1), Mg=jit(0.35), Ca=jit(0.3), Cl=jit(1.2), SO4=jit(0.5),
                          Alk=jit(1.3), Si=jit(0.05), F=0.0) for _ in range(12)]
    return cls


def synth_world(sizes, mix, rng, only_areas=None):
    """mix: list of (class, share). Area effects on the logit scale (sd 1) shift the share of the first class per area.
    The first class's share is calibrated so its expected share over areas equals the planted value."""
    (c1, p1), rest = mix[0], mix[1:]
    shift = calib_logit(p1)
    rows = []
    for ai, n in enumerate(sizes):
        pa = 0.0 if p1 <= 0 else 1 / (1 + math.exp(-(shift + rng.gauss(0, 1.0))))
        if only_areas is not None and ai >= only_areas: pa = 0.0
        tot_rest = sum(p for _, p in rest) or 1.0
        for _ in range(n):
            if rng.random() < pa:
                c = c1
            else:
                u = rng.random() * tot_rest; c = rest[-1][0]
                for cc, p in rest:
                    if u < p: c = cc; break
                    u -= p
            rows.append((c, f'a{ai}'))
    return rows


_CAL = {}


def calib_logit(p):
    """Logit shift s with E[logistic(s + N(0,1))] = p (Gauss-Hermite-free: fine grid + bisection)."""
    if p <= 0 or p >= 1: return 0.0
    if p in _CAL: return _CAL[p]
    zs = [(-4 + 8 * i / 400) for i in range(401)]
    wz = [math.exp(-z * z / 2) for z in zs]; sw = sum(wz)
    def m(s): return sum(w / (1 + math.exp(-(s + z))) for w, z in zip(wz, zs)) / sw
    lo, hi = -15.0, 15.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if m(mid) < p: lo = mid
        else: hi = mid
    _CAL[p] = (lo + hi) / 2
    return _CAL[p]


WORLDS = [
    ('P0 none pass',                 [('pass', 0.0), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'H killed'),
    ('P1 window common (30%)',       [('pass', 0.30), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'H supported'),
    ('P2 on the bar (5%)',           [('pass', 0.05), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'kills and supports both rare (false-call rates)'),
    ('P3 rare (1%)',                 [('pass', 0.01), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'mostly H killed'),
    ('P4 below the bar (2.5%)',      [('pass', 0.025), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'kill power below the bar'),
    ('P5 above the bar (12%)',       [('pass', 0.12), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'support power above the bar'),
    ('P6 sepiolite decides (25%)',   [('sep', 0.25), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'not reported as a kill'),
    ('P7 strict closes it (30%)',    [('strict', 0.30), ('fail_ca', 0.4), ('fail_acid', 0.4), ('fail_salt', 0.2)], None, 'not reported as support'),
    ('P8 two areas only',            [('pass', 0.6), ('fail_ca', 0.5), ('fail_acid', 0.5)], 2, 'no support'),
]


def cmd_planted():
    eng = Engine(); rng = random.Random(SEED)
    cls = template_waters(rng)
    lib = {}
    print('Template waters through PHREEQC (all nine path combinations each):')
    tmpl_check = {}
    for c, ws in cls.items():
        lib[c] = [run_water(eng, w) for w in ws]
        pm = sum(r[PRIMARY]['flags']['M'] for r in lib[c] if r[PRIMARY]['flags']) / len(ws)
        ps = sum(r['strict_Ts_closed']['flags']['M_strict'] for r in lib[c] if r['strict_Ts_closed']['flags']) / len(ws)
        pg = sum(any(r[g]['flags'] and r[g]['flags']['M_lenient_pH3'] for g in GEN) for r in lib[c]) / len(ws)
        nf = sum(r[k]['failed'] for r in lib[c] for k in COMBOS)
        tmpl_check[c] = dict(primary_M=pm, strict_Mstrict=ps, generous_any_Mlenient=pg, failed_paths=nf)
        print(f'  {c:10s} pass rate: primary/M {pm:.2f}  strict/M_strict {ps:.2f}  generous-any/M_lenient_pH3 {pg:.2f}  failed paths {nf}')
    expect = {'pass': (1, 1, 1), 'fail_ca': (0, 0, 0), 'fail_acid': (0, 0, 0), 'fail_salt': (0, 0, 0), 'sep': (0, 0, 1), 'strict': (1, 0, 1)}
    tmpl_ok = all(abs(tmpl_check[c]['primary_M'] - e[0]) < 0.2 and abs(tmpl_check[c]['strict_Mstrict'] - e[1]) < 0.2
                  and abs(tmpl_check[c]['generous_any_Mlenient'] - e[2]) < 0.2 for c, e in expect.items())
    print('TEMPLATES', 'AS DESIGNED' if tmpl_ok else 'NOT AS DESIGNED')
    sc = json.load(open(os.path.join(EXP, 'data', 'structure_counts.json')))['cluster_sizes']
    structures = [s for s in ('usgs:thermal water', 'hist:thermal water source') if s in sc]
    runs, nb = 200, 400
    res = {'templates': tmpl_check, 'templates_as_designed': tmpl_ok, 'runs': runs, 'n_boot': nb, 'cells': []}
    for sname in structures:
        sizes = sc[sname]
        print(f'\n{sname}: {sum(sizes)} rows, {len(sizes)} areas')
        print(f'  {"world":30s} {"expected":44s} kill  supp  incon notrep cannot')
        for wname, mix, only, expect_txt in WORLDS:
            tally = {}
            for _ in range(runs):
                rows = synth_world(sizes, mix, rng, only)
                results = [lib[c][rng.randrange(len(lib[c]))] for c, _ in rows]
                areas = [a for _, a in rows]
                o = analyse_fast(results, areas, nb, rng)
                tally[o] = tally.get(o, 0) + 1
            g = lambda k: tally.get(k, 0) / runs
            cell = dict(structure=sname, world=wname, expected=expect_txt, killed=g('H killed'), supported=g('H supported'),
                        inconclusive=g('inconclusive'), not_reported=g('not reported as a kill') + g('not reported as support'),
                        cannot=g('cannot decide by design'))
            res['cells'].append(cell)
            print(f'  {wname:30s} {expect_txt:44s} {cell["killed"]:.3f} {cell["supported"]:.3f} {cell["inconclusive"]:.3f} {cell["not_reported"]:.3f}  {cell["cannot"]:.3f}')
    dump('t7_planted.json', res)
    return 0


def analyse_fast(results, areas, nb, rng):
    """Mixed-arm verdict only (the planted check); same rule code as `real`."""
    bw, sw, kw = ARMS['mixed']
    fl = lambda c, wn: [int(bool(r[c]['flags'] and r[c]['flags'][wn])) for r in results]
    base = share_stats(fl(PRIMARY, bw), areas, nb, rng)
    sg = share_stats(fl('strict_Ts_closed', sw), areas, nb, rng)
    kflags = [int(any(r[c]['flags'] and r[c]['flags'][kw] for c in GEN + [PRIMARY, 'base_Ts_open', 'base_25_closed', 'base_25_open'])) for r in results]
    kg = share_stats(kflags, areas, nb, rng)
    fs = max(sum(1 for r in results if r[c]['failed']) / len(results) for c in COMBOS)
    return verdict(base, sg, kg, fs)[0]


# ----------------------------------------------------------------------------- real (sealed) and dryrun

def seal_status():
    me = sha256(os.path.abspath(__file__))
    pr = os.path.join(REPO, PREREG_REL)
    pr_sha = sha256(pr) if os.path.exists(pr) else None
    hp = os.path.join(REPO, 'docs', 'prereg', 'HASHES.txt')
    s_named = s_hashed = p_named = p_hashed = False
    if os.path.exists(hp):
        for line in open(hp, encoding='utf-8'):
            parts = line.split()
            if len(parts) < 2: continue
            if parts[1] == SELF:
                s_named = True; s_hashed |= parts[0] == me
            if parts[1] == PREREG_REL:
                p_named = True; p_hashed |= parts[0] == pr_sha
    return dict(script_sha256=me, prereg_sha256=pr_sha, script_line=s_named, script_hash_matches=s_hashed,
                prereg_line=p_named, prereg_hash_matches=p_hashed, real_allowed=s_hashed and p_hashed)


def decision_rows(eng, key):
    rows, _ = load_usgs(F[key], key)
    typ = 'thermal water' if key == 'usgs' else 'thermal water source'
    rows = [w for w in rows if w['type'] == typ]
    keep, _ = cbe_filter(eng, rows)
    return keep


def cmd_real(dry=False, lim=(None, 200)):
    st = seal_status()
    if not dry and not st['real_allowed']:
        print('REFUSED: T7 is not sealed. docs/prereg/HASHES.txt needs a line naming %s with sha256 %s and a line naming %s with sha256 %s.'
              % (SELF, st['script_sha256'], PREREG_REL, st['prereg_sha256']))
        return 2
    for k in F:
        got = sha256(os.path.join(REPO, F[k]))
        if got != SHA[k]:
            print('input hash mismatch for', F[k], got); return 3
    eng = Engine(); rng = random.Random(SEED + (4 if dry else 3))
    if eng.db_sha != PITZER_SHA:
        print('pitzer.dat hash mismatch', eng.db_sha); return 3
    out = {'mode': 'dryrun_permuted_inputs' if dry else 'real', 'seal': st,
           'engine': dict(phreeqpython=eng.version, pitzer_dat_sha256=eng.db_sha), 'cfg': CFG, 'sets': {}}
    for key, limit in (('usgs', lim[0] if dry else None), ('hist', lim[1] if dry else None)):
        rows = decision_rows(eng, key)
        if dry:
            # permute every solute column (and pH, T) independently across rows; areas stay with their row positions
            for k in SOLUTES:
                col = [w[k] for w in rows]; rng.shuffle(col)
                for w, v in zip(rows, col): w[k] = v
            if limit: rows = rows[:limit]
        results = []
        for i, w in enumerate(rows):
            results.append(run_water(eng, w))
            if (i + 1) % 100 == 0: print(f'  {key}: {i + 1}/{len(rows)} waters', flush=True)
        areas = [w['area'] for w in rows]
        a = analyse(results, areas, CFG['n_boot_real'] if not dry else 2000, rng)
        a['rows'] = len(rows); a['areas'] = len(set(areas))
        # reported only (added at the seal): primary-path share among rows with raw pH >= 4.5; own rng so other draws are unchanged
        nn = [i for i, w in enumerate(rows) if w['pH'] is not None and w['pH'] >= 4.5]
        rng_nn = random.Random(SEED + 7)
        a['reported_only_pH_ge_4p5'] = {arm: share_stats(
            [int(bool(results[i][PRIMARY]['flags'] and results[i][PRIMARY]['flags'][ARMS[arm][0]])) for i in nn],
            [areas[i] for i in nn], 2000, rng_nn) for arm in ARMS} if nn else None
        out['sets'][key] = a
        for arm in ARMS:
            b = a[arm]['base']
            print(f'{key} {arm:5s}: {a[arm]["verdict"]:28s} {a[arm]["label"]:30s} S {b["S"]:.4f} [{b["lo"]:.4f}, {b["hi"]:.4f}] '
                  f'passing rows {b["k"]}/{b["n"]} in {b["areas_pass"]}/{b["areas"]} areas')
        print(f'{key} attribution (primary path, first state with Mg >= 1 mM):', a['attribution_primary'])
        print(f'{key} failed path share by combo:', {k: round(v, 3) for k, v in a['failed_share_by_combo'].items()})
    if dry:
        dump('t7_dryrun_permuted.json', out)
    else:
        os.makedirs(os.path.join(EXP, 'results'), exist_ok=True)
        with open(os.path.join(EXP, 'results', 't7_real.json'), 'w') as f:
            json.dump(out, f, indent=1)
    return 0


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'sealcheck': print(json.dumps(seal_status(), indent=1)); sys.exit(0)
    if mode == 'count': sys.exit(cmd_count())
    if mode == 'gate': sys.exit(cmd_gate())
    if mode == 'planted': sys.exit(cmd_planted())
    if mode == 'dryrun':
        a = [int(x) if x != 'all' else None for x in sys.argv[2:4]]
        sys.exit(cmd_real(dry=True, lim=(a[0] if a else None, a[1] if len(a) > 1 else 200)))
    if mode == 'real': sys.exit(cmd_real())
    print(__doc__); sys.exit(1)
