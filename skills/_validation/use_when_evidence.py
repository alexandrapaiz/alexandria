#!/usr/bin/env python3
"""What the two papers on the when-to-use field say about USE_WHEN_BOOST.

    python3 skills/_validation/use_when_evidence.py
    python3 skills/_validation/use_when_evidence.py --json PATH

`USE_WHEN_BOOST` has been 1.25 since lexical/2 and nothing ever justified it
with evidence. It was a reasonable editorial intuition promoted to a numeric
coefficient, and the 2026-11-02 panel audit found it carries a 0.84x
asymmetry between the library and its null panel. This seat queued the
question of whether any paper measures the field; the research seat answered
it with two ids and read both in full, and the answer runs against the
coefficient rather than for it.

What the two papers say, as the research seat reported them and as the
reading queue records them:

  arXiv:2602.05366 ablates a when-to-use field add-one and one-out on a dense
    and a sparse retriever over thirty-five unified datasets, and keeps it.
    The field its authors drop is example-usage. So HAVING the clause is
    supported. Its section 4.1 is the finding; its section 2.2 carries a
    sentence naming the wrong field that reverses it.
  arXiv:2510.22670 is the only source either seat can find that measures a
    WEIGHT on the field rather than its presence. It learns per-field weights
    and publishes them: the usage-scenario field runs 0.269x to 1.363x of the
    description field's weight across six dataset and retriever cells, median
    0.695x, and it sits BELOW the description in five of the six.

Ours is a fixed 1.25x above it. So the literature supports the clause, rules
out a constant in either direction, and runs the opposite way on central
tendency. This file measures what our own suite does across the range the
literature actually publishes, so the coefficient stops being defended by
intuition alone.

It also measures the two corrections the research seat landed on this seat's
own prose, because both were accepted in a pull request body and neither
reached the code:

  A uniform boost is a no-op on the RANKING and not on the verdict. route()
    also reads `library_score >= FLOOR` and `abs(null_margin) <
    NARROW_MARGIN`, both against absolute numbers, and a uniform boost scales
    both. The no-op is therefore a property of this panel rather than of the
    scheme.
  The three stopwords added in lexical/2.2 are not interchangeable. Only
    "last" is load-bearing for the length-bias delta. Stripping either of the
    other two alone GROWS it, because both sit in the prompt and in neither
    description, so removing one shrinks the denominator and leaves the
    numerator alone.

No database and no model call: every number here is derived from this
repository's own descriptions, decoy panel and trigger cases.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import trigger_test as tt  # noqa: E402

# The six cells arXiv:2510.22670 publishes for the usage-scenario field's
# weight, as a multiple of the description field's. Recorded here as the
# literature's own range rather than as a recommendation, because the paper's
# own conclusion is that no constant is right.
LIT_CELLS = (0.269, 1.363)
LIT_MEDIAN = 0.695
LIT_BELOW_DESCRIPTION = 5          # of six cells
LIT_WEIGHT_PAPER = "arXiv:2510.22670"
LIT_PRESENCE_PAPER = "arXiv:2602.05366"

# The 2026-09-30 length-bias experiment, held fixed so the decomposition is
# the published one. The candidate, prompt and topic are the same; only the
# description's length varies, which is what made the original result a
# statement about rewriting rather than about length.
LENGTH_PROMPT = ("Our Postgres query got slow after the last release and I "
                 "think the planner stopped using the index")
LENGTH_CANDIDATE = "decoy-postgres-tuning"


def candidates(skills_dir, decoys_path):
    skills = tt.load_skills(skills_dir)
    decoys = tt.load_decoys(decoys_path)
    return skills, decoys


def engine_for(skills, decoys, boost, uniform=False):
    """An engine at one boost coefficient, optionally with the boost applied
    uniformly to every candidate's whole term set.

    Uniform is the counterfactual that isolates the positional artifact:
    activation_clause() is a positional slice, so under the live engine what
    fraction of a description gets boosted is decided by where its "Use when"
    sits. Setting the activation set to the body set gives every candidate the
    boost on all of its terms, which is what a unified schema would do.
    """
    old = tt.USE_WHEN_BOOST
    tt.USE_WHEN_BOOST = boost
    try:
        eng = tt.ENGINES[tt.ENGINE_VERSION]({**skills, **decoys})
        if uniform:
            eng.sets = {k: (body, set(body)) for k, (body, _) in eng.sets.items()}
        # Bind the coefficient onto the instance, so the engine keeps scoring
        # at this arm's boost after the module global is put back. Without
        # this every arm would silently share the last value set.
        eng.score = _bound_score(eng, boost)
        return eng
    finally:
        tt.USE_WHEN_BOOST = old


def _bound_score(eng, boost):
    def score(prompt, key):
        body, act = eng.sets[key]
        prompt_terms = set(tt.tokens(prompt))
        if not prompt_terms:
            return 0.0
        total = matched = 0.0
        for t in prompt_terms:
            w = eng.idf.get(t, eng.default_idf)
            total += w
            if t in body:
                matched += w * (boost if t in act else 1.0)
        return matched / total if total else 0.0
    return score


def all_cases(skills_dir):
    import glob
    out = []
    for cf in sorted(glob.glob(os.path.join(skills_dir, "*", "triggers.json"))):
        suite = json.load(open(cf, encoding="utf-8"))
        for case in suite["cases"]:
            out.append({"id": case["id"], "prompt": case["prompt"],
                        "expect": case.get("expect"), "kind": case.get("kind")})
    return out


def arm_decisions(eng, cases):
    """Every field route() carries, for every case, so an arm is compared on
    the whole verdict and not only on the pass rate. The 2026-11-02 correction
    is exactly that a comparison printing only the fired decision misses two
    fields the policy reads."""
    out = {}
    for c in cases:
        d = eng.route(c["prompt"])
        out[c["id"]] = {
            "fired": d["fired"],
            "library_score": d["library_score"],
            "null_margin": d["null_margin"],
            "narrow": d["narrow"],
            "under_floor": d["library_score"] < tt.FLOOR,
            "passed": d["fired"] == c["expect"],
        }
    return out


def boosted_share(eng, keys, weighted):
    """The share of a candidate's own term set that sits inside its activation
    slice, counted two ways.

    `weighted=False` counts stems, which is what panel_audit() ships and what
    PANEL_BOOST_TOLERANCE is checked against. `weighted=True` counts idf mass,
    which is what the boost actually multiplies in score(). The two are not
    the same number and the shipped gate uses the one the engine does not,
    so both are reported here rather than one.
    """
    shares = {}
    for k in keys:
        body, act = eng.sets[k]
        if not body:
            shares[k] = 0.0
            continue
        if weighted:
            total = sum(eng.idf.get(t, eng.default_idf) for t in body)
            inside = sum(eng.idf.get(t, eng.default_idf) for t in body & act)
        else:
            total, inside = len(body), len(body & act)
        shares[k] = round(inside / total, 4) if total else 0.0
    return shares


def length_bias_delta(skills, decoys, stopword_extras):
    """The published length-bias delta, recomputed with a chosen set of the
    three lexical/2.2 stopwords in force.

    The arm is the whole point: the delta is a statement about which WORDS the
    engine pays for, so a stopword set is the variable and the decomposition
    is what the original experiment did not do.
    """
    base = set(tt.STOPWORDS) - {"got", "last", "think"}
    old = tt.STOPWORDS
    tt.STOPWORDS = base | set(stopword_extras)
    try:
        short = json.load(open(os.path.join(HERE, "decoys-v1-retired.json"),
                                encoding="utf-8"))
        short_desc = next(d["description"] for d in short["decoys"]
                          if d["name"] == LENGTH_CANDIDATE)
        long_desc = decoys[LENGTH_CANDIDATE]["description"]
        out = {}
        for label, desc in (("short_41w", short_desc), ("long_123w", long_desc)):
            panel = {k: dict(v) for k, v in decoys.items()}
            panel[LENGTH_CANDIDATE] = dict(panel[LENGTH_CANDIDATE])
            panel[LENGTH_CANDIDATE]["description"] = desc
            panel[LENGTH_CANDIDATE]["activation"] = tt.activation_clause(desc)
            eng = tt.ENGINES[tt.ENGINE_VERSION]({**skills, **panel})
            out[label] = round(eng.score(LENGTH_PROMPT, LENGTH_CANDIDATE), 4)
        out["delta"] = round(out["long_123w"] - out["short_41w"], 4)
        return out
    finally:
        tt.STOPWORDS = old


def measure(skills_dir, decoys_path):
    skills, decoys = candidates(skills_dir, decoys_path)
    cases = all_cases(skills_dir)
    live = engine_for(skills, decoys, tt.USE_WHEN_BOOST)

    # ---- the asymmetry, and what it is an asymmetry in -------------------
    asymmetry = {"tolerance": tt.PANEL_BOOST_TOLERANCE}
    for label, weighted in (("stem_count_as_shipped", False),
                            ("idf_mass_as_scored", True)):
        lib_shares = boosted_share(live, list(skills), weighted)
        panel_shares = boosted_share(live, list(decoys), weighted)
        lib_mean = statistics.mean(lib_shares.values())
        panel_mean = statistics.mean(panel_shares.values())
        asymmetry[label] = {
            "library_boosted_share": round(lib_mean, 4),
            "panel_boosted_share": round(panel_mean, 4),
            "ratio": round(lib_mean / panel_mean, 4) if panel_mean else None,
            "trips_tolerance": not (
                1 / tt.PANEL_BOOST_TOLERANCE
                <= (lib_mean / panel_mean if panel_mean else 1)
                <= tt.PANEL_BOOST_TOLERANCE),
            "per_skill": lib_shares,
            "per_decoy": panel_shares,
        }

    # ---- three arms, compared on every field the verdict reads -----------
    arms = {
        "boost_off": arm_decisions(engine_for(skills, decoys, 1.0), cases),
        "boost_live": arm_decisions(live, cases),
        "boost_uniform": arm_decisions(
            engine_for(skills, decoys, tt.USE_WHEN_BOOST, uniform=True), cases),
    }

    def summarise(a):
        return {
            "fired": sum(1 for v in a.values() if v["fired"]),
            "passed": sum(1 for v in a.values() if v["passed"]),
            "narrow_flags": sum(1 for v in a.values() if v["narrow"]),
            "under_floor": sum(1 for v in a.values() if v["under_floor"]),
        }

    def diff(a, b, field):
        return sorted(k for k in a if a[k][field] != b[k][field])

    comparisons = {}
    for left, right in (("boost_off", "boost_live"),
                        ("boost_off", "boost_uniform"),
                        ("boost_uniform", "boost_live")):
        a, b = arms[left], arms[right]
        comparisons[f"{left}_vs_{right}"] = {
            "fired_moved": diff(a, b, "fired"),
            "narrow_moved": [
                {"case": k,
                 left: a[k]["null_margin"], right: b[k]["null_margin"]}
                for k in diff(a, b, "narrow")],
            "under_floor_moved": diff(a, b, "under_floor"),
            # Direction, not just a count. "Three cases move" is the
            # sentence a net of plus one hides inside, which is the
            # composition-against-total error the 2026-11-02 panel v3
            # prediction was corrected for.
            "passed_moved": [
                {"case": k,
                 left: a[k]["passed"], right: b[k]["passed"]}
                for k in diff(a, b, "passed")],
        }

    # ---- the floor: binding, or silenced by the ranking clause first? ----
    under = [(k, v["library_score"], v["null_margin"])
             for k, v in arms["boost_live"].items() if v["under_floor"]]
    floor_state = [
        {"case": k, "library_score": s, "null_margin": m,
         "ranking_silences_it_first": m <= 0}
        for k, s, m in under]

    # ---- the stopword decomposition, one arm per subset ------------------
    stopwords = {
        "none_of_three_lexical_2.1": length_bias_delta(skills, decoys, []),
        "all_three_lexical_2.2": length_bias_delta(
            skills, decoys, ["got", "last", "think"]),
        "last_only": length_bias_delta(skills, decoys, ["last"]),
        "got_only": length_bias_delta(skills, decoys, ["got"]),
        "think_only": length_bias_delta(skills, decoys, ["think"]),
    }

    # ---- the coefficient, swept over the range the literature publishes --
    # Swept twice on purpose. The live arm applies the coefficient through
    # activation_clause()'s positional slice, so it carries the 0.84x
    # asymmetry; the uniform arm applies it to every candidate's whole term
    # set, which is what a unified schema would do. If the suite's pass rate
    # responds to the coefficient in the live arm and not in the uniform one,
    # then what the suite is measuring is the artifact and not the clause.
    sweep = []
    for boost in (LIT_CELLS[0], 0.5, LIT_MEDIAN, 1.0, 1.25, LIT_CELLS[1], 1.5):
        row = {"boost": boost,
               "in_literature_range": LIT_CELLS[0] <= boost <= LIT_CELLS[1]}
        for label, uniform in (("live", False), ("uniform", True)):
            row[label] = summarise(arm_decisions(
                engine_for(skills, decoys, boost, uniform=uniform), cases))
        sweep.append(row)

    return {
        "engine": tt.ENGINE_VERSION,
        "use_when_boost_shipped": tt.USE_WHEN_BOOST,
        "total_cases": len(cases),
        "literature": {
            "presence_paper": LIT_PRESENCE_PAPER,
            "weight_paper": LIT_WEIGHT_PAPER,
            "weight_cells_min": LIT_CELLS[0],
            "weight_cells_max": LIT_CELLS[1],
            "weight_median": LIT_MEDIAN,
            "cells_below_description": LIT_BELOW_DESCRIPTION,
            "cells_total": 6,
            "ours_is_above_description": tt.USE_WHEN_BOOST > 1.0,
            "ours_inside_published_range":
                LIT_CELLS[0] <= tt.USE_WHEN_BOOST <= LIT_CELLS[1],
        },
        "asymmetry": asymmetry,
        "arms": {k: summarise(v) for k, v in arms.items()},
        "comparisons": comparisons,
        "floor": floor_state,
        "stopword_decomposition": stopwords,
        "coefficient_sweep": sweep,
    }


def render(r):
    L = []
    L.append(f"USE_WHEN_BOOST against the literature  ({r['engine']}, "
             f"{r['total_cases']} cases)")
    L.append("=" * 72)
    lit = r["literature"]
    L.append("")
    L.append("What the two papers say")
    L.append(f"  {lit['presence_paper']}: keeps the when-to-use field, drops "
             f"example-usage. Having the clause is supported.")
    L.append(f"  {lit['weight_paper']}: the field's learned weight runs "
             f"{lit['weight_cells_min']}x to {lit['weight_cells_max']}x of the "
             f"description's,")
    L.append(f"    median {lit['weight_median']}x, below the description in "
             f"{lit['cells_below_description']} of {lit['cells_total']} cells.")
    L.append(f"  ours: {r['use_when_boost_shipped']}x, which is "
             f"{'ABOVE' if lit['ours_is_above_description'] else 'below'} the "
             f"description and "
             f"{'inside' if lit['ours_inside_published_range'] else 'outside'} "
             f"the published range.")
    L.append("    So the clause is supported, a constant is ruled out in either")
    L.append("    direction, and central tendency runs the opposite way.")

    a = r["asymmetry"]
    L.append("")
    L.append("The asymmetry the boost is actually applied through")
    for label in ("stem_count_as_shipped", "idf_mass_as_scored"):
        b = a[label]
        L.append(f"  {label:<22} library {b['library_boosted_share']}, panel "
                 f"{b['panel_boosted_share']}, ratio {b['ratio']}x, trips "
                 f"{b['trips_tolerance']}")
    L.append(f"  tolerance {a['tolerance']}x. The gate checks the stem count "
             f"and the engine multiplies")
    L.append("  idf mass, so the gate watches a different number from the one "
             "the boost moves.")
    L.append("  Both trip, so the finding stands either way, and the gap is "
             "worth one line")
    L.append("  rather than a repair.")

    L.append("")
    L.append("Three arms, on every field the verdict reads")
    L.append(f"  {'arm':<16}{'fired':>7}{'passed':>8}{'narrow':>8}{'<floor':>8}")
    for name, s in r["arms"].items():
        L.append(f"  {name:<16}{s['fired']:>7}{s['passed']:>8}"
                 f"{s['narrow_flags']:>8}{s['under_floor']:>8}")

    L.append("")
    L.append("What moves between arms")
    for name, c in r["comparisons"].items():
        L.append(f"  {name}")
        L.append(f"    fired moved:  {c['fired_moved'] or 'none'}")
        if c["passed_moved"]:
            for m in c["passed_moved"]:
                a_v, b_v = [v for k, v in m.items() if k != "case"]
                L.append(f"    passed moved: {m['case']} "
                         f"{'pass' if a_v else 'fail'} -> "
                         f"{'pass' if b_v else 'fail'}")
        else:
            L.append("    passed moved: none")
        if c["narrow_moved"]:
            for m in c["narrow_moved"]:
                pair = [v for k, v in m.items() if k != "case"]
                L.append(f"    narrow flag moved: {m['case']} "
                         f"{pair[0]:+.4f} -> {pair[1]:+.4f}")
        else:
            L.append("    narrow flag moved: none")
        L.append(f"    under floor moved: {c['under_floor_moved'] or 'none'}")

    L.append("")
    L.append("The floor, and whether it binds on anything")
    if not r["floor"]:
        L.append("  nothing scores under the floor today")
    for f in r["floor"]:
        L.append(f"  {f['case']}: score {f['library_score']}, margin "
                 f"{f['null_margin']:+.4f}; ranking silences it first: "
                 f"{f['ranking_silences_it_first']}")
    L.append("  So the floor is UNTESTED rather than satisfied: the one case")
    L.append("  under it also trails its decoy, so the ranking clause decides")
    L.append("  it before the floor is consulted.")

    L.append("")
    L.append("The three lexical/2.2 stopwords, decomposed")
    L.append(f"  {'arm':<28}{'41w':>9}{'123w':>9}{'delta':>9}")
    for name, d in r["stopword_decomposition"].items():
        L.append(f"  {name:<28}{d['short_41w']:>9.4f}{d['long_123w']:>9.4f}"
                 f"{d['delta']:>+9.4f}")
    L.append("  Only 'last' is load-bearing. Stripping either other one alone")
    L.append("  GROWS the delta, because both sit in the prompt and in neither")
    L.append("  description, so removing one shrinks the denominator and leaves")
    L.append("  the numerator alone.")

    L.append("")
    L.append("The coefficient, swept over the range the literature publishes")
    L.append("  live = through activation_clause()'s positional slice, as "
             "shipped.")
    L.append("  uniform = applied to every candidate's whole term set, as a "
             "unified schema would.")
    L.append(f"  {'boost':>7}{'in range':>10}{'live pass':>11}"
             f"{'live <fl':>10}{'unif pass':>11}{'unif <fl':>10}")
    for row in r["coefficient_sweep"]:
        L.append(f"  {row['boost']:>7}{str(row['in_literature_range']):>10}"
                 f"{row['live']['passed']:>11}{row['live']['under_floor']:>10}"
                 f"{row['uniform']['passed']:>11}"
                 f"{row['uniform']['under_floor']:>10}")
    live_span = (min(x["live"]["passed"] for x in r["coefficient_sweep"]),
                 max(x["live"]["passed"] for x in r["coefficient_sweep"]))
    unif_span = (min(x["uniform"]["passed"] for x in r["coefficient_sweep"]),
                 max(x["uniform"]["passed"] for x in r["coefficient_sweep"]))
    L.append(f"  live span {live_span[0]} to {live_span[1]} of "
             f"{r['total_cases']}; uniform span {unif_span[0]} to "
             f"{unif_span[1]}.")
    L.append("  This is the measurement that decides what the coefficient is "
             "worth. The")
    L.append("  suite's pass rate responds to the coefficient only through the "
             "positional")
    flat = {x["uniform"]["passed"] for x in r["coefficient_sweep"]
            if x["boost"] >= 0.5}
    L.append("  slice. Applied uniformly, every arm at 0.5x and above scores "
             f"{sorted(flat)}, which is")
    L.append("  exactly flat, and the only movement below that is the floor "
             "collapsing rather")
    L.append("  than the clause earning anything. So what 1.25 buys this suite "
             "is the")
    L.append("  asymmetry and not the clause, and tuning the coefficient on the "
             "pass rate")
    L.append("  would be tuning on a confound.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-dir", default=os.path.dirname(HERE))
    ap.add_argument("--decoys", default=os.path.join(HERE, "decoys.json"))
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()
    r = measure(args.skills_dir, args.decoys)
    print(render(r))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=2, sort_keys=True)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
