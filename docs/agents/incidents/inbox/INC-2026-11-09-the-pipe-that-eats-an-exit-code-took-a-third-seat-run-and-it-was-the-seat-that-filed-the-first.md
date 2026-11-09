## INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-third-seat-run-and-it-was-the-seat-that-filed-the-first - the suite died on a full disk and the shell reported zero, because the run was piped into tail (2026-11-09, engineer seat)

**What happened.** This run started the full suite as
`timeout 1200 python3 -m pytest tests/ -q 2>&1 | tail -18`. It died about a
third of the way through with
`INTERNALERROR> OSError: [Errno 28] No space left on device`, on a host at 99
per cent with 529MB free, and the shell reported exit code 0. The zero is
`tail`'s. A pipeline's exit status is its last command's and `tail` succeeds on
anything it can read, so pytest's own code never reached the shell. I wrote the
first version of the ledger entry for the disk saying the suite "exited 0 after
an internal error", which would have made pytest the silent-pass culprit, and
corrected it after reading my own command back.

**Why it is in this register.** The standing rule binds any repeat, and this is
the third instance and the second filing.
`INC-2026-11-02-a-probe-of-an-exit-code-piped-it-into-tail-and-read-the-pipes-exit-instead`
recorded the first two, four hours apart on 2026-11-02: alexandria/skill
reported exit 0 for all six of its validation instruments including two that
were crashing, and this seat reported `EXIT=0` for a `board.py` refusal that
was really returning 5. **This seat wrote that entry, and this seat typed the
pipe again seven days later.** That is the finding rather than the pipe. The
2026-11-02 entry's own remedy, "when a pipe is genuinely wanted, `set -o
pipefail` or read `${PIPESTATUS[0]}`", is correct, was recorded in the right
register by the right seat, and changed nothing about what the same seat typed,
because nothing between the entry and the command ever opens the file. That is
incident 20's shape exactly: a register with a gate on writing and no gate on
checking.

**What it cost.** Nothing durable this time, and only because the output file
was readable: the internal error was in the text above `tail`'s window and I
read it rather than the code. Had the error landed outside the last 18 lines,
this run would have recorded a passing suite over a run that stopped at 30 per
cent, and the merge rule reads "the run is green" off exactly that.

**The fix, or why there is not one yet.** No code fix, and saying so is the
point. The previous entry already carries the correct remedy and a third
instance proves that recording it is not what makes it fire. What would fire is
a line in the charter every seat reads before it works, next to the existing
`grep` and `gh run list` commands, rather than a sentence in a register a seat
opens weekly. I cannot put it there: a charter edit is the owner's merge and
this seat's daily pull request may not carry one. So it is proposed in
`docs/ideas/inbox/` and named here, and the next seat that pipes a gate into
`tail` is the measurement of whether that was enough.
