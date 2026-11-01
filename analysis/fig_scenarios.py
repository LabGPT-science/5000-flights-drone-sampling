"""Figure: one panel per scenario showing planned route, one flown mission and every collected sample.

Inputs: data/raw/sim_runs_2026-10-24/{mission_waypoints.csv, sample_events.csv, tracks_1Hz_<scenario>.csv.gz}
Output: figures/scenario_<n>.png (n = 1..5)
"""
import csv
import gzip
from collections import defaultdict
import matplotlib.pyplot as plt
from config import SIM_RUNS, FIGURES, SCENARIOS, GREEN, DARK_GREEN, INK, GREY, AMBER, LIGHT

with open(SIM_RUNS / "mission_waypoints.csv") as f:
    wps = list(csv.DictReader(f))
path = [(float(w["east_m"]), float(w["north_m"])) for w in wps]
planned = [p for p, w in zip(path, wps) if w["type"] == "Sample"]

samples = defaultdict(list)
with open(SIM_RUNS / "sample_events.csv") as f:
    for r in csv.DictReader(f):
        samples[r["scenario"]].append((float(r["actual_east_m"]), float(r["actual_north_m"])))

for k, (sc, label) in enumerate(SCENARIOS):
    example_run = str(k * 1000)  # first run of each scenario
    track = []
    for part in sorted(SIM_RUNS.glob(f"tracks_1Hz_{sc}*.csv.gz")):  # S4 and S5 are split into parts
        with gzip.open(part, "rt") as f:
            track += [(float(r["true_east_m"]), float(r["true_north_m"])) for r in csv.DictReader(f) if r["run_id"] == example_run]
    fig, ax = plt.subplots(figsize=(3.2, 3.6), dpi=220)
    ax.plot(*zip(*path), color=LIGHT, lw=1.2, ls="--", zorder=1)
    if track:
        ax.plot(*zip(*track), color=DARK_GREEN, lw=0.9, alpha=0.8, zorder=2)
    pts = samples[sc]
    if pts:
        ax.scatter(*zip(*pts), s=2, color=GREEN, alpha=0.25, lw=0, zorder=3)
    ax.scatter(*zip(*planned), s=26, facecolors="none", edgecolors=AMBER, lw=1.3, zorder=4)
    ax.set_xlim(-35, 125); ax.set_ylim(-35, 155); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(LIGHT)
    ax.set_title(f"S{k+1} · {label}", fontsize=8.5, color=INK, pad=4)
    ax.text(0.03, 0.02, f"{len(pts):,} samples", transform=ax.transAxes, fontsize=7.5, color=GREY)
    fig.tight_layout(pad=0.3); fig.savefig(FIGURES / f"scenario_{k+1}.png", facecolor="white"); plt.close(fig)
print("wrote figures/scenario_1..5.png")
