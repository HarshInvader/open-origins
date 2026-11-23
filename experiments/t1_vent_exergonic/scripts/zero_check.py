"""Post-seal diagnosis (DEVIATIONS.md): are the 37 sigma>=100 reactions exactly 0 in every Table 3 cell and sheet?
Reads only Wimmer's published Table 3 and the gate diagnosis; computes no arm statistic.
Usage: .venv/bin/python -I scripts/zero_check.py"""
import sys, json, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import t1_analysis as T
from xlsx_dump import read
g = json.load(open(HERE.parent / "scripts_out" / "t1_gate_diagnose.json"))
book = dict(read(str(T.T3)))
print("sheets", list(book))
# the 37 ids: rerun membership from gate diagnose rows is not stored; rebuild from worst list is partial, so recompute ids
import numpy as np
core = T.load_core(); cc, Q_, ver = T.eq_setup(); rx, meta = T.eq_parse(cc, core)
ok = [i for i, m in enumerate(meta) if m[0]]
mu, U = T.eq_grid(cc, Q_, [rx[i] for i in ok], [(7, 25)])
sig = np.sqrt(np.sum(U ** 2, axis=1))
bad = {core[i]['reaction_id'] for j, i in enumerate(ok) if sig[j] >= 100}
good = {core[i]['reaction_id'] for j, i in enumerate(ok) if sig[j] < 100}
res = {}
for sh, rows in book.items():
    cnt = collections.Counter()
    for r in rows[2:]:
        if not r or not r[0].strip():
            continue
        rid = r[0].strip()
        nums = []
        for v in r[1:]:
            try: nums.append(float(v))
            except Exception: pass
        if not nums:
            continue
        grp = "bad" if rid in bad else ("good" if rid in good else "other")
        cnt[(grp, "all_zero" if all(x == 0 for x in nums) else ("some_zero" if any(x == 0 for x in nums) else "no_zero"))] += 1
    res[sh] = {f"{a}|{b}": n for (a, b), n in sorted(cnt.items())}
print(json.dumps({"n_bad": len(bad), "per_sheet": res}, indent=1))
json.dump({"n_bad": len(bad), "bad_ids": sorted(bad), "per_sheet": res},
          open(HERE.parent / "scripts_out" / "t1_zero_check.json", "w"), indent=1)
