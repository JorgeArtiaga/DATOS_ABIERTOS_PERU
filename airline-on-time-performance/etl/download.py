"""Download monthly On-Time Performance files from the US Bureau of Transportation Statistics (BTS).

Usage:
    python etl/download.py --year 2024
    python etl/download.py --year 2024 --months 1 2 3
"""
import argparse
from pathlib import Path

import requests

BASE_URL = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
)
PROJECT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_DIR / "data" / "raw"


def download_month(year: int, month: int, force: bool = False) -> Path:
    """Download one month of flights as a zip file into data/raw. Skips files already downloaded."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / f"ontime_{year}_{month:02d}.zip"
    if target.exists() and not force:
        print(f"[skip] {target.name} already exists")
        return target

    url = BASE_URL.format(year=year, month=month)
    print(f"[download] {url}")
    partial = target.with_suffix(".part")
    with requests.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with open(partial, "wb") as file:
            for chunk in response.iter_content(chunk_size=1 << 20):
                file.write(chunk)
    partial.rename(target)
    print(f"[ok] {target.name} ({target.stat().st_size / 1e6:.1f} MB)")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--year", type=int, required=True, help="Year to download, e.g. 2024")
    parser.add_argument("--months", type=int, nargs="+", default=list(range(1, 13)), help="Months (1-12), default: all")
    parser.add_argument("--force", action="store_true", help="Download again even if the file exists")
    args = parser.parse_args()

    for month in args.months:
        download_month(args.year, month, force=args.force)


if __name__ == "__main__":
    main()
