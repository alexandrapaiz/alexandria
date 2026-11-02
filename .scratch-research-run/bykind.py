import sys, json, itertools, tempfile, os, statistics
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt
ALL = sorted(tt.load_decoys('skills/_validation/decoys.json'))
def run_with(subset):
    d = json.load(open('skills/_validation/decoys.json'))
    d['decoys'] = [x for x in d['decoys'] if x['name'] in subset]
    fd, path = tempfile.mkstemp(suffix='.json', dir='.scratch-research-run')
    with os.fdopen(fd, 'w') as f: json.dump(d, f)
    try: r = tt.run('skills', path, 'lexical/2.1')
    finally: os.unlink(path)
    by = {}
    for s in r['suites']:
        for c in s['cases']:
            by.setdefault(c['kind'], [0,0])
            by[c['kind']][1] += 1
            by[c['kind']][0] += bool(c['passed'])
    return by
kinds = ['positive','negative','confusion']
print(f"{'k':>2}  " + "  ".join(f"{x:>22}" for x in kinds))
for k in range(1, 9):
    acc = {x: [] for x in kinds}
    for s in itertools.combinations(ALL, k):
        by = run_with(set(s))
        for x in kinds:
            if x in by: acc[x].append(by[x][0])
    tot = run_with(set(ALL[:k]))
    cells = []
    for x in kinds:
        n = run_with(set(ALL))[x][1]
        cells.append(f"{statistics.mean(acc[x]):5.2f} of {n:<2} ({statistics.mean(acc[x])/n:.3f})")
    print(f"{k:>2}  " + "  ".join(f"{c:>22}" for c in cells))
