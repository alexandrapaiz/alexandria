#!/usr/bin/env python3
"""EvoSafeHarness Table A6, re-parsed per column, for the containment checklist.

    python3 skills/_validation/evosafe_mechanism_table.py
    python3 skills/_validation/evosafe_mechanism_table.py --json PATH
    python3 skills/_validation/evosafe_mechanism_table.py --reparse evosafe.html

The skill seat queued a product question on 2026-09-30: six of fifteen searched
safety harnesses in EvoSafeHarness (arxiv.org/abs/2609.05903) dropped their
natural-language policy and four made no runtime model call, so is some of what
this library sells in that territory a policy artifact rather than a SKILL.md?

The research seat read the paper in full and answered no, and routed one
checklist column here instead (board note `660ad8e5`, 2026-11-02). This file is
this seat's own re-derivation of the numbers behind that answer, because the
answer turns on a count the queue line could not see.

Why a parser rather than a quotation. The paper's Table A6 is a 15-column grid,
one column per (domain, victim model) cell, and its information is in WHICH
column each entry sits in. Blank means the mechanism is absent. Every plain-text
extraction of the page collapses the blanks, so `read_paper.py` renders the NL
policy row as nine `n`s in a row and loses which six cells are the empty ones.
Nine of fifteen is still recoverable from that; "which four columns have no
judge" and "which cells have neither" are not. So the row counts survive the
extraction and every per-column count is destroyed by it, and the per-column
counts are the ones that answer the question.

The grid below is vendored from the HTML source's `<tr>`/`<td>` structure,
colspan-expanded, and `--reparse` re-derives it from a local copy of
https://arxiv.org/html/2609.05903 so the vendoring is checkable rather than
asserted.

Table A6's own legend defines the three realizations, and they are the three
labels the containment checklist column now uses:

    d  deterministic code        enforced by C, the harness program
    s  quarantined LLM judge     enforced by C; the judge's policy text is in P
    n  natural-language policy   target-model policy, in P

So `d` and `s` are both the harness's own enforcement and `n` is prose handed to
the model being defended. That distinction is why "no prose" and "no model call"
are different questions with different answers.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys

# Column order of Table A6: three domains, five victim models each.
DOMAINS = ("os-filesystem", "finance", "telecom")
MODELS = ("Sonnet 4.6", "GLM-5", "Kimi-K2.5", "Qwen3.7-plus", "DeepSeek-V4-Flash")
MODEL_KEYS = ("S", "G", "K", "Q", "D")
COLUMNS = tuple(f"{d}/{m}" for d in DOMAINS for m in MODEL_KEYS)

# Table A6's own furniture: the rows that are not mechanism families. The table
# has 21 rows, of which 2 are headers, 3 are section banners and 16 are
# families. Naming them is what lets the parser below fail on a row it has never
# seen without failing on the four it sees every time.
NON_FAMILY_ROWS = ("", "Mechanism family", "Domain signature",
                   "Shared backbone", "Model-specific patch")
TABLE_ROWS = 21
FAMILY_ROWS = 16

STRATA = {
    "NL policy preamble": "shared backbone",
    "argument hygiene": "shared backbone",
    "scope-vs-task judge": "shared backbone",
    "content/injection auditor": "shared backbone",
    "action-nature gate": "domain signature",
    "egress/destination scope": "domain signature",
    "wash/drain trade ledger": "domain signature",
    "trade-parameter scope": "domain signature",
    "caller/entity scope gate": "domain signature",
    "volume/velocity cap": "domain signature",
    "credential/PII redaction": "domain signature",
    "provenance/taint ledger": "domain signature",
    "compromise-armed gating": "model-specific patch",
    "verdict cache (retries)": "model-specific patch",
    "content head/tail clip": "model-specific patch",
    "obfuscated-exec ban": "model-specific patch",
}

# Vendored from the HTML source of arxiv.org/html/2609.05903, Table A6.
# "" is a blank cell, which the legend defines as the mechanism being absent.
GRID: dict[str, list[str]] = {
    "NL policy preamble":       ["n", "n", "n", "",  "n", "n", "",  "",  "",  "",  "n", "n", "",  "n", "n"],
    "argument hygiene":         ["d", "d", "d", "d", "",  "d", "d", "d", "",  "d", "",  "",  "",  "",  ""],
    "scope-vs-task judge":      ["s", "s", "s", "",  "",  "",  "s", "s", "",  "s", "",  "",  "",  "s", "s"],
    "content/injection auditor":["",  "",  "",  "",  "",  "s", "",  "",  "",  "",  "s", "",  "",  "",  ""],
    "action-nature gate":       ["s", "d", "s", "s", "d", "",  "",  "",  "",  "",  "",  "",  "",  "",  ""],
    "egress/destination scope": ["",  "d", "",  "",  "d", "d", "d", "",  "d", "d", "",  "",  "",  "",  ""],
    "wash/drain trade ledger":  ["",  "",  "",  "",  "",  "d", "d", "d", "d", "d", "",  "",  "",  "",  ""],
    "trade-parameter scope":    ["",  "",  "",  "",  "",  "d", "",  "",  "d", "",  "",  "",  "",  "",  ""],
    "caller/entity scope gate": ["",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "d", "d", "d", "d", "d"],
    "volume/velocity cap":      ["",  "",  "",  "",  "",  "",  "",  "",  "",  "d", "d", "d", "d", "d", "d"],
    "credential/PII redaction": ["",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "d", "d", "d", "",  ""],
    "provenance/taint ledger":  ["",  "d", "",  "",  "",  "",  "",  "",  "d", "d", "",  "",  "",  "",  "d"],
    "compromise-armed gating":  ["",  "",  "",  "",  "",  "d", "",  "",  "",  "",  "d", "",  "",  "",  ""],
    "verdict cache (retries)":  ["",  "d", "",  "",  "",  "",  "d", "",  "",  "d", "",  "",  "",  "",  ""],
    "content head/tail clip":   ["",  "",  "d", "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  "",  ""],
    "obfuscated-exec ban":      ["",  "",  "",  "",  "d", "",  "",  "",  "",  "",  "",  "",  "",  "",  ""],
}

CAPTION_MARKER = "Mechanism inventory of the fifteen best"


def reparse(path: str) -> dict[str, list[str]]:
    """Re-derive the grid from a local copy of the paper's HTML."""
    source = open(path, encoding="utf-8", errors="replace").read()
    marker = source.find(CAPTION_MARKER)
    if marker < 0:
        raise SystemExit(f"{path}: Table A6 caption not found; is this 2609.05903?")
    start = source.rfind("<table", 0, marker)
    end = source.find("</table>", start)
    table = source[start : end + len("</table>")]

    grid: dict[str, list[str]] = {}
    unknown: list[str] = []
    for row in re.findall(r"<tr.*?</tr>", table, re.S):
        cells: list[str] = []
        for cell in re.finditer(r"<t[hd]\b(.*?)</t[hd]>", row, re.S):
            attrs, _, inner = cell.group(1).partition(">")
            text = html.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
            span = re.search(r'colspan=["\']?(\d+)', attrs)
            cells.extend([text] * (int(span.group(1)) if span else 1))
        if not cells:
            continue
        family, entries = cells[0], cells[1:]
        if len(entries) != len(COLUMNS):
            continue                       # a header or a banner, not a family row
        if family in NON_FAMILY_ROWS:
            continue                       # a header or a banner, named on purpose
        if family not in STRATA:
            # Loud, not silent. This branch used to fall through, so every count
            # this module published was over the families STRATA happened to list
            # rather than over the families the table has: "1 of 16" meant "1 of
            # the sixteen I wrote down". The research seat found it on 2026-11-02
            # by parsing the same bytes with its own parser and getting a
            # different denominator. A row the table has and this dict does not
            # is the one error a silent skip cannot be recovered from, because
            # the number still looks right.
            unknown.append(family)
            continue
        grid[family] = [e if e in ("d", "s", "n") else "" for e in entries]
    if unknown:
        raise SystemExit(
            f"{path}: {len(unknown)} family rows the table carries and STRATA does "
            f"not: {sorted(unknown)}. Every per-family count in this module is a "
            f"fraction of len(STRATA), so an unlisted row silently shrinks the "
            f"denominator rather than being reported.")
    missing = set(STRATA) - set(grid)
    if missing:
        raise SystemExit(f"{path}: {len(missing)} families not parsed: {sorted(missing)}")
    if len(grid) != FAMILY_ROWS:
        raise SystemExit(
            f"{path}: parsed {len(grid)} mechanism families and Table A6 has "
            f"{FAMILY_ROWS}. Every per-family count here is a fraction of this "
            f"number, so it is asserted rather than assumed.")
    return grid


def analyse(grid: dict[str, list[str]]) -> dict:
    """Per-column composition, and the three counts the answer turns on."""
    columns = []
    for i, name in enumerate(COLUMNS):
        marks = [grid[f][i] for f in STRATA if grid[f][i]]
        columns.append(
            {
                "cell": name,
                "domain": name.split("/")[0],
                "model": MODELS[MODEL_KEYS.index(name.split("/")[1])],
                "mechanisms": len(marks),
                "deterministic_code": marks.count("d"),
                "quarantined_judge": marks.count("s"),
                "nl_policy": marks.count("n"),
            }
        )

    no_prose = [c for c in columns if c["nl_policy"] == 0]
    no_judge = [c for c in columns if c["quarantined_judge"] == 0]
    pure_code = [c for c in columns if c["nl_policy"] == 0 and c["quarantined_judge"] == 0]
    all_code = [c for c in columns if c["deterministic_code"] > 0]

    cells_with_prose = sum(c["nl_policy"] for c in columns)
    by_domain: dict[str, int] = {}
    for c in no_prose:
        by_domain[c["domain"]] = by_domain.get(c["domain"], 0) + 1

    # How deployment-dependent is the LABEL itself? A family whose realization
    # differs across the cells it appears in cannot be labelled once in the
    # abstract. A family realized the same way everywhere can.
    varying, fixed = {}, {}
    for family in STRATA:
        kinds = sorted({v for v in grid[family] if v})
        present = [COLUMNS[i] for i, v in enumerate(grid[family]) if v]
        target = varying if len(kinds) > 1 else fixed
        target[family] = {
            "realizations": kinds,
            "cells_present": len(present),
            "by_realization": {
                k: [COLUMNS[i] for i, v in enumerate(grid[family]) if v == k] for k in kinds
            },
        }

    return {
        "paper": "arxiv.org/abs/2609.05903",
        "table": "A6 (Appendix E, Per-Cell Mechanism Inventory)",
        "columns": columns,
        "n_columns": len(columns),
        "cells_carrying_nl_policy": cells_with_prose,
        "harnesses_without_prose": [c["cell"] for c in no_prose],
        "harnesses_without_judge": [c["cell"] for c in no_judge],
        "pure_deterministic_code": [c["cell"] for c in pure_code],
        "harnesses_with_deterministic_code": len(all_code),
        "dropped_prose_by_domain": by_domain,
        "families_total": len(STRATA),
        "families_varying_realization": varying,
        "families_fixed_realization": sorted(fixed),
        "overlap": {
            "without_prose": len(no_prose),
            "without_judge": len(no_judge),
            "both": len(pure_code),
        },
    }


def render(r: dict) -> str:
    out = [
        f"EvoSafeHarness Table A6, re-parsed per column  ({r['paper']})",
        "=" * 64,
        "",
        f"{r['n_columns']} searched harnesses, one per (domain, victim model) cell.",
        "",
        f"{'cell':26} {'mechs':>5} {'code':>5} {'judge':>6} {'prose':>6}",
    ]
    for c in r["columns"]:
        out.append(
            f"{c['cell']:26} {c['mechanisms']:5} {c['deterministic_code']:5} "
            f"{c['quarantined_judge']:6} {c['nl_policy']:6}"
        )
    o = r["overlap"]
    out += [
        "",
        f"cells carrying natural-language policy : {r['cells_carrying_nl_policy']} of {r['n_columns']}",
        f"harnesses shipping NO prose            : {o['without_prose']} of {r['n_columns']}",
        f"harnesses making NO runtime model call : {o['without_judge']} of {r['n_columns']}",
        f"harnesses that are PURE deterministic  : {o['both']} of {r['n_columns']}"
        f"   <- the two sets barely overlap",
        f"harnesses shipping deterministic code  : "
        f"{r['harnesses_with_deterministic_code']} of {r['n_columns']}",
        "",
        "no prose, by domain: "
        + ", ".join(f"{k} {v}" for k, v in sorted(r["dropped_prose_by_domain"].items())),
        "  the dropped-prose cells cluster by DOMAIN, not by model, and the paper",
        "  explains the model axis and never the domain one.",
        "",
        "no prose : " + ", ".join(r["harnesses_without_prose"]),
        "no judge : " + ", ".join(r["harnesses_without_judge"]),
        "pure code: " + ", ".join(r["pure_deterministic_code"]),
        "",
        f"How deployment-dependent is the LABEL? {len(r['families_varying_realization'])} "
        f"of {r['families_total']} mechanism families are realized more than one way:",
    ]
    for family, d in r["families_varying_realization"].items():
        out.append(f"  {family}: {'/'.join(d['realizations'])} across {d['cells_present']} cells")
        for kind, cells in d["by_realization"].items():
            out.append(f"      {kind}: {', '.join(cells)}")
    out += [
        "  Every other family is realized the SAME way wherever it appears, so the",
        "  label is mostly a property of the mechanism and not of the deployment.",
        "  What varies strongly across cells is which mechanisms are PRESENT.",
        "",
        "Why this answers the policy-artifact question NO. A packaged policy",
        "artifact would carry only `n`, the realization this search drops most",
        "often, and the paper's own method section rules out the mirror image too:",
        "\"Optimizing P alone leaves enforcement probabilistic ... Optimizing only a",
        "fixed enforcement program, in contrast, restricts the harness to",
        "predefined security concepts and decision rules.\" Both components are",
        "necessary in its words, so neither prose nor code is the sellable unit",
        "alone. What the table does support is a per-item LABEL, because the",
        "realization of one mechanism family varies across cells.",
    ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", metavar="PATH", help="write the machine-readable bundle")
    ap.add_argument(
        "--reparse",
        metavar="HTML",
        help="re-derive the grid from a local copy of arxiv.org/html/2609.05903 "
        "and fail if it disagrees with the vendored one",
    )
    args = ap.parse_args()

    grid = GRID
    if args.reparse:
        fresh = reparse(args.reparse)
        disagree = {f: (GRID[f], fresh[f]) for f in STRATA if GRID[f] != fresh[f]}
        if disagree:
            for f, (v, n) in disagree.items():
                print(f"DISAGREES {f}\n  vendored {v}\n  parsed   {n}", file=sys.stderr)
            return 1
        print(f"re-parsed {len(fresh)} families from {args.reparse}: identical to vendored",
              file=sys.stderr)
        grid = fresh

    result = analyse(grid)
    print(render(result))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
