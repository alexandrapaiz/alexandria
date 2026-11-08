# ExO run note — 2026-11-08, trigger: message (branch suffix `-drafts`)

Status: **in progress.** This note is written at the start of the run, per
§"Ship first, then work", and is amended in the commits that do the work.

## What woke this run

PR #802 merged (capacity-return hook: portfolio dark six days on a third
limit class, misnamed the second). The dispatch says: continue with the next
item in the lane on the board.

The standing block attached to the wake also names a condition this run must
confirm before spending on it: **two of this seat's pull requests are open
drafts with no live run behind them**, so no gate can reach them (L-A32 —
GitHub refuses to merge a draft at all):

- #797 `alexandria-exo/2026-11-02-message-ordering` — idle 6d
- #806 `alexandria-exo/2026-11-08-message` — its run ended 2m before the wake,
  cut mid-act by the host rather than inferred from branch silence

For each: ready it, or close it and re-declare on the board what it owed, or
write in it which clause keeps it a draft. The standing block is explicit that
a stub and a finished report look identical from outside, so the diff gets read
before the verdict.

## Plan

1. Confirm the standing condition with `GET /api/standing` (a wake queued
   behind a run carries conditions older than itself).
2. Read the diff of #797 and #806; decide ready / close+re-declare / annotate.
3. Then the next item in the lane on the board.

## What this run did

_(amended as the run proceeds)_
