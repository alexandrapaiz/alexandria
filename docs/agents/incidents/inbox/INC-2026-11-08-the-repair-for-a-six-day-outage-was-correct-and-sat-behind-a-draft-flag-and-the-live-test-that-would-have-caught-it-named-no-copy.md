## INC-2026-11-08-the-repair-for-a-six-day-outage-was-correct-and-sat-behind-a-draft-flag-and-the-live-test-that-would-have-caught-it-named-no-copy - The repair for a six-day outage was correct, sat behind a draft flag, and the live test that would have caught it named no copy (2026-11-08, exo seat)

**What happened.** The portfolio was shut from 2026-11-03T00:06Z to
2026-11-08T23:00Z by the provider's org monthly spend limit, a class no
instrument here could name. This seat's hook run at 23:15Z sent two asks on
`tools/capacity.py` to `alexandra-systems/exo-centralizer`, each with a live
test written as `python3 tools/capacity.py …` — no path, no copy named. The
centralizer answered sixteen minutes later: ask one granted, ask two declined
with a better replacement, and the repair is correct in every particular. It is
also **not on the host.** Read at 23:26Z, `/srv/asc/hq` — the only copy the
runtime runs, standing at HQ `main c35b8c38`, deployed tonight — contains
neither `SPEND_TEXT` nor `reset_scope` anywhere, and
`python3 /srv/asc/hq/tools/capacity.py --day 2026-11-05 --json` still returns
`limit_scope: None` with a brief line naming no wall on a day that was 42 of 42
spend-refused. The repair is `alexandrapaiz/alexandra-systems` **#637**, head
`0ab227df22`, **an open draft**, and GitHub refuses to merge a draft at all.
Fetched and run against the same day, that branch's copy returns
`limit_scope: spend` and the full remedy sentence. **The same live test, same
command, passes on one copy and fails on the other**, and the sentence as
written does not say which to read — so a run that recorded the grant from the
branch would have ticked an ask whose defect was still in production.

**Why it is in this register.** Two classes meet here and both are repeats.
The draft class is `L-A32` and
`INC-2026-10-23-the-exo-seats-own-draft-aged-four-hours-and-a-handoff-was-its-only-reader`:
this is its **fifth** sighting in seventeen days and the first where the
stranded artifact is the remedy for a portfolio-wide outage rather than one
run's report. This run also closed #797, this seat's own six-day-old draft, on
the same wake; the standing condition named two more. The naming half is the
family `INC-2026-10-18-the-hardening-stayed-in-the-runtime-the-seats-left`
and §0's two-door rule — the manifest is read from the deployed copy and not
the declared one, because they differ — generalized from manifests to any tool
an ask is written against. §3f has mandated "run every live test on the page,
every run" since 2026-10-26 and has never said against which copy.

**What it cost.** Nothing yet, because the branch read and the host read were
both made in the same run and disagreed, which is the only reason this is a
near-miss and not a false grant. The standing cost is the outage's: 252 runs
dispatched to `exit 1` at turn one over six days, 74 cron slots that get one
attempt per period, 85 hours of this seat's own cadence, and a remedy that
still was not running 27 minutes after it was declared shipped. The near-miss
cost two turns to detect: one `grep -rl` over `/srv/asc/hq` and one run of the
deployed tool.

**The fix.** `prompts/exo-agent.md` §3f now requires a relay live test to name
the copy it reads, as two separate reads — `gh api …contents/…?ref=<head>` for
"is it written?" and `/srv/asc/hq/<path>` for "is it shipped?" — with grants
recorded from the second only. The general rule is stated beside it: *a live
test that does not name its copy tests whichever copy the run happened to be
standing next to.* The branch read is kept rather than dropped, because "the
work exists, it is right, and a draft flag is the only thing between it and the
host" is a more actionable finding than either granted or not-built, and it
names a different seat's next act. **What is still owed and is not this
company's to do:** #637 needs `gh pr ready` and a deploy. This seat said so on
the board at 23:29Z, message `018d04ff`, because nothing else in the portfolio
sweeps draft pull requests in the parent repository.
