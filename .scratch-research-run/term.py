import sys
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt
PROMPT = ("Our Postgres query got slow after the last release and I think the "
          "planner stopped using the index")
KEY = 'decoy-postgres-tuning'
skills = tt.load_skills('skills'); v2 = tt.load_decoys('skills/_validation/decoys.json')
cands = {**skills, **v2}
e = tt.ENGINES['lexical/2.1'](cands)
p = set(tt.tokens(PROMPT))
total = sum(e.idf.get(t, e.default_idf) for t in p)
print(f"candidates in idf corpus: {len(cands)}   default_idf={e.default_idf:.4f}")
print(f"prompt terms ({len(p)}), idf mass {total:.4f}:")
body, act = e.sets[KEY]
for t in sorted(p, key=lambda t: -e.idf.get(t, e.default_idf)):
    w = e.idf.get(t, e.default_idf)
    df = sum(1 for k in cands if t in e.sets[k][0])
    print(f"  {t:12} idf={w:.4f}  df={df:2}/{len(cands)}  share={w/total:.4f}"
          f"  {'MATCHED' if t in body else ''}")
print()
print(f"share of prompt idf mass carried by 'last' alone: "
      f"{e.idf.get('last', e.default_idf)/total:.4f}")
print("published candidate-set delta for lexical/2.1 was +0.1311")
