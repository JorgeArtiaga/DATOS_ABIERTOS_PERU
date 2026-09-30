-- Star schema for the On-Time Performance analysis (DuckDB).
-- Paths are relative to the project folder (airline-on-time-performance/).

-- Fact: one row per scheduled flight
CREATE OR REPLACE TABLE fact_flights AS
SELECT
    CAST(flight_date AS DATE)           AS flight_date,
    airline_code,
    flight_number,
    tail_number,
    origin,
    dest,
    crs_dep_hour,
    crs_arr_hour,
    dep_delay,
    arr_delay,
    dep_del15,
    arr_del15,
    taxi_out,
    taxi_in,
    cancelled,
    cancellation_code,
    diverted,
    distance,
    carrier_delay,
    weather_delay,
    nas_delay,
    security_delay,
    late_aircraft_delay
FROM read_parquet('data/processed/*.parquet');

-- Fact: delay minutes by cause (long format, easier to chart in Power BI)
CREATE OR REPLACE TABLE fact_delay_minutes AS
SELECT flight_date, airline_code, origin, dest, delay_cause, delay_minutes
FROM (
    UNPIVOT (
        SELECT
            flight_date, airline_code, origin, dest,
            carrier_delay       AS carrier,
            weather_delay       AS weather,
            nas_delay           AS nas,
            security_delay      AS security,
            late_aircraft_delay AS late_aircraft
        FROM fact_flights
    )
    ON carrier, weather, nas, security, late_aircraft
    INTO NAME delay_cause VALUE delay_minutes
)
WHERE delay_minutes > 0;

-- Dimension: calendar
CREATE OR REPLACE TABLE dim_date AS
WITH bounds AS (
    SELECT min(flight_date) AS first_day, max(flight_date) AS last_day FROM fact_flights
)
SELECT
    CAST(d AS DATE)          AS date,
    year(d)                  AS year,
    quarter(d)               AS quarter,
    month(d)                 AS month,
    monthname(d)             AS month_name,
    strftime(d, '%Y-%m')     AS year_month,
    day(d)                   AS day,
    isodow(d)                AS day_of_week,
    dayname(d)               AS day_name,
    isodow(d) IN (6, 7)      AS is_weekend
FROM bounds, generate_series(first_day, last_day, INTERVAL 1 DAY) AS t(d);

-- Dimension: airlines (names from reference/airlines.csv, code as fallback)
CREATE OR REPLACE TABLE dim_airline AS
SELECT
    f.airline_code,
    coalesce(r.airline_name, f.airline_code) AS airline_name
FROM (SELECT DISTINCT airline_code FROM fact_flights) AS f
LEFT JOIN read_csv('reference/airlines.csv', header = true) AS r USING (airline_code);

-- Dimension: airports (seen as origin or destination)
CREATE OR REPLACE TABLE dim_airport AS
SELECT airport_code, any_value(city) AS city, any_value(state) AS state
FROM (
    SELECT origin AS airport_code, origin_city AS city, origin_state AS state
    FROM read_parquet('data/processed/*.parquet')
    UNION ALL
    SELECT dest, dest_city, dest_state
    FROM read_parquet('data/processed/*.parquet')
)
GROUP BY airport_code;

-- Dimension: delay causes
CREATE OR REPLACE TABLE dim_delay_cause AS
SELECT * FROM read_csv('reference/delay_causes.csv', header = true);
