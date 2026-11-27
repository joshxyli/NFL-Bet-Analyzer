import json,sys
src,zipd,out=sys.argv[1:4]
h=open(src).read()
def apply(h,edits,swap,tag):
    for i,e in enumerate(edits):
        o,n=(e['new_text'],e['old_text']) if swap else (e['old_text'],e['new_text'])
        c=h.count(o); print(tag,i,'count',c, repr(o[:70]))
        if c!=1: raise SystemExit('edit does not apply uniquely')
        h=h.replace(o,n)
    return h
h=apply(h,json.load(open(f'{zipd}/out/edits_rb.json')),True,'rb-undo')
h=apply(h,json.load(open(f'{zipd}/out/edits_revert.json')),False,'wr-revert')
open(out,'w').write(h)
