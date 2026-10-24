# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-24, hook pass (~16:26-16:40 UTC)

**Mode.** This run's trigger is `hook`, not `message`: "capacity returned,
the provider limit that refused your last run has reset." Not Monday, so
charter §0 makes this a standup pass (§4 alone) regardless of trigger type.
No sprint opened, no retro, no grooming.

**Housekeeping.** This seat's own last run left #460 open
(`alexandria-pm/2026-10-24-message-fourth-citation`, fourth in today's
message-pass thread). Chose **build on it**: branched from its tip,
containment verified (`git log origin/alexandria-pm/2026-10-24-message-fourth-citation
^HEAD` printed nothing). This PR supersedes #460; #460 closed with a
pointer here once this one was open and pushed.

**Also checked, and not closed: nine other open PM-seat PRs from today**
(#440, #442, #444, #445, #447, #448, #450, #452, #454). Ran the same
containment proof against each. All nine failed it (1 to 26 commits each,
never zero), so none is contained in this branch and none is closed here.
They are siblings of the #458/#460 thread, not links in it. Full finding
in `pending.md`; it is a reconciliation task for a future pass, not
something this one can resolve without a containment proof or the owner's
say.

**What actually changed since #460 (13:47 UTC), in the ~2h40m gap.**
Nothing merged, nothing new opened, and `gh run list` shows zero runs of
any kind between 13:00:24Z and this run's own start at 16:26Z — a dead
fleet for about three and a half hours. Then, in the same minute this run
started, two other seats opened fresh draft pull requests on the identical
naming pattern: `alexandria-writer/2026-10-24-hook` (#461) and
`alexandria-engineer/2026-10-24-hook` (#462). That is not a coincidence to
flag as a problem, it is the shape of the finding: a provider capacity
limit silenced the whole fleet for roughly three and a half hours, and the
same `hook` event that woke this seat woke writer and engineer at the same
moment. Reporting it because an outage the owner did not see is exactly
the gap section 1f exists to close, not because anything here needs
action — no seat's own PR is red, and `main` is unaffected.

**Nothing dispatched this run, and the queue holds none.**
`PM_DISPATCH_ENABLED` read directly from this run's environment: unset, so
section 5 stays inactive regardless of what follows. Checked the rest of
the criteria anyway. `writer` and `engineer` both just opened fresh PRs
from this same hook wake (#461, #462), so the hard stop in §5 forbids
dispatching either. `frontend` still has #435 open since 06:54, unchanged.
`market`, `skill`, `security`, `okr`, and `research` have no new evidenced
trigger since the last pass — nothing in `docs/decisions.md` or
`docs/allhands/` is newer than the #443 merge commit, and no ruling landed
in the quiet window. Inventing a trigger for an empty three-and-a-half-hour
gap would be the failure this section warns against, not a save.

## The four numbers (queue gauge, charter §4 2b)

1. **`main`'s age and check state.** Newest commit `1765bb3` (merge of
   #443), landed 2026-10-24T13:00:21Z, about 3h25m before this pass.
   Newest `checks` run on `main`: `success`, same push.
2. **Open pull requests:** 15 total, 7 opened since the last merge to
   `main` (#452, #454, #455, #459, #460 this morning, plus #461 and #462
   from this run's own wake).
3. **Conversion, last 7 days:** 78 merged / 137 opened.
4. **Deepest open supersession chain:** unchanged at depth 8, #455 (exo):
   #404 to #411 to #414 to #441 to #446 to #449 to #453 to #455. Nothing
   merged in the gap to move it either direction.

No 48-hour stall. `main` moved 3h25m ago, well under the threshold, so
this stays a normal line rather than the headline.

## Merge call this run: none

Same instruction as every pass today: no merge, no push to `main`. No
Tier judgment exercised.

- **#455 (exo)** is unchanged: Tier C on the file list alone
  (`prompts/*-agent.md`, all fourteen), the owner's to merge.
- **#430 (writer)** and **#435 (frontend)** are unchanged: Tier-B-eligible
  per earlier passes, waiting on each seat's own `gh pr ready`, never on
  the PM.

## Run health

`gh run list --limit 60`: every run in the window since the last pass is
either `success` or doesn't exist (the three-and-a-half-hour gap above).
The six `failure` rows visible in the last 60 are all dated 2026-10-18,
already old and not part of this pass's window. Nothing new to triage.

## Cap ratio

No run in this pass's window reported a `num_turns` figure (the gap had no
runs at all, and `gh run list` does not surface turn counts directly).
Nothing to flag this pass; the live cap question from earlier today
(`exo` at 155/200 turns on #414, `writer`'s last two runs reading over the
line against the stale-cap number #414 itself raised) is unchanged and
already carried in `pending.md`.

## Delivery health (`docs/agents/delivery-health.md`, via `tools/delivery_health.py`)

Ran it fresh this pass rather than trusting the last pass's figures.
**ok:** press (2026-W42, newest), site (3 issues, newest 2026-W42),
archive (ends at 2026-W42). **FAILING, unchanged:** compute, pipeline, and
mcp (Modal workspace `ac-5DsaR3hWSUxqyNoGYiowja` still disabled, taking
down every cron and the MCP server together); checkout (the three
`POLAR_CHECKOUT_*` env vars still unset, no checkout link renders);
deploy (distill 8.6 days behind, ingest 8.0 days, weekly 8.9 days
undeployed behind `origin/main`; the tool's own deadline math now reads
18.5h from now for ingest's next scheduled run, counted from the moment
compute comes back, not a time to work to). **unknown:** payments
(`payment_exceptions` table does not exist; `modal run
pipeline/db_setup.py::apply_schema` is the one owner-only command that
closes it). All of this is owner-only (the Modal workspace and the Polar
secrets) and unchanged from every pass today.

## Dispatched by the PM

None this run.
