#!/usr/bin/env python3
"""Read docs/ideas.md the way its contract says it is shaped, instead of grepping it.

    python3 tools/ledger.py --census
    python3 tools/ledger.py --status accepted
    python3 tools/ledger.py --check
    python3 tools/ledger.py --patch origin/main

The ledger's entry contract is printed at the bottom of one charter in this
repository, `prompts/engineer-agent.md`, and nine more name this file as a write
surface and inherit that contract without restating it. This docstring said
"every charter" until 2026-11-09, when the claim was checked for the first time
while an entry was being written about those same charters: `grep -l 'Status:
proposed' prompts/*.md` returns one of twenty. Three different consumers depend
on the contract. The PM grooms
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
import datetime
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


def seat_names() -> tuple[str, ...]:
    """The seats `company.yaml` declares, or empty when it cannot be read.

    Delegated to `tools/board.py`, which has parsed this manifest with the
    standard library since 2026-11-02 and is authoritative only about its own
    company. Empty means no refusal rather than a refusal of everything: this is
    a source of roster names, never a source of absences.
    """
    try:
        import board
        return tuple(sorted(board.manifest_seats("alexandria")))
    except Exception:
        return ()


def _today() -> str:
    """The filing date. A function so a test can pin it without patching time."""
    return datetime.date.today().isoformat()

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
#: third path, and `ingest` emitting law 8's url).
#:
#: Re-measured once more an hour later, at 218, after `origin/main` moved under
#: this branch mid-run: the writer seat's own entry of tonight, the heading
#: ban's remedy, carries no `What`, `First step` or `Cost`. That is the
#: thirteenth and it is worth noting for what it demonstrates rather than for
#: the one it adds. This number moved twice inside a single run of a single
#: seat, both times from other seats' merges, which is exactly the reason the
#: paragraph above holds it to a re-measurement rather than to a ratchet.
#: `origin/main` measures 218 on its own, and this branch's 7 new entries add
#: none of them.
#:
#: 2026-11-09: 218 to 220, and the shape of the move is the same as the two
#: above it. `origin/main` measures 220 on its own at `d26661b6`, and this
#: branch's 4 new entries add none of them. Both are the writer seat's entries
#: of 2026-11-08, arriving in #812 while this branch was open: law 14's fourth
#: count having no instrument, and `selfcheck` excusing every indented line.
#: Each is short of `What` and `First step`. That makes three re-measurements
#: in two days, all three from the same seat's appends, which is a number worth
#: carrying to the Monday retrospective rather than only to this constant: the
#: contract's two prose fields are the ones a fast append drops, and nothing
#: asks for them at the moment of writing.
#:
#: Why it is not the gate. On 2026-11-01 this number was 196 when the engineer
#: branch was cut and 202 ninety minutes later, because six pull requests
#: merged in between and six of their entries were short of the contract. None
#: of the six was the branch's. A ratchet on a whole-file number cannot tell
#: those apart, which is what `patch` below is for: the project number absorbs
#: everybody's history and the patch number has no budget at all.
PROJECT_INCOMPLETE = 220


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


# ---------------------------------------------------------------------------
# The inbox, 2026-11-09.
#
# `docs/standards/lessons.md` L-A18, amended 2026-10-18, named the two
# registers in this repository that still appended at a shared anchor:
#
# > A register the whole company appends to needs this; the two that still do
# > not have it, `docs/agents/incidents.md` and this file, are the same defect
# > waiting.
#
# The incident register stopped waiting on 2026-10-24 and got
# `tools/incidents.py`. The ledger is the other one, and "this file" in that
# quote is HQ's lessons register rather than ours, so the ledger was never
# named by the law at all. It was named by the measurement instead. The skill
# seat's rebase of 2026-11-09 handed this seat a count rather than a
# complaint: `python3 tools/anchor_contention.py --fetch` reads the ledger as
# the highest-contended path on this seat's own surfaces with no inbox beside
# it, and the merge that opened the run which built this conflicted here, at
# this anchor, for the second time in two days.
#
# The shape is `tools/incidents.py`'s and the differences are three.
#
# *The key is the entry's own heading.* `### YYYY-MM-DD - name` needs no
# allocator, for the same reason `INC-YYYY-MM-DD-slug` needs none: uniqueness
# comes from the date and the subject. So a fold is pure movement, never a
# renaming, and a missed fold is harmless rather than silent. `--require-folded`
# is therefore opt-in, on `tools/incidents.py`'s own argument, that a gate able
# to turn `main` red for a bookkeeping step nobody promised to run is a worse
# defect than the one it fixes.
#
# *The inbox can be strict where `--check` cannot.* The ratchet above exists
# because 62 live entries carry an unreadable status and no seat may rewrite
# another seat's triage. An inbox holds only entries written after this landed,
# so it has no backlog to grandfather: an inbox entry owes the contract's four
# fields and a readable status, with no baseline and no budget. That is the
# same strictness `--patch` already applies to a branch's own entries, moved
# one step earlier, to the moment of writing rather than the moment of review.
#
# *A fold carries its own section heading.* The register is organised into
# `## ` run sections and an entry is a `### ` inside one. The incident register
# has no such nesting, so its fold can append at the tail and stop. Appending a
# bare `### ` at this register's tail would file it under whichever seat's run
# section happens to be last, which on the day this was written is another
# seat's, and a register that misattributes an entry to a seat that did not
# write it is worse than one that is hard to merge.
# ---------------------------------------------------------------------------

#: `docs/ideas.md` and `docs/ideas/inbox/`. The pair is named here once; nothing
#: downstream needs a list, because `tools/anchor_contention.py` discovers a
#: register from its inbox's own position (`<path>/inbox/` implies `<path>.md`),
#: so this directory appears in that report the day it exists.
INBOX = ROOT / "docs" / "ideas" / "inbox"
LEDGER_PATH = "docs/ideas.md"
INBOX_PATH = "docs/ideas/inbox"

#: `YYYY-MM-DD-slug.md`, the decisions inbox's filename and the incident
#: inbox's minus its `INC-` prefix. The slug's alphabet is `[a-z0-9-]` and it
#: ends alphanumeric, which keeps a trailing hyphen out of the stem without
#: naming any separator, per the note in `tools/incidents.py` on the two times
#: an enumerated delimiter list broke that register's parse.
INBOX_FILENAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9](?:[a-z0-9-]*[a-z0-9])?)\.md$")

#: A conflict marker, so an inbox file carrying one is refused before it can
#: become ordinary text. `tools/check_registers.py` catches these on the
#: register and nothing was watching the inbox, which is step zero of every
#: charter's ship check applied to the surface this file adds.
CONFLICT = re.compile(r"^(<{7}|={7}|>{7})(\s|$)")

#: The statuses a seat may file something *new* under. The contract's five are
#: the vocabulary of the register; these two are the vocabulary of an arrival.
#: `accepted` and `rejected` are the owner's transitions and `built` is a
#: transition this seat makes on an entry that already exists, so none of the
#: three can be the status of an entry being written for the first time. No
#: other surface in this repository could say that, because no other surface
#: knows which entries are new.
FILEABLE_STATUSES = ("proposed", "urgent")

#: The skeleton's own unfilled placeholder, `<like this>`. Written as a gate
#: because `--inbox-new` emits a file that passes every other predicate below:
#: four fields, a readable status, a parsing heading, and not one word of
#: content. A stub and a finished entry look identical from the outside, and
#: this register already holds entries whose body is a single sentence of
#: intent.
#:
#: Narrow on purpose, an angle-bracketed run of lowercase prose, so a body
#: quoting `<div>` or `<PR#>` is not caught. The first draft of it was still too
#: wide and the live register said so: swept over `docs/ideas.md`, 931 entries,
#: it matched two lines, and both were a template being *quoted* inside
#: backticks rather than a field left unfilled. So a placeholder inside an
#: inline code span is syntax and not a stub, `_uncoded` strips those spans
#: first, and the same sweep then matches nothing. That measurement is pinned in
#: `tests/test_ledger.py`, because the next widening of this pattern should have
#: to move a number rather than an opinion.
PLACEHOLDER = re.compile(r"<[a-z][a-z0-9 ,.'`:;/()\[\]-]{15,}>")

#: An inline code span, non-greedy, single or double backtick.
CODE_SPAN = re.compile(r"``[^`]*``|`[^`]*`")


def _uncoded(line: str) -> str:
    """The line with its inline code spans blanked out, lengths preserved.

    Lengths are preserved so a column number taken from the result still points
    at the right place in the source line.

    A backtick left over after the complete spans are gone opens a span that
    closes on a later line, and the register has one of those: the ship-first
    clause quotes `git log --oneline origin/<the-older-branch> ^HEAD` wrapped
    across two lines. Everything from that backtick to the end of the line is
    inside the span, so it is blanked too. Dropping this half left exactly one
    false positive on the live file, which is how the case was found.
    """
    stripped = CODE_SPAN.sub(lambda m: " " * len(m.group(0)), line)
    tick = stripped.find("`")
    if tick != -1:
        stripped = stripped[:tick] + " " * (len(stripped) - tick)
    return stripped


def inbox_files(inbox: Path = INBOX) -> list[Path]:
    """The inbox, in filename order. `README.md` is documentation, not an entry.

    Everything else is returned, including a file whose name is nothing like a
    filing, because `check_inbox` has a predicate about exactly that and a
    directory listing that quietly skipped the badly named files would make it
    unreachable.
    """
    if not inbox.is_dir():
        return []
    return sorted(p for p in inbox.iterdir() if p.is_file() and p.name != "README.md")


def read_inbox(inbox: Path = INBOX) -> list[tuple[str, str]]:
    return [(p.name, p.read_text(encoding="utf-8")) for p in inbox_files(inbox)]


def _entry_headings(text: str) -> list[tuple[int, str]]:
    """Every top-level `### ` heading in an inbox file, fences excluded.

    A `### ` inside a fenced block is a quoted heading and not a sibling: the
    register already holds one entry whose body quotes the contract block, and
    an inbox entry that does the same must not read as two entries.
    """
    out = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if fenced:
            continue
        if HEADING.match(line):
            out.append((number, line))
    return out


def check_inbox(inbox: list[tuple[str, str]], register_text: str = "") -> list[str]:
    """Every reason an inbox entry is not fit to fold. Empty means fold it.

    Strict by construction and with no baseline, which is the one thing this
    surface has that `--check` does not: see the header note above.
    """
    problems: list[str] = []
    registered = {(e.date, e.name) for e in parse(register_text)} if register_text else set()
    seen: dict[tuple[str, str], str] = {}

    for name, text in inbox:
        where = f"{INBOX_PATH}/{name}"
        match = INBOX_FILENAME.match(name)
        if not match:
            problems.append(
                f"{where}: the filename is not `YYYY-MM-DD-slug.md`, so nothing can "
                f"tell which entry it claims"
            )
            continue
        file_date = match.group(1)

        markers = [n for n, line in enumerate(text.splitlines(), start=1)
                   if CONFLICT.match(line)]
        if markers:
            problems.append(
                f"{where}:{markers[0]}: a conflict marker. A committed marker "
                f"conflicts once and is ordinary text forever after"
            )
            continue

        headings = _entry_headings(text)
        if len(headings) != 1:
            problems.append(
                f"{where}: {len(headings)} `### ` headings, and an inbox file holds "
                f"exactly one entry. Per-entry granularity is the whole remedy: two "
                f"entries in one file share a line range again"
            )
            continue

        entries = parse(text)
        if not entries:
            line, heading = headings[0]
            problems.append(
                f"{where}:{line}: the heading does not parse as "
                f"`### YYYY-MM-DD - name`, so every consumer of this register is "
                f"blind to it: {heading.strip()!r}"
            )
            continue
        entry = entries[0]

        if entry.date != file_date:
            problems.append(
                f"{where}:{entry.line}: the heading is dated {entry.date} and the "
                f"filename {file_date}. A reader sorting the inbox and a reader "
                f"sorting the register would disagree about this entry's order"
            )
        if entry.missing_fields:
            problems.append(
                f"{where}:{entry.line}: missing {', '.join(entry.missing_fields)}. "
                f"The contract's four fields, and an arriving entry has no baseline "
                f"to be grandfathered by"
            )
        if entry.problem:
            problems.append(
                f"{where}:{entry.line}: {entry.problem}. An entry whose status no "
                f"filter can read is not rejected by any consumer, it is silently "
                f"absent"
            )
        elif entry.status not in FILEABLE_STATUSES:
            problems.append(
                f"{where}:{entry.line}: status {entry.status!r}. A new filing carries "
                f"{' or '.join(FILEABLE_STATUSES)}; "
                f"{entry.status!r} is a transition on an entry that already exists "
                f"and this one does not yet"
            )

        stubs = [n for n, line in enumerate(text.splitlines(), start=1)
                 if PLACEHOLDER.search(_uncoded(line))]
        if stubs:
            problems.append(
                f"{where}:{stubs[0]}: an unfilled `<...>` placeholder from the "
                f"skeleton. Every other check here passes on a file with no content "
                f"in it, so this is the one that tells a stub from an entry"
            )

        key = (entry.date, entry.name)
        if key in seen:
            problems.append(
                f"{where}: the same date and name as {INBOX_PATH}/{seen[key]}, so the "
                f"fold would put two entries in this register under one identifier"
            )
        else:
            seen[key] = name
        if key in registered:
            problems.append(
                f"{where}:{entry.line}: {entry.date} - {entry.name!r} is already in "
                f"{LEDGER_PATH}. Folding it would be a second entry answering to one "
                f"identifier, which is the collision L-A18 is about"
            )
    return problems


def fold_section_heading(date: str) -> str:
    """The `## ` heading a fold opens, and why it is not optional.

    See the third difference in the header note: a bare `### ` appended at this
    register's tail joins whichever run section is last, which attributes one
    seat's entry to another seat's run.
    """
    return f"## Folded from the ledger inbox, {date}"


def fold_text(register_text: str, inbox: list[tuple[str, str]], date: str) -> str:
    """The register with every inbox entry appended under one fold heading.

    Ordered by the entry's own date and then by filename, so the result does not
    depend on directory order and the register stays in filing order.
    """
    if not inbox:
        return register_text
    ordered = sorted(inbox, key=lambda pair: (pair[0][:10], pair[0]))
    out = register_text.rstrip("\n")
    out += "\n\n" + fold_section_heading(date)
    for _, text in ordered:
        out += "\n\n" + text.strip("\n")
    return out + "\n"


def fold_invariant(before: str, inbox: list[tuple[str, str]], after: str,
                   date: str) -> list[str]:
    """Prove the fold moved entries and changed nothing else.

    `tools/incidents.py`'s three claims, plus the heading in the arithmetic.
    Stated rather than asserted, because a fold that silently drops a line is
    the failure a hand-resolved append already made twice in this register.
    """
    failures = []
    if not inbox:
        return failures
    if not after.startswith(before.rstrip("\n")):
        failures.append(
            "the fold did not keep the register it started from as a prefix, so it "
            "rewrote history instead of appending to it"
        )
    for name, text in inbox:
        block = text.strip("\n")
        if block and block not in after:
            failures.append(f"{name}: its body is not present verbatim in the result")

    expected = (
        len(before.rstrip("\n").splitlines())
        + 2
        + sum(len(text.strip("\n").splitlines()) + 1 for _, text in inbox)
    )
    actual = len(after.rstrip("\n").splitlines())
    if actual != expected:
        failures.append(
            f"line arithmetic: expected {expected} lines, got {actual}. Fewer means "
            f"the fold dropped a line, more means it duplicated one"
        )
    if fold_section_heading(date) not in after:
        failures.append(
            "the fold heading is absent, so the entries joined another seat's run "
            "section"
        )
    return failures


SKELETON = """### {date} - {title} ({seat} seat)

- Trigger: <the observation that produced this. A charter requires one: an
  untriggered idea does not count>
- What: <one paragraph, concrete>
- First step: <the first day-sized unit of work>
- Cost: $0
- Status: proposed
"""


def new_entry(slug: str, date: str, seat: str, title: str,
              inbox: Path = INBOX) -> Path:
    """Write a skeleton inbox entry and return its path.

    The format is the enforcement. A convention nothing writes for you is a
    convention every seat reimplements slightly wrong, which is why 51 entries
    in this register carry no status line at all.

    The separator is " - " and not an em dash: `tools/ban_list.py` entry 13
    rejects U+2014 and `ENTRY` above accepts the hyphen, so an em dash here
    would emit a heading the voice gate then fails.
    """
    stem = f"{date}-{slug}"
    if not INBOX_FILENAME.match(f"{stem}.md"):
        raise ValueError(
            f"{stem}.md is not `YYYY-MM-DD-slug.md`: a slug is lowercase "
            f"letters, digits and hyphens, and ends alphanumeric"
        )
    path = inbox / f"{stem}.md"
    if path.exists():
        raise FileExistsError(f"{path} already exists, so this entry is already filed")
    inbox.mkdir(parents=True, exist_ok=True)
    path.write_text(SKELETON.format(date=date, title=title, seat=seat), encoding="utf-8")
    return path


def git(*args: str, root: Path | None = None) -> tuple[int, str]:
    done = subprocess.run(
        ["git", "-C", str(root or ROOT), *args], capture_output=True, text=True
    )
    return done.returncode, done.stdout


def inbox_identities(inbox: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """The `(date, name)` each inbox file claims, read from its own heading.

    Not from the filename. The filename's slug is the author's shorthand and
    the heading is the identifier, so joining on the filename would claim any
    entry that merely shares a date. `tools/incidents.py` can join on the
    filename because there the filename *is* the id; here it is not.
    """
    claimed = set()
    for _, text in inbox:
        for entry in parse(text):
            claimed.add((entry.date, entry.name))
    return claimed


def repo_root_for(path: Path) -> Path:
    """The git root containing `path`, or this repository's own root.

    `branch_appends` runs `git -C <root>` and passes repository-relative
    pathspecs, so the two have to agree about where the root is. Taking it from
    the ledger under test is what lets `--ledger` and `--inbox-dir` point at a
    scratch repository and still mean the same thing they mean here, and the
    first draft of the CLI path skipped every run for want of it.
    """
    code, top = git("rev-parse", "--show-toplevel", root=path.parent)
    return Path(top.strip()) if code == 0 and top.strip() else ROOT


def branch_appends(base: str, inbox: list[tuple[str, str]],
                   root: Path | None = None) -> tuple[list[str], str]:
    """Entries this branch adds to the register that no inbox file claims.

    The one predicate here that reads the branch rather than the files, and
    `tools/incidents.py` carries the same one for the same reason: every other
    check inspects an entry already in the inbox or already in the register, so
    a seat that bypassed the inbox entirely produces a clean read.

    Opt-in through `--base`, because a predicate needing a merge base cannot run
    on a checkout that has none, and it says so rather than passing quiet.

    The fold is exempt, and the exemption keys on the inbox file the diff
    deletes rather than on the branch it runs from, so a fold is a fold wherever
    it happens and an append that only resembles one is not. A folded file's
    identities are read from the merge base, where the file still exists, which
    is the only place they can be read from once the fold has deleted it.

    **One property to know before trusting the number.** On a branch that
    supersedes another, every entry the superseded branch appended reads as
    unclaimed here, because it was appended before this surface existed and the
    merge makes it part of this branch's diff. That is a true answer to the
    question asked and the wrong answer to the question meant, so the caller
    gets the list and decides.
    """
    code, merge_base = git("merge-base", base, "HEAD", root=root)
    if code != 0 or not merge_base.strip():
        return [], (
            f"skipped: no merge base between {base} and HEAD, so this checkout "
            f"cannot say what the branch added"
        )
    merge_base = merge_base.strip()

    code, diff = git("diff", f"{merge_base}...HEAD", "--", LEDGER_PATH, root=root)
    if code != 0:
        return [], f"skipped: git diff against {base} failed"

    added: list[tuple[str, str]] = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        entry = ENTRY.match(line[1:])
        if entry:
            added.append((entry.group(1), entry.group(2)))

    claimed = inbox_identities(inbox)

    code, names = git("diff", "--name-status", f"{merge_base}...HEAD",
                      "--", INBOX_PATH, root=root)
    if code == 0:
        for row in names.splitlines():
            if not row.startswith("D"):
                continue
            path = row.split("\t")[-1]
            shown, body = git("show", f"{merge_base}:{path}", root=root)
            if shown == 0:
                claimed |= inbox_identities([(Path(path).name, body)])

    return [f"{date} - {name}" for date, name in added
            if (date, name) not in claimed], ""


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
    parser.add_argument("--inbox", action="store_true",
                        help="the inbox's entries and every reason one cannot fold")
    parser.add_argument("--inbox-new", metavar="SLUG", default="",
                        help="write a skeleton inbox entry under this slug")
    parser.add_argument("--title", default="",
                        help="the entry name, with --inbox-new")
    parser.add_argument("--seat", default="engineer",
                        help="the seat filing it, with --inbox-new")
    parser.add_argument("--date", default="",
                        help="the filing date, with --inbox-new; today by default")
    parser.add_argument("--fold", action="store_true",
                        help="say what would move from the inbox into the register")
    parser.add_argument("--apply", action="store_true",
                        help="with --fold, move it, and prove nothing was lost")
    parser.add_argument("--require-folded", action="store_true",
                        help="with --check, also fail when the inbox holds anything")
    parser.add_argument("--base", metavar="REF", default="",
                        help="with --check, also fail when this branch appends an "
                             "entry to the register that no inbox file claims")
    parser.add_argument("--inbox-dir", default=str(INBOX),
                        help="the inbox directory; the repository's own by default")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    text = Path(args.ledger).read_text(encoding="utf-8")
    entries = parse(text)
    inbox_dir = Path(args.inbox_dir)

    # `--seat` is a roster flag and `company.yaml` is the roster that needs no
    # network, so a typo refuses by name rather than reaching the register as
    # `(enginer seat)` in a heading no reader will fix. `tools/board.py` already
    # parses that manifest, standard library only, and reading the set off the
    # place that holds it beats restating it: two implementations agree only on
    # the day they are written.
    #
    # Checked here rather than inside `--inbox-new`, which is the only surface
    # that uses the value. A check reachable only through the flag that consumes
    # it is a check `tools/target_census.py --probe` cannot see, and that probe
    # is the thing which decides whether this declaration is honest. It said so:
    # declared `roster` with the check one branch deeper, the probe passed the
    # tool a seat nothing carries and got exit 0.
    known = seat_names()
    if known:
        refusal = resolve_target.check(
            "seat", args.seat, known,
            hint="`company.yaml` is the roster, and it needs no network.")
        if refusal is not None:
            return refusal

    if args.inbox_new:
        date = args.date or _today()
        title = args.title or "<name this entry>"
        try:
            path = new_entry(args.inbox_new, date, args.seat, title, inbox=inbox_dir)
        except (ValueError, FileExistsError) as problem:
            print(f"refused: {problem}", file=sys.stderr)
            return 1
        print(path.relative_to(ROOT))
        print(f"\nWrite the entry there rather than at the register's tail. Nothing "
              f"folds it on your branch: the mainline does, with one author and one "
              f"snapshot.", file=sys.stderr)
        return 0

    if args.inbox:
        pending = read_inbox(inbox_dir)
        problems = check_inbox(pending, text)
        if args.json:
            print(json.dumps({"entries": [n for n, _ in pending],
                              "problems": problems}, indent=2))
            return 1 if problems else 0
        for name, body in pending:
            first = parse(body)
            label = f"{first[0].date}  {first[0].name}" if first else "unparsed"
            print(f"{INBOX_PATH}/{name}  {label}")
        for problem in problems:
            print(f"BLOCKING: {problem}", file=sys.stderr)
        print(f"\n{len(pending)} entr{'y' if len(pending) == 1 else 'ies'} in the "
              f"inbox, {len(problems)} blocking.", file=sys.stderr)
        return 1 if problems else 0

    if args.fold:
        pending = read_inbox(inbox_dir)
        if not pending:
            print("The inbox is empty, so there is nothing to fold.", file=sys.stderr)
            return 0
        problems = check_inbox(pending, text)
        if problems:
            for problem in problems:
                print(f"BLOCKING: {problem}", file=sys.stderr)
            print(f"\nRefused: {len(problems)} problem(s). A fold is pure movement "
                  f"and it will not move an entry the register would then hold "
                  f"badly.", file=sys.stderr)
            return 1
        date = args.date or _today()
        folded = fold_text(text, pending, date)
        failures = fold_invariant(text, pending, folded, date)
        if failures:
            for failure in failures:
                print(f"BLOCKING: {failure}", file=sys.stderr)
            return 1
        moving = [name for name, _ in pending]
        if not args.apply:
            for name in moving:
                print(f"would move {INBOX_PATH}/{name} -> {LEDGER_PATH}")
            print(f"\n{len(moving)} entr{'y' if len(moving) == 1 else 'ies'} would "
                  f"move under {fold_section_heading(date)!r}. The invariant holds: "
                  f"the register is kept as a prefix, every body appears verbatim, "
                  f"and the line arithmetic balances. Re-run with --apply.",
                  file=sys.stderr)
            return 0
        Path(args.ledger).write_text(folded, encoding="utf-8")
        for name in moving:
            (inbox_dir / name).unlink()
            print(f"moved {INBOX_PATH}/{name} -> {LEDGER_PATH}")
        print(f"\n{len(moving)} entr{'y' if len(moving) == 1 else 'ies'} folded "
              f"under {fold_section_heading(date)!r}, invariant proved.",
              file=sys.stderr)
        return 0

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
        pending = read_inbox(inbox_dir)
        # Strict and unbudgeted, which only this surface can afford: the inbox
        # holds nothing older than the day it was built, so there is no backlog
        # to grandfather and no other seat's triage to rewrite.
        blocking = blocking + check_inbox(pending, text)
        if args.require_folded and pending:
            blocking = blocking + [
                f"{len(pending)} entr{'y' if len(pending) == 1 else 'ies'} still in "
                f"{INBOX_PATH}: python3 tools/ledger.py --fold --apply"
            ]
        if args.base:
            unclaimed, skipped = branch_appends(
                args.base, pending,
                root=repo_root_for(Path(args.ledger).resolve()))
            if skipped:
                print(skipped, file=sys.stderr)
            blocking = blocking + [
                f"{LEDGER_PATH}: this branch appends {entry!r} and no inbox file "
                f"claims it. An entry written at the register's tail meets another "
                f"seat's bytes on the second merge; one written in "
                f"{INBOX_PATH}/ never does"
                for entry in unclaimed
            ]
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
