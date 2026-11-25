import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "t18_qt45_error_threshold", "scripts"))
import numpy as np, t18_analysis as T, t18_core as C
cal = T.calib(); S, D, _, _ = C.load_real(); muts = C.mutation_list()
mask = [((i, bi), (j, bj)) for (i, bi) in muts for (j, bj) in muts if j > i and np.isfinite(D[i, bi, j, bj])]
kw = dict(N=20000, k=5, T0=120, burn0=60, T=80, burn=30, refine=False)
truth, So, Do, params, rng = T.make_truth("B", 1, cal, mask)
tr = C.threshold(truth, rng, w_dead=T.W_DEAD, **kw)
ge = C.fit_ge(So, Do)
fi = C.threshold(C.MeasuredLandscape(So, Do, "ge", ge=ge), rng, w_dead=T.W_DEAD, **kw)
# oracle: truth landscape but HD>=3 replaced by global curve of the truth's own additive+pair latent (no h field)
tr0 = C.TruthLandscape(truth.A, truth.E.astype(float), 0.0, truth.lo, truth.hi, truth.nu, seed=1)
t0 = C.threshold(tr0, rng, w_dead=T.W_DEAD, **kw)
out = dict(rep=1, e_true=tr["e_star"], e_fit=fi["e_star"], rel_err=fi["e_star"]/tr["e_star"]-1,
           e_true_without_higher_order_field=t0["e_star"], settings=kw)
json.dump(out, open("t18_qt45_error_threshold/scripts_out/t18_diag_f2_B1.json", "w"), indent=1)
print(json.dumps(out))
