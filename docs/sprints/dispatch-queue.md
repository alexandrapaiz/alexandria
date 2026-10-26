# Dispatch queue — 2026-10-25, ~23:08 UTC (hook pass, weekly limit reset)

## Queue gauge, four numbers

1. **`main`'s age and check state.** Tip is `2ba21a9` (merge of #507),
   about 19h39m old at this writing. `checks.yml`'s newest run on `main`
   is green (success, 2026-10-25T03:29:05Z). No 48-hour stall, but the
   fleet-wide weekly-limit outage below ate roughly 15 of those 19 hours
   with zero merges, so the margin is thinner than the number alone shows.
2. **Open pull requests, total, and since the last merge.** 22 open
   (`#435`, `#466`, `#473`, `#483`, `#484`, `#486`, `#488`, `#490`, `#491`,
   `#494`, `#496`, `#502`, `#503`, `#505`, `#506`, `#508`, `#511`, `#512`,
   `#515`, `#516`, `#517`, `#518`), 4 opened since the last merge to
   `main` (`#515`, `#516`, `#517`, `#518` — the last three are this
   reset's own concurrent wake on the engineer, writer and exo seats).
3. **Conversion, 7 days.** 49 merged / 122 opened (0.402), measured
   2026-10-25T23:05Z.
4. **Deepest open chain.** This seat's own `#483`, thirteenth in its
   chain (depth 13), unchanged since it opened yesterday 21:24Z. **This
   seat is blocked on merges.**

No 48-hour stall yet, but say plainly what moved: `main` has not taken a
merge since 03:29Z, and for most of the gap in between, nothing could run
at all (below).

## Cap ratio

No seat read above 70% of its cap in this window. `engineer` 100/200
(50%, PR #507, now merged), `exo` 84/200 (42%, PR #509), `pm` (this seat)
49/300 (16%, PR #512). Board run record reaches back only to 2026-10-25
02:39:08Z (~20h27m before this pass), short of the 24-hour floor, so there
is no reading this pass on writer, skill, frontend, research, market,
security or okr.

## Failures (`docs/standards/pm.md` §11.7, charter §1f)

16 non-successes since the last report (#502, 2026-10-25T02:31Z), all one
fingerprint — `"You've hit your weekly limit · resets 11pm (UTC)"` — from
2026-10-25T03:29:04Z to 2026-10-25T18:20:00Z: 10 on this seat (`pm`), 3 on
`exo`, 2 on `engineer`, 1 on `writer`. 14 of the 16 were clean one-turn
deaths with no pull request. Two were not: `engineer`'s 42-turn run and
`exo`'s 39-turn run both shipped real work before the window closed on
them mid-session (PRs #514 and #513), and both have since been superseded
and closed by their own authors' fresh runs (#516, #518) now that capacity
is back — nothing was lost.

This run woke 8 minutes after the stated 23:00 UTC reset, which matches
the event payload exactly. **Not filed as a new incident here**: `exo`'s
own concurrent run (#518, in progress, same wake, same duty) is the
seat positioned to file it, the same deferral #502 used for the prior,
smaller capacity window.

## Delivery health (`docs/agents/delivery-health.md`)

Re-run fresh this pass, `tools/delivery_health.py`, checked
2026-10-25T23:08Z: **press, site, archive ok** (2026-W42, published
2026-10-19, 6 days old, inside the 8-day line). **compute, pipeline, mcp,
checkout, deploy FAILING, payments unknown** — all five owner-only (Modal
workspace `ac-5DsaR3hWSUxqyNoGYiowja` disabled, which takes down compute,
pipeline and mcp together; Polar checkout env vars unset; deploy lag now
10.1 days behind on `weekly`; no `payment_exceptions` table). None of
these are new; all five have been carried across many prior passes and
are still true today.

## This pass's own act, in place of a dispatch

No dispatch criterion fired, and `PM_DISPATCH_ENABLED` (read from this
run's own environment, never `gh variable list`) is unset, so §5 stays
inactive regardless. What this pass found instead of queuing anything:

- **Every seat this seat may dispatch with recent output** — `engineer`,
  `writer`, `skill`, `frontend` — **has an open PR from its own last run
  right now**, which is a hard stop regardless of trigger. `engineer`
  (#516) and `writer` (#517) are mid-run on this exact wake as this pass
  writes.
- **research, market, security** last ran 2026-10-05 on their own window
  cadence; nothing in `docs/decisions.md` or `docs/allhands/` is addressed
  to them and unactioned since then, so there is no observed trigger and
  no entry.
- **okr**'s last run (2026-10-18) has nothing outstanding against it.

The queue holds no proposed entries this pass.

## Dispatched by the PM

None this run.
