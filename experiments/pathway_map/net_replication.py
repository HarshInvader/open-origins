"""Task #18: is net replication above or below 1 per cycle under each paper's own conditions?

Every input number is quoted from the source (section in comments). The model is ours and simple:
two strands copy each other at first-order rates k+ and k- (per template) and decay at kdeg, so the
population grows as exp(r t) with r = sqrt(k+ k-) - kdeg. Yields are converted to rates as
k = yield / time (valid while yield << 1). Updates results.json (run after score_map.py).
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --- Gianni et al. 2026, Science, 10.1126/science.adt2760 (abstract; Results "self-synthesis"; Fig. 4 legend)
QT = dict(
    days=72.0,
    y_minus=0.0024,       # QT45(-) full-length, all 64 triplets: "yield: 0.24% after 72 days"
    y_plus=0.0017,        # QT45(+) full-length, defined triplets + one hexamer: "yield: 0.17%, in 72 days"
    perfect_minus=0.109,  # "10.9% perfect full-length (-) strand sequences" (NNN pool), fidelity 94.1%/nt
    perfect_plus=0.434,   # "43.4% of perfect full-length QT45 (+) products" (defined substrates)
    half_life_days=117.0, # "half-life of ~117 days in standard reaction conditions (fig. S8)" - conditions not read
    temp_c=-7.0, ph=9.0,
)

# --- Attwater et al. 2025, Nat Chem, 10.1038/s41557-025-01830-y (Results; Fig. 3 legend; Methods)
AT = dict(
    cycle_hours=24.0,  # Methods: HCl, 80 C 2 min, KOH, flash-freeze, -7 C ~24 h
    fitc_exponent=0.38, cy5_exponent=0.20,           # Fig. 3e fits: e^0.38x, e^0.20x (emergent clone, no dilution)
    emergent_per_cycle=[1.37, 1.30, 1.27],          # +8, +11, +14 nt classes, "apparent exponents"
    plus14_per_cycle=[1.20, 1.38],                  # (+)/(-) of the +14-nt sequence, 4-cycle growth then plateau
    fragment_29nt_max_per_cycle=1.26,               # gamma fragment of the TPR ribozyme, "up to 1.26-fold per cycle"
    AD_fold=[9.0, 31.0], AD_cycles=21,              # A_D duplex: 9x (A+), 31x (A-) over 21 cycles after dilution correction
)


def qt45():
    t = QT["days"]
    kp, km = QT["y_plus"] / t, QT["y_minus"] / t
    kdeg = math.log(2) / QT["half_life_days"]
    ksyn = math.sqrt(kp * km)
    r = ksyn - kdeg
    kp_f, km_f = kp * QT["perfect_plus"], km * QT["perfect_minus"]
    ksyn_f = math.sqrt(kp_f * km_f)
    r_f = ksyn_f - kdeg
    # correction: ribozyme decays during the 72 days, so the endpoint yield underestimates the
    # initial rate by the mean surviving fraction (1-exp(-kdeg t))/(kdeg t)
    mean_active = (1 - math.exp(-kdeg * t)) / (kdeg * t)
    ksyn_c = ksyn / mean_active
    return dict(
        conditions="eutectic ice -7 C, pH 9 (CHES-KOH), 0.4 mM MgCl2, 1.2 mM KCl, 8 nM template, 80 nM ribozyme, 50 nM each triplet; (+) and (-) synthesised in separate tubes",
        gross_synthesis_factor_per_72d=math.exp(ksyn * t),
        survival_per_72d=math.exp(-kdeg * t),
        net_factor_per_72d=math.exp(r * t),
        net_factor_per_72d_functional_only=math.exp(r_f * t),
        net_factor_per_72d_rate_corrected_for_ribozyme_decay=math.exp((ksyn_c - kdeg) * t),
        synthesis_rate_per_day=ksyn, decay_rate_per_day=kdeg,
        fold_rate_increase_needed=kdeg / ksyn,
        fold_rate_increase_needed_functional_only=kdeg / ksyn_f,
        doubling_time_years_if_no_decay=math.log(2) / ksyn / 365.25,
        verdict="below 1",
        caveats=["half-life measured in 'standard reaction conditions' (fig. S8, not read); the low-Mg self-synthesis buffer may differ",
                 "yields are 72-day endpoints, so rates are averages; the decay correction changes the gap by ~1.2x",
                 "(+) synthesis needed a pre-made hexamer and defined triplets; (-) used all 64 triplets",
                 "no cycling: these are single 72-day incubations, so 'cycle' = 72 days"],
    )


def attwater():
    ad = [f ** (1 / AT["AD_cycles"]) for f in AT["AD_fold"]]
    short = [math.exp(AT["fitc_exponent"]), math.exp(AT["cy5_exponent"])] + AT["emergent_per_cycle"] + AT["plus14_per_cycle"]
    return dict(
        conditions="pH-freeze-thaw cycles (~1 per day): +HCl, 80 C 2 min, +KOH, -7 C ~24 h; 0.4 mM MgCl2, 1.8 mM KCl, pH 9; 20 nM TPR ribozyme, 100 nM each triplet; twofold dilution into fresh ribozyme and substrates every 4th cycle",
        short_templates_per_cycle_range=[min(short), max(short)],
        AD_duplex_per_cycle=ad,
        ribozyme_fragment_29nt_per_cycle_max=AT["fragment_29nt_max_per_cycle"],
        whole_replicase_per_cycle=None,
        verdict=("above 1 for short templates (1.11-1.46 per cycle) and a 29-nt ribozyme fragment (up to 1.26), "
                 "with fresh ribozyme supplied; not measured for the whole ribozyme, which is supplied, not copied"),
    )


def main():
    out = dict(task=18, qt45=qt45(), attwater2025=attwater(),
               sources={"qt45": "10.1126/science.adt2760", "attwater2025": "10.1038/s41557-025-01830-y"})
    p = HERE / "results.json"
    res = json.loads(p.read_text()) if p.exists() else {}
    res["net_replication"] = out
    if 18 not in res.get("task", []):
        res["task"] = res.get("task", []) + [18]
    p.write_text(json.dumps(res, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
