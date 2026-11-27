# usage: python3 -I add_nflverse_results.py REPO nflverse_week.csv WEEK OUTDIR  -> OUTDIR/data.json with nflverse box scores added for games not already in results
import csv,json,sys,collections,os,shutil
from datetime import date,datetime,timedelta
REPO,CSV,WK,OUT=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]
D=json.load(open(f'{REPO}/data.json')); res=D['collections']['results']; log=D['collections']['log']
NICK={'ARI':'Arizona Cardinals','ATL':'Atlanta Falcons','BAL':'Baltimore Ravens','BUF':'Buffalo Bills','CAR':'Carolina Panthers','CHI':'Chicago Bears','CIN':'Cincinnati Bengals','CLE':'Cleveland Browns','DAL':'Dallas Cowboys','DEN':'Denver Broncos','DET':'Detroit Lions','GB':'Green Bay Packers','HOU':'Houston Texans','IND':'Indianapolis Colts','JAX':'Jacksonville Jaguars','KC':'Kansas City Chiefs','LV':'Las Vegas Raiders','LAC':'Los Angeles Chargers','LA':'Los Angeles Rams','MIA':'Miami Dolphins','MIN':'Minnesota Vikings','NE':'New England Patriots','NO':'New Orleans Saints','NYG':'New York Giants','NYJ':'New York Jets','PHI':'Philadelphia Eagles','PIT':'Pittsburgh Steelers','SF':'San Francisco 49ers','SEA':'Seattle Seahawks','TB':'Tampa Bay Buccaneers','TEN':'Tennessee Titans','WAS':'Washington Commanders'}
REV={v:k for k,v in NICK.items()}
rows=[r for r in csv.DictReader(open(CSV)) if r['week']==WK and r['season_type']=='REG']
G=collections.defaultdict(list)
for r in rows: G[r['game_id']].append(r)
have={(r['home'],r['away']) for r in res.values() if r['date']>='2026-11-24'}
n=lambda x:int(float(x or 0))
added=[]
for gid,ps in G.items():
    _,_,away,home=gid.split('_')
    if (home,away) in have: continue
    doc=[d for d in log.values() if REV.get(d['home'])==home and REV.get(d['away'])==away and d['commence']>='2026-11-24']
    if not doc: continue
    ko=datetime.fromisoformat(doc[0]['commence'].replace('Z','+00:00'))-timedelta(hours=5)   # US local date of kickoff
    key=f'{away}-{home}-{ko:%Y%m%d}'
    p=['|'.join([r['player_display_name'],r['team'],r['position'],str(n(r['passing_yards'])),str(n(r['passing_tds'])),str(n(r['rushing_yards'])),str(n(r['receptions'])),str(n(r['receiving_yards'])),str(n(r['rushing_tds'])+n(r['receiving_tds']))]) for r in ps]
    res[key]=dict(away=away,home=home,date=f'{ko:%Y-%m-%d}',key=key,p=p,src='nflverse stats_player_week_2026 (scores not filled)',homeScore=None,awayScore=None)
    added.append((key,len(p)))
os.makedirs(OUT,exist_ok=True); json.dump(D,open(f'{OUT}/data.json','w'))
if not os.path.exists(f'{OUT}/stats.json'): shutil.copy(f'{REPO}/stats.json',f'{OUT}/stats.json')
print('added',added)
