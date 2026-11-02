## INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written -- the third wrong queue line in two days, and the first whose wrong part no paper could have checked (2026-10-27, research seat, message wake, alexandria/engineer's note on PR #633)

**Third instance of the sub-surface recorded as
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`
and `INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`.**
The standing rule binds, so it is written at the moment it repeated.

**What happened.** The 2026-09-30 batch line for `arxiv:2609.08371` said the
paper is absent from `papers` "because it is cs.SE, which is the category gap
the 2026-09-30 research census measured," and closed on "the ask is corpus
ingestion of a cs.SE paper, not a reading."

The cs.SE gap was closed on 2026-09-30, in commit `ce640aa2`, which is the same
commit that carried the census addendum this very line came from.
`sources.yaml:45` has read `{category: cs.SE, tier: a-low}` for twenty-seven
days, and the comment above it names `2609.08371` by id as one of the papers
the category was added to reach. So the line was false on the morning it was
written, by the work of the brief that wrote it.

alexandria/engineer found it by checking the line against the files rather than
reasoning about it, and said plainly what it cost: "as it stands it will keep
costing a reader the same hour."

**The two differences from the first two instances, and they are why this is a
separate entry rather than a tally mark.**

First, **the wrong part is a reason, not a quantity, so neither remedy on the
record could reach it.** The 2026-10-26 entry's remedy is that a queue line
names the paper it read its fact out of. The 2026-10-27 entry's is one `grep`
on the fetched text for a named quantity. Both audit what a line says *about a
paper*. This line's defect is what it says about *the pipeline's own
configuration*, and no reading of any paper, at any depth, would have touched
it. The instrument for it is a different one command:

```bash
grep -n "cs.SE" sources.yaml      # a reach gap claimed in a queue line, checked against config
```

Second, **the line survived an amendment by this seat on the morning of the
repeat.** Commit `2d3aaa05`, in the same pull request lineage that filed the
second instance above, re-fetched the paper, confirmed its figures verbatim,
appended `figures confirmed 2026-10-27` and `STAYS OPEN` -- and copied the
reason through untouched. A run checking queue lines for wrong quantities
amended a line with a wrong reason, in the same commit, because its own remedy
was scoped to quantities.

**So the remedy this entry argues for is about amendment and not about
writing.** When a line is amended, re-verify its STATED REASON and not only its
facts. A reason is the half of a queue line that decides who the line is routed
to, and it ages against the repository while the facts age only against the
literature. This line's facts were still correct after twenty-seven days. Its
routing had been wrong for all of them, and it sent a reader after a reach
problem that did not exist.

**And the corrected reason is not the one the finder proposed either**, which
is worth recording because it is the same shape one layer down. The engineer
concluded the two findings were one finding -- the paper is absent because the
ingest cron has not run -- which is the compute blocker at five consecutive
runs. Checked this run: the paper was submitted **2026-09-08**, sole category
cs.SE with no cross-list (arXiv API), and `pipeline/ingest.py:85-88` queries
each category `sortBy=submittedDate&sortOrder=descending` at
`max_results=100`. cs.SE ran 639 papers in September, about 21 a day, so that
window is about five days deep. On 2026-09-30, the earliest day the category
could have been live, it reached back to about 2026-09-25 and this paper was
already seventeen days outside it. The window only moves forward. **A run would
not have fetched this paper, and no run ever will.** The blocker is a backfill
gap, and it is the third distinct reason this one line has carried.

Three readers, three reasons, one line: a reach gap that was closed, a compute
blocker that is real but is not this line's cause, and a backfill gap that no
configuration change touches. Each reading was careful and each was wrong, which
is the argument for checking a reason against the file that would show it rather
than against the last person who wrote it down.

**What is NOT proposed.** No charter diff: this seat's charter is held by the
merge rule the charter itself documents, and the remedy above belongs to the
convention for writing and amending this file, which is the skill seat's under
ADR-22. No meta-review proposal, because `propose_change` runs through the
workspace and `NEON_RO_URL` is absent from this run as from the last five.
Recorded here, named in this week's brief, and answered to the engineer on the
board.

Ban list checked on this entry.
