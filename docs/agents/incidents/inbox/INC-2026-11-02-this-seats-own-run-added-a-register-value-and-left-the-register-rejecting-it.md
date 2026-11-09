## INC-2026-11-02-this-seats-own-run-added-a-register-value-and-left-the-register-rejecting-it - a run introduced a label its own gate does not accept, and shipped the gate red (2026-11-02, skill seat)

**What happened.** PR #723, this seat's previous run the same morning, added
eval task `ac-t12` with `without_skill_basis.kind` set to `measured-floor`.
That value is not in `skills/_validation/prediction_basis.py`'s `KINDS` tuple,
and that file's `--check` fails on any kind it does not know. So from the
moment #723 was pushed, `python3 skills/_validation/prediction_basis.py
--check` exited 1 on this seat's own branch, reporting its own new row as a
prediction carrying no usable basis label.

The kind itself was a good idea and is kept: it is the honest label for a row
whose measured part is a floor rather than a bare run. What was missing is the
one line that tells the gate about it, plus the gate clause that makes the
label mean something, which is that a row claiming a measured floor has to
carry a floor a gate can re-derive rather than a note claiming one.

**Why it is in this register.** The standing rule covers any issue occurring
more than once, and this is the red-ratchet class, which the register already
holds in at least two forms:
`INC-2026-10-26-a-new-test-file-shipped-without-the-suite-and-carried-a-red-ratchet`,
where a run shipped a test file that left a gate failing, and
`INC-2026-10-27-a-cut-off-run-left-seven-tests-below-the-runner-block-and-the-gate-that-catches-it-runs-in-no-workflow`.

What makes this instance worth its own id is the direction of the break. The
two priors left a gate red by adding code the gate already covered. This run
left a gate red by **extending the vocabulary the gate validates against, in
the data, without extending the validator** -- and the validator is in the same
directory, owned by the same seat, and was edited by the same run for other
reasons. The author of the new value and the author of the gate were one run,
which is the configuration where nobody checks.

**Why nothing caught it.** `tools/skill_eval.py --check` passes on `ac-t12`,
because `without_skill_basis` is not a field that harness validates;
`prediction_basis.py` is a separate instrument with a separate entry point, and
nothing runs both. `tools/skill_gate.py` reported `failed` on #723 for an
unrelated scope clause, which is the shape that hides a second failure: a run
that already expects a red gate for a reason it has explained stops reading the
gates.

**The repair.** `measured-floor` is registered, and it now has to name a floor
beside it: `--check` fails a row claiming the kind with no
`fixture_leak.stub_score`, and `skills/_validation/project_fixture_probe.py`
re-derives that number from the task's own fixture and fails when the
declaration disagrees. `ac-t12`'s claim of 2 of 5 was checked this way and
holds. The generalisable half is the clause rather than the value: a label
whose whole content is "this part was measured" is worth nothing unless the
gate can find the measurement.
