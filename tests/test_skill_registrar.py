"""The skill registrar and the daily revision job.

    python3 -m pytest tests/test_skill_registrar.py -q

Two of these tests are the reason this file exists at all. `tools/skill_registrar.py`
holds three statements that no CI job anywhere in this organization can execute,
because there is no Postgres in CI and the only one that matters is production.
So the statements are parsed with libpg_query and every relation and column they
name is resolved against `db/schema.sql`, exactly as `tests/test_graph_audit.py`
does. A migration that renames `promotions.claim_ids` turns this file red instead
of turning a daily cron silently useless.

The rest holds the parser and the job's pure half. Everything about the job that
touches GitHub or Neon is a real write, so what is tested is the decision that
precedes it: which pairs are new, what the line says, and whether a dispatch
goes out at all.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import skill_registrar as reg          # noqa: E402
import skill_revision as job           # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# --------------------------------------------------------------- the SQL

def _walk(node, out):
    """Every AST node under `node`. Same shape as tests/test_graph_audit.py's.

    Written out again rather than imported, because a walker that silently
    returns nothing makes every assertion below vacuously true, and that is
    exactly what the first draft of this file did.
    """
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
    # psycopg's placeholder is not PostgreSQL's. The server never sees `%s`.
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


@pytest.mark.parametrize("name", sorted(reg.QUERIES))
def test_every_statement_parses(name):
    assert _parse(reg.QUERIES[name])


@pytest.mark.parametrize("name", ["registered", "revisions"])
def test_the_read_statements_only_read(name):
    for node in _walk(_parse(reg.QUERIES[name]), []):
        assert type(node).__name__ not in (
            "InsertStmt", "UpdateStmt", "DeleteStmt", "DropStmt", "AlterTableStmt"
        ), f"{name} is supposed to be a read"


def test_the_only_write_is_the_upsert():
    kinds = {type(n).__name__ for n in _walk(_parse(reg.QUERIES["upsert"]), [])}
    assert "InsertStmt" in kinds
    assert not {"DeleteStmt", "DropStmt", "AlterTableStmt"} & kinds


def test_every_relation_the_registrar_names_exists():
    relations, _ = _schema_names()
    for name, sql in reg.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in relations, (
                    f"{name} reads {node.relname}, which db/schema.sql does not "
                    "define. Either the migration is missing or this guard is "
                    "pointed at a relation that was renamed.")


def test_every_column_the_registrar_names_exists():
    _, columns = _schema_names()
    # `excluded` is the upsert's own pseudo-relation and `cited`/`claim_id` come
    # from the view's lateral, so the names the statements introduce themselves
    # are allowed alongside the schema's.
    allowed = columns | {"excluded", "claim_id", "cited", "now"}
    for name, sql in reg.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "ColumnRef":
                parts = [f.sval for f in node.fields if hasattr(f, "sval")]
                for part in parts:
                    assert part in allowed, (
                        f"{name} names the column {part}, which is neither in "
                        "db/schema.sql nor introduced by the statement itself")


def test_the_partial_unique_index_the_upsert_infers_exists():
    # `on conflict (path) where kind = 'skill'` needs an index with exactly that
    # predicate. Without it Postgres raises at runtime, on the first row, inside
    # a cron nobody is watching.
    assert "promotions_skill_path_idx" in SCHEMA
    assert "on promotions (path) where kind = 'skill'" in SCHEMA


# --------------------------------------------------------------- the parser

def test_every_real_skill_yields_a_row():
    rows, problems = reg.read_skills()
    assert problems == [], problems
    assert len(rows) >= 6
    for row in rows:
        assert row.path == f"skills/{row.slug}"
        assert row.claim_ids, f"{row.slug} cites no claims"
        assert all(isinstance(c, int) for c in row.claim_ids)


def test_the_claim_ids_match_the_text_of_the_file():
    """The parser against a second, independent reading of the same line.

    This is the assertion that would have caught PR #133's bug eleven days
    earlier: a reader that silently returns nothing for an indented field looks
    exactly like a skill that cites nothing.
    """
    import re

    for row in reg.read_skills()[0]:
        raw = (ROOT / row.path / "SKILL.md").read_text()
        match = re.search(r"^\s+claims:\s*\[([^\]]*)\]", raw, re.M)
        assert match, f"{row.slug} has no inline claims array"
        expected = [int(x) for x in match.group(1).replace(" ", "").split(",") if x]
        assert row.claim_ids == expected


def test_a_skill_with_no_provenance_block_is_a_finding(tmp_path):
    skills = tmp_path / "skills"
    (skills / "lonely").mkdir(parents=True)
    (skills / "lonely" / "SKILL.md").write_text(
        "---\nname: lonely\nversion: 1\n---\n\n# Lonely\n")
    rows, problems = reg.read_skills(skills)
    assert rows == []
    assert any("no `provenance:` map" in p for p in problems)


def test_a_skill_that_cites_nothing_is_a_finding(tmp_path):
    skills = tmp_path / "skills"
    (skills / "empty").mkdir(parents=True)
    (skills / "empty" / "SKILL.md").write_text(
        "---\nname: empty\nprovenance:\n  extracted: 2026-09-30\n  claims: []\n"
        "---\n\n# Empty\n")
    rows, problems = reg.read_skills(skills)
    assert any("cites no claim ids" in p for p in problems)
    assert rows and rows[0].claim_ids == []


def test_a_name_that_disagrees_with_its_directory_is_a_finding(tmp_path):
    skills = tmp_path / "skills"
    (skills / "one-name").mkdir(parents=True)
    (skills / "one-name" / "SKILL.md").write_text(
        "---\nname: another-name\nprovenance:\n  claims: [1, 2]\n---\n\n# x\n")
    _, problems = reg.read_skills(skills)
    assert any("which is not its directory" in p for p in problems)


def test_a_directory_with_no_skill_md_is_a_finding(tmp_path):
    skills = tmp_path / "skills"
    (skills / "halfway").mkdir(parents=True)
    _, problems = reg.read_skills(skills)
    assert any("has no SKILL.md" in p for p in problems)


def test_validation_is_not_read_as_a_broken_skill(tmp_path):
    skills = tmp_path / "skills"
    (skills / "_validation").mkdir(parents=True)
    rows, problems = reg.read_skills(skills)
    assert (rows, problems) == ([], [])


def test_the_files_only_gate_passes_on_this_repository(capsys):
    assert reg.main(["--files-only"]) == 0


def test_a_database_mode_with_no_credential_is_unknown_and_exit_two(monkeypatch,
                                                                   capsys):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("NEON_RO_URL", raising=False)
    assert reg.main(["--check"]) == 2
    assert "unknown:" in capsys.readouterr().out


def test_an_unregistered_skill_is_a_finding_not_a_shrug():
    rows, _ = reg.read_skills()
    assert reg.unregistered(rows, {}) == rows
    live = {r.path: r.claim_ids for r in rows}
    assert reg.unregistered(rows, live) == []


def test_a_row_whose_claims_drifted_is_stale():
    rows, _ = reg.read_skills()
    live = {r.path: r.claim_ids for r in rows}
    assert reg.stale(rows, live) == []
    # Order must not count: a revision that reorders the list is not a change.
    live = {r.path: list(reversed(r.claim_ids)) for r in rows}
    assert reg.stale(rows, live) == []
    first = rows[0]
    live[first.path] = first.claim_ids[:-1]
    assert reg.stale(rows, live) == [first]


def test_the_offline_cross_reference_finds_the_skill_that_cites_the_claim():
    rows, _ = reg.read_skills()
    cited = rows[0].claim_ids[0]
    hits = reg.touching(rows, [cited])
    assert any(h["skill_path"] == rows[0].path for h in hits)
    assert reg.touching(rows, [10 ** 9]) == []


# --------------------------------------------------------------- the job

ROW = {"skill_path": "skills/context-window-engineering",
       "deprecated_claim_id": 85,
       "deprecated_claim": "the same approach attains only 12.5% on RMBench"}


def test_a_pair_already_in_the_queue_is_not_queued_again():
    block = job.queue_block([ROW], "2026-09-30")
    assert job.new_pairs("", [ROW]) == [ROW]
    assert job.new_pairs(block, [ROW]) == []


def test_a_line_struck_by_the_research_seat_still_counts_as_carried():
    struck = job.queue_block([ROW], "2026-09-30").replace("- [ ]", "- [x]")
    assert job.new_pairs(struck, [ROW]) == []


def test_two_identical_rows_in_one_read_produce_one_line():
    assert len(job.new_pairs("", [ROW, dict(ROW)])) == 1


def test_the_queue_line_carries_no_arxiv_id():
    """`pipeline/reading_queue.py` treats an id as a paper to fetch.

    A revision line names no paper, because the paper that contradicts the claim
    is what the reading is for. An invented id would put a fetch request in front
    of distill for a paper nobody asked for.
    """
    line = job.queue_line(ROW["skill_path"], 85, ROW["deprecated_claim"],
                          "2026-09-30")
    import reading_queue

    assert reading_queue.parse(line) == []


def test_the_queue_line_is_a_checklist_item_in_the_documented_shape():
    line = job.queue_line(ROW["skill_path"], 85, ROW["deprecated_claim"],
                          "2026-09-30")
    assert line.startswith("- [ ] ")
    assert "asked by skills/context-window-engineering" in line
    assert line.endswith("2026-09-30")


def test_a_very_long_claim_is_truncated_rather_than_pasted_whole():
    line = job.queue_line("skills/x", 1, "word " * 200, "2026-09-30")
    assert "..." in line and len(line) < 500


def test_the_dispatch_names_the_pairs_and_warns_about_a_wrong_edge():
    text = job.dispatch_instructions([ROW], "2026-09-30")
    assert "[deprecated] skills/context-window-engineering" in text
    assert "cites claim 85," in text
    assert "2026-09-28" in text, (
        "the dispatch has to carry the research seat's finding that four of six "
        "contradicts edges were wrong, or the skill seat rewrites a skill over a "
        "misclassification")


def test_a_long_list_names_only_what_one_run_can_do():
    rows = [{"skill_path": f"skills/s{n}", "deprecated_claim_id": n,
             "deprecated_claim": "x"} for n in range(20)]
    text = job.dispatch_instructions(rows, "2026-09-30")
    assert text.count("\n- [deprecated] skills/") == job.MAX_PAIRS_PER_DISPATCH
    assert "further findings are in the queue" in text


def test_the_job_is_not_in_the_kimi_window_table():
    """It calls no model, so putting it there would make the guard lie."""
    import llm

    assert not any("skill_revision" in k for k in llm.KIMI_WINDOWS)
    assert "16:00-16:15  skill revision" in pathlib.Path(
        ROOT / "pipeline" / "llm.py").read_text(), (
        "the slot is undocumented, so the next seat to schedule something at "
        "16:00 UTC has no way to know it is taken")
    assert llm.window_overlaps() == []


def test_the_schedule_sits_outside_every_reserved_window():
    import re

    import llm

    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    cron = re.search(r'modal\.Cron\("(\d+) (\d+) ', source)
    assert cron, "the job no longer declares a daily cron where this test looks"
    minute_of_day = int(cron.group(2)) * 60 + int(cron.group(1))
    for label, (start, end) in llm.KIMI_WINDOWS.items():
        assert not (start <= minute_of_day < end), (
            f"the revision job starts inside {label}'s window")


def test_the_kill_switch_stops_the_loop_before_anything_is_written():
    """Guardrail 2 of ADR-37's amendment, 2026-09-29.

    `skills/MAINTENANCE_PAUSED` on main pauses automatic maintenance. This job is
    where the loop starts, so it is the cheapest place to read the switch: no
    queue line, no dispatch, and the run prints whose reason stopped it.
    """
    class Fake:
        def __init__(self, text):
            self.text = text

        def read_file(self, path, ref):
            assert path == job.PAUSE_PATH
            if self.text is None:
                raise RuntimeError("404")
            return (self.text, "sha")

    assert job.paused(Fake(None), "main") == ""
    assert job.paused(Fake("  the graph is wrong\n\n"), "main") == \
        "the graph is wrong"
    assert job.paused(Fake("   \n"), "main") == "no reason given in the file"


def test_the_pause_path_is_where_the_amendment_put_it():
    assert job.PAUSE_PATH == "skills/MAINTENANCE_PAUSED"
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    assert "guardrail 2" in source.lower()
    # Read before the queue append and the dispatch, never after.
    assert source.index("PAUSED:") < source.index("# Step 3, the queue.")
