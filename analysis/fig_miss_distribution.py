"""Figure: distribution of sample miss distance per positioning scenario (S1–S4).

Input:  data/raw/sim_runs_2026-10-24/sample_events.csv
Output: figures/miss_distribution.png
"""
import csv
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter, FixedLocator
from config import SIM_RUNS, FIGURES, SCENARIOS, GREEN, DARK_GREEN, INK, GREY

miss = defaultdict(list)
with open(SIM_RUNS / "sample_events.csv") as f:
    for r in csv.DictReader(f):
        miss[r["scenario"]].append(float(r["miss_m"]))

order = SCENARIOS[:4]
fig, ax = plt.subplots(figsize=(8.2, 5.4), dpi=200)
data = [np.log10(np.array(miss[k])) for k, _ in order]
vp = ax.violinplot(data, positions=range(1, 5), widths=0.8, showextrema=False)
for b in vp["bodies"]:
    b.set_facecolor(GREEN); b.set_edgecolor(DARK_GREEN); b.set_alpha(0.55)
for i, (k, _) in enumerate(order):
    a = np.array(miss[k]); med = np.median(a)
    ax.scatter([i + 1], [np.log10(med)], s=60, c=INK, zorder=3)
    lab = f"{med*100:.0f} cm" if med < 1 else f"{med:.1f} m"
    ax.text(i + 1.12, np.log10(med), f"median {lab}", va="center", fontsize=10, color=INK)
    ax.text(i + 1, np.log10(a.max()) + 0.18, f"n = {len(a):,}", ha="center", fontsize=9, color=GREY)
ticks = [0.001, 0.01, 0.1, 1, 10, 100]
ax.yaxis.set_major_locator(FixedLocator(np.log10(ticks)))
ax.yaxis.set_major_formatter(FixedFormatter(["1 mm", "1 cm", "10 cm", "1 m", "10 m", "100 m"]))
ax.set_ylim(-3.2, 2.3)
ax.set_xticks(range(1, 5)); ax.set_xticklabels([l.replace(", ", ",\n") for _, l in order], fontsize=10)
ax.set_xlabel("Positioning the drone steers by", fontsize=12, labelpad=8)
ax.set_ylabel("Distance from planned sample point", fontsize=12)
ax.grid(axis="y", color="#E3E8E5"); ax.set_axisbelow(True)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(FIGURES / "miss_distribution.png", facecolor="white")
print("wrote figures/miss_distribution.png")
