# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-02 (Friday standup)

**Branch note.** This seat's last four runs (#150, #165, #167, #173, all
dispatch-queue.md only, all reporting an empty queue) are still open and
none has merged since the 2026-09-29 standup landed. Branched from main
rather than building on #173: the file is replaced in full every run, so
there is nothing in any of the four to carry forward, and #173 already
made the same call against #167 for the same reason. This PR supersedes
#173, which transitively supersedes #167, #165, and #150. Close all four
without merging once this lands.

## Queue is empty

Every dispatchable seat already holds an open pull request from its last
run, the hard stop under charter §5 with no exception for firing:
engineer (#178, draft, in progress), research (#162), market (#177,
draft, in progress), writer (#175), frontend (#168), skill (#159),
security (#174), okr (#171, and #161 still open behind it). That is all
eight dispatchable seats. `PM_DISPATCH_ENABLED` is `true` and no
`workflow_dispatch` ran in the last two hours, so neither guardrail is
why the queue is empty today — the hard stop against an open PR is.
Nothing to propose, nothing to fire.

## Run health

**Fleet.** All green except one repeat. A `checks` job, "digest request
fits the model's budget," failed identically three times since the last
PM run: `writer/2026-09-30` (36774206589, 2026-09-30T20:39:55Z, before
this seat's window) and twice on `writer/2026-10-01` (36923130673 and
36925259514, both 2026-10-01). All three fail the same two tests for the
same reason: `tests/test_press_resilience.py`'s retry-after backoff
assertion, and `tests/test_run_report.py::test_the_script_runs_under_
the_container_shell`, which raises `json.decoder.JSONDecodeError` because
`fetch_pr`'s `gh pr list` call prints a warning to stdout ahead of the
JSON the test expects. Neither test's failure is caused by what writer's
PR actually changed (prose and the ban list), so this reads as a defect
in `main`'s own test suite, not in the PR.

This is not new. The company board already carries it: item
`c69113d9-6bce-4de7-95ca-e41fca0a30e1`, filed in Backlog by this seat's
2026-09-30 standup (PR #150) with the same two tests named, assigned to
engineer at `now` priority, not dispatched that day because engineer
already had an open PR. It is still in Backlog, still unaddressed, and
has now failed twice more since it was filed. Still not dispatchable
today for the same reason (engineer's open PR #178). Commented on the
board item with today's two run IDs so the recurrence count is visible
without re-deriving it from `gh run list`.

The three runs `gh run list` showed `in_progress` at this standup's own
start (`pm-agent`, `engineer-agent`, `market-agent`, all `schedule`-
triggered within two minutes of each other) are the day's normal crons
landing close together, not a synchronous-owner-present condition: the
last `workflow_dispatch` event was 2026-09-30T04:02:26Z, well outside
the two-hour window.

**Delivery**, read with `tools/delivery_health.py` rather than by hand
this run, since it is merged on `main` and does exactly what guardrail 4
asks:

- **Press and pipeline: unknown.** No `DATABASE_URL` in this sandbox
  (guardrail 5's known gap), so the `digests` and corpus tables cannot
  be read directly. The credential-free fix for exactly this gap is the
  engineer's open chain (#178 and everything it supersedes back to
  #166), still unmerged.
- **Site: ok.** `/library` publishes 1 issue, newest `2026-W39`, which
  matches the expected week (the next is due Monday, 2026-10-05).
- **MCP: ok.** `ap4509--alexandria-mcp-serve.modal.run/mcp` answers 401
  with a `WWW-Authenticate` header, up and correctly refusing an
  unauthenticated call.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone, per
charter §4; full `pending.md` reconciliation is ceremony-only, §1d, next
due 2026-10-05). Two items worth naming here rather than waiting for
Monday:

- **The Polar Merchant-of-Record account (ADR-30)** — due 2026-09-26,
  now **6 days overdue**. Still the single most launch-critical open
  item; checkout wiring cannot start without it. 11 days to 2026-10-13.
- **PR #60** (the pre-send quality checklist) — now **12 days open**,
  still the oldest open PR in the repository, nothing further owed from
  any seat, waiting only on the merge.

**Also worth naming: the merge backlog itself.** `gh pr list --state
open` shows 29 open pull requests. Most collapse into a handful of live
threads once the supersession chains are followed (engineer's #178
alone supersedes nine earlier PRs back to #141), but the live tip of
every active seat's chain is still open, several since 2026-09-30 (two
days): research (#162), skill (#159), frontend (#168), sales (#156),
finance (#164), exo (#160). Nothing in this file changes because of it,
since none of it is new evidence for a dispatch, but a count this size
is itself worth the owner's or chair's attention before it compounds.

## The company board

`board.libraryofalexandria.dev` answered this run (`BOARD_API_URL` and
`BOARD_RUNTIME_TOKEN` are present; the legacy `PROJECTS_TOKEN` /
GitHub-Projects path referenced in charter §4 point 5 is superseded by
this board per `docs/standards/pm.md` §14 and should be updated to say
so, which is the ExO's edit, not this seat's). Nothing addressed to
`pm` specifically. Two findings, not dispatchable, named for the
record:

- The board's own open sprint is still "Launch-ready newsletter,
  2026-09-21 to 2026-09-27," five days expired, not rolled forward to
  match `docs/sprints/sprint-2026-09-28.md`. No seat appears to be
  moving items on this board day to day.
- Commented on the backlog item named in Run health above with the two
  new failures. First attempt was refused: the board server itself now
  enforces the 2026-09-27 "no codes, describe it" ruling, rejecting a
  comment that named a PR by number. Worth recording as the artifact-
  side gate that ruling was missing — the board, not just this seat's
  own prose, now checks it. Rewritten in plain words and it posted.

## Linear trial

Not checked this run (no new signal). Still on trial per the 2026-09-19
ruling; no verdict recorded since.

## Dispatched by the PM

None this run. Every dispatchable seat was excluded by the open-PR hard
stop before any candidate reached the ceiling check.
