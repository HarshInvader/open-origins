"""Declared blind count (prereg 'Open before sealing' A, option 3): per setting, rows and clusters inside tier A
(T, pH, Mg ranges of D6) and which bound excludes the rest; controls in or out. Counts and booleans only:
no cleavage rate, contrast, L* or measured value is computed or printed."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t3_analysis as T
C = T.CFG
m, _ = T.load_marhys(); u, _ = T.load_usgs()
def inr(r, lo, hi): return lo <= r <= hi
out = {}
for name, d in (('marhys4', m), ('usgs', u)):
    for k, rows in d.items():
        def flags(r, mgmax):
            return (inr(r['T'], *C['T_range']), inr(r['pH'], *C['pH_range']), inr(r['Mg'], C['Mg_range'][0], mgmax))
        rec = {'rows': len(rows), 'clusters': len({r['cluster'] for r in rows})}
        for lab, mgmax in (('mg55', 0.055), ('mg50', 0.050)):
            ins = [r for r in rows if all(flags(r, mgmax))]
            rec[lab] = {'in_rows': len(ins), 'in_clusters': len({r['cluster'] for r in ins})}
        rec['fails_T'] = sum(not flags(r, 0.055)[0] for r in rows); rec['fails_pH'] = sum(not flags(r, 0.055)[1] for r in rows)
        rec['fails_Mg'] = sum(not flags(r, 0.055)[2] for r in rows)
        out[f'{name}|{k}'] = rec
sw = T.median_chem(m['SW|SW']); st = T.median_chem(u['river, stream, or creek'])
out['controls_in_range'] = {'seawater_pH_Mg55': inr(sw['pH'], *C['pH_range']) and inr(sw['Mg'], C['Mg_range'][0], 0.055),
                            'seawater_Mg50': inr(sw['Mg'], C['Mg_range'][0], 0.050),
                            'stream_pH_Mg55': inr(st['pH'], *C['pH_range']) and inr(st['Mg'], C['Mg_range'][0], 0.055)}
print('CFG ranges', C['T_range'], C['pH_range'], C['Mg_range'])
json.dump(out, open(os.path.join(T.EXP, 'scripts_out', 't3_range_count.json'), 'w'), indent=1)
for k, v in out.items(): print(k, v)
