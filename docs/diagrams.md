# Diagram atlas

Every architecture diagram in one place, rendered natively by GitHub. Diagrams
drawn in chat are ephemeral, and these are the durable copies. Numbers in the
status diagram are a dated snapshot, and the database is always the truth.

The system has two layers and this atlas holds both. Diagrams 1 to 3 are the
pipeline, which is what the company makes. Diagram 4 is the org, which is who
makes it.

Companion diagrams elsewhere: the **two-layer architecture** and the
**deployment view** are in the [README](../README.md); the **current vs.
institutional stack** is in [stack.md](stack.md); the **product pipeline in
three layers** is in [product/pipeline.md](product/pipeline.md); the
**schema/ERD** is [schema.sql](../db/schema.sql) itself; and the seat-by-seat
table behind diagram 4 is [agents/org-chart.md](agents/org-chart.md).

## 1. Pipeline status — structure current 2026-09-18, counts from 2026-09-08

Green = live. Dashed = left to build. The frontier has moved twice since this
diagram was first drawn: the weekly digest, the slow citation loop, and the
first promotions to gold have all shipped, and the frontier now sits at the
reviewer panel (ADR-13) that is meant to replace the owner as the gate on gold.

The per-node counts below are the 2026-09-08 snapshot and are known to be low.
The one fresher number on record is 441 claims in silver on 2026-09-18, counted
directly against the database by the skill agent (PR #16). Refreshing the rest
needs database access this seat does not have, so it is ledgered for the
engineer rather than guessed at here.

```mermaid
flowchart TB
    classDef live fill:#0F6E56,stroke:#5DCAA5,color:#E1F5EE
    classDef todo fill:none,stroke:#888780,stroke-dasharray:5 4,color:#888780

    SRC["Sources — 22 feeds · 6 arXiv categories · HF daily papers"]:::live
    ING["Ingest 11:00 UTC — 2,312 papers in bronze"]:::live
    TRI["Triage 12:00 UTC — 1,446 routed four ways"]:::live
    DIS["Distill 11:30 UTC — 80 claims, all embedded"]:::live
    INT["Interpret 14:00 UTC — 22 edges · 1 deprecated"]:::live
    DIG["Weekly digest Mon 15:00 UTC — live, first edition 2026-W37"]:::live
    SLOW["Slow loop — citations via Semantic Scholar, in the weekly cron"]:::live
    GOLD["Promotion to gold — 2 skills merged, owner-approved"]:::live
    PANEL["Reviewer panel (ADR-13) — replaces the owner as the gate"]:::todo
    META["Meta-review — the research seat's loop (ADR-25)"]:::todo

    SRC --> ING --> TRI --> DIS --> INT
    INT --> DIG
    DIG --> SLOW
    DIG --> GOLD
    GOLD -. you are here .-> PANEL
    DIG --> META
```

## 2. The blackboard — workers around the shared database

No worker talks to another. Each reads its inbox as a SQL view over what has
not yet been done; state lives in Postgres, so any worker can die mid-run and
resume at the next cron.

```mermaid
flowchart TB
    classDef live fill:#0F6E56,stroke:#5DCAA5,color:#E1F5EE
    classDef store fill:#085041,stroke:#5DCAA5,color:#E1F5EE
    classDef todo fill:none,stroke:#888780,stroke-dasharray:5 4,color:#888780
    classDef human fill:#993C1D,stroke:#F0997B,color:#FAECE7

    ING2["Ingest"]:::live
    DIS2["Distill"]:::live
    TRI2["Triage"]:::live
    INT2["Interpret"]:::live
    subgraph NEON["Neon Postgres — the blackboard"]
        B[("bronze — 2,312 papers")]:::store
        L[("triage log — 1,446 rows")]:::store
        S[("silver — 80 claims · 22 edges")]:::store
        G[("gold — 2 skills promoted")]:::store
    end
    ING2 --> B
    TRI2 --> L
    DIS2 --> S
    INT2 --> S
    NEON --> BRIEF["Weekly digest — live, Mondays"]:::live
    BRIEF --> YOU["Owner — reviews, merges, promotes (optional at end state)"]:::human
    YOU --> G
    NEON --> META2["Meta-review — the research seat, from 2026-09-21"]:::todo
```

## 3. The agent loop, unrolled onto the pipeline

The classic perceive → memory → reason → act → observe loop is what the daily
pipeline *is*, spread across cron jobs:

```mermaid
flowchart LR
    P["Perceive — ingest pulls the day's papers"] --> M["Memory — bronze/silver/gold + claim graph"]
    M --> R["Reason — triage routes · distill extracts · interpret judges"]
    R --> A["Act — write claims, edges, (later) skills + PRs"]
    A --> O["Observe — triage log + human verdicts"]
    O --> P
```

## 4. The org — the week as a loop, and the one gate at the end of it

Added 2026-09-18 by the ExO agent. Every diagram in this atlas until now drew
the pipeline and none drew the organization that builds it, which stopped being
accurate the week eleven agent seats went live (ADR-14 through ADR-25).

Read it as a heartbeat. The weekly seats hand the week around a ring, the
engineer runs underneath every morning, two seats keep a slower beat, and every
one of them ends its run the same way: one branch, one pull request, no merge.
The owner is the only node in the whole organization that can change main, which
is the same gate ADR-7 put on the pipeline, applied to the workers themselves.

```mermaid
flowchart TB
    classDef seat fill:#0F6E56,stroke:#5DCAA5,color:#E1F5EE
    classDef human fill:#993C1D,stroke:#F0997B,color:#FAECE7
    classDef store fill:#085041,stroke:#5DCAA5,color:#E1F5EE
    classDef todo fill:none,stroke:#888780,stroke-dasharray:5 4,color:#888780

    subgraph WEEK["The weekly ring"]
        direction LR
        MON["<b>Mon</b><br/>pm plans the sprint<br/>research ranks what to read"]:::seat
        TUE["<b>Tue</b><br/>skill extracts one skill"]:::seat
        WED["<b>Wed</b><br/>frontend verifies the pixels"]:::seat
        FRI["<b>Fri</b><br/>market reads the outside"]:::seat
        SUN["<b>Sun</b><br/>exo reviews the workers,<br/>itself included"]:::seat
        MON --> TUE --> WED --> FRI --> SUN --> MON
    end

    ENG["<b>engineer</b><br/>every morning, 7:06 ET"]:::seat
    SEC["<b>security</b><br/>1st and 15th"]:::seat
    OKR["<b>okr</b><br/>1st of the month"]:::seat
    DORM["<b>finance · sales</b><br/>dormant until the owner<br/>adds one cron line"]:::todo

    PR["One branch, one pull request per run<br/>deviations confessed in the description"]
    OWNER{"Owner merges<br/>the only write to main"}:::human
    MAIN[("main — code · prompts · charters · skills")]:::store

    WEEK --> PR
    ENG --> PR
    SEC --> PR
    OKR --> PR
    DORM -.-> PR
    PR --> OWNER --> MAIN
    MAIN -.->|"charters and workflows change the seats"| WEEK
    MAIN -.->|"the pipeline the seats build"| PIPE["Diagrams 1 to 3"]
```

The recursion worth noticing is the dotted line back into the ring. The ExO
seat's own charter is a file on main, so a Sunday run that improves the
organization improves the thing that will improve the organization next Sunday,
and it still cannot apply a word of it without the owner merging. The org's
memory of what those runs found lives in
[agents/learning-log.md](agents/learning-log.md) and
[agents/incidents.md](agents/incidents.md), because every run starts with an
empty context.
