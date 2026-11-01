"""Evidence grade: what kind of support a claim actually has.

The corpus is about to take in engineering blog posts alongside arXiv papers
(docs/ideas.md, "Corpus expansion scoping spike"). Without a grade on the row,
a controlled ablation and a company's launch-post assertion arrive in the
digest as the same kind of sentence, and the reader has no way to tell them
apart. This module is the grader, kept free of Modal and psycopg so the rules
can be tested without a deployment or a database.

Three facts decide the grade, and only three:

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
3. **Whose result the claim is about.** A claim about an experiment the source
   ran and a claim about what some other work found are different kinds of
   row, and until 2026-10-26 they were the same kind of row. The distill model
   answers this per claim (prompts/distill.md's `relayed` field) and this
   module checks it against the evidence text, the same one-way way.

The five grades that fall out, strongest first:

- `controlled`     — paper, with numbers. A benchmark, a delta, an ablation.
- `field_measured` — a practitioner or lab reporting its own numbers.
- `asserted`       — a paper stating something it did not measure here.
- `anecdote`       — a field report with no measurement in it at all.
- `relayed`        — another work's result, as this source reports it.

## Why `relayed` outranks nothing, and why it is a grade rather than a flag
(2026-10-26, `INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`)

`skills/context-window-engineering` rested a shipped delta on one paper's
sentence about two other papers. The sentence was wrong about both: one runs no
random baseline at all, and the other's result agrees with the citing paper
rather than opposing it. Nothing in the pipeline looked for that, because the
evidence bar as written asks whether a finding is in a paper, and a citation is
a finding *about* another paper that enters the corpus on the citing paper's
authority with no check. Three sources that all cite one mischaracterisation
make a pattern that looks identical, from inside, to three independent results.

So `relayed` is last, below `anecdote`, and it is last whatever numbers the
evidence carries. The numbers in a relayed row are real numbers from a paper
nobody here has read, and the one thing this corpus can say about them is that
it has not checked them. A relayed claim is a reading-queue line, not a fact.

It is a grade and not a second boolean column for one reason: every reader of a
claim's support already reads this column. The digest ranks on it, the
reviewer panel's adversary reports it against a skill's citation list, and the
research seat's queries group by it. A flag beside the grade would have reached
none of them without a change in each. Nothing is lost by folding it in,
because the source class the grade usually carries stays derivable from the
paper id: `source_class(paper_id)` answers it at any time, for any row.

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
RELAYED = "relayed"

# strongest first; db/schema.sql's check constraint carries the same five
GRADES = (CONTROLLED, FIELD_MEASURED, ASSERTED, ANECDOTE, RELAYED)

PAPER_SOURCES = frozenset({"arxiv", "hf-daily"})

# any digit run: "38.2%", "7B", "three of four tasks" fails it, which is the
# intended direction — the guard is conservative on purpose
_NUMBER = re.compile(r"\d")

# The relay guard, as named patterns, because a guard that only returns a
# boolean cannot be reviewed by reading its output. Each one is an attribution
# to somebody other than the source, and the shape they share is an
# attribution phrase sitting next to a reporting verb. That pairing is the
# whole design: "we compare against Zhang et al." is this paper measuring
# another method and is first-hand, while "Zhang et al. report 38.2%" is this
# paper passing a number along. A bare name, a bare citation and a bare "prior
# work" therefore do not fire.
_SAYS = (r"(?:report|reports|reported|show|shows|showed|shown|find|finds|found"
         r"|claim|claims|claimed|conclude|concludes|concluded|argue|argues"
         r"|argued|state|states|stated|note|notes|noted|observe|observes"
         r"|observed|demonstrate|demonstrates|demonstrated|measure|measures"
         r"|measured)")
# How far an attribution and its verb may sit apart: inside one clause, so the
# span stops at a full stop or a semicolon rather than counting characters. The
# semicolon is there because "prior work used 8-bit; this paper measures 48.7%"
# pairs somebody else's noun with this paper's verb across a clause boundary,
# and that sentence is first-hand.
_NEAR = r"[^.!?;]{0,90}?"
RELAY_MARKERS = {
    "et-al-says": rf"\bet\s+al\.{_NEAR}\b{_SAYS}\b",
    "says-et-al": rf"\b{_SAYS}\b{_NEAR}\bet\s+al\.",
    "others-say": rf"\bothers?\b{_NEAR}\b{_SAYS}\b",
    "prior-work-says": (r"\b(?:prior|previous|earlier|related|other|existing)\s+"
                        rf"(?:work|works|study|studies|paper|papers|method|methods"
                        rf"|literature|result|results|evaluation|evaluations|"
                        rf"baseline|baselines)\b{_NEAR}\b{_SAYS}\b"),
    "as-reported-in": (r"\bas\s+(?:reported|shown|demonstrated|found|observed"
                       r"|noted|described)\s+(?:in|by)\b"),
    "according-to": r"\baccording\s+to\b",
    "reportedly": r"\breportedly\b",
    "cites": r"\bcit(?:es|ing|ed\s+by)\b",
    "in-the-literature": r"\bin\s+the\s+literature\b",
}
_RELAY = {name: re.compile(pattern, re.I) for name, pattern in RELAY_MARKERS.items()}


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


def relay_markers(evidence: str | None) -> list[str]:
    """The names of the relay patterns the evidence text matches, in order.

    A list rather than a boolean so a run log and a reviewer's finding can say
    which phrase fired. `RELAY_MARKERS` carries the patterns and the reasoning
    for the pairing they all share.
    """
    text = evidence or ""
    return [name for name, rx in _RELAY.items() if rx.search(text)]


def reads_relayed(evidence: str | None) -> bool:
    """True when the evidence text attributes its result to another work.

    The same shape as `has_measurement`: a guard on the model's own answer,
    checked against the text the model wrote, and one-directional. It can only
    make a claim `relayed`, never clear a claim the model already called
    relayed, because the model saw the whole paper and this function sees four
    sentences.

    `evidence` is the field it reads and the claim sentence is not, because
    prompts/distill.md puts the source's own support text there and requires a
    relayed claim to name the work it belongs to in it. One locus, which is
    where the measurement guard already looks.
    """
    return bool(relay_markers(evidence))


def as_bool(value) -> bool:
    """The model returns JSON, and JSON from a model is not always typed."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1"}
    return False


def grade(paper_id: str, evidence: str | None, measured,
          source: str | None = None, relayed=None) -> str:
    """The grade for one claim. See the module docstring for the five values.

    `relayed` is the model's answer to whose result the claim is about, and it
    is checked before anything else: a result this source only passes along is
    unchecked here whatever its venue and whatever numbers came with it.
    """
    if as_bool(relayed) or reads_relayed(evidence):
        return RELAYED
    is_measured = as_bool(measured) and has_measurement(evidence)
    if source_class(paper_id, source) == "paper":
        return CONTROLLED if is_measured else ASSERTED
    return FIELD_MEASURED if is_measured else ANECDOTE


def backfill_grade(paper_id: str, evidence: str | None,
                   source: str | None = None) -> str:
    """The grade for a claim distilled before the column existed.

    `grade` with the measurement signal taken from the evidence text alone,
    because the model's `measured` boolean was never stored and cannot be
    recovered. See the module docstring for what that costs: on the
    measurement question this is the permissive half of a two-signal test, so
    it can be one step generous and never one step harsh.

    The relay question runs on the text alone for the same reason, and it goes
    the other way: a backfilled row can come back `relayed` where the live
    grader, with the model's answer in hand, would have called it the paper's
    own. That is not a flaw in the pairing, it is the one direction worth
    being wrong in. A row graded `relayed` is read as a verification target
    and a row wrongly graded `controlled` is read as a fact, and this whole
    grade exists because the second one shipped. It also cannot cost an
    existing grade anything: `pipeline/backfill_grades.py` writes only
    `where evidence_grade is null`, so every row this answers had no answer.

    Deterministic, so running it twice on the same row gives the same answer,
    which is what makes the backfill idempotent.
    """
    return grade(paper_id, evidence, True, source)
