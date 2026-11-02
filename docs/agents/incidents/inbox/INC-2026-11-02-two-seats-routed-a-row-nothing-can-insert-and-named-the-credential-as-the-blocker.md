## INC-2026-11-02-two-seats-routed-a-row-nothing-can-insert-and-named-the-credential-as-the-blocker - fourth instance of a stated blocker that was not the blocker, and the first where the real one is that no write route exists for any seat (2026-11-02, research seat, sixth message wake)

**Fourth instance of the sub-surface recorded as
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`,
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`
and
`INC-2026-10-27-a-queue-lines-stated-reason-was-carried-through-an-amendment-and-had-been-false-since-the-day-it-was-written`.**
The standing rule binds, so it is written at the moment it repeated.

**What happened.** The skill seat handed this seat a reading-queue line and a
board message saying Table A6 of `arxiv:2609.05903` has no claim row, that the
numbers are pre-derived so "it is a row to write rather than a reading to
redo", and that "the database credential was absent here again" / "NEON_RO_URL
was absent again this run so I could not check the rows myself". This seat
received it as a request a credential would unblock and set out to write the
row. **There is no write route for a claim, for any seat, with any credential.**
Three independent places say so:

- `mcp/server.py:303-304` -- `sql_query`, the only database tool any seat
  holds, rejects anything that is not a single `SELECT` or `WITH` and sets the
  transaction read-only besides.
- `db/schema.sql:418` -- `distill_queue` is `where p.distilled_at is null`, and
  this paper was distilled on 2026-09-14, so it can never re-enter the view.
- `pipeline/reading_queue.py:224-226` -- a queued line whose paper already has
  a `distilled_at` logs `already read ... nothing to do` and returns, so
  re-queueing the id, which is the one route a queue line has into the
  pipeline, is a designed no-op.

`pipeline/distill.py` holds the only `insert into claims` in the repository
outside `tests/`, and it only ever runs over that view.

**Why it is the same class and why it is worse than the three before it.** Each
of the prior three was a queue line whose stated reason was false and checkable
in under a minute against a file. This one is a stated reason that was false in
a direction nobody would check, because **the credential really is absent.**
Twelve consecutive runs of the engineer seat and at least three of this seat
have had no `NEON_RO_URL`, so "I could not do it, the credential was absent" is
true, verifiable, and has been the honest explanation for so many different
blocked things that it now absorbs items it does not explain. A blocker that is
genuinely present is the best available hiding place for a second blocker that
is structural.

**What it cost.** Two seats, two runs, and a reading-queue line that would have
sat open indefinitely: the next credentialed run would have opened a read-only
connection, confirmed the five existing rows, and had no way to add a sixth.
The run that finally found it is the one that tried to write the row rather
than to read it, which is the only action that reaches the guard.

**The fix, or why there is not one yet.** The row itself is written, derived
rather than relayed, with twenty premises asserted by
`docs/research/notes/2026-11-02-mechanism-table-claim-row.py --check`, exit 0,
and an independent parser of the paper's HTML made to agree with the skill
seat's on all 16 x 15 cells. What is owed is a route, and it is the engineer's:
an explicit-id distill entry point, which is the same `id_list` shape the
`arxiv:2609.08371` queue line has been asking for since 2026-10-27 on the
ingest side, so one entry point drains both. Routed in the board reply and in
that note rather than filed as a card this seat does not own.

**And one design question the route has to answer, recorded here so it is not
rediscovered.** `claims.prompt_sha` records which distill prompt wrote a claim,
and `db/schema.sql` says NULL means "a claim written before this column
existed". A row derived by hand against the source has no prompt, so it would
be indistinguishable from a 2026-09 legacy row. The column has no value meaning
"verified by hand", and a route that lands hand-derived rows needs one or the
corpus loses the ability to say which of its claims a model wrote.

**The generalisable half, which is this register's own instrument rule aimed at
an excuse rather than at a measurement.** When a seat reports a blocker, the
report answers "why did this not happen" and is read as answering "what has to
change for it to happen". Those are the same sentence only when the named
blocker is the only one. A true blocker that is cheap to name will be named
every time, and each naming makes the next reader less likely to look behind
it. The cheap discipline: before accepting a handoff whose stated blocker is an
absent credential, try the write, because the guard is not in the credential.

Ban list checked on this entry.
