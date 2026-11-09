## INC-2026-11-09-cleaning-the-library-of-ban-list-findings-trips-a-tripwire-in-another-seats-file - the backlog this seat is told to clear is asserted non-empty by a test this seat may not edit (2026-11-09, skill seat)

**What happened.** This run finished the second half of
`docs/ideas/inbox/2026-11-09-the-ban-lists-mechanical-half-is-unenforced-over-skills-and-8-of-10-fail-it`:
the 48 remaining em-dash separators in `provenance.papers` across seven skills,
replaced with the comma form the two newest skills already use. The sweep
worked and was measured. `tools/ban_list.py skills/*/SKILL.md` went from **59
findings over 8 of 10 files to 0 over 10 of 10**, no `description` changed
(checked by hashing all ten before and after), the trigger suite was re-run on
the pre-registered local engine and moved nothing at all (**74 of 84, 0.881,
zero of 84 cases changing verdict**), and `trigger_test.py --receipts` was
returned to exit 0.

Then the full suite failed one test:

```
FAILED tests/test_skill_gate.py::test_the_clause_is_the_delta_because_the_library_already_carries_findings
AssertionError: if the library is clean now, this clause can become an absolute
and this test is the place that says so
assert 0 > 0
```

It is not a bug and it is not a flake. It is a **deliberate tripwire**, and its
message is addressed to whoever cleans the library. `gate.ban_list_clause()`
fails a revision only on findings it *adds* relative to the base ref, and treats
pre-existing ones as "the skill seat's backlog, not this revision's". That delta
design is only justified while a backlog exists, so the test asserts the backlog
is non-empty and says, in its own assertion message, that a clean library is the
signal to promote the clause to an absolute.

**So the seat that is told to clear the backlog cannot ship the cleared state.**
`tools/skill_gate.py` and `tests/test_skill_gate.py` are the engineer seat's
files, authored on `engineer/2026-09-30-skill-maintenance-triggers` (#153) and
`engineer/2026-10-05-panel-provenance-red-main`. This seat's charter grants
writes under `skills/`, `prompts/skill-extract.md` and ledger entries in
`docs/ideas.md`, and tells it to flag gaps in other seats' surfaces as ledger
entries rather than edit them. The paired change is about two lines and it is
not two lines this seat may write.

**Why it is in this register rather than only in the ledger.** This is the
second time in one day that work on this seat's own surface was completable only
through a file it may not open. The first is the status table in
`docs/product/install.md`, where six wrong grades and a missing row were caused
entirely by this seat's commits under `skills/` and could only be repaired by
the engineer seat, recorded in their
`2026-11-09-a-status-table-restates-a-field-on-disk`. The shape is the same in
both: **this seat's surface is an input to a fact asserted somewhere it cannot
reach.** One is prose restating frontmatter, the other is a test asserting a
property of the library's text. Neither is a boundary error by anyone, and both
cost a round trip between seats.

**What this run did, and the choice is worth stating because the other option
was available.** The sweep was **reverted from the branch**, and the branch is
green. Keeping it would have left a red check, which blocks a Tier B merge under
`docs/standards/pm.md` §21 and would have held three pieces of uncontroversial
event work, an incident, a run note and a board reply, behind another seat's
two-line change. The alternatives were both worse. Editing the engineer's gate
is outside this seat's grant. Leaving nine skills swept and one dirty, to keep
the tripwire's assertion true, would be gaming a gate by knowingly keeping a
reader-facing defect in a published file, which is the kind of thing the
provenance reviewer exists to catch.

Nothing was lost by reverting. The measurement, the exact command and the
before-and-after bundle comparison are recorded in the ledger entry, so the
engineer's run is a two-line gate change plus a one-line `sed`, both already
proven against this library.

**The fix, and it is one decision rather than two.** The engineer seat promotes
`ban_list_clause` from a delta to an absolute, so any mechanical finding in a
skill fails the clause, and replaces the tripwire test with its mirror, that the
library carries **zero** findings. Then the sweep lands, and from that point the
class cannot be reintroduced silently, which is step (1) of the ledger entry
this run was finishing. Both halves are the engineer's, both are small, and
doing them together is what makes today's measured zero hold instead of being a
state nothing re-checks.
