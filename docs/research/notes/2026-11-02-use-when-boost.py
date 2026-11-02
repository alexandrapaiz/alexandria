#!/usr/bin/env python3
"""Receipt for the 2026-11-02 reading of alexandria/skill's sixth finding.

Every number in docs/research/notes/2026-11-02-use-when-boost.md comes from
here. No database, no model call, no network: it loads whatever
skills/_validation/trigger_test.py the tree it is pointed at holds and
measures the scoring function against it.

    python3 docs/research/notes/2026-11-02-use-when-boost.py            # this tree
    python3 docs/research/notes/2026-11-02-use-when-boost.py --tree /path/to/worktree

Point --tree at the skill seat's branch to reproduce the lexical/2.2 rows.
On a lexical/2.1 tree the stopword rows say so and run anyway, because the
decomposition is a property of the term, not of the policy that strips it.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import statistics
import sys

PROMPT = ("Our Postgres query got slow after the last release and I think "
          "the planner stopped using the index")
NEW_STOPWORDS = {"got", "last", "think"}


def load(tree):
    path = os.path.join(tree, "skills/_validation/trigger_test.py")
    if not os.path.exists(path):
        sys.exit(f"no trigger_test.py under {tree}")
    spec = importlib.util.spec_from_file_location("tt", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, spec


def fresh(spec):
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def suite(tt, tree, patch=None):
    """Run the whole suite and return (bundle, {case id: case})."""
    if patch:
        patch(tt)
    with contextlib.redirect_stdout(io.StringIO()):
        res = tt.run(os.path.join(tree, "skills"),
                     os.path.join(tree, "skills/_validation/decoys.json"))
    return res, {c["id"]: c for s in res["suites"] for c in s["cases"]}


def uniform(tt):
    """A strictly uniform boost: every candidate's whole term set is boosted,
    so `matched` scales by exactly USE_WHEN_BOOST for every candidate alike.
    This is the counterfactual the skill seat's 'a uniform boost is a no-op'
    sentence is about."""
    original = tt.LexicalEngine.__init__

    def patched(self, candidates):
        original(self, candidates)
        self.sets = {k: (body, body) for k, (body, _) in self.sets.items()}

    tt.LexicalEngine.__init__ = patched


def decoys_unboosted(tt):
    """The limiting case of panel v3: the decoys lose the boost entirely while
    the library keeps its own boosted share. Panel v3 lands somewhere between
    today's panel and this."""
    original = tt.LexicalEngine.__init__

    def patched(self, candidates):
        original(self, candidates)
        self.sets = {k: (body, act if candidates[k]["library"] else set())
                     for k, (body, act) in self.sets.items()}

    tt.LexicalEngine.__init__ = patched


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default=os.getcwd())
    args = ap.parse_args()
    tree = os.path.abspath(args.tree)
    tt, spec = load(tree)
    print(f"tree   {tree}")
    print(f"engine {tt.ENGINE_VERSION}   boost {tt.USE_WHEN_BOOST}   "
          f"floor {tt.FLOOR}   narrow margin {tt.NARROW_MARGIN}")
    base_bundle, base = suite(fresh(spec), tree)
    print(f"baseline {base_bundle['passed']}/{base_bundle['total']}")

    # -- 1. the boosted-share asymmetry itself -----------------------------
    print("\n1. the asymmetry: how much of each side's term set the boost covers")
    audit = base_bundle.get("panel_audit", {})
    lib = audit.get("library_mean_boosted_share")
    dec = audit.get("decoy_mean_boosted_share")
    if lib is None:
        skills = tt.load_skills(os.path.join(tree, "skills"))
        decoys = tt.load_decoys(os.path.join(tree, "skills/_validation/decoys.json"))

        def share(c):
            body = set(tt.tokens(c["description"]))
            act = set(tt.tokens(c["activation"])) & body
            return len(act) / len(body) if body else 0.0

        lib = statistics.mean(share(c) for c in skills.values())
        dec = statistics.mean(share(c) for c in decoys.values())
        print("   (computed here; this tree's panel_audit does not report it)")
    print(f"   library {lib:.4f}   decoy panel {dec:.4f}   "
          f"ratio {lib / dec:.3f}x")

    # -- 2. turning the boost off ------------------------------------------
    print("\n2. turning the boost off")
    off_b, off = suite(fresh(spec), tree,
                       lambda m: setattr(m, "USE_WHEN_BOOST", 1.0))
    moved = sorted(i for i in base if base[i]["passed"] != off[i]["passed"])
    print(f"   {off_b['passed']}/{off_b['total']}, "
          f"{len(moved)} cases move: {moved}")
    gained = [i for i in moved if off[i]["passed"]]
    lost = [i for i in moved if not off[i]["passed"]]
    print(f"   of those, {len(lost)} lost and {len(gained)} gained, "
          f"so the net is {off_b['passed'] - base_bundle['passed']:+d}")

    # -- 3. is a uniform boost a no-op? ------------------------------------
    print("\n3. a strictly uniform boost against no boost at all")
    uni_b, uni = suite(fresh(spec), tree, uniform)
    print(f"   uniform {uni_b['passed']}/{uni_b['total']}   "
          f"off {off_b['passed']}/{off_b['total']}")
    ratios = [uni[i]["library_score"] / off[i]["library_score"]
              for i in off if off[i]["library_score"] > 0]
    print(f"   every library score scales by {min(ratios):.3f}-{max(ratios):.3f}"
          f" (4dp rounding in the bundle), so the ranking cannot move")
    pf = [i for i in off if off[i]["passed"] != uni[i]["passed"]]
    nr = [i for i in off if off[i]["narrow"] != uni[i]["narrow"]]
    print(f"   pass/fail differences: {len(pf)} {pf}")
    print(f"   narrow-flag differences: {len(nr)} {nr}")
    for i in nr:
        print(f"      {i}: margin {off[i]['null_margin']:+.4f} -> "
              f"{uni[i]['null_margin']:+.4f}, crossing "
              f"{tt.NARROW_MARGIN}; narrow {off[i]['narrow']} -> "
              f"{uni[i]['narrow']}")

    # -- 4. can the floor ever bind? ---------------------------------------
    print("\n4. the floor: a case must score under it AND lead the panel")
    for tag, cs in (("today", base), ("boost off", off),
                    ("uniform", uni)):
        binding = [i for i, c in cs.items()
                   if c["library_score"] < tt.FLOOR and c["null_margin"] > 0]
        under = [(i, round(c["library_score"], 4), round(c["null_margin"], 4))
                 for i, c in cs.items() if c["library_score"] < tt.FLOOR]
        print(f"   {tag:10s} binding: {len(binding)} {binding}   "
              f"under the floor at all: {under}")

    # -- 5. the limiting case of panel v3 ----------------------------------
    print("\n5. the limiting case of panel v3 (decoys lose the boost entirely)")
    v3_b, v3 = suite(fresh(spec), tree, decoys_unboosted)
    print(f"   total {base_bundle['passed']}/{base_bundle['total']} -> "
          f"{v3_b['passed']}/{v3_b['total']}")
    def by_kind(cases):
        out = {}
        for c in cases.values():
            k = out.setdefault(c["kind"], [0, 0])
            k[0] += 1 if c["passed"] else 0
            k[1] += 1
        return out

    before, after = by_kind(base), by_kind(v3)
    for kind in sorted(before):
        a, b = before[kind], after[kind]
        print(f"   {kind:10s} {a[0]}/{a[1]} -> {b[0]}/{b[1]}   "
              f"{b[0] - a[0]:+d}")
    for i in sorted(i for i in base if base[i]["passed"] != v3[i]["passed"]):
        print(f"   {i:12s} {base[i]['kind']:9s} "
              f"{base[i]['passed']} -> {v3[i]['passed']}   "
              f"margin {base[i]['null_margin']:+.4f} -> "
              f"{v3[i]['null_margin']:+.4f}")

    # -- 6. the stopword decomposition -------------------------------------
    print("\n6. the published length-bias delta, decomposed")
    v1 = os.path.join(tree, "skills/_validation/decoys-v1-retired.json")
    v2 = os.path.join(tree, "skills/_validation/decoys.json")
    short = next(d["description"] for d in json.load(open(v1))["decoys"]
                 if d["name"] == "decoy-postgres-tuning")
    long_ = next(d["description"] for d in json.load(open(v2))["decoys"]
                 if d["name"] == "decoy-postgres-tuning")
    print(f"   candidate decoy-postgres-tuning at "
          f"{len(short.split())} words and {len(long_.split())} words, "
          f"prompt and library held fixed")

    def delta(extra):
        m = fresh(spec)
        m.STOPWORDS = (m.STOPWORDS - NEW_STOPWORDS) | set(extra)
        skills = m.load_skills(os.path.join(tree, "skills"))
        decoys = m.load_decoys(v2)
        out = []
        for text in (short, long_):
            cand = {**skills, **decoys}
            cand["decoy-postgres-tuning"] = {
                **cand["decoy-postgres-tuning"], "description": text,
                "activation": m.activation_clause(text)}
            out.append(m.LexicalEngine(cand).score(PROMPT,
                                                   "decoy-postgres-tuning"))
        return out[0], out[1], out[1] - out[0]

    for label, extra in (("none stripped (lexical/2.1)", ()),
                         ("'last' alone", ("last",)),
                         ("'got' alone", ("got",)),
                         ("'think' alone", ("think",)),
                         ("all three (lexical/2.2)", tuple(NEW_STOPWORDS))):
        a, b, d = delta(extra)
        print(f"   {label:28s} short {a:.4f}  long {b:.4f}  delta {d:+.4f}")

    # -- 7. what the shipped stopword change moved -------------------------
    print("\n7. lexical/2.1 against lexical/2.2, beyond the pass rate")
    if not (NEW_STOPWORDS <= tt.STOPWORDS):
        print("   this tree does not carry the three, so both arms below "
              "are the same run and the comparison is vacuous here; "
              "point --tree at a lexical/2.2 tree for the real one")
    def strip(m):
        m.STOPWORDS = m.STOPWORDS - NEW_STOPWORDS
    a_b, a_c = suite(fresh(spec), tree)
    b_b, b_c = suite(fresh(spec), tree, strip)
    print(f"   with the three {a_b['passed']}/{a_b['total']}   "
          f"without {b_b['passed']}/{b_b['total']}")
    fa = sorted(i for i in a_c if not a_c[i]["passed"])
    fb = sorted(i for i in b_c if not b_c[i]["passed"])
    print(f"   failing with   : {fa}")
    print(f"   failing without: {fb}")
    print(f"   same set: {fa == fb}")
    print(f"   narrow-flag differences: "
          f"{[i for i in a_c if a_c[i]['narrow'] != b_c[i]['narrow']]}")
    floor = a_b.get("policy", {}).get("floor", tt.FLOOR)
    print(f"   floor-side differences: "
          f"{[i for i in a_c if (a_c[i]['library_score'] < floor) != (b_c[i]['library_score'] < floor)]}")

    # -- 8. the literature, as arithmetic ----------------------------------
    print("\n8. arxiv:2602.05366 table 5, the only measured weights on this field")
    cells = [("E5-Base", "APIGen", 26.90, 26.20),
             ("E5-Base", "APIBank", 26.40, 24.60),
             ("E5-Base", "Toolink", 29.40, 7.90),
             ("GTE", "APIGen", 38.00, 14.50),
             ("GTE", "APIBank", 48.00, 22.00),
             ("GTE", "Toolink", 24.50, 33.40)]
    rs = []
    for retriever, dataset, desc, ex in cells:
        r = ex / desc
        rs.append(r)
        print(f"   {retriever:8s} {dataset:8s} description {desc:5.2f}%  "
              f"example {ex:5.2f}%  example/description {r:.3f}x")
    print(f"   range {min(rs):.3f}x to {max(rs):.3f}x, median "
          f"{statistics.median(rs):.3f}x, below 1.0 in "
          f"{sum(1 for r in rs if r < 1)} of {len(rs)} cells")
    print(f"   USE_WHEN_BOOST on this tree: {tt.USE_WHEN_BOOST}x")


if __name__ == "__main__":
    main()
