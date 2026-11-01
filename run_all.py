"""Regenerate every figure and number used in the talk.

    python run_all.py

Requires the data files described in data/README.md.
"""
import runpy, sys
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parent / "analysis"
sys.path.insert(0, str(ANALYSIS))
for script in ["stats.py", "fig_literature.py", "fig_scenarios.py", "fig_miss_distribution.py", "fig_wind.py", "fig_flight_times.py"]:
    print(f"--- {script}")
    runpy.run_path(str(ANALYSIS / script), run_name="__main__")
