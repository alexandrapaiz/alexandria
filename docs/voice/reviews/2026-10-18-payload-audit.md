# The generator against its payload, 2026-10-18 (writer run 41)

Branched from main. No writer pull request was open when this run started, so
nothing is superseded and the chain depth is one.

The lane was empty when this run opened the board. Its one item, the
quality-claims gate, merged to main this morning, so this run closed it and
created the next one, which is this page. An item rather than a note, because
`docs/standards/pm.md` section 14 requires one.

## The edition check, which comes before anything else

**Still no issue. The newest the press has produced is 2026-W40, sent
2026-10-05, and today is the thirteenth day since.**

```
$ python3 tools/delivery_health.py --surface press --no-notify
  FAILING  press     the newest issue is 2026-W40 and 2026-W41 has ended;
                     1 issue(s) missing
```

This run does not write the fifteenth consecutive grade of one unchanged
artifact. The verdicts of 2026-10-17 stand on 2026-W40 because the body is
unchanged, and the run of this morning already scored that artifact against the
market, which is the one thing a stale artifact is still good for.

So this run graded the other artifact in this seat's custody, which is the
generator itself, and it graded it against the only thing that decides whether
its rules can be obeyed: the payload the press actually builds.

**No database.** `NEON_RO_URL` and `DATABASE_URL` are both absent here, so
nothing below is a read of a stored row. Every statement about the payload is
read off `gather()` in `pipeline/weekly.py`, `PAYLOAD_CAPS` in
`pipeline/budget.py` and `db/schema.sql`, which are the three files that decide
what the model is handed.

| what | sha256[:12] |
|---|---|
| `prompts/digest.md` on main, before this run | `8597f19dac4b` |
| `prompts/digest.md` after this run | `0d52aa51b1e8` |

## The single biggest weakness

**The generator does not know which of its six streams carries which field, so
seven of its rules ask the model for something the row in front of it does not
hold. The model cannot refuse. It substitutes, and the substitution reads
exactly like the thing that was asked for.**

This was found once this morning, by accident, while the blind prose benchmark
was measuring something else: the in-line grade's second half asks what a paper
did not measure, nothing in the payload records an absence, and six of seven
grades in 2026-W40 filled that position with who ran the work. The benchmark
filed it as a missing field and moved on. It is not a missing field. It is one
instance of a class, and the class is what this page is about.

The class has a shape worth naming, because it defeats every gate this seat
owns. A rule asking for a field that does not exist does not produce an error
and does not produce an absence. It produces a well-formed sentence of the
right length in the right position, drawn from the nearest field that does
exist. Reading the issue cannot catch it, because the sentence is fine. Reading
the prompt cannot catch it, because the rule is fine. It is only visible when
the two are read against each other, which no gate did until today.

## What the payload actually holds

| stream | rows | what one row carries |
|---|---|---|
| `new_claims` | up to 22 | claim, topics, paper, url, tier, triage decision, score, edges, `evidence`, `procedure`, up to three authors, `institutions` |
| `superseded` | up to 10 | old claim, new claim, confidence, both papers, both urls |
| `supported_claims` | up to 12 | claim, paper, url, support count |
| `citation_movers` | up to 12 | paper, url, citations before, citations now |
| `deprecated` | up to 8 | old claim, contradicting claim, confidence, the OLD paper and the OLD url |
| `deep_reads` | up to 10 | paper, url, `why` (the triage note, 200 chars) |

Plus `week`, `dates`, `stats` and `prior_titles`.

One line summarises the whole audit: **five of the six streams carry neither an
institution, nor an author, nor an evidence string.** The traction slot leads
every issue at every cadence and is fed by two of those five. The fell-behind
slot is fed by two more. The reading list is fed by the fifth.

## The seven, graded

Each one gets the law it serves, the rule as it stood, what the payload holds,
and the smallest change that makes the rule obeyable. All seven prompt changes
are in this pull request.

### 1. The evidence grade names three sources and they sit on one stream

Law 6, and house law at the top of the file: in-line grades bind every item at
every cadence. The rule said "draw the grade from the payload's `evidence`,
source tier and support counts".

`evidence` and `tier` are on `new_claims`. The support count is on
`supported_claims`. An item from `citation_movers`, `superseded`, `deprecated`
or `deep_reads` has none of the three.

Fixed by naming what each stream can support. A support count is the strongest
grade this product prints, because separate groups reporting one effect is
replication. A fell-behind item grades on the number of newer results standing
against the older one, which the rows do hold. An item with none of the three
gets no grade, and the rule now says in those words that assembling one out of
the claim string is the failure: "nothing here says how widely that was tested"
grades our knowledge of the paper rather than the paper, and the reader cannot
tell the difference.

### 2. The reading list demands what a paper cannot establish, from a triage note

Law 6 again, and this is the sharpest of the seven, because the reading list is
the one place the issue asks a reader for an hour.

The rule said "say what this work cannot establish", and backed it with a
count: "that has failed on every entry of both prints of 2026-10-05, six of
six, so it is a count here rather than a sentence you are trusted with."

A `deep_reads` row is a title, a url and `why`. There is no evidence, no tier,
no support count, no procedure. Six of six was not a discipline failure. It was
the only available answer to an unanswerable question, and the prompt was
counting it.

Fixed: where `why` says something about how the result was got, that is the
grade. Where it does not, the entry says what decision the paper informs and
claims nothing about how well established it is. The stapled-grade count
survives, scoped to entries that have a grade, because it governs where a grade
sits and not whether one exists.

### 3. The attribution count is unsatisfiable outside one stream

Law 9, institution-first attribution, and ban list 111.

The gate said: list every named work, count the ones attributed to an
institution or a named author, "the two numbers are the same number or the
issue is not finished". It then cited its own evidence: "in the print of
2026-10-05 they were 5 and 12, and all four items in the fell-behind section
sat on the wrong side of it, which is the slot whose own rule in this file says
attributed by institution."

Those four items came from `deprecated` and `superseded`. Neither carries an
institution. Neither carries an author. The gate marked four items as failures
for not inventing a name, and the diagnosis it recorded blamed the slot.

Fixed in three places. The gate's denominator is now the named works whose
stream carries an attribution field. The rule's third form, the finding written
with no attributive phrase at all, is a pass rather than a shortfall. And the
fell-behind slot no longer says "attributed by institution", because its stream
cannot.

Ban list 111 is corrected rather than removed. The tell it names is real and
unchanged, which is an item with no agent anywhere in it. Its stated repair was
the one the payload could not supply.

### 4. The contradicted pair carries one url for two works

Law 8, links reach the full text, and the link rule's own counting clause:
every named work carries a link.

`superseded` carries both urls. `deprecated` joins `papers` on the old claim's
paper only, so the work that overturned the belief has no url anywhere in the
row. The fell-behind slot's first kind is about exactly that pairing.

Fixed in the prompt by naming the one join that is reachable, which is the
contradicting claim's own text at the front of a `new_claims` row, and by
saying plainly that where it is not found the newer work is not named, because
a url you reasoned your way to is a url you invented. The real fix is one line
of SQL and it is filed in the ledger.

### 5. The citation-movers item was required to be about work the payload never names

Law 5, traction leads, and the never-invent rule.

The rule, added after the print of 2026-10-05 buried a finding inside a clause
about a count, said "write the item about what the CITING work found".

A `citation_movers` row is a title, a url and two integers. Semantic Scholar
returned a count. Who cited the paper, and what any of them found, is not in
the payload at any point. The repair asked for something strictly absent, and
the nearest available answer is to call some other paper in the payload the
citing one, which asserts a citation relationship nothing recorded.

Fixed: the item is written from the finding of the paper whose count moved,
reached by matching its url in `supported_claims` or `new_claims`. Where the
url appears in no other row, the issue has a title and two numbers, which is
bookkeeping with a link on it, and the rule now says to drop it.

### 6. A branch that tells the model to go and read the paper

The fell-behind slot, on an item whose claim string dropped its context: "so
either go to the linked paper for the context the claim string dropped or cut
the item."

`call_model` in `pipeline/weekly.py` documents itself as "one prompt in, one
issue out, no tools". There is no fetch. An instruction to go and read
something is an instruction to supply it from memory, and supplying a paper's
context from memory is the exact invention that slot's own rules spend three
paragraphs preventing.

Fixed by deleting the branch. The remaining instruction is to cut the item,
which was always the honest half.

### 7. The owner's title ruling never reached the file her ruling named

This one is not a missing field. It is the same audit from the other side, and
it is the finding of the run.

On 2026-10-04 she ruled: "two issues should never have the same title. thats a
big and quite obvious issue." It was recorded in `docs/voice/taste.md` the same
day, and the entry ends "The writer carries this into the digest prompt as a
rule, not a hint."

The engineer built the payload half. `prior_titles` carries the last
twenty-four titles, and `ensure_fresh_title` refuses an exact repeat after the
fact. Fourteen days later `prompts/digest.md` contained no title-uniqueness
rule, never mentioned `prior_titles`, and enumerated six payload keys for a
payload that carries eight. The generator was handed the list of titles it must
not reuse and was never told the list existed.

What that costs, precisely. The backstop matches on normalised string equality,
so the repeat it catches is the verbatim one and the repeat that reaches a
reader is the reworded one, which only the generator can judge. And when the
retitle call fails, the backstop stamps the week's dates onto the repeated
title, which breaks her ruling of 2026-09-19 that the date does not belong in
that line. The last enforcement standing ends by spending another of her
rulings.

Fixed: the rule is in the title slot, `prior_titles` is in the payload
enumeration, and the ruling is canon law 16, so the grading instrument scores
it rather than taste.md merely holding it.

Filed as `INC-2026-10-18-a-taste-ruling-named-its-file-and-never-reached-it`.
It is incident 20's shape with a work order attached, which is the part worth
keeping: this ruling did not need a gate to find it. It named the file and the
seat in its own last sentence, and five writer runs read that sentence without
executing it, because each of them was holding site copy and the charter's
taste check is written as a check against the artifact in front of you. A
ruling whose artifact is the generator is invisible on a day the generator is
not the artifact.

## Two findings reported rather than fixed

**The preflight budget is short by the titles.** `worst_case_payload()` in
`pipeline/budget.py` builds every stream from `PAYLOAD_CAPS` and omits
`prior_titles`, which `weekly()` adds at line 1700. So the worst case the
preflight prices is smaller than the payload the press actually sends, by up to
twenty-four title strings. Engineer's surface, filed in the ledger.

**`dates` can never name a single day.** The prompt tells the model that the
cadence is a fact in the payload, that `dates` spans a range for the weekly and
names one day for a daily, and that it should settle the question there before
writing the title. One cron writes an issue, Monday at 09:00, and
`week_just_ended()` returns a range on every path. So the test can only ever
answer weekly, and roughly sixty lines of daily shape ride along in a prompt
whose budget is tight enough to carry a short edition for when it does not fit.

This run left all of it standing. Whether the daily ships is a product decision
and not a prose one, and law 9 says the daily's shape belongs in the base layer
rather than beside it. The number is the report: sixty lines, every run, for a
cadence that has never run.

## Checked before shipping

- `docs/voice/taste.md`, ruling by ruling. The artifact this time is the
  generator, which is how the title ruling of 2026-10-04 surfaced at all. The
  2026-09-19 date ruling and the 2026-10-04 title ruling are in direct conflict
  on the backstop's last resort, and that conflict is written into canon law 16
  rather than resolved by this seat.
- `docs/voice/canon.md`. Laws 5, 6, 8 and 9 are the four this run's changes
  serve, and law 16 is added.
- `docs/voice/ban-list.md`. Entry 111's repair corrected, its enforcement
  anchor moved with the text it cites. No entry deleted. `check_voice.py`
  reports every enforcement anchored again, which it did not after the first
  edit of this run.
  **No new tell was appended, and that is a judgment rather than an
  oversight.** Six of this run's seven findings are defects in the generator
  and not shapes in a printed issue, so they have no specimen a reader could
  meet. The two that do print are already on the register, which is entry 111
  for the item with no agent in it and entry 124 for the grade that names a
  person where a limitation belongs. Both were correct about the sentence and
  wrong about the cause, and correcting a cause is worth more here than a
  seventy-fourth row.
- `docs/voice/awaiting-her-word.md`. Nine rows, none of them touched by this
  run. This run drafted no site copy and no reader-facing line, so
  `docs/agents/quality-claims.md` and `docs/voice/value.md` do not gate it.
- `docs/agents/incidents.md`. One repeat appended.
- `docs/standards/lessons.md`, the `any` section. L-A21 is the law this whole
  run is an instance of: a gate is judged by what it can see, and the
  attribution count fired on schedule, passed its own audit, and was asking
  for a field the stream could not hold. L-A9 is why the title ruling needed
  canon law 16 and not another entry. L-A22 is why the check this run cannot
  write is the one it filed. There is no writer section in that file, so
  the seat's own law is this repository's canon.

## What this run does not fix

Nothing checks that a ruling in taste.md which names a file has reached that
file. The one above was findable by reading two files against each other, it
cost fourteen days, and the check is a command somebody could write in an
afternoon. That is the ledger entry this run is most confident about and the
one it could not write itself, because the surface is `tools/`.

And the deeper one, which this page is the first instance of: the generator is
2,400 lines of rules written over three weeks against a payload that was never
printed beside them. Seven mismatches were found by reading the whole prompt
against `gather()` once. There is no reason to believe seven is the number. It
is the number one pass found.
