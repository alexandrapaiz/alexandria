#!/usr/bin/env python3
"""Read docs/ideas.md the way its contract says it is shaped, instead of grepping it.

    python3 tools/ledger.py --census
    python3 tools/ledger.py --status accepted
    python3 tools/ledger.py --check
    python3 tools/ledger.py --patch origin/main

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
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# A sibling in `tools/`, which is on `sys.path` both when this file is run as a
# script and when a test inserts `tools/` to import it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import resolve_target                                            # noqa: E402

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

#: How wide a qualifier a field label may carry before the colon.
#:
#: The contract block prints `- What:` and seats write `- What alexandria does
#: better:`, `- What is worth stealing:`, `- Cost to HQ:`, `- First step, if
#: accepted:`. Measured on the live file the day this was written: 163 lines
#: across 98 distinct labels, every one of them a contract field wearing a
#: qualifier, and not one of them a different kind of line. A matcher pinned to
#: the bare label called all 163 absent, so 80 field misses were the parser's
#: and not the file's, fourteen entries were reported incomplete that are not,
#: and the measurement in `tests/test_ledger.py` had been red on `main` for
#: days reporting them.
#:
#: Two bounds keep this from swallowing prose. The field name must end on a
#: word boundary, so `- Costs nothing:` is not a `Cost` field and
#: `- First steps:` is not a `First step` one. And the whole label must fit in
#: the width below with no colon inside it, so a paragraph that happens to open
#: with the word is not read as a label. The widest real label on the file is
#: 75 characters.
FIELD_QUALIFIER_WIDTH = 90

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
    #: Field -> the qualified label it was written under, for the fields
    #: this entry never wrote in the contract's bare form.
    qualified_fields: dict[str, str] = field(default_factory=dict)

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
            "qualified_fields": self.qualified_fields,
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


def field_label(line: str) -> tuple[str, str] | None:
    """The contract field a list item carries, and the label it carried it under.

    Returns `("What", "What alexandria does better")` for a qualified label and
    `("What", "What")` for the bare one, so a caller can tell the two apart.
    `None` for a line that is not a field at all. The first field that matches
    wins and the order is `CONTRACT_FIELDS`, which matters for nothing today
    because no two of the four share a prefix.
    """
    head = re.match(rf"^-\s+([^:\n]{{1,{FIELD_QUALIFIER_WIDTH}}}):", line)
    if head is None:
        return None
    label = head.group(1).strip()
    for name in CONTRACT_FIELDS:
        if re.match(rf"^{re.escape(name)}\b", label, re.I):
            return name, label
    return None


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
        # The first status line is the entry's, and a second one is the
        # `duplicate-status` problem rather than a correction of the first.
        # Both the line and the value come from the same place so a warning
        # cannot quote one entry's wording at another entry's line number.
        status_line = found[0][0] + 1 if found else None
        status_raw = found[0][1] if found else None
        decoys = [
            n + 1
            for n in range(start, end)
            if n + 1 not in {f[0] + 1 for f in found} and DECOY.search(lines[n])
        ]
        body = lines[start:end]
        labelled: dict[str, str] = {}
        for line in body:
            found_field = field_label(line)
            if found_field is None:
                continue
            name, label = found_field
            # The bare label wins over a qualified one, so `qualified` names
            # only the entries that never wrote the plain form.
            if name not in labelled or label.lower() == name.lower():
                labelled[name] = label
        missing = [name for name in CONTRACT_FIELDS if name not in labelled]
        qualified = {
            name: label
            for name, label in labelled.items()
            if label.lower() != name.lower()
        }
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
                qualified_fields=qualified,
            )
        )
    return entries


def decoy_lines(text: str, entries: list["Entry"]) -> list[int]:
    """Lines reading `Status: <keyword>` anywhere except an entry's status line.

    File-wide rather than per-entry, because a grep is file-wide. The first
    version of this walked each entry's own body and missed the preamble, and
    the test that caught it caught the preamble this run had just written.
    """
    own = {e.status_line for e in entries if e.status_line is not None}
    return [
        n
        for n, line in enumerate(text.splitlines(), 1)
        if n not in own and DECOY.search(line)
    ]


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
        "decoy_lines": decoy_lines(text, entries),
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
    decoys = decoy_lines(text, entries)
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


#: The contract-field count measured on `main` on 2026-11-02, with the parser
#: this file carries today. It is pinned in `tests/test_ledger.py` rather than
#: here because it is a measurement rather than a gate.
#:
#: **It is re-measured against `main`, and that is not the same rule as
#: `BASELINE`'s.** This constant said "it may fall and it may not rise" when it
#: was written, and the two paragraphs below it already explained why it has to
#: rise: it absorbs every seat's history, so a merge that brings in an
#: incomplete entry raises it through no act of the branch that next reads it.
#: Held to the stricter rule, the number is a gate on other seats' backlog
#: wearing a measurement's clothes, and the first branch to meet it pays for a
#: defect it cannot see. So: re-measure on `origin/main`, set it to that, and
#: say in the pull request what the delta was and whose entries moved it. What
#: may never rise is `PATCH_INCOMPLETE`, which is the branch's own appends and
#: has no budget at all. 2026-11-02: 202 to 205, every one of the three from
#: `main` (`origin/main` measures 205 on its own, and this branch's 31 new
#: entries add none).
#:
#: 2026-11-08: 205 to 217, and `main` was red on this for six days because the
#: portfolio spent its provider week in 25 hours and nothing ran to re-measure
#: it. All twelve are the writer seat's entries of 2026-11-02, each short of
#: exactly one field: five have no `What`
#: (the pre-send gate's three laws, the overwritten press row, the carded
#: caller column, the widened reader, the incident inbox's unflagged gate) and
#: seven have no `First step` (refusing a non-seat name, refusing an over-limit
#: message, the bounded fetch for every charter, the refusal module's sentence,
#: `undeployed_commits` blaming the deploy for the clone, the shape formatter's
#: third path, and `ingest` emitting law 8's url). `origin/main` measures 217
#: on its own, and this branch's 3 new entries add none of them.
#:
#: Why it is not the gate. On 2026-11-01 this number was 196 when the engineer
#: branch was cut and 202 ninety minutes later, because six pull requests
#: merged in between and six of their entries were short of the contract. None
#: of the six was the branch's. A ratchet on a whole-file number cannot tell
#: those apart, which is what `patch` below is for: the project number absorbs
#: everybody's history and the patch number has no budget at all.
PROJECT_INCOMPLETE = 217


def ledger_at(ref: str, path: str = "docs/ideas.md") -> str | None:
    """The ledger as of `ref`, or None when the ref is not in this checkout.

    None rather than an exception, because the host clones this repository
    shallow with a single-branch refspec, so `origin/main` resolves on some
    checkouts and not on others, and a caller has to be able to say "skipped"
    instead of failing. `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`
    is the entry for how long that has cost.
    """
    try:
        done = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def patch(base_text: str, head_text: str) -> dict:
    """The entries `head_text` adds, and what the contract says about them.

    Codecov's split, applied to this file: a project status "measures overall
    code coverage across your entire codebase" and a patch status "only
    measures lines adjusted in the pull request". The project number here is a
    backlog of 202 entries nobody in the room wrote, so a ratchet is the only
    shape it can take. The patch number is the author's own appends, so it has
    no budget: an entry this branch adds carries the four contract fields or it
    does not, and no amount of unrelated cleanup elsewhere pays for it.

    Entries are matched on `(date, name)`, which is the pair a heading carries
    and the pair a reader cites. An entry that was edited rather than added is
    therefore not in `added`, which is deliberate: this answers for what the
    branch wrote, and rewriting another seat's entry is a thing no seat may do.
    """
    base = {(e.date, e.name) for e in parse(base_text)}
    added = [e for e in parse(head_text) if (e.date, e.name) not in base]
    return {
        "added": len(added),
        "incomplete": [e.as_dict() for e in added if e.missing_fields],
        "no_status": [e.as_dict() for e in added if not e.readable],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--ledger", default=str(LEDGER))
    parser.add_argument("--census", action="store_true",
                        help="counts by status, and what cannot be counted")
    parser.add_argument("--status", default="",
                        help="the entries carrying one status, read properly")
    parser.add_argument("--check", action="store_true",
                        help="the ratchet: exit 1 when the unreadable count climbs")
    parser.add_argument("--patch", metavar="REF", default="",
                        help="the entries this branch adds on top of REF, and "
                             "whether they meet the contract; strict, no budget")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    text = Path(args.ledger).read_text(encoding="utf-8")
    entries = parse(text)

    if args.status:
        # A status outside the five is a caller's typo, and "0 entries at
        # status 'accpeted'" is the confident zero the writer seat measured on
        # 2026-11-02: the filter is right, the vocabulary is closed, and the
        # answer reads like an empty backlog. The five live in VALID_STATUSES
        # above and the ledger contract owns them, so the refusal prints them.
        refusal = resolve_target.check(
            "ledger status", args.status, VALID_STATUSES,
            hint="`--census` counts every status, including the unreadable ones.")
        if refusal is not None:
            return refusal
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

    if args.patch:
        base_text = ledger_at(args.patch)
        if base_text is None:
            print(f"skipped: {args.patch}:docs/ideas.md is not in this checkout, "
                  f"so there is nothing to diff against", file=sys.stderr)
            return 0
        report = patch(base_text, text)
        if args.json:
            print(json.dumps(report, indent=2))
            return 1 if report["incomplete"] or report["no_status"] else 0
        print(f"{report['added']} entries added on top of {args.patch}.")
        for bad in report["incomplete"]:
            print(f"  docs/ideas.md:{bad['line']}  missing "
                  f"{', '.join(bad['missing_fields'])}  {bad['name']}")
        for bad in report["no_status"]:
            print(f"  docs/ideas.md:{bad['line']}  {bad['problem']}  {bad['name']}")
        if report["incomplete"] or report["no_status"]:
            print(f"\nBLOCKING: {len(report['incomplete'])} of this branch's own "
                  f"entries are short of the contract and "
                  f"{len(report['no_status'])} carry no readable status. There is "
                  f"no baseline to lower here: these are yours.", file=sys.stderr)
            return 1
        print("\nEvery entry this branch adds carries the contract's four fields "
              "and a readable status.", file=sys.stderr)
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
