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

**Work in progress; this entry is completed before the PR leaves draft.**

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
