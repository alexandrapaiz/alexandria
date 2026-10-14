# self-improving-post-training-loops: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

Most wanted. This skill asks for the most expensive experiments in the library,
so a single report from anyone who actually ran a training loop with it open is
worth more here than anywhere else:

- **The teacher gate.** The best-evidenced section in the file, and the one
  whose cost claim is easiest to check: the compute win was a jump in teacher
  utilisation, not an accuracy story. A report should say whether the gate paid
  for itself on the utilisation number alone.
- **Dynamic rubrics without a verifier.** Prescribed for the case where you
  have no ground truth, which is the case hardest to report honestly, because
  there is nothing to check the rubric against.
- **The ordering caveat.** This skill tells a reader to exhaust harness work
  first. If it talked you out of a training run, say so. That is the most
  valuable thing it can do and the least visible to an eval.
