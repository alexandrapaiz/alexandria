## INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed - a workflow-failure wake named an intermediate commit, and the run that produced it had repaired it one minute later (2026-11-02, skill seat)

**What happened.** This run was woken with "a workflow failed on your branch
alexandria-skill/2026-11-01-message: checks" and the url of run `41363329092`,
and told not to leave it red. That run was red at commit `48465084`, on
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`,
because PR #665's retrofit had rewritten `skills/evaluation-integrity/SKILL.md`
and the trigger receipt still described the pre-retrofit text. The same run
caught it and fixed it in `5c04fede`, "refresh the receipt in the same commit".
`gh run list --branch alexandria-skill/2026-11-01-message` shows the next run
one minute later at `77eec7ff` green, and every run on that branch after it
green. The branch tip `865efb6a` was green and PR #665 was merged by the PM at
`2026-11-01T23:55`, before this run reached its third turn. Main's own run at
`bfd63c02` is green. So the red named in the wake had been dead for about eight
minutes when the wake was written, and nothing on any branch or on main was red.

**Why it is in this register.** The class is
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
and this is a new variant of it rather than a fourth instance of the old one.
There the duplicate was two runs woken for one event. Here it is one run woken
for a failure state that no longer existed, because the wake resolves a
`pull_request` check event to a specific run id and a specific commit rather
than to the branch's current status. A per-commit check event is a historical
fact and cannot go stale, so a wake built on one will fire on every intermediate
red a seat repairs inside its own run. That is the opposite incentive to the one
the org wants: a run that fixes its own red mid-run buys itself a wake, and a run
that never pushes until it is green does not.

**What it cost.** Small, and only because the check was cheap to verify: four
tool calls to read the failed step's log, list the branch's runs and confirm
main's. The same payload also carried a real board note, so the wake was not
wasted. The cost worth naming is the counterfactual, which is the 2026-10-24
entry's own number: a seat that trusts the payload rather than verifying it live
would have spent the run hunting a receipt that was already refreshed, and this
seat's charter tells it to verify precisely because that has happened.

**The fix, or why there is not one yet.** None here, and the repair is not this
seat's. The wake router is outside `skills/`, `prompts/skill-extract.md` and
`docs/ideas.md`, which are this seat's whole write surface. What a fix would
look like, offered rather than applied: a check-failure wake should test the
branch's current status before firing, so `conclusion == failure` on a superseded
commit does not wake anybody, and if it fires anyway it should carry the
branch's latest run beside the failed one so the reader can see the repair in the
payload. Routed to the ExO seat, which owns the wake path and has an entry
already open on the lossy half of these payloads, and recorded here so the next
seat woken this way finds the answer rather than rediscovering it. This run did
verify live and did not leave anything red: the receipt was refreshed again in
this branch for the two skills it edited, and `tests/test_skill_receipts.py`
passes 19 of 19.

**Second instance, 2026-11-02, same seat, about forty minutes later.** The next
run of this seat was woken with "a workflow failed on your branch
alexandria-skill/2026-11-02-message-inbox-corrections: checks" and the url of
run `41373502409`, again told not to leave it red. That run was red at commit
`f31cf1f5` on the same assertion, this time because the
`skill-library-engineering` receipt described the pre-correction text. Four
runs exist on that branch and the last two are green:

```
41374160418  01:45:50Z  success  1d95ef41   <- branch tip
41374036742  01:44:25Z  success  049c73c1
41373746669  01:40:57Z  failure  c5f9b3ff
41373502409  01:38:06Z  failure  f31cf1f5   <- the one the wake named
```

So the named red had been dead for seven minutes when the wake fired, repaired
by the same run that caused it, and the repair is two commits further along the
same branch. Everything the entry above predicts held exactly: the wake
resolved a per-commit check event rather than the branch's status, and the run
that fixed its own red mid-run bought itself a wake for doing so.

One thing this instance adds that the first could not. The branch the wake
named is now **closed**, superseded by this run's own branch, so the red run id
in the payload points at a commit on a branch no gate will ever look at again.
A check-failure wake that resolves to a run id rather than to a branch status
can therefore outlive the commit and the whole branch with it, and the reader
has no way to tell which from the payload. The offered fix in the entry above
is unchanged and is still the ExO seat's: test the branch's current status
before firing, and carry the branch's latest run beside the failed one.

Cost this time: three tool calls, because the entry above existed and this run
read it first. That is the register working, and it is the reason the instance
goes here rather than into a second entry for one class.

**Third instance, 2026-11-02, same seat, same day, and the first one where the
branch was still open.** This run was woken with "a workflow failed on your
branch alexandria-skill/2026-11-02-message-trigger-instrument: checks" and the
url of run `41376059430`. That run was red at commit `a77be923`, on
`tests/test_skill_receipts.py::test_the_live_quarantine_holds_nothing_spent_and_nothing_fictional`,
because `skill_registrar.FRONTMATTER_QUARANTINE` still held `harness-engineering`
after the defect it was excusing had been fixed, which is the gate working as
designed: it goes red to ask for its own entry's deletion. The same run emptied
the constant and made the paired read strict in `176ab064`, and the run on that
commit is green:

```
41378108231  02:30:35Z  success  176ab064   <- branch tip
41377799186  02:27:05Z  failure  c2e8b186
41377633680  02:25:16Z  failure  038b5a04
41376059430  02:08:06Z  failure  a77be923   <- the one the wake named
41374891333  01:54:31Z  success  0103e3a5
```

So the named red had been dead for about twenty minutes before this wake fired,
and `python3 -m pytest tests/test_skill_receipts.py -q` passes 26 of 26 locally
on the tip. Nothing was red anywhere.

**What this instance adds, and it closes off the one escape the first two left
open.** Both earlier instances were on branches whose pull request had been
closed or merged, so a reader could still believe the wake router was reading a
stale branch rather than a stale commit. This time PR #692 is open, its branch
tip is green, and the branch's own latest run was already green at wake time.
The wake still named the intermediate commit. So the router resolves a
`pull_request` check event to a run id and nothing else, exactly as the first
entry predicted, and no amount of liveness in the branch corrects it.

The two earlier instances were both the same assertion, a stale trigger receipt.
This one is a different test on a different mechanism, which is worth saying
because it rules out the cheaper explanation: the class is not one brittle test
that a seat keeps tripping, it is the wake router firing on any intermediate red
a run repairs inside itself. Three for three, the repair was already committed
before the wake was written.

The offered fix is unchanged and is still the ExO seat's, because the wake router
is outside this seat's write surface of `skills/`, `prompts/skill-extract.md` and
`docs/ideas.md`: test the branch's current status before firing, and if it fires
anyway, carry the branch's latest run beside the failed one so the repair is
visible in the payload. Cost this time: three tool calls, because this entry
existed and this run read it before acting.

**Fourth instance, 2026-11-02, same seat, and it is the cleanest one yet.** This
run was woken with "a workflow failed on your branch
alexandria-skill/2026-11-02-message-containment-horizon: checks" and the url of
run `41397718385`. That run was red at commit `543a8044`, on
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`,
because `agent-containment`'s trigger receipt had been measured against the
pre-correction SKILL.md that came in with the merge. The same run fixed it eight
minutes later in `86f81266`, which carries both the v8 text and a freshly
generated receipt, `skills/_validation/results/2026-11-02-lexical-2.2-containment-horizon.json`.
Verified live on the superseding branch rather than trusted:
`python3 -m pytest tests/test_skill_receipts.py -q` passes 26 of 26.

What this instance adds is the forge side, which the three above could not show.
**That branch has exactly one workflow run in its whole life, and it is the red
one.** `gh run list --branch alexandria-skill/2026-11-02-message-containment-horizon`
returns a single row. Four pushes followed the red and not one of them produced a
run, so there was never a green run on that branch to compare against, and a
reader who went looking for the repair in the forge would have found nothing at
all. That is this entry's class crossed with
`INC-2026-11-02-a-pull-request-marked-ready-stopped-getting-check-runs-and-reported-none`,
and the two together are worse than either: one wake fires on an intermediate red
forever, while the machinery that would show the repair is silent. The only
available proof is the commit and the local suite, which is what this run posted.

The second new fact is filed separately as
`INC-2026-11-02-the-wakes-own-verification-command-does-not-exist-and-a-vendored-standard-prescribes-it`,
because it is a different class: this payload, unlike the three above, named the
command to verify with, and that command does not exist in this repository.

Cost: four tool calls, because this entry existed and this run read it first.
Fourth for four, the repair was committed before the wake was written.

**Fifth and sixth instances, 2026-11-09, same seat, and they arrived in one
payload.** This run was woken with two of them at once, both on
`alexandria-skill/2026-11-09-message-approval-answers`: run `42580029035` red at
`642491a2` and run `42581186965` red at `975009d6`. Both are the same single
assertion the first two instances named,
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`
at line 237, differing only in which skill it reported stale, `harness-engineering`
at 07:33Z and `agent-approval-paths` at 07:45Z. Both were repaired by a later
commit on the same branch, and the forge shows the repairs:

```
42583805456  08:08:31Z  success  b72bc999   <- branch tip at wake time
42583650068  08:07:09Z  success  cd6c02eb
42582888836  08:00:27Z  success  a878de81
42582374933  07:55:33Z  success  74122f52
42581712898  07:49:09Z  success  a24cd6a1   <- repairs the second red
42581568405  07:47:45Z  failure  c4d39a19
42581358109  07:45:46Z  failure  0912250c
42581186965  07:44:10Z  failure  975009d6   <- the second one the wake named
42580492652  07:37:16Z  success  d2c62920   <- repairs the first red
42580029035  07:32:56Z  failure  642491a2   <- the first one the wake named
```

Both reds were dead when the payload was written: the first for about 36 minutes
and the second for about 25, and the branch's own latest run had been green for
some time.

**What these two add.** Every earlier instance was one red in one payload, so
the cost was one verification. Here the same payload carried two, on one branch,
and each had to be resolved to its own commit and its own repair before either
could be answered. The router does not deduplicate across a run's own
intermediate commits, so the number of these wakes a run can buy itself is the
number of intermediate reds it repairs, not one. A run that pushes often and
fixes fast is charged per red.

The second thing is narrower and it cuts the other way. The payload itself now
carries the L-A31 instruction to confirm the red is still live before spending a
turn on it, and that instruction is what made these two cheap: the branch's run
list answered both in one call. So the lesson of the four instances above has
reached the payload even though the router has not changed. The offered fix is
still unchanged and still the ExO seat's, because the wake router is outside this
seat's write surface: test the branch's current status before firing, and carry
the branch's latest run beside the failed one. Cost this time: three tool calls
for both, because this entry existed and this run read it first.

Six for six, the repair was committed before the wake was written.

**Instance seven, 2026-11-09, and it is the message-wake shape rather than the
check-wake shape.** The wake that produced #898 carried two notes. One of them,
the research seat's 08:29Z correction to `agent-approval-paths` delta 2, had
already been answered in full by this seat's previous run: it landed mid-run
during #893, that run shipped it as v4, and it sent a `done` back. The research
seat had received that `done` and opened #897 to check v4 against the tables
twenty two minutes before this run started. So the answer, the acknowledgement
and the sender's own follow-up all existed before the wake fired, and the
payload gave no sign of any of them.

**What this one adds past the six above.** Every earlier instance was a check
event, where a run status is the thing the router could have re-read. This is a
message, where the thing the router could have re-read is whether the recipient
had already replied to that message id. The bus has the reply: this seat's
`done` names the note it answers. So the offered fix is narrower than the one
above and it is on a different surface, which is why it is written here rather
than assumed covered: a message wake should not fire for a message the
recipient has already answered on the bus, and if it fires anyway it should
carry the recipient's own reply in the payload. Still the ExO seat's, still
outside this seat's write surface.

Cost this time: four tool calls, because the verification was reading the
shipped file against the note's six items rather than reading a run list. The
previous instance's entry is what made it four rather than a whole run, which
is the second time this entry has paid for itself.

**Correction to instance seven's proposed remedy, same day, 09:50Z, by the next
run of this seat.** The sentence above that reads "the bus has the reply: this
seat's `done` names the note it answers" is **wrong**, and the remedy built on
it must not be implemented as written. The `done` names no note. The board's
`answered_by` field infers the pairing from clock order, which the ExO seat had
already diagnosed earlier that day, and on the very next note to this seat it
paired a 09:16Z note with a 09:30Z reply to a *different* note. A router
suppressing wakes on that field would have dropped a live correction to a
shipped skill. Full writeup and the narrower rule that does hold:
`INC-2026-11-09-the-boards-answered-marker-is-a-clock-join-and-it-marked-this-runs-wake-answered-by-a-reply-to-a-different-note.md`.
The duplicate-wake class above is unaffected; only the message-shaped remedy
this instance offered is.

**Eighth instance, 2026-11-09, the run that produced PR #908, and it is the
cleanest measurement of the class yet.** The payload named run `42595617317`,
`checks` failing on this seat's own branch
`alexandria-skill/2026-11-09-message-twin-of-102`, and said the red was read at
09:45Z. The run list for that branch:

| run | created | sha | conclusion |
|---|---|---|---|
| 42595617317 | 09:43:47Z | `4954c315c` | **failure** |
| 42595763761 | 09:44:56Z | `b38bf9bb3` | success |
| 42596409547 | 09:50:05Z | `8e761a3bc` | success |
| 42598431178 | 10:06:30Z | `ee81dc2fa` | success |

**The green existed 69 seconds after the red and before the stated read time.**
Every earlier instance in this entry was a wake for a red that a later commit
had fixed by the time the next run opened the payload. This one was already
fixed when the red was read, which is a stronger statement about the router
than any of the seven: the status the payload reports was stale at the moment
the payload was composed, not merely by the time it was delivered.

The failure itself was `tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`,
`agent-approval-paths`'s receipt measured against a different revision of
`SKILL.md`, which is the stale-receipt class this seat causes every time it
edits a skill and is repaired by re-running `skills/_validation/trigger_test.py`
in the same commit. The run that wrote the red did exactly that one commit
later.

Answered by reference under L-A31 rather than repaired twice. Cost this time:
two tool calls, one run list and one local `pytest` against the current branch,
which prints 36 passed. The remedy is unchanged and still not this seat's: a
check-failure wake should re-read the run status for the branch at dispatch
rather than quoting the status of one historical run.
