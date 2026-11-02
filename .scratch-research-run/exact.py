import sys
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt
PROMPT = ("Our Postgres query got slow after the last release and I think the "
          "planner stopped using the index")
KEY = 'decoy-postgres-tuning'
skills = tt.load_skills('skills')
v2 = tt.load_decoys('skills/_validation/decoys.json')
v1 = tt.load_decoys('skills/_validation/decoys-v1-retired.json')
# hold the idf model fixed at panel v2; vary only this candidate's description
for label, desc in (('v1 desc', v1[KEY]['description']), ('v2 desc', v2[KEY]['description'])):
    cands = {**skills, **{k: dict(v) for k, v in v2.items()}}
    cands[KEY]['description'] = desc
    cands[KEY]['activation'] = tt.activation_clause(desc)
    e = tt.ENGINES['lexical/2.1'](cands)
    body, act = e.sets[KEY]
    p = set(tt.tokens(PROMPT))
    total = sum(e.idf.get(t, e.default_idf) for t in p)
    print(f"{label}  ({tt.word_count(desc)} words, |terms|={len(body)})  score={e.score(PROMPT,KEY):.4f}")
    for t in sorted(p & body, key=lambda t: -e.idf.get(t, e.default_idf)):
        w = e.idf.get(t, e.default_idf); b = tt.USE_WHEN_BOOST if t in act else 1.0
        print(f"    {t:10} idf={w:.4f} boost={b}  contributes {w*b/total:.4f}")
    print()
