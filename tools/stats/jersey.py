"""Jersey numbers for the players in stats.json, from the nflverse roster file (roster_<season>.csv).
add(stats, data_dir, prev=None) sets p['j'] on each player matched by gsis id, then by name and team.
If the roster file is missing it is downloaded; if that fails, numbers from the previous stats file are kept.
Returns the number of players with a jersey number."""
import os, csv, urllib.request
import nfl
URL = 'https://github.com/nflverse/nflverse-data/releases/download/rosters/roster_{}.csv'
def add(s, data_dir, prev=None, season=2026):
    path = os.path.join(data_dir, f'roster_{season}.csv')
    if not os.path.exists(path):
        try:
            req = urllib.request.Request(URL.format(season), headers={'User-Agent': 'curl/8'})
            with urllib.request.urlopen(req, timeout=120) as r, open(path, 'wb') as f: f.write(r.read())
        except Exception: pass
    by_id, by_name = {}, {}
    if os.path.exists(path):
        rows = list(csv.DictReader(open(path)))
        last = max((int(r['week'] or 0) for r in rows), default=0)
        for r in sorted(rows, key=lambda r: int(r['week'] or 0)):   # the latest week wins
            j = (r.get('jersey_number') or '').strip()
            if not j or j == 'NA': continue
            j = str(int(float(j)))
            if r.get('gsis_id'): by_id[r['gsis_id']] = j
            by_name[(nfl.nn(r['full_name']), r['team'])] = j
    old = {}
    for p in (prev or {}).get('players', []):
        if p.get('j'): old[p.get('id') or (nfl.nn(p['n']), p['t'])] = p['j']
    n = 0
    for p in s['players']:
        j = by_id.get(p.get('id')) or by_name.get((nfl.nn(p['n']), p['t'])) or old.get(p.get('id') or (nfl.nn(p['n']), p['t']))
        if j: p['j'] = j; n += 1
        else: p.pop('j', None)
    return n
