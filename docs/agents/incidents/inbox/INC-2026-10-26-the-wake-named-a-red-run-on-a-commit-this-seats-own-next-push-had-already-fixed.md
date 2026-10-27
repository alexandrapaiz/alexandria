## INC-2026-10-26-the-wake-named-a-red-run-on-a-commit-this-seats-own-next-push-had-already-fixed - the fifth instance of the resolved-condition wake, and the first where the stale red and its repair are both this seat's (2026-10-26, skill seat)

**What happened.** This run was woken with "a workflow failed on your branch
`alexandria-skill/2026-10-26-message-cwe-corrections`: checks", run
`40394950492`, and the instruction not to leave it red. The run history on that
branch is three runs, not one:

```
2026-10-26T20:34:50Z  40396902775  checks  43ff0d7f  success
2026-10-26T20:21:49Z  40394950492  checks  5b792013  failure
2026-10-26T20:10:26Z  40393271951  checks  1d072138  success
```

`5b792013` is an intermediate commit. `43ff0d7f` is the branch head, it is the
next commit on the same branch, and it is green. The failure was real and it was
this seat's: `tests/test_panel_provenance.py` has a vocabulary of four accepted
phrasings for an unsourced judgment, and the revision pushed at 20:21 wrote two
phrasings outside it, `ours, assembled from the four setups below` and
`ours, with all three branches measured`. Five of its 55 tests failed on them.
The commit eleven minutes later rewrote both to `ours, not the papers'`, which
is in the vocabulary, and the suite went to 55 passed. Verified here rather than
taken from the report: `python3 -m pytest tests/test_panel_provenance.py -q` is
55 passed on this branch's base commit.

**Why it is in this register.** The class is already filed as
`INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`, which
recorded four instances this morning and whose own relay note names this exact
shape: "A failure notice for a commit that is not the branch head, and a message
whose subject is a check that has since gone green, are both cheap to filter at
the sender and expensive to filter at the receiver." This is the fifth instance
and the first on this seat's branch. It has one new fact worth the entry. In the
four earlier instances the stale state travelled between seats, so the engineer
read a PM message about a check the engineer had already fixed. Here there is no
second seat: the red commit, the green commit and the wake all belong to one
seat's one branch, and the green run finished at 20:34:50Z while the wake that
named the red one fired after it. So the defect is not a seat failing to notice
a sibling's repair. The sender is holding a per-commit run result and reporting
it as the state of a branch.

**What it cost.** Four tool calls: the run's failed step, its head SHA, the
branch's run list, and a local re-run of the suite. Small here because the
charter's own duplicate-wake clause sent this run to check the state before
acting on it. The cost it threatens is the one the payload names, "do not leave
it red": a seat that obeyed without checking would have hunted a failure that
does not exist on the branch head, and the honest repair is a sentence rather
than a commit.

**The fix, or why there is not one yet.** Nothing is owed in this repository and
nothing is owed in the skill. The suppression belongs at the sender, which is
the composer the earlier entry already routed to the relay, and this entry adds
the one-line version of it: a failure notice is worth sending only when the
failing commit is still the branch head at compose time, which is one
comparison the composer can already make because it names the branch.

One thing is owed inside this seat, and it is cheaper than the register entry.
The phrasing vocabulary that went red is four fixed strings in a test, and this
seat met it by writing prose and finding out in CI. `python3 -m pytest
tests/test_panel_provenance.py -q` runs in two seconds with no credential and no
network. It is now in this run's own pre-push sequence alongside the trigger
test, which is where a four-string vocabulary should have been checked the first
time.
