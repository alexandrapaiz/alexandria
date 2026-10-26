# Engineer run note, 2026-10-25 (hook, graph slice 2)

Woken by the capacity-return hook. This seat's previous run of the day, #514,
opened its draft pull request and was refused by the provider limit before it
wrote anything, so it shipped a six-line run note and no work. This run
supersedes it, contains its commit, and did the slice it named. #514 is closed.

## What shipped

Slice 2 of `docs/product/graph-quality.md`, the accepted ledger entry
"Knowledge graph upgraded to industry standard". The shortlist in
`pipeline/interpret.py` stops deciding the graph's density: same-paper
candidates are excluded, `NEIGHBORS` is 10 rather than 5, and a distance floor
lets a shortlist come back shorter than its limit instead of padding itself
with claims the embedding has already called unrelated.

The retrieval had never been tested. It is `SHORTLIST_SQL` now, with
`tests/test_shortlist.py` behind it: nine live assertions against a real
cluster with pgvector, verified by deleting each clause in turn.

Two things found on the way rather than planned. The cap's cost comment had
been stale since `prompts/interpret.md` grew, so the spend ceiling was computed
from a request smaller than the one being sent, and the same defect is live in
`pipeline/triage.py`. That is filed as `INC-2026-10-25-a-cost-comment-goes-stale-in-two-production-jobs-at-once`
and as a ledger entry, fixed here for interpret only. And the audit's density
metrics now read `latest_links`, which is the question slice 5 explicitly
deferred to this slice.

## What is owed

The done-condition's two snapshots need a database credential no seat holds,
which is the ledger entry of 2026-09-28. The run reports the retrieval-side
half of the same question to its own log instead.

The reservation moved from 600 to 1,000 tokens, which
`docs/agents/runtime-changes.md` makes a runtime change, so
`modal run pipeline/interpret.py::rehearse` is owed before this runs in
production. It cannot be run from a seat sandbox, and the Modal workspace is
switched off today, which is this seat's own second `This sprint` card.
