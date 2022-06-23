from types import NoneType
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col
import methods as m
import random


app = Flask(__name__)
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mohamed01@localhost/NBA2K22'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hcazhrrpiolcch:0b2fd0a41aeef0912b7a52bd6b815eb8f640677233ac19db0facdd03639d44d4@ec2-52-72-99-110.compute-1.amazonaws.com:5432/d61t5isgsk4kcq'
db = SQLAlchemy(app)

@app.route('/')
def home():
    title, header, data = m.printCareerAvg()
    return render_template('landing.html', header = header)

@app.route('/CareerAvg')
def CareerAvg():
    pos = request.args.get('Position')
    if pos == 'All Positions' or pos == None:
        title, header, data = m.printCareerAvg()
        pos = 'All Positions'
    else:
        title, header,data = m.printAvgbyPos(pos,True)

    return render_template('Average.html', title=title, header = header,data=data, pos = pos)

@app.route('/Matchup')
def Matchup():
    pos = request.args.get('Position')
    name = request.args.get('Name')
    if(pos == None or name == None):
        pos = "All Positions"
        name = m.Names[random.randint(0, len(m.Names)-1)]
        title = "Select A Player And Position"
        return render_template('matchup.html', Names=m.Names, title=title, header = [], data=[], pos=pos, name=name)
    else:
        if(pos == "All Positions"):
            title, header, data = m.printOpps(name)
        else:
            title, header, data = m.printOppsByPos(name, pos, True)

        return render_template('matchup.html', Names=m.Names, title=title,header = header,data=data, pos = pos, name=name)

@app.route('/Teammate')
def Teammate():
    type = request.args.get('Type')
    name = request.args.get('Name') 
    if(type == None or name == None):
        type = "All Combinations"
        name = m.Names[random.randint(0, len(m.Names)-1)]
        title = "Select A Player And A Teammate Output Type"
        return render_template('teammate.html', Names=m.Names, title=title, header = [], data=[], type=type, name=name)
    else:
        if(type == 'All Combinations'):
            title, header, data = m.printTeammates(name)
            return render_template('teammate.html', Names=m.Names, title=title, header = header, data=data, type=type, name=name)
        else:
            title, header, data = m.printSingleTeammate(name)
            return render_template('teammate.html', Names=m.Names, title=title, header = header, data=data, type=type, name=name)


@app.route('/CareerHigh')
def CareerHigh():
    cat = request.args.get('cat')
    if cat == 'Points' or cat == None:
        title, header, data = m.printCareerHighs("Points")
        cat = "Points"
    else:
        title, header,data = m.printCareerHighs(cat)

    return render_template('CareerHigh.html', title=title, header = header,data=data, cat = cat)


if __name__ == '__main__':
    app.run()

    