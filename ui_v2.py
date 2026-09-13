"""v2 UI, served at the site root: the game log and the stat pages built around it.

Every stat row links to the games behind it, and those links always find exactly the
number of games the row shows.
"""
from flask import Blueprint, abort, render_template, request, url_for

import stats

bp = Blueprint('v2', __name__)

# (endpoints that mark the link as the current page, label)
NAV_ITEMS = [
    (('v2.games', 'v2.game'), 'Games'),
    (('v2.averages',), 'Averages'),
    (('v2.matchups',), 'Matchups'),
    (('v2.teammates',), 'Teammates'),
    (('v2.highs',), 'Highs'),
    (('v2.upload',), 'Upload'),
]

# Table columns after name, games and W-L: (StatLine field, header, full name, decimals, behind "More stats")
COLUMNS = [
    ('win_pct', 'W%', 'Win percentage', 1, False),
    ('pts', 'PPG', 'Points per game', 2, False),
    ('reb', 'RPG', 'Rebounds per game', 2, False),
    ('ast', 'APG', 'Assists per game', 2, False),
    ('fg_pct', 'FG%', 'Field goal percentage', 1, False),
    ('tp_pct', '3P%', 'Three-point percentage', 1, False),
    ('stl', 'SPG', 'Steals per game', 2, True),
    ('blk', 'BPG', 'Blocks per game', 2, True),
    ('tov', 'TPG', 'Turnovers per game', 2, True),
    ('fouls', 'FPG', 'Fouls per game', 2, True),
    ('fgm', 'FGM', 'Field goals made per game', 2, True),
    ('fga', 'FGA', 'Field goals attempted per game', 2, True),
    ('tpm', '3PM', 'Threes made per game', 2, True),
    ('tpa', '3PA', 'Threes attempted per game', 2, True),
]
# Columns where the group's best gets marked; higher is better in all of them
LEADER_KEYS = ('win_pct', 'pts', 'reb', 'ast', 'fg_pct', 'tp_pct', 'stl', 'blk')

# A record against an opponent or with a teammate needs this many games to be called out
MIN_GAMES_TO_CALL_OUT = 5

CAT_NAMES = {'Points': 'points', 'Rebounds': 'rebounds', 'Assists': 'assists', 'Steals': 'steals',
             'Blocks': 'blocks', 'Turnovers': 'turnovers', 'FGM': 'field goals made', '3PM': 'threes made'}


def _pick(value, allowed):
    return value if value in allowed else None


def _leaders(lines):
    if len(lines) < 2:
        return {}
    return {key: max(getattr(line, key) for line in lines) for key in LEADER_KEYS}


def _called_out(lines):
    """The best and worst records among lines with enough games, or (None, None)."""
    enough = [line for line in lines if line.games >= MIN_GAMES_TO_CALL_OUT]
    if len(enough) < 2:
        return None, None
    ranked = sorted(enough, key=lambda line: (line.win_pct, line.games))
    return ranked[-1], ranked[0]


def _seat(game, name):
    team, player = stats.player_in(game, name)
    return {'player': player, 'won': team.side == game.winner}


def _nights(games):
    """Games grouped by night, newest first; the undated games come last under None."""
    groups = []
    for game in games:
        night = stats.night_of(game.played) if game.played else None
        if not groups or groups[-1][0] != night:
            groups.append((night, []))
        groups[-1][1].append(game)
    return groups


def _game_date(game_id):
    game = stats.game(game_id)
    return short_day(stats.night_of(game.played)) if game.played else 'No date'


@bp.app_template_filter('day')
def day(value):
    return f"{value:%a}, {value:%b} {value.day}, {value.year}"


@bp.app_template_filter('short_day')
def short_day(value):
    return f"{value:%b} {value.day}, {value.year}"


@bp.app_template_filter('clock')
def clock(value):
    return f"{value.hour % 12 or 12}:{value:%M} {'AM' if value.hour < 12 else 'PM'}"


@bp.app_template_filter('night')
def night(value):
    return stats.night_of(value)


@bp.context_processor
def site_context():
    return {'nav_items': NAV_ITEMS, 'site': stats.landing_highlights(), 'positions': stats.POSITIONS}


@bp.route('/')
def home():
    dated = [game for game in stats.box_scores() if game.played]
    return render_template('v2/index.html', h=stats.landing_highlights(),
                           last=dated[0] if dated else None, latest=dated[:5])


@bp.route('/games')
def games():
    names = stats.names()
    name = _pick(request.args.get('Name'), names)
    pos = with_ = vs = None
    exact = False
    if name:
        pos = _pick(request.args.get('Position'), stats.POSITIONS)
        with_ = [mate for mate in request.args.getlist('With') if mate in names and mate != name]
        vs = _pick(request.args.get('Vs'), names)
        exact = request.args.get('Lineup') == 'exact' and bool(with_)

    found = stats.find_games(name, pos, with_ or (), vs, exact)
    seats = {game.id: _seat(game, name) for game in found} if name else {}
    wins = sum(seat['won'] for seat in seats.values())

    return render_template(
        'v2/games.html', names=names, name=name, pos=pos, with_=with_ or [], vs=vs, exact=exact,
        player_positions=stats.positions_of(name) if name else [],
        lineup=len(with_ or []) > 1 or exact, groups=_nights(found), count=len(found),
        wins=wins, seats=seats,
        clear_lineup_url=url_for('v2.games', Name=name, Position=pos, Vs=vs))


@bp.route('/games/<game_id>')
def game(game_id):
    found = stats.game(game_id)
    if found is None:
        abort(404)
    everything = stats.box_scores()
    index = everything.index(found)
    unlisted = {team.side: team.points - sum(player.points for player in team.players) for team in found.teams}
    return render_template('v2/game.html', game=found, unlisted=unlisted,
                           newer=everything[index - 1] if index > 0 else None,
                           older=everything[index + 1] if index + 1 < len(everything) else None)


@bp.route('/CareerAvg')
def averages():
    pos = _pick(request.args.get('Position'), stats.POSITIONS)
    lines = sorted(stats.average_lines(pos), key=lambda line: line.pts, reverse=True)
    rows = [{'line': line, 'href': url_for('v2.games', Name=line.label, Position=pos)} for line in lines]
    return render_template('v2/averages.html', pos=pos, rows=rows, columns=COLUMNS,
                           leaders=_leaders(lines), leader=lines[0] if lines else None)


@bp.route('/Matchup')
def matchups():
    names = stats.names()
    name = _pick(request.args.get('Name'), names)
    pos = _pick(request.args.get('Position'), stats.POSITIONS)
    lines = sorted(stats.matchup_lines(name, pos), key=lambda line: (-line.games, line.label)) if name else []
    rows = [{'line': line, 'href': url_for('v2.games', Name=name, Position=pos, Vs=line.label)} for line in lines]
    best, worst = _called_out(lines)
    return render_template('v2/matchups.html', names=names, name=name, pos=pos, rows=rows,
                           player_positions=stats.positions_of(name) if name else [],
                           columns=COLUMNS, best=best, worst=worst, min_games=MIN_GAMES_TO_CALL_OUT)


@bp.route('/Teammate')
def teammates():
    names = stats.names()
    name = _pick(request.args.get('Name'), names)
    view = 'lineups' if request.args.get('Type') == 'All Combinations' else 'teammates'
    rows, best, worst, once_count = [], None, None, 0
    if name and view == 'lineups':
        lines = sorted(stats.lineup_lines(name), key=lambda line: (-line.games, line.label))
        rows = [{'line': line, 'once': line.games == 1,
                 'href': url_for('v2.games', Name=name, With=line.label.split(', '), Lineup='exact')}
                for line in lines]
        once_count = sum(row['once'] for row in rows)
    elif name:
        lines = sorted(stats.teammate_lines(name), key=lambda line: (-line.games, line.label))
        rows = [{'line': line, 'href': url_for('v2.games', Name=name, With=line.label)} for line in lines]
        best, worst = _called_out(lines)
    return render_template('v2/teammates.html', names=names, name=name, view=view, rows=rows,
                           columns=COLUMNS, best=best, worst=worst, once_count=once_count,
                           min_games=MIN_GAMES_TO_CALL_OUT)


@bp.route('/CareerHigh')
def highs():
    cat = _pick(request.args.get('cat'), stats.ALLOWED_CATS) or 'Points'
    board = [(board_cat, value, [(holder, game_id, _game_date(game_id)) for holder, _, game_id in holders])
             for board_cat, value, holders in stats.record_board()]
    ranked, rank, previous = [], 0, None
    for position, (holder, value, game_id) in enumerate(stats.record_holders(cat), start=1):
        if value != previous:
            rank, previous = position, value
        ranked.append((rank, holder, value, game_id, _game_date(game_id)))
    return render_template('v2/highs.html', cat=cat, cats=stats.ALLOWED_CATS, cat_names=CAT_NAMES,
                           board=board, ranked=ranked)


@bp.route('/Upload', methods=['GET', 'POST'])
def upload():
    message = None
    if request.method == 'POST':
        # OCR isn't built yet, so the file is thrown away without being saved
        if request.files.get('screenshot'):
            message = "OCR isn't ready yet, so your upload wasn't saved."
        else:
            message = "Pick an image to upload first."
    return render_template('v2/upload.html', message=message)


@bp.app_errorhandler(413)
def upload_too_large(error):
    return render_template('v2/upload.html', message="That file is over 5 MB, so it wasn't uploaded."), 413
