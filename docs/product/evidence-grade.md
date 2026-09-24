# Evidence grade on every claim

**Built 2026-09-23** (engineer seat). This is the design record for the first
step of the ledger entry "Corpus expansion scoping spike (Q4) and Q1
objective" (docs/ideas.md, accepted 2026-09-18), which asks for an
`evidence_grade` column set at distill, five engineering-blog feeds, and a
practices variant of the distill prompt. The column, the grader, the tests and
the first feed shipped together. The other four feeds and the prompt variant
are the next slices.

## The problem

The corpus is taking in engineering blog posts alongside arXiv papers. A
paper's ablation table and a company's launch post are both text, both get
distilled into the same `claims` table, and once they are rows there is
nothing on either one that says which was measured and which was asserted. The
digest then prints them in the same voice, and the reader has no way to tell
them apart. The owner's guardrail for corpus expansion says the scope is
findings that carry cited evidence. Without a grade, the pipeline cannot tell
whether a row carries any.

## The rule

Two facts decide a claim's grade, and only two.

**Where the text came from.** `paper` covers arXiv and Hugging Face daily
papers. `field` covers everything that arrives through a feed in sources.yaml,
a frontier lab's own channel and a practitioner's blog alike. This comes off
the paper row, so the model cannot reach it.

**Whether the evidence carries a measurement.** The distill model answers this
per claim in a new `measured` field, and `pipeline/evidence.py` checks the
answer against the evidence text the model just wrote. If it called a claim
measured and then wrote evidence containing no number at all, the claim is not
graded as measured. The check runs one direction only. It can take away a
grade the model claimed and it can never award one the model did not.

Four grades come out of the pair, strongest first:

| grade | what it means |
| --- | --- |
| `controlled` | A paper, with numbers. A benchmark, a delta, an ablation. |
| `field_measured` | A practitioner or a lab reporting its own numbers. |
| `asserted` | A paper stating something it did not measure here. |
| `anecdote` | A field report with no measurement in it at all. |

`field_measured` ranks above `asserted` on purpose. A number someone published
can be argued with, and an assertion with no measurement behind it cannot,
whatever the venue it appeared in.

NULL means ungraded. That is the honest state of every claim distilled before
the column existed, and nothing backfills it, because the measurement judgment
belongs to the run that actually read the source.

## Where it lives

- `pipeline/evidence.py` — the rules, with no Modal and no psycopg in it, so
  they can be tested without a deployment or a database.
- `db/schema.sql` — the column, a check constraint naming the same four
  grades, and an index on it.
- `pipeline/distill.py` — the write. It asks the database whether the column
  exists before it uses it, so a deploy that lands before the schema run
  distills normally instead of failing every insert.
- `prompts/distill.md` — the `measured` field, defined as a question about
  whether a number is present and not about how good the work is.
- `tests/test_evidence_grade.py` — ten tests, run with `python3`. One of them
  reads the check constraint out of `db/schema.sql` and asserts it names the
  same four grades the module returns, because those two lists living in two
  files is exactly how a day of claims gets silently lost to a failed insert.

## What is deliberately not here yet

**The digest does not read the grade.** Surfacing it belongs in
`pipeline/weekly.py`'s `gather()`, and PR #60 is rewriting that file for the
daily issue. A second edit to the same function in a parallel branch buys
nothing today and costs the owner a merge conflict. It is filed in the ledger
as its own entry.

**When it does surface, it surfaces in plain words.** Ban-list item 14
(docs/voice/ban-list.md) forbids printing internal vocabulary at the reader.
`field_measured` is internal vocabulary. What the reader should see is the
plain-English version, something on the order of "measured in production" or
"the authors state this without measuring it".

**Nothing is backfilled**, as above.

**Blog posts are still distilled from their feed summary.** `fetch_fulltext`
returns None for anything that is not an arXiv id, so a practice report's
numbers usually sit in a body the pipeline never reads, and `field_measured`
will be rare until that changes. Filed in the ledger the same day this shipped.
