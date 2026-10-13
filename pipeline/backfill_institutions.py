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

# Rows per transaction, for the same reason backfill_topics has one: how much
# progress a killed run loses.
BATCH = 25

# A paper arXiv has no HTML for today may have HTML in a month, so an attempt
# expires rather than settling the question forever.
RECHECK_DAYS = 30

# distill writes `institutions` as up to three strings and pipeline/budget.py
# caps the field at 200 characters. Both numbers are matched here on purpose: a
# backfill that writes a shape the live insert would not write is a backfill
# that makes the column mean two things.
MAX_INSTITUTIONS = 3
MAX_LEN = 120

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    # The one reader, the same file distill reads papers with. A backfill with
    # its own fetcher would be a second answer to "did we read this paper".
    .add_local_file("tools/read_paper.py", "/root/read_paper.py")
)

app = modal.App("alexandria-backfill-institutions", image=image)


def read_paper():
    """tools/read_paper.py, wherever this is running from.

    distill.py's two-path trick, for the same reason: /root in the Modal image
    and ../tools in a checkout.
    """
    import sys

    here = pathlib.Path(__file__).resolve().parent
    for path in ("/root", str(here.parent / "tools")):
        if path not in sys.path:
            sys.path.insert(0, path)
    import read_paper as module

    return module


# ----------------------------------------------------- the extractor, pure

# The label LaTeXML renders inside the affiliation span. It is not part of the
# answer, and on the KAN paper two affiliations arrive as two spans whose text
# both begin with it.
LABEL = re.compile(r"\s*Affiliation\s*:\s*", re.I)

TAGS = re.compile(r"<[^>]+>")
SPAN_OPEN = re.compile(r"<span\b", re.I)
SPAN_CLOSE = re.compile(r"</span\s*>", re.I)
AFFILIATION_CLASS = re.compile(r'class="[^"]*\bltx_role_affiliation\b[^"]*"', re.I)
AUTHORS_BLOCK = re.compile(r'class="[^"]*\bltx_authors\b[^"]*"', re.I)
ABSTRACT = re.compile(r'class="[^"]*\bltx_abstract\b[^"]*"', re.I)

# Pattern B's marker: a one- or two-digit affiliation number, at a word
# boundary, followed by a space and a capital. The lookahead is what keeps it
# off "Shao 1,2", where the digit is a superscript on a name.
MARKER = re.compile(r"(?:(?<=^)|(?<=[\s,;)]))(\d{1,2})\s+(?=[A-Z(])")

# Where an affiliation segment ends, besides the next marker: the
# corresponding-author email block, a URL, a footnote marker, a LaTeX macro
# LaTeXML could not render, or the start of a sentence addressed to the reader.
# Every alternative here was found in a real header.
SEGMENT_END = re.compile(
    r"[{@\\]|https?://|[∗*†‡]|\bNote:|\bthanks:|\bPlease\b|\bCorrespondence\b"
    r"|\bFull authorship\b")

# Pattern C's second bar. A single token carrying a capital after its first
# letter is a company's own spelling of itself: OpenAI, DeepMind, DeepSeek-AI.
# A person's name is not written that way, which is the distinction Pattern C
# needs and cannot get from INSTITUTION_WORDS alone.
CAMEL_TOKEN = re.compile(r"\b[A-Z][a-z]*[A-Z]\w*")

# An email address or a URL, removed before a segment is cut rather than cut
# at. "DeepSeek-AI research@deepseek.com" cut at the `@` leaves "DeepSeek-AI
# research", and the lab is not called that.
CONTACT = re.compile(r"\S+@\S+|https?://\S+|www\.\S+")

# Pattern B keeps a segment only if it carries one of these. The list is small
# and literal on purpose: it is not a taxonomy, it is the question "does this
# string name an organisation at all", and a tag that folds to nothing on it is
# printed rather than guessed at. Pattern A does not use it, because there the
# markup has already answered that question and the bar would cost real
# affiliations: "UC Berkeley" carries none of these words and is correct.
INSTITUTION_WORDS = frozenset("""
university universite universitat universidad universita college school
institute institut instituto laboratory laboratoire lab labs academy academia
research centre center college hospital foundation cnrs inria ai inc llc ltd
gmbh corporation corp company technologies technology polytechnique
department dept faculty division group team
""".split())

# A refusal list, not a taxonomy. Every phrase here was found in a real
# `ltx_role_affiliation` span, holding something that is not an affiliation.
FOOTNOTE_PHRASES = (
    "equal advising", "equal contribution", "equal contributions",
    "core contributor", "core contributors", "corresponding author",
    "work done", "work was done", "during an internship", "now at",
    "alphabetical order", "project lead", "these authors",
)

# Markers of a sentence rather than a name. `@` and `http` catch the contact
# block that sits in the same part of the header.
SENTENCE_MARKERS = ("@", "http", " and the ", " we ", " this paper ")


PERSONNAME = re.compile(r'<span[^>]*class="[^"]*\bltx_personname\b[^"]*"[^>]*>', re.I)


def author_names(html: str) -> set[str]:
    """The paper's own author names, from `ltx_personname`, normalised.

    The affiliation field holds a person's name often enough that this is the
    refusal that earns its keep: `arxiv:2310.06825`'s last author block holds
    "William El Sayed", one name, no commas and no organisation word, so every
    other rule here lets it through. The header already knows it is a name.
    """
    names: set[str] = set()
    for match in PERSONNAME.finditer(html):
        text = _span_text(html, html.rfind("<span", 0, match.end()))
        for piece in text.split(","):
            key = _key(piece)
            if key:
                names.add(key)
    return names


def _key(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _words(text: str) -> set[str]:
    return {w for w in re.split(r"[^a-z]+", text.lower()) if w}


def accept(candidate: str, *, require_institution_word: bool,
           names: set[str] | None = None) -> str | None:
    """One candidate string, cleaned, or None with the reason printed by callers.

    The caller prints refusals; this returns the cleaned string or nothing, so
    the rule is one function and both patterns are held to the same one.
    """
    text = " ".join(LABEL.sub(" ", candidate).split())
    text = text.strip(" ,;:.·-–—()[]{}<>*")
    text = re.sub(r"^\d{1,2}\s+", "", text)   # a marker that came along
    if len(text) < 3 or len(text) > MAX_LEN:
        return None
    low = text.lower()
    if any(phrase in low for phrase in FOOTNOTE_PHRASES):
        return None
    if any(marker in low for marker in SENTENCE_MARKERS):
        return None
    words = _words(text)
    # A person list. Two commas and no organisation word is the Mistral 7B
    # shape, and it is the refusal that matters most: that string would reach
    # the issue as an institution and read as a defect.
    if looks_like_a_person_list(text):
        return None
    if require_institution_word and not (words & INSTITUTION_WORDS):
        return None
    # A name the paper's own header prints as an author. Checked per comma
    # piece, so a list of three authors is refused by its first one.
    if names and any(_key(piece) in names for piece in text.split(",")):
        return None
    return text


def looks_like_a_person_list(text: str) -> bool:
    """Two commas and no organisation word: a list of authors, not a lab."""
    return text.count(",") >= 2 and not (_words(text) & INSTITUTION_WORDS)


def names_the_field(candidates: list[str]) -> bool:
    """Is this paper using its affiliation field for author names?

    A document-level question, and it has to be one. `arxiv:2310.06825` puts
    twenty author names in four affiliation spans, and the fourth holds a
    single name with no comma and no organisation word, so every per-string
    rule in `accept()` lets it through on its own. What gives it away is the
    company it keeps: three of that paper's four spans are plainly author
    lists, so the field means "more authors" in this paper and nothing read
    out of it is an institution.
    """
    return any(looks_like_a_person_list(c) for c in candidates)


def _span_text(html: str, open_at: int) -> str:
    """The text of the <span> starting at `open_at`, nested spans included.

    No parser, and no regex either: the affiliation span contains spans, and
    `<span.*?</span>` stops at the first inner close, which is how an earlier
    draft of this read two sibling affiliations as one string.
    """
    depth = 0
    i = open_at
    while i < len(html):
        nxt_open = SPAN_OPEN.search(html, i)
        nxt_close = SPAN_CLOSE.search(html, i)
        if nxt_close is None:
            break
        if nxt_open is not None and nxt_open.start() < nxt_close.start():
            depth += 1
            i = nxt_open.end()
            continue
        depth -= 1
        if depth == 0:
            inner = html[open_at:nxt_close.start()]
            return _plain(inner)
        i = nxt_close.end()
    return _plain(html[open_at:])


def _plain(fragment: str) -> str:
    import html as htmllib

    return " ".join(htmllib.unescape(TAGS.sub(" ", fragment)).split())


def _author_block(html: str) -> str:
    """The header text between the author block and the abstract, tags out.

    Pattern B reads this and nothing else. The body of a paper is full of
    numbered lists and the first section of many papers is "1 Introduction".
    """
    start = AUTHORS_BLOCK.search(html)
    if start is None:
        return ""
    end = ABSTRACT.search(html, start.end())
    # Back up to the `<` of the tag that carries the class, not to the class
    # attribute itself: cutting mid-tag leaves `<div ` in the text, and an
    # unterminated tag is not what the tag stripper removes.
    stop = html.rfind("<", 0, end.start()) if end else start.end() + 6000
    return _plain(html[start.end():stop])


def from_affiliation_spans(html: str) -> tuple[list[str], list[str]]:
    """Pattern A. (accepted, refused), in document order."""
    names = author_names(html)
    pieces: list[str] = []
    for match in AFFILIATION_CLASS.finditer(html):
        open_at = html.rfind("<span", 0, match.start())
        if open_at < 0:
            continue
        raw = _span_text(html, open_at)
        # One span can hold two affiliations when LaTeXML renders siblings
        # inside one contact block, and the label is the only separator.
        pieces.extend(piece for piece in re.split(r"Affiliation\s*:", raw, flags=re.I)
                      if piece.strip())

    tidied = [_tidy(piece) for piece in pieces]
    # The second bar, and it is per paper rather than per string. When the
    # field is being used for author names here, a candidate is kept only if it
    # says so itself by naming an organisation.
    strict = names_the_field(tidied)
    accepted: list[str] = []
    refused: list[str] = []
    for piece, tidy in zip(pieces, tidied):
        kept = accept(piece, require_institution_word=strict, names=names)
        (accepted if kept else refused).append(kept or tidy)
    return _dedupe(accepted), refused


def from_numbered_markers(html: str) -> tuple[list[str], list[str]]:
    """Pattern B. (accepted, refused), in marker order."""
    text = _author_block(html)
    names = author_names(html)
    marks = [(m.start(), m.end(), int(m.group(1))) for m in MARKER.finditer(text)]
    # The longest ascending run starting at 1. "Junxiao Song 1 Xiao Bi 1" gives
    # two runs of length one and the affiliation list gives 1, 2, 3.
    best: list[tuple[int, int, int]] = []
    run: list[tuple[int, int, int]] = []
    for mark in marks:
        if mark[2] == 1:
            run = [mark]
        elif run and mark[2] == run[-1][2] + 1:
            run.append(mark)
        else:
            run = []
        if len(run) > len(best):
            best = list(run)
    if len(best) < 2:
        return [], []
    accepted: list[str] = []
    refused: list[str] = []
    for index, (_, end, _number) in enumerate(best):
        stop = best[index + 1][0] if index + 1 < len(best) else len(text)
        segment = text[end:stop]
        cut = SEGMENT_END.search(segment)
        if cut:
            segment = segment[:cut.start()]
        kept = accept(segment, require_institution_word=True, names=names)
        (accepted if kept else refused).append(kept or _tidy(segment))
    return _dedupe(accepted), refused


def _tidy(refusal: str) -> str:
    """A refused string, printable. It is never written, only reported."""
    return " ".join(LABEL.sub(" ", refusal).split()).strip(" ,;:.")


def from_organisation_byline(html: str) -> tuple[list[str], list[str]]:
    """Pattern C. The papers whose author is an organisation. (accepted, refused).

    "DeepSeek-AI research@deepseek.com" is the entire byline of
    `arxiv:2501.12948`, `arxiv:2412.19437` and `arxiv:2405.04434`. "OpenAI" is
    the GPT-4o system card's, "Gemma Team Google DeepMind" is Gemma 2's, and
    "Gemini Team, Google" is Gemini 1.5's. None of the five carries LaTeXML
    affiliation markup or a numbered list, and all five print the institution
    in the one place a reader looks first.

The gate that makes it safe: *every* `ltx_personname` span in the header has
    to spell an organisation, by a word from `INSTITUTION_WORDS` or a capital
    inside a token, which is how a company writes its own name and not how
    anybody writes a human's. Gemma 2 has two bylines and both are labs. A
    paper with one lab and ten people has ten bylines that are people, and
    reading the lab out of that would be reading one author's employer as the
    paper's address. A single-author paper bylined "Jane Doe" fails too, which
    is the whole point of reading the paper rather than a metadata API.
    """
    bylines = []
    for match in PERSONNAME.finditer(html):
        open_at = html.rfind("<span", 0, match.end())
        if open_at >= 0:
            bylines.append(_span_text(html, open_at))
    if not bylines:
        return [], []
    accepted: list[str] = []
    for byline in bylines:
        text = CONTACT.sub(" ", byline)
        cut = SEGMENT_END.search(text)
        if cut:
            text = text[:cut.start()]
        candidate = accept(text, require_institution_word=False)
        if candidate is None or not (
                (_words(candidate) & INSTITUTION_WORDS) or CAMEL_TOKEN.search(candidate)):
            # One byline that is not an organisation refuses the whole header.
            # Gemma 2 has two, "Gemma Team" and "Google DeepMind", and both
            # are labs; a paper with one lab and ten people has ten bylines
            # that are people, and reading the lab out of it would be reading
            # one author's affiliation as the paper's.
            return [], [_tidy(candidate or text)]
        accepted.append(candidate)
    return _dedupe(accepted), []


def _dedupe(values: list[str]) -> list[str]:
    """Order preserved, case-insensitive duplicates collapsed, first spelling wins.

    "Google DeepMind" and "Google Deepmind" are one institution and the Gemini
    paper prints both. Capped at MAX_INSTITUTIONS, which is distill's own [:3].
    """
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        key = _key(value)
        if key and key not in seen:
            seen.add(key)
            out.append(value)
    return out[:MAX_INSTITUTIONS]


def institutions_from_html(html: str) -> tuple[list[str], list[str], str]:
    """(institutions, refused, which pattern answered) for one paper's HTML.

    Pattern B runs only when A found nothing, because A is the author's own
    structured answer and B is a reading of free text. A paper whose structured
    field holds only footnotes falls through to B, which is the right order:
    the refusal is not evidence that the header has no affiliations.
    """
    accepted, refused = from_affiliation_spans(html)
    if accepted:
        return accepted, refused, "affiliation-spans"
    numbered, refused_b = from_numbered_markers(html)
    if numbered:
        return numbered, refused + refused_b, "numbered-markers"
    byline, refused_c = from_organisation_byline(html)
    if byline:
        return byline, refused + refused_b + refused_c, "organisation-byline"
    return [], refused + refused_b + refused_c, "nothing"


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
    """
    try:
        arxiv_id = reader.normalize_id(paper_id)
    except ValueError:
        return None
    try:
        status, body = reader._get(reader.ARXIV_HTML.format(id=arxiv_id), timeout)
    except Exception as exc:
        print(f"  fetch failed for {paper_id}: {exc}")
        return None
    if status != 200 or len(body) < reader.MIN_HTML_BYTES:
        return None
    return body


def walk(conn, *, limit: int, write: bool) -> dict:
    """One pass. `write=False` is the dry run and touches nothing at all."""
    import time

    reader = read_paper()
    conn.execute(ADD_COLUMN)
    if write:
        conn.commit()
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
def count(limit: int = MAX_PAPERS_PER_RUN):
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
