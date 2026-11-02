import sys, json
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt

PROMPT = ("Our Postgres query got slow after the last release and I think the "
          "planner stopped using the index")
KEY = 'decoy-postgres-tuning'

skills = tt.load_skills('skills')
v2 = tt.load_decoys('skills/_validation/decoys.json')
v1 = tt.load_decoys('skills/_validation/decoys-v1-retired.json')

def build(decoys):
    return {**skills, **decoys}

def score(engine_cls, decoys, key, prompt, override=None):
    cands = build(decoys)
    if override is not None:
        cands = {k: dict(v) for k, v in cands.items()}
        cands[key]['description'] = override
    e = engine_cls(cands)
    return e.score(prompt, key)

E21 = tt.ENGINES['lexical/2.1']
E3 = tt.ENGINES['lexical/3']

d1 = v1[KEY]['description']; d2 = v2[KEY]['description']
print(f"v1 words={tt.word_count(d1)}  v2 words={tt.word_count(d2)}")
print()
print("A. the published measurement, reproduced (v1 short decoy vs v2 long decoy)")
for name, E in (('lexical/2.1', E21), ('lexical/3', E3)):
    s1 = score(E, v1, KEY, PROMPT)
    s2 = score(E, v2, KEY, PROMPT)
    print(f"  {name:12} v1={s1:.4f}  v2={s2:.4f}  delta={s2-s1:+.4f}")
print()
print("B. PURE length: v2 description repeated 3x (identical term set, 3x words)")
for name, E in (('lexical/2.1', E21), ('lexical/3', E3)):
    s1 = score(E, v2, KEY, PROMPT)
    s3 = score(E, v2, KEY, PROMPT, override=(d2 + " ") * 3)
    print(f"  {name:12} 1x={s1:.4f}  3x={s3:.4f}  delta={s3-s1:+.4f}  words {tt.word_count(d2)} -> {tt.word_count((d2+' ')*3)}")
print()
print("C. what actually changed: the term set")
t1 = set(tt.tokens(d1)); t2 = set(tt.tokens(d2))
p = set(tt.tokens(PROMPT))
print(f"  |v1 terms|={len(t1)}  |v2 terms|={len(t2)}  added={len(t2-t1)}  dropped={len(t1-t2)}")
print(f"  prompt terms matched by v1: {sorted(p & t1)}")
print(f"  prompt terms matched by v2: {sorted(p & t2)}")
print(f"  prompt terms NEW in v2:     {sorted((p & t2) - t1)}")
