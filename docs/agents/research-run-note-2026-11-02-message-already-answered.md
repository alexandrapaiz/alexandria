# Research run note, 2026-11-02 (message wake): the note was already answered, so the run bought the thing nobody had

**Chosen deliberately: branched from `main`, and this pull request does not
supersede #691.** #691 is this seat's own open pull request, pushed four minutes
before this run woke, and it already answered the event that woke this run. It
holds `docs/research/reading-queue.md` and the prediction-basis notes; this run
writes none of those, so the two merge in any order and the complete,
reviewable work in #691 does not get pushed back into the queue to carry a
duplicate-wake line.

## 1. The event, and the verdict on it

The wake carried 1,217 of 3,728 characters of alexandria/skill's note
`278f4668-04a7-45b8-9787-2ece62f34245`, cut before the sender's disposition.
Read whole on the board, per the charter.

It was already answered. #691's reply went onto the board at 02:04 as
`70b2e9ef-a557-4d7f-9a24-26d2b38792cb`, carrying `"answers": "278f4668-..."`,
five minutes before this wake fired at 02:09.

**Verified live rather than trusted**, which is what the charter asks for when
the open pull request may be the event's answer:

- `skills/_validation/prediction_basis.py --check`, run on the skill seat's own
  live branch tip (`alexandria-skill/2026-11-02-message-trigger-instrument`,
  #692): exit 0, and the three counts print as 1 observed-bare-run, 3
  this-repository-history, 98 authored-judgement.
- #691's `docs/research/notes/2026-11-02-prediction-basis.py`, run on its own
  branch: reproduces ten wide-net candidates, nine real, the eight, the four
  conceded, `ac-t11` as never ours, and `he-t9` as the single undated
  repository fact.

Both halves hold. Nothing in the earlier answer needed rewriting, and this run
rewrote none of it.

## 2. What the run spent itself on instead

One thing in that note was asked of nobody and done by nobody: remedy two is
filed in `docs/ideas.md` with **"Cost: unknown, and the honest first step is one
costed estimate rather than a run."** Producing it spends nothing, it is this
seat's kind of work, and the owner's decision under pm.md section 22 cannot be
taken without it.

`docs/research/notes/2026-11-02-independence-costed-estimate.md`, with
`...estimate.py` as the receipt. Three results:

1. **Remedy one is eleven cents, or free.** 102 reviewer calls over 110,254
   measured characters of reviewable payload is 91,826 input and 6,120 output
   tokens: $0.1117 on `kimi-k2.6`, **$0.00** on the two groq free-tier models
   `pipeline/budget.py` already records. The free tier's ceilings fit it (102
   requests against 1,000 RPD, 97,946 tokens against 200,000 TPD) and pace it
   at 12.2 minutes. So the ask is not a spending decision at all. It is one
   signup, and one twelve-minute pass inside an ordinary run.
2. **Remedy two is low four figures per model-harness arm with caching, five
   figures without**, and the entire width is one unmeasured quantity, tokens
   per turn, which the paper does not report and nothing here has measured.
   Caching is a four-to-sevenfold lever across every row, larger than any model
   substitution available. The judge arm is $1 to $5 and the sandbox is tens of
   dollars, so neither is the driver and neither is worth optimising first.
   **The purchase to make is a five-task pilot at about $16**, which replaces a
   sixtyfold spread with a number.
3. **The finding that outranks the estimate.** Skill-Use's own exclusivity
   instrument is not an observed bare run either; its masked-skill check is a
   model's counterfactual judgement, the same shape as our 98
   authored-judgement rows. What makes it admissible is three separable
   safeguards, and only one needs the credential: cross-family review needs it,
   while the red-team refutation pass on five named axes and the ten percent
   human spot-check do not. So the honest restatement is narrower than the
   ledger's: **the prediction fields are blocked on the cross-family third of
   independence, not on independence.** And the paper's own funnel settles the
   ordering, since it runs the cheap screen first and admits only survivors to
   the sandboxed stage, which makes remedy one a precondition for remedy two
   rather than a cheaper alternative to it.

The facts in (3) were already in this seat's queue answer on #691. The
inference and the decomposition are not, and the note says so in its own text
rather than letting a reader assume otherwise.

## 3. The reading queue

Not drained by this run, and it did not need draining. The 2026-09-30
independence line that started this whole exchange is struck on #691's branch
with the full answer under it, and #679, which first carried that strike, is
closed as superseded. `docs/research/reading-queue.md` is a surface #691 holds;
a second run editing it from `main` is the ledger-collision shape the charter
names, so this run read it and left it alone. 135 lines pending on `main`, 131
on #691's branch.

## 4. The repeat

`INC-2026-11-02-the-second-wake-fired-after-its-own-answer-was-already-on-the-board`,
two classes in one entry: the fifth sighting of one-event-two-runs, and the
fourth truncated wake of the day cut at the same place.

The new half is a cheap detector. Every earlier instance of the duplicate-wake
class was found by survey, which costs a `gh pr list` plus a read and cannot
tell a collision from an answer without the read. This one was answered **on
the bus** in a machine-readable field before the second run began: both sides of
this exchange put the id they are answering in `data.answers`. A run holding a
message id could ask whether its own seat has already answered that id and get
the verdict in one call. The limit, stated plainly: `data.answers` is on 2 of
the 245 messages this seat can see in a week, and both are this exchange, so it
is a two-seat practice rather than a bus feature. Promoting it is a change to
the bus or to twelve charters, and it is routed, not applied.

## 5. Charter steps not taken, and why

This was a message wake, not the weekly run. No digest review, no synthesis, no
curation brief, no source census, and no skill proposal: none of those is this
event's work, and the week's brief is not due to this run. No meta-review
proposal either, which is the normal outcome, and this run has no pattern of
several instances pointing one way that it did not already file as an incident.
