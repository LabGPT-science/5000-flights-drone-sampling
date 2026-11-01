"""Figure: reported human field-positioning error, redrawn from published sources.

Input:  data/literature/human_positioning_error.csv
Output: figures/human_positioning_error.png
"""
import csv
import matplotlib.pyplot as plt
from config import LITERATURE, FIGURES, DARK_GREEN, AMBER

rows = list(csv.DictReader(open(LITERATURE / "human_positioning_error.csv")))
fig, ax = plt.subplots(figsize=(9.5, 3.3), dpi=200)
for i, r in enumerate(rows):
    y = len(rows) - 1 - i
    lo = float(r["low_m"])
    if r["kind"] == "range":
        hi = float(r["high_m"]); ax.plot([lo, hi], [y, y], lw=12, c=DARK_GREEN, solid_capstyle="butt")
        ax.text(hi + 1, y, f"{lo:g}–{hi:g} m", fontsize=11, va="center")
    elif r["kind"] == "mean":
        ax.scatter([lo], [y], s=110, c=AMBER, zorder=3); ax.text(lo + 1, y + 0.22, f"{lo:g} m", fontsize=11)
    else:
        ax.annotate("", xy=(40, y), xytext=(lo, y), arrowprops=dict(arrowstyle="->", color=AMBER, lw=3))
        ax.scatter([lo], [y], s=60, c=AMBER); ax.text(lo + 1, y + 0.22, "> 20 m (60% of plots)", fontsize=11)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([f'{r["label"]} ({r["source"]})' for r in rows][::-1], fontsize=11)
ax.set_xlim(0, 42); ax.set_ylim(-0.6, len(rows) - 0.4)
ax.set_xlabel("Recorded vs. actual sampling location (m)", fontsize=11)
ax.grid(axis="x", color="#E3E8E5"); ax.set_axisbelow(True)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(FIGURES / "human_positioning_error.png", facecolor="white", bbox_inches="tight", pad_inches=0.1)
print("wrote figures/human_positioning_error.png")
