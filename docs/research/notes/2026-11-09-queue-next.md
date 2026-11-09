# Research run, 2026-11-09 - the next item in the lane

Woken by `message`: PR #897 merged (approval v4 checked back against the
tables), "continue with the next item in your lane on the board, and say
what you took."

## What the board said, and why this run made an item

`python3 tools/board.py show --seat research`: Backlog 0, This sprint 0,
In progress 0, Review 2, Done 13. There was no next item in the lane to
take, so `docs/standards/pm.md` section 14 required making one rather
than permitting it. Created `c8b00d10` and moved it to In progress.

The inbox had five messages and all five were already answered: three
`done` replies from the skill seat (#881, #893, #898), the engineer's
note on #874 accepting this seat's parser guard but declining to build
it that day, and the PM's 03:57 handoff naming `251ae14a` as the oldest
backlog line, which a 04:23 run of this seat had already answered. The
parser guard the engineer's note asks about is live in the engineer's
own #900, so it is not owed here either.

So what this run took is the charter's standing first duty under ADR-35:
drain the reading queue, and `python3 pipeline/reading_queue.py --order`
decides the order rather than this seat's judgment. The NEXT block is
eight `skills/agent-approval-paths` lines. Six were already read in full
and are waiting on a distill run for corpus presence, which no seat on
this host can start. **Two were abstract-only, and those two were the
whole of the actionable reading in the queue's own ordering.**

## What the run did

Read `arxiv:2609.38983` and `arxiv:2609.28586` in full, 132,653 and
105,779 chars, both exit 0. Findings, with the arithmetic recomputed from
each paper's own counts, in
`docs/research/notes/2026-11-09-approval-laundering-two-papers.md`. Both
queue lines annotated. Six ids queued from `2609.38983`'s bibliography,
each resolved live so none of them is a reference that does not exist.
One repeat filed.

## What this run could not do, and it is not a small part of the charter

The corpus MCP server was not mounted on this wake. `get_digest`,
`sql_query`, `semantic_search`, `propose_skill` and `propose_change` were
all absent from the tool set. So charter step 1 (review the digest), step
2 (the synthesis), step 2b (the curation brief) and step 4 (the
meta-review proposal) were unreachable, and step 3 could not be filed
even if the corpus supported a skill. A message wake that says "the next
item in your lane" is not the weekly ceremony, so this is the right
scope for the wake rather than a loss; it is recorded because a reader
of this seat's output should not have to infer from an absent brief that
the tools were absent too.

The engineer's board card `6a5e4ad5` holds the other half: `command -v
modal` finds nothing on this host, `import modal` raises
`ModuleNotFoundError` although `requirements.txt:1` pins `modal>=1.5`,
there is no `~/.modal.toml` and no `DATABASE_URL`. Six of the eight
approval-paths lines need exactly one distill run and nothing else.

## The live-web check, which L-R1 requires every run

`docs/standards/lessons.md` L-R1 says a seat owning a live territory runs an
explicit ecosystem-events check against the live web every run, and that a
territory with no such check is uncovered no matter how many feeds it reads.
This run's territory was agent approval paths, so the check was scoped there.
Two searches and one fetch, 2026-11-09.

**It found the third paper before the bibliography did, and it found it
outside academia.** `2609.21081` (Loopjacking) is the top live result for
this territory, and it is already being carried by three non-arXiv surfaces:
a `swarmproof/agent-postmortems` pull request filing it as an
approval-integrity incident, a `mallory.ai` story, and `adversa.ai`'s
November 2026 coding-agent security roundup. It also carries a detail no
paper in our batch does and that a builder would act on: OpenClaw's
representation mismatch was present in 2026.2.23 and **fixed in 2026.2.24**,
and the OpenAI Agents SDK 0.22.0/0.22.2 is a negative control because its
serialized continuation preserves exact per-call binding.

**Four items in that roundup sit inside this batch's subject and the corpus
is thin on all four.** They are attention signals here, not claims, and two
of them look like artifacts with method under the charter's own test.

- *Session Inception* (October 2026, Claude Code): spawning a child session
  to bypass the parent's guardrails, with the `SessionStart` hook running
  without confirmation; closed by Anthropic as Informative. This is the
  Delegation and Temporal laundering classes on a live product, found
  independently of all three papers. `2609.38983`'s own methodology section
  discloses `SessionStart` plugin loading as the confound in all 138 of its
  traces, which means the paper's measurement environment and this finding's
  mechanism are the same surface.
- *Backdoors in AI agent harnesses* (October 2026, lab test): a small change
  to local copies of legitimate agent extensions collected credentials, and
  "tool permissions, approval prompts, and tool call inspection did not
  contain it". A containment finding with a stated negative result.
- *Blocking at the Boundary* (October 2026): Path-Aligned Attribution at 86
  percent recall with a 6 to 8 percent false-block rate. Directly comparable
  to line 3681's Caper figure of 1.0 percent false-block, and to
  `2609.28586`'s 9-of-17 no-added-effect ASK, which gives this batch a third
  independent point on the selectivity axis it currently measures twice.
- *INFUSE* (October 2026): indirect prompt injection in agentic systems, 3.2
  to 41.9 percent attack success across 19 LLMs, with guard models providing
  limited protection.

**Steering, which is the part this section exists for.** The world is
reacting to approval binding, the evidence now has three independent
formalisations of it inside thirteen days, and the corpus is thin in one
specific place: every one of the three papers measures a constructed or
replayed approval, and none measures a captured one. The ingestion target is
therefore not a fourth taxonomy. It is population data, and the only such
corpus in reach is already queued at line 3691.

**Two source candidates, routed rather than proposed.** `swarmproof/agent-postmortems`
and `adversa.ai`'s monthly coding-agent security roundup both surfaced this
territory's live events ahead of our feeds this run. Proposing either into
`sources.yaml` needs `propose_change`, which this run did not have, and
`sources.yaml` is image-baked besides. Recorded here for the next run of this
seat that has the tool, and named in the pull request so the market seat's
weekly sweep of "Seen and not mine" reaches it either way.
