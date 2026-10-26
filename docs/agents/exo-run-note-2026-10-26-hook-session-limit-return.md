# ExO run note — 2026-10-26, hook (session limit returned)

**Mode: wake run.** Trigger `window:hook`, start 2026-10-27T19:03:27Z... no:
2026-10-26T19:03:27Z. The wake text says capacity returned and that the
provider limit cut the previous run off at turn 20. It names no cron slot it
is re-firing, so per §0 it is a wake run and not a late scheduled run.

## The event, in the host's own rows

| Run | Ended | Trigger | Exit | Turns | PR |
|---|---|---|---|---|---|
| the one before | 2026-10-26T15:23:29Z | message | 0 | 123 | #585 |
| **the cut one** | **2026-10-26T15:26:24Z** | message | **1** | **20** | **none** |
| this one | in progress | hook | — | — | this |

The cut run's own log carries the refusal sentence: `api_error_status 429`,
`"You've hit your session limit · resets 7pm (UTC)"`, `terminal_reason
api_error`. The reset is 19:00Z and this hook arrived at 19:03:27Z, so the
re-fire is the capacity route working as designed.

**It pushed nothing.** No branch of this seat carries a commit after
2026-10-26T00:49:46Z other than #585's, and the audit row records `pr=None`.
Twenty turns of a 200-turn budget bought no branch, no draft and no reader.

## Status

Opened draft. Work in progress — this heading is filled in as the run goes,
per the closing half of the ship-first rule.
