"""
main_pipeline.py
------------------
Runs the entire Climate Risk & Business Analyzer pipeline end-to-end:

    1. Generate synthetic data (skip this step once you wire in real data)
    2. Load data into MySQL
    3. Compute the Climate Risk Index and write it back to MySQL
    4. Run statistical analysis (descriptive stats, correlation, regression, t-test)
    5. Generate all visualizations
    6. Export a flat table for Power BI

Prerequisites:
    - MySQL Workbench 8.0 CE running locally
    - sql/01_create_database_schema.sql already executed once in Workbench
    - src/config.py DB_CONFIG credentials updated

Usage:
    python -m src.main_pipeline
"""

from src import generate_synthetic_data
from src import load_data_to_mysql
from src import risk_scoring
from src import statistical_analysis
from src import visualization
from src import powerbi_export


def main():
    print("STEP 1/6: Generating synthetic dataset ...")
    generate_synthetic_data.main()

    print("\nSTEP 2/6: Loading data into MySQL ...")
    load_data_to_mysql.main()

    print("\nSTEP 3/6: Computing Climate Risk Index ...")
    risk_scoring.main()

    print("\nSTEP 4/6: Running statistical analysis ...")
    statistical_analysis.main()

    print("\nSTEP 5/6: Generating visualizations ...")
    visualization.main()

    print("\nSTEP 6/6: Exporting flat table for Power BI ...")
    powerbi_export.main()

    print("\nPipeline complete. Check outputs/figures, data/processed, and outputs/powerbi_export.")


if __name__ == "__main__":
    main()
