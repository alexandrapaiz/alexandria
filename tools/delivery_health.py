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
| compute  | one probe of Modal's HTTP edge, which fronts  | nothing  |
|          | every cron and the MCP server alike           |          |
| pipeline | newest rows in `papers` and `claims`, and the queue depth behind each, plus whether `compute` is answering | nothing  |
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
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SITE_URL = "https://libraryofalexandria.dev"
MCP_URL = "https://ap4509--alexandria-mcp-serve.modal.run"

# The page a stranger is sent to in order to buy something, and the only
# surface in this file that is read for what it is NOT showing.
PRICING_URL = f"{SITE_URL}/pricing"

# The credential-free reader for the three database surfaces. The site already
# holds DATABASE_URL in its own environment, so `site/app/api/delivery/route.js`
# publishes the rows this command judges and no seat needs a credential to read
# them. Facts only: the judgement below is the single copy.
RECEIPT_URL = f"{SITE_URL}/api/delivery"
RECEIPT_VERSION = 6  # must match site/lib/delivery-core.js RECEIPT_VERSION

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
# readable too, and version 4 added the two sibling-stage markers on the same
# terms again, and version 5 added the `payments` block on the same terms once
# more: an absent block is a till this reader cannot see, which is `unknown`,
# and never a till with nothing wrong. Version 6 added the `unreadable` block
# on the same terms a fifth time, and it is the easiest of the six to justify:
# the block says why another block is null, so a receipt without it is one that
# gives no reason, which is exactly what every receipt before it did. A version
# that removed or renamed a field would not be added to this tuple.
READABLE_VERSIONS = (1, 2, 3, 4, 5, 6)

# Why a fail-soft block could not be read, and what closes it.
#
# The three strings are site/lib/delivery-core.js's `UNREADABLE_REASONS`, which
# the receipt publishes in its version 6 `unreadable` block, and this file
# classifies a direct psycopg failure into the same three so the two readers
# stay interchangeable. That interchangeability is the contract the whole
# credential-free half of this file rests on: a receipt and a connection must
# not be able to reach different first steps from the same database.
#
# The second half is the point. A surface that says it could not look is honest
# and it is not actionable, and `payments` proved how far that goes: it answered
# `unknown` in every standup from the day the block shipped, because
# `payment_exceptions` is newer than every other table here and `apply_schema`
# is a hand-run step. One command closed it the entire time and no report said
# so. So a reason this file recognises carries its own next step.
NO_TABLE, NO_COLUMN, QUERY_FAILED = ("no such table", "no such column",
                                     "query failed")

UNREADABLE_HANDS = {
    NO_TABLE: ("this database is behind db/schema.sql, so one hand-run "
               "`modal run pipeline/db_setup.py::apply_schema` closes it"),
    NO_COLUMN: ("this database is behind db/schema.sql by a column, so one "
                "hand-run `modal run pipeline/db_setup.py::apply_schema` "
                "closes it"),
    QUERY_FAILED: ("the table is there and the query broke, so this one needs "
                   "a log read rather than a migration"),
}


def unreadable_reason(value) -> str | None:
    """One of the three reasons, or None for anything this reader does not know.

    None rather than `query failed` for an unrecognised string, because a newer
    receipt inventing a fourth reason is a fact this reader does not have, and
    guessing at it would put a first step in a report on no evidence. The
    generic `unknown` sentence is the honest answer there.
    """
    return value if value in UNREADABLE_HANDS else None


def why_unreadable(exc: BaseException) -> str:
    """A psycopg failure as one of the three reasons the receipt publishes.

    `sqlstate` and never the message. 42P01 is undefined_table and 42703 is
    undefined_column, and both of those mean the schema is behind rather than
    the query being wrong. Everything else is `query failed`, which is the
    state whose first step is a log.
    """
    state = getattr(exc, "sqlstate", None)
    if state == "42P01":
        return NO_TABLE
    if state == "42703":
        return NO_COLUMN
    return QUERY_FAILED


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

# How long a deferred payment may stay deferred before it is an alarm rather
# than a retry in flight. Polar answers a 503 by bringing the event back on its
# own schedule, and the usual cause is this product's own Clerk webhook not
# having landed yet, which is seconds. Six hours is many retries later: by then
# the row is not waiting on a race, it is waiting on somebody. The number is
# deliberately well inside Polar's own retry window, because the failure to
# catch is a payment that stays stuck until the buyer writes in, and a day-long
# grace is a day of a paid customer with no access.
PAYMENT_DEFER_GRACE_HOURS = 6

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


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Stop at the redirect instead of following it.

    Returning None from `redirect_request` leaves the 3xx unhandled, so urllib
    raises it as an `HTTPError`, which `fetch` already turns into a status and
    a header dict. The checkout probe needs this because where a redirect goes
    is the whole answer: the same route sends a stranger to `/sign-up` and an
    unknown plan to `/pricing`, and a follower sees HTTP 200 for both.
    """

    def redirect_request(self, *args, **kwargs):
        return None


def fetch(url: str, timeout: int = 25, follow: bool = True) -> tuple[int, str, dict]:
    """GET a URL. Returns (status, body, headers); status 0 means it never answered.

    Never raises. A surface that is unreachable is a finding to report, not an
    exception to propagate, because one dead surface must not stop the other
    three from being checked.

    `follow=False` reports the first answer rather than the last one, and it
    builds its own opener so that every existing caller keeps the default
    opener it has always used.
    """
    request = urllib.request.Request(url, headers={"User-Agent": "alexandria-delivery-health"})
    opener = urllib.request.build_opener(_NoRedirect) if not follow else None

    def headers_of(message) -> dict:
        # Lowercased keys. `email.message.Message` looks up case-insensitively
        # and a plain dict() of it does not, so the WWW-Authenticate header the
        # MCP probe reads for came back missing and the server read as broken
        # while it was answering correctly.
        return {k.lower(): v for k, v in message.items()}

    try:
        open_it = opener.open if opener else urllib.request.urlopen
        with open_it(request, timeout=timeout) as response:
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


# Modal's HTTP edge answers for every app in the workspace, including the ones
# it will not route. It replies in plain text on one line, prefixed `modal-http:`,
# and that line is the only place the real cause is written down. The probe below
# used to read the status code and drop the body, which turned the most
# consequential outage this pipeline can have into an unexplained 404 on one
# surface.
MODAL_EDGE_PREFIX = "modal-http:"


def modal_edge_outage(status: int, body: str) -> str | None:
    """Modal's own explanation for a request it refused to route, or None.

    None for anything that is not the edge talking, which includes a 404 from a
    server that is genuinely up and merely has no route at that path. A string
    only when Modal itself says it will not route, and the string is Modal's
    reason rendered as a sentence.

    The workspace case is singled out because its blast radius is the whole
    company and not the one surface that happened to be probed. Every cron in
    `pipeline/` and the MCP server are apps in one workspace, so a workspace
    that is disabled is a total compute outage however many surfaces notice.
    """
    if status == 0 or not body:
        return None
    line = body.strip().splitlines()[0].strip() if body.strip() else ""
    if not line.lower().startswith(MODAL_EDGE_PREFIX):
        return None
    reason = line[len(MODAL_EDGE_PREFIX):].strip()
    if "disabled" in reason.lower():
        return (f"Modal's edge says {reason}, which takes down every cron in "
                "this pipeline and the MCP server together")
    return f"Modal's edge will not route this app: {reason}"


def check_compute() -> Surface:
    """Is the platform every scheduled job runs on accepting requests at all.

    This surface exists because the two that would notice an outage cannot see
    one. `pipeline` reads how recently rows arrived, over a two-day window, so
    it reports green for up to two days after the last cron that will ever run.
    `deploy` reads what the last run recorded, which an outage freezes rather
    than changes. Both were green on 2026-10-23 at 23:08 UTC, with the whole
    workspace switched off since some time between 12:00 and 14:00 that day.

    The one Modal URL this repository knows is the MCP server's, and it is
    enough: the edge that refuses it is the same edge in front of every app in
    the workspace, so one probe answers for all of them.

    Guardrail 1 in docs/agents/delivery-health.md draws the line this follows.
    A request that never arrived and an answer that says everything is gone are
    the same silence and very different facts, so a network failure here is
    `unknown` and never `failing`.
    """
    status, body, _ = fetch(f"{MCP_URL}/mcp")
    evidence = {"probed": f"{MCP_URL}/mcp", "status": status,
                "body": body.strip().splitlines()[0].strip() if body.strip() else ""}
    if status == 0:
        return Surface("compute", UNKNOWN,
                       "the Modal edge could not be reached from here, which "
                       f"is this checkout's network and not a verdict: {body}",
                       evidence)
    outage = modal_edge_outage(status, body)
    if outage:
        return Surface("compute", FAILING, outage, evidence)
    return Surface("compute", OK,
                   "the Modal edge is routing, so the platform every cron runs "
                   "on is answering", evidence)


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
    # Before any judgement about this server, ask whether the platform under it
    # is routing at all. The edge answers for an app it will not serve, so a
    # workspace that has been switched off reads here as a plain 404 from a
    # server that is in fact running fine wherever it is. On 2026-10-23 that is
    # what this probe said, in those words, while every cron in the pipeline was
    # equally gone and nothing in the report named the cause.
    outage = modal_edge_outage(status, body)
    if outage:
        evidence["modal_edge"] = outage
        return Surface("mcp", FAILING,
                       f"{outage}, so this server is unreachable for a reason "
                       "that has nothing to do with it", evidence)
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


# --------------------------------------------- can a sale happen at all
#
# Every surface above this one watches a sale that has already happened.
# `payments` is the closest, and it asks whether a verified payment became
# access, which is the failure *after* somebody bought something. Nothing asked
# whether anybody could buy anything, so on 2026-10-18 both paid tiers on the
# public pricing page rendered the words "Opens shortly" with no link behind
# either one, five days past the date the company committed to taking a
# payment, and every health report the org produced was accurate.
#
# That is L-A16 in `docs/standards/lessons.md`, word for word: configured is
# not in effect, and the gap between the two is silent by construction. The
# checkout route exists, the webhook is written, the entitlement read is live,
# and none of that is a door a buyer can walk through.

OFFERS_BLOCK_RE = re.compile(r"export const OFFERS\s*=\s*\[(.*?)\n\]", re.S)
OFFER_FIELDS_RE = re.compile(r'id:\s*"([a-z0-9-]+)"\s*,\s*env:\s*"([A-Z0-9_]+)"')
CHECKOUT_PATH_RE = re.compile(r"/api/checkout/([a-z0-9-]+)")

# Clerk's two doors. Either one means the route is alive and asking a stranger
# for an account, which is the designed answer and not a fault.
SIGN_IN_PATHS = ("/sign-up", "/sign-in")
REDIRECTS = (301, 302, 303, 307, 308)


def checkout_offers(repo_root: Path | None = None) -> list[tuple[str, str]]:
    """What the product sells, as (offer id, environment variable name) pairs.

    Read out of `site/lib/polar-core.js` for the same reason `hidden_weeks` is
    read out of `site/lib/content.js`. `OFFERS` is the single list that decides
    which tiers the pricing page renders, so a second copy of it here would be
    a second place to forget. Only the two names are read, because a checkout
    URL is a secret this file never sees and has no use for.

    An unreadable file yields an empty list, and that failure deserves saying
    out loud rather than hiding, because it points the opposite way from the
    hidden-weeks read. An empty hidden set can only make that check noisier. An
    empty offer list makes this one quieter, since the per-offer comparison
    below has nothing left to compare and only the floor check survives. So the
    surface puts the list's provenance in its own evidence instead of implying
    it looked.
    """
    root = repo_root or Path(__file__).resolve().parents[1]
    try:
        text = (root / "site" / "lib" / "polar-core.js").read_text()
    except OSError:
        return []
    block = OFFERS_BLOCK_RE.search(text)
    return OFFER_FIELDS_RE.findall(block.group(1)) if block else []


def judge_hop(status: int, location: str, body: str = "") -> tuple[str | None, str]:
    """Where one checkout link leads, and whether that counts as a door opening.

    A pure function of one answer, so the five endings this probe can meet are
    tested without a network and without a Polar account.

    Returns the kind of hop and the words for it, or None and why the door did
    not open. Two kinds count as open. A hop to another host is the seller, and
    a hop to the sign-up page is `/api/checkout/[plan]` asking a stranger for
    an account before it asks for a card, which is the deliberate design and
    the reason that route exists at all rather than a bare link on the page.
    """
    if status == 0:
        return None, f"nowhere, because the route did not answer: {body}"
    if status in REDIRECTS:
        if not location:
            return None, (f"nowhere, because HTTP {status} arrived with no Location "
                          "header for a client to follow")
        target = urllib.parse.urlparse(urllib.parse.urljoin(PRICING_URL, location))
        if target.netloc and target.netloc != urllib.parse.urlparse(SITE_URL).netloc:
            return "seller", f"off-site to {target.netloc}, which is the seller"
        if target.path.startswith(SIGN_IN_PATHS):
            return "sign-in", "to the sign-up page, which asks for an account before a card"
        if target.path.startswith("/pricing"):
            return None, ("back to the pricing page, which is where this route sends a "
                          "plan it does not recognise and an offer whose checkout link "
                          "is unset")
        return None, (f"to {target.path or '/'}, which is neither the sign-up page "
                      "nor the seller")
    if 200 <= status < 300:
        return None, (f"nowhere, because the route answered HTTP {status} instead of "
                      "redirecting, and the route in this repository only ever redirects")
    if status == 404:
        return None, "nowhere, because the checkout route answered HTTP 404 and is not deployed"
    return None, f"nowhere, because the route answered HTTP {status}"


def check_checkout(repo_root: Path | None = None) -> Surface:
    """Can a stranger buy anything, read from the page a stranger is sent to.

    Two assertions in a fixed order, and **the order is the whole design**.

    First, the public pricing page has to render at least one checkout link.
    Second, every link it renders has to open when it is followed.

    The order matters because the second assertion cannot do the first one's
    job, and a future reader who drops the page fetch and probes the route
    directly will get a green report out of a shop with nothing for sale. The
    reason is in `site/app/api/checkout/[plan]/route.js`: that route asks for a
    signed-in account **before** it looks up the checkout link, so an
    unauthenticated probe of `/api/checkout/monthly` gets the same 303 to
    `/sign-up` whether the offer is configured or not. The rendered href is the
    only evidence from out here that the environment variable behind it is set,
    because `checkoutOffers` in `site/lib/polar-core.js` emits the link only
    when it holds an https URL. So the page is the artifact and the route is
    the follow-up, never the other way round.

    **Where this is stricter than the ask, and why.** The handoff that asked
    for this wanted at least one link present and answering. This fails instead
    whenever any offer in `OFFERS` has no link on the page, which is the same
    rule applied per offer rather than once. The argument for the stricter
    form is that `OFFERS` is also what renders the tiers, so a tier the owner
    does not want to sell leaves that list and stops being expected here, while
    a tier that stays on the page and cannot be bought is exactly the failure
    being watched. Half a launch reading green is how a report teaches its
    reader to stop reading it.

    **What this probe costs and touches.** One GET of a public page, plus one
    GET per link. The checkout route is a GET by design and starts no session
    that anybody is charged for, which its own comment says in so many words,
    and an anonymous probe stops at the sign-up page without ever reaching the
    seller. So this is free to run on a schedule and it spends nothing.

    **What it still cannot see.** Whether the configured URL is a live product
    at the seller. Proving that needs a session, so it is the next rung and not
    this one, and it is in `docs/ideas.md` for the day a real account exists.
    """
    status, body, _ = fetch(PRICING_URL)
    evidence: dict = {"url": PRICING_URL, "status": status}
    if status == 0:
        # Guardrail 1's distinction, and this surface had it backwards until
        # 2026-10-23. A page that never answered and a page with nothing for
        # sale are the same silence and very different facts, and the one that
        # costs something is calling the shop shut from a sandbox with no
        # egress. `check_compute` reads the same silence the same way.
        return Surface("checkout", UNKNOWN,
                       "the pricing page could not be reached from here, which "
                       f"is this checkout's network and not a verdict: {body}",
                       evidence)
    if status != 200:
        return Surface("checkout", FAILING,
                       f"/pricing returned HTTP {status}, so nobody is reading an offer "
                       "on it at all", evidence)

    linked = sorted(set(CHECKOUT_PATH_RE.findall(body)))
    offers = checkout_offers(repo_root)
    env_of = dict(offers)
    expected = [offer for offer, _ in offers]
    evidence.update({
        "linked": linked,
        "expected": expected,
        "expected_read_from": ("site/lib/polar-core.js" if offers
                               else "unreadable, so only the floor check ran"),
    })

    if not linked:
        unset = ", ".join(env_of[offer] for offer in expected)
        return Surface("checkout", FAILING,
                       "the pricing page renders no checkout link at all, so there is "
                       "nothing on it a buyer can buy"
                       + (f". Unset in the site's environment: {unset}" if unset else ""),
                       evidence)

    followed: dict[str, dict] = {}
    shut = []
    for offer in linked:
        hop_status, hop_body, headers = fetch(f"{SITE_URL}/api/checkout/{offer}", follow=False)
        location = headers.get("location", "")
        hop, why = judge_hop(hop_status, location, hop_body)
        followed[offer] = {"status": hop_status, "location": location,
                           "hop": hop, "leads": why}
        if hop is None:
            shut.append(f"{offer} leads {why}")
    evidence["followed"] = followed

    if shut:
        more = f", and {len(shut) - 1} more offer(s) in the same state" if len(shut) > 1 else ""
        return Surface("checkout", FAILING,
                       f"a checkout link on /pricing does not open a sale: {shut[0]}{more}",
                       evidence)

    missing = [offer for offer in expected if offer not in linked]
    if missing:
        names = ", ".join(f"{offer} ({env_of[offer]})" for offer in missing)
        return Surface("checkout", FAILING,
                       f"{len(linked)} of {len(expected)} offers can be bought, and the "
                       f"page advertises the others with no link behind them: {names}",
                       evidence)

    stops_at_sign_up = all(hop["hop"] == "sign-in" for hop in followed.values())
    return Surface("checkout", OK,
                   f"all {len(linked)} offer(s) on /pricing carry a checkout link and "
                   "every one of them opens"
                   + (", each at the sign-up page, which is the route asking for an "
                      "account before a card" if stops_at_sign_up else ""),
                   evidence)

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


# The newest row each sibling stage wrote, and what wrote it. Two statements
# rather than one, because the pair wanted per table is a row and not two
# aggregates, and scalar subqueries would scan each table once per column.
SIBLING_MARKERS = {
    "triage": "select created_at, model from triage_log "
              "order by created_at desc limit 1",
    "interpret": "select created_at, method from claim_links "
                 "order by created_at desc limit 1",
}


def sibling_facts(conn) -> dict | None:
    """When the two stages either side of distill last wrote, and on which model.

    Triage writes `triage_log`, interpret writes `claim_links`, and both call
    Kimi on the same Moonshot organization key distill calls
    (`pipeline/llm.py` KIMI_WINDOWS holds all four windows in one table).
    Distill's window is 15:00 UTC, after triage's 12:00 and interpret's 14:00,
    so these two rows answer the question distill's own markers cannot: whether
    the provider was answering anybody.

    The model is the half that makes the answer decisive, because every corpus
    stage falls back to Groq's free tier when Moonshot refuses (ADR-39). A
    sibling row alone proves a model answered. Which model it was separates
    "the account is up and this is distill's own job" from "the fallback
    carried the small stages and distill is the one whose payload the free tier
    cannot take".

    Fail-soft, with a stage of None where the table is empty and the whole
    block None only when a read failed. Both tables have existed since the
    first schema, so an absent one is unlikely rather than impossible, and a
    read that failed must not be able to report a stage that never wrote.
    """
    out: dict[str, dict | None] = {}
    for stage, sql in SIBLING_MARKERS.items():
        try:
            with conn.transaction():
                row = conn.execute(sql).fetchone()
        except Exception:
            return None
        out[stage] = None if row is None else {
            "newest": row[0],
            # `claim_links.method` is `model@prompt_sha`. The model half is the
            # only half this judgement asks about, and it is also the only half
            # the receipt publishes, so both readers hold the same string.
            "model": (row[1].split("@")[0] if isinstance(row[1], str) else None),
        }
    return out


def pipeline_facts(conn) -> dict:
    """When the corpus last moved, and how much is waiting to move it.

    The newest row in `papers` and in `claims`, which is the staleness, plus
    three facts that are the cause rather than the clock: the queue depths,
    when distill last marked a paper read, and when the two sibling Kimi
    stages last wrote anything. Read in that order so the cheap reads answer
    even when the views are absent.

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
        "siblings": sibling_facts(conn),
    }


def queue_cause(label: str, queues: dict | None, distilled: datetime | None = None,
                now: datetime | None = None, siblings: dict | None = None) -> str:
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
            f"and did not do it" + _unread_or_unwritten(distilled, now, siblings))


def _unread_or_unwritten(distilled: datetime | None, now: datetime | None,
                         siblings: dict | None = None) -> str:
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
            f"reached a paper" + _provider_or_cron(siblings, now))


def _age_days(value: datetime | None, now: datetime) -> float | None:
    """How old a marker is, in days to one decimal, or None when there is none."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    age = now - value
    return round(age.days + age.seconds / 86400, 1)


# Which stage writes which table, in the order their crons fire, so the
# sentence below reads in the order the day happened. `pipeline/llm.py`
# KIMI_WINDOWS is the table those windows come from.
SIBLING_STAGES = (("triage", "triage_log"), ("interpret", "claim_links"))

# The account the stall's two provider-side suspects belong to. Spelled for a
# reader rather than as the id, because the headline is read by a person.
MOONSHOT = "moonshot"


def _provider_of(model: str | None) -> str | None:
    """Which account a model id belongs to, out of pipeline/budget.py's table.

    Read rather than pattern-matched. `budget.MODELS` is the one place in this
    repository that says which provider serves which id, the deploy guard and
    every cron already trust it, and a second copy of that mapping here would
    be wrong on the day a model is added. None when the table cannot be
    imported or does not know the id, which reads as "cannot say" below and
    never as the wrong account.
    """
    if not model:
        return None
    try:
        from pipeline import budget
    except Exception:
        return None
    return (budget.MODELS.get(model) or {}).get("provider")


def _sibling_evidence(row: dict | None) -> dict | None:
    """One sibling stage, shaped for the evidence block.

    A timestamp as a string and the model beside it, so a reader of `--json`
    sees the same two facts the headline was built from. Both readers come
    through here, which is what keeps the credentialled evidence block and the
    credential-free one identical for one state.
    """
    if not row or row.get("newest") is None:
        return None
    return {"newest": str(row["newest"]), "model": row.get("model")}


def _provider_or_cron(siblings: dict | None, now: datetime | None) -> str:
    """Of the three suspects for a stage that never read, which ones survive.

    The clause this continues leaves three: distill's cron, the model
    availability gate and the spend cap. The first belongs to this job alone
    and the other two belong to the Moonshot organization key that triage,
    interpret and the press all share, so the sibling stages are the control
    that splits them. Triage runs at 12:00 UTC and interpret at 14:00, both
    before distill's 15:00, and triage writes a `triage_log` row for every
    paper it judges, a discard included.

    The model each sibling wrote on is what makes that control worth anything,
    because every corpus stage falls back to Groq's free tier when Moonshot
    refuses (ADR-39). Three answers, three different first steps. A sibling
    writing on Moonshot means the account answered and the stall is distill's
    own. A sibling whose newest row is on the Groq fallback means the account
    may be refusing everybody, and distill is the stage the fallback cannot
    carry, because ADR-39's window is 250,000 characters against a free tier of
    8,000 tokens a minute. That claim stays on the newest row rather than on
    the day, because one row per table is what these two statements read. Every sibling quiet since the same day as distill
    means one shared cause rather than three.

    `None` is "cannot say" here exactly as it is everywhere else on this
    surface, and it arrives from three places that have to stay equivalent: a
    receipt older than version 4 with no block at all, a version 4 receipt
    whose site could not run the query, and a direct read of two tables that
    are genuinely empty. A wrong first step costs more than a missing one, so
    all three keep the suspect list the stall carried before this clause.
    """
    now = now or datetime.now(timezone.utc)
    rows = [(stage, (siblings or {}).get(stage) or {}) for stage, _ in SIBLING_STAGES]
    readable = [(stage, _age_days(row.get("newest"), now), row.get("model"))
                for stage, row in rows]
    readable = [entry for entry in readable if entry[1] is not None]
    if not readable:
        return (": the cron, the model availability gate and the spend cap are "
                "the suspects, no sibling stage's marker is readable here to "
                "split them, and `modal app logs alexandria-distill` is where "
                "they show")
    said = " and ".join(
        [f"{stage} last wrote {days} days ago{_on(model)}" if i == 0
         else f"{stage} {days} days ago{_on(model)}"
         for i, (stage, days, model) in enumerate(readable)])
    fresh = [entry for entry in readable if entry[1] <= PIPELINE_STALE_DAYS]
    if not fresh:
        return (f": {said}, so every stage on the shared Moonshot key went "
                f"quiet together, which makes the account, its key and its "
                f"daily token allowance the first place to look rather than "
                f"distill's cron")
    providers = {_provider_of(model) for _, _, model in fresh}
    if MOONSHOT in providers:
        return (f": {said}, so the Moonshot account answered a caller after "
                f"distill stopped, which leaves this job's own cron, its "
                f"deploy and its caps rather than the provider, and `modal app "
                f"logs alexandria-distill` is where they show")
    if providers and None not in providers:
        return (f": {said}, which is the Groq fallback and not Moonshot, so "
                f"the account is the first place to look: distill is the one "
                f"stage the fallback cannot carry, because ADR-39's window is "
                f"250,000 characters against a free tier of 8,000 tokens a "
                f"minute")
    return (f": {said}, and no table here says which account served that, so "
            f"the cron, the availability gate and the spend cap all stand: "
            f"`modal app logs alexandria-distill` is where they show")


def _on(model: str | None) -> str:
    """` on kimi-k2.6`, or nothing at all when the row did not record one."""
    return f" on {model}" if model else ""


def judge_pipeline(facts: dict, now: datetime | None = None,
                   source: str = DIRECT, compute: str | None = None) -> Surface:
    """The daily crons, read through the rows they leave behind.

    delivery-health.md's own table calls this the next gap and says why it
    matters most: it is the surface that feeds every other one. A press that
    prints on an empty corpus prints an empty issue.

    `compute` is the one thing the rows cannot say. Every judgement below is
    about how long ago a row arrived, and the window is two days, so a pipeline
    whose platform was switched off an hour ago is indistinguishable here from
    one that is running perfectly. It is passed in as a fact rather than probed
    for, so this stays a function of what it is given and keeps its tests.
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
    # Out of the loop for the same reason, and it matters more here: these are
    # two other stages' timestamps, and this surface raises on the corpus
    # tables. Left in `rows` they would make a quiet interpret run read as a
    # third stale table and report one outage twice.
    siblings = rows.pop("siblings", None)
    # One shape for "cannot say", collapsed here rather than at either reader.
    # A failed query hands this None, a version 3 receipt has no fields to hand
    # it, and two genuinely empty tables hand it two nulls. All three mean the
    # same thing, and leaving them in three shapes is how the credentialled
    # reader and the credential-free one grow different evidence blocks for one
    # state.
    if siblings is not None and not any(
            (siblings.get(stage) or {}).get("newest") for stage, _ in SIBLING_STAGES):
        siblings = None
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
                         + queue_cause(label, queues, distilled, now, siblings))
    # In the evidence on every path, including the healthy one. A queue that is
    # deep while the corpus still moves is not an alarm by this surface's own
    # unit, which is staleness, and inventing a depth threshold here would be a
    # second alarm nobody asked for. It is a number a reader wants beside the
    # dates, so it is reported and not judged.
    evidence["queues"] = queues
    # Beside the depths and on every path, for the same reason they are: it is
    # a number a reader wants next to the dates, and it is not judged here.
    evidence["distilled"] = str(distilled) if distilled is not None else None
    # Same rule again: reported on every path, judged on none. A seat reading
    # the evidence block wants the two dates next to the three above even when
    # the corpus is moving and nothing is wrong.
    evidence["siblings"] = (None if siblings is None else
                            {stage: _sibling_evidence(siblings.get(stage))
                             for stage, _ in SIBLING_STAGES})
    # On every path, judged on one. A reader looking at fresh rows deserves to
    # see whether the thing that produced them can still run.
    evidence["compute"] = compute
    if stale:
        return Surface("pipeline", FAILING, "; ".join(stale), evidence)
    if compute:
        return Surface("pipeline", FAILING,
                       f"every row above predates an outage that is still "
                       f"running: {compute}. Nothing reads as stale yet because "
                       f"staleness takes {PIPELINE_STALE_DAYS} days to show and "
                       "the crons stopped hours ago", evidence)
    return Surface("pipeline", OK,
                   f"ingesting and distilling within {PIPELINE_STALE_DAYS} days", evidence)


def check_pipeline(conn, compute: str | None = None) -> Surface:
    return judge_pipeline(pipeline_facts(conn), compute=compute)


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


def _is_shallow(repo_root: Path) -> bool:
    """Does this checkout hold a truncated history.

    Asked rather than inferred, because every message this surface prints
    about an undatable drift used to guess at the cause ("usually a shallow
    clone") and a guess is not a next step. `git rev-parse
    --is-shallow-repository` answers it in one call and has since git 2.15,
    and a git that does not understand the flag answers non-zero, which
    reads here as "cannot say", which is the honest answer rather than
    `False`.

    The reason this is worth a function of its own is that the answer
    changed under the org without any file in this repository changing.
    Until 2026-10-17 every seat's run was a GitHub workflow checking out
    with `fetch-depth: 0`, so full history was a property of the runtime and
    this question had one answer everywhere it mattered. `ab4e5bb` moved
    every seat's cadence to the host manifests, the host clones one commit
    deep, and three guards went quiet without a line of their own code
    moving (INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone,
    INC-2026-10-23-the-drift-guard-answered-green-from-a-checkout-that-could-not-see).
    """
    status, out = _git(repo_root, "rev-parse", "--is-shallow-repository")
    return status == 0 and out.strip() == "true"


#: What closes an undatable drift, for the reader who has one. Named rather
#: than described, the way every other unknown on this surface has named its
#: one command since 2026-10-24.
UNSHALLOW = "git fetch --unshallow"

#: Set to anything non-empty to forbid the deepening fetch below. For a run
#: that must not touch the network, and for the tests, which assert on both
#: branches and must never depend on a remote being reachable.
NO_FETCH_ENV = "DELIVERY_HEALTH_NO_FETCH"

#: How long the deepening fetch may take before it is abandoned. Measured
#: rather than guessed: 4.5 seconds for this repository's whole history, 2,327
#: commits and 24 MB, on 2026-10-24. Ninety seconds is twenty times that, so
#: the ceiling is here to stop a hung transport from taking the standup down
#: and not to ration a cost anybody has met.
DEEPEN_TIMEOUT_SECONDS = 90

#: One attempt per process, remembered here. `judge_deploy` is called once per
#: run today, but `tools/drift_watch.py` and the PM's standup both reach it
#: through different doors, and a retry loop that re-fetches on every call
#: would turn a 4.5 second cost into an unbounded one.
_deepen_attempted: dict[str, bool] = {}


def _deepen(repo_root: Path) -> bool:
    """Fetch the history this checkout is missing. True when it worked.

    Why a guard does network I/O, which is the fair question to ask of it.
    This surface already reads <https://libraryofalexandria.dev/api/delivery>
    on every run that has no database credential, so a fetch is not a new
    category of behaviour for this file. And the alternative has been measured
    for six days: the `deploy` row reads `unknown` from every seat's run,
    because the host clones one commit deep, and the one command that answers
    it is a command no seat ever runs.

    That left the only surface watching production answering a question nobody
    asked it. On 2026-10-18 the PM read 44.7 hours off the standing Deploy
    card's body while the truth was 8.2 days, and the correction came from a
    seat that had run `git fetch --unshallow` by hand. Naming the command was
    yesterday's fix (#436) and it is strictly better than guessing, but a
    guard that tells its reader to go and re-run it by hand has moved the work
    rather than done it. Four and a half seconds is cheaper than a wrong
    number in a card body for six days.

    It degrades to exactly the behaviour it replaced. No remote, no network, a
    git too old for the flag, or `DELIVERY_HEALTH_NO_FETCH` set: this returns
    False, the checkout stays shallow, and every message downstream is the one
    this file printed before today, which names `UNSHALLOW` for a reader who
    can run it in a place where the fetch could not.
    """
    import os
    import subprocess

    key = str(repo_root)
    if key in _deepen_attempted:
        return _deepen_attempted[key]
    if os.environ.get(NO_FETCH_ENV):
        _deepen_attempted[key] = False
        return False
    try:
        done = subprocess.run(
            ["git", "-C", key, "fetch", "--unshallow", "--quiet"],
            capture_output=True, text=True,
            timeout=DEEPEN_TIMEOUT_SECONDS)
        ok = done.returncode == 0
    except (OSError, subprocess.SubprocessError):
        ok = False
    # Asked again rather than trusted: a fetch can exit 0 and leave a
    # repository shallow if the remote itself is a shallow mirror, and the
    # thing the caller needs to know is whether the history is here now.
    _deepen_attempted[key] = ok and not _is_shallow(repo_root)
    return _deepen_attempted[key]


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
    available history ever touched. It degrades to `unknown` rather than to a
    guess.

    This docstring used to end "the seat workflows check out with
    `fetch-depth: 0`, so in the place this actually runs daily the answer is
    real". That sentence was true when it was written and stopped being true
    on 2026-10-17, when `ab4e5bb` moved every seat's cadence off GitHub
    schedules and onto the host manifests. The workflow files still say
    `fetch-depth: 0` and they are no longer what checks out a scheduled run;
    the host clones one commit deep. So the daily place this runs is exactly
    the shallow case the old sentence promised it was not, and the promise
    was part of why nobody looked. `_is_shallow` is the replacement, and it
    asks rather than assuming.
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


def drift_began(found: dict, changed_at: datetime) -> tuple[datetime, str]:
    """When this app's deploy started being late, and which fact says so.

    The grace window exists so that a merge at noon is not an alarm at one.
    It was measured from `changed_at`, the newest commit on the trunk to touch
    the app's files, and that is the wrong end of the drift. A merge resets
    that clock. An app eleven days behind therefore reads "inside the 24h
    window" on any day somebody touches its files, and in a repository where
    every seat commits daily that is every day.

    The press is what it cost. `weekly`'s running image was built from
    `3bbf430` of 2026-10-04. The degraded-edition repair for
    `INC-2026-10-12-the-press-had-no-degraded-path-and-the-week-got-no-issue`
    merged on 2026-10-12 and never reached a container, the Monday cron of
    2026-10-12 printed nothing, and this surface said `ok, a deploy is pending
    and still inside the 24h window: weekly (20.7h)` for every one of those
    days. Eleven days of drift, reported as twenty hours, because a later
    commit kept moving the number the verdict was read off.

    So the anchor is the OLDEST undeployed commit: the moment the running
    image stopped being the trunk. `undeployed_commits` already recovers it
    and already puts it in the evidence, which is the detail that makes this a
    dating bug rather than a missing measurement. The number was on the page
    the whole time, next to the one the verdict used.

    Falls back to `changed_at` whenever the walk could not recover the
    deployed commit, which is a shallow clone or a digest matching nothing in
    range. That is the old behaviour, and keeping it is deliberate: a guard
    that cannot date a drift should under-report rather than invent one. The
    returned label says which of the two answered, so a reader never has to
    guess which question the number is answering.
    """
    commits = found.get("commits")
    if commits:
        oldest = _parse_iso(commits[-1].get("at"))
        if oldest:
            return oldest, "the oldest undeployed commit"
    return changed_at, "the newest commit to the app's files"


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


def recording_asked_at(repo_root: Path, app: str, ref: str = "HEAD") -> dict:
    """When the trunk started asking this app to record a runtime.

    The answer is a date and the commit that carries it, or a `why`. It exists
    because "this app has no row" has two causes that look identical in the
    table and are opposites in production.

    One is an app that cannot record: it is in `runtime_sha.APPS` and its
    module never calls `record_runtime`, so no deploy of it will ever write a
    row and the age of its code says nothing about the age of its image. That
    is unmeasured, and this function returns a `why` for it.

    The other is an app whose own code has asked it to record since a datable
    commit, and which has still never recorded. A deploy built from that commit
    or anything after it writes its row on its first run. So no row means the
    running image predates that commit, which makes the age of that commit a
    lower bound on the age of the deploy. That is drift, and it is the state
    `distill` and `ingest` were in for five days while this guard called them
    unmeasured and said nothing (`INC-2026-10-14-the-two-apps-the-drift-guard-
    could-not-see`).

    The pickaxe takes the newest commit that changed the call rather than the
    oldest, which is the conservative end: a later edit to that line cannot
    make the image younger than it is, and dating from the original add would
    report an age the evidence does not carry.
    """
    from pipeline import runtime_sha

    module = runtime_sha.APPS[app]
    status, out = _git(repo_root, "log", "-1", "--format=%h%x1f%cI",
                       "-S", f'record_runtime(conn, "{app}"', ref,
                       "--", module)
    if status != 0:
        return {"why": f"git could not read {module} at {ref} here"}
    if not out:
        return {"why": f"no commit in this history adds a record_runtime call "
                       f"to {module}"}
    short, _, when = out.partition("\x1f")
    try:
        at = datetime.fromisoformat(when).astimezone(timezone.utc)
    except ValueError:
        return {"why": f"the commit that added the call ({short}) has no "
                       f"readable date here"}
    return {"sha": short, "at": at}


def undeployed_since(repo_root: Path, app: str, commit: str,
                     limit: int = DEPLOY_HISTORY_LIMIT,
                     ref: str = "HEAD") -> dict:
    """The commits an image older than `commit` cannot contain.

    `undeployed_commits` recovers the deployed commit by replaying digests
    until one matches what the container reported. An app that has never
    reported has no digest to match, so that walk cannot start, and until now
    the answer stopped at "there is no deployed state to diff against". There
    is still no deployed commit here, and there is a bound: everything from
    `commit` forward that touched this app's files is undeployed, because the
    image predates `commit` by the argument in `recording_asked_at`.

    A bound is worth naming. "distill is 5 days behind" does not tell the
    owner that the five days contain the three fixes to the thing that is
    broken, and `name_unrecorded` puts them in the headline.
    """
    paths = _paths_at(repo_root, app, ref)
    if paths is None:
        from pipeline import runtime_sha
        return {"why": f"{runtime_sha.APPS[app]} cannot be read at {ref} here"}
    # `commit^..ref` would drop `commit` itself, and `commit` is undeployed too.
    status, out = _git(repo_root, "log", f"-{limit}",
                       "--format=%H%x1f%h%x1f%s%x1f%cI",
                       f"{commit}~1..{ref}", "--", *paths)
    if status != 0:
        # A root commit has no `~1`, and a shallow clone may not have the
        # parent either. Both are a reason to name nothing rather than to
        # guess at a range.
        return {"why": f"this checkout cannot list the commits since {commit}"}
    commits = []
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 4:
            commits.append({"sha": parts[1], "subject": parts[2], "at": parts[3]})
    return {"asked_in": commit, "commits": commits, "searched": len(commits)}


def name_unrecorded(found: dict, limit: int = DEPLOY_NAMED_COMMITS) -> str:
    """The same clause as `name_undeployed`, for an app with no row at all.

    Empty string when there is nothing trustworthy to say, so a caller can
    append it unconditionally.
    """
    if "commits" not in found:
        return ""
    commits = found["commits"]
    if not commits:
        return ""
    named = ", ".join(f"{c['sha']} {c['subject']}" for c in commits[:limit])
    rest = len(commits) - limit
    plural = "commit" if len(commits) == 1 else "commits"
    return (f"{len(commits)} undeployed {plural} since {found['asked_in']}: "
            f"{named}" + (f", and {rest} more" if rest > 0 else ""))


# Modal reads every cron in UTC, which is also the only clock in this file, so
# a schedule parsed out of a decorator needs no timezone argument.
#
# This evaluator covers `*`, a comma list, a range and a step, which is every
# shape the five deployed schedules use and a fair margin past it. Anything
# else returns None rather than a guess, because the whole value of the number
# it produces is that a reader can act on it: a deadline computed from a field
# this code misread is worse than no deadline at all, and "nothing here can
# read that schedule" is an answer a caller can print.
def _cron_field(spec: str, low: int, high: int) -> set[int] | None:
    """One cron field as the set of values it matches, or None if unreadable."""
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            return None
        step = 1
        if "/" in part:
            part, _, raw = part.partition("/")
            if not raw.isdigit() or int(raw) < 1:
                return None
            step = int(raw)
        if part == "*":
            first, last = low, high
        elif "-" in part.lstrip("-"):
            start, _, end = part.partition("-")
            if not (start.isdigit() and end.isdigit()):
                return None
            first, last = int(start), int(end)
        elif part.isdigit():
            first = last = int(part)
        else:
            return None
        if first > last or first < low or last > high:
            return None
        out.update(range(first, last + 1, step))
    return out or None


def parse_cron(expr: str) -> dict | None:
    """A five-field cron expression as sets, or None if this cannot read it.

    Day-of-week is 0-6 with 0 as Sunday, which is what Modal accepts, and 7 is
    normalised to Sunday too because crontab has always allowed both.
    """
    fields = (expr or "").split()
    if len(fields) != 5:
        return None
    bounds = [("minute", 0, 59), ("hour", 0, 23), ("dom", 1, 31),
              ("month", 1, 12), ("dow", 0, 7)]
    parsed = {}
    for spec, (name, low, high) in zip(fields, bounds):
        values = _cron_field(spec, low, high)
        if values is None:
            return None
        parsed[name] = values
        parsed[f"{name}_any"] = spec.strip() == "*"
    parsed["dow"] = {0 if v == 7 else v for v in parsed["dow"]}
    return parsed


def next_fire(expr: str, now: datetime) -> datetime | None:
    """The first minute at or after `now` that this cron fires, or None.

    Day-of-month and day-of-week are OR'd when both are restricted and AND'd
    when either is `*`, which is crontab's own rule and is the one piece of
    this that surprises people. None of the five deployed schedules restricts
    both, so the branch is here to be correct rather than because it is
    exercised in production.

    Searches forward a day at a time and only inside the hours and minutes the
    expression allows, so the walk is bounded by the days in the window rather
    than by the minutes in it.
    """
    cron = parse_cron(expr)
    if cron is None:
        return None
    start = now.astimezone(timezone.utc).replace(second=0, microsecond=0)
    hours, minutes = sorted(cron["hour"]), sorted(cron["minute"])
    # Four years, so that a 29 February in the expression is answered rather
    # than reported unreachable.
    for offset in range(0, 366 * 4 + 1):
        day = (start + timedelta(days=offset)).date()
        if day.month not in cron["month"]:
            continue
        # Python's Monday-is-0 to cron's Sunday-is-0.
        dow = (day.weekday() + 1) % 7
        by_dom, by_dow = day.day in cron["dom"], dow in cron["dow"]
        if cron["dom_any"] or cron["dow_any"]:
            if not (by_dom and by_dow):
                continue
        elif not (by_dom or by_dow):
            continue
        for hour in hours:
            for minute in minutes:
                when = datetime(day.year, day.month, day.day, hour, minute,
                                tzinfo=timezone.utc)
                if when >= start:
                    return when
    return None


def next_run(app: str, repo_root: Path, now: datetime) -> dict:
    """When this app's cron next fires, as the deploy surface reports it.

    Returns `{"cron": ..., "at": ..., "hours": ...}` or `{"why": ...}`. The
    reason this exists at all is that a drift measured only backwards cannot
    be acted on: "weekly is 8.7 days behind" and "weekly next runs in 41
    hours" are the same fact, and only the second one says whether a deploy
    tomorrow is in time. The ExO seat wrote that sentence onto the compute
    card by hand on 2026-10-24, having worked out the press cron from the
    docstring, which is the work this function is here to stop repeating.
    """
    try:
        from pipeline import runtime_sha
    except Exception as exc:
        return {"why": f"pipeline/runtime_sha.py could not be read here: {exc}"}
    found = runtime_sha.schedule_of(app, repo_root)
    if "cron" not in found:
        return found
    when = next_fire(found["cron"], now)
    if when is None:
        return {"cron": found["cron"],
                "why": f"this cron expression cannot be read here: "
                       f"{found['cron']}"}
    return {"cron": found["cron"], "at": when,
            "hours": round((when - now).total_seconds() / 3600, 1)}


def deadline_phrase(entry: dict) -> str:
    """How a next run reads in a headline or on a card, or "" when unknown."""
    if not entry or "at" not in entry:
        return ""
    return (f"{entry['at']:%Y-%m-%d %H:%M} UTC, "
            f"{_ageing_hours(entry['hours'])} from now")


def _ageing_hours(hours: float | None) -> str:
    """Hours as the unit a reader thinks in."""
    if hours is None:
        return "an unknown time"
    if hours < 1:
        return "under an hour"
    if hours < 48:
        return f"{round(hours, 1)}h"
    return f"{round(hours / 24, 1)} days"


def _soonest(apps: list[str], deadlines: dict,
             compute: str | None = None) -> str:
    """The first of these stale apps to serve a real run, as a sentence.

    Returns "" when none of them has a readable schedule, because a headline
    that says "the next run could not be computed" spends a reader's attention
    on the instrument instead of on the deploy. The per-app evidence carries
    the `why` for anyone who wants it.

    One app named rather than all of them. The reader of this headline has one
    action, which is a deploy, and what they need from it is the moment after
    which running it is too late.
    """
    dated = [(deadlines[app]["at"], app) for app in apps
             if "at" in (deadlines.get(app) or {})]
    if not dated:
        return ""
    when, app = min(dated)
    if compute:
        return (f"On the schedule the first of these to serve a run would be "
                f"{app}, {deadline_phrase(deadlines[app])}, but nothing is "
                f"firing at all: {compute}. So that is the deadline from the "
                f"moment compute is back rather than a time to work to. ")
    return (f"The first of these to serve a real run is {app}, which fires "
            f"{deadline_phrase(deadlines[app])}, so a deploy after that is a "
            f"run too late. ")


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
                 source: str = DIRECT, compute: str | None = None) -> Surface:
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

    `compute` is the platform outage, when there is one, in the same shape
    `judge_pipeline` already takes it. It is here because this surface now
    reports a deadline, and a deadline read off a cron is a claim that the cron
    fires. On 2026-10-24 the Modal workspace was disabled and none of the five
    did, so an unqualified "weekly fires Monday 09:00" would have been the
    guard inventing a schedule out of a decorator.
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

    evidence = {"read_via": source, "ref": ref, "compute_outage": compute}
    # Asked once for the whole surface rather than once per app: the answer is
    # a property of the checkout, not of an app, and it is what turns "cannot
    # be dated" from a dead end into one command.
    shallow = _is_shallow(root)
    # And if it is shallow, fetch what is missing before judging anything,
    # because the answer below is only as good as the history behind it and
    # every seat's checkout arrives one commit deep. `deepened` is in the
    # evidence because the fetch is a side effect on the reader's repository
    # and a guard should say when it changed something rather than leave it to
    # be discovered.
    import os

    evidence["deepened"] = False
    # Forbidding the fetch is a different fact from the fetch failing, and the
    # words below differ on it, so the switch is read here rather than
    # inferred from a False return that means both.
    fetch_forbidden = bool(os.environ.get(NO_FETCH_ENV))
    evidence["fetch_forbidden"] = fetch_forbidden
    tried_to_deepen = False
    if shallow and not fetch_forbidden:
        tried_to_deepen = True
        evidence["deepened"] = _deepen(root)
        if evidence["deepened"]:
            shallow = False
    evidence["shallow_checkout"] = shallow
    # Still shallow, which now has two causes that need different words. The
    # fetch was forbidden, and the reader can run it; or the fetch was tried
    # from here and failed, and telling that reader to run the command this
    # process just ran would be advice the surface already knows is wrong.
    # Both still name the command, because the reader is often somewhere the
    # run was not.
    failed_to_deepen = shallow and tried_to_deepen
    remedy_short = (f"{UNSHALLOW} could not complete here" if failed_to_deepen
                    else UNSHALLOW)
    remedy_long = (f"`{UNSHALLOW}` was tried from here and did not complete"
                   if failed_to_deepen
                   else f"`{UNSHALLOW}` and ask again")
    # Asked once per app, before anything else about it is judged, because
    # every branch below wants it and none of them can reach it: an app that
    # has never recorded and an app eight days behind have the same deadline,
    # which is the next time its cron fires. Five file reads and some
    # arithmetic, no network, no git.
    deadlines = {app: next_run(app, root, now) for app in sorted(runtime_sha.APPS)}
    evidence["schedules"] = {
        app: (entry.get("cron") or entry.get("why"))
        for app, entry in deadlines.items()}

    drifted, unknowns, alarms = [], [], []
    # The apps in `drifted`, as names rather than as the prose that describes
    # them, because the grace-window question below is about an app's clock and
    # `drifted` holds sentences.
    pending: list[tuple[str, float]] = []
    # Alarms that cannot be mailed, kept apart from the ones that can. The
    # cooldown lives in `deploy_runtime.notified_at`, so an app with no row
    # has nowhere to remember that it was mailed, and this file already
    # refuses to mail without a cooldown on the receipt path for the same
    # reason: one mail every time a seat runs the standup is not an alarm.
    blind = []
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
        due = deadlines.get(app) or {}
        here = {"expected_sha": local, "files": len(keys), "ref": ref,
                "recorded_sha": row["runtime_sha"] if row else None,
                "last_run": str(row["recorded_at"]) if row else None,
                "cron": due.get("cron"),
                "next_run_at": str(due["at"]) if "at" in due else None,
                "next_run_in_hours": due.get("hours"),
                "next_run_why": due.get("why")}

        # Never recorded is a third state, and the question it turns on is
        # not whether a row exists. It is whether the code at `ref` asks for
        # one. `recording_asked_at` is the whole argument; the short version
        # is that an app whose module calls `record_runtime` writes its row on
        # the first run of any deploy built from that commit, so no row means
        # the image predates it, and the age of that commit is a lower bound
        # on the age of the deploy.
        #
        # This branch read UNKNOWN for both causes from 2026-10-09 to today,
        # on the reasoning that dating an unmeasured app from its last commit
        # cries wolf. That reasoning was right about the number and wrong
        # about the state, and `ingest` was the case it was written against:
        # it had never recorded because the deploy that would have recorded
        # had not happened. Neither had `distill`'s. The guard called them
        # unmeasured for five days while the stage that fills `claims` ran an
        # image from before 2026-10-09, which is before all three fixes to
        # the fallback pacing that was stopping it. The press printed nothing
        # on 2026-10-12 and nothing on launch day because of it, and the one
        # surface that could have named the cause was the one holding its
        # tongue. INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see.
        #
        # Only when something else did record, and that condition is the whole
        # of the distinction. An EMPTY table is not five unmeasured apps, it is
        # a recorder that has never worked, and that is a failure this guard
        # must keep shouting about: `test_a_job_that_never_reported_is_treated
        # _as_drift` has held that line since the guard shipped and it still
        # holds it. One app missing among four that reported is a gap in
        # coverage. Every app missing is a gap in the mechanism.
        if row is None and rows:
            asked = recording_asked_at(root, app, ref)
            if "at" not in asked:
                why = ("has never recorded a runtime and nothing in its code "
                       f"asks it to ({asked['why']}), so this app is "
                       "unmeasured rather than behind: modal deploy "
                       f"{runtime_sha.APPS[app]}")
                here.update(state=UNKNOWN, why=why)
                unknowns.append(f"{app} (never recorded)")
                evidence[app] = here
                continue
            age_hours = (now - asked["at"]).total_seconds() / 3600
            found = undeployed_since(root, app, asked["sha"], ref=ref)
            named = name_unrecorded(found)
            here.update(state=FAILING if age_hours > DEPLOY_GRACE_HOURS else OK,
                        asked_in=asked["sha"], asked_at=str(asked["at"]),
                        drift_hours=round(age_hours, 1), undeployed=found,
                        why=("has never recorded a runtime, and "
                             f"{asked['sha']} asked it to "
                             f"{round(age_hours / 24, 1)} days ago, so the "
                             "running image is at least that old: modal "
                             f"deploy {runtime_sha.APPS[app]}"))
            evidence[app] = here
            if age_hours > DEPLOY_GRACE_HOURS:
                blind.append((app, round(age_hours / 24, 1), asked["sha"], named))
            else:
                pending.append((app, age_hours))
                drifted.append(f"{app} (asked to record {round(age_hours, 1)}h "
                               "ago and has not run since)")
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

        # Only here, and never on the green path: the walk costs git processes
        # and an app that matches has nothing to name.
        found = undeployed_commits(root, app,
                                   row["runtime_sha"] if row else None,
                                   ref=ref)
        named = name_undeployed(found)
        since, anchor = drift_began(found, changed_at)
        age_hours = (now - since).total_seconds() / 3600

        # A drift the replay could not date, measured from the wrong end and
        # landing inside the window, is not a green app. It is an unanswered
        # question, and until 2026-10-23 it answered OK.
        #
        # The cost was total and it was invisible. Every agent seat runs from
        # a shallow clone, `git clone --depth 1`, which has one commit of
        # history, so `undeployed_commits` can never match the running digest
        # and `drift_began` always falls back to the newest commit to the
        # app's files, which in a shallow clone is that single commit and is
        # therefore hours old. The same tree, the same rows, the same moment:
        # shallow read `ok, a deploy is pending and still inside the 24h
        # window: distill (0.1h), ingest (0.1h), weekly (0.1h)`, and the same
        # checkout after `git fetch --unshallow` read three apps between 7.3
        # and 8.2 days behind. So the drift alarm was silent for every reader
        # it has, which is every seat, and `tools/drift_watch.py` exited 0 on
        # a press job eight days behind.
        #
        # `drift_began` is right that a guard which cannot date a drift should
        # under-report rather than invent one. That argument is about the
        # number. This is about the state: an undated app whose fallback clock
        # already puts it past the window still alarms, exactly as before, and
        # only the one that would have been called fine on a clock it cannot
        # trust goes to `unknown`.
        if age_hours <= DEPLOY_GRACE_HOURS and "commits" not in found:
            here.update(state=UNKNOWN, merged_at=str(changed_at),
                        drift_began=str(since), drift_anchor=anchor,
                        drift_hours=round(age_hours, 1), undeployed=found,
                        shallow_checkout=shallow,
                        why=("the running image matches no commit this "
                             "checkout can see, so the only clock left is the "
                             "newest commit to this app's files and that says "
                             "nothing about how far behind production is: "
                             + str(found.get("why", ""))
                             + (f". This checkout is a shallow clone, so "
                                f"{remedy_long}"
                                if shallow else "")))
            unknowns.append(
                f"{app} (the drift cannot be dated from this checkout"
                + (f", which is shallow: {remedy_short}" if shallow else "")
                + ")")
            evidence[app] = here
            continue

        here.update(state=FAILING if age_hours > DEPLOY_GRACE_HOURS else OK,
                    merged_at=str(changed_at), drift_began=str(since),
                    drift_anchor=anchor, drift_hours=round(age_hours, 1),
                    undeployed=found)
        evidence[app] = here
        if age_hours > DEPLOY_GRACE_HOURS:
            alarms.append((app, round(age_hours / 24, 1), row, local, named))
        else:
            pending.append((app, age_hours))
            inside = f"{round(age_hours, 1)}h" + (f", {named}" if named else "")
            drifted.append(f"{app} ({inside})")

    # A pending deploy is forgiven for a day because a merge at noon is not an
    # alarm at one. That reasoning holds only while nothing actually runs
    # inside the day. Four of the five jobs here are daily, so their next run
    # nearly always lands inside the window, which means the window quietly
    # guarantees the undeployed image serves at least one production run before
    # this guard says a word.
    #
    # Moving the threshold is the owner's call and not this function's, so the
    # state here is unchanged: what used to be silent is now said out loud
    # every time it is true, and the decision sits with whoever reads it.
    early = []
    for app, age_hours in pending:
        due = deadlines.get(app) or {}
        if due.get("hours") is None:
            continue
        left = DEPLOY_GRACE_HOURS - age_hours
        if due["hours"] <= left:
            early.append(f"{app} fires {deadline_phrase(due)}, inside the "
                         f"{round(left, 1)}h of grace it has left")
    evidence["fires_inside_grace"] = early

    if alarms or blind:
        names = "; ".join(
            [f"{app} is {days} days behind" + (f" ({named})" if named else "")
             for app, days, _, _, named in alarms]
            + [f"{app} has never recorded a runtime and {sha} asked it to "
               f"{days} days ago, so its image predates {sha}"
               + (f" ({named})" if named else "")
               for app, days, sha, named in blind])
        if alarms and notify_conn is not None:
            note = _notify_drift(notify_conn, alarms, root, now)
        elif alarms and source == DIRECT:
            note = "not notified"
        elif alarms:
            note = (f"not mailed: these rows came from {source}, which cannot "
                    "write the once-a-day cooldown, and an alarm with no "
                    "cooldown is one mail every time the standup runs")
        else:
            note = ""
        if blind:
            withheld = ("the apps with no row are not mailed: the cooldown is "
                        "a column on the row they do not have, and an alarm "
                        "with no cooldown is one mail every time the standup "
                        "runs. This surface is where they are read")
            note = f"{note}. {withheld}" if note else withheld
        evidence["alarm"] = note
        # The undated apps ride along on the FAILING headline rather than
        # being dropped by it. This branch is tested ahead of `unknowns` and
        # used to return without ever mentioning them, so a run that could
        # measure one app and not another reported the one it could and said
        # nothing at all about the other. That is
        # INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see one layer
        # down, and company standard L-A21 in its own words: a gate that saw
        # nothing must not read as a quiet pass. A reader told "weekly is 8
        # days behind" and not told "distill could not be measured" has been
        # given a verdict on production and a blank where its scope should be.
        blind_note = ("; and the deploy cannot be compared from here for: "
                      + "; ".join(unknowns)) if unknowns else ""
        # The deadline, which is the half of this that can be acted on. Every
        # number above this line is backwards-looking: it says how stale the
        # image is and nothing about whether a deploy tomorrow is in time.
        soonest = _soonest([app for app, *_ in alarms]
                           + [app for app, *_ in blind], deadlines, compute)
        return Surface("deploy", FAILING,
                       f"the deployed code is not {ref}: {names}{blind_note}. "
                       f"{soonest}{note}", evidence)
    if unknowns:
        return Surface("deploy", UNKNOWN,
                       "the deploy cannot be compared from here: "
                       + "; ".join(unknowns), evidence)
    if drifted:
        return Surface("deploy", OK,
                       f"a deploy is pending and still inside the "
                       f"{DEPLOY_GRACE_HOURS}h window: {', '.join(drifted)}"
                       + (f"; and the window outlasts the schedule for "
                          f"{'; '.join(early)}, so the grace runs out after "
                          "the undeployed image has already served a run"
                          if early else ""),
                       evidence)
    return Surface("deploy", OK,
                   f"all {len(runtime_sha.APPS)} jobs are running {ref}",
                   evidence)


def check_deploy(conn, repo_root: Path | None = None,
                 now: datetime | None = None, notify: bool = True,
                 compute: str | None = None) -> Surface:
    return judge_deploy(deploy_facts(conn), repo_root, now,
                        notify_conn=conn if notify else None, compute=compute)


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


# ------------------------------------------------------------- the till
#
# Whether a verified payment turned into access. This is the one surface here
# that is not about the product reaching a reader; it is about a reader
# reaching the product, and it fails in the same shape as everything else on
# this page. Polar is the Merchant of Record (ADR-30), so /api/polar-webhook is
# the only place this product learns anybody paid, and its two unrecoverable
# outcomes used to end in a Vercel function log that nothing in this org reads.
# `payment_exceptions` gives them a row and this reads the open ones.

PAYMENT_TOTALS = """
    select count(*),
           count(*) filter (where not retryable),
           min(occurred_at),
           max(last_seen_at)
    from payment_exceptions
    where resolved_at is null
"""

PAYMENT_CODES = """
    select reason_code, count(*)
    from payment_exceptions
    where resolved_at is null
    group by reason_code
    order by count(*) desc, reason_code
"""


def payment_facts(conn) -> dict | str | None:
    """The open exceptions, or why they could not be read.

    A dict of counts, or one of the three reasons in `UNREADABLE_HANDS` when
    the read failed, which is the same shape `deploy_facts` has always had and
    for the same reason. None stays reachable for the one case that is neither:
    a read that worked and returned no row at all.

    None rather than zeroes, the same contract `queue_facts` keeps and for the
    same reason: `payment_exceptions` is newer than every other table this file
    reads and `apply_schema` is a hand step, so a database without it is a
    state this really meets. A count of zero is the good news this surface
    exists to confirm, and it is only good news when somebody looked.

    Both reads run inside one `conn.transaction()`, which is a savepoint when
    the caller is already in a transaction, and that is load-bearing rather
    than tidy. A failed statement in psycopg aborts the whole transaction, and
    `check_deploy` runs after this on the same connection, so without the
    savepoint a missing `payment_exceptions` would take the deploy surface down
    with it and the drift alarm would fire on a schema step. `queue_facts`
    carries the same comment because it met the same thing first.
    """
    try:
        with conn.transaction():
            total = conn.execute(PAYMENT_TOTALS).fetchone()
            codes = conn.execute(PAYMENT_CODES).fetchall()
    except Exception as exc:
        # The reason and not a bare None, so this reader reaches the same first
        # step the receipt's `unreadable.payments` gives the credential-free
        # one. `why_unreadable` reads the sqlstate and never the message.
        return why_unreadable(exc)
    if total is None:
        return None
    return {"unresolved": total[0], "needs_a_hand": total[1],
            "oldest": total[2], "newest": total[3],
            "codes": [{"code": row[0], "n": row[1]} for row in codes]}


def _name_codes(codes: list | None) -> str:
    """The reason codes as a clause, so the headline names the job.

    "3 payments unmatched" tells the owner a number. "2 no_account, 1
    ambiguous_email" tells her that two people need inviting and one duplicate
    needs merging, which are different half-hours of her afternoon. L-E11's
    rule that a guard reports the smallest true thing applies to what it
    reports as well as to how loud it is.
    """
    named = [f"{row['n']} {row['code']}" for row in (codes or [])
             if row.get("code") and row.get("n")]
    return ", ".join(named)


def judge_payments(facts: dict | str | None, now: datetime | None = None,
                   source: str = DIRECT) -> Surface:
    """Open payment exceptions, against what will clear itself.

    Three states and the middle one is the one worth being careful about.

    A row Polar will retry is the system working. The usual cause of one is
    this product's own Clerk webhook not having landed yet, which is a race
    measured in seconds, and alarming on it would make every signup-then-buy
    inside one second a red report. So a deferred row inside the grace window
    is `ok` and says so with its count.

    A row nothing will retry is somebody's money with no access, and it never
    clears on its own: nobody holds that address at Clerk, or two accounts do.
    That is `failing` from the first row, with no grace window, because the
    grace window for a person waiting on the owner is the wrong idea.

    And a deferred row still open after the grace window has stopped being a
    race. Those two cases produce the same alarm on purpose: from the buyer's
    side there is no difference between a refusal and a retry that will never
    land, and the evidence below says which one it was.
    """
    now = now or datetime.now(timezone.utc)
    read = {"read_via": source}
    if facts is None or isinstance(facts, str):
        # `unknown` either way, because an unread till is not a clear one. What
        # changes with a reason is whether the report ends at "could not look".
        # It answered exactly that for the nine days since it shipped while one
        # hand-run migration was all it ever needed, which is the gap the
        # version 6 receipt and `why_unreadable` exist to close.
        why = unreadable_reason(facts)
        if why is None:
            return Surface("payments", UNKNOWN,
                           "payment_exceptions could not be read, so whether a "
                           "verified payment reached an account is unknown here",
                           read)
        return Surface("payments", UNKNOWN,
                       f"payment_exceptions could not be read ({why}), so "
                       f"whether a verified payment reached an account is "
                       f"unknown here: {UNREADABLE_HANDS[why]}",
                       {"unreadable": why, **read})

    open_rows = int(facts.get("unresolved") or 0)
    stuck = int(facts.get("needs_a_hand") or 0)
    oldest = facts.get("oldest")
    age = _age_days(oldest, now)
    evidence = {"unresolved": open_rows, "needs_a_hand": stuck,
                "codes": _name_codes(facts.get("codes")) or "none",
                "oldest_unresolved_at": str(oldest) if oldest else None,
                "newest_unresolved_at": (str(facts.get("newest"))
                                         if facts.get("newest") else None),
                "defer_grace_hours": PAYMENT_DEFER_GRACE_HOURS, **read}

    if open_rows == 0:
        return Surface("payments", OK,
                       "every verified payment reached an account", evidence)

    named = _name_codes(facts.get("codes"))
    aged = f", oldest {age:.1f} days" if age is not None else ""

    if stuck:
        return Surface("payments", FAILING,
                       f"{stuck} verified payment(s) cannot reach an account "
                       f"and will not retry ({named}{aged}); "
                       f"{open_rows} open in total", evidence)

    if age is not None and age * 24 > PAYMENT_DEFER_GRACE_HOURS:
        return Surface("payments", FAILING,
                       f"{open_rows} payment(s) have been waiting on a retry "
                       f"for {age:.1f} days, past the "
                       f"{PAYMENT_DEFER_GRACE_HOURS}-hour window a retry "
                       f"lands in ({named})", evidence)

    return Surface("payments", OK,
                   f"{open_rows} payment(s) deferred and inside the "
                   f"{PAYMENT_DEFER_GRACE_HOURS}-hour retry window "
                   f"({named}){aged}", evidence)


def check_payments(conn) -> Surface:
    return judge_payments(payment_facts(conn))


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


def receipt_facts(payload: dict) -> tuple[dict | None, dict, dict | str, dict | None]:
    """The receipt's JSON, in the same four shapes the database reader returns.

    This is the whole of the translation. The judgement is `judge_press`,
    `judge_pipeline`, `judge_deploy` and `judge_payments`, unchanged and shared,
    so a receipt and a connection cannot reach different conclusions about the
    same week.
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
    # The sibling block is absent on versions 1 to 3 and null on a version 4
    # receipt whose site could not read the two tables. Both arrive here as
    # None, which is the shape a direct read of two empty tables hands the
    # judgement, so neither reader can reach a first step the other cannot.
    published = payload.get("siblings")
    siblings = None if not isinstance(published, dict) else {
        stage: (None if not isinstance(published.get(stage), dict) else
                {"newest": _parse_iso(published[stage].get("newest")),
                 "model": published[stage].get("model")})
        for stage, _ in SIBLING_STAGES}
    pipeline_row = {"papers": _parse_iso(pipeline.get("papers_newest")),
                    "claims": _parse_iso(pipeline.get("claims_newest")),
                    "distilled": _parse_iso(pipeline.get("distilled_newest")),
                    "queues": queues if isinstance(queues, dict) else None,
                    "siblings": siblings}

    # Version 6's reasons for the blocks that are null, keyed by block name.
    # Absent on versions 1 to 5 and on any receipt where everything read, and
    # `unreadable_reason` turns anything this reader does not recognise back
    # into None, so an older site and a newer one both land on the sentence
    # that claims nothing.
    unreadable = payload.get("unreadable")
    if not isinstance(unreadable, dict):
        unreadable = {}

    deploy = payload.get("deploy")
    if deploy is None:
        # The route sends null when it could not run that query at all, and an
        # empty list when the table is really empty. Collapsing the two would
        # make a missing table look like three jobs that never reported, which
        # is the drift alarm firing on a schema step.
        why = unreadable_reason(unreadable.get("deploy"))
        deploy_rows: dict | str = ("deploy_runtime could not be read by the site "
                                   "either, so the receipt carries no deploy rows")
        if why is not None:
            deploy_rows += f" ({why}): {UNREADABLE_HANDS[why]}"
    else:
        deploy_rows = {row["app"]: {"runtime_sha": row.get("runtime_sha"),
                                    "recorded_at": _parse_iso(row.get("recorded_at")),
                                    "first_seen_at": _parse_iso(row.get("first_seen_at")),
                                    "notified_at": _parse_iso(row.get("notified_at"))}
                       for row in deploy if isinstance(row, dict) and row.get("app")}

    # The till. Absent on versions 1 to 4 and null on a version 5 receipt whose
    # site could not read the table, and both arrive here as None, which is the
    # shape `payment_facts` returns for an unreadable table. So the two readers
    # hand the judgement the same thing and neither can call the till clear on
    # evidence the other would call unknown.
    published = payload.get("payments")
    # A version 6 receipt says why, and the reason is what gives the verdict a
    # next step instead of a shrug. On an older receipt there is no reason to
    # carry and None is the same unknown it has always been.
    payments: dict | str | None = unreadable_reason(unreadable.get("payments"))
    if isinstance(published, dict):
        codes = published.get("codes")
        payments = {
            "unresolved": published.get("unresolved"),
            "needs_a_hand": published.get("needs_a_hand"),
            "oldest": _parse_iso(published.get("oldest_unresolved_at")),
            "newest": _parse_iso(published.get("newest_unresolved_at")),
            "codes": [row for row in codes if isinstance(row, dict)]
                     if isinstance(codes, list) else [],
        }

    return press_row, pipeline_row, deploy_rows, payments


# ------------------------------------------------------------------ driver

def database_surfaces(today: date | None = None, repo_root: Path | None = None,
                      notify: bool = True, compute: str | None = None) -> list[Surface]:
    """`press`, `pipeline`, `payments` and `deploy`, by the best reader available.

    Two readers, in order. A direct connection when this environment holds
    `DATABASE_URL`, which is the Modal jobs and the owner's laptop. Otherwise
    the receipt the site publishes, which needs no credential and is what every
    agent seat actually has. Both are judged by the same three functions.

    When neither answers, all four surfaces are `unknown` and the message names
    both paths, because the whole reason guardrail 4 went unenforced for four
    days is that nobody could see which reader was missing what.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    direct_why = "no DATABASE_URL in this environment"
    if url:
        surfaces, direct_why = _from_database(url, today, repo_root, notify, compute)
        if surfaces is not None:
            return surfaces

    payload, receipt_why = read_receipt()
    if payload is not None:
        press, pipeline, deploy, payments = receipt_facts(payload)
        return [judge_press(press, today, RECEIPT_URL),
                judge_pipeline(pipeline, source=RECEIPT_URL, compute=compute),
                judge_payments(payments, source=RECEIPT_URL),
                judge_deploy(deploy, repo_root, source=RECEIPT_URL,
                             compute=compute)]

    why = (f"the artifact guardrail 4 names cannot be read here: {direct_why}, "
           f"and the published receipt did not answer either ({receipt_why})")
    return [Surface("press", UNKNOWN, why, {"expected": week_label(today)}),
            Surface("pipeline", UNKNOWN, why),
            Surface("payments", UNKNOWN, why),
            Surface("deploy", UNKNOWN, why)]


def _from_database(url: str, today: date | None, repo_root: Path | None,
                   notify: bool, compute: str | None = None) -> tuple[list[Surface] | None, str]:
    """The four surfaces over a real connection, or None and why not.

    None rather than four `unknown` surfaces, so the caller can fall through to
    the receipt. A connection that fails is not a healthy press and not a broken
    one, and neither is a missing driver.
    """
    try:
        import psycopg
    except ImportError:
        return None, "psycopg is not installed here (pip install 'psycopg[binary]')"
    try:
        with psycopg.connect(url, connect_timeout=15) as conn:
            return [check_press(conn, today), check_pipeline(conn, compute),
                    check_payments(conn),
                    check_deploy(conn, repo_root, notify=notify,
                                 compute=compute)], ""
    except Exception as exc:
        return None, f"DATABASE_URL is set but the connection failed: {exc}"


# `checkout` sits next to `payments` on purpose. One asks whether a sale can
# happen and the other whether a sale that happened became access, and a reader
# scanning this report for the state of the till should meet both in one glance.
ORDER = ["press", "compute", "pipeline", "payments", "checkout", "deploy",
         "site", "archive", "mcp"]


def run(surfaces: list[str], today: date | None = None,
        repo_root: Path | None = None, notify: bool = True) -> list[Surface]:
    asked = set(surfaces)

    # `archive` compares the press's record against the site's page, so asking
    # for it alone has to fetch both of those and then not report them. The two
    # extra names are added here and dropped at the end, rather than inside the
    # comparison, so that `judge_archive` stays a function of two surfaces and
    # is testable as one.
    needed = asked | ({"press", "site"} if "archive" in asked else set())

    # One probe, three readers. `pipeline` and `deploy` both need the answer as
    # a fact and neither can go and get it, so the platform is checked here
    # even when only one of them was asked for, and the extra surface is
    # dropped by the filter at the end.
    #
    # `deploy` joined this set on 2026-10-24, when that surface started
    # reporting when a stale image next serves a run. It costs the deploy-only
    # callers, of which `tools/drift_watch.py` is one, a single HTTP request,
    # and it buys them not putting a deadline on a card for a cron that is not
    # running.
    compute = None
    outage = None
    if {"compute", "pipeline", "deploy"} & needed:
        compute = check_compute()
        outage = compute.headline if compute.state == FAILING else None

    out: list[Surface] = []
    if compute is not None:
        out.append(compute)
    if {"press", "pipeline", "payments", "deploy"} & needed:
        out += [s for s in database_surfaces(today, repo_root, notify, outage)
                if s.name in needed]
    if "site" in needed:
        out.append(check_site(today))
    if "archive" in asked:
        by_name = {s.name: s for s in out}
        out.append(judge_archive(by_name.get("press"), by_name.get("site")))
    if "checkout" in asked:
        out.append(check_checkout(repo_root))
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
                        help="check one surface; repeatable, default is all nine")
    parser.add_argument("--no-notify", action="store_true",
                        help="find a stale deploy and do not mail the owner about it")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON instead of prose")
    parser.add_argument("--no-fetch", action="store_true",
                        help="do not deepen a shallow checkout to date the "
                             "deploy drift. The deploy row then answers "
                             "unknown from a one-commit clone, which is what "
                             "it did before 2026-10-24")
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD, or an ISO timestamp, to ask what a "
                             "given moment should have seen. A bare date means "
                             "the end of that day; the time matters only on a "
                             "Monday, when the press's own deadline falls "
                             "inside it")
    args = parser.parse_args(argv)
    if args.no_fetch:
        # Set rather than threaded through, because `judge_deploy` is reached
        # from `tools/drift_watch.py` and the PM's standup as well as from
        # here, and one switch every door honours beats three signatures.
        import os

        os.environ[NO_FETCH_ENV] = "1"

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
