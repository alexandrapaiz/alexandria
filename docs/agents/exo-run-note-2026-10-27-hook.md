# ExO run note — 2026-10-27, hook wake (capacity returned)

**Trigger.** A capacity-return hook. The wake text says the provider limit
that refused the previous run has reset, that nothing else would have woken
this seat before its next scheduled window, and — the part no later run could
have recovered — that **the run before the refused one, at 2026-10-26T21:12:12Z,
was cut off at turn 60 and nothing has completed for this seat since**. So
there are two unfinished things in front of this run rather than one: the
cut-off run's work, and this run's own.

The wake names no re-fired cron slot, so by §0 it is a hook and therefore a
wake run — **unless the owed-cycle detector outranks the trigger**. That
command is run before anything else and its verdict is recorded here.

**Continuation, not a restart.** This branch is cut from
`alexandria-exo/2026-10-26-message-withdrawn-wake` (PR #618), which carries the
cut-off run's two commits: its stub and one incidents entry. Supersedes #618
(depth 8). This seat is blocked on merges.

Observations and decisions are appended to this note as the run proceeds.
