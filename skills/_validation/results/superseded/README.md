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

The real repair is in the ledger and in
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`:
tie-break on a timestamp, and record the library membership in the bundle so a
receipt says what composition produced it. This directory is a holding pattern
until that lands, not the fix.
