import json,collections,math,random
R=json.load(open('lever_rows.json'))
for r in R: r['key']=tuple(r['key']); r['line']=tuple(r['line'])
dec=lambda a:1+a/100 if a>0 else 1+100/-a
lg=lambda p:math.log(max(1e-4,min(1-1e-4,p))/(1-max(1e-4,min(1-1e-4,p))))
sg=lambda x:1/(1+math.exp(-x))
def side_p(r,pover): return pover if r['side']=='Over' else 1-pover
def bet(rows,pf,thr=0.0,filt=lambda c:True):
    best={}
    for r in rows:
        p=pf(r); d=dec(r['pr']); ev=p*d-1; c=best.get(r['key'])
        if c is None or ev>c[1]: best[r['key']]=(r,ev,p-1/d,d)
    n=w=0;pr=0.0;picks=[]
    for r,ev,e,d in best.values():
        if e<=thr or r['out']=='p' or not filt(r): continue
        n+=1; won=r['out']=='w'; w+=won; pr+=(d-1) if won else -1; picks.append((r['game'],(d-1) if won else -1))
    return dict(n=n,w=w,profit=round(pr,1),roi=round(100*pr/n,1) if n else None,picks=picks)
def boot(picks,B=2000):
    g=collections.defaultdict(list)
    for gm,x in picks: g[gm].append(x)
    G=list(g); random.seed(1); s=[]
    for _ in range(B):
        xs=[x for k in random.choices(G,k=len(G)) for x in g[k]]; s.append(100*sum(xs)/len(xs) if xs else 0)
    s.sort(); return (round(s[int(.05*B)],1),round(s[int(.95*B)],1))
TR=[r for r in R if r['period']=='train']; TE=[r for r in R if r['period']=='test']
def show(name,pf,thr=0.0,filt=lambda c:True,ci=False):
    a=bet(TR,pf,thr,filt);b=bet(TE,pf,thr,filt)
    s=f"  {name:52s} train {a['n']:4d} {a['w']:4d}W {a['profit']:+7.1f}u {a['roi'] if a['roi'] is not None else 0:+6.1f}% | test {b['n']:4d} {b['w']:4d}W {b['profit']:+7.1f}u {b['roi'] if b['roi'] is not None else 0:+6.1f}%"
    if ci and b['n']: s+=f"  test ROI 90% {boot(b['picks'])}"
    print(s); return a,b
blend=lambda w:(lambda r:w*side_p(r,r['pover'])+(1-w)*r['fair'])
print('A. Current approach: blend at trust w, any positive edge (props in rush/rec markets; best-EV side per player-prop, $1 at book price)')
for w in (0.1,0.2,0.3,0.6,1.0): show(f'trust {int(w*100)}%',blend(w),ci=True)
print('B. Edge floors')
for w in (0.2,0.3,0.6):
    for t in (0.02,0.05,0.08): show(f'trust {int(w*100)}%, edge > {int(t*100)} pts',blend(w),t)
print('C. No model: always the under / always the over at the best price')
show('every Under (market chance only, bet regardless)',lambda r:1 if r['side']=='Under' else 0,-9,ci=True)
show('every Over',lambda r:1 if r['side']=='Over' else 0,-9,ci=True)
show('Unders where best price is plus money',lambda r:1 if r['side']=='Under' else 0,-9,filt=lambda r:r['pr']>0)
# D. stacking: fit y_over ~ a + b*logit(mkt) + c*(logit(model)-logit(mkt)) on train lines (one per player-line)
def lines(rows):
    L=collections.defaultdict(list)
    for r in rows: L[r['line']].append(r)
    out=[]
    for k,rs in L.items():
        if rs[0]['overOut']=='p': continue
        fo=sum(r['fair'] if r['side']=='Over' else 1-r['fair'] for r in rs)/len(rs)
        out.append(dict(y=1 if rs[0]['overOut']=='w' else 0,m=lg(fo),d=lg(rs[0]['pover'])-lg(fo),g=rs[0]['g'],mk=rs[0]['mk']))
    return out
def fit(X,y,l2=1.0):
    k=len(X[0]); b=[0.0]*k
    for _ in range(50):
        g=[0.0]*k; H=[[0.0]*k for _ in range(k)]
        for x,t in zip(X,y):
            p=sg(sum(bi*xi for bi,xi in zip(b,x))); 
            for i in range(k):
                g[i]+=(p-t)*x[i]
                for jj in range(k): H[i][jj]+=p*(1-p)*x[i]*x[jj]
        for i in range(k): g[i]+=l2*b[i]; H[i][i]+=l2
        # solve H s = g
        n=k; A=[H[i][:]+[g[i]] for i in range(n)]
        for i in range(n):
            piv=max(range(i,n),key=lambda r:abs(A[r][i])); A[i],A[piv]=A[piv],A[i]
            for r in range(n):
                if r!=i:
                    f=A[r][i]/A[i][i]; A[r]=[a-f*c for a,c in zip(A[r],A[i])]
        s=[A[i][n]/A[i][i] for i in range(n)]; b=[bi-si for bi,si in zip(b,s)]
    return b
TL=lines(TR)
G=['WR1/2','WR3+','RB1','RB2+','TE','QB']
b1=fit([[1,l['m'],l['d']] for l in TL],[l['y'] for l in TL])
print(f'D. Recalibrated blend fitted on weeks 5-9: logit(p_over) = {b1[0]:+.3f} + {b1[1]:.3f}*logit(market) + {b1[2]:.3f}*(logit(model)-logit(market))')
stack=lambda b:(lambda r:side_p(r,sg(b[0]+b[1]*lg(r['fair'] if r['side']=='Over' else 1-r['fair'])+b[2]*(lg(r['pover'])-lg(r['fair'] if r['side']=='Over' else 1-r['fair'])))))
show('recalibrated (one model weight + under intercept)',stack(b1),ci=True)
for t in (0.02,0.05): show(f'recalibrated, edge > {int(t*100)} pts',stack(b1),t)
# per-group weight
X=[[1,l['m']]+[l['d'] if l['g']==g else 0 for g in G] for l in TL]; bg=fit(X,[l['y'] for l in TL],l2=2.0)
print('   per-group model weight:',{g:round(bg[2+i],3) for i,g in enumerate(G)},'intercept',round(bg[0],3))
def stackg(r):
    fo=r['fair'] if r['side']=='Over' else 1-r['fair']; m=lg(fo); d=lg(r['pover'])-m
    gi=G.index(r['g']) if r['g'] in G else None
    return side_p(r,sg(bg[0]+bg[1]*m+(bg[2+gi]*d if gi is not None else 0)))
show('recalibrated, weight per group',stackg,ci=True)
show('recalibrated, weight per group, edge > 2 pts',stackg,0.02)
# E. trust per group chosen on train (grid), applied to test
W=(0,0.1,0.2,0.3,0.5,0.7,1.0); best={}
for g in G:
    sc=[(bet([r for r in TR if r['g']==g],blend(w))['profit'],w) for w in W]; best[g]=max(sc)[1]
print('E. Trust per group picked on weeks 5-9:',best)
show('trust per group',lambda r:blend(best.get(r['g'],0.2))(r),ci=True)
# drop groups that lost on train at w=.3
for g in G: show(f'   only {g}, trust 30%',blend(0.3),filt=lambda r,g=g:r['g']==g)
