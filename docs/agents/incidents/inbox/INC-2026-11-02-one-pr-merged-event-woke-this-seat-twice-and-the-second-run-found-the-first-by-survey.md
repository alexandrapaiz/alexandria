## INC-2026-11-02-one-pr-merged-event-woke-this-seat-twice-and-the-second-run-found-the-first-by-survey - the fourth sighting of the one-event-two-runs class, and the first where the survey ran early enough to be cheap (2026-11-02, exo seat)

**What happened.** The merge of #652 woke this seat twice. The first run opened
**#663** at 2026-11-01T23:27:52Z; this run was woken by the same event, with the
same instruction ("continue with the next item in your lane on the board"), and
opened **#667** at 23:50:48Z — 23 minutes later. Neither payload gave any sign
the other existed. The PM seat logged a duplicate wake of its own for #652 in
the same hour (#666), so the event fanned out to at least two seats twice.

`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
is the standing finding and it is still correct. What is new is the cost.

**The reordering paid off, and this is the measurement it was owed.** The
2026-10-26 grant moved §"Your own last run may still be open" to run *after* the
draft is pushed rather than before it. Under the old order this run would have
spent its first turns on the survey and found #663 before branching. Under the
new order it branched, pushed and opened #667 at **turn 4**, then ran the survey
at turn 5 and found #663 immediately. The predicted cost of the reordering was
"one extra merge on the runs where the survey turns something up." The actual
cost here was **one extra branch and one renamed file**: #663 and this run both
created `docs/agents/exo-run-note-2026-11-01-message.md`, caught because
`tools/anchor_contention.py` listed that path at two open pull requests, and
renamed to `-lane`. That is the cheap half of the trade arriving exactly as
argued.

**What the second run did with the first, which is the part worth copying.**
#663 was read rather than trusted. Its claims were verified live: #652 merged at
23:34:41Z (confirmed), and the per-pass pending convention still in use at
23:39Z (confirmed). Then its own handoff list was taken as the lane's next work
rather than redone. Item 1 of that list was "**does #657 ship?** The run was
still going when this one ended — read it, do not assume it." It did not ship:
the re-fire exited **124** at 23:04:44Z and left #657 a draft. Chasing that
answer is what turned up the two defects in `tools/cron_firing.py` that this
run fixed.

> A duplicate wake is only waste if the second run repeats the first. #663 left
> a list of four things it could not finish, and the second run's cheapest
> possible contribution was the first item on it.

**What is still owed.** The payload carries no "already answered" signal and
nothing here can add one; that ask belongs upward and
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
already carries it. The sentence this entry adds is about the receiving end: a
seat whose previous run left an explicit handoff list converts a duplicate wake
into a continuation, and a seat that does not leave one cannot.
