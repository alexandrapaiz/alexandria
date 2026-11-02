## INC-2026-11-02-a-paper-called-unreadable-for-thirty-three-days-was-one-url-away - a reader with one route wrote its own failure into a register as a property of the literature (2026-11-02, research seat, message wake after a merge)

**What happened.** `docs/research/reading-queue.md` carried a line, queued by
`skills/context-window-engineering` on 2026-09-30 and open for 33 days, that
read in its own words: "arxiv:2609.07103, Revisiting Complete Reasoning Traces
for Post-Training, publishes no full HTML and was read at the abstract only,
for the second run running." It then offered the seat a choice between two
expensive options, get the PDF into the corpus or mark the skill's convergence
as resting on one paper rather than two.

Neither was needed. The paper publishes a full HTML rendering at
`ar5iv.labs.arxiv.org/html/2609.07103`: 266 KB of markup, 78,295 characters of
text, the author list, all eight tables, and two appendices the abstract does
not hint at, one of which is the only inference-time experiment in the paper
and therefore the only part of it that bears on the skill that queued the line.
`arxiv.org/pdf/2609.07103` also answers 200, and `pypdf` is installed in this
sandbox.

`tools/read_paper.py` tries `arxiv.org/html/<id>` and no other route. For this
id that URL is a genuine 404, and so is its `v1`. The tool then falls back to
the abstract and exits 3, which is correct behaviour for the tool and was read
three times as a statement about arXiv.

**Why it is a repeat.** The queue line says "for the second run running" in its
own text, so the misreading was recorded as having already happened twice
before this run opened the file, and this run would have been the third. The
standing rule at the top of the register says a repeat is recorded at the moment
it repeats, with no exceptions.

**The class, and it is not the fetch.** A single-route instrument returning a
negative result, written down as a fact about the world rather than a fact about
the instrument. The nearest relative in this register is incident 32, where a
pre-send gate ran, found nothing, and its silence was available to be read as
approval. The shape here is the same with the sign flipped: the instrument spoke,
said exactly what it meant, and what it meant was narrower than what two runs
wrote down. Nothing in the line's wording distinguished "we could not fetch it"
from "it does not exist", and a queue line has no field for that difference.

**What it cost.** Thirty-three days of an open line. Two runs that each paid a
fetch and a write-up and left the question where they found it. A skill left
with a withdrawn sentence whose own half-source nobody had read, when the source
in fact confirms the withdrawal and supplies an independent support for a
different sentence in the same file that the skill does not currently carry.

**The repair, and the half of it this seat could do.** The tool's fix is six
lines and it is the engineer's, routed with the patch, because `tools/` runs from
the repository checkout and a merge reaches production without a deploy. The half
this seat can do is a wording rule, applied to the struck line: when a fetch
fails, the queue line says which route was tried, so the next reader knows
whether the paper or the fetcher is the thing that failed.
