# 5,000 Flights to Answer One Question: Can a Drone Sample as Well as a Human?

Data and analysis behind the LabGPT talk at **Voxel51: Visual AI in Agriculture** (5 November 2026), by Rohan Talwadiya and Alice Chen.

We flew the same drone survey mission 5,000 times in simulation over our field site at Próspera, Roatán, Honduras, changing only the positioning system the drone steers by (RTK GNSS, standard drone GNSS, and handheld-grade GPS in the open and under canopy) and the wind. A second simulation models 5,000 out-and-back sampling flights from an edge lab at the centre of the site.

> **All results in this repository are simulation outputs, not field measurements.** The drone-versus-hand field comparison has been designed but not yet run.

## Status

| Item | Status |
|---|---|
| Analysis code | ✅ Included |
| Simulation code for the Próspera flight model (`simulation/prospera_sim.py`) | ✅ Included |
| Literature values (`data/literature/`) | ✅ Included |
| Simulation outputs (`data/raw/`) | ✅ Included. See [data/README.md](data/README.md) for the file inventory and column definitions |
| Archived release with DOI (Zenodo) | ⏳ Planned |
| Browser simulator used for the survey runs | Not included (proprietary) |

## Reproduce the results

```bash
git clone https://github.com/LabGPT-science/5000-flights-drone-sampling.git
cd 5000-flights-drone-sampling
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Regenerate the Próspera flight-time data (seeded, deterministic)
python simulation/prospera_sim.py

# 2. Regenerate every figure and number used in the talk (uses data/raw/)
python run_all.py
```

`run_all.py` writes all figures to `figures/` and every number quoted in the talk to `figures/talk_numbers.json`. If the data lives elsewhere, set `LABGPT_DATA_DIR` to its folder.

## What each figure shows

| Figure | Script | Talk slide |
|---|---|---|
| `human_positioning_error.png` | `analysis/fig_literature.py` | What a human expedition looks like today |
| `scenario_1.png` … `scenario_5.png` | `analysis/fig_scenarios.py` | The experiment: one mission, 5,000 times |
| `miss_distribution.png` | `analysis/fig_miss_distribution.py` | Positioning decides everything |
| `wind_samples.png` | `analysis/fig_wind.py` | Roatán wind: precision holds |
| `flight_times.png` | `analysis/fig_flight_times.py` | Flight time per sample |

## Key results (simulation)

| Scenario | Samples collected | Median miss | 95th percentile miss |
|---|---|---|---|
| S1 RTK GNSS, calm | 8,000 / 8,000 | 3 cm | 6 cm |
| S2 Drone GNSS, calm | 8,000 / 8,000 | 0.84 m | 1.78 m |
| S3 Handheld-grade GPS, open sky | 8,000 / 8,000 | 3.3 m | 7.0 m |
| S4 Handheld-grade GPS, under canopy | 3,323 / 8,000 | 16.8 m | 34.6 m |
| S5 RTK GNSS, Roatán wind | 2,356 / 7,808 | 3 cm | 6 cm |

Round-trip flight time per sample from the edge lab: median 3.8 minutes (5–95%: 2.8–5.2 minutes) over 5,000 flights.

Methods, assumptions and limitations: [docs/methods.md](docs/methods.md). Positions are published as local metres; exact geographic coordinates are not published.

## Repository layout

```
.
├── README.md                 This file
├── LICENSE                   MIT licence (code)
├── LICENSE-DATA.md           CC BY 4.0 (data and figures)
├── CITATION.cff              How to cite
├── requirements.txt          Pinned Python dependencies
├── run_all.py                Regenerates all figures and numbers
├── analysis/                 One script per figure, plus stats.py and shared config.py
├── simulation/prospera_sim.py  Monte Carlo model of sampling flights at Próspera
├── data/
│   ├── README.md             File inventory and data dictionary
│   ├── literature/           Published values used for comparison
│   └── raw/                  Simulation outputs
├── docs/methods.md           Simulation setup, scenarios, assumptions, limitations
└── figures/                  Generated figures and talk_numbers.json
```

## How to cite

If you use this data or code, please cite it using the metadata in [CITATION.cff](CITATION.cff) (GitHub shows a "Cite this repository" button). A DOI will be added when the release is archived on Zenodo.

## Contact

Questions and corrections are welcome through [GitHub Issues](https://github.com/LabGPT-science/5000-flights-drone-sampling/issues).

## Licence

Code: MIT ([LICENSE](LICENSE)). Data and figures: CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)).
