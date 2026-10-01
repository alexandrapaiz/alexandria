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
| press    | newest row in `digests`, against the week   | nothing  |
| pipeline | newest rows in `papers` and `claims`        | nothing  |
| site     | the issues `/library` actually publishes    | nothing  |
| mcp      | an unauthenticated probe of `/mcp`          | nothing  |
| deploy   | `deploy_runtime` against this checkout      | git      |

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

Three ways this surface refuses to guess, all of them `unknown` rather than a
verdict. A checkout with uncommitted changes under a job's file list is
comparing the deploy against something nobody merged, which is the normal state
of a seat's own sandbox. A checkout too shallow to date the last commit that
touched those files cannot tell a drift of an hour from a drift of a month.
And no `DATABASE_URL` means the recorded side cannot be read at all.
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
RECEIPT_VERSION = 1  # must match site/lib/delivery-core.js RECEIPT_VERSION

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


class Surface:
    """One delivery surface's answer: a state, a headline, and its evidence."""

    def __init__(self, name: str, state: str, headline: str,
                 evidence: dict | None = None):
        self.name, self.state, self.headline = name, state, headline
        self.evidence = evidence or {}

    def as_dict(self) -> dict:
        return {"surface": self.name, "state": self.state,
                "headline": self.headline, "evidence": self.evidence}


def week_label(today: date | None = None) -> str:
    """The week the press should most recently have printed.

    Imported from the press itself rather than recomputed here. A health check
    that carries its own copy of the rule can only ever agree with the press by
    luck, and disagreeing silently is worse than not checking. That matters
    more than usual for this particular rule, which was wrong until today: a
    second copy written this morning would have been a second copy of the bug.

    `pipeline/weekly.py` imports `modal` at module scope, for decorators, and a
    seat's sandbox has no reason to have the Modal SDK installed. So when it is
    absent this stands a namespace in for it long enough to read one pure date
    function out of the module. `tests/conftest.py` does the same thing for the
    same reason, and the alternative is the duplicated rule.
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

    from pipeline.weekly import week_just_ended

    return week_just_ended(today)[0]


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

def check_site(today: date | None = None) -> Surface:
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
    expected = week_label(today)
    evidence = {"url": f"{SITE_URL}/library", "published": weeks, "expected": expected}
    if not weeks:
        return Surface("site", FAILING, "/library renders but publishes no issue at all",
                       evidence)
    if weeks[0] < expected:
        return Surface(
            "site", FAILING,
            f"the newest issue a reader can read is {weeks[0]}, and {expected} "
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


def judge_press(facts: dict | None, today: date | None = None,
                source: str = DIRECT) -> Surface:
    """The newest issue, against the week that has ended.

    Takes rows rather than a connection, so the credential-free reader and the
    credentialled one are judged by this function and not by two copies of it.
    The file already makes this argument about `week_just_ended`: a second copy
    of a rule can only ever agree with the first by luck.
    """
    expected = week_label(today)
    if facts is None:
        return Surface("press", FAILING, "the digests table is empty",
                       {"expected": expected, "read_via": source})
    week, created_at, model = facts["week"], facts["created_at"], facts["model"]
    evidence = {"newest_week": week, "expected": expected,
                "created_at": str(created_at), "model": model,
                "read_via": source}
    if week < expected:
        missing = _weeks_between(week, expected)
        return Surface("press", FAILING,
                       f"the newest issue is {week} and {expected} has ended; "
                       f"{missing} issue(s) missing", evidence)
    return Surface("press", OK, f"{week} is written, by {model}", evidence)


def check_press(conn, today: date | None = None) -> Surface:
    return judge_press(press_facts(conn), today)


def pipeline_facts(conn) -> dict:
    """When the corpus last moved: the newest row in `papers` and in `claims`."""
    return {
        "papers": conn.execute("select max(fetched_at) from papers").fetchone()[0],
        "claims": conn.execute("select max(created_at) from claims").fetchone()[0],
    }


def judge_pipeline(facts: dict, now: datetime | None = None,
                   source: str = DIRECT) -> Surface:
    """The daily crons, read through the rows they leave behind.

    delivery-health.md's own table calls this the next gap and says why it
    matters most: it is the surface that feeds every other one. A press that
    prints on an empty corpus prints an empty issue.
    """
    now = now or datetime.now(timezone.utc)
    rows = dict(facts)
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
            stale.append(f"{label} has not moved in {age.days} days")
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
    """Which of these files the working tree has changed and not committed."""
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


def _last_commit_at(repo_root: Path, paths: list[str]) -> datetime | None:
    """When the newest commit touching any of these files landed.

    None when the answer cannot be trusted, which is a shallow clone that
    predates the change, git not being present, or a path set nothing in the
    available history ever touched. The seat workflows check out with
    `fetch-depth: 0`, so in the place this actually runs daily the answer is
    real; anywhere else it degrades to `unknown` instead of to a guess.
    """
    status, out = _git(repo_root, "log", "-1", "--format=%cI", "--", *paths)
    if status != 0 or not out:
        return None
    try:
        return datetime.fromisoformat(out).astimezone(timezone.utc)
    except ValueError:
        return None


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
    """Is the code on this checkout the code the crons are running.

    One surface for all three jobs rather than three, because the question the
    reader has is "is anything stale" and the headline can name which. The
    evidence block carries each app separately for whoever wants the detail.

    `notify_conn` is a connection or None. None means do not mail, and the two
    reasons for that are a caller passing `notify=False` and the facts having
    come from the public receipt, which cannot write the alarm's cooldown.
    """
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]
    now = now or datetime.now(timezone.utc)

    try:
        from pipeline import runtime_sha
    except Exception as exc:
        return Surface("deploy", UNKNOWN,
                       f"pipeline/runtime_sha.py could not be read here: {exc}",
                       {"read_via": source})

    if isinstance(facts, str):
        return Surface("deploy", UNKNOWN, facts, {"read_via": source})
    rows = facts

    evidence, drifted, unknowns, alarms = {"read_via": source}, [], [], []
    for app in sorted(runtime_sha.APPS):
        try:
            entries = runtime_sha.local_entries(app, root)
        except OSError as exc:
            unknowns.append(f"{app} ({exc})")
            evidence[app] = {"state": UNKNOWN, "why": str(exc)}
            continue
        keys = [key for key, _ in entries]
        local = runtime_sha.digest(entries)
        row = rows.get(app)
        here = {"expected_sha": local, "files": len(entries),
                "recorded_sha": row["runtime_sha"] if row else None,
                "last_run": str(row["recorded_at"]) if row else None}

        if row and row["runtime_sha"] == local:
            here["state"] = OK
            here["live_since"] = str(row["first_seen_at"])
            evidence[app] = here
            continue

        dirty = _dirty(root, keys)
        if dirty:
            here.update(state=UNKNOWN, uncommitted=dirty)
            unknowns.append(f"{app} (uncommitted: {', '.join(dirty)})")
            evidence[app] = here
            continue

        changed_at = _last_commit_at(root, keys)
        if changed_at is None:
            here.update(state=UNKNOWN, why="this checkout cannot date the change")
            unknowns.append(f"{app} (no datable history for its files here)")
            evidence[app] = here
            continue

        age_hours = (now - changed_at).total_seconds() / 3600
        here.update(state=FAILING if age_hours > DEPLOY_GRACE_HOURS else OK,
                    merged_at=str(changed_at), drift_hours=round(age_hours, 1))
        evidence[app] = here
        if age_hours > DEPLOY_GRACE_HOURS:
            alarms.append((app, round(age_hours / 24, 1), row, local))
        else:
            drifted.append(f"{app} ({round(age_hours, 1)}h)")

    if alarms:
        names = ", ".join(f"{app} is {days} days behind" for app, days, _, _ in alarms)
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
                       f"the deployed code is not this code: {names}. "
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
                   f"all {len(runtime_sha.APPS)} jobs are running this checkout",
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
    for app, days, row, local in alarms:
        last = row["notified_at"] if row else None
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            if (now - last) < timedelta(hours=DEPLOY_NOTIFY_COOLDOWN_HOURS):
                continue
        due.append((app, days, row, local))
    if not due:
        return "the owner was mailed about this within the last day already"

    try:
        from pipeline.notify import notify_owner
    except Exception as exc:
        return f"NOT NOTIFIED: the alarm channel could not be loaded ({exc})"

    from pipeline import runtime_sha

    lines = []
    for app, days, row, local in due:
        running = row["runtime_sha"] if row else "nothing recorded at all"
        lines.append(f"{app}: this repository is at {local}, the last run "
                     f"reported {running}, and the change merged {days} days ago.")
    detail = "\n\n".join(
        ["A merged change has not reached the jobs that run it.", "\n".join(lines)])
    steps = [f"modal deploy {runtime_sha.APPS[app]}" for app, _, _, _ in due]
    steps.append("then run tools/delivery_health.py --surface deploy again; "
                 "the next run of each job clears its own row")
    sent = notify_owner("alexandria: a merged change is not deployed",
                        detail, steps, sender="alexandria drift guard")

    if sent.startswith("owner notified"):
        try:
            with conn.transaction():
                conn.execute(
                    "update deploy_runtime set notified_at = now() where app = any(%s)",
                    ([app for app, _, _, _ in due],))
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
    if payload.get("version") != RECEIPT_VERSION:
        # A version this reader does not know is not a licence to read the
        # fields it recognises. The missing field would read as a null and a
        # null here is a surface answering FAILING.
        return None, (f"{url} published receipt version {payload.get('version')} "
                      f"and this reader speaks version {RECEIPT_VERSION}")
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
    pipeline_row = {"papers": _parse_iso(pipeline.get("papers_newest")),
                    "claims": _parse_iso(pipeline.get("claims_newest"))}

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
                        help="YYYY-MM-DD, to ask what a given day should have seen")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else None
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
