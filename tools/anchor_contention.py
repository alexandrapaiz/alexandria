#!/usr/bin/env python3
"""A shared append anchor is a merge queue that cannot be merged, and this counts it.

    python3 tools/anchor_contention.py --fetch           # ask gh for the open pull requests
    python3 tools/anchor_contention.py --prs prs.json    # read a file instead, no network
    python3 tools/anchor_contention.py --json            # the verdict as a script reads it
    python3 tools/anchor_contention.py --min-anchor 3    # which counts are worth printing
    python3 tools/anchor_contention.py --max-anchor 6    # opt in to a failing threshold

`docs/standards/lessons.md` L-A18 says a register the whole company appends to
needs an inbox: one file per entry, written by the seat, folded into the register
on the mainline where there is one author. The rule is right and it has been
right since 2026-10-18. What it has never had is a number.

That is what this file is. It answers two questions about the rule rather than
restating it: **which paths are being appended to by several open pull requests
at once**, and **where an inbox exists, how many of the pull requests that
append to its register went around it.**

Both questions are answered from one input, the file lists of the open pull
requests, because contention is a property of the open set and not of the
mainline. A path with one writer is not an anchor no matter how long it is, and
`main` cannot show you a collision that has not been attempted yet.

Why this is report-only by default. `tools/incidents.py` states the rule this
obeys: "a gate that can turn `main` red for a bookkeeping step nobody promised
to run is a worse defect than the one being fixed." Contention is not an error,
it is a cost, and the cost is paid by whoever merges rather than by whoever
pushed. So the exit code is 0 unless a caller asks for a threshold with
`--max-anchor`, which is how a sweep opts in without every pull request
inheriting it.

Four readings, and the distinction between the last two is the measurement.

`fold` — the pull request removes inbox entries and adds to the register, adding
no new inbox entry. That is the single-writer movement the remedy is built on
and it is not contention, even though it touches the anchor.

`inbox` — the pull request writes inbox entries and leaves the register alone.
The remedy, working.

`bypass` — the pull request appends to the register and writes no inbox entry.
The remedy, available and not used.

`both` — the pull request writes inbox entries *and* appends to the register.
Worth its own word because it is the reading that looks like adoption in a diff
summary and collides exactly like a bypass.

The register/inbox pairs are discovered rather than listed: a directory
`<path>/inbox/` implies the register `<path>.md` beside it. A list would have to
be maintained, and L-A18 names a second register still owed an inbox, so the
next pair should appear here the day it is built and not the day somebody
remembers this file.
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def discover_registers(root=REPO_ROOT):
    """Map register path -> inbox prefix, for every `<path>/inbox/` in docs/."""
    pairs = {}
    docs = Path(root) / "docs"
    if not docs.is_dir():
        return pairs
    for inbox in sorted(docs.rglob("inbox")):
        if not inbox.is_dir():
            continue
        register = inbox.parent.with_suffix(".md")
        pairs[str(register.relative_to(root))] = str(inbox.relative_to(root)) + "/"
    return pairs


def fetch_open_prs(limit=100):
    """Ask gh for the open pull requests and their file lists."""
    listing = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--json", "number", "--limit", str(limit)],
        capture_output=True, text=True, check=True,
    )
    prs = []
    for entry in json.loads(listing.stdout):
        number = entry["number"]
        view = subprocess.run(
            ["gh", "pr", "view", str(number), "--json", "files"],
            capture_output=True, text=True,
        )
        if view.returncode != 0 or not view.stdout.strip():
            continue
        prs.append({"number": number, "files": json.loads(view.stdout)["files"]})
    return prs


def classify(pr, register, inbox_prefix):
    """How did this pull request treat one register? None if it did not touch it."""
    appended = 0
    new_entries = 0
    removed_entries = 0
    for f in pr.get("files", []):
        path = f.get("path", "")
        additions = f.get("additions", 0) or 0
        deletions = f.get("deletions", 0) or 0
        if path == register:
            appended = additions
        elif path.startswith(inbox_prefix):
            if additions > 0 and deletions == 0:
                new_entries += 1
            elif additions == 0 and deletions > 0:
                removed_entries += 1
    if not appended and not new_entries and not removed_entries:
        return None
    if appended and removed_entries and not new_entries:
        return "fold"
    if appended and new_entries:
        return "both"
    if appended:
        return "bypass"
    return "inbox"


def contention(prs):
    """How many open pull requests touch each path."""
    counts = Counter()
    for pr in prs:
        for path in {f.get("path", "") for f in pr.get("files", [])}:
            if path:
                counts[path] += 1
    return counts


def measure(prs, registers):
    counts = contention(prs)
    report = {"open_prs": len(prs), "anchors": [], "registers": {}}
    for path, count in counts.most_common():
        report["anchors"].append({"path": path, "open_prs": count})
    for register, inbox_prefix in sorted(registers.items()):
        readings = {}
        for pr in prs:
            reading = classify(pr, register, inbox_prefix)
            if reading:
                readings[pr["number"]] = reading
        contested = {n: r for n, r in readings.items() if r != "fold"}
        using = sum(1 for r in contested.values() if r == "inbox")
        bypassing = sum(1 for r in contested.values() if r in ("bypass", "both"))
        report["registers"][register] = {
            "inbox": inbox_prefix,
            "touching": len(readings),
            "folds": sum(1 for r in readings.values() if r == "fold"),
            "using_inbox": using,
            "bypassing": bypassing,
            "bypass_rate": (bypassing / (using + bypassing)) if (using + bypassing) else None,
            "by_pr": readings,
        }
    return report


def render(report, min_anchor):
    lines = [f"{report['open_prs']} open pull requests read."]
    anchors = [a for a in report["anchors"] if a["open_prs"] >= min_anchor]
    if anchors:
        lines.append("")
        lines.append(f"Paths written by {min_anchor} or more open pull requests at once:")
        for a in anchors:
            lines.append(f"  {a['open_prs']:>3}  {a['path']}")
    else:
        lines.append(f"No path is written by {min_anchor} or more open pull requests.")
    for register, r in report["registers"].items():
        lines.append("")
        lines.append(f"{register}  (inbox: {r['inbox']})")
        if not r["touching"]:
            lines.append("  no open pull request touches it")
            continue
        rate = "n/a" if r["bypass_rate"] is None else f"{r['bypass_rate']:.0%}"
        lines.append(
            f"  {r['touching']} touching: {r['folds']} fold, "
            f"{r['using_inbox']} use the inbox, {r['bypassing']} go around it "
            f"— bypass rate {rate}"
        )
        for number, reading in sorted(r["by_pr"].items()):
            lines.append(f"    #{number}: {reading}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--fetch", action="store_true", help="ask gh for the open pull requests")
    source.add_argument("--prs", type=Path, help="a JSON file of {number, files} objects")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    parser.add_argument("--min-anchor", type=int, default=3, help="smallest count worth printing")
    parser.add_argument(
        "--max-anchor", type=int, default=None,
        help="exit 1 if any path is written by more than this many open pull requests",
    )
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)

    prs = fetch_open_prs() if args.fetch else json.loads(args.prs.read_text())
    report = measure(prs, discover_registers(args.root))

    print(json.dumps(report, indent=2) if args.json else render(report, args.min_anchor))

    if args.max_anchor is not None:
        worst = report["anchors"][0]["open_prs"] if report["anchors"] else 0
        if worst > args.max_anchor:
            print(
                f"\nFAIL: {report['anchors'][0]['path']} is written by {worst} open "
                f"pull requests, over the {args.max_anchor} asked for.",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
