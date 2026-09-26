# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log. (Note: the last few
2026-09-24 passes drifted into appending dated sections instead of
replacing the file; this run restores the charter's literal rule. That
history is not lost — it is in git and in PR #100 — it just no longer
lives in this file.)

## 2026-09-25 (Friday standup)

**Nothing to propose. The queue is empty on purpose, not by omission.**

- **engineer, writer, and market are all disqualified by charter §4's
  hard rule**, "never propose a dispatch for a seat whose last pull
  request is still open" (promoted to a hard stop under §5's dispatch
  authority): engineer has #60, #94, #96, #102 open; writer has #101
  open; market has #93 (draft) and #98 open.
- **The five other dispatchable seats (research, frontend, skill,
  security, okr) have no due cadence today and no fresh, evidenced
  trigger.** Checked the newest research brief (2026-09-24) and market
  brief (2026-09-24) for anything pointing at one of them: research's
  brief names the triage interleaving fix as the one thing that would
  unblock its next curation decision, but that fix is `pipeline/triage.py`
  (already committed 2026-09-19) awaiting a `modal deploy`, which is a
  chair/owner action, not a seat to dispatch. Nothing else in either
  brief, in `docs/decisions.md`'s newest entries (ADR-32/33/34), or in
  `docs/sprints/pending.md` names a task for research, frontend, skill,
  security, or okr that is both ready and undone.
- **One piece of good news worth surfacing rather than sitting silent
  in pending.md:** sprint-2026-09-21 item 1, the MCP OAuth redirect-URI
  validation gap (blocking, due before Stripe launch 2026-09-26),
  is shipped. Verified directly against `mcp/oauth_flow.py`: `/register`
  now validates and stores `redirect_uris` (`normalize_redirect_uris`,
  `issue_client_id`), and `/authorize` and `/token` reject any
  `redirect_uri` that does not match what was registered
  (`check_redirect_uri`), with `tests/test_oauth_redirect_uri.py` in the
  tree. Tomorrow's deadline is not at risk from this item.

## Run health

**Fleet health.** All green since PR #100's last check (2026-09-24
16:09 UTC). `gh run list` for everything created after that shows two
completed runs, both `schedule`, both `success` (writer-agent
2026-09-24T19:34:00Z, engineer-agent 2026-09-25T01:23:23Z), plus this
window's three in-progress scheduled runs (market, pm, engineer,
2026-09-25 ~15:45-47 UTC). No new failure class. The one non-success in
the last 30 runs overall (`writer-agent` 35958638663, cancelled) is
already registered as
`INC-2026-09-24-writer-dispatch-started-twice`, no new entry needed.

**Delivery health.**

- **The press.** No database credentials in this sandbox, so the
  `digests` table itself was not queried. `https://libraryofalexandria.dev/library`
  returns 200 and lists `2026-W39` as the newest issue, consistent with
  the last confirmed state (no digests DB access; site checked instead,
  same limitation PR #100 noted). No new weekly issue is expected before
  Monday 2026-09-28 09:00 UTC, so this is not a staleness finding.
- **The site.** `https://libraryofalexandria.dev/` returns 200, serving
  current content.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  answers HTTP 404 on a bare GET rather than timing out or refusing the
  connection — the process is up. Not a protocol-level check (no route
  exists at `/`, so this only confirms the container is alive).

## Pending items past their date

Checked every dated obligation in `docs/sprints/pending.md`
("due 2026-09-26" for the Polar account, "due 2026-09-27" for the
sprint-2026-09-21 milestone, "due mid-November" for the PR-merge token
scope). None have passed their date as of today, 2026-09-25. The Polar
deadline is tomorrow; worth the owner's eye, not yet a lapsed item.

## Linear trial

Not checked this run (no new signal to report). Still on trial per the
2026-09-19 ruling; no verdict yet.

## Dispatched by the PM

None this run. No qualifying trigger existed for any seat that charter
§5 permits this seat to dispatch (see above); firing one without a
trigger would violate §4's relay rule regardless of whether
`PM_DISPATCH_ENABLED` is `true`. Note for whoever next attempts a real
dispatch: `INC-2026-09-24-dispatch-403` recorded that the PM's own
`gh workflow run` calls 403'd yesterday despite every documented
condition being met, and no follow-up in this file or in
`docs/decisions.md` shows that resolved. Untested again this run since
there was nothing to test it with.
