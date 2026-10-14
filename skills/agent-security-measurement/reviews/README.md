# agent-security-measurement: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

This skill is mostly about what not to report, which makes its reports unusual:
the decision it changes is often a number someone was about to publish. Say so
explicitly if that happened. A report that reads "we did not ship the refusal
rate" is a decision change, and it is the kind an eval cannot see.

Most wanted:

- **Section 1, completed harm.** Whether you could actually write the predicate
  over state that verifies completed harm in your own system. The section
  assumes you can, and that assumption is untested outside the papers.
- **Section 5, observability before a better monitor.** The ordering claim is
  the most actionable thing here and the most expensive to act on. A report
  should say whether the hook existed already or had to be built.
- **Section 7, the orchestrator.** It tells you that adding an agent raises the
  misbehaviour rate in every configuration tested. If that stopped a planned
  topology, that is the report.
