# The claim graph, measured

**Slice 1 built 2026-09-29, slice 5 built 2026-10-24 and finished 2026-10-25,
slice 2 built 2026-10-25** (engineer seat). This is
the design record for the
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
| The shortlist | `pipeline/interpret.py`, `SHORTLIST_SQL` | pgvector kNN over `claims.embedding` against strictly older claims, excluding the new claim's own paper and anything past `CANDIDATE_MAX_DISTANCE`, capped at `NEIGHBORS` |
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

**The shortlist ceiling.** `NEIGHBORS` decides how many candidates a claim is
judged against, so it is the most distinct neighbors any claim can be linked to
on the run that interpreted it. A claim sitting exactly at that number is a
claim whose edge count was decided by a Python constant instead of by the
corpus. One claim in ten at the ceiling is tolerable. Three in ten means the
cheapest available upgrade is a larger integer, and every clever change made
before that one is measured against a graph that was truncated.

It was five when this was written and it is ten since slice 2, which is the
cheapest upgrade being taken rather than this metric being satisfied. The
numbers above are shares, so they do not move when the constant does, and the
metric is still the one that says whether the new constant binds too. The audit
keeps its own copy of the number and a test holds it against the job's, because
a ceiling metric measuring a shortlist nobody sends reads as a healthy graph.
`reach`, added in the same slice, asks the same question of the candidates
rather than of the edges, and it is the one of the two a seat can run before the
credential exists.

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

**Slice 2, stop the shortlist deciding the density. Built 2026-10-25.** Three
changes in `pipeline/interpret.py`, all small: exclude candidates from the same
`paper_id` as the new claim, raise `NEIGHBORS`, and add a distance floor so a
claim with no genuinely close neighbor is judged against fewer than five
candidates rather than being handed five distant ones. The floor is the one that
needs a number, and the dedup probe's distance histogram is where that number
comes from. Cost is bounded by the same `CAP_USD` already in that file, because
more candidates means a longer user message and not more calls.
**Done when:** the ceiling metric is under its bound on a fresh snapshot and the
same-paper share has fallen, with both snapshots committed.

All three shipped, as `SHORTLIST_SQL`, `NEIGHBORS = 10` and
`CANDIDATE_MAX_DISTANCE = 0.40`. Four things the paragraph above did not
anticipate are worth more than the three it did.

**The query had never been tested, and that is the finding rather than the
chore.** The retrieval that decides the shape of this graph was six lines of
SQL inline in the run loop. Every metric slice 1 built measures something
downstream of it, the audit's own `integrity` check exists to catch an edge
pointing backwards through time, and nothing anywhere asserted that the query
only ever looked backwards. `tests/test_shortlist.py` is nine live assertions
against a real cluster with pgvector, one for each way out of the list, and the
fixture is built so that the target's own sibling is the nearest claim in the
corpus, because that is what the defect looked like in production. Deleting any
one clause takes the suite to ten failures. The audit could only ever have
caught the symptom, after the bad edges were already rows.

**The cost comment was wrong before this slice touched it.** It said the system
prompt was 880 tokens. Measured with `pipeline/budget.py`'s own tokenizer it is
1,260, because `prompts/interpret.md` has grown since somebody wrote 880 down
and nothing recomputes a comment. So the cap had been set against a request
smaller than the one being sent. `drain` and `preflight` each carried a third
copy of the pair as `1_050, 150`. There is one measured pair now,
`CALL_PROMPT_TOKENS` and `CALL_OUTPUT_TOKENS`, every forecast reads it, and a
test recomputes both rather than reading them, because the failure here is not
arithmetic anybody got wrong. It is a number that was right on the day and
decays with no symptom.

**The raise is not free, and "bounded by `CAP_USD`" was the wrong frame.** It is
true that a wider shortlist is a longer message and not a second call, so the
cap still holds and no run can overspend. What changes is what the cap buys: the
ceiling per call goes from $0.00400 to $0.00594, so $0.30 buys 50 claims in the
worst case where it bought 74, and about 95 in practice where it bought 135. A
fallback day falls further, from 56 claims to 23, because the free tier's
allowance is a token budget and the call got bigger. That is the price of slice
2 and it is worth paying at today's depths, where `interpret_pending` is 0 and
the backlog is upstream in distill. It would be worth re-reading if the fresh
queue is ever thousands deep again, and this paragraph exists so that re-reading
does not have to start by rediscovering the arithmetic.

**The floor's number is the weakest thing here, so it ships with the instrument
that moves it.** The paragraph above says the dedup probe's distance histogram
is where the number comes from, and no probe has ever run, because no seat holds
a database credential. So 0.40 comes from the band already recorded beside
`NEAR_DUPLICATE_DISTANCE`: Qwen3-Embedding-0.6B puts paraphrases below 0.1 and
unrelated sentences between 0.4 and 0.8, and 0.40 is the near edge of the
unrelated band. That is an argument and not a measurement, the same as every
bound in section 2. The audit's new `reach` metric is the measurement when
somebody can run it: it runs the job's own retrieval against a seeded sample and
reports how many candidates the shortlist offers, how many claims are offered
none, and a histogram of nearest cross-paper distance in tenths. The histogram
is deliberately not truncated at the floor, because the whole question a reader
has is how much of the corpus sits just outside it. `reach` carries no bound, on
purpose: a short shortlist is the floor working, and a bound there would call a
fact about the corpus a failure.

**The question a filter over a vector index always raises, asked and closed.**
`claims` carries an HNSW index (`claims_embedding_idx`, `vector_cosine_ops`),
and an HNSW scan can only evaluate the distance ordering. The other two clauses
of this shortlist, `id < %s` and `paper_id <> %s`, are therefore post-filters,
and a post-filtered approximate scan is the standard way a query like this
quietly returns fewer rows than its `limit`: the index hands back a bounded
number of candidates, the filters delete some of them, and nothing goes back
for more. If that happened here, raising `NEIGHBORS` from 5 to 10 would buy
nothing and the audit would report a low ceiling for the wrong reason.

Measured rather than reasoned about. On a 1,200-claim corpus across 50 papers
with the index built, the shortlist returns 10 candidates of 10, with the floor
active and with the floor disabled, and identically whether the index is
allowed or `enable_indexscan` is off. The plan says why: Postgres chooses
`Limit -> Sort` on an exact distance computation rather than the index at all,
at this size and with these filters. So the recall is exact and the raise
delivers what it claims.

What that does not say is that it is exact forever. The planner switches to the
index when the table is large enough for the sort to look expensive, and that is
the point where the post-filter behaviour starts to matter. Two things are worth
knowing then. The server's pgvector version decides whether a filtered scan can
widen its own search, since `hnsw.iterative_scan` arrived in 0.8.0 and the host
this was measured on runs 0.6.0, and nothing in this repository records which
version Neon runs, because no seat can read the database to ask. And the
instrument already exists: the run's own ceiling line falls when the shortlist
stops filling, so a scan that silently returns six candidates where ten qualify
shows up as a ceiling share collapsing without the corpus changing.

**One gap this slice opens and does not close, recorded here because the next
person to touch the reservation needs it.** Raising
`MAX_COMPLETION_TOKENS` makes this a runtime change under
`docs/agents/runtime-changes.md`, whose third gate is
`modal run pipeline/interpret.py::rehearse`, and that law's own words are that
a rehearsal uses "the real provider, the real key, the real token reservation,
the real timeout". The reservation it sends is real. The payload is not:
`REHEARSAL_NEIGHBORS` is a fixed five-candidate shortlist, so the rehearsal now
exercises about half the user message production sends, which is the half of
the request that grew. It would still catch a dead key, a missing model, a
timeout and a judge that labels everything or nothing, so it is not useless. It
would not catch a model that handles five candidates and degrades at ten.

Extending it means five more hand-written claims whose right answer is
knowable, because that fixture's value is that a reader can check the verdict,
and `tests/test_corpus_drain.py` pins the length at five on purpose. That is a
small piece of work and it is not this slice's, so it is written down rather
than rushed. Nothing is urgent about it: the gate cannot run at all until the
Modal workspace comes back.

**And the done-condition cannot be met today, by anyone in this org.** Both
halves of it are read off a database. So the run reports the retrieval-side half
of the same question in its own log, which is the one surface a seat can reach:
every run now prints its mean candidates per claim and how many claims hit the
`NEIGHBORS` ceiling. Above a tenth there, `NEIGHBORS` is binding again and the
next raise is cheaper than any cleverness. The snapshots the done-condition
names are still owed and still belong to whoever holds the credential, which is
the ledger entry of 2026-09-28.

The audit also settled the question slice 5 handed forward. A metric that gates
a bound reads `latest_links` now, a metric that asks what the judges have done
reads `claim_links`, `integrity` keeps reading the rows because a view would
hide the rows it hunts for, and `shape` reports both so the gap between them
says whether anything has ever been re-judged. No pair in production carries a
second opinion yet, so every number that split touches is unchanged today and
right tomorrow.

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

**Slice 5, the slow loop ADR-10 promised. Built 2026-10-24.** Re-judgment has
been the missing half of the design since the founding night. Append-only makes
it easy rather than hard: a second opinion is a second row with a new `method`,
nothing is edited, and the read path prefers the newest method per pair. That
last part is the actual work, and it is the same shape as `latest_triage`, which
already solves this exact problem for `triage_log`. A view named `latest_links`
is probably the whole change.
**Done when:** a claim judged under two prompts has two rows and exactly one
current answer, and `deprecated_claims` reads the current one.

**The view was not the whole change, and the sentence above is wrong in a way
worth keeping.** `claim_links` keyed `(from_claim, to_claim, relation)`, so the
second row the paragraph assumes could not exist. An October prompt that
*agreed* with September's hit the key and `pipeline/interpret.py`'s `on conflict
do nothing` discarded it without a word, which means the design made its most
useful outcome the one outcome it could not record: a new prompt confirming an
old verdict is how prompt stability gets measured, and the key threw it away.
Reproduced on a real server before anything was written, where the insert
reported `INSERT 0 0`. So slice 5 is a key change and then a view:
`claim_links_opinion_idx` puts `method` in the key and folds NULL to the empty
string, because a NULL is never equal to itself in a key and the edges drawn
before that column existed have to stay insertable.

**And there were more readers than one.** Pointing `deprecated_claims` at the
view satisfies the done-condition, and it would have left the weekly issue
wrong, because a read written against a one-verdict-per-pair table does not
degrade quietly when a pair gains a second. Five reads in `pipeline/weekly.py`
moved: the relation list beside each new claim, which would have printed both
verdicts side by side; the 2+ supports list, where two prompts agreeing read as
the two different supporters the list requires; the `superseded` and
`deprecated` sections, which date a pair by `created_at` and so would have
reprinted September's verdict as this week's news; and `links_drawn`, which
`prompts/digest.md` promises a subscriber counts "the connections drawn between
findings" and which now counts a pair by its first sighting rather than by its
rows. That last one is the owner's 2026-09-25 directive on the stats line
applied to a new way of inflating the same number.

**The instrument had to be corrected against its own measurement.**
`integrity.self_contradictory` counted a pair holding both `supports` and
`contradicts` and called it corruption, which is exactly the shape a changed
mind now leaves behind. It groups by the opinion rather than by the pair, so it
still catches one judge asserting both at once and no longer reports the slow
loop as damage. The `contradiction` metric reads `latest_links` too, because its
last number comes from `deprecated_claims` and a report whose own four numbers
do not reconcile is worse than one that is merely stale.

**The trigger, built 2026-10-25, and the paragraph that asked for it is kept
below because it was right about the shape and wrong about the inputs.** What it
asked for: "nothing re-queues a judged claim yet. `interpreted_at` marks a claim
done and the loop needs a trigger that picks claims whose newest opinion
predates the current prompt sha, which is a job rather than a read path and is
the natural next day of work here."

Two things that sentence assumes are not true of the data, and both of them are
a bill rather than a wrong answer, which is why they are worth writing down.

**A claim's newest opinion is not always a row.** An edge is written when the
judge found a relation, so a pass that read a claim and found nothing leaves
nothing behind. In `claim_links` that claim is indistinguishable from one the
current prompt has never seen, so a trigger reading the edges re-selects it on
every run and pays for a model call every time, forever, and the graph never
changes to say otherwise. The pass is therefore the unit rather than the
finding: `claim_judgments` is append-only, keyed `(claim_id, prompt_sha)`, and
carries an edge count that is allowed to be zero. The empty passes are the rows
the table exists for.

**And the sha the trigger compares against is the prompt's, not `method`'s.**
`method` is `model@sha` and the model is whichever provider answered, which is
ADR-32's Moonshot normally and Groq's free tier when Moonshot refused. So a
trigger keyed on `method` re-judges the entire corpus the first time the
fallback answers, and again when the primary comes back, and neither pass is a
change of mind. The prompt is the judge's instructions and the model is a
capacity accident. `method` is still recorded beside the sha, because which
provider answered is worth knowing and this is now the only place it survives
per claim.

**What the trigger will not do is spend anything.** Re-judgment takes the slots
the fresh queue leaves and never one it wanted, inside the same `max_claims` and
the same dollar cap the run already had. A first opinion is worth more than a
second one: an unjudged claim has no edges at all, so judging it can only add to
the graph, where re-judging a claim usually confirms what is already there. The
fresh queue was 2,000-odd deep at the last reading, so the trigger returns
nothing today and the loop stays latent until the drain catches up. That is the
right order of work rather than a limitation, and it is also why turning this on
cannot regress production this week.

**The backfill is the difference between starting correct and starting with a
bill.** Every claim judged before the table existed has no row in it, so the
first run under any prompt would see the whole judged corpus as never-judged.
The shas are recoverable: they are already in `claim_links.method`, so a claim
judged under today's prompt is recorded as judged under today's prompt and is
correctly left alone, and the pass is dated from the edge rather than from
`now()`, because those passes happened and on known dates.

**The drain caught up overnight, in the way nobody was watching for, and the
sentence this paragraph used to open with was wrong within the day.** It said
everything in the slice was correct and latent until the drain caught up. On
2026-10-25 `/api/delivery` reported `interpret_pending: 0`. The queue did not
drain, it moved one stage upstream: `distill_pending` was 3,680 and no claim
had been written since 2026-10-22, because the Modal workspace has been
switched off since 2026-10-23 and distill is what makes claims. An empty fresh
queue and a deep one look identical to `rejudge_budget`, which takes the
leftovers either way, so the sweep takes whole runs from the first one after
deploy rather than none.

Nothing about that is a defect in the trigger. It is bounded by the
`max_claims` and `CAP_USD` the job already had, so no run costs more than it
could before, and it terminates because every pass writes a row. What was
wrong is the claim that it was free, and the reason it was wrong is worth more
than the correction: a safety argument keyed to a queue depth is a reading
with an expiry date, and this one was written the day before it expired.

Two things follow from it, both built 2026-10-25. `drain` now prices the sweep
the way it already priced the backlog, in runs and dollars, and splits the
depth into the passes under a known older prompt and the backfill's `unknown`
rows, so the bill can be read before it is spent instead of after. And the
sweep is ordered by what it buys rather than by `c.id`: a claim carrying a
comparable prior verdict goes first, because a run the cap cuts short should
be cut short at the cheap end. The select is a left join rather than an inner
one, so a claim judged by an image older than the table is still reachable.

No pair in production has a second opinion yet, so every number in this
paragraph's list is unchanged today and right tomorrow. The audit's volume metrics (`shape.edges`, `degrees`, `relations`,
`confidence`) still count every opinion ever given, which is the right question
for "what has the judge done" and the wrong one for "how dense is the graph".
That choice belongs with slice 2, which is where density is argued, and it is
recorded here rather than guessed at now.

**Settled 2026-10-25 by slice 2, in the direction this paragraph expected.** A
metric that gates a bound reads `latest_links`, because every one of those
bounds is a claim about the graph as it stands: `degrees` feeds isolation and the
ceiling, `confidence` feeds calibration and the 0.7 gate, `provenance` feeds the
same-paper share. A metric that asks what the judges have done keeps reading
`claim_links`, which is `judges` and also `integrity`, and `integrity` is the one
where reading the view would have been a defect rather than an imprecision,
because it hunts for rows that should not exist and the view hides all but the
newest row per pair. `shape` reports both as `edges` and `current_edges`, so the
gap between them is the cheapest way for a reader to see whether the slow loop
has ever run.

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
