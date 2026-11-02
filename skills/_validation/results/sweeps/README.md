# Sweeps and gates, not receipts

A trigger-test receipt is a bundle with `generated`, `library`, `suites` and a
per-skill `skill_sha256`. Both consumers of the parent directory assume that
shape: `site/lib/content.js` globs `*.json` one level deep and
`tools/panel_validator.py` globs `*.json` in the parent, and neither checks
what it opened before reading its keys.

The files here are a different kind of record and would be read as receipts if
they sat one level up. They live in a subdirectory for the same reason
`superseded/` does, and the parent's README states it: a subdirectory is
invisible to both globs.

- `2026-11-02-panel-sweep-255.json` and `.txt`. Reliability over every one of
  the 255 non-empty subsets of the eight decoys, library fixed, split by case
  kind. Written by `trigger_test.py --sweep`. The published cell, the full
  panel, is 0.9104; the curve spans 0.7612 to 0.9403. The maximum in that file
  is not a target and choosing the subset that scores best would be tuning the
  null model to the library.
- `2026-11-02-invariance-gate.txt`. The output of `trigger_test.py
  --invariance`, which is the pre-registered gate on an engine change as of
  2026-11-02. It takes no cases and makes no model call, so it has nothing in
  common with a receipt except the directory it would otherwise sit in.
