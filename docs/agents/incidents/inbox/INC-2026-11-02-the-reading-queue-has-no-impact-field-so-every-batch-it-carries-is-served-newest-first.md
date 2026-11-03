## INC-2026-11-02-the-reading-queue-has-no-impact-field-so-every-batch-it-carries-is-served-newest-first - the relevance law has no instrument inside the one file that decides what gets read, and the chair's own batch is ordered against it (2026-11-02, research seat, PR #760)

**What happened.** This run drained the chair's RLVR batch in
`docs/research/reading-queue.md`, 24 open lines queued on 2026-10-05 under
"make sure the corpus includes RLVR", 28 days open. The five lines the queue
marks `NEXT`, and therefore the five a returning distill run would read first,
hold **1, 0, 0, 0 and 0 citations**. The paper with 12, which is 2.0x the
runner-up on citations per day as well as on raw count, sits twenty-first of
twenty-four.

Measured this run with one Semantic Scholar batch call; the command, the full
24-row table and the age normalization are in
`docs/research/notes/2026-11-02-rlvr-chair-batch.md`.

**Why it is in this register rather than only in the note.** The relevance law
in `prompts/research-agent.md` says every ranking this seat produces orders by
evidenced impact and uses recency only as a tiebreak, and says in its own words
that "the owner has had to state this rule repeatedly" and that "a ranking that
reads as a release-date feed violates it". Every recorded instance of that
class has been a document a seat wrote: a brief, a set of extraction targets, a
source proposal. **This is the first instance inside an instrument**, which
makes it the first one that repeats without anybody deciding anything. A seat
that writes a release-date brief can be corrected. A queue that serves
release-date order serves it to every run, forever, and no seat is making the
error.

**Where the defect is, stated precisely so it is not aimed at the wrong file.**
Not at `pipeline/reading_queue.py`. `pending()` groups blocked skills first and
otherwise preserves file order, which is the right behaviour for a file whose
contract is append-only and whose format is documented at the top. The asker
token is not the problem either: `ASKED_BY` takes one whitespace token so
`asked by the chair` parses as `the`, and the module's own comment at lines
46-57 says exactly that, isolates it from every decision through
`SKILL_ASKER`, and names the 2026-10-05 occasion when it was load-bearing. That
was checked before being reported, and it is working as designed.

The defect is that **no stage between "a line is appended" and "a distill run
takes the first six" has any impact signal to sort on.** The documented line
format is `arxiv:<id> -- why -- asked by <who> -- YYYY-MM-DD`: an id, free
prose, an asker, and a date. Four fields, and the only orderable one is the
date. So when 27 ids arrive in one batch the order that survives is the order
they were typed, which for a chair pasting a month of arXiv listings is
newest-first, which is least-traction-first by consequence.

**What it cost, and the part that is not recoverable.** `MAX_PER_RUN` is 6. On
the queue's order the first distill run after the workspace returns would have
spent its whole budget on five zero-or-one-citation papers plus one more, and
the two papers that carry 18 of the batch's 32 citations would have waited
three more runs. Both of those two are on-policy distillation against RLVR,
which on this evidence is the live question in the layer, and the eighteen
lines ahead of them are eighteen separate policy-optimization objectives
holding 11 citations between them with nine at zero. The unrecoverable part is
the 28 days: the batch could have been measured on the day it was queued, by
the same one command, and the measurement would have been the same.

**The fix, routed rather than built.** One field, not a rewrite: a queue line
that carries a traction number can be sorted by it, and the number is one batch
API call for the whole file rather than one call per line. `tools/read_paper.py`
already proves a seat host can reach arXiv unauthenticated; the Semantic Scholar
batch endpoint answers 200 from the same host where its single-paper route
answers 429, so the batch route is the one to build on. Routed to the engineer
in the board reply, because `pipeline/reading_queue.py` is not in the ADR-12
whitelist this seat may propose into.

**And the half this seat could do without waiting**, done in PR #760: the
batch's own lines now carry the ranking, so the next drain reads the six
highest-traction lines first whether or not the field ever exists. That is a
patch on one batch and it does not generalize, which is why the field is still
owed.

**The generalisable half.** A law that binds the documents a seat writes and
not the instruments it reads will be obeyed exactly where it is cheap and
broken exactly where it is structural. The reading queue is the second register
in this repository found enforcing nothing while naming the right thing, after
the taste ruling of incident 20, and the shape is the same both times: the rule
was written into the place that decides what gets recorded, and never into the
place that decides what gets served.

Ban list checked on this entry.
