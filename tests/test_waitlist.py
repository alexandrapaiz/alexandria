"""The signup path: the row it writes, the SQL that writes it, and the copy.

    python3 -m pytest tests/test_waitlist.py -q

Sprint 2026-10-05 item 2. Until this change `site/lib/waitlist.js` appended to
a JSONL file on local disk, and its own comment left the database insert as
"the seam the engineer wires later". This file is how that seam is checked
without a Postgres, which this org runs nowhere in CI.

Three tools for three different questions.

The decision logic is executed for real in `tests/waitlist.test.mjs`, which
this file also runs, so one pytest command covers the whole path.

The SQL is parsed with libpg_query, the server's own parser, and every
relation and column it names is resolved against `db/schema.sql`. That is the
check that matters here, because an insert in a serverless route is otherwise
run for the first time by a stranger submitting a form, and a typo in it is a
person lost rather than a build failed. The same technique holds
`tools/graph_audit.py` (tests/test_graph_audit.py) and the two files share the
reasoning rather than the code, since the audit's queries are a dict in Python
and these are template literals in JavaScript.

The copy is read as text, because a form that creates a real subscriber while
promising to write only "on the day subscriptions open" is a broken promise
rather than a broken build, and nothing else in the repository would notice.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (ROOT / "db" / "schema.sql").read_text()
CORE = (ROOT / "site" / "lib" / "waitlist-core.js").read_text()
HELPER = (ROOT / "site" / "lib" / "waitlist.js").read_text()
ROUTE = (ROOT / "site" / "app" / "api" / "waitlist" / "route.js").read_text()
FORM = (ROOT / "site" / "app" / "components" / "Waitlist.jsx").read_text()


def code_only(text):
    """The file with its `//` comments removed.

    Several assertions below are about what the code does and would otherwise
    be satisfied, or broken, by a comment that merely quotes the thing. This
    file's own history is the example: the helper's comment names the JSONL
    path it replaced, and the form's comment quotes the sentence it stopped
    saying, and both are the right thing to write down and the wrong thing to
    match on.
    """
    return "\n".join(re.sub(r"//.*$", "", line) for line in text.splitlines())


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


def _schema_names():
    """(relations, columns) as libpg_query reads db/schema.sql.

    Columns come from CREATE TABLE and from the ALTER TABLE ADD COLUMN
    migrations further down the file, which is where `source` lives.
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


def statements():
    """Every SQL template literal in site/lib/waitlist.js, by name.

    A tagged template is the driver's parameter binding, so `${row.email}`
    reaches the server as a placeholder and never as text. `$1` is what the
    server actually sees, which is what the parser has to be given.
    """
    code = code_only(HELPER)
    found = {}
    for name, body in re.findall(
            r"const (\w+) = \(sql, row\) => sql`(.*?)`;", code, re.S):
        found[name] = re.sub(r"\$\{[^}]*\}", "$1", body)
    # The status read is written inline rather than as a named constant,
    # because it is the only statement here that is not an insert. Collected
    # anyway, so that every statement reaching the server is under the parser.
    named = "|".join(re.escape(sql) for sql in found.values()) or r"(?!)"
    for body in re.findall(r"await sql`(.*?)`", code, re.S):
        normalized = re.sub(r"\$\{[^}]*\}", "$1", body)
        if not re.fullmatch(named, normalized, re.S):
            found["STATUS_BEFORE"] = normalized
    return found


def parse_one(sql):
    pglast = pytest.importorskip(
        "pglast", reason="pip install -r requirements-dev.txt")
    parsed = pglast.parse_sql(sql)
    assert len(parsed) == 1, "one statement per literal, so one failure per name"
    return parsed[0]


def test_there_are_exactly_the_three_statements_this_file_knows_about():
    """A fourth query added without a test is the thing this catches.

    Two inserts (one for a database that has had today's migration and one for
    a database that has not) and the status read that tells a returning
    subscriber from one who never left.
    """
    assert sorted(statements()) == ["INSERT_WITHOUT_SOURCE", "INSERT_WITH_SOURCE",
                                    "STATUS_BEFORE"], sorted(statements())


def test_every_statement_parses_as_postgresql():
    """A typo fails the pull request instead of losing a subscriber."""
    for name, sql in statements().items():
        parse_one(sql)


def test_every_relation_the_signup_names_exists():
    schema_relations, _ = _schema_names()
    for name, sql in statements().items():
        for node in _walk(parse_one(sql), []):
            if type(node).__name__ == "RangeVar":
                assert node.relname in schema_relations, (
                    f"{name} writes {node.relname}, which db/schema.sql does "
                    "not create")


def _insert_target_columns(stmt):
    """The column list of `insert into t (a, b, c)`, and of its DO UPDATE SET.

    These are `ResTarget` nodes, the same node type a SELECT uses for an output
    alias, and the difference matters: a SELECT's `ResTarget` name is invented
    by the query and an INSERT's names a real column. Collapsing the two is how
    the first draft of this file passed a deliberate `statuss` typo, which was
    the whole defect it was written to catch.
    """
    names = set()
    for target in (stmt.cols or ()):
        if target.name:
            names.add(target.name)
    conflict = getattr(stmt, "onConflictClause", None)
    for target in (getattr(conflict, "targetList", None) or ()):
        if target.name:
            names.add(target.name)
    return names


def test_every_column_the_signup_names_exists():
    """Schema columns, plus `xmax`, which is PostgreSQL's and not ours.

    `source` is in this set only because db/schema.sql gained it in the same
    change as the insert. If a later edit drops the ALTER TABLE and keeps the
    insert, this is the test that fails.
    """
    _, schema_columns = _schema_names()
    system = {"xmax"}
    for name, sql in statements().items():
        stmt = parse_one(sql).stmt
        nodes = _walk(stmt, [])

        # Written columns first, and against the schema only. Nothing an
        # INSERT writes is allowed to be excused by the statement itself.
        written = (_insert_target_columns(stmt)
                   if type(stmt).__name__ == "InsertStmt" else set())
        for column in sorted(written):
            assert column in schema_columns, (
                f"{name} writes a column {column}, which db/schema.sql does "
                "not create")

        defined = set()
        for node in nodes:
            kind = type(node).__name__
            if kind == "ResTarget" and node.name and node.name not in written:
                defined.add(node.name)
            if kind == "Alias":
                defined.update(c.sval for c in (node.colnames or ()))
        allowed = schema_columns | defined | system
        for node in nodes:
            if type(node).__name__ != "ColumnRef":
                continue
            fields = [f.sval for f in node.fields if hasattr(f, "sval")]
            if not fields:
                continue
            assert fields[-1] in allowed, (
                f"{name} names a column {fields[-1]}, which is neither in "
                "db/schema.sql nor defined by the statement itself")


def test_the_insert_writes_an_active_comped_digest_row():
    """The sprint item, read off the SQL rather than off the helper's comment.

    `status = 'active'` is the whole of it. pipeline/weekly.py selects
    `status = 'active'` and nothing else, so a signup in any other state is a
    row waiting on a human, which clause 1 of the definition of done rules out.
    """
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        sql = statements()[name]
        assert type(parse_one(sql).stmt).__name__ == "InsertStmt", name
        assert re.search(r"insert into subscribers", sql, re.I), name
    assert "status: \"active\"" in CORE
    assert "comp: true" in CORE
    assert "tier: \"digest\"" in CORE


def test_no_signup_can_land_in_a_state_the_press_does_not_read():
    """The status check still names two states, and 'waitlist' is not one.

    site/lib/waitlist.js used to ask, in its own comment, for 'waitlist' to be
    added to this constraint. Following that instruction would have rebuilt the
    manual promotion step the sprint item exists to remove, so the instruction
    was dropped rather than followed, and this is the test that keeps it
    dropped.
    """
    body = re.search(r"create table if not exists\s+subscribers\s*\((.*?)\n\);",
                     SCHEMA, re.S | re.I).group(1)
    allowed = re.search(r"status.*?check \(status in \((.*?)\)\)", body, re.S | re.I)
    assert allowed, "subscribers.status accepts any string"
    assert sorted(re.findall(r"'(\w+)'", allowed.group(1))) == ["active", "unsubscribed"]


def test_the_upsert_revives_an_unsubscriber_and_touches_nothing_else():
    """Somebody who unsubscribed in March and signs up in June has asked
    twice, and the second ask is the current one. But if the owner has comped
    or upgraded somebody by hand, a form must not undo it, so the conflict
    branch writes `status` and `unsubscribed_at` and no other column."""
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        sql = statements()[name]
        assert "on conflict (email) do update" in sql, name
        clause = sql[sql.index("do update"):]
        clause = clause[:clause.index("returning")]
        written = set(re.findall(r"^\s*(?:set\s+)?(\w+)\s*=", clause, re.M))
        assert written == {"status", "unsubscribed_at"}, (name, written)


def test_the_insert_reports_whether_it_inserted_rather_than_asking_again():
    """A second query to find out would race with a concurrent signup for the
    same address, and `xmax = 0` is the server's own answer."""
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        assert "(xmax = 0) as inserted" in statements()[name], name


def test_the_source_column_is_optional_at_the_point_of_insert():
    """`source` and the column arrive in one change, and the deploy that
    applies db/schema.sql is a separate step the owner runs. For the window
    between the merge and that step the column does not exist, so the insert
    falls back rather than refusing the signup. 42703 is undefined_column, and
    it is matched by code because the message is localised and the code is
    not."""
    assert '"42703"' in HELPER
    assert "INSERT_WITHOUT_SOURCE" in HELPER
    assert "source" not in statements()["INSERT_WITHOUT_SOURCE"]
    assert "source" in statements()["INSERT_WITH_SOURCE"]
    line = [l for l in SCHEMA.splitlines()
            if "add column if not exists source" in l][0]
    assert "not null" not in line.lower(), (
        "a not-null column with no default cannot be added to a live table")


# ---------------------------------------------------------------- no file

def test_nothing_on_the_signup_path_writes_to_disk():
    """The holding pen is gone, which is the point. A file on a serverless
    host is a list that can lose the list, which its own comment admitted."""
    for name, text in (("waitlist.js", HELPER), ("route.js", ROUTE),
                       ("waitlist-core.js", CORE)):
        code = code_only(text)
        assert "node:fs" not in code, name
        assert "appendFile" not in code, name
        assert "waitlist.jsonl" not in code, name
        assert "WAITLIST_FILE" not in code, name


def test_the_pure_core_stays_import_free():
    """tests/waitlist.test.mjs loads it by evaluating its source, which only
    works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


def test_no_credential_appears_in_any_file_on_this_path():
    """DATABASE_URL by name, read from the environment, never a literal."""
    assert "process.env.DATABASE_URL" in HELPER
    for name, text in (("waitlist.js", HELPER), ("route.js", ROUTE),
                       ("waitlist-core.js", CORE)):
        assert not re.search(r"postgres(ql)?://", text), name
        assert not re.search(r"DATABASE_URL\s*=\s*['\"]", text), name


# ----------------------------------------------------------------- the route

def test_a_bad_address_is_refused_before_the_database_is_opened():
    """The person's own typo gets a 400 they can act on, and it costs no
    round trip. Everything after that point is ours, not theirs."""
    check = ROUTE.index("normalizeEmail(")
    insert = ROUTE.index("subscribe(")
    assert check < insert, "the route inserts before it validates"
    assert "status: 400" in ROUTE


def test_an_unreachable_list_answers_503_and_a_refused_address_400():
    """The status code is the only place the difference survives. The request
    was fine and the list was not, and a 500 says neither."""
    assert "result.retryable ? 503 : 400" in ROUTE
    assert 'retryable: true, reason: "DATABASE_URL is not set"' in HELPER


def test_the_route_never_tells_the_person_which_outcome_they_were():
    """They are on the list in all three cases, and the distinction is for the
    owner's counts. Saying it would only make them wonder."""
    assert "already" not in ROUTE
    assert "resubscribed" not in ROUTE
    assert "{ ok: true, outcome: result.outcome }" in ROUTE


def test_an_error_inside_the_insert_cannot_take_the_endpoint_down():
    assert ".catch(() => ({" in ROUTE


# ------------------------------------------------------------------ the copy

def test_the_form_no_longer_promises_a_single_email_that_never_comes():
    """The submit creates a subscriber the Monday press sends to. The old
    sentence, "We will write on the day subscriptions open", was true of a
    holding pen and is a broken promise now."""
    for stale in ("on the day subscriptions open", "Join the waitlist",
                  "We write once", "We send one email"):
        for page in ("page.jsx", "pricing/page.jsx"):
            text = code_only((ROOT / "site" / "app" / page).read_text())
            assert stale not in text, f"{page} still says {stale!r}"
        assert stale not in code_only(FORM), f"the form still says {stale!r}"


def test_the_form_says_what_actually_happens_next():
    assert "You are subscribed." in FORM
    assert ">Subscribe<" in FORM or '"Subscribe"' in FORM


def test_the_copy_keeps_the_house_voice():
    """No em dash and no semicolon joining two clauses, per
    docs/voice/ban-list.md, over the sentences a stranger reads."""
    sentences = re.findall(r'(?:note=|>)\s*"?([A-Z][^"<>{}]{15,})', FORM)
    assert sentences, "no copy found to check"
    for line in sentences:
        assert "—" not in line, line
        assert ";" not in line, line


# -------------------------------------------------------------- executed js

def test_waitlist_core_logic():
    """Runs tests/waitlist.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/waitlist.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "waitlist.test.mjs")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
