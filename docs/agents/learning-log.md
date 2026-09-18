# ExO agent learning log

Append-only, dated, newest run at the bottom. This file is the org's
memory across the ExO agent's fresh contexts. Write for a successor who
knows nothing and has not read this run's transcript.

---

## 2026-09-18 — First run

First cycle per prompts/exo-agent.md. Dispatched the night of the first
all-hands (docs/allhands/2026-09-17.md), with a seat directive that
named the baseline to establish and capped this run to at most one
charter fix.

### Purpose read

vision.md §0 (amended 2026-09-17): the product is the data and
orchestration layer for frontier AI research, sold as skills, a
possible memory layer, and automations; the newsletter is the human
interface, not the whole product. Free digest, $20 paid spine, launch
2026-10-13, profitable at launch, differentiation is technical
research/systems/orchestration tools, not AI news. docs/okrs/ and
docs/sprints/ hold only READMEs on main; the actual Q4 OKRs and sprint
1 exist only in still-open PRs (see below). No ADRs landed since
ADR-19 (this seat's own charter).

### Observed

1. **OIDC `id-token` failure, already fixed before this run started.**
   agent-engineer run 35297972051 (02:05) failed 3/3 OIDC attempts with
   `Unable to get ACTIONS_ID_TOKEN_REQUEST_URL`, because the workflow's
   `permissions:` block lacked `id-token: write`. Commit c7e67d5 added
   it across the agent-*.yml workflows before I read the repo, and the
   next engineer run (35298569798, 02:14) went green. No action needed;
   noted so the next run does not re-diagnose it.

2. **Three first-run PRs are open and unmerged: #1 (pm,
   `pm/sprint-2026-09-14`), #2 (okr, `okr/2026-09`), #3 (market,
   `market/2026-09-18`).** All three write to `docs/ideas.md`. PR #2
   and #3 branch from the identical base commit (169d806) and both
   insert their new entries immediately after the same anchor line (the
   `## Proposals` header, then end of file). That guarantees a textual
   merge conflict on whichever one the owner merges second: its patch
   expects the header to still be followed by nothing, and it no longer
   is. Neither PR's description mentions the other open PR or the
   collision risk. This is the concrete case the seat directive named
   ("both first-run PRs appending to docs/ideas.md and guaranteeing a
   conflict") — it is actually #2 and #3; #1 branched from an older
   base and lands in a different region of the file.

3. **A second wave of workflow_dispatch runs at 02:18 (pm, okr, market)
   was cancelled by the owner (@alexandrapaiz) a few minutes in.** No
   failure logs, no annotation beyond "canceled by @alexandrapaiz."
   Most likely a duplicate-run guard: PRs #1-3 already existed, so
   re-running those agents ad hoc would have opened a second competing
   PR per seat on top of the first. Not treated as an org defect this
   run; there is no evidence of what triggered the dispatch or why it
   was judged redundant. If this recurs, the next run should look for a
   pattern (who/what fires ad-hoc dispatches, and whether the agents
   need a "check for my own already-open PR before running" guard).

4. **docs/agents/ did not exist.** Created it now to hold this file, as
   ADR-19 and the charter require.

5. Charters read in full: engineer, pm, okr, market, exo (this one).
   All four ledger-writing charters (engineer, pm, okr, market) instruct
   appending to `docs/ideas.md` but none instructed checking for other
   open PRs first, and none required flagging a collision in the PR
   description. This is the learnability gap the charter's step 6 asks
   this run to close.

### Changed

One evidenced fix, spanning the four charters that write to
`docs/ideas.md` (engineer-agent.md, pm-agent.md, okr-agent.md,
market-agent.md): each now requires, immediately before the final
commit, running `gh pr list --state open` for other open PRs touching
`docs/ideas.md`, and if one exists, naming it and the expected merge
order at the top of the new PR's description. This does not make git
auto-merge two same-anchor appends — that is a real git limitation, not
a charter problem — but it means the owner sees the collision coming
instead of discovering it as a failed merge, and it gives whichever
agent runs second the information needed to note the conflict instead
of writing a PR description that reads as if it is the only one in
flight.

Kept to this one change per the first-run instruction. Did not touch my
own charter (prompts/exo-agent.md) this run; nothing observed argued
for a specific edit to it yet, and the directive capped this run's
charter edits regardless.

### Next run must check

- Did PRs #1, #2, #3 merge, in what order, and did #2/#3 actually
  conflict as predicted? If the owner resolved it manually, that is a
  one-time cost; if the pattern repeats with new ledger-writing PRs,
  the `gh pr list` check added this run should show up in their PR
  descriptions. Its absence is a finding.
- Whether the OIDC fix (c7e67d5) holds on the first real *scheduled*
  (cron) runs, not just workflow_dispatch.
- The PM's all-hands directive (docs/allhands/2026-09-17.md) is to
  consolidate everything into one backlog, possibly restructuring
  `docs/ideas.md` into `docs/backlog.md`. If that lands, the shared
  append-point this run's fix targets may move or disappear — reread
  the current pm-agent.md and the ledger file's actual structure before
  assuming the collision-check instruction is still well-placed.
- Whether the four charter edits this run actually get exercised (do
  the next engineer/pm/okr/market PR descriptions mention the `gh pr
  list` check) or whether they read as unused boilerplate that should
  be cut or reworded.
- The `PROJECTS_TOKEN` secret and the PM's GitHub Projects board are
  pending the owner; not this seat's concern but relevant context.
- This is a standing all-hands seat from now on (owner's decision,
  2026-09-17 all-hands). Read the newest docs/allhands/ file for
  seat-specific directives before starting purpose/observe.

---

## 2026-09-18 — Second run (synchronous, owner-priority dispatch)

Owner present, dispatched mid-session with a binding directive: audit
README.md and every architecture diagram in the repo for staleness,
rewrite the README so a stranger understands both layers of the system
(the data pipeline and the agent org that runs the company), and keep
the ADR trail and status checklist truthful. Charter §5b makes the
GitHub home this seat's, so this run spends itself there.

### Purpose read

Mission, final and alone (vision.md §0, 2026-09-18): *accelerate every
builder to frontier speed.* Tiebreak autonomy, end state a standalone
knowledge business, north star product quality against the Elicit and
TLDR-AI class. Pricing settled: the digest is free and full, the paid
spine is the operational layer at $20 a month, launch 2026-10-13,
profitable at launch. Q4 OKRs committed in docs/okrs/okrs-2026-Q4.md,
sprint in docs/sprints/sprint-2026-09-21.md, backlog consolidated in
docs/backlog.md. Newest ADR is 25, the weekly seat renamed research.

### Observed

Checked the previous run's "next run must check" list first.

1. **The ledger collision predicted last run never happened, because the
   ledger got restructured instead.** PRs #1-#3 resolved: #1 closed
   unmerged, #2 and #3 both merged (02:32 and 02:34) without the
   predicted conflict. The PM's all-hands directive landed:
   docs/backlog.md is now the consolidated leverage-ordered board and
   docs/ideas.md kept only the append-and-verdict contract. The
   same-anchor append point the last run's charter fix targeted has
   effectively moved. The `gh pr list` collision check is still cheap
   and still correct, so it stays, but it is no longer the live risk.

2. **Sixteen PRs opened, fourteen merged, in one night.** Every active
   seat shipped. Eleven seats now exist (nine active, two dormant) per
   docs/agents/org-chart.md.

3. **The research seat has never run.** agent-research.yml exists with a
   Monday 16:30 UTC cron and ADR-25 renamed the seat, but `gh run list`
   shows no research-agent run at all, and docs/research/briefs/, the
   directory ADR-25 commissions for the curation brief, does not exist.
   Not a failure, the cron has not come round yet. Recorded so the next
   run treats a still-missing brief on Tuesday as a real finding.

4. **The repo's front door describes a system two weeks dead.** This is
   the owner's directive and the evidence is flat. README.md claims the
   weekly agent is unbuilt and points at `prompts/weekly-agent.md`, a
   file that does not exist (ADR-25 renamed it research-agent.md); it
   lists `pipeline/` as holding a meta-review Modal app that was never
   written (ADR-12 folded meta-review into the weekly job, ADR-25 moved
   it to the research seat); its layout section predates docs/agents/,
   docs/sprints/, docs/okrs/, docs/allhands/, docs/security/ and
   docs/backlog.md; its status checklist calls the first skill PRs
   pending when two skills are merged in skills/; and neither of its two
   architecture diagrams contains a single agent seat, so a stranger
   reading it cannot tell that eleven agents and an owner merge gate are
   what actually run this company. Pricing is absent from the README
   entirely, so the free-digest-plus-$20-spine decision and the
   2026-10-13 launch are invisible at the front door.

5. **docs/diagrams.md carries the same blind spot plus a stale
   snapshot.** Its pipeline-status diagram is dated 2026-09-08 and still
   draws the weekly digest, gold promotion and the slow loop as dashed
   "left to build" nodes; all three have since shipped. Its blackboard
   diagram labels gold "empty, awaits promotion" while skills/ holds two
   merged skills. The file itself warns that its numbers are a dated
   snapshot, which covers the counts but not the shipped/unshipped
   status of whole nodes. No diagram anywhere in the repo shows the org
   layer.

6. **Inventory of every diagram in the repo, for the successor.**
   Four files hold mermaid: README.md (logical view, deployment view),
   docs/diagrams.md (pipeline status, blackboard, agent loop),
   docs/stack.md (current vs institutional stack), and
   docs/product/pipeline.md (the three-layer product diagram, engineer's
   surface, current). There are no ascii diagrams. site/app/graph/ and
   site/lib/graph-data.js render the *claim* graph, which is product,
   not architecture, and is not this seat's to touch.

7. **A pipeline docstring still calls the newsletter the paid product.**
   pipeline/weekly.py's header says the digest "goes to subscribers by
   email ... the newsletter is the paid product". The owner decided the
   opposite on 2026-09-17: the digest is free and full, the $20 spine is
   the operational layer. Pipeline code is outside this seat's lane, so
   this goes to the engineer as a ledger note, not an edit.

8. **A cap failed a run that had already shipped, and the owner had
   escalated the cap pattern mid-run.** The security seat's first run
   (35299288455) opened PR #8 and was then failed by the action for
   using 108 turns against a cap of 100. Separately, main gained an
   incident 10 while this run was working, recording turn-cap
   starvation as a repeat and assigning the postmortem here by name.
   Both are answered in incidents.md.

9. **The org is running synchronously around this run.** main moved four
   times while this branch was open, and PRs #17, #19 and #20 appeared
   or merged mid-run. Re-read main before assuming the repo is where the
   observe step left it. This run had to merge main and renumber its own
   incident entries because of it.

### Changed

Three improvements, each with a trigger in the section above.

1. **README rewritten around both layers, with a two-layer architecture
   diagram.** The evidence is finding 4. The new diagram draws the
   eleven seats with their cadences, the one-PR-per-run channel, the
   owner's merge as the single write to main, and main deploying the
   pipeline the org just changed, so the recursion is visible rather
   than described. Added: the seat table with its ADR per row, the
   planning hierarchy, a product section carrying free digest plus $20
   spine plus 2026-10-13, and a status checklist split into pipeline,
   org and launch. Corrected against reality: the stack table (it still
   named Llama 3.3 for triage and a metered Anthropic model for distill,
   when both are gpt-oss-120b on Groq's free tier), the MCP tool list
   (missing discovery_report and propose_change), the source counts (6
   arXiv categories and 22 feeds, not 7 and 11), the layout block, and
   the dead pointer to prompts/weekly-agent.md.

2. **The diagram atlas gained the org and lost three lies.** Evidence is
   finding 5. New section 4 draws the week as a ring with the owner's
   merge at the end of it. The status and blackboard diagrams no longer
   draw the weekly digest, the slow loop and gold promotion as unbuilt.
   The 2026-09-08 counts are kept and labelled as stale rather than
   guessed at, and refreshing them is ledgered for the engineer.

3. **Incident 3's pattern fix finally shipped, and a lane this seat
   never had was given up.** Evidence is incident 13. "Ship first, then
   work" is now a section in all eleven charters: branch, commit, push
   and `gh pr create --draft` in the first few turns, then commit as you
   go. Step 2 of this charter now reads the incident register as a work
   queue, where a pending fix outranks a new idea.

   The workflow half could not ship, and that is the most important
   thing this run learned. `GITHUB_TOKEN` cannot push
   `.github/workflows/` at all, and no `permissions:` block grants it,
   so §5 of this charter had been claiming a lane for a week that no run
   could reach. The charter now says so. The no-ship tripwire and the
   re-derived turn caps are written out in full in the new
   docs/agents/pending-workflow-changes.md for the owner to apply, and
   the durable fix (a PAT with the `workflow` scope) is flagged as an
   authority change that is hers alone to make.

Also done under §5b, as housekeeping rather than as one of the three:
five stale surfaces belonging to other seats filed in docs/ideas.md
rather than edited (see finding 7 and the ledger section dated today);
ADR-12 annotated to point at ADR-25, since it named a charter file that
no longer exists; and fifteen merged remote branches deleted after
proving each was an ancestor of main.

### Next run must check

- **Did the owner apply docs/agents/pending-workflow-changes.md?** Verify
  against the workflow files themselves, not against that page, and
  delete what landed. If she instead minted a `workflow`-scoped token,
  §5 of this charter should be rewritten to take the lane back.
- **Did the tripwire earn its place, if it landed?** It fails a run only
  when commits reached no remote branch. If it fires on a healthy run
  even once, that is a false positive and the check is wrong, not the
  seat.
- **Is "Ship first, then work" actually being obeyed?** The cheap test is
  `gh pr list --state all --json isDraft,createdAt` against run start
  times: a PR created in a run's first minutes is the rule working. If
  PRs still appear only at the end, the rule is boilerplate and needs to
  move into the workflow prompts, which are also unpushable, so it would
  join the queue.
- **Re-derive the caps.** Incident 10's rule is twice the highest
  observed turn count, floor 100. Read `num_turns` from the logs again,
  because two seats had never run when this table was built. The
  research seat's first scheduled run is 2026-09-21 and the finance seat
  has still never run.
- **Did the research seat run, and did docs/research/briefs/ appear?**
  ADR-25 commissions the curation brief and the directory did not exist
  this run. After 2026-09-21 a missing brief is a real finding.
- **One branch was left undeleted on purpose.**
  `fe/2026-09-18-mission-and-hover` has three commits that are not
  ancestors of main, but whose subjects and content duplicate three
  commits that are in main under different SHAs, which means PR #19 was
  rebased onto a fresh branch and left the old one carrying orphans.
  Nothing is lost, but confirm that before deleting it, and if frontend
  runs keep branching off already-merged branches, that is a charter fix.
- **The ledger-collision check from run 1 is being exercised.** This
  run's ledger append is the second one in flight against docs/ideas.md,
  and the merge order is declared in PR #18's description as the rule
  requires. Check whether other seats' PR descriptions do the same, or
  whether it reads as unused boilerplate.

---

## 2026-09-18 — Third run (owner order, relayed by the chair)

Dispatched in parallel with the security seat on the same evidence. The
order was specific: write the blameless postmortem for the day's six
failures, update the incident register with the third occurrence and
with the false-failure flavor as its own finding, define a standing
right-sizing methodology so caps are never guessed again, and restate
the one structural blocker for the owner. Four deliverables, one PR.

### Purpose read

Mission (vision.md §0, final 2026-09-18): *accelerate every builder to
frontier speed*, alone, no subtitle. Tiebreak autonomy, end state a
standalone knowledge business, north star product quality against the
Elicit and TLDR-AI class. Free digest, $20 operational spine, launch
2026-10-13, profitable at launch. The autonomy tiebreak matters directly
to this run, because the blocker below is exactly a case where the org
cannot act without its owner.

### Observed

Every number here came out of `num_turns` and `CLAUDE_ARGS` in the run
logs, and every shipping claim out of `git log` against the run's
window. Nothing was taken from a run's own conclusion.

1. **The six failures are confirmed exactly as relayed, and they are not
   six new incidents.** Four were already registered: the security 108
   (item 11), the frontend 151 (item 4), and the two pm 61s (item 10's
   second and third). Only two were new, and those two are the finding:
   frontend died at 150, the cap went to 250, and the very next frontend
   run used 286, twenty minutes later. PM died at 60 twice, the cap went
   to 140, and its fourth run under the new cap used 141. **Both
   reactive raises were outgrown by the seats that got them, the same
   day.** That is the argument for a ratio instead of a number.

2. **Ship first, then work has now been proven under fire, with a
   timestamp.** The rule landed on main at 05:11:42 (PR #18). All three
   runs that lost everything started before it. Run 35311930240 is the
   first cap-killed run after it: killed at 06:00:28, its PR #24 merged
   by the owner at 06:01:07. Thirty-nine seconds. The rule turned a
   total loss into a delivered sprint revision. Keep the no-ship
   tripwire queued regardless, because caps change how often a run dies
   and shipping first changes what a death costs.

3. **The two cap flavors have different fingerprints, and the difference
   is diagnostic.** Hard starvation always ends at exactly the cap plus
   one (61/60, 151/150, 141/140, no exceptions in the data). False
   failures end far past it (108/100, 286/250) with `"subtype":
   "success"` and `"is_error": false`. One counter cannot make both
   shapes, so the counter a run stops itself on and the `num_turns` it
   reports are different numbers, and the action fails the job on a
   post-hoc comparison of the reported one. The overshoot scales with
   run length, 8 turns on 108 and 36 on 286, which fits. Recorded as a
   hypothesis, because it is inferred from the data rather than read
   from the action's source.

4. **Three caps are still short after the chair's raises, including two
   this seat would not have guessed.** Measured against the rule:
   frontend 400 needs 600, pm 250 needs at least 300, security 200 needs
   250. Also worth knowing, the ExO's own last run used 93 turns against
   a 100 cap. That was a near miss nobody logged, and it is why this
   seat's cap is now in the table rather than assumed fine.

5. **Item 10's stated limit is closed.** It recorded that the two pm
   60-cap logs could not be retrieved. They retrieve fine now, and both
   read 61 against 60, confirming the owner's account exactly. The gap
   was timing, not missing data.

6. **Housekeeping.** Seven merged remote branches deleted, including
   `fe/2026-09-18-mission-and-hover`, which the last run flagged for
   confirmation: `git cherry` shows all three of its commits already in
   main by patch-id, so nothing was lost. `pm/sprint-2026-09-14` is left
   alive on purpose, because its PR #1 was closed unmerged and its work
   is not in main.

### Changed

Three improvements, plus the owner's fourth deliverable.

1. **docs/agents/turn-caps.md, new.** The standing methodology: a cap is
   at least twice the seat's highest observed turn count, rounded up to
   the next 50, floor 100. Three clauses make it usable. A run that hit
   its cap is a censored lower bound rather than a measurement, so
   re-derive from the next free-running run. A seat that has never run
   inherits its nearest twin's cap, marked provisional. Duty growth is a
   re-measurement trigger, so a charter edit that adds work gets a cap
   check instead of waiting for the failure. Four measurement commands
   are written out and were each run against this repository before
   being written down. The current table for all eleven seats is there
   with dates.

2. **incidents.md items 15 and 16.** Item 15 is the six-failure
   postmortem: what happened, why reaction always lands behind a moving
   number, what the org grew from it, and the three caps still short.
   Item 16 promotes the false failure to its own named defect class on
   its second occurrence, with the counter-mismatch diagnosis and the
   honest limit that no cap value makes it impossible, because the
   post-hoc check is upstream code this repo does not own. Both entries
   sit under a new dated section, which is also the fix for the
   register's duplicate numbering: entries now go under a new dated
   heading with the next free number, never at a shared anchor, and
   ambiguous numbers get cited with a descriptor rather than renumbered.

3. **This charter, step 6.** Turn caps are now a named standing duty:
   re-derive monthly in the first run of the month, and immediately
   whenever a cap was hit or a charter edit grew a seat's duties, with
   the two flavors' fingerprints written down so the next run diagnoses
   before it theorizes. Two ambiguous incident cross-references in this
   charter were also corrected, since the duplicate numbers had made
   both of them point at the wrong entry.

The owner's fourth deliverable, the structural blocker, is stated at the
top of docs/agents/pending-workflow-changes.md rather than buried in an
incident: no agent seat can fix the machinery that runs it, because
`GITHUB_TOKEN` cannot hold the `workflow` scope and no `permissions:`
block grants it. Six runs failed on caps and not one affected seat could
raise its own. The decision is the owner's alone, stated with both sides
of it, because a `workflow`-scoped PAT would also hand every run a token
strong enough to rewrite what runs the agents.

### Next run must check

- **Were the three queued caps applied?** Verify with
  `grep -HoE '\-\-max-turns [0-9]+' .github/workflows/agent-*.yml`,
  never by trusting the queue page, and delete what landed. If any seat
  hit a cap again in the interim, that is an immediate re-derivation, not
  a monthly one.
- **Re-derive the table regardless.** pm's 141 is censored and should be
  replaced by its first free-running peak. security has exactly one
  sample and it is the run that overshot. research and finance were
  still unmeasured at the time of writing.
- **Did the owner decide on the `workflow`-scoped PAT?** If she minted
  it, §5 of this charter takes the workflow lane back and
  pending-workflow-changes.md becomes a history file. If she declined,
  say so in that file so no future run re-litigates it.
- **Is the false-failure class still live?** It needs a run that exceeds
  its cap and still reports success. If the corrected caps hold for a
  month with no recurrence, item 16 can be marked dormant rather than
  open.
- **Did the register's new anchor convention hold?** If another seat
  appended a duplicate number under an old heading, the convention needs
  to move from this log into the charters that tell seats to write here.
- **Did the research seat run on 2026-09-21, and did
  docs/research/briefs/ appear?** Carried forward unanswered from the
  last run. After 2026-09-21 a missing brief is a real finding.
- **The no-ship tripwire is still queued and still unapplied.** It has
  outlived two ExO runs now. If it is still unapplied at the next one,
  that is itself worth an incident entry, because it is the same shape
  as item 13.

