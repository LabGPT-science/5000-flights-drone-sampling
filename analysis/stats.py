"""Recompute every number quoted in the talk from the raw files. Writes figures/talk_numbers.json."""
import csv, json
from collections import defaultdict
import numpy as np
from config import SIM_RUNS, PROSPERA, FIGURES, SCENARIOS

ev = defaultdict(list)
for r in csv.DictReader(open(SIM_RUNS / "sample_events.csv")):
    ev[r["scenario"]].append(float(r["miss_m"]))
runs = list(csv.DictReader(open(SIM_RUNS / "runs_summary.csv")))
out = {"scenarios": {}}
for sc, label in SCENARIOS:
    m = np.array(ev[sc]); rr = [r for r in runs if r["scenario"] == sc]
    out["scenarios"][sc] = {
        "label": label,
        "missions": len(rr),
        "samples_possible": 8 * sum(r["no_go_wind_ge_12ms"] == "false" for r in rr),
        "samples_collected": int(len(m)),
        "missions_timed_out_600s": sum(r["timed_out_600s"] == "true" for r in rr),
        "miss_median_m": round(float(np.median(m)), 4) if len(m) else None,
        "miss_p95_m": round(float(np.percentile(m, 95)), 4) if len(m) else None,
        "path_error_mean_m_median_run": round(float(np.median([float(r["xte_mean_m"]) for r in rr])), 3),
    }
fl = list(csv.DictReader(open(PROSPERA / "flights.csv")))
t = np.array([float(r["water_1L_time_s"]) for r in fl]) / 60
w = np.array([float(r["wind_ms"]) for r in fl])
out["prospera_flights"] = {
    "n": len(fl),
    "round_trip_min_median": round(float(np.median(t)), 2),
    "round_trip_min_p5_p95": [round(float(np.percentile(t, 5)), 2), round(float(np.percentile(t, 95)), 2)],
    "wind_ms_median_modelled": round(float(np.median(w)), 2),
    "share_within_12ms_rating": round(float(np.mean(w < 12)), 3),
}
json.dump(out, open(FIGURES / "talk_numbers.json", "w"), indent=2)
print(json.dumps(out, indent=2))
