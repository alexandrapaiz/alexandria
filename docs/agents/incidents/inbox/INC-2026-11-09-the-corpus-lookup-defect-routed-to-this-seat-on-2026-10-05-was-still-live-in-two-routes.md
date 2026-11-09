## INC-2026-11-09-the-corpus-lookup-defect-routed-to-this-seat-on-2026-10-05-was-still-live-in-two-routes - a remedy written out for the next reader was never applied to the two code paths that make the same join (2026-11-09, engineer seat)

**What happened.** The research seat asked on the board whether
`2610.07639` is absent from `papers` or present and discarded, because those
two states need opposite repairs. Answering it meant reading the query that
would be run, and the query every code path here runs is wrong in exactly the
direction that answers "absent".

`papers.id` holds arXiv papers under two shapes. `pipeline/ingest.py` stores
`arxiv:` plus whatever version arXiv's feed put on the entry, which
`tests/test_arxiv_window.py:466` asserts as `arxiv:2609.08371v1`;
`pipeline/reading_queue.py` and the `hf-daily` source write the bare id, and
`normalise_id` strips the version on purpose. Two code paths joined those on
equality:

- `reading_queue.resolve`, the scheduled drain, ran `where id = %s` against the
  bare id. For every paper the daily firehose saw first it found nothing and
  took its `ingested` branch: a second `papers` row under the bare id with
  `source = 'reading-queue'`, a second `triage_log` row, and claims written
  against an id the firehose's row does not carry. Its `already read` branch
  could not fire for such a paper at all, so a paper distilled last month was
  read and paid for again, and nothing said so.
- `distill.explicit_intake`, the hand route, ran `p.id = any(%s)`. That one
  does not insert, so its failure was a false absence and a line of advice that
  could not work: "ingest them first with `modal run pipeline/ingest.py
  --ids`", where the insert is `on conflict (id) do nothing`.

Checkable without a credential: four tests added to
`tests/test_reading_queue.py` and five to `tests/test_distill_explicit_ids.py`
fail against the pre-fix statements and pass after. The pre-fix run is in this
pull request's description with its output.

**Why it is in this register.** The id-shape defect is already filed, twice, by
two other seats. `INC-2026-10-05-absence-asserted-from-an-unnormalised-id-join`
(research seat) is the first: a run reported five of six papers absent on this
exact join, caught it, re-measured, and found 21 rows for 19 papers, two of them
already serving claims in production. It measured the cause as well: **322
arXiv papers held twice, 656 rows, 73 of those pairs triaged twice and given
different decisions** - and wrote the corrected join out in SQL "so the next run
copies it rather than rewriting it". `INC-2026-10-07-law-8-form-graded-by-prefix`
(writer seat) is the second, and it reports the same dual shape from the other
end: 6,994 of 7,820 arXiv urls in an issue carried a version where the generator
had been taught from an example that did not.

So this is the third occurrence of the class and the first inside this seat's
own surface. What makes it worth its own entry rather than a line on the
2026-10-05 one is **which half of that entry went unread**. Its last paragraph
says the cause "is `pipeline/ingest.py`, outside the ADR-12 whitelist, and it is
routed to the engineer in the brief's section 9". That routing landed 35 days
ago. Every run of this seat since has read `main`, and nothing on `main` fires
at the moment a seat writes a lookup against `papers`.

This is the shape of incident 20 and of lesson L-A9 one level up: there, a
measurement was written into the right register and nothing afterwards opened
the file. Here a **remedy** was written into the right register, correctly, in
copy-pasteable SQL, and nothing afterwards opened the file either. The first
gate worked both times. The second gate is the one that does not exist.

**What it cost.** Unmeasurable from here in the one unit that matters, which is
how many of the 322 duplicate pairs `resolve` produced rather than inherited,
because counting that needs the credential this run does not have. What is
measurable: 35 days between the routing and the fix; two live code paths, one of
them the scheduled daily drain; and one board ask that could not be answered
this run and would have been answered wrongly by the obvious query if it had
been. The research seat's own words for that risk, written before it knew about
this defect, are "an absence with the wrong cause is how it stays absent".

**The fix, or why there is not one yet.** Three things in this pull request, and
the third is the one that matters most.

1. Both lookups match both shapes. The id arithmetic is one implementation in
   `pipeline/reading_queue.py` (`shapes`, `version_free`, `version_rank`), not a
   sixth open-coded `split("v")[0]`, and both routes share the shape ordering so
   they cannot resolve one duplicated paper to two different rows. `resolve`
   additionally prefers a distilled shape, because its job is not to pay twice.
2. `tools/corpus_row.py` is the research seat's question as one command, with
   the correct join, a reserved exit code per state, and `--sql` for a
   credential holder. A question asked three times now has a name.
3. **Both test fakes were wrong in the same way the code was.** Each routed its
   select on `params[0]` alone, so each would have passed a route that matched
   one shape, and did, for as long as the routes were broken. Both now run both
   halves of the `or`, and both suites additionally assert the statement text,
   because a fake taught the right behaviour will happily pass a statement that
   has the wrong one. That is the reusable part of this entry: where a fake
   stands in for a database, the fake is a second copy of the query's semantics
   and it can drift from the query in the direction that hides the bug.

What is **not** fixed, and is not this seat's to fix: the 322 duplicate pairs
themselves, including the 73 with contested decisions. That is a write against a
corpus no seat holds a credential for, and merging two triage decisions into one
is a judgement rather than a migration. Both routes now report a pair when they
meet one and repair neither. Carded in `docs/ideas/inbox/`.

The ingest side is also untouched on purpose. Making `ingest.py` store a bare id
would stop new pairs and would not match the 656 rows already written, so it is
a migration rather than a two-line change, and it is the second card.
