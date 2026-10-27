## INC-2026-10-26-two-tests-were-red-on-this-branch-and-green-on-main-and-no-instrument-this-charter-names-could-see-either - one of them is the ledger gate repeating, the other is a red test no workflow runs (2026-10-26, skill seat)

**What happened.** This run ran the whole suite before shipping, which is not
what the charter asks for and is what found both of these. `python3 -m pytest
tests/ -q` on this branch: `2 failed, 2208 passed, 1 skipped`. On `origin/main`
both pass.

The first is `tests/test_ledger.py::test_every_live_entry_carrying_a_readable_status_has_the_contract_fields`,
a ratchet at 206 entries missing contract fields. This run's three ledger
appends took it to 209, because each one opened on a prose bullet rather than on
`- Trigger:` and `- What:`. The two instruments this seat's charter names both
said the ledger was fine: `python3 tools/ledger.py --census` printed its census
without complaint and `python3 tools/check_registers.py` printed `0 blocking, 71
warning(s)`. Repaired in this pull request by relabelling the three entries, and
the test is 26 passed.

The second is `tests/test_skill_scope.py::test_scoping_loads_fewer_skills_and_keeps_recall`,
which asserts `scope/body recall >= unscoped recall` and now reads
`0.8776 >= 0.898`. Bisected across the four-run chain this branch carries:
green at `a53ba05e`, red at `5b792013`, which is the commit that revised
`context-window-engineering` and rewrote its description. It has been red for
every commit since, and the `checks` run on `43ff0d7f` was green anyway, because
`.github/workflows/checks.yml` runs `tests/test_skill_receipts.py` and no other
test file in the repository. Not repaired here: `tests/` and `tools/` are both
outside this seat's write surface, and the repair the red test asks for is
tuning a reader-facing description until an experimental selector passes, which
is the one repair this seat should not make. Filed as a ledger entry for the
engineer with the measurement and the bisect.

**Why it is in this register.** The first is a repeat.
`INC-2026-10-26-the-ledger-instrument-a-charter-names-does-not-ratchet-what-the-ledger-test-ratchets`,
filed by this seat earlier today, recorded exactly this: the ledger instrument a
charter names does not ratchet what the ledger test ratchets, so a seat that
obeys its charter ships a red ledger test. That entry is on the branch of #582
and this is the second instance, which is what the standing rule records.

The second is new in shape and belongs beside it, because both have the same
cause. A gate exists, it is correct, and the path a seat is told to walk does
not pass through it. For the ledger the path is a named instrument that checks
less than the test. For the scope test the path is CI, which runs one test file
out of 60-odd and is the only green light a seat sees before it asks for a
merge.

**What it cost.** One 558-second suite run, which is the only reason either was
found, plus six worktree checkouts to bisect the second. The scope test has been
red for four commits and three pull requests, every one of which reported green
checks honestly, because the checks were green.

**The fix, or why there is not one yet.** The ledger half is repaired in this
pull request and the repair is the same one the earlier entry proposed, which is
that the instrument should ratchet what the test ratchets. It is still owed, and
it is still not this seat's file.

The second half is cheaper than it looks and it is worth stating as a general
rule rather than as one workflow edit. **A test suite that CI does not run is
not a gate, it is documentation**, and this repository has 2,210 tests of which
CI reads the 19 in one file. Either the `checks` workflow runs `pytest tests/`,
which took 9 minutes 18 seconds here and is affordable, or every seat's charter
stops implying that a green pull request means a green tree. The first is one
line in a workflow this seat may not edit, so it goes to the relay with the
measurement attached.
