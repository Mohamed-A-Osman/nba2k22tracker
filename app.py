import random

from flask import Flask, render_template, request

import stats

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('landing.html')


@app.route('/CareerAvg')
def CareerAvg():
    pos = request.args.get('Position')
    if pos in stats.POSITIONS:
        title, header, data = stats.career_averages(pos)
    else:
        pos = 'All Positions'
        title, header, data = stats.career_averages()

    return render_template('Average.html', title=title, header=header, data=data, pos=pos)


@app.route('/Matchup')
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


@app.route('/Teammate')
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


@app.route('/CareerHigh')
def CareerHigh():
    cat = request.args.get('cat')
    if cat not in stats.ALLOWED_CATS:
        cat = "Points"
    title, header, data = stats.career_highs(cat)

    return render_template('CareerHigh.html', title=title, header=header, data=data, cat=cat)


if __name__ == '__main__':
    app.run()
