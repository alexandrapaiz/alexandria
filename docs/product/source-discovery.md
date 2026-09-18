# Source discovery: from a static file to a system that finds its own frontier

Owner's directive (all-hands addendum, 2026-09-18, docs/allhands/2026-09-17.md):
propose how alexandria's ingestion surface evolves over time to find important
new topics, sources, frontier labs, and researchers, instead of staying a
static `sources.yaml`. This document is that proposal: three discovery
signals, each built from data the pipeline already holds, a channel that
turns each signal into a reviewable diff, what runs where under the
constraints already in place, and a phased rollout. Skills remain the
sellable product (all-hands decision 6); this is pipeline machinery that
serves the digest and the skill library, not a new SKU.

## 1. Why a static file is the wrong end state

`sources.yaml` today is 7 arXiv categories, one Hugging Face feed, and 19
hand-picked RSS feeds, each with a hand-assigned tier. It is a snapshot of
what mattered on the day someone edited it. Nothing in the pipeline notices
when a new lab starts publishing, when a researcher who wasn't on anyone's
radar becomes prolific, when a genuinely new topic starts appearing across
multiple independent papers, or when a source we treat as neutral (tier `a`
or `d`) turns out to be producing work the field is citing fast. The file
only grows when a human remembers to edit it.

The system does not need external tooling to fix this. Four fields it
already writes on every run are exactly the signal a human curator would use
to notice the same things by hand:

- **The claim graph** (`claims`, `claim_links` — `supports`, `refines`,
  `contradicts`, `duplicates`) and each claim's embedding, for topic novelty.
- **`papers.authors`** (from ingest) and **`papers.institutions`** (extracted
  from full text at distill time), for researcher and lab discovery.
- **`citation_log`**, the Semantic Scholar slow loop `weekly.py` already
  runs every Monday, for traction that predates our own curation.
- **`papers.tier`**, the prior sources.yaml already assigns, as the
  baseline every signal below measures itself against — a paper from a tier
  we already trust gaining traction is not news; a paper from a tier we
  treat as neutral gaining traction is.

Discovery, done this way, is retrospective judgment applied to data already
in hand, which is exactly the shape of work ADR-7's meta-review loop was
built for. It is not a new capability; it is three new queries feeding a
channel that already exists.

## 2. Why the topics column can't do this

The first instinct is to look for "new topics" in `claims.topics`. That
column cannot do the job: `prompts/distill.md` restricts it to a closed
13-tag vocabulary (skills, context-engineering, harness-engineering,
loop-engineering, memory, retrieval, multi-agent, evals, post-training,
serving, systems, tooling, other). A paper introducing something the
vocabulary has no tag for gets forced into `other`, which looks identical to
every other paper that didn't fit cleanly. The tag column is doing its job —
it keeps the digest's sections legible — but it is structurally incapable of
naming a topic nobody has named yet.

Real novelty has to be read from the embedding space instead: `claims`
and `papers` both carry a 1024-dim Qwen3-Embedding-0.6B vector, normalized,
indexed with HNSW for cosine distance. A claim that sits far (in cosine
distance) from everything the corpus held before a given date, and that
several other recent, independent papers are also landing near, is
novelty plus growth — the same definition the literature converges on for
"an emerging topic" (see §4).

## 3. Three signals, grounded in what the pipeline already holds

### 3.1 Embedding-space topic novelty

For claims from the last N days, find each one's nearest neighbor among
claims older than N days (pgvector `<=>`, cosine distance). A claim whose
nearest old neighbor is distant is a novelty candidate on its own; it
becomes a real signal once several such candidates, from different papers,
are also close to *each other* — independent convergence, not one outlier
paper. `cluster_size` (how many other recent, distant-from-old claims a
candidate sits near) is the growth half of "novelty + growth."

This directly answers "important new topics": a cluster of 3+ claims from
3+ different papers, all distant from anything the corpus held a month ago,
is worth a human or the weekly agent reading the source papers and deciding
whether it names something sources.yaml should now watch on purpose (a
category, a lab's feed, a keyword worth triage's attention).

### 3.2 Rising authors and institutions

`papers.authors` (ingest) and `papers.institutions` (distill, from full
text) already carry exactly the fields a citation-network tool would build
a "rising author" or "new lab" detector from. The signal: an author or
institution whose earliest paper in our corpus is within the last N days,
with 2+ papers already routed past `discard` by triage — not just present,
but the triage model itself judged the work non-trivial more than once.

This directly answers "frontier labs" and "researchers": a lab that starts
appearing multiple times inside a few weeks, none of it discarded, is either
a new group worth a dedicated feed or an existing group suddenly shipping
more.

Caveat, stated plainly: this signal reads thin at launch. The pipeline has
about two weeks of history as of this writing, so nearly every author looks
"first seen recently" — that's the corpus being young, not a real signal.
The query does no harm run early (it returns real names, just not yet
meaningfully filtered by recency), but its judgment value grows with corpus
age; it's worth little before 60-90 days of history exist, and worth more
every week after that.

### 3.3 Citation velocity from a source we don't already trust

`weekly.py`'s slow loop already re-checks citation counts on a rolling
schedule and writes them to `citation_log`, append-only, exactly so
trajectory (not a single count) is computable. The digest already surfaces
the fastest movers. The discovery angle on the same data: filter that
movers query to papers whose `tier` is *not* `b` or `c` — i.e., papers that
arrived through the neutral or skeptical firehose, not through a source we
already curate as strong. A paper gaining citations fast from a source we
treat as neutral is exactly the case where sources.yaml's prior was wrong
and should be revisited.

This directly answers "sources": it is retroactive evidence that a tier
assignment or a missing feed cost us confidence we should have had at
publication time, not months later.

### 3.4 A fourth mechanism the pipeline doesn't support yet (named, not built)

"New topics" could also mean "a whole arXiv category we don't track starts
mattering." The arXiv firehose can't discover this on its own — it only
ever pulls from the categories already listed in `sources.yaml`, so by
construction it cannot see a category outside that list. The one source we
ingest that *isn't* category-filtered is `hf_daily_papers`, HuggingFace's
own curator picks, which can and does include papers from categories we
never asked for. Today we can't use that fact: `papers` has no `category`
column, so once a paper lands in bronze there is no record of which arXiv
category it came from. Storing it (`alter table papers add column category
text`, populated in `ingest.py`'s `fetch_arxiv`/`fetch_hf_daily`) is a small,
real schema change, not a design idea — it's phase 2 (§6), not this PR,
because schema changes deserve their own review independent of a research
document.

## 4. How others approach the same problem

Public research and tooling confirm the shape above rather than suggesting
something alexandria is missing:

- **Emerging-topic detection** in the bibliometrics literature traces to
  Kleinberg's burst-detection algorithm (a term's emission rate flipping
  from a low-rate to a high-rate state), and newer neural work like
  BERTrend (arXiv 2411.05930) tracks topic-*embedding* drift over time and
  defines emergence explicitly as novelty plus growth — the same two
  numbers §3.1 computes (`nearest_old_distance`, `cluster_size`).
- **Rising-author detection** in bibliometrics normalizes citation counts by
  time-since-first-paper and subfield norms rather than using raw counts
  (arXiv 1404.3084); citation *velocity*, not the raw count, is the
  faster-arriving signal, which is what §3.3 filters on.
- **Affiliation/lab discovery** is typically done by clustering normalized
  affiliation strings (the Research Organization Registry, ror.org, is the
  standard identifier space) and flagging a paper whose affiliation doesn't
  match any known cluster as a candidate new organization — the same idea
  as §3.2's "first seen" check, done here with the plain-text institution
  strings distill already extracts rather than a formal registry (a
  possible later refinement, not needed yet at this corpus size).
- No publicly documented system was found that **fully automates** turning
  these signals into an actual expanded source list with no human in the
  loop — Zeta Alpha's research platform and Semantic Scholar's own
  recommendation API both do rich embedding-based retrieval and
  recommendation, but the "watch this new thing going forward" step stays a
  human curation action in every system surveyed. That is the gap §5
  proposes filling, and it is a reasonable one for alexandria to fill first:
  the ADR-12 whitelist-and-PR channel below already exists for exactly this
  kind of self-authored diff, built for the meta-review loop before this
  document ever asked for it.

(Full source list available on request; representative citations: Kleinberg,
"Bursty and Hierarchical Structure in Streams"; BERTrend, arXiv 2411.05930;
"Bibliometric Indicators of Young Authors," arXiv 1404.3084; the Semantic
Scholar Open Data Platform, arXiv 2301.10140; ror.org's affiliation-matching
writeup.)

## 5. From signal to sources.yaml diff: the existing channel

Nothing about turning a discovery signal into a proposal is new plumbing.
ADR-12 already gives the system exactly one way to change its own sources:
`propose_change` (mcp/server.py), which opens a pull request against a
whitelist of `prompts/*.md` and `sources.yaml`, writes a `promotions` row
(`kind = 'system_diff'`), and requires a human (today) or the ADR-13 panel
(once the panel is live) to merge before it takes effect. That gate does not
change. What this document adds is the evidence `propose_change` needs
before it's justified in touching `sources.yaml` at all.

The new MCP tool this PR ships, `discovery_report` (§6), returns the three
signals above as structured evidence, not a diff. Turning a `discovery_report`
finding into an actual `propose_change` call is judgment, the same kind
`prompts/weekly-agent.md`'s existing Step 4 already exercises on triage and
graph health evidence:

1. Require a pattern, not an anecdote — the same bar Step 4 already holds
   itself to ("at least several instances pointing the same way"). A single
   novel claim, a single new author, a single citation spike proves nothing;
   `cluster_size >= 3` from 3+ distinct papers, or an author/institution
   appearing 2+ times, is the floor.
2. Decide what kind of diff the evidence supports. A rising institution with
   a discoverable RSS feed becomes a new `feeds:` entry, tier `c` (a
   frontier/open-lab channel) or `d` (a practitioner voice), pending the
   first few weeks of what it actually publishes. A citation-velocity
   outlier from an existing feed just means that feed's tier was set too
   low and should move up. Not every finding has a clean file diff yet — a
   rising author with no blog, or a genuinely new topic with no natural
   arXiv category or feed behind it, has nowhere to land in the current
   schema (§6 phase 2 addresses this gap explicitly rather than pretending
   it isn't there).
3. Write the rationale `propose_change` already requires with the specific
   `discovery_report` numbers in it (cluster size, nearest-old distance,
   papers-in-window, citations-per-day) so a reviewer — human today, panel
   later — can check the claim with one more query, exactly as ADR-12
   already expects of every meta-review proposal.

Worked example, using the shape of what `discovery_report` returns rather
than a fabricated result (this PR ships the tool with no production data to
query yet): if `rising_institutions` shows an institution with 3 papers in
14 days, none discarded by triage, and `citation_velocity_outliers` shows
one of that institution's papers gaining citations fastest of the week from
tier `a`, that is two independent signals agreeing. The weekly agent checks
whether the institution publishes a feed; if it does, it drafts the new
`feeds:` line and calls `propose_change` with both numbers in the
rationale; if it doesn't, it records the observation in the ledger instead
of forcing a diff that doesn't exist yet.

## 6. What runs where

**No new Modal cron.** Modal's free tier caps scheduled functions at five,
and all five are already spoken for: `ingest` (11:00 UTC), `distill`
(11:30), `triage` (12:00), `interpret` (14:00), `weekly` (Monday 15:00) —
this is the same constraint ADR-12 cited when it put meta-review inside the
weekly agent instead of a sixth cron, and it still holds. Discovery follows
the same rule: it is judgment over an open-ended evidence surface (which
cluster is real, which institution is worth a feed), not a fixed query a
workflow can run unattended, so it belongs with the agent, not with a cron.

**This PR's slice:** one new read-only MCP tool, `discovery_report`, added
to the already-deployed `mcp/server.py` alongside `semantic_search`,
`rag_answer`, and `sql_query`. It costs no new secret, no new dependency, no
new infrastructure, and no new cron slot — it is three SQL queries against
data the pipeline already writes, callable today by anyone with the MCP
connector (the owner, directly, right now; the weekly agent, once it runs).

**The gap this depends on:** `prompts/weekly-agent.md`'s Step 4 is where
this evidence is meant to turn into a `propose_change` call, but Step 4 has
no automated runner today. README's status checklist still carries it
unchecked ("Claude weekly agent scheduled task ... → first skill PRs"), and
unlike engineer, PM, market, OKR, security, exo, and skill, there is no
`agent-weekly.yml` in `.github/workflows/`. Skill authoring (weekly-agent.md
Step 3) was already superseded by the dedicated skill agent (ADR-22,
Tuesdays); Step 4 meta-review, including everything in this document, has
no seat running it on any cadence. This document's mechanism works the
moment someone runs `discovery_report` and acts on it, but it stays a
manual, owner-initiated action — exactly as it is today for the rest of
Step 4 — until that gap closes. Closing it is a ledger item (§7), not part
of this PR: it's a decision about standing up or re-routing an autonomous
seat with write access to `prompts/*.md` and `sources.yaml`, which deserves
its own review rather than riding in on a design document.

## 7. Phased rollout

**Phase 0 — this PR.** `discovery_report`, the MCP tool, shipped and
callable. No sources.yaml diffs yet; there isn't enough corpus history for a
finding to clear the evidence bar in §5 honestly, and fabricating one would
defeat the point of requiring a pattern.

**Phase 1 (ledger, day-sized).** Automate Step 4's runner: an
`agent-weekly.yml` GitHub Actions workflow, matching the pattern the other
seven seats already use, running `prompts/weekly-agent.md` with direct
database access the way `skill-agent.md` already does (`NEON_RO_URL`) rather
than depending on the MCP server's human-oriented OAuth login. Step 4 gains
an explicit discovery sub-step that calls `discovery_report` and applies
the evidence bar in §5.

**Phase 2 (ledger, day-sized).** Two schema-adjacent gaps named in §3.4 and
§5 get addressed once phase 1 is producing real findings to design against:
a `category` column on `papers` so `hf_daily_papers`' cross-category picks
can flag an uncovered arXiv category, and a `watchlist:` section in
`sources.yaml` (authors and institutions, not just feeds and categories) so
a rising researcher or lab with no blog has somewhere to land besides a
ledger note.

**Phase 3 (later, cost-gated).** Widen the Semantic Scholar batch call
`weekly.py` already makes to request `references`/`citations` fields (still
inside the free tier, more calls against the same rate limit) to find venue
centrality — a venue or workshop that keeps appearing as a citation hub for
papers we already trust, the closest analog to "discover a new venue" the
research in §4 describes. Not scoped further here: it changes the shape of
the slow loop's API usage and belongs in its own proposal once phases 1-2
show whether the simpler signals are pulling their weight.

## 8. What this is not

This is pipeline machinery, in service of digest and skill quality — it is
not a new sellable surface. All-hands decision 6 keeps skills as the focus
for now; a better-fed corpus makes better claims, which makes better
skills, which is the only place this shows up for a subscriber. Nothing
here creates a customer-facing feature, a new price point, or a new product
surface.
