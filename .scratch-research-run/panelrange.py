import sys, json, itertools, tempfile, os
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
    return r['passed'], r['total']
rows = []
for k in range(1, 9):
    for s in itertools.combinations(ALL, k):
        p, n = run_with(set(s))
        rows.append((p, k, s))
rows.sort()
lo, hi = rows[0], rows[-1]
n = 67
import math
def ci(k, n):
    a, b = tt.clopper_pearson(k, n)
    return f"[{a:.2f}, {b:.2f}]"
print(f"255 non-empty panels, library/cases/engine all fixed")
print(f"WORST  {lo[0]}/{n} = {lo[0]/n:.3f}  CI {ci(lo[0],n)}  k={lo[1]}  {list(lo[2])}")
print(f"BEST   {hi[0]}/{n} = {hi[0]/n:.3f}  CI {ci(hi[0],n)}  k={hi[1]}  {list(hi[2])}")
print(f"SHIPPED (k=8) 61/{n} = {61/n:.3f}  CI {ci(61,n)}")
print(f"swing = {(hi[0]-lo[0])/n:.3f} reliability points on a parameter nothing calibrates")
best = [r for r in rows if r[0] >= 62]
print(f"\npanels beating the shipped 61: {len(best)}")
for p, k, s in sorted(best, reverse=True)[:8]:
    print(f"  {p}/{n}  k={k}  dropped: {sorted(set(ALL)-set(s))}")
