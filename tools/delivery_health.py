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

| Surface  | Evidence                                   | Needs          |
| ---      | ---                                        | ---            |
| press    | newest row in `digests`, against the week  | `DATABASE_URL` |
| pipeline | newest rows in `papers` and `claims`       | `DATABASE_URL` |
| site     | the issues `/library` actually publishes   | nothing        |
| mcp      | an unauthenticated probe of `/mcp`         | nothing        |

Two of the four are public, so this command is useful in a seat's sandbox
today. The other two want one read-only connection string in the environment,
and the only thing standing between guardrail 4 and enforcement is that nobody
has put one there.
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

OK, FAILING, UNKNOWN = "ok", "failing", "unknown"

# The daily crons run between 11:00 and 14:00 UTC, so a corpus table that has
# not moved in two days has missed two of them. One day would fire on any run
# that merely started late.
PIPELINE_STALE_DAYS = 2


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
            "has ended. The site archive is hand-committed: nothing in this "
            "repository publishes a digest, so a written issue reaches the "
            "public only when someone commits it under site/content/issues/.",
            evidence)
    return Surface("site", OK,
                   f"{len(weeks)} issue(s) published, newest {weeks[0]}", evidence)


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


def check_press(conn, today: date | None = None) -> Surface:
    """The newest row in `digests`, against the week that has ended.

    This is guardrail 4's own named evidence and the one query incident 24
    would have been answered by in a second.
    """
    row = conn.execute(
        "select week, created_at, model from digests order by week desc limit 1"
    ).fetchone()
    expected = week_label(today)
    if row is None:
        return Surface("press", FAILING, "the digests table is empty",
                       {"expected": expected})
    week, created_at, model = row
    evidence = {"newest_week": week, "expected": expected,
                "created_at": str(created_at), "model": model}
    if week < expected:
        missing = _weeks_between(week, expected)
        return Surface("press", FAILING,
                       f"the newest issue is {week} and {expected} has ended; "
                       f"{missing} issue(s) missing", evidence)
    return Surface("press", OK, f"{week} is written, by {model}", evidence)


def check_pipeline(conn) -> Surface:
    """The daily crons, read through the rows they leave behind.

    delivery-health.md's own table calls this the next gap and says why it
    matters most: it is the surface that feeds every other one. A press that
    prints on an empty corpus prints an empty issue.
    """
    now = datetime.now(timezone.utc)
    rows = {}
    for label, sql in (
        ("papers", "select max(fetched_at) from papers"),
        ("claims", "select max(created_at) from claims"),
    ):
        value = conn.execute(sql).fetchone()[0]
        rows[label] = value
    stale = []
    evidence = {}
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


def _weeks_between(have: str, want: str) -> int:
    """How many issues are missing between the newest row and the week that ended."""
    def monday(label: str) -> date:
        year, week = label.split("-W")
        return date.fromisocalendar(int(year), int(week), 1)

    return max(0, (monday(want) - monday(have)).days // 7)


# ------------------------------------------------------------------ driver

def database_surfaces(today: date | None = None) -> list[Surface]:
    """`press` and `pipeline`, or one honest `unknown` each if we cannot look.

    The message names the variable, because the whole reason guardrail 4 has
    never been enforced is that nobody could see which credential was missing
    from where.
    """
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        why = ("no DATABASE_URL in this environment, so the artifact guardrail "
               "4 names cannot be read here")
        return [Surface("press", UNKNOWN, why, {"expected": week_label(today)}),
                Surface("pipeline", UNKNOWN, why)]
    try:
        import psycopg
    except ImportError:
        why = "psycopg is not installed here (pip install 'psycopg[binary]')"
        return [Surface("press", UNKNOWN, why), Surface("pipeline", UNKNOWN, why)]
    try:
        with psycopg.connect(url, connect_timeout=15) as conn:
            return [check_press(conn, today), check_pipeline(conn)]
    except Exception as exc:
        # A connection that fails is not a healthy press and not a broken one.
        # It is the check failing, and saying so is the point of this state.
        why = f"DATABASE_URL is set but the connection failed: {exc}"
        return [Surface("press", UNKNOWN, why), Surface("pipeline", UNKNOWN, why)]


def run(surfaces: list[str], today: date | None = None) -> list[Surface]:
    out: list[Surface] = []
    if {"press", "pipeline"} & set(surfaces):
        out += [s for s in database_surfaces(today) if s.name in surfaces]
    if "site" in surfaces:
        out.append(check_site(today))
    if "mcp" in surfaces:
        out.append(check_mcp())
    return sorted(out, key=lambda s: ["press", "pipeline", "site", "mcp"].index(s.name))


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
                        choices=["press", "pipeline", "site", "mcp"],
                        help="check one surface; repeatable, default is all four")
    parser.add_argument("--json", action="store_true",
                        help="print the result as JSON instead of prose")
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD, to ask what a given day should have seen")
    args = parser.parse_args(argv)

    today = date.fromisoformat(args.today) if args.today else None
    results = run(args.surfaces or ["press", "pipeline", "site", "mcp"], today)

    if args.json:
        print(json.dumps({"checked_at": datetime.now(timezone.utc).isoformat(),
                          "surfaces": [s.as_dict() for s in results]},
                         indent=2, ensure_ascii=False))
    else:
        print(render(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
