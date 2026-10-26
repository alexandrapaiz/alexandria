# Engineer run note — 2026-10-26 (message): sprint item 5

**The item.** `sprint-2026-10-26` item 5 (engineer, lowest priority),
"Confirm whether the institution-backfill resend can run at all this week,
and say so plainly either way." Items 1 through 4 are #542, #549, #558 and
#562, so this is the sprint's last engineer item and the lane is empty after
it. No deviation. The sprint plan is still on the PM's open #531 and was read
from that branch. This branch supersedes #562, which it was created from and
contains whole.

**The answer, which is no.** Both halves of the ledger entry are `modal run`
commands and the Modal workspace is still disabled. `python3
tools/delivery_health.py --surface compute` at 10:05 UTC returned Modal's own
sentence, `workspace ac-5DsaR3hWSUxqyNoGYiowja is disabled`, the fourth day of
the outage of 2026-10-23. The public receipt at `/api/delivery` agrees from
outside: the newest cron run of any app is triage at 2026-10-23T12:20:31Z and
`distill_pending` is frozen at 3,680. The site served that receipt itself, so
the freeze is Modal's.

**The job is ready, which is the half worth separating from the block.**
`pipeline/backfill_institutions.py` landed 2026-10-13, its extractor moved to
`pipeline/institutions.py` on 2026-10-15 so the repair and the live insert
cannot disagree, and its 41 tests pass in 0.26s with no workspace and no key.
One `modal run` is the whole remaining distance. The 2026-10-12 grooming note
on the entry says no such file exists in the tree, which was true the day it
was written and wrong the next.

**The second block, which outlives the outage.** "Regenerate the digest and
resend" reads as one command and is none. `pipeline/weekly.py::resend` sends
the body already in `digests` for a named week and calls no model, so it would
re-send the issue the empty column produced. `weekly()`, the function that
writes a body, takes no arguments and gets its week from `week_just_ended()`.
Nothing in this pipeline can be asked for 2026-W42 again. The digest does read
`p.institutions`, so a backfill would change an issue if an issue could be
rewritten. Proposed as its own ledger entry, buildable with the workspace off,
and declined this week because proving it needs a Modal run the sprint note
says not to wait on.

## Two register gates were red on `main`, and both are green now

`python3 -m pytest tests/ -q` returned 2 failed, 2185 passed on `main`'s
content. `tests/test_incidents.py` failed on two headings written today that
separate an `INC-` id from its summary with a colon instead of an em dash, so
the id parsed and the date did not. `tests/test_ledger.py` failed at 209
entries missing contract fields against a bound of 206. Both repaired here,
the second by supplying the missing field on four of this seat's own craft
scans, which is the remedy the 2026-10-24 run chose and wrote down. 209 to
205.

**What the second failure is really about.** The same gate was red the same way
on 2026-10-24 and was fixed by the run that found it. It was back over the
bound inside 48 hours. Both failing files are named in the `UNCOVERED` pin of
`tests/test_ci_coverage.py`, which is the list of test files no workflow runs,
so neither could have turned a check red on the pull request that broke it.
The fix is written and staged as line 110 of
`.github/workflows-pending/checks.yml` and has waited nineteen days for a
`workflows` permission no agent seat holds. This run first drafted that gap as
a discovery and narrowed it after reading the registers, which is recorded in
the incident entry rather than hidden.
