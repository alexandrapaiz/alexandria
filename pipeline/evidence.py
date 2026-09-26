"""Evidence grade: what kind of support a claim actually has.

The corpus is about to take in engineering blog posts alongside arXiv papers
(docs/ideas.md, "Corpus expansion scoping spike"). Without a grade on the row,
a controlled ablation and a company's launch-post assertion arrive in the
digest as the same kind of sentence, and the reader has no way to tell them
apart. This module is the grader, kept free of Modal and psycopg so the rules
can be tested without a deployment or a database.

Two facts decide the grade, and only two:

1. **Where the text came from.** `paper` covers arXiv and Hugging Face daily
   papers: a preprint or a published paper, written to be checked. `field`
   covers everything that arrives through a feed in sources.yaml, whether it
   is a frontier lab's own channel or a practitioner's blog. Deriving this
   from the row rather than asking the model keeps it beyond the model's
   reach.
2. **Whether the evidence carries a measurement.** The distill model answers
   this per claim (prompts/distill.md's `measured` field), and this module
   checks its answer against the evidence text it wrote. The check is a guard,
   not a second opinion: it can only downgrade a claim the model called
   measured, never upgrade one it did not.

The four grades that fall out, strongest first:

- `controlled`     — paper, with numbers. A benchmark, a delta, an ablation.
- `field_measured` — a practitioner or lab reporting its own numbers.
- `asserted`       — a paper stating something it did not measure here.
- `anecdote`       — a field report with no measurement in it at all.

`field_measured` ranks above `asserted` deliberately. A number someone
published can be argued with; an assertion with no measurement behind it
cannot, whatever the venue.

A NULL grade means ungraded, which was the state of every claim distilled
before this column existed.

## The backfill, and what it can honestly recover (2026-09-26)

This docstring used to end "nothing backfills it, because the model's
measurement judgment is a fact of the run that wrote the claim and cannot be
recovered afterwards". The first half of that is now wrong and the second half
is still right, so it is worth being precise about which is which.

The owner's count: 693 of 746 claims have no grade, every one of them distilled
before 2026-09-24. A digest ranked over a column that is NULL on 93% of its rows
is ranked over nothing, and "ungraded" is not a neutral state when it is the
majority state. So `backfill_grade` exists and `pipeline/backfill_grades.py`
runs it.

What it recovers: the source class, exactly, from the paper id, which is a fact
about the row and not about the run. And the measurement, from the evidence text
the model wrote, using the same `has_measurement` check the live grader already
applies.

What it cannot recover: the model's own `measured` boolean. A fresh claim is
graded on two signals that have to agree, the model's judgment and the text;
a backfilled claim is graded on the text alone. That is a weaker test, and it
is weaker in a known direction. `has_measurement` is the permissive half of the
pair, so a backfilled grade can be one step stronger than the live grader would
have given the same claim, never weaker. `asserted` claims can come back as
`controlled` if the evidence quotes a number the paper did not measure itself.

That asymmetry is why the backfill is a separate function with its own name
rather than a default argument on `grade`. A caller reaching for
`backfill_grade` is asking for the weaker test on purpose, and a reader of the
call site can see it.
"""

import re

CONTROLLED = "controlled"
FIELD_MEASURED = "field_measured"
ASSERTED = "asserted"
ANECDOTE = "anecdote"

# strongest first; db/schema.sql's check constraint carries the same four
GRADES = (CONTROLLED, FIELD_MEASURED, ASSERTED, ANECDOTE)

PAPER_SOURCES = frozenset({"arxiv", "hf-daily"})

# any digit run: "38.2%", "7B", "three of four tasks" fails it, which is the
# intended direction — the guard is conservative on purpose
_NUMBER = re.compile(r"\d")


def source_class(paper_id: str, source: str | None = None) -> str:
    """'paper' for arXiv and hf-daily rows, 'field' for everything else.

    The paper id is the primary signal because it is the one thing ingest
    guarantees: arXiv ids and Hugging Face picks share the `arxiv:` key space
    (fetch_hf_daily writes `arxiv:<id>` so a curated pick upgrades a row the
    firehose already has), and every feed item is `blog:<feed>:<hash>`.
    `source` is the fallback for rows keyed some other way.
    """
    if (paper_id or "").startswith("arxiv:"):
        return "paper"
    if (source or "") in PAPER_SOURCES:
        return "paper"
    return "field"


def has_measurement(evidence: str | None) -> bool:
    """True when the evidence text contains a number at all.

    prompts/distill.md already requires every concrete number the source ties
    to a claim to appear in `evidence`, so a claim the model calls measured
    and then supports with no digits anywhere has one of the two wrong.
    """
    return bool(_NUMBER.search(evidence or ""))


def as_bool(value) -> bool:
    """The model returns JSON, and JSON from a model is not always typed."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1"}
    return False


def grade(paper_id: str, evidence: str | None, measured, source: str | None = None) -> str:
    """The grade for one claim. See the module docstring for the four values."""
    is_measured = as_bool(measured) and has_measurement(evidence)
    if source_class(paper_id, source) == "paper":
        return CONTROLLED if is_measured else ASSERTED
    return FIELD_MEASURED if is_measured else ANECDOTE


def backfill_grade(paper_id: str, evidence: str | None,
                   source: str | None = None) -> str:
    """The grade for a claim distilled before the column existed.

    `grade` with the measurement signal taken from the evidence text alone,
    because the model's `measured` boolean was never stored and cannot be
    recovered. See the module docstring for what that costs: this is the
    permissive half of a two-signal test, so it can be one step generous and
    never one step harsh.

    Deterministic, so running it twice on the same row gives the same answer,
    which is what makes the backfill idempotent.
    """
    return grade(paper_id, evidence, True, source)
