"""In-memory DuckDB copy of the stats data, loaded from Parquet files.

DATA_SOURCE is a folder containing player_stats.parquet and game_totals.parquet
(defaults to ./data, created by scripts/export_to_parquet.py).
"""
import os
import threading
from pathlib import Path

import duckdb

DATA_SOURCE = os.environ.get("DATA_SOURCE", str(Path(__file__).parent / "data"))
TABLES = ("player_stats", "game_totals")

# One row per player per game, with whether that player's team won.
PLAYER_GAMES_VIEW = """
CREATE VIEW player_games AS
SELECT p.*, (own."Points" > opp."Points") AS won
FROM player_stats p
JOIN game_totals own ON own."gameID" = p."gameID" AND own."Team" = p."Team"
JOIN game_totals opp ON opp."gameID" = p."gameID" AND opp."Team" <> p."Team"
"""

_con = None
_lock = threading.Lock()


def _load(folder):
    con = duckdb.connect()
    for table in TABLES:
        path = (Path(folder) / f"{table}.parquet").as_posix()
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{path}')")
    con.execute(PLAYER_GAMES_VIEW)
    return con


def _connection():
    global _con
    with _lock:
        if _con is None:
            _con = _load(DATA_SOURCE)
        return _con


def query(sql, params=None):
    """Run a query with $name parameters and return all rows as tuples."""
    # cursor() gives each call its own connection handle, so threads don't share state
    return _connection().cursor().execute(sql, params or {}).fetchall()
