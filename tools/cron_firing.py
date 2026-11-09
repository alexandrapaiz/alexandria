#!/usr/bin/env python3
"""A cron slot whose run produced nothing is a lost cycle, and it says so.

    python3 tools/cron_firing.py                        # today, every seat
    python3 tools/cron_firing.py --day 2026-10-25
    python3 tools/cron_firing.py --seat alexandria-engineer
    python3 tools/cron_firing.py --json                  # the verdict as a script reads it
    python3 tools/cron_firing.py --root /path/to/logs    # for tests and for other hosts
    gh pr list --state all --limit 200 \
      --json number,url,headRefName,createdAt > /tmp/prs.json
    python3 tools/cron_firing.py --prs /tmp/prs.json      # settles a cut-off run's shipping
    python3 tools/cron_firing.py --claims /path/to/capacity-retry.json  # default: the host's

Exit 0 when every cron slot that came due on the day either shipped something,
was rescued by HQ's retry, or was never on the clock. Exit 1 when one fired
and produced nothing, which is the thing this file exists to make visible.

**The population is the runs the host logged, and not the slots that came due**
(added 2026-11-02 by the security seat). Every reading here starts from
`/srv/asc/state/.epito/logs/<seat>/`, which holds a file only when a run
actually started. A cron slot that fired and started no run leaves no log
behind, so it is not scored `lost` and it is not scored at all. The host's own
audit log records that case as `{"action": "cron", "coalesced": true}`, and it
has happened 17 times, 10 of which never produced a cron run afterwards. Three
of those were on 2026-11-02 and two were on seats whose period is a week:
alexandria-exo's 01:00Z weekly cycle, and ursa-security's 01:15Z weekly
security sweep. This file printed neither, and on that day it printed two other
losses and exited 1, so the day read as measured rather than as partly unread.
Closing the gap means enumerating the declared slots from the roster manifests
instead of inferring them from history, which is a change of input rather than
a correction and sits in docs/ideas.md as `proposed`.

**And that gap is closed below rather than only described**, by the ExO seat on
the same night and from the other side of the same pair of notes: `--audit`
reads those `{"action": "cron", "coalesced": true}` rows and `coalesced` is a
state here now. The security seat's own proposal — enumerate the declared slots
from the roster manifests instead of inferring them from history — is a
different and larger repair, is still right, and is still `proposed` in
`docs/ideas.md`: it would also fix the `unseen` rows that name a seat's *old*
slot minute after its clock moved, which `coalesced` does not touch.

And a slot can fire and produce nothing without ever starting a run, which is
`coalesced` below and which this file could not see until 2026-11-02 because it
read only per-run logs. Three weekly slots went that way in one half hour on
the night it was found, and the only surface that records them is the audit
log, hence `--audit`.

A seat being revived is not the same as a cycle being carried, and `orphaned`
is the gap between them. HQ's retry re-fires a refused seat once per window and
the claim file names the window's *last* refused log for that seat, so a window
that refuses a seat several times leaves every earlier refusal unclaimed. The
seat comes back, the re-fire's wake text names the claimed log, and the cycle
refused earlier in the same window is handed to nobody. Measured on
2026-10-27's 01:03-01:46Z window: 20 seats, 20 claims, 46 refused runs, and in
16 of the 20 the claim named a turn-1 refusal while the run that had been cut
mid-work carried between 15 and 201 turns.

A refused slot is not the same as a lost one. HQ's retry re-dispatches a
refused log as a `hook`, so the firing record shows a failed `cron` row and a
successful `hook` row with nothing joining them, and the join key is the log
filename in `capacity-retry.json`. Reading the record without that file scores
every re-fired slot as a lost cycle; it did exactly that to research's
2026-10-26T16:30Z slot on the first day a class-A slot came due, and that slot
had shipped and merged.

`--prs` only settles runs in the repository the list came from. A cross-repo
row is resolved from its own trailer or not at all.

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
    with it: `monthly-spend`, `weekly-limit` and `session-limit` are the
    provider's three refusals, which arrive as the same `429` and are told
    apart only by the sentence in the result, and the monthly one has to be
    tested first because its sentence names the weekly reset inside itself
    (see `classify_refusal`). `api-error` is any other error status, `nonzero-exit` is a run
    that failed without one, and `silent` is the worst of the five, a run that
    exited 0 and shipped nothing anyway. That last one is incident 3's failure
    mode and the reason the ship-first rule is in every charter.

`recovering`
    The slot was refused, HQ's retry claimed the log, and the re-fire it
    dispatched **has not finished**. Its trailer is missing, so its `pr=-` is
    the absence of a report and not the absence of a pull request. Never
    reported as lost and never in the exit code, for the same reason
    `reason_of` will not call a live run lost: the cost of a false alarm is
    every reading of the report, and the cost of waiting is one reading.
    Observed on 2026-11-01 against `alexandria-security`, whose 13:00Z slot
    was scored `1 cycle(s) lost` at 23:34Z while the re-fire that rescued it
    had been committing to pull request 657 since 23:06Z.

`coalesced`
    The slot fired and the host started no run for it, because a run of that
    seat was already going, so it folded the firing into that one. **This state
    is read from the audit log and not from a log**, and it has to be: a
    coalesced slot writes no run log, so every other state here is blind to it
    and the slot is not reported as anything at all. Found 2026-11-02 by
    alexandria/security on this file and by alexandria/exo on HQ's
    `tools/check-cron-fired.py`, which counts coalesced slots in its header and
    then omits them from `findings()`. Both instruments called that night clean
    of a class that took three weekly cycles from it, one of them the cycle of
    the seat that found it.

    A coalesced firing the host later dispatched is **not** this state. The host
    holds the firing and starts it the instant the in-flight run ends, so
    `ursa-exo` coalesced at 01:30:23Z and ran at 01:40:48.770Z and lost nothing
    but ten minutes; `alexandria-exo` coalesced at 01:00:20Z and the dispatch
    that followed its run was a `message`. Those rows are identical in the
    audit log. The discriminator is whether a later `cron` run of that seat
    starts at all, and where one does, the deferral is attached to that run's
    own finding — which also corrects that finding's slot label, because it was
    being reported at the minute it was dispatched rather than the minute it
    was due.

`unseen`
    A slot this seat has fired at on other days in the history window, with no
    row on the day asked about. This is **never reported as a failure**, because
    a clock that was retired and a clock that did not fire leave the same
    absence, and this file cannot tell them apart. It is reported as a question
    carrying the evidence that formed it: the days the slot did fire. A seat
    that reads it can go and look.

    The slot label is therefore the clock this seat was observed on and not the
    clock it declares. For a weekly seat with one firing in the window the two
    can differ by hours: on 2026-11-02 this file named `ursa-security 15:15Z`
    from a single 2026-10-25 firing, while that seat's manifest declares
    `15 1 * * 1`, which is 01:15Z. Nothing here reads a manifest, so a reader
    who needs the declared clock has to go to the roster for it.

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
#
# **And `exit` is not always a number.** When the host kills a run on the wall
# clock it writes `# exit=timeout pr=- session=- turns=-`, and until 2026-11-02
# this pattern accepted digits only. So the one trailer that proves a run is
# dead was the one trailer this reader could not see, and a run killed on
# timeout was indistinguishable from a run still working for the whole
# `GRACE_MINUTES` window. Measured on security's 2026-11-01T23:04:44Z re-fire:
# the trailer said `exit=timeout`, the reader said "which is still running",
# and the draft check below could not fire because `recovering` outranks it.
# `exit_code` stays an int or None, because every caller compares it to 0;
# the word goes in `exit_word`, and `ended` is what says a trailer was found.
_TRAILER = re.compile(
    r"^#\s+exit=(?P<exit>-?\d+|[A-Za-z]\w*)\s+pr=(?P<pr>\S+)"
    r"(?:\s+session=(?P<session>\S+))?(?:\s+turns=(?P<turns>\d+|-))?")

LOG_ROOT = pathlib.Path("/srv/asc/state/.epito/logs")

# HQ's capacity retry keys its claims by log filename, so a refused run whose
# log appears here did not lose its cycle: it handed it to a named successor.
# Reading the firing record without this file scores every re-fired slot as a
# lost cycle, which is what it did to research's 2026-10-26T16:30Z slot on the
# first day one of them came due.
CLAIM_FILE = pathlib.Path("/srv/asc/state/.epito/capacity-retry.json")

# The audit log, which is the ONLY surface that records a coalesced firing.
# Everything else in this file reads per-run logs, and a coalesced slot starts
# no run, so it writes no log: it is not `lost`, not `unseen`, not any state —
# it has no row at all. See `read_coalesced`.
AUDIT_FILE = pathlib.Path("/srv/asc/state/.epito/audit.jsonl")

# ...and it is the sibling of the log root, which is how `--audit` defaults.
# Deriving it from `--root` rather than hard-coding the host path is not
# tidiness: a default that reads `/srv/asc/state` no matter what `--root` says
# makes every test in tests/test_cron_firing.py read the real host, which is
# the one thing that file's docstring says it never does. Eleven of them went
# red the first time this default was a constant.
AUDIT_BESIDE_LOGS = "audit.jsonl"

# How long after a run starts its missing trailer still means "working"
# rather than "killed". See `verdict_of`.
GRACE_MINUTES = 90

# How long a run can plausibly still be the one that opened a given pull
# request. See `resolve_shipped`. Four hours is bounded by the provider's own
# session window, which is five hours: a run cut off by the session limit
# cannot have been running longer than the session it exhausted.
MAX_RUN_HOURS = 4

UTC = timezone.utc


def classify_refusal(result_text, api_error_status, stop_reason=None):
    """Which of the provider's refusals stopped this run, if one did.

    Three of them are limits, and the count is three rather than two because
    two seats found a class each and this docstring is the merge of both. All
    three limits arrive as `api_error_status: 429` and the only discriminator
    is the sentence, which is the finding
    `INC-2026-10-25-the-weekly-slot-is-scheduled-inside-the-hours-the-weekly-provider-budget-is-spent`
    turns on. A weekly limit resets at a week boundary and a session limit
    resets in hours, so reading them as one refusal makes a lost week look
    like a lost hour.

    **There are three limits and not two, and the third one spent six days
    wearing the second one's name** (2026-11-08, engineer seat,
    `INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days-because-its-sentence-ends-by-naming-the-weekly-reset`).
    The org's monthly spend cap refuses with

        You've hit your org's monthly spend limit · ask your admin to raise it
        at claude.ai/admin-settings/usage · your weekly limit resets Nov 8,
        11pm (UTC)

    and that sentence contains the word `weekly` in its closing clause, so the
    substring test below returned `weekly-limit` for every one of them. 257
    refusals across the portfolio's six dark days of 2026-11-03 to 2026-11-08
    were filed as the weekly pool running out when the weekly pool was not
    what refused them. The costly part is the remedy: a weekly pool is
    rationed by moving slots and lowering burn, which is what every surface
    here proposed, and a monthly spend cap is raised in the org's admin
    settings by the owner and is untouched by any amount of rescheduling.

    So `monthly-spend` is tested first, because it is the only one of the
    three whose sentence names another limit inside itself. The order is the
    fix, and a test pins it.

    The third is not a limit and it is why `stop_reason` is read here
    (security seat, 2026-11-02,
    `INC-2026-11-02-a-content-safeguard-refusal-is-not-capacity-and-waiting-for-it-to-clear-waits-forever`).
    A content safeguard declines the message itself: this seat's 03:48:09Z run
    stopped at turn 17 with `stop_reason: "refusal"`, `terminal_reason:
    "api_error"`, a sentence naming the provider's use policy and the
    classifier `[bio]`, and **`api_error_status: null`**. So the 429 gate above
    returned None, `reason_of` fell through to `nonzero-exit`, and a refusal by
    the provider was reported in the same word as this seat's own crash.

    Keeping it apart from the limits is the whole point rather than tidiness.
    A limit clears by waiting and the provider says when; a safeguard refusal
    has no reset, and its own guidance is to rephrase or change model. An hour
    of waiting buys a limit its reset and buys this nothing, so a reader who
    cannot tell them apart holds a slot for a window that never comes.
    """
    if stop_reason == "refusal":
        return "safeguard-refusal"
    if api_error_status != 429:
        return None
    text = (result_text or "").lower()
    if "monthly" in text or "spend limit" in text:
        return "monthly-spend"
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
        "exit_word": None,
        "ended": False,
        "pr": None,
        "turns": None,
        "api_error_status": None,
        "refusal": None,
        "refusal_text": None,
        "truncated": True,
        "retry_claimed": False,
        "retried_by": None,
        "retry_of": None,
        "orphaned_behind": None,
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
            run["ended"] = True
            word = trailer["exit"]
            if word.lstrip("-").isdigit():
                run["exit_code"] = int(word)
            else:
                run["exit_word"] = word
            run["pr"] = None if trailer["pr"] == "-" else trailer["pr"]
            # `turns=-` rides along with `exit=timeout`: the host has no count
            # to write for a run it killed. Absent and unknown are the same
            # thing here, and both are None rather than zero.
            run["turns"] = (int(trailer["turns"])
                            if (trailer["turns"] or "-").isdigit() else None)
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
                result.get("result"), result.get("api_error_status"),
                result.get("stop_reason"))
            # The sentence as well as the class, because a weekly refusal
            # announces its own reset instant — `resets Nov 8, 11pm (UTC)` —
            # and that is the only authoritative statement of where the
            # provider cycle's boundary falls. `tools/provider_cycle.py` reads
            # it rather than assuming the Sunday rule.
            if run["refusal"]:
                run["refusal_text"] = result.get("result")

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


#: The tie-break below shells out to git, which is the only call in this file
#: that leaves the process. Thirty seconds rather than none, and the reason is
#: in `company_here`'s docstring.
COMPANY_PROBE_TIMEOUT = 30


def company_here(env=None, root=".", timeout=COMPANY_PROBE_TIMEOUT):
    """Which company's checkout this is, for disambiguating a bare seat name.

    Not a guess about which seat is meant. It is only a tie-break, and only
    between directories that all genuinely exist, so the worst it can do is
    prefer the company whose repository the reader is standing in.

    **The git probe is bounded, and a failed probe is not an answer** (added
    2026-11-09 by the security seat, running its own class inward). Three
    things were wrong with the call this replaces, and all three are the class
    this seat reported against two other seats' tools the same evening.

    It had no timeout, so a hung git stalled every caller for as long as git
    chose. Reproduced with a hanging `git` on `PATH`: the old call was still
    waiting when an eight-second external clock killed it at exit 124, which
    is the same word the host writes for the sixty-minute wall.

    It had no handler, so a host with no `git` binary raised `FileNotFoundError`
    out of a tie-break and took the whole tool down with a traceback.

    And it read `proc.stdout if proc.returncode == 0 else ""`, which is the
    half that matters, because that turns every way the probe can fail into the
    one answer "this checkout has no origin". A failed probe is the tool saying
    nothing, and the empty string is the tool saying something. So the probe
    now returns None when it could not look, and the caller falls back to the
    declared default rather than to an empty company name.

    This path is the live path on this host rather than the fallback: the seats
    left GitHub Actions on 2026-10-17, so `GITHUB_REPOSITORY` is unset and the
    probe runs on every call that gets this far.
    """
    env = os.environ if env is None else env
    named = env.get("ASC_COMPANY")
    if named:
        return named
    repo = env.get("GITHUB_REPOSITORY") or ""
    if not repo:
        probed = _probe_origin(root, timeout)
        if probed is None:
            # Could not look, which is not the same as looking and finding a
            # company. The caller gets None and declines to tie-break, which
            # is what the old empty string did in effect and could not say.
            return None
        repo = probed
    name = repo.rstrip("/").rsplit("/", 1)[-1]
    name = name[:-4] if name.endswith(".git") else name
    return name or None


def _probe_origin(root, timeout=COMPANY_PROBE_TIMEOUT):
    """`origin`'s URL, or None when the question could not be asked.

    None is returned for every shape of could-not-look, and they are listed
    here rather than collapsed in silence: a timeout, a missing git binary, any
    other OSError on the exec, and git exiting non-zero because `root` is not a
    checkout or has no `origin`. The last of those is genuinely git answering
    "no origin", and it is folded in with the rest on purpose, because the
    caller's only use for either is to stop tie-breaking.

    What is not folded in is the empty string. A caller that reads "" as a
    company name has been handed the instrument's failure as a fact about the
    world, and that is the conflation this function exists to refuse.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", root, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"cron_firing: git did not answer within {timeout}s, so the "
              f"company tie-break is skipped rather than guessed",
              file=sys.stderr)
        return None
    except OSError as exc:
        print(f"cron_firing: could not run git ({exc}), so the company "
              f"tie-break is skipped rather than guessed", file=sys.stderr)
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


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
        here = company if company is not None else company_here()
        # `here` of None is `company_here` saying it could not look, and that
        # is read here rather than formatted into a prefix. An unanswerable
        # tie-break is a collision, which is what this raise already says.
        if here:
            mine = f"{here}-{seat}"
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


def read_coalesced(path=AUDIT_FILE, seat=None, day=None):
    """Cron firings the host folded into a run of the same seat already going.

    This is the blind spot the rest of this file cannot see from where it
    stands. Every other state here is derived from a per-run log, and the host
    writes a log when it starts a run; when a slot comes due while that seat is
    already running, the host records the firing and starts nothing, so the
    slot leaves no log and no reader below ever asks about it. It is not
    reported as `lost`, and it is not even reported as `unseen`, because
    `unseen` is itself derived from log history.

    The audit log carries it, on the firing's own row, as `coalesced: true`.
    That field is also what HQ's `tools/check-cron-fired.py` counts, and that
    gate prints the count and then omits it from `findings()`, so both
    instruments were blind to the same slots from opposite sides. Measured
    2026-11-02T03:50Z: three weekly slots coalesced in the 01:00-01:30Z half
    hour, `alexandria-exo`, `ursa-security` and `ursa-exo`, and this file named
    two unrelated losses and exited 1 without mentioning any of them.

    Returns `[{"seat", "minute", "at", "when"}]` for `day`, oldest first. A missing or
    unreadable audit log is an empty reading rather than a traceback, for the
    same reason a missing log root is: a pull request checkout has neither, and
    a could-not-look must not read as a finding of nothing.
    """
    path = pathlib.Path(path)
    out = []
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return out
    for line in text.splitlines():
        if '"coalesced"' not in line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if row.get("action") != "cron" or not row.get("coalesced"):
            continue
        stamp = _parse_iso((row.get("ts") or "").replace("Z", "+00:00"))
        if stamp is None:
            continue
        name = row.get("agent") or ""
        if seat and name != seat:
            continue
        if day and stamp.strftime("%Y-%m-%d") != day:
            continue
        out.append({"seat": name, "minute": stamp.hour * 60 + stamp.minute,
                    "at": stamp.strftime("%H:%M:%SZ"), "when": stamp})
    out.sort(key=lambda row: (row["at"], row["seat"]))
    return out


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
    failure mode. A run that was refused, errored, exited non-zero, was killed
    on the wall clock or left no trailer at all was stopped, and under the
    ship-first rule its draft pull request is more likely open than not, so
    `pr=-` is evidence of nothing.

    **The wall kill is named separately above because it is the case this
    docstring used to describe wrongly** (security seat, 2026-11-02). The old
    wording offered "left no trailer at all" as the stopped-run case, and a
    reader carried that into an ask to HQ as "a wall kill writes no trailer".
    It does write one. Measured over every log this host holds: 36 of 36
    `exit=timeout` runs end with `# exit=timeout pr=- session=- turns=-`, so
    the trailer is present and it is the three fields that are placeholders.
    The code below has always been right about this, because `exit=timeout`
    leaves `exit_code` None and the final clause then fails, but the prose
    said something the code does not do. The empty half of a killed run's log
    is the body between the `---` fences, not the trailer.

    A run with a url needs no judgement, which is why that case answers True:
    there is no absence to weigh.
    """
    if run["pr"]:
        return True
    if run["truncated"]:
        return False
    if run.get("retry_of"):
        # The third reason for `pr=-`, found on 2026-10-27 and not in the two
        # above: the run shipped and the host's scraper did not find the url in
        # its final answer. `alexandria-writer`'s re-fire of the 2026-10-26
        # 16:00Z slot exited 0 after 124 turns with `pr=-`, and had opened
        # #591 on a branch named `2026-10-26-hook-refired-slot`.
        #
        # This stays narrow on purpose. A run known to be re-firing a refused
        # slot is performing a cycle under the ship-first rule, so a pull
        # request of that seat inside its window belongs to it. Widening the
        # same reasoning to every exit-0 run would dissolve `silent`, which is
        # the state incident 3 exists to keep visible.
        #
        # THE PREMISE ABOVE IS FALSE AND THE WIDENING WAS THE WRONG REMEDY TO
        # REACH FOR (security seat, 2026-11-02,
        # `INC-2026-11-02-a-clean-exit-0-run-names-no-pull-request-and-the-settlement-is-gated-off`).
        # `retry_of` was added because a re-fired run shipped without saying
        # so, and the case was read as something re-firing does. It is not.
        # Two runs of this seat on 2026-11-02 exited 0 at 104 and 80 turns,
        # wrote a complete final answer, re-fired nothing, and named neither
        # of the pull requests they had opened (#715, since merged, and #724)
        # because their closing prose wrote `#715` rather than a url. Whether
        # a run names its pull request is a property of its prose, not of how
        # it stopped, so no predicate over exit codes can recover it.
        #
        # So this function is deliberately left as it is. It answers the
        # question it is asked -- is the absence, on its own, evidence -- and
        # for a caller holding no better evidence the answer is still yes.
        # The repair belongs in `resolve_shipped`, which does hold better
        # evidence and used to skip these runs before consulting it.
        return False
    return (not run["refusal"]
            and not run["api_error_status"]
            and run["exit_code"] == 0)


# Branch prefixes no rule derives from the seat directory name. One entry is
# not a pattern; `index_is_blind_to` is what catches the second one.
ALIASES = {"alexandria-security": {"sec"}}


def _branch_prefixes(seat):
    """The branch prefixes a seat's own pull requests use.

    Seat directories are named `alexandria-engineer` and today's branches are
    `alexandria-engineer/2026-10-26-hook`, but the convention in this
    repository's history is the bare role, `engineer/2026-10-18-slug`, and both
    are still in the pull request list. Matching on either is what makes a
    reading of an older day work.

    A third form exists and no rule derives it. The security seat's branches
    are `sec/2026-11-01`, not `alexandria-security/` and not `security/`, so
    the two prefixes above are both blind to the only pull request that seat
    has ever opened. On 2026-11-01 that blindness produced a verdict rather
    than a question: the re-fire of security's 13:00Z slot had opened #657
    twenty minutes before the reading, and this file reported that it "opened
    no pull request either, so the cycle is lost after a recovery attempt."
    The answer happened to be right for another reason -- #657 was left a
    draft by a run that exited 124 -- which is the worst way for an instrument
    to be wrong, because nothing finds it until the day the answer differs.

    `ALIASES` is a maintained list and maintained lists rot, so it is not the
    remedy here; it is the repair of one instance. The remedy is
    `index_is_blind_to` below, which costs nothing to keep true and fires for
    the next seat whose convention nobody wrote down.
    """
    prefixes = {seat}
    if "-" in seat:
        prefixes.add(seat.split("-", 1)[1])
    prefixes |= ALIASES.get(seat, set())
    return prefixes


def index_is_blind_to(seat, pr_index):
    """Does the pull request list carry any branch at all for this seat?

    "This seat opened no pull request" and "I cannot see this seat's branches"
    are different claims, and only the first is evidence. The file already
    draws exactly this distinction for the firing record, where a slot with no
    row is `unseen` rather than failed, because a retired clock and a clock
    that did not fire leave the same absence. A pull request index that knows
    no branch of a seat's is the same absence one surface over, and until
    2026-11-02 this file read it as the other thing.
    """
    if not pr_index:
        return False
    prefixes = _branch_prefixes(seat)
    for entry in pr_index:
        branch = entry.get("headRefName") or ""
        if any(branch.startswith(f"{prefix}/") for prefix in prefixes):
            return False
    return True


def resolve_shipped(runs, pr_index, max_run_hours=MAX_RUN_HOURS):
    """Fill in the pull request a cut-off run opened and never got to name.

    `pr_index` is what `gh pr list --json number,url,headRefName,createdAt`
    prints, which is a list of dicts. A pull request belongs to a run when its
    branch carries the seat's prefix and it was created after that run started
    and before whichever came first: the seat's next run, or `max_run_hours`.
    Both bounds are needed. The next run is the tight one and it does not exist
    for the newest run of a seat, which is exactly the run a reading of today
    asks about.

    A run whose absence is not evidence is settled outright, as before. A run
    whose absence *is* evidence keeps its `silent` verdict and now also
    records `pr_candidate`, which is the thing this function used to compute
    and throw away: a pull request of this seat created inside this run's
    window. Nothing is reclassified by it. The point is that `silent` stops
    being reported with a confidence nothing behind it has.

    WHY IT IS NOT A STRAIGHT SETTLEMENT (security seat, 2026-11-02,
    `INC-2026-11-02-a-clean-exit-0-run-names-no-pull-request-and-the-settlement-is-gated-off`).
    The scraper misses a clean run's pull request often, because a clean run
    writes a closing summary and a summary is free to say `#715` instead of a
    url. Measured on this host: 21 alexandria cron and hook runs are classed
    `silent` with a pull request of their own seat in their window, two of
    them merged (#645, #660), and 78 rows fleet-wide are eligible. So the gate
    is wrong often. But the obvious repair -- delete the gate and settle these
    the same way -- was tried here and backed out, because
    `test_a_silent_run_stays_silent_even_with_the_list` is not a restatement
    of the gate. It forbids lending one run's pull request to another, and the
    branch name cannot tell those apart: #530 is a `cron` run's pull request
    on a branch named `...-2026-10-26-message`, so a trigger-word check that
    looks principled declines correct attributions. A timestamp inside a
    window is not enough evidence to overturn incident 3's failure mode, and
    it is ample evidence to stop asserting the opposite.

    A reading with no index is untouched: `pr_index` empty returns early one
    line below. Nothing here is a fallback for a trailer that already has a
    url; a url the host wrote is better evidence than a timestamp match.
    """
    if not pr_index:
        return runs
    by_seat = {}
    for run in runs:
        by_seat.setdefault(run["seat"], []).append(run)

    for seat, seat_runs in by_seat.items():
        seat_runs.sort(key=lambda r: r["started"])
        blind = index_is_blind_to(seat, pr_index)
        if blind:
            for run in seat_runs:
                run["pr_index_blind"] = True
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
            if run["pr"]:
                # The host already named it, and that beats a timestamp match.
                continue
            opens = run["started"]
            closes = opens + timedelta(hours=max_run_hours)
            if index + 1 < len(seat_runs):
                closes = min(closes, seat_runs[index + 1]["started"])
            settles = not pr_absence_is_evidence(run)
            for created, entry in candidates:
                if opens <= created < closes:
                    url = entry.get("url") or f"#{entry.get('number')}"
                    if not settles:
                        # The run stopped on its own terms, so the absence is
                        # evidence and this match does not get to overturn it.
                        # But it is not nothing either, and the old code threw
                        # it away before anybody saw it. Recording it is the
                        # whole repair: `silent` keeps its meaning, and a
                        # reader is told that a pull request of this seat sits
                        # inside this run's window and wants a human.
                        run["pr_candidate"] = url
                        run["pr_candidate_branch"] = (
                            entry.get("headRefName") or "")
                        break
                    run["pr"] = url
                    run["pr_source"] = "pull request list"
                    # A draft is not a shipped cycle. `isDraft` is absent from
                    # an index built without it, and an absent field is read as
                    # unknown rather than as false, which is the same rule the
                    # claim file is read by.
                    if entry.get("isDraft") is True:
                        run["pr_is_draft"] = True
                    break
    return runs


def read_retry_claims(path=CLAIM_FILE):
    """`{seat: {log filename, ...}}` from the retry's claim file, or `{}`.

    The file is the host's and is absent on a pull request checkout, so a
    missing file is the ordinary case and not an error. Everything downstream
    degrades to the pre-retry reading when this is empty, which is the old
    behaviour and is wrong only for slots the retry actually claimed.
    """
    try:
        raw = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(raw, dict):
        return {}
    claims = {}
    for seat, names in raw.items():
        if isinstance(names, str):
            names = [names]
        if not isinstance(names, list):
            continue
        claims[seat] = {str(name) for name in names}
    return claims


def resolve_retried(runs, claims):
    """Point each claimed run at the run that re-fired it.

    A claimed run gets `retry_of` on its successor and `retried_by` on itself,
    and the successor is the seat's **next `hook` run**. That is what the retry
    is: it re-dispatches a refused log and the host records the re-dispatch as
    `hook`, never as the original trigger, so the firing record shows a failed
    `cron` row and a successful `hook` row with nothing joining them.

    The successor is required to be a `hook` rather than merely the next run,
    because a seat this busy takes message wakes in between and crediting a
    slot with an unrelated wake's pull request would be the same error in the
    generous direction. When no hook follows, the claim is recorded and no
    successor is named, so the slot stays lost with the claim stated.
    """
    if not claims:
        return runs
    by_seat = {}
    for run in runs:
        by_seat.setdefault(run["seat"], []).append(run)

    for seat, seat_runs in by_seat.items():
        claimed = claims.get(seat)
        if not claimed:
            continue
        seat_runs.sort(key=lambda r: r["started"])
        for index, run in enumerate(seat_runs):
            if f"{run['run_id']}.log" not in claimed:
                continue
            run["retry_claimed"] = True
            successor = None
            for candidate in seat_runs[index + 1:]:
                if candidate["trigger"] != "hook":
                    continue
                successor = candidate
                run["retried_by"] = candidate
                candidate["retry_of"] = run["run_id"]
                break
            # The claim file holds at most one entry per seat per window and it
            # is the seat's *last* refused log, so a window that refuses a seat
            # several times leaves every earlier refusal unclaimed. Walk back
            # over them while the seat never recovered in between: those runs
            # were refused by the same window and the same single re-fire
            # revived the seat, but the re-fire was dispatched for this log and
            # its wake text names this log, so nobody was told to carry theirs.
            for earlier in reversed(seat_runs[:index]):
                if not earlier["refusal"]:
                    break
                if earlier["retry_claimed"]:
                    break
                earlier["orphaned_behind"] = run["run_id"]
                if successor is not None:
                    earlier["retried_by"] = successor
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
    # A trailer whose exit is a word is a run the host stopped, not a run that
    # stopped on its own terms, and falling through to None here would read
    # `exit=timeout` as a clean finish. The word is the reason, so it is
    # returned as the reason.
    if run.get("exit_word"):
        return run["exit_word"]
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


def judge(runs, day, tolerance=15, history_days=14, now=None, pr_index=None,
          claims=None, coalesced=None):
    """What every cron slot that came due on `day` did, in the four states.

    `tolerance` is how many minutes apart two firings can be and still be the
    same slot. The host's own record is tight, 11:06:03 against 11:06:07 on
    consecutive days, so fifteen minutes is loose enough to absorb a queue and
    far short of the twelve hours between this seat's two slots.

    `pr_index` is optional and it is what settles a cut-off run: without it a
    run whose trailer says `pr=-` for a reason that is not evidence is reported
    as lost with that doubt stated, and with it the same run is reported as
    `cut` naming the pull request it opened.

    `coalesced` is `read_coalesced`'s rows and it is the one input here that
    does not come from a log, because the slots it describes have none. Without
    it this function cannot report them at all — not as lost and not as a
    question — so a reading taken without it is silent about the whole class
    rather than uncertain about it.
    """
    # `resolve_retried` first, because it is what tells `resolve_shipped`
    # which runs are re-fires, and a re-fire's `pr=-` is not evidence.
    runs = resolve_retried(runs, claims or {})
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
        finding = {
            "seat": run["seat"],
            "slot": _slot_label(slot(run)),
            "state": state,
            "why": verdict,
            "run_id": run["run_id"],
            "turns": run["turns"],
            "pr": run["pr"],
            "pr_source": run.get("pr_source", "trailer" if run["pr"] else None),
            "pr_unknown": not pr_absence_is_evidence(run),
            "pr_candidate": run.get("pr_candidate"),
            "pr_candidate_branch": run.get("pr_candidate_branch"),
            "pr_index_blind": bool(run.get("pr_index_blind")),
            "pr_is_draft": bool(run.get("pr_is_draft")),
            "retry_claimed": bool(run.get("retry_claimed")),
            "retried_by": None,
            "retry_pr": None,
            "retry_pr_is_draft": False,
            "orphaned_behind": run.get("orphaned_behind"),
        }
        # A slot the retry claimed and re-fired successfully is not a lost
        # cycle. It is a late one, and the lateness is the finding rather than
        # the loss, so it gets its own state and does not set the exit code.
        successor = run.get("retried_by")
        if state == "lost" and successor is not None:
            finding["retried_by"] = successor["run_id"]
            finding["retry_pr"] = successor["pr"]
            finding["retry_pr_is_draft"] = bool(successor.get("pr_is_draft"))
            # L-A32: a gate cannot reach a draft, and GitHub refuses to merge
            # one at all. So a re-fire that opened a draft and stopped has not
            # carried the cycle, however complete its branch looks. Measured
            # on 2026-11-01: security's re-fire opened #657 and exited 124
            # before `gh pr ready`, and promoting on the pull request's
            # existence alone reported that cycle as arrived.
            if (run.get("retry_claimed") and successor["pr"]
                    and not successor.get("pr_is_draft")):
                finding["state"] = "retried"
                finding["late_minutes"] = int(
                    (successor["started"] - run["started"]).total_seconds() // 60)
            elif (run.get("retry_claimed")
                  and verdict_of(successor, now=now) == "in-flight"):
                # The re-fire is still running, so its `pr=-` is the absence of
                # a trailer and not the absence of a pull request. `reason_of`
                # already refuses to call a live run lost; that reasoning was
                # applied to the refused run's own verdict and never to its
                # successor's, so a slot in recovery scored `lost` and set the
                # exit code. The verdict here is owed at the next reading.
                finding["state"] = "recovering"
            elif run.get("orphaned_behind"):
                # The seat came back and this cycle did not. `orphaned` stays
                # in the exit code because the cadence did lose the cycle; what
                # changes is where the remedy goes, which is the claim's key
                # rather than the clock or the seat.
                finding["state"] = "orphaned"
        findings.append(finding)

    # A coalesced slot, from the audit log rather than from a log that does not
    # exist. This block comes before `unseen` on purpose: a minute this seat
    # has fired at on other days and coalesced on this one would otherwise be
    # folded into the `unseen` question, which says "no row today" about a slot
    # whose row is sitting in the audit log saying exactly what happened to it.
    #
    # AND A COALESCED SLOT IS NOT ALWAYS A LOST ONE, which is the half that
    # took a second reading to see. The host appears to hold the firing and
    # dispatch it the instant the in-flight run ends: `ursa-exo` coalesced at
    # 01:30:23Z on 2026-11-02 and a `cron` run of that seat started at
    # 01:40:48.770Z, three thousandths of a second after the run it was waiting
    # on ended. `alexandria-exo` coalesced at 01:00:20Z and the next dispatch
    # when its run ended was a `message`; `ursa-security` the same. So the
    # same audit row means deferred in one case and dropped in the other, and
    # nothing in the row says which — the discriminator is whether a later
    # `cron` run of that seat starts at all.
    for row in (coalesced or []):
        later = sorted((r for r in day_runs
                        if r["seat"] == row["seat"] and r["trigger"] == "cron"
                        and r["started"] > row["when"]),
                       key=lambda r: r["started"])
        if later:
            # Deferred, not lost. The carrying run already has a finding here
            # under the minute it was DISPATCHED at, which is not its slot:
            # that is how `ursa-exo` 01:30Z came to be reported as `01:40Z`,
            # a label with no cron line anywhere behind it. Correct the label
            # and attach the deferral rather than adding a second row about
            # one slot.
            carrier = later[0]
            late = int((carrier["started"] - row["when"]).total_seconds() // 60)
            for finding in findings:
                if (finding["seat"] == row["seat"]
                        and finding["slot"] == _slot_label(slot(carrier))):
                    finding["slot"] = _slot_label(row["minute"])
                    finding["coalesced_at"] = row["at"]
                    finding["deferred_minutes"] = late
                    break
            continue
        absorbing = [r for r in day_runs if r["seat"] == row["seat"]
                     and slot(r) <= row["minute"]]
        absorbing = max(absorbing, key=slot) if absorbing else None
        findings.append({
            "seat": row["seat"],
            "slot": _slot_label(row["minute"]),
            "state": "coalesced",
            "why": "fired, started no run, and no later cron run carried it",
            "at": row["at"],
            "absorbed_into": (f'{_slot_label(slot(absorbing))} '
                              f'{absorbing["trigger"]}') if absorbing else None,
        })

    fired = {(r["seat"], slot(r)) for r in day_runs if r["trigger"] == "cron"}
    seen = {}
    for run in history:
        seen.setdefault((run["seat"], slot(run)), []).append(run["day"])
    for (seat, minute), days in sorted(seen.items()):
        if any(s == seat and abs(m - minute) <= tolerance for s, m in fired):
            continue
        # Fold slots that are the same clock a minute apart into one question.
        if any(f["seat"] == seat and f["state"] in ("unseen", "coalesced")
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
        "orphaned": [f for f in findings if f["state"] == "orphaned"],
        "cut": [f for f in findings if f["state"] == "cut"],
        "retried": [f for f in findings if f["state"] == "retried"],
        "recovering": [f for f in findings if f["state"] == "recovering"],
        "coalesced": [f for f in findings if f["state"] == "coalesced"],
        "history_days": history_days,
    }


def _minute_of(label):
    return int(label[0:2]) * 60 + int(label[3:5])


def render(result, root, prs_given=False):
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
        elif finding["state"] == "retried":
            late = finding.get("late_minutes")
            late = f", {late // 60}h{late % 60:02d}m late" if late else ""
            lines.append(f"  retried  {finding['seat']} {finding['slot']} "
                         f"{finding['why']}, re-fired by "
                         f"{finding['retried_by']} -> {finding['retry_pr']}"
                         f"{late}. The slot fired, the provider refused it and "
                         f"the retry carried the cycle")
        elif finding["state"] == "recovering":
            lines.append(f"  recover  {finding['seat']} {finding['slot']} "
                         f"{finding['why']}, re-fired by "
                         f"{finding['retried_by']}, which is still running. "
                         f"Its `pr=-` is a missing trailer and not a missing "
                         f"pull request, so the cycle is in recovery and the "
                         f"verdict is owed at the next reading")
        elif finding["state"] == "orphaned":
            turns = finding["turns"]
            turns = f", {turns} turn{'' if turns == 1 else 's'}" if turns else ""
            lines.append(f"  orphaned {finding['seat']} {finding['slot']} "
                         f"{finding['why']}{turns}. The same window refused "
                         f"this seat again afterwards, the retry's claim named "
                         f"that later log ({finding['orphaned_behind']}) and "
                         f"not this one, so the re-fire arrived carrying the "
                         f"other run's instruction and nobody was told to "
                         f"carry this cycle")
        elif finding["state"] == "lost":
            turns = finding["turns"]
            turns = f", {turns} turn{'' if turns == 1 else 's'}" if turns else ""
            if finding["pr_unknown"]:
                # Two different absences, and telling a reader to pass a flag
                # they already passed sends them back to the step they just
                # took. Say which evidence is actually missing.
                if finding["retry_pr"] and finding["retry_pr_is_draft"]:
                    hint = (f"The retry re-fired it as {finding['retried_by']}, "
                            f"and that run opened {finding['retry_pr']} and left "
                            f"it a draft, which no gate can reach, so the cycle "
                            f"is owed by a branch that exists")
                elif finding["pr_index_blind"]:
                    hint = ("The pull request list carries no branch with this "
                            "seat's prefixes at all, so it is blind to this "
                            "seat and `pr=-` is not evidence either way. Add "
                            "the seat's real prefix to ALIASES")
                elif finding["retried_by"]:
                    hint = (f"The retry re-fired it as {finding['retried_by']}, "
                            f"and that run opened no pull request either, so "
                            f"the cycle is lost after a recovery attempt")
                elif finding["retry_claimed"]:
                    hint = ("The retry claimed this log and no hook followed "
                            "it, so the re-fire is owed and has not happened")
                elif prs_given:
                    hint = ("The run was stopped rather than finished, and no "
                            "pull request in the list matches its window, so "
                            "`pr=-` stands")
                else:
                    hint = ("The run was stopped rather than finished, so "
                            "`pr=-` is not evidence it shipped nothing. Pass "
                            "--prs to settle it")
                lines.append(f"  LOST?    {finding['seat']} {finding['slot']} "
                             f"{finding['why']}{turns}. {hint}")
            else:
                late = finding.get("deferred_minutes")
                deferred = (f", and the slot had coalesced at "
                            f"{finding['coalesced_at']} and was dispatched "
                            f"{late} minute(s) late" if late is not None else "")
                line = (f"  LOST     {finding['seat']} {finding['slot']} "
                        f"{finding['why']}{turns}, no pull "
                        f"request{deferred}")
                if finding.get("pr_candidate"):
                    # The verdict is unchanged and deliberately so, see
                    # `resolve_shipped`. What changes is that it stops being
                    # the only thing printed: the scraper reads a run's
                    # closing prose, a clean run is free not to quote a url,
                    # and this seat's own #715 and #724 of 2026-11-02 are
                    # what that looks like. A reader settling this opens the
                    # branch and looks.
                    line += (f". But {finding['pr_candidate']} "
                             f"({finding['pr_candidate_branch']}) was opened "
                             f"inside this run's window by this seat, and the "
                             f"host scrapes `pr=` out of a run's closing "
                             f"answer, so a clean run that wrote `#1234` "
                             f"rather than a url reads exactly like this. "
                             f"Settle it against the branch before you treat "
                             f"the cycle as lost")
                lines.append(line)
        elif finding["state"] == "coalesced":
            into = finding.get("absorbed_into")
            into = (f", which had started at {into}" if into
                    else ", and no log of this seat covers the minute")
            lines.append(f"  COALESCED {finding['seat']} {finding['slot']} "
                         f"fired {finding['at']} and started no run: the host "
                         f"folded it into a run already going{into}, and no "
                         f"later cron run of this seat carried it. The slot "
                         f"has no log, so every other reader here is blind to "
                         f"it")
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
    if result.get("orphaned"):
        lines.append("")
        lines.append(f"{len(result['orphaned'])} cycle(s) orphaned behind a "
                     f"later refusal of the same seat. The seat was re-fired "
                     f"once and came back; the cycle did not, because the "
                     f"claim file keys by log filename and holds the window's "
                     f"last refused log per seat. These count as lost, and the "
                     f"remedy is the claim's key rather than the clock or the "
                     f"seat.")
    if result.get("coalesced"):
        lines.append("")
        lines.append(f"{len(result['coalesced'])} slot(s) coalesced into a run "
                     f"already going. The clock fired and the slot's own work "
                     f"never started, so for a weekly seat the whole cycle is "
                     f"gone. These count as lost. Read from the audit log, "
                     f"because a coalesced slot writes no run log and HQ's "
                     f"`check-cron-fired.py` counts them and then omits them "
                     f"from `findings()`, so the day reads clean on both "
                     f"instruments.")
    if result.get("retried"):
        lines.append("")
        lines.append(f"{len(result['retried'])} cycle(s) refused and re-fired "
                     f"by HQ's retry. The clock worked, the provider did not, "
                     f"and the cycle arrived late rather than not at all. The "
                     f"firing record alone shows these as a failed cron row "
                     f"and an unrelated hook row.")
    if result.get("recovering"):
        lines.append("")
        lines.append(f"{len(result['recovering'])} cycle(s) in recovery: "
                     f"refused, claimed by HQ's retry, and re-fired by a run "
                     f"that has not finished. These do not count as lost, "
                     f"because the only evidence against them is a trailer "
                     f"nobody has written yet. Read the slot again once the "
                     f"re-fire ends.")
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
                        help="an ISO stamp that pins the clock a verdict is "
                             "reached at, which is not the day being read: "
                             "`--day` chooses that. The grace window in "
                             "`reason_of` makes one verdict a function of the "
                             "time of asking, so a reading that has to be "
                             "reproduced needs the clock pinned. Passing "
                             "`--now` alone still reads today, which the first "
                             "clause here used to claim otherwise")
    parser.add_argument("--prs", default=None,
                        help="a file of `gh pr list --json "
                             "number,url,headRefName,createdAt` output, which "
                             "settles whether a cut-off run shipped")
    parser.add_argument("--claims", default=str(CLAIM_FILE),
                        help="HQ's capacity-retry claim file, which says which "
                             "refused logs were re-fired. Without it a slot "
                             "the retry rescued reads as a lost cycle")
    parser.add_argument("--audit", default=None,
                        help="the host's audit log, which is the only surface "
                             "that records a cron slot the host folded into a "
                             "run already going. Without it this reading is "
                             "silent about that class rather than clean of it. "
                             "Defaults to `audit.jsonl` beside --root, which "
                             "is where the host keeps it")
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

    claims = read_retry_claims(args.claims)
    audit = pathlib.Path(args.audit) if args.audit else root.parent / AUDIT_BESIDE_LOGS
    coalesced = read_coalesced(audit, seat=seat, day=day)
    result = judge(runs, day, history_days=args.history_days,
                   pr_index=pr_index, now=now, claims=claims,
                   coalesced=coalesced)
    print(json.dumps(result, indent=2, default=str) if args.json
          else render(result, root, prs_given=pr_index is not None))
    # An orphaned cycle is a lost one, so it sets the exit code too. Before
    # `orphaned` existed these rows read as `lost` and already did, which is
    # why naming them changes the sentence and not the contract.
    #
    # A coalesced slot does change the contract, and that is the point: it is a
    # slot whose work never started, and before 2026-11-02 it set no exit code
    # anywhere, in this file or in HQ's gate. On the night it was found, this
    # file exited 1 for two unrelated losses while saying nothing about three
    # coalesced weekly slots, one of them this seat's own.
    return 1 if (result["lost"] or result["orphaned"]
                 or result.get("coalesced")) else 0


if __name__ == "__main__":
    sys.exit(main())
