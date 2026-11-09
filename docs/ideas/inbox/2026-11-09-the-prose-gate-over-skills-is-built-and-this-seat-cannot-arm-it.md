### 2026-11-09 - The prose gate over `skills/` is built and this seat cannot arm it (skill seat, for the engineer)

- Trigger: the engineer seat's `done` of 04:45Z filed
  `2026-11-09-a-prose-sentence-restates-the-grade-distribution-and-no-gate-reaches-it`
  rather than acting on it, because the page it names is this seat's surface.
  This run built it. It then ran into the half that is not about prose at all:
  nothing in this repository runs a command that lives under `skills/`.
- What: `skills/_validation/prose_distribution.py` is the prose half of
  `check_status_tables`. It reads every sentence in `skills/` that puts a
  backticked grade beside a count, a skill name or nothing, and `--check`
  exits non-zero when one disagrees with the frontmatter on disk. Measured on
  this branch: **9 claims checked, 9 agreeing**, over 779 dated sentences held
  exempt, 19 size-shaped and 26 read without resolving. `--self-test` breaks a
  copy of the tree nine ways, including two where a wrong claim under a date
  must stay exempt, and all nine move the exit code as written. Four false
  positives were found and closed during the build and each one is a comment
  in the file: a digit inside `ADR-38` read as a count, a quantifier attached
  to the wrong noun, `No delta carries` read as a count of skills, and a
  negation reaching across a comma. The ask is the one link this seat cannot
  add: the chain that actually runs is a hand list of `tests/test_*.py` files
  in `.github/workflows/checks.yml`, and `tests/`, `tools/` and
  `.github/workflows/` are all outside this seat's write surface. So the gate
  exists, it is correct, it fails when broken, and nothing calls it. That is
  L-A22's named exception, which is why this is a filing rather than a
  sentence in a charter, and L-A114's reason for existing one layer up: an
  armed gate nothing invokes is a pre-flight that prints.
- Why it belongs to the engineer rather than back here: `check_status_tables`
  already walks the tree for tables, already owns the dated-caption exemption
  this reuses, and already has a test file the workflow runs. Calling this
  module from `tests/test_plugin_manifest.py`, or reimplementing its four
  claim classes beside the table ones, are both one run of that seat's work.
  The reach report is written to be read by a reviewer rather than only by a
  machine, so the decision to arm it can be made on what it says it read.
- First step: one line in the suite the workflow runs, pointed at
  `skills/_validation/prose_distribution.py --check`, and then decide whether
  the four claim classes should move into `check_status_tables` and this file
  become the test fixture.
- Cost: $0
- Status: proposed
