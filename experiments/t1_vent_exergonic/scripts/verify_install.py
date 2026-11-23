"""Install check on ONE textbook reaction outside Wimmer's set:
ATP + H2O = ADP + Pi (KEGG C00002 + C00001 = C00008 + C00009), pH 7, I = 0.25 M,
pMg 3 (Wimmer's Mg2+ 3 mM; eQuilibrator default also pMg 3), 25 C.
Usage: .venv/bin/python -I scripts/verify_install.py"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import eq_env  # noqa: E402  (must precede equilibrator imports)
from equilibrator_api import Q_  # noqa: E402

cc = eq_env.make_cc('bundled')
cc.p_h = Q_(7.0)
cc.ionic_strength = Q_('0.25M')
cc.p_mg = Q_(3.0)
cc.temperature = Q_('298.15K')
rxn = cc.parse_reaction_formula('kegg:C00002 + kegg:C00001 = kegg:C00008 + kegg:C00009')
assert rxn.is_balanced(), 'unbalanced'
dg0 = cc.standard_dg_prime(rxn)
dgm = cc.physiological_dg_prime(rxn)
out = {'reaction': 'ATP + H2O = ADP + Pi (C00002 + C00001 = C00008 + C00009)',
       'conditions': 'pH 7.0, I 0.25 M, pMg 3.0, 298.15 K',
       'dG_prime_0_kJ_per_mol': round(dg0.value.m_as('kJ/mol'), 2),
       'sigma_kJ_per_mol': round(dg0.error.m_as('kJ/mol'), 2),
       'dG_prime_m_1mM_kJ_per_mol': round(dgm.value.m_as('kJ/mol'), 2),
       'versions': eq_env.versions(),
       'cache_dir_contents': sorted(os.listdir(eq_env.CACHE))}
print(json.dumps(out, indent=1))
