"""Match box-score screenshots to games and add them to the site's data.

Usage:
    python scripts/import_screenshots.py <folder> [<folder> ...] [--out data]

The screenshots are console captures named like "NBA 2K22_20211127012938.jpg"; the digits
are the game's ID. Each matched image is resized for the web and saved as
<out>/screenshots/<game id>.webp, and <out>/screenshots.parquet records which game each
image belongs to. When several folders hold the same game, the first one wins. Images that
match no game (for example shots taken before the final buzzer) are listed and skipped.
Run scripts/export_to_parquet.py first: it writes the player_stats.parquet this reads.
"""
import re
import sys
from pathlib import Path

import duckdb
from PIL import Image

MAX_WIDTH = 1600
QUALITY = 80


def main():
    args = sys.argv[1:]
    out = Path('data')
    if '--out' in args:
        i = args.index('--out')
        out = Path(args[i + 1])
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)

    con = duckdb.connect()
    stats_file = (out / 'player_stats.parquet').as_posix()
    game_ids = [row[0] for row in con.execute(f"SELECT DISTINCT \"gameID\" FROM read_parquet('{stats_file}')").fetchall()]
    # Prefixed IDs and the undated games' bare IDs both end in the capture timestamp
    by_stamp = {re.search(r'(\d{14})', game_id).group(1): game_id for game_id in game_ids}

    target = out / 'screenshots'
    target.mkdir(parents=True, exist_ok=True)
    rows, skipped = {}, []
    for folder in map(Path, args):
        for path in sorted(folder.iterdir()):
            if path.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
                continue
            stamp = re.search(r'(\d{14})', path.name)
            game_id = by_stamp.get(stamp.group(1)) if stamp else None
            if game_id is None:
                skipped.append(path.name)
                continue
            if game_id in rows:
                continue
            with Image.open(path) as original:
                image = original.convert('RGB')
            if image.width > MAX_WIDTH:
                image = image.resize((MAX_WIDTH, round(image.height * MAX_WIDTH / image.width)), Image.LANCZOS)
            file = f'{game_id}.webp'
            image.save(target / file, 'WEBP', quality=QUALITY, method=6)
            rows[game_id] = (game_id, file, image.width, image.height, path.name)

    con.execute('CREATE TABLE screenshots ("gameID" VARCHAR, file VARCHAR, width INTEGER, height INTEGER, source VARCHAR)')
    con.executemany('INSERT INTO screenshots VALUES (?, ?, ?, ?, ?)', list(rows.values()))
    con.execute(f"COPY screenshots TO '{(out / 'screenshots.parquet').as_posix()}' (FORMAT parquet)")

    size = sum((target / row[1]).stat().st_size for row in rows.values())
    print(f"{len(rows)} of {len(game_ids)} games have a screenshot ({size / 1e6:.1f} MB) in {target}")
    skipped = sorted(set(skipped))  # the same capture can sit in more than one folder
    if skipped:
        print(f"Skipped {len(skipped)} images that match no game: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
