# python3 -I compare.py REPO jobs ev var (saved|rescore) OUT.json [--no-thin]
import json,collections,sys,re,random
REPO,jf,ef,vf,src,OUT=sys.argv[1:7];NOTHIN='--no-thin' in sys.argv
J=json.load(open(jf));E=json.load(open(ef));V=json.load(open(vf))
norm=lambda s:' '.join(re.sub(r'[^a-z ]',' ',(s or '').lower()).split())
rsc=json.load(open(f'{REPO}/data.json'))['collections']['rescore']
RS={}
for eid,d in rsc.items():
    for s in d['o']:
        f=s.split('|')
        if len(f)>8 and f[6]!='': RS[(eid,f[0],f[1],f[2],f[3],f[4])]=float(f[6])
def ref(j):  # the new-model chance on record (over side)
    if src=='saved': v=j['saved']
    else:
        v=RS.get((j['eid'],j['pl'],j['mk'],j['book'],j['side'],('%g'%j['pt']) if False else None))
        if v is None:
            for k in ((j['eid'],j['pl'],j['mk'],j['book'],j['side'],x) for x in (str(j['pt']),'%g'%j['pt'],'%.1f'%j['pt'])):
                if k in RS: v=RS[k]; break
        if v is None: return None
    return v if j['side']=='Over' else 1-v
vote=collections.defaultdict(collections.Counter); nref=0
for j,e in zip(J,E):
    if not j['pos']: continue
    sv=ref(j)
    if sv is None: continue
    nref+=1
    if abs(e['new0']-e['new1'])>0.004: vote[(j['eid'],norm(j['nm']))][0 if abs(sv-e['new0'])<abs(sv-e['new1']) else 1]+=1
GN={('WR',0):'WR1/2',('WR',1):'WR3+',('RB',0):'RB1',('RB',1):'RB2+'}
rows=[]; nodr=0
for j,e,v in zip(J,E,V):
    if j['overOut'] is None or j['posx'] not in ('WR','RB'): continue
    if NOTHIN and e['oldThin'] and j['pos']: continue
    vv=vote.get((j['eid'],norm(j['nm'])))
    if vv: low=vv.most_common(1)[0][0]
    else: nodr+=1; low=0 if re.match(r'^(WR[12]|RB1)$',j['dr']) else 1
    g=GN[(j['posx'],low)]
    if j['pos']: cur,hz=v['cur%d'%low],v['halfZ%d'%low]
    else: cur=hz=e['old']   # WR rushing: unchanged
    po=dict(old=e['old'],new=cur,halfZ=hz,rbRecHalf=v.get('rbRecHalf%d'%low,cur),rbRecHalf_wr25=v.get('rbRecHalf_wr25%d'%low,cur),rbRevert=e['old'] if g=='RB2+' else cur,halfZ_rbRevert=e['old'] if g=='RB2+' else hz)
    o=j['overOut']; out=o if j['side']=='Over' else {'w':'l','l':'w','p':'p'}[o]
    fr= low==1 and ((j['mk']=='player_receptions' and j['pt']<=2.5) or (j['mk']=='player_reception_yds' and j['pt']<=20.5))
    rows.append(dict(j=j,g=g,po=po,out=out,overOut=o,fr=fr))
M=list(rows[0]['po'].keys())
# lines
L=collections.defaultdict(list)
for r in rows: j=r['j']; L[(j['game'],j['eid'],norm(j['pl']),j['mk'],j['pt'])].append(r)
lines=[]
for k,rs in L.items():
    if rs[0]['overOut']=='p': continue
    fo=[r['j']['fair'] if r['j']['side']=='Over' else 1-r['j']['fair'] for r in rs]
    lines.append(dict(game=k[0],g=rs[0]['g'],mk=k[3],fr=rs[0]['fr'],y=1 if rs[0]['overOut']=='w' else 0,mkt=sum(fo)/len(fo),**rs[0]['po']))
def cal(ls):
    n=len(ls); 
    if not n: return None
    d=dict(n=n,under_actual=1-sum(l['y'] for l in ls)/n,under_mkt=1-sum(l['mkt'] for l in ls)/n,brier_mkt=sum((l['mkt']-l['y'])**2 for l in ls)/n)
    for m in M: d['under_'+m]=1-sum(l[m] for l in ls)/n; d['brier_'+m]=sum((l[m]-l['y'])**2 for l in ls)/n
    return d
res={'nref':nref,'nodr':nodr,'cal':{},'roi':{},'boot':{}}
sets={'WR3+':lambda l:l['g']=='WR3+','RB2+':lambda l:l['g']=='RB2+','WR1/2':lambda l:l['g']=='WR1/2','RB1':lambda l:l['g']=='RB1',
      'WR3+ rec yds':lambda l:l['g']=='WR3+' and l['mk']=='player_reception_yds','RB2+ rec yds':lambda l:l['g']=='RB2+' and l['mk']=='player_reception_yds',
      'RB2+ rush yds':lambda l:l['g']=='RB2+' and l['mk']=='player_rush_yds','fringe lines':lambda l:l['fr'],'all WR/RB':lambda l:True}
for k,f in sets.items(): res['cal'][k]=cal([l for l in lines if f(l)])
# bootstrap by game: under lean minus actual, new vs old, for WR3+ and RB2+ and fringe
random.seed(7); games=sorted({l['game'] for l in lines}); byg=collections.defaultdict(list)
for l in lines: byg[l['game']].append(l)
for k in ('WR3+','RB2+','fringe lines','WR3+ rec yds','RB2+ rec yds'):
    f=sets[k]; diffs=[]
    for _ in range(2000):
        s=[l for g in random.choices(games,k=len(games)) for l in byg[g] if f(l)]
        if s: diffs.append(sum(l['old']-l['new'] for l in s)/len(s))  # = new under lean minus old under lean
    diffs.sort(); res['boot'][k]=dict(mean=sum(diffs)/len(diffs),lo=diffs[int(.025*len(diffs))],hi=diffs[int(.975*len(diffs))])
dec=lambda a:1+a/100 if a>0 else 1+100/-a
for w in (0.1,0.3,0.6,1.0):
    for m in M:
        for frule in (False,True):
            if frule and m!='new': continue
            best={}
            for r in rows:
                j=r['j']; pov=r['po'][m]; p_m=pov if j['side']=='Over' else 1-pov
                ww=w*0.5 if (frule and r['fr'] and j['side']=='Under') else w; p=ww*p_m+(1-ww)*j['fair']; d=dec(j['pr']); ev=p*d-1
                key=(j['eid'],norm(j['pl']),j['mk']); c=best.get(key)
                if c is None or ev>c[1]: best[key]=(r,ev,p-1/d,d)
            out={}
            for g in ('WR1/2','WR3+','RB1','RB2+','all'):
                for side in ('Over','Under','all'):
                    sel=[c for c in best.values() if c[2]>0 and (g=='all' or c[0]['g']==g) and (side=='all' or c[0]['j']['side']==side) and c[0]['out']!='p']
                    pr=sum((c[3]-1) if c[0]['out']=='w' else -1 for c in sel); out[f'{g}|{side}']=dict(bets=len(sel),wins=sum(c[0]['out']=='w' for c in sel),profit=round(pr,2))
            res['roi'][f"{m}{'+fringe' if frule else ''}|{w}"]=out
res['lines']=lines; json.dump(res,open(OUT,'w'),indent=1); print(src,'rows',len(rows),'lines',len(lines),'ref rows',nref,'group from depth chart (no saved match)',nodr)
