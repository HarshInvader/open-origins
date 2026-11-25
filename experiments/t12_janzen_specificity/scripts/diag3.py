"""T12 calibration diagnostic 3 (synthetic only): SIMEX on R_adj.  Usage: python -I diag3.py <dir> <subset> <nrep>"""
import sys, os, importlib.util
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t12", os.path.join(here, "t12_analysis.py"))
argv = sys.argv[:]; sys.argv = [argv[0], argv[1], "diag"]
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
t.SUBSET = argv[2]; nrep = int(argv[3])
d = t.Data(); nb = t.NoiseBank(d.r, d.sig)
rng = np.random.default_rng(13)
LAM = np.array([0.0, 0.5, 1.0, 1.5, 2.0]); K = 40


def simex(R, s):
    vals = [t.stats_of(R)[1]]
    for lam in LAM[1:]:
        Rl = R[None] * np.exp(np.sqrt(lam) * s[None] * rng.standard_normal((K,) + R.shape))
        vals.append(np.nanmean(t.stats_of(Rl)[1]))
    vals = np.array(vals, float)
    c2 = np.polyfit(LAM, vals, 2); c1 = np.polyfit(LAM, vals, 1)
    return vals, np.polyval(c2, -1.0), np.polyval(c1, -1.0)


for gamma, tau, mix, nz in ((0.0, 0.7, False, "level"), (0.0, 1.2, False, "level"), (0.0, 0.4, False, "level"),
                            (0.0, 0.7, True, "level"), (0.0, 0.7, False, "cell"),
                            (0.1, 0.7, False, "level"), (0.2, 0.7, False, "level")):
    for f in t.FAMS:
        ro, rt, q, l, ns = [], [], [], [], []
        for k in range(nrep):
            ix = d.family(f)
            Rm, s, rtrue = t.synth_family(f, d.r[ix].sum(1), d.sig[ix], nb, rng, gamma, tau, True, nz, mix)
            vals, rq, rl = simex(Rm, s)
            ro.append(vals[0]); rt.append(rtrue); q.append(rq); l.append(rl); ns.append(t.stats_of(Rm)[2])
        print("g %.1f tau %.1f mix %d %-5s %s nsub %4.0f  obs %+.3f  true %+.3f  simex-quad %+.3f (sd %.3f)  simex-lin %+.3f"
              % (gamma, tau, mix, nz, f, np.mean(ns), np.mean(ro), np.mean(rt), np.mean(q), np.std(q), np.mean(l)), flush=True)
