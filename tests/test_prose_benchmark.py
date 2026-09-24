"""Tests for tools/blind_prose_benchmark.py.

The thing worth pinning here is not the arithmetic. It is that the
blinding actually blinds: a specimen that still carries a non-breaking
hyphen, an arXiv link or the word "alexandria" is not a blind specimen,
and the experiment it feeds is worthless whether or not anyone notices.
"""

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import blind_prose_benchmark as bench  # noqa: E402

PACKET = ROOT / "docs/evals/2026-09-21-prose-benchmark/specimens"
SOURCE = ROOT / "docs/evals/2026-09-21-prose-benchmark/sources/comparison-2026-09-21.txt"
ISSUE = ROOT / "site/content/issues/2026-W37.md"


# --------------------------------------------------------------- blinding

def test_typographic_characters_become_ascii():
    raw = "long‑horizon gains of 28.5 % and 3× speed—really"
    out = bench.blind(raw, [])
    assert all(ord(c) < 128 for c in out)
    assert "long-horizon" in out
    assert "28.5%" in out
    assert "3x" in out


def test_publisher_names_are_redacted_case_insensitively():
    out = bench.blind("Alexandria beats tldr ai this week", ["alexandria", "TLDR AI"])
    assert "lexandria" not in out
    assert "tldr" not in out.lower()
    assert out.count("[publication]") == 2


def test_a_publisher_name_inside_another_word_survives():
    # "Alexandrian" is not the publisher, and a substring replace would eat it.
    assert "Alexandrian" in bench.blind("An Alexandrian library", ["alexandria"])


def test_links_and_annotations_go():
    out = bench.blind(
        "A Paper [https://arxiv.org/abs/2609.08404](https://arxiv.org/abs/2609.08404)\n"
        "The Inference Gap (56 minute read)\nAX (GitHub Repo)",
        [],
    )
    assert "arxiv" not in out
    assert "http" not in out
    assert "minute read" not in out
    assert "GitHub Repo" not in out
    assert "The Inference Gap" in out and "AX" in out


def test_emphasis_is_flattened_on_both_sides():
    out = bench.blind("**Bold lead.** Then *italic* and `code`.", [])
    assert "*" not in out and "`" not in out
    assert "Bold lead. Then italic and code." in out


def test_sub_list_indentation_survives_space_collapsing():
    out = bench.blind("body   text\n  - a   sub   bullet", [])
    assert "body text" in out
    assert "\n  - a sub bullet" in out


# ------------------------------------------------------------- extraction

def test_house_extract_takes_the_opening_and_only_the_first_item():
    opening, heading, item = bench.extract_house(ISSUE.read_text(encoding="utf-8"))
    assert opening.startswith("This week")
    assert heading == "Trailblazing"
    assert sum(1 for l in item if l.startswith("- ")) == 1


def test_house_title_is_not_double_punctuated():
    lines = bench.house_item_lines(["- **A finding lands.**  ", "  Body sentence."])
    assert lines[0] == "A finding lands."
    assert not lines[0].endswith("..")


def test_comparison_uses_the_second_section_and_skips_sponsors():
    source = (
        "publisher: X\n---\n"
        "## First\nLead item (1 minute read)\nbody\n\n"
        "## Second\nAn ad (Sponsor)\nbuy this\n\nReal item (2 minute read)\n"
        + " ".join(["word"] * 200) + "\n"
    )
    _, sections = bench.parse_comparison(source)
    name, items = bench.extract_comparison(sections, 50)
    assert name == "Second"
    assert [i["title"] for i in items] == ["Real item (2 minute read)"]


def test_comparison_stops_once_it_reaches_the_target_length():
    source = "publisher: X\n---\n## First\n(items not retained: 1 items)\n\n## Second\n" + "".join(
        f"Item {n} (1 minute read)\n{' '.join(['word'] * 20)}\n\n" for n in range(5)
    )
    _, sections = bench.parse_comparison(source)
    # Each item is 25 words: a five-word title and a twenty-word body.
    _, few = bench.extract_comparison(sections, 30)
    _, many = bench.extract_comparison(sections, 90)
    assert len(few) == 2 and len(many) == 4


def test_comparison_source_on_disk_parses_to_the_sections_we_claim():
    meta, sections = bench.parse_comparison(SOURCE.read_text(encoding="utf-8"))
    assert meta["publisher"] == "TLDR AI"
    assert [s["name"] for s in sections][:2] == ["Headlines & Launches", "Deep Dives & Analysis"]
    assert len(sections[1]["items"]) == 3


# ---------------------------------------------------------------- shuffle

def test_assignment_is_deterministic_and_gives_each_side_its_own_label():
    first = bench.assignment(20260921)
    assert first == bench.assignment(20260921)
    assert set(first.values()) == {"A", "B"}
    assert any(bench.assignment(s) != first for s in range(50))


# ------------------------------------------------- the committed specimens

@pytest.mark.parametrize("name", ["specimen-A.md", "specimen-B.md"])
def test_committed_specimen_carries_no_identity_tell(name):
    text = (PACKET / name).read_text(encoding="utf-8")
    assert all(ord(c) < 128 for c in text), "typographic tell survived"
    lowered = text.lower()
    for tell in ("alexandria", "tldr", "arxiv", "http", "minute read",
                 "github repo", "sponsor", "2026-w37", "digest"):
        assert tell not in lowered, f"{name} still carries {tell!r}"


def test_the_two_committed_specimens_are_within_a_third_of_each_other():
    sizes = [len((PACKET / n).read_text(encoding="utf-8").split())
             for n in ("specimen-A.md", "specimen-B.md")]
    assert max(sizes) / min(sizes) < 1.34, f"specimens are lopsided: {sizes}"


def test_the_packet_ships_a_sheet_and_no_key():
    names = {p.name for p in PACKET.iterdir()}
    assert names == {"specimen-A.md", "specimen-B.md", "scoring-sheet.md"}


# ------------------------------------------------------------------ tally

def sheet(grader, a, b, preference, recognised="no"):
    return (
        f"# a comment\ngrader: {grader}\n\n"
        f"A-clarity: {a[0]}\nA-clarity-why: because\nA-human: {a[1]}\nA-lands: {a[2]}\n"
        f"B-clarity: {b[0]}\nB-human: {b[1]}\nB-lands: {b[2]}\n"
        f"recognised: {recognised}\npreference: {preference}\npreference-why: reasons\n"
    )


def test_parse_sheet_skips_comments_and_blank_answers():
    fields = bench.parse_sheet("# Clarity: a question\ngrader: Ana\nA-clarity:\nA-human: 4\n")
    assert fields == {"grader": "Ana", "A-human": "4"}


def test_tally_averages_and_maps_labels_back_to_publications(tmp_path, capsys):
    scores = tmp_path / "scores"
    scores.mkdir()
    (scores / "ana.md").write_text(sheet("Ana", [5, 4, 5], [2, 1, 2], "A"))
    (scores / "ben.md").write_text(sheet("Ben", [4, 4, 4], [3, 1, 2], "A", recognised="B"))
    out = tmp_path / "result.json"
    assert bench.main(["--seed", "20260921", "tally", "--scores", str(scores),
                       "--write", str(out)]) == 0
    import json
    result = json.loads(out.read_text())
    assert result["key"] == {"specimen-A": "comparison", "specimen-B": "house"}
    assert result["scores"]["comparison"]["clarity"] == 4.5
    assert result["scores"]["house"]["human"] == 1.0
    assert result["preference"] == {"house": 0, "comparison": 2}
    assert result["recognised"] == {"house": 1, "comparison": 0}
    assert result["graders"] == ["Ana", "Ben"]


def test_tally_refuses_a_score_outside_the_scale(tmp_path):
    scores = tmp_path / "scores"
    scores.mkdir()
    (scores / "ana.md").write_text(sheet("Ana", [9, 4, 5], [2, 1, 2], "A"))
    assert bench.main(["tally", "--scores", str(scores)]) == 1


def test_tally_refuses_a_score_that_is_not_a_number(tmp_path):
    scores = tmp_path / "scores"
    scores.mkdir()
    (scores / "ana.md").write_text(sheet("Ana", ["good", 4, 5], [2, 1, 2], "A"))
    assert bench.main(["tally", "--scores", str(scores)]) == 1


def test_tally_says_so_rather_than_inventing_a_result(tmp_path):
    assert bench.main(["tally", "--scores", str(tmp_path / "nothing")]) == 1
