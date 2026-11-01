"""`db()` must not hand the production database password to an MCP caller.

    python3 -m pytest tests/test_mcp_dsn_redaction.py -q

The 2026-10-01 audit filed this as low, on the reasoning that it "needs a
malformed `DATABASE_URL` to trigger, which means the server is already broken
when it happens". The 2026-11-01 sweep measured the reasoning instead of
carrying it, and the trigger is narrower and far more ordinary than that:

libpq treats a string as a URI only when it begins exactly with `postgres://`
or `postgresql://`. A single leading space or tab, or a value that was stored
with its surrounding quotes, is parsed as a keyword/value connection string
instead, and the first error that parse raises is `missing "=" after
"<the whole DSN>"`. So the malformation that leaks the password is the most
common way a pasted secret is malformed, a trailing newline is tolerated and
does not leak, and nothing warns the operator who made the paste error.

`db()` lives inside `serve()`, which cannot be imported without Modal, a
database and the embedding model. So `_redact` is lifted out of the source by
`ast` and executed on its own, which is the same trade tests/test_oauth_redirect_uri.py
names in its own header: what runs here is the deployed function's real body
rather than a stand-in of it.
"""

import ast
import os
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / "mcp" / "server.py"
SOURCE = SERVER.read_text()

PASSWORD = "n0t-a-real-password-just-a-fixture"
DSN = f"postgres://alexandria:{PASSWORD}@ep-fixture-0000.us-east-2.aws.neon.tech/neondb?sslmode=require"


def _lift(name):
    """Execute one function out of mcp/server.py without importing the module."""
    for node in ast.walk(ast.parse(SOURCE)):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            namespace = {"os": os}
            exec(textwrap.dedent(ast.get_source_segment(SOURCE, node)), namespace)
            return namespace[name]
    raise AssertionError(f"mcp/server.py no longer defines {name}()")


@pytest.fixture
def redact(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DSN)
    return _lift("_redact")


# ---------------------------------------------------------------- the leak

def test_the_malformation_that_leaks_is_a_leading_space_and_it_is_measured():
    """The claim this file is built on, asserted against psycopg rather than read.

    Skipped rather than failed where psycopg is absent, because this is the one
    assertion here that needs the real library and the suite must still run for
    a seat whose sandbox has no database driver.
    """
    psycopg = pytest.importorskip("psycopg")

    with pytest.raises(Exception) as leaking:
        psycopg.conninfo.conninfo_to_dict(" " + DSN)
    assert PASSWORD in str(leaking.value), (
        "a leading space no longer makes libpq echo the DSN; if this is now "
        "safe, the strip() in db() can go and this file should say so")

    # And the other half, which is why `.strip()` is the fix and not a tidy-up.
    assert psycopg.conninfo.conninfo_to_dict((" " + DSN).strip())
    assert psycopg.conninfo.conninfo_to_dict(DSN + "\n"), "a trailing newline is tolerated"


# ------------------------------------------------------------ the redaction

def test_the_whole_dsn_echoed_back_is_struck_out(redact):
    message = f'missing "=" after "{DSN}" in connection info string'
    assert PASSWORD not in redact(message, DSN)
    assert "<redacted>" in redact(message, DSN)


def test_the_password_alone_is_struck_out(redact):
    """The deeper errors quote the credential without the URL around it."""
    assert PASSWORD not in redact(
        f"password authentication failed for user (sent {PASSWORD})", DSN)


def test_the_unstripped_environment_value_is_struck_out_too(redact, monkeypatch):
    """db() strips before connecting, so the env value and `url` differ.

    The error raised on the malformed value quotes the value as it arrived, so
    the candidate set has to hold both or the leaking case is the one that gets
    through.
    """
    monkeypatch.setenv("DATABASE_URL", " " + DSN)
    assert PASSWORD not in redact(f'missing "=" after " {DSN}"', " " + DSN.strip())


def test_a_message_carrying_no_credential_survives_intact(redact):
    """Swallowing every failure would trade a rare leak for no diagnosis at all.

    A caller debugging its own integration needs this sentence, and it carries
    nothing, so it has to come through unchanged.
    """
    plain = "could not translate host name to address: Name or service not known"
    assert redact(plain, DSN) == plain


def test_an_empty_or_absent_environment_does_not_redact_everything(monkeypatch):
    """A missing secret must not turn into a wildcard.

    `replace("")` matches at every position, so a missing DATABASE_URL with no
    length floor would shred an unrelated message into `<redacted>`.
    """
    monkeypatch.delenv("DATABASE_URL", raising=False)
    redact = _lift("_redact")
    assert redact("host unreachable", "") == "host unreachable"


def test_a_secret_too_short_to_be_one_does_not_become_a_wildcard(monkeypatch):
    """The empty case above passes with or without the length floor.

    An absent value is falsy, so `if secret:` and `if len(secret) >= 6:` agree
    on it and the floor is untested by that case alone. A one-character
    password is where they disagree, and it is reachable: a half-written
    `DATABASE_URL` during a deploy is exactly when these errors fire.
    """
    monkeypatch.setenv("DATABASE_URL", "postgres://u:x@h/d")
    redact = _lift("_redact")
    plain = "could not translate host name to address: six extra words here"
    assert redact(plain, "postgres://u:x@h/d") == plain, (
        "a one-character password redacted every 'x' in an unrelated message")


# ------------------------------------------------------------------ the wiring
#
# Structural rather than textual, because the call site is inside `serve()` and
# cannot be imported here, and because the obvious version of this test does not
# work. `assert "from None" in body` passes on a db() whose `from None` has been
# deleted, because the comment above it explains the words it is checking for.
# tests/path.test.mjs documents the mirror image of that trap and strips
# comments to dodge it; the ast carries no comments at all, so these read the
# parse tree and the question disappears.
#
# Every assertion below was confirmed to fail against a db() with that one
# guard removed, which is incident 32's rule applied to this file.

def _db_node():
    return next(n for n in ast.walk(ast.parse(SOURCE))
                if isinstance(n, ast.FunctionDef) and n.name == "db")


def test_db_strips_the_secret_before_libpq_sees_it():
    """The read of DATABASE_URL is wrapped in at least one .strip()."""
    for node in ast.walk(_db_node()):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "strip"):
            continue
        if "DATABASE_URL" in ast.dump(node.func.value):
            return
    raise AssertionError(
        "db() reads DATABASE_URL without stripping it, so a leading space in "
        "the secret makes libpq echo the password (see this file's header)")


def test_db_raises_no_connect_failure_without_passing_it_through_redact():
    """Every `raise` in db()'s except block names _redact, and suppresses context."""
    raises = [n for n in ast.walk(_db_node()) if isinstance(n, ast.Raise)]
    assert raises, "db() no longer re-raises a connect failure at all"
    for node in raises:
        assert "_redact" in ast.dump(node), (
            "db() raises a connect failure without passing it through _redact")
        # `raise X from None` parses as cause=Constant(None). A bare `raise X`
        # leaves cause as the attribute None, and chains the original, whose
        # unredacted message prints through the traceback.
        assert isinstance(node.cause, ast.Constant) and node.cause.value is None, (
            "db() chains the original exception, so the unredacted message "
            "prints through the traceback and defeats the redaction above it")
