"""Top-level keys, dict sizes, and the full structures pickle (base-pair index lists). No activity values."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_pickle as sp
R = sys.argv[1]
for f in sorted(glob.glob(os.path.join(R, 'Data_Counts_JB_*Mut12_seqData_JB.p'))):
    o = sp.load(f)
    if not all(isinstance(v, dict) for v in o.values()): continue
    print(os.path.basename(f), {k: (len(v), type(next(iter(v.values()))).__name__) for k, v in o.items()})
s = sp.load(os.path.join(R, 'Data_Structures_ribo_structures.p'))
for k, v in s.items(): print(k, v)
