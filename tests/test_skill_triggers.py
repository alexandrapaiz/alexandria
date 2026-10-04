"""The four staleness triggers, and the one line they must never write.

    python3 -m pytest tests/test_skill_triggers.py -q

`tools/skill_triggers.py`'s own docstring has named this file since it was
written: "tests/test_skill_triggers.py asserts that every line this module can
produce parses as zero papers to fetch". The file did not exist. The property
was real and checked, inside `--smoke`, which no workflow runs, so the sentence
pointed at a gate that was not where it said it was. That is the fifth sighting
of one pattern in a week (INC-2026-10-04-a-named-test-file-that-was-never-
written), and the cheapest answer to it is the file.

What is here and not in `--smoke`: the fetch property against the inputs that
make `paper_reference` fall back, the record the harness now writes read by the
module that reads it, and the comparisons that must *not* happen, which is the
half a demonstration never covers.

Nothing here touches a database, a model or the network.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import reading_queue                       # noqa: E402
import skill_eval as ev                    # noqa: E402
import skill_triggers as st                # noqa: E402

TODAY = "2026-10-04"
SKILL = "skills/harness-engineering"


# ------------------------------------------- the line that must never be a fetch

def every_record() -> list[dict]:
    """One record of every kind this module can produce, including the shapes
    that make `paper_reference` fall back to the paper id."""
    paper = {"claim_id": 200, "paper_id": "arxiv:2609.08572",
             "paper_title": "A paper the field found",
             "paper_url": "arxiv.org/abs/2609.08572",
             "citations_before": 4, "citations_now": 40,
             "checked_before": "2026-09-16", "checked_at": "2026-09-30"}
    # The fallback path: no url and no title, so the only name left for the
    # paper is its own id, which is the one string that must not survive.
    bare = dict(paper, paper_title="", paper_url="", claim_id=201)
    url_only = dict(paper, paper_title="", claim_id=202)
    edge = {"claim_id": 199, "refined_by": 421, "confidence": 0.82,
            "created_at": "2026-09-28", "claim": "the narrower form",
            "paper_id": "arxiv:2609.09134", "paper_title": "A newer paper",
            "paper_url": "arxiv.org/abs/2609.09134"}
    return [
        st.deprecated_record(SKILL, 85, "the older result"),
        st.refines_record(SKILL, 199, edge, "2026-09-15",
                          "provenance.extracted"),
        st.citations_record(SKILL, paper),
        st.citations_record(SKILL, bare),
        st.citations_record(SKILL, url_only),
        st.eval_record(SKILL, f"{SKILL}#eval-2026-09-29",
                       "its delta fell on arxiv:2609.09134's own numbers",
                       {"verdict": "no gain"}),
    ]


def test_no_line_asks_distill_to_fetch_a_paper_the_corpus_already_has():
    text = st.block(every_record(), TODAY)
    assert reading_queue.parse(text) == [], (
        "pipeline/reading_queue.py reads any arxiv:<id> in a queue line as a "
        "fetch request and front-loads distill's drain with it")


def test_the_fallback_name_for_a_paper_is_not_an_arxiv_id():
    """`paper_reference`'s last resort is the id, and it has to be defused."""
    bare = st.paper_reference({"paper_id": "arxiv:2609.08572"})
    assert "arxiv:" not in bare and "2609.08572" in bare
    assert reading_queue.parse(f"- [ ] {bare}") == []


def test_the_eval_record_cannot_smuggle_one_through_its_evidence():
    """The one record type whose evidence is written by a caller, not by this
    module. If a caller ever puts an id in it, this is the line that notices."""
    rec = st.eval_record(SKILL, f"{SKILL}#eval", "measured on arxiv:2609.09134",
                         {})
    assert reading_queue.parse(st.line(rec, TODAY)) == []


# ------------------------------------------------------- the record, as written

def test_the_reader_is_the_harness_s_own(tmp_path):
    """One format, one implementation. `tools/skill_eval.py` writes `history`
    and these three names are that file's, not a second copy of them."""
    assert st.history_entries is ev.history_entries
    assert st.summary_entry is ev.summary_entry
    assert st.ENTRY_FIELDS is ev.ENTRY_FIELDS


def test_a_single_measurement_is_never_compared_against_itself():
    """The bug the append-only record closes. With one slot per skill, the
    newest result was the only result, and the reader synthesised it into a
    one-entry history that `regression` then compared with itself."""
    one = [{"version": "2", "date": "2026-10-04", "subject_model": "kimi-k2.6",
            "verdict": "gain", "delta": {"mean": 0.05, "ci95": [0.01, 0.4]}}]
    assert st.regression(one, "kimi-k2.6") == ""
    assert st.eval_records(SKILL, {"history": one}, "kimi-k2.6") == []


def test_a_delta_that_fell_between_two_entries_is_a_finding():
    history = [
        {"version": "1", "date": "2026-09-20", "subject_model": "kimi-k2.6",
         "verdict": "gain", "delta": {"mean": 0.41, "ci95": [0.2, 0.6]}},
        {"version": "2", "date": "2026-09-29", "subject_model": "kimi-k2.6",
         "verdict": "gain", "delta": {"mean": 0.05, "ci95": [-0.1, 0.2]}},
    ]
    why = st.regression(history, "kimi-k2.6")
    assert "fell from +0.41 to +0.05" in why and "+0.20" in why
    records = st.eval_records(SKILL, {"history": history}, "kimi-k2.6")
    assert len(records) == 1 and records[0]["trigger"] == "eval"


def test_two_deltas_measured_on_different_models_are_not_compared():
    """A model rollout must never read as a regression, which is the same rule
    `skill_eval.gate_problems` keeps and the reason both read the subject."""
    history = [
        {"version": "1", "date": "2026-09-20", "subject_model": "kimi-k2.5",
         "verdict": "gain", "delta": {"mean": 0.41, "ci95": [0.2, 0.6]}},
        {"version": "2", "date": "2026-09-29", "subject_model": "kimi-k2.6",
         "verdict": "gain", "delta": {"mean": 0.05, "ci95": [-0.1, 0.2]}},
    ]
    assert st.regression(history, "kimi-k2.6") == ""
    records = st.eval_records(SKILL, {"history": history}, "kimi-k2.6")
    assert records == [], "one measurement on this model is not a comparison"


def test_a_subject_that_moved_asks_for_a_re_run_and_never_a_retirement():
    history = [{"version": "2", "date": "2026-09-29",
                "subject_model": "kimi-k2.6", "verdict": "gain",
                "delta": {"mean": 0.41, "ci95": [0.2, 0.6]}}]
    records = st.eval_records(SKILL, {"history": history}, "kimi-k3")
    assert len(records) == 1, "one dispatch asks for one re-run, not two"
    assert "Re-run the eval on the new subject" in records[0]["evidence"]
    assert "retire" not in records[0]["evidence"]


def test_an_unmeasured_skill_is_not_this_trigger_s_finding():
    assert st.eval_records(SKILL, {}, "kimi-k2.6") == []


# ------------------------------------------------------------- the version date

class Row:
    def __init__(self, version="2", extracted="2026-09-12"):
        self.version = version
        self.extracted = extracted
        self.path = SKILL


def write_result(tmp_path: pathlib.Path, doc) -> pathlib.Path:
    import json

    evals = tmp_path / "evals"
    evals.mkdir(parents=True, exist_ok=True)
    (evals / "results.json").write_text(json.dumps(doc))
    return tmp_path


def test_the_version_date_is_the_day_that_version_was_measured(tmp_path):
    doc = {"history": [
        {"version": "1", "date": "2026-09-20", "subject_model": "kimi-k2.6",
         "verdict": "gain", "delta": {"mean": 0.4, "ci95": [0.2, 0.6]}},
        {"version": "2", "date": "2026-09-29", "subject_model": "kimi-k2.6",
         "verdict": "gain", "delta": {"mean": 0.5, "ci95": [0.3, 0.7]}},
    ]}
    date, why = st.version_date(write_result(tmp_path, doc), Row(version="2"))
    assert (date, why) == ("2026-09-29", "the date this version was measured")
    # The version on the page, not the newest row: an entry for a later version
    # must not date an earlier one.
    date, why = st.version_date(write_result(tmp_path, doc), Row(version="1"))
    assert date == "2026-09-20"


def test_a_version_with_no_entry_falls_back_to_the_extraction_date(tmp_path):
    doc = {"history": [{"version": "1", "date": "2026-09-20",
                        "subject_model": "kimi-k2.6", "verdict": "gain",
                        "delta": {"mean": 0.4, "ci95": [0.2, 0.6]}}]}
    date, why = st.version_date(write_result(tmp_path, doc), Row(version="3"))
    assert (date, why) == ("2026-09-12", "provenance.extracted")


def test_no_date_anywhere_is_empty_rather_than_the_epoch(tmp_path):
    date, why = st.version_date(write_result(tmp_path, {}),
                                Row(version="3", extracted=""))
    assert (date, why) == ("", ""), (
        "defaulting to the epoch would fire trigger 2 on every edge the graph "
        "has ever held"
    )


def test_a_corrupt_result_file_is_not_a_crash(tmp_path):
    evals = tmp_path / "evals"
    evals.mkdir(parents=True)
    (evals / "results.json").write_text("{this was a measurement once")
    assert st.read_results(tmp_path) == {}
    assert st.version_date(tmp_path, Row())[1] == "provenance.extracted"


# -------------------------------------------------------------- the dedupe key

def test_the_key_is_in_the_line_so_the_file_is_the_store():
    for rec in every_record():
        line = st.line(rec, TODAY)
        assert f"key: {rec['key']}" in line
        assert st.carried(line, rec)


def test_a_struck_line_still_counts_as_read():
    records = every_record()
    text = st.block(records, TODAY).replace("- [ ]", "- [x]")
    assert st.fresh(text, records) == []


def test_the_same_finding_twice_in_one_pass_is_queued_once():
    rec = st.deprecated_record(SKILL, 85, "the older result")
    assert len(st.fresh("", [rec, dict(rec)])) == 1


def test_a_trigger_this_module_does_not_name_is_refused():
    with pytest.raises(ValueError):
        st.record("vibes", SKILL, "k", "e")
    assert set(st.LABELS) == set(st.TRIGGERS), (
        "a trigger with no label renders a KeyError into the queue file"
    )


def test_the_smoke_run_still_agrees_with_all_of_this(capsys):
    assert st.smoke() == 0
    assert "FAIL" not in capsys.readouterr().out


def test_a_claim_whose_own_text_quotes_a_paper_id_does_not_queue_a_fetch():
    """The reachable half of the property, and the reason `defuse` is in
    `record` rather than in one field of one record type. Claim text and paper
    titles come out of the corpus, so this input is a row in the database and
    not a hypothetical."""
    rec = st.deprecated_record(
        SKILL, 85, "the result of arxiv:2609.09134 does not replicate")
    assert "arxiv:" not in rec["evidence"]
    assert "arXiv 2609.09134" in rec["evidence"]
    assert reading_queue.parse(st.line(rec, TODAY)) == []


def test_every_spelling_the_queue_reader_acts_on_is_defused():
    for raw in ("arxiv:2609.09134", "arXiv: 2609.09134", "ARXIV:2609.09134v2",
                "arxiv:cs.CL/0612345"):
        line = st.line(st.eval_record(SKILL, "k", f"see {raw}", {}), TODAY)
        assert reading_queue.parse(line) == [], raw


def test_defusing_leaves_a_name_a_person_can_still_follow():
    """A defence that deleted the id would cost the reader the paper."""
    assert st.defuse("see arxiv:2609.09134 for it") == "see arXiv 2609.09134 for it"
    assert st.defuse("nothing to do here") == "nothing to do here"
    assert st.defuse("") == ""
