#!/usr/bin/env python3
"""The buyer's path: how far anybody gets, and which step loses them.

    python3 tools/buyer_path.py                  # the path, for a human
    python3 tools/buyer_path.py --json           # the same answer, for a script
    python3 tools/buyer_path.py --days 30
    python3 tools/buyer_path.py --surface install

Board card c688ef2e, "Build a way to measure the buyer's path". Its own
sentence is the reason this file exists: "Nothing in the site tracks visits,
installs or payments today, because no analytics of any kind has been wired
in. Without it nobody can tell which skill actually sells."

This is the judgement half. The facts come from `site/app/api/funnel/route.js`,
which publishes counts and no verdicts, exactly as `/api/delivery` does, and
for the same reason: no agent seat holds `DATABASE_URL`, so a measurement only
the owner's laptop can read is a measurement no seat can report. The rule that
split those two files applies here unchanged. A second copy of a verdict can
only ever agree with the first by luck.

## The four states, and why two of them are not failures

Every surface answers `ok`, `failing`, `unknown` or `idle`.

`tools/delivery_health.py` argues the first three at length and the argument is
not repeated here. The fourth is this file's own and it is the one that keeps
the report readable before launch.

**`idle` is a measurement that is working and has nothing to measure.** The
table is readable, the recorder is live, and no human has arrived in the
window. Before launch that is the true state of this product most days, and it
has to be distinguishable from two other things it looks exactly like: a
recorder that is not running, and a site that is down. So `idle` is only ever
reported when the instrument itself was proved to be working, and when it
cannot be proved the answer is `unknown` instead.

Collapsing those two would be the expensive mistake in both directions. A quiet
week reported as a failure teaches the reader to stop reading, which is
incident 24's shape. A broken recorder reported as a quiet week is a month of
zeros nobody questions, which is worse, because the day the owner finally asks
which skill sells the answer is that nothing was ever recorded.

## What this cannot answer, stated before any number

**A conversion rate.** `path_events` holds no identifier, by a decision
db/schema.sql and site/lib/path-core.js both explain: the live privacy page
promises a reader there is no third-party script watching them read, and the
salted hash every cookieless analytics product ships is still a pseudonymous
identifier for one person. So two steps here are two counts of events and not
two counts of the same people, and dividing one by the other would read like a
rate while meaning nothing. The counts are reported. The ratio is refused.

**The install.** `/plugin marketplace add alexandrapaiz/alexandria` is a git
clone from the buyer's terminal straight to GitHub, so it never touches the
site and no instrumentation there can see it. GitHub's own traffic API is the
only observer and no token this org holds can read it:

    gh api repos/alexandrapaiz/alexandria/traffic/clones
      -> 403 Resource not accessible by personal access token

That call is attempted on every run anyway, so the step fills itself in the day
the permission exists and nothing here has to change for it. The permission is
`administration: read` on a fine-grained token, or the `repo` scope on a classic
one, and it is one line in a token's settings rather than a build.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.delivery_health import SITE_URL, fetch  # noqa: E402

FUNNEL_URL = f"{SITE_URL}/api/funnel"

# The one sentence `judge_recorder` treats as `unknown` rather than `failing`.
# A sentinel rather than a substring match, because matching on prose is how a
# later edit to a message silently changes a verdict.
NOT_DEPLOYED = "this deploy does not publish /api/funnel yet"

# The repository the install line names, which is the repository whose clones
# are the install count. Read from the manifest rather than written twice, so
# the two cannot disagree: tools/check_plugin_manifest.py already holds that
# the install line and the manifest agree, and this reads the same file.
MANIFEST = Path(__file__).resolve().parents[1] / ".claude-plugin" / "plugin.json"
FALLBACK_REPO = "alexandrapaiz/alexandria"

OK, FAILING, UNKNOWN, IDLE = "ok", "failing", "unknown", "idle"

# Which reader answered, carried in every surface's evidence for the reason
# delivery_health gives: "the press printed" and "a second-hand record says the
# press printed" are different strengths of evidence.
#
# There is one reader here and delivery_health has two, which is a difference
# worth stating rather than leaving as an asymmetry somebody later calls a bug.
# Its second reader is a direct `DATABASE_URL` connection for the Modal jobs
# and the owner's own machine, and it earns its place because the surfaces it
# answers are about a press that may have failed to print. This one is about a
# page-view count, nothing schedules it inside Modal, and a second reader would
# be a second copy of four queries that no test in this repository can execute.
# So the receipt is the only reader, and a deploy that has not happened yet
# reads `unknown` rather than being worked around.
RECEIPT = "/api/funnel"

DEFAULT_DAYS = 7

# The steps in the order a buyer walks them, which is the order the report
# prints and the order the drop is measured along. The five from
# site/lib/path-core.js, plus the two that are not rows in `path_events`:
# `install`, which nothing here can see, and `payment`, which is a state in
# `users` rather than an event.
ORDER = ["visit", "catalog", "skill", "install", "pricing", "checkout", "payment"]

# What each step means to a reader who has not read the schema. One line each,
# because a report that names `catalog` and explains nothing is a report its
# own author can read.
MEANS = {
    "visit": "arrived anywhere on the site",
    "catalog": "opened the skill catalogue",
    "skill": "opened one skill",
    "install": "cloned the repository, which is what installing the plugin is",
    "pricing": "opened the pricing page",
    "checkout": "started a checkout",
    "payment": "has an account that is paying",
}


class Surface:
    """One named thing, its state, and the facts behind it."""

    def __init__(self, name: str, state: str, detail: str, evidence: dict | None = None):
        self.name = name
        self.state = state
        self.detail = detail
        self.evidence = evidence or {}

    def as_dict(self) -> dict:
        return {
            "surface": self.name,
            "state": self.state,
            "detail": self.detail,
            "evidence": self.evidence,
        }


# ------------------------------------------------------------------ the facts


def repo_slug(manifest: Path | None = None) -> str:
    """The owner/name the install line clones, from the plugin manifest."""
    path = manifest or MANIFEST
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return FALLBACK_REPO
    url = str(data.get("repository") or "")
    # Any of the forms a manifest may carry: an https url, a git url, or the
    # slug on its own. Only the last two segments matter.
    trimmed = url.removesuffix(".git").rstrip("/")
    parts = [p for p in trimmed.split("/") if p and ":" not in p]
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return FALLBACK_REPO


def funnel_facts(url: str = FUNNEL_URL) -> dict | str:
    """The counts the site publishes, or a sentence saying why not."""
    status, body, _ = fetch(url)
    if status == 0:
        return f"{url} never answered: {body}"
    if status == 404:
        # A deploy that predates this endpoint, which is every deploy between
        # the merge that adds it and the build that ships it. Marked so the
        # recorder reads `unknown` rather than `failing` for that window: a
        # red tick on a correct deploy is the kind every other seat then
        # inherits through its own merge check and cannot tell from its own.
        return NOT_DEPLOYED
    if status == 503:
        try:
            reason = json.loads(body).get("reason")
        except ValueError:
            reason = None
        return reason or f"{url} answered 503"
    if status != 200:
        return f"{url} answered {status}"
    try:
        data = json.loads(body)
    except ValueError:
        return f"{url} answered 200 with a body that is not JSON"
    if not isinstance(data, dict) or data.get("receipt") != "alexandria-funnel":
        return f"{url} answered 200 with something that is not the funnel receipt"
    return data


def clone_facts(slug: str, token: str | None = None) -> dict:
    """GitHub's clone traffic for the repository the install line names.

    Returns the count when the token may read it, and the refusal otherwise.
    The refusal is a fact worth carrying: a 403 here is one permission away
    from a number and a 404 is a wrong repository name, and those two need
    different hands.
    """
    token = token if token is not None else (
        os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    )
    if not token:
        return {"clones": None, "reason": "no GH_TOKEN or GITHUB_TOKEN in this environment"}

    url = f"https://api.github.com/repos/{slug}/traffic/clones"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "alexandria-buyer-path",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            return {
                "clones": None,
                "reason": (
                    "GitHub refused the clone traffic with 403: this token lacks "
                    "administration: read, which is the one permission between "
                    "this report and an install count"
                ),
            }
        if exc.code == 404:
            return {"clones": None, "reason": f"GitHub has no repository {slug}"}
        return {"clones": None, "reason": f"GitHub answered {exc.code}"}
    except (urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
        return {"clones": None, "reason": f"GitHub never answered: {exc}"}

    total = data.get("count")
    uniques = data.get("uniques")
    if not isinstance(total, int):
        return {"clones": None, "reason": "GitHub answered without a count"}
    # GitHub's window is fourteen days and is not configurable, so the number
    # is labelled with its own window rather than with the one that was asked
    # for. A count over a different period than the steps around it, reported
    # as though it matched, is the quiet kind of wrong.
    return {"clones": total, "uniques": uniques, "window_days": 14, "reason": None}


# --------------------------------------------------------------- the judgement


def judge_recorder(facts: dict | str) -> Surface:
    """Is the instrument working. Every other surface depends on this answer.

    This is the surface that earns the file. A funnel of zeros is the correct
    output of a working recorder on a quiet day and of a dead one on a busy
    day, and nothing downstream can tell those apart, so the distinction is
    made once, here, and carried.
    """
    if isinstance(facts, str):
        state = UNKNOWN if facts == NOT_DEPLOYED else FAILING
        return Surface("recorder", state, facts, {"read_via": RECEIPT})

    evidence = {
        "read_via": facts.get("read_via", RECEIPT),
        "days": facts.get("days"),
        "counts_read": facts.get("counts_read"),
        "off": facts.get("off"),
    }

    if facts.get("off"):
        # Deliberately off, which is neither a failure nor a quiet week. The
        # switch is `PATH_MEASUREMENT=off` in the site's environment and it is
        # the owner's to hold (site/lib/path.js). Reported as `unknown`
        # because that is what the buyer's path is while it is set, and read
        # before the counts because the counts under it are a frozen number
        # that would otherwise read as live.
        return Surface(
            "recorder",
            UNKNOWN,
            "PATH_MEASUREMENT is off in the site's environment, so nothing is "
            "being recorded and the counts below stopped when it was set",
            evidence,
        )

    if not facts.get("counts_read"):
        return Surface(
            "recorder",
            FAILING,
            facts.get("counts_reason") or "the site could not read path_events",
            evidence,
        )

    # An insert that failed is the one fault a count of zero hides completely,
    # so it is read before the counts are. The site publishes the newest one.
    last_error = facts.get("last_record_error")
    if last_error:
        return Surface(
            "recorder",
            FAILING,
            f"the newest insert failed: {last_error}",
            {**evidence, "last_record_error": last_error},
        )

    rows = (facts.get("funnel") or {}).get("rows") or []
    recorded = sum(r.get("events") or 0 for r in rows if r.get("measured") and r.get("step") in PATH_STEPS)
    evidence["recorded"] = recorded

    if recorded == 0:
        # Readable, writable as far as anything here can tell, and empty. That
        # is `idle` and not `ok`, because `ok` would claim the recorder has
        # been proved to work and an empty table is not that proof.
        return Surface(
            "recorder",
            IDLE,
            "path_events is readable and holds nothing in the window, so this "
            "cannot yet tell a quiet week from a recorder that is not running",
            evidence,
        )

    return Surface(
        "recorder",
        OK,
        f"{recorded} step(s) recorded in the last {facts.get('days')} day(s)",
        evidence,
    )


PATH_STEPS = ("visit", "catalog", "skill", "pricing", "checkout")


def steps_of(facts: dict, install: dict, recorder: Surface) -> list[dict]:
    """The seven steps in a buyer's order, each with its count or its reason."""
    rows = {r.get("step"): r for r in ((facts.get("funnel") or {}).get("rows") or [])}
    out = []
    for step in ORDER:
        row = rows.get(step, {})
        events = row.get("events")
        note = row.get("note")
        if step == "install":
            events = install.get("clones")
            note = install.get("reason")
        measured = events is not None
        # A measured zero is only honest when the recorder was proved to work.
        # When it was not, the zero is withdrawn rather than printed, because a
        # printed zero is a claim nobody made.
        if measured and events == 0 and step in PATH_STEPS and recorder.state not in (OK, IDLE):
            measured, events = False, None
            note = note or recorder.detail
        out.append(
            {
                "step": step,
                "means": MEANS[step],
                "events": events,
                "measured": measured,
                "note": note,
            }
        )
    return out


def biggest_drop(steps: list[dict]) -> dict | None:
    """Where the most people stop, between two steps that were both measured.

    Reported as two counts and never as a percentage, for the reason the
    module docstring gives: these are counts of events and not of people.
    An unmeasured step does not break the chain, it is skipped, because the
    install step is unmeasured today and a reader still wants to know what
    happens between the catalogue and the pricing page.
    """
    known = [s for s in steps if s["measured"]]
    if len(known) < 2:
        return None
    worst = None
    for before, after in zip(known, known[1:]):
        lost = before["events"] - after["events"]
        if lost <= 0:
            continue
        if worst is None or lost > worst["lost"]:
            worst = {"from": before["step"], "to": after["step"], "lost": lost,
                     "from_events": before["events"], "to_events": after["events"]}
    return worst


def judge_install(install: dict) -> Surface:
    if install.get("clones") is None:
        return Surface("install", UNKNOWN, install.get("reason") or "not readable", install)
    return Surface(
        "install",
        OK,
        f"{install['clones']} clone(s) in GitHub's own 14-day window",
        install,
    )


def judge_payment(facts: dict | str) -> Surface:
    if isinstance(facts, str):
        return Surface("payment", UNKNOWN, facts, {})
    rows = {r.get("step"): r for r in ((facts.get("funnel") or {}).get("rows") or [])}
    row = rows.get("payment", {})
    if not row.get("measured"):
        return Surface("payment", UNKNOWN, row.get("note") or "the billing record is not readable", row)
    accounts = row.get("events") or 0
    if accounts == 0:
        # Zero paying accounts is not a failure of this product's machinery. It
        # is the state of a till nobody has walked up to yet, and ADR-30 keeps
        # the door shut until the owner creates the Polar account. Saying
        # `failing` here would put a red tick on a correct deploy every day.
        return Surface("payment", IDLE, "no account is paying yet", row)
    return Surface("payment", OK, f"{accounts} account(s) paying", row)


def judge_skills(facts: dict | str) -> Surface:
    """Which skill sells, which is the question the card was written to answer."""
    if isinstance(facts, str):
        return Surface("skills", UNKNOWN, facts, {})
    skills = facts.get("skills")
    if skills is None:
        return Surface("skills", UNKNOWN, facts.get("skills_reason") or "not readable", {})
    if not skills:
        return Surface("skills", IDLE, "no skill page has been opened in the window", {"skills": []})
    top = ", ".join(f"{s['skill']} ({s['events']})" for s in skills[:3])
    return Surface("skills", OK, f"most opened: {top}", {"skills": skills})


def report(days: int = DEFAULT_DAYS, url: str = FUNNEL_URL,
           slug: str | None = None, token: str | None = None) -> dict:
    facts = funnel_facts(f"{url}?days={days}")
    slug = slug or repo_slug()
    install = clone_facts(slug, token)

    recorder = judge_recorder(facts)
    surfaces = [
        recorder,
        judge_install(install),
        judge_payment(facts),
        judge_skills(facts),
    ]
    steps = steps_of(facts, install, recorder) if isinstance(facts, dict) else []

    states = [s.state for s in surfaces]
    if FAILING in states:
        exit_code = 1
    elif UNKNOWN in states:
        exit_code = 2
    else:
        exit_code = 0

    return {
        "report": "alexandria-buyer-path",
        "days": days,
        "repo": slug,
        "surfaces": [s.as_dict() for s in surfaces],
        "steps": steps,
        "drop": biggest_drop(steps),
        "rate": None,
        "rate_reason": (
            "path_events holds no identifier, so these are counts of events and "
            "not counts of people, and a ratio of two of them is not a rate"
        ),
        "exit": exit_code,
    }


# ------------------------------------------------------------------ the print

MARK = {OK: "ok", FAILING: "FAILING", UNKNOWN: "unknown", IDLE: "idle"}


def render(data: dict) -> str:
    lines = [f"the buyer's path, last {data['days']} day(s)", ""]

    width = max(len(s["step"]) for s in data["steps"]) if data["steps"] else 8
    for step in data["steps"]:
        count = str(step["events"]) if step["measured"] else "unmeasured"
        lines.append(f"  {step['step']:<{width}}  {count:>11}   {step['means']}")
        if not step["measured"] and step["note"]:
            lines.append(f"  {'':<{width}}  {'':>11}   why: {step['note']}")
    if not data["steps"]:
        lines.append("  no steps: the funnel could not be read")

    drop = data.get("drop")
    lines.append("")
    if drop:
        lines.append(
            f"  biggest drop: {drop['lost']} between {drop['from']} "
            f"({drop['from_events']}) and {drop['to']} ({drop['to_events']})"
        )
    else:
        lines.append("  biggest drop: not computable from one measured step")
    lines.append(f"  no rate: {data['rate_reason']}")

    lines.append("")
    for surface in data["surfaces"]:
        lines.append(f"  {surface['surface']:<9} {MARK[surface['state']]:<8} {surface['detail']}")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The buyer's path, measured.")
    parser.add_argument("--json", action="store_true", help="the same answer, for a script")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"the window in days (default {DEFAULT_DAYS})")
    parser.add_argument("--surface", help="one surface only: recorder, install, payment, skills")
    parser.add_argument("--url", default=FUNNEL_URL, help="where the counts are published")
    args = parser.parse_args(argv)

    data = report(days=max(1, min(90, args.days)), url=args.url)

    if args.surface:
        kept = [s for s in data["surfaces"] if s["surface"] == args.surface]
        if not kept:
            names = ", ".join(s["surface"] for s in data["surfaces"])
            print(f"no such surface: {args.surface}. try one of: {names}", file=sys.stderr)
            return 2
        data = {**data, "surfaces": kept}
        states = [s["state"] for s in kept]
        data["exit"] = 1 if FAILING in states else (2 if UNKNOWN in states else 0)

    print(json.dumps(data, indent=2) if args.json else render(data))
    return data["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
