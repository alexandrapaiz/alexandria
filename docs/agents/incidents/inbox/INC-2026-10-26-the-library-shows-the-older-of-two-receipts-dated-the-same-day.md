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
