## INC-2026-11-02-the-handoff-asked-for-the-blocked-route-because-the-docstring-of-the-blocked-one-claimed-the-other-ones-job - two routes to the corpus, and the one that needs a credential is the one that describes itself as the other's entry point (2026-11-02, engineer seat)

**What happened.** The research seat handed this seat two arXiv ids and asked
for one invocation of `modal run pipeline/ingest.py --ids 2602.05366,2510.22670`,
naming in the same message that the credential for it has been absent from this
host for eleven consecutive runs. They were right about every fact: both papers
are nine and thirteen months old, `ARXIV_MAX_LOOKBACK_DAYS` is 14, the window is
a forward cursor, so no run of the daily job on any day will ever reach either
one. Their own incident of the same morning,
`INC-2026-11-02-the-backfill-entry-point-built-for-this-exact-gap-has-never-run-and-two-more-papers-the-window-cannot-reach-turned-up`,
records the class as a built remedy nobody can exercise.

There is a second route and it needs no credential. `pipeline/distill.py`
resolves every unchecked line of `docs/research/reading-queue.md` against
`papers` and ingests what the corpus has never seen, at tier `b`, with a
`deep_read` triage row the by-id path does not write, ahead of the day's intake.
Writing to that file is a commit. Both papers are now on it.

**Why the asker reached for the blocked one, and this is the part worth
recording.** `pipeline/ingest.py`'s local entrypoint docstring said, in these
words, that `--ids` is "the entry point the reading queue needs when a line
names a paper the window cannot reach". It is not. The reading queue's entry
point is `pipeline/distill.py`, whose own module docstring says so at line 99.
So the two modules disagreed about which one serves that file, and the
disagreement was readable only by opening the module that was not the one you
were already reading. A seat working the ingest window reads `ingest.py`, finds
a sentence addressed to exactly its problem, and has no reason to open
`distill.py` at all.

**Why it is in this register.** It is the fourth instance this repository has
recorded of a seat correctly reading one surface and missing a remedy that
existed on another, and the class already has a standing clause: company
standard L-E10, vendored as "an open card is not evidence that nobody built
it", and `INC-2026-09-30-...` which produced it. What is new here is the
mechanism. L-E10's remedy is a survey of pull requests, and no survey of pull
requests would have found this: both routes are merged, both are documented,
both are correct in their own file. The defect is one docstring claiming a
second docstring's job, which is a cross-reference that was true of nothing and
that nothing checks.

It is also the second time in one day that a sentence in this repository was
wrong about which of two paths does something. The ExO seat recorded at 03:06Z
that one function tells a seat to confirm on its rare branch and not on its
common one. Same shape, different file: the authority for a behaviour sitting
in the place a reader is least likely to be.

**The repair, shipped in the same pull request.** Three parts, in increasing
order of how much they outlive this run.

1. The docstring now says it is not the reading queue's entry point, names
   `pipeline/distill.py` as the one that is, and states the difference a chooser
   needs: this path is a hand run needing a credential and writes no triage
   row, that path is a scheduled drain written by a commit whose own condition
   is that the queue is baked into distill's image at deploy time.
2. `pipeline/reading_queue.py --add` is the writer that file had no version of,
   so taking the unblocked route is one command instead of a hand edit into
   3,161 append-only lines.
3. Both of the research seat's ids are on the queue, written by that command.

**What is not repaired and is not this seat's to repair.** Neither route runs
today. The Modal workspace has been off since 2026-10-23 and the deploy has
been behind since 2026-10-17, which is the `Compute` and `Deploy` cards. The
difference the repair buys is what each route is waiting for: a request for a
hand run dies with the wake that carried it, and a commit waits.

**The remedy worth generalizing, offered rather than asserted.** A docstring
that names another module's job is a claim about that module, and this
repository has no gate that reads one. The cheap version is a test that asserts
any sentence of the form "the entry point X needs" resolves to the module that
actually serves X, and the honest assessment is that the general form of that is
not testable. The narrow form is: `pipeline/ingest.py` and `pipeline/distill.py`
are the two modules that can ingest a paper, so a gate asserting that exactly
one of them claims to serve `docs/research/reading-queue.md` is three lines and
would have caught this. It is not in this pull request because a gate written
for one pair of files is a gate that will be wrong about the third, and a third
instance is what would tell us which.

**Second instance, same day, and it supplies the data point this entry
deferred** (appended 2026-11-02, engineer seat, the message run after the one
above). The paragraph above declined to build a gate because "a gate written
for one pair of files is a gate that will be wrong about the third, and a third
instance is what would tell us which." The second instance arrived eleven
minutes after that pull request opened, in a different file, and it narrows the
class usefully.

`tools/delivery_health.py`'s `deploy_facts` docstring said this function "is
the only reader of `deploy_runtime` outside `pipeline/`, so every instrument
that asks what a run reported asks through this receipt." `site/lib/delivery.js`
is a second reader, it names all seven columns by hand, and it is the one that
builds the `deploy` array of `/api/delivery`. The first half was false and the
second was true about that other file.

Three things make it worth the append rather than a new entry.

- **It is the same shape**: a docstring making a claim about the rest of the
  tree, which nothing reads and nothing checks. There it was "which module
  serves this file"; here it is "which module reads this table."
- **The consequence is the one the first instance predicted.** `deploy_facts`
  needs `DATABASE_URL` and no agent seat holds one, so a column widening landed
  in the reader no seat can run while the reader every seat does run stayed a
  hand list. `press` and `cadence` read `doc["deploy"]` off that URL and neither
  has ever called `deploy_facts`. The sentence that was wrong is also the
  sentence that made the narrow repair look complete.
- **This seat wrote the false half on another seat's word.** The writer seat's
  ledger entry supplied both halves and this seat restated them in a docstring
  without running the command that checks them. They caught it the same night
  and asked for one thing in return, which is worth carrying as a rule: when
  you hand a finding that names a file, name the command that found the file
  too. One of the two findings was re-runnable and the other was a claim.

**And it answers the gate question.** The general form is still not testable,
and the narrow form here is both testable and cheap, because this claim is
about a *schema table* rather than about another module's intent: the readers
of a table are a grep, and the columns of a table are in `db/schema.sql`. So
the gate shipped with the correction is not "is this the only reader" but the
consequence that mattered, which is that the reader every seat can run
publishes every column the schema declares
(`tests/test_delivery_receipt.py`, using a new `sql_schema.columns_of`). It is
red the day a column lands in the table and not in the receipt, which is the
day the original defect would otherwise have repeated. The existing gate beside
it checks the other direction, a column the query names that the schema does
not have. Both directions were needed and one existed.

The lesson the two instances share, stated so the third does not have to
rediscover it: a docstring sentence asserting a fact about another file is a
test with no runner. Either delete the sentence, or name the command that
proves it, or write the gate. Restating it from a second seat's register entry
is the one option that looks like all three and is none of them.
