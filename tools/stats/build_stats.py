"""Rebuild stats.json for NFL Bet Analyzer from the latest nflverse files.
Usage: NFL_DATA=<dir with nflverse files> python3 -I build_stats.py <previous stats.json> <output stats.json>
Stats run through the last completed week; the board's games are the next week's. The model fit
(league effects, calibration, defensive-starter effects) is historical and carried over from the previous file."""
import sys, os, json, csv, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nfl, dst
prev_path, out_path = sys.argv[1], sys.argv[2]
D = nfl.D
G = list(csv.DictReader(open(D + 'games.csv')))
season = 2026
done = [g for g in G if int(g['season']) == season and g['game_type'] == 'REG' and g['home_score'] not in ('', 'NA')]
week = max(int(g['week']) for g in done)
if any(int(g['week']) == week and g['home_score'] in ('', 'NA') for g in G if int(g['season']) == season and g['game_type'] == 'REG'): week -= 1
last_day = max(g['gameday'] for g in done if int(g['week']) == week)
prev = json.load(open(prev_path))
d = nfl.Data(); d.fit = prev['fit']
s = d.build(season, week)
games = d.upcoming(season, week, n=1)
for g in games: g['wind'] = None
fmt = lambda iso: datetime.date.fromisoformat(iso[:10]).strftime('%a %b %-d')
note = f'Stats through {fmt(last_day)} (Week {week}) · depth charts as of {fmt(d.depth_dt)}'
out = dict(gm=prev['gm'], asOf=datetime.date.today().isoformat(), note=note, depthAsOf=d.depth_dt, games=games, **s)
out['dst'] = dst.build(season, week); out['dstAsOf'] = datetime.date.today().isoformat()
if len(out['players']) < 300 or len(out['dst']) < 28: sys.exit('REFUSED: the rebuilt file looks incomplete (%d players, %d teams)' % (len(out['players']), len(out['dst'])))
json.dump(out, open(out_path, 'w'), separators=(',', ':'))
print('BUILT', note, '|', len(out['players']), 'players |', len(games), 'games')
