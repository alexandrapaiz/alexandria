#!/usr/bin/env python3
"""Measure what the audit log's `pr` field actually records.

The host writes one `run.end` row per run into `/srv/asc/state/.epito/audit.jsonl`,
and that row carries a `pr` field.  The field is NOT a fact about whether the run
opened a pull request: it is `tail.match(PR_URL_RE)` over the last 64 KiB of the
run's output (`cli/src/lib/runner.js` lines 167/178/193), so a run that opened a
pull request and did not print its web address again before finishing records a
null.  Both halves of the `pr=-` ratio two seats published on 2026-11-02 were that
null rate rather than a behaviour.

This tool establishes ground truth instead of trusting the field.  It brackets
each seat's runs between its `run.start` and `run.end` rows, counts the pull
requests actually created inside each window from the GitHub API, and reports the
field's false-negative rate against that.

    gh pr list --state all --limit 200 \
       --json number,headRefName,createdAt \
       --jq '.[] | [.createdAt,.number,.headRefName] | @tsv' > /tmp/prs.tsv
    python3 tools/pr_field_truth.py --day 2026-11-02 --prs /tmp/prs.tsv

Exits 1 when the field's false-negative rate exceeds --max-miss (default 0.10),
because above that the field cannot support any claim about shipping behaviour.
"""
import argparse
import collections
import json
import sys

AUDIT = "/srv/asc/state/.epito/audit.jsonl"


def run_windows(audit_path, day):
    """Pair each seat's run.start with the run.end that closes it."""
    rows = []
    with open(audit_path) as fh:
        for line in fh:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if str(r.get("ts", "")).startswith(day) and r.get("action") in (
                "run.start",
                "run.end",
            ):
                rows.append(r)
    pending, windows = {}, collections.defaultdict(list)
    for r in sorted(rows, key=lambda x: x["ts"]):
        seat = r["agent"]
        if r["action"] == "run.start":
            pending[seat] = r["ts"]
        else:
            start = pending.pop(seat, None)
            if start:  # a run.end with no start in-window is a run from yesterday
                windows[seat].append((start, r["ts"], r.get("pr"), r.get("exit")))
    return windows


def pulls(prs_path, day):
    out = []
    with open(prs_path) as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            ts, num, ref = parts
            if ts.startswith(day):
                out.append((ts.rstrip("Z"), int(num), ref))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--prs", required=True, help="TSV of createdAt/number/headRefName")
    ap.add_argument("--audit", default=AUDIT)
    ap.add_argument("--max-miss", type=float, default=0.10)
    args = ap.parse_args()

    windows = run_windows(args.audit, args.day)
    all_prs = pulls(args.prs, args.day)
    # a branch's first path segment is the seat name the audit log uses
    by_seat = collections.defaultdict(list)
    for ts, num, ref in all_prs:
        by_seat[ref.split("/")[0]].append((ts, num, ref))

    hit = miss = none_opened = 0
    skipped = []
    print(f"{args.day}: ground truth from {len(all_prs)} pull requests created\n")
    for seat in sorted(windows):
        mine = by_seat.get(seat, [])
        h = m = z = 0
        missed = []
        for start, end, pr, _exit in windows[seat]:
            opened = [p for p in mine if start < p[0] < end]
            if not opened:
                # A window with the field SET and no attributable pull request is
                # proof that this seat's branches do not start with its audit-log
                # name -- `security` ships on `sec/`.  That is a gap in this
                # mapping and not a run that opened nothing, so the seat's
                # zero-opened windows cannot be counted either way.
                z += 1
                if pr:
                    h = -1
                    break
                continue
            if pr:
                h += 1
            else:
                m += 1
                missed.append(opened[0][1])
        if h < 0 or (h + m == 0 and z):
            skipped.append(seat)
            continue
        if h + m + z == 0:
            continue
        hit, miss, none_opened = hit + h, miss + m, none_opened + z
        rate = f"{100 * m / (h + m):.1f}%"
        print(
            f"  {seat:24} windows={h + m + z:3}  opened>=1={h + m:3} "
            f"(field set {h:3}, field null {m:3} = {rate} false negative)  opened 0={z:2}"
        )
        if missed:
            print(f"  {'':24} pull requests the field does not record: {missed}")

    total = hit + miss
    print()
    if skipped:
        print(
            "seats whose branch prefix this mapping cannot reach, excluded rather "
            f"than counted as having shipped nothing: {', '.join(skipped)}"
        )
        print()
    print(f"runs that demonstrably opened a pull request : {total}")
    print(f"  the `pr` field recorded it                 : {hit}")
    print(f"  the `pr` field is null                     : {miss}")
    print(f"runs that opened nothing, field correctly null: {none_opened}")
    if not total:
        print("\nno bracketed runs: nothing to say about the field")
        return 0
    rate = miss / total
    print(f"\nfalse-negative rate: {100 * rate:.1f}%")
    print(
        "a null in this field means the run did not reprint its pull request URL "
        "in its last 64 KiB of output, and it means nothing else"
    )
    if rate > args.max_miss:
        print(
            f"\nFAIL: {100 * rate:.1f}% exceeds the {100 * args.max_miss:.0f}% "
            "ceiling, so no claim about shipping behaviour may be drawn from "
            "this field or from the log trailer that shares its regex"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
