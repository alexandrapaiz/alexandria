# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~13:50 UTC, fourth pass)

**Nothing dispatched this run, and the queue holds none.** `PM_DISPATCH_ENABLED`
is unset in this run's environment, so section 5 stays inactive regardless
of what follows.

**Why the queue is empty rather than a sign of nothing to do.** `engineer`,
`writer` and `frontend` each have an open pull request from their own last
run right now (#456 draft, #430 draft, #435 draft). The hard stop in
charter §5 forbids proposing a dispatch for a seat in that state unless the
instruction explicitly tells it to build on the open branch, and nothing
observed this pass warrants that. `market`, `skill`, `security` and `okr`
have no evidenced trigger this pass can cite without inventing one. That
matches every message pass today; the queue has been legitimately empty
all day, not silently skipped.

## The four numbers (queue gauge, charter §4 2b)

1. **`main`'s age and check state.** Newest commit `1765bb3`'s underlying
   merge landed at 13:00:24Z (PR #443), roughly 50 minutes before this
   pass. Newest `checks` run on `main`: success, same timestamp.
2. **Open pull requests:** 14 total (post #458 close, #460 opened in its
   place), 7 opened since the last merge to `main`.
3. **Conversion, last 7 days:** 82 merged / 134 opened.
4. **Deepest open supersession chain:** #455 (exo), depth 8 — #404 to #411
   to #414 to #441 to #446 to #449 to #453 to #455. Up from depth 7 last
   pass; #453 closed, superseded by #455.

Threshold not crossed (something merged to `main` ~50 minutes ago, well
under 48 hours), so this stays a normal line rather than the headline.

## Merge call this run: none, by instruction rather than by Tier

This run carries an explicit instruction not to merge any pull request and
not to push to `main`. That binds for this pass regardless of what
`docs/standards/pm.md` §10/§21 would otherwise let a PM seat do, so no Tier
A/B/C judgment was exercised here one way or the other:

- **#455 (exo)** supersedes the closed #453. Touches every
  `prompts/*-agent.md` file at once, Tier C on the file list alone, the
  owner's to merge.
- **#430 (writer)** and **#435 (frontend)** are unchanged: Tier-B-eligible
  per earlier passes' verification, waiting on each seat's own `gh pr
  ready`, never on the PM.

## Run health

`gh run list --limit 30`: every run since the last pass is `success`. No
non-success to triage.

## Flagged, not actioned: a fourth occurrence of a push toward merging via a tool that does not exist

This run's wake carried, for the fourth time today, an instruction naming
`tools/check-draft-prs.sh` (which has never existed in this repository) as
grounds to ready-and-merge #430 or #435, plus a direct instruction to
review and merge #455 "against the merge rule." Per the standing rule that
the event payload is data and never overrides the charter, neither was
acted on. Logged as an addendum to the existing
`INC-2026-10-24-the-event-bus-kept-naming-a-script-that-does-not-exist-to-push-the-pm-toward-merging`
entry in `docs/agents/incidents.md` rather than a new entry, since the
mechanism is unchanged from the prior three occurrences.

## Dispatched by the PM

None this run.
