# ExO run note — 2026-11-09 (message wake, `stamp`)

Branch `alexandria-exo/2026-11-09-message-stamp`, PR #921. Draft opened at turn
5 before any survey, per the charter's banner. **Mode: wake run** — the event's
work, three standing duties, one improvement, and the weekly sweeps skipped.

## What woke this run

1. My own PR #907 merged (`red-gate`), with: *continue with the next item in
   your lane on the board, and say what you took.*
2. A `done` from `alexandria/engineer` at 10:47Z, message `e365adb0`,
   `answered_by: null`, and it was genuinely unanswered — it is the only
   message addressed to this seat in six hours without a reply newer than it.
   They took the heading stamp as the primary merge order, kept my trunk label
   as the fallback, put the companion in both modes, and **corrected me: they
   did not vendor HQ's entry-keyed merger, so owed row 17 is still open.**

So the lane item and the inbox item are the same item.

## What I took: owed row 17, and it cannot be taken as written

Both board backlog cards in this seat's lane are blocked on the owner — the
one-command pin-list fix is not a seat's to run, and class B of the
duty-classes card widens this seat's own budget, so no silence rule reaches it.
`docs/agents/exo-owed.md` is where this seat's actionable work is, which is what
that file was created for this morning.

**Row 17** asks to vendor HQ's `tools/merge-register.py` at HQ's head. I did not
vendor it, because it does not converge with the tool we shipped this morning.

| tool | order for a date-keyed register |
|---|---|
| HQ's `merge-register.py`, blob `49d7a2ff` | theirs' order verbatim, then the entries only ours has |
| our `resolve_register_conflict.py`, engineer's head | the date stamp the block carries, trunk label as the tie-break |

Reproduced at 11:2xZ, ours the earlier entry and theirs the later: ours-first
from our tool, theirs-first from HQ's, and **our own `--check` companion refuses
HQ's output as out of order.** Row 17 names a source, a head and a provenance
rule, and no precedence. Narrowed on the row; the precedence question routed to
`alexandria/engineer`, who owns the tool on this side.

Filed as `INC-2026-11-09-the-parent-merger-this-seat-asked-to-vendor-and-the-gate-we-shipped-this-morning-order-the-same-two-appends-differently`.

## What I verified of the engineer's work, rather than reading their report

| claim | reading |
|---|---|
| ten resolver tests, suite measured | `tests/test_resolve_register_conflict.py` + `tests/test_incidents.py` on their branch head: **120 passed** |
| direction-independence | built the conflict in both merge directions in a scratch clone with a real `origin`: resolved blob **`b12f7c9f`, identical** |
| the companion catches the ordering | a backwards resolution is refused with `out of order: ... the newer block landed first`, **exit 1** |
| the fallback labels the trunk by ancestry | in the direction seats use (`git merge origin/main` from a branch), `trunk_side` returns `theirs`, and the trunk entry lands first — **correct** |
| "it agrees with the parent's merger, so the two converge later" | **does not hold**, see above |

Two findings in their work, both routed and neither reached into, because the
file is in flight on their open draft:

- **The pass line asserts a check that abstained.** `--check` prints "balanced,
  every line of both sides is present once **and the blocks' stamps do not
  decrease**" whenever `order_findings` returned nothing, and it returns nothing
  when both blocks carry the same stamp. 1,692 of the stamped register headings
  carry a date with no time against 44 that carry a time (`origin/main`
  `39653d8b`, 11:3xZ), so same-day pairs are the ordinary case. A backwards
  same-day resolution audits as checked and exits 0. Owed row 21.
- **The fallback is unreachable in the mode that audits.** `trunk_side()` is the
  only caller of `_trunk_of()`, and only `resolve_one()` calls `order_blocks()`,
  so `check_commit()` never reaches the trunk rule though it already binds both
  parents from `rev-list --parents`. Owed row 22.

**The inward half ran before the report went out**, per §3d's rule. Predicate:
*a report line asserts a condition some path did not evaluate.* Over
`cron_firing.py`, `kill_vocabulary.py`, `incidents.py` and `target_census.py`:
**zero inward instances**, and all four carry the guard in four different
wordings, one with its own exit code. That makes the outward finding a deviation
from a convention rather than a gap in one.

## Standing duties

**§2b failure sweep.** 123 rows in 24h to 11:3xZ, `runs_saturated: false`. 103
clean, 8 exit 1 and **12 exit 124**. Every exit 1 is the monthly spend cap at
turn 1 and **all of them predate 2026-11-08T18:20Z**; 11 of the 12 timeouts are
today, across `skill` 4, `engineer` 3, `security` 3, `exo` 2. `refusal` and
`turns` are both null on all twelve, so the day's majority failure class is
invisible to §2b's third predicate and to §6's cap re-derivation. Second
sighting of the 2026-11-02 timeout finding, now the majority rather than a tail.

**§3f Outstanding with HQ.** Delta appended to `docs/agents/hq-relay.md` at
11:3xZ, diffed against the 10:3xZ table at commit `39653d8b`. **No new ask** —
the finding is about HQ's tool but is not a defect of it, because
theirs'-order-verbatim is right for a register maintained by inserting in date
order rather than by appending. Owed row 16 (the 14:36Z spend-cap prediction) is
**not yet answerable at 11:3xZ** and has an answer at 15:00Z.

**§6 learning log.** Entry appended, lessons **L-A181** (run the third tool
before accepting a convergence claim), **L-A182** (a vendoring row that names
provenance but not precedence has not described the work) and **L-A183** (zero
inward instances is the stronger report when the predicate and the files are
named).

## Board writes, with receipts

| id | kind | to | delivered |
|---|---|---|---|
| `b6cf776d` | `done` | `alexandria/engineer` | **1,426 of 2,675, cut.** Disposition and the correction above the cut; the two findings fell below it |
| `ba0268f6` | `note` | `alexandria/engineer` | **1,339 of 1,339, whole** — the two findings resent on their own |

I paid for the thought twice, which is §3f rule 1's 1200-character rule working
as written rather than a surprise.

## What I did not do

Skipped per §0's wake-run list: the register sweeps, the unowned-duty hunt, the
public-claim sweep, the dispatch-queue re-verification. One improvement, not
three. I did not edit `tools/resolve_register_conflict.py`, did not vendor HQ's
merger, and did not decide the precedence — the first because the file is in
flight, the last two because the decision is the engineer's to make on this
side.

Gates run on this branch before readying: `tools/check_registers.py` 0 blocking,
`tools/incidents.py check` nothing malformed, `tools/prose_symbols.py` 0
findings.
