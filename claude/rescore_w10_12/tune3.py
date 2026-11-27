exec(open('tune.py').read().split("CUR={g:")[0])
CUR={g:(DEFAULT.get(g,('none',)),1) for g in groups}
RULE={g:(DEFAULT.get(g,('none',)),0 if g in('WR1/2','WR3+','RB2+') else 1) for g in groups}
def mod(**kw):
    c=dict(RULE)
    for g,k in kw.items(): c[g.replace('_','/').replace('WR3p','WR3+')]=(DEFAULT.get(g,('none',)),k)
    return c
V={'rule':(RULE,0),'rule + QB off':(mod(QB=0),0),'rule + TE off':(mod(TE=0),0),'rule + RB1 half':(mod(RB1=0.5),0),'rule + TE half':(mod(TE=0.5),0),
   'rule + QB half':(mod(QB=0.5),0),'rule + lean under 0.1':(RULE,-0.1),'rule + lean over 0.1':(RULE,0.1),'rule + WR1/2 quarter':({**RULE,'WR1/2':(('lev','1.07'),0.25)},0),
   'rule + WR3+ quarter':({**RULE,'WR3+':(('z','1'),0.25)},0),'rule + RB2+ quarter':({**RULE,'RB2+':(('zz','1','1'),0.25)},0),'current':(CUR,0)}
print(f"{'variant':26s}"+''.join(f'{"trust "+str(int(w*100))+"%":>22s}' for w in T)+'   | per-week profit at 30% (wk5..11) | week 12 at 30/60/100')
for n,(cfg,dl) in V.items():
    cells=''.join(f'{tot(cfg,dl,WEEKS,(w,)):+9.1f} ({int(tot(cfg,dl,WEEKS,(w,),True)):4d} bets)' for w in T)
    pw=' '.join(f'{tot(cfg,dl,[wk],(0.3,)):+5.1f}' for wk in WEEKS); w12=' '.join(f'{tot(cfg,dl,[12],(w,)):+.1f}' for w in (0.3,0.6,1.0))
    print(f'{n:26s}{cells}   | {pw} | {w12}')
# bootstrap by game: rule vs current, weeks 5-11, per trust
import random
def per_game(cfg,dl,w):
    d=collections.defaultdict(float)
    for g in groups:
        kn,k=cfg[g]; rows=G[g]
        best={}
        for r in rows:
            if r['wk']>11: continue
            po=cl(sg(lg(cl(pover(r,kn)))+dl)); m=po if r['side']=='Over' else 1-po; m=cl(r['fair']+k*(m-r['fair'])); p=w*m+(1-w)*r['fair']; ev=p*r['d']-1; c=best.get(r['pk'])
            if c is None or ev>c[0]: best[r['pk']]=(ev,p-1/r['d'],r)
        for ev,e,r in best.values():
            if e>0 and r['out']!='p': d[r['game']]+= r['win'] if r['out']=='w' else -1
    return d
games=sorted({r['game'] for r in R if r['wk']<=11}); random.seed(5)
for w in T:
    a=per_game(CUR,0,w); b=per_game(RULE,0,w); s=[]
    for _ in range(4000):
        ks=random.choices(games,k=len(games)); s.append(sum(b.get(k,0)-a.get(k,0) for k in ks))
    s.sort(); rb=per_game(RULE,0,w); s2=[]
    for _ in range(4000):
        ks=random.choices(games,k=len(games)); s2.append(sum(rb.get(k,0) for k in ks))
    s2.sort()
    print(f'trust {int(w*100)}%: rule minus current {sum(b.values())-sum(a.values()):+.1f} [90%: {s[200]:+.1f}, {s[3800]:+.1f}] P(better)={sum(x>0 for x in s)/4000:.2f} ; rule profit itself 90% [{s2[200]:+.1f}, {s2[3800]:+.1f}] P(profit>0)={sum(x>0 for x in s2)/4000:.2f}')
