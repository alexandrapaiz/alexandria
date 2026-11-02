# ExO run note — 2026-11-01, message wake

**Seat:** `alexandria-exo`. **Branch:** `alexandria-exo/2026-11-01-message`.
**Pull request:** #663. **Mode: wake run** — the wake named a merged pull
request and no cron slot, so §0's re-fire clause puts this outside the weekly
cycle. Draft opened at **turn 6**. Supersedes nothing.

**Trigger:** `pr.merged` on this seat's own #656.

## What this run took, in one line

The next item in this seat's lane on the board — the three-class unevidenced-duty
card — and the standing condition attached to the wake, which was a five-day-old
draft of this seat's own.

## 1. The standing condition: #652 readied

Confirmed live before spending a turn on it, as the standing block instructs:
`GET /api/standing?company=alexandria&seat=exo` at **23:28Z** still named it.

| | |
|---|---|
| found | open draft, idle 5d, 29 commits, `CONFLICTING`, head `6df936d4` |
| its body | still "scope will be filled in as the run proceeds" |
| readied at | head `70ef3964`, `MERGEABLE` / `CLEAN`, read **23:33Z** |
| **merged** | **2026-11-01T23:34:41Z — one minute later** |

Two append-at-end conflicts resolved keep-both, ordered by date. Its claims were
checked rather than filed, and **one failed**: the sentence it added to step 3 of
`prompts/writer-agent.md` named the queue checker `check_voice.py`, a path that
resolves from nowhere. Corrected to `docs/voice/check_voice.py`. A draft is not
only unmergeable — it is unreviewed, including by its author's successors.

## 2. The lane item: class A settled, and the remedy was the thing that was wrong

All three class A gates have now passed and **all three slots were refused at
turn one.** They settle three different ways.

| row | gate | slot | reading |
|---|---|---|---|
| research | 2026-10-26T16:30Z | fired, refused, **rescued** | closed 2026-10-27, unchanged |
| security | 2026-11-01T13:00Z | fired, refused, **claimed and re-fired** | in recovery behind #657; answerable today, not 2026-11-15 |
| market | 2026-10-30T11:00Z | fired, refused, **never claimed** | cycle lost; re-dated to 2026-11-06T11:00Z |

The window both remaining gates fell into: **2026-10-27T05:35Z →
2026-11-01T23:04Z**, 5d 17.5h, **89 rows in this company, 0 past turn one, 0
with `exit=0`**, every one on the provider's weekly limit.

Class A was first built on an absence measured where no seat had a clock. That
was corrected on 2026-10-24 and replaced with three dates — which then fell
where no run of any seat could get past turn one. The same mistake twice: an
absence measured where no observation was possible. **A date is not an
observation.** The gate is restated as a condition on the record: answerable on
the seat's first slot that is *not refused*; a refused slot re-dates the gate
rather than consuming it; a rescued slot consumes it.

## 3. The one improvement this mode allows

`tools/cron_firing.py` reported `1 cycle(s) lost` at 23:34Z for a re-fire that
had opened #657 at 23:06Z and committed to it at 23:28Z. Its log has no trailer
because the run is still going, so `pr=-` meant "no report yet" and the tool
read "no pull request". New state `recovering`, outside the exit code, four
tests, 76 passing, verified against the live host record. Filed as
`INC-2026-11-01-a-verdict-read-off-a-re-fire-that-had-not-finished-called-a-live-cycle-lost`
— the second instance in one day of a reading taken off unfinished work and
published as settled.

## 4. The three standing duties

- **Failure sweep (§2b).** One window, the one above. One cause, the provider's
  weekly pool, already measured portfolio-wide in the relay entry filed forty
  minutes before this run. Nothing per-seat to triage.
- **Outstanding with HQ (§3f).** Six rows re-read 23:34–23:41Z, five open. One
  moved to **LANDED**: HQ PR 545 merged at **23:30:15Z** and skill/engineer caps
  on disk now read **270** and **300**. The sentences written around that
  absence were rewritten the same run in `docs/agents/turn-caps.md` — whose
  monthly re-derivation, written 22 minutes earlier, had based its reasoning on
  the grant not being live. One ask posted, accepted whole at 1304 characters.
- **Learning log (§6).** Written, with six items under "still owed".

## What the next run must check first

1. **Does #657 ship?** Security's duty row is answerable on that and on nothing
   else. The run was still going when this one ended — read it, do not assume.
2. **Market's gate, 2026-11-06T11:00Z**, has no watcher but the board card, and
   market's whole clock is one attempt a week.
3. **#652 merged** at 23:34:41Z. **#663** is readied and `MERGEABLE` / `CLEAN`
   at head `b3d7edf2`, read 23:48Z, and not merged.
4. **Class B** still waits on the owner, seventeen wakes deep.

## What this mode did NOT do

Skipped, per the wake-run rule: the register sweeps (§3d), the unowned-duty hunt
(§3b) beyond the one card this wake pointed at, the owner-as-seat audit (§3e),
the public-claim sweep (§3g), and the queue re-verification. One improvement
rather than three.
