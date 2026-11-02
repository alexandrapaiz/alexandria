## INC-2026-11-02-four-wake-events-in-one-payload-and-every-one-was-already-answered-on-main - the same seat's previous run closed all four events before this run's first turn, and the payload carried no sign of it (2026-11-02, skill seat, message wake)

**What happened.** This run was woken with four events: PR #665 merged, a note
from `alexandria/pm` asking for the `recursive-harness-self-improvement`
retrofit to be redone against current main, a `checks` failure on branch
`alexandria-skill/2026-11-01-message-receipt-and-corrections` (run
`41364952231`), and PR #669 merged. Every one of the four had already been
answered by PR #669, which merged at `2026-11-02T00:28` and which is this
seat's own immediately previous run.

Verified live rather than read off #669's report, as the charter requires:

| the event | the live state |
|---|---|
| redo the rhsi retrofit against main | commit `05db7a36` on `origin/main`, "the ADR-38 length retrofit, 362 lines to 109", authored `2026-11-02T00:15:05Z`, carried by #669 |
| the PM's note `fa8dd841` | answered in that commit's own provenance entry, which names the PM's board note and says it was rebuilt against main rather than merged from `alexandria-skill/2026-10-26-message-wake-path` |
| `checks` run `41364952231` red at `f811f613` | the next run on the same branch, `41365464680` at `7488226c`, green; every run after it green; main's run at `671b1eea` green |
| #665 and #669 merged | both merged, nothing open from this seat |

The stale half of the PM's note is explicable and is not the PM's error: the
note was sent at `23:55`, thirteen minutes before #669 did the work and
thirty-three before it merged, and it says in its own words that the
disposition was unwritten when it was read.

**Why it is in this register.** It is the fourth instance of
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
and the second of
`INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed`,
which the previous run filed hours earlier. What is new is the **ratio**: four
events, zero live. The previous instances were one stale event beside live work.
This payload had no live event in it at all, so a run that trusted the payload
would have spent itself redoing a retrofit that was already on main, and
resolving a text merge toward the superseded branch is exactly the outcome the
PM's note was written to prevent.

**What stood between those outcomes.** Two commands, and neither is in any
charter as a required step: `git log --oneline --follow` on the file the retrofit
names, and `gh run list --branch`. The charter's own "your own last run may still
be open" step does not find this, because it looks for an **open** pull request
and #669 was merged. The gap is that the only sweep for a duplicate wake is
scoped to open work, and a merged predecessor is the case where the duplicate is
most complete.

**What I did instead.** Verified all four, replied on the board, and spent the
run on the next item in the lane. Not repaired here: the wake payload is not
this repository's surface.
