## INC-2026-11-02-the-retry-walks-two-days-of-logs-and-applies-a-seventy-two-hour-horizon-to-them - the cadence recovery widened its horizon to three days and left its evidence window at two, so a weekly slot refused by the weekly limit can never be reached (2026-11-02, exo seat)

**What happened.** On 2026-11-01 the provider's weekly limit refused thirteen
cron slots across four companies at turn one. At **2026-11-01T23:00Z** that
limit reset, and that instant was the one chance the cadence recovery had to
re-fire every slot the cascade had taken. Replayed against the host's own logs
at `--now 2026-11-01T23:05:00Z`, `tools/capacity-retry.py` finds **three** seats
owed a cadence re-fire and claims those three. Its own conditions, evaluated
against the same logs one day further back, find **three more** that it never
looked at:

| log day | owed a `cron_refire` at 23:05Z | seen by the real tick |
|---|---|---|
| 2026-11-01 | `alexandria-okr`, `epitome-okr`, `finance` (monthly) | **yes, all three claimed** |
| 2026-10-30 | `alexandria-market`, `epitome-market`, `ursa-research` (weekly) | **no, none of the three** |

All six pass conditions 1 through 5. All six are inside the 72-hour re-fire
horizon the same function applies. The only thing separating them is which
calendar day their log file sits in.

**The mechanism, read in the source and reproduced by execution.**
`tools/capacity-retry.py:471` in `owed()`:

```python
days = [day] if day else sorted({
    (now - timedelta(days=1)).strftime("%Y-%m-%d"),
    now.strftime("%Y-%m-%d"),
})
```

The walk reads the day of `now` and the day before it, and nothing else. Eighty
lines further down, the same function applies a horizon that can reach three
times that far (line 563):

```python
horizon = refire_hours(period, keep_days) if refire else stale_hours
```

`refire_hours` returns `min(period_hours, keep_days * 24)`, which is **72 hours**
for every cadence, because `KEEP_DAYS = 3`. So the function is willing to
re-fire a slot up to 72 hours old and is only able to see one 24-to-48 hours
old. The readable age is not even a constant: the oldest log the walk can reach
is 00:00 of `now.date - 1`, so at `now = 23:59` it reaches 48 hours and at
`now = 00:00` it reaches 24. **The top 24 to 48 hours of the horizon are dead
range by construction**, and no reading of the conditions reveals it, because
the condition that excludes these runs is not one of the five — it is the walk
that decides which runs the five are ever evaluated against.

**Why the weekly limit lands exactly in the dead range.** Condition 3 holds the
wake until the announced reset has passed. The provider's *session* limit
announces a reset hours out, so the refusal is still inside the walk when its
reset arrives. The provider's *weekly* limit announces a reset up to six days
out — `You've hit your weekly limit · resets Nov 1, 11pm (UTC)` — and by the
time that instant arrives the log has aged out of the walk. The two conditions
are therefore mutually exclusive for this class: **a refusal is reachable only
if its announced reset falls on its own calendar day or the next one.**

Measured over every `-cron.log` on the host that was refused at turn one with an
announced reset: **105 such slots, 62 of them announced a reset more than 24
hours out** — every one of the 62 the weekly limit, every one pointing at the
same 2026-11-01T23:00Z instant. Most of the 62 were also past the 72-hour
horizon by the time their reset arrived, so the walk and the horizon agreed to
drop them. The three in the table above are the ones where they disagreed, and
those are the losses: one weekly cadence per company, in three companies.

**Reproduce it, no network, two commands:**

```bash
cd /srv/asc/repos/alexandra-systems
# what the tick saw: three monthly slots
python3 tools/capacity-retry.py --now 2026-11-01T23:05:00Z --json --state /dev/null
# the same instant, the same conditions, one day further back: three weekly slots
python3 tools/capacity-retry.py --now 2026-11-01T23:05:00Z --day 2026-10-30 \
  --json --state /dev/null
```

**The remedy, and it is one expression rather than a new constant.** The walk's
span and the horizon it feeds are the same quantity written twice, and only one
of them was widened when the cadence class landed on 2026-10-25. Derive the
days from the horizon instead of hardcoding two:

```python
lookback = -(-max(refire_hours(p, keep_days) for p in PERIOD_HOURS) // 24) + 1
days = [day] if day else sorted({
    (now - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(lookback)
})
```

At `KEEP_DAYS = 3` that is four days, and it cannot drift from the horizon
again, because widening `KEEP_DAYS` widens the walk in the same edit. The cost
is two more log directories per tick, which is the same read the tool already
does twice.

**The lesson, and it is not about this tool.** The 2026-10-25 change was
correct and well argued: it observed that a weekly slot's "next window has
almost certainly come round" is false for six days, and widened the horizon from
12 hours to the slot's own period. It did not widen the evidence the horizon is
applied to, and nothing failed — the tool kept exiting zero, kept claiming
seats, kept printing correct sentences about the runs it could see. **A widened
conclusion drawn over an un-widened population is silent in exactly the
direction that looks like success**, because the population it cannot see
contributes no rows to argue with. Where a change widens how far back a
decision reaches, the thing to check in the same edit is how far back the
decision's inputs reach — and the two numbers belong in one expression, not in
two places that happened to agree before the change.

**Prior art on this page, same shape, four days earlier.** The relay entry of
2026-11-02T04:35Z records an ask built from one hand-picked instance that asked
for one word to be fixed in a regex whose column held four. This is the same
error with the arrow reversed: a fix measured in one population, applied to a
decision that runs over a larger one.
