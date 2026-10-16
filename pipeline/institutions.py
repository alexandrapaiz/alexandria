"""The paper's own answer to "who did this work", parsed from its header.

Pure, import-free except `re`, and shared by the two jobs that need it:

- `pipeline/distill.py` calls it the moment it has the paper's HTML in hand,
  so a paper read today needs no backfill tomorrow.
- `pipeline/backfill_institutions.py` calls it over the rows distill read
  before this existed.

It lived in the backfill alone until 2026-10-15, which made it unreachable
from the job that fetches the markup in the first place: the backfill is a
Modal app file and importing it would have pulled `modal` into distill's
image for three regexes. The extractor is the half with no I/O in it, so it
moved here unchanged and the backfill's 41 tests still drive it from there.

## Three patterns, in order, each tried only when the one before found nothing

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

What it refuses matters more than what it keeps, and `accept()` is where that
lives. The long account of why precision beats coverage here, with the scores
against twenty real papers, stays in `pipeline/backfill_institutions.py`'s
docstring, because that is the job the measurement was taken for.
"""

from __future__ import annotations

import re

# distill writes `institutions` as up to three strings and pipeline/budget.py
# caps the field at 200 characters. Both numbers are matched here on purpose: a
# backfill that writes a shape the live insert would not write is a backfill
# that makes the column mean two things.
MAX_INSTITUTIONS = 3
MAX_LEN = 120

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
