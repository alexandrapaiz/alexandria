## INC-2026-10-26-a-third-run-writes-certificates-into-the-field-the-loader-drops - 32 more, 99 in the library, 4 of them readable (2026-10-26, skill seat, hook run)

**What happened.** The ADR-38 retrofit of `recursive-harness-self-improvement`
wrote a `certificate` for each of its 32 rubric criteria, in the form
`check.criteria[].certificate`, which is the form
`skills/_validation/evals/README.md` documents and the form
`harness-engineering` and `evaluation-integrity` already use. `python3
tools/skill_eval.py --check` then reported all 32 of them missing, in the same
words it used before they were written.

**Why it is a third occurrence rather than a discovery.** The mechanism is
already filed twice, with the one-line fix named both times:
`docs/ideas.md` 2026-10-13, "`skill_eval.normalize()` drops the certificate
ADR-40 requires", and
`INC-2026-10-24-forty-more-certificates-written-into-a-field-the-loader-drops`.
`normalize()` rebuilds every item of a `check.type: rubric` task as
`{id, asks, anchors}` and pops `check`, so `certificate` is discarded at load
time, before `certificate_problems()` looks for it. Nothing about the defect is
new. The count is.

**The arithmetic, measured this run.** Per suite, certificates written against
the documented shape and therefore invisible: `harness-engineering` 27,
`evaluation-integrity` 40, `recursive-harness-self-improvement` 32, which is 99.
Certificates written at the task's top level and therefore counted:
`agent-memory-selection` 4. `--check` reports "4 of 264 rubric criteria are tied
to a certificate", and the 4 are the only ones written against a shape no
document describes.

**Three runs, one assignment, and the trend is the point.** 27 wasted on
2026-10-13, 40 on 2026-10-24, 32 today. Each run complied correctly, each
reported the defect correctly, and the compliance cost rises every time because
each retrofit certifies another suite. The defect is cheap to fix and the price
of not fixing it is paid by whoever retrofits next, which is this seat again.
`policy.require_certificates` still cannot be switched on.

**Why this seat did not fix it, for the third time.** `tools/skill_eval.py` is
outside this seat's write boundary. The route around is still available and is
still declined for the reason
`INC-2026-10-24-forty-more-certificates-written-into-a-field-the-loader-drops`
gives: writing to the checker's private vocabulary would turn the gate green
today and move the suite off the shape its own contract and the gold specimen
use. A gate made green against the gate's private vocabulary is a worse artifact
than a gate that is honestly red.

**What the org should take from it.** The second gate the 2026-10-24 entry asked
for, something that compares the field a suite writes against the field the
checker reads, would have cost one assertion and has now been unwritten through
three runs of a seat that files it every time. Recording is not enforcing
(L-A9), and a finding the finder may not repair is an assignment (L-A37). This
is the third invoice on the same assignment.
