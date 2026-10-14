#!/usr/bin/env python3
"""The press went quiet, and something says so the hour it happens.

    python3 tools/press_watch.py                      # check, and post if the issue is late
    python3 tools/press_watch.py --dry-run            # the same check, printing what it would post
    python3 tools/press_watch.py --json               # the verdict as a script reads it
    python3 tools/press_watch.py --today 2026-10-12T11:30:00Z

Sprint 2026-10-12 item 5, and it is the sprint's own process finding rather
than a feature. On Monday 2026-10-12 the press cron started at 09:00 UTC,
recorded its own runtime fingerprint, and wrote no row to `digests`. The gap
sat undetected for eleven hours, until the PM's ceremony opened the delivery
receipt at 20:00 and found 2026-W40 still the newest issue. The reason it sat
is in the schedule rather than in the check: `tools/delivery_health.py` already
answers this question correctly and the only scheduled reader of its press
surface is the daily standup, which on a Monday runs the weekly ceremony
instead. The one day of the week the press can fail is the one day nothing
reads whether it did.

Two days later the same week was still missing. At 15:51 UTC on 2026-10-14 the
receipt said `2026-W41` had ended with no issue written, 29 hours after its
deadline, and the board carried nothing about it.

## What this adds, which is a reader and not a rule

The judgement here is `delivery_health.judge_press`, called and not copied.
That function already knows the press's deadline, which is `PRESS_CRON` plus
`PRESS_GRACE`, and already refuses to call a missing issue a fault before the
window closes. A second copy of that rule could only ever agree with the first
by luck, which is the argument `delivery_health` itself makes about the press's
own week label.

What is new is where the answer goes. `delivery_health` prints and exits, so it
informs whoever ran it, and nothing ran it on a Monday. This posts the finding
to the board, which is the surface `docs/standards/pm.md` §14 makes the state of
the work and the one the owner and every seat already read.

## One card a week, and the board is its own cooldown

An alarm with no cooldown is noise by the second firing, and the deploy alarm
in `delivery_health` keeps its cooldown in a column of the row it alarms about.
There is no such column here, so the card itself is the memory: the title
carries the due week, so a second run on the same week finds its own card and
writes nothing. That is what makes a daily schedule safe, and a daily schedule
is the point, because a Monday run that GitHub skips is then caught on Tuesday
rather than next week.

A week that stays missing gets one nudge a day at most, as a comment, and the
cooldown for that is the timestamp on the newest comment the card already
carries. A missing issue on Thursday is worth saying again. Saying it twelve
times is worth less than saying it once.

## Exit codes, and why a blind run is not a quiet pass

    0   the press is on time, or the week that just ended is not due yet
    1   the window closed with no issue, and the board now carries it
    2   the press surface could not be read at all from here

The third is the one this file is careful about. `INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`
and company standard L-A21 are both the same shape, which is a gate that saw
nothing reading as a quiet pass. A run that cannot reach the receipt posts no
card, because an alarm about the press would be a claim this run cannot
support, and it exits 2 so the job that ran it goes red and says so.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import board  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

#: The title a card carries, with the due week in it. The week is what makes
#: the dedupe work, so it is in the title rather than only in the body: the
#: board's list view is what a seat reads, and a card that does not name its
#: week reads as the same alarm every time.
TITLE = "Press: no issue for {week}"

#: The part of the title that is the same every week, which is what tells a
#: card this command wrote from a card somebody else wrote about the same week.
TITLE_PREFIX = TITLE.split("{")[0]

#: Which seat the card lands on. The press is the engineer seat's surface and
#: sprint 2026-10-12 put the send itself on that seat, so an unassigned card
#: would be a finding with nobody holding it.
SEAT = "engineer"

#: Where the card goes. A guardrail's card in the backlog is a guardrail
#: nobody meets, so it asks for the working column by name. An unresolvable
#: name is not fatal: the card is worth more than its column, so it is created
#: in the board's default column with the failure named in stderr.
COLUMN = "This sprint"

#: One nudge a day on a week that stays missing, counted from the newest
#: comment the card already carries.
NUDGE_AFTER = timedelta(hours=24)

#: How far back `due_deadline` will look for the week a card names. Six weeks
#: of silence is not a schedule problem and no card is the right answer to it.
WEEKS_BACK = 6


def _press():
    """The press module, which owns every date rule this file reads."""
    return dh._press_module()


# ------------------------------------------------------------ the pure core


def due_week(press) -> str | None:
    """The week the card is about, read out of the surface's own evidence.

    Both failing branches of `judge_press` carry `due`, including the empty
    table, so this never has to recompute the deadline it was judged by.
    """
    return (press.evidence or {}).get("due")


def is_late(press) -> bool:
    """Did the grace window close on an issue that was never written.

    This is one line because it is allowed to be. `judge_press` is `failing`
    only when the newest issue is older than the week the press owes by now,
    and `press_due_week` is what decides when "by now" starts, so the window
    is already in the verdict.
    """
    return press.state == dh.FAILING


def card_title(week: str) -> str:
    return TITLE.format(week=week)


def lateness(late_for: timedelta) -> str:
    """How late, in the unit a reader would use out loud.

    The scheduled run fires minutes after the deadline, so hours to one
    decimal reads "0.1 hours ago" on the card that matters most, and a week
    nobody has fixed by Thursday reads "72.0 hours ago" when "3.0 days" is the
    same fact in the unit that lands.
    """
    hours = late_for.total_seconds() / 3600
    if hours < 1:
        return f"{late_for.total_seconds() / 60:.0f} minutes"
    if hours < 48:
        return f"{hours:.1f} hours"
    return f"{hours / 24:.1f} days"


def due_deadline(week: str, now: datetime) -> datetime:
    """When the issue this card is about was due.

    Walked back from the most recent Sunday until the press's own label for
    that week matches, rather than computed from today. The two differ in the
    case this guardrail exists for: between midnight on a Monday and the cron
    at 09:00, the week that owes an issue is the week before the one that has
    just ended, and dating the card from today would print a deadline in the
    future on the one morning a reader is most likely to be looking.
    """
    press = _press()
    sunday = press.last_sunday(now.date())
    for _ in range(WEEKS_BACK):
        if press.week_just_ended(sunday + timedelta(days=1))[0] == week:
            return dh.press_deadline(sunday)
        sunday -= timedelta(days=7)
    # A week this far back is a gap no card can be the right response to, and
    # a wrong date is worse than a vague one, so fall back to the deadline the
    # surface was judged against.
    return dh.press_deadline(press.last_sunday(now.date()))


def card_body(press, now: datetime) -> str:
    """What the card says, written for the person who has to fix it.

    The headline is the surface's own, so the card and the command cannot
    disagree about what is wrong. Everything after it is the part a card can
    carry and a command's exit code cannot: when the deadline was, how late
    this is, and the two things that would close it.
    """
    evidence = press.evidence or {}
    week = due_week(press) or dh.week_label(now.date())
    deadline = due_deadline(week, now)
    late_for = lateness(now - deadline)
    lines = [
        press.headline + ".",
        "",
        f"The issue for {week} was due at {deadline:%Y-%m-%d %H:%M} UTC, which "
        f"is the {dh.PRESS_CRON} cron plus the "
        f"{int(dh.PRESS_GRACE.total_seconds() // 3600)} hour grace window in "
        f"docs/agents/delivery-health.md. That was {late_for} ago.",
        "",
        f"Newest issue on record: {evidence.get('newest_week') or 'none at all'}"
        + (f", written {evidence.get('created_at')} by "
           f"{evidence.get('model')}" if evidence.get("newest_week") else "")
        + ".",
        f"Read from: {evidence.get('read_via')}.",
        "",
        "Two things close this, and both are a hand on a Modal token. Either "
        f"the issue is written late, which is `modal run "
        f"pipeline/weekly.py::resend --week {week}` behind the rehearsal "
        "ladder in docs/agents/press-rehearsal.md, or somebody writes down "
        "why the press correctly held and what the right next trigger is. A "
        "held send is a legitimate answer and a silent one is not.",
        "",
        "Posted by tools/press_watch.py, which is the outside observer "
        "guardrail 4 asks for. It reads the artifact rather than the "
        "scheduler, so it fires whether or not the cron started.",
    ]
    return "\n".join(lines)


def find_card(payload: dict, week: str) -> dict | None:
    """The card this week already has, or None.

    Matched on the week in the title rather than on an id kept somewhere,
    because there is nowhere to keep one: this runs from a fresh checkout with
    no state but the board itself. Every column is searched, including Done, so
    a week somebody has already closed is not alarmed about twice.
    """
    for item in payload.get("items") or []:
        title = item.get("title") or ""
        if title.startswith(TITLE_PREFIX) and week in title:
            return item
    return None


def _comment_time(comment: dict) -> datetime | None:
    for key in ("created_at", "createdAt", "updated_at"):
        when = dh._parse_iso(comment.get(key)) if isinstance(comment, dict) else None
        if when:
            return when
    return None


def needs_nudge(card: dict, now: datetime, after: timedelta = NUDGE_AFTER) -> bool:
    """Has it been long enough since this card last said anything.

    The card's own comments are the cooldown store. A card whose comment shape
    this does not recognise is treated as recently nudged rather than as never
    nudged, because the failure that costs something here is a comment a run,
    and the failure that costs nothing is a day of quiet on a card that is
    already on the board.
    """
    comments = card.get("comments")
    if comments is None:
        # The board read that lists a column does not carry comments at all,
        # so this is the shape an unrecognised card has, not an empty one.
        return False
    if not comments:
        # Nothing has been said since the card was created, so the card's own
        # age is the age of the last thing said about this week.
        created = _comment_time(card)
        return bool(created) and now - created >= after
    times = [t for t in (_comment_time(c) for c in comments) if t]
    return bool(times) and now - max(times) >= after


def nudge_body(press, now: datetime) -> str:
    week = due_week(press) or dh.week_label(now.date())
    late_for = lateness(now - due_deadline(week, now))
    return (f"Still missing {late_for} after the deadline. "
            f"{press.headline}. Read from "
            f"{(press.evidence or {}).get('read_via')}.")


# ------------------------------------------------------------------- the run


def read_press(today=None):
    """The press surface, by whichever reader this environment has."""
    return dh.run(["press"], today=today, notify=False)[0]


def post(press, week: str, now: datetime, dry_run: bool = False,
         company: str | None = None, seat: str = SEAT,
         column: str | None = COLUMN) -> dict:
    """Put the finding on the board, once per week, and nudge once a day.

    Returns what it did, as a dict, so `--json` and the prose render read the
    same answer rather than two.
    """
    title, body = card_title(week), card_body(press, now)
    if dry_run:
        return {"action": "would create", "title": title, "body": body,
                "column": column, "seat": seat}

    company = company or board.company_from_repo(
        os.environ.get("GITHUB_REPOSITORY", "")) or "alexandria"
    payload = board.read_board(company)
    found = find_card(payload, week)
    if found:
        if not needs_nudge(found, now):
            return {"action": "already on the board", "id": found.get("id"),
                    "title": found.get("title")}
        board.api(f"/api/items/{found['id']}/comments", method="POST",
                  payload={"company": company, "seat": seat,
                           "body": nudge_body(press, now)})
        return {"action": "nudged", "id": found.get("id"),
                "title": found.get("title")}

    item = {"company": company, "seat": seat, "title": title,
            "body": body, "horizon": "now"}
    if column:
        try:
            item["column_id"] = board.resolve_column(payload, column)
        except board.BoardError as exc:
            print(f"press_watch: {exc}. Creating the card without a column, "
                  "because the card matters and its column does not.",
                  file=sys.stderr)
    created = board.api("/api/items", method="POST", payload=item)
    return {"action": "created", "id": created.get("id"), "title": title}


def watch(today=None, dry_run: bool = False, company: str | None = None) -> dict:
    press = read_press(today)
    now = dh._instant(today)
    answer = {"checked_at": now.isoformat(), "press": press.as_dict(),
              "late": is_late(press), "due": due_week(press)}
    if press.state == dh.UNKNOWN:
        answer["board"] = {"action": "nothing posted",
                           "why": "the press surface could not be read from "
                                  "here, so an alarm about it would be a "
                                  "claim this run cannot support"}
        answer["exit"] = 2
        return answer
    if not is_late(press):
        answer["board"] = {"action": "nothing to post"}
        answer["exit"] = 0
        return answer
    week = due_week(press) or dh.week_label(now.date())
    try:
        answer["board"] = post(press, week, now, dry_run=dry_run, company=company)
    except board.BoardError as exc:
        # The finding is real whether or not the board took it, and a run that
        # swallowed the exit code here would report a working guardrail on a
        # week nobody was told about.
        answer["board"] = {"action": "not posted", "why": str(exc)}
    answer["exit"] = 1
    return answer


def render(answer: dict) -> str:
    press = answer["press"]
    mark = {dh.OK: "ok     ", dh.FAILING: "FAILING", dh.UNKNOWN: "unknown"}
    action = answer.get("board", {})
    lines = ["The press, two hours after its cron",
             "(sprint 2026-10-12 item 5: a send that goes quiet says so the "
             "hour it happens)",
             "",
             f"  {mark[press['state']]}  press     {press['headline']}",
             f"  board      {action.get('action', '-')}"
             + (f": {action.get('title') or action.get('why') or ''}"
                if action.get("title") or action.get("why") else ""),
             ""]
    lines.append({
        0: "The press is current, or the week that just ended is not due yet.",
        1: "The window closed with no issue. The card above is the whole "
           "point of this command.",
        2: "Nothing was posted and this is not a green report: the press "
           "surface could not be read at all from here.",
    }[answer["exit"]])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--today", default=None,
                        help="YYYY-MM-DD, or an ISO timestamp, to ask what a "
                             "given moment should have seen")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the card instead of posting it, and need "
                             "no board credential")
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
    sys.exit(main())
