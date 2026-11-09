#!/usr/bin/env python3
"""ADR-38 rule 3, measured against the consumer the rule names.

Rule 3 says the builder's checklist sits first, immediately after the opening
paragraph, and that "a consumer who reads the first twenty lines and stops
should have the whole procedure."

A 2026-11-09 run of this seat reported rule 3 as 0 of 10 and named the
provenance block as the cause in all ten, then moved 1,837 words of revision
history out of one skill on that basis. The number was measured from byte zero
of the file, which counts the YAML frontmatter. That is a defensible denominator
for one consumer and the wrong one for the other, and the rule's own words
("immediately after the opening paragraph") describe document structure, which
begins after the frontmatter. Measured from the body, the same library is 10 of
10 within twenty rendered lines.

So this file reports three numbers instead of one, because which consumer you
mean decides the answer:

  from_file     rendered lines from byte zero to the Apply heading. The
                frontmatter dominates it, and the frontmatter is not prose a
                reader reads.
  from_body     rendered lines from the end of the frontmatter to the Apply
                heading. This is the one rule 3's wording picks out.
  whole_procedure
                from the end of the frontmatter to the END of the checklist.
                This is the one rule 3's second sentence picks out, because
                having the whole procedure means having the checklist and not
                merely having reached it.

Rendering is at 100 columns, the same unit `skill_length.py` uses, so the two
instruments are comparable. Like that one, this is wired into no gate: rule 3
names no number of its own beyond "twenty lines", and choosing which of the
three numbers that bound applies to is a charter edit and so the owner's.
"""

from __future__ import annotations

import argparse
import glob
import os
import textwrap

COLUMNS = 100
BOUND = 20  # rule 3's "first twenty lines"


def rendered(lines: list[str]) -> int:
    """Lines a reader sees at COLUMNS columns. A blank line is one line."""
    total = 0
    for line in lines:
        total += len(textwrap.wrap(line, COLUMNS)) or 1
    return total


def split(path: str) -> tuple[list[str], list[str]]:
    lines = open(path, encoding="utf-8").read().split("\n")
    if lines and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)
            return lines[: end + 1], lines[end + 1 :]
        except ValueError:
            pass
    return [], lines


def measure(path: str) -> dict:
    fm, body = split(path)
    try:
        apply_at = next(i for i, l in enumerate(body) if l.startswith("## Apply"))
    except StopIteration:
        return {"skill": os.path.basename(os.path.dirname(path)), "apply": None}
    after = [i for i, l in enumerate(body) if l.startswith("## ") and i > apply_at]
    checklist_end = after[0] if after else len(body)
    return {
        "skill": os.path.basename(os.path.dirname(path)),
        "apply": True,
        "frontmatter": rendered(fm),
        "from_file": rendered(fm) + rendered(body[:apply_at]),
        "from_body": rendered(body[:apply_at]),
        "whole_procedure": rendered(body[:checklist_end]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skills-dir", default="skills")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any skill misses the bound on from_body, "
                         "which is the reading rule 3's wording picks out")
    args = ap.parse_args()

    rows = [measure(p) for p in sorted(glob.glob(os.path.join(args.skills_dir, "*", "SKILL.md")))]
    rows = [r for r in rows if r.get("apply")]
    if not rows:
        print("no skill carries an `## Apply` heading, so rule 3 has nothing to measure")
        return 1

    print(f"ADR-38 rule 3, rendered at {COLUMNS} columns, against its bound of {BOUND} lines\n")
    print(f"{'skill':36} {'from_file':>10} {'from_body':>10} {'whole_proc':>11} {'frontmatter':>12}")
    for r in rows:
        print(f"{r['skill']:36} {r['from_file']:>10} {r['from_body']:>10} "
              f"{r['whole_procedure']:>11} {r['frontmatter']:>12}")

    def report(key: str, what: str) -> int:
        vals = sorted(r[key] for r in rows)
        inside = sum(1 for v in vals if v <= BOUND)
        print(f"\n{what}: {inside} of {len(vals)} within {BOUND}; "
              f"median {vals[len(vals) // 2]}, worst {vals[-1]}")
        return inside

    report("from_file", "from byte zero, frontmatter counted")
    inside_body = report("from_body", "from the body, the reading rule 3's wording picks out")
    report("whole_procedure", "to the END of the checklist, the reading its second sentence picks out")

    print("\nThe three numbers disagree because the frontmatter is most of the first,\n"
          "and the frontmatter is not prose. Which one rule 3's bound applies to is a\n"
          "charter question, so nothing here gates on anything.")

    if args.check and inside_body < len(rows):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
