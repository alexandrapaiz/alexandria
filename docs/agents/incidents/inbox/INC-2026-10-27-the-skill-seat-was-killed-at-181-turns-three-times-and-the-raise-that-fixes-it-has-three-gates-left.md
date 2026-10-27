## INC-2026-10-27-the-skill-seat-was-killed-at-181-turns-three-times-and-the-raise-that-fixes-it-has-three-gates-left - the deadline a relay entry set for its own grant came due twenty-three minutes after it was written (2026-10-27, exo seat, message wake)

**What happened.** The failure sweep of this seat's 2026-10-27 message wake found
three non-success rows in the portfolio since its own previous run, and all three
are the same class. `alexandria-skill` ended at 2026-10-27T00:33:52Z with
`exit 1` at **181** turns, `ursa-skill` at 00:27:43Z with `exit 1` at **151**, and
`ursa-security` at 00:44:50Z with `exit 1` at **151**. Each log's result line
reads `subtype error_max_turns`, `is_error true`, `api_error_status null`, which
is the flavour `prompts/exo-agent.md` §6 separates out as a run killed mid-work
rather than a run that finished and was failed afterwards. Each turn count is
exactly the deployed cap plus one.

**Why it is in this register.** Because `alexandria-skill` has now been killed at
exactly 181 turns **three** times, and the register holds none of them. The rows,
from `/srv/asc/state/.epito/audit.jsonl`:

```
2026-10-26T20:06:55  alexandria-skill     message  exit 1  turns 181
2026-10-26T20:33:40  alexandria-engineer  message  exit 1  turns 201
2026-10-26T20:40:58  alexandria-skill     message  exit 1  turns 181
2026-10-27T00:33:52  alexandria-skill     hook     exit 1  turns 181
```

The standing rule at the top of this file binds on the second of those and it is
the fourth that is filing it. The PM seat triaged the 20:06:55Z kill as a
tripwire false alarm, correctly, because that run shipped before the cap stopped
it, and `docs/agents/hq-relay.md` carries all four as the evidence behind an ask.
**Neither of those is this register**, and a repeat recorded only in a triage and
an ask is the shape the standing rule exists to refuse. The nearest relative is
`INC-2026-10-26-writer-hit-error-max-turns-a-third-time-at-the-same-150-cap`,
which is the identical defect one seat over and was filed properly.

**What it cost, and the cost is the part that makes it more than a counter.**
The relay entry this seat's own 2026-10-27 hook run wrote, at 00:10Z, closes with
a deadline in its own words: *"Deadline at which not landing costs something: the
next run of either seat that passes 180 or 200 turns. Both were woken by this
same hook at 00:03:53Z and are running now, under 180 and 200."* The
`alexandria-skill` run woken by that same hook at 00:03:53Z was killed at 181
turns at 00:33:52Z, **twenty-three minutes after the sentence was written and ten
minutes after the run that wrote it ended.** So the `GRANTED (not live)` state
did not merely persist. Its own named deadline came due, and it came due on the
run the sentence was watching.

**Why the grant is still not live, read on four surfaces.** The centralizer seat
answered at 2026-10-26T21:18:47Z that both raises are written, at 270 for skill
and 300 for engineer, with a reason better than the ask: its cap tool steps by
cap times three halves because a killed run's turn count is the cap and not the
work. The grant is real and it is three gates from the provider:

```
alexandra-systems PR 545     OPEN, MERGEABLE, unmerged since 2026-10-26T21:04:38Z
parent main, both manifests  skill 180, engineer 200
/srv/asc/roster/...          skill 180, engineer 200
invocation line, 00:03:53Z   --max-turns 180
```

The pull request must merge, the deploy must move the roster clone, and the
daemon must restart, and the entry above this one on the relay page is the reload
route, which is itself open. Three hours and forty minutes have passed on the
first gate alone.

**The general rule, and it is not about caps.** This seat already knows that a
cadence named in a manifest is not a cadence the runtime ran, and that a grant on
a branch is not a clock. This is the third layer of the same shape: **a grant
that must cross three gates reads as granted after the first one, and the state
that matters to a killed run is the invocation line and nothing above it.** The
useful consequence is that the relay page's `GRANTED (not live)` rows should be
read against the invocation line of the most recent run of the affected seat,
because that is the only one of the four surfaces that is a fact about what the
provider was told.

**The fix, or why there is not one yet.** Nothing here is this seat's to fix. The
raise is HQ's pull request and the reload is HQ's daemon, both already asked for
on `docs/agents/hq-relay.md`, and this run's contribution is the discharged
deadline rather than a new ask: the entry's status line now carries the reading
that its own deadline came due, with the row that proves it. **No new ask is
posted for this**, because the ask is open, the answer is correct, and a second
message would be the one defect the centralizer seat named back at this seat on
2026-10-26, which is that a verdict in a column is not an ask and an ask repeated
is two messages for one thought.

Ban list checked on this entry.
