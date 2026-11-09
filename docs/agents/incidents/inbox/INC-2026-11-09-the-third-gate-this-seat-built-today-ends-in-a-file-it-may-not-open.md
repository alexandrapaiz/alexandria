## INC-2026-11-09-the-third-gate-this-seat-built-today-ends-in-a-file-it-may-not-open - every enforcement point this seat's surface needs is in `tests/`, `tools/` or `.github/workflows/`, and the seat's write surface is `skills/` (2026-11-09, skill seat)

**What happened.** This run built
`skills/_validation/prose_distribution.py`, the prose half of the engineer
seat's `check_status_tables`: it reads every sentence in `skills/` that puts a
backticked grade beside a count, a skill name or nothing, and `--check` exits
non-zero when one disagrees with the frontmatter on disk. It measures 9 claims
checked and 9 agreeing over the library, and `--self-test` breaks a copy of the
tree nine ways and all nine move the exit code. It is a finished gate and
nothing invokes it, because the chain that actually runs on this repository is
a hand list of `tests/test_*.py` files in `.github/workflows/checks.yml`, and
`tests/`, `tools/` and `.github/workflows/` are all outside this seat's write
surface. Nothing outside `skills/` references `skills/_validation` at all, which
is one `grep -rln` and covers seven instruments this seat has shipped there, so
the finding is about the directory and not about today's file. The same shape
closed two other items on this seat's surface in the same twenty-four hours.
`docs/product/install.md` restated the grade distribution in a table wrong in
seven places for thirteen days, and the seat that writes `status:` may not open
that page, so the engineer repaired it. The ban-list sweep over
`provenance.papers` took the library from 59 mechanical findings to 0 and was
reverted the same run, because `tests/test_skill_gate.py` carries a deliberate
tripwire that fails a revision adding findings while tolerating the existing
backlog, which means the seat told to clear the backlog cannot ship the cleared
state. Three items, three dead ends, one cause.

**Why it is in this register.** Third instance in one day of one class, and the
class already has entries from two other seats. The nearest prior readings are
the second finding of
`INC-2026-10-26-two-tests-were-red-on-this-branch-and-green-on-main-and-no-instrument-this-charter-names-could-see-either`,
whose own words for it are that a gate exists, it is correct, and the path a
seat is told to walk does not pass through it, and
`INC-2026-11-02-the-column-repair-landed-in-the-reader-no-seat-can-run`, filed
by the writer seat as the fifth instance of the partial-landing class in eight
days. `INC-2026-10-26-the-copy-rounds-precondition-cannot-be-met-by-the-seat-it-blocks-and-four-runs-have-read-it-four-ways`
is the same geometry a layer up, where the precondition cannot be met by the
seat it blocks. What is new today is the denominator. This is not one unlucky
file: it is every enforcement point the seat's own surface needs, and the seat
has now reached it three times from three different directions in one day, each
time having already done the part it is allowed to do.

**What it cost.** Nothing lost, and that is the point rather than a mitigation.
All three pieces of work were completed and measured before the boundary was
reached, so the cost is latency and a second seat's run each time rather than
rework. For the ban-list sweep it was one run's work reverted and handed over
with its measurement attached. For the table it was thirteen days of a wrong
page that neither seat's discipline could have shortened. For this gate it is
one line in a file this seat cannot write, against a module that is finished,
tested and green today. By the standing rule's own arithmetic the class has now
cost at least five runs across three seats.

**The fix, or why there is not one yet.** Not this seat's to make, in the
strictest sense available: the repair is a charter or a standard deciding where
a seat's enforcement points live, and widening this seat's own write surface is
reserved to the owner with no silence rule attached, so it cannot be proposed
as an ask that proceeds. What is filed instead is the one-line wiring request,
`docs/ideas/inbox/2026-11-09-the-prose-gate-over-skills-is-built-and-this-seat-cannot-arm-it.md`,
sent to the engineer on the board. The alternative worth putting in front of
whoever reads this register: a single test file in `tests/` that discovers and
runs every `--check` under `skills/_validation/`, written once by the engineer,
would arm every instrument this seat ships from now on without another
handover. That is a smaller change than three more filings, and it is the
mechanical half of L-A22 applied to a whole directory rather than to one file.
