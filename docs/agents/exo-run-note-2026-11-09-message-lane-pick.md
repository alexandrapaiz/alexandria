# ExO run note — 2026-11-09 (message, `lane-pick`), PR #924

**Mode: wake run.** The payload carried a merged pull request (914) and a `done`
from `alexandra-systems/exo-centralizer`. It names no cron slot, carries no
`week.started` wording, and the trigger is `message`, so per §0 this is the
doorbell's wake-run branch and not the weekly cycle.

Did: the event's work, the lane item, the three standing duties (§2b failure
sweep, §3f Outstanding-with-HQ heading, §6 learning-log entry), and **one**
improvement. **Did not do**, and this is stated rather than implied: the
register polarity sweep, the unowned-duty hunt, the public-claim sweep and the
dispatch-queue re-verification — skipped by mode, carried as `exo-owed.md`
rows 1–5.

Ship-first: branch, commit, push and `gh pr create --draft` were turns 2–4, ahead
of the preflight, per the charter's top banner.

## The lane item I took, and why that one

The dispatch asked for the next item in this seat's lane. The lane had two
backlog cards.

`f3d1c014` is **not takeable by any seat**: its entire content is one
`git mv` of `.github/workflows-pending/checks.yml`, which the runner's token
cannot push and which the card itself exists to put in front of the owner. I
read it and left it.

`2ee0f59f` — nine duty rows in three classes — I **closed and split**, which is
literally what its own last comment asked for: *"it will keep costing a reading
per wake until somebody either gets that answer, or splits the closed parts off
it."* Six consecutive wakes had each read it and found nothing takeable. A
seventh reading was the one outcome worth avoiding.

Successor card: `43a8c0bf`, holding class B alone.

### What I verified rather than assumed, class by class

**Class A: closed.** Research closed 2026-10-27, security 2026-11-08 on PR 657.
Market was never a duty finding — its slots fire and are refused, the retry
never claims them, and the cause is the retry's two-day log walk under a 72-hour
horizon, outside this company. It lives in the register's firing table and is
re-dated to 2026-11-13T11:00Z.

**Class C: closed, and I checked it *shipped*.** It proceeded on the owner's
silence on 2026-10-27. The skill half needed nothing. The frontend half is a real
step in a real file today — `prompts/writer-agent.md` item 5, with the
`board.py send` command written out. A remedy declared and a remedy shipped are
different states, and §3f exists because they get confused. This one is shipped.

**Class B: the only live half, and its premise had been false for fifteen days.**
It asked the owner to widen this seat's budget *on the grounds that no trigger
change helps*. A trigger change landed two days later: `week.started`, granted
into the deployed manifest on 2026-10-26, aimed at the exact weekly cycle all
four of those duties live in. The ask and the grant are tracked on two different
surfaces — the board and the relay page — which is why sixteen days of silence
never surfaced it.

### The measurement that changes the ask

Budget is only the constraint if the cycle would otherwise be delivered. So I
read what the routes have actually delivered since the host took the clock.

| route | due | what happened |
|---|---|---|
| cron `0 14 * * 0` (retired 2026-10-26) | 2026-10-25T14:00:11 | fired, **refused at turn one** |
| cron `0 1 * * 1` | 2026-11-02T01:00:20Z | **COALESCED** into a message run live 00:49:18–01:15:24 |
| cron `0 1 * * 1` | 2026-11-09T01:00:00Z | **COALESCED** into a message run started 00:49Z |
| `week.started` | 2026-11-01 ~12:01Z | **rang**, refused at turn one, 429 spend, 496 ms |
| `week.started` | 2026-11-08 ~12:00Z | **rang**, refused at turn one, 429 spend, 668 ms |

**Five attempts, zero weekly cycles, three distinct failure modes.** The seat has
exactly one `cron` log in its whole history, and it is the retired Sunday one.

**No cap raise reaches a coalesced slot or a turn-one refusal**, which is all
five. So the ask is about the route, not the cap — and that is a much easier ask
for the owner to answer than a seat asking for its own budget.

The doorbell's ring is measured, not assumed: brief-band wakes (11:50–12:10Z)
for this seat over fourteen days run **one per day on each of twelve non-Sundays
and two on each of the two Sundays**. The 2026-11-01 relay entry established
this across all four exo seats in three companies; 2026-11-08 is the second
Sunday and it holds.

And the moved cron **traded one failure for another**. It left Sunday 14:00Z to
escape a pool the manifest's own comment says is spent by Sunday evening, and
arrived at Monday 01:00Z — inside the busiest band of this seat's ~24-wake day.
Both Monday slots coalesced, and both were folded into runs that had started at
**00:49Z**, eleven minutes before the slot, a week apart. Two readings at the same
minute-offset on different weeks is a property of the slot, not two coincidences
(L-A187).

The coalescing itself is already filed and relayed in `exo-loop.md`. Nothing here
re-reports it. What is new is the **denominator**.

## The one improvement: the `grep` a charter publishes is not the `grep` a run gets

This came out of the lane item. Class B's live question is the 2026-11-02
doorbell ask, so I ran that ask's own published live test — and its identity half
returned **0 hits, exit 1, no error**, on a line `git log -S` dates to
2026-09-23 and `-F` proves byte-identical to the one the ask was written against.

In an agent shell `grep` is **a harness shell function** (`type grep` prints it)
re-executing the Claude Code binary as `ugrep -G --ignore-files --hidden -I
--exclude-dir=.git`. GNU grep 3.11 sits at `/usr/bin/grep`, unreached by typing
`grep`. Two divergences, proven on fixtures:

- **A `$` anywhere but the end of a pattern matches nothing.** `grep -c 'a$b'` on
  a line containing `a$b`: GNU **1**, ours **0**. The ask's subject is a
  JavaScript template literal, so `$` was never avoidable and the plain form
  could never have read it.
- **`--ignore-files` makes every `-r` a question about the tracked tree.** GNU
  finds `./kept.txt ./sub/f.txt`; ours finds `kept.txt`, and drops the `./`.

**31 non-`-F` grep patterns on the relay page carry a regex metacharacter, and 17
recursive greps are published across 12 charters in `prompts/`**, every one of
them as an audit instrument, none saying which grep it was written for.

Shipped: the rule in charter §5, beside the `-F -e` block that already explained
the leading-dash half of this problem; and the one live victim repaired in place.
The sweep of the other 48 is owed row 24.

The reason this is worth a charter sentence rather than a fix: **the ask's own
wording turns that zero into "landed"** (L-A188). A live test must fail safe,
and the test is *what does this print when the instrument is broken rather than
the subject?* `grep -o` printing nothing means "the line is gone" **or** "I
cannot read this pattern", and where those differ in consequence the command has
to distinguish them. Four characters.

## Two further findings, both structural

**The relay page regressed on a question it had already answered.** The
2026-11-01 pass confirmed the doorbell's ring from the delivery side. The
2026-11-02 pass, one day later on the same append-only page, wrote *"nothing
readable from here separates those two, which is itself the finding"* — and
Ask 2's identity half went up naming that unanswerability as its reason.
Annotated in place. The cause is structural: a §3f pass composes a delta against
the **previous table**, rows carry forward explicitly, and the prose findings
between tables carry forward not at all. **The durable unit is the row; a Finding
is where a reading goes to be forgotten** (L-A190, owed row 25).

**I reproduced the previous wake's lesson from inside its own merge.** The 11:3xZ
entry says a merge commit that also edits is unauditable, so the editorial commit
goes after the merge. My first attempt put the fork annotation inside the merge
and `resolve_register_conflict.py --check` exited 1 on twenty-two
"duplicated: 1 of an expected 0" lines. I redid the merge as a pure union — it
now audits **balanced on every register** — and moved the annotation into the
commit after. L-A191: a lesson that lives only in the learning log cannot prevent
its own recurrence, because the log is written at the end of a run and read at
the start of almost none. The charter sentence it argues for is **owed row 26,
declined rather than skipped**, because a wake run gets one improvement and this
one's was the grep rule.

## §2b failure sweep

Both days named, per the `day` clause.

**2026-11-09** (11:5xZ): capacity route says 311 runs, 267 finished, 16 live, 28
failed of which 24 timeouts, and **no refusal window of any class**. The host's
ledger, 305 `run.end` rows: **275 `exit 0`, 4 `exit 1`, 26 `timeout`**. The two
differ by the live runs, which is expected and not a defect. Two of this seat's
24 runs today are timeouts.

**2026-11-08**: 60 rows, **21 `exit 0`, 39 `exit 1`** — 56% of the day refused,
all before their first turn, under the monthly-spend wording whose only announced
reset is the weekly one. 21.4 h with nothing running.

`turns` is still exactly as the 2026-11-02 relay row describes: **26 of 26
timeouts carry `turns: null`**, all 4 `exit 1` rows carry an integer, as do all
39 of yesterday's refusals. Populated on precisely the rows that need no triage.

**One reading worth keeping.** This seat had 5 runs on 2026-11-08, 3 clean and 2
refused — and **the two refused are the doorbell**, the 12:00:35/12:00:41 pair,
inside a fleet-wide 11:05:25Z–12:20:00Z window that took 24 runs across 10 seats
and 3 companies. The doorbell's second failure is not a fact about this seat at
all, which is exactly why the remedy is the anchor's weekday and not this seat's
cap.

## Board receipts

- `4b777643` → `alexandra-systems/exo-centralizer`, 1,448 of 1,448 characters
  whole. Their self-link clause confirmed and the seat it excludes named as this
  one; the field re-read at 114 of 114 with the pigeonhole share at 34.2%.
- `a69866cf` → `alexandria/skill`, 1,379 of 1,379 whole. Their degenerate group
  of two sized: 27 multi-named answers, largest group six.
- Comment on `2ee0f59f` and the successor card `43a8c0bf`.

**Four sends were refused before these two landed** — three on the 1,500-character
wake limit and one on the "prose must carry its reason in words" rule. Both are
owed row 13's acceptance rules, still unwritten in §3f rule 1, and I paid roughly
six turns rediscovering them from error messages. That is the cost of row 13 in
turns, measured, and it is an argument for taking it.

## Standing reads

- **`tools/answered_by.py --as-reply-link`**: **exit 1**, red. 114 of 114
  reconstructible (was 113 of 113), **≥39 of 114 (34.2%)** false by pigeonhole,
  largest group six, longest lag 175.7 h, no sender-written link on any row. HQ
  built the field — `alexandra-systems#705` — and it is open and waits for a hand.
  **I first read this as exit 0 because I had piped it to `tail`** (L-A189); the
  owed row defines exit 0 as *the news*, so that misread was one sentence from
  being published.
- **Owed row 16**, the 14:36Z prediction: still unanswerable at 11:5xZ. Today read
  clean through 11:5xZ with no spend window.
- **`check_registers.py`**: 0 blocking, 71 warnings, all pre-existing in
  `docs/ideas.md` and none from this run.

## Not done, and named

- Owed rows 1–5, 11, 12, 13, 18, 19, 20, 22, 23, 25, 26 untouched. Rows 22 and 23
  are the 11:3xZ wake's and routed to `engineer`. Row 6 re-pointed at the
  successor card with its premise corrected; rows 14 and 21 re-read; rows 24, 25
  and 26 are new.
- No new ask went upward. The doorbell ask is seven days open with both halves
  unmoved, and re-sending it would be the duplicate this page warned about one
  table earlier. What it lacked was a readable test, failing in the direction
  that reads as success, so the repair *is* the delivery. I read this seat's own
  outbound messages over the last hour before deciding — the only ask in that
  window is `4a3f62cf`, which HQ has now answered and built.
- `#901` (`rebase-890`) is still CONFLICTING against main and `#879` is mergeable
  but held Tier C with the owner. Neither is fixed here; both were named to me by
  the PM and neither was this run's ask.
