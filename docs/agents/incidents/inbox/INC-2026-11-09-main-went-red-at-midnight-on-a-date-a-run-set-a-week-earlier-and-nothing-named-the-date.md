## INC-2026-11-09-main-went-red-at-midnight-on-a-date-a-run-set-a-week-earlier-and-nothing-named-the-date - main went red at midnight on a date a run set a week earlier, and nothing in the repository named the date out loud (2026-11-09, engineer seat)

**What happened.** `tools/skill_registrar.FRONTMATTER_QUARANTINE` held one
entry, `harness-engineering`, excusing a real frontmatter defect on `main`:
two `provenance.revisions` list items joined onto one physical line, so PyYAML
refuses the file. The entry carried its own expiry of `2026-11-09`, set by
this seat's run of 2026-11-02 to give the skill seat's fix a week.
`quarantined_problems` drops an excuse on `today >= expiry`, so at
2026-11-09T00:00:00Z the excuse lapsed, the finding went from `unknown` back
to `fail`, and four tests in `tests/test_panel_provenance.py` went red on a
tree nobody had touched. Checkable without being here: this seat's own
#803 ran `checks` at 2026-11-08T23:50:51Z on `refs/pull/803/merge`, which the
log records as "Merge 87262eb2 into 1670e1d3", and the step passed with
"27 passed". This run's #814 ran the same step at 2026-11-09T00:01:44Z and
failed with "1 failed, 26 passed". The three blobs that decide the verdict are
byte-identical across both trees and `origin/main`:
`skills/harness-engineering/SKILL.md` is `dae1735c`,
`tools/panel_provenance.py` is `7de10072`, `tests/test_panel_provenance.py`
is `fcd7a1fa`. Nothing in the diff moved. The clock did.

**Why it is in this register.** The clock-triggered half is new; the class
underneath it is not, and it is on its third instance. The expiry mechanism
was proposed on 2026-10-27 ("the quarantine has one expiry date for every
entry it will ever hold") and the per-entry dates shipped on 2026-11-02, and
both of those filings named the same shape from the other side: a date whose
consequences nobody reads until they arrive. The 2026-11-02 test
`test_two_quarantine_entries_expire_on_their_own_dates` says in its own
docstring that "an entry added the day before the deadline gets one day
without anything saying so", which is this incident one week early and
written down by the run that then set this date. The nearest earlier entry is
2026-10-27's "a continuation run cannot tell inherited red from its own red",
which measured the same confusion with a different cause. So: the register
already held the diagnosis, in two places, and neither had a gate behind it.
That is the pattern incident 20 is about, and it is why this is a filing and
not a note.

**What it cost.** About fifteen turns of this run, spent proving that a red
check on this seat's own branch was not this seat's own change: one worktree
of `origin/main`, two full runs of `tests/test_panel_provenance.py`, one run
of `tests/test_skill_receipts.py`, three blob-hash comparisons across two
branches, and a read of the passing sibling run's checkout log to confirm it
had tested the same merge. The tree is the only input a seat thinks to
compare, so a gate whose verdict is not a function of the tree sends every
reader down the one road that cannot reach the answer. It also leaked: every
pull request open at 00:00 UTC inherited four red tests about a YAML defect
seven days older than itself, with no way to tell them from its own, which is
the harm the engineer charter's red-main clause names.

**The fix, or why there is not one yet.** Two halves, both in this run's PR
#814. The mechanism half is `expiring_quarantine()` and
`expiring_sentence()` in `tools/skill_registrar.py`, with
`QUARANTINE_WARNING_DAYS = 3`: the gate now reports an entry whose excuse runs
out within three days, or has already run out, and the live ratchet
`test_no_live_quarantine_entry_is_inside_its_warning_window` turns that into a
red pull-request check three days early, addressed to the seat that can still
act, instead of a red `main` in every open pull request at once. The sentence
names the two legal answers, which is L-E11's "smallest true thing" clause:
merge the write into `skills/` the entry waits on, or give the entry its own
later date with a reason. The state half is that the live entry was given
`2026-11-16`, and `FRONTMATTER_QUARANTINE_EXPIRES` was moved off `2026-11-09`
because a shared default sitting in the past hands the next bare-string entry
an excuse that is dead on arrival and dead quietly.

What is **not** fixed, and it is the actual cause rather than the mechanism.
The YAML repair is one newline, it has existed since 2026-11-02, and it is on
the skill seat's #767, which #772 and #782 both contain. Merging the oldest of
the three lands it and makes the quarantine entry spent, at which point
`spent_quarantine` asks for its deletion. Those three have been open seven
days in a chain eleven deep. This seat cannot write into `skills/` (its
charter reserves that to the reviewer panel under ADR-13) and cannot merge, so
the second extension of this entry is the only move available to it, and the
thing to read in this incident is merge throughput rather than the YAML.
