## INC-2026-11-09-two-result-bundles-share-a-date-and-the-second-is-unreachable-so-the-gate-cannot-go-green - the third same-day instance of one key too coarse to hold two records, and this one makes a gate unreachable (2026-11-09, skill seat)

**What happened.** This run edited `skills/harness-engineering/SKILL.md`, which
makes every recorded trigger receipt stale, and re-ran the suite into a new
bundle in the same commit, which is what the format contract and the engineer's
own handoff both instruct.
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`
stayed red, and its failure message is "Re-run
skills/_validation/trigger_test.py." That command had just been run and had
written a correct receipt for the new text. `rank_bundles()` in
`skills/_validation/trigger_test.py`, and `rankBundles()` in
`site/lib/skill-provenance.js` which is deliberately the same rule, sort on
`generated` with one tie-break on `policy.pre_registered`. `trigger_test.py`
writes `generated` as `date.today().isoformat()`, so two bundles recorded on one
day are equal on both keys and the winner is whichever `sorted(glob.glob(...))`
returned first, which is alphabetical by filename. Three bundles carry
`2026-11-09` and `2026-11-09-ban-list-separator-sweep.json` beats the other two
on `b`. Checkable without being here: copy the newest bundle to
`skills/_validation/results/2026-11-09-aaa-probe.json`, byte-identical content
under a name that sorts first, and `--receipts` goes from `1 stale` to `all 10
skills carry a receipt for today's text`. This run ran that probe and deleted it.

**Why it is in this register.** The standing rule binds on repeat and this is
the third instance in one day, by one seat, of one class: a key too coarse to
hold two records, where the first wins and the second is silently absent rather
than rejected. The first took `main` red,
`- Status:` appearing twice in one ledger entry so the fold gate read
`duplicate-status`. The second is
`INC-2026-11-09-a-trigger-case-id-was-reused-and-one-of-two-cases-was-invisible-to-every-per-case-record`,
where `ac-pos-5` named two different cases and the failure list printed an id
that a passing case also held. This third one is the worst of the three, because
the first two produced a wrong record and this one produces **a gate with no
green state**: a seat that edits a `SKILL.md` for the second time in a day
cannot satisfy the check by doing what the check tells it to do.

It is also the second instance today of the related class the ADR-38 work is
full of, a measurement whose unit cannot see what it governs, already filed twice
as `INC-2026-11-09-the-length-gate-reports-a-pass-in-a-unit-that-stopped-measuring-when-the-files-changed-shape`
and `INC-2026-11-09-a-library-bar-was-measured-in-a-unit-that-does-not-match-the-rules-subject-twice-in-one-day`.
A date cannot order two runs in a day for the same reason `wc -l` cannot see a
paragraph's length.

**What it cost.** About twenty minutes of this run, and one pull request that
ships red on one test of 29 in its suite rather than green. The larger cost is
not this run's and it is reader-facing: the page uses the same ranking rule, so
on any date carrying more than one bundle the result the library publishes is
whichever run of that day sorts first by filename rather than the last one.
2026-11-02 carries four bundles. This seat's own earlier run today passed the
same check by luck, because `ban-list-separator-sweep` happens to sort before
`evaluation-integrity-aggregate`.

**The fix, or why there is not one yet.** One line each on two sides and they
have to land together, filed as
`docs/ideas/inbox/2026-11-09-the-receipt-gate-cannot-reach-green-for-a-second-same-day-skill-edit.md`.
This seat writes `generated` and would write a full ISO-8601 timestamp, which
both rankers already order correctly because both compare the field as a plain
string. It cannot land alone:
`tests/test_skill_receipts.py:234` asserts `re.fullmatch(r"\d{4}-\d{2}-\d{2}",
v["date"])` and would refuse it, and `site/lib/skill-provenance.js:150` hands the
field to the page as a display date. Both are the engineer's files, and adding a
tie-break to `rank_bundles()` alone would break the parity its own docstring
says must hold. The one thing this run did not do is rename its bundle to win
the alphabetical sort, which would have turned the gate green and left the
defect invisible to the next seat.
