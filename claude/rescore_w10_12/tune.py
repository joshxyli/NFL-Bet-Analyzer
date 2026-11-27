import json,math,collections,itertools
R=json.load(open('tune_rows.json'))
T=(0.1,0.3,0.6,1.0); WEEKS=list(range(5,12)); DELTA=(-0.2,-0.1,0,0.1,0.2); K=(0,0.25,0.5,0.75,1,1.5)
LEV=('1','1.035','1.07'); ZS=('0','0.25','0.5','0.75','1')
dec=lambda a:1+a/100 if a>0 else 1+100/-a
lg=lambda p:math.log(p/(1-p)); sg=lambda x:1/(1+math.exp(-x)); cl=lambda p:min(0.999,max(0.001,p))
for r in R: r['d']=dec(r['pr']); r['win']=r['d']-1
G=collections.defaultdict(list)
for r in R: G[r['g']].append(r)
def knobs(g):  # shape options per group
    if g=='WR1/2': return [('lev',l) for l in LEV]
    if g=='WR3+': return [('z',z) for z in ZS]
    if g=='RB2+': return [('zz',a,b) for a in ZS for b in ZS]
    return [('none',)]
def pover(r,kn):
    if 'base' in r['p'] and len(r['p'])==1: return r['p']['base']
    if kn[0]=='lev': return r['p'][f"{kn[1]}|1"]
    if kn[0]=='z': return r['p'][f"1.07|{kn[1]}"]
    if kn[0]=='zz': return r['p'][kn[1] if r.get('rbk')=='RBrec' else kn[2]]
    return r['p'][r['default']]
def score(rows,kn,k,dl):
    # profit per (week, trust) of the backtest's positive-edge picks for these rows
    best={}
    for r in rows:
        po=cl(sg(lg(cl(pover(r,kn)))+dl)); m=po if r['side']=='Over' else 1-po; m=cl(r['fair']+k*(m-r['fair']))
        for w in T:
            p=w*m+(1-w)*r['fair']; ev=p*r['d']-1; key=(r['pk'],w); c=best.get(key)
            if c is None or ev>c[0]: best[key]=(ev,p-1/r['d'],r)
    out=collections.defaultdict(float); n=collections.defaultdict(int)
    for (pk,w),(ev,e,r) in best.items():
        if e<=0 or r['out']=='p': continue
        out[(r['wk'],w)]+= r['win'] if r['out']=='w' else -1; n[(r['wk'],w)]+=1
    return out,n
DEFAULT={'WR1/2':('lev','1.07'),'WR3+':('z','1'),'RB2+':('zz','1','1')}
TAB={}  # (g, kn, k, dl) -> per week/trust profit
for g,rows in G.items():
    for kn in knobs(g):
        for k in K:
            for dl in DELTA: TAB[(g,kn,k,dl)]=score(rows,kn,k,dl)
groups=list(G)
def tot(cfg,dl,weeks,trusts=T,cnt=False):
    s=0.0
    for g in groups:
        kn,k=cfg[g]; o,n=TAB[(g,kn,k,dl)]; src=n if cnt else o
        s+=sum(src.get((wk,w),0) for wk in weeks for w in trusts)
    return s
def fit(weeks):
    best=None
    for dl in DELTA:
        cfg={}; 
        for g in groups:
            cands=[(sum(TAB[(g,kn,k,dl)][0].get((wk,w),0) for wk in weeks for w in T),-abs(k-1),kn,k) for kn in knobs(g) for k in K]
            v=max(cands); cfg[g]=(v[2],v[3])
        t=tot(cfg,dl,weeks)
        if best is None or t>best[0]: best=(t,dl,cfg)
    return best
CUR={g:(DEFAULT.get(g,('none',)),1) for g in groups}
def per_trust(cfg,dl,weeks): return {w:(round(tot(cfg,dl,weeks,(w,)),1),int(tot(cfg,dl,weeks,(w,),True))) for w in T}
print('CURRENT model, weeks 5-11, positive-edge profit (units, bets) by trust:',per_trust(CUR,0,WEEKS))
print('CURRENT model, week 12 (4 games):',per_trust(CUR,0,[12]))
# leave-one-week-out: tune on 6 weeks, score the 7th
cvT=collections.defaultdict(float); cvC=collections.defaultdict(float); folds=[]
for hold in WEEKS:
    tr=[w for w in WEEKS if w!=hold]; t,dl,cfg=fit(tr)
    for w in T: cvT[w]+=tot(cfg,dl,[hold],(w,)); cvC[w]+=tot(CUR,0,[hold],(w,))
    folds.append((hold,round(tot(cfg,dl,[hold]),1),round(tot(CUR,0,[hold]),1),dl,{g:(cfg[g][0][1:] ,cfg[g][1]) for g in sorted(cfg)}))
print('\nLeave-one-week-out (held-out week only): tuned vs current, units by trust')
for w in T: print(f'  trust {int(w*100)}%: tuned {cvT[w]:+.1f}  current {cvC[w]:+.1f}  gain {cvT[w]-cvC[w]:+.1f}')
for f in folds: print('  held-out wk',f[0],'tuned',f[1],'current',f[2],'delta',f[3],f[4])
t,dl,cfg=fit(WEEKS)
print('\nFINAL (tuned on weeks 5-11): delta',dl,{g:(cfg[g][0][1:],cfg[g][1]) for g in sorted(cfg)})
print('  weeks 5-11 (in-sample):',per_trust(cfg,dl,WEEKS))
print('  week 12 (held out):',per_trust(cfg,dl,[12]))
json.dump(dict(delta=dl,cfg={g:[list(cfg[g][0]),cfg[g][1]] for g in cfg}),open('tune_final.json','w'))
