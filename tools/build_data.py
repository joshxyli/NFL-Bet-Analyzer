"""Build data.json for the website copy of NFL Bet Analyzer.
Usage: python3 -I tools/build_data.py <export_dir> <out_file>
<export_dir> holds the artifact database exported as <collection>/<doc_id>.json (ArtifactData out_dir layout)."""
import json, os, sys, datetime
src, out = sys.argv[1], sys.argv[2]
now = datetime.datetime.now(datetime.timezone.utc)
def ts(s):
    try: return datetime.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
    except Exception: return None
KEEP_META = {'injuries', 'overrides', 'marks', 'grade'}          # no usage counters or run state
cols = {}
for coll in ['lines', 'pulls', 'meta', 'slips', 'log', 'results', 'rescore']:
    d = os.path.join(src, coll); docs = {}
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.endswith('.json'): continue
            j = json.load(open(os.path.join(d, f)))
            doc_id = f[:-5]
            if coll == 'meta' and doc_id not in KEEP_META: continue
            if coll in ('lines', 'pulls'):                         # only games that have not ended
                t = ts(j.get('commence'))
                if not t or (now - t).total_seconds() > 6 * 3600: continue
            if coll == 'slips':                                    # bet amounts and payouts stay private
                for k in ('stake', 'payout'): j.pop(k, None)
            docs[doc_id] = j
    cols[coll] = docs
snap = {'at': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'collections': cols}
json.dump(snap, open(out, 'w'), separators=(',', ':'))
print('wrote', out, os.path.getsize(out), 'bytes;', {k: len(v) for k, v in cols.items()})
