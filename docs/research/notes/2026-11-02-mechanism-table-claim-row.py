#!/usr/bin/env python3
"""The claim row the skill seat asked for, derived rather than relayed.

    python3 docs/research/notes/2026-11-02-mechanism-table-claim-row.py
    python3 docs/research/notes/2026-11-02-mechanism-table-claim-row.py --check
    python3 docs/research/notes/2026-11-02-mechanism-table-claim-row.py --html PATH

The skill seat asked this seat for one claim row covering Table A6 of
EvoSafeHarness (arxiv.org/abs/2609.05903), the per-cell mechanism inventory.
Their report is that rows 306 to 310 carry that paper's attack-success and
utility results and nothing carries the inventory, while
`skills/agent-containment` delta 5 and `skills/agent-security-measurement` now
both reason from it. Their words: a row to write rather than a reading to redo.

That report is RELAYED and this run could not check it: there is no
`NEON_RO_URL` here either, so the five existing rows were never read. The one
piece of corroboration available offline is `docs/research/reading-queue.md`,
which records this paper as distilled 2026-09-14 with 5 claims, and the
2026-10-12 brief, which cites C307, C308 and C309 for its attack-success and
utility figures. That agrees with their count and does not establish the id
range, so nothing below depends on it.

This file is the deriving half, and it deliberately does NOT import the skill
seat's `skills/_validation/evosafe_mechanism_table.py`. That instrument vendors
a colspan-expanded grid and offers `--reparse` to check the vendoring. Importing
it would make this row rest on their parse; parsing the page again here, with a
different parser, makes agreement corroboration instead. Both parsers are run
against the same fetched page and `--check` fails if they disagree on any cell.

What `--check` asserts, each of which is a sentence in the claim row:

  1.  Table A6 has exactly 21 `<tr>`: two header rows, three stratum banners
      and SIXTEEN mechanism families. This is the assertion that matters most
      and neither seat had made it. A parser keyed on a hard-coded family list
      skips a row it does not know, silently, and every denominator in the
      claim ("1 of 16") is that list's length. Counting the rows first is what
      turns "1 of 16 families" into "1 of every family in the table".
  2.  The 15 per-cell compositions, as (mechanisms, code, judge, prose).
  3.  The five counts the product answer rests on: 9 cells with prose, 6
      without, 4 with no runtime model call, 2 pure deterministic code, and 15
      of 15 shipping deterministic code.
  4.  1 of 16 families is realized more than one way, and it is the
      action-nature gate, `d` in 2 cells and `s` in 3, all five in
      os-filesystem. The skill seat's narrowing, independently confirmed.
  5.  The scope-vs-task judge is a judge in 8 of the 8 cells it appears in,
      which is the hole their checklist gained an item for.
  6.  The domain clustering: 4 of the 6 prose-dropping cells are finance,
      which is 4 of the 5 finance cells.
  7.  Two facts that CONTRADICT the paper's own stated reason for prose
      removal, which is why the claim row states the inventory and not the
      mechanism. See the note beside this file.

Exit 0 when every assertion holds, 1 on the first that does not.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import urllib.request

PAPER = "arxiv:2609.05903"
PAGE = "https://arxiv.org/html/2609.05903"
CAPTION = "Mechanism inventory of the fifteen best"
DEFAULT_HTML = ".cache/html/2609.05903.html"

DOMAINS = ("os-filesystem", "finance", "telecom")
MODEL_KEYS = ("S", "G", "K", "Q", "D")
CELLS = tuple(f"{d}/{m}" for d in DOMAINS for m in MODEL_KEYS)

# The three stratum banner rows, which are full-width and carry no mechanism.
BANNERS = ("Shared backbone", "Domain signature", "Model-specific patch")

# Expected shape, asserted rather than assumed (assertion 1).
EXPECT_ROWS = 21
EXPECT_FAMILIES = 16

# Expected per-cell composition: mechanisms, deterministic code, judge, prose.
EXPECT_CELLS = {
    "os-filesystem/S": (4, 1, 2, 1),
    "os-filesystem/G": (7, 5, 1, 1),
    "os-filesystem/K": (5, 2, 2, 1),
    "os-filesystem/Q": (2, 1, 1, 0),
    "os-filesystem/D": (4, 3, 0, 1),
    "finance/S":       (7, 5, 1, 1),
    "finance/G":       (5, 4, 1, 0),
    "finance/K":       (3, 2, 1, 0),
    "finance/Q":       (4, 4, 0, 0),
    "finance/D":       (7, 6, 1, 0),
    "telecom/S":       (6, 4, 1, 1),
    "telecom/G":       (4, 3, 0, 1),
    "telecom/K":       (3, 3, 0, 0),
    "telecom/Q":       (4, 2, 1, 1),
    "telecom/D":       (5, 3, 1, 1),
}


def fetch(path: str) -> str:
    """The page, cached on disk, because every number below is derived from it."""
    p = pathlib.Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8", errors="replace")
    p.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(PAGE, headers={"User-Agent": "alexandria-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode("utf-8", errors="replace")
    p.write_text(body, encoding="utf-8")
    return body


def rows_of_table(page: str) -> list[list[str]]:
    """Every `<tr>` of Table A6, colspan-expanded, as plain cell text.

    Nothing is filtered here, deliberately. The caller counts the rows, and a
    parser that drops the rows it does not recognise cannot be asked how many
    rows there were.
    """
    marker = page.find(CAPTION)
    if marker < 0:
        raise SystemExit(f"Table A6's caption is not on this page; is it {PAPER}?")
    start = page.rfind("<table", 0, marker)
    end = page.find("</table>", start)
    table = page[start : end + len("</table>")]

    out = []
    for tr in re.findall(r"<tr.*?</tr>", table, re.S):
        cells: list[str] = []
        for cell in re.finditer(r"<t[hd]\b(.*?)</t[hd]>", tr, re.S):
            attrs, _, inner = cell.group(1).partition(">")
            text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
            span = re.search(r'colspan=["\']?(\d+)', attrs)
            cells.extend([text] * (int(span.group(1)) if span else 1))
        if cells:
            out.append(cells)
    return out


def families_of(rows: list[list[str]]) -> dict[str, list[str]]:
    """The 16 mechanism rows, keyed by family, as 15 marks of `d`/`s`/`n`/``.

    A mechanism row is one whose first cell is not a banner and whose remaining
    cells are all empty or one of the three legend marks. That test is on the
    CONTENT rather than on a list of family names, so a family this seat has
    never heard of is picked up rather than skipped.
    """
    grid: dict[str, list[str]] = {}
    for cells in rows:
        head, entries = cells[0], cells[1:]
        if head in BANNERS or len(entries) != len(CELLS):
            continue
        if all(e in ("", "d", "s", "n") for e in entries) and head:
            grid[head] = list(entries)
    return grid


def compose(grid: dict[str, list[str]]) -> dict[str, tuple[int, int, int, int]]:
    out = {}
    for i, cell in enumerate(CELLS):
        marks = [grid[f][i] for f in grid if grid[f][i]]
        out[cell] = (len(marks), marks.count("d"), marks.count("s"), marks.count("n"))
    return out


def realizations(grid: dict[str, list[str]]) -> dict[str, dict]:
    out = {}
    for family, marks in grid.items():
        kinds = sorted({m for m in marks if m})
        out[family] = {
            "kinds": kinds,
            "cells": {k: [CELLS[i] for i, m in enumerate(marks) if m == k] for k in kinds},
        }
    return out


def code_share(comp: dict[str, tuple[int, int, int, int]]) -> dict[str, float]:
    """The circularity catch, as two numbers instead of one.

    "Prose is dropped where deterministic checks already cover the hazard"
    predicts that prose-free cells carry a higher share of deterministic code.
    Measured naively the prediction looks strongly confirmed. But the NL policy
    preamble is itself one of the mechanisms counted in the denominator, so a
    cell that KEPT its prose has prose in its own denominator and scores lower
    for that reason alone. Removing the prose row from the denominator is the
    only honest version, and it shrinks the gap by about 3.6x.
    """
    def mean(xs):
        return sum(xs) / len(xs)

    with_prose = [c for c, v in comp.items() if v[3] > 0]
    without = [c for c, v in comp.items() if v[3] == 0]
    naive_w = mean([comp[c][1] / comp[c][0] for c in with_prose])
    naive_o = mean([comp[c][1] / comp[c][0] for c in without])
    # denominator with the prose row removed
    corr_w = mean([comp[c][1] / (comp[c][0] - comp[c][3]) for c in with_prose])
    corr_o = mean([comp[c][1] / (comp[c][0] - comp[c][3]) for c in without])
    return {
        "naive_with_prose": naive_w,
        "naive_without_prose": naive_o,
        "naive_gap": naive_o - naive_w,
        "corrected_with_prose": corr_w,
        "corrected_without_prose": corr_o,
        "corrected_gap": corr_o - corr_w,
        "inflation": (naive_o - naive_w) / (corr_o - corr_w),
    }


CLAIM = (
    "In EvoSafeHarness's fifteen searched harnesses (one per domain-victim-model "
    "cell, Table A6), the realization of a safety mechanism is mostly a property "
    "of the mechanism family rather than of the deployment: only 1 of the 16 "
    "families in the table is realized more than one way across the cells it "
    "appears in, and what the deployment changes is which families are PRESENT. "
    "All 15 harnesses ship deterministic code; 9 of 15 cells carry "
    "natural-language policy and 6 ship none; 4 of 15 make no runtime model "
    "call; only 2 of 15 are pure deterministic code with neither prose nor a "
    "judge."
)

EVIDENCE = (
    "Table A6 (Appendix E, Per-Cell Mechanism Inventory) re-parsed per column "
    "from arxiv.org/html/2609.05903, whose 21 rows are two headers, three "
    "stratum banners and 16 mechanism families. Marks are the paper's own "
    "legend: d deterministic code, s quarantined LLM judge, n natural-language "
    "policy, blank absent. The one family realized two ways is the "
    "action-nature gate, code in os-filesystem/GLM-5 and /DeepSeek-V4-Flash and "
    "a judge in /Sonnet-4.6, /Kimi-K2.5 and /Qwen3.7-plus; every other family "
    "is realized identically wherever it appears, and the scope-vs-task judge "
    "is a judge in 8 of the 8 cells it occupies. The 6 prose-free cells are "
    "os-filesystem/Qwen, finance/GLM-5, finance/Kimi, finance/Qwen, "
    "finance/DeepSeek and telecom/Kimi, so 4 of the 6 are finance, which is 4 "
    "of the 5 finance cells. The 4 cells with no runtime model call are "
    "os-filesystem/DeepSeek, finance/Qwen, telecom/GLM-5 and telecom/Kimi. "
    "Section 4's own summary is \"the domain decides what to protect; the model "
    "decides how\", and its conclusion is \"agent safety is deployment-dependent: "
    "the domain sets which relations must be protected, and the model sets how "
    "strictly they must be enforced\" -- which this table supports on PRESENCE "
    "and, per family, mostly not on realization."
)

PROCEDURE = (
    "1) Read Table A6's legend, which defines three realizations of a safety "
    "relation: deterministic code in the enforcement program C, a quarantined "
    "LLM judge called by C whose policy text sits in the bundle P, and "
    "natural-language policy handed to the target model in P. "
    "2) For each mechanism in a harness, record which of the three realizes it; "
    "blank means the mechanism is absent, not unspecified. "
    "3) Label per mechanism family, not per harness: 13 of the 15 harnesses "
    "mix realizations and the 2 that do not are the pure-code cells, so no "
    "single label describes a harness. "
    "4) Treat the label as fixed for the family and the PRESENCE as chosen per "
    "deployment, which is what this table measures, and keep the action-nature "
    "gate as the one family where the realization itself moves."
)

TOPICS = ["containment", "security", "harness-engineering", "skills"]
GRADE = "controlled"


def report(path: str) -> dict:
    page = fetch(path)
    rows = rows_of_table(page)
    grid = families_of(rows)
    comp = compose(grid)
    real = realizations(grid)
    varying = {f: d for f, d in real.items() if len(d["kinds"]) > 1}
    prose_free = [c for c, v in comp.items() if v[3] == 0]
    return {
        "paper": PAPER,
        "n_rows": len(rows),
        "n_families": len(grid),
        "families": sorted(grid),
        "composition": comp,
        "varying": varying,
        "prose_free": prose_free,
        "prose_free_by_domain": {
            d: sum(1 for c in prose_free if c.startswith(d + "/")) for d in DOMAINS
        },
        "no_judge": [c for c, v in comp.items() if v[2] == 0],
        "pure_code": [c for c, v in comp.items() if v[2] == 0 and v[3] == 0],
        "with_code": [c for c, v in comp.items() if v[1] > 0],
        "scope_judge": real.get("scope-vs-task judge", {}),
        "code_share": code_share(comp),
        "mech_count_mean_with_prose": sum(
            comp[c][0] for c in comp if comp[c][3] > 0
        ) / sum(1 for c in comp if comp[c][3] > 0),
        "mech_count_mean_without_prose": sum(
            comp[c][0] for c in comp if comp[c][3] == 0
        ) / len(prose_free),
        "three_thinnest": sorted(comp, key=lambda c: comp[c][0])[:3],
        "row": {
            "paper_id": PAPER,
            "claim": CLAIM,
            "evidence": EVIDENCE,
            "procedure": PROCEDURE,
            "topics": TOPICS,
            "evidence_grade": GRADE,
            "relayed": False,
            "attributed_to": None,
        },
    }


def cross_check(path: str) -> str:
    """Run the skill seat's parser on the same page and compare cell by cell.

    Theirs is the instrument two skills cite; this is the only place the two
    are made to agree on the same bytes rather than on the same prose.
    """
    root = pathlib.Path(__file__).resolve().parents[3]
    theirs = root / "skills/_validation/evosafe_mechanism_table.py"
    if not theirs.exists():
        return (f"cross-check SKIPPED: {theirs.relative_to(root)} is not in this "
                "working tree (it is on the skill seat's open branch)")
    sys.path.insert(0, str(theirs.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_evosafe_theirs", theirs)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mine = families_of(rows_of_table(fetch(path)))
    other = mod.reparse(path)
    if set(mine) != set(other):
        raise SystemExit(f"cross-check FAILED on family set: "
                         f"{sorted(set(mine) ^ set(other))}")
    bad = {f: (mine[f], other[f]) for f in mine if mine[f] != other[f]}
    if bad:
        for f, (a, b) in bad.items():
            print(f"DISAGREES {f}\n  mine   {a}\n  theirs {b}", file=sys.stderr)
        raise SystemExit("cross-check FAILED")
    return (f"cross-check PASSED: two independent parsers agree on all "
            f"{len(mine)} x {len(CELLS)} cells")


def check(r: dict) -> int:
    fails = []

    def want(label, got, expected):
        if got != expected:
            fails.append(f"{label}: got {got!r}, expected {expected!r}")

    want("Table A6 <tr> count", r["n_rows"], EXPECT_ROWS)
    want("mechanism families", r["n_families"], EXPECT_FAMILIES)
    for cell, expected in EXPECT_CELLS.items():
        want(f"composition {cell}", r["composition"][cell], expected)
    want("cells carrying prose", sum(1 for c in r["composition"]
                                    if r["composition"][c][3] > 0), 9)
    want("cells with no prose", len(r["prose_free"]), 6)
    want("cells with no runtime model call", len(r["no_judge"]), 4)
    want("pure deterministic cells", len(r["pure_code"]), 2)
    want("cells shipping deterministic code", len(r["with_code"]), 15)
    want("families realized more than one way", sorted(r["varying"]),
         ["action-nature gate"])
    gate = r["varying"].get("action-nature gate", {"cells": {}})
    want("action-nature gate as code", len(gate["cells"].get("d", [])), 2)
    want("action-nature gate as judge", len(gate["cells"].get("s", [])), 3)
    want("action-nature gate confined to os-filesystem",
         sorted({c.split("/")[0] for ks in gate["cells"].values() for c in ks}),
         ["os-filesystem"])
    want("scope-vs-task judge realizations", r["scope_judge"].get("kinds"), ["s"])
    want("scope-vs-task judge cells", len(r["scope_judge"]["cells"]["s"]), 8)
    want("prose-free finance cells", r["prose_free_by_domain"]["finance"], 4)
    mixing = [c for c, v in r["composition"].items()
              if sum(1 for x in v[1:] if x > 0) > 1]
    want("harnesses mixing realizations", len(mixing), 13)
    want("harnesses with a single realization",
         sorted(c for c in r["composition"] if c not in mixing),
         ["finance/Q", "telecom/K"])

    # Assertion 7: the two facts that contradict the paper's stated removal rule.
    thin = r["three_thinnest"]
    want("the three thinnest harnesses all dropped prose",
         [c for c in thin if r["composition"][c][3] == 0], thin)
    if not r["mech_count_mean_without_prose"] < r["mech_count_mean_with_prose"]:
        fails.append("prose-free cells are not the SMALLER harnesses, which is "
                     "the direction this note reports")
    cs = r["code_share"]
    if not cs["inflation"] > 3.0:
        fails.append(f"the naive code-share gap inflates the corrected one by "
                     f"{cs['inflation']:.2f}x, under the 3x this note reports")

    for f in fails:
        print(f"FAIL  {f}", file=sys.stderr)
    if fails:
        print(f"\n{len(fails)} of the row's premises do not hold.", file=sys.stderr)
        return 1
    print(f"OK  every premise of the claim row holds, re-derived from {PAGE}")
    return 0


def render(r: dict) -> str:
    c = r["composition"]
    cs = r["code_share"]
    out = [
        f"EvoSafeHarness Table A6 -> one claim row for {PAPER}",
        "=" * 72,
        "",
        f"Table A6 has {r['n_rows']} <tr>: 2 headers, {len(BANNERS)} stratum "
        f"banners, {r['n_families']} mechanism families.",
        "",
        f"{'cell':20} {'mechs':>5} {'code':>5} {'judge':>6} {'prose':>6}",
    ]
    for cell in CELLS:
        m, d, s, n = c[cell]
        out.append(f"{cell:20} {m:5} {d:5} {s:6} {n:6}")
    out += [
        "",
        f"prose present      : {sum(1 for x in c.values() if x[3] > 0)} of 15",
        f"no prose           : {len(r['prose_free'])} of 15   "
        f"({', '.join(f'{k} {v}' for k, v in r['prose_free_by_domain'].items() if v)})",
        f"no runtime judge   : {len(r['no_judge'])} of 15",
        f"pure deterministic : {len(r['pure_code'])} of 15",
        f"ships code         : {len(r['with_code'])} of 15",
        "",
        f"families realized more than one way: {len(r['varying'])} of {r['n_families']}",
    ]
    for f, d in r["varying"].items():
        for kind, cells in d["cells"].items():
            out.append(f"  {f} as {kind}: {', '.join(cells)}")
    out += [
        "",
        "AGAINST the paper's own removal rule (section 4: a generic safety policy",
        "is removed once precise checks cover it, and because it costs utility):",
        f"  the three thinnest harnesses are {', '.join(r['three_thinnest'])}, "
        f"with {', '.join(str(c[x][0]) for x in r['three_thinnest'])} mechanisms,",
        "  and all three dropped the preamble, which redundancy cannot explain.",
        f"  mean mechanisms, prose-free {r['mech_count_mean_without_prose']:.2f} "
        f"vs prose-carrying {r['mech_count_mean_with_prose']:.2f} -- the "
        "prose-carrying",
        "  harnesses are the LARGER ones, the reverse of the prediction.",
        "",
        "And the statistic that looks like support, corrected:",
        f"  deterministic share, naive     : {cs['naive_without_prose']:.4f} "
        f"prose-free vs {cs['naive_with_prose']:.4f} -> gap {cs['naive_gap']:.4f}",
        f"  with the prose row removed     : {cs['corrected_without_prose']:.4f} "
        f"vs {cs['corrected_with_prose']:.4f} -> gap {cs['corrected_gap']:.4f}",
        f"  the naive gap is {cs['inflation']:.2f}x the honest one, because the "
        "prose row sits in",
        "  its own denominator.",
        "",
        "-" * 72,
        "THE ROW, ready to apply:",
        "-" * 72,
        json.dumps(r["row"], indent=2),
    ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--html", default=DEFAULT_HTML,
                    help=f"local copy of {PAGE}; fetched and cached if absent")
    ap.add_argument("--check", action="store_true",
                    help="assert every premise of the claim row; exit 1 on any failure")
    ap.add_argument("--json", metavar="PATH", help="write the machine-readable bundle")
    ap.add_argument("--no-cross-check", action="store_true",
                    help="skip comparing against the skill seat's parser")
    args = ap.parse_args()

    r = report(args.html)
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(r, indent=2, sort_keys=True,
                                                      default=list) + "\n")
    if args.check:
        rc = check(r)
        if not args.no_cross_check:
            print(cross_check(args.html))
        return rc
    print(render(r))
    if not args.no_cross_check:
        print()
        print(cross_check(args.html))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
