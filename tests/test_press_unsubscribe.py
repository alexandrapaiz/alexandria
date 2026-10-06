"""The foot of every issue is a link that works, and a mailto only when it cannot be.

Sprint 2026-10-05 item 3, the press half. The site half (the `/unsubscribe`
page, the `/api/unsubscribe` route and the `subscribers.unsubscribe_token`
column) is on its own branch; this file holds the promises the press makes
about the link it puts in the email.

Four of them, and each one is a way this could go wrong in a reader's mail
client rather than a restatement of the code:

1. **The link carries a token, never an address.** An unsubscribe link is
   published to every recipient and then lives in their mail client forever.
   With an address in it, anybody who ever sees one can unsubscribe the person
   whose address they already know.
2. **Each recipient gets their own.** One render per recipient is how the
   footer already names the address it was sent to, and a token pasted into a
   shared render would unsubscribe the wrong reader.
3. **A missing token costs that reader the old mailto, and nobody the issue.**
   The column arrives in a migration the press does not wait for.
4. **A missing column does not cost the send.** This is the one that is not
   about the footer at all. The probe runs on a connection that is not in
   autocommit, so a failed statement aborts the transaction and every query
   after it fails too, including the one that reads the previous issue's title.
   Probing without rolling back would turn a cosmetic footer problem into a
   week with no issue.

Run with `python3 tests/test_press_unsubscribe.py` or under pytest.
"""

import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if "modal" not in sys.modules:
    modal = types.ModuleType("modal")
    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
    )
    sys.modules["modal"] = modal

from pipeline import weekly  # noqa: E402

ISSUE = (ROOT / "site" / "content" / "issues" / "2026-W39.md").read_text()
SENDER = "owner@gmail.com"
TOKEN_A = "7f3b1c90-0000-4000-8000-000000000001"
TOKEN_B = "7f3b1c90-0000-4000-8000-000000000002"


# ---------------- 1. the link carries a token, never an address ----------

def test_a_token_becomes_a_site_link():
    link = weekly.unsubscribe_link(TOKEN_A, SENDER)
    assert link == f"{weekly.email_render().site_base()}/unsubscribe?t={TOKEN_A}"
    assert link.startswith("https://"), "a bare host would not be a clickable href"


def test_the_link_never_carries_an_address():
    link = weekly.unsubscribe_link(TOKEN_A, SENDER)
    assert SENDER not in link
    assert "@" not in link, (
        "an address in an unsubscribe link lets anybody who knows an address "
        "remove that person"
    )


def test_the_token_is_escaped_into_the_query_string():
    # Today's tokens are uuids, so nothing here needs escaping. The column is
    # typed `uuid` and could be widened to `text` by a later migration, and a
    # token with an `&` or a `#` in it would silently truncate the parameter
    # and send every such reader to a link that cannot be read.
    link = weekly.unsubscribe_link("a&b=c#d /e", SENDER)
    assert link.endswith("/unsubscribe?t=a%26b%3Dc%23d%20%2Fe")
    assert "&" not in link.split("?t=", 1)[1]


def test_a_uuid_object_is_accepted():
    # psycopg returns a `uuid` column as uuid.UUID, not as str.
    import uuid

    link = weekly.unsubscribe_link(uuid.UUID(TOKEN_A), SENDER)
    assert link.endswith(f"/unsubscribe?t={TOKEN_A}")


def test_the_site_base_is_overridable(monkeypatch=None):
    # The rehearsal points at a preview deploy by setting SITE_URL, and the
    # unsubscribe link has to move with the rest of the email's links.
    import os

    saved = os.environ.get("SITE_URL")
    os.environ["SITE_URL"] = "https://preview.example.dev/"
    try:
        assert weekly.unsubscribe_link(TOKEN_A, SENDER).startswith(
            "https://preview.example.dev/unsubscribe?t=")
    finally:
        if saved is None:
            del os.environ["SITE_URL"]
        else:
            os.environ["SITE_URL"] = saved


# ---------------- 2. no token is the old mailto, and that is deliberate ----

def test_no_token_falls_back_to_the_mailto():
    for empty in (None, "", 0):
        assert weekly.unsubscribe_link(empty, SENDER) == (
            f"mailto:{SENDER}?subject=Unsubscribe"), (
            "until the column exists, the footer keeps the contract "
            "site/emails/README.md already accepts"
        )


# ---------------- 3. the email itself, per recipient ----------------

def test_each_recipient_gets_their_own_link():
    rows = [("a@example.com", "A", TOKEN_A), ("b@example.com", "B", TOKEN_B)]
    msgs = weekly.build_messages("2026-W39", ISSUE, rows, SENDER)
    assert len(msgs) == 2
    first, second = msgs[0][3], msgs[1][3]
    assert TOKEN_A in first and TOKEN_B not in first
    assert TOKEN_B in second and TOKEN_A not in second


def test_a_real_link_replaces_the_mailto_in_the_rendered_email():
    rows = [("a@example.com", "A", TOKEN_A)]
    html = weekly.build_messages("2026-W39", ISSUE, rows, SENDER)[0][3]
    assert "/unsubscribe?t=" in html
    assert "subject=Unsubscribe" not in html, (
        "a reader with a token must not also be offered the reply path"
    )


def test_the_short_row_shape_still_renders():
    # tools/rehearse_email.py builds its own rows as (address, None), and the
    # `only=` resend path predates the column. Both must keep working.
    msgs = weekly.build_messages("2026-W39", ISSUE, [("a@example.com", None)], SENDER)
    assert len(msgs) == 1
    assert "subject=Unsubscribe" in msgs[0][3]


def test_a_render_failure_still_delivers_to_three_column_rows():
    # The fallback render iterates `rows` too, and it used to unpack pairs.
    mod = weekly.email_render()
    saved = mod.template_text
    mod.template_text = lambda: (_ for _ in ()).throw(RuntimeError("template moved"))
    try:
        msgs = weekly.build_messages(
            "2026-W39", ISSUE,
            [("a@x.com", "A", TOKEN_A), ("b@x.com", "B", TOKEN_B)], SENDER)
    finally:
        mod.template_text = saved
    assert [m[0] for m in msgs] == ["a@x.com", "b@x.com"]
    assert all(m[3] for m in msgs), "a failed render must still produce an email"


# ---------------- 4. the column may not be there yet ----------------

class FakeUndefinedColumn(Exception):
    sqlstate = "42703"


class FakeOtherError(Exception):
    sqlstate = "57014"  # query_canceled, which must not be swallowed


class FakeConn:
    """Records every statement and rollback, in order."""

    def __init__(self, fail_on_token=False, error=None):
        self.fail_on_token = fail_on_token
        self.error = error or FakeUndefinedColumn("column does not exist")
        self.log = []

    def execute(self, sql, params=None):
        self.log.append(sql)
        if self.fail_on_token and "unsubscribe_token" in sql:
            raise self.error
        rows = ([("a@x.com", "A", TOKEN_A)] if "unsubscribe_token" in sql
                else [("a@x.com", "A")])
        return types.SimpleNamespace(fetchall=lambda: rows,
                                     fetchone=lambda: rows[0])

    def rollback(self):
        self.log.append("ROLLBACK")


def test_the_token_column_is_read_when_it_exists():
    conn = FakeConn()
    assert weekly.active_recipients(conn) == [("a@x.com", "A", TOKEN_A)]
    assert conn.log == [
        "select email, name, unsubscribe_token from subscribers "
        "where status = 'active'"
    ]
    assert "ROLLBACK" not in conn.log, "nothing failed, so nothing to roll back"


def test_a_missing_column_falls_back_and_rolls_back_first():
    conn = FakeConn(fail_on_token=True)
    assert weekly.active_recipients(conn) == [("a@x.com", "A")]
    assert conn.log[1] == "ROLLBACK", (
        "the rollback must come between the failed probe and the retry, or "
        "every later query in the send fails with InFailedSqlTransaction"
    )
    assert "unsubscribe_token" not in conn.log[2]
    assert len(conn.log) == 3


def test_any_other_database_error_is_not_swallowed():
    conn = FakeConn(fail_on_token=True, error=FakeOtherError("canceled"))
    try:
        weekly.active_recipients(conn)
    except FakeOtherError:
        pass
    else:
        raise AssertionError(
            "only a missing column may be retried; a timeout or a dead "
            "connection must reach send_newsletter's own handler"
        )
    assert "ROLLBACK" not in conn.log


def test_an_error_with_no_sqlstate_is_not_swallowed():
    conn = FakeConn(fail_on_token=True, error=RuntimeError("socket closed"))
    try:
        weekly.active_recipients(conn)
    except RuntimeError:
        pass
    else:
        raise AssertionError("a non-database error must propagate")


# ---------------- the seam, so a later edit cannot quietly undo this --------

def test_send_newsletter_goes_through_active_recipients():
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    body = source.split("def send_newsletter")[1].split("\ndef ")[0]
    assert "active_recipients(conn)" in body
    assert "from subscribers" not in body, (
        "the recipient query belongs in active_recipients, which is where the "
        "missing-column fallback lives"
    )


def test_no_mailto_unsubscribe_is_hardcoded_outside_the_fallback():
    source = (ROOT / "pipeline" / "weekly.py").read_text()
    hits = [m for m in re.findall(r"mailto:[^\"'\s]*Unsubscribe", source)]
    assert len(hits) == 1, (
        f"the reply-to-unsubscribe address should exist once, in "
        f"unsubscribe_link's no-token branch; found {len(hits)}"
    )
    fn = source.split("def unsubscribe_link")[1].split("\ndef ")[0]
    assert "mailto:" in fn


def _run():
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  ok   {name}")
            except Exception as exc:
                failures += 1
                print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
    print(f"\n{failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_run())
