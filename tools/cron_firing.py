#!/usr/bin/env python3
"""A cron slot that fired and produced nothing is a lost cycle, and it says so.

    python3 tools/cron_firing.py                        # today, every seat
    python3 tools/cron_firing.py --day 2026-10-25
    python3 tools/cron_firing.py --seat alexandria-engineer
    python3 tools/cron_firing.py --json                  # the verdict as a script reads it
    python3 tools/cron_firing.py --root /path/to/logs    # for tests and for other hosts
    gh pr list --state all --limit 200 \
      --json number,url,headRefName,createdAt > /tmp/prs.json
    python3 tools/cron_firing.py --prs /tmp/prs.json      # settles a cut-off run's shipping

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

`cut`
    The slot fired, the run opened a pull request, and something cut it off
    before it finished. The cycle delivered its work and did not deliver its
    report, which is a different thing from a lost cycle and has to be named
    separately, because the next run of the seat has to continue it rather
    than start it again.

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

## Why `pr=-` is not the same fact as "shipped nothing"

The trailer's pull request field is scraped from what a run says when it
finishes, so a run that never finishes never names its pull request and the
host writes `pr=-`. That absence is trustworthy for a run that ended under its
own control and worthless for a run that was cut off, and the ship-first rule
in every charter is what makes the difference matter: a seat opens its draft
pull request in its first few turns precisely so that a run dying at turn 90
still delivers.

This file's first version read `pr=-` as "no pull request" in both cases, and
the run that found it was its own. On 2026-10-26 at 00:31:38Z this seat's
message run opened pull request 530 at 00:33:05Z, built the day's work on it,
and was refused at turn 89 by the provider's session limit. Its trailer is
`# exit=1 pr=- session=5a660600 turns=89`. The first version called that a lost
cycle. The cycle had in fact shipped 1,849 lines, and the next run of the seat
read them and carried them forward, which is the ship-first rule working
exactly as written and an instrument that could not see it.

So the absence is only evidence when the run ended cleanly, which is
`pr_absence_is_evidence`. When it is not evidence, this file says so rather
than guessing, and `--prs` settles it from the pull request list the repository
can already produce.

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
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

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

# How long a run can plausibly still be the one that opened a given pull
# request. See `resolve_shipped`. Four hours is bounded by the provider's own
# session window, which is five hours: a run cut off by the session limit
# cannot have been running longer than the session it exhausted.
MAX_RUN_HOURS = 4

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


def days_back(day, count):
    """The day asked about and the `count` days before it, as name prefixes."""
    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=UTC)
    return {(start - timedelta(days=n)).strftime("%Y-%m-%d")
            for n in range(count + 1)}


class SeatNotFound(Exception):
    """A `--seat` value that names no directory in the host's roster.

    This exists because the alternative was answering it. Until this run
    `--seat research` and `--seat totallyfake` printed the same sentence, byte
    for byte: that no cron slot had fired and none had in the trailing 14 days.
    The research slot had fired on time the previous afternoon
    (`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`).

    The reason that is urgent rather than untidy is what this tool is for. The
    ExO seat's duty card instructs its next reader to read each slot here and
    never from the absence of a pull request, and that card exists because an
    earlier run nearly retired three working seats on a bad absence. On the one
    argument a reader supplies by hand, the remedy reproduced the failure it
    was built to prevent.

    So an unresolvable seat raises. An empty list is the right answer to "this
    seat did not fire" and the wrong answer to "there is no such seat," and
    those two were indistinguishable in the output.
    """


def seat_roster(root=LOG_ROOT):
    """The seat directory names the host has written logs for, sorted."""
    root = pathlib.Path(root)
    if not root.is_dir():
        return []
    return sorted(d.name for d in root.iterdir() if d.is_dir())


def company_here(env=None, root="."):
    """Which company's checkout this is, for disambiguating a bare seat name.

    Not a guess about which seat is meant. It is only a tie-break, and only
    between directories that all genuinely exist, so the worst it can do is
    prefer the company whose repository the reader is standing in.
    """
    env = os.environ if env is None else env
    named = env.get("ASC_COMPANY")
    if named:
        return named
    repo = env.get("GITHUB_REPOSITORY") or ""
    if not repo:
        proc = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                              capture_output=True, text=True)
        repo = proc.stdout.strip() if proc.returncode == 0 else ""
    name = repo.rstrip("/").rsplit("/", 1)[-1]
    return name[:-4] if name.endswith(".git") else name


def resolve_seat(seat, root=LOG_ROOT, company=None):
    """A `--seat` argument as a directory name, or `SeatNotFound`.

    The host names each directory `<company>-<seat>`, and the board, the duty
    register and all twelve charters name the seat alone. Both forms are in use
    by people reading this tool, so both resolve: an exact directory name
    first, then the bare seat name against the suffix after the first hyphen.

    Exact match wins over the suffix search, and it has to. This host carries a
    directory literally named `engineer` alongside `alexandria-engineer`,
    `atelier-engineer` and `epitome-engineer`, so a bare `engineer` is both an
    exact name and a four-way suffix collision. Resolving it to the thing the
    reader typed is the only reading that cannot surprise them.

    A suffix that matches more than one company is settled by the company whose
    checkout this is, and only by that: `--seat research` under
    `alexandrapaiz/alexandria` is `alexandria-research`, because the host also
    carries `ursa-research`. When the tie-break does not apply, the collision
    raises rather than being picked. A reader who typed `exo` from outside all
    four companies wants to be asked which, and a tool that guesses there is
    back to answering about a seat nobody named.
    """
    if seat is None:
        return None
    roster = seat_roster(root)
    if not roster:
        # No roster to resolve against, which is the unmounted-sandbox case
        # `read_runs` already answers with "observation skipped". Passing the
        # value through keeps that path intact instead of turning a missing
        # mount into a missing seat.
        return seat
    if seat in roster:
        return seat
    suffixed = [name for name in roster if name.partition("-")[2] == seat]
    if len(suffixed) == 1:
        return suffixed[0]
    if len(suffixed) > 1:
        mine = f"{company if company is not None else company_here()}-{seat}"
        if mine in suffixed:
            return mine
        raise SeatNotFound(
            f"{seat!r} is a seat in {len(suffixed)} companies here "
            f"({', '.join(suffixed)}): name one of those instead"
        )
    raise SeatNotFound(
        f"{seat!r} is not a seat the host has written logs for. The roster "
        f"under {root} is: {', '.join(roster)}"
    )


def read_runs(root=LOG_ROOT, seat=None, days=None):
    """Every run log under `root`, newest last. Missing root is not an error.

    A seat sandbox is not guaranteed to have the host's log directory mounted,
    and neither is a pull request check. Both get an empty list and a caller
    that can say "observation skipped" rather than a traceback.

    `days` is a set of `YYYY-MM-DD` prefixes, and a file outside it is skipped
    on its name without being opened. The archive on this host is 1,714 logs
    and 9.8 MB after five weeks and it only grows, so a reader that opens all
    of them to answer about one day gets slower every day it runs. The
    filename carries the date, which is the whole reason this is cheap.
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
            if days is not None and log.name[:10] not in days:
                continue
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


def pr_absence_is_evidence(run):
    """Does `pr=-` mean this run shipped nothing, or only that it never said.

    The host scrapes the pull request out of a run's final answer, so the field
    is absent for two different reasons and they need telling apart. A run that
    exited 0 with no error chose to stop, and if it had opened a pull request it
    would have named it, so `pr=-` is evidence: that is `silent`, incident 3's
    failure mode. A run that was refused, errored, exited non-zero or left no
    trailer at all was stopped, and under the ship-first rule its draft pull
    request is more likely open than not, so `pr=-` is evidence of nothing.

    A run with a url needs no judgement, which is why that case answers True:
    there is no absence to weigh.
    """
    if run["pr"]:
        return True
    if run["truncated"]:
        return False
    return (not run["refusal"]
            and not run["api_error_status"]
            and run["exit_code"] == 0)


def _branch_prefixes(seat):
    """The branch prefixes a seat's own pull requests use.

    Seat directories are named `alexandria-engineer` and today's branches are
    `alexandria-engineer/2026-10-26-hook`, but the convention in this
    repository's history is the bare role, `engineer/2026-10-18-slug`, and both
    are still in the pull request list. Matching on either is what makes a
    reading of an older day work.
    """
    prefixes = {seat}
    if "-" in seat:
        prefixes.add(seat.split("-", 1)[1])
    return prefixes


def resolve_shipped(runs, pr_index, max_run_hours=MAX_RUN_HOURS):
    """Fill in the pull request a cut-off run opened and never got to name.

    `pr_index` is what `gh pr list --json number,url,headRefName,createdAt`
    prints, which is a list of dicts. A pull request belongs to a run when its
    branch carries the seat's prefix and it was created after that run started
    and before whichever came first: the seat's next run, or `max_run_hours`.
    Both bounds are needed. The next run is the tight one and it does not exist
    for the newest run of a seat, which is exactly the run a reading of today
    asks about.

    Only runs whose absence is not evidence are resolved, so a `silent` run
    stays silent. Nothing here is a fallback for a trailer that already has a
    url; a url the host wrote is better evidence than a timestamp match.
    """
    if not pr_index:
        return runs
    by_seat = {}
    for run in runs:
        by_seat.setdefault(run["seat"], []).append(run)

    for seat, seat_runs in by_seat.items():
        seat_runs.sort(key=lambda r: r["started"])
        prefixes = _branch_prefixes(seat)
        candidates = []
        for entry in pr_index:
            branch = entry.get("headRefName") or ""
            if not any(branch.startswith(f"{prefix}/") for prefix in prefixes):
                continue
            created = _parse_iso(entry.get("createdAt"))
            if created is not None:
                candidates.append((created, entry))
        candidates.sort()

        for index, run in enumerate(seat_runs):
            if pr_absence_is_evidence(run):
                continue
            opens = run["started"]
            closes = opens + timedelta(hours=max_run_hours)
            if index + 1 < len(seat_runs):
                closes = min(closes, seat_runs[index + 1]["started"])
            for created, entry in candidates:
                if opens <= created < closes:
                    run["pr"] = entry.get("url") or f"#{entry.get('number')}"
                    run["pr_source"] = "pull request list"
                    break
    return runs


def _parse_iso(stamp):
    """`2026-10-26T00:33:05Z` as an aware datetime, or None.

    GitHub writes `Z` and `datetime.fromisoformat` did not accept it before
    3.11, so the replacement is not decoration.
    """
    if not stamp:
        return None
    try:
        return datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except ValueError:
        return None


def reason_of(run, now=None, grace_minutes=GRACE_MINUTES):
    """Why this run stopped, or None when it stopped on its own terms.

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

    This is separate from the verdict because a run can stop badly and still
    have shipped. Reading the two as one question is what made a cut-off run
    that opened a pull request indistinguishable from a cycle that produced
    nothing.
    """
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
    return None


def verdict_of(run, now=None, grace_minutes=GRACE_MINUTES):
    """`shipped`, `in-flight`, or the one word for why the run stopped.

    A run with a pull request and no reason to have stopped is `shipped`. A run
    with a pull request and a reason is reported under that reason, and `judge`
    reads the pair as `cut`: it delivered the work and not the report. A run
    with no pull request and no reason is `silent`, which is the worst state in
    the file and the one the ship-first rule exists to prevent.
    """
    reason = reason_of(run, now=now, grace_minutes=grace_minutes)
    if run["pr"]:
        return "shipped" if reason is None else reason
    return reason or "silent"


def judge(runs, day, tolerance=15, history_days=14, now=None, pr_index=None):
    """What every cron slot that came due on `day` did, in the four states.

    `tolerance` is how many minutes apart two firings can be and still be the
    same slot. The host's own record is tight, 11:06:03 against 11:06:07 on
    consecutive days, so fifteen minutes is loose enough to absorb a queue and
    far short of the twelve hours between this seat's two slots.

    `pr_index` is optional and it is what settles a cut-off run: without it a
    run whose trailer says `pr=-` for a reason that is not evidence is reported
    as lost with that doubt stated, and with it the same run is reported as
    `cut` naming the pull request it opened.
    """
    runs = resolve_shipped(runs, pr_index)
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
        state = {"shipped": "shipped",
                 "in-flight": "in-flight"}.get(verdict)
        if state is None:
            state = "cut" if run["pr"] else "lost"
        findings.append({
            "seat": run["seat"],
            "slot": _slot_label(slot(run)),
            "state": state,
            "why": verdict,
            "run_id": run["run_id"],
            "turns": run["turns"],
            "pr": run["pr"],
            "pr_source": run.get("pr_source", "trailer" if run["pr"] else None),
            "pr_unknown": not pr_absence_is_evidence(run),
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
        "cut": [f for f in findings if f["state"] == "cut"],
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
        elif finding["state"] == "cut":
            turns = finding["turns"]
            turns = f" at turn {turns}" if turns else ""
            lines.append(f"  cut      {finding['seat']} {finding['slot']} "
                         f"{finding['why']}{turns}, after opening "
                         f"{finding['pr']} ({finding['pr_source']}). The work "
                         f"shipped and the report did not")
        elif finding["state"] == "lost":
            turns = finding["turns"]
            turns = f", {turns} turn{'' if turns == 1 else 's'}" if turns else ""
            if finding["pr_unknown"]:
                lines.append(f"  LOST?    {finding['seat']} {finding['slot']} "
                             f"{finding['why']}{turns}. The run was stopped "
                             f"rather than finished, so `pr=-` is not evidence "
                             f"it shipped nothing. Pass --prs to settle it")
            else:
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
    if result.get("cut"):
        lines.append("")
        lines.append(f"{len(result['cut'])} cycle(s) cut off after shipping. "
                     f"The next run of that seat continues the open pull "
                     f"request rather than starting the work again.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--day", default=None,
                        help="YYYY-MM-DD, default today in UTC")
    parser.add_argument("--seat", default=None,
                        help="one seat, as the host's directory name "
                             "(`alexandria-research`) or as the bare seat name "
                             "the charters use (`research`); default every seat")
    parser.add_argument("--root", default=str(LOG_ROOT),
                        help="the host's log directory")
    parser.add_argument("--history-days", type=int, default=14,
                        help="how far back to look for a slot's other firings")
    parser.add_argument("--now", default=None,
                        help="an ISO stamp to read the day as of, rather than "
                             "the wall clock. The grace window in `reason_of` "
                             "makes one verdict a function of the time of "
                             "asking, so a reading that has to be reproduced "
                             "needs the clock pinned")
    parser.add_argument("--prs", default=None,
                        help="a file of `gh pr list --json "
                             "number,url,headRefName,createdAt` output, which "
                             "settles whether a cut-off run shipped")
    parser.add_argument("--json", action="store_true",
                        help="the verdict as a script reads it")
    args = parser.parse_args(argv)

    day = args.day or datetime.now(UTC).strftime("%Y-%m-%d")
    root = pathlib.Path(args.root)
    # Before any reading, because every verdict below is about a seat and a
    # verdict about a seat that does not exist is worse than no verdict.
    try:
        seat = resolve_seat(args.seat, root)
    except SeatNotFound as exc:
        print(f"cron_firing: {exc}", file=sys.stderr)
        return 2
    if seat != args.seat:
        print(f"note: reading {seat} for --seat {args.seat!r}", file=sys.stderr)
    runs = read_runs(root, seat=seat,
                     days=days_back(day, args.history_days))
    if not runs and not root.is_dir():
        message = (f"observation skipped: {root} is not a directory here, so "
                   f"this sandbox holds no firing record to read")
        print(json.dumps({"day": day, "why_skipped": message}, indent=2)
              if args.json else message)
        return 0

    pr_index = None
    if args.prs:
        try:
            pr_index = json.loads(pathlib.Path(args.prs).read_text())
        except (OSError, ValueError) as exc:
            # A bad index must not turn a reading into a traceback. The reading
            # without it is still correct, it is only less decided, and saying
            # so beats failing.
            print(f"note: --prs could not be read ({exc}), so a cut-off run "
                  f"stays unsettled", file=sys.stderr)

    now = _parse_iso(args.now) if args.now else None
    if args.now and now is None:
        print(f"note: --now {args.now!r} is not an ISO stamp, so the wall "
              f"clock stands", file=sys.stderr)

    result = judge(runs, day, history_days=args.history_days,
                   pr_index=pr_index, now=now)
    print(json.dumps(result, indent=2, default=str) if args.json
          else render(result, root))
    return 1 if result["lost"] else 0


if __name__ == "__main__":
    sys.exit(main())
