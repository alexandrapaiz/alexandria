# Architecture decision records

Each entry: the decision, the alternatives weighed, and why. These are the study
material as much as the system is — the meta-goal of alexandria is learning systems
architecture by making these calls deliberately.

## ADR-1: Terminal state of a paper is an artifact, not "read"

Every ingested paper ends as a skill, a pattern note, or a discard. This single
decision drives the rest of the design: it makes the claim (not the paper) the unit
of storage, makes triage a routing problem rather than a summarization problem, and
gives the system a falsifiable purpose.

## ADR-2: Compute on Modal, serverless, scale-to-zero

Alternatives: GitHub Actions cron (free forever, no card, but unpunctual cron, no
GPU, push-to-test dev loop), rented GPU instance (billed while idle — wrong cost
structure for minutes-per-day workloads). Modal wins on scheduling reliability,
seconds-fast dev loop (`modal run`), first-class logs, and an open GPU path; the
$30/month starter credits cover the entire workload. GitHub Actions remains the
documented fallback — the swap was designed and costed before choosing.

## ADR-3: One Postgres (Neon) with pgvector, not a dedicated vector DB

Alternatives: Pinecone/Qdrant/Chroma (a second system to sync), Supabase (fine, but
an app platform whose auth/storage/API batteries we would not use), Turso (not
Postgres). Neon is exactly the needed thing: serverless Postgres, scale-to-zero,
vectors and structured data in one store so hybrid queries (semantic ranking +
SQL filters) are single statements.

## ADR-4: Medallion data model (bronze / silver / gold)

Borrowed from the lakehouse world: bronze = raw papers, silver = distilled claims,
gold = human-approved skills and patterns. Adopting the pattern at 1/1000th scale is
also the cheapest way to genuinely understand Databricks-style architectures.

## ADR-5: Right-size the model to the task

Triage: the largest open model on Groq's free tier (gpt-oss-120b as of 2026-09;
Groq rotates its lineup, which is exactly why the model name is one constant).
Distillation: originally slated for Claude (paid); AMENDED 2026-09-07 by blind
bake-off (docs/evals/2026-09-07-distill-bakeoff.json): gpt-oss-120b won 4–1–3
over Qwen3.8-27B on faithfulness and claim readability, so distillation is $0 on
Groq too; Qwen3.8 is the fallback, and Gemini was disqualified on free-tier
reliability (7/8 calls 429'd under backoff). Upgrading to a paid frontier
distiller stays on the roadmap, now with a golden set to measure it against.
Embeddings: Qwen3-Embedding-0.6B in-process on Modal (top open family on MTEB;
batch jobs load the model in the job, no serving endpoint needed). All providers sit
behind swappable interfaces; free-tier limits change, so portability is designed in.

## ADR-6: Retrieval is hardwired for batch, agentic for humans

The triage loop uses classic pipeline retrieval (embed, dedupe, route) because the
retrieval need is known in advance — hardwired is cheaper and more predictable. The
interactive side exposes `semantic_search` and `sql_query` as MCP tools and lets the
agent decide what to search and when to stop. Same database, two consumption modes.

## ADR-7: The system proposes changes to itself; a human merges them

The weekly meta-review reads the triage log (every decision + reasoning, labeled by
human verdicts — the eval set the pipeline emits as exhaust) and newly distilled
claims, and opens pull requests against the system's own prompts and code. It never
self-modifies: unsupervised drift in triage criteria is the eval problem eating
itself, and the human review step is where the owner's learning happens. Prompts are
versioned files precisely so that self-improvement proposals are literal git diffs.

## ADR-8: The digest looks backward as well as forward

The weekly brief is not only "what's new." Two retrospective sections are part of
the design (implemented once the claims layer has accumulated history):

- **Matured** — a slow loop revisits past claims and index-tier papers after
  months, using citation counts (Semantic Scholar API) and reinforcement by later
  claims to surface what aged well — including sleepers our triage under-rated,
  which become labeled eval failures for the meta-review.
- **Deprecated** — when a new claim lands, semantic search finds its nearest older
  claims and a model classifies the relation (supports / refines / contradicts);
  contradiction edges surface superseded techniques in the digest.

Citation counts are deliberately NOT used at the leading edge: papers arrive with
zero citations, so citations are a lagging signal — useful for retrospectives,
useless for daily triage. The fast attention proxy at the front edge is tier `b`
(human curation).

## ADR-9: Blackboard coordination — the schema is the orchestrator

Workers (ingest, triage, distill, meta-review) never message each other. They read
and write a shared store, and coordination emerges from the data's state — the
blackboard pattern (Hearsay-II, 1970s AI), rediscovered by every pipeline that
scales. Each worker's inbox is a SQL view (`triage_queue`, `distill_queue`):
an item is claimed when the worker's output row exists, which makes idempotency
and resume properties of the schema rather than of any worker's code. The
alternative — multi-agent message passing — buys parallelism at the cost of an
order of magnitude more tokens and much harder debugging; it is the institutional
swap (see docs/scaling.md), not the default. Corollary: adding a pipeline stage
means adding a view, and the stage's contract is reviewable as one SQL statement.

## ADR-10: Claim graph in Postgres, append-only, time-directional

The interpreting layer relates claims: supports / refines / contradicts /
duplicates, stored as an edges table (`claim_links`). Relational over Neo4j
because our traversals are shallow (1–3 hops), our graph queries constantly fuse
with SQL filters and pgvector similarity (one store, one query), and the graph is
small and derived — rebuildable from silver at any time. Neo4j is the
institutional swap when deep traversals dominate (docs/scaling.md); Apache AGE is
the middle rung if Cypher ergonomics are ever wanted inside Postgres.

Edges are append-only and time-directional: a new claim judges strictly older
claims; edges are never edited. Re-judgment (a later claim recontextualizing an
old edge) belongs to the slow loop. Mechanism per edge: pgvector kNN retrieves
candidate neighbors cheaply, a small model classifies the shortlisted pairs —
the same retrieve-then-reason shape as triage and RAG, one level up. The
`deprecated_claims` view (a confident incoming `contradicts` edge from a newer
claim) is ADR-8's digest section expressed as SQL.

## ADR-11: The agentic layer — thin MCP server, OAuth 2.1, promotion by pull request

The agentic layer is Claude (via the user's claude.ai subscription — a weekly
scheduled task plus ad-hoc sessions) acting as MCP host against a thin MCP
server on Modal. Division of labor: **all intelligence in the agent, all
authority in the server.** The server exposes four tools — `semantic_search`
(embeds the query with the same pinned Qwen3 model as the corpus; a vector
search is only valid inside one embedding space, so the server owns the model),
`sql_query` (SELECT-only, enforced server-side), `get_digest`, and
`propose_skill`. The agent never holds a database password or GitHub token; it
holds tools.

Auth is OAuth 2.1 as the MCP spec standardizes it — authorization code + PKCE +
dynamic client registration — implemented in-process and stateless (signed
JWTs; a single passphrase login, since there is one user). A bearer-token
shortcut was considered and rejected: claude.ai connectors speak spec OAuth
natively, and learning the industry-standard agent-auth flow is part of this
project's purpose.

Promotion is a pull request, not a write. `propose_skill` records a
`promotions` row and opens a PR into `skills/` using the server-held GitHub
token. The agent can propose anything and commit nothing — ADR-7's human gate
is enforced by plumbing, not by prompt. The meta-review loop will reuse this
same proposal channel for prompt/source diffs. Graduation path (vision §3):
when the measured record justifies it, the same agent prompt moves onto a
metered API key as a cron, and the human gate becomes optional.

## ADR-12: Meta-review lives in the weekly agent, not a sixth cron

The recursive loop (ADR-7) ships as Step 4 of the weekly agent
(prompts/weekly-agent.md) plus one MCP tool, `propose_change`, which can open
PRs against a whitelist of the system's own files (prompts/*.md, sources.yaml)
and records each proposal as a `promotions` row (kind `system_diff`).

Three forcings aligned. First, Modal's free tier caps scheduled functions at
five, all taken — a sixth cron had real cost. Second, the workflows-vs-agents
rule: meta-review is judgment over an open-ended evidence surface (triage
drift, graph errors, human overturns), which is agent-shaped work, unlike the
digest's fixed queries. Third, the proposal channel already existed —
propose_skill built the branch-file-PR plumbing; meta-review reuses it with a
path whitelist. The whitelist is the safety boundary: the loop can rewrite the
system's *judgment* (prompts, sources) but not its *machinery* (pipeline code,
schema, this file) — machinery changes stay human-authored. Cadence is bounded
in the prompt (≤1 proposal/week, evidence must be a pattern), and the human
merge remains the only way any proposal takes effect.

*Amended by ADR-25 (2026-09-18).* The seat this ADR calls the weekly
agent is now the research agent, and the charter it names has moved from
`prompts/weekly-agent.md`, which no longer exists, to
`prompts/research-agent.md`. Meta-review as Step 4 of one weekly seat,
and the path whitelist as its safety boundary, both stand as written.

## ADR-13: The gate is an agent panel, not a human

Owner's decision (2026-09-17), superseding the human-merge gate of ADR-7/12:
the skill lifecycle runs fully autonomously. Review does not disappear — it is
reassigned. A proposal (a `propose_skill` or `propose_change` PR) is judged by
a panel of independent reviewer agents, and merges when the panel passes it.
No human approval is required anywhere in the loop; the owner can still read,
revert, or override anything after the fact. Human optional, exactly as
vision §3 always declared.

The panel is harness engineering applied to our own system — each reviewer is
a small, stable, verifiable step with fresh context (independent samples, no
shared context with the author, so agreement is evidence rather than an echo):

- **Provenance reviewer.** Every claim id the skill cites must exist, and the
  cited claim must actually support the sentence citing it. Practical judgment
  not backed by a claim must be marked as ours, not the paper's.
- **Adversary.** Searches the claim graph for contradicting or refining claims
  the draft ignored. If the graph disagrees with the skill, the PR fails.
- **Validator.** Runs the A/B trial — bare model vs. skill-loaded on held-out
  prompts — and passes only if behavior moves in the direction the evidence
  supports.

Every verdict is a structured `promotions` row, so the audit trail replaces
the approval gate: **change under evidence** is preserved by recording the
evidence, not by queuing on a person. Unanimous pass merges the PR via the
server-held GitHub token; any failure leaves the PR open with the verdicts
attached for the next weekly run to address.

Scope is still bounded by the ADR-12 whitelist: the panel can merge judgment
(`skills/`, `prompts/*.md`, `sources.yaml`) but never machinery (pipeline
code, schema, these docs). Autonomy applies to what the system knows, not to
what the system is.

## ADR-14: A daily engineer agent maintains the machinery

Owner's decision (2026-09-17): alongside ADR-13's reviewer panel, a single
software-engineering agent runs once a day in a fresh session and works the
product itself — fixing bugs, maintaining code, comparing alexandria to
adjacent products, and proposing ideas the owner has not thought to prompt
for. The goal, in her words: exponential creativity, so the product is not
limited by her prompt generation. The agent's daily observations become the
prompt stream.

The loop is OODA, one cycle per day, and the charter is a versioned file
(prompts/engineer-agent.md): **Observe** — repo state, PR queue, pipeline
logs, and a rotating one-product competitive scan; **Orient** — rank against
vision.md, broken things first, then owner-accepted ideas, then its own;
**Decide** — exactly one shippable unit of work plus one to three new
triggered ideas; **Act** — one PR on an `engineer/` branch, ideas appended
to the ledger (docs/ideas.md).

Division of authority completes ADR-13's picture. The panel autonomously
*merges knowledge*; the engineer autonomously *proposes machinery* but never
merges it — machinery PRs keep ADR-7's human gate, now fed on a daily clock.
The ideas ledger is the steering interface: the agent appends `proposed`
entries with the triggering observation, the owner flips them to `accepted`
or `rejected`, and accepted ideas outrank the agent's new ones. The
engineer's own charter is carved out of every autonomous-merge surface: it
can be proposed against in the ledger, never edited in a daily PR.

Launch vehicle: a daily scheduled Claude Code task on the owner's machine —
her existing subscription is the compute budget, so steady-state cost stays
$0. Each run is a fresh clone with fresh context; statelessness is the
harness discipline, and everything durable lives in the repo, the PR queue,
and the ledger.

## ADR-15: A project manager agent runs the sprint cadence

Owner's decision (2026-09-17): a project manager agent runs Scrum over the
engineer agent and every future agent seat. Sprints are one week, Monday
through Sunday, matching the clock the system already keeps (weekly digest,
weekly meta-review). The charter is prompts/pm-agent.md; the board is
markdown in docs/sprints/, one file per sprint.

Roles map onto Scrum without inventing anything: the owner is Product
Owner (ledger verdicts and merges are the commitments), the PM agent is
Scrum Master and backlog groom, the engineer agent is the development
team, and future agents join as named seats on the sprint backlog. The
ceremonies map onto runs — the engineer's daily run is the standup (its PR
description is the standup report), and the PM's Monday run performs
retrospective, backlog grooming, and sprint planning in one pass, opening
one PR whose merge by the owner IS the sprint commitment.

Division of authority follows ADR-13/14: the PM writes only planning
surfaces (docs/sprints/, grooming notes in docs/ideas.md), never code,
never charters, and never merges. The engineer takes its daily priority
from the committed sprint file, break-fixes excepted. Velocity is measured
against merged PRs only, so the retro naturally surfaces the one queue
only the owner can drain. Blackboard coordination again, one level up:
the agents never talk to each other, they read and write the repo, and
the sprint file is the blackboard.

## ADR-16: A monthly OKR agent guards the purpose

Owner's decision (2026-09-17), with the purpose settled on the record
first (vision.md §0): autonomy wins tiebreaks, the end state is a
standalone knowledge business, and the north star is **quality of the
product, benchmarked monthly against industry-grade competitors** — her
words: "we must benchmark with industry grade competitors."

The OKR agent completes the planning hierarchy: purpose (owner) → OKRs
(quarterly, checked monthly) → sprints (PM, weekly) → days (engineer,
daily). Charter at prompts/okr-agent.md; artifacts in docs/okrs/, one
file per quarter with monthly check-ins appended. Each monthly run does
four things: reads the north star directly (a five-axis scoring of the
live product against three real competitors, rotating through the
Elicit/Consensus class, the TLDR/Import AI class, and agent-knowledge
ecosystems — the score trendline IS the metric), scores every key
result with evidence, audits the month's sprints and ledger for drift
(orphan work, orphan objectives, manual substitutions for autonomy),
and drafts or adjusts OKRs — new objectives only at quarter turns.

Authority is consistent with ADR-14/15: one PR per run, owner's merge
commits the OKRs, writable surface is docs/okrs/ plus dated ledger
notes, and purpose itself is untouchable — vision.md §0 changes only by
the owner's own hand. The PM reads the committed OKRs when planning, so
every sprint goal names the objective it serves and the chain from a
Tuesday PR to the purpose is inspectable end to end.

## ADR-17: A weekly market research agent owns the outside view

Owner's decision (2026-09-17): a market research agent runs every Friday
and owns the market the product sits inside — competitor landscape,
demand signals, pricing, positioning. Charter at prompts/market-agent.md;
artifacts in docs/market/ (landscape.md as the living competitor map,
positioning.md as the why-pay answer and observed price ladder, and one
one-page brief per week in briefs/).

The three outward-looking functions now divide cleanly and feed each
other: the engineer's daily scan is *craft* (one thing to steal in the
product), the OKR agent's monthly benchmark is *evaluation* (five-axis
scores against three competitors, picked from the market agent's
landscape map), and the market agent is *intelligence* (what the market
ships, charges, and leaves unmet). The Friday brief lands before Monday,
so the PM plans every sprint with the market in view, and market-triggered
ideas enter the same ledger as everything else, with sources attached.

Authority follows the house pattern: one PR per run merged by the owner,
writable surface limited to docs/market/ and `proposed` ledger entries,
never code, charters, sprints, OKRs, or vision.md. Research is read-only
on free public surfaces — no accounts, no posting, no contact with
anyone, no paywall scraping — because the agent gathers intelligence and
the owner alone acts in the market. Pricing decisions stay hers; the
positioning doc exists so she never makes one blind.

## ADR-18: The agent org runs in the cloud, not on the owner's laptop

Owner's finding (2026-09-17), the same day the org was born: the four
agents launched as desktop scheduled tasks, which run only while her app
is open on her machine. That fails the purpose's own tiebreak — an
organism whose heartbeat is a laptop lid is not autonomous.

The fix is the compute fallback ADR-2 documented from the start: GitHub
Actions. Each agent is a scheduled workflow in .github/workflows/
(agent-engineer daily, agent-pm Mondays, agent-market Fridays, agent-okr
monthly, plus workflow_dispatch for manual runs) that checks out the
repo and runs Claude Code headlessly via anthropics/claude-code-action.
The workflow prompt is deliberately thin — identity, the charter file to
obey, and the hard boundaries — because the charters stay the single
source of truth and remain owner-merged files.

Cost stays $0 the same way everything else does: Actions minutes are
free on a public repo, and the model runs on the owner's existing Claude
subscription through a long-lived OAuth token (`claude setup-token`)
stored as the CLAUDE_CODE_OAUTH_TOKEN repository secret. Two setup steps
are owner-only, since secrets never pass through the system: minting
that token, and enabling "Allow GitHub Actions to create and approve
pull requests" in the repo's Actions settings. The desktop scheduled
tasks are retired once the first cloud runs go green; they remain the
documented fallback if Actions cron ever proves unpunctual for a
time-sensitive agent.

## ADR-19: An ExO agent reviews and improves the agents

Owner's decision (2026-09-17): the organization gets its own loop. A
weekly ExO agent, named for the exponential-organization idea that the
org itself must improve as fast as the product, reviews how every agent
actually ran and edits the agents accordingly. Charter at
prompts/exo-agent.md; it runs Sundays in the cloud, before Monday's PM
planning.

The loop is the owner's, an OODA variant with purpose bolted on the
front and learning bolted on the end: **purpose** (vision §0, committed
OKRs, all-hands minutes and her recorded words) → **observe** (the
week's workflow runs and logs, PR outcomes, retros, drift audits, and
every charter) → **orient** (diagnose the org, not the product: charter
deviations, overlaps, gaps, repeated failures nothing remembered) →
**decide** (at most three evidenced improvements) → **orchestrate**
(edit the agent layer: charters, agent workflows, org docs) →
**learn** (docs/agents/learning-log.md, append-only, the org's memory
across the ExO's own fresh contexts).

The recursion is deliberate and bounded. Improving the agents includes
improving the ExO agent, and its charter edits to itself travel the
same one-PR-per-run channel as everything else, so the loop that
improves the loops is still gated by the owner's merge. Division of
labor stays clean: the OKR agent audits whether the WORK serves the
purpose; the ExO agent audits whether the WORKERS and their design do.
Lane rules as ever: agent layer only, never pipeline code, site,
skills, plans, or vision; any edit that moves authority between agents
or loosens an owner gate must be flagged in bold in the PR.

## ADR-20: A debug and security agent sweeps every two weeks

Owner's decision (2026-09-17): a combined debug and cybersecurity
agent runs on the 1st and 15th in the cloud
(prompts/security-agent.md, agent-security.yml). One seat, two
defensive functions. The debug sweep hunts defects: workflow failures,
broken builds, lying docstrings, dead code, and it ships small
behavior-preserving fixes in its own PR while routing larger repairs
to the engineer through the ledger. The security audit covers the
things a public-repo, $0-stack, agent-run business actually risks:
secrets in the tree or git history (found values are never printed,
only located, with rotation flagged urgent for the owner),
dependencies, the public/private boundary around digests and
subscriber data, the MCP server's OAuth and SELECT-only enforcement,
Actions workflow security, and the prompt-injection surface that comes
with agents who read the public web. Reports land in docs/security/,
severe findings in bold at the top of the PR. Strictly defensive:
no offensive tooling, nothing probed that we do not own. Fixes
preserve behavior; features stay the engineer's. Same authority
pattern as every seat: one PR per run, merged only by the owner.

## ADR-21: RAG is a synthesis tool bolted onto existing retrieval, not a new store

Owner's directive (all-hands, 2026-09-17): build RAG for real, both as a
sellable capability and inside the pipeline, beyond the retrieve-then-reason
`interpret` already does in miniature (ADR-6).

The decision: add generation on top of the retrieval alexandria already had,
rather than standing up a second retrieval path. `rag_answer` (mcp/server.py)
calls the exact same kNN query `semantic_search` uses, then hands the
retrieved claims to `gpt-oss-120b` — the same free-tier Groq model as
triage/distill/interpret, so this adds $0 to the standing cost — governed by
a new versioned prompt, `prompts/rag-answer.md`. The prompt is strict on two
failure modes that matter more here than elsewhere: it must refuse rather
than fabricate when retrieved context doesn't support an answer, and it must
cite both sides rather than silently resolve a conflict when retrieved claims
disagree — a synthesis tool that quietly picks a winner between contradicting
claims would corrupt trust in the whole corpus, not just one answer. Every
sentence in an answer carries an inline `[C<id>]` citation back to the claim
that supports it, so any answer is checkable against the same claim graph a
human would consult directly.

This keeps ADR-11's division of labor intact: authority (the DB connection,
the embedding model, the Groq key) stays server-side; the only thing new is
that synthesis now also happens server-side, against a fixed prompt, over
context the server itself retrieved — never against the open corpus and
never against the model's own training data. `rag_answer` writes nothing, so
it needs no promotion gate; it composes existing primitives rather than
adding a new authority surface. Full design writeup, the plain-language
semantic-search-vs-RAG explanation, and the product framing (self-used today,
sellable next) are in docs/product/pipeline.md §5. What's deliberately not
decided here: a customer-facing hosted endpoint, a frontier-model synthesis
tier for paying customers, and wiring this into the weekly digest draft —
each is a ledger proposal, not a call this ADR makes.

## ADR-22: A skill agent owns the gold production line

Owner's decision (2026-09-18, at the all-hands): with skills declared
the sellable focus (all-hands decision 6) and the ExO's finding that
every station of the skills pipeline was designed but none had a seat,
a weekly skill agent is commissioned (prompts/skill-agent.md, Tuesdays
in Actions). One skill per run: pick the strongest un-extracted claim
cluster, draft the skill with provenance frontmatter and claim-id
citations after the gold specimen, include a five-prompt trigger test
in the PR (the market audit found 69 percent of public skills never
fire, and the differentiator dies if ours join them), and flag library
rendering gaps to the engineer. Read-only database access comes from
an owner-created NEON_RO_URL secret; absent that, runs do the
non-database work and say so. The ADR-13 panel remains the judge of
record once live; until then the owner's merge gates gold, as
everywhere. Writable surface: skills/, prompts/skill-extract.md, and
ledger entries only.

## ADR-23: A frontend engineer verifies the product visually

Owner's decision (2026-09-18): the ninth seat. A weekly frontend
engineer (prompts/frontend-agent.md, Wednesdays in Actions) owns how
the product looks and feels on every screen, from iPhone to iPad to
desktop, and its defining rule is the owner's: verification is VISUAL.
The run builds the site, screenshots every page at three viewports
with Playwright, and the agent reads the rendered pixels before
judging anything; a page is never fine because the code reads right.
It fixes what it sees, benchmarks best-in-class AI product sites for
interaction craft (the owner's named exemplar: Elicit's satisfying
bouncy hover), implements at most two verified polish refinements per
run translated into the fixed B&W Apple-clean identity, and ships
before-and-after screenshots in the PR as evidence. Hard protections:
the hero mark's owner-approved geometry is untouchable without her
word, no color enters the palette, sprint feature builds stay the
engineer's. Same authority as every seat: one PR per run, owner's
merge, lane-bounded writes (site/, docs/design/, ledger, board).

## ADR-24: Finance and sales seats, created dormant

Owner's decision (2026-09-18): two more seats exist on paper before
they exist on a schedule. The finance agent (prompts/finance-agent.md)
keeps the books: a measured OPEX ledger proving the $0 principle, then
revenue and unit economics once sales begin; it never sees credentials
or moves money, and figures it cannot measure it asks for. The sales
agent (prompts/sales-agent.md) builds campaigns, launch sequences, and
outreach material under one law: it prepares, the owner sends; it
never contacts anyone, posts, or creates accounts, because the company
speaks in one voice, hers. Both workflows are workflow_dispatch only,
no cron, until the owner activates them; activation is a one-line
schedule addition. The PM's charter gains the org chart
(docs/agents/org-chart.md), the one-page view of every seat, active
and dormant, and the company initiative each serves.

## ADR-25: The weekly seat is the research agent

Owner's decision (2026-09-18), on the chair's recommendation against
adding a twelfth seat: the function she described as a product
researcher (evaluate what input serves the mission, guide the engineer
and skill seats by what is gaining citation traction and reputation,
find new sources and researchers beyond arXiv) already lived in the
weekly meta-review seat, which consumed discovery_report, proposed
sources.yaml diffs, and reviewed what the pipeline read. The seat is
renamed the research agent (prompts/research-agent.md,
agent-research.yml, research/ branches) and gains the one output that
was missing: the weekly CURATION BRIEF (docs/research/briefs/),
ranking what is rising by evidence, naming extraction targets for the
skill agent, and warning what is noise. The PM plans from it. Skill
drafting stays with the skill agent; one seat decides what is worth
reading, another what is worth packaging, and the engineer builds.

## ADR-26: Decision 11 resolved, the release gate is a four

Owner's decision (2026-09-18, closing the open question from the
2026-09-17 all-hands): the release gate drops from a benchmark score
of five to a four, and the October 13 launch date holds. The bar is
the OKR seat's five-axis benchmark (speed to the frontier, judgment,
actionability for a reader, actionability for an agent, product
surface), scored against real competitors, harshly. Until launch the
company's focus is essentially the product: validated digests, tested
skills, live data, real content. Surface area, plumbing, and anything
that does not move the benchmark toward four waits. This supersedes
the provisional phased-gate assumption the PM triage run of
2026-09-18 planned under; where that run's outputs reference the
phased gate, this ADR is the ruling. Consequences the seats already
named: the OKR seat's October run scores against one target, the
skill seat learns whether known gaps ship by whether the benchmark
reaches four with them open, and the market seat keeps positioning
claims inside what the product actually is at launch. Owner logistics
running alongside, in her hands: the Stripe account (an email
conflict is being resolved), then the domain purchase. The finance
seat activates at the first real expenditure and books it, CapEx and
all four questions, from receipts she reports, never from access.

## ADR-27: Seats get one shared GitHub App identity

Owner's decision (2026-09-18), choosing option 1 of the agent-identity
analysis (Entra Agent ID's idea, translated to where the seats live):
the eleven seats will act through ONE shared GitHub App instead of the
owner's personal tokens. The App is a first-class principal: commits
attribute to the App's bot name rather than to her, tokens are minted
short-lived per run, permissions are fine-grained (contents, pull
requests, workflows), and revocation is one click that touches nothing
personal. Holding the `workflows` permission, the App also closes the
long-open workflow-scope PAT question: seats gain the ability to fix
their own machinery through ordinary PRs, and the owner's merge gate
remains the authority boundary exactly as before. Per-seat Apps (full
least-privilege, one badge per seat) are the anticipated second step,
deliberately deferred until the shared App proves out. Implementation
waits on the owner's two-minute App creation; the chair wires token
minting into the workflows once APP_ID and APP_PRIVATE_KEY exist as
secrets. PROJECTS_TOKEN stays as-is for the board. Machine users and
per-seat PATs were considered and rejected; real Entra with OIDC
federation was noted as the enterprise-grade version worth watching,
not adopting.

## ADR-28: The writer seat, editor-in-chief

Owner's decision (2026-09-19): a twelfth seat owns the words as a
craft, because she was frequently dissatisfied with the newsletter's
writing and structure and the root cause was ownership: the engineer
owned the pipeline, research owned the content, frontend owned the
pixels, and nobody owned the prose. The seat is an EDITOR, not a
scribe: it never hand-writes issues, which would break the autonomy
tiebreak; it owns the writing system instead. Three files mirror the
design system's proven pattern: docs/voice/canon.md (the register,
references from Morning Brew, Matt Levine, The Economist, and
Stratechery, and ten laws), docs/voice/ban-list.md (the enumerated
prose tells, appended as slop drifts), and docs/voice/taste.md (her
editorial rulings, permanent). The daily loop: read the newest issue
cold, grade it against the laws with quoted evidence, and patch
prompts/digest.md, the prompt that actually writes every issue, so
the generator itself improves. Runs daily on Opus after the digest
publishes, one PR, owner merge. Charter prompts/writer-agent.md,
workflow agent-writer.yml. The pre-send gate idea is deferred until
the daily cadence exists in the pipeline; carded for the engineer.

## ADR-29: The zero-gap mandate

Owner's decision (2026-09-19): "Hugging Face was just one example of
a gap. I want 0 gaps going forward." The mandate, made operational:
a gap is anything the org is UNAWARE of, cannot REACH, has not
PROCESSED, or does not ENFORCE, in territory it claims. Consciously
declining coverage is not a gap; not knowing there was something to
decline is. Since no system can promise a gap never opens, the
enforceable promise is that no gap survives a detection cycle, and
every class has a named hunter:

1. **Awareness gaps** (the world knows, we don't — the HF incident).
   Hunters: the signal feeds (ingested), the market seat's weekly
   competitor coverage-gap check, the research seat's weekly signal
   read. Detection cycle: one week.
2. **Reach gaps** (relevant work our sources structurally cannot
   see — cs.CR's 45% non-cross-listed agent-security papers).
   Hunter: the research seat, MONTHLY source census measuring
   sources.yaml against external ground truth exactly the way the
   containment brief did (live-API sampling of what a category
   carries versus what we can reach). Detection cycle: one month.
3. **Processing gaps** (owned but never looked at — the 2,445-paper
   untriaged firehose, 64% of the corpus). Hunters: the engineer's
   pipeline-health observation and a standing metric the PM carries:
   percent of ingested corpus triaged, reported every Monday until
   100 and watched thereafter. Detection cycle: one week.
4. **Enforcement gaps** (ruled but not checked at the artifact —
   incident 20). Hunter: the ExO, whose recorded-is-not-enforced
   audit generalizes the check to every register. Detection cycle:
   every ExO run.

Every detected gap is an incident-register entry with its class
named, however small, per the owner's standing repeated-issue rule
and the diagnosis-over-a-minute rule. The OKR seat's October run
must carry a coverage key result derived from these metrics, so the
mandate is scored, not remembered. The benchmark's "speed to the
frontier" axis now explicitly includes "was anything major missed,"
judged against competitors and the month's news in retrospect.

## ADR-30: Payments through a Merchant of Record, not Stripe direct

Owner's decision (2026-09-19). She is not a US resident and Stripe
does not support Guatemala; a US mailing address does not change the
legal entity Stripe verifies, and building on a mismatched entity
risks a frozen account with funds inside. The paid spine therefore
sells through a Merchant of Record: the MoR is the legal seller,
handles checkout, tax, and payouts, and pays her out. Candidate order:
Polar first (developer-native, Clerk and Next.js integrations, lowest
fee tier), Lemon Squeezy as fallback. Entitlement architecture: the
MoR's webhook writes the paid state into the Clerk user's metadata,
and site/lib/entitlement.js (hasSpine) reads Clerk, so the site never
talks to the payment provider at request time. A US entity (Stripe
Atlas or a Delaware LLC for the parent company) stays on the table as
the long-term move once volume justifies Stripe's lower margin; that
is a parent-level decision, not a launch blocker. The runway's
"Stripe account by Sep 26" deliverable is replaced by "MoR account and
webhook by Sep 26".

## ADR-31: The paid plan's shape — trial, monthly, lifetime

Owner's decision (2026-09-19), refining ADR-30's Merchant of Record
setup. The paid spine ("Full access") sells three ways:
1. **A 3-day free trial** on the monthly plan, card up front through
   the MoR, converting automatically unless cancelled.
2. **$20 a month**, with the owner's earlier billing principle kept:
   the subscriber chooses recurring, or a non-recurring month that
   simply lapses until they choose to renew ("we would rather earn
   the renewal than collect it", already on the pricing page).
3. **$200 lifetime access**, one payment, permanent entitlement.
The chair's flag, recorded for the finance seat: a lifetime tier
sells ten months of revenue for a lifetime of service, so it is a
launch-liquidity instrument, not a steady-state price; finance
models its breakeven and the OKR seat's benchmark watches whether it
cannibalizes monthly. Entitlement stays one flag on the Clerk user
(hasSpine), set by the MoR webhook for all three, with the lifetime
tier setting it permanently and the trial setting it with an expiry
the webhook later confirms or revokes. The pricing page copy follows
the writer seat's site-copy rules; the site's current "Opens
October 13" pills become the three offers.
## ADR-32: Accounts via Clerk, Neon as system of record, door-closed launch

**Status.** Accepted 2026-09-19, owner-directed. Chair-authored in parallel
with ADR-30 and ADR-31, which settled the payments half (Polar as MoR,
plan shape) independently and consistently; this record keeps the
identity half and the launch posture, and defers to ADR-30/31 on
payments wherever they overlap.

**Identity: Clerk.** Already the de facto choice — `@clerk/nextjs` 7.9.4,
`clerkMiddleware()`, and the sign-in/sign-up routes are in the tree. This
ADR ratifies it and names what was missing: Neon is the system of
record. A `users` table keyed by `clerk_id` holds the durable graph, so
Clerk stays a swappable surface rather than a dependency (the company's
law from epito.me ADR-6: integrations are surfaces, never dependencies).
Migration away means re-issuing credentials by email re-auth, never
losing users or their history.

**Payments: Polar, as Merchant of Record.** Not Stripe: Stripe operates
in 46 countries and Guatemala, where the owner is based, is not one of
them. Using Stripe directly would require incorporating in a supported
country — a corporate-structure decision, not a migration, and deferred
until revenue justifies it. Not a storefront (Shopify et al.): there is
no catalog. Alexandria sells one $20/month subscription, which is the
payments category.

Polar is the Merchant of Record, which means Polar is the legal seller:
it registers, collects and files VAT and sales tax worldwide, issues
invoices, and absorbs refunds and chargebacks. Verified 2026-09-19 to
pay out to Guatemala via Stripe Connect Express. Fee ~4% + 40c,
revenue-contingent, so $0 until someone pays. Lemon Squeezy (~5% + 50c,
bank/PayPal payouts, Stripe-owned) is the fallback if Polar's smaller
size proves a risk.

The owner still owes what no processor can assume: a privacy policy and
terms as data controller, and Guatemalan income tax on what she
receives.

**Launch posture: door closed.** The accounts plumbing is built now; the
free digest ships publicly with no accounts, since it is the acquisition
engine by the distribution plan and needs none. Public signup and
payments open as a separate, later decision, on evidence.

**Consequences.** The `users` table, a Clerk webhook syncing
`user.created` into Neon, linkage of existing `subscribers` rows by
email, and a gating helper are engineer work. Per-user MCP identity (the
server is single-passphrase today, ADR-11) is the immediate follow-on:
it is what makes the paid tier reachable from inside Claude. Third-party
machine principals (Clerk M2M tokens) are a ledger idea, not launch work.

## ADR-32: The press writes on Kimi K2; sovereign hosting is the destination

Owner's decision (2026-09-24). Groq's free tier can no longer carry
the press (incident 24: every remaining free model has an 8K
per-request ceiling and the generator prompt alone is 9,865 tokens).
The press's single writing call moves to Kimi K2 through the
Moonshot API the owner funded on 2026-09-20: open weights, 256K
context, no per-request wall on a prepaid account, roughly $0.05 an
issue. The corpus crons (triage, distill, interpret) stay on Groq's
free tier, where their small prompts fit. The PM's failures on Kimi
(incident 23) do not bear on this: those were 30-turn agent loops
under a harness, and the press is one prompt in, one issue out, no
tools, graded by the writer seat the next morning. Finance books
Moonshot usage as a direct alexandria cost. The destination, on the
post-launch roadmap next to the router evaluation: SOVEREIGN HOSTING,
the model served by alexandria itself (vLLM on Modal, an open-weight
writer such as gpt-oss-120b or Qwen3), so no provider can withdraw
the press's model again. Groq's role stays as it was: the corpus's
brain, not the company's.
