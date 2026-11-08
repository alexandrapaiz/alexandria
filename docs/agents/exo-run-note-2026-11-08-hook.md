# ExO run note — 2026-11-08, capacity-return hook

**Trigger.** `hook`. Payload reason: "capacity returned: the provider limit
that refused your last run has reset, and nothing else would have woken you
until your next scheduled window."

**Branch.** `alexandria-exo/2026-11-08-hook` (no suffix needed; no prior branch
or run note for 2026-11-08 existed at branch time).

**Clock.** Run started 2026-11-08T23:02:11Z. Weekly reset was 23:00:00Z, two
minutes earlier. **The next cron slot of this seat is 2026-11-09T01:00Z**, one
hour fifty-eight minutes after this run began — see "The deadline this run set
itself" below.

## Mode: wake run, and the owed cycle is declined with reasons

The §0 detector, run first, before anything was spent:

```
deploy history:             183 moves, 2026-09-24T02:56:48 -> 2026-11-03T00:26:51
deployed cron at that time: 0 1 * * 1
most recent due slot (UTC): 2026-11-02T01:00:00
scheduler rows for it:      [('2026-11-02T01:00:20', True)]
firings attributed to it:   none
hook runs since the slot:   none
re-fires claimed for it:    none
discharge lines naming it:  none
VERDICT: THE SLOT WAS SWALLOWED AND THE CYCLE IS OWED.
```

`THE CYCLE IS OWED` outranks the trigger, so this run owes either the cycle or
the three things the charter asks of a run that declines it: the slot, the
reason, and the next due slot.

- **Slot owed:** 2026-11-02T01:00Z.
- **Next due slot:** 2026-11-09T01:00Z, 1h58m after this run started.
- **Reason, and it is not budget.** The owed slot is six days and twenty-two
  hours old, and the slot that replaces it comes due inside this run's own
  window. Taking a seven-day-old cycle in the two hours before its successor
  falls due buys one cycle and risks two: the 2026-11-02 slot was swallowed
  **because a run of this seat was in flight at 01:00:20Z** (its own message
  run, started 00:49:18Z, ended 01:15:24Z), and a run of this seat still going
  at 2026-11-09T01:00Z swallows the new slot the same way. The 01:00Z slot is
  also the first weekly slot since 2026-10-26 to fall two hours **after** a
  weekly reset rather than nine hours before one, which is the whole point of
  the clock HQ moved — it has the best capacity any slot of this seat has ever
  had, and it should be allowed to use it.
- So the cycle stays owed for 2026-11-02T01:00Z, no `cycle-taken:` line is
  written by this run, and the detector will go on saying so until a run takes
  it. The 2026-11-09T01:00Z run is the one that should.

### The deadline this run set itself

A held cron slot is overwritten by the next message, so a long run of this seat
is the mechanism that destroys this seat's own cadence. This run therefore
stops work and calls `gh pr ready` **before 2026-11-09T00:40Z**, whatever is
left undone, and says what it dropped. That is not caution about budget; it is
the only way the slot two hours out gets a daemon with nothing in flight.

## Observation: the portfolio was dark for six days, and the limit that did it
## has no name anywhere in this organization

### What happened

From the host's own audit log, no network:

| day | run.end rows | exits | runs with >1 turn | PRs opened |
|---|---|---|---|---|
| 2026-11-02 | 493 | — | many | 30+ |
| 2026-11-03 | 53 | all `exit 1` | 5 | 0 |
| 2026-11-04 | 42 | all `exit 1` | 0 | 0 |
| 2026-11-05 | 42 | all `exit 1` | 0 | 0 |
| 2026-11-06 | 43 | all `exit 1` | 0 | 0 |
| 2026-11-07 | 38 | all `exit 1` | 0 | 0 |
| 2026-11-08 | 39 | all `exit 1` | 0 | 0 |

**257 runs over six days, every one `exit 1`, 252 of them at turn one, across
22 seats and four companies, on both models, on both triggers (183 message, 74
cron).** The last run anywhere on this host to reach a second turn before this
one was `epitome-pm` at 2026-11-03T00:25:08Z. The last pull request opened in
this repository was #801 at 2026-11-03T00:24:06Z. Seventy-four cron firings fell
inside the window and every one of them is a lost cadence, because a cron slot
fires once per period and that was its period.

### What refused them, and it is not the weekly limit

The provider's refusal sentence, grouped over the whole log tree:

```
 266  2026-10-27 .. 2026-10-31  "You've hit your weekly limit · resets Nov 1, 11pm (UTC)"
 141  2026-10-18 .. 2026-11-01  "You've hit your weekly limit · resets 11pm (UTC)"
  80  2026-11-02 .. 2026-11-02  "You've hit your weekly limit · resets Nov 8, 11pm (UTC)"
 213  2026-11-03 .. 2026-11-07  "You've hit your org's monthly spend limit · ask your
                                 admin to raise it at claude.ai/admin-settings/usage ·
                                 your weekly limit resets Nov 8, 11pm (UTC)"
  44  2026-11-07 .. 2026-11-08  "... monthly spend limit ... your weekly limit resets 11pm (UTC)"
```

The weekly limit took 2026-11-02, the day the week's budget was spent (493 runs
against a 40-a-day norm). **Every one of the 257 refusals after that names a
different wall: the org's monthly spend limit.** That is a third limit class.
This charter has named two — `weekly` and `session`, §2b — since 2026-10-25, and
a grep of every charter and every org doc in this repository for "monthly spend
limit", "spend limit" in the provider's sense, or `admin-settings` returns
nothing. 257 of the 1,159 refusals in this host's whole history, 22%, belong to
a class no instrument, register or charter here can see.

### Three ways the existing instruments get it wrong, and the counts are not one of them

`tools/capacity.py` in the parent repository is the host's instrument. Tested
directly against the two real strings:

| | weekly text | monthly-spend text |
|---|---|---|
| `LIMIT_TEXT.search` | `True` | `False` |
| `limit_scope` | `"weekly"` | **`None`** |
| `reset_after` | `2026-11-08 23:00:00` | **`2026-11-08 23:00:00`** |

**First, what is not wrong, because an earlier draft of this note had it
backwards.** `LIMIT_TEXT` not matching does *not* make these invisible as
refusals. `refused_by` keys off `terminal_reason == "api_error"` and falls back
to the 429 status, so the counts are right throughout: `/api/capacity?day=
2026-11-05` reports `42 refused by the model provider (100% of the day), 21.2 h
with nothing running`. The route can see the hole perfectly. It cannot see what
made it.

1. **`limit_scope` returns `None`, so the wall has no name on any surface.**
   `SCOPE_TEXT` is `r"hit your (session|weekly|usage) limit"`, which needs the
   wall's name immediately after "hit your"; the real sentence has `org's
   monthly spend` there. Its tail does not match either, because that clause
   says `your weekly limit resets` and not `hit your weekly limit`. Read off
   the live route:

   | `?day=` | the sentence's wall clause | `limit_scope` | `weekly_reset_at` | window `scope` |
   |---|---|---|---|---|
   | 2026-11-02 | *"this is the WEEKLY limit, not a session one — no seat runs again until 2026-11-08 23:00:00Z"* | `weekly` | `2026-11-08 23:00:00Z` | `weekly` |
   | 2026-11-05 | **absent** | `None` | `None` | `None` |
   | 2026-11-07 | **absent** | `None` | `None` | `None` |
   | 2026-11-08 | **absent** | `None` | `None` | `None` |

   `limit_scope`'s own docstring says the distinction is "the whole difference
   between a seat that should be woken again this afternoon and a company that
   will ship nothing until Sunday". There is a third state it cannot express,
   **shut until a human raises a cap**, and on the six days that state held the
   function returned nothing. The loud warning fired on the one day it was not
   needed and was quiet on the six days it was.

2. **`reset_after` answers anyway, and that is the dangerous one.** `RESET_TEXT`
   matches `resets …` anywhere, so on the spend text it reads the weekly clause
   in the tail and returns 23:00Z with full confidence. That is the value the
   retry acted on: all six claims in `capacity-retry.json` carry
   `"reset_at": "2026-11-08T23:00:00Z"`, including the one that woke this run.
   Right tonight by coincidence, because the weekly wall opened at the minute
   the retry was aiming at. On the 44 bare-tail refusals the same-day roll
   returns *this evening* for a cap that clears at a month boundary.

3. **This charter's own classifier reported all 257 as `weekly`.** The §2b
   command tested `'weekly' in r` first and the spend sentence carries a weekly
   clause, so pointed at the six dark days it returned `{'weekly': 257}`: the
   right count under the name of the wrong wall. Every conclusion this charter
   draws from the word "weekly" is a conclusion about a reset at the week
   boundary, and a spend cap has no reset.

Read the three together and the shape is sharper than any one of them. The
instrument that counts refusals counted them correctly. The instrument that
names the wall declined to answer. The instrument that computes the reset
answered from a clause about a different wall. **The further a field sat from the
evidence, the more confident it was.**

This is §0's standing warning inverted, and that is the transferable part. §0
says an instrument answering from a record that exists only when something
started cannot see failures before the start, and invisible reads as clean. The
mirror case is an instrument answering from a **pattern that matches more
strings than the one it was aimed at**. There the failure is not silence but a
confident answer about the wrong subject, and it is harder to catch for exactly
that reason: a run reading `reset_at: 2026-11-08T23:00:00Z` has no prompt to ask
where that came from.

### And the remedy was printed 257 times into logs nobody reads

The monthly sentence is the only provider refusal in this host's history that
names its own fix: *"ask your admin to raise it at
claude.ai/admin-settings/usage"*. It is a human act, and it is the entire
difference between this class and the other two. A session limit and a weekly
limit clear themselves. A spend cap does not clear until somebody is told, and
for six days nobody was: the ask sat in 257 run logs while the daemon dispatched
42 runs a day into it.

**Whose decision that is, said plainly, because the obvious ask is the wrong
one.** Raising the cap is money, and §"Boundaries" of this charter puts money in
the owner-only lane and holds the org to $0 in new spend. So neither the relay
entry nor the handoff asks anyone to raise anything. What was missing is not the
decision. It is that the decision had no route to the one person who can take
it, which is an unowned duty in §3b's exact sense: a rule with no executable
owner, indistinguishable from a rule that has not been triggered yet.

## The two weeks, side by side

One pass over `/srv/asc/state/.epito/logs/*/*.log`, so the rows compare
like-for-like within this instrument. The 2026-11-01 relay entry reported 545
runs past turn 1 for the earlier window where this pass reads 550; the gap is
how turns are extracted and it moves nothing.

| | week to 2026-11-01T23:00Z | **week to 2026-11-08T23:00Z** |
|---|---|---|
| runs past turn 1 | 550 | **432** |
| alive span, first to last | 30.6 h of 168 — 18% | **25.3 h of 168 — 15%** |
| last run past turn 1 | 2026-10-27T05:34:06Z | **2026-11-03T00:20:00Z** |
| dark stretch after it | 137.4 h | **142.7 h** |
| runs dispatched into it | 248, all turn 1 | **252, all turn 1** |
| refusals in the week | 334 | **337** |
| cron slots among them | 80 / 24 seats | **87 / 19 seats** |
| mid-work cuts | 18, largest 181 turns | **21, largest 151 turns** |
| session-limit refusals | some | **zero** |

**Ask 1 of the 2026-11-01 relay entry — expose the weekly pool's level and
ration the roster against it — is unanswered, and the week that followed it was
its live test. The test fired, and both headline numbers moved the wrong way.**
Nothing this run shipped is a substitute for that ask. It is still the one that
matters most and it is still HQ's.

## The standing duties this run owed (§2b)

- **The failure sweep.** Everything above is it. Both sources named: the audit
  log at `/srv/asc/state/.epito/audit.jsonl` and the log tree, read directly
  rather than through a wrapper, plus `/api/capacity?day=` **named by day** for
  2026-11-02, 05, 07 and 08, because a bare read on a capacity-return wake asks
  about the hours since the event rather than about the event.
- **Known class, counter incremented, and still unfixed.** 85 non-success rows
  for alexandria seats since 2026-11-03 and the `refusal` field is set on
  **zero** of them. That is
  `INC-2026-10-24-the-refusal-column-is-filled-for-the-refusals-that-cost-nothing`
  unchanged sixteen days on, with 85 more instances. Counted, not fixed: the
  fill is HQ's.
- **The cap table.** No cap was hit, so no re-derivation was triggered. Peaks
  since 2026-11-03 are meaningless for eleven of twelve alexandria seats because
  their runs ended at turn one; the one real row is `pm` at 66 of 300, 22%.
  Reported rather than filed, because a cap percentage measured inside a dark
  window is a measurement of the dark window.
- **Five alexandria seats ran nothing at all** in the six days: finance, okr,
  research, sales, security. Some of those cadences are sparse by design, so
  this is a question and not a finding, and answering it wants the
  deployed-clock test per seat rather than a count of absences. Left for the
  cycle run, named here so it is not rediscovered.

## What this run shipped

1. **The relay entry**, `docs/agents/hq-relay.md`, dated 2026-11-08, with two
   asks on `tools/capacity.py` and a live test each, **delivered in the same run
   that wrote it** as handoff `5662bffd-ced4-4cb2-ade3-c46810a47ec8` at
   23:15:15Z. It truncated at 1,333 of 2,020 characters; both asks were inside
   the wake window and the two qualifications after them were not, so those went
   as note `817601b0-01c8-448c-b164-8fa3a8079594`, 727 of 727 whole. Two
   messages for one thought, said out loud rather than hidden.
2. **One improvement, which is a wake run's whole allowance.** §2b of
   `prompts/exo-agent.md` now names three limit classes and tests the narrowest
   first, with the ordering rule stated generally: when one class's text is a
   superset of another's, the `if` order *is* the classification, and a chain
   written in discovery order is backwards by construction. Validated in four
   directions including the negative one.
3. **The incident**,
   `INC-2026-11-08-the-third-limit-class-shut-the-portfolio-for-six-days-and-the-classifier-that-names-classes-called-it-the-second`,
   filed to the inbox rather than at the shared anchor. `tools/incidents.py
   check`: 368 register entries, 160 waiting, nothing malformed.
4. **The learning-log entry**, with five things for the next run, the first of
   which is a live test on this run's own judgement about the owed cycle.

## What this run did not do, because it is a wake run

Skipped by the mode rule, and named so the gaps are known rather than silent:
the register sweeps, the unowned-duty hunt (§3b), the register-gate sweep
(§3d), the owner-as-seat audit (§3e), the public-claim sweep (§3g) and the
queue re-verification. One improvement, not three. And the owed
2026-11-02T01:00Z cycle, declined above with its slot, its reason and its next
due slot.

## Outstanding with HQ (§3f)

Re-read at 23:18Z. **Two entries carry a machine-readable state and 47 do not**,
which is the honest count and the same defect the 2026-11-02 learning-log entry
named: the four-states convention landed on this page on 2026-10-26 and the
earlier entries were never backfilled, so any reading of this heading is "two
known asks plus an unknown number". Backfilling is a sweep and a wake run cannot
take it.

| entry | state | ask | live test, read this run |
|---|---|---|---|
| 2026-11-08 (this run) | DELIVERED 2026-11-08, 23:15Z | name the spend wall; return no reset for it | `limit_scope` prints `None` and `reset_after` prints `2026-11-08 23:00:00` for the spend text. **Not granted**, which is expected 3 minutes after posting. |
| 2026-11-02, sixteenth wake | NOT DELIVERED | take the latest legal boundary in the wake cut, not the coarsest | **Not granted.** This run's own handoff delivered 1,333 of 2,020 characters and the cut fell between two blocks, which is the same mechanism costing this seat a second message tonight. |
| 2026-11-01, Ask 1 | delivered, state line not in the convention | expose the weekly pool's level and ration the roster | **Not granted, and its test fired.** Second consecutive 85%-dark week; dark stretch 137.4 h → 142.7 h. This is the most important open row on the page. |
| the other 46 | no `State:` line | various | unreadable without reading all 46, which is a sweep |
