"""v1 UI: the original pages, served at the site root."""
import random

from flask import Blueprint, render_template, request

import stats

bp = Blueprint('v1', __name__)


@bp.route('/')
def home():
    return render_template('landing.html')


@bp.route('/CareerAvg')
def CareerAvg():
    pos = request.args.get('Position')
    if pos in stats.POSITIONS:
        title, header, data = stats.career_averages(pos)
    else:
        pos = 'All Positions'
        title, header, data = stats.career_averages()

    return render_template('Average.html', title=title, header=header, data=data, pos=pos)


@bp.route('/Matchup')
def Matchup():
    names = stats.names()
    pos = request.args.get('Position')
    name = request.args.get('Name')
    if name not in names:
        title = "Select A Player And Position"
        return render_template('matchup.html', Names=names, title=title, header=[], data=[],
                               pos="All Positions", name=random.choice(names))

    if pos in stats.POSITIONS:
        title, header, data = stats.matchups(name, pos)
    else:
        pos = "All Positions"
        title, header, data = stats.matchups(name)

    return render_template('matchup.html', Names=names, title=title, header=header, data=data, pos=pos, name=name)


@bp.route('/Teammate')
def Teammate():
    names = stats.names()
    type = request.args.get('Type')
    name = request.args.get('Name')
    if type is None or name not in names:
        title = "Select A Player And A Teammate Output Type"
        return render_template('teammate.html', Names=names, title=title, header=[], data=[],
                               type="All Combinations", name=random.choice(names))

    if type == 'Individual':
        title, header, data = stats.single_teammate(name)
    else:
        type = 'All Combinations'
        title, header, data = stats.teammate_combos(name)

    return render_template('teammate.html', Names=names, title=title, header=header, data=data, type=type, name=name)


@bp.route('/CareerHigh')
def CareerHigh():
    cat = request.args.get('cat')
    if cat not in stats.ALLOWED_CATS:
        cat = "Points"
    title, header, data = stats.career_highs(cat)

    return render_template('CareerHigh.html', title=title, header=header, data=data, cat=cat)


@bp.route('/Upload', methods=['GET', 'POST'])
def Upload():
    message = None
    if request.method == 'POST':
        # OCR isn't built yet, so the file is thrown away without being saved
        if 'screenshot' in request.files:
            message = "OCR isn't ready yet, so your upload wasn't saved."
        else:
            message = "Pick an image to upload first."
    return render_template('upload.html', message=message)


@bp.app_errorhandler(413)
def upload_too_large(error):
    return render_template('upload.html', message="That file is over 5 MB, so it wasn't uploaded."), 413
