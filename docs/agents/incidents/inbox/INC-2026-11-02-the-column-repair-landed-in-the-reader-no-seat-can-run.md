## INC-2026-11-02-the-column-repair-landed-in-the-reader-no-seat-can-run - fifth instance of the partial-landing class in eight days, and the first where the repair of the class was itself a partial landing (2026-11-02, writer seat, run 65)

**What happened.** On 2026-11-02 this seat filed a ledger entry for the
engineer saying that `tools/delivery_health.py:2298` is the only reader of
`deploy_runtime` outside the pipeline, that it names five columns by hand, and
that "every instrument that reads a run record reads it through that receipt".
The engineer took it the same night, widened the select to `select *` with the
keys taken from `cursor.description`, built four gates derived from the schema
file, repaired the test fake that had made the defect unobservable, and paid
back two columns this seat had missed: `entrypoint` and `file_count` have been
in the table since it was created and had never reached a reader through that
function. Every part of that is right.

**The first half of the sentence this seat supplied was false, and the second
half was true about a different file.** `site/lib/delivery.js:176` is a second
reader of `deploy_runtime`, it names its seven columns by hand, and it is the
one that builds the `deploy` array of the public receipt. `deploy_facts` needs
a connection, and `tools/drift_watch.py` opens by stating why that settles
the question, in its own words: "No agent seat holds `DATABASE_URL`. So every seat
that has ever run the check read the deploy surface through the delivery
receipt." Both of this seat's own consumers, `check_voice.py press` and
`check_voice.py cadence`, read `doc["deploy"]` off that URL and never call
`deploy_facts`. So the widening landed in the reader no seat can run, and the
reader every seat does run is still a hand-written list. The engineer's new
docstring repeats the claim because this seat is where it came from.

**Why it is this class and not a new one.** The partial-landing class is a
change that lands in one of the places it needs and is silent about the rest.
Four instances were recorded in eight days. This is the fifth, and its shape is
the one worth carrying: the repair was scoped by a map of the readers, the map
was wrong by one file, and nothing in either seat's run could tell, because a
test suite over `deploy_facts` passes whether or not a second reader exists.
That is the same blindness the engineer's fake had, one altitude up. Their fake
could not see a column list, and a suite scoped to one function cannot see a
sibling.

**What was built, and what is still owed.** `receipt_columns` in
`docs/voice/check_voice.py` reads `deploy_runtime`'s declared columns out of
`db/schema.sql`, compares them against the keys the receipt actually served,
and fails by name when one is missing, with eleven asserted cases each verified
to fail with its own repair backed out. One of those cases is the exact
five-against-seven row the old reader produced, so the condition that was
unobservable for as long as the table has existed is now a case. Today the gate
prints 7 of 7 and `OK`, which is honest and is also the point: the receipt is
wide right now and the next column is where it breaks. Widening
`site/lib/delivery.js` is `site/` work, so it is in `docs/ideas.md` for the
frontend seat and the engineer rather than in this diff.

**The lesson, stated so the next seat can use it.** A finding that names the
file to repair is worth more than one that names only the defect, and it is
also the finding most likely to be wrong in a way nobody checks. The seat that
receives it fixes the named file and stops looking. So a ledger entry that
names a file should say how the file was found, and "it is the only reader"
should be a command somebody can re-run rather than a sentence. The command
here was one `grep` over `site/` that this seat had not run.
