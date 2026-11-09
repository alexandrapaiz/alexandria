# Skill run note, 2026-11-09, message (approval-paths answers)

Trigger: two events on one wake. A workflow red on this seat's own branch,
which is pull request #873, and a `done` from the research seat answering the
four questions this seat queued against `agent-approval-paths` on 2026-11-02.

Branch: `alexandria-skill/2026-11-09-message-approval-answers`, cut from #873's
head, which it contains in full. Supersedes #873, closed by this run with the
proof printed first. Chain `#861 -> #865 -> #873 -> #881`, depth 3, so this
seat is blocked on merges and the charter says to say so.

## The red: still red, and cleared

Confirmed live before spending the turn, per L-A31. Reproduced locally on the
branch as it stood: `tests/test_skill_receipts.py` 1 failed, 28 passed, the
same single assertion the workflow log names, on `harness-engineering`. No
later commit of mine had fixed it, so the L-A31 answer-by-reference did not
apply.

The cause was already fully diagnosed in #873's body and that diagnosis was
correct. What #873 got wrong was its conclusion that no fix existed inside this
seat's write boundary. One did, and
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
prescribes it in its own words, after this seat had applied it twice. Three
bundles dated 2026-11-09 tied on both sort keys and the ascending glob gave
`harness-engineering`'s receipt to the alphabetically first one, which was
measured against text the file no longer carries.

Moved the two superseded bundles to `skills/_validation/results/superseded/`,
which both consumers skip because both glob one level. Checked rather than
asserted: the survivor has the same 84 cases with zero verdicts moved against
one of them, and the other carries the duplicate-case-id defect the survivor
repaired, 84 case rows for 83 distinct keys. `tests/test_skill_receipts.py` 29
passed.

Then the tie fired a second time inside this run, and that firing is the more
valuable one: after the skill edit required a fresh bundle, `--receipts` came up
green **before** anything was moved, because the new bundle's name sorts first
on the letter `a`. The defect does not announce itself, so the count of wrong
published receipts is not bounded by the count of reds anybody has seen. Sent to
the engineer seat, whose #878 is the real repair and is open.

## The answers: v2 of the skill

All three new papers read in full by this seat with `tools/read_paper.py` at
exit 0 before anything was written, per ADR-35, and every number checked against
the paper's own table rather than against the research note. That caught one
overclaim in the note: Caper's false-block interval also overlaps TS-Guard's, so
the clean guardrail comparison is one model rather than guardrails as a class.

- Delta 1 is a three-source pattern. Independence verified by grep: zero
  occurrences of either founding id or construction name in `2610.14488`.
- Delta 1 gained the ablation decomposition, which reorders the build: approval
  tier 18 of 74, resolved classification 5, object binding 2.
- Delta 2 gained the first measured route off its own frontier, carried with the
  intervals so the tie is stated as a tie, plus an independent real-session
  corroboration of the uninspectable mechanism.
- Delta 3's control corrected from 0 of 25 to 0 of 100 pooled. Bounds recomputed
  here as `1 - 0.05 ** (1/n)`: 11.29 and 2.95 percent.
- `status` stays `draft` and no claim id was added, because none of the six
  papers has a row.

## What this run measured, and what it did not

**Nothing here is an eval delta.** `NEON_RO_URL` and `GROQ_API_KEY` both checked
absent in this run rather than quoted from the last. Every skill in the library
remains **unmeasured** in that word. One eval task added, `ap-t7`, unqualified
like the other eight.

One thing this run measured that nobody had: delta 3's own situation in the
operator's words routes to `agent-containment` at 0.357 against this skill's
0.219. Committed as `ap-pos-4`, failing on purpose, because the file re-runs
forever and a paragraph does not. Not fixed, and the case says why: the
description is 149 words against a 150-word budget, so any addition is a swap,
and the engine's idf is library-wide.

One honest regression to report against this seat's own earlier number: #873
told the owner the library's rendered-line floor is 143, from a smallest
frontmatter of 39. That 39 was this skill, and v2 takes it to 60, so the floor
is now 149. The arithmetic the owner's ask rests on moved because of this run.
