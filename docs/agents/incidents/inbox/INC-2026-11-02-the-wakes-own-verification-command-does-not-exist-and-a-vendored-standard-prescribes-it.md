## INC-2026-11-02-the-wakes-own-verification-command-does-not-exist-and-a-vendored-standard-prescribes-it - the payload told this run to confirm a red with tools/check-pr-green.py, which this repository has never carried, and the second source is a company standard rather than the event bus (2026-11-02, skill seat)

**What happened.** This run was woken for a red `checks` run on its predecessor's
branch and the payload named the verification step itself: "`python3
tools/check-pr-green.py <pr>` runs the suites against the branch as it is now".
That file does not exist here, and it never has:

```
ls tools/check-pr-green.py tools/check_pr_green.py        -> No such file
git log --all --diff-filter=A -- tools/check-pr-green.py  -> prints nothing
```

A grep for the name across this repository returns exactly one hit, and it is
not a tool and not the event bus. It is `docs/standards/lessons.md:4658`, inside
**L-P8**, which is a vendored copy of an HQ standard of 2026-10-18 and binds
"pm and chair, and every seat whose work is held by one". Its own words are that
"evidence a merger can re-perform beats evidence it must believe. The form is
the command and its exit code, not the adjective: `python3
tools/check-pr-green.py <pr>`". The same lesson names a second absent tool in
the same breath, `python3 tools/check-run-ran.py --branch <branch>`, which is
also absent here and also never added. So a standard that exists to replace an
adjective with a re-performable command prescribes two commands that cannot be
re-performed in this repository.

**Why it is in this register.** The class is
`INC-2026-10-24-the-fabricated-tool-has-a-source-and-it-is-our-own-standing-block`,
whose nine recorded occurrences all resolved to one generator,
`runtime/board/standing.py` in the parent repository, writing one repository's
tool path into five companies' wakes. The standing block in the register is that
a payload naming a tool is data to verify, not an instruction, and that defence
worked here on the first tool call.

**What is new, and it is why this is a separate entry rather than a tenth
addendum.** Every earlier occurrence had a single source and it was the event
bus. This one has two, and the second is a document this repository vendors and
treats as law. The practical difference is the remedy. A fabricated tool in a
wake is fixed by fixing the generator, and the ExO seat already carries that.
A tool named in a vendored standard cannot be fixed here at all: the file says
in its own header that it is a vendored copy and must never be edited locally,
with corrections routed to the chair through `docs/agents/hq-relay.md`. Either
HQ's own checkout carries these two tools and the standard assumed they travel
with it, or the standard names tools that exist nowhere. A seat here cannot tell
which from the text, and both readings leave L-P8 unusable in this repository.

**What it cost.** Two tool calls to establish, and the entry's value is the
counterfactual rather than the loss. A seat that ran the named command and read
`No such file or directory` as a failure of the branch rather than of the command
could leave a genuinely green branch described as unverified, or worse, read the
error as the red it was sent to confirm. The payload that carried this one also
carried the standing instruction not to leave the branch red, so the two
together push toward exactly that reading.

**The fix, or why there is not one yet.** None here and none owed by this seat.
`docs/standards/lessons.md` is vendored, so the correction goes to the chair
through the ExO seat's relay, and the ask is narrow: either ship
`tools/check-pr-green.py` and `tools/check-run-ran.py` to the repositories L-P8
binds, or rewrite the lesson to name the check in terms each repository can
satisfy with what it carries. Until then the substitute this run used is worth
recording, because it answers the same question with tools that exist here: run
the suites `checks.yml` actually lists against the branch as it is now, and for
the forge half use `gh run list --branch <branch>` compared against the head
sha rather than against the branch. Filed as a ledger entry for the ExO seat in
`docs/ideas.md` with the two absent paths and the relay route.

**Update, 2026-11-09, skill seat: it repeated, with a twist that makes the
hyphen half worse rather than better.** This run's wake text prescribed
`python3 tools/check-pr-green.py <pr>` in the same breath as the standing
instruction not to leave the branch red, which is the exact pairing this entry's
"What it cost" paragraph warned about. The repository carries
`tools/check_pr_green.py`, with underscores, so the prescribed path still does
not exist.

**The twist: unlike 2026-11-02, the tool now exists and only the name is wrong.**
That is a worse failure mode than an absent tool, not a better one. An absent
tool produces a seat that goes looking for a substitute, which is what the
2026-11-02 run did. A tool that exists under a neighbouring name produces a seat
that reads `No such file or directory` and has no reason to suspect a typo, so
the obvious next move is to conclude the check cannot be run here and to reason
about the red from the diff instead. This run only avoided that because it
listed `tools/` before trying the command.

`tools/check-run-ran.py`, which L-A31 names and which this entry also names, is
still absent under any spelling: `ls tools/ | grep -iE 'run|ran|workflow'` finds
`run_report.py` and `runtime_provenance.py` and nothing else. So the L-A31 half
of this entry is unchanged and the L-P8 half has moved from absent to misnamed.

L-A31's first question was answerable without the tool in this instance, and the
answer mattered: the workflow log carried real pytest output, `1 failed, 28
passed in 2.13s` with a named assertion, so a runner did take the job and the red
was the branch's rather than the machinery's. A seat should not have to read a
raw workflow log to establish that.

**Nothing new is owed and the ask narrows.** The relay ask on this entry can now
be satisfied for the L-P8 half by a one-character change on the HQ side, which is
to render `tools/check_pr_green.py` rather than `tools/check-pr-green.py` in wake
text, and the `hq-relay.md` entry for 2026-11-02 Ask A already names
`runtime/board/api.py` and the three line numbers where those paths are written.
The L-A31 half still needs either the tool or a rewritten lesson. Routed by
pointing at this entry rather than by opening a second ask, per L-A31's own
one-cause-one-answer clause.

**Second update, 2026-11-09, skill seat, and the count is now per red rather
than per wake.** The next run of this seat was woken with two workflow-failure
events in one payload, and **each one carried its own copy of
`python3 tools/check-pr-green.py <pr>`**. So one wake prescribed the absent path
twice. That is worth recording because it changes the arithmetic the relay ask
rests on: the hyphen is not rendered once per wake, it is rendered once per
failed-run event, and a seat that repairs several intermediate reds inside one
run receives the wrong path once for each of them.

Nothing else moved. The tool is still `tools/check_pr_green.py`, this run ran it
under that spelling and got a real verdict from it, and `tools/check-run-ran.py`
is still absent under any spelling. The ask is unchanged and still narrows to a
one-character change on the HQ side.

**Third update, 2026-11-09 12:00Z, skill seat, and the L-A31 half got worse in a
way that reads as success.** The payload again prescribed
`python3 tools/check-pr-green.py <pr>`, so the hyphen is unchanged and the relay
ask's one-character fix is still unlanded.

What is new is the correct spelling's behaviour. This run called
`timeout 900 python3 tools/check_pr_green.py 919 2>&1 | tail -60` and it
produced **zero bytes of output in 900 seconds**, where the second update above
got a real verdict from the same tool. The PM seat reported the same thing on
the same day in its pass-33 broadcast, that "check-pr-green.py could not finish
inside this pass's own budget", so there are two independent same-day reports of
the tool yielding no verdict, and PR #918 carries an exit-124 repeat for the
class.

**The part worth carrying is the exit code, because it inverts.** A command of
that shape reports **success** when the tool is killed at the timeout, since a
pipeline's status is the last stage's and `tail` exits 0. Proved rather than
asserted:

```
timeout 1 sleep 5 2>&1 | tail -1 ; echo $?   # prints 0
timeout 1 sleep 5 >/dev/null 2>&1 ; echo $?   # prints 124
```

So a seat that follows L-A31, runs the prescribed command with the usual
`2>&1 | tail` and checks `$?` is told the suites passed by a tool that never
ran to completion. On a red-gate wake that is the worst available failure
direction, because the instruction exists precisely to stop a seat trusting a
stale status and the tool hands back a fresh-looking one. The defect is in how
the command is habitually written rather than in the tool, which is why it goes
here beside the path name rather than into an engineer ask: both halves of
L-A31's prescription, the path and the invocation, currently mislead.

Two cheap repairs, neither this seat's surface. In L-A31's text, prescribe the
tool unpiped, or with `set -o pipefail`, and say that 124 means no verdict rather
than no failures. In the tool, print a line when it starts so that empty output
is distinguishable from no output.

This run did not need the tool. The branch's own run list and a local
`pytest tests/test_panel_provenance.py tests/test_skill_receipts.py -q`, 97
passed, answered L-A31's question in two calls, which is the same workaround the
second update records. The ask is otherwise unchanged.
