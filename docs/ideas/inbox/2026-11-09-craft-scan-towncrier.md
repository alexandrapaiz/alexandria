### 2026-11-09 - Craft scan: towncrier puts a fragment's kind in its filename, where alexandria's ledger infers the same distinction from prose (engineer seat, message run)

- Trigger: this run built a per-entry inbox for `docs/ideas.md` and then went
  looking for the product that has shipped this pattern longest, to find out
  what it learned that one evening of building cannot. towncrier
  (towncrier.readthedocs.io, read 2026-11-09) is the Python ecosystem's answer
  to the same defect: a changelog is a register every contributor appends to at
  one anchor, and it has been solving it with a `newsfragments/` directory for
  years.
- What converged independently, which is worth saying because it is evidence
  the shape is right rather than a thing to steal. `towncrier check` "verifies
  that a feature branch includes at least one news fragment" and "compares the
  current branch against `origin/main`". That is `tools/ledger.py --check --base
  origin/main` and `tools/incidents.py check --base origin/main`, arrived at
  here from an incident rather than from their docs. `towncrier build` deletes
  the fragments with `git rm` and appends to the news file, which is `--fold
  --apply`. `--draft` renders without writing, which is the dry run.
- What is worth stealing: **the kind of entry is in the filename**, not in the
  body. A fragment is `{issue_id}.{type}` over five types, feature, bugfix,
  doc, removal and misc, so the build groups by type without reading a word of
  prose. The ledger has exactly one kind distinction and it matters: a proposal
  owes a status and a craft or competitive scan note arguably does not, which is
  an open question the owner has not ruled on. `tools/ledger.py` decides it
  today with `SCAN_NAME`, a regex matching `^(craft|competitive) scan\b`
  against the entry's **name**, and its own docstring admits the consequence:
  30 of the 51 statusless entries are scan notes, every one written before the
  convention settled. A heuristic over prose is the thing towncrier's filename
  removes. `YYYY-MM-DD-slug.scan.md` beside `YYYY-MM-DD-slug.md` would make the
  kind a fact about the file for every entry arriving from now on, and leave
  `SCAN_NAME` to cover only the ones already in the register.
- What alexandria does better, and it is the half towncrier gets wrong:
  **the exemption.** `towncrier check` "automatically skips checking if the main
  news file itself was modified", reading that as a release branch. So a
  contributor who edits the changelog by hand instead of filing a fragment
  passes the check that exists to stop exactly that. Both inboxes here key the
  exemption on the inbox file the diff **deletes** rather than on the register
  being touched, so a fold is a fold wherever it happens and an append that
  only resembles one is not. That is the stricter predicate and it was already
  written down in `tools/incidents.py` before this scan found the looser one.
- First step, if accepted: the filename suffix. One clause in
  `INBOX_FILENAME`, one branch in `check_inbox` exempting a `.scan.md` entry
  from the status requirement, and the open question goes to the owner as what
  it is, a ruling about two kinds of row rather than a backlog of 51 lapses.
- Cost: $0
- Status: proposed
