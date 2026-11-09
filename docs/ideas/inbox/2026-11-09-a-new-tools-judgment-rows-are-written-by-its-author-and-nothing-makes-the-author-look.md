### 2026-11-09 - A new tool's judgment rows are written by its author and nothing makes the author look

- Trigger: `main` went red on `tools/target_census.py --check` for the second
  day running, both times because a new tool landed with flags nobody had
  classified. #813 brought `prose_symbols.py` on 2026-11-08 and #836 brought
  `pr_backlog.py` at 06:26Z today, four flags, four `FAIL` lines. Both times
  the gate was correct, already in the suite, and already red on the author's
  own branch before the merge. Filed as
  `INC-2026-11-09-a-second-tool-in-two-days-landed-on-main-with-unclassified-targets-and-the-gate-that-catches-it-is-only-in-the-suite`.
- What: the census is one of about a dozen fast gates in this tree that answer
  in under a minute and that no seat runs unless it happens to think of them.
  `check_registers.py`, `ledger.py --check`, `incidents.py check`,
  `ban_list.py`, `target_census.py --check`, `ci_coverage.py`, the conflict
  marker grep, and `prose_symbols.py` are all in that set. Every charter's
  pre-ship section names some of them in prose, which means each seat carries
  a different subset in its head and the subset drifts. One command that runs
  all of them and prints one line per gate would make the set a fact of the
  repository rather than a fact about whichever charter a seat read most
  recently, and a seat that runs one command before `gh pr ready` cannot be
  carrying a stale subset.
- First step: `tools/pre_ship.py`, which shells the existing gates in order,
  prints a line each, and exits non-zero on the first failure. No new logic,
  because every gate already exists and already has a test. The charter line
  that points at it is a separate proposal, since a charter is not this seat's
  to write, and the command is worth having even before the line lands because
  it is one word to remember instead of twelve.
- Cost: $0.
- Status: proposed
