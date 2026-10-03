"""ADR-13's provenance reviewer: its SQL, its file checks, and its wiring.

    python3 -m pytest tests/test_panel_provenance.py -q

Three kinds of check here, and they need different tools.

**The SQL.** `tools/panel_provenance.py` sends three statements and no CI job in
this organization can execute any of them, because there is no Postgres in CI.
So they are parsed with libpg_query and every relation and column they name is
resolved against `db/schema.sql`, the same instrument `tests/test_graph_audit.py`
and `tests/test_skill_registrar.py` use. A renamed column fails the pull request
rather than the daily cron.

**The judgments.** Everything the reviewer decides is a pure function of a
SKILL.md's text and a dict of claim rows, so each duty is exercised against a
written-out skill rather than against the library. The live library is then
reviewed too, because a reviewer that passes a fixture and fails on the real
six skills would be a reviewer nobody can read.

**The wiring.** The reviewer runs daily inside `pipeline/skill_revision.py`, and
that is the half most likely to rot: the image has to carry the file, the job
has to call it inside its database connection and before its early return, and
the owner's alarm has to key on the string the pass actually prints. Those are
read as source, because the job itself writes to Neon and GitHub.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import panel_provenance as panel      # noqa: E402
import skill_revision as job          # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# --------------------------------------------------------------- the SQL

def _walk(node, out):
    """Every AST node under `node`. Same shape as tests/test_graph_audit.py's.

    Written out again rather than imported, for the reason that file gives: a
    walker that silently returns nothing makes every assertion below vacuously
    true, and that is what its own first draft did.
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
            columns.add(node.name)          # a view's own output column names
    return relations, columns


def test_the_walker_actually_walks():
    assert len(_walk(_parse(panel.QUERIES["claims"]), [])) > 5


@pytest.mark.parametrize("name", sorted(panel.QUERIES))
def test_every_statement_parses(name):
    statements = _parse(panel.QUERIES[name])
    assert len(statements) == 1, "one statement per entry, one failure per name"


def test_the_reviewer_reads_everything_and_writes_one_table():
    """ADR-13's first slice is read-only apart from the verdict it files.

    The reviewer is pointed at the production corpus by the daily job, so "it
    only reads, except for its own verdict row" has to be a checked property
    rather than a sentence in a docstring.
    """
    kinds = {}
    for name, sql in panel.QUERIES.items():
        kinds[name] = type(_parse(sql)[0].stmt).__name__
    assert kinds["claims"] == "SelectStmt"
    assert kinds["consensus"] == "SelectStmt"
    assert kinds["file"] == "InsertStmt"

    insert = _parse(panel.QUERIES["file"])[0].stmt
    assert insert.relation.relname == "panel_verdicts"
    writes = [k for k, v in kinds.items() if v != "SelectStmt"]
    assert writes == ["file"], f"something else writes: {writes}"


def test_every_relation_the_reviewer_names_exists():
    relations, _ = _schema_names()
    for name, sql in panel.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in relations, (
                    f"{name} reads {node.relname}, which db/schema.sql does "
                    "not create")


def test_every_column_the_reviewer_names_exists():
    _, columns = _schema_names()
    for name, sql in panel.QUERIES.items():
        nodes = _walk(_parse(sql), [])
        defined = set()
        for node in nodes:
            if type(node).__name__ == "ResTarget" and node.name:
                defined.add(node.name)
            if type(node).__name__ == "Alias":
                defined.update(c.sval for c in (node.colnames or ()))
        allowed = columns | defined
        for node in nodes:
            if type(node).__name__ != "ColumnRef":
                continue
            fields = [f.sval for f in node.fields if hasattr(f, "sval")]
            if not fields:
                continue
            assert fields[-1] in allowed, (
                f"{name} reads a column named {fields[-1]}, which is neither "
                "in db/schema.sql nor defined by the statement itself")


def test_the_verdict_row_is_pinned_to_the_text_it_judged():
    """The property the third slice's merge will rest on.

    ADR-13 merges on unanimous pass. If a verdict did not say which text it
    passed, a pull request could earn three passes and then be edited, and the
    merge would ship the edit. `target_sha` is that defence, so the insert has
    to carry it and the schema has to require it.
    """
    assert "target_sha" in panel.QUERIES["file"]
    create = [s for s in SCHEMA.split(";") if "create table if not exists panel_verdicts" in s]
    assert create, "db/schema.sql has no panel_verdicts table"
    assert "target_sha   text not null" in create[0]


def test_unanimous_means_three_passes_on_one_text():
    """The gate, as the view computes it, read as source.

    Two mistakes are easy here and both are fatal to ADR-13's autonomy: count
    passes without checking they are passes of the same text, or read "every
    reviewer who filed passed" as unanimous when only one filed.
    """
    view = SCHEMA.split("create or replace view panel_consensus as")[1]
    view = view.split(";")[0]
    assert "count(*) filter (where verdict = 'pass') = 3" in view
    assert "count(distinct target_sha) = 1" in view




def _table_columns(table: str) -> set:
    """The columns db/schema.sql gives one table, not the schema's whole union.

    `_schema_names` flattens every column name in the file into one set, which
    is the right looseness for a SELECT whose FROM this test does not resolve.
    It is too loose for an INSERT: `panel_verdicts (model)` would pass against a
    `model` column that belongs to `triage_log`.
    """
    pglast = pytest.importorskip("pglast")
    for node in _walk(pglast.parse_sql(SCHEMA), []):
        if type(node).__name__ != "CreateStmt":
            continue
        relation = getattr(node, "relation", None)
        if relation is None or relation.relname != table:
            continue
        return {c.colname for c in _walk(node, [])
                if type(c).__name__ == "ColumnDef" and c.colname}
    raise AssertionError(f"db/schema.sql creates no table named {table}")


def test_the_schema_reader_finds_the_table_it_is_asked_for():
    """`_table_columns` returning an empty set would make the test below
    vacuously true, which is the failure mode `_walk`'s own guard exists for.
    """
    assert "target_sha" in _table_columns("panel_verdicts")
    assert "to_claim" not in _table_columns("panel_verdicts")


def test_every_column_this_reviewer_writes_exists_in_panel_verdicts():
    """The half the SELECT tests above do not reach, and the only half that
    matters for what a reviewer *writes*.

    An INSERT's target columns are `ResTarget` nodes in `stmt.cols`, not
    `ColumnRef`s, so the column test above never looked at them. Renaming
    `panel_verdicts.target_sha` left all three reviewer suites green and would
    have been discovered by a 16:00 UTC cron raising on every verdict it tried
    to file. Recorded as INC-2026-10-03-reviewer-suites-never-resolved-the-
    insert-columns.
    """
    columns = _table_columns("panel_verdicts")
    stmt = _parse(panel.QUERIES["file"])[0].stmt
    assert stmt.cols, "the INSERT names no columns, so the order is positional"
    for col in stmt.cols:
        assert col.name in columns, (
            f"this reviewer writes panel_verdicts.{col.name}, which "
            "db/schema.sql does not define")
    values = stmt.selectStmt.valuesLists[0]
    assert len(stmt.cols) == len(values), (
        f"{len(stmt.cols)} columns and {len(values)} values, so the row would be written into the wrong columns or not at all")


# ------------------------------------------------------- a skill, written out

FRONTMATTER = """---
name: {slug}
description: A fixture skill, long enough to look like one.
version: 1
status: active
provenance:
  extracted: 2026-09-12
  validated: {validated}
  claims: [{claims}]
  papers:
{papers}
---
"""

BODY = """
# A fixture skill

## First section

A finding the papers support, stated flat.

## Second section

A practical ordering (ours, not the paper's) that no paper states.
"""


def write_skill(root, slug="fixture-skill", claims="1, 2", validated='""',
                papers=("A paper - arxiv.org/abs/2609.09134",), body=BODY):
    directory = root / slug
    directory.mkdir(parents=True, exist_ok=True)
    listed = "\n".join(f'    - "{p}"' for p in papers)
    (directory / "SKILL.md").write_text(
        FRONTMATTER.format(slug=slug, claims=claims, validated=validated,
                           papers=listed) + body)
    return root


def only(verdicts, check=None, severity=None):
    out = []
    for verdict in verdicts:
        for finding in verdict["findings"]:
            if check and finding["check"] != check:
                continue
            if severity and finding["severity"] != severity:
                continue
            out.append(finding)
    return out


# ------------------------------------------------------------- the verdict

def test_fail_beats_unknown_beats_pass():
    F = panel.Finding
    assert panel.verdict_of([]) == "pass"
    assert panel.verdict_of([F("a", "note", "")]) == "pass"
    assert panel.verdict_of([F("a", "unknown", "")]) == "unknown"
    assert panel.verdict_of([F("a", "unknown", ""), F("b", "fail", "")]) == "fail"


def test_an_unknown_is_not_a_pass_so_it_cannot_merge():
    """Why `unknown` is a verdict rather than a pass with a caveat.

    ADR-13 merges on unanimous pass. A reviewer that could not measure
    something has to block, and the only way to make that true is for its
    inability to be a verdict word the gate does not count as a pass.
    """
    assert "unknown" in panel.Finding.SEVERITIES
    assert panel.verdict_of([panel.Finding("x", "unknown", "")]) != "pass"


# ------------------------------------------------------ duty 3, the markers

def test_a_marker_wrapped_across_two_lines_is_still_a_marker():
    """The reason this is a function and not a grep.

    Five of the nineteen markers in the library today are broken by the prose's
    80-column wrap, and a reviewer built on `grep` would have reported five
    marked passages as unsourced judgment.
    """
    wrapped = "A practical ordering (ours,\nnot the paper's) that follows."
    found, drifted = panel.ours_markers(wrapped)
    assert (found, drifted) == (1, [])


def test_every_marker_phrasing_in_the_library_is_in_the_vocabulary():
    """The check, against the real six skills, which is the whole point of it."""
    for skill in sorted((ROOT / "skills").iterdir()):
        if not skill.is_dir() or skill.name in ("_validation",):
            continue
        raw = (skill / "SKILL.md").read_text()
        _, body = panel.registrar.split_frontmatter(raw)
        found, drifted = panel.ours_markers(body)
        assert not drifted, f"{skill.name} uses {drifted}"


def test_a_drifted_phrasing_is_a_finding_rather_than_a_silent_pass(tmp_path):
    root = write_skill(tmp_path, body=BODY.replace(
        "(ours, not the paper's)", "(ours, not the authors')"))
    verdicts = panel.review(skills_dir=root)
    fails = only(verdicts, check="ours-marked", severity="fail")
    assert len(fails) == 1
    assert "ours, not the authors'" in fails[0]["detail"]


def test_a_passage_with_no_marker_at_all_is_what_this_check_cannot_see(tmp_path):
    """The limit of duty 3 without a model, written down rather than implied.

    The word `ours` is the handle, so the reviewer catches drift in the words
    after it and cannot catch a recommendation that was never marked. Saying so
    in a test is the difference between a known limit and a false pass.
    """
    root = write_skill(tmp_path, body=BODY.replace(
        " (ours, not the paper's)", ""))
    findings = only(panel.review(skills_dir=root), check="ours-marked")
    assert [f["severity"] for f in findings] == ["note"]
    assert findings[0]["detail"].endswith("0")


# ------------------------------------------------------- duty 1, the file half

def test_a_claim_cited_twice_is_a_finding(tmp_path):
    root = write_skill(tmp_path, claims="1, 2, 1")
    fails = only(panel.review(skills_dir=root), check="claim-ids", severity="fail")
    assert len(fails) == 1 and "[1]" in fails[0]["detail"]


def test_a_skill_that_names_no_paper_fails(tmp_path):
    root = write_skill(tmp_path, papers=())
    fails = only(panel.review(skills_dir=root), check="papers-listed", severity="fail")
    assert len(fails) == 1


def test_the_same_paper_listed_twice_fails(tmp_path):
    root = write_skill(tmp_path, papers=(
        "A paper - arxiv.org/abs/2609.09134",
        "The same paper, cited again - arxiv.org/abs/2609.09134v2"))
    fails = only(panel.review(skills_dir=root), check="papers-listed", severity="fail")
    assert len(fails) == 1 and "2609.09134" in fails[0]["detail"]


def test_a_source_with_no_arxiv_id_is_unknown_not_a_defect(tmp_path):
    """A blog post or a handbook is a legitimate source with no id to match."""
    root = write_skill(tmp_path, papers=("An engineering blog post - example.com/post",))
    findings = only(panel.review(skills_dir=root), check="papers-listed")
    assert [f["severity"] for f in findings] == ["unknown"]


def test_the_version_suffix_is_not_part_of_the_id():
    ids, unreadable = panel.paper_sources([
        "One - arxiv.org/abs/2609.09134v3", "Two - nothing here"])
    assert ids == ["2609.09134"] and unreadable == ["Two - nothing here"]


# ------------------------------------------------------- duty 2, undecidable

def test_duty_two_is_unknown_and_says_why(tmp_path):
    """The finding that is the argument for the format change.

    A skill cites its claim ids once for the whole document, so no sentence
    names the claim behind it and "the cited claim supports the sentence citing
    it" has no pair to judge. The reviewer reports that rather than guessing a
    mapping, and the report carries the two numbers that show the size of the
    guess it refused to make.
    """
    root = write_skill(tmp_path)
    findings = only(panel.review(skills_dir=root), check="claim-supports-sentence")
    assert [f["severity"] for f in findings] == ["unknown"]
    assert "2 sections" in findings[0]["detail"]
    assert "2 claim ids" in findings[0]["detail"]


def test_no_skill_in_the_library_can_be_passed_by_this_slice():
    """Stated as a test so the next reader cannot miss it.

    Slice 1 files hard failures and the record. It cannot return `pass`,
    because duty 2 is undecidable against today's format, and that is the
    correct behaviour for a gate that merges on unanimous pass: it blocks.
    """
    verdicts = panel.review()
    assert verdicts, "the library has no skills to review"
    assert {v["verdict"] for v in verdicts} == {"unknown"}


# -------------------------------------------------------- duty 1, the corpus

class FakeConn:
    """Answers the three statements with rows handed to it. Executes nothing."""

    def __init__(self, claims=None, consensus=None):
        self.claims = claims or {}
        self.consensus = consensus or []
        self.inserted = []

    def execute(self, sql, params=()):
        self.last = (sql, params)
        if "from claims" in sql:
            wanted = set(params[0])
            rows = [(cid, pid, url) for cid, (pid, url) in self.claims.items()
                    if cid in wanted]
            return FakeResult(rows)
        if "panel_consensus" in sql:
            return FakeResult(self.consensus)
        if sql.strip().startswith("insert"):
            self.inserted.append(params)
            return FakeResult([(len(self.inserted),)])
        raise AssertionError(f"unexpected statement: {sql}")

    def commit(self):
        self.committed = True


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


def test_a_cited_claim_that_is_not_in_the_corpus_fails(tmp_path):
    """ADR-13's first duty, and the question no run had ever asked.

    The six skills on main cite 131 claim ids and nothing in this repository
    had ever asked Postgres whether those rows exist.
    """
    root = write_skill(tmp_path, claims="1, 2")
    conn = FakeConn(claims={1: ("2609.09134", "https://arxiv.org/abs/2609.09134")})
    verdicts = panel.review(skills_dir=root, conn=conn)
    fails = only(verdicts, check="claims-exist", severity="fail")
    assert len(fails) == 1 and "[2]" in fails[0]["detail"]
    assert verdicts[0]["verdict"] == "fail"


def test_a_claim_whose_paper_the_skill_does_not_list_fails(tmp_path):
    root = write_skill(tmp_path, claims="1")
    conn = FakeConn(claims={1: ("2609.99999", "https://arxiv.org/abs/2609.99999")})
    fails = only(panel.review(skills_dir=root, conn=conn),
                 check="claim-paper-attributed", severity="fail")
    assert len(fails) == 1 and "2609.99999" in fails[0]["detail"]


def test_an_attributed_claim_raises_nothing(tmp_path):
    root = write_skill(tmp_path, claims="1")
    conn = FakeConn(claims={1: ("2609.09134", "https://arxiv.org/abs/2609.09134")})
    verdicts = panel.review(skills_dir=root, conn=conn)
    assert not only(verdicts, check="claim-paper-attributed", severity="fail")
    assert only(verdicts, check="claims-exist", severity="note")


def test_a_claim_from_a_non_arxiv_paper_is_unknown(tmp_path):
    root = write_skill(tmp_path, claims="1")
    conn = FakeConn(claims={1: ("blog-9f2a", "https://example.com/post")})
    findings = only(panel.review(skills_dir=root, conn=conn),
                    check="claim-paper-attributed")
    assert [f["severity"] for f in findings] == ["unknown"]


def test_without_a_database_duty_one_is_unknown_rather_than_assumed(tmp_path):
    root = write_skill(tmp_path)
    findings = only(panel.review(skills_dir=root), check="claims-exist")
    assert [f["severity"] for f in findings] == ["unknown"]


# ------------------------------------------------------ the validated field

def test_an_empty_validated_field_is_honest(tmp_path):
    root = write_skill(tmp_path)
    findings = only(panel.review(skills_dir=root), check="validated-field")
    assert [f["severity"] for f in findings] == ["note"]


def test_a_validated_field_with_no_verdict_behind_it_fails(tmp_path):
    """ADR-38 made that field the panel's. Asserting it without a panel is the
    library making its strongest claim about itself on its own authority."""
    root = write_skill(tmp_path, validated='"2026-09-12 A/B trial: it moved"')
    conn = FakeConn(claims={1: ("2609.09134", "https://arxiv.org/abs/2609.09134"),
                            2: ("2609.09134", "https://arxiv.org/abs/2609.09134")})
    fails = only(panel.review(skills_dir=root, conn=conn),
                 check="validated-field", severity="fail")
    assert len(fails) == 1


def test_a_validated_field_the_panel_passed_is_a_note(tmp_path):
    root = write_skill(tmp_path, slug="fixture-skill",
                       validated='"2026-09-12 A/B trial: it moved"')
    conn = FakeConn(
        claims={1: ("2609.09134", "https://arxiv.org/abs/2609.09134"),
                2: ("2609.09134", "https://arxiv.org/abs/2609.09134")},
        consensus=[("skills/fixture-skill", 3, 3, 0, True, True, None)])
    findings = only(panel.review(skills_dir=root, conn=conn),
                    check="validated-field")
    assert [f["severity"] for f in findings] == ["note"]


def test_the_live_library_has_no_file_half_defect():
    """The gate, over the real six skills, with no database.

    This is the assertion that makes the reviewer worth merging: a skill that
    arrives with a duplicate claim id, an unattributed paper or an unmarked
    judgment turns this red on its own pull request. `skills/**` is in
    checks.yml's paths, so that is the pull request it turns red.
    """
    verdicts = panel.review()
    fails = [f for v in verdicts for f in v["findings"] if f["severity"] == "fail"]
    assert fails == []


# --------------------------------------------------------------- the record

def test_a_filed_verdict_carries_the_sha_and_the_findings(tmp_path):
    root = write_skill(tmp_path)
    verdicts = panel.review(skills_dir=root)
    conn = FakeConn()
    ids = panel.file_verdicts(conn, verdicts, "abc123")
    assert ids == [1]
    target, verdict, findings, target_sha, reviewer_sha = conn.inserted[0]
    assert target == "skills/fixture-skill"
    assert verdict == "unknown"
    assert target_sha == verdicts[0]["target_sha"] and len(target_sha) == 64
    assert reviewer_sha == "abc123"
    assert json.loads(findings), "the findings are the row's payload"
    assert conn.committed


def test_the_findings_column_is_json_the_database_will_take(tmp_path):
    """jsonb, so the payload has to be a string of JSON rather than a dict."""
    root = write_skill(tmp_path)
    conn = FakeConn()
    panel.file_verdicts(conn, panel.review(skills_dir=root), None)
    assert isinstance(conn.inserted[0][2], str)


# ------------------------------------------------------------- the CLI

def test_files_only_exits_two_because_something_was_not_measurable(capsys):
    code = panel.main(["--files-only"])
    out = capsys.readouterr().out
    assert code == 2
    assert "skills reviewed" in out


def test_record_without_the_database_half_is_refused():
    with pytest.raises(SystemExit):
        panel.main(["--files-only", "--record"])


def test_one_skill_can_be_reviewed_alone(capsys):
    panel.main(["--files-only", "--skill", "harness-engineering"])
    out = capsys.readouterr().out
    assert "skills/harness-engineering" in out
    assert "skills/evaluation-integrity" not in out


def test_json_carries_every_finding_including_the_notes(capsys):
    panel.main(["--files-only", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["reviewer"] == "provenance"
    severities = {f["severity"] for v in payload["verdicts"] for f in v["findings"]}
    assert "note" in severities, "the row has to say what was measured"


# -------------------------------------------------------------- the wiring

def test_the_image_carries_the_reviewer():
    """Without this line the daily job imports a file that is not there."""
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    assert '.add_local_file("tools/panel_provenance.py", "/root/panel_provenance.py")' in source


def test_the_review_runs_before_the_early_return():
    """A day with nothing to revise is still a day the evidence is sound or not.

    `run()` returns early when `skills_needing_revision` is empty, which is most
    days. A review added after that line would run almost never, which is the
    merged-but-inert failure this sprint is about.
    """
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    reviewed = source.index("log.extend(reviewed(")
    early = source.index("nothing needs revision today")
    assert reviewed < early
    assert source.index("pending = reg.revisions(conn)") > reviewed


def test_the_owner_alarm_keys_on_the_string_the_pass_prints():
    """One constant, used by the pass and by the notifier, held together here.

    An alarm that greps for a sentence the code no longer prints is an alarm
    that is permanently silent, and nothing about the job would look wrong.
    """
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    assert job.VERDICT_ALARM == "panel verdict failing:"
    assert source.count("VERDICT_ALARM") >= 3
    assert f'{{VERDICT_ALARM}} {{verdict[\'target\']}}' in source


def test_the_job_reviews_the_skills_it_read_from_main():
    """Not the image's copy, which is as old as the last deploy."""
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    assert "rows, problems, skills_root = skills_from_github" in source
    assert "reviewer.review(skills_dir=skills_root, conn=conn," in source


def test_a_dry_run_files_nothing():
    """`preflight` is the gate before a deploy and it must not write a verdict."""
    conn = FakeConn()
    rows, problems = panel.registrar.read_skills()
    log = job.reviewed(conn, rows, problems, ROOT / "skills", dry_run=True)
    assert conn.inserted == []
    assert any("no verdict row was filed" in line for line in log)


def test_the_pass_logs_one_line_per_failing_finding(tmp_path):
    root = write_skill(tmp_path, claims="1, 1")
    rows, problems = panel.registrar.read_skills(root)
    conn = FakeConn(claims={1: ("2609.09134", "https://arxiv.org/abs/2609.09134")})
    log = job.reviewed(conn, rows, problems, root, dry_run=False)
    alarms = [line for line in log if line.startswith(job.VERDICT_ALARM)]
    assert len(alarms) == 1 and "claim-ids" in alarms[0]
    assert conn.inserted, "a real run files the row"


# ------------------------------------------------- the format, as published

def test_a_description_past_the_published_ceiling_fails(tmp_path):
    """agentskills.io/specification, read 2026-10-02: 1024 characters.

    A file past it is rejected by a client that validates it. The library's
    longest description is 994 characters today, so this is 30 characters of
    headroom rather than a hypothetical.
    """
    root = write_skill(tmp_path)
    skill = root / "fixture-skill" / "SKILL.md"
    skill.write_text(skill.read_text().replace(
        "A fixture skill, long enough to look like one.", "x" * 1025))
    fails = only(panel.review(skills_dir=root), check="spec-conformance",
                 severity="fail")
    assert len(fails) == 1 and "1025 characters" in fails[0]["detail"]


def test_the_note_says_how_much_headroom_is_left(tmp_path):
    root = write_skill(tmp_path)
    notes = only(panel.review(skills_dir=root), check="spec-conformance",
                 severity="note")
    assert len(notes) == 1 and "under the ceiling" in notes[0]["detail"]


def test_every_skill_in_the_library_is_within_the_published_limits():
    """The measurement, over the real six, so a revision that crosses the line
    fails on its own pull request instead of on a reader's client."""
    verdicts = panel.review()
    assert not [f for v in verdicts for f in v["findings"]
                if f["check"] == "spec-conformance" and f["severity"] == "fail"]
    headroom = {}
    for verdict in verdicts:
        for finding in verdict["findings"]:
            if finding["check"] == "spec-conformance":
                headroom[verdict["target"]] = finding["detail"]
    assert len(headroom) == len(verdicts), "every skill reports its headroom"


def test_no_skill_on_this_branch_fails_a_file_level_check():
    """The check the queued `--files-only` step cannot be.

    `python3 tools/panel_provenance.py --files-only` exits 2 over the real
    library and always will: duty 2 is structurally `unknown` for every skill
    until the per-section claim id format lands, and the three states are
    `0 nothing wrong`, `1 a finding`, `2 something unmeasurable`. A CI step on
    that command would be red on every pull request forever, which is why item
    18 of docs/agents/pending-workflow-changes.md queues two pytest steps and
    not three commands. This test is the part of it worth having: a skill whose
    provenance block has a real defect fails here, and an honest `unknown`
    does not.
    """
    verdicts = panel.review(conn=None)
    fails = [(v["target"], f["check"], f["detail"])
             for v in verdicts for f in v["findings"]
             if f["severity"] == "fail"]
    assert not fails, fails
    assert verdicts, "the library has no skills to review"
