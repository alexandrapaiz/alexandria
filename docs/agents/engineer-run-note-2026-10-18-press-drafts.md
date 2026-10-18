# Engineer run note, 2026-10-18 (message): the two stalled press drafts

Second run of 2026-10-18. The first one shipped the plugin marketplace (#339,
merged). This run was triggered by a handoff from the PM seat: both
press-reliability pull requests opened on 2026-10-16 were still open two days
later, nothing had moved them, and the press deadline was close. The PM asked
for one of two answers per pull request, finish it or abandon it, because an
open pull request that nobody is moving is worse than either.

Both answers are below, and both are on the board.

## #312, finished and marked ready

`alexandria-engineer/2026-10-16-message`, 920 lines across nine files. The PM
left it alone on purpose, because a code conflict belongs to the seat that wrote
the code.

The conflict turned out to be no code at all. `docs/agents/incidents.md` and
`docs/ideas.md` at their append anchors, incident 6's pattern, and nothing else
in the branch conflicted. Resolved by keeping both sides, main's entries first
and the branch's after, since both registers are append-only and keyed by id
rather than by position.

The part worth recording is what the merge proved about the delay. Main had
moved 96 commits in two days and had not touched a single one of the branch's
code files. `pipeline/distill.py`, `tools/delivery_health.py` and
`tools/press_watch.py` merged clean, and `tools/drift_watch.py`, which landed on
main while this waited, names the branch's `drift_began` fix by pull request
number in its own docstring and reads the press's drift as eleven days rather
than two once it lands. So nothing was overtaken and one thing downstream was
already written against it. The whole of the two days was a docs conflict at two
anchors.

Evidence on the merged tree: 1662 tests passed and one skipped, the budget
guard passed, the three script-style suites CI runs passed, the register gate
printed zero blocking, and `checks.yml` went green on the branch.

What the branch still does not do is write an issue. 2026-W41 is missing, the
window to recover it under its own label closes at 23:59 UTC tonight, and the
command that recovers it is `modal run`. The mail path is the owner's Gmail over
SMTP behind the Modal secrets named `Gmail` and `gmail_pass`, and the issue row
needs `DATABASE_URL`. No agent seat holds any of the three. The branch makes the
next outage survivable and visible. It cannot write the issue the last one ate.

## #315, abandoned, and this is the reason

`alexandria-engineer/2026-10-16-message-press-backup-seat`, one commit, one
file, 33 lines, its own run note. The PM could not tell from the diff whether it
was live, which is the correct reading: there was nothing in it to tell from.

It planned three things, and the reason it is abandoned is that the first was
built elsewhere and the other two are blocked on credentials that no change to
this repository can produce.

Item 1 was a board event when the press cannot write an issue, naming the ISO
week it failed on. That exists and is merged. `tools/press_watch.py` posts it,
and the card titled "Press: no issue for 2026-W41" on the board is that event
having fired.

Items 2 and 3 were a backup writer seat on the host and a rehearsal proving it.
The design said the seat would write the week's issue from the corpus, hold it to
the voice check, and send it down the same mail path. The last clause is where it
dies. The mail path is authenticated SMTP through the owner's Gmail, held as
Modal secrets. Recording the issue needs `DATABASE_URL`. A host seat holds
neither, and holds no Modal token to borrow them with. So the backup pen as
designed would write an issue it cannot send and cannot record, which does not
remove the one human step that is actually holding 2026-W41.

Abandoning the pull request is not abandoning the idea. The honest version of it
is in `docs/ideas.md` on this branch: a command that drafts the week's issue into
a file for the owner to send with one command, which is a smaller promise that
can actually be kept. The branch is kept and closing is reversible.

## The repeat this run filed

`INC-2026-10-18-the-ship-first-rules-closing-half-went-unrun-and-an-empty-draft-aged-two-days`.
The ship-first rule has two halves and the org only ever runs the first one. A
run-note-only draft is byte-identical to a live run's first commit, so nothing
can tell a pull request opened three minutes ago from one opened two days ago
and dead, and the cost of that falls on whoever reads the queue.
