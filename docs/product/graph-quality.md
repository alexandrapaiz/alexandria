# The claim graph, measured

**Slice 1 built 2026-09-29** (engineer seat). This is the design record for the
ledger entry "Knowledge graph upgraded to industry standard" (docs/ideas.md,
accepted 2026-09-18), whose first step asks for a graph-quality audit with
metrics and an upgrade design doc. The audit shipped as `tools/graph_audit.py`
with `tests/test_graph_audit.py` behind it. This file is the other half, and it
is also the argument behind every bound the tool applies.

The directive, verbatim: the knowledge graph "needs maintenance and to be
upgraded to be industry standard right now it's very junior and behind and
prehistoric and almost like a toy."

That sentence is a judgment about something nobody in this org has ever
measured. `claim_links` has existed since the founding night, three different
models have written into it under at least two prompts, and not one number
about its quality has been produced. So the first slice is deliberately not a
redesign. An upgrade whose before-state is an impression can only be argued
about, and the most likely outcome of redesigning first is a new graph that
nobody can show is better than the old one.

## 1. What the graph is today

Four files hold all of it.

| Piece | Where | What it does |
| --- | --- | --- |
| The edges | `db/schema.sql`, `claim_links` | `(from_claim, to_claim, relation)` as the primary key, plus `confidence`, `method`, `created_at` |
| The judge | `pipeline/interpret.py` | daily Modal cron at 14:00 UTC, oldest claim first |
| The shortlist | `pipeline/interpret.py`, `NEIGHBORS = 5` | pgvector kNN over `claims.embedding` against strictly older claims |
| The rubric | `prompts/interpret.md` | the four relations and what each one means |
| The consumers | `db/schema.sql`, `deprecated_claims` and `site/lib/graph-live.js` | a view gating on an incoming `contradicts` edge at confidence >= 0.7, and the `/graph` page, which reads every edge live |

The design is ADR-10, and two of its properties matter for everything below.
Edges are **append-only**, so nothing is ever corrected in place and a second
opinion is a second row. And they are **time-directional**, so `from_claim` is
always the newer claim, which on a bigserial means the larger id. Re-judgment
was assigned to a slow loop that has never been built.

The vocabulary is four verbs: `supports`, `refines`, `contradicts`,
`duplicates`. Confidence is a real the model writes, and no rubric anywhere
says what a given value means.

## 2. The instrument

```bash
python3 tools/graph_audit.py                  # every metric, for a human
python3 tools/graph_audit.py --json --raw     # the snapshot, to commit
python3 tools/graph_audit.py --sample 40 > sheet.json   # edges to label
python3 tools/graph_audit.py --labels sheet.json        # precision, from the labels
```

It needs `DATABASE_URL` and `psycopg`, it only ever selects, and
`tests/test_graph_audit.py` holds that last property by parsing every statement
rather than by trusting the sentence you just read.

Eleven metrics. Each one is a number a bound can be argued about, and the
argument is in the tool beside the number so the next person can move it.

| Metric | What it catches | Bound |
| --- | --- | --- |
| size | the shape of the thing, claims and edges and backlog | none, informational |
| isolation | interpreted claims with no edge in either direction | 33 percent |
| shortlist ceiling | claims linked to all 5 candidates, so density is set by a constant | 10 percent |
| relation mix | a vocabulary collapsed onto one verb | none, informational |
| confidence calibration | the share of edges carrying one value | 60 percent |
| same-paper edges | a paper agreeing with itself | 40 percent |
| duplicate rate | near-duplicate pairs no judge ever marked | 10 percent |
| contradiction coverage | contradicts edges against the 0.7 gate and the page it feeds | none, informational |
| integrity | self-edges, backwards edges, unattributed edges, pairs both supported and contradicted | zero, any value fails |
| freshness | the newest edge against the daily cron | 2 days |
| judges | edges per `model@prompt_sha`, with dates | none, informational |

Three of those deserve their reasoning in prose, because they are the ones a
reader is most likely to think are arbitrary.

**The shortlist ceiling.** `NEIGHBORS = 5` decides how many candidates a claim
is judged against, so five is the most distinct neighbors any claim can be
linked to on the run that interpreted it. A claim sitting exactly at five is a
claim whose edge count was decided by a Python constant instead of by the
corpus. One claim in ten at the ceiling is tolerable. Three in ten means the
cheapest available upgrade is a larger integer, and every clever change made
before that one is measured against a graph that was truncated.

**Confidence calibration.** `prompts/interpret.md` does define the value. It
says confidence is "your probability that the relation label is right" and warns
that `contradicts` at 0.7 or above deprecates the candidate. What it does not do
is anchor it, because nothing in the prompt says what separates a 0.7 from a
0.9, and a definition with no worked example is the condition under which models
answer the same number to everything. That would be a cosmetic problem except
that `deprecated_claims` gates on exactly this value and the Left-Behind Index
is built on that view. So a flat score does not merely look unscientific. It
decides a customer-facing page by a number the model was asked for and never
taught to vary.

**Same-paper edges.** Two claims distilled from one paper are near-neighbors in
embedding space almost by construction, so kNN hands the judge a paper's own
siblings before it hands it anything from another paper. Those edges are usually
true and worth nothing, because the product's promise is this week's finding
against what we already knew, and a paper agreeing with itself is not that. Each
one also costs one of the five shortlist slots, which is why this metric and the
ceiling metric are read together.

### Precision needs a reader, so it is a worksheet

Whether `contradicts` is correct on a given pair is a reading, and there is no
honest way to get it from SQL. `--sample` draws edges ordered by a hash of a
seed and the edge's own key, which is the one design decision in that query
worth defending: `random()` would look identical in review and would quietly
destroy every before-and-after comparison, because the second audit would
measure a different sample rather than a second judge. With a fixed seed, the
same forty edges come back a month later under a new prompt, and the difference
between the two numbers is the prompt.

`--labels` reports precision overall, per relation, and per confidence band.
The last of those is calibration read straight off the sheet: of the edges the
judge called 0.9, how many were right. A band whose precision sits far from its
own number is the argument for recalibrating rather than for reprompting.

`unsure` is counted and excluded from every denominator. A reader who cannot
tell is evidence about the claims, not about the edge.

## 3. The before-state, and why this document does not contain it

No seat in this org holds a database credential. That is the ledger entry of
2026-09-28, "nobody in this org can tell whether the press printed today", and
it is the owner's to close with a read-only Neon role in a repository secret.
Until she does, `tools/graph_audit.py` answers `unknown` and exits 2 from any
seat sandbox, and this section stays empty on purpose rather than being filled
with an estimate dressed as a measurement.

What can be said now comes from the two live readings this repository already
holds, both taken on 2026-09-26 and both of the same database.

The owner read Neon directly, and `pipeline/interpret.py` records what she
found in its own docstring: **746 claims, 487 of them still in
`interpret_queue`**, with the job drawing 11 to 14 edges a day. So 259 claims
had been judged and the other 487 had not.

The frontend seat read the same database the same day, and
`site/lib/graph-live.js` records that reading in its own comment: **214 of 746
claims carry no link at all**, so 532 do. Its query defines linked as appearing
on either end of an edge, which is the union of `from_claim` and `to_claim`.

Put beside each other those two readings say something neither says alone. Only
259 claims have ever been judged, and 532 are linked, so **at least 273 of the
linked claims are claims the judge has never reached.** They are in the graph
because something newer pointed at them, not because anything asked what they
relate to. A quarter of the corpus is unlinked and roughly two thirds of it is
unjudged, and those are different problems with different fixes.

This is exactly why the instrument is the first slice rather than the last.
"532 of 746 claims are linked" reads as a healthy graph on the site's own page.
The audit's isolation metric asks a narrower question, which is how many claims
the judge looked at and drew nothing from, and the two numbers can point in
opposite directions from one database. Neither reading is wrong. They have
different denominators, nothing in the org has ever written both down at once,
and that is the whole gap.

So the honest prediction is a fork rather than a number. Either isolation comes
back low, in which case the graph's problem is size and the right next slice is
draining `interpret_queue` faster instead of any redesign, or it comes back
high, in which case the judge is refusing on the claims it does see and slices 2
and 3 are the work. One run of one command settles it, and until somebody runs
it every plan past this paragraph is a guess.

**Done when:** whoever holds the credential runs

```bash
python3 tools/graph_audit.py --json --raw > docs/evals/YYYY-MM-DD-graph-audit.json
python3 tools/graph_audit.py --sample 40 > /tmp/sheet.json
```

and files the snapshot beside the other receipts in `docs/evals/`, and a reader
labels the worksheet so there is a precision number to improve on.

## 4. The upgrade, in slices

Each slice is a day of work with an observable done-condition, and each one is
$0. They are ordered so that every later slice can be measured against the
snapshot the earlier ones produced. Taking them out of order is possible and
costs the ability to say whether anything improved.

**Slice 1, the instrument. Built 2026-09-29.** Done when the audit runs against
the real graph and its snapshot is filed.

**Slice 2, stop the shortlist deciding the density.** Three changes in
`pipeline/interpret.py`, all small: exclude candidates from the same
`paper_id` as the new claim, raise `NEIGHBORS`, and add a distance floor so a
claim with no genuinely close neighbor is judged against fewer than five
candidates rather than being handed five distant ones. The floor is the one that
needs a number, and the dedup probe's distance histogram is where that number
comes from. Cost is bounded by the same `CAP_USD` already in that file, because
more candidates means a longer user message and not more calls.
**Done when:** the ceiling metric is under its bound on a fresh snapshot and the
same-paper share has fallen, with both snapshots committed.

**Slice 3, anchor the confidence.** `prompts/interpret.md` defines confidence as
a probability and names the 0.7 consequence, and it stops there. Give it three
bands with a worked pair at each, in the style of the `unrelated` example that
prompt already carries and that is the best-taught part of it, then re-run and
read `--labels` by band against the previous worksheet. This is the slice with
the most direct customer consequence, because the 0.7 gate under the Left-Behind
Index is currently a threshold applied to a number nothing calibrates.
**Done when:** precision by band is within 0.15 of each band's own midpoint on a
40-edge sample, or the bands are revised and the reason recorded here.

**Slice 4, entity resolution.** Every unmarked near-duplicate is one claim
counted twice in every total the product prints, including the ones in the
weekly issue. The cheap version needs no model: at distill, compare the new
claim's embedding against the corpus and mark a `duplicates` edge below the
threshold before the judge is ever called. The expensive question, which is
whether duplicates should collapse into a canonical claim rather than stay two
rows joined by an edge, is deliberately deferred to slice 6, because collapsing
is destructive and the append-only rule exists to prevent exactly that class of
mistake.
**Done when:** the duplicate rate is under its bound and no claim text appears
twice in one weekly issue.

**Slice 5, the slow loop ADR-10 promised.** Re-judgment has been the missing
half of the design since the founding night. Append-only makes it easy rather
than hard: a second opinion is a second row with a new `method`, nothing is
edited, and the read path prefers the newest method per pair. That last part is
the actual work, and it is the same shape as `latest_triage`, which already
solves this exact problem for `triage_log`. A view named `latest_links` is
probably the whole change.
**Done when:** a claim judged under two prompts has two rows and exactly one
current answer, and `deprecated_claims` reads the current one.

**Slice 6, richer relation semantics.** Four verbs may be too few. They may also
be exactly right, and the honest position today is that nobody knows, because
precision per relation has never been measured. This slice is gated on slice 1's
worksheet: if `refines` comes back with low precision because readers keep
reaching for a distinction the vocabulary does not offer, that is the evidence
for extending it. Without that evidence, adding relations adds ways for the
judge to be wrong.
**Done when:** the worksheet says which relation the readers could not express,
or this slice is closed as unnecessary with the numbers that closed it.

**Slice 7, the storage escalation, which is not today.** ADR-10 names Apache AGE
as the middle rung and Neo4j as the institutional swap, and `docs/scaling.md`
names Neo4j or Neptune "once traversals dominate the query mix". Neither applies
to a graph with roughly a hundred edges whose only consumer is a one-hop view.
The gate is written here so the next person does not have to relitigate it: move
when the query mix actually contains traversals deeper than three hops, or when
a recursive CTE over `claim_links` becomes the slow part of a page. Both are
observable, and neither is true now. Doing this first would be the most
expensive way available to leave every quality problem above exactly where it is.

## 5. The tradeoffs taken, and what would make this wrong

**The audit is a tool and not a cron.** It could run daily and alert. It does
not, because the org already has one deploy-drift alarm and one delivery-health
check and no seat that can read either, and adding a third unread signal is
worse than adding none. When a credential exists, wiring it into the daily
availability check is one line, and that is the moment to do it.

**The bounds are set from argument and not from data.** Nobody has seen a real
number yet, so every bound in the table is a first bar rather than a
measurement. The first real run will move some of them, and moving a bound is
fine as long as the reason is written next to it. Silently loosening one to make
a report green is the failure mode to watch for.

**The dedup probe reads a sample and not the corpus.** Two hundred claims, one
indexed nearest-neighbor lookup each. An all-pairs scan would be exact and would
also be the only part of this tool that cannot be run casually. The sample is
seeded, so the imprecision is at least the same imprecision every time.

**What would make the plan wrong.** Section 3's fork. If the first snapshot
comes back with isolation under the bound and a healthy spread of confidence
values, then the graph's problem is not quality at all, it is that two thirds of
the corpus has never been judged, and the right next slice is draining
`interpret_queue` faster rather than any of slices 2 through 6.
`pipeline/interpret.py::drain` already prints that forecast and costs nothing to
run, so it is worth running in the same session as the first audit. The answer
would be capacity rather than design, and slices 2 through 6 would still be
owed, just later.

## 6. What this does not cover

Claim extraction quality, which is `prompts/distill.md` and belongs to the
evidence-grade work. The embedding model, which is pinned and shared with the
MCP server, so changing it re-embeds the corpus and is its own decision. And what
a reader sees. `/graph` has read the live database since 2026-09-26 and reports
claims, linked claims, edges and papers, which is an honest surface over a graph
whose quality nobody has measured. Whether it should also say how much of the
corpus has never been judged is a question for the frontend seat, and it is
worth asking once these numbers exist rather than before.
