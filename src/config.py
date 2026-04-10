from pathlib import Path
from typing import Union

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
DB_PATH = DATA_DIR / 'esports_stats.db'
DEFAULT_TOP_LEAGUES = ['LCK', 'LPL', 'LEC', 'LCS', 'Worlds', 'MSI', 'PCS', 'CBLOL']

BASE_URL = 'https://drive.google.com/uc?id='
CSV_FILES = {
    '2025': BASE_URL + '1v6LRphp2kYciU4SXp0PCjEMuev1bDejc',
    '2024': BASE_URL + '1IjIEhLc9n8eLKeY-yh_YigKVWbhgGBsN',
    '2023': BASE_URL + '1XXk2LO0CsNADBB1LRGOV5rUpyZdEZ8s2',
    '2022': BASE_URL + '1EHmptHyzY8owv0BAcNKtkQpMwfkURwRy',
    '2021': BASE_URL + '1fzwTTz77hcnYjOnO9ONeoPrkWCoOSecA',
    '2020': BASE_URL + '1dlSIczXShnv1vIfGNvBjgk-thMKA5j7d',
    '2019': BASE_URL + '11eKtScnZcpfZcD3w3UrD7nnpfLHvj9_t',
    '2018': BASE_URL + '1GsNetJQOMx0QJ6_FN8M1kwGvU_GPPcPZ',
    '2017': BASE_URL + '11fx3nNjSYB0X8vKxLAbYOrS2Bu6avm9A',
    '2016': BASE_URL + '1muyfpaIqk8_0BFkgLCWXDGNgWSXoPBwG',
    '2015': BASE_URL + '1qyckLuw0-hJM8XqFhlV9l1xAbr3H78T_',
    '2014': BASE_URL + '12syQsRH2QnKrQZTQQ6G5zyVeTG2pAYvu',
}

AVAILABLE_YEARS = sorted(CSV_FILES.keys())
DEFAULT_YEARS = AVAILABLE_YEARS[-3:]


def raw_csv_path_for_year(year: Union[str, int]) -> Path:
    year = str(year)
    return RAW_DATA_DIR / f'{year}_LoL_esports_match_data.csv'