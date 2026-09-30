# Airline On-Time Performance

Operational KPI analysis of US domestic flights using open data from the US Bureau of Transportation Statistics (BTS).
The project covers the full BI workflow: automated ingestion with Python, a star schema in SQL (DuckDB) and a Power BI dashboard.

> Status: **in progress**. The pipeline and data model are ready; the dashboard and findings are being built.

<!-- Once the dashboard is ready, add a screenshot and uncomment:
![Dashboard overview](images/overview.png)
-->

## Business questions

1. What share of flights arrive on time, and how does it change month to month?
2. Which airlines and airports perform best and worst?
3. What causes delays: the airline, weather, the air traffic system, security or late-arriving aircraft?
4. At which airports and hours is ground congestion (taxi-out time) highest?

## KPIs

| KPI | Definition |
| --- | --- |
| On-time performance (OTP) | % of operated flights (not cancelled or diverted) arriving less than 15 minutes late |
| Cancellation rate | % of scheduled flights cancelled |
| Average delay when late | Average arrival delay of flights that arrived late |
| Delay minutes by cause | Total delay minutes split into carrier, weather, NAS, security and late aircraft |
| Average and P90 taxi-out | Minutes from gate departure to wheels-off, by airport and hour |

## Data

- **Source:** [BTS – Reporting Carrier On-Time Performance (1987–present)](https://www.transtats.bts.gov/)
- **Granularity:** one row per scheduled flight, about 7 million flights per year
- **License:** US government public data
- Raw data is **not** stored in this repository; `etl/download.py` fetches it.

## Architecture

```
BTS monthly zip files
      │  etl/download.py     download to data/raw/
      ▼
Raw CSV (zip)
      │  etl/transform.py    clean, type and rename → data/processed/*.parquet
      ▼
Parquet files
      │  etl/build_model.py  run sql/01_model.sql in DuckDB → data/model/*.parquet
      ▼
Star schema ──► Power BI dashboard (powerbi/)
```

### Data model

| Table | Type | Grain |
| --- | --- | --- |
| `fact_flights` | Fact | One scheduled flight |
| `fact_delay_minutes` | Fact | One flight and delay cause (minutes > 0) |
| `dim_date` | Dimension | One calendar day |
| `dim_airline` | Dimension | One airline |
| `dim_airport` | Dimension | One airport |
| `dim_delay_cause` | Dimension | One delay cause |

## How to run

Requires Python 3.10+.

```bash
cd airline-on-time-performance
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python etl/download.py --year 2024 # all months, about 25-35 MB each
python etl/transform.py
python etl/build_model.py
```

Then open Power BI Desktop and load the Parquet files in `data/model/` (Get data › Parquet).
Exploration queries are in `sql/02_kpis.sql`.

## Project structure

```
airline-on-time-performance/
├── etl/
│   ├── download.py       Download monthly files from BTS
│   ├── transform.py      Clean and convert to Parquet
│   └── build_model.py    Build the star schema and export it
├── sql/
│   ├── 01_model.sql      Star schema (DuckDB)
│   └── 02_kpis.sql       KPI exploration queries
├── reference/            Airline names and delay cause descriptions
├── powerbi/              Dashboard file and design notes
└── images/               Dashboard screenshots
```

## Key findings

_Coming soon: 3 to 5 findings backed by the data, each with a chart._

## Author

**Jorge Artiaga**, Business Intelligence & Data Analyst with experience in airport operations.
[LinkedIn](https://www.linkedin.com/in/jorge-artiaga) · [GitHub](https://github.com/JorgeArtiaga)
