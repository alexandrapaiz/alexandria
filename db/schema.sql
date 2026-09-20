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
    primary key (from_claim, to_claim, relation)
);

create index if not exists claim_links_to_idx on claim_links (to_claim);

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

-- ============ blackboard queues ============
-- Coordination is the schema, not messages (ADR-9). Each worker's inbox is a
-- view: an item is "claimed" when the worker's output row exists, so every job
-- is resumable from the board's state alone.

create or replace view triage_queue as
    select p.*
    from papers p
    left join triage_log t on t.paper_id = p.id
    where t.id is null;

-- drop first: adding distilled_at to papers changed this view's column order,
-- which CREATE OR REPLACE refuses to do
drop view if exists distill_queue;
create view distill_queue as
    select p.*, t.decision as triage_decision
    from papers p
    join triage_log t on t.paper_id = p.id
        and t.decision in ('distill', 'deep_read')
        and t.model != 'rule:backfill'
    where p.distilled_at is null;

create or replace view interpret_queue as
    select c.*
    from claims c
    where c.interpreted_at is null
      and c.embedding is not null;

-- a claim is deprecated when a newer claim contradicts it with confidence;
-- this is ADR-8's "deprecated" digest section as a view
create or replace view deprecated_claims as
    select distinct c.*
    from claims c
    join claim_links l on l.to_claim = c.id
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

create index if not exists papers_embedding_idx
    on papers using hnsw (embedding vector_cosine_ops);
create index if not exists claims_embedding_idx
    on claims using hnsw (embedding vector_cosine_ops);
create index if not exists triage_log_paper_idx on triage_log (paper_id);
create index if not exists claims_topics_idx on claims using gin (topics);

-- institutions: the labs/universities behind a paper, extracted from full text
-- at distill time — attribution in the digest ("researchers at X") needs them
alter table papers add column if not exists institutions text[];

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
