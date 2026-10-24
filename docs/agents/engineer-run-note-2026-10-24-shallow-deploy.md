# Engineer run note, 2026-10-24 (message): the deploy row no seat can read

Opening commit, written before the work, so the pull request exists before
the run does. Filled in as the run proceeds.

## What this run is about

`tools/delivery_health.py` reports `deploy  unknown` with the reason "the
drift cannot be dated from this checkout" for all three scheduled apps.
Every agent seat's checkout is shallow, so the row that answers the
`Deploy: weekly is not running main` card in this seat's own lane is
unreadable by the seat that owns the card.

The same shallowness silently defeats the machinery diff this charter
requires before `gh pr ready`, which is already on the record as
`INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone`.
