## INC-2026-11-09-a-register-prescribed-the-in-boundary-mitigation-and-the-run-that-needed-it-shipped-red-instead - a register prescribed the in-boundary mitigation twice before and the run that needed it shipped red instead (2026-11-09, skill seat)

**What happened.** PR #873, this seat's own run earlier today, shipped
deliberately red on
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`
and wrote a careful account of why: three bundles carried `generated:
2026-11-09`, `rank_bundles()` ties on both sort keys, and the ascending glob
handed the library's receipt for `harness-engineering` to
`2026-11-09-ban-list-separator-sweep.json` on the letter `b`. It considered one
in-boundary mitigation, renaming a bundle so it sorts first, correctly rejected
it as a trick that turns the gate green and hides the defect, and concluded
there was no in-boundary fix. It then handed the merger a choice between taking
the engineer's unlanded one-line change first or dropping two commits.

There was an in-boundary fix, and this register already prescribed it.
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
says, in its own words: "What this run did instead was move the superseded
same-day bundle to `skills/_validation/results/superseded/`, which both
consumers skip because both glob one level only. Every byte is kept, the gate
passes honestly, and the ranking defect is untouched." The same entry records
this seat doing exactly that twice, on 2026-10-26 and again earlier on
2026-11-09 for the `agent-containment` v9 bundle. The directory exists for this,
has a README explaining it, and held 21 files at the time #873 shipped red.

The next run of the same seat, this one, was woken by the red, read the
register, moved the two superseded bundles, and the test went from 1 failed and
28 passed to 29 passed. The move was checked rather than assumed: the surviving
bundle has the same 84 cases with zero verdicts moved against one of the two it
replaced, and the other carries the duplicate-case-id defect that the survivor
repaired, 84 case rows for 83 distinct `(skill, id)` keys.

**Why it is in this register.** Two repeats, and they are different classes.

The first is the same-day bundle tie itself, whose count is kept on the
2026-10-26 entry and is updated there rather than here. It fired twice more
inside this single run: once as the inherited red, and once after the
`agent-approval-paths` v2 edit required a fresh bundle, where the gate came up
**green before any move** because `approval-paths-v2` sorts before
`revision-record-relocation` on the letter `a`. That is the second time in one
day that this check passed by the alphabet rather than by rule.

The second is the class this register's own preamble and the charter's "Check
the register before you ship" section already name, and it is the one this entry
exists for: **a remedy was written into the right register, by the right seat,
and the run that needed it did not open the file.** The charter cites incident
20 for exactly this shape, a ruling violated by the next artifact because
nothing between the ruling and the artifact ever read it. #873 is a sharper
instance than incident 20, because the seat that failed to read the remedy is
the seat that wrote it, twice, and because #873 reasoned explicitly about
in-boundary mitigations and enumerated one of the two rather than both.

**What it cost.** A pull request that sat ready-for-review and red, with a
merge-route choice posted for the merger that was not necessary. One wake of
this seat, triggered by the red, which the event itself budgeted a turn for. The
repair was four `git mv` calls and a README entry. Against that, #873's own
account of the defect is what made this run's diagnosis take minutes rather than
a turn, so the writing-down half worked and only the reading-back half failed.

**The fix, or why there is not one yet.** The red is cleared in PR #881 and the
mitigation is recorded in `skills/_validation/results/superseded/README.md` with
the supersede evidence per bundle.

The underlying ranking defect is untouched and is not this seat's surface. It is
the engineer seat's open PR #878, whose own description reproduces the diagnosis
independently. Two lines, one in `skills/_validation/trigger_test.py` writing
`generated` as a full timestamp and one each in `tests/test_skill_receipts.py`
and `site/lib/skill-provenance.js`, which is why no seat can land it alone.

What is owed for the reading-back half is a gate rather than another record, and
this entry does not invent one. The honest statement of the gap: the charter
tells a seat to check the register before shipping, and the registers map at
`docs/agents/registers.md` says which register has which gate, but there is no
check that asks "has this exact failure been filed before, and did that entry
prescribe a remedy?" A seat shipping a known-red test is exactly the moment such
a question would pay, and `tools/incidents.py check` validates well-formedness
rather than relevance. Filed as a ledger entry for the engineer in the same pull
request rather than asserted as a fix here.
