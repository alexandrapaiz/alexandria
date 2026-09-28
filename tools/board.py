#!/usr/bin/env python3
"""The company board, as a seat reads it and writes to it.

    python3 tools/board.py show                          # the board, as a human reads it
    python3 tools/board.py show --json                   # the same state, as an agent reads it
    python3 tools/board.py get --id <uuid>               # one item, with its comments and runs
    python3 tools/board.py item --title "..." --horizon now
    python3 tools/board.py move --id <uuid> --column "In progress"
    python3 tools/board.py comment --id <uuid> --body "shipped in #127"
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

#: A markdown bullet, including the one Slack renders. Written as an escape
#: rather than as the character, so every file in this repository stays plain
#: ASCII (ban-list entry 13).
BULLET_LINE = "^\\s*[-*•] "


class BoardError(RuntimeError):
    """Anything the board refused, or could not be asked."""


# --------------------------------------------------------------------------
# The pure core. No network, no environment, no clock.
# --------------------------------------------------------------------------


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


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
        "exit": args.status,
    }
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
        raise BoardError(f"board said {exc.code} to {method} {path}: {detail[:400]}") from None
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


def seat_of(args, env=None):
    env = os.environ if env is None else env
    seat = args.seat or env.get("ASC_SEAT") or seat_from_workflow(env.get("GITHUB_WORKFLOW"))
    if not seat:
        raise BoardError("this call needs a seat: pass --seat, or set ASC_SEAT")
    return seat


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
    payload = {
        "company": company_of(args),
        "seat": seat_of(args),
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
        "seat": seat_of(args),
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
    payload = {"company": company_of(args), "seat": seat_of(args), "body": args.body}
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        print(f"would POST /api/items/{args.id}/comments")
        return 0
    api(f"/api/items/{urllib.parse.quote(args.id)}/comments", method="POST", payload=payload)
    print(f"board: commented on {args.id}")
    return 0


def cmd_report(args):
    branch = args.branch if args.branch is not None else current_branch()
    payload = run_payload(os.environ, args, branch=branch, pr=pr_for_branch(branch))
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
        print(f"::warning::board: run report not posted, {exc}")
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
