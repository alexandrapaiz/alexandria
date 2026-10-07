## Updated 2026-10-07, ~06:20 UTC (six-hour pass): the engineer's two main-fix branches merged into one clean, green pull request, and it is still the owner's to merge

**Reconciliation first, per charter §1d.** Read `docs/decisions.md`, the
board, and `docs/agents/incidents.md` back to the last pass (~00:30
UTC). Nothing new to strike: no ADR past ADR-40, no all-hands past
2026-09-18, no incident dated after 2026-10-05.

**Inbox, checked first.** Nothing addressed to `alexandria`'s `pm` is
newer than yesterday evening's reading-enjoyability handoff, already
acted on. One broadcast note (Kimi's prepaid balance, $1.36 available,
from the finance seat at HQ) is informational and addressed to
everyone, not this seat specifically; no reply owed.

**Failed runs, last six hours.** Zero. `gh run list --status failure
--created ">=2026-10-07T00:33:00Z"` (since the last pass's commit)
returns nothing. Nothing to triage, rerun, or file.

**What changed since the last pass.** The engineer closed both of its
own open pull requests (the main-fix branch and the second, separate
branch carrying the real unsubscribe link) and replaced them with one
new pull request, #240, that supersedes both. Checks are green and the
merge state is clean against `main` — an improvement over the last
pass, where the main-fix branch had gone conflicting. It still carries
two files under `prompts/` (`distill.md`, `distill-practices.md`),
which Tier C reserves for the owner, so it waits on exactly the same
ground its predecessor did, just in better shape to merge the moment
she does.

**Tier B merge check, this run, all seven other open pull requests
(the queue's own is excluded by Tier B condition 1):**

- **#240** (engineer, supersedes #233 and #236) — checks green, merge
  state clean, no conflicts. **Disqualified on condition 4 only**: the
  diff still carries `prompts/distill.md` and `prompts/distill-practices.md`.
  This is now the single best candidate in the queue — one merge closes
  `main`'s red suite, a real subscriber row, and a real unsubscribe
  endpoint at once, with no conflict to untangle first.
- **#237** (skill, the independent fix for the same `main` defect) —
  **disqualified on conditions 3 and 4**: checks still red (it branched
  before its own fix reached `main`), and the diff carries
  `prompts/skill-extract.md`. Unchanged from last pass; worth the same
  word on whether the owner wants this landed alongside #240 or treats
  #240 as the one that supersedes the need for it.
- **#238** (writer, third in its own chain) — **disqualified on
  conditions 3 and 4**: checks still red (inherits the same `main`
  defect, cut before either candidate fix existed), and the diff
  carries `prompts/digest.md`. Unchanged from last pass.
- **#60** (engineer, pre-send quality checklist) — **disqualified on
  conditions 4 and 5**: carries `prompts/daily.md` and is conflicting.
  Now **16 days** open, still the oldest open pull request in the
  repository.
- **#205, #203, #202** (finance, OKR, frontend) — drafts, excluded by
  Tier B's own second condition, not reported as blocked.

**Zero of the seven qualify for a Tier B merge this run**, same finding
as last pass, but the shape of what waits improved: one fewer
conflicting pull request, one clean green candidate in its place.

**The Polar Merchant-of-Record account (ADR-30)** remains overdue,
still **11 days**, since 2026-09-26.

**What waits on the owner, one line each.**

1. **Merge #240** — green, clean, no conflicts, closes `main`'s red
   suite, a real subscriber row, and a real unsubscribe endpoint in one
   merge. The highest-leverage single action available right now.
2. **Decide #237** — a second, independent fix for the same defect
   #240 already closes. Land both, or treat #240 as superseding it.
3. **#60**, the pre-send quality checklist, 16 days open, conflicting.
4. **The Polar Merchant-of-Record account (ADR-30)**, 11 days overdue.

**No dispatch fired or queued this run.** Every blocker is an owner-only
merge; engineer, skill, and writer each already hold an open pull
request of their own, which is the hard stop on dispatching any of
them, and none of their own further work clears the blocker anyway.

**Posted to the board**, a first-person note summarizing this pass,
with the same "what waits on you" list above.

## Updated 2026-10-07, ~00:30 UTC (six-hour pass): two more Tier C PRs joined the queue, zero still clear Tier B, nothing new to answer

**Reconciliation first, per charter §1d.** Read `docs/decisions.md` and
the board back to the last pass (2026-10-06, ~17:30 UTC). Nothing new:
no ADR landed, no allhands entry, no board resolution to strike. The
merge-authority grant this tracker struck last pass stays struck; this
run confirmed it operationally, not just by citation (below).

**The grant is real, not just vendored.** Last pass cited the vendoring
of `docs/standards/pm.md` §21 as confirmation. This run went one step
further and checked that the session driving it can actually execute a
merge (`gh pr list --state merged ... --json mergedBy` shows this
seat's own prior pull requests and others', including PRs not authored
by the PM seat, merged through this same route). The grant is live, not
theoretical, which is why the finding below is "zero qualify" rather
than "the question is unresolved."

**Failed runs, last six hours.** `gh run list --status failure
--created ">=6 hours ago"` returns four runs, all the `checks` gate on
the writer's open branch, none an agent seat's own run. All four fail
the same assertion: `skills/agent-containment/SKILL.md` on `main` still
carries an empty `claims` list. This is not a new defect and not the
writer's own: it is the same `main`-level breakage named last pass,
inherited because that branch was cut from `main` before any fix
landed. No rerun, because the same input fails the same way until a fix
merges. No new incident entry, because the root cause and both
candidate fixes are already named below and in the pull requests that
carry them.

**Tier B merge check, this run, all seven open pull requests:**

- **The engineer's main-fix pull request** — checks green, otherwise
  mergeable, but its diff still carries two files under `prompts/`,
  which Tier C reserves for the owner. **Changed since last pass: it is
  now also conflicting against `main`**, not merely clean-but-blocked.
  This is the pull request that, by its own account, also wires the
  real subscriber row and the real unsubscribe endpoint, so one owner
  merge would close three sprint items at once, not one.
- **A second, independent fix for the same `main`-level defect**, from
  the skill seat, new since last pass — also blocked on a file under
  `prompts/`, and its own checks are red (the same assertion, because
  it branched before its own fix reached `main` either). The owner has
  two candidate fixes for one defect now and neither can land without
  her, worth a word on whether both are wanted or one supersedes the
  other.
- **The writer's third pull request in its own chain**, new since last
  pass, replacing the one this tracker named yesterday (that one is
  closed, superseded) — blocked the same two ways: a file under
  `prompts/`, and the inherited `main` defect above.
- **A second engineer pull request**, new since last pass, deliberately
  branched from `main` rather than stacked on the first one, carrying
  the real unsubscribe link in the sent email. No `prompts/` file in
  its diff, so Tier C is not why it waits. It conflicts against `main`
  right now, and its own body already worked out why and in what
  order: the first engineer pull request merges first, then this one,
  and the only collision is two append-only knowledge files with a
  single hunk each. That is the docs-only conflict Tier B lets this
  seat resolve directly, but not yet: the merge order its own author
  named has not happened, so resolving it now would be fixing a
  conflict against a `main` that is about to change again. Queued to
  resolve once the first one lands, not before.
- **The pre-send quality checklist**, unchanged, now **17 days** open:
  a file under `prompts/`, conflicting, waiting only on the owner.
- **Two drafts opened directly by the owner's own window sessions**
  (finance, OKR) and one by the chair (frontend) are excluded from this
  check by Tier B's own second condition, not reported as blocked: a
  draft is work still being written, not a pull request this seat is
  the one holding up.

**Zero of the seven qualify for a Tier B merge this run.** Four wait on
the owner for a file under `prompts/`; one waits on the first of those
four landing before its own conflict is this seat's to resolve; three
are the owner's or the chair's own drafts, not this seat's to act on at
all.

**The Polar Merchant-of-Record account (ADR-30)** remains overdue,
now **11 days**, since 2026-09-26; no live keys visible in the tree as
of this run.

**Nothing addressed to this seat went unanswered.** Read the inbox
first, per the board protocol. The newest item naming `alexandria`'s
`pm` is headquarters confirming it merged this seat's own pull request
last pass, which needs no reply. Nothing older than that pass is still
open against this seat.

**No dispatch fired or queued this run.** Every blocker found above is
either an owner-only merge or a conflict this seat cannot resolve until
that merge lands; no seat's own further work would clear either kind,
so the dispatch criteria do not fire for anyone this pass.

## Updated 2026-10-06, ~17:30 UTC (standup): reconciliation, red `main`'s stuck fix, one dispatch

**Reconciliation first, per charter §1d.** Read `docs/decisions.md` and
the board back to the last pass. One item struck:

- ~~Item: "The merge-authority grant is unconfirmed" (board item
  `00863731`, and this tracker's own 2026-10-05 04:27 and 05:32
  entries)~~ — **resolved.** `docs/standards/pm.md` §21 ("Merges belong
  to the PMs and the chairs, not the owner") is now vendored into this
  repo's own copy, merged as PR #230 (commit `c696875`, 2026-10-06
  00:32:09 UTC). That is the confirmation this item was waiting on; the
  board item is moved to Done with that citation.

**New, top of this run: `main` is red, and the fix is stuck on a Tier C
file.** PR #233 (engineer) measured `main` directly — 19 pytest
failures, all traceable to `skills/agent-containment/SKILL.md` still
carrying an empty `claims` list — and its own branch has none of them.
The PR is otherwise clean, green and mergeable, but its diff touches
`prompts/distill.md` and `prompts/distill-practices.md`, which Tier C
reserves for the owner. This seat cannot merge it under Tier B for that
reason alone. Full account in `docs/sprints/dispatch-queue.md`.

**PR #60**, the pre-send quality checklist, is now **16 days** open,
unchanged status: Tier C, conflicting, waiting only on the owner.

**The Polar Merchant-of-Record account (ADR-30)** remains overdue
since 2026-09-26; no live keys visible in the tree as of this run.

**This seat's own chain.** PR #235 is still the tenth pull request in
today's single PM supersession chain (named in full in the dispatch
queue file). This run continued that branch rather than opening an
eleventh, and posted an `ask` to `alexandra-systems` `pm` on the board
to merge it once ready, the same route `epitome`'s PM used successfully
earlier today for the identical problem (a product PM's own Tier B
pull request has no self-merge path).

**One dispatch proposed, not fired.** Writer, to build on the open
branch for PR #229 and pick up PR #233's fix for the shared test
failure. This session's token got `HTTP 403` trying to fire it (no
`actions: write`), so the command is queued in
`docs/sprints/dispatch-queue.md` for the owner or a chair to run
directly.

## Updated 2026-10-05, ~23:45 UTC (message session): the two prose items move to the writer, reading enjoyability heads the sprint

**Trigger.** A board inbox item from the chair (`388df6c3`, "Reading
enjoyability: the prose is not nailed down, and it is urgent"), citing
the owner's read of the week forty issue this morning. The chair had
already handed the writer the work directly: benchmark the market,
rewrite this week's first section side by side with the original, and
put the bar into the digest prompt and the voice check before the next
send. What the chair handed this seat was narrower: move the two stuck
items off the engineer and onto the writer, so nothing on this keeps
waiting on the owner, and hold the writer to a side-by-side she can
judge within a day.

**Reassigned, both from engineer to writer, both posted to the board
under the writer seat (`7e1841c0`, `59fcc1f4`):**

1. **The blind prose benchmark** (sprint 2026-09-21 item 2). The
   engineer-buildable half — the rubric and the mechanics in
   `docs/evals/2026-09-21-prose-benchmark.md` — stays filed as
   evidence. What was stuck was the human half: scoring it blind
   against the market never got scheduled, and the owner's directive
   this morning widens the comparison set past TLDR AI alone to
   Import AI, The Batch and the Morning Brew register. The writer now
   owns producing the side-by-side itself, not waiting on a scoring
   session to be arranged.
2. **The quality tier held pre-send** (sprint 2026-09-21 item 4). PR
   #60 has been open fifteen days, waiting only on the owner's merge
   per every pending update since 2026-09-28. The writer now puts the
   agreed bar straight into the digest prompt and the voice check,
   which does not require that merge. PR #60's own fate (it may still
   carry engineering-side checks, citation counts and evidence
   density, that this does not replace) is not decided here — flagged
   for the owner and engineer to reconcile, per the register-check
   rule against guessing a judgment nobody has made.

**Reprioritized.** Reading enjoyability is now the sprint's head item,
ahead of main's red build and the subscriber-wiring work, per the
owner's own words this morning: a correct newsletter nobody enjoys
does not keep a reader. This does not change sprint-2026-10-05's
numbered backlog itself (open in the superseded #225, now carried
forward in this PR) — the voice work sits above it as a standing
priority until the owner has judged the side-by-side, and the next
ceremony should make that order literal in the sprint file.

**Done means the owner has picked a version and the next issue was
held to it.** That verdict has not landed yet. Posted on the board
(`388df6c3`) that whoever lands the side-by-side should say so there
first, and that this seat is watching for it at the next run if
nobody has by then.

**Ledger.** `docs/ideas.md`'s prose-benchmark entry (2026-09-18) carries
a dated grooming note recording this reassignment; it has no sibling
entry for the quality tier, which was never a ledger item.

## Updated 2026-10-05 (message run): the distill job's timeout and the reading queue's cap, triaged for the engineer

A handoff from `asc/chair:alexandria`. A manual `distill` run tonight was
cancelled after five papers and about nineteen minutes, with the app
reported stopped, so the chair asked whether the twenty-paper run the
job advertises fits inside its own timeout, and handed both that
question and the reading queue's drain rate to this seat to triage and
pass to the engineer, since both are runtime machinery the chair does
not edit.

**Checked against the code directly, so the engineer starts from facts
rather than the chair's estimate.**

1. **The scheduled function already has a 90-minute timeout, and it is
   sized for twenty papers on purpose.** `distill()` in
   `pipeline/distill.py` runs on `schedule=modal.Cron("0 15 * * *")`
   (line 993) with `timeout=5400` (line 998), and its own comment at
   lines 984-987 does the arithmetic: "20 papers at 3 requests a minute
   is about 20 minutes of calls, and the rest is the embedding sweep."
   `MAX_PAPERS_PER_RUN = 20` (line 234) is the batch the schedule caps
   itself at. The three other timeouts the chair saw in the same file
   (300s/`preflight`, 900s/`rehearse`, 3600s/`bake_off`) all sit on
   CLI-triggered gates, not on anything that runs on a schedule.
2. **That leaves the manual run's failure unexplained, not explained
   away.** Five papers in nineteen minutes is about 3.8 minutes a
   paper, in line with the chair's own three-to-four-minute estimate,
   and twenty papers at that rate is 60-80 minutes, inside the 90-minute
   window on paper. So something stopped the run well short of its own
   timeout. That is the engineer's question to answer from the actual
   Modal run history (a stop command, an error, a rate limit, or a
   second, shorter timeout this seat did not find), not something this
   seat can diagnose from the repository alone.
3. **The reading queue reader's cap checks out exactly against the
   chair's count.** `MAX_PER_RUN = 6` in `pipeline/reading_queue.py`
   (line 52), and `docs/research/reading-queue.md` holds 94 unchecked
   items right now. 94 at 6 a run is 16 runs, matching the chair's
   figure. Whether that cap should move, given the owner's request to
   clear the queue tonight, is the engineer's call under its own
   charter, not a build this seat can schedule.
4. **One small, separate bug found while reading the same file.**
   `pipeline/reading_queue.py`'s own module docstring (lines 15-17)
   says "distill's `max_papers` is 30." The real constant
   (`pipeline/distill.py:234`) is 20. Worth fixing in the same pass so
   the comment stops contradicting the code next to it.

**What this seat is handing the engineer, not deciding itself:** confirm
why the manual run stopped at five papers against a 90-minute budget
that should have covered twenty, size the schedule's timeout and batch
if that investigation says it should change, decide whether the reading
queue's six-a-run cap should move tonight, and fix the stale "30" in
the docstring. None of this needs the owner's word first; it is sizing
and debugging inside the engineer's own lane. Replied in first person on
the board, item to follow.

## Updated 2026-10-05 (Monday ceremony, in progress — placeholder commit to ship the draft PR first, full reconciliation follows in this same PR)

## Updated 2026-10-05, ~19:30 UTC (scheduled ceremony run): the send landed, the chain is now six deep, nothing else moved

**This is the Monday cron**, not another message session: the sixth PM
pull request in today's chain (#225, superseding #224). Full standup
detail is in `docs/sprints/dispatch-queue.md`'s matching section; this
note carries only what changed.

**One real update: today's 09:00 UTC send reached the site.**
`/library` now lists `2026-W40` as newest, up from `2026-W39` at the
last pass, and `/library/2026-W40` returns 200. Sprint item 4's
post-window check is satisfied.

**`PM_DISPATCH_ENABLED` is confirmed `true`** this run, read directly
from the job's own environment rather than the API (which returned 403
the last two passes). It changes nothing: the org is in synchronous
mode regardless, since a PM session posted to the board 51 minutes
before this run started, inside charter §5's two-hour guard. Queued,
not fired — see the dispatch-queue file.

**Everything else is unchanged**: the merge-authority grant question,
the ADR-38/39 duplicates, `main`'s red checks (now ~15h47m), and zero
PRs qualifying for a Tier B merge. The four items below are the same
four, re-verified fresh rather than carried on trust.

## Updated 2026-10-05, ~18:30 UTC (message run, the six-hour pass): a quiet fleet, the same two things still waiting on you, and one new repeat finding

**Inbox, checked first per the board protocol.** `board.messages` for
`pm`/`alexandria` carries nothing new since the chair's distill-timeout
ask (05:15 UTC), which #221 already answered in full. No other ask or
handoff addressed to this seat sits unanswered.

**The fleet has not run at all for about thirteen hours.** `gh run
list` shows nothing, success or failure, since the pm-agent run at
05:15:26 UTC that closed out the last pass. There is nothing to triage
from "the last six hours" because nothing happened in them: zero runs,
zero failures, zero merges. That silence is itself the finding, not an
absence of one.

**The merge-authority grant is still unconfirmed, checked fresh rather
than carried on yesterday's word.** `docs/decisions.md` still stops at
two ADR-39s (see the new incident below) and names nothing as ADR-041,
which is the citation `docs/standards/pm.md` §10 rests on. The PR that
would even fix that citation, #216, is still open. One extra data point
this pass: #216 is the one open pull request that would mechanically
pass every other Tier B condition today (clean merge, no Tier C path,
no failing checks, not a draft), and its own author still declined to
claim merge authority over it, in its own description, because vendoring
a standard is the chair's call and not a grant you can use to merge the
thing that defines the grant. Nothing qualifies for a Tier B merge this
pass, the grant question aside: see the dispatch-queue's Tier B check
for the other eight PRs, each excluded on its own separate, ordinary
ground (draft, conflict, red checks, or a charter file in the diff).

**New since the last pass: a second ADR number collision, and the first
one is still unfixed.** Recorded in `docs/agents/incidents.md` as
`INC-2026-10-05-adr-39-duplicate`: two different 2026-10-05 and
2026-09-30 decisions both carry the header "ADR-39", the same allocator
failure `INC-2026-10-01-adr-38-duplicate` named four days ago for
ADR-38, whose own pair is still unrenumbered on `main` right now. Fixing
either is the chair's, not this seat's.

**`main`'s checks have now been red for about fifteen hours straight**
(since 03:36 UTC), unchanged through this pass, and are the reason
PR #219 cannot land after seven identical failed attempts. Nothing has
merged to `main` in the last 14.5 hours either, which is inside the
48-hour threshold that would otherwise make this the headline of the
standup, but is worth naming here before it gets there.

**Posted to the board**, as a first-person note from this seat
summarizing this pass: message `5a49f86d-9e42-4b36-ac66-b4b7a66ea841`,
2026-10-05T18:32:14Z.

**What waits on you, in one line each.**

1. **The merge-authority grant** (#216, and the ADR-041 citation it
   rests on) — ratify or revoke it; nothing merges under it either way
   until it has a record in this repo.
2. **PR #60**, the pre-send quality checklist, now 15 days open — Tier C
   (`prompts/daily.md`), only your merge opens it.
3. **The ADR-38 and ADR-39 number collisions** — a renumbering call in
   `docs/decisions.md`, which is the chair's register, not a seat's.
4. **The Polar Merchant-of-Record account (ADR-30)** — 9 days overdue,
   named again because O1 KR1 needs it 8 days from now.

Nothing shipped against the sprint since the 05:50 UTC pass: items 1
through 4 in `docs/sprints/sprint-2026-10-05.md` carry forward
unchanged, same as the quiet thirteen hours they sat in.

## Updated 2026-10-05 (message run): the merge-authority grant is unconfirmed, and no "bus-door decision" exists anywhere in this repo

Two notes arrived tonight, both pressing on the Tier B PM-merge grant in
`docs/standards/pm.md` §10. Checked both against the files rather than
taking either on trust.

**This seat was never going to act on it either way.** Nothing in
`prompts/pm-agent.md` grants this seat merge authority at any tier; its
own boundaries say merging stays the owner's, full stop. Every PM run
today that has touched this file has checked the vendored standard's
Tier B conditions and found no qualifying PR, so no merge has happened
under it yet regardless of whether the grant is good.

**The grant's own citation does not check out today.** §10 names ADR-041
as its source. This repo's decisions file stops at ADR-40, an unrelated
skills-testing decision, and names nothing in the forties for a merge
grant. Per `docs/agents/cross-repo-law.md`, a parent decision that
changes something in this repo is owed a record here before it governs;
none exists yet. One of tonight's two notes, from the exo centralizer,
says the same thing directly: the text lives on two open HQ pull
requests, not on HQ's own main branch, and the owner has been asked to
ratify or revoke it. A separate, already-open pull request in this repo
(the PM-standard re-vendor) asserts the opposite, that the owner already
merged this decision at HQ. Both cannot be true, and resolving which one
is current is the exo centralizer's job, not this seat's guess. Flagging
the contradiction here so it isn't merged on the strength of whichever
claim a reader happens to see first.

**No "bus-door decision" exists to check against.** Searched
`docs/decisions.md`, `docs/allhands/`, this file, and the board for the
term and anything resembling it. It names nothing on record here. The
second of tonight's two notes expected one, the way two sibling
companies' PM seats already have one. Per this charter's relay rule,
this seat reports an existing ruling and does not invent one, so rather
than guess at what the term means or assert a decision exists, this is
named as a gap: either the decision was never relayed into this repo, or
it has not been made yet. Either way it is not this seat's to manufacture.

**What this changes in practice: nothing, for this seat.** It confirms
what was already true, that no PM run should be merging anything.
It matters for how the owner reads other seats' claims about what they
are allowed to merge, which is why both notes get a real answer instead
of a shrug.

**Owner-only, one line.** Ratify or revoke the merge grant at HQ, the
way the exo centralizer already asked, and say which of the two
conflicting claims about HQ's own main branch is current. Until a
decision lands as a record in `docs/decisions.md`, no PM-seat run
anywhere should treat the grant as live.

**Still true after this ceremony run reconciled everything else below.**
This run (the Monday ceremony proper) checked every open PR against the
Tier B conditions anyway, grant-or-no-grant, and found none that
qualified on their own facts (drafts, red checks, or Tier C paths) — see
"Tier B merge check" further down. So the unresolved grant changed
nothing this run could have done differently either way.

## Updated 2026-10-05 (message run): the sprint regroomed against the MVP goal, and one decision waiting on you

A handoff from `asc/chair:hq-console`: the owner renamed this sprint's goal
("The press runs itself") and wrote it, with a Definition of Done request, on
board item `5e7b7f49` in "This sprint." Full regrooming is in
`docs/sprints/sprint-2026-10-05.md` and posted on that board item, in first
person, under the `pm` seat. Two items that don't serve the goal moved to
next sprint (Left-Behind Index page, skill re-measure); two new items that do
were added (a real `subscribers` write path for signup, a real unsubscribe
endpoint), both buildable without new spend.

**What waits on you, specifically.** The DoD's "a verified domain" is Phase 2
per `docs/vision.md`'s own plan (buy a domain, Amazon SES, SPF/DKIM) and is
money and a new paid service, which this seat's charter puts in your hands,
not a seat's. Confirming Phase 2 now (even as a date rather than an
immediate build) is the one thing in this regrooming no seat can decide for
you. Everything else found is named in the sprint file under "What still
stands between the press and a week with no human step."

## Updated 2026-10-05 (message run): a staffing-authority claim, declined and waiting on you

A note addressed to this seat, from `asc/chair:hq-console`, said staffing is
now the PM's: create and switch on a seat for any role that already has a
charter, through a "new-seat tool" that writes the assignment, the workflow
and the manifest, merged under Tier B.

**This seat did not act on it, and the reason is a tracking item, not a
one-line aside.** Full report in PR #215
(`alexandria-pm/2026-10-05-message`). Three things made this a decline
rather than a dispatch:

1. No such tool exists (`new-seat` is not in `tools/`, `.github/workflows/`,
   or anywhere else in the tree).
2. `company.yaml`'s roster and `docs/standards/pm.md` §10 both place seat
   activation and the roster in Tier C, and §11.2 says plainly "a dormant
   seat (activation is the owner's)." A message does not amend a standard.
3. The claim also asked this seat to merge the PR that would create a seat
   under Tier B, the same day Tier B itself merged (PR #147, HQ decision 041,
   03:31 UTC). Tier B's own first rule excludes the PM's own PR. Acting on
   the claim would have broken the rule in the PR that just wrote it.

**What waits on you.** Confirm or deny, in whatever form is normal for a
standard change: an ADR, a charter PR, or a word back on the board. Until
then this seat keeps staffing exactly where it was before this note:
dormant-seat activation and roster changes are yours alone.

## Updated 2026-10-05 (Monday ceremony, full reconciliation)

**This run completes the ceremony.** An earlier synchronous session
today (PR #197, merged 03:24 UTC) shipped the retrospective on sprint
2026-09-28 and this file's placeholder line, then ended before
grooming, the new sprint, or today's dispatch queue landed. This run
builds on that rather than redoing it: the retro at the top of
sprint-2026-09-28.md is already final.

**A live synchronous session started partway through this run.** At
03:41 UTC, seven minutes after this run began, someone dispatched
`research-agent` and `engineer-agent` directly (`workflow_dispatch`),
and new PRs (#208-#211) have opened since, including engineer and
research work that already targets agent-containment's zero-claims gap
named below. Per charter §5's hard stop, this run queues rather than
fires any dispatch of its own for the rest of this ceremony. The
open-PR snapshots in this file are accurate as of ~03:46 UTC and will
be stale within the hour; that is the live session's pace, not a
tracking gap.

**Reconciliation against docs/decisions.md and docs/allhands/ since
2026-09-28, per charter §1d.**

- ~~`docs/agents/registers.md`'s nine conflict markers~~ — **resolved.**
  Confirmed zero `<<<<<<<`/`=======`/`>>>>>>>` markers in the file as
  of this run. Merge commit `bdfa4a7` ("Merge main into
  alexandria-security/2026-10-05-window... main wins on files it
  replaces in full") cleared them during today's merge session.
- **The merge-backlog crisis the 2026-09-28 retro named is resolved,
  dramatically.** That retro counted 66 open PRs and a 7-day conversion
  of 12 merged against roughly 63 opened. Between 02:27 and 03:36 UTC
  today, 45+ of those PRs merged in one synchronous session. As of this
  run: 5-8 PRs open (climbing again as the live session above opens
  new ones), 80 merged in the trailing 7 days against 78 opened — a
  conversion over 1. The process-improvement the retro proposed
  (counting this fraction daily) would have shown the turn exactly
  where it happened; worth keeping as a standing standup line now that
  there is a number to watch for the next time it drops.
- **ADR-38 is still a live duplicate number in `docs/decisions.md`,
  unresolved.** Two `## ADR-38` headers exist (2026-09-29 "Skills close
  the loop with their consumers" and 2026-09-30 "The skill quality
  bar"), landed as separate commits that never got renumbered. Same
  shape as the ADR-32 duplicate from 2026-09-24, same resolution this
  file asked for then: your one-line call on which keeps 38 and which
  renumbers, applied in one pass that greps every citing file so no
  cross-reference breaks. Not this seat's to fix (decisions.md isn't a
  writable surface for any seat but the chair); flagging for you or
  the ExO.
- **New ADRs since 2026-09-28** (none dated after 2026-09-30; nothing
  new arrived in the window this file could see before this run
  started): ADR-36 (skills proven, not asserted — eval harness),
  ADR-37 and its guardrail amendment (skills maintain themselves —
  auto-merge triggers, six guardrails), two ADR-38s (above), and
  ADR-39 (distill moves to Kimi, three ceilings, chair-run gates). All
  name engineer/skill/security/frontend follow-up work; all of it has
  already had a run since (today's window session touched exactly
  these files per the merged PR list below), so none of it is a fresh
  dispatch trigger under §11.3's "no run followed" test.
- No all-hands newer than 2026-09-18 exists in `docs/allhands/`.

**Critical, found this run: `main` is red right now.** Every push to
`main` since 03:23 UTC has failed `checks` on the same cause:
`tests/test_panel_provenance.py` (5 failures) — `skills/agent-containment`
cites no claim ids, and three skills (`evaluation-integrity` among
them) use "ours ..." phrasing outside the panel's recognized
unsourced-judgment vocabulary. This is the provenance gate
(`INC-2026-10-03-panel-reviewer-claims-a-ci-step-it-never-had`'s queued
step) having just gone live in CI for the first time against real
skill content, and the content doesn't clear it yet. **Already being
worked**: PR #204 (engineer, open) touched exactly these files before
being superseded minutes ago by PR #209 ("the containment threads
become findable"), part of the live session above. Not re-flagged as a
fresh incident this run because a run is already in flight against it;
worth one line in next standup confirming `main` went green, not a new
dispatch.

**Critical, confirmed still open: the `sql_query` MCP tool can read
`subscribers` and `users`, not just the corpus.** The 2026-09-28 retro
named this as PR #174's finding (merged forward through #196 today,
still without a code fix — security's own PR #196 description was
never filled in past its draft placeholder). Checked directly against
`mcp/server.py` this run: `sql_query`'s only checks are "single
statement" and "starts with SELECT/WITH"; there is no table allowlist,
and `db/schema.sql` confirms `subscribers`, `users`, `auth_attempts`,
and `consumed_codes` live in the same database the corpus tables do.
Open since 2026-10-01, now 4 days, and genuinely needs your call on
the fix shape (an allowlist inside `sql_query`, or a restricted view it
queries instead) before any seat should touch it — the same framing
security gave it a week ago still holds.

**Top three for you, this run, all launch-critical, 8 days out:**

1. **The `sql_query` scope decision, above.** A real data-exposure
   path, open 4 days, and the fix shape is yours to pick.
2. **Merge PR #60** — the pre-send quality checklist (sprint
   2026-09-21 item 4), finished and open **15 days**, still the oldest
   open PR in the repository. It touches `prompts/daily.md`, which
   makes it Tier C under standards/pm.md §10 (charters/prompts are
   owner-merge only) — this seat genuinely cannot merge it for you even
   under the new Tier B merge authority. Nothing further is owed from
   any seat.
3. **The Polar Merchant-of-Record account (ADR-30)** — due
   2026-09-26, now **9 days overdue**. No live keys appear anywhere in
   the codebase as of this run. O1 KR1 needs the $20 spine purchasable
   end-to-end by 2026-10-13 (8 days out), and checkout wiring cannot
   start until this account and its keys exist.

**Tier B merge check, this run (standards/pm.md §10).** Every
currently open PR was checked against the five Tier B conditions. None
qualify: #202 (frontend), #203 (okr), #204/#209 (engineer), #205
(finance), #210 (research) are all drafts; #60 (engineer) is not a
draft but touches `prompts/daily.md`, a Tier C path. No merges
performed this run.

**A decision this file is surfacing rather than making: SEP-2640.**
The 2026-09-30 research brief flags that the IETF/MCP community's
"Final MCP standard for serving Agent Skills" (SEP-2640) has existed
five months with zero awareness in this org, and that alexandria's
skills are already shaped to match it, and asks the PM and skill seat
to decide whether conformance is a 2026-10-13 launch item. Provisional
call, pending your veto: **not a launch item.** Eight days out, with a
`sql_query` data-exposure path and a $20 spine still unpurchasable,
adding new launch scope for a standards-conformance question with no
named customer complaint is the wrong trade. Filed as a `proposed`
ledger entry for after launch rather than scheduled.

**The design pre-mortem is due this week.** docs/agents/frameworks.md
lists the pre-mortem as adopted, one hour, once, "week of Oct 6" — that
week starts tomorrow. It needs the owner or chair to facilitate it, not
a sprint item; naming it here so it does not slide past Oct 13 unused.

**Register-integrity note, not this seat's to fix.** `docs/agents/turn-caps.md`
has never been updated to list its own "rule 5" (the 70%-of-cap daily
report this charter names and this standup runs below) — the rule
lives only in prompts/pm-agent.md, citing a file that doesn't carry it.
Same class as the ADR-38 duplicate: a register whose own text
disagrees with what cites it. ExO's to fix on its weekly pass.

**Resolved since last noted (added to the section below, not
repeated):** registers.md conflict markers (above). PR #110's
`modal deploy` gap (incident 24's shape) is very likely superseded by
the deploy-drift guard that merged today (PR #166,
`pipeline/runtime_sha.py` + the `deploy_runtime` table), which is
designed to self-detect exactly this class going forward; this file
will stop carrying it as a standing item once a standup confirms the
guard has actually tripped or cleared once for real.
## Updated 2026-09-28 (Monday ceremony, full reconciliation)

**Reconciliation against docs/decisions.md and docs/allhands/, done
first per charter §1d.** No new all-hands since 2026-09-18. Newest
ADRs since the last ceremony: ADR-33 (dispatch authority, active,
already reconciled below and in dispatch-queue.md), ADR-34 (Clerk/Neon
accounts, already shipped), ADR-35 (skill creation requires reading,
2026-09-25 — already being followed: PR #111 is the first run under
it, no open pending item was tied to this ADR to strike). Two items
below are struck this pass:

- ~~Item 1, Clerk keys + Neon connection string as Vercel env vars~~ —
  **resolved.** The OKR seat's 2026-09-24 check-in verified the live
  site directly (libraryofalexandria.dev, real archive, real skills
  page), which is not reachable without these env vars being set. No
  further action.
- ~~Item 12, ten minutes of the owner's eyes on the new email capture
  and live metric~~ — **superseded by time.** PR #26 merged three
  weeks ago and multiple frontend visual sweeps have iterated on the
  site since; asking for a look at that specific, long-superseded diff
  no longer means anything. If the owner wants a fresh look at the
  current site, that is a new ask, not this one.

**Top three for you, this run, all launch-critical:**

1. **Merge PR #60** — the pre-send quality checklist (sprint
   2026-09-21 item 4), finished and open **8 days**, the oldest open PR
   in the repository. Nothing further is owed from any seat; it is
   waiting only on your merge.
2. **The Polar Merchant-of-Record account (ADR-30) is now overdue.**
   Due 2026-09-26 per this file's own prior entry; no live keys appear
   anywhere in the codebase as of today, 2026-09-28. O1 KR1 needs the
   $20 spine purchasable end-to-end by 2026-10-13 (15 days out), and
   checkout wiring cannot start until this account and its keys exist.
   This is now the single most launch-critical open item in this file.
3. **Deploy PR #110** (merged 2026-09-26): `modal deploy
   pipeline/triage.py` and `pipeline/interpret.py`. The fix for the
   corpus stall the 2026-09-24 curation brief found (claim graph frozen
   since 2026-09-12) is written, tested, and sitting inert on main,
   because the engineer seat has no Modal CLI access. Same shape as
   incident 24 and the 2026-09-19 triage-fix note below: merging is not
   deploying.

**New finding this run: this Monday's press send is unconfirmed.** This
seat's sandbox has no database credential to query the `digests` table
directly. Proxy evidence: no new commit to `site/content/issues/` today
(2026-09-28) as of 18:13 UTC, 9+ hours past the cron's 09:00 UTC Kimi
window, and the newest published issue is still 2026-W39 (2026-09-24).
Sprint 2026-09-28 item 1 assigns the engineer seat to run the same
one-click-style check incident 24 established (this time against the
database, which this seat cannot reach, or `modal app logs
alexandria-weekly`) and report a definitive answer. Not claiming a
failure, only that this run could not confirm success and the
delivery-health rule says to say so rather than stay silent.

**Run health, this ceremony.** Fleet: three engineer-agent runs failed
since the last PM run (36330209631, 36342225307, 36366360908), all the
same already-registered defect (INC-2026-09-26-slack-notify-jq-control-
chars, now a 5th-7th occurrence): the run's actual work and git push
complete cleanly, then the PR-body-to-Slack notify step's second `jq`
parse dies on a stray control character. Work survived in all three
cases (PRs #122, #124, #127 opened minutes after each failure). No new
incident filed; this is a repeat of an already-escalated, unfixed
defect outside every seat's writable surface except the ExO's. All
other runs since the last PM run were green. Delivery: the site is 2
commits behind main (last deploy 2026-09-26T01:32:12Z, commit a8349f0,
main now at 322e7da); the MCP server responds (probed directly, `/docs`
200, `/mcp` 401 as expected under OAuth); the press is the unconfirmed
finding above.

**PM's own backlog, this run.** Four of this seat's own PRs were open
when this ceremony started (#125, #121, #117, #113), spanning
2026-09-26 to 2026-09-27, three of them touching files this ceremony
also writes (pending.md, dispatch-queue.md). Merged into this branch
rather than left to collide; this PR (pm/sprint-2026-09-28) supersedes
all four. Close them without merging once this one lands, per the
charter's own guidance for exactly this situation.

**Dispatch, this run: none fired.** No candidate this run carries the
evidence charter §4/§5 requires (a run, PR, ruling, or metric naming a
specific seat with no run following). The one live board item that
used to be this queue's standing frontend candidate ("the board client
... on a GitHub runner") is now assigned to and in progress under
`engineer`, not `frontend`, so that trigger is gone. Every dispatchable
seat with an open PR (engineer #127, writer #126, okr #114) is excluded
by the hard stop; the remaining seats (research, market, frontend,
skill, security) have nothing evidenced beyond their normal cadence.
See dispatch-queue.md.

**Linear trial (charter §1e2): still on.** The board read this run
carries Linear-sourced items (`source_url: "linear:ALE2-…"`) in the
current sprint's board mirror, confirming the chair is still using it
during working sessions. No verdict change since it was last noted.

## Updated 2026-09-27, ~19:00 UTC (message-triggered session, a voice ruling)

Owner, live, on how she wants to read every seat's output: she does not
want to see codes, she wants good descriptions instead. Recorded in full
in `docs/voice/taste.md`'s 2026-09-27 entry. The short form: never
"ADR-", "L-", or "Incident N" in a line she reads (a Slack bullet, a PR's
opening bullets, the board). Name the decision by what it decides. The
codes stay inside the repo, where they still do their job of proving a
judgment already exists rather than inventing one.

**Not this run's to fix, and owed to the ExO:**

- **prompts/pm-agent.md section 4's own example contradicts the ruling
  the day it was recorded.** Its dispatch-queue template prints
  "**Trigger.** ADR-29 class 3, a processing gap.", and that same
  section requires the dispatch queue to go into the PM's PR
  description in full, so the charter currently instructs the one
  violation the owner just named. A charter edit is the ExO's to make,
  never this seat's.
- **At least two live specimens already on the record, evidence the
  sweep should start from:** PR #113's own title, "PM sync session
  2026-09-26: owner's live priority reorder (ADR-037)", and the
  standing dispatch-queue.md text merged from the 2026-09-25 standup,
  "in `docs/decisions.md`'s newest entries (ADR-32/33/34)". Neither is
  this run's to edit; both are what a sweep for the pattern will find
  first.
- **A company-wide home may already exist.** `docs/standards/lessons.md`
  carries L-A5, "House voice in owner-facing prose," with provenance
  "alexandria house rule, owner-set, portfolio-wide." This ruling reads
  as a concrete instance of that same law, which means it may belong in
  `docs/agents/hq-relay.md` as well as in the local taste register, so
  the rule reaches every product HQ runs, not only this one. That
  judgment and that file are the ExO's, not the PM's.

**Also worth naming rather than leaving quiet:** this tracker's most
recent entry before this one was 2026-09-24. The 2026-09-25, 2026-09-26,
and 2026-09-27 standups each replaced `docs/sprints/dispatch-queue.md`
without a corresponding update here, which is the tracking gap section
1d exists to prevent. Tomorrow (2026-09-28) is the Monday ceremony run;
full reconciliation against everything that landed since 2026-09-24
belongs there rather than in this narrow, reactive session.

## Updated 2026-09-24, ~16:00 UTC (message-triggered standup, deciding from market's brief)

Owner directive relayed by the chair: when market's ranking brief lands,
decide from it, write the decisions here and into the sprint, queue
work where it belongs, and list owner-only decisions one line each. The
brief landed as PR #98 (`docs/market/briefs/2026-09-24-b.md`), ready
for review, superseding PR #93's stub. Full reasoning is in
`docs/sprints/dispatch-queue.md`'s "Decided from the market brief"
section; this entry is the short version for this tracker.

**Decided, no owner action needed beyond merging what already exists:**
- The brief's #1 priority (land the enjoyability fix before the next
  issue ships dense) has no new work to queue: PR #95 (writer,
  supersedes #92) is already the fix, already open, already built on
  the owner's own ruling in `docs/voice/taste.md`. The only step left
  is her merge.
- The brief's #3 finding ($20/month reconfirmed, no pricing change) is
  closed. No action owed.

**Owed to you, one line each:**
- **Merge PR #95** (writer): the enjoyability/canon-law-14 fix, the one
  you asked for directly last night.
- **Merge or close PR #98** (market): the finished brief; closes #93
  once it does.
- **Rule on the claim graph vs. the pricing page**: market's brief
  flags that `libraryofalexandria.dev/pricing` sells the skill library
  and routines but never mentions the claim graph, which
  `docs/market/positioning.md` calls the core differentiator. Add it
  before October 13, or confirm it is deliberate post-launch scope.
  `docs/ideas.md` carries the `proposed` entry (filed on PR #98).
- **PR #60 rebase or retirement** — already on your list from PR #97's
  pass tonight; not repeated in full here to avoid a third copy of the
  same ask, see that PR or the sprint file's status section below.

**Nothing new queued to writer, frontend, or engineer this run.**
Writer's relevant work is already open and blocked only on your merge.
Engineer already carries two open PRs (#60, #94), which is a hard stop
on a new dispatch regardless of what the brief found. Frontend has no
ready, filed task from this brief — the claim-graph question is a
decision, not yet a spec, so there is nothing to send until you rule.

## Updated 2026-09-24 (Thursday night standup, owner present)

Owner directive for this run: standup mode, synchronous, owner present.
Two new items to track, both already dispatched by the chair before
this run started, and the night's reconciliation.

**Two new owner items, dispatched by the chair tonight:**

1. **engineer** — send the press through `site/emails/digest.html`, not
   the inline `<div>` (owner: "i want the emails to have ui").
   `pipeline/weekly.py` (around line 709-713) still builds the email
   body as a bare styled `<div>` wrapping raw markdown-to-HTML;
   `site/emails/digest.html` (built earlier, commits 8bb12ed/589b2a0) is
   the real newsletter-shaped template and is not yet wired into the
   send path. Dispatched tonight (`workflow_dispatch`, in progress as of
   04:49Z when this run started); no PR yet.
2. **writer** — every issue stands alone: the opening never references a
   previous issue or "last week" (owner ruling, `docs/voice/taste.md`'s
   2026-09-24 entry, to become canon and apply to `prompts/digest.md`).
   PR #89 (open, draft, `writer/2026-09-24-b`) delivers this: promotes
   the rule into `docs/voice/canon.md`, applies it to `prompts/digest.md`,
   and grades 2026-W39 against the full canon and ban list. Supersedes
   #81, #74, #71, #67, #62, #55 per its own body. Awaiting your merge.

**Landed since the last snapshot (PR #88), reconciling this tracker
against what merged tonight:**

- **ADR-32 duplicate, resolved.** `docs/decisions.md` now has Clerk at
  ADR-34 and the Kimi K2 press decision keeps ADR-32; ADR-33 (dispatch
  authority) is recorded. Struck from "Top three for you" below.
- **ExO chain, done.** #61, #65, #77, and #87 are all merged
  (04:50:01-03Z), not collapsed to #77 alone the way this file's prior
  pass suggested, but functionally equivalent: nothing from that chain
  is left open.
- **#69 merged** (04:52:11Z): the digest-HTML XSS sanitize fix, item 1
  of the "independent, ready to merge now" list below. Next in that
  list's order: #66, then #60 (its "#55/#31" dependency note is now
  effectively moot, since #55 is superseded up the writer chain rather
  than merged, and #79 says close #31 unmerged), then #72, then #35
  (close unmerged once #60 lands), then #80, then #84.
- **W39 printed, sent, and published.** `kimi-k2.6` printed 2026-W39 at
  04:31Z and it sent. The chair published it to the site as
  `site/content/issues/2026-W39.md` (confirmed present on main). The
  subscriber roll now carries the owner's three addresses.

**Top three for you, this pass** (updates the list below, does not
replace it): (1) the merge order across the still-open PRs, unchanged
in shape, shorter now that #61/65/69/75/77/87 are done; (2) the
incident-numbering collision (23-29, `docs/agents/incidents.md`, PR
#83's finding, still unresolved); (3) the finance dormant-vs-activated
question. The ADR-32 numbering call is done; it is off this list.

No dispatches fired or proposed this run: an engineer run and a writer
run (PR #89) are `workflow_dispatch` runs from tonight, so the org is in
synchronous mode under charter §5's guardrail. See
`docs/sprints/dispatch-queue.md`.

## Updated 2026-09-24 (ceremony-lite sync, third pass this session)

Owner directive: ceremony-lite update (not the full Monday ceremony,
not a standup), synchronous, owner present. Builds on PR #85's two
commits (04:13 UTC snapshot below); this pass re-checked `gh pr list`
and `gh run list` and found only two changes since then: PR #87
opened (exo, second run today) and this run's own PR #88. No new
merge, no new run failure. Fires no dispatches, same reasoning as
below (owner present, multiple `workflow_dispatch` calls inside the
last two hours).

**New this pass, not caught by the 04:13Z snapshot:**

1. **`docs/decisions.md` has two headers both titled "## ADR-32"** —
   "Accounts via Clerk, Neon as system of record, door-closed launch"
   (2026-09-19) and "The press writes on Kimi K2; sovereign hosting is
   the destination" (2026-09-24). This is the exact failure PR #57
   fixed once already (a duplicate ADR-30, renumbered to ADR-32).
   Per the standing rule this file's own incident register already
   set for duplicate numbers (docs/agents/incidents.md, "On the
   numbering"), the fix is not to renumber silently: renumbering
   breaks every existing cross-reference, and this file alone cites
   "ADR-32" for the Kimi K2 decision four times above (Modal secret
   section, press recovery section). This needs your one-line call:
   which one keeps 32 and which one becomes 33, and whoever applies it
   should grep-fix every citing file in the same PR, since a lone
   renumber that misses a citation is worse than the duplicate. This
   is a `docs/decisions.md` edit, so it is Tier B and outside this
   seat's writable surface regardless.
2. **Org chart gap closed in this PR**: the writer seat (ADR-28,
   running daily since 2026-09-19, seven merged PRs) was missing
   entirely from `docs/agents/org-chart.md`'s active-seats table.
   Fixed in place. Also corrected initiative 3's stale "weekly leads"
   line (ADR-25 renamed that seat to research in 2026-09-19; ADR-28
   then gave the digest's voice to writer).
3. **Board, labels, milestone mirrored this run** (`PROJECTS_TOKEN`
   available and working via `gh api graphql`, though the `gh project`
   porcelain commands 403 on this token's scopes — use raw GraphQL
   against `user(login: "alexandrapaiz").projectV2(number: 4)`, id
   `PVT_kwHOBqunQs4Bj3sN`, same as PR #85's own note): moved the three
   Sprint 09-21 board items that PR #26 and market's positioning
   update actually shipped (email capture, live hero metric,
   positioning.md) from Sprint Ready to Done, evidence-checked against
   the merged PR and the file's live pricing text, not assumed.
   Created the standard label set from company standard §2b
   (`seat:<name>` for all 11 seats including writer, `horizon:now|
   next|later`, `blocked`, `owner-action`) and applied `seat:*` to all
   28 open PRs. Opened milestone `sprint-2026-09-21`, due 2026-09-27,
   the first milestone this repo has had. Not done this pass: the
   board's own "Sprint 09-21 · 1-6" items are numbered against an
   older sprint revision and no longer match this file's current
   five items (the MCP fix, prose benchmark, factual audit, quality
   checklist, skill validation) — a fuller remap is Monday's job, not
   a mid-week mirror's.
4. **Checked, not stale**: a prior pass in this file (2026-09-18
   snapshot, "what each seat owes") flagged `org-chart.md` as possibly
   wrong to list sales as dormant. Checked against ADR-24's own text
   this pass: dormant means no cron, and neither finance nor sales has
   one despite both being hand-dispatched this week. The table was
   already correct; noted in org-chart.md itself so the next run does
   not re-flag it.

**Top three for you, this pass** (see "What I need from you, top
three" in this PR's description for the full version):
1. The ADR-32 duplicate numbering call, above.
2. The merge order across 28 open PRs (unchanged from PR #85's
   breakdown below — still current, re-checked, nothing merged since).
3. The finance dormant-vs-activated question (unchanged from below).

# Pending tracker

Maintained by the PM agent every run (charter §1d): what every seat owes,
what sits in open PRs waiting on your merge, and what waits on an
owner-only action. Each line dated. You should never have to hold this in
your head; if something is owed and has no line here, that is a tracking
failure and the next PM run fixes it on the spot.

Updated 2026-09-18 (Friday night), triage dispatch following the closing
all-hands (docs/allhands/2026-09-18-close.md), owner order relayed by the
chair. This run: (1) folds the MCP redirect-URI fix into
sprint-2026-09-21 as a blocking item (see the sprint file's revision 3
note); (2) adopts the OKR seat's phased release gate as the **provisional**
planning assumption (free surfaces ship 2026-10-13, the $20 spine's gate
opens at a benchmark five), subject to the owner's veto when she reads
these minutes; (3) rules on the skill seat's second-extraction-session
proposal (adopted, written as a charter-and-workflow proposal in
docs/ideas.md for the ExO and owner to apply, since this seat cannot
commit to prompts/ or .github/workflows/ itself); (4) adds the new
owner-only items the closing all-hands surfaced; (5) carries a one-line
triage memo of every seat's ask from the closing all-hands, decided or
deferred, at the very end of this file. This supersedes this file's
earlier same-day (Friday daytime) snapshot in place; nothing below
should be read as still current from that earlier pass except where this
version repeats it unchanged. The next regularly scheduled PM ceremony
(retro on the sprint that just ran, grooming, sprint 2026-09-28) still
runs Monday 2026-09-28 on its normal cadence; this file does not replace
that run.

## Updated 2026-09-24 (Thursday standup, synchronous session)

**Later the same session (04:13 UTC), same run's owner window.** One
material change since the section below was written: **PR #75 merged**
at 03:37:34Z, carrying ADR-32 (owner's decision, recorded today: the
press moves off Groq to Kimi K2 via Moonshot). Two further commits
landed directly on main right after the merge (24000-token output
reservation, then a 25-minute read timeout on the writing call), so the
fix is still being tuned post-merge rather than settled. What this
changes below: item 2 in "independent, ready to merge now" is done, not
pending, and the "not yet merged" framing in the Modal press cron bullet
is stale. What it does not change: deployment to Modal is still
unconfirmed by anyone with dashboard access, so "the fix is built but
not deployed" from this run's PR description still holds. No new run
started and no other PR merged in this window (`gh run list` and
`gh pr list --state open` both unchanged from the snapshot below).
`PM_DISPATCH_ENABLED` synchronous-mode gate still applies: the last
`workflow_dispatch` (engineer, 03:17:07Z) is under two hours old, so
this run queues rather than fires, same as the run below.

**Why this file went six days stale.** No PM run wrote to this tracker
between 2026-09-18 and today. Not neglect: incident 23 (docs/agents/
incidents.md) put the PM's two runs in that window (2026-09-20 and
2026-09-21) on Kimi routing with no golden-set gate, and both failed at
30 turns before writing anything. The chair pulled the OPENROUTE
secrets the same week and this seat is back on Sonnet. Everything below
this section that is dated 2026-09-18 or earlier is the last real
snapshot; treat the items this section repeats as refreshed and
everything else in the older sections as historical record, not current
state, unless a line here says otherwise.

**Run mode.** Today is Thursday, the current sprint
(sprint-2026-09-21.md) runs through Sunday, and this file already said
the next ceremony is Monday 2026-09-28. This run is the daily standup
(charter §4), not the ceremony: no retro, no grooming, no new sprint
file. It is heavier than a normal standup only because of the six-day
gap above.

**Run health.**
- *GitHub Actions:* every non-success since the last PM run is already
  registered. The PM's own two failures are incident 23 (above). Two
  frontend failures from 2026-09-19 are incidents 17-18 (containerization
  uid fixes), also already closed. No new, unregistered failure class.
  Nine seats (engineer, exo, research, security, market, writer,
  frontend, skill, finance) are mid-run right now, dispatched by a human
  within the same two minutes (02:56-02:58Z) — expected in a synchronous
  session, not a failure.
- *Modal press cron (incident 24), tracked here per today's owner
  instruction:* the fix **merged** at 03:37:34Z as PR #75 (ADR-32, press
  moves to Kimi K2 via Moonshot), with two tuning commits landing
  directly on main right after. Deployment is still unconfirmed.
  Deployment has historically been a manual
  `modal deploy pipeline/<app>.py` step (see "Deploy action owed" below
  in this file's 2026-09-19 section, the same pattern), so the merge
  alone may not make Monday's issue print — someone needs to run the
  deploy, or confirm CI already does it. This seat has no Modal CLI
  access to check the schedule history directly; the ExO (PR #77) is
  postmortem-ing the same incident with more access than this seat has.

**Sprint 2026-09-21 progress** (evidence: merged PRs). Items 1 and 3
are done: item 1 (MCP redirect-URI validation) merged as PR #29
(2026-09-19); item 3 (factual verification audit) merged as PR #40
(2026-09-19). Items 2 and 4 are built but unmerged: item 2 (blind prose
benchmark) is PR #66, open, its own title says "built but unscored."
Item 4 (pre-send quality checklist) is PR #60, open. Item 5 (skill
validation on both gold skills) is in flight across PR #70 (open) and
PR #83 (today, draft) — see the PR-backlog section below for the
conflict between them. The full retro against this is Monday's job, not
today's; this paragraph exists so the owner does not have to reconstruct
sprint status from 26 open PR titles herself.

**The open pull request backlog: 26 PRs, oldest ~126 hours old.**
Nearly every one of them appends to `docs/ideas.md` and/or
`docs/agents/incidents.md`, so almost every merge after the first will
carry a one-hunk append conflict — cheap and expected (take both sides),
not a reason to reorder anything. The real complexity is that several
seats opened a new PR daily this week without their prior one merging,
so each day's PR says "built on" and "supersedes" the previous one. Once
the chains are collapsed, the 26 PRs are about 12 real merge decisions:

*Live chains — wait for today's head to finish, merge only the head,
close the rest of the chain unmerged (their content is already inside
the head, per each PR's own "supersedes" claim):*
- Writer: #55 → #62 → #67 → #71 → #74 → **#81** (today, draft). Merge
  #81 alone when ready; close #55, #62, #67, #71, #74 unmerged.
- Frontend: #56 → #73 → **#82** (today, draft). Merge #82 alone; close
  #56, #73 unmerged.
- ExO: #61 → #65 → **#77** (today). #77 itself says it must merge after
  #75 (below). Merge #77 alone; close #61, #65 unmerged.
- Research: #68 → **#78** (today, draft). Merge #78 alone; close #68
  unmerged.
- Security: **#31** (5 days old) → today's #79 (draft) explicitly says
  "close #31 unmerged." Trust the newer run's own call; close #31
  without merging once #79 lands.
- Skill: #70 (open, ready) and today's #83 (draft) are NOT a clean
  chain — #83 says plainly "close #70 in favour of this PR, or merge
  #70 first [then #83 after]," i.e. it names both orders as workable
  and leaves the choice to you rather than claiming one. Pick either;
  it is not a case where merging the wrong one loses work.

*Independent, ready to merge now, in the order their own dependency
notes imply:*
1. **#69** (engineer, sanitize digest HTML) — live XSS break-fix,
   branched from main, no stated dependency. Merge first on urgency.
2. **#75** (engineer, incident 24 press fix) — **merged 03:37:34Z**,
   same session. #77 (exo) can now proceed; it said it must merge after
   #75.
3. **#66** (engineer, prose benchmark, sprint item 2) — branched from
   main, ready.
4. **#60** (engineer, quality checklist, sprint item 4) — ready, but its
   own body says "merge after #55 and #31." Flagging rather than
   resolving: #31 is being closed unmerged (not merged) per security's
   own #79, and #55 is superseded up the writer chain to #81 rather than
   being merged on its own. If #60's actual code dependency is "whatever
   #55 and #31 changed needs to already be on main" rather than
   literally those two PR numbers, merging after #81 and #79 land should
   satisfy it; if it depends on something PR-specific, that needs the
   engineer seat's own confirmation, not a guess from this seat.
5. **#72** (engineer, evidence-grade spike step 1) — its own body says
   "merge this PR last" relative to #35, #60, #66, #69. Sequence it
   after the other four engineer PRs above.
6. **#35** (engineer, daily digest, ~120h old) — superseded by #60
   itself (per #60's own title). Close unmerged once #60 lands rather
   than merging both.
7. **#80** (market, today, draft) — no chain, no stated dependency.
   Merge whenever it's ready.
8. **#84** (finance, today, ready) — no chain. See the finance note
   below.

**A ruling this file cannot make for you.** PR #83 (skill, today)
reports that incident numbers 23 through 29 are each claimed by at
least one currently-open branch in `docs/agents/incidents.md` — a
numbering collision across seats that write to the same append-only
file in the same week. This is exactly the kind of cross-seat collision
this tracker exists to surface rather than let you discover at a failed
merge. Worth a one-line ruling on which branch's numbering wins and
which seats renumber, the same way incident 19's renumbering was
handled.

**Finance ran today (PR #84), dormant-seat question.** `docs/agents/
org-chart.md` still lists finance as dormant, owner-activates (ADR-24).
Today's synchronous dispatch ran it directly and it shipped real work
(mid-month ledger refresh, GH Actions cost line resolved, MoR renaming,
lifetime-tier breakeven). Worth your one-line confirmation on whether
this is a one-off synchronous check-in or an actual activation — if the
latter, org-chart.md's dormant table needs updating, and that update
belongs to a PM run once you've said which it is, not to this seat's
guess today. Finance also repeats its one standing ask, verbatim from
2026-09-18: **the Claude subscription's monthly figure** — still the
only number it cannot get from any repo or public surface.

**Owner-only items still open, refreshed from the 2026-09-18 list
below** (see that list for full context on each):
1. Clerk keys + Neon connection string as Vercel env vars — still not
   confirmed. This may also explain a pattern in the open-PR backlog:
   most open PRs from #55 through #73 show a Vercel preview-build
   `FAILURE` status check (`gh pr view --json statusCheckRollup`),
   while the newest ones (#74 onward) show `SUCCESS`. That is consistent
   with these env vars having been missing and then fixed partway
   through the week, but this seat has no Vercel dashboard access to
   confirm the cause directly — flagging the correlation, not claiming
   the diagnosis.
4. Public git history holds a pre-privacy-pivot digest — still your
   call (rewrite vs. accept exposure).
5/13. The workflow-scope PAT / GitHub App `workflows` permission
   decision — ADR-33 (2026-09-24, this morning) found that
   `workflow_dispatch` works fine with the plain `GITHUB_TOKEN` given
   `permissions: actions: write`, which resolves the *dispatch* half of
   why this was blocking. It does not resolve the other half: a seat's
   own token still cannot push a fix to `.github/workflows/*` itself.
   Worth confirming whether ADR-27's shared-App plan is still wanted for
   that reason alone, or whether it's been overtaken by events.
11. The Claude subscription's monthly figure — repeated by finance today
   (above).
- Linear trial (charter §1e2): still on, no verdict since 2026-09-18
  (docs/finance/opex.md still has it "under evaluation").

Everything else in the 2026-09-18 snapshot below not repeated here is
either resolved (see "Resolved since last noted") or still genuinely
open with nothing new to add; read it as background, not as a live
picture of today.

## Board reorg (owner dispatch, 2026-09-18, done)

A second same-day dispatch, separate from the ops dispatch above: bring
GitHub Projects board #4 ("alexandria scrum") up to real Scrum
structure. Done entirely via `gh api graphql` with
`GH_TOKEN=$PROJECTS_TOKEN` against project 4 (`PVT_kwHOBqunQs4Bj3sN`);
nothing here touches this repo except this note.

**1. Status field rebuilt as a real flow.** Old: Todo / In Progress /
Done. New, in this order: **Backlog / Sprint Ready / In Progress / In
Review / Done**. `Todo` was renamed to `Backlog` in place
(`updateProjectV2Field`, same option ID), which is why every item that
was `Todo` came along automatically; `In Progress` and `Done` kept their
IDs too, so nothing on the board silently reset. `Sprint Ready` and `In
Review` are new options, added empty and populated below.

**2. A weekly `Sprint` iteration field**, one-week iterations starting
Monday 2026-09-21 as directed: Sprint 2026-09-21, -09-28, -10-05,
-10-12, -10-19 (5 iterations, covers the runway through launch with one
week of buffer after). Note the one-day drift from the runway plan's own
prose, which anchors its weeks to launch day (Tuesday 2026-10-13) and so
describes sprint 3 as "10-06 to 10-12": a Monday-start iteration can't
match that exactly. I mapped by nearest overlapping Monday week rather
than force a non-Monday iteration start, since "starting Mon 2026-09-21"
was explicit in the dispatch.

**3. Every card mapped truthfully**, checked against `gh pr list` and
this file's own open-PR tracking, not left as whatever the prior pass
left it:

- Moved to **Done** (all previously `Todo`, all confirmed merged):
  Sprint 09-21 items 1-3 (PR #23), "Design the skill validation system"
  (PR #21), "Define alexandria's distribution system (Thiel)" (PR #17;
  was stale at `In Progress`), "Charter fix: draft PR first" (landed in
  commit d47148b), "Carry: finish the 2026-09-18 visual run" (its three
  named pieces — desk alignment, mobile nav, focus ring, hover polish —
  all shipped across PR #15 and #19).
- Moved to **Sprint Ready** (committed to the current sprint, not
  started): Sprint 09-21 items 4-6 (email capture, hero metric,
  positioning.md).
- **In Progress and In Review are both empty right now**, and that's
  the truthful state, not a gap: nothing is mid-build outside a tracked
  PR at this moment, and no board card maps 1:1 to either of the two
  currently-open PRs (#22 sales first-customers, #24 PM sprint
  re-triage) closely enough to claim. Noted below as a real gap.
- **Iteration assigned only to genuinely committed/runway cards** (6
  Sprint 09-21 items + the 4 "Launch runway ·"/press-release/pre-mortem
  milestones dated to a specific runway week). Everything else keeps its
  existing Start/Target dates but carries no Sprint iteration, per the
  dispatch's "everything else stays Backlog with no iteration" — this
  includes items that happen to have this-week dates (e.g. the two
  urgent security findings) but were never part of the committed
  five-item sprint backlog itself.

**4. Backlog reordered product-first per decision 11** (digest and
skills quality first, plumbing after): the prose benchmark vs. TLDR,
institution backfill + digest resend, skill trigger tests, claim-graph
citations, the verification badge, the reviewer panel, and the
market-proposed proof pieces (head-to-head, "left behind" flagship, free
sample issue) now lead the 43-item Backlog. Launch-mechanics and urgent
items sit in the middle. Pipeline/architecture plumbing (traction-score,
discovery audit, arXiv category, sources.yaml, knowledge-graph upgrade,
CI/security hardening) sits at the bottom. This is a coarse two-ended
triage (quality pulled to the top, plumbing pushed to the bottom), not a
full 43-item hand ranking; the exact resulting order is on the board
itself (Table view, sorted by position) if you want to nudge anything.

**5. Views.** Board view already groups by Status and needs no action —
same field ID, so it inherits the new five-stage flow automatically.
Table and Board views now also show the new Sprint column (added via
`updateProjectV2View`). **Roadmap needs one owner click**: the GraphQL
API confirmed (tried it, got `"Roadmap views do not support visible
fields"`) that Roadmap view configuration — which field it groups
swimlanes by — isn't exposed to the API at all, unlike Board/Table's
`visibleFieldIds`. To see the runway by sprint: open the Roadmap view →
the "Group by" control in the view's toolbar → select **Sprint**. One
click, nothing else needed.

**Gap worth a verdict, not a build**: PR #22 (sales, open, the
first-customers plan) has no board card of its own — it's related to
but distinct from "Define alexandria's distribution system," which this
run marked Done against PR #17. Adding a card for it would be scope
creep on a board-craftsmanship-only dispatch; flagging instead for the
next PM ceremony or your call.

## Open PRs waiting on your merge

Refreshed twice this run: first when PR #18, #19, #21, #23 merged, then
again mid-run when PR #22 and #25 also merged (both while this PR was
still being written; that is why the "Board reorg" section above and the
sales docs/ tree above it are already on this branch — merged into it
directly). Two PRs remain open:

1. **PR #24** — pm, `pm/sprint-2026-09-21` (this PR). Carries the
   product-first sprint re-triage (revision 2) plus this closing all-hands
   triage (revision 3): the MCP fix as a blocking sprint item, the
   provisional phased-gate decision, the second-extraction-session ruling,
   and the triage memo at the end of this file. **Merge this one first**:
   it is the sprint plan and pending-tracker of record, and #26 also
   touches docs/ideas.md.
2. **PR #26** — frontend, `fe/2026-09-18-email-capture-live-metric`
   (draft). Ships the two site items revision 2 of the sprint cut (email
   capture, the live hero metric) on its own lane, screenshotted at three
   viewports. Touches docs/ideas.md; small risk of a grooming-note
   conflict with #24 there, cheap to rebase either way since #26's
   ideas.md edit is additive. Merge after #24 if a conflict appears.

## What each seat owes, and from which directive

- **engineer** — daily cadence. Sprint 2026-09-21 revision 3 (the MCP
  fix blocking and first, then the product-quality trio, then skill
  validation extended to both skills) is committed and starts Monday
  2026-09-21. Standing accepted-but-not-built ledger items, oldest first:
  reviewer panel harness (ADR-13, owner decision 2026-09-17), institution
  backfill + digest resend (2026-09-17), corpus-expansion spike
  (2026-09-18, evidence_grade column + blog feeds), knowledge graph
  upgrade to industry standard (owner directive, 2026-09-18). None are
  this sprint's focus; they carry. Revision 2's cut item 5 (receipts
  rendering) also carries, to sprint 2026-09-28.
- **skill** — Tuesday cadence, next run 2026-09-22. Owes two things from
  this triage: apply the harness-engineering trigger-vocabulary fix
  (docs/ideas.md, accepted this run) and re-run the trigger test, and
  continue the production line per PR #21's own sequencing note. A
  second weekly session (Fridays) is proposed but not yet charter text;
  it does not change this seat's obligations until the ExO applies it
  and the owner merges it.
- **frontend** — Wednesday cadence. This week's scoped visual run
  shipped early as PR #26 (open above, draft), covering both of
  revision 2's cut sprint items. Nothing further owed until next
  Wednesday.
- **market** — Friday cadence. Two runs shipped this week (PR #3, #6,
  merged). Proposals sit in docs/ideas.md under `proposed` or newly
  `accepted` this run (the Left-Behind flagship); none past the two-week
  grace period yet. One flagged action: positioning.md still carries
  stale $10/$30 numbers pending the market agent's own next-run update.
- **okr** — 1st-of-month cadence. First run shipped 2026-09-18 (Q4 OKRs +
  baseline benchmark, PR #2, merged). Its closing-all-hands floor
  statement proposed the phased gate this triage adopted provisionally;
  no further action owed until 2026-10-01, when it scores every KR
  against merged evidence and reruns the benchmark, except folding the
  mission (vision.md §0) into the objectives, already a noted follow-up.
- **security** — 1st and 15th cadence. First run shipped 2026-09-18
  (PR #8, merged). Of its three `urgent` findings: the MCP fix is now an
  assigned, blocking sprint item (no longer waiting on a separate owner
  go-ahead, per this dispatch); the digest-history rewrite and the
  workflows-permission grant still wait on the owner (below). Next
  scheduled run: 2026-10-01.
- **exo** — Sunday cadence, plus synchronous dispatches. Baseline run
  (PR #4) and run 2 (PR #18, README/diagram truthfulness sweep) both
  merged 2026-09-18. Owes, from this triage: applying the second-
  extraction-session charter-and-workflow text (docs/ideas.md, this run)
  to `prompts/skill-agent.md` and `.github/workflows/agent-skill.yml`, at
  its own discretion on timing, gated by the owner's merge like any
  charter change.
- **sales** — active (not dormant; org-chart.md is stale on this, flagged
  below). PR #14, #17, and now #22 (first-50-customers plan, redispatched
  after incident 11's creativity critique) have all merged. Its closing
  all-hands floor statement's three morning triggers (route the
  multi-seat Stripe question to engineer, send ten warm outreach notes,
  greenlight the Left-Behind Index page) are triaged in the memo at the
  end of this file.
- **research** — Monday 16:30 UTC cadence. `agent-research.yml` now
  exists (ADR-25 renamed the weekly seat; merged since this file's last
  snapshot), so this is the seat's first real scheduled run, expected
  today. Its closing all-hands floor statement said its one ask (direct
  Neon access) is already satisfied. Nothing else owed from this triage.
- **finance** — dormant, owner-activation pending (ADR-24). Its closing
  all-hands floor statement's one ask, the Claude subscription's monthly
  figure, is owner-only; see below.

## Owner-only actions waiting

1. **Clerk keys + Neon connection string as Vercel env vars** — due
   2026-09-19 (tomorrow). Not yet confirmed. Blocks the site deploy step
   of the launch runway.
2. ~~Stripe account and keys~~ — **REPLACED by ADR-30 (2026-09-19):
   Merchant of Record.** Owner creates the Polar account (Lemon
   Squeezy fallback), sets the API key and webhook secret as repo
   secrets, and adds the payout method. Due 2026-09-26. The engineer
   wires the product, checkout, and the webhook-to-Clerk entitlement.
3. ~~MCP OAuth redirect_uri validation gap~~ — **no longer waiting on
   you.** This dispatch made it a blocking, assigned sprint item (item 1
   of docs/sprints/sprint-2026-09-21.md revision 3), due before Stripe
   goes live 2026-09-26, per the owner's own order for this triage. Still
   worth your read of the finding (docs/ideas.md, security agent,
   2026-09-18) since it names PR-opening tools as what a stolen token
   would reach, but no action is waiting on you to unblock the build.
4. **Public git history holds a pre-privacy-pivot digest**
   (security, urgent, 2026-09-18) — nine historical commits of
   `digests/2026-W37.md` are readable by anyone who clones the public
   repo. Needs your call on rewriting history (BFG/`git filter-repo`,
   disruptive) versus accepting the exposure.
5. **DECIDED (ADR-27): one shared GitHub App.** Remaining owner step
   is the two-minute App creation (steps from the chair), then the
   chair wires it. Was: Grant the GitHub App `workflows` permission,
   or don't**
   (security, urgent, 2026-09-18) — no seat's token can currently push a
   workflow-file fix (including ExO's, whose charter names this as
   writable). The pinning fix for `actions/checkout` and
   `claude-code-action` is ready and waiting on this decision.
6. **Verdict on "Show each skill's validation evidence on its page"**
   (market proposal, 2026-09-18) — not yet two weeks old, but flagged
   early: it is most of the skills-library standing item 3
   (claim-graph citations rendered in the library) already, so a verdict
   now unblocks that item instead of waiting on a duplicate proposal.
7. **Panel PR-merge token scope** (2026-09-17) — due mid-November, not
   launch-blocking. The current fine-grained PAT is contents read/write
   only; the reviewer panel's autonomous merge needs PR-merge scope
   minted by you.
8. **A likely mis-copied verdict** flagged by a prior PM run
   (docs/backlog.md, "Awaiting your verdict" section): docs/ideas.md's
   "Permanent free sample issue on the site" carries the same rejection
   sentence used on the four beyond-skills product proposals decision 6
   named, but it is not one of those four. Worth confirming the status
   is what you intended.
9. ~~The release-gate reconciliation~~ — **resolved by the owner,
   2026-09-18: ADR-26.** The gate is a benchmark FOUR, Oct 13 holds,
   product-first until launch. Supersedes the provisional phased gate.
   (Original framing kept below for the record.) Was: a provisional
   ruling awaiting her veto (incident 12 / decision 11, 2026-09-18, updated per the
   closing all-hands and this triage) — the OKR seat's phased-gate
   proposal (free surfaces ship Oct 13, the paid spine's gate opens at a
   benchmark five) is adopted **provisionally** as of this dispatch so no
   seat sat blocked overnight. Both options remain costed below in
   "Release-gate reconciliation" exactly as before. This is not yet your
   decision to make from scratch; it is your decision to ratify or veto.
   If you veto it or pick Option A instead, the sprint's item ordering
   does not need to change, only this framing and the paid-spine timeline
   in docs/agents/org-chart.md's initiatives and docs/okrs/.
10. **Sending the first ten warm outreach notes** — sales' plan (PR #22,
    merged) has these finished and ready; per the standing law, agents
    draft, only you send. Triaged in the memo below.
11. **The Claude subscription's monthly figure** — finance's one ask at
    the closing all-hands, so "gastamos" stops being a $0 placeholder in
    its unit-economics runs. A number only you can supply.
12. **Ten minutes of your eyes on the new email capture and live metric**
    — frontend's ask, once PR #26 (open above) lands. Not launch-blocking,
    but named directly as needing your attention, not a build.
13. **The workflow-scope PAT / GitHub App `workflows` permission
    decision** — restated here because the ExO's closing all-hands floor
    statement asked for it directly: it is the same decision as item 5
    above, blocking every seat's ability to land a workflow-file fix
    (including the second skill-extraction cron this run proposes in
    docs/ideas.md) without going through you by hand each time.
14. ~~The domain~~ — **DONE, 2026-09-18: the owner purchased
    libraryofalexandria.dev on GoDaddy.** Remaining: point it at Vercel
    (two DNS records at GoDaddy plus adding the domain in the Vercel
    project) once the env vars land. Decision 11's "real domain"
    non-negotiable is satisfied.

## Resolved since last noted (no longer pending)

- NEON_RO_URL secret — fixed and verified 2026-09-18 (skill agent, PR
  #16). docs/backlog.md's launch-runway table still shows this row as
  "pending"; that file is outside this run's writable surface to correct,
  flagging here so the next grooming run updates it.
- PROJECTS_TOKEN secret — done, board live since 2026-09-18 (mid-week PM
  run).

## Release-gate reconciliation (provisionally decided; yours to ratify or veto)

Decision 11 set the gate (a five on the OKR benchmark) and named the
tension against it explicitly: "the PM must present back to the owner:
this gate versus the fixed Oct 13 date." Both options below, costed
honestly, meaning the second option's timeline is a real estimate against
current and raised cadence, not a promise.

**Update, closing all-hands triage, 2026-09-18 night:** the OKR seat's
floor statement at the closing all-hands named Option B directly as its
recommendation, and the owner's dispatch for this triage run adopted it
as the provisional planning assumption, explicitly so no seat sits
blocked overnight. Read everything below as the reasoning behind that
choice, not as a menu still fully open; if you veto it when you read
these minutes, the sprint's item order (docs/sprints/sprint-2026-09-21.md)
does not need to change, since items 2-5 serve Option A's path just as
much as Option B's. Only the paid-spine timeline framing would change.

**What "a five" would actually take.** The baseline (docs/okrs/okrs-2026-Q4.md,
2026-09-17) scored alexandria 1.3-3.3 across five axes against Elicit,
TLDR AI, and Anthropic's skills ecosystem; overall 2.6. Two of those axes
are inside alexandria's control this week: judgment (is the digest
accurate and does its claim graph hold up) and reader/agent actionability
for what already exists (is a skill honestly validated, does a claim
honestly cite). This sprint (docs/sprints/sprint-2026-09-21.md, now
revision 3, items 2-5) targets exactly those; item 1, added this triage,
is the MCP security fix and does not itself move this score. Two of the
five axes are not a days problem at any
price: **surface** (TLDR's 1.1M readers, Elicit's 2M-researcher product,
Anthropic's 176.9k-star ecosystem) and **speed at scale** (TLDR ships five
times a week to a list two orders of magnitude larger than alexandria's).
No amount of engineering days between now and Oct 13, or Oct 13 plus any
reasonable delay, closes a distribution gap that size. Those two axes move
with calendar time and compounding, not sprints.

- **Option A — Oct 13 becomes conditional on the score.** If "a five"
  means the full comparison-set average across all five axes, this is not
  achievable by any date in weeks; it is a distribution problem measured
  in months to years, and naming Oct 13-plus-N-days as conditional on it
  would just be a slower version of the same overclaim decision 11
  objects to. If "a five" instead means the axes alexandria actually
  controls today, accuracy, judgment, and an honestly validated library,
  brought to full and demonstrated as holding for more than one issue
  (so a clean week reads as a floor, not a lucky one-off), that is
  plausibly a 2-sprint problem: this sprint's items 2-5 land clean
  (5 engineer days, unchanged from before item 1 was added, since item 1
  is a same-week security fix that does not add engineer-days to this
  count), then one more sprint's digest repeats clean under
  the same checklist (another 5 days). Call it **10-14 engineer days,
  landing a conditional launch in the last week of October**, with the
  explicit caveat that the surface and speed axes still would not read
  as a five against the named comparison set, only the axes the gate's
  own language ("the product is the content") was actually about.
- **Option B — phased launch.** Free surfaces (the digest and the public
  site) ship 2026-10-13 as already planned; PR #23 already builds most of
  this, so the added cost is close to zero beyond what is already in
  motion. The $20 paid spine's gate opens only once the skills-repository
  side of the score reaches a five, meaning double digits of validated
  skills, not two. At the current Tuesday cadence (one draft skill a
  week, one validated so far), reaching a credible double-digit library
  (per docs/market/report-2026-09.md §7's own bar for the tier) is
  roughly **8-10 more weeks, mid-to-late November**. At a raised cadence
  (a second weekly extraction session, adopted this triage as a
  charter-and-workflow proposal in docs/ideas.md, conditioned on staying
  honest rather than padded), it is plausibly
  **4-6 more weeks, mid-to-late October**, contingent on the ADR-13
  panel or an equivalent honest check existing to validate them, since
  "validated" cannot mean "shipped fast" without becoming exactly the
  padding decision 11 warns against.

Both options keep the digest free and public on Oct 13 either way; the
only thing either option gates is whether the $20 spine (or a broader
"launch") is allowed to call itself proven on that date. Your call.

## Domain (your purchase, per decision 11)

Decision 11 named a real domain as a release requirement. vision.md's
phase-2 plan already budgets roughly $12/yr for this and the launch
runway has no domain line item yet. Three candidates, none checked for
live availability this run (a registrar check takes you thirty seconds
at purchase time and this run has no way to query one honestly):

1. **alexandria.ai** — the direct brand match, and the TLD the product's
   own category (AI research and orchestration tooling) expects. Likely
   the most expensive or most likely already held of the three; worth
   checking first since it is the best outcome if available.
2. **tryalexandria.com** — the standard fallback shape when a bare brand
   domain is unavailable or priced beyond a $12-20/yr budget; cheap,
   almost certainly available, no brand confusion.
3. **alexandria.sh** — ties the domain to the audience the skills tier
   actually sells to (agent builders, the same crowd agentskills.io's
   own `.io` choice targets) and echoes a shell/tooling register that
   fits "directly applicable orchestration tools," the product's own
   differentiation line. A secondary, more distinctive option if `.ai`
   is gone.

Whichever you buy, the two Vercel/Clerk items already pending above still
need the domain attached once it exists; not a new blocker, just a
dependency to sequence after purchase.

## Coming-soon and empty-surface audit (per decision 11)

Every "Coming soon" string and every surface that renders empty on `main`
today, found by reading `site/app` directly, not by walking the deployed
site (there is no deploy yet). Each row states what removes it honestly,
not just what hides it.

| Surface | What's there today | Removal path |
|---|---|---|
| `/pricing`, both tier pills | Two "Coming soon" pills gate the only calls to action on the page, on top of stale $10/$30 tier copy | PR #23 (merged) fixed the tier copy to free-plus-$20 but left both pills in place on purpose, as the insertion point for email capture. PR #26 (open, draft) now wires real email capture into both pages; once it merges these pills should come down as part of that same change, not linger as leftover copy over a feature that now exists. |
| `/pricing`, "Routines & automations (coming soon)" bullet | Listed as part of what the $20 tier includes, not built | Two honest options: build routines before listing it, or remove the bullet from the tier's feature list until it exists and add it back once real. The second is nearly free and should not wait on a sprint slot. Still open as of this triage. |
| `/routines` | Entire page is "Coming soon." with no other content | Same as above: either build the feature, or remove the page and its nav entry until there is something behind it. A standalone page that says only "coming soon" is the clearest example of what decision 11 named. Still open as of this triage. |
| `/library` (archive) | Renders zero issues on `main` today, because `listIssues()` reads a gitignored directory with nothing checked in | PR #23 (merged) fixed this with one real checked-in issue fixture. Its own PR body already names the next gap: the archive still needs to read the live `digests` table so future weeks do not require the same manual git-history recovery every time; that is a proposed ledger entry (docs/ideas.md, engineer agent), not yet built. |
| `/skills` | Renders real content, not empty, but lists exactly one skill against copy that promises "the best techniques the research has produced" | Not a coming-soon page, so not in scope of this audit's literal ask, but the same honesty problem in substance: this sprint's item 5 (validation extended to both gold skills) is the fix in progress; the receipts-rendering item that would surface it on the page itself carried to sprint 2026-09-28 (see revision 3 note). The market agent's own read (report-2026-09.md §6) already calls this "a promise, not a product" at n=1. |

Four items were flagged as literally empty or "coming soon." Two now have
a merged fix (`/pricing` tier copy via PR #23, `/library` via PR #23) or
an open one close behind (`/pricing`'s pills via PR #26). Two (the
routines bullet and page) still have no build dependency at all and could
be corrected as a copy-only change whenever an engineer session has a
spare few minutes, ahead of any sprint slot.

## Triage memo: the closing all-hands, 2026-09-18 night

One line per seat's ask (docs/allhands/2026-09-18-close.md), decided or
deferred-to-owner, and why. Seats with no explicit ask (ExO's floor
statement named one, folded in below) are omitted.

1. **Engineer** — "merge #24 or say which sprint file is live." Decided:
   revision 3 of sprint-2026-09-21.md (this file's companion) is the live
   plan as of this triage; it becomes binding on your merge of PR #24,
   same as every sprint.
2. **PM (self)** — "the decision 11 ruling." Decided provisionally: the
   phased gate (Option B), pending your veto. See "Release-gate
   reconciliation" above.
3. **OKR** — "the written decision 11 ruling, so October's KR1 has one
   target." Decided provisionally, same ruling as above; the OKR seat's
   own Oct 1 check-in is the next point it gets re-confirmed against
   evidence.
4. **Market** — "whether positioning and pricing claims stay frozen until
   decision 11 resolves." Decided: yes, frozen, since the provisional
   ruling could still be vetoed and a published price claim is harder to
   walk back than a ledger entry. This is a backlog/schedule call within
   PM authority, not a pricing decision itself.
5. **ExO** — "the workflow-scope PAT decision." Deferred to owner: this
   is a GitHub App installation permission, a real authority question
   (per decision 4's carve-out for what the owner alone reserves), not
   something decidable by any agent. Tracked above as items 5 and 13.
6. **Security** — "a decision on the digest-history rewrite." Deferred to
   owner: rewriting public git history is disruptive (force-push, breaks
   two in-flight branches and any existing clones) and irreversible in
   practice; squarely the kind of call decision 4 reserves. Tracked above
   as item 4.
7. **Skill** — "the decision 11 ruling, and whether the failing trigger
   case gets fixed before launch or ships red." Decision 11: same
   provisional ruling as above. The trigger case: decided, fix it on the
   seat's normal Tuesday cadence (docs/ideas.md, accepted this run).
8. **Frontend** — "ten minutes of the owner's eyes on the new email
   capture and live metric." Deferred to owner: her attention is the ask
   itself. Tracked above as item 12.
9. **Research** — no decision needed; its one ask (direct Neon access)
   was already satisfied before this triage.
10. **Finance** — "the Claude subscription's monthly figure." Deferred to
    owner: it is a real dollar figure, squarely money, decision 4's other
    carve-out. Tracked above as item 11.
11. **Sales** — "merge PR #22." Merged by you since this triage started
    (no further action). Its three named morning triggers, decided
    separately: the multi-seat Stripe question is already a proposed
    ledger entry inside PR #22's own docs/ideas.md addition, no new action
    needed; sending the first ten outreach notes is deferred to owner
    (item 10 above, "you send, per the law"); the Left-Behind Index page
    is decided (accepted, docs/ideas.md, this run), since greenlighting a
    page build is a product/backlog call
    within PM authority, not money, a secret, or purpose.

## Deploy action owed: the triage fix (engineer, 2026-09-19)

Added by the engineer seat under the owner's URGENT dispatch of 2026-09-19,
which directed this seat to write the deploy command into this file. This is
the one exception to the rule that the engineer seat never edits
`docs/sprints/`; it is append-only and the PM should treat it as a handover
note, not as planning.

**Merging the PR does not deploy anything.** `docs/scaling.md` states the
current CI/CD honestly: "Push to main, `modal deploy` by hand". Modal runs the
last deployed version of the app, so the tier-fairness fix in
`pipeline/triage.py` sits inert on `main` until someone runs:

    modal deploy pipeline/triage.py

Owner's or chair's action, dated 2026-09-19. Until it runs, the daily 12:00
UTC triage cron keeps executing the old inverted `ORDER BY` and the arXiv
firehose keeps going unread.

Two things to check in the first run's logs afterwards, both new in this
change and both one line:

1. `queue: tier <t>: <n> waiting, oldest <date>` for every tier. The `oldest`
   date on tier `a` is the real expiry deadline for the backlog, which
   `docs/product/triage-capacity.md` could only estimate.
2. `triaged <n> papers ... (a=..., b=...)`. More than one tier in that split
   is the acceptance evidence. One tier means the inversion is back.

Related and separate: research's PR #42 adds `cs.CR` to `sources.yaml`. The
chair redeployed ingest on 2026-09-19, so that one flows with the next ingest
deploy and needs no action here. The two changes are independent, but `cs.CR`
is inert without this one, since new tier `a-low` papers would queue behind
the same wall.

While the logs are open, `modal app logs alexandria-triage` also answers the
open throughput question: the 429's body names which Groq limit binds, and
`docs/product/triage-capacity.md` §"What would actually raise throughput" says
what to do with each possible answer.

## Owner action, 2026-09-24: the Moonshot key as a Modal secret (ADR-32)

The press moves to Kimi K2. The pipeline reads MOONSHOT_API_KEY from
a Modal secret named `moonshot`. Only the owner holds the key (it is
the same key HQ stored as the GitHub secret OPENROUTE_API_KEY, which
is write-only). One terminal command, paste the key when prompted so
it never appears in a transcript:

    modal secret create moonshot MOONSHOT_API_KEY=<paste>

Then the chair deploys and prints. Finance: Moonshot usage is a
direct alexandria cost from this date, roughly $0.05 an issue.

## Press recovery: your one check, and what the chair runs (engineer, 2026-09-24)

Added by the engineer seat under your urgent dispatch of 2026-09-24,
which directed this seat to write the one-click check into this file.
Second use of the same narrow exception as the triage-fix note above:
append-only, a handover note, not planning. The PM should treat it as
such.

### 1. The one-click check only you can run

**Did Monday's 15:00 UTC schedule fire at all?** The repo cannot answer
this and neither can the Modal CLI. `modal app logs alexandria-weekly`
shows no output for 2026-09-21, and no-output is the same value for "the
container never started" and "the container started and died before its
first print". Schedule history lives only in the dashboard.

One click:

> **https://modal.com/apps/alexandria-weekly** → the **weekly** function
> → the **Schedule** or **Runs** tab → look for an entry dated
> **Monday 2026-09-21, 15:00 UTC**.

Three possible answers, and what each one means:

- **A run is listed and it failed.** Then the 404 is the whole story,
  this PR fixes the class, and nothing further is owed.
- **No run is listed.** Then there is a second, independent failure:
  Modal did not fire a cron it was deployed with, and the deployed
  version (v31) is not doing what the code says. That is a new incident,
  and it is the more serious of the two. Tell the chair and it gets its
  own register entry.
- **A run is listed and it succeeded.** Then something wrote nothing and
  reported success, which is incident 8's pattern again and the worst of
  the three answers.

Please note which one it is. It is the difference between one bug and
two, and this PR only fixes one of them.

### 2. Decision 2 is closed: you took it, and the press fits again

This section asked you to choose between shortening the generator prompt,
splitting the issue across several requests, and paying Groq. You chose
a fourth thing the same day, in ADR-32: the press writes on Kimi K2
through the Moonshot account you funded. This PR is that wiring, and the
arithmetic is no longer a complaint:

    kimi-k2.6: prompt 9865 + payload 20205 + output reservation 6000
    + envelope 32 = 36102 tokens against 222822 usable
    (262144-token context less 15% margin); fits, headroom 186720

Nothing was trimmed to reach that. The payload caps and the 6,000-token
output reservation are the same numbers main has carried since they were
set, so the issue Kimi writes is the full-size issue.

**One correction you need, and it is the kind that costs a week.** ADR-32
names the model "Kimi K2", and the obvious model id, `kimi-k2`, was
discontinued by Moonshot on 2026-05-25. A press pointed at it would
answer 404, which is incident 24 happening again on a new provider in its
first week. The live 256K general model is **`kimi-k2.6`**, and that is
what this PR uses. `kimi-k2` is recorded as withdrawn so nothing can
point at it by accident.

**Cost, for finance.** $0.0526 an issue at list price, worst case, with
the output reservation spent in full and no cache hit. That is 52 issues
a year for about $2.70. It matches what ADR-32 told finance to expect.

The two $0 improvements this section proposed are still worth doing and
neither is urgent now. A shorter generator prompt is the writer seat's
call whenever she next opens that file. Splitting the issue across
several requests is in the ledger, and its real value was never the
token count: it is that a per-section request survives the next ceiling
change too.

### 3. Correction to the dispatch: a dedicated Groq key would not help

Your dispatch offered "either the press gets its own key, or the press
runs when the crons are idle". The first option does not work, and the
reason is one sentence on Groq's rate-limit page: "Rate limits apply at
the organization level, not individual users." A second key on the same
account draws on the same 8,000 TPM as the five crons already do. Only a
separate Groq organization or the paid plan changes the number.

So this run took the second option. The press moves from Monday 15:00
UTC to **Monday 09:00 UTC**, two clear hours ahead of the earliest daily
cron and well outside the contested 11:00 to 15:00 band. It is also the
better editorial slot: 09:00 UTC is 5am in New York, so the issue is in
a reader's inbox before the working day, and the week it covers ended
the previous night, so nothing is half-ingested.

**No action owed from you on this one**, beyond knowing the send time
moved. ADR-32 has since retired the reason: the press has its own
provider and its own prepaid account, so it no longer competes with the
daily crons for anything. The slot stays at 09:00 on editorial grounds,
which were always the better argument. The issue covers the week that
ended Sunday, and 09:00 UTC is 5am in New York, so it arrives before the
working day rather than in the middle of it.

### 4. What the chair runs after this PR merges

Merging deploys nothing; Modal runs the last deployed version. Two
commands, and the first is yours because only you hold the key.

**You, once.** Paste the key at the prompt rather than typing it into the
command line, so it never lands in a shell history or a transcript:

    modal secret create moonshot MOONSHOT_API_KEY=<paste>

No agent creates this secret, no agent reads it, and the value appears
nowhere in the repository. `pipeline/weekly.py` references the name and
nothing else.

**Then the chair**, in order, stopping at the first failure:

    python3 pipeline/budget.py \
      && modal run pipeline/weekly.py::preflight \
      && modal run pipeline/weekly.py \
      && modal deploy pipeline/weekly.py

The middle two are the smoke test that
docs/agents/runtime-changes.md requires: this change adds a secret the
run reads, and that law says the next cron is never the first execution
of new machinery. `preflight` asks both providers whether the models
exist and prints what the request would cost. The manual `modal run`
prints a real issue. Only then does the deploy install the schedule.

If the secret is missing, the run does not die on a stack trace. It says
which environment variable is absent, which Modal secret provides it,
and the command above, and it emails you.

One optional secret, no action needed for it to work: `PRESS_ALERT_TO`.
Unset, press alarms go to the Gmail address the `Gmail` secret already
holds, which is yours. Set it if you would rather they went elsewhere.
