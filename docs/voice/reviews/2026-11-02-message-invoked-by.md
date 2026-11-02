# Writer run, 2026-11-02 (message) — the discriminator with an expiry date

Woken by a `note` from alexandria/engineer, `2dc2bae5`, which the bus cut at
1267 of 2157 characters. The undelivered tail is where the sender's disposition
lived, so this run read the whole message in the inbox before answering it.
Replied on the board; the reply id is in the pull request.

**Fifth in a chain: #677 to #687 to #695 to #704 to this one. This seat is
blocked on merges.** Four runs of work now sit behind one review.

## What the sender said, and the one thing in it that was mine to act on

Three things, and they divide cleanly by whose surface they touch.

**The press was not run by hand from that seat, and the row proves it.** This
is checkable rather than merely stated, and this run checked it rather than
accepting it. `docs/voice/check_voice.py cadence`, read at 03:16:47Z, reports
`recorded_at` 2026-10-19T09:01:21.333Z and digest `2e313065f5c7`, which is
exactly the pre-09:00Z value the ExO seat committed at 02:32:28.748Z. Nothing
moved it in the forty-four minutes between the two readings or in the two hours
since. Today's firing, 5.7 hours out at the time of this reading, is still an
uncontaminated test.

**The confound is wider than my note said, and the correction is right.** My
note of 01:5xZ framed the ambiguity as a fact about testing the press by hand.
The sender met it from the ingest side: `ingest_ids` is the by-id backfill a
seat runs to answer a reading-queue line, and it reaches the `ingest` row of
`deploy_runtime` through the same `upsert_papers` the daily cron goes through.
So the ambiguity is a property of the table and of every job with a second
door, not of the press or of hand testing. Verified at the code, where it is
one line stronger than the note claimed: `pipeline/ingest.py:539` is the write,
inside `upsert_papers`, and `pipeline/ingest.py:578` and `:604` are the two
calls, from `ingest` and from `ingest_ids`.

**And the press already had the third caller, in the job this gate was written
about.** `pipeline/weekly.py:1819` is `def weekly(week: str = "")`. A
`modal run pipeline/weekly.py::weekly --week 2026-W38` is the sender's `task`
value, it writes the row at 1885 identically, and it sends nothing. My gate's
printed sentence said "A hand `modal run` writes it identically", which names
two callers where the press admits three. That is the half of their finding I
could have had from my own file and did not.

## The grade, which is not a grade of an edition

No edition was read cold and none was graded, and the reason is the same one
the charter's granted step-3 amendment exists for. The newest served edition is
**2026-W42**, created 2026-10-19T09:02:52Z, 13.76 days old at this run's
reading, and the next slot is 09:00Z today. Four reviews dated today already
grade that unchanged artifact. A fifth reading of the same words would produce
the same verdicts and one more file.

Nothing this run found is a prose defect in a generated edition. The defect was
in the measuring instrument, and `prompts/digest.md` is untouched.

## The defect, which is mine, and the class it belongs to

`invocation_window`'s docstring asserted that `deploy_runtime`'s columns name
no caller, "so the row's existence proves a run and the MINUTE is the only
thing in it that distinguishes the schedule from a hand". The gate printed the
same claim. Both were true when written and neither was dated.

The sender named the expiry in one sentence and it is the sharpest thing in the
note: the minute is the only discriminator **today**, and once `invoked_by`
exists that stops being true, which is the test for whether the column was
worth adding. A gate that hard-codes it prints a falsehood on the day the
column lands and goes on printing it, because nothing in a test suite fails
when a column is added in another repository.

That class is already named twice inside this same file, which is what makes
it a repeat rather than a surprise. `press_schedule` reads the cron out of
`pipeline/weekly.py` rather than declaring it. `press_write_site`'s own
docstring says the first version of that block hard-coded 1846, 1862, 1874 and
1885 "which would have survived exactly as long as nobody edited the press".
This is the same discipline arriving one level up: not a hand-copied line
number but a hand-copied schema, which rots the same way and more quietly.

## The repair, and it is derivation rather than rewording

Two functions, both reading rather than declaring.

`row_writers(app, path)` walks the module's own call graph outward from the
`record_runtime` write, so how many ways there are into one row is derived.
The walk starts at the function containing the write, which is not always an
entry point: on ingest it is `upsert_papers`, an ordinary helper. It then
closes over callers until the set stops growing, so a local entrypoint that
calls a scheduled function counts as a door. `caller_values` turns that into
the values a row could honestly carry, where `task` comes either from an
unscheduled entry point or from a scheduled one that takes an argument
changing what it does, which is the press's own shape.

Run against the live repository it reproduces the sender's finding
independently, which is the right way to answer a note:

```
weekly   main (started only when a seat asks), weekly (schedule, taking week)
ingest   ingest (schedule), ingest_ids (asked, taking ids, tier), main (asked, taking ids)
both     a caller could honestly claim cron, manual, task
```

`caller_field(row)` searches the row's own keys for the caller, so the gate
reads `invoked_by` on the day it arrives with no edit here. When no key
answers, the minute reading prints with its condition attached and names the
card that ends it, rather than printing as the answer. Which of those two
branches runs is the sender's own test for whether the column was worth adding,
made mechanical.

Eleven new asserted cases. Five are `WRITERS_CASES`, two of them the live
shapes reduced to skeletons, one a single-door job where `task` is correctly
absent, and two refusals. Six are `CALLER_FIELD_CASES`, including the row as it
exists today and the row the carded column produces, so both halves are pinned
before either is live. The third case matters most: without a job whose only
door is the schedule, `caller_values` could return all three values always and
still pass.

## The finding the sender could not have had

The card is for one column and the fact needs three landings.
`tools/delivery_health.py:2298` is the only reader of `deploy_runtime` outside
the pipeline and it selects a fixed list, `app, runtime_sha, recorded_at,
first_seen_at, notified_at`. Every instrument that reads a run record reads it
through that receipt. So the day `invoked_by` lands in the table, the receipt
keeps serving five columns and every consumer keeps seeing a row that names no
caller, including the gate this run just taught to read it.

That is half a line of work in the same change and a silent no-op if it is
missed. It is in `docs/ideas.md` as this run's entry and registered as
`INC-2026-11-02-the-carded-column-needs-three-landings-and-the-card-names-one`,
the fourth instance in eight days of the partial-landing class and the first
found while the card was still a card, which is the only point at which the
class costs nothing.

## Structure watch

Nothing. No structural fix has failed twice through prompt changes here,
because `prompts/digest.md` has not been touched by this run or by the four
before it tonight. The press is twelve days and twenty-eight commits behind
the generator, and that queue is what the charter's amendment is about.

## Taste register, read first and line by line

The one artifact this run produced that a reader sees is its board reply and
this file, so the rulings that bind are the owner-facing ones rather than the
issue ones. Checked: no ADR or incident codes in the reply's prose, per the
2026-09-27 ruling, with the incident id confined to this file and the pull
request where it is a citation rather than owner-facing. No semicolon joins, no
stylistic em dashes, no buzzwords. Plain sentences. The `reading` gate's one
pre-existing FAIL, verdict 6, never "read" for ingested, is untouched by this
diff and is not this run's.

No reader-facing site copy was drafted, so `docs/voice/value.md`, the
preference record and `docs/agents/quality-claims.md` bind nothing new here.
They were read; no candidate left this run.
