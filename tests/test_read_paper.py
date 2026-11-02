"""The paper reader's fetch routes, and the header that says which one answered.

`tools/read_paper.py` is the one command every seat goes through to read a
paper, and until 2026-11-02 it had no test file at all. It also had one
full-text route. A 404 from `arxiv.org/html/<id>` meant exit 3, which is
correct for the tool, and two research runs wrote that exit code into
`docs/research/reading-queue.md` as "this paper publishes no full HTML". That
is a claim about arXiv rather than about one url: `arxiv:2609.07103` returned
404 there while the arXiv-run ar5iv mirror served 78,293 characters, all eight
tables and two appendices, and the queue line sat open on the wrong conclusion
for thirty-three days
(`INC-2026-11-02-a-paper-the-queue-called-unreadable-for-thirty-three-days-was-one-url-away`).

So the tests below are mostly about which route answered and what the output
says about it, in both directions.

A route that answers must not be skipped, and a route that answers must not be
misreported. The second half is the one the incident is really about: a header
whose `# source:` line names a url the body did not come from is the same wrong
claim the queue line made, written by the tool itself instead of by a seat. It
is checked on a first read, on a reprint from cache, and on the abstract
fallback.

The other direction matters just as much. `abstract-only` must stay reachable,
because a fallback chain that always finds something turns exit 3 into a code
nobody ever sees and the reading queue loses the signal it exists to record.
`test_no_route_answering_is_still_abstract_only` is that floor.

Nothing here touches the network: every test drives `_get` through a fake that
records the urls it was asked for, which is also how the route order is
asserted. One test is the live proof for the incident, and it is skipped unless
`READ_PAPER_LIVE=1` is set, because a test that needs two volunteer services to
be up is not a test the suite can be held to:

    READ_PAPER_LIVE=1 python3 -m pytest tests/test_read_paper.py -q

Run with `python3 -m pytest tests/test_read_paper.py -q`.
"""

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import read_paper as rp  # noqa: E402

PAPER = "2609.07103"
ARXIV_URL = f"https://arxiv.org/html/{PAPER}"
AR5IV_URL = f"https://ar5iv.labs.arxiv.org/html/{PAPER}"
ABS_URL = f"https://arxiv.org/abs/{PAPER}"

# Over MIN_HTML_BYTES and, cleaned, over MIN_TEXT_CHARS, so it reads as a paper.
BODY = "<html><body><span class='ltx_role_affiliation'>NAVER AI Lab</span>" \
       + ("the reasoning trace is kept whole. " * 400) + "</body></html>"

# The shape of the arXiv 404 page as served on 2026-11-02: 7,882 bytes, which
# is over MIN_HTML_BYTES, carrying 602 characters of text, which is under
# MIN_TEXT_CHARS. Nearly all of it is markup, which is why the byte floor
# passes it. The status code is what rejects it.
def _stub_page(total_bytes: int = 7882, text_chars: int = 602) -> str:
    """A 404 page's real proportions: mostly tags, a paragraph of apology."""
    head = "<html><head>"
    tail = "</head><body><p>" + ("No HTML is available for this submission. "
                                 * 15)[:text_chars] + "</p></body></html>"
    filler = '<meta name="citation_x" content="{}">'
    page = head + tail
    while len(page) < total_bytes:
        pad = min(total_bytes - len(page) - len(filler.format("")), 400)
        if pad <= 0:
            break
        page = head + filler.format("y" * pad) + page[len(head):]
    return page


STUB = _stub_page()

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><entry>
  <title>Revisiting Complete Reasoning Traces for Post-Training</title>
  <summary>Keeping both endpoints of a trace beats keeping the whole of it.</summary>
  <author><name>Jaehui Hwang</name></author>
  <published>2026-09-08T00:00:00Z</published>
</entry></feed>"""


class FakeGet:
    """A `_get` that answers from a url -> (status, body) table and records calls."""

    def __init__(self, table):
        self.table = table
        self.asked = []

    def __call__(self, url, timeout):
        self.asked.append(url)
        if url not in self.table:
            return 404, ""
        status, body = self.table[url]
        if isinstance(body, Exception):
            raise body
        return status, body


@pytest.fixture
def fake(monkeypatch):
    """Install a `_get` table; returns the installer so each test names its own."""
    def install(table):
        got = FakeGet(table)
        monkeypatch.setattr(rp, "_get", got)
        return got
    return install


# --------------------------------------------------- the routes, in order

def test_arxivs_own_html_is_tried_first_and_the_mirror_is_not_asked(fake):
    got = fake({ARXIV_URL: (200, BODY), AR5IV_URL: (200, "wrong")})
    body, source = rp.fetch_html_from(PAPER)
    assert source == ARXIV_URL
    assert body == BODY
    assert got.asked == [ARXIV_URL], "the mirror was asked for a paper arXiv served"


def test_a_404_on_arxivs_html_falls_through_to_the_mirror(fake):
    got = fake({ARXIV_URL: (404, STUB), AR5IV_URL: (200, BODY)})
    body, source = rp.fetch_html_from(PAPER)
    assert source == AR5IV_URL, "the mirror answered and the source does not say so"
    assert body == BODY
    assert got.asked == [ARXIV_URL, AR5IV_URL]


def test_the_404_body_is_over_the_byte_floor_so_the_status_is_what_rejects_it():
    """The premise of the fall-through, pinned as a number rather than a belief.

    The comment above `MIN_HTML_BYTES` used to call an arXiv stub "a few
    hundred bytes". The real one is 7,882. A fall-through that relied on the
    byte floor would not have fired at all.
    """
    assert len(STUB) == 7882, "the fixture no longer has the measured size"
    assert len(STUB) > rp.MIN_HTML_BYTES
    assert len(rp.clean_html(STUB)) < rp.MIN_TEXT_CHARS


def test_a_raising_route_does_not_stop_the_next_one(fake):
    got = fake({ARXIV_URL: (200, OSError("connection reset")), AR5IV_URL: (200, BODY)})
    body, source = rp.fetch_html_from(PAPER)
    assert source == AR5IV_URL
    assert got.asked == [ARXIV_URL, AR5IV_URL]


def test_no_route_answering_is_none_rather_than_an_empty_string(fake):
    fake({})
    assert rp.fetch_html_from(PAPER) is None
    assert rp.fetch_html(PAPER) is None


def test_a_blog_id_asks_no_route_at_all(fake):
    got = fake({ARXIV_URL: (200, BODY)})
    assert rp.fetch_html_from("blog:some-post") is None
    assert got.asked == []


def test_an_unparseable_id_asks_no_route_at_all(fake):
    got = fake({ARXIV_URL: (200, BODY)})
    assert rp.fetch_html_from("not-a-paper") is None
    assert got.asked == []


def test_every_route_is_a_formattable_template_with_the_arxiv_one_first():
    assert rp.HTML_ROUTES[0] is rp.ARXIV_HTML
    assert rp.AR5IV_HTML in rp.HTML_ROUTES
    for route in rp.HTML_ROUTES:
        assert route.format(id=PAPER).startswith("https://")
        assert PAPER in route.format(id=PAPER)


# ------------------------------------------- the source, through every layer

def test_fetch_paper_hands_the_answering_route_back_to_its_caller(fake):
    fake({ARXIV_URL: (404, STUB), AR5IV_URL: (200, BODY)})
    got = rp.fetch_paper(PAPER)
    assert got["source"] == AR5IV_URL
    assert got["text"] and got["html"] == BODY


def test_a_page_too_thin_to_read_still_reports_where_it_came_from(fake):
    """`text` is None and `html` is not, and the source belongs to the html."""
    fake({ARXIV_URL: (404, ""), AR5IV_URL: (200, STUB)})
    got = rp.fetch_paper(PAPER)
    assert got["text"] is None
    assert got["source"] == AR5IV_URL


def test_the_header_names_the_mirror_when_the_mirror_answered(fake, tmp_path):
    fake({ARXIV_URL: (404, STUB), AR5IV_URL: (200, BODY),
          rp.ARXIV_API.format(id=PAPER): (200, ATOM)})
    paper = rp.read(PAPER, cache_dir=str(tmp_path))
    assert paper["how"] == rp.FULL_TEXT
    assert paper["source"] == AR5IV_URL
    assert f"# source: {AR5IV_URL}" in Path(paper["path"]).read_text()


def test_the_header_names_arxiv_when_arxiv_answered(fake, tmp_path):
    fake({ARXIV_URL: (200, BODY), rp.ARXIV_API.format(id=PAPER): (200, ATOM)})
    paper = rp.read(PAPER, cache_dir=str(tmp_path))
    assert paper["source"] == ARXIV_URL
    assert f"# source: {ARXIV_URL}" in Path(paper["path"]).read_text()


def test_a_read_from_cache_keeps_the_route_the_first_read_recorded(fake, tmp_path):
    fake({ARXIV_URL: (404, STUB), AR5IV_URL: (200, BODY),
          rp.ARXIV_API.format(id=PAPER): (200, ATOM)})
    first = rp.read(PAPER, cache_dir=str(tmp_path))
    second = rp.read(PAPER, cache_dir=str(tmp_path))
    assert second["cached"] is True
    assert second["source"] == first["source"] == AR5IV_URL


def test_the_abstract_fallback_names_the_abs_page_and_not_a_html_route(fake, tmp_path):
    fake({rp.ARXIV_API.format(id=PAPER): (200, ATOM)})
    paper = rp.read(PAPER, cache_dir=str(tmp_path))
    assert paper["how"] == rp.ABSTRACT_ONLY
    assert paper["source"] == ABS_URL
    assert f"# source: {ABS_URL}" in Path(paper["path"]).read_text()


def test_render_without_a_source_still_names_the_first_route():
    """The default is the old behaviour, so an un-updated caller is not wrong,
    only less precise: it names the route that is right whenever route one won."""
    assert f"# source: {ARXIV_URL}" in rp._render(PAPER, rp.FULL_TEXT, "t", "body")
    assert f"# source: {ABS_URL}" in rp._render(PAPER, rp.ABSTRACT_ONLY, "t", "body")


# ------------------------------------------------------- the exit contract

def test_no_route_answering_is_still_abstract_only(fake, tmp_path):
    """The floor under the whole change.

    Adding routes must not make exit 3 unreachable. The reading queue's own
    signal is that code, and a chain that always finds something would delete
    it without changing a line of the queue's text.
    """
    fake({rp.ARXIV_API.format(id=PAPER): (200, ATOM)})
    paper = rp.read(PAPER, cache_dir=str(tmp_path))
    assert rp.EXIT[paper["how"]] == 3


def test_nothing_at_all_is_exit_four_and_caches_no_path(fake, tmp_path):
    fake({})
    paper = rp.read(PAPER, cache_dir=str(tmp_path))
    assert paper["how"] == rp.NOTHING
    assert rp.EXIT[paper["how"]] == 4
    assert paper["path"] == ""
    assert list(tmp_path.iterdir()) == []


def test_the_cli_exit_code_is_the_worst_of_the_ids_it_was_given(fake, tmp_path, capsys):
    other = "2602.10560"
    fake({ARXIV_URL: (404, STUB), AR5IV_URL: (200, BODY),
          rp.ARXIV_API.format(id=PAPER): (200, ATOM),
          rp.ARXIV_API.format(id=other): (200, ATOM)})
    code = rp.main([PAPER, other, "--cache-dir", str(tmp_path), "--quiet"])
    assert code == 3, "one full text and one abstract must report the abstract"
    assert f"# source: {AR5IV_URL}" in capsys.readouterr().out


# ------------------------------------------------------------- the live proof

@pytest.mark.skipif(
    not os.environ.get("READ_PAPER_LIVE"),
    reason="live fetch; set READ_PAPER_LIVE=1 to run it",
)
def test_live_the_paper_the_queue_called_unreadable_reads_whole():
    """The incident's own measurement, against the real services.

    Skipped unless asked for, because the suite runs without a network. Run it
    by hand when the route list changes:
    `READ_PAPER_LIVE=1 python3 -m pytest tests/test_read_paper.py -q`.
    """
    got = rp.fetch_paper(PAPER)
    assert got is not None
    assert got["source"] == AR5IV_URL, "arXiv's own html started serving this id"
    assert len(got["text"]) > 70000
    assert got["html"].count("ltx_role_affiliation") == 2, \
        "the mirror stopped carrying the spans pipeline/institutions.py reads"
