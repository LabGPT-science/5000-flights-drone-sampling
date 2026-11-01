# Methods

## 1. Survey simulation (`sim_runs_2026-10-24`)

The same survey mission was flown 1,000 times in each of five scenarios using LabGPT's in-browser drone simulator (seeded physics, time step 0.02 s, track logged at 1 Hz).

**Mission.** 4 survey lines, 120 m long and 30 m apart; 16 waypoints, of which 8 are sample points (2 per line); flown 30 m above ground; centred on the Próspera site centroid (Roatán, Honduras). Arrival radius 0.5 m, 3 s hover at each sample, 600 s timeout.

**Scenarios.**

| ID | Positioning the drone steers by | Wind |
|---|---|---|
| S1 | RTK GNSS, σ 0.025 m | None |
| S2 | Drone GNSS, σ 0.75 m (DJI ±1.5 m hover specification taken as about 2σ) | None |
| S3 | Handheld-grade GPS, open sky, σ 3 m | None |
| S4 | Handheld-grade GPS, under canopy, σ 15 m | None |
| S5 | RTK GNSS, σ 0.025 m | Roatán: speed per mission from a Weibull distribution (k = 2) with the 11 kt (5.66 m/s) Windfinder mean, from ENE (67.5° ± 30°), gust σ 2.6 m/s; missions at ≥ 12 m/s marked no-go |

S3 and S4 put handheld-grade GPS error on the same drone. They are a proxy for where a person with a handheld GPS believes a sample point is; they do not model how a person walks or chooses a spot.

**Why S4 collected 3,323 of 8,000 samples.** With σ 15 m GPS error the drone often never registers arriving within the 0.5 m arrival radius, so every S4 mission reached the 600 s timeout before visiting all points.

## 2. Próspera flight model (`simulation/prospera_sim.py`)

A Monte Carlo model of 5,000 out-and-back flights from an edge lab at the centroid of the 184.6-acre Próspera polygon to random sample points inside it. Reference airframe: DJI Matrice 350 RTK published specifications. Wind per flight is drawn from a Weibull model (k = 2) of the Windfinder record for Roatán International Airport (2008–2026, mean 11 kt, ENE). Every input in `CONFIG` is labelled as sourced or as a model choice.

## 3. Literature comparison (`data/literature`)

Published human field-positioning errors (USGS handheld GPS accuracy; Japan National Forest Inventory plot relocation; University of Ljubljana study of Slovenian permanent plots), redrawn as a chart rather than reproducing the original figures.

## Limitations

- These are simulations, not field measurements.
- Ground is flat in batch mode; terrain is not modelled.
- The simulator's canopy factor is not used by the physics; S4 uses the handheld-under-canopy GPS preset instead.
- The simulator autopilot is proportional-only, with no wind compensation, so in S5 missions stall above about 3 m/s wind. Production flight controllers compensate for wind (DJI specifies ±0.1 m RTK hover in moderate wind).
- Battery figures in the survey simulation use the simulator's simple model, not the reference-airframe energy model.
- Wind distribution shape, gust σ and the S2 GNSS σ are model choices, not measured values.
