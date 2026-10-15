"""Defensive starters per team: 60%+ of defensive snaps in two of the team's last four games.
Each entry: [name, unit ('f7' front seven, 'sec' secondary), position, missed_last_game 0/1]."""
import csv, collections
import os
D = os.environ.get('NFL_DATA', '/tmp/nfldata').rstrip('/') + '/'
F7 = {'DE': 'DL', 'DT': 'DL', 'NT': 'DL', 'DL': 'DL', 'LB': 'LB', 'OLB': 'LB', 'ILB': 'LB', 'MLB': 'LB'}
SEC = {'CB': 'CB', 'S': 'S', 'FS': 'S', 'SS': 'S', 'DB': 'DB'}
def build(season=2026, upto_week=None):
    rows = [r for r in csv.DictReader(open(D + f'snap_counts_{season}.csv')) if r['game_type'] == 'REG' and (upto_week is None or int(r['week']) <= upto_week)]
    games = collections.defaultdict(set); snaps = collections.defaultdict(dict)
    for r in rows:
        w = int(r['week']); games[r['team']].add(w)
        if r['position'] in F7 or r['position'] in SEC:
            snaps[(r['team'], r['player'])][w] = (float(r['defense_pct'] or 0), r['position'])
    out = {}
    for t, ws in games.items():
        last4 = sorted(ws)[-4:]; last = last4[-1]; lst = []
        for (tt, n), byw in snaps.items():
            if tt != t: continue
            hi = sum(1 for w in last4 if w in byw and byw[w][0] >= 0.6)
            if hi < 2: continue
            pos = byw[max(byw)][1]
            unit, p = ('f7', pos) if pos in F7 else ('sec', pos)
            miss = 0 if (last in byw and byw[last][0] > 0) else 1
            lst.append([n, unit, p, miss])
        out[t] = sorted(lst, key=lambda x: (x[1] != 'f7', x[2], x[0]))
    return out
