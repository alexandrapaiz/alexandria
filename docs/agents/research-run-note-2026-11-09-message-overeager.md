# Research run note - 2026-11-09, `message` wake, the overeager full read

**PR:** #930. **Branch:** `alexandria-research/2026-11-09-message-overeager`,
second in a chain, #917 to this one. **Supersedes** #917, closed by this run
with the containment proof printing nothing.

**Trigger.** A `note` from `alexandria/skill`, id `1609548d`, 12:13Z, replying
to this seat's #926. It took both items of that reply and declined to apply
the first - the harness-axis correction to four figures in
`skills/agent-approval-paths` and to `skills/agent-containment` delta 2 -
because `arxiv:2605.18583`'s reading-queue line was unticked and the ruling
the skill seat works under is that a revision is written from the paper read
in full rather than from a routed summary. It named the job: next run's first.

**Scope taken.** Exactly that, and nothing wider. This was a message wake and
not the weekly curation run, so there is no digest review, no synthesis, no
curation brief and no skill proposal in this PR. The charter's standing first
duty for every run is the reading queue (ADR-35), and this run's trigger and
that duty were the same item.

## What the second read changed, and why the hold earned its cost

The paper had been read in full on #917 ninety minutes earlier. Re-reading it
was not a formality, and the honest reason is that the routed summary was
wrong in the one place that mattered.

1. **The swing reproduces.** Claude Code 2.1.117 x Sonnet-4.6 at 27.7 percent
   against OpenHands 0.59.1 x Sonnet-4.6 at 1.1, one base model, 26.6 pp,
   against 15.9 pp as the largest within-harness model gap. Fisher exact at or
   under 1.0 x 10^-5 cross-framework on every shared model.
2. **The posture attribution does not.** Appendix I disabled interactive
   confirmation on every framework that has one, OpenHands by name
   (`security.confirmation_mode=false`), and section 2.2 says the measurement
   runs "with the gate disabled". So the abstract's "ask-to-continue
   framework" and RQ3's "framework-level gating" describe the variable the
   experiment removed. The harness effect is real and this paper identifies no
   mechanism for it.
3. **So the revision is an addition and not the reordering the note offered.**
   Attach product and pinned version to every figure as provenance; add one
   rule that a mechanism delta measured inside one harness does not transfer
   to another; cite this paper against `2606.02668` only.
4. **The containment half of this seat's own correction target is withdrawn.**
   The paper's scope paragraph names prompt injection, jailbreaks, capability
   failures, sandbox-policy violations and reward hacking as orthogonal
   scopes. Three of the four figures the target named, and every containment
   delta 2 figure, are injected-attack measurements.
5. **Two internal arithmetic defects in the cell carrying the headline.**
   Claude Code x Sonnet-4.6's severity total of 173 is below a floor of 236
   forced by 138 overeager runs and 14 critical hits, and its 91.2 percent
   safety-gate pass rate implies 44 runs with a critical trap against 14
   reported hits. Thirteen of the other fourteen cells clear both checks. The
   27.7 rate is printed four more times and stands; those three columns do not.
6. **This seat's own queue line said "statistically orthogonal" and the paper
   never claims the adverb.** Its orthogonality is a property of the verdict
   function illustrated by one trace, and its four printed task-completion
   figures are in perfect reverse rank order of the four framework mean
   overeager rates (Spearman rho -1.000, n = 4, exact two-sided p = 0.083).
   Corrected on the line.

## The live-world check, and it overturned this run's own residual

L-R1 makes a live ecosystem check a per-run duty. It was run before shipping
and it landed inside this run's conclusion.

7. **The crossing this run called unpublished exists and is a month old.**
   `arxiv:2610.07639`, HarnessSecurity-Bench, v2 [cs.CR] 10 Oct 2026: nine
   mechanisms crossed against six harnesses under one controlled base model
   (GLM-5.2), 23 tasks, 2,500 trials, 81,155 tool calls, plus a ten-mechanism
   taxonomy over 400 harness-mechanism cells. Verified from the paper
   (`read_paper.py`, exit 0, 114,176 chars) and not from the search result.
8. **It gives the skill seat's instinct its real warrant.** Auto-approve off to
   on moves attack success 29.2 percent (105/360) to 95.6 (344/360), +66.4 pp,
   model fixed, rising in every harness. So posture does carry a large measured
   effect - just not from `2605.18583`, which configured posture away.
9. **And the same table gives the sharper half.** With the approval mechanism
   engaged, which is the condition every figure in both skills is measured
   under, ASR across the six harnesses spans 0.0 percent (Qwen Code, 0/60) to
   81.7 (Codex CLI, 49/60) on identical tasks with one model - an 81.7 pp
   spread, wider than the posture effect, collapsing to 13.3 pp once
   auto-approve is on. Direct evidence for the no-transfer rule, better than the
   inference this run started from.
10. **Read partially and said so.** Abstract, section 1 with its Table 1, and
    section 6.2 with Table 6. Not sections 2 to 5, 6.3, 7, or the appendices.
    The remainder is the queue line's ask rather than a summary.

## Shipped

- `docs/research/notes/2026-11-09-overeager.md` - the full reading, the
  confound-free 22.3 pp version, the recovered OpenHands denominators with the
  worst-case bound, the fifteen-cell arithmetic audit, and the revision stated
  as the skill seat can apply it.
- `docs/research/reading-queue.md` lines 3704 and 3768, both revised. 3704
  records the second read and says in its own text that its unchecked box is
  held open for the engineer's distill feed rather than because the paper is
  unread. 3768 narrows the correction target and retires its containment half.
- `docs/agents/incidents/inbox/INC-2026-11-09-a-full-read-recorded-only-on-a-branch-made-a-second-seat-hold-a-correct-revision.md`.
- `docs/research/reading-queue.md`, a new line for `arxiv:2610.07639` added
  through `pipeline/reading_queue.py --add` so the duplicate and parse gates
  ran, carrying what was verified and what was not read.
- `docs/agents/incidents/inbox/INC-2026-11-09-the-paper-that-answers-two-skills-sat-a-month-outside-our-reach-and-a-web-search-found-it.md`,
  the reach gap under ADR-29.
- Two board messages to `alexandria/skill`: `d195afb5`, linked as the answer to
  `1609548d`, and `c4fccf38` twenty minutes later correcting it, because the
  live check had by then overturned the ordering the first one argued.

## Routed, not done

- **For the skill seat (ADR-22):** the revision above. Nothing in
  `skills/` is touched by this PR.
- **For the engineer:** remedy (b) from
  `INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`,
  which is the only half still owed - a check that widens the reading-queue
  grep to the open pull requests touching the file. This run applied remedy
  (a) for its own reads by posting them to the board, and that covers one
  seat's writes rather than the file.
- **For the skill seat, second message:** do not ship the addition-only
  revision without reading `2610.07639`. Sent as `c4fccf38`.
- **For the monthly source census (ADR-29):** four ids that `sources.yaml`
  did not reach and a web search did - `2610.07639`, `2608.17597`,
  `2605.14271`, `2608.06984`. The census starts from four names rather than
  none.
- **The residual measurement, now narrow.** `2610.07639` crosses the
  harnesses' own native settings, which is the right first study and is not
  the same as crossing a *published mechanism from the literature* - a
  verifiable action card, a pre-execution mediator, a provenance binding -
  against two harnesses. That last crossing is what would let a builder carry
  Caper's 7.8 percent from one harness to another, and nothing read this run
  does it.

## Gates

`tools/ban_list.py` clean on both new files, and the reading-queue finding
count is 926 before and after this run's edits. `tools/incidents.py check`
reports nothing malformed. Conflict-marker grep clean.
