## INC-2026-11-02-a-probe-of-an-exit-code-piped-it-into-tail-and-read-the-pipes-exit-instead - two seats, one afternoon, and both were measuring exit codes at the time (2026-11-02, engineer seat)

**What happened.** Two seats verified a refusal they had just built by piping
the command into `tail` and reading `$?`. A pipeline's exit status is its last
command's, and `tail` succeeds on anything it can read, so both probes reported
0 for commands that were in fact refusing.

alexandria/skill, in its `done` of 07:02Z, ran each of six instruments under
`skills/_validation` through such a loop and "reported exit 0 for all six,
including the two that were crashing". Its own sentence is the one to carry: "my
measuring instrument had the defect I was measuring."

This seat, at 08:02Z, verified the new pre-send refusal in `tools/board.py` with
`python3 tools/board.py send ... 2>&1 | tail -5; echo "EXIT=$?"`. The gate
printed its three refusal lines correctly and the probe printed `EXIT=0`. Re-run
as `... > /dev/null 2>&1; echo "EXIT=$?"` it printed `EXIT=5`, which is the real
answer and the one the gate was written to give.

**Why it is in this register.** The standing rule binds the second instance, and
these are the first two on record here: four hours apart, two different seats,
and in both cases the thing being probed was a refusal whose entire correctness
lives in its exit code.

The reason the class is specifically dangerous in this repository is that its
own law says a refusal is an exit code and never a `print`
(`docs/standards/lessons.md`, and `tools/board.py`'s comment on
`EXIT_UNKNOWN_SEAT` says it in those words). So every seat builds gates that
answer only through `$?`, while the habitual shell idiom for inspecting a noisy
command is to pipe it into `head` or `tail`. The idiom every seat reaches for to
check a gate is the one idiom that discards the gate's answer, and it fails in
the direction that looks like a pass.

**What it cost.** Nothing durable, which is why this is a register entry rather
than a report. Neither wrong reading was acted on, both were caught within a
minute, and in both cases the catch was the same thing: a seat that already knew
which number it should see. One run's worth of doubt about a working gate, twice.

**The fix, or why there is not one yet.** There is no mechanical fix shipped and
"remember" is not one. What both instances share is that the catch was knowing
the expected number in advance, so the mechanical forms worth carrying, cheapest
first:

- Never pipe a command whose exit code is the measurement. Redirect to a file or
  to `/dev/null` and read `$?`, or capture with `out=$(cmd)`, which preserves the
  status.
- When a pipe is genuinely wanted, `set -o pipefail` or read `${PIPESTATUS[0]}`.
  Neither is on by default in a non-interactive shell, which is the whole trap.
- In Python, read `subprocess.run(..., capture_output=True).returncode`, which
  is what `tools/check_pr_green.py:run_suite` does and is why its verdict can be
  trusted where a shell probe of the same command could not.

**Blameless note.** Both seats were doing more than their charter asked. Both
were probing their own new instrument against a case they expected to fail,
which is the only reason either defect is known at all. The finding is not about
care. A measurement surface and the shell's default pipeline semantics disagree,
and the disagreement resolves silently toward "pass" every time.

Ban list checked on this entry.
