"""Stat page calculations. Each stat page is a single SQL query over the player_games view."""
from collections import namedtuple
from datetime import datetime, timedelta

from data import cached, has_table, query

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


class StatLine(namedtuple("StatLine", "label games wins pts reb ast stl blk fouls tov "
                                      "fgm fga fg_pct tpm tpa tp_pct")):
    """One row of STAT_COLUMNS with its label: per-game averages and shooting percentages."""
    __slots__ = ()

    @property
    def losses(self):
        return self.games - self.wins

    @property
    def win_pct(self):
        return 100 * self.wins / self.games


def _lines(sql, params=None):
    return [StatLine(*row) for row in query(sql, params)]


def _format_row(line):
    return [line.label, line.games, f"{line.wins}-{line.losses}", f"{line.win_pct:.2f}",
            *(f"{value:.2f}" for value in line[3:])]


@cached
def names():
    return [row[0] for row in query('SELECT DISTINCT "Name" FROM player_stats ORDER BY 1')]


@cached
def positions_of(name):
    """Positions a player has played, in the usual PG to C order."""
    played = {row[0] for row in query('SELECT DISTINCT "Position" FROM player_stats WHERE "Name" = $name',
                                      {"name": name})}
    return [pos for pos in POSITIONS if pos in played]


@cached
def position_owners():
    """The player with the most games at each position: [(position, name, games)]."""
    owners = []
    for pos in POSITIONS:
        row = query('SELECT "Name", count(*) FROM player_stats WHERE "Position" = $pos '
                    'GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 1', {"pos": pos})
        if row:
            owners.append((pos, row[0][0], row[0][1]))
    return owners


@cached
def average_lines(pos=None):
    if pos is None:
        return _lines(f'SELECT "Name", {STAT_COLUMNS} FROM player_games GROUP BY "Name" HAVING count(*) >= 10')
    return _lines(f'SELECT "Name", {STAT_COLUMNS} FROM player_games WHERE "Position" = $pos GROUP BY "Name"',
                  {"pos": pos})


@cached
def career_averages(pos=None):
    title = "CAREER AVERAGES" if pos is None else "AVERAGE STATS AT " + pos
    return title, ['Name', 'Games Played', *STAT_HEADERS], [_format_row(line) for line in average_lines(pos)]


def _label_lines(name, labels_sql, pos=None):
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
    return _lines(sql, {"name": name, "pos": pos} if pos else {"name": name})


# Opponent = the other player at the same position in that game
MATCHUP_LABELS = """
    SELECT m."gameID", string_agg(o."Name", ', ' ORDER BY o."Name") AS label
    FROM mine m
    JOIN player_stats o ON o."gameID" = m."gameID" AND o."Position" = m."Position" AND o."Name" <> m."Name"
    GROUP BY m."gameID"
"""
# Label = everyone else on the player's team that game
LINEUP_LABELS = """
    SELECT m."gameID", string_agg(t."Name", ', ' ORDER BY t."Name") AS label
    FROM mine m
    JOIN player_stats t ON t."gameID" = m."gameID" AND t."Team" = m."Team" AND t."Name" <> m."Name"
    GROUP BY m."gameID"
"""
# One label per teammate per game, so every game with them counts once in their row
TEAMMATE_LABELS = """
    SELECT DISTINCT m."gameID", t."Name" AS label
    FROM mine m
    JOIN player_stats t ON t."gameID" = m."gameID" AND t."Team" = m."Team" AND t."Name" <> m."Name"
"""


@cached
def matchup_lines(name, pos=None):
    return _label_lines(name, MATCHUP_LABELS, pos)


@cached
def lineup_lines(name):
    return _label_lines(name, LINEUP_LABELS)


@cached
def teammate_lines(name):
    return _label_lines(name, TEAMMATE_LABELS)


@cached
def matchups(name, pos=None):
    if pos is None:
        title = name + "'s Stats When Matched Up Against:"
    else:
        title = name + "'s " + pos + " Stats When Matched Up Against:"
    return title, ['Opponent', 'Occurences', *STAT_HEADERS], [_format_row(line) for line in matchup_lines(name, pos)]


@cached
def teammate_combos(name):
    title = name + "'s Stats When He Plays With"
    return title, ['Teammates', 'Occurences', *STAT_HEADERS], [_format_row(line) for line in lineup_lines(name)]


@cached
def single_teammate(name):
    title = name + "'s Stats When He Plays With"
    return title, ['Teammate', 'Occurences', *STAT_HEADERS], [_format_row(line) for line in teammate_lines(name)]


@cached
def career_highs(cat):
    if cat not in ALLOWED_CATS:
        raise ValueError(f"Unknown category: {cat}")
    rows = query(f'SELECT "Name", max("{cat}") FROM player_stats GROUP BY "Name"')
    return "CAREER HIGHS - " + cat.upper(), ['Name', cat], [[name, int(value)] for name, value in rows]


@cached
def record_holders(cat):
    """Each player's best game in a category, best first: (name, value, game id).

    When a player matched their best more than once, the first time counts.
    """
    if cat not in ALLOWED_CATS:
        raise ValueError(f"Unknown category: {cat}")
    rows = query(f"""
        SELECT "Name", "{cat}", "gameID" FROM (
            SELECT "Name", "{cat}", "gameID",
                   row_number() OVER (PARTITION BY "Name"
                                      ORDER BY "{cat}" DESC, regexp_extract("gameID", '(\\d{{14}})', 1)) AS pick
            FROM player_stats)
        WHERE pick = 1
        ORDER BY "{cat}" DESC, "Name"
    """)
    return [(name, int(value), game_id) for name, value, game_id in rows]


@cached
def record_board():
    """The top value in every category and everyone who reached it: (category, value, holders)."""
    board = []
    for cat in ALLOWED_CATS:
        holders = record_holders(cat)
        best = holders[0][1]
        board.append((cat, best, [holder for holder in holders if holder[1] == best]))
    return board


# ---------------------------------------------------------------------------
# Box scores for the game log

Player = namedtuple("Player", "name position grade points rebounds assists steals blocks fouls turnovers "
                              "fgm fga tpm tpa")
Team = namedtuple("Team", "side points grade players")
Game = namedtuple("Game", "id played teams winner")


def _played(game_id):
    """When the game was played, or None for the games entered later without their date."""
    if not game_id.startswith("NBA2K22_"):
        return None
    return datetime.strptime(game_id[-14:], "%Y%m%d%H%M%S")


def night_of(played):
    """Sessions run past midnight, so anything before 6 am counts as the evening before."""
    return (played - timedelta(hours=6)).date()


def _grade(text):
    # Two team grades were typed with stray spaces or dashes ("A -", "B- -")
    cleaned = (text or "").replace(" ", "")
    return cleaned[:2] if len(cleaned) > 2 else cleaned


@cached
def box_scores():
    """Every game, newest first, with the undated games last."""
    players = {}
    for game_id, side, name, position, grade, *numbers in query("""
        SELECT "gameID", "Team", "Name", "Position", "Grade", "Points", "Rebounds", "Assists", "Steals",
               "Blocks", "Fouls", "Turnovers", "FGM", "FGA", "3PM", "3PA"
        FROM player_stats
        ORDER BY "Points" DESC, "Name"
    """):
        players.setdefault((game_id, side), []).append(
            Player(name, position, _grade(grade), *(int(number) for number in numbers)))

    teams = {}
    for game_id, side, points, grade in query('SELECT "gameID", "Team", "Points", "Grade" FROM game_totals'):
        teams.setdefault(game_id, {})[side] = Team(side, int(points), _grade(grade), players.get((game_id, side), []))

    games = []
    for game_id, sides in teams.items():
        t1, t2 = sides["T1"], sides["T2"]
        winner = "T1" if t1.points > t2.points else "T2" if t2.points > t1.points else None
        games.append(Game(game_id, _played(game_id), (t1, t2), winner))
    games.sort(key=lambda game: (game.played is not None, game.played or datetime.min, game.id), reverse=True)
    return games


@cached
def _games_by_id():
    return {game.id: game for game in box_scores()}


def game(game_id):
    return _games_by_id().get(game_id)


@cached
def screenshots():
    """The box-score screenshot for each game that has one: {game id: (file, width, height)}."""
    if not has_table("screenshots"):
        return {}
    return {game_id: (file, width, height)
            for game_id, file, width, height in query('SELECT "gameID", file, width, height FROM screenshots')}


def player_in(game, name):
    """(team, player line) for a player in a game, or None if they didn't play."""
    for team in game.teams:
        for player in team.players:
            if player.name == name:
                return team, player
    return None


def find_games(name=None, pos=None, with_=(), vs=None, exact=False):
    """Games for the game log's filters, newest first.

    The other filters only apply with a player: pos is their position that game, with_ their
    teammates (exact means exactly those teammates) and vs their same-position opponent.
    """
    if not name:
        return box_scores()
    wanted = set(with_)
    found = []
    for game in box_scores():
        seat = player_in(game, name)
        if seat is None:
            continue
        team, me = seat
        if pos and me.position != pos:
            continue
        mates = {player.name for player in team.players if player.name != name}
        if (mates != wanted) if (exact and wanted) else not wanted <= mates:
            continue
        if vs and not any(player.name == vs and player.position == me.position
                          for side in game.teams for player in side.players if player.name != name):
            continue
        found.append(game)
    return found


# ---------------------------------------------------------------------------
# Landing page

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

    top = max(average_lines(), key=lambda line: line.pts, default=None)
    leader = None
    if top:
        leader = {"name": top.label, "ppg": f"{top.pts:.1f}", "win_pct": f"{top.win_pct:.1f}",
                  "fg_pct": f"{top.fg_pct:.1f}"}

    points = record_holders("Points")
    record = {"name": points[0][0], "points": points[0][1], "game_id": points[0][2]} if points else None

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
        "record": record,
        "duo": _duo(*duo[0]) if duo else None,
        "rivalry": _rivalry(*rivalry[0]) if rivalry else None,
    }
