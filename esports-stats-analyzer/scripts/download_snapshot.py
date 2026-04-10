from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import RAW_CSV_PATH
from src.data_loader import download_snapshot


if __name__ == '__main__':
    download_snapshot(RAW_CSV_PATH)
    print(f"Downloaded Oracle's Elixir snapshot to {RAW_CSV_PATH}")
