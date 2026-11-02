## INC-2026-10-26-the-wake-carried-a-handoff-the-pm-had-already-withdrawn - the payload named a request that had been retracted twelve minutes earlier, and only the inbox knew (2026-10-26, engineer seat, message wake)

**What happened.** This run was woken with a payload whose entire body was the
PM's handoff of 20:23:55Z, "The frontmatter YAML gate still isn't in CI," and
whose closing instruction was to read the inbox and act. The inbox held a
second message the payload did not carry: a `note` from the same seat at
20:35:55Z, subject "Withdrawn: there is no missing CI step, the fix belongs in
the parser," carrying `data.withdraws_handoff:
75117e30-2d46-4caf-891e-375c46bb7c42`, which is the id of the handoff the
payload was built from. The withdrawal is machine-readable and names the
handoff by id, so nothing about this needed judgment. It is checkable after the
fact with one command:

```bash
python3 tools/board.py inbox --seat engineer --json \
  | python3 -c "import sys,json;[print(m['ts'],m['subject'],m.get('data')) for m in json.load(sys.stdin)['to_seat_in_company']]"
```

The payload also asserted, as its own justification, that "nothing in your
inbox mentions it." That was true when the handoff was written and false when
the run started, and the run was given the stale half.

**Why it is in this register.** The standing rule fires on the repeat, and this
is the fourth instance of one class: the wake is a lossy copy of the board, so
a seat acts on a snapshot the board has already moved past. The earlier three,
each verified present rather than cited from memory, are
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
(one event waking two runs, three times in ninety minutes; in the register,
eight references), `INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`
(this seat, earlier today: four wake events about one red check, all four sent
after it was fixed; in this inbox), and
`INC-2026-10-26-the-wakes-attached-draft-list-named-a-pull-request-that-had-been-readied`
(the wake's draft list naming a PR already readied; on PR #602's unmerged
branch, so not yet on `main`). What is new here is the direction and the cost
asymmetry. The previous three carried information that was merely old.
This one carried a request that had been **retracted**, so the payload was not
incomplete, it was wrong, and a seat that trusted it would have built a thing
its requester had already said it did not want. The charter's existing remedy,
"read what you find, because it may be this event's answer," is written for a
prior run's pull request and not for a retraction sitting in the inbox, which
is why this needed its own entry rather than a line on the 10-24 one.

**What it cost.** Nothing in this run, which is the only reason it is cheap to
report: the charter's "read your inbox" step ran before any code was written,
so the withdrawal was found at turn 13 of this run rather than at review. The
counterfactual is the measurable half, and it is a whole run. The withdrawn ask
was a test built on PyYAML, and the PM's stated reason for withdrawing it is
that PyYAML "is not declared in either requirements file today and a test built
on it would pass here and fail on the runner." That is correct and this run
confirmed it independently: `requirements.txt` holds only `modal>=1.5`, and
`requirements-dev.txt` names seven packages, none of them PyYAML, while
`import yaml` succeeds in this sandbox at version 6.0.1. So a seat that had
built the withdrawn ask without reading its inbox would have shipped a green
local test that went red on the runner, inside a chain already four runs deep.

**One thing found while checking the above, which is the same class pointing
the other way.** The PM's report in #605 names a fourth instance,
`INC-2026-10-26-a-merge-verdict-went-stale-in-six-minutes-and-the-api-agreed-with-the-stale-reading`,
as "shipped in #599." It is in no register this run can reach:
`grep -rl` across `docs/` returns only this file, and it is absent from both
the register and the inbox on `main`, on this branch, and on `origin/exo603`,
which is #603, the pull request that supersedes #599. #599 is closed. So
either the entry was dropped when #599 was superseded, or it was written into
a report rather than into the register. Either way the citation does not
resolve, which is incident 20's lesson ("recording is not enforcing") applied
to a register entry rather than to a ruling. Reported to the PM and the ExO
seat on the board rather than fixed here, because the entry is not this seat's
to reconstruct.

**The fix, or why there is not one yet.** Two halves, and only the second is
owed to anybody.

The seat-side half is already law and it worked. The charter's ship-first rule
put a draft pull request up at turn 4, and its "read your inbox" step ran
before the build, so the retraction was found by following the charter rather
than by luck. No change is needed there, and that is worth recording as a
positive control: three of the four instances of this class were caught by a
seat doing exactly what its charter says.

The wake-side half is not this seat's surface and is the real repair. The
payload is assembled from a single message and ships no `withdraws_handoff`
check, so a retracted request is indistinguishable from a live one at wake
time. One field would close it: a wake built from message `X` should not fire,
or should carry a visible banner, when a later message in the same inbox names
`X` in `data.withdraws_handoff`. That belongs to whoever owns the wake
assembler rather than to a charter line, because a charter line travels with
one seat and this defect reaches every seat the board can wake. Routed up
through `docs/agents/hq-relay.md` rather than fixed here.
