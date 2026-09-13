"""In-memory DuckDB copy of the stats data, loaded from Parquet files.

DATA_SOURCE holds player_stats.parquet and game_totals.parquet, plus screenshots.parquet when
the box-score screenshots have been imported. It is either a local folder (defaults to ./data,
created by scripts/export_to_parquet.py) or an S3 prefix like s3://bucket/data, in which case
the files are downloaded to the temp folder first. Results of @cached functions are kept until
those files change.
"""
import functools
import os
import tempfile
import threading
import time
from pathlib import Path

import duckdb

DATA_SOURCE = os.environ.get("DATA_SOURCE", str(Path(__file__).parent / "data"))
TABLES = ("player_stats", "game_totals")
# Loaded only when present: the screenshot index written by scripts/import_screenshots.py
OPTIONAL_TABLES = ("screenshots",)
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
_s3 = None


def _s3_client():
    global _s3
    if _s3 is None:
        import boto3  # only needed when the data is in S3
        _s3 = boto3.client("s3")
    return _s3


def _s3_location(source, table):
    """Bucket and key of a table's Parquet file under an s3://bucket/prefix source."""
    bucket, _, prefix = source.removeprefix("s3://").partition("/")
    prefix = prefix.strip("/")
    return bucket, f"{prefix}/{table}.parquet" if prefix else f"{table}.parquet"


def _version_of(source, table):
    """A value that changes when the table's file changes, or None if an optional file is missing."""
    if source.startswith("s3://"):
        bucket, key = _s3_location(source, table)
        try:
            return _s3_client().head_object(Bucket=bucket, Key=key)["ETag"]
        except Exception:
            if table in OPTIONAL_TABLES:
                return None
            raise
    path = Path(source) / f"{table}.parquet"
    if table in OPTIONAL_TABLES and not path.exists():
        return None
    return path.stat().st_mtime_ns


def _files_version(source):
    return tuple(_version_of(source, table) for table in TABLES + OPTIONAL_TABLES)


def _local_folder(source, tables):
    """Folder with the tables' Parquet files, downloading them from S3 first if needed."""
    if not source.startswith("s3://"):
        return source
    folder = Path(tempfile.gettempdir()) / "nba2k22-data"
    folder.mkdir(exist_ok=True)
    for table in tables:
        bucket, key = _s3_location(source, table)
        _s3_client().download_file(bucket, key, str(folder / f"{table}.parquet"))
    return folder


def _load(folder, tables):
    con = duckdb.connect()
    for table in tables:
        path = (Path(folder) / f"{table}.parquet").as_posix()
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{path}')")
    con.execute(PLAYER_GAMES_VIEW)
    return con


def _refresh():
    """Return the connection, reloading it (and dropping cached results) if the files changed."""
    global _con, _version, _checked_at
    with _lock:
        now = time.monotonic()
        if _con is not None and now - _checked_at < VERSION_CHECK_SECONDS:
            return _con
        version = _files_version(DATA_SOURCE)
        if version != _version:
            present = [table for table, v in zip(TABLES + OPTIONAL_TABLES, version) if v is not None]
            _con = _load(_local_folder(DATA_SOURCE, present), present)
            _version = version
            _cache.clear()
        _checked_at = now
        return _con


def query(sql, params=None):
    """Run a query with $name parameters and return all rows as tuples."""
    # cursor() gives each call its own connection handle, so threads don't share state
    return _refresh().cursor().execute(sql, params or {}).fetchall()


def has_table(name):
    return query("SELECT count(*) FROM information_schema.tables WHERE table_name = $name", {"name": name})[0][0] > 0


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
