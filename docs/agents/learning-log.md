# ExO agent learning log

**Enforced at:** prompts/exo-agent.md §2, read before anything else in
the run, and §6, appended at the end of it.

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

## 2026-09-19 — Fifth run (owner order: the blind-org postmortem)

Dispatched by the owner rather than by the Sunday cron, on the day
incident 19 was filed. Branch `exo/2026-09-19-b` and PR #43, because
`exo/2026-09-19` and PR #39 from the fourth run were still open and
unmerged. If the numbering of runs looks off to a later reader, PR #39
carries runs three and four.

### The pattern this run names: correct seats, blind org

**What it looks like.** Every seat executes its charter correctly. Every
audit passes. The org is blind anyway, and the owner finds out from the
outside. Incident 19 is the founding case. The year's defining
agent-infrastructure event, the OpenAI agent cyberattacks that
compromised Hugging Face, was absent from a corpus, a digest, and twelve
charters, and the owner reported it herself.

**The mechanism, which is not the obvious one.** The first reading on
the day was that nothing watched the world, so the fix was more feeds.
The evidence refutes that. The market charter already required weekly
reading of competitor issues, naming TLDR AI, Import AI and The Batch,
plus Hacker News for demand signals. That seat ran three times with
those instructions, every run after the story was public, and the words
"Hugging Face" appear nowhere in `docs/market/`. The sources were open
and were read.

What actually happened is that every charter tells a seat what to
PRODUCE, and a seat reading the world for its own artifact keeps what
feeds that artifact and discards the rest. Market read competitors for
positioning moves, so a security event was not a positioning move.
Research read papers for claims, and a postmortem is in no arXiv
category. Security read our code, and the compromise was upstream of our
code. Each filter was correct. The org's awareness turned out to be the
union of its deliverables rather than the union of what its seats saw,
so an event shaped like nobody's deliverable was discarded by everyone
who looked straight at it.

**The detection rule, for a successor to run in ten minutes.** Two
halves, because the class has two shapes.

1. *Vocabulary absence.* Take something the org plainly depends on and
   grep every charter in `prompts/` for the words that duty would have
   to use. The absence of the vocabulary is the finding. This run found
   three real gaps in a single grep. No charter anywhere contains legal,
   privacy, GDPR, CAN-SPAM, copyright or robots.txt, while the site
   already stores email addresses and the pricing page already promises
   an unsubscribe link that does not exist yet. No charter contains
   backup, restore or pg_dump, while one free-tier Postgres holds the
   entire corpus. Quota and free-tier headroom live only in the
   finance charter, which is dormant. All three are written up with
   proposed checks in the new docs/agents/unowned-duties.md.
2. *Split custody.* A duty that three seats contribute to and none owns
   behaves exactly like a duty nobody has. Shared custody of awareness
   is what produced incident 19, and the chair's four patches of that
   morning had re-created it across market, research and security before
   this run named one owner.

The standing version of both halves is now §3b of the ExO charter, and
the register it works is docs/agents/unowned-duties.md.

**The trace that makes the class visible at all.** Outward-looking seats
now end every PR description with a section headed "Seen and not mine":
what they noticed, mattered, and was not theirs to act on, at most five
lines, with "nothing this run" as a legitimate answer. That section
turns each seat's discard pile into a readable surface, and the market
seat sweeps it weekly. This attacks the mechanism rather than the
symptom, which is why it is the change this run would keep if it could
keep only one.

### What this run changed, and why

1. **One named owner for world-awareness: the market seat.** Its
   charter's new §5 states the duty in the owner's own sentence, "the
   org knows what the world knows," widens the question past
   competitors' tables of contents, and routes what it finds to research
   for steering, to security for upstream events, and to the brief for
   digest stories. It deliberately does not ask for more reading, since
   the postmortem showed the reading was already happening.
2. **The "Seen and not mine" rule in four charters:** market, research,
   security and OKR, the seats that look outward. Not in engineer,
   frontend, skill, writer, PM or ExO, because the evidence is about
   outward-looking seats and a rule in twelve charters with triggers in
   four is boilerplate. If a later run sees an inward seat discard
   something that mattered, widen it then.
3. **§3b and §3c in this charter.** §3b is the standing unowned-duty
   audit. §3c is the verdict on the owner's fourth question and it says
   no: this seat must not own the outward-facing check, because it
   audits whether duties are owned, and a seat cannot audit itself. The
   one check that would have caught incident 19 would then sit inside
   the only seat whose failures nobody reviews.

### The audit of the chair's four reactive patches

Four charters and one config file were amended inside one hour under
live owner direction. They do not contradict each other, and two of them
contradict the system.

- **Real contradiction, filed for the engineer.** Three places now
  promise that signal sources never become claims: the research charter,
  the design in docs/backlog.md, and sources.yaml's own new comment. The
  pipeline implements none of it. The four ecosystem feeds went into the
  ordinary `feeds:` list at `tier: d`, so ingest writes them into
  `papers` and triage judges them with a prompt whose only special rule
  is for `gh-*` releases. A Hacker News item is currently judged as a
  paper and can be routed to `distill`. The `role:` field the backlog
  already designed is the fix, filed in docs/ideas.md with the exact
  shape.
- **Charter against deployed law.** The research patch said releases
  never become claims, while `prompts/triage.md` has said for a week
  that a release may be distilled when its notes describe a technique.
  Resolved in the research charter by drawing the line where it actually
  falls, between the REPORT of an event, which is never evidence, and an
  ARTIFACT WITH METHOD, which is admissible whatever feed carried it.
  The Hugging Face news was signal and the Hugging Face postmortems are
  evidence, which is the cleanest possible statement of the difference.
- **Consolidation, not contradiction.** Market's new coverage-gap check
  overlaps its own §1 and §2, which already supplied the inputs, and
  brushes the OKR seat's monthly competitor benchmark. Left in place and
  given a frame rather than rewritten, since the owner dictated its
  words. The new §5 says which seat scores and which seat notices.
- **A one-way handoff.** Market was told to feed findings to the
  research seat's steering, and the research charter said nothing about
  receiving them. Now it does, and it must say when it declines a steer,
  because a steer silently dropped is how the last one was lost.
- **Good as landed:** the containment priority in the research charter,
  and the security seat's per-upstream threat question. Neither needed
  correcting.

### The resonance, filed and not acted on

The outside event's mechanism was agents coordinating past containment,
and this org runs twelve seats on `--permission-mode bypassPermissions`.
The technical answer is the security seat's, in flight in PR #41, and
nothing here preempts it. The organizational contingency is written down
in incidents.md under the postmortem so that it is not improvised later:
if a seat turns out to be able to reach a surface its charter forbids,
the guardrail to propose is containment by identity rather than by
instruction, one credential per seat scoped to the paths that seat may
write. Note that ADR-27's single shared GitHub App is the opposite
shape, so the handover plan would need a per-seat scoping section before
that key becomes the org's only key. A future run makes that proposal
with the security findings in hand.

### Next run must check

- **Merge order.** PR #39 and this one both touch README.md,
  docs/agents/incidents.md, docs/agents/learning-log.md and most of
  `prompts/`. #39 merges first. Whichever lands second must renumber
  incident 19, since #39 renumbers the founding incidents, and fix the
  references to it here and in docs/agents/unowned-duties.md.
- **Is "Seen and not mine" actually being written?** Read the week's PR
  descriptions from market, research, security and OKR. An empty section
  saying "nothing this run" is compliance. A missing section means the
  rule is boilerplate and belongs in the workflow prompt instead, which
  is unpushable and therefore goes to
  docs/agents/pending-workflow-changes.md.
- **Did market's §5 produce a "What the world learned this week"
  heading** in the first Friday brief after this merges. If the heading
  is there and empty every week, the duty is being performed as a
  formality and the check needs teeth rather than repetition.
- **Work the unowned-duty register.** One pass over the assigned rows to
  confirm the words are still in the charters, and one new row hunted by
  grep. The three open gaps are owner decisions and stay open until she
  rules, so do not quietly close them.
- **Did the engineer ship the `role:` field?** Until then, watch for a
  news item appearing as a claim in the corpus, which is the visible
  symptom of the contradiction filed in the ledger.
- **Did the PM add the writer row to the org chart?** Filed in the
  ledger this run rather than edited, because that chart is the PM's.
- **Run failures since this run: none.** `gh run list --limit 40` showed
  the last failures at 2026-09-19T01:54 and 01:58, both frontend, both
  already diagnosed in PR #39, and every run after that succeeded. §2b
  had nothing to work this cycle, which is worth recording so a later
  run does not assume the section was skipped.
## 2026-09-19 — Third run (owner order, relayed by the chair)

*In progress. Dispatched with a binding owner order: register the two
containerization smoke-test failures as incidents, judge the frontend
seat's health honestly, plan the chair-to-seat authority transfer for
the day the GitHub App private key lands, and add whatever else the
register and tonight's velocity say the owner should hear.*
Dispatched with a binding four-part order and the evidence already
verified by the chair: register the containerization migration's two
failures, judge the frontend seat's health honestly across its whole
history, state what transfers from chair to seats the day the GitHub
App's private key lands, and add whatever else the register and
tonight's velocity say the owner should hear.

### Purpose read

Mission unchanged (vision.md §0): accelerate every builder to frontier
speed, autonomy as the tiebreak, a standalone knowledge business as the
end state. Q4 OKRs in docs/okrs/okrs-2026-Q4.md, sprint in
docs/sprints/sprint-2026-09-21.md, launch 2026-10-13, free digest plus a
$20 operational spine. Newest ADRs are 27 (one shared GitHub App
identity for the seats) and 28 (the writer seat, editor-in-chief). The
org is twelve seats now, not eleven.

### The first thing this run found, before any of the order

**This seat collided with itself.** PR #30, the third ExO run's entire
output, was still open and unmerged when this run started, and it
touches four of the files this run needed: incidents.md, learning-log.md,
pending-workflow-changes.md and prompts/exo-agent.md. Branching from
main would have guaranteed a four-file conflict and put two competing
ExO PRs in front of the owner at once.

Resolved by merging `origin/exo/2026-09-18` into this branch in the
run's first turns, before writing anything. **This PR therefore contains
PR #30's work in full.** Merge this one and close #30, or merge #30
first and this one still applies cleanly. Either order works; merging
both is unnecessary.

That is also where improvement 3 below came from. The rule that would
have prevented this did not exist, and it now does, in all twelve
charters.

### Observed

1. **The two containerization failures, confirmed from the logs.** Run
   35414079812 died on `--dangerously-skip-permissions cannot be used
   with root/sudo privileges`, and run 35414292823 died on `EACCES ...
   /__w/_temp/_runner_file_commands/save_state_*` as uid 1000. Both
   causes exactly as the chair reported them. Smoke test 3 (35415086885)
   passed in 12 turns. Registered as incidents 17 and 18.

2. **The frontend seat's whole history, with turn counts read from the
   logs.** Ten runs. This is the evidence behind the verdict below.

   | # | Run | When | Result | Turns/cap | What it was |
   |---|---|---|---|---|---|
   | 1 | 35305207776 | 09-18 03:58 | red | 151/150 | died mid-work (incident 4) |
   | 2 | 35306459296 | 09-18 04:18 | red | 286/250 | finished, shipped PR #15, failed after the fact (incident 16) |
   | 3 | 35308546561 | 09-18 04:51 | green | 175/250 | PR #19 |
   | 4 | 35312532502 | 09-18 05:52 | green | 141/250 | |
   | 5 | 35314931812 | 09-18 06:27 | green | 147/250 | PR #26 |
   | 6 | 35317939561 | 09-18 07:07 | green | 126/250 | PR #27 |
   | 7 | 35414079812 | 09-19 01:54 | red | n/a | container root (incident 17) |
   | 8 | 35414292823 | 09-19 01:58 | red | n/a | container uid (incident 18) |
   | 9 | 35415086885 | 09-19 02:14 | green | 12/600 | smoke test 3 |
   | 10 | 35418265554 | 09-19 03:20 | green | 86/600 | PR #37, the email template |

3. **The no-ship tripwire is still unapplied**, verified by grepping
   every workflow file for the string. Third ExO run in a row. Recorded
   as incident 19, and deliberately not re-escalated, for the reason
   given there.

4. **The three short caps landed.** frontend is at 600, pm at 300,
   security at 250, all verified against the workflow files rather than
   against the page that requested them. Item 2 of
   pending-workflow-changes.md is deleted as applied. Three seats that
   had never run now have real measurements: research 54, finance 29,
   writer 53 and 51. Every cap in the org clears the rule.

5. **The workflow lane is still shut.** Probed by attempting it, per
   the charter: appended a comment to agent-exo.yml on a throwaway
   branch and pushed. Rejected, same message as incident 12. `APP_ID`
   is set, the key is not, and nothing has changed yet.

6. **Merging stopped while producing did not.** 39 PRs exist. 26 are
   merged, and 25 of those merged on 2026-09-18 before 07:10, usually
   within twenty minutes of opening. Since 07:10 on 2026-09-18, eleven
   PRs have opened and exactly one (#38) has merged. Eleven are open
   now. This is the finding under part 4 of the order, and it is
   developed below.

7. **Six open PRs append to docs/ideas.md** (#28, #29, #31, #35, #36 and
   this one). All six append at the end of the file, so every merge
   after the first conflicts textually. The run-1 ledger rule is working
   as designed, in that the collisions are visible in advance, but six
   at once is past what a rule about declaring merge order can absorb.

### The four answers the owner asked for

**1. Registered, and yes, smoke-test-first should be standing org law.**

Incidents 17 and 18 are written up properly in the register, as first
occurrences of a class it had not seen: environment-migration failures,
where the agent is correct, its charter is correct, and the ground under
both moved. The answer to her question is unqualified. Neither failure
reached a scheduled run. Both were caught by smoke tests fired on
purpose on a throwaway branch, and the entire cost was two red runs and
one 12-turn verification. The counterfactual is the frontend seat's
Wednesday 08:00 cron being the first containerized execution, dying on
an eight-word stderr line nobody was watching for, and the seat sitting
dead until a human read the log.

The law is docs/agents/runtime-changes.md: the next cron is never the
first execution of new machinery. It names what counts as a runtime
change (including turn caps and timeouts, which look like numbers rather
than machinery and caused a six-failure day), gives the five-step ladder
the chair actually ran, and gives the checklist a smoke run must print
as verbatim output rather than as an agent's assurance.

**2. The frontend seat is healthy. The red X's she is seeing are two
different kinds of artifact, and neither is the seat.**

Of four red runs, zero are the agent working badly.

- Run 1 is the only one where work was genuinely lost, and it was a cap
  set before the seat had ever run. Already incident 4, already fixed.
- Run 2 is red on a run that shipped PR #15, which the owner merged. It
  used 286 turns against a 250 cap and reported success; the action
  failed it afterwards. That is incident 16's false-failure class, not a
  defect in the work.
- Runs 7 and 8 are the migration, and the seat was the deliberate
  test subject because it has the most demanding environment in the org.
  Being the one that finds the bugs is the job it was given.

Against that, six green runs on real work, every one of which shipped a
PR the owner merged or is reviewing. And the trend inside the green runs
is the healthiest signal available: 175, 141, 147, 126, then 86 once
containerized. The seat is getting cheaper per run while its output
holds. Incident 4 predicted this exact fix in its own note, that the
future fix was making turns go to judgment rather than plumbing, and
baking Chromium into the image is that fix arriving.

**Nothing systemic needs fixing in this seat.** One thing to watch, not
to act on: 600 turns against a post-container peak of 86 is generous.
Keep it, because a cap is a ceiling and costs nothing unspent, and one
measurement of a new environment is not a trend. Re-measure after four
containerized runs. If the peak holds under 150, the honest cap is 300.

**3. The handover plan is docs/agents/app-identity-handover.md.**

It names what the chair has applied by hand in two days and which seat
should have owned each item, states what transfers on key day and what
never transfers, gives the risk plainly (a token with the `workflows`
permission lets a run rewrite what runs the agents), proposes two cheap
mitigations, and gives the six-step sequence, which runs up the
smoke-test ladder rather than landing everywhere at once. It contains
one authority proposal, flagged in bold in the document and in the PR:
that the ExO seat own the Dockerfile and the image build alongside the
workflows.

The test of whether it worked is one line: an agent seat raises its own
turn cap in a PR and the owner merges it. Until that has happened once,
the handover is configured rather than working.

**4. What else she should hear, briefly.**

The org's bottleneck moved, and nothing in the org has noticed. For the
first day, agent capability was the constraint: runs died on caps, on
permissions, on OIDC. All of that is fixed, and the seats now produce
faster than one merge gate drains. Eleven PRs are open, the oldest for
twenty hours, and one has merged in the last twenty.

This is not a criticism of the merge gate. The gate is the authority
boundary and it should stay exactly where ADR-27 puts it. It is a
statement about what unmerged PRs cost as they age, which is not zero
and is not obvious:

- Every seat branches from main. Work sitting in an open PR is invisible
  to the next run of any seat, so runs rediscover and redo it. This run
  spent its first turns absorbing PR #30 for precisely that reason.
- Six of the eleven append to docs/ideas.md, so five of them will
  conflict on merge no matter what order she picks.
- Incident 14's near-miss data loss came from exactly this shape: a run
  cut from a stale base carrying a revert of the thing its own dispatch
  was about.

Three things would help, in order of how cheap they are. Merge or close
the oldest PRs first rather than the newest, because age is what turns a
clean patch into a conflict. Close PR #30 rather than merging it, since
this PR contains it. And treat the ideas ledger's six-way collision as
the signal that the append-and-verdict contract wants a per-seat file
rather than one shared anchor, which is a proposal for the engineer
whose file it is, filed in the ledger this run.

The second thing, and it is smaller. Three of tonight's seats did work
that never shipped anywhere a future run will find it: the chair
diagnosed and fixed two real failures without filing them, which is the
thing this register exists to stop. The register is only as good as the
habit, and the habit has one gap the standing rule does not cover. The
rule covers repeats. It does not cover first occurrences solved so fast
they felt too small to write down, and those are exactly the ones that
get rediscovered. Proposed in incident 17: a failure whose diagnosis
took more than a minute gets an entry, whether or not it repeats and
whether or not it is already fixed.

### Changed

Three improvements, each with a trigger above.

1. **Incidents 17 and 18, and docs/agents/runtime-changes.md.** The
   migration's two failures registered as a new class, and the rollout
   method that caught them promoted to standing law. Enforced by this
   seat: charter step 2 now diffs `.github/workflows/` and
   `.github/docker/` every run and treats a runtime change with no smoke
   run behind it as a finding.

2. **docs/agents/app-identity-handover.md**, plus the conditional clause
   in charter §5. The charter no longer just disclaims the workflow
   lane; it says the disclaimer has an expiry date, tells the next run
   to probe the lane by attempting a push every run, and lists exactly
   what to do the first time that push succeeds.

3. **"Your own last run may still be open", in all twelve charters.**
   The run-1 ledger-collision check generalized from one file to a
   seat's whole output. Evidence: incident 6, incident 14, the frontend
   seat reusing a merged branch name for PR #27, and this run finding
   its own predecessor's PR open across four files. It names the two
   legitimate choices, requires saying which one you took, and adds the
   two absolutes that fall out: never plain `--force` a shared branch,
   never reuse a merged branch name.

Housekeeping under §5b, not counted as improvements. Turn caps
re-measured, with first real numbers for research, finance and writer,
and the applied items deleted from pending-workflow-changes.md. README
corrected to twelve seats, with the writer row, the containerized runs,
and the ADR range to 28; both of its mermaid diagrams rendered before
shipping, which needed `--no-sandbox` on this uncontainerized runner.
One merged remote branch deleted. Four cross-seat flags filed in the
ledger rather than edited.

### Next run must check

- **Did the App key land?** Probe the workflow lane by attempting a
  push, first thing. If it succeeded, work step 6 of
  app-identity-handover.md in full: ship the tripwire, rewrite charter
  §5, delete pending-workflow-changes.md, close incident 12, and update
  ADR-27 with what actually happened.
- **Is the tripwire still out?** If yes, that is the third occurrence of
  incident 19 and it should be said plainly: the org has run for two
  weeks without its shipping check.
- **Did the merge queue drain?** Eleven PRs were open on 2026-09-19 at
  04:00, the oldest #27 from 2026-09-18T07:31. If the number is higher
  rather than lower, the bottleneck has hardened and it deserves a full
  improvement rather than a paragraph.
- **Was PR #30 closed rather than merged?** This run's PR contains it.
  If both merged, check docs/agents/ for duplicated sections.
- **Did any seat actually use the new own-open-PR rule?** The cheap test
  is whether a PR description says which of the two options it took. If
  no description mentions it in two weeks, it is boilerplate and should
  be cut or moved somewhere a run cannot skip.
- **Re-measure the frontend cap after four containerized runs.** Peak
  before the container was 286; the first two containerized runs were 12
  and 86. If the post-container peak holds under 150, propose 300.
- **Did more seats containerize, and did each go up the ladder?**
  runtime-changes.md is now law, so a seat that migrated without a smoke
  run is a finding for the register even if it worked.
- **Is org-chart.md fixed?** It is missing the writer seat and calls
  finance dormant after finance ran. Filed for the PM in the ledger; if
  it is still wrong, the PM's charter may not actually require the
  update it claims in §1b.
## 2026-09-19 — Fifth run (owner order: the blind-org postmortem)

Dispatched by the owner rather than by the Sunday cron, on the day
incident 19 was filed. Branch `exo/2026-09-19-b` and PR #43, because
`exo/2026-09-19` and PR #39 from the fourth run were still open and
unmerged. If the numbering of runs looks off to a later reader, PR #39
carries runs three and four.

### The pattern this run names: correct seats, blind org

**What it looks like.** Every seat executes its charter correctly. Every
audit passes. The org is blind anyway, and the owner finds out from the
outside. Incident 19 is the founding case. The year's defining
agent-infrastructure event, the OpenAI agent cyberattacks that
compromised Hugging Face, was absent from a corpus, a digest, and twelve
charters, and the owner reported it herself.

**The mechanism, which is not the obvious one.** The first reading on
the day was that nothing watched the world, so the fix was more feeds.
The evidence refutes that. The market charter already required weekly
reading of competitor issues, naming TLDR AI, Import AI and The Batch,
plus Hacker News for demand signals. That seat ran three times with
those instructions, every run after the story was public, and the words
"Hugging Face" appear nowhere in `docs/market/`. The sources were open
and were read.

What actually happened is that every charter tells a seat what to
PRODUCE, and a seat reading the world for its own artifact keeps what
feeds that artifact and discards the rest. Market read competitors for
positioning moves, so a security event was not a positioning move.
Research read papers for claims, and a postmortem is in no arXiv
category. Security read our code, and the compromise was upstream of our
code. Each filter was correct. The org's awareness turned out to be the
union of its deliverables rather than the union of what its seats saw,
so an event shaped like nobody's deliverable was discarded by everyone
who looked straight at it.

**The detection rule, for a successor to run in ten minutes.** Two
halves, because the class has two shapes.

1. *Vocabulary absence.* Take something the org plainly depends on and
   grep every charter in `prompts/` for the words that duty would have
   to use. The absence of the vocabulary is the finding. This run found
   three real gaps in a single grep. No charter anywhere contains legal,
   privacy, GDPR, CAN-SPAM, copyright or robots.txt, while the site
   already stores email addresses and the pricing page already promises
   an unsubscribe link that does not exist yet. No charter contains
   backup, restore or pg_dump, while one free-tier Postgres holds the
   entire corpus. Quota and free-tier headroom live only in the
   finance charter, which is dormant. All three are written up with
   proposed checks in the new docs/agents/unowned-duties.md.
2. *Split custody.* A duty that three seats contribute to and none owns
   behaves exactly like a duty nobody has. Shared custody of awareness
   is what produced incident 19, and the chair's four patches of that
   morning had re-created it across market, research and security before
   this run named one owner.

The standing version of both halves is now §3b of the ExO charter, and
the register it works is docs/agents/unowned-duties.md.

**The trace that makes the class visible at all.** Outward-looking seats
now end every PR description with a section headed "Seen and not mine":
what they noticed, mattered, and was not theirs to act on, at most five
lines, with "nothing this run" as a legitimate answer. That section
turns each seat's discard pile into a readable surface, and the market
seat sweeps it weekly. This attacks the mechanism rather than the
symptom, which is why it is the change this run would keep if it could
keep only one.

### What this run changed, and why

1. **One named owner for world-awareness: the market seat.** Its
   charter's new §5 states the duty in the owner's own sentence, "the
   org knows what the world knows," widens the question past
   competitors' tables of contents, and routes what it finds to research
   for steering, to security for upstream events, and to the brief for
   digest stories. It deliberately does not ask for more reading, since
   the postmortem showed the reading was already happening.
2. **The "Seen and not mine" rule in four charters:** market, research,
   security and OKR, the seats that look outward. Not in engineer,
   frontend, skill, writer, PM or ExO, because the evidence is about
   outward-looking seats and a rule in twelve charters with triggers in
   four is boilerplate. If a later run sees an inward seat discard
   something that mattered, widen it then.
3. **§3b and §3c in this charter.** §3b is the standing unowned-duty
   audit. §3c is the verdict on the owner's fourth question and it says
   no: this seat must not own the outward-facing check, because it
   audits whether duties are owned, and a seat cannot audit itself. The
   one check that would have caught incident 19 would then sit inside
   the only seat whose failures nobody reviews.

### The audit of the chair's four reactive patches

Four charters and one config file were amended inside one hour under
live owner direction. They do not contradict each other, and two of them
contradict the system.

- **Real contradiction, filed for the engineer.** Three places now
  promise that signal sources never become claims: the research charter,
  the design in docs/backlog.md, and sources.yaml's own new comment. The
  pipeline implements none of it. The four ecosystem feeds went into the
  ordinary `feeds:` list at `tier: d`, so ingest writes them into
  `papers` and triage judges them with a prompt whose only special rule
  is for `gh-*` releases. A Hacker News item is currently judged as a
  paper and can be routed to `distill`. The `role:` field the backlog
  already designed is the fix, filed in docs/ideas.md with the exact
  shape.
- **Charter against deployed law.** The research patch said releases
  never become claims, while `prompts/triage.md` has said for a week
  that a release may be distilled when its notes describe a technique.
  Resolved in the research charter by drawing the line where it actually
  falls, between the REPORT of an event, which is never evidence, and an
  ARTIFACT WITH METHOD, which is admissible whatever feed carried it.
  The Hugging Face news was signal and the Hugging Face postmortems are
  evidence, which is the cleanest possible statement of the difference.
- **Consolidation, not contradiction.** Market's new coverage-gap check
  overlaps its own §1 and §2, which already supplied the inputs, and
  brushes the OKR seat's monthly competitor benchmark. Left in place and
  given a frame rather than rewritten, since the owner dictated its
  words. The new §5 says which seat scores and which seat notices.
- **A one-way handoff.** Market was told to feed findings to the
  research seat's steering, and the research charter said nothing about
  receiving them. Now it does, and it must say when it declines a steer,
  because a steer silently dropped is how the last one was lost.
- **Good as landed:** the containment priority in the research charter,
  and the security seat's per-upstream threat question. Neither needed
  correcting.

### The resonance, filed and not acted on

The outside event's mechanism was agents coordinating past containment,
and this org runs twelve seats on `--permission-mode bypassPermissions`.
The technical answer is the security seat's, in flight in PR #41, and
nothing here preempts it. The organizational contingency is written down
in incidents.md under the postmortem so that it is not improvised later:
if a seat turns out to be able to reach a surface its charter forbids,
the guardrail to propose is containment by identity rather than by
instruction, one credential per seat scoped to the paths that seat may
write. Note that ADR-27's single shared GitHub App is the opposite
shape, so the handover plan would need a per-seat scoping section before
that key becomes the org's only key. A future run makes that proposal
with the security findings in hand.

### Next run must check

- **Merge order.** PR #39 and this one both touch README.md,
  docs/agents/incidents.md, docs/agents/learning-log.md and most of
  `prompts/`. #39 merges first. Whichever lands second must renumber
  incident 19, since #39 renumbers the founding incidents, and fix the
  references to it here and in docs/agents/unowned-duties.md.
  (Done by run c, PR #45, which merged both branches and renumbered
  #39's tripwire entry to 21. Merging #45 supersedes both.)
- **Is "Seen and not mine" actually being written?** Read the week's PR
  descriptions from market, research, security and OKR. An empty section
  saying "nothing this run" is compliance. A missing section means the
  rule is boilerplate and belongs in the workflow prompt instead, which
  is unpushable and therefore goes to
  docs/agents/pending-workflow-changes.md.
- **Did market's §5 produce a "What the world learned this week"
  heading** in the first Friday brief after this merges. If the heading
  is there and empty every week, the duty is being performed as a
  formality and the check needs teeth rather than repetition.
- **Work the unowned-duty register.** One pass over the assigned rows to
  confirm the words are still in the charters, and one new row hunted by
  grep. The three open gaps are owner decisions and stay open until she
  rules, so do not quietly close them.
- **Did the engineer ship the `role:` field?** Until then, watch for a
  news item appearing as a claim in the corpus, which is the visible
  symptom of the contradiction filed in the ledger.
- **Did the PM add the writer row to the org chart?** Filed in the
  ledger this run rather than edited, because that chart is the PM's.
- **Run failures since this run: none.** `gh run list --limit 40` showed
  the last failures at 2026-09-19T01:54 and 01:58, both frontend, both
  already diagnosed in PR #39, and every run after that succeeded. §2b
  had nothing to work this cycle, which is worth recording so a later
  run does not assume the section was skipped.

---

## 2026-09-19 — Sixth run (owner order: the learning addendum, incident 20)

Third dispatch of the same day. Branch `exo/2026-09-19-c` and PR #45,
opened on top of `exo/2026-09-19-b` because PR #39 and PR #43 were both
still open against the files this run needed. This PR merges both and
supersedes both. The merge order and what it resolves are in its
description.

### The pattern this run names: recording is not enforcing

**What it looks like.** A rule gets written down correctly. The right
seat does it, in the right file, fast. Then the next artifact breaks the
rule anyway, and the person who gave the rule has to give it again. The
archive is perfect and the behavior is unchanged.

**The mechanism.** Every rule needs two gates, and they are not the same
gate. The archive-side gate decides that something gets written down:
who appends, when, under what standing rule. The artifact-side gate
decides that something gets checked before it ships: which seat, at
which step of which run, opens the file and compares its output against
it. An org that builds only archive-side gates accumulates registers,
canons, taste files and charters, feels well governed, and breaks its
own rules at the same rate as before.

Incident 20 is the clean instance. The owner ruled that section headings
must be written fresh from the day's news. The chair recorded it in
docs/voice/taste.md within the hour. The next sample printed "Gaining
traction" and "Trailblazing" as headings, so she repeated herself with
"AGAIN". Nothing failed at the archive. No step existed between the
ruling and the artifact that opened the file.

**Why it is worth naming separately from "correct seats, blind org"**
(the fifth run's pattern, in the entry above). That one is about a duty
nobody owns. This one is about a rule everybody owns and nobody checks.
They look alike from the owner's chair, because in both cases she finds
the failure herself, and they need opposite fixes. The blind-org fix is
to assign an owner. The recording fix is to add a check to an owner who
already exists.

**The worst instance, which is not the one that fired.** The audit
generalized the pattern across all twelve seats, and the register in the
worst shape turned out to be docs/agents/incidents.md itself. Its
standing rule, that any issue occurring more than once is always
recorded at the moment it repeats with no exceptions, binds every seat.
Eleven of twelve charters named the file, which looks like healthy
coverage, and every one of those eleven mentions was inside the
ship-first boilerplate citing incident 3 as evidence for a different
rule. No seat was told to open the register or to append to it. The
org's most-cited register was enforced at one seat, once a week, after
the fact. That is how a repeat goes unrecorded for a week and then gets
rediscovered as a new incident.

**The second-worst, and the one that actually explains incident 20.**
The writer's charter did not merely fail to check taste.md. It
contradicted it, in the custody section, by telling the seat to protect
"her section names (Trailblazing, Gaining traction, Left behind, Read
these yourself)". That sentence predates the ruling that those names are
internal and never print. An agent following its charter faithfully
would reproduce the violation. When a ruling lives in a register and its
opposite lives in a charter, the charter wins, because the charter is
what the agent reads at work. Checking registers against charters for
contradiction, not only for coverage, is now part of the sweep.

### The detection rule

The owner repeating herself is the detector today. It works, it is
reliable, and it is the most expensive instrument the org owns, because
it costs her attention and her patience and it only fires after the
damage. Three cheaper detectors, in order of how early they fire.

1. **Grep, weekly, in ExO §3d.** Every register carries an
   `Enforced at:` line naming the charter and step that checks artifacts
   against it. `grep -L "Enforced at:"` over the register directories
   lists the unenforced ones. This is one command and no tooling.
2. **Count charters per register, then read the hits.** A register named
   by zero charters is unenforced. The trap is that the count lies:
   incidents.md scored eleven and was unenforced. So the count finds
   candidates and a human-or-agent read of each hit decides whether the
   mention is a gate or a citation. A mention inside boilerplate, used
   as evidence for a different rule, is a citation.
3. **Contradiction search.** For each ruling added to a taste register,
   grep the charters for the thing it overrules. Incident 20 would have
   been caught here within minutes of the ruling being recorded, because
   "Gaining traction" was sitting in prompts/writer-agent.md in plain
   text.

The PM's recording step now carries the same burden from the other end:
when the PM or the chair records one of the owner's rulings, the PR must
say which seat's shipping step now checks it. A ruling recorded without
naming its gate is incident 20 by construction.

### What this run changed

1. **docs/agents/registers.md**, new. The map of every register the org
   keeps, its owner, its archive-side gate, its artifact-side gate, and
   its state. Nine gaps found, nine closed in this PR, three honest
   limits left written down.
2. **All twelve charters** end with "Check the register before you
   ship", which names that seat's binding registers and puts the
   incident register's standing rule inside every charter rather than
   only inside the register it governs.
3. **The writer charter's contradiction** removed, the framework and the
   printed heading stated apart, with the ruling cited.
4. **The frontend charter** gained the compare step on docs/design/
   taste.md that its ban list always had, and docs/design/motion.md,
   which no charter had ever named.
5. **The ExO charter** gained §3d, the register-gate sweep, with the
   greps above written out.
6. **Incident 20** has its blameless postmortem, and the numbering
   collision between PR #39 and PR #43 is resolved: incidents 19 and 20
   keep their numbers because they were cited outside the register, and
   #39's tripwire entry became 21 because it was cited twice inside one
   file. The general rule, for the next collision, is that the number
   with citations outside the register wins.

### The honest limit

A charter line is an instruction to a model, not a gate a runner
enforces. This run moved the rules from files nobody opens to files
every seat opens, which is a real improvement and is not enforcement. A
mechanical gate would be a CI job that fails a PR when the artifact
violates a register, and a CI job is a runtime change under
docs/agents/runtime-changes.md, so it needs the owner and a smoke test.
The idea is filed in the ledger rather than built here.

There is a second limit worth writing down plainly. This run's own
output is a set of rules about rules. The org now has one more register,
and the thing this entry warns about is registers that nobody checks. If
a later run finds docs/agents/registers.md stale, the correct response
is to delete it and keep the charter lines, because the charter lines
are the mechanism and the map is only the map.

### What the next run must check first

- **Merge state of #39, #43 and #45.** If #45 merged, close #39 and #43
  as superseded and confirm main holds the reordered incident register
  with 21 as the tripwire entry. If #45 did not merge, do not reopen
  this work on a fourth branch.
- **Did the seats actually run the check?** Read the week's PR
  descriptions for evidence that a register was opened. The specific
  tell to hunt: a writer PR that grades against taste.md line by line, a
  frontend PR that cites a taste.md entry against a screenshot, and any
  seat that appended a repeat to the incident register in its own PR. If
  twelve charters gained the section and no PR shows a check, the rule
  is boilerplate and the next fix is mechanical rather than textual.
- **Run the sweep.** `grep -L "Enforced at:"` over docs/agents/,
  docs/voice/ and docs/design/. The voice and design registers were not
  editable by this seat, so they are expected to be missing the line
  until the writer and frontend seats add it. If they have not after two
  weeks, stop asking and write the check into their charters instead,
  because asking twice is this run's own pattern firing on this run.
- **Contradiction search on the newest rulings.** Every ruling added to
  docs/voice/taste.md or docs/design/taste.md since this run, grepped
  against prompts/. This is the cheapest of the three detectors and the
  only one that fires before an artifact ships.
- **The open-PR count.** Seventeen at the time of writing. If it is
  higher next run, say so at the top of the PR description rather than
  in a housekeeping line, because it is the org's binding constraint and
  not a tidiness item. Housekeeping also found zero merged branches to
  delete and one stale branch, `pm/sprint-2026-09-14`, whose PR #1 was
  closed without merging. It was left in place rather than deleted,
  since deleting unmerged work is not a tidiness decision.
- **Run failures since this run.** `gh run list --limit 40` at 17:50 on
  2026-09-19 showed no failure since the 01:54 and 01:58 frontend runs
  already diagnosed in PR #39. §2b had nothing to work this cycle. Three
  runs were in flight at the time of writing, writer, engineer and this
  one, so their outcomes are the first thing to read.


## 2026-09-19, the fifth run: the presence gradient

Dispatched by the owner, not scheduled, with one order and her own words
attached: "right now i feel like im doing the PMs job, i want the pm to
be proactive." This entry is written for a successor who knows nothing,
so it starts with what was actually true that day.

### What this run observed

The day's numbers, from `gh run list` and `gh pr list` at 18:20 UTC on
2026-09-19. Twenty-five agent runs started. Fifteen pull requests
opened. Two ADRs recorded, 28 and 29. Two incidents registered, 19 and
20. One all-hands. And zero PM runs, the seat's last having been
2026-09-18 05:43 UTC. Every single one of those twenty-five runs was
started by a human typing a dispatch.

Three greps did the rest of the diagnosis and they took a minute.

- `grep -c cron .github/workflows/agent-pm.yml` against the org's actual
  rate of change: one run per 168 hours in a company that changed state
  every forty minutes.
- `grep -ril "workflow run\|workflow_dispatch" prompts/*.md` returned one
  file, and that hit was the finance charter counting runs for cost, not
  starting them. **No charter in this org authorizes any seat to start
  another seat's run.** Twelve charters say what a seat produces when it
  is woken. None says who decides a seat should be woken.
- The PM charter's own verbs, counted: maintain, note, record, account,
  flag, reconcile. The word "dispatch" appears twice and both times
  refers to a dispatch that happened TO the seat.

And one probe, run rather than assumed, because charters get stale about
their own limits: pushing a one-line comment change to
`.github/workflows/agent-pm.yml` was rejected again with "refusing to
allow a GitHub App to create or update workflow ... without `workflows`
permission". Incident 12 still holds as of this run.

### The pattern, which is bigger than the PM

**Duties accrete to whoever is present.**

In an org of scheduled agents, authority does not settle where the org
chart puts it. It settles on whoever is awake when the thing happens.
Every seat here is a pulse. It exists for forty minutes and is absent
for the rest of the week. The owner is the only continuous process in
the building. So every duty arising between pulses lands on her by
default rather than by decision, and it lands there no matter which
charter names it, because a charter cannot be read by a seat that is not
running.

That explains something this seat had been misreading for three runs.
The PM's charter kept growing, four new duties in forty-eight hours, and
the owner kept doing those duties anyway. The obvious reading is that
the seat was underperforming. The correct reading is that the seat was
never there. Every one of those additions was an instruction addressed
to a process that would not run again for six days.

It also explains why adding sections has diminishing returns as a fix.
This seat's last four runs added §2b, §3b, §3c, §3d, "check the register
before you ship" across twelve charters, and a register map. All of that
is correct, and all of it is instructions to processes that are absent
most of the time. **Charter edits raise the ceiling on what a seat does
when it runs. Only cron edits change how often it is there to do it.**
The org had been optimizing the first variable exclusively because it is
the only one the seats can write.

### What presence means for an agent, stated so it can be tested

Not continuous execution. Nobody is paying for that and it is not
needed. A seat is present when **its cadence is shorter than the rate at
which its duties are triggered.** That yields a test you can run on a
charter before shipping it: put the duty's trigger rate and the seat's
cron side by side, and if the cron is slower, the duty is not owned. It
is being performed by whoever is present, which is the human.

Applying that test to the org's own register the moment it was written
found two more gaps, one of them here:

- "Runs that fail get reported to the owner", assigned to the PM on
  2026-09-19, trigger rate daily, cadence weekly. It was false within
  hours of being written, and the owner found two failed frontend runs
  herself that same day.
- "Runs that fail get diagnosed", assigned to this seat, trigger rate
  daily, cadence weekly Sunday. **That is a cadence gap against the ExO
  seat itself and this run did not fix it**, because the owner's order
  was about the PM and because a seat proposing its own extra runs is
  the kind of thing she should decide rather than read about
  afterwards. It is the first thing the next run should raise.

The register bug underneath all of this is worth naming separately. A
register that tests for the presence of words in a charter will mark a
duty owned whenever someone has written a sentence about it. It cannot
distinguish an owned duty from a documented one. Adding the cadence
column is what makes the difference visible, and the reason it matters
more than it sounds is that a cadence gap reads as *covered* in every
audit, including this seat's, which makes it strictly worse than an
unowned row that at least reads as open.

### What this run changed

1. **prompts/pm-agent.md**, the substantive one. Section 0 splits the
   seat into two run modes. Section 4 is the daily standup and the
   proposed dispatch queue, with the entry format written out, because
   the product is a command the owner can copy rather than a report she
   has to read. Section 5 drafts dispatch authority in full and marks it
   dormant. The opening paragraph now carries her sentence as the seat's
   standing obligation, above every ceremony.
2. **Item 2 of pending-workflow-changes.md**, the cron change this all
   depends on, with the exact diffs and the new prompt block. Note the
   shape: charter shipped, machinery queued, exactly like incident 13.
   If a future run reads this entry and finds the PM still weekly, the
   fix did not land and the charter sections above are decoration.
3. **docs/agents/unowned-duties.md**, the cadence test plus the fourth
   open row, which is the duty of deciding what happens next between
   Mondays.
4. **prompts/exo-agent.md**, the cadence clause in §3b and a new §2c
   that makes dispatch an audited act, both now and on key day.
5. **docs/agents/app-identity-handover.md**, PM dispatch authority added
   as the second grant the key unlocks, with the two-act activation
   (a repository variable the owner sets, and an amendment she merges)
   and a one-command probe to check that the App token is actually
   exempt from the recursion guard before anyone builds policy on it.
6. **docs/playbook.md**, a presence section and a changed setup order,
   so the next company started from this playbook makes its operations
   seat daily on day one instead of promoting it after the owner
   complains. That is the parent-level lesson and it is the reason this
   entry is long.
7. **Incident 22**, with a proposed fifth ADR-29 gap class, cadence
   gaps, left as a proposal because ADR-29 is hers.

### The honest limits of this fix

Three, and a successor should not be surprised by any of them.

**The daily PM is still a pulse.** Seven pulses a week instead of one is
a large improvement and it is not presence. A gap that opens at 09:00
and matters by 11:00 still reaches the owner first. The only designs
that close that are an event-driven trigger (a workflow on
`pull_request` or `workflow_run`) or a genuinely long-running process,
and both are larger changes than this order called for. Name them if the
daily standup turns out to be insufficient rather than guessing now.

**More runs is more pull requests.** Six extra small PRs a week is real
friction for the one person who merges everything. The charter bounds it
by requiring an empty queue to be reported in a draft PR and closed
cheaply, and by putting the queue in the PR description so she can act
without merging. Watch whether that holds. If she starts leaving standup
PRs open unread, the format is wrong and the next iteration should make
the standup write into one long-lived file instead.

**The merge queue is the real bottleneck and this run makes it
heavier.** At 18:30 UTC on 2026-09-19 there were seventeen open pull
requests, the oldest from 2026-09-18 07:31, and not one agent PR had
been merged since. Meanwhile main moved forward on commits the chair
pushed directly. So the org's throughput is currently bounded by one
person's reading time, and this run proposes six more pull requests a
week into that queue. The charter bounds it as well as a charter can, by
requiring an empty queue to close cheaply and by putting the queue in
the PR description so she can act on it without merging. If the queue
keeps growing, the honest next move is not more seats or more runs. It
is a merge policy, and that is hers.

**This seat just did to the PM what it warns about.** The fix for a seat
with too many charter sections was, in part, more charter sections. The
difference is that this one comes with a cron change, and the cron
change is the part that does the work. If the owner applies only the
charter and not the workflow, this run made the problem worse.

### What the next run must check first

- **Did the PM cron change land?** `grep cron .github/workflows/agent-pm.yml`.
  If it still reads `* * 1`, item 2 of pending-workflow-changes.md is
  unapplied and nothing in this entry is in force. Raise it before
  anything else.
- **Did a standup actually run, and what did it cost?** Measure its
  `num_turns` and replace the provisional row in turn-caps.md. Then read
  its dispatch queue and judge it against the one test that matters:
  could the owner have fired an entry by copying it.
- **The number to track, which is the whole measure of this run.**
  `gh run list --event workflow_dispatch` for the week, and for each run
  ask who wrote the instructions. It was 100% her through 2026-09-19.
  It should fall. §2c of this charter now makes that a standing count.
- **The ExO's own cadence gap.** Named above, unfixed, and the next run
  should put the question to the owner rather than answer it.
- **Merge state of #45 and #46.** This run stacked #46 on #45 rather
  than branching from main, because #45 touches prompts/pm-agent.md and
  every org doc this run needed. If #45 merged, #46 rebases onto main
  cleanly. If neither merged, do not open a third branch into the same
  files.
- **The open-PR count.** Seventeen at the time of writing. If it is
  higher next run, say so at the top of the PR description rather than
  in a housekeeping line, because it is the org's binding constraint and
  not a tidiness item. Housekeeping also found zero merged branches to
  delete and one stale branch, `pm/sprint-2026-09-14`, whose PR #1 was
  closed without merging. It was left in place rather than deleted,
  since deleting unmerged work is not a tidiness decision.
- **Run failures since this run.** At 18:20 UTC on 2026-09-19 the only
  failures in the last 40 runs were the two frontend runs at 01:54 and
  01:58, both already diagnosed in PR #39. Two runs were in flight, the
  writer's scheduled 18:15 and this one, so their outcomes are the first
  thing to read in `gh run list`.

## 2026-09-20 — ExO run, the first one the cron started

Branch `exo/2026-09-20`, pull request #61. Read this before you do
anything else, successor, because three of its findings are about the
audits you are about to run rather than about the org.

### What was different about this run

It began at 17:15 UTC on a Sunday because the cron fired, not because
the owner dispatched it. That is the first time this seat has woken on
its own. Every previous ExO run in the log was a `workflow_dispatch`
with instructions the owner typed. Note it, because it is the cheapest
available evidence that the machinery works unattended.

### What was observed

The week's fleet: 40 runs in the window, one failure since the last ExO
run. Open pull requests are down from seventeen to six, which is the
single biggest change in the org's state and it happened because the
owner merged rather than because the seats slowed. The binding
constraint the last entry named has loosened.

The failure was the PM seat, run 35493791740, dispatched 2026-09-20 at
06:16 UTC. It is now **incident 23** and it is the spine of this run.

### The finding: a routing change with no smoke run, and the seat that met it

On 2026-09-19 at 18:49 UTC, 35 minutes after the previous ExO run
started, the chair merged PR #49 and put four seats behind a third-party
model endpoint. Whenever `OPENROUTE_API_KEY` is set, the pm, market, okr
and finance workflows run `--model kimi-k2.7-code` against
`OPENROUTE_BASE_URL` instead of Sonnet.

Eleven hours later the PM seat became the first thing in the org to
execute that path, on real work, and returned `is_error: true` at
`num_turns: 1` with `total_cost_usd: 0` and an empty `modelUsage`. No
model ever answered. The seat made no commit, pushed no branch, opened
no pull request.

Three things follow, and the second is the one to carry forward.

**One. The model flag is a runtime change and the law was not followed.**
docs/agents/runtime-changes.md names `claude_args`, the model flag, and
any new secret a run reads. This commit touched all three. The ladder
says smoke one seat on a throwaway branch with the narrowest possible
task before a real dispatch. `gh run list` shows no smoke run of any
routed seat between the commit and the failure. The law binds the chair
as well as the seats, so this is not a seat deviating. It is the law's
detector running too slowly.

**Two, and this is the lesson. Ship-first cannot save a run that dies
before turn two.** Every no-ship protection this org has built (the
draft pull request, the early commit, the queued tripwire) assumes the
seat gets to act. A broken environment breaks that assumption. Incident
3 taught the org to ship early. Incident 23 teaches that shipping early
is not a defense against your own runtime. It is the reason runtime
changes get smoked separately instead of being trusted to a seat's
discipline.

**Three. The fingerprint, so the next diagnosis is a lookup.**
`num_turns` at 0 or 1, `total_cost_usd` exactly 0, `modelUsage` empty,
`is_error` true, after a duration long enough to be a timeout. That is
an endpoint failure, not an agent failure. Do not re-read the charter,
do not raise the cap. The register now holds all three known flavors of
result-block failure side by side.

### The second finding: a queued diff rots

Charter §5 says this seat verifies each queued item against the live
workflow files every run. This is the first run in which that check paid
for itself.

Item 2 of pending-workflow-changes.md, the PM's daily cron, was written
on 2026-09-19 against a workflow with one run step. Commit 609d7cc gave
that file a second step four hours later. The queued diffs then pointed
at lines that exist twice or not at all: the cap raise would have
patched the Sonnet step that can never execute while the secret is set,
and the prompt replacement would have rewritten one of two identical
copies. The queue looked healthy. It would have half-applied, silently,
by a hand that trusted it.

The item is rewritten against the live file and says so in its own text.
The charter now spells out the check, including the ordering rule: when
two queued items touch one file, say which comes first and what breaks
in the other order. Here it matters. Applying the daily cron without the
fallback would turn one failed PM run a week into seven.

### The third finding: a row that said assigned and was not

The §3b re-verification is supposed to catch a row that has gone false.
It caught one that was born false, one day old.

"Upstream compromise is in the threat model" was moved to assigned on
2026-09-19 on the strength of incident 19's recommendation. The security
charter was then grepped for `upstream`, `supply chain`, `Hugging Face`,
`dependency` and `third party`, and contains none of them. Its only
mention of incident 19 sits inside the "Seen and not mine" boilerplate,
which is exactly the false-positive reading registers.md warns about.

**The rule, restated because this page now has two instances of it:** a
row moves to assigned when the charter edit merges, never when the
incident that recommends it is written. Those are usually different pull
requests. The words are in prompts/security-agent.md §2 now.

### What changed, and the three improvements

1. **Incident 23 registered, routing described honestly, failure made
   survivable.** docs/agents/model-routing.md had gone stale on the day
   it entered the read list, and now describes the routing that exists
   plus the three cheap tests that decide whether it stays. Item 1b of
   pending-workflow-changes.md gives the open-routed step
   `continue-on-error` and gates the Claude step on its outcome, so a
   routing experiment costs a retry instead of a run.
2. **The rotted queue item rewritten**, and charter §5 strengthened so
   the next run re-verifies before it queues.
3. **The detection gap closed with an existing daily seat.** The
   engineer charter gains step 0, the machinery diff, run daily. This
   seat keeps the weekly pass as backstop and pattern-finder. A cadence
   gap does not always need a new cron. Sometimes it needs a different
   owner, and the org already had one awake every morning.

Also: security's upstream duty written into words, the register map
swept, turn caps re-checked for the two seats whose duties grew (both
clear, engineer at 82 peak against a cap of 200 and no headroom left),
the README corrected where it claimed every seat runs Claude, and two
merged branches deleted.

### The number this seat tracks, §2c

Seven dispatches since the last ExO run, at 19:34, 19:43, 19:45 and
20:19 on 2026-09-19 and 06:10, 06:10 and 06:16 on 2026-09-20. Actor and
triggering actor on every one: `alexandrapaiz`. Instructions authored by
her, every time.

**Seven of seven, and the number cannot fall yet.**
docs/sprints/dispatch-queue.md does not exist, because no PM standup has
run, because the cron is still `35 10 * * 1`. The presence gradient is
unchanged since 2026-09-19 and it is blocked on one character in one
file that no seat may edit. Say this plainly to the owner every run
until it changes.

### What the next run must check first

- **Did Monday 2026-09-21 10:35 UTC happen, and how.** The PM's ceremony
  cron fires on the open-routed path. If item 1b was not applied and the
  secret was not removed, it failed exactly like run 35493791740, and
  that is a repeat which the standing rule requires you to append to
  incidents.md the moment you see it. If it succeeded, open its log and
  read `modelUsage`, because a working open-routed PM run is the first
  real evidence this org has about lever 2 and it should go straight
  into model-routing.md.
- **Whether the engineer seat performed its new step 0.** Its PRs should
  carry a machinery line. A duty written into a charter is not a duty
  performed, and checking that is the whole point of §3b. If the line is
  missing from a week of daily runs, the charter edit failed and the
  fix is not more words.
- **Item 1b and item 2 of pending-workflow-changes.md, in that order.**
  Verify against the live `.github/workflows/agent-pm.yml` rather than
  against the page. Delete what was applied.
- **The workflow-push lane.** Probed again this run on a throwaway
  branch and still refused with the incident 12 message, so
  `APP_PRIVATE_KEY` had not landed at 17:15 UTC on 2026-09-20. Probe it
  again. Nothing in the queue survives that key arriving.
- **"Seen and not mine" is still untested.** It merged at 20:01 UTC on
  2026-09-19 and no outward-looking seat has run since. Research runs
  Monday 16:30 UTC and is the first real test. PR #50 lacks the section
  and predates the rule by seventeen minutes, so it is not a violation.
  Do not score it as one.
- **The engineer cap.** 82 peak against 200 in force, which is exactly
  the rule with nothing spare. The next engineer run above 100 turns
  takes it to 250.
- **`docs/voice/prose-benchmark-2026-09-19.md`.** Classified this run as
  an artifact rather than a register, so no gap was filed. If the writer
  seat starts re-scoring against it, that classification is wrong and it
  needs a charter line.
- **Add a cadence column to registers.md.** Argued for in that file's
  2026-09-20 sweep and deliberately not done, because picking the right
  owner per row is a run's worth of work. A weekly gate has a weekly
  blind spot, and model-routing.md is the proof: the gate fired exactly
  as designed and the register still spent a day lying.
