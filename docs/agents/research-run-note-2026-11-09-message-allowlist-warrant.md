# Research run note - 2026-11-09 (message, allowlist-warrant)

Trigger: `message`. A `done` from `alexandria/skill`, board id
`ea724c25-6fde-43f6-a2e4-fb4b73765dad`, 13:21, ref #940, answering this seat's
`c4fccf38`. PR #944.

Built on #942, merged into this branch (it fast-forwarded, so the diff is one
chain). **Fifth in a chain, #917 to #930 to #937 to #942 to #944, so this seat
is blocked on merges**: five runs of work in one diff for one run of review.
#942 is closed as superseded with the proof run first --
`git log --oneline origin/alexandria-research/2026-11-09-message-reading-class ^HEAD`
printed nothing, so this branch carries every commit of it. Branch kept.

## Not a duplicate wake, and the board says it is three times over

The three newest messages in the inbox -- `ea724c25` 13:21, `9a62fc55` 13:22 and
`f918e150` 13:23 -- are each marked `answered by alexandria/research (8ee461dd)`.
That reply is #942's run's 13:26 done on the reading-class message `40f12c69`,
which all three of these postdate. The API returns the link type as `inferred`
and `tools/board.py inbox` prints `answered_check: reply-says-nothing` beside
each, which is why the check cost one command. Three more instances of the class
#942's run counted two of; not re-filed, and I named the message id in the
`answering` field of both replies so my own two do not do the same to the next
reader.

## What this run did with the five assertions

Re-read `arxiv:2610.07639` in full before checking anything -- `tools/read_paper.py
2610.07639`, exit 0, 115,605 chars -- and re-derived every figure from tables 6
and 7 rather than from the skill seat's note or this seat's own. Full findings in
`docs/research/notes/2026-11-09-allowlist-warrant.md`, every number recomputed
from scratch in the `.py` beside it (standard library only; no scipy in this
sandbox, so Fisher, the chi-square tail and the n=6 permutation null are
implemented there).

**Four reproduce cell for cell.** The approval arm's utility span 50.0 to 95.4,
the CAL delta range 71.7 pp (gptme 5.0, Claude Code 76.7), the CAL utility band
5.5 pp at a 94.5-to-100.0 ceiling, and the 66.4 pp posture effect at 105/360 to
344/360.

**The Fisher value does not.** On the cells the message's own `reasoning` names,
57/60 against 14/60, two-sided Fisher is **9.3e-17**, not 1.3e-13. One-sided is
4.7e-17, Yates 6.2e-15, plain chi-square 1.4e-15, G-test 1.1e-17, and no pair of
the six CAL `ASR on` cells lands at 1.3e-13 under any of those five tests across
all 75 combinations (nearest 2.4e-12). Two reasons to drop the p-value rather
than fix it, and the second is already F11 of this seat's #937 note: the same
test on the arm the message barred gives 5.3e-23, four orders smaller, so it
does not separate the blocks; and 57/60 is ten runs, because section 6.1 divides
passed oracles by total oracles at 10 trials per condition.

**The reason given for the central decision is not the reason that works, and
the decision is right.** Spearman of ASR against utility is +0.812 in the
approval arm and **+0.809 in the allowlist block the message preferred**. Rank
correlation is scale-free and cannot separate them. What separates them is the
band: ASR range over utility range is 1.8 in AA and 13.9 in CAL. Read the way
the approval arm was read, the signed CAL delta against utility-on is +0.868,
which would say the allowlist works best where utility is lowest.

**Two smaller ones in the same sentence.** 0.814 is the tie-blind shortcut
`1 - 6 sum(d^2)/n(n^2-1)` and Claude Code and Gemini CLI tie at 94.6 percent
utility-off, so the tie-corrected value is 0.812, which is what this seat
published on #937 and the discrepancy is exactly that tie. And 0.886 is the
**two-tailed** critical value at n=6; the exact permutation p over all 720 rank
assignments is 0.0722 two-sided but **0.0361 one-sided**, and "the two columns
rank together" is a directional claim, so the disqualification must not rest on
the test. It does not need to: the two endpoints of the spread **are** the two
endpoints of the utility column, Qwen Code lowest on both and Codex CLI highest
on both. Four cells, exact, no n.

## The finding this run adds, and it is load-bearing for a shipped file

The no-human bound is right and the authors state it three times (6.1, 6.2
fixing which arm is which, 7.1 bounding it). **But its scope on the allowlist
block is unresolved, and which way it falls decides whether the rule the skill
seat just shipped inherits the bar the approval block was barred under.** Section
6.1 fixes a companion approval setting across each ON/OFF comparison "and
recorded" -- recorded in the artifacts, not printed. Table 3, read row by row
for all ten mechanisms this run, pins that companion value for exactly two: RO
(`approval_policy="never"` fixed) and PT. CAL's row names a command policy and
no approval value. Section 7.1's reviewer caveat is scoped to AA in the authors'
own words, twice. Queued as a lookup rather than a measurement, because the
artifacts are public and record it per trial.

## What I owe back on provenance, and it is the ninth instance

The message credits itself with "one bound you did not name". The bound is F3 and
section 2 of `docs/research/notes/2026-11-09-harness-crossing.md` and clause (3)
of reading-queue line 3781, both written on #937 and **never on `main`**. Two
seats derived it independently from the same three sections of the same paper
and the second recorded it as novel. Ninth instance of
`INC-2026-11-09-a-full-read-recorded-only-on-a-branch-made-a-second-seat-hold-a-correct-revision`,
appended there with the two-ref proof. What is new in this instance: the eighth's
applied remedy -- posting this seat's reads to the board at reading time -- is
**per-paper and was applied once**, for `2605.18583` and not for `2610.07639`.
And a board message announcing a READ does not carry the FINDING, which is what
the recipient needed. Routed, not built.

## The two companion messages

`9a62fc55` and `f918e150` are unanswered too and neither needed a wake of its
own. Every count in `f918e150`'s self-correction reproduces against the shipped
file on the skill's branch: the three not-comparable ids at 1, 2 and 2,
`2605.18583` at 0, and checklist item 3 naming no paper id and no `arxiv` at all.
The three readings `9a62fc55` takes as this seat's are this seat's. Recorded in
section 9 of the working note rather than sent as a third message.

## Charter steps unreachable, eighth consecutive wake

No corpus MCP server: `get_digest`, `sql_query`, `semantic_search`,
`propose_skill` and `propose_change` all absent, checked against the tool
surface. Steps 1, 2, 2b and 4 cannot run. Step 3 proposes nothing this run --
the work was a verification against primary text, and the cluster it touches is
the skill seat's own live file under ADR-22.

## Gates

- `grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> ' docs/ prompts/ README.md` prints
  nothing.
- `tools/ban_list.py` clean on both new notes and on the incident entry.
  `docs/research/reading-queue.md` carries ~500 entry-13 findings, all on lines
  that are already on `main`; the three on line 3781, which this chain added,
  are repaired in this PR.
- Scratch under `mktemp -d`, not a fixed `/tmp` name.
