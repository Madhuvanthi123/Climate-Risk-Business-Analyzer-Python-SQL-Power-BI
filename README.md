# Climate-Risk-Business-Analyzer-Python-SQL-Power-BI
End-to-end climate risk analytics project that quantifies how extreme weather and climate trends impact business assets, revenue, and operations, using Python, SQL, statistics, and Power BI dashboards.
# 🌍 Climate Risk Business Analyzer

## 📌 Project Overview
This project assesses how climate-related hazards (heatwaves, floods, droughts,
cyclones, rainfall variability) affect business operations and financial
performance. It combines climate and business datasets, applies statistical
analysis to detect trends and risk patterns, and presents the results through
an interactive Power BI dashboard to support risk-aware decision making.

## 🎯 Business Objectives
- Quantify exposure of business locations/assets to climate hazards
- Measure the relationship between climate events and revenue, cost, or downtime
- Identify high-risk regions, sectors, and time periods
- Build a transparent climate risk score for each location
- Provide actionable recommendations for mitigation and adaptation

## 📊 Key Metrics & KPIs
| Metric | Description |
|---|---|
| Climate Risk Score | Weighted index of hazard frequency, severity, and exposure |
| Hazard Frequency | Number of extreme events per location per year |
| Revenue at Risk | Revenue from locations above a risk threshold |
| Estimated Loss Impact | Financial loss linked to climate events |
| Temperature / Rainfall Anomaly | Deviation from long-term average |
| Vulnerability Index | Sensitivity of assets based on sector and location |

## 🗂️ Dataset
- **Climate data:** NASA POWER, NOAA, Kaggle climate datasets, IMD (India)
- **Business data:** Sample or synthetic sales, asset, and operations data
- **Disaster data:** EM-DAT or other public disaster records
- **Format:** CSV / Excel / SQL tables
- (Update with exact source links and record counts)

## 🛠️ Tools & Technologies
| Category | Tools |
|---|---|
| Programming | Python (Pandas, NumPy) |
| Visualization | Matplotlib, Seaborn, Power BI |
| Database | SQL (MySQL / PostgreSQL / SQLite) |
| Statistics | SciPy, Statsmodels |
| Reporting | Excel, Power BI |

## 🔄 Project Workflow
1. **Data Collection**: gathered climate, disaster, and business datasets
2. **Data Cleaning**: handled missing values, outliers, and date formats (Pandas)
3. **SQL Analysis**: joins, aggregations, window functions, and CTEs for hazard and revenue summaries
4. **Exploratory Data Analysis**: trends, seasonality, distributions, correlation heatmaps
5. **Statistical Analysis**: hypothesis testing, correlation, regression, trend tests
6. **Risk Scoring**: normalized and weighted indicators to build a composite risk index
7. **Dashboarding**: Excel summary sheets and an interactive Power BI report
8. **Insights & Recommendations**: documented findings and mitigation strategy

## 📐 Statistical Methods Used
- Descriptive statistics (mean, median, std, skewness)
- Pearson / Spearman correlation between climate variables and business outcomes
- Linear regression to estimate the impact of temperature and rainfall on revenue
- Mann-Kendall / linear trend analysis for long-term climate change
- t-test / ANOVA to compare performance across risk zones
- Z-score and IQR methods for anomaly and outlier detection

## 🧮 Sample Code

**SQL: Revenue at risk by region**
```sql
SELECT r.region,
       COUNT(e.event_id)       AS total_events,
       SUM(s.revenue)          AS total_revenue,
       SUM(CASE WHEN rk.risk_score >= 70 THEN s.revenue END) AS revenue_at_risk
FROM sales s
JOIN regions r       ON s.region_id = r.region_id
JOIN risk_scores rk  ON r.region_id = rk.region_id
LEFT JOIN climate_events e ON r.region_id = e.region_id
GROUP BY r.region
ORDER BY revenue_at_risk DESC;
```

**Python: Composite climate risk score**
```python
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

features = ["hazard_freq", "avg_severity", "exposure", "vulnerability"]
scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

weights = {"hazard_freq": 0.35, "avg_severity": 0.25,
           "exposure": 0.25, "vulnerability": 0.15}
df["risk_score"] = sum(df[c] * w for c, w in weights.items()) * 100
```

**Python: Correlation and regression**
```python
import seaborn as sns
import statsmodels.api as sm

sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm")

X = sm.add_constant(df[["temp_anomaly", "rainfall_anomaly"]])
model = sm.OLS(df["revenue"], X).fit()
print(model.summary())
```

## 📈 Power BI Dashboard Pages
1. **Executive Overview**: headline KPIs and global/regional risk map
2. **Hazard Analysis**: event frequency, severity trends, seasonality
3. **Business Impact**: revenue at risk, loss estimates, downtime
4. **Location Risk Ranking**: risk scores, drill-through by site
5. **Scenario & Recommendations**: high-risk zones and mitigation priorities

## 💡 Key Insights
- Replace with your real findings, for example:
- Locations in the top risk quartile account for XX% of revenue
- Rainfall anomaly shows a statistically significant negative effect on revenue (p < 0.05)
- Heat-related events increased by XX% over the last decade

## ✅ Recommendations
- Diversify operations away from the highest-risk zones
- Invest in climate-resilient infrastructure at critical sites
- Build early-warning and insurance strategies for high-exposure regions
- Monitor risk scores quarterly using the dashboard

## 📸 Dashboard Preview
![Dashboard](images/dashboard.png)

## 📁 Repository Structure
