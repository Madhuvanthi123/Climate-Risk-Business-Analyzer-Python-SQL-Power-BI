"""
generate_synthetic_data.py
---------------------------
Generates a realistic, internally-consistent synthetic dataset so the whole
pipeline (SQL -> Python -> stats -> visuals -> Power BI) can be demoed and
tested end-to-end even before you plug in a real climate/business data feed.

Replace this module later with real loaders (e.g. NOAA/IMD climate data +
your ERP/finance exports) without touching any downstream code, since every
other script only cares about the final table shapes, not where rows came
from.

Output: two CSVs in data/raw/
  - regions.csv
  - climate_business_monthly.csv   (one row per region per month)
"""

import numpy as np
import pandas as pd
from src.config import DATA_RAW_DIR

np.random.seed(42)

REGIONS = [
    {"region_id": 1, "region_name": "Chennai",    "country": "India", "latitude": 13.0827, "longitude": 80.2707, "base_risk": 0.65},
    {"region_id": 2, "region_name": "Mumbai",      "country": "India", "latitude": 19.0760, "longitude": 72.8777, "base_risk": 0.70},
    {"region_id": 3, "region_name": "Kolkata",     "country": "India", "latitude": 22.5726, "longitude": 88.3639, "base_risk": 0.75},
    {"region_id": 4, "region_name": "Bengaluru",   "country": "India", "latitude": 12.9716, "longitude": 77.5946, "base_risk": 0.35},
    {"region_id": 5, "region_name": "Delhi",       "country": "India", "latitude": 28.7041, "longitude": 77.1025, "base_risk": 0.50},
    {"region_id": 6, "region_name": "Hyderabad",   "country": "India", "latitude": 17.3850, "longitude": 78.4867, "base_risk": 0.40},
    {"region_id": 7, "region_name": "Jakarta",     "country": "Indonesia", "latitude": -6.2088, "longitude": 106.8456, "base_risk": 0.80},
    {"region_id": 8, "region_name": "Miami",       "country": "USA", "latitude": 25.7617, "longitude": -80.1918, "base_risk": 0.72},
]

START_DATE = "2016-01-01"
END_DATE = "2025-12-01"


def generate_regions_table():
    return pd.DataFrame(REGIONS)[["region_id", "region_name", "country", "latitude", "longitude"]]


def generate_climate_business_data():
    dates = pd.date_range(START_DATE, END_DATE, freq="MS")  # month start
    rows = []

    for region in REGIONS:
        base_risk = region["base_risk"]
        # smooth seasonal cycle (peaks around monsoon/hurricane months) + slow warming trend
        month_idx = np.arange(len(dates))
        seasonal = np.sin(2 * np.pi * (month_idx % 12) / 12 - np.pi / 2)
        warming_trend = month_idx / len(dates) * 1.2  # gradual multi-year warming signal

        avg_temp_c = 24 + 6 * base_risk + 3 * seasonal + warming_trend + np.random.normal(0, 0.8, len(dates))
        precipitation_mm = np.clip(
            120 + 300 * base_risk * (seasonal.clip(min=0)) + np.random.normal(0, 40, len(dates)), 0, None
        )
        extreme_weather_events = np.random.poisson(lam=base_risk * 2.2 + seasonal.clip(min=0), size=len(dates))
        drought_index = np.clip(
            50 * base_risk + 20 * (-seasonal).clip(min=0) + np.random.normal(0, 8, len(dates)), 0, 100
        )
        flood_risk_score = np.clip(
            60 * base_risk + 25 * seasonal.clip(min=0) + np.random.normal(0, 7, len(dates)), 0, 100
        )
        cyclone_alerts = np.random.poisson(lam=base_risk * 1.1 * seasonal.clip(min=0).mean() + base_risk * 0.4, size=len(dates))

        # Composite "true" hazard signal used to drive business impact (kept hidden from downstream code)
        hazard_signal = (
            0.25 * (extreme_weather_events / (extreme_weather_events.max() + 1e-9))
            + 0.20 * (drought_index / 100)
            + 0.20 * (flood_risk_score / 100)
            + 0.15 * (cyclone_alerts / (cyclone_alerts.max() + 1e-9))
            + 0.20 * base_risk
        )

        base_revenue = np.random.uniform(80, 150)  # in INR lakhs / $000s, arbitrary unit
        revenue = (
            base_revenue * (1 + 0.02 * month_idx / 12)          # organic growth
            - base_revenue * 0.35 * hazard_signal                 # climate drag
            + np.random.normal(0, base_revenue * 0.05, len(dates))
        )
        operational_cost = base_revenue * 0.6 * (1 + 0.4 * hazard_signal) + np.random.normal(0, 3, len(dates))
        supply_chain_delay_days = np.clip(2 + 18 * hazard_signal + np.random.normal(0, 1.5, len(dates)), 0, None)
        insurance_claims = np.random.poisson(lam=hazard_signal * 4, size=len(dates))
        facility_downtime_hours = np.clip(4 + 60 * hazard_signal + np.random.normal(0, 5, len(dates)), 0, None)
        employee_safety_incidents = np.random.poisson(lam=hazard_signal * 1.5, size=len(dates))

        region_df = pd.DataFrame({
            "region_id": region["region_id"],
            "record_date": dates,
            "avg_temp_c": avg_temp_c.round(2),
            "precipitation_mm": precipitation_mm.round(1),
            "extreme_weather_events": extreme_weather_events,
            "drought_index": drought_index.round(1),
            "flood_risk_score": flood_risk_score.round(1),
            "cyclone_alerts": cyclone_alerts,
            "revenue": revenue.round(2),
            "operational_cost": operational_cost.round(2),
            "supply_chain_delay_days": supply_chain_delay_days.round(1),
            "insurance_claims": insurance_claims,
            "facility_downtime_hours": facility_downtime_hours.round(1),
            "employee_safety_incidents": employee_safety_incidents,
        })
        rows.append(region_df)

    return pd.concat(rows, ignore_index=True)


def main():
    regions_df = generate_regions_table()
    monthly_df = generate_climate_business_data()

    regions_path = DATA_RAW_DIR / "regions.csv"
    monthly_path = DATA_RAW_DIR / "climate_business_monthly.csv"

    regions_df.to_csv(regions_path, index=False)
    monthly_df.to_csv(monthly_path, index=False)

    print(f"Wrote {len(regions_df)} regions to {regions_path}")
    print(f"Wrote {len(monthly_df)} monthly records to {monthly_path}")


if __name__ == "__main__":
    main()
