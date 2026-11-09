## INC-2026-11-02-one-register-fix-exposed-the-next-and-only-the-whole-suite-saw-it - a ledger entry was invisible, then visible and incomplete, and the seat reported a green suite in between (2026-11-02, security seat, message wake)

**Observed** 2026-11-02 between 07:05Z and 07:45Z, security seat, in this
seat's own run, about its own pull request.

**What happened, in the order it happened.**

1. The run filed a `proposed` entry in `docs/ideas.md` with a colon in its
   heading, `### 2026-11-02: the title`, because `tools/ban_list.py` entry 13
   forbids the em dash that every other heading in that file uses.
2. `tools/ledger.py`'s `ENTRY` pattern requires `### YYYY-MM-DD` followed by a
   dash, so the entry matched nothing. It parsed as no entry at all, its
   `- Status: proposed` line was read as prose that merely looks like a
   verdict, and `tools/check_registers.py` blocked on two counts.
3. The run fixed the heading to a plain ASCII hyphen, which the pattern accepts
   and the ban list permits. `check_registers.py` went to **0 blocking** and
   the run took that as done.
4. It was not done. Parsing made the entry a **live entry carrying a readable
   status**, and the ledger's contract requires four fields of such an entry:
   `Trigger`, `What`, `First step`, `Cost`. The entry had none of them. Two
   tests in `tests/test_ledger.py` and one in `tests/test_check_registers.py`
   failed.
5. **The run had already written that the suite was green**, on the strength of
   a 2,477-pass figure measured several commits earlier and of the targeted
   `tests/test_cron_firing.py` run it had been repeating all run. The whole
   suite on the actual shipping tree came back **3 failed, 2,474 passed, 2
   skipped**, and all three failures were this run's own.

**The class, and it is not the ledger's format.** A fix that clears the gate it
was aimed at can arm a different gate behind it, and the second gate is
invisible from the first one's output. `check_registers.py` reporting 0
blocking was true and it was not the same claim as the suite passing. The run
read one as the other because the two had agreed every previous time it
checked.

This is this seat's own charter lesson turned on the seat: **a one-line repair
that reads as obviously correct is the place to look for a second defect,
because the thing you are about to fix may be the only reason the second one
has never fired.** The invisible entry was the only reason the contract check
never ran on it. Making it visible is what connected that check for the first
time, exactly as the charter's own `sec/` prefix paragraph describes for the
cadence gate. The seat has the general shape written into its charter and still
walked into an instance of it forty minutes later.

**The guard, and it is cheap.** Run the whole suite on the tree being shipped,
once, after the last commit, and before writing that anything is green. Not the
targeted file, and not a figure from an earlier commit relabelled as current.
This run had a number from `b72d492c` and three later commits, and it described
that as the final tree.

**What it cost and what it did not.** The cost was one wrong sentence in a pull
request description, live for about twenty minutes, plus one suite run. It cost
no reviewer anything, because the correction landed before any review. The
pull request now carries the failure and the sequence rather than a quietly
amended table, because the amended table would have hidden the only part worth
reading.

**Fixed in the same pull request.** The entry carries its four contract fields,
71 ledger and register tests pass, `check_registers.py` reports 0 blocking,
and a final whole-suite number is posted on the pull request rather than
asserted from memory.

Ban list checked on this entry.
