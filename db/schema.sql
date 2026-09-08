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

-- ============ blackboard queues ============
-- Coordination is the schema, not messages (ADR-9). Each worker's inbox is a
-- view: an item is "claimed" when the worker's output row exists, so every job
-- is resumable from the board's state alone.

create or replace view triage_queue as
    select p.*
    from papers p
    left join triage_log t on t.paper_id = p.id
    where t.id is null;

create or replace view distill_queue as
    select p.*, t.decision as triage_decision
    from papers p
    join triage_log t on t.paper_id = p.id
        and t.decision in ('distill', 'deep_read')
        and t.model != 'rule:backfill'
    left join claims c on c.paper_id = p.id
    where c.id is null;

create index if not exists papers_embedding_idx
    on papers using hnsw (embedding vector_cosine_ops);
create index if not exists claims_embedding_idx
    on claims using hnsw (embedding vector_cosine_ops);
create index if not exists triage_log_paper_idx on triage_log (paper_id);
create index if not exists claims_topics_idx on claims using gin (topics);
