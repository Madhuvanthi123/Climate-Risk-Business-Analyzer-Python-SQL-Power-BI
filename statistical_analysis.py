"""
statistical_analysis.py
-------------------------
Runs the core statistics of the project on the merged climate + business +
risk dataset:

  1. Descriptive statistics (pandas .describe())
  2. Correlation matrix + significance (scipy.stats.pearsonr)
  3. OLS regression: Revenue ~ Climate Risk Index (statsmodels)
  4. Hypothesis test: is revenue significantly different between
     High/Severe risk months vs. Low/Medium risk months (independent t-test)

Usage:
    python -m src.statistical_analysis
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from src.db_connector import run_query
from src.config import DATA_PROCESSED_DIR


def load_full_dataset() -> pd.DataFrame:
    return run_query("""
        SELECT m.*, cri.cri_score, cri.risk_category, r.region_name, r.country
        FROM climate_business_monthly m
        JOIN climate_risk_index cri ON cri.record_id = m.record_id
        JOIN regions r ON r.region_id = m.region_id
    """)


def descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].describe().T


def correlation_with_significance(df: pd.DataFrame, target_cols, driver_cols) -> pd.DataFrame:
    """Pearson correlation + p-value between each driver and each target."""
    records = []
    for target in target_cols:
        for driver in driver_cols:
            r, p = stats.pearsonr(df[driver], df[target])
            records.append({
                "driver": driver,
                "target": target,
                "pearson_r": round(r, 3),
                "p_value": round(p, 5),
                "significant_at_0.05": p < 0.05,
            })
    return pd.DataFrame(records)


def ols_regression(df: pd.DataFrame, y_col: str, x_cols: list):
    """Fit y = b0 + b1*x1 + ... and return the fitted statsmodels result."""
    X = sm.add_constant(df[x_cols])
    y = df[y_col]
    model = sm.OLS(y, X).fit()
    return model


def high_vs_low_risk_ttest(df: pd.DataFrame, value_col: str = "revenue"):
    """Independent two-sample t-test: High/Severe risk vs Low/Medium risk."""
    high_risk = df.loc[df["risk_category"].isin(["High", "Severe"]), value_col]
    low_risk = df.loc[df["risk_category"].isin(["Low", "Medium"]), value_col]
    t_stat, p_val = stats.ttest_ind(high_risk, low_risk, equal_var=False)
    return {
        "metric": value_col,
        "n_high_risk": len(high_risk),
        "n_low_risk": len(low_risk),
        "mean_high_risk": round(high_risk.mean(), 2),
        "mean_low_risk": round(low_risk.mean(), 2),
        "t_statistic": round(t_stat, 3),
        "p_value": round(p_val, 5),
        "significant_at_0.05": p_val < 0.05,
    }


def main():
    df = load_full_dataset()

    print("\n=== 1. Descriptive statistics ===")
    desc = descriptive_stats(df)
    print(desc)
    desc.to_csv(DATA_PROCESSED_DIR / "descriptive_stats.csv")

    print("\n=== 2. Correlation: hazard drivers vs. business impact ===")
    driver_cols = ["cri_score", "extreme_weather_events", "flood_risk_score", "drought_index"]
    target_cols = ["revenue", "operational_cost", "supply_chain_delay_days",
                   "facility_downtime_hours", "insurance_claims"]
    corr_df = correlation_with_significance(df, target_cols, driver_cols)
    print(corr_df.to_string(index=False))
    corr_df.to_csv(DATA_PROCESSED_DIR / "correlation_results.csv", index=False)

    print("\n=== 3. OLS Regression: revenue ~ cri_score + extreme_weather_events ===")
    model = ols_regression(df, "revenue", ["cri_score", "extreme_weather_events"])
    print(model.summary())
    with open(DATA_PROCESSED_DIR / "ols_regression_summary.txt", "w") as f:
        f.write(str(model.summary()))

    print("\n=== 4. Hypothesis test: High/Severe risk vs Low/Medium risk revenue ===")
    ttest_result = high_vs_low_risk_ttest(df, "revenue")
    print(ttest_result)
    pd.DataFrame([ttest_result]).to_csv(DATA_PROCESSED_DIR / "ttest_result.csv", index=False)

    print(f"\nAll stats artifacts written to {DATA_PROCESSED_DIR}")


if __name__ == "__main__":
    main()
