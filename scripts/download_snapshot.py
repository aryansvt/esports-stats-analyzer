from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import AVAILABLE_YEARS, DEFAULT_YEARS, raw_csv_path_for_year
from src.data_loader import download_snapshot


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download Oracle's Elixir yearly LoL snapshots")
    parser.add_argument('--years', nargs='*', default=DEFAULT_YEARS, help='Years to download (ex: --years 2022 2023 2024)')
    parser.add_argument('--all-years', action='store_true', help='Download every available year')
    args = parser.parse_args()

    years = AVAILABLE_YEARS if args.all_years else [str(year) for year in args.years]

    for year in years:
        path = download_snapshot(year, raw_csv_path_for_year(year))
        print(f'Downloaded {year} snapshot to {path}')
