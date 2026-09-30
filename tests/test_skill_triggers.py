"""ADR-37's four triggers: the arithmetic, the SQL, and the one line that must not fetch.

Three kinds of assertion in here, and the second is the reason the file exists at
all.

The arithmetic is pure and testable: which refines edge fires, which citation
move is noise, which eval history is a regression. That half is ordinary.

The SQL cannot be executed anywhere in this organization. There is no Postgres in
CI and the only one that matters is production, so the two statements
`tools/skill_triggers.py` sends are parsed with libpg_query and every relation and
column they name is resolved against `db/schema.sql`, exactly as
`tests/test_graph_audit.py` and `tests/test_skill_registrar.py` do. A renamed
column would otherwise turn a daily cron silently useless, which is the failure
mode this org has already met twice.

The third is a safety property. `pipeline/reading_queue.py` treats any
`arxiv:<id>` in a queue line as a paper to fetch and puts it at the front of
distill's drain. The citation trigger's evidence is about a paper the corpus
already holds, so a line that named it as an id would ask distill to re-fetch it.
Every line every trigger can produce is parsed by the real reading-queue parser
here, and must yield nothing to fetch.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import skill_triggers as tr           # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# --------------------------------------------------------------- the SQL

def _walk(node, out):
    ast = pytest.importorskip("pglast").ast
    if isinstance(node, ast.Node):
        out.append(node)
        for slot in node.__slots__:
            _walk(getattr(node, slot, None), out)
    elif isinstance(node, (list, tuple)):
        for item in node:
            _walk(item, out)
    return out


def _parse(sql):
    pglast = pytest.importorskip(
        "pglast", reason="pip install -r requirements-dev.txt")
    return pglast.parse_sql(sql.replace("%s", "$1"))


def _schema_names():
    pglast = pytest.importorskip("pglast")
    relations, columns = set(), set()
    for node in _walk(pglast.parse_sql(SCHEMA), []):
        name = type(node).__name__
        if name in ("CreateStmt", "ViewStmt"):
            rel = getattr(node, "relation", None) or getattr(node, "view", None)
            if rel is not None:
                relations.add(rel.relname)
        if name == "ColumnDef" and node.colname:
            columns.add(node.colname)
        if name == "ResTarget" and node.name:
            columns.add(node.name)
    return relations, columns


@pytest.mark.parametrize("name", sorted(tr.QUERIES))
def test_every_statement_parses(name):
    assert _parse(tr.QUERIES[name])


@pytest.mark.parametrize("name", sorted(tr.QUERIES))
def test_every_statement_only_reads(name):
    """Nothing here writes. The one write in this loop is the registrar's upsert."""
    for node in _walk(_parse(tr.QUERIES[name]), []):
        assert type(node).__name__ not in (
            "InsertStmt", "UpdateStmt", "DeleteStmt", "DropStmt",
            "AlterTableStmt", "CreateStmt"), f"{name} is supposed to be a read"


def test_every_relation_the_triggers_name_exists():
    relations, _ = _schema_names()
    # `checks` is the citation query's own CTE.
    allowed = relations | {"checks"}
    for name, sql in tr.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in allowed, (
                    f"{name} reads {node.relname}, which db/schema.sql does not "
                    "define. Either a migration is missing or this trigger is "
                    "pointed at a relation that was renamed.")


def test_every_column_the_triggers_name_exists():
    _, columns = _schema_names()
    # The names the statements introduce themselves.
    allowed = columns | {"rn", "checks", "latest", "prev", "l", "c", "p", "nc",
                         "np", "to_claim", "from_claim"}
    for name, sql in tr.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "ColumnRef":
                for field in node.fields:
                    part = getattr(field, "sval", None)
                    if part is None:
                        continue
                    assert part in allowed, (
                        f"{name} names the column {part}, which is neither in "
                        "db/schema.sql nor introduced by the statement itself")


def test_the_citation_query_reads_the_slow_loop_s_own_window():
    """`weekly.py`'s movers section means the last two checks. So does this."""
    sql = tr.QUERIES["citation_moves"]
    assert "rn = 1" in sql and "rn = 2" in sql
    assert "citation_log" in sql


def test_the_refines_query_asks_for_the_relation_and_the_confidence():
    sql = tr.QUERIES["refines_since"]
    assert "relation = 'refines'" in sql
    assert "coalesce(l.confidence, 0) >= %s" in sql, (
        "a null confidence must not read as a confident edge")


# --------------------------------------------------------------- trigger 2

class Row:
    def __init__(self, path="skills/x", claims=(1, 2, 3), version="1",
                 extracted="2026-09-15"):
        self.path = path
        self.slug = path.rsplit("/", 1)[-1]
        self.claim_ids = list(claims)
        self.version = version
        self.extracted = extracted


EDGE = {"claim_id": 2, "refined_by": 99, "confidence": 0.8,
        "created_at": "2026-09-20", "claim": "the narrower form",
        "paper_id": "arxiv:2609.09134", "paper_title": "A newer paper",
        "paper_url": "arxiv.org/abs/2609.09134"}


def _refines(edge, since="2026-09-15", claims=(1, 2, 3)):
    row = Row(claims=claims)
    return tr.refines_records({row.path: row}, [edge],
                              {row.path: (since, "provenance.extracted")})


def test_a_confident_refines_edge_after_the_version_date_fires():
    hits = _refines(EDGE)
    assert len(hits) == 1
    assert hits[0]["trigger"] == "refines"
    assert "claim 99 now refines it" in hits[0]["evidence"]


def test_an_edge_below_the_confidence_floor_does_not_fire():
    assert _refines({**EDGE, "confidence": 0.69}) == []
    assert tr.REFINES_MIN_CONFIDENCE == 0.7, (
        "ADR-37 names 0.7, the same number deprecated_claims uses")


def test_an_edge_with_no_confidence_at_all_does_not_fire():
    assert _refines({**EDGE, "confidence": None}) == []


def test_an_edge_older_than_the_version_does_not_fire():
    """The skill's author already had that paper when they wrote the version."""
    assert _refines({**EDGE, "created_at": "2026-09-01"}) == []


def test_an_edge_on_a_claim_the_skill_does_not_cite_does_not_fire():
    assert _refines(EDGE, claims=(1, 3)) == []


def test_a_skill_with_no_knowable_version_date_is_skipped_not_guessed():
    """Defaulting to the epoch would fire on every edge the graph has ever held."""
    row = Row()
    assert tr.refines_records({row.path: row}, [EDGE], {row.path: ("", "")}) == []


def test_the_version_date_prefers_the_date_the_version_was_measured(tmp_path):
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals" / "results.json").write_text(
        '{"history": [{"version": "2", "date": "2026-09-28",'
        ' "subject_model": "kimi-k2.6", "delta": {"mean": 0.3,'
        ' "ci95": [0.1, 0.5]}}]}')
    date, source = tr.version_date(tmp_path, Row(version="2"))
    assert date == "2026-09-28" and "measured" in source


def test_the_version_date_falls_back_to_the_provenance_block(tmp_path):
    date, source = tr.version_date(tmp_path, Row(version="2"))
    assert date == "2026-09-15" and source == "provenance.extracted"


# --------------------------------------------------------------- trigger 3

@pytest.mark.parametrize("before,now,fires", [
    (4, 40, True),      # both rules
    (30, 50, True),     # the absolute rule alone
    (5, 11, True),      # the ratio rule alone
    (40, 4, True),      # down counts too: ADR-37 says up or down
    (1, 3, False),      # 3x on noise, below the floor
    (2, 4, False),      # 2x on noise, below the floor
    (0, 4, False),      # from nothing to nearly nothing
    (0, 25, True),      # from nothing to something, on the absolute rule
    (100, 110, False),  # a tenth of a move on a well-cited paper
])
def test_which_citation_moves_matter(before, now, fires):
    assert tr.moved(before, now) is fires


def test_the_reason_names_the_rule_that_fired():
    assert "20 the trigger names" in tr.movement_reason(4, 40)
    assert "2x the trigger names" in tr.movement_reason(5, 11)


def test_a_citation_record_names_the_paper_by_url_and_never_by_id():
    row = {"claim_id": 1, "paper_id": "arxiv:2609.08572",
           "paper_title": "A paper", "paper_url": "arxiv.org/abs/2609.08572",
           "citations_before": 4, "citations_now": 40,
           "checked_before": "2026-09-16", "checked_at": "2026-09-30"}
    hits = tr.citation_records({"skills/x": {1}}, [row])
    assert len(hits) == 1
    assert "arxiv:" not in tr.line(hits[0], "2026-09-30")


# --------------------------------------------------------------- trigger 4

GAIN = {"version": "1", "date": "2026-09-20", "subject_model": "kimi-k2.6",
        "verdict": "gain", "delta": {"mean": 0.4, "ci95": [0.2, 0.6]}}


def test_a_delta_below_the_previous_lower_bound_is_a_regression():
    worse = {**GAIN, "version": "2", "date": "2026-09-29",
             "delta": {"mean": 0.1, "ci95": [-0.1, 0.3]}}
    hits = tr.eval_records("skills/x", {"history": [GAIN, worse]}, "kimi-k2.6")
    assert len(hits) == 1 and "fell from" in hits[0]["evidence"]


def test_a_delta_that_dipped_inside_the_spread_is_not_a_regression():
    inside = {**GAIN, "version": "2", "date": "2026-09-29",
              "delta": {"mean": 0.25, "ci95": [0.05, 0.45]}}
    assert tr.eval_records("skills/x", {"history": [GAIN, inside]},
                           "kimi-k2.6") == []


def test_a_verdict_that_is_not_a_gain_is_a_finding():
    flat = {**GAIN, "verdict": "no gain",
            "delta": {"mean": 0.02, "ci95": [-0.2, 0.2]}}
    hits = tr.eval_records("skills/x", {"history": [flat]}, "kimi-k2.6")
    assert len(hits) == 1 and "no gain" in hits[0]["evidence"]


def test_a_subject_model_that_moved_asks_for_a_re_run_and_nothing_else():
    hits = tr.eval_records("skills/x", {"history": [GAIN]}, "kimi-k3")
    assert len(hits) == 1
    assert hits[0]["trigger"] == "eval"
    assert "kimi-k3" in hits[0]["evidence"]
    assert "retire" not in hits[0]["evidence"], (
        "a model rollout must never read as a regression")


def test_a_regression_across_a_model_change_is_not_reported_as_one():
    """The two deltas are not comparable, and ADR-36 says so in the harness too."""
    old_model = {**GAIN, "subject_model": "kimi-k2.5",
                 "delta": {"mean": 0.9, "ci95": [0.8, 1.0]}}
    now = {**GAIN, "version": "2", "delta": {"mean": 0.3, "ci95": [0.1, 0.5]}}
    hits = tr.eval_records("skills/x", {"history": [old_model, now]},
                           "kimi-k2.6")
    assert hits == []


def test_a_skill_with_no_eval_is_unmeasured_and_never_a_trigger():
    assert tr.eval_records("skills/x", {}, "kimi-k2.6") == []


def test_a_results_file_written_before_the_history_existed_still_compares():
    """One entry, synthesised, so the record starts at the published number."""
    doc = {"date": "2026-09-20", "subject_model": "kimi-k2.6",
           "verdict": "no gain", "delta": {"mean": 0.0, "ci95": [-0.2, 0.2]}}
    assert len(tr.history_entries(doc)) == 1
    assert tr.eval_records("skills/x", doc, "kimi-k2.6")


def test_a_history_entry_carries_no_nested_history():
    entry = tr.summary_entry({"date": "2026-09-30", "verdict": "gain",
                              "delta": {"mean": 0.4, "ci95": [0.2, 0.6]},
                              "history": ["something"], "per_task": [1, 2, 3]},
                             "3", "refines")
    assert "history" not in entry and "per_task" not in entry
    assert entry["trigger"] == "refines" and entry["version"] == "3"


# --------------------------------------------------------------- the queue

RECORDS = [
    tr.deprecated_record("skills/x", 85, "the older result"),
    tr.refines_record("skills/x", 2, EDGE, "2026-09-15", "provenance.extracted"),
    tr.citations_record("skills/x", {
        "claim_id": 1, "paper_id": "arxiv:2609.08572", "paper_title": "A paper",
        "paper_url": "arxiv.org/abs/2609.08572", "citations_before": 4,
        "citations_now": 40, "checked_before": "2026-09-16",
        "checked_at": "2026-09-30"}),
    tr.eval_record("skills/x", "skills/x#eval-2026-09-29", "the delta fell",
                   {}),
]


def test_no_queue_line_this_module_can_write_asks_distill_to_fetch_anything():
    import reading_queue

    text = tr.block(RECORDS, "2026-09-30")
    assert reading_queue.parse(text) == [], (
        "a line carrying an arxiv id would be read as a fetch request and put a "
        "paper the corpus already holds at the front of distill's drain")


def test_every_line_is_a_checklist_item_in_the_documented_shape():
    for rec in RECORDS:
        line = tr.line(rec, "2026-09-30")
        assert line.startswith("- [ ] ")
        assert f"asked by {rec['skill_path']}" in line
        assert line.endswith("2026-09-30")
        assert len(line) < 600


def test_the_same_finding_is_never_queued_twice():
    text = tr.block(RECORDS, "2026-09-30")
    assert tr.fresh(text, RECORDS) == []
    assert tr.fresh("", RECORDS) == RECORDS


def test_a_line_struck_by_the_research_seat_still_counts_as_carried():
    struck = tr.block(RECORDS, "2026-09-30").replace("- [ ]", "- [x]")
    assert tr.fresh(struck, RECORDS) == []


def test_a_deprecated_line_from_the_first_pass_still_counts_as_carried():
    """The first version of the job wrote no key. Nothing on main has one yet."""
    legacy = ("- [ ] Revision: skills/x cites claim 85, which the graph now "
              "marks deprecated. — asked by skills/x — 2026-09-29")
    assert tr.carried(legacy, RECORDS[0])


def test_the_heading_says_which_triggers_found_what():
    text = tr.block(RECORDS, "2026-09-30")
    for label in tr.LABELS.values():
        assert label in text


def test_a_record_with_an_unknown_trigger_is_refused():
    with pytest.raises(ValueError):
        tr.record("vibes", "skills/x", "k", "because")


# --------------------------------------------------------------- the snapshot

def test_claim_ids_compress_to_ranges_and_answer_membership():
    spans = tr.ranges([1, 2, 3, 7, 8, 100])
    assert spans == [[1, 3], [7, 8], [100, 100]]
    assert tr.in_ranges(2, spans) and tr.in_ranges(100, spans)
    assert not tr.in_ranges(4, spans) and not tr.in_ranges(101, spans)


def test_a_snapshot_says_when_it_was_measured_and_what_it_is_for():
    doc = tr.snapshot([[1, 300]], [85, 85, 129], "2026-09-30")
    assert doc["generated_at"] == "2026-09-30"
    assert doc["deprecated_claim_ids"] == [85, 129]
    assert "tools/skill_gate.py" in doc["what_this_is"]


def test_a_missing_or_stale_snapshot_is_a_problem_and_a_fresh_one_is_not():
    fresh = tr.snapshot([[1, 300]], [85], "2026-09-30")
    assert tr.snapshot_problems(fresh, "2026-09-30", 3) == []
    assert tr.snapshot_problems(fresh, "2026-10-05", 3)
    assert tr.snapshot_problems({}, "2026-09-30", 3)
    assert tr.snapshot_problems({"claim_id_ranges": [[1, 2]]}, "2026-09-30", 3)


def test_a_deprecated_or_missing_cited_claim_is_named_one_by_one():
    doc = tr.snapshot([[1, 300]], [85], "2026-09-30")
    problems = tr.claim_problems([85, 9001, 12], doc)
    assert len(problems) == 2
    assert any("deprecated" in p for p in problems)
    assert any("does not exist" in p for p in problems)


# --------------------------------------------------------------- the library

def test_the_real_library_reads_a_version_date_for_every_skill():
    """Trigger 2 is unmeasurable for a skill with no date, so this is the floor."""
    import skill_registrar as registrar

    rows, _ = registrar.read_skills()
    assert rows
    for row in rows:
        date, source = tr.version_date(registrar.SKILLS_DIR / row.slug, row)
        assert date, f"{row.path} has no version date, so trigger 2 cannot run"


def test_the_smoke_passes():
    assert tr.smoke() == 0
