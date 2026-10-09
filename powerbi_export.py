"""
powerbi_export.py
------------------
Exports one flat, Power-BI-ready table (CSV + Excel) combining regions,
climate indicators, business metrics, and the computed Climate Risk Index.

Power BI can either:
  (a) connect straight to MySQL (Get Data > MySQL database) and use the
      vw_climate_business_full view created in sql/02_analysis_queries.sql, OR
  (b) import the CSV/XLSX produced here if a live DB connection isn't
      available on the machine running Power BI Desktop.

Usage:
    python -m src.powerbi_export
"""

import pandas as pd
from src.db_connector import run_query
from src.config import POWERBI_EXPORT_DIR


def main():
    df = run_query("""
        SELECT
            m.record_id, r.region_name, r.country, r.latitude, r.longitude,
            m.record_date,
            YEAR(m.record_date)  AS year,
            MONTH(m.record_date) AS month,
            m.avg_temp_c, m.precipitation_mm, m.extreme_weather_events,
            m.drought_index, m.flood_risk_score, m.cyclone_alerts,
            m.revenue, m.operational_cost, m.supply_chain_delay_days,
            m.insurance_claims, m.facility_downtime_hours, m.employee_safety_incidents,
            cri.cri_score, cri.risk_category
        FROM climate_business_monthly m
        JOIN regions r ON r.region_id = m.region_id
        JOIN climate_risk_index cri ON cri.record_id = m.record_id
        ORDER BY r.region_name, m.record_date
    """)

    csv_path = POWERBI_EXPORT_DIR / "climate_business_powerbi.csv"
    xlsx_path = POWERBI_EXPORT_DIR / "climate_business_powerbi.xlsx"

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, sheet_name="climate_business")

    print(f"Exported {len(df)} rows to:\n  {csv_path}\n  {xlsx_path}")


if __name__ == "__main__":
    main()
