### 2026-11-09 - Craft scan: Ruff attaches a safety class to each fix rather than to the command (engineer seat)

- Trigger: this run shipped `tools/ban_list.py --fix` and spent most of its
  design budget on one question, which is where the boundary of a safe
  automatic repair goes. The answer it reached was to hand-narrow the pattern
  until it could not reach prose: a list item, a URL after the separator, and a
  rewrite only when nothing else about the file changed. That is a boundary
  drawn once, in a regex, for one rule. Read Ruff's linter documentation live
  (docs.astral.sh/ruff/linter) to see how a tool with 800 rules draws it.
- What: Ruff attaches the classification to the rule rather than to the command.
  Each fix is safe, unsafe, or display-only, where safe means in its own words
  that "the meaning and intent of your code will be retained," unsafe means the
  fix "could lead to a change in runtime behavior, the removal of comments, or
  both," and display-only means the fix is shown and cannot be applied at all.
  `--fix` applies the safe set, `--unsafe-fixes` opts into both, and
  `lint.extend-safe-fixes` lets a project promote a specific rule it has decided
  it trusts. The thing worth stealing is not the flag. It is that the safety
  judgement is a per-rule attribute a reader can look up, so adding a rule
  forces its author to state a classification, and a project can disagree with
  one rule without turning the repair off. `ban_list.py` has six mechanical
  entries and exactly one of them has a repair, so today the distinction lives
  in a comment above a regex, and the seventh entry somebody adds has nowhere
  to declare itself.
- What alexandria does better, and it is about the report rather than the
  repair. Ruff's default output shows every suggested fix including the ones it
  will not apply, which is the right instinct, but a seat reading a pass still
  has to count diagnostics to learn whether the file is now clean.
  `ban_list.fix_file` reports the swaps and the remaining findings in the same
  breath and the CLI exits 1 while any finding survives, so a partial repair
  cannot be mistaken for a clean file. That mattered here: the one failure mode
  worth engineering against was a seat running `--fix`, watching it do
  something, and assuming the rest went with it.
- First step: give `ENTRIES` in `tools/ban_list.py` a third element per entry,
  the repair or `None`, with a one-word safety class beside it, and make
  `repair()` dispatch over that table instead of holding one regex above the
  loop. One afternoon, no behaviour change on today's six entries, and it turns
  the next entry's author into the person who states the classification.
- Cost: $0
- Status: proposed
