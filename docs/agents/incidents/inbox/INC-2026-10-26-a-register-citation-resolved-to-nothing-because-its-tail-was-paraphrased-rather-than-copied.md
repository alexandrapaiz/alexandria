## INC-2026-10-26-a-register-citation-resolved-to-nothing-because-its-tail-was-paraphrased-rather-than-copied - a seat reported a register entry missing, and the entry was present under a slug whose last clause had been rewritten in the citing report (2026-10-26, exo seat)

**What happened.** The engineer seat handed this seat a gap: the PM seat's
report in #605 cites an incident as shipped in this seat's #599, and the id
"resolves to nothing", absent from `docs/agents/incidents.md` and from the
inbox on `main`, on the engineer's branch, and on the branch said to supersede
the one carrying it. The engineer's search was correct and the conclusion it
invited was wrong. The entry exists. It was filed by commit `40e264b3` at
20:05:23Z and it is at `docs/agents/incidents.md:23678` on this seat's live
branch, under

```
INC-2026-10-26-a-merge-verdict-went-stale-in-six-minutes-and-the-note-carrying-it-named-no-snapshot
```

while the id the report cited, and the id the engineer therefore searched for,
ends `-and-the-api-agreed-with-the-stale-reading`. The two agree for the first
forty-nine characters and diverge in the clause that carries the finding. #599's
own description names the real slug; the citing report names the other one. So
`grep` returned nothing on every surface, including the one surface holding the
entry, and nothing in that answer distinguished a dropped entry from a
mistyped citation.

**Why it is in this register.** Third occurrence of the class this week, and
the class is **a precise-looking identifier that was reconstructed from its
subject rather than copied from its source.** The first was
`INC-2026-10-24-a-404-on-a-misspelled-repo-name-was-read-as-a-revoked-credential`,
where `alexandria-systems` for `alexandra-systems` cost two runs a false
finding about a credential, and the general rule this charter took from it is
in §0: a name a run types from habit is wrong by one letter, and the surface
answers a wrong name and a real absence identically. The second is the
`?since_hours=` / `?limit=` probe recorded in §2a-0, where guessed parameter
names were refused and the refusal was the answer. This is the first instance
where the reconstructed identifier was a *register id*, and register ids are
the worst case for it: they are sentence-shaped, so a paraphrase of one is
still a well-formed id, and `INC-YYYY-MM-DD-slug` deliberately allocates from
a date and a subject, which is what makes two runs describing one incident
produce two plausible ids for it.

**What it cost.** The engineer spent a search across three branches and two
files and routed a finding it could not resolve; this seat spent four commands
confirming the entry was never lost. No work was lost, because the engineer
declined to reconstruct the entry and handed the gap over instead, which is the
behaviour that kept this cheap: a seat that had "restored" the missing entry
would have filed a second copy of a live incident under a second id, and the
register would now carry the duplicate this inbox exists to prevent.

**The fix, or why there is not one yet.** Two halves, and only one is this
seat's.

The repair to the surface is `tools/incidents.py check`, which already fails on
"a filename that does not match the id in its own heading" and on an id already
in the register. It does not read citations. A citation checker — every
`INC-\d{4}-\d{2}-\d{2}-[a-z0-9-]+` string under `docs/` and `prompts/` resolved
against the register and the inbox, failing on any that resolves to nothing —
is the mechanical form, and the Ursa skill seat built exactly that this evening
against `tools/registers/registers.json` and reported 98 cited, 83 exact, 0
broken on its default branch. That is the instrument to adopt rather than
re-derive, and it is filed as owed on this seat rather than shipped here,
because this run's one improvement is spent elsewhere and an unmeasured
instrument shipped in a hurry is the thing §3b refuses.

**One trap for whoever builds it, found by this run getting it wrong first.**
The obvious resolution test is the one `tools/incidents.py check` already
enforces on inbox files: the id is the `## ` heading. Run that against the
register and it reports this seat's own
`INC-2026-10-26-three-disposition-verdicts-on-one-pull-request-in-twenty-two-minutes-and-none-named-the-head-commit`
as broken, which is how this run briefly concluded a second entry was missing.
It is not. The id sits on its own line immediately below a date-and-prose
heading at `docs/agents/incidents.md:23728`, and **10 of the register's 350
`## ` headings are date-and-prose rather than ids**, all of them legacy. So a
heading-anchored checker starts life with ten false positives on `main`, and a
plain string search over the register and the inbox has none. Search for the
string; do not require it to be a heading. A checker whose first run is ten
false alarms is a checker nobody runs twice, which is the same shape as §2b's
third predicate that had never selected a row.

The half that needed no tool is the one already taken: **cite by copy, never by
recall**, and the cheap check is `grep -c` for the string you are about to put
in a report before you put it there. The citation in #605 was written by a seat
reading this seat's report rather than this seat's register, which is the same
one-layer-removed read that §2a-0 records about the relay page saying
`DELIVERED` while the route it described was already fixed.

The entry itself needs nothing: it is correct, it is live, and it is off `main`
only because this seat's chain is seven deep and unmerged, which is reported as
a merge-throughput fact rather than as a register fact.
