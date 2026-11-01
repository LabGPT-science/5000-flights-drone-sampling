"""Figure: mean samples collected per mission (of 8) by wind speed, scenario S5 (RTK + Roatán wind).

Input:  data/raw/sim_runs_2026-10-24/runs_summary.csv
Output: figures/wind_samples.png
"""
import csv
import numpy as np
import matplotlib.pyplot as plt
from config import SIM_RUNS, FIGURES, GREEN, INK

bins = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 8)]
rows = [r for r in csv.DictReader(open(SIM_RUNS / "runs_summary.csv")) if r["scenario"] == "S5_RTK_RoatanWind"]
means = []
for lo, hi in bins:
    v = [int(r["samples_collected_of_8"]) for r in rows if lo <= float(r["wind_ms"]) < hi and r["no_go_wind_ge_12ms"] == "false"]
    means.append(np.mean(v) if v else 0)
fig, ax = plt.subplots(figsize=(6.6, 4.3), dpi=200)
labels = [f"{lo}–{hi}" for lo, hi in bins]
ax.bar(labels, means, color=GREEN)
for i, m in enumerate(means):
    ax.text(i, m + 0.15, f"{m:.1f}", ha="center", fontsize=10, color=INK)
ax.set_ylim(0, 9)
ax.set_xlabel("Wind speed (m/s)", fontsize=12); ax.set_ylabel("Samples collected per mission (of 8)", fontsize=12)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(FIGURES / "wind_samples.png", facecolor="white")
print("wrote figures/wind_samples.png", dict(zip(labels, np.round(means, 2))))
