from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from .config import CSV_FILES, DB_PATH, raw_csv_path_for_year
from .database import get_connection


@st.cache_data(show_spinner=False)
def load_players() -> pd.DataFrame:
    with get_connection(DB_PATH) as conn:
        players = pd.read_sql_query('SELECT * FROM players', conn, parse_dates=['date'])
    players['date'] = pd.to_datetime(players['date'])
    return players


@st.cache_data(show_spinner=False)
def load_teams() -> pd.DataFrame:
    with get_connection(DB_PATH) as conn:
        teams = pd.read_sql_query('SELECT * FROM teams', conn, parse_dates=['date'])
    teams['date'] = pd.to_datetime(teams['date'])
    return teams


@st.cache_data(show_spinner=False)
def load_metadata() -> pd.DataFrame:
    with get_connection(DB_PATH) as conn:
        metadata = pd.read_sql_query('SELECT * FROM metadata', conn)
    return metadata


def download_snapshot(year: str | int, target_path: Path | None = None) -> Path:
    year = str(year)
    if year not in CSV_FILES:
        raise ValueError(f'Year {year} is not available. Choose from: {", ".join(sorted(CSV_FILES))}')

    target_path = target_path or raw_csv_path_for_year(year)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(CSV_FILES[year], stream=True, timeout=180) as response:
        response.raise_for_status()
        with open(target_path, 'wb') as file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_handle.write(chunk)

    return target_path
