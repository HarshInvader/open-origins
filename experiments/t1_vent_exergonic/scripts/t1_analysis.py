"""T1: is the exergonic tendency of LUCA's biosynthetic core (Wimmer et al. 2021) specific
to the synthesis direction, to the core, and to vent conditions?

Modes
  selftest  eQuilibrator mechanics on R00086 (ATP + H2O -> ADP + Pi) only; this one value
            was already seen in the install check. No core or null reaction is touched.
  planted   synthetic Delta G'0 only (no eQuilibrator); real covariates/clusters/strata.
            Reports verdict rates for planted scenarios. Safe to run before sealing.
  gate      reproduction gate on the core: our Delta G at pH 7, 25 C, 1 mM vs Wimmer SI
            Table 3 sheet A. Writes scripts_out/t1_gate.json. RUN ONLY AFTER SEALING.
  real      the three arms. Refuses to run unless t1_gate.json says pass. RUN ONLY AFTER
            SEALING.

Run with the experiment venv, one core, low priority:
  taskpolicy -b nice -n 20 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      VECLIB_MAXIMUM_THREADS=1 .venv/bin/python -I scripts/t1_analysis.py <mode>

Every decision the prereg lists under "Fixed decisions" (D1-D15) is fixed in CFG.
"""
import sys, os, json, re, math, hashlib, collections
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
DATA, OUT = EXP / 'data', EXP / 'scripts_out'
T3 = EXP / 'raw' / 'wimmer_supp' / 'x' / 'Table_3.XLSX'
R_KJ = 8.314462618e-3  # kJ mol-1 K-1

CFG = {
    'seed': 20261124,
    # conditions (Wimmer Methods, verbatim values)
    'ionic_strength_M': 0.25, 'p_mg': 3.0,        # FIXED D12: pMg 3 (2.52 is gate fallback 2)
    'grid_ph': list(range(1, 15)), 'grid_t_c': list(range(25, 101, 5)),
    'c_equal_M': 1e-3, 'c_reactant_M': 1e-3, 'c_product_M': 1e-5,   # 1 : 0.01 mM
    # FIXED D1: 'table1' = organic-reductant equations (Table 1/3, 402 -> 351), all arms
    'core_set': 'table1',
    # FIXED D2: chosen by the gate's D11 diagnostic cell (higher r wins; other variant is a
    # reported sensitivity run). 'T' = eQuilibrator at the grid T; '298.15' = transform at 25 C.
    'transform_temperature': 'by_gate',
    # FIXED D3: 'aqueous' = CO2 and H2 at the side concentration like any solute
    # ('gas_1bar' is a gate fallback only).
    'gas_rule': 'aqueous',
    # FIXED D4: computable = all compounds found + balanced + sigma(dG'0) < sigma_max_kJ
    'sigma_max_kJ': 100.0,
    'compound_tier': 'bundled',       # FIXED D10: bundled mini DB ('full' = later sensitivity)
    # FIXED D5: K-direction verdict uses the point estimate at mean dG'0; MC interval reported
    'dir_verdict_value': 'point_estimate',
    # FIXED D6: settings
    'vent': (9, 80), 'pond': (7, 25),
    'window_ph': (8, 10), 'window_t_min_c': 70,   # K-setting peak window: REPORTED ONLY, no rule
    # FIXED D7: null pools. Primary and second direction rule; verdicts must agree.
    'null_primary': 'rhea_uniprot', 'null_second': 's4_kgml',
    'null_exclude_o2': True,
    'null_exclude_ids': ['R00086'],   # seen in the install check
    'null_taxon_filter': None,        # FIXED D14: no taxon filter on N1 in the primary run
    'core_keep_both_R01214': True,    # FIXED D13: keep R01214_1 and R01214_2 (as Wimmer did)
    # FIXED D8: matching strata, tried in order until the stratum is non-empty
    'strata_levels': [('ec_class', 'nl', 'nr', 'ntp'), ('ec_class', 'ntp'), ('ntp',)],
    'main_cap': 3,
    # FIXED D9: cluster bootstrap unit: first KEGG module; 'added manually' -> synthesis target
    'n_boot': 1000, 'n_draws': 1000,
    'mc_in_boot': True,
    # thresholds (plan, unchanged), in percentage points
    'dir_kill_ge': 50.0, 'dir_support_le': 30.0,
    # K-specificity decision statistic: core - matched-null share at the vent cell at EQUAL
    # concentrations (every participant at c_equal_M). The gradient-cell gap is reported only.
    'spec_kill_gap_lt': 5.0, 'spec_kill_ci_upper_lt': 10.0,
    'spec_support_gap_ge': 15.0, 'spec_support_ci_lower_gt': 5.0,
    # K-setting: verdict from the gradient contrast's 95% interval only. Kill: includes 0, or
    # FIXED D15: lies wholly below 0. Support: lower bound > 0. Window fraction and the
    # equal-concentration contrast are reported only.
    'set_kill_ci_wholly_negative': True,
    # gate
    'gate_r_min': 0.98, 'gate_share_tol': 2.0,
    'gate_second_cell': None,   # no extra GATING cell
    # FIXED D2/D11: non-gating diagnostic. Sheet A, pH 7, 80 C under both transform-temperature
    # variants; the variant with the higher r is used by `real` (transform_temperature 'by_gate').
    'gate_d2_diagnostic': ('A', 7, 80),
    'pond_sensitivity': [(6, 25), (3, 70)],   # reported without a rule
    # planted
    'planted_reps': 100, 'planted_draws': 200, 'planted_boot': 200,
    'planted_sd': 25.0, 'planted_sigma': 5.0,
}


# ---------------------------------------------------------------------------- io
def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def read_tsv(p):
    lines = [l.rstrip('\n').split('\t') for l in open(p) if not l.startswith('#')]
    return [dict(zip(lines[0], r)) for r in lines[1:]]


def cluster_of(r):
    m = r['kegg_module'].split(',')[0].strip()
    return m if m.startswith('M') else 'target:' + r['synthesis_target']


def load_core():
    rows = read_tsv(DATA / 'wimmer2021_core_reactions.tsv')
    for r in rows:
        r['formula'] = re.sub(r'(C\d{5})', r'kegg:\1', r['kegg_equation']).replace('<=>', '=')
        r['cluster'] = cluster_of(r)
    return rows


def load_null(name):
    if name == 'rhea_uniprot':
        rows = read_tsv(DATA / 'rhea_null_pool.tsv')
        for r in rows:
            r['id'], r['formula'] = 'RHEA:' + r['rhea_master'], r['eq_formula']
    elif name == 'rhea_uniprot_metacyc_agree':
        rows = [r for r in load_null('rhea_uniprot') if r['directions_agree'] == '1']
    elif name == 's4_kgml':
        rows = read_tsv(DATA / 's4_null_pool.tsv')
        for r in rows:
            r['id'] = r['reaction_id']
            r['formula'] = re.sub(r'(C\d{5})', r'kegg:\1', r['kegg_equation']).replace('<=>', '=')
    else:
        raise ValueError(name)
    if CFG['null_exclude_o2']:
        rows = [r for r in rows if r['has_o2'] == '0']
    rows = [r for r in rows if r.get('id', r.get('reaction_id')) not in CFG['null_exclude_ids']]
    return rows


def stratum_keys(r):
    cap = CFG['main_cap']
    v = {'ec_class': r['ec_class'], 'nl': min(int(r['n_left_main']), cap),
         'nr': min(int(r['n_right_main']), cap), 'ntp': int(r['ntp_hydrolysis_left'])}
    return [tuple(v[k] for k in lvl) for lvl in CFG['strata_levels']]


# ---------------------------------------------------------------- thermodynamics
def rt(t_c):
    return R_KJ * (t_c + 273.15)


def dg(dg0, ar, ap, t_c, cr, cp, reverse=False):
    """Delta G = Delta G'0 + RT ln Q. ar/ap: summed stoichiometry of solutes in Q on the
    reactant/product side (H2O and H+ excluded, activity 1). reverse: the reaction read
    right-to-left with the same concentration rule (its reactants at cr)."""
    if not reverse:
        return dg0 + rt(t_c) * (ap * math.log(cp) - ar * math.log(cr))
    return -dg0 + rt(t_c) * (ar * math.log(cp) - ap * math.log(cr))


def share(x):
    return 100.0 * float(np.mean(x <= 0.0))


def conditions():
    return [(p, t) for t in CFG['grid_t_c'] for p in CFG['grid_ph']]


# ------------------------------------------------------------------- matching
class Matcher:
    def __init__(self, core_rows, null_rows):
        idx = [collections.defaultdict(list) for _ in CFG['strata_levels']]
        for j, r in enumerate(null_rows):
            for lvl, k in enumerate(stratum_keys(r)):
                idx[lvl][k].append(j)
        self.cands, self.level = [], []
        for r in core_rows:
            for lvl, k in enumerate(stratum_keys(r)):
                if idx[lvl].get(k):
                    self.cands.append(np.array(idx[lvl][k]))
                    self.level.append(lvl)
                    break
            else:
                self.cands.append(np.arange(len(null_rows)))
                self.level.append(len(CFG['strata_levels']))

        self.flat = np.concatenate(self.cands)
        self.lens = np.array([len(c) for c in self.cands])
        self.starts = np.concatenate([[0], np.cumsum(self.lens)[:-1]])

    def draw(self, rng, core_idx):
        """One matched null reaction (uniform within its stratum, with replacement) per
        core reaction in core_idx."""
        core_idx = np.asarray(core_idx)
        u = rng.integers(0, self.lens[core_idx])
        return self.flat[self.starts[core_idx] + u]

    def level_counts(self):
        return dict(collections.Counter(self.level))


def cluster_resample(rng, clusters):
    groups = collections.defaultdict(list)
    for i, c in enumerate(clusters):
        groups[c].append(i)
    keys = list(groups)
    pick = rng.integers(len(keys), size=len(keys))
    return np.array([i for k in pick for i in groups[keys[k]]])


# ------------------------------------------------------------------------ arms
def run_arms(S, rng, n_boot, n_draws):
    """S: dict with core/null arrays: dg0 [n_cond, n], U [n, k] (sqrt cov), ar, ap;
    plus clusters, matcher, conds. Returns arm statistics and verdicts."""
    conds = S['conds']
    ci = {c: i for i, c in enumerate(conds)}
    iv, ip = ci[CFG['vent']], ci[CFG['pond']]
    tv, tp = CFG['vent'][1], CFG['pond'][1]
    cr, cp = CFG['c_reactant_M'], CFG['c_product_M']
    C, N, M = S['core'], S['null'], S['matcher']
    nc = len(C['ar'])
    all_core = np.arange(nc)

    def draw_dg0(X, z):
        # U is [n, k] (sqrt of the covariance) or a 1-D vector of independent sigmas
        noise = X['U'] * z if X['U'].ndim == 1 else X['U'] @ z
        return X['dg0'] + noise[None, :]

    def zs(X):
        return rng.standard_normal(X['U'].shape[0] if X['U'].ndim == 1 else X['U'].shape[1])

    # arm 1: direction (point estimate at mean dG'0; MC interval reported)
    fwd = share(dg(C['dg0'][iv], C['ar'], C['ap'], tv, cr, cp))
    rev = share(dg(C['dg0'][iv], C['ar'], C['ap'], tv, cr, cp, reverse=True))
    rev_mc = []
    for _ in range(n_draws):
        d0 = draw_dg0(C, zs(C))
        rev_mc.append(share(dg(d0[iv], C['ar'], C['ap'], tv, cr, cp, reverse=True)))
    dn = C['ap'] - C['ar']   # descriptive: the gradient favours reactions with more product species
    by_dn = {}
    for lab, msk in (('dn<0', dn < 0), ('dn=0', dn == 0), ('dn>0', dn > 0)):
        if msk.any():
            by_dn[lab] = {'n': int(msk.sum()),
                          'forward': share(dg(C['dg0'][iv][msk], C['ar'][msk], C['ap'][msk], tv, cr, cp)),
                          'reversed': share(dg(C['dg0'][iv][msk], C['ar'][msk], C['ap'][msk], tv, cr, cp, True))}
    a1 = {'core_forward_share_vent': fwd, 'core_reversed_share_vent': rev,
          'reversed_share_mc_95': list(np.percentile(rev_mc, [2.5, 97.5])),
          'by_delta_n_descriptive': by_dn}
    a1['verdict'] = ('kill' if rev >= CFG['dir_kill_ge'] else
                     'support' if rev <= CFG['dir_support_le'] else 'inconclusive')

    # arm 2: specificity (core vs matched null, vent cell). Decision statistic at EQUAL
    # concentrations (every participant at c_equal_M); the gradient-cell gap is reported only
    # (under the gradient the null is already ~85-88% exergonic, so that gap has a ceiling).
    ce = CFG['c_equal_M']
    core_v = dg(C['dg0'][iv], C['ar'], C['ap'], tv, ce, ce)
    null_v = dg(N['dg0'][iv], N['ar'], N['ap'], tv, ce, ce)
    core_vg = dg(C['dg0'][iv], C['ar'], C['ap'], tv, cr, cp)
    null_vg = dg(N['dg0'][iv], N['ar'], N['ap'], tv, cr, cp)
    null_pt, null_ptg = [], []
    for _ in range(n_boot):
        m = M.draw(rng, all_core)
        null_pt.append(share(null_v[m])); null_ptg.append(share(null_vg[m]))
    null_pt, null_ptg = float(np.mean(null_pt)), float(np.mean(null_ptg))
    gap_pt = share(core_v) - null_pt
    gap_ptg = share(core_vg) - null_ptg
    gaps, gapsg = [], []
    for _ in range(n_boot):
        idx = cluster_resample(rng, S['clusters'])
        if CFG['mc_in_boot']:
            cd, nd = draw_dg0(C, zs(C))[iv], draw_dg0(N, zs(N))[iv]
            cv, nv = dg(cd, C['ar'], C['ap'], tv, ce, ce), dg(nd, N['ar'], N['ap'], tv, ce, ce)
            cvg, nvg = dg(cd, C['ar'], C['ap'], tv, cr, cp), dg(nd, N['ar'], N['ap'], tv, cr, cp)
        else:
            cv, nv, cvg, nvg = core_v, null_v, core_vg, null_vg
        m = M.draw(rng, idx)
        gaps.append(share(cv[idx]) - share(nv[m]))
        gapsg.append(share(cvg[idx]) - share(nvg[m]))
    lo, hi = np.percentile(gaps, [2.5, 97.5])
    a2 = {'core_share_vent_equal': share(core_v), 'matched_null_share_vent_equal': null_pt,
          'gap_points': gap_pt, 'gap_ci95': [lo, hi], 'match_levels': M.level_counts(),
          'gradient_reported_no_rule': {
              'core_share_vent_gradient': share(core_vg), 'matched_null_share_vent_gradient': null_ptg,
              'gap_points': gap_ptg, 'gap_ci95': list(np.percentile(gapsg, [2.5, 97.5]))}}
    a2['verdict'] = ('kill' if gap_pt < CFG['spec_kill_gap_lt'] and hi < CFG['spec_kill_ci_upper_lt'] else
                     'support' if gap_pt >= CFG['spec_support_gap_ge'] and lo > CFG['spec_support_ci_lower_gt']
                     else 'inconclusive')

    # arm 3: setting (vent - pond, core minus matched null) + location of the core maximum
    T_c = np.array([t for _, t in conds])
    P_h = np.array([p for p, _ in conds])
    in_win = (P_h >= CFG['window_ph'][0]) & (P_h <= CFG['window_ph'][1]) & (T_c >= CFG['window_t_min_c'])
    lnq_c = (C['ap'] * math.log(cp) - C['ar'] * math.log(cr))[None, :]
    ce = CFG['c_equal_M']
    contrasts, contrasts_eq, win = [], [], []
    for _ in range(n_draws):
        cd0, nd0 = draw_dg0(C, zs(C)), draw_dg0(N, zs(N))
        m = M.draw(rng, all_core)
        cs = lambda i, t, a=cr, b=cp: share(dg(cd0[i], C['ar'], C['ap'], t, a, b))
        ns = lambda i, t, a=cr, b=cp: share(dg(nd0[i][m], N['ar'][m], N['ap'][m], t, a, b))
        contrasts.append((cs(iv, tv) - cs(ip, tp)) - (ns(iv, tv) - ns(ip, tp)))
        contrasts_eq.append((cs(iv, tv, ce, ce) - cs(ip, tp, ce, ce)) - (ns(iv, tv, ce, ce) - ns(ip, tp, ce, ce)))
        grid = 100.0 * np.mean(cd0 + (R_KJ * (T_c + 273.15))[:, None] * lnq_c <= 0.0, axis=1)
        top = grid == grid.max()
        win.append(float(np.mean(in_win[top])))   # fractional credit for tied maxima
    lo3, hi3 = np.percentile(contrasts, [2.5, 97.5])
    wf = float(np.mean(win))
    a3 = {'contrast_points_median': float(np.median(contrasts)), 'contrast_ci95': [lo3, hi3],
          'max_in_window_fraction_reported_no_rule': wf,
          'contrast_equal_conc_reported_no_rule': {
              'median': float(np.median(contrasts_eq)),
              'ci95': list(np.percentile(contrasts_eq, [2.5, 97.5]))}}
    # verdict from the contrast only. D15: an interval wholly below 0 is a kill.
    ci_has0 = lo3 <= 0.0 <= hi3
    ci_neg = CFG['set_kill_ci_wholly_negative'] and hi3 < 0.0
    a3['verdict'] = ('kill' if ci_has0 or ci_neg else
                     'support' if lo3 > 0.0 else 'inconclusive')
    return {'direction': a1, 'specificity': a2, 'setting': a3}


def overall(v):
    kills = sum(x == 'kill' for x in v)
    if kills >= 2:
        return 'uninformative (two or more kills)'
    if all(x == 'support' for x in v):
        return 'supported'
    return 'per arm'


# -------------------------------------------------------------------- planted
def planted():
    rng = np.random.default_rng(CFG['seed'])
    core = [r for r in load_core() if r['table3_has_value'] == '1']
    null = load_null(CFG['null_primary'])
    M = Matcher(core, null)
    conds = conditions()
    k10 = math.log(10)
    ar_c = np.array([float(r['n_left']) for r in core]); ap_c = np.array([float(r['n_right']) for r in core])
    ar_n = np.array([float(r['n_left']) for r in null]); ap_n = np.array([float(r['n_right']) for r in null])
    sd, sg = CFG['planted_sd'], CFG['planted_sigma']

    def make(n, shift, h, sd):
        base = rng.normal(shift, sd, n)
        rows = []
        for p, t in conds:
            tt = t if CFG['transform_temperature'] in ('T', 'by_gate') else 25
            rows.append(base - h * rt(tt) * k10 * (p - CFG['vent'][0]))
        return np.array(rows)

    def hvec(n, kind):
        if kind == 'flat':
            return rng.choice([-1, 0, 1], n).astype(float)
        if kind == 'zero':
            return np.zeros(n)
        if kind == 'peak9':
            return rng.choice([-1, 1], n).astype(float)
        raise ValueError(kind)

    scen = {
        'S0_symmetric_null':      dict(core_shift=0.0, core_h='flat', null_h='flat'),
        'S1_core_minus15':        dict(core_shift=-15.0, core_h='flat', null_h='flat'),
        'S1b_core_minus15_sd15':  dict(core_shift=-15.0, core_h='flat', null_h='flat', sd=15.0),
        'S1c_core_minus25':       dict(core_shift=-25.0, core_h='flat', null_h='flat'),
        'S2_core_minus40':        dict(core_shift=-40.0, core_h='flat', null_h='flat'),
        'S2b_core_minus60':       dict(core_shift=-60.0, core_h='flat', null_h='flat'),
        'S3_core_peak_pH9':       dict(core_shift=0.0, core_h='peak9', null_h='zero'),
        'S4_core_minus15_peak_pH9': dict(core_shift=-15.0, core_h='peak9', null_h='zero'),
    }
    out = {'note': 'synthetic dG0 only; real covariates, clusters, strata; dG0(pH) = b - h*RT*ln10*(pH-9)',
           'n_core': len(core), 'n_null': len(null), 'sd': sd, 'sigma': sg, 'scenarios': {}}
    # sanity: symmetric dG0 at equal concentrations and no ln Q -> ~50% exergonic
    b = rng.normal(0, sd, 100000)
    out['symmetric_equal_conc_share'] = share(b)
    for name, s in scen.items():
        tallies = collections.defaultdict(collections.Counter)
        stats = collections.defaultdict(list)
        for _ in range(CFG['planted_reps']):
            S = {'conds': conds, 'matcher': M, 'clusters': [r['cluster'] for r in core],
                 'core': {'dg0': make(len(core), s['core_shift'], hvec(len(core), s['core_h']), s.get('sd', sd)),
                          'U': np.full(len(core), sg), 'ar': ar_c, 'ap': ap_c},
                 'null': {'dg0': make(len(null), 0.0, hvec(len(null), s['null_h']), s.get('sd', sd)),
                          'U': np.full(len(null), sg), 'ar': ar_n, 'ap': ap_n}}
            res = run_arms(S, rng, CFG['planted_boot'], CFG['planted_draws'])
            v = [res[a]['verdict'] for a in ('direction', 'specificity', 'setting')]
            for a, x in zip(('direction', 'specificity', 'setting'), v):
                tallies[a][x] += 1
            tallies['overall'][overall(v)] += 1
            stats['reversed_share'].append(res['direction']['core_reversed_share_vent'])
            stats['gap_equal'].append(res['specificity']['gap_points'])
            stats['gap_equal_ci_lo'].append(res['specificity']['gap_ci95'][0])
            stats['gap_gradient_no_rule'].append(res['specificity']['gradient_reported_no_rule']['gap_points'])
            stats['null_share_gradient'].append(res['specificity']['gradient_reported_no_rule']['matched_null_share_vent_gradient'])
            stats['contrast'].append(res['setting']['contrast_points_median'])
            stats['contrast_ci_lo'].append(res['setting']['contrast_ci95'][0])
            stats['contrast_equal_no_rule'].append(res['setting']['contrast_equal_conc_reported_no_rule']['median'])
            stats['window_no_rule'].append(res['setting']['max_in_window_fraction_reported_no_rule'])
        out['scenarios'][name] = {
            'spec': s, 'reps': CFG['planted_reps'],
            'verdict_rates': {a: {k: c / CFG['planted_reps'] for k, c in t.items()} for a, t in tallies.items()},
            'mean_stats': {k: float(np.mean(v)) for k, v in stats.items()}}
        print(name, json.dumps(out['scenarios'][name]['verdict_rates']), flush=True)
    return out


# ------------------------------------------------------------ eQuilibrator side
def eq_setup():
    sys.path.insert(0, str(HERE))
    import eq_env  # noqa: F401  (redirects the pooch cache into raw/)
    cc = eq_env.make_cc(CFG['compound_tier'])
    from equilibrator_api import Q_
    cc.ionic_strength = Q_(f"{CFG['ionic_strength_M']}M")
    cc.p_mg = Q_(CFG['p_mg'])
    return cc, Q_, eq_env.versions()


def transform_mode():
    v = CFG['transform_temperature']
    if v == 'by_gate':
        g = OUT / 't1_gate.json'
        if not g.exists():
            # only reached while `gate` itself runs; its gating cell is at 25 C, where
            # both variants coincide. The D2 diagnostic sets the variant explicitly.
            return 'T'
        return json.load(open(g))['d2_diagnostic']['chosen']
    return v


GAS_INCHI = {'InChI=1S/CO2/c2-1-3', 'InChI=1S/H2/h1H'}


def eq_parse(cc, rows):
    """Returns parsed reactions and per-row (ok, reason, ar, ap). No energies."""
    rx, meta = [], []
    for r in rows:
        try:
            x = cc.parse_reaction_formula(r['formula'])
            if any(pc.compound is None for pc in x.sparse_with_phases):
                raise ValueError('compound not found')
            if not x.is_balanced():
                rx.append(None); meta.append((False, 'unbalanced', 0.0, 0.0)); continue
        except Exception as e:  # noqa: BLE001
            rx.append(None); meta.append((False, f'parse: {e}'[:80], 0.0, 0.0)); continue
        ar = ap = 0.0
        for pc, coeff in x.sparse_with_phases.items():
            if cc.ccache.is_water(pc.compound) or cc.ccache.is_proton(pc.compound):
                continue
            if CFG['gas_rule'] == 'gas_1bar' and pc.compound.inchi in GAS_INCHI:
                continue
            if coeff < 0:
                ar += -coeff
            else:
                ap += coeff
        rx.append(x); meta.append((True, 'ok', ar, ap))
    return rx, meta


def eq_grid(cc, Q_, reactions, conds):
    """Mean dG'0 for every condition [n_cond, n] and a sqrt-covariance U [n, k] at pH 7,
    25 C (the CC uncertainty does not depend on pH, I, pMg or T)."""
    means = []
    U = None
    for p, t in conds:
        cc.p_h = Q_(float(p))
        tt = t if transform_mode() == 'T' else 25
        cc.temperature = Q_(f'{tt + 273.15}K')
        mu, u = cc.standard_dg_prime_multi(reactions, uncertainty_representation='fullrank')
        means.append(mu.m_as('kJ/mol'))
        if U is None:
            U = u.m_as('kJ/mol')
    return np.array(means), np.array(U)


def computable(rows, rx, meta, U):
    sig = np.sqrt(np.sum(U ** 2, axis=1))
    keep = [i for i, m in enumerate(meta) if m[0] and sig[i] < CFG['sigma_max_kJ']]
    return keep, sig


def selftest():
    cc, Q_, ver = eq_setup()
    rows = [{'formula': 'kegg:C00002 + kegg:C00001 = kegg:C00008 + kegg:C00009'}]
    rx, meta = eq_parse(cc, rows)
    conds = [(7, 25), (9, 80)]
    mu, U = eq_grid(cc, Q_, rx, conds)
    ar, ap = meta[0][2], meta[0][3]
    return {'versions': ver, 'meta': meta, 'dg0_pH7_25': mu[0].tolist(), 'dg0_pH9_80': mu[1].tolist(),
            'sigma': float(np.sqrt((U ** 2).sum())),
            'dg_equal_1mM_pH7_25': dg(mu[0][0], ar, ap, 25, 1e-3, 1e-3),
            'dg_gradient_pH9_80': dg(mu[1][0], ar, ap, 80, CFG['c_reactant_M'], CFG['c_product_M']),
            'dg_gradient_pH9_80_reversed': dg(mu[1][0], ar, ap, 80, CFG['c_reactant_M'], CFG['c_product_M'], True)}


# ------------------------------------------------------------------------ gate
def table3_column(sheet, ph, t_c):
    sys.path.insert(0, str(HERE))
    from xlsx_dump import read
    rows = dict(read(str(T3)))[sheet]
    top, sub = rows[0], rows[1]
    start = next(i for i, v in enumerate(top) if v.startswith(f'{t_c}°C'))
    col = next(i for i in range(start, len(sub)) if sub[i].strip() == f'pH {ph}')
    vals = collections.defaultdict(list)
    for r in rows[2:]:
        if r and r[0].strip():
            v = r[col] if col < len(r) else 'NA'
            vals[r[0].strip()].append(None if v in ('NA', '') else float(v))
    return vals


def gate():
    core = load_core()
    cc, Q_, ver = eq_setup()
    rx, meta = eq_parse(cc, core)
    ok = [i for i, m in enumerate(meta) if m[0]]
    cells = [('A', 7, 25, CFG['c_equal_M'], CFG['c_equal_M'])]
    if CFG['gate_second_cell']:
        s, p, t = CFG['gate_second_cell']
        cells.append((s, p, t, CFG['c_reactant_M'], CFG['c_product_M']))
    mu, U = eq_grid(cc, Q_, [rx[i] for i in ok], [(p, t) for _, p, t, _, _ in cells])
    sig = np.sqrt(np.sum(U ** 2, axis=1))
    res = {'versions': ver, 'cfg': {k: CFG[k] for k in ('transform_temperature', 'gas_rule', 'compound_tier')},
           'n_parsed_balanced': len(ok), 'n_sigma_ok': int(np.sum(sig < CFG['sigma_max_kJ'])), 'cells': []}
    passed = True
    for ci_, (sheet, p, t, cr, cp) in enumerate(cells):
        theirs = table3_column(sheet, p, t)
        seen = collections.Counter()
        ours_all, pairs, theirs_all = {}, [], []
        for j, i in enumerate(ok):
            ours_all[i] = dg(mu[ci_][j], meta[i][2], meta[i][3], t, cr, cp)
        for i, r in enumerate(core):
            k = seen[r['reaction_id']]; seen[r['reaction_id']] += 1
            tv = theirs.get(r['reaction_id'], [None] * (k + 1))[k]
            if tv is not None:
                theirs_all.append(tv)
                if i in ours_all:
                    pairs.append((ours_all[i], tv))
        a = np.array(pairs)
        r_ = float(np.corrcoef(a[:, 0], a[:, 1])[0, 1])
        sh_ours_int, sh_theirs_int = share(a[:, 0]), share(a[:, 1])
        cell = {'sheet': sheet, 'pH': p, 'T_C': t, 'n_theirs': len(theirs_all), 'n_ours': len(ours_all),
                'n_both': len(pairs), 'pearson_r': r_,
                'share_ours_intersection': sh_ours_int, 'share_theirs_intersection': sh_theirs_int,
                'share_ours_all': share(np.array(list(ours_all.values()))),
                'share_theirs_all': share(np.array(theirs_all)),
                'max_abs_diff_kJ': float(np.max(np.abs(a[:, 0] - a[:, 1])))}
        cell['pass'] = bool(r_ >= CFG['gate_r_min'] and abs(sh_ours_int - sh_theirs_int) <= CFG['gate_share_tol'])
        passed &= cell['pass']
        res['cells'].append(cell)
    if CFG['gate_d2_diagnostic']:
        sheet, p, t = CFG['gate_d2_diagnostic']
        theirs = table3_column(sheet, p, t)
        diag = {}
        saved = CFG['transform_temperature']
        for variant in ('T', '298.15'):
            CFG['transform_temperature'] = variant
            m2, _ = eq_grid(cc, Q_, [rx[i] for i in ok], [(p, t)])
            seen = collections.Counter(); pairs = []
            pos = {i: j for j, i in enumerate(ok)}
            for i, r in enumerate(core):
                k = seen[r['reaction_id']]; seen[r['reaction_id']] += 1
                tv = theirs.get(r['reaction_id'], [None] * (k + 1))[k]
                if tv is not None and i in pos:
                    pairs.append((dg(m2[0][pos[i]], meta[i][2], meta[i][3], t, CFG['c_equal_M'], CFG['c_equal_M']), tv))
            a = np.array(pairs)
            diag[variant] = {'pearson_r': float(np.corrcoef(a[:, 0], a[:, 1])[0, 1]),
                             'mean_abs_diff_kJ': float(np.mean(np.abs(a[:, 0] - a[:, 1]))), 'n': len(pairs)}
        CFG['transform_temperature'] = saved
        diag['chosen'] = max(('T', '298.15'), key=lambda v: (diag[v]['pearson_r'], -diag[v]['mean_abs_diff_kJ']))
        res['d2_diagnostic'] = {'cell': [sheet, p, t], **diag}
    res['pass'] = bool(passed)
    return res


# ------------------------------------------------------------------------ real
def build_real(cc, Q_, null_name, conds):
    core = load_core()
    null = load_null(null_name)
    rows = core + null
    rx, meta = eq_parse(cc, rows)
    okidx = [i for i, m in enumerate(meta) if m[0]]
    mu, U = eq_grid(cc, Q_, [rx[i] for i in okidx], conds)
    sig = np.sqrt(np.sum(U ** 2, axis=1))
    keep = [j for j in range(len(okidx)) if sig[j] < CFG['sigma_max_kJ']]
    kc = [j for j in keep if okidx[j] < len(core)]
    kn = [j for j in keep if okidx[j] >= len(core)]
    core_k = [core[okidx[j]] for j in kc]
    null_k = [null[okidx[j] - len(core)] for j in kn]

    def pack(js):
        return {'dg0': mu[:, js], 'U': U[js, :],
                'ar': np.array([meta[okidx[j]][2] for j in js]),
                'ap': np.array([meta[okidx[j]][3] for j in js])}
    S = {'conds': conds, 'core': pack(kc), 'null': pack(kn), 'matcher': Matcher(core_k, null_k),
         'clusters': [r['cluster'] for r in core_k]}
    counts = {'core_rows': len(core), 'core_used': len(kc), 'null_rows': len(null), 'null_used': len(kn),
              'parse_fail_or_unbalanced': sum(1 for m in meta if not m[0]),
              'sigma_excluded': len(okidx) - len(keep)}
    return S, counts


def real():
    g = OUT / 't1_gate.json'
    if not g.exists() or not json.load(open(g)).get('pass'):
        sys.exit('gate has not passed: stop (prereg rule)')
    cc, Q_, ver = eq_setup()
    conds = conditions()
    rng = np.random.default_rng(CFG['seed'])
    res = {'versions': ver, 'cfg': CFG, 'by_null': {}}
    for name in (CFG['null_primary'], CFG['null_second']):
        S, counts = build_real(cc, Q_, name, conds)
        arms = run_arms(S, rng, CFG['n_boot'], CFG['n_draws'])
        sens = {}
        saved = CFG['pond']
        for pond in CFG['pond_sensitivity']:
            CFG['pond'] = tuple(pond)
            sens[f'pond_pH{pond[0]}_{pond[1]}C'] = run_arms(S, rng, CFG['n_boot'], CFG['n_draws'])['setting']
        CFG['pond'] = saved
        res['by_null'][name] = {'counts': counts, 'arms': arms, 'setting_pond_sensitivity_no_rule': sens}
    a = res['by_null']
    p, s = a[CFG['null_primary']]['arms'], a[CFG['null_second']]['arms']
    v_dir = p['direction']['verdict']            # core-only arm; identical across pools
    v_spec = p['specificity']['verdict'] if p['specificity']['verdict'] == s['specificity']['verdict'] else 'inconclusive (null rules disagree)'
    v_set = p['setting']['verdict'] if p['setting']['verdict'] == s['setting']['verdict'] else 'inconclusive (null rules disagree)'
    res['verdicts'] = {'direction': v_dir, 'specificity': v_spec, 'setting': v_set}
    res['overall'] = overall([v_dir, v_spec, v_set])
    return res


# ------------------------------------------------------------------------ main
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    OUT.mkdir(exist_ok=True)
    if mode == 'planted':
        res = planted()
    elif mode == 'selftest':
        res = selftest()
    elif mode == 'gate':
        res = gate()
    elif mode == 'real':
        res = real()
    else:
        sys.exit(__doc__)
    res['script_sha256'] = sha(__file__)
    p = OUT / f't1_{mode}.json'
    json.dump(res, open(p, 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print('wrote', p)


if __name__ == '__main__':
    main()
