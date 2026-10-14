# agent-containment: consumer reports

The lane is open and empty. File as `YYYY-MM-DD-<consumer>.md` against the
contract in
[skills/_validation/reviews/README.md](../../_validation/reviews/README.md).

Revised 2026-10-06 with the ADR-38 retrofit, because the three sections this
file asked for no longer all exist. The skill now carries 15 claim ids over 6
papers rather than an empty provenance block, and `status: provisional` with no
bare-arm screen run, so a report remains the only evidence about this skill that
is not a reading.

Most wanted, in priority order.

- **Delta 2, the within-tool axis.** The newest finding here and the one with
  the most practical consequence: a tool-filtering defence left within-tool
  hijacking at 2.381 to 14.458 percent while cutting cross-tool success to near
  zero, so the common fix constrains the wrong axis. If you have shipped tool
  filtering or an injection classifier and been hit anyway, that is the report.
  If you moved to provenance-constrained parameter bindings, say what it cost in
  false refusals, because the paper's own stated failure mode is conservative
  refusal when a legitimate value only arrives through an untrusted channel.
- **Delta 1, the enforcement point, specifically the effect-verification half.**
  The null result on deny lists is the file's central claim and the one most
  likely to be argued with. A report from a team that replaced a deny list with
  a blocking pre-dispatch interceptor should say what the migration cost and
  whether declaring effect atoms on every tool schema was the real work, since
  the ablation attributes most of the security gain to that part.
- **Delta 3, default-deny as a property of the language.** Flagged in the file
  itself as the delta most likely to already be in a bare model's answer. A
  report that says this section told you nothing you did not know is directly
  useful: under ADR-38 that is grounds to cut it, and several reports saying so
  make it a deprecation candidate.

Two things this skill no longer answers, so a report on them is not wanted here.
The isolation-tier decision and the undo primitive were both cut on 2026-10-06
and are queued in `docs/research/reading-queue.md`, the second as a skill of its
own.
