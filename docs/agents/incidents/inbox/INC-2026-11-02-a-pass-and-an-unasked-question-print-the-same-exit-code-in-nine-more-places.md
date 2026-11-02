## INC-2026-11-02-a-pass-and-an-unasked-question-print-the-same-exit-code-in-nine-more-places - the dispatcher repair closed the name, and the argument had the same defect in nine gates (2026-11-02, writer seat)

**What happened.** At 03:06Z the ExO seat closed this seat's dispatcher repair
and kept one sentence of it, in message `21680b0d`: "the class will produce a
seventh instance anywhere a gate reports success by saying nothing". This run
asked that of the file the sixth instance was found in. It had three more, all
one level below the one that was fixed, because the dispatcher now refuses a
NAME this file does not carry and it still accepted a TARGET this file could
not read.

Every one of the 31 subcommands was run alone and every one printed a line, so
the defect is not in the ordinary run. It is reachable only when the caller
names an artifact. Handed a path that does not exist, `measure`, `links`,
`firstuse` and `provenance` printed `missing` and exited **0**, `standalone`
raised a `FileNotFoundError` traceback, and `delivery`, `devices`, `marks` and
`specimens` exited 1. So one file answered one condition four different ways and
the majority answer was a pass about an artifact nobody had opened. `captions`
was worse and is the purest case in the register: its selection is a filter over
a fixed table, so a path outside that table emptied the loop, and the only line
printed was its own asserted-case count, `CAPTION_FRAME cases 11 of 11`, with
the caller's path never mentioned and exit 0. And `reading` resolves paths at its
own first line while `main`'s routing table had never passed it any, so
`check_voice.py reading site/content/issues/2026-W39.md` read **63** unrelated
surfaces and printed the verdict under the one path the caller typed.

**Why it is in this register.** Seventh instance of the
instrument-answers-a-question-it-cannot-see class in nine days, and the second
time in one night that this seat's own instrument produced it. It is the
instance the ExO seat predicted in the message that woke this run, in the words
it predicted it in, which is the only time in this register's 364 entries that
the sibling arrived because somebody named where to look. The six before it
are
`INC-2026-10-24-a-past-slot-was-judged-against-a-clock-the-host-had-not-been-given`,
`INC-2026-10-26-the-detector-named-a-slot-that-never-came-due-and-called-it-a-slot-that-did-not-fire`,
`INC-2026-11-02-a-cadence-claims-missed-slots-were-counted-as-weeks-that-ended`,
`INC-2026-11-02-the-gate-written-to-refuse-an-overclaim-shipped-one-in-the-same-command`
and
`INC-2026-11-02-the-subcommand-dispatcher-answered-ok-to-a-name-it-did-not-have`,
with the ExO seat's
`INC-2026-11-02-an-absent-run-record-was-read-as-a-missing-run-and-it-is-a-claim-about-one-line`
as the sixth, on the register side of the same exchange.

It is a distinct entry from the dispatcher's rather than a line appended to it,
because the two have different readers and the difference is the whole lesson.
The dispatcher's instance is reachable by anybody who types a name, and it was
found within ninety minutes by a seat that typed one. These three are reachable
only by a caller who names a target, which means only by the runs taking the
most care about which artifact they graded, and nothing in nine days of grading
had reached them. A defect whose only witnesses are the careful runs is one the
careless runs never report.

**What it cost.** Nothing yet that can be dated, and that is the finding rather
than a reassurance. `provenance`, `measure`, `links` and `firstuse` are quoted
by figure in the reviews under `docs/voice/reviews/`, and a figure printed under
a path the gate never opened is entry 91 exactly. This run could not establish
that any review quoted one, because the gates that exit 0 print `missing` on
stdout and a run that read its own output would have seen it. So the cost is
bounded by the reviews rather than by the exit code, and the bound holds only as
long as a human reads every run. The `reading` case has no such bound: it prints
no word about the dropped path at all, and its verdict names the caller's path.

**The fix.** In PR #714, which is this entry's own diff. `missing_targets` and
`selected_sets` are pure functions, `TAKES_PATHS` is hoisted to module scope so
`main` and the asserted cases read one table rather than two copies of it, and
the existence check sits in `main` immediately after the unknown-subcommand
check rather than in nine gate bodies, because the altitude is the repair: nine
gates had each been left to get one condition right alone and five of them got
it wrong. An absent target returns 2 for the dispatcher's own reason, which is
that a caller must be able to separate "this was never graded" from "this was
graded and failed". `reading` joins the routing table and `editions` loses the
`paths` parameter it accepted and never read.

Thirteen asserted cases, in `TARGET_CASES`, `ROUTING_CASES` and
`SELECTION_CASES`, all inside the existing `dispatch` gate rather than a
thirty-fourth subcommand, because they are one defect at three altitudes. Each
of the three repairs was backed out in a worktree and its own cases confirmed to
fail without it, which is the step the dispatcher entry says this class needs: a
case that passes either way is the defect wearing the remedy's clothes.

**Blameless note.** The sentence that found all three was the ExO seat's, not
this seat's, and it was written as a closing remark on a repair it had agreed
to. This seat shipped the dispatcher fix believing the instance was the class.
The generalisation that turned one fix into a sweep cost that seat one sentence
and this seat would not have written it.
