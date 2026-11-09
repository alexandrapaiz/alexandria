#!/usr/bin/env python3
"""Read the kill vocabulary of both surfaces, and check it against the codes
our own standards name — in both directions.

Why this exists, and it is not the reader HQ already shipped. On 2026-11-09
`alexandra-systems/exo-centralizer` shipped a reader that prints each
surface's whole vocabulary with its row count, and this file does not
re-ship it. It adds the two things that reader cannot do, each of which cost
a wrong conclusion the same morning:

1. **It segments by runtime era.** The audit log's `exit` field changed its
   whole encoding when the seats left GitHub Actions on 2026-10-17, and the
   field carries no marker saying so. Before the boundary it holds the
   runner's signal arithmetic (`143` = 128+SIGTERM); after it, the host's own
   words (`timeout`, `clone`). A tally over the whole file returns the union
   of two encodings and reads as one live code space. Two runs reached
   opposite wrong answers from that union on 2026-11-09: this seat's
   amendment paired `timeout` with the board's `124` and presented it to HQ
   as a documented mapping, and HQ's reply refused the mapping as lossy on
   the strength of 28 `143` rows that had not been written for 23 days.

2. **It checks the standards against the surfaces, not just the surfaces.**
   `MACHINERY_EXITS = {124, 137, 143}` is named by `docs/standards/pm.md` as
   the set that wakes HQ's engineer on a killed run. Of its three codes `143`
   was last written 2026-10-17, `137` has **never** been written on either
   surface in either era, and `124` is live only on the board. A vocabulary
   printer shows you what the surfaces say; it cannot tell you that a rule
   is watching for a code nothing emits. That direction is the silent one,
   because a wake that never fires looks exactly like a fleet with no kills.

So the check is two-way and either direction is a finding:
  * a surface writes a value no standard names  -> a kill nothing wakes on
  * a standard names a value no surface writes  -> a rule watching a dead code

Exit 0 clean, 1 findings, 2 a surface could not be read (never 0 on a
surface that failed to answer: an unreadable surface reporting no findings is
the 2026-10-11 defect this org has paid for more than once).

    python3 tools/kill_vocabulary.py              # both surfaces, both directions
    python3 tools/kill_vocabulary.py --json
"""

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import sys

AUDIT = os.environ.get("ASC_AUDIT", "/srv/asc/state/.epito/audit.jsonl")
ROSTER = os.environ.get("ASC_ROSTER", "/srv/asc/roster")

# The day the seats left GitHub Actions for the resident host (HQ decisions
# 054/056). Rows on either side of it are in different encodings and a tally
# that spans it is a tally of two things.
RUNTIME_BOUNDARY = "2026-10-18"

# The codes our own standards name as a thing to wake on, with where they say
# it, so a finding can cite the line rather than the claim.
STANDARD_CODES = {
    "124": "docs/standards/pm.md (machinery wake: exit 124, 137, 143)",
    "137": "docs/standards/pm.md (machinery wake: exit 124, 137, 143)",
    "143": "docs/standards/pm.md (machinery wake: exit 124, 137, 143)",
}

# Values that mean the run finished and had its say. Everything else is a kill
# or a failure and belongs to the vocabulary this file is about.
CLEAN = {"0", "1"}


def era(ts):
    return "actions" if ts[:10] < RUNTIME_BOUNDARY else "host"


def read_audit(path=AUDIT):
    """Every `run.end` row's exit, by era. The whole file, parsed row by row:
    a regex over the lines would be the very blindness this file reports on."""
    if not os.path.exists(path):
        return None, "the audit log is not on this filesystem: %s" % path
    vocab = collections.defaultdict(collections.Counter)
    durations = collections.defaultdict(list)
    rows = 0
    with open(path) as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("action") != "run.end" or "exit" not in row:
                continue
            rows += 1
            value = str(row["exit"])
            vocab[era(row["ts"])][value] += 1
            ms = row.get("durationMs")
            if ms is not None:
                durations[(era(row["ts"]), value)].append(ms / 1000.0)
    return {"rows": rows, "vocab": vocab, "durations": durations}, None


def read_board():
    """Every board run row, asked per seat manifest. The company route caps at
    200 rows and saturates, so it cannot answer this question; the per-seat
    route partitions the same rows small enough to be read whole. Saturation is
    reported rather than swallowed, because a truncated tally cannot prove an
    absence and absence is half of what this file checks."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import board as board_api
    except ImportError as why:
        return None, "tools/board.py will not import (%s)" % why
    seats = sorted(
        (p.split(os.sep)[-3], p.split(os.sep)[-2])
        for p in glob.glob(os.path.join(ROSTER, "*", "*", "agent.toml"))
    )
    if not seats:
        return None, "no seat manifests under %s, so no seat to ask for" % ROSTER
    vocab = collections.defaultdict(collections.Counter)
    durations = collections.defaultdict(list)
    seen, saturated, errors = set(), [], []
    for company, seat in seats:
        try:
            reply = board_api.api(
                "/api/runs?company=%s&seat=%s&days=100000&limit=100000" % (company, seat)
            )
        except Exception as why:                      # noqa: BLE001 - any reach can fail
            errors.append("%s/%s: %s" % (company, seat, why))
            continue
        if reply.get("saturated"):
            saturated.append("%s/%s" % (company, seat))
        for run in reply.get("runs") or []:
            if run.get("id") in seen:
                continue
            seen.add(run.get("id"))
            value = "null" if run.get("exit") is None else str(run["exit"])
            stamp = (run.get("ended_at") or run.get("created_at") or "")[:10]
            vocab[era(stamp) if stamp else "host"][value] += 1
            start, end = run.get("started_at"), run.get("ended_at")
            if start and end:
                try:
                    durations[(era(stamp) if stamp else "host", value)].append(
                        (dt.datetime.fromisoformat(end) - dt.datetime.fromisoformat(start)).total_seconds()
                    )
                except ValueError:
                    pass
    if errors and not seen:
        return None, "no seat answered: %s" % "; ".join(errors[:3])
    return {
        "rows": len(seen), "vocab": vocab, "durations": durations,
        "saturated": saturated, "errors": errors,
        # The route's own ceiling. An absence measured through a window is an
        # absence inside that window and this is where the bound is stated.
        "window_days": 90,
    }, None


def named_in_standards(root="."):
    """The codes the standards actually name today, read off the files rather
    than trusted to the table above, so this check cannot outlive its own
    premise the way the thing it is checking did."""
    found = {}
    for rel in sorted({path for path in STANDARD_CODES.values()}):
        name = rel.split(" ")[0]
        try:
            text = open(os.path.join(root, name)).read()
        except OSError:
            continue
        for match in re.finditer(r"exit (\d+), (\d+),? (?:and )?(\d+)", text):
            for code in match.groups():
                found[code] = name
    return found or {code: src.split(" ")[0] for code, src in STANDARD_CODES.items()}


def span(values):
    if not values:
        return "no durations"
    ordered = sorted(values)
    return "%.0f-%.0f s, median %.0f" % (ordered[0], ordered[-1], ordered[len(ordered) // 2])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="the reading as data")
    parser.add_argument("--root", default=".", help="repository root, for the standards")
    args = parser.parse_args(argv)

    audit, audit_why = read_audit()
    board_rows, board_why = read_board()
    standards = named_in_standards(args.root)

    findings, unreadable = [], []
    for label, surface, why in (("audit log", audit, audit_why), ("board", board_rows, board_why)):
        if surface is None:
            unreadable.append("%s: %s" % (label, why))

    # Direction 1: a kill no standard names.
    live_unnamed = collections.Counter()
    for label, surface in (("audit log", audit), ("board", board_rows)):
        if surface is None:
            continue
        for value, count in surface["vocab"].get("host", {}).items():
            if value in CLEAN or value in standards:
                continue
            live_unnamed[(label, value)] += count
    for (label, value), count in sorted(live_unnamed.items(), key=lambda item: -item[1]):
        findings.append(
            "the %s writes %r on the live runtime (%d rows) and no standard names it: "
            "a killed run nothing wakes on" % (label, value, count)
        )

    # Direction 2: a standard watching a code nothing emits. The silent one.
    for code, where in sorted(standards.items()):
        live = sum(
            surface["vocab"].get("host", {}).get(code, 0)
            for surface in (audit, board_rows) if surface is not None
        )
        if live:
            continue
        ever = sum(
            sum(counter.get(code, 0) for counter in surface["vocab"].values())
            for surface in (audit, board_rows) if surface is not None
        )
        findings.append(
            "%s names exit %s and no surface has written it %s: a rule watching a dead code"
            % (where, code, "since %s" % RUNTIME_BOUNDARY if ever else "ever")
        )

    if args.json:
        print(json.dumps({
            "findings": findings,
            "unreadable": unreadable,
            "boundary": RUNTIME_BOUNDARY,
            "standards": standards,
            "audit": None if audit is None else {
                "rows": audit["rows"],
                "vocab": {era_: dict(counter) for era_, counter in audit["vocab"].items()},
            },
            "board": None if board_rows is None else {
                "rows": board_rows["rows"],
                "vocab": {era_: dict(counter) for era_, counter in board_rows["vocab"].items()},
                "saturated": board_rows["saturated"],
                "window_days": board_rows["window_days"],
            },
        }, indent=1, sort_keys=True))
    else:
        print("Kill vocabulary of both surfaces, split at the %s runtime boundary" % RUNTIME_BOUNDARY)
        print("(before it the GitHub Actions runner's signal arithmetic; after it the host's words)\n")
        for label, surface, why in (("audit log", audit, audit_why), ("board", board_rows, board_why)):
            if surface is None:
                print("%s: UNREADABLE — %s\n" % (label, why))
                continue
            note = ""
            if surface.get("saturated"):
                note = "  [%d seat(s) saturated: an absence here is not proven]" % len(surface["saturated"])
            print("%s — %d rows%s" % (label, surface["rows"], note))
            for era_ in ("actions", "host"):
                counter = surface["vocab"].get(era_)
                if not counter:
                    print("  %-8s (no rows)" % era_)
                    continue
                print("  %-8s" % era_)
                for value, count in counter.most_common():
                    mark = "" if value in CLEAN else ("  named by %s" % standards[value] if value in standards else "  NAMED BY NO STANDARD")
                    print("    %-16s %5d   %-26s%s" % (value, count, span(surface["durations"].get((era_, value), [])), mark))
            print()
        if findings:
            print("Findings, %d:" % len(findings))
            for item in findings:
                print("  - %s" % item)
        else:
            print("No findings: every live kill is named by a standard and every named code is live.")
        if unreadable:
            print("\nUnreadable surfaces, %d — this run proves nothing about them:" % len(unreadable))
            for item in unreadable:
                print("  - %s" % item)

    if unreadable:
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
