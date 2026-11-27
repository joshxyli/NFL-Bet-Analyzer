import json,sys
r=json.load(open(sys.argv[1]))
print('BRIER (one row per player-line; lower is better)  n  over%  mkt  old  new | mean under chance: actual mkt old new')
for k,b in r['brier'].items():
    if b: u=b['mean_under']; print(f"  {k:52s}{b['n']:4d} {b['over_rate']:.3f} {b['mkt']:.4f} {b['old']:.4f} {b['new']:.4f} | {u['actual']:.3f} {u['mkt']:.3f} {u['old']:.3f} {u['new']:.3f}")
f=lambda s:f"{s['bets']:3d} {s['w']:3d}-{s['l']:<3d} {100*s['roi']:+6.1f}%" if s['bets'] else '  -'
for filt in ('pos','every'):
    print('\nROI,',{'pos':'positive edge only','every':'every pick'}[filt],' columns: bets W-L ROI')
    cols=['all','Over','Under']+[f'{g}|{s}' for g in ('WR1/2','WR3+','RB1','RB2+') for s in ('Over','Under')]+['fringeUnders']
    for w in (0.1,0.3,0.6,1.0):
        for m in ('old','new','new+fringe'):
            x=r['roi'][f'{m}|{w}'][filt]; print(f'  w={w:<4} {m:11s}', ' | '.join(f'{c}: '+f(x[c]) for c in cols))
