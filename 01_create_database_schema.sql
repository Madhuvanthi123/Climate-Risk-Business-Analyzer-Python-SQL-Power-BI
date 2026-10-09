-- =====================================================================
-- 01_create_database_schema.sql
-- Climate Risk & Business Analyzer -- Schema
-- Run this in MySQL Workbench 8.0 CE (File > Open SQL Script > Execute,
-- or select all and hit the lightning-bolt "Execute" button).
-- =====================================================================

CREATE DATABASE IF NOT EXISTS climate_risk_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE climate_risk_db;

-- ---------------------------------------------------------------------
-- 1. Dimension table: regions/facilities being monitored
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS regions;
CREATE TABLE regions (
    region_id     INT PRIMARY KEY,
    region_name   VARCHAR(100) NOT NULL,
    country       VARCHAR(100) NOT NULL,
    latitude      DECIMAL(9,6),
    longitude     DECIMAL(9,6)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. Fact table: monthly climate + business metrics per region
--    (kept as ONE wide table for simplicity; can be normalized further
--     into climate_data / business_data if you prefer 3NF)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS climate_business_monthly;
CREATE TABLE climate_business_monthly (
    record_id                   INT AUTO_INCREMENT PRIMARY KEY,
    region_id                   INT NOT NULL,
    record_date                 DATE NOT NULL,

    -- climate hazard indicators
    avg_temp_c                  DECIMAL(5,2),
    precipitation_mm            DECIMAL(7,2),
    extreme_weather_events      INT,
    drought_index               DECIMAL(5,2),   -- 0-100
    flood_risk_score            DECIMAL(5,2),   -- 0-100
    cyclone_alerts               INT,

    -- business impact indicators
    revenue                     DECIMAL(12,2),
    operational_cost            DECIMAL(12,2),
    supply_chain_delay_days     DECIMAL(5,2),
    insurance_claims            INT,
    facility_downtime_hours     DECIMAL(6,2),
    employee_safety_incidents   INT,

    CONSTRAINT fk_region
        FOREIGN KEY (region_id) REFERENCES regions(region_id)
        ON DELETE CASCADE,

    UNIQUE KEY uq_region_month (region_id, record_date)
) ENGINE=InnoDB;

CREATE INDEX idx_record_date ON climate_business_monthly (record_date);
CREATE INDEX idx_region_date ON climate_business_monthly (region_id, record_date);

-- ---------------------------------------------------------------------
-- 3. Table to persist the composite Climate Risk Index (CRI) once it
--    is calculated in Python (src/risk_scoring.py writes here).
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS climate_risk_index;
CREATE TABLE climate_risk_index (
    record_id     INT PRIMARY KEY,             -- matches climate_business_monthly.record_id
    region_id     INT NOT NULL,
    record_date   DATE NOT NULL,
    cri_score     DECIMAL(6,3),                 -- normalized 0-1 composite risk score
    risk_category VARCHAR(20),                  -- Low / Medium / High / Severe
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
) ENGINE=InnoDB;

-- Sanity check
SHOW TABLES;




