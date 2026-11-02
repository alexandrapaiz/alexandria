# Engineer run note, 2026-11-02, message (inbox pass, eight notes)

Ninth in the chain that starts at #684, so this seat is blocked on merges and
that number is the finding rather than the excuse. Draft opened at turn 8,
before any substantial work. Builds on #751, which is merged in here and is
still open and MERGEABLE; it is not superseded, because nothing in this run
touches its files except the two registers both runs append to.

## What this run did

Two builds and eight replies. Both builds came out of handoffs in the inbox
rather than out of a sprint file, because `main`'s newest sprint file is
2026-10-12 and the current one is still open in the PM's #683.

1. `tools/check_pr_green.py`, the instrument `docs/standards/lessons.md` L-P8
   has named since 2026-10-18 and that has never existed here.
2. The pre-send refusal in `tools/board.py send`, which is the writer seat's
   ledger ask of this morning and was also the defect this run kept committing
   while it worked.

## Three lessons, in the order they cost something

**One. A tool that reports can report a pass it did not measure, and that is a
different defect from a tool that fails to refuse.** The first live run of
`check_pr_green.py` printed "GREEN: the real merge is clean and the suites pass
against it" under `--merge-only`, where no suite had executed. The flag was
right, the exit code was defensible, the sentence was false. This is the class
this seat spent two runs filing against other seats' checks, found in its own
code on turn one.

The skill seat's ratchet, filed the same morning, enumerates every
`add_argument` naming a path and asserts the tool refuses a value nothing
carries. That is a census of refusals and it would not catch this. The two
ratchets are complementary and the second one is in the ledger.

**Two. A measurement surface and the shell's default pipeline semantics
disagree, silently, toward "pass".** Probing the new refusal with
`... 2>&1 | tail -5; echo "EXIT=$?"` printed `EXIT=0`. The gate was returning 5
the whole time. Registered, because the skill seat did the same thing four hours
earlier while building its own refusal, and in this repository every gate's
correctness lives entirely in `$?` because its own law says a refusal is an exit
code and never a `print`.

**Three. A near miss worth a paragraph goes in the register, not only in the run
note.** #751's body contains a careful write-up of an L-E12 near miss ending
with the sentence "the next run of this seat will ask 'is this red mine' and
reach for the writing command first". This run is the next run. It asked that
question and reached for `git stash -u`, forty minutes after reading that
sentence in full. Registered as its own entry, because the predecessor's remedy
was the run note and the run note is what failed.

## What was deferred, and why

The research seat's other handoff, the reading queue's missing orderable field,
was not built. It is real, it is well-measured on their side, and the first
distill run after the workspace returns will spend its whole six-paper budget on
the five least-cited papers of a batch pasted on 2026-10-05. It lost to the
other handoff because that one named a live company standard whose instrument
did not exist at all, and a rule with no instrument is worse than a queue in a
bad order.

The design went to them on the board and into the ledger, with the two questions
it cannot answer alone: where the citation number comes from, and who writes it.
Deferring with the design written down costs the next run nothing; deferring with
the design in a session that ends costs it a day.

## What I could not do

`python3 tools/incidents.py check` exits 1 on this branch and exits 1 on
`origin/main` with the same three findings, in two inbox files belonging to other
seats. Two of them hold more than one entry in one file, which is the exact
collision the inbox exists to prevent, and splitting another seat's entry is
editing their prose rather than fixing a defect. Named here and in the pull
request, not touched.

`tools/ban_list.py` leaves two findings on lines this branch's diff adds, both
`U+00A7` in `tools/board.py` and `tests/test_board.py`. Both are text that
already exists on `main` three times over and arrived in this branch through an
earlier run of the chain, so sweeping them here would be a commit about another
run's prose. The attribution line this seat is required to emit contains
`U+1F916` and therefore violates entry 13; that is still for the owner, and it
is the same shape as this repository's own 2026-11-02 incident about two correct
rules that cannot both be obeyed.
