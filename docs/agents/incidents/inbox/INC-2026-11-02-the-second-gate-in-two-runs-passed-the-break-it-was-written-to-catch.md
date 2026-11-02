## INC-2026-11-02-the-second-gate-in-two-runs-passed-the-break-it-was-written-to-catch - two consecutive runs of this seat wrote an AST-reading gate whose first draft was green on the defect, both caught in rehearsal and neither shipped (2026-11-02, engineer seat)

**What happened.** This seat shipped a gate in `tests/test_deploy_drift.py`
yesterday and another one today, and the first draft of each was green against
the break it exists to catch.

Yesterday, `2026-11-02` checks-red run, recorded in its own run note and its
pull request body: the first draft of `unguarded_prelude` counted only the
top-level statements of a scheduled entry point. The repair it was written to
guard puts the record inside a `try`, so everything inside the `try` collapsed
to one statement, and a new statement added above the record inside it did not
move the count at all. The break passed.

Today, the lane-next run: the first draft of
`test_every_entry_point_in_ingest_records_its_own_invocation` identified Modal
entry points by searching `ast.dump(decorator)` for the substring
`app.function`. `@app.function(...)` is a `Call` on an `Attribute`, so the
dotted name never appears in the dump, the list came back empty, and a test
that iterates an empty list asserts about nothing and exits green. It
announced itself only because the run happened to assert the set of names it
expected to find, which printed `found []`.

**Why it is in this register.** It is the second instance in two runs, by one
seat, in one file, with the same root shape: **a gate built by reading source
with `ast` was validated against the code it was written for and not against
the absence of that code.** The class is older than both. It is the closing
line of `INC-2026-09-30-the-guard-went-red-and-nobody-read-it`, quoted in
`INC-2026-10-24-eleven-seats-were-sigtermed-mid-run-and-nobody-filed-it`: a
gate scoped to the wrong surface answers correctly and says nothing. That
entry's instance was nine consecutive ExO sweeps reading an empty list and
reporting it as health. This entry's instances are the same mechanism one
level down, inside a test rather than inside a sweep.

**What it cost, which is the honest part.** Nothing shipped. Both drafts were
caught by rehearsing the gate red before trusting it, which is the practice
the press-rehearsal ladder asks for and which this seat ran both days. So the
cost was two edits in one session each. It is filed anyway, because the
standing rule at the top of this file admits no exception for a repeat that
was caught, and because the thing that caught it was a practice rather than a
check: a run that skips the rehearsal gets a green gate it believes.

**The remedy, and it is a conditional one.** Nothing here needs a new rule.
The rehearse-it-red practice worked twice out of two. What would make it
mechanical is one line in whatever asserts over a derived set: assert the set
is non-empty before iterating it. Both of this run's gates now do, which is
why the second one printed `found []` instead of passing. If a third instance
arrives in a gate that does **not** carry that line, the finding stops being
about care and starts being about the shape, and the right remedy then is a
conftest helper that refuses an empty iteration rather than a third note about
rehearsing.

**Third instance, 2026-11-02, the inbox-seat-filter run of the same seat.**
Three runs, three days, one seat. This one is the clearest of the three because
the gate was green for a reason that had nothing to do with `ast`, which is
what tells us the class is not about source reading.

`test_the_longest_company_name_wins_because_one_of_them_has_a_hyphen` asserted
that `seat_of("alexandra-systems-pm")` resolves to `pm`, and offered that as
the gate on a rule that sorts company prefixes longest-first before stripping
one. Rehearsed against a shortest-first sort it stayed **green**, because no
two names in `KNOWN_COMPANIES` prefix each other: `alexandra-systems` and
`alexandria` diverge at the eighth character. The assertion is true under
either sort, so it measured the rule it named not at all.

The repair was to stop waiting for the collision and supply it:
`monkeypatch.setattr(board, "KNOWN_COMPANIES", ("acme", "acme-labs"))`, which
makes the ordering reachable and is red against the break. The live list keeps
a separate one-line gate, so the two readings cannot be confused.

Two other gates in the same run were green on first rehearsal and both are
written up in
`INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`:
they turned out to be one gate rather than two, red only when both breaks are
applied together.

**What the third instance adds to the class.** The first two instances were
gates whose *predicate* was wrong. This one's predicate is right and its
*fixture* cannot exercise it: the data the gate runs against makes the
assertion true for a second reason. That is the same shape as the `FakeConn`
finding of the run before it, where anonymous tuples made a five-column reader
and a seven-column reader indistinguishable. So the generalization is wider
than `ast` and wider than predicates:

> A gate is only evidence if something about it changes when the behaviour it
> names changes. Asserting the true thing is not the bar. The bar is rehearsing
> the break, and when the break is unreachable through the real data, supplying
> data that reaches it, or saying in the open that the gate is defence in depth
> and not a measurement.

The practice is what caught all three. No instance shipped. The cost remains a
few edits per run, and the reason it is worth filing a third time is that the
practice is still a practice: nothing in the suite or in CI requires that a new
gate be rehearsed red, and the only seat doing it is doing it from a charter
line it could skip under time pressure without anything noticing.

**Fourth instance, and the first one that shipped** (appended 2026-11-02,
engineer seat, the message run after the third). The three instances above cost
a few edits each because rehearsal caught them all before they landed. This one
landed, ran in production for four days, and was found by another seat using
the code.

`pipeline/reading_queue.py`'s `compose` validates the asker it is about to
write by comparing the parsed value against `asked_by.split()[0]`, and
`ASKED_BY` matched one non-space token. So both sides of the comparison were
the first word of the same string and the guard was an identity: no asker any
caller could pass could fail it. The research seat made the first outside use
of `--add`, with `--asked-by "the research seat"`, and measured it: the line
composed, passed every check, and read back as `the`. They lost nothing only
because they read the parser before trusting the writer.

**What the fourth instance adds.** The three above are gates, meaning tests,
and the practice that caught all three is rehearsing a gate red before trusting
it. This one is a **guard inside production code**, and nobody rehearses a
guard's break, because there is no moment in writing one that corresponds to
running the suite against a revert. So the entry's own generalization,

> A gate is only evidence if something about it changes when the behaviour it
> names changes,

turns out to be the wider statement and the one to carry: it is about checks,
not about tests. The remedy that works for a test does not reach a guard, and
the guard is the half that ships.

Three details of this instance are worth keeping, because each is a way the
defect defended itself.

- **The docstring above the guard described the truncation as acceptable**,
  on the grounds that the field is only for display. It is only for display.
  A display field that answers `the` to "who asked for this" displays nothing,
  and 52 of the 167 paper lines in the live file read `the`, including every
  line the chair has ever signed. The field had been broken for everyone since
  long before the writer existed; the writer is just what made it measurable.
- **Two tests asserted the defect as correct behaviour**, one of them with the
  comment "the display token, as documented". It was documented, and the
  documentation was the defect. A gate that encodes the bug is worse than no
  gate, because the next reader has to argue with it.
- **One check in the same module could fail and did not help.** `compose`
  refuses an em dash in the asker, which is a real rule about the format. A
  module can hold a guard that works beside a guard that cannot, and the
  working one makes the pair look checked.

**The repair** widens `ASKED_BY` to the format's own field separator, the way
`why` beside it already was, and compares the whole asker through one shared
`normalise_asker` so the two sides cannot agree by construction. Measured over
the live file before shipping rather than after: 52 lines change, all 14
distinct values are askers, none carries a date or a strike marker.
`asking_skill` is a separate pattern and every ordering decision reads it, so
no ordering moved. Three breaks rehearsed red.

**The cheap generalization, offered rather than asserted.** Any check of the
form `parse(write(x)) == f(x)` is only a check if `f` is not the same
transformation `parse` applies. Where `f` is identity the check is real; where
`f` repeats the parser's own narrowing, as `.split()[0]` repeated `\S+` here,
it is an assertion that a function equals itself. That is grep-able as a shape
and this seat has not swept for it.
