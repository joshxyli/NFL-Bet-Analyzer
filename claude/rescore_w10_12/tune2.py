exec(open('tune.py').read().split("CUR={g:")[0])
CUR={g:(DEFAULT.get(g,('none',)),1) for g in groups}
def fitp(weeks,trusts,Ks,dls,shape):
    best=None
    for dl in dls:
        cfg={}
        for g in groups:
            kns=knobs(g) if shape else [DEFAULT.get(g,('none',))]
            cands=[(sum(TAB[(g,kn,k,dl)][0].get((wk,w),0) for wk in weeks for w in trusts),-abs(k-1),kn,k) for kn in kns for k in Ks]
            v=max(cands); cfg[g]=(v[2],v[3])
        t=sum(sum(TAB[(g,cfg[g][0],cfg[g][1],dl)][0].get((wk,w),0) for wk in weeks for w in trusts) for g in groups)
        if best is None or t>best[0]: best=(t,dl,cfg)
    return best[1],best[2]
RULE={g:(DEFAULT.get(g,('none',)),0 if g in('WR1/2','WR3+','RB2+') else 1) for g in groups}
P={
 'fixed: model off WR+RB2+':None,
 'on/off per group (all trusts)':dict(K=(0,1),D=(0,),S=False,per=False),
 'on/off per group (per trust)':dict(K=(0,1),D=(0,),S=False,per=True),
 'on/off + under lean (per trust)':dict(K=(0,1),D=DELTA,S=False,per=True),
 'weights 0-1.5 (per trust)':dict(K=K,D=(0,),S=False,per=True),
 'weights + shape (per trust)':dict(K=K,D=(0,),S=True,per=True),
 'everything (per trust)':dict(K=K,D=DELTA,S=True,per=True),
 'everything (all trusts)':dict(K=K,D=DELTA,S=True,per=False),
}
print('Held-out-week profit summed over the 7 folds (weeks 5-11), units; current model shown first')
cur={w:sum(tot(CUR,0,[h],(w,)) for h in WEEKS) for w in T}
print(f"  {'current model':36s}",'  '.join(f'{int(w*100)}%: {cur[w]:+7.1f}' for w in T))
for name,c in P.items():
    res={}
    for w in T:
        s=0.0
        for h in WEEKS:
            tr=[x for x in WEEKS if x!=h]
            if c is None: dl,cfg=0,RULE
            else: dl,cfg=fitp(tr,(w,) if c['per'] else T,c['K'],c['D'],c['S'])
            s+=tot(cfg,dl,[h],(w,))
        res[w]=s
    print(f'  {name:36s}','  '.join(f'{int(w*100)}%: {res[w]:+7.1f} ({res[w]-cur[w]:+6.1f})' for w in T))
