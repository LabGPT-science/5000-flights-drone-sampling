"""Shared paths and plotting style. All paths are relative to the repository root."""
from pathlib import Path
import os
import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
# Override with LABGPT_DATA_DIR if the data lives elsewhere (for example, a Zenodo download).
DATA = Path(os.environ.get("LABGPT_DATA_DIR", ROOT / "data"))
SIM_RUNS = DATA / "raw" / "sim_runs_2026-10-24"
PROSPERA = DATA / "raw" / "prospera_sim"
LITERATURE = DATA / "literature"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

GREEN, DARK_GREEN, INK, GREY, AMBER, LIGHT = "#00A859", "#1B5C35", "#10241B", "#5A6A64", "#D6962A", "#C9CFCC"

SCENARIOS = [
    ("S1_RTK_calm", "RTK GNSS"),
    ("S2_droneGNSS_calm", "Standard drone GNSS"),
    ("S3_handheldGPSopen_calm", "Handheld-grade GPS, open sky"),
    ("S4_handheldGPScanopy_calm", "Handheld-grade GPS, under canopy"),
    ("S5_RTK_RoatanWind", "RTK GNSS, Roatán wind"),
]
