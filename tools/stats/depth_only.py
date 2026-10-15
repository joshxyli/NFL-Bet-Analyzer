"""Refresh only the depth charts in stats.json (each player's depth-chart spot, and the off-the-chart flag),
leaving game logs and everything else as they are. Run by the injury update so depth charts match the injury report.
Usage: NFL_DATA=<dir with depth_charts_2026.csv> python3 -I depth_only.py <current stats.json> <output stats.json>"""
import sys, os, csv, json, datetime, re, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nfl
src, out_path = sys.argv[1], sys.argv[2]
s = json.load(open(src))
rows = list(csv.DictReader(open(nfl.D + 'depth_charts_2026.csv'))); mx = max(r['dt'] for r in rows)
by_id, by_name = {}, {}
for r in rows:
    if r['dt'] != mx or r['pos_abb'] not in ('QB', 'RB', 'WR', 'TE', 'FB'): continue
    v = (r['team'], r['pos_abb'] + r['pos_rank'])
    if r['gsis_id'] and r['gsis_id'] not in by_id: by_id[r['gsis_id']] = v
    k = (nfl.nn(r['player_name']), r['team'])
    if k not in by_name: by_name[k] = v
if len(by_id) < 500: sys.exit('REFUSED: the depth chart file looks incomplete (%d players)' % len(by_id))
changed = 0
for p in s['players']:
    d = by_id.get(p.get('id')) or by_name.get((nfl.nn(p['n']), p['t']))
    old = (p.get('dr'), p.get('off'))
    p.pop('dr', None); p.pop('off', None)
    if d and d[0] == p['t']: p['dr'] = d[1]
    elif p['cur']: p['off'] = 1
    changed += old != (p.get('dr'), p.get('off'))
s['depthAsOf'] = mx
fmt = datetime.date.fromisoformat(mx[:10]).strftime('%a %b %-d')
s['note'] = re.sub(r'depth charts as of [A-Za-z]{3} [A-Za-z]{3} \d+', 'depth charts as of ' + fmt, s['note'])
json.dump(s, open(out_path, 'w'), separators=(',', ':'))
print('DEPTH', mx, '|', changed, 'players changed spot |', s['note'])
