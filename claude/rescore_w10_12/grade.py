# usage: python3 -I grade.py jobs.json ev.json OUT.json [--no-thin]
import json,collections,sys,random,re
J=json.load(open(sys.argv[1]));E=json.load(open(sys.argv[2]));OUT=sys.argv[3];NOTHIN='--no-thin' in sys.argv
norm=lambda s:' '.join(re.sub(r'[^a-z ]',' ',(s or '').lower()).split())
# 1) shape group per player-game, read off the saved chance (yards rows separate low 0/1; WR catches via the 7% level)
vote=collections.defaultdict(collections.Counter)
for j,e in zip(J,E):
    if not j['pos']: continue
    sv=j['saved'] if j['side']=='Over' else 1-j['saved']; d0,d1=abs(sv-e['new0']),abs(sv-e['new1'])
    if abs(e['new0']-e['new1'])>0.004: vote[(j['eid'],norm(j['nm']))][0 if d0<d1 else 1]+=1
def group(j):
    if j['posx'] not in ('WR','RB'): return j['posx'] or '?'
    v=vote.get((j['eid'],norm(j['nm'])))
    low=v.most_common(1)[0][0] if v else (0 if re.match(r'^(WR[12]|RB1)$',j['dr']) else 1)
    return {('WR',0):'WR1/2',('WR',1):'WR3+',('RB',0):'RB1',('RB',1):'RB2+'}[(j['posx'],low)]
rows=[]
for j,e in zip(J,E):
    if j['overOut'] is None: continue          # did not play: void
    g=group(j); low=1 if g in ('WR3+','RB2+') else 0
    if NOTHIN and e['oldThin'] and j['pos']: continue
    po={'old':e['old'],'new':e['new%d'%low] if j['pos'] else e['old'],'saved':j['saved'] if j['side']=='Over' else 1-j['saved']}
    o=j['overOut']; out=o if j['side']=='Over' else {'w':'l','l':'w','p':'p'}[o]
    fringe= low==1 and j['side']=='Under' and ((j['mk']=='player_receptions' and j['pt']<=2.5) or (j['mk']=='player_reception_yds' and j['pt']<=20.5))
    rows.append(dict(j=j,g=g,po=po,out=out,overOut=o,fringe=fringe))
dec=lambda a:1+a/100 if a>0 else 1+100/-a
MODELS=[('old','old',False),('new','new',False),('new+fringe','new',True),('saved','saved',False)]
def roi(w,mname,pk,fr,subset=None):
    best={}
    for r in rows:
        j=r['j']; pov=r['po'][pk]; m=pov if j['side']=='Over' else 1-pov
        ww=w*0.5 if (fr and r['fringe']) else w; p=ww*m+(1-ww)*j['fair']; d=dec(j['pr']); ev=p*d-1
        k=(j['eid'],norm(j['pl']),j['mk']); c=best.get(k)
        if c is None or ev>c['ev']: best[k]=dict(r=r,p=p,ev=ev,edge=p-1/d,d=d)
    return list(best.values())
def summ(cs):
    s=dict(bets=0,w=0,l=0,p=0,profit=0.0,exp=0.0)
    for c in cs:
        o=c['r']['out']
        if o=='p': s['p']+=1; continue
        s['bets']+=1; s['exp']+=c['p']
        if o=='w': s['w']+=1; s['profit']+=c['d']-1
        else: s['l']+=1; s['profit']-=1
    s['roi']=s['profit']/s['bets'] if s['bets'] else None; return s
GROUPS=['WR1/2','WR3+','RB1','RB2+','TE','QB']
res={'roi':{},'brier':{},'under_cal':{}}
for w in (0.1,0.3,0.6,1.0):
    for mname,pk,fr in MODELS:
        cs=roi(w,mname,pk,fr); key=f'{mname}|{w}'; out={}
        for filt in ('every','pos'):
            sel=[c for c in cs if filt=='every' or c['edge']>0]
            out[filt]={'all':summ(sel)}
            for side in ('Over','Under'): out[filt][side]=summ([c for c in sel if c['r']['j']['side']==side])
            for g in GROUPS:
                for side in ('all','Over','Under'):
                    out[filt][f'{g}|{side}']=summ([c for c in sel if c['r']['g']==g and (side=='all' or c['r']['j']['side']==side)])
            out[filt]['fringeUnders']=summ([c for c in sel if c['r']['fringe']])
        res['roi'][key]=out
        # clustered bootstrap by game of positive-edge unders ROI in WR3+/RB2+ and all unders
        res['roi'][key]['_picks']=[(c['r']['j']['game'],c['r']['g'],c['r']['j']['side'],c['edge']>0,c['r']['out'],round(c['d'],4),c['r']['fringe'],c['r']['j']['pl'],c['r']['j']['mk'],c['r']['j']['pt']) for c in cs]
# Brier, one row per player-line (over side), market = mean no-vig over chance across books
L=collections.defaultdict(list)
for r in rows:
    j=r['j']; L[(j['eid'],norm(j['pl']),j['mk'],j['pt'])].append(r)
lines=[]
for k,rs in L.items():
    o=rs[0]['overOut']
    if o=='p': continue
    y=1 if o=='w' else 0
    fo=[r['j']['fair'] if r['j']['side']=='Over' else 1-r['j']['fair'] for r in rs]
    lines.append(dict(g=rs[0]['g'],y=y,mkt=sum(fo)/len(fo),**{m:rs[0]['po'][m] for m in ('old','new','saved')},fringe=any(r['fringe'] for r in rs) or (rs[0]['g'] in ('WR3+','RB2+') and ((k[2]=='player_receptions' and k[3]<=2.5) or (k[2]=='player_reception_yds' and k[3]<=20.5))),mk=k[2]))
def brier(ls):
    n=len(ls)
    if not n: return None
    b=lambda f:sum((f(l)-l['y'])**2 for l in ls)/n
    return dict(n=n,over_rate=sum(l['y'] for l in ls)/n,mkt=b(lambda l:l['mkt']),old=b(lambda l:l['old']),new=b(lambda l:l['new']),
        mean_under={'actual':1-sum(l['y'] for l in ls)/n,'mkt':1-sum(l['mkt'] for l in ls)/n,'old':1-sum(l['old'] for l in ls)/n,'new':1-sum(l['new'] for l in ls)/n})
res['brier']['All WR/RB/TE/QB']=brier(lines)
for g in GROUPS: res['brier'][g]=brier([l for l in lines if l['g']==g])
res['brier']['fringe lines (WR3+/RB2+, <=2.5 rec / <=20.5 yds)']=brier([l for l in lines if l['fringe']])
for g in ('WR1/2','WR3+','RB1','RB2+'):
    for mk in ('player_receptions','player_reception_yds','player_rush_yds'):
        b=brier([l for l in lines if l['g']==g and l['mk']==mk])
        if b: res['brier'][f'{g} {mk}']=b
res['nrows']=len(rows); res['nlines']=len(lines)
json.dump(res,open(OUT,'w'),indent=1); print('rows',len(rows),'lines',len(lines),'groups',collections.Counter(r['g'] for r in rows))
