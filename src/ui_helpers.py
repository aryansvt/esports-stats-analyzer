from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st


PERCENT_COLUMNS = {
    'win_rate',
    'recent_win_rate',
    'kill_participation',
    'firstblood_rate',
    'firstdragon_rate',
    'firstherald_rate',
    'firstbaron_rate',
    'firsttower_rate',
    'firstmidtower_rate',
    'firsttothreetowers_rate',
}


def format_leaderboard(df: pd.DataFrame, percent_columns: set[str] | None = None) -> pd.DataFrame:
    if df.empty:
        return df
    percent_columns = percent_columns or PERCENT_COLUMNS
    formatted = df.copy()
    for column in formatted.columns:
        if column in percent_columns:
            formatted[column] = (formatted[column] * 100).round(1)
        elif pd.api.types.is_numeric_dtype(formatted[column]):
            formatted[column] = formatted[column].round(2)
    return formatted


def render_metric_card(label: str, value: str | int | float) -> None:
    st.markdown(
        f"""
        <div style='padding: 1rem 1.1rem; border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; background: rgba(16,18,24,0.95);'>
            <div style='font-size: 0.85rem; color: #9aa4b2; margin-bottom: 0.35rem;'>{label}</div>
            <div style='font-size: 1.7rem; font-weight: 700; color: #f8fafc;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, title: str | None = None):
    if df.empty:
        return None
    fig = px.bar(df, x=x, y=y, color=color, title=title)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text='')
    return fig
