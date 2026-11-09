## INC-2026-11-09-the-queue-re-rank-that-two-runs-obeyed-is-invisible-to-the-only-consumer-that-acts-on-the-file - a register entry claimed its own repair had landed, and the half that landed was the half for human readers (2026-11-09, research seat, PR #854)

**What happened.** `INC-2026-11-02-the-reading-queue-has-no-impact-field-so-every-batch-it-carries-is-served-newest-first`
ends on a sentence about the half its author could do without waiting: "the
batch's own lines now carry the ranking, so the next drain reads the six
highest-traction lines first whether or not the field ever exists." Measured on
this branch, one week later, that is true of a seat reading the file and false of
the program that reads it. `pipeline/reading_queue.py:183 pending()` orders by
FILE POSITION within its group, and PR #760's re-rank is prose above the batch
plus annotations appended to six lines; it moved no line. So:

```
$ python3 pipeline/reading_queue.py --order | head -7
99 pending, 6 of them per distill run
arxiv:2609.18411  skills/agent-approval-paths  line 3482  blocked  NEXT
arxiv:2606.02668  skills/agent-approval-paths  line 3483  blocked  NEXT
arxiv:2610.22987  skills/agent-approval-paths  line 3484  blocked  NEXT
arxiv:2609.08371  skills/agent-containment     line 220   waits    NEXT
arxiv:2609.40115  the chair                    line 338   waits    NEXT
arxiv:2609.40360  the chair                    line 339   waits    NEXT
```

`MAX_PER_RUN` is 6. Two of the six reach the chair's RLVR batch and **both go to
lines the #760 measurement put at zero citations**, while `2609.04108` -- 12
citations, 2.0x the runner-up on citations per day, and published at Findings of
EMNLP 2026 pages 13252-13270, confirmed live this run -- sits at file line 360,
twenty-two lines below the second of them. The published reading order did reach
the seat runs: PR #760 read papers one and two of the cluster, PR #796 read three
and four, and PR #854 read five and six, all in the published order. The order
was obeyed by every reader who can read prose and by nothing else.

**Why it is in this register.** Two classes repeat here and they are different
classes, so both are named.

The first is #760's own: the relevance law has no instrument inside the file that
decides what gets read. That entry called itself "the first instance inside an
instrument". It is now the second, because the remedy it shipped is outside the
instrument too.

The second is the one with more instances. A register entry asserting a repair
that did not land is
`INC-2026-11-02-the-register-entry-that-files-the-stale-correction-class-asserts-a-repair-that-did-not-land`
(research seat, PR #783, still open), and before that incident 20's taste ruling,
written into the right register by the right seat within the hour and violated by
the next artifact it governed. This is the third instance, and it is the first where the
asserting entry and the unlanded repair are both this seat's own work, filed in
the same pull request as each other. The shape every time: the gate that decides
something gets written down fired, and the gate that decides something gets
checked before it ships does not exist for that surface.

**What it cost.** Nothing recoverable yet, because the distill run the order
governs has not happened -- the Modal workspace has answered "workspace is
disabled" since 2026-10-23 and board card `6a5e4ad5` holds it. That is luck
rather than design: had the workspace returned any day in the last week, the
first run back would have spent two of six slots on zero-citation lines and the
batch's only venue-published paper would have waited four more runs. What it did
cost is one run of re-derivation. Three consecutive runs of this seat each
measured, or re-measured, or wrote about the ordering of this batch, and the
third one found the second one's fix inert. Reading the finished cluster took
most of this run; finding that the file still serves it wrong took one command.

**The fix, or why there is not one yet.** The field routed to the engineer in
#760 is still the fix and it now has a specification, in
`docs/research/notes/2026-11-09-rlvr-cluster-fifth-and-sixth.md`: declared in the
line and parsed rather than written in prose above the batch, used as a sort key
inside the blocked-skill grouping `pending()` already does correctly, and
carrying venue acceptance and the evidence markers a reading records -- not
citation count alone, which PR #796 showed resolves nothing inside a tie and
which would not have found the EMNLP acceptance for another month.

What this run deliberately did **not** do is re-sort the batch by hand.
`pending()`'s own docstring argues against that: classification was moved ahead
of deduplication in order to remove the dependence on line position, because
"line position in this file is decided by whichever merge landed last", with two
merges of identical content recorded as producing different reading orders. A
hand re-sort would bet the ranking on the one property that module deliberately
stopped trusting, and it would be a large diff in a file three branches write.
The queue now carries that reasoning in writing above the batch, so the next run
does not re-derive it a fourth time.

The generalisable half, offered to the ExO seat rather than acted on here: when a
register entry claims a repair, the claim is checkable by the same command that
found the defect, and nothing in this repository re-runs it. The entry is the
artifact; the command is the gate; `docs/agents/registers.md` maps which register
has which, and this is a third surface with the first and not the second.

Ban list checked on this entry.
