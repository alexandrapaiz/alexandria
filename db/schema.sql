-- alexandria schema: medallion layers + triage log
-- Apply with: psql "$DATABASE_URL" -f db/schema.sql

create extension if not exists vector;

-- ============ bronze: raw ingested papers ============
create table if not exists papers (
    id           text primary key,          -- arxiv id, or url hash for blog posts
    source       text not null,             -- 'arxiv' | 'hf-daily' | feed name from sources.yaml
    tier         text not null default 'a', -- triage prior; see sources.yaml
    title        text not null,
    authors      text[] default '{}',
    abstract     text,
    url          text not null,
    published_at date,
    fetched_at   timestamptz not null default now(),
    -- Qwen3-Embedding-0.6B produces 1024-dim vectors; changing the embedding
    -- model means re-embedding every row (batch and query models must match)
    embedding    vector(1024)
);

-- migrations for databases created before the tier column existed
alter table papers add column if not exists tier text not null default 'a';
update papers set tier = 'c' where source = 'blog' and tier = 'a';

-- distilled_at marks a paper as processed by distill (blackboard marker; claims
-- alone can't mark completion because a paper may honestly yield zero claims)
alter table papers add column if not exists distilled_at timestamptz;

-- fulltext_chars: how much of the paper distill actually read, in characters, or
-- NULL when it read the abstract only. Distill is the one step that fetches
-- arXiv HTML, and until 2026-09-26 nothing recorded whether the fetch succeeded,
-- so "read in full" was a number nobody could produce from the database. The
-- weekly issue now states it (owner's directive 2026-09-25: the stats line says
-- what happened, not "read N papers"), and a number the issue prints has to come
-- from a column rather than from an assumption about a code path.
--
-- Rows distilled before this column existed stay NULL and are honestly unknown.
-- The issue counts only the last seven days, so the gap ages out of every issue
-- within a week of the column landing.
alter table papers add column if not exists fulltext_chars integer;

-- ============ triage log: every routing decision, with reasoning ============
-- This table doubles as the eval set for the recursive loop: human_verdict
-- labels each machine decision, and disagreements drive prompt proposals.
create table if not exists triage_log (
    id            bigserial primary key,
    paper_id      text not null references papers(id),
    decision      text not null check (decision in ('discard', 'index', 'distill', 'deep_read')),
    score         real,
    reasoning     text,
    model         text,
    prompt_sha    text,                     -- git blob hash of prompts/triage.md used
    created_at    timestamptz not null default now(),
    human_verdict text check (human_verdict in ('agree', 'overturn')),
    human_note    text
);

-- method: model + prompt sha, the one string that says which judge produced a
-- decision. `model` and `prompt_sha` have both been written since the table
-- existed, and every question anybody actually asks needs the pair: which rows
-- came from the rubric that is live now, and which came from the one before it.
-- Same shape and same reason as claim_links.method, which has carried
-- `model@sha` since the graph's first edge.
alter table triage_log add column if not exists method text;

-- Old rows get the pair they already recorded in two columns. Idempotent: the
-- guard is the null, so a second run writes nothing.
update triage_log
   set method = coalesce(model, 'unknown') || '@' || coalesce(prompt_sha, 'unknown')
 where method is null;

create index if not exists triage_log_method_idx on triage_log (method);

-- A paper may now carry MORE THAN ONE row here. Re-triage under a revised rubric
-- appends a new decision rather than editing the old one, so the log stays the
-- eval set it was built to be: the disagreement between two rubrics about the
-- same paper is the most valuable row in the table, and an UPDATE would destroy
-- it. `latest_triage` below is what every consumer reads, and it is the only
-- place that knows a paper can have a history.

-- ============ silver: distilled claims ============
-- The unit of knowledge is the claim, not the paper.
create table if not exists claims (
    id         bigserial primary key,
    paper_id   text not null references papers(id),
    claim      text not null,
    evidence   text,
    topics     text[] default '{}',         -- e.g. context-engineering, loop-engineering
    embedding  vector(1024),
    created_at timestamptz not null default now()
);

-- interpreted_at marks a claim as judged against its neighbors (blackboard marker;
-- edges alone can't mark completion because a claim may legitimately have none)
alter table claims add column if not exists interpreted_at timestamptz;

-- procedure: the mechanism as numbered operational steps, when the paper gives
-- one — the raw material for extractable systems and skills (digest "how it
-- works" sections, skill proposals)
alter table claims add column if not exists procedure text;

-- evidence_grade: what kind of support this claim has, written at distill from
-- the paper's source class, whether the model found a measurement in the
-- evidence it wrote, and whose result the claim is about
-- (pipeline/evidence.py holds the rules and the reasoning).
-- NULL means ungraded, which is every claim distilled before this column
-- existed; nothing backfills it, because the measurement judgment belongs to
-- the run that read the source.
alter table claims add column if not exists evidence_grade text;

-- `relayed` is the fifth value, added 2026-10-26: another work's result, as
-- this source reports it. The constraint is dropped and rebuilt rather than
-- added only when absent, because the four-value version is already on every
-- database this schema has ever been applied to, and an `if not exists` guard
-- around a widening would see it there and leave the old list in place. That
-- is the shape of failure the parity test in tests/test_evidence_grade.py
-- exists for: a grade the grader returns and the column rejects loses a whole
-- run of claims on the insert. Both statements are idempotent.
alter table claims drop constraint if exists claims_evidence_grade_check;
alter table claims add constraint claims_evidence_grade_check
    check (evidence_grade is null or evidence_grade in
           ('controlled', 'field_measured', 'asserted', 'anecdote', 'relayed'));

-- prompt_sha: which distill prompt wrote this claim, the first 12 hex of its
-- sha256. As of 2026-09-30 there are two of them, prompts/distill.md for papers
-- and prompts/distill-practices.md for field reports, so this column now answers
-- which prompt as well as which version of it, and the two shas are what
-- separate a claim mined from a paper from one mined from a blog post.
-- The press has recorded this on every issue since it existed and triage
-- on every decision; claims had nothing, so the deploy state of the distill
-- prompt was only knowable by inference from the shape of its output. That is
-- how the interpret prompt went seven days stale unnoticed
-- (INC-2026-09-26-interpret-stale-third-sighting), and a revised rubric whose
-- arrival cannot be seen in the data is a rubric nobody can show is live.
-- NULL means a claim written before this column existed.
alter table claims add column if not exists prompt_sha text;

-- broke: what failed, regressed, or had to be abandoned, as the source reports
-- it. Only the practices prompt asks for this, because only a field report has
-- it to give: a paper publishes the configuration that worked and an engineering
-- blog post is the one place the industry writes down what it tried first. That
-- half of a field report is the half most often dropped in summary, and it is
-- the material the deprecated-claims view and the left-behind index are made of,
-- so it gets a column rather than being folded into `evidence` where no query
-- can find it. NULL means the source reported no failure, which for a field
-- report is a fact about the source worth reading rather than a missing value.
alter table claims add column if not exists broke text;

-- attributed_to: the work a relayed claim's result belongs to, as the source
-- names it ("Yuan et al., 2026", "arxiv:2605.09490", "the Chroma report").
-- Only meaningful where evidence_grade is 'relayed', and it is what makes such
-- a row actionable rather than only doubtful: the repair
-- INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully
-- asks for is that a load-bearing citation becomes a reading-queue line, and a
-- queue line needs an address. NULL on a relayed row is its own signal, which
-- is a relational sentence whose subject the source never named.
alter table claims add column if not exists attributed_to text;

create index if not exists claims_evidence_grade_idx on claims (evidence_grade);
create index if not exists claims_prompt_sha_idx on claims (prompt_sha);

-- ============ claim graph: relations between claims ============
-- Append-only and time-directional: from_claim is always the newer, judging
-- claim (ADR-10). Re-judgment belongs to the slow loop, not to edits.
create table if not exists claim_links (
    from_claim bigint not null references claims(id),
    to_claim   bigint not null references claims(id),
    relation   text not null check (relation in ('supports', 'refines', 'contradicts', 'duplicates')),
    confidence real,
    method     text,                       -- model + prompt sha that produced the edge
    created_at timestamptz not null default now(),
    -- Dropped a few lines below and replaced by claim_links_opinion_idx. It is
    -- declared here because this is what fresh databases got until 2026-10-24
    -- and the migration governs both cases from one place; read the end state
    -- there rather than here.
    primary key (from_claim, to_claim, relation)
);

create index if not exists claim_links_to_idx on claim_links (to_claim);

-- Re-judgment needs a row to land in, and until 2026-10-24 it had none. The
-- primary key above was (from_claim, to_claim, relation), so a second opinion
-- that agreed with the first collided with it and `pipeline/interpret.py`'s
-- `on conflict do nothing` dropped it without a word. That made the slow loop
-- ADR-10 promised impossible to record, and it threw away the outcome most
-- worth keeping: a new prompt confirming what an old prompt already said.
--
-- The opinion is the unit, so `method` belongs in the key. It is NULL on every
-- edge drawn before that column existed, and a NULL is never equal to itself in
-- a key, so the index folds NULL to the empty string and reads the whole
-- unattributed era as one opinion. Re-running the same method stays idempotent,
-- which is the job `on conflict do nothing` is actually there for.
create unique index if not exists claim_links_opinion_idx
    on claim_links (from_claim, to_claim, relation, coalesce(method, ''));

-- Then the old key goes, and the order of these two matters. The index above is
-- strictly finer than the key it replaces, so it cannot fail on rows the key
-- already accepted, and creating it first leaves no window where the table has
-- neither. It also carries the (from_claim, to_claim) prefix that the dropped
-- key was quietly serving as an index.
do $$
begin
    if exists (select 1 from pg_constraint
                where conrelid = 'claim_links'::regclass and contype = 'p') then
        alter table claim_links drop constraint claim_links_pkey;
    end if;
end $$;

-- ============ claim graph: which judge has seen which claim ============
-- Slice 5 gave a second opinion somewhere to land. It did not give anything a
-- way to ask for one, and `docs/product/graph-quality.md` named the gap in its
-- own words: the loop needs a trigger that picks claims whose newest opinion
-- predates the current prompt. This table is what that trigger reads.
--
-- Why `claim_links` cannot answer it. An edge is written when the judge found a
-- relation, so a claim judged under October's prompt that found nothing leaves
-- no row at all, and it is indistinguishable from a claim October never read.
-- A trigger keyed on the absence of an edge therefore re-judges the silent
-- claims on every single run, forever, and pays a model call each time. The
-- judgment pass is the thing being tracked, so the judgment pass is the row,
-- and the empty ones are exactly the rows that matter.
--
-- Why the key is the prompt sha and not `method`. `method` is `model@sha` and
-- the model is whichever provider answered: ADR-32's Moonshot normally, Groq's
-- free tier when it did not. Keying re-judgment on `method` would therefore
-- re-judge the whole corpus every time the fallback answered, and again when
-- the primary came back, which is a bill rather than a second opinion. The
-- prompt is the judge's instructions and the model is a capacity accident, so
-- the prompt is what a change of mind is measured against. `method` is kept
-- beside it, because which provider answered is still worth knowing and it is
-- the only place that survives.
create table if not exists claim_judgments (
    claim_id   bigint not null references claims(id),
    prompt_sha text not null,              -- the 12-char sha of prompts/interpret.md
    method     text,                       -- model@sha that answered, NULL if unknown
    edges      integer not null default 0, -- how many relations this pass wrote
    created_at timestamptz not null default now(),
    primary key (claim_id, prompt_sha)
);

create index if not exists claim_judgments_prompt_idx on claim_judgments (prompt_sha);

-- Backfill, and it is the difference between the loop starting correct and the
-- loop starting with a bill. Every claim interpreted before this table existed
-- has no row, so without this the first run under any prompt sees the entire
-- judged corpus as never-judged. The shas already in `claim_links.method` are
-- the real history and they are recoverable, so a claim already judged under
-- today's prompt is recorded as judged under today's prompt and is correctly
-- left alone.
--
-- `created_at` comes from the edges rather than from `now()`: these passes
-- happened, they happened on known dates, and stamping them today would make
-- the table's first reading of its own history a lie.
insert into claim_judgments (claim_id, prompt_sha, method, edges, created_at)
select l.from_claim,
       case when position('@' in coalesce(l.method, '')) > 0
            then split_part(l.method, '@', 2)
            else 'unknown' end,
       min(l.method),
       count(*),
       min(l.created_at)
  from claim_links l
 group by 1, 2
    on conflict do nothing;

-- Then the silent ones: interpreted, no edge to recover a sha from. They are
-- the rows the paragraph above is about, and they are recorded under 'unknown'
-- so the next real prompt reads them once and then never again.
insert into claim_judgments (claim_id, prompt_sha, method, edges, created_at)
select c.id, 'unknown', null, 0, c.interpreted_at
  from claims c
 where c.interpreted_at is not null
   and not exists (select 1 from claim_judgments j where j.claim_id = c.id)
    on conflict do nothing;

-- ============ gold: promotions (human-approved only) ============
create table if not exists promotions (
    id         bigserial primary key,
    claim_ids  bigint[] not null,
    kind       text not null check (kind in ('skill', 'pattern', 'system_diff')),
    path       text,                        -- file path in repo (skills/...) or PR url
    status     text not null default 'proposed'
               check (status in ('proposed', 'approved', 'rejected')),
    created_at timestamptz not null default now(),
    decided_at timestamptz
);

-- ============ slow loop: citation history ============
-- Append-only log of citation counts from Semantic Scholar. Trajectory (this
-- week's count vs. last check) is what "gaining traction" means; a single
-- snapshot can't show it, so this is a log, not a column on papers.
create table if not exists citation_log (
    id         bigserial primary key,
    paper_id   text not null references papers(id),
    citations  int not null,
    checked_at timestamptz not null default now()
);

create index if not exists citation_log_paper_idx on citation_log (paper_id, checked_at desc);

-- ============ digests: the weekly product ============
-- One row per ISO week. This row is the database of record. The digest is
-- never published to the repo (email-only, gitignored digests/) and survives
-- even if the email send fails.
create table if not exists digests (
    id         bigserial primary key,
    week       text not null unique,        -- e.g. '2026-W37'
    body       text not null,               -- the digest markdown
    model      text,
    prompt_sha text,
    created_at timestamptz not null default now()
);

-- ============ press_rehearsals: the scratch print ============
-- A rehearsal is a full press run that writes here instead of to digests and
-- mails nobody (docs/agents/press-rehearsal.md). The separation is the whole
-- point: a rehearsal must never be able to overwrite a published week, so it
-- gets its own table with no unique constraint on week. Many rehearsals of one
-- week are expected, and the newest row is the receipt the deploy chain reads.
create table if not exists press_rehearsals (
    id               bigserial primary key,
    week             text not null,           -- e.g. '2026-W39', not unique
    body             text not null,           -- the digest markdown, unsent
    model            text,                    -- the model that actually answered
    prompt_sha       text,                    -- sha256 of the prompt it was given
    elapsed_seconds  numeric,                 -- wall clock of the model call
    finish_reason    text,                    -- 'stop', 'length', whatever came back
    payload_stats    jsonb,                   -- the same counts weekly() prints
    created_at       timestamptz not null default now()
);

create index if not exists press_rehearsals_recent_idx
    on press_rehearsals (created_at desc);

-- ============ subscribers: the newsletter list ============
-- Source of truth for who receives the digest. Friends-and-family phase sends
-- via Gmail SMTP; past ~20 subscribers this graduates to SES + a real domain
-- + Stripe (docs/vision.md §4). comp = free access (friends).
create table if not exists subscribers (
    id              bigserial primary key,
    email           text not null unique,
    name            text,
    tier            text not null default 'digest' check (tier in ('digest', 'full')),
    comp            boolean not null default false,
    status          text not null default 'active' check (status in ('active', 'unsubscribed')),
    created_at      timestamptz not null default now(),
    unsubscribed_at timestamptz
);

-- Where a subscriber came from: the page whose form they used, or null for
-- the rows the owner added by hand before the site had a form. Added
-- 2026-10-06 with the signup insert in site/lib/waitlist.js, which is the
-- first thing that ever had an answer to put here.
--
-- The status check above still names exactly two states, and that is on
-- purpose. site/lib/waitlist.js's own comment used to ask for a third,
-- 'waitlist', so that a signup could land somewhere the press does not read.
-- pipeline/weekly.py sends to `status = 'active'`, so such a row needs a human
-- to come back and change it, which is the step sprint 2026-10-05's definition
-- of done rules out in clause 1. A signup is active, comped, and done.
alter table subscribers add column if not exists source text;

-- The unsubscribe token (sprint 2026-10-05 item 3). One opaque value per
-- subscriber, carried in the link at the foot of every issue, so that
-- unsubscribing is a click rather than a reply the owner reads and acts on.
--
-- Three statements rather than one `add column ... not null default`, and the
-- reason is worth keeping. A volatile default on ADD COLUMN forces a table
-- rewrite and the per-row evaluation is a property of that rewrite, which is
-- not something this org can test, because it runs no Postgres in CI. If the
-- expression were ever evaluated once instead of per row, every subscriber
-- would share a token and any of them could unsubscribe all of them. An
-- UPDATE has no such ambiguity. So the column arrives nullable, an UPDATE
-- fills the rows that exist, and the default is set afterwards for the rows
-- that do not yet. All three are idempotent, which they have to be: this file
-- is applied in full every time pipeline/db_setup.py runs.
alter table subscribers add column if not exists unsubscribe_token uuid;
update subscribers set unsubscribe_token = gen_random_uuid()
 where unsubscribe_token is null;
alter table subscribers alter column unsubscribe_token set default gen_random_uuid();
create unique index if not exists subscribers_unsubscribe_token_idx
    on subscribers (unsubscribe_token);

-- ============ blackboard queues ============
-- Coordination is the schema, not messages (ADR-9). Each worker's inbox is a
-- view: an item is "claimed" when the worker's output row exists, so every job
-- is resumable from the board's state alone.

create or replace view triage_queue as
    select p.*
    from papers p
    left join triage_log t on t.paper_id = p.id
    where t.id is null;

-- The newest decision per paper, and the only triage row anything downstream
-- reads. Re-triage appends (see triage_log above), so a paper judged `index` in
-- September and `distill` in October has two rows and exactly one current
-- answer. Without this view the join below would return such a paper twice and
-- distill would spend its budget reading the same PDF twice in one run.
create or replace view latest_triage as
    select distinct on (paper_id)
           paper_id, decision, score, reasoning, model, prompt_sha, method,
           created_at
    from triage_log
    order by paper_id, created_at desc, id desc;

-- drop first: adding distilled_at to papers changed this view's column order,
-- which CREATE OR REPLACE refuses to do. It is dropped again now because the
-- join moved from triage_log to latest_triage.
drop view if exists distill_queue;
create view distill_queue as
    select p.*, t.decision as triage_decision
    from papers p
    join latest_triage t on t.paper_id = p.id
        and t.decision in ('distill', 'deep_read')
        and t.model != 'rule:backfill'
    where p.distilled_at is null;

create or replace view interpret_queue as
    select c.*
    from claims c
    where c.interpreted_at is null
      and c.embedding is not null;

-- The current answer per pair, and the same shape as `latest_triage` above.
-- Re-judgment appends (see claim_links), so a pair judged `contradicts` under
-- September's prompt and `supports` under October's has two rows and exactly one
-- current answer. A read that wants today's verdict reads this view. A read that
-- wants how a pair has been judged over time reads `claim_links` and says so.
--
-- `created_at desc` is the recency. The two sort keys after it only break a tie
-- inside a single transaction, where `now()` is identical for every row the run
-- wrote, and they are there so the view answers the same way twice running
-- rather than to carry a meaning of their own.
create or replace view latest_links as
    select distinct on (from_claim, to_claim)
           from_claim, to_claim, relation, confidence, method, created_at
    from claim_links
    order by from_claim, to_claim, created_at desc, method desc, relation desc;

-- Which prompt the graph currently reflects, one row per claim, and the same
-- `distinct on` shape as the two views above it. The trigger itself does not
-- read this, because the trigger asks "has this claim been judged under sha X"
-- and X is a runtime value no view can carry. This answers the question a
-- reader has instead: for each claim, which judge spoke last and what it found.
-- A corpus where every row still says 'unknown' has never been re-judged, and
-- that is a fact worth being able to see in one query.
create or replace view latest_judgment as
    select distinct on (claim_id)
           claim_id, prompt_sha, method, edges, created_at
    from claim_judgments
    order by claim_id, created_at desc, prompt_sha desc;

-- a claim is deprecated when a newer claim contradicts it with confidence;
-- this is ADR-8's "deprecated" digest section as a view.
--
-- It reads latest_links rather than claim_links because a contradiction that a
-- later prompt withdrew is not a deprecation. Before 2026-10-24 this view had no
-- way to tell the two apart, so the older verdict outvoted the newer one for as
-- long as the row existed.
create or replace view deprecated_claims as
    select distinct c.*
    from claims c
    join latest_links l on l.to_claim = c.id
        and l.relation = 'contradicts'
        and coalesce(l.confidence, 0) >= 0.7;

-- a promoted skill needs revision when a claim it cites has since been
-- contradicted by newer evidence (deprecated_claims already computes this
-- for claims; this is the identical check joined against what skills cite,
-- proposed in docs/product/architecture-next.md §2.1)
create or replace view skills_needing_revision as
    select distinct pr.id as promotion_id, pr.path as skill_path,
           pr.claim_ids, dc.id as deprecated_claim_id, dc.claim as deprecated_claim
    from promotions pr
    cross join lateral unnest(pr.claim_ids) as cited(claim_id)
    join deprecated_claims dc on dc.id = cited.claim_id
    where pr.kind = 'skill' and pr.status = 'approved';

-- ============ gold: panel verdicts (ADR-13) ============
-- ADR-13 replaced the human merge gate with three independent reviewer agents
-- (provenance, adversary, validator) and said every verdict is a structured
-- row, so the audit trail replaces the approval queue. This is that row.
--
-- Why it is not a column on `promotions`. The promotion is the proposal, and
-- `promotions.status` is one three-way word for it. Three reviewers produce
-- three verdicts about one proposal, each with its own findings and its own
-- date, and the later slices need to ask "did all three pass, and did they
-- pass the same text". That is a child table, not a column, and the whole
-- point of ADR-13 is that the evidence is recorded rather than summarised.
--
-- `target_sha` is the sha256 of the exact SKILL.md the reviewer read, the same
-- digest `tools/skill_registrar.py` derives and the same one the library's
-- receipts are pinned by. It is what keeps a pass honest: a skill edited after
-- its review carries a verdict for text that no longer exists, so the merge
-- step in ADR-13's third slice can refuse it instead of trusting a stale pass.
-- Without it, "unanimous pass merges the PR" would merge whatever the branch
-- happens to say at merge time.
--
-- Verdicts are append-only. A re-review writes a new row; nothing updates an
-- old one, because the disagreement between two reviews of the same text is
-- the most useful row in the table (the same reasoning as `triage_log`).
create table if not exists panel_verdicts (
    id           bigserial primary key,
    target       text not null,              -- 'skills/<slug>', the proposal reviewed
    reviewer     text not null
                 check (reviewer in ('provenance', 'adversary', 'validator')),
    verdict      text not null
                 check (verdict in ('pass', 'fail', 'unknown')),
    findings     jsonb not null default '[]'::jsonb,
    target_sha   text not null,              -- sha256 of the SKILL.md judged
    reviewer_sha text,                       -- git blob sha of the reviewer's own code
    model        text,                       -- NULL for a reviewer that calls no model
    created_at   timestamptz not null default now()
);

create index if not exists panel_verdicts_target_idx
    on panel_verdicts (target, reviewer, created_at desc);

-- the newest verdict each reviewer has filed about each target
create or replace view panel_latest as
    select distinct on (target, reviewer)
           target, reviewer, verdict, findings, target_sha, reviewer_sha,
           model, created_at
    from panel_verdicts
    order by target, reviewer, created_at desc;

-- ADR-13's gate as arithmetic: unanimous means three passes on one text.
-- The 3 is the panel's size as the ADR fixes it, written here rather than
-- inferred from how many reviewers happen to have filed, because a panel of
-- one that passed is exactly the thing this must not read as unanimous.
create or replace view panel_consensus as
    select target,
           count(*) as verdicts,
           count(*) filter (where verdict = 'pass') as passes,
           count(*) filter (where verdict = 'fail') as fails,
           count(distinct target_sha) = 1 as one_text,
           (count(*) filter (where verdict = 'pass') = 3
            and count(distinct target_sha) = 1) as unanimous,
           max(created_at) as latest
    from panel_latest
    group by target;

create index if not exists papers_embedding_idx
    on papers using hnsw (embedding vector_cosine_ops);
create index if not exists claims_embedding_idx
    on claims using hnsw (embedding vector_cosine_ops);
create index if not exists triage_log_paper_idx on triage_log (paper_id);
create index if not exists claims_topics_idx on claims using gin (topics);

-- institutions: the labs/universities behind a paper, extracted from full text
-- at distill time — attribution in the digest ("researchers at X") needs them
alter table papers add column if not exists institutions text[];

-- institutions_checked_at: when pipeline/backfill_institutions.py last asked
-- arXiv for this paper's header, answered or not. Distinct from the column
-- above being empty, which cannot tell "nobody has looked" from "arXiv has no
-- HTML for this one", and without the difference the backfill re-fetches the
-- same unanswerable papers on every run. RECHECK_DAYS in that file lets a
-- paper come round again, because arXiv renders HTML weeks after a posting.
alter table papers add column if not exists institutions_checked_at timestamptz;

-- ============ users: accounts (ADR-30) ============
-- Neon is the system of record for who has an account; Clerk is a surface
-- that can be swapped without losing a user or their history. The row is
-- keyed by clerk_id because that is what a session carries, and it is the
-- only Clerk-shaped thing in here. Migrating off Clerk means re-issuing
-- credentials by email re-auth against these rows, never re-creating them.
--
-- This table is the account. It is NOT the newsletter list: `subscribers`
-- below stays independent, because someone may read the digest forever
-- without ever making an account, and an account may exist with no
-- subscription. The two are joined on lower(email), never merged.
create table if not exists users (
    clerk_id            text primary key,
    email               text not null,
    name                text,
    -- The tier this account pays for. 'free' until payments open; ADR-30
    -- keeps the door closed this release, so nothing writes anything else
    -- yet. Polar is the processor when it does (merchant of record).
    subscription_status text not null default 'free'
                        check (subscription_status in ('free', 'active', 'past_due', 'canceled')),
    polar_customer_id   text,                 -- unused until payments open
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

-- Email uniqueness is enforced case-insensitively, not by a plain unique
-- constraint, because the join to subscribers is on lower(email). A plain
-- unique(email) would let Ada@x.com and ada@x.com both exist as accounts,
-- and then "the user for this subscriber" would have two honest answers.
-- This index is what makes that join single-valued, and it is also the
-- index the join reads.
create unique index if not exists users_email_lower_idx on users (lower(email));

-- The other half of the same join. subscribers predates this table and has
-- a plain unique(email), which does not rule out case variants, so the
-- unique version of this index can fail on legacy rows. Attempt it, and
-- fall back to a non-unique index plus a loud warning rather than aborting
-- the rest of the schema: an un-deduped digest list is a data problem for
-- the owner to fix, not a reason for `psql -f db/schema.sql` to stop.
do $$
begin
    if exists (
        select 1 from subscribers group by lower(email) having count(*) > 1
    ) then
        raise warning 'subscribers holds case-variant duplicate emails; creating a NON-unique index. Dedupe with: select lower(email), count(*) from subscribers group by 1 having count(*) > 1;';
        create index if not exists subscribers_email_lower_idx on subscribers (lower(email));
    else
        create unique index if not exists subscribers_email_lower_idx on subscribers (lower(email));
    end if;
end $$;

-- The linkage, as a view, so no caller has to remember which side is which
-- or that the comparison is case-folded. LEFT join on purpose: an account
-- with no digest subscription is an ordinary account, not a missing row.
-- Read it by clerk_id.
create or replace view user_accounts as
    select u.clerk_id,
           u.email,
           u.name,
           u.subscription_status,
           u.polar_customer_id,
           u.created_at,
           s.id      as subscriber_id,
           s.tier    as digest_tier,
           s.status  as digest_status,
           s.comp    as digest_comp
    from users u
    left join subscribers s on lower(s.email) = lower(u.email);

-- ============ auth_attempts: the passphrase throttle (mcp/oauth_flow.py) ============
-- One row, keyed 'mcp-authorize', counting consecutive wrong passphrases on
-- POST /authorize. It lives in Postgres rather than in the server's memory for
-- one reason: the MCP container scales to zero, so an in-process counter is
-- reset by every cold start and kept separately by every replica, which is the
-- same as no counter at all to anyone patient enough to notice.
--
-- The right passphrase deletes the row. A row whose last_fail is older than the
-- decay window is treated as a finished run of failures, not a continuing one.
create table if not exists auth_attempts (
    scope      text primary key,
    fails      integer not null default 0,
    last_fail  timestamptz not null default now()
);


-- ============ consumed_codes: single-use authorization codes (mcp/oauth_flow.py) ============
-- One row per successful OAuth login. The row's name is the `jti` claim of the
-- authorization code that was spent, and every access and refresh token issued
-- from that code carries the same name in its `sid` claim. So the row is really
-- the session, which is why two things are true about it.
--
-- The insert is the single-use check itself: `on conflict do nothing returning`
-- hands a row back only to the caller that created it, so a code presented
-- twice is refused even if the two attempts land on different replicas. A
-- read-then-write would race here. This does not.
--
-- And `expires_at` is when the longest-lived token from that login dies, not
-- when the 60-second code did. Purging on the code's own expiry would drop the
-- row a minute after login and leave nothing to mark revoked for the 180 days
-- the refresh token still works. Rows past expires_at are deleted opportunist-
-- ically by the same statement that spends the next code.
create table if not exists consumed_codes (
    jti         text primary key,
    consumed_at timestamptz not null default now(),
    expires_at  timestamptz not null,
    revoked     boolean not null default false
);

create index if not exists consumed_codes_expires_idx on consumed_codes (expires_at);

-- ============ skill registration (ADR-36) ============
-- `skills_needing_revision` above has existed since the founding and had never
-- returned a row, because it reads `promotions` and nothing ever wrote a
-- promotions row for a skill. The skill seat writes a SKILL.md into the
-- repository and the owner merges it, and that was the whole promotion. So the
-- view joined an empty table, seven claims went deprecated, no skill knew, and
-- the site went on saying a skill is revised when the research moves.
--
-- `tools/skill_registrar.py` derives the row from the skill's own provenance
-- block. This index is what lets it run every day without writing a second row
-- for a skill it already registered: the skill's directory is its identity, so
-- `on conflict (path) where kind = 'skill'` updates the claim ids in place when
-- a revision adds a paper.
--
-- Partial rather than plain, on purpose. `promotions` also holds `pattern` and
-- `system_diff` rows whose `path` is a pull request url, and two system diffs
-- may well point at one PR. Only a skill's path is an identity.
create unique index if not exists promotions_skill_path_idx
    on promotions (path) where kind = 'skill';

-- `live_at`: when a self-improvement proposal actually started running.
-- Sprint 2026-10-26 item 4, and the column the 2026-10-18 OKR check-in was
-- reaching for when it graded O3 KR2 "met on the letter, not on the spirit."
--
-- `status` and `decided_at` are about the human gate (ADR-7): a merge is the
-- approval. They were also, until this column, the only thing the loop could
-- call its own ending, and that is the defect. `modal deploy` bakes the
-- repository into an image, so a merge and a deploy are two events, and
-- `INC-2026-10-12-meta-review-proposal-merged-never-deployed` is what lives in
-- between them: `prompts/triage.md` changed on 2026-10-05, the triage job went
-- on running the prompt of 2026-09-29, and 8,861 rows were judged against the
-- old one.
--
-- So the two facts get two columns. `decided_at` says a human approved it.
-- `live_at` says the image that reads the file is running code that contains
-- the merge, which is the question `tools/loop_close.py` asks and the only
-- answer that closes the loop. A row with `decided_at` set and `live_at` null
-- is a merge that has bought nothing yet, and that row is now countable.
alter table promotions add column if not exists live_at timestamptz;

-- Partial, because the query this serves is "what is still open" and a loop
-- that has closed is never asked about again.
create index if not exists promotions_open_system_diff_idx
    on promotions (id) where kind = 'system_diff' and live_at is null;

-- ============ deploy_runtime: what each scheduled job is actually running ============
-- Sprint 2026-09-28 item 2. `modal deploy` bakes the repository into an image,
-- so a merge to main and a deploy are two events, and the org has twice
-- discovered days later that the second one never happened: incident 24, and
-- PR #110, merged 2026-09-26 and inert while three documents called it live.
--
-- One row per app, written by the job itself at the top of every run from
-- `pipeline/runtime_sha.py`. The digest covers the module and every file its
-- Modal image adds, keyed by repository path, so `tools/delivery_health.py`
-- can compare it against the same digest computed from a git checkout.
--
-- Three times, because they answer three different questions. `recorded_at`
-- is when the job last ran at all. `first_seen_at` is when this exact deploy
-- started running, which is how you answer "when did the fix actually go
-- live". `notified_at` is the drift alarm's own cooldown, so a deploy that
-- stays stale for a week costs the owner one mail a day and not one per check;
-- it resets to null whenever the running sha changes, because a new deploy is
-- a new fact and the next drift deserves its own first alarm.
create table if not exists deploy_runtime (
    app           text primary key,          -- 'triage' | 'interpret' | 'weekly'
    runtime_sha   text not null,             -- 12 hex chars, runtime_sha.digest()
    entrypoint    text not null,             -- 'pipeline/triage.py', for the deploy command
    file_count    integer not null,          -- how many files the digest covered
    recorded_at   timestamptz not null default now(),
    first_seen_at timestamptz not null default now(),
    notified_at   timestamptz
);

-- retag_log: the one-time Layer 4 retag's record of what it has judged
-- (pipeline/retag_threads.py, owner directive 2026-10-05).
--
-- This table is what makes that job resumable, and it needs saying why, because
-- the sibling job pipeline/backfill_topics.py needs no such table. That one's
-- fold is a pure function, so a repaired row repairs to itself and "already
-- done" is derivable from the row. The retag asks a model instead, and a model
-- that reads a claim and correctly decides it needs none of the four new tags
-- leaves `claims.topics` byte-identical to a row nobody has looked at. So
-- "judged" is not derivable from the claims table, and without this row the
-- job would pay for the same declined call on every run forever.
--
-- It is also the audit trail. `model` and `added` together mean a tag written
-- by that backfill stays distinguishable from one the distiller chose, which
-- matters because the research seat's census of 2026-09-30 found that the
-- keyword match these claims were selected by is not evidence of anything.
-- `why` is the model's own sentence, kept so a wrong tag can be argued with
-- rather than only reverted.
create table if not exists retag_log (
    claim_id   bigint primary key references claims(id),
    judged_at  timestamptz not null default now(),
    model      text not null,             -- whichever model answered, logged
    added      text[] not null default '{}',   -- empty is the common answer
    why        text
);

-- ======== payment_exceptions: money that arrived and did not become access ========
--
-- The payments layer's alarm path (site/lib/polar.js, ADR-30, ADR-31). The
-- corpus has one already: pipeline/notify.py mails the owner when a job
-- fails. The site had none, so every site-side failure was a
-- `console.error` in a Vercel function log that nothing in this org reads,
-- and the two outcomes that cost the most are exactly the two that end
-- there. A buyer with no Clerk account cannot be granted anything, and an
-- email matching two accounts matches neither. Both are correct refusals
-- and both are a paid customer with no access, discovered when they write
-- in rather than on the day it happened.
--
-- So the refusal gets a row instead of a line. `tools/delivery_health.py`
-- counts the unresolved ones through the public receipt, which means the
-- daily standup reads it with no credential, and the same row answers the
-- owner's first question when somebody does write in: did we get their
-- money and what did we do with it.
--
-- **This table holds no money and no card.** Polar is the Merchant of
-- Record, so the charge, the card and the invoice all live there. What is
-- here is the identifier needed to find that record in Polar's dashboard
-- and the reason this product could not act on it.
--
-- `event_id` is Polar's own webhook delivery id, from the `webhook-id`
-- header the signature covers, and it is unique on purpose. Polar retries a
-- delivery this endpoint answered with a 503, so without that constraint one
-- stuck payment would write a row every retry for a day and the count the
-- standup reads would measure Polar's retry schedule rather than the number
-- of people affected. One row per delivery, `attempts` counting the retries,
-- is the number a human would want.
--
-- `resolved_at` is what makes the count trustworthy in the other direction.
-- A deferred event whose retry later succeeds resolves its own row, so the
-- unresolved count falls back to zero without anybody clearing it by hand.
-- A count that only ever rises is a count the org learns to ignore, which is
-- incident 20's shape and the reason this column is not an afterthought.
create table if not exists payment_exceptions (
    id                  bigserial primary key,
    -- Polar's webhook delivery id. One row per delivery, however many times
    -- it is retried.
    event_id            text not null unique,
    event_type          text not null,          -- 'subscription.active', 'order.paid', ...
    -- Why this product could not turn the payment into access. Checked
    -- rather than free text, because the count the standup reads is grouped
    -- by it and a typo would become a category.
    reason_code         text not null
                        check (reason_code in ('no_account',
                                               'ambiguous_email',
                                               'lookup_failed',
                                               'no_users_row',
                                               'no_database',
                                               'handler_threw')),
    -- Whether Polar will bring this event back by itself. A deferred row may
    -- resolve on its own; a refused one never will and needs a hand.
    retryable           boolean not null default false,
    attempts            integer not null default 1,
    detail              text,                   -- the reason sentence, for a reader
    -- Where to find the charge in Polar's dashboard. Nullable because an
    -- event that threw before it was parsed carries none of them.
    polar_customer_id   text,
    polar_subscription_id text,
    -- The address the buyer gave Polar, which is how the owner reaches them
    -- to invite them or to merge the duplicate. Lower-cased by subjectOf(),
    -- the same folding `users_email_lower_idx` uses.
    email               text,
    occurred_at         timestamptz not null default now(),
    last_seen_at        timestamptz not null default now(),
    resolved_at         timestamptz,
    resolved_note       text
);

-- The index the standup's count reads: unresolved rows, newest first. Partial,
-- because the resolved rows are history and the alarm only ever asks about the
-- open ones, so the index stays the size of the problem rather than the size of
-- the table.
create index if not exists payment_exceptions_open_idx
    on payment_exceptions (occurred_at desc)
    where resolved_at is null;

-- ============ path_events: the buyer's path, counted and never identified ============
-- Board card c688ef2e, "Build a way to measure the buyer's path". Until this
-- table existed, nothing in this product recorded a visit, and the card's own
-- sentence is why that mattered: without it nobody can tell which skill
-- actually sells.
--
-- **What this table deliberately does not hold, and the sentence that decided
-- it.** `site/app/privacy/page.jsx` promises a reader that "there is no
-- analytics, no tracking pixel, no advertising network, and no third-party
-- script watching you read". So there is no address here, no user agent, no
-- cookie, no session, no referrer and no identifier of any kind, not even an
-- irreversible hash of one. Every cookieless analytics product ships that
-- hash and it is still a pseudonymous identifier for one person, which is the
-- thing the promise rules out.
--
-- The cost of that is real and it is stated rather than hidden: a conversion
-- rate is not computable from these rows. Two steps counted here are two
-- counts of events and not two counts of the same people, so
-- `tools/buyer_path.py` reports the counts and refuses the ratio. What the
-- card asks for survives the refusal, because which skill sells is a count
-- per skill.
--
-- `step` is checked rather than free text for the reason `payment_exceptions`
-- gives above: the funnel is grouped by it, so a typo would quietly become a
-- sixth step. `site/lib/path-core.js` holds the same five words and
-- tests/path.test.mjs asserts the two lists agree, so a step added to one and
-- not the other fails on the pull request that adds it.
--
-- `detail` is the one varying field and it is bounded and sanitised in
-- `path-core.js` before it arrives: a skill's slug on a `skill` row, a plan id
-- on a `checkout` row, and null everywhere else. It is never a query string,
-- because a query string is where an address ends up by accident.
create table if not exists path_events (
    id          bigserial primary key,
    step        text not null
                check (step in ('visit', 'catalog', 'skill', 'pricing', 'checkout')),
    -- The route, normalised to the shape the funnel groups by, so that
    -- /library/2026-W39 and /library/2026-W40 are one row's worth of path
    -- rather than one path each.
    path        text not null,
    detail      text,
    occurred_at timestamptz not null default now()
);

-- The index the funnel reads: a window of recent rows, grouped by step. Both
-- queries in site/lib/path.js start from a time bound, so the time column
-- leads.
create index if not exists path_events_recent_idx
    on path_events (occurred_at desc, step);

-- Which skill sells, which is the card's own question, so it gets an index
-- rather than a sequential scan over every visit ever recorded. Partial,
-- because only `skill` rows carry a slug and that is a small fraction of the
-- table, so the index stays the size of the question.
create index if not exists path_events_skill_idx
    on path_events (detail, occurred_at desc)
    where step = 'skill';

-- The shape a human reads, and the shape the daily reader asks for: one row
-- per day per step. A view rather than a rollup table, because the volume
-- this product sees pre-launch is counted in hundreds and a materialised copy
-- would be a second number that can disagree with the first.
create or replace view buyer_path_daily as
    select date_trunc('day', occurred_at)::date as day,
           step,
           count(*) as events
    from path_events
    group by 1, 2;
