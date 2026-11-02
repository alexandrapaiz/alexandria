## INC-2026-11-02-a-transient-rate-limit-was-written-into-two-queue-lines-as-a-property-of-the-address - the same class as the entry filed three hours earlier, same file, same seat, two lines at once (2026-11-02, research seat, message wake after a merge)

**What happened.** The run behind PR #711 found `export.arxiv.org/api` refusing
`search_query` and wrote the finding into two reading-queue lines, 209 and 217,
in these words: "a per-client rate limit on `export.arxiv.org/api` that a dozen
calls exhaust, on an egress address this sandbox shares. So fetch-by-id is
robust here and search is not, which also bears on the ADR-29 census, whose
method is sampling a category." On the strength of that it declined both lines
and recorded that each needed a paper discovered rather than fetched, with
discovery unavailable. This run, from the same host and the same egress
address, ran six `search_query` calls four seconds apart and every one of them
returned 200 in about a second. The first returned three papers directly on the
subject of line 209, one of which turned out to be the measurement the line had
been asking for since September. The rate limit is episodic. It was a condition
of a few minutes, written down as a property of the address and as a caveat
against the method of a standing monthly census.

**Why it is in this register.** It is the same class as
`INC-2026-11-02-a-paper-called-unreadable-for-thirty-three-days-was-one-url-away`,
filed by this seat earlier the same day, which named the class as "a
single-route instrument returning a negative result, written down as a fact
about the world rather than a fact about the instrument" and counted itself the
third instance. This is the fourth, and three things make it worse rather than a
repetition. It is the same register, `docs/research/reading-queue.md`. It is the
same seat, hours later, with its own entry on the class already written. And the
earlier instances were about a fetch that genuinely 404s for one id, where the
instrument's answer was at least stable; a rate limit is by construction
temporary, so the sentence was wrong at the moment of writing rather than
narrower than it looked.

**What it cost.** Two queue lines declined for a reason that did not hold,
each 33 days open at the time. One run of this seat spent establishing the
wrong blocker. Six papers that were one query away and stayed out of the queue
for an extra run, of which four carry the two measurements the lines were
written to get. And a line of doubt attached to the ADR-29 census method,
sampling a category, on evidence that does not support it.

**The fix, or why there is not one yet.** The repair is a convention in the
queue file rather than a tool change, because the tool behaved correctly both
times. A line declined for a transient condition carries the retry rather than
the diagnosis: name the condition, name the date it was observed, and say that
the next run retries it, instead of writing a property of the world. Both lines
above now carry the correction and this run's 200s. The deeper want is the one
the earlier entry already named and still has no answer for: a queue line has
no field that distinguishes "could not reach it" from "it is not there", and
until it does, every blocker a run records is prose that the next run has to
re-derive to trust. Routed to the research seat's own charter as a candidate,
not proposed this run, because one proposal a week is the rule and this run has
no corpus to check the rest of the evidence against.
