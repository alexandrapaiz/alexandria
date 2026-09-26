# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-26 (Saturday standup)

**PR #113 note.** `alexandria-pm/2026-09-26-window` (PR #113, draft,
authored by the owner's account, "PM sync session 2026-09-26") is a
synchronous session from earlier today, last active 2026-09-26T01:25Z
(about 13.5 hours before this run). It also writes this file. It was not
built on: its content is stale by design (a queue is replaced in full
each run) and the session itself ended hours ago with no dispatch
currently in flight, so there is nothing to merge forward except its
"Dispatched by the PM" record (okr, PR #114), which is preserved
permanently in that PR's own description and in `gh run list`, not in
this file. Recommended order: merge #113 first (it is the record of
today's ADR-037 relay and the okr dispatch), then this PR, since this
file's content fully replaces #113's version of the same file either
way.

### 1. frontend — the board's read-only view, queued and ready

**Trigger.** HQ ADR-037 priority 1 (relayed live in PR #113). Engineer
built the store in open PR #115 ("the board's own store, and every run
reports onto it"), shipped `docs/board.md` as an explicit spec for this
seat ("written so the frontend seat can build the next slice from it
without asking"), and already queued item `board-ui` on the `board` ref
itself: `status: next, assignee: frontend, note: "queued by the PM in
#113; reads the board ref, see docs/board.md"`. Frontend's own last PR
(#108) is merged, so the hard stop against dispatching a seat with an
open PR does not apply.

**Cost of skipping it today.** The store exists and nobody reads it. The
owner's stated requirement ("every run reports live on the board")
stays half-true: runs report, nothing shows them.

**Status: attempted, not fired — see the 403 below.** This is not a
"proposed, copy this" entry; it is the record of a real attempt that
`INC-2026-09-26-dispatch-403-repeat` documents. The exact command, for
the owner or chair to run by hand:

```bash
gh workflow run agent-frontend.yml -f owner_instructions='Build the read-only board view on the site. Trigger: HQ ADR-037 priority 1 (relayed live in PR #113, "PM sync session 2026-09-26"), which the engineer seat then built in open PR #115 ("the board'"'"'s own store, and every run reports onto it"). PR #115 ships docs/board.md as your spec and already queued item `board-ui` on the board ref (status: next, assignee: frontend, note: "queued by the PM in #113; reads the board ref, see docs/board.md"). PR #115 is still open, so branch from engineer/2026-09-26-board-store, not main: tools/board.py, board/views.json, and docs/board.md only exist on that branch today. Per docs/board.md'"'"'s own "Reading it from the site" section: fetch the whole board with one request, GET https://codeload.github.com/alexandrapaiz/alexandria/tar.gz/refs/heads/board (1,029 bytes gzipped as of 2026-09-26), untar server-side, keep files under board/events/, and fold them with the same rules tools/board.py fold uses (items are last-write-wins per field ordered by `at`; runs keep the latest per seat and the whole list in order). Do not use the GitHub trees API plus one request per file — unauthenticated GitHub API calls are capped at 60/hour, which a fold of a thousand events exhausts on first render. Read the view columns from board/views.json rather than inventing your own. This slice is read-only: no view-creation UI (only the owner'"'"'s merge to board/views.json on main may add a view, per docs/board.md), no workflow step, no item dependencies/labels/comments/due-date alarms. Move item `board-ui` to `doing` via `python3 tools/board.py item --id board-ui --status doing --assignee frontend` when you start, and to `review` when your PR is open.'
```

Both `gh workflow run` and the direct `gh api .../dispatches -X POST`
form failed identically:

```
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
(https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361059087/dispatches)
```

Full diagnosis, including a confirmed new lead (the active token is a
GitHub App installation token, `ghs_...`, authenticated as `claude[bot]`,
not the plain Actions `GITHUB_TOKEN`), in
`INC-2026-09-26-dispatch-403-repeat`.

### Why nothing else is in the queue

**engineer, writer, research, skill, and okr are all disqualified** by
the hard rule ("never propose a dispatch for a seat whose last pull
request is still open"): engineer has #60, #110, #115, #116 open;
writer has #107, #112 open; research has #109 open; skill has #111
open; okr has #114 open.

**market and security have no fresh, evidenced trigger.** Market's last
PR (#103) is merged and its newest brief (2026-09-25) proposes one item,
and it names engineer ("confirm the pipeline bills at Opus 5.5's new,
lower price"), not market or security, so it is not a trigger for either
seat today; it is already in `docs/ideas.md` as `proposed` for the
ceremony run to groom. Security's last run was 2026-09-24 with no open
PR since, and nothing in the newest decisions, the newest market or
research brief, or `pending.md` names undone security work.

Only one entry this run, not three, because the queue holds evidenced
triggers and not a quota to fill.

## Run health

**Fleet health, since the last PM run (2026-09-25T15:46:46Z schedule,
success).**

- **Two new-class failures, work survived.** `engineer-agent` runs
  `36208446311` (schedule, 01:26:48Z, became PR #115) and `36208644267`
  (workflow_dispatch, 01:30:22Z, became PR #116) both finished their
  actual work (the `claude-code-action` step and the no-ship tripwire
  both succeeded, both PRs exist and are open) and then failed the job
  at the Slack-notify sub-step of "Post run report," identically: `jq`
  parse error on control characters, exit code 4. New failure class,
  first time seen, already repeated twice today, recorded as
  `INC-2026-09-26-slack-notify-jq-control-chars`.
- **One cancelled run, already registered.** `writer-agent` run
  `36206422947` (00:52:19Z, cancelled) matches
  `INC-2026-09-24-writer-dispatch-started-twice`'s pattern, not a new
  entry.
- **One workflow-machinery finding, already filed by the reporting
  seat.** PR #115 (engineer) filed `INC-2026-09-26-deploy-workflow-no-smoke-run`
  for `deploy-main.yml` reaching main on 2026-09-25 with no smoke run
  behind it. Not duplicated here; flagged so the owner sees it named
  once.
- **Everything else since the last PM run is a plain success**:
  okr (`36207911573`), writer x2, skill, research, frontend (`36206159763`,
  merged as PR #108), one more engineer run (`36206420676`, PR #110),
  and this morning's scheduled writer/engineer/pm/market runs. One
  scheduled `engineer-agent` run (`36250253554`) is still `in_progress`
  as this PR opens; its result is not yet known.
- **This run's own dispatch attempt 403'd.** See the queue entry above
  and `INC-2026-09-26-dispatch-403-repeat`, a repeat of
  `INC-2026-09-24-dispatch-403` with new diagnostic evidence.

**Delivery health.**

- **The press.** No database credentials in this sandbox, so `digests`
  itself was not queried (same limitation every standup since
  2026-09-24 has noted). `https://libraryofalexandria.dev/library`
  returns 200 and still lists `2026-W39` as the newest issue. No new
  weekly issue is expected before Monday 2026-09-28 09:00 UTC, so this
  is not a staleness finding. The daily pipeline's corpus growth was not
  independently checked this run (no DB access); reported as unchecked,
  not as green.
- **The site.** `https://libraryofalexandria.dev/` returns 200, serving
  current content.
- **The MCP server.** Checked deeper than the last few standups' bare
  `GET /`: `https://ap4509--alexandria-mcp-serve.modal.run/mcp` answers
  `401` (expected, unauthenticated) rather than timing out, and
  `/.well-known/oauth-protected-resource` returns a well-formed JSON
  body naming the same host as its authorization server. Both confirm
  the MCP protocol layer is actually serving requests, not only that
  the container is alive.

## Pending items past their date

Read `docs/sprints/pending.md` (last touched 2026-09-24; not rewritten
this run, out of scope for a standup per charter §0/§4). Three items
flagged there are now resolved and the file does not yet say so, a
ceremony-run job, not a standup one, but worth naming so nobody re-reads
them as open: PR #95 (writer) merged 2026-09-26T00:22:04Z, PR #98
(market) merged 2026-09-26T00:22:17Z, both same morning. **PR #60
(engineer, "the pre-send quality gate") is still open since
2026-09-20T14:44:15Z** — six days now, the oldest open PR in the repo,
and `pending.md` has been asking for "rebase or retirement" on it since
2026-09-24. **The Polar account setup (owner-only action) is due today,
2026-09-26**; this run has no way to confirm it happened (no secrets
access, by design), so it is named here rather than assumed either way.

## Linear trial

Not checked this run (no new signal since the 2026-09-19 ruling; still
on trial).

## Dispatched by the PM

None fired. One attempted (frontend, above) and blocked by
`INC-2026-09-26-dispatch-403-repeat`, not by a missing trigger or a
guardrail. The instruction is recorded above for the owner or chair to
run by hand.
