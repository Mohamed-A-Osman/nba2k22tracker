"""Stat page calculations. Each page is a single SQL query over the player_games view."""
from data import query

POSITIONS = ("PG", "SG", "SF", "PF", "C")
# Career-high categories users can pick. Also the only column names ever put into SQL.
ALLOWED_CATS = ("Points", "Rebounds", "Assists", "Steals", "Blocks", "Turnovers", "FGM", "3PM")

STAT_HEADERS = ['W-L', 'W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG',
                'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%']

# Games, wins, per-game averages and shooting percentages for each group of rows.
STAT_COLUMNS = """
    count(*), sum(won::INT),
    avg("Points"), avg("Rebounds"), avg("Assists"), avg("Steals"), avg("Blocks"),
    avg("Fouls"), avg("Turnovers"), avg("FGM"), avg("FGA"),
    coalesce(100 * sum("FGM") / nullif(sum("FGA"), 0), 0),
    avg("3PM"), avg("3PA"),
    coalesce(100 * sum("3PM") / nullif(sum("3PA"), 0), 0)
"""


def _format_row(label, games, wins, *averages):
    return [label, games, f"{wins}-{games - wins}", f"{100 * wins / games:.2f}",
            *(f"{value:.2f}" for value in averages)]


def names():
    return [row[0] for row in query('SELECT DISTINCT "Name" FROM player_stats ORDER BY 1')]


def career_averages(pos=None):
    if pos is None:
        title = "CAREER AVERAGES"
        sql = f'SELECT "Name", {STAT_COLUMNS} FROM player_games GROUP BY "Name" HAVING count(*) >= 10'
        rows = query(sql)
    else:
        title = "AVERAGE STATS AT " + pos
        sql = f'SELECT "Name", {STAT_COLUMNS} FROM player_games WHERE "Position" = $pos GROUP BY "Name"'
        rows = query(sql, {"pos": pos})
    return title, ['Name', 'Games Played', *STAT_HEADERS], [_format_row(*row) for row in rows]


def career_highs(cat):
    if cat not in ALLOWED_CATS:
        raise ValueError(f"Unknown category: {cat}")
    rows = query(f'SELECT "Name", max("{cat}") FROM player_stats GROUP BY "Name"')
    return "CAREER HIGHS - " + cat.upper(), ['Name', cat], [[name, int(value)] for name, value in rows]
