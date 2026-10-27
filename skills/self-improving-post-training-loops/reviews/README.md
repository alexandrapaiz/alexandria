# self-improving-post-training-loops: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

Most wanted. This skill asks for the most expensive experiments in the library,
so a single report from anyone who actually ran a training loop with it open is
worth more here than anywhere else. The three below are ordered by what a report
would move, after the 2026-10-26 retrofit renamed every section:

- **Delta 2, the teacher gate.** The best-evidenced delta in the file and the
  one whose cost claim is cheapest to check, because the compute win is a jump
  in teacher utilisation rather than an accuracy story. The retrofit also
  narrowed this delta's accuracy claim: the gate took the best score on nine of
  fourteen benchmark-scale pairs, not on every setting. A report should say
  whether the gate paid for itself on the utilisation number alone, and whether
  three probes at a two-of-three threshold was the right setting for your
  verifier.
- **Delta 3's first gate, decontamination.** The retrofit added it, because the
  paper leads with it and the previous version of this file omitted it. It is
  the prescription most likely to be skipped as routine and the one whose
  absence is hardest to see afterwards, since a leaked eval item shows up as a
  good number. If your loop ran a second iteration at all, that is the other
  thing to report: the published result is a single pass, so iteration two is
  outside the evidence in either direction.
- **The ordering line in the checklist.** This skill tells a reader to exhaust
  harness work first. If it talked you out of a training run, say so. That is
  the most valuable thing it can do and the least visible to an eval.

One note on what a report cannot settle. No delta here has a differential
number, so a report that says a section changed a decision is currently the
only evidence this skill has of helping anyone.
