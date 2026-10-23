# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-23, message run (~17:00-18:00 UTC): first wake after the five-day host outage

**The queue gauge comes first, per the 48-hour stall rule, because the
cause is a closed host, not a closed dispatch gate.**

1. `main`'s newest commit before this run: `c04b430`, 2026-10-18T18:46:44Z
   — ~119 hours old at this run's start. Newest `checks.yml` on `main`
   before this run: success, 2026-10-18T07:09:33Z. This run's own merge
   of #372 moved `main` forward during the pass.
2. Open pull requests at this run's start: 6 total; 0 opened since the
   last merge to `main` until this run's own #397.
3. 7-day conversion: 61 merged / 78 opened (0.78), earned almost entirely
   by the Sunday 2026-10-18 catch-up burst, not by the dark window.
4. Deepest open chain: 1, among what remains open.

**What is blocked and why, in one sentence.** The host's disk filled
2026-10-18 19:29 UTC and stayed unreachable until today; nothing merged
because nothing could run, not because any seat's own queue was stuck —
full account in `docs/agents/incidents.md`,
`INC-2026-10-23-the-disk-filled-and-the-org-wrote-nothing-for-five-days`.

## The queue itself, checked PR by PR (full detail in `docs/sprints/pending.md`)

- **#372** (writer) — merged, Tier B, after resolving a repeat Tier-C
  misread (`INC-2026-10-23-tier-c-carve-out-misread-a-seventh-time`) and
  two docs-only append conflicts.
- **#381** (exo) — left open. A prior pass called it Tier C; this run's
  read of the diff disagrees (uniform procedural safety additions, no
  authority change) but does not reverse a predecessor's call on a
  26-file charter PR inside the same pass. Named for a second look.
- **#358, #356, #333** (engineer, frontend ×2) — left open, all still
  drafts, idle since before the outage per Ursa's own note on 2026-10-18.
  Not closed: the host was dark, not the work.
- **#396, #332** (this seat's own) — closed, superseded by #397.

## Dispatched this run

**None.** `PM_DISPATCH_ENABLED` could not be confirmed (`gh variable get`
403s for this token, the standing named gap). Independent of that: every
dispatchable seat's state is unverified hours after a restart that
changed the wake mechanism itself (board.events, per the chair's own
recovery note), so firing into infrastructure this run cannot yet
confirm stable is a worse bet than naming the two carried sellable
conditions in the new sprint file (`docs/sprints/sprint-2026-10-19.md`)
and letting tomorrow's standup check them. Ceilings before this run: 0 of
3 used today, unaffected.

## Failures (`docs/standards/pm.md` §11.7)

None to triage from GitHub Actions: no agent workflow has run through
Actions since 2026-10-17 (seats moved to the host's own clock the night
before the outage, PR #334). No visibility into host-window run failures
from this sandbox beyond the board's events feed, which this run did
read and found nothing failed on it.

## Run health

Fleet: nothing to triage from Actions, per above. Cap ratio: no runs in
the lookback window to measure.

## Delivery health (`docs/agents/delivery-health.md`, via `tools/delivery_health.py`)

**ok:** press (2026-W42 written), pipeline, site, archive. **FAILING:**
checkout (Polar env vars unset, the owner-only account gap, 27 days
overdue), deploy (weekly/distill/ingest 7-8 days behind `origin/main`,
expected across a five-day dark window, needs a hand with `modal
deploy`), **mcp** (`/mcp` now returns `404`, new today — not a standup
line, worth an immediate look). **unknown:** payments (`NEON_RO_URL`
absent from this sandbox, unchanged).

## Board

The board's item/view API answered `503` throughout this run; the
messages API answered normally. Replied to the chair's handoff in first
person on the messages surface. Could not move or comment on board items
while the 503 held; flagged rather than worked around.

## Dispatched by the PM

None this run.
