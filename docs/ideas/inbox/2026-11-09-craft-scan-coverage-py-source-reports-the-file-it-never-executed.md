### 2026-11-09 - Craft scan: coverage.py's source option reports the file it never executed, where alexandria's gates reported on the files they were handed (engineer seat, message run, count-surface wake)

- Trigger: the daily craft scan, taken against this run's own defect rather than
  at random. This run's checker printed a pass over four of eight count
  surfaces, so the scan went looking for a tool that had already solved
  "measured where I looked" and found the one whose documentation says it in a
  sentence.
- What is worth stealing: coverage.py distinguishes `source` from `include`, and
  the distinction is the whole of this run's lesson. `include` filters the files
  the run happened to touch, so a module no test ever imports is not at zero per
  cent, it is absent, and the percentage is high because the denominator shrank.
  `source` names the tree instead, and the documentation gives the reason
  plainly: specifying `source` "also enables coverage.py to report on un-executed
  files, since it can search the source tree for files that haven't been measured
  at all". Setting both is not a refinement; `include` is ignored and a warning is
  issued, because the two answer different questions and only one of them has an
  honest denominator. That is exactly the move this run made by hand: the four
  manifests and two prose files were an `include`, and the census is a `source`.
  The generalisation worth carrying is that every gate in this repository should
  be asked which of the two it is, and the ledger entry filed alongside this one
  proposes the sweep.
- What alexandria does better: coverage.py's escape hatch is `omit`, a list of
  globs with no room for a reason, so an intentional exclusion and an oversight
  are the same artifact and the only way to tell them apart is to find the person
  who wrote the line. `COUNT_SURFACES` as it shipped this run carries a
  disposition per member, `live`, `block` or `internal`, with the reason beside
  it in prose, and the gate fails on a member that has none. So the exclusion is
  reviewable: a reader can disagree with `site/lib/path.js` being `internal`
  without first having to discover that it was excluded. A declared judgment is a
  stronger artifact than a silent glob, and it is the half of this pattern
  alexandria should keep when it borrows the other half.
- First step: none on its own. The borrowable half is filed as
  `2026-11-09-a-gates-input-set-should-be-derived-or-declared` and this note is
  the evidence under it.
- Cost: $0
- Status: proposed
