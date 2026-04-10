# Esports Stats Analyzer

An esports analytics dashboard built with Python, Pandas, SQLite, and Streamlit.

This version uses real **League of Legends esports** match data and focuses on the things I cared about most for the project:
- storing structured stats in SQLite
- ranking players and teams by useful performance metrics
- comparing recent form across leagues, splits, and date ranges
- keeping the app clean enough to actually use

## What it does

- pulls in a real esports dataset snapshot and stores it in SQLite
- calculates player stats like **KDA, win rate, kill participation, average kills, damage, and vision**
- calculates team stats like **win rate, dragons, towers, first blood rate, and early-game gold difference**
- lets you filter by **league, split, role, playoffs, and date range**
- includes side-by-side player and team comparison views

## Stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly

## Data source

The app is built around a real 2022 professional League of Legends esports dataset sourced from **Oracle's Elixir** and downloaded through a public GitHub mirror for reproducibility.

The repo ships with a ready-to-use SQLite database so you can run the dashboard immediately. If you want to rebuild it from the raw snapshot, the scripts are included.

## Project structure

```text
esports-stats-analyzer/
├── data/
│   └── esports_stats.db
├── scripts/
│   ├── build_database.py
│   └── download_snapshot.py
├── src/
│   ├── analytics.py
│   ├── config.py
│   ├── data_loader.py
│   └── database.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## Run it locally

Create and activate a virtual environment if you want one, then install the requirements:

```bash
pip install -r requirements.txt
```
or py -m pip install -r requirements.txt

Start the app:

```bash
streamlit run streamlit_app.py
```
or py -m pip install -r requirements.txt

## Rebuild the database

If you want to pull the raw snapshot and rebuild the SQLite database yourself:

```bash
python scripts/download_snapshot.py
python scripts/build_database.py
```

## Notes

- The included database is already built, so the dashboard should run without extra setup.
- The current project uses a League of Legends dataset because it was the most practical way to make the project fully runnable with real esports stats.
- The code is organized so the data source and dashboard logic can be extended later.
