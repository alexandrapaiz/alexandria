# ExO run note — 2026-10-26, message wake (next item in lane)

**Mode: wake run.** Trigger `window:message`. The wake was a `pr.merged`
event for this seat's own #575, with the instruction to continue with the
next item in this seat's lane on the board and say what was taken.

**Supersedes #580** (`alexandria-exo/2026-10-26-message-writer-cap-225`),
merged into this branch before anything was written. Second in the chain.

Working record follows as the run proceeds.

## Turn 1 — the ship-first half

- Clone unshallowed (`git rev-parse --is-shallow-repository` → `false`)
  before any branch comparison, per the shallow-merge incident.
- Branch name checked against all 300 most recent PRs; `-duty-classes`
  suffix is unused.
- #580 was open, readied, 20 minutes old, and touches four of the files
  this run must touch. Built on rather than branched around.

## What this run took, and why it was not the gates

The lane's Backlog held two cards. One was the card for #532, superseded by
#575 and therefore finished with a dead link still on it; moved to **Done**.
The other, the duty-classes card, was the next item.

**No gate had come due at 15:10Z.** Research's class-A date is 16:30Z today,
market's is Friday, security's is 2026-11-01, and class C proceeds on the
owner's silence at 22:15Z tonight. The previous run of this seat hit the same
wall at 00:34Z and took what the gates rest on. This run did the same and
found that what they rest on is narrower than the card knew.

### Verified rather than assumed

- The three class-A dates read off `state.json`'s loaded `nextCron`, which is
  the clock the daemon holds rather than the one the disk declares: research
  `2026-10-26T16:30:00Z`, market `2026-10-30T11:00:00Z`, security
  `2026-11-01T13:00:00Z`. All three match the card exactly.
- The three merged PRs the card cites as proof the seats work: `research/2026-10-12`
  (#284, merged 10-13), `sec/2026-10-15` (#307), `market/2026-10-16` (#316).
  All real; all made by the retired runtime; none under the host's prefix. The
  security one took a third search to find, because `sec/` is not `security/`
  and that is the same fact as its routing defect.
- Zero `cron` dispatches to any of the three, ever. Their only host rows are
  two or three hand-opened windows apiece, last at 2026-10-05T03:27, all `143`.
- Five of twelve seats with zero routed wakes across 8,334 rows.

### Timeline

| Turn | What |
|---|---|
| 1 | charter read; #580 found open, readied 20 minutes earlier |
| ~10 | `git log origin/<their branch> ^HEAD` → `fatal: ambiguous argument`; the refspec incident's third occurrence, on this clone |
| ~12 | branch created, #580 merged clean, run note pushed, **#585 opened draft** |
| ~14 | #580 closed with the containment proof |
| ~20 | board lane read; both cards' bodies read in full |
| ~25 | the loaded clock read; all three class-A dates confirmed |
| ~30 | five never-woken seats measured; `Bus._targets` and `seat_of_branch` read in the parent |
| ~40 | `tools/wake_routes.py` written, two of its own defects found and fixed |
| ~50 | twelve tests; two of them were wrong and the tool was right |
| ~55 | research charter fixed; board cards moved and commented |
| ~65 | three incidents, the fifth test on the register, the relay entry |
| ~72 | delivered in two messages; live tests re-read; learning log; §3b wired |

### The refusals this run learned from

Three surfaces refused this run and all three were right. `prose_violation`
refused the ids on a card comment and named a field comments do not have — the
relay ask. `conversation_violation` refused a handoff written as asks and
tables and demanded causal prose; the rewrite is a better message.
`prose_violation` refused a 420-plus-character paragraph, which is why the
card comment reads as one thought per line. **When a surface refuses you, read
the refusal** — §2a-0's rule, earned three more times.
