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

A NULL grade means ungraded, which is the honest state of every claim
distilled before this column existed. Nothing backfills it, because the
model's measurement judgment is a fact of the run that wrote the claim and
cannot be recovered afterwards.
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
