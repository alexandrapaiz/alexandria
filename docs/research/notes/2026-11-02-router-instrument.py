#!/usr/bin/env python3
"""Measurements behind docs/research/notes/2026-11-02-router-instrument.md.

Drains three reading-queue questions queued 2026-09-30 by the skill seat for
skills/_validation: candidate-length invariance, null-model size, and whether
the trigger suite has the power to decide an engine change.

    python3 docs/research/notes/2026-11-02-router-instrument.py            # all
    python3 docs/research/notes/2026-11-02-router-instrument.py invariance
    python3 docs/research/notes/2026-11-02-router-instrument.py panel
    python3 docs/research/notes/2026-11-02-router-instrument.py power
    python3 docs/research/notes/2026-11-02-router-instrument.py guard

Run from the repository root. Reads only; writes nothing but temporary decoy
panels under a mkdtemp. `panel` runs the 255-subset sweep and takes a few
minutes; the others are seconds.

It lives here rather than in skills/_validation because the harness is the
skill seat's under ADR-22. Folding any of it into trigger_test.py is that
seat's call, and the run note routes the recommendation there.
"""

import itertools
import json
import math
import os
import statistics
import sys
import tempfile
from math import comb, lgamma

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "skills", "_validation"))
import trigger_test as tt  # noqa: E402

SKILLS_DIR = os.path.join(ROOT, "skills")
PANEL_V2 = os.path.join(SKILLS_DIR, "_validation", "decoys.json")
PANEL_V1 = os.path.join(SKILLS_DIR, "_validation", "decoys-v1-retired.json")

# The prompt and candidate the 2026-09-30 engine-decision doc used for its
# length table, carried verbatim so the numbers are comparable.
PROMPT = ("Our Postgres query got slow after the last release and I think the "
          "planner stopped using the index")
KEY = "decoy-postgres-tuning"


def _cands(decoys, swap_desc=None):
    out = {**tt.load_skills(SKILLS_DIR),
           **{k: dict(v) for k, v in decoys.items()}}
    if swap_desc is not None:
        out[KEY]["description"] = swap_desc
        out[KEY]["activation"] = tt.activation_clause(swap_desc)
    return out


def _score(engine_cls, decoys, swap_desc=None):
    return engine_cls(_cands(decoys, swap_desc)).score(PROMPT, KEY)


def invariance():
    """Q1: is either engine invariant to candidate description length?"""
    v1, v2 = tt.load_decoys(PANEL_V1), tt.load_decoys(PANEL_V2)
    d1, d2 = v1[KEY]["description"], v2[KEY]["description"]
    engines = [("lexical/2.1", tt.ENGINES["lexical/2.1"]),
               ("lexical/3", tt.ENGINES["lexical/3"])]

    print("A. PURE length: the same description repeated, so the term set is "
          "identical and only the word count moves")
    for name, E in engines:
        a = _score(E, v2)
        b = _score(E, v2, (d2 + " ") * 3)
        print(f"   {name:12} {tt.word_count(d2)}w={a:.4f}  "
              f"{tt.word_count((d2 + ' ') * 3)}w={b:.4f}  delta={b - a:+.4f}")
    print("   tokens() is set-ified, so repetition is exactly a no-op under "
          "both engines.\n")

    print("B. the published table, reproduced, then decomposed")
    for name, E in engines:
        a = _score(E, v1)                      # panel v1, candidate v1
        b = _score(E, v2)                      # panel v2, candidate v2
        cand_only = _score(E, v2, d1)          # panel v2, candidate v1 text
        print(f"   {name:12} short={a:.4f} long={b:.4f} delta={b - a:+.4f}"
              f"  = candidate term set {b - cand_only:+.4f}"
              f" + idf model {cand_only - a:+.4f}")
    print("   the published delta is the candidate's term set, not its "
          "length; the idf model contributes under 0.006.\n")

    print("C. which prompt terms the candidate matched, idf model held at "
          "panel v2")
    for label, desc in (("short (v1 text)", d1), ("long (v2 text)", d2)):
        cands = _cands(tt.load_decoys(PANEL_V2), desc)
        e = tt.ENGINES["lexical/2.1"](cands)
        body, act = e.sets[KEY]
        p = set(tt.tokens(PROMPT))
        total = sum(e.idf.get(t, e.default_idf) for t in p)
        print(f"   {label}: {tt.word_count(desc)} words, "
              f"|terms|={len(body)}, score={e.score(PROMPT, KEY):.4f}")
        for t in sorted(p & body, key=lambda t: -e.idf.get(t, e.default_idf)):
            w = e.idf.get(t, e.default_idf)
            boost = tt.USE_WHEN_BOOST if t in act else 1.0
            print(f"     {t:10} idf={w:.4f} boost={boost} "
                  f"contributes {w * boost / total:.4f}")


def panel(exhaustive=True):
    """Q2: what does the null panel's size decide?"""
    names = sorted(tt.load_decoys(PANEL_V2))
    base = json.load(open(PANEL_V2))
    tmp = tempfile.mkdtemp(prefix="panel-sweep-")

    def run_with(subset):
        d = dict(base)
        d["decoys"] = [x for x in base["decoys"] if x["name"] in subset]
        path = os.path.join(tmp, "panel.json")
        with open(path, "w") as f:
            json.dump(d, f)
        r = tt.run(SKILLS_DIR, path, "lexical/2.1")
        by = {}
        for s in r["suites"]:
            for c in s["cases"]:
                k = c["kind"]
                by.setdefault(k, [0, 0])
                by[k][1] += 1
                by[k][0] += bool(c["passed"])
        return r["passed"], r["total"], by

    kinds = ["positive", "negative", "confusion"]
    print(f"panel of {len(names)} decoys, library and cases and engine fixed\n")
    header = f"{'k':>2} {'subsets':>7} {'mean pass':>9} {'min':>4} {'max':>4}  "
    print(header + "  ".join(f"{x[:9]:>13}" for x in kinds))
    best = (0, None)
    worst = (10 ** 9, None)
    for k in range(1, len(names) + 1):
        subs = list(itertools.combinations(names, k))
        if not exhaustive and len(subs) > 12:
            subs = subs[:12]
        passes, acc = [], {x: [] for x in kinds}
        for s in subs:
            p, n, by = run_with(set(s))
            passes.append(p)
            for x in kinds:
                if x in by:
                    acc[x].append(by[x][0] / by[x][1])
            if p > best[0]:
                best = (p, s)
            if p < worst[0]:
                worst = (p, s)
        cells = "  ".join(f"{statistics.mean(acc[x]):13.3f}" for x in kinds)
        print(f"{k:>2} {len(subs):>7} {statistics.mean(passes):9.2f} "
              f"{min(passes):>4} {max(passes):>4}  {cells}")
    n = run_with(set(names))[1]
    print(f"\nworst panel {worst[0]}/{n} = {worst[0] / n:.3f}  {list(worst[1])}")
    print(f"best  panel {best[0]}/{n} = {best[0] / n:.3f}  {list(best[1])}")
    shipped = run_with(set(names))[0]
    print(f"shipped     {shipped}/{n} = {shipped / n:.3f}  (all {len(names)})")
    print(f"swing on a parameter nothing calibrates: "
          f"{(best[0] - worst[0]) / n:.3f} reliability points")


def _exact_p(b, nd):
    """Two-sided exact McNemar: a sign test on the discordant pairs at p=0.5."""
    if nd == 0:
        return 1.0
    tail = sum(comb(nd, i) for i in range(0, min(b, nd - b) + 1)) / 2 ** nd
    return min(1.0, 2 * tail)


def _lbinom(n, k, p):
    """log P(k successes in n trials at rate p), finite at p in {0, 1}."""
    if p >= 1.0:
        return 0.0 if k == n else float("-inf")
    if p <= 0.0:
        return 0.0 if k == 0 else float("-inf")
    return (lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
            + k * math.log(p) + (n - k) * math.log1p(-p))


def _power(N, delta, pi, alpha=0.05):
    # Sum over discordant counts out to ten standard deviations above the
    # mean; a fixed cap silently returns zero power once N*delta outgrows it,
    # which breaks the monotonicity the search below relies on.
    mean = N * delta
    cap = min(N, int(mean + 10 * math.sqrt(max(mean * (1 - delta), 1.0))) + 50)
    total = 0.0
    for nd in range(0, cap + 1):
        pnd = math.exp(_lbinom(N, nd, delta))
        if pnd < 1e-13:
            continue
        total += pnd * sum(math.exp(_lbinom(nd, b, pi))
                           for b in range(nd + 1)
                           if _exact_p(b, nd) <= alpha)
    return total


def power():
    """Q3: how many cases before an engine change is decidable?"""
    def flat(engine):
        r = tt.run(SKILLS_DIR, PANEL_V2, engine)
        return {c["id"]: c["passed"] for s in r["suites"] for c in s["cases"]}

    a, b = flat("lexical/2.1"), flat("lexical/3")
    n = len(a)
    only_a = sorted(k for k in a if a[k] and not b[k])
    only_b = sorted(k for k in a if b[k] and not a[k])
    nd = len(only_a) + len(only_b)
    print(f"paired on the same {n} cases: lexical/2.1 {sum(a.values())}, "
          f"lexical/3 {sum(b.values())}")
    print(f"concordant {n - nd}  discordant {nd} = {nd / n:.4f}")
    print(f"  2.1 only: {only_a}")
    print(f"  3 only:   {only_b}")
    print(f"exact two-sided p = {_exact_p(len(only_a), nd):.4f}\n")

    print("hard floor: the fewest discordant cases that can ever reach "
          "p<=0.05, every one falling the same way")
    for k in range(1, 9):
        verdict = "DECIDABLE" if _exact_p(k, k) <= 0.05 else ""
        print(f"  n_d={k}  best two-sided p = {_exact_p(k, k):.4f}  {verdict}")

    delta = nd / n
    print(f"\npower at alpha=0.05, discordance {delta:.4f}, by suite size")
    pis = (1.0, 0.9, 0.8, 0.67)
    print(f"{'N':>6} " + "  ".join(f"pi={p:.2f}" for p in pis))
    for N in (67, 100, 134, 176, 200, 280, 400, 517, 1000, 1601):
        print(f"{N:>6} " + "  ".join(f"{_power(N, delta, p):7.3f}"
                                     for p in pis))
    print()
    for pi in pis:
        lo, hi = 10, 8000
        while lo < hi:
            mid = (lo + hi) // 2
            if _power(mid, delta, pi) < 0.80:
                lo = mid + 1
            else:
                hi = mid
        print(f"  pi={pi:.2f}: N for 80% power = {lo}")


def guard():
    """Does the shipped panel-symmetry guard watch the variable that moves
    scores?"""
    cands = {**tt.load_skills(SKILLS_DIR), **tt.load_decoys(PANEL_V2)}
    rows = []
    for k, c in sorted(cands.items()):
        w = tt.word_count(c["description"])
        t = len(set(tt.tokens(c["description"])))
        rows.append((k, w, t, c["library"]))
    print(f"{'candidate':42} {'words':>5} {'|terms|':>7} {'t/w':>6}")
    for k, w, t, _ in rows:
        print(f"{k:42} {w:5} {t:7} {t / w:6.3f}")
    ws = [r[1] for r in rows]
    ts = [r[2] for r in rows]
    mw, mt = statistics.mean(ws), statistics.mean(ts)
    num = sum((a - mw) * (b - mt) for a, b in zip(ws, ts))
    den = (sum((a - mw) ** 2 for a in ws)
           * sum((b - mt) ** 2 for b in ts)) ** 0.5
    print(f"\nPearson r(words, |terms|) over {len(rows)} candidates "
          f"= {num / den:.4f}  (r^2 = {(num / den) ** 2:.3f})")
    for label, path in (("v1 panel", PANEL_V1), ("v2 panel", PANEL_V2)):
        sk = tt.load_skills(SKILLS_DIR)
        de = tt.load_decoys(path)
        lw = statistics.mean(tt.word_count(c["description"])
                             for c in sk.values())
        dw = statistics.mean(tt.word_count(c["description"])
                             for c in de.values())
        lt = statistics.mean(len(set(tt.tokens(c["description"])))
                             for c in sk.values())
        dt = statistics.mean(len(set(tt.tokens(c["description"])))
                             for c in de.values())
        print(f"  {label}: library/decoy words {lw / dw:.2f}x  "
              f"(gated at 1.35x)   term sets {lt / dt:.2f}x  (ungated)")


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    parts = {"invariance": invariance, "panel": panel,
             "power": power, "guard": guard}
    if which == "all":
        for name, fn in parts.items():
            print(f"\n{'=' * 72}\n{name}\n{'=' * 72}")
            fn()
        return 0
    if which not in parts:
        print(f"unknown section {which!r}; one of {sorted(parts)} or 'all'",
              file=sys.stderr)
        return 2
    parts[which]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
