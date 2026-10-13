"""The institution backfill: what it writes, and the four things it refuses.

    pip install -r requirements-dev.txt && python3 -m pytest tests/ -q

`papers.institutions` is empty on 99.2% of rows and the digest's attribution
line depends on it (canon law 9). `pipeline/backfill_institutions.py` fills it
from the affiliations the authors printed in the paper's own header, and the
whole value of that choice is precision: an issue that says "a team at Oxford"
about an OpenAI system card is a worse artifact than one that says "a team led
by <first author>".

So this file is mostly a refusal suite, and it runs against verbatim slices of
four real arXiv pages under `tests/fixtures/arxiv-html/`, captured 2026-10-13,
rather than against markup written to pass. Three of the four are papers whose
affiliation field holds something that is not an affiliation, which is not an
edge case: it is what the field looks like in the wild.

Nothing here touches the network or a database. The two Modal entrypoints are
the thin half; `walk()` is driven against a fake connection so that what is
proved is the SQL's shape, the order of the writes, and that the dry run
writes nothing.
"""

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import backfill_institutions as bi                                # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "arxiv-html"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


# ------------------------------------------------- pattern A, the markup

def test_structured_affiliations_are_read_in_document_order():
    """arxiv:2404.19756 (KAN): two spans on the first author, one on the second."""
    found, _refused, pattern = bi.institutions_from_html(
        fixture("kan-affiliation-spans.html"))
    assert pattern == "affiliation-spans"
    assert found == [
        "Massachusetts Institute of Technology",
        "The NSF Institute for Artificial Intelligence and Fundamental Interactions",
        "California Institute of Technology",
    ]


def test_two_affiliations_in_one_span_are_two_institutions():
    """The KAN paper's first author carries both in a single contact block.

    An earlier draft matched the span with `<span.*?</span>` and read the two
    as one 90-character string. The nesting walk is what fixes it, and this is
    the assertion that would have caught it.
    """
    accepted, _ = bi.from_affiliation_spans(fixture("kan-affiliation-spans.html"))
    assert "Massachusetts Institute of Technology" in accepted
    assert not any("Affiliation" in value for value in accepted)


def test_a_bare_lab_name_with_no_institution_word_is_still_kept():
    """arxiv:2408.03314: "UC Berkeley" carries no word from INSTITUTION_WORDS.

    Pattern A does not apply that filter, and this is why. The markup has
    already said the string is an affiliation; requiring "university" or
    "institute" on top of that would drop the correct answer.
    """
    found, _refused, _ = bi.institutions_from_html(
        fixture("scaling-test-time-affiliation-spans.html"))
    assert found == ["UC Berkeley", "Google DeepMind"]


def test_footnotes_in_the_affiliation_field_are_refused():
    """The same paper's last author block holds two footnotes, not affiliations."""
    found, refused, _ = bi.institutions_from_html(
        fixture("scaling-test-time-affiliation-spans.html"))
    assert "Equal advising" not in found
    assert not any("internship" in value for value in found)
    refused_text = " | ".join(refused)
    assert "Equal advising" in refused_text
    assert "internship" in refused_text


def test_a_person_list_in_the_affiliation_field_is_refused():
    """arxiv:2310.06825 (Mistral 7B) puts the author list in the affiliation.

    Every span in that header holds names. The right answer is to write
    nothing, and the names have to appear in the refusals so the dry run can
    show a reader why a paper was skipped.
    """
    found, refused, pattern = bi.institutions_from_html(
        fixture("mistral-7b-affiliation-holds-a-person-list.html"))
    assert found == []
    assert pattern == "nothing"
    assert any("Chaplot" in value for value in refused)


# --------------------------------------- pattern B, the numbered list

def test_numbered_affiliations_are_read_when_there_is_no_markup():
    """arxiv:2402.03300 (DeepSeekMath): "1 DeepSeek-AI, 2 Tsinghua ...".

    No `ltx_role_affiliation` anywhere in this paper, and the author block
    prints the three affiliations as a numbered list. This is the pattern that
    takes the DeepSeek papers, which are the ones the corpus reads most.
    """
    found, _refused, pattern = bi.institutions_from_html(
        fixture("deepseekmath-numbered-markers.html"))
    assert pattern == "numbered-markers"
    assert found == ["DeepSeek-AI", "Tsinghua University", "Peking University"]


def test_the_email_block_after_the_last_affiliation_is_cut():
    """The third segment runs into `{zhihongshao,...}@deepseek.com`."""
    found, _, _ = bi.institutions_from_html(
        fixture("deepseekmath-numbered-markers.html"))
    assert all("@" not in value and "{" not in value for value in found)


def test_author_superscripts_do_not_become_institutions():
    """"Junxiao Song 1 Xiao Bi 1" is a marker followed by a capital, twice.

    Pattern B survives it two ways: the ascending run has to start at 1 and
    climb, and a segment has to carry an organisation word. Both were needed.
    """
    found, _, _ = bi.institutions_from_html(
        fixture("deepseekmath-numbered-markers.html"))
    assert not any("Xiao Bi" in value or "Song" in value for value in found)


def test_a_lone_marker_is_not_an_affiliation_list():
    """One marker is "1 Introduction". The run has to be at least two long."""
    accepted, refused = bi.from_numbered_markers(
        '<div class="ltx_authors">A. Author 1 Some University</div>'
        '<div class="ltx_abstract">x</div>')
    assert accepted == [] and refused == []


def test_pattern_b_requires_an_organisation_word():
    accepted, refused = bi.from_numbered_markers(
        '<div class="ltx_authors">Names here'
        ' 1 Reykjavik, 2 Something Else</div><div class="ltx_abstract">x</div>')
    assert accepted == []
    assert refused == ["Reykjavik", "Something Else"]


def test_pattern_b_runs_only_when_the_markup_found_nothing():
    """The KAN paper has both signals. The structured one wins."""
    _found, _refused, pattern = bi.institutions_from_html(
        fixture("kan-affiliation-spans.html"))
    assert pattern == "affiliation-spans"


# ------------------------------------- pattern C, the organisation byline

def test_a_lab_that_is_its_own_author_is_read_from_the_byline():
    """arxiv:2501.12948 (DeepSeek-R1): the whole byline is the lab and an email.

    No affiliation markup, no numbered list, and the three DeepSeek model
    papers in the corpus are all shaped this way, so pattern C is the one that
    reaches the papers this product reads most.
    """
    found, _refused, pattern = bi.institutions_from_html(
        fixture("deepseek-r1-organisation-byline.html"))
    assert pattern == "organisation-byline"
    assert found == ["DeepSeek-AI"]


def test_the_contact_email_is_removed_rather_than_cut_at():
    """"DeepSeek-AI research@deepseek.com" cut at the `@` is "DeepSeek-AI
    research", and the lab is not called that."""
    found, _, _ = bi.institutions_from_html(
        fixture("deepseek-r1-organisation-byline.html"))
    assert found == ["DeepSeek-AI"]


def test_two_organisation_bylines_are_two_institutions():
    """arxiv:2408.00118 (Gemma 2): "Gemma Team" and "Google DeepMind"."""
    found, _refused, pattern = bi.institutions_from_html(
        fixture("gemma-2-two-organisation-bylines.html"))
    assert pattern == "organisation-byline"
    assert found == ["Gemma Team", "Google DeepMind"]
    assert all("authfootnotemark" not in value for value in found)


def test_a_byline_of_author_names_is_refused_whole():
    """arxiv:2406.11931 (DeepSeek-Coder-V2) prints 40 names and no affiliation.

    This is the paper that says why pattern C needs its gate. Cut at the first
    footnote marker, its byline begins "Qihao Zhu", and a backfill that wrote
    that into `institutions` would have the digest attribute a DeepSeek paper
    to a person.
    """
    found, refused, pattern = bi.institutions_from_html(
        fixture("deepseek-coder-v2-byline-is-an-author-list.html"))
    assert found == []
    assert pattern == "nothing"
    assert refused == ["Qihao Zhu"]


def test_one_human_byline_refuses_the_whole_header():
    """A lab and ten people is ten author affiliations, not the paper's."""
    accepted, refused = bi.from_organisation_byline(
        '<div class="ltx_authors">'
        '<span class="ltx_personname">Google DeepMind</span>'
        '<span class="ltx_personname">Jane Doe</span>'
        '</div><div class="ltx_abstract">x</div>')
    assert accepted == []
    assert refused == ["Jane Doe"]


def test_a_single_human_author_is_left_empty():
    accepted, _refused = bi.from_organisation_byline(
        '<div class="ltx_authors"><span class="ltx_personname">Jane Doe</span>'
        '</div><div class="ltx_abstract">x</div>')
    assert accepted == []


def test_pattern_c_runs_only_when_the_first_two_found_nothing():
    """The scaling paper has four human bylines and real affiliation markup."""
    _found, _refused, pattern = bi.institutions_from_html(
        fixture("scaling-test-time-affiliation-spans.html"))
    assert pattern == "affiliation-spans"


# ------------------------------------------------------ accept(), directly

@pytest.mark.parametrize("candidate", [
    "",
    "MI",                                           # under three characters
    "x" * (bi.MAX_LEN + 1),                         # a paragraph
    "Equal contribution",
    "Work done while at Google",
    "zmliu@mit.edu",
    "https://github.com/deepseek-ai/DeepSeek-Math",
    "Devendra Singh Chaplot, Diego de las Casas, Florian Bressand",
])
def test_accept_refuses(candidate):
    assert bi.accept(candidate, require_institution_word=False) is None


@pytest.mark.parametrize("candidate,expected", [
    ("Affiliation: Google DeepMind", "Google DeepMind"),
    ("  Massachusetts Institute of Technology\n", "Massachusetts Institute of Technology"),
    ("1 DeepSeek-AI,", "DeepSeek-AI"),
    ("UC Berkeley", "UC Berkeley"),
    # Three commas, but it names a department and a university, so it is an
    # address and not a person list.
    ("Department of Physics, MIT, Cambridge, USA", "Department of Physics, MIT, Cambridge, USA"),
])
def test_accept_keeps_and_cleans(candidate, expected):
    assert bi.accept(candidate, require_institution_word=False) == expected


def test_the_write_is_capped_at_what_distill_writes():
    """distill takes `[:3]`. A backfill that writes four makes the column
    mean two different things depending on which job filled it."""
    assert bi.MAX_INSTITUTIONS == 3
    assert bi._dedupe([f"University {n}" for n in range(9)]) == [
        "University 0", "University 1", "University 2"]


def test_case_variant_spellings_collapse_to_the_first_one():
    """The Gemini 1.5 header prints "Google DeepMind" and "Google Deepmind"."""
    assert bi._dedupe(["Google DeepMind", "Google Deepmind", "google deepmind"]) \
        == ["Google DeepMind"]


# -------------------------------------------------------- walk(), on a fake

class FakeConn:
    """Enough psycopg to prove the SQL's shape and the order of the writes."""

    def __init__(self, due):
        self.due = due
        self.statements: list[tuple[str, tuple]] = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, sql, params=()):
        self.statements.append((" ".join(sql.split()), params))
        rows = self.due if "from papers p" in sql else []
        return _Result(rows)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class _Result:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


@pytest.fixture
def no_waiting(monkeypatch):
    monkeypatch.setattr(bi, "POLITE_SECONDS", 0)


@pytest.fixture
def one_paper(monkeypatch, no_waiting):
    monkeypatch.setattr(bi, "read_paper", lambda: object())
    monkeypatch.setattr(bi, "_fetch_html", lambda reader, pid, timeout=30:
                        fixture("kan-affiliation-spans.html"))
    return FakeConn([("arxiv:2404.19756", "KAN: Kolmogorov-Arnold Networks")])


def test_the_dry_run_writes_nothing(one_paper, capsys):
    result = bi.walk(one_paper, limit=10, write=False)
    assert result["filled"] == 1
    assert one_paper.commits == 0
    updates = [sql for sql, _ in one_paper.statements if sql.startswith("update")]
    assert updates == []
    assert "nothing was written" in capsys.readouterr().out


def test_the_write_pass_fills_and_marks_the_attempt(one_paper):
    bi.walk(one_paper, limit=10, write=True)
    updates = [(sql, params) for sql, params in one_paper.statements
               if sql.startswith("update papers")]
    assert updates[0][1][0] == [
        "Massachusetts Institute of Technology",
        "The NSF Institute for Artificial Intelligence and Fundamental Interactions",
        "California Institute of Technology",
    ]
    assert "institutions_checked_at = now()" in updates[1][0]
    assert one_paper.commits >= 1


def test_a_paper_with_no_html_is_still_marked_so_the_next_run_moves_on(
        monkeypatch, no_waiting):
    monkeypatch.setattr(bi, "read_paper", lambda: object())
    monkeypatch.setattr(bi, "_fetch_html", lambda reader, pid, timeout=30: None)
    conn = FakeConn([("arxiv:2212.08073", "Constitutional AI")])
    result = bi.walk(conn, limit=10, write=True)
    assert result["filled"] == 0
    marks = [sql for sql, _ in conn.statements
             if "institutions_checked_at = now()" in sql]
    assert len(marks) == 1


def test_only_empty_institutions_are_selected(one_paper):
    """The clause that makes this job unable to overwrite distill."""
    bi.walk(one_paper, limit=10, write=False)
    due = next(sql for sql, _ in one_paper.statements if "from papers p" in sql)
    assert "institutions is null or cardinality(p.institutions) = 0" in due
    assert "institutions_checked_at is null" in due
    assert "exists (select 1 from claims c where c.paper_id = p.id)" in due
    assert "p.id like 'arxiv:%%'" in due


def test_the_attempt_column_is_created_by_the_job_itself(one_paper):
    bi.walk(one_paper, limit=10, write=False)
    first = one_paper.statements[0][0]
    assert first == ("alter table papers add column if not exists "
                     "institutions_checked_at timestamptz")


def test_the_column_is_in_the_schema_too():
    """So `db_setup.py::apply_schema` and the job cannot disagree about it."""
    schema = (ROOT / "db" / "schema.sql").read_text()
    assert "institutions_checked_at" in schema


def test_the_job_is_given_no_provider_secret():
    """It calls no model, so it cannot acquire a cost by a later edit, and it
    cannot take a minute of the free tier from distill, which needs all of
    them. The assertion is on the source, because the decorator's argument is
    the only place this promise lives."""
    source = (ROOT / "pipeline" / "backfill_institutions.py").read_text()
    assert source.count('modal.Secret.from_name("neon")') == 2
    for provider in ("groq", "moonshot", "openai", "anthropic"):
        assert f'from_name("{provider}")' not in source
