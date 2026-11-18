"""Task #2: is QT45 net replication above or below 1 per cycle? Pure arithmetic on published numbers + a planted check.
Usage: .venv/bin/python -I net_replication.py <out_dir>
"""
import sys, os, json
import numpy as np
from scipy.integrate import solve_ivp

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

# ---- published inputs (Gianni et al. 2026, Science 391:1022, doi:10.1126/science.adt2760; PMC7618777 main text + SI)
P = dict(
    Y_minus=0.0024,      # (-) strand full-length yield, 72 d, NNN pool (main text, Fig 4C)
    Y_plus=0.0017,       # (+) strand full-length yield, 72 d, defined triplets + 1 hexamer (main text)
    T_days=72.0,
    perfect_minus=0.109,  # fraction of perfect full-length (-) reads, NNN pool
    perfect_plus=0.434,   # fraction of perfect full-length (+) reads, defined substrates
    fid_minus=0.941,      # per-nt fidelity of (-) synthesis
    primer_nM=8.0, template_nM=8.0, ribozyme_nM=80.0,   # Fig 4 legend
    k_decay_per_day=0.0059,  # SI fig S8, t1/2 ~117 d (50 mM MgCl2, pH 9, -7 C frozen; NOT the 0.4 mM Mg replication buffer)
    HH_yield_defined=0.0188, HH_yield_NNN=0.0039, HH_days=65.0,
)
r = {'inputs': P}

# 1. second-hand "0.02%" check: yield per template vs per ribozyme molecule
r['copies_per_template_72d_minus'] = P['Y_minus']
r['copies_per_ribozyme_72d_minus'] = P['Y_minus'] * P['template_nM'] / P['ribozyme_nM']
r['copies_per_ribozyme_72d_plus'] = P['Y_plus'] * P['template_nM'] / P['ribozyme_nM']

# 2. survival of RNA over one 72-d reaction and one full (+ -> - -> +) cycle
S72 = np.exp(-P['k_decay_per_day'] * P['T_days'])
r['survival_72d'] = S72
r['survival_cycle_144d'] = S72 ** 2


def growth_factor(Yp, Ym, S):
    """leading eigenvalue of x+' = S(x+ + Yp x-), x-' = S(x- + Ym x+) per 72-d step"""
    M = S * np.array([[1.0, Yp], [Ym, 1.0]])
    return float(np.max(np.real(np.linalg.eigvals(M))))


lam = growth_factor(P['Y_plus'], P['Y_minus'], S72)
r['lambda_per_72d_any_fulllength'] = lam
r['lambda_per_cycle_144d_any_fulllength'] = lam ** 2
lam_perfect = growth_factor(P['Y_plus'] * P['perfect_plus'], P['Y_minus'] * P['perfect_minus'], S72)
r['lambda_per_cycle_144d_perfect_copies'] = lam_perfect ** 2
lam_nodecay = growth_factor(P['Y_plus'], P['Y_minus'], 1.0)
r['lambda_per_cycle_no_decay'] = lam_nodecay ** 2
r['new_plus_per_plus_per_cycle_no_decay'] = P['Y_minus'] * P['Y_plus']
# break-even: geometric-mean yield per 72 d needed for lambda = 1 given decay
r['breakeven_geomean_yield_per_72d'] = 1 / S72 - 1
r['fold_improvement_needed'] = r['breakeven_geomean_yield_per_72d'] / np.sqrt(P['Y_plus'] * P['Y_minus'])
# per-day rates
r['synthesis_rate_per_day_geomean'] = np.sqrt(P['Y_plus'] * P['Y_minus']) / P['T_days']
r['decay_to_synthesis_ratio'] = P['k_decay_per_day'] / r['synthesis_rate_per_day_geomean']
# sensitivity to decay rate (replication buffer has 0.4 mM Mg, likely slower hydrolysis than the 50 mM assay)
sens = {}
for th in [117, 234, 500, 1000, 5000, 1e9]:
    S = np.exp(-np.log(2) / th * P['T_days'])
    sens[str(th)] = dict(lambda_cycle=growth_factor(P['Y_plus'], P['Y_minus'], S) ** 2,
                         breakeven_yield=1 / S - 1)
r['sensitivity_half_life_days'] = sens
# half-life at which lambda=1 (decay balanced by synthesis)
g = np.sqrt(P['Y_plus'] * P['Y_minus'])
r['halflife_needed_for_lambda1_days'] = float(np.log(2) * P['T_days'] / np.log(1 + g))

# 3. Eigen error threshold numbers stated in SI fig S32 (recomputed): L = -ln(s)/ln(q) -> s_min = q^-L
L, q = 84, P['fid_minus']
r['eigen_s_min_recomputed'] = float(q ** (-L))
r['perfect_genome_copy_prob_q^L'] = float(q ** L)

# ---- planted check: simulate the 2-strand linear model as an ODE with known rates and recover lambda
pl = {}
for Yp, Ym, k in [(0.0017, 0.0024, 0.0059), (0.3, 0.5, 0.001), (0.9, 0.7, 0.0059)]:
    # continuous-time: dx+/dt = c_p x- - k x+, dx-/dt = c_m x+ - k x-; choose c so that over 72 d with no decay
    # the discrete yield equals Y (first order in small Y); recover lambda numerically and compare to the matrix formula
    c_p, c_m = Yp / 72, Ym / 72
    sol = solve_ivp(lambda t, x: [c_p * x[1] - k * x[0], c_m * x[0] - k * x[1]], [0, 72 * 20], [1.0, 1.0],
                    t_eval=[72 * 19, 72 * 20], rtol=1e-10, atol=1e-14)
    ode_lam = float((sol.y[0, 1] + sol.y[1, 1]) / (sol.y[0, 0] + sol.y[1, 0]))
    exact = float(np.exp((np.sqrt(c_p * c_m) - k) * 72))
    pl[f'Yp{Yp}_Ym{Ym}_k{k}'] = dict(ode_lambda_72d=ode_lam, analytic_lambda_72d=exact,
                                      matrix_formula=growth_factor(Yp, Ym, np.exp(-k * 72)),
                                      rel_err_ode_vs_analytic=abs(ode_lam - exact) / exact)
r['planted_check'] = pl
r['planted_pass'] = all(v['rel_err_ode_vs_analytic'] < 1e-4 for v in pl.values())
json.dump(r, open(os.path.join(OUT, 'results_calc.json'), 'w'), indent=1, default=float)
print(json.dumps(r, indent=1, default=float))
