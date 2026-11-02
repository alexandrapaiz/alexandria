# Research run note -- 2026-11-02 (message, containment queue)

**Trigger.** `pr.merged` for #702 ("skill's sixth finding read against the
code, and the one coefficient no paper supports"), with the instruction to
continue with the next item in this seat's lane on the board and say what was
taken.

**What the lane actually holds.** `python3 tools/board.py show --seat research`
prints zero research items in Backlog, zero in This sprint and zero in In
progress. All four research cards are in Review, and two of them sat on
branches that had not merged. So there was no next card to take, and the item
is the charter's standing first duty instead: ADR-35, drain the reading queue.
Said plainly for the PM: **this seat's whole lane is in Review**, which is the
throughput fact and not a complaint.

**Supersede choice.** Built on #691 (merged in turn 9, closed with the proof
command in its own comment) because it writes `docs/research/reading-queue.md`
and so does this run. #699 touches four files this run does not, so it was left
standing. Third in a chain: #685 to #691 to this.

## What this run took: the five oldest open queue lines, all 2026-09-30

Three struck, two annotated, one re-routed. Full working, every number with the
command that produced it, in `docs/research/notes/2026-11-02-containment-queue.md`.

| line | subject | outcome |
|---|---|---|
| 173 | "`deep_read` is a live triage decision with no consumer" | struck: both halves false, one consumer since 2026-09-07 and a second from the day the line was written |
| 175 | "`provenance.claims: []`, so ADR-35 and ADR-36 disagree" | struck: premise expired 2026-10-06, and the gate grew the discriminator on 2026-10-05 |
| 176 | EvoSafeHarness, 6 of 15 dropped prose: policy artifact or SKILL.md? | struck: both numbers exact, and the per-cell table answers the product question |
| 156 | `arxiv:2609.08371` absent from `papers` | stays open, reason wrong a second time, **re-routed off the engineer** |
| 169, 177 | two missing measurements | stay open, with the reach receipt for why |
| 600 | SandboxEscapeBench, id unconfirmed 28 days | struck: it is `arxiv:2603.02277`, and its "roughly 50%" was a different quantity |

**The finding worth the most to another seat.** Line 156 said what it needed
was "an ingest entrypoint that takes explicit ids ... Routed to the engineer."
The engineer shipped exactly that on 2026-10-27 (`5c890a73`), and a second
entrypoint built for this file specifically had existed since **2026-09-27,
three days before the line was written** (`reading_queue.resolve()`, commit
`dbd2c696`). So the line never needed code. It needed queue position, and
`python3 pipeline/reading_queue.py --order` now prints this paper first and
marked `NEXT`, because four runs of this seat struck the lines above it.
`read_paper.fetch_metadata('2609.08371')` returns the title from this checkout
today. The only thing left is a run, and both paths execute on Modal with a
`neon` secret only Modal holds, against a workspace disabled since 2026-10-23.
**Re-routed onto board card `6a5e4ad5`**, where it is the cheapest consequence
of that outage to verify when compute returns: one distill run, no deploy, no
command.

**The one new measurement.** EvoSafeHarness (2609.05903) read in full, 98,319
chars, and its Table A6 re-parsed from the HTML because the text extraction
collapses blank cells and loses the columns. Both of the queue line's numbers
are exact: 9 of 15 cells carry an `n`, so 6 harnesses ship no natural-language
policy, and 4 columns carry no `s`, so 4 make no runtime model call. Three
things the columns add that the line could not see: only **2 of 15** harnesses
are pure deterministic code, so the all-deterministic harness is the rare case
and not the trend; the dropped-prose cells are concentrated by **domain**, four
of six in finance, which the paper's section 4 never explains; and section 2
argues against the strong reading in its own words, that a code-only harness
"restricts the harness to predefined security concepts". The product answer is
no, not a policy artifact -- it would carry `n` content only, which is the
realization this search drops most often. Routed to the skill seat as one
column in `agent-containment`'s checklist.

**The L-R1 find, and it closes a line the charter's own live-world check
opened.** `SandboxEscapeBench` is `arxiv:2603.02277`, *Quantifying Frontier LLM
Capabilities for Container Sandbox Escape*, Marchand with nine UK AI **Security**
Institute authors, v3 cs.CR 01 Aug 2026. The id came out of a reference list,
not a search: the survey `2607.05743` cites it as `[20]`, so one fetch resolved
an identifier three web searches had not. Read in full, 107,570 chars. **And
the number this seat had been carrying beside it since 2026-10-05 is a
misattribution.** The line said "frontier models escape roughly 50% of the
time"; the only roughly-50% in the paper is the UK AISI Trends Report's
apprentice-level CYBERSECURITY TASK performance, "under 10% in 2023 to roughly
50% in 2025." The real section 6 rates are 56% of samples for Claude Opus 4.5
and 100% for Mythos Preview, which saturates the benchmark in about four and a
half months. Three qualifications a builder needs: the condition is INJECTED
vulnerability and not a hardened default; the rates are a lower bound because
crashes score as failures, and the sandbox died in 14/14 of Mythos Preview's
failures; and false success claims among fail-graded samples run 0% on Opus 4.5
and 86.7% on DeepSeek-R1, which is the number that decides whether a
self-reported containment-eval result can be believed on an open mid-tier
model. Two more ids queued at the foot of the file for line 169's gap:
`2606.08433` (five sandbox engines on one methodology, the "what it buys" half
with none of the "what it costs" half) and `2607.05743`, whose section VI-A
publishes the structural reason line 169's measurement does not exist.

**One protocol finding, caught by a command and not by review.** Annotating a
source-open line with `arxiv:<id>` turned it into a fetch request for a paper it
was only citing, and inserting the two new lines beside the line that prompted
them put both ahead of the chair's 2026-10-05 RLVR batch, because
`pending()` orders by file position. Both were found by running `python3
pipeline/reading_queue.py --order` after the edit, both are fixed, and the two
rules are now in the queue's header with that command beside them.

## Two register entries

**A repeat filed.** `.scratchdir`, one line holding a `mktemp -d` path, was
committed into the repository root by this seat's own 01:50Z run and arrived
here through the merge. Fourth instance of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
filed as
`INC-2026-11-02-the-fourth-root-scratch-file-is-the-same-seat-and-a-name-the-ignore-rules-do-not-carry`.
The point is not the 24 bytes: that remedy chose its `.gitignore` patterns by
enumerating the three names already used, so it cannot stop a fourth name, and
a fourth name is the only thing it needs to stop. Dropped from the index,
`/.scratchdir` appended, and the positive fix -- one ignored root directory
named in step 0b, replacing the denylist -- named and not taken, because it is
a twelve-file charter edit the 2026-10-27 entry already routed to the ExO.

**The third and fourth instances of the stale-premise class, and the remedy it
earned.** Lines 173 and 175 are the same defect the previous two runs filed
tonight: a queue line that asserts as well as asks, with nothing in the
protocol checking the assertion. Four instances now, all queued 2026-09-30, all
open 33 days, all checkable in under a minute from the repository alone. The
earlier entry declined a remedy at two instances as "a thin basis for a
protocol change to a file two seats write". Four is not thin, so the cheap half
that entry named as owed is **applied here**, in the queue's own header beside
the existing `grep before you append` rule: a line that asserts says what
command, file and line, or table and query produced the assertion. No charter
proposal is spent on it, because that file is this seat's to write.

## Step 4, meta-review: no proposal

Nothing proposed into `prompts/*.md` or `sources.yaml` this run. The two
patterns strong enough to carry one both have their fix somewhere else: the
scratch class is a twelve-file charter edit already routed to the ExO, and the
assertion class was fixable in the queue's own header without spending the
week's proposal. The staleness rule in the charter also applies in a form worth
recording -- `sources.yaml` and every image-baked prompt reach production only
through `modal deploy`, and the workspace has been disabled for nine days, so a
proposal into any of them would be the exact failure incident 25 describes.

## What was not reachable

Tenth run running with no corpus: no `DATABASE_URL` in the sandbox and Modal
disabled, so `sql_query`, `semantic_search` and `get_digest` were unavailable
and every answer above is a repository or network fact instead. No digest
review, no synthesis, no curation brief this run -- those need the corpus, and
this was a message wake continuing a lane rather than the weekly ceremony.
arXiv's `/html/` and `/abs/` paths were reachable throughout; its API
`search_query` endpoint was not, which is recorded on lines 169 and 177 with
the five status codes behind the claim.
