#!/usr/bin/env python3
"""Every seat's turns against the cap the host actually enforces.

    python3 tools/run-record.py                    # 7 days, every seat
    python3 tools/run-record.py --days 30
    python3 tools/run-record.py --seat exo-centralizer
    python3 tools/run-record.py --company Ursa
    python3 tools/run-record.py --json
    python3 tools/run-record.py --quiet            # findings and exit code only

Why this exists, in two numbers. On 2026-10-24 `tools/check-turn-caps.sh` read
**19 runs** across the whole portfolio over seven days and reported **one**
seat exhausted. Over the same seven days the host's own run record holds
**794 runs** and **49 of them were killed at their cap, across 12 seats** —
HQ's frontend in 8 of its 10 runs. The instrument was not wrong about its
sample. It was reading 2.4% of the population and exiting 0.

Two independent reasons it could not do better, and both are why this is a
second reader and not a patch to the first:

  * **It reads a dormant surface.** It lists runs of
    `.github/workflows/agent-<seat>.yml`. Decision 054 moved the clock to the
    resident host on 2026-10-16, and the last agent-workflow run anywhere in
    the portfolio was epitome's at 2026-10-18T19:47Z. Every seat run since is
    executed by the host daemon and appears in Actions not at all. Worse, the
    count only falls: once the window clears 2026-10-18 the tool reads zero
    runs and exits 0, which reads as "no seat exhausted its cap."
  * **It reads the wrong cap.** It greps `max-turns` out of the workflow. The
    cap the host enforces is `max_turns` in the seat's manifest,
    `runtime/agents/<company>/<seat>/agent.toml`, and the two disagree:
    alexandria/writer binds at 150 while its workflow says 225, Ursa's
    engineer binds at 120 while its workflow says 180. Both disagreements
    overstate the headroom, so both failures point the same way.

Three properties this reader is built to have, because each is a way the first
one failed.

  * **The scope is part of the answer** (L-A47). Every output names the file,
    the window, the number of records read and the number of lines it could
    not parse. One line of 5,621 was torn on 2026-10-20 — two concurrent
    appends interleaved — so unparseable lines are a real population, and a
    reader that drops them silently shrinks its own sample without saying so.
  * **Nothing readable is a refusal, not an all-clear** (L-A114). A missing
    record, an empty window or a record with no manifest to compare against
    exits **3**. A seat at or over its cap exits **1**. Only a measured,
    complete read with no seat at its cap exits **0**.
  * **A censored peak is labelled.** A run killed at the cap reports
    `turns = cap + 1`, which is the cap and not the seat's real peak (L-X3).
    Those runs are counted as `killed` and the peak is printed as `cap+` so no
    reader sets the next cap off a number the cap itself produced.

The record needs no credential: `/srv/asc/state/.epito/audit.jsonl` is on
every seat's own filesystem, written one JSON line per run event by the host
daemon since 2026-09-24. `ASC_RUN_RECORD` or `--path` overrides it, which is
also how the tests run with no host.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import os
import re
import sys

RECORD = os.environ.get("ASC_RUN_RECORD", "/srv/asc/state/.epito/audit.jsonl")
# The manifests the host enforces. The repo copy and /srv/asc/roster were
# identical on 2026-10-24 across all 41 seats; the repo copy is read because it
# is the one a seat on any machine has, and --manifests points at the other.
MANIFESTS = os.environ.get("ASC_AGENT_MANIFESTS", "runtime/agents")
# runtime/agents/<seat>/agent.toml is an HQ seat; runtime/agents/<company>/<seat>/
# is a product's. The audit record's `agent` field is the same path with the
# separator flattened, which is also the hook route (POST /hooks/<agent>).
HQ = "alexandra-systems"


def manifest_caps(root: str) -> dict:
    """{audit agent name: (company, seat, max_turns)}, from the seat manifests."""
    out = {}
    for rel in sorted(glob.glob("**/agent.toml", root_dir=root, recursive=True)):
        try:
            text = open(os.path.join(root, rel)).read()
        except OSError:
            continue
        found = re.search(r"^max_turns\s*=\s*(\d+)", text, re.M)
        parts = rel.split("/")[:-1]
        if not parts:
            continue
        company, seat = (HQ, parts[0]) if len(parts) == 1 else (parts[0], parts[-1])
        out["-".join(parts)] = (company, seat, int(found.group(1)) if found else None)
    return out


def read(path: str, since: datetime.datetime):
    """The `run.end` records in the window, and what the read itself cost.

    Returns (runs, scope). `scope` is the answer's own provenance and is never
    omitted from an output: a reader who cannot see the sample cannot judge the
    number computed from it.
    """
    scope = {"path": path, "lines": 0, "unparseable": 0, "run_end": 0,
             "in_window": 0, "since": since.isoformat(), "readable": False}
    runs = []
    try:
        handle = open(path, errors="replace")
    except OSError as failed:
        scope["error"] = str(failed)
        return runs, scope
    scope["readable"] = True
    with handle:
        for line in handle:
            if not line.strip():
                continue
            scope["lines"] += 1
            try:
                record = json.loads(line)
            except ValueError:
                # A torn line is two concurrent appends interleaved. Counted and
                # reported, never dropped quietly.
                scope["unparseable"] += 1
                continue
            if record.get("action") != "run.end":
                continue
            scope["run_end"] += 1
            stamp = record.get("ts") or ""
            try:
                when = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError:
                scope["unparseable"] += 1
                continue
            if when < since:
                continue
            scope["in_window"] += 1
            record["_when"] = when
            runs.append(record)
    return runs, scope


def percentile(values: list, share: float) -> int:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))]


def summarise(runs: list, caps: dict) -> list:
    """One row per seat that ran, with the cap that binds it beside its turns."""
    grouped = collections.defaultdict(list)
    for record in runs:
        grouped[record.get("agent") or "?"].append(record)
    rows = []
    for agent, group in grouped.items():
        company, seat, cap = caps.get(agent, (None, agent, None))
        turns = [r["turns"] for r in group if isinstance(r.get("turns"), int)]
        killed = [r for r in group if cap and isinstance(r.get("turns"), int) and r["turns"] > cap]
        # A run that reports more turns than the cap was cut off at it, so its
        # count is the cap and not evidence about the seat (L-X3). Every
        # distribution figure is therefore computed over the runs that finished
        # INSIDE the cap, and not over all of them. Labelling only the peak is
        # not enough: the first draft of this tool printed `cap+` in the peak
        # column and the censored number itself one column to the right, which
        # is the same wrong cap for anyone reading the row rather than the
        # header. Where nothing finished inside the cap there is no uncensored
        # figure to print, and the column says `cap+` rather than a number.
        free = [r["turns"] for r in group
                if isinstance(r.get("turns"), int) and not (cap and r["turns"] > cap)]
        rows.append({
            "agent": agent, "company": company, "seat": seat, "cap": cap,
            "manifest": agent in caps,
            "runs": len(group), "measured": len(turns), "uncensored": len(free),
            "peak": max(free) if free else None,
            "p90": percentile(free, 0.9) if free else None,
            "median": percentile(free, 0.5) if free else None,
            "killed": len(killed),
            "censored": bool(killed),
            "at_cap": bool(cap and turns and max(turns) >= cap),
            # The highest turn count the record holds for this seat, censored or
            # not. Kept so `--json` can show the raw number; never printed as a
            # peak, because for a killed run it is the cap.
            "highest_seen": max(turns) if turns else None,
            "failed": sum(1 for r in group if r.get("exit")),
            "no_pr": sum(1 for r in group if not r.get("pr")),
        })
    return sorted(rows, key=lambda r: (-r["killed"], -(r["peak"] or 0)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--seat", default="")
    ap.add_argument("--company", default="")
    ap.add_argument("--path", default=RECORD)
    ap.add_argument("--manifests", default=MANIFESTS)
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--help", "-h", action="store_true", dest="want_help")
    args = ap.parse_args(argv)
    if args.want_help:
        print(__doc__.rstrip())
        return 0

    now = datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(days=args.days)
    runs, scope = read(args.path, since)
    caps = manifest_caps(args.manifests)
    scope["manifests"] = len(caps)
    scope["manifests_root"] = args.manifests

    rows = summarise(runs, caps)
    if args.company:
        rows = [r for r in rows if (r["company"] or "").lower() == args.company.lower()]
    if args.seat:
        want = args.seat.lower()
        rows = [r for r in rows if want in (r["seat"] or "").lower() or want == r["agent"].lower()]

    findings = [r for r in rows if r["at_cap"]]
    unmeasured = (not scope["readable"]) or not scope["in_window"] or not caps
    if args.as_json:
        print(json.dumps({"scope": scope, "seats": rows,
                          "findings": [r["agent"] for r in findings],
                          "killed": sum(r["killed"] for r in rows)}, indent=2, default=str))
    elif not args.quiet:
        if not scope["readable"]:
            print("run-record: %s is not readable here (%s)." % (args.path, scope.get("error")))
            print("The record lives on the seat host. Read it there, or point --path at a copy.")
        else:
            print("%s — %d of %d lines were run.end, %d in the last %g days, %d unparseable."
                  % (scope["path"], scope["run_end"], scope["lines"], scope["in_window"],
                     args.days, scope["unparseable"]))
            print("caps from %s (%d seat manifests; the cap the host enforces, not the workflow's)\n"
                  % (args.manifests, len(caps)))
            print("PEAK and P90 are over the runs that finished INSIDE the cap: a run killed at")
            print("the cap reports cap + 1, which is the cap and not the seat (L-X3).\n")
            print("%-18s %-16s %5s %5s %6s %5s %6s %6s %6s  %s"
                  % ("COMPANY", "SEAT", "CAP", "RUNS", "KILLED", "PEAK", "P90", "FAILED", "NO-PR", "NOTE"))
            for r in rows:
                peak = "cap+" if r["censored"] else (r["peak"] if r["peak"] is not None else "-")
                p90 = r["p90"] if r["p90"] is not None else ("cap+" if r["censored"] else "-")
                note = ""
                if r["killed"]:
                    note = ("killed at the cap %dx of %d runs — peak is censored; step to %d (L-X3)"
                            % (r["killed"], r["runs"], r["cap"] * 3 // 2))
                elif r["at_cap"]:
                    note = "reached the cap exactly; no headroom left"
                elif not r["manifest"]:
                    note = "no seat manifest found — an unstated cap is still a cap, and nobody has measured it"
                print("%-18s %-16s %5s %5d %6d %5s %6s %6d %6d  %s"
                      % (r["company"] or "?", r["seat"], r["cap"] if r["cap"] else "-",
                         r["runs"], r["killed"], peak, p90,
                         r["failed"], r["no_pr"], note))
            print()

    if unmeasured:
        if not args.as_json:
            reason = ("the record is not readable here" if not scope["readable"]
                      else "no run.end record falls in the window" if not scope["in_window"]
                      else "no seat manifest was readable, so no cap could be compared")
            print("Nothing measured: %s. This is not an all-clear (L-A47)." % reason)
        return 3
    if findings:
        if not args.as_json:
            print("%d of %d seat(s) reached or passed the cap the host enforces, and %d run(s) "
                  "were killed at one in the last %g days."
                  % (len(findings), len(rows), sum(r["killed"] for r in rows), args.days))
            print("A cap hit is evidence about the cap, not about the seat "
                  "(standards/roles/exo.md §7). Raising one is an edit to the seat's manifest, "
                  "which is the owner's merge (ADR-011).")
        return 1
    if not args.as_json and not args.quiet:
        print("No seat reached its cap in the last %g days, over %d measured runs."
              % (args.days, scope["in_window"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
