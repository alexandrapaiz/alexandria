#!/usr/bin/env python3
"""A merged change that never reached production says so on the board.

    python3 tools/drift_watch.py                  # check, and post if an app is behind
    python3 tools/drift_watch.py --dry-run        # the same check, printing what it would post
    python3 tools/drift_watch.py --json           # the verdict as a script reads it
    python3 tools/drift_watch.py --today 2026-10-17T14:00:00Z

The deploy surface of `tools/delivery_health.py` has been correct since
2026-10-08 and has raised an alarm to nobody since the day it shipped. Its
alarm is an email, its cooldown is the `notified_at` column on the
`deploy_runtime` row it alarms about, and writing that column needs
`DATABASE_URL`. No agent seat holds `DATABASE_URL`. So every seat that has
ever run the check read the deploy surface through the delivery receipt, and
every one of them got the same sentence back instead of a mail:

    not mailed: these rows came from https://libraryofalexandria.dev/api/delivery,
    which cannot write the once-a-day cooldown, and an alarm with no cooldown
    is one mail every time the standup runs

That reasoning is right and the conclusion it reaches is that the alarm never
fires. `docs/ideas.md` has carried it at status `urgent` since 2026-10-09,
"the deploy alarm trips and mails nobody, so a four-day drift raises to no one
at all", and on the day this file was written the drift it could not raise was
eleven days old on the press.

## The cooldown is the card, which `tools/press_watch.py` already worked out

Two days before this file, the same seat hit the same wall on the press and
answered it in `tools/press_watch.py`, whose docstring names this exact alarm
as the unsolved half:

    An alarm with no cooldown is noise by the second firing, and the deploy
    alarm in `delivery_health` keeps its cooldown in a column of the row it
    alarms about. There is no such column here, so the card itself is the
    memory.

The board is a store every seat can write, because `BOARD_API_URL` and
`BOARD_RUNTIME_TOKEN` are in all twelve seat workflows, and it is also the
surface `docs/standards/pm.md` §14 makes the state of the work. So the alarm
goes where the org already looks, and the card is its own cooldown.

## What the card is keyed on, which is the running image and not the day

The press's card is keyed on the week, because a week is what a missing issue
is about. A drift is about an image. So the key here is the sha the job
reported last time it ran, and a card titled with it is the same alarm until
that sha changes. Three things fall out of that and all three are the point.

A deploy that fixes the drift ends the alarm, because the next run of the job
records the trunk's sha and the surface goes green, and nothing here has to
notice. A deploy that lands a *different* stale image gets a new card, because
it is a new fact about a new image. And a second run on the same day, the same
week, or the same fortnight finds its own card and writes nothing, so a job
that stays behind for eleven days costs the board one card and one nudge a day
rather than eleven cards.

An app that has never recorded a runtime at all has no sha to key on, so it is
keyed on the commit that asked it to start recording, which is the same fact
one step upstream and is just as stable.

## The judgement is called and not copied

`delivery_health.judge_deploy` owns every rule this file reads: which apps
exist, what the trunk's sha for each one is, how long the grace window is, and
which of reported-and-behind, never-recorded-and-behind, and cannot-be-dated
an app is in. This file reads that verdict's own evidence and decides where to
put it. A second implementation of the drift rule could only ever agree with
the first by luck, which is the argument `press_watch` makes about the press's
week label and `delivery_health` makes about its own.

One consequence worth stating, because it changes the numbers on the cards:
the drift hours this prints are whatever `judge_deploy` computes. On a tree
where PR #312's `drift_began` has merged, that is measured from the oldest
undeployed commit and reads eleven days on the press; without it, it is
measured from the newest commit to touch the app's files and reads two. Both
are this file's input rather than its claim, and the card names the deployed
commit and its date either way, so a reader can see the real age even when the
headline under-reports it.

## Exit codes, and why a blind run is not a quiet pass

    0   every app is running the trunk, or is behind and still inside the
        grace window, and every app could be placed against production
    1   at least one app is past the window, and the board now carries it
    2   at least one app could not be placed against production at all, or
        the deploy surface could not be read from here at all

The second half of 2 was added on 2026-10-24 and it is the narrow case the
first half was always meant to cover. `judge_deploy` tests its alarm branch
before its unknown branch, so a surface with one app behind and one app it
could not date reads `failing` rather than `unknown`, and this file used to
exit 1 on it: a run that measured two apps out of three reported the two and
said nothing about the third. Any app in `unknown` now reaches 2, the cards
for the apps that did alarm are posted first so no real drift is lost, and
`render` names the unmeasured apps on every path. L-A21, and the surface's
own `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`.

The third is the one to be careful about, for the reason
`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see` and company
standard L-A21 both record: a gate that saw nothing must not read as a quiet
pass. A run that cannot reach the receipt posts no card, because a claim that
production is stale is a claim this run cannot support, and it exits 2 so the
job that ran it goes red and says so.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import board  # noqa: E402
from tools import delivery_health as dh  # noqa: E402
from tools import board_alarm  # noqa: E402

#: The title a card carries. The app and the running image are both in it,
#: because the board's list view is what a seat reads and a card that names
#: neither reads as the same alarm every time. The key is what makes the
#: dedupe work, so it is in the title rather than only in the body.
TITLE = "Deploy: {app} is not running main, still on {key}"

#: The part of the title that is the same for every app, which is what tells a
#: card this command wrote from a card somebody else wrote about a deploy.
TITLE_PREFIX = "Deploy: "

#: Which seat the card lands on. `pipeline/` is the engineer seat's surface
#: and the deploy command is the one action that closes this, so an unassigned
#: card would be a finding with nobody holding it.
SEAT = "engineer"

#: Where the card goes. A guardrail's card in the backlog is a guardrail
#: nobody meets, so it asks for the working column by name. An unresolvable
#: name is not fatal: the card is worth more than its column, so it is created
#: in the board's default column with the failure named on stderr.
COLUMN = "This sprint"

#: One nudge a day on an app that stays behind, counted from the newest
#: comment the card already carries.
NUDGE_AFTER = timedelta(hours=24)

#: Evidence keys on the deploy surface that are about the read rather than
#: about an app. Everything else in that mapping is an app.
NOT_AN_APP = {"read_via", "ref", "alarm", "shallow_checkout"}


# ------------------------------------------------------------ the pure core


def behind(deploy) -> list[dict]:
    """The apps past the grace window, each as one record this file can post.

    Read out of the surface's evidence rather than parsed out of its headline.
    The headline is one sentence built for a human and it joins the apps with
    semicolons; the evidence is the same facts with the app names still
    attached to them, which is the difference between reading a verdict and
    re-deriving one.

    `judge_deploy` marks an app `failing` in exactly the two cases this file
    alarms on, and `ok` for an app that is behind but still inside the window.
    So the filter is the state, and the grace window never appears here.
    """
    found = []
    for app, here in sorted((deploy.evidence or {}).items()):
        if app in NOT_AN_APP or not isinstance(here, dict):
            continue
        if here.get("state") != dh.FAILING:
            continue
        found.append({"app": app, "key": cooldown_key(here), "evidence": here})
    return found


def undated(deploy) -> list[dict]:
    """The apps this run could not measure at all, each with its reason.

    `behind()` filters the evidence to `failing` and that is right: those are
    the apps worth a card. The gap it leaves is every other state, and one of
    them is not a pass. An app the surface marked `unknown` is an app whose
    production image this run could not place, and reporting nothing about it
    is reporting that there was nothing to report.

    This read was missing until 2026-10-24 and the hole it left was narrow and
    total. `watch()` checked the *surface's* state for `unknown`, which is only
    reached when no app alarms, because `judge_deploy` tests its alarm branch
    first. So a run with one app past the window and one app it could not date
    came back `failing`, posted a card for the first, exited 1, and never
    mentioned the second. Company standard L-A21 is the rule it broke and
    `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see` is the same
    surface's own precedent for breaking it.

    The mixed state is not hypothetical. Two routes reach it with no shallow
    clone at all: an app that has never recorded a runtime and whose code does
    not ask it to is `unknown` while its siblings compare fine, and a clone
    deep enough to date one app's handful of commits and not another's twenty
    dates exactly one of them. Depth is a knob on the host harness, and every
    value of it between one and full produces this.
    """
    found = []
    for app, here in sorted((deploy.evidence or {}).items()):
        if app in NOT_AN_APP or not isinstance(here, dict):
            continue
        if here.get("state") != dh.UNKNOWN:
            continue
        found.append({"app": app, "why": str(here.get("why") or "no reason given")})
    return found


def cooldown_key(here: dict) -> str:
    """What this card is about, in the one string that stays stable while it is.

    The sha the job reported on its last run, for an app that has reported.
    For an app that never has, the commit that asked it to start recording,
    which `judge_deploy` puts in the evidence as `asked_in`. Both change only
    when the fact the card is about changes, which is the whole requirement:
    a key that moved every day would post a card every day, and a key that
    never moved would hide a second, different drift behind the first card.
    """
    recorded = here.get("recorded_sha")
    if recorded:
        return str(recorded)
    asked = here.get("asked_in")
    return f"nothing, asked in {asked}" if asked else "nothing recorded at all"


def card_title(app: str, key: str) -> str:
    return TITLE.format(app=app, key=key)


def ageing(hours: float | None) -> str:
    """How far behind, in the unit a reader would use out loud.

    Hours while the number is still small enough to be about today, days once
    it is not, because "44.6 hours" and "1.9 days" are the same fact and only
    the second one reads as a backlog.
    """
    if hours is None:
        return "an unknown time"
    if hours < 48:
        return f"{hours:.1f} hours"
    return f"{hours / 24:.1f} days"


def deploy_command(app: str) -> str:
    """The one action that closes this card, named rather than described.

    Imported rather than hardcoded, so an app whose entrypoint moves does not
    leave this file printing a path that no longer exists.
    """
    try:
        from pipeline import runtime_sha
        return f"modal deploy {runtime_sha.APPS[app]}"
    except Exception:
        return f"modal deploy the {app} app"


def card_body(record: dict, deploy, now: datetime) -> str:
    """What the card says, written for the person who has to run the deploy.

    Prose and not a field list, because the board enforces that on its own
    side: a body of labelled lines comes back as `400 item refused: the prose
    must carry its reason in words`. Passed through `board.scannable` too,
    because the board refuses a block over 420 characters and one of these
    blocks quotes a commit subject this function does not control.
    """
    app, here = record["app"], record["evidence"]
    undeployed = here.get("undeployed") or {}
    commits = undeployed.get("commits") or []
    deployed = undeployed.get("deployed_commit")
    deployed_at = dh._parse_iso(str(undeployed.get("deployed_at")))
    behind_for = ageing(here.get("drift_hours"))

    if here.get("recorded_sha"):
        what = (f"The {app} job last ran on {here['recorded_sha']} and "
                f"{here.get('ref', 'origin/main')} is at "
                f"{here.get('expected_sha')}, so the code that runs in "
                "production is not the code this repository holds.")
    else:
        what = (f"The {app} job has never recorded a runtime at all, and "
                f"{here.get('asked_in')} asked it to, so its image is at "
                "least as old as that commit and nothing can say how much "
                "older.")

    if commits:
        named = ", ".join(f"{c.get('sha')} {c.get('subject')}" for c in commits[:2])
        more = len(commits) - 2
        history = (f"There are {board.plural(len(commits), 'commit')} waiting, "
                   f"the newest of them {named}"
                   + (f", and {more} more behind those" if more > 0 else "")
                   + (f". The running image was built from {deployed} of "
                      f"{deployed_at:%Y-%m-%d}." if deployed and deployed_at
                      else "."))
    elif (deploy.evidence or {}).get("shallow_checkout"):
        history = ("The commits behind it could not be named from this "
                   f"checkout, because the checkout is a shallow clone, so "
                   f"read the number above as a floor. `{dh.UNSHALLOW}` and "
                   "this command will name them.")
    else:
        history = ("The commits behind it could not be named from this "
                   "checkout, and the checkout is not shallow, so this is an "
                   "image that matches no commit on the trunk rather than a "
                   "gap in the history. Read the number above as a floor.")

    return board.scannable("\n\n".join([
        f"{what} It has been behind for {behind_for}, which is past the "
        f"{dh.DEPLOY_GRACE_HOURS} hour grace window in "
        "docs/agents/delivery-health.md, so this is drift rather than a "
        "deploy in flight.",

        history,

        f"I am reading this from {(deploy.evidence or {}).get('read_via')} "
        "rather than from the database, because no agent seat holds a "
        "database credential. That is also why this is a card and not the "
        "email the check was built to send: the email's once-a-day cooldown "
        "is a column on a row only the database can write, so the alarm has "
        "raised to nobody since it shipped, and the card is the cooldown "
        "instead.",

        f"This closes with one command and it needs a hand on a Modal token, "
        f"so it is not mine: {deploy_command(app)}, behind the rehearsal "
        "ladder in docs/agents/press-rehearsal.md. The next run of the job "
        "records its own sha and this surface goes green on its own.",
    ]))


def find_card(payload: dict, app: str, key: str) -> dict | None:
    """The card this app and image already have, or None.

    Matched on the app and the key in the title rather than on an id kept
    somewhere, because there is nowhere to keep one: this runs from a fresh
    checkout with no state but the board itself. Every column is searched,
    including Done, so a drift somebody has already closed is not alarmed
    about twice.
    """
    return board_alarm.find_card(payload, [app, key], prefix=TITLE_PREFIX)


def needs_nudge(card: dict, now: datetime, after: timedelta = NUDGE_AFTER) -> bool:
    """Has it been long enough since this card last said anything.

    One rule for every watcher, in `tools/board_alarm.py`. This used to call
    `press_watch.needs_nudge` with a docstring arguing that the reasoning is
    about cards and not about the press, which was right and was an import
    between two siblings. The third sibling is what turned that argument into
    a module.
    """
    return board_alarm.needs_nudge(card, now, after)


def nudge_body(record: dict, now: datetime) -> str:
    here = record["evidence"]
    return board.scannable(
        f"Still not deployed {ageing(here.get('drift_hours'))} on, because "
        f"nothing has run {deploy_command(record['app'])} yet. Production is "
        f"on {here.get('recorded_sha') or 'an image it has never recorded'} "
        f"and {here.get('ref', 'origin/main')} is at "
        f"{here.get('expected_sha')}.")


# ------------------------------------------------------------------- the run


def read_deploy(today=None):
    """The deploy surface, by whichever reader this environment has.

    `notify=False` because the email path is the one this file exists to
    replace. A run that held both would mail and card the same drift on the
    one machine that can do both, which is the owner's laptop.
    """
    return dh.run(["deploy"], today=today, notify=False)[0]


def post(record: dict, deploy, now: datetime, dry_run: bool = False,
         company: str | None = None, seat: str = SEAT,
         column: str | None = COLUMN, payload: dict | None = None) -> dict:
    """Put one app's drift on the board, once per image, and nudge once a day.

    Takes the board payload as an argument so that a run alarming about three
    apps reads the board once rather than three times. Returns what it did, as
    a dict, so `--json` and the prose render read the same answer.
    """
    app, key = record["app"], record["key"]
    title, body = card_title(app, key), card_body(record, deploy, now)
    if dry_run:
        return {"app": app, "action": "would create", "title": title,
                "body": body, "column": column, "seat": seat}

    company = board_alarm.company_here(company)
    if payload is None:
        payload = board.read_board(company)
    found = find_card(payload, app, key)
    did = board_alarm.place(
        found, payload=payload, title=title, body=body,
        nudge=nudge_body(record, now), now=now, company=company,
        tool="drift_watch", seat=seat, column=column)
    # The app rides along, because a run alarming about three apps reports
    # three lines and a reader needs to know which app each one is about.
    return {"app": app, **did}


def watch(today=None, dry_run: bool = False, company: str | None = None) -> dict:
    deploy = read_deploy(today)
    now = dh._instant(today)
    late = behind(deploy)
    blind = undated(deploy)
    answer = {"checked_at": now.isoformat(), "deploy": deploy.as_dict(),
              "behind": [r["app"] for r in late],
              "undated": [r["app"] for r in blind],
              "undated_why": {r["app"]: r["why"] for r in blind}}

    if deploy.state == dh.UNKNOWN:
        answer["board"] = [{"action": "nothing posted",
                            "why": "the deploy surface could not be read "
                                   "from here, so an alarm about production "
                                   "would be a claim this run cannot support"}]
        answer["exit"] = 2
        return answer
    if not late:
        # Nothing to post is only a green run when there was also nothing this
        # run could not see. An app in `unknown` with no app alarming reaches
        # the surface-level branch above and exits 2; an app in `unknown`
        # alongside an app that is merely inside the grace window does not,
        # and that is this line.
        answer["board"] = [{"action": "nothing to post"}]
        answer["exit"] = 2 if blind else 0
        return answer

    # One read of the board for the whole run, shared by every card below.
    # A failure to read it is a failure to post all of them, and it is
    # reported per app rather than once, so the JSON shape does not change
    # between the path that worked and the path that did not.
    payload = None
    if not dry_run:
        company = board_alarm.company_here(company)
        try:
            payload = board.read_board(company)
        except board.BoardError as exc:
            answer["board"] = [{"app": r["app"], "action": "not posted",
                                "why": str(exc)} for r in late]
            # Same rule as the success path below, so that "any app this run
            # could not place makes it exit 2" is true of every return in this
            # function rather than of most of them.
            answer["exit"] = 2 if blind else 1
            return answer

    done = []
    for record in late:
        try:
            done.append(post(record, deploy, now, dry_run=dry_run,
                             company=company, payload=payload))
        except board.BoardError as exc:
            # The drift is real whether or not the board took it, and a run
            # that swallowed the exit code here would report a working
            # guardrail on an app nobody was told about.
            done.append({"app": record["app"], "action": "not posted",
                         "why": str(exc)})
    answer["board"] = done
    # 2 beats 1 when both are true, and the cards are posted either way. The
    # exit code is a statement about whether this run's answer can be trusted
    # as a whole, and a run that measured two apps out of three cannot be: a
    # reader who sees 1 is told "production is stale and the board carries
    # it", which is a claim about every app. The drift that was found is not
    # lost by this, because it is on the board before the code returns.
    answer["exit"] = 2 if blind else 1
    return answer


def render(answer: dict) -> str:
    deploy = answer["deploy"]
    mark = {dh.OK: "ok     ", dh.FAILING: "FAILING", dh.UNKNOWN: "unknown"}
    lines = ["The deploy, against the trunk it should be running",
             "(docs/agents/delivery-health.md: read the artifact, not the "
             "scheduler)",
             "",
             f"  {mark[deploy['state']]}  deploy    {deploy['headline']}",
             ""]
    for action in answer.get("board") or []:
        detail = action.get("title") or action.get("why") or ""
        lines.append(f"  board      {action.get('app', '-')}: "
                     f"{action.get('action', '-')}"
                     + (f": {detail}" if detail else ""))
    # Printed whatever the exit code is, because the apps this run could not
    # measure are the scope of every other line above and a reader cannot
    # infer them from a headline about the apps it could.
    for record in answer.get("undated_why", {}).items():
        lines.append(f"  unmeasured {record[0]}: {record[1]}")
    lines.append("")
    blind = answer.get("undated") or []
    if answer["exit"] == 2 and blind:
        lines.append("Not a green report: "
                     + board.plural(len(blind), "app") + " could not be "
                     "placed against production at all ("
                     + ", ".join(blind) + "), so this run cannot say whether "
                     "the rest of the pipeline is deployed.")
    else:
        lines.append({
            0: "Every job is running the trunk, or is behind and still inside "
               "the grace window.",
            1: "A merged change has not reached the jobs that run it. The "
               "card above is the whole point of this command.",
            2: "Nothing was posted and this is not a green report: the deploy "
               "surface could not be read at all from here.",
        }[answer["exit"]])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD, or an ISO timestamp, to ask what a "
                             "given moment should have seen")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the cards instead of posting them, and "
                             "need no board credential")
    parser.add_argument("--company", default=None,
                        help="board company; defaults to this repository's name")
    parser.add_argument("--json", action="store_true",
                        help="print the verdict as JSON instead of prose")
    args = parser.parse_args(argv)

    answer = watch(today=dh.parse_moment(args.today), dry_run=args.dry_run,
                   company=args.company)
    print(json.dumps(answer, indent=2, ensure_ascii=False, default=str)
          if args.json else render(answer))
    return answer["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
