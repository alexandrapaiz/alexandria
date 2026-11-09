#!/usr/bin/env python3
"""A queue served newest-first has no event that will ever name its oldest row.

    python3 tools/pr_backlog.py --fetch                  # read the live queue
    python3 tools/pr_backlog.py --prs /tmp/prs.json      # read a saved one
    python3 tools/pr_backlog.py --fetch --since 2026-11-08T23:00:00Z
    python3 tools/pr_backlog.py --fetch --json
    python3 tools/pr_backlog.py --fetch --age-hours 48   # what counts as backlog

Exit 0 when the queue has no backlog, or when the backlog is being drained at
least as fast as new work arrives. Exit 1 when the backlog is non-empty and the
merges since `--since` came mostly from rows newer than it, which is the thing
this file exists to make visible.

**Why age and not path.** This tool was written on 2026-11-09 to explain why two
items in the ExO seat's lane had been stalled for a week, and the first
hypothesis was wrong in a way worth keeping. The guess was contention: eleven
open pull requests wrote `prompts/exo-agent.md` at once, a previous run had
declined to ship its one improvement on exactly that ground, and the file is the
third most contested path in the repository. The measurement says the opposite.
Of the 200 most recent merges, the 24 that touched `prompts/exo-agent.md` are
the **fastest** population in the repository — median 0.41 h from open to merge,
mean 0.80 h, maximum 2.5 h — against a median of 1.09 h for pull requests with
no `prompts/` path at all and 1.76 h for another seat's charter. A contested
path is not a slow path here. What is slow is being old, and nothing in the
repository measured that, so this file measures it.

**The mechanism, which is a property of the manifests and not of anybody's
diligence.** Merging in this company is done by the PM seat, and the PM seat is
woken by `/srv/asc/roster/alexandria/pm/agent.toml`:

    subscriptions = ["message.posted", "item.moved", "pr.merged",
                     "check.failed", "run.failed", "run.reported", "pr.opened"]

Every one of those is an **edge** — a thing that just changed state. `pr.opened`
is the only one that names a pull request at birth and it fires exactly once. No
subscription in any manifest can express "wake me about a row that has been open
for a week", because no such event exists to subscribe to. So a pull request has
one notification in its whole life, and if the pass that receives it does not
merge it, the row is thereafter reachable only by a seat that goes looking. The
PM's daily cron, `5 11 * * *`, is the single oldest-first door in the company.

**The instance it was built on.** 2026-11-02 was a 158-run day for this company
and opened 32 pull requests. 2026-11-03 to 2026-11-07 then ran 72 runs of which
**one** passed turn one and **none** exited clean, the second multi-day provider
blackout in twelve days. The budget reset at 2026-11-08T23:00:00Z and the
company came back. In the first three hours after the reset, 13 pull requests
merged: 11 of them had been opened on 2026-11-08 or 2026-11-09, and **two** came
from the backlog. Meanwhile 40 of the 62 open rows predated the reset and 32 of
those were that single 2026-11-02 cohort. The recovery was real and it drained
the queue from the newest end, because the newest end is the end that emits
events.

**So the reading to take from a non-empty backlog is not that anybody is
behind.** It is that the rows in it have already spent their only notification,
and will not be merged by any seat that is waiting to be woken. That is why this
tool prints the oldest rows by number and author rather than only a count: the
output is meant to be pasted into a message to whoever merges, because a message
is `message.posted` and that is an event the queue does have.

**One honest limit.** A row can be old because nobody looked at it or because
somebody looked and held it, and a draft or a hold label is evidence of the
second. Both are reported per row and neither is subtracted from the count,
because this tool cannot read a disposition and should not guess one. A seat
reading the output decides; a run that wants the distinction asks the merger.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

FIELDS = "number,title,author,createdAt,isDraft,labels,headRefName"
HOLD_HINTS = ("hold", "blocked", "wait", "do-not-merge", "tier-c")


def _dt(s):
    """GitHub stamps are Zulu; datetime wants an offset it recognises."""
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


GH_TIMEOUT = 60


class FetchError(Exception):
    """A read that did not happen, carrying why, so no count is printed."""


def fetch(state, limit):
    """One `gh pr list`, bounded, with every failure named rather than raised.

    The bound is the point. This tool shipped on 2026-11-09 with no timeout
    and no handler on this call, on the same day this seat reported that very
    class in another seat's tools -- the fourth sighting of it, and the first
    found in this seat's own code, by the charter rule the report produced
    (prompts/exo-agent.md, "Run the class over your own code before you report
    it"). A hung `gh` here does not fail: it waits, and the only thing that
    ends the wait is the sixty-minute wall that ends the whole run, which is
    the portfolio's binding constraint and is invisible in the turn counts.

    And `check=True` with no handler threw `gh`'s own stderr away, because
    `capture_output=True` moves it off the terminal and `CalledProcessError`
    does not print it. An unauthenticated or rate-limited `gh` therefore
    produced a traceback that named the exit status and never the reason.
    """
    fields = FIELDS + ",mergedAt" if state == "merged" else FIELDS
    argv = ["gh", "pr", "list", "--state", state, "--limit", str(limit),
            "--json", fields]
    try:
        out = subprocess.run(argv, capture_output=True, text=True,
                             timeout=GH_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise FetchError(
            "gh pr list --state %s did not answer in %ds; no count is printed, "
            "because a partial queue read is a progress bar and not a "
            "measurement" % (state, GH_TIMEOUT))
    except FileNotFoundError:
        raise FetchError("no gh binary on PATH; this tool reads the queue "
                         "through gh and has no second door")
    if out.returncode != 0:
        raise FetchError("gh pr list --state %s exited %d: %s"
                         % (state, out.returncode,
                            (out.stderr or "").strip() or "no stderr"))
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as exc:
        raise FetchError("gh pr list --state %s returned %d bytes that are "
                         "not JSON: %s" % (state, len(out.stdout), exc))


def held(pr):
    """Evidence that somebody looked and chose not to merge, never a verdict."""
    if pr.get("isDraft"):
        return "draft"
    for lab in pr.get("labels") or []:
        name = (lab.get("name") if isinstance(lab, dict) else str(lab)) or ""
        if any(h in name.lower() for h in HOLD_HINTS):
            return "label:" + name
    return ""


def login(pr):
    a = pr.get("author") or {}
    return (a.get("login") if isinstance(a, dict) else str(a)) or "?"


def seat(pr):
    """The seat is the branch prefix, and it is never the author.

    Found by running this tool against the live queue on the day it was
    written: all 40 backlog rows reported one author, `alexandrapaiz`, because
    every seat in this company pushes with the same GitHub credential. A queue
    tool that groups by author therefore reports a single bucket and says
    nothing. The branch prefix is the discriminator that works, and it is the
    same one the bus itself uses to route `pr.merged` to a seat.
    """
    return ((pr.get("headRefName") or "").split("/")[0]) or "?"


def measure(open_prs, merged_prs, now, age_hours, since):
    """Split the open queue at `age_hours`, and the merges at `since`."""
    cut = now - datetime.timedelta(hours=age_hours)
    backlog, fresh = [], []
    for pr in open_prs:
        row = {
            "number": pr["number"],
            "title": pr.get("title") or "",
            "author": login(pr),
            "seat": seat(pr),
            "branch": pr.get("headRefName") or "",
            "created_at": pr["createdAt"],
            "age_hours": round((now - _dt(pr["createdAt"])).total_seconds() / 3600, 1),
            "held": held(pr),
        }
        (backlog if _dt(pr["createdAt"]) < cut else fresh).append(row)
    backlog.sort(key=lambda r: r["created_at"])

    drained = arrived = None
    if since is not None:
        drained = arrived = 0
        for pr in merged_prs:
            if not pr.get("mergedAt") or _dt(pr["mergedAt"]) < since:
                continue
            if _dt(pr["createdAt"]) < since:
                drained += 1
            else:
                arrived += 1
    return {
        "now": now.isoformat().replace("+00:00", "Z"),
        "age_hours": age_hours,
        "since": since.isoformat().replace("+00:00", "Z") if since else None,
        "open_total": len(open_prs),
        "backlog": backlog,
        "fresh_count": len(fresh),
        "merged_from_backlog": drained,
        "merged_new": arrived,
        "backlog_by_seat": _by_seat(backlog),
    }


def _by_seat(backlog):
    """Who the stalled rows belong to, oldest-row age per seat."""
    out = {}
    for row in backlog:
        s = out.setdefault(row["seat"], {"count": 0, "oldest_hours": 0.0})
        s["count"] += 1
        s["oldest_hours"] = max(s["oldest_hours"], row["age_hours"])
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["count"]))


def verdict(m):
    """Exit 1 only when there is a backlog *and* the drain is losing to intake.

    An empty backlog is the healthy case. A backlog with no `--since` is
    unjudged rather than passing, because this tool will not call a queue
    newest-first without having watched it move.
    """
    if not m["backlog"]:
        return 0, "no backlog: every open row is newer than the age cut"
    if m["merged_from_backlog"] is None:
        return 0, "backlog of %d, drain unmeasured (pass --since to judge it)" % len(m["backlog"])
    if m["merged_from_backlog"] + m["merged_new"] == 0:
        # A frozen queue is not a queue served newest-first, and saying so would
        # be a verdict on nothing. Same refusal as the no---since case: this
        # tool reports newest-first only after watching rows actually move.
        return 0, ("backlog of %d and nothing merged in the window at all: "
                   "unjudged, not draining" % len(m["backlog"]))
    if m["merged_from_backlog"] >= m["merged_new"]:
        return 0, "backlog of %d, draining: %d of %d merges since --since came from it" % (
            len(m["backlog"]), m["merged_from_backlog"],
            m["merged_from_backlog"] + m["merged_new"])
    return 1, "backlog of %d served newest-first: %d of %d merges since --since came from it" % (
        len(m["backlog"]), m["merged_from_backlog"],
        m["merged_from_backlog"] + m["merged_new"])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--fetch", action="store_true", help="read the live queue with gh")
    src.add_argument("--prs", help="a file of `gh pr list --json` output, open rows")
    p.add_argument("--merged", help="the same for merged rows; implied by --fetch")
    p.add_argument("--age-hours", type=float, default=24.0,
                   help="a row older than this is backlog (default 24)")
    p.add_argument("--since", help="measure the drain over merges after this stamp")
    p.add_argument("--now", help="override the clock, for tests")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--top", type=int, default=10, help="how many oldest rows to print")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    if a.fetch:
        try:
            open_prs = fetch("open", a.limit)
            merged_prs = fetch("merged", a.limit) if a.since else []
        except FetchError as exc:
            # Exit 2 is "I could not read", kept distinct from verdict()'s own
            # codes, so a reader never mistakes an unread queue for a clean one.
            print("pr_backlog: %s" % exc, file=sys.stderr)
            return 2
    else:
        open_prs = json.load(open(a.prs))
        merged_prs = json.load(open(a.merged)) if a.merged else []

    now = (_dt(a.now) if a.now
           else datetime.datetime.now(datetime.timezone.utc))
    since = _dt(a.since) if a.since else None
    m = measure(open_prs, merged_prs, now, a.age_hours, since)
    code, line = verdict(m)
    m["verdict"] = line
    m["exit"] = code

    if a.json:
        print(json.dumps(m, indent=2))
        return code

    print("open %d, backlog %d (older than %gh), fresh %d"
          % (m["open_total"], len(m["backlog"]), m["age_hours"], m["fresh_count"]))
    if m["since"]:
        print("merges since %s: %d from the backlog, %d from rows opened after it"
              % (m["since"], m["merged_from_backlog"], m["merged_new"]))
    print(line)
    if m["backlog"]:
        print("\noldest rows first — paste these at whoever merges, because a message is an event:")
        for row in m["backlog"][:a.top]:
            print("  #%-4d %6.1f h  %-22s %s%s"
                  % (row["number"], row["age_hours"], row["seat"],
                     row["title"][:58], "  [%s]" % row["held"] if row["held"] else ""))
        if len(m["backlog"]) > a.top:
            print("  ... and %d more" % (len(m["backlog"]) - a.top))
        print("\nby seat, from the branch prefix and not the author:")
        for name, s in m["backlog_by_seat"].items():
            print("  %-24s %3d stalled, oldest %.1f h" % (name, s["count"], s["oldest_hours"]))
    return code


if __name__ == "__main__":
    sys.exit(main())
