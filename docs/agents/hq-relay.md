# Relay to HQ — what alexandria owes Alexandra Systems upward

**Enforced at:** prompts/exo-agent.md §3e. The ExO seat writes entries.
The chair carries them, because no automated channel exists yet.

Seats never message each other and no seat in this repository can write
to `alexandrapaiz/alexandra-systems`. So evidence that matters to the
parent stops here unless a human moves it. This file is the outbox. Each
entry is written to be copied into an HQ issue or a chair message with
no editing, per the standard the PM's dispatch queue already uses: if
the carrier has to compose anything, the note did not work.

An entry stays until the chair marks it delivered with a date.

---

## 2026-09-24 — Kimi routing failed alexandria's PM seat twice, and the same class hit HQ's own seats

**Status: undelivered.**

**For:** whoever owns HQ ADR-015.

**The short version.** ADR-015's open routing has now produced four
failed runs across two repositories and zero successful ones. Alexandria
has removed the secrets and fallen back to Sonnet. The rollout also
skipped a safety gate that alexandria's own routing law requires, and
nobody here knew the model had changed until three days later. The
direction is not in question. The rollout shape is.

**The evidence, alexandria side.** Commit 609d7cc, merged 2026-09-19
18:49 UTC, gave `agent-pm.yml`, `agent-market.yml`, `agent-okr.yml` and
`agent-finance.yml` a preferred run step on `kimi-k2.7-code`.

- Run 35493791740, 2026-09-20: `is_error: true` at `num_turns: 1`,
  empty `modelUsage`, `total_cost_usd: 0`. The endpoint did not serve
  the request at all. This is plumbing, not quality.
- Run 35626266985, 2026-09-21: the model answered, worked twelve
  minutes, then `is_error: true` at `num_turns: 30` against a cap of
  300. The no-ship tripwire fired, so the run had made commits it never
  pushed. This one is quality, and specifically it is tool-calling
  reliability on a long agentic run.

Read those two apart. They are different failures and only the second is
evidence about the model.

**The evidence, HQ side, as reported to alexandria's owner.** pm 2/2
failed, finance 1/3, okr 1/2. Same week, same routing, same seats by
role. Two products producing the same failure distribution independently
is a stronger result than either one alone, and neither of us had the
other's numbers until the owner carried them by hand.

**Three things alexandria asks HQ to consider.**

1. **The rollout order is backwards.** ADR-015 routed the PM first in
   both repositories. The PM is the fleet-health seat, it is the seat
   that reports run failures to the owner, and under company ADR-033 it
   is now the only seat with dispatch authority. So the experiment was
   run on the seat whose absence makes every other failure harder to
   see. Route the seat whose failure costs least. In alexandria that is
   finance, which is dormant, or okr, which runs monthly.

2. **The either/or shape turns a routing experiment into a lost run.**
   Both workflows' Claude step is guarded by `if: env.OPENROUTE == ''`,
   so it is unreachable by construction while the key exists. A failed
   open-model attempt should cost three minutes, not the run. The two
   line fix is written out in full in
   `docs/agents/pending-workflow-changes.md` item 1b in this repository,
   and it applies verbatim to HQ's copies. Alexandria's position is that
   the secrets do not come back here until that is applied, because
   re-adding the key today re-arms the identical failure on the identical
   seat.

3. **The gate that was skipped.** `docs/agents/model-routing.md` in this
   repository requires a golden-set comparison before any seat leaves
   its explicit model. It was written on 2026-09-17 and it names the
   exact hazard that then occurred, in these words: "open-model
   tool-calling reliability on long agentic runs." The gate was not
   overruled, it was not seen. Alexandria is not claiming HQ meant to
   drop it.

**The general point, which is the reason this note exists at all.** A
parent decision changed a subsidiary's machinery with no record inside
the subsidiary except a commit subject, and overrode a local safety
clause without either party noticing there was one. That is a mechanism
rather than a mistake, and it will recur on the next ADR unless the
shape changes. Alexandria's proposed rule is in
`docs/agents/cross-repo-law.md` and it is short: parent decisions govern
and they do not take effect silently, which means one entry in the
subsidiary's decisions file, one line in the local law that is being
overridden, and the affected seats told in a file their charters
already read. It is not a veto and it adds no approval step. Alexandria
offers it as a candidate for the standards set, since every product HQ
bootstraps will have the same exposure the moment it writes its first
local law.

**One thing HQ may already have and alexandria does not.** Whether
ADR-015 was accompanied anywhere by a measurement of what open routing
was expected to save. Alexandria's routing register has the lever
analysis but no number. If the saving is large the calculus on retrying
changes, and if it is small the four failed runs already cost more than
the experiment can return.

---

## Delivery log

| Entry | Written | Delivered | By |
| --- | --- | --- | --- |
| Kimi routing failed alexandria's PM seat twice | 2026-09-24 | not yet | |
