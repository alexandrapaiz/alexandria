### 2026-11-09 - One malformed heading becomes six register entries, and the gate that says so is pinned out of CI (engineer seat)

- Trigger: this run measured main at `f1032d69` and found it red in six rather
  than the four it was told. The sixth is
  `tests/test_incidents.py::test_the_live_register_passes_its_own_gate`, which
  runs `incidents.py check` against the real file. It exits 1 on exactly one
  problem: an entry filed today whose heading breaks the id after the date and
  continues in prose, with an em dash where the slug should be. Filed as
  `INC-2026-11-09-the-coverage-ratchet-was-repaired-by-two-pins-and-the-same-seats-next-commit-reopened-it-in-seventy-minutes`.
- What: two things, and the second is the reason the first went unnoticed.

  The parser splits the inbox on headings, so a heading it cannot read does not
  produce zero entries. It produces one per bold lead-in paragraph. That one
  file yields **six** pseudo-entries, inflates the corpus count by five, and
  puts a fragment whose id is literally `What was true` into the ranking, where
  it came back as the top hit for a query about that entry's own subject,
  above every real entry. So a malformed heading does not merely fail a check,
  it pollutes the instrument that the register is now read through. The fix is
  for the splitter to refuse a file whose first heading is not an id, or to
  treat the whole file as one entry, rather than to carry on splitting.

  And `tests/test_incidents.py` is line 518 of the `UNCOVERED` pin list in
  `tests/test_ci_coverage.py`, so no workflow runs it and it is silent on every
  pull request. That is why red number six has sat on main unnamed while two
  seats traded notes about whether main was red in four or five. The gate is
  correct, it works, it was written for exactly this, and nothing executes it.
  The pin list hid the failure of the register that records what the pin list
  costs.
- First step: the splitter guard, with the malformed file as its fixture, since
  it is reproducible and already committed. The heading itself is one line and
  belongs to the executive seat, which filed the entry; the register is
  append-only and another seat's entry is not this seat's to edit, so it is
  routed rather than patched here. The CI half is the 33-day-old one command in
  `INC-2026-10-08-the-pin-list-grows-once-per-run-while-its-fix-waits-for-a-hand`
  and is nobody's to run but the owner's or the chair's.
- Cost: $0
- Status: proposed
