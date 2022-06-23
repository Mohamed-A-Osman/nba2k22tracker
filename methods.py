from fileinput import close
from collections import Counter
from re import T
from prettytable import PrettyTable
from prettytable.colortable import ColorTable,Themes
import numpy as np
from numpy import array, average
import psycopg2 
from app import db

nameList = db.engine.execute('Select "Name" FROM public."PlayerStats" GROUP BY "Name"').fetchall()
Names = []
for name in nameList:
    Names.append(name[0])



################################################################################################
#AVG BY POSITION
def getAvgByPos(name, pos, included):
    if included == True:
        sql_playerStats = """Select "Points", "Rebounds", "Assists", "Steals", "Blocks", "Fouls", "Turnovers", "FGM", "FGA", "3PM", "3PA"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" = '""" + pos + """'"""
        sql_gameIdStats = """Select "gameID", "Team"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" = '""" + pos + """'"""

    else:
        sql_playerStats = """Select "Points", "Rebounds", "Assists", "Steals", "Blocks", "Fouls", "Turnovers", "FGM", "FGA", "3PM", "3PA"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" != '""" + pos + """'"""
        sql_gameIdStats = """Select "gameID", "Team"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" != '""" + pos + """'"""
    
    list = db.engine.execute(sql_playerStats).fetchall()
    col_avg = average(list, axis = 0)
    gameId_Team_values = db.engine.execute(sql_gameIdStats).fetchall()
    win = 0
    loss = 0
    for game in gameId_Team_values:
        if getWin_Loss(game[0], game[1]) == True:
            win += 1
        else:
            loss += 1 
    
    return col_avg,list,win,loss
    


def getCareerAvg(name):
    sql_playerStats = """Select "Points", "Rebounds", "Assists", "Steals", "Blocks", "Fouls", "Turnovers", "FGM", "FGA", "3PM", "3PA"  FROM public."PlayerStats" where "Name" = '""" + name + """'"""
    sql_gameIdStats = """Select "gameID", "Team"  FROM public."PlayerStats" where "Name" = '""" + name + """'"""
 
    list = db.engine.execute(sql_playerStats).fetchall()
    col_avg = average(list, axis = 0)
    
    gameId_Team_values = db.engine.execute(sql_gameIdStats).fetchall()
    win = 0
    loss = 0
    for game in gameId_Team_values:
        if getWin_Loss(game[0], game[1]) == True:
            win += 1
        else:
            loss += 1 

    return [col_avg,list,win,loss]


def printCareerAvg():
    title = "CAREER AVERAGES"
    field_names = ['Name','Games Played','W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    final_lst =[]
    for name in Names:
        stats, gamesPlayed, win, loss = getCareerAvg(name)
        if len(gamesPlayed) < 10:
            continue
        final_lst.append([name,"{:.0f}".format(len(gamesPlayed)), str(win) + "-" + str(loss),"{:.2f}".format(win*100/len(gamesPlayed)), "{:.2f}".format(stats[0]), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
        "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
         "{:.2f}".format(stats[9]*100/stats[10])])
    return title, field_names, final_lst


def printAvgbyPos(pos, included):
    if included == True:
        title = "AVERAGE STATS AT " + pos
    else:
        title = "AVERAGE STATS WITHOUT " + pos
    field_names = ['Name','Games Played', 'W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    final_lst = []
    for name in Names:
        stats, gamesPlayed, win, loss = getAvgByPos(name, pos, included)
        if len(gamesPlayed) < 1:
            continue

        ## HANDLE DENOMINATOR OF 0 FOR 3PA for centers that don't shoot 3s
        if stats[10]==0:
            denom2 = 1
        else:
            denom2 = stats[10]
        final_lst.append([name,"{:.0f}".format(len(gamesPlayed)), str(win) + "-" + str(loss),"{:.2f}".format(win*100/len(gamesPlayed)), float("{:.2f}".format(stats[0])), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
        "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
         "{:.2f}".format(stats[9]*100/denom2)])
    
    return title, field_names, final_lst

def getWin_Loss(gameID, team):
    Team1,Team2 = db.engine.execute("""SELECT "Points","Team" From public."GameTotals" where "gameID" = '""" + gameID + """'""").fetchall()
    if team == 'T1':
        if Team1[0] > Team2[0]:
            return True
        else:
            return False  
    if team == 'T2':
        if Team2[0] > Team1[0]:
            return True
        else:
            return False  


def getTeammates(name):
    gameID_SQL = """ Select "gameID", "Team"  FROM public."PlayerStats" where "Name" = '""" + name + """'"""
    gameIdStats = db.engine.execute(gameID_SQL).fetchall()
    teamsList = []
    dict = {}
    for stat in gameIdStats:
        teammates_SQL = """ SELECT "Name" From public."PlayerStats" where "Name" != '""" + name + """' and "gameID" = '""" + stat[0] + """' and "Team" = '"""+ stat[1] +"""'"""
        team = db.engine.execute(teammates_SQL).fetchall()
        dict.update({stat[0]:team})

    tuple_of_tuples = tuple(tuple(x) for x in dict.values())
    count = Counter(tuple(sorted(t)) for t in tuple_of_tuples)
    return count, dict


def getPlayerStats(name, gameIDs):
    wins = 0
    loss = 0
    stats = []
    for id in gameIDs:
        statsSQL = """Select "Points", "Rebounds", "Assists", "Steals", "Blocks", "Fouls", "Turnovers", "FGM", "FGA", "3PM", "3PA"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "gameID" = '""" + id + """'"""
        teamSQL = """Select "Team"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "gameID" = '""" + id + """'"""
        stat = db.engine.execute(statsSQL).fetchall()
        stats.append(stat)
        team = db.engine.execute(teamSQL).fetchall() #prints value as a tuple so under you have to decouple
        if getWin_Loss(id, ', '.join(team[0])) == True:
            wins += 1
        else:
            loss += 1 
    col_avg = average(stats, axis = 0)
    return col_avg[0], wins, loss


def getMatchUps(name):
    gameID_SQL = """ Select "gameID", "Position"  FROM public."PlayerStats" where "Name" = '""" + name + """'"""
    gameIdStats = db.engine.execute(gameID_SQL).fetchall()
    oppList = []
    dict = {}
    for stat in gameIdStats:
        opp_SQL = """ SELECT "Name" From public."PlayerStats" where "Name" != '""" + name + """' and "gameID" = '""" + stat[0] + """' and "Position" = '"""+ stat[1] +"""'"""
        opp = db.engine.execute(opp_SQL).fetchall()
        dict.update({stat[0]:opp})

    tuple_of_tuples = tuple(tuple(x) for x in dict.values())
    count = Counter(tuple(sorted(t)) for t in tuple_of_tuples)
    return count, dict

def getMatchUpsByPos(name, pos, included):
    if included == True:
        gameID_SQL = """ Select "gameID", "Position"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" = '""" + pos + """'"""
    else:
        gameID_SQL = """ Select "gameID", "Position"  FROM public."PlayerStats" where "Name" = '""" + name + """' and "Position" != '""" + pos + """'"""
    
    gameIdStats = db.engine.execute(gameID_SQL).fetchall()
    oppList = []
    dict = {}
    for stat in gameIdStats:
        opp_SQL = """ SELECT "Name" From public."PlayerStats" where "Name" != '""" + name + """' and "gameID" = '""" + stat[0] + """' and "Position" = '"""+ stat[1] +"""'"""
        opp = db.engine.execute(opp_SQL).fetchall()
        dict.update({stat[0]:opp})

    tuple_of_tuples = tuple(tuple(x) for x in dict.values())
    count = Counter(tuple(sorted(t)) for t in tuple_of_tuples)
    return count, dict

def getCareerHigh(name, cat):
    sql_Statement = ''' SELECT "''' + cat + '''" From public."PlayerStats" where "Name" = ''' + """'""" + name + """'ORDER BY """ '''"'''+ cat + '''" DESC LIMIT 1'''
    lst = db.engine.execute(sql_Statement).fetchall()
    return name,lst[0][0]



def grabGameIDs(t,dict): #t is the tupple with teammates/opps, dict is the dictionary with gameID as key, and teammates as value
    storeGameIDs = []
    count = 0
    teammates_opp = dict.values()
    ids = list(dict.keys())
    for t_o in teammates_opp:
        if(set(t) == set(t_o)):
            storeGameIDs.append(ids[count])
        
        count += 1
    return storeGameIDs
    
    

def printTeammates(name):
    title = name + "'s Stats When He Plays With" 
    field_names = ['Teammates', 'Occurences', 'W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    final_list = []
    count, dict = getTeammates(name)
    teammates = count.keys()
    for t in teammates:
        gameIDs = grabGameIDs(t, dict) 
        stats, wins, loss = getPlayerStats(name, gameIDs)

        ## HANDLE DENOMINATOR OF 0 FOR 3PA for centers that don't shoot 3s
        if stats[10]==0:
            denom2 = 1
        else:
            denom2 = stats[10]
        team = [i[0] for i in t]
        final_list.append([', '.join(team), count[t], str(wins) + "-" + str(loss),"{:.2f}".format(wins*100/count[t]),float("{:.2f}".format(stats[0])), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
        "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
         "{:.2f}".format(stats[9]*100/denom2)])
    
    return title, field_names, final_list

def printSingleTeammate(name):
    title = name + "'s Stats When He Plays With" 
    field_names = ['Teammate', 'Occurences', 'W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    count, dict = getTeammates(name)
    teammates = count.keys()
    final_list = []
    for n in Names:
        winCount = 0
        lossCount = 0
        occCount = 0
        lst = [] #list of your stats when your on the team of n
        for t in teammates:
            gameIDs = grabGameIDs(t, dict) 
            stats, wins, loss = getPlayerStats(name, gameIDs)
            team = [i[0] for i in t]
            
            if n in team:
                occCount += count[t]
                winCount += wins
                lossCount += loss
                lst.append([stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], stats[6], stats[7], stats[8], stats[9], stats[10]])
                

        if lst != []:
            stats = average(lst, axis = 0)
            ## HANDLE DENOMINATOR OF 0 FOR 3PA for centers that don't shoot 3s
            if stats[10] == 0:
                    denom2 = 1
            else:
                    denom2 = stats[10]
            final_list.append([n, occCount, str(winCount) + "-" + str(lossCount),"{:.2f}".format(winCount*100/occCount),float("{:.2f}".format(stats[0])), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
            "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
            "{:.2f}".format(stats[9]*100/denom2)])
     
    return title, field_names, final_list


def printOpps(name):
    title = name + "'s Stats When Matched Up Against:"
    field_names = ['Opponent', 'Occurences', 'W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    count, dict = getMatchUps(name)
    opps = count.keys()
    final_list = []
    for o in opps:
        gameIDs = grabGameIDs(o, dict) 
        stats, wins, loss = getPlayerStats(name, gameIDs)
        ## HANDLE DENOMINATOR OF 0 FOR 3PA for centers that don't shoot 3s
        if stats[10]==0:
            denom2 = 1
        else:
            denom2 = stats[10]
        opp = [i[0] for i in o]
        if opp == []:
            continue
        final_list.append([', '.join(opp), count[o], str(wins) + "-" + str(loss),"{:.2f}".format(wins*100/count[o]),float("{:.2f}".format(stats[0])), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
        "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
         "{:.2f}".format(stats[9]*100/denom2)])
    return title, field_names, final_list

def printCareerHighs(cat):
    title = "CAREER HIGHS - " + cat.upper()
    field_names = ['Name', cat]
    final_list = []
    for name in Names:
        name, val = getCareerHigh(name, cat)
        final_list.append([name, val])
    return title, field_names, final_list

def printOppsByPos(name, pos, included):
    if included == True:
        title = name + "'s "+ pos+ " Stats When Matched Up Against:"
    else:
        title = name + "'s Stats minus " + pos + " When Matched Up Against:"
    field_names = ['Opponent', 'Occurences', 'W-L','W%', 'PPG', 'RPG', 'APG', 'SPG', 'BPG', 'FPG', 'TPG', 'FGM','FGA', 'FG%', '3PM','3PA','3P%']
    final_list = []
    count, dict = getMatchUpsByPos(name, pos, included)
    opps = count.keys()
    for o in opps:
        gameIDs = grabGameIDs(o, dict) 
        stats, wins, loss = getPlayerStats(name, gameIDs)
        ## HANDLE DENOMINATOR OF 0 FOR 3PA for centers that don't shoot 3s
        if stats[10]==0:
            denom2 = 1
        else:
            denom2 = stats[10]
        opp = [i[0] for i in o]
        if opp == []:
            continue
        final_list.append([', '.join(opp), count[o], str(wins) + "-" + str(loss),"{:.2f}".format(wins*100/count[o]),float("{:.2f}".format(stats[0])), "{:.2f}".format(stats[1]), "{:.2f}".format(stats[2]), "{:.2f}".format(stats[3]), "{:.2f}".format(stats[4]), "{:.2f}".format(stats[5]), 
        "{:.2f}".format(stats[6]), "{:.2f}".format(stats[7]), "{:.2f}".format(stats[8]), "{:.2f}".format(stats[7]*100/stats[8]), "{:.2f}".format(stats[9]), "{:.2f}".format(stats[10]),
         "{:.2f}".format(stats[9]*100/denom2)])
    return title, field_names, final_list

if __name__ == '__main__':
    #printCareerAvg()

    #printAvgbyPos('PG', True)

    #printTeammates('TripleA_00')

    #printOpps('luqmansheikh')
    #printOppsByPos('moh-_-1', 'C', True)
    #printCareerHighs('Points')
    #printSingleTeammate('BallaHendrix')
    #printCareerAvg()
    #printSingleTeammate('moh-_-1')
    print(Names)
