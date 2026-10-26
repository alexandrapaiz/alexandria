#!/usr/bin/env python3
"""The incident register's append surface, so two seats filing at once cannot collide.

    python3 tools/incidents.py check            # are the register and the inbox well formed?
    python3 tools/incidents.py new --slug ...   # write a skeleton entry into the inbox
    python3 tools/incidents.py fold             # say what would move into the register
    python3 tools/incidents.py fold --apply     # move it, and prove nothing was lost

`docs/standards/lessons.md` L-A18, amended 2026-10-18, names this file's problem
and names its fix, and it names them by path:

> A register the whole company appends to needs this; the two that still do not
> have it, `docs/agents/incidents.md` and this file, are the same defect
> waiting.

"This" is the inbox HQ built for the decisions register: one file per entry,
`YYYY-MM-DD-slug.md`, written by the seat, folded into the register on the
mainline where there is one author and one snapshot. The defect it removes is
positional rather than semantic. Every seat appends at the same anchor, the end
of the file, so two seats filing between merges conflict on the second merge no
matter how correct both entries are.

The waiting ended today. Merging #462 into #475 conflicted here, at that anchor.
Four of the PM seat's nine sibling branches conflicted on the same shape in
`docs/sprints/pending.md`
(`INC-2026-10-24-nine-of-the-pm-seats-own-prs-forked-the-same-anchor-and-none-contained-any-other`).
The register's own count of the anchor stands at fifteen occurrences
(`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`).

Two tools already stand downstream of the collision and neither prevents it.
`tools/check_registers.py` finds a conflict marker that reached `main`.
`tools/resolve_register_conflict.py` resolves a conflict mechanically and proves
the resolution lost nothing. Both are repairs. An entry written into the inbox
never meets another seat's bytes, so there is nothing to repair.

**What this does not need.** The decisions inbox exists partly to issue numbers,
because an ADR's identifier is a count and a count cannot be allocated without
coordination. This register stopped allocating counts on 2026-09-24: its ids are
`INC-YYYY-MM-DD-slug`, whose uniqueness comes from the date and the subject, so
folding is pure movement and never renaming. That makes the fold safe to run at
any time by anyone, and it makes a missed fold harmless rather than silent,
which is why `check` does not require an empty inbox unless asked with
`--require-folded`. A gate that can turn `main` red for a bookkeeping step nobody
promised to run is a worse defect than the one being fixed.

**The baselines are the honest half.** Nine legacy numbers in this register
answer to more than one entry and twelve entries are excess copies, all from the
sequential allocator L-A18 retired. L-A18 says identifiers already issued are
permanent, so those are recorded as a baseline rather than reported as failures.
A new collision moves the count and is loud. Exit 2 when the register cannot be
read at all, because a gate that saw nothing must not read as a quiet pass
(L-A21).
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "agents" / "incidents.md"
INBOX = ROOT / "docs" / "agents" / "incidents" / "inbox"

# An entry heading is a level-two heading. Level three and deeper are sections
# inside an entry, and the register has 302 of the former and many of the latter.
ENTRY = re.compile(r"^##(?!#)\s+(.*\S)\s*$")

# The id scheme of 2026-09-24 (incident 29). The date is the day the incident was
# observed, which is why the id is not always today's date.
INC_ID = re.compile(r"^(INC-(\d{4})-(\d{2})-(\d{2})-[a-z0-9][a-z0-9-]*?)(?=$|[\s—–])")

# A legacy heading keyed by its sequential number, which is what collided.
LEGACY_NUMBER = re.compile(r"^Incident\s+(\d+)\b")

CONFLICT = re.compile(r"^(<{7}|={7}|>{7})(\s|$)")

FENCE = re.compile(r"^\s*(```|~~~)")

INBOX_FILENAME = re.compile(r"^(INC-\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*)\.md$")

# Measured on the register at the commit that added this file. Nine legacy
# numbers answer to more than one entry and twelve entries are the excess
# copies, all of them from the sequential allocator L-A18 retired on
# 2026-09-24. The register's own header admits one of the nine ("Two entries
# numbered 22 remain"), which is itself the argument for a measured baseline
# over a remembered one.
#
# This is a set and not a count, and the first draft of this file made it a
# count. A count cannot see a substitution: repair one legacy duplicate, let a
# new number collide, and `9 == 9` reports nothing. That is incident 26's shape
# in this register, "a gate written as a list catches only what already
# shipped", and its own test caught it here before this shipped.
BASELINE_DUPLICATE_LEGACY: dict[str, int] = {
    "Incident 22": 2,
    "Incident 24": 3,
    "Incident 25": 3,
    "Incident 26": 3,
    "Incident 27": 2,
    "Incident 28": 2,
    "Incident 29": 2,
    "Incident 30": 2,
    "Incident 31": 2,
}
BASELINE_EXCESS_LEGACY_ENTRIES = sum(n - 1 for n in BASELINE_DUPLICATE_LEGACY.values())


class Entry:
    """One level-two entry of the register, or one inbox file."""

    def __init__(self, key: str, heading: str, line: int, body: list[str], source: str):
        self.key = key
        self.heading = heading
        self.line = line
        self.body = body
        self.source = source

    @property
    def inc_id(self) -> str | None:
        return self.key if self.key.startswith("INC-") else None

    @property
    def date(self) -> str | None:
        """The id's own date, which is what the fold sorts by."""
        match = INC_ID.match(self.heading)
        return "-".join(match.group(2, 3, 4)) if match else None

    def __repr__(self) -> str:
        return f"Entry({self.key!r} at {self.source}:{self.line})"


def heading_key(heading: str) -> str:
    """The identifier a charter would cite this entry by.

    Three shapes, because the register has carried three. `INC-` ids key
    themselves. A legacy `Incident N` keys on the number, because the number is
    what two branches allocated twice. Anything else keys on its whole heading,
    which is unique by construction for the dated narrative sections.
    """
    inc = INC_ID.match(heading)
    if inc:
        return inc.group(1)
    legacy = LEGACY_NUMBER.match(heading)
    if legacy:
        return f"Incident {legacy.group(1)}"
    return heading


def split_entries(text: str, source: str = "register") -> list[Entry]:
    """Every level-two entry, ignoring headings inside fenced code blocks."""
    entries: list[Entry] = []
    fenced = False
    current: Entry | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            fenced = not fenced
            if current is not None:
                current.body.append(line)
            continue
        match = None if fenced else ENTRY.match(line)
        if match:
            heading = match.group(1)
            current = Entry(heading_key(heading), heading, number, [line], source)
            entries.append(current)
        elif current is not None:
            current.body.append(line)
    return entries


def conflict_lines(text: str) -> list[int]:
    """Conflict markers, which `tools/check_registers.py` also looks for.

    Repeated here rather than imported because this tool runs on inbox files that
    the other one does not know about, and a marker in an inbox file would be
    folded into the register verbatim.
    """
    return [n for n, line in enumerate(text.splitlines(), start=1) if CONFLICT.match(line)]


def inbox_files(inbox: Path = INBOX) -> list[Path]:
    """The inbox, in filename order. `README.md` is documentation, not an entry."""
    if not inbox.is_dir():
        return []
    return sorted(p for p in inbox.iterdir() if p.is_file() and p.name != "README.md")


def legacy_census(entries: list[Entry]) -> dict:
    """How many legacy keys answer to more than one entry, and how many copies."""
    legacy = [e.key for e in entries if not e.key.startswith("INC-")]
    counts = collections.Counter(legacy)
    duplicated = {key: n for key, n in counts.items() if n > 1}
    return {
        "keys": len(duplicated),
        "excess": sum(n - 1 for n in duplicated.values()),
        "detail": duplicated,
    }


def check(register_text: str, inbox: list[tuple[str, str]], require_folded: bool = False):
    """Problems in the register and the inbox. Returns a list of strings.

    `inbox` is a list of `(filename, text)` so this is testable without a disk.
    """
    problems: list[str] = []
    entries = split_entries(register_text, "docs/agents/incidents.md")

    for number in conflict_lines(register_text):
        problems.append(
            f"docs/agents/incidents.md:{number}: a conflict marker reached the register"
        )

    # New INC ids must be unique. Legacy numbers are permanent per L-A18, so they
    # are compared against a measured baseline instead.
    inc_counts = collections.Counter(e.key for e in entries if e.key.startswith("INC-"))
    for key, count in sorted(inc_counts.items()):
        if count > 1:
            where = ", ".join(str(e.line) for e in entries if e.key == key)
            problems.append(
                f"docs/agents/incidents.md: {key} appears {count} times (lines {where}): "
                "two entries answering to one id"
            )

    # Legacy numbers are compared key by key against the measured baseline, so a
    # number that collides for the first time is loud even if another one was
    # repaired in the same change and the total did not move.
    for key, count in sorted(legacy_census(entries)["detail"].items()):
        allowed = BASELINE_DUPLICATE_LEGACY.get(key, 1)
        if count > allowed:
            problems.append(
                f"docs/agents/incidents.md: {key!r} answers to {count} entries and the "
                f"baseline records {allowed}: a sequential id was allocated again"
            )

    known = set(inc_counts)
    seen: dict[str, str] = {}
    for name, text in inbox:
        filename_match = INBOX_FILENAME.match(name)
        if not filename_match:
            problems.append(
                f"{name}: an inbox filename must be INC-YYYY-MM-DD-slug.md, so the "
                "file the fold moves and the id a charter cites are the same string"
            )
            continue
        from_name = filename_match.group(1)

        for number in conflict_lines(text):
            problems.append(f"{name}:{number}: a conflict marker in an inbox entry")

        found = split_entries(text, name)
        if not found:
            problems.append(
                f"{name}: no level-two heading, so the fold has no entry to move. "
                "An inbox file starts with `## INC-...`"
            )
            continue
        if len(found) > 1:
            problems.append(
                f"{name}: {len(found)} level-two headings. One entry per file is the "
                "whole point: two entries in one file collide again on the next filing"
            )
        heading_id = found[0].inc_id
        if heading_id is None:
            problems.append(
                f"{name}: the heading does not start with an INC id: {found[0].heading!r}"
            )
        elif heading_id != from_name:
            problems.append(
                f"{name}: the filename says {from_name} and the heading says "
                f"{heading_id}. A reader who greps the id finds one and not the other"
            )
        if from_name in known:
            problems.append(
                f"{name}: {from_name} is already in the register, so the fold would "
                "file it twice"
            )
        if from_name in seen:
            problems.append(
                f"{name}: {from_name} is also filed by {seen[from_name]}"
            )
        else:
            seen[from_name] = name

    if require_folded and inbox:
        problems.append(
            f"the inbox still holds {len(inbox)} entries: run "
            "`python3 tools/incidents.py fold --apply` on the mainline"
        )
    return problems


def fold_text(register_text: str, inbox: list[tuple[str, str]]) -> str:
    """The register with every inbox entry appended, oldest observation first.

    Sorted by the id's own date and then by filename, so the register stays in
    roughly observation order and the result does not depend on directory order.
    """
    ordered = sorted(inbox, key=lambda pair: (pair[0][4:14], pair[0]))
    out = register_text.rstrip("\n")
    for _, text in ordered:
        out += "\n\n" + text.strip("\n")
    return out + "\n"


def fold_invariant(before: str, inbox: list[tuple[str, str]], after: str) -> list[str]:
    """Prove the fold moved entries and changed nothing else.

    The same discipline `tools/resolve_register_conflict.py` applies to a merge
    resolution: state the arithmetic so the claim is testable rather than
    asserted. Three claims, and a fold that breaks any of them is refused.
    """
    failures = []
    if not after.startswith(before.rstrip("\n")):
        failures.append(
            "the fold did not keep the register it started from as a prefix, so it "
            "rewrote history instead of appending to it"
        )
    for name, text in inbox:
        block = text.strip("\n")
        if block and block not in after:
            failures.append(f"{name}: its body is not present verbatim in the result")

    expected = len(before.rstrip("\n").splitlines()) + sum(
        len(text.strip("\n").splitlines()) + 1 for _, text in inbox
    )
    actual = len(after.rstrip("\n").splitlines())
    if actual != expected:
        failures.append(
            f"line arithmetic: expected {expected} lines, got {actual}. Fewer means "
            "the fold dropped a line, more means it duplicated one"
        )
    return failures


# The separator is " - " rather than an em dash, because tools/ban_list.py
# entry 13 rejects U+2014 and INC_ID's lookahead accepts a plain space, so
# the em dash made `new` emit a heading that the voice gate then failed.
SKELETON = """## {inc_id} - {title} ({date}, {seat} seat)

**What happened.** <one paragraph, concrete, with the evidence that makes it
checkable by someone who was not here>

**Why it is in this register.** <the standing rule says any issue occurring more
than once is recorded the moment it repeats, so name the earlier occurrences and
say how many there now are>

**What it cost.** <the measurable half: turns, hours, runs, lines>

**The fix, or why there is not one yet.** <what changed, or what is owed and to
whom>
"""


def new_entry(slug: str, date: str, seat: str, title: str, inbox: Path = INBOX) -> Path:
    """Write a skeleton inbox entry and return its path.

    This exists because the format is the enforcement. Two seats found the board's
    message endpoint by probing it with curl six days apart, and a convention
    nothing writes for you is a convention every seat reimplements slightly wrong.
    """
    inc_id = f"INC-{date}-{slug}"
    path = inbox / f"{inc_id}.md"
    if path.exists():
        raise FileExistsError(f"{path} already exists, so this id is already filed")
    inbox.mkdir(parents=True, exist_ok=True)
    path.write_text(SKELETON.format(inc_id=inc_id, title=title, date=date, seat=seat))
    return path


def _read_inbox(inbox: Path) -> list[tuple[str, str]]:
    return [(p.name, p.read_text()) for p in inbox_files(inbox)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="The incident register's append surface.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    checker = sub.add_parser("check", help="is the register and its inbox well formed?")
    checker.add_argument(
        "--require-folded",
        action="store_true",
        help="also fail when the inbox is not empty (for a mainline assertion)",
    )

    maker = sub.add_parser("new", help="write a skeleton entry into the inbox")
    maker.add_argument("--slug", required=True, help="the subject half of the id")
    maker.add_argument("--date", required=True, help="the day the incident was observed")
    maker.add_argument("--seat", default="engineer", help="the seat filing it")
    maker.add_argument("--title", default="<one line>", help="the heading's own summary")

    folder = sub.add_parser("fold", help="move the inbox into the register")
    folder.add_argument(
        "--apply", action="store_true", help="write the files, rather than saying what would move"
    )

    args = parser.parse_args(argv)

    if not REGISTER.is_file():
        print(f"{REGISTER} does not exist, so this run says nothing about the register")
        return 2

    register_text = REGISTER.read_text()
    inbox = _read_inbox(INBOX)

    if args.command == "check":
        problems = check(register_text, inbox, require_folded=args.require_folded)
        entries = split_entries(register_text)
        if problems:
            for problem in problems:
                print(problem)
            print(
                f"\n{len(problems)} problem(s). {len(entries)} entries in the register, "
                f"{len(inbox)} waiting in the inbox."
            )
            return 1
        print(
            f"{len(entries)} entries in the register, {len(inbox)} waiting in the inbox, "
            "nothing malformed."
        )
        return 0

    if args.command == "new":
        try:
            path = new_entry(args.slug, args.date, args.seat, args.title)
        except FileExistsError as exc:
            print(exc)
            return 1
        print(path.relative_to(ROOT))
        return 0

    problems = check(register_text, inbox)
    if problems:
        for problem in problems:
            print(problem)
        print("\nrefusing to fold: fix the above first")
        return 1
    if not inbox:
        print("the inbox is empty, so there is nothing to fold")
        return 0

    folded = fold_text(register_text, inbox)
    failures = fold_invariant(register_text, inbox, folded)
    if failures:
        for failure in failures:
            print(failure)
        print("\nrefusing to fold: the result does not pass its own arithmetic")
        return 1

    moved = ", ".join(name for name, _ in inbox)
    if not args.apply:
        print(f"would fold {len(inbox)} entry(ies) into docs/agents/incidents.md: {moved}")
        print("re-run with --apply to write it")
        return 0

    REGISTER.write_text(folded)
    for path in inbox_files(INBOX):
        path.unlink()
    print(f"folded {len(inbox)} entry(ies) into docs/agents/incidents.md: {moved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
