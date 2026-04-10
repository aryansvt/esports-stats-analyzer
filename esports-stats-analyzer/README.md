# Esports Stats Analyzer

An esports analytics dashboard built with Python, Pandas, SQLite, and Streamlit.

This version uses real **League of Legends esports** match data and focuses on the things I cared about most for the project:
- storing structured stats in SQLite
- ranking players and teams by useful performance metrics
- comparing recent form across leagues, splits, and years
- keeping the app clean enough to actually use

## What it does

- pulls in real yearly Oracle's Elixir snapshots and stores them in SQLite
- calculates player stats like **KDA, win rate, kill participation, average kills, damage, and vision**
- calculates team stats like **win rate, dragons, towers, first blood rate, and early-game gold difference**
- lets you filter by **year, league, split, role, playoffs, and date range**
- includes side-by-side player and team comparison views

## Stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly

## Data source

The app is built around real professional League of Legends esports data from **Oracle's Elixir**.

The rebuild scripts now support **multiple yearly snapshots**, so you can load one year or several years into the same SQLite database and switch between them from the dashboard.

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
py -m pip install -r requirements.txt
```

Start the app:

```bash
py -m streamlit run streamlit_app.py
```

## Rebuild the database

### Build from a few years

```bash
py scripts/download_snapshot.py --years 2022 2023 2024
py scripts/build_database.py --years 2022 2023 2024
```
Something to note: 2025 is included in the analyzer filters but is unable to pull data from. 

### Build from every available year

```bash
py scripts/download_snapshot.py --all-years
py scripts/build_database.py --all-years
```

After rebuilding, run the app again and use the **Year** filter in the sidebar.

## Notes

- The included database may only contain those specific snapshots until you rebuild it
- The multi-year setup uses yearly Oracle's Elixir files so the dashboard can switch cleanly across seasons
