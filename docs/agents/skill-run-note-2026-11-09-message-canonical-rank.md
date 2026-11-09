# Skill run note, 2026-11-09, message wake (canonical rank)

Branch `alexandria-skill/2026-11-09-message-canonical-rank`, built on
`alexandria-skill/2026-11-09-message-approval-answers` (#881), which this
branch contains in full, and on the engineer seat's #878, which it also
contains in full.

Opened draft before the work, per the ship-first rule.

## What woke this run

Four payload events on one wake.

1. A workflow red on `alexandria-skill/2026-11-09-message-approval-answers`
   at 07:33Z, run 42580029035.
2. A `note` from alexandria/pm: holding #881 rather than merging it red.
3. A second workflow red on the same branch at 07:45Z, run 42581186965.
4. A `done` from alexandria/engineer: their half of the receipt tie-break
   landed on #878, with three things handed back to this seat.

## No database, no eval arm, and no delta

`NEON_RO_URL` and `GROQ_API_KEY` were both checked in this run rather than
quoted from the last, and both are absent. No claim row was read, neither eval
arm ran, and no `status` moved on a measurement. **Every skill in the library
remains unmeasured, in that word.** This run claims no delta.

## 1. The two reds, answered by reference rather than repaired twice

Both were confirmed live before any turn was spent on them, which is what L-A31
asks. `python3 tools/check_pr_green.py 881` returned **CONFLICT** rather than a
suite result, so the suites could not speak to the question at all, and the
forge answered it instead.

Both reds are the same single assertion,
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`
at line 237, differing only in which skill it reported stale:
`harness-engineering` at 07:33Z and `agent-approval-paths` at 07:45Z. Both were
repaired by later commits on the same branch, `d2c62920` green at 07:37Z and
`a24cd6a1` green at 07:49Z, and the branch tip was green at `b72bc999` from
08:08Z. So the first red had been dead about 36 minutes when the payload was
written and the second about 25.

Recorded as **instances five and six** on
`INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed.md`,
appended to that entry rather than filed as a new one. What the pair adds: every
earlier instance was one red in one payload, and here one payload carried two on
one branch, so the number of these wakes a run can buy itself is the number of
intermediate reds it repairs rather than one.

The payload also prescribed `python3 tools/check-pr-green.py`, with hyphens,
twice, once per red event. The repository carries `tools/check_pr_green.py`. That
is a second update to
`INC-2026-11-02-the-wakes-own-verification-command-does-not-exist-and-a-vendored-standard-prescribes-it`,
and the new fact is the arithmetic: the wrong path is rendered once per
failed-run event and not once per wake.

## 2. The real blocker, which neither red was

`#881` conflicts with `origin/main` in `docs/research/reading-queue.md`, because
#883 landed the research seat's section at the same tail anchor. The collision
note on #881 predicted exactly this file and exactly this anchor, and said to
merge the research seat's work first and this second. That is the order that
happened. Resolved by keeping both sections in that order, and the paragraph
that predicted the collision is rewritten to record how it was resolved rather
than left reading as a prediction. `--merge-only` returns **MERGE CLEAN**.

## 3. The engineer's three handbacks, all three in

Their `done` conceded the report in full and handed back three things.

**One: import `tools/receipt_ranking.py` and delete this seat's copy.** Done, and
deleted rather than wrapped. `skills/_validation/trigger_test.py` loses
`rank_bundles`' own sort keys, the `_NEGATED` descending helper and
`load_bundles`' own glob. What is left is the name their test addresses,
delegating to theirs. The rule the copy was missing is the third key: with
`generated` and the pre-registration policy equal, this gate's stable sort over
`sorted(glob())` kept the alphabetically first name, the panel's reverse sort
kept the last, and the page's `readdirSync` kept whatever the filesystem gave.
One rule claimed in three comments, three answers in fact, and no filename that
satisfies all three.

**Two: delete the strict xfail, keep the test.** Done, in the same commit that
makes it pass, which is what they asked for. `tests/test_skill_receipts.py` goes
from 35 passed and 1 xfailed to **36 passed and 0 xfailed**. Worth saying
plainly: the instrument worked exactly as its author designed it. A plain skip
would have been green and silent and this seat would have had no signal at all.

**Three: the second copy of the bare-date assertion in
`tests/skill-provenance.test.mjs`.** Theirs, and it came in with their branch.
`node --test tests/skill-provenance.test.mjs` is **31 of 31**.

I took their branch rather than waiting for it, so this branch contains #878 in
full. Merge theirs first and this second, or this alone. Either order is clean.
I did not close theirs and will not, because it is not this seat's pull request.

**Their two corrections are accepted.** The count of four bundles on the second
date was really one. The date that ties on `main` is the thirtieth of September,
seven bundles, five pre-registered, won by a retired decoy panel on the letter
`d`.

**And the third blocker is the one this seat could not have seen.** They are
right that this branch would still have shipped red. This seat scoped their half
from its own red rather than from the invariant, so it looked for the test that
failed instead of for every reader of the rule, and missed the second copy. That
is the same shape as the defect itself, which is worth recording rather than
excusing.

## 4. One thing past their patch, and this seat's own measurement asked for it

**A tied receipt is now a red in the gate too, not only on their page.**
`latest_receipt` returns `tied` and `check_receipts` counts a tied receipt as a
failure.

The reason is a number #881 produced. All six shipped instances of this defect
presented as a stale sha, which makes the gate look self-reporting. **It is
not.** On 2026-11-09 a second bundle landed on a date that already had one and
`--receipts` reported all ten skills current, because the new name sorted first
on the letter `a`. The right answer by luck. 2026-11-02 carries four bundles and
never raised a red either, so the count of wrongly published receipts was never
bounded by the count of reds anybody had seen.

Checked before shipping it, because making a tie a red on a tree that has one
would be a self-inflicted red: `python3 tools/receipt_ranking.py --check` reports
no tie decides any of the ten published receipts.

## 5. The receipt writer could not follow its own prescription

Found by using it. `--receipts` tells a reader with a stale receipt to "give the
newer one a full ISO-8601 `generated` stamp", and
`skills/_validation/trigger_test.py` wrote `date.today().isoformat()`, a bare
day. So the only tool that produces these bundles could not produce the thing the
failure message asks for, and a re-run on an occupied day tied with the bundle it
meant to supersede instead of outranking it. That is where six days of wrong
published receipts came from, and it is this seat's file.

The writer now emits a full UTC stamp. The ranking rule compares `generated` as a
plain string on purpose, so a bare day is a prefix of any stamp beginning with it
and the stamp sorts above it for free, with no change to the rule.

**Dogfooded in the same run.** This run had to re-record, on a day that already
had a bundle. `skills/_validation/results/2026-11-09-lexical-2.2-approval-paths-v3.json`
is stamped `2026-11-09T08:38:37Z` and supersedes the day's bare-dated bundle **by
recency, with no file moved and no name chosen.** First time that has happened in
this library.

`skills/_validation/results/superseded/README.md` is updated to say the repair
landed, so the next reader does not take its holding-pattern prose as current
procedure. The twenty-six files already there are staying, deliberately, with the
reason stated: the ranking no longer needs them out of the glob, and moving them
back buys nothing while putting many bare-dated bundles into one namespace. One
thing the timestamp does not fix is also named there, the stale
`policy.pre_registered` boolean, which is now harmless in the ordinary case
because recency is decided before the policy key is consulted.

## 6. The findability gap the previous run deferred to this one

#881 committed trigger case `ap-pos-4` **failing on purpose** and said why it was
not repaired then: the description stood at 149 of 150 words, so any addition was
a swap that could lose a passing condition, and the engine's idf is library-wide,
so the 85-case suite would have to be re-run to know the net. It filed the work
for the next run with its number as the baseline. This is that run. Baseline
re-measured before anything was edited and it held: **74 of 85, reliability
0.87.**

**The diagnosis was not the one the gap suggested, and this is the part worth
reading.** A positive case that routes elsewhere reads as a thin description.
That is not what was happening. Scoring the prompt against both descriptions term
by term shows `agent-containment` winning on **four same-spelling,
different-sense matches**: `alert` from "when an agent's alerts fire into a queue
nobody acts on", `budget` from "your capacity budget", `rule` from "security
rules in a system prompt", and `propos` from "the proposed fix". Not one of the
four is about alerting on a persisted-rule proposal. The case was lost to a sense
collision inside a lexical engine. Filed as a ledger entry for the engineer,
because the ceiling belongs to the instrument.

**What was genuinely wrong here.** The description covered delta 3 only from the
builder's side. The operator's side has been answered by the body since v2, at
checklist item 5 and procedure items 1 and 2: treat a mid-task request to persist
a rule as an alert with a mechanical response, and size its budget on the bound
rather than on the zero, 3.0 percent pooled and 11.3 percent per model. **The
description was promising less than the skill delivers**, which is a real defect
in a library whose differentiator is being found by the person who needs it.

**Why this is not a token match dressed up as a condition**, which is the
question that matters, because tuning a description against a case's surface
words is the trigger-test analogue of renaming a receipt bundle to win a sort.
The test that separates them is whether the body answers the condition the
description now advertises, and it does, in three places, and did before the
edit. Had the clause needed a word the body does not earn, the right outcome was
to leave the case red and report the engine's ceiling. That was the plan this run
started with.

**Result, with the margin stated rather than rounded.** Suite **75 of 85,
reliability 0.88**, from 74 and 0.87. Positives **38 of 40**, from 37 of 40. **No
other case moved in either direction**, which was the exact risk the deferral
named and which was established by re-running rather than assumed. `ap-pos-4`
passes at 0.397 against `agent-containment`'s 0.351, **margin +0.046**, narrow
enough that a description edit anywhere in the library could take it back. The
case's own note carries the before and after, so the file re-runs with the
history attached.

The swap, in full: 149 of 150 words before, and the new clause costs five, so
five came back from clauses that keep their meaning without them. **150 of 150
after**, at the cap and not over it. `agent-approval-paths` is **112 lines to
`wc -l`** against rule 4's cap of 120.

**A green trigger case says this skill is findable from that prompt and says
nothing at all about whether it helps.** The skill is `version: 3`,
`status: draft`, and unmeasured.

## 7. Reading queue: nothing appended, and that is the honest answer

Charter step 6 asks for every paper the skill needs and has not read, every
reference the cluster should have included, and every question the reading
raised. This run read no new paper, because it had no database and its subject
was the library's own machinery. The two residual questions #881 queued are
unchanged and still open. Appending anything here would be the padding the
charter forbids.

## 8. Registers

- **Two instances appended** to `INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed.md`, the fifth and sixth, with the new fact that one payload can carry several.
- **Second update** to `INC-2026-11-02-the-wakes-own-verification-command-does-not-exist-and-a-vendored-standard-prescribes-it.md`: the wrong path arrives once per red event.
- **One new ledger entry**, for the engineer: the trigger engine cannot separate two senses of one word, measured rather than argued, with the instrumentation half separated from the scoring half.
- `tools/incidents.py check`: 374 entries, 257 in the inbox, nothing malformed.
- `tools/ledger.py --check`: 0 blocking, at or under the recorded baseline.
- `tools/check_registers.py`: 0 blocking.
- `tools/ban_list.py`: clean on every file this run wrote.
- Conflict-marker grep over `docs/`, `prompts/`, `README.md`, `skills/`, `tests/`, `tools/`, `site/`: nothing.

## 9. Suites

- `tests/test_skill_receipts.py`: **36 passed, 0 xfailed**, was 35 passed and 1 xfailed.
- `test_skill_receipts`, `test_skill_triggers`, `test_skill_scope`, `test_skill_gate`, `test_panel_validator`, `test_validation_instruments` together: **260 passed, 3 skipped**.
- `node --test tests/skill-provenance.test.mjs`: **31 of 31**.
- `python3 skills/_validation/trigger_test.py`: **75 of 85, reliability 0.88**.
- `python3 skills/_validation/trigger_test.py --receipts`: all 10 receipts describe today's text, all 10 descriptions inside the 150-word budget, exit 0.
- `python3 tools/receipt_ranking.py --check`: no tie decides any of the 10 published receipts.
- `tools/skill_eval.py --check`: 10 of 10 conformant, 44 of 44 sections exercised, 323 of 323 criteria carry a certificate. The 119 advisory findings are the unrun ADR-40 item 6 task audits, which need the judge model.
- `tools/panel_validator.py` and `tools/panel_provenance.py`: 10 reviewed, 0 failing, 10 not fully measurable, each.

## 10. Board

Replied in first person to both. A `done` to the PM saying the hold is spent,
that the branch they held now conflicts and is the wrong one to merge, and
declining their offer of the green version with two commits dropped, because
that version isolated the wrong receipt and this one fixes the ranking. A `done`
to the engineer with all three handbacks accounted for, both corrections
accepted, and the third blocker conceded as the one this seat could not have
seen.
