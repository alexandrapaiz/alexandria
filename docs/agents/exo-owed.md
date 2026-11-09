# The ExO seat's owed list

Work this seat has found and not yet done. One row per item, in one file, so
that losing a row takes an edit instead of a silence.

**Read this file every wake run.** §0 of `prompts/exo-agent.md` gives a wake run
the event's work, three standing duties and one improvement, and tells it to
skip the weekly sweeps. The items those skipped sweeps generate land here. A
wake run that takes one of them says so in its run note and moves the row.

## Why this file exists, and it is not tidiness

This list used to be carried by re-copying it into each new entry of
`docs/agents/learning-log.md`. It was written that way from 2026-10-24, where
the duty-classes card counted it "fourteen consecutive wake runs" deep, and it
was last written on **2026-10-26**, six items long. Then it stopped. Nothing
decided to stop it and nothing recorded that it had: the next entry simply did
not contain the paragraph, and neither did any of the **22 learning-log entries
of this seat** after it, across **58 host-recorded runs**, 36 of which exited
clean. Thirteen days.

An append-only log is the wrong home for standing state, and the reason is a
property of the medium rather than of anybody's care. A list that survives only
by being re-copied has exactly one failure mode and it is silent: the entry that
omits it looks exactly like an entry written on a day when nothing was owed. No
diff shows a deletion, because nothing was deleted. No check can fire, because
there is no declared place for the thing to be missing from. It survived 21
entries on diligence and died on the 22nd without a trace.

In a file, the same loss is a deletion, with an author, a commit and a date.
That is the entire argument.

**And the cost was not only bookkeeping.** The duty-classes card
(`docs/agents/unowned-duties.md`, class B) has been with the owner since
2026-10-24T22:15Z — **sixteen days** — asking her to let a wake run take one
owed item per wake. Its whole case is the depth of this list. The evidence
stopped being maintained two days after the ask was posted, so the figure the
owner is deciding on is frozen at a number that is now wrong in the direction
that weakens it. Worse, the remedy it proposes — "a wake run takes one item from
the owed list, oldest first" — could not have been executed on the day it was
granted, because there was no list left to take an item from. **A proposal
waiting on a decision had its own input destroyed while it waited.**

## The rows

Restored on 2026-11-09 from the list's last two writings, which are the
2026-10-26 entries at `docs/agents/learning-log.md` — the six-item paragraph
and the three cap rows beside it.

**Every row below is `unverified`, and that is deliberate.** Thirteen days
passed in which some of these may have been discharged by a weekly cycle or by
a wake run that did not know it was clearing a row. This run restored the
ledger; it did not re-derive ten sweeps, which is weekly-cycle work a wake run
is told to skip. So each row carries the date it was last *confirmed* owed
rather than an assertion that it is owed today. Verifying them is the next
cycle's work, one row at a time, and a row that turns out to be done is struck
with the evidence that closed it.

This follows the register's own rule, written on 2026-11-01 after three class A
gates were read off a calendar: **a date is not an observation.** A row here
says when somebody last looked, never what is true now.

| # | owed item | source | last confirmed | state |
| --- | --- | --- | --- | --- |
| 1 | §3g public-claim sweep, live-surface pass | charter §3g | 2026-10-26 | unverified |
| 2 | Register polarity sweep (§3d's polarity test) | charter §3d | 2026-10-26 | unverified |
| 3 | §3b unowned-duty hunt | charter §3b | 2026-10-26 | unverified |
| 4 | Dispatch-queue re-verification | charter §5 | 2026-10-26 | unverified |
| 5 | §5b repository sweep (the GitHub home) | charter §5b | 2026-10-26 | unverified |
| 6 | Duty-classes card, class B — four rows naming this seat | `unowned-duties.md` | 2026-11-09 | **open, with the owner 16 days** |
| 7 | Rule-5 cap re-derivation, `engineer` — 450 wanted, marked unmeasured | `turn-caps.md` rule 5 | 2026-10-26 | unverified |
| 8 | Rule-5 cap re-derivation, `skill` — 400 wanted, marked unmeasured | `turn-caps.md` rule 5 | 2026-10-26 | unverified |
| 9 | The charter split proposed in the 2026-10-26 weekly-cycle note | learning log, 2026-10-26 | 2026-10-26 | unverified |
| 10 | On a daemon restart, re-run the three-state check across all twelve seats | learning log, 2026-10-26 | 2026-10-26 | unverified, conditional |
| 11 | Relay page: move the 2026-11-08 capacity Ask 1 to LANDED and rewrite the sentences written around its absence | `exo-run-note-2026-11-09-message-order.md` | 2026-11-09 | **open** |
| 12 | Apply the two charter sentences the 2026-11-09 order wake deferred: a conflict claim names two heads, and the relay page needs a DECLINED state | `exo-run-note-2026-11-09-message-order.md` | 2026-11-09 | **open** |
| 13 | Write the message route's two acceptance rules into §3f rule 1: no block over 420 characters, and no `#`-and-digit in the body | `INC-2026-11-09-the-message-route-enforces-two-prose-rules-no-charter-records-and-the-refusal-reads-like-a-field-error` | 2026-11-09 | **open** |
| 14 | Route the `answered_by` time-join: the board pairs a note with its addressee's next outbound message whatever the subject, so a note is marked answered by a message that never read it. 34 of 158 messages to this seat carry the field. Computed board-side; appears nowhere in this repository | `exo-run-note-2026-11-09-message-disjoint.md` | 2026-11-09 | **open, routed not reached into** |
| 15 | `MACHINERY_EXITS = {124, 137, 143}` in `docs/standards/pm.md:883` watches one live code on the surface missing 83 of 110 kills, and fires on none of the live word vocabulary. HQ's vendored standard, so routed | `tools/kill_vocabulary.py` (exits 1 on four findings) | 2026-11-09 | **open, routed not reached into** |
| 16 | Read back the 14:36Z prediction on the relay page's cap row: does a `scope: spend` refusal window appear after ~14:30Z on 2026-11-09? Either reading closes a two-round disagreement with HQ about whether the monthly cap gates the weekly overflow | `hq-relay.md` 2026-11-09 09:0xZ entry; `exo-run-note-2026-11-09-message-gauge.md` | 2026-11-09 | **open, and it has an answer by 15:00Z** |
| 17 | Vendor HQ's `tools/merge-register.py` into this repository, at HQ's head and not at Ursa's pin | `exo-run-note-2026-11-09-message-rebase.md` | 2026-11-09 | **open, routed to `engineer` not reached into** |
| 18 | Point the §2 instrument rules at the *selector* and not only at the subject and the argument: group a regex's own hits by day before trusting it. Three sections of the charter carry the subject/argument/floor versions; none covers a regex whose last match is a week old | learning log L-A180, 2026-11-09 | 2026-11-09 | **open** |
| 19 | Carry the arrival-rate factor into the charters that set wake behaviour. `tools/burn_shares.py` says 79% of the burn growth is runs/hour and 94% of this cycle's runs woke on a message; §5 makes the agent layer the one writable surface, and no charter in this repository mentions the cost of a wake | `tools/burn_shares.py` (exits 1), 2026-11-09 | 2026-11-09 | **open, the improvement this run measured and did not spend** |
| 20 | A §3f delta must name the **commit** of the table it diffs against, not only its timestamp. Two wakes of this seat composing deltas in parallel against the same parent each read a true previous table and fork the chain invisibly; this run's 09:0xZ table skipped the 08:4xZ generation that way and the repair was made in the merge | `hq-relay.md` 2026-11-09 09:0xZ entry, the correction at the foot of its table | 2026-11-09 | **open** |
| 21 | Write the resolution-timing rule into the charter beside §864's *a decision that waits grows*: **resolve a register conflict when the merge is next, not when the conflict appears.** Measured — the previous wake's hand resolution of #879 survived 17m36s against a 47-hour owner clock, and each redo moves a head a live ask pins. Charter edit, so Tier C | `exo-run-note-2026-11-09-message-rebase-890.md` | 2026-11-09 | **open** |
| 22 | This file carries the defect it exists to cure: row 6 reads "sixteen days" with no instant beside it, so it decays the way a held cycle verdict does. Replace every duration on this page with the instant it is measured from | this file, found by the `rebase-890` wake | 2026-11-09 | **open** |

Row 6 is the one row on this page this seat may not settle for itself: it widens
this seat's own budget, so no silence rule reaches it and it waits.

Rows 11 and 12 were added by this run from the previous wake's run note, where
they were recorded as owed in prose addressed to "the next run of this seat".
That is the same defect this file fixes one layer out: an obligation left in a
run note is readable only by a run that thinks to open that note, and there are
twenty-two notes.

## How to use it

- **Taking a row.** Name it by number in your run note and in the pull request,
  strike it here in the same commit, and say what closed it. A row closed
  without evidence on this page is not closed.
- **Adding a row.** Append it with today's date and the surface that generated
  it. A finding that is correct, written down and never applied is the failure
  this seat exists to prevent.
- **Verifying a row.** Replace `unverified` with the date you looked and what
  you found. If it was already done, strike it and name the run that did it.
- **This file is not an owner.** It records work; it does not authorise any. A
  row that needs a budget or another seat's charter still needs the ask.

**The hole at 16 was left on purpose, and a later wake has filled it, so #879
now faces the collision the hole existed to prevent** (corrected 2026-11-09
09:3xZ by the `rebase-890` wake).

The original note read: *"Row 17 is numbered 17 and not 16 … Row 16 is allocated
on `alexandria-exo/2026-11-09-message-draft-debt` (PR #879), which is mergeable
but unmerged, so `main` will read 15 then 17 until that branch lands. Taking 16
here would have recreated by hand exactly the collision this run had just
resolved by hand. The hole is cheaper than the collision."* The reasoning was
right and the prediction is now false. **`main` reads 16**, taken by the `gauge`
wake on PR #895. So when #879 lands, its own row 16 collides with that one,
which is exactly the outcome the hole was left to avoid.

Two things follow, and the second is the general one.

- **For #879 specifically:** its row 16 is renumbered on merge rather than kept.
  By this page's own rule the published side keeps its numbers, so main's 16
  stands and #879's row takes the next free number. Whoever resolves that merge
  should renumber the row **and** any prose in #879 that names it by number.
- **A reserved hole is not a reservation.** The note above was correct reasoning
  written in prose, at the foot of a file with no field a later wake reads
  before allocating. The next wake allocated into the hole without ever
  disagreeing with it, because nothing made it read it. That is the same class
  this run struck out of the cycle register: **a reading that was true when
  written, put down without the instant it was true at, is read by the next run
  as a standing fact.** The cure is the same too — a declared place for the
  thing rather than a paragraph asking for care. For this page that means **the
  next free number belongs in a field at the top of the table, not in a sentence
  at the foot of the file.** Not done here, because changing this register's
  shape is more than a wake run's one improvement; it is owed beside row 22.
