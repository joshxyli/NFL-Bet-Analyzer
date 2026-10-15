"""Loaders and the stats.json builder for Parlay Picker. Source: nflverse-data releases."""
import csv, gzip, json, collections, math, re, unicodedata
import numpy as np
import os
D = os.environ.get('NFL_DATA', '/tmp/nfldata').rstrip('/') + '/'
F = ['attempts', 'completions', 'passing_yards', 'passing_tds', 'passing_interceptions', 'carries', 'rushing_yards', 'receptions', 'targets', 'receiving_yards']

def num(x):
    try: return float(x or 0)
    except ValueError: return 0.0
def nn(s):
    s = unicodedata.normalize('NFD', (s or '').lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[.'’]", '', s); s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', s); s = re.sub(r'[^a-z ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

class Data:
    def __init__(self, seasons=(2025, 2026), depth=True, depth_cut=None):
        self.rows = []          # offensive player-games
        self.team = {}          # (season, week, team) -> dict
        self.snap = {}          # (season, week, team, normname) -> pct 0..100
        self.rz = collections.Counter(); self.rzteam = collections.Counter()
        self.games = {}; self.inj = {}; self.depth = {}
        for r in csv.DictReader(open(D + 'games.csv')):
            self.games[r['game_id']] = r
        for yr in seasons:
            for r in csv.DictReader(open(D + f'stats_player_week_{yr}.csv')):
                if r['position'] not in ('QB', 'RB', 'WR', 'TE', 'FB'): continue
                v = [num(r[f]) for f in F]; v.append(num(r['rushing_tds']) + num(r['receiving_tds']))
                if v[0] + v[5] + v[8] == 0: continue
                self.rows.append(dict(id=r['player_id'], name=r['player_display_name'], pos=r['position'], team=r['team'], opp=r['opponent_team'],
                                      season=int(r['season']), week=int(r['week']), gid=r['game_id'], v=v))
            for r in csv.DictReader(open(D + f'stats_team_week_{yr}.csv')):
                self.team[(int(r['season']), int(r['week']), r['team'])] = dict(att=num(r['attempts']), car=num(r['carries']), pyd=num(r['passing_yards']), ryd=num(r['rushing_yards']),
                    td=num(r['passing_tds']) + num(r['rushing_tds']), gid=r['game_id'], opp=r['opponent_team'])
            for r in csv.DictReader(open(D + f'snap_counts_{yr}.csv')):
                self.snap[(int(r['season']), int(r['week']), r['team'], nn(r['player']))] = round(num(r['offense_pct']) * 100)
            with gzip.open(D + f'play_by_play_{yr}.csv.gz', 'rt') as fh:
                for r in csv.DictReader(fh):
                    if r['play_type'] not in ('run', 'pass') or r['two_point_attempt'] == '1' or not r['yardline_100']: continue
                    if float(r['yardline_100']) > 20: continue
                    pid = r['rusher_player_id'] if r['play_type'] == 'run' else r['receiver_player_id']
                    if not pid or pid == 'NA': continue
                    self.rz[(r['game_id'], pid)] += 1; self.rzteam[(r['game_id'], r['posteam'])] += 1
            for r in csv.DictReader(open(D + f'injuries_{yr}.csv')):
                st = r['report_status'] or ('DNP' if r['practice_status'].startswith('Did Not') else '')
                if st: self.inj[(int(r['season']), int(r['week']), r['gsis_id'])] = (st, r['report_primary_injury'] or r['practice_primary_injury'])
        # weeks are numbered straight through the playoffs in every file
        self.rows.sort(key=lambda r: (r['season'], r['week']))
        self._mark_starts()
        if depth:
            d = list(csv.DictReader(open(D + 'depth_charts_2026.csv'))); mx = max(r['dt'] for r in d if not depth_cut or r['dt'][:10] <= depth_cut)
            self.depth_dt = mx
            for r in d:
                if r['dt'] == mx and r['pos_abb'] in ('QB', 'RB', 'WR', 'TE', 'FB') and r['gsis_id'] not in self.depth:
                    self.depth[r['gsis_id']] = (r['team'], r['pos_abb'] + r['pos_rank'])
        self.fit = None

    # Starting slots per position. A player "started" a game when he was in his team's top slots at his position that
    # week: most carries for backs, most pass attempts for quarterbacks, offensive snap share for receivers and tight ends
    # (targets break ties and stand in when snaps are missing).
    SLOTS = {'QB': 1, 'RB': 1, 'WR': 3, 'TE': 1}
    FLOOR = {'QB': 70, 'RB': 35, 'WR': 50, 'TE': 45}   # minimum offensive snap share for a game to count as a start
    def _mark_starts(self):
        grp = collections.defaultdict(list)
        for r in self.rows:
            if r['pos'] in self.SLOTS: grp[(r['season'], r['week'], r['team'], r['pos'])].append(r)
        self.started = set()
        for (s, w, t, pos), rs in grp.items():
            sn = {r['id']: self.snap.get((s, w, t, nn(r['name'])), -1) for r in rs}
            allsn = all(x >= 0 for x in sn.values())
            def key(r):
                v = r['v']
                if pos == 'RB': return (v[5], sn[r['id']], v[8])     # the lead back is the one with the most carries
                if pos == 'QB': return (v[0], sn[r['id']])           # the passer
                return (sn[r['id']], v[8]) if allsn else (v[8],)
            rs = sorted(rs, key=key, reverse=True)
            for r in rs[:self.SLOTS[pos]]:
                # a full game, not relief duty: enough of the snaps (or, for a passer with no snap count, enough throws)
                x = sn[r['id']]
                if x >= 0 and x < self.FLOOR[pos]: continue
                if x < 0 and pos == 'QB' and r['v'][0] < 15: continue
                self.started.add((s, w, t, r['id']))

    def team_pts(self, gid, team):
        g = self.games.get(gid)
        if not g or g['home_score'] in ('', 'NA'): return None
        return num(g['home_score'] if g['home_team'] == team else g['away_score'])

    def build(self, season, week, next_week_inj=True):
        """Everything the page needs, using only games up to and including (season, week)."""
        upto = lambda s, w: (s, w) <= (season, week)
        rows = [r for r in self.rows if upto(r['season'], r['week'])]
        tg = collections.defaultdict(list)     # team -> its games, newest first
        for (s, w, t), v in self.team.items():
            if upto(s, w): tg[t].append((s, w, v))
        for t in tg: tg[t].sort(key=lambda x: (x[0], x[1]), reverse=True)
        # defence factors, this season only
        IDX = {'pyd': 2, 'ptd': 3, 'ryd': 6, 'rec': 7, 'recyd': 9, 'td': 10}
        allowed = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * 11))
        for r in rows:
            if r['season'] != season: continue
            a = allowed[r['opp']][r['week']]
            for i, x in enumerate(r['v']): a[i] += x
        per = {t: {k: sum(g[i] for g in w.values()) / len(w) for k, i in IDX.items()} for t, w in allowed.items()}
        lg = {k: sum(p[k] for p in per.values()) / max(1, len(per)) for k in IDX}
        defs = {t: {k: round(1 + (len(allowed[t]) / (len(allowed[t]) + 6)) * (per[t][k] / lg[k] - 1), 3) for k in IDX} for t in per}
        # team offence baselines, recency weighted over the last 8 games
        teams = {}
        for t, gl in tg.items():
            sw = 0; acc = collections.Counter()
            for i, (s, w, v) in enumerate(gl[:8]):
                wt = 0.88 ** i * (1 if s == season else 0.5)
                pts = self.team_pts(v['gid'], t)
                gg = self.games.get(v['gid']); sp = num(gg['spread_line']) if gg and gg['spread_line'] not in ('', 'NA') else 0.0
                acc['fav'] += wt * (sp if gg and gg['home_team'] == t else -sp)
                sw += wt; acc['att'] += wt * v['att']; acc['car'] += wt * v['car']; acc['td'] += wt * v['td']
                acc['rz'] += wt * self.rzteam[(v['gid'], t)]; acc['pts'] += wt * (pts if pts is not None else 21)
            teams[t] = {k: round(acc[k] / sw, 2) for k in ('att', 'car', 'td', 'rz', 'pts', 'fav')}
        by = collections.defaultdict(list)
        for r in rows: by[r['id']].append(r)
        players = []
        for pid, g in by.items():
            g = sorted(g, key=lambda r: (r['season'], r['week']), reverse=True)
            if not (g[0]['season'] == season or g[0]['week'] >= 12): continue
            older = g[10:]; g = g[:10]
            if sum(r['v'][0] + r['v'][5] + r['v'][8] for r in g) < 3: continue
            team = g[0]['team']
            def row(r):
                tv = self.team.get((r['season'], r['week'], r['team']), {})
                return [r['season'] % 100, r['week'], r['opp']] + [int(x) for x in r['v']] + [
                    self.snap.get((r['season'], r['week'], r['team'], nn(r['name'])), -1), int(tv.get('att', 0)), int(tv.get('car', 0)),
                    self.rz[(r['gid'], pid)], self.rzteam[(r['gid'], r['team'])],
                    1 if (r['season'], r['week'], r['team'], pid) in self.started else 0]   # [19] started this game
            out = [row(r) for r in g]
            # a part-time player's older starts, so he can be projected from them when he fills in for a starter
            sg = [row(r) for r in older if (r['season'], r['week'], r['team'], pid) in self.started][:max(0, 6 - sum(x[19] for x in out))]
            # share of the team's last three games, counting missed games as zero: what goes missing if he sits
            last3 = tg[team][:3]; u = [0.0, 0.0, 0.0, 0.0]
            mine = {(r['season'], r['week']): r for r in g if r['team'] == team}
            for (s, w, v) in last3:
                r = mine.get((s, w))
                if not r: continue
                u[0] += r['v'][8] / max(1, v['att']) / len(last3); u[1] += r['v'][5] / max(1, v['car']) / len(last3)
                u[2] += self.rz[(r['gid'], pid)] / max(1, self.rzteam[(r['gid'], team)]) / len(last3)
                u[3] += (1 if r['v'][0] >= 10 else 0) / len(last3)   # share of recent games he was the passer
            p = dict(n=g[0]['name'], p=g[0]['pos'], t=team, cur=1 if g[0]['season'] == season else 0, g=out, u=[round(x, 3) for x in u], id=pid)
            if sg: p['sg'] = sg
            nxt = self._next_week(team, *tg[team][0][:2]) if tg[team] else None
            st = self.inj.get((nxt[0], nxt[1], pid)) if nxt and next_week_inj else None
            if st: p['st'] = st[0]; p['inj'] = st[1]
            if self.depth:
                d = self.depth.get(pid)
                if d and d[0] == team: p['dr'] = d[1]
                elif p['cur']: p['off'] = 1      # played this season but not on the team's current depth chart
            players.append(p)
        players.sort(key=lambda p: p['n'])
        return dict(lg={k: round(v, 2) for k, v in lg.items()}, defs=defs, teams=teams, players=players, fit=self.fit)

    def _next_week(self, team, season, week):
        c = [(int(g['season']), int(g['week'])) for g in self.games.values() if team in (g['home_team'], g['away_team']) and (int(g['season']), int(g['week'])) > (season, week)]
        return min(c) if c else None

    def upcoming(self, season, week, n=2):
        out = []
        for g in self.games.values():
            s, w = int(g['season']), int(g['week'])
            if s == season and week < w <= week + n and g['home_score'] in ('', 'NA'):
                roof = g['roof'] or 'retractable'
                out.append(dict(id=g['game_id'], home=g['home_team'], away=g['away_team'], date=g['gameday'], time=g['gametime'], wk=w,
                    spread=num(g['spread_line']) if g['spread_line'] not in ('', 'NA') else None, total=num(g['total_line']) if g['total_line'] not in ('', 'NA') else None,
                    indoor=roof in ('dome', 'closed', 'retractable'), roof=roof, homeRest=int(num(g['home_rest'])), awayRest=int(num(g['away_rest'])), neutral=g['location'] == 'Neutral', stadium=g['stadium']))
        return sorted(out, key=lambda g: (g['date'], g['time']))

    def _backup(self, gid, team, starts):
        """1 when the game was started by someone other than the team's main quarterback that season."""
        g = self.games[gid]; st = starts[(int(g['season']), team)]
        if not st: return 0.0
        main = st.most_common(1)[0][0]
        return 0.0 if (g['home_qb_id'] if g['home_team'] == team else g['away_qb_id']) == main else 1.0

    def fit_effects(self):
        """How team volume and efficiency move with the spread, implied points, wind, venue and rest (2021-2025)."""
        tw = {}
        for yr in (2021, 2022, 2023, 2024, 2025):
            for r in csv.DictReader(open(D + f'stats_team_week_{yr}.csv')):
                if r['season_type'] != 'REG': continue
                tw[(r['game_id'], r['team'])] = dict(s=yr, att=num(r['attempts']), car=num(r['carries']), pyd=num(r['passing_yards']), ryd=num(r['rushing_yards']), td=num(r['passing_tds']) + num(r['rushing_tds']), cmp=num(r['completions']))
        starts = collections.defaultdict(collections.Counter)   # (season, team) -> starts by quarterback
        for g in self.games.values():
            if g['game_type'] != 'REG' or g['home_score'] in ('', 'NA'): continue
            starts[(int(g['season']), g['home_team'])][g['home_qb_id']] += 1; starts[(int(g['season']), g['away_team'])][g['away_qb_id']] += 1
        base = collections.defaultdict(lambda: collections.Counter())
        for (gid, t), v in tw.items():
            b = base[(v['s'], t)]; pts = self.team_pts(gid, t)
            for k in ('att', 'car', 'pyd', 'ryd', 'td', 'cmp'): b[k] += v[k]
            b['bk'] += self._backup(gid, t, starts)
            b['pts'] += pts or 0; b['n'] += 1
            gg = self.games[gid]
            if gg['spread_line'] not in ('', 'NA'): b['fav'] += num(gg['spread_line']) * (1 if gg['home_team'] == t else -1)
        X = []; Y = collections.defaultdict(list)
        for (gid, t), v in tw.items():
            g = self.games[gid]; b = base[(v['s'], t)]
            if g['spread_line'] in ('', 'NA') or g['total_line'] in ('', 'NA') or b['n'] < 10 or v['att'] < 5 or v['car'] < 5: continue
            home = g['home_team'] == t; sp = num(g['spread_line']); fav = sp if home else -sp
            imp = num(g['total_line']) / 2 + fav / 2
            out = g['roof'] in ('outdoors', 'open')
            wind = max(0.0, num(g['wind']) - 10) if out and g['wind'] not in ('', 'NA') else 0.0
            cold = 1.0 if out and g['temp'] not in ('', 'NA') and num(g['temp']) < 35 else 0.0
            rest = num(g['home_rest'] if home else g['away_rest'])
            X.append([fav - b['fav'] / b['n'], imp - b['pts'] / b['n'], wind, cold, (1.0 if home else 0.0) - 0.5 if g['location'] != 'Neutral' else 0.0, 1.0 if rest <= 5 else 0.0, 1.0 if rest >= 11 else 0.0, self._backup(gid, t, starts) - b['bk'] / b['n']])
            Y['att'].append(v['att'] / (b['att'] / b['n']) - 1); Y['car'].append(v['car'] / (b['car'] / b['n']) - 1)
            Y['ypa'].append((v['pyd'] / v['att']) / (b['pyd'] / b['att']) - 1); Y['ypc'].append((v['ryd'] / v['car']) / (b['ryd'] / b['car']) - 1)
            Y['td'].append(v['td'] / (b['td'] / b['n']) - 1); Y['cmp'].append(v['cmp'] / (b['cmp'] / b['n']) - 1)
        X = np.array(X); names = ['fav', 'imp', 'wind', 'cold', 'home', 'short', 'long', 'bk']
        fit = {}; report = {}
        for k, y in Y.items():
            y = np.array(y); A = np.c_[X, np.ones(len(X))]
            beta, *_ = np.linalg.lstsq(A, y, rcond=None)
            res = y - A @ beta; se = np.sqrt(np.diag(np.linalg.inv(A.T @ A)) * res.var(ddof=A.shape[1]))
            fit[k] = {n: (round(float(b), 5) if abs(b / s) >= 2 else 0) for n, b, s in zip(names, beta, se)}
            report[k] = {n: (round(float(b), 4), round(float(b / s), 1)) for n, b, s in zip(names, beta, se)}
        # touchdowns from red-zone chances and yards (non-QB), and league priors for efficiency
        A = []; y = []; pri = collections.defaultdict(lambda: [0, 0, 0])
        qa = [0, 0, 0]; rb = [0, 0]
        for r in self.rows:
            if r['season'] != 2025 or r['week'] > 18: continue
            v = r['v']
            if r['pos'] == 'QB': qa[0] += v[0]; qa[1] += v[2]; qa[2] += v[3]; continue
            A.append([self.rz[(r['gid'], r['id'])], v[6] + v[9]]); y.append(v[10])
            pri[r['pos']][0] += v[8]; pri[r['pos']][1] += v[7]; pri[r['pos']][2] += v[9]
            if r['pos'] == 'RB': rb[0] += v[5]; rb[1] += v[6]
        tdb, *_ = np.linalg.lstsq(np.array(A, float), np.array(y, float), rcond=None)
        fit['td_rz'] = round(float(tdb[0]), 4); fit['td_yd'] = round(float(tdb[1]), 5)
        fit['cr'] = {p: round(v[1] / v[0], 3) for p, v in pri.items()}; fit['ypr'] = {p: round(v[2] / v[1], 2) for p, v in pri.items()}
        fit['lg_ypa'] = round(qa[1] / qa[0], 2); fit['lg_ptd'] = round(qa[2] / qa[0], 4); fit['lg_ypc'] = round(rb[1] / rb[0], 2)
        fit['n'] = int(len(X)); self.fit = fit
        return report
