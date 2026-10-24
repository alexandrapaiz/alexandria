# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~01:30-01:40 UTC)

**Trigger.** Two board/message events, both confirmations rather than new
asks: "your pull request merged: PR #419 checked against the merge rule,
Tier B, merged (`#423`)" and "your pull request merged: PR #420 checked
against the merge rule, Tier B, merged (`#425`)." Both say to continue
with the next item in this seat's lane and name what was taken.

**Nothing dispatched this run, and the queue holds none.** `PM_DISPATCH_ENABLED`
read directly from this run's own environment: still empty, not `true`,
unchanged from the last pass. Checked the rest of the criteria anyway.

Every dispatchable seat but one either has an open draft pull request from
its own last run right now (`engineer` on `#426`, `writer` on `#424`,
`frontend` on `#421`, all three still drafts) or has no evidenced trigger
this pass can cite without inventing one (`market`, `skill`, `security`,
`okr`, `research`, unchanged from the last pass's read). `exo` is never
dispatchable (it audits this seat).

## What was taken: confirmed both merges landed, found nothing new to merge, closed out the depth-4 chain

**#423 and #425, both this seat's own prior passes, confirmed on `main`.**
`git log --oneline origin/main` shows both merge commits: `#420` at
`6baf03d` (via `#425`, merged 01:29:08Z) and `#419` at `507099e` (via
`#423`, merged 01:19:31Z). No re-verification needed beyond the commit
log; both passes already ran the suite and the merge-rule checks
themselves.

**No new Tier B merge available.** The three other open pull requests are
all drafts (`#421`, `#424`, `#426`), so condition 2 of §10 holds every
one of them back regardless of their diffs. `#414` is unchanged: still
open, still the same unresolved question this seat already put to the
owner in `pending.md` (whether a routine, non-authority charter fix
counts as the "except a change to a seat's own authority" carve-out, or
as the standard's separately-enumerated owner-only "Charters (`prompts/`)"
category). No new fact arrived to answer it, so it stays held rather than
re-litigated.

**This seat's own `#403` absorbed here rather than left to grow a sixth
link.** `#403` was still open, still carrying unique commits (`c96f5dc`
back to the sprint-2026-10-19 close), and it writes into the same
`pending.md`/`dispatch-queue.md` anchor this pass needed to write into.
Built on it: merged `origin/main` into `#403`'s branch, resolved four
docs-only conflicts (two append-only ledgers, kept both sides in full;
`pending.md`, kept both in full with `main`'s newer entries on top,
matching the file's newest-first convention; `dispatch-queue.md`, took
`main`'s version whole, since that file is replaced in full each run
rather than appended to). `git log --oneline
origin/alexandria-pm/2026-10-23-message-pr402-merge ^HEAD` printed
nothing, confirming containment. `#403` closed as superseded by this
pull request. **Chain: `#397` to `#399` to `#401` to `#403` to this one,
depth 5.**

**This seat is blocked on merges.** At depth 5 this diff carries five
runs of `pending.md`/`dispatch-queue.md` work for one run of review,
which is slower to review, which deepens the chain again. The real fix
(splitting `pending.md` by writer, per `#414`) is itself one of the
things held above, which makes this a knot: the fix for the stacking
problem is stuck in the same queue the stacking problem is stuck in.

**Board walked for an orphaned item; none found.** `d69a5c1a` (pm lane,
the home-page quality-claims row) stays in Backlog, not Done: the actual
fix is bundled inside `#414` and is not on `main` yet, same reasoning the
pm's own comment on `#414`'s board card already gives for leaving that
card in Review. No other pm-lane card changed state. No new comment
needed on any board item this pass, since nothing changed since the last
one.

## Held, not resolved — the conflict is in code, not prose

Unchanged: `#416` was itself superseded and closed by the frontend seat's
own `#421`. No action needed from this seat.

## Failures (`docs/standards/pm.md` §11.7)

No new non-successes since the last pass's read (checked the board's run
list: the newest entries since then are three more `pm` passes and one
`engineer` pass, all exit 0). The two already-registered failures
(`exo` and `pm`, both 2026-10-23T19:0x UTC) are unchanged, still drafted
inside the unmerged `#414`.

## Run health

Fleet: unchanged since the last pass, ten minutes ago. Cap ratio: not
recomputed this pass; no new run to measure since the last reading.

## Delivery health

Not recomputed this pass. Unchanged since the last reading ten minutes
ago: press, site, archive ok; compute/pipeline/mcp, checkout, and deploy
still failing on the same three owner-only blockers; payments unknown.

## Queue gauge, four numbers

1. `main`'s newest commit: the merge of `#425`, 2026-10-24T01:29:08Z,
   about eight minutes old at this writing. `checks.yml` fires only on
   specific paths; its newest matching run on `main` is still `success`
   from 2026-10-23T23:31:12Z, unchanged, because nothing since has touched
   one of those paths.
2. Open pull requests: 5 (`#414`, `#421`, `#424`, `#426`, this seat's own),
   1 opened since the last merge to `main` (this seat's own).
3. 7-day conversion: 77 merged / 104 opened (0.74).
4. Deepest open chain: 6 (`#414`), unchanged. This seat's own is next at 5.

No 48-hour stall; `main` moved eight minutes ago.

## Board

No new comment posted. Walked the board; nothing changed that needed one
(see above).

## Dispatched by the PM

None this run.
