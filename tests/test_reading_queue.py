#!/usr/bin/env python3
"""The reading queue reaches the pipeline, and the reader reads or says it did not.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

ADR-35 put reading in front of skill creation and left the queue it produces
(docs/research/reading-queue.md) with no reader on the machine side. These are
the tests for the two halves that close it: `pipeline/reading_queue.py`, which
turns unchecked lines into rows at the front of distill's drain, and
`tools/read_paper.py`, which is the one reader both the job and the seats use.

Nothing here touches the network or a database. The reader's single HTTP call
goes through `_get`, so these replace `_get`; `resolve` takes a connection and
a metadata function, so these hand it a fake of each. The fake connection is
deliberately dumb: it matches on the first word of the statement and records
everything, because what these tests care about is which statements were sent
and in what order, not that anyone reimplemented Postgres.
"""

import os
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
sys.path.insert(0, str(ROOT / "tools"))

import read_paper                                                # noqa: E402
import reading_queue as rq                                       # noqa: E402

QUEUE = """# Reading queue

Append-only, one line per item. Format: `- [ ] arxiv:<id> — why — asked by
skills/<slug> — YYYY-MM-DD`

- [ ] arxiv:2602.12670 — SkillsBench, the premise three read papers build on — asked by skills/skill-library-engineering — 2026-09-26
- [x] arxiv:2603.22455 — SkillRouter — asked by skills/skill-library-engineering — 2026-09-26 — read 2026-09-27 in #99
- [ ] arxiv:2608.04828v3 — Skill-Use, the 177-task benchmark — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2602.12670 — asked for twice, by a second skill — asked by skills/agent-evaluation — 2026-09-27

Questions the reading raised, for the research seat rather than a single paper.

- [ ] Does the trigger-rate collapse reproduce on alexandria's own skills? — asked by skills/skill-library-engineering — 2026-09-26
"""


# --- the parser -------------------------------------------------------------

def test_only_unchecked_lines_with_an_id_are_pending():
    ids = [i.paper_id for i in rq.pending(QUEUE, limit=None)]
    assert ids == ["arxiv:2602.12670", "arxiv:2608.04828"]


def test_a_struck_line_is_never_read_again():
    """The research seat strikes a line by checking the box. That is the whole
    protocol, so a checked line has to be invisible to the drain."""
    assert all(not i.checked for i in rq.pending(QUEUE, limit=None))
    assert "arxiv:2603.22455" in [i.paper_id for i in rq.parse(QUEUE)]


def test_a_question_line_is_not_a_paper():
    """The file's second half is questions for the research seat. They match the
    checklist shape and carry no id, and a fetcher must skip them silently."""
    assert len(rq.parse(QUEUE)) == 4  # four paper lines, the question not among them


def test_the_version_suffix_is_dropped_because_papers_keys_on_the_bare_id():
    assert rq.pending(QUEUE, limit=None)[1].paper_id == "arxiv:2608.04828"


def test_the_same_paper_asked_for_twice_is_one_fetch():
    pending = rq.pending(QUEUE, limit=None)
    assert [i.paper_id for i in pending].count("arxiv:2602.12670") == 1


def test_who_asked_is_carried_so_the_log_can_say_it():
    assert rq.pending(QUEUE, limit=None)[0].asked_by == "skills/skill-library-engineering"


def test_the_per_run_limit_holds():
    assert len(rq.pending(QUEUE, limit=1)) == 1


def test_a_missing_file_is_not_an_error():
    """Distill reads the queue from an image path that may not exist. Absent
    means distill the day's intake, never fail the run."""
    assert rq.read_file("/nonexistent/reading-queue.md") == ""


def test_the_real_queue_file_parses():
    """The format lives in the file's own header, and this is the test that the
    parser and the header have not drifted apart."""
    text = (ROOT / "docs" / "research" / "reading-queue.md").read_text()
    for item in rq.parse(text):
        assert item.paper_id.startswith("arxiv:")


# --- resolving a line into a row distill can distill -------------------------

class FakeCursor:
    def __init__(self, row):
        self._row = row

    def fetchone(self):
        return self._row


class FakeConn:
    """Enough of psycopg3 to answer one select and record the writes."""

    def __init__(self, papers=None):
        self.papers = papers or {}     # id -> (title, abstract, source, distilled_at)
        self.statements = []

    def execute(self, sql, params=()):
        self.statements.append((" ".join(sql.split()), params))
        if sql.strip().lower().startswith("select"):
            return FakeCursor(self.papers.get(params[0]))
        return FakeCursor(None)

    def commit(self):
        pass


def only(items):
    return rq.pending(QUEUE, limit=None)[:items]


def test_a_paper_the_corpus_holds_becomes_a_row_at_the_front(capsys):
    conn = FakeConn({"arxiv:2602.12670": ("SkillsBench", "an abstract", "arxiv", None)})
    rows = rq.resolve(conn, only(1), fetch_metadata=lambda pid: pytest.fail("no fetch needed"))
    assert rows == [("arxiv:2602.12670", "SkillsBench", "an abstract", "deep_read", "arxiv")]
    assert "reading-queue: arxiv:2602.12670 queued" in capsys.readouterr().out


def test_a_paper_the_corpus_has_never_seen_is_ingested_on_the_spot(capsys):
    conn = FakeConn()
    meta = {"id": "arxiv:2602.12670", "title": "SkillsBench", "abstract": "an abstract",
            "authors": ["A. Author"], "url": "https://arxiv.org/abs/2602.12670",
            "published_at": "2026-02-19"}
    rows = rq.resolve(conn, only(1), fetch_metadata=lambda pid: meta)
    assert rows == [("arxiv:2602.12670", "SkillsBench", "an abstract",
                     "deep_read", "reading-queue")]
    writes = [s for s, _ in conn.statements if s.lower().startswith("insert")]
    assert any("into papers" in w for w in writes)
    assert any("into triage_log" in w for w in writes)
    assert "ingested from arXiv" in capsys.readouterr().out


def test_the_ingested_paper_carries_its_provenance_not_the_firehoses():
    """`source = 'reading-queue'` is how anyone later answers "why is this paper
    in the corpus", and the triage row is why triage does not spend a model
    call on a paper that has already been distilled."""
    conn = FakeConn()
    rq.resolve(conn, only(1), fetch_metadata=lambda pid: {
        "title": "SkillsBench", "abstract": "a", "authors": [],
        "url": "https://arxiv.org/abs/2602.12670", "published_at": None})
    papers_insert = [s for s, _ in conn.statements if "into papers" in s][0]
    assert "'reading-queue'" in papers_insert
    triage_insert = [(s, p) for s, p in conn.statements if "into triage_log" in s][0]
    assert triage_insert[1][1] == rq.TRIAGE_MODEL
    assert "deep_read" in triage_insert[0]
    assert "skills/skill-library-engineering" in triage_insert[1][2]


def test_a_paper_already_distilled_is_reported_and_not_read_twice(capsys):
    """The skill seat may queue something the corpus read last month. Re-reading
    it would write every claim a second time; the answer is to tell the research
    seat it can strike the line."""
    conn = FakeConn({"arxiv:2602.12670": ("SkillsBench", "a", "arxiv", "2026-09-01")})
    assert rq.resolve(conn, only(1), fetch_metadata=lambda pid: None) == []
    assert "already read 2026-09-01" in capsys.readouterr().out


def test_an_id_arxiv_does_not_know_leaves_the_line_alone(capsys):
    conn = FakeConn()
    assert rq.resolve(conn, only(1), fetch_metadata=lambda pid: None) == []
    assert not [s for s, _ in conn.statements if s.lower().startswith("insert")]
    assert "unavailable at arXiv, left on the queue" in capsys.readouterr().out


def test_every_line_names_its_id_so_the_research_seat_can_strike_it(capsys):
    """The seat that strikes the line reads the run log. An id that never
    appears in it cannot be struck, and the queue silts up."""
    conn = FakeConn({"arxiv:2602.12670": ("SkillsBench", "a", "arxiv", None)})
    rq.resolve(conn, only(2), fetch_metadata=lambda pid: None)
    out = capsys.readouterr().out
    for item in only(2):
        assert item.paper_id in out


# --- the ordering, which is the whole point ---------------------------------

def row(pid, decision="distill"):
    return (pid, f"title {pid}", "abstract", decision, "arxiv")


def test_the_queue_comes_before_the_day_and_the_day_is_trimmed():
    first = [row("arxiv:2602.12670", "deep_read")]
    intake = [row(f"arxiv:2609.0000{n}") for n in range(5)]
    merged = rq.merge(first, intake, max_papers=3)
    assert [r[0] for r in merged][0] == "arxiv:2602.12670"
    assert len(merged) == 3


def test_a_paper_in_both_lists_is_distilled_once():
    first = [row("arxiv:2602.12670", "deep_read")]
    intake = [row("arxiv:2602.12670"), row("arxiv:2609.00001")]
    merged = rq.merge(first, intake, max_papers=10)
    assert [r[0] for r in merged] == ["arxiv:2602.12670", "arxiv:2609.00001"]


def test_a_queue_longer_than_the_cap_still_gets_read():
    """First means first. The bound on a runaway queue is MAX_PER_RUN, which is
    applied when the lines are chosen, not here."""
    first = [row(f"arxiv:260{n}.00001", "deep_read") for n in range(4)]
    merged = rq.merge(first, [row("arxiv:2609.00001")], max_papers=2)
    assert len(merged) == 4
    assert all(r[3] == "deep_read" for r in merged)


def test_no_queue_leaves_the_day_exactly_as_it_was():
    intake = [row(f"arxiv:2609.0000{n}") for n in range(3)]
    assert rq.merge([], intake, max_papers=30) == intake


# --- the reader --------------------------------------------------------------

HTML = "<html><head><style>p{}</style></head><body><p>Method &amp; results. " \
       + "We measured 71.3% on the held-out split. " * 200 + "</p></body></html>"

ABS_PAGE = '''<html><head>
<meta name="citation_title" content="SkillsBench: how well agent skills work" />
<meta name="citation_author" content="Author, A." />
<meta name="citation_date" content="2026/02/19" />
<meta name="citation_abstract" content="An ill-suited skill leaves the task worse off." />
</head><body>x</body></html>'''

ATOM = '''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>SkillsBench: how well agent skills work</title>
<summary>An ill-suited skill leaves the task worse off.</summary>
<published>2026-02-19T00:00:00Z</published>
<author><name>Author, A.</name></author>
</entry></feed>'''


@pytest.fixture
def responses(monkeypatch):
    """Route `_get` by URL, and record what was asked for."""
    asked = []
    table = {}

    def fake_get(url, timeout):
        asked.append(url)
        for fragment, answer in table.items():
            if fragment in url:
                return answer
        return (404, "")

    monkeypatch.setattr(read_paper, "_get", fake_get)
    return type("R", (), {"asked": asked, "table": table})()


@pytest.mark.parametrize("raw,expected", [
    ("2602.12670", "2602.12670"),
    ("arxiv:2602.12670", "2602.12670"),
    ("ARXIV:2602.12670v3", "2602.12670"),
    ("https://arxiv.org/abs/2602.12670", "2602.12670"),
    ("https://arxiv.org/pdf/2602.12670v2", "2602.12670"),
    ("cs.LG/9901001", "cs.LG/9901001"),
])
def test_every_shape_of_an_arxiv_id_normalizes(raw, expected):
    assert read_paper.normalize_id(raw) == expected


def test_something_that_is_not_an_id_says_so():
    with pytest.raises(ValueError):
        read_paper.normalize_id("the paper about skills")


def test_the_full_text_is_the_html_with_the_tags_taken_out(responses):
    responses.table["/html/"] = (200, HTML)
    text = read_paper.fetch_fulltext("arxiv:2602.12670")
    assert "<p>" not in text and "style" not in text
    assert text.startswith("Method & results.")


def test_the_caller_can_cut_it_and_the_cut_is_the_callers_business(responses):
    """distill passes FULLTEXT_CHARS because that is a provider limit. A seat
    passes nothing and gets the paper."""
    responses.table["/html/"] = (200, HTML)
    assert len(read_paper.fetch_fulltext("arxiv:2602.12670", max_chars=500)) == 500
    assert len(read_paper.fetch_fulltext("arxiv:2602.12670")) > 500


def test_no_html_version_is_not_an_error_it_is_the_fallback(responses):
    responses.table["/html/"] = (404, "")
    assert read_paper.fetch_fulltext("arxiv:1706.03762") is None


def test_a_stub_page_is_not_a_paper(responses):
    """arXiv answers 200 with a few hundred bytes for papers it has not
    rendered. Length is the only thing that tells them apart."""
    responses.table["/html/"] = (200, "<html><body>No HTML for this paper</body></html>")
    assert read_paper.fetch_fulltext("arxiv:1706.03762") is None


def test_a_blog_post_is_never_fetched_from_arxiv(responses):
    assert read_paper.fetch_fulltext("blog:import-ai:abc123") is None
    assert responses.asked == []


def test_metadata_comes_from_the_api_when_the_api_answers(responses):
    responses.table["/api/query"] = (200, ATOM)
    meta = read_paper.fetch_metadata("arxiv:2602.12670")
    assert meta["title"] == "SkillsBench: how well agent skills work"
    assert meta["published_at"] == "2026-02-19"
    assert meta["authors"] == ["Author, A."]
    assert meta["url"] == "https://arxiv.org/abs/2602.12670"


def test_metadata_falls_back_to_the_abs_page_when_the_api_refuses(responses):
    """On 2026-09-27 every form of the arXiv API answered 406 from the runner
    the seats run on, and the abs page answered 200 a second later. This is
    that fallback, and it is the reason the reader works in CI at all."""
    responses.table["/api/query"] = (406, "")
    responses.table["/abs/"] = (200, ABS_PAGE)
    meta = read_paper.fetch_metadata("2602.12670")
    assert meta["title"] == "SkillsBench: how well agent skills work"
    assert meta["abstract"] == "An ill-suited skill leaves the task worse off."
    assert meta["published_at"] == "2026-02-19"


def test_an_id_arxiv_does_not_have_yields_nothing(responses):
    responses.table["/api/query"] = (404, "")
    responses.table["/abs/"] = (404, "")
    assert read_paper.fetch_metadata("2999.99999") is None


def test_reading_says_full_text_when_it_got_the_paper(responses, tmp_path):
    responses.table["/html/"] = (200, HTML)
    responses.table["/abs/"] = (200, ABS_PAGE)
    paper = read_paper.read("2602.12670", cache_dir=str(tmp_path))
    assert paper["how"] == read_paper.FULL_TEXT
    assert paper["title"].startswith("SkillsBench")


def test_reading_says_abstract_only_when_that_is_all_there_was(responses, tmp_path):
    """The whole point of the exit code. A caller that gets this is looking at
    the thing the reading queue exists to record."""
    responses.table["/html/"] = (404, "")
    responses.table["/abs/"] = (200, ABS_PAGE)
    paper = read_paper.read("1706.03762", cache_dir=str(tmp_path))
    assert paper["how"] == read_paper.ABSTRACT_ONLY
    assert paper["text"] == "An ill-suited skill leaves the task worse off."


def test_reading_says_unavailable_and_caches_nothing(responses, tmp_path):
    """An outage must not be cached as a fact about the paper."""
    paper = read_paper.read("2999.99999", cache_dir=str(tmp_path))
    assert paper["how"] == read_paper.NOTHING
    assert list(tmp_path.iterdir()) == []


def test_the_second_ask_costs_no_fetch(responses, tmp_path):
    responses.table["/html/"] = (200, HTML)
    responses.table["/abs/"] = (200, ABS_PAGE)
    first = read_paper.read("2602.12670", cache_dir=str(tmp_path))
    responses.asked.clear()
    again = read_paper.read("arxiv:2602.12670v2", cache_dir=str(tmp_path))
    assert again["cached"] is True
    assert responses.asked == []
    assert again["text"] == first["text"]
    assert again["how"] == first["how"] and again["title"] == first["title"]


def test_refresh_fetches_again(responses, tmp_path):
    responses.table["/html/"] = (200, HTML)
    responses.table["/abs/"] = (200, ABS_PAGE)
    read_paper.read("2602.12670", cache_dir=str(tmp_path))
    responses.asked.clear()
    read_paper.read("2602.12670", cache_dir=str(tmp_path), refresh=True)
    assert responses.asked


@pytest.mark.parametrize("html,abs_page,code", [
    (HTML, ABS_PAGE, 0),
    ("", ABS_PAGE, 3),
    ("", "", 4),
])
def test_the_exit_code_is_the_answer_to_did_you_read_it(responses, tmp_path, capsys,
                                                        html, abs_page, code):
    """0 full text, 3 abstract only, 4 nothing, so a shell script can queue what
    it could not read without parsing a word of the output."""
    if html:
        responses.table["/html/"] = (200, html)
    if abs_page:
        responses.table["/abs/"] = (200, abs_page)
    assert read_paper.main(["2602.12670", "--cache-dir", str(tmp_path)]) == code


def test_the_header_says_how_much_there_is_not_how_much_was_printed(responses, tmp_path,
                                                                    capsys):
    """A truncated paper that reports its printed length reads as a short paper,
    and a seat deciding whether it has enough would be deciding on the wrong
    number."""
    responses.table["/html/"] = (200, HTML)
    responses.table["/abs/"] = (200, ABS_PAGE)
    read_paper.main(["2602.12670", "--max-chars", "200", "--cache-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert "# read: full-text (7,000 chars)" in out or "# printed: the first 200" in out
    assert "# printed: the first 200 chars" in out


def test_bare_prints_the_paper_and_nothing_else(responses, tmp_path, capsys):
    responses.table["/html/"] = (200, HTML)
    responses.table["/abs/"] = (200, ABS_PAGE)
    read_paper.main(["2602.12670", "--bare", "--quiet", "--cache-dir", str(tmp_path)])
    assert not capsys.readouterr().out.startswith("#")


# --- the wiring: distill uses both, and one reader exists rather than two -----

def test_distill_fetches_through_the_shared_reader(monkeypatch):
    """Two copies of the arXiv fetch is how one of them goes stale. distill
    keeps the cut to FULLTEXT_CHARS and nothing else."""
    sys.path.insert(0, str(ROOT / "tests"))
    import conftest                                              # noqa: F401
    import distill

    seen = {}

    def fake(paper_id, *, max_chars=None, timeout=30):
        seen["id"], seen["max_chars"] = paper_id, max_chars
        return {"text": "x" * (max_chars or 99), "html": "<html>"}

    monkeypatch.setattr(read_paper, "fetch_paper", fake)
    got = distill.fetch_paper("arxiv:2602.12670")
    assert seen == {"id": "arxiv:2602.12670", "max_chars": distill.FULLTEXT_CHARS}
    assert len(got["text"]) == distill.FULLTEXT_CHARS


def test_one_fetch_hands_back_the_text_and_the_markup(monkeypatch):
    """The fix for the field being 99.2% empty, at its narrowest.

    distill needs two things out of one arXiv page: the cleaned text a model
    reads, and the markup the affiliations are printed in, which `clean_html`
    deletes. Before 2026-10-15 the reader returned only the first, so the
    institution backfill fetched the same page a second time to read a header
    distill had already held. One `_get`, asserted by counting it.
    """
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return 200, (
            '<html><div class="ltx_authors">'
            '<span class="ltx_personname">A Person</span>'
            '<span class="ltx_role_affiliation">Google DeepMind</span>'
            '</div>' + "word " * 2000 + '</html>')

    monkeypatch.setattr(read_paper, "_get", fake_get)
    got = read_paper.fetch_paper("arxiv:2602.12670")
    assert len(calls) == 1, "one page, one fetch"
    assert "ltx_role_affiliation" in got["html"], "the markup survives"
    assert "<span" not in got["text"], "and the text is still cleaned"
    assert read_paper.fetch_fulltext("arxiv:2602.12670") == got["text"], \
        "the old entry point still answers exactly what it used to"
    assert len(calls) == 2, "the wrapper is a second fetch, which is why "\
        "distill calls fetch_paper and not this"


def test_a_page_too_thin_to_read_still_hands_back_its_header(monkeypatch):
    """The asymmetry in `fetch_paper`, which is deliberate and is a product
    decision: a landing page cleans down below MIN_TEXT_CHARS and the claims
    then come from the abstract, but the author block is still printed on it,
    so `institutions` can be filled for a paper that was never read in full.
    """
    # Over MIN_HTML_BYTES as a page and under MIN_TEXT_CHARS once cleaned,
    # which is what arXiv's "no HTML for this paper" rendering looks like:
    # all chrome and no body.
    stub = ('<html><div class="ltx_authors">'
            '<span class="ltx_role_affiliation">OpenAI</span></div>'
            + '<div class="ltx_page_content"></div>' * 300 + '</html>')
    assert len(stub) > read_paper.MIN_HTML_BYTES
    assert len(read_paper.clean_html(stub)) < read_paper.MIN_TEXT_CHARS
    monkeypatch.setattr(read_paper, "_get", lambda url, timeout: (200, stub))
    got = read_paper.fetch_paper("arxiv:2602.12670")
    assert got["text"] is None, "nothing a model should be asked to read"
    assert "OpenAI" in got["html"], "and a header a parser can still read"
    assert read_paper.fetch_fulltext("arxiv:2602.12670") is None


def test_no_page_at_all_is_none_rather_than_a_dict(monkeypatch):
    """None means arXiv has no HTML for this paper, which for anything before
    roughly 2024 is the common case and is not an error. The caller branches
    on the whole return, so an empty dict here would be a truthy nothing."""
    monkeypatch.setattr(read_paper, "_get", lambda url, timeout: (404, ""))
    assert read_paper.fetch_paper("arxiv:2602.12670") is None
    assert read_paper.fetch_html("arxiv:2602.12670") is None
    # A stub page arXiv serves for a paper with no HTML rendering.
    monkeypatch.setattr(read_paper, "_get", lambda url, timeout: (200, "no HTML"))
    assert read_paper.fetch_paper("arxiv:2602.12670") is None


def test_the_queue_file_and_the_reader_travel_with_the_job():
    """A job that reads a file has to carry it. The image build is where this
    is decided, and a missing `add_local_file` is a run that quietly drains
    only the intake."""
    source = (ROOT / "pipeline" / "distill.py").read_text()
    for path in ("tools/read_paper.py", "pipeline/reading_queue.py",
                 # The extractor, added 2026-10-15. A job that writes
                 # `institutions` from the markup and does not carry the
                 # parser fails at the import, every paper, after the model
                 # has already been paid for the call.
                 "pipeline/institutions.py",
                 "docs/research/reading-queue.md"):
        assert f'add_local_file("{path}"' in source


def test_distill_takes_the_queue_before_the_intake():
    """The order in the source, asserted, because the whole directive is an
    ordering and an ordering has no other test that does not need a database."""
    source = (ROOT / "pipeline" / "distill.py").read_text()
    body = source[source.index("def distill("):]
    assert body.index("queue.resolve(") < body.index("from distill_queue")


def test_there_is_one_cleaner_and_both_callers_use_it():
    """`tools/fulltext_density.py` measured the density of a cleaner it had
    copied, and the docstring claiming a test held the copy identical named a
    test file that does not exist. A receipt for the wrong cleaner is worse
    than no receipt. Both callers import `read_paper.clean_html` now."""
    density = (ROOT / "tools" / "fulltext_density.py").read_text()
    distill_source = (ROOT / "pipeline" / "distill.py").read_text()
    assert "read_paper.clean_html(raw)" in density
    assert "re.sub(r\"<[^>]+>\"" not in density
    assert "read_paper().fetch_paper(" in distill_source
    assert "re.sub(r\"<[^>]+>\"" not in distill_source


# --- who goes first: a blocked skill before a sourced one -------------------

ORDERED = """# Reading queue

- [ ] arxiv:2602.12670 — older, from a skill that already cites claims — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2603.22455 — also older, also sourced — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2609.08371 — newer, from a draft that cites nothing — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2509.22040 — the same draft's second request — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2604.17935 — a line nobody signed — 2026-09-28
"""

SOURCED = {"skills/skill-library-engineering"}


def test_without_the_sourced_set_the_order_is_exactly_what_it_always_was():
    """The default is unchanged, so no caller is surprised by this."""
    assert [i.paper_id for i in rq.pending(ORDERED, limit=None)] == [
        "arxiv:2602.12670", "arxiv:2603.22455", "arxiv:2609.08371",
        "arxiv:2509.22040", "arxiv:2604.17935"]


def test_a_skill_that_cites_no_claims_is_read_before_one_that_cites_plenty():
    """Owner directive 2026-10-05, item 3.

    47 pending lines, six a run, and the 2026-09-30 containment requests sat
    behind 27 older lines from skills that already carry claims. That put
    `skills/agent-containment` eight runs away while it was a draft with
    `claims: []` holding thirteen tests red. FIFO is right for a queue of
    equals and these were not equals.
    """
    got = [i.paper_id for i in rq.pending(ORDERED, limit=None, sourced=SOURCED)]
    assert got[:2] == ["arxiv:2609.08371", "arxiv:2509.22040"]
    assert got[2:] == ["arxiv:2602.12670", "arxiv:2603.22455", "arxiv:2604.17935"]


def test_file_order_still_decides_inside_each_group():
    """Only the grouping is new. Within a group the oldest line still wins."""
    got = [i.paper_id for i in rq.pending(ORDERED, limit=None, sourced=SOURCED)]
    assert got.index("arxiv:2609.08371") < got.index("arxiv:2509.22040")
    assert got.index("arxiv:2602.12670") < got.index("arxiv:2603.22455")


def test_the_per_run_limit_now_spends_itself_on_the_blocked_skill():
    assert [i.asked_by for i in rq.pending(ORDERED, limit=2, sourced=SOURCED)] \
        == ["skills/agent-containment", "skills/agent-containment"]


PROSE_ASKERS = """# Reading queue

- [ ] arxiv:2602.12670 — older, from a skill that already cites claims — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2609.40115 — RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2606.22504 — stop authority — asked by the research seat's L-R1 check — 2026-10-05
- [ ] arxiv:2609.08371 — from a draft that cites nothing — asked by skills/agent-containment — 2026-09-30
"""


def test_a_line_the_chair_signed_is_not_a_blocked_skills_request():
    """The defect this fixture is named for, and it had 46 lines on the real file.

    `ASKED_BY` takes one whitespace token, which is right for display and wrong
    for a decision. The chair signs lines "asked by the chair (owner: ...)" and
    the research seat signs them "asked by the research seat's L-R1 check", and
    both read as the token `the`. `the` is outside every `sourced` set, so the
    grouping read all of them as skills that cannot cite a claim and lifted them
    over the one skill that actually could not.

    The queue is the draft's only route out of citing nothing, so a phantom
    blocked group in front of it is the starvation the ordering was built to end,
    reintroduced by the parser three lines above the ordering.
    """
    got = rq.pending(PROSE_ASKERS, limit=None, sourced=SOURCED)
    assert [i.paper_id for i in got] == [
        "arxiv:2609.08371",     # the only line a blocked skill signed
        "arxiv:2602.12670", "arxiv:2609.40115", "arxiv:2606.22504",
    ], [(i.paper_id, i.asked_by, i.asking_skill) for i in got]


def test_the_asker_shown_is_the_text_and_the_asker_obeyed_is_the_slug():
    """Two fields because they answer two questions, and only one may order.

    `asked_by` is what the line says, so `resolve`'s log can name the chair. Any
    decision reads `asking_skill`, which is empty unless the line names a skill
    in the format the file's own header documents.
    """
    by_id = {i.paper_id: i for i in rq.parse(PROSE_ASKERS)}
    chair = by_id["arxiv:2609.40115"]
    # Was `"the"` until 2026-11-02, which is what this assertion said and what
    # the field actually held. A display field answering `the` to "who asked for
    # this" displays nothing, so the pattern now reads to the format's own
    # separator and this gate reads the asker the chair signed.
    assert chair.asked_by == "the chair (owner: make sure the corpus includes RLVR)"
    assert chair.asking_skill == ""
    skill = by_id["arxiv:2609.08371"]
    assert skill.asked_by == "skills/agent-containment"
    assert skill.asking_skill == "skills/agent-containment"


def test_the_cli_can_print_the_order_a_run_will_actually_use(tmp_path, capsys):
    """The observability half of the same defect, and the reason it lasted.

    `main` called `pending` with no `sourced`, so the only tool that reads this
    module's state printed file order while the cron used the grouped order. A
    reader could not see which group a line landed in, which is the one fact that
    went wrong. Default output is unchanged, because a flag that moves nobody's
    existing output is the cheap version of this.
    """
    queue = tmp_path / "q.md"
    queue.write_text(PROSE_ASKERS)
    (tmp_path / "skills" / "skill-library-engineering").mkdir(parents=True)
    (tmp_path / "skills" / "skill-library-engineering" / "SKILL.md").write_text(
        "---\nprovenance:\n  claims: [200]\n---\n")
    (tmp_path / "skills" / "agent-containment").mkdir(parents=True)
    (tmp_path / "skills" / "agent-containment" / "SKILL.md").write_text(
        "---\nprovenance:\n  claims: []\n---\n")

    assert rq.sourced_from_tree(tmp_path) == {"skills/skill-library-engineering"}

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        assert rq.main([str(queue), "--order"]) == 0
    finally:
        os.chdir(cwd)
    out, err = capsys.readouterr()
    lines = [l for l in out.splitlines() if l.strip()]
    assert lines[0].startswith("arxiv:2609.08371"), lines
    assert "\tblocked\tskills/agent-containment\tNEXT" in lines[0], lines[0]
    # The chair's line is in the batch because the fixture is short, and it must
    # say `waits` with no skill, which is the assertion that would have failed.
    chair = next(l for l in lines if l.startswith("arxiv:2609.40115"))
    assert "\twaits\t-\t" in chair, chair
    assert "stands in for `promotions`" in err


def test_no_line_on_the_live_file_names_a_skill_the_parser_cannot_read():
    """Against the real queue, because the fixture above cannot go stale and it can.

    This is the assertion that would have failed on 2026-10-05, the day the
    ordering shipped. It fails again if a seat invents a third way to sign a line
    that happens to start with `skills/` and does not parse.
    """
    text = rq.read_file(ROOT / rq.QUEUE_PATH)
    assert text, "the live queue is unreadable"
    bad = [i.raw[:90] for i in rq.parse(text)
           if i.asked_by.startswith("skills/") and not i.asking_skill]
    assert not bad, bad


def test_an_unsigned_line_is_not_treated_as_a_blocked_skills_request():
    """A line nobody signed is not evidence that a skill is stuck on it."""
    got = rq.pending(ORDERED, limit=None, sourced=SOURCED)
    assert got[-1].paper_id == "arxiv:2604.17935"


def test_no_skill_citing_claims_collapses_to_the_old_order():
    """The safe fallback, and the one a stale database produces.

    `sourced` comes from `promotions`, so an empty or unwritten table makes
    every line look blocked. That has to degrade to file order rather than to
    some other order nobody chose.
    """
    assert [i.paper_id for i in rq.pending(ORDERED, limit=None, sourced=set())] \
        == [i.paper_id for i in rq.pending(ORDERED, limit=None)]


def test_the_sourced_set_is_read_from_promotions_and_not_from_the_skills_tree():
    """`skills/` is not in distill's image and should not be.

    Baking the library into the reading job would make every skill edit need a
    distill redeploy.
    """
    class Rows(FakeConn):
        def execute(self, sql, params=()):
            self.statements.append((" ".join(sql.split()), params))
            cursor = FakeCursor(None)
            cursor.fetchall = lambda: [("skills/harness-engineering",)]
            return cursor

    got = rq.skills_with_claims(Rows())
    assert got == {"skills/harness-engineering"}


def test_a_database_that_cannot_answer_is_not_fatal():
    """A reading job that dies because `promotions` moved has lost the queue."""
    class Broken:
        def execute(self, *a, **k):
            raise RuntimeError("relation \"promotions\" does not exist")

    assert rq.skills_with_claims(Broken()) == set()


def test_the_live_queue_serves_a_blocked_skills_papers_on_the_next_run():
    """The verification the directive asked for, against the real file.

    This used to name `skills/agent-containment` and assert it was still a draft
    with `claims: []`. That made the test fail the moment the draft was fixed,
    which is the queue's own purpose being served: on 2026-10-06 the skill seat
    filled those claim ids in and this assertion went red on a library that had
    just got better. A test that forbids the outcome it was written to produce is
    a tripwire aimed at its own side.

    So the slug is gone and the rule is what is asserted. Whichever skill in the
    library cites no claims, its queue lines come first; and when every skill
    cites claims, the live file has nothing for the rule to promote and must
    degrade to file order rather than to some other order nobody chose. Both
    states are real, both are asserted, and neither is skipped.
    """
    import re

    text = rq.read_file(ROOT / rq.QUEUE_PATH)
    sourced, unsourced = set(), set()
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        cited = re.search(r"claims:\s*\[([^\]]*)\]", skill.read_text())
        slug = f"skills/{skill.parent.name}"
        (sourced if cited and cited.group(1).strip() else unsourced).add(slug)
    assert sourced, "no skill in the library cites a claim id, so `sourced` is empty"

    served = rq.pending(text, sourced=sourced)
    assert served, "the live queue is empty"
    before = rq.pending(text)

    asking = {i.asked_by.rstrip("/") for i in rq.parse(text)
              if not i.checked and i.asked_by} & unsourced
    if not asking:
        # Every skill with a line in the queue cites claims. The grouping has
        # nothing to lift, so it must change nothing at all.
        assert [i.paper_id for i in served] == [i.paper_id for i in before], (
            "no skill in the queue is blocked, so the order must be file order")
        return

    assert any(i.asked_by.rstrip("/") in asking for i in served), \
        [i.asked_by for i in served]
    # The thing that was actually broken: not one of their lines was reachable.
    assert not any(i.asked_by.rstrip("/") in asking for i in before), (
        "the old order already reached every blocked skill, so this test is no "
        "longer measuring the defect it was written for")


# --- the group is a function of the content, not of the line order ---------
#
# Measured by the research seat on 2026-11-02 and handed to this seat. `pending`
# deduplicated by id first, keeping whichever line came first in the file, and
# classified the survivor. So the signature deciding the group was the line a
# merge happened to put on top, and this file has two writers with a third
# proposed. Three priority members at positions one, two and three one way;
# zero members at eighty-eight, eighty-nine and ninety the other; identical
# content both times.

DUPLICATE_ASKERS = [
    "- [ ] arxiv:2602.12670 — the blocked draft's request — asked by skills/agent-containment — 2026-09-30",
    "- [ ] arxiv:2602.12670 — the same paper, a seat's request — asked by alexandria/research — 2026-11-02",
]

FILLER = [f"- [ ] arxiv:2401.{n:05d} — filler — asked by alexandria/research — 2026-11-02"
          for n in range(1, 88)]


def _both_orders(sourced):
    """The same eighty-nine lines, with the duplicate pair swapped, as two files.

    The pair sits after the filler rather than around it, which is the research
    seat's own fixture shape and the only one where position diverges as well as
    membership. With the pair straddling the file the paper is line one in both
    orders, so a position assertion passes on the defect by coincidence. That
    first draft of this fixture did exactly that.
    """
    first, second = DUPLICATE_ASKERS
    skill_first = "\n".join([*FILLER, first, second])
    research_first = "\n".join([*FILLER, second, first])
    return (rq.pending(skill_first, limit=None, sourced=sourced),
            rq.pending(research_first, limit=None, sourced=sourced))


def test_which_line_a_merge_put_on_top_no_longer_decides_the_group():
    """The defect, stated as the thing that must not happen again."""
    skill_first, research_first = _both_orders(set())
    members = lambda out: [i.paper_id for i in out if i.asking_skill]
    assert members(skill_first) == members(research_first) == ["arxiv:2602.12670"]


def test_the_served_order_is_identical_under_both_line_orders():
    """Not just membership. The position the paper is served at, too.

    Position is what the per-run limit spends itself on, so a paper that is in
    the right group at position eighty-eight is still eight runs away.
    """
    skill_first, research_first = _both_orders(set())
    at = lambda out: [n for n, i in enumerate(out, 1)
                      if i.paper_id == "arxiv:2602.12670"]
    assert [i.paper_id for i in skill_first] == [i.paper_id for i in research_first]
    # Ahead of the filler in both, rather than ahead in one and eighty-seven
    # lines behind in the other, which at six papers a run is fifteen runs.
    assert at(skill_first) == at(research_first) == [1]


def test_one_blocked_line_is_enough_because_one_fetch_serves_every_line():
    """Why ANY and not the first line.

    The two lines are one fetch, and the fetch unblocks the blocked asker
    whether its line is first or last. So a paper with one blocked asker among
    its lines belongs in the blocked group, and the line kept is the earliest
    of the ones that decided the group rather than the earliest overall.
    """
    skill_first, research_first = _both_orders(set())
    for out in (skill_first, research_first):
        kept = [i for i in out if i.paper_id == "arxiv:2602.12670"]
        assert len(kept) == 1, "still one fetch per paper"
        assert kept[0].asking_skill == "skills/agent-containment", \
            "the asker reported is the one the priority is owed to"


def test_the_ungrouped_default_is_still_file_order_under_both_orders():
    """`sourced=None` means no grouping, and that promise is order-blind too."""
    first, second = DUPLICATE_ASKERS
    a = rq.pending("\n".join([*FILLER, first, second]), limit=None)
    b = rq.pending("\n".join([*FILLER, second, first]), limit=None)
    assert [i.paper_id for i in a] == [i.paper_id for i in b]
    assert a[-1].paper_id == "arxiv:2602.12670"


def test_a_struck_duplicate_does_not_strike_the_line_still_asking():
    """Unchanged behaviour, asserted because the rewrite could have lost it.

    Striking one line is the research seat's business and it strikes that line.
    A second line still asking for the same paper is still pending, and the
    answer does not depend on which of the two came first.
    """
    done = "- [x] arxiv:2602.12670 — read — asked by alexandria/research — 2026-11-02"
    asking = DUPLICATE_ASKERS[0]
    for text in ("\n".join([done, asking]), "\n".join([asking, done])):
        out = rq.pending(text, limit=None, sourced=set())
        assert [i.paper_id for i in out] == ["arxiv:2602.12670"]
        assert out[0].asking_skill == "skills/agent-containment"


def test_the_live_queue_order_does_not_move_when_its_duplicates_are_reordered():
    """The claim on the real file, since the fixtures above are synthetic.

    Twelve ids sit on more than one unchecked line today. Swapping each pair in
    place must leave the served order identical.

    What this is computed over, because a gate that does not say so can pass on
    nothing: the count of repeated ids is asserted non-zero, and the count of
    pairs whose two lines fall in DIFFERENT groups is printed rather than
    asserted.

    **That second count was zero when this was written and it is eight now, and
    the sentence saying it was zero is why this test read as a watch rather
    than a live gate** (corrected 2026-11-09, engineer seat). The old wording
    said "no live duplicate is signed by a skill at all, so this is a watch on
    the live file rather than a reproduction of the defect". That stopped being
    true when the reading queue next grew, eight of the twelve pairs are now
    signed on one line and unsigned on the other, and this test went red on
    `main` reproducing the defect for real. The repair is in
    `pipeline/reading_queue.py`: the group's sort key was the served item's
    line, the served item is the earliest of the DECIDING lines rather than of
    the group, and a subset's position is what moves when the group's lines are
    permuted.

    So this is no longer a watch, and the number above is printed rather than
    asserted on purpose: it is a fact about the queue's content, which the
    research seat owns, and a gate that failed when the queue stopped having
    straddling pairs would be asserting on somebody else's file.
    """
    import collections

    text = rq.read_file(ROOT / rq.QUEUE_PATH)
    lines = text.splitlines()
    groups = collections.defaultdict(list)
    for item in rq.parse(text):
        if not item.checked:
            groups[item.paper_id].append(item)
    dups = {k: v for k, v in groups.items() if len(v) > 1}
    assert dups, "no id repeats on the live file, so this test measures nothing"

    swapped = list(lines)
    for group in dups.values():
        a, b = group[0].line_no - 1, group[-1].line_no - 1
        swapped[a], swapped[b] = swapped[b], swapped[a]
    sourced = rq.skills_with_claims(_NoDatabase())

    before = rq.pending(text, limit=None, sourced=sourced)
    after = rq.pending("\n".join(swapped), limit=None, sourced=sourced)
    assert [i.paper_id for i in before] == [i.paper_id for i in after]

    straddling = sum(1 for g in dups.values()
                     if len({bool(i.asking_skill and i.asking_skill not in sourced)
                             for i in g}) > 1)
    print(f"{len(dups)} repeated ids swapped, {straddling} straddling the groups")


class _NoDatabase:
    """A connection that cannot answer, so `sourced` is the empty set.

    `skills_with_claims` is specified to return nothing rather than raise when
    the database is unreachable, and the empty set is the strictest input for
    the grouping: every skill looks blocked.
    """

    def execute(self, *_a, **_k):
        raise RuntimeError("no database in this test")


# --- the append path, added 2026-11-02 --------------------------------------
#
# Why there is a writer at all. The research seat asked this seat on 2026-11-02
# to run `modal run pipeline/ingest.py --ids 2602.05366,2510.22670` for two
# papers nine and thirteen months old, which the ingest job's fourteen-day
# ceiling can never reach, and said in the same message that the credential for
# that command has been absent for eleven consecutive runs. This file is the
# other route to the same place: a scheduled job drains it, and writing to it
# needs no credential. What it did not have was a writer, so every request was
# a hand edit into 3,161 append-only lines whose own header asks the writer to
# grep first and whose format makes a wrong line invisible rather than broken.

SECTIONED = QUEUE + """
## Queued 2026-10-01 by skills/first

- [ ] arxiv:2601.11111 — the first section's line — asked by skills/first — 2026-10-01

## Queued 2026-10-02 by skills/second

- [ ] arxiv:2601.22222 — the last section's line — asked by skills/second — 2026-10-02
"""


def test_the_added_line_is_read_back_by_the_parser_that_decides_the_fetch():
    """The only check worth having: the writer validated by the reader.

    `parse` skips any line it cannot read, so a malformed request is not a
    broken request. It is a request that silently does not exist, which is the
    one failure this path is built to make impossible.
    """
    before = rq.pending(QUEUE, limit=None)
    after, line = rq.add(QUEUE, "2602.05366", "Multi-Field Tool Retrieval",
                         "the research seat", "2026-11-02")
    served = rq.pending(after, limit=None)
    assert len(served) == len(before) + 1, [i.paper_id for i in served]
    added = [i for i in served if i.paper_id == "arxiv:2602.05366"]
    assert len(added) == 1, [i.paper_id for i in served]
    assert added[0].checked is False
    # Was `"the"` with the comment "the display token, as documented". It was
    # documented, and the documentation was the defect: this is the gate on the
    # writer-checked-by-the-reader path, and it asserted that the asker the
    # caller passed arrives truncated. The whole asker now survives.
    assert added[0].asked_by == "the research seat"
    assert added[0].asking_skill == ""         # a seat is not a blocked skill
    assert line in after
    assert after.startswith(QUEUE.rstrip("\n"))   # append, never insert


def test_an_id_already_in_the_file_is_refused_with_every_line_it_is_on():
    """The file's own header rule, enforced instead of recorded.

    `INC-2026-10-27-a-paper-struck-as-read-was-requeued-as-the-highest-value-
    unread-paper-the-next-day`: a line landed 1,374 lines below a strike of the
    same id. Append-only is exactly the property that means a writer never has
    to read the file, so the rule asking them to grep is the rule most easily
    skipped.
    """
    with pytest.raises(ValueError) as struck:
        rq.add(QUEUE, "2603.22455", "already read", "me", "2026-11-02")
    assert "struck" in str(struck.value)
    with pytest.raises(ValueError) as open_line:
        rq.add(QUEUE, "2602.12670", "asked a third time", "me", "2026-11-02")
    # Both of the lines that carry it, not just the first. Counted on the
    # marker rather than on the word "line", which the explanatory half of the
    # message also uses.
    assert str(open_line.value).count("(open)") == 2, str(open_line.value)


def test_a_version_suffix_does_not_slip_past_the_duplicate_check():
    """`2608.04828` and `2608.04828v3` are one paper in `papers` and must be
    one line here. The queue's live file carries both spellings."""
    with pytest.raises(ValueError, match="already in this file"):
        rq.add(QUEUE, "2608.04828", "the bare id of a v3 line", "me", "2026-11-02")
    with pytest.raises(ValueError, match="already in this file"):
        rq.add(QUEUE, "arxiv:2608.04828v9", "a different version", "me", "2026-11-02")
    # And the version is dropped from what gets written, because `resolve`
    # looks the line up in `papers`, which is keyed on the bare id.
    _, line = rq.add(QUEUE, "arxiv:2510.22670v2", "under-documented tools",
                     "the research seat", "2026-11-02")
    assert "arxiv:2510.22670 " in line and "v2" not in line


def test_a_request_that_cannot_be_a_request_is_refused_and_not_written():
    for bad, why in (
        (dict(arxiv_id="notanid"), "not an arXiv id"),
        (dict(why="   "), "needs a reason"),
        (dict(asked_by=""), "needs an asker"),
        (dict(why="an em — dash in the reason"), "em dash"),
        (dict(asked_by="skills/x — and more"), "em dash"),
    ):
        kwargs = dict(arxiv_id="2602.05366", why="a reason", asked_by="me",
                      date="2026-11-02")
        kwargs.update(bad)
        with pytest.raises(ValueError, match=why):
            rq.add(QUEUE, **kwargs)


def test_an_awkward_reason_still_parses_back_as_one_request():
    """The reasons seats actually write, run through the writer and the reader.

    Queue lines in the live file carry colons, hyphens, quotes, parentheses,
    percentages and arXiv ids inside the reason. A separator chosen badly would
    make some of those unparseable, and the failure would be silent.
    """
    for why in ("a reason: with a colon",
                "a reason - with a hyphen",
                'a reason with "quotes" and (parens)',
                "60.6% to 67.9% exact match (+7.3)",
                "the baseline in arxiv:2608.04828 section 4.4",
                "a reason\twith a tab and   collapsed    spaces"):
        after, line = rq.add(QUEUE, "2602.05366", why, "the research seat",
                             "2026-11-02")
        read = rq.parse(line)
        assert len(read) == 1 and read[0].arxiv_id == "2602.05366", line
        assert rq.pending(after, limit=None)[-1].paper_id == "arxiv:2602.05366"


def test_an_id_in_the_reason_is_not_what_the_line_requests():
    """`ARXIV.search` takes the first id on the line, and the format puts the
    requested one first. A reason that cites another paper must not change what
    gets fetched, and queue lines cite other papers constantly."""
    _, line = rq.add(QUEUE, "2510.22670",
                     "the ablation arxiv:2602.05366 table 5 measures a weight on",
                     "the research seat", "2026-11-02")
    assert rq.parse(line)[0].paper_id == "arxiv:2510.22670"


def test_filing_under_an_earlier_section_is_refused_rather_than_inserted():
    """Two seats write this file and both of them append. Writing into the
    middle of it is how a concurrent append loses a line, so a named section
    that is not the last one is a refusal with its line number rather than a
    quiet append somewhere else."""
    with pytest.raises(ValueError, match="not the last heading"):
        rq.add(SECTIONED, "2602.05366", "a reason", "me", "2026-11-02",
               section="Queued 2026-10-01 by skills/first")


def test_the_last_section_is_reused_and_a_new_one_is_created():
    reused, line = rq.add(SECTIONED, "2602.05366", "a reason", "me",
                          "2026-11-02",
                          section="Queued 2026-10-02 by skills/second")
    assert reused.count("## Queued 2026-10-02 by skills/second") == 1
    assert reused.rstrip().endswith(line)
    fresh, line = rq.add(SECTIONED, "2602.05366", "a reason", "me",
                         "2026-11-02", section="Queued 2026-11-02 by me")
    assert "## Queued 2026-11-02 by me" in fresh
    assert fresh.index("## Queued 2026-11-02 by me") > \
        fresh.index("## Queued 2026-10-02 by skills/second")
    assert fresh.rstrip().endswith(line)


def test_the_cli_writes_nothing_on_a_dry_run_and_exits_2_on_a_refusal(tmp_path, capsys):
    path = tmp_path / "reading-queue.md"
    path.write_text(QUEUE)
    code = rq.main(["--add", "2602.05366", "--why", "a reason", "--asked-by",
                    "the research seat", "--file", str(path), "--dry-run"])
    out, err = capsys.readouterr()
    assert code == 0
    assert "arxiv:2602.05366" in out
    assert path.read_text() == QUEUE, "a dry run wrote to the file"

    code = rq.main(["--add", "2603.22455", "--why", "a reason", "--asked-by",
                    "me", "--file", str(path)])
    out, err = capsys.readouterr()
    assert code == 2, err
    assert "refused" in err and "struck" in err
    assert path.read_text() == QUEUE, "a refusal wrote to the file"


def test_the_cli_appends_once_and_says_what_the_route_needs(tmp_path, capsys):
    """The printed route is half of what this command is for.

    An appended line is not an ingested paper. The queue's content is baked
    into distill's image at deploy time, so the line reaches the cron on the
    next `modal deploy`. A command that wrote the line and said nothing would
    leave the caller believing the paper was on its way.
    """
    path = tmp_path / "reading-queue.md"
    path.write_text(QUEUE)
    before = len(rq.pending(QUEUE, limit=None))
    code = rq.main(["--add", "arxiv:2602.05366v1", "--why", "Multi-Field Tool "
                    "Retrieval, the only measured weights on this field",
                    "--asked-by", "the research seat", "--date", "2026-11-02",
                    "--file", str(path), "--section", "Queued 2026-11-02 by me"])
    out, err = capsys.readouterr()
    assert code == 0, err
    text = path.read_text()
    assert len(rq.pending(text, limit=None)) == before + 1
    assert "## Queued 2026-11-02 by me" in text
    assert "modal deploy" in err, err
    assert "tier b" in err, err
    assert str(before) in err and str(before + 1) in err


def test_the_live_file_is_still_writable_by_this_path():
    """The gates above all run against a fixture. This one asks the question
    about the file the pipeline actually reads, because that file is 3,161
    lines written by three seats and the fixture is fourteen."""
    text = rq.read_file(rq.QUEUE_PATH)
    assert text, rq.QUEUE_PATH
    after, line = rq.add(text, "2699.99999", "a probe that is never committed",
                         "the engineer seat", "2026-11-02")
    assert len(rq.pending(after, limit=None)) == len(rq.pending(text, limit=None)) + 1
    assert rq.parse(line)[0].paper_id == "arxiv:2699.99999"


# --- the asker guard, which could not fail until 2026-11-02 ------------------


def test_a_multi_word_asker_survives_the_write_whole():
    """The defect the research seat measured on the first outside use of `--add`.

    They queued a paper with `--asked-by "the research seat"`, and the line they
    got composed, passed every check `compose` makes, and read back as `the`. The
    reason is the shape of the check rather than the value: `compose` compared the
    parsed asker against `asked_by.split()[0]`, and the parser took one
    whitespace token, so both sides were the first word and the guard was an
    identity. It cost them nothing only because they read the parser before
    trusting the writer.
    """
    line = rq.compose("2606.01234", "a reason", "the research seat", "2026-11-02")
    assert rq.parse(line)[0].asked_by == "the research seat"


def test_the_asker_guard_can_refuse_a_line_whose_asker_does_not_survive():
    """The guard, pointed at a reader that truncates, which is what it is for.

    Reverting `ASKED_BY` to one whitespace token must make this raise. That is
    the whole claim: before this change the same monkeypatch left `compose`
    perfectly happy, because the thing it compared against was truncated by the
    same rule.
    """
    monkey = re.compile(r"asked by\s+(?P<who>\S+)")
    original = rq.ASKED_BY
    rq.ASKED_BY = monkey
    try:
        with pytest.raises(ValueError, match="reads back as"):
            rq.compose("2606.01234", "a reason", "the research seat", "2026-11-02")
    finally:
        rq.ASKED_BY = original


def test_the_asker_is_read_to_the_separator_and_not_past_it():
    """A widened pattern must stop at the field boundary or it swallows the date.

    This is the risk the widening carries, and it is the reason `compose` refuses
    an em dash inside either text field: the separator has to mean one thing.
    """
    line = rq.compose("2606.01234", "a reason", "the chair (owner: do the thing)",
                      "2026-11-02")
    item = rq.parse(line)[0]
    assert item.asked_by == "the chair (owner: do the thing)"
    assert "2026-11-02" not in item.asked_by


def test_every_asker_on_the_live_file_stops_at_the_separator():
    """The fixture is four lines; the file is 167 paper lines by three seats.

    A widened pattern is only safe if the em dash really terminates the field
    everywhere it has been written by hand, including on struck lines that carry
    a paragraph of answer after the date. Measured before shipping: 52 of 167
    lines changed, all 14 distinct values are askers, and none of them carries a
    date or a strike marker.
    """
    items = rq.parse(rq.read_file(rq.QUEUE_PATH))
    assert len(items) > 100, len(items)
    for item in items:
        assert "\u2014" not in item.asked_by, item.raw
        assert "~~" not in item.asked_by, item.raw
        assert not re.search(r"\d{4}-\d{2}-\d{2}", item.asked_by), item.raw
    recovered = [i for i in items if i.asked_by and not i.asking_skill]
    assert len(recovered) >= 50, len(recovered)
    assert all(i.asked_by != "the" for i in recovered)


def test_widening_the_display_field_moved_no_decision():
    """`asked_by` is display and `asking_skill` decides. Only one of them changed.

    The gate that matters for the blast radius: `pending`'s ordering reads
    `asking_skill`, which `SKILL_ASKER` supplies and this change did not touch,
    so the live file's grouping is byte-for-byte what it was.
    """
    items = rq.parse(rq.read_file(rq.QUEUE_PATH))
    for item in items:
        assert item.asking_skill in ("", item.asked_by) or item.asked_by.startswith(
            item.asking_skill), (item.asking_skill, item.asked_by)
        if item.asking_skill:
            assert item.asking_skill.startswith("skills/")


def test_a_trailing_comma_on_the_asker_is_normalised_the_same_on_both_sides():
    """`compose` checks the writer against the reader, so the two must agree.

    A check whose sides normalise differently fires on its own normalisation. One
    function does it for both, which is why this composes rather than raising.
    """
    line = rq.compose("2606.01234", "a reason", "the research seat,", "2026-11-02")
    assert rq.parse(line)[0].asked_by == "the research seat"
    assert rq.normalise_asker("  the   research  seat.  ") == "the research seat"


# --------------------------------------------------------------------------
# An id inside a sentence is not a request (engineer seat, 2026-11-09)
#
# Filed by the research seat, which measured the defect and declined to build
# it because its decision record puts pipeline code outside its whitelist. The
# cases below are the live lines it found, quoted rather than paraphrased, so
# the matcher turns on the real prose and not on a reconstruction of it.
# --------------------------------------------------------------------------

def test_a_struck_question_that_mentions_a_paper_does_not_request_it():
    """The shape the research seat found, and the reason the test is not
    "the match starts at zero".

    Every one of the nineteen live lines carries a strike, a bold or a backtick
    before the id, because a struck question is how this file retires a line.
    So position zero is the wrong test and these would all pass it.

    Each line below is quoted from `docs/research/reading-queue.md` rather than
    reconstructed, because the prose is what the matcher turns on. The first
    draft of this test invented a case the guard accepts on purpose, which is
    how the paragraph after the list got written.
    """
    lines = [
        # The id after a struck "question" marker, line 186.
        "- [x] ~~question — arxiv:2609.07103, Revisiting Complete Reasoning "
        "Traces for Post-Training, publishes no full HTML and was read at the "
        "abstract only~~",
        # A line that says in prose that there is no id, line 179.
        "- [x] ~~no arXiv id in the citing paper — SciWorld and BFCL-V3, the "
        "two benchmarks the feedback-enrichment result is measured on, cited by "
        "arxiv:2609.08404 without ids in the text~~",
        # A bolded title first, the id further along, line 670.
        "- [x] ~~**SandboxEscapeBench**, UK AI Safety Institute, reported "
        "published 2026-03, and reported in arxiv:2603.02277~~",
        # A backticked id inside a question, line 3455.
        "- [x] ~~question - Does `arXiv:2510.22670` report an effect SIZE for "
        "the when-to-use field, or only the keep-or-drop verdict?~~",
    ]
    for line in lines:
        assert rq.parse(line) == [], line


def test_an_emphasised_id_in_the_leading_position_is_still_a_request():
    """Where the guard deliberately stops, said out loud because it looks like
    a gap.

    `- [x] **arxiv:1234.5678 is the wrong paper**` is prose, and this guard
    reads it as a request. It cannot tell that case from an emphasised request
    without parsing English, and the file's documented format says an id in the
    leading position IS the request. No live line has that shape. If one ever
    does, the fix is the line and not the pattern, and this test is where the
    next reader finds that out instead of inferring a bug.
    """
    read = rq.parse("- [x] **arxiv:2603.02277 is the wrong paper for this**")
    assert len(read) == 1 and read[0].arxiv_id == "2603.02277"


def test_the_id_still_counts_through_the_emphasis_the_file_actually_uses():
    """The other half, and it is why the guard strips rather than anchors.

    A struck request is still a request that was made, and the duplicate check
    in `add` depends on seeing it. Dropping every emphasised line would trade
    this defect for its mirror image.
    """
    for body in ("arxiv:2602.12670", "~~arxiv:2602.12670~~",
                 "**arxiv:2602.12670**", "`arxiv:2602.12670`",
                 "  ~~ arxiv:2602.12670 ~~"):
        read = rq.parse(f"- [x] {body} — why — asked by the chair — 2026-11-02")
        assert len(read) == 1 and read[0].arxiv_id == "2602.12670", body


def test_the_five_papers_nobody_asked_for_can_be_queued_again():
    """What the guard buys, on the live file, and it is not a wasted slot.

    `pending` reads only unchecked lines and all nineteen are struck, so the
    served queue is unchanged by this guard. The reachable harm was in `add`:
    five of the nineteen carry an id that appears on no other line, so each one
    made `add` refuse a real request with "the paper is read and the answer is
    in the file", which was false about all five. Two of the five open with the
    literal words "no arXiv id".
    """
    text = rq.read_file(rq.QUEUE_PATH)
    for paper in ("2601.04748", "2407.18901", "2609.08404",
                  "2609.07103", "2603.02277"):
        assert rq.hits(text, paper) == [], (
            f"{paper} is still read as a request by some line in the live file")
        rq.add(text, paper, "a real request for this paper",
               "the engineer seat", "2026-11-09")


def test_a_paper_genuinely_struck_is_still_refused():
    """The guard must not become a way to re-queue a paper that was read.

    The control for the test above: it asserts five refusals went away, and on
    its own it cannot tell a narrowed guard from a deleted one.
    """
    text = rq.read_file(rq.QUEUE_PATH)
    struck = [i for i in rq.parse(text) if i.checked]
    assert struck, "no struck request on the live file, so this proves nothing"
    for item in struck[:5]:
        with pytest.raises(ValueError, match="already in this file"):
            rq.add(text, item.arxiv_id, "a reason",
                   "the engineer seat", "2026-11-09")


def test_the_guard_returns_a_value_in_band_when_it_does_nothing():
    """The control Ursa's ExO seat asked for, applied to this guard.

    Its refinement: ask what an instrument returns when it does nothing, and
    whether that value is inside the legal range of the real answer. A
    `REQUEST` pattern that could never match returns `[]` from `parse`, `[]`
    from `pending`, and a distill run that reads the day's intake and nothing
    from the queue. Every one of those is legal: an empty queue is the state
    this file is supposed to reach. So the silent failure is indistinguishable
    from success and needs a control, which is this test.

    It is deliberately a floor on the live file rather than an exact count, so
    that draining the queue does not fail it.
    """
    text = rq.read_file(rq.QUEUE_PATH)
    items = rq.parse(text)
    assert len(items) > 150, (
        f"the live queue parses {len(items)} requests; a guard that stopped "
        "matching would read as an empty queue and distill would be silent")
    assert rq.REQUEST.match("arxiv:2602.12670"), "the pattern matches nothing"
    assert sum(1 for i in items if not i.checked) > 50, (
        "no unchecked request survives the guard")
