-- =====================================================================
-- 02_analysis_queries.sql
-- Ready-to-run analysis queries for MySQL Workbench 8.0 CE.
-- Run these AFTER the tables have been populated
-- (via src/load_data_to_mysql.py and src/risk_scoring.py).
-- =====================================================================

USE climate_risk_db;

-- ---------------------------------------------------------------------
-- Q1. Average climate risk index by region (highest risk first)
-- ---------------------------------------------------------------------
SELECT
    r.region_name,
    r.country,
    ROUND(AVG(c.cri_score), 3)  AS avg_cri,
    COUNT(*)                    AS months_recorded
FROM climate_risk_index c
JOIN regions r ON r.region_id = c.region_id
GROUP BY r.region_name, r.country
ORDER BY avg_cri DESC;

-- ---------------------------------------------------------------------
-- Q2. Year-over-year revenue vs. climate risk, per region
-- ---------------------------------------------------------------------
SELECT
    r.region_name,
    YEAR(m.record_date)                AS yr,
    ROUND(SUM(m.revenue), 2)           AS total_revenue,
    ROUND(AVG(cri.cri_score), 3)       AS avg_cri
FROM climate_business_monthly m
JOIN regions r  ON r.region_id = m.region_id
JOIN climate_risk_index cri ON cri.record_id = m.record_id
GROUP BY r.region_name, YEAR(m.record_date)
ORDER BY r.region_name, yr;

-- ---------------------------------------------------------------------
-- Q3. Top 10 highest-risk months (any region) with business impact
-- ---------------------------------------------------------------------
SELECT
    r.region_name,
    m.record_date,
    cri.cri_score,
    cri.risk_category,
    m.revenue,
    m.facility_downtime_hours,
    m.supply_chain_delay_days
FROM climate_business_monthly m
JOIN climate_risk_index cri ON cri.record_id = m.record_id
JOIN regions r ON r.region_id = m.region_id
ORDER BY cri.cri_score DESC
LIMIT 10;

-- ---------------------------------------------------------------------
-- Q4. Manual Pearson correlation (MySQL has no CORR() built-in) between
--     Climate Risk Index and Revenue, per region.
--     Formula: r = (n*SumXY - SumX*SumY) / sqrt((n*SumX2-SumX^2)*(n*SumY2-SumY^2))
-- ---------------------------------------------------------------------
SELECT
    r.region_name,
    COUNT(*)                                                              AS n,
    ROUND(
        (COUNT(*) * SUM(cri.cri_score * m.revenue) - SUM(cri.cri_score) * SUM(m.revenue))
        /
        NULLIF(
            SQRT(
                (COUNT(*) * SUM(POW(cri.cri_score, 2)) - POW(SUM(cri.cri_score), 2)) *
                (COUNT(*) * SUM(POW(m.revenue, 2))     - POW(SUM(m.revenue), 2))
            ), 0
        )
    , 3) AS pearson_r_cri_vs_revenue
FROM climate_business_monthly m
JOIN climate_risk_index cri ON cri.record_id = m.record_id
JOIN regions r ON r.region_id = m.region_id
GROUP BY r.region_name
ORDER BY pearson_r_cri_vs_revenue ASC;

-- ---------------------------------------------------------------------
-- Q5. 3-month moving average of CRI per region (MySQL 8.0 window function)
-- ---------------------------------------------------------------------
SELECT
    r.region_name,
    m.record_date,
    cri.cri_score,
    ROUND(
        AVG(cri.cri_score) OVER (
            PARTITION BY m.region_id
            ORDER BY m.record_date
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 3
    ) AS cri_3mo_moving_avg
FROM climate_business_monthly m
JOIN climate_risk_index cri ON cri.record_id = m.record_id
JOIN regions r ON r.region_id = m.region_id
ORDER BY r.region_name, m.record_date;

-- ---------------------------------------------------------------------
-- Q6. Rank regions by risk-adjusted revenue loss (window function RANK)
-- ---------------------------------------------------------------------
WITH region_summary AS (
    SELECT
        r.region_id,
        r.region_name,
        AVG(cri.cri_score)      AS avg_cri,
        AVG(m.facility_downtime_hours) AS avg_downtime,
        SUM(m.insurance_claims) AS total_claims
    FROM climate_business_monthly m
    JOIN climate_risk_index cri ON cri.record_id = m.record_id
    JOIN regions r ON r.region_id = m.region_id
    GROUP BY r.region_id, r.region_name
)
SELECT
    region_name,
    ROUND(avg_cri, 3)      AS avg_cri,
    ROUND(avg_downtime, 1) AS avg_downtime_hours,
    total_claims,
    RANK() OVER (ORDER BY avg_cri DESC) AS risk_rank
FROM region_summary
ORDER BY risk_rank;

-- ---------------------------------------------------------------------
-- Q7. A view Power BI (or any BI tool) can query directly as one flat table
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_climate_business_full AS
SELECT
    m.record_id,
    r.region_name,
    r.country,
    r.latitude,
    r.longitude,
    m.record_date,
    m.avg_temp_c,
    m.precipitation_mm,
    m.extreme_weather_events,
    m.drought_index,
    m.flood_risk_score,
    m.cyclone_alerts,
    m.revenue,
    m.operational_cost,
    m.supply_chain_delay_days,
    m.insurance_claims,
    m.facility_downtime_hours,
    m.employee_safety_incidents,
    cri.cri_score,
    cri.risk_category
FROM climate_business_monthly m
JOIN regions r ON r.region_id = m.region_id
JOIN climate_risk_index cri ON cri.record_id = m.record_id;

SELECT * FROM vw_climate_business_full LIMIT 20;
SELECT COUNT(*) FROM climate_business_monthly;
