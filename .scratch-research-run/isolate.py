import sys
sys.path.insert(0, 'skills/_validation')
import trigger_test as tt

PROMPT = ("Our Postgres query got slow after the last release and I think the "
          "planner stopped using the index")
KEY = 'decoy-postgres-tuning'
skills = tt.load_skills('skills')
v2 = tt.load_decoys('skills/_validation/decoys.json')
v1 = tt.load_decoys('skills/_validation/decoys-v1-retired.json')
E21 = tt.ENGINES['lexical/2.1']; E3 = tt.ENGINES['lexical/3']

def sc(E, decoys, swap_desc=None):
    cands = {**skills, **{k: dict(v) for k, v in decoys.items()}}
    if swap_desc is not None:
        cands[KEY]['description'] = swap_desc
    return E(cands).score(PROMPT, KEY)

cells = {
  'panel v1, candidate v1 (published "short")': (v1, None),
  'panel v2, candidate v2 (published "long")':  (v2, None),
  'panel v2, candidate v1 desc  [candidate only]': (v2, v1[KEY]['description']),
  'panel v1, candidate v2 desc  [idf model only]': (v1, v2[KEY]['description']),
}
for name, E in (('lexical/2.1', E21), ('lexical/3', E3)):
    print(name)
    for label, (panel, swap) in cells.items():
        print(f"  {label:48} {sc(E, panel, swap):.4f}")
    a = sc(E, v1, None); b = sc(E, v2, None)
    cand_only = sc(E, v2, v1[KEY]['description'])
    print(f"  published delta {b-a:+.4f}  =  candidate-set part {b-cand_only:+.4f}"
          f"  +  idf-model part {cand_only-a:+.4f}")
    print()
