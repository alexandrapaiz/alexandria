"""The graph audit: its SQL, its bounds, and its precision arithmetic.

    python3 -m pytest tests/test_graph_audit.py -q

No database runs anywhere in this org's CI, and `tools/graph_audit.py` is a
database tool, so this file splits the problem the way the tool is built to be
split. Everything downstream of `_rows()` is pure, and those functions are
exercised here on handwritten snapshots. The SQL itself is checked by parsing
it with libpg_query, the same parser the server uses, and by resolving every
relation and column it names against `db/schema.sql`. That catches the failure
this file exists for, which is a statement that is only ever run for the first
time in production.

What it cannot catch is a query that parses, resolves, and answers the wrong
question. That is what the design doc's worked example is for.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import graph_audit as ga  # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# ------------------------------------------------------------------ the SQL

def _walk(node, out):
    """Every AST node under `node`, pglast's tree being tuples and nodes."""
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
    """(relations, columns) as libpg_query reads db/schema.sql.

    Columns come from CREATE TABLE and from the ALTER TABLE ADD COLUMN
    migrations further down the file, which is where half of this schema's
    columns actually live.
    """
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
    return relations, columns


@pytest.mark.parametrize("name", sorted(ga.QUERIES))
def test_every_query_parses_and_only_reads(name):
    """A typo fails the pull request, not the run. And nothing here writes.

    The audit is pointed at the production corpus by whoever holds the
    credential, so "it only selects" has to be a checked property rather than a
    promise in a docstring.
    """
    statements = _parse(ga.QUERIES[name])
    assert len(statements) == 1, "one query per entry, so one failure per name"
    assert type(statements[0].stmt).__name__ == "SelectStmt"


def test_every_relation_the_audit_names_exists():
    schema_relations, _ = _schema_names()
    for name, sql in ga.QUERIES.items():
        for node in _walk(_parse(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in schema_relations, (
                    f"{name} reads {node.relname}, which db/schema.sql does "
                    "not create")


def test_every_column_the_audit_names_exists():
    """Schema columns, plus the names each query defines for itself.

    The second half matters: `o.neighbors` and `n.distance` are invented by the
    laterals that produce them, so an allow-list of schema columns alone would
    reject the real query. Aliases are collected per query, which keeps one
    query's invention from excusing another query's typo.
    """
    _, schema_columns = _schema_names()
    for name, sql in ga.QUERIES.items():
        nodes = _walk(_parse(sql), [])
        defined = set()
        for node in nodes:
            kind = type(node).__name__
            if kind == "ResTarget" and node.name:
                defined.add(node.name)
            if kind == "Alias":
                defined.update(c.sval for c in (node.colnames or ()))
        allowed = schema_columns | defined
        for node in nodes:
            if type(node).__name__ != "ColumnRef":
                continue
            fields = [f.sval for f in node.fields if hasattr(f, "sval")]
            if not fields:                      # count(*), an A_Star
                continue
            assert fields[-1] in allowed, (
                f"{name} reads a column named {fields[-1]}, which is neither "
                "in db/schema.sql nor defined by the query itself")


def test_the_sample_query_draws_the_same_edges_for_one_seed():
    """The ordering is a hash of the seed and the edge's own key, not random().

    This is what makes a second audit a re-measurement rather than a new
    sample, so it is worth asserting against the text: `random()` here would
    look identical in a code review and quietly destroy every before-and-after
    comparison the upgrade depends on.
    """
    sample = ga.QUERIES["sample"]
    assert "order by md5(" in sample
    assert "random()" not in sample
    assert "from_claim" in sample and "to_claim" in sample and "relation" in sample


# ------------------------------------------------------------ the snapshots

NOW = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)


def snapshot(**overrides):
    """A small, healthy graph. Every test below breaks exactly one thing in it."""
    raw = {
        "collected_at": NOW.isoformat(),
        "seed": "alexandria",
        "shape": {"claims": 100, "interpreted": 80, "unembedded": 4,
                  "edges": 120, "papers": 30,
                  "newest_edge": (NOW - timedelta(hours=6)).isoformat(),
                  "oldest_edge": "2026-09-17T02:00:00+00:00"},
        "degrees": {"interpreted": 80, "no_out": 12, "isolated": 8,
                    "at_ceiling": 4, "median_out": 1, "p90_out": 3, "max_out": 5},
        "relations": [{"relation": "supports", "edges": 70, "unscored": 0,
                       "mean_confidence": 0.82},
                      {"relation": "refines", "edges": 30, "unscored": 0,
                       "mean_confidence": 0.71},
                      {"relation": "contradicts", "edges": 12, "unscored": 0,
                       "mean_confidence": 0.75},
                      {"relation": "duplicates", "edges": 8, "unscored": 0,
                       "mean_confidence": 0.9}],
        "confidence": [{"value": "0.80", "edges": 40},
                       {"value": "0.90", "edges": 35},
                       {"value": "0.70", "edges": 30},
                       {"value": "0.60", "edges": 15}],
        "integrity": {"self_edges": 0, "backwards": 0, "unattributed": 0,
                      "self_contradictory": 0},
        "provenance": {"edges": 120, "same_paper": 24},
        "contradiction": {"edges": 12, "confident": 9,
                          "claims_contradicted": 11, "deprecated": 11},
        "judges": [{"method": "kimi-k2.6@abc123def456", "edges": 120,
                    "first_edge": "2026-09-26T14:00:00+00:00",
                    "last_edge": (NOW - timedelta(hours=6)).isoformat()}],
        "dedup": {"sampled": 200, "near_duplicates": 14, "unmarked": 9},
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(raw.get(key), dict):
            raw[key] = {**raw[key], **value}
        else:
            raw[key] = value
    return raw


def read(metrics, name):
    return next(m for m in metrics if m.name == name)


def test_a_healthy_graph_reads_clean_and_exits_zero():
    metrics = ga.analyze(snapshot(), now=NOW)
    offenders = [(m.name, m.state, m.headline)
                 for m in metrics if m.state != ga.OK]
    assert offenders == []
    assert ga.exit_code(metrics) == 0


def test_isolation_is_measured_in_both_directions():
    """A claim whose judge drew nothing may still be judged BY a later claim.

    `no_out` is 12 and `isolated` is 8 in the healthy snapshot, so this is the
    difference the metric has to respect: four of those claims are in the graph,
    they were simply written before the claims that relate to them.
    """
    clean = read(ga.analyze(snapshot(), now=NOW), "isolation")
    assert clean.evidence["isolated"] == 8
    assert clean.evidence["no_outgoing"] == 12
    assert clean.evidence["share"] == 0.1

    lonely = read(ga.analyze(
        snapshot(degrees={"isolated": 40, "no_out": 50}), now=NOW), "isolation")
    assert lonely.state == ga.FAILING
    assert "50.0 percent" in lonely.headline


def test_the_shortlist_ceiling_catches_a_constant_setting_the_density():
    at_ceiling = read(ga.analyze(
        snapshot(degrees={"at_ceiling": 30}), now=NOW), "shortlist ceiling")
    assert at_ceiling.state == ga.FAILING
    assert at_ceiling.evidence["shortlist"] == ga.SHORTLIST == 5
    assert "NEIGHBORS" in at_ceiling.headline


def test_a_judge_that_writes_one_confidence_fails_calibration():
    """The failure this catches is the one the graph is most likely to have.

    A model asked for a confidence and given no rubric tends to answer 0.9 to
    everything, and `deprecated_claims` gates on 0.7. So a flat score does not
    merely look unscientific: it decides the Left-Behind Index by a constant.
    """
    flat = read(ga.analyze(
        snapshot(confidence=[{"value": "0.90", "edges": 115},
                             {"value": "0.80", "edges": 5}]),
        now=NOW), "confidence calibration")
    assert flat.state == ga.FAILING
    assert flat.evidence["modal_value"] == "0.90"
    assert flat.evidence["distinct_values"] == 2


def test_same_paper_edges_are_counted_as_their_own_defect():
    inbred = read(ga.analyze(
        snapshot(provenance={"same_paper": 90}), now=NOW), "same-paper edges")
    assert inbred.state == ga.FAILING
    assert "same paper" in inbred.headline


def test_unmarked_near_duplicates_are_the_dedup_number():
    dupes = read(ga.analyze(
        snapshot(dedup={"sampled": 200, "near_duplicates": 60, "unmarked": 55}),
        now=NOW), "duplicate rate")
    assert dupes.state == ga.FAILING
    assert dupes.evidence["share"] == 0.275
    # Marked duplicates are not the defect. Five of the sixty were caught.
    assert dupes.evidence["near_duplicates"] - dupes.evidence["unmarked"] == 5


@pytest.mark.parametrize("field,phrase", [
    ("self_edges", "related to itself"),
    ("backwards", "ADR-10 forbids"),
    ("unattributed", "no judge owns it"),
    ("self_contradictory", "both supports and contradicts"),
])
def test_every_integrity_count_is_a_defect_at_any_value(field, phrase):
    metric = read(ga.analyze(snapshot(integrity={field: 3}), now=NOW),
                  "integrity")
    assert metric.state == ga.FAILING
    assert phrase in metric.headline


def test_freshness_reads_the_newest_edge_against_the_daily_cron():
    stale = read(ga.analyze(
        snapshot(shape={"newest_edge": (NOW - timedelta(days=5)).isoformat()}),
        now=NOW), "freshness")
    assert stale.state == ga.FAILING
    assert "5.0 days old" in stale.headline

    never = read(ga.analyze(snapshot(shape={"newest_edge": None}), now=NOW),
                 "freshness")
    assert never.state == ga.UNKNOWN


def test_an_empty_graph_reports_rather_than_dividing_by_zero():
    """The state on the day the audit first runs against a fresh database.

    Nothing here is `ok`, because nothing here was measured, and a tool that
    printed a clean bill of health for an empty table would be worse than no
    tool.
    """
    empty = snapshot(
        shape={"claims": 0, "interpreted": 0, "edges": 0, "papers": 0,
               "unembedded": 0, "newest_edge": None, "oldest_edge": None},
        degrees={"interpreted": 0, "no_out": 0, "isolated": 0, "at_ceiling": 0,
                 "median_out": None, "p90_out": None, "max_out": None},
        relations=[], confidence=[], judges=[],
        provenance={"edges": 0, "same_paper": 0},
        contradiction={"edges": 0, "confident": 0, "claims_contradicted": 0,
                       "deprecated": 0},
        dedup={"sampled": 0, "near_duplicates": 0, "unmarked": 0})
    metrics = ga.analyze(empty, now=NOW)
    assert ga.exit_code(metrics) == 2
    assert read(metrics, "isolation").state == ga.UNKNOWN
    assert read(metrics, "relation mix").headline == "no edges at all"


def test_the_contradiction_metric_names_the_confidence_gate():
    """The number the Left-Behind Index is made of, and the one above it.

    Twelve contradicts edges and eleven deprecated claims is a healthy read.
    Twelve and zero is a page that renders empty for a calibration reason, and
    the two look identical from the page itself.
    """
    metric = read(ga.analyze(
        snapshot(contradiction={"confident": 0, "deprecated": 0}), now=NOW),
        "contradiction coverage")
    assert "12 contradicts edges" in metric.headline
    assert "0 claims on the Left-Behind Index" in metric.headline


# ----------------------------------------------------------- the worksheet

SHEET_ROWS = [
    {"from_claim": 9, "to_claim": 4, "relation": "supports", "confidence": 0.9},
    {"from_claim": 9, "to_claim": 5, "relation": "supports", "confidence": 0.9},
    {"from_claim": 8, "to_claim": 2, "relation": "contradicts", "confidence": 0.75},
    {"from_claim": 7, "to_claim": 1, "relation": "refines", "confidence": None},
]


def test_a_worksheet_ships_blank_verdicts_and_its_own_instructions():
    sheet = ga.worksheet(SHEET_ROWS, seed="alexandria", size=4)
    assert [e["verdict"] for e in sheet["edges"]] == [None] * 4
    assert all(word in sheet["instructions"] for word in ga.VERDICTS)
    # The rows are copied, never aliased: filling in a verdict must not reach
    # back into whatever the caller still holds.
    assert all("verdict" not in row for row in SHEET_ROWS)
    json.dumps(sheet)                       # it is a file, so it must serialize


def test_precision_excludes_unsure_from_the_denominator():
    sheet = ga.worksheet(SHEET_ROWS, "alexandria", 4)
    for edge, verdict in zip(sheet["edges"],
                             ["correct", "wrong", "correct", "unsure"]):
        edge["verdict"] = verdict
    result = ga.precision(sheet)

    assert result["labelled"] == 4
    assert result["overall"] == {"correct": 2, "wrong": 1, "unsure": 1,
                                "precision": round(2 / 3, 3)}
    assert result["by_relation"]["supports"]["precision"] == 0.5
    assert result["by_relation"]["contradicts"]["precision"] == 1.0
    # One unsure and nothing else judged is not precision 0. It is no answer.
    assert result["by_relation"]["refines"]["precision"] is None


def test_precision_bands_confidence_so_calibration_is_readable():
    """0.9 and 0.75 are different bands, and an unscored edge is its own bucket."""
    sheet = ga.worksheet(SHEET_ROWS, "alexandria", 4)
    for edge, verdict in zip(sheet["edges"],
                             ["correct", "wrong", "correct", "correct"]):
        edge["verdict"] = verdict
    bands = ga.precision(sheet)["by_confidence"]

    assert set(bands) == {"0.9-1.0", "0.7-0.8", "unscored"}
    assert bands["0.9-1.0"]["precision"] == 0.5
    assert bands["0.7-0.8"]["precision"] == 1.0
    assert bands["unscored"]["precision"] == 1.0


def test_an_unlabelled_sheet_reports_nothing_rather_than_perfect():
    result = ga.precision(ga.worksheet(SHEET_ROWS, "alexandria", 4))
    assert result["labelled"] == 0
    assert result["overall"]["precision"] is None


def test_a_misspelled_verdict_raises_instead_of_being_counted_wrong():
    sheet = ga.worksheet(SHEET_ROWS, "alexandria", 4)
    sheet["edges"][0]["verdict"] = "Correct"
    with pytest.raises(ValueError, match="verdict must be one of"):
        ga.precision(sheet)


# --------------------------------------------------------------- the driver

def test_no_credential_is_unknown_and_exit_two(monkeypatch, capsys):
    """The state in every seat sandbox today, and it must not read as green."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert ga.main([]) == 2
    out = capsys.readouterr().out
    assert "DATABASE_URL" in out
    assert "not a clean report" in out


def test_a_snapshot_can_be_audited_without_a_database(tmp_path, capsys):
    """How a reader without the credential checks the reading of a graph.

    Whoever can reach Neon runs `--json --raw` and commits the snapshot. Anyone
    can then run the bounds against it, which is what makes the audit reviewable
    by the seats that will never hold a password.
    """
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(snapshot(degrees={"isolated": 60})))
    assert ga.main(["--snapshot", str(path)]) == 1
    assert "FAILING" in capsys.readouterr().out


def test_json_raw_round_trips_the_snapshot(tmp_path, capsys):
    path = tmp_path / "snapshot.json"
    path.write_text(json.dumps(snapshot()))
    ga.main(["--snapshot", str(path), "--json", "--raw"])
    assert json.loads(capsys.readouterr().out)["shape"]["claims"] == 100
