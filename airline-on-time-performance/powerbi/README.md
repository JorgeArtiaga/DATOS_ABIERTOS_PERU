# Power BI dashboard

Save the report here as `airline-on-time-performance.pbix` and add screenshots to `../images/`.

## Loading the model

1. Get data › Parquet, and load every file in `data/model/`.
2. Create the relationships (many-to-one, single direction):
   - `fact_flights[flight_date]` → `dim_date[date]`
   - `fact_flights[airline_code]` → `dim_airline[airline_code]`
   - `fact_flights[origin]` → `dim_airport[airport_code]`
   - `fact_delay_minutes[flight_date]` → `dim_date[date]`
   - `fact_delay_minutes[airline_code]` → `dim_airline[airline_code]`
   - `fact_delay_minutes[delay_cause]` → `dim_delay_cause[delay_cause]`
3. Mark `dim_date` as the date table.

## Measures (DAX)

```dax
Scheduled Flights = COUNTROWS ( fact_flights )

Operated Flights =
CALCULATE ( [Scheduled Flights], fact_flights[cancelled] = 0, fact_flights[diverted] = 0 )

Late Arrivals =
CALCULATE ( SUM ( fact_flights[arr_del15] ), fact_flights[cancelled] = 0, fact_flights[diverted] = 0 )

On-Time % = 1 - DIVIDE ( [Late Arrivals], [Operated Flights] )

Cancellation % =
DIVIDE ( CALCULATE ( [Scheduled Flights], fact_flights[cancelled] = 1 ), [Scheduled Flights] )

Avg Delay When Late (min) =
CALCULATE ( AVERAGE ( fact_flights[arr_delay] ), fact_flights[arr_delay] > 0 )

Delay Hours = DIVIDE ( SUM ( fact_delay_minutes[delay_minutes] ), 60 )

Avg Taxi-Out (min) = AVERAGE ( fact_flights[taxi_out] )
```

## Pages

1. **Overview:** KPI cards (On-Time %, Cancellation %, Avg Delay When Late, Scheduled Flights), monthly trend, slicers for month and airline.
2. **Delay causes:** delay hours by cause, airline ranking by On-Time %, airport ranking.
3. **Ground operations:** heatmap of average taxi-out by airport (rows) and scheduled departure hour (columns).
