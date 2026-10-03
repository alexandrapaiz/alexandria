"""ADR-13's adversary: its SQL, its judgments, its threshold, and its wiring.

    python3 -m pytest tests/test_panel_adversary.py -q

This reviewer is harder to test than the first one and the reason is the point
of it. Everything the provenance reviewer decides is in a SKILL.md, so a test
can write the file. Nothing the adversary decides is in a SKILL.md: its whole
input is the claim graph, which lives in production Neon and which no CI job in
this organization can reach. So the tests come in four kinds.

**The SQL.** Parsed with libpg_query, every relation and column resolved
against `db/schema.sql`, the same instrument `tests/test_panel_provenance.py`
and `tests/test_graph_audit.py` use. A migration that renames `interpreted_at`
fails the pull request rather than the daily cron.

**The judgments.** Each one is a pure function of (what a skill cites, what the
corpus says about it), so the graph is written out as rows. Every duty gets the
case that must fail and the case that must not, because a reviewer that fails
everything is as useless as one that passes everything.

**The threshold.** `deprecated_claims` in the schema is where this
organization defines a contradicted claim, and the reviewer reads the same
number. That agreement is asserted against the schema text, so moving one
without the other turns this red.

**The wiring.** It runs in exactly one place and the two halves of that are
both easy to get wrong: the Modal image has to carry three files, and the pass
has to file its own row rather than being folded into the first reviewer's.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import panel                       # noqa: E402
import panel_adversary as adv      # noqa: E402
import skill_registrar as registrar  # noqa: E402
import skill_revision as job       # noqa: E402

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
            columns.add(node.name)
    return relations, columns


def test_the_walker_actually_walks():
    assert len(_walk(_parse(adv.QUERIES["disagreements"]), [])) > 5


@pytest.mark.parametrize("name", sorted(adv.QUERIES))
def test_every_statement_parses(name):
    assert len(_parse(adv.QUERIES[name])) == 1, "one statement per entry"


def test_the_adversary_reads_everything_and_writes_one_table():
    kinds = {name: type(_parse(sql)[0].stmt).__name__
             for name, sql in adv.QUERIES.items()}
    assert kinds["cited"] == "SelectStmt"
    assert kinds["disagreements"] == "SelectStmt"
    assert kinds["file"] == "InsertStmt"
    assert _parse(adv.QUERIES["file"])[0].stmt.relation.relname == "panel_verdicts"
    assert [k for k, v in kinds.items() if v != "SelectStmt"] == ["file"]


def test_every_relation_the_adversary_names_exists():
    relations, _ = _schema_names()
    for name, sql in adv.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in relations, (
                    f"{name} reads {node.relname}, which db/schema.sql does "
                    "not create")


def test_every_column_the_adversary_names_exists():
    _, columns = _schema_names()
    for name, sql in adv.QUERIES.items():
        nodes = _walk(_parse(sql), [])
        defined = set()
        for node in nodes:
            if type(node).__name__ == "ResTarget" and node.name:
                defined.add(node.name)
            if type(node).__name__ == "Alias":
                defined.update(c.sval for c in (node.colnames or ()))
        for node in nodes:
            if type(node).__name__ != "ColumnRef":
                continue
            fields = [f.sval for f in node.fields if hasattr(f, "sval")]
            if not fields:
                continue
            assert fields[-1] in (columns | defined), (
                f"{name} reads a column named {fields[-1]}, which is neither "
                "in db/schema.sql nor defined by the statement itself")


def test_it_files_under_its_own_reviewer_name():
    """A verdict filed as 'provenance' by the adversary would make a panel of
    one read as two agreeing reviewers, which is the one arithmetic error
    `panel_consensus` cannot survive.
    """
    assert "'adversary'" in adv.QUERIES["file"]
    assert "'provenance'" not in adv.QUERIES["file"]
    check = SCHEMA.split("check (reviewer in (")[1].split(")")[0]
    assert "'adversary'" in check, "the schema does not admit this reviewer"


def test_it_does_not_search_for_supporting_claims():
    """ADR-13 asks for disagreement, not for completeness.

    A `supports` edge the draft did not cite is a claim the skill could have
    used, which is a different and much weaker finding. Including it would turn
    every skill in the library into a fail on the day the corpus grew.
    """
    sql = adv.QUERIES["disagreements"]
    assert "'contradicts'" in sql and "'refines'" in sql and "'duplicates'" in sql
    assert "'supports'" not in sql


def test_it_reads_the_edges_pointing_at_what_the_skill_cites():
    """ADR-10 fixes the direction: from_claim is always the newer claim.

    Reading `from_claim = any(...)` instead would find what the skill's own
    evidence judged, which is the past rather than the future, and the reviewer
    would report a clean graph on a skill the corpus had since overturned.
    """
    sql = adv.QUERIES["disagreements"]
    assert "l.to_claim = any" in sql
    assert "l.from_claim = any" not in sql




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
    stmt = _parse(adv.QUERIES["file"])[0].stmt
    assert stmt.cols, "the INSERT names no columns, so the order is positional"
    for col in stmt.cols:
        assert col.name in columns, (
            f"this reviewer writes panel_verdicts.{col.name}, which "
            "db/schema.sql does not define")
    values = stmt.selectStmt.valuesLists[0]
    assert len(stmt.cols) == len(values), (
        f"{len(stmt.cols)} columns and {len(values)} values, so the row would be written into the wrong columns or not at all")


# ------------------------------------------------------- the threshold

def test_the_confidence_line_is_the_schema_s_own():
    """One question, one answer.

    `deprecated_claims` is where this organization defines a contradicted
    claim, and `skills_needing_revision` is that view joined against what
    skills cite, which is what queues a revision. A reviewer with its own
    threshold would fail skills the revision queue never queues, or pass
    skills it does.
    """
    view = SCHEMA.split("create or replace view deprecated_claims as")[1]
    view = view.split(";")[0]
    assert "confidence, 0) >= 0.7" in view
    assert adv.CONTRADICTION_CONFIDENCE == 0.7


# ------------------------------------------------------- the judgments

class Row:
    """The two fields of a registrar row the adversary reads."""

    def __init__(self, claim_ids, slug="fixture"):
        self.claim_ids = list(claim_ids)
        self.slug = slug
        self.path = f"skills/{slug}"
        self.sha = "0" * 64


def edge(to_claim, from_claim, relation, confidence=0.9, claim="newer evidence",
         paper_id="2509.00001"):
    return {"to_claim": to_claim, "from_claim": from_claim,
            "relation": relation, "confidence": confidence, "claim": claim,
            "paper_id": paper_id, "created_at": None}


def interpreted(*ids, grade="controlled"):
    return {i: {"interpreted_at": "2026-10-01", "evidence_grade": grade}
            for i in ids}


def severities(findings, check=None):
    return [f.severity for f in findings
            if check is None or f.check == check]


def test_a_contradiction_the_draft_ignored_fails():
    row = Row([10, 11])
    findings = adv.contradicted(row, [edge(10, 99, "contradicts", 0.9,
                                           "the opposite is true")])
    fails = [f for f in findings if f.severity == "fail"]
    assert len(fails) == 1
    assert fails[0].check == "contradiction-ignored"
    assert "claim 99" in fails[0].detail
    assert "the opposite is true" in fails[0].detail, (
        "a finding that does not say what the contradicting claim found sends "
        "a reader to the database")


def test_a_contradiction_below_the_threshold_is_evidence_and_not_a_defect():
    row = Row([10])
    findings = adv.contradicted(row, [edge(10, 99, "contradicts", 0.4)])
    assert severities(findings) == ["note"]
    assert "0.7" in findings[0].detail


def test_citing_both_sides_of_a_contradiction_is_unknown_not_a_pass():
    """The format cannot say whether the skill discusses the disagreement."""
    row = Row([10, 99])
    findings = adv.contradicted(row, [edge(10, 99, "contradicts", 0.9)])
    unknowns = [f for f in findings if f.severity == "unknown"]
    assert len(unknowns) == 1
    assert unknowns[0].check == "contradiction-both-cited"
    assert "fail" not in severities(findings)


def test_a_clean_graph_passes_and_says_it_looked():
    row = Row([10])
    findings = adv.contradicted(row, [])
    assert severities(findings) == ["note"]
    assert adv.verdict_of(findings) == "pass"
    assert "no contradicting edge" in findings[0].detail


def test_a_refinement_the_draft_ignored_fails_and_says_it_is_out_of_date():
    row = Row([10])
    findings = adv.refined(row, [edge(10, 77, "refines")])
    fails = [f for f in findings if f.severity == "fail"]
    assert len(fails) == 1 and fails[0].check == "refinement-ignored"
    assert "out of date rather than wrong" in fails[0].detail


def test_a_refinement_the_draft_cites_is_acknowledged_and_not_a_defect():
    row = Row([10, 77])
    findings = adv.refined(row, [edge(10, 77, "refines")])
    assert severities(findings) == ["note"]


def test_the_refinement_severity_is_one_line_the_owner_can_soften():
    """The docstring promises this, so the promise is checked."""
    assert adv.SEVERITY == {"contradicts": "fail", "refines": "fail"}
    row = Row([10])
    adv.SEVERITY["refines"] = "note"
    try:
        assert severities(adv.refined(row, [edge(10, 77, "refines")])) == ["note"]
    finally:
        adv.SEVERITY["refines"] = "fail"


def test_an_uninterpreted_claim_blocks_instead_of_reading_as_agreement():
    """The most dangerous output this reviewer could produce.

    A claim with `interpreted_at` null has no edges because nothing ever looked
    at it. Reporting that as a pass would turn "the graph was never asked" into
    "the graph agrees", and the claim graph has stalled twice in this product's
    life.
    """
    row = Row([10, 11])
    cited = {10: {"interpreted_at": "2026-10-01", "evidence_grade": "controlled"},
             11: {"interpreted_at": None, "evidence_grade": None}}
    findings = adv.searchable(row, cited)
    unknowns = [f for f in findings if f.severity == "unknown"]
    assert len(unknowns) == 1
    assert "[11]" in unknowns[0].detail
    assert "never asked" in unknowns[0].detail
    assert adv.verdict_of(findings) == "unknown"


def test_a_cited_id_with_no_claim_row_is_unknown_and_credited_to_duty_one():
    """The defect is the provenance reviewer's. Reporting it as this
    reviewer's own fail would make one defect look like two.
    """
    row = Row([10, 4242])
    findings = adv.searchable(row, interpreted(10))
    unknowns = [f for f in findings if f.severity == "unknown"]
    assert len(unknowns) == 1
    assert "[4242]" in unknowns[0].detail
    assert "duty 1" in unknowns[0].detail


def test_a_fully_interpreted_skill_is_searchable_and_says_how_far():
    row = Row([10, 11])
    findings = adv.searchable(row, interpreted(10, 11))
    assert severities(findings) == ["note"]
    assert "2 of 2" in findings[0].detail


def test_duplicate_claims_narrow_the_evidence_without_failing_the_skill():
    row = Row([10, 11, 12])
    findings = adv.breadth(row, [edge(10, 11, "duplicates")])
    assert severities(findings) == ["note"]
    assert "about 2 distinct findings" in findings[0].detail


def test_breadth_ignores_a_duplicate_of_a_claim_the_skill_does_not_cite():
    """A duplicate outside the citation list does not shrink the list."""
    row = Row([10])
    findings = adv.breadth(row, [edge(10, 11, "duplicates")])
    assert "none of them duplicates" in findings[0].detail


def test_the_evidence_grades_are_recorded_and_never_graded():
    row = Row([10, 11, 12])
    cited = {10: {"interpreted_at": "x", "evidence_grade": "controlled"},
             11: {"interpreted_at": "x", "evidence_grade": "anecdote"}}
    findings = adv.grades(row, cited)
    assert severities(findings) == ["note"], (
        "no register sets a bar for evidence grade, so a verdict here would be "
        "this reviewer legislating")
    assert "1 anecdote" in findings[0].detail
    assert "1 controlled" in findings[0].detail
    assert "1 ungraded" in findings[0].detail
    assert "no measurement behind them" in findings[0].detail


def test_a_quote_is_short_enough_to_read_in_a_log_line():
    long = edge(1, 2, "contradicts", claim="x" * 400)
    assert len(adv.quote(long)) < 160
    assert adv.quote(long).endswith("...'")
    assert "claim 2" in adv.quote(long)


def test_every_character_a_finding_can_print_is_ascii():
    """These findings reach the owner's alarm mail, and entry 13 of
    docs/voice/ban-list.md is the whole class of non-ASCII characters in
    anything she reads. The truncation marker is the one this file nearly
    shipped as a single-character ellipsis.
    """
    row = Row([10])
    findings = (adv.contradicted(row, [edge(10, 99, "contradicts", 0.9,
                                            "x" * 400)])
                + adv.refined(row, [edge(10, 77, "refines")])
                + adv.breadth(row, [edge(10, 11, "duplicates")])
                + adv.grades(row, interpreted(10))
                + adv.searchable(row, {}))
    for finding in findings:
        finding.detail.encode("ascii")
    source = (ROOT / "tools" / "panel_adversary.py").read_text()
    source.encode("ascii")


def test_a_wrapped_claim_reads_as_one_line():
    wrapped = edge(1, 2, "contradicts", claim="two\n  words")
    assert "'two words'" in adv.quote(wrapped)


# --------------------------------------------- the reviewer over a library

class FakeConn:
    """A graph, written out, answering the two SELECTs the reviewer sends."""

    def __init__(self, cited, edges):
        self.cited, self.edges = cited, edges
        self.inserted = []

    def execute(self, sql, params):
        if "from claim_links" in sql:
            ids = set(params[0])
            rows = [(e["to_claim"], e["from_claim"], e["relation"],
                     e["confidence"], e["claim"], e["paper_id"],
                     e["created_at"])
                    for e in self.edges if e["to_claim"] in ids]
            return _Result(rows)
        if "from claims" in sql:
            ids = set(params[0])
            rows = [(i, v["interpreted_at"], v["evidence_grade"])
                    for i, v in self.cited.items() if i in ids]
            return _Result(rows)
        self.inserted.append(params)
        return _Result([(len(self.inserted),)])

    def commit(self):
        pass


class _Result:
    def __init__(self, rows):
        self.rows = rows

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0]


def test_the_whole_reviewer_over_a_library_with_one_overturned_skill():
    """End to end through `review()`, which is what the daily job calls."""
    rows = [Row([10, 11], slug="sound"), Row([20], slug="overturned")]
    conn = FakeConn(interpreted(10, 11, 20),
                    [edge(20, 99, "contradicts", 0.95, "the opposite")])
    verdicts = adv.review(rows=rows, conn=conn)
    by_target = {v["target"]: v for v in verdicts}
    assert by_target["skills/sound"]["verdict"] == "pass"
    assert by_target["skills/overturned"]["verdict"] == "fail"
    assert all(v["reviewer"] == "adversary" for v in verdicts)
    assert all(v["target_sha"] for v in verdicts)


def test_without_a_connection_every_verdict_is_unknown_and_says_why():
    """There is no reduced check. A pass here would be a lie about the graph."""
    verdicts = adv.review(rows=[Row([10])], conn=None)
    assert verdicts[0]["verdict"] == "unknown"
    detail = verdicts[0]["findings"][0]["detail"]
    assert "no database credential" in detail
    assert "no reduced check" in detail


def test_the_registrar_s_problems_are_not_repeated_by_this_reviewer():
    """One defect must not read as two independent findings."""
    verdicts = adv.review(rows=[Row([10])], conn=None,
                          problems=["skills/fixture/SKILL.md is broken"])
    assert not any("broken" in f["detail"] for f in verdicts[0]["findings"])


def test_the_live_library_is_reviewable_and_every_id_is_searched():
    """A reviewer that only works on fixtures is a reviewer nobody can read."""
    live, _ = registrar.read_skills()
    assert live, "the library has no skills to review"
    verdicts = adv.review(rows=live, conn=None)
    assert len(verdicts) == len(live)
    for row, verdict in zip(live, verdicts):
        assert str(len(row.claim_ids)) in verdict["findings"][0]["detail"]


# ----------------------------------------------------------- independence

def test_neither_reviewer_imports_the_other():
    """ADR-13's reviewers are independent samples, not a pipeline.

    They share the verdict vocabulary in tools/panel.py on purpose, because
    `panel_consensus` counts passes across them. They must not share a
    judgment, and an import is the cheapest way for one to start.
    """
    adversary = (ROOT / "tools" / "panel_adversary.py").read_text()
    provenance = (ROOT / "tools" / "panel_provenance.py").read_text()
    assert "import panel_provenance" not in adversary
    assert "import panel_adversary" not in provenance
    assert "import panel" in adversary and "import panel" in provenance


def test_the_shared_vocabulary_holds_no_judgment():
    """tools/panel.py is the scale, not a reviewer.

    If a check ever lands in there, both reviewers would make it and
    `panel_consensus` would count one finding twice as two agreeing reviewers.
    """
    shared = (ROOT / "tools" / "panel.py").read_text()
    for word in ("claim_ids", "claim_links", "provenance.papers", "SKILL.md"):
        assert word not in shared, f"tools/panel.py mentions {word}"


def test_the_severities_are_one_set_for_the_whole_panel():
    assert adv.Finding is panel.Finding
    assert panel.Finding.SEVERITIES == ("fail", "unknown", "note")


# ----------------------------------------------------------- the wiring

def test_the_image_carries_both_reviewers_and_what_they_share():
    """The adversary runs in exactly one place, so the image is the only
    delivery path it has. A missing line here is an ImportError at 16:00 UTC.
    """
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    for name in ("panel.py", "panel_provenance.py", "panel_adversary.py"):
        assert f'.add_local_file("tools/{name}", "/root/{name}")' in source


def test_both_reviewers_run_in_the_daily_job_before_the_early_return():
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    first = source.index("log.extend(reviewed(")
    second = source.index("log.extend(adversary_reviewed(")
    early = source.index("if not pending:")
    assert first < second < early
    assert source.index("pending = reg.revisions(conn)") > second


def test_each_reviewer_files_its_own_row():
    """A pass that merged two reviewers' findings into one row would make a
    panel of two read as a panel of one to `panel_consensus`.
    """
    rows = [Row([10], slug="one")]
    conn = FakeConn(interpreted(10), [])
    log = job.adversary_reviewed(conn, rows, [], ROOT / "skills", dry_run=False)
    assert len(conn.inserted) == 1
    assert conn.inserted[0][1] == "pass"
    assert any(line.startswith("adversary: 1 skills reviewed") for line in log)


def test_a_dry_run_files_nothing():
    conn = FakeConn(interpreted(10), [])
    log = job.adversary_reviewed(conn, [Row([10])], [], ROOT / "skills",
                                 dry_run=True)
    assert conn.inserted == []
    assert any("no verdict row was filed" in line for line in log)


def test_an_adversary_fail_reaches_the_owner_alarm():
    """Same marker as the provenance reviewer's, because the mail is one mail
    and the log line names which reviewer failed.
    """
    conn = FakeConn(interpreted(10),
                    [edge(10, 99, "contradicts", 0.95, "the opposite")])
    log = job.adversary_reviewed(conn, [Row([10])], [], ROOT / "skills",
                                 dry_run=False)
    alarms = [line for line in log if line.startswith(job.VERDICT_ALARM)]
    assert len(alarms) == 1 and "contradiction-ignored" in alarms[0]
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    assert "python3 tools/panel_adversary.py" in source, (
        "the alarm mail has to name a command that diagnoses an adversary "
        "finding, and --files-only is not one")


def test_the_adversary_has_no_files_only_mode_and_ci_never_runs_the_reviewer():
    """A green CI step that ran this reviewer would read as the graph agreeing,
    when all it could mean is that nobody asked the graph.

    Its *tests* are a different thing and belong in CI: they are how the SQL
    above is resolved against db/schema.sql, which is the only place that can
    happen. So what is forbidden is the command, not the filename.
    """
    assert not hasattr(adv, "review_file")
    with pytest.raises(SystemExit):
        adv.main(["--files-only"])
    workflow = (ROOT / ".github" / "workflows" / "checks.yml").read_text()
    assert "tools/panel_adversary.py" not in workflow, (
        "checks.yml runs the adversary, and CI holds no database credential, "
        "so the step can only ever report that nobody asked the graph")


def test_the_reviewer_sha_is_the_sha_git_would_give():
    """The column exists so a verdict says which reviewer code judged.

    Asking git for it made the column null on every row that will ever exist
    in production, because the Modal image carries the reviewer's file and not
    the repository. Hashing the bytes in git's blob format needs no repository
    and gives the same number, so this asserts the two agree on the real file.
    """
    import subprocess

    for name in ("tools/panel.py", "tools/panel_provenance.py",
                 "tools/panel_adversary.py"):
        expected = subprocess.run(["git", "hash-object", name], cwd=ROOT,
                                  capture_output=True, text=True, check=True)
        assert panel.reviewer_sha(name) == expected.stdout.strip(), name


def test_the_reviewer_sha_is_found_the_way_the_image_lays_the_files_out():
    """In the container the file is `/root/panel_adversary.py`, with no
    `tools/` above it and no repository anywhere. The basename lookup beside
    this module is what makes the same call work in both places.
    """
    assert panel.reviewer_sha("anywhere/at/all/panel_adversary.py") == \
        panel.reviewer_sha("tools/panel_adversary.py")
    assert panel.reviewer_sha("tools/not_a_reviewer.py") is None


def test_both_reviewers_file_a_sha_rather_than_a_null():
    for module in (adv, __import__("panel_provenance")):
        assert module.reviewer_sha(), f"{module.REVIEWER} files a null sha"
