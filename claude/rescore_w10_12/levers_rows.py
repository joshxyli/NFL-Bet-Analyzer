# Build one table of side-rows (both periods) with the model chance the app would use now (new model), market, price, outcome, group.
import json,collections,re,sys
REPO='../repo12'
norm=lambda s:' '.join(re.sub(r'[^a-z ]',' ',(s or '').lower()).split())
rsc=json.load(open(f'{REPO}/data.json'))['collections']['rescore']
RS={}
for eid,d in rsc.items():
    for s in d['o']:
        f=s.split('|')
        if len(f)>8 and f[6]!='': RS[(eid,f[0],f[1],f[2],f[3],f[4])]=float(f[6])
GN={('WR',0):'WR1/2',('WR',1):'WR3+',('RB',0):'RB1',('RB',1):'RB2+'}
out=[]
for period,jf,ef in (('train','jobs_old.json','ev_old.json'),('test','jobs_w1012.json','ev_w1012.json')):
    J=json.load(open(jf));E=json.load(open(ef))
    def ref(j):
        if period=='test': v=j['saved']
        else:
            v=None
            for x in (str(j['pt']),'%g'%j['pt'],'%.1f'%j['pt']):
                v=RS.get((j['eid'],j['pl'],j['mk'],j['book'],j['side'],x))
                if v is not None: break
            if v is None: return None
        return v if j['side']=='Over' else 1-v
    vote=collections.defaultdict(collections.Counter)
    for j,e in zip(J,E):
        sv=ref(j)
        if j['pos'] and sv is not None and abs(e['new0']-e['new1'])>0.004: vote[(j['eid'],norm(j['nm']))][0 if abs(sv-e['new0'])<abs(sv-e['new1']) else 1]+=1
    for j,e in zip(J,E):
        if j['overOut'] is None: continue
        if j['posx'] in ('WR','RB'):
            vv=vote.get((j['eid'],norm(j['nm']))); low=vv.most_common(1)[0][0] if vv else (0 if re.match(r'^(WR[12]|RB1)$',j['dr']) else 1); g=GN[(j['posx'],low)]
        else: low=0; g=j['posx']
        sv=ref(j)
        if sv is None: sv=e['new%d'%low] if j['pos'] else (j['saved'] if j['side']=='Over' else 1-j['saved'])  # train rows without rescore match
        if period=='train' and not j['pos']: sv=j['saved'] if j['side']=='Over' else 1-j['saved']           # unchanged by Nov 10: saved is exact
        o=j['overOut']; won=o if j['side']=='Over' else {'w':'l','l':'w','p':'p'}[o]
        fr= low==1 and j['side']=='Under' and ((j['mk']=='player_receptions' and j['pt']<=2.5) or (j['mk']=='player_reception_yds' and j['pt']<=20.5))
        out.append(dict(period=period,wk=j['wk'],game=j['game'],key=(j['eid'],norm(j['pl']),j['mk']),line=(j['eid'],norm(j['pl']),j['mk'],j['pt']),g=g,mk=j['mk'],side=j['side'],pt=j['pt'],pr=j['pr'],fair=j['fair'],pover=sv,out=won,overOut=o,fringe=fr,book=j['book']))
json.dump(out,open('lever_rows.json','w')); print(collections.Counter((r['period'],r['g']) for r in out))
