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

**And one predicate reads the branch rather than the files.** Added 2026-10-27,
routed here by the ExO seat, whose charter confines it to charters and the agent
docs. `check --base origin/main` fails when the diff against the merge base adds
a level-two incident heading to the register and no inbox file claims that id.
Every other predicate below inspects an entry that is already in the inbox or
already in the register, so a seat that bypassed the inbox entirely produced a
clean read, which is what seven commits did in the thirty-nine hours after the
inbox landed
(`INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`).
One of them was handed back against a pull request that had already passed
review clean.

The fold is exempt, and the exemption is keyed on the inbox file the diff
deletes rather than on the branch it runs from, so a fold is a fold wherever it
happens and an append that only resembles one is not. `--base` is opt-in for the
reason the paragraph above gives: a predicate that needs a merge base cannot run
on a checkout that has none, and it says so on stderr rather than passing quiet.

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
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "docs" / "agents" / "incidents.md"
INBOX = ROOT / "docs" / "agents" / "incidents" / "inbox"

# The same two paths as repository-relative strings, which is the form `git
# diff` takes and the form a problem line quotes back to a reader.
REGISTER_PATH = "docs/agents/incidents.md"
INBOX_PATH = "docs/agents/incidents/inbox"

# An entry heading is a level-two heading. Level three and deeper are sections
# inside an entry, and the register has 302 of the former and many of the latter.
ENTRY = re.compile(r"^##(?!#)\s+(.*\S)\s*$")

# The id scheme of 2026-09-24 (incident 29). The date is the day the incident was
# observed, which is why the id is not always today's date.
#
# **The boundary is the slug's own alphabet, and not a list of the punctuation
# marks seen so far** (2026-11-08, engineer seat, and the id for it is
# `INC-2026-11-08-the-id-delimiter-list-was-extended-once-and-the-next-separator-broke-it-six-days-later`).
# This used to end on a lookahead naming the characters allowed to follow a
# slug, `(?=$|[\s—–:])`, and `:` was added to that set on 2026-11-02 because the
# register had come to contain one. Six days later a heading separated its id
# from its summary with `, `, the match failed in exactly the same way, and the
# register's own parse gate went red on `main`.
#
# The cost is the same both times and it is not cosmetic. A heading that does
# not match here falls through to `heading_key` keying the entry on its whole
# heading, so a charter citing the id finds nothing and a second filing of the
# same id does not collide with the first, which is the one guarantee the
# `INC-YYYY-MM-DD-slug` scheme makes.
#
# Enumerating delimiters is incident 26's shape, "a gate written as a list
# catches only what already shipped", and this list caught precisely what had
# already shipped, twice running. A slug is `[a-z0-9-]` by construction, so the
# id is simply its longest prefix in that alphabet, and whatever follows is
# prose no matter which mark introduces it. Requiring the slug to *end*
# alphanumeric is what keeps a trailing hyphen out of the id without naming any
# separator at all. Measured over all 331 INC headings on `main`: every one
# parses, and exactly one id moves, which is the one that was failing.
INC_ID = re.compile(r"^(INC-(\d{4})-(\d{2})-(\d{2})-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)")

# A legacy heading keyed by its sequential number, which is what collided.
LEGACY_NUMBER = re.compile(r"^Incident\s+(\d+)\b")

CONFLICT = re.compile(r"^(<{7}|={7}|>{7})(\s|$)")

FENCE = re.compile(r"^\s*(```|~~~)")

INBOX_FILENAME = re.compile(r"^(INC-\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*)\.md$")

#: An inbox file's own id heading, at either level. `#` as well as `##` because
#: three of the files on `main` on 2026-11-02 title themselves at level one and
#: section themselves at level two, which is ordinary Markdown and was never
#: wrong; only this gate's proxy for "one entry per file" said it was.
INBOX_ID_HEADING = re.compile(r"^#{1,2}(?!#)\s+(INC-\S.*\S)\s*$")

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


def git(*args: str, root: Path | None = None) -> tuple[int, str]:
    # `root` resolves at call time rather than binding `ROOT` as a default, so a
    # caller can point the whole predicate at another checkout. A default
    # evaluated at import is a default nothing can override.
    proc = subprocess.run(["git", "-C", str(ROOT if root is None else root), *args],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout


def register_diff(base: str, root: Path | None = None, path: str = REGISTER_PATH) -> tuple[str, str]:
    """The register's diff against the merge base, or a reason it is unreadable.

    `A...B` on purpose, which is the merge base rather than the tip, so a
    branch that is behind `main` is not credited with everything `main` added
    since it forked. The fallback to a two-dot diff is there for the one state
    this repository keeps producing: the host clones `--depth 1`, which implies
    `--single-branch`, so the default branch is grafted with no parents and a
    merge base between two close branches cannot be computed at all
    (`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`).
    """
    code, out = git("diff", f"{base}...HEAD", "--", path, root=root)
    if code == 0:
        return out, ""
    code, out = git("diff", base, "--", path, root=root)
    if code == 0:
        return out, ""
    return "", (f"git could not diff {path} against {base}, so this run says "
                "nothing about what the branch adds to the register")


def added_and_removed_ids(diff: str) -> tuple[set[str], set[str]]:
    """The INC ids whose level-two headings this diff adds, and which it removes.

    Removals matter because a fold is a move. It deletes the inbox file and adds
    the heading, and reading only the additions would make the one legitimate
    append the loudest failure in the file.
    """
    added, removed = set(), set()
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line[:1] not in "+-":
            continue
        entry = ENTRY.match(line[1:])
        if entry is None:
            continue
        match = INC_ID.match(entry.group(1))
        if match is None:
            continue
        (added if line[0] == "+" else removed).add(match.group(1))
    return added, removed


def unclaimed_register_appends(added: set[str], inbox_names: list[str],
                               exempt: set[str] | None = None) -> list[str]:
    """Ids this branch appends to the register that no inbox file claims.

    The predicate the ExO seat routed here, and the measurement behind it: the
    register's append anchor needed a keep-both merge resolve seven times in the
    thirty-nine hours after the inbox landed
    (`INC-2026-10-27-the-register-anchor-conflicted-seven-times-in-two-days-and-its-inbox-has-no-gate`).
    One of those was handed back against a pull request that had already passed
    review clean.

    Every other predicate in `check` inspects an entry that is already in the
    inbox or already in the register, so a seat that ignores the inbox entirely
    passed cleanly, which is exactly what those seven commits did. This is the
    one that reads the thing the seat did rather than the thing it produced.

    Exempt: an id whose inbox file this same diff deletes. That is the fold, and
    it is the one legitimate append. Keying the exemption on the move rather
    than on the branch name means a fold is still a fold wherever it is run, and
    an append that only pretends to be one is not.
    """
    claimed = {match.group(1) for match in
               (INBOX_FILENAME.match(name) for name in inbox_names) if match}
    claimed |= (exempt or set())
    return [
        f"{REGISTER_PATH}: this branch appends {inc_id} straight to the register "
        "and no inbox file claims it. File it with "
        "`python3 tools/incidents.py new --slug ...` instead, so two seats filing "
        "between merges cannot collide on the register's append anchor"
        for inc_id in sorted(added - claimed)
    ]


def folded_ids(base: str, root: Path | None = None) -> set[str]:
    """The ids whose inbox files this branch deletes, which is the fold's shape.

    Read from the inbox directory's own diff rather than from the register's, so
    a heading that was moved and a heading that was typed are told apart by the
    file that stopped existing.
    """
    code, out = git("diff", "--diff-filter=D", "--name-only", f"{base}...HEAD",
                    "--", INBOX_PATH, root=root)
    if code != 0:
        code, out = git("diff", "--diff-filter=D", "--name-only", base,
                        "--", INBOX_PATH, root=root)
    if code != 0:
        return set()
    ids = set()
    for line in out.splitlines():
        match = INBOX_FILENAME.match(line.strip().rsplit("/", 1)[-1])
        if match:
            ids.add(match.group(1))
    return ids


def branch_appends(base: str, inbox_names: list[str], root: Path | None = None) -> tuple[list[str], str]:
    """The routed predicate, run against git. Returns (problems, skipped-reason).

    The reason is returned rather than swallowed because a gate that saw
    nothing must not read as a quiet pass (L-A21, and this file's own closing
    paragraph). On a checkout where the base cannot be resolved this predicate
    has no opinion, and saying so is the honest answer.
    """
    diff, error = register_diff(base, root=root)
    if error:
        return [], error
    added, _ = added_and_removed_ids(diff)
    if not added:
        return [], ""
    return unclaimed_register_appends(
        added, inbox_names, exempt=folded_ids(base, root=root)
    ), ""


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

        # One ENTRY per file is the invariant. Counting level-two headings was
        # the proxy for it, and the proxy was wrong about three files on `main`
        # on 2026-11-02: two were a seat appending a new instance under an
        # `## Instance appended ...` heading, which is precisely what this
        # register's standing rule asks a seat to do when a thing repeats, and
        # the third titles itself at level one and sections itself at level two.
        # So this gate reported a collision for the correct act and for ordinary
        # Markdown, and `tests/test_incidents.py::test_the_live_register_passes
        # _its_own_gate` was red on `main` for all three, which is the class this
        # register itself files as testing a proxy instead of the mechanism.
        #
        # The mechanism is the id. Two entries collide when two headings in one
        # file carry two different INC ids; a section heading and an appended
        # instance carry none, so they cannot collide with anything.
        id_headings = [m.group(1) for m in
                       (INBOX_ID_HEADING.match(line) for line in text.splitlines())
                       if m]
        ids = []
        for heading in id_headings:
            match = INC_ID.match(heading)
            if match and match.group(1) not in ids:
                ids.append(match.group(1))
        if not id_headings:
            problems.append(
                f"{name}: no heading carries an INC id, so the fold has no entry "
                "to move. An inbox file titles itself `# INC-...` or `## INC-...`"
            )
            continue
        if len(ids) > 1:
            problems.append(
                f"{name}: {len(ids)} INC ids in one file ({', '.join(ids)}). One "
                "entry per file is the whole point: two entries in one file "
                "collide again on the next filing"
            )
        heading_id = ids[0] if ids else None
        if heading_id is None:
            problems.append(
                f"{name}: the heading does not start with an INC id: {id_headings[0]!r}"
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


# ---------------------------------------------------------------------------
# The lookup half: has this failure been filed before, and did that entry
# prescribe a remedy?
#
# INC-2026-11-09-the-register-had-the-remedy-and-the-run-that-was-told-to-check-it-still-missed-it:
# every charter carries "check the register before you ship". On 2026-11-09 a
# seat obeyed that step, shipped red anyway, and the remedy was in an entry its
# own seat had written twice. The rule fired and the lookup it implies does not
# exist. `check` asks whether the register is well formed and `fold` moves it;
# neither answers the question a seat actually has in hand, which is a failure
# and not an id.
#
# Two properties of this register make grep the wrong instrument for it, and
# both are measured rather than asserted:
#
#   1. 41% of the entries are not in the register file. 256 of 618 live as
#      one-file-per-entry in `docs/agents/incidents/inbox/`, which is what L-A18
#      asked for and what made the append safe. A seat that reads
#      `docs/agents/incidents.md` and greps it reads 362 entries and misses the
#      other 256, and the remedy missed on 2026-11-09 was in the inbox half.
#   2. The unit of the answer is an entry, not a line. A grep hit on
#      `receipt` returns ninety lines of prose across thirty entries with no
#      entry id, no date and no fix paragraph attached to any of them, so the
#      reader still has to open the file and find the boundaries by hand. That
#      is the step that does not happen under time pressure.
#
# So the scoring is deliberately plain and the output is deliberately not. Terms
# are weighted by inverse document frequency over the entries themselves, which
# means a path like `results/superseded` that appears in two entries dominates a
# word like `register` that appears in four hundred, with no hand-curated
# stopword list to go stale. The ranking is a convenience. The part that repays
# the run is the remedy paragraph printed under each hit, and the verdict saying
# whether there is one.

IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:[./:-][A-Za-z0-9_]+)+|--[a-z][a-z0-9-]*|[a-z_]+_[a-z_0-9]+")
WORD = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")

# An identifier in the query is worth more than a word because it is rarer in
# the world, not only in this corpus: a seat pasting `test_skill_receipts.py`
# knows something a seat pasting `receipts` does not. IDF already rewards rarity
# inside the register, and this rewards the shape independently of it, which is
# what separates a precise query from a lucky one.
IDENTIFIER_WEIGHT = 3.0
WORD_WEIGHT = 1.0

# A bold lead-in that introduces what was done about the incident. Taken from
# the register as it is written rather than from the skeleton: `incidents.py new`
# prescribes one of these ("The fix, or why there is not one yet.") and the file
# carries a dozen variants from before the skeleton existed, so matching only
# the skeleton's wording would find 100 entries of 618 and call the rest
# remedyless.
REMEDY_LEADIN = re.compile(
    r"^\*\*("
    r"(?:the\s+)?fix(?:ed)?\b[^*]*"
    r"|what\s+(?:was\s+fixed|this\s+run\s+did|the\s+fix\s+is)[^*]*"
    r"|what\s+shipped[^*]*"
    r"|the\s+remedy[^*]*"
    r"|what\s+changed[^*]*"
    r")\.?\*\*",
    re.IGNORECASE,
)

# A fix section that says there is not one. The register's own skeleton invites
# this ("or why there is not one yet"), so an entry can carry a fix heading and
# prescribe nothing, and a lookup that reported those as remedies would send a
# seat to read a paragraph that tells it to wait.
NO_REMEDY_YET = re.compile(
    r"not\s+one\s+yet|there\s+is\s+(?:no|not)\s+(?:a\s+)?fix|no\s+fix\s+yet"
    r"|nothing\s+is\s+fixed|not\s+fixed(?:\s+here|\s+in\s+this\s+run)?\b"
    r"|owed\s+to|still\s+open|unfixed|none\s+here"
    # The shapes the register actually uses for a remedy it describes and does
    # not apply. All five are from live entries: a seat that cannot write the
    # surface says so in the fix section rather than omitting it, which is
    # correct of the seat and a trap for a reader that counts fix sections.
    r"|rather\s+than\s+(?:built|applied|shipped|fixed|done)"
    r"|offered\s+rather\s+than|proposal\s+rather\s+than"
    r"|filed\s+as\s+(?:an?\s+)?(?:ledger\s+)?(?:proposal|idea|urgent)"
    r"|routed\s+to\s+the\s+\w+\s+seat|not\s+this\s+seat'?s?\b",
    re.IGNORECASE,
)

SEAT_IN_HEADING = re.compile(r"\b([a-z][a-z/-]*)\s+seat\b")


def terms(text: str) -> dict[str, float]:
    """The query's terms and the weight each carries, lowercased and deduped.

    An identifier contributes itself and its parts, because a seat holding
    `tests/test_skill_receipts.py` should match an entry that only ever wrote
    `test_skill_receipts`, and the whole is scored above the parts so that the
    exact string still wins when both are present.
    """
    weights: dict[str, float] = {}
    for match in IDENTIFIER.finditer(text):
        whole = match.group(0).lower().strip("-./:")
        if not whole:
            continue
        weights[whole] = max(weights.get(whole, 0.0), IDENTIFIER_WEIGHT)
        for part in re.split(r"[./:_-]+", whole):
            if len(part) > 2:
                weights[part] = max(weights.get(part, 0.0), WORD_WEIGHT)
    for match in WORD.finditer(text):
        word = match.group(0).lower()
        weights[word] = max(weights.get(word, 0.0), WORD_WEIGHT)
    return weights


def entry_terms(entry: "Entry") -> set[str]:
    """Every term an entry can be matched on, from its heading and its body."""
    text = "\n".join(entry.body)
    found = set()
    for match in IDENTIFIER.finditer(text):
        whole = match.group(0).lower().strip("-./:")
        if not whole:
            continue
        found.add(whole)
        found.update(p for p in re.split(r"[./:_-]+", whole) if len(p) > 2)
    found.update(m.group(0).lower() for m in WORD.finditer(text))
    return found


def all_entries(register_text: str | None = None, inbox: Path = INBOX) -> list["Entry"]:
    """Every entry in both halves of the register, the file and the inbox.

    Both halves, always. The inbox is not a staging area a reader may skip: it
    is where 41% of the entries live and where they stay until somebody runs
    `fold`, which `check` deliberately does not require.
    """
    if register_text is None:
        register_text = REGISTER.read_text() if REGISTER.is_file() else ""
    entries = split_entries(register_text, "register")
    for path in inbox_files(inbox):
        entries.extend(split_entries(path.read_text(), f"inbox/{path.name}"))
    return entries


def remedy_of(entry: "Entry") -> tuple[str, list[str]]:
    """The entry's fix section, as (verdict, lines).

    Verdict is `REMEDY` when the section names something that was done, `OPEN`
    when the section exists and says the fix is owed, and `NONE` when the entry
    has no fix section at all. `NONE` is not a reproach: the oldest entries
    predate the skeleton. It is information, because it is the one verdict that
    tells a seat the register will not answer its second question.
    """
    body = entry.body
    for index, line in enumerate(body):
        if not REMEDY_LEADIN.match(line.strip()):
            continue
        section = [line.rstrip()]
        for following in body[index + 1:]:
            if following.strip().startswith("**") and not section[-1].strip().endswith("**"):
                break
            if ENTRY.match(following):
                break
            section.append(following.rstrip())
        while section and not section[-1].strip():
            section.pop()
        text = "\n".join(section)
        return ("OPEN" if NO_REMEDY_YET.search(text) else "REMEDY"), section
    return "NONE", []


def seat_of(entry: "Entry") -> str | None:
    """The seat the heading credits, when it names one in the usual form."""
    match = SEAT_IN_HEADING.search(entry.heading)
    return match.group(1) if match else None


def prior_art(query: str, entries: list["Entry"] | None = None,
              limit: int = 5, remedies_only: bool = False) -> dict:
    """Rank the register's entries against a failure in hand.

    `query` is whatever the seat has: a pytest line, an assertion message, a
    path, a flag, a sentence. Nothing is required of its shape, which is the
    point, because the shape a failure arrives in is not under the reader's
    control.
    """
    if entries is None:
        entries = all_entries()
    wanted = terms(query)
    indexed = [(entry, entry_terms(entry)) for entry in entries]
    total = len(indexed) or 1
    document_frequency = {
        term: sum(1 for _, found in indexed if term in found) for term in wanted
    }
    # log(N / df) with a floor, so a term in every entry scores zero rather than
    # negative and a term in none is simply absent from the sum.
    idf = {
        term: max(0.0, math.log(total / df))
        for term, df in document_frequency.items() if df
    }
    ceiling = sum(wanted[term] * idf[term] for term in idf) or 1.0
    scored = []
    for entry, found in indexed:
        hits = [term for term in idf if term in found and idf[term] > 0]
        if not hits:
            continue
        score = sum(wanted[term] * idf[term] for term in hits)
        verdict, section = remedy_of(entry)
        if remedies_only and verdict != "REMEDY":
            continue
        scored.append({
            "id": entry.key,
            "heading": entry.heading,
            "where": f"{entry.source}:{entry.line}",
            "date": entry.date,
            "seat": seat_of(entry),
            "confidence": round(score / ceiling, 3),
            "matched": sorted(hits, key=lambda t: -wanted[t] * idf[t])[:8],
            "remedy": verdict,
            "remedy_lines": section,
        })
    scored.sort(key=lambda row: (-row["confidence"], row["id"]))
    # `matched` counts every entry sharing any distinctive term, which on this
    # corpus is nearly all of them, so it is data and never the headline. The
    # number a reader can use is `close`, counted over the whole ranking rather
    # than over the printed slice: a seat that passes --limit 3 still needs to
    # know there are nine close matches behind them.
    close = [row for row in scored if row["confidence"] >= STRONG]
    return {
        "query": query,
        "entries_searched": total,
        "register_entries": sum(1 for e, _ in indexed if e.source == "register"),
        "inbox_entries": sum(1 for e, _ in indexed if e.source != "register"),
        "matched": len(scored),
        "with_remedy": sum(1 for row in scored if row["remedy"] == "REMEDY"),
        "close": len(close),
        "close_with_remedy": sum(1 for row in close if row["remedy"] == "REMEDY"),
        "hits": scored[:limit],
    }


# A hit this strong is worth the reader's attention even when they were sure
# nothing had been filed. Below it the ranking is still useful and the headline
# stops claiming a class, because a lookup that cries repeat at every query
# trains a seat to skip it, which is the failure mode this tool was built to
# answer rather than to reproduce.
STRONG = 0.25


def report_prior(found: dict, seat: str | None = None, stream=sys.stdout) -> int:
    """Print the lookup for a person, and return the count of strong hits."""
    print(
        f"searched {found['entries_searched']} entries "
        f"({found['register_entries']} in docs/agents/incidents.md, "
        f"{found['inbox_entries']} in docs/agents/incidents/inbox/)",
        file=stream,
    )
    if not found["hits"]:
        print("\nnothing in the register matches this. File it as a first instance.", file=stream)
        return 0
    strong = [row for row in found["hits"] if row["confidence"] >= STRONG]
    remedies = [row for row in strong if row["remedy"] == "REMEDY"]
    if found["close"]:
        print(
            f"{found['close']} of them are close matches and "
            f"{found['close_with_remedy']} of those prescribe a remedy.",
            file=stream,
        )
    else:
        print(
            "No close match. Nothing here is more than a shared word, so read the "
            "ranking\nas a weak hint rather than as prior art.",
            file=stream,
        )
    print(f"\nThe closest {len(found['hits'])}:", file=stream)
    for row in found["hits"]:
        mine = " YOUR OWN SEAT" if seat and row["seat"] == seat else ""
        print(f"\n  [{row['confidence']:.3f}] {row['remedy']}{mine}  {row['where']}", file=stream)
        print(f"  {row['id']}", file=stream)
        print(f"  matched on: {', '.join(row['matched'])}", file=stream)
        if row["remedy_lines"]:
            for line in row["remedy_lines"]:
                print(f"    | {line}", file=stream)
        else:
            print("    | (no fix section: this entry records the failure and no remedy)", file=stream)
    if strong:
        subject = "one of these is a close match" if len(strong) == 1 else \
            f"{len(strong)} of these are close matches"
        print(
            f"\n{subject[0].upper()}{subject[1:]}. The standing rule at the top of the "
            f"register\nsays a repeat is recorded the moment it repeats, so if this is one of "
            f"them,\nfile it in this pull request.",
            file=stream,
        )
    if remedies:
        print(
            f"\n{len(remedies)} close match(es) already prescribe a remedy. Read it before you "
            f"write a\nnew one: a remedy that exists and goes unread is how this lookup came "
            f"to be built.",
            file=stream,
        )
    own = [row for row in strong if seat and row["seat"] == seat]
    if own:
        verb = "was" if len(own) == 1 else "were"
        print(
            f"\n{len(own)} of the close matches {verb} filed by your own seat. A seat's own "
            f"prior entry is\nthe one it is most likely to have written and least likely to go "
            f"looking for.",
            file=stream,
        )
    return len(strong)


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
    checker.add_argument(
        "--base",
        default=None,
        help="a ref to read this branch's own appends against, normally "
             "origin/main. Without it the register and the inbox are checked "
             "for shape and nothing is said about what the branch adds",
    )

    maker = sub.add_parser("new", help="write a skeleton entry into the inbox")
    maker.add_argument("--slug", required=True, help="the subject half of the id")
    maker.add_argument("--date", required=True, help="the day the incident was observed")
    maker.add_argument("--seat", default="engineer", help="the seat filing it")
    maker.add_argument("--title", default="<one line>", help="the heading's own summary")
    maker.add_argument(
        "--no-prior", action="store_true",
        help="skip the prior-art lookup this otherwise runs on the slug and title",
    )

    asker = sub.add_parser(
        "prior", help="has this failure been filed before, and was a remedy prescribed?"
    )
    asker.add_argument(
        "query", nargs="*",
        help="the failure in hand: a test name, an assertion, a path, a flag, a sentence",
    )
    asker.add_argument(
        "--file", default=None, metavar="PATH",
        help="read the query from a file instead, so a pytest log can be the query",
    )
    asker.add_argument("--limit", type=int, default=5, help="how many hits to print (default 5)")
    asker.add_argument(
        "--seat", default=None,
        help="your seat, so a prior entry your own seat filed is called out as yours",
    )
    asker.add_argument(
        "--remedies-only", action="store_true",
        help="rank only entries that prescribe a remedy",
    )
    asker.add_argument("--json", action="store_true", help="the ranking as data")

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
        skipped = ""
        if args.base:
            appends, skipped = branch_appends(args.base, [name for name, _ in inbox])
            problems.extend(appends)
        entries = split_entries(register_text)
        if skipped:
            # Printed on stderr whichever way the gate goes, because the one
            # outcome this file refuses is a predicate that saw nothing and
            # read as a pass.
            print(f"note: {skipped}", file=sys.stderr)
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

    if args.command == "prior":
        query = " ".join(args.query)
        if args.file:
            try:
                query = f"{query}\n{Path(args.file).read_text()}".strip()
            except OSError as exc:
                print(f"cannot read the query from {args.file}: {exc}")
                return 2
        if not query.strip():
            print("nothing to look up: pass the failure as words, or --file a log")
            return 2
        found = prior_art(
            query,
            all_entries(register_text, INBOX),
            limit=args.limit,
            remedies_only=args.remedies_only,
        )
        if args.json:
            print(json.dumps(found, indent=2, sort_keys=True))
            return 0
        report_prior(found, seat=args.seat)
        # Always zero. This answers a question; it does not hold a pull
        # request. A lookup that can fail a run is a lookup a seat stops
        # running, and an unrun lookup is the defect it was built for.
        return 0

    if args.command == "new":
        try:
            path = new_entry(args.slug, args.date, args.seat, args.title)
        except FileExistsError as exc:
            print(exc)
            return 1
        print(path.relative_to(ROOT))
        if not args.no_prior:
            # The repeat question, asked where the standing rule applies rather
            # than where a charter remembers to tell a seat to ask it. Filing is
            # the one moment every seat passes through, and it is the moment the
            # seat has the failure in hand and the register still unread.
            print()
            found = prior_art(
                f"{args.slug.replace('-', ' ')} {args.title}",
                all_entries(register_text, INBOX),
                limit=3,
            )
            report_prior(found, seat=args.seat)
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
