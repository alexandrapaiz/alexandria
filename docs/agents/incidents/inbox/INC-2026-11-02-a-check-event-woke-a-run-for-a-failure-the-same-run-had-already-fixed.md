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
