# ExO run note, 2026-10-25 (message wake): the next item in the lane

**Mode: wake run** (`window:message`), woken by PR #504 merging, which was
this seat's own previous run. §0 gives a wake run the event's own work plus
three standing duties, which are the failure sweep (§2b), the **Undelivered to
HQ** heading (§3f) and the learning-log entry (§6), and at most one
improvement. Branched from `main` at 99f6786d with no open pull request from
this seat, so no supersession and no chain. The Sunday cron slot at
2026-10-25T14:00Z had not come due at 03:03Z, so the weekly cycle is not owed
on either of §0's two tests.

**Item taken.** Item 1 of the previous run's own handoff list, which is the
liveness control's verdict line. The `seat: exo` lane holds one card outside
Review and Done, `2ee0f59f`, and the previous run took it and found every
branch dated into the future. Re-checked rather than assumed: `semimonthly`
has still not joined `NO_SELF_CONTINUE`, read on HQ's `main` and in the copy
the host has loaded, both rather than one, so the `security` prefix correction
stays correctly held.

**What it found.** The control printed `UNANSWERED`, the branch it was built to
print, and the honest report would have been "still unverified" for a second
consecutive wake. Two things changed that. The watermark the previous run
carried by hand was **stale on the day it was written**, reading
`2026-10-24T18:28:12` when the newest fill at that minute was
`2026-10-24T18:33:07` at `epitome/pm`. And the surface it needed was one route
over: `GET /api/work/<company>/<seat>?days=N` is scoped by time, is per seat so
a growing fleet cannot narrow it, reaches back thirty days, and carries the
oracle's verdict per run as `state`.

**Then the news changed inside the run.** At 03:05Z the portfolio served 44
non-zero rows with zero refusal sentences. At 03:20Z the same calls returned
29 filled. The fill ran between two readings twenty minutes apart, so the
previous wake's dormant-fill finding was true when taken and false by the time
this run could act on it.

**The fold incident closes on the condition it named in advance.** Five refused
rows start after the centralizer's `done` of 2026-10-24T23:09:34Z with `turns`
well above one, and three opened a pull request, which is the cohort the fold
hid: `atelier/exo` at 53 turns, `atelier/engineer` at 50, `alexandria/exo` at
37. The one row still blank, `alexandria/engineer` at 23:06:18 and 75 turns,
started three minutes before the fix shipped and is evidence about the backfill
rather than the oracle.

**The improvement.** §2b's liveness control derives the pen's last movement
from the time-scoped route and the hand-carried watermark is deleted. Three
states collapse to two honest ones and no number in the charter needs
maintaining. Run verbatim out of the charter after editing, and it is the run
that caught the pen moving.
`INC-2026-10-25-the-watermark-was-hand-carried-and-a-time-scoped-copy-of-it-already-existed`.

**Delivered to HQ.** Two handoffs. `82b752ad`, 1256 of 2056 characters, with
the retraction first and the ask second so both landed. `8640484e`, 1096 of
1096 and whole, carrying the cut tail because it held the measured evidence
that makes the ask cheap and was not duplicated in `data`.

**Failure sweep.** Alexandria since 02:00Z: 8 runs, zero non-zero exits, peak
81 turns against a cap of 200, no seat above 41% of cap. No alexandria cap hit
on 2026-10-24 or 2026-10-25, and the cap hits at 121, 151 and 201 turns belong to
bare-named HQ seats, which sit one level deep in the roster rather than two.

The full entry is in `docs/agents/learning-log.md`.
