"""Summarise runs.jsonl into a grid table + results.json. Usage: .venv/bin/python -I summarize.py <dir>"""
import sys, os, json
import pandas as pd
D = sys.argv[1]
rows = [json.loads(l) for l in open(os.path.join(D, 'out/runs.jsonl'))]
recs = []
for r in rows:
    for R in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
        recs.append(dict(mu=r['mu'], ratio=r['ratio'], seed=r['seed'], rule=R, precision=r[R]['precision'],
                         recall=r[R]['recall'], called=r[R]['called'], n_true=r['n_true'], n_obs=r['n_obs'],
                         size_relerr=r['size_relerr']))
df = pd.DataFrame(recs)
g = df.groupby(['mu', 'ratio', 'rule']).agg(prec=('precision', 'mean'), prec_sd=('precision', 'std'),
                                            rec=('recall', 'mean'), rec_sd=('recall', 'std'),
                                            called=('called', 'mean'), n_true=('n_true', 'mean'),
                                            n_obs=('n_obs', 'mean'), size_relerr=('size_relerr', 'mean'),
                                            reps=('seed', 'size')).reset_index()
g['validated'] = (g.prec >= 0.8) & (g.rec >= 0.5)
g['size_validated'] = g.size_relerr.abs() <= 0.2
g.round(3).to_csv(os.path.join(D, 'grid_summary.csv'), index=False)
dec = {}
for mu in sorted(g.mu.unique()):
    ok = g[(g.mu == mu) & (g.rule == 'R4') & g.validated].ratio
    dec[str(mu)] = float(ok.max()) if len(ok) else None
res = dict(task=9, agent='orig-2', decisive_max_ratio_R4_validated=dec,
           grid=g.round(4).to_dict('records'))
json.dump(res, open(os.path.join(D, 'results.json'), 'w'), indent=1)
pd.set_option('display.width', 200)
print(g.pivot_table(index=['mu', 'ratio'], columns='rule', values=['prec', 'rec']).round(2).to_string())
print(g[g.rule == 'R1'][['mu', 'ratio', 'n_true', 'n_obs', 'size_relerr']].round(3).to_string())
print('decisive', dec)
