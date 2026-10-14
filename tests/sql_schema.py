"""Resolve the SQL a JavaScript module runs against db/schema.sql.

Not collected by pytest, which only picks up `test_*.py`. Imported by
tests/test_waitlist.py and tests/test_unsubscribe.py.

This org runs no Postgres in CI and the only Postgres that matters is the
production one, so a statement inside a serverless route is otherwise executed
for the first time by a stranger using the site. libpg_query is the server's
own parser, so parsing each statement and resolving every relation and column
it names against `db/schema.sql` is the strongest check available without a
database. It catches the two failures that actually happen: a typo, and a
column that was added to the insert and not to the schema.

`tools/graph_audit.py`'s suite (tests/test_graph_audit.py) does the same thing
with its own copy of these helpers, written first and deliberately left alone.
It is one of the steps in `checks.yml`, its queries are a dict in Python rather
than template literals in JavaScript, and churn in a guard that is green is
worth less than the duplication costs.

What none of this catches is a statement that parses, resolves, and asks the
wrong question. That is what the tests around these helpers are for.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (ROOT / "db" / "schema.sql").read_text()


def walk(node, out=None):
    """Every AST node under `node`, pglast's tree being tuples and nodes."""
    ast = pytest.importorskip("pglast").ast
    out = [] if out is None else out
    if isinstance(node, ast.Node):
        out.append(node)
        for slot in node.__slots__:
            walk(getattr(node, slot, None), out)
    elif isinstance(node, (list, tuple)):
        for item in node:
            walk(item, out)
    return out


def schema_names():
    """(relations, columns) as libpg_query reads db/schema.sql.

    Columns come from CREATE TABLE and from the ALTER TABLE ADD COLUMN
    migrations further down the file, which is where half of this schema's
    columns live.
    """
    pglast = pytest.importorskip("pglast")
    relations, columns = set(), set()
    for node in walk(pglast.parse_sql(SCHEMA)):
        name = type(node).__name__
        if name in ("CreateStmt", "ViewStmt"):
            rel = getattr(node, "relation", None) or getattr(node, "view", None)
            if rel is not None:
                relations.add(rel.relname)
        if name == "ColumnDef" and node.colname:
            columns.add(node.colname)
    return relations, columns


def literals(source: str) -> dict[str, str]:
    """Every `sql`...`` template literal in a JavaScript module, by name.

    Named by the `const` it is assigned to where there is one, and otherwise by
    the order it appears, so that a statement written inline is still collected
    and still has to pass. A tagged template is the driver's parameter binding,
    so `${row.email}` reaches the server as a placeholder and never as text,
    and `$1` is what the server actually sees.
    """
    code = strip_comments(source)
    found: dict[str, str] = {}
    for name, body in re.findall(
            r"const (\w+) =(?: \(\w+(?:, \w+)*\) =>)? sql`(.*?)`", code, re.S):
        found[name] = placeholders(body)
    named = set(found.values())
    inline = 0
    for body in re.findall(r"(?:await|return) sql`(.*?)`", code, re.S):
        statement = placeholders(body)
        if statement not in named:
            inline += 1
            found[f"INLINE_{inline}"] = statement
    return found


def placeholders(body: str) -> str:
    return re.sub(r"\$\{[^}]*\}", "$1", body)


def strip_comments(text: str) -> str:
    """The file with its `//` comments removed.

    Several assertions in both suites are about what the code does and would
    otherwise be satisfied, or broken, by a comment that merely quotes the
    thing. The signup helper's comment names the JSONL path it replaced and the
    form's comment quotes the sentence it stopped saying, and both are the right
    thing to write down and the wrong thing to match on.
    """
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.splitlines())


def parse_one(sql: str):
    pglast = pytest.importorskip(
        "pglast", reason="pip install -r requirements-dev.txt")
    parsed = pglast.parse_sql(sql)
    assert len(parsed) == 1, "one statement per literal, so one failure per name"
    return parsed[0]


def written_columns(stmt) -> set[str]:
    """The columns a statement writes, by name, for INSERT and UPDATE.

    These are `ResTarget` nodes, the same node type a SELECT uses for an output
    alias, and the difference matters: a SELECT's `ResTarget` name is invented
    by the query and an INSERT's names a real column. Collapsing the two is how
    the first draft of tests/test_waitlist.py passed a deliberate `statuss`
    typo, which was the whole defect it was written to catch.
    """
    names = set()
    kind = type(stmt).__name__
    if kind == "InsertStmt":
        for target in (stmt.cols or ()):
            if target.name:
                names.add(target.name)
        conflict = getattr(stmt, "onConflictClause", None)
        for target in (getattr(conflict, "targetList", None) or ()):
            if target.name:
                names.add(target.name)
    elif kind == "UpdateStmt":
        for target in (stmt.targetList or ()):
            if target.name:
                names.add(target.name)
    return names


def assert_resolves(name: str, sql: str, system: set[str] | None = None):
    """Every relation and column the statement names exists in the schema.

    Columns a statement writes are checked against the schema alone, because
    nothing an INSERT or an UPDATE writes may be excused by the statement
    itself. Columns it only reads may also be names the statement invents, so
    output aliases and column aliases are allowed there.
    """
    schema_relations, schema_columns = schema_names()
    stmt = parse_one(sql).stmt
    nodes = walk(stmt)

    for node in nodes:
        if type(node).__name__ == "RangeVar":
            assert node.relname in schema_relations, (
                f"{name} names {node.relname}, which db/schema.sql does not "
                "create")

    written = written_columns(stmt)
    for column in sorted(written):
        assert column in schema_columns, (
            f"{name} writes a column {column}, which db/schema.sql does not "
            "create")

    defined = set()
    for node in nodes:
        kind = type(node).__name__
        if kind == "ResTarget" and node.name and node.name not in written:
            defined.add(node.name)
        if kind == "Alias":
            defined.update(c.sval for c in (node.colnames or ()))

    allowed = schema_columns | defined | (system or set())
    for node in nodes:
        if type(node).__name__ != "ColumnRef":
            continue
        fields = [f.sval for f in node.fields if hasattr(f, "sval")]
        if not fields:                          # count(*), an A_Star
            continue
        assert fields[-1] in allowed, (
            f"{name} names a column {fields[-1]}, which is neither in "
            "db/schema.sql nor defined by the statement itself")


def table_body(name: str) -> str:
    """The body of `create table if not exists <name> ( ... );`."""
    m = re.search(r"create table if not exists\s+%s\s*\((.*?)\n\);" % name,
                  SCHEMA, re.S | re.I)
    assert m, f"no create table for {name}"
    return m.group(1)
