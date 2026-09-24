#!/usr/bin/env python3
"""Are the shared registers still well formed after everyone appended to them?

    python3 tools/check_registers.py

Every seat appends to the same handful of files: the ideas ledger, the incident
register, the ban list, the decision record. The charters already warn that two
seats appending at one anchor conflict on the second merge (incident 6), and the
warning is aimed at the seat about to append. Nothing was aimed at the file
afterwards, so a merge resolved badly leaves damage that no one is looking for.

This run found a bare `=======` sitting in docs/agents/incidents.md on main,
between the last line of incident 32 and a renumbering note. That is the middle
marker of a conflict whose outer two markers were cleaned up and whose middle
one was not. It had been read by every seat that opened the file since.

Exit 0 and print nothing when the registers are clean, so this can sit in front
of an `&&` without being noticed. Runtime-changes.md's own closing rule is that
a gate belongs in a command rather than in a charter line, and a register check
is worth exactly as much as the number of commands that run it.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REGISTERS = [
    "docs/ideas.md",
    "docs/decisions.md",
    "docs/agents/incidents.md",
    "docs/agents/registers.md",
    "docs/agents/runtime-changes.md",
    "docs/voice/ban-list.md",
    "docs/voice/taste.md",
    "docs/standards/lessons.md",
]

#: Git writes each marker as exactly seven characters at the start of a line.
#: A markdown setext underline is a run of `=` too, which is why the length is
#: pinned rather than matched loosely: `===` under a heading is not damage.
CONFLICT = re.compile(r"^(<{7}|={7}|>{7})(\s|$)")

#: `INC-YYYY-MM-DD-slug`, the scheme incident 29 replaced the counter with.
INCIDENT_SLUG = re.compile(r"^#{2,3}\s+(INC-\d{4}-\d{2}-\d{2}-[a-z0-9-]+)", re.M)

#: The ledger's own entry contract, docs/ideas.md.
LEDGER_STATUS = re.compile(r"^-\s+Status:\s*(\w+)", re.M)
VALID_STATUSES = {"proposed", "accepted", "rejected", "built", "urgent"}


def conflict_markers(path: Path, root: Path = ROOT) -> list[str]:
    """Merge damage left in a file, which is the loudest thing this can find."""
    out = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if CONFLICT.match(line):
            out.append(f"{path.relative_to(root)}:{n}: merge conflict marker left in place: {line!r}")
    return out


def duplicate_incident_ids(path: Path, root: Path = ROOT) -> list[str]:
    """Two seats allocating one id is the collision the date scheme was meant to end."""
    seen, out = {}, []
    for match in INCIDENT_SLUG.finditer(path.read_text()):
        slug = match.group(1)
        line = path.read_text()[: match.start()].count("\n") + 1
        if slug in seen:
            out.append(f"{path.relative_to(root)}:{line}: incident id {slug} already used at line {seen[slug]}")
        else:
            seen[slug] = line
    return out


def unknown_ledger_statuses(path: Path, root: Path = ROOT) -> list[str]:
    """A status outside the contract is usually a typo, and it hides the entry."""
    out = []
    text = path.read_text()
    for match in LEDGER_STATUS.finditer(text):
        status = match.group(1)
        if status not in VALID_STATUSES:
            line = text[: match.start()].count("\n") + 1
            out.append(f"{path.relative_to(root)}:{line}: status {status!r} is not one of {sorted(VALID_STATUSES)}")
    return out


def check(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """Return (blocking, warnings).

    The split is deliberate and narrow. Merge damage blocks, because it is
    damage to the file itself and whoever left it can always remove it. A
    status outside the ledger contract only warns, because the entry belongs
    to another seat and no charter lets this one rewrite it. Two classes is
    the most this tool gets: incident 32 is what happens when a gate has a
    warning tier wide enough to put real failures in.
    """
    blocking, warnings = [], []
    for name in REGISTERS:
        path = root / name
        if not path.exists():
            blocking.append(f"{name}: register named in tools/check_registers.py does not exist")
            continue
        blocking += conflict_markers(path, root)
    incidents = root / "docs/agents/incidents.md"
    if incidents.exists():
        blocking += duplicate_incident_ids(incidents, root)
    ledger = root / "docs/ideas.md"
    if ledger.exists():
        warnings += unknown_ledger_statuses(ledger, root)
    return blocking, warnings


def main() -> int:
    blocking, warnings = check()
    for finding in warnings:
        print(f"warning: {finding}", file=sys.stderr)
    for finding in blocking:
        print(f"BLOCKING: {finding}", file=sys.stderr)
    if blocking:
        print(f"\n{len(blocking)} blocking, {len(warnings)} warning(s). "
              f"The registers are damaged and every seat reads them.", file=sys.stderr)
        return 1
    if warnings:
        print(f"\n0 blocking, {len(warnings)} warning(s).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
