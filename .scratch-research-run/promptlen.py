import sys, json, copy
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt

FILLER = (" I was wondering whether somebody could possibly glance at "
          "this sometime fairly soon, thanks awfully folks.")

skills = tt.load_skills('skills'); decoys = tt.load_decoys('skills/_validation/decoys.json')
cands = {**skills, **decoys}
e = tt.ENGINES['lexical/2.1'](cands)
ft = tt.tokens(FILLER)
print(f"filler tokens ({len(ft)}): {ft}")
unmatched = [t for t in set(ft) if not any(t in e.sets[k][0] for k in cands)]
print(f"of those, matched by NO candidate: {len(set(ft))} distinct, {len(unmatched)} unmatchable -> max idf")
print()

# re-run the whole suite with every prompt padded, by monkeypatching run()'s cases
import re
orig_tokens = tt.tokens

def run_padded(reps):
    # patch LexicalEngine.score's prompt by wrapping route
    Base = tt.ENGINES['lexical/2.1']
    class Padded(Base):
        name = 'lexical/2.1'
        def route(self, prompt):
            return super().route(prompt + FILLER * reps)
    tt.ENGINES['lexical/2.1-padded'] = Padded
    r = tt.run('skills', 'skills/_validation/decoys.json', 'lexical/2.1-padded')
    out = {}
    for s in r['suites']:
        for c in s['cases']:
            out[c['id']] = c['passed']
    return r, out

r0, base = run_padded(0)
print(f"reps=0 (control)   {sum(base.values())}/{len(base)}  reliability {r0['reliability']}")
for reps in (1, 2, 3, 5):
    r, res = run_padded(reps)
    flips_lost = sorted(k for k in base if base[k] and not res[k])
    flips_won  = sorted(k for k in base if not base[k] and res[k])
    print(f"reps={reps}  {sum(res.values())}/{len(res)}  reliability {r['reliability']}  "
          f"lost {len(flips_lost)} {flips_lost}  gained {len(flips_won)} {flips_won}")
