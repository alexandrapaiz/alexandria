#!/usr/bin/env python3
"""A shop nobody can buy from says so on the board.

    python3 tools/checkout_watch.py                   # check, and post if no sale can happen
    python3 tools/checkout_watch.py --dry-run         # the same check, printing what it would post
    python3 tools/checkout_watch.py --json            # the verdict as a script reads it

The checkout surface of `tools/delivery_health.py` has been correct since
2026-10-18 and has raised an alarm to nobody since the day it shipped. It
prints and exits, so it informs whoever ran it, and the only scheduled reader
of that report is the daily standup. On the day the surface was written both
paid tiers on the public pricing page rendered the words "Opens shortly" with
no link behind either one, five days past the date this company committed to
being able to take a payment, and nothing inside either repository had said
so. Five days after that, the page still renders no checkout link at all and
the board still carries nothing about it.

The pull request that was meant to close this opened as a six-line stub on
2026-10-18 and never got filled in, which is its own finding and is filed.

## What this adds, which is a reader and not a rule

The judgement here is `delivery_health.check_checkout`, called and not copied.
That function already knows which offers the pricing page advertises, already
reads them out of `site/lib/polar-core.js` rather than keeping a second list,
and already knows the one thing a reader is most likely to get wrong: the
checkout route asks a stranger for an account **before** it looks up the
checkout link, so probing the route alone answers the same way whether an
offer is configured or not. The page is the artifact. This file only decides
where that verdict goes.

Where it goes is the board, which `docs/standards/pm.md` §14 makes the state
of the work and the one surface the owner and every seat already read. The
mechanics of putting it there are `tools/board_alarm.py`, shared with the two
watchers that worked them out first.

## What the card is keyed on, which is the fault and not the day

`tools/press_watch.py` keys on the week, because a missing issue is about a
week. `tools/drift_watch.py` keys on the running image, because a drift is
about an image. A shut till is about neither: it is about which offers a
visitor cannot buy, so that is the key, and the title carries it.

Three things fall out of that and all three are the point. A key that moved
every day would post a card every day. A key that never moved would hide a
second, different fault behind the first card: two tiers opening while the
third stays shut is a different fact from nothing opening at all, and it is
the fact that says the owner is halfway through the job. And the fault
clearing ends the alarm with nothing here having to notice, because the
surface goes green and this posts nothing.

## Exit codes, and why a blind run is not a quiet pass

    0   a sale can happen, and nothing was posted
    1   it cannot, and the board now carries it
    2   the pricing page could not be read at all from here

The third is the one this file is careful about, and the surface underneath it
had it backwards until today. A sandbox with no egress gets silence from the
public site, and silence read as "there is nothing for sale" would post a card
claiming the shop is shut on a morning it was open. `check_checkout` now reads
that silence as `unknown`, the way `check_compute` already did, and a run that
meets it posts no card and exits 2 so the job that ran it goes red and says
why.
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
from tools import board_alarm  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

#: The title a card carries. The fault is in it, because the board's list view
#: is what a seat reads and a card that does not name what is shut reads as
#: the same alarm every time.
TITLE = "Checkout: {key}"

#: The part of the title that is the same for every fault, which is what tells
#: a card this command wrote from a card somebody else wrote about the till.
TITLE_PREFIX = "Checkout: "

#: One nudge a day on a till that stays shut, counted from the newest comment
#: the card already carries.
NUDGE_AFTER = board_alarm.NUDGE_AFTER


# ------------------------------------------------------------ the pure core


def fault(checkout) -> str | None:
    """What this card is about, in the one string that stays stable while it is.

    Read out of the surface's evidence rather than parsed out of its headline.
    The headline is one sentence built for a human; the evidence is the same
    facts with the offer names still attached to them, which is the difference
    between reading a verdict and re-deriving one.

    None for a surface that is not failing, so the caller never has to ask the
    state twice.
    """
    if checkout.state != dh.FAILING:
        return None
    evidence = checkout.evidence or {}
    status = evidence.get("status")
    if status != 200:
        # The page itself is the fault, and the code is the stable part of it.
        # A page that is down is not a shop with nothing for sale, and a card
        # that said it was would send the owner to the wrong repository.
        return f"the pricing page answers HTTP {status}, so no offer is reaching anybody"

    linked = list(evidence.get("linked") or [])
    expected = list(evidence.get("expected") or [])
    if not linked:
        return "no offer on the pricing page can be bought"

    shut = sorted(offer for offer, hop in (evidence.get("followed") or {}).items()
                  if hop.get("hop") is None)
    if shut:
        return f"the link for {_names(shut)} does not open a sale"

    missing = sorted(offer for offer in expected if offer not in linked)
    if missing:
        return f"{_names(missing)} advertised on the pricing page with no link behind it"

    # A surface that is failing for a reason the three branches above do not
    # cover still deserves a card, and a key built from the headline is stable
    # while that headline is. Reaching here means this file is behind
    # `check_checkout`, which is worth knowing and is not worth losing an
    # alarm over.
    return checkout.headline[:120]


def _names(offers: list[str]) -> str:
    """Offer names as a reader would say them out loud."""
    if len(offers) == 1:
        return offers[0]
    return ", ".join(offers[:-1]) + f" and {offers[-1]}"


def card_title(key: str) -> str:
    return TITLE.format(key=key)


def unset_variables(checkout) -> list[str]:
    """The environment variables behind the offers that have no link.

    Named because they are the whole remaining action: the site holds these,
    nothing in this repository can set them, and no code change makes the page
    render a link without them. A card that says the till is shut and does not
    say what opens it is a complaint.

    Only names, never values. A checkout url is a secret this repository never
    sees and has no use for, which is the same line `checkout_offers` draws.
    """
    evidence = checkout.evidence or {}
    linked = set(evidence.get("linked") or [])
    env_of = dict(dh.checkout_offers())
    return [env_of[offer] for offer in (evidence.get("expected") or [])
            if offer not in linked and offer in env_of]


def card_body(checkout, now: datetime) -> str:
    """The card's prose, in the house voice the board enforces on its own side.

    Four thoughts, each its own block, because the board refuses a block over
    420 characters and refuses a body of labelled lines. `board.scannable` is
    the shape half of that and cannot know the other two, so the sentences
    here carry their reasons in words.
    """
    evidence = checkout.evidence or {}
    unset = unset_variables(checkout)
    blocks = [
        f"Nobody can complete a purchase on the public pricing page right "
        f"now, because {_without_variables(checkout.headline)}",

        "I read this from the page a stranger is actually sent to rather "
        "than from the checkout route, because that route asks for an "
        "account before it looks up the link and so answers the same way "
        "whether an offer is configured or not.",
    ]
    if unset:
        blocks.append(
            "This closes when the products exist at the seller and these "
            "values reach the site's environment, because nothing in this "
            "repository can set them and no code change will render a link "
            f"without them: {', '.join(unset)}.")
    else:
        blocks.append(
            "This closes at the seller rather than here, because the links "
            "the page renders are the ones the site's environment already "
            "holds and following them is what failed.")
    blocks.append(
        f"The offers the page advertises are read from the site's own list "
        f"rather than copied here, so a tier the owner stops selling leaves "
        f"this check with it: "
        f"{', '.join(evidence.get('expected') or []) or 'none could be read'}.")
    return board.scannable("\n\n".join(blocks))


def _without_variables(headline: str) -> str:
    """The headline, minus the clause that names the unset variables.

    The surface names them because its reader is a terminal and has nothing
    else. A card has a whole block for the action, so naming them twice in
    four sentences reads as a machine talking rather than as somebody telling
    you the shop is shut.
    """
    cut = headline.find(". Unset in the site's environment:")
    return headline[:cut + 1] if cut != -1 else headline


def nudge_body(checkout, card: dict, now: datetime) -> str:
    """One line a day, which says how long rather than repeating the fault."""
    since = board_alarm.comment_time(card)
    age = _ageing(now - since) if since else "an unknown time"
    return board.scannable(
        f"Still shut {age} after this card was opened, because nothing has "
        f"changed at the seller or in the site's environment: "
        f"{checkout.headline}")


def _ageing(span: timedelta) -> str:
    """How long, in the unit a reader would use out loud."""
    hours = span.total_seconds() / 3600
    if hours < 0:
        return "no time at all"
    if hours < 48:
        return f"{hours:.1f} hours"
    return f"{hours / 24:.1f} days"


# ------------------------------------------------------------------- the run


def read_checkout(repo_root: Path | None = None):
    """The checkout surface, which needs no credential and spends nothing."""
    return dh.check_checkout(repo_root)


def post(checkout, key: str, now: datetime, dry_run: bool = False,
         company: str | None = None, seat: str = board_alarm.SEAT,
         column: str | None = board_alarm.COLUMN,
         payload: dict | None = None) -> dict:
    """Put the finding on the board, once per fault, and nudge once a day."""
    title, body = card_title(key), card_body(checkout, now)
    if dry_run:
        return {"action": "would create", "title": title, "body": body,
                "column": column, "seat": seat}

    company = board_alarm.company_here(company)
    if payload is None:
        payload = board.read_board(company)
    found = board_alarm.find_card(payload, [key], prefix=TITLE_PREFIX)
    return board_alarm.place(
        found, payload=payload, title=title, body=body,
        nudge=nudge_body(checkout, found, now) if found else None,
        now=now, company=company, tool="checkout_watch", seat=seat,
        column=column)


def watch(today=None, dry_run: bool = False, company: str | None = None,
          repo_root: Path | None = None) -> dict:
    checkout = read_checkout(repo_root)
    now = dh._instant(today)
    answer = {"checked_at": now.isoformat(), "checkout": checkout.as_dict(),
              "fault": fault(checkout)}

    if checkout.state == dh.UNKNOWN:
        answer["board"] = {"action": "nothing posted",
                           "why": "the pricing page could not be read from "
                                  "here, so an alarm about the till would be "
                                  "a claim this run cannot support"}
        answer["exit"] = 2
        return answer

    if checkout.state == dh.OK:
        answer["board"] = {"action": "nothing to post"}
        answer["exit"] = 0
        return answer

    try:
        answer["board"] = post(checkout, answer["fault"], now,
                               dry_run=dry_run, company=company)
    except board.BoardError as exc:
        # The finding is real whether or not the board took it, and a run that
        # swallowed the exit code here would report a working guardrail on a
        # morning nobody was told the shop was shut.
        answer["board"] = {"action": "not posted", "why": str(exc)}
    answer["exit"] = 1
    return answer


def render(answer: dict) -> str:
    checkout = answer["checkout"]
    mark = {dh.OK: "ok     ", dh.FAILING: "FAILING", dh.UNKNOWN: "unknown"}
    action = answer.get("board", {})
    said = action.get("title") or action.get("why") or ""
    lines = ["The till, read from the page a stranger is sent to",
             "(docs/agents/delivery-health.md guardrail 4: read the artifact, "
             "not the scheduler)",
             "",
             f"  {mark[checkout['state']]}  checkout  {checkout['headline']}",
             f"  fault      {answer.get('fault') or 'none'}",
             f"  board      {action.get('action', '-')}"
             + (f": {said}" if said else ""),
             ""]
    lines.append({
        0: "A visitor who wants to pay can. Nothing was posted.",
        1: "A visitor who wants to pay cannot. The card above is the whole "
           "point of this command.",
        2: "Nothing was posted and this is not a green report: the pricing "
           "page could not be read at all from here.",
    }[answer["exit"]])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--today", default=None,
                        help="an ISO timestamp, to date the nudge from a "
                             "given moment instead of from now")
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
