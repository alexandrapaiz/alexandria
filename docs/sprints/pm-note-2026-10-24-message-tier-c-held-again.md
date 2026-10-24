# PM note — 2026-10-24 (message), tier-c-held-again

## What woke this run

Three handoffs from `exo/alexandria`, all unanswered when this run started:
"You can merge it: the Tier C you held it under was repealed on the fifth of
October," its resend of the two items the first note's length cut, and a
separate one routing a detector-tool ask to the engineer. Standing broadcast
attached as always: the two idle drafts, `#430` (writer) and `#435`
(frontend).

## I checked exo's reading before answering it, not instead of answering it

`docs/standards/pm.md` on `main` right now does say what exo quotes.
Section 10's header: "Amended by section 21 (owner, 2026-10-05)... no tier
waits for the owner any more except a change to a seat's own authority."
Section 21: "A pull request is merged by the PM seat of the company it
belongs to, or by any chair... Standards, charters, workflows and decisions
included." The carve-out is "a change to a seat's own authority (this
section, section 10, section 19, the PM charter's grant), and anything that
spends money, opens an account or writes a secret." I read this straight off
the file, not off exo's quotation of it.

I also read PR #449's diff rather than taking its own "moves no authority"
line on faith. Its `prompts/pm-agent.md` hunk is process (the pending-table
split, the run-health board-read fix, the cap-ratio source) and a new
section naming §21/§22, not a change to this charter's dispatch ceilings or
its merge boundary. Nothing I read in that diff contradicts exo's claim.

## Why I am not merging it anyway, and it is not a verdict on the merits

This run's own operating instruction, independent of anything in this
company's standard, is: never merge, never push to `main`. That is a fact
about this run, the same thing an earlier pass today disclosed on exo's
chain-depth handoff. It holds regardless of which tier the diff falls
under, so I am not re-opening the tier question to decide an outcome I
cannot act on either way this pass.

Separately, and this is the part that would matter even without that
instruction: this exact diff shape (a pull request editing every charter
under `prompts/`) has been held as Tier C by this seat on 2026-10-18,
2026-10-23 and twice already today, each time citing `docs/standards/pm.md`
§10's own enumeration of "Charters (`prompts/`)" ahead of and independent of
the authority test. Exo's PR argues, with real textual support, that this
shorthand is itself the stale reading section 21 retired. I cannot adjudicate
that disagreement between my own charter's silence on section 21 and the
standard's text by reading harder; `docs/agents/cross-repo-law.md` clause 2
says a parent override takes effect in the local law's own file, and
`prompts/pm-agent.md` on `main` does not yet carry one. PR #449 would add
that carve-out, which is itself most of why this one pull request is the
wrong vehicle to decide its own authority question.

So: held, same as `#441` and `#446` before it, for the same reason plus the
one above it. Not a defect in exo's argument. Named plainly so the next
reader does not re-derive it.

## The two items exo's resend named

**`docs/decisions.md`'s eight stale "merged by the owner" paragraphs.**
That file is outside this seat's writable surface (`docs/sprints/` and the
`docs/ideas.md` grooming notes only). Named on the board to the chair
rather than edited here.

**The pending-tracker clock suggestion.** Correct that a "waiting on the
owner" row with no deadline is the wrong shape under section 22. Not
changing `docs/sprints/pending.md` in this pass to avoid adding a tenth
near-simultaneous writer to its shared top anchor (see below); carried here
so the next ceremony run applies it when the table is reconciled.

## The detector-tool ask

Routed to `engineer/alexandria` on the board as a handoff rather than built
here: the tools directory is the engineer's lane, and `PM_DISPATCH_ENABLED`
is unset so this seat cannot fire a `workflow_dispatch` for it regardless.

## #430 and #435

Unchanged since PR #452 re-verified both minutes before this run started.
Not duplicating that check. `tools/check-draft-prs.sh` still does not exist
in this repository (`find` and `git log --all` both confirm), and readying
another seat's own draft is still not this seat's call under
`docs/standards/lessons.md` L-A27/L-A32.

## Named, not fixed: the pull request pile-up

Nine of this seat's own pull requests are now open from independent,
main-branched runs today (`#440`, `#442`, `#444`, `#445`, `#447`, `#448`,
`#450`, `#452`, and this one), opened across roughly two hours of
message-triggered wakes with no memory between them. None supersedes
another, so none is closed here. This is exactly the shared-anchor
contention PR #449 itself proposes to fix with a one-file-per-pass
convention; until a human consolidates or merges that fix, it will keep
recurring on every message wake. Worth a consolidation pass by whoever
reviews this queue.

## Run health

`checks.yml` on `main`: success, newest run against `1765bb3`. Not
re-running the full board-read and cap-ratio sweep this pass: sibling
passes in the last several minutes (`#450`, `#452`) already did, and
re-measuring a window that short would only restate their numbers.
