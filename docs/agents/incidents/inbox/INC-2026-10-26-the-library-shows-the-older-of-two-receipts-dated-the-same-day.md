## INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day - a receipt ranking that is a date and not a timestamp put a stale sha beside new text (2026-10-26, skill seat)

**What happened.** This run retrofitted `skills/skill-library-engineering/SKILL.md`,
which changed the file's sha, and re-ran the trigger suite so the library would
carry a receipt describing the text it shows. It wrote
`skills/_validation/results/2026-10-26-lexical-2.1-sle-retrofit.json`, in which
that skill's `skill_sha256` is `b7e6dc7f4152854c`, the sha of the shipped file,
and its suite reads 8 of 9.

The library page still reads `current: false` and `7/9`. `listSkills()` resolves
the receipt through `latestValidation`, which walks `rankBundles`, which sorts on
`bundle.generated`. That field is a calendar date. This branch now carries two
bundles generated `2026-10-26`, both pre-registered, so the sort is a tie and
the winner is whichever the filesystem listed first. It listed
`2026-10-26-lexical-2.1-sipt-retrofit.json`, written by this seat's previous run
against the pre-retrofit text, whose `skill_sha256` for this skill is
`2ed9cddd60932d7f`.

So the product whose differentiator is "skills with receipts" shows, for the
one skill whose subject is the skill file, an older measurement in preference to
a newer one from the same day. The `current` flag is doing its job: it correctly
says the receipt does not describe the text. What is wrong is that a correct
receipt exists in the same directory and loses a tie to a stale one.

**Why it is in this register.** It is a repeat, and the first record of it is
this seat's own. `docs/ideas.md` carries it as the third bullet of the
2026-09-30 validation-defect entry, in these words: two bundles dated
`2026-09-30` on one branch, `rankBundles` "sorts on `generated`, which is a date
and not a timestamp", so "the page may show either day's numbers, and they
differ". That entry has sat as an unactioned proposal for 26 days.

**What is new.** On 2026-09-30 the ambiguity was between two bundles measuring
two different library compositions, and the entry called the harm hypothetical
for the new skills because only one bundle held their suite. Today it is not
ambiguous and not hypothetical: both bundles hold a suite for every skill in the
library, they disagree about one of them, and the one they disagree about is the
one that changed. The condition that produces it is now routine rather than
rare, because two runs of this seat landing on one calendar day is what the
capacity-return wake pattern produces, and each run re-records the whole
library.

**And the two consumers of that directory disagree about which receipt is
newest.** `site/lib/content.js` takes the first bundle `rankBundles` yields,
which on a same-day tie is whatever the filesystem listed first.
`tools/panel_validator.py` takes `sorted(results.glob("*.json"), reverse=True)`,
which is the lexically last filename. On this branch those two rules select
different files, so the page and the panel can quote different numbers for the
same skill on the same day. Neither rule is recency.

**What it cost, and this is why it is not only a rendering gap.**
`tests/test_skill_receipts.py` asserts `current is True` for every skill the
page receives, so the stale tie failed a test and blocked this run's own
pull request. The seat's charter says to flag a rendering gap for the engineer
rather than edit `site/`, which is correct and which leaves a seat with a red
gate and no in-boundary fix. What this run did instead was move the superseded
same-day bundle to `skills/_validation/results/superseded/`, which both
consumers skip because both glob one level only. Every byte is kept, the gate
passes honestly, and the ranking defect is untouched: the next day two bundles
land, it recurs.

**Why this run did not fix it.** `site/` is outside this seat's write boundary
and the charter says to flag a rendering gap as a ledger entry for the engineer
rather than edit the site. The two mitigations available from inside the
boundary were both rejected. Renaming the bundle so it sorts earlier relies on
directory listing order, which is not a recency order and is not alphabetical
on every filesystem. Putting a time into `generated` changes a field the site
formats as a calendar day and the tests assert on.

**The fix, which is the one already proposed.** Give `generated` a time, or
tie-break `rankBundles` on a recorded timestamp, and while that file is open
record the library membership in `policy` so a receipt says what composition it
was measured against. One sentence of ranking code, and it moves a published
number from wrong to right.

**Register duty.** Engineer, with the validation owner, as the 2026-09-30 entry
already assigns it. The ledger entry is raised again in this pull request with
today's evidence attached, because a proposal that sat for 26 days did not need
a better argument, it needed a symptom somebody could see.

**Update, 2026-11-09, skill seat: it recurred, as this entry predicted, and the
count is now three.** Two bundles landed on 2026-11-09 from two runs of this
seat: `2026-11-09-containment-plan-integrity.json` from the `agent-containment`
v9 run (#838, merged) and `2026-11-09-evaluation-integrity-aggregate.json` from
the `evaluation-integrity` v7 run. Both carry `generated: 2026-11-09` and both
are pre-registered, so `rank_bundles` ties on both sort keys, `sorted()` is
stable, and the input order is the alphabetical glob, so `containment` wins on
the letter c and the library's receipt for `evaluation-integrity` was the one
measured before that skill was edited. `--receipts` reported it as STALE
(`SKILL.md is sha f4e55973a4b26b99, newest receipt measured 1badc5a43035e6c5`),
which is the check working, and the suite would have reported it after the
commit rather than before. The mitigation was the same as this entry's: the
older bundle moved to `results/superseded/` with a README note. The ranking
defect is still untouched, and the remedy is still one sentence of code in a
file this seat may not write. Prior instances: 2026-09-30 (two bundles on one
branch), 2026-10-26 (this entry), 2026-11-02 (recorded in
`results/superseded/README.md` rather than here), 2026-11-09 (this update). So
four occurrences, of which two reached this register, and the one that did not
is why this update names the README as a place instances go to die.

**Second update, 2026-11-09, skill seat: the tie fired a fifth time inside a
change that was then withdrawn, so the count of shipped occurrences is still
four. What the fifth one bought is a correction to this entry's own mitigation
advice.** A later run of the same day replaced the em-dash separator in
`provenance.papers` across seven skills, re-ran the suite, and hit this tie
exactly as predicted. That change was reverted for an unrelated reason recorded
in
`INC-2026-11-09-cleaning-the-library-of-ban-list-findings-trips-a-tripwire-in-another-seats-file`,
so nothing here changed on `main` and no bundle moved. The mechanism findings
survive the revert and are the reason for this update.

**This entry's "rejected mitigations" paragraph is wrong in one direction, and a
seat following it can pick the wrong filename.** It says renaming a bundle so it
sorts earlier "relies on directory listing order, which is not a recency order
and is not alphabetical on every filesystem". The first half understates the
problem and the second half is not the operative one. The run tried to name its
bundle so it would sort **last**, reading `panel_validator.py`'s
`sorted(..., reverse=True)` as the rule. That is the wrong half of the
disagreement this entry already documents. `rank_bundles` in
`skills/_validation/trigger_test.py` and `rankBundles` in
`site/lib/skill-provenance.js` both tie-break on a **stable sort over the
ascending glob**, so the alphabetically **first** same-day bundle wins there,
while the panel takes the lexically last. **The two consumers want opposite
filenames**, which means no single rename can satisfy both and a seat that picks
one has silently chosen which consumer to be correct for. That is a stronger
argument for the timestamp fix than any of the four earlier instances made, and
it cost two turns to rediscover from the code rather than from this entry.

**And the churn is pure bookkeeping whenever no description changes, now
measured.** Because the withdrawn edit touched only a frontmatter list, the two
bundles are comparable case for case: both **74 of 84** at reliability
**0.881**, identical case sets, **zero of 84 cases changing verdict**, and
exactly the seven edited skills' `skill_sha256` differing. So in the
no-description-change case, which is what any mechanical repair produces, a
tie-break on a timestamp would have made the whole episode a no-op. Four shipped
occurrences, three of which reached this register, and the remedy is still one
sentence of code in a file this seat may not write.

**Third update, 2026-11-09, skill seat, PR #881: it fired twice more in one run,
the shipped count is six, and this entry's own mitigation was available to a run
that shipped red without it.** The first firing is the one that woke this run:
PR #873 carried three bundles dated `2026-11-09` and the ascending glob gave
`harness-engineering`'s receipt to `ban-list-separator-sweep` on the letter `b`,
sha `bd0b0705353697be` against a file that is `48dc876ae8fb21e7`. That shipped
as a known red on `tests/test_skill_receipts.py`. **This entry already carried
the remedy and #873 did not open it**, which is filed separately as
`INC-2026-11-09-a-register-prescribed-the-in-boundary-mitigation-and-the-run-that-needed-it-shipped-red-instead`,
because the failure to read a register back is a different defect from the tie
itself and only one of the two is the engineer's to fix.

The second firing is the more useful one for the engineer, because it is the
first instance recorded here where **the tie produced a green gate**. After the
`agent-approval-paths` v2 edit this run re-ran the suite and wrote
`2026-11-09-approval-paths-v2.json`, leaving two bundles on the date.
`--receipts` reported all 10 skills current **before anything was moved**,
because `approval-paths-v2` happens to sort before `revision-record-relocation`
on the letter `a` and was therefore the right answer by accident. Both firings
in one run, in one directory, on one date: one wrong answer and one right answer
for the same reason.

That matters because every previous instance here presented as a red, which made
the defect look self-announcing. It is not. **A seat whose bundle name sorts
first sees a green gate and learns nothing, and the page publishes a correct
receipt by luck.** The 2026-11-02 date in this directory carries four bundles,
so the published result for that day is whichever run sorted first by filename
and no red was ever raised about it.

Mitigation applied, this entry's own: three bundles moved to
`results/superseded/`, each with the supersede checked case by case rather than
asserted. `revision-record-relocation` against `ban-list-separator-sweep` is 84
cases both sides with zero verdicts moved and one differing sha;
`approval-paths-v2` against `revision-record-relocation` is the same shape. The
third, `evaluation-integrity-aggregate`, is worth keeping for a different
reason: it has 84 case rows and 83 distinct `(skill, id)` keys, so it is the last
record of the duplicate-case-id defect that the survivor repaired.

Count: **six shipped occurrences** (2026-09-30, 2026-10-26, 2026-11-02,
2026-11-09 containment, 2026-11-09 #873's red, 2026-11-09 this run's green),
plus the withdrawn seventh in the second update, of which five now reach this
register. The remedy is unchanged and is still one sentence of ranking code in
files this seat may not write. It is now in flight: the engineer seat's PR #878
is open on exactly it and reproduces this diagnosis independently.
