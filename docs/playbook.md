# The agent-company playbook

How this project is actually run: a company of AI agents with one human
owner. Written 2026-09-18 at the owner's direction so the structure can
be lifted onto any other project. The PM seat maintains it (charter
§1c); everything here is practiced in this repo, not theorized.

## The core pattern

A **seat** is: a charter (a versioned prompt file in prompts/), a
scheduled cloud workflow (.github/workflows/agent-<seat>.yml), and one
pull request per run. Nothing more. Seats never message each other;
they read and write the repository, which is the shared blackboard
(sprint files, the backlog, the ledger, the board). The owner's merge
is the only gate: agents decide everything decidable, and authority
stays with whoever clicks merge.

Roles: the **owner** is Product Owner, merge gate, and sole holder of
secrets and money. The **chair** is the interactive Claude session the
owner talks to: it convenes seats live, dispatches runs with her
instructions, does the mechanical merging on her verdicts, and records
decisions. Every seat is a fresh context per run, so anything worth
remembering must live in a file.

## The $0 cloud stack

- **GitHub repository** (public = unlimited free Actions minutes;
  private = 2,000/month).
- **GitHub Actions** as the agent runtime: each seat a workflow with
  `schedule:` cron plus `workflow_dispatch` carrying an
  `owner_instructions` input for ad-hoc runs with live orders.
- **anthropics/claude-code-action@v1** runs Claude Code headlessly on
  the owner's existing subscription: `claude setup-token` once, stored
  as the `CLAUDE_CODE_OAUTH_TOKEN` repo secret (set it via
  `claude setup-token | grep -oE 'sk-ant-[A-Za-z0-9_-]+' | gh secret
  set ...` so the token never displays).
- Workflow essentials learned the hard way (see
  docs/agents/incidents.md): permissions need `id-token: write`;
  `claude_args` needs `--permission-mode bypassPermissions` (the
  default sandbox blocks git push and reports success anyway) and an
  explicit `--model` (the action silently defaults to Sonnet);
  runs must open a DRAFT PR within their first turns and commit into
  it, or a died run ships nothing.
- Capability secrets, all owner-made, values never through any agent:
  `PROJECTS_TOKEN` (classic PAT, project scope) for the board, a
  read-only database URL where a seat needs data, and any others named
  by exact secret name only.
- Everything else per project: this one uses Modal (crons), Neon
  Postgres + pgvector, Groq free-tier open models for pipeline
  judgment, self-hosted embeddings.

## The seat roster (instantiate what the project needs)

| Seat | Cadence here | Function |
|---|---|---|
| engineer | daily | builds; OODA cycle against the sprint |
| pm (COO scope) | weekly Mon | operations: sprint, backlog, board, org chart, this playbook |
| okr | monthly | purpose guard: benchmark, KR grading, drift audit |
| market | weekly Fri | outside view: landscape, positioning, demand |
| exo | weekly Sun | improves the agents themselves; owns postmortems |
| security | biweekly | debug sweep + defensive audit |
| skill (product line) | weekly | the sellable asset's production line |
| frontend | weekly Wed | visual quality; verification by screenshot, never prose |
| weekly (domain loop) | weekly Mon | the product's own review/meta loop |
| finance, sales | dormant | books (the four questions, ROIC, EVA) and campaigns (prepare-only); activate when real |

## Governance, minimal and real

- **Mission**: one blunt Google-form sentence in vision §0, chosen by
  the owner, held quarterly by the okr seat.
- **OKRs**: at most 3 objectives x 3 KRs, tagged Committed or
  Aspirational, graded 0.0-1.0, new objectives only at quarter turns.
- **Scrum, minimal**: one-week sprints, a sprint is a GOAL plus a set
  of seat-assigned tasks, Monday planning + retro in one PM run, the
  engineer's daily PR is the standup. No ceremony without function.
- **The board**: GitHub Projects mirrors the committed files; the repo
  is the source of truth. Anyone (any agent) adds and self-assigns
  backlog cards; the PM alone sets priorities. Card standard: readable,
  self-sufficient, seat named.
- **The ledger** (docs/ideas.md): every idea with its trigger, first
  step, cost, and a status only the owner moves (proposed / accepted /
  rejected / built / urgent).
- **ADRs**: every architectural or organizational decision recorded
  with alternatives and why. The org's decisions are ADRs exactly like
  the code's.
- **All-hands**: seats convened live as fresh-context consultations,
  moderated by the chair, owner speaking directly; minutes in
  docs/allhands/ are binding owner instruction agents must read.
- **Incidents** (docs/agents/incidents.md): blameless postmortems owned
  by the exo seat; a failure recorded once and prevented forever.

## The frameworks register (adopt minimally, discard by default)

The PM stays current on operational frameworks and triages them in
docs/agents/frameworks.md under one law: a framework must never
consume more than the work it organizes. Entry requires naming the
problem it solves; one trial at a time; every adopted practice carries
a measured ceremony cost and a kill-by-default review date. Adopted
here (2026-09-18, all near-zero ceremony): minimal Scrum (already
practiced), OKRs with Committed/Aspirational grading, Amazon Working
Backwards (the launch press release and FAQ written before building
further), the pre-mortem (one hour, the week before any launch),
Kanban WIP limits (a number on the board's In Progress column), and
Team Topologies as the vocabulary for seat design. Deliberately
discarded with reasons on record: SAFe, EOS, holacracy, DACI; Shape Up
is studied as Scrum's rival, not adopted. Portable rule for any new
project: start with the adopted list above and an empty register, not
with framework shopping.

## Operating modes

**Synchronous**: owner present; relevant seats work with her live
(convened subagents or immediate dispatches carrying her words).
**Asynchronous**: owner away; the schedules are the heartbeat.
Scheduled runs never wait for her; live work never duplicates a
scheduled run in flight.

## Model and agent routing (portable, the full method)

Use models intelligently: the cheapest model that passes the bar per
task class, with the routing an explicit, verified policy, never an
accident. The three levers, cheapest first:

1. **Right-size within the family, per seat.** Set `--model`
   EXPLICITLY in every workflow's claude_args: the runner's default is
   NOT the top model, and unset means silently under-modeled (learned
   as incident 9). Premium tier for seats where errors cost most:
   code, security audits, charter edits, visual judgment, and, learned
   as incident 11, creative breadth under open briefs. Sonnet-class
   for structured strategy and writing over a repo (pm, market, okr,
   finance). A Haiku sweeper subagent (.claude/agents/sweeper.md,
   frontmatter `model: haiku`) for mechanical grunt work inside any
   run: log parsing, link checks, inventories, so premium tokens
   never read logs.
2. **Route whole seats to open models through a proxy** once a seat's
   run shape is stable: claude-code-router (or a LiteLLM-class
   OpenAI-compatible proxy) started in the runner, pointed at a free
   tier such as Groq. Gate every migration with a golden-set
   comparison, the bake-off discipline, because open-model tool
   calling on long agentic runs is the real risk.
3. **An owned router in the orchestration layer** as the destination:
   a task-class table plus an escalation rule (open model first,
   escalate to premium when a verifier rejects or the run stalls),
   tuned by the org-improvement seat from evidence. RouteLLM is the
   reference design.

Routing laws, all learned the hard way: assert the model from run
logs' modelUsage, never from config intent; a routing change that
saves tokens but dents the quality benchmark reverts; batch pipeline
judgment (non-agentic, known shape) belongs on free open models from
day one, with the agent org as the only premium spend. Turn caps are
part of routing too: size each seat's --max-turns to its real
workload, since a starved cap silently eats an entire run (incident
10), and pair every cap with the draft-PR-first rule so partial work
survives.

## Which seats first (the setup order)

For a new product run this way, create seats in this order, and
smoke-run each one supervised before trusting its schedule:

1. **No agents yet: settle the mission.** You and the chair write
   vision §0 and a first hand-made backlog. Agents amplify direction;
   they cannot invent it.
2. **The OKR seat first.** It turns the mission into objectives and a
   benchmark, so every later seat has something to serve and a score
   to be judged by.
3. **The PM/COO second.** Backlog, sprints, board, pending tracker.
   From here on, every directive you speak becomes a card.
4. **The ExO third, the moment two seats exist.** Failures then
   compound into fixes from week one: the incident register and the
   ship-first rule exist before the builders arrive.
5. **Builder seats fourth**: the engineer plus the product-line seat.
   Now the sprint has hands.
6. **Market fifth**, before any pricing or positioning decision gets
   made blind.
7. **Security before anything deploys** or touches data; **frontend
   when there is a UI**; the domain research loop when there is a
   corpus to curate.
8. **Finance and sales exist dormant from day one**, activated when
   money or launch nears.

Rule of thumb: purpose seats before planning seats, planning before
building, building before selling.

## Bootstrapping a new project with this structure

1. Repo with docs/vision.md (§0 mission + owner's calls), docs/ideas.md,
   docs/backlog.md, docs/decisions.md, docs/allhands/, docs/agents/.
2. `claude setup-token` piped into the CLAUDE_CODE_OAUTH_TOKEN secret;
   enable Actions PR creation; PROJECTS_TOKEN if using a board.
3. Copy the workflow template (this repo's agent-engineer.yml) and the
   charters that fit; write the product-specific seats fresh.
4. Seed the board and ledger with the owner's backlog; first all-hands
   sets mission, differentiation, and the first sprint.
5. Dispatch supervised smoke runs before trusting the crons; read the
   incident register first so the founding-night failures happen zero
   times instead of once.
