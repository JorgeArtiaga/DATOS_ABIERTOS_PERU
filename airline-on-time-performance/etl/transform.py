"""Clean the raw BTS zip files and save them as Parquet, one file per month.

Keeps only the columns used in the analysis, renames them to snake_case,
fixes data types and derives the scheduled departure and arrival hour.

Usage:
    python etl/transform.py
"""
import zipfile
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

# Source column -> clean name
COLUMNS = {
    "FlightDate": "flight_date",
    "Reporting_Airline": "airline_code",
    "Flight_Number_Reporting_Airline": "flight_number",
    "Tail_Number": "tail_number",
    "Origin": "origin",
    "OriginCityName": "origin_city",
    "OriginState": "origin_state",
    "Dest": "dest",
    "DestCityName": "dest_city",
    "DestState": "dest_state",
    "CRSDepTime": "crs_dep_time",
    "DepDelay": "dep_delay",
    "DepDel15": "dep_del15",
    "TaxiOut": "taxi_out",
    "TaxiIn": "taxi_in",
    "CRSArrTime": "crs_arr_time",
    "ArrDelay": "arr_delay",
    "ArrDel15": "arr_del15",
    "Cancelled": "cancelled",
    "CancellationCode": "cancellation_code",
    "Diverted": "diverted",
    "Distance": "distance",
    "CarrierDelay": "carrier_delay",
    "WeatherDelay": "weather_delay",
    "NASDelay": "nas_delay",
    "SecurityDelay": "security_delay",
    "LateAircraftDelay": "late_aircraft_delay",
}
TEXT_COLUMNS = [
    "airline_code", "tail_number", "origin", "origin_city", "origin_state",
    "dest", "dest_city", "dest_state", "cancellation_code",
]
FLAG_COLUMNS = ["dep_del15", "arr_del15", "cancelled", "diverted"]


def read_raw_zip(path: Path) -> pd.DataFrame:
    """Read the flights CSV inside a BTS zip (the zip also holds a readme file)."""
    with zipfile.ZipFile(path) as archive:
        csv_name = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
        with archive.open(csv_name) as csv_file:
            return pd.read_csv(csv_file, usecols=list(COLUMNS), dtype=str)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMNS)

    for column in df.columns:
        if column in TEXT_COLUMNS:
            df[column] = df[column].str.strip().replace("", pd.NA).astype("string")
        elif column != "flight_date":
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["flight_date"] = pd.to_datetime(df["flight_date"]).dt.date
    df["flight_number"] = df["flight_number"].astype("Int64")
    for column in FLAG_COLUMNS:
        df[column] = df[column].astype("Int8")

    # Times come as hhmm (e.g. 1435); 2400 means midnight
    for prefix in ("dep", "arr"):
        hhmm = df[f"crs_{prefix}_time"].astype("Int64")
        df[f"crs_{prefix}_time"] = hhmm
        df[f"crs_{prefix}_hour"] = ((hhmm // 100) % 24).astype("Int8")

    return df


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("ontime_*.zip"))
    if not raw_files:
        raise SystemExit(f"No raw files in {RAW_DIR}. Run etl/download.py first.")

    for raw_file in raw_files:
        target = PROCESSED_DIR / f"{raw_file.stem}.parquet"
        df = clean(read_raw_zip(raw_file))
        df.to_parquet(target, index=False)
        print(f"[ok] {target.name}: {len(df):,} flights")


if __name__ == "__main__":
    main()
