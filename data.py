"""In-memory DuckDB copy of the stats data, loaded from Parquet files.

DATA_SOURCE is a folder containing player_stats.parquet and game_totals.parquet
(defaults to ./data, created by scripts/export_to_parquet.py).
Results of @cached functions are kept until those files change.
"""
import functools
import os
import threading
import time
from pathlib import Path

import duckdb

DATA_SOURCE = os.environ.get("DATA_SOURCE", str(Path(__file__).parent / "data"))
TABLES = ("player_stats", "game_totals")
# How often to check whether the data files changed
VERSION_CHECK_SECONDS = 60

# One row per player per game, with whether that player's team won.
PLAYER_GAMES_VIEW = """
CREATE VIEW player_games AS
SELECT p.*, (own."Points" > opp."Points") AS won
FROM player_stats p
JOIN game_totals own ON own."gameID" = p."gameID" AND own."Team" = p."Team"
JOIN game_totals opp ON opp."gameID" = p."gameID" AND opp."Team" <> p."Team"
"""

_con = None
_version = None
_checked_at = 0.0
_cache = {}
_lock = threading.Lock()


def _load(folder):
    con = duckdb.connect()
    for table in TABLES:
        path = (Path(folder) / f"{table}.parquet").as_posix()
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{path}')")
    con.execute(PLAYER_GAMES_VIEW)
    return con


def _files_version(folder):
    return tuple((Path(folder) / f"{table}.parquet").stat().st_mtime_ns for table in TABLES)


def _refresh():
    """Return the connection, reloading it (and dropping cached results) if the files changed."""
    global _con, _version, _checked_at
    with _lock:
        now = time.monotonic()
        if _con is not None and now - _checked_at < VERSION_CHECK_SECONDS:
            return _con
        version = _files_version(DATA_SOURCE)
        if version != _version:
            _con = _load(DATA_SOURCE)
            _version = version
            _cache.clear()
        _checked_at = now
        return _con


def query(sql, params=None):
    """Run a query with $name parameters and return all rows as tuples."""
    # cursor() gives each call its own connection handle, so threads don't share state
    return _refresh().cursor().execute(sql, params or {}).fetchall()


def cached(fn):
    """Keep fn's results until the data changes."""
    @functools.wraps(fn)
    def wrapper(*args):
        _refresh()
        key = (fn.__name__, args)
        if key not in _cache:
            _cache[key] = fn(*args)
        return _cache[key]
    return wrapper
