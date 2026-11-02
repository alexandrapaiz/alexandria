#!/usr/bin/env python3
"""Receipt for the 2026-11-02 reading of the skill seat's clause-position question.

Every number in docs/research/notes/2026-11-02-clause-position.md comes from
here. No database, no model call, no network: it loads whatever
skills/_validation/trigger_test.py the tree it is pointed at holds and
measures the candidates against it.

    python3 docs/research/notes/2026-11-02-clause-position.py
    python3 docs/research/notes/2026-11-02-clause-position.py --check
    python3 docs/research/notes/2026-11-02-clause-position.py --tree /path/to/worktree

The question, queued by `skills/_validation/use_when_evidence.py` on 2026-11-02:
does any paper control for WHERE a candidate puts its when-to-use clause before
measuring what weighting that clause buys? The literature half is answered in the
note from the two papers' own text. This file answers the half that is ours: in
OUR panel, how much of the 0.84x asymmetry is explained by clause placement
alone, with no engine involved.

It also settles the one digit the two seats' instruments disagreed on, by
computing the same delta at full precision and at each of the two rounding
orders, so the disagreement is attributed rather than split.
"""
import argparse
import importlib.util
import json
import math
import os
import statistics
import sys

PROMPT = ("Our Postgres query got slow after the last release and I think "
          "the planner stopped using the index")
NEW_STOPWORDS = {"got", "last", "think"}
LENGTH_CANDIDATE = "decoy-postgres-tuning"

# arXiv:2510.22670 section 2.2's expansion prompt caps the generated
# `when_to_use` field at "less than 20 words" and marks it optional.
PAPER_CLAUSE_WORD_CAP = 20


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


def candidates(tt, tree):
    skills = tt.load_skills(os.path.join(tree, "skills"))
    decoys = tt.load_decoys(os.path.join(tree, "skills/_validation/decoys.json"))
    return skills, decoys


def placement(tt, tree):
    """Per candidate: the clause's word share of the description, the offset at
    which the literal "use when" occurs as a fraction of the description, and
    the engine's own boosted stem share. The first two need no engine at all."""
    skills, decoys = candidates(tt, tree)
    cand = {**skills, **decoys}
    eng = tt.ENGINES[tt.ENGINE_VERSION](cand)
    rows = []
    for key in cand:
        body, act = eng.sets[key]
        desc = cand[key]["description"]
        clause = cand[key].get("activation") or ""
        found = desc.lower().find("use when")
        rows.append({
            "candidate": key,
            "kind": "panel" if key in decoys else "library",
            "desc_words": len(desc.split()),
            "clause_words": len(clause.split()),
            "clause_word_share": (len(clause.split()) / len(desc.split())
                                  if desc.split() else 0.0),
            "use_when_offset": (found / len(desc)) if found >= 0 else None,
            "boosted_stem_share": (len(body & act) / len(body)) if body else 0.0,
        })
    rows.sort(key=lambda r: -r["clause_word_share"])
    return rows


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs)
                    * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")


def length_bias(spec, tree, extra):
    """The published length-bias delta at FULL precision, plus the same delta
    under the two rounding orders two seats' instruments happen to use."""
    m = fresh(spec)
    m.STOPWORDS = (m.STOPWORDS - NEW_STOPWORDS) | set(extra)
    v1 = os.path.join(tree, "skills/_validation/decoys-v1-retired.json")
    v2 = os.path.join(tree, "skills/_validation/decoys.json")
    short = next(d["description"] for d in json.load(open(v1))["decoys"]
                 if d["name"] == LENGTH_CANDIDATE)
    long_ = next(d["description"] for d in json.load(open(v2))["decoys"]
                 if d["name"] == LENGTH_CANDIDATE)
    skills = m.load_skills(os.path.join(tree, "skills"))
    decoys = m.load_decoys(v2)
    scores = []
    for text in (short, long_):
        cand = {**skills, **decoys}
        cand[LENGTH_CANDIDATE] = {**cand[LENGTH_CANDIDATE],
                                  "description": text,
                                  "activation": m.activation_clause(text)}
        scores.append(m.LexicalEngine(cand).score(PROMPT, LENGTH_CANDIDATE))
    exact = scores[1] - scores[0]
    return {
        "short": scores[0],
        "long": scores[1],
        "delta_exact": exact,
        # subtract first, round once: what this seat's instrument reports
        "delta_round_after": round(exact, 4),
        # round each score, then subtract: what the skill seat's reports
        "delta_round_before": round(round(scores[1], 4) - round(scores[0], 4), 4),
    }


def shares(eng, keys, weighted):
    """Boosted share per candidate, at full precision."""
    out = {}
    for k in keys:
        body, act = eng.sets[k]
        if not body:
            out[k] = 0.0
            continue
        if weighted:
            total = sum(eng.idf.get(t, eng.default_idf) for t in body)
            inside = sum(eng.idf.get(t, eng.default_idf) for t in body & act)
        else:
            total, inside = len(body), len(body & act)
        out[k] = inside / total
    return out


def asymmetry(tt, tree):
    """The library/panel ratio both ways, and under both aggregation orders."""
    skills, decoys = candidates(tt, tree)
    eng = tt.ENGINES[tt.ENGINE_VERSION]({**skills, **decoys})
    out = {}
    for label, weighted in (("stem_count_as_shipped", False),
                            ("idf_mass_as_scored", True)):
        lib = shares(eng, list(skills), weighted)
        pan = shares(eng, list(decoys), weighted)
        exact = statistics.mean(lib.values()) / statistics.mean(pan.values())
        pre = (statistics.mean(round(v, 4) for v in lib.values())
               / statistics.mean(round(v, 4) for v in pan.values()))
        out[label] = {
            "library": statistics.mean(lib.values()),
            "panel": statistics.mean(pan.values()),
            "ratio_exact": exact,
            "ratio_round_after": round(exact, 4),
            "ratio_round_before_aggregating": round(pre, 4),
        }
    return out


def report(tt, spec, tree):
    print("The clause-position question, measured against our own panel")
    print("=" * 72)

    rows = placement(tt, tree)
    lib = [r for r in rows if r["kind"] == "library"]
    pan = [r for r in rows if r["kind"] == "panel"]

    print("\n1. Where each candidate puts its clause, and what the boost pays it")
    print(f"   {'candidate':35s}{'kind':9s}{'clause w':>9s}{'word share':>12s}"
          f"{'offset':>9s}{'stem share':>12s}")
    for r in rows:
        off = ("%.4f" % r["use_when_offset"]) if r["use_when_offset"] is not None else "n/a"
        print(f"   {r['candidate']:35s}{r['kind']:9s}{r['clause_words']:>9d}"
              f"{r['clause_word_share']:>12.4f}{off:>9s}"
              f"{r['boosted_stem_share']:>12.4f}")

    r_ws = pearson([r["clause_word_share"] for r in rows],
                   [r["boosted_stem_share"] for r in rows])
    r_off = pearson([r["use_when_offset"] for r in rows],
                    [r["boosted_stem_share"] for r in rows])
    print(f"\n   r(clause word share, boosted stem share) = {r_ws:.4f}  "
          f"over {len(rows)} candidates")
    print(f"   r(use-when offset,   boosted stem share) = {r_off:.4f}")
    print(f"   library word share  {statistics.mean(r['clause_word_share'] for r in lib):.4f}"
          f"   panel {statistics.mean(r['clause_word_share'] for r in pan):.4f}"
          f"   ratio {statistics.mean(r['clause_word_share'] for r in lib) / statistics.mean(r['clause_word_share'] for r in pan):.4f}")
    print(f"   library stem share  {statistics.mean(r['boosted_stem_share'] for r in lib):.4f}"
          f"   panel {statistics.mean(r['boosted_stem_share'] for r in pan):.4f}"
          f"   ratio {statistics.mean(r['boosted_stem_share'] for r in lib) / statistics.mean(r['boosted_stem_share'] for r in pan):.4f}")
    sep_lib = max(r["clause_word_share"] for r in lib)
    sep_pan = min(r["clause_word_share"] for r in pan)
    print(f"   the two populations do not overlap on word share: "
          f"library max {sep_lib:.4f} < panel min {sep_pan:.4f}")
    off_lib = min(r["use_when_offset"] for r in lib)
    off_pan = max(r["use_when_offset"] for r in pan)
    print(f"   nor on offset: panel max {off_pan:.4f} < library min {off_lib:.4f}")

    print(f"\n2. Against the only published cap on this field "
          f"(arXiv:2510.22670, <{PAPER_CLAUSE_WORD_CAP} words, optional)")
    over = [r for r in rows if r["clause_words"] > PAPER_CLAUSE_WORD_CAP]
    print(f"   clauses over the cap: {len(over)}/{len(rows)}")
    cw = [r["clause_words"] for r in rows]
    print(f"   clause words: min {min(cw)}  median {statistics.median(cw)}  "
          f"max {max(cw)}  i.e. {min(cw) / PAPER_CLAUSE_WORD_CAP:.1f}x to "
          f"{max(cw) / PAPER_CLAUSE_WORD_CAP:.1f}x the cap")

    print("\n3. The one digit the two instruments disagreed on")
    print(f"   {'arm':28s}{'41w':>9s}{'123w':>9s}{'exact':>12s}"
          f"{'round after':>13s}{'round before':>14s}")
    for label, extra in (("none stripped (2.1)", ()),
                         ("'last' alone", ("last",)),
                         ("'got' alone", ("got",)),
                         ("'think' alone", ("think",)),
                         ("all three (2.2)", tuple(NEW_STOPWORDS))):
        d = length_bias(spec, tree, extra)
        flag = "  <-- differs" if d["delta_round_after"] != d["delta_round_before"] else ""
        print(f"   {label:28s}{d['short']:>9.4f}{d['long']:>9.4f}"
              f"{d['delta_exact']:>+12.7f}{d['delta_round_after']:>+13.4f}"
              f"{d['delta_round_before']:>+14.4f}{flag}")

    print("\n4. The asymmetry, under both aggregation orders")
    for label, a in asymmetry(tt, tree).items():
        flag = ("  <-- differs"
                if a["ratio_round_after"] != a["ratio_round_before_aggregating"]
                else "")
        print(f"   {label:24s} library {a['library']:.6f}  panel {a['panel']:.6f}")
        print(f"   {'':24s} ratio exact {a['ratio_exact']:.7f}  "
              f"round after {a['ratio_round_after']:.4f}  "
              f"round before aggregating {a['ratio_round_before_aggregating']:.4f}"
              f"{flag}")


PREMISES = [
    # (description, callable returning (actual, expected))
    ("17 candidates: 9 library skills and 8 decoys",
     lambda tt, spec, tree: (
         (len([r for r in placement(tt, tree) if r["kind"] == "library"]),
          len([r for r in placement(tt, tree) if r["kind"] == "panel"])),
         (9, 8))),
    ("every candidate's clause exceeds the paper's 20-word cap",
     lambda tt, spec, tree: (
         len([r for r in placement(tt, tree)
              if r["clause_words"] > PAPER_CLAUSE_WORD_CAP]),
         len(placement(tt, tree)))),
    ("clause word share and boosted stem share correlate above 0.97",
     lambda tt, spec, tree: (
         pearson([r["clause_word_share"] for r in placement(tt, tree)],
                 [r["boosted_stem_share"] for r in placement(tt, tree)]) > 0.97,
         True)),
    ("the two populations do not overlap on clause word share",
     lambda tt, spec, tree: (
         max(r["clause_word_share"] for r in placement(tt, tree)
             if r["kind"] == "library")
         < min(r["clause_word_share"] for r in placement(tt, tree)
               if r["kind"] == "panel"),
         True)),
    ("nor on where the literal 'use when' falls",
     lambda tt, spec, tree: (
         max(r["use_when_offset"] for r in placement(tt, tree)
             if r["kind"] == "panel")
         < min(r["use_when_offset"] for r in placement(tt, tree)
               if r["kind"] == "library"),
         True)),
    ("word share alone recovers the stem-share ratio to within 0.04",
     lambda tt, spec, tree: (
         abs(_ratio(tt, tree, "clause_word_share")
             - _ratio(tt, tree, "boosted_stem_share")) < 0.04,
         True)),
    ("'got' alone: the exact delta is 0.15017, which rounds to 0.1502",
     lambda tt, spec, tree: (
         (round(length_bias(spec, tree, ("got",))["delta_exact"], 5),
          length_bias(spec, tree, ("got",))["delta_round_after"]),
         (0.15017, 0.1502))),
    ("rounding the two scores before subtracting them gives 0.1501",
     lambda tt, spec, tree: (
         length_bias(spec, tree, ("got",))["delta_round_before"], 0.1501)),
    # Compared at 12 places rather than exactly, on purpose. The engine sums
    # idf over Python sets of stems, so the summation order follows string hash
    # order, which PYTHONHASHSEED randomizes per process. The two arms are
    # mathematically equal and their floats differ at 1e-16 in some runs and
    # not others -- measured, five runs, two distinct values. An exact-equality
    # premise here would be flaky by construction.
    ("'think' alone behaves identically to 'got' alone, to 12 places",
     lambda tt, spec, tree: (
         round(length_bias(spec, tree, ("think",))["delta_exact"], 12),
         round(length_bias(spec, tree, ("got",))["delta_exact"], 12))),
    ("'last' alone takes the delta to exactly zero",
     lambda tt, spec, tree: (
         length_bias(spec, tree, ("last",))["delta_exact"], 0.0)),
    # The ratios below are engine-version dependent: the three lexical/2.2
    # stopwords sit in decoy descriptions, so they move the PANEL share and
    # leave the library share alone. Both trees are asserted, and which one
    # applies is read off the tree rather than assumed.
    ("the library stem share is 0.7963 on either engine version",
     lambda tt, spec, tree: (
         round(asymmetry(tt, tree)["stem_count_as_shipped"]["library"], 4),
         0.7963)),
    ("the stem-count ratio is 0.8435 on lexical/2.2 and 0.8433 on lexical/2.1",
     lambda tt, spec, tree: (
         asymmetry(tt, tree)["stem_count_as_shipped"]["ratio_round_after"],
         0.8435 if _is_22(tt) else 0.8433)),
    ("the idf-mass ratio's two rounding orders disagree on lexical/2.2 "
     "(0.8539 against 0.8538) and agree on lexical/2.1 (0.8537)",
     lambda tt, spec, tree: (
         (asymmetry(tt, tree)["idf_mass_as_scored"]["ratio_round_after"],
          asymmetry(tt, tree)["idf_mass_as_scored"]["ratio_round_before_aggregating"]),
         (0.8539, 0.8538) if _is_22(tt) else (0.8537, 0.8537))),
    ("the stem-count ratio agrees under both rounding orders on either tree, "
     "so that row matches by luck rather than by construction",
     lambda tt, spec, tree: (
         asymmetry(tt, tree)["stem_count_as_shipped"]["ratio_round_after"]
         == asymmetry(tt, tree)["stem_count_as_shipped"]["ratio_round_before_aggregating"],
         True)),
    # PANEL_BOOST_TOLERANCE is a lexical/2.2 addition, so a 2.1 tree is asked
    # against the same 1.15 the gate ships rather than skipped.
    ("both ratios trip the 1.15x boost tolerance on either tree",
     lambda tt, spec, tree: (
         all(not (1 / getattr(tt, "PANEL_BOOST_TOLERANCE", 1.15)
                  <= a["ratio_exact"]
                  <= getattr(tt, "PANEL_BOOST_TOLERANCE", 1.15))
             for a in asymmetry(tt, tree).values()),
         True)),

]


def _is_22(tt):
    """True on a tree carrying the three lexical/2.2 stopwords."""
    return NEW_STOPWORDS <= set(tt.STOPWORDS)


def _ratio(tt, tree, field):
    rows = placement(tt, tree)
    lib = statistics.mean(r[field] for r in rows if r["kind"] == "library")
    pan = statistics.mean(r[field] for r in rows if r["kind"] == "panel")
    return lib / pan


def check(tt, spec, tree):
    bad = 0
    for desc, fn in PREMISES:
        actual, expected = fn(tt, spec, tree)
        ok = actual == expected
        if not ok:
            bad += 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {desc}")
        if not ok:
            print(f"        got {actual!r}, expected {expected!r}")
    print(f"\n{len(PREMISES) - bad}/{len(PREMISES)} premises hold")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tree", default=".")
    ap.add_argument("--check", action="store_true",
                    help="assert the note's factual premises and exit nonzero "
                         "on any that no longer hold")
    args = ap.parse_args()
    tt, spec = load(args.tree)
    if args.check:
        sys.exit(check(tt, spec, args.tree))
    report(tt, spec, args.tree)


if __name__ == "__main__":
    main()
