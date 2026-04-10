from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from .config import DB_PATH, RAW_CSV_PATH, SNAPSHOT_URL
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


def download_snapshot(target_path=RAW_CSV_PATH) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(SNAPSHOT_URL, stream=True, timeout=120) as response:
        response.raise_for_status()
        with open(target_path, 'wb') as file_handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_handle.write(chunk)
