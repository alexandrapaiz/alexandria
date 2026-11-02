"""Canon law 8's url, decided by `pipeline/arxiv_html.py` rather than by a model.

    pip install -r requirements-dev.txt && python3 -m pytest tests/test_law8_url.py -q

The rule says an arXiv link goes to `arxiv.org/html/<id>`, and to
`arxiv.org/abs/<id>` only when the paper has no HTML version. The question
inside it cannot be answered by reading the artifact, so for six wordings of
`prompts/digest.md` it was answered by the generator. The writer seat graded
2026-W42 against arXiv itself: nine of ten links were `abs`, and seven of
those nine had an HTML full text. Judgment went seven for nine.

The three assertions this file exists for, in the order they matter:

`test_an_unreachable_arxiv_is_not_the_fallback` is the one that is easy to
get wrong and silent when it is wrong. `html_full_text` has three outcomes,
and a caller that folds None into False publishes `abs` as though the paper
had been checked and found to have no HTML version.

`test_the_identifier_is_never_composed` is ban list 100. 2026-W42 carried six
bare identifiers against four versioned ones, which is one artifact
disagreeing with itself about a string that is meant to be copied. The
identifier here is read out of the url the payload already holds, so the
disagreement has no way in.

`test_the_modal_image_carries_this_module` is the merge-time check for the
hand list in `weekly.py`. The image names its files one by one, so a module
`weekly.py` imports and the image omits is an ImportError on the next cron
and nothing earlier.

No network. Every entry point takes its probe as an argument, and the fake
below answers from a dict so a wrong path shows up as a KeyError rather than
as a passing test of a mock.
"""

import pathlib
import sys
import urllib.error

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pipeline"))

import arxiv_html  # noqa: E402


@pytest.fixture(autouse=True)
def _no_cache_between_tests():
    """The process cache is correct in the press and wrong across tests."""
    arxiv_html._HTML_EXISTS.clear()
    yield
    arxiv_html._HTML_EXISTS.clear()


def fake_arxiv(answers):
    """A probe that knows exactly these identifiers and nothing else."""

    def probe(ident):
        return answers[ident]

    return probe


# --- the rule itself -------------------------------------------------------


def test_abs_becomes_html_when_arxiv_serves_the_full_text():
    url, reason = arxiv_html.law8_url(
        "https://arxiv.org/abs/2604.24594", probe=fake_arxiv({"2604.24594": True})
    )
    assert url == "https://arxiv.org/html/2604.24594"
    assert reason == arxiv_html.REWROTE


def test_abs_stands_when_the_paper_has_no_html_version():
    """2026-W42's two correct links. The rule's own fallback, earned."""
    url, reason = arxiv_html.law8_url(
        "https://arxiv.org/abs/2609.37312v1",
        probe=fake_arxiv({"2609.37312v1": False}),
    )
    assert url == "https://arxiv.org/abs/2609.37312v1"
    assert reason == arxiv_html.NO_HTML


def test_an_unreachable_arxiv_is_not_the_fallback():
    """None is a third outcome and it must not read as "no html version".

    The two reasons are different strings on purpose: the press log, and any
    gate reading the payload, has to be able to tell a paper that was asked
    about from one that was not.
    """
    url, reason = arxiv_html.law8_url(
        "https://arxiv.org/abs/2610.22344", probe=fake_arxiv({"2610.22344": None})
    )
    assert url == "https://arxiv.org/abs/2610.22344"
    assert reason == arxiv_html.UNREACHED
    assert reason != arxiv_html.NO_HTML


def test_the_identifier_is_never_composed():
    """Ban list 100: the version suffix is copied, never chosen.

    Both of these resolve to html, and the suffix each one came in with is the
    suffix it leaves with. Nothing in this module can produce a payload that
    names one paper two ways.
    """
    probe = fake_arxiv({"2610.22322": True, "2609.38981v1": True})
    bare, _ = arxiv_html.law8_url("https://arxiv.org/abs/2610.22322", probe=probe)
    versioned, _ = arxiv_html.law8_url(
        "https://arxiv.org/abs/2609.38981v1", probe=probe
    )
    assert bare == "https://arxiv.org/html/2610.22322"
    assert versioned == "https://arxiv.org/html/2609.38981v1"


@pytest.mark.parametrize(
    "url",
    [
        "https://arxiv.org/html/2604.01687",
        "https://arxiv.org/pdf/2604.01687",
    ],
)
def test_a_link_already_at_the_full_text_is_left_alone(url):
    """No probe is called, which the fake proves by having no answers in it."""
    out, reason = arxiv_html.law8_url(url, probe=fake_arxiv({}))
    assert out == url
    assert reason == arxiv_html.ALREADY


@pytest.mark.parametrize(
    "url",
    [
        "https://example.org/blog/a-post",
        "https://arxiv.org/list/cs.AI/recent",
        "not a url at all",
        None,
        "",
    ],
)
def test_anything_that_is_not_an_arxiv_abs_link_passes_through(url):
    out, reason = arxiv_html.law8_url(url, probe=fake_arxiv({}))
    assert out == url
    assert reason == arxiv_html.NOT_ARXIV


# --- the probe's three outcomes --------------------------------------------


def test_a_404_is_false_and_any_other_error_is_unknown():
    def raiser(exc):
        def opener(url):
            raise exc

        return opener

    gone = urllib.error.HTTPError("u", 404, "Not Found", None, None)
    assert arxiv_html.html_full_text("2604.00001", opener=raiser(gone)) is False
    arxiv_html._HTML_EXISTS.clear()
    broke = urllib.error.HTTPError("u", 503, "Unavailable", None, None)
    assert arxiv_html.html_full_text("2604.00001", opener=raiser(broke)) is None
    arxiv_html._HTML_EXISTS.clear()
    assert arxiv_html.html_full_text(
        "2604.00001", opener=raiser(urllib.error.URLError("down"))
    ) is None


def test_the_same_paper_is_asked_about_once():
    """A payload names one paper in several sections routinely."""
    calls = []

    def counting(url):
        calls.append(url)
        return True

    for _ in range(4):
        arxiv_html.html_full_text("2605.05726", opener=counting)
    assert len(calls) == 1
    assert calls[0] == "https://arxiv.org/html/2605.05726"


# --- the payload walk ------------------------------------------------------


def payload():
    """The shape `gather` returns, trimmed to the keys that hold links."""
    return {
        "stats": {"papers_ingested": 40},
        "new_claims": [
            {"claim": "a", "url": "https://arxiv.org/abs/2604.24594"},
            {"claim": "b", "url": "https://example.org/blog/post"},
        ],
        "superseded": [
            {
                "old_claim": "c",
                "old_url": "https://arxiv.org/abs/2606.03056",
                "new_claim": "d",
                "new_url": "https://arxiv.org/abs/2609.37312v1",
            }
        ],
        "traction": {
            "citation_movers": [
                {"paper": "e", "url": "https://arxiv.org/abs/2610.22344"}
            ],
        },
        "deep_reads": [{"paper": "f", "url": "https://arxiv.org/html/2605.05726"}],
    }


def test_every_section_is_reached_including_the_nested_one():
    """`traction` holds its rows two levels down and `superseded` has two urls.

    The walk is recursive rather than a list of section names because
    `deep_reads` and `traction` were both added to `gather` after law 8 was
    written. A section added tomorrow is covered the day it appears.
    """
    data = payload()
    counts = arxiv_html.resolve_payload(
        data,
        probe=fake_arxiv(
            {
                "2604.24594": True,
                "2606.03056": True,
                "2609.37312v1": False,
                "2610.22344": None,
            }
        ),
    )
    assert data["new_claims"][0]["url"] == "https://arxiv.org/html/2604.24594"
    assert data["superseded"][0]["old_url"] == "https://arxiv.org/html/2606.03056"
    assert data["superseded"][0]["new_url"] == "https://arxiv.org/abs/2609.37312v1"
    assert data["traction"]["citation_movers"][0]["url"] == (
        "https://arxiv.org/abs/2610.22344"
    )
    assert counts == {
        arxiv_html.REWROTE: 2,
        arxiv_html.NO_HTML: 1,
        arxiv_html.UNREACHED: 1,
        arxiv_html.ALREADY: 1,
        arxiv_html.NOT_ARXIV: 1,
    }


def test_the_reason_travels_beside_the_url():
    """The generator is handed the answer, so a reader can audit the decision."""
    data = payload()
    arxiv_html.resolve_payload(
        data,
        probe=fake_arxiv(
            {
                "2604.24594": True,
                "2606.03056": True,
                "2609.37312v1": False,
                "2610.22344": None,
            }
        ),
    )
    assert data["new_claims"][0]["url_law8"] == arxiv_html.REWROTE
    assert data["superseded"][0]["new_url_law8"] == arxiv_html.NO_HTML
    assert data["traction"]["citation_movers"][0]["url_law8"] == arxiv_html.UNREACHED


def test_a_second_pass_is_a_no_op():
    """`gather` runs once, but a rehearsal re-reads a payload it already has."""
    probe = fake_arxiv({"2604.24594": True, "2606.03056": True,
                        "2609.37312v1": False, "2610.22344": None})
    data = payload()
    arxiv_html.resolve_payload(data, probe=probe)
    first = data["new_claims"][0]["url"]
    arxiv_html.resolve_payload(data, probe=probe)
    assert data["new_claims"][0]["url"] == first
    assert data["new_claims"][0]["url_law8"] == arxiv_html.ALREADY


def test_the_summary_names_the_two_outcomes_that_need_a_reader_first():
    line = arxiv_html.summarise(
        {arxiv_html.ALREADY: 3, arxiv_html.UNREACHED: 1, arxiv_html.REWROTE: 7}
    )
    assert line.index(arxiv_html.REWROTE) < line.index(arxiv_html.UNREACHED)
    assert line.index(arxiv_html.UNREACHED) < line.index(arxiv_html.ALREADY)


def test_an_issue_with_no_links_still_logs_that_the_step_ran():
    assert "no links in payload" in arxiv_html.summarise({})


# --- the hand list in weekly.py -------------------------------------------


def test_the_modal_image_carries_this_module():
    """`weekly.py` imports this file at runtime and the image is a hand list.

    The failure this refuses is an ImportError on a Monday cron, which is
    `docs/agents/runtime-changes.md`'s whole subject: a change that is correct
    locally and absent from the container.
    """
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    assert 'add_local_file("pipeline/arxiv_html.py", "/root/arxiv_html.py")' in source


def test_gather_resolves_the_urls_before_it_returns_them():
    """The call site, asserted as text because `gather` needs a database.

    A unit test of `resolve_payload` passes whether or not anything calls it,
    and the defect that matters is the wiring rather than the function.
    """
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    body = source[source.index("def gather("):source.index("def arxiv_html(")]
    assert "resolve_payload(payload" in body
    assert body.index("payload = {") < body.index("resolve_payload(payload")
    assert body.rstrip().endswith("return payload")
