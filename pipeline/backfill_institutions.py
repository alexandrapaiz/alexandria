"""The field the digest wants most, filled from the paper's own front matter.

    modal run pipeline/backfill_institutions.py::count      # the dry run. Writes nothing.
    modal run pipeline/backfill_institutions.py::backfill   # then, and only then, write

`papers.institutions` is empty on 99.2% of rows, measured by the writer seat on
2026-09-19 and unchanged at the 2026-10-12 ceremony. Canon law 9 and the owner's
own fine-tuning both ask for institution-first attribution, because a reader
knows DeepMind and does not know the fourth author, so every issue falls back to
"a team led by <first author>" instead. That fallback is the weaker line and it
is the same line every time, which is why it reads as furniture by its third
use. This job is the fill.

## Why it reads the paper and not a metadata API

The obvious cheap source is Semantic Scholar's `authors.affiliations`, which the
press already queries for `citationCount` on the same quota. Measured live
against twenty real arXiv papers on 2026-10-13: S2 knew all twenty, and fifteen
carried at least one author affiliation, which looks like a 75% fill against
today's 0.8%.

It is not. S2's affiliations are the author's *profile* affiliation, not the
paper's, and they are present on one or two authors out of hundreds. So the
strongest string S2 offers for the DeepSeek-R1 paper is "Tsinghua University"
(2 of 198 authors), for the GPT-4o system card "University of Oxford" (1 of
416), for Constitutional AI "UC Berkeley" ahead of Anthropic, and for the
chain-of-thought paper "Inflection AI", which is where its first author works
now and not who paid for the work. Scored by hand against the paper's real lab,
the top S2 string was wrong on nine of those fifteen. A digest that says "a
team at Oxford" about an OpenAI system card is worse than one that says nothing,
because the empty field degrades to a weaker sentence and the wrong field
degrades to a false one.

So this job reads the only source that is right by construction: the
affiliations the authors themselves printed in the paper's header, from the same
arXiv HTML `pipeline/distill.py` already reads through `tools/read_paper.py`.
Coverage is lower and precision is the point. Measured against twelve real
arXiv pages on 2026-10-13, the three patterns below fill nine, and every one of
the nine is the paper's actual lab. The three it leaves empty it leaves empty on
purpose: two print only an author list in the header and one renders no author
block at all.

## What it writes, and what it refuses

Three patterns, in order, each tried only when the one before it found
nothing.

**A. `ltx_role_affiliation`**, LaTeXML's structured affiliation field. When a
paper has it, it is the author's own answer to this question.

**B. The numbered list**, for the papers whose LaTeX puts affiliations in the
author block as "1 DeepSeek-AI, 2 Tsinghua University, 3 Peking University".
Pattern B mines free text, so it is held to a stricter bar than A: a segment
is kept only if it carries a word from `INSTITUTION_WORDS`, and only if the
markers form an ascending run starting at 1, which is what separates a real
affiliation list from the superscript on an author's name.

**C. The organisation byline**, for the papers whose author *is* a lab.
`arxiv:2501.12948`'s whole author block is "DeepSeek-AI research@deepseek.com",
and the GPT-4o system card's is "OpenAI". It runs only on a header that names
no person anywhere, which is the paper's own way of saying its author is an
organisation, so a one-author paper's byline can never be read as a lab.

Both patterns then pass `accept()`, and what it refuses matters more than what
it keeps, because the structured field is routinely used for something else:

- A person list. `arxiv:2310.06825`, Mistral 7B, puts twenty author names in
  the affiliation field, and a row reading "institutions: Devendra Singh
  Chaplot, Diego de las Casas" is a visible defect in the issue.
- A footnote. `arxiv:2408.03314` has two affiliation spans holding "Equal
  advising" and "Work done during an internship at Google DeepMind", beside
  the real "UC Berkeley" and "Google DeepMind".
- A sentence, an email, a URL, or anything over `MAX_LEN` characters.

A refusal is printed and never written, and the dry run prints every one, so
the filter is reviewable by reading its output rather than by reading its code.
This is `pipeline/backfill_topics.py`'s rule in a second job: a repair that only
ever repairs is a repair nobody has to review twice.

## Idempotent, resumable, and free

It calls no model and is given no provider secret, so it cannot acquire a cost
by a later edit, and it cannot take a minute of the free tier away from distill,
which has 2,223 papers waiting for one. It writes only where `institutions` is
empty, so it can never overwrite what distill extracted. `papers
.institutions_checked_at` records every attempt, answered or not, so the second
run does not re-fetch the papers arXiv has no HTML for; `RECHECK_DAYS` lets them
come round again, because arXiv renders HTML for a paper weeks after it is
posted. A run killed halfway is resumed by running it again.
"""

from __future__ import annotations

import pathlib
import re

import modal

# Papers per run. The fetch is one HTTP request to arXiv per paper with
# `POLITE_SECONDS` between them, so this is the wall clock as much as the
# progress: 150 papers is about nine minutes of fetching.
MAX_PAPERS_PER_RUN = 150
POLITE_SECONDS = 3

# The dry run is the one a person waits on, so it looks at fewer papers by
# default. Pass `--limit` for more.
DRY_RUN_PAPERS = 40

# Rows per transaction, for the same reason backfill_topics has one: how much
# progress a killed run loses.
BATCH = 25

# A paper arXiv has no HTML for today may have HTML in a month, so an attempt
# expires rather than settling the question forever.
RECHECK_DAYS = 30

# `MAX_INSTITUTIONS` and `MAX_LEN` are the extractor's own and are re-exported
# below, beside the functions, so there is one definition of the shape this
# column holds rather than one per job.

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    # The one reader, the same file distill reads papers with. A backfill with
    # its own fetcher would be a second answer to "did we read this paper".
    .add_local_file("tools/read_paper.py", "/root/read_paper.py")
    # The extractor, which distill now runs too. One file, so a pattern added
    # for a paper this job refused is a pattern the live insert gains as well.
    .add_local_file("pipeline/institutions.py", "/root/institutions.py")
)

app = modal.App("alexandria-backfill-institutions", image=image)


def _import_sibling(name: str):
    """Import a module Modal dropped at /root, or that sits beside this file.

    distill.py's two-path trick, for the same reason: /root in the Modal image,
    and in a checkout either this directory or ../tools.
    """
    import importlib
    import sys

    here = pathlib.Path(__file__).resolve().parent
    for path in ("/root", str(here), str(here.parent / "tools")):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module(name)


def read_paper():
    """tools/read_paper.py, the one reader, shared with distill and the seats."""
    return _import_sibling("read_paper")


# ----------------------------------------------- the extractor, elsewhere

# `pipeline/institutions.py`, verbatim out of this file on 2026-10-15 and
# unchanged. It moved so `pipeline/distill.py` can call it at the moment it
# already holds the paper's HTML, which is the fix for the field being 99.2%
# empty on a path that was meant to fill it: the backfill below repairs the
# rows distill read before that, and stops being a standing job once it has.
#
# The names are re-exported rather than reached through a module handle
# because this file's own prose, its dry run and its 41 tests all name them
# directly, and a move is only reviewable as a move if nothing it moved
# changed shape on the way.
_extractor = _import_sibling("institutions")

MAX_INSTITUTIONS = _extractor.MAX_INSTITUTIONS
MAX_LEN = _extractor.MAX_LEN
accept = _extractor.accept
author_names = _extractor.author_names
from_affiliation_spans = _extractor.from_affiliation_spans
from_numbered_markers = _extractor.from_numbered_markers
from_organisation_byline = _extractor.from_organisation_byline
institutions_from_html = _extractor.institutions_from_html
looks_like_a_person_list = _extractor.looks_like_a_person_list
names_the_field = _extractor.names_the_field
_dedupe = _extractor._dedupe

# --------------------------------------------------------- the database side

# The attempt marker. Added here as well as in db/schema.sql so the job is
# self-sufficient: `add column if not exists` is idempotent, and a backfill
# that needs a separate `db_setup.py::apply_schema` first is a backfill whose
# second step somebody forgets.
ADD_COLUMN = ("alter table papers add column if not exists "
              "institutions_checked_at timestamptz")

DUE = """
    select p.id, p.title
    from papers p
    where p.id like 'arxiv:%%'
      and (p.institutions is null or cardinality(p.institutions) = 0)
      and (p.institutions_checked_at is null
           or p.institutions_checked_at < now() - make_interval(days => %s))
      -- Papers the product has actually read. The digest attributes the papers
      -- it prints and those are the ones with claims, so this is the slice
      -- where a filled field changes a sentence a reader sees. The rest of the
      -- table is 2,223 papers distill has not reached yet, and distill writes
      -- institutions itself when it gets there.
      and exists (select 1 from claims c where c.paper_id = p.id)
    order by p.published_at desc nulls last
    limit %s
"""


def _fetch_html(reader, paper_id: str, timeout: float = 30) -> str | None:
    """arXiv's HTML for one paper, raw, or None.

    Raw and not `reader.fetch_fulltext`, which strips the tags: the affiliation
    markup is the whole signal here and distill's cleaner is what removes it.

    One line, because the reader grew a public `fetch_html` on 2026-10-15 and
    this had been reaching through `reader._get`, `reader.ARXIV_HTML` and
    `reader.MIN_HTML_BYTES` to assemble its own. Three privates of one module
    copied into another is two answers to "what counts as an arXiv page",
    which is exactly what one reader exists to prevent.
    """
    return reader.fetch_html(paper_id, timeout=timeout)


def ensure_column(conn) -> None:
    """The attempt column, in its own transaction, committed before the walk.

    `alter table` holds an ACCESS EXCLUSIVE lock on `papers` until the
    transaction it runs in commits, and the walk below runs for minutes. Left
    inside the walk's transaction this would block ingest and distill for the
    length of the run, and the dry run would block them while writing nothing.
    So it commits here, in both passes: the statement is additive and
    idempotent, and it is the one thing the dry run does write.
    """
    conn.execute(ADD_COLUMN)
    conn.commit()


def walk(conn, *, limit: int, write: bool) -> dict:
    """One pass. `write=False` reads arXiv and writes no row."""
    import time

    reader = read_paper()
    ensure_column(conn)
    rows = conn.execute(DUE, (RECHECK_DAYS, limit)).fetchall()
    print(f"{len(rows)} papers with claims and no institutions")

    filled = 0
    by_pattern: dict[str, int] = {}
    refusals: list[str] = []
    for index, (pid, title) in enumerate(rows):
        html = _fetch_html(reader, pid)
        if html is None:
            print(f"  no HTML: {pid} {title[:48]}")
            by_pattern["no-html"] = by_pattern.get("no-html", 0) + 1
        else:
            found, refused, pattern = institutions_from_html(html)
            by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
            for item in refused:
                refusals.append(f"{pid}: {item[:90]}")
            if found:
                filled += 1
                print(f"  {pid}: {found}  [{pattern}] {title[:40]}")
                if write:
                    conn.execute(
                        "update papers set institutions = %s where id = %s",
                        (found, pid),
                    )
            else:
                print(f"  nothing in the header: {pid} {title[:44]}")
        if write:
            conn.execute(
                "update papers set institutions_checked_at = now() where id = %s",
                (pid,),
            )
            if index % BATCH == BATCH - 1:
                conn.commit()
        time.sleep(POLITE_SECONDS)
    if write:
        conn.commit()

    print(f"\nfilled: {filled} of {len(rows)}")
    for pattern, n in sorted(by_pattern.items(), key=lambda kv: -kv[1]):
        print(f"  {pattern}: {n}")
    if refusals:
        print(f"\nrefused, and written nowhere ({len(refusals)}). Every line here "
              "is a string that sat in a paper's affiliation field and is not an "
              "institution; a real one in this list is a bug in accept().")
        for line in refusals[:40]:
            print(f"  - {line}")
    if not write:
        print("\nthis was the dry run and nothing was written. "
              "modal run pipeline/backfill_institutions.py::backfill")
    return {"due": len(rows), "filled": filled, "patterns": by_pattern}


@app.function(secrets=[modal.Secret.from_name("neon")], timeout=1800)
def count(limit: int = DRY_RUN_PAPERS):
    """The dry run. Reads arXiv, writes nothing, prints what it would write."""
    import os

    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        total, empty = conn.execute(
            """
            select count(*),
                   count(*) filter (where institutions is null
                                      or cardinality(institutions) = 0)
            from papers
            """
        ).fetchone()
        share = f" ({100.0 * empty / total:.1f}%)" if total else ""
        print(f"papers: {total}, with no institutions: {empty}{share}")
        result = walk(conn, limit=limit, write=False)
        conn.rollback()
    return result


@app.function(secrets=[modal.Secret.from_name("neon")], timeout=1800)
def backfill(limit: int = MAX_PAPERS_PER_RUN):
    """The write pass. Fills only what is empty; never overwrites distill."""
    import os

    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        return walk(conn, limit=limit, write=True)
