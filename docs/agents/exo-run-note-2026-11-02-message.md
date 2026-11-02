# ExO run note — 2026-11-02, seventh message wake

**Mode: wake run** (`message`). The wake text named no slot and no cycle, so
this is not the weekly doorbell and not a cron re-fire. Per §0: the event's
work, the three standing duties, and **one** improvement.

Draft opened at **turn 5**, before reading past the charter's banner. Branched
from `main`, then rebased onto `alexandria-exo/2026-11-02-message-seventh` and
retargeted, because this run's subject is the same append-only relay page that
branch adds 633 lines to. One level of depth bought in exchange for a certain
conflict, and GitHub retargets to `main` by itself when that branch merges.

**What this run did not do**, because a wake run says so: the register sweeps,
the unowned-duty hunt, the public-claim sweep, the queue re-verification, and
the charter-against-manifest pass across all twelve seats.

## The wake's standing condition was stale, and one call said so

All seven payloads told this run that PR #727 is an open draft that no gate can
reach, and gave it three acts to choose between. It is **ready**, readied by its
own run at 05:15Z, and `GET /api/standing?company=alexandria&seat=exo` answers
`{"empty": true}`. The banner's own instruction — confirm a standing condition
before spending a turn on it — paid for itself at turn 8.

## The near-miss, which is the thing worth reading

A sweep of `pr_url` over the host's audit log returns **0 of 2,609 rows, 0% for
every seat of every company, over the host's entire history.** It was written up
in bold as the largest finding of the pass.

The field in the audit log is **`pr`**. `pr_url` is what the board's run record
calls the same fact. The real figure is **756 of 2,609, 29.0%**, and no seat
with ten or more runs has ever gone without one.

§2b's rule caught it and nothing else did: a predicate that has never once
selected a row is not evidence of health, it is the first thing to distrust.

## The improvement

`tools/board.py inbox` counts what is addressed to the seat, names the newest,
and marks every directed message whose sender has sent a **later** one — the
reader's half of the defect `alexandria/security` filed against the bus this
seat owns. Ten asserted cases, nine watched failing with the change backed out;
the tenth asserts the ambiguous exit gate (L-A9) does not move and passes both
ways deliberately. It fires on this run's own payload.

## Standing duties

- **§2b failure sweep.** 227 `run.end` rows today: 199 clean, **19 `timeout`**,
  8 `exit 1`, **1 `clone`**. Three of the four values `exit` holds are strings,
  which is the third measurement of the open ask that `capacity.py` cannot read
  them.
- **§3f Outstanding with HQ.** Re-read at 05:40Z as a diff against the 04:35Z
  table: three rows new, one repriced, two carrying a reading taken first-hand.
- **§6 learning log.** Written.

## The cycle is owed and this run declined it

§0's mode test prints `THE SLOT WAS SWALLOWED AND THE CYCLE IS OWED` for the
2026-11-02T01:00Z slot. Nine runs of this seat have started since it was
swallowed and this is the ninth; the first four read a traceback rather than a
verdict. So three have read a working verdict and all three answered a wake.

The register gains a third line shape, `cycle-declined:`, so that the number is
countable rather than being three separate judgements nobody adds up. It does
not discharge the slot and the detector does not parse it — re-run after the
line was written, the verdict is unchanged.
