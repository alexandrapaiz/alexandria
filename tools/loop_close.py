#!/usr/bin/env python3
"""A self-improvement proposal is done when the pipeline reads it, not when it merges.

    python3 tools/loop_close.py                   # judge every open proposal, print
    python3 tools/loop_close.py --json            # the same verdict as a script reads it
    python3 tools/loop_close.py --post            # a board card for anything merged and dark
    python3 tools/loop_close.py --write           # close the live ones (needs DATABASE_URL)
    python3 tools/loop_close.py --proposals f.json --receipt f.json   # offline facts

`mcp/server.py`'s `propose_change` is the meta-review's hand on the system: it
opens a pull request against `prompts/*.md` or `sources.yaml` and writes a
`promotions` row with `kind = 'system_diff'`. The body it writes says "merging
this PR is the approval (ADR-7)", and that sentence is true about the approval
and was read by this organization as the end of the loop.

It is not the end of the loop. `modal deploy` bakes the repository into an
image, so a merge and a deploy are two events, and the gap between them is
where the only self-improvement proposal this product has ever merged went to
die. `INC-2026-10-12-meta-review-proposal-merged-never-deployed`: commit
`fa029bf` changed `prompts/triage.md` on 2026-10-05, the triage job went on
running `ea61cbc` of 2026-09-29, and 8,861 rows were judged against the old
prompt before anybody noticed. The 2026-10-18 OKR check-in graded O3 KR2 "met
on the letter, not on the spirit" for exactly that reason: "the merge bought
nothing, because the prompt it changed has not judged a single paper."

So the closing condition moves. A proposal is `live` when the image that reads
its file is running code that contains the merge, and `dark` while it is
merged and the image is not. `dark` is the state this file exists to name,
because it is the state that used to be called done.

## What the question is asked against, and why none of it is hand-kept

**Which app reads a file** comes from `pipeline/runtime_sha.APPS` and the
`add_local_file` manifest in each job's own module, through
`runtime_sha.local_entries`. Today every target `propose_change` can write has
exactly one reader (`sources.yaml` to `ingest`, `prompts/triage.md` to
`triage`, `prompts/interpret.md` to `interpret`, `prompts/distill*.md` to
`distill`, `prompts/digest*.md` to `weekly`), and none of that is written
down here, because a hand-kept copy of an image's file list is a copy that
disagrees with the deploy on the day it matters. A file no image adds has no
deploy to confirm, and that is `no_reader` rather than a quiet pass.

**Which commit an image was built from** comes from
`tools.delivery_health.undeployed_commits`, which replays the deploy digest
over the app's own history until it matches the digest the container wrote.
That function owns the rule and this file calls it, for the reason
`tools/drift_watch.py` gives about the same function: a second implementation
of one rule agrees with the first only by luck.

**Whether the merge is in that commit** is `git merge-base --is-ancestor`,
over the whole repository rather than over the file's history. Ancestry is
the exact question. A pathspec'd `git log` is not: history simplification
picks one parent at a merge, so a true merge commit can be absent from the
log of the very file it changed, and a sha-in-a-list test would call a
deployed proposal dark.

## Ancestry needs the history, so this guard says what it needs

The host clones one commit deep, and `git merge-base --is-ancestor` on a
grafted history answers "no" for every commit that is really an ancestor.
That is the same trap `undeployed_commits` already fell into, and the same
deepening fetch answers both: this file calls `delivery_health`'s, once, and
reports `unknown` rather than `dark` when the history is still truncated.
Refusing to answer is the only safe failure here, because `dark` writes a
card and `live` closes a row.

## The dark window, which is the number the OKR wanted

`first_seen_at` on the `deploy_runtime` row is when the image now running
started running. For a proposal whose merge that image contains, it is the
latest moment the proposal can have gone live, so the window from `merged_at`
to `first_seen_at` is an upper bound on how long the merge bought nothing.
Reported as a bound and never as a measurement, because an earlier image this
org never recorded may well have carried it first.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from tools import delivery_health as dh  # noqa: E402

#: What this guard needs from the runtime it is run in, as data rather than as
#: a docstring a changed runtime can silently falsify. `git_history` is "full"
#: because ancestry over a grafted clone is wrong rather than unavailable.
NEEDS = {"git_history": "full", "egress": True, "database": False}

#: The states a proposal can be in. `dark` is the one this file was written
#: for; `done` is `live`, and nothing else counts as done.
OPEN = "open"
LIVE = "live"
DARK = "dark"
NO_READER = "no_reader"
UNKNOWN = "unknown"

#: What `propose_change` is allowed to target (`mcp/server.py`). A pull
#: request that touched other files as well is judged on these and the rest is
#: reported, because a proposal that smuggled a code change past the regex is
#: a finding rather than something to average over.
TARGETABLE = ("prompts/", "sources.yaml")

#: The board column and the title prefix a dark proposal's card carries.
CARD_PREFIX = "Self-improvement: "


def targets(files: list[str]) -> tuple[list[str], list[str]]:
    """Split a pull request's files into the ones a proposal may change, and the rest."""
    inside = [f for f in files
              if f == "sources.yaml" or f.startswith("prompts/")]
    return inside, [f for f in files if f not in inside]


def apps_reading(path: str, repo_root: pathlib.Path,
                 ref: str = "HEAD") -> list[str]:
    """Every scheduled app whose image contains this repository path.

    Read out of each app's own manifest at `ref` rather than from a table
    here. An empty list is the real answer for a file no image adds, and the
    caller reports it rather than treating it as nothing to check.
    """
    from pipeline import runtime_sha

    found = []
    for app in sorted(runtime_sha.APPS):
        paths = dh._paths_at(repo_root, app, ref)
        if paths is None:
            continue
        for key in paths:
            if key == path or (key.endswith("/") and path.startswith(key)):
                found.append(app)
                break
    return found


def contains(repo_root: pathlib.Path, ancestor: str, descendant: str) -> bool | None:
    """Is `ancestor` in `descendant`'s history. None when git cannot say.

    `git merge-base --is-ancestor` exits 0 for yes and 1 for no, and any other
    status is a commit this checkout does not hold, which is not a no.
    """
    status, _ = dh._git(repo_root, "merge-base", "--is-ancestor",
                        ancestor, descendant)
    if status == 0:
        return True
    if status == 1:
        return False
    return None


def _parse(value) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def judge_one(proposal: dict, deploy: dict, repo_root: pathlib.Path,
              ref: str = "HEAD") -> dict:
    """One proposal's state, with the evidence that reached it.

    `proposal` carries what GitHub knows: `pr_url`, `merged`, `merge_commit`,
    `merged_at`, `files`. `deploy` is `deploy_facts`' shape, one entry per app.
    """
    out = {"id": proposal.get("id"), "pr_url": proposal.get("pr_url"),
           "merged_at": proposal.get("merged_at")}

    if not proposal.get("merged"):
        out.update(state=OPEN,
                   why="the pull request has not merged, so the loop is still running")
        return out

    merge_commit = proposal.get("merge_commit")
    if not merge_commit:
        out.update(state=UNKNOWN,
                   why="the pull request is merged and no merge commit came "
                       "back with it, so nothing can be placed against the deploy")
        return out

    inside, outside = targets(proposal.get("files") or [])
    out["files"] = inside
    if outside:
        out["off_target"] = outside
    if not inside:
        out.update(state=NO_READER,
                   why="this pull request changed nothing `propose_change` can "
                       "target, so there is no prompt for a deploy to start reading")
        return out

    pairs, unknowns, dark, live = [], [], [], []
    for path in inside:
        apps = apps_reading(path, repo_root, ref)
        if not apps:
            pairs.append({"path": path, "app": None, "state": NO_READER,
                          "why": "no scheduled image adds this file, so no "
                                 "deploy can confirm it"})
            continue
        for app in apps:
            row = (deploy or {}).get(app) or {}
            found = dh.undeployed_commits(repo_root, app,
                                          row.get("runtime_sha"), ref=ref)
            if "why" in found:
                pairs.append({"path": path, "app": app, "state": UNKNOWN,
                              "why": found["why"]})
                unknowns.append(app)
                continue
            held = contains(repo_root, merge_commit, found["deployed_commit"])
            entry = {"path": path, "app": app,
                     "deployed_commit": found["deployed_commit"],
                     "deployed_at": found["deployed_at"],
                     "first_seen_at": str(row.get("first_seen_at") or "")}
            if held is None:
                entry.update(state=UNKNOWN,
                             why=f"this checkout cannot place {merge_commit[:8]} "
                                 f"against {found['deployed_commit']}, which is "
                                 f"a truncated history rather than a no")
                unknowns.append(app)
            elif held:
                entry.update(state=LIVE)
                live.append(app)
            else:
                entry.update(state=DARK,
                             why=f"{app} is running {found['deployed_commit']} "
                                 f"of {found['deployed_at'][:10]}, which does "
                                 f"not contain this merge")
                dark.append(app)
            pairs.append(entry)

    out["pairs"] = pairs
    # Order matters and it is the order of safety. An unknown anywhere stops a
    # close, because closing a row is the thing that cannot be taken back by
    # the next run. A dark anywhere is dark, because a proposal that reaches
    # one of its two readers has not reached production.
    if unknowns:
        out.update(state=UNKNOWN,
                   why=f"the deploy could not be placed for {', '.join(sorted(set(unknowns)))}")
        return out
    if dark:
        out.update(state=DARK,
                   why=f"merged, and {', '.join(sorted(set(dark)))} has not "
                       f"deployed it")
        return out
    if not live:
        out.update(state=NO_READER,
                   why="nothing scheduled reads the files this proposal "
                       "changed, so a deploy cannot confirm it")
        return out

    out.update(state=LIVE)
    seen = [_parse(p.get("first_seen_at")) for p in pairs
            if p.get("state") == LIVE]
    seen = [s for s in seen if s]
    merged_at = _parse(proposal.get("merged_at"))
    if seen:
        latest = max(seen)
        out["live_no_later_than"] = latest.isoformat()
        if merged_at:
            out["dark_days"] = round((latest - merged_at).total_seconds() / 86400, 1)
    out["why"] = (f"every image that reads these files contains the merge"
                  + (f", dark for at most {out['dark_days']} days"
                     if out.get("dark_days") is not None else ""))
    return out


def judge(proposals: list[dict], deploy: dict | str,
          repo_root: pathlib.Path | None = None,
          ref: str | None = None) -> dict:
    """Every proposal's state, plus the one sentence a reader wants first."""
    root = pathlib.Path(repo_root or pathlib.Path(__file__).resolve().parents[1])
    if isinstance(deploy, str):
        return {"verdict": UNKNOWN, "why": deploy, "proposals": [],
                "ref": ref or ""}

    # The deepening fetch, once, before a single ancestry question is asked.
    # `judge_deploy` does this for its own reasons and this file needs it for
    # a sharper one: a grafted history answers "not an ancestor" for a commit
    # that is one, which is a false `dark`, which writes a card.
    deepened = False
    if dh._is_shallow(root):
        deepened = dh._deepen(root)
    ref = ref or dh._deployable_ref(root)

    judged = [judge_one(p, deploy, root, ref) for p in proposals]
    states = [p["state"] for p in judged]
    if not judged:
        verdict, why = "ok", "no system_diff proposal is open"
    elif UNKNOWN in states:
        verdict = UNKNOWN
        why = (f"{states.count(UNKNOWN)} of {len(states)} proposals could not "
               f"be placed against production")
    elif DARK in states:
        verdict = "failing"
        why = (f"{states.count(DARK)} merged proposal(s) are dark: the prompt "
               f"changed and the job reading it has not")
    else:
        verdict = "ok"
        why = (f"{states.count(LIVE)} live, {states.count(OPEN)} still open, "
               f"{states.count(NO_READER)} with no scheduled reader")
    return {"verdict": verdict, "why": why, "proposals": judged,
            "ref": ref, "deepened": deepened,
            "shallow": dh._is_shallow(root)}


# ------------------------------------------------------------------ the facts


def connect():
    """A connection when this environment holds one, and None when it does not.

    None is the ordinary case and not an error: no agent seat holds
    `DATABASE_URL`, which is why the judgement below reads the published
    receipt and the pull requests instead. Only the Modal jobs and the owner's
    laptop reach this branch, and only they can write the done event down.
    """
    import os

    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        return None
    try:                                                 # pragma: no cover
        import psycopg

        return psycopg.connect(url, connect_timeout=15)
    except Exception as exc:                             # pragma: no cover
        print(f"loop_close: DATABASE_URL is set and the connection failed "
              f"({exc})", file=sys.stderr)
        return None


PROPOSAL_SQL = """
select id, path, created_at, live_at
  from promotions
 where kind = 'system_diff'
   and live_at is null
 order by id
"""


def proposals_from_db(conn) -> list[dict] | str:
    """Open `system_diff` rows, as `judge` wants them, minus what GitHub knows."""
    try:
        rows = conn.execute(PROPOSAL_SQL).fetchall()
    except Exception as exc:
        return f"promotions could not be read: {exc}"
    return [{"id": row[0], "pr_url": row[1], "proposed_at": str(row[2])}
            for row in rows]


def pr_number(url: str) -> int | None:
    try:
        return int(str(url).rstrip("/").rsplit("/", 1)[-1])
    except (ValueError, AttributeError):
        return None


def pr_facts(url: str, repo_root: pathlib.Path) -> dict:
    """What GitHub says about one proposal's pull request.

    Through `gh`, because every seat that runs this holds a `gh` the host
    already authenticated and none of them holds a bare GitHub token to put in
    a header. A `gh` that cannot answer is a reason to say `unknown`, which is
    what the empty dict below becomes in `judge_one`.
    """
    import subprocess

    number = pr_number(url)
    if number is None:
        return {"merged": False, "why": f"{url} is not a pull request url"}
    try:
        done = subprocess.run(
            ["gh", "pr", "view", str(number), "--json",
             "mergedAt,mergeCommit,state,files"],
            capture_output=True, text=True, timeout=60, cwd=str(repo_root))
    except (OSError, subprocess.SubprocessError) as exc:
        return {"merged": False, "why": f"gh could not be run: {exc}"}
    if done.returncode != 0:
        return {"merged": False,
                "why": f"gh could not read PR {number}: {done.stderr.strip()[:200]}"}
    try:
        got = json.loads(done.stdout)
    except ValueError as exc:
        return {"merged": False, "why": f"gh returned no JSON for PR {number}: {exc}"}
    merged = got.get("state") == "MERGED"
    return {"merged": merged,
            "merge_commit": (got.get("mergeCommit") or {}).get("oid"),
            "merged_at": got.get("mergedAt"),
            "files": [f.get("path") for f in (got.get("files") or [])]}


def gather(repo_root: pathlib.Path, proposals_file: str | None,
           receipt_file: str | None) -> tuple[list[dict], dict | str]:
    """The two inputs, from files when given and from the world when not."""
    if proposals_file:
        rows = json.loads(pathlib.Path(proposals_file).read_text())
    else:
        rows = _proposals_from_the_world(repo_root)

    enriched = []
    for row in rows:
        if "merged" in row:          # a fixture already carries the PR facts
            enriched.append(row)
            continue
        enriched.append({**row, **pr_facts(row.get("pr_url", ""), repo_root)})

    if receipt_file:
        payload = json.loads(pathlib.Path(receipt_file).read_text())
    else:
        payload, why = dh.read_receipt()
        if payload is None:
            return enriched, why
    return enriched, (dh.receipt_facts(payload)[2])


def _proposals_from_the_world(repo_root: pathlib.Path) -> list[dict]:
    """Open proposals, from the database when there is one and from `gh` when not.

    No agent seat holds `DATABASE_URL`, which is the whole reason
    `tools/drift_watch.py` exists in the shape it does. So the fallback reads
    the pull requests themselves: `propose_change` titles every one of them
    `meta: <path>`, and that title is the only handle a seat without the
    database has on the same set of rows.
    """
    import subprocess

    conn = connect()
    if conn is not None:                                # pragma: no cover
        try:
            with conn:
                rows = proposals_from_db(conn)
            if isinstance(rows, list):
                return rows
            print(f"loop_close: {rows}", file=sys.stderr)
        except Exception as exc:
            print(f"loop_close: the database could not be read ({exc}), "
                  f"falling back to the pull requests", file=sys.stderr)
    try:
        done = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "100",
             "--search", "meta: in:title", "--json", "number,url,title"],
            capture_output=True, text=True, timeout=60, cwd=str(repo_root))
        found = json.loads(done.stdout) if done.returncode == 0 else []
    except (OSError, subprocess.SubprocessError, ValueError):
        found = []
    return [{"id": None, "pr_url": p["url"], "title": p.get("title")}
            for p in found
            if str(p.get("title", "")).startswith("meta: ")]


# ------------------------------------------------------------------- the write


CLOSE_SQL = """
update promotions
   set live_at = coalesce(%s, now()),
       status = case when status = 'proposed' then 'approved' else status end,
       decided_at = coalesce(decided_at, now())
 where id = %s and kind = 'system_diff' and live_at is null
"""


def close_live(conn, judged: list[dict]) -> list[dict]:
    """Write the done event for every proposal a deploy has confirmed.

    `live_at` is the loop's own done event and it is the whole point of this
    file: it is set here, after a deploy-confirmation read, and nowhere near a
    merge. `status` moves to `approved` alongside it because ADR-7's gate did
    pass, and the two columns now say two different things, which is the
    distinction the organization did not have.
    """
    wrote = []
    for item in judged:
        if item.get("state") != LIVE or item.get("id") is None:
            continue
        conn.execute(CLOSE_SQL, (item.get("live_no_later_than"), item["id"]))
        wrote.append({"id": item["id"], "live_at": item.get("live_no_later_than")})
    if wrote:
        conn.commit()
    return wrote


# -------------------------------------------------------------------- the card


def card_text(item: dict) -> tuple[str, str]:
    """The title and body of the board card one dark proposal earns."""
    number = pr_number(item.get("pr_url") or "")
    where = ", ".join(sorted({p["app"] for p in item.get("pairs") or []
                              if p.get("state") == DARK}))
    files = ", ".join(item.get("files") or [])
    title = (f"{CARD_PREFIX}#{number} merged and is not running"
             if number else f"{CARD_PREFIX}a merged proposal is not running")
    body = (
        f"{item.get('pr_url')} changed `{files}` and merged"
        f"{' on ' + str(item['merged_at'])[:10] if item.get('merged_at') else ''}.\n\n"
        f"The image that reads it has not been rebuilt, so the merge has "
        f"bought nothing yet: `{where}` is still running code that does not "
        f"contain it.\n\n"
        + "\n".join(f"- `{p['app']}` is on `{p['deployed_commit']}` "
                    f"of {str(p.get('deployed_at'))[:10]}"
                    for p in item.get("pairs") or [] if p.get("state") == DARK)
        + "\n\nThe loop closes when the deploy happens and not before "
          "(`tools/loop_close.py`). One command closes it:\n\n"
          "```\nmodal deploy " + "\n".join(
              sorted({_entrypoint(p["app"]) for p in item.get("pairs") or []
                      if p.get("state") == DARK})) + "\n```\n")
    return title, body


def _entrypoint(app: str) -> str:
    from pipeline import runtime_sha
    return runtime_sha.APPS.get(app, app)


def post(judged: list[dict], now: datetime, dry_run: bool = False) -> list[dict]:
    """A card for every dark proposal, created once and nudged daily after."""
    from tools import board, board_alarm

    dark = [p for p in judged if p.get("state") == DARK]
    if not dark:
        return []
    company = board_alarm.company_here()
    payload = board.api(f"/api/board/{company}")
    done = []
    for item in dark:
        title, body = card_text(item)
        found = board_alarm.find_card(payload, [title], prefix=CARD_PREFIX)
        if dry_run:
            done.append({"action": "would post" if not found else "already on the board",
                         "title": title})
            continue
        done.append(board_alarm.place(
            found, payload=payload, title=title, body=body,
            nudge=f"Still dark on {now.date().isoformat()}.",
            now=now, company=company, tool="loop_close"))
    return done


# --------------------------------------------------------------------- the CLI


def render(result: dict) -> str:
    lines = [f"loop_close: {result['verdict'].upper()} — {result['why']}",
             f"  judged against {result.get('ref') or 'HEAD'}"
             + ("  (history deepened here)" if result.get("deepened") else "")]
    for item in result.get("proposals") or []:
        head = f"  [{item['state']:9}] {item.get('pr_url') or item.get('id')}"
        lines.append(head)
        if item.get("why"):
            lines.append(f"              {item['why']}")
        for pair in item.get("pairs") or []:
            lines.append(f"              {pair.get('app') or '-':10} "
                         f"{pair['path']:28} {pair['state']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--post", action="store_true",
                        help="put a card on the board for anything dark")
    parser.add_argument("--write", action="store_true",
                        help="close the live ones in promotions (needs DATABASE_URL)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--proposals", help="a JSON file of proposals, for a run offline")
    parser.add_argument("--receipt", help="a JSON file of the delivery receipt")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--today", default=None)
    args = parser.parse_args(argv)

    root = pathlib.Path(args.repo_root or pathlib.Path(__file__).resolve().parents[1])
    now = _parse(args.today) or datetime.now(timezone.utc)

    proposals, deploy = gather(root, args.proposals, args.receipt)
    result = judge(proposals, deploy, root)

    if args.post:
        result["posted"] = post(result["proposals"], now, dry_run=args.dry_run)
    if args.write and not args.dry_run:
        import os
        if not os.environ.get("DATABASE_URL"):
            print("loop_close: --write needs DATABASE_URL, and this run has "
                  "none, so nothing was closed", file=sys.stderr)
        else:                                            # pragma: no cover
            conn = connect()
            if conn is None:
                print("loop_close: DATABASE_URL is set and the connection "
                      "failed, so nothing was closed", file=sys.stderr)
            else:
                with conn:
                    result["closed"] = close_live(conn, result["proposals"])

    print(json.dumps(result, indent=2, default=str) if args.json else render(result))
    return {"ok": 0, "failing": 1, UNKNOWN: 2}.get(result["verdict"], 2)


if __name__ == "__main__":
    raise SystemExit(main())
