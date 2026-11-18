"""P1a-refit (lead ruling after P1a/OOF failure): planted size-only labels, pre-registered refit-bootstrap CI.
Same M_MW, same 50 planted label draws (default_rng(11), first item of P1), same nboot (300) and seeds (rep),
same pass mark (CI for AUC(MW+HA+MA)-AUC(MW+HA) covers 0 in >=90% of replicates). Untuned.
Usage: .venv/bin/python -I planted_refit.py <out_dir>
"""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1'); os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import sys, json, time
from multiprocessing import Pool
import numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

OUT = sys.argv[1]


def build_mmw():  # verbatim copy of molecules.py set construction (rng consumption order kept)
    mol = pd.read_csv(os.path.join(OUT, 'molecules.csv'))
    cache = pd.read_json(os.path.join(OUT, 'ma_cache.jsonl'), lines=True).drop_duplicates('smiles').set_index('smiles')
    mol['MA'] = mol.smiles.map(cache.MA); mol['timeout'] = mol.smiles.map(cache.timeout)
    abio = mol[mol.set.isin(['gdb13_1201', 'gdb17_200']) & (mol.keep == True)]  # noqa
    bio = mol[mol.set == 'rhea']
    W = pd.concat([bio, abio])
    W = W[W.MA.notna() & (W.timeout == False)]  # noqa
    W = W.drop_duplicates('smiles', keep=False)
    W = W[W.HA.isin(set(abio.HA) & set(bio.HA))].reset_index(drop=True)
    rng = np.random.default_rng(0)
    for h, g in W.groupby('HA'):  # consume rng exactly as M_HA construction does
        b, a = g[g.label == 1], g[g.label == 0]
        k = min(len(a), len(b))
        if k == 0:
            continue
        b.sample(k, random_state=int(rng.integers(1e9))); a.sample(k, random_state=int(rng.integers(1e9)))
    a = W[W.label == 0].sample(frac=1, random_state=0)
    b = W[W.label == 1].copy(); used = np.zeros(len(b), bool); bmw = b.MW.values
    pairs = []
    for i, r in a.iterrows():
        dd = np.abs(bmw - r.MW); dd[used] = np.inf; j = int(np.argmin(dd))
        if dd[j] <= 1.0:
            used[j] = True; pairs += [r, b.iloc[j]]
    return pd.DataFrame(pairs).reset_index(drop=True)


def oof(df, cols, seed=0, folds=10):
    y = df.label.values
    X = df[cols].values.astype(float); p = np.zeros(len(y))
    for tr, te in StratifiedKFold(folds, shuffle=True, random_state=seed).split(X, y):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)).fit(X[tr], y[tr])
        p[te] = m.predict_proba(X[te])[:, 1]
    return p


def delta_boot_refit(df, colsA, colsB, nboot, seed):  # same logic as molecules.py
    r = np.random.default_rng(seed); ds = []
    pos, neg = np.where(df.label == 1)[0], np.where(df.label == 0)[0]
    for k in range(nboot):
        i = np.r_[r.choice(pos, len(pos)), r.choice(neg, len(neg))]
        s = df.iloc[i].reset_index(drop=True)
        ds.append(roc_auc_score(s.label, oof(s, colsA, seed=k)) - roc_auc_score(s.label, oof(s, colsB, seed=k)))
    return np.percentile(ds, [2.5, 97.5])


S, SMA = ['MW', 'HA'], ['MW', 'HA', 'MA']
MMW = build_mmw()


def job(args):
    rep, y = args
    d = MMW[['MW', 'HA', 'MA']].copy(); d['label'] = y
    delta = roc_auc_score(y, oof(d, SMA)) - roc_auc_score(y, oof(d, S))
    lo, hi = delta_boot_refit(d, SMA, S, nboot=300, seed=rep)
    return dict(rep=rep, delta=float(delta), lo=float(lo), hi=float(hi), n_pos=int(y.sum()))


if __name__ == '__main__':
    t0 = time.time()
    z = lambda v: (v - v.mean()) / v.std()  # noqa
    lin = 1.0 * z(MMW.HA.values)
    pr = np.random.default_rng(11); R = 50
    ys = [(pr.random(len(MMW)) < 1 / (1 + np.exp(-lin))).astype(int) for _ in range(R)]
    with Pool(2) as p:
        rows = p.map(job, list(enumerate(ys)), chunksize=1)
    cover = np.mean([r['lo'] <= 0 <= r['hi'] for r in rows]); fp = np.mean([r['lo'] > 0 for r in rows])
    out = dict(check='P1a_refit size_only_b1', method='refit bootstrap (molecules resampled, 10-fold CV refit, nboot=300)',
               n_M_MW=len(MMW), reps=R, ci_covers0=float(cover), false_pos_rate=float(fp),
               mean_gain=float(np.mean([r['delta'] for r in rows])), pass_mark=0.9, passed=bool(cover >= 0.9),
               mean_ci_width=float(np.mean([r['hi'] - r['lo'] for r in rows])), seconds=round(time.time() - t0), rows=rows)
    json.dump(out, open(os.path.join(OUT, 'planted_refit.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'rows'}), flush=True)
