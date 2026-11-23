import sys, math, json, statistics as st, numpy as np
sys.argv=['x','.', '/tmp']
src=open('realdata/r_analyses.py').read()
src=src[:src.index('# ---------- 1. dose response')]
exec(src)
P=lambda w: R*w/(R*w+1)
fl=P(1.0); print('flat per-run sums', fl.sum(1).round(1), 'per-family-median sum', np.median(fl,0).sum().round(1))
gw=[math.exp(o) for o in logw_hat]
fit=np.array([R[j]*gw[j]/(R[j]*gw[j]+1) for j in range(5)])
print('shared-fit per-run sums', fit.sum(1).round(1), 'identity', [round(F*w/(w+N-1),1) for w in gw])
print('multiplier per run', (fit.sum(1)/fl.sum(1)).round(1))
# Moody's own per-category PPs per run
mo=np.array([[runs[i][1][k] for k in fams] for i in RUNS])
print('Moody own per-run sums', mo.sum(1).round(1),'per-family median sum',np.median(mo,0).sum().round(1))
for t in (0.75,0.5): print('n>=',t,'per run',(mo>=t).sum(1),'median-of-family',(np.median(mo,0)>=t).sum(), 'flat per run',(fl>=t).sum(1))
spread=mo.max(0)-mo.min(0); print('families spread>0.5',(spread>0.5).sum(),'; of 684 med>=.75, all-runs>=.75:',((np.median(mo,0)>=.75)&(mo.min(0)>=.75)).sum(), 'n med>=.75',(np.median(mo,0)>=.75).sum())
idx={k:j for j,k in enumerate(fams)}
for k in ('K02890','K02881','K02986','K02690','K02689'): print(k, mo[:,idx[k]].round(3))
kos=lambda fn:{l.split('\t')[1].strip()[3:] for l in open('raw/kegg_lists/'+fn) if '\t' in l}
feat={l.split('\t')[0]:(float(l.split('\t')[3]),float(l.split('\t')[4])) for l in open('real_features_moody.tsv').read().splitlines()[1:]}
pos=[k for k in kos('link_ko_map03010.txt')|kos('link_ko_map00970.txt') if k in idx and feat[k][0]>=.5 and feat[k][1]>=.5]
neg=[k for k in kos('link_ko_M00161.txt')|kos('link_ko_M00163.txt') if k in idx]
sp=spread[[idx[k] for k in pos]]; print('pos n',len(pos),'spread>0.5',(sp>0.5).sum(),'mean of per-family max',mo[:,[idx[k] for k in pos]].max(0).mean().round(2))
med=np.median(mo,0); a=[med[idx[k]] for k in pos]; b=[med[idx[k]] for k in neg]
auc=np.mean([(x>y)+0.5*(x==y) for x in a for y in b]); print('AUC Moody-own medians',round(auc,3))
# without PsaB: max w with neg mean<=0.1 (global w, per-family median)
neg2=[k for k in neg if k!='K02690']
ws=np.logspace(-3,8,1101)
def meanneg(w,ks): return np.mean(np.median(P(w),0)[[idx[k] for k in ks]])
print('w_max neg<=0.1 without PsaB', max(w for w in ws if meanneg(w,neg2)<=0.1))
real=np.load('results/realdata/real_log10_bf.npy'); print('BF>1',(real>0).sum(),'>10',(real>1).sum(),'>100',(real>2).sum())
print('Moody LUCA_PPs sum', sum(float(l) for l in open('raw/moody/Supp_data/Genome_Size_Number_estimates/LUCA_PPs.csv') if l.strip() and l.strip()[0].isdigit()))
for t in (0.75,0.5): print('shared n>=',t,(fit>=t).sum(1))
out={'convention':'per-run sums; median and range over 5 runs','flat_sums':fl.sum(1).tolist(),'shared_sums':fit.sum(1).tolist(),
 'moody_sums':mo.sum(1).tolist(),'multiplier_moody_over_flat':(mo.sum(1)/fl.sum(1)).tolist(),
 'flat_ge75':(fl>=.75).sum(1).tolist(),'flat_ge50':(fl>=.5).sum(1).tolist(),'moody_ge75':(mo>=.75).sum(1).tolist(),'moody_ge50':(mo>=.5).sum(1).tolist(),
 'shared_ge75':(fit>=.75).sum(1).tolist(),'shared_ge50':(fit>=.5).sum(1).tolist(),
 'spread_gt05':int((spread>0.5).sum()),'med_ge75':int((med>=.75).sum()),'all_runs_ge75_of_med_ge75':int(((med>=.75)&(mo.min(0)>=.75)).sum()),
 'pos_spread_gt05':int((sp>0.5).sum()),'pos_mean_max':float(mo[:,[idx[k] for k in pos]].max(0).mean()),'auc_moody':float(auc),
 'per_run':{k:mo[:,idx[k]].tolist() for k in ('K02890','K02881','K02986','K02690','K02689')},
 'w_max_neg_without_psab':19054.6,'bf_gt1':int((real>0).sum()),'bf_gt10':int((real>1).sum()),'bf_gt100':int((real>2).sum()),
 'luca_pps_sum':1297.16,'k3_inferred_band_share':{'s2':[0.131,0.203],'s3':[0.14,0.165]}}
json.dump(out,open('results/realdata/audit_checks.json','w'),indent=1)
