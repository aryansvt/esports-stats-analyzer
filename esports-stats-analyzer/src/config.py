from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
DB_PATH = DATA_DIR / 'esports_stats.db'
RAW_CSV_PATH = RAW_DATA_DIR / '2022_LoL_esports_match_data_2022_07_25.csv'
SNAPSHOT_URL = (
    'https://github.com/vladiseki/League_of_Legends-Predicting_Wins_and_Losses/'
    'raw/refs/heads/main/2022_LoL_esports_match_data_2022_07_25.csv'
)
DEFAULT_TOP_LEAGUES = ['LCK', 'LPL', 'LEC', 'LCS', 'Worlds', 'MSI', 'PCS', 'CBLOL']
