#!/usr/bin/env python3
"""One answer for "you named something that does not exist".

    python3 tools/resolve_target.py --smoke

The writer seat's measurement of 2026-11-02 is what this file is for. The tools
tree declares 246 arguments, 242 of them carried by a flag, and two sweeps for
the class below covered four of them: one passed a bad command name and one a
bad positional. The class is a flag whose value NAMES something -- a seat, a
skill, a status, a paper -- handed a value nothing carries, and answered with a
confident zero and exit 0 instead of a refusal. Its two recorded instances both
cost real work:

- `INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`
- `INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`

Both of those were repaired in `tools/board.py` with a spelling rule and then a
roster check, and `board.py` now exits `EXIT_UNKNOWN_SEAT = 4` for it. The
number here is deliberately the same number. A reader who learns that 4 means
"the thing you named is not here" on one tool should not have to learn it again
on the next, and the writer's argument for separating "this seat is not here"
from "this seat has no mail" is an argument about every target in the tree
rather than about one seat.

What this does NOT do is guess. A resolver that falls back to a fuzzy match is
how a typo becomes a read of the wrong subject, so `refuse` names the value, the
kind, and the whole roster when the roster is short, and nothing else.

The subset measured on 2026-11-02, after the 242 flags were classified: 102 are
boolean switches with no target to resolve, 7 carry `choices=` and so are
refused by argparse already, 77 take a number or free text, and 56 name
something that could be resolved. Eight of those 56 were probed by hand and
four already refused. The three this module repairs are the three that did not.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: The exit code for "the thing you named is not here", spelled the way
#: `tools/board.py` spells it, because it is the same answer to the same
#: question. Distinct from 0, which has to keep meaning "a clean read of a
#: possibly empty result", and from 1 and 2, which already mean "the check
#: failed" and "the service refused" in this tree.
EXIT_UNKNOWN_TARGET = 4

#: How many names a refusal prints in full before it prints a count instead.
#: Ten skills and nine seats both fit; the ledger's five statuses certainly do.
ROSTER_PRINT_LIMIT = 24


def skill_slugs(root: pathlib.Path | None = None) -> set[str]:
    """Every skill slug on disk, which is every directory under `skills/`.

    `_validation` is the suite contract's own fixtures rather than a skill, and
    `tools/skill_gate.py` already excludes it by name. Excluded here the same
    way rather than by a shape test, so the two agree on what a skill is.
    """
    base = (root or ROOT) / "skills"
    if not base.is_dir():
        return set()
    return {d.name for d in base.iterdir()
            if d.is_dir() and d.name != "_validation"}


def refuse(kind: str, value: str, known, *, hint: str = "") -> str:
    """The sentence a tool prints when the name it was handed resolves to nothing.

    Written once because the two incidents behind this module were both fixed
    by writing it a third time, differently, in one tool.
    """
    names = sorted(n for n in known if n)
    if len(names) <= ROSTER_PRINT_LIMIT:
        roster = ", ".join(names) if names else "nothing at all"
    else:
        roster = f"{len(names)} names, too many to print"
    line = (f"{value!r} is not a {kind} this repository carries. "
            f"What it carries: {roster}.")
    return line + (f" {hint}" if hint else "")


def check(kind: str, value: str, known, *, hint: str = "",
          stream=None) -> int | None:
    """`None` when the name resolves, and the exit code when it does not.

    Returned rather than raised so a caller keeps its own control flow, and
    written to stderr rather than stdout so a `--json` caller's output stays
    parseable while the refusal still reaches a person.
    """
    if not value or value in set(known):
        return None
    print(refuse(kind, value, known, hint=hint),
          file=stream or sys.stderr)
    return EXIT_UNKNOWN_TARGET


def smoke() -> int:
    checks = {}
    known = {"a", "b"}
    checks["a name on the roster resolves"] = check("seat", "a", known) is None
    checks["an empty value is not a refusal, it is no filter"] = (
        check("seat", "", known) is None)
    checks["a name off the roster exits 4"] = (
        check("seat", "zzz", known) == EXIT_UNKNOWN_TARGET)
    said = refuse("seat", "zzz", known)
    checks["the refusal names the value"] = "'zzz'" in said
    checks["the refusal names the roster"] = "a, b" in said
    checks["an empty roster says so rather than printing nothing"] = (
        "nothing at all" in refuse("seat", "zzz", set()))
    checks["a long roster is counted rather than printed"] = (
        "too many to print" in refuse("seat", "zzz",
                                      {str(i) for i in range(50)}))
    checks["the skills on disk are found"] = bool(skill_slugs())
    checks["_validation is not a skill"] = "_validation" not in skill_slugs()
    for label, ok in checks.items():
        print(("ok:   " if ok else "FAIL: ") + label)
    return 0 if all(checks.values()) else 1


def parser() -> argparse.ArgumentParser:
    """The declaration, so this file is inside the flag gate's domain.

    This shipped reading `sys.argv` directly, which worked and put the file
    outside the sweep that classifies every flag in the tree. The writer seat
    found it from that side: its gate has no row for a file that declares no
    parser, so a clean sweep read wider than the sweep actually was. A module
    whose whole subject is refusing an unknown target was the one module the
    target census could not see.

    `--smoke` is a boolean switch. It names nothing, so it belongs to the 102
    the census already excludes, and that is the answer the gate needed rather
    than an exemption.
    """
    ap = argparse.ArgumentParser(
        prog="resolve_target.py",
        description="One answer for \"you named something that does not exist\".")
    ap.add_argument("--smoke", action="store_true",
                    help="run this module's own checks and exit")
    return ap


if __name__ == "__main__":
    args = parser().parse_args()
    if args.smoke:
        sys.exit(smoke())
    print(__doc__.strip())
