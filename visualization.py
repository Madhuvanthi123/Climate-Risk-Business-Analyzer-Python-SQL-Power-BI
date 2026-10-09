"""
visualization.py
-----------------
Generates the core chart set for the project using matplotlib + seaborn.
All figures are saved as PNGs into outputs/figures/ so they can be dropped
straight into a report, slide deck, or used as static visuals alongside the
Power BI dashboard.

Usage:
    python -m src.visualization
"""

import matplotlib
matplotlib.use("Agg")  # headless-safe backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.db_connector import run_query
from src.config import FIGURES_DIR

sns.set_theme(style="whitegrid", palette="viridis")


def load_full_dataset() -> pd.DataFrame:
    return run_query("""
        SELECT m.*, cri.cri_score, cri.risk_category, r.region_name, r.country
        FROM climate_business_monthly m
        JOIN climate_risk_index cri ON cri.record_id = m.record_id
        JOIN regions r ON r.region_id = m.region_id
        ORDER BY r.region_name, m.record_date
    """)


def plot_correlation_heatmap(df, save_as="correlation_heatmap.png"):
    cols = ["avg_temp_c", "precipitation_mm", "extreme_weather_events", "drought_index",
            "flood_risk_score", "cyclone_alerts", "cri_score", "revenue",
            "operational_cost", "supply_chain_delay_days", "facility_downtime_hours",
            "insurance_claims"]
    corr = df[cols].corr()

    plt.figure(figsize=(11, 9))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title("Correlation Matrix: Climate Hazard Indicators vs. Business Impact")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def plot_cri_trend_by_region(df, save_as="cri_trend_by_region.png"):
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="record_date", y="cri_score", hue="region_name", linewidth=1.5)
    plt.title("Climate Risk Index (CRI) Trend Over Time by Region")
    plt.xlabel("Date")
    plt.ylabel("Climate Risk Index (0-1)")
    plt.legend(title="Region", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def plot_avg_cri_by_region(df, save_as="avg_cri_by_region.png"):
    agg = df.groupby("region_name", as_index=False)["cri_score"].mean().sort_values("cri_score", ascending=False)
    plt.figure(figsize=(9, 6))
    sns.barplot(data=agg, x="cri_score", y="region_name", hue="region_name",
                palette="rocket", legend=False)
    plt.title("Average Climate Risk Index by Region")
    plt.xlabel("Average CRI")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def plot_revenue_vs_risk_scatter(df, save_as="revenue_vs_cri_scatter.png"):
    plt.figure(figsize=(9, 6))
    sns.regplot(data=df, x="cri_score", y="revenue", scatter_kws={"alpha": 0.4, "s": 25},
                line_kws={"color": "crimson"})
    plt.title("Revenue vs. Climate Risk Index (with linear fit)")
    plt.xlabel("Climate Risk Index")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def plot_revenue_by_risk_category(df, save_as="revenue_by_risk_category.png"):
    order = ["Low", "Medium", "High", "Severe"]
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x="risk_category", y="revenue", hue="risk_category",
                order=order, palette="mako", legend=False)
    plt.title("Revenue Distribution by Climate Risk Category")
    plt.xlabel("Risk Category")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def plot_downtime_vs_extreme_events(df, save_as="downtime_vs_extreme_events.png"):
    plt.figure(figsize=(9, 6))
    sns.scatterplot(data=df, x="extreme_weather_events", y="facility_downtime_hours",
                     hue="region_name", alpha=0.7)
    plt.title("Facility Downtime vs. Extreme Weather Events")
    plt.xlabel("Extreme Weather Events (count/month)")
    plt.ylabel("Facility Downtime (hours)")
    plt.legend(title="Region", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / save_as, dpi=150)
    plt.close()


def main():
    df = load_full_dataset()
    plot_correlation_heatmap(df)
    plot_cri_trend_by_region(df)
    plot_avg_cri_by_region(df)
    plot_revenue_vs_risk_scatter(df)
    plot_revenue_by_risk_category(df)
    plot_downtime_vs_extreme_events(df)
    print(f"Saved 6 figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
