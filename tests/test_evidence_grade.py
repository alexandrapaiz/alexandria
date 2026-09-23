"""The evidence grade, as tests.

These encode the rule the digest will eventually rest on: a lab's blog post and
a paper's ablation table do not reach a reader as the same kind of sentence.
Run with `python3 tests/test_evidence_grade.py`.
"""

import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pipeline"))

# Stub modal so distill's non-Modal helpers can be imported without the SDK.
if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
    chain = types.SimpleNamespace()
    chain.pip_install = lambda *a, **k: chain
    chain.add_local_file = lambda *a, **k: chain
    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: chain)
    modal.Volume = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

import evidence
import pipeline.distill as distill

PAPER = "arxiv:2609.14079"
POST = "blog:cloudflare-engineering:0f1e2d3c4b5a6978"
NUMBERS = "Raises SWE-bench Verified from 41.2% to 48.7% across three seeds."
PROSE = "The authors' assertion, with no measurement given anywhere in the paper."


def test_the_four_grades():
    """The grid, in full: source class times whether a number is there."""
    assert evidence.grade(PAPER, NUMBERS, True) == "controlled"
    assert evidence.grade(PAPER, PROSE, False) == "asserted"
    assert evidence.grade(POST, NUMBERS, True) == "field_measured"
    assert evidence.grade(POST, PROSE, False) == "anecdote"


def test_hf_daily_picks_are_papers():
    """fetch_hf_daily writes arxiv: ids so a curated pick upgrades the row."""
    assert evidence.source_class("arxiv:2609.15906", "hf-daily") == "paper"
    assert evidence.source_class("arxiv:2609.15906", "arxiv") == "paper"


def test_source_is_the_fallback_when_the_id_is_not_arxiv_shaped():
    assert evidence.source_class("something-else", "arxiv") == "paper"
    assert evidence.source_class("something-else", "simonwillison") == "field"
    assert evidence.source_class("something-else", None) == "field"


def test_the_number_guard_downgrades_a_model_that_says_measured_without_one():
    """The whole point of checking: 'measured' has to survive its own evidence."""
    assert evidence.grade(PAPER, PROSE, True) == "asserted"
    assert evidence.grade(POST, PROSE, True) == "anecdote"


def test_the_number_guard_never_upgrades():
    """A number in the text is not a measurement the model vouched for."""
    assert evidence.grade(PAPER, NUMBERS, False) == "asserted"
    assert evidence.grade(POST, NUMBERS, False) == "anecdote"


def test_missing_and_empty_evidence_is_not_measured():
    assert evidence.grade(PAPER, None, True) == "asserted"
    assert evidence.grade(PAPER, "", True) == "asserted"


def test_json_from_a_model_is_not_always_typed():
    assert evidence.as_bool("true") and evidence.as_bool("TRUE") and evidence.as_bool("yes")
    assert evidence.as_bool(1) and evidence.as_bool(True)
    assert not evidence.as_bool("false")
    assert not evidence.as_bool("")
    assert not evidence.as_bool(None)
    assert not evidence.as_bool({"measured": True})
    assert evidence.grade(PAPER, NUMBERS, "true") == "controlled"
    assert evidence.grade(PAPER, NUMBERS, None) == "asserted"


def test_every_grade_is_one_the_database_accepts():
    """The check constraint in db/schema.sql and GRADES here are one list.

    They are written in two files and cannot be allowed to drift: a grade this
    module returns and the column rejects fails the insert, silently losing a
    day of claims.
    """
    schema = (ROOT / "db" / "schema.sql").read_text()
    match = re.search(
        r"claims_evidence_grade_check\s.*?evidence_grade in\s*\(([^)]*)\)",
        schema,
        re.S,
    )
    assert match, "the check constraint is gone from db/schema.sql"
    in_schema = set(re.findall(r"'([a-z_]+)'", match.group(1)))
    assert in_schema == set(evidence.GRADES), (in_schema, evidence.GRADES)


def test_distill_finds_the_grader_module_the_way_modal_will():
    """distill.evidence() must return this same module, not a copy of it."""
    assert distill.evidence().GRADES == evidence.GRADES


def test_distill_asks_the_database_whether_the_column_exists():
    """A deploy that lands before the schema run distills without grading."""

    class Conn:
        def __init__(self, answer):
            self.answer = answer
            self.sql = None

        def execute(self, sql, *args):
            self.sql = sql
            return types.SimpleNamespace(fetchone=lambda: self.answer)

    present, absent = Conn((1,)), Conn(None)
    assert distill.has_evidence_grade(present) is True
    assert distill.has_evidence_grade(absent) is False
    assert "information_schema.columns" in present.sql
    assert "evidence_grade" in present.sql


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"{len(tests)} passed")
