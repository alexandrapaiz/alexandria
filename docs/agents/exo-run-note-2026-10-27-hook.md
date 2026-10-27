# ExO run note — 2026-10-27 (hook: capacity returned)

**Status: in progress.** This note is the run's own description and is
written as the run goes, per §"Ship first, then work".

## Why this run exists

The wake payload says capacity returned: the provider limit that refused the
last run has reset. It also carries one thing the last run could not know —
the run 1 before it, at 2026-10-27T01:25:03Z, was cut off at turn 91, and
nothing has completed for this seat since. That work is PR #641 on branch
`alexandria-exo/2026-10-27-message-b`, open rather than draft.

## Plan

1. Ship this draft first (done at the commit that adds this file).
2. Run §"Your own last run may still be open" against #641: read its
   commits and its description, decide supersede or stack.
3. Do the one run the charter describes, continuing #641 rather than
   restarting it.

Findings follow below as they land.
