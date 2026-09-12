"""Stat page calculations. Each page is a single SQL query over the player_games view."""
from datetime import datetime

from data import cached, query

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


@cached
def names():
    return [row[0] for row in query('SELECT DISTINCT "Name" FROM player_stats ORDER BY 1')]


@cached
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


def _stats_by_label(name, labels_sql, pos=None):
    """The player's stats grouped by a label per game (e.g. who they matched up against).

    labels_sql selects ("gameID", label) rows from `mine`, the player's own games.
    Games without a label are left out.
    """
    position_filter = 'AND "Position" = $pos' if pos else ""
    sql = f"""
        WITH mine AS (SELECT * FROM player_games WHERE "Name" = $name {position_filter}),
             labels AS ({labels_sql})
        SELECT label, {STAT_COLUMNS}
        FROM mine JOIN labels USING ("gameID")
        GROUP BY label
    """
    params = {"name": name, "pos": pos} if pos else {"name": name}
    return [_format_row(*row) for row in query(sql, params)]


@cached
def matchups(name, pos=None):
    if pos is None:
        title = name + "'s Stats When Matched Up Against:"
    else:
        title = name + "'s " + pos + " Stats When Matched Up Against:"
    # Opponent = the other player at the same position in that game
    labels_sql = """
        SELECT m."gameID", string_agg(o."Name", ', ' ORDER BY o."Name") AS label
        FROM mine m
        JOIN player_stats o ON o."gameID" = m."gameID" AND o."Position" = m."Position" AND o."Name" <> m."Name"
        GROUP BY m."gameID"
    """
    return title, ['Opponent', 'Occurences', *STAT_HEADERS], _stats_by_label(name, labels_sql, pos)


@cached
def teammate_combos(name):
    title = name + "'s Stats When He Plays With"
    # Label = everyone else on the player's team that game
    labels_sql = """
        SELECT m."gameID", string_agg(t."Name", ', ' ORDER BY t."Name") AS label
        FROM mine m
        JOIN player_stats t ON t."gameID" = m."gameID" AND t."Team" = m."Team" AND t."Name" <> m."Name"
        GROUP BY m."gameID"
    """
    return title, ['Teammates', 'Occurences', *STAT_HEADERS], _stats_by_label(name, labels_sql)


@cached
def single_teammate(name):
    title = name + "'s Stats When He Plays With"
    # One label per teammate per game, so every game with them counts once in their row
    labels_sql = """
        SELECT DISTINCT m."gameID", t."Name" AS label
        FROM mine m
        JOIN player_stats t ON t."gameID" = m."gameID" AND t."Team" = m."Team" AND t."Name" <> m."Name"
    """
    return title, ['Teammate', 'Occurences', *STAT_HEADERS], _stats_by_label(name, labels_sql)


@cached
def career_highs(cat):
    if cat not in ALLOWED_CATS:
        raise ValueError(f"Unknown category: {cat}")
    rows = query(f'SELECT "Name", max("{cat}") FROM player_stats GROUP BY "Name"')
    return "CAREER HIGHS - " + cat.upper(), ['Name', cat], [[name, int(value)] for name, value in rows]


# Two players need this many games on the same team to count as a duo
DUO_MIN_GAMES = 15


def _month(timestamp):
    return datetime.strptime(timestamp[:6], "%Y%m").strftime("%B %Y") if timestamp else ""


def _duo(a, b, games, wins):
    return {"players": (a, b), "record": f"{wins}–{games - wins}"}


def _rivalry(a, b, games, a_wins):
    b_wins = games - a_wins
    leader = a if a_wins > b_wins else b if b_wins > a_wins else None
    return {"players": (a, b), "games": games, "leader": leader,
            "score": f"{max(a_wins, b_wins)}–{min(a_wins, b_wins)}"}


@cached
def landing_highlights():
    """Headline numbers for the v2 landing page."""
    games, players, first, last = query("""
        SELECT count(DISTINCT "gameID"), count(DISTINCT "Name"),
               min(regexp_extract("gameID", '(\\d{14})', 1)),
               max(regexp_extract("gameID", '(\\d{14})', 1))
        FROM player_stats
    """)[0]

    _, header, averages = career_averages()
    ppg, win_pct, fg_pct = header.index('PPG'), header.index('W%'), header.index('FG%')
    top = max(averages, key=lambda row: float(row[ppg]), default=None)
    leader = None
    if top:
        leader = {"name": top[0], "ppg": f"{float(top[ppg]):.1f}",
                  "win_pct": f"{float(top[win_pct]):.1f}", "fg_pct": f"{float(top[fg_pct]):.1f}"}

    record = max(career_highs("Points")[2], key=lambda row: row[1], default=None)

    duo = query("""
        SELECT a."Name", b."Name", count(*), sum(a.won::INT)
        FROM player_games a
        JOIN player_games b ON b."gameID" = a."gameID" AND b."Team" = a."Team" AND b."Name" > a."Name"
        GROUP BY a."Name", b."Name"
        HAVING count(*) >= $min_games
        ORDER BY avg(a.won::INT) DESC, count(*) DESC
        LIMIT 1
    """, {"min_games": DUO_MIN_GAMES})

    # Most meetings at the same position; ties go to the closest series
    rivalry = query("""
        SELECT a."Name", b."Name", count(*), sum(a.won::INT)
        FROM player_games a
        JOIN player_games b ON b."gameID" = a."gameID" AND b."Position" = a."Position"
                           AND b."Team" <> a."Team" AND b."Name" > a."Name"
        GROUP BY a."Name", b."Name"
        ORDER BY count(*) DESC, abs(2 * sum(a.won::INT) - count(*)), a."Name", b."Name"
        LIMIT 1
    """)

    return {
        "games": games,
        "players": players,
        "first_month": _month(first),
        "last_month": _month(last),
        "leader": leader,
        "record": {"name": record[0], "points": record[1]} if record else None,
        "duo": _duo(*duo[0]) if duo else None,
        "rivalry": _rivalry(*rivalry[0]) if rivalry else None,
    }
