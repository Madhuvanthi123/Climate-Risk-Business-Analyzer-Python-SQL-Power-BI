"""
risk_scoring.py
----------------
Computes a composite Climate Risk Index (CRI) per region/month by:
  1. Pulling raw climate indicators from MySQL,
  2. Min-max normalizing each indicator to a 0-1 scale,
  3. Combining them with the weights defined in config.CRI_WEIGHTS,
  4. Bucketing the result into Low / Medium / High / Severe categories,
  5. Writing the scores back to the climate_risk_index table so both
     SQL (Workbench) and Power BI can consume them directly.

Usage:
    python -m src.risk_scoring
"""

import numpy as np
import pandas as pd
from src.config import CRI_WEIGHTS, DATA_PROCESSED_DIR
from src.db_connector import get_engine, run_query


CLIMATE_COLUMNS_MAP = {
    # column in DB -> key in CRI_WEIGHTS
    "avg_temp_c": "avg_temp_anomaly",
    "precipitation_mm": "precipitation_anomaly",
    "extreme_weather_events": "extreme_weather_events",
    "drought_index": "drought_index",
    "flood_risk_score": "flood_risk_score",
    "cyclone_alerts": "cyclone_alerts",
}


def min_max_normalize(series: pd.Series) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi - lo == 0:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - lo) / (hi - lo)


def categorize_risk(score: float) -> str:
    if score < 0.25:
        return "Low"
    elif score < 0.50:
        return "Medium"
    elif score < 0.75:
        return "High"
    return "Severe"


def compute_cri(df: pd.DataFrame) -> pd.DataFrame:
    """df must contain the raw columns in CLIMATE_COLUMNS_MAP, one row per record."""
    normalized = pd.DataFrame(index=df.index)
    for db_col, weight_key in CLIMATE_COLUMNS_MAP.items():
        # temperature and precipitation contribute as *anomalies* (deviation from
        # that region's own mean), everything else contributes as its raw
        # normalized magnitude -- both are legitimate hazard signals.
        if db_col in ("avg_temp_c", "precipitation_mm"):
            region_mean = df.groupby("region_id")[db_col].transform("mean")
            anomaly = (df[db_col] - region_mean).abs()
            normalized[weight_key] = min_max_normalize(anomaly)
        else:
            normalized[weight_key] = min_max_normalize(df[db_col])

    weights = np.array([CRI_WEIGHTS[k] for k in normalized.columns])
    assert abs(weights.sum() - 1.0) < 1e-6, "CRI_WEIGHTS must sum to 1.0"

    df = df.copy()
    df["cri_score"] = normalized.values @ weights
    df["risk_category"] = df["cri_score"].apply(categorize_risk)
    return df


def main():
    raw = run_query("""
        SELECT record_id, region_id, record_date,
               avg_temp_c, precipitation_mm, extreme_weather_events,
               drought_index, flood_risk_score, cyclone_alerts
        FROM climate_business_monthly
    """)

    scored = compute_cri(raw)
    out = scored[["record_id", "region_id", "record_date", "cri_score", "risk_category"]]

    # save a local copy too, useful for quick inspection / Power BI fallback import
    out_path = DATA_PROCESSED_DIR / "climate_risk_index.csv"
    out.to_csv(out_path, index=False)
    print(f"Computed CRI for {len(out)} records -> {out_path}")

    engine = get_engine()
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE climate_risk_index")
    out.to_sql("climate_risk_index", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print("Wrote CRI scores to MySQL table climate_risk_index")


if __name__ == "__main__":
    main()
