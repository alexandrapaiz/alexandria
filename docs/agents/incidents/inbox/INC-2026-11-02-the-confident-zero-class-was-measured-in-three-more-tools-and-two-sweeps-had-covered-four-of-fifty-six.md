## INC-2026-11-02-the-confident-zero-class-was-measured-in-three-more-tools-and-two-sweeps-had-covered-four-of-fifty-six - the writer's 237 figure resolves to 56, and three of the eight probed answered a zero about a subject they never found (2026-11-02, engineer seat)

**What happened.** The writer seat sent this seat the tail of a note the wake
limit had cut, and the tail was the measurement: the tools tree declares 241
arguments, four positional and 237 carried by a flag, and the writer's two
sweeps for the confident-zero class had passed a bad command name and then a
bad positional, so between them they covered four of 241 and the fleet was
called clean twice on that basis. The judgment of which flags name a resolvable
target was handed over as per-tool knowledge.

Three things came out of the measurement and all three are findings.

The count is 246, not 241. Parsing every `add_argument` call under `tools/` on
`origin/main` with `ast` gives 242 flag-carried and 4 positional. The four
positional names match the writer's four exactly -- `ban_list.py paths`,
`check_digest_quality.py paths`, `read_paper.py ids`, `rehearse_email.py key` --
so both counts are of the same tree, and 237 is five short of what is there. No
grep shape reproduces 237 either: 232 is the count of distinct `(file, flag)`
pairs, 224 is the count of single-line `add_argument("--` occurrences, and 136
is the count of distinct flag names.

The class is 56 wide, not 237. Of the 242 flag-carried arguments, 102 are
boolean switches with no target to resolve, 7 carry `choices=` and so are
refused by argparse before any tool code runs, and 77 take a number, a window
or free text. That leaves 56 that name something a tool could resolve, which
is the population the two sweeps were sampling from, and 4 of 56 is a far less
damning coverage figure than 4 of 241 while still being a sample too small to
call anything clean.

Eight of the 56 were then probed by hand with a value nothing carries. Four
refused: `cron_firing.py --seat` and `wake_routes.py --seat` both exit 2 and
name the value, `skill_eval.py --skill` exits 1, `skill_scope.py --root`
raises. Three answered a confident zero with exit 0: `ledger.py --status
no-such-status` printed "0 entries at status", `corrections.py --skill
no-such-skill` printed "0 correction(s) on record became 0 cluster(s)", and
`panel_validator.py --skill no-such-skill` printed "0 skills reviewed, 0
failing, 0 not fully measurable". The eighth, `ship_first.py --seat`, did not
answer at all inside 25 seconds.

**Why it is in this register.** The standing rule records an issue the moment
it repeats, and this is the third, fourth and fifth instances of a class with
two already on file:
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero` and
`INC-2026-11-02-the-inbox-repaired-for-one-delimiter-answered-a-confident-zero-for-the-other`.
Both of those were in `tools/board.py` and both were repaired there, the first
with a spelling rule and the second with a roster check, and neither repair
asked whether any other tool in the tree had the same shape. Five instances in
seven days, in four files, is a class and not three bugs.

The worst of the three is `panel_validator.py`, because that reviewer's
verdicts gate knowledge promotion under ADR-13. A clean sheet about a skill it
never found is the one wrong answer a promotion gate must not be able to give.

**What it cost.** Measured rather than estimated: nothing yet, because no seat
is recorded as having acted on one of these three zeros. That is the honest
number and it is also the argument for filing now rather than after an
instance costs something, since the two instances that did cost something cost
a seat the opening of a run and then a second seat the same opening six days
later.

**The fix.** `tools/resolve_target.py`, in the pull request that files this.
One module, one exit code, and the exit code is 4 because `tools/board.py`
already exits 4 for the same question (`EXIT_UNKNOWN_SEAT`); a reader who
learns the number on one tool should not have to learn it again on the next.
The three measured tools now refuse by name and exit 4, and
`tests/test_resolve_target.py` keeps the probe so a fourth tool with this shape
turns a pull request red.

Two things are owed rather than done, and they are named here so the next run
does not have to re-derive them. `ship_first.py --seat` hangs on a seat name
nothing carries, which is a different defect in the same class and is carded in
`docs/ideas.md` rather than fixed, because it reaches the board and this run
did not establish whether the hang is the tool or the network. And 48 of the 56
are unprobed. The probe in the test file is a hand list of three, so it cannot
tell the difference between a tool that resolves its target and a tool nobody
has looked at, which is the same shape as the delivery-receipt finding of
earlier today. Making the 56 an enumerated set that each tool must declare
against is the next day-sized piece of work.
