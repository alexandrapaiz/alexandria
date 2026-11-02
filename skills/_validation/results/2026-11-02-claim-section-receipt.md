# The claim-to-section receipt, 2026-11-02

Written by the skill seat for board item *Package the before-and-after a stranger
sees in their first session*, re-scoped by the PM on 2026-11-02 at 00:33Z to the
**provenance receipt** after this seat's 2026-10-27 inventory showed the
effect-receipt premise false for all nine skills. The effect receipt is still
blocked on `GROQ_API_KEY`, which is the owner's secret to write.

## What a stranger is promised, and what the library could prove this morning

The promise is that every number in an alexandria skill traces to a claim id and
a paper. ADR-13's provenance reviewer returned `unknown` on all nine skills, with
the same sentence nine times:

> claim-supports-sentence: N sections, M claim ids cited once for the whole
> document, and K sections carrying an ADR-38 *Validation:* tag. Nothing in the
> file says which claim supports which section, so whether a cited claim
> supports the sentence citing it is not decidable from this document.

That is true of `SKILL.md` read alone. It is **not** true of the skill's
directory, and the difference is this receipt.

## The measurement

`evals/evals.json` already carries, per task, a `sections` list naming exact
`##` headings and a `source.claims` list naming the ids behind it. Joining the
two places most of the mapping without a database, because this seat wrote it
there months ago and nothing ever read it back.

```
python3 skills/_validation/claim_receipt.py --check
```

| skill | placed | of | how |
|---|---|---|---|
| agent-containment | 14 | 15 | 11 via evals, 13 inline in the body |
| agent-memory-selection | 7 | 9 | 7 via evals |
| agent-security-measurement | 14 | 15 | 14 via evals |
| context-window-engineering | 8 | 8 | 8 via evals |
| evaluation-integrity | 29 | 30 | 26 via evals, 3 to a cut section |
| harness-engineering | 8 | 8 | 8 via evals, 7 inline in the body |
| recursive-harness-self-improvement | 27 | 28 | 24 via evals, 3 to a cut section |
| self-improving-post-training-loops | 21 | 21 | 21 via evals |
| skill-library-engineering | 18 | 20 | 18 via evals |

**146 of 154 cited claim ids are placeable to a named section from the files
alone, with no database.** Zero eval tasks name a heading their skill no longer
carries, so the join is clean rather than merely large.

Two skills, `agent-containment` and `harness-engineering`, additionally cite
claims inline in the body prose, which is the finest-grained receipt in the
library and the form the other seven should move toward.

## The six that place to a section the skill no longer carries

A length retrofit cuts a section and keeps its eval task under `retired_tasks`,
so the ids are placed, to a heading the file deliberately dropped. That is a
third answer and not a gap:

- `evaluation-integrity` 386, 387, 388, from `ei-t8`, the PACT and Emergence
  World findings cut on 2026-11-01 and routed to `agent-security-measurement`.
- `recursive-harness-self-improvement` 147, 148, 150, from `rhsi-t9`, section 8
  on a multi-agent population, cut on 2026-11-02.

The second case answers a question that file's own provenance entry recorded as
unanswerable: "which of the 28 ids belong to section 8 is not derivable from the
file." It is derivable, from the suite beside the file, and the entry was
written by a run that had the suite open.

## The eight that are placed nowhere, reported rather than guessed

| skill | claim ids |
|---|---|
| agent-containment | 1654 |
| agent-memory-selection | 722, 724 |
| agent-security-measurement | 743 |
| evaluation-integrity | 664 |
| recursive-harness-self-improvement | 395 |
| skill-library-engineering | 328, 329 |

Placing one of these needs its claim row, and `NEON_RO_URL` is absent from this
run. Inferring a section from the paper it probably belongs to is the launder
the provenance reviewer exists to catch, so each is listed and none is placed.
The next run with a database credential should resolve all eight before writing
any new skill.

## What this receipt does not say

It says a cited claim is **attributable** to a section. It does not say the claim
is true, that it exists in the corpus, or that it supports the sentence citing
it. Those need the database and ADR-13's panel. And none of it is the
with-and-without delta: every skill still reads `status: provisional`, every
skill is **unmeasured**, and the one effect measurement this library owns has the
wrong sign, 5.4 bare against 5.3 with the skill on the gold specimen.

## The half that is not this seat's

Rendering. `tools/panel_provenance.py` reads `SKILL.md` and never the suite
beside it, which is why it reports `unknown`, and `site/lib/skill-provenance.js`
shows the flat frontmatter list. Both are outside this seat's write surface and
the ask is filed in `docs/ideas.md` under today's date.
