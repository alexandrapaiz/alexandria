"""Clustering the corrections before any of them becomes an edit.

ADR-40's refinement item 3 (C244): consumer reports, the survival signal and
failed-task notes are clustered, each cluster becomes one generalized edit, and
the raw pile is never applied. The failure it prevents is the one a maintenance
loop falls into by default. Eleven reports each asking for one sentence produce
eleven individually reasonable edits, and the skill grows past the point where
anything measurable is attributable to any of it.

The clustering here is lexical rather than embedded, which is a stated
limitation and not an oversight: this organization funds no embedding endpoint
and the engineer seat may not create a recurring cost. So these tests assert the
honest-reporting half as hard as the clustering half, because a lexical
clusterer that silently passes the pile through is the way this becomes
decoration.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import corrections as cx             # noqa: E402


def test_the_module_smoke_passes(capsys):
    assert cx.smoke() == 0
    assert "FAIL:" not in capsys.readouterr().out


def test_two_reports_asking_for_the_same_thing_become_one_edit():
    pile = [
        {"source": "consumer report", "where": "a", "consumer": "one",
         "sections": [], "text": "the order of operations section needs a "
                                 "worked number for the regression"},
        {"source": "consumer report", "where": "b", "consumer": "two",
         "sections": [], "text": "order of operations should quantify the "
                                 "regression it mentions"},
        {"source": "failed task", "where": "c", "consumer": "the eval harness",
         "sections": [], "text": "the container needs a memory limit"},
    ]
    groups = cx.cluster(pile)
    assert len(groups) == 2
    assert groups[0]["size"] == 2
    assert groups[0]["consumers"] == ["one", "two"]
    assert groups[0]["sources"] == ["consumer report"]
    assert "2 correction(s) from 2 source(s)" in groups[0]["edit"]


def test_the_edit_names_the_section_and_leaves_the_prose_to_the_skill_seat():
    """A generator that drafted the sentence would be this file proposing skill
    content, which is the skill seat's call and ADR-13's."""
    groups = cx.cluster([
        {"source": "consumer report", "where": "a", "consumer": "one",
         "sections": ["Order of operations"], "text": "quantify the regression"},
    ])
    assert groups[0]["edit"].startswith("[Order of operations]")
    assert groups[0]["sections"] == ["Order of operations"]


def test_clustering_is_deterministic_so_the_loop_proposes_one_thing():
    pile = [{"source": "consumer report", "where": str(i), "consumer": "c",
             "sections": [], "text": t}
            for i, t in enumerate(["quantify the regression in the harness "
                                   "section", "the harness section needs the "
                                   "regression quantified", "memory limits on "
                                   "the container"])]
    first = [g["edit"] for g in cx.cluster(pile)]
    assert first == [g["edit"] for g in cx.cluster(pile)]
    assert first == [g["edit"] for g in cx.cluster(list(pile))]


def test_a_pile_that_would_not_cluster_is_reported_rather_than_passed_off():
    """The number that matters is clusters against corrections. When they are
    equal the clusterer found nothing, and saying so is the only honest
    outcome for an instrument the ADR asked to be better than this one."""
    doc = cx.report("harness-engineering")
    assert doc["corrections"] >= 1
    if doc["clusters"] == doc["corrections"]:
        assert doc["passthrough"] is True
        assert "the raw pile with a label on it" in doc["reads"]
    else:
        assert doc["passthrough"] is False


def test_the_real_consumer_report_in_the_library_parses():
    """The one report that exists, which derived ADR-38's format by hand."""
    path = (ROOT / "skills" / "harness-engineering" / "reviews"
            / "2026-09-29-ursa-chair.md")
    assert path.exists(), "the worked example moved, and this test names it"
    text = path.read_text()
    meta = cx.frontmatter(text)
    assert meta["skill"] == "harness-engineering"
    assert cx.listed(meta["sections_exercised"])
    found = cx.proposals(text)
    assert len(found) >= 4, (
        "ADR-38's format ends in numbered proposals and this report has four")
    assert all(len(item) > 20 for item in found)


def test_the_body_s_own_numbered_lists_are_not_proposals():
    report = ("---\nskill: x\n---\n\n## Section by section\n\n"
              "1. This is the body's structure.\n\n"
              "## What alexandria should improve\n\n"
              "1. This one is a proposal.\n")
    assert cx.proposals(report) == ["This one is a proposal."]


def test_a_report_with_no_improve_section_yields_nothing():
    assert cx.proposals("---\nskill: x\n---\n\n# Bottom line\n\nFine.\n") == []
    assert cx.frontmatter("no frontmatter here") == {}


def test_a_task_the_skill_did_not_help_on_is_a_correction_nobody_filed():
    """Before ADR-40 a negative per-task delta sat in results.json and the only
    number anything read was the mean over all of them."""
    out = cx.from_results({"per_task": [
        {"id": "helped", "delta": 0.4, "with_mean": 0.9, "without_mean": 0.5},
        {"id": "flat", "delta": 0.0, "with_mean": 0.5, "without_mean": 0.5,
         "sections": ["Order of operations"], "scored_by": "rubric"},
        {"id": "hurt", "delta": -0.4, "with_mean": 0.1, "without_mean": 0.5},
        {"id": "a-control", "delta": -1.0, "control": True},
        {"id": "an-indicator", "delta": -1.0, "indicator": True},
    ]})
    assert [c["where"] for c in out] == ["flat", "hurt"]
    assert "Order of operations" in out[0]["text"]
    assert out[0]["sections"] == ["Order of operations"]
    assert all(c["source"] == "failed task" for c in out)


def test_the_survival_shape_is_fixed_now_so_its_arrival_is_a_data_change():
    """ADR-39 writes it. Nothing writes it today, and the key is reserved."""
    out = cx.from_survival({"section_deltas": {
        "Dead": {"survival": {"acted_on": False, "loads": 12}},
        "Live": {"survival": {"acted_on": True, "loads": 12}},
        "Unknown": {"survival": None},
    }})
    assert [c["where"] for c in out] == ["Dead"]
    assert "retirement candidate" in out[0]["text"]
    assert "12" in out[0]["text"]
    # Null is "nobody measured it", which must never read as "nobody acted".
    assert all(c["where"] != "Unknown" for c in out)


def test_gathering_a_skill_with_nothing_on_record_is_empty_and_not_an_error(tmp_path):
    (tmp_path / "skills" / "lonely").mkdir(parents=True)
    assert cx.gather("lonely", root=tmp_path) == []
    (tmp_path / "skills" / "lonely" / "evals").mkdir()
    (tmp_path / "skills" / "lonely" / "evals" / "results.json").write_text("{[")
    assert cx.gather("lonely", root=tmp_path) == []


def test_a_skill_with_nothing_on_record_says_where_an_edit_could_not_have_come_from(tmp_path):
    """ADR-40's trap (C965): a small model refining itself consolidates on what
    it can already reach, so a proposal with no consumer behind it is suspect."""
    (tmp_path / "skills" / "lonely").mkdir(parents=True)
    doc = cx.report("lonely", root=tmp_path)
    assert doc["corrections"] == 0 and doc["groups"] == []
    assert doc["passthrough"] is False
    assert "from somewhere" in cx.render(doc) or "nothing is on record" \
        in cx.render(doc)
