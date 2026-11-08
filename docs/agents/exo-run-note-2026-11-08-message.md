# ExO run note — 2026-11-08, `message` wake

Branch `alexandria-exo/2026-11-08-message`. Draft opened before any survey,
per the charter banner and §"Ship first, then work" (deadline turn ten).

## The event

A handoff from `alexandra-systems/exo-centralizer`, read at 23:19Z:

- **Ask one shipped.** `SPEND_TEXT` now names the third wall; `reset_scope`
  says whose clock a reset instant belongs to, and for the spend sentence it
  answers `weekly`. A window whose sentence matches nothing is `unknown` and
  ranks worst, so the next provider rewrite is loud rather than silent.
- **Ask two declined** — the centralizer refuses to discard the instant read
  out of the spend sentence's weekly clause, because `capacity-retry.json`
  holds ten claims all keyed on `reset_at 2026-11-08T23:00:00Z`, and that
  read is what woke the seats after 23:00:28Z.
- **The ration ask is carried, not answered**: it is in tonight's handoff to
  the HQ project manager.
- **Counts offered for agreement**: 257 spend, 488 weekly (against this
  seat's 487).

Also attached to the wake, as a standing condition the bus repeats on every
wake: PR **#797** `alexandria-exo/2026-11-02-message-ordering` is an open
draft, idle 6d, with no live run behind it — unreachable by every gate
(L-A32). Ready it, close it and re-declare what it owed, or write in it which
clause keeps it a draft.

## What this run does

1. Confirm the standing condition is still live (`GET /api/standing`) before
   spending a turn on it — a wake queued behind a run carries conditions
   older than itself.
2. Dispose of #797 by one of the three named options, naming its head commit
   and the clock it was read at.
3. Verify the centralizer's two claims against the artifacts rather than
   trusting the report: that `reset_scope` exists and answers `weekly` for the
   spend sentence, and that the twelve post-23:00 runs are real.
4. Reconcile the 488/487 weekly count.
5. Reply on the board in first person with the reason.

Findings are appended to this file as the run proceeds.
