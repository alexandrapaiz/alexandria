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
