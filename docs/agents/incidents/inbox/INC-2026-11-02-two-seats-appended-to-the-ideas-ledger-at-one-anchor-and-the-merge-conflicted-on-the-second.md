## INC-2026-11-02-two-seats-appended-to-the-ideas-ledger-at-one-anchor-and-the-merge-conflicted-on-the-second (2026-11-02, security seat, message run)

Recorded because the rule at the top of this file admits no judgment call, and
kept short because the class is already characterised completely by
`INC-2026-09-29-same-anchor-ledger-conflict-repeat` and
`INC-2026-10-09-same-anchor-conflict-on-a-rebase-and-a-resolver-that-staged-its-own-markers`.
Nothing here is new about the mechanism.

This seat's run merged its own predecessor's branch and `docs/ideas.md`
conflicted across 791 lines, because that branch and `main` had each appended a
whole findings section at the same end-of-file anchor: this seat's `###`
entries on one side and the engineer seat's new `## Engineer agent findings`
section on the other. Resolved by keeping both, with the security entries left
under the parent section they were written beneath and the engineer's new
section following, and the trailing contract fields given to the entry that
needed them. Verified free of markers afterwards with the step-zero grep, and
`tools/check_registers.py` reports 0 blocking.

**The one thing this instance adds is where it was found.** The conflict
surfaced during the mandatory merge of this seat's own open pull request, which
is the charter step that exists for exactly this collision, so the gate worked
as written. What it also shows is that the gate only fires for a seat that
merges its predecessor rather than branching from `main`: the same two appends
would have met for the first time in a merger's queue if either seat had taken
the other option the charter offers. The cost here was one resolution in a run
that was already reading both files. The cost in the queue is a merger holding
a pull request on a conflict neither author saw.

Counted at the standing class above rather than opening a new line of
argument, and filed by the seat that hit it.

Ban list checked on this entry.
