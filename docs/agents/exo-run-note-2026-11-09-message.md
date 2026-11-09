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

## The merge, which arrived mid-run where it was predicted

#813 merged to `main` while this run was working, so the first readiness check
returned `CONFLICTING` on `docs/agents/hq-relay.md` and
`docs/agents/learning-log.md` — the anchor contention this run's own learning-log
item 4 is about. Merged `origin/main` in, resolved keep-both with
`tools/resolve_register_conflict.py`, then reordered so #813's earlier entry
reads first in both registers, as a block move proven to be a reorder rather
than an edit (identical sorted line multiset before and after).
`--check HEAD`: both files balanced, every line of both sides present once.

Head after the merge: `ab648241`, `mergeable=MERGEABLE`, read 2026-11-09T01:0xZ.
**Merge order is now #806 → #810 → #819.** `main` is green on its own head —
`fcc56889`, `checks` passed on `fcc568893a` at 00:40:39Z.

Board report `cb9430d1`. Reply `993b4e5b`, whole at 1,497 of 1,500.

## The late finding: the full suite caught two defects after I had readied

Run in the background and read after readying. Four flags were unaccounted for
in `tools/target_census.py` — two mine (`wall_encounters.py --root`, `--seat`)
and two already failing on `main` from #813's `prose_symbols.py`. All four
registered.

The census's probe then caught a real defect: my `--seat` took any string and
an unknown seat returned an **empty survey**, so `--survivals` would have
reported all-clear for a typo. That is
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
committed by the run whose own docstring cites it. Fixed through
`cron_firing.resolve_seat`, exit 2 naming the value, three tests.

**And the gate that caught it runs in no workflow.** `tools/ci_coverage.py`: 14
of 93 test files run in CI. `tests/test_target_census.py` is not one, so it went
red in the suite and `checks` passed on `main`'s head — the gate had no voice on
the pull request that broke it. `tests/test_wall_encounters.py` is in the same
79, so this run's own 15 tests report nothing on any pull request. Said here
rather than left as an implied green.

Three `tests/test_skill_registrar.py` failures from the pre-merge run are gone
on the merged tree; main fixed them.
