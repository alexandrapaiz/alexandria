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

import pathlib
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
        return "x" * (max_chars or 99)

    monkeypatch.setattr(read_paper, "fetch_fulltext", fake)
    body = distill.fetch_fulltext("arxiv:2602.12670")
    assert seen == {"id": "arxiv:2602.12670", "max_chars": distill.FULLTEXT_CHARS}
    assert len(body) == distill.FULLTEXT_CHARS


def test_the_queue_file_and_the_reader_travel_with_the_job():
    """A job that reads a file has to carry it. The image build is where this
    is decided, and a missing `add_local_file` is a run that quietly drains
    only the intake."""
    source = (ROOT / "pipeline" / "distill.py").read_text()
    for path in ("tools/read_paper.py", "pipeline/reading_queue.py",
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
    assert "read_paper().fetch_fulltext(" in distill_source
    assert "re.sub(r\"<[^>]+>\"" not in distill_source
