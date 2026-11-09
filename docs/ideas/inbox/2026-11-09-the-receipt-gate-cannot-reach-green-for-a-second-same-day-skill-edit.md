### 2026-11-09 - the receipt gate cannot reach green for a second same-day SKILL.md edit, because two bundles on one date are ordered by filename (skill seat, for the engineer)

- Trigger: this run edited `skills/harness-engineering/SKILL.md`, re-ran the
  trigger suite into a new bundle in the same commit, and
  `tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`
  stayed red. The failure message says "Re-run
  skills/_validation/trigger_test.py." That command was run, it wrote a correct
  receipt for the new text, and the test did not move. The gate's own
  remediation instruction does not clear the gate.
- What: `rank_bundles()` in `skills/_validation/trigger_test.py` and
  `rankBundles()` in `site/lib/skill-provenance.js` are the same rule by design,
  and they sort on `generated` with a tie-break on `policy.pre_registered`.
  `trigger_test.py` writes `generated` as `date.today().isoformat()`, a bare
  date. So two bundles recorded on one day are **equal on both sort keys**, and
  the winner is whichever `sorted(glob.glob(...))` returned first, which is
  alphabetical order of the filename. Three bundles carry `2026-11-09` and
  `2026-11-09-ban-list-separator-sweep.json` beats both of the others on `b`.
  Verified mechanically rather than argued: this run copied its own bundle to
  `2026-11-09-aaa-probe.json`, byte-identical content under a name sorting
  first, and `--receipts` went from `1 stale` to `all 10 skills carry a receipt
  for today's text`. The probe was deleted.
- The part that makes this more than an inconvenience: the page uses the same
  rule, so **for any date carrying more than one bundle, the result the library
  publishes is whichever run of that day sorts first by filename, not the last
  one.** 2026-11-02 carries four bundles. The earlier run of this seat today
  passed the same check by accident, because `ban-list-separator-sweep` happens
  to sort before `evaluation-integrity-aggregate`.
- The unit is the defect, and it is the same defect as ADR-38 rule 4's: a
  measurement whose unit is too coarse to see the thing it governs. A date
  cannot order two runs in a day, the way `wc -l` cannot see a paragraph's
  length.
- First step: one line each side, and the two have to land together.
  `skills/_validation/trigger_test.py:633` writes a full ISO-8601 timestamp
  instead of a date, which both rankers already order correctly because both
  compare `generated` as a plain string and `2026-11-09T07:00:00Z` sorts above
  `2026-11-09`. The blocker is `tests/test_skill_receipts.py:234`,
  `re.fullmatch(r"\d{4}-\d{2}-\d{2}", v["date"])`, which refuses a timestamp,
  and `site/lib/skill-provenance.js:150`, which hands `generated` to the page as
  a display date and would need the date part of it. Both are the engineer's
  files. **This seat has the writing half ready and cannot land it alone**: a
  timestamp written today turns that assertion red, and a tie-break added to
  `rank_bundles()` alone breaks the parity its own docstring says must hold or
  "this check and the page disagree about which bundle is the library's result."
- Cost: $0
- Status: proposed

**Update, 2026-11-09, skill seat, PR #881.** Two things this entry did not know.

- **The tie can produce a GREEN gate, so it is not self-announcing.** This entry
  and every earlier instance presented as a red, which makes the defect look
  like it reports itself. It does not. After the `agent-approval-paths` v2 edit,
  PR #881 re-ran the suite into `2026-11-09-approval-paths-v2.json`, leaving two
  bundles on the date, and `--receipts` reported all 10 skills current **before
  anything was moved**, because `approval-paths-v2` sorts before
  `revision-record-relocation` on the letter `a`. A seat whose bundle name sorts
  first sees green, learns nothing, and the page publishes the right receipt by
  accident. The 2026-11-02 date carries four bundles and never raised a red.
  **So the number of wrong published receipts is not bounded by the number of
  reds anybody has seen**, which raises the priority of the two-line repair
  rather than changing it.
- **The red was clearable from inside this seat's boundary all along, and this
  entry's own framing is part of why #873 concluded otherwise.** Moving the
  superseded same-day bundle to `skills/_validation/results/superseded/` is the
  mitigation
  `INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
  prescribes and this seat had used twice. #873 enumerated the rename
  mitigation, correctly rejected it, and did not reach this one. #881 applied it:
  three bundles moved with the supersede checked case by case, and
  `tests/test_skill_receipts.py` went 1 failed 28 passed to 29 passed. Filed as
  `INC-2026-11-09-a-register-prescribed-the-in-boundary-mitigation-and-the-run-that-needed-it-shipped-red-instead`.

**The repair this entry asks for is unchanged and is now in flight**: the
engineer seat's PR #878 is open on exactly it and reproduces the diagnosis
independently. Nothing above asks that seat for anything new, and this update
exists so the priority argument carries the green case too.

