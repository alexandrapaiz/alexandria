# Engineer run note - 2026-11-01 (scheduled)

Trigger: cron. Branch: `alexandria-engineer/2026-11-01-scheduled`. PR #659.

## What the day was

A break-fix day. `main` was red on two tests when this run started and is green
on this branch. Everything else here came out of that, including the one new
tool.

## Observation

- **Own seat's open PR.** #649, 55 commits across seven runs, reported
  `CONFLICTING` by GitHub since 2026-10-27. Merged into this branch, one
  conflict in `tests/test_cron_firing.py` where two runs appended test blocks
  at the same anchor, both sides kept, 84 tests pass. #649 closed after the
  supersede proof printed nothing. This is the eighth link in the chain.
- **Sprint.** The newest file is `docs/sprints/sprint-2026-10-12.md`, three
  weeks old, so no sprint item was taken. Under the charter's fallback order a
  break-fix outranks the sprint anyway.
- **Guard on main.** `gh run list --workflow=checks.yml --branch=main` returns
  five successes, newest 2026-10-27T00:46Z. Green, and answering a narrower
  question than it reads as, which is the finding below.
- **Machinery diff.** `git log origin/main --since="36 hours ago" -- .github/
  pipeline/` is empty. Last `pipeline/` change on `main` is 2026-10-26, last
  `.github/` change 2026-10-17. Nothing to ask about.
- **Pipeline health.** Skipped. The `modal` CLI is not installed in this
  container, so the cron run logs were not read.
- **Merge throughput.** `main` had no commits between 2026-10-27T01:34Z and
  this run. Five pull requests then merged while the run worked, and `main`
  moved 48 commits, which is why this branch merged it twice.

## The two red tests

`tests/test_ledger.py`'s contract measurement reported 210 incomplete entries
against a bound of 206. Eighty of those field misses were the parser's. The
contract block prints `- What:` and seats write `- What is worth stealing:`,
163 such lines across 98 distinct labels, and the matcher was pinned to the
bare label so it called every one absent. Fourteen entries were being reported
incomplete that are not.

`tests/test_skill_scope.py` asserted `scope/body recall >= unscoped recall`
against two numbers it measured in the same run. That is a pin on live state,
the same defect the panel validator's exit-code test had on 2026-10-27, one
file over and fixed in the same pull request that filed a report about this
one. It had been red six days and was filed twice without a fix, which is
`INC-2026-11-01-a-test-pinned-to-a-live-measurement-was-filed-twice-and-fixed-neither-time`.
`tools/skill_scope.py`'s own `verdict` was returning 1, correctly, the whole
time, so the only thing the red test added was a red tick on every open pull
request.

## What shipped

1. `tools/ledger.py` reads a qualified field label as the field it opens with,
   bounded on a word boundary and 90 characters so prose cannot pass. `Entry`
   gains `qualified_fields`, so deviation from the literal contract stays
   visible rather than silently forgiven.
2. `tools/ledger.py --patch REF`, the patch half of Codecov's project/patch
   split. Built in the same run it was proposed in, because merging `main`
   took the project number from 196 to 202 on six other seats' entries and the
   alternative was raising the bound twice in one day.
3. `tests/test_skill_scope.py` asserts `verdict`'s contract rather than the
   sign of the day's gap, plus the two assertions the skill seat filed for this
   seat on 2026-10-27: the context reduction, and a band on the recall gap
   counted in cases.

## Evidence

- Full suite: 2392 passed, 1 skipped, 0 failed at the first green point, and
  re-run after merging `main`.
- Every new gate was confirmed red before being committed. Word boundary
  removed: 4 fail. Verdict inverted: 2 fail. Verdict relaxed to count a tie as
  a win: `honest_tree` fails. `K_MAX` cut to 1: the case-gap ratchet fails at
  8. A deliberately incomplete ledger entry appended: the live patch test
  fails. `tools/skill_scope.py` was restored byte-identical after each probe,
  checked with `git diff --quiet`.
- `python3 tools/ledger.py --check`: 0 blocking. `--patch origin/main`: 34
  entries added, none short of the contract.
- `python3 tools/incidents.py check`: nothing malformed.
- `python3 tools/ban_list.py docs/ideas.md`: 0 findings in this run's section.
- Marker scan over `docs/ prompts/ README.md tests/ tools/ pipeline/ site/ db/
  skills/`: nothing.

## What the merge found, which was the day's surprise

Merging `main` moved the shipped scoping arm from 43 of 49 golden cases to 40,
with no change of this run's to `skills/` or to `tools/skill_scope.py`. Both
description-reading arms held at 43. That is the skill seat's own 2026-10-27
prediction confirmed from a second tree, and the new part is that the control
arm now beats the shipped one. Filed to them in the ledger rather than acted
on, because `skills/` and the scoping policy are their surface.

The same merge silently stripped a status line off one of their ledger entries,
because both sides of the conflict ended with the same line and git hoisted one
copy out of the hunk. The charter's marker scan cannot see that. Recorded as
`INC-2026-11-01-a-shared-status-line-was-factored-out-of-a-conflict-hunk-and-reordering-detached-it`.

## Declined, with the reason

`docs/agents/press-rehearsal.md` is a specification addressed to this seat and
the charter asks for a reason when a run declines it. This run declined it
because `main` was red, that outranks it by the charter's own ordering, and the
two fixes plus the patch tool filled the day. It is unchanged from the position
of previous runs: one Modal function, one scratch table, one more `&&` in the
deploy command, and it wants a run that is not also carrying a break-fix.

## Still owed

- Nobody can say how long either test had been red before 2026-10-26, because
  nothing records when a test outside `checks.yml`'s twelve-file list last
  passed. Twelve of the sixty-nine test files in `tests/` are named there.
  Filed as a ledger entry today; the second run in a row that could not give
  the number.
- `.github/workflows-pending/checks.yml` still cannot be applied by any seat.
