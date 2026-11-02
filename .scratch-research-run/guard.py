import sys, statistics
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt
skills = tt.load_skills('skills'); decoys = tt.load_decoys('skills/_validation/decoys.json')
cands = {**skills, **decoys}
rows = []
for k, c in sorted(cands.items()):
    w = tt.word_count(c['description']); n = len(set(tt.tokens(c['description'])))
    rows.append((k, w, n, n / w))
print(f"{'candidate':42} {'words':>5} {'|terms|':>7} {'terms/word':>10}")
for k, w, n, r in rows:
    print(f"{k:42} {w:5} {n:7} {r:10.3f}")
ws = [r[1] for r in rows]; ns = [r[2] for r in rows]
mw, mn = statistics.mean(ws), statistics.mean(ns)
num = sum((a-mw)*(b-mn) for a,b in zip(ws,ns))
den = (sum((a-mw)**2 for a in ws) * sum((b-mn)**2 for b in ns)) ** 0.5
print(f"\nPearson r(words, |terms|) over {len(rows)} candidates = {num/den:.4f}")
rat = [r[3] for r in rows]
print(f"terms-per-word: min {min(rat):.3f}  max {max(rat):.3f}  spread {max(rat)/min(rat):.2f}x")
lib = [r for r in rows if cands[r[0]]['library']]
dec = [r for r in rows if not cands[r[0]]['library']]
print(f"\nthe shipped guard's variable:  library mean words {statistics.mean([r[1] for r in lib]):.1f}"
      f"  decoy mean words {statistics.mean([r[1] for r in dec]):.1f}"
      f"  ratio {statistics.mean([r[1] for r in lib])/statistics.mean([r[1] for r in dec]):.3f}x  (tolerance 1.35x)")
print(f"the variable that moves scores: library mean |terms| {statistics.mean([r[2] for r in lib]):.1f}"
      f"  decoy mean |terms| {statistics.mean([r[2] for r in dec]):.1f}"
      f"  ratio {statistics.mean([r[2] for r in lib])/statistics.mean([r[2] for r in dec]):.3f}x  (ungated)")
