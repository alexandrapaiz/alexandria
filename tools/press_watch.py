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
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline import llm  # noqa: E402
from tools import board  # noqa: E402
from tools import board_alarm  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

#: The title a card carries, with the due week in it. The week is what makes
#: the dedupe work, so it is in the title rather than only in the body: the
#: board's list view is what a seat reads, and a card that does not name its
#: week reads as the same alarm every time.
TITLE = "Press: no issue for {week}"

#: The other thing worth a card, and the reason this file grew a second one.
#: The owner's priority of 2026-10-16 is a press that runs on its own, and she
#: asked for two things in one sentence: when a provider refuses, fall back to
#: another, and say so on the board. The press has had the first half since
#: ADR-32 and `write_digest` walks four models across two providers. The
#: second half did not exist. A fallback that nobody is told about is a
#: degradation the org discovers next quarter, from a reader, which is how it
#: discovered the last three.
FALLBACK_TITLE = "Press: {week} was written on a fallback, not {primary}"

#: The part of each title that is the same every week, which is what tells a
#: card this command wrote from a card somebody else wrote about the same week.
#: Two titles now, so the mark is a phrase rather than a leading slice: both
#: begin "Press: " and a dedupe on that alone would let a week's fallback card
#: suppress its own missing-issue card, which are opposite findings.
TITLE_PREFIX = TITLE.split("{")[0]
FALLBACK_MARK = "was written on a fallback"

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

    Prose and not a field list, because the board enforces that on its own
    side: a body of labelled lines comes back as `400 item refused: the prose
    must carry its reason in words (so that, because, otherwise): what you are
    doing and why, as a conversation, not a list of labels`. The first draft
    of this function was refused for exactly that, which is the right outcome
    and is recorded in `tools/board.py`.

    It is also passed through `board.scannable`, because the board refuses a
    block over 420 characters and one of these blocks quotes a headline this
    function does not control. The pipeline surface's headline is already over
    500 characters on a bad day, so the arithmetic that holds today is not a
    property worth relying on at the moment the alarm matters.

    The headline is the surface's own, so the card and the command cannot
    disagree about what is wrong. The rest is what a card can carry and an
    exit code cannot: when the deadline was, how late this is, which reader
    answered, and the two things that would close it.
    """
    evidence = press.evidence or {}
    week = due_week(press) or dh.week_label(now.date())
    deadline = due_deadline(week, now)
    late_for = lateness(now - deadline)
    newest = evidence.get("newest_week")
    # The receipt's timestamp arrives with microseconds on it, which is six
    # digits of precision nobody reading a card about a missing week needs.
    written = dh._parse_iso(str(evidence.get("created_at")))
    written = f"{written:%Y-%m-%d %H:%M} UTC" if written else evidence.get("created_at")
    had = (f"The newest issue on record is {newest}, written "
           f"{written} by {evidence.get('model')}, so "
           f"anyone opening /library today reads {newest} as the latest thing "
           "this product has published."
           if newest else
           "There is no issue on record at all, because the digests table is "
           "empty, so a reader opening /library finds nothing to read.")
    return board.scannable("\n\n".join([
        f"The press owes an issue for {week} and no row exists for it, so "
        f"{press.headline}. The deadline was {deadline:%Y-%m-%d %H:%M} UTC, "
        f"which is the {dh.PRESS_CRON} cron plus the "
        f"{int(dh.PRESS_GRACE.total_seconds() // 3600)} hour grace window in "
        f"docs/agents/delivery-health.md, so this is {late_for} late.",

        had + f" I am reading that from {evidence.get('read_via')} rather "
        "than from the database, because no agent seat holds a database "
        "credential and the site publishes the same rows without one.",

        "I am posting this because nothing read the press on the hour it "
        "went quiet. The check that answers this question has been correct "
        "since 2026-10-08, and its only scheduled reader is the daily "
        "standup, which on a Monday runs the weekly ceremony instead, so the "
        "one day the press can fail is the one day nobody was asking.",

        "This closes one of two ways, and both of them need a hand on a "
        f"Modal token, so neither is mine. Either the issue is written late, "
        f"which is `modal run pipeline/weekly.py::resend --week {week}` "
        "behind the rehearsal ladder in docs/agents/press-rehearsal.md, or "
        "somebody writes down why the press correctly held and what the "
        "right next trigger is, because a held send is a legitimate answer "
        "and a silent one is not.",
    ]))


def wrote_on_fallback(press) -> bool:
    """Did a provider other than the primary write the issue on record.

    `llm.on_fallback` is the rule, called and not copied, which is the same
    argument this file already makes about `judge_press`. It compares the
    model's provider against `budget.PRIMARY_MODEL`'s, so the day the primary
    moves this answer moves with it and no second table has to be remembered.

    False for a week with no issue at all, because "nobody wrote it" is the
    other card and saying both about one week would be two alarms for one
    fact.
    """
    model = (press.evidence or {}).get("model")
    return bool(model) and not is_late(press) and llm.on_fallback(model)


def fallback_title(press) -> str:
    return FALLBACK_TITLE.format(week=(press.evidence or {}).get("newest_week"),
                                 primary=llm.budget().PRIMARY_MODEL)


def fallback_body(press, now: datetime) -> str:
    """What the card says when the press survived on its second choice.

    Written as news rather than as an alarm, because it is news: the issue
    went out. What the reader has to decide is whether the primary is coming
    back on its own, and the two facts that decide it are which provider
    answered and what the issue cost in quality for having asked it.

    The quality sentence is arithmetic rather than a guess.
    `pipeline/budget.py` prints it on every run: the full generator prompt is
    110,404 tokens against the 6,800 a Groq free-tier request may hold, so no
    Groq model in `FALLBACK_MODELS` can print anything but the short edition.
    An issue written off Moonshot is therefore a 400-word issue carrying a
    handful of the ban list rather than the whole of it.
    """
    evidence = press.evidence or {}
    model = evidence.get("model")
    week = evidence.get("newest_week")
    primary = llm.budget().PRIMARY_MODEL
    provider = llm.budget().provider_of(model) or "an unknown provider"
    written = dh._parse_iso(str(evidence.get("created_at")))
    written = f"{written:%Y-%m-%d %H:%M} UTC" if written else evidence.get("created_at")
    short = ("Everything behind the primary is on a free tier whose request "
             "ceiling is 6,800 tokens against the full issue's 110,404, so "
             "what went out is the short edition: 400 words, and a handful of "
             "the ban list rather than all of it.")
    return board.scannable("\n\n".join([
        f"{week} went out on {model} at {written}, which is {provider} and "
        f"not {primary}, so the press printed but it printed on its second "
        "choice. I am saying so here because a fallback nobody is told about "
        "is a degradation this org finds out about from a reader.",

        short if llm.budget().provider_of(model) != "moonshot" else
        ("The model is off the primary's provider, so the issue is the "
         "degraded edition rather than the full one."),

        "What this asks of a reader is one decision rather than a fix, "
        "because the issue is already in the archive. Either the primary is "
        "down for a reason that passes on its own, which a balance is, or it "
        "is down for a reason that does not, and the difference decides "
        f"whether next Monday prints in full. `modal app logs "
        f"alexandria-weekly` carries the refusal {primary} gave.",

        f"I am reading this from {evidence.get('read_via')} rather than from "
        "the database, because no agent seat holds a database credential and "
        "the site publishes the same rows without one.",
    ]))


def find_card(payload: dict, week: str, mark: str = TITLE_PREFIX) -> dict | None:
    """The card this week already has for `mark`, or None.

    Matched on the week in the title rather than on an id kept somewhere,
    because there is nowhere to keep one: this runs from a fresh checkout with
    no state but the board itself. Every column is searched, including Done, so
    a week somebody has already closed is not alarmed about twice.

    `mark` is what makes one week able to hold two different findings. A week
    can be late and then be written on a fallback, and those are not the same
    card: closing the first does not answer the second.

    The matching itself moved to `tools/board_alarm.py` on 2026-10-23, when a
    third watcher needed it. What stays here is the pair of marks, which is
    the only part of this that is about the press.
    """
    return board_alarm.find_card(payload, [mark, week])


def _comment_time(comment: dict) -> datetime | None:
    return board_alarm.comment_time(comment)


def needs_nudge(card: dict, now: datetime, after: timedelta = NUDGE_AFTER) -> bool:
    """Has it been long enough since this card last said anything.

    The card's own comments are the cooldown store. A card whose comment shape
    this does not recognise is treated as recently nudged rather than as never
    nudged, because the failure that costs something here is a comment a run,
    and the failure that costs nothing is a day of quiet on a card that is
    already on the board.

    That reasoning is about cards and not about the press, which is why
    `drift_watch` called this rather than copying it and why it now lives in
    `tools/board_alarm.py` where all three watchers reach the same copy.
    """
    return board_alarm.needs_nudge(card, now, after)


def nudge_body(press, now: datetime) -> str:
    week = due_week(press) or dh.week_label(now.date())
    late_for = lateness(now - due_deadline(week, now))
    return board.scannable(
        f"Still missing {late_for} after the deadline, because nothing "
        f"has sent it yet: {press.headline}, read again just now from "
        f"{(press.evidence or {}).get('read_via')}.")


# ------------------------------------------------------------------- the run


def read_press(today=None):
    """The press surface, by whichever reader this environment has."""
    return dh.run(["press"], today=today, notify=False)[0]


def post(press, week: str, now: datetime, dry_run: bool = False,
         company: str | None = None, seat: str = SEAT,
         column: str | None = COLUMN, kind: str = "late") -> dict:
    """Put the finding on the board, once per week, and nudge once a day.

    Returns what it did, as a dict, so `--json` and the prose render read the
    same answer rather than two.

    `kind` picks which of the two findings this is. One function rather than
    two, because everything below the title and the body is the same problem
    solved the same way: dedupe on the week, resolve the column by name,
    survive a board that will not take it. Two copies of that would disagree
    the first time one of them was edited.
    """
    if kind == "fallback":
        title, body, mark = (fallback_title(press),
                             fallback_body(press, now), FALLBACK_MARK)
    else:
        title, body, mark = card_title(week), card_body(press, now), TITLE_PREFIX
    if dry_run:
        return {"action": "would create", "title": title, "body": body,
                "column": column, "seat": seat}

    company = board_alarm.company_here(company)
    payload = board.read_board(company)
    found = find_card(payload, week, mark)
    # A fallback card is a statement and not an open problem, so it is said
    # once and never nudged, which is what a nudge of None means. The late
    # card is the opposite: a week that is still missing on Thursday is worth
    # saying again.
    return board_alarm.place(
        found, payload=payload, title=title, body=body,
        nudge=None if kind == "fallback" else nudge_body(press, now),
        now=now, company=company, tool="press_watch", seat=seat, column=column)


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
    answer["on_fallback"] = wrote_on_fallback(press)
    if not is_late(press):
        if not answer["on_fallback"]:
            answer["board"] = {"action": "nothing to post"}
            answer["exit"] = 0
            return answer
        # The press delivered, so this exits 0 and the scheduled job stays
        # green. That is deliberate and it is the whole design of a fallback:
        # a degraded path that works is a success, and a red tick on a week
        # the reader got an issue teaches everybody to stop reading the ticks.
        # The card is the channel, because the card is read by a person who
        # can decide about the provider, and a red run is read by nobody with
        # that decision in front of them.
        week = (press.evidence or {}).get("newest_week") or dh.week_label(now.date())
        try:
            answer["board"] = post(press, week, now, dry_run=dry_run,
                                   company=company, kind="fallback")
        except board.BoardError as exc:
            answer["board"] = {"action": "not posted", "why": str(exc)}
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
             f"  provider   {(press.get('evidence') or {}).get('model') or 'none on record'}"
             + ("  (a fallback, not the primary)" if answer.get("on_fallback")
                else ""),
             f"  board      {action.get('action', '-')}"
             + (f": {action.get('title') or action.get('why') or ''}"
                if action.get("title") or action.get("why") else ""),
             ""]
    lines.append({
        0: ("The press is current, or the week that just ended is not due "
            "yet." + (" It printed on a fallback provider, which is a "
                      "success and a card rather than a failure."
                      if answer.get("on_fallback") else "")),
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
