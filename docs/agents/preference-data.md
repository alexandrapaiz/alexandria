# Preference data — the schema for the owner's rulings

**Enforced at:** prompts/writer-agent.md §"Site copy is yours to draft"
step 4, prompts/pm-agent.md's ruling-capture step, and
prompts/exo-agent.md §3e every run.

Written by the ExO agent on 2026-09-21, on the owner's order, after
auditing `docs/voice/preferences/site-copy-2026-09-20.md` against its
stated purpose.

## Why this file exists

The org already has a place where the owner's rulings become permanent
law, which is `docs/voice/taste.md`. It is a register of rules and it is
working as designed.

Preference data is a different artifact for a different consumer. A rule
says "no marketing tone". Preference data says "here is the exact
sentence, here is her verdict, here is her reason in her words", which is
the form a taste model can learn from. The owner's Ursa project consumes
accept and reject pairs with reasons. Every hour she spends ruling on
candidates is training signal, and signal that was recorded in prose is
signal that has to be re-derived by hand before anyone can use it.

So the standing position: **her rulings are recorded twice, once as a
rule and once as data, and they are not the same write.**

## The audit of the first file, and the verdict

`docs/voice/preferences/site-copy-2026-09-20.md` is the first preference
file the org produced. It was written by the chair after the session of
2026-09-20 and it holds 22 rejected candidates across 8 rounds, plus 4
approved lines.

**As a human record it is good.** It keeps her words, it groups by round,
and it states the pattern the chair saw without pretending that pattern
is a verdict. The writer seat can read it and learn from it today, which
is most of its value.

**As data for a taste loop it does not hold up.** Nine defects, all
verified against the file.

1. **The metadata contradicts the body.** The header says "Six rounds."
   The body records R1 through R8. A dataset whose own count is wrong
   cannot be trusted by a consumer that does not re-read it.
2. **Five of 22 rows carry no verdict from her.** Two are "not chosen"
   and three are "implicit no". Those are facts about the session rather
   than rulings, so they have no label and cannot be a pair.
3. **One verdict is a question rather than a ruling.** Round five's is
   "can you tell theres a bit of a marketing tone?" Read in context it is
   plainly a rejection, and the reading is the chair's rather than hers.
   A dataset should not silently promote an inference to a label.
4. **The candidate text is missing or truncated in five rows, and the
   header promises verbatim.** Round four's home candidates are recorded
   only as "smoothed 'frontier moves every day' variants", and round
   five's are recorded only as "home A/B/C, library A/B". The actual
   sentences she rejected are gone. Two of eight rounds are substantially
   unrecoverable, which is the worst defect on this list, because no
   schema recovers text that was never written down.
5. **Rows bundle two and three candidates under one verdict.** Round
   four's library row holds three candidates and one "implicit no", and
   round six holds three candidates and one reason. When one reason
   covers three sentences, no consumer can tell which sentence the reason
   describes.
6. **There are no stable ids**, so nothing can cite a candidate. "R8
   Sheldon library" is a name in prose, not a key.
7. **The slot lives inside the prose.** "home line 2", "library intro"
   and "skills heading" are real structure, encoded as English, so every
   consumer writes a bespoke parser and each one parses differently.
8. **Approved and rejected are in separate sections and unpaired.** The
   approved home statement and the six rejected home candidates belong to
   one slot, and reconstructing that grouping is manual work.
9. **One row holds two rulings across time.** Round three's home A
   records "first 'i like ... smoother and less choppy?', then on the
   reworked opener 'i hate the tone'". Two events, one row, and the
   reworked opener that drew the second verdict is not recorded at all.

None of this is a criticism of the chair's write-up, which was done after
the fact, at the end of a long session, from a conversation. It is the
predictable result of capturing data as narrative. The fix is to capture
it as data during the session, in a schema, which is what follows.

## The format

Two files per session, and the split is the point.

- `docs/voice/preferences/YYYY-MM-DD-<topic>.jsonl` is the **machine
  record** and the canonical one. One JSON object per line, one object
  per candidate.
- `docs/voice/preferences/YYYY-MM-DD-<topic>.md` is the **human
  companion**: what the session was about, what changed in her thinking,
  and the pattern whoever wrote it saw. It carries no verdicts that the
  jsonl does not carry.

JSONL rather than a table for one reason. It appends cleanly during a
live session, one line per candidate as the verdict arrives, so the
record is complete when the session ends rather than reconstructed
afterwards. That is the defect that produced all nine findings above.

### The fields

```json
{
  "id": "2026-09-20-r8-home-01",
  "session": "2026-09-20-site-copy",
  "date": "2026-09-20",
  "surface": "site",
  "slot": "home.statement",
  "round": 8,
  "variant": "A",
  "author": "chair",
  "text": "Every day it reads the new papers, extracts the findings, and checks them against everything it has read before.",
  "verdict": "rejected",
  "reason_verbatim": "'it'. its describing the mechanism not what it delivers. or the value to a builder.",
  "reason_interpreted": null,
  "supersedes": "2026-09-20-r7-home-01",
  "recorded_by": "chair"
}
```

- `id` — `YYYY-MM-DD-r<round>-<slot-short>-<nn>`. Stable and citable.
- `surface` — `site`, `digest`, `mission`, `email`. What the words were
  for.
- `slot` — dotted and from a fixed list, so two sessions agree.
  `home.statement`, `home.line2`, `home.para`, `library.heading`,
  `library.intro`, `skills.heading`, `skills.line`, `skills.intro`,
  `mission.page`. A new slot is added to this list in the same commit
  that first uses it.
- `round` — integer, counted from one within the session.
- `variant` — `A`, `B`, `C` when several candidates were offered for one
  slot in one round, otherwise `A`.
- `author` — `writer`, `chair`, or `owner`. Who wrote the candidate. This
  is the field that makes the process measurable, because a session where
  every candidate's author is `chair` is the failure incident 25 records.
- `text` — the candidate, **complete and verbatim**. Never truncated,
  never summarized, no ellipsis. A candidate that cannot be quoted in
  full is not recorded, and its absence is noted in the companion file.
- `verdict` — `approved`, `rejected`, or `no_ruling`. Exactly these three.
- `reason_verbatim` — her words, unedited, or `null`. Her spelling and
  her punctuation stay as she typed them, because the tell is often in
  the typing.
- `reason_interpreted` — only ever filled when `reason_verbatim` is
  `null`, and it is always somebody's reading rather than her ruling. A
  consumer training on reasons uses the verbatim field alone.
- `supersedes` — the `id` this candidate was rewritten from, or `null`.
  This is what makes the trajectory readable, and the trajectory is the
  most valuable thing in the whole file.
- `recorded_by` — the seat that wrote the line.

### The rules that make it usable

1. **One candidate, one object.** Never bundle. Three candidates in one
   round is three lines.
2. **No verdict, no label.** `no_ruling` rows stay in the file, because
   what was shown and not ruled on is real history, and they are excluded
   from any training set by the `verdict` field alone.
3. **Never promote an inference to a ruling.** If she did not say it,
   `reason_verbatim` is `null`.
4. **Pairs are derived, never stored.** For any `slot`, every `approved`
   row pairs with every `rejected` row in the same slot. Storing pairs
   would duplicate text and drift.
5. **Append during the session.** The line is written when the verdict
   arrives. A session recorded afterwards loses the candidate text, which
   is finding 4 above and is unrecoverable.
6. **Append-only.** A later ruling that reverses an earlier one is a new
   line with `supersedes` set, never an edit.

### Migrating the 2026-09-20 file

Worth doing and not worth faking. Sixteen of the 22 rejected rows and all
4 approved lines convert cleanly, because their text and her reason are
both present. Five rows convert with `verdict: "no_ruling"`. The round
four and round five candidates whose text was never written down cannot
be converted at all, and the honest migration records that gap in the
companion file rather than inventing the sentences.

The existing markdown file stays exactly as it is. It is the human
companion for that session, and it is also the evidence for incident 25.

## Who owns this

**The chair records**, in the session, as it happens. That matches
`docs/voice/taste.md`, where the chair or the PM records her rulings, and
it is the only actor present when a ruling is given in chat.

**The writer consumes**, every copy round, as the newest file in
`docs/voice/preferences/`.

**This seat audits** that the record exists and that its `author` field
is telling the truth about who is doing the drafting. That is
prompts/exo-agent.md §3e.

## What this page does not decide

Whether Ursa ingests this schema, and what it trains on, is the owner's.
This page's claim is narrower and it is the only one this seat can make:
the data as recorded on 2026-09-20 is not machine-consumable, the fix is
cheap, and the cost of not fixing it is paid every time she rules on
another twenty candidates.
