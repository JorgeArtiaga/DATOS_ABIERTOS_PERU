-- KPI queries to explore the model before building the dashboard (DuckDB).
-- On-time: arrival less than 15 minutes late, over flights that were not cancelled or diverted.

-- 1. Monthly overview
SELECT
    d.year_month,
    count(*)                                                    AS scheduled_flights,
    round(100 * avg(f.cancelled), 2)                            AS cancelled_pct,
    round(100 * (1 - avg(f.arr_del15) FILTER (WHERE f.cancelled = 0 AND f.diverted = 0)), 2)
                                                                AS on_time_pct,
    round(avg(f.arr_delay) FILTER (WHERE f.arr_delay > 0), 1)   AS avg_delay_when_late_min
FROM fact_flights AS f
JOIN dim_date AS d ON d.date = f.flight_date
GROUP BY d.year_month
ORDER BY d.year_month;

-- 2. On-time performance by airline
SELECT
    a.airline_name,
    count(*)                                                    AS flights,
    round(100 * (1 - avg(f.arr_del15)), 2)                      AS on_time_pct
FROM fact_flights AS f
JOIN dim_airline AS a USING (airline_code)
WHERE f.cancelled = 0 AND f.diverted = 0
GROUP BY a.airline_name
ORDER BY on_time_pct DESC;

-- 3. Share of delay minutes by cause
SELECT
    c.delay_cause_name,
    round(sum(m.delay_minutes) / 60)                            AS delay_hours,
    round(100 * sum(m.delay_minutes) / sum(sum(m.delay_minutes)) OVER (), 1)
                                                                AS share_pct
FROM fact_delay_minutes AS m
JOIN dim_delay_cause AS c USING (delay_cause)
GROUP BY c.delay_cause_name
ORDER BY delay_hours DESC;

-- 4. Taxi-out by hour at the 10 busiest airports (ground congestion)
WITH busiest AS (
    SELECT origin FROM fact_flights
    WHERE cancelled = 0
    GROUP BY origin
    ORDER BY count(*) DESC
    LIMIT 10
)
SELECT
    f.origin,
    f.crs_dep_hour,
    count(*)                                                    AS departures,
    round(avg(f.taxi_out), 1)                                   AS avg_taxi_out_min,
    round(quantile_cont(f.taxi_out, 0.9), 1)                    AS p90_taxi_out_min
FROM fact_flights AS f
JOIN busiest USING (origin)
WHERE f.cancelled = 0 AND f.taxi_out IS NOT NULL
GROUP BY f.origin, f.crs_dep_hour
ORDER BY f.origin, f.crs_dep_hour;
