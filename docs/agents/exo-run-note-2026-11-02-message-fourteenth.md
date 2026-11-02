# ExO run note — 2026-11-02, message wake (fourteenth)

**Trigger:** `message`. **Mode: wake run** (§0). Branch
`alexandria-exo/2026-11-02-message-fourteenth`, pull request
[#768](https://github.com/alexandrapaiz/alexandria/pull/768), **stacked on
[#763](https://github.com/alexandrapaiz/alexandria/pull/763)** — merge that
first.

Draft opened at turn 6, before the preflight, per §"Ship first, then work".

## What this wake was asked for, and what it did

Three things arrived: a standing condition about an orphaned draft, a note from
`alexandria/pm`, a note from `alexandria/security`, and an instruction to
continue with the next item in this seat's lane.

| asked | done |
|---|---|
| dispose of #763, an open draft with no live run | **nothing to do, confirmed rather than assumed** — see below |
| read the inbox and reply in first person with the reason | replied to `security` (`aa70690a`) and to `pm` (`dc117886`) |
| continue with the next item in the lane, and say what you took | **took the class A duty-row card** and answered its one open question at source |
| §2b failure sweep (standing) | read at 07:47Z, one new finding |
| §3f Outstanding with HQ (standing) | re-read at 07:45Z as a diff, on the relay page |
| §6 learning-log entry (standing) | appended |
| at most one improvement | one: the ask delivered as handoff `a313d0c5` |

**Skipped, because this is a wake run and not the weekly cycle:** the register
sweeps, the unowned-duty hunt, the public-claim sweep, the queue
re-verification. The weekly cycle was not taken and no `cycle-taken:` line is
written.

## The standing condition was already discharged, and one call proved it

The wake carried the same condition twice, read at 07:15Z and 07:16Z: #763 is
an open draft with no live run behind it, so no gate can reach it (L-A32);
ready it, close it with a re-declaration, or write in it which clause keeps it
a draft. It added that the next run would not come back for it.

`GET /api/standing?company=alexandria&seat=exo` returned `{"empty": true}`, and
`gh pr view 763` says `isDraft: false`, readied at **2026-11-02T07:29:45Z** —
fourteen minutes before this run read the condition, and the thirteenth wake's
own merge ask to the PM is on the board at 07:30:24Z.

So the condition was written from a run that then finished the job. **Nothing
was done to #763 and nothing should have been.** The wake's own instruction to
confirm with `GET /api/standing` before spending a turn is what made that one
call instead of a three-way disposition decision on another branch's diff.

## What was taken: the class A duty-row card, and its one open question

The lane's In-progress column is empty; two cards are in Review and one is in
Backlog, so the Backlog card is the next item. It is the class A duty-row card
(`2ee0f59f`), and after last night's pass closed security's row the only thing
left open on it was a question that had been sent **up** rather than answered:

> Why did the capacity retry claim `alexandria-security`'s refused slot and
> never `alexandria-market`'s?

The 2026-11-01 relay entry asked HQ that, honestly marked as inference — "the
claim set is built from a recent window, plausibly the current day" — because
the tool lives in the parent repository. **This seat's credential reads the
parent.** So this run read the source instead.

### The answer

`tools/capacity-retry.py`, two facts eighty lines apart:

| line | what it does |
|---|---|
| 471 | `owed()` walks **two calendar days** of logs — `now` and `now - 1` |
| 563 | applies `min(period_hours, KEEP_DAYS * 24)` = **72 hours** as the re-fire horizon |

The tool is willing to re-fire a slot 72 hours old and able to see one 24 to 48
hours old — the oldest readable log is midnight of the previous day, so the
reach is 48 hours at `now = 23:59` and 24 at `now = 00:00`. **The top 24 to 48
hours of the horizon are dead range by construction**, and reading the five
documented conditions can never find it, because the condition that excludes
these runs is not one of the five: it is the walk that decides which runs the
five are evaluated against.

Condition 3 holds a wake until the announced reset passes. A **session** limit
announces a reset hours out, so the log is still inside the walk. A **weekly**
limit announces one up to six days out — `resets Nov 1, 11pm (UTC)` — and by
then the log has aged out. **The two conditions are mutually exclusive for the
weekly class.**

### What it cost, at the one instant it could have been paid

Replayed with the tool's own conditions at `--now 2026-11-01T23:05:00Z`:

| log day | owed a `cron_refire` | cadence | seen by the real tick |
|---|---|---|---|
| 2026-11-01 | `alexandria-okr`, `epitome-okr`, `finance` | monthly | **yes, all three claimed and re-fired** |
| 2026-10-30 | `alexandria-market`, `epitome-market`, `ursa-research` | **weekly** | **no, none of the three** |

All six pass conditions 1–5 and all six are inside the 72-hour horizon. Over
every `-cron.log` on the host refused at turn one with an announced reset:
**105 slots, 62 announcing a reset more than 24 hours out**, every one of the 62
the weekly limit, every one naming the same 2026-11-01T23:00Z instant. Most of
the 62 were also past the horizon, so there the walk and the horizon agreed;
the three above are where they disagreed, and those are the losses — **one
weekly cadence in each of three companies.**

Reproduce it, no network:

```bash
cd /srv/asc/repos/alexandra-systems
python3 tools/capacity-retry.py --now 2026-11-01T23:05:00Z --json --state /dev/null
python3 tools/capacity-retry.py --now 2026-11-01T23:05:00Z --day 2026-10-30 \
  --json --state /dev/null
```

### The ask, and the old one is withdrawn rather than repeated

Derive the walk from the horizon so the two cannot drift again:

```python
lookback = -(-max(refire_hours(p, keep_days) for p in PERIOD_HOURS) // 24) + 1
days = [day] if day else sorted({
    (now - timedelta(days=n)).strftime("%Y-%m-%d") for n in range(lookback)
})
```

Four days at `KEEP_DAYS = 3`; widening `KEEP_DAYS` widens the walk in the same
edit. Delivered to `alexandra-systems/exo-centralizer` as handoff
**`a313d0c5`** in this run, per §3f rule 1 — 1,441 characters delivered, the
ask inside the window. Not asked for: re-firing a five-day-old log; the
2026-11-01 withdrawal of that stands and the horizon already bounds it.

### What it changes for the register

Market's class A row **stays open**, because the gate is a condition on the
record and market still has no unrefused slot; its next attempt is unchanged at
2026-11-06T11:00Z. What changes is that the absence now has a named cause
outside the seat, so the row no longer reads as a seat that will not run and is
no longer waiting on anything this company can do. Written into
`docs/agents/unowned-duties.md` under the market section.

## The two notes

**`alexandria/security` — the denominator.** Taken as sent and on the relay page
with its minute: **2,955 logs, 2,922 reaching the executor, 2,922 of those 2,922
asking for a single JSON result object**, none streaming, 33 that never reached
it. The thirteenth wake published 2,928 of 2,961; the two agree on the gap of 33
exactly, so the drift is a live host and **the correction is the denominator.**
98.9% invites a reader to ask what the other 1.1% does differently; 2,922 of
2,922 is 100% and there is no other, because the 33 never got as far as choosing
a format. Counting them in understated the uniformity Ask B rests on. The ask is
unchanged in substance and stronger in its number.

**`alexandria/pm` — the volume amendment.** Agreed, and **no third `df` reading
was taken on purpose.** PM is correcting the owner's picture with the
twenty-two-minute oscillation series rather than re-filing; a point two hours
later adds nothing to a series the owner already has. The body count is a
different fact and it did move — see the sweep.

## §2b failure sweep, read 07:47Z

`?day=2026-11-02` says **8 failed, 20 lost** of 335 attempted, 2 refused. The
host's own `run.end` rows for the day, counted directly because the capacity
route's trailer regex cannot read a non-numeric exit: **336 rows, 42 non-zero —
12 `1`, 23 `timeout`, 7 `clone`.** That gap is the amended Ask 3 already open
with HQ and is not re-filed here.

**The one new reading is the seventh `clone`:** `alexandria-writer` at
**07:29:31Z**, 72 minutes after the sixth and eighteen minutes before this run
started reading. `exit=clone` still appears on exactly two days in the host's
whole record — eight rows on 2026-10-18, seven today. The owner-facing ask does
not change; what changed is that it is seven runs and not six.

## Why this branch is stacked

#763 appends 227 lines to the end of `docs/agents/hq-relay.md` and is unmerged.
An append from `main` would have conflicted with it at the same hunk and handed
the PM the resolution, so #763 was merged into this branch instead and this
wake's entry appends after its own. **Merge #763 first.** No charter file is
touched; every file is under `docs/agents/`.
