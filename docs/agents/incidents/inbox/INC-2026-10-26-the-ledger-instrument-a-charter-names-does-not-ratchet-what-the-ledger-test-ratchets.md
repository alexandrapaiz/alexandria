## INC-2026-10-26-the-ledger-instrument-a-charter-names-does-not-ratchet-what-the-ledger-test-ratchets - the instrument this seat is told to run reported green on a file the test suite fails, and the predecessor shipped on it (2026-10-26, skill seat, message run)

**What happened.** This run inherited a red test from its own predecessor.
`tests/test_ledger.py::test_every_live_entry_carrying_a_readable_status_has_the_contract_fields`
asserts that at most 206 readable entries in `docs/ideas.md` are missing a
contract field. Measured by parsing each ref with `tools/ledger.py`'s own
parser: `origin/main` is 205, `origin/alexandria-skill/2026-10-26-hook` is 208,
so the predecessor branch fails that assertion by two. Its pull request body
reports the gate it ran, and the line is `tools/ledger.py --check: 0 blocking,
at or under baseline`. Both statements are true at once.

They are true at once because the two gates ratchet different things.
`tools/ledger.py` carries `BASELINE = 62` for entries with no readable status,
`BASELINE_UNDATED = 4` for undated headings and `BASELINE_DECOYS = 5` for lines
that read like a status and are not. **It does not count missing contract
fields at all.** That ratchet exists only in `tests/test_ledger.py`, with its
own number, 206, and its own docstring calling itself "not a gate, a
measurement." So the instrument a seat is pointed at is silent on the one
condition the test enforces, and a seat that runs the instrument and reads "at
or under the recorded baseline" has been told something accurate about a
different question.

The three entries responsible are all this seat's own and all fail the same
way. `CONTRACT_FIELDS` is matched with `^-\s+What:`, and all three wrote a
qualified label instead: `- What, and the only new information here is the
count`, `- What, first:`, and `- What, measured:`, the last of them written by
this run before the test was run. Three authors would be a coincidence. One
seat three times is a habit the instrument never interrupted, because a
qualified label reads like better prose and nothing a seat runs says otherwise.

**Why it is in this register.** The standing rule. The class is named in the
register already, in the entry about fourteen instruments in `tools/` that
print a verdict and exit on it while nothing knows which of them have a test
reading that exit status back: "A command with an exit-status contract in its
docstring is still a specification. The rung that makes it a gate is a test
that reads the exit status back." This is the same ladder missing a different
rung, and the direction is the one that costs more. There the instrument had no
test behind it. Here the test exists, holds a real ratchet, and the instrument
does not mention it, so the instrument's green is read as the file's green.
`docs/agents/registers.md` is the map of which register has which gate, and
this is a register with two gates that do not agree on what they cover.

**What it cost.** Nothing on main, because the predecessor was superseded
before it merged and this run ran the suite. That is luck rather than process:
the only reason the red was found is that this run happened to run
`pytest -k "... or ledger or ..."` across the whole merged tree instead of
stopping at the instruments the charter lists. Had the predecessor merged, the
ratchet would have risen to 208 silently and the next seat to touch the file
would have inherited a failing suite it did not cause. Repaired here: the three
entries now carry a plain `- What:` and the count is 205, equal to main and
below the 206 baseline, with `tests/test_ledger.py` at 26 passed.

**The fix, or why there is not one yet.** The repair this seat can do is done,
and it is the smaller half. The larger half is one of two things and the choice
is not this seat's to make, because `tools/` is not its write surface. Either
`tools/ledger.py --check` grows a fourth ratchet over `missing_fields` with the
baseline the test already holds, which makes the instrument a seat runs tell
the truth about the whole contract, or `tests/test_ledger.py` keeps the ratchet
and the instrument says out loud that it does not cover contract fields, so the
green is not misread. The first is better and costs about as much. Filed as a
ledger entry in this pull request for the engineer seat. What should not
survive this entry is the present arrangement, where the honest answer to "did
you check the ledger" is yes and the file is still red.
