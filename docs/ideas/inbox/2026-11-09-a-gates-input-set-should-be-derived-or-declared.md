### 2026-11-09 - a gate whose input set is a hand list reads as a clean pass, so sweep tools for the pattern (engineer seat)

- Trigger: `tools/check_plugin_manifest.py` named two manifests in module
  constants and two prose files in a two-tuple, and reported "The install line
  and the manifests agree" over half the surfaces that exist. Filed as
  `INC-2026-11-09-the-checkers-four-count-surfaces-were-its-own-reach-and-eight-ship`.
  `INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`
  is the same defect in `tools/` at a different scale, and
  `tools/target_census.py` exists because of it. Three instances of one shape
  means the shape is worth finding mechanically rather than one gate at a time.
- What: a sweep over `tools/` for the pattern, not a new gate over the product.
  The signature is mechanical and `ast` reaches it: a module-level tuple, list or
  dict literal of string path fragments, read inside a function that also opens
  files or appends to a `problems` list. Each hit is a candidate hand list, and
  for each one the question is the one `target_census.py` answered: is there a
  convention that derives this set, and if there is not, is each member's
  disposition written down with its reason. Those are the only two acceptable
  states. A bare list is the third state, and it is the one that reads as a
  clean pass.
- What this is not: a rule that hand lists are banned. `COUNT_SURFACES` shipped
  this run is a hand list, deliberately, because whether a file's counts are
  claims or records is a judgment no parser carries. The difference is that it
  carries a disposition and a reason per member and the gate fails on an
  unclassified member, so the list cannot silently shrink relative to the tree.
  That is the distinction the sweep should sort hits into.
- First step: the measurement, which decides whether anything gets built. Run
  the `ast` signature over `tools/` and count the hits, then classify them by
  hand into derived, declared and bare. If the bare count is small, fix them
  directly and write no tool. If it is large, the sweep becomes a `--check` the
  way `target_census.py` did. One afternoon.
- Cost: $0
- Status: proposed
