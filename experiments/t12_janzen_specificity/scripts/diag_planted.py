"""T12 calibration diagnostic (synthetic data only; reads no real rate profile).
Usage: python -I diag_planted.py <experiments/t12_janzen_specificity dir> <family> <gamma>
Prints mean I_adj by log10 all_sum bin for one synthetic family: observed, and each null variant."""
import sys, os, importlib.util
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t12", os.path.join(here, "t12_analysis.py"))
sys.argv = [sys.argv[0], sys.argv[1], "diag", sys.argv[2], sys.argv[3]]
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
fam, gamma = sys.argv[3], float(sys.argv[4])
d = t.Data(); nb = t.NoiseBank(d.r, d.sig)
rng = np.random.default_rng(7)
ix = d.family(fam)
Rm, s, rtrue = t.synth_family(fam, d.r[ix].sum(1), d.sig[ix], nb, rng, gamma, 0.7)
edges = np.array([0.9, 1.2, 1.5, 1.8, 2.1, 2.5, 4])


def prof(R):
    _, radj, nsub, allsum, Iadj, sub = t.stats_of(R)
    la = np.log10(allsum)
    out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = sub & (la >= a) & (la < b)
        out.append("%5.3f(%4d)" % (np.nanmean(Iadj[m]) if m.sum() else np.nan, m.sum() / (R.shape[0] if R.ndim == 3 else 1)))
    return float(np.nanmean(radj)), out


print("bins log10 all_sum", edges)
print("observed  R_adj %.3f" % prof(Rm)[0], prof(Rm)[1])
eb = t.EBDonors(Rm, s)
for v in ("eb", "donor", "plain"):
    Rn = t.null_rates(Rm, s, rng, 50, v, nb, eb)
    r, o = prof(Rn)
    print("%-8s  R_adj %.3f" % (v, r), o)
