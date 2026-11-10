"""Pull this week's NFL lines from Parlay API and write lines_pull.json in the shape NFL Bet Analyzer stores in its `lines` collection.
Runs in GitHub Actions (PARLAY_KEY secret). Usage: python3 tools/pull_lines.py [input.json]  (input = a saved API reply, for testing)"""
import os, sys, json, re, datetime, unicodedata, urllib.request, urllib.parse, zoneinfo

API = 'https://parlay-api.com/v1/sports/americanfootball_nfl/odds'
MARKETS = 'player_pass_yds,player_pass_tds,player_rush_yds,player_receptions,player_rec_yds,h2h,spreads,totals'
PLAYER = {'player_pass_yds', 'player_pass_tds', 'player_rush_yds', 'player_receptions', 'player_reception_yds'}
GAME = {'h2h', 'spreads', 'totals'}
BOOKS = {'fanduel', 'draftkings'}
SIDE = {'over': 'Over', 'under': 'Under', 'yes': 'Yes', 'more': 'Over', 'less': 'Under', 'higher': 'Over', 'lower': 'Under'}

def to_american(dec): return round((dec - 1) * 100) if dec >= 2 else round(-100 / (dec - 1))
def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[.'’]", '', s); s = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', s); s = re.sub(r'[^a-z ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
def fix_min(iso):
    d = datetime.datetime.fromisoformat(iso.replace('Z', '+00:00'))
    if d.minute % 5 == 1: d -= datetime.timedelta(minutes=1)
    return d.astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def week_idx(t):  # NFL weeks run Tuesday 4 AM Eastern to the next Tuesday 4 AM Eastern
    et = t.astimezone(zoneinfo.ZoneInfo('America/New_York'))
    naive = datetime.datetime(et.year, et.month, et.day, et.hour, et.minute)
    return int((naive - datetime.timedelta(hours=4) - datetime.datetime(2024, 1, 2)).total_seconds() // (7 * 86400))

def game_offers(g):
    offers, hp, tp = [], [], []
    for b in g.get('bookmakers') or []:
        if b.get('key') not in BOOKS: continue
        for mk in b.get('markets') or []:
            key = mk.get('key')
            for oc in mk.get('outcomes') or []:
                if key == 'spreads' and oc.get('name') == g['home_team'] and oc.get('point') is not None: hp.append(float(oc['point']))
                if key == 'totals' and oc.get('name') == 'Over' and oc.get('point') is not None: tp.append(float(oc['point']))
                try: pr = float(oc.get('price'))
                except (TypeError, ValueError): continue
                if abs(pr) < 100: pr = to_american(pr)
                pr = int(round(pr))
                if key in GAME:
                    o = {'pl': 'GAME', 'm': key, 'b': b['key'], 's': oc['name'], 'pr': pr}
                    if oc.get('point') is not None: o['pt'] = float(oc['point'])
                    offers.append(o); continue
                pm = 'player_reception_yds' if key == 'player_rec_yds' else key
                if pm not in PLAYER or not oc.get('description'): continue
                w1 = str(oc.get('name') or '').split(' ')[0]
                o = {'pl': str(oc['description']).strip(), 'm': pm, 'b': b['key'], 's': SIDE.get(w1.lower(), oc.get('name')), 'pr': pr}
                if oc.get('point') is not None: o['pt'] = float(oc['point'])
                if o['pl']: offers.append(o)
    seen = {}
    for o in offers:  # same de-duplication as the app
        if o['pl'] != 'GAME' and re.search(r'(^|\s)(defense|d/st)$', o['pl'], re.I): continue
        k = '|'.join([('GAME' if o['pl'] == 'GAME' else norm(o['pl'])), o['m'], o['b'], str(o['s']), str(o.get('pt', ''))])
        if k not in seen or len(o['pl']) > len(seen[k]['pl']): seen[k] = o
    avg = lambda a: sum(a) / len(a)
    ctx = {'fav': -avg(hp), 'total': avg(tp) if tp else None} if hp else None
    return list(seen.values()), ctx

def main():
    if len(sys.argv) > 1: raw = json.load(open(sys.argv[1]))
    else:
        url = API + '?' + urllib.parse.urlencode({'apiKey': os.environ['PARLAY_KEY'].strip(), 'bookmakers': 'fanduel,draftkings', 'markets': MARKETS, 'oddsFormat': 'american'})
        try: raw = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'curl/8'}), timeout=120))
        except urllib.error.HTTPError as e: sys.exit('Parlay API answered HTTP %d: %s' % (e.code, e.read()[:300].decode('utf8', 'replace')))
    if isinstance(raw, dict) and not raw.get('bookmakers'):
        sys.exit('API error: ' + str(raw.get('message') or raw.get('error') or raw.get('detail') or raw)[:300])
    games = raw if isinstance(raw, list) else [raw]
    now = datetime.datetime.now(datetime.timezone.utc); wk = week_idx(now); out, seen = [], set()
    for g in games:
        if not (g.get('bookmakers') and g.get('commence_time') and g.get('home_team')): continue
        t = datetime.datetime.fromisoformat(g['commence_time'].replace('Z', '+00:00'))
        k = g['home_team'] + '|' + g['away_team']
        if t <= now or week_idx(t) != wk or k in seen: continue
        seen.add(k)
        offers, ctx = game_offers(g)
        if not offers: continue
        out.append({'gid': 'p-' + str(g['id']), 'home': g['home_team'], 'away': g['away_team'], 'commence': fix_min(g['commence_time']), 'ctx': ctx, 'offers': offers})
    if not out: sys.exit('No upcoming games with prices in the reply.')
    json.dump({'at': now.strftime('%Y-%m-%dT%H:%M:%S.000Z'), 'source': 'parlay', 'games': out}, open('lines_pull.json', 'w'), separators=(',', ':'))
    print('WROTE', len(out), 'games,', sum(len(x['offers']) for x in out), 'prices')
main()
