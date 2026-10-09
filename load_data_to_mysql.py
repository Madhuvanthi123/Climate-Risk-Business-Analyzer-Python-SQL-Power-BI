"""
load_data_to_mysql.py
----------------------
Loads the CSVs from data/raw/ into the MySQL tables created by
sql/01_create_database_schema.sql.

Prerequisites:
  1. MySQL Workbench 8.0 CE running, schema created (run 01_create_database_schema.sql).
  2. src/config.py DB_CONFIG updated with your credentials (or a .env file).
  3. Run src/generate_synthetic_data.py first (or point this script at your
     own real climate/business CSVs with the same column names).

Usage:
    python -m src.load_data_to_mysql
"""

import pandas as pd
from src.config import DATA_RAW_DIR
from src.db_connector import get_engine


def load_regions(engine):
    df = pd.read_csv(DATA_RAW_DIR / "regions.csv")
    df.to_sql("regions", engine, if_exists="append", index=False, method="multi")
    print(f"Loaded {len(df)} rows into regions")


def load_climate_business_monthly(engine):
    df = pd.read_csv(DATA_RAW_DIR / "climate_business_monthly.csv", parse_dates=["record_date"])
    df.to_sql(
        "climate_business_monthly",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
    print(f"Loaded {len(df)} rows into climate_business_monthly")


def main():
    engine = get_engine()
    # Truncate first so this script is safely re-runnable during development
    with engine.begin() as conn:
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=0")
        conn.exec_driver_sql("TRUNCATE TABLE climate_risk_index")
        conn.exec_driver_sql("TRUNCATE TABLE climate_business_monthly")
        conn.exec_driver_sql("TRUNCATE TABLE regions")
        conn.exec_driver_sql("SET FOREIGN_KEY_CHECKS=1")

    load_regions(engine)
    load_climate_business_monthly(engine)
    print("Done. Now run: python -m src.risk_scoring")


if __name__ == "__main__":
    main()
