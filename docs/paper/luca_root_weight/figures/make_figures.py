"""Figures 1-3 for the LUCA root-weight preprint, from results/realdata/realdata_v7.json (prereg v7).

Usage: python -I make_figures.py <luca_calib results/realdata dir> <out dir>
"""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RD, OUT = sys.argv[1], sys.argv[2]
r = json.load(open(f"{RD}/realdata_v7.json"))
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
N = 1399
plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                     "axes.spines.right": False, "lines.linewidth": 2, "legend.frameon": False})
w_hat = r["w_hat_median"]

def mark_what(ax, label=True):
    ax.axvline(w_hat, color=INK2, lw=1, ls=(0, (3, 2)))
    if label:
        ax.text(w_hat * 1.15, ax.get_ylim()[1] * 0.96, "fitted $\\hat w$", color=INK2, va="top", fontsize=7.5)

def share_axis(ax):
    top = ax.secondary_xaxis("top", functions=(lambda w: w, lambda w: w))
    ticks = [0.001, 0.01, 0.1, 0.5, 0.9]
    top.set_xticks([s * (N - 1) / (1 - s) for s in ticks])
    top.set_xticklabels([f"{s:g}" for s in ticks])
    top.set_xlabel("prior share of originations at the root, $w/(w+N-1)$", color=INK2)
    top.tick_params(colors=INK2)

# ---- Figure 1: dose response ----
d = r["dose"]
w = np.array([x["w"] for x in d])
fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.9), constrained_layout=True)
a.fill_between(w, [x["sum_pp_min_run"] for x in d], [x["sum_pp_max_run"] for x in d], color=C1, alpha=0.2, lw=0)
a.plot(w, [x["sum_pp_median_run"] for x in d], color=C1, label="sum of PPs")
a.plot(w, [x["n_pp_ge_0.5_median_run"] for x in d], color=C2, label="families with PP ≥ 0.5")
a.set_xscale("log"); a.set_xlabel("root weight $w$"); a.set_ylabel("LUCA gene families (KOs)")
a.set_xlim(1, 1e5); a.set_ylim(0, 7456); a.grid(axis="y", color=GRID, lw=0.6)
a.axhline(7456, color=INK2, lw=0.8); a.text(1.2, 7300, "all 7,456 scored families", color=INK2, va="top", fontsize=7.5)
mark_what(a, label=False); a.legend(loc="center left", bbox_to_anchor=(0.0, 0.62))
share_axis(a); a.set_title("a", loc="left", fontweight="bold")
lo = r["loess"]["dose"]
wl = [x["w"] for x in lo if x["proteins"]]; pl = [x["proteins"] for x in lo if x["proteins"]]
b.plot(wl, pl, color=C1, marker="o", ms=4, lw=1.5)
b.set_xscale("log"); b.set_xlim(1, 1e5); b.set_ylim(0, 12000)
b.set_xlabel("root weight $w$"); b.set_ylabel("predicted LUCA proteins (LOESS)")
b.grid(axis="y", color=GRID, lw=0.6); mark_what(b)
b.text(1.2, 1500, "below the smallest\nmodern genome\n(161 KOs): not\npredicted", color=INK2, fontsize=7)
share_axis(b); b.set_title("b", loc="left", fontweight="bold")
fig.savefig(f"{OUT}/fig1_dose.pdf"); fig.savefig(f"{OUT}/fig1_dose.png", dpi=200)

# ---- Figure 2: Bayes factors ----
real = np.load(f"{RD}/real_log10_bf.npy")
sims = json.load(open(f"{RD}/sim_log10_bf.json"))
sl = np.array([x for s in sims.values() for x, t in s if t == 1])
sn = np.array([x for s in sims.values() for x, t in s if t == 0])
bins = np.linspace(-4, 6, 51)
fig, ax = plt.subplots(figsize=(4.6, 3.1), constrained_layout=True)
for v, c, lab in ((sn, C2, "simulated, did not originate at root"),
                  (sl, C3, "simulated, originated at root"),
                  (real, C1, "real families")):
    below = (v < -4).mean()
    h, _ = np.histogram(v[(v >= -4) & (v <= 6)], bins=bins)
    h = np.append(h, (v > 6).sum())
    ax.stairs(h[:-1] / len(v) / np.diff(bins), bins, color=c, lw=2,
              label=f"{lab} (n = {len(v):,}; {below:.0%} below $-4$)")
t = r["bf"]["pooled_log10_bf_star"]
ax.axvline(t, color=INK2, lw=1, ls=(0, (3, 2)))
ax.set_xlabel("log$_{10}$ Bayes factor for origination at the root, $r(N-1)$")
ax.set_ylabel("share of families per unit"); ax.set_xlim(-4, 6); ax.grid(axis="y", color=GRID, lw=0.6)
ax.set_ylim(0, ax.get_ylim()[1] * 1.45)
ax.text(t + 0.12, ax.get_ylim()[1] * 0.62, "threshold", color=INK2, fontsize=7.5)
ax.legend(loc="upper left", fontsize=6.8)
fig.savefig(f"{OUT}/fig2_bf.pdf"); fig.savefig(f"{OUT}/fig2_bf.png", dpi=200)

# ---- Figure 3: controls ----
cv = np.array(r["controls"]["curve"])
c = r["controls"]
fig, ax = plt.subplots(figsize=(4.6, 2.9), constrained_layout=True)
ax.axhspan(0.9, 1.0, color=C1, alpha=0.08, lw=0); ax.axhspan(0, 0.1, color=C2, alpha=0.08, lw=0)
ax.plot(cv[:, 0], cv[:, 1], color=C1, label=f"ribosome and tRNA-charging families, universal (n = {c['n_pos']})")
ax.plot(cv[:, 0], cv[:, 2], color=C2, label=f"photosystem I and II families (n = {c['n_neg']})")
ax.set_xscale("log"); ax.set_xlim(1e-1, 1e7); ax.set_ylim(0, 1)
ax.set_xlabel("root weight $w$"); ax.set_ylabel("mean PP of the set")
ax.grid(axis="y", color=GRID, lw=0.6); mark_what(ax, label=False)
ax.text(w_hat * 1.15, 0.5, "fitted $\\hat w$", color=INK2, fontsize=7.5)
ax.legend(loc="upper left", fontsize=7)
share_axis(ax)
fig.savefig(f"{OUT}/fig3_controls.pdf"); fig.savefig(f"{OUT}/fig3_controls.png", dpi=200)
print("ok")
