"""Per file: key lengths, wild type (the key with most total reads, checked against the per-position consensus),
mutant-class coverage and read depth (allowed before the seal). No activity value is printed."""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle as sp
import numpy as np
R = sys.argv[1]
for f in sorted(glob.glob(os.path.join(R, 'Data_Counts_JB_*Mut12_seqData_JB.p'))):
    o = sp.load(f)
    if 'rz_cleaved1' not in o: continue
    name = os.path.basename(f).split('_')[3]
    keys = set()
    for k in o:
        if k.startswith('rz_'): keys |= set(o[k])
    L = collections.Counter(len(k) for k in keys)
    tot = collections.Counter()
    for r in (1, 2, 3):
        for k in ('rz_cleaved%d' % r, 'rz_uncleaved%d' % r):
            for s, n in o[k].items(): tot[s] += n
    wt = max(tot, key=tot.get)
    cons = ''.join(collections.Counter(c).most_common(1)[0][0] for c in zip(*[k for k in keys if len(k) == len(wt)]))
    nm = collections.Counter(); depth = collections.defaultdict(list)
    for s in keys:
        m = sum(a != b for a, b in zip(s, wt)); nm[m] += 1; depth[m].append(tot[s])
    Lw = len(wt)
    print('==', name, 'keylens', dict(L), 'WT len', Lw, 'WT==consensus', wt == cons)
    print('   WT', wt)
    print('   n variants by #mut', dict(sorted(nm.items())), 'expected singles', 3 * Lw, 'doubles', 9 * Lw * (Lw - 1) // 2)
    for m in (0, 1, 2):
        d = np.array(depth[m]); print('   depth m=%d: n=%d min=%d p5=%d median=%d' % (m, len(d), d.min(), np.percentile(d, 5), np.median(d)))
    d2 = np.array(depth[2]); print('   doubles with total reads >=10: %d, >=20: %d, >=50: %d' % ((d2 >= 10).sum(), (d2 >= 20).sum(), (d2 >= 50).sum()))
    # per-replicate depth of doubles
    for r in (1, 2, 3):
        c = np.array([o['rz_cleaved%d' % r].get(s, 0) + o['rz_uncleaved%d' % r].get(s, 0) for s in keys if sum(a != b for a, b in zip(s, wt)) == 2])
        print('   rep%d doubles: median reads %d, zero-read %d' % (r, np.median(c), (c == 0).sum()))
