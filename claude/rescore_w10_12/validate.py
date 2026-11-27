import json,collections,statistics as S
def ov(j): return j['saved'] if j['side']=='Over' else 1-j['saved']
for tag in ('old','new'):
    J=json.load(open(f'jobs_{tag}.json'));E=json.load(open(f'ev_{tag}.json'))
    agg=collections.defaultdict(list)
    for j,e in zip(J,E):
        if tag=='old':
            agg[(j['posx'],j['mk'],'thin' if e['oldThin'] else 'smooth')].append(abs(ov(j)-e['old']))
        else:
            if j['pos']:
                d0,d1=abs(ov(j)-e['new0']),abs(ov(j)-e['new1']); low=0 if d0<=d1 else 1; agg[(j['posx'],j['mk'],'low'+str(low))].append(min(d0,d1))
            else: agg[(j['posx'],j['mk'],'noshape-old')].append(abs(ov(j)-e['old']))
    print('==',tag,'saved vs rebuilt: n, median |diff|, share within .01, share within .03')
    for k,v in sorted(agg.items(),key=lambda kv:str(kv[0])):
        print(' ',k,len(v),'%.4f'%S.median(v),'%.2f'%(sum(x<.01 for x in v)/len(v)),'%.2f'%(sum(x<.03 for x in v)/len(v)))
