#!/usr/bin/env python3
"""One card for a finding, and one nudge a day while it stays true.

Not a command. This is the part `tools/press_watch.py` and
`tools/drift_watch.py` had each written for themselves, lifted out on the day
a third watcher needed it, because three copies of a rule is no longer two
tools that happen to agree.

## What the duplication actually was

Both watchers answer a different question (did the press print, is production
running main) and both put the answer in the same place the same way. Strip
the question out and what is left is one mechanic in three steps. Find the
card this finding already has, by reading the board rather than by keeping an
id anywhere, because a watcher runs from a fresh checkout with no state but
the board. If there is no card, create one in a named column. If there is,
say nothing, unless the last thing said about it is old enough that saying it
again is worth a line on somebody's screen.

`drift_watch` had already reached half of this conclusion on its own: its
`needs_nudge` is one line that calls `press_watch.needs_nudge`, with a
docstring explaining that the reasoning is about cards and not about the
press. This file is the rest of that sentence.

## Why the cooldown lives on the card

Neither watcher can write a database. The deploy alarm this one replaces kept
its cooldown in a `notified_at` column of the row it alarmed about, which
needs `DATABASE_URL`, which no agent seat holds, so it raised to nobody for
nine days. The board is the one store every seat can write, so the card is its
own memory: the title carries the key, a second run on the same key finds its
own card, and the timestamps on that card's comments are how long it has been
since anybody was told.

## The one direction this errs in, on purpose

A card whose comment shape this does not recognise is treated as recently
nudged rather than as never nudged. The failure that costs something is a
comment every run, which teaches a reader to scroll past the card. The failure
that costs nothing is a quiet day on a finding that is already on the board
where somebody can see it.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import board  # noqa: E402
from tools import delivery_health as dh  # noqa: E402

#: One nudge a day on a finding that stays true, counted from the newest
#: comment the card already carries.
NUDGE_AFTER = timedelta(hours=24)

#: Which seat a guardrail's card lands on. Every watcher in this repository
#: reads a surface the engineer seat owns, and an unassigned card is a finding
#: with nobody holding it.
SEAT = "engineer"

#: Where the card goes. A guardrail's card in the backlog is a guardrail
#: nobody meets, so it asks for the working column by name. An unresolvable
#: name is not fatal: the card is worth more than its column.
COLUMN = "This sprint"


# ------------------------------------------------------------ the pure core


def comment_time(comment: dict) -> datetime | None:
    """When a comment was made, under whichever key the board used for it.

    Three spellings rather than one because the board's read shape has changed
    once already and a guardrail that loses its cooldown to a renamed key
    starts commenting every run.
    """
    for key in ("created_at", "createdAt", "updated_at"):
        when = dh._parse_iso(comment.get(key)) if isinstance(comment, dict) else None
        if when:
            return when
    return None


def needs_nudge(card: dict, now: datetime, after: timedelta = NUDGE_AFTER) -> bool:
    """Has it been long enough since this card last said anything."""
    comments = card.get("comments")
    if comments is None:
        # The board read that lists a column does not carry comments at all,
        # so this is the shape an unrecognised card has, not an empty one.
        return False
    if not comments:
        # Nothing has been said since the card was created, so the card's own
        # age is the age of the last thing said about this finding.
        created = comment_time(card)
        return bool(created) and now - created >= after
    times = [t for t in (comment_time(c) for c in comments) if t]
    return bool(times) and now - max(times) >= after


def find_card(payload: dict, marks: Sequence[str],
              prefix: str | None = None) -> dict | None:
    """The card that already carries this finding, or None.

    Matched on substrings of the title rather than on an id kept somewhere,
    because there is nowhere to keep one. Every column is searched, including
    Done, so a finding somebody has already closed is not alarmed about twice.

    `marks` are all required, which is what lets one subject hold two
    different findings: a week can be late and can also have been written on a
    fallback, and closing the first does not answer the second.
    """
    for item in payload.get("items") or []:
        title = item.get("title") or ""
        if prefix and not title.startswith(prefix):
            continue
        if all(mark in title for mark in marks if mark):
            return item
    return None


def company_here(company: str | None = None, env: dict | None = None) -> str:
    env = os.environ if env is None else env
    return (company
            or board.company_from_repo(env.get("GITHUB_REPOSITORY", ""))
            or "alexandria")


# ------------------------------------------------------------------- the run


def place(found: dict | None, *, payload: dict, title: str, body: str,
          nudge: str | None, now: datetime, company: str, tool: str,
          seat: str = SEAT, column: str | None = COLUMN,
          after: timedelta = NUDGE_AFTER) -> dict:
    """Create the card, nudge it, or leave it alone. Exactly one of the three.

    Returns what it did, as a dict, so a caller's `--json` and its prose render
    read the same answer rather than two.

    `nudge` of None means a finding that is said once and never repeated. A
    statement is that shape: the press printing on a fallback provider is worth
    a card and is not worth a reminder, because nothing about it gets worse by
    being left alone. An open fault is the opposite.

    `tool` is only ever used to name the caller in a warning on stderr, so a
    reader of a job log can tell which watcher could not resolve its column.
    """
    if found:
        if nudge is None or not needs_nudge(found, now, after):
            return {"action": "already on the board", "id": found.get("id"),
                    "title": found.get("title")}
        board.api(f"/api/items/{found['id']}/comments", method="POST",
                  payload={"company": company, "seat": seat, "body": nudge})
        return {"action": "nudged", "id": found.get("id"),
                "title": found.get("title")}

    item = {"company": company, "seat": seat, "title": title,
            "body": body, "horizon": "now"}
    if column:
        try:
            item["column_id"] = board.resolve_column(payload, column)
        except board.BoardError as exc:
            print(f"{tool}: {exc}. Creating the card without a column, "
                  "because the card matters and its column does not.",
                  file=sys.stderr)
    created = board.api("/api/items", method="POST", payload=item)
    return {"action": "created", "id": created.get("id"), "title": title}
