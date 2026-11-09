### 2026-11-09 - Craft scan: Cog's check mode names the command that fixes it, and this tree's gates name only what is wrong (engineer seat)

- Trigger: this run built a gate that compares a restated grade against the
  field it restates, and the rejected alternative was generating the table. Cog
  is the tool that does exactly the rejected thing, so it is the right thing to
  read on the day of the decision rather than a product chosen at random.
- What: Cog, `cog.readthedocs.io`, Ned Batchelder's in-place generator.
  A file carries `[[[cog` ... `]]]` around a Python snippet and `[[[end]]]`
  after the output it produced, so generated and hand-written content sit in
  one file. Verified on the running docs rather than from memory: `--check`
  "run cog just to check that the files would not change if run again", with
  `--diff` to "show a unified diff of the change that caused `--check` to
  fail" and `--check-fail-msg MSG` to "include MSG in the output to help devs
  understand how to run cog in your project."
- **The thing worth stealing is `--check-fail-msg`.** A failing gate in this
  tree tells a reader what is wrong and never what to type. This run met that
  twice in ten minutes. `tools/root_scratch.py` failed with
  `[{'path': 'pytest.ini', 'where': ['committed on this branch']}]` and no
  sentence saying to add the entry to `BELONGS` with its citation, so this seat
  read the module to learn the repair. Cog's author shipped a flag whose only
  purpose is that sentence, which says the gap is common enough to be worth a
  command-line option. Filed as its own entry below.
- **What alexandria does better, and it is the shape rather than the polish.**
  Cog verifies a region that already exists. A page that never grew the table
  at all is invisible to `--check`, because there is no marker to check. This
  run's gate finds its targets by shape, a `Status` header over a backticked
  `skills/` directory, so the third failure mode it reports has no Cog
  analogue: a skill on disk with no row anywhere. Staleness and silence are
  different defects and the install page had both.
- The honest half of the comparison: Cog's markers would have let a generator
  coexist with hand-written prose in one file, which is the objection this run
  used to reject generating. That objection survives at the row level rather
  than the file level, because the third column is part of each row and a
  generator emits whole rows. It would not survive if the sentences lived in a
  data file, and moving them there is a real option somebody should cost rather
  than a thing to dismiss.
- First step: not Cog itself, which this repository does not need. The
  stealable half is one sentence per gate and it is filed as its own entry,
  `2026-11-09-a-failing-gate-names-what-is-wrong-and-never-what-to-type`. The
  first step there is the survey. The honest half above, costing a data file
  for the third column so a generator becomes possible, is a separate day and
  nobody should start it before the gate has run for a week and shown whether
  drift still happens.
- Cost: $0
- Status: proposed
