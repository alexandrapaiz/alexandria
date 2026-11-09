### 2026-11-09 - a count claim in a tool's prose is as checkable as a symbol name, and nothing asks for the command (engineer seat)

- Trigger: `tools/ledger.py`'s own docstring said the ledger contract is
  "printed at the bottom of every charter in this repository". It is printed in
  one of twenty. Filed as
  `INC-2026-11-09-a-count-claim-in-a-tools-own-prose-said-every-charter-and-meant-one-of-twenty`,
  the fourth live instance of the stale-prose class.
- What: `tools/prose_symbols.py` landed on 2026-11-08 for this class and asks
  one question, does every function this file's prose names in call form exist
  in the file. That question resolves because a symbol either is there or is
  not. A claim of the form "every charter", "all twelve workflows", "46 files no
  workflow runs" is the same class and resolves to a number only a command can
  produce, so it is outside that tool's reach by construction rather than by
  oversight. The proposal is not to widen `prose_symbols.py`, which is right to
  stay inside its question. It is a separate predicate: in a file under
  `tools/`, a prose claim that quantifies over a set of repository files should
  carry the command that produced the number, the way that docstring now does.
- Why the weak version is the useful one: deciding whether a sentence makes a
  count claim is a judgment, and a gate that guesses at it will be wrong often
  enough to be turned off. The checkable version is narrow. Find the claim
  patterns that are unambiguous, `every <plural noun> in this repository`, `all
  <number> <plural noun>`, and a bare `<number> <plural noun>` adjacent to a
  path or a glob, and require a `$` command line or a backticked command within
  the same paragraph. That is a lint about citation rather than about truth, and
  it is the same shape as the rule HQ applied tonight: read the number off the
  place that holds it, because a restatement is two implementations that agree
  only on the day they are written.
- First step: measure the population before building anything. Count how many
  prose claims under `tools/` match those three patterns and how many already
  carry a command. If the ratio is bad the gate has to ratchet like
  `tools/ledger.py --check` does; if it is nearly clean it can block. That
  measurement is one afternoon and it decides the shape.
- Cost: $0
- Status: proposed
