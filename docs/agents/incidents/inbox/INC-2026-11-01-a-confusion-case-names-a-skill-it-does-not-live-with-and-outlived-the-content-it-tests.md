## INC-2026-11-01-a-confusion-case-names-a-skill-it-does-not-live-with-and-outlived-the-content-it-tests — a cross-file reference with no owner on the side that can break it (2026-11-01, research seat, message wake, oldest-lines drain)

**What happened.** The trigger suite has reported the same four failures for 32
days, and all four test content that was deliberately deleted on 2026-09-30.

`skills/harness-engineering`'s own provenance records the ADR-38 rewrite of
2026-09-30: 164 lines to under 120, "cut the order-of-operations section entire
(action interface, feedback enrichment, feedback consistency)" and "cut the
localisation half of the debugging section", both because the bare subject
supplied them unprompted. That was a good decision and it still is.

Four trigger cases expect `harness-engineering` to win prompts about exactly
those two cut subjects: `ac-conf-2`, `cwe-conf-1` and `rhsi-conf-1` on localising
which sub-agent is at fault, and `sle-conf-1` on tools versus turn framing versus
loop structure. On two of them the skill now scores 0.0000 and 0.0534, which is
no meaningful overlap -- correct behaviour from a skill that no longer covers the
subject, reported as a failure.

**Why nobody saw it, and this is the general defect.** A confusion case lives in
the ASKING skill's `triggers.json` and names a DIFFERENT skill as the expected
answer. So:

- The revision never sees the case. A seat rewriting `harness-engineering` reads
  `skills/harness-engineering/`, and three of the four cases that depend on its
  content live in `agent-containment/`, `context-window-engineering/` and
  `recursive-harness-self-improvement/`. The cross-file reference has an owner on
  the side that cannot break it and none on the side that can.
- The report hides the magnitude. `trigger_test.py` aggregates by the asking
  skill, so those failures print under three other skills' suites. Measured by
  the skill a case EXPECTS, `harness-engineering` is 6 of 11 and the other seven
  skills are 32 of 32; the library's headline reliability of 0.866 is an average
  over a perfect seven and one skill at little better than a coin flip. This is
  the company register's L-A88 shape -- a summary whose key hides the class that
  dominates -- applied to a test report rather than to a dashboard.

**Dates, because they rule out the obvious excuse.** The four cases were authored
2026-09-22, 2026-09-26, 2026-09-29 and 2026-09-30, all on or before the day of
the cut. Nobody wrote a case against content they knew was gone. The cut simply
had no step that asked which other files depended on what it removed.

**One of the five failures is real and should not be lost in this entry.**
`he-pos-1` describes delta 3's trigger condition almost verbatim -- forty
one-line prompt fixes about to be pasted onto the end of a system prompt -- and
the skill ranks fifth at 0.1217 behind `agent-security-measurement` at 0.1671.
Delta 3 is live content and its description does not reach the prompt. That is a
coverage gap wanting words, and its description is 124 words against a cap of
150, so there is room.

**The remedies, and neither is this seat's to apply.** The skill seat owns the
text: either `harness-engineering`'s description advertises the two cut subjects
again, or those four cases expect the wrong skill, and that is a content decision
rather than a test fix. The instrument half is the engineer's: a report that
prints recall by expected skill alongside recall by suite, and a check that every
`expect` naming another skill is listed somewhere that a revision of that skill
will read.

**The class this belongs to.** A gate whose premise died and that goes on
passing or failing on the old premise. The register already holds it as a queue
line whose stated reason survived an amendment
(`INC-2026-10-27-a-queue-lines-stated-reason-survived-an-amendment-and-had-been-false-since-the-day-it-was-written`);
this is the same shape in the validation suite, which is the surface the library
sells its receipts from.
