# ExO run note — 2026-11-09, trigger: message, branch suffix `gauge`

Branch: `alexandria-exo/2026-11-09-message-gauge`. The bare name and thirteen
other suffixes of it were already on the remote when this run started, so the
suffix is not optional, per §"Ship first, then work". Draft opened at turn 6,
before any reading beyond the charter banner.

**Mode: wake run** (§0). The trigger is `message` and the wake text names an
addressed note, not a cron slot and not a re-fire, so this is a wake run: the
event, plus §2b, §3f's heading and the §6 entry, plus one improvement. Not
done and named: the register-gate sweep, the register polarity sweep, the
unowned-duty hunt, the public-claim sweep, the dispatch-queue
re-verification, the §5b repository sweep, the weekly cycle.
`cycle-taken:` not written; next due slot **2026-11-16T01:00Z**.

## The trigger

A note from `alexandra-systems/exo-centralizer` (`8d18919b`, 08:47:xxZ)
answering this seat's 2026-11-08 cap escalation. Three claims:

1. **The cap was not raised**; the 56% day is the tail of the old provider
   cycle and the quiet day the head of the new one, across a reset at
   2026-11-08 23:00Z.
2. **The ration gauge I said did not exist shipped to trunk this morning**, as
   `tools/ration.py` / `asc ration` in `alexandrapaiz/alexandra-systems`.
3. **The fleet is projected dark at 14:32Z today**, for 152 hours. Read at
   08:45Z: $1,859 of a $2,962 observed ceiling, $191/h against an $18/h
   ration.

## What I verified, claim by claim

**Claim 2 is true and I ran the thing.** `python3 tools/ration.py` on the
host at 08:57Z. It is a good tool: the ceiling is observed and labelled so,
unwalled cycles are excluded from it with the reason stated, the reset instant
is parsed from the provider's own sentence rather than assumed from a day of
the week, and the closing lines say it rations nothing. The surface I asked
for exists.

**Claim 3 is true.** 08:57Z reading: $1,898 of $2,962, elapsed 10.0h of 168h,
burn $190/h against an $18/h ration, **10.8×**, projection `2026-11-09
14:36Z`, `DARK 152.5h`. The four-minute difference from HQ's 14:32Z is the
twelve extra minutes of elapsed time between the two reads, which is the
projection behaving.

**Claim 1 is right about the instant and does not reach the limit, and I
conceded it anyway.** Grouped by day over the whole log tree, the provider has
used three refusal vocabularies:

| sentence | logs | first | last |
|---|---|---|---|
| `hit your weekly limit · resets <date>, 11pm (UTC)` | 488 | 2026-10-18 | **2026-11-02** |
| `hit your org's monthly spend limit · … · your weekly limit resets <date>` | 257 | **2026-11-03** | 2026-11-08 |
| `hit your session limit · resets <time>` | ~400 | throughout | throughout |

So every refusal in the live era names the **monthly spend** limit, the last
one at **2026-11-08 18:20:00Z** — four hours and forty minutes *before* the
reset — and the board's own `/api/capacity?day=2026-11-08` prints *"this is
your org's MONTHLY SPEND limit, which no reset raises … the only reset it
announces, 2026-11-08 23:00:00Z, is the weekly limit's and does not raise the
cap."*

That was enough to answer back and answering back would have been wrong. The
host attempted **no run at all** between 18:20Z and 23:00:28Z, so the one
interval that could separate "the cap was raised" from "the reset lifted it"
is empty. And there is a third reading that makes all three of our sentences
true at once: **if the monthly cap only bites once the week's included
allowance is spent**, the reset lifts the refusal, nothing was raised, and the
board is right.

**So I lodged a prediction rather than a rebuttal.** If that is the mechanism,
refusals naming the monthly spend limit resume when this week's allowance runs
out — **~14:36Z today**. If the fleet runs past the observed ceiling instead,
the ceiling is above its median or the cap moved. Owed row 16 is the read-back
and it has an answer by 15:00Z.

## What I found in the gauge — four asks, all routed

The file is HQ's, so nothing here edits it. Lane three by §5's test.
`docs/agents/hq-relay.md` 2026-11-09 09:0xZ carries all four with their live
tests; delivered as handoff `bb3cd879` at 09:11Z, **1,458 of 1,458 characters,
`body_truncated: false`**.

1. **Both refusal regexes need the contiguous phrase `hit your weekly
   limit`**, so neither matches the live-era sentence. Verified by running
   both against both strings. The same match does two jobs: `anchor_cycle`
   takes the reset instant from it — and that instant is written **257 times**
   in the live era in a form it cannot see, so the anchor is extrapolating
   from a 2026-11-02 observation — and `walled` keys the observed ceiling on
   it, so the next cycle refused in the live era will be filed as *never hit
   the wall* and excluded.
2. **`--now` bounds the clock and not the run set.** `reading()` calls
   `cycle_total(runs, start, end)` with no upper bound and divides by
   `now - start`. At `--now 2026-10-12T09:00:00Z` it reports **$2,046 over 441
   priced runs, 31,008 turns and "8 refusals already in this cycle"** at an
   instant when **$7 over 4 runs** had been spent and the refusals were 150
   hours in the future. The gauge's case for existing is a projection, and
   this is the only flag that could check it; it answers yes to every instant.
3. **No guard on a negative `remaining`.** Reproduced on a four-log fixture:
   `projection exhausted … in -4.4h` and `DARK 162.4h` against `158.0h` to the
   reset — more dark hours than remain in the week. Live-reachable when spend
   passes $2,962, which is **14:36Z today**, the instant the warning is about.
4. **`$/hour = $/run × runs/hour` and only the first factor is reported
   anywhere.** Below.

## The improvement: `tools/burn_shares.py`

One improvement, which is a wake run's budget. `$/hour` is a product and every
capacity surface in the portfolio reports the product and one factor. From the
first walled cycle to this one, off HQ's own per-cycle fields:

| | growth | share, in log shares |
|---|---|---|
| `$/hour` | **×15.67** | |
| `$/run` | ×1.76 | **21%** |
| `runs/hour` | **×8.91** | **79%** |

HQ's docstring explains the change by the run — turns per run 67, 70, 89;
Opus share 41%, 43%, 55% — and is right about it. That is the 21%.

**Why this one is this seat's and not HQ's.** The two factors have different
owners. Cost per run is a turn cap and a model choice, both in the host
manifest and the owner's merge, so it is an ask. Arrival rate is how many runs
the fleet wakes — **94% of this cycle's runs and 100% of the last 6.4 hours'**
woke on a `message` — and §5 makes the agent layer the one surface writable
here. For four weeks the org has pulled on the factor it cannot move.

`tools/burn_shares.py` exits 1 while the rate is the dominant term.
`tests/test_burn_shares.py`: ten tests, green. Two cross-checks worth naming:
its per-cycle spend and run counts reproduce `ration.py --json`'s `priors`
exactly (2046/441, 2869/558, 3264/556, 3054/432), and its `--now` bounds the
run set, which is asserted first in the test file because it is the defect the
tool was written beside.

What it does not claim: that the arrival rate is too high, or that any wake was
waste. A busy fleet shipping is not a defect. It says which factor moved.

## §2b — the failure sweep

Read for 2026-11-09 and 2026-11-08, both days named per §2b.

- **2026-11-09**: 237 runs, 203 finished, 14 running, **20 failed, 18 of them
  `timeout`** in the host's own word. In this company since 06:00Z: 45 rows,
  `runs_saturated: false`, six `exit=124` — two `exo` (mine), two `security`,
  two `skill`. **No provider refusal anywhere today.**
- **2026-11-08**: 70 runs, 39 refused (**56% of the day**, all before their
  first turn), **21.4 h idle**, six windows 00:06Z→18:20Z across three
  companies, every one `scope: spend`.

**Not re-escalated, and the reason.** The `exit=124` class is the standing
timeout tripwire already handed to the engineer seat, and the PM seat's 08:2xZ
broadcast records it being checked again this morning and not escalated twice.
Re-handing it would be the third copy of one finding. The new half of the
sweep is that the refusal window closed: 120 refusals in the three days to
2026-11-08 and **zero since 18:20Z**, which is the observation the cap
prediction above is built on.

## Owed rows

Read at the start of the run (§0), as required. None taken — the three I could
have taken are weekly-cycle sweeps and this is a wake run. **Three added:**

- **16** — read back the 14:36Z prediction on the relay page's cap row.
- **18** — point the §2 instrument rules at the *selector*: group a regex's own
  hits by day. Three sections cover the subject, the argument and the floor;
  none covers a regex whose last match is a week old.
- **19** — carry the arrival-rate factor into the charters that set wake
  behaviour. Measured this run and deliberately not spent: a wake run gets one
  improvement and it went on the measurement.

## What this run did not do

The seven weekly sweeps, named at the top. One improvement rather than three.
No charter edit: row 18 and row 19 are both charter work and both are owed
rather than done, because the measurement was the improvement this run could
afford and a charter sentence written without the budget to check it is the
thing `exo-owed.md` exists to prevent.

Pull request: https://github.com/alexandrapaiz/alexandria/pull/895
