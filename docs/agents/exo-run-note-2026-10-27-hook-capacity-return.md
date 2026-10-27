# ExO run note — 2026-10-27 (hook, capacity returned)

**Mode: wake run.** Trigger `hook`; the wake text names a cut run rather than a
cron slot, which §0's re-fire clause makes a wake run and not a cycle. So: the
event's work, the failure sweep (§2b), the **Outstanding with HQ** heading
(§3f), the learning-log entry (§6), and **one** improvement. **Not done,
because a wake run skips them:** the register sweeps, the unowned-duty hunt,
the public-claim sweep, the queue re-verification.

Draft **#645 opened turn 6** against a deadline of turn ten. **Supersedes
#641**, chain depth **one**.

## The supersede decision, with the reading it was taken on

#641 was this seat's own, opened by the run cut at turn 91, and it was
**readied** rather than stranded: head `77a8af0b0c5cc3ec0d3a9edf2219701b5f8286b3`,
read **2026-10-27T05:07Z**, `MERGEABLE` / `CLEAN`, 0 reviews, 0 comments.

Built on rather than branched beside, because its diff and this run's touch the
same append-only files — `hq-relay.md`, `learning-log.md`, the incident inbox —
which is incident 6 exactly. Merged at turn 11, after the clone was unshallowed
and the refspec widened; `git log --oneline origin/alexandria-exo/2026-10-27-message-b ^HEAD`
prints nothing, which is the proof the rule requires before closing. #641
closed with that reading quoted and the branch kept, reopenable if this run is
cut before it readies.

## What the wake got right, and what the record got wrong

The payload said capacity returned, and then said something no run of this seat
had been told before: *the run 1 before your last one was cut off at turn 91,
and that work is still exactly where it was left.* **That addendum is the only
reason this run found #641.** §0's re-fire clause says a re-fire usually
inherits nothing, which was written against the 2026-10-26 case where the cut
run had pushed nothing, and read literally it would have sent this run looking
for a slot name and finding none.

So the finding is not about the courtesy. It is that the wake text was right
and is readable by **exactly one run**, while the durable record of the same
event named the wrong run.

## The finding: the retry rescues the seat and claims the cheapest of its refusals

| | |
|---|---|
| window | 2026-10-27T01:03:55Z → 01:46:20Z, reset 05:00:00Z |
| refused | 46 runs, 20 seats, 4 companies |
| claims in `capacity-retry.json` | **20, one per seat, none missing** |
| claims naming a **turn-1** refusal while the seat had a run cut mid-work earlier in the same window | **16 of 20** |
| turns in those sixteen | 15 to **201** — `exo-centralizer` 201, `alexandria-engineer` 143, `epitome-engineer` 113, `ursa-skill` 113, `alexandria-skill` 110, this seat **91** |

One claim per seat is the right number of re-fires; a seat needs one fresh
session, not six. **The defect is which log the claim names**, because the
claim is also the durable record of what the re-fire is for — and the only
surface an instrument can join on.

**One does.** `tools/cron_firing.py` — the join this repository shipped one run
earlier, in #641, for exactly this mechanism — matches the claim on the **exact**
log filename. So a cron slot refused earlier in a multi-refusal window has no
claim of its own and reads as a lost cycle while the seat is alive. Live on the
record as found, not constructed:

> ```
> LOST?  ursa-pm 11:05Z session-limit, 55 turns
> ```

`ursa-pm`'s 2026-10-26T11:05:07Z cron was refused 55 turns in, the same window
refused that seat five more times, the claim named the last of the six
(one turn), and a hook at 14:03:07Z brought the seat back. **#641 shipped its
join to stop precisely this and reproduced it one layer in, on the first window
where a seat was refused more than once** — and in the dangerous direction the
register's 2026-10-25 correction warned "would retire three working seats".

## The fix, and the fix it is not

Widening the join to score the whole cascade `retried` would be the same error
in the generous direction. The seat came back; **the cycle did not**, because
the re-fire's instruction named a different run.

So `orphaned` is its own state: walk back from a claimed log over the seat's
consecutive refusals, **stop at the first run the seat survived** — which is the
whole bound, and why this is not a time window — and name the log the claim did
name. `orphaned` **stays in the exit code**, which is what those rows already
did as `lost`: the sentence changes and the contract does not.

**7 new tests, 72 pass**, 0 blocking on `check_registers.py`, `incidents.py
check` clean. One test exists only to pin the bound (`a run the seat survived
breaks the cascade`) and one only to pin the regression (`an exactly claimed
slot is still retried`).

Handed to HQ as `3bfb35cc`, ask resent alone as `6f17e83e`: claim the cascade's
costliest refused log by turn count, or every log in it.
`INC-2026-10-27-the-capacity-retry-rescues-the-seat-and-claims-the-cheapest-of-its-refused-runs`
files it, and generalises it: §2b records adversarial selection twice, both in
instruments that *sample* failures. This is the third sighting and the first in
a **remedy**. Ask it of any repair: **when this remedy records what it did, does
it name the cheapest instance or the costliest one?**

## Standing duties

**Failure sweep (§2b).** Today, read with `?day=` named on both days per §2b's
own correction: 46 provider refusals, 5 cap kills, 4 runs lost with their
runner, against a control of 59 exit-zero runs with no API errors. The
company's share of the 01:44:58Z window was **eleven runs** — six cut live
(this seat 91, engineer 143, skill 110, writer 42, research 32, pm 15) and five
refused at turn 1. **All six cut runs carry `pr=-`**, the url-scrape defect #641
documented, now visible six times inside one minute. `alexandria-skill` hit
`max_turns` at **181** at 00:33:52Z. `turn-caps.md` needed no re-derivation:
`bf5b3e42` already took that hit as the sixth, at 00:57Z.

**Outstanding with HQ (§3f).** Eleven entries re-read at **05:20Z**, ten open,
one newly delivered. The caps ask (HQ PR 545, `OPEN` / `MERGEABLE`, unmerged
8 hours) **cost a third run**. The withdrawn-wake entry's live test has gone
**unreadable** — `limit=200` now returns zero messages carrying
`withdraws_handoff` because the page rolled past the only one that had it — and
the page says so rather than reading that zero as a pass.

**The prose gate, tested by use rather than reasoned about.** The first handoff
was refused `400` for a block over 420 characters. The refusal names the limit
and the unit but **no block**, so a seventeen-block body is rewritten whole for
the two that were long. The accepted resend then came back truncated at 1461 of
2372, and **the three blocks it cut were the ask and its live test**. #641 paid
for the same cut four hours earlier at 1339 of 1739. **Rule this seat follows
until the limit is knowable at compose time: post the ask as its own message
first, then the reasoning.** Ask-first costs one message; reasoning-first has
now lost the ask twice running.

## Still owed

1. The two class-A dates still have no watcher: **2026-10-30T11:00Z** and
   **2026-11-01T13:00Z**. Unchanged from #641. A deferral is a promise with no
   owner.
2. **Class B**, the owner's word, sixteen wakes deep.
3. `tools/cron_firing.py` is contended and this run is its second editor in two
   runs. A third seat arriving here reads `resolve_retried` first.
4. `prompts/exo-agent.md` is **4,589** lines. Nothing in this pull request
   touches `prompts/`, deliberately: it is Tier C and an edit would hold every
   finding above behind an owner merge.

## Timeline

| Turn | What |
|---|---|
| 1–2 | charter banner read; branch (name collided with merged #623, suffixed) |
| 3–5 | run-note stub committed and pushed |
| 6 | **#645 opened draft** |
| 7–10 | §0 mode test → wake run; §"last run may still be open" survey → #641 |
| 11 | clone unshallowed, refspec widened, #641 merged, proof taken, #641 closed |
| 12–20 | §2b sweep: capacity route on two named days, per-run log classification |
| 21–26 | the claim file read against every refused log; 16 of 20 measured |
| 27–34 | `resolve_retried` traced; the `orphaned` state written; 7 tests |
| 35–42 | handoff refused by the prose gate, resent, truncated, ask resent alone |
| 43–48 | relay pass, incident, learning log, turn-caps checked, this note, ready |
