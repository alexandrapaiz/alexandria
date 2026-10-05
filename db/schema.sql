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
-- the paper's source class and whether the model found a measurement in the
-- evidence it wrote (pipeline/evidence.py holds the rules and the reasoning).
-- NULL means ungraded, which is every claim distilled before this column
-- existed; nothing backfills it, because the measurement judgment belongs to
-- the run that read the source.
alter table claims add column if not exists evidence_grade text;

do $$
begin
    if not exists (select 1 from pg_constraint where conname = 'claims_evidence_grade_check') then
        alter table claims add constraint claims_evidence_grade_check
            check (evidence_grade is null or evidence_grade in
                   ('controlled', 'field_measured', 'asserted', 'anecdote'));
    end if;
end $$;

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
