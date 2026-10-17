#!/usr/bin/env python3
"""Read docs/ideas.md the way its contract says it is shaped, instead of grepping it.

    python3 tools/ledger.py --census
    python3 tools/ledger.py --status accepted
    python3 tools/ledger.py --check

The ledger's entry contract is printed at the bottom of every charter in this
repository, and three different consumers depend on it. The PM grooms
`accepted` entries into sprints. The engineer's fallback order looks for
`accepted` entries no sprint has picked up. Every seat scans for `urgent`. All
three do it with grep, and the ledger entry of 2026-09-24, "A ledger entry can
hide from every consumer by writing its status as a sentence", is about what
that costs: an entry whose status line is prose is not rejected by any of them,
it is silently absent, which is the failure mode that leaves no trace.

That entry asked for the status rule to move "from warning to blocking in one
edit" once the count reached zero. The count has not reached zero and the
count was never the whole number. `tools/check_registers.py` reports the
status problems it can see by walking the status lines it finds, so an entry
with no status line at all is invisible to the checker for exactly the same
reason it is invisible to the consumers. This file walks the entries instead.

What that changes, measured on the live file the day this was written: the
checker reported 6 problems and there are 62. Fifty-one entries carry no
status line, five carry an empty one, six carry a word outside the vocabulary.
Thirty of the fifty-one are scan notes, which may not owe a status at all, and
that leaves twenty-one proposals that do and are invisible without one.

The failure runs in both directions, which is the part no entry had named.
`grep "Status: accepted" docs/ideas.md`, the command the 2026-09-24 entry
quotes as its own first observation step, returns eleven hits on this file and
two of them are prose: one inside that very entry, quoting the command, and
one in a chair's note reading "Status: accepted by the chair on the owner's
word". So a seat that greps for its own work gets nine real entries, two
inventions, and no warning about the fifty-one it cannot see. This run was
misled by it before it wrote a line of this file.

Hence two surfaces rather than one. `--status` answers the question the
consumers are actually asking, and prints how many entries it could not read a
status from, because a filter that cannot say what it skipped is the defect.
`--check` is the gate, and it ratchets: `BASELINE` below is the count measured
today and the check fails when the number climbs. A ratchet is the only
enforceable shape here, because the fix for a bad status is a judgement about
what its author meant, the statuses belong to the owner, and no seat may
rewrite another seat's triage state. Blocking on today's number would block
every seat on a backlog none of them made. Blocking on tomorrow's addition
stops the backlog growing, which is the thing a command can actually do.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "ideas.md"

#: The five the contract names. Kept in one place so the checker and this file
#: cannot drift apart; `tools/check_registers.py` imports it from here.
VALID_STATUSES = ("proposed", "accepted", "rejected", "built", "urgent")

#: An entry opens with a date and a name. The separator is an em dash in every
#: entry written so far and a hyphen is accepted too, because the contract
#: block in the charters is the authority on the shape and it does not pin the
#: character, so a hyphen is a typo rather than a different kind of line.
ENTRY = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})\s*[—–-]\s*(.+?)\s*$")

#: A `## ` section heading closes the entry above it. The file is organised
#: into them ("Proposals", "Security agent findings", one per run) and an entry
#: never spans one.
SECTION = re.compile(r"^##\s+\S")

#: The status line, as a list item, which is how the contract writes it. The
#: value is captured raw and whole: the point of this file is to see a status
#: that was written as a sentence, so the pattern must match the sentence.
STATUS_LINE = re.compile(r"^-\s+Status:\s*(.*?)\s*$")

#: `Status: <one of the five>` anywhere other than an entry's own status line.
#: These are what make a grep over-count, so they are counted even though they
#: are not damage to the entry carrying them.
DECOY = re.compile(r"Status:\s*(" + "|".join(VALID_STATUSES) + r")\b", re.I)

#: The four fields besides the status that the contract asks for.
CONTRACT_FIELDS = ("Trigger", "What", "First step", "Cost")

#: A craft or competitive scan note. The charter asks for one of these every
#: run alongside the day's ideas, and a note is not a proposal, so whether it
#: owes a status is a real question rather than a lapse. It is reported
#: separately for exactly that reason: 30 of the 51 entries with no status are
#: scan notes, every one of them written before the convention settled, and
#: every scan note appended since 2026-10-15 carries `proposed`. Exempting
#: them is the owner's call and the ledger entry for it is filed. Until she
#: rules, they count, because an entry the contract covers and the file does
#: not is the whole defect this file is about.
SCAN_NAME = re.compile(r"^(craft|competitive)\s+scan\b", re.I)

#: Any `### ` heading at all, dated or not. An entry whose heading carries no
#: date is invisible to `ENTRY`, so it is invisible to this file's parser for
#: the same reason it is invisible to a grep, and it does not appear in the
#: unreadable-status count either, because there is no entry there to count.
#: Four sit on the live file. A fifth is legitimate: a `### ` heading inside a
#: dated entry's body is sub-structure rather than a sibling, and one entry
#: uses it that way, so the two are told apart by what encloses them rather
#: than by how the heading reads.
HEADING = re.compile(r"^###\s+(.+?)\s*$")


@dataclass
class Entry:
    """One `### YYYY-MM-DD — name` block and what its status line says."""

    line: int
    date: str
    name: str
    status: str | None
    status_raw: str | None
    status_line: int | None
    extra_status_lines: list[int] = field(default_factory=list)
    decoys: list[int] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    @property
    def readable(self) -> bool:
        """Can a consumer filtering by status see this entry at all?"""
        return self.status in VALID_STATUSES and not self.extra_status_lines

    @property
    def problem(self) -> str | None:
        """The one word for why a filter cannot read this entry, or None."""
        if self.extra_status_lines:
            return "duplicate-status"
        if self.status_line is None:
            return "no-status"
        if not self.status_raw:
            return "empty-status"
        if self.status not in VALID_STATUSES:
            return "unknown-status"
        return None

    def as_dict(self) -> dict:
        return {
            "line": self.line,
            "date": self.date,
            "name": self.name,
            "status": self.status,
            "status_raw": self.status_raw,
            "status_line": self.status_line,
            "problem": self.problem,
            "decoys": self.decoys,
            "missing_fields": self.missing_fields,
        }


def _first_word(raw: str) -> str:
    """The status keyword at the head of a status line, however it was dressed.

    `- Status: proposed  (filed 2026-09-20 as urgent; carried here)` is a
    `proposed` entry with a note after it, and four entries are written that
    way. `- Status: mostly moot as of run 3` is not a status at all. Both are
    the first word with its punctuation and emphasis stripped, which is why
    this is a function rather than a split.
    """
    words = raw.split()
    if not words:
        return ""
    return words[0].strip("`*_.,;:()[]").lower()


def parse(text: str) -> list[Entry]:
    """Every dated entry in the ledger, in file order."""
    lines = text.splitlines()
    opens = [n for n, line in enumerate(lines) if ENTRY.match(line)]
    entries: list[Entry] = []
    for index, start in enumerate(opens):
        end = len(lines)
        for n in range(start + 1, len(lines)):
            if ENTRY.match(lines[n]) or SECTION.match(lines[n]):
                end = n
                break
        head = ENTRY.match(lines[start])
        assert head is not None
        found = [
            (n, match.group(1))
            for n in range(start + 1, end)
            for match in [STATUS_LINE.match(lines[n])]
            if match
        ]
        status_line = found[0][0] + 1 if found else None
        status_raw = found[-1][1] if found else None
        decoys = [
            n + 1
            for n in range(start, end)
            if n + 1 not in {f[0] + 1 for f in found} and DECOY.search(lines[n])
        ]
        body = lines[start:end]
        missing = [
            name
            for name in CONTRACT_FIELDS
            if not any(re.match(rf"^-\s+{re.escape(name)}:", line) for line in body)
        ]
        entries.append(
            Entry(
                line=start + 1,
                date=head.group(1),
                name=head.group(2),
                status=_first_word(status_raw) if status_raw is not None else None,
                status_raw=status_raw,
                status_line=status_line,
                extra_status_lines=[f[0] + 1 for f in found[1:]],
                decoys=decoys,
                missing_fields=missing,
            )
        )
    return entries


def undated_headings(text: str) -> list[tuple[int, str]]:
    """`### ` headings that sit where an entry belongs and carry no date.

    Returned as (line, heading). A heading nested inside a dated entry's body
    is left out, because that is sub-structure and the ledger uses it that
    way once on purpose.
    """
    lines = text.splitlines()
    out = []
    for n, line in enumerate(lines):
        if not HEADING.match(line) or ENTRY.match(line):
            continue
        enclosed = False
        for j in range(n - 1, -1, -1):
            if ENTRY.match(lines[j]):
                enclosed = True
                break
            if SECTION.match(lines[j]):
                break
        if not enclosed:
            out.append((n + 1, HEADING.match(line).group(1)))
    return out


def read(path: Path = LEDGER) -> list[Entry]:
    return parse(path.read_text(encoding="utf-8"))


def by_status(entries: list[Entry], status: str) -> list[Entry]:
    """The entries a consumer asking for one status should actually get."""
    wanted = status.strip().lower()
    return [e for e in entries if e.readable and e.status == wanted]


def unreadable(entries: list[Entry]) -> list[Entry]:
    """Entries no status filter can see, which is the whole point of the file."""
    return [e for e in entries if e.problem is not None]


def census(entries: list[Entry], text: str = "") -> dict:
    counts: dict[str, int] = {}
    for entry in entries:
        if entry.readable:
            counts[entry.status] = counts.get(entry.status, 0) + 1
    problems: dict[str, int] = {}
    for entry in unreadable(entries):
        problems[entry.problem] = problems.get(entry.problem, 0) + 1
    blind = unreadable(entries)
    return {
        "entries": len(entries),
        "readable": sum(1 for e in entries if e.readable),
        "by_status": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
        "problems": dict(sorted(problems.items(), key=lambda kv: -kv[1])),
        "unreadable": len(blind),
        "unreadable_scan_notes": sum(1 for e in blind if SCAN_NAME.match(e.name)),
        "undated_headings": [{"line": n, "heading": h} for n, h in undated_headings(text)],
        "decoy_lines": sorted(n for e in entries for n in e.decoys),
    }


#: The count measured on main on 2026-10-17, which is what the gate ratchets
#: against. It may fall and it may not rise. Lowering it is a one-line edit and
#: belongs in the same pull request as the entries that were fixed, which is
#: the idiom `tools/feed_health.py` and `tests/test_ci_coverage.py` both use.
#:
#: 51 no-status, 5 empty-status, 6 unknown-status, 0 duplicate-status.
BASELINE = 62

#: Five lines of prose that read `Status: <keyword>` without being a status.
#: Same rule: may fall, may not rise.
BASELINE_DECOYS = 5

#: Four `### ` headings sitting where an entry belongs with no date on them.
#: Same rule again.
BASELINE_UNDATED = 4


def check(entries: list[Entry], text: str = "") -> tuple[list[str], list[str]]:
    """Return (blocking, warnings).

    Blocking is the ratchet and nothing else. Every individual bad entry is a
    warning, because fixing one is a judgement about what its author meant and
    the statuses belong to the owner.
    """
    blocking: list[str] = []
    warnings: list[str] = []
    broken = unreadable(entries)
    decoys = [n for e in entries for n in e.decoys]
    undated = undated_headings(text)

    for entry in broken:
        where = entry.status_line or entry.line
        detail = f"{entry.problem}"
        if entry.status_raw:
            detail += f" ({entry.status_raw[:50]!r})"
        warnings.append(
            f"docs/ideas.md:{where}: {detail}: "
            f"{entry.date} {entry.name[:60]!r} is invisible to every status filter"
        )
    for n, heading in undated:
        warnings.append(
            f"docs/ideas.md:{n}: heading with no date where an entry belongs: "
            f"{heading[:60]!r}. Nothing that reads this file as entries can see it."
        )
    for n in sorted(decoys):
        warnings.append(
            f"docs/ideas.md:{n}: prose reading 'Status: <keyword>' outside a status line, "
            f"which makes a grep over-count"
        )

    if len(broken) > BASELINE:
        blocking.append(
            f"docs/ideas.md: {len(broken)} entries carry no readable status, "
            f"up from the recorded {BASELINE}. A new entry was appended without one. "
            f"Give it a status from {list(VALID_STATUSES)}, or lower BASELINE in "
            f"tools/ledger.py in the same pull request that fixes the old ones."
        )
    if len(undated) > BASELINE_UNDATED:
        blocking.append(
            f"docs/ideas.md: {len(undated)} headings carry no date where an entry "
            f"belongs, up from the recorded {BASELINE_UNDATED}. The contract's shape "
            f"is `### YYYY-MM-DD — name` and nothing that parses this file as "
            f"entries can see a heading without one."
        )
    if len(decoys) > BASELINE_DECOYS:
        blocking.append(
            f"docs/ideas.md: {len(decoys)} lines of prose read 'Status: <keyword>' "
            f"without being a status line, up from the recorded {BASELINE_DECOYS}. "
            f"Rewrite the new one so a grep cannot mistake it for a verdict."
        )
    return blocking, warnings


def render_census(data: dict) -> str:
    out = [
        f"{data['entries']} dated entries in docs/ideas.md, "
        f"{data['readable']} with a status a filter can read"
    ]
    for status, count in data["by_status"].items():
        out.append(f"  {status:<10} {count}")
    if data["problems"]:
        out.append("")
        out.append(f"{data['unreadable']} entries no status filter can see:")
        for problem, count in data["problems"].items():
            out.append(f"  {problem:<18} {count}")
        out.append(
            f"  of which scan notes: {data['unreadable_scan_notes']} "
            f"(a note is not a proposal, so an exemption is the owner's call)"
        )
    if data.get("undated_headings"):
        out.append("")
        out.append(
            f"{len(data['undated_headings'])} headings carry no date where an entry "
            f"belongs, so they are not entries to anything that reads this file:"
        )
        for item in data["undated_headings"]:
            out.append(f"  docs/ideas.md:{item['line']}  {item['heading'][:66]}")
    if data["decoy_lines"]:
        out.append("")
        out.append(
            f"{len(data['decoy_lines'])} lines of prose read 'Status: <keyword>' "
            f"without being one, so a grep over-counts by that much: "
            f"{', '.join(str(n) for n in data['decoy_lines'])}"
        )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ledger", default=str(LEDGER))
    parser.add_argument("--census", action="store_true",
                        help="counts by status, and what cannot be counted")
    parser.add_argument("--status", default="",
                        help="the entries carrying one status, read properly")
    parser.add_argument("--check", action="store_true",
                        help="the ratchet: exit 1 when the unreadable count climbs")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    text = Path(args.ledger).read_text(encoding="utf-8")
    entries = parse(text)

    if args.status:
        picked = by_status(entries, args.status)
        blind = unreadable(entries)
        if args.json:
            print(json.dumps([e.as_dict() for e in picked], indent=2))
        else:
            for entry in picked:
                print(f"docs/ideas.md:{entry.line}  {entry.date}  {entry.name}")
            sys.stdout.flush()
            print(f"\n{len(picked)} entries at status {args.status!r}.", file=sys.stderr)
            if blind:
                print(
                    f"{len(blind)} further entries carry no readable status and may "
                    f"belong here: python3 tools/ledger.py --census",
                    file=sys.stderr,
                )
        return 0

    if args.check:
        blocking, warnings = check(entries, text)
        for finding in warnings:
            print(f"warning: {finding}", file=sys.stderr)
        for finding in blocking:
            print(f"BLOCKING: {finding}", file=sys.stderr)
        if blocking:
            return 1
        if warnings:
            print(f"\n0 blocking, {len(warnings)} warning(s), "
                  f"at or under the recorded baseline.", file=sys.stderr)
        return 0

    data = census(entries, text)
    print(json.dumps(data, indent=2) if args.json else render_census(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
