# ExO run note — 2026-11-09, message wake (`two-dones`)

Branch `alexandria-exo/2026-11-09-message-two-dones`, pull request
<https://github.com/alexandrapaiz/alexandria/pull/890>. Draft opened at turn 6,
before any survey, per the charter's top banner.

**Mode: wake run** (trigger `message`, no slot and no cut-run text in the wake,
so §0's re-fire branch does not apply). Did the event, plus the three standing
duties §0 names for a wake run — the failure sweep, the Outstanding-with-HQ
heading, and this note's learning entry. Did **not** run the register sweeps,
the unowned-duty hunt, the public-claim sweep or the queue re-verification.

## The wake

Two `done` messages from `alexandria/pm`, both addressed to this seat, both
answering handoffs this seat made. Both `answered_by: None` on the live inbox
read at 08:14Z, so neither was already discharged by an earlier wake of this
seat — §2a-1's outbox check, which this run ran before composing anything.

Also unanswered on that read and **not** this run's event: two notes from
`alexandria/engineer` at 07:10:21Z and 07:10:30Z. Left for whoever is woken
for them; naming them here so the next run of this seat does not rediscover
them as news.

## 1. The two-head migration table — PM's claims verified, one correction

All four pull requests read at **2026-11-09T08:18:54Z**, all four OPEN:

| PR | branch | head | role |
|----|--------|------|------|
| 885 | `alexandria-pm/2026-11-09-message-pending-gate` | `369eed08` | PM's adopting branch |
| 863 | `alexandria-pm/2026-11-09-message-ceremony` | `20ce4f12` | the newer table, adopted |
| 683 | `alexandria-pm/2026-11-02-ceremony` | `abd250f2` | the older table, dropped |
| 879 | `alexandria-exo/2026-11-09-message-draft-debt` | `9c9bec42` | this seat's charter fix, held |

Both of PM's head hashes match the live heads, so the report is live and not
stale.

**The byte-for-byte claim holds, and it holds harder than PM stated it.** The
archive blob is `bf1ced34b7d5e39be2112ca19b48f32bd14466bb`, 340,437 bytes, and
it is the *same blob* on all three branches — `pending/archive-to-2026-11-09.md`
on 863 and on 885, `pending/archive-to-2026-10-26.md` on 683. It is also
**identical to `docs/sprints/pending.md` on `origin/main`**. So the archive is
provably an unaltered copy of main's unmigrated file rather than merely two
copies that happen to agree, and the two differing filenames carry one blob.

**The adoption is exact.** `docs/sprints/pending.md` is blob `8a563427` on 885
and `8a563427` on 863 — byte-identical, zero-line diff. 683's is `99c495b8`.
PM took the newer table verbatim.

**Correction, and it is the one line of PM's note that is scoped wrong.** "The
branch I am dropping loses nothing by being dropped" is true of the *archive*
and false of the *branch*. Against main at this clock, 683 is the only branch
that files the four `INC-2026-10-24-*` records out of
`docs/agents/incidents/inbox/` into the register: it deletes those four inbox
files and adds **426 lines** to `docs/agents/incidents.md`. 863 does not touch
`docs/agents/incidents.md` at all, and all four slugs are absent from main's
`incidents.md` while all four inbox files are still present on main. So the
filing has not happened anywhere, and 683 is the only open branch that performs
it. A next reviewer who closes 683 on the strength of "loses nothing" closes
that with it. PM did not close it, which is the right call for a second reason
beyond the containment one it gave.

**And 885 is a strict subset of 863 for the migration, so 863 is still owed.**
885 changes three paths; 863 changes fourteen, including
`sprint-2026-10-26.md`, `sprint-2026-11-02.md`, `sprint-2026-11-09.md` — the
three missed Mondays — and `dispatch-queue.md`. Adopting 885 discharges the
conflict, not the ceremony.

**Adopting 885 costs 863 nothing in mergeability**, which is the thing worth
checking before recommending the order. Simulated with `git merge-tree
--write-tree`: 863 into main today conflicts on exactly one file,
`docs/ideas.md`; 863 onto a simulated post-885 main conflicts on exactly the
same one file and nothing else. The two shared paths cannot conflict because
both sides make the identical change. 683 into main today conflicts on
`docs/sprints/dispatch-queue.md`. Both conflicts are pre-existing staleness
against main and neither is caused by the adoption.

PM's refusal to close another seat's open work without a containment proof it
cannot produce from its own branch is correct and this seat is not asking it to
reverse that.

## 2. The Tier C hold on 879 — accepted, and one defect in the ask's clock

**The hold is right and this seat is not arguing it again.** Re-read on
`origin/main`, `docs/standards/pm.md` line 388: "**Tier C — owner merge.**
Charters (`prompts/`), this section and any change to the tiers or the dispatch
stops..." There is no content predicate in that sentence, so a `prompts/` edit
that widens nothing is still Tier C. PM is describing the documented current
state. This seat's register names the *narrowing that has not landed*, which is
a different object from PM's reading, and PM was right to say so.

**The §22 route is also right.** §22 covers "editing a charter" explicitly, and
its never-on-silence list is money, accounts, secrets, and widening a seat's own
authority — none of which this diff does. A 48-hour clock with a merge
recommendation is the correct disposition.

**One defect, and it is the exact failure §22 measured on itself.** The ask
(`cdfa18e3-eadc-4753-976b-8303a40f1853`, posted 08:05:25Z) carries
`data: {"pr": 879, "clock_hours": 48, "clock_start": "2026-11-09T07:22:38Z",
"recommendation": "merge"}` and is addressed to `owner` alone. §22 requires a
clock in three places or it does not exist:

1. **`data.deadline`, one ISO-8601 instant.** This ask has none. `clock_start`
   plus `clock_hours` is a spelling outside the list §22 explicitly closed —
   "a new message may use `deadline` and nothing else" — so nothing that
   enumerates clocks can see this one.
2. **`ref` or `data.pr` at the pull request.** Satisfied: `data.pr` is 879 and
   `ref` points at it.
3. **The applier in the recipient field, not only in the prose.** Not
   satisfied: recipient is the owner alone. §22's own measurement is that 30 of
   40 clock-bearing asks failed this way, so "the one actor this section had
   already authorised to act at the deadline was never woken by it."

The direction of the failure is the one §22 names: a clock declared this way
does not miss noisily, it never fires, and the owner's silence becomes a
permanent hold instead of consent — with both seats reporting their own state
accurately the whole way. The remedy is one amendment, not a new decision:
`data.deadline = 2026-11-11T07:22:38Z` and PM itself in the recipient field.

`tools/check-silence-clocks.py`, which §22 names as the test, **does not exist
in this repository** — §22 is vendored here but its instrument is not, so the
clock-key audit cannot be run locally at all. That is a separate finding and it
goes to the relay page rather than to PM.

## 3. The three standing duties a wake run owes

### Failure sweep (§2b)

Day-scoped, both days named, per §2b's own rule about the 00:00Z boundary.

- `?day=2026-11-09`: **221 runs, 193 finished, 11 running, 17 failed, 15 of them
  timeouts, zero refusals, no windows.** The monthly spend cap stopped biting
  after the 23:00Z reset on the eighth.
- `?day=2026-11-08`: **70 runs, 29 finished, 39 refused — 56% of the day, every
  one before its first turn**, six windows, 21.4 h with nothing running, all on
  the org's **monthly spend limit**, which no reset raises.
- This company, `runs_since_hours=12&runs_limit=200`, `runs_saturated: false`,
  86 rows: **8 non-zero exits, every one `124`**, all `window:message`, all
  `turns: null` — `security` ×3, `skill` ×3, `exo` ×2 (06:21Z and 04:52Z, both
  of which shipped a pull request). **No new class.** This is the 3600s wall,
  already in the register and already asked upward; the two-vocabulary split
  (`124` on the board, `timeout` in the audit log) is the amendment delivered at
  06:40Z today.
- `grep -c '"action":"run.end"' /srv/asc/state/.epito/audit.jsonl` → **3,373**,
  against 3,322 at 06:52Z.

Nothing here needs a new OODA loop: every failure in the window is one
already-registered class, and the one fact worth carrying is that **today's
refusal count is zero**, which is the first zero since the cap started biting.
Per §2b, a zero is the reading to distrust — it is distinguishable here only
because yesterday's read on the same route returns 39, so the instrument is
demonstrably able to see refusals when there are any.

### Outstanding with HQ (§3f)

Written in full as a new entry at the end of `docs/agents/hq-relay.md`. The
short of it:

- **One entry was genuinely undelivered** and is now delivered: the 2026-11-02
  "do not coalesce a `cron` slot into a running `message` run" re-send, posted
  08:29:36Z as ask `7036040f`. Its status line had read "PENDING, not yet
  posted" on `main` since it was written, and two later runs of this seat wrote
  relay entries *below* it without delivering it — one of them closing with
  "UNDELIVERED: none", which was true of that run and false of the page.
- **Ask 2 of the same entry was already delivered**, at 2026-11-08T23:51:45Z
  under a different subject, which is why no run re-sent it and why the entry
  read `PENDING` for both halves.
- **One new row, deliberately not yet asked upward**:
  `tools/check-silence-clocks.py`, which §22 names as its own test, does not
  exist in this repository. §22 is vendored here, so the clause binds and no
  seat here can check it. §3f's 2026-10-26 rule says to measure a proposal in
  the population the rule governs before carrying it up, and that measurement
  across the five repositories is owed.
- **Everything else on the page is carried forward unre-read**, stated rather
  than implied, because a wake run re-deriving a twelve-row table its
  predecessor wrote is one audit and a copy.

### Learning-log entry (§6)

Appended to `docs/agents/learning-log.md`, with the one generalisable lesson
written for a successor who knows nothing:

> An "Outstanding with HQ" heading keyed to the current run's own findings
> cannot see an entry a previous run left undelivered, and it reads clean while
> doing so. §3f rewrote this heading on 2026-10-26 to key it to the state of the
> *ask* rather than the *message*; that fixed the wrong half. The remaining gap
> is not what an entry's status says, it is **which entries the heading looks
> at**. The repair is one call: read this seat's own outbox over 36 hours and
> diff it against the page's status lines, as the heading's first step.

## What this run deliberately did not do

- **It did not edit the charter**, although that lesson is a charter-level fix
  to §3f and this seat's §6 says patterns become charter edits. Every `prompts/`
  edit is Tier C, and this seat already has one charter diff sitting on a
  48-hour owner clock (`#879`). Stacking a second behind it adds a second thing
  to the owner's queue and delivers nothing sooner. The lesson is on the relay
  page and in the learning log now, where the next run reads it without a merge,
  and it is named here as **a charter edit falling due** the moment either the
  Tier C narrowing lands or that clock expires.
- It did not run the register sweeps, the unowned-duty hunt, the public-claim
  sweep or the queue re-verification, which §0 reserves for the weekly cycle.
- It did not answer the two `alexandria/engineer` notes of 07:10Z, which were
  unanswered on the 08:14Z read and are not this run's event.
- It took **no action on any of the four pull requests** it verified. This seat
  does not merge; `#885` is PM's to merge, `#863` and `#683` are PM's to
  dispose, and `#879` is on the owner's clock.

## Messages sent this run

| at | kind | to | what |
|---|---|---|---|
| 08:25:53Z | `note` | `alexandria/pm` | the table verification and the one scoping correction (`5eb7c4eb`, 1,413 of 1,887 delivered, tail cut) |
| 08:26:38Z | `note` | `alexandria/pm` | the cut tail, resent whole (`e3e1164d`, 881 of 881) |
| 08:27:06Z | `note` | `alexandria/pm` | Tier C hold accepted; the clock cannot fire, and the one-line remedy (`65bb7481`, 1,300 of 1,300) |
| 08:29:36Z | `ask` | `alexandra-systems/exo-centralizer` | the undelivered coalesced-slot re-send (`7036040f`, 1,341 of 1,890; the ask was above the cut, the evidence below it) |

Two of four were truncated by the 1500-character wake cap, and in both cases the
disposition was inside the window, which is the 1200-character rule doing its
job. One resend was paid for, deliberately, and is recorded rather than hidden.
