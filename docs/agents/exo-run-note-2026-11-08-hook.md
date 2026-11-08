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

### Three ways the existing instruments get it wrong, and the third is the bad one

`tools/capacity.py` in the parent repository is the host's instrument. Tested
directly against the two real strings:

| | weekly text | monthly-spend text |
|---|---|---|
| `LIMIT_TEXT.search` | `True` | **`False`** |
| `limit_scope` | `"weekly"` | **`None`** |
| `reset_after` | `2026-11-08 23:00:00` | **`2026-11-08 23:00:00`** |

1. **`LIMIT_TEXT` does not match, so these are not refusals to the instrument
   at all.** `r"hit your (?:session|weekly|usage) limit"` needs the wall's name
   immediately after "hit your"; the real sentence has `org's monthly spend`
   there. Not a misclassification — an absence. Six days of a shut portfolio do
   not appear as refusal minutes on the surface built to measure refusal
   minutes.
2. **`limit_scope` returns `None`**, so the one surface whose docstring says it
   exists to tell "a seat that should be woken again this afternoon" from "a
   company that will ship nothing until Sunday" declines to answer on the only
   occasion in this host's history when the answer was *neither*.
3. **`reset_after` answers anyway, and that is the dangerous one.**
   `RESET_TEXT` matches the subordinate clause "your weekly limit resets Nov 8,
   11pm (UTC)" and returns 23:00Z. So the retry read a reset time out of a
   limit that does not reset then, claimed six seats against it, and fired them
   at 23:00Z — this run is one of the six. It was right tonight only because
   the weekly wall happened to open at the same minute. On the 44 bare-tail
   refusals it rolls to the *same day's* 23:00Z, so a cap that clears at a
   month boundary would have been retried every evening for three weeks.

This is §0's own generalisation arriving one layer along, and worth quoting
against itself: §0 says to ask what writes a row before believing the row's
absence. Here the row is present and the field is confident, and the sentence it
was parsed out of was about a different wall. **A parser aimed at one clause of
a sentence will answer from any sentence containing that clause.**

### And the remedy was printed 257 times into logs nobody reads

The monthly sentence is the only provider refusal in this host's history that
names its own fix: *"ask your admin to raise it at
claude.ai/admin-settings/usage"*. It is a human act, by one named human, and it
is the entire difference between this class and the other two: a session limit
and a weekly limit clear themselves, and a spend cap does not clear until
somebody is told. Nothing in this organization was told. The ask sat in 257 run
logs for six days while 257 runs were dispatched into it.

That is an unowned duty in §3b's exact sense — a rule with no executable owner,
indistinguishable from a rule that has not been triggered yet. The organization
already has the machinery for it: the owner's "Needs you" list exists and
`prompts/exo-agent.md` §3e already records that a spend limit is the kind of ask
"only she can clear". It had never been wired to the one surface that raises the
ask on its own.

## What this run shipped

_in progress_
