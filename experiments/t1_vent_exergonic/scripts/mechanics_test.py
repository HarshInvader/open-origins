"""Mechanics test of the `real` code path (build_real -> run_arms -> verdicts) on FAKE
core and null sets made only of R00086 (ATP + H2O -> ADP + Pi), whose Delta G'0 was
already seen in the install check. Touches no core or null reaction and no Table 3 value.
Usage: .venv/bin/python -I scripts/mechanics_test.py"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('t1', HERE / 't1_analysis.py')
t1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t1)

F = 'kegg:C00002 + kegg:C00001 = kegg:C00008 + kegg:C00009'
R = 'kegg:C00008 + kegg:C00009 = kegg:C00002 + kegg:C00001'
base = {'ec_class': '3', 'n_left_main': '0', 'n_right_main': '0', 'ntp_hydrolysis_left': '1',
        'reaction_id': 'R00086', 'kegg_module': 'M00000', 'synthesis_target': 'x'}
fake_core = [dict(base, formula=F, cluster='M1'), dict(base, formula=F, cluster='M2'),
             dict(base, formula=R, cluster='M3', ntp_hydrolysis_left='0')]
fake_null = [dict(base, formula=F), dict(base, formula=R, ntp_hydrolysis_left='0')]
t1.load_core = lambda: fake_core
t1.load_null = lambda name: fake_null
t1.CFG['transform_temperature'] = 'T'
cc, Q_, ver = t1.eq_setup()
S, counts = t1.build_real(cc, Q_, 'fake', t1.conditions())
res = t1.run_arms(S, np.random.default_rng(1), 50, 50)
print(json.dumps({'counts': counts, 'arms': res}, indent=1, default=str))
