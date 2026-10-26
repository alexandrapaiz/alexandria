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

The real repair is in the ledger and in
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`:
tie-break on a timestamp, and record the library membership in the bundle so a
receipt says what composition produced it. This directory is a holding pattern
until that lands, not the fix.
