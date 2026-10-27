# ExO run note — 2026-10-27 (message, lane-next)

**Mode: wake run.** Trigger `window:message`; the wake was a `pr.merged`
event for this seat's own #630, with the instruction to continue with the
next item in this seat's lane on the board and say what was taken.

**Not superseding anything.** `gh pr list` showed no other open
`alexandria-exo/` pull request, so this branch is off `main` at `0225add`
and the chain depth is zero, after eight.

## Ship-first

Draft **#641** opened on **turn 6**, against a deadline of turn ten, before
the charter was read past its top banner. Branch, one commit, push, draft —
the four acts the banner says need nothing read first.

## What this run took, and why

The lane holds one item outside Review and Done: the duty-classes card
(`2ee0f59f`). It was the next item, and it was the next item for the two
previous runs as well — both read it, both found no gate due, both set it
down and took the thing the gates rest on instead. **Two of its three gates
have come due since the last reading.**

| Gate | Due | State this run |
|---|---|---|
| class A, research | 2026-10-26T16:30Z | **came due, answered: firing** |
| class C, owner's silence | 2026-10-26T22:15Z | **expired, proceeded** |
| class A, market | 2026-10-30T11:00Z | three days out |
| class A, security | 2026-11-01T13:00Z | five days out |
| class B, owner's word | — | still owed, fifteen wakes |

## Gate one: the first class-A slot ever to come due

Four mechanisms ran in series and every one of them was unevidenced on the
register before today:

| # | Mechanism | Record |
|---|---|---|
| 1 | the host's clock | `cron` at **2026-10-26T16:30:23.796Z** against `30 16 * * 1`, on time to the second |
| 2 | the provider | refused at turn 1, `api_error_status: 429`, `"You've hit your session limit · resets 7pm (UTC)"`, exit 1 in 5.6s |
| 3 | HQ's retry | `capacity-retry.json` holds `2026-10-26T16-30-23-798Z-cron.log`; re-fired **19:03:27.547Z** as a `hook` |
| 4 | the seat | named itself correctly — PR **#589**, "(hook, re-fired weekly slot)" — 94 turns, exit 0, **merged 19:30:56Z** |

So research's row moves off `unevidenced` and onto `firing`. **It answers
through a failure, which is stronger evidence than a clean fire would have
been**, because a clean fire tests one mechanism and this tested four.

## The finding: the instrument built for this slot got it wrong

`tools/cron_firing.py` was written one run earlier, explicitly for these
dates, and reported the slot `LOST?` — in the dangerous direction. The
register's own 2026-10-25 correction warned that "a run reading the 16:30Z
slot at 16:31Z off an absent pull request would retire three working seats."
The tool was built to prevent that error and reproduced it on the first slot
it ever had to judge.

Three defects, none visible without a real retried slot:

1. **The window excludes the retry by construction.** `resolve_shipped`
   bounds a cut run's window by the seat's *next run*, and for a refused slot
   the next run **is** the retry. #589 was created 66 seconds past the bound.
   No value of any flag reaches it.
2. **A retry successor's `pr=-` was read as `silent`.** The writer's re-fire
   of its own 16:00Z slot exited 0 after **124 turns** with `pr=-`, having
   opened #591 on a branch named `2026-10-26-hook-refired-slot`.
3. **The `LOST?` hint lied.** "Pass `--prs` to settle it" printed
   unconditionally, so a reader who had passed it was sent back to the step
   they had just taken.

**The fix** joins through `capacity-retry.json` on the log filename — the key
already existed — as a new `retried` state that does not set the exit code.
Narrow on purpose: only a run known to be re-firing a refused slot gets the
`pr=-` exemption, so `silent`, the state incident 3 exists to keep visible,
survives for every other run.

Re-reading 2026-10-24 to 2026-10-26 moves **seven** slots out of `lost`.
**12 new tests, 65 pass.** An autouse fixture restores the test file's own
promise that nothing in it reads `/srv/asc/state`, which this change had
quietly broken by defaulting `--claims` to the host path.

## Gate two: class C proceeded

The owner's silence gate expired 2026-10-26T22:15Z. The ask went to the
**writer** seat as a message: when a copy branch of theirs merges, address the
frontend seat, because `pr.merged` routes by branch prefix and the frontend
seat cannot see the one event its duty depends on.

Sent as a message and **not** as an edit to `prompts/writer-agent.md`, for two
reasons. `prompts/` is Tier C, so a charter edit would hold this entire pull
request behind an owner merge; and a sentence somebody else wrote into your
charter is worse than one you wrote yourself, because you are the seat that
has to remember it at the moment it fires.

## A correction to an incident, because its remedy was a call that does not exist

A board card's **body is immutable**. The board answers `PATCH`, `PUT` and
`DELETE` with `501`, and it answers `501` for a non-existent id too, so the
method is refused before routing. `tools/board.py` exposes no update route.

`INC-2026-10-25-a-withdrawn-finding-was-corrected-in-the-cards-comments-and-the-card-body-kept-the-dated-instruction`
recorded two runs as having "neither rewrote the body". **Neither could.** The
comment thread is not a workaround; it is the only writable surface. Filed as
`INC-2026-10-27-the-incident-about-an-uncorrected-card-body-asked-two-runs-for-a-write-the-board-answers-501`
with three performable remedies, and the register now states the immutability
where its cards are read.

## Timeline

| Turn | What |
|---|---|
| 1–5 | charter banner; `main` synced; branch; run-note stub committed and pushed |
| 6 | **#641 opened draft** |
| 7–10 | §0 mode test → wake run; no open pull request of this seat to supersede |
| 11–16 | board lane read; duty-classes card body read in full; register's class sections read |
| 17–22 | the 16:30Z slot found in the audit log, refused with a 429; the claim file joined it to the 19:03Z hook and #589 |
| 23–26 | `cron_firing.py` run against the slot: `LOST?`. Defect 1 located and confirmed structural |
| 27–35 | the fix; defect 2 found while checking the remaining `LOST?` rows were not under-credits |
| 36–45 | 12 tests; the autouse fixture; portfolio re-read across three days |
| 46–52 | `PATCH`/`PUT` probed at 501; card commented; class C ask sent to the writer |
| 53–60 | relay live tests re-read; the writer's cap found landed at 225 |
| 61–70 | incident, register note, learning log, this note, ready |

## The refusals and surprises this run learned from

The card comment went through first try, written as one thought per line with
no ids in the prose — the three prose-gate refusals the 2026-10-26 run earned
are now cheap to avoid, which is what a learning log is for.

The surprise was defect 2. It was found only because the remaining `LOST?`
lines looked too numerous and one was checked for an *under*-credit rather
than an over-credit. **A fix verified only in the direction it was aimed at
would have shipped with the writer's slot still wrong.**
