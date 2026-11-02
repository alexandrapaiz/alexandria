import sys, json, itertools, statistics
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt

ALL = sorted(tt.load_decoys('skills/_validation/decoys.json'))
full = tt.load_decoys('skills/_validation/decoys.json')
import tempfile, os

def run_with(subset):
    d = json.load(open('skills/_validation/decoys.json'))
    keep = [x for x in d['decoys'] if x['name'] in subset]
    d['decoys'] = keep
    fd, path = tempfile.mkstemp(suffix='.json', dir='.scratch-research-run')
    with os.fdopen(fd, 'w') as f:
        json.dump(d, f)
    try:
        r = tt.run('skills', path, 'lexical/2.1')
    finally:
        os.unlink(path)
    out = {}
    for s in r['suites']:
        for c in s['cases']:
            out[c['id']] = c['passed']
    return out

print(f"panel has {len(ALL)} decoys: {ALL}")
rows = []
for k in range(1, len(ALL) + 1):
    subs = list(itertools.combinations(ALL, k))
    rates = []
    for s in subs:
        res = run_with(set(s))
        rates.append(sum(res.values()))
    rows.append((k, len(subs), min(rates), statistics.mean(rates), max(rates)))
    print(f"k={k}  subsets={len(subs):3}  passes of 67: min={min(rates)} mean={statistics.mean(rates):.2f} max={max(rates)}")
