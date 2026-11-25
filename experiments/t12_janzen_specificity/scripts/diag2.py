"""T12 calibration diagnostic 2 (synthetic only).  Usage: python -I diag2.py <dir> <subset> <rescale 0/1> <nrep>"""
import sys, os, importlib.util
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("t12", os.path.join(here, "t12_analysis.py"))
argv = sys.argv[:]; sys.argv = [argv[0], argv[1], "diag"]
t = importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
t.SUBSET = argv[2]; t.RESCALE = bool(int(argv[3])); nrep = int(argv[4])
d = t.Data(); nb = t.NoiseBank(d.r, d.sig)
rng = np.random.default_rng(11)
for gamma, tau, mix in ((0.0, 0.7, False), (0.0, 1.2, False), (0.0, 0.7, True), (0.1, 0.7, False), (0.2, 0.7, False)):
    for f in t.FAMS[:4]:
        ex = {v: [] for v in ("eb", "donor", "plain")}; ro = []; rt = []; ns = []
        for k in range(nrep):
            ix = d.family(f)
            Rm, s, rtrue = t.synth_family(f, d.r[ix].sum(1), d.sig[ix], nb, rng, gamma, tau, True, "level", mix)
            _, radj, nsub, _, _, _ = t.stats_of(Rm); ro.append(radj); rt.append(rtrue); ns.append(nsub)
            eb = t.EBDonors(Rm, s)
            for v in ex:
                Rn = t.null_rates(Rm, s, rng, 60, v, nb, eb)
                ex[v].append(radj - np.nanmedian(t.stats_of(Rn)[1]))
        print("g %.1f tau %.1f mix %d %s  Radj %+.3f true %+.3f nsub %4.0f | excess eb %+.3f donor %+.3f plain %+.3f"
              % (gamma, tau, mix, f, np.mean(ro), np.mean(rt), np.mean(ns), np.mean(ex["eb"]), np.mean(ex["donor"]), np.mean(ex["plain"])), flush=True)
