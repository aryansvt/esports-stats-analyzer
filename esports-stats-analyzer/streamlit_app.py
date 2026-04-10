from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.analytics import (
    build_player_leaderboard,
    build_team_leaderboard,
    filter_players,
    filter_teams,
    summary_metrics,
    top_recent_players,
    top_recent_teams,
)
from src.config import DEFAULT_YEARS
from src.data_loader import load_metadata, load_players, load_teams
from src.ui_helpers import format_leaderboard, render_metric_card


st.set_page_config(page_title='Esports Stats Analyzer', page_icon='🎮', layout='wide')

st.title('Esports Stats Analyzer')
st.caption('League of Legends esports data explorer built with Python, Pandas, SQLite, and Streamlit.')

players = load_players()
teams = load_teams()
metadata = load_metadata()

min_date = players['date'].min().date()
max_date = players['date'].max().date()
all_years = sorted(players['year'].dropna().astype(int).unique().tolist())
all_leagues = sorted(players['league'].dropna().unique().tolist())
all_splits = sorted(players['split'].dropna().unique().tolist())
all_positions = ['top', 'jng', 'mid', 'bot', 'sup']
default_years = [int(year) for year in DEFAULT_YEARS if int(year) in all_years] or all_years[-3:] or all_years

with st.sidebar:
    st.header('Filters')
    selected_years = st.multiselect('Year', all_years, default=default_years)
    selected_leagues = st.multiselect('League', all_leagues, default=['LCK', 'LPL', 'LEC', 'LCS'] if set(['LCK', 'LPL', 'LEC', 'LCS']).issubset(set(all_leagues)) else all_leagues[:4])
    selected_splits = st.multiselect('Split', all_splits, default=all_splits)
    selected_positions = st.multiselect('Player roles', all_positions, default=all_positions)
    selected_dates = st.date_input('Date range', value=(min_date, max_date), min_value=min_date, max_value=max_date)
    playoffs_only = st.checkbox('Playoffs only')
    min_games = st.slider('Minimum games', min_value=1, max_value=30, value=5)
    st.markdown('---')
    with st.expander('Data source', expanded=False):
        if not metadata.empty:
            st.write(metadata.loc[0, 'source_name'])
            if 'years_loaded' in metadata.columns:
                st.caption(f"Years loaded: {metadata.loc[0, 'years_loaded']}")
            st.caption('SQLite snapshot ships with the repo so the dashboard runs immediately once the database is built.')

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    date_range = selected_dates
else:
    date_range = (min_date, max_date)

filtered_players = filter_players(players, selected_years, selected_leagues, selected_splits, date_range, playoffs_only, selected_positions)
filtered_teams = filter_teams(teams, selected_years, selected_leagues, selected_splits, date_range, playoffs_only)

player_board = build_player_leaderboard(filtered_players, min_games=min_games)
team_board = build_team_leaderboard(filtered_teams, min_games=min_games)
metrics = summary_metrics(filtered_players, filtered_teams)

overview_tab, players_tab, teams_tab, compare_tab = st.tabs(['Overview', 'Player Rankings', 'Team Rankings', 'Compare'])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card('Matches', f"{metrics['matches']:,}")
    with col2:
        render_metric_card('Players', f"{metrics['players']:,}")
    with col3:
        render_metric_card('Teams', f"{metrics['teams']:,}")
    with col4:
        render_metric_card('Avg KDA', f"{metrics['avg_kda']:.2f}")

    left, right = st.columns(2)
    with left:
        st.subheader('Top players right now')
        recent_players = top_recent_players(filtered_players, min_games=min_games, limit=10)
        if recent_players.empty:
            st.info('No player results match the current filters.')
        else:
            recent_player_chart = recent_players[['playername', 'recent_win_rate']].copy()
            recent_player_chart['recent_win_rate'] *= 100
            fig = px.bar(recent_player_chart.sort_values('recent_win_rate'), x='recent_win_rate', y='playername', orientation='h', title='Recent 5-game win rate')
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig, width='stretch')

    with right:
        st.subheader('Top teams right now')
        recent_teams = top_recent_teams(filtered_teams, min_games=min_games, limit=10)
        if recent_teams.empty:
            st.info('No team results match the current filters.')
        else:
            recent_team_chart = recent_teams[['teamname', 'recent_win_rate']].copy()
            recent_team_chart['recent_win_rate'] *= 100
            fig = px.bar(recent_team_chart.sort_values('recent_win_rate'), x='recent_win_rate', y='teamname', orientation='h', title='Recent 5-game win rate')
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            st.plotly_chart(fig, width='stretch')

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader('Best player KDA')
        if not player_board.empty:
            fig = px.bar(player_board.head(10).sort_values('kda'), x='kda', y='playername', color='position', orientation='h')
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), legend_title_text='')
            st.plotly_chart(fig, width='stretch')
        else:
            st.info('No player data to show.')

    with chart_col2:
        st.subheader('Best team early-game gold diff')
        if not team_board.empty:
            fig = px.bar(team_board.head(10).sort_values('avg_gold15_diff'), x='avg_gold15_diff', y='teamname', orientation='h')
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info('No team data to show.')

with players_tab:
    st.subheader('Player leaderboard')
    player_sort = st.selectbox(
        'Sort players by',
        ['kda', 'win_rate', 'recent_win_rate', 'avg_kills', 'avg_damage', 'kill_participation', 'avg_vision', 'avg_cspm'],
        index=0,
    )
    player_table = player_board.sort_values(player_sort, ascending=False).copy()
    if player_table.empty:
        st.info('No player rows match the current filters.')
    else:
        player_table = format_leaderboard(player_table)
        display_cols = [
                'playername', 'teamname', 'position', 'games', 'win_rate', 'kda', 'avg_kills', 'avg_deaths',
                'avg_assists', 'kill_participation', 'avg_damage', 'avg_vision', 'avg_cspm', 'recent_form', 'recent_win_rate'
            ]
        st.dataframe(
            player_table[display_cols],
            width='stretch',
            hide_index=True,
        )
        st.download_button(
            'Download player leaderboard (CSV)',
            player_table[display_cols].to_csv(index=False),
            file_name='player_leaderboard.csv',
            mime='text/csv',
        )

with teams_tab:
    st.subheader('Team leaderboard')
    team_sort = st.selectbox(
        'Sort teams by',
        ['win_rate', 'recent_win_rate', 'avg_gold15_diff', 'avg_dragons', 'avg_towers', 'firstblood_rate'],
        index=0,
    )
    team_table = team_board.sort_values(team_sort, ascending=False).copy()
    if team_table.empty:
        st.info('No team rows match the current filters.')
    else:
        team_table = format_leaderboard(team_table)
        display_cols = [
                'teamname', 'games', 'win_rate', 'avg_kills', 'avg_deaths', 'avg_dragons', 'avg_barons', 'avg_towers',
                'avg_gold15_diff', 'avg_xp15_diff', 'firstblood_rate', 'firstdragon_rate', 'firstbaron_rate',
                'recent_form', 'recent_win_rate'
            ]
        st.dataframe(
            team_table[display_cols],
            width='stretch',
            hide_index=True,
        )
        st.download_button(
            'Download team leaderboard (CSV)',
            team_table[display_cols].to_csv(index=False),
            file_name='team_leaderboard.csv',
            mime='text/csv',
        )

with compare_tab:
    compare_mode = st.radio('Compare', ['Players', 'Teams'], horizontal=True)
    if compare_mode == 'Players':
        options = player_board['playername'].drop_duplicates().tolist()
        selected = st.multiselect('Choose up to 4 players', options, max_selections=4)
        if selected:
            comp = player_board[player_board['playername'].isin(selected)].copy()
            chart_metric = st.selectbox('Metric', ['kda', 'win_rate', 'recent_win_rate', 'avg_kills', 'avg_damage', 'kill_participation'])
            if chart_metric in {'win_rate', 'recent_win_rate', 'kill_participation'}:
                comp[chart_metric] *= 100
            fig = px.bar(comp, x='playername', y=chart_metric, color='teamname', barmode='group')
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), legend_title_text='')
            st.plotly_chart(fig, width='stretch')
            st.dataframe(format_leaderboard(comp), width='stretch', hide_index=True)
        else:
            st.info('Pick at least one player to compare.')
    else:
        options = team_board['teamname'].drop_duplicates().tolist()
        selected = st.multiselect('Choose up to 4 teams', options, max_selections=4)
        if selected:
            comp = team_board[team_board['teamname'].isin(selected)].copy()
            chart_metric = st.selectbox('Metric', ['win_rate', 'recent_win_rate', 'avg_gold15_diff', 'avg_dragons', 'avg_towers', 'firstblood_rate'])
            if chart_metric in {'win_rate', 'recent_win_rate', 'firstblood_rate'}:
                comp[chart_metric] *= 100
            fig = px.bar(comp, x='teamname', y=chart_metric, color='teamname', barmode='group')
            fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
            st.plotly_chart(fig, width='stretch')
            st.dataframe(format_leaderboard(comp), width='stretch', hide_index=True)
        else:
            st.info('Pick at least one team to compare.')
