# Data

All distances are in metres, times in seconds, wind in metres per second, unless stated. Coordinates `east_m` / `north_m` are local metres: from mission waypoint 0 for the survey simulation, and from the site centre for the Próspera flight model. Exact geographic coordinates are not published.

## Inventory

| Path | Rows | Produced by | Status |
|---|---|---|---|
| `literature/human_positioning_error.csv` | 4 | Summarised from published sources | Included |
| `raw/sim_runs_2026-10-24/mission_waypoints.csv` | 16 | Simulator grid generator | Included |
| `raw/sim_runs_2026-10-24/runs_summary.csv` | 5,000 | Survey simulator, one row per mission | Included |
| `raw/sim_runs_2026-10-24/sample_events.csv` | 29,679 | Survey simulator, one row per collected sample | Included |
| `raw/sim_runs_2026-10-24/tracks_1Hz_<scenario>[_partN].csv.gz` | 1,954,691 total | Survey simulator, track logged at 1 Hz (gzip-compressed CSV). S4 is split into 3 parts and S5 into 2 parts by run_id; every part has a header row | Included |
| `raw/prospera_sim/flights.csv` | 5,000 | `simulation/prospera_sim.py` (seed 51) | Included (the script regenerates it exactly) |
| `raw/prospera_sim/summary.json` | – | `simulation/prospera_sim.py` | Included |

Scenario IDs: `S1_RTK_calm`, `S2_droneGNSS_calm`, `S3_handheldGPSopen_calm`, `S4_handheldGPScanopy_calm`, `S5_RTK_RoatanWind`. Each scenario has 1,000 missions; `run_id` 0–999 is S1, 1000–1999 S2, and so on.

## Column definitions

### `mission_waypoints.csv`
| Column | Meaning |
|---|---|
| `wp_idx` | Waypoint index, 0–15 |
| `type` | `Sample` (hover and collect) or `Pass` (turn point) |
| `name` | Waypoint label |
| `east_m`, `north_m` | Planned position |
| `alt_m` | Planned altitude above the simulator's reference (ground fixed at 25 m; flown 30 m above ground) |

### `runs_summary.csv`
| Column | Meaning |
|---|---|
| `run_id`, `scenario`, `seed` | Mission identifier, scenario, random seed (runs are exactly reproducible from the seed) |
| `wind_ms`, `wind_from_deg`, `gust_std_ms` | Mean wind speed, direction it blows from, gust standard deviation |
| `gps_h_std_m`, `gps_v_std_m`, `gps_tau_s` | Horizontal and vertical GPS error standard deviation, and error correlation time |
| `no_go_wind_ge_12ms` | `true` if wind ≥ 12 m/s (drone's rating), mission not flown |
| `timed_out_600s` | `true` if the mission hit the 600 s timeout |
| `duration_s`, `path_length_m`, `battery_used_pct` | Mission duration, distance flown, battery used |
| `samples_collected_of_8` | Samples collected out of 8 planned |
| `miss_mean_m`, `miss_max_m` | Mean and maximum distance between actual and planned sample position |
| `xte_mean_m`, `xte_p95_m`, `xte_max_m` | Path (cross-track) error: mean, 95th percentile, maximum |

### `sample_events.csv`
| Column | Meaning |
|---|---|
| `run_id`, `scenario`, `seed` | As above |
| `wp_idx`, `sample_no` | Waypoint index and sample number (1–8) |
| `planned_east_m`, `planned_north_m` | Planned sample position |
| `actual_east_m`, `actual_north_m`, `actual_alt_m` | True position of the drone when the sample was taken |
| `miss_m` | Horizontal distance between actual and planned position |
| `battery_pct` | Battery remaining at the sample |
| `wind_ms` | Mission mean wind |
| `gps_h_std_m` | Horizontal GPS error standard deviation for the scenario |

### `tracks_1Hz_<scenario>.csv.gz`
Gzip-compressed CSV; read with `pandas.read_csv(path)` or Python `gzip.open(path, "rt")`.

| Column | Meaning |
|---|---|
| `run_id`, `scenario`, `seed`, `t_s` | Mission, scenario, seed, simulation time |
| `true_east_m`, `true_north_m`, `true_alt_m` | True drone position |
| `est_east_m`, `est_north_m`, `est_alt_m` | Position as estimated by the drone's GPS |
| `gps_err_m` | Distance between true and estimated position |
| `speed_ms`, `battery_pct` | Ground speed, battery remaining |

### `prospera_sim/flights.csv`
| Column | Meaning |
|---|---|
| `flight` | Flight number, 1–5,000 |
| `east_m`, `north_m`, `one_way_m` | Sample point relative to the edge lab at the site centroid, and one-way distance |
| `wind_ms`, `gust_ms_est`, `wind_from_deg` | Wind drawn for the flight (Weibull model of the Windfinder record) and estimated gust |
| `go_sustained_rule`, `go_gust_rule` | Whether the flight can go under the sustained-wind rule (< 12 m/s) or the strict gust rule |
| `<payload>_time_s` | Round-trip flight time including take-off, transit, hover and sampling, for each payload scenario |
| `<payload>_energy_Wh`, `<payload>_batt_pct` | Energy and battery share used |
| `<payload>_within_mtow` | Whether the payload keeps the drone under its maximum take-off weight |
| `rtk_sample_offset_m`, `gnss_sample_offset_m` | Simulated sample position error with RTK and standard GNSS |

Payload scenarios: `water_1L`, `eDNA_2L`, `soil_200g_tool0.5`, `soil_200g_tool1.0`.

### `literature/human_positioning_error.csv`
| Column | Meaning |
|---|---|
| `label`, `source` | What was measured and by whom |
| `low_m`, `high_m` | Reported value or range |
| `kind` | `range`, `mean`, or `lower_bound` |
| `note` | Context |
