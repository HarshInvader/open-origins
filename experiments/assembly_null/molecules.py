"""T7a: biotic (Rhea) vs abiotic enumerated (GDB-13/17) molecules: does MA add separation beyond size, and beat compression?
Also T7c (Hazen minerals, descriptive). Usage: .venv/bin/python -I molecules.py <out_dir>
"""
import sys, os, json
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

OUT = sys.argv[1]
mol = pd.read_csv(os.path.join(OUT, 'molecules.csv'))
cache = pd.read_json(os.path.join(OUT, 'ma_cache.jsonl'), lines=True).drop_duplicates('smiles').set_index('smiles')
mol['MA'] = mol.smiles.map(cache.MA)
mol['timeout'] = mol.smiles.map(cache.timeout)
res = {}

# ---------- validation gate
val = {}
for s in ['checks', 'coconut_55', 'gdb13_1201', 'gdb17_200', 'reaxys']:
    g = mol[(mol.set == s) & mol.MA.notna() & (mol.timeout == False)]  # noqa
    val[s] = dict(n=len(g), agree=float((g.MA == g.ref_ma).mean()),
                  mean_diff=float((g.MA - g.ref_ma).mean()),
                  n_timeout=int((mol[mol.set == s].timeout == True).sum()))  # noqa
res['validation'] = val
res['gate_pass'] = all(val[s]['agree'] == 1.0 for s in ['checks', 'coconut_55', 'gdb13_1201', 'gdb17_200'])
print('validation', json.dumps(val, indent=1), 'gate', res['gate_pass'], flush=True)

# ---------- analysis set
abio = mol[mol.set.isin(['gdb13_1201', 'gdb17_200']) & (mol.keep == True)]  # noqa
bio = mol[mol.set == 'rhea']
W = pd.concat([bio, abio])
n_to = int((W.timeout == True).sum())  # noqa
W = W[W.MA.notna() & (W.timeout == False)]  # noqa
W = W.drop_duplicates('smiles', keep=False)  # drop any molecule in both groups
W = W[W.HA.isin(set(abio.HA) & set(bio.HA))].reset_index(drop=True)
res['window'] = dict(n_bio=int((W.label == 1).sum()), n_abio=int((W.label == 0).sum()), n_timeout_dropped=n_to,
                     HA_values=sorted(int(x) for x in W.HA.unique()))

rng = np.random.default_rng(0)
# M_HA
parts = []
for h, g in W.groupby('HA'):
    b, a = g[g.label == 1], g[g.label == 0]
    k = min(len(a), len(b))
    if k == 0:
        continue
    parts += [b.sample(k, random_state=int(rng.integers(1e9))), a.sample(k, random_state=int(rng.integers(1e9)))]
MHA = pd.concat(parts).reset_index(drop=True)
# M_MW: nearest unused biotic within 1 Da
a = W[W.label == 0].sample(frac=1, random_state=0)
b = W[W.label == 1].copy(); used = np.zeros(len(b), bool); bmw = b.MW.values
pairs = []
for i, r in a.iterrows():
    dd = np.abs(bmw - r.MW); dd[used] = np.inf; j = int(np.argmin(dd))
    if dd[j] <= 1.0:
        used[j] = True; pairs += [r, b.iloc[j]]
MMW = pd.DataFrame(pairs).reset_index(drop=True)
res['M_HA_n'] = len(MHA); res['M_MW_n'] = len(MMW)


def oof(df, cols, y=None, seed=0, folds=10):
    y = df.label.values if y is None else y
    X = df[cols].values.astype(float); p = np.zeros(len(y))
    for tr, te in StratifiedKFold(folds, shuffle=True, random_state=seed).split(X, y):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return p


def cv_auc(df, cols, y=None, reps=5):
    y = df.label.values if y is None else y
    return float(np.mean([roc_auc_score(y, oof(df, cols, y, seed=s)) for s in range(reps)]))


def delta_boot_oof(df, colsA, colsB, y=None, nboot=1000, seed=0):
    """CI for AUC(A)-AUC(B) by bootstrapping out-of-fold predictions (fast; used in planted controls)"""
    y = df.label.values if y is None else y
    pa, pb = oof(df, colsA, y), oof(df, colsB, y); r = np.random.default_rng(seed); ds = []
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    for _ in range(nboot):
        i = np.r_[r.choice(pos, len(pos)), r.choice(neg, len(neg))]
        ds.append(roc_auc_score(y[i], pa[i]) - roc_auc_score(y[i], pb[i]))
    return roc_auc_score(y, pa) - roc_auc_score(y, pb), np.percentile(ds, [2.5, 97.5])


def delta_boot_refit(df, colsA, colsB, nboot=2000, seed=0):
    """prereg primary: bootstrap molecules, refit 10-fold CV (1 repeat) each time"""
    r = np.random.default_rng(seed); ds = []
    pos, neg = np.where(df.label == 1)[0], np.where(df.label == 0)[0]
    for k in range(nboot):
        i = np.r_[r.choice(pos, len(pos)), r.choice(neg, len(neg))]
        s = df.iloc[i].reset_index(drop=True)
        ds.append(roc_auc_score(s.label, oof(s, colsA, seed=k)) - roc_auc_score(s.label, oof(s, colsB, seed=k)))
    return np.percentile(ds, [2.5, 97.5])


S, SMA, SLZ = ['MW', 'HA'], ['MW', 'HA', 'MA'], ['MW', 'HA', 'LZ']

# ---------- P1 planted controls on the real M_MW feature matrix
ma_resid = MMW.MA - np.polyval(np.polyfit(MMW.HA, MMW.MA, 1), MMW.HA)
z = lambda v: (v - v.mean()) / v.std()  # noqa
pr = np.random.default_rng(11); P1 = {}
for name, lin in [('size_only_b1', 1.0 * z(MMW.HA.values))] + \
                 [(f'ma_resid_g{g}', g * z(ma_resid.values)) for g in [0.1, 0.2, 0.3, 0.5]]:
    hits = cover = 0; gains = []; R = 50
    for rep in range(R):
        y = (pr.random(len(MMW)) < 1 / (1 + np.exp(-lin))).astype(int)
        d, (lo, hi) = delta_boot_oof(MMW, SMA, S, y=y, nboot=300, seed=rep)
        gains.append(d); hits += lo > 0; cover += lo <= 0 <= hi
    P1[name] = dict(power=hits / R, ci_covers0=cover / R, mean_gain=float(np.mean(gains)), reps=R)
    print('P1', name, P1[name], flush=True)
res['planted_P1'] = P1
res['P1a_pass'] = P1['size_only_b1']['ci_covers0'] >= 0.9

# ---------- real data
prim = dict(auc_S=cv_auc(MMW, S), auc_SMA=cv_auc(MMW, SMA), auc_SLZ=cv_auc(MMW, SLZ),
            auc_SMALZ=cv_auc(MMW, S + ['MA', 'LZ']))
prim['delta_primary'] = prim['auc_SMA'] - prim['auc_S']
prim['delta_primary_ci'] = list(delta_boot_refit(MMW, SMA, S, nboot=2000, seed=1))
prim['delta_S1'] = prim['auc_SMA'] - prim['auc_SLZ']
prim['delta_S1_ci'] = list(delta_boot_refit(MMW, SMA, SLZ, nboot=2000, seed=2))
res['primary_M_MW'] = prim
print('primary', prim, flush=True)


def single(df, col, nboot=2000, seed=0):
    r = np.random.default_rng(seed); y = df.label.values; x = df[col].values; a = []
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    for _ in range(nboot):
        i = np.r_[r.choice(pos, len(pos)), r.choice(neg, len(neg))]
        a.append(roc_auc_score(y[i], x[i]))
    return dict(auc=float(roc_auc_score(y, x)), ci=list(np.percentile(a, [2.5, 97.5])))


# S5 (added after the validation finding, before outcomes): Kekule-form sensitivity. Replace GDB MA with the
# reference MA computed on the original GDB mol files (= our implementation on those files, 1471/1471 agreement).
M5 = MMW.copy()
isg = M5.set.isin(['gdb13_1201', 'gdb17_200'])
M5.loc[isg, 'MA'] = M5.loc[isg, 'ref_ma']
s5 = dict(n_changed=int((MMW.MA != M5.MA).sum()), auc_S=cv_auc(M5, S), auc_SMA=cv_auc(M5, SMA), auc_SLZ=cv_auc(M5, SLZ))
s5['delta_primary'] = s5['auc_SMA'] - s5['auc_S']
s5['delta_primary_ci_oofboot'] = list(delta_boot_oof(M5, SMA, S, nboot=2000, seed=7)[1])
res['S5_kekule_sensitivity'] = s5

res['S2_single_M_HA'] = {c: single(MHA, c) for c in ['MA', 'LZ', 'MW', 'HA']}
res['S3_single_unmatched'] = {c: single(W, c) for c in ['MA', 'LZ', 'MW', 'HA']}
# S4 direction: mean MA(bio)-MA(abio) on M_HA, stratified by HA (each stratum balanced), bootstrap within strata
diffs = []; r = np.random.default_rng(5)
groups = [(g[g.label == 1].MA.values, g[g.label == 0].MA.values) for _, g in MHA.groupby('HA')]
wts = np.array([len(x) for x, _ in groups], float)
point = float(np.sum([w * (x.mean() - y.mean()) for w, (x, y) in zip(wts, groups)]) / wts.sum())
for _ in range(2000):
    diffs.append(np.sum([w * (r.choice(x, len(x)).mean() - r.choice(y, len(y)).mean()) for w, (x, y) in zip(wts, groups)]) / wts.sum())
res['S4_MA_bio_minus_abio_M_HA'] = dict(mean=point, ci=list(np.percentile(diffs, [2.5, 97.5])))
# per-HA summary table
res['per_HA'] = W.groupby(['HA', 'label']).agg(n=('MA', 'size'), MA_mean=('MA', 'mean'), LZ_mean=('LZ', 'mean')).round(2).reset_index().to_dict('records')
res['MA_ge15'] = dict(bio=int((W[W.label == 1].MA >= 15).sum()), abio=int((W[W.label == 0].MA >= 15).sum()))

# ---------- T7c Hazen minerals (descriptive): heavy atoms of subunits (H excluded), EMA published
hazen = [  # mineral, subunit heavy-atom count from formula in Table 1, SBMA, EMA
    ('calcite', 1 + 3, 3, 2), ('forsterite', 1 + 4, 3, 2), ('akermanite', 2 + 7, 5, 3), ('beryl', 6 + 18, 6, 5),
    ('vesuvianite', 1 + 4 + 2 + 7 + 1 + 4, 10, 8), ('fluor-uvite', 3 + 3 + 6 + 36, 14, 11),
    ('eudialyte_a', 6 + 2 * 12 + 6 * 13, 12, 10), ('eudialyte_b', 2 * 36 + 6 * 5, 12, 10),
    ('vanarsite', 1 + 12 + 6 + 51, 16, 11), ('paddlewheelite', 2 + 2 + 4 + 12 + 12 * 4, 17, 13),
    ('ewingite', 24 * 3 + 30 * 4 + 4, 20, 18), ('ilmajokite', 1 + 3 * 15 + 17 + 35, 21, 18)]
org = W  # organic MA~HA relation (both groups pooled) on our window
cf = np.polyfit(org.HA, org.MA, 1)
res['T7c_hazen'] = dict(organic_fit_MA_on_HA=list(cf), organic_HA_range=[int(org.HA.min()), int(org.HA.max())],
                        minerals=[dict(mineral=m, HA=h, SBMA=s, EMA=e, organic_trend_MA=float(np.polyval(cf, h)),
                                       EMA_per_HA=e / h) for m, h, s, e in hazen],
                        organic_MA_per_HA_median=float((org.MA / org.HA).median()))
json.dump(res, open(os.path.join(OUT, 'molecules.json'), 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k not in ('per_HA',)}, indent=1, default=float))
