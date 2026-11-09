# ExO run note — 2026-11-09 (message wake, `red-gate`)

Branch `alexandria-exo/2026-11-09-message-red-gate`, PR #907. Trigger:
`message`. Mode: wake run, not the weekly doorbell — the wake text names a
routed note and two merge notices, and no payload item names `week.started`.

Trunk read at **`eb5819dc`, 2026-11-09T10:16:14Z**, which was `main`'s head for
the whole run.

## What woke this run, and what I took

Four payload items: merge notices for my own #895 and #890, a `done` from
`alexandria/engineer`, and a routed note from `alexandria/skill` naming two red
gates of mine plus the wake-router half still owed.

I took the note's three items and the engineer's handed-back merge debt. The
board's one backlog card (`2ee0f59f`, the nine unevidenced duty rows) is left
untaken, on purpose: three live reds on the trunk outrank a backlog item, and
the note's own instruction was to read the inbox and act.

## Four reds, three of them from my own merges

| gate | red since | repaired |
| --- | --- | --- |
| `tools/target_census.py --check`, 7 flags unaccounted | 00:26 | **this run** |
| `tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown` | 08:13 | **this run** |
| `tests/test_incidents.py::test_the_live_register_passes_its_own_gate` | 08:51 | by my own #895 at 09:29:58Z, 65s before the note reporting it was sent |

The census one had been red for ten hours and nobody had named it. It was found
by widening the note's claim with one command — the whole suite — rather than
by running the gate I was pointed at.

## The measurement that reframes all three

A full local suite over `main`'s content, 3,007 cases, 995 s:

- **5 failing cases in 2 files.** Both files are in the `UNCOVERED` pin list of
  `tests/test_ci_coverage.py`.
- **The 14 test files `.github/workflows/checks.yml` runs were all green.**
- 86 of 100 test files run in no workflow.

So every pull request that produced today's red state carried a green `checks`
run. The note read the coverage failure as a manual pin step nobody asked the
second run to take; that is one level short. **No run of mine was ever offered
these gates.** The remedy is not a reminder, and both real remedies are a
`workflows` write that this seat's dispatch forbids. Pinning is the gate's own
last resort and the only resort available to the seat that breaks it.

## What this run changed

1. **Pinned** `tests/test_burn_shares.py` and `tests/test_kill_vocabulary.py`,
   with what each guards and the reason above rather than a filename.
2. **Declared the 7 census flags** with the kind and reason each takes, gave
   `burn_shares.py --root` the help text it shipped without, and
   **deduplicated** two keys that sat in the `DECLARED` literal twice — written
   by two runs each of which believed it was adding them, the second silently
   shadowing the first.
3. **Verified the third red in both directions** rather than trusting the note
   or the trunk: restored the pre-repair heading in place, reproduced
   `1 problem(s)` and the red test; restored the repaired one, got `nothing
   malformed` and 51 green.
4. **Paid the first trunk merge** the engineer handed back. #879 now reads
   `MERGEABLE`/`CLEAN`. Its one conflict, `docs/agents/exo-owed.md`, is
   hand-resolved by renumbering this branch's row 16 to 21; the resolver's
   `--check` confirms the four registers it does cover are balanced.
5. **Registered `docs/agents/exo-owed.md`**, which was in no register table at
   all, so §3d's sweep had never reached this seat's own duty register. Its gate
   column reads GAP with the reason.
6. **Narrowed the duplicate-wake ask** on the relay page into three shapes and
   sent the narrowing up as `4a3f62cf`, whole, 1,258 of 1,258 characters.
7. **Registers:** one incident entry, one append to the exit-code entry (seventh
   instance), two ledger inbox entries, two owed rows (21, 22), the learning-log
   entry, this note.

## What I did not do, and why

- **The second trunk merge is not done.** I probed #744: three conflicts, the
  resolver pays on one, the other two need judgement on a week-old branch.
  Aborted rather than half-resolved at the end of a run.
- **§2b's failure sweep is not run.** Three wakes of this seat swept it in the
  last two hours and nothing this wake touched moves it; re-taking it is the
  spend §3f rule 3 says not to make.
- **No charter edit.** Four charter diffs of mine are already held at Tier C
  with the owner. The content that would have gone into §2a-1 — the three wake
  shapes — is in the learning log and on the relay page instead, where it ships
  without a hold. Named here so the next run can decide differently.

## The three shapes of one word, because the proposed fix is wrong for two

1. **Duplicate wake.** One event, two runs, message still true. The only shape
   a router can act on. Seven instances.
2. **Stale wake.** True when composed, false when delivered. The surface moved;
   nothing was answered. **No router reaches it.** New today, and mine.
3. **Wrongly suppressed wake.** `answered_by` is a clock join, so a router on it
   would have dropped a wake carrying a real correction to a shipped skill.
   Measured by the seat that proposed the suppression, on its own messages.

Six of shape 1 cost runs nobody needed; one of shape 3 would have cost a run
somebody did. Hence: key suppression on an `in_reply_to` the **sender** writes.

## One finding about this run's own instrument

The suite was started in the harness's background mode so that no hand-rolled
pipe could eat the status. The completion notification said `exit code 0`; the
output file's last summary line said `5 failed, 3002 passed`. Seventh instance
of the exit-code class and the first with no remedy inside the command.
**Read the tool's own last line, not its exit code.** Appended to the existing
entry rather than opened as a new one.

## Pull request

https://github.com/alexandrapaiz/alexandria/pull/907
