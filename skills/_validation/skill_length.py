#!/usr/bin/env python3
"""ADR-38 rule 4, measured in a unit the content cannot inflate.

Rule 4 caps a skill at 120 lines "counted with `wc -l` including frontmatter".
The rule was not wrong when it was written and it is not being broken on
purpose. It stopped measuring because the files changed shape underneath it.

On 2026-09-30, commit `0610e2ba` ("cwe and harness-engineering: reflow to 88
columns, both under the 120-line bar") left `context-window-engineering`
hard-wrapped: 120 lines to `wc -l`, 1,316 words, 145 rendered lines at 100
columns. In that shape the metric was a fair proxy, because a paragraph cost
as many lines as it took to read.

Every SKILL.md was later unwrapped to one paragraph per physical line. A
paragraph is now one line however long it is, and the longest single line in
the library is 5,597 characters, about 56 lines on a 100-column terminal and
one line to `wc -l`. Prose appended to an existing paragraph became free.

What followed is measurable. Of the seven skills whose ADR-38 retrofit commit
is nameable, five were revised after their retrofit and all five grew in
words: +26, +53, +95, +99 and +121 percent. The two that did not grow are the
two that were never revised again. Every one of them reported 119 lines or
fewer against the 120-line cap the entire time, so the gate has never once
caught a regrowth, because it cannot.

`context-window-engineering` is the case that settles it. It reads 89 lines
today against 117 at the reflow, a 24 percent reduction by the governing
metric, while its word count went from 1,318 to 3,513. The metric says it got
shorter by a quarter. It got 2.7 times longer to read.

This script reports all three units side by side. It takes no position on what
the cap should be, because changing rule 4 is a charter edit and this seat does
not make those. What it removes is the ability to pass the rule without
knowing.

**And it splits the count in two, added 2026-11-09, because the first run that
read this instrument's output found the interesting half was not the prose.**
Rule 4 counts "including frontmatter" and the frontmatter is where ADR-37 puts
the revision record, one narrative entry per maintenance run, growing forever by
design. On the day the split was added, `harness-engineering`, the gold specimen
this library's whole quality bar was measured on, read 104 rendered lines of
body against 123 of frontmatter: its metadata was larger than its advice and
larger than the entire cap. Its five `provenance.revisions` entries were 8,651
of the file's 17,602 characters, and three of those entries record, in their own
words, cutting reader-facing advice to make room for a revision entry.

So the two halves are reported apart, because the remedy differs. A long body is
prose a seat can cut. A long frontmatter is a record the law requires, and
cutting advice to pay for it is the gate doing harm rather than work. The
smallest frontmatter in the library plus the shortest body already exceed 120,
which means a cap on the sum cannot be met by any skill the format contract
permits, and `--check` says so in its own output.

    python3 skills/_validation/skill_length.py              # the table
    python3 skills/_validation/skill_length.py --check      # exit 1 on a regression
    python3 skills/_validation/skill_length.py --since-retrofit

`--check` fails a skill whose rendered length exceeds `RENDERED_CAP`, which is
the cap rule 4 names applied to the unit rule 4 meant. It is deliberately not
wired into any gate: the gate is the owner's to set.
"""

import argparse
import pathlib
import subprocess
import sys

COLUMNS = 100
RENDERED_CAP = 120
SKILLS = pathlib.Path(__file__).resolve().parents[1]


def rendered_lines(text: str, columns: int = COLUMNS) -> int:
    """Physical lines after soft-wrapping at `columns`, which is what a reader pays."""
    return sum(max(1, -(-len(line) // columns)) for line in text.splitlines())


def split_frontmatter(text: str) -> tuple[str, str]:
    """The YAML block and the body, by the second `---` line.

    Rule 4 counts the frontmatter and that is the half nobody was looking at,
    so every measurement here reports the two separately. `tools/` has its own
    splitter; this one is deliberately standalone, because an instrument that
    cannot run without importing the code it audits is harder to trust.
    """
    lines = text.splitlines(keepends=True)
    fences = [i for i, line in enumerate(lines) if line.rstrip("\n") == "---"]
    if len(fences) < 2:
        return "", text
    end = fences[1]
    return "".join(lines[:end + 1]), "".join(lines[end + 1:])


def measure(text: str) -> dict:
    lines = text.splitlines()
    front, body = split_frontmatter(text)
    return {
        "wc_l": len(lines),
        "words": len(text.split()),
        "chars": len(text),
        "longest": max((len(line) for line in lines), default=0),
        "rendered": rendered_lines(text),
        "front_rendered": rendered_lines(front),
        "body_rendered": rendered_lines(body),
    }


def skill_files() -> list[pathlib.Path]:
    return sorted(SKILLS.glob("*/SKILL.md"))


def retrofit_commit(path: pathlib.Path) -> str | None:
    """The oldest commit whose subject names the ADR-38 retrofit, if there is one."""
    log = subprocess.run(
        ["git", "log", "--format=%h %s", "--follow", "--", str(path)],
        capture_output=True, text=True,
    ).stdout.splitlines()
    hits = [line.split()[0] for line in log
            if "etrofit" in line or "ADR-38" in line]
    return hits[-1] if hits else None


def at_commit(rev: str, path: pathlib.Path) -> str | None:
    # `resolve()` first: every caller inside this file passes an absolute path
    # from `skill_files()`, and the first caller from outside it passed a
    # relative one and got ValueError out of `relative_to` instead of a
    # measurement (2026-11-09).
    rel = path.resolve().relative_to(SKILLS.parent)
    out = subprocess.run(["git", "show", f"{rev}:{rel}"],
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def table() -> None:
    print(f"{'skill':36s} {'wc -l':>6s} {'words':>6s} {'longest':>8s} "
          f"{'front':>6s} {'body':>5s} {'rendered':>9s}  rule 4")
    for path in skill_files():
        m = measure(path.read_text())
        verdict = "ok" if m["rendered"] <= RENDERED_CAP else \
                  f"over by {m['rendered'] - RENDERED_CAP}"
        print(f"{path.parent.name:36s} {m['wc_l']:6d} {m['words']:6d} "
              f"{m['longest']:8d} {m['front_rendered']:6d} "
              f"{m['body_rendered']:5d} {m['rendered']:9d}  {verdict}")
    print(f"\n`front` and `body` are the two halves of `rendered`. They are "
          f"reported apart because the\nremedies are different: a long body is "
          f"prose a seat can cut, and a long frontmatter is\nprovenance ADR-37 "
          f"requires to grow on every maintenance run.")


def since_retrofit() -> None:
    print("word count at the ADR-38 retrofit against today, for every skill "
          "whose retrofit commit is nameable\n")
    print(f"{'skill':36s} {'commit':>9s} {'then':>16s} {'now':>16s}  change")
    print(f"{'':36s} {'':9s} {'lines/words':>16s} {'lines/words':>16s}")
    for path in skill_files():
        rev = retrofit_commit(path)
        if rev is None:
            print(f"{path.parent.name:36s} {'-':>9s}   "
                  "no commit names the retrofit")
            continue
        then_text = at_commit(rev, path)
        if then_text is None:
            continue
        then, now = measure(then_text), measure(path.read_text())
        if then["words"] == 0:
            continue
        pct = 100 * (now["words"] - then["words"]) / then["words"]
        print(f"{path.parent.name:36s} {rev:>9s} "
              f"{then['wc_l']:6d}/{then['words']:<9d} "
              f"{now['wc_l']:6d}/{now['words']:<9d}  {pct:+6.0f}%")


def check() -> int:
    findings, body_only_pass = [], 0
    for path in skill_files():
        m = measure(path.read_text())
        if m["body_rendered"] <= RENDERED_CAP:
            body_only_pass += 1
        if m["rendered"] > RENDERED_CAP:
            half = ("the frontmatter alone is over the whole cap"
                    if m["front_rendered"] > RENDERED_CAP else
                    "the body alone is over the whole cap"
                    if m["body_rendered"] > RENDERED_CAP else
                    "neither half is over the cap alone and the sum is")
            findings.append(
                f"finding: {path.parent.name}: {m['wc_l']} lines to `wc -l` and "
                f"{m['rendered']} rendered at {COLUMNS} columns, against rule 4's "
                f"cap of {RENDERED_CAP}. Frontmatter {m['front_rendered']}, body "
                f"{m['body_rendered']}, so {half}. Longest single line "
                f"{m['longest']} chars.")
    for line in findings:
        print(line)
    total = len(skill_files())
    print(f"\n{total - len(findings)} of {total} skills are under "
          f"{RENDERED_CAP} rendered lines at {COLUMNS} columns, and "
          f"{body_only_pass} of {total} are under it on the body alone")
    if findings:
        print("rule 4 is measured in `wc -l`, under which every one of these "
              "passes. This exit code is the unit rule 4 meant, not the unit "
              "it names, and changing the rule is the owner's.")
        print(f"\nThe cap read as rendered lines including frontmatter is not "
              f"reachable today, which is\nthe measurement this seat owes the "
              f"owner alongside the unit question. The smallest\nfrontmatter in "
              f"the library is {min(measure(p.read_text())['front_rendered'] for p in skill_files())} "
              f"rendered lines and the shortest body is "
              f"{min(measure(p.read_text())['body_rendered'] for p in skill_files())},"
              f"\nso the shortest skill the format contract permits is already "
              f"over {RENDERED_CAP}. Any cap on\nthe sum is therefore a cap on "
              f"the provenance block first and on the advice second.")
    return 1 if findings else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on any skill over the rendered cap")
    ap.add_argument("--since-retrofit", action="store_true",
                    help="word count at the ADR-38 retrofit against today")
    args = ap.parse_args()
    if args.check:
        return check()
    if args.since_retrofit:
        since_retrofit()
        return 0
    table()
    return 0


if __name__ == "__main__":
    sys.exit(main())
