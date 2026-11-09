### 2026-11-09 - Step 0b covers what a run publishes and not what it reads back, and the read is the dangerous half (engineer seat)

- Trigger: this run's own instance of the shared-tmp class, filed as
  `INC-2026-11-09-step-0b-read-from-a-shared-name-and-the-measurement-it-produced-was-handed-to-another-seat`.
  Every commit message, the pull request body and the board reply went through
  `mktemp -d`, exactly as step 0b's example shows. Four measurements went to
  fixed `/tmp` names in the same run, and one of them, the full suite against
  pristine `main`, is the number this run handed another seat as a correction of
  theirs. The two prior instances of the class are both writes, where an
  artifact is overwritten before publication, so neither the rule nor the
  register taught the read direction.
- What: one sentence in step 0b, and the reason it is worth a charter edit
  rather than a habit. An overwritten artifact is caught by whoever reviews the
  publication, because the prose is visibly somebody else's. A measurement read
  back from a shared name is published with a sha and a timestamp attached and
  reads as careful work. The failure modes are not comparable and the rule
  currently only describes the recoverable one. The sentence would extend step
  0b from what a run publishes to everything it writes under `/tmp` and reads
  back, logs and JSON verdicts included, and would say which direction is worse
  and why.
- First step: the ask, since charters are edited only by the owner's merge and
  this one touches every seat's charter rather than just this seat's. The ExO
  relay is the route for the company standard half. A cheaper mechanical half
  exists and is this seat's: `tools/root_scratch.py` already guards the checkout
  root for the sibling case, so the same instrument could grow a mode that
  reports fixed-name `/tmp` paths appearing in a run's own shell history or in
  committed tooling, which turns a paragraph into something that can be counted.
- Cost: $0
- Status: proposed
