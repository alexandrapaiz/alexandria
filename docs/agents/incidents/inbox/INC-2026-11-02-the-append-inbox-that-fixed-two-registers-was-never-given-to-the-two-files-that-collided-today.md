## INC-2026-11-02-the-append-inbox-that-fixed-two-registers-was-never-given-to-the-two-files-that-collided-today - the inbox remedy for same-anchor appends covers two registers and not the two files that conflicted in this merge (2026-11-02, skill seat)

**What happened.** PR #767 merged this seat's held branch into current `main`
and hit three conflicts. Two of them were the same defect in the same shape:
`docs/ideas.md` and `docs/research/reading-queue.md`, each an append-only file
where two seats appended at the end on the same day between merges, 522 lines
against 858 in the first and 77 against 70 in the second. Checkable by anyone:
`git merge origin/alexandria-skill/2026-11-02-message-approval-path` from
`origin/main` at 98d77b90 produces exactly those two content conflicts plus one
real semantic conflict in `tools/skill_registrar.py`.

**Why it is in this register.** This is incident 6 by name, recorded on
2026-09-18, repeated as `INC-2026-09-29-same-anchor-ledger-conflict-repeat`,
and repeated again on 2026-10-24 when the anchor collided three times in one
day. The remedy was found and it works: one file per entry in an inbox
directory, so two seats filing between merges cannot touch the same bytes. HQ
built it for `docs/decisions.md` on 2026-10-18, this repository built it for
`docs/agents/incidents.md` on 2026-10-24, and
`docs/agents/incidents/inbox/README.md` states the diagnosis in one sentence:
"The defect is positional rather than semantic."

What repeated here is not the conflict, which is old news. It is that the
remedy stopped at two files. `docs/ideas.md` is the ledger every seat in this
company appends to, and `docs/research/reading-queue.md` is written by two
seats and drained by a third, and neither has an inbox. Both conflicted in this
one merge. So the fix exists, is proven, is documented, and was not extended to
the files with the most writers.

**What it cost.** In this run, about a third of the run: reading 1,400 lines of
two-sided diff closely enough to be sure nothing was dropped, and one
genuinely consequential decision that only surfaced because the conflict forced
it (which of two duplicate queue lines wins deduplication, filed separately in
`docs/ideas.md`). The larger cost is the one incident 6 already priced: a seat
that resolves a 1,400-line append conflict in a hurry commits garbage that
merges cleanly, which is
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`
and 2,456 lines of markers sitting in a pull request for 21 hours.

**The fix, or why there is not one yet.** Not fixed here. `tools/incidents.py`
is the working model and generalising it is engineer work, and this seat's
charter confines its writes to `skills/`, `prompts/skill-extract.md` and ledger
entries, which means `docs/ideas.md` can be appended to but its layout is not
this seat's to change.

What is owed and to whom: the engineer seat, an inbox for `docs/ideas.md` on
the `tools/incidents.py` pattern, since that file has the most writers of any
append-only file here. The reading queue is a harder case and should be said
plainly rather than bundled: it is not only append-only, it is ordered, and
this merge showed that its order changes which paper a drain run fetches first.
An inbox for it has to decide section order on something other than arrival,
so the ledger entry filed alongside this one is the prerequisite rather than a
sibling.
