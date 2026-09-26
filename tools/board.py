#!/usr/bin/env python3
"""The board: our own task manager, and the log of every seat's runs.

    python3 tools/board.py show                      # the board, as a human reads it
    python3 tools/board.py show --view runs --json   # the same state, as an agent reads it
    python3 tools/board.py report --status success   # what a seat's workflow step calls
    python3 tools/board.py item --id board-ui --title "Read-only board view" \
        --status next --assignee frontend

Owner's ruling of 2026-09-26 (HQ ADR-037 item 1): the board is ours, it
replaces Linear, seats cannot create views, and every seat run reports onto
it. This file is the whole store's write path and read path. There is no
other writer.

## Where the state lives, and why it is not in the two obvious places

**Not in Neon.** The only database credential a seat's run holds is
`NEON_RO_URL`, which is read-only on purpose. Writing run reports to Postgres
would mean minting a writable URL and handing it to all twelve seats, so the
cost of a board would be that every agent run could write the production
corpus. That is an authority change, not a storage choice, and it belongs to
the owner the same way the `workflow`-scoped PAT in
docs/agents/pending-workflow-changes.md does.

**Not on `main`.** Two reasons, and the second one is the expensive one. A
seat may not push to main at all, so a report would have to travel by pull
request and would appear only after a merge, which is the one moment a board
is no longer worth reading. And since 2026-09-25 a push to main runs
`deploy-main.yml`, so twelve seats reporting twice a day would spend 24
production deploys a day against the vendor's 100/day limit that HQ incident 5
is already on record for.

**So: the `board` branch, one JSON file per event, append only.** It is a real
ref in this repository, which costs nothing, needs no new secret, and is
readable by `git` and, because this repository is public, by an unauthenticated
GitHub API call from the site. Nothing merges it into main and nothing deploys
it. Conflicts are impossible rather than handled: an event's path contains the
run id or a content hash, so no two writers ever address the same path. This
is ADR-9's blackboard, which the pipeline's workers already coordinate through,
pointed at the seats instead of at the papers.

**The views are the other half, and they live on `main`** in
`board/views.json`. A view only becomes real for everyone when the owner
merges it, which is how "seats cannot create views" is enforced by something
sturdier than a sentence in a charter. This file has no command that writes a
view, and it refuses an item whose status is not one of the columns that file
declares, so a seat cannot invent a column either. What a seat can still do is
edit `board/views.json` on its own branch and see the result inside its own
run. It cannot show that view to anybody else.
"""

import argparse
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: The ref the state lives on. Never merged into main, never deployed.
BOARD_REF = "board"
EVENTS_DIR = "board/events"
VIEWS_FILE = "board/views.json"

#: The fields an `item` event may set. A fold is a last-write-wins patch over
#: these, so adding a field here is the only thing needed to carry a new one.
ITEM_FIELDS = ("title", "status", "assignee", "note", "pr", "due")

#: A run report's shape, which is the owner's list: seat, run id, PR, result.
RUN_FIELDS = ("seat", "run_id", "attempt", "status", "branch", "pr", "result", "url")

RUN_STATUSES = ("success", "failure", "cancelled", "skipped")

SLUG = re.compile(r"[^a-z0-9]+")


# --------------------------------------------------------------------------
# The pure core. No network, no git, no clock: everything below is a function
# of its arguments, which is why the tests can hold all of it.
# --------------------------------------------------------------------------


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def slugify(text, limit=48):
    return SLUG.sub("-", (text or "").lower()).strip("-")[:limit] or "untitled"


def now_iso(clock=None):
    clock = clock or (lambda: datetime.now(timezone.utc))
    return clock().strftime("%Y-%m-%dT%H:%M:%SZ")


def event_path(event):
    """Where an event is stored, and the reason two writers never collide.

    A run report's path is derived from the run id and the attempt, so it is
    the same path every time that attempt reports. Posting twice is then a
    no-op rather than a duplicate row, which matters because the workflow step
    runs under `if: always()` and a re-run of a failed job keeps the run id.

    An item event is a patch and every patch counts, so its path carries the
    timestamp and a hash of the payload. Two different patches cannot collide;
    the same patch twice is the same path, and again a no-op.
    """
    kind = event["kind"]
    day = event["at"][:10]
    if kind == "run":
        name = f"{slugify(event['seat'])}-{event['run_id']}-{event.get('attempt', 1)}"
        return f"{EVENTS_DIR}/run/{day}/{name}.json"
    if kind == "item":
        stamp = event["at"].replace(":", "").replace("-", "")
        payload = json.dumps(event, sort_keys=True).encode()
        digest = hashlib.sha256(payload).hexdigest()[:8]
        return f"{EVENTS_DIR}/item/{day}/{stamp}-{slugify(event['id'])}-{digest}.json"
    raise ValueError(f"unknown event kind: {kind!r}")


def validate(event, views):
    """Refuse an event the board cannot hold, and say what was wrong.

    Called before the write, so a bad event never reaches the ref. The status
    check is the interesting one: the columns come from `board/views.json` on
    main, so a seat cannot invent a column by writing an item into it.
    """
    problems = []
    kind = event.get("kind")
    if kind not in ("run", "item"):
        return [f"kind must be 'run' or 'item', not {kind!r}"]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event.get("at", "")):
        problems.append("at must be an ISO UTC timestamp like 2026-09-26T02:11:44Z")
    if kind == "run":
        for field in ("seat", "run_id", "status"):
            if not str(event.get(field, "")).strip():
                problems.append(f"a run report needs {field}")
        if event.get("status") not in RUN_STATUSES:
            problems.append(f"status must be one of {', '.join(RUN_STATUSES)}")
        if "\n" in str(event.get("result", "")):
            problems.append("result is one line")
    if kind == "item":
        if not str(event.get("id", "")).strip():
            problems.append("an item event needs an id")
        columns = views.get("columns", [])
        status = event.get("status")
        if status is not None and status not in columns:
            problems.append(
                f"status {status!r} is not a column. The columns are "
                f"{', '.join(columns)}, and they are declared in {VIEWS_FILE} on "
                "main, so a new one takes a pull request the owner merges."
            )
    return problems


def fold(events):
    """The board's current state, folded out of the append-only log.

    Items are last-write-wins per field, so a `move` is just an item event
    carrying a status and nothing else. Runs keep the latest per seat and the
    whole list in order, because the board answers two different questions:
    what is each seat doing now, and what has the fleet been doing.
    """
    items, runs = {}, []
    for event in sorted(events, key=lambda e: (e.get("at", ""), event_path(e))):
        if event["kind"] == "item":
            item = items.setdefault(event["id"], {"id": event["id"], "events": 0})
            for field in ITEM_FIELDS:
                if field in event:
                    item[field] = event[field]
            item["events"] += 1
            item["updated"] = event["at"]
            item["by"] = event.get("by", item.get("by"))
        elif event["kind"] == "run":
            runs.append({field: event.get(field) for field in RUN_FIELDS} | {"at": event["at"]})
    latest = {}
    for run in runs:
        latest[run["seat"]] = run
    return {"items": items, "runs": runs, "latest_run": latest}


def resolve_view(views, name):
    """A named view, or an error that teaches the rule it just enforced."""
    available = views.get("views", {})
    if name not in available:
        raise SystemExit(
            f"board: no view named {name!r}. The views are "
            f"{', '.join(sorted(available)) or 'none'}. Seats do not create views: "
            f"a new one is an edit to {VIEWS_FILE} that the owner merges "
            "(her ruling of 2026-09-26)."
        )
    view = dict(available[name])
    view.setdefault("title", name)
    view.setdefault("group_by", "status")
    view.setdefault("columns", views.get("columns", []))
    view.setdefault("runs", 0)
    return view


def render(state, view, views):
    """The board as text. One column per group, then the runs the view asks for."""
    lines = [view["title"], "=" * len(view["title"]), ""]
    items = list(state["items"].values())
    if flt := view.get("filter", {}):
        items = [i for i in items if all(i.get(k) == v for k, v in flt.items())]

    group_by = view["group_by"]
    if group_by == "status":
        groups = [(column, [i for i in items if i.get("status") == column]) for column in view["columns"]]
    else:
        keys = sorted({str(i.get(group_by) or "unassigned") for i in items})
        groups = [(key, [i for i in items if str(i.get(group_by) or "unassigned") == key]) for key in keys]

    placed = 0
    for name, group in groups:
        lines.append(f"{name}  ({len(group)})")
        placed += len(group)
        for item in sorted(group, key=lambda i: (str(i.get("assignee") or ""), i["id"])):
            who = item.get("assignee") or "-"
            pr = f"  #{item['pr']}" if item.get("pr") else ""
            lines.append(f"  {item['id']:<28} {who:<10} {item.get('title', '')}{pr}")
        if not group:
            lines.append("  -")
        lines.append("")

    # A worker that drains a queue prints the depth of what it did not drain
    # (the 2026-09-19 ledger rule). Here that is the items no column holds,
    # which is how a status dropped from views.json becomes visible instead of
    # silently hiding its items.
    if stranded := [i for i in items if group_by == "status" and i.get("status") not in view["columns"]]:
        lines.append(f"not in any column of this view  ({len(stranded)})")
        for item in stranded:
            lines.append(f"  {item['id']:<28} {item.get('status')!r}")
        lines.append("")

    if view["runs"]:
        lines.append(f"runs, newest first  ({plural(len(state['runs']), 'run')} recorded)")
        for run in list(reversed(state["runs"]))[: view["runs"]]:
            pr = f"#{run['pr']}" if run.get("pr") else "no PR"
            result = (run.get("result") or "")[:96]
            lines.append(f"  {run['at']}  {run['seat']:<10} {run['status']:<9} {pr:<7} {result}")
        lines.append("")
    lines.append(
        f"{plural(placed, 'item')} in {plural(len(views.get('columns', [])), 'column')}, "
        f"{plural(len(state['runs']), 'run')}"
    )
    return "\n".join(lines)


def result_line(pr_body, pr_title, limit=200):
    """One line of result, taken from the PR the way the Slack step takes it.

    The owner's correction of 2026-09-26 was that a report reads as bullets
    rather than prose, so the first bullet of the description is the seat's own
    one-line summary of its run and is better than anything this tool could
    invent. A description with no bullets falls back to its title.
    """
    for line in (pr_body or "").splitlines():
        if re.match(r"^\s*[-*•] ", line):
            text = re.sub(r"^\s*[-*•] +", "", line).replace("**", "").strip()
            if text:
                return text[:limit]
    return (pr_title or "").strip()[:limit]


# --------------------------------------------------------------------------
# The edges. Everything that touches git, the API or the environment.
# --------------------------------------------------------------------------


def _run(argv, check=True, stdin=None):
    proc = subprocess.run(argv, capture_output=True, text=(stdin is None), input=stdin)
    if check and proc.returncode != 0:
        err = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode(errors="replace")
        raise RuntimeError(f"{' '.join(argv[:3])} failed: {err.strip()[:400]}")
    return proc


def gh_api(path, method="GET", payload=None, check=True):
    argv = ["gh", "api", "--method", method, path]
    if payload is not None:
        argv += ["--input", "-"]
    proc = subprocess.run(
        argv, capture_output=True, text=True, input=json.dumps(payload) if payload is not None else None
    )
    if proc.returncode != 0:
        if check:
            raise RuntimeError(f"gh api {method} {path} failed: {proc.stderr.strip()[:400]}")
        return None
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def repo_slug():
    return os.environ.get("GITHUB_REPOSITORY") or _run(
        ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
    ).stdout.strip()


def load_views(root=ROOT):
    """The views, from the working tree. Missing or broken is a hard error.

    Not a default and not an empty dict: the columns are the only thing
    stopping a seat from inventing one, so a board that cannot read them
    refuses to write rather than accepting anything.
    """
    path = Path(root) / VIEWS_FILE
    if not path.exists():
        raise SystemExit(f"board: {VIEWS_FILE} is missing, so no column or view is defined.")
    try:
        views = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"board: {VIEWS_FILE} is not valid JSON ({exc}).")
    if not views.get("columns"):
        raise SystemExit(f"board: {VIEWS_FILE} declares no columns.")
    return views


def ensure_ref(repo, message="The board's state lives here"):
    """Create the `board` ref if it does not exist. Idempotent, and orphan.

    Orphan on purpose: the state shares no history with main, so nothing about
    it can be mistaken for something under review, and a `git log` of main
    never fills with run reports.
    """
    if gh_api(f"repos/{repo}/git/ref/heads/{BOARD_REF}", check=False):
        return False
    readme = (
        "# The board's state\n\n"
        "Append-only. One JSON file per event under `board/events/`, written only by\n"
        "`tools/board.py`. This branch is never merged into main and never deployed.\n"
        "Read it with `python3 tools/board.py show`.\n"
    )
    tree = gh_api(
        f"repos/{repo}/git/trees",
        "POST",
        {"tree": [{"path": "README.md", "mode": "100644", "type": "blob", "content": readme}]},
    )
    commit = gh_api(f"repos/{repo}/git/commits", "POST", {"message": message, "tree": tree["sha"]})
    gh_api(f"repos/{repo}/git/refs", "POST", {"ref": f"refs/heads/{BOARD_REF}", "sha": commit["sha"]})
    return True


def write_event(event, views, repo=None, attempts=4, sleep=time.sleep, update=False):
    """Put one event on the board ref. Returns "written", "exists" or "updated".

    A second post of the same run attempt is a no-op by default, which is what
    `if: always()` firing twice should cost. `update=True` replaces it instead,
    for the one case that needs it: a report written before its pull request
    description was final, where the stale line is worse than a second write.

    The Contents API rather than a push, for two reasons. It cannot touch the
    working tree, so a seat's own branch is never disturbed by reporting, and
    it cannot reach main even by mistake. Two seats writing at the same instant
    address different paths but move the same ref, which the API answers with a
    409; that is the retry, and it is the only one.
    """
    if problems := validate(event, views):
        raise SystemExit("board: this event was refused:\n  " + "\n  ".join(problems))
    repo = repo or repo_slug()
    ensure_ref(repo)
    path = event_path(event)
    body = json.dumps(event, indent=2, sort_keys=True) + "\n"
    payload = {
        "message": f"board: {event['kind']} {event.get('seat') or event.get('id')}",
        "content": base64.b64encode(body.encode()).decode(),
        "branch": BOARD_REF,
    }
    for attempt in range(1, attempts + 1):
        proc = subprocess.run(
            ["gh", "api", "--method", "PUT", f"repos/{repo}/contents/{path}", "--input", "-"],
            capture_output=True,
            text=True,
            input=json.dumps(payload),
        )
        if proc.returncode == 0:
            return "updated" if "sha" in payload else "written"
        # Any failure asks one question before retrying: is the event already
        # there? Paths are deterministic, so a path that exists means this
        # event was already posted, and that is a success rather than a race to
        # retry. The API answers a create against an existing path with a 422
        # about a missing `sha`, which is exactly this case.
        existing = gh_api(f"repos/{repo}/contents/{path}?ref={BOARD_REF}", check=False)
        if existing and existing.get("sha"):
            if not update:
                return "exists"
            # Replace rather than duplicate: the API takes the blob's sha as
            # the caller's proof it knew what it was overwriting.
            payload["sha"] = existing["sha"]
            if attempt < attempts:
                continue
        if attempt == attempts:
            raise RuntimeError(f"board: could not write {path}: {proc.stderr.strip()[:400]}")
        sleep(min(2 ** attempt, 8))
    return "written"  # pragma: no cover - the loop returns or raises


def read_events(ref=None, root=ROOT, fetch=True):
    """Every event on the board ref, read with git rather than the API.

    `git archive` hands back the whole subtree in one call, so reading a year
    of reports is one subprocess instead of nine thousand HTTP requests. The
    site cannot use this path and does not need to: on a public repository the
    same state is two unauthenticated calls, which docs/board.md writes out.
    """
    ref = ref or f"refs/remotes/origin/{BOARD_REF}"
    if fetch:
        subprocess.run(
            ["git", "-C", str(root), "fetch", "--quiet", "origin", f"+{BOARD_REF}:refs/remotes/origin/{BOARD_REF}"],
            capture_output=True,
        )
    proc = subprocess.run(
        ["git", "-C", str(root), "archive", ref, EVENTS_DIR], capture_output=True
    )
    if proc.returncode != 0:
        return []  # no ref yet, or no events on it: an empty board, not an error
    events = []
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tar:
        for member in tar.getmembers():
            if not (member.isfile() and member.name.endswith(".json")):
                continue
            raw = tar.extractfile(member).read()
            try:
                event = json.loads(raw)
            except json.JSONDecodeError:
                event = None
            if not isinstance(event, dict) or event.get("kind") not in ("run", "item"):
                # One unreadable file must not take the whole board down with
                # it, and must not pass unmentioned either.
                print(f"board: skipped {member.name}, which is not an event", file=sys.stderr)
                continue
            events.append(event)
    return events


def env_report(env, args, root=ROOT):
    """A run report, filled in from the Actions environment and from git.

    The workflow step passes the one thing it alone knows, `job.status`. Every
    other field is derivable, and deriving it here is what keeps twelve
    workflow files identical and one line long.
    """
    workflow = env.get("GITHUB_WORKFLOW", "")
    seat = args.seat or re.sub(r"-agent$", "", workflow) or "unknown"
    run_id = args.run_id or env.get("GITHUB_RUN_ID") or "local"
    branch = args.branch
    if branch is None:
        proc = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
        )
        branch = proc.stdout.strip() if proc.returncode == 0 else ""
    pr, result = args.pr, args.result
    if (pr is None or result is None) and branch:
        proc = subprocess.run(
            ["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number,title,url,body",
             "--jq", ".[0]"],
            capture_output=True, text=True,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            found = json.loads(proc.stdout)
            pr = pr if pr is not None else found.get("number")
            result = result if result is not None else result_line(found.get("body"), found.get("title"))
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    repo = env.get("GITHUB_REPOSITORY", "")
    event = {
        "kind": "run",
        "at": now_iso(),
        "seat": seat,
        "run_id": str(run_id),
        "attempt": int(args.attempt or env.get("GITHUB_RUN_ATTEMPT") or 1),
        "status": args.status,
        "branch": branch,
        "result": result or "",
    }
    if pr:
        event["pr"] = int(pr)
    if repo and run_id != "local":
        event["url"] = f"{server}/{repo}/actions/runs/{run_id}"
    return event


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------


def cmd_show(args):
    views = load_views()
    state = fold(read_events(fetch=not args.no_fetch))
    if args.seat:
        state["runs"] = [r for r in state["runs"] if r["seat"] == args.seat]
        state["items"] = {k: v for k, v in state["items"].items() if v.get("assignee") == args.seat}
    if args.json:
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0
    print(render(state, resolve_view(views, args.view), views))
    return 0


def cmd_report(args):
    views = load_views()
    event = env_report(os.environ, args)
    if args.dry_run:
        print(json.dumps(event, indent=2, sort_keys=True))
        print(f"would write {event_path(event)} on {BOARD_REF}")
        return 0
    outcome = write_event(event, views, update=args.update)
    print(f"board: {outcome} {event_path(event)}")
    return 0


def cmd_item(args):
    views = load_views()
    event = {"kind": "item", "at": now_iso(), "id": args.id, "by": args.by}
    for field in ITEM_FIELDS:
        if (value := getattr(args, field, None)) is not None:
            event[field] = int(value) if field == "pr" else value
    if args.dry_run:
        print(json.dumps(event, indent=2, sort_keys=True))
        print(f"would write {event_path(event)} on {BOARD_REF}")
        return 0
    print(f"board: {write_event(event, views)} {event_path(event)}")
    return 0


def cmd_init(args):
    repo = repo_slug()
    created = ensure_ref(repo)
    print(f"board: ref {BOARD_REF} {'created' if created else 'already exists'} on {repo}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show", help="print the current board")
    show.add_argument("--view", default="board")
    show.add_argument("--seat", help="only this seat's items and runs")
    show.add_argument("--json", action="store_true", help="the state as an agent reads it")
    show.add_argument("--no-fetch", action="store_true", help="read the ref already fetched")
    show.set_defaults(func=cmd_show)

    report = sub.add_parser("report", help="post this run's report onto the board")
    report.add_argument("--status", required=True, choices=RUN_STATUSES)
    report.add_argument("--seat")
    report.add_argument("--run-id")
    report.add_argument("--attempt")
    report.add_argument("--branch")
    report.add_argument("--pr")
    report.add_argument("--result", help="one line; defaults to the PR's first bullet")
    report.add_argument("--dry-run", action="store_true")
    report.add_argument(
        "--update",
        action="store_true",
        help="replace this run attempt's report instead of leaving the first one, "
        "for a report written before the pull request description was final",
    )
    report.add_argument(
        "--strict",
        action="store_true",
        help="fail the caller when the board cannot be written; off by default, "
        "because a board outage must not fail a seat's run",
    )
    report.set_defaults(func=cmd_report)

    item = sub.add_parser("item", help="create or update one board item")
    item.add_argument("--id", required=True)
    item.add_argument("--title")
    item.add_argument("--status")
    item.add_argument("--assignee")
    item.add_argument("--note")
    item.add_argument("--pr")
    item.add_argument("--due")
    item.add_argument("--by", default=os.environ.get("BOARD_ACTOR", "seat"))
    item.add_argument("--dry-run", action="store_true")
    item.set_defaults(func=cmd_item)

    init = sub.add_parser("init", help="create the board ref if it does not exist")
    init.set_defaults(func=cmd_init)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "report" and not args.strict:
        # The board is a window, not a gate. A seat's run is not less finished
        # because the report did not land, so this path swallows everything and
        # says what happened. `--strict` is for the tests and for a human
        # debugging the store.
        try:
            return args.func(args)
        except (SystemExit, RuntimeError, OSError, ValueError) as exc:
            print(f"board: report not posted ({exc})", file=sys.stderr)
            return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
