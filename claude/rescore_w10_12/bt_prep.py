# writes bt_docs.json: {period: [{doc, key, wk}]}, results, dr map
import json,sys
sys.argv=['x','../repo12','5','/dev/null']
src=open('collect.py').read().split('jobs=[]')[0]; exec(src)
D=json.load(open('../repo12/data.json'))['collections']
out={'A_w10_12':[],'B_w5_9':[]}
for eid,doc in D['log'].items():
    r=match(doc)
    if r and wk(r['date']) in (10,11,12): out['A_w10_12'].append(dict(doc=doc,key=r['key'],wk=wk(r['date'])))
for eid,doc in D['rescore'].items():
    r=match(doc)
    if r and wk(r['date']) in (5,6,7,8,9): out['B_w5_9'].append(dict(doc=doc,key=r['key'],wk=wk(r['date'])))
dr={}
for p in st['players']: dr[norm(p['n'])+'|'+p['t']]=p.get('dr') or ''
json.dump(dict(periods=out,results={r['key']:r for r in D['results'].values()},dr=dr),open('bt_docs.json','w'))
print({k:len(v) for k,v in out.items()})
