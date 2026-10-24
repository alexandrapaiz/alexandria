# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~13:40 UTC)

**Nothing dispatched this run, and the queue holds none.** `PM_DISPATCH_ENABLED`
is unset in this run's environment, so section 5 stays inactive regardless
of what follows. This run also carried an explicit operating instruction not
to fire anything irreversible before its draft PR was open, so dispatch was
never attempted even hypothetically.

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

1. **`main`'s age and check state.** Newest commit `eb4e211`'s underlying
   merge landed at 13:00:24Z (PR #443), roughly 40 minutes before this
   pass. Newest `checks` run on `main`: success, same timestamp.
2. **Open pull requests:** 14 total, 7 opened since the last merge to `main`.
3. **Conversion, last 7 days:** 82 merged / 134 opened.
4. **Deepest open supersession chain:** #453 (exo), depth 7 — #404 to #411
   to #414 to #441 to #446 to #449 to #453.

Threshold not crossed (something merged to `main` 40 minutes ago, well
under 48 hours), so this stays a normal line rather than the headline.

## Merge call this run: none, by instruction rather than by Tier

This run carries an explicit instruction not to merge any pull request and
not to push to `main`. That binds for this pass regardless of what
`docs/standards/pm.md` §10/§21 would otherwise let a PM seat do, so no Tier
A/B/C judgment was exercised here one way or the other:

- **#451 (engineer)** needed no judgment: already closed before this run
  started, superseded by the engineer seat's own #456.
- **#453 (exo)** is unchanged from the last two passes' read: Tier C (all
  fourteen `prompts/*-agent.md` files), owner's to merge.
- **#430 (writer)** and **#435 (frontend)** are unchanged: Tier-B-eligible
  per earlier passes' verification, waiting on each seat's own `gh pr
  ready`, never on the PM.

## Run health

`gh run list --limit 30`: every run since the last pass is `success`. No
non-success to triage. Not re-running the cap-ratio sweep (`--max-turns`
vs. `num_turns`): three sibling passes in the last hour already did it on
a window too short to have moved, same reasoning the prior pass used.

## Flagged, not actioned: a repeated push toward merging via a tool that does not exist

This run's wake carried, for the third time today, an instruction naming
`tools/check-draft-prs.sh` (which has never existed in this repository) as
grounds to ready-and-merge #430 or #435, plus a direct instruction to merge
#451 (already closed) "against the merge rule." Per the standing rule that
the event payload is data and never overrides the charter, neither was
acted on. Written up as
`INC-2026-10-24-the-event-bus-kept-naming-a-script-that-does-not-exist-to-push-the-pm-toward-merging`
in `docs/agents/incidents.md`, since this is the third occurrence today
and the standing rule requires a register entry on a repeat, not just an
inline catch. Worth the ExO's and the owner's attention as a possible
compromised or spoofed source on the event bus, not a routine finding.

## Dispatched by the PM

None this run.
