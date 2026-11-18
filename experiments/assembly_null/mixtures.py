"""T7b: Marshall 2021 mixtures. MS2 peak count (MA proxy) vs m/z (size) for biological vs non-living samples.
Planted controls P2 first, then real data. Usage: .venv/bin/python -I mixtures.py <raw_dir> <out_dir>
"""
import sys, os, json
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression

RAW, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
M = os.path.join(RAW, 'marshall')
rng0 = np.random.default_rng(0)
NSUB, NBOOT, K = 500, 2000, 15

d = pd.read_csv(os.path.join(M, 'Figure_4_-_Mixtures/EnviromentalSamplesUpdated_Oct2020_outsidedata_seawater.csv'))
d.columns = ['mz', 'peaks', 'sample', 'source']
EXCL = {'MeOH Control', 'Aeromonas veronii TOP15', 'Seawater TOP15'}
blind = d[d.source == '??']
d = d[(d.source != '??') & (~d['sample'].isin(EXCL))].copy()

# standard curve: MA ~ mean.MS2 (OLS)
sc = pd.read_csv(os.path.join(M, 'Figure_3-_MS2-Single_Molecules/MS_data_Standard_Curve.csv'))
b1, b0 = np.polyfit(sc['mean.MS2'], sc['MA'], 1)
r_sc = np.corrcoef(sc['mean.MS2'], sc['MA'])[0, 1]


def est_ma(p):
    return b0 + b1 * p


def sample_feats(df, rng, nsub=NSUB, k=K):
    """per-sample max peaks and max m/z, averaged over random subsamples of min(n,k) ions"""
    out = []
    for s, g in df.groupby('sample'):
        pk, mz = g.peaks.values, g.mz.values
        n = len(g)
        if n <= k or nsub == 0:
            mp_, mm = pk.max(), mz.max()
            if nsub == 0:
                pass
        else:
            idx = np.array([rng.choice(n, k, replace=False) for _ in range(nsub)])
            mp_, mm = pk[idx].max(1).mean(), mz[idx].max(1).mean()
        out.append(dict(sample=s, y=int(g.y.iloc[0]), maxpk=mp_, maxmz=mm, n=n))
    return pd.DataFrame(out)


def auc(y, x):
    return roc_auc_score(y, x)


def boot_delta(sf, rng, nboot=NBOOT):
    y = sf.y.values; a = sf.maxpk.values; b = sf.maxmz.values
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    ds = []
    for _ in range(nboot):
        i = np.r_[rng.choice(pos, len(pos)), rng.choice(neg, len(neg))]
        ds.append(auc(y[i], a[i]) - auc(y[i], b[i]))
    return np.percentile(ds, [2.5, 97.5])


def binned_auc(df, col):
    """ion-level AUC within 50-Da m/z bins, weighted by #pos*#neg pairs"""
    num = den = 0.0
    for _, g in df.groupby((df.mz // 50).astype(int)):
        npos, nneg = (g.y == 1).sum(), (g.y == 0).sum()
        if npos and nneg:
            w = npos * nneg
            num += w * auc(g.y, g[col]); den += w
    return num / den if den else np.nan


def loso(sf, cols):
    y = sf.y.values; X = sf[cols].values; X = (X - X.mean(0)) / X.std(0)
    p = np.zeros(len(y))
    for i in range(len(y)):
        tr = np.arange(len(y)) != i
        p[i] = LogisticRegression().fit(X[tr], y[tr]).predict_proba(X[i:i + 1])[0, 1]
    return auc(y, p)


def analyse(df, rng, nsub=NSUB, nboot=NBOOT, full=True):
    sf = sample_feats(df, rng, nsub)
    r = dict(n_pos=int(sf.y.sum()), n_neg=int((1 - sf.y).sum()),
             auc_peaks=auc(sf.y, sf.maxpk), auc_mz=auc(sf.y, sf.maxmz))
    r['delta'] = r['auc_peaks'] - r['auc_mz']
    r['delta_ci'] = list(boot_delta(sf, rng, nboot))
    if full:
        r['ion_binned_auc_peaks'] = binned_auc(df, 'peaks')
        r['ion_binned_auc_mz'] = binned_auc(df, 'mz')
        r['loso_mz'] = loso(sf, ['maxmz']); r['loso_mz_peaks'] = loso(sf, ['maxmz', 'maxpk'])
        sf['estMA'] = est_ma(sf.maxpk)
        r['frac_estMA_ge15_bio'] = float((sf[sf.y == 1].estMA >= 15).mean())
        r['frac_estMA_ge15_nonbio'] = float((sf[sf.y == 0].estMA >= 15).mean())
        r['samples'] = sf.round(3).to_dict('records')
    return r


def label(df, neg, pos={'Biological'}, swap=()):
    df = df[df.source.isin(pos | neg)].copy()
    df['y'] = df.source.isin(pos).astype(int)
    df.loc[df['sample'].isin(swap), 'y'] = 0
    return df


res = dict(standard_curve=dict(slope=b1, intercept=b0, r=r_sc, n=len(sc)))

# ---------- P2 planted controls: keep real sample structure (ion counts, m/z), resample peaks
base = label(d, {'Abiotic', 'Dead'})
# pooled peaks ~ m/z relation (log peaks linear in m/z) on all included ions, labels ignored
lp = np.log1p(base.peaks.values); cf = np.polyfit(base.mz.values, lp, 1)
resid_sd = np.std(lp - np.polyval(cf, base.mz.values))
# per-sample random effect so samples differ (sd from data: sd of per-sample mean residuals)
base['res'] = lp - np.polyval(cf, base.mz.values)
samp_sd = base.groupby('sample').res.mean().std()
planted = {}
rng = np.random.default_rng(1)
for delta in [0.0, 0.5, 1.0, 1.5, 2.0]:
    hits = cover = 0; R = 40
    for _ in range(R):
        sim = base.copy()
        u = {s: rng.normal(0, samp_sd) for s in sim['sample'].unique()}
        shift = sim.y.values * delta * samp_sd
        sim['peaks'] = np.expm1(np.polyval(cf, sim.mz.values) + sim['sample'].map(u).values + shift
                                + rng.normal(0, np.sqrt(max(resid_sd**2 - samp_sd**2, 1e-6)), len(sim)))
        r = analyse(sim, rng, nsub=30, nboot=400, full=False)
        lo, hi = r['delta_ci']
        hits += lo > 0; cover += lo <= 0 <= hi
    planted[str(delta)] = dict(power=hits / R, ci_covers0=cover / R, reps=R)
    print('P2 delta(sample-sd units)', delta, planted[str(delta)], flush=True)
res['planted_P2'] = dict(note='delta in units of between-sample SD of log-peak residual', samp_sd=samp_sd,
                         resid_sd=resid_sd, results=planted)
res['P2a_pass'] = planted['0.0']['ci_covers0'] >= 0.9

# ---------- real data
res['primary'] = analyse(base, np.random.default_rng(2))
res['sens_formose_neg'] = analyse(label(d, {'Abiotic', 'Dead'}, swap={'Formose Recursive Cycle'}), np.random.default_rng(3))
res['sens_abiotic_only'] = analyse(label(d, {'Abiotic'}), np.random.default_rng(4))
res['sens_no_subsample'] = analyse(base, np.random.default_rng(5), nsub=0)
# blinded samples, descriptive
bf = blind.copy(); bf['y'] = 0
res['blinded'] = sample_feats(bf, np.random.default_rng(6)).assign(estMA=lambda x: est_ma(x.maxpk)).round(2).to_dict('records')
json.dump(res, open(os.path.join(OUT, 'mixtures.json'), 'w'), indent=1, default=float)
for k in ['primary', 'sens_formose_neg', 'sens_abiotic_only', 'sens_no_subsample']:
    r = res[k]; print(k, {x: (round(v, 3) if isinstance(v, float) else v) for x, v in r.items() if x != 'samples'})
