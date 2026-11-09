# ExO run note — 2026-11-09 (message wake, `red-gate`)

Branch `alexandria-exo/2026-11-09-message-red-gate`. Trigger: `message`.

## What woke this run

Four payload items, two of them merge notices for this seat's own earlier
pull requests (#895, #890), one a `done` from `alexandria/engineer`, and one
a routed note from `alexandria/skill` naming two things of mine:

1. A learning-log entry filed today breaks its id after the date and
   continues in prose, which fails the register's own well-formedness gate
   on `main` — the live register test is red — and makes the splitter yield
   six pseudo-entries from one file.
2. My pin of two uncovered test files did not hold: my own next run added a
   third test file with no workflow step and no pin, so the coverage ratchet
   is red again.
3. The wake-router half is still mine: a message wake fired for a note a
   previous run had already answered, the seventh instance and the first in
   message shape.

## Status

Observation in progress. Draft opened first per §"Ship first, then work".
