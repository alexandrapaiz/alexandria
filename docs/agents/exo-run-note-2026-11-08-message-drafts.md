# ExO run note — 2026-11-08, trigger: message (branch suffix `-drafts`)

Status: **complete.** Opened at the start of the run per §"Ship first, then
work", amended in the commits that did the work.

**Mode: wake run.** Trigger `message`, a `pr.merged` on the capacity-return
hook's pull request. One improvement, three standing duties, and the register
sweeps skipped by the mode rule — named at the bottom so the gaps are known.

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

## The standing block: both conditions were discharged by the run it called dead

Confirmed before spending on it, which is what the block itself instructs:
`GET /api/standing?company=alexandria&seat=exo` at **23:35:27Z** returns
`{"company": "alexandria", "seat": "exo", "standing": "", "empty": true}`.

What happened in the eleven minutes between the block being composed at 23:21Z
and this run reading it:

| read at | surface | reading |
| --- | --- | --- |
| 23:36Z | #797 | **CLOSED** 2026-11-08T23:27:48Z |
| 23:36Z | #806 | **not a draft** — `ready_for_review` 23:32:31Z, state OPEN, 8 commits, +563/5 files |

Both acts were performed by run `cf72f999` — the run the block called over. Its
own description records closing #797 at 23:27:45Z with the verdict in a comment,
and it readied itself five minutes later. **It was not cut mid-act. It finished,
and the last two things it did were exactly the two the block asked this run to
do.**

So none of the block's three offered acts was this run's to take, and the honest
answer is the fourth it does not offer: the premise was false. That is the
fourth sighting of `run_row_behind`'s time-containment matcher calling a live
run finished, already diagnosed in
`INC-2026-11-02-one-wake-carried-three-conditions-and-all-three-were-already-resolved`,
so nothing is added to it but the instance.

**What is worth keeping is that the dismissal was cheap.** The block names its
own confirmation route, and one HTTP call settled two conditions. A wake that
names how to check it costs a turn to dismiss; one that does not costs a run.

## What this run took from the lane, and what it found there

The board's exo lane holds three non-`Done` cards: two in **Review** awaiting
the owner, and one in **Backlog** — the duty-classes card, whose body ends *"this
card exists so the next wake of this seat finds the work on the board"*. Its
class A had left two readings explicitly to "the next run of this seat". Both
were due.

### Security's row closes

| surface | reading |
| --- | --- |
| the slot | `2026-11-01T13:00:27Z`, fired on time, refused at turn 1 on the **weekly** wall |
| HQ's retry | claimed that exact log name, re-fired at `23:04:44Z` |
| pull request 657 | **merged `2026-11-02T01:13:17Z`**, +1061, 8 files, not a draft |

A re-fire that ships consumes the gate. Note what the 2026-11-01 entry got right
by *refusing* to answer: that night the firing tool printed `1 cycle(s) lost`
about this very run while it was alive and committing, and the entry left it for
today rather than publishing the verdict.

### Market's row stays open, and its gate was misnamed

| surface | reading |
| --- | --- |
| the slot | `2026-11-06T11:00:10.855Z`, fired on time, `trigger=cron` |
| its result | `429`, **`You've hit your org's monthly spend limit · ask your admin to raise it … · your weekly limit resets Nov 8, 11pm (UTC)`**, 1 turn, 406ms |
| a re-fire | **none** — the seat has no `-hook` log at all |
| next slot | `0 11 * * 5` → **2026-11-13T11:00Z** |

The card says to read each slot with the firing tool. It printed **`weekly-limit`**.

## The finding: a fourth reader of one sentence

`tools/cron_firing.py::classify_refusal` tested `"weekly" in text` first, and
both spend variants on this host carry `your weekly limit resets` in a
subordinate clause about a different wall.

| measured over `/srv/asc/state/.epito/logs`, one pass | |
| --- | --- |
| spend refusals returning `weekly-limit` | **257 of 257** — never `unclassified-429` |
| of those, cron slots | **74**, matching the incident's own count exactly |
| against | 487 genuine weekly, 415 session, 1,159 total |
| share of the slot refusals this module names | 74 of 177, **42%** |

Fixed with nine tests; both real spend variants quoted rather than paraphrased,
the **order** of the branches pinned by a sentence naming both walls, and the
three real weekly variants asserted in the other direction. `117 passed`.

Re-read after the fix, every `LOST?` row across the dark week names the right
wall: `python3 tools/cron_firing.py --day 2026-11-06` now reports `spend-limit`
for all ten refused slots in four companies.

**Why it matters past accuracy.** A weekly wall names its own reset; a spend cap
has none. Every remedy that follows from the word "weekly" is *wait for the
boundary*. Under the wrong label market's row read as waiting for a Sunday;
under the right one it had been waiting for the owner for six days.

**And the lesson is about where a rule gets written.** Tonight's
`INC-2026-11-08` entry measured three readers of this sentence, fixed the one
this seat owns, and wrote the correct rule *inside the file of the reader it had
just fixed*. Nothing walked it outward, and three hours later an unrelated
reading walked into the fourth. A classifier is **copied far more often than it
is imported**, so the unit of repair is the repository, not the reader. One
grep — `grep -rn 'weekly' --include='*.py' tools/` — would have found this on
the night.

## Three further corrections the reading forced

**The gate rule had no termination condition.** 2026-11-01 restated class A's
gate off the calendar and onto the record, which was right, but "a refused slot
re-dates the gate" re-dates forever while the row reads as *pending*. Market has
been re-dated three times on three refusals it did not cause. Added a counter:
after a **second** consecutive slot that fires, is refused, and is not claimed
by the retry, the row becomes a finding about the re-fire route and goes to the
relay. The row is still re-dated; the page stops reporting the wait as the state.

**A total written beside its table decays silently.** The firing-state table's
summary said "nine rows are unevidenced and four of those nine name this seat".
Counted off the cells it is **three and one** — and it was already wrong before
this run touched anything: the three exo rows it counted had been moved, in that
same table, to `fired and produced nothing` when the 2026-10-25 slot was
measured (correctly; that refusal was a genuine weekly one, verified). Nobody
re-derived the total when the cells changed. The stale sentence is kept with its
date, because what happened to it is the finding.

**The 2026-11-01 entry was one ahead of its own record.** It called 2026-11-06
market's "third gate, with two refusals recorded against it". Counting observed
slots it was the second of each. Said rather than quietly renumbered; the
refusal count has since caught up to two.

## The failure sweep (§2b)

- **2026-11-07** — 38 attempted, **38 refused, every one the spend wall**, 11
  seats, zero completed. Wholly dark.
- **2026-11-08** — 64 attempted, 39 refused (all spend, last at 18:20:00Z), 9
  completed, 11 still running at read time, **zero failed, zero killed**.

Every non-success on both days is the provider's wall. Not one is a seat's
defect.

**And the sweep's third predicate selected five runs that had not failed.**
`exit=0` with `pr=-` picked out five runs at 85, 51, 54, 146 and 52 turns.
**Both of the two this seat can check had shipped** — the `alexandria-exo` run
is #806 and the `alexandria-pm` run is #807, both open, neither a draft. `pr` is
scraped from what a run says as it ends, so `pr=-` is the absence of a *report*.
The other three are in repositories this seat cannot read. So the honest result
is **zero verified silent runs, not five**, and that is this run's one charter
improvement (§2b), because `cron_firing.py` has carried the guard in its own
docs since 2026-10-25 while the predicate this charter publishes did not.

**On the spend cap itself**, which the previous note left as its first check:
**26 runs started at or after 23:00:00Z and zero were refused**, against 14 when
that note was written. Last refusal anywhere 18:20:00Z. Still undecided between
"the cap was raised" and "the weekly reset is masking it", and it stays
undecided until refusals either resume or do not.

## Outstanding with HQ

Re-read against the **deployed** copy, per §3f's two-reads rule. Asks 1 and 2
are **still open on the host**: `limit_scope(spend)` returns `None` and
`reset_after` returns the weekly instant for both texts; `reset_scope` is not
present there. What moved is the blocker — `alexandra-systems` #637 is **no
longer a draft** (head `c9196e88d6`), so the distance is now a merge and a
deploy, neither of them this company's to perform.

**Ask 3 is new**, out of class A: `alexandria-market` is the only seat in this
company with a cron row and **no hook row**, across 190 re-fires and 33 agents
(`ursa-market` has two, so the seat's kind is not the discriminator). And the
retry's claim decisions are recorded nowhere — the claim file is overwritten per
window, the audit log has no claim action — so **a claim that produced nothing
is indistinguishable from no claim at all**, and nobody can answer whether
market was ever claimed. Asks for one append-only audit row per claim decision.
Delivered 23:51:45Z, message `1b4a8505`, 1,381 of 3,304 characters reaching the
wake with the ask in the first 300.

The board's `GET /api/claims` is **not** this surface — it is cards a seat is
changing, and it returns `{"claims": []}`. Checked before the ask was written.

## What shipped

- **`tools/cron_firing.py`** — `spend-limit` as a third refusal class, tested
  before `weekly`. Nine tests, `117 passed`.
- **`docs/agents/unowned-duties.md`** — class A closed out: security's row
  shut, market's re-dated and reclassified `open`, the table's summary count
  re-derived, the gate rule given a counter.
- **The incident addendum** — the fourth reader, written into tonight's
  third-limit-class entry rather than filed as a duplicate class.
  `tools/incidents.py check`: 368 entries, 160 waiting, nothing malformed.
- **`docs/agents/hq-relay.md`** — asks 1 and 2 re-read on the host, ask 3
  opened and delivered in the same run.
- **`prompts/exo-agent.md` §2b** — the one improvement.
  `tools/check_authority.py`: 7 files, 11 hunks, no line answered yes.
- **`docs/agents/learning-log.md`** — the entry, five live tests for the next
  run.
- **The board** — a comment on the duty-classes card saying what was taken and
  why the card stays in Backlog, and the handoff above.
- `tools/check_registers.py`: **0 blocking**, 71 warnings, all pre-existing in
  `docs/ideas.md`.

## Two things said rather than hidden

**`tools/ban_list.py` exits 1 on tonight's incident entry as it stands on
`main`** — 9 non-ASCII hits at lines 34–99 — despite the entry's closing line
"Ban list checked on this entry". The pre-existing hits are left alone, four of
them being the provider's quoted sentences, which is evidence. The addendum was
rewritten to plain ASCII so it does not add to them.

**My own first measurement of two exit codes was wrong** and is corrected here
rather than in a later run: I read `$?` after a pipe into `head`/`tail`, so I
reported `ban_list` as passing when it was `tail` that passed. Re-measured
directly. The charter's §2b warns about exactly this shape of reading and it
caught me on the tool whose job is to catch it.

## The card stays in Backlog

Class A has nothing left to say. **Class B is untouched** — the four rows naming
this seat, which need the owner's word and widen this seat's own budget, so they
do not proceed on silence. That is why the card was commented and not moved.

## Skipped by the mode rule, named so the gaps are known

The register sweeps, the unowned-duty *hunt* for a new row (§3b second test —
the class A reading above is the first test, not the hunt), the register-gate
sweep, the owner-as-seat audit, the HQ-origin audit, the public-claim sweep, and
the queue re-verification. At most one improvement, and it was §2b.
