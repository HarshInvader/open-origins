"""T3 rate-law gate. Reads NO field data.

Implements the Li & Breaker (1999) RNA cleavage rate law as reproduced in two
open-access papers, and checks it against numbers printed in those papers.

  Wayment-Steele et al. 2021, NAR 49:10604, doi:10.1093/nar/gkab764 (PMC8499941), Methods + Table 1
  Schwintek et al. 2025, eLife, doi:10.7554/eLife.100152 (PMC12240584), Appendix 8, Eq. 19

k_bond [1/min] = k_bg * 10^(0.983 (pH-6)) * 10^(-0.24 (3.16-[K+])) * 10^(0.07 (T-23))
                 * [ 69.3 [Mg]^0.80 * 3.57 [K+]^-0.419 ]      (Mg term omitted when [Mg] = 0)
k_bg = 1.30e-9 1/min; concentrations in M; T in deg C.
"""
import math

K_BG = 1.30e-9  # 1/min, reference point pH 6, 23 C, [K+] = 3.17 M (Wayment-Steele Methods)


def k_bond(pH, T, K, Mg, mg_term="ws"):
    """Per-linkage cleavage rate constant, 1/min.
    mg_term: 'ws'  = omit the Mg and K power terms when Mg == 0 (Wayment-Steele rule)
             'none'= always omit them
    """
    k = K_BG * 10 ** (0.983 * (pH - 6)) * 10 ** (-0.24 * (3.16 - K)) * 10 ** (0.07 * (T - 23))
    if mg_term == "ws" and Mg > 0:
        k *= 69.3 * Mg ** 0.80 * 3.57 * K ** -0.419
    return k


def main():
    print("Gate A: Wayment-Steele 2021 Table 1 (0.14 M K+, AUP 0.4; k_deg = L * AUP * k_bond)")
    rows = [  # label, T, pH, Mg (M), L, printed k_deg (1e-7 /min), printed half-life (days)
        ("cold chain", 5, 7.4, 0.0, 4000, 5.1, 941),
        ("cold chain SAM", 5, 7.4, 0.0, 12000, 15.3, 314),
        ("pKa shifted", 5, 9.4, 0.0, 4000, 470, 10.2),
        ("temperature excursion", 37, 7.4, 0.0, 4000, 890, 5.4),
        ("in vitro transcription", 37, 7.6, 0.014, 4000, 57000, 0.084),
        ("physiological", 37, 7.4, 0.001, 4000, 2000, 2.4),
    ]
    worst = 0.0
    n_ok = 0
    for lab, T, pH, Mg, L, kp, hp in rows:
        k = L * 0.4 * k_bond(pH, T, 0.14, Mg)
        half = math.log(2) / k / 60 / 24
        rel = k / (kp * 1e-7) - 1
        worst = max(worst, abs(rel))
        n_ok += abs(rel) < 0.05
        print(f"  {lab:24s} ours {k/1e-7:10.1f} printed {kp:8.1f} (x1e-7/min) rel {rel:+.3f} | half-life {half:8.3f} d printed {hp}")
    print(f"  rows within 5%: {n_ok} of {len(rows)}; worst relative difference {worst:.3f}")
    print("  The in-vitro-transcription row (14 mM Mg) is not reproduced from the printed inputs (ours is 2.2x lower).")

    print("\nGate B: eLife 2025 Appendix 8 (24-mer, 45 C, pH 7; printed 8.91703e-6 /min at 200 uM Mg; 3.231e-5 at 1 mM)")
    for K in (0.004, 0.008, 0.012):
        a = 24 * k_bond(7, 45, K, 200e-6)
        b = 24 * k_bond(7, 45, K, 1e-3)
        print(f"  monovalent {K*1e3:4.0f} mM: 200 uM Mg -> {a:.3e} /min ; 1 mM Mg -> {b:.3e} /min")
    print("  The paper does not print the K+ value it used. K+ = 1 mM reproduces both printed rates:")
    print(f"  monovalent    1 mM: 200 uM Mg -> {24*k_bond(7,45,0.001,200e-6):.3e} /min ; 1 mM Mg -> {24*k_bond(7,45,0.001,1e-3):.3e} /min")

    print("\nWhere the law misbehaves (not a result; reasons for fixed decisions):")
    for K in (0.001, 0.01, 0.14, 1.0):
        mg_x = (1 / (69.3 * 3.57 * K ** -0.419)) ** (1 / 0.8)
        print(f"  K+ = {K:5.3f} M: Mg term < 1 (law predicts Mg SLOWS cleavage) below Mg = {mg_x*1e3:.3f} mM")
    print("  K+ -> 0 with Mg > 0: K^-0.419 diverges (rate -> infinity).")
    print("  T term: one decade per 14.3 C, no upper limit in the formula.")


if __name__ == "__main__":
    main()
