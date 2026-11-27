# usage: python3 -I collect.py REPO WEEKS(csv) OUTJOBS
import json,re,unicodedata,collections,sys
from datetime import date
REPO,WEEKS,OUT=sys.argv[1],set(map(int,sys.argv[2].split(','))),sys.argv[3]
c=json.load(open(f'{REPO}/data.json'))['collections']; st=json.load(open(f'{REPO}/stats.json'))
log,res=c['log'],c['results']
def norm(n):
    n=unicodedata.normalize('NFKD',n or '').encode('ascii','ignore').decode().lower(); n=re.sub(r"[.'’]",'',n); n=re.sub(r'\b(jr|sr|ii|iii|iv|v)\b','',n)
    return ' '.join(re.sub(r'[^a-z ]',' ',n).split())
NICK={'ARI':'Arizona Cardinals','ATL':'Atlanta Falcons','BAL':'Baltimore Ravens','BUF':'Buffalo Bills','CAR':'Carolina Panthers','CHI':'Chicago Bears','CIN':'Cincinnati Bengals','CLE':'Cleveland Browns','DAL':'Dallas Cowboys','DEN':'Denver Broncos','DET':'Detroit Lions','GB':'Green Bay Packers','HOU':'Houston Texans','IND':'Indianapolis Colts','JAX':'Jacksonville Jaguars','KC':'Kansas City Chiefs','LV':'Las Vegas Raiders','LAC':'Los Angeles Chargers','LA':'Los Angeles Rams','MIA':'Miami Dolphins','MIN':'Minnesota Vikings','NE':'New England Patriots','NO':'New Orleans Saints','NYG':'New York Giants','NYJ':'New York Jets','PHI':'Philadelphia Eagles','PIT':'Pittsburgh Steelers','SF':'San Francisco 49ers','SEA':'Seattle Seahawks','TB':'Tampa Bay Buccaneers','TEN':'Tennessee Titans','WAS':'Washington Commanders'}
REV={v:k for k,v in NICK.items()}
dd=lambda s:date(*map(int,s[:10].split('-')))
wk=lambda s:(dd(s)-date(2026,9,8)).days//7+1
resby=collections.defaultdict(list)
for r in res.values(): resby[(r['home'],r['away'])].append(r)
def match(doc):
    cc=[r for r in resby.get((REV.get(doc['home']),REV.get(doc['away'])),[]) if abs((dd(r['date'])-dd(doc['commence'])).days)<=1]
    return cc[0] if cc else None
pl=collections.defaultdict(list)
for p in st['players']: pl[norm(p['n'])].append(p)
IDX={'player_rush_yds':9,'player_receptions':10,'player_reception_yds':12}
CV={'player_rush_yds':0.55,'player_reception_yds':0.62}
RES={'player_rush_yds':5,'player_receptions':6,'player_reception_yds':7}
jobs=[]; miss=collections.Counter()
for eid,doc in log.items():
    r=match(doc)
    if not r: continue
    W=wk(r['date'])
    if W not in WEEKS: continue
    box={norm(s.split('|')[0]):s.split('|') for s in r['p']}
    for i,s in enumerate(doc['o']):
        f=s.split('|')
        if len(f)<9 or f[0]=='GAME' or f[1] not in IDX or f[6]=='' or f[8]=='': continue
        nm=f[10] or f[0]; b=box.get(norm(nm)) or box.get(norm(f[0]))
        cand=pl.get(norm(nm)) or pl.get(norm(f[0])) or []
        if b: cand=[p for p in cand if p['t']==b[1]] or cand
        p=cand[0] if cand else None
        pos=(b[2] if b else (p['p'] if p else None))
        if not p: miss['no stats player']+=1; continue
        # game log before this game: season 26 weeks < W, plus earlier seasons
        g=[x for x in p['g'] if x[0]<26 or (x[0]==26 and x[1]<W)]
        mk=f[1]; mean=max(float(f[8]),0.05); sd=None
        if mk in CV and g:
            cur=max(x[0] for x in g); ws=[0.88**k*(0.5 if x[0]<cur or not p.get('cur') else 1) for k,x in enumerate(g)]
            xs=[x[IDX[mk]] for x in g]; sw=sum(ws); base=sum(w*x for w,x in zip(ws,xs))/sw
            nEff=sw*sw/sum(w*w for w in ws); scale=(mean/base) if base>0 else 1
            varObs=max(0,sum(w*x*x for w,x in zip(ws,xs))/sw-base*base)*scale*scale
            prior=(CV[mk]*max(mean,1))**2; sd=((nEff*varObs+4*prior)/(nEff+4))**0.5
        elif mk in CV: sd=CV[mk]*max(mean,1)
        # outcome
        out=None
        if b: x=float(b[RES[mk]]); pt=float(f[4]); out='w' if x>pt else 'l' if x<pt else 'p'   # over side result
        else: miss['no box (void)']+=1
        jobs.append(dict(eid=eid,wk=W,game=r['key'],pl=f[0],nm=nm,mk=mk,book=f[2],side=f[3],pt=float(f[4]),pr=float(f[5]),saved=float(f[6]),fair=float(f[7]),
            mean=mean,sd=sd,pos=pos if (pos=='RB' or (pos=='WR' and mk!='player_rush_yds')) else None,posx=pos,dr=p.get('dr') or '',g=[[0]*9+[x[9],x[10],0,x[12]] for x in g],overOut=out,ng=len(g)))
json.dump(jobs,open(OUT,'w')); print(len(jobs),'rows',dict(miss),collections.Counter((j['wk'],j['posx']) for j in jobs))
