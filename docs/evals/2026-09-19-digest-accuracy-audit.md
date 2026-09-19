# Digest accuracy audit, every issue sent to date

Sprint 2026-09-21, item 3. Engineer agent, 2026-09-19.

The owner's finding was that roughly two issues have gone out with no
testing or validation of them. This is the retroactive check: every claim
in everything sent, read against the paper it rests on.

The short version. One issue exists, not two, and the repo cannot prove
how many times it was mailed. Of 34 checkable claims in it, 25 hold, 3 are
wrong, 4 are overstated or unsourced in a way a careful reader would catch,
and 2 could not be settled at all. The three wrong ones are fixed in the
public archive as of this audit, with a correction note on the issue.

## How many issues actually went out

The sprint asked for the real count first. The two sources of truth for it
are the `digests` table and the Gmail sent log, and neither was reachable
from this session: `NEON_RO_URL` is not wired into
`.github/workflows/agent-engineer.yml`, and the Gmail account is the
owner's. So this section reports what the repository can prove on its own,
and the gap is flagged rather than guessed.

What the repository proves:

- **One ISO week has ever been written: 2026-W37.** No W36 and no W38
  body exists anywhere in git history, on the site, or in any doc.
- **That one week was generated at least nine separate times**, on
  2026-09-08 and 2026-09-11, before `digests/` went gitignored. The nine
  bodies are all different, and not slightly: they run from 4,897 bytes to
  10,237 bytes. Each is a full regeneration, not an edit.
- **Each regeneration overwrote the one before it.** `pipeline/weekly.py`
  inserts with `on conflict (week) do update set body = excluded.body`, so
  the `digests` table holds exactly one W37 row, and it is the last body
  written, not necessarily any body a reader received.
- **The Monday 2026-09-14 cron also wrote W37, not W38.** `weekly()`
  derives the label from yesterday, so a Monday run stamps the week that
  just ended. Sunday 2026-09-13 falls in ISO week 37. That run therefore
  overwrote the row again. W38 first appears on Monday 2026-09-21.
- **The archive publishes a body from the middle of that sequence.**
  `site/content/issues/2026-W37.md` is byte-identical to commit `d98885e`
  (2026-09-11 20:11, 9,570 bytes), which is the eighth of the nine, not
  the last, and not necessarily the one in the database.

The consequence, stated plainly: **there is no record anywhere in this
repo of which text reached a subscriber.** The digest send runs inside the
same function, after the upsert, against whatever body that run produced.
If the Gmail secret was live on 2026-09-08 and 2026-09-11, the list
received up to nine or ten different emails all presenting themselves as
the same issue. If it was not live, the list received none. The repo
cannot tell the difference, and the database of record was designed in a
way that cannot either, because it keeps one row per week and throws away
every earlier body.

The owner's "roughly two issues" is best restated as: one issue, ten
drafts, no provenance. That is a worse position than two unvalidated
issues, and it is the most important thing this audit found.

Everything below audits the archived body, since it is the one text that
is both public today and recoverable.

## Method

Every claim was read against its primary source, not against a summary.
The claim graph was unreachable this session for the reason above, so
`semantic_search` and `sql_query` were not available and the check was run
the other way round: straight to the papers. Nine arXiv identifiers are
cited in the issue. All nine were resolved through the arXiv API, and the
two papers carrying numeric claims were pulled in full text and searched
for every figure the issue prints.

The title-to-identifier part of this is now automated and lives in
`tools/check_issue_citations.py`, so the next issue gets the check for
free. It reproduces finding 3 below on its own.

## Claims that hold

Verified against `arxiv.org/abs/2609.11042` full text, section by section.

| Issue says | Paper says | Verdict |
|---|---|---|
| 49.4 % to 64.0 % resolved | "From a supervised checkpoint at 49.4 %, three epochs of PPO on the quality-filtered T1-15k reach 64.0 % resolved" | holds |
| 28 % relative gain | "a 28.5 % relative gain from RL alone" | holds, rounded down |
| three PPO epochs | "three epochs of PPO" | holds |
| 15 k quality-filtered examples | "T1-15k: 15,000 tasks selected from the synthesis rounds" | holds |
| learning-rate ratio 30 : 1, critic over actor | "a warm-started critic trained at 30x the actor learning rate" | holds |
| reward on a fixed global scale | "on a scale fixed once for the whole run" | holds |
| reward enters at the final response token | "The scalar enters at the final response token" | holds |
| a binary reward never beats the baseline | "our first binary-reward campaign never exceeded its supervised baseline" | holds |
| log-probability gap 0.021 to 0.013 | figure 6, "T1 (TITO + R3) 0.013, without TITO and R3 0.021" | holds |
| zero token drift in the loss region | "with exactly aligned zero token drift in the loss region" | holds |
| 122 B Mixture-of-Experts | "a Mixture-of-Experts model of 122B total" | holds |
| DeepSeek-V4-Flash at 56.9 % | 56.9 | holds |
| Claude Opus 4.7 at 66.1 % | 66.1 | holds |
| TITO preserves token prefixes across turn boundaries, masks loss | sections 4.2, 4.3 | holds |
| R3 records expert routing in rollout, replays it in training | section 4.3 | holds |

Verified against `arxiv.org/abs/2609.08404`:

| Issue says | Paper says | Verdict |
|---|---|---|
| guidance internalised into policy weights, not an inference-time prior | analysis finding (3), almost word for word | holds |
| broader state-space exploration on difficult tasks | analysis finding (2) | holds |
| environments add observation signals during training | "transitioning from action guidance to observation enrichment" | holds |

Two of the ten uncited "Gaining traction" lines were traced to their
papers by search and both are accurate:

- Puffin-World unifying physics, geometry and appearance as native world
  states matches `arxiv.org/abs/2609.04196` exactly: "three native world
  states: physics (gravity field and latitude), geometry (depth), and
  appearance (image)".
- WorldReward structuring visual evidence from chunks and aggregating by
  voting matches `arxiv.org/abs/2609.03952` exactly: "organizes each chunk
  into structured visual evidence, and aggregates chunk-level decisions by
  voting".

The "inference-time context management" line traces to the Iris paper,
`arxiv.org/abs/2609.04304`, which the issue already cites elsewhere:
"inference-time context management is worth more on these benchmarks than
most reported differences between systems".

## What is wrong

### 1. GPT-3.5-Turbo, where the paper says GPT-5.4 (fixed)

The issue: "the agent outperforms GPT-3.5-Turbo (54.8 %) and
DeepSeek-V4-Flash (56.9 %)".

The paper: "this places T1 above GPT-5.4 at 54.8 % and DeepSeek-V4-Flash
at 56.9 %". GPT-3.5-Turbo appears nowhere in the paper. The score is
right, the model attached to it is a different generation entirely.

This is the worst error in the issue, because it inverts the point. Beating
GPT-5.4 with a 122 B open model is the reason the result is interesting.
Beating GPT-3.5-Turbo would be unremarkable, and a reader who knows the
field reads the sentence, disbelieves it, and stops trusting the rest.

### 2. The 64 % is not the long-horizon number (fixed)

The issue's opening paragraph: the training tricks "push a 122 B
Mixture-of-Experts terminal agent past the 60 % success barrier on
long-horizon benchmarks."

64.0 % is Terminal-Bench 2.1. On Long-Horizon Terminal-Bench, which is the
benchmark the sentence actually names, T1 reaches **27.9 %**. The paper is
explicit that this is the harder and more relevant measure: it calls LHTB
"the closer proxy for what this recipe optimizes". The issue took the
flattering number and attached it to the demanding benchmark.

### 3. A paper cited under a title that is not its title (fixed)

"Read these yourself" lists *Omni Interaction Agent Technical Report* at
`arxiv.org/abs/2609.08977`. That identifier resolves to **Multimodal Duplex
Interaction Agent**, which presents a model called Gander. The one-line
description the issue gives it, a cerebellum-brain streaming architecture
for continuous multimodal interaction, is accurate for the real paper. Only
the title is invented. A reader who searches for the title we printed finds
nothing.

This is the failure `tools/check_issue_citations.py` now catches.

## What is overstated

### 4. The benchmark is never named

Three of the four Trailblazing items rest on Terminal-Bench 2.1, 89
held-out tasks, and the issue calls it "the standard benchmark" and "long-
horizon benchmarks" without ever naming it. A reader cannot check a number
against a benchmark we decline to identify. This is the same evidence floor
O1 KR3 already sets for claim graph edges, applied to benchmarks.

### 5. "Bridge most of the gap to the strongest proprietary models"

True only inside one harness. The paper's own table warns that "harness
choice materially changes scores" and shows Claude Opus 4.6 at 63.8 under
Terminus-2 against 70.1 under Claude Code, with GPT-5.3-Codex at 79.1 under
Codex CLI. The paper's actual claim is narrower and still strong: T1 is the
best model in its size band. The issue dropped the size band, dropped the
harness caveat, and kept the sweep.

### 6. A causal link the FEE paper does not make

The issue: "Training becomes more stable because intra-group feedback
consistency reduces entropy volatility."

The paper lists two separate findings: FEEs "(1) stabilize training dynamics
by reducing entropy volatility" and "(4) identify intra-group feedback
consistency as a critical boundary for stable optimization". A boundary
condition is not a cause. The issue welded two findings into one mechanism
that the paper does not assert.

### 7. The dense reward described as text checking

The issue: the reward "counts how many logical assertions a generated
answer satisfies". In the paper it is the count of passing assertions from
an executed held-out verifier, run against a terminal trajectory of up to
300 tool-call turns in a cloud sandbox. Calling that "a generated answer"
makes an execution-grounded reward sound like a text grader, which is the
one detail that makes the result matter.

## What could not be settled

### 8. Thirteen claims with no citation at all

Every one of the ten "Gaining traction" lines and all three "Left behind"
lines ships with no link, no title, and no identifier. Three were traced
by hand above and were accurate. The other ten cannot be checked by a
reader, and could not be checked here either without the claim graph.

One of them should not have shipped uncited under any standard: **"The
claim that Claude Opus 5 under Claude Code solves only 23.9 % of
simulations is overturned..."** That names a commercial product, attaches a
specific and unflattering number to it, and offers no source. Targeted
arXiv searches this session did not locate the paper it came from. Until
somebody can point at the source, that line is a liability, not a finding.

The "Left behind" section also contradicts itself. Its first bullet says
builders "should no longer treat the lower figure as a ceiling". Its third
bullet then contradicts "the claim that the expert-authored reference
implementation sets an 82.2 % ceiling", which is a claim the issue never
made and appears to be a garbled graph edge rendered as prose.

### 9. The masthead numbers

"3431 papers ingested / 216 claims distilled / 80 edges drawn this week"
cannot be checked without the database. Flagged, not doubted.

## Fixes applied

The three errors in section "What is wrong" are corrected in
`site/content/issues/2026-W37.md` on this branch, with a dated correction
note at the foot of the issue naming each change. The archive is a public
acquisition surface, so a claim known to be wrong does not get to stay live
there on the grounds that the email already went out. The email itself
cannot be recalled.

The overstatements in sections 4 through 7 are left in place deliberately.
They are judgement calls about framing rather than false statements, and
rewriting the voice of a shipped issue after the fact is a different job
from correcting its facts. They belong to the item 4 pre-send checklist,
where they can be caught before a send instead of after one.

## What this says about the next send

Three of the nine numeric comparisons in the issue's strongest item were
either wrong or unverifiable, and the one outright factual error was a
model name the writing model supplied from its own prior rather than from
the payload. The pattern is consistent: the pipeline is accurate where it
copies a number and unreliable where it supplies a noun. Section 5's sweep
and section 1's model name are both cases of the model filling in
plausible context around a correct figure.

That is the specific failure mode the item 4 checklist has to catch, and it
is not caught by reading for tone. It is caught by making every proper
noun and every benchmark name in an item trace to the payload.

## Owed, not done

- Confirm the send count and the sent bodies against the Gmail sent log
  and the `digests` table. Needs the owner, or `NEON_RO_URL` in
  `.github/workflows/agent-engineer.yml`.
- Identify or retract the Claude Opus 5 at 23.9 % claim.
- Keep every body, not one row per week, so this audit is answerable next
  time. Filed as a ledger entry with this PR.
