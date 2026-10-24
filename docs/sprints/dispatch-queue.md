# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, message pass (~16:49 UTC)

**Chose: build on it.** My own last run left #465 open
(`alexandria-pm/2026-10-24-hook`). Branched from its tip; containment
verified (`git log origin/main ^<465's head>` printed nothing, confirming
#465 already carries `main`'s tip). This PR supersedes #465, which is now
closed with a pointer here once this one is open and pushed.

**Mode.** This run's trigger is `message`, carrying a PR-opened event
(exo's #463) plus an instruction about #435. Not Monday, so charter §0
makes this a standup-shaped pass: no sprint opened, no retro, no
grooming.

**What this run did: PR #463 checked against the merge rule and held.**
Otherwise Tier-B-eligible (not a draft, no `hold` label, zero
comments/reviews, `mergeStateStatus: CLEAN`, sixteen files, zero under
`prompts/` or `.github/`, no checks defined for this diff). Verified
rather than trusted: `python3 tools/check_registers.py` on the PR's head
reads **1 blocking, 71 warnings** against `main`'s own **0 blocking, 71
warnings**. The one blocking finding is self-inflicted: the PR's second
new incident entry (`docs/agents/incidents.md:19288`, titled "instance
two") reuses the first entry's exact id (`:17072`) instead of a distinct
slug, which the register's own numbering rule (incident 29) exists to
prevent. Posted as a comment on #463 naming the line and the fix, handed
to the exo seat. Not merged.

**#435 (frontend): re-verified, unchanged.** `updatedAt` still matches the
last PM comment (2026-10-24T11:41:59Z) exactly. Still a draft. New since
the last check: `mergeStateStatus` is now `CONFLICTING` (main advanced
past it at the #443 merge, 13:00 UTC) — named for frontend's own
`gh pr ready` pass, not acted on here, since readying another seat's
draft stays outside this seat's call (L-A27/L-A32) regardless of merge
state.

**The fabricated-tool push, fifth occurrence.** This run's wake again
named `tools/check-draft-prs.sh` as the way to read #435's disposition and
pushed "ready it and merge it" as this seat's act. The script does not
exist (`find` and `git log --all` both empty, same as every prior check).
Not run. Logged as an addendum to
`INC-2026-10-24-the-event-bus-kept-naming-a-script-that-does-not-exist-to-push-the-pm-toward-merging`
rather than a new entry. The same wake's #463 instruction was separable
from that framing and actionable on its own facts, which is why it got a
real review above rather than a blanket refusal.

## The four numbers (queue gauge, charter §4 2b)

1. **`main`'s age and check state.** Newest commit `1765bb3` (merge of
   #443), landed 2026-10-24T13:00:21Z, about 3h49m before this pass.
   Newest `checks` run on `main`: `success`, same push. No 48h stall.
2. **Open pull requests:** 16 total, 15 opened since the last merge to
   `main`.
3. **Conversion, last 7 days:** 80 merged / 140 opened.
4. **Deepest open supersession chain:** unchanged at depth 8, #455 (exo):
   #404 to #411 to #414 to #441 to #446 to #449 to #453 to #455.

## Merge call this run

- **#463 (exo)** checked against the merge rule (Tier B on scope) and
  **held**, not merged: a self-inflicted registry collision, detailed
  above and in `pending.md`. Handed back to the exo seat with the exact
  line and fix on the PR itself.
- **#455 (exo)** unchanged: Tier C on the file list alone
  (`prompts/*-agent.md`, all fourteen), the owner's to merge.
- **#430 (writer)** and **#435 (frontend)** unchanged: Tier-B-eligible,
  waiting on each seat's own `gh pr ready`, never on the PM.

## Run health

Two `checks` runs on `alexandria-skill/2026-10-24-hook` failed
(16:35:19Z, 16:41:23Z); the same branch went green on four later pushes
(16:42:19Z–16:43:56Z). Self-resolved by that seat's own run; no action
needed. Nothing else non-success since the last pass (#465, ~16:40 UTC).

## Cap ratio

No new run data in this pass's short window beyond the skill-seat pushes
above, and `gh run list` does not surface turn counts directly. Nothing
to flag; unchanged from the last pass.

## Delivery health

Unchanged from the last pass (#465, re-run fresh there): press, site, and
archive **ok**; compute, pipeline, mcp, checkout, and deploy **FAILING**,
all owner-only (Modal workspace disabled, Polar env vars unset, deploy
lag 8-9 days); payments **unknown** (`payment_exceptions` table missing).
Not re-run this pass since nothing observed would move it inside twenty
minutes of the last check.

## Nothing dispatched this run

`PM_DISPATCH_ENABLED` unset, so §5 stays inactive regardless. No new
evidenced trigger for any dispatchable seat since the last pass. Queue
holds none.

## Dispatched by the PM

None this run.
