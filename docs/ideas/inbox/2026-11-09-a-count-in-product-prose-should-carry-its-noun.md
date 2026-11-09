### 2026-11-09 - a count in product prose should carry its noun, because an elided one is unreachable by any gate (engineer seat)

- Trigger: the census shipped this run found six stale skill counts and could
  not see two more that sit in the same paragraphs as the ones it found.
  `site/app/llms.txt/route.js` says "the repository carries a Cursor plugin
  manifest for the same nine" and `docs/product/install.md` says "what every one
  of the nine shares", both live, both wrong, both fixed by hand this run. The
  count gate matches `<number> skills` and `<number> skill files`. A count whose
  noun was elided by the previous sentence resolves only by reading the previous
  sentence, which is a parser rather than a pattern.
- What: this is a writing rule that buys a gate, which is the cheap direction.
  In product prose a count carries the noun it counts: "the same ten skills"
  rather than "the same ten". The sentence is barely longer, it reads better out
  of context, and it moves the claim from unreachable to checked by an
  instrument that already exists. The proposal is a line in
  `docs/voice/ban-list.md` or its neighbouring guidance, plus the matching
  pattern in the voice checker: in the declared product surfaces, a number word
  or digit followed within a few words by `shares`, `of those`, `of them`, `the
  same` or an end of sentence, with no noun between, is flagged for the writer to
  name the noun. It is a lint about reachability rather than about style, and the
  remedy is one word.
- Why the weak version: deciding that a bare number is a count is a judgment and
  a gate that guesses will be wrong often enough to be switched off, which is
  this repository's own recorded reason for reading only marked blocks. So scope
  it to the handful of files already declared in `COUNT_SURFACES` as `live`,
  where every number is about the library by construction, rather than to all
  prose.
- First step: measure the population before building. Count the bare numbers in
  the `live` surfaces and how many are counts of skills. If it is under a dozen
  the rule is worth a gate; if the false positives outnumber them, the rule
  stays guidance in the voice file and the gate is not built. That measurement is
  an hour.
- Cost: $0
- Status: proposed
