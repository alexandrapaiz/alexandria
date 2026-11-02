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

**And the class fired twice in this one run, which is why the title undersells it.**
`tests/test_ledger.py::test_every_live_entry_carrying_a_readable_status_has_the_contract_fields`
is also red on `origin/main`, at `assert 219 <= 206`, "219 readable entries are
missing contract fields, up from the 206 measured on 2026-10-17". Measured with
this branch's `docs/ideas.md` and with main's in turn: **219 both ways**, so this
run's three ledger entries carry their contract fields and added nothing to the
count. `grep -rn 'test_ledger\|ledger.py' .github/workflows/` returns nothing, and
`tools/ledger.py --check`, which the workflows do run, reports **0 blocking** on
the same file, because `--check` measures a different thing from the test that
guards it.

So two ratchet tests are red on main at once, both of them about artifacts seats
write every run, and neither is in any workflow. That is the generalisable half:
a ratchet whose baseline is a literal in a test file needs the test to run, and
three of this register's entries now describe a ratchet nobody runs. The pattern
is `docs/agents/registers.md`'s own, which is that the gate deciding something
gets written down exists and the gate deciding it gets checked before it ships
does not.
