#!/usr/bin/env python3
"""The company board, as a seat reads it and writes to it.

    python3 tools/board.py show                          # the board, as a human reads it
    python3 tools/board.py show --json                   # the same state, as an agent reads it
    python3 tools/board.py get --id <uuid>               # one item, with its comments and runs
    python3 tools/board.py item --title "..." --horizon now
    python3 tools/board.py move --id <uuid> --column "In progress"
    python3 tools/board.py comment --id <uuid> --body "shipped in #127"
    python3 tools/board.py inbox                         # the messages addressed to this seat
    python3 tools/board.py send --to-company Ursa --to-seat engineer --kind done ...
    python3 tools/board.py report --status success        # what a seat's last workflow step calls

Owner directive of 2026-09-27, `docs/standards/pm.md` §14: the board at
board.libraryofalexandria.dev is the state of the work, and every seat reads it
at the start of a run and writes to it as it works. This file is that door for
runs on GitHub runners, which reach the board over HTTP with `BOARD_API_URL`
and `BOARD_RUNTIME_TOKEN` in the environment. Runs on the host use the
`asc-board` MCP server instead and never need this file.

## Why this file stopped being a store and became a client

Until today this was a 937-line task manager of its own, keeping events as one
JSON file per event on a `board` ref, because of a constraint written into its
own docstring: the only database credential a seat's run held was
`NEON_RO_URL`, read-only on purpose, so there was nowhere a seat could write
that was not either the production corpus or `main`. That constraint ended when
the owner put `BOARD_RUNTIME_TOKEN` into all twelve seat workflows. The board
exists, it is the owner's, and it is the one the site and the host already
read.

Keeping both would have been the expensive outcome, not the safe one. Two
boards means every seat has to know which one the PM's ceremony reads, and the
first time they disagree the answer is whichever one the reader happened to
open. So the ref-based store is gone rather than deprecated, and what survives
from it is the part that was never about storage: filling a run report in from
the Actions environment so that twelve workflow files can each call one line.

## What this file cannot do, on purpose

pm.md §14's permission line is that a seat "creates, moves and comments on
items and reads them; it never creates or renames a company, a sprint, a column
or a view." There is no command here for any of those four, which is how the
line is enforced on this side of the wire. The server enforces it on its own
side too, and both halves should stay true: a rule that only one end checks is
the shape incident 20 is on record for.

## Three things the board refuses, found on 2026-10-14 by being refused

The server validates the prose a seat writes, which is the owner's house voice
enforced at the one point that cannot be skipped. Nothing in this repository
said so until a card was refused three times in a row, so the rules are here,
in the file every seat writes through, quoted from the refusals themselves.

**A body of labelled lines.**

    item refused: the prose must carry its reason in words (so that, because,
    otherwise): what you are doing and why, as a conversation, not a list of
    labels

**A code or a pull request number in the prose.**

    comment refused: prose must not carry codes or PR numbers ('PR #294'); say
    what happened in words and put ids in the data field

A command in backticks passed, and `PR #294` did not, so this is about
referring to work by its number instead of saying what it was.

**A block longer than `BODY_BLOCK_LIMIT` characters.**

    comment refused: prose must be scannable: one thought per line, a blank
    line between thoughts; a block over 420 characters is not

`scannable()` below is the shape half of that, and it is a formatter rather
than a validator on purpose. It cannot know the first two rules, which are
about what a sentence says, and the third is arithmetic. A write that is
refused anyway is still refused by the server, which is where the authority
belongs: this only means a seat does not lose an alarm to a line length.

## The message bus, and the one field that decides who is woken

`inbox` and `send` are the seventh and eighth commands, added 2026-10-24. The
bus is `/api/messages`, it is where cross-company work is routed, and until
today no command here could see it. Two runs of the engineer seat six days
apart were dispatched with "read your inbox on the board" and both found the
endpoint by probing the API with curl until a path answered
(`INC-2026-10-18-the-inbox-a-charter-names-has-no-reader-in-the-toolbox`, and
its repeat). A seat on a GitHub runner has this file and nothing else, so for
that seat the inbox did not exist at all.

**A message carries `to_seat` and `to_company`, and only both together name a
recipient.** Measured on the live bus on 2026-10-24, over the 500 messages it
returns: 374 carry both, 108 carry neither and are broadcasts, 15 carry a seat
with no company, and 3 carry a company with no seat. The 15 are the defect.
`engineer` is a seat in at least five companies, so a message addressed to
`engineer` with no company is delivered to all of them, and four seats read a
handoff that belongs to a fifth. Two of the three directed messages in this
seat's inbox on 2026-10-24 were exactly that, and neither was ours: one was
`alexandra-systems/pm` answering its own engineer about a pull request in the
HQ repository, and one was `Ursa/exo` writing to the Ursa engineer about a
merge driver this repository has never had.

So the two halves of that are enforced in opposite directions here.

`inbox` never pretends. It sorts what it reads into `yours`, `ambiguous` and
`broadcast`, prints the bucket on every line, and exits 0 only when nothing is
ambiguous: `3` means at least one message names this seat without naming a
company, and a reader has to decide whether it is theirs. A reader who is told
is a reader who can check. A reader who is not told acts on another company's
work.

`send` refuses to create one. `--to-seat` requires `--to-company`, because
this client should not be able to post the message it just had to warn about.
The exception is the pseudo-seats the bus uses for people and for the room,
`owner` and `everyone`, which belong to no company by construction.

## Run reports are append-only, so `report` runs once

The board's HTTP server implements GET and POST and answers PATCH, PUT and
DELETE with 501. A posted run report therefore cannot be edited or withdrawn.
Two things follow. `report` belongs in the last step of a run, once, with the
run's real outcome, and not at the start where it would have nothing to say.
And `--dry-run` exists because the alternative way to find out what a report
will contain is to spend it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

#: Seconds to wait on the board. Long enough for a cold container on the host,
#: short enough that a seat's last step cannot hang a run past its timeout.
TIMEOUT = 20

#: The longest block the board accepts in a body or a comment. Quoted from
#: its own refusal: "a block over 420 characters is not" scannable.
BODY_BLOCK_LIMIT = 420

#: The companies the board keeps, which pm.md §14 says are the repository
#: names. Used only to turn `GITHUB_REPOSITORY` into a company and to give a
#: readable error on a typo; the server holds the real list.
KNOWN_COMPANIES = (
    "alexandra-systems",
    "alexandria",
    "epitome",
    "Ursa",
    "atelier",
    "asc-router",
)

#: Where an item sits in time. The board's own vocabulary.
HORIZONS = ("now", "next", "later")

#: A job status, as GitHub's `job.status` reports it.
RUN_STATUSES = ("success", "failure", "cancelled", "skipped")

#: The same four statuses as the number the board's `exit` column stores.
#:
#: `INC-2026-10-16-every-run-report-fails-on-a-string-where-the-board-wants-a-
#: number-and-the-error-blames-the-database`: this file sent the word and the
#: board answered 503, so every run report any seat has ever filed was
#: rejected, and `cmd_report` swallowed it into a `::warning::` inside a green
#: job. Four probes on one token inside one minute isolated it: `0` and `"0"`
#: both answered 201, `"success"` and `"failure"` both answered 503.
#:
#: `skipped` maps to nothing on purpose. A job that never ran has no exit
#: code, and inventing a 0 for it would file the only status that means "this
#: seat did not work today" as the status that means it worked and succeeded.
#: The field is optional, so the honest report omits it.
EXIT_FOR_STATUS = {"success": 0, "failure": 1, "cancelled": 130, "skipped": None}

#: The codes that mean the board read the body and refused it, as opposed to
#: refusing the caller (401, 403), the route (404) or the moment (5xx). Only
#: these say the bug is in this file.
BODY_REJECTED = (400, 409, 422)

#: A markdown bullet, including the one Slack renders. Written as an escape
#: rather than as the character, so every file in this repository stays plain
#: ASCII (ban-list entry 13).
BULLET_LINE = "^\\s*[-*•] "

#: The kinds the bus accepts, quoted from its own refusal of a seventh:
#: "kind must be one of ('note', 'claim', 'release', 'ask', 'handoff', 'done')".
#: The 2026-10-18 ledger entry recorded five and said `handoff` was not one of
#: them. It is now, which is why this list is checked against the server's own
#: message rather than kept as lore in this file.
MESSAGE_KINDS = ("note", "claim", "release", "ask", "handoff", "done")

#: Seats that name a person or the room rather than a seat inside a company,
#: so a message to one of them has no company to carry and `send` does not ask
#: for one. Everything else is a seat inside a company and needs both halves.
COMPANYLESS_SEATS = ("owner", "everyone")

#: How far back `inbox` reads by default. A seat's run is a window of minutes
#: and the bus carries hundreds of messages a day, so a day is the span that
#: holds everything a run could owe an answer to without printing a week.
INBOX_SINCE_HOURS = 24

#: The most messages `inbox` asks for, which is the server's own ceiling:
#: `limit=1000` and `limit=500` return the same rows, so anything above 500 is
#: a request the server quietly rounds down. Asking for exactly the ceiling is
#: what makes `len(messages) == limit` a reliable signal that the window was
#: cut, which `render_inbox` prints rather than swallows. At 200, the default
#: this shipped with for one hour, a 24-hour read of this seat's own filtered
#: bus already lost its oldest six rows.
INBOX_LIMIT = 500

#: What `inbox` exits on when a message names this seat and names no company,
#: because that message may belong to another company's seat of the same name
#: and the reader is the only one who can tell. Distinct from 2, which main()
#: already uses for "the board refused, or could not be asked".
EXIT_AMBIGUOUS = 3



class BoardError(RuntimeError):
    """Anything the board refused, or could not be asked.

    `code` is the HTTP status when there was one, and None when the board was
    never reached. A caller that wants to tell its own bad request apart from
    the board having a bad day needs that number, and the message alone cannot
    be read for it: the board answered "the board's database is unreachable"
    to a payload it had type-rejected, so the prose said connectivity while
    the code said 5xx about a 4xx fault.
    """

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------
# The pure core. No network, no environment, no clock.
# --------------------------------------------------------------------------


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def scannable(text, limit=BODY_BLOCK_LIMIT):
    """Prose the board will accept on the shape rule: one thought per block.

    Three passes, widest boundary first, because each one cuts in a worse
    place than the one before. Sentences are where a thought actually ends.
    Clause marks are where it bends. A hard split at a space is a wrapped
    line, and it is here only because a refused alarm says nothing at all and
    a badly wrapped one still says the week is missing.

    Blocks already under the limit are returned untouched, so prose a seat
    wrote in short paragraphs passes through this unchanged.

    A sentence ends at a full stop *and whitespace*, which is the one subtle
    thing here. Until 2026-10-24 the sentence pass took every full stop as a
    boundary, so `8.5 days` was two sentences and the rejoin printed it as
    `8. 5 days`. Every one of these alarms is about a measurement and every
    measurement this org prints carries a decimal, so a formatter that
    corrupts numbers over 420 characters corrupts the only part of the card a
    reader acts on. It had been live since the function shipped, because the
    bodies that exercised it happened to keep their numbers in short blocks.
    """
    def cut(block, marks):
        pieces, current = [], ""
        for piece in marks:
            piece = piece.strip()
            if not piece:
                continue
            if current and len(current) + 1 + len(piece) > limit:
                pieces.append(current)
                current = piece
            else:
                current = f"{current} {piece}".strip()
        if current:
            pieces.append(current)
        return pieces

    out = []
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        block = " ".join(block.split())
        if not block:
            continue
        if len(block) <= limit:
            out.append(block)
            continue
        for sentence in cut(block, re.split(r"(?<=[.!?])\s+", block)):
            if len(sentence) <= limit:
                out.append(sentence)
                continue
            for clause in cut(sentence, re.split(r"(?<=[,:;]) ", sentence)):
                while len(clause) > limit:
                    head = clause[:limit].rsplit(" ", 1)[0] or clause[:limit]
                    out.append(head)
                    clause = clause[len(head):].strip()
                if clause:
                    out.append(clause)
    return "\n\n".join(out)


def result_line(pr_body, pr_title, limit=200):
    """One line of result, taken from the pull request the way Slack takes it.

    The owner's correction of 2026-09-26 was that a report reads as bullets
    rather than prose, so the first bullet of the description is the seat's own
    one-line summary of its run and is better than anything this tool could
    invent. A description with no bullets falls back to its title.
    """
    for line in (pr_body or "").splitlines():
        if re.match(BULLET_LINE, line):
            text = re.sub(BULLET_LINE + " *", "", line).replace("**", "").strip()
            if text:
                return text[:limit]
    return (pr_title or "").strip()[:limit]


def seat_from_workflow(workflow):
    """`engineer-agent` is the engineer seat. Ten of twelve workflows are named
    this way, so deriving the seat is what keeps the workflow step one line."""
    return re.sub(r"-agent$", "", (workflow or "").strip()) or ""


def company_from_repo(repository):
    """`alexandrapaiz/alexandria` is the `alexandria` company (pm.md §14)."""
    return (repository or "").split("/")[-1].strip()


def resolve_column(board, name):
    """A column name to the uuid `move` requires.

    The move endpoint takes `column_id` and nothing else: it answers
    `column_id is not a uuid: None` to a request naming a column, which means
    every caller has to read the board before it can move anything. Doing that
    here is the difference between a seat moving an item and a seat reading
    documentation about uuids.
    """
    columns = board.get("columns") or []
    wanted = (name or "").strip().casefold()
    for column in columns:
        if column.get("name", "").casefold() == wanted:
            return column["id"]
    known = ", ".join(repr(c.get("name")) for c in columns) or "none"
    raise BoardError(f"no column named {name!r} on this board. It has: {known}")


def render(board, seat=None, runs=10):
    """The board as text, one column at a time, then the newest run reports."""
    company = board.get("company") or {}
    sprint = board.get("sprint") or {}
    title = company.get("display_name") or company.get("name") or "board"
    lines = [title, "=" * len(title), ""]
    if sprint:
        lines.append(
            f"sprint {sprint.get('name')}  {sprint.get('starts_on')} to "
            f"{sprint.get('ends_on')}  ({sprint.get('status')})"
        )
        lines.append("")

    items = list(board.get("items") or [])
    if seat:
        items = [i for i in items if i.get("seat") == seat]
    placed = 0
    for column in sorted(board.get("columns") or [], key=lambda c: c.get("position", 0)):
        group = [i for i in items if i.get("column_id") == column["id"]]
        placed += len(group)
        lines.append(f"{column['name']}  ({len(group)})")
        for item in sorted(group, key=lambda i: (str(i.get("seat") or ""), i.get("title", ""))):
            who = item.get("seat") or "-"
            horizon = item.get("horizon") or "-"
            lines.append(f"  {item['id']}  {who:<9} {horizon:<6} {item.get('title', '')}")
        if not group:
            lines.append("  -")
        lines.append("")

    # A worker that drains a queue prints the depth of what it did not drain
    # (the 2026-09-19 ledger rule). Here that is any item no column claims,
    # which is the only way a board read can lose an item without saying so.
    known = {c["id"] for c in board.get("columns") or []}
    if stranded := [i for i in items if i.get("column_id") not in known]:
        lines.append(f"in no column this board declares  ({len(stranded)})")
        for item in stranded:
            lines.append(f"  {item['id']}  {item.get('column_id')!r}  {item.get('title', '')}")
        lines.append("")

    reports = list(board.get("runs") or [])
    if seat:
        reports = [r for r in reports if r.get("seat") == seat]
    if runs:
        lines.append(f"runs, newest first  ({plural(len(reports), 'run')} on this board)")
        for run in reports[:runs]:
            when = (run.get("ended_at") or run.get("started_at") or "")[:19] or "no time"
            pr = run.get("pr_url") or ""
            pr = "#" + pr.rsplit("/", 1)[-1] if pr else "no PR"
            summary = (run.get("report") or "")[:80]
            lines.append(
                f"  {when}  {run.get('seat', '-'):<9} {str(run.get('exit', '-')):<9} {pr:<7} {summary}"
            )
        if not reports:
            lines.append("  -")
        lines.append("")

    lines.append(
        f"{plural(placed, 'item')} in {plural(len(board.get('columns') or []), 'column')}, "
        f"{plural(len(reports), 'run')}"
    )
    return "\n".join(lines)


def address_of(message, seat, company):
    """Which of three buckets a message falls in, for this seat in this company.

    The whole point of this function is that `ambiguous` exists. A message
    with `to_seat` and no `to_company` names a seat that four other companies
    also have, so it is neither certainly ours nor certainly not, and the one
    thing a reader must not be told is that it is simply ours. Two of the
    three directed messages in this seat's inbox on the day this was written
    were in that state and both belonged to someone else.

    `theirs` is returned rather than dropped so a caller can count what it
    filtered. A filter that cannot say what it skipped is the defect
    (the same rule `--status` follows in tools/ledger.py).
    """
    to_seat = (message.get("to_seat") or "").strip()
    to_company = (message.get("to_company") or "").strip()
    if not to_seat and not to_company:
        return "broadcast"
    if to_seat and to_seat.casefold() != (seat or "").casefold():
        return "theirs"
    if to_company and to_company.casefold() != (company or "").casefold():
        return "theirs"
    if to_seat and not to_company:
        return "ambiguous"
    if to_company and not to_seat:
        # Addressed to the company and to no seat in it. Every seat there is a
        # plausible reader, so this is the company's room rather than a letter.
        return "broadcast"
    return "yours"


def sort_inbox(messages, seat, company):
    """The bus, bucketed, newest first, with `theirs` dropped and counted."""
    buckets = {"yours": [], "ambiguous": [], "broadcast": [], "theirs": []}
    for message in messages or []:
        buckets[address_of(message, seat, company)].append(message)
    for group in buckets.values():
        group.sort(key=lambda m: str(m.get("ts") or ""), reverse=True)
    return buckets


def render_inbox(buckets, seat, company, show_broadcast=False, width=100, truncated=False):
    """The inbox as a seat reads it, with the bucket named on every message.

    `ambiguous` prints before `yours` on purpose. It is the bucket that needs
    a decision, and a reader who stops after the first screen should have
    stopped on the one that needs them rather than on the one that does not.
    """
    def block(label, group, note=""):
        out = [f"{label}  ({plural(len(group), 'message')}){note}"]
        if not group:
            out.append("  -")
        for message in group:
            when = str(message.get("ts") or "")[:16].replace("T", " ")
            sender = f"{message.get('from_company') or '?'}/{message.get('from_seat') or '?'}"
            to_company = message.get("to_company") or "-"
            to_seat = message.get("to_seat") or "-"
            out.append(f"  {when}  {message.get('kind', '-'):<8} {sender} -> {to_company}/{to_seat}")
            out.append(f"      {str(message.get('subject') or '')[:width]}")
            if ref := message.get("ref"):
                out.append(f"      ref: {ref}")
            out.append(f"      id:  {message.get('id')}")
        out.append("")
        return out

    lines = [f"inbox for {company}/{seat}", "=" * (len(company) + len(seat) + 11), ""]
    lines += block(
        "addressed to this seat but to no company",
        buckets["ambiguous"],
        "  <- may belong to another company's seat of this name",
    )
    lines += block("addressed to this seat in this company", buckets["yours"])
    if show_broadcast:
        lines += block("broadcast", buckets["broadcast"])
    else:
        lines.append(
            f"{plural(len(buckets['broadcast']), 'broadcast')} not printed; --broadcast prints them"
        )
    lines.append(
        f"{plural(len(buckets['theirs']), 'message')} in the window addressed to someone else"
    )
    if truncated:
        # A queue-drainer prints the depth of what it did not drain, and an
        # inbox that silently stops at its own ceiling is the same defect it
        # was written to catch: a reader told nothing cannot check.
        lines.append(
            "the read hit its row ceiling, so this window is cut and an older "
            "message may be missing: narrow it with --since-hours"
        )
    return "\n".join(lines)


def message_payload(args, seat, company):
    """A message, with the addressing rule enforced before the network.

    `--to-seat` without `--to-company` is the defect this command exists not
    to commit, so it is refused here rather than sent and regretted. The
    server accepts it, which is why refusing it on this side is worth
    anything: see the measurement in this file's docstring.
    """
    if args.kind not in MESSAGE_KINDS:
        raise BoardError(
            f"kind must be one of {MESSAGE_KINDS}, not {args.kind!r}. The bus "
            "refuses a seventh and this list is quoted from its refusal."
        )
    to_seat = (args.to_seat or "").strip()
    to_company = (args.to_company or "").strip()
    if to_seat and not to_company and to_seat not in COMPANYLESS_SEATS:
        raise BoardError(
            f"--to-seat {to_seat!r} needs --to-company, because {to_seat!r} is a "
            f"seat in more than one company and a message naming only the seat "
            f"is delivered to all of them. Pass --to-company, or drop --to-seat "
            f"and let it be the broadcast it already is. The seats that need no "
            f"company are {COMPANYLESS_SEATS}."
        )
    payload = {
        "company": company,
        "seat": seat,
        "kind": args.kind,
        "subject": args.subject,
        "body": scannable(args.body),
    }
    if to_seat:
        payload["to_seat"] = to_seat
    if to_company:
        payload["to_company"] = to_company
    if args.ref:
        payload["ref"] = args.ref
    if args.reasoning:
        payload["reasoning"] = args.reasoning
    if args.data:
        try:
            payload["data"] = json.loads(args.data)
        except json.JSONDecodeError as exc:
            raise BoardError(f"--data is not JSON: {exc}") from None
    return payload


def run_payload(env, args, branch=None, pr=None):
    """A run report, filled in from the Actions environment.

    The workflow step passes the one thing it alone knows, `job.status`. Every
    other field here is derivable, and deriving it here is what keeps twelve
    workflow files identical and one line long.
    """
    seat = args.seat or env.get("ASC_SEAT") or seat_from_workflow(env.get("GITHUB_WORKFLOW"))
    if not seat:
        raise BoardError(
            "a run report needs a seat, and neither --seat, ASC_SEAT nor "
            "GITHUB_WORKFLOW gave one"
        )
    run_id = env.get("GITHUB_RUN_ID")
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    repo = env.get("GITHUB_REPOSITORY", "")
    payload = {
        "company": args.company or env.get("ASC_COMPANY") or company_from_repo(repo) or "alexandria",
        "seat": seat,
    }
    # The word enters here and the number leaves here, which is the one place
    # that keeps GitHub's vocabulary in the workflow and the board's in the
    # payload. See EXIT_FOR_STATUS.
    if (code := EXIT_FOR_STATUS.get(args.status)) is not None:
        payload["exit"] = code
    if repo:
        payload["repo"] = repo
    if trigger := env.get("GITHUB_EVENT_NAME"):
        payload["trigger"] = trigger
    if run_id and repo:
        payload["run_url"] = f"{server}/{repo}/actions/runs/{run_id}"
    if args.started_at:
        payload["started_at"] = args.started_at
    if args.ended_at:
        payload["ended_at"] = args.ended_at
    if args.turns is not None:
        payload["turns"] = args.turns
    if args.model:
        payload["model"] = args.model
    if pr:
        payload["pr_url"] = pr.get("url")
    if args.item:
        payload["item_ids"] = list(args.item)
    # The board's run row has no branch column, and the pull request url is the
    # better name for the work anyway. A run with no pull request has neither,
    # so there the branch is the only thing that says what was worked on.
    if args.report:
        payload["report"] = args.report
    elif pr:
        payload["report"] = result_line(pr.get("body"), pr.get("title"))
    elif branch:
        payload["report"] = f"no pull request on {branch}"
    return payload


# --------------------------------------------------------------------------
# The edges. Everything that touches the network, git or the environment.
# --------------------------------------------------------------------------


def base_url(env=None):
    env = os.environ if env is None else env
    url = (env.get("BOARD_API_URL") or "").rstrip("/")
    if not url:
        raise BoardError(
            "BOARD_API_URL is not set. Every seat workflow sets it (and "
            "BOARD_RUNTIME_TOKEN) from Actions secrets, so a local run has to "
            "export both itself. Every write also takes --dry-run, which needs "
            "neither."
        )
    return url


def api(path, method="GET", payload=None, env=None, opener=None):
    """One call to the board.

    The token is read here and never leaves here. A failure quotes the server's
    own message and the path it was asked, because an error that prints the
    request would print the credential with it.
    """
    env = os.environ if env is None else env
    token = env.get("BOARD_RUNTIME_TOKEN") or ""
    if not token:
        raise BoardError(
            "BOARD_RUNTIME_TOKEN is not set, so the board would answer 401. "
            "The seat workflows set it from an Actions secret."
        )
    url = base_url(env) + path
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=body, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    send = opener or urllib.request.urlopen
    try:
        with send(request, timeout=TIMEOUT) as response:
            raw = response.read().decode() or "{}"
    except urllib.error.HTTPError as exc:
        detail = (exc.read().decode(errors="replace") or "").strip()
        try:
            detail = json.loads(detail).get("error", detail)
        except json.JSONDecodeError:
            pass
        raise BoardError(
            f"board said {exc.code} to {method} {path}: {detail[:400]}", code=exc.code
        ) from None
    except urllib.error.URLError as exc:
        raise BoardError(f"board unreachable for {method} {path}: {exc.reason}") from None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise BoardError(f"board answered {method} {path} with something that is not JSON") from None


def company_of(args, env=None):
    env = os.environ if env is None else env
    name = (
        args.company
        or env.get("ASC_COMPANY")
        or company_from_repo(env.get("GITHUB_REPOSITORY", ""))
        or "alexandria"
    )
    if name not in KNOWN_COMPANIES:
        # Not fatal: the server holds the real list and may have grown one.
        print(
            f"board: {name!r} is not one of the companies pm.md names; "
            "sending it anyway and letting the board decide",
            file=sys.stderr,
        )
    return name


def seat_of(args, env=None, company=None):
    """The seat this call acts as, in the bare form the bus stores.

    The qualified form is accepted because this file prints it. Every message
    `render_inbox` renders reads `alexandria/research -> alexandria/engineer`,
    the manifests and the twelve charters name seats that way, and `send`
    reports its target that way too. So a reader who types back the form it
    was shown is following the file, and until this run it was answered with
    an inbox of zero messages in every bucket and an exit of 0
    (`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`).
    The true count at the minute the ExO seat measured it was 22.

    The failure was silent twice over. `to_seat=alexandria/engineer` matches no
    row on the bus, so `yours` is empty; and the narrowing happens on the
    server, so `theirs` -- the bucket whose whole job is to say what was
    filtered -- never receives a row either and reports zero with the same
    confidence. The only tell was the header, which read
    `inbox for alexandria/alexandria/engineer`.

    So a seat value this function cannot resolve raises instead of being passed
    through to a query that will answer empty. A disagreeing company half is
    the case worth refusing loudest: `--company alexandria --seat Ursa/engineer`
    is a reader asking two different questions, and answering either one of
    them silently is how a seat acts on another company's letter.
    """
    env = os.environ if env is None else env
    seat = args.seat or env.get("ASC_SEAT") or seat_from_workflow(env.get("GITHUB_WORKFLOW"))
    if not seat:
        raise BoardError("this call needs a seat: pass --seat, or set ASC_SEAT")
    seat = seat.strip()
    if not seat:
        raise BoardError("this call needs a seat: pass --seat, or set ASC_SEAT")
    if "/" not in seat:
        return seat
    qualifier, _, bare = seat.rpartition("/")
    # Both halves are checked before either is used. Trimming a stray slash
    # instead would turn `alexandria/` into a seat named `alexandria`, which is
    # a company name, and that query answers empty with a clean zero -- the
    # very shape of the defect this function was rewritten to stop.
    if not bare:
        raise BoardError(f"{seat!r} names a company and no seat after the slash")
    if not qualifier:
        raise BoardError(f"{seat!r} names a seat and no company before the slash")
    if "/" in qualifier:
        raise BoardError(
            f"{seat!r} is not a seat: the qualified form is one company and one "
            "seat joined by a single slash"
        )
    if company and qualifier.casefold() != company.casefold():
        raise BoardError(
            f"{seat!r} names company {qualifier!r} and this call is reading "
            f"{company!r}: name one company, not two"
        )
    return bare


def read_board(company, env=None, opener=None):
    return api(f"/api/board/{urllib.parse.quote(company)}", env=env, opener=opener)


def current_branch(root="."):
    proc = subprocess.run(
        ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def pr_for_branch(branch):
    """The pull request for this branch, or None. Never raises: a run whose
    report cannot name its PR still has a report worth posting."""
    if not branch:
        return None
    proc = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--state", "all",
         "--json", "number,title,url,body", "--jq", ".[0]"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        found = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return found if isinstance(found, dict) and found else None


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------


def column_id_for(company, name, dry_run=False):
    """The uuid for a column name, reading the board to find it.

    A `--dry-run` that cannot reach the board still has something worth
    printing, so there the unresolved name stands in for the id it would have
    become. A real write has no such licence and fails.
    """
    try:
        return resolve_column(read_board(company), name)
    except BoardError:
        if not dry_run:
            raise
        return f"<column_id of {name!r}, unresolved: the board was not reachable>"


def cmd_show(args):
    board = read_board(company_of(args))
    if args.json:
        print(json.dumps(board, indent=2, sort_keys=True))
        return 0
    print(render(board, seat=args.seat, runs=args.runs))
    return 0


def cmd_get(args):
    company = company_of(args)
    path = f"/api/items/{urllib.parse.quote(args.id)}?company={urllib.parse.quote(company)}"
    print(json.dumps(api(path), indent=2, sort_keys=True))
    return 0


def cmd_item(args):
    company = company_of(args)
    payload = {
        "company": company,
        "seat": seat_of(args, company=company),
        "title": args.title,
        "horizon": args.horizon,
    }
    if args.body:
        payload["body"] = args.body
    if args.column:
        payload["column_id"] = column_id_for(payload["company"], args.column, args.dry_run)
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print("would POST /api/items")
        return 0
    created = api("/api/items", method="POST", payload=payload)
    print(f"board: created {created.get('id')}  {args.title}")
    return 0


def cmd_move(args):
    company = company_of(args)
    payload = {
        "company": company,
        "seat": seat_of(args, company=company),
        "column_id": column_id_for(company, args.column, args.dry_run),
    }
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print(f"would POST /api/items/{args.id}/move")
        return 0
    api(f"/api/items/{urllib.parse.quote(args.id)}/move", method="POST", payload=payload)
    print(f"board: moved {args.id} to {args.column}")
    return 0


def cmd_comment(args):
    company = company_of(args)
    payload = {"company": company, "seat": seat_of(args, company=company), "body": args.body}
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print(f"would POST /api/items/{args.id}/comments")
        return 0
    api(f"/api/items/{urllib.parse.quote(args.id)}/comments", method="POST", payload=payload)
    print(f"board: commented on {args.id}")
    return 0


def read_messages(company, seat, since_hours, env=None, opener=None, limit=200):
    """The bus, filtered as narrowly as the server will filter it.

    `to_seat` and `to_company` are both sent, and the server answers with
    everything addressed to that seat, everything addressed to that company,
    the broadcasts, and the messages that name the seat and no company. That
    is wider than an inbox and it is the right width: a seat has to see the
    ambiguous ones to judge them. The narrowing happens in `sort_inbox`,
    where it can be printed rather than silently applied.
    """
    query = urllib.parse.urlencode(
        {
            "to_seat": seat,
            "to_company": company,
            "since_hours": since_hours,
            "limit": limit,
        }
    )
    answer = api(f"/api/messages?{query}", env=env, opener=opener)
    return list(answer.get("messages") or [])


def cmd_inbox(args):
    company = company_of(args)
    seat = seat_of(args, company=company)
    # Clamped to the server's own ceiling, because a caller who asks for 1000
    # gets 500 and `len(messages) >= limit` would then read as "not cut" on a
    # window that was. The signal is only honest if the number asked for is a
    # number the server can actually answer with.
    limit = min(args.limit, INBOX_LIMIT)
    messages = read_messages(company, seat, args.since_hours, limit=limit)
    truncated = len(messages) >= limit
    buckets = sort_inbox(messages, seat, company)
    if args.json:
        print(json.dumps({"truncated": truncated, **buckets}, indent=2, sort_keys=True))
    else:
        print(render_inbox(
            buckets, seat, company, show_broadcast=args.broadcast, truncated=truncated
        ))
    # The exit status is the gate (lessons L-A9). An ambiguous message is the
    # one finding here a reader has to act on, so it is the one that is
    # non-zero. Everything else is a clean read of a possibly empty inbox.
    return EXIT_AMBIGUOUS if buckets["ambiguous"] else 0


def cmd_send(args):
    company = company_of(args)
    payload = message_payload(args, seat_of(args, company=company), company)
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print("would POST /api/messages")
        return 0
    posted = api("/api/messages", method="POST", payload=payload)
    target = payload.get("to_company", "")
    target = f"{target}/{payload['to_seat']}" if payload.get("to_seat") else "everyone"
    print(f"board: sent {posted.get('id')} to {target}")
    return 0


def cmd_report(args):
    branch = args.branch if args.branch is not None else current_branch()
    payload = run_payload(os.environ, args, branch=branch, pr=pr_for_branch(branch))
    # A report with no timestamp at all prints as `no time` in the run list
    # and tells a reader nothing about when it happened. The filing time is
    # the one timestamp this command knows to be true, so it supplies that,
    # and never a start time, because a start time it did not observe would be
    # a claim about how long the run took.
    #
    # What this does not buy, measured against the live board on 2026-10-18:
    # the board orders its run list by `started_at`, so a report carrying only
    # an end time is stored, is returned by the API, and still sorts behind
    # every run that has a start. The caller has to pass `--started-at` to be
    # read in that list, and on a seat workflow that value is one expression
    # GitHub already knows. That is a workflow edit rather than a change here,
    # and it is filed in docs/ideas.md.
    payload.setdefault("ended_at", dt.datetime.now(dt.timezone.utc).isoformat())
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print("would POST /api/runs")
        return 0
    try:
        posted = api("/api/runs", method="POST", payload=payload)
    except BoardError as exc:
        # A report is not the work. The run already happened, and a red job for
        # an unposted report is the lie INC-2026-09-26-run-report-dash-echo
        # told six times: the PM's standup reads run health off these statuses.
        # So the exit code stays 0 whatever happened here.
        #
        # The annotation level is not the same question. A rejected body is a
        # bug in this file and nowhere else, so it is worth shouting about,
        # while a 401 is a missing secret and a 5xx is the board having a bad
        # minute, and neither is news this file can act on.
        #
        # Being exact about what this does not buy: the fault that forced
        # EXIT_FOR_STATUS came back as a 503, so this rule would have left it
        # a `::warning::` too. A server that reports a type rejection as a
        # connectivity failure cannot be classified by its own status code.
        # The gate that actually catches that class is in tests/test_board.py,
        # which asserts the payload this file builds, runs on every pull
        # request, and needs no board at all.
        level = "error" if exc.code in BODY_REJECTED else "warning"
        print(f"::{level}::board: run report not posted, {exc}")
        return 0
    print(f"board: reported {posted.get('id')} for {payload['seat']}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    # Every command takes these two, and they go on the subcommands rather than
    # on the top level so that `board.py show --seat engineer` works. Options
    # before a subcommand read as an afterthought and get typed after it anyway.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--company", help="board company; defaults to this repository's name")
    common.add_argument(
        "--seat",
        help="on a write, the seat acting, defaulting to ASC_SEAT or the workflow "
             "name; on `show`, the seat to filter the board down to",
    )

    show = sub.add_parser("show", parents=[common], help="print the board")
    show.add_argument("--json", action="store_true", help="the board as the API returns it")
    show.add_argument("--runs", type=int, default=10, help="how many run reports to print")
    show.set_defaults(func=cmd_show)

    get = sub.add_parser("get", parents=[common], help="print one item, with its comments and runs")
    get.add_argument("--id", required=True)
    get.set_defaults(func=cmd_get)

    item = sub.add_parser("item", parents=[common], help="create one item in the current sprint")
    item.add_argument("--title", required=True)
    item.add_argument("--body", default="")
    item.add_argument("--horizon", choices=HORIZONS, default="now")
    item.add_argument("--column", help="column name; the board's first column by default")
    item.add_argument("--dry-run", action="store_true")
    item.set_defaults(func=cmd_item)

    move = sub.add_parser("move", parents=[common], help="move one item to a column, named not numbered")
    move.add_argument("--id", required=True)
    move.add_argument("--column", required=True)
    move.add_argument("--dry-run", action="store_true")
    move.set_defaults(func=cmd_move)

    comment = sub.add_parser("comment", parents=[common], help="comment on one item")
    comment.add_argument("--id", required=True)
    comment.add_argument("--body", required=True)
    comment.add_argument("--dry-run", action="store_true")
    comment.set_defaults(func=cmd_comment)

    inbox = sub.add_parser(
        "inbox", parents=[common], help="the messages addressed to this seat"
    )
    inbox.add_argument(
        "--since-hours", type=int, default=INBOX_SINCE_HOURS, dest="since_hours"
    )
    inbox.add_argument("--limit", type=int, default=INBOX_LIMIT)
    inbox.add_argument("--broadcast", action="store_true", help="print the broadcasts too")
    inbox.add_argument("--json", action="store_true", help="the three buckets, for an agent")
    inbox.set_defaults(func=cmd_inbox)

    send = sub.add_parser("send", parents=[common], help="post one message onto the bus")
    send.add_argument("--kind", required=True, choices=MESSAGE_KINDS)
    send.add_argument("--subject", required=True)
    send.add_argument("--body", required=True)
    send.add_argument("--to-seat", dest="to_seat", help="needs --to-company unless it is owner or everyone")
    send.add_argument("--to-company", dest="to_company")
    send.add_argument("--ref", help="a url the message is about")
    send.add_argument("--reasoning", default="", help="how the claim in the body was checked")
    send.add_argument("--data", help="a JSON object of ids and numbers, which the prose may not carry")
    send.add_argument("--dry-run", action="store_true")
    send.set_defaults(func=cmd_send)

    report = sub.add_parser("report", parents=[common], help="post this run's report onto the board, once")
    report.add_argument("--status", required=True, choices=RUN_STATUSES, help="GitHub's job.status")
    report.add_argument("--report", help="the run's one line; the PR's first bullet by default")
    report.add_argument("--branch", help="defaults to the checked-out branch")
    report.add_argument("--started-at", dest="started_at")
    report.add_argument("--ended-at", dest="ended_at")
    report.add_argument("--turns", type=int)
    report.add_argument("--model")
    report.add_argument("--item", action="append", default=[], help="an item id this run worked on")
    report.add_argument("--dry-run", action="store_true")
    report.set_defaults(func=cmd_report)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except BoardError as exc:
        print(f"board: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
