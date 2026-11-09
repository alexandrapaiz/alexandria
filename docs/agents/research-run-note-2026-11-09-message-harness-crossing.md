# Research run note - 2026-11-09 (message, harness-crossing)

Trigger: `message`. PR #926 merged, the payload saying "continue with the next
item in your lane on the board, and say what you took."

Built on #930, which is merged into this branch and closed as superseded.
**Third in a chain, #917 to #930 to #937, so this seat is blocked on merges**:
three runs of work in one diff for one run of review. The supersede proof,
`git log --oneline origin/alexandria-research/2026-11-09-message-overeager ^HEAD`,
printed nothing before #930 was closed. PR #937.

## What I took, and why it was the next item

The board's research lane has nothing in Backlog, This sprint or In progress
(`python3 tools/board.py show --seat research`: 4 items in Review, 15 in Done).
So there was no card to take and the lane item is the charter's standing duty,
ADR-35: drain the reading queue.

The item taken is `arxiv:2610.07639`, HarnessSecurity-Bench, which is the
newest line in the file and the one this seat's own last run left half-done.
#930's live-world check found it at the end of that run and read the abstract,
section 1 with table 1, and section 6.2 with table 6 only, recording in the
line itself that "the rest is this line's ask": sections 2 to 5, 6.3, 7 and
both appendices.

It is the right next item on the relevance law rather than on recency. It holds
the model fixed and crosses nine security mechanisms against six harnesses,
which is the measurement two shipped skills (`agent-approval-paths`,
`agent-containment`) currently price without naming the harness -- the
correction target this seat opened on #917 and half-withdrew on #930 when
`2605.18583` turned out to have removed the variable it was named for.

## What the run did

`python3 tools/read_paper.py 2610.07639 --no-cache`, exit 0, 114,176 chars, all
nine sections plus both appendices. Findings in
`docs/research/notes/2026-11-09-harness-crossing.md`, eleven of them
claim-grade with tables, denominators and scope, in section 9 of that note.

**The partial read's figures all stand and its sentence does not.** The 81.7 pp
gated-arm harness spread is exactly as recorded (0.0 percent, Qwen Code 0/60, to
81.7, Codex CLI 49/60). Calling it "LARGER than the posture effect" is true
against the pooled 66.4 pp and false for three of six harnesses taken one at a
time (Gemini CLI +96.7, Qwen Code +90.0, GitHub Copilot +85.0). The line set a
cross-harness range against a pooled mean difference.

**The replacement is stronger, and the paper never states it.** Computing the
cross-harness spread separately per arm, the split falls along what the
mechanism does to a capability. Mechanisms that MEDIATE one diverge when
engaged -- path restriction 97.5 pp (0.0 to 97.5), the approval gate 81.7,
command allowlisting 76.7, MCP permissions 63.3, project trust 51.7 -- while
mechanisms that REMOVE one collapse to within 5 pp once engaged (network
isolation, denylisting and read-only all 0.0 to 5.0). **So a figure for a
mediating mechanism does not transfer across harnesses and a figure for a
removing one does.** That is the no-transfer rule with the scope condition it
was missing, and it is a usable instruction to a skill rather than a warning.

**The bound the partial read could not have.** The approval gate's OFF arm is
answered by a Qwen3.8-27B model through a deterministic bridge, not by a person
(section 6.1, bounded by the authors at 7.1). So every AA figure in the paper
is a property of six native approval surfaces under one fixed LLM reviewer,
with no decomposition into coverage versus rendering.

**The sharpest single cell**, and the one worth a skill's attention: at the same
model and the same utility, Gemini CLI reaches 3.3 percent ASR against Claude
Code's 43.3 at an identical 94.6 percent utility. Across the six harnesses ASR
and utility move together at Spearman rho +0.812 (n=6), so most of the spread is
a gate that blocks a lot of everything; that one pair is the exception and is
Pareto-clean.

**Every checkable quantity in the paper reproduces**, which is the opposite of
`2605.18583` on #930. All of tables 6 and 7's Overall rows and deltas, the three
prose utility decompositions, and -- independently, by parsing all 2,000 rater
verdicts out of appendix A -- the 205/83/112 rating totals, the five
per-mechanism counts, the evidence-gap split, exactly 382 of 400 cells with a
3-of-5 majority all matching table 4, and **all three Krippendorff alphas to
three decimals at the stated n**, using an ordinal ordering the paper never
states and that is the only one that reproduces all three.

**Two boundaries the reproduction exposed**, neither of which the paper names:
the headline 0.911 human agreement is measured on 192 of 400 cells because one
human rater returned unknown on 191 of 400, and the least-hesitant of the five
raters is GLM-5.2, the same model used as the base LLM for all 2,500 trials.

## The queue, and the reach claim I corrected in my own seat's line

The `2610.07639` line is annotated with the read and stays open, because its
remaining ask is corpus presence, which is a row and not a reading. Three of its
own statements are corrected on the line, including the one that matters for
routing: **"not in sources.yaml's reach" is false.** The paper is cs.CR primary
with a cs.SE cross-list and both categories were configured before it was
submitted (`sources.yaml:25` and `:45`). This is not a category gap and the
monthly census it was routed to would have found nothing to change.

What is still unknown is whether the paper is absent from `papers` or present
and discarded at triage. **This run cannot answer it**: there is no
`NEON_RO_URL` in the environment and no corpus MCP server attached, both checked
rather than assumed. Routed in the pull request to whoever holds the credential;
the entrypoint for the row once that lands is
`modal run pipeline/ingest.py --ids 2610.07639`.

Three questions appended, no paper, per the no-padding rule: the
coverage-versus-rendering decomposition, whether the mediate-versus-remove split
holds outside this one dataset, and a joint harm-per-utility statistic to replace
the bare harm rates both skills carry. `pipeline/reading_queue.py --order` run
after the edit, per the header; 112 pending, the new lines carry no `arxiv:`
prefix so nothing was turned into a fetch request.

## Registers

Conflict markers: `grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md`
prints nothing.

Ban list: checked on the note, the queue annotation and the incident entry. All
three are plain ASCII (entry 13), and the note carries no slop-lexicon word
(entry 1).

Incident filed, as a repeat:
`INC-2026-11-09-a-queue-line-claimed-a-sources-yaml-reach-gap-and-both-of-the-papers-categories-were-already-configured`.
Second instance for this seat in this file -- line 220 records the first, on
`2609.08371`'s cs.SE claim, corrected 2026-10-27 in PR #636 -- and the fifth of
the wider asserted-premise class. The aggravating fact is that the rule which
would have caught it was in the header of the file the asserting run was
appending to, and the hedge "as far as this run can tell" is what let the clause
past, which is ban-list entry 50's shape in a register line.

Scratch files: `mktemp -d` for the pull request body, per step 0b.

## What this run did not do

A `message` wake, so no digest review, no curation brief, no skill proposal and
no meta-review. The charter's weekly steps belong to the scheduled run.

No claim rows were filed. Filing needs the corpus and this seat holds no write
path to it; the eleven claim-grade findings are written up with their
denominators so whoever runs distill can file them without re-reading the paper.
