"""
config.py
---------
Central configuration for the Climate Risk & Business Analyzer.

Just edit DB_CONFIG below with your MySQL Workbench 8.0 CE credentials.
No .env file, no environment variables needed -- this is the only place
you need to touch.
"""

import pathlib

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "Madhu@pumo123",   # <-- put your actual MySQL password here
    "database": "climate_risk_db",
}

# Weights used to build the composite Climate Risk Index (CRI).
# Must sum to 1.0. Tune these based on domain knowledge / stakeholder input.
CRI_WEIGHTS = {
    "avg_temp_anomaly": 0.15,
    "precipitation_anomaly": 0.15,
    "extreme_weather_events": 0.25,
    "drought_index": 0.20,
    "flood_risk_score": 0.15,
    "cyclone_alerts": 0.10,
}

# Paths
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
POWERBI_EXPORT_DIR = BASE_DIR / "outputs" / "powerbi_export"

for _dir in (DATA_RAW_DIR, DATA_PROCESSED_DIR, FIGURES_DIR, POWERBI_EXPORT_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
