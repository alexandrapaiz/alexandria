# Diagram atlas

Every architecture diagram in one place, rendered natively by GitHub. Diagrams
drawn in chat are ephemeral; these are the durable copies. Numbers in the
status diagram are a dated snapshot — the database is always the truth.

Companion diagrams elsewhere: the **logical view** and **deployment view** are
in the [README](../README.md); the **current vs. institutional stack** is in
[stack.md](stack.md); the **schema/ERD** is [schema.sql](../db/schema.sql)
itself.

## Pipeline status — snapshot 2026-09-08

Green = live and ran today. Dashed = left to build. The frontier sits between
the interpret worker and the weekly digest.

```mermaid
flowchart TB
    classDef live fill:#0F6E56,stroke:#5DCAA5,color:#E1F5EE
    classDef todo fill:none,stroke:#888780,stroke-dasharray:5 4,color:#888780

    SRC["Sources — 16 feeds · 7 arXiv categories"]:::live
    ING["Ingest 11:00 UTC — 2,312 papers in bronze"]:::live
    TRI["Triage 12:00 UTC — 1,446 routed four ways"]:::live
    DIS["Distill 11:30 UTC — 80 claims, all embedded"]:::live
    INT["Interpret 14:00 UTC — 22 edges · 1 deprecated"]:::live
    DIG["Weekly digest — next build"]:::todo
    GOLD["Promotion → gold skills"]:::todo
    META["Meta-review — proposes PRs to itself"]:::todo
    SLOW["Slow loop — citations · retrospectives"]:::todo

    SRC --> ING --> TRI --> DIS --> INT
    INT -. you are here .-> DIG
    DIG --> GOLD
    DIG --> META
    META --> SLOW
```

## The blackboard — workers around the shared database

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
        G[("gold — empty, awaits promotion")]:::store
    end
    ING2 --> B
    TRI2 --> L
    DIS2 --> S
    INT2 --> S
    NEON --> BRIEF["Weekly digest — planned next"]:::todo
    BRIEF --> YOU["You — review, promote (optional at end state)"]:::human
    YOU --> G
    NEON --> META2["Meta-review — proposes PRs, later"]:::todo
```

## The agent loop, unrolled onto the pipeline

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
