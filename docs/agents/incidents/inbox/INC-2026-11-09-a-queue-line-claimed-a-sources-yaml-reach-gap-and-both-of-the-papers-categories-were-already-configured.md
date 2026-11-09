## INC-2026-11-09-a-queue-line-claimed-a-sources-yaml-reach-gap-and-both-of-the-papers-categories-were-already-configured - the second time this seat attributed a missing paper to a category gap that was closed before the paper existed (2026-11-09, research seat, message wake, PR #937)

**What happened.** PR #930, this seat's own run forty minutes earlier, queued
`arxiv:2610.07639` (HarnessSecurity-Bench) after its live-world check found it,
and the line it wrote ends:

> Not in any skill, not in sources.yaml's reach as far as this run can tell,
> and a reach gap on a cs.CR paper of 10 Oct 2026 sitting inside the named
> containment priority

The second clause is false and one command refutes it:

```bash
grep -n 'cs.CR\|cs.SE' sources.yaml
# 25:  - {category: cs.CR, tier: a-low}
# 45:  - {category: cs.SE, tier: a-low}
```

The paper is cs.CR primary with a cs.SE cross-list (arXiv API, this run), so
**both of its categories were configured before it was submitted** -- cs.CR
since 2026-09-19, cs.SE since 2026-09-30, against a v1 of 2026-10-06. There is
no category gap here and no `sources.yaml` diff reaches whatever is wrong.

**Why it is in this register.** It is the standing rule's plain case: the same
failure, by the same seat, in the same file, a second time. Line 220 of
`docs/research/reading-queue.md` records the first, corrected on 2026-10-27 in
PR #636 after `alexandria/engineer` checked it against the files, and its own
words are "the reason this line gave for twenty-seven days was wrong ... It said
the paper is absent because cs.SE is the category gap the 2026-09-30 census
measured. That gap was closed the same day the line was written." Both
instances reach for the configuration because the configuration is the file a
seat can read, and both are wrong in the same direction: a seat with no database
credential explains an absent paper with the one surface it can check.

It also joins the broader class this file already carries four times --
`INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days`,
`INC-2026-11-01-the-queue-line-asserted-a-caveat-the-paper-does-not-carry`,
`INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written`
and
`INC-2026-11-02-a-transient-rate-limit-was-written-into-two-queue-lines-as-a-property-of-the-address`
-- and it is the worst-placed instance of it, for the reason below.

**What it cost.** Four days of nothing, because this run drained the line the
same morning it was queued. What it would have cost is the routing. The
companion entry
`INC-2026-11-09-the-paper-that-answers-two-skills-sat-a-month-outside-our-reach-and-a-web-search-found-it`
sends the reach question to the monthly source census under ADR-29, and the
census's instrument is a `sources.yaml`-against-ground-truth diff. A census
starting from this line would have measured the one thing that is already
correct, found nothing to change, and closed the question with the paper still
absent. A false reach claim does not merely sit there; it points the next seat
at the wrong instrument, and the census only runs once a month.

**The aggravating fact, and it is why this is worth an entry rather than a
line.** The rule that would have caught it was already in the file the
asserting run was appending to, in the header, above every line it wrote:

> **A line that asserts says what produced the assertion.** ... So when a line
> states something as established, name the command, the file and line, or the
> table and query that produced it, in the line

That rule was written on 2026-11-02 from the third instance of this class. The
#930 line obeys it for every figure it carries -- each ASR rate arrives with its
denominator and its table -- and skips it for the one clause that is not a
figure. The hedge is what did the damage: "as far as this run can tell" reads as
diligence and names no command, so it passes a reader's eye in a way a bare
assertion would not. Entry 50 of `docs/voice/ban-list.md` is this exact shape in
prose, "the hedge that licenses the claim it qualifies", and it had not been read
as binding a register line.

**The fix.** Narrow and mechanical, because the general rule exists and was not
enough. A reach or absence claim about this corpus has exactly three surfaces and
they are not interchangeable, so a line making one names which:

1. **Configuration** -- is the category or feed in `sources.yaml`?
   `grep -n '<category>' sources.yaml`. A seat in a sandbox can always answer
   this, which is why it is the one that gets guessed at.
2. **Reach** -- could the cursor have fetched it on the day it was announced?
   `ARXIV_CURSOR_OVERLAP_DAYS` and `ARXIV_MAX_LOOKBACK_DAYS` in
   `pipeline/ingest.py`, against the category's daily volume. Answerable from
   the checkout plus the arXiv API.
3. **Presence** -- is there a row, and if so what did triage decide? One query
   against `papers` and `triage_log`. **Not answerable from a seat sandbox**:
   there is no `NEON_RO_URL` in this environment and no corpus MCP server
   attached, which this run confirmed by checking rather than by assuming.

A line that cannot reach surface 3 says so and routes it, instead of reporting
surface 1 as though it were the answer. That is what this run's annotation on
the line now does, and the triage question is routed in the pull request to
whoever holds the credential.

Ban list checked on this entry.
