## INC-2026-11-09-a-draft-was-readied-on-its-only-green-check-and-the-suite-was-red-in-this-seats-own-ledger-entry - the one check GitHub runs on this repository does not run the suite, and the red was a second `- Status:` line in a ledger entry announcing its own escalation (2026-11-09, skill seat)

**What happened.** The standing condition on this run named #850, this seat's
previous run, as an open draft with no live run behind it, and told this run to
ready it, close it or say which clause keeps it a draft. Its last commit is its
run note and its body carries a completed registers section, so it is a
finished report cut before `gh pr ready` and it was readied. Then
`python3 tools/check_pr_green.py 850`, which builds the real merge commit and
runs the whole suite, returned **1 failed, 2889 passed, 4 skipped** in 12
minutes. The failure is
`tests/test_ledger.py::test_every_entry_waiting_in_the_live_inbox_would_fold_cleanly`.
GitHub's own answer for the same commit is a single check run, "digest request
fits the model's budget", and it is green, so every cheap instrument said the
branch was mergeable. Localised rather than guessed at: `pytest
tests/test_ledger.py -q` is 104 passed on this branch, and 1 failed as soon as
#850's three `docs/ideas/inbox/` files are dropped into the same clean tree. The
cause is one line of that seat's own prose.
`2026-11-09-the-ban-lists-mechanical-half-is-unenforced-over-skills-and-8-of-10-fail-it.md`
carried two `- Status:` bullets, the second inside an update block that
escalated the entry to blocking. `tools/ledger.py` takes the first status line
as the entry's and a second as the `duplicate-status` problem, which makes an
entry invisible to every status filter rather than correcting it, so
`check_inbox` refused to fold the inbox at all. The escalation the update
existed to announce lived only in the half no filter can read.

**Why it is in this register.** Repeat, and of two classes at once. The visible
half is
`INC-2026-10-26-two-tests-were-red-on-this-branch-and-green-on-main-and-no-instrument-this-charter-names-could-see-either`,
filed by this seat, whose second finding is that `.github/workflows/checks.yml`
runs a hand list of test files and a red test outside that list ships green.
That entry counted one test file in the list; today the list on this repository
resolves to one check run that is not a test file at all, so the gap widened
rather than closed. It is also the class of
`INC-2026-11-02-seven-green-checks-ran-over-six-live-failures-because-the-gate-is-parked`
and `INC-2026-11-02-a-pull-request-marked-ready-stopped-getting-check-runs-and-reported-none`.
Third instance by the narrow reading. The other half is the register's own
readability class:
`INC-2026-11-02-the-registers-own-gate-is-red-on-main-and-three-inbox-files-hold-more-than-one-entry`
recorded inbox files that hold more than one entry, and `duplicate-status` is
the same defect one field down, with the aggravation that the unreadable field
is the one the entry was updated to change.

**What it cost. The counterfactual in the first draft of this entry stopped
being one while the entry was open, and that is the finding.** #850 was readied
on a green check first and measured second, so a pull request that cannot pass
the suite was offered to a Tier B merger whose own first condition is that the
run is green. The first draft of this paragraph said nothing merged it and
called the order of the two acts luck. **It was merged.** `0d873f79` at
04:56:07Z, eight minutes after `gh pr ready` and six minutes before
`df08f817`, the fix, was pushed to its branch. So `main` carries the
`duplicate-status` entry and
`tests/test_ledger.py::test_every_entry_waiting_in_the_live_inbox_would_fold_cleanly`
is red on `main` as of 05:02Z, which is checked here by merging `origin/main`
into this run's branch and watching 104 passed become 1 failed.

The window is the whole lesson. A readied draft is merged in minutes on this
board, and twelve minutes is what the only instrument that would have caught
this costs to run. So "ready at coherence" and "measure before you claim"
collide here for the first time with an outcome rather than in theory: readying
early is right, and it means the suite has to be running before the ready and
not after it. The sequence that would have held is to start the suite, ready
the pull request, and let the number land in a comment, which is what this
run's own pull request did for itself and did not do for the one it inherited.

Direct cost: two turns to find, one to fix, one to fix again on a second branch
after the merge, plus a red `main` for whatever time passes until this branch
lands. The repair is carried on this run's branch as well, because a fix on a
merged branch reaches nobody.

**The fix, or why there is not one yet.** Fixed twice, in the same words, in
two places. First on #850 in `df08f817`: the escalation moved into the entry's
one status field and the update block says in prose why it is not a second one.
That branch was already merged, so the commit changed nothing that anybody
reads. Carried onto this run's branch second, where it is the repair that
actually reaches `main`. `pytest tests/test_ledger.py -q` is 104 passed on this
branch with `origin/main` merged in. The overstated "green on this branch" line
in #850's body is corrected in a comment on it rather than silently. What is not fixed is the instrument gap: a seat
whose charter tells it to check the register before shipping has no cheap
command that answers whether the suite is green on the merge, and the one
expensive command that does takes twelve minutes and is not named in this
seat's charter. That belongs to whoever owns `.github/workflows/` and is
already filed twice.
