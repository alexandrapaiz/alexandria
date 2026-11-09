## INC-2026-11-09-the-paper-that-answers-two-skills-sat-a-month-outside-our-reach-and-a-web-search-found-it - a reach gap on the one paper that measures the question two shipped skills turn on (2026-11-09, research seat, message wake, PR #930)

**What happened.** This run wrote, as the residual of its own reading, that no
published work holds a security mechanism fixed and varies the harness. The
L-R1 live-web check, run before shipping, returned
[arXiv:2610.07639](https://arxiv.org/abs/2610.07639) - "HarnessSecurity-Bench:
Do Security Mechanisms Really Protect Coding Agent Harnesses?", v2 [cs.CR],
10 October 2026 - which is that study: nine mechanisms crossed against six
harnesses under one controlled base model, 23 tasks, 2,500 trials, 81,155 tool
calls, plus a ten-mechanism taxonomy rated over 400 harness-mechanism cells.
Verified from the paper (`tools/read_paper.py 2610.07639`, exit 0, 114,176
chars) rather than from the search result. Three siblings came back in the same
search and are equally absent: `2608.17597`, `2605.14271`, `2608.06984`.

The gap is checkable in two commands against `main`:

```bash
grep -rl 2610.07639 skills/ docs/research/        # nothing
grep -c 2610.07639 docs/research/reading-queue.md # 0, before this run appended
```

**Why it is in this register.** ADR-29, the zero-gap mandate, says a reach gap
found by the monthly source census is a register entry and one found by the
owner is a failure of it. This one was found by neither: it was found by this
seat's own per-run live check, which is the intended mechanism working, so the
entry is the record rather than the reprimand. What makes it register-worthy is
the shape. This is not a paper in a thin corner of the corpus. It is a cs.CR
paper, a month old, sitting inside the charter's named AGENT CONTAINMENT
priority, answering the exact question `skills/agent-approval-paths` and
`skills/agent-containment` both turn on, and it was reachable by one web search
from the terms this seat had already written down.

**What it cost, and what it nearly cost.** Nothing yet, because the check ran
before `gh pr ready` rather than after. What it nearly cost is the measure: the
draft of `docs/research/notes/2026-11-09-overeager.md` carried an absence claim
as a finding, and `alexandria/skill` had been sent a revision whose ordering
rests on the weaker paper. Both were corrected in this run, the second by a
second board message to the same seat within the half hour. An absence claim is
the cheapest kind of error to make and the most expensive to leave standing,
because nothing downstream ever re-checks it.

**The fix, or why there is not one yet.** The paper is queued with
`pipeline/reading_queue.py --add`, carrying what was verified, what was not read
(most of it), and the denominators for the figures the partial read did
establish. The reach question - what in `sources.yaml` should have returned a
cs.CR harness-security paper and did not - is the monthly census's, and this run
is a message wake rather than the census. Routed in the pull request with the
three sibling ids, so the next census starts from four names instead of none.

**And the generalisable half.** This seat's queue header already says a line
that asserts must name the command that produced the assertion. That rule was
written for claims about files and tables. It binds an absence claim harder than
anything else it covers, and an absence claim's command is a search, which no
seat was running before L-R1 made it per-run. The honest statement of the rule:
never write "nobody has measured X" in a note until the live check for X has
been run in that same run.

Ban list checked on this entry.
