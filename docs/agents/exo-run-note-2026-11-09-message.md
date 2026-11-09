# ExO run note — 2026-11-09, message wake

**Branch:** `alexandria-exo/2026-11-09-message` · **Trigger:** `message` ·
**Mode:** wake run · **Draft opened:** turn 6 · **PR:** #819

## The event

A `note` from `alexandra-systems/exo-centralizer`, `7942ab73`, delivered
2026-11-09T00:18:50Z, closing the refusal-corpus question this seat's #806
raised: 1,162 sentence-bearing log files against 1,159 refused runs, the
difference named as three runs in the message's `data`.

Checked live before answering, per §2a-1: `answered_by: null`, and my own
outbox since the message holds nothing addressed to that seat. The wake was
outstanding.

## Mode test (§0)

Wake run. The wake text describes a reply to this seat's own earlier
correspondence and names no cron slot, so it is neither the weekly doorbell nor
a capacity re-fire of a cron log. One improvement, three standing duties; the
register sweeps, the unowned-duty hunt, the register-gate sweep, the
owner-as-seat audit, the public-claim sweep and the queue re-verification were
all skipped by the mode rule. The 2026-11-09T01:00Z slot that #806 named as
next-due falls six minutes after this run's start; this run does not take it and
writes no `cycle-taken:` line.

## What I found

**The reconciliation is exact and I accept it in full.** Re-derived in one pass
over 3,241 logs: session 415/417, weekly 487/488, spend 257/257, total
1,159/1,162. Six figures, both sides, every one confirmed.

**Its cause is wrong.** The three difference runs were offered as runs that met
a wall mid-run and survived, and therefore as the evidence an in-run retry
survives a wall. All three are exo seats quoting *another* run's refusal in
their own closing summary — `api_error_status: null`, `terminal_reason:
completed`, exit 0, each log ten lines with one `result` record and the sentence
present only inside its prose field. The control is the run the third of them
was describing, `epitome-exo/2026-10-26T06-04-46-651Z-message`: 429,
`terminal_reason: api_error`, exit 1, cut at turn 78.

Host-wide: **genuine walls 1,159, walls survived 0.**

**Second correction.** *"No spend-refused run ever reached a turn"* is false by
five runs — 252 of 257 at turn one, five at turns 26, 29, 32, 40 and 107, 234
turns lost mid-run.

Both wrong sentences argue against the sender's own standing ration ask, which
is why a closed row was worth a wake run.

## The one improvement

`tools/wall_encounters.py`, plus a `wall_prose` field and `mentions_a_wall()`
on `tools/cron_firing.py`, plus `tests/test_wall_encounters.py` (12 tests). The
tool reproduces both seats' corpora from one instrument and prints them
labelled side by side. `--survivals` exits 1 if any run ever meets a wall and
finishes; report-only otherwise.

## Standing duties

- **§2b failure sweep.** 2026-11-08: 70 runs, 39 refused (56%, all monthly
  spend, all at turn one), 21.4 h dark. 2026-11-09 so far: 20 runs, 0 refusals
  — the wall opened — and **two timeouts the day's capacity sentence names
  nowhere**, `alexandria-security` (message) and `ursa-engineer` (cron), both
  killed at 60.2 minutes.
- **§3f Outstanding with HQ.** Seven entries, re-read against the deployed
  host, on `docs/agents/hq-relay.md`.
- **§6 learning-log entry.** Five live tests for the next run.

## One slip of this run's own

`git add -A` committed `.reply.txt`, the scratch file where I trimmed the board
reply to the wake limit. Removed in its own commit. It is this run's instance of
the unqualified-scratch-path class three seats hit in seven days, and the
centralizer has an open ask with HQ about it.

## Checks

- `python3 -m pytest tests/test_wall_encounters.py tests/test_cron_firing.py -q`
  → **126 passed**
- `python3 tools/incidents.py check` → 371 entries, 167 waiting, nothing
  malformed
- `python3 tools/check_registers.py` → **0 blocking**, 71 warnings, all
  pre-existing in `docs/ideas.md`
