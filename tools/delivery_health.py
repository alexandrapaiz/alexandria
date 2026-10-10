#!/usr/bin/env python3
"""Delivery health: did the product reach a reader. Guardrail 4, as a command.

    python3 tools/delivery_health.py            # every surface, for a human
    python3 tools/delivery_health.py --json     # the same answer, for a script
    python3 tools/delivery_health.py --surface press

`docs/agents/delivery-health.md` was written on 2026-09-24 after incident 24, and it
says the right thing: read the artifact, not the scheduler. A scheduler reports
its own intentions. Guardrail 4 makes the PM's daily standup the outside
observer that catches a run which never started, and it names the evidence
exactly: the newest row in `digests`, the newest issue the live site publishes,
a probe of the MCP endpoint.

It was prose. Nothing executed it, and on 2026-09-28 the standup that was meant
to enforce it reported that it could not check the press because the seat had
no database credential, and reached instead for a proxy that cannot answer the
question at all: whether a commit had landed under `site/content/issues/`.
Nothing in this repository publishes a digest to the site. `site/lib/content.js`
reads hand-committed markdown and says so in its own comment. So the proxy
would have read the same on a perfect week as on a dead one.

That is incident 20's shape again, which `docs/agents/registers.md` names: a
register with a gate that decides something gets written down and no gate that
decides it gets checked. This file is the second gate.

## The three states, and why "unknown" is one of them

Every surface answers `ok`, `failing`, or `unknown`, and the third is not a
shrug. Guardrail 1 already draws this distinction for the press's own
availability check, in its own words: a network failure must raise rather than
return an empty set, because "the request failed" and "everything is gone" are
the same value and very different facts. A health check owes its reader the
same honesty about itself. A surface this environment holds no credential for
is `unknown`, it is never green, and it is never red either, because reporting
a healthy press as broken teaches the reader to ignore the report.

The exit status carries that distinction so a caller does not have to parse
prose:

    0   every surface checked is ok, and every surface could be checked
    1   at least one surface is failing
    2   nothing is failing, but at least one surface could not be answered

## What each surface needs

| Surface  | Evidence                                    | Needs    |
| ---      | ---                                         | ---      |
| press    | newest row in `digests`, against the week it | nothing  |
|          | owes by now, which on a Monday is not the    |          |
|          | week that has just ended until the cron runs |          |
| pipeline | newest rows in `papers` and `claims`, and the queue depth behind each | nothing  |
| site     | the issues `/library` actually publishes    | nothing  |
| mcp      | an unauthenticated probe of `/mcp`          | nothing  |
| deploy   | `deploy_runtime` against the trunk, never   | git      |
|          | against the branch this is run from         |          |

That column read `DATABASE_URL` for three of the six rows until 2026-10-01, and
the gap was not academic. No agent seat holds that credential, so every seat ever
asked whether the press printed answered `unknown`, and the ledger has carried
that as urgent since 2026-09-28. The fix is two readers for the same three
surfaces, in this order.

1. **A direct connection**, when `DATABASE_URL` is in the environment. That is
   the Modal jobs and the owner's own machine.
2. **The receipt the site publishes**, `site/app/api/delivery/route.js`, which
   needs no credential and is what every agent seat actually has. The site
   already holds `DATABASE_URL` in its own environment
   (`site/lib/graph-live.js`, `site/lib/entitlement.js`), so it is the one place
   in this company where the database and a public HTTP surface already meet.

The receipt carries rows and no verdicts, and the judgement stays here in one
copy: `judge_press`, `judge_pipeline` and `judge_deploy` take facts rather than a
connection, and both readers hand them the same shapes. A second copy of a rule
can only ever agree with the first by luck, which is the argument `week_label`
below already makes about the press's own week.

Every surface says which reader answered it, as `read_via` in its evidence. A
receipt is second-hand, and a report that hides that is the kind incident 24 was
full of. One thing the receipt cannot do is write, so a drift alarm read that
way is reported and not mailed, and it says so.

## The fifth surface: is the merged code the running code

Sprint 2026-09-28 item 2. Every surface above reads an artifact, and a deploy
leaves no artifact at all, which is how PR #110 sat merged and inert from
2026-09-26 while three documents described its behaviour as live. Incident 24
is the same shape a week earlier. `modal deploy` bakes the repository into an
image and the chair's deploy step is a separate, easy-to-forget hand action,
so "merged" and "running" are two different facts and nothing compared them.

Now they do compare. `pipeline/runtime_sha.py` rides into each job's image and
each job writes a digest of the files it is actually running from into
`deploy_runtime` at the top of every run. This surface computes the same digest
from the checkout it is standing in and says whether the two agree.

A drift is only an alarm once it is a day old. The org merges most days, and a
surface that went red the moment a pull request landed would be red most
mornings for a reason that resolves itself, which is exactly how a report
teaches its reader to stop reading it. So a drift younger than
`DEPLOY_GRACE_HOURS` reads as ok with the pending deploy named in its headline,
and past that it is `failing` and the owner is mailed through
`pipeline/notify.py`.

The deploy surface judges the trunk, never the branch it is run from. Both
halves of its comparison are read out of `origin/main` (see `_deployable_ref`),
because a hand deploys from the trunk and a commit that has not merged has
never been inside an image. Until 2026-10-09 it read the working tree instead,
so a seat's own fresh commit dated the drift at an hour and the surface read
green on every branch in the org while the live `triage` image was four days
behind. A guard whose answer depends on where you stand is a guard that reads
green in the only places anyone actually runs it.

Two ways this surface refuses to guess, both of them `unknown` rather than a
verdict. A checkout too shallow to date the last commit on the trunk that
touched a job's files cannot tell a drift of an hour from a drift of a month.
And no `DATABASE_URL` means the recorded side cannot be read at all. A dirty
working tree used to be a third; it is reported in the evidence now and changes
nothing, because an uncommitted edit cannot alter what the trunk says.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import types
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SITE_URL = "https://libraryofalexandria.dev"
MCP_URL = "https://ap4509--alexandria-mcp-serve.modal.run"

# The credential-free reader for the three database surfaces. The site already
# holds DATABASE_URL in its own environment, so `site/app/api/delivery/route.js`
# publishes the rows this command judges and no seat needs a credential to read
# them. Facts only: the judgement below is the single copy.
RECEIPT_URL = f"{SITE_URL}/api/delivery"
RECEIPT_VERSION = 3  # must match site/lib/delivery-core.js RECEIPT_VERSION

# And the versions this reader can still read. Exact-match was the rule until
# 2026-10-10 and it made every additive field an outage: the site deploys on a
# merge to `main` and a seat's checkout updates the instant the branch lands, so
# the newest reader meets the previous receipt for as long as the deploy takes,
# and a refused receipt is all three database surfaces answering `unknown`.
#
# A version is readable when every field this reader needs for a verdict is
# present in it or is optional in it. Version 2 added `queues`, which is
# optional by construction (an absent queue depth is a fact this reader does not
# have, never a queue of zero), so version 1 stays readable. Version 3 added
# `pipeline.distilled_newest` on the same terms, so versions 1 and 2 stay
# readable too. A version that removed or renamed a field would not be added to
# this tuple.
READABLE_VERSIONS = (1, 2, 3)

# Which reader answered. It goes in every surface's evidence as `read_via`,
# because "the press printed" and "a second-hand record says the press printed"
# are different strengths of evidence and a report that hides the difference is
# the kind of report incident 24 was full of.
DIRECT = "DATABASE_URL"

OK, FAILING, UNKNOWN = "ok", "failing", "unknown"

# The daily crons run between 11:00 and 14:00 UTC, so a corpus table that has
# not moved in two days has missed two of them. One day would fire on any run
# that merely started late.
PIPELINE_STALE_DAYS = 2

# How long a merged change may sit undeployed before it is an alarm rather than
# a pending deploy. A day is the number sprint 2026-09-28 item 2 asks for, and
# it is also the longest any of the three jobs waits for its next run: triage at
# 12:00 UTC and interpret at 14:00 UTC are daily, so a deploy that is a day old
# has already had a run go out on stale code. The press is weekly and is the
# reason this is not tightened further, since its own drift is caught here long
# before Monday comes round again.
DEPLOY_GRACE_HOURS = 24

# One mail a day per app while a drift lasts, not one per check. The standup
# runs this command every morning and a week of stale deploy must not be a week
# of hourly mail; `deploy_runtime.notified_at` is the cooldown's memory and the
# jobs clear it themselves whenever the running sha changes.
DEPLOY_NOTIFY_COOLDOWN_HOURS = 24

# How far back the surface will replay the digest looking for the commit the
# running image was built from. Forty is generous for three apps whose file sets
# change a few times a week, and it is a ceiling rather than a cost: the walk
# stops at the first commit that matches, which on a normal day is the first or
# second one it tries. Only a drifted app is ever walked at all.
DEPLOY_HISTORY_LIMIT = 40

# How many commits a headline names before it starts counting instead. Three
# fits on a line, and the rest are in the evidence block either way.
DEPLOY_NAMED_COMMITS = 3

# The only code that was ever deployable. `modal deploy` is run by a hand
# standing on the trunk, so a commit that has not merged has never been in an
# image, and judging the running deploy against a branch asks a question nobody
# needs the answer to. Tried in this order because a seat's sandbox has
# `origin/main`, a bare clone of the trunk may carry only `main`, and a
# repository with neither is judged against its own `HEAD` (see
# `_deployable_ref`).
DEPLOYABLE_REFS = ("origin/main", "main")


class Surface:
    """One delivery surface's answer: a state, a headline, and its evidence."""

    def __init__(self, name: str, state: str, headline: str,
                 evidence: dict | None = None):
        self.name, self.state, self.headline = name, state, headline
        self.evidence = evidence or {}

    def as_dict(self) -> dict:
        return {"surface": self.name, "state": self.state,
                "headline": self.headline, "evidence": self.evidence}


def _press_module():
    """`pipeline.weekly`, importable in a sandbox with no Modal SDK.

    Every date rule this file needs is read out of the press rather than
    recomputed here. A health check that carries its own copy of a rule can
    only ever agree with the press by luck, and disagreeing silently is worse
    than not checking. That matters more than usual for the week rule, which
    was wrong until 2026-09-23: a second copy written that morning would have
    been a second copy of the bug.

    `pipeline/weekly.py` imports `modal` at module scope, for decorators, and a
    seat's sandbox has no reason to have the Modal SDK installed. So when it is
    absent this stands a namespace in for it long enough to read the pure date
    functions out of the module. `tests/conftest.py` does the same thing for
    the same reason, and the alternative is the duplicated rule.
    """
    if "modal" not in sys.modules:
        try:
            import modal  # noqa: F401
        except ImportError:
            stub = types.ModuleType("modal")

            class _Chaining:
                def __getattr__(self, name):
                    return lambda *a, **k: self

            stub.Cron = lambda *a, **k: None
            stub.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
            stub.Volume = types.SimpleNamespace(from_name=lambda *a, **k: None)
            stub.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Chaining())
            stub.App = lambda *a, **k: types.SimpleNamespace(
                function=lambda *a, **k: (lambda f: f),
                local_entrypoint=lambda *a, **k: (lambda f: f),
            )
            sys.modules["modal"] = stub

    from pipeline import weekly

    return weekly


def week_label(today: date | None = None) -> str:
    """The week the press should most recently have printed."""
    return _press_module().week_just_ended(today)[0]


# `pipeline/weekly.py`'s `weekly()` carries `schedule=modal.Cron("0 9 * * 1")`:
# Monday at 09:00 UTC. This is the one fact about the press's clock that this
# file needs and cannot read out of `week_just_ended`, which answers which week
# the press should print and never when it gets its turn. So it is a copy, and
# this file's standing argument is that a copy agrees with the original only by
# luck. `test_the_cron_this_check_assumes_is_the_cron_the_press_runs` reads the
# decorator out of `pipeline/weekly.py` and pins it to this constant: change
# the schedule and that test is what sends you back here.
PRESS_CRON = "0 9 * * 1"

# How long after its cron fires the press may still be working before lateness
# is real. The scheduled run opens a connection, calls a provider under a
# 1800-second timeout and then mails every subscriber, so a run still going at
# 09:40 is a working press rather than a missing issue. Erring long is the
# cheap direction. A check that is early by an hour cries wolf every single
# week, which is how a seat learns to stop reading it, where a check that is
# late by an hour reports a genuinely missing issue at 11:00 instead of 09:00.
PRESS_GRACE = timedelta(hours=2)


def _instant(when: date | datetime | None = None) -> datetime:
    """A `today` argument, as the instant the question is being asked at.

    This file's public functions have always taken `today: date`, which is
    enough to know which week should have been printed and not enough to know
    whether that week's deadline has passed. Both are needed now, so a
    `datetime` is accepted everywhere a `date` was.

    A bare `date` means the end of that day. Every existing caller that passes
    one is asking about a day that is over, so reading it as midnight would
    quietly change the question they are asking. `datetime` is a subclass of
    `date`, which is why it is tested for first, and a naive one is read as UTC
    because every other clock in this file is UTC.
    """
    if when is None:
        return datetime.now(timezone.utc)
    if isinstance(when, datetime):
        return when if when.tzinfo else when.replace(tzinfo=timezone.utc)
    return datetime(when.year, when.month, when.day, 23, 59, 59,
                    tzinfo=timezone.utc)


def press_deadline(week_end: date) -> datetime:
    """When the issue for the week ending on `week_end`, a Sunday, is due.

    The cron fires the morning after the week ends, so the deadline is that
    Monday at the cron's own hour plus the grace the run itself needs.
    """
    minute, hour = PRESS_CRON.split()[:2]
    monday = week_end + timedelta(days=1)
    fires = datetime(monday.year, monday.month, monday.day,
                     int(hour), int(minute), tzinfo=timezone.utc)
    return fires + PRESS_GRACE


def press_due_week(when: date | datetime | None = None) -> tuple[str, str | None]:
    """The newest issue the press is obliged to have printed, and the one it owes.

    `week_label` answers which week has ended. That is the right question for
    the press, which prints the week that ended, and the wrong question for a
    health check, which also has to know whether the press has had its turn
    yet. Between Monday 00:00 UTC and the cron at 09:00 the week that has just
    ended has no issue and nothing at all is wrong, and for those nine hours
    this check reported FAILING every single week. Sprint 2026-10-05's item 4
    names exactly this: the press surface "reads FAILING on any Monday before
    the cron fires, with nothing standing that re-checks after the window
    closes". A guardrail that is wrong on a schedule teaches the seats reading
    it to discount it, which costs more than the check is worth.

    Returns the due week and, when the week that most recently ended is not due
    yet, that week as `pending`, so the surface can name the issue it is
    waiting for instead of quietly expecting the one before it.
    """
    press = _press_module()
    now = _instant(when)
    ended = press.last_sunday(now.date())

    def label(sunday: date) -> str:
        # The press labels the week that ended on `sunday` when it runs the
        # morning after, so ask it that way rather than formatting a second
        # ISO week here.
        return press.week_just_ended(sunday + timedelta(days=1))[0]

    if now < press_deadline(ended):
        return label(ended - timedelta(days=7)), label(ended)
    return label(ended), None


def fetch(url: str, timeout: int = 25) -> tuple[int, str, dict]:
    """GET a URL. Returns (status, body, headers); status 0 means it never answered.

    Never raises. A surface that is unreachable is a finding to report, not an
    exception to propagate, because one dead surface must not stop the other
    three from being checked.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "alexandria-delivery-health"})

    def headers_of(message) -> dict:
        # Lowercased keys. `email.message.Message` looks up case-insensitively
        # and a plain dict() of it does not, so the WWW-Authenticate header the
        # MCP probe reads for came back missing and the server read as broken
        # while it was answering correctly.
        return {k.lower(): v for k, v in message.items()}

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return (response.status, response.read().decode("utf-8", "replace"),
                    headers_of(response.headers))
    except urllib.error.HTTPError as exc:
        # An HTTP error is an answer. The MCP probe wants a 401 and would be
        # wrong to read it as silence.
        return exc.code, exc.read().decode("utf-8", "replace"), headers_of(exc.headers)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return 0, str(exc), {}


# ---------------------------------------------------------------- surfaces

def check_site(today: date | datetime | None = None) -> Surface:
    """Which issues can a reader actually read, and is the newest one current.

    The evidence is the rendered `/library` listing rather than a file on disk
    or a commit on main, because all three can disagree and only one of them is
    what a reader meets. `site/lib/content.js` also keeps a HIDDEN_WEEKS set,
    so a week can be present in the repository and deliberately unpublished.

    Since 2026-10-01 the listing is the `digests` table rather than the
    committed files (`site/lib/issues-live.js`), which changes what a stale
    answer here means but not what is read to get it. This surface and the
    press surface should now agree on the newest week, and the listing falls
    back to the committed files when the site cannot reach Neon, so they can
    still disagree. That disagreement is worth reporting rather than hiding:
    it is the site failing closed, which is the behaviour this check should
    want and not the behaviour it should assume.
    """
    status, body, _ = fetch(f"{SITE_URL}/library")
    if status == 0:
        return Surface("site", FAILING, f"the site did not answer: {body}")
    if status != 200:
        return Surface("site", FAILING, f"/library returned HTTP {status}")

    weeks = sorted(set(re.findall(r"\b(\d{4}-W\d{2})\b", body)), reverse=True)
    expected = week_label(_instant(today).date())
    # Same rule as the press surface, and for the same reason: the site cannot
    # publish an issue the press is not due to have written yet, so judging it
    # against `expected` made the archive cry wolf on exactly the Mondays the
    # press surface did.
    due, pending = press_due_week(today)
    evidence = {"url": f"{SITE_URL}/library", "published": weeks,
                "expected": expected, "due": due, "pending": pending}
    if not weeks:
        return Surface("site", FAILING, "/library renders but publishes no issue at all",
                       evidence)
    if weeks[0] < due:
        return Surface(
            "site", FAILING,
            f"the newest issue a reader can read is {weeks[0]}, and {due} "
            "has ended. The archive reads the `digests` table now "
            "(site/lib/issues-live.js), so this no longer means a commit was "
            "forgotten: it means the press wrote no row for that week, or the "
            "site cannot read the database, or the week is in HIDDEN_WEEKS. "
            "The press surface above distinguishes the first two.",
            evidence)
    return Surface("site", OK,
                   f"{len(weeks)} issue(s) published, newest {weeks[0]}", evidence)


HIDDEN_WEEKS_RE = re.compile(r"HIDDEN_WEEKS\s*=\s*new Set\(\[(.*?)\]\)", re.S)


def hidden_weeks(repo_root: Path | None = None) -> set[str]:
    """The weeks the site deliberately does not publish.

    Read out of `site/lib/content.js` rather than listed here, because that set
    is the owner's veto over the archive (2026-W37, retired on her order
    2026-09-19) and a second copy of it would be a second place to forget.
    An unreadable file yields an empty set, which can only make this check
    noisier and never quieter.
    """
    root = repo_root or Path(__file__).resolve().parents[1]
    try:
        text = (root / "site" / "lib" / "content.js").read_text()
    except OSError:
        return set()
    m = HIDDEN_WEEKS_RE.search(text)
    return set(re.findall(r"\d{4}-W\d{2}", m.group(1))) if m else set()


def judge_archive(press: Surface | None, site: Surface | None,
                  hidden: set[str] | None = None) -> Surface:
    """Does the public archive show the week the press recorded.

    This surface exists because of the shape of the fix that made it
    answerable. `site/lib/issues-live.js` reads the `digests` table and falls
    back to the committed markdown when it cannot, which is the right way to
    fail and is also L-A16 in docs/standards/lessons.md: "the gap between
    intent and effect is silent by construction, because a well-built fallback
    makes the run succeed anyway." If the site's environment has no
    `DATABASE_URL`, or the role cannot read `digests`, the archive keeps
    serving the committed files and every other surface here stays green. The
    record path would be dead and nothing would say so.

    So the two answers are compared. The press surface knows the newest week in
    `digests`. The site surface knows the newest week a reader can open. When
    they agree, the connection between them is working, and that is the only
    evidence that it is.
    """
    hidden = hidden if hidden is not None else hidden_weeks()
    if press is None or site is None:
        return Surface("archive", UNKNOWN,
                       "needs both the press and the site surface to compare")
    if press.state == UNKNOWN or site.state == UNKNOWN:
        unread = press.name if press.state == UNKNOWN else site.name
        return Surface("archive", UNKNOWN,
                       f"the {unread} surface could not be read here, so the "
                       "record and the page cannot be compared")

    recorded = press.evidence.get("newest_week")
    published = [w for w in site.evidence.get("published", []) if w not in hidden]
    evidence = {"recorded": recorded, "published": published,
                "hidden": sorted(hidden)}
    if not recorded:
        return Surface("archive", UNKNOWN,
                       "the press surface reported no week to compare", evidence)
    if recorded in hidden:
        return Surface("archive", OK,
                       f"{recorded} is the newest record and is deliberately "
                       "unpublished", evidence)
    if not published:
        return Surface("archive", FAILING,
                       f"the record holds {recorded} and the archive publishes "
                       "nothing", evidence)

    newest_published = max(published)
    if newest_published == recorded:
        return Surface("archive", OK,
                       f"the record and the archive both end at {recorded}",
                       evidence)
    if newest_published < recorded:
        return Surface("archive", FAILING,
                       f"the press recorded {recorded} and the newest issue a "
                       f"reader can open is {newest_published}. Either the "
                       "site cannot read the database, in which case the "
                       "archive is serving the committed files and the record "
                       "path is dead, or that week is hidden and this list "
                       "does not know it", evidence)
    return Surface("archive", OK,
                   f"the archive publishes {newest_published} and the record "
                   f"does not hold it. The newest record is {recorded}. A week "
                   "published by hand is the old path still working, not a "
                   "failure", evidence)


def check_mcp() -> Surface:
    """Alive and still guarded, in one unauthenticated request.

    Two failures share this probe on purpose. A connection error means the
    server is down, which incident 21 says costs the org something. A 200 means
    it is up and answering tool calls to anyone who asks, which is worse than
    down, so it is reported as failing rather than as a happy 'reachable'.
    """
    status, body, headers = fetch(f"{MCP_URL}/mcp")
    evidence = {"url": f"{MCP_URL}/mcp", "status": status,
                "www_authenticate": headers.get("www-authenticate", "")}
    if status == 0:
        return Surface("mcp", FAILING, f"the MCP server did not answer: {body}", evidence)
    if status == 401:
        if not evidence["www_authenticate"]:
            return Surface("mcp", FAILING,
                           "401 with no WWW-Authenticate header, so a client "
                           "cannot discover how to authenticate", evidence)
        return Surface("mcp", OK, "up, and refusing unauthenticated calls", evidence)
    if status == 200:
        return Surface("mcp", FAILING,
                       "/mcp answered 200 to a request carrying no token", evidence)
    return Surface("mcp", FAILING, f"/mcp returned an unexpected HTTP {status}", evidence)


def press_facts(conn) -> dict | None:
    """The newest row in `digests`, or None when the table is empty.

    This is guardrail 4's own named evidence and the one query incident 24
    would have been answered by in a second.
    """
    row = conn.execute(
        "select week, created_at, model from digests order by week desc limit 1"
    ).fetchone()
    if row is None:
        return None
    return {"week": row[0], "created_at": row[1], "model": row[2]}


def judge_press(facts: dict | None, today: date | datetime | None = None,
                source: str = DIRECT) -> Surface:
    """The newest issue, against the newest issue the press owes by now.

    Takes rows rather than a connection, so the credential-free reader and the
    credentialled one are judged by this function and not by two copies of it.
    The file already makes this argument about `week_just_ended`: a second copy
    of a rule can only ever agree with the first by luck.

    `due` and not `expected` is what the verdict turns on. They differ for the
    nine hours of every Monday between midnight and the cron, and this check
    called those hours a missing issue until 2026-10-08. `expected` stays in
    the evidence because it is still the honest answer to a different question,
    which week has ended, and because that is the field incident 24 is read by.
    """
    expected = week_label(_instant(today).date())
    due, pending = press_due_week(today)
    waiting = {"expected": expected, "due": due, "pending": pending,
               "read_via": source}
    if facts is None:
        # An empty table is broken whatever the clock says. There is no week
        # the press has ever printed, so there is nothing for the grace window
        # to excuse.
        return Surface("press", FAILING, "the digests table is empty", waiting)
    week, created_at, model = facts["week"], facts["created_at"], facts["model"]
    evidence = {"newest_week": week, **waiting,
                "created_at": str(created_at), "model": model}
    if week < due:
        missing = _weeks_between(week, due)
        return Surface("press", FAILING,
                       f"the newest issue is {week} and {due} has ended; "
                       f"{missing} issue(s) missing", evidence)
    if pending and week < pending:
        deadline = press_deadline(_press_module().last_sunday(_instant(today).date()))
        return Surface("press", OK,
                       f"{week} is written, by {model}. {pending} is not due "
                       f"yet: the press has until "
                       f"{deadline:%Y-%m-%d %H:%M} UTC to print it, so a "
                       f"missing {pending} before then is the schedule and "
                       f"not a fault", evidence)
    return Surface("press", OK, f"{week} is written, by {model}", evidence)


def check_press(conn, today: date | datetime | None = None) -> Surface:
    return judge_press(press_facts(conn), today)


QUEUE_DEPTHS = """
    select
      (select count(*) from papers p
        where not exists (
          select 1 from latest_triage t where t.paper_id = p.id
        )),
      (select count(*) from distill_queue),
      (select count(*) from interpret_queue)
"""


def queue_facts(conn) -> dict | None:
    """How many rows wait at each stage, or None when this database cannot say.

    Fail-soft for the same reason site/lib/delivery.js is. These are views in
    db/schema.sql and `apply_schema` is a hand step, so a database one migration
    behind must still be able to report when the corpus last moved. The read
    runs inside `conn.transaction()`, which is a savepoint when the caller is
    already in a transaction: a failed statement in psycopg aborts the whole
    transaction, so without it a missing view would take the deploy surface
    down with it on the same connection.

    None and never zeroes. A queue of zero is a real fact, and it is half of the
    diagnosis below, so a failed read must not be able to claim it.
    """
    try:
        with conn.transaction():
            row = conn.execute(QUEUE_DEPTHS).fetchone()
    except Exception:
        return None
    if row is None:
        return None
    return {"triage_pending": row[0], "distill_pending": row[1],
            "interpret_pending": row[2]}


def pipeline_facts(conn) -> dict:
    """When the corpus last moved, and how much is waiting to move it.

    The newest row in `papers` and in `claims`, which is the staleness, plus
    two facts that are the cause rather than the clock: the queue depths, and
    when distill last marked a paper read. Read in that order so the cheap
    reads answer even when the views are absent.

    `fetched_at` and `distilled_at` come back from one statement, because they
    are two columns of the same table and neither has an index to use. One scan
    for two scalars rather than two scans for one each.
    """
    papers, distilled = conn.execute(
        "select max(fetched_at), max(distilled_at) from papers").fetchone()
    return {
        "papers": papers,
        "claims": conn.execute("select max(created_at) from claims").fetchone()[0],
        "distilled": distilled,
        "queues": queue_facts(conn),
    }


def queue_cause(label: str, queues: dict | None, distilled: datetime | None = None,
                now: datetime | None = None) -> str:
    """Why a stalled table stalled, said as a clause on the headline.

    `claims` is the only one of the two corpus tables with a queue inside this
    database. Papers come from arXiv, so ingest's queue is somebody else's
    index and there is nothing here to count. `distill_queue` is what turns a
    paper into claims, and a stale `claims` therefore has exactly two causes:
    the stage had nothing to read, or it had work and did not do it. One number
    separates them, and separating them is the whole reason the site publishes
    it.

    The 2026-10-09 ledger entry is the case this is written against. It
    established that claims had not moved in two days, that triage and
    interpret were firing, and that no merged commit explained it, and then had
    to stop: "whether the cron fired at all, whether it fired and found an
    empty queue, or whether it fired and raised" needed a credential no seat
    holds. The first two of those three are this clause.

    The third of those three is `distilled`, and it was added once the depth
    went live and answered only half. The published depth on 2026-10-10 was
    2099 against a `claims` frozen since 2026-10-07, which settles that the
    stage had work and leaves the two causes that are not an empty queue. They
    do not have the same first step, so splitting them is worth a clause:
    `papers.distilled_at` moves per paper in the same committed loop as that
    paper's claims, so a marker that moved while `claims` stood still is a
    stage that read and extracted nothing, and a marker that stood still with
    it is a stage that never reached a paper.
    """
    if label != "claims":
        return ""
    if queues is None:
        return (", and no queue depth is published here, so whether distill had "
                "nothing to read or had work and did not do it cannot be said "
                "from this reader")
    depth = queues.get("distill_pending")
    if depth is None:
        return ", and distill_queue could not be read, so the cause is still one of two"
    if depth == 0:
        return (", with distill_queue empty, so the stage had nothing to read and "
                "the gap is upstream of it in ingest or triage")
    return (f", with {depth} papers waiting in distill_queue, so the stage had work "
            f"and did not do it" + _unread_or_unwritten(distilled, now))


def _unread_or_unwritten(distilled: datetime | None, now: datetime | None) -> str:
    """Which of the two remaining causes it is, from the distill marker.

    Split out because the sentence is the actionable half and it is the half a
    reader quotes. Both readers reach it through `queue_cause`, so the receipt
    and a connection cannot name different first steps for the same stall.

    `None` is deliberately read as "cannot say" and never as "never ran". A
    direct connection means it as "no paper carries the marker" and a version 1
    or 2 receipt has no field at all, and the two arrive here identically. A
    wrong cause costs more than a missing one, so the one wording that is true
    of both is the wording used.
    """
    if distilled is None:
        return (", and no distill marker is readable here, so which of those two "
                "it is needs `modal app logs alexandria-distill`")
    now = now or datetime.now(timezone.utc)
    if distilled.tzinfo is None:
        distilled = distilled.replace(tzinfo=timezone.utc)
    age = now - distilled
    days = round(age.days + age.seconds / 86400, 1)
    if age <= timedelta(days=PIPELINE_STALE_DAYS):
        return (f", and it marked a paper read {days} days ago, so it ran and "
                f"extracted nothing: the prompt and the parse are the suspects "
                f"rather than the cron")
    return (f", and it has marked nothing read in {days} days either, so it never "
            f"reached a paper: the cron, the model availability gate and the spend "
            f"cap are the suspects, and `modal app logs alexandria-distill` is "
            f"where they show")


def judge_pipeline(facts: dict, now: datetime | None = None,
                   source: str = DIRECT) -> Surface:
    """The daily crons, read through the rows they leave behind.

    delivery-health.md's own table calls this the next gap and says why it
    matters most: it is the surface that feeds every other one. A press that
    prints on an empty corpus prints an empty issue.
    """
    now = now or datetime.now(timezone.utc)
    rows = dict(facts)
    # Out of the staleness loop before it runs: everything left in `rows` is a
    # corpus timestamp this surface raises on, and these two are a cause rather
    # than a clock. `distilled` is a timestamp and would otherwise be read as a
    # third stale table, which would report one outage twice and alarm on a
    # marker no stage promises to keep current.
    queues = rows.pop("queues", None)
    distilled = rows.pop("distilled", None)
    stale = []
    evidence = {"read_via": source}
    for label, value in rows.items():
        if value is None:
            stale.append(f"{label} is empty")
            evidence[label] = None
            continue
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        age = now - value
        evidence[label] = {"newest": str(value), "age_days": round(age.days + age.seconds / 86400, 2)}
        if age > timedelta(days=PIPELINE_STALE_DAYS):
            stale.append(f"{label} has not moved in {age.days} days"
                         + queue_cause(label, queues, distilled, now))
    # In the evidence on every path, including the healthy one. A queue that is
    # deep while the corpus still moves is not an alarm by this surface's own
    # unit, which is staleness, and inventing a depth threshold here would be a
    # second alarm nobody asked for. It is a number a reader wants beside the
    # dates, so it is reported and not judged.
    evidence["queues"] = queues
    # Beside the depths and on every path, for the same reason they are: it is
    # a number a reader wants next to the dates, and it is not judged here.
    evidence["distilled"] = str(distilled) if distilled is not None else None
    if stale:
        return Surface("pipeline", FAILING, "; ".join(stale), evidence)
    return Surface("pipeline", OK,
                   f"ingesting and distilling within {PIPELINE_STALE_DAYS} days", evidence)


def check_pipeline(conn) -> Surface:
    return judge_pipeline(pipeline_facts(conn))


def _git(repo_root: Path, *args: str) -> tuple[int, str]:
    """Run one git command in the checkout. Returns (status, stdout stripped).

    Never raises. Git missing, or a directory that is not a repository, is a
    reason to answer `unknown`, and an exception here would take the other four
    surfaces down with it.
    """
    import subprocess

    try:
        done = subprocess.run(["git", "-C", str(repo_root), *args],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return 1, str(exc)
    return done.returncode, done.stdout.strip()


def _dirty(repo_root: Path, paths: list[str]) -> list[str]:
    """Which of these files the working tree has changed and not committed.

    Context for the reader, not a verdict, since 2026-10-09. It used to make
    the deploy surface answer `unknown`, which was right while the surface
    hashed the disk and is wrong now that it hashes a commit.
    """
    status, out = _git(repo_root, "status", "--porcelain", "--", *paths)
    if status != 0 or not out:
        return []
    # `XY path`, and the path is taken by splitting rather than by slicing off
    # two status characters and a space. `_git` strips its output, so the very
    # first line of an unstaged change arrives as `M path` with its leading
    # space already gone, and a fixed offset ate the first letter of the
    # filename. It read `ipeline/triage.py`, which is the kind of wrong that
    # still looks like an answer.
    return sorted({line.split(maxsplit=1)[-1].strip()
                   for line in out.splitlines() if line.split(maxsplit=1)[1:]})


def _deployable_ref(repo_root: Path) -> str:
    """Which commit the running image is judged against.

    "Is the code on *this checkout* the code the crons are running" was the
    wrong question, and on 2026-10-09 it answered green on a lie. Every agent
    seat runs on its own branch, and a branch commit made an hour ago dates the
    drift at an hour however far behind the trunk the live image really is.
    The same guard, in the same minute, off the same `deploy_runtime` row, read
    `ok` ("a deploy is pending and still inside the 24h window") on an engineer
    branch and `FAILING` ("triage is 3.9 days behind") in a clean `main`
    worktree. The run that first met this re-measured by hand in a scratch
    worktree and wrote the workaround down, which leaves a guard whose answer
    depends on a step the reader has to know to take.

    So the question becomes "is the trunk the code the crons are running",
    which is the one with an actionable answer: a hand deploys from the trunk,
    so the trunk is the only code that has ever been in an image.

    `HEAD` when neither ref resolves. That is a repository with no trunk to
    compare against, where the old question is the only one available and is
    also the right one, because there is no branch to be standing on.
    """
    for ref in DEPLOYABLE_REFS:
        status, _ = _git(repo_root, "rev-parse", "--verify", "--quiet", ref)
        if status == 0:
            return ref
    return "HEAD"


def _last_commit_at(repo_root: Path, paths: list[str],
                    ref: str = "HEAD") -> datetime | None:
    """When the newest commit on `ref` touching any of these files landed.

    None when the answer cannot be trusted, which is a shallow clone that
    predates the change, git not being present, or a path set nothing in the
    available history ever touched. The seat workflows check out with
    `fetch-depth: 0`, so in the place this actually runs daily the answer is
    real; anywhere else it degrades to `unknown` instead of to a guess.
    """
    status, out = _git(repo_root, "log", "-1", "--format=%cI", ref,
                       "--", *paths)
    if status != 0 or not out:
        return None
    try:
        return datetime.fromisoformat(out).astimezone(timezone.utc)
    except ValueError:
        return None


def _git_bytes(repo_root: Path, *args: str) -> tuple[int, bytes]:
    """`_git`, but the output arrives as bytes and nothing is stripped.

    `_git` strips its stdout, which is right for a sha or a date and wrong for
    a file's contents: a hash over a stripped copy of a file is a hash of a
    different file, and `site/emails/digest.html` would mismatch itself.
    """
    import subprocess

    try:
        done = subprocess.run(["git", "-C", str(repo_root), *args],
                              capture_output=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return 1, b""
    return done.returncode, done.stdout


def _tree_blobs(repo_root: Path, commit: str,
                paths: list[str]) -> dict[str, str] | None:
    """(repository path -> git object id) for every blob under these paths.

    One call per commit for the whole file set, because the alternative is one
    process per file and this runs inside a daily standup. None means git could
    not answer, which the caller turns into `unknown` rather than a guess.
    """
    if not paths:
        return {}
    status, out = _git(repo_root, "ls-tree", "-r", commit, "--", *paths)
    if status != 0:
        return None
    blobs = {}
    for line in out.splitlines():
        meta, _, path = line.partition("\t")
        bits = meta.split()
        if path and len(bits) == 3 and bits[1] == "blob":
            blobs[path] = bits[2]
    return blobs


def _digest_at(repo_root: Path, app: str, commit: str,
               cache: dict[str, str]) -> str | None:
    """The deploy digest this repository would have produced at one commit.

    The manifest is re-read from the module's source *as it was at that
    commit*, not as it is today, because a commit that added a file to an image
    changed the file list as well as the files. Reading today's list against an
    older tree would report a missing entry for every file added since, and
    every digest in history would mismatch.

    `cache` maps a git object id to its content hash. Most of these blobs are
    unchanged from one commit to the next, so the cache is what keeps the walk
    to roughly one hash per distinct version of a file rather than one per
    commit per file.
    """
    from pipeline import runtime_sha

    module = runtime_sha.APPS[app]

    def content(oid: str) -> str:
        if oid not in cache:
            status, body = _git_bytes(repo_root, "cat-file", "blob", oid)
            if status != 0:
                return runtime_sha.MISSING
            cache[oid] = runtime_sha.inner_hash_bytes(body)
        return cache[oid]

    head = _tree_blobs(repo_root, commit, [module])
    if head is None or module not in head:
        return None
    status, body = _git_bytes(repo_root, "cat-file", "blob", head[module])
    if status != 0:
        return None
    cache[head[module]] = runtime_sha.inner_hash_bytes(body)

    pairs = runtime_sha.manifest(body.decode("utf-8", "replace"))
    wanted = [repo for repo, _, _ in pairs]
    blobs = _tree_blobs(repo_root, commit, wanted)
    if blobs is None:
        return None

    inner = [(module, content(head[module]))]
    for repo, _, is_dir in pairs:
        if not is_dir:
            oid = blobs.get(repo)
            inner.append((repo, content(oid) if oid else runtime_sha.MISSING))
            continue
        # `_expand` walks the directory and keys each file by its path relative
        # to the directory, skipping caches. The same two rules, against a tree
        # instead of a disk.
        under = {path: oid for path, oid in blobs.items()
                 if path.startswith(repo + "/")
                 and "__pycache__" not in path.split("/")}
        if not under:
            inner.append((repo + "/", runtime_sha.MISSING))
            continue
        for path, oid in under.items():
            inner.append((f"{repo}/{path[len(repo) + 1:]}", content(oid)))
    return runtime_sha.digest_of(inner)


def _paths_at(repo_root: Path, app: str, ref: str) -> list[str] | None:
    """The repository paths in this app's image, as the manifest read at `ref`.

    The same reasoning `_digest_at` gives for re-reading the manifest at a
    commit rather than at the working tree, and for the same reason the caller
    needs it: a branch that adds a file to an image must not change the file
    list the trunk is judged by, or a seat's own uncommitted work would move
    the question.

    None when git cannot answer, which the callers turn into `unknown`.
    """
    from pipeline import runtime_sha

    module = runtime_sha.APPS[app]
    blobs = _tree_blobs(repo_root, ref, [module])
    if blobs is None or module not in blobs:
        return None
    status, body = _git_bytes(repo_root, "cat-file", "blob", blobs[module])
    if status != 0:
        return None
    pairs = runtime_sha.manifest(body.decode("utf-8", "replace"))
    return [module] + [repo for repo, _, _ in pairs]


def undeployed_commits(repo_root: Path, app: str, recorded_sha: str | None,
                       limit: int = DEPLOY_HISTORY_LIMIT,
                       ref: str = "HEAD") -> dict:
    """Which merged commits the running image does not contain.

    "`triage` is 2.9 days behind" does not tell the reader whether the drift is
    a docstring or a provider change, and that was the whole complaint in the
    ledger entry this answers. The age of a drift is a number about the clock.
    The commits inside it are the thing somebody has to decide about.

    There is no commit sha in `deploy_runtime`, and there should not be: the
    row is written by a container that was built from an image and has no way
    to know which commit produced it. So the commit is recovered rather than
    recorded. The digest is replayed over the history of the app's own files
    until a commit produces the digest the container reported, and that commit
    is the one the image was built from. Everything newer that touched those
    files is undeployed.

    Returns a dict for the evidence block. `why` is present and the rest is
    absent whenever the answer is not trustworthy, which is a shallow clone, a
    job that has never reported, or a digest that matches nothing in range.
    """
    from pipeline import runtime_sha

    if not recorded_sha:
        return {"why": "this job has never reported a running digest, so there "
                       "is no deployed state to diff against"}

    module = runtime_sha.APPS[app]
    paths = _paths_at(repo_root, app, ref)
    if paths is None:
        return {"why": f"{module} cannot be read at {ref} here"}

    status, out = _git(repo_root, "log", f"-{limit}",
                       "--format=%H%x1f%h%x1f%s%x1f%cI", ref, "--", *paths)
    if status != 0 or not out:
        return {"why": "this checkout has no history for the app's files, so "
                       "the deployed commit cannot be recovered"}

    commits = []
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 4:
            commits.append(parts)

    cache: dict[str, str] = {}
    ahead = []
    for full, short, subject, when in commits:
        if _digest_at(repo_root, app, full, cache) == recorded_sha:
            return {"deployed_commit": short, "deployed_at": when,
                    "commits": ahead, "searched": len(commits)}
        ahead.append({"sha": short, "subject": subject, "at": when})
    return {"why": f"the running digest {recorded_sha} matches none of the "
                   f"last {len(commits)} commits to touch this app's files, so "
                   f"the deploy was built from code that is not in this "
                   f"history",
            "searched": len(commits)}


def name_undeployed(found: dict, limit: int = DEPLOY_NAMED_COMMITS) -> str:
    """The commits, as one clause for a headline or an alarm.

    Empty string when there is nothing trustworthy to say, so a caller can
    append it unconditionally and a degraded answer costs the headline nothing.
    """
    if "commits" not in found:
        return ""
    commits = found["commits"]
    if not commits:
        return (f"no commit to its files is undeployed; the image is "
                f"{found['deployed_commit']} and so is this checkout")
    named = ", ".join(f"{c['sha']} {c['subject']}" for c in commits[:limit])
    rest = len(commits) - limit
    plural = "commit" if len(commits) == 1 else "commits"
    return (f"{len(commits)} undeployed {plural} since "
            f"{found['deployed_commit']}: {named}"
            + (f", and {rest} more" if rest > 0 else ""))


def deploy_facts(conn) -> dict | str:
    """What each job last reported it was running, from `deploy_runtime`.

    Returns one entry per app, or a string saying why there are none. The table
    lands in db/schema.sql in the same change as this check and `apply_schema`
    is a separate hand-run step, so "no such table" is a state this surface
    will really meet, and it is not a broken deploy.
    """
    try:
        rows = conn.execute(
            "select app, runtime_sha, recorded_at, first_seen_at, notified_at "
            "from deploy_runtime").fetchall()
    except Exception as exc:
        return f"deploy_runtime could not be read: {exc}"
    return {app: {"runtime_sha": sha, "recorded_at": recorded_at,
                  "first_seen_at": first_seen_at, "notified_at": notified_at}
            for app, sha, recorded_at, first_seen_at, notified_at in rows}


def judge_deploy(facts: dict | str, repo_root: Path | None = None,
                 now: datetime | None = None, notify_conn=None,
                 source: str = DIRECT) -> Surface:
    """Is the trunk the code the crons are running.

    One surface for all three jobs rather than three, because the question the
    reader has is "is anything stale" and the headline can name which. The
    evidence block carries each app separately for whoever wants the detail.

    Judged against `_deployable_ref`, not against this checkout. The reason is
    the whole of that function's docstring: a seat runs on a branch, and until
    2026-10-09 a branch commit reset the drift clock, so the one surface that
    watches production read green for every seat and told the truth only in a
    worktree somebody made by hand. `ref` is in the evidence so a reader can
    see which question was answered.

    `notify_conn` is a connection or None. None means do not mail, and the two
    reasons for that are a caller passing `notify=False` and the facts having
    come from the public receipt, which cannot write the alarm's cooldown.
    """
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]
    now = now or datetime.now(timezone.utc)
    ref = _deployable_ref(root)

    try:
        from pipeline import runtime_sha
    except Exception as exc:
        return Surface("deploy", UNKNOWN,
                       f"pipeline/runtime_sha.py could not be read here: {exc}",
                       {"read_via": source})

    if isinstance(facts, str):
        return Surface("deploy", UNKNOWN, facts, {"read_via": source})
    rows = facts

    evidence = {"read_via": source, "ref": ref}
    drifted, unknowns, alarms = [], [], []
    cache: dict[str, str] = {}
    for app in sorted(runtime_sha.APPS):
        keys = _paths_at(root, app, ref)
        local = _digest_at(root, app, ref, cache) if keys else None
        if (keys is None or local is None) and ref == "HEAD":
            # A directory with the files in it and no git in it, which is how
            # this tool arrives anywhere that is not a checkout. There is no
            # trunk to ask, so read the disk and let the dating step below be
            # the one that refuses, exactly as it did before 2026-10-09.
            try:
                entries = runtime_sha.local_entries(app, root)
            except OSError as exc:
                unknowns.append(f"{app} ({exc})")
                evidence[app] = {"state": UNKNOWN, "why": str(exc)}
                continue
            keys = [key for key, _ in entries]
            local = runtime_sha.digest(entries)
        if keys is None or local is None:
            why = f"{ref} has no readable file list for this app here"
            unknowns.append(f"{app} ({why})")
            evidence[app] = {"state": UNKNOWN, "why": why}
            continue
        row = rows.get(app)
        here = {"expected_sha": local, "files": len(keys), "ref": ref,
                "recorded_sha": row["runtime_sha"] if row else None,
                "last_run": str(row["recorded_at"]) if row else None}

        # Never recorded is a third state, and it used to be read as the
        # second. An app with no row has told this guard nothing, so the age
        # of its last commit is not evidence that a deploy is late: it is
        # evidence that the app is unmeasured. Reading it as drift produces a
        # FAILING whose number is the age of the code rather than the age of
        # the deploy, which cries wolf on an app that may be running
        # perfectly. `ingest` is the live case: it delivered papers at 11:01
        # UTC on 2026-10-09 and has never recorded a runtime in its life.
        #
        # Only when something else did record, and that condition is the whole
        # of the distinction. An EMPTY table is not five unmeasured apps, it is
        # a recorder that has never worked, and that is a failure this guard
        # must keep shouting about: `test_a_job_that_never_reported_is_treated
        # _as_drift` has held that line since the guard shipped and it still
        # holds it. One app missing among four that reported is a gap in
        # coverage. Every app missing is a gap in the mechanism.
        if row is None and rows:
            why = ("has never recorded a runtime, so this app is unmeasured "
                   "rather than behind. It records on its next run after a "
                   f"deploy: modal deploy {runtime_sha.APPS[app]}")
            here.update(state=UNKNOWN, why=why)
            unknowns.append(f"{app} (never recorded)")
            evidence[app] = here
            continue

        # Reported, never a verdict. Both halves of the comparison now come
        # from a commit, so an uncommitted edit cannot move the answer and
        # refusing to answer because the sandbox is dirty would be a silence
        # with no cause: a seat's own run leaves this tree dirty every day.
        # It stays in the evidence because a reader looking at a sandbox that
        # differs from the verdict deserves to be told why it differs.
        dirty = _dirty(root, keys)
        if dirty:
            here["uncommitted_here"] = dirty

        if row and row["runtime_sha"] == local:
            here["state"] = OK
            here["live_since"] = str(row["first_seen_at"])
            evidence[app] = here
            continue

        changed_at = _last_commit_at(root, keys, ref)
        if changed_at is None:
            here.update(state=UNKNOWN,
                        why=f"this checkout cannot date the change on {ref}")
            unknowns.append(f"{app} (no datable history for its files here)")
            evidence[app] = here
            continue

        age_hours = (now - changed_at).total_seconds() / 3600
        # Only here, and never on the green path: the walk costs git processes
        # and an app that matches has nothing to name.
        found = undeployed_commits(root, app,
                                   row["runtime_sha"] if row else None,
                                   ref=ref)
        named = name_undeployed(found)
        here.update(state=FAILING if age_hours > DEPLOY_GRACE_HOURS else OK,
                    merged_at=str(changed_at), drift_hours=round(age_hours, 1),
                    undeployed=found)
        evidence[app] = here
        if age_hours > DEPLOY_GRACE_HOURS:
            alarms.append((app, round(age_hours / 24, 1), row, local, named))
        else:
            inside = f"{round(age_hours, 1)}h" + (f", {named}" if named else "")
            drifted.append(f"{app} ({inside})")

    if alarms:
        names = "; ".join(
            f"{app} is {days} days behind" + (f" ({named})" if named else "")
            for app, days, _, _, named in alarms)
        if notify_conn is not None:
            note = _notify_drift(notify_conn, alarms, root, now)
        elif source == DIRECT:
            note = "not notified"
        else:
            note = (f"not mailed: these rows came from {source}, which cannot "
                    "write the once-a-day cooldown, and an alarm with no "
                    "cooldown is one mail every time the standup runs")
        evidence["alarm"] = note
        return Surface("deploy", FAILING,
                       f"the deployed code is not {ref}: {names}. "
                       f"{note}", evidence)
    if unknowns:
        return Surface("deploy", UNKNOWN,
                       "the deploy cannot be compared from here: "
                       + "; ".join(unknowns), evidence)
    if drifted:
        return Surface("deploy", OK,
                       f"a deploy is pending and still inside the "
                       f"{DEPLOY_GRACE_HOURS}h window: {', '.join(drifted)}",
                       evidence)
    return Surface("deploy", OK,
                   f"all {len(runtime_sha.APPS)} jobs are running {ref}",
                   evidence)


def check_deploy(conn, repo_root: Path | None = None,
                 now: datetime | None = None, notify: bool = True) -> Surface:
    return judge_deploy(deploy_facts(conn), repo_root, now,
                        notify_conn=conn if notify else None)


def _notify_drift(conn, alarms: list[tuple], repo_root: Path,
                  now: datetime) -> str:
    """Mail the owner once a day per stale app, and say what happened either way.

    The alarm names the deploy command rather than the problem, because the
    reader of this mail has one action available and it is that command.
    """
    due = []
    for app, days, row, local, named in alarms:
        last = row["notified_at"] if row else None
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if (now - last) < timedelta(hours=DEPLOY_NOTIFY_COOLDOWN_HOURS):
                continue
        due.append((app, days, row, local, named))
    if not due:
        return "the owner was mailed about this within the last day already"

    try:
        from pipeline.notify import notify_owner
    except Exception as exc:
        return f"NOT NOTIFIED: the alarm channel could not be loaded ({exc})"

    from pipeline import runtime_sha

    lines = []
    for app, days, row, local, named in due:
        running = row["runtime_sha"] if row else "nothing recorded at all"
        lines.append(f"{app}: this repository is at {local}, the last run "
                     f"reported {running}, and the change merged {days} days ago.")
        # The commits, where they could be recovered. The reader of this mail
        # decides whether to deploy now or at the next window, and a docstring
        # and a provider change are different answers to that question.
        if named:
            lines.append(f"    {named}")
    detail = "\n\n".join(
        ["A merged change has not reached the jobs that run it.", "\n".join(lines)])
    steps = [f"modal deploy {runtime_sha.APPS[app]}" for app, *_ in due]
    steps.append("then run tools/delivery_health.py --surface deploy again; "
                 "the next run of each job clears its own row")
    sent = notify_owner("alexandria: a merged change is not deployed",
                        detail, steps, sender="alexandria drift guard")

    if sent.startswith("owner notified"):
        try:
            with conn.transaction():
                conn.execute(
                    "update deploy_runtime set notified_at = now() where app = any(%s)",
                    ([app for app, *_ in due],))
        except Exception as exc:
            return f"{sent}; the cooldown was not written ({exc})"
    return sent


def _weeks_between(have: str, want: str) -> int:
    """How many issues are missing between the newest row and the week that ended."""
    def monday(label: str) -> date:
        year, week = label.split("-W")
        return date.fromisocalendar(int(year), int(week), 1)

    return max(0, (monday(want) - monday(have)).days // 7)


# ------------------------------------------------- the credential-free reader

def _parse_iso(value: str | None) -> datetime | None:
    """A timestamp out of the receipt's JSON, as an aware datetime or None."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def read_receipt(url: str | None = None) -> tuple[dict | None, str]:
    """GET the published delivery receipt. Returns (payload, why it is absent).

    Every rejection below is a reason to answer `unknown` rather than to guess,
    and the reason is carried back as prose because the reader of this command
    needs to know which of the two paths failed and how.
    """
    url = url or RECEIPT_URL
    status, body, _ = fetch(url)
    if status == 0:
        return None, f"{url} did not answer: {body}"
    if status != 200:
        # The route's own 503 carries the diagnosis in a `reason` field, and it
        # is the only one available to a seat that cannot see the site's
        # environment: `DATABASE_URL` absent there is one setting away from
        # working, and a failing query is not. Relayed rather than dropped.
        reason = ""
        try:
            reason = json.loads(body).get("reason") or ""
        except (ValueError, AttributeError):
            reason = ""
        return None, (f"{url} returned HTTP {status}"
                      + (f": {reason}" if reason else ""))
    try:
        payload = json.loads(body)
    except ValueError as exc:
        return None, f"{url} did not return JSON: {exc}"
    if not isinstance(payload, dict) or payload.get("receipt") != "alexandria-delivery":
        return None, f"{url} answered something that is not a delivery receipt"
    if payload.get("version") not in READABLE_VERSIONS:
        # A version this reader does not know is not a licence to read the
        # fields it recognises. The missing field would read as a null and a
        # null here is a surface answering FAILING. READABLE_VERSIONS is the
        # list of versions where that is not true, and its header says what
        # earns a place on it.
        return None, (f"{url} published receipt version {payload.get('version')} "
                      f"and this reader speaks {', '.join(str(v) for v in READABLE_VERSIONS)}")
    return payload, ""


def receipt_facts(payload: dict) -> tuple[dict | None, dict, dict | str]:
    """The receipt's JSON, in the same three shapes the database reader returns.

    This is the whole of the translation. The judgement is `judge_press`,
    `judge_pipeline` and `judge_deploy`, unchanged and shared, so a receipt and
    a connection cannot reach different conclusions about the same week.
    """
    press = payload.get("press")
    press_row = None
    if isinstance(press, dict) and press.get("newest_week"):
        press_row = {"week": press["newest_week"],
                     "created_at": _parse_iso(press.get("created_at")),
                     "model": press.get("model")}

    pipeline = payload.get("pipeline") or {}
    # `queues` is absent on a version 1 receipt and null when the site could not
    # read the views. Both mean the same thing to the judgement, which is that
    # the depth is a fact this reader does not have, and neither means zero.
    queues = payload.get("queues")
    # `distilled_newest` is absent on versions 1 and 2 and null when no paper
    # carries the marker. `_parse_iso` returns None for both, which is the
    # shape a direct read of an all-null column returns too, so the two readers
    # hand the judgement the same thing and reach the same sentence.
    pipeline_row = {"papers": _parse_iso(pipeline.get("papers_newest")),
                    "claims": _parse_iso(pipeline.get("claims_newest")),
                    "distilled": _parse_iso(pipeline.get("distilled_newest")),
                    "queues": queues if isinstance(queues, dict) else None}

    deploy = payload.get("deploy")
    if deploy is None:
        # The route sends null when it could not run that query at all, and an
        # empty list when the table is really empty. Collapsing the two would
        # make a missing table look like three jobs that never reported, which
        # is the drift alarm firing on a schema step.
        deploy_rows: dict | str = ("deploy_runtime could not be read by the site "
                                   "either, so the receipt carries no deploy rows")
    else:
        deploy_rows = {row["app"]: {"runtime_sha": row.get("runtime_sha"),
                                    "recorded_at": _parse_iso(row.get("recorded_at")),
                                    "first_seen_at": _parse_iso(row.get("first_seen_at")),
                                    "notified_at": _parse_iso(row.get("notified_at"))}
                       for row in deploy if isinstance(row, dict) and row.get("app")}
    return press_row, pipeline_row, deploy_rows


# ------------------------------------------------------------------ driver

def database_surfaces(today: date | None = None, repo_root: Path | None = None,
                      notify: bool = True) -> list[Surface]:
    """`press`, `pipeline` and `deploy`, by the best reader available.

    Two readers, in order. A direct connection when this environment holds
    `DATABASE_URL`, which is the Modal jobs and the owner's laptop. Otherwise
    the receipt the site publishes, which needs no credential and is what every
    agent seat actually has. Both are judged by the same three functions.

    When neither answers, all three surfaces are `unknown` and the message names
    both paths, because the whole reason guardrail 4 went unenforced for four
    days is that nobody could see which reader was missing what.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    direct_why = "no DATABASE_URL in this environment"
    if url:
        surfaces, direct_why = _from_database(url, today, repo_root, notify)
        if surfaces is not None:
            return surfaces

    payload, receipt_why = read_receipt()
    if payload is not None:
        press, pipeline, deploy = receipt_facts(payload)
        return [judge_press(press, today, RECEIPT_URL),
                judge_pipeline(pipeline, source=RECEIPT_URL),
                judge_deploy(deploy, repo_root, source=RECEIPT_URL)]

    why = (f"the artifact guardrail 4 names cannot be read here: {direct_why}, "
           f"and the published receipt did not answer either ({receipt_why})")
    return [Surface("press", UNKNOWN, why, {"expected": week_label(today)}),
            Surface("pipeline", UNKNOWN, why),
            Surface("deploy", UNKNOWN, why)]


def _from_database(url: str, today: date | None, repo_root: Path | None,
                   notify: bool) -> tuple[list[Surface] | None, str]:
    """The three surfaces over a real connection, or None and why not.

    None rather than three `unknown` surfaces, so the caller can fall through to
    the receipt. A connection that fails is not a healthy press and not a broken
    one, and neither is a missing driver.
    """
    try:
        import psycopg
    except ImportError:
        return None, "psycopg is not installed here (pip install 'psycopg[binary]')"
    try:
        with psycopg.connect(url, connect_timeout=15) as conn:
            return [check_press(conn, today), check_pipeline(conn),
                    check_deploy(conn, repo_root, notify=notify)], ""
    except Exception as exc:
        return None, f"DATABASE_URL is set but the connection failed: {exc}"


ORDER = ["press", "pipeline", "deploy", "site", "archive", "mcp"]


def run(surfaces: list[str], today: date | None = None,
        repo_root: Path | None = None, notify: bool = True) -> list[Surface]:
    asked = set(surfaces)

    # `archive` compares the press's record against the site's page, so asking
    # for it alone has to fetch both of those and then not report them. The two
    # extra names are added here and dropped at the end, rather than inside the
    # comparison, so that `judge_archive` stays a function of two surfaces and
    # is testable as one.
    needed = asked | ({"press", "site"} if "archive" in asked else set())

    out: list[Surface] = []
    if {"press", "pipeline", "deploy"} & needed:
        out += [s for s in database_surfaces(today, repo_root, notify)
                if s.name in needed]
    if "site" in needed:
        out.append(check_site(today))
    if "archive" in asked:
        by_name = {s.name: s for s in out}
        out.append(judge_archive(by_name.get("press"), by_name.get("site")))
    if "mcp" in asked:
        out.append(check_mcp())

    out = [s for s in out if s.name in asked]
    return sorted(out, key=lambda s: ORDER.index(s.name))


def parse_moment(value: str | None) -> date | datetime | None:
    """`--today`, as either a day or an instant inside one.

    A date was enough while the press surface judged by the week that had
    ended. It stopped being enough when the surface learned the press's
    deadline, because "did Monday see a missing issue" has two answers on a
    Monday and the time of day picks between them. Both spellings are accepted
    so no existing invocation of this command changes meaning.
    """
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return date.fromisoformat(text)
    except ValueError:
        return datetime.fromisoformat(text)


def exit_code(results: list[Surface]) -> int:
    if any(s.state == FAILING for s in results):
        return 1
    if any(s.state == UNKNOWN for s in results):
        return 2
    return 0


def render(results: list[Surface]) -> str:
    mark = {OK: "ok     ", FAILING: "FAILING", UNKNOWN: "unknown"}
    lines = ["Delivery health: did the product reach a reader",
             "(docs/agents/delivery-health.md guardrail 4: read the artifact, not the scheduler)",
             ""]
    for s in results:
        lines.append(f"  {mark[s.state]}  {s.name:9} {s.headline}")
    lines.append("")
    code = exit_code(results)
    lines.append({
        0: "Every surface checked answered, and every one of them is delivering.",
        1: "At least one surface is not delivering. The headline above says which.",
        2: ("Nothing is failing, and this is not a green report: a surface "
            "above could not be answered at all from here."),
    }[code])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--surface", action="append", dest="surfaces",
                        choices=ORDER,
                        help="check one surface; repeatable, default is all six")
    parser.add_argument("--no-notify", action="store_true",
                        help="find a stale deploy and do not mail the owner about it")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON instead of prose")
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD, or an ISO timestamp, to ask what a "
                             "given moment should have seen. A bare date means "
                             "the end of that day; the time matters only on a "
                             "Monday, when the press's own deadline falls "
                             "inside it")
    args = parser.parse_args(argv)

    today = parse_moment(args.today)
    results = run(args.surfaces or ORDER, today, notify=not args.no_notify)

    if args.json:
        print(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                          "surfaces": [s.as_dict() for s in results]},
                         indent=2, ensure_ascii=False))
    else:
        print(render(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
