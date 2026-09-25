# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24, ~16:03 UTC (third PM pass this window, reconciles #97 and #99)

**What this run is.** Not a new standup read. `gh run list` and
`gh pr list --state open` at 16:03 UTC, six minutes after PR #99
opened, show no new run, no new PR, and no new decision beyond what
#97 and #99 already recorded. There is nothing new to propose. This
run's only contribution is fixing the thing #99 itself flagged as a
problem: two open PM PRs (#97, #99) each fully replacing this file
from the same base, leaving the owner to resolve the conflict by
hand. This branch merges both (#97 first, then #99, per #99's own
recommended order) and resolves docs/agents/incidents.md (both
branches' entries are additive, both kept) and this file (#99's
version kept in full, per #99's own note that it supersedes #97's
proposals) into one mergeable PR. **Recommend the owner close #97 and
#99 unmerged and merge this PR instead**, so there is one queue to
read rather than two to reconcile.

No new dispatch is proposed. Owner presence and the two
`workflow_dispatch` runs inside the last two hours (per #97's and
#99's own timestamps) still hold, and six quiet minutes since #99
does not change that.

## 2026-09-24, ~16:00 UTC (message-triggered standup, chair holding presence)

**Mid-run collision, disclosed plainly.** A scheduled `pm-agent` run
(36022688185) started 15:46:55Z, four minutes before this session
reached the point of opening its own PR, and produced **PR #97**,
covering the same standup ground (market's stub, PR #60's conflict,
run health). PR #97 has better evidence than this run could gather on
one point: it could read `PM_DISPATCH_ENABLED` (confirmed `true`) and
tried two real dispatches, both returning `HTTP 403`, logged as
`INC-2026-09-24-dispatch-403`. Trust that finding over anything this
run says about dispatch authority. Two more PRs landed in the same
window: **#98** (market, delivers the ranking brief PR #93's stub
promised) and **#95** (writer, supersedes #92, the canon-law-14/W39
rewrite chain's new head). #98 postdates #97, so #97 never read it —
this run did, and that is this run's one piece of non-duplicate value:
deciding from the finished brief, which the chair's handoff asked for
by name. Read this file's proposals as an addendum to #97's, not a
second copy of them; no new market or engineer dispatch is proposed
here for that reason.

### Decided from the market brief (PR #98, `docs/market/briefs/2026-09-24-b.md`)

The brief's own priority-ordered decision list, read and dispositioned:

1. **Land the enjoyability fix before the next issue ships dense.**
   Already in flight and already the owner's own ruling
   (`docs/voice/taste.md`, 2026-09-24 entries). Nothing to dispatch:
   PR #95 (writer, supersedes #92) is the fix, open, and the only
   action left is the merge, which is hers. Flagged with urgency below
   under owner-only decisions, not queued as a dispatch, because
   dispatching a seat with an open PR on the same chain is exactly the
   hard stop charter §5 already sets.
2. **Whether the claim graph belongs on the live pricing page before
   October 13.** The brief frames this as a PM-and-engineer call, not
   an owner one, but no existing ruling says which way to resolve it
   (ADR-26's two non-negotiables — a real domain, no coming-soon pages
   — bear on it without deciding it), and the relay rule in charter §4
   says a judgment not already made in a file does not get guessed at
   in a dispatch. Listed below as needing a decision rather than
   queued as work, and engineer already has two open PRs (#60, #94),
   so there is nowhere to send it today even once decided.
3. **No pricing change.** $20/month reconfirmed from a new angle
   (Ben's Bites' Pro tier). No action owed; recorded so it is not
   re-derived.

**Nothing queued to writer, frontend, or engineer this run.** Writer's
relevant work is already open (PR #95) and blocked only on merge.
Frontend has no open PR and no filed, ready task from this brief — the
claim-graph question is a decision, not yet a spec. Engineer has two
open PRs and the hard stop in charter §5 rules it out regardless.

## Owner-only decisions, one line each

- **Merge PR #95** (writer, supersedes #92): the enjoyability/canon-law-14
  fix and W39 rewrite the owner asked for directly last night.
- **Merge or close PR #98** (market): the finished ranking brief:
  closes out PR #93 (stub) once merged.
- **Rule on the claim graph vs. the live pricing page**: add it before
  October 13, or confirm it is deliberate post-launch scope and say so
  on the page. `docs/ideas.md` carries market's `proposed` entry for
  this (filed on PR #98's branch).
- **Rebase or retire PR #60** (engineer, `CONFLICTING`, sprint item 4):
  already flagged in PR #97's queue with the hand-run command; not
  repeated here to avoid a third copy of the same ask.

## Run health

**Fleet health.** No new failure class beyond what PR #97 already
logged (`INC-2026-09-24-dispatch-403`) and what this run adds
separately (`INC-2026-09-24-market-ranking-stub-only`, the market
run that reported success but shipped only its stub — since resolved
in substance by PR #98, the incident stands as a record of the
pattern, not as an open problem). Everything else in `gh run list
--limit 30` is `success`, including the two runs `in_progress` when
this session started (`pm-agent` 36022688185, now PR #97;
`engineer-agent` 36022750452, still running as of this writing, not
yet checked further since it is not this run's PR to review). One
direct-to-main commit landed after all three PM passes started
(504cc8d, "incidents: Kimi organization concurrency collision between
rehearsal and press") — a chair fix for `INC-2026-09-24-kimi-org-concurrency`
(below), not a workflow run, so it does not show in `gh run list`.

**Delivery health.**

- **The press.** No `DATABASE_URL` in this sandbox, so the `digests`
  table was not queried directly. `https://libraryofalexandria.dev/library`
  returns 200 and lists `2026-W39` as newest;
  `https://libraryofalexandria.dev/library/2026-W39` returns 200 with a
  real title, not a generic one. Consistent with the chair's report
  that W39 sent at 05:05Z, but this is the site, not the table.
- **The site.** Live, 200, serving current content.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  answers HTTP 404 on a bare GET rather than timing out — the process
  is up; GET `/` simply is not a route on a mounted MCP app. Not a
  protocol-level check.

## Pending items past their date

`docs/sprints/pending.md` gets a new dated section from this run (see
the top of that file) recording the decisions above, since the chair's
handoff asked directly for it: "write decisions into the sprint and
pending.md." Nothing else in the file is yet a day past its own date.

## Linear trial

Not checked this run. Still a trial per the 2026-09-19 ruling; no new
signal on adoption or abandonment.

## Dispatched by the PM

None this run. See PR #97 for the two dispatch attempts made this
window and their `HTTP 403` result.
