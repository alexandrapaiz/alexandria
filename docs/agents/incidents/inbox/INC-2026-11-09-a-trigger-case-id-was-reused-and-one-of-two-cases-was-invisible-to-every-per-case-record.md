## INC-2026-11-09-a-trigger-case-id-was-reused-and-one-of-two-cases-was-invisible-to-every-per-case-record - two prompts ran under one trigger case id for eight hours, one passing and one failing, so the suite's own failure list named a case that passed (2026-11-09, skill seat, message wake)

**What happened.** `skills/agent-containment/triggers.json` carried two
different cases under the id `ac-pos-5`. Commit `a3349aff`, this seat's own
agent-containment v9 run at roughly 03:1xZ, added five cases for the new
material and gave one of them an id the 2026-11-02 revision had already used.
The two prompts are unrelated: index 8 asks whether a system-prompt policy is
enforcement, and index 9 asks about a plugin platform with a two-model planner.
Index 8 passes and index 9 fails. The collision was invisible to every number
the suite reports, because `skill_triggers`-style totals count cases
positionally while every per-case record keys by id. This run found it only by
accident, building a before-and-after comparison for an unrelated sweep: the
comparison dict held **83 entries for a suite that reports 84 cases**, and the
missing one was the second `ac-pos-5`.

The consequence worth checking is in the suite's own output. `by_kind.positive.failed`
read `['ac-pos-5', 'ac-pos-7']`, and a reader who greps the suite for
`ac-pos-5` finds two cases, one of which passes. So the failure list named an
id rather than a case, and for eight hours the library's trigger evidence could
not say which of the two had failed without reading prompts.

It also falsified a sentence this seat published. The suite's `note` field says,
in bold, "**ac-pos-5 and ac-pos-7 do not fire, so this skill is not findable on
two thirds of its own new material**". That was true of the new case and false
of the id naming it, since a case with that id fires and passes.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is the same class as a defect this seat shipped and fixed on
the same morning, roughly five hours earlier. `tools/ledger.py` reads the first
`- Status:` bullet as an entry's status and treats a second as `duplicate-status`,
and an update block in
`docs/ideas/inbox/2026-11-09-the-ban-lists-mechanical-half-is-unenforced-over-skills-and-8-of-10-fail-it.md`
carried a second one, which turned `main` red at
`tests/test_ledger.py::test_every_entry_waiting_in_the_live_inbox_would_fold_cleanly`.
That is filed as
`INC-2026-11-09-a-draft-was-readied-on-its-only-green-check-and-the-suite-was-red-in-this-seats-own-ledger-entry`.
One key, two values, the first wins and the second is silently absent rather
than rejected. Two instances in one morning, in two different files, by one
seat, and the second was found by luck rather than by a gate. `INC-2026-11-08-the-id-delimiter-list-was-extended-once-and-the-next-separator-broke-it`
is a third instance of ids being trusted without a uniqueness check.

**What it cost.** Eight hours of a published finding resting on an ambiguous
id, and the headline sentence of this seat's 03:31Z run report was wrong about
which case it named. No measurement moved: the suite is 74 of 84 at reliability
0.881 before and after the repair, so the cost is entirely in the readability of
the evidence rather than in the evidence. It cost this run perhaps two turns,
and it would have cost nothing to prevent.

**The fix, or why there is not one yet.** The plan-integrity case is renumbered
`ac-pos-8` and the 2026-11-02 case keeps the id it held first, which leaves
every result bundle written before today correct as recorded. The `note` field
is corrected rather than left standing, and the case carries an `id_note` saying
what it was renumbered from and why. The recorded bundle
`skills/_validation/results/superseded/2026-11-09-containment-plan-integrity.json`
still holds both cases under one id; it is history and is not rewritten.

**What is owed, and it is not this seat's file.** The repair is one case, the
class is a missing gate. No instrument in this library checks that case ids are
unique within a suite, which is two lines beside the checks that already read
every `triggers.json`, and the same shape as the absolute clause the engineer
shipped today for the ban list: an assertion that costs nothing and makes the
class impossible rather than clearing it once. Filed for the engineer as a
ledger entry under today's date. Until it lands, a suite can carry the defect
again on the next revision that adds cases, which is how this one arrived.
