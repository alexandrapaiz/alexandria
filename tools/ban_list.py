#!/usr/bin/env python3
"""The machine-checkable part of docs/voice/ban-list.md, run against a file.

    python3 tools/ban_list.py skills/harness-engineering/SKILL.md
    python3 tools/ban_list.py --json docs/research/*.md
    python3 tools/ban_list.py --smoke

Written for ADR-37's gate, which requires that "the ban list and the trigger
test pass" before a skill revision may merge with no human in the loop. The ban
list is 60-odd entries of prose judgement and most of them need a reader. Six of
them are a substring away from mechanical, and those six are what this file
checks, by number, so a report says which entry it is quoting and a reader can
tell at a glance what was NOT checked.

    1   the slop lexicon
    4   the hedge stack
    5   empty intensifiers
    6   the fake question opener and the fake dialogue transition
    13  characters outside plain ASCII (the entry is the class, not the three
        examples, per its 2026-09-21 amendment and incident 27)
    39  "not just X, but Y" and its family, where one is checked here

What this does NOT check is everything else: symmetric rhythm, uniform
enthusiasm, a summary that restates the headline, internal vocabulary printed at
the reader. A pass here is a floor, exactly like the trigger test's, and the
report says so in its own last line rather than leaving a reader to assume.

Code is exempt. A fenced block and an inline span are skipped, because `robust`
inside a variable name is not a prose tell, and a skill about harnesses quotes
code constantly.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# Entry 1. The list is the entry's own list. `leverage` is only a tell as a
# verb, so it is matched with an object after it rather than on its own, and
# `landscape` is skipped entirely here: this organization has a
# docs/market/landscape.md and the word is a filename in half the registers.
SLOP = ("delve", "tapestry", "realm", "pivotal", "seamless",
        "unlock", "empower", "supercharge", "game-changer", "game changer",
        "revolutionize", "revolutionise", "in the ever-evolving")
SLOP_VERBS = (r"leverage[sd]?\s+(?:the|this|that|its|our|their|a|an)\b",)

# Entry 4, verbatim from the entry.
HEDGES = ("could potentially", "may possibly", "it's important to note",
          "it is important to note", "it should be noted")

# Entry 5, verbatim from the entry.
INTENSIFIERS = (r"\bvery\b", r"\btruly\b", r"\bincredibly\b", r"\bremarkably\b")

# Entry 6.
FAKE_OPENERS = (r"^\s*what if\b.*\?", r"but here'?s the thing",
                r"^\s*the (?:secret|trick|catch) is this\b")

# Entry 39's family, the one member of it that is a regex.
NOT_JUST = (r"not just\b[^.]{0,60}\bbut\b",)

ENTRIES = {
    1: ("the slop lexicon", [re.escape(w) for w in SLOP] + list(SLOP_VERBS)),
    4: ("the hedge stack", [re.escape(w) for w in HEDGES]),
    5: ("empty intensifiers", list(INTENSIFIERS)),
    6: ("the fake question opener or dialogue transition", list(FAKE_OPENERS)),
    39: ("\"not just X, but Y\"", list(NOT_JUST)),
}

FENCE = re.compile(r"^\s*```")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK_TARGET = re.compile(r"\]\([^)]*\)")


def prose_lines(text: str) -> list[tuple[int, str]]:
    """Every line that is prose: no fenced code, no inline spans, no link urls."""
    out, in_fence = [], False
    for n, raw in enumerate(text.split("\n"), start=1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = LINK_TARGET.sub("]()", INLINE_CODE.sub("``", raw))
        out.append((n, line))
    return out


def non_ascii(text: str, allow: str = "") -> list[dict]:
    """Entry 13. Every character outside plain ASCII, with its line.

    The entry's one exception is a person's or an institution's name as the
    source spells it. `allow` is how a caller passes those through, and a gate
    that needs it should say which name it is allowing and why.
    """
    findings = []
    for n, line in enumerate(text.split("\n"), start=1):
        for char in line:
            if ord(char) < 128 or char in allow:
                continue
            findings.append({"entry": 13, "line": n, "found": char,
                             "why": (f"U+{ord(char):04X} is outside plain "
                                     "ASCII. Entry 13 is the class, not its "
                                     "three examples: the reader's search box "
                                     "and the agent loading the text both match "
                                     "on ASCII, and neither matches on this.")})
    return findings


def check(text: str, allow: str = "") -> list[dict]:
    """Every mechanical finding in this text, with the entry number it quotes."""
    findings = non_ascii(text, allow)
    for n, line in prose_lines(text):
        lowered = line.lower()
        for entry, (label, patterns) in sorted(ENTRIES.items()):
            for pattern in patterns:
                match = re.search(pattern, lowered, re.I)
                if match:
                    findings.append({
                        "entry": entry, "line": n, "found": match.group(0),
                        "why": f"entry {entry}, {label}"})
    return sorted(findings, key=lambda f: (f["line"], f["entry"]))


def render(path: str, findings: list[dict]) -> str:
    if not findings:
        return (f"ok: {path} clears the six mechanical entries of "
                "docs/voice/ban-list.md. The rest of that list needs a reader, "
                "so this is a floor and not a pass on the voice.")
    lines = [f"failing: {path}, {len(findings)} findings against "
             "docs/voice/ban-list.md"]
    for f in findings:
        lines.append(f"  line {f['line']}: {f['found']!r} — {f['why']}")
    return "\n".join(lines)


SMOKE = {
    "a clean paragraph": ("The harness is the scaffold around the model. "
                          "Change it before the weights.", 0),
    "entry 1": ("Let us delve into the tapestry of agent design.", 2),
    "entry 4": ("It is important to note that this could potentially work.", 2),
    "entry 5": ("This is a very robust result.", 1),
    "entry 6": ("But here's the thing: nobody measured it.", 1),
    "entry 13": ("The delta was 28.5 %, an em dash — and a 3× move.", 3),
    "entry 39": ("This is not just a harness, but a loop.", 1),
    "code is exempt": ("```\nvery = leverage the thing\n```\nPlain prose.", 0),
    "an inline span is exempt": ("Call `delve_into(x)` and move on.", 0),
}


def smoke() -> int:
    ok = True
    for label, (text, expected) in SMOKE.items():
        found = check(text)
        got = len(found)
        passed = got == expected
        ok = ok and passed
        print(("ok:   " if passed else "FAIL: ")
              + f"{label}: {got} findings, expected {expected}"
              + ("" if passed else f" ({[f['found'] for f in found]})"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--allow", default="",
                    help="characters entry 13 lets through, for a name the "
                         "source spells that way")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()
    if not args.paths:
        ap.error("a path, or --smoke")

    out, failing = {}, False
    for name in args.paths:
        path = pathlib.Path(name)
        if not path.exists():
            print(f"failing: {name} does not exist")
            failing = True
            continue
        findings = check(path.read_text(), args.allow)
        out[name] = findings
        failing = failing or bool(findings)
        if not args.json:
            print(render(name, findings))
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
