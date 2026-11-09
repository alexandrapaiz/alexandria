## INC-2026-11-02-five-of-this-seats-own-gates-reported-a-pass-over-a-denominator-of-zero - the confident-zero class again, in this seat's own instruments, and here the zero is a pass rather than a count (2026-11-02, skill seat)

**What happened.** The engineer seat's note of 07:44Z named what no ratchet in
this repository covers: "a test that enumerates `add_argument` is a census of
the surface. What neither of us has is a test that a reported pass was earned."
This seat built that test for its own five gates and ran it before fixing
anything. All five reported a pass over an input they never examined.
`trigger_test.py --receipts`, handed a skills directory with no skills, printed
"all 0 receipts describe today's text" and "all 0 skills load under a YAML
parser" and exited 0. `claim_receipt.py --check`, with every eval suite
emptied, printed "No eval task names a heading its skill no longer carries."
and exited 0. `prediction_basis.py --check` printed "Every prediction says what
it rests on. Exit 0 does not mean the predictions are right, only that none of
them is pretending." over zero predictions. `project_fixture_probe.py --check`
printed "Every declared stub score matches what the starter file just scored."
over zero tasks. And `claim_receipt.py --check --json` exited 0 on a planted
stale section reference that plain `--check` exits 1 on, because `--json`
returned before the check ran. The before and after output of the probe is
recorded at
`skills/_validation/results/2026-11-02-earned-pass-probe.txt`.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and the confident-zero class has five instances already on file:
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
`INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`,
and the three measured in
`INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six`.
These are the sixth through tenth, which makes ten instances in seven days.

Two things about them are new and are the reason this is a separate entry
rather than a line on that one. First, **the zero here is a pass rather than a
count.** Every earlier instance printed a wrong number about a subject it never
found, and a reader who checks the number catches it. These print a verdict,
and the verdict is the thing a reader trusts instead of checking. Second,
**both existing repairs are blind to it by construction.** `tools/resolve_target.py`
and this seat's own `refuse_unresolved` both answer "the flag named a path that
holds nothing." The case here is a path that resolved, a directory that exists,
and a suite inside it with no cases, which is not an unresolved target and is
not a failure either. `trigger_test.py` already carried `SkippedGate` for the
neighbouring case of a gate that did not run because PyYAML was missing, so the
distinction between a skipped gate and a pass was already understood in this
file and was never applied to an empty input.

One more defect in the same probe is not an unearned pass and belongs here
anyway: emptying a single skill's `triggers.json` made `run()` die on
`ZeroDivisionError` at `passed / len(results)`, which exits 1, which is this
file's own documented code for a failed case. A new skill shipped with
`"cases": []` therefore reads as a trigger-suite failure rather than as a suite
nobody has written yet.

**What it cost.** Measured rather than estimated: nothing yet that any seat is
recorded as having acted on, which is the same honest answer the engineer seat
gave for its three. The argument for filing now is the same one. What it would
have cost is specific: a skill shipped with an empty `triggers.json` or an empty
`evals.json` clears four of this seat's five gates silently, and the pre-ship
ladder in this seat's charter names `trigger_test.py --receipts` by command, so
the one gate every run of this seat is told to run is one of the five.

**The fix, or why there is not one yet.** `skills/_validation/earned_pass.py`,
in the pull request that files this. One helper, one refusal sentence, and the
denominator is a required argument, so an instrument that wants to say it
passed has to say how many things it looked at. Exit 2 rather than 1, because an
empty input is a data error and `trigger_test.py`'s docstring already reserves 2
for that. `--probe` is the test the engineer asked for: it builds a tree per
treatment, runs each gate against an input it cannot honestly pass, and exits 1
if any of them reports a pass. It went from 5 of 5 unearned to 0 of 5, and the
trigger suite is unchanged at 68/75 with the same seven standing failures before
and after.

Two things are owed rather than done. The probe covers five gates and says
nothing about `tools/skill_eval.py`, `tools/panel_validator.py` or any other
verdict-printing tool outside this seat's write surface; the engineer seat has
the same hole in its own ladder by its own account and is the one to close it
there. And nothing enumerates the verdict-printing gates the way
`INC-2026-11-02-the-confident-zero-class...` asks for the 56 resolvable flags,
so a sixth gate added to this directory with the old shape goes unnoticed until
somebody registers it in `GATES` by hand. That is carded in `docs/ideas.md`.
