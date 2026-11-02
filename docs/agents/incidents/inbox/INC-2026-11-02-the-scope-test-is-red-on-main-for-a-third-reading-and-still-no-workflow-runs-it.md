## INC-2026-11-02-the-scope-test-is-red-on-main-for-a-third-reading-and-still-no-workflow-runs-it - the third distinct pair of numbers in eight days, and this run's body edits moved it by nothing at all (2026-11-02, skill seat, message wake)

**What happened.** `tests/test_skill_scope.py::test_scoping_loads_fewer_skills_and_keeps_recall`
is red on `origin/main`, at `assert 0.9184 >= 0.9592`.

**Why it is in this register.** Third instance of
`INC-2026-11-01-the-length-law-moved-the-scope-test-a-second-time-and-no-workflow-ran-it`
and of the 2026-10-26 entry it repeats. The numbers on both sides of the
assertion have now been recorded three times and no two readings agree:

| recorded | scoped recall | unscoped recall |
|---|---|---|
| 2026-10-26, skill seat | 0.8776 | 0.898 |
| 2026-11-01, PR #665 | 0.8163 | 0.898 |
| 2026-11-02, this run | 0.9184 | 0.9592 |

**The half that narrows the earlier entries rather than repeating them.** This
run edited three skill bodies: two clause cuts in `harness-engineering` and a
heading folded into `Caveats` in `agent-containment`. The test reads the body.
Measured with the working tree against `git stash`, the assertion is **0.9184
against 0.9592 on both sides, identical to four digits**. So the second
reading's finding holds and strengthens: the ratchet is not monotone in body
length, and the three readings above moved because the *content* of the
descriptions and bodies moved rather than because any of them got shorter. An
entry that reads this as a length ratchet is reading it too simply, and tuning
a skill body against this assertion would be tuning a reader-facing artifact
until a lexical selector passes.

**Still unrepaired, and now across four merges.** No workflow runs this file.
`grep -rn skill_scope .github/workflows/` returns nothing, and
`.github/workflows/checks.yml` runs nine named pytest files of which this is not
one, so every `checks` run over #665, #669 and this branch was green with the
test already red. Both the test and the scoping tool are outside this seat's
write surface, and the repair the red test invites, editing descriptions until
the selector passes, is the one repair this seat must not make.
