"""Export the Postgres tables to Parquet files for the DuckDB data layer.

Usage:
    PG_URL=postgresql://user:pass@localhost/NBA2K22 python scripts/export_to_parquet.py [out_dir]

out_dir defaults to ./data. Upload the resulting files to S3 for the deployed site.
"""
import os
import sys
from pathlib import Path

import duckdb

# Postgres table -> Parquet file name
TABLES = {"PlayerStats": "player_stats", "GameTotals": "game_totals"}


def main():
    pg_url = os.environ.get("PG_URL")
    if not pg_url:
        sys.exit("Set PG_URL to your Postgres connection URL first.")

    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    out_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    con.execute("INSTALL postgres")
    con.execute("LOAD postgres")
    con.execute("ATTACH '" + pg_url.replace("'", "''") + "' AS pg (TYPE postgres, READ_ONLY)")

    for table, file_name in TABLES.items():
        path = (out_dir / f"{file_name}.parquet").as_posix()
        con.execute(f'COPY (SELECT * FROM pg.public."{table}" ORDER BY id) TO \'{path}\' (FORMAT parquet)')
        rows = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchone()[0]
        print(f"{table} -> {path} ({rows} rows)")


if __name__ == "__main__":
    main()
