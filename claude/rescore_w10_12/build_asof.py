# usage: NFL_DATA=<dir> python3 -I build_asof.py <ppbuild dir> <current stats.json> <out dir>
import sys, os, json, csv, time
sys.path.insert(0, sys.argv[1]); import nfl
cur = json.load(open(sys.argv[2])); OUT = sys.argv[3]
t = time.time(); d = nfl.Data(depth=False); print('loaded', round(time.time() - t), 's')
d.fit = cur['fit']
G = [g for g in d.games.values() if g['season'] == '2026' and g['game_type'] == 'REG']
dep = list(csv.DictReader(open(nfl.D + 'depth_charts_2026.csv')))
for W in range(4, 12):
    nxt = sorted(g['gameday'] for g in G if int(g['week']) == W + 1)[0]
    mx = max(r['dt'] for r in dep if r['dt'][:10] <= nxt)
    d.depth = {}
    for r in dep:
        if r['dt'] == mx and r['pos_abb'] in ('QB', 'RB', 'WR', 'TE', 'FB') and r['gsis_id'] not in d.depth:
            d.depth[r['gsis_id']] = (r['team'], r['pos_abb'] + r['pos_rank'])
    s = d.build(2026, W); s['gm'] = cur['gm']; s['asof'] = dict(stats_week=W, depth_dt=mx)
    json.dump(s, open(f'{OUT}/stats_w{W}.json', 'w'), separators=(',', ':'))
    print('week', W, 'depth', mx, 'players', len(s['players']))
