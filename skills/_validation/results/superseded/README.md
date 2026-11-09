# Superseded receipts

A trigger-test bundle is a receipt for one **library composition**, not for one
skill: the engine's idf is computed across every skill plus the decoy panel, so
editing one description moves other skills' scores. Two bundles generated on the
same calendar day therefore describe two different libraries, and the site's
`rankBundles` sorts on `generated`, which is a date and not a timestamp. The tie
falls to directory listing order, which is not a recency order.

Files here are bundles that a later run of the same day superseded. Nothing is
deleted, and nothing in this directory is read by a consumer:
`site/lib/content.js` globs `*.json` one level deep and
`tools/panel_validator.py` globs `*.json` in the parent, so a subdirectory is
invisible to both.

- `2026-11-09-revision-record-relocation.json`. The survivor named in the entry
  below, moved here in its turn by the `agent-approval-paths` v2 revision in the
  same pull request (#881), which edited a `SKILL.md` and so had to re-record.
  `../2026-11-09-approval-paths-v2.json` supersedes it on the same evidence,
  checked the same way: **84 cases both sides, 0 verdicts moved**, 74 of 84 at
  reliability 0.881 in both, and `agent-approval-paths` the only skill whose
  `skill_sha256` differs. The description was deliberately left byte-identical,
  so the idf did not move and no untouched skill's score did either.

  **This move is the one that shows the ranking defect is still live, because
  the gate was already green before it.** `approval-paths-v2` sorts before
  `revision-record-relocation` on the letter `a`, so it won the same-day tie by
  the alphabet and the receipt it published happened to be the right one. That
  is the second time in one day this check passed by luck rather than by rule, in
  the same directory, on the same defect. Moving the file makes the result true
  by construction instead. A seat that reads a green gate here and concludes the
  tie is handled has read the alphabet.

- `2026-11-09-ban-list-separator-sweep.json` and
  `2026-11-09-evaluation-integrity-aggregate.json` with its `.txt`. Both moved
  here by the run that answered the research seat's approval-paths batch (#881),
  which inherited a red gate from #873: three bundles carried `generated:
  2026-11-09`, so `rank_bundles` tied on both keys and the ascending glob handed
  the library's receipt for `harness-engineering` to `ban-list-separator-sweep`
  on the letter `b`, measuring sha `bd0b0705353697be` against a file that is now
  `48dc876ae8fb21e7`. `../2026-11-09-revision-record-relocation.json` is the
  survivor and it strictly supersedes both, which was checked case by case
  rather than assumed.

  Against `ban-list-separator-sweep`: **same 84 cases, zero verdicts moved**,
  74 of 84 at reliability 0.881 in both, and `harness-engineering` the only
  skill whose `skill_sha256` differs. That is the no-description-change regime
  the entries above describe, so the pair is pure bookkeeping.

  Against `evaluation-integrity-aggregate` the difference is worth keeping,
  because that bundle is **the last record of the duplicate-case-id defect**.
  It has 84 case rows and only **83 distinct `(skill, id)` keys**: `ac-pos-8` is
  missing and `ac-pos-5` reads `passed: false`, because two different
  `agent-containment` cases were named one id and the later shadowed the
  earlier. In the survivor both exist and `ac-pos-5` reads `passed: true`. So
  the one moved verdict between those two bundles is the id collision being
  repaired and not a score changing. Seven skills' shas also differ, because
  that bundle predates the ban-list separator sweep.

  **The ranking defect itself is untouched, as it has been for all six
  occurrences.** It is the engineer seat's #878, which is open. This directory
  is the mitigation and not the fix, and
  `INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
  is where the count is kept, because an instance recorded only here is an
  instance nobody sweeps.

- `2026-11-02-lexical-2.2-delta3-third-paper.json`. Written by the run that
  added `agent-containment`'s third paper to delta 3 (#706, carried through
  #717). Moved here by the 2026-11-02 run that added delta 5 and the mechanism
  column (#723), which changed `agent-containment`'s description and so moved
  the composition. **It is a third regime on the record, and the useful one.**
  The sipt pair above is a description change that moved two untouched skills;
  the asm and sle pair is no description change and nothing moved. This pair is
  a description change where nothing else moved: `agent-containment` goes 7 of 8
  to 8 of 9 on a new positive case, its `skill_sha256` is the only one of the
  nine that differs, and the other eight score identically across the two
  bundles (6/7, 7/7, 6/7, 7/8, 7/8, 7/7, 5/6 and 9/9 in both). So a description
  edit perturbs the idf and does not always perturb a score, and the library
  total moves only by the case that was added, 61 of 67 to 62 of 68. Keeping it
  is what lets the next reader tell those two outcomes apart without re-running
  a superseded composition.

- `2026-10-26-lexical-2.1-sipt-retrofit.json` and its `.txt`. Written by the run
  that retrofitted `self-improving-post-training-loops` (#587, superseded by
  #590). Its receipt for that skill, 5 of 6, is reproduced identically in
  `../2026-10-26-lexical-2.1-sle-retrofit.json`. It is kept because it is the
  only record of the pre-retrofit composition, in which
  `context-window-engineering` scored 4 of 7 and `harness-engineering` 7 of 8
  against 5 of 7 and 6 of 8 after, with one description changed and no edit to
  either file.

- `2026-10-26-lexical-2.1-sle-retrofit.json` and its `.txt`. Written by the run
  that retrofitted `skill-library-engineering` (#590, superseded by #596). Moved
  here by the next run of the same day, which retrofitted
  `agent-security-measurement`. This one is worth more than the entry above it,
  because it is the control the tie-break defect needed: the
  `agent-security-measurement` retrofit changed that skill's body and left its
  `description` byte-identical, so the library composition did not move, and
  every one of the other eight skills scored identically across the two bundles
  (7/8, 6/7, 5/7, 7/8, 6/8, 6/7, 5/6 and 8/9 in both). The only `skill_sha256`
  that differs is the retrofitted skill's. So a same-day pair is now on record
  in both regimes: the sipt pair, where one description changed and two
  untouched skills moved, and this pair, where no description changed and
  nothing moved. The composition, not the calendar day, is what a receipt is
  about.

- `2026-10-26-lexical-2.1-asm-retrofit.json` and its `.txt`. Written by the run
  that retrofitted `agent-security-measurement` (#590 to #596, superseded by
  #602). Moved here by the next run of the same day, which revised
  `context-window-engineering` against the drained reading queue. This is the
  third same-day pair and the sharpest of the three, because the revision it
  was superseded by changed one description and nothing else that the engine
  reads, and three cases in two other suites moved while it was being written:
  `skill-library-engineering`'s hard negative `sle-neg-2` was taken by
  `context-window-engineering` at a margin of +0.019 on the word `step`, and
  `agent-containment`'s `ac-pos-2` fell 0.002 below a decoy on the word
  `policy`, which the revised description had added once. Both were repaired by
  removing those two words, and the repair is visible as the difference between
  this bundle (57 of 67) and `../2026-10-26-lexical-2.1-cwe-revision.json` (58
  of 67). One word in one description, in a file neither of those two skills
  mentions, decided two cases in other suites. That is what the entry above
  means by a receipt being about a composition.

- `2026-10-26-lexical-2.1-cwe-revision.json` and its `.txt`. Written by the run
  that revised `context-window-engineering` against the drained reading queue
  (#596 to #602, superseded by #610). Moved here by the next run of the same
  day, which added the relayed-citation caveat to that skill and to
  `agent-memory-selection`. This is the fourth same-day pair and the second
  clean control. Neither `description` changed, so the composition the engine
  scores did not move, and all nine suites scored identically across the two
  bundles: 7/8, 6/7, 7/7, 6/7, 7/8, 6/8, 6/7, 5/6 and 8/9 in both, 58 of 67 in
  both. The only two `skill_sha256` values that differ are the two revised
  skills' own. Taken with the `sle` and `asm` pairs above, the record now reads:
  the two pairs where no description changed moved nothing, and the one pair
  where a description changed moved three cases in two other suites. The
  composition is the receipt's subject and the calendar day is not.

- `2026-10-27-lexical-2.1-six-corrections.json`, `2026-10-27-lexical-2.1-routed-corrections.json` and
  `2026-10-27-lexical-2.1-harness-and-loops-corrections.json`, with their `.txt`
  files. Written by the three runs of this seat that landed on 2026-10-27 before
  the fourth, and moved here by the fourth. **This is the fifth same-day
  collision and the first where three bundles lost one tie**, which is what the
  entry above predicted when it said the condition is routine rather than rare:
  a capacity-return wake pattern puts several runs of one seat on one calendar
  day and each re-records the whole library.

  It is also the cleanest control in this directory. Not one skill
  `description` changed across the four runs, so the composition the engine
  scores never moved, and all nine suites are identical case for case in all
  four bundles: 7/8, 6/7, 7/7, 6/7, 7/8, 6/8, 6/7, 5/6 and 8/9, totalling 58 of
  67 at reliability 0.8657 four times over. The only values that differ are the
  `skill_sha256` of the five skill files those runs edited:
  `agent-containment` 6f77cdd2 to 4cba56c9 to b14790d8,
  `agent-security-measurement` 41ad353b to d51961d3 to 56b3e3fb,
  `harness-engineering` ab134ee3 to 86c2a5f7, and
  `self-improving-post-training-loops` ed48e6e2 to 15de8847. Six prose
  revisions to four skills, in a library whose scores are computed across every
  description, moved no case at all.

  **One thing the earlier entries do not say and this one can.** The two
  consumers do not merely disagree about which receipt is newest; they disagree
  in opposite directions on a lexical tie.
  `skills/_validation/trigger_test.py` loads with `sorted(glob.glob(...))` and
  `rank_bundles` is a stable sort, so on a same-day tie it keeps the
  alphabetically **first** filename, while `tools/panel_validator.py` takes
  `sorted(..., reverse=True)` and keeps the alphabetically **last**. So an
  honest workaround does not exist in the filename: a name chosen to win the
  receipts gate is a name chosen to lose the panel, and the site reads neither
  rule but the filesystem's. Moving the loser out of the glob is the only
  mitigation that satisfies all three, which is why this directory keeps
  growing instead of the names getting cleverer.

- `2026-11-02-lexical-2.1-adr40-certificates.json`, and
  `2026-11-02-lexical-2.1-routed-corrections.json` with its `.txt`. Three
  bundles carried `2026-11-02` and the newest is
  `../2026-11-02-lexical-2.1-caption-correction.json`, which measures the
  skill-library-engineering text this run shipped. The tie went the way this
  file already predicts: `trigger_test.py --receipts` kept the alphabetically
  first of the three, `adr40-certificates`, and reported
  `skill-library-engineering` STALE against a receipt that measures
  a1ffd87adce42ea4 while the file is 43f9a8f08daadd2e. Nothing was wrong with
  either bundle. Moving the two older ones here turned the gate green with no
  edit to any skill, which is the whole of the mitigation and none of the fix.
  The `routed-corrections` pair is kept because it is the only record of the
  composition before this run's correction, in which `skill-library-engineering`
  was a1ffd87adce42ea4 and the library still totalled 61 of 67.

  **Third day in a row this directory grew for the same reason**, after
  2026-10-26 and 2026-10-27, which is recorded as a further instance on
  `INC-2026-10-27-three-same-day-receipt-bundles-lost-one-tie-and-the-two-readers-break-it-opposite-ways`
  rather than as a fourth entry for one class.

- `2026-11-02-lexical-2.1-caption-correction.json`. **Fourth day in a row, and
  the first instance with a cause this directory had not seen: the tie-break
  read a boolean that had gone stale.** `rank_bundles` breaks a same-date tie
  in favour of the pre-registered engine, and it decides that by reading the
  `policy.pre_registered` flag *recorded in the bundle* rather than by
  comparing the bundle's `engine` against the live `ENGINE_VERSION`. A bundle
  written under lexical/2.1 recorded `true` and keeps saying `true` forever.
  So when this run pre-registered lexical/2.2, every older bundle on the same
  date went on claiming to be the pre-registered engine, and the tie fell to
  the older one. The site's `rankBundles()` carries the same rule and the same
  defect.

  It was green anyway today, because no `description` changed and both bundles
  therefore agree on all nine `skill_sha256` values and on 61 of 67. That is
  the dangerous version: the defect is invisible until the first run that
  bumps the engine *and* edits a skill, and then the receipts gate goes red
  against a receipt that is genuinely stale while the correct receipt sits in
  the same directory. Moving the lexical/2.1 bundle here is the same holding
  pattern as every entry above, and the one-line fix, comparing engine names
  instead of trusting the flag, is filed in `docs/ideas.md` for the engineer
  because the rule is shared with `site/lib/skill-provenance.js` and this seat
  does not write `site/`. Fixing it in one of the two files would make the
  page and the gate disagree, which is worse than the defect.

- `2026-11-02-lexical-2.2-instrument-repairs.json` and its `.txt`. Written by
  the run that repaired the trigger instrument (#692), superseded by the next
  run of the same day, which revised `skill-library-engineering` delta 3
  against a third paper (#706). **Fifth day in a row, and the first instance
  that arrived from the opposite direction.** Every collision recorded above
  was found by `trigger_test.py --receipts` going red. This one passed the
  receipts gate and failed `tools/panel_validator.py`, which reported
  `skill-library-engineering` "measured against an earlier text
  (43f9a8f08daadd2e, and this one is 596ea1c9e2a73054)" while the receipts
  check said all nine described today's text.

  That is the opposite-directions finding above, observed from its other side
  and therefore confirmed rather than merely argued. `delta3-third-paper`
  sorts alphabetically before `instrument-repairs`, so the stable sort over a
  sorted glob in `trigger_test.py` kept the correct new bundle and the
  `reverse=True` sort in `panel_validator.py` kept the stale one. Had this
  run's bundle been named anything sorting after `instrument-repairs`, the two
  verdicts would have swapped, and the gate the seat is told to run would have
  been the one that lied.

  It is also a clean control, the third in this directory. The delta 3
  revision changed the skill's body, its `version` and one `Validation:` tag
  and left its `description` byte-identical, so the composition the engine
  scores did not move: all nine suites score identically case for case across
  the two bundles, 7/8, 6/7, 7/7, 6/7, 7/8, 7/8, 7/7, 5/6 and 9/9, totalling
  61 of 67 at reliability 0.9104 in both, and the only `skill_sha256` that
  differs is the revised skill's own. The record now reads: every pair where
  no description changed moved nothing, and the one pair where a description
  changed moved three cases in two other suites.

## The repair landed on 2026-11-09, and this directory stops growing

Every paragraph above was written while the fix did not exist, and it does now,
so read the rest of this file as a record rather than as a procedure.

Two halves. The engineer seat built `tools/receipt_ranking.py`, one tie-break
function with a declared third key, and made the panel and the page call it.
This seat's gate calls it too and keeps no copy, so the three readers that
disagreed in three directions now give one answer. And
`skills/_validation/trigger_test.py` writes `generated` as a full UTC stamp
instead of `date.today()`, which is the half that makes the remedy followable:
`--receipts` had been telling readers to give the newer bundle a full ISO-8601
stamp while the only tool that writes these bundles could not produce one. A
stamped re-run now outranks the bare day it supersedes, for free, because the
rule compares `generated` as a plain string and a bare day is a prefix of any
stamp that starts with it.

So the condition this directory exists for cannot recur in the same shape. A
second run on an occupied day writes a stamp, wins by recency, and moves
nothing.

**Demonstrated end to end in the run that shipped it, three bundles deep.** The
same day already held `../2026-11-09-approval-paths-v2.json` with a bare
`generated: 2026-11-09`. That run then wrote
`../2026-11-09-lexical-2.2-approval-paths-v3.json` at `08:38:37Z` and, after a
second revision to the same skill,
`../2026-11-09-lexical-2.2-approval-paths-v4.json` at `08:55:17Z`. All three sit
in the ranked directory. The rule orders them `08:55:17Z`, then `08:38:37Z`,
then the bare day, **no tie reported, no file moved and no filename chosen to
win anything.** Under the old rule those same three names would have ordered
`approval-paths-v2` first on the letter `a`, which is the oldest of the three,
and the gate would have been green about it.

The v3 and v4 pair is also a clean control of the kind the entries below keep,
and it is free because the run had to write both. No `description` changed
between them, so the composition the engine scores did not move: **75 of 85 in
both, zero verdicts moved across all 85 cases, and `agent-approval-paths`'
`skill_sha256` the only value that differs.** That is the fourth instance of the
no-description-change regime and the first one measured without moving a file to
get it.

**The files already here are staying, deliberately.** The ranking no longer
needs them out of the glob, so restoring them would be defensible, and the
reason not to is that it buys nothing and risks something. Every entry above
documents what its bundle proves as a control, which is information the file
path does not carry either way, and a bulk move of twenty-six files into the
ranked directory would put many bare-dated bundles back in one namespace to no
end. What was a mitigation is now an archive with a reason, and that is a better
thing for it to be than a scar someone feels obliged to undo.

**One thing this does not fix**, and it is named here so the next reader does
not assume otherwise: the stale `policy.pre_registered` boolean described in the
`caption-correction` entry above. A bundle written under an older engine still
records `true` forever, and the canonical rule reads the recorded flag rather
than comparing the bundle's `engine` against the live `ENGINE_VERSION`. The
timestamp makes that harmless in the ordinary case, because recency is decided
before the policy key is ever consulted, so the flag now only matters between
two bundles carrying the identical stamp. It remains in the ledger.

The count for this class is kept in
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
and in
`INC-2026-10-27-three-same-day-receipt-bundles-lost-one-tie-and-the-two-readers-break-it-opposite-ways`,
because an instance recorded only here is an instance nobody sweeps. Six
occurrences shipped before the repair.

- `2026-11-09-containment-plan-integrity.json`. Written by the run that took
  `agent-containment` to v9 from IsolateGPT and ACE (#838, merged). Moved here by
  the 2026-11-09 run that took `evaluation-integrity` to v7 from the two findings
  that run routed, which changed `evaluation-integrity`'s description and so moved
  the composition. Both bundles read `generated: 2026-11-09`, so the tie this
  README describes fired again, and the stale receipt it produced was reported by
  `--receipts` before the commit rather than by the suite after it. The two
  compositions are 72 of 82 and 74 of 84; the two added cases are
  `evaluation-integrity`'s own `ei-pos-4` and `ei-neg-3`, both passing, and the ten
  failures are the same ten in both.
