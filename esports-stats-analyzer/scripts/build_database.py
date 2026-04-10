from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import DB_PATH, RAW_CSV_PATH, SNAPSHOT_URL
from src.data_loader import download_snapshot


PLAYER_POSITIONS = ['top', 'jng', 'mid', 'bot', 'sup']

PLAYER_COLUMNS = [
    'gameid', 'league', 'year', 'split', 'playoffs', 'date', 'patch', 'side', 'position',
    'playername', 'playerid', 'teamname', 'teamid', 'champion', 'gamelength', 'result',
    'teamkills', 'teamdeaths', 'kills', 'deaths', 'assists',
    'doublekills', 'triplekills', 'quadrakills', 'pentakills',
    'damagetochampions', 'visionscore', 'earned gpm', 'cspm',
    'goldat15', 'xpat15', 'csat15', 'killsat15', 'assistsat15', 'deathsat15',
]

TEAM_COLUMNS = [
    'gameid', 'league', 'year', 'split', 'playoffs', 'date', 'patch', 'side',
    'teamname', 'teamid', 'gamelength', 'result', 'kills', 'deaths', 'assists',
    'firstblood', 'firstdragon', 'firstherald', 'firstbaron', 'firsttower', 'firstmidtower', 'firsttothreetowers',
    'dragons', 'heralds', 'barons', 'towers',
    'team kpm', 'ckpm', 'earned gpm',
    'goldat15', 'xpat15', 'csat15', 'golddiffat15', 'xpdiffat15', 'csdiffat15',
    'killsat15', 'assistsat15', 'deathsat15',
]


def build_database(csv_path: Path = RAW_CSV_PATH, db_path: Path = DB_PATH) -> None:
    if not csv_path.exists():
        print('Snapshot not found locally. Downloading it now...')
        download_snapshot(csv_path)

    df = pd.read_csv(csv_path, low_memory=False)

    players = df[df['position'].isin(PLAYER_POSITIONS)][PLAYER_COLUMNS].rename(
        columns={
            'earned gpm': 'earned_gpm',
            'teamkills': 'team_kills',
            'teamdeaths': 'team_deaths',
        }
    )

    teams = df[df['position'] == 'team'][TEAM_COLUMNS].rename(
        columns={
            'team kpm': 'team_kpm',
            'earned gpm': 'earned_gpm',
        }
    )

    for frame in (players, teams):
        frame['date'] = pd.to_datetime(frame['date'], errors='coerce')
        frame['playoffs'] = pd.to_numeric(frame['playoffs'], errors='coerce').fillna(0).astype(int)
        protected = {
            'gameid', 'league', 'split', 'date', 'patch', 'side', 'position',
            'playername', 'playerid', 'teamname', 'teamid', 'champion',
        }
        for column in frame.columns:
            if column not in protected and column != 'playoffs':
                frame[column] = pd.to_numeric(frame[column], errors='coerce')

    players = players.dropna(subset=['playername', 'teamname', 'date']).copy()
    teams = teams.dropna(subset=['teamname', 'date']).copy()

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        players.to_sql('players', conn, index=False)
        teams.to_sql('teams', conn, index=False)
        metadata = pd.DataFrame([
            {
                'source_name': "Oracle's Elixir 2022 LoL esports snapshot",
                'source_url': SNAPSHOT_URL,
                'player_rows': len(players),
                'team_rows': len(teams),
            }
        ])
        metadata.to_sql('metadata', conn, index=False)

        cursor = conn.cursor()
        for statement in [
            'CREATE INDEX idx_players_date ON players(date);',
            'CREATE INDEX idx_players_league ON players(league);',
            'CREATE INDEX idx_players_name ON players(playername);',
            'CREATE INDEX idx_players_team ON players(teamname);',
            'CREATE INDEX idx_teams_date ON teams(date);',
            'CREATE INDEX idx_teams_league ON teams(league);',
            'CREATE INDEX idx_teams_name ON teams(teamname);',
        ]:
            cursor.execute(statement)
        conn.commit()

    print(f'Built database at {db_path}')
    print(f'Players rows: {len(players):,}')
    print(f'Team rows: {len(teams):,}')


if __name__ == '__main__':
    build_database()
