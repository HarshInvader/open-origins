#!/usr/bin/env python3
"""T3: RNA persistence budget per origin setting.  Prereg: docs/prereg/t3_rna_persistence.md

Modes
  gate     lab conditions printed in opened papers only. Reads no field file.
  planted  synthetic worlds on the real cluster structure (data/structure_counts.json:
           counts and labels only). Reads no measured field value.
  real     the sealed analysis on field rows. Refuses to run unless docs/prereg/HASHES.txt
           holds a line for the prereg and a line for this script, both matching the files on disk.

Standard library only. Single process. Run with: nice python3 -I t3_analysis.py <mode>
"""
import csv, hashlib, json, math, os, random, re, statistics, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(EXP))
PREREG_REL = 'docs/prereg/t3_rna_persistence.md'
SCRIPT_REL = 'experiments/t3_rna_persistence/scripts/t3_analysis.py'

CFG = {
    # rate law (Li & Breaker 1999 as reproduced in Wayment-Steele 2021 and Schwintek 2025)
    'k_bg': 1.30e-9, 'pH_slope': 0.983, 'salt_slope': 0.24, 'salt_ref': 3.16, 'T_slope': 0.07, 'T_ref': 23.0,
    'mg_pref': 69.3, 'mg_exp': 0.80, 'k_pref': 3.57, 'k_exp': -0.419,
    # D4 monovalent rules
    'salt_floor_b': 0.14, 'salt_min_a': 1e-4,
    # D6 confirmed range (decision tier A). Mg 5-10 mM is the only fitted range confirmed from an opened source.
    'T_range': (5.0, 45.0), 'pH_range': (6.0, 9.5), 'Mg_range': (0.005, 0.010),
    # D7 reported-only tier: pH floor (no acid term in the law) and ceiling (pKa 13.7; kept well below)
    'pH_report_range': (5.0, 11.0),
    # D12 thresholds
    'L_fail': 45, 'L_pass': 90, 'bar_zero': 0.0, 'bar_benign': 0.3, 'bar_hostile': 1.0,
    'k1_fail_share': 0.95, 'k1_pass_share': 0.25, 'mg_strict_floor': 0.001,
    'min_rows': 30, 'min_clusters': 5,
    # D13 copying systems, k_ext per hour
    'systems': {'S1_nonenzymatic_helper': 27.0, 'S2_nonenzymatic_monomer': 3.7, 'S3_ribozyme_24-3': 72.0},
    'deciding_system': 'S3_ribozyme_24-3',
    # guards
    'pH_shift': 0.5, 'law_rel': 0.15, 'mix_fractions': (0.1, 0.5, 0.9),
    # D14
    'seed': 20261125, 'n_boot_real': 10000, 'n_boot_planted': 200, 'n_planted_runs': 200,
    # gate: declared exception (disclosed before sealing; see prereg "Gates")
    'declared_gate_exceptions': ['wayment_steele_table1_row5_ivt_14mM_Mg'],
}

# ----------------------------------------------------------------------------- rate law

def log10_F(Mg, M, c=CFG, mg_exp=None):
    """Mg term. D5: never below 1 (Mg does not slow cleavage of unstructured RNA)."""
    if Mg <= 0:
        return 0.0
    e = c['mg_exp'] if mg_exp is None else mg_exp
    v = math.log10(c['mg_pref']) + e * math.log10(Mg) + math.log10(c['k_pref']) + c['k_exp'] * math.log10(M)
    return max(0.0, v)


def log10_k(T, pH, Mg, M, c=CFG, literal=False):
    """log10 of the per-linkage cleavage rate constant in 1/min. literal=True drops the D5 floor."""
    base = math.log10(c['k_bg']) + c['pH_slope'] * (pH - 6) - c['salt_slope'] * (c['salt_ref'] - M) + c['T_slope'] * (T - c['T_ref'])
    if Mg <= 0:
        return base
    if literal:
        return base + math.log10(c['mg_pref']) + c['mg_exp'] * math.log10(Mg) + math.log10(c['k_pref']) + c['k_exp'] * math.log10(M)
    return base + log10_F(Mg, M, c)


def L_star(k_ext_per_h, log10k_per_min):
    return math.sqrt(math.log(2) * k_ext_per_h / (2 * 10 ** log10k_per_min * 60))


def salt(M, rule, c=CFG):
    return max(M, c['salt_floor_b']) if rule == 'b' else max(M, c['salt_min_a'])


def contrast_parts(row, ctrl, rule='a', c=CFG, pH_slope=None, mg_exp=None):
    """(c_pH, c_salt, c_Mg): log10 rate ratio, sample chemistry over control chemistry, same T."""
    s = c['pH_slope'] if pH_slope is None else pH_slope
    M, Mc = salt(row['M'], rule), salt(ctrl['M'], rule)
    return (s * (row['pH'] - ctrl['pH']), c['salt_slope'] * (M - Mc),
            log10_F(row['Mg'], M, c, mg_exp) - log10_F(ctrl['Mg'], Mc, c, mg_exp))

# ----------------------------------------------------------------------------- statistics

def in_range(row, c=CFG):
    return (c['T_range'][0] <= row['T'] <= c['T_range'][1] and c['pH_range'][0] <= row['pH'] <= c['pH_range'][1]
            and c['Mg_range'][0] <= row['Mg'] <= c['Mg_range'][1])


def reportable(row, c=CFG):
    return c['pH_report_range'][0] <= row['pH'] <= c['pH_report_range'][1]


def make_draws(clusters, n_boot, rng):
    """Cluster bootstrap: each draw is a list of row indices."""
    groups = {}
    for i, g in enumerate(clusters):
        groups.setdefault(g, []).append(i)
    keys = sorted(groups)
    draws = []
    for _ in range(n_boot):
        idx = []
        for _ in keys:
            idx.extend(groups[keys[int(rng.random() * len(keys))]])
        draws.append(idx)
    return draws, len(keys)


def med_ci(values, draws):
    if not values:
        return None
    meds = sorted(statistics.median([values[i] for i in d]) for d in draws)
    n = len(meds)
    return (statistics.median(values), meds[int(0.025 * (n - 1))], meds[int(math.ceil(0.975 * (n - 1)))])


def call(ci, claim, shift=0.0, c=CFG):
    """Verdict on a named claim from a (median, lo, hi) interval."""
    lo, hi = ci[1] + shift, ci[2] + shift
    if claim == 'hostile':
        if hi < c['bar_zero']: return 'kill'
        if lo > c['bar_hostile']: return 'support'
    else:  # benign
        if lo > c['bar_hostile']: return 'kill'
        if hi < c['bar_benign']: return 'support'
    return 'inconclusive'


def analyse(rows, ctrl, claim, n_boot, rng, em_rows=None, sw=None, c=CFG):
    """K3 (chemistry contrast) with guards, plus K1/K2 budget labels. Same code for planted and real."""
    out = {'n_rows': len(rows), 'claim': claim}
    ctrl_ok = c['Mg_range'][0] <= ctrl['Mg'] <= c['Mg_range'][1] and c['pH_range'][0] <= ctrl['pH'] <= c['pH_range'][1]
    A = [r for r in rows if in_range(r)]
    B = [r for r in rows if reportable(r)]
    out['n_in_range'] = len(A); out['n_reportable'] = len(B); out['control_in_range'] = ctrl_ok

    def vec(rs, **kw):
        return [sum(contrast_parts(r, ctrl, **kw)) for r in rs]

    # tier B: extrapolated, reported only
    if B:
        dB, kB = make_draws([r['cluster'] for r in B], n_boot, rng)
        out['extrapolated'] = {'clusters': kB, 'C': med_ci(vec(B), dB),
                               'C_pH': med_ci([contrast_parts(r, ctrl)[0] for r in B], dB),
                               'C_salt': med_ci([contrast_parts(r, ctrl)[1] for r in B], dB),
                               'C_Mg': med_ci([contrast_parts(r, ctrl)[2] for r in B], dB)}
    # tier A: decision
    nclA = len(set(r['cluster'] for r in A))
    out['clusters_in_range'] = nclA
    if not ctrl_ok or len(A) < c['min_rows'] or nclA < c['min_clusters']:
        out['verdict'] = 'cannot decide by design'
        out['why'] = ('control outside confirmed range' if not ctrl_ok else
                      f'{len(A)} in-range rows in {nclA} clusters (need {c["min_rows"]} and {c["min_clusters"]})')
    else:
        dA, _ = make_draws([r['cluster'] for r in A], n_boot, rng)
        base = med_ci(vec(A), dA)
        out['C'] = base
        v = call(base, claim)
        out['base_call'] = v
        flags = []
        if v != 'inconclusive':
            variants = {'salt_rule_b': med_ci(vec(A, rule='b'), dA),
                        'pH_slope_lo': med_ci(vec(A, pH_slope=c['pH_slope'] * (1 - c['law_rel'])), dA),
                        'pH_slope_hi': med_ci(vec(A, pH_slope=c['pH_slope'] * (1 + c['law_rel'])), dA),
                        'mg_exp_lo': med_ci(vec(A, mg_exp=c['mg_exp'] * (1 - c['law_rel'])), dA),
                        'mg_exp_hi': med_ci(vec(A, mg_exp=c['mg_exp'] * (1 + c['law_rel'])), dA)}
            out['variants'] = variants
            for name, ci in variants.items():
                if call(ci, claim) != v: flags.append('fragile:' + name)
            for sgn in (-1, 1):
                if call(base, claim, shift=sgn * c['pH_shift'] * c['pH_slope']) != v:
                    flags.append('pH-convention:%+.1f' % (sgn * c['pH_shift']))
            noMg = med_ci([sum(contrast_parts(r, ctrl)[:2]) for r in A], dA)
            out['C_without_Mg'] = noMg
            if call(noMg, claim) != v: flags.append('Mg-driven')
        out['flags'] = flags
        out['verdict'] = v if not flags else 'not reported as a %s (%s)' % (v, '; '.join(flags))
    # definition guard: end-member rows and the mixing line (extrapolated basis; never a verdict by itself)
    if em_rows and sw:
        em = {}
        versions = {'EM_rows': em_rows}
        for f in c['mix_fractions']:
            versions['mix_sw%.1f' % f] = [dict(r, pH=f * sw['pH'] + (1 - f) * r['pH'], Mg=f * sw['Mg'] + (1 - f) * r['Mg'],
                                               M=f * sw['M'] + (1 - f) * r['M']) for r in em_rows]
        for name, rs in versions.items():
            rs = [r for r in rs if reportable(r)]
            if len(rs) >= c['min_rows'] and len(set(r['cluster'] for r in rs)) >= c['min_clusters']:
                d, _ = make_draws([r['cluster'] for r in rs], n_boot, rng)
                ci = med_ci(vec(rs), d)
                em[name] = {'C': ci, 'call': call(ci, claim)}
        out['definition_versions'] = em
        calls = set(x['call'] for x in em.values()) - {'inconclusive'}
        hf = out.get('base_call', 'inconclusive')
        if (calls and hf == 'inconclusive') or (hf != 'inconclusive' and calls - {hf}):
            out['definition_flag'] = 'definition-driven: measured rows say %s, end-member or mixing-line versions say %s' % (hf, sorted(calls))
            if hf != 'inconclusive' and not out['verdict'].startswith('not reported'):
                out['verdict'] = 'not reported as a %s (definition-driven)' % hf
    # K1 / K2 budget (in-range rows only; reported with a label, decides nothing alone)
    kext = c['systems'][c['deciding_system']]
    if A:
        def share_fail(rs_logk):
            return sum(1 for lk in rs_logk if L_star(kext, lk) < c['L_fail']) / len(rs_logk)
        own = [log10_k(r['T'], r['pH'], r['Mg'], salt(r['M'], 'a')) for r in A]
        t_neutral = [log10_k(c['T_ref'], r['pH'], r['Mg'], salt(r['M'], 'a')) for r in A]
        chem_neutral = [log10_k(r['T'], ctrl['pH'], ctrl['Mg'], salt(ctrl['M'], 'a')) for r in A]
        strict = [log10_k(r['T'], r['pH'], max(r['Mg'], c['mg_strict_floor']), salt(r['M'], 'a')) for r in A]
        k1 = {'share_fail': share_fail(own), 'share_fail_T_neutral': share_fail(t_neutral),
              'share_fail_chem_neutral': share_fail(chem_neutral),
              'share_pass_strict': sum(1 for lk in strict if L_star(kext, lk) >= c['L_pass']) / len(strict)}
        fails = k1['share_fail'] >= c['k1_fail_share']
        k1['label'] = ('passes' if k1['share_pass_strict'] >= c['k1_pass_share'] else 'neither') if not fails else (
            'chemistry' if k1['share_fail_T_neutral'] >= c['k1_fail_share'] else
            'temperature only' if k1['share_fail_chem_neutral'] >= c['k1_fail_share'] else 'temperature and chemistry together')
        out['K1'] = k1
    # extrapolated budget label for all reportable rows (shows what a naive budget would have said)
    if B:
        own = [log10_k(r['T'], r['pH'], r['Mg'], salt(r['M'], 'a')) for r in B]
        tn = [log10_k(c['T_ref'], r['pH'], r['Mg'], salt(r['M'], 'a')) for r in B]
        cn = [log10_k(r['T'], ctrl['pH'], ctrl['Mg'], salt(ctrl['M'], 'a')) for r in B]
        sf = lambda v: sum(1 for lk in v if L_star(kext, lk) < c['L_fail']) / len(v)
        e = {'share_fail': sf(own), 'share_fail_T_neutral': sf(tn), 'share_fail_chem_neutral': sf(cn)}
        e['label'] = 'does not fail' if e['share_fail'] < c['k1_fail_share'] else (
            'chemistry' if e['share_fail_T_neutral'] >= c['k1_fail_share'] else
            'temperature only' if e['share_fail_chem_neutral'] >= c['k1_fail_share'] else 'temperature and chemistry together')
        out['K1_extrapolated'] = e
    return out

# ----------------------------------------------------------------------------- gate

def cmd_gate():
    ok = True
    def line(name, passed, text):
        nonlocal ok
        ok = ok and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {text}")

    print('G1 Wayment-Steele 2021 Table 1 (0.14 M K+, k_deg = L x 0.4 x k_bond; literal law, as the paper uses it)')
    rows = [('cold chain', 5, 7.4, 0.0, 4000, 5.1), ('cold chain SAM', 5, 7.4, 0.0, 12000, 15.3), ('pKa shifted', 5, 9.4, 0.0, 4000, 470),
            ('temperature excursion', 37, 7.4, 0.0, 4000, 890), ('in vitro transcription', 37, 7.6, 0.014, 4000, 57000),
            ('physiological', 37, 7.4, 0.001, 4000, 2000)]
    for i, (lab, T, pH, Mg, L, printed) in enumerate(rows):
        k = L * 0.4 * 10 ** log10_k(T, pH, Mg, 0.14, literal=True) / 1e-7
        rel = k / printed - 1
        if i == 4:
            declared = 'wayment_steele_table1_row5_ivt_14mM_Mg' in CFG['declared_gate_exceptions']
            line(lab, declared and abs(rel + 0.545) < 0.01, f'ours {k:.0f} printed {printed} rel {rel:+.3f}  DECLARED EXCEPTION (unexplained; tolerated only because declared before sealing)')
        else:
            line(lab, abs(rel) < 0.02, f'ours {k:.1f} printed {printed} rel {rel:+.3f}')

    print('G2 Schwintek 2025 Appendix 8 (24-mer, 45 C, pH 7). K+ is not printed in the paper; 1 mM is back-calculated.')
    for Mg, printed in ((200e-6, 8.91703e-6), (1e-3, 3.231e-5)):
        k = 24 * 10 ** log10_k(45, 7, Mg, 0.001, literal=True)
        line(f'Mg {Mg*1e3:g} mM', abs(k / printed - 1) < 0.01, f'ours {k:.4e} printed {printed:.4e}')

    print('G3 Breaker et al. 2003 (PMC1370461): "~10^-8 min^-1 ... (pH 7.0, 250 mM K+, 5 mM Mg2+, 23 C)"')
    k = 10 ** log10_k(23, 7, 0.005, 0.25)
    line('order of magnitude', 1 / 3 < k / 1e-8 < 3, f'ours {k:.2e} per min')

    print('G4 Cohen 2024 quoting Li & Breaker: "~1% RNA degradation after 72 hours in 1 M K+ and 5 mM Mg2+ at pH 9.5" (T not given; 23 C assumed)')
    loss = 1 - math.exp(-10 ** log10_k(23, 9.5, 0.005, 1.0) * 72 * 60)
    line('within a factor of 3', 1 / 3 < loss / 0.01 < 3, f'ours {100*loss:.2f}% per linkage')

    print('G5 known answer, soda lake (Cohen 2024: pH 10, ~1 mM Mg, ~1 M Na+, room temperature; no primer hydrolysis seen at 72 h, partial at 6 days)')
    lk = log10_k(23, 10, 0.001, 1.0)
    l72 = 1 - math.exp(-10 ** lk * 72 * 60); l144 = 1 - math.exp(-10 ** lk * 144 * 60)
    line('per-linkage loss at 72 h below 10%', l72 < 0.10, f'{100*l72:.2f}% at 72 h, {100*l144:.2f}% at 6 days, per linkage (primer length not read from the paper; the primer is in a duplex)')

    print('G6 known answer, ice (Gianni 2026: QT45 half-life ~117 days at -7 C, pH 9, 50 mM MgCl2; no pass bar)')
    for M in (0.05, 0.14):
        hl = math.log(2) / (44 * 10 ** log10_k(-7, 9, 0.05, M)) / 60 / 24
        print(f'  [INFO] 44 linkages, monovalent {M} M: predicted half-life {hl:.1f} days; measured/predicted = {117/hl:.1f}')

    print('G7 positive controls: the buffers where copying was shown must pass the budget')
    for name, kext, T, pH, Mg, M in (('S1 Walton 2019 buffer (pH 8, 100 mM Mg, 250 mM Na, 23 C)', 27.0, 23, 8.0, 0.1, 0.25),
                                    ('S3 Horning & Joyce 2016 buffer (pH 8.3, 200 mM Mg, 17 C; monovalent floored at 0.14 M)', 72.0, 17, 8.3, 0.2, 0.14),
                                    ('lake-water chemistry with S1 (pH 10, 1 mM Mg, 1 M Na, 23 C)', 27.0, 23, 10.0, 0.001, 1.0)):
        L = L_star(kext, log10_k(T, pH, Mg, M))
        line(name, L >= CFG['L_fail'], f'L* = {L:.0f} nt')
    print('GATE', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1

# ----------------------------------------------------------------------------- planted

WORLDS = {
    # name: (dT, dpH, Mg factor, EM dpH, hot)  -> see prereg table
    'P0_null':              dict(dpH=0.0, mgf=1.0),
    'P1_hot_only':          dict(dpH=0.0, mgf=1.0, T=(85.0, 125.0)),
    'P1b_warm_in_range':    dict(dpH=0.0, mgf=1.0, T=(35.0, 45.0)),
    'P2_hostile':           dict(dpH=+1.6, mgf=1.0),
    'P3_mild_hostile':      dict(dpH=+0.5, mgf=1.0),
    'P4_protective':        dict(dpH=-1.1, mgf=1.0, em=dict(dpH=-1.1)),
    'P5_Mg_dilution_only':  dict(dpH=0.0, mgf=0.75, em=dict(dpH=-1.1)),
    'P6_EM_only_effect':    dict(dpH=0.0, mgf=1.0, em=dict(dpH=-1.1)),
}
CTRL_SYN = {'pH': 7.5, 'Mg': 0.0075, 'M': 0.5}   # synthetic control, inside the confirmed range. Not seawater.


def synth_rows(sizes, w, rng, em=False):
    rows = []
    T_lo, T_hi = w.get('T', (5.0, 45.0))
    dpH = w['em']['dpH'] if em else w['dpH']
    for g, n in enumerate(sizes):
        cl_pH = rng.gauss(0, 0.15); cl_mg = rng.gauss(0, 0.05); cl_T = rng.uniform(T_lo, T_hi)
        for _ in range(n):
            T = min(T_hi, max(T_lo, cl_T + rng.gauss(0, 5)))
            if w.get('T') is None: T = min(45.0, max(5.0, T))
            Mg = 0.0 if em else CTRL_SYN['Mg'] * w['mgf'] * math.exp(cl_mg + rng.gauss(0, 0.05))
            rows.append({'T': T, 'pH': CTRL_SYN['pH'] + dpH + cl_pH + rng.gauss(0, 0.15), 'Mg': Mg,
                         'M': CTRL_SYN['M'] * math.exp(rng.gauss(0, 0.2)), 'cluster': g})
    return rows


def cmd_planted():
    sc = json.load(open(os.path.join(EXP, 'data', 'structure_counts.json')))
    m = sc['marhys4']['complete_cluster_sizes']; u = sc['usgs_ynp_v2']['complete_cluster_sizes']
    rng = random.Random(CFG['seed'])
    thin = lambda sizes, p: [k for k in (sum(1 for _ in range(n) if rng.random() < p) for n in sizes) if k > 0]
    shapes = {'vent_basalt_ridge (29 clusters, 640 rows)': (m['HF|V1_basalt_ridge'], m['EM|V1_basalt_ridge']),
              'vent_ultramafic (5 clusters, 147 rows)': (m['HF|V2_ultramafic'], m['EM|V2_ultramafic']),
              'hot_springs (39 clusters, 605 rows)': (u['thermal water'], None),
              'vent_basalt_ridge thinned to 10% in range': (thin(m['HF|V1_basalt_ridge'], 0.10), m['EM|V1_basalt_ridge'])}
    runs, nb = CFG['n_planted_runs'], CFG['n_boot_planted']
    res = {}
    print(f'planted: {runs} runs per cell, {nb} bootstrap draws, seed {CFG["seed"]}; claim "hostile"; synthetic control {CTRL_SYN}')
    for sname, (hf_sizes, em_sizes) in shapes.items():
        print(f'\n{sname}: rows {sum(hf_sizes)} clusters {len(hf_sizes)}')
        print(f'  {"world":22s} {"kill":>6s} {"support":>8s} {"inconcl":>8s} {"not-rep":>8s} {"cannot":>7s} {"def-flag":>9s}  K1-extrap label (mode)   median C')
        for wname, w in WORLDS.items():
            tally = {'kill': 0, 'support': 0, 'inconclusive': 0, 'not reported': 0, 'cannot': 0}
            dflag = 0; labels = {}; Cs = []
            for _ in range(runs):
                rows = synth_rows(hf_sizes, w, rng)
                em_rows = synth_rows(em_sizes, w, rng, em=True) if (em_sizes and 'em' in w) else None
                o = analyse(rows, CTRL_SYN, 'hostile', nb, rng, em_rows=em_rows, sw=CTRL_SYN)
                v = o['verdict']
                key = 'cannot' if v.startswith('cannot') else 'not reported' if v.startswith('not reported') else v
                tally[key] += 1
                dflag += 1 if 'definition_flag' in o else 0
                lab = o.get('K1_extrapolated', {}).get('label', 'none'); labels[lab] = labels.get(lab, 0) + 1
                if 'C' in o: Cs.append(o['C'][0])
            mode = max(labels, key=labels.get)
            medC = '%+.2f' % statistics.median(Cs) if Cs else '  n/a'
            print(f'  {wname:22s} {tally["kill"]/runs:6.2f} {tally["support"]/runs:8.2f} {tally["inconclusive"]/runs:8.2f} {tally["not reported"]/runs:8.2f} {tally["cannot"]/runs:7.2f} {dflag/runs:9.2f}  {mode} ({labels[mode]/runs:.2f})   {medC}')
            res[f'{sname}|{wname}'] = {**{k: v / runs for k, v in tally.items()}, 'definition_flag': dflag / runs, 'K1_extrapolated_labels': labels}
    os.makedirs(os.path.join(EXP, 'scripts_out'), exist_ok=True)
    json.dump({'cfg': {k: v for k, v in CFG.items()}, 'control': CTRL_SYN, 'worlds': WORLDS, 'results': res},
              open(os.path.join(EXP, 'scripts_out', 't3_planted.json'), 'w'), indent=1)
    return 0

# ----------------------------------------------------------------------------- real

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def seal_ok():
    hp = os.path.join(REPO, 'docs', 'prereg', 'HASHES.txt')
    if not os.path.exists(hp):
        return False, 'docs/prereg/HASHES.txt not found'
    sealed = {}
    for ln in open(hp, encoding='utf-8'):
        parts = ln.split()
        if len(parts) >= 2: sealed[parts[1]] = parts[0]      # the last line for a path wins
    for rel in (PREREG_REL, SCRIPT_REL):
        if rel not in sealed: return False, f'no HASHES.txt line for {rel}'
        if sealed[rel] != sha256(os.path.join(REPO, rel)): return False, f'{rel} differs from its sealed hash'
    return True, 'sealed'


def vent_class(geol, rock1, area):
    if area in ('Lost City Hydrothermal Field', 'Old City Hydrothermal Field'): return 'V2a_alkaline_serpentinite'
    if rock1 == 'Peridotite': return 'V2b_ultramafic_other'
    if rock1 == 'Sediment': return 'V4_sediment'
    if geol == 'Mid-oceanic spreading center' and rock1 == 'Basalt': return 'V1_basalt_ridge'
    if geol in ('Back-arc spreading center', 'Volcanic arc'): return 'V3_arc_backarc'
    return 'V5_other'


def load_marhys():
    z = zipfile.ZipFile(os.path.join(EXP, 'raw', 'marhys4', 'MARHYS_DB_4_0.xlsx'))
    S = [re.sub(r'<[^>]+>', '', m) for m in re.findall(r'<si>(.*?)</si>', z.read('xl/sharedStrings.xml').decode('utf-8', 'replace'), flags=re.S)]
    xml = z.read('xl/worksheets/sheet1.xml').decode('utf-8', 'replace')
    LAB = {'Z': 'type', 'K': 'geol', 'G': 'rock1', 'E': 'area', 'C': 'vent'}
    NUM = {'AG': 'T', 'AK': 'pH', 'BM': 'Mg', 'BK': 'K', 'BR': 'Na'}     # D2, D3: the merged T and pH columns
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
        cls = 'SW' if t == 'SW' else vent_class(lab.get('geol', ''), lab.get('rock1', ''), lab.get('area', ''))
        need = ('pH', 'Mg', 'K', 'Na') if t == 'SW' else ('T', 'pH', 'Mg', 'K', 'Na')
        key = f'{t}|{cls}'
        if not all(k in num for k in need):
            dropped[key] = dropped.get(key, 0) + 1; continue
        cluster = lab.get('vent', '') if cls == 'V2a_alkaline_serpentinite' else lab.get('area', '')   # D10
        out.setdefault(key, []).append({'T': num.get('T', float('nan')), 'pH': num['pH'], 'Mg': num['Mg'] / 1000.0,   # D8 mmol/kg -> mol/L
                                        'M': (num['Na'] + num['K']) / 1000.0, 'cluster': cluster})
    return out, dropped


def _num(s):
    s = s.strip()
    if s in ('', '--', 'NA', 'na', 'nd'): return None
    try:
        return float(s[1:]) / 2 if s.startswith('<') else float(s)      # D9
    except ValueError:
        return None


def load_usgs():
    out = {}; dropped = {}
    with open(os.path.join(EXP, 'raw', 'usgs_ynp_p92xkju7', 'YNP_WQ.csv'), newline='', encoding='utf-8', errors='replace') as f:
        for r in csv.DictReader(f):
            wt = r['WaterType'].strip()
            pH = _num(r['pH_Field_StandardUnits']); pH = _num(r['pH_Lab_StandardUnits']) if pH is None else pH
            T = _num(r['WaterTemperature_DegreesCelsius'])
            Mg = _num(r['Magnesium_Dissolved_MilligramsPerLiter_Mg']); Na = _num(r['Sodium_Dissolved_MilligramsPerLiter_Na']); K = _num(r['Potassium_Dissolved_MilligramsPerLiter_K'])
            if None in (pH, T, Mg, Na, K):
                dropped[wt] = dropped.get(wt, 0) + 1; continue
            out.setdefault(wt, []).append({'T': T, 'pH': pH, 'Mg': Mg / 24.305 / 1000, 'M': (Na / 22.990 + K / 39.098) / 1000, 'cluster': r['Area'].strip()})
    return out, dropped


def median_chem(rows):
    return {k: statistics.median(r[k] for r in rows) for k in ('pH', 'Mg', 'M')}


def cmd_real(loadcheck=False):
    m, md = load_marhys(); u, ud = load_usgs()
    if loadcheck:   # counts only; prints no measured value
        for name, d, dr in (('marhys4', m, md), ('usgs_ynp_v2', u, ud)):
            for k in sorted(set(d) | set(dr)):
                print(f'{name:12s} {k:32s} loaded {len(d.get(k, [])):5d} clusters {len(set(r["cluster"] for r in d.get(k, []))):3d} dropped {dr.get(k, 0)}')
        return 0
    ok, why = seal_ok()
    if not ok:
        print('REFUSED: T3 is not sealed (%s). Seal the prereg and this script in docs/prereg/HASHES.txt first.' % why)
        return 2
    rng = random.Random(CFG['seed']); nb = CFG['n_boot_real']
    sw = median_chem(m['SW|SW']); stream = median_chem(u['river, stream, or creek'])
    res = {'controls': {'seawater_n': len(m['SW|SW']), 'stream_n': len(u['river, stream, or creek'])}, 'dropped': {'marhys4': md, 'usgs': ud}, 'settings': {}}
    # negative control (prereg gate 5): control waters under the budget at their own temperature
    kext = CFG['systems'][CFG['deciding_system']]
    st = u['river, stream, or creek']
    res['negative_control_stream_share_fail'] = sum(1 for r in st if L_star(kext, log10_k(r['T'], r['pH'], r['Mg'], salt(r['M'], 'a'))) < CFG['L_fail']) / len(st)
    for cls in ('V1_basalt_ridge', 'V2a_alkaline_serpentinite', 'V2b_ultramafic_other', 'V3_arc_backarc', 'V4_sediment', 'V5_other'):
        rows = m.get('HF|' + cls, [])
        if rows:
            res['settings']['vent:' + cls + ' vs seawater'] = analyse(rows, sw, 'hostile', nb, rng, em_rows=m.get('EM|' + cls), sw=sw)
            res['settings']['vent:' + cls + ' vs stream water'] = analyse(rows, stream, 'hostile', nb, rng, em_rows=m.get('EM|' + cls), sw=sw)
    for wt, claim in (('thermal water', 'hostile'), ('lake', 'benign')):
        if u.get(wt):
            res['settings'][f'usgs:{wt} vs stream water'] = analyse(u[wt], stream, claim, nb, rng)
            res['settings'][f'usgs:{wt} vs seawater'] = analyse(u[wt], sw, claim, nb, rng)
    os.makedirs(os.path.join(EXP, 'scripts_out'), exist_ok=True)
    json.dump(res, open(os.path.join(EXP, 'scripts_out', 't3_real.json'), 'w'), indent=1)
    for k, v in res['settings'].items():
        print(f'{k:48s} {v["verdict"]}')
    return 0


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode == 'gate': sys.exit(cmd_gate())
    if mode == 'planted': sys.exit(cmd_planted())
    if mode == 'real': sys.exit(cmd_real())
    if mode == 'loadcheck': sys.exit(cmd_real(loadcheck=True))
    print(__doc__); sys.exit(1)
