from __future__ import annotations

import numpy as np
import pandas as pd


def apply_shared_filters(
    df: pd.DataFrame,
    years: list[int],
    leagues: list[str],
    splits: list[str],
    date_range: tuple[pd.Timestamp, pd.Timestamp],
    playoffs_only: bool,
) -> pd.DataFrame:
    filtered = df.copy()

    if years:
        filtered = filtered[filtered['year'].isin(years)]
    if leagues:
        filtered = filtered[filtered['league'].isin(leagues)]
    if splits:
        filtered = filtered[filtered['split'].isin(splits)]

    start_date, end_date = date_range
    filtered = filtered[(filtered['date'] >= pd.to_datetime(start_date)) & (filtered['date'] <= pd.to_datetime(end_date))]

    if playoffs_only:
        filtered = filtered[filtered['playoffs'] == 1]

    return filtered


def filter_players(
    players: pd.DataFrame,
    years: list[int],
    leagues: list[str],
    splits: list[str],
    date_range: tuple[pd.Timestamp, pd.Timestamp],
    playoffs_only: bool,
    positions: list[str],
) -> pd.DataFrame:
    filtered = apply_shared_filters(players, years, leagues, splits, date_range, playoffs_only)
    if positions:
        filtered = filtered[filtered['position'].isin(positions)]
    return filtered


def filter_teams(
    teams: pd.DataFrame,
    years: list[int],
    leagues: list[str],
    splits: list[str],
    date_range: tuple[pd.Timestamp, pd.Timestamp],
    playoffs_only: bool,
) -> pd.DataFrame:
    return apply_shared_filters(teams, years, leagues, splits, date_range, playoffs_only)


RESULT_MAP = {1: 'W', 0: 'L'}


def recent_form(series: pd.Series, lookback: int = 5) -> str:
    last_results = series.sort_index().tail(lookback).tolist()
    return ''.join(RESULT_MAP.get(int(value), '-') for value in last_results)


def recent_win_rate(series: pd.Series, lookback: int = 5) -> float:
    last_results = series.sort_index().tail(lookback)
    if len(last_results) == 0:
        return 0.0
    return float(last_results.mean())


def build_player_leaderboard(players: pd.DataFrame, min_games: int = 5) -> pd.DataFrame:
    if players.empty:
        return pd.DataFrame()

    ordered = players.sort_values('date')
    grouped = ordered.groupby(['playername', 'teamname', 'position'], dropna=False)

    leaderboard = grouped.agg(
        games=('gameid', 'count'),
        wins=('result', 'sum'),
        kills=('kills', 'sum'),
        deaths=('deaths', 'sum'),
        assists=('assists', 'sum'),
        avg_kills=('kills', 'mean'),
        avg_deaths=('deaths', 'mean'),
        avg_assists=('assists', 'mean'),
        avg_damage=('damagetochampions', 'mean'),
        avg_vision=('visionscore', 'mean'),
        avg_cspm=('cspm', 'mean'),
        avg_gpm=('earned_gpm', 'mean'),
        avg_team_kills=('team_kills', 'mean'),
    ).reset_index()

    kp_group = grouped.apply(
        lambda group: ((group['kills'] + group['assists']) / group['team_kills'].replace(0, np.nan)).mean(),
        include_groups=False,
    ).reset_index(name='kill_participation')

    recent_group = grouped['result'].apply(recent_form).reset_index(name='recent_form')
    recent_wr_group = grouped['result'].apply(recent_win_rate).reset_index(name='recent_win_rate')

    leaderboard = leaderboard.merge(kp_group, on=['playername', 'teamname', 'position'])
    leaderboard = leaderboard.merge(recent_group, on=['playername', 'teamname', 'position'])
    leaderboard = leaderboard.merge(recent_wr_group, on=['playername', 'teamname', 'position'])

    leaderboard['win_rate'] = leaderboard['wins'] / leaderboard['games']
    leaderboard['kda'] = np.where(
        leaderboard['deaths'] > 0,
        (leaderboard['kills'] + leaderboard['assists']) / leaderboard['deaths'],
        leaderboard['kills'] + leaderboard['assists'],
    )

    leaderboard = leaderboard[leaderboard['games'] >= min_games].copy()
    leaderboard['kill_participation'] = leaderboard['kill_participation'].fillna(0.0)
    return leaderboard.sort_values(['kda', 'win_rate', 'games'], ascending=[False, False, False])


TEAM_RATE_COLUMNS = [
    'firstblood',
    'firstdragon',
    'firstherald',
    'firstbaron',
    'firsttower',
    'firstmidtower',
    'firsttothreetowers',
]


def build_team_leaderboard(teams: pd.DataFrame, min_games: int = 5) -> pd.DataFrame:
    if teams.empty:
        return pd.DataFrame()

    ordered = teams.sort_values('date')
    grouped = ordered.groupby('teamname', dropna=False)

    agg_spec = {
        'games': ('gameid', 'count'),
        'wins': ('result', 'sum'),
        'avg_kills': ('kills', 'mean'),
        'avg_deaths': ('deaths', 'mean'),
        'avg_assists': ('assists', 'mean'),
        'avg_dragons': ('dragons', 'mean'),
        'avg_heralds': ('heralds', 'mean'),
        'avg_barons': ('barons', 'mean'),
        'avg_towers': ('towers', 'mean'),
        'avg_gold15_diff': ('golddiffat15', 'mean'),
        'avg_xp15_diff': ('xpdiffat15', 'mean'),
        'avg_cs15_diff': ('csdiffat15', 'mean'),
        'avg_ckpm': ('ckpm', 'mean'),
        'avg_team_kpm': ('team_kpm', 'mean'),
    }
    for column in TEAM_RATE_COLUMNS:
        agg_spec[f'{column}_rate'] = (column, 'mean')

    leaderboard = grouped.agg(**agg_spec).reset_index()
    leaderboard['win_rate'] = leaderboard['wins'] / leaderboard['games']
    leaderboard['recent_form'] = grouped['result'].apply(recent_form).values
    leaderboard['recent_win_rate'] = grouped['result'].apply(recent_win_rate).values

    leaderboard = leaderboard[leaderboard['games'] >= min_games].copy()
    return leaderboard.sort_values(['win_rate', 'avg_gold15_diff', 'games'], ascending=[False, False, False])


def summary_metrics(players: pd.DataFrame, teams: pd.DataFrame) -> dict[str, float | int | str]:
    if players.empty or teams.empty:
        return {
            'matches': 0,
            'players': 0,
            'teams': 0,
            'avg_kda': 0.0,
        }

    player_level_kda = np.where(
        players['deaths'] > 0,
        (players['kills'] + players['assists']) / players['deaths'],
        players['kills'] + players['assists'],
    )

    return {
        'matches': int(teams['gameid'].nunique()),
        'players': int(players['playername'].nunique()),
        'teams': int(teams['teamname'].nunique()),
        'avg_kda': float(np.mean(player_level_kda)),
    }


def top_recent_players(players: pd.DataFrame, min_games: int = 5, limit: int = 10) -> pd.DataFrame:
    board = build_player_leaderboard(players, min_games=min_games)
    if board.empty:
        return board
    return board.sort_values(['recent_win_rate', 'kda', 'games'], ascending=[False, False, False]).head(limit)


def top_recent_teams(teams: pd.DataFrame, min_games: int = 5, limit: int = 10) -> pd.DataFrame:
    board = build_team_leaderboard(teams, min_games=min_games)
    if board.empty:
        return board
    return board.sort_values(['recent_win_rate', 'win_rate', 'avg_gold15_diff'], ascending=[False, False, False]).head(limit)
