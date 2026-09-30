"""Build the star schema in DuckDB and export each table to Parquet for Power BI.

Usage:
    python etl/build_model.py
"""
import os
from pathlib import Path

import duckdb

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATABASE = PROJECT_DIR / "data" / "flights.duckdb"
MODEL_DIR = PROJECT_DIR / "data" / "model"
TABLES = ["fact_flights", "fact_delay_minutes", "dim_date", "dim_airline", "dim_airport", "dim_delay_cause"]


def main() -> None:
    os.chdir(PROJECT_DIR)  # SQL files use paths relative to the project folder
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(DATABASE)) as con:
        con.execute((PROJECT_DIR / "sql" / "01_model.sql").read_text())
        for table in TABLES:
            target = MODEL_DIR / f"{table}.parquet"
            con.execute(f"COPY {table} TO '{target.as_posix()}' (FORMAT parquet)")
            rows = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            print(f"[ok] {table}: {rows:,} rows -> data/model/{target.name}")


if __name__ == "__main__":
    main()
