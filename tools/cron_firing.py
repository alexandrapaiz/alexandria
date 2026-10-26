#!/usr/bin/env python3
"""A cron slot that fired and produced nothing is a lost cycle, and it says so.

    python3 tools/cron_firing.py                        # today, every seat
    python3 tools/cron_firing.py --day 2026-10-25
    python3 tools/cron_firing.py --seat alexandria-engineer
    python3 tools/cron_firing.py --json                  # the verdict as a script reads it
    python3 tools/cron_firing.py --root /path/to/logs    # for tests and for other hosts

Exit 0 when every cron slot that came due on the day either shipped something
or was never on the clock. Exit 1 when one fired and produced nothing, which
is the thing this file exists to make visible.

## Why this exists

The host writes one log per run to `/srv/asc/state/.epito/logs/<seat>/`, and
each one carries the three facts a cadence audit needs: when the clock fired,
what triggered it, and whether the run reached a pull request. Nothing in this
repository has ever read them. The reading has been done by hand, by one seat,
once a week, with a Python heredoc pasted into a relay page
(`docs/agents/hq-relay.md`), and the findings that came out of it are
`INC-2026-10-25-the-seats-first-cron-slot-fired-was-refused-and-the-mode-rule-read-the-refusal-as-coverage`
and
`INC-2026-10-25-the-weekly-slot-is-scheduled-inside-the-hours-the-weekly-provider-budget-is-spent`.

Both of those were correct and both arrived late, because a weekly audit is
how fast a weekly audit can be. On 2026-10-25 this seat's own 11:06Z cron slot
fired, was refused by the provider's weekly limit in 351 milliseconds, and
produced nothing. A daily seat lost a day, no instrument noticed, and the next
run of the seat had no way to tell a lost cycle from a cycle that never came
due. That is the gap: the register has learned the lesson twice and nothing
checks it.

## Three states, because two is what gets this wrong

The register's own newest lesson is that absence is weak evidence. It was
written twice in two days: a slot with no row may never have had a clock
(2026-10-24), and a slot with a row may have done nothing (2026-10-25). A
check that reports fired-or-not therefore answers the wrong question, so this
one answers three.

`shipped`
    The slot fired and the run reached a pull request. The trailer the host
    writes is `# exit=0 pr=<url>`, so this is read rather than inferred.

`lost`
    The slot fired and the run reached no pull request. The reason is carried
    with it: `weekly-limit` and `session-limit` are the provider's two refusals,
    which arrive as the same `429` and are told apart only by the sentence in
    the result, `api-error` is any other error status, `nonzero-exit` is a run
    that failed without one, and `silent` is the worst of the five, a run that
    exited 0 and shipped nothing anyway. That last one is incident 3's failure
    mode and the reason the ship-first rule is in every charter.

`unseen`
    A slot this seat has fired at on other days in the history window, with no
    row on the day asked about. This is **never reported as a failure**, because
    a clock that was retired and a clock that did not fire leave the same
    absence, and this file cannot tell them apart. It is reported as a question
    carrying the evidence that formed it: the days the slot did fire. A seat
    that reads it can go and look.

## What it reads out of a log, and what it refuses to read

Only whitelisted fields, and never a raw line. The filename gives the start
time and the trigger, the trailer gives the exit code and the pull request, and
the result JSON gives the turn count and the refusal sentence. Everything else
in the file is skipped on purpose: the header line names the environment
variables a run was handed, the body carries whatever the run's prompt and its
tool output contained, and a tool that prints log lines to a terminal or a pull
request is a tool that will eventually print one of those. Nothing here is
secret today and the whitelist is what keeps that true tomorrow.

The filename is authoritative for the trigger rather than the header, because
the filename is what the host names the run and the header is a comment. They
agree in every log on this host; when they disagree, the name wins and the
disagreement is reported.
"""

import argparse
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

# `2026-10-25T23-52-25-817Z-cron.log`: an ISO instant with the colons and the
# dot beaten into hyphens so it can be a filename, then the trigger.
_NAME = re.compile(
    r"^(?P<stamp>\d{4}-\d{2}-\d{2})T(?P<h>\d{2})-(?P<m>\d{2})-(?P<s>\d{2})"
    r"-(?P<ms>\d{3})Z-(?P<trigger>[a-z]+)\.log$")

# `# trigger=cron model=claude-opus-5 repo=... ref=(default) executor=claude`
_HEADER_TRIGGER = re.compile(r"^#\s+trigger=(?P<trigger>\S+)")

# `# exit=0 pr=https://github.com/o/r/pull/516 session=<uuid> turns=25`, and
# `pr=-` when the run reached none. The trailer is the last line the host
# writes, so a log without one belongs to a run that was killed.
_TRAILER = re.compile(
    r"^#\s+exit=(?P<exit>-?\d+)\s+pr=(?P<pr>\S+)"
    r"(?:\s+session=(?P<session>\S+))?(?:\s+turns=(?P<turns>\d+))?")

LOG_ROOT = pathlib.Path("/srv/asc/state/.epito/logs")

# How long after a run starts its missing trailer still means "working"
# rather than "killed". See `verdict_of`.
GRACE_MINUTES = 90

UTC = timezone.utc


def classify_refusal(result_text, api_error_status):
    """Which of the provider's two limits refused this run, if one did.

    Both arrive as `api_error_status: 429` and the only discriminator is the
    sentence, which is the finding
    `INC-2026-10-25-the-weekly-slot-is-scheduled-inside-the-hours-the-weekly-provider-budget-is-spent`
    turns on. A weekly limit resets at a week boundary and a session limit
    resets in hours, so reading them as one refusal makes a lost week look
    like a lost hour.
    """
    if api_error_status != 429:
        return None
    text = (result_text or "").lower()
    if "weekly" in text:
        return "weekly-limit"
    if "session" in text or "5-hour" in text or "5 hour" in text:
        return "session-limit"
    return "unclassified-429"


def parse_run(path):
    """The five facts a cadence audit needs out of one run's log, or None.

    None means the filename is not a run log, which is how a stray file in the
    directory is skipped rather than guessed at.
    """
    path = pathlib.Path(path)
    name = _NAME.match(path.name)
    if not name:
        return None
    started = datetime(
        int(name["stamp"][0:4]), int(name["stamp"][5:7]), int(name["stamp"][8:10]),
        int(name["h"]), int(name["m"]), int(name["s"]),
        int(name["ms"]) * 1000, tzinfo=UTC)

    run = {
        "seat": path.parent.name,
        "run_id": path.name[:-len(".log")],
        "day": name["stamp"],
        "started": started,
        "trigger": name["trigger"],
        "header_trigger": None,
        "exit_code": None,
        "pr": None,
        "turns": None,
        "api_error_status": None,
        "refusal": None,
        "truncated": True,
    }

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        run["why_unread"] = f"{path.name} could not be read here ({exc})"
        return run

    for line in lines:
        if run["header_trigger"] is None:
            header = _HEADER_TRIGGER.match(line)
            if header:
                run["header_trigger"] = header["trigger"]
                continue
        trailer = _TRAILER.match(line)
        if trailer:
            run["exit_code"] = int(trailer["exit"])
            run["pr"] = None if trailer["pr"] == "-" else trailer["pr"]
            run["turns"] = (int(trailer["turns"])
                            if trailer["turns"] is not None else None)
            run["truncated"] = False
            continue
        # The result object is one line of JSON among a stream of them, and it
        # is the only one worth parsing. Guarding the parse rather than the
        # line keeps a half-written log readable: a run killed mid-write leaves
        # a truncated final line, and the facts before it are still true.
        #
        # The line is identified by parsing it and reading `type`, not by
        # matching `"type":"result"` as text, which is what this file did
        # first. That version worked against every log on this host and broke
        # against a fixture whose only difference was a space after the colon,
        # and the way it broke is the problem: a refused run read as a plain
        # non-zero exit, so the refusal silently stopped being classified
        # while the count of lost cycles stayed right. A reader of a format it
        # does not own should not depend on that format's whitespace.
        if not line.startswith("{") or '"type"' not in line:
            continue
        try:
            result = json.loads(line)
        except ValueError:
            continue
        if result.get("type") == "result":
            run["api_error_status"] = result.get("api_error_status")
            if run["turns"] is None:
                run["turns"] = result.get("num_turns")
            run["refusal"] = classify_refusal(
                result.get("result"), result.get("api_error_status"))

    return run


def read_runs(root=LOG_ROOT, seat=None):
    """Every run log under `root`, newest last. Missing root is not an error.

    A seat sandbox is not guaranteed to have the host's log directory mounted,
    and neither is a pull request check. Both get an empty list and a caller
    that can say "observation skipped" rather than a traceback.
    """
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    runs = []
    for seat_dir in sorted(root.iterdir()):
        if not seat_dir.is_dir():
            continue
        if seat is not None and seat_dir.name != seat:
            continue
        for log in sorted(seat_dir.iterdir()):
            run = parse_run(log)
            if run is not None:
                runs.append(run)
    runs.sort(key=lambda r: r["started"])
    return runs


def slot(run):
    """The minute of the day a run started, which is the slot it fired in."""
    return run["started"].hour * 60 + run["started"].minute


def _slot_label(minute):
    return f"{minute // 60:02d}:{minute % 60:02d}Z"


def verdict_of(run, now=None, grace_minutes=GRACE_MINUTES):
    """`shipped`, `in-flight`, or the one word for why no pull request.

    A log with no trailer is a run the host has not finished writing, and from
    the log alone a run still working and a run killed mid-turn are the same
    file. So the age of the run decides: inside `grace_minutes` it is
    `in-flight`, which is not a finding, and past it the trailer is missing
    because nobody is coming to write it.

    The grace has to be longer than a run, and the longest completed run in
    this seat's own record is 311 seconds. Ninety minutes is generous on
    purpose: the cost of calling a live run lost is a false alarm in every
    report, and the cost of waiting is that a killed run is named in the next
    reading rather than this one.
    """
    if run["pr"]:
        return "shipped"
    if run["refusal"]:
        return run["refusal"]
    if run["api_error_status"]:
        return "api-error"
    if run["truncated"]:
        now = now or datetime.now(UTC)
        age = (now - run["started"]).total_seconds() / 60
        return "in-flight" if age < grace_minutes else "no-trailer"
    if run["exit_code"]:
        return "nonzero-exit"
    return "silent"


def judge(runs, day, tolerance=15, history_days=14, now=None):
    """What every cron slot that came due on `day` did, in the three states.

    `tolerance` is how many minutes apart two firings can be and still be the
    same slot. The host's own record is tight, 11:06:03 against 11:06:07 on
    consecutive days, so fifteen minutes is loose enough to absorb a queue and
    far short of the twelve hours between this seat's two slots.
    """
    day_runs = [r for r in runs if r["day"] == day]
    asked = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=UTC)
    now = now or datetime.now(UTC)

    history = [r for r in runs
               if r["trigger"] == "cron"
               and r["day"] != day
               and 0 < (asked - r["started"].replace(
                   hour=0, minute=0, second=0, microsecond=0)).days
               <= history_days]

    findings = []
    for run in day_runs:
        if run["trigger"] != "cron":
            continue
        verdict = verdict_of(run, now=now)
        findings.append({
            "seat": run["seat"],
            "slot": _slot_label(slot(run)),
            "state": {"shipped": "shipped",
                      "in-flight": "in-flight"}.get(verdict, "lost"),
            "why": verdict,
            "run_id": run["run_id"],
            "turns": run["turns"],
            "pr": run["pr"],
        })

    fired = {(r["seat"], slot(r)) for r in day_runs if r["trigger"] == "cron"}
    seen = {}
    for run in history:
        seen.setdefault((run["seat"], slot(run)), []).append(run["day"])
    for (seat, minute), days in sorted(seen.items()):
        if any(s == seat and abs(m - minute) <= tolerance for s, m in fired):
            continue
        # Fold slots that are the same clock a minute apart into one question.
        if any(f["seat"] == seat and f["state"] == "unseen"
               and abs(_minute_of(f["slot"]) - minute) <= tolerance
               for f in findings):
            continue
        findings.append({
            "seat": seat,
            "slot": _slot_label(minute),
            "state": "unseen",
            "why": "no row on this day",
            "evidence": sorted(set(days)),
        })

    findings.sort(key=lambda f: (f["seat"], f["slot"]))
    return {
        "day": day,
        "findings": findings,
        "lost": [f for f in findings if f["state"] == "lost"],
        "history_days": history_days,
    }


def _minute_of(label):
    return int(label[0:2]) * 60 + int(label[3:5])


def render(result, root):
    lines = [f"cron slots on {result['day']}, from the host's firing record"]
    if not result["findings"]:
        lines.append(f"  no cron slot fired and none has in the trailing "
                     f"{result['history_days']} days under {root}")
        return "\n".join(lines)
    for finding in result["findings"]:
        if finding["state"] == "shipped":
            lines.append(f"  shipped  {finding['seat']} {finding['slot']} "
                         f"-> {finding['pr']}")
        elif finding["state"] == "in-flight":
            lines.append(f"  running  {finding['seat']} {finding['slot']} "
                         f"no trailer yet, and young enough that the run is "
                         f"more likely working than killed")
        elif finding["state"] == "lost":
            turns = finding["turns"]
            turns = f", {turns} turn{'' if turns == 1 else 's'}" if turns else ""
            lines.append(f"  LOST     {finding['seat']} {finding['slot']} "
                         f"{finding['why']}{turns}, no pull request")
        else:
            days = ", ".join(finding["evidence"])
            lines.append(f"  unseen   {finding['seat']} {finding['slot']} "
                         f"no row today; it fired on {days}. A retired clock "
                         f"and a clock that did not fire look the same here")
    if result["lost"]:
        lines.append("")
        lines.append(f"{len(result['lost'])} cycle(s) lost. A cron slot that "
                     f"fires and produces nothing is the cadence failing while "
                     f"the firing record says it worked.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--day", default=None,
                        help="YYYY-MM-DD, default today in UTC")
    parser.add_argument("--seat", default=None,
                        help="one seat's directory name, default every seat")
    parser.add_argument("--root", default=str(LOG_ROOT),
                        help="the host's log directory")
    parser.add_argument("--history-days", type=int, default=14,
                        help="how far back to look for a slot's other firings")
    parser.add_argument("--json", action="store_true",
                        help="the verdict as a script reads it")
    args = parser.parse_args(argv)

    day = args.day or datetime.now(UTC).strftime("%Y-%m-%d")
    root = pathlib.Path(args.root)
    runs = read_runs(root, seat=args.seat)
    if not runs and not root.is_dir():
        message = (f"observation skipped: {root} is not a directory here, so "
                   f"this sandbox holds no firing record to read")
        print(json.dumps({"day": day, "why_skipped": message}, indent=2)
              if args.json else message)
        return 0

    result = judge(runs, day, history_days=args.history_days)
    print(json.dumps(result, indent=2, default=str) if args.json
          else render(result, root))
    return 1 if result["lost"] else 0


if __name__ == "__main__":
    sys.exit(main())
